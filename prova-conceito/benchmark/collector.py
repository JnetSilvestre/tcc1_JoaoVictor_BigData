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



def parse_utc(stamp):
    """ISO UTC com Z ou offset; nunca subtrair relógios monotônicos de máquinas."""
    if not isinstance(stamp, str):
        return None
    try:
        value = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        return None
    return value.astimezone(timezone.utc) if value.tzinfo is not None else None


def quality(samples, expected, batch=None, collection_errors=None,
            min_batch_s=10.0, edge_slack_s=3.0, max_gap_s=4.0,
            min_distinct_samples=5):
    """Disponibilidade de contadores != adequação temporal.

    UTC do cliente e Kubelet serve APENAS à estimativa de cobertura temporal:
    sem garantia medida de sincronismo de relógios nem fronteiras idênticas.
    O delta por bracketing inclui incerteza nas bordas, não CPU exata do lote.
    """
    errors = list(collection_errors or [])
    issues = [f"collector: {x}" for x in errors]
    started = parse_utc((batch or {}).get("batch_started_utc"))
    finished = parse_utc((batch or {}).get("batch_finished_utc"))
    elapsed_ns = (batch or {}).get("elapsed_ns")
    elapsed_s = elapsed_ns / 1e9 if type(elapsed_ns) is int and elapsed_ns >= 0 else None
    valid_window = (started is not None and finished is not None
                    and started < finished and elapsed_s is not None)
    long_enough = bool(valid_window and elapsed_s >= min_batch_s)
    if not valid_window:
        issues.append("batch: marcadores UTC/tempo monotônico ausentes ou inválidos")
    elif not long_enough:
        issues.append(f"batch: duração {elapsed_s:.3f}s inferior ao mínimo experimental {min_batch_s:.3f}s")
    per_role = {}
    for role, (uid, container) in expected.items():
        entries = [r for r in samples if r.get("pod_uid") == uid
                   and r.get("container") == container]
        # A origem do kubelet pode arredondar timestamps a segundos inteiros:
        # a mesma hora pode aparecer com contador CRESCENTE, sem regressao.
        # A monotonicidade e aferida na ordem de captura, nao por valores
        # reordenados por timestamps de baixa resolucao.
        cpu_rows = []
        for idx, row in enumerate(entries):
            stamp = parse_utc(row.get("cpu_time_utc"))
            count = row.get("cpu_usage_core_ns")
            if stamp and type(count) is int and count >= 0:
                cpu_rows.append((stamp, count, idx))
        counter_regression = any(
            cpu_rows[i+1][1] < cpu_rows[i][1]
            for i in range(len(cpu_rows)-1))
        timestamp_regression = any(
            cpu_rows[i+1][0] < cpu_rows[i][0]
            for i in range(len(cpu_rows)-1))
        values_by_stamp = {}
        for stamp, counter, _ in cpu_rows:
            values_by_stamp.setdefault(stamp, []).append(counter)
        # Apenas o ULTIMO valor da mesma marcacao vira representante.
        # Se a duplicata coincidir com borda, o delta nao e aprovado.
        ambiguous_times = {stamp for stamp, values in values_by_stamp.items()
                           if len(set(values)) > 1}
        sequence = sorted((stamp, values[-1])
                          for stamp, values in values_by_stamp.items())
        monotonic = (len(sequence) >= 2 and not counter_regression
                     and not timestamp_regression)
        role_result = {
            "observations": len(entries),
            "unique_cpu_timestamps": len(sequence),
            "cpu_duplicate_timestamp_count": sum(len(v)-1 for v in values_by_stamp.values()),
            "cpu_timestamp_ambiguous_count": len(ambiguous_times),
            "cpu_counter_regressed": bool(counter_regression),
            "cpu_timestamp_regressed": bool(timestamp_regression),
            "cpu_counter_present_monotonic": bool(monotonic),
            "cpu_window_adequate": False,
            "memory_window_adequate": False,
            "first_cpu_time_utc": sequence[0][0].isoformat() if sequence else None,
            "last_cpu_time_utc": sequence[-1][0].isoformat() if sequence else None,
            "cpu_delta_bracketing_s": None,
            "cpu_bracketing_span_s": None,
            "memory_max_sampled_mib": None,
        }
        memory_rows = []
        for row in entries:
            mt = parse_utc(row.get("memory_time_utc"))
            mv = row.get("memory_working_set_bytes")
            if mt and type(mv) is int and mv >= 0:
                memory_rows.append((mt, mv))
        if memory_rows:
            role_result["memory_max_sampled_mib"] = max(v for _,v in memory_rows) / (1024**2)
        if not monotonic:
            issues.append(f"{role}: CPU ausente, regressivo ou timestamp decrescente")
        if ambiguous_times:
            issues.append(f"{role}: {len(ambiguous_times)} timestamps CPU duplicados com contadores diferentes; resolucao temporal insuficiente nesses instantes")
        if not memory_rows:
            issues.append(f"{role}: working set ausente")
        if monotonic and long_enough and not errors:
            before = [p for p in sequence if p[0] <= started]
            after = [p for p in sequence if p[0] >= finished]
            if before and after:
                left, right = before[-1], after[0]
                bracket = [p for p in sequence if left[0] <= p[0] <= right[0]]
                gap = max(((bracket[i+1][0]-bracket[i][0]).total_seconds()
                           for i in range(len(bracket)-1)), default=float("inf"))
                left_margin = (started-left[0]).total_seconds()
                right_margin = (right[0]-finished).total_seconds()
                if (left_margin <= edge_slack_s and right_margin <= edge_slack_s
                        and left[0] not in ambiguous_times
                        and right[0] not in ambiguous_times
                        and len(bracket) >= min_distinct_samples and gap <= max_gap_s):
                    role_result["cpu_window_adequate"] = True
                    role_result["cpu_delta_bracketing_s"] = (right[1]-left[1]) / 1e9
                    role_result["cpu_bracketing_span_s"] = (right[0]-left[0]).total_seconds()
            if not role_result["cpu_window_adequate"]:
                issues.append(f"{role}: cobertura temporal da CPU insuficiente")
        if long_enough and not errors and memory_rows:
            mem_unique = sorted(set(t for t,_ in memory_rows))
            before = [t for t in mem_unique if t <= started]
            after = [t for t in mem_unique if t >= finished]
            if before and after:
                bracket = [t for t in mem_unique if before[-1] <= t <= after[0]]
                gap = max(((bracket[i+1]-bracket[i]).total_seconds()
                           for i in range(len(bracket)-1)), default=float("inf"))
                role_result["memory_window_adequate"] = (
                    len(bracket) >= min_distinct_samples and gap <= max_gap_s
                    and (started-before[-1]).total_seconds() <= edge_slack_s
                    and (after[0]-finished).total_seconds() <= edge_slack_s
                )
            if not role_result["memory_window_adequate"]:
                issues.append(f"{role}: cobertura temporal da memória insuficiente")
        per_role[role] = role_result
    cpu_counter_ok = all(x["cpu_counter_present_monotonic"] for x in per_role.values())
    cpu_window_ok = all(x["cpu_window_adequate"] for x in per_role.values())
    memory_window_ok = all(x["memory_window_adequate"] for x in per_role.values())
    return {
        "cpu_counter_present_monotonic": cpu_counter_ok,
        "cpu_window_adequate": cpu_window_ok,
        "memory_window_adequate": memory_window_ok,
        "usable_cpu": cpu_window_ok,  # conservador, legado
        "usable_memory": memory_window_ok,
        "batch_elapsed_s": elapsed_s,
        "minimum_batch_s_for_quality_gate": min_batch_s,
        "edge_slack_s": edge_slack_s,
        "max_sample_gap_s": max_gap_s,
        "min_distinct_samples": min_distinct_samples,
        "sample_count": len(samples),
        "roles": per_role,
        "issues": issues,
        "interpretation": "CPU delta em amostras que cercam o lote; NAO atribuir consumo exato. Working-set maximo apenas amostrado.",
    }
