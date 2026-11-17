"""E11-M00C: portoes de capacidade e quotas efetivas (somente leitura).

Nenhuma mutacao de estado de servico, POST, snapshot, stop ou delete.
O check de cgroup executa apenas leitura de arquivos V2 por python -c
DENTRO dos containers NOVOS da rodada, antes do primeiro snapshot.
"""
import json

# Limiares candidatos operacionais, conservadores e NAO calibrados
# cientificamente. Fixar antes das series definitivas.
MIN_WINDOWS_FREE_BYTES = 3 * 1024 ** 3
MIN_DISK_FREE_BYTES = 15 * 1024 ** 3
CPU_MILLICORES = 500
APP_MEMORY_BYTES = 256 * 1024 ** 2
CLIENT_MEMORY_BYTES = 128 * 1024 ** 2
ROLES = ("attribute-source", "logic-engine", "rule-executor", "client")

# Sem dependencias do pacote benchmark dentro da imagem aprovada.
CGROUP_READER = (
    "import json,pathlib\n"
    "p=pathlib.Path('/sys/fs/cgroup')\n"
    "def get(name):\n"
    " q=p/name\n"
    " return q.read_text(encoding='utf-8').strip() if q.is_file() else None\n"
    "print(json.dumps({'cpu_max':get('cpu.max'),"
    "'memory_max':get('memory.max'),"
    "'memory_current':get('memory.current'),"
    "'memory_swap_max':get('memory.swap.max'),"
    "'memory_events':get('memory.events')}))\n"
)


def assess_capacity(environment):
    """Um STOP de precaucao; nao e um indicador de desempenho experimental."""
    if environment.get("status") != "BASELINE_READ_ONLY_NOT_CAPACITY_APPROVAL":
        raise ValueError("environment.json ausente/incompativel")
    if environment.get("docker_cgroup_version") != "2":
        raise ValueError("somente cgroup v2 suportado")
    ram = environment.get("windows_host_ram_free_bytes")
    disk = environment.get("disk_free_bytes")
    if not isinstance(ram, int) or not isinstance(disk, int):
        raise ValueError("RAM livre Windows e disco sao obrigatorios")
    if ram < MIN_WINDOWS_FREE_BYTES:
        raise ValueError("STOP: RAM fisica livre Windows abaixo de 3 GiB")
    if disk < MIN_DISK_FREE_BYTES:
        raise ValueError("STOP: disco livre no diretorio do projeto abaixo de 15 GiB")
    return {
        "status": "CAPACITY_SAFETY_GATE_PASS_NOT_PERFORMANCE_APPROVAL",
        "windows_free_bytes": ram, "disk_free_bytes": disk,
        "min_windows_free_bytes": MIN_WINDOWS_FREE_BYTES,
        "min_disk_free_bytes": MIN_DISK_FREE_BYTES,
        "scientific_note": "limiares de precaucao operacional, NAO validade estatistica",
    }


def _event_counts(raw):
    out = {}
    if not isinstance(raw, str):
        raise ValueError("memory.events cgroup v2 ausente")
    for line in raw.splitlines():
        pair = line.strip().split()
        if len(pair) != 2 or not pair[1].isdigit():
            raise ValueError("memory.events invalido")
        out[pair[0]] = int(pair[1])
    return out


def validate_cgroup_v2(sample, role):
    """Exige CPU 500m e memoria 256/128 MiB no cgroup, nao so no manifesto."""
    if role not in ROLES or not isinstance(sample, dict):
        raise ValueError("role/amostra cgroup invalidos")
    cpu = sample.get("cpu_max")
    if not isinstance(cpu, str) or len(cpu.split()) != 2:
        raise ValueError(f"{role}: cpu.max ausente")
    quota, period = cpu.split()
    if not quota.isdigit() or not period.isdigit() or int(period) == 0:
        raise ValueError(f"{role}: CPU quota desconhecida/ilimitada")
    if int(quota) * 1000 != CPU_MILLICORES * int(period):
        raise ValueError(f"{role}: CPU quota efetiva diferente de 500m")
    memory = sample.get("memory_max")
    required = CLIENT_MEMORY_BYTES if role == "client" else APP_MEMORY_BYTES
    if not isinstance(memory, str) or not memory.isdigit() or int(memory) != required:
        raise ValueError(f"{role}: memoria efetiva diferente do limite nominal")
    used = sample.get("memory_current")
    if not isinstance(used, str) or not used.isdigit() or int(used) > required:
        raise ValueError(f"{role}: memory.current invalido")
    events = _event_counts(sample.get("memory_events"))
    if events.get("oom", 0) or events.get("oom_kill", 0):
        raise ValueError(f"{role}: OOM previo no cgroup de bancada nova")
    return {
        "role": role, "cpu_max": cpu, "memory_max_bytes": required,
        "memory_current_bytes": int(used),
        "memory_swap_max": sample.get("memory_swap_max"),
        "memory_events": events,
        "status": "EFFECTIVE_CGROUP_LIMITS_PASS_NOT_USAGE_COMPARISON",
    }


def capture_effective_quotas(scenario, *, names=None, pods=None,
                             namespace=None, query=None):
    """Somente NOVAS identidades previamente conferidas pelo preflight.

    query eh uma funcao com argv Docker/Kubectl; nao contem comandos mutantes.
    """
    if scenario not in ("C2", "C3", "C4") or query is None:
        raise ValueError("cenario/leitor ausentes")
    targets = {}
    if scenario == "C2":
        if not isinstance(names, dict) or set(names) != {"attribute-source", "logic-engine", "rule-executor", "client"}:
            raise ValueError("lista de containers incompleta")
        for role in ROLES:
            expected_prefix = "tcc2-pon-e11-c2-m"
            name = names[role]
            if not isinstance(name, str) or not name.startswith(expected_prefix):
                raise ValueError("container historico ou fora de escopo")
            targets[role] = ("docker", "exec", name, "python", "-c", CGROUP_READER)
    else:
        if not isinstance(namespace, str) or not namespace.startswith(
                f"tcc2-pon-e11-{scenario.lower()}-m"):
            raise ValueError("namespace historico ou fora de escopo")
        if not isinstance(pods, dict) or set(pods) != set(ROLES):
            raise ValueError("Pods incompletos")
        for role in ROLES:
            name = pods[role]
            if not isinstance(name, str) or not name:
                raise ValueError("Pod sem nome")
            container = "e11-benchmark-client" if role == "client" else role
            targets[role] = (
                "kubectl", "--context", "kind-tcc2-pon", "-n", namespace,
                "exec", name, "-c", container, "--", "python", "-c", CGROUP_READER,
            )
    measured = {}
    for role, argv in targets.items():
        raw = query(*argv)
        measured[role] = validate_cgroup_v2(json.loads(raw), role)
    return {
        "status": "EFFECTIVE_LIMITS_ALL_FOUR_PASS",
        "scenario": scenario, "namespace": namespace,
        "roles": measured,
        "resource_sampling_during_batch": False,
        "resource_metrics_comparable": False,
        "note": "Somente cgroup v2 e pre-snapshot; captura nao e medicao CPU/RAM do lote",
    }
