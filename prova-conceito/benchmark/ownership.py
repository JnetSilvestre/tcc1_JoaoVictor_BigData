"""E11-M00: registro de propriedade de bancada M01, somente consultas read-only.

NENHUM stop, rm, delete, apply ou comando que altere estado.
Exige labels de campanha, run_id e IDs imutaveis dos recursos NOVOS.
"""
import json
import re

ROLES = ("attribute-source", "logic-engine", "rule-executor", "client")
CAMPAIGN_LABEL = "tcc2.e11/campaign"
RUN_LABEL = "tcc2.e11/run-id"
IMAGE_ID = "sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a"
HEX_ID = re.compile(r"^[a-f0-9]{12,64}$")


def exact_identity(scenario, label, run_id):
    if scenario not in ("C2", "C3", "C4"):
        raise ValueError("cenario nao permitido")
    if not isinstance(label, str) or not re.fullmatch(r"m[a-z0-9][a-z0-9-]{1,20}", label):
        raise ValueError("label M01 invalido")
    if run_id != f"e11-{scenario.lower()}-{label}":
        raise ValueError("run_id nao corresponde a campanha")
    return f"tcc2-pon-e11-{scenario.lower()}-{label}"


def check_labels(labels, run_id):
    if not isinstance(labels, dict) or labels.get(CAMPAIGN_LABEL) != "m01":
        raise ValueError("recurso sem label M01")
    if labels.get(RUN_LABEL) != run_id:
        raise ValueError("recurso sem label exata da rodada")


def _exact_id(value):
    return isinstance(value, str) and HEX_ID.fullmatch(value) is not None


def capture_docker_ownership(label, run_id, query):
    """Inspeciona apenas rede e 4 conteineres com NOMES derivados da rodada."""
    base = exact_identity("C2", label, run_id)
    net = json.loads(query("docker", "network", "inspect", base))
    if not isinstance(net, list) or len(net) != 1 or net[0].get("Name") != base:
        raise ValueError("rede Docker inesperada")
    network = net[0]
    check_labels(network.get("Labels"), run_id)
    net_id = network.get("Id")
    if not _exact_id(net_id):
        raise ValueError("network ID ausente/invalido")
    containers = {}
    for role in ROLES:
        name = base + ("-benchmark-client" if role == "client" else "-" + role)
        data = json.loads(query("docker", "inspect", name))
        if not isinstance(data, list) or len(data) != 1:
            raise ValueError("inspect Docker incompleto")
        entry = data[0]
        config = entry.get("Config") or {}
        check_labels(config.get("Labels"), run_id)
        conn = (entry.get("NetworkSettings") or {}).get("Networks") or {}
        attached = conn.get(base) or {}
        if (entry.get("Name", "").lstrip("/") != name
                or not _exact_id(entry.get("Id"))
                or entry.get("Image") != IMAGE_ID
                or entry.get("State", {}).get("Running") is not True
                or attached.get("NetworkID") != net_id):
            raise ValueError(f"{role}: identidade/imagem/rede inesperada")
        containers[role] = {"name": name, "id": entry["Id"], "image_id": entry["Image"]}
    if len(set(x["id"] for x in containers.values())) != 4:
        raise ValueError("container IDs duplicados")
    return {
        "status": "NEW_BENCH_OWNERSHIP_READONLY_PASS",
        "scenario": "C2", "run_id": run_id, "namespace": None,
        "network": {"name": base, "id": net_id},
        "containers": containers,
        "delete_authorized": False, "commands": [],
    }


def capture_kind_ownership(scenario, label, run_id, query):
    """Le namespace e quatro Pods NOVOS; sem inspecionar/mutar historicos."""
    if scenario not in ("C3", "C4"):
        raise ValueError("somente C3/C4")
    namespace = exact_identity(scenario, label, run_id)
    prefix = ("kubectl", "--context", "kind-tcc2-pon")
    ns = json.loads(query(*prefix, "get", "namespace", namespace, "-o", "json"))
    md = ns.get("metadata") or {}
    if md.get("name") != namespace or not isinstance(md.get("uid"), str) or not md["uid"]:
        raise ValueError("namespace UID inesperado")
    check_labels(md.get("labels"), run_id)
    raw = json.loads(query(*prefix, "-n", namespace, "get", "pods", "-o", "json"))
    items = raw.get("items")
    if not isinstance(items, list) or len(items) != 4:
        raise ValueError("esperados exatamente 4 Pods novos")
    pods = {}
    for item in items:
        metadata = item.get("metadata") or {}
        labels = metadata.get("labels") or {}
        role = labels.get("app")
        if role == "e11-benchmark-client":
            role = "client"
        uid = metadata.get("uid")
        if (role not in ROLES or role in pods or metadata.get("namespace") != namespace
                or labels.get("app.kubernetes.io/part-of") != namespace
                or not isinstance(uid, str) or not uid):
            raise ValueError("Pod estranho ou fora do namespace da rodada")
        statuses = (item.get("status") or {}).get("containerStatuses") or []
        if (len(statuses) != 1
                or not statuses[0].get("containerID")
                or statuses[0].get("restartCount") != 0
                or item.get("status", {}).get("phase") != "Running"):
            raise ValueError("Pod sem container ID estavel")
        pods[role] = {
            "name": metadata["name"], "uid": uid,
            "container_id": statuses[0]["containerID"],
        }
    if set(pods) != set(ROLES) or len(set(p["uid"] for p in pods.values())) != 4:
        raise ValueError("Pods incompletos/UIDs duplicados")
    return {
        "status": "NEW_BENCH_OWNERSHIP_READONLY_PASS",
        "scenario": scenario, "run_id": run_id,
        "namespace": {"name": namespace, "uid": md["uid"]},
        "pods": pods, "delete_authorized": False, "commands": [],
    }
