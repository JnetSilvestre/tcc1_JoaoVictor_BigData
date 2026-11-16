"""E11-M00B: checagem ESTATICA de requests/limits de Pods kind.

Verificar contratos declarados nao prova equivalencia de consumo fisico,
governanca de cgroup, throttling ou ausencia de interferencia do host.
Nenhuma chamada a kubectl, Docker ou recursos externos.
"""
ROLES = ("attribute-source", "logic-engine", "rule-executor")

APP_REQUESTS = {"cpu": "100m", "memory": "128Mi"}
APP_LIMITS = {"cpu": "500m", "memory": "256Mi"}
CLIENT_REQUESTS = {"cpu": "100m", "memory": "64Mi"}
CLIENT_LIMITS = {"cpu": "500m", "memory": "128Mi"}


def assert_container_resources(container, requests, limits, role):
    resources = container.get("resources") or {}
    if resources.get("requests") != requests or resources.get("limits") != limits:
        raise ValueError(f"{role}: requests/limits divergentes dos manifestos aprovados")
    return {
        "requests": dict(requests),
        "limits": dict(limits),
        "resource_semantics": "quotas declaradas, NAO observacao de consumo real",
    }


def verify_kube_resources(topology, client_pod):
    """Verifica os 3 Pods + Deployments e o Pod cliente, de forma fail-closed."""
    pods = (topology.get("pods_full") or {}).get("items") or []
    deployments = (topology.get("deployments_full") or {}).get("items") or []
    roles = {}
    for role in ROLES:
        matches = [p for p in pods if (p.get("metadata", {}).get("labels") or {}).get("app") == role]
        deploy = [d for d in deployments if d.get("metadata", {}).get("name") == role]
        if len(matches) != 1 or len(deploy) != 1:
            raise ValueError(f"{role}: quantidade inesperada de Pods/Deployments")
        pcontainers = matches[0].get("spec", {}).get("containers") or []
        dcontainers = (deploy[0].get("spec", {}).get("template", {}).get("spec", {}).get("containers") or [])
        if len(pcontainers) != 1 or len(dcontainers) != 1:
            raise ValueError(f"{role}: quantidade inesperada de containers")
        roles[role] = assert_container_resources(pcontainers[0], APP_REQUESTS, APP_LIMITS, role)
        assert_container_resources(dcontainers[0], APP_REQUESTS, APP_LIMITS, role + "/deployment")
    clients = client_pod.get("spec", {}).get("containers") or []
    if len(clients) != 1:
        raise ValueError("cliente: quantidade inesperada de containers")
    client = assert_container_resources(clients[0], CLIENT_REQUESTS, CLIENT_LIMITS, "client")
    return {
        "status": "DECLARED_LIMITS_MATCH",
        "services": roles,
        "client": client,
        "physical_cpu_memory_equivalence": False,
    }
