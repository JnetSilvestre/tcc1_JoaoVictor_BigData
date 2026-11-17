"""E11-M00C: auditar ZIP e propor identidades de nova bancada, SEM remocao.

Nao importa subprocess, docker, kubectl ou shutil.rmtree. Nenhuma rotina
neste modulo interrompe ou deleta qualquer recurso, antigo ou novo.
"""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

from benchmark.measurement_profile import TIMING_ONLY, require_new_timing_identity

MANDATORY = frozenset({
    "manifest.json", "validation.json", "inputs.jsonl", "expected.jsonl",
    "states-cold.json", "preflight-uniform.json", "environment.json",
    "snapshot-response.json", "metrics-status.json", "checksums.sha256",
    "capacity-gate.json", "effective-quotas.json",
    "campaign-exclusivity.json", "ownership-start.json",
})


def sha256_bytes(payload):
    return hashlib.sha256(payload).hexdigest()


def audit_archive(zip_path, scenario, label, run_id):
    """Verifica CRC, hashes de TODOS membros, status e propriedade da rodada."""
    require_new_timing_identity(TIMING_ONLY, scenario, label, run_id)
    path = Path(zip_path)
    if not path.is_file():
        raise ValueError("ZIP de evidencias ausente")
    with ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("ZIP com nomes duplicados")
        files = set(names)
        if not MANDATORY.issubset(files):
            raise ValueError(f"ZIP incompleto: {sorted(MANDATORY-files)}")
        if archive.testzip() is not None:
            raise ValueError("CRC ZIP invalido")
        checksums = archive.read("checksums.sha256").decode("utf-8")
        observed = {}
        for line in checksums.splitlines():
            if "  " not in line:
                raise ValueError("linha de checksum malformada")
            sha, name = line.split("  ", 1)
            if name in observed or name == "checksums.sha256" or name not in files:
                raise ValueError("membro listado invalido em checksums")
            if len(sha) != 64 or sha256_bytes(archive.read(name)) != sha:
                raise ValueError(f"SHA-256 divergente: {name}")
            observed[name] = sha
        if set(observed) != files - {"checksums.sha256"}:
            raise ValueError("checksums nao cobrem todo ZIP")
        manifest = json.loads(archive.read("manifest.json"))
        validation = json.loads(archive.read("validation.json"))
        if manifest.get("scenario") != scenario or manifest.get("run_id") != run_id:
            raise ValueError("manifest sem propriedade da bancada")
        if manifest.get("measurement_mode") != TIMING_ONLY:
            raise ValueError("modo de benchmark diferente de timing_only")
        if validation.get("status") != "PASS":
            raise ValueError("arquivamento de tentativa FAIL nao autoriza aposentadoria")
        if validation.get("started_snapshot") is not True or validation.get("started_changes") is not True:
            raise ValueError("execucao incompleta/sem mutacao")
        env = json.loads(archive.read("environment.json"))
        if env.get("scenario") != scenario or env.get("run_id") != run_id:
            raise ValueError("environment nao pertence a bancada")
        cold = json.loads(archive.read("preflight-uniform.json"))
        if cold.get("status") != "PASS_COLD_READ_ONLY":
            raise ValueError("preflight frio uniforme ausente/invalido")
        capacity = json.loads(archive.read("capacity-gate.json"))
        if capacity.get("status") != "CAPACITY_SAFETY_GATE_PASS_NOT_PERFORMANCE_APPROVAL":
            raise ValueError("gate de RAM/disco nao aprovado")
        effective = json.loads(archive.read("effective-quotas.json"))
        if effective.get("status") != "EFFECTIVE_LIMITS_ALL_FOUR_PASS":
            raise ValueError("cgroup real nao aprovado")
        if effective.get("scenario") != scenario or set(effective.get("roles", {})) != {
                "attribute-source", "logic-engine", "rule-executor", "client"}:
            raise ValueError("identidade/quantidade de papeis do cgroup divergente")
        if any(x.get("status") != "EFFECTIVE_CGROUP_LIMITS_PASS_NOT_USAGE_COMPARISON"
               for x in effective["roles"].values()):
            raise ValueError("cgroup de papel divergente")
        exclusivity = json.loads(archive.read("campaign-exclusivity.json"))
        if (exclusivity.get("status") != "ONE_NEW_CAMPAIGN_BENCH_ONLY"
                or exclusivity.get("scenario") != scenario
                or exclusivity.get("historic_resources_mutated") is not False):
            raise ValueError("exclusividade de bancada nao comprovada")
        ownership = json.loads(archive.read("ownership-start.json"))
        if (ownership.get("status") != "NEW_BENCH_OWNERSHIP_READONLY_PASS"
                or ownership.get("scenario") != scenario
                or ownership.get("run_id") != run_id
                or ownership.get("delete_authorized") is not False
                or ownership.get("commands") != []):
            raise ValueError("ownership nao verificado")
        if scenario == "C2":
            if (ownership.get("network", {}).get("name") !=
                    f"tcc2-pon-e11-c2-{label}" or
                    set(ownership.get("containers", {})) != {
                        "attribute-source", "logic-engine", "rule-executor", "client"}):
                raise ValueError("IDs de propriedade C2 ausentes")
        else:
            if (ownership.get("namespace", {}).get("name") !=
                    f"tcc2-pon-e11-{scenario.lower()}-{label}" or
                    set(ownership.get("pods", {})) != {
                        "attribute-source", "logic-engine", "rule-executor", "client"}):
                raise ValueError("UIDs de propriedade kind ausentes")


    return {
        "status": "ZIP_INTEGRITY_VERIFIED_NOT_DELETION_AUTHORIZATION",
        "scenario": scenario, "run_id": run_id,
        "zip_name": path.name,
        "zip_sha256": sha256_bytes(path.read_bytes()),
        "members": len(files),
        "functional_pass_verified": True,
        "delete_authorized": False,
        "note": "Este laudo verifica evidencia, NAO autoriza/realiza stop ou delete",
    }


def retirement_review_only(scenario, label, run_id, audit):
    """Allowlist positiva, sem gerar comandos executaveis de stop/delete."""
    require_new_timing_identity(TIMING_ONLY, scenario, label, run_id)
    if (audit.get("status") != "ZIP_INTEGRITY_VERIFIED_NOT_DELETION_AUTHORIZATION"
            or audit.get("scenario") != scenario or audit.get("run_id") != run_id
            or audit.get("delete_authorized") is not False):
        raise ValueError("sem auditoria externa de propriedade e integridade")
    base = f"tcc2-pon-e11-{scenario.lower()}-{label}"
    if scenario == "C2":
        proposed = {
            "network": base,
            "containers": [f"{base}-{role}" for role in (
                "attribute-source", "logic-engine", "rule-executor", "benchmark-client")],
        }
    else:
        proposed = {"namespace": base}
    return {
        "status": "REVIEW_ONLY_NO_ACTION",
        "run_id": run_id, "scenario": scenario,
        "expected_new_resource_names": proposed,
        "must_verify_runtime_ids_and_provenance_before_any_future_action": True,
        "may_touch_historical_resources": False,
        "delete_authorized": False,
        "commands": [],
        "note": "Nenhum stop, delete, rm ou prune implementado; sujeito a allowlist UID/ID e aceite em fase futura",
    }
