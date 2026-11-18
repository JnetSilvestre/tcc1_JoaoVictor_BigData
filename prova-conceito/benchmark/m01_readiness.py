"""E11-M00I: matriz fixa e auditoria pre-campanha, SOMENTE LEITURA.

Nao importa subprocess para mutacao; todas as consultas externas sao get/
inspect/list. Nenhuma das 30 rodadas e iniciada por este modulo.
"""
import argparse
import json
from pathlib import Path
import re

from benchmark.backup_integrity import compare_backup_pair, sha256_file
from benchmark.environment_snapshot import capture_environment, run_readonly
from benchmark.lifecycle_audit import audit_archive
from benchmark.runtime_gate import assess_capacity
from benchmark.campaign_exclusivity import NEW_DOCKER, NEW_KUBE

FIXTURE_SHA = "26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551"
EXPECTED_EFFECTS_SHA = "430e61ca65d582f0441eb49649d9577905d0f8fa9e1d5ff04bc01eb53eda7b1c"
APPROVED_IMAGE_ID = "sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a"
ORDER = (
    ("C2", "C3", "C4"), ("C3", "C4", "C2"),
    ("C4", "C2", "C3"), ("C4", "C3", "C2"),
    ("C3", "C2", "C4"), ("C2", "C4", "C3"),
    ("C2", "C3", "C4"), ("C3", "C4", "C2"),
    ("C4", "C2", "C3"), ("C4", "C3", "C2"),
)
ARCHIVES = {
    "C2": {"event": "E11-M00E", "leaf": "C2-m01-s01.zip",
           "backup": "C2-m01-s01.zip", "journal": "C2-m01-s01-retirement.jsonl",
           "last_status": "S01_RETIREMENT_COMPLETE",
           "sha": "6e448f37f80456590af80309586e245b038b6e143400cd4b4d325766dd8d5bd6"},
    "C3": {"event": "E11-M00G", "leaf": "C3-m01-s01/resultado.zip",
           "backup": "C3-m01-s01.zip", "journal": "C3-m01-s01-retirement.jsonl",
           "last_status": "C3_S01_RETIREMENT_COMPLETE",
           "sha": "463f56042536c95874a4f36dadfd5fd211fec18325132704c9f585d2ec6e80c8"},
    "C4": {"event": "E11-M00H", "leaf": "C4-m01-s01/resultado.zip",
           "backup": "C4-m01-s01.zip", "journal": "C4-m01-s01-retirement.jsonl",
           "last_status": "C4_S01_RETIREMENT_COMPLETE",
           "sha": "8e2f5a0918bcfe398e3d76b737973a08f35c59d62bfc9c03eea1939b29883f27"},
}


def full_schedule():
    """Retorna as 30 identidades imutaveis do protocolo pré-registrado."""
    entries = []
    for index, scenarios in enumerate(ORDER, start=1):
        if set(scenarios) != {"C2", "C3", "C4"}:
            raise ValueError("STOP: bloco incompleto ou repetido")
        label = f"m01-b{index:02d}"
        for position, scenario in enumerate(scenarios, start=1):
            run_id = f"e11-{scenario.lower()}-{label}"
            entries.append({
                "block": f"B{index:02d}", "position": position,
                "scenario": scenario, "label": label, "run_id": run_id,
                "resource_base": f"tcc2-pon-e11-{scenario.lower()}-{label}",
                "requests": 1000, "seed": 20260502,
                "measurement_mode": "timing_only",
            })
    ids = [x["run_id"] for x in entries]
    if len(entries) != 30 or len(set(ids)) != 30:
        raise ValueError("STOP: a matriz nao tem 30 IDs exclusivos")
    return entries


def check_completed_sacrificial_archives(home, backup_root):
    """Valida os 3 ZIPs e journals de retirada sem alterar arquivos."""
    home, backup_root = Path(home), Path(backup_root)
    result = {}
    for scenario, item in ARCHIVES.items():
        primary = home / "TCC2-Evidencias" / item["event"] / item["leaf"]
        backup = backup_root / item["event"] / item["backup"]
        journal = backup_root / item["event"] / item["journal"]
        if not journal.is_file() or journal.is_symlink():
            raise ValueError(f"STOP: journal de retirada {scenario} ausente/nao confiavel")
        lines = [s for s in journal.read_text(encoding="utf-8-sig").splitlines() if s.strip()]
        if not lines:
            raise ValueError(f"STOP: journal {scenario} vazio")
        last = json.loads(lines[-1])
        if (last.get("stage") != "COMPLETE"
                or last.get("status") != item["last_status"]
                or last.get("run_id") != f"e11-{scenario.lower()}-m01-s01"):
            raise ValueError(f"STOP: journal {scenario} nao comprova retirada")
        if sha256_file(primary) != item["sha"]:
            raise ValueError(f"STOP: ZIP de {scenario} alterado")
        audit = audit_archive(primary, scenario, "m01-s01",
                              f"e11-{scenario.lower()}-m01-s01")
        copy = compare_backup_pair(primary, backup)
        if (audit.get("status") != "ZIP_INTEGRITY_VERIFIED_NOT_DELETION_AUTHORIZATION"
                or audit.get("zip_sha256") != item["sha"]
                or copy.get("status") != "BACKUP_BYTES_VERIFIED_NO_CLEANUP_AUTHORIZATION"
                or copy.get("zip_sha256") != item["sha"]
                or copy.get("different_filesystem_volume") is not True
                or copy.get("delete_authorized") is not False):
            raise ValueError(f"STOP: ZIP ou backup {scenario} invalido")
        result[scenario] = {
            "qualification": "FUNCTIONAL_PASS_SACRIFICIAL_EXCLUDED_FROM_M01",
            "retirement": "COMPLETE_WITH_UID_OR_ID_GUARD",
            "zip_sha256": item["sha"],
            "backup_distinct_filesystem_volume": True,
        }
    return result


def inspect_global_exclusivity(query):
    """Inclui Docker M01 parados, redes e todos os namespaces."""
    containers = query("docker", "ps", "-a", "--format", "{{.Names}}").splitlines()
    networks = query("docker", "network", "ls", "--format", "{{.Name}}").splitlines()
    raw = json.loads(query("kubectl", "--context", "kind-tcc2-pon",
                           "get", "namespaces", "-o", "json"))
    names = [i["metadata"]["name"] for i in raw["items"]]
    present = {
        "docker_containers": sorted(x for x in containers if NEW_DOCKER.fullmatch(x)),
        "docker_networks": sorted(x for x in networks if
                                  re.fullmatch(r"tcc2-pon-e11-c2-m[a-z0-9-]+", x)),
        "kube_namespaces": sorted(x for x in names if NEW_KUBE.fullmatch(x)),
    }
    if any(present.values()):
        raise ValueError(f"STOP: ainda existe bancada M01 nova: {present}")
    if not {"default", "tcc2-pon", "tcc2-pon-c4"}.issubset(names):
        raise ValueError("STOP: namespaces historicos de referencia nao encontrados")
    return {"status": "NO_NEW_M01_RESOURCES_PRESENT", "historic_namespaces_not_targeted": True}


def prepare_readonly_report(home, backup_root, fixture_path, query, capture):
    """Gate anterior à primeira B01, sem permitir --execute."""
    if query("git", "branch", "--show-current").strip() != "tcc2/desenvolvimento":
        raise ValueError("STOP: branch incorreta")
    if query("git", "status", "--porcelain").strip():
        raise ValueError("STOP: arvore Git modificada")
    git_sha = query("git", "rev-parse", "HEAD").strip()
    if not re.fullmatch(r"[0-9a-f]{40}", git_sha):
        raise ValueError("STOP: Git SHA invalido")
    if sha256_file(fixture_path) != FIXTURE_SHA:
        raise ValueError("STOP: fixture canônica divergente")
    archives = check_completed_sacrificial_archives(home, backup_root)
    exclusive = inspect_global_exclusivity(query)
    host = capture("C4", "e11-c4-m01-b01")
    capacity = assess_capacity(host)
    nodes = host.get("node_allocatable") or {}
    if set(nodes) != {"tcc2-pon-worker", "tcc2-pon-control-plane"}:
        raise ValueError("STOP: cluster kind nao tem apenas os 2 nos previstos")
    schedule = full_schedule()
    return {
        "status": "M01_READONLY_BASELINE_PASS_NOT_EXECUTION_AUTHORIZATION",
        "git_sha": git_sha,
        "fixture_sha256": FIXTURE_SHA,
        "oracle_sha256": EXPECTED_EFFECTS_SHA,
        "image_id": APPROVED_IMAGE_ID,
        "capacity_status": capacity["status"],
        "windows_ram_free_bytes": capacity["windows_free_bytes"],
        "project_disk_free_bytes": capacity["disk_free_bytes"],
        "node_uids": {name: row.get("uid") for name, row in nodes.items()},
        "sacrificial_archives": archives,
        "exclusive": exclusive,
        "matrix": schedule,
        "matrix_size": len(schedule),
        "first_round": schedule[0],
        "cpu_ram_comparison_approved": False,
        "main_b01_started": False,
        "generalized_retirement_lifecycle_approved": False,
        "start_authorized": False,
        "mutation_commands": [],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--backup-root", type=Path,
                        default=Path("D:/TCC2-Backup"))
    parser.add_argument("--home", type=Path, default=Path.home())
    args = parser.parse_args(argv)
    result = prepare_readonly_report(
        args.home, args.backup_root, args.fixture, run_readonly,
        capture_environment)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("PREPARACAO READ-ONLY E11-M01: PASS, EXECUCAO PRINCIPAL BLOQUEADA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
