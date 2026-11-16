"""E11-M00B: selecao declarativa da instrumentacao, sem efeitos de I/O.

O modo timing_only NAO cria monitor de recursos. A falta de amostras e
documentada como NOT_COLLECTED, nunca como CPU/RAM igual a zero.
"""
TIMING_ONLY = "timing_only"
RESOURCES_DIAGNOSTIC = "resources_diagnostic"
MODES = (TIMING_ONLY, RESOURCES_DIAGNOSTIC)


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
