"""E11-I05: sonda SOMENTE LEITURA Docker Engine API via named pipe do Windows.

SEM docker exec, docker run, POST ou alteracao de containers. A opcao --probe
faz leituras REST GET em quatro containers E11-C2 JA EXISTENTES. Sem --probe:
apenas PLAN_ONLY. Codigo experimental: compatibilidade Windows a validar.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

from benchmark.docker_c2 import IMAGE_ID, identities
from benchmark.evidence import archive, write_csv, write_json, write_jsonl

ROOT = Path(__file__).resolve().parents[1]
ROLE_ORDER = ("attribute-source", "logic-engine", "rule-executor", "client")
MAX_BODY = 4 * 1024 * 1024
PIPE_RE = re.compile(r"^npipe:////\./pipe/(docker_engine|dockerDesktopLinuxEngine)$")
DOCKER_ID_RE = re.compile(r"^[a-f0-9]{64}$")
API_RE = re.compile(r"^[0-9]{1,2}\.[0-9]{1,2}$")
CSV_FIELDS = (
    "role", "container_name", "container_id", "docker_read_utc",
    "retrieved_utc", "collection_seconds", "cpu_total_ns",
    "cpu_throttled_periods", "cpu_throttled_time_ns", "memory_usage_bytes",
    "memory_limit_bytes", "memory_inactive_file_bytes",
    "memory_cli_adjusted_bytes", "network_rx_bytes", "network_tx_bytes",
)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def run_cli(*args, timeout=15):
    p = subprocess.run([str(a) for a in args], cwd=ROOT, capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       timeout=timeout, check=False)
    if p.returncode:
        raise RuntimeError(f"comando de leitura falhou: {args[:4]}, "
                           f"stderr={p.stderr[-300:]}")
    return p.stdout


def named_pipe_from_context(context):
    """Somente pipes locais conhecidos; sem TCP, SSH, socket em contêiner."""
    if not isinstance(context, str) or not PIPE_RE.fullmatch(context):
        raise ValueError("Docker context nao usa pipe local esperada; recusar a sonda")
    return "\\\\.\\pipe\\" + context.rsplit("/", 1)[1]


def check_local_engine():
    if os.name != "nt":
        raise RuntimeError("sonda usa named pipe Windows; nao suportada neste host")
    if os.environ.get("DOCKER_HOST"):
        raise RuntimeError("DOCKER_HOST definido: contexto CLI ambiguo; recusar sonda")
    current = json.loads(run_cli("docker", "context", "inspect"))
    if not isinstance(current, list) or len(current) != 1:
        raise ValueError("docker context inspect inesperado")
    endpoint = (((current[0].get("Endpoints") or {}).get("docker") or {}).get("Host"))
    pipe = named_pipe_from_context(endpoint)
    api_version = run_cli("docker", "version", "--format",
                          "{{.Server.APIVersion}}").strip()
    if not API_RE.fullmatch(api_version):
        raise ValueError("Docker Server APIVersion invalida")
    return {"endpoint": endpoint, "pipe": pipe, "api_version": api_version}


def parse_http_response(raw):
    """Parser HTTP/1.1 limitado. Sem dependencia externa e SEM enviar comandos mutantes."""
    if not isinstance(raw, bytes) or len(raw) > MAX_BODY:
        raise ValueError("resposta HTTP nao e bytes ou excede tamanho maximo")
    header, sep, body = raw.partition(b"\r\n\r\n")
    if not sep:
        raise ValueError("cabecalho HTTP incompleto")
    lines = header.split(b"\r\n")
    first = lines[0].split(b" ", 2)
    if len(first) < 2 or first[0] not in (b"HTTP/1.1", b"HTTP/1.0"):
        raise ValueError("status HTTP invalido")
    status = int(first[1])
    headers = {}
    for line in lines[1:]:
        k, sep, v = line.partition(b":")
        if not sep:
            raise ValueError("cabecalho HTTP malformado")
        headers[k.decode("ascii").lower()] = v.decode("ascii").strip().lower()
    if "chunked" in headers.get("transfer-encoding", ""):
        pieces = []
        offset = 0
        while True:
            end = body.find(b"\r\n", offset)
            if end < 0:
                raise ValueError("chunk sem delimitador")
            head = body[offset:end].split(b";", 1)[0]
            try:
                length = int(head, 16)
            except ValueError as e:
                raise ValueError("tamanho de chunk invalido") from e
            offset = end + 2
            if length < 0 or offset + length + 2 > len(body):
                raise ValueError("chunk truncado")
            if body[offset + length:offset + length + 2] != b"\r\n":
                raise ValueError("chunk sem CRLF final")
            if length == 0:
                break
            pieces.append(body[offset:offset + length])
            offset += length + 2
        body = b"".join(pieces)
    elif "content-length" in headers:
        size = int(headers["content-length"])
        if size < 0 or size > MAX_BODY or len(body) < size:
            raise ValueError("Content-Length invalido ou incompleto")
        body = body[:size]
    if status != 200:
        raise RuntimeError(f"Docker Engine API HTTP {status}: {body[:300]!r}")
    decoded = json.loads(body.decode("utf-8"))
    if not isinstance(decoded, dict):
        raise ValueError("estatisticas Docker nao retornaram objeto JSON")
    return decoded


def _pipe_worker(pipe, api, container_id):
    """Uma requisicao GET autenticada pelo pipe do Docker local, em subprocesso isolado."""
    if pipe not in ("\\\\.\\pipe\\docker_engine",
                    "\\\\.\\pipe\\dockerDesktopLinuxEngine"):
        raise ValueError("named pipe nao permitida")
    if not API_RE.fullmatch(api) or not DOCKER_ID_RE.fullmatch(container_id):
        raise ValueError("versao Docker ou ID do container invalido")
    if os.name != "nt":
        raise RuntimeError("pipe worker exige Windows")
    request = (
        f"GET /v{api}/containers/{container_id}/stats?stream=false&one-shot=true HTTP/1.1\r\n"
        "Host: docker\r\nAccept: application/json\r\nConnection: close\r\n\r\n"
    ).encode("ascii")
    fd = os.open(pipe, os.O_RDWR | os.O_BINARY)
    try:
        sent = 0
        while sent < len(request):
            count = os.write(fd, request[sent:])
            if count <= 0:
                raise RuntimeError("escrita HTTP nao avancou")
            sent += count
        raw = bytearray()
        while len(raw) < MAX_BODY:
            try:
                part = os.read(fd, 65536)
            except OSError as exc:
                if getattr(exc, "winerror", None) == 109:
                    break  # ERROR_BROKEN_PIPE: a resposta pode ter sido entregue.
                raise
            if not part:
                break
            raw.extend(part)
        return parse_http_response(bytes(raw))
    finally:
        os.close(fd)


def parse_stats(raw, role, name, container_id, elapsed, retrieved):
    """CPU: cumulativa em nanosegundos. Memoria: uso BRUTO, nao working-set."""
    cpu = (raw.get("cpu_stats") or {}).get("cpu_usage") or {}
    throttle = (raw.get("cpu_stats") or {}).get("throttling_data") or {}
    memory = raw.get("memory_stats") or {}
    memory_details = memory.get("stats") or {}
    networks = raw.get("networks") or {}
    def natural(value):
        return value if type(value) is int and value >= 0 else None
    usage = natural(memory.get("usage"))
    inactive = natural(memory_details.get("inactive_file"))
    adjusted = (usage - inactive if usage is not None and inactive is not None
                and usage >= inactive else None)
    cpu_total = natural(cpu.get("total_usage"))
    rx = [natural(x.get("rx_bytes")) for x in networks.values() if isinstance(x, dict)]
    tx = [natural(x.get("tx_bytes")) for x in networks.values() if isinstance(x, dict)]
    return {
        "role": role, "container_name": name, "container_id": container_id,
        "docker_read_utc": raw.get("read"), "retrieved_utc": retrieved,
        "collection_seconds": elapsed, "cpu_total_ns": cpu_total,
        "cpu_throttled_periods": natural(throttle.get("throttled_periods")),
        "cpu_throttled_time_ns": natural(throttle.get("throttled_time")),
        "memory_usage_bytes": usage,
        "memory_limit_bytes": natural(memory.get("limit")),
        "memory_inactive_file_bytes": inactive,
        "memory_cli_adjusted_bytes": adjusted,
        "network_rx_bytes": sum(rx) if rx and all(v is not None for v in rx) else None,
        "network_tx_bytes": sum(tx) if tx and all(v is not None for v in tx) else None,
    }


def assert_new_pilot_containers(names):
    result = {}
    for role, name in names.items():
        obj = json.loads(run_cli("docker", "inspect", name))[0]
        if (obj.get("Image") != IMAGE_ID
                or obj.get("State", {}).get("Running") is not True
                or obj.get("RestartCount") != 0
                or ((obj.get("Config") or {}).get("Labels") or {}).get("tcc2.e11") != "pilot"):
            raise ValueError(f"container nao e um piloto C2 E11 integro: {role}")
        cid = obj.get("Id")
        if not isinstance(cid, str) or not DOCKER_ID_RE.fullmatch(cid):
            raise ValueError(f"ID Docker invalido para {role}")
        result[role] = cid
    return result


def engine_stat(pipe, api, cid, role, name, timeout=20):
    begin = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, "-m", "benchmark.docker_engine_api", "--pipe-worker",
         "--pipe", pipe, "--api-version", api, "--container-id", cid],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=timeout, check=False,
    )
    elapsed = time.perf_counter()-begin
    stamp = utc_now()
    if proc.returncode:
        raise RuntimeError(f"consulta GET falhou para {role}: {proc.stderr[-500:]}")
    raw = json.loads(proc.stdout)
    return parse_stats(raw, role, name, cid, elapsed, stamp)


def assess(samples, roles):
    issues = []
    details = {}
    for role in roles:
        rows = [x for x in samples if x.get("role") == role]
        counts = [x["cpu_total_ns"] for x in rows if x.get("cpu_total_ns") is not None]
        regressed = any(b < a for a, b in zip(counts, counts[1:]))
        missing = any(x.get("cpu_total_ns") is None
                      or x.get("memory_usage_bytes") is None for x in rows)
        details[role] = {
            "samples": len(rows), "cpu_counter_regressed": regressed,
            "fields_missing": missing,
            "first_cpu_ns": counts[0] if counts else None,
            "last_cpu_ns": counts[-1] if counts else None,
            "last_memory_usage_bytes": rows[-1]["memory_usage_bytes"] if rows else None,
        }
        if len(rows) < 2 or missing or regressed:
            issues.append(f"{role}: contador ausente, amostra insuficiente ou regressao")
    return {
        "fields_available_and_monotonic": not issues,
        "measurement_approved": False,
        "provenance": "Docker Engine GET /containers/{id}/stats, via Windows named pipe",
        "cpu_interpretation": "cpu_total_ns cumulativo, NAO CPU exclusiva do lote",
        "memory_interpretation": "memory_stats.usage e uso bruto, NAO workingSetBytes Kubernetes; nao ha pico de lote",
        "observer_effect": "sem docker exec; consultas Docker Engine/host ainda usam recursos e precisam de calibracao",
        "issues": issues, "roles": details,
    }


def probe(label, output, samples_count, interval_s):
    network, names = identities(label)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    report = {"status": "FAIL", "label": label, "network": network,
              "read_only": True, "measurement_approved": False}
    observations = []
    try:
        engine = check_local_engine()
        container_ids = assert_new_pilot_containers(names)
        write_json(output / "engine-context.json", {
            "endpoint": engine["endpoint"], "api_version": engine["api_version"],
            "containers": container_ids, "collection": "READ_ONLY, GET only"})
        report["context"] = {"api_version": engine["api_version"], "endpoint": engine["endpoint"]}
        for i in range(samples_count):
            started = time.perf_counter()
            for role in ROLE_ORDER:
                observations.append(engine_stat(
                    engine["pipe"], engine["api_version"], container_ids[role],
                    role, names[role]))
            if i + 1 < samples_count:
                wait_s = interval_s - (time.perf_counter() - started)
                if wait_s > 0:
                    time.sleep(wait_s)
        result = assess(observations, ROLE_ORDER)
        report["assessment"] = result
        report["status"] = "PASS_READ_ONLY" if result["fields_available_and_monotonic"] else "FAIL"
    except Exception as e:
        report["error"] = f"{type(e).__name__}: {e}"
    finally:
        write_jsonl(output / "engine-stats.jsonl", observations)
        write_csv(output / "engine-stats.csv", observations, CSV_FIELDS)
        write_json(output / "probe-report.json", report)
        zipped = archive(output)
        print("STATUS:", report["status"], flush=True)
        print("ZIP:", zipped["zip"], flush=True)
        print("ZIP_SHA256:", zipped["sha256"], flush=True)
        print("READ_ONLY: SIM; SNAPSHOT: NAO; BENCHMARK: NAO", flush=True)
    return report["status"] == "PASS_READ_ONLY"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--label", required=False)
    p.add_argument("--output", type=Path)
    p.add_argument("--samples", type=int, default=2)
    p.add_argument("--interval", type=float, default=1.5)
    p.add_argument("--probe", action="store_true")
    p.add_argument("--pipe-worker", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--pipe", help=argparse.SUPPRESS)
    p.add_argument("--api-version", help=argparse.SUPPRESS)
    p.add_argument("--container-id", help=argparse.SUPPRESS)
    args = p.parse_args(argv)
    if args.pipe_worker:
        try:
            print(json.dumps(_pipe_worker(args.pipe, args.api_version,
                                          args.container_id), separators=(",", ":")))
            return 0
        except Exception as e:
            print(f"GET-only pipe worker: {type(e).__name__}: {e}", file=sys.stderr)
            return 2
    if not args.label or args.output is None:
        p.error("informe --label e --output")
    if not 2 <= args.samples <= 4 or not 0.5 <= args.interval <= 10:
        p.error("samples deve estar em 2..4; interval em 0.5..10s")
    network, names = identities(args.label)
    if not args.probe:
        print(json.dumps({
            "status": "PLAN_ONLY", "read_only": True, "network": network,
            "containers": names, "output": str(args.output), "requests_http_app": 0,
            "docker_exec": False, "benchmark": False, "execute_probe": False,
        }, ensure_ascii=False, indent=2))
        return 0
    return 0 if probe(args.label, args.output, args.samples, args.interval) else 2


if __name__ == "__main__":
    sys.exit(main())
