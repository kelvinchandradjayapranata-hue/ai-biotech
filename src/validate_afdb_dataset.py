#!/usr/bin/env python3
"""
validate_afdb_dataset.py - Tahap 5: validasi integritas CIF + PAE hasil unduhan AFDB (offline).

Input  : data/alphafold_db/raw/ (file unduhan), data/alphafold_db/metadata/api_<acc>.json,
         data/alphafold_db/metadata/download_checksums.csv
Output : results/dataset/structure_validation.csv
         results/dataset/pae_validation.csv
         results/dataset/dataset_download_manifest.csv (manifest hasil unduhan, terpisah
         dari dataset_manifest.csv Tahap 4 yang TIDAK diubah)

Aturan:
- Offline (tanpa akses jaringan). Tidak mengubah nilai PAE. Tidak ada interpretasi biologis.
- Sekuens resmi pembanding = uniprotSequence dari metadata API AFDB (respons mentah
  tersimpan di api_<acc>.json). Nilai sequenceChecksum API diverifikasi sebagai MD5.
- Output deterministik (tanpa timestamp). Status manifest: DOWNLOADED_VALIDATED hanya
  jika CIF + PAE + checksum + sekuens semuanya PASS; selain itu FAILED.
"""

from __future__ import annotations

import csv
import hashlib
import json
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

STRUCT_COLUMNS = [
    "protein_id",
    "uniprot_accession",
    "expected_length",
    "observed_length",
    "sequence_match",
    "model_count",
    "chain_count",
    "chain_id",
    "afdb_sequence_checksum_match",
    "validation_status",
    "notes",
]

PAE_COLUMNS = [
    "protein_id",
    "uniprot_accession",
    "sequence_length",
    "pae_rows",
    "pae_columns",
    "matrix_shape_valid",
    "min_pae",
    "max_pae",
    "validation_status",
    "notes",
]

DOWNLOAD_MANIFEST_COLUMNS = [
    "protein_id",
    "uniprot_accession",
    "afdb_id",
    "afdb_version",
    "sequence_length",
    "structure_filename",
    "pae_filename",
    "structure_sha256",
    "pae_sha256",
    "structure_validation",
    "pae_validation",
    "source",
    "license",
    "status",
]

SOURCE_VALUE = "AlphaFoldDB"   # konsisten dengan candidates.json Tahap 4
LICENSE_VALUE = "CC BY 4.0"


def parse_cif(cif_path: Path) -> dict:
    """Parse CIF: jumlah model/chain + sekuens dari residu standar. Error -> field 'error'."""
    info = {
        "model_count": 0, "chain_count": 0, "chain_ids": [],
        "sequence": "", "n_unknown_residues": 0, "error": "",
    }
    try:
        structure = MMCIFParser(QUIET=True).get_structure("model", str(cif_path))
    except Exception as exc:  # noqa: BLE001
        info["error"] = f"parsing error: {exc}"
        return info
    models = list(structure.get_models())
    info["model_count"] = len(models)
    if len(models) != 1:
        info["error"] = f"jumlah model={info['model_count']} (diharapkan 1)"
        return info
    parts: list[str] = []
    for chain in models[0].get_chains():
        info["chain_ids"].append(chain.id)
        for res in chain.get_residues():
            if res.id[0] != " ":  # hanya residu standar (bukan HETATM/air)
                continue
            aa1 = protein_letters_3to1.get(res.resname.strip().upper())
            if aa1 is None:
                info["n_unknown_residues"] += 1
                parts.append("X")
            else:
                parts.append(aa1)
    info["chain_count"] = len(info["chain_ids"])
    info["sequence"] = "".join(parts)
    return info


def parse_pae(pae_path: Path) -> tuple[list | None, str, float | None, str]:
    """Kembalikan (matrix, format, max_predicted_aligned_error, error).

    Format yang diterima (eksplisit, tanpa transpose/reshape/tebakan):
      - dict dengan key 'predicted_aligned_error'
      - list[0] dict dengan key 'predicted_aligned_error' (format AFDB v6)
      - bare list-of-rows
    """
    try:
        data = json.loads(pae_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return None, "", None, f"JSON tidak valid: {exc}"

    matrix = None
    fmt = ""
    max_scalar = None
    if isinstance(data, dict) and "predicted_aligned_error" in data:
        matrix, fmt = data["predicted_aligned_error"], "dict['predicted_aligned_error']"
        max_scalar = data.get("max_predicted_aligned_error")
    elif isinstance(data, list) and data and isinstance(data[0], dict) and "predicted_aligned_error" in data[0]:
        matrix, fmt = data[0]["predicted_aligned_error"], "list[0]['predicted_aligned_error']"
        max_scalar = data[0].get("max_predicted_aligned_error")
    elif isinstance(data, list) and data and all(isinstance(row, list) for row in data):
        matrix, fmt = data, "bare list-of-rows"

    if matrix is None:
        return None, "", None, "format PAE tidak dikenali (key 'predicted_aligned_error' tidak ditemukan)"
    if not isinstance(matrix, list) or not matrix or not all(isinstance(row, list) for row in matrix):
        return None, "", None, "matrix PAE bukan list-of-rows"
    return matrix, fmt, max_scalar, ""


def load_checksums() -> dict[str, dict[str, dict]]:
    """acc -> {'structure_cif': row, 'pae_json': row}."""
    out: dict[str, dict[str, dict]] = {}
    with CHECKSUMS_PATH.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            out.setdefault(row["uniprot_accession"], {})[row["file_type"]] = row
    return out


def write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    for p in (CANDIDATES_PATH, CHECKSUMS_PATH):
        if not p.is_file():
            print(f"[!] Tidak ada: {p}")
            return 2

    candidates = json.loads(CANDIDATES_PATH.read_text(encoding="utf-8"))["candidates"]
    checksums = load_checksums()

    struct_rows: list[dict] = []
    pae_rows: list[dict] = []
    manifest_rows: list[dict] = []
    all_ok = True

    for c in candidates:
        acc = c["uniprot_accession"]
        expected_len = int(c["sequence_length"])
        rec = json.loads((META_DIR / f"api_{acc}.json").read_text(encoding="utf-8"))
        rec = rec[0] if isinstance(rec, list) else rec
        official_seq = str(rec["uniprotSequence"])
        entry_id = str(rec["entryId"])
        version = int(rec["latestVersion"])
        cs = checksums.get(acc, {})
        cif_row = cs.get("structure_cif", {})
        pae_row = cs.get("pae_json", {})

        # --- E. Validasi struktur CIF
        cif_path = RAW_DIR / cif_row.get("filename", "")
        notes: list[str] = []
        if not cif_path.is_file():
            info = {"model_count": 0, "chain_count": 0, "chain_ids": [], "sequence": "",
                    "n_unknown_residues": 0, "error": f"file tidak ada: {cif_path.name}"}
        else:
            info = parse_cif(cif_path)
        observed_len = len(info["sequence"])
        seq_match = info["sequence"] == official_seq
        md5_match = hashlib.md5(official_seq.encode("ascii")).hexdigest() == str(rec.get("sequenceChecksum", ""))
        if info["error"]:
            notes.append(info["error"])
        if info["chain_ids"]:
            notes.append(f"chains={','.join(info['chain_ids'])}")
        if info["n_unknown_residues"]:
            notes.append(f"{info['n_unknown_residues']} residu non-standar (X)")
        if observed_len != expected_len:
            notes.append(f"panjang observasi {observed_len} != metadata {expected_len}")
        if not seq_match:
            notes.append("sekuens CIF BERBEDA dari uniprotSequence metadata API")
        struct_status = "PASS" if (
            not info["error"]
            and info["model_count"] == 1
            and info["chain_count"] == 1
            and info["n_unknown_residues"] == 0
            and observed_len > 0
            and seq_match
            and observed_len == expected_len
            and md5_match
        ) else "FAIL"
        struct_rows.append({
            "protein_id": acc,
            "uniprot_accession": acc,
            "expected_length": expected_len,
            "observed_length": observed_len,
            "sequence_match": "YES" if seq_match else "NO",
            "model_count": info["model_count"],
            "chain_count": info["chain_count"],
            "chain_id": ",".join(info["chain_ids"]),
            "afdb_sequence_checksum_match": "YES" if md5_match else "NO",
            "validation_status": struct_status,
            "notes": "; ".join(notes),
        })

        # --- F. Validasi PAE
        pae_path = RAW_DIR / pae_row.get("filename", "")
        pae_notes: list[str] = []
        if not pae_path.is_file():
            matrix, fmt, max_scalar, err = None, "", None, f"file tidak ada: {pae_path.name}"
        else:
            matrix, fmt, max_scalar, err = parse_pae(pae_path)
        if err:
            pae_notes.append(err)
            rows_n = cols_n = 0
            shape_valid = False
            min_pae = max_pae = ""
        else:
            rows_n = len(matrix)
            col_lengths = {len(r) for r in matrix}
            rectangular = len(col_lengths) == 1
            cols_n = len(matrix[0])
            shape_valid = rectangular and rows_n == expected_len and cols_n == expected_len
            # dibaca apa adanya (read-only), tidak mengubah nilai
            min_pae = min(min(r) for r in matrix)
            max_pae = max(max(r) for r in matrix)
            if fmt:
                pae_notes.append(f"format={fmt}")
            if not rectangular:
                pae_notes.append("matrix tidak persegi (row length berbeda)")
            if max_scalar is not None:
                pae_notes.append(f"max_predicted_aligned_error={max_scalar}")
        pae_status = "PASS" if (not err and shape_valid) else "FAIL"
        pae_rows.append({
            "protein_id": acc,
            "uniprot_accession": acc,
            "sequence_length": expected_len,
            "pae_rows": rows_n,
            "pae_columns": cols_n,
            "matrix_shape_valid": "YES" if shape_valid else "NO",
            "min_pae": min_pae,
            "max_pae": max_pae,
            "validation_status": pae_status,
            "notes": "; ".join(pae_notes),
        })

        # --- G. Baris manifest unduhan
        files_ok = (
            cif_row.get("download_status") == "OK"
            and pae_row.get("download_status") == "OK"
            and bool(cif_row.get("sha256"))
            and bool(pae_row.get("sha256"))
        )
        status = "DOWNLOADED_VALIDATED" if (struct_status == "PASS" and pae_status == "PASS" and files_ok) else "FAILED"
        if status != "DOWNLOADED_VALIDATED":
            all_ok = False
        manifest_rows.append({
            "protein_id": acc,
            "uniprot_accession": acc,
            "afdb_id": entry_id,
            "afdb_version": version,
            "sequence_length": expected_len,
            "structure_filename": cif_row.get("filename", ""),
            "pae_filename": pae_row.get("filename", ""),
            "structure_sha256": cif_row.get("sha256", ""),
            "pae_sha256": pae_row.get("sha256", ""),
            "structure_validation": struct_status,
            "pae_validation": pae_status,
            "source": SOURCE_VALUE,
            "license": LICENSE_VALUE,
            "status": status,
        })

        print(
            f"{acc} {entry_id} v{version}: CIF {struct_status} "
            f"({info['model_count']} model, {info['chain_count']} chain, seq {'MATCH' if seq_match else 'MISMATCH'}) | "
            f"PAE {pae_status} ({rows_n}x{cols_n}) | manifest: {status}"
        )

    write_csv(RESULTS_DIR / "structure_validation.csv", STRUCT_COLUMNS, struct_rows)
    write_csv(RESULTS_DIR / "pae_validation.csv", PAE_COLUMNS, pae_rows)
    write_csv(RESULTS_DIR / "dataset_download_manifest.csv", DOWNLOAD_MANIFEST_COLUMNS, manifest_rows)
    print(f"\nDitulis: results/dataset/structure_validation.csv, pae_validation.csv, dataset_download_manifest.csv")
    n_ok = sum(1 for r in manifest_rows if r["status"] == "DOWNLOADED_VALIDATED")
    print(f"Status: {n_ok}/{len(manifest_rows)} DOWNLOADED_VALIDATED")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
