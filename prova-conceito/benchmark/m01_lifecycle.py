"""E11-M00J: controlador GERAL de uma rodada M01, fail-closed.

As 30 identidades e ordem sao as do pre-registro E11-M00-v1.
Toda criacao/POST/retirada esta DESABILITADA por padrao nesta revisao.
O codigo mutante so sera habilitado apos regressao no host e homologacao.

Estados de rodada:
  PLAN_ONLY -> RUN_PASS_BACKED_UP -> RETIREMENT_COMPLETE
Em falha/incerteza: journal permanente e STOP, SEM retry automatico.
O operador aprova executar e retirar com frases SEPARADAS por slot.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from zipfile import ZipFile

from benchmark.backup_integrity import compare_backup_pair, sha256_file
from benchmark.environment_snapshot import capture_environment, run_readonly
from benchmark.lifecycle_audit import audit_archive, review_retirement_packet
from benchmark.m01_readiness import (
    FIXTURE_SHA, check_completed_sacrificial_archives,
    full_schedule, inspect_global_exclusivity,
)
from benchmark.ownership import (
    IMAGE_ID, ROLES, capture_docker_ownership, capture_kind_ownership,
    check_labels,
)
from benchmark.retirement_execute_c3_s01 import (
    INVENTORY_TYPES, ALLOWED_OTHER_OBJECTS, SERVICE_NAMES,
)
from benchmark.runtime_gate import assess_capacity

ROOT = Path(__file__).resolve().parents[1]
CONTEXT = "kind-tcc2-pon"
# TRAVA INTENCIONAL: nenhum --execute na campanha principal ainda.
MAIN_CAMPAIGN_ENABLED = False


def slot_by_position(position):
    if type(position) is not int or not 1 <= position <= 30:
        raise ValueError("STOP: posicao de rodada invalida")
    return full_schedule()[position - 1]


def paths_for(slot, home, backup_root):
    home, backup_root = Path(home), Path(backup_root)
    root = home / "TCC2-Evidencias" / "E11-M01" / slot["run_id"]
    backup = backup_root / "E11-M01"
    return {
        "root": root, "result": root / "resultado",
        "primary": root / "resultado.zip",
        "manifest": root / "manifest.yaml",
        "backup_root": backup, "backup": backup / (slot["run_id"] + ".zip"),
        "run_journal": backup / (slot["run_id"] + "-run.jsonl"),
        "retire_journal": backup / (slot["run_id"] + "-retirement.jsonl"),
        "delete_options": backup / (slot["run_id"] + "-delete-options.json"),
    }


def last_event(path):
    path = Path(path)
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"STOP: journal ausente ou simbolico: {path}")
    lines = [s for s in path.read_text(encoding="utf-8-sig").splitlines() if s.strip()]
    if not lines:
        raise ValueError("STOP: journal vazio")
    return json.loads(lines[-1])


def require_complete(path, run_id, stage, status):
    event = last_event(path)
    if (event.get("run_id") != run_id or event.get("stage") != stage
            or event.get("status") != status):
        raise ValueError(f"STOP: journal nao comprova conclusao: {path}")
    return event


def assert_prior_completed(position, home, backup_root):
    """Nenhuma tentativa posterior ou anterior inconclusa pode ser ignorada."""
    for i, older in enumerate(full_schedule(), start=1):
        p = paths_for(older, home, backup_root)
        exists = [p[x].exists() for x in ("root", "primary", "backup",
                                          "run_journal", "retire_journal")]
        if i < position:
            require_complete(p["run_journal"], older["run_id"], "COMPLETE",
                             "M01_RUN_PASS_BACKED_UP")
            require_complete(p["retire_journal"], older["run_id"], "COMPLETE",
                             "M01_RETIREMENT_COMPLETE")
            audit = audit_archive(p["primary"], older["scenario"],
                                  older["label"], older["run_id"])
            copy = compare_backup_pair(p["primary"], p["backup"])
            final = last_event(p["retire_journal"])
            if (copy["zip_sha256"] != audit["zip_sha256"]
                    or copy["different_filesystem_volume"] is not True
                    or final.get("zip_sha256") != audit["zip_sha256"]):
                raise ValueError("STOP: evidencia/journal anterior alterado")
        if i > position and any(exists):
            raise ValueError("STOP: rodada posterior ja possui artefatos")
    return True


def journal(handle, stage, slot, **fields):
    record = {
        "utc": datetime.now(timezone.utc).isoformat(),
        "stage": stage, "run_id": slot["run_id"], "scenario": slot["scenario"],
        **fields,
    }
    handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
    handle.flush()
    os.fsync(handle.fileno())


def query_command(*argv):
    """Subprocesso de consulta; sem mutacoes (nao usar para executar)."""
    if not argv or argv[0] not in ("git", "docker", "kubectl"):
        raise ValueError("STOP: programa de consulta nao permitido")
    return run_readonly(*argv)


def execute_action(*argv):
    """Unico adaptador de comandos mutantes; somente invocado por fluxo autorizado."""
    result = subprocess.run([str(x) for x in argv], cwd=ROOT,
                            text=True, encoding="utf-8", errors="replace",
                            capture_output=True, timeout=900, check=False)
    if result.returncode:
        raise RuntimeError(f"STOP: comando falhou: {argv[:5]!r} "
                           f"exit={result.returncode}, stderr={result.stderr[-400:]}")
    return result.stdout


def exact_names(slot):
    base = slot["resource_base"]
    return {role: base + ("-benchmark-client" if role == "client" else "-" + role)
            for role in ROLES}


def namespaces(query):
    raw = json.loads(query("kubectl", "--context", CONTEXT,
                           "get", "namespaces", "-o", "json"))
    result = {}
    for item in raw["items"]:
        m = item["metadata"]
        if m["name"] in result or not m.get("uid"):
            raise ValueError("STOP: namespaces incompletos")
        result[m["name"]] = m["uid"]
    return result


def global_inventory(query):
    containers = set(query("docker", "ps", "-a",
                           "--format", "{{.Names}}").splitlines())
    networks = set(query("docker", "network", "ls",
                         "--format", "{{.Name}}").splitlines())
    nss = namespaces(query)
    return {
        # Detectar TAMBEM nomes inesperados com prefixo M01, nao apenas
        # os quatro roles conhecidos. Um recurso novo desconhecido bloqueia.
        "docker": {x for x in containers if x.startswith("tcc2-pon-e11-c2-m")},
        "networks": {x for x in networks if x.startswith("tcc2-pon-e11-c2-m")},
        "namespaces": {x for x in nss if x.startswith((
            "tcc2-pon-e11-c3-m", "tcc2-pon-e11-c4-m"))},
        "namespace_uids": nss,
    }


def check_live_slot_only(slot, query):
    inv = global_inventory(query)
    if slot["scenario"] == "C2":
        if (inv["docker"] != set(exact_names(slot).values())
                or inv["networks"] != {slot["resource_base"]}
                or inv["namespaces"]):
            raise ValueError("STOP: bancada C2 nao e a unica M01")
    else:
        if (inv["docker"] or inv["networks"]
                or inv["namespaces"] != {slot["resource_base"]}):
            raise ValueError("STOP: namespace nao e a unica bancada M01")
    return inv


def verify_kube_objects(slot, archived, query):
    ns = slot["resource_base"]
    raw = json.loads(query("kubectl", "--context", CONTEXT, "-n", ns,
                           "get", INVENTORY_TYPES, "-o", "json"))
    kinds, replicas = {}, []
    for item in raw["items"]:
        meta = item["metadata"]
        if meta.get("namespace") != ns:
            raise ValueError("STOP: objeto estranho no inventario")
        if item["kind"] == "ReplicaSet":
            replicas.append(item)
        else:
            kinds.setdefault(item["kind"], set()).add(meta["name"])
    if kinds.pop("Pod", set()) != {r["name"] for r in archived["pods"].values()}:
        raise ValueError("STOP: pods inesperados no namespace")
    for kind, expected in ALLOWED_OTHER_OBJECTS.items():
        expected_names = expected
        if kind == "ConfigMap":
            expected_names = {f"e11-{slot['scenario'].lower()}-config", "kube-root-ca.crt"}
        if kinds.pop(kind, set()) != expected_names:
            raise ValueError("STOP: inventario Kube divergente")
    if kinds or len(replicas) != 3:
        raise ValueError("STOP: objetos adicionais no namespace")
    roles = set()
    for obj in replicas:
        md = obj["metadata"]
        role = (md.get("labels") or {}).get("app")
        refs = md.get("ownerReferences") or []
        if (role not in SERVICE_NAMES or role in roles
                or len(refs) != 1 or refs[0].get("kind") != "Deployment"
                or refs[0].get("name") != role
                or refs[0].get("controller") is not True):
            raise ValueError("STOP: replicaset inesperado")
        roles.add(role)
    if roles != SERVICE_NAMES:
        raise ValueError("STOP: replicasets incompletos")
    return len(raw["items"])


def verify_c2_network(slot, ownership, query, *, must_be_empty=False):
    net_id = ownership["network"]["id"]
    if not re.fullmatch(r"[a-f0-9]{64}", net_id):
        raise ValueError("STOP: ID completo de rede Docker ausente")
    raw = json.loads(query("docker", "network", "inspect", net_id))
    if len(raw) != 1:
        raise ValueError("STOP: rede alterada")
    entry = raw[0]
    check_labels(entry.get("Labels"), slot["run_id"])
    if (entry.get("Id") != net_id
            or entry.get("Name") != slot["resource_base"]
            or entry.get("Driver") != "bridge"
            or entry.get("Internal") is not True):
        raise ValueError("STOP: rede ID/nome/configuracao alterados")
    endpoints = entry.get("Containers") or {}
    if must_be_empty:
        if endpoints:
            raise ValueError("STOP: rede nao esta vazia")
    else:
        expected = {x["id"]: x["name"] for x in ownership["containers"].values()}
        if set(endpoints) != set(expected):
            raise ValueError("STOP: endpoint terceiro ou ausente")
        if any(endpoints[key].get("Name") != val for key, val in expected.items()):
            raise ValueError("STOP: nome de endpoint divergente")


def inspect_c2_container(slot, ownership, role, query, running):
    obj = ownership["containers"][role]
    if not re.fullmatch(r"[a-f0-9]{64}", obj["id"]):
        raise ValueError("STOP: ID completo do container Docker ausente")
    raw = json.loads(query("docker", "inspect", obj["id"]))
    if len(raw) != 1:
        raise ValueError("STOP: inspect container incompleto")
    item = raw[0]
    check_labels((item.get("Config") or {}).get("Labels"), slot["run_id"])
    networks = (item.get("NetworkSettings") or {}).get("Networks") or {}
    if (item.get("Id") != obj["id"]
            or item.get("Name", "").lstrip("/") != obj["name"]
            or item.get("Image") != IMAGE_ID
            or item.get("RestartCount") != 0
            or set(networks) != {slot["resource_base"]}
            or (item.get("State") or {}).get("Running") is not running):
        raise ValueError("STOP: identidade/estado de container alterado")


def review_retirement(slot, paths, query):
    """ZIP/backup + UID/ID + inventario fechado, NUNCA autoriza por si."""
    audit = audit_archive(paths["primary"], slot["scenario"],
                          slot["label"], slot["run_id"])
    copy = compare_backup_pair(paths["primary"], paths["backup"])
    if (copy["different_filesystem_volume"] is not True
            or copy["zip_sha256"] != audit["zip_sha256"]):
        raise ValueError("STOP: backup nao aprovado")
    require_complete(paths["run_journal"], slot["run_id"], "COMPLETE",
                     "M01_RUN_PASS_BACKED_UP")
    with ZipFile(paths["primary"]) as z:
        archived = json.loads(z.read("ownership-start.json"))
    if slot["scenario"] == "C2":
        owner = capture_docker_ownership(slot["label"], slot["run_id"], query)
        if (archived.get("network") != owner.get("network")
                or archived.get("containers") != owner.get("containers")):
            raise ValueError("STOP: containers/IDs diferentes do ZIP")
        check_live_slot_only(slot, query)
        verify_c2_network(slot, owner, query)
        for role in ROLES:
            inspect_c2_container(slot, owner, role, query, True)
    else:
        owner = capture_kind_ownership(slot["scenario"], slot["label"],
                                       slot["run_id"], query)
        if (archived.get("namespace") != owner.get("namespace")
                or archived.get("pods") != owner.get("pods")):
            raise ValueError("STOP: namespace/Pod UID diferentes do ZIP")
        check_live_slot_only(slot, query)
        if owner["namespace"]["uid"] != namespaces(query)[slot["resource_base"]]:
            raise ValueError("STOP: UID do namespace alterado")
        obj = json.loads(query("kubectl", "--context", CONTEXT,
                               "get", "namespace", slot["resource_base"],
                               "-o", "json"))
        metadata = obj.get("metadata") or {}
        check_labels(metadata.get("labels"), slot["run_id"])
        if metadata.get("deletionTimestamp"):
            raise ValueError("STOP: namespace em processo de exclusao")
        verify_kube_objects(slot, archived, query)
    review = review_retirement_packet(
        slot["scenario"], slot["label"], slot["run_id"],
        audit, owner, copy)
    if review.get("delete_authorized") is not False or review.get("commands") != []:
        raise ValueError("STOP: aprovacao automatica inesperada")
    return {
        "status": "M01_RETIREMENT_REVIEW_ONLY_PASS",
        "run_id": slot["run_id"], "scenario": slot["scenario"],
        "zip_sha256": audit["zip_sha256"],
        "resource_immutable_ids": review["resource_immutable_ids"],
        "ownership": owner,
        "delete_authorized": False, "commands": [],
    }


def verify_clean_git(query, approved_head):
    if query("git", "branch", "--show-current").strip() != "tcc2/desenvolvimento":
        raise ValueError("STOP: branch incorreta")
    if query("git", "status", "--porcelain").strip():
        raise ValueError("STOP: Git alterado")
    head = query("git", "rev-parse", "HEAD").strip()
    if (head != approved_head or not re.fullmatch(r"[a-f0-9]{40}", head)):
        raise ValueError("STOP: SHA da versao testada diferente")
    return head


def approval_phrase(stage, slot):
    if stage not in ("RUN", "RETIRE"):
        raise ValueError("STOP: tipo de aceite invalido")
    return f"AUTORIZO_{stage}_{slot['run_id'].upper().replace('-', '_')}"


def run_sequence_preflight(position, home, backup_root, fixture, query, capture):
    slot = slot_by_position(position)
    paths = paths_for(slot, home, backup_root)
    if query("git", "branch", "--show-current").strip() != "tcc2/desenvolvimento":
        raise ValueError("STOP: branch Git incorreta")
    if query("git", "status", "--porcelain").strip():
        raise ValueError("STOP: arvore Git suja")
    if not re.fullmatch(r"[a-f0-9]{40}",
                        query("git", "rev-parse", "HEAD").strip()):
        raise ValueError("STOP: Git SHA invalido")
    if sha256_file(fixture) != FIXTURE_SHA:
        raise ValueError("STOP: fixture canonica alterada")
    check_completed_sacrificial_archives(home, backup_root)
    assert_prior_completed(position, home, backup_root)
    if any(paths[key].exists() for key in ("root", "primary", "backup",
                                           "run_journal", "retire_journal",
                                           "delete_options")):
        raise ValueError("STOP: tentativa atual ja possui artefato, nao repetir")
    inspect_global_exclusivity(query)
    host = capture(slot["scenario"], slot["run_id"])
    capacity = assess_capacity(host)
    if slot["scenario"] in ("C3", "C4"):
        nodes = host.get("node_allocatable") or {}
        if set(nodes) != {"tcc2-pon-worker", "tcc2-pon-control-plane"}:
            raise ValueError("STOP: topologia kind inesperada")
    return {"status": "M01_SLOT_PLAN_ONLY",
            "slot": slot, "capacity": capacity["status"],
            "start_authorized": False, "commands": []}


def invoke_runner(slot, paths, fixture, action):
    """Nao automatico: chamado 1x apos aceite e journal exclusivo."""
    cmd = [
        sys.executable, "-m",
        "benchmark.docker_c2" if slot["scenario"] == "C2"
        else "benchmark.runner",
    ]
    if slot["scenario"] != "C2":
        cmd += ["--scenario", slot["scenario"]]
    cmd += ["--label", slot["label"], "--run-id", slot["run_id"],
            "--fixture", str(fixture), "--output", str(paths["result"]),
            "--measurement-mode", "timing_only",
            "--timeout", "10", "--batch-timeout", "600", "--execute"]
    return action(*cmd)


def execute_run(position, home, backup_root, fixture, approved_head,
                approval, query, capture, action):
    if not MAIN_CAMPAIGN_ENABLED:
        raise ValueError("STOP: E11-M01 permanece bloqueada por codigo")
    slot = slot_by_position(position)
    if approval != approval_phrase("RUN", slot):
        raise ValueError("STOP: consentimento de RUN ausente")
    verify_clean_git(query, approved_head)
    plan = run_sequence_preflight(position, home, backup_root, fixture,
                                  query, capture)
    paths = paths_for(slot, home, backup_root)
    if paths["backup_root"].is_symlink() or not paths["backup_root"].is_dir():
        raise ValueError("STOP: volume de backup nao preparado")
    # Retestar exclusividade o mais proximo possivel da criacao.
    inspect_global_exclusivity(query)
    paths["root"].mkdir(parents=True, exist_ok=False)
    with paths["run_journal"].open("x", encoding="utf-8", newline="\n") as events:
        journal(events, "BEFORE_RUN", slot, git_sha=approved_head,
                fixture_sha256=FIXTURE_SHA)
        try:
            if slot["scenario"] in ("C3", "C4"):
                from benchmark.prepare import render
                ns, manifest = render(slot["scenario"], slot["label"])
                if ns != slot["resource_base"]:
                    raise ValueError("STOP: namespace renderizado diverge")
                with paths["manifest"].open("x", encoding="utf-8") as out:
                    out.write(manifest)
                    out.flush()
                    os.fsync(out.fileno())
                action("kubectl", "--context", CONTEXT, "apply",
                       "--dry-run=client", "--validate=strict",
                       "-f", str(paths["manifest"]))
                inspect_global_exclusivity(query)
                journal(events, "BEFORE_APPLY", slot, namespace=ns)
                action("kubectl", "--context", CONTEXT, "apply",
                       "-f", str(paths["manifest"]))
                journal(events, "AFTER_APPLY", slot, namespace=ns)
                for role in ("rule-executor", "logic-engine", "attribute-source"):
                    action("kubectl", "--context", CONTEXT, "-n", ns,
                           "rollout", "status", "deployment/" + role,
                           "--timeout=180s")
                action("kubectl", "--context", CONTEXT, "-n", ns,
                       "wait", "--for=condition=Ready",
                       "pod/e11-benchmark-client", "--timeout=180s")
                owner = capture_kind_ownership(
                    slot["scenario"], slot["label"], slot["run_id"], query)
                journal(events, "NAMESPACE_UID", slot,
                        namespace_uid=owner["namespace"]["uid"])
            else:
                inspect_global_exclusivity(query)
            journal(events, "BEFORE_SNAPSHOT_BATCH", slot,
                    attempt_single_shot=True)
            invoke_runner(slot, paths, fixture, action)
            journal(events, "AFTER_RUNNER", slot)
            audit = audit_archive(paths["primary"], slot["scenario"],
                                  slot["label"], slot["run_id"])
            if paths["backup"].exists():
                raise ValueError("STOP: backup ja existe")
            with paths["primary"].open("rb") as src, paths["backup"].open("xb") as dst:
                shutil.copyfileobj(src, dst)
                dst.flush()
                os.fsync(dst.fileno())
            copied = compare_backup_pair(paths["primary"], paths["backup"])
            if copied["zip_sha256"] != audit["zip_sha256"] or not copied["different_filesystem_volume"]:
                raise ValueError("STOP: backup divergente")
            journal(events, "BACKUP_PASS", slot, zip_sha256=audit["zip_sha256"])
            # A bancada permanece para retirada SEPARADA, nunca auto-delete.
            journal(events, "COMPLETE", slot,
                    status="M01_RUN_PASS_BACKED_UP",
                    zip_sha256=audit["zip_sha256"])
            return {"status": "M01_RUN_PASS_BACKED_UP",
                    "slot": slot, "zip_sha256": audit["zip_sha256"],
                    "backup": str(paths["backup"]),
                    "retirement_authorized": False}
        except BaseException as exc:
            journal(events, "INTERRUPTED_DO_NOT_RETRY", slot,
                    error=f"{type(exc).__name__}: {exc}")
            raise


def execute_retirement(position, home, backup_root, approved_head,
                       approval, query, action):
    if not MAIN_CAMPAIGN_ENABLED:
        raise ValueError("STOP: E11-M01 permanece bloqueada por codigo")
    slot = slot_by_position(position)
    if approval != approval_phrase("RETIRE", slot):
        raise ValueError("STOP: consentimento de RETIRE ausente")
    verify_clean_git(query, approved_head)
    assert_prior_completed(position, home, backup_root)
    paths = paths_for(slot, home, backup_root)
    if paths["retire_journal"].exists() or paths["delete_options"].exists():
        raise ValueError("STOP: tentativa de retirada ja registrada")
    packet = review_retirement(slot, paths, query)
    initial = namespaces(query)
    owner = packet["ownership"]
    if paths["backup_root"].is_symlink() or not paths["backup_root"].is_dir():
        raise ValueError("STOP: diretorio do diario de retirada ausente/invalido")
    with paths["retire_journal"].open("x", encoding="utf-8", newline="\n") as events:
        journal(events, "AUTHORIZED_BEGIN", slot, git_sha=approved_head,
                zip_sha256=packet["zip_sha256"],
                immutable_ids=packet["resource_immutable_ids"])
        try:
            # Revalidar tudo antes do primeiro ato mutante.
            again = review_retirement(slot, paths, query)
            if again != packet or namespaces(query) != initial:
                raise ValueError("STOP: propriedade alterou antes de retirar")
            if slot["scenario"] == "C2":
                for role in ("client", "attribute-source", "logic-engine", "rule-executor"):
                    obj = owner["containers"][role]
                    inspect_c2_container(slot, owner, role, query, True)
                    journal(events, "BEFORE_STOP", slot, role=role, id=obj["id"])
                    action("docker", "container", "stop", "--time", "10", obj["id"])
                    journal(events, "AFTER_STOP", slot, role=role, id=obj["id"])
                    inspect_c2_container(slot, owner, role, query, False)
                for role in ("client", "attribute-source", "logic-engine", "rule-executor"):
                    obj = owner["containers"][role]
                    inspect_c2_container(slot, owner, role, query, False)
                    journal(events, "BEFORE_RM", slot, role=role, id=obj["id"])
                    action("docker", "container", "rm", obj["id"])
                    journal(events, "AFTER_RM", slot, role=role, id=obj["id"])
                    names = query("docker", "ps", "-a",
                                  "--format", "{{.Names}}").splitlines()
                    if obj["name"] in names:
                        raise ValueError("STOP: container ainda presente")
                verify_c2_network(slot, owner, query, must_be_empty=True)
                journal(events, "BEFORE_NETWORK_RM", slot, id=owner["network"]["id"])
                action("docker", "network", "rm", owner["network"]["id"])
                journal(events, "AFTER_NETWORK_RM", slot, id=owner["network"]["id"])
                networks = query("docker", "network", "ls",
                                 "--format", "{{.Name}}").splitlines()
                if slot["resource_base"] in networks:
                    raise ValueError("STOP: rede continua presente")
            else:
                uid = owner["namespace"]["uid"]
                data = {
                    "apiVersion": "meta.k8s.io/v1", "kind": "DeleteOptions",
                    "preconditions": {"uid": uid},
                    "propagationPolicy": "Foreground",
                }
                with paths["delete_options"].open("x", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                    f.write("\n")
                    f.flush()
                    os.fsync(f.fileno())
                journal(events, "BEFORE_UID_DELETE", slot, uid=uid)
                action("kubectl", "--context", CONTEXT, "delete", "--raw",
                       "/api/v1/namespaces/" + slot["resource_base"],
                       "-f", str(paths["delete_options"]))
                journal(events, "DELETE_ACCEPTED", slot, uid=uid)
                action("kubectl", "--context", CONTEXT, "wait",
                       "--for=delete", "namespace/" + slot["resource_base"],
                       "--timeout=180s")
            after = namespaces(query)
            if (slot["resource_base"] in after and slot["scenario"] != "C2") or (
                    {k: v for k, v in initial.items()
                     if k != slot["resource_base"]} !=
                    {k: v for k, v in after.items()
                     if k != slot["resource_base"]}):
                raise ValueError("STOP: UID historico modificado")
            if (sha256_file(paths["primary"]) != packet["zip_sha256"]
                    or sha256_file(paths["backup"]) != packet["zip_sha256"]):
                raise ValueError("STOP: ZIP ou backup modificado")
            journal(events, "COMPLETE", slot,
                    status="M01_RETIREMENT_COMPLETE",
                    zip_sha256=packet["zip_sha256"])
            return {"status": "M01_RETIREMENT_COMPLETE",
                    "slot": slot, "historic_resources_targeted": 0,
                    "zip_and_backup_preserved": True}
        except BaseException as exc:
            journal(events, "INTERRUPTED_DO_NOT_RETRY", slot,
                    error=f"{type(exc).__name__}: {exc}")
            raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--position", type=int, required=True,
                        help="1..30, conforme matriz B01-B10")
    parser.add_argument("--stage", choices=("plan", "review", "run", "retire"),
                        default="plan")
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--backup-root", type=Path,
                        default=Path("D:/TCC2-Backup"))
    parser.add_argument("--approved-head")
    args = parser.parse_args(argv)
    slot = slot_by_position(args.position)
    paths = paths_for(slot, args.home, args.backup_root)
    if args.stage == "plan":
        report = run_sequence_preflight(
            args.position, args.home, args.backup_root, args.fixture,
            query_command, capture_environment)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0
    if args.stage == "review":
        print(json.dumps(review_retirement(slot, paths, query_command),
                         indent=2, ensure_ascii=False))
        return 0
    if not MAIN_CAMPAIGN_ENABLED:
        parser.error("E11-M01 ainda bloqueada, nenhuma operacao mutante liberada")
    if not args.approved_head:
        parser.error("SHA do codigo testado requerido")
    phrase = approval_phrase("RUN" if args.stage == "run" else "RETIRE", slot)
    print(f"ALVO EXCLUSIVO: {slot['run_id']} / {slot['resource_base']}")
    value = input("Digite exatamente " + phrase + " para autorizar: ").strip()
    if args.stage == "run":
        result = execute_run(
            args.position, args.home, args.backup_root,
            args.fixture, args.approved_head, value,
            query_command, capture_environment, execute_action)
    else:
        result = execute_retirement(
            args.position, args.home, args.backup_root,
            args.approved_head, value, query_command, execute_action)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
