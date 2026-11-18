"""E11-M00F: prévia de desmobilização EXCLUSIVA de C2-S01, SEM mutações.

Não aceita --execute nem possui rotinas de stop/rm/delete. Falha fechada.
Confere evidências de duas cópias, identidades de contêiner/rede e
ausência de outros recursos novos antes de apresentar a allowlist.
"""
import argparse
import json
import re
from pathlib import Path
from zipfile import ZipFile

from benchmark.backup_integrity import compare_backup_pair
from benchmark.lifecycle_audit import audit_archive, review_retirement_packet
from benchmark.ownership import capture_docker_ownership

SCENARIO = "C2"
LABEL = "m01-s01"
RUN_ID = "e11-c2-m01-s01"
BASE = "tcc2-pon-e11-c2-m01-s01"
ROLES = ("attribute-source", "logic-engine", "rule-executor", "client")
NEW_C2_CONTAINER = re.compile(
    r"^tcc2-pon-e11-c2-m[a-z0-9-]+-(?:attribute-source|logic-engine|rule-executor|benchmark-client)$")
NEW_C2_NETWORK = re.compile(r"^tcc2-pon-e11-c2-m[a-z0-9-]+$")
NEW_KUBE_NAMESPACE = re.compile(r"^tcc2-pon-e11-c[34]-m[a-z0-9-]+$")


def verify_live_inventory(ownership, query):
    """Confirma somente UMA nova bancada C2-S01, inclusive recursos parados."""
    expected_names = {ownership["containers"][r]["name"] for r in ROLES}
    current_names = set(query("docker", "ps", "-a", "--format", "{{.Names}}").splitlines())
    observed_new = {x for x in current_names if NEW_C2_CONTAINER.fullmatch(x)}
    if observed_new != expected_names:
        raise ValueError("STOP: inventario de novos containers difere da bancada unica")
    names = set(query("docker", "network", "ls", "--format", "{{.Name}}").splitlines())
    new_nets = {x for x in names if NEW_C2_NETWORK.fullmatch(x)}
    if new_nets != {BASE}:
        raise ValueError("STOP: redes M01 inesperadas/ausentes")
    kube = json.loads(query(
        "kubectl", "--context", "kind-tcc2-pon", "get", "namespaces", "-o", "json"))
    if any(NEW_KUBE_NAMESPACE.fullmatch(x["metadata"]["name"])
           for x in kube["items"]):
        raise ValueError("STOP: outra bancada nova Kubernetes presente")

    info = json.loads(query("docker", "network", "inspect", BASE))
    if not isinstance(info, list) or len(info) != 1:
        raise ValueError("STOP: rede inesperada")
    net = info[0]
    if net.get("Id") != ownership["network"]["id"]:
        raise ValueError("STOP: identidade da rede alterada")
    endpoint_map = net.get("Containers")
    expected_ids = {ownership["containers"][r]["id"] for r in ROLES}
    if not isinstance(endpoint_map, dict) or set(endpoint_map) != expected_ids:
        raise ValueError("STOP: conectados inesperados na rede M01")
    for role in ROLES:
        record = ownership["containers"][role]
        if (endpoint_map[record["id"]].get("Name") != record["name"]):
            raise ValueError("STOP: endpoint Docker com nome inesperado")
        inspected = json.loads(query("docker", "inspect", record["id"]))
        if not isinstance(inspected, list) or len(inspected) != 1:
            raise ValueError("STOP: inspect por ID incompleto")
        item = inspected[0]
        if (item.get("Id") != record["id"]
                or item.get("Name", "").lstrip("/") != record["name"]
                or set((item.get("NetworkSettings") or {}).get("Networks") or {})
                != {BASE}):
            raise ValueError("STOP: contêiner trocado ou conectado a outra rede")
    return {"containers": len(expected_names), "networks": 1,
            "new_kube_namespaces": 0, "unexpected_new_resources": 0}


def plan_s01_retirement(primary, backup, query):
    """Plano documental read-only, sem comandos e sem permissão de exclusão."""
    audit = audit_archive(primary, SCENARIO, LABEL, RUN_ID)
    verified_backup = compare_backup_pair(primary, backup)
    if verified_backup.get("different_filesystem_volume") is not True:
        raise ValueError("STOP: copia nao esta em outro volume")
    current = capture_docker_ownership(LABEL, RUN_ID, query)
    with ZipFile(primary) as archive:
        original = json.loads(archive.read("ownership-start.json"))
    if original.get("network") != current.get("network"):
        raise ValueError("STOP: ID de rede diferente do ZIP")
    if original.get("containers") != current.get("containers"):
        raise ValueError("STOP: IDs/nomes dos 4 conteineres diferentes do ZIP")
    review = review_retirement_packet(
        SCENARIO, LABEL, RUN_ID, audit, current, verified_backup)
    inventory = verify_live_inventory(current, query)
    if review.get("delete_authorized") is not False or review.get("commands") != []:
        raise ValueError("STOP: review retornou acao inesperada")
    return {
        "status": "RETIREMENT_PREVIEW_READONLY_PASS_NOT_AUTHORIZATION",
        "scenario": SCENARIO, "run_id": RUN_ID,
        "zip_sha256": audit["zip_sha256"],
        "backup_sha256": verified_backup["zip_sha256"],
        "inventory": inventory,
        "expected_new_resource_names": review["expected_new_resource_names"],
        "resource_immutable_ids": review["resource_immutable_ids"],
        "historic_resources_mutated": False,
        "requires_explicit_operator_approval": True,
        "requires_tested_execution_procedure": True,
        "delete_authorized": False, "commands": [],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--backup", type=Path, required=True)
    args = parser.parse_args(argv)
    # checked() executa apenas os comandos de leitura definidos nas funções.
    from benchmark.docker_c2 import checked
    result = plan_s01_retirement(args.primary, args.backup, checked)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("PREVIA SOMENTE LEITURA: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
