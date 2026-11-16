"""E11-M00B: selecao declarativa da instrumentacao, sem efeitos de I/O.

O modo timing_only NAO cria monitor de recursos. A falta de amostras e
documentada como NOT_COLLECTED, nunca como CPU/RAM igual a zero.
"""
TIMING_ONLY = "timing_only"
RESOURCES_DIAGNOSTIC = "resources_diagnostic"
MODES = (TIMING_ONLY, RESOURCES_DIAGNOSTIC)


def require_new_timing_identity(mode, scenario, label, run_id):
    """Timing_only e exclusivo de futura bancada M01 com ID distinto dos pilotos P."""
    import re

    if mode not in MODES or scenario not in ("C2", "C3", "C4"):
        raise ValueError("modo/cenario invalido")
    if mode == TIMING_ONLY:
        if not re.fullmatch(r"m[a-z0-9][a-z0-9-]{1,20}", label):
            raise ValueError("timing_only exige label inedito com prefixo m")
        if run_id != f"e11-{scenario.lower()}-{label}":
            raise ValueError("timing_only exige run_id exclusivo ligado ao cenario/label")
    return True


def select_sampler(mode, factory):
    """Factory deve ser invocada APENAS em modo diagnostico."""
    if mode == TIMING_ONLY:
        return None
    if mode == RESOURCES_DIAGNOSTIC:
        return factory()
    raise ValueError("modo de instrumentacao desconhecido")


def profile_record(mode):
    if mode not in MODES:
        raise ValueError("modo de instrumentacao desconhecido")
    return {
        "measurement_mode": mode,
        "resource_sampling_during_batch": mode == RESOURCES_DIAGNOSTIC,
        "resource_metrics_comparable": False,
        "scientific_note": (
            "E11-M00B: modo preparado; nao aprova serie quantitativa ou CPU/RAM"
        ),
    }


def not_collected_quality():
    """Sem amostras, retornos NULL, nao contadores sinteticamente zerados."""
    return {
        "status": "NOT_COLLECTED",
        "reason": "timing_only: nenhuma sonda periodica de CPU/memoria",
        "resource_metrics_collected": False,
        "sample_count": None,
        "cpu_window_adequate": None,
        "memory_window_adequate": None,
        "usable_cpu": False,
        "usable_memory": False,
        "measurement_approved": False,
        "memory_comparable_to_kubelet": None,
    }
