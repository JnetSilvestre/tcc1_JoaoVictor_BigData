"""E11-M01: um unico comando para conduzir a campanha definitiva de 30 slots.

* Retoma B01/C2 ja executada sem qualquer novo snapshot ou POST.
* NUNCA repete RUN, snapshot ou lote se ha arquivos/journal anteriores.
* Audita ZIP/journal/backup e recursos novos imediatamente antes de RETIRE.
* A autorizacao para RETIRE eh diferente da autorizacao para RUN, por rodada.
* A cada STOP preserva evidencias, containers, redes e namespaces.
* A ordem B01-B10 vem SOMENTE de m01_readiness.full_schedule().
* Nao elimina nem reinicia recursos historicos.
"""
import argparse
import json
from pathlib import Path
import sys

from benchmark import m01_lifecycle as life
from benchmark.backup_integrity import compare_backup_pair
from benchmark.environment_snapshot import capture_environment
from benchmark.lifecycle_audit import audit_archive
from benchmark.m01_readiness import full_schedule


def require_archive_for_completed(slot, paths):
    """Checa integridade/backup/journal mesmo ao pular uma rodada concluida."""
    event = life.require_complete(
        paths["run_journal"], slot["run_id"], "COMPLETE",
        "M01_RUN_PASS_BACKED_UP",
    )
    audit = audit_archive(paths["primary"], slot["scenario"],
                          slot["label"], slot["run_id"])
    backup = compare_backup_pair(paths["primary"], paths["backup"])
    if (event.get("zip_sha256") != audit["zip_sha256"]
            or backup.get("zip_sha256") != audit["zip_sha256"]
            or backup.get("different_filesystem_volume") is not True):
        raise ValueError("STOP: rodada anterior sem evidencia íntegra")
    return audit["zip_sha256"]


def require_retirement_complete(slot, paths, expected_sha):
    event = life.require_complete(
        paths["retire_journal"], slot["run_id"], "COMPLETE",
        "M01_RETIREMENT_COMPLETE",
    )
    if event.get("zip_sha256") != expected_sha:
        raise ValueError("STOP: retirada nao confere com ZIP preservado")
    return True


def authorize(phase, slot):
    """Consentimento humano por fase E por identidade. Nao infere de RUN PASS."""
    phrase = life.approval_phrase(phase, slot)
    print(f"\nALVO: {slot['run_id']} | {slot['scenario']} | {phase}", flush=True)
    print("Continuar apenas se esta operacao especifica estiver autorizada.",
          flush=True)
    answer = input(f"Digite exatamente {phrase} para permitir; outra resposta cancela: ").strip()
    if answer != phrase:
        raise ValueError("STOP: autorizacao especifica recusada")
    return answer


def assert_review_pass(slot, paths):
    packet = life.review_retirement(slot, paths, life.query_command)
    if (packet.get("status") != "M01_RETIREMENT_REVIEW_ONLY_PASS"
            or packet.get("run_id") != slot["run_id"]
            or packet.get("scenario") != slot["scenario"]
            or packet.get("delete_authorized") is not False
            or packet.get("commands") != []):
        raise ValueError("STOP: auditoria de propriedade nao passou")
    print("REVIEW_READONLY_PASS", slot["run_id"],
          "ZIP_SHA256", packet["zip_sha256"], flush=True)
    return packet


def process_slot(slot, position, home, backup_root, fixture, approved_head):
    paths = life.paths_for(slot, home, backup_root)
    print(f"\n=== {position:02d}/30 {slot['block']}/{slot['scenario']} "
          f"{slot['run_id']} ===", flush=True)

    retired = paths["retire_journal"].exists()
    ran = paths["run_journal"].exists()

    if retired and not ran:
        raise ValueError("STOP: retirada presente sem diario da rodada")

    if retired:
        digest = require_archive_for_completed(slot, paths)
        require_retirement_complete(slot, paths, digest)
        print("JA CONCLUIDA: RUN + RETIRE; nenhuma repeticao.", flush=True)
        return "SKIPPED_COMPLETED"

    if ran:
        # Retomada sem repetir snapshot/POST, mesmo que o RUN tenha ocorrido
        # em outra sessao ou o journal esteja interrompido.
        digest = require_archive_for_completed(slot, paths)
        print("RUN JA EXISTE: nao executar novamente.", flush=True)
    else:
        plan = life.run_sequence_preflight(
            position, home, backup_root, fixture,
            life.query_command, capture_environment,
        )
        if (plan.get("status") != "M01_SLOT_PLAN_ONLY"
                or plan.get("slot", {}).get("run_id") != slot["run_id"]
                or plan.get("start_authorized") is not False
                or plan.get("commands") != []):
            raise ValueError("STOP: preflight nao autorizado")
        # O RUN real refaz todos os gates imediatamente antes da criacao.
        permission = authorize("RUN", slot)
        result = life.execute_run(
            position, home, backup_root, fixture, approved_head, permission,
            life.query_command, capture_environment, life.execute_action,
        )
        if (result.get("status") != "M01_RUN_PASS_BACKED_UP"
                or result.get("retirement_authorized") is not False):
            raise ValueError("STOP: RUN nao concluiu com ZIP+backup PASS")
        digest = require_archive_for_completed(slot, paths)
        print("RUN_PASS_BACKED_UP", slot["run_id"], digest, flush=True)

    # Somente se o ZIP/backup e journals passaram, inspecionar os novos
    # recursos vivos. Nao autoriza exclusao implicitamente.
    packet = assert_review_pass(slot, paths)
    if packet["zip_sha256"] != digest:
        raise ValueError("STOP: review ZIP divergente do journal")

    permission = authorize("RETIRE", slot)
    retired_report = life.execute_retirement(
        position, home, backup_root, approved_head,
        permission, life.query_command, life.execute_action,
    )
    if (retired_report.get("status") != "M01_RETIREMENT_COMPLETE"
            or retired_report.get("zip_and_backup_preserved") is not True):
        raise ValueError("STOP: retirada nao comprovada")

    require_retirement_complete(slot, paths, digest)
    # Mais uma leitura apos o DELETE; nao modifica ZIP nem backup.
    preserved = require_archive_for_completed(slot, paths)
    if preserved != digest:
        raise ValueError("STOP: evidencia mudou apos retirada")
    print("RETIREMENT_COMPLETE", slot["run_id"], flush=True)
    return "COMPLETED"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--approved-head", required=True)
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--backup-root", type=Path,
                        default=Path("D:/TCC2-Backup"))
    parser.add_argument("--until-position", type=int, default=30,
                        help="Ultima posicao a executar, 1..30. Padrao: 30.")
    args = parser.parse_args(argv)
    if not 1 <= args.until_position <= 30:
        parser.error("--until-position deve ser de 1 a 30")

    # Gates preliminares: SHA/branch/working tree, schedule imutavel, release
    # formal de cada operacao e artefatos existentes.
    life.verify_clean_git(life.query_command, args.approved_head)
    schedule = full_schedule()
    if len(schedule) != 30:
        raise ValueError("STOP: matriz experimental invalida")
    for position in range(1, args.until_position + 1):
        life.require_stage_release("RUN", position)
        life.require_stage_release("RETIRE", position)

    print("E11-M01: EXECUCAO SEQUENCIAL COM CONSENTIMENTO POR FASE")
    print("B01/C2 ja foi executada: se journal PASS existe, NAO repetira os POSTs.")
    print("Nenhuma limpeza generica ou retry de rodada e permitido.")
    print("Em qualquer STOP: preservar estado e nao relancar automaticamente.",
          flush=True)

    counts = {"SKIPPED_COMPLETED": 0, "COMPLETED": 0}
    for i, slot in enumerate(schedule[:args.until_position], start=1):
        outcome = process_slot(slot, i, args.home, args.backup_root,
                               args.fixture, args.approved_head)
        counts[outcome] += 1

    print(json.dumps({
        "status": "M01_CAMPAIGN_SEGMENT_COMPLETE",
        "last_position": args.until_position,
        "already_complete": counts["SKIPPED_COMPLETED"],
        "completed_this_session": counts["COMPLETED"],
        "all_30_completed": args.until_position == 30,
        "scientific_results_are_in_zip_files": True,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (Exception, KeyboardInterrupt) as exc:
        print(f"\nSTOP: {type(exc).__name__}: {exc}", file=sys.stderr,
              flush=True)
        print("NAO REPETIR AUTOMATICAMENTE. Preservar ZIPs, journals e recursos.",
              file=sys.stderr, flush=True)
        sys.exit(2)
