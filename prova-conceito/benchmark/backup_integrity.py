"""E11-M00: verificar copia de ZIP sem criar, alterar ou apagar arquivos.

O operador realiza eventual copia por fluxo separado e auditavel.
Copia em volume distinto e uma evidência de separacao de volume, nao
prova de dispositivo fisico independente nem permissao para cleanup.
"""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as src:
        for piece in iter(lambda: src.read(1024 * 1024), b""):
            h.update(piece)
    return h.hexdigest()


def verify_zip_bytes(path):
    """Verifica CRC e checksums internos sem exigir PASS funcional (retém FAIL)."""
    path = Path(path)
    if not path.is_file() or path.is_symlink():
        raise ValueError("ZIP ausente, nao regular ou symlink")
    with ZipFile(path, "r") as zf:
        members = zf.namelist()
        if len(members) != len(set(members)) or not members:
            raise ValueError("ZIP com membros duplicados ou vazio")
        if zf.testzip() is not None:
            raise ValueError("CRC de ZIP invalido")
        if "checksums.sha256" not in members:
            raise ValueError("checksums.sha256 ausente")
        expected = {}
        for row in zf.read("checksums.sha256").decode("utf-8").splitlines():
            if "  " not in row:
                raise ValueError("linha de checksum invalida")
            digest, name = row.split("  ", 1)
            if (len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest)
                    or name in expected or name == "checksums.sha256"
                    or name not in members or "/" in name or "\\" in name):
                raise ValueError("checksum com nome/digest invalido")
            expected[name] = digest
        if set(expected) != set(members) - {"checksums.sha256"}:
            raise ValueError("checksum nao cobre todos os membros")
        for name, digest in expected.items():
            if hashlib.sha256(zf.read(name)).hexdigest() != digest:
                raise ValueError(f"SHA-256 interno divergente: {name}")
    return {"status": "ZIP_CRC_SHA256_VERIFIED", "members": len(members)}


def compare_backup_pair(primary_path, backup_path):
    """Duas COPIAS fisicamente distintas por caminho, sem escrita/delecao."""
    primary, backup = Path(primary_path), Path(backup_path)
    if not primary.is_file() or not backup.is_file():
        raise ValueError("ZIP principal ou copia ausente")
    if primary.is_symlink() or backup.is_symlink() or primary.samefile(backup):
        raise ValueError("copia aponta para o mesmo arquivo")
    if primary.resolve().parent == backup.resolve().parent:
        raise ValueError("backup no mesmo diretorio do arquivo principal")
    first = verify_zip_bytes(primary)
    second = verify_zip_bytes(backup)
    if first != second or primary.stat().st_size != backup.stat().st_size:
        raise ValueError("ZIPs com estrutura/tamanho diferentes")
    main_sha = sha256_file(primary)
    if main_sha != sha256_file(backup):
        raise ValueError("ZIPs nao sao identicos byte a byte")
    # No Windows e em outros SOs, st_dev identifica o volume filesystem,
    # nao necessariamente discos fisicos independentes.
    other_volume = primary.stat().st_dev != backup.stat().st_dev
    return {
        "status": "BACKUP_BYTES_VERIFIED_NO_CLEANUP_AUTHORIZATION",
        "zip_sha256": main_sha,
        "zip_bytes": primary.stat().st_size,
        "members": first["members"],
        "different_filesystem_volume": other_volume,
        "independent_physical_device_verified": False,
        "delete_authorized": False,
        "commands": [],
        "note": "Copia identica em caminho distinto; volumes diferentes nao comprovam discos fisicos independentes",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--backup", type=Path, required=True)
    args = parser.parse_args(argv)
    print(json.dumps(compare_backup_pair(args.primary, args.backup),
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
