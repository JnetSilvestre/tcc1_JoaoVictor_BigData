"""E11-D09: preflight C3/C4 de 1000 requests, SOMENTE LEITURA no cluster.

Nao aplica manifestos, nao cria namespace, nao faz POST/snapshot ou benchmark.
Sem --probe: PLAN_ONLY local. --probe: GET em namespace/nodes/Summary API
apenas para analisar disponibilidade dos instrumentos em Pods HISTORICOS.
Os novos namespaces sao exclusivamente nomes e YAML gerados localmente.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

from benchmark import collector
from benchmark.evidence import archive, hash_file, write_json
from benchmark.fixtures import characterize, rebase
from benchmark.prepare import IMAGE, namespace_for, render
from benchmark.runner import CONTEXT, NODES, ensure_safe
from c0.io import read_jsonl, validate_input

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_INPUT_SHA256 = "26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551"
CANONICAL_EXPECTED_SHA256 = "430e61ca65d582f0441eb49649d9577905d0f8fa9e1d5ff04bc01eb53eda7b1c"
IMAGE_ID = "sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a"
HISTORICAL = ("tcc2-pon", "tcc2-pon-c4")
SCENARIOS = ("C3", "C4")
ROLES = ("attribute-source", "logic-engine", "rule-executor")


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def run_readonly(*args, timeout=30):
    proc = subprocess.run([str(x) for x in args], cwd=ROOT,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout, check=False)
    if proc.returncode:
        raise RuntimeError(f"consulta read-only falhou ({proc.returncode}): "
                           f"{args[:5]}, stderr={proc.stderr[-400:]}")
    return proc.stdout


def check_repo():
    branch = run_readonly("git", "branch", "--show-current").strip()
    if branch != "tcc2/desenvolvimento":
        raise ValueError("branch diferente da aprovada")
    if run_readonly("git", "status", "--porcelain").strip():
        raise ValueError("working tree Git nao esta limpa")
    return run_readonly("git", "rev-parse", "HEAD").strip()


def validate_canonical(fixture):
    rows = read_jsonl(fixture)
    if validate_input(rows) != ("e11-canonical-1000-20260502", 20260502):
        raise ValueError("run_id/seed da fixture 1000 divergentes")
    if hash_file(fixture) != CANONICAL_INPUT_SHA256:
        raise ValueError("fixture 1000 nao corresponde ao SHA-256 canônico")
    expected = Path(fixture).with_name("expected.jsonl")
    if not expected.is_file() or hash_file(expected) != CANONICAL_EXPECTED_SHA256:
        raise ValueError("oraculo esperado ausente ou com SHA-256 divergente")
    return rows, expected


def validate_manifest(scenario, namespace, text):
    """Validação textual estática: o manifesto não será aplicado."""
    if scenario not in SCENARIOS or not namespace.startswith("tcc2-pon-e11-"):
        raise ValueError("scenario/namespace nao autorizado")
    namespace_lines = re.findall(r"(?m)^\s*namespace:\s*(\S+)\s*$", text)
    if not namespace_lines or set(namespace_lines) != {namespace}:
        raise ValueError(f"{scenario}: namespace de recurso errado")
    if not re.search(rf"(?m)^  name:\s*{re.escape(namespace)}\s*$", text):
        raise ValueError(f"{scenario}: objeto Namespace nao identificado")
    if len(re.findall(r"(?m)^\s+image:\s*" + re.escape(IMAGE) + r"\s*$", text)) != 4:
        raise ValueError(f"{scenario}: nao ha exatamente 3 imagens de servico e 1 cliente")
    if "kind: Pod\nmetadata:\n  name: e11-benchmark-client\n" not in text:
        raise ValueError(f"{scenario}: cliente isolado nao encontrado")
    original = "tcc2-pon" if scenario == "C3" else "tcc2-pon-c4"
    if re.search(rf"(?m)^\s*namespace:\s*{re.escape(original)}\s*$", text):
        raise ValueError(f"{scenario}: manifesto referencia namespace historico")
    if scenario == "C4":
        if "kubernetes.io/hostname: tcc2-pon-control-plane" not in text:
            raise ValueError("C4 nao fixa logic-engine no control-plane")
        if 'key: "node-role.kubernetes.io/control-plane"' not in text:
            raise ValueError("C4 nao tem toleration para control-plane")
    return {"namespace_fields": len(namespace_lines),
            "image_occurrences": 4,
            "old_namespace_isolated": True,
            "planned_only": True}


def make_plans(label, rows):
    plans = {}
    for scenario in SCENARIOS:
        run_id = f"e11-{scenario.lower()}-{label}"
        ns = ensure_safe(scenario, label, run_id, rows)
        expected_ns = namespace_for(scenario, label)
        if ns != expected_ns:
            raise ValueError("identificador do namespace nao corresponde ao runner")
        namespace, yaml_text = render(scenario, label)
        if namespace != ns:
            raise ValueError("manifesto gerado em namespace divergente")
        checks = validate_manifest(scenario, namespace, yaml_text)
        plans[scenario] = {
            "namespace": namespace, "run_id": run_id,
            "expected": characterize(rebase(rows, run_id)),
            "checks": checks,
            "manifest_text": yaml_text,
        }
    return plans


def verify_namespace_discovery(items, planned):
    names = {x["metadata"]["name"] for x in items}
    missing = sorted(set(HISTORICAL)-names)
    already_exists = sorted(set(planned)&names)
    if missing:
        raise ValueError(f"namespaces funcionais historicos ausentes: {missing}")
    if already_exists:
        raise ValueError(f"namespace planejado ja existe: {already_exists}")
    return {"historic_present": list(HISTORICAL),
            "planned_namespaces_absent": sorted(planned),
            "total_namespace_count": len(names),
            "safe_to_apply_later": False}


def verify_nodes(items):
    names = {x["metadata"]["name"]: x for x in items}
    details = {}
    for node in NODES:
        if node not in names:
            raise ValueError(f"node kind esperado ausente: {node}")
        obj = names[node]
        conditions = {s.get("type"): s.get("status")
                      for s in obj.get("status", {}).get("conditions", [])}
        ready = conditions.get("Ready") == "True"
        if not ready:
            raise ValueError(f"node nao esta Ready: {node}")
        details[node] = {
            "ready": True, "uid": obj["metadata"].get("uid"),
            "allocatable": obj.get("status", {}).get("allocatable", {}),
            "node_info": obj.get("status", {}).get("nodeInfo", {}),
        }
    return details


def summarize_kubelet(body, node, captured_utc):
    """Somente pods historicos como referencia de disponibilidade/frescor."""
    if not isinstance(body, dict) or not isinstance(body.get("pods"), list):
        raise ValueError(f"Summary API {node} sem campo pods")
    entries = {}
    for pod in body["pods"]:
        pref = pod.get("podRef") or {}
        if pref.get("namespace") not in HISTORICAL:
            continue
        for c in pod.get("containers") or []:
            cpu = c.get("cpu") or {}
            mem = c.get("memory") or {}
            if c.get("name") not in ROLES:
                continue
            key = f'{pref.get("namespace")}/{pref.get("uid")}/{c.get("name")}'
            entries[key] = {
                "namespace": pref.get("namespace"),
                "pod": pref.get("name"), "pod_uid": pref.get("uid"),
                "container": c.get("name"),
                "cpu_time_utc": cpu.get("time"),
                "cpu_usage_core_ns": cpu.get("usageCoreNanoSeconds"),
                "memory_time_utc": mem.get("time"),
                "memory_working_set_bytes": mem.get("workingSetBytes"),
            }
    valid_cpu = sum(type(v["cpu_usage_core_ns"]) is int
                    and v["cpu_usage_core_ns"] >= 0
                    and collector.parse_utc(v["cpu_time_utc"]) is not None
                    for v in entries.values())
    valid_mem = sum(type(v["memory_working_set_bytes"]) is int
                    and v["memory_working_set_bytes"] >= 0
                    and collector.parse_utc(v["memory_time_utc"]) is not None
                    for v in entries.values())
    return {"node": node, "captured_utc": captured_utc,
            "historical_containers": len(entries),
            "cpu_fields_valid": valid_cpu, "memory_fields_valid": valid_mem,
            "containers": entries}


def compare_snapshots(first, second):
    """Dois instantes em repouso nao validam cadencia durante carga."""
    a, b = first["containers"], second["containers"]
    overlap = sorted(set(a)&set(b))
    distinct_times = 0
    regressions = 0
    for key in overlap:
        left, right = a[key], b[key]
        ta = collector.parse_utc(left["cpu_time_utc"])
        tb = collector.parse_utc(right["cpu_time_utc"])
        ca, cb = left["cpu_usage_core_ns"], right["cpu_usage_core_ns"]
        if ta and tb and ta != tb:
            distinct_times += 1
        if ta and tb and tb < ta:
            regressions += 1
        if type(ca) is int and type(cb) is int and cb < ca:
            regressions += 1
    return {"overlapping_historical_containers":len(overlap),
            "cpu_timestamp_distinct":distinct_times,
            "cpu_timestamp_regressions_or_counter_regressions":regressions,
            "interpretation":"Amostras historicas em repouso; nao sao dados de benchmark"}


def kube_json(*args):
    return json.loads(run_readonly("kubectl", "--context", CONTEXT, *args, timeout=35))


def probe_cluster(planned_ns, interval):
    current = run_readonly("kubectl", "config", "current-context").strip()
    if current != CONTEXT:
        raise ValueError(f"contexto kubectl ativo e {current}, esperado {CONTEXT}")
    nodes = verify_nodes(kube_json("get","nodes","-o","json")["items"])
    nscheck = verify_namespace_discovery(
        kube_json("get","namespaces","-o","json")["items"], planned_ns)
    image = json.loads(run_readonly("docker","image","inspect",IMAGE))[0]
    if image.get("Id") != IMAGE_ID:
        raise ValueError("imagem local Docker diverge da imagem C2 aprovada")
    api_samples = {node: [] for node in NODES}
    for iteration in range(2):
        for node in NODES:
            raw = kube_json("get","--raw",
                            f"/api/v1/nodes/{node}/proxy/stats/summary")
            api_samples[node].append(summarize_kubelet(raw,node,utc_now()))
        if iteration == 0:
            time.sleep(interval)
    observations = {node: compare_snapshots(*api_samples[node]) for node in NODES}
    if not all(api_samples[node][0]["cpu_fields_valid"] > 0 and
               api_samples[node][0]["memory_fields_valid"] > 0 for node in NODES):
        raise ValueError("Kubelet nao retorna CPU e memoria legiveis em todos os nos")
    if any(o["cpu_timestamp_regressions_or_counter_regressions"] for o in observations.values()):
        raise ValueError("regressao inesperada nos counters/timestamps historicos")
    status = ("PASS_READ_ONLY" if all(
              x["cpu_timestamp_distinct"] > 0 for x in observations.values())
              else "PASS_READ_ONLY_WITH_TIMESTAMP_WARNING")
    return {"status":status,"nodes":nodes,"namespaces":nscheck,
            "docker_image_id":image.get("Id"),
            "kubelet_api_rounds":api_samples,"kubelet_readiness":observations,
            "sampling_approved":False,
            "note":"Nao ha namespace E11 novo. Kubelet historico em repouso e instrumento candidato, nao medicao de carga."}


def execute(args):
    rows, expected_file = validate_canonical(args.fixture)
    plans = make_plans(args.label, rows)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    result = {"status":"FAIL","read_only":True,"execute":False,
              "git_sha":None,"context":CONTEXT,
              "fixture_sha256":hash_file(args.fixture),
              "expected_sha256":hash_file(expected_file),
              "count":len(rows),
              "description":"planejamento e diagnostico C3/C4, sem aplicar YAML",
              "plans":{k:{x:y for x,y in v.items() if x != "manifest_text"}
                       for k,v in plans.items()}}
    try:
        result["git_sha"] = check_repo()
        shutil.copyfile(args.fixture,output/"canonical-inputs.jsonl")
        shutil.copyfile(expected_file,output/"canonical-expected.jsonl")
        for scenario, plan in plans.items():
            (output/f"{scenario.lower()}-manifest-NOT-APPLIED.yaml").write_text(
                plan["manifest_text"],encoding="utf-8")
        if args.probe:
            result["diagnostic"] = probe_cluster(
                [plan["namespace"] for plan in plans.values()],
                args.interval)
            result["status"] = result["diagnostic"]["status"]
        else:
            result["status"]="PLAN_ONLY"
    except Exception as e:
        result["error"]=f"{type(e).__name__}: {e}"
    finally:
        write_json(output/"e11-d09-report.json",result)
        zipped=archive(output)
        print("E11-D09:",result["status"])
        print("KUBE_MUTATIONS: NONE")
        print("SNAPSHOT: NO")
        print("BENCHMARK: NO")
        print("EVIDENCE_ZIP:",zipped["zip"])
        print("ZIP_SHA256:",zipped["sha256"])
        if result.get("error"):
            print("ERROR:",result["error"],file=sys.stderr)
    return result["status"] in ("PLAN_ONLY","PASS_READ_ONLY",
                                "PASS_READ_ONLY_WITH_TIMESTAMP_WARNING")


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--label",required=True)
    ap.add_argument("--fixture",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    ap.add_argument("--interval",type=float,default=2.0)
    ap.add_argument("--probe",action="store_true")
    args=ap.parse_args(argv)
    if not 1.0<=args.interval<=10.0:
        ap.error("interval fora de 1..10 s")
    return 0 if execute(args) else 2


if __name__=="__main__":
    sys.exit(main())
