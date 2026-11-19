"""Auditoria e extração offline da campanha E11-M01."""
import argparse
import csv
from datetime import datetime
from io import StringIO
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

from benchmark.evidence import check_run, hash_file, write_csv, write_json
from benchmark.fixtures import rebase
from benchmark.kube_preflight import IMAGE_ID, CANONICAL_INPUT_SHA256, validate_canonical
from benchmark.lifecycle_audit import audit_archive, sha256_bytes
from benchmark.m01_readiness import full_schedule
from c0.oracle import calculate_expected_effects

CAMPAIGN_SHA = "24740e922181dace018a26938b353f10d952da06"
FIRST_SHA = "eecc15e3bb1c36c9ee51b3165f882d76a0c6ed9b"
FIRST_RUN = "e11-c2-m01-b01"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def jsonl(data):
    return [json.loads(line) for line in data.splitlines()]


def iso(value):
    return datetime.fromisoformat(value)


def check_journal(raw, run_id, scenario, digest, status):
    rows = jsonl(raw)
    require(all((r["run_id"], r["scenario"]) == (run_id, scenario) for r in rows),
            "identidade em journal")
    require([r["stage"] for r in rows].count("COMPLETE") == 1
            and rows[-1]["stage"] == "COMPLETE" and rows[-1]["status"] == status,
            "conclusão em journal")
    hashes = [r["zip_sha256"] for r in rows if "zip_sha256" in r]
    require(len(hashes) >= 2 and set(hashes) == {digest}
            and rows[-1]["zip_sha256"] == digest, "SHA-256 em journal")
    times = [iso(r["utc"]) for r in rows]
    require(times == sorted(times), "ordem interna do journal")
    return rows


def check_identity(archive, slot, retirement):
    scenario = slot["scenario"]
    ownership = json.loads(archive.read("ownership-start.json"))
    before = json.loads(archive.read("topology-start.json"))
    after = json.loads(archive.read("topology-end.json"))
    client_pod = before.pop("client_pod", None)
    # Alguns snapshots kind registram o nome do cliente apenas na abertura.
    require(before == after, "topologia mudou durante a rodada")
    if scenario == "C2":
        key, identity = "containers", "id"
        ids = {"network_id": ownership["network"]["id"]}
        ids["container_ids"] = {k: v["id"] for k, v in ownership[key].items()}
        require(before["network"] == slot["resource_base"], "nome da rede")
    else:
        key, identity = "pods", "uid"
        ids = {"namespace_uid": ownership["namespace"]["uid"]}
        ids["pod_uids"] = {k: v["uid"] for k, v in ownership[key].items()}
        placement = {role: "tcc2-pon-worker" for role in before[key]}
        if scenario == "C4":
            placement["logic-engine"] = "tcc2-pon-control-plane"
        require({k: v["node"] for k, v in before[key].items()} == placement,
                "placement kind")
        require(set(before[key]) == {"attribute-source", "logic-engine", "rule-executor"}
                and client_pod == ownership[key]["client"]["name"],
                "papéis da topologia kind")
    require(all(v["restart_count"] == 0 and v[identity] == ownership[key][k][identity]
                for k, v in before[key].items()), "ID/UID ou reinício")
    require(retirement[0]["stage"] == "AUTHORIZED_BEGIN"
            and retirement[0]["git_sha"] == CAMPAIGN_SHA
            and retirement[0]["immutable_ids"] == ids, "identidade da retirada")
    return ids


def check_transport(archive, oracle, attribute_ids):
    source, logic, executor = (
        jsonl(archive.read(f"{role}-logs.jsonl"))
        for role in ("attribute-source", "logic-engine", "rule-executor")
    )
    for sender, receiver, kind, count in (
        (source, logic, "attribute", 874),
        (logic, executor, "condition", 500),
    ):
        path = f"/notifications/{kind}"
        sent = [r["payload"] for r in sender
                if r.get("event_type") == "send" and r.get("path") == path]
        received = [r["payload"] for r in receiver if r.get("event_type") == "mutation"
                    and r.get("path") == path and r.get("status") == 200]
        ids = {r["event_id"] for r in sent}
        require(len(sent) == len(ids) == count and sent == received, f"transporte {kind}")
        if kind == "attribute":
            require(ids == attribute_ids, "IDs de atributo no cliente e no log")
    require([r["payload"] for r in executor if r.get("event_type") == "effect"] == oracle,
            "efeitos no log do executor")


def extract(archive, slot, canonical):
    run_id = slot["run_id"]
    manifest = json.loads(archive.read("manifest.json"))
    env = json.loads(archive.read("environment.json"))
    git_sha = FIRST_SHA if run_id == FIRST_RUN else CAMPAIGN_SHA
    require(manifest["git_sha"] == env["git_sha"] == git_sha
            and manifest["image_id"] == IMAGE_ID and manifest["seed"] == 20260502
            and manifest.get("load", manifest.get("requests")) == 1000
            and manifest.get("canonical_input_sha256", manifest.get("fixture_sha256"))
            == CANONICAL_INPUT_SHA256, "commit, imagem, seed ou carga")
    for report in (manifest, json.loads(archive.read("metrics-status.json"))):
        require(report["measurement_mode"] == "timing_only"
                and report["resource_sampling_during_batch"] is False
                and report["resource_metrics_comparable"] is False, "perfil de medição")
    inputs = jsonl(archive.read("inputs.jsonl"))
    require(inputs == rebase(canonical, run_id), "carga diverge da fixture canônica")
    oracle = calculate_expected_effects(inputs)
    require(len(oracle) == 250 and oracle == jsonl(archive.read("expected.jsonl"))
            == jsonl(archive.read("effects.jsonl"))
            and len({row["event_id"] for row in oracle}) == 250, "oráculo/efeitos")
    records = jsonl(archive.read("client.stdout.jsonl"))
    summary = json.loads(archive.read("batch-summary.json"))
    require(len(records) == 1001 and records[-1] == summary
            and summary["requests_sent"] == summary["requests_target"] == 1000
            and summary["status"] == "PASS" and summary["error"] is None
            and summary["clock"] == "time.perf_counter_ns", "resumo do cliente")
    validation = json.loads(archive.read("validation.json"))
    functional = validation["validation"]
    require(validation["run_id"] == run_id and validation["scenario"] == slot["scenario"]
            and functional["status"] == "PASS" and functional["expected_effects"] == 250
            and all(check is True for check in functional["transport"].values())
            and check_run(inputs, records, json.loads(archive.read("states-final.json")))
            ["status"] == "PASS", "validação funcional ou transporte")
    csv_rows = list(csv.DictReader(StringIO(archive.read("requests.csv").decode())))
    require(len(csv_rows) == 1000, "contagem de linhas em requests.csv")
    rows = []
    event_ids = set()
    for source, request, row in zip(inputs, records[:-1], csv_rows, strict=True):
        response = request["response"]
        changed = response["changed"]
        duration = request["duration_ns"]
        require(request["type"] == "request" and request["step"] == source["step"]
                and request["status"] == 200 and type(duration) is int and duration > 0
                and type(changed) is bool and response["duplicate_request"] is False
                and row == {"step": str(source["step"]), "duration_ns": str(duration),
                            "status": "200", "changed": str(changed)}, "CSV/JSONL ou resposta")
        if changed:
            event_id = response["event_id"]
            require(event_id and event_id not in event_ids, "evento duplicado")
            event_ids.add(event_id)
        rows.append({**slot, "request_id": source["request_id"], "step": source["step"],
                     "duration_ns": duration, "status": 200, "changed": changed})
    require(len(event_ids) == 874 and sum(r["duration_ns"] for r in rows)
            <= summary["elapsed_ns"], "mudanças ou duração cumulativa")
    check_transport(archive, oracle, event_ids)
    return rows, summary, git_sha


def audit_round(originals, backups, slot, canonical):
    run_id = slot["run_id"]
    folder = originals / run_id
    original = folder / "resultado.zip"
    backup = backups / f"{run_id}.zip"
    run_path = backups / f"{run_id}-run.jsonl"
    retire_path = backups / f"{run_id}-retirement.jsonl"
    report = audit_archive(original, slot["scenario"], slot["label"], run_id)
    digest = report["zip_sha256"]
    require(hash_file(backup) == digest, "SHA-256 da cópia")
    run_raw, retire_raw = run_path.read_bytes(), retire_path.read_bytes()
    run = check_journal(run_raw, run_id, slot["scenario"], digest, "M01_RUN_PASS_BACKED_UP")
    retire = check_journal(retire_raw, run_id, slot["scenario"], digest,
                           "M01_RETIREMENT_COMPLETE")
    attempts = [r for r in run if r["stage"] == "BEFORE_SNAPSHOT_BATCH"]
    require(len(attempts) == 1 and attempts[0]["attempt_single_shot"] is True
            and iso(run[-1]["utc"]) < iso(retire[0]["utc"]), "tentativa única/cronologia")
    if run_id != FIRST_RUN:
        require(run[0]["stage"] == "BEFORE_RUN" and run[0]["git_sha"] == CAMPAIGN_SHA
                and run[0]["fixture_sha256"] == CANONICAL_INPUT_SHA256, "abertura da rodada")
    with ZipFile(original) as archive:
        members = {name: sha256_bytes(archive.read(name)) for name in archive.namelist()}
        unpacked = folder / "resultado"
        require(set(members) == {p.name for p in unpacked.iterdir()}
                and all(hash_file(unpacked / n) == h for n, h in members.items()),
                "arquivos locais divergem do ZIP")
        ids = check_identity(archive, slot, retire)
        rows, summary, git_sha = extract(archive, slot, canonical)
    require(iso(attempts[0]["utc"]) <= iso(summary["batch_started_utc"])
            < iso(summary["batch_finished_utc"]) <= iso(run[-1]["utc"]),
            "cronologia do lote")
    inventory = {
        **slot, "git_sha": git_sha, "retirement_git_sha": CAMPAIGN_SHA,
        "original": original.relative_to(originals).as_posix(), "backup": backup.name,
        "zip_sha256": digest, "zip_bytes": original.stat().st_size,
        "members": len(members), "members_sha256": members, "run_journal": run_path.name,
        "run_journal_sha256": sha256_bytes(run_raw), "retirement_journal": retire_path.name,
        "retirement_journal_sha256": sha256_bytes(retire_raw), "resource_ids": ids,
        "batch_started_utc": summary["batch_started_utc"],
        "batch_finished_utc": summary["batch_finished_utc"],
        "batch_elapsed_ns": summary["elapsed_ns"], "requests": len(rows),
        "http_200": len(rows), "changes": 874, "no_ops": 126, "effects": 250,
        "attribute_notifications": 874, "condition_notifications": 500,
    }
    for path in (folder / "manifest.yaml", backups / f"{run_id}-delete-options.json"):
        if path.is_file():
            inventory[path.name] = hash_file(path)
    return inventory, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("originals", "backups", "fixture", "output"):
        parser.add_argument(f"--{arg}", required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    for source in (args.originals, args.backups, args.fixture.parent):
        require(not output.is_relative_to(source.resolve()), "saída dentro das evidências")
    require(output.suffix == ".zip" and not output.exists(), "use um novo caminho .zip")
    canonical, expected = validate_canonical(args.fixture)
    schedule = full_schedule()
    run_ids = {s["run_id"] for s in schedule}
    require(len(run_ids) == 30, "agenda inválida")
    require({p.name for p in args.originals.glob("e11-*-m01-b*")} == run_ids,
            "inventário de originais diverge da agenda")
    for suffix in (".zip", "-run.jsonl", "-retirement.jsonl"):
        require({p.name for p in args.backups.glob(f"e11-*-m01-b*{suffix}")}
                == {run_id + suffix for run_id in run_ids}, f"inventário de {suffix}")
    rounds, requests = [], []
    for slot in schedule:
        try:
            inventory, rows = audit_round(args.originals, args.backups, slot, canonical)
        except (OSError, KeyError, ValueError) as exc:
            raise ValueError(f"{slot['run_id']}: {exc}") from exc
        rounds.append(inventory)
        requests.extend(rows)
    require(len({r["zip_sha256"] for r in rounds}) == 30
            and len({r["request_id"] for r in requests}) == 30000, "ZIP ou requisição duplicado")
    resource_ids = [value for r in rounds for group in r["resource_ids"].values()
                    for value in (group.values() if isinstance(group, dict) else [group])]
    require(len(set(resource_ids)) == len(resource_ids) == 150, "ID/UID duplicado")
    require(all(iso(a["batch_finished_utc"]) < iso(b["batch_started_utc"])
                for a, b in zip(rounds, rounds[1:])), "ordem B01–B10 diverge da agenda")
    with TemporaryDirectory() as temp:
        folder = Path(temp)
        scalar_columns = [k for k, v in rounds[0].items() if not isinstance(v, dict) and not k.endswith((".yaml", ".json"))]
        write_json(folder / "inventario.json", {
            "schema_version": 1, "campaign": "E11-M01", "rounds": rounds,
            "fixture_sha256": hash_file(args.fixture), "oracle_sha256": hash_file(expected),
        })
        write_csv(folder / "rodadas.csv", rounds, scalar_columns)
        write_csv(folder / "requisicoes.csv", requests,
                  [*schedule[0], "request_id", "step", "duration_ns", "status", "changed"])
        files = sorted(folder.iterdir())
        checksum = "".join(f"{hash_file(p)}  {p.name}\n" for p in files)
        with ZipFile(output, "x", compression=ZIP_DEFLATED) as package:
            for path in files:
                package.write(path, path.name)
            package.writestr("checksums.sha256", checksum)
    print(f"PASS: {len(rounds)} rodadas, {len(requests)} requisições.")
    print(f"{hash_file(output)}  {output}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        sys.exit(f"FALHA: {exc}")
