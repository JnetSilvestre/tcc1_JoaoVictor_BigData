"""E08-D14B: rejeicoes HTTP 4xx de V03 em bancada C2 ainda sem snapshot.

Executa somente mensagens INVALIDAS; preserva as tres instancias C2 originais.
Assembleia de evidencias: status HTTP, estado pre/pos de cada tentativa,
metadados dos conteineres, logs JSONL e hashes SHA-256.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

from c0.runner import PROJECT_ROOT, sha256_file, write_json

IMAGE_TAG = "tcc2-pon:c2-e08-dbefcd2cf3d2"
BUILD_SHA = "dbefcd2cf3d2fbf220cff8eda34d52189e08192a"
NETWORK = "tcc2-pon-c2-v03"
CONTAINERS = {
    "attribute-source": "tcc2-v03-attribute-source",
    "logic-engine": "tcc2-v03-logic-engine",
    "rule-executor": "tcc2-v03-rule-executor",
}

GET = '''import sys,json,urllib.request,urllib.error
url="http://127.0.0.1:8080"+sys.argv[1]
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
try:
    with opener.open(url,timeout=7) as response:
        status=response.status
        body=json.load(response)
except urllib.error.HTTPError as error:
    status=error.code
    body=json.loads(error.read().decode("utf-8"))
print(json.dumps({"status":status,"body":body},sort_keys=True))
'''

POST = '''import sys,json,urllib.request,urllib.error
path,body,content_type=sys.argv[1:4]
req=urllib.request.Request("http://127.0.0.1:8080"+path,
    data=body.encode("utf-8"),headers={"Content-Type":content_type},method="POST")
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
try:
    with opener.open(req,timeout=7) as response:
        status=response.status
        data=json.load(response)
except urllib.error.HTTPError as error:
    status=error.code
    data=json.loads(error.read().decode("utf-8"))
print(json.dumps({"status":status,"body":data},sort_keys=True))
'''

# Casos são invalidos mesmo que algum servico venha a ser inicializado; a
# precondicao "cold" continua obrigatoria para atribuir evidencias a esta rodada.
CASES = [
    ("S01", "attribute-source", "/init/snapshot", '{"run_id":""}', "application/json", 422),
    ("S02", "attribute-source", "/init/snapshot", '{"run_id":"v03-cold","extra":1}', "application/json", 422),
    ("S03", "attribute-source", "/init/snapshot", "[]", "application/json", 422),
    ("S04", "attribute-source", "/init/snapshot", '{"run_id":', "application/json", 400),
    ("S05", "attribute-source", "/init/snapshot", '{"run_id":"v03-cold"}', "text/plain", 415),
    ("S06", "attribute-source", "/attributes/change", '{"run_id":"v03-cold","entity_id":"atA","value":5}', "application/json", 422),
    ("S07", "attribute-source", "/attributes/change", '{"run_id":"v03-cold","request_id":"x","entity_id":"invalid","value":5}', "application/json", 422),
    ("S08", "logic-engine", "/notifications/attribute", "{}", "application/json", 422),
    ("S09", "rule-executor", "/notifications/condition", "{}", "application/json", 422),
    ("S10", "attribute-source", "/rota-desconhecida", "{}", "application/json", 404),
]


def call(*args):
    proc = subprocess.run(
        [str(a) for a in args], cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        encoding="utf-8", errors="replace", timeout=25, check=False,
    )
    if proc.returncode:
        raise RuntimeError(
            f"comando falhou ({proc.returncode}): {args[:4]}\n"
            f"stdout: {proc.stdout[-1000:]}\nstderr: {proc.stderr[-1000:]}"
        )
    return proc.stdout


def service_get(role, path):
    response = json.loads(call("docker", "exec", CONTAINERS[role],
                               "python", "-c", GET, path))
    return response


def service_post(role, path, body, content_type):
    return json.loads(call("docker", "exec", CONTAINERS[role],
                           "python", "-c", POST, path, body, content_type))


def states():
    result = {}
    for role in CONTAINERS:
        response = service_get(role, "/state")
        if response["status"] != 200:
            raise ValueError(f"/state inesperado em {role}: {response}")
        result[role] = response["body"]
    return result


def assert_cold(current):
    for role, state in current.items():
        if state.get("ready") is not False or state.get("run_id") is not None:
            raise ValueError(f"bancada V03 ja foi inicializada: {role}")
        if state.get("snapshot_version") is not None:
            raise ValueError(f"snapshot ja presente: {role}")
        if role in ("attribute-source", "logic-engine"):
            if state.get("attributes") != {"atA": 0, "atB": 0}:
                raise ValueError(f"atributos alterados: {role}")
            if state.get("sequences") != {"atA": 0, "atB": 0}:
                raise ValueError(f"sequencias alteradas: {role}")
        if role == "attribute-source" and state.get("pending_request_id") is not None:
            raise ValueError("produtor com pedido pendente")
        if role == "logic-engine" and (
            state.get("received_ids") or state.get("condition_events")
            or state.get("faulted") or state.get("condition_sequence") != 0
        ):
            raise ValueError("avaliador contem historico")
        if role == "rule-executor" and (
            state.get("received_ids") or state.get("effects")
            or state.get("faulted") or state.get("condition_sequence") != 0
        ):
            raise ValueError("executor contem historico")


def topology():
    network = json.loads(call("docker", "network", "inspect", NETWORK))[0]
    if network["Driver"] != "bridge" or network["Internal"] is not True:
        raise ValueError("rede V03 nao e bridge interna")
    image = json.loads(call("docker", "image", "inspect", IMAGE_TAG))[0]
    if image["Os"] != "linux" or image["Architecture"] != "amd64":
        raise ValueError("imagem nao e linux/amd64")
    if image["Config"]["Labels"].get("org.opencontainers.image.revision") != BUILD_SHA:
        raise ValueError("revisao da imagem divergente")
    containers = {}
    for role, name in CONTAINERS.items():
        info = json.loads(call("docker", "inspect", name))[0]
        if (info["State"]["Running"] is not True
                or info["Image"] != image["Id"]
                or info["Config"]["Labels"].get("tcc2.test") != "V03"
                or NETWORK not in info["NetworkSettings"]["Networks"]
                or info["HostConfig"]["PortBindings"]):
            raise ValueError(f"conteiner V03 inesperado: {name}")
        containers[role] = {"name": name, "id": info["Id"],
                            "started_at": info["State"]["StartedAt"]}
    if len({x["id"] for x in containers.values()}) != 3:
        raise ValueError("IDs Docker repetidos")
    return {"network": NETWORK, "internal": True, "image": IMAGE_TAG,
            "image_id": image["Id"], "image_revision": BUILD_SHA,
            "containers": containers}


def execute(output):
    folder = Path(output)
    folder.mkdir(parents=True, exist_ok=False)
    result = {"scenario": "C2", "criterion": "V03", "phase": "cold",
              "status": "FAIL", "cases_completed": 0, "cases_planned": len(CASES),
              "timestamp_utc": datetime.now(timezone.utc).isoformat()}
    transcript = []
    try:
        if call("git", "branch", "--show-current").strip() != "tcc2/desenvolvimento":
            raise ValueError("branch incorreta")
        if call("git", "status", "--porcelain").strip():
            raise ValueError("Git possui alteracoes locais")
        manifest = topology()
        manifest["git_sha"] = call("git", "rev-parse", "HEAD").strip()
        write_json(folder / "manifest.json", manifest)

        before = states()
        assert_cold(before)
        write_json(folder / "states-before.json", before)
        for role in CONTAINERS:
            ready = service_get(role, "/health/ready")
            if ready["status"] != 503 or ready["body"].get("ready") is not False:
                raise ValueError(f"readiness inesperada: {role}: {ready}")

        for case_id, role, path, body, content_type, expected in CASES:
            per_case_before = states()
            if per_case_before != before:
                raise ValueError(f"estado anterior divergente no caso {case_id}")
            outcome = service_post(role, path, body, content_type)
            per_case_after = states()
            record = {"case_id": case_id, "role": role, "path": path,
                      "body": body, "content_type": content_type,
                      "expected_status": expected, "actual_status": outcome["status"],
                      "response": outcome["body"],
                      "state_unchanged": per_case_after == per_case_before}
            transcript.append(record)
            write_json(folder / "http-cases.json", transcript)
            if outcome["status"] != expected or not isinstance(outcome["body"].get("error"), str):
                raise ValueError(f"resposta inesperada no caso {case_id}: {outcome}")
            if per_case_after != per_case_before:
                raise ValueError(f"estado alterado no caso {case_id}")
            result["cases_completed"] += 1

        final = states()
        assert_cold(final)
        write_json(folder / "states-after.json", final)
        result["status"] = "PASS"
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.TimeoutExpired) as error:
        result["error"] = str(error)
    finally:
        for role, name in CONTAINERS.items():
            try:
                (folder / f"{role}.jsonl").write_text(
                    call("docker", "logs", name), encoding="utf-8")
            except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
                (folder / f"{role}.capture-error.txt").write_text(
                    str(error), encoding="utf-8")
        write_json(folder / "validation.json", result)
        (folder / "checksums.sha256").write_text("".join(
            f"{sha256_file(p)}  {p.name}\n"
            for p in sorted(folder.iterdir()) if p.name != "checksums.sha256"
        ), encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = execute(args.output)
    except (OSError, ValueError) as error:
        print("E08-D14B: FALHA ANTES DA RODADA:", error, file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("Evidencias:", args.output.resolve())
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
