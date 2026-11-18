"""E11-M00H: revisão/retirada C4-S01, somente namespace novo com UID congelado.

Sem --execute: apenas consultas. Com --execute: exige frase digitada,
HEAD completo aprovado, ZIP original+backup e UIDs/labels exatos.
Envio de DELETE com DeleteOptions.preconditions.uid (API server).
Sem --force, sem limpeza de historicos, sem retry em falha.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from benchmark.backup_integrity import compare_backup_pair, sha256_file
from benchmark.lifecycle_audit import audit_archive, review_retirement_packet
from benchmark.ownership import capture_kind_ownership, check_labels
from benchmark.retirement_preview_c2 import NEW_C2_CONTAINER, NEW_C2_NETWORK, NEW_KUBE_NAMESPACE

CONTEXT = "kind-tcc2-pon"
NS = "tcc2-pon-e11-c4-m01-s01"
LABEL = "m01-s01"
RUN_ID = "e11-c4-m01-s01"
UID = "08c6e166-4fc3-4aaf-b1d4-67ac5f628a30"
ZIP_SHA = "8e2f5a0918bcfe398e3d76b737973a08f35c59d62bfc9c03eea1939b29883f27"
APPROVAL = "AUTORIZO_DESMOBILIZAR_EXCLUSIVAMENTE_C4_M01_S01"
JOURNAL = "C4-m01-s01-retirement.jsonl"
DELETE_OPTIONS = "C4-m01-s01-delete-options.json"
ROLES = {"attribute-source", "logic-engine", "rule-executor", "client"}
SERVICE_NAMES = {"attribute-source", "logic-engine", "rule-executor"}
ALLOWED_OTHER_OBJECTS = {
    "Deployment": SERVICE_NAMES,
    "Service": SERVICE_NAMES,
    "ConfigMap": {"e11-c4-config", "kube-root-ca.crt"},
    "ServiceAccount": {"default"},
}
INVENTORY_TYPES = (
    "pods,deployments,replicasets,services,configmaps,serviceaccounts,"
    "persistentvolumeclaims,jobs,cronjobs,networkpolicies,ingresses,"
    "secrets,roles,rolebindings"
)


def parse_one(value):
    return json.loads(value)


def namespaces(query):
    raw = parse_one(query("kubectl", "--context", CONTEXT,
                          "get", "namespaces", "-o", "json"))
    rows = {}
    for item in raw["items"]:
        m = item["metadata"]
        if m["name"] in rows:
            raise ValueError("STOP: namespace duplicado")
        rows[m["name"]] = m["uid"]
    return rows


def verify_inventory(query, archived):
    raw = parse_one(query("kubectl", "--context", CONTEXT, "-n", NS,
                          "get", INVENTORY_TYPES, "-o", "json"))
    kinds = {}
    replicas = []
    for item in raw["items"]:
        kind = item["kind"]
        meta = item["metadata"]
        if meta.get("namespace") != NS:
            raise ValueError("STOP: objeto fora da C4-S01")
        name = meta["name"]
        if kind == "ReplicaSet":
            replicas.append(item)
        else:
            kinds.setdefault(kind, set()).add(name)
    expected_pods = {x["name"] for x in archived["pods"].values()}
    if kinds.pop("Pod", set()) != expected_pods:
        raise ValueError("STOP: Pods adicionais, ausentes ou renomeados")
    for kind, expected in ALLOWED_OTHER_OBJECTS.items():
        if kinds.pop(kind, set()) != expected:
            raise ValueError(f"STOP: objetos {kind} nao correspondem ao manifesto")
    if kinds:
        raise ValueError(f"STOP: tipo ou objeto alheio presente: {kinds!r}")
    if len(replicas) != 3:
        raise ValueError("STOP: esperado exatamente um ReplicaSet por servico")
    seen_roles = set()
    for rs in replicas:
        meta = rs["metadata"]
        role = (meta.get("labels") or {}).get("app")
        refs = meta.get("ownerReferences") or []
        if (role not in SERVICE_NAMES or role in seen_roles
                or len(refs) != 1 or refs[0].get("kind") != "Deployment"
                or refs[0].get("name") != role
                or refs[0].get("controller") is not True):
            raise ValueError("STOP: ReplicaSet fora da cadeia de propriedade")
        seen_roles.add(role)
    if seen_roles != SERVICE_NAMES:
        raise ValueError("STOP: ReplicaSets incompletos")
    return {"objects_approved": len(raw["items"]), "replicasets": 3}


def preview(primary, backup, query):
    audit = audit_archive(primary, "C4", LABEL, RUN_ID)
    copy = compare_backup_pair(primary, backup)
    if audit["zip_sha256"] != ZIP_SHA or copy["zip_sha256"] != ZIP_SHA:
        raise ValueError("STOP: ZIP/backup diferentes do C4-S01 aprovado")
    if copy.get("different_filesystem_volume") is not True:
        raise ValueError("STOP: backup no mesmo volume")

    live = capture_kind_ownership("C4", LABEL, RUN_ID, query)
    with __import__("zipfile").ZipFile(primary) as zf:
        archived = parse_one(zf.read("ownership-start.json"))
    if (archived.get("namespace") != live.get("namespace")
            or archived.get("pods") != live.get("pods")
            or live["namespace"].get("uid") != UID):
        raise ValueError("STOP: Pod UID/containerID ou Namespace UID alterado")
    review = review_retirement_packet("C4", LABEL, RUN_ID, audit, live, copy)
    if review.get("delete_authorized") is not False or review.get("commands") != []:
        raise ValueError("STOP: review indevidamente autoriza mutacao")

    ns = parse_one(query("kubectl", "--context", CONTEXT,
                         "get", "namespace", NS, "-o", "json"))
    meta = ns.get("metadata") or {}
    if (meta.get("name") != NS or meta.get("uid") != UID
            or meta.get("deletionTimestamp")):
        raise ValueError("STOP: namespace original nao esta ativo/imutavel")
    check_labels(meta.get("labels"), RUN_ID)

    docker_names = query("docker", "ps", "-a", "--format", "{{.Names}}").splitlines()
    networks = query("docker", "network", "ls", "--format", "{{.Name}}").splitlines()
    if any(NEW_C2_CONTAINER.fullmatch(x) for x in docker_names):
        raise ValueError("STOP: contêiner M01 adicional, mesmo parado")
    if any(NEW_C2_NETWORK.fullmatch(x) for x in networks):
        raise ValueError("STOP: rede Docker M01 adicional")
    ns_owners = namespaces(query)
    if any(NEW_KUBE_NAMESPACE.fullmatch(x) and x != NS for x in ns_owners):
        raise ValueError("STOP: outro namespace M01 coexistente")
    if ns_owners.get(NS) != UID:
        raise ValueError("STOP: namespace foi trocado")
    objects = verify_inventory(query, archived)
    return {
        "status": "C4_S01_RETIREMENT_READONLY_PASS_NOT_AUTHORIZED",
        "run_id": RUN_ID, "namespace": NS, "namespace_uid": UID,
        "pods": archived["pods"], "zip_sha256": ZIP_SHA,
        "backup_volume_distinct": True, "inventory": objects,
        "other_new_resources": 0,
        "delete_authorized": False, "commands": [],
    }


def write_event(handle, stage, **data):
    record = {"time_utc": datetime.now(timezone.utc).isoformat(),
              "stage": stage, "run_id": RUN_ID, **data}
    handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    handle.flush()
    os.fsync(handle.fileno())


def apply_approved_retirement(primary, backup, approval, approved_head, query, action,
                             git_head, journal_path, options_path):
    if approval != APPROVAL:
        raise ValueError("STOP: aceite para desmobilizacao C4-S01 ausente")
    if (git_head != approved_head or len(git_head) != 40
            or any(c not in "0123456789abcdef" for c in git_head)):
        raise ValueError("STOP: SHA Git nao corresponde ao codigo testado")
    packet = preview(primary, backup, query)
    journal_path, options_path = Path(journal_path), Path(options_path)
    if (journal_path.name != JOURNAL or options_path.name != DELETE_OPTIONS
            or journal_path.parent != options_path.parent
            or not journal_path.parent.is_dir()
            or journal_path.exists() or options_path.exists()):
        raise ValueError("STOP: journal/options anteriores ou local errado")
    baseline = namespaces(query)
    with journal_path.open("x", encoding="utf-8", newline="\n") as stream:
        write_event(stream, "AUTHORIZED_BEGIN", git_sha=git_head,
                    namespace_uid=UID, zip_sha256=ZIP_SHA)
        try:
            # Precondicao da API protege contra troca do objeto entre GET e DELETE.
            payload = {
                "apiVersion": "meta.k8s.io/v1", "kind": "DeleteOptions",
                "preconditions": {"uid": UID},
                "propagationPolicy": "Foreground",
            }
            with options_path.open("x", encoding="utf-8", newline="\n") as dst:
                json.dump(payload, dst, indent=2)
                dst.write("\n")
                dst.flush()
                os.fsync(dst.fileno())
            # Novo snapshot imediatamente antes do unico ato mutante.
            again = preview(primary, backup, query)
            if packet != again or namespaces(query) != baseline:
                raise ValueError("STOP: mudou a identidade/topologia antes do DELETE")
            write_event(stream, "BEFORE_UID_PRECONDITIONED_DELETE",
                        namespace=NS, namespace_uid=UID, deleteoptions=str(options_path))
            reply = action("kubectl", "--context", CONTEXT, "delete",
                           "--raw", f"/api/v1/namespaces/{NS}",
                           "-f", str(options_path))
            write_event(stream, "DELETE_REQUEST_ACCEPTED", response=reply[-400:])
            action("kubectl", "--context", CONTEXT,
                   "wait", "--for=delete", f"namespace/{NS}", "--timeout=180s")
            after = namespaces(query)
            if {k: v for k, v in after.items() if k != NS} != {
                k: v for k, v in baseline.items() if k != NS
            } or NS in after:
                raise ValueError("STOP: cluster mudou ou namespace ainda existe")
            if sha256_file(primary) != ZIP_SHA or sha256_file(backup) != ZIP_SHA:
                raise ValueError("STOP: evidencias foram modificadas")
            write_event(stream, "COMPLETE", status="C4_S01_RETIREMENT_COMPLETE",
                        historical_namespace_uids_preserved=True)
        except BaseException as exc:
            write_event(stream, "INTERRUPTED_DO_NOT_RETRY",
                        error=f"{type(exc).__name__}: {exc}")
            raise
    return {"status": "C4_S01_RETIREMENT_COMPLETE",
            "namespace": NS, "namespace_uid_deleted": UID,
            "historic_resources_targeted": 0,
            "original_and_backup_preserved": True,
            "journal": str(journal_path)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--backup", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--approved-head")
    args = parser.parse_args(argv)
    from benchmark.docker_c2 import checked
    packet = preview(args.primary, args.backup, checked)
    if not args.execute:
        print(json.dumps(packet, ensure_ascii=False, indent=2))
        print("C4-S01 PREVIA SOMENTE LEITURA: PASS; NENHUMA EXCLUSAO")
        return 0
    if (args.primary.name != "resultado.zip" or args.backup.name != "C4-m01-s01.zip"
            or os.name == "nt" and args.backup.drive.upper() != "D:"):
        parser.error("ZIP/caminho de backup fora do escopo")
    if not args.approved_head:
        parser.error("SHA de versao testada obrigatorio")
    if checked("git", "branch", "--show-current").strip() != "tcc2/desenvolvimento":
        raise ValueError("STOP: Git branch incorreta")
    if checked("git", "status", "--porcelain").strip():
        raise ValueError("STOP: Git possui alteracoes locais")
    head = checked("git", "rev-parse", "HEAD").strip()
    print(f"ALVO EXCLUSIVO: {NS} UID={UID}")
    print("ACAO: DELETE do namespace NOVO C4-S01 com precondicao UID.")
    print("AS EVIDENCIAS SERÃO PRESERVADAS; nenhum historico sera removido.")
    phrase = input("Digite AUTORIZO_DESMOBILIZAR_EXCLUSIVAMENTE_C4_M01_S01: ").strip()
    if phrase != APPROVAL:
        raise ValueError("STOP: operador nao autorizou exclusao")
    folder = args.backup.parent
    result = apply_approved_retirement(
        args.primary, args.backup, phrase, args.approved_head, checked, checked,
        head, folder / JOURNAL, folder / DELETE_OPTIONS)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
