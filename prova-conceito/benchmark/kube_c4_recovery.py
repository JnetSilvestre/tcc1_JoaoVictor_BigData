"""E11-R01: recuperar evidencias de C4 apos falha de quoting do PowerShell.

SOMENTE LEITURA NO KUBERNETES: kubectl get, logs e kubectl exec apenas
com GET /state; NENHUM apply/create/rollout/delete, snapshot ou POST.
Reutiliza o namespace ja criado, sem produzir novos recursos K8s.
"""
import argparse
import json
import re
from pathlib import Path
import shutil
import sys

from benchmark.evidence import archive, hash_file, write_json
from benchmark.runner import CONTEXT, ROLES, configure, preflight, kubedata, command
from c3 import runner as kube

EXPECTED_NODES = {
    "attribute-source": "tcc2-pon-worker",
    "logic-engine": "tcc2-pon-control-plane",
    "rule-executor": "tcc2-pon-worker",
    "e11-benchmark-client": "tcc2-pon-worker",
}
HISTORICAL = (
    "tcc2-pon", "tcc2-pon-c4", "tcc2-pon-e11-c3-p20261115-235728",
)
IMAGE = "tcc2-pon:c2-e08-dbefcd2cf3d2"
KNOWN_NS = "tcc2-pon-e11-c4-p20261116-001328"
KNOWN_RUN_ID = "e11-c4-p20261116-001328"


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def pod_identity(pod, role):
    statuses = pod.get("status", {}).get("containerStatuses") or []
    spec_containers = pod.get("spec", {}).get("containers") or []
    meta = pod.get("metadata") or {}
    if (meta.get("labels", {}).get("app") != role
            or meta.get("namespace") != KNOWN_NS
            or not meta.get("uid")
            or pod.get("spec", {}).get("nodeName") != EXPECTED_NODES[role]
            or pod.get("status", {}).get("phase") != "Running"
            or len(statuses) != 1 or len(spec_containers) != 1
            or statuses[0].get("ready") is not True
            or statuses[0].get("restartCount") != 0
            or not statuses[0].get("containerID")
            or spec_containers[0].get("image") != IMAGE):
        raise ValueError(f"{role}: identidade, imagem, no ou prontidao inadequados")
    return {
        "name": meta.get("name"),
        "uid": meta["uid"],
        "namespace": meta["namespace"],
        "node": pod["spec"]["nodeName"],
        "container_id": statuses[0]["containerID"],
        "runtime_image_id": statuses[0].get("imageID"),
        "restart_count": statuses[0]["restartCount"],
        "ready": statuses[0]["ready"],
        "image_tag": spec_containers[0]["image"],
    }


def check_pod_stability(expected_pods, current_pods):
    expected_pods = expected_pods.get("items") or []
    current_pods = current_pods.get("items") or []
    if len(expected_pods) != 4 or len(current_pods) != 4:
        raise ValueError("necessarios exatamente quatro Pods em ambas fotografias")
    expected, current = {}, {}
    for items, target in ((expected_pods, expected), (current_pods, current)):
        for pod in items:
            role = (pod.get("metadata") or {}).get("labels", {}).get("app")
            if role not in EXPECTED_NODES or role in target:
                raise ValueError("role ausente/duplicado ou Pod desconhecido")
            target[role] = pod_identity(pod, role)
        if set(target) != set(EXPECTED_NODES):
            raise ValueError("papeis C4 incompletos")
    if len({v["uid"] for v in current.values()}) != 4:
        raise ValueError("UID repetido entre Pods C4")
    if expected != current:
        raise ValueError("identidades, IDs runtime ou no mudaram desde o E11-D12")
    return current


def check_cold_complete(states):
    if set(states) != set(ROLES):
        raise ValueError("conjunto de estados incompleto")
    for role in ROLES:
        state = states[role]
        if (state.get("ready") is not False
                or state.get("run_id") is not None
                or state.get("snapshot_version") is not None):
            raise ValueError(f"{role}: snapshot ou inicializacao ja detectado")
        if state.get("faulted"):
            raise ValueError(f"{role}: estado faulted")
    for role in ("attribute-source", "logic-engine"):
        if (states[role].get("attributes") != {"atA": 0, "atB": 0}
                or states[role].get("sequences") != {"atA": 0, "atB": 0}):
            raise ValueError(f"{role}: atributos/sequencias nao frios")
    source, logic, executor = (states[r] for r in ROLES)
    if source.get("pending_request_id") is not None:
        raise ValueError("source: pedido pendente")
    if (logic.get("condition") is not False
            or logic.get("condition_sequence") != 0
            or logic.get("received_ids")
            or logic.get("condition_events")):
        raise ValueError("logic-engine: historico de notificacoes presente")
    if (executor.get("approved") is not False
            or executor.get("condition_sequence") != 0
            or executor.get("received_ids")
            or executor.get("effects")):
        raise ValueError("rule-executor: historico de efeitos presente")
    return True


def history_snapshot():
    result = {}
    for namespace in HISTORICAL:
        pods = kubedata(namespace, "get", "pods", "-o", "json")["items"]
        result[namespace] = sorted(
            f'{p["metadata"]["name"]}:{p["metadata"]["uid"]}' for p in pods)
    return result


def check_historical(before, after):
    if set(before) != set(HISTORICAL) or set(after) != set(HISTORICAL):
        raise ValueError("historicos ausentes da evidencia")
    for namespace in HISTORICAL:
        a, b = before[namespace], after[namespace]
        if not isinstance(a, list) or len(a) == 0 or sorted(a) != b:
            raise ValueError(f"historico mudou: {namespace}")
    return True


def recover(args):
    if args.namespace != KNOWN_NS or args.run_id != KNOWN_RUN_ID:
        raise ValueError("namespace/run_id nao sao os da unica bancada E11-D12")
    prior = Path(args.evidence)
    if not prior.is_dir():
        raise FileNotFoundError(prior)
    existing_pods = prior / "pods-c4.json"
    history_before = prior / "historical-before.json"
    planned = prior / "preflight" / "e11-d09-report.json"
    for p in (existing_pods, history_before, planned):
        if not p.is_file():
            raise FileNotFoundError(f"arquivo de evidencia local ausente: {p}")
    original = read_json(existing_pods)
    before = read_json(history_before)
    report_pre = read_json(planned)
    if (report_pre.get("status") not in (
            "PASS_READ_ONLY", "PASS_READ_ONLY_WITH_TIMESTAMP_WARNING")
            or report_pre.get("plans", {}).get("C4", {}).get("namespace") != KNOWN_NS
            or report_pre.get("plans", {}).get("C4", {}).get("run_id") != KNOWN_RUN_ID):
        raise ValueError("preflight original nao corresponde a esta bancada")
    # Valida a fotografia anterior antes de abrir qualquer pasta de saida.
    check_pod_stability(original, original)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    result = {
        "status": "BLOCKED", "kubernetes_mutations": False,
        "snapshot_executed": False, "benchmark_executed": False,
        "namespace": args.namespace, "run_id": args.run_id,
        "cold_state_confirmed": False, "approved_for_pilot": False,
        "prior_pod_sha256": hash_file(existing_pods),
        "prior_historical_sha256": hash_file(history_before),
        "prior_preflight_report_sha256": hash_file(planned),
    }
    try:
        current_ctx = command("kubectl", "config", "current-context").stdout.strip()
        if current_ctx != CONTEXT:
            raise ValueError("contexto kubectl ativo incorreto")
        if command("git", "branch", "--show-current").stdout.strip() != "tcc2/desenvolvimento":
            raise ValueError("branch Git incorreta")
        if command("git", "status", "--porcelain").stdout.strip():
            raise ValueError("Git com alteracoes locais")
        result["git_sha"] = command("git", "rev-parse", "HEAD").stdout.strip()
        # As consultas Kubernetes a seguir sao apenas GET/list/logs.
        fresh_pods = kubedata(KNOWN_NS, "get", "pods", "-o", "json")
        write_json(output / "pods-c4-recovery.json", fresh_pods)
        identities = check_pod_stability(original, fresh_pods)
        result["pods"] = identities
        historical_after = history_snapshot()
        write_json(output / "historical-after.json", historical_after)
        check_historical(before, historical_after)
        configure("C4", KNOWN_NS, KNOWN_RUN_ID)
        top, client, source, cold = preflight("C4", KNOWN_NS)
        check_cold_complete(cold)
        if top["pods"]["logic-engine"]["node"] != "tcc2-pon-control-plane":
            raise ValueError("C4 logic-engine fora do control-plane")
        for role in ROLES:
            if top["pods"][role]["uid"] != identities[role]["uid"]:
                raise ValueError(f"{role}: UID difere da topologia")
        if client != identities["e11-benchmark-client"]["name"]:
            raise ValueError("cliente difere do Pod registrado")
        write_json(output / "states-cold.json", cold)
        write_json(output / "topology-c4-cold.json", {
            "pods": top["pods"], "nodes": top["nodes"],
            "services": top["services"], "client_pod": client, "source_pod": source})
        shutil.copyfile(existing_pods, output / "pods-c4-from-e11-d12.json")
        shutil.copyfile(history_before, output / "historical-before.json")
        result["cold_state_confirmed"] = True
        result["status"] = "PASS_COLD_READ_ONLY"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        write_json(output / "recovery-report.json", result)
        archived = archive(output)
        print("STATUS:", result["status"])
        print("SNAPSHOT: NAO; BENCHMARK: NAO; APPLY: NAO")
        print("NAMESPACE:", KNOWN_NS)
        print("ZIP:", archived["zip"])
        print("ZIP_SHA256:", archived["sha256"])
        if "error" in result:
            print("ERRO:", result["error"], file=sys.stderr)
    return result["status"] == "PASS_COLD_READ_ONLY"


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--namespace", required=True)
    parser.add_argument("--run-id",required=True)
    parser.add_argument("--evidence",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args(argv)
    return 0 if recover(args) else 2


if __name__=="__main__":
    sys.exit(main())
