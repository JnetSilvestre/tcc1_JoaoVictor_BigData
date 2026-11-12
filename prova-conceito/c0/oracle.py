"""Oráculo independente: apenas estado, comparações e transições Python.

Este módulo NÃO importa o pacote PON e não reproduz suas classes.
É a referência independente contra a qual a cadeia PON é comparada.
"""


def calculate_expected_effects(rows):
    values = {"atA": 0, "atB": 0}
    attribute_sequences = {"atA": 0, "atB": 0}
    previous = False
    condition_sequence = 0
    effect_sequence = 0
    effects = []

    for row in rows:
        name = row["entity_id"]
        value = row["value"]
        if values[name] == value:
            continue

        values[name] = value
        attribute_sequences[name] += 1
        attr_id = f'{row["run_id"]}:{name}:{attribute_sequences[name]}'
        approved = values["atA"] >= 5 and values["atB"] == 1

        if approved != previous:
            condition_sequence += 1
            if approved:
                effect_sequence += 1
                effects.append({
                    "schema_version": 1,
                    "run_id": row["run_id"],
                    "event_id": f'{row["run_id"]}:rl1:{effect_sequence}',
                    "entity_id": "rl1",
                    "step": row["step"],
                    "caused_by": f'{row["run_id"]}:cn1:{condition_sequence}',
                    "attribute_event_id": attr_id,
                    "effect": "executed",
                })
            previous = approved

    return effects
