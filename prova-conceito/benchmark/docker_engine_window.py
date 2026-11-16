"""E11-I06: amostragem externa Docker Engine API durante lote C2.

Somente GET por named pipe do Windows. O processo de carga usa docker exec
APENAS no conteiner CLIENTE, nunca para coletar métricas dos servicos.
As janelas de CPU fornecem deltas aproximados entre amostras envolventes,
nao consumo exato; memoria Docker NAO equivale a workingSet Kubelet.
"""
from datetime import datetime, timezone
import threading
import time

from benchmark import docker_engine_api as engine

ROLES = ("attribute-source", "logic-engine", "rule-executor", "client")


def utc_parse(value):
    if not isinstance(value, str):
        return None
    try:
        date = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, OverflowError):
        return None
    return date.astimezone(timezone.utc) if date.tzinfo else None


class EngineSampler:
    """Coleta externa por GET. A sondagem nunca inicia ou reinicia containers."""

    def __init__(self, names, period, engine_module=None):
        self.names, self.period = names, period
        self.engine = engine if engine_module is None else engine_module
        self.ids = None
        self.context = None
        self.samples, self.errors, self.rounds = [], [], []
        self.done = threading.Event()
        self.worker = threading.Thread(target=self._loop, daemon=True)

    def preflight(self):
        """FALHAR antes do snapshot se a interface de observacao for invalida."""
        self.context = self.engine.check_local_engine()
        self.ids = self.engine.assert_new_pilot_containers(self.names)
        if set(self.ids) != set(ROLES):
            raise ValueError("os quatro conteineres C2 nao foram identificados")

    def context_record(self):
        return {
            "api_version": self.context["api_version"],
            "endpoint": self.context["endpoint"],
            "container_ids": self.ids,
            "metric_source": "Docker Engine GET stats?stream=false&one-shot=true",
            "metric_scope": "containers; leitura externa por Windows named pipe",
            "cpu_semantics": "contador cumulativo; delta de bracketing com incerteza",
            "memory_semantics": "uso bruto, nao workingSetBytes Kubelet",
            "measurement_approved": False,
        }

    def one_round(self):
        t0 = time.perf_counter()
        rows = []
        # Guardar a rodada inteira para distinguir sequencialidade de simultaneidade.
        for role in ROLES:
            rows.append(self.engine.engine_stat(
                self.context["pipe"], self.context["api_version"],
                self.ids[role], role, self.names[role]))
        self.samples.extend(rows)
        self.rounds.append(time.perf_counter() - t0)

    def prime(self):
        """Primeira rodada antes do lote: erro impede qualquer POST."""
        self.one_round()

    def _loop(self):
        while not self.done.is_set():
            started = time.perf_counter()
            try:
                self.one_round()
            except Exception as e:
                self.errors.append(f"{type(e).__name__}: {e}")
            self.done.wait(max(0.0, self.period - (time.perf_counter()-started)))

    def start(self):
        self.worker.start()

    def stop(self):
        self.done.set()
        self.worker.join(timeout=90)
        if self.worker.is_alive():
            self.errors.append("thread de observacao ainda ativa apos timeout")
            return
        try:
            self.one_round()
        except Exception as e:
            self.errors.append(f"after: {type(e).__name__}: {e}")


def quality_window(samples, expected_ids, summary=None, errors=None,
                   minimum_batch_s=10.0, max_edge_s=3.0,
                   max_gap_s=4.0, minimum_points=5, max_stale_s=5.0):
    """Disponibilidade dos campos != adequacao temporal != calibracao.

    expected_ids mapeia cada papel ao ID Docker exato. Usa Docker read UTC
    para fronteiras estimadas; exige frescor de read/retrieved e identidade.
    CPU delta nao corresponde necessariamente ao lote exato.
    """
    summary = summary or {}
    errors = list(errors or [])
    started = utc_parse(summary.get("batch_started_utc"))
    finished = utc_parse(summary.get("batch_finished_utc"))
    elapsed_ns = summary.get("elapsed_ns")
    batch_s = elapsed_ns / 1e9 if type(elapsed_ns) is int and elapsed_ns >= 0 else None
    clock_valid = (started is not None and finished is not None and
                   finished > started and batch_s is not None)
    utc_s = (finished-started).total_seconds() if clock_valid else None
    discrepancy = abs(utc_s-batch_s) if clock_valid else None
    clock_coherent = bool(clock_valid and discrepancy <= max(.25, .05 * batch_s))
    long_enough = bool(clock_coherent and batch_s >= minimum_batch_s)
    issues = [f"collector: {e}" for e in errors]
    if not clock_valid:
        issues.append("batch: marcadores invalidos")
    elif not clock_coherent:
        issues.append("batch: UTC diverge da duracao monotônica")
    elif not long_enough:
        issues.append(f"batch: {batch_s:.3f}s abaixo de {minimum_batch_s:.1f}s")
    details = {}
    for role, cid in expected_ids.items():
        rows = [r for r in samples if r.get("role") == role]
        has_wrong_id = any(r.get("container_id") != cid for r in rows)
        clock_issues = False
        counter_regressed = False
        timestamp_regressed = False
        entries = []
        all_fields = len(rows) >= 2
        for r in rows:
            t = utc_parse(r.get("docker_read_utc"))
            retrieved = utc_parse(r.get("retrieved_utc"))
            value, mem = r.get("cpu_total_ns"), r.get("memory_usage_bytes")
            valid_count = type(value) is int and value >= 0
            valid_memory = type(mem) is int and mem >= 0
            if not valid_count or not valid_memory or t is None or retrieved is None:
                all_fields = False
                continue
            age_s = (retrieved-t).total_seconds()
            if not -0.5 <= age_s <= max_stale_s:
                clock_issues = True
            entries.append((t, value))
        for (t0, c0), (t1, c1) in zip(entries, entries[1:]):
            if c1 < c0:
                counter_regressed = True
            if t1 < t0:
                timestamp_regressed = True
        distinct = {}
        for t, count in entries:
            distinct.setdefault(t, []).append(count)
        ambiguous = {t for t, values in distinct.items() if len(set(values)) > 1}
        timeline = sorted((t, vals[-1]) for t, vals in distinct.items())
        counter_ok = (all_fields and not counter_regressed
                      and not timestamp_regressed and not has_wrong_id
                      and not clock_issues and len(timeline) >= 2)
        cpu_covered = False
        delta_s = None
        bracket_span_s = None
        edge_before_s = None
        edge_after_s = None
        max_observed_gap = None
        if counter_ok and long_enough and not errors:
            before = [x for x in timeline if x[0] <= started]
            after = [x for x in timeline if x[0] >= finished]
            if before and after:
                l, r = before[-1], after[0]
                in_window = [x for x in timeline if l[0] <= x[0] <= r[0]]
                gaps = [(b[0]-a[0]).total_seconds()
                        for a,b in zip(in_window,in_window[1:])]
                max_observed_gap = max(gaps, default=None)
                edge_before_s = (started-l[0]).total_seconds()
                edge_after_s = (r[0]-finished).total_seconds()
                cpu_covered = bool(
                    l[0] not in ambiguous and r[0] not in ambiguous
                    and len(in_window) >= minimum_points
                    and max_observed_gap is not None
                    and max_observed_gap <= max_gap_s
                    and edge_before_s <= max_edge_s
                    and edge_after_s <= max_edge_s)
                if cpu_covered:
                    delta_s = (r[1]-l[1]) / 1e9
                    bracket_span_s = (r[0]-l[0]).total_seconds()
        detail = {
            "samples": len(rows),
            "unique_source_timestamps": len(timeline),
            "duplicate_source_timestamps": len(entries)-len(timeline),
            "ambiguous_source_timestamps": len(ambiguous),
            "fields_available": all_fields,
            "identity_stable": not has_wrong_id,
            "source_timestamp_fresh": not clock_issues,
            "cpu_counter_regressed": counter_regressed,
            "source_timestamp_regressed": timestamp_regressed,
            "counter_available_monotonic": counter_ok,
            "cpu_window_adequate": cpu_covered,
            "cpu_delta_bracketing_s": delta_s,
            "bracketing_span_s": bracket_span_s,
            "edge_before_s": edge_before_s,
            "edge_after_s": edge_after_s,
            "max_source_gap_s": max_observed_gap,
            "memory_usage_max_sampled_bytes": max(
                (r["memory_usage_bytes"] for r in rows
                 if type(r.get("memory_usage_bytes")) is int), default=None),
        }
        if not counter_ok:
            issues.append(f"{role}: campos, identidade, relogios ou contador invalidos")
        elif not cpu_covered:
            issues.append(f"{role}: janela CPU nao delimitada adequadamente")
        details[role] = detail
    all_counters = bool(details) and all(
        d["counter_available_monotonic"] for d in details.values())
    temporal = bool(details) and all(d["cpu_window_adequate"] for d in details.values())
    return {
        "cpu_counters_available": all_counters,
        "cpu_window_adequate": temporal,
        "memory_window_adequate": False,
        "measurement_approved": False,
        "memory_comparable_to_kubelet": False,
        "batch_elapsed_s": batch_s,
        "batch_utc_elapsed_s": utc_s,
        "utc_monotonic_discrepancy_s": discrepancy,
        "clock_coherent": clock_coherent,
        "thresholds_provisional": {
            "minimum_batch_s": minimum_batch_s, "max_edge_s": max_edge_s,
            "max_gap_s": max_gap_s, "minimum_points": minimum_points,
            "max_source_age_s": max_stale_s},
        "roles": details,
        "issues": issues,
        "interpretation": (
            "Deltas de CPU com bracketing somente quando cobertura validada; "
            "nao sao custos exatos. Memoria Docker bruta nao e working set. "
            "Overhead do monitor e efeito da plataforma nao calibrados."),
    }
