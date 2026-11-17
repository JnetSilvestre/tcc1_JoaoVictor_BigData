"""E11-M00C: somente UMA bancada NOVA ativa por vez, consultas read-only.

Bancadas historicas (p..., v03/v05/v06/c2 e namespaces antigos)
nao sao consideradas para limpeza ou alteracao: sao preservadas.
"""
import json
import re

NEW_DOCKER = re.compile(r"^tcc2-pon-e11-c2-m[a-z0-9-]+-(?:attribute-source|logic-engine|rule-executor|benchmark-client)$")
NEW_KUBE = re.compile(r"^tcc2-pon-e11-c[34]-m[a-z0-9-]+$")


def check_exclusivity(scenario, target, active_docker_names, kube_names):
    if scenario not in ("C2", "C3", "C4") or not isinstance(target, str):
        raise ValueError("cenario/target invalidos")
    new_docker = sorted(x for x in active_docker_names if NEW_DOCKER.fullmatch(x))
    new_kube = sorted(x for x in kube_names if NEW_KUBE.fullmatch(x))
    if scenario == "C2":
        if not target.startswith("tcc2-pon-e11-c2-m"):
            raise ValueError("target Docker fora de M01")
        if new_docker or new_kube:
            raise ValueError("STOP: outra bancada M01 ativa/presente")
    else:
        if not target.startswith(f"tcc2-pon-e11-{scenario.lower()}-m"):
            raise ValueError("target namespace fora de M01")
        if new_docker or any(x != target for x in new_kube):
            raise ValueError("STOP: outra bancada M01 ativa/presente")
        if target not in new_kube:
            raise ValueError("namespace novo esperado ausente")
    return {
        "status": "ONE_NEW_CAMPAIGN_BENCH_ONLY",
        "scenario": scenario, "target": target,
        "active_new_docker": new_docker, "new_kube_namespaces": new_kube,
        "historic_resources_mutated": False,
    }


def check_exclusivity_readonly(scenario, target, reader):
    docker_names = reader("docker", "ps", "--format", "{{.Names}}").splitlines()
    namespaces = json.loads(reader(
        "kubectl", "--context", "kind-tcc2-pon", "get", "namespaces", "-o", "json"))
    names = [x["metadata"]["name"] for x in namespaces["items"]]
    return check_exclusivity(scenario, target, docker_names, names)
