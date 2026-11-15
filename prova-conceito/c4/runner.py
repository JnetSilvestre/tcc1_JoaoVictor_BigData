"""E10/C4: inicializacao unica + fixture em dois nos kind (um host fisico).

NAO repetir a execucao: um novo snapshot e uma rodada de sete passos
serao aplicados em uma bancada isolada, no namespace tcc2-pon-c4.
Nao altera ou reinicia os Pods do namespace C3.
"""
import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys
from zipfile import ZipFile, ZIP_DEFLATED

from c3 import runner as base

RUN_ID = "c4-e10-i02-v1"
NAMESPACE = "tcc2-pon-c4"
ASSIGNMENT = {
    "attribute-source": "tcc2-pon-worker",
    "logic-engine": "tcc2-pon-control-plane",
    "rule-executor": "tcc2-pon-worker",
}


def configure():
    base.NS = NAMESPACE
    base.RUN_ID = RUN_ID
    base.SCENARIO = "C4"
    base.EXECUTION_LABEL = "E10-C4-FIXTURE"


def check_preflight(output):
    # Nenhum POST pode ocorrer se houver codigo alterado ou metadados incompletos.
    if base.command("git", "branch", "--show-current").strip() != "tcc2/desenvolvimento":
        raise ValueError("branch incorreta")
    if base.command("git", "status", "--porcelain").strip():
        raise ValueError("Git com alteracoes locais")
    base.command("git", "diff", "--quiet", base.BUILD_SHA, "HEAD", "--",
                 "pon", "c1", "Dockerfile", ".dockerignore")
    image = json.loads(base.command("docker", "image", "inspect", base.IMAGE))[0]
    if (image["Id"] != base.IMAGE_ID
            or image["Os"] != "linux" or image["Architecture"] != "amd64"
            or image["Config"]["Labels"].get("org.opencontainers.image.revision") != base.BUILD_SHA):
        raise ValueError("imagem nao corresponde ao C2 aprovado")

    topo = base.topology()
    observed = {role: topo["pods"][role]["node"] for role in base.ROLES}
    if observed != ASSIGNMENT:
        raise ValueError(f"posicionamento multinó C4 incorreto: {observed}")
    if len(set(observed.values())) != 2:
        raise ValueError("C4 nao atravessa dois nos virtuais")
    if len(set(topo["pods"][role]["uid"] for role in base.ROLES)) != 3:
        raise ValueError("Pod UIDs nao distintos")
    if len(set(topo["pods"][role]["container_id"] for role in base.ROLES)) != 3:
        raise ValueError("containers nao distintos")
    image_ids = {topo["pods"][r]["image_id_runtime"] for r in base.ROLES}
    if None in image_ids or len(image_ids) != 1:
        raise ValueError("imagem de runtime divergente entre Pods")

    base.write_json(output / "topology-pre-snapshot.json", topo)
    source_pod = topo["pods"]["attribute-source"]["name"]
    states, logs = {}, {}
    for role in base.ROLES:
        live_status, live = base.http(source_pod, role, "/health/live")
        ready_status, ready = base.http(source_pod, role, "/health/ready")
        state_status, state = base.http(source_pod, role, "/state")
        if (live_status != 200 or live["service"] != role
                or ready_status != 503 or ready.get("ready") is not False
                or state_status != 200):
            raise ValueError(f"saude HTTP fria inesperada para {role}")
        if state["ready"] is not False or state["run_id"] is not None:
            raise ValueError(f"servico nao esta frio: {role}")
        record = base.read_logs(topo["pods"][role]["name"])
        if any(e.get("event_type") == "mutation" for e in record):
            raise ValueError(f"mutacao anterior detectada: {role}")
        states[role], logs[role] = state, record
        base.write_jsonl(output / f"{role}-logs-before-snapshot.jsonl", record)
        print(f"COLD {role}: HTTP live=200 ready=503, node={observed[role]}", flush=True)
    base.write_json(output / "states-before-snapshot.json", states)
    return topo, source_pod


def confirm_bootstrap(output, source_pod, topo):
    states = {}
    logs = {}
    for role in base.ROLES:
        ready_status, ready = base.http(source_pod, role, "/health/ready")
        state_status, state = base.http(source_pod, role, "/state")
        if ready_status != 200 or ready.get("ready") is not True or state_status != 200:
            raise ValueError(f"prontidao funcional ausente apos snapshot: {role}")
        states[role] = state
        logs[role] = base.read_logs(topo["pods"][role]["name"])
    base.write_json(output / "states-after-snapshot.json", states)
    for role in base.ROLES:
        base.write_jsonl(output / f"{role}-logs-after-snapshot.jsonl", logs[role])
    base.check_initial(states, logs)
    topo_after = base.topology()
    base.write_json(output / "topology-after-snapshot.json", topo_after)
    if topo["pods"] != topo_after["pods"]:
        raise ValueError("Pod reiniciado/migrado entre preflight e snapshot")
    print("E10-C4-SNAPSHOT: PASS (3/3 prontos, 0 efeitos, nos distintos)", flush=True)


def capture_on_failure(output):
    try:
        topo = base.topology()
        base.write_json(output / "topology-recovery.json", topo)
        source = topo["pods"]["attribute-source"]["name"]
    except Exception as error:
        (output / "topology-recovery-error.txt").write_text(str(error) + "\n", encoding="utf-8")
        return
    for role in base.ROLES:
        try:
            status, state = base.http(source, role, "/state")
            base.write_json(output / f"{role}-recovery-state.json",
                            {"status": status, "state": state})
        except Exception as error:
            (output / f"{role}-recovery-state-error.txt").write_text(
                str(error) + "\n", encoding="utf-8")
        try:
            logs = base.read_logs(topo["pods"][role]["name"])
            base.write_jsonl(output / f"{role}-logs-captured.jsonl", logs)
        except Exception as error:
            (output / f"{role}-logs-captured-error.txt").write_text(
                str(error) + "\n", encoding="utf-8")


def run(output):
    configure()
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    report = {
        "scenario": "C4", "run_id": RUN_ID, "namespace": NAMESPACE,
        "status": "FAIL", "started_snapshot": False, "started_changes": False,
        "context": base.CONTEXT, "host_python": platform.python_version(),
        "git_sha": base.git_sha(), "timestamp_utc": base.utc_now(),
        "expected_node_assignment": ASSIGNMENT,
        "note": "multinó kind virtual sobre UM host fisico; sem benchmark nem replay",
    }
    try:
        print("=== E10-C4: PREFLIGHT SEM MUTACAO ===", flush=True)
        topo, source = check_preflight(output)
        report["topology_pre_snapshot"] = topo["pods"]
        report["runtime_image_id"] = next(iter(
            {topo["pods"][r]["image_id_runtime"] for r in base.ROLES}
        ))
        base.write_json(output / "preflight.json", report)
        base.append_jsonl(output / "snapshot-attempt.jsonl", {
            "timestamp_utc": base.utc_now(), "intent": "BEFORE_POST",
            "target": "attribute-source:8080/init/snapshot", "run_id": RUN_ID,
        })
        report["started_snapshot"] = True
        print("=== E10-C4: SNAPSHOT UNICO ===", flush=True)
        status, response = base.http(
            source, "attribute-source", "/init/snapshot", {"run_id": RUN_ID}
        )
        base.write_json(output / "snapshot-response.json",
                        {"status": status, "response": response})
        if (status != 200 or response.get("duplicate") is not False
                or response.get("ready") is not True
                or response.get("snapshot_version") != RUN_ID + ":snapshot:0"):
            raise ValueError(f"snapshot HTTP inesperado: {status} {response}")
        confirm_bootstrap(output, source, topo)
        print("=== E10-C4: FIXTURE DE SETE PASSOS ===", flush=True)
        passed = base.run(output / "fixture")
        fixture_report_path = output / "fixture" / "validation.json"
        if fixture_report_path.exists():
            fixture_report = json.loads(fixture_report_path.read_text(encoding="utf-8"))
            report["started_changes"] = fixture_report.get("started_changes", False)
            report["fixture_status"] = fixture_report.get("status")
            report["fixture_checks"] = fixture_report.get("checks", {})
        if not passed:
            raise ValueError("fixture C4 falhou; preservar evidencias")
        if len(report.get("fixture_checks", {})) != 14:
            raise ValueError("quantidade inesperada de verificacoes da fixture")
        report["status"] = "PASS"
    except Exception as error:
        report["status"] = "FAIL"
        report["error"] = f"{type(error).__name__}: {error}"
    finally:
        if report["status"] != "PASS":
            capture_on_failure(output)
        base.write_json(output / "validation-c4.json", report)
        # A inclusao do ZIP da fixture garante todos os seus arquivos e hashes.
        (output / "checksums.sha256").write_text(
            "".join(f"{base.sha256_file(item)}  {item.name}\n"
                    for item in sorted(output.iterdir())
                    if item.is_file() and item.name != "checksums.sha256"),
            encoding="utf-8",
        )
        archive_path = output.with_suffix(".zip")
        with ZipFile(archive_path, "w", ZIP_DEFLATED) as archive:
            for file in sorted(output.iterdir()):
                if file.is_file():
                    archive.write(file, arcname=file.name)
        print("E10-C4:", report["status"], flush=True)
        if report["status"] != "PASS":
            print("ERRO:", report.get("error"), flush=True)
            print("NAO repetir: snapshot ou alteracoes podem ter sido aplicados.", flush=True)
        else:
            print("E10-C4: 14/14 checks da fixture; dois efeitos nos passos 3 e 7", flush=True)
        print("ZIP_C4:", archive_path.resolve(), flush=True)
        print("ZIP_C4_BYTES:", archive_path.stat().st_size, flush=True)
        print("ZIP_C4_SHA256:", base.sha256_file(archive_path), flush=True)
    return report["status"] == "PASS"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        return 0 if run(args.output) else 1
    except (ValueError, OSError) as error:
        print(f"E10-C4 BLOQUEADO SEM RETENTATIVA: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
