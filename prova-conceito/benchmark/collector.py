"""Kubelet Summary API: coleta SOMENTE LEITURA; nao consulta endpoints da aplicacao."""
from datetime import datetime, timezone
import json
import subprocess
import time


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def parse_summary(body, namespace, node, retrieved_utc, duration_s):
    rows = []
    for pod in body.get("pods", []):
        identity = pod.get("podRef") or {}
        if identity.get("namespace") != namespace:
            continue
        net = pod.get("network") or {}
        for container in pod.get("containers", []):
            cpu = container.get("cpu") or {}
            mem = container.get("memory") or {}
            rows.append({
                "retrieved_utc": retrieved_utc, "collector_seconds": duration_s,
                "node": node, "namespace": namespace, "pod": identity.get("name"),
                "pod_uid": identity.get("uid"), "container": container.get("name"),
                "cpu_time_utc": cpu.get("time"),
                "cpu_usage_core_ns": cpu.get("usageCoreNanoSeconds"),
                "memory_time_utc": mem.get("time"),
                "memory_working_set_bytes": mem.get("workingSetBytes"),
                "network_rx_bytes_pod": net.get("rxBytes"),
                "network_tx_bytes_pod": net.get("txBytes"),
                "network_interfaces": len(net.get("interfaces") or []),
            })
    return rows


def capture(context, namespace, nodes, timeout=15):
    result = []
    for node in nodes:
        t0 = time.perf_counter()
        proc = subprocess.run(
            ["kubectl", "--context", context, "get", "--raw",
             f"/api/v1/nodes/{node}/proxy/stats/summary"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=timeout, check=False)
        elapsed = time.perf_counter() - t0
        stamp = utc_now()
        if proc.returncode != 0:
            raise RuntimeError(f"Summary API de {node} falhou: {proc.stderr[-300:]}")
        result.extend(parse_summary(json.loads(proc.stdout), namespace, node, stamp, elapsed))
    return result


def quality(samples, expected):
    """Conservador: nao usar CPU como zero quando timestamps nao evoluirem."""
    issues = []
    for role, (uid, container) in expected.items():
        rows = [r for r in samples if r["pod_uid"] == uid and r["container"] == container]
        timepoints = {r["cpu_time_utc"] for r in rows if r["cpu_usage_core_ns"] is not None}
        if len(rows) < 2 or len(timepoints) < 2:
            issues.append(f"{role}: contador CPU sem duas amostras temporais distintas")
        elif rows[-1]["cpu_usage_core_ns"] < rows[0]["cpu_usage_core_ns"]:
            issues.append(f"{role}: contador CPU regrediu (possivel reinicio)")
        if not any(r["memory_working_set_bytes"] is not None for r in rows):
            issues.append(f"{role}: memoria ausente")
    return {"usable_cpu": not any("CPU" in s for s in issues),
            "issues": issues, "sample_count": len(samples)}
