"""Cria YAML de bancada E11 ISOLADA. NAO executa kubectl apply nem faz POST."""
import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
IMAGE = "tcc2-pon:c2-e08-dbefcd2cf3d2"


def namespace_for(scenario, label):
    if scenario not in ("C3", "C4"):
        raise ValueError("somente C3/C4")
    if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,20}[a-z0-9])?", label):
        raise ValueError("identificador curto DNS invalido")
    return f"tcc2-pon-e11-{scenario.lower()}-{label}"


def render(scenario, label):
    ns = namespace_for(scenario, label)
    old_ns = {"C3": "tcc2-pon", "C4": "tcc2-pon-c4"}[scenario]
    source = ROOT / "infraestrutura" / "kubernetes" / scenario.lower() / "manifests.yaml"
    text = source.read_text(encoding="utf-8")
    for field, old, new in (
        ("namespace", old_ns, ns),
        ("name", old_ns, ns),
        ("name", f"tcc2-pon-{scenario.lower()}-config", f"e11-{scenario.lower()}-config"),
        ("app.kubernetes.io/part-of", f"tcc2-pon-{scenario.lower()}", ns),
    ):
        pattern = rf"(?m)^(\s*{re.escape(field)}:\s*){re.escape(old)}(?=\s*$)"
        text, n = re.subn(pattern, lambda m: m.group(1) + new, text)
        if not n:
            raise ValueError(f"campo nao encontrado no manifesto: {field}={old}")
    if (f"namespace: {old_ns}\n" in text
            or f"  name: {old_ns}\n" in text
            or f"tcc2-pon-{scenario.lower()}-config" in text):
        raise ValueError("manifesto ainda referencia namespace/config original")
    # Positivacao de ownership SOMENTE na definicao do namespace M01 novo.
    # Nao altera os manifestos historicos nem o codigo dos servicos.
    if label.startswith("m"):
        before = f"kind: Namespace\\nmetadata:\\n  name: {ns}\\n  labels:\\n"
        after = (before + f"    tcc2.e11/campaign: m01\\n"
                 + f"    tcc2.e11/run-id: e11-{scenario.lower()}-{label}\\n")
        # Converter escapes de template em quebras reais apenas nesta rotina.
        before = before.replace("\\n", "\n")
        after = after.replace("\\n", "\n")
        if text.count(before) != 1:
            raise ValueError("Namespace M01 sem cabecalho unico para ownership")
        text = text.replace(before, after)

    # Um Pod de cliente sem o codigo da aplicacao mutado: mesma imagem, comando diferente.
    client = f"""
---
apiVersion: v1
kind: Pod
metadata:
  name: e11-benchmark-client
  namespace: {ns}
  labels:
    app: e11-benchmark-client
    app.kubernetes.io/part-of: {ns}
spec:
  restartPolicy: Never
  nodeSelector:
    kubernetes.io/hostname: tcc2-pon-worker
  containers:
    - name: e11-benchmark-client
      image: {IMAGE}
      imagePullPolicy: Never
      command: ["python", "-c", "import time; time.sleep(86400)"]
      resources:
        requests:
          cpu: 100m
          memory: 64Mi
        limits:
          cpu: 500m
          memory: 128Mi
"""
    return ns, "# E11 — gerado, nao aplicado. Usar somente namespace novo.\n" + text + client


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=["C3", "C4"], required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    ns, yaml_text = render(args.scenario, args.label)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.write_text(yaml_text, encoding="utf-8")
    print(f"MANIFESTO_PREPARADO: {args.output}")
    print(f"NAMESPACE_NOVO: {ns}")
    print("APLICADO: NAO; SNAPSHOT: NAO; BENCHMARK: NAO")


if __name__ == "__main__":
    main()
