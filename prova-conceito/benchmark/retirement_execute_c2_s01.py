"""E11-M00F: aposentadoria estritamente de C2-S01 apos aceite explicito.

Sem --execute: APENAS PREVIA. --execute requer frase exata de autorizacao,
SHA do HEAD testado, inventario/ZIP/backup integro e journal novo em D:.
Nao aceita labels, IDs ou cenarios alternativos. NUNCA faz prune/forca.
Falha parcial: STOP e preservar journal; nunca repetir automaticamente.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from benchmark.ownership import IMAGE_ID, check_labels
from benchmark.retirement_preview_c2 import (
    BASE, LABEL, ROLES, RUN_ID, plan_s01_retirement,
)

APPROVAL = "AUTORIZO_DESMOBILIZAR_EXCLUSIVAMENTE_C2_M01_S01"
ZIP_SHA256 = "6e448f37f80456590af80309586e245b038b6e143400cd4b4d325766dd8d5bd6"
NETWORK_ID = "0748fe465ec0d1cf31302808b403bdf85522fd70305f30e6067d4c58737f18ae"
CONTAINER_IDS = {
    "attribute-source": "56439673aed7c8c19cf2b365cfa26c445cf7a59d47e7f73989957d6f7b7dd4b0",
    "logic-engine": "a0cf7976754f5628e26d5bc1f26ac47a1f866ccb357214b58c48aa04ffbefe32",
    "rule-executor": "2cb6bc4bf321141b2e07ce7b9cb4c7162e2ae72b26c40554c2385bbb55501ac9",
    "client": "6dbbf1bce2f82a931530fc8fa19703a87debf244879af227750c0f672bbaaae0",
}
STOP_ORDER = ("client", "attribute-source", "logic-engine", "rule-executor")
JOURNAL_NAME = "C2-m01-s01-retirement.jsonl"


def expected_name(role):
    return BASE + ("-benchmark-client" if role == "client" else "-" + role)


def validate_frozen_plan(plan):
    """Nao confiar em IDs fornecidos pela CLI ou copiados de outra rodada."""
    if (plan.get("status") != "RETIREMENT_PREVIEW_READONLY_PASS_NOT_AUTHORIZATION"
            or plan.get("run_id") != RUN_ID or plan.get("scenario") != "C2"
            or plan.get("zip_sha256") != ZIP_SHA256
            or plan.get("backup_sha256") != ZIP_SHA256
            or plan.get("delete_authorized") is not False
            or plan.get("commands") != []
            or plan.get("requires_explicit_operator_approval") is not True
            or plan.get("requires_tested_execution_procedure") is not True):
        raise ValueError("STOP: previa nao corresponde a C2-S01 congelada")
    actual = plan.get("resource_immutable_ids") or {}
    if (actual.get("network_id") != NETWORK_ID
            or actual.get("container_ids") != CONTAINER_IDS):
        raise ValueError("STOP: ID de rede/container diferente do inventario real congelado")
    proposed = plan.get("expected_new_resource_names") or {}
    expected = [expected_name(x) for x in
                ("attribute-source", "logic-engine", "rule-executor", "client")]
    if (proposed.get("network") != BASE or proposed.get("containers") != expected
            or plan.get("historic_resources_mutated") is not False):
        raise ValueError("STOP: allowlist de nomes inesperada")
    inventory = plan.get("inventory") or {}
    if (inventory.get("containers") != 4 or inventory.get("networks") != 1
            or inventory.get("new_kube_namespaces") != 0
            or inventory.get("unexpected_new_resources") != 0):
        raise ValueError("STOP: inventario nao e uma bancada unica")


def inspect_target(role, query, must_run):
    """Confere identidade integral antes de CADA stop/rm, inclusive labels."""
    identifier = CONTAINER_IDS[role]
    raw = json.loads(query("docker", "container", "inspect", identifier))
    if not isinstance(raw, list) or len(raw) != 1:
        raise ValueError("STOP: inspecao de container incompleta")
    item = raw[0]
    config = item.get("Config") or {}
    check_labels(config.get("Labels"), RUN_ID)
    networks = (item.get("NetworkSettings") or {}).get("Networks") or {}
    state = item.get("State") or {}
    if (item.get("Id") != identifier
            or item.get("Name", "").lstrip("/") != expected_name(role)
            or item.get("Image") != IMAGE_ID
            or set(networks) != {BASE}
            or state.get("Running") is not must_run):
        raise ValueError(f"STOP: identidade/estado de {role} divergente")
    return state


def inspect_network(query, require_empty):
    raw = json.loads(query("docker", "network", "inspect", NETWORK_ID))
    if not isinstance(raw, list) or len(raw) != 1:
        raise ValueError("STOP: rede ausente/ambigua")
    net = raw[0]
    check_labels(net.get("Labels"), RUN_ID)
    if net.get("Id") != NETWORK_ID or net.get("Name") != BASE:
        raise ValueError("STOP: rede nao corresponde ao ID permitido")
    endpoints = net.get("Containers") or {}
    if require_empty:
        if endpoints:
            raise ValueError("STOP: rede ainda tem endpoints")
    elif set(endpoints) != set(CONTAINER_IDS.values()):
        raise ValueError("STOP: endpoints diferentes dos quatro contêineres")
    return net


def journal_append(stream, stage, **extra):
    stream.write(json.dumps({
        "utc": datetime.now(timezone.utc).isoformat(),
        "stage": stage, "run_id": RUN_ID, **extra,
    }, ensure_ascii=False, sort_keys=True) + "\n")
    stream.flush()
    os.fsync(stream.fileno())


def execute_only_s01(plan, query, action, journal_path, approval, approved_head, head):
    """Mutante, apenas se C2-S01/ZIP/IDs/aceite/HEAD/journal todos validos."""
    if approval != APPROVAL or not isinstance(approved_head, str):
        raise ValueError("STOP: aceite explicito C2-S01 ausente")
    if (head != approved_head or len(head) != 40
            or any(c not in "0123456789abcdef" for c in head)):
        raise ValueError("STOP: HEAD diferente da versao aprovada/testada")
    validate_frozen_plan(plan)
    inspect_network(query, require_empty=False)
    for role in ROLES:
        inspect_target(role, query, must_run=True)
    path = Path(journal_path)
    if (path.name != JOURNAL_NAME or path.exists() or path.is_symlink()
            or not path.parent.is_dir()):
        raise ValueError("STOP: journal existente ou pasta invalida")
    # Criacao exclusiva impede execucao dupla. Escrever antes de cada comando.
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        journal_append(stream, "AUTHORIZED_BEGIN", git_sha=head,
                       zip_sha256=ZIP_SHA256, network_id=NETWORK_ID,
                       container_ids=CONTAINER_IDS.copy())
        try:
            for role in STOP_ORDER:
                identifier = CONTAINER_IDS[role]
                inspect_target(role, query, must_run=True)
                journal_append(stream, "BEFORE_STOP", role=role, id=identifier)
                action("docker", "container", "stop", "--time", "10", identifier)
                journal_append(stream, "AFTER_STOP", role=role, id=identifier)
                inspect_target(role, query, must_run=False)

            for role in STOP_ORDER:
                identifier = CONTAINER_IDS[role]
                inspect_target(role, query, must_run=False)
                journal_append(stream, "BEFORE_RM", role=role, id=identifier)
                action("docker", "container", "rm", identifier)
                journal_append(stream, "AFTER_RM", role=role, id=identifier)
                names = query("docker", "ps", "-a", "--format", "{{.Names}}").splitlines()
                if expected_name(role) in names:
                    raise ValueError("STOP: container ainda existe apos rm")

            inspect_network(query, require_empty=True)
            journal_append(stream, "BEFORE_NETWORK_RM", id=NETWORK_ID)
            action("docker", "network", "rm", NETWORK_ID)
            journal_append(stream, "AFTER_NETWORK_RM", id=NETWORK_ID)
            names = query("docker", "network", "ls", "--format", "{{.Name}}").splitlines()
            if BASE in names:
                raise ValueError("STOP: rede ainda existe")
            journal_append(stream, "COMPLETE", status="S01_RETIREMENT_COMPLETE")
        except BaseException as exc:
            journal_append(stream, "INTERRUPTED_DO_NOT_RETRY",
                           error=f"{type(exc).__name__}: {exc}")
            raise
    return {
        "status": "S01_RETIREMENT_COMPLETE",
        "run_id": RUN_ID, "journal": str(path),
        "containers_stopped_removed": 4,
        "network_removed": 1, "historic_resources_targeted": 0,
        "zip_original_or_backup_modified": False,
        "other_resources_retirement_authorized": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--backup", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--approve")
    parser.add_argument("--approved-head")
    args = parser.parse_args(argv)

    from benchmark.docker_c2 import checked
    plan = plan_s01_retirement(args.primary, args.backup, checked)
    validate_frozen_plan(plan)
    if not args.execute:
        if args.approve or args.approved_head:
            parser.error("na previa read-only, nao fornecer autorizacao")
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        print("MODO: SOMENTE LEITURA; NENHUM RECURSO ALTERADO")
        return 0

    if args.approve != APPROVAL or not args.approved_head:
        parser.error("execucao exige aceite C2-S01 e SHA exato testado")
    if args.backup.name != "C2-m01-s01.zip" or args.primary.name != "C2-m01-s01.zip":
        parser.error("caminhos nao correspondem ao ZIP S01")
    if os.name == "nt" and args.backup.drive.upper() != "D:":
        parser.error("backup precisa estar no volume D:")
    if (args.primary.resolve() == args.backup.resolve()
            or args.primary.parent.resolve() == args.backup.parent.resolve()):
        parser.error("backup nao e volume externo ao original")
    if checked("git", "branch", "--show-current").strip() != "tcc2/desenvolvimento":
        raise ValueError("STOP: branch Git incorreta")
    if checked("git", "status", "--porcelain").strip():
        raise ValueError("STOP: working tree Git nao esta limpa")
    sha = checked("git", "rev-parse", "HEAD").strip()
    journal = args.backup.with_name(JOURNAL_NAME)
    result = execute_only_s01(plan, checked, checked, journal,
                              args.approve, args.approved_head, sha)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
