"""Contratos de mensagens v1 para o cenário C1, somente biblioteca padrão."""
from datetime import datetime, timezone


class ContractError(ValueError):
    def __init__(self, message, status=422):
        super().__init__(message)
        self.status = status


def _object(payload, required, optional=()):
    if not isinstance(payload, dict):
        raise ContractError("payload deve ser objeto JSON")
    missing = set(required) - set(payload)
    unexpected = set(payload) - set(required) - set(optional)
    if missing or unexpected:
        raise ContractError(f"campos invalidos: ausentes={sorted(missing)}, extras={sorted(unexpected)}")


def _nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{label} deve ser string nao vazia")


def _int(value, label, minimum=None):
    if type(value) is not int or (minimum is not None and value < minimum):
        raise ContractError(f"{label} deve ser inteiro valido")


def _utc(value):
    _nonempty(value, "emitted_at")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError("emitted_at ISO 8601 invalido") from exc
    if dt.tzinfo is None or dt.utcoffset() != timezone.utc.utcoffset(dt):
        raise ContractError("emitted_at precisa estar em UTC")


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def validate_change(payload):
    _object(payload, {"run_id", "request_id", "entity_id", "value"}, {"step"})
    _nonempty(payload["run_id"], "run_id")
    _nonempty(payload["request_id"], "request_id")
    if payload["entity_id"] not in ("atA", "atB"):
        raise ContractError("entity_id desconhecido")
    _int(payload["value"], "value")
    if "step" in payload:
        _int(payload["step"], "step", minimum=1)
    return payload


def validate_snapshot(payload):
    _object(payload, {"schema_version", "run_id", "snapshot_version", "attributes", "sequences"})
    if type(payload["schema_version"]) is not int or payload["schema_version"] != 1:
        raise ContractError("schema_version incompativel")
    _nonempty(payload["run_id"], "run_id")
    _nonempty(payload["snapshot_version"], "snapshot_version")
    for name in ("attributes", "sequences"):
        if not isinstance(payload[name], dict) or set(payload[name]) != {"atA", "atB"}:
            raise ContractError(f"{name} deve conter atA/atB")
    for k, v in payload["attributes"].items():
        _int(v, f"attributes.{k}")
    for k, v in payload["sequences"].items():
        _int(v, f"sequences.{k}", minimum=0)
    return payload


def validate_executor_snapshot(payload):
    _object(payload, {"schema_version", "run_id", "snapshot_version", "condition_sequence", "approved"})
    if type(payload["schema_version"]) is not int or payload["schema_version"] != 1:
        raise ContractError("schema_version incompativel")
    _nonempty(payload["run_id"], "run_id")
    _nonempty(payload["snapshot_version"], "snapshot_version")
    _int(payload["condition_sequence"], "condition_sequence", minimum=0)
    if type(payload["approved"]) is not bool:
        raise ContractError("approved deve ser booleano")
    return payload


def validate_attribute_event(payload):
    _object(payload, {"schema_version", "event_id", "run_id", "source", "entity_id", "sequence", "value", "emitted_at"}, {"step", "request_id"})
    if type(payload["schema_version"]) is not int or payload["schema_version"] != 1:
        raise ContractError("schema_version incompativel")
    _nonempty(payload["run_id"], "run_id")
    if payload["source"] != "attribute-source":
        raise ContractError("source incorreta")
    if payload["entity_id"] not in ("atA", "atB"):
        raise ContractError("entity_id desconhecido")
    _int(payload["sequence"], "sequence", minimum=1)
    _int(payload["value"], "value")
    _utc(payload["emitted_at"])
    if payload["event_id"] != f'{payload["run_id"]}:{payload["entity_id"]}:{payload["sequence"]}':
        raise ContractError("event_id nao corresponde a run/entity/sequence")
    if "request_id" in payload:
        _nonempty(payload["request_id"], "request_id")
    if "step" in payload:
        _int(payload["step"], "step", minimum=1)
    return payload


def validate_condition_event(payload):
    _object(payload, {"schema_version", "event_id", "run_id", "source", "entity_id", "sequence", "approved", "caused_by", "emitted_at"}, {"step"})
    if type(payload["schema_version"]) is not int or payload["schema_version"] != 1:
        raise ContractError("schema_version incompativel")
    _nonempty(payload["run_id"], "run_id")
    if payload["source"] != "logic-engine" or payload["entity_id"] != "cn1":
        raise ContractError("source/entity_id de condicao incorreta")
    _int(payload["sequence"], "sequence", minimum=1)
    if type(payload["approved"]) is not bool:
        raise ContractError("approved deve ser booleano")
    _nonempty(payload["caused_by"], "caused_by")
    _utc(payload["emitted_at"])
    if payload["event_id"] != f'{payload["run_id"]}:cn1:{payload["sequence"]}':
        raise ContractError("event_id nao corresponde a run/condition/sequence")
    if "step" in payload:
        _int(payload["step"], "step", minimum=1)
    return payload
