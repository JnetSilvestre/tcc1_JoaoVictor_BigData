"""Gera tabelas e figura da E11-M01 a partir do pacote auditado."""
import argparse
from collections import defaultdict
import csv
from hashlib import sha256
from io import StringIO
from itertools import combinations
from math import ceil
from pathlib import Path
from statistics import median, quantiles
from zipfile import ZipFile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SCENARIOS = ("C2", "C3", "C4")
BLOCKS = tuple(f"B{i:02d}" for i in range(1, 11))


def read_package(path):
    with ZipFile(path) as archive:
        names = ("inventario.json", "rodadas.csv", "requisicoes.csv")
        expected = "".join(f"{sha256(archive.read(n)).hexdigest()}  {n}\n" for n in names)
        if sorted(archive.read("checksums.sha256").decode().splitlines()) != sorted(expected.splitlines()):
            raise ValueError("Checksums do pacote divergentes")
        return [list(csv.DictReader(StringIO(archive.read(n).decode()))) for n in names[1:]]


def summarize(numbers):
    first, _, third = quantiles(numbers, n=4, method="inclusive")
    return median(numbers), first, third, min(numbers), max(numbers)


def br(number, decimals=2):
    return f"{number:.{decimals}f}".replace(".", ",")


def interval(numbers):
    center, first, third, low, high = map(br, summarize(numbers))
    return f"{center} [{first}; {third}] ({low}--{high})"


def stacked_interval(numbers):
    center, first, third, low, high = map(br, summarize(numbers))
    return rf"\shortstack{{{center} [{first}; {third}] \\ ({low}--{high})}}"


def tex_rows(path, rows):
    body = "".join(" & ".join(map(str, row)) + r" \\" + "\n" for row in rows)
    path.write_text(body + "\\hline\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    runs, requests = read_package(args.package)
    samples = defaultdict(list)
    ids = set()
    for request in requests:
        duration = int(request["duration_ns"])
        if request["status"] != "200" or request["request_id"] in ids or duration <= 0:
            raise ValueError("Requisição inválida ou repetida")
        ids.add(request["request_id"])
        key = (request["run_id"], request["block"], request["scenario"], request["position"])
        samples[key].append((int(request["step"]), duration / 1e6))
    metrics = {}
    positions = defaultdict(dict)
    for run in runs:
        run_id, block, scenario = (run[k] for k in ("run_id", "block", "scenario"))
        elapsed = int(run["batch_elapsed_ns"]) / 1e9
        observations = samples.pop((run_id, block, scenario, run["position"]), [])
        rtt = sorted(value for _, value in observations)
        if (sorted(step for step, _ in observations) != list(range(1, 1001))
                or elapsed <= 0 or (block, scenario) in metrics):
            raise ValueError(f"Rodada inválida: {run_id}")
        metrics[block, scenario] = (
            elapsed, 1000 / elapsed, median(rtt), rtt[ceil(.95 * len(rtt)) - 1],
            rtt[ceil(.99 * len(rtt)) - 1], rtt[-1] - rtt[0],
        )
        positions[block][int(run["position"])] = scenario
    if samples or set(metrics) != {(b, s) for b in BLOCKS for s in SCENARIOS}:
        raise ValueError("Matriz incompleta")
    groups = {s: [metrics[b, s] for b in BLOCKS] for s in SCENARIOS}
    folder = args.root / "capitulos" / "dados-e11-m01"
    folder.mkdir(exist_ok=True)
    labels = ("Lote (s)", "Vazão (req/s)", "RTT mediano (ms)", "RTT p95 (ms)",
              "RTT p99 (ms)", "Amplitude do RTT (ms)")
    tex_rows(folder / "resumo.tex",
             [(label, *(stacked_interval([row[i] for row in groups[s]]) for s in SCENARIOS))
              for i, label in enumerate(labels)])
    with (args.root / "docs" / "tcc2" / "e11-m01-metricas-por-rodada.csv").open(
        "w", encoding="utf-8", newline=""
    ) as stream:
        table = csv.writer(stream, lineterminator="\n")
        table.writerow(("run_id", "block", "position", "scenario", "batch_s", "requests_s",
                        "rtt_median_ms", "rtt_p95_ms", "rtt_p99_ms", "rtt_range_ms"))
        for run in runs:
            values = metrics[run["block"], run["scenario"]]
            table.writerow([run[k] for k in ("run_id", "block", "position", "scenario")]
                           + [f"{value:.9f}" for value in values])
    pairs = list(combinations(SCENARIOS, 2))
    tex_rows(folder / "blocos.tex",
             [(b, "/".join(positions[b][i] for i in (1, 2, 3)),
               *(br(metrics[b, s][0]) for s in SCENARIOS),
               *(f"{br(metrics[b, y][0] - metrics[b, x][0])} / "
                 f"{br(metrics[b, y][0] / metrics[b, x][0], 3)}" for x, y in pairs))
              for b in BLOCKS])
    tex_rows(folder / "contrastes.tex",
             [(f"{y} vs. {x}",
               interval([metrics[b, y][0] - metrics[b, x][0] for b in BLOCKS]),
               interval([metrics[b, y][0] / metrics[b, x][0] for b in BLOCKS]))
              for x, y in pairs])
    fig, ax = plt.subplots(figsize=(7, 3.2), layout="constrained")
    for scenario, color, marker in zip(SCENARIOS, ("#235789", "#ac4619", "#207259"), "os^"):
        ax.plot(BLOCKS, [row[0] for row in groups[scenario]], label=scenario,
                color=color, marker=marker)
    ax.set(xlabel="Bloco", ylabel="Tempo de lote (s)")
    ax.legend(ncols=3)
    ax.grid(axis="y", alpha=.25)
    fig.savefig(args.root / "figuras" / "e11-m01-tempos-por-bloco.pdf",
                metadata={"CreationDate": None, "ModDate": None})
    fig, axes = plt.subplots(1, 2, figsize=(7, 3.2), layout="constrained", sharey=True)
    for ax, index, title in zip(axes, (3, 4), ("p95", "p99"), strict=True):
        for scenario, color, marker in zip(SCENARIOS, ("#235789", "#ac4619", "#207259"), "os^"):
            ax.plot(BLOCKS, [row[index] for row in groups[scenario]], color=color,
                    marker=marker, label=scenario)
        ax.set(xlabel="Bloco", title=title)
        ax.tick_params(axis="x", labelrotation=55)
        ax.grid(axis="y", alpha=.25)
    axes[0].set_ylabel("RTT (ms)")
    axes[1].legend()
    fig.savefig(args.root / "figuras" / "e11-m01-cauda-rtt.pdf",
                metadata={"CreationDate": None, "ModDate": None})


if __name__ == "__main__":
    main()
