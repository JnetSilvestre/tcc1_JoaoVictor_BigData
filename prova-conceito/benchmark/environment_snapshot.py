"""E11-M00C: inventario versionavel do host, SOMENTE LEITURA.

Executar antes do snapshot e fora da janela de T_batch. Dados pontuais
nao aprovam automaticamente capacidade, equivalencia ou quotas fisicas.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CONTEXT = "kind-tcc2-pon"
IMAGE = "tcc2-pon:c2-e08-dbefcd2cf3d2"
IMAGE_ID = "sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a"


def run_readonly(*argv):
    proc = subprocess.run(
        list(argv), cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=35, check=False)
    if proc.returncode:
        raise RuntimeError(f"consulta somente leitura falhou: {argv[0:3]!r}, "
                           f"exit={proc.returncode}, stderr={proc.stderr[-400:]}")
    return proc.stdout.strip()


def capture_environment(scenario, run_id, *, reader=None, root=None,
                        os_name=None, disk_usage=None):
    """Captura 1 baseline; readers injetaveis permitem testes sem Docker/kubectl."""
    if scenario not in ("C2", "C3", "C4") or not run_id.startswith("e11-"):
        raise ValueError("cenario/run_id invalidos")
    query = reader if reader is not None else run_readonly
    base = Path(root) if root is not None else ROOT
    usage = disk_usage if disk_usage is not None else shutil.disk_usage
    system = os_name if os_name is not None else platform.system()
    disk = usage(base)
    if disk.total <= 0 or disk.free < 0:
        raise ValueError("inventario de disco invalido")

    docker_raw = query("docker", "info", "--format",
                       "{{.CgroupVersion}}|{{.NCPU}}|{{.MemTotal}}").strip()
    fields = docker_raw.split("|")
    if len(fields) != 3 or fields[0] not in ("1", "2"):
        raise ValueError("informacoes Docker cgroup ausentes")
    docker_cpus, docker_ram = int(fields[1]), int(fields[2])
    if docker_cpus <= 0 or docker_ram <= 0:
        raise ValueError("recursos Docker invalidos")

    image_id = query("docker", "image", "inspect", IMAGE, "--format", "{{.Id}}").strip()
    if image_id != IMAGE_ID:
        raise ValueError("imagem Docker divergente do ID aprovado")

    record = {
        "status": "BASELINE_READ_ONLY_NOT_CAPACITY_APPROVAL",
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "scenario": scenario,
        "run_id": run_id,
        "git_sha": query("git", "rev-parse", "HEAD").strip(),
        "os_family": system,
        "os_release": platform.release(),
        "python_version": sys.version.split()[0],
        "logical_cpus_visible_to_python": os.cpu_count(),
        "disk_total_bytes": disk.total,
        "disk_free_bytes": disk.free,
        "docker_context": query("docker", "context", "show").strip(),
        "docker_cgroup_version": fields[0],
        "docker_cpus": docker_cpus,
        "docker_mem_total_bytes": docker_ram,
        "image_tag": IMAGE,
        "image_id": image_id,
        "windows_host_ram_total_bytes": None,
        "windows_host_ram_free_bytes": None,
        "node_allocatable": None,
        "cpu_ram_comparison_approved": False,
        "note": "Leitura pontual PRE-snapshot; nao mede uso durante lote, quotas efetivas ou host livre em M01",
    }
    if record["docker_context"] != "desktop-linux":
        raise ValueError("Docker context diferente do inventariado")

    if system == "Windows":
        script = (
            "$ErrorActionPreference='Stop';"
            "$pc=Get-CimInstance Win32_ComputerSystem;"
            "$os=Get-CimInstance Win32_OperatingSystem;"
            "[pscustomobject]@{"
            "total_bytes=[int64]$pc.TotalPhysicalMemory;"
            "free_bytes=([int64]$os.FreePhysicalMemory*1024)"
            "} | ConvertTo-Json -Compress"
        )
        host = json.loads(query("powershell.exe", "-NoProfile", "-NonInteractive",
                                "-Command", script))
        total, free = host.get("total_bytes"), host.get("free_bytes")
        if type(total) is not int or type(free) is not int or not 0 <= free <= total:
            raise ValueError("RAM Windows nao pode ser verificada")
        record["windows_host_ram_total_bytes"] = total
        record["windows_host_ram_free_bytes"] = free

    if scenario in ("C3", "C4"):
        raw = query("kubectl", "--context", CONTEXT, "get", "nodes", "-o", "json")
        items = json.loads(raw)["items"]
        nodes = {}
        for item in items:
            name = item["metadata"]["name"]
            nodes[name] = {
                "uid": item["metadata"].get("uid"),
                "allocatable": item.get("status", {}).get("allocatable"),
                "ready": any(c.get("type") == "Ready" and c.get("status") == "True"
                             for c in item.get("status", {}).get("conditions", [])),
            }
        if not {"tcc2-pon-worker", "tcc2-pon-control-plane"}.issubset(nodes):
            raise ValueError("nos kind obrigatorios ausentes")
        if not all(nodes[n]["ready"] for n in (
                "tcc2-pon-worker", "tcc2-pon-control-plane")):
            raise ValueError("node kind nao Ready")
        record["node_allocatable"] = nodes
    return record
