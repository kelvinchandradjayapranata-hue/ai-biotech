#!/usr/bin/env python3
"""
test_afdb_download.py - Tahap 5: validasi hasil unduhan AlphaFold DB (read-only).

Memeriksa artefak Tahap 5:
  - results/dataset/dataset_download_manifest.csv
  - data/alphafold_db/metadata/download_checksums.csv
  - results/dataset/structure_validation.csv
  - results/dataset/pae_validation.csv
  - file mentah di data/alphafold_db/raw/ dan data/alphafold_db/metadata/api_*.json

Semua nilai kritis DIHITUNG ULANG dari file mentah (bukan sekadar membaca CSV).
Tidak mengakses jaringan. Tidak mengubah file apa pun.
Exit code 0 hanya jika SEMUA test PASS.

Checklist (sesuai permintaan Tahap 5):
  1. Tepat 7 protein, sesuai daftar kandidat yang disetujui.
  2. Accession unik.
  3. Setiap protein punya file CIF.
  4. Setiap protein punya file PAE JSON.
  5. Ukuran file > 0 dan cocok dengan catatan checksums.
  6. SHA256 valid (dihitung ulang) dan konsisten CSV <-> manifest.
  7. Panjang sekuens CIF cocok dengan metadata.
  8. Sequence match CIF vs sekuens resmi metadata API = PASS.
  9. Matrix PAE cocok dengan panjang sekuens (N x N).
 10. Source = AlphaFold DB.
 11. License metadata tersedia.
 12. Tidak ada file kandidat tambahan yang tidak disetujui.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

from Bio.PDB import MMCIFParser
from Bio.PDB.Polypeptide import protein_letters_3to1

PROJECT_ROOT = Path(__file__).resolve().parent.parent
META_DIR = PROJECT_ROOT / "data" / "alphafold_db" / "metadata"
RAW_DIR = PROJECT_ROOT / "data" / "alphafold_db" / "raw"
RESULTS_DIR = PROJECT_ROOT / "results" / "dataset"
CANDIDATES_PATH = META_DIR / "candidates.json"
CHECKSUMS_PATH = META_DIR / "download_checksums.csv"
DOWNLOAD_MANIFEST_PATH = RESULTS_DIR / "dataset_download_manifest.csv"
STRUCT_VAL_PATH = RESULTS_DIR / "structure_validation.csv"
PAE_VAL_PATH = RESULTS_DIR / "pae_validation.csv"

HEX64 = re.compile(r"^[0-9a-f]{64}$")
RAW_SUFFIXES = {".cif", ".mmcif", ".pdb", ".json"}

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, bool(ok), detail))
    status = "PASS" if ok else "FAIL"
    line = f"[{status}] {name}"
    if detail and not ok:
        line += f"  -> {detail}"
    print(line)


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def sha256_of_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cif_sequence(path: Path) -> tuple[str, int, int, str]:
    """Hitung ulang: (sequence, model_count, chain_count, chain_ids). Independen dari validate script."""
    structure = MMCIFParser(QUIET=True).get_structure("model", str(path))
    models = list(structure.get_models())
    if len(models) != 1:
        raise ValueError(f"jumlah model = {len(models)}")
    parts: list[str] = []
    chain_ids: list[str] = []
    for chain in models[0].get_chains():
        chain_ids.append(chain.id)
        for res in chain.get_residues():
            if res.id[0] != " ":
                continue
            aa1 = protein_letters_3to1.get(res.resname.strip().upper())
            parts.append(aa1 if aa1 else "X")
    return "".join(parts), len(models), len(chain_ids), ",".join(chain_ids)


def pae_matrix(path: Path) -> list[list[float]]:
    """Ekstrak matrix PAE via format yang diterima eksplisit (tanpa transpose/reshape)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    matrix = None
    if isinstance(data, dict) and "predicted_aligned_error" in data:
        matrix = data["predicted_aligned_error"]
    elif isinstance(data, list) and data and isinstance(data[0], dict) and "predicted_aligned_error" in data[0]:
        matrix = data[0]["predicted_aligned_error"]
    elif isinstance(data, list) and data and all(isinstance(row, list) for row in data):
        matrix = data
    if not isinstance(matrix, list) or not matrix or not all(isinstance(row, list) for row in matrix):
        raise ValueError("format PAE tidak dikenali")
    return matrix


def main() -> int:
    required = [CANDIDATES_PATH, CHECKSUMS_PATH, DOWNLOAD_MANIFEST_PATH, STRUCT_VAL_PATH, PAE_VAL_PATH]
    for p in required:
        if not p.is_file():
            print(f"[!] File wajib tidak ada: {p}")
            return 2

    cands = json.loads(CANDIDATES_PATH.read_text(encoding="utf-8"))
    approved = {c["uniprot_accession"] for c in cands["candidates"]}
    approved_len = {c["uniprot_accession"]: int(c["sequence_length"]) for c in cands["candidates"]}
    manifest = read_csv(DOWNLOAD_MANIFEST_PATH)
    checksums = read_csv(CHECKSUMS_PATH)
    struct_val = read_csv(STRUCT_VAL_PATH)
    pae_val = read_csv(PAE_VAL_PATH)

    manifest_by_acc = {r["uniprot_accession"]: r for r in manifest}
    checks_by_acc: dict[str, dict[str, dict]] = {}
    for r in checksums:
        checks_by_acc.setdefault(r["uniprot_accession"], {})[r["file_type"]] = r
    struct_by_acc = {r["uniprot_accession"]: r for r in struct_val}
    pae_by_acc = {r["uniprot_accession"]: r for r in pae_val}

    # --- 1. Tepat 7 protein sesuai daftar yang disetujui
    check(
        "1. Tepat 7 protein, sesuai kandidat yang disetujui",
        len(manifest) == 7 and {r["uniprot_accession"] for r in manifest} == approved,
        f"manifest={sorted(r['uniprot_accession'] for r in manifest)}",
    )

    # --- 2. Accession unik
    accs = [r["uniprot_accession"] for r in manifest]
    check("2. Accession unik", len(accs) == len(set(accs)) == 7, f"{len(accs)} baris, {len(set(accs))} unik")

    # --- 3 & 4. CIF + PAE ada untuk setiap protein
    cif_ok = all((RAW_DIR / r["structure_filename"]).is_file() for r in manifest)
    pae_ok = all((RAW_DIR / r["pae_filename"]).is_file() for r in manifest)
    check("3. Setiap protein punya file CIF", cif_ok,
          f"hilang: {[r['structure_filename'] for r in manifest if not (RAW_DIR / r['structure_filename']).is_file()]}")
    check("4. Setiap protein punya file PAE JSON", pae_ok,
          f"hilang: {[r['pae_filename'] for r in manifest if not (RAW_DIR / r['pae_filename']).is_file()]}")

    # --- 5. Ukuran file > 0 dan cocok dengan checksums
    size_ok, size_detail = True, ""
    for acc in approved:
        for ft in ("structure_cif", "pae_json"):
            row = checks_by_acc.get(acc, {}).get(ft)
            if not row:
                size_ok, size_detail = False, f"{acc}: baris checksums {ft} tidak ada"
                break
            fpath = RAW_DIR / row["filename"]
            actual = fpath.stat().st_size if fpath.is_file() else -1
            if actual <= 0 or actual != int(row["file_size_bytes"]):
                size_ok, size_detail = False, f"{acc}/{ft}: disk={actual} csv={row['file_size_bytes']}"
                break
        if not size_ok:
            break
    check("5. Ukuran file > 0 dan cocok dengan catatan checksums", size_ok, size_detail)

    # --- 6. SHA256 dihitung ulang, format valid, konsisten CSV <-> manifest
    sha_ok, sha_detail = True, ""
    for acc in approved:
        m = manifest_by_acc[acc]
        for ft, manifest_field in (("structure_cif", "structure_sha256"), ("pae_json", "pae_sha256")):
            row = checks_by_acc.get(acc, {}).get(ft)
            fpath = RAW_DIR / row["filename"] if row else None
            recomputed = sha256_of_file(fpath) if fpath and fpath.is_file() else ""
            if not (HEX64.match(row["sha256"] if row else "") and recomputed == (row["sha256"] if row else "") == m[manifest_field]):
                sha_ok, sha_detail = False, f"{acc}/{ft}: csv={row['sha256'][:12] if row else None}.. manifest={m[manifest_field][:12]}.. hitung-ulang={recomputed[:12]}.."
                break
        if not sha_ok:
            break
    check("6. SHA256 valid (dihitung ulang) & konsisten checksums <-> manifest", sha_ok, sha_detail)

    # --- 7 & 8. Panjang sekuens + sequence match (hitung ulang dari CIF vs metadata API)
    seq_ok, seq_detail = True, ""
    match_ok, match_detail = True, ""
    for acc in approved:
        m = manifest_by_acc[acc]
        rec = json.loads((META_DIR / f"api_{acc}.json").read_text(encoding="utf-8"))
        rec = rec[0] if isinstance(rec, list) else rec
        seq_cif, n_models, n_chains = cif_sequence(RAW_DIR / m["structure_filename"])[:3]
        if len(seq_cif) != int(m["sequence_length"]) != approved_len[acc]:
            seq_ok, seq_detail = False, f"{acc}: CIF={len(seq_cif)}, manifest={m['sequence_length']}, kandidat={approved_len[acc]}"
            break
        if seq_cif != rec["uniprotSequence"] or struct_by_acc[acc]["sequence_match"] != "YES":
            match_ok, match_detail = False, f"{acc}: CIF==API? {seq_cif == rec['uniprotSequence']}, csv sequence_match={struct_by_acc[acc]['sequence_match']}"
            break
    check("7. Panjang sekuens CIF cocok dengan metadata", seq_ok, seq_detail)
    check("8. Sequence match CIF vs sekuens resmi metadata API = PASS", match_ok, match_detail)

    # --- 9. Matrix PAE N x N cocok dengan panjang sekuens (hitung ulang)
    pae_shape_ok, pae_shape_detail = True, ""
    for acc in approved:
        m = manifest_by_acc[acc]
        matrix = pae_matrix(RAW_DIR / m["pae_filename"])
        n = int(m["sequence_length"])
        dims_ok = len(matrix) == n and all(len(row) == n for row in matrix)
        csv_ok = (
            pae_by_acc[acc]["matrix_shape_valid"] == "YES"
            and int(pae_by_acc[acc]["pae_rows"]) == n
            and int(pae_by_acc[acc]["pae_columns"]) == n
        )
        if not (dims_ok and csv_ok):
            pae_shape_ok, pae_shape_detail = False, f"{acc}: matrix={len(matrix)}x{len(matrix[0])}, n={n}, csv={pae_by_acc[acc]['matrix_shape_valid']}"
            break
    check("9. Matrix PAE N x N cocok dengan panjang sekuens", pae_shape_ok, pae_shape_detail)

    # --- 10. Source = AlphaFold DB
    src_ok = all(r["source"] == "AlphaFoldDB" for r in manifest) and all(
        r["url"].startswith("https://alphafold.ebi.ac.uk/") for r in checksums
    )
    check("10. Source = AlphaFold DB (nilai 'AlphaFoldDB', URL host alphafold.ebi.ac.uk)", src_ok,
          f"sources={sorted({r['source'] for r in manifest})}")

    # --- 11. License metadata tersedia
    lic_ok = all(r["license"] == "CC BY 4.0" for r in manifest) and bool(
        str(cands.get("source", {}).get("license", "")).strip()
    )
    check("11. License metadata tersedia (CC BY 4.0)", lic_ok,
          f"licenses={sorted({r['license'] for r in manifest})}")

    # --- 12. Tidak ada file kandidat tambahan
    expected_files = set()
    for r in manifest:
        expected_files.add(r["structure_filename"])
        expected_files.add(r["pae_filename"])
    actual_files = sorted(f.name for f in RAW_DIR.iterdir() if f.is_file() and f.suffix.lower() in RAW_SUFFIXES)
    extra = [f for f in actual_files if f not in expected_files]
    missing = [f for f in expected_files if f not in actual_files]
    check("12. Tidak ada file kandidat tambahan yang tidak disetujui", not extra and not missing,
          f"ekstra={extra[:5]}, hilang={missing[:5]}")

    # --- Test tambahan
    check("E1. Checksums: 14 baris, semua download_status=OK, http_status=200",
          len(checksums) == 14 and all(r["download_status"] == "OK" and r["http_status"] == "200" for r in checksums),
          f"rows={len(checksums)}")

    struct_e_ok = all(
        r["validation_status"] == "PASS" and r["model_count"] == "1" and r["chain_count"] == "1"
        and r["observed_length"] == r["expected_length"] and r["afdb_sequence_checksum_match"] == "YES"
        for r in struct_val
    )
    check("E2. Structure validation: 1 model, 1 chain, panjang cocok, checksum AFDB cocok = PASS semua", struct_e_ok)

    manifest_e_ok = all(
        r["status"] == "DOWNLOADED_VALIDATED" and r["structure_validation"] == "PASS" and r["pae_validation"] == "PASS"
        for r in manifest
    )
    check("E3. Semua manifest status = DOWNLOADED_VALIDATED", manifest_e_ok,
          f"status={sorted({r['status'] for r in manifest})}")

    ver_ok = True
    ver_detail = ""
    for acc in approved:
        rec = json.loads((META_DIR / f"api_{acc}.json").read_text(encoding="utf-8"))
        rec = rec[0] if isinstance(rec, list) else rec
        api_ver = str(rec["latestVersion"])
        csv_vers = {checks_by_acc[acc][ft]["afdb_version"] for ft in ("structure_cif", "pae_json")}
        if csv_vers != {api_ver} or manifest_by_acc[acc]["afdb_version"] != api_ver:
            ver_ok, ver_detail = False, f"{acc}: api=v{api_ver}, csv={csv_vers}, manifest=v{manifest_by_acc[acc]['afdb_version']}"
            break
    check("E4. Versi AFDB konsisten (checksums == manifest == API latestVersion)", ver_ok, ver_detail)

    # --- Ringkasan
    failed = [r for r in results if not r[1]]
    print("\n" + "=" * 68)
    if failed:
        print(f"HASIL: {len(results) - len(failed)}/{len(results)} PASS, {len(failed)} FAIL")
        for name, _, detail in failed:
            print(f"  - {name}: {detail}")
        return 1
    print(f"HASIL: SEMUA {len(results)} TEST PASS")
    print("Catatan: ini validasi integritas file & konsistensi metadata, bukan validasi biologis.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
