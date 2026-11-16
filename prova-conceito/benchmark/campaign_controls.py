"""E11-M00C: conferencia final e UNIFORME do estado frio, somente GET/logs.

O chamador injeta tres leitores, que DEVEM ser read-only. Este modulo nao
possui cliente Docker/kubectl, nao faz POST, snapshot, reset ou exclusao.
"""
from datetime import datetime, timezone

ROLES = ("attribute-source", "logic-engine", "rule-executor")
EXPECTED_ATTRIBUTES = {"atA": 0, "atB": 0}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def _empty(value):
    return isinstance(value, list) and len(value) == 0


def validate_cold(health, states, logs):
    """Falhar fechado se GETs/estados/ledgers diferirem do zero pre-snapshot."""
    if set(health) != set(ROLES) or set(states) != set(ROLES) or set(logs) != set(ROLES):
        raise ValueError("conferencia fria incompleta")
    for role in ROLES:
        live = health[role]
        state = states[role]
        entries = logs[role]
        if not isinstance(live, dict) or live.get("live") is not True:
            raise ValueError(f"{role}: GET health/live invalido")
        if not isinstance(state, dict) or state.get("ready") is not False or state.get("run_id") is not None:
            raise ValueError(f"{role}: estado ja iniciado")
        if not isinstance(entries, list) or any(not isinstance(x, dict) for x in entries):
            raise ValueError(f"{role}: logs invalidos")
        if any(x.get("event_type") == "mutation" for x in entries):
            raise ValueError(f"{role}: historico de mutacao pre-snapshot")
    source, logic, executor = (states[r] for r in ROLES)
    # Contrato REAL c1/state.py antes do primeiro snapshot:
    # source nasce com atributos zerados; logic ainda nao possui
    # atributos/condicao; executor nao possui sinal de aprovacao.
    if source.get("attributes") != EXPECTED_ATTRIBUTES:
        raise ValueError("source: atributos nao zerados")
    if source.get("sequences") != EXPECTED_ATTRIBUTES:
        raise ValueError("source: contadores nao zerados")
    if logic.get("attributes") is not None:
        raise ValueError("logic: atributos ja inicializados")
    if logic.get("sequences") != EXPECTED_ATTRIBUTES:
        raise ValueError("logic: contadores nao zerados")
    if source.get("pending_request_id") is not None:
        raise ValueError("source com requisicao pendente")
    if (logic.get("condition") is not None
            or logic.get("condition_sequence") != 0
            or not _empty(logic.get("received_ids"))
            or not _empty(logic.get("condition_events"))
            or logic.get("faulted") is not False):
        raise ValueError("logic nao esta fria")
    if (executor.get("approved") is not None
            or executor.get("condition_sequence") != 0
            or not _empty(executor.get("received_ids"))
            or not _empty(executor.get("effects"))
            or executor.get("faulted") is not False):
        raise ValueError("executor nao esta frio")
    return {
        "status": "PASS_COLD_READ_ONLY",
        "requests_per_role": {"GET /health/live": 1, "GET /state": 1, "logs": 1},
        "mutation_count": 0,
        "pre_snapshot": True,
        "functional_warmup_posts": 0,
        "note": "GETs finais nao equivalem a aquecimento por carga; demais readiness/probes preexistem",
    }


def final_readonly_cold_check(get_health, get_state, get_logs):
    """Uma passada fixa: 3 GET health, 3 GET state e 3 leituras de logs."""
    started = utc_now()
    health, states, logs = {}, {}, {}
    for role in ROLES:
        health[role] = get_health(role)
        states[role] = get_state(role)
        logs[role] = get_logs(role)
    assessment = validate_cold(health, states, logs)
    assessment["started_utc"] = started
    assessment["ended_utc"] = utc_now()
    assessment["health"] = health
    assessment["states"] = states
    assessment["log_count_by_role"] = {r: len(logs[r]) for r in ROLES}
    return assessment
