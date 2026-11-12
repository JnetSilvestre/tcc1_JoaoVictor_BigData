"""Execução local da cadeia PON, com eventos estruturados determinísticos."""

from pon import Action, Attribute, Instigation, Rule


class ConditionObserver:
    def __init__(self, condition, on_transition):
        self.condition = condition
        self.on_transition = on_transition

    def update(self, notifier_id):
        self.on_transition(self.condition.approved())


def execute_pon(rows):
    run_id = rows[0]["run_id"]
    attributes = {"atA": Attribute(0), "atB": Attribute(0)}
    condition = (attributes["atA"] >= 5) & (attributes["atB"] == 1)
    attribute_sequences = {"atA": 0, "atB": 0}
    context = {"step": None, "attribute_event_id": None, "condition_event_id": None}
    trace = []
    effects = []
    condition_sequence = [0]
    effect_sequence = [0]

    def on_transition(approved):
        condition_sequence[0] += 1
        event_id = f"{run_id}:cn1:{condition_sequence[0]}"
        context["condition_event_id"] = event_id
        trace.append({
            "event_type": "condition_changed",
            "run_id": run_id,
            "event_id": event_id,
            "entity_id": "cn1",
            "step": context["step"],
            "approved": approved,
            "caused_by": context["attribute_event_id"],
        })

    # Registrar primeiro o observador garante que o ID da transição exista
    # quando o Rule disparar a Action logo depois, de forma síncrona.
    condition.register(ConditionObserver(condition, on_transition))

    def on_action():
        effect_sequence[0] += 1
        effect = {
            "schema_version": 1,
            "run_id": run_id,
            "event_id": f"{run_id}:rl1:{effect_sequence[0]}",
            "entity_id": "rl1",
            "step": context["step"],
            "caused_by": context["condition_event_id"],
            "attribute_event_id": context["attribute_event_id"],
            "effect": "executed",
        }
        effects.append(effect)
        trace.append({"event_type": "rule_effect", **effect})

    rule = Rule(condition, Action([Instigation([on_action])]))

    for row in rows:
        name = row["entity_id"]
        changed = attributes[name].value != row["value"]
        context["step"] = row["step"]
        trace.append({
            "event_type": "request",
            "run_id": run_id,
            "request_id": row["request_id"],
            "step": row["step"],
            "entity_id": name,
            "value": row["value"],
            "changed": changed,
        })
        if not changed:
            continue

        attribute_sequences[name] += 1
        event_id = f"{run_id}:{name}:{attribute_sequences[name]}"
        context["attribute_event_id"] = event_id
        context["condition_event_id"] = None
        trace.append({
            "event_type": "attribute_changed",
            "run_id": run_id,
            "event_id": event_id,
            "entity_id": name,
            "step": row["step"],
            "value": row["value"],
        })
        # Setter notifica Premise, depois Condition e Rule; é a cadeia PON real.
        attributes[name].value = row["value"]

    assert rule is not None
    return {
        "effects": effects,
        "trace": trace,
        "final_state": {
            "atA": attributes["atA"].value,
            "atB": attributes["atB"].value,
            "condition": condition.approved(),
        },
        "attribute_sequences": attribute_sequences,
        "condition_sequence": condition_sequence[0],
    }
