"""Estado local para os três papéis de C1.

Callbacks de envio são injetados. Neste incremento, a ligação é direta
para testes unitários; transporte HTTP e isolamento por PID virão depois.
Não há persistência, concorrência segura ou recuperação automática.
"""

from pon import Action, Attribute, Condition, Instigation, Rule
from .protocol import (
    ContractError, utc_now, validate_attribute_event, validate_change,
    validate_condition_event, validate_executor_snapshot, validate_snapshot,
)


class AttributeSource:
    """Estado autoritativo do produtor, com retry estável por request_id."""

    def __init__(self, send_snapshot, send_attribute):
        self.send_snapshot = send_snapshot
        self.send_attribute = send_attribute
        self.run_id = None
        self.snapshot_version = None
        self.values = {"atA": 0, "atB": 0}
        self.sequences = {"atA": 0, "atB": 0}
        self.requests = {}
        self.pending = None

    @property
    def ready(self):
        return self.run_id is not None

    def initialize(self, run_id):
        if not isinstance(run_id, str) or not run_id.strip():
            raise ContractError("run_id invalido")
        if self.ready:
            if run_id == self.run_id:
                return {"ready": True, "snapshot_version": self.snapshot_version, "duplicate": True}
            raise ContractError("outra rodada ja inicializada", status=409)
        snapshot = {
            "schema_version": 1, "run_id": run_id,
            "snapshot_version": f"{run_id}:snapshot:0",
            "attributes": dict(self.values), "sequences": dict(self.sequences),
        }
        self.send_snapshot(snapshot)
        # Só aceitar mudanças após confirmação do snapshot.
        self.run_id = run_id
        self.snapshot_version = snapshot["snapshot_version"]
        return {"ready": True, "snapshot_version": self.snapshot_version, "duplicate": False}

    def change(self, payload):
        validate_change(payload)
        if not self.ready or payload["run_id"] != self.run_id:
            raise ContractError("source nao inicializado para esta rodada", status=409)
        request_id = payload["request_id"]
        if request_id in self.requests:
            old_payload, response = self.requests[request_id]
            if old_payload != payload:
                raise ContractError("request_id conflitante", status=409)
            return {**response, "duplicate_request": True}
        if self.pending is not None and self.pending["payload"] != payload:
            raise ContractError("envio pendente, reenvie primeiro request_id", status=409)

        name = payload["entity_id"]
        if self.pending is None:
            changed = self.values[name] != payload["value"]
            sequence = self.sequences[name] + (1 if changed else 0)
            event_id = f"{self.run_id}:{name}:{sequence}" if changed else None
            response = {
                "changed": changed, "sequence": sequence,
                "event_id": event_id, "duplicate_request": False,
            }
            if not changed:
                self.requests[request_id] = (dict(payload), response)
                return response
            event = {
                "schema_version": 1, "event_id": event_id,
                "run_id": self.run_id, "source": "attribute-source",
                "entity_id": name, "sequence": sequence, "value": payload["value"],
                "emitted_at": utc_now(), "request_id": request_id,
            }
            if "step" in payload:
                event["step"] = payload["step"]
            self.pending = {
                "payload": dict(payload), "event": event, "response": response,
            }

        # Em caso de exceção, manter pendente o MESMO evento com MESMO timestamp.
        # Se o receptor recebeu e a resposta se perdeu, poderá deduplicar por ID.
        self.send_attribute(self.pending["event"])
        record = self.pending
        self.values[name] = payload["value"]
        self.sequences[name] = record["response"]["sequence"]
        self.requests[request_id] = (dict(payload), record["response"])
        self.pending = None
        return record["response"]

    def state(self):
        return {
            "ready": self.ready, "run_id": self.run_id,
            "snapshot_version": self.snapshot_version,
            "attributes": dict(self.values), "sequences": dict(self.sequences),
            "pending_request_id": self.pending["payload"]["request_id"] if self.pending else None,
        }


class _ConditionObserver:
    def __init__(self, condition, callback):
        self.condition = condition
        self.callback = callback

    def update(self, notifier_id):
        self.callback(self.condition.approved())


class LogicEngine:
    """Réplicas de atributos + Premise/Condition PON com watermark por origem."""

    def __init__(self, send_executor_snapshot, send_condition):
        self.send_executor_snapshot = send_executor_snapshot
        self.send_condition = send_condition
        self.run_id = None
        self.snapshot_version = None
        self._snapshot = None
        self.attributes = None
        self.condition = None
        self.sequences = {"atA": 0, "atB": 0}
        self.condition_sequence = 0
        self.ledger = {}
        self.condition_events = []
        self.current_event = None
        self.faulted = False

    @property
    def ready(self):
        return self.run_id is not None and not self.faulted

    def initialize(self, snapshot):
        validate_snapshot(snapshot)
        if self.run_id is not None:
            if snapshot == self._snapshot:
                return {"ready": self.ready, "duplicate": True}
            raise ContractError("snapshot diferente apos inicializacao", status=409)
        # Sem historico das transicoes, C1 inicial exige watermark zero.
        if any(snapshot["sequences"].values()):
            raise ContractError("C1 inicial requer watermarks zero; replay nao implementado", status=409)
        attributes = {name: Attribute(value) for name, value in snapshot["attributes"].items()}
        condition = (attributes["atA"] >= 5) & (attributes["atB"] == 1)
        condition.register(_ConditionObserver(condition, self._on_transition))
        executor_snapshot = {
            "schema_version": 1, "run_id": snapshot["run_id"],
            "snapshot_version": snapshot["snapshot_version"],
            "condition_sequence": 0, "approved": condition.approved(),
        }
        self.send_executor_snapshot(executor_snapshot)
        self.run_id = snapshot["run_id"]
        self.snapshot_version = snapshot["snapshot_version"]
        self._snapshot = {
            **snapshot,
            "attributes": dict(snapshot["attributes"]),
            "sequences": dict(snapshot["sequences"]),
        }
        self.attributes = attributes
        self.condition = condition
        self.sequences = dict(snapshot["sequences"])
        return {"ready": True, "duplicate": False}

    def _on_transition(self, approved):
        event = self.current_event
        sequence = self.condition_sequence + 1
        notification = {
            "schema_version": 1,
            "event_id": f"{self.run_id}:cn1:{sequence}",
            "run_id": self.run_id, "source": "logic-engine",
            "entity_id": "cn1", "sequence": sequence,
            "approved": approved, "caused_by": event["event_id"],
            "emitted_at": utc_now(),
        }
        if "step" in event:
            notification["step"] = event["step"]
        self.send_condition(notification)
        self.condition_sequence = sequence
        self.condition_events.append(notification)

    def receive(self, event):
        validate_attribute_event(event)
        if not self.ready:
            raise ContractError("logic-engine sem snapshot ou em falha", status=409)
        if event["run_id"] != self.run_id:
            raise ContractError("run_id divergente", status=409)
        event_id = event["event_id"]
        if event_id in self.ledger:
            if event != self.ledger[event_id]:
                raise ContractError("event_id reutilizado com payload diferente", status=409)
            return {"accepted": True, "duplicate": True}
        name = event["entity_id"]
        if event["sequence"] != self.sequences[name] + 1:
            raise ContractError("evento atrasado ou lacuna de sequence", status=409)
        if event["value"] == self.attributes[name].value:
            raise ContractError("notificacao sem alteracao real", status=409)

        self.current_event = event
        try:
            # Atualização real da cadeia PON; pode emitir ConditionChanged.
            self.attributes[name].value = event["value"]
        except Exception:
            # Não presumir rollback após falha parcial no downstream.
            self.faulted = True
            raise
        finally:
            self.current_event = None

        self.sequences[name] = event["sequence"]
        self.ledger[event_id] = dict(event)
        return {"accepted": True, "duplicate": False}

    def state(self):
        return {
            "ready": self.ready, "faulted": self.faulted,
            "run_id": self.run_id, "snapshot_version": self.snapshot_version,
            "attributes": ({name: at.value for name, at in self.attributes.items()}
                           if self.attributes is not None else None),
            "sequences": dict(self.sequences),
            "condition": self.condition.approved() if self.condition else None,
            "condition_sequence": self.condition_sequence,
            "received_ids": list(self.ledger),
            "condition_events": list(self.condition_events),
        }


class RuleExecutor:
    """Estado da regra remota; efeito gerado pela cadeia PON em memória."""

    def __init__(self):
        self.run_id = None
        self.snapshot_version = None
        self._snapshot = None
        self.condition_sequence = 0
        self.ledger = {}
        self.effects = []
        self.current_event = None
        self.signal = None
        self.condition = None
        self.rule = None
        self.faulted = False

    @property
    def ready(self):
        return self.run_id is not None and not self.faulted

    def initialize(self, snapshot):
        validate_executor_snapshot(snapshot)
        if self.run_id is not None:
            if snapshot == self._snapshot:
                return {"ready": self.ready, "duplicate": True}
            raise ContractError("snapshot diferente apos inicializacao", status=409)
        if snapshot["condition_sequence"] != 0:
            raise ContractError("C1 inicial requer sequencia de condicao zero", status=409)
        signal = Attribute(snapshot["approved"])
        premise = signal == True
        condition = Condition(lambda: premise.approved(), [premise])
        rule = Rule(condition, Action([Instigation([self._effect])]))
        self.run_id = snapshot["run_id"]
        self.snapshot_version = snapshot["snapshot_version"]
        self._snapshot = dict(snapshot)
        self.condition_sequence = 0
        self.signal = signal
        self.condition = condition
        self.rule = rule
        return {"ready": True, "duplicate": False}

    def _effect(self):
        event = self.current_event
        self.effects.append({
            "schema_version": 1, "run_id": self.run_id,
            "event_id": f"{self.run_id}:rl1:{len(self.effects) + 1}",
            "entity_id": "rl1", "step": event.get("step"),
            "caused_by": event["event_id"],
            "attribute_event_id": event["caused_by"], "effect": "executed",
        })

    def receive(self, event):
        validate_condition_event(event)
        if not self.ready:
            raise ContractError("rule-executor sem snapshot ou em falha", status=409)
        if event["run_id"] != self.run_id:
            raise ContractError("run_id divergente", status=409)
        event_id = event["event_id"]
        if event_id in self.ledger:
            if event != self.ledger[event_id]:
                raise ContractError("event_id reutilizado com payload diferente", status=409)
            return {"accepted": True, "duplicate": True}
        if event["sequence"] != self.condition_sequence + 1:
            raise ContractError("evento atrasado ou lacuna de sequence", status=409)
        if event["approved"] == self.signal.value:
            raise ContractError("condicao nao apresentou transicao", status=409)
        self.current_event = event
        try:
            # Attribute -> Premise -> Condition -> Rule -> Action -> Instigation.
            self.signal.value = event["approved"]
        except Exception:
            self.faulted = True
            raise
        finally:
            self.current_event = None
        self.condition_sequence = event["sequence"]
        self.ledger[event_id] = dict(event)
        return {"accepted": True, "duplicate": False}

    def state(self):
        return {
            "ready": self.ready, "faulted": self.faulted,
            "run_id": self.run_id, "snapshot_version": self.snapshot_version,
            "condition_sequence": self.condition_sequence,
            "approved": self.signal.value if self.signal else None,
            "received_ids": list(self.ledger), "effects": list(self.effects),
        }
