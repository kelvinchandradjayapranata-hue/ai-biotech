#!/usr/bin/env python3
"""
prepare_dataset.py - Tahap 4: bangun manifest dataset dari metadata kandidat AlphaFold DB.

Membaca metadata kandidat (default: data/alphafold_db/metadata/candidates.json),
memvalidasi skema + keunikan identifier + validitas panjang sekuens + kelengkapan
sumber/lisensi, lalu menulis manifest deterministik ke
results/dataset/dataset_manifest.csv.

PENTING:
- Script ini TIDAK melakukan akses jaringan dan TIDAK mengunduh apa pun.
  Unduhan struktur AlphaFold DB dilakukan di tahap terpisah SETELAH manifest direview.
- Output deterministik (tanpa timestamp) sehingga bisa direproduksi dan
  dibandingkan byte-per-byte oleh src/test_dataset_manifest.py.
- Validasi gagal -> manifest TIDAK ditulis, exit code 1.

Contoh pemakaian:
    python src/prepare_dataset.py
    python src/prepare_dataset.py --candidates data/alphafold_db/metadata/candidates.json --outdir results/dataset
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CANDIDATES = PROJECT_ROOT / "data" / "alphafold_db" / "metadata" / "candidates.json"
DEFAULT_OUTDIR = PROJECT_ROOT / "results" / "dataset"
DEFAULT_MANIFEST_NAME = "dataset_manifest.csv"

# Kolom manifest (urutan tetap; perubahan di sini = perubahan skema)
MANIFEST_COLUMNS = [
    "protein_id",
    "uniprot_accession",
    "uniprot_entry_name",
    "afdb_entry_id",
    "protein_name",
    "gene",
    "organism",
    "category",
    "sequence_length",
    "function_summary",
    "source",
    "source_url",
    "api_url",
    "license",
    "license_url",
    "annotation_source",
    "annotation_url",
    "planned_model_file",
    "planned_pae_file",
    "status",
    "notes",
]

# Field wajib (string tidak kosong) per kandidat.
# sequence_length & model_version_recorded divalidasi terpisah sebagai integer.
REQUIRED_STR_FIELDS = [
    "protein_id",
    "uniprot_accession",
    "uniprot_entry_name",
    "afdb_entry_id",
    "protein_name",
    "gene",
    "organism",
    "category",
    "function_summary",
    "source",
    "source_url",
    "api_url",
    "license",
    "license_url",
    "annotation_source",
    "annotation_url",
    "planned_model_file",
    "planned_pae_file",
    "status",
]

# Regex accession UniProtKB resmi (6 atau 10 karakter)
ACCESSION_RE = re.compile(
    r"^([OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2})$"
)
# Entry ID AlphaFold DB: AF-<accession>-F<n>
ENTRY_ID_RE = re.compile(r"^AF-[A-Z0-9]{6,10}-F[0-9]+$")

SOURCE_ALLOWED = {"AlphaFoldDB"}
LICENSE_ALLOWED = {"CC BY 4.0"}
STATUS_ALLOWED = {"planned_not_downloaded", "downloaded"}
CATEGORY_ALLOWED = {
    "enzyme",
    "oxygen_binding",
    "electron_transfer",
    "calcium_signaling",
    "antioxidant_enzyme",
    "fluorescent_protein",
}

SEQ_LEN_MIN, SEQ_LEN_MAX = 20, 600   # kriteria Tahap 4: protein kecil/moderat
COUNT_MIN, COUNT_MAX = 5, 10         # target jumlah kandidat Tahap 4
MIN_CATEGORIES = 3                   # kriteria keberagaman


def validate(doc: dict) -> tuple[list[str], list[str]]:
    """Validasi dokumen metadata kandidat. Kembalikan (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    # --- Blok sumber & lisensi wajib lengkap
    src = doc.get("source")
    if not isinstance(src, dict):
        errors.append("dokumen tidak punya blok 'source' (objek)")
        src = {}
    for key in ("name", "full_name", "url", "license", "license_url", "attribution_note"):
        if not str(src.get(key, "")).strip():
            errors.append(f"source.{key} wajib diisi")
    citations = src.get("citation")
    if not (isinstance(citations, list) and citations and all(str(c).strip() for c in citations)):
        errors.append("source.citation wajib berisi minimal 1 sitasi")

    # --- Daftar kandidat
    cands = doc.get("candidates")
    if not isinstance(cands, list) or not cands:
        errors.append("'candidates' wajib berupa list tidak kosong")
        return errors, warnings
    if not (COUNT_MIN <= len(cands) <= COUNT_MAX):
        warnings.append(
            f"jumlah kandidat {len(cands)} di luar target Tahap 4 ({COUNT_MIN}-{COUNT_MAX})"
        )

    seen: dict[str, list[str]] = {
        "protein_id": [],
        "uniprot_accession": [],
        "afdb_entry_id": [],
        "source_url": [],
    }
    cats: set[str] = set()

    for i, c in enumerate(cands):
        tag = f"kandidat #{i + 1}"
        if not isinstance(c, dict):
            errors.append(f"{tag}: bukan objek JSON")
            continue
        pid = str(c.get("protein_id", "")).strip() or tag
        acc = str(c.get("uniprot_accession", "")).strip()
        entry = str(c.get("afdb_entry_id", "")).strip()

        # Field string wajib
        for field in REQUIRED_STR_FIELDS:
            if not str(c.get(field, "")).strip():
                errors.append(f"{tag} ({pid}): field '{field}' wajib diisi")

        # Identifier
        if acc and not ACCESSION_RE.match(acc):
            errors.append(f"{tag} ({pid}): format accession UniProt tidak valid: {acc!r}")
        if acc and pid and pid != acc:
            errors.append(f"{tag} ({pid}): protein_id harus sama dengan uniprot_accession")
        if entry:
            if not ENTRY_ID_RE.match(entry):
                errors.append(f"{tag} ({pid}): format afdb_entry_id tidak valid: {entry!r}")
            elif acc and entry != f"AF-{acc}-F1":
                errors.append(f"{tag} ({pid}): afdb_entry_id {entry!r} != 'AF-{acc}-F1'")

        # URL konsisten dengan accession
        for field, expected in (
            ("source_url", f"https://alphafold.ebi.ac.uk/entry/{acc}"),
            ("api_url", f"https://alphafold.ebi.ac.uk/api/prediction/{acc}"),
            ("annotation_url", f"https://www.uniprot.org/uniprotkb/{acc}/entry"),
        ):
            got = str(c.get(field, "")).strip()
            if acc and got and got != expected:
                errors.append(f"{tag} ({pid}): {field} tidak konsisten dengan accession ({got!r})")

        # Enum source / license / status / category
        if str(c.get("source", "")).strip() not in SOURCE_ALLOWED:
            errors.append(f"{tag} ({pid}): source harus salah satu {sorted(SOURCE_ALLOWED)}")
        if str(c.get("license", "")).strip() not in LICENSE_ALLOWED:
            errors.append(f"{tag} ({pid}): license harus salah satu {sorted(LICENSE_ALLOWED)}")
        if str(c.get("status", "")).strip() not in STATUS_ALLOWED:
            errors.append(f"{tag} ({pid}): status harus salah satu {sorted(STATUS_ALLOWED)}")
        cat = str(c.get("category", "")).strip()
        if cat:
            cats.add(cat)
            if cat not in CATEGORY_ALLOWED:
                errors.append(
                    f"{tag} ({pid}): category {cat!r} tidak dikenal (opsi: {sorted(CATEGORY_ALLOWED)})"
                )

        # Panjang sekuens
        ln = c.get("sequence_length")
        if isinstance(ln, bool) or not isinstance(ln, int):
            errors.append(f"{tag} ({pid}): sequence_length harus integer, ditemukan {ln!r}")
        elif not (SEQ_LEN_MIN <= ln <= SEQ_LEN_MAX):
            errors.append(
                f"{tag} ({pid}): sequence_length {ln} di luar kriteria Tahap 4 "
                f"({SEQ_LEN_MIN}-{SEQ_LEN_MAX} aa)"
            )

        # Versi model + nama file rencana harus konsisten dengan entry ID
        ver = c.get("model_version_recorded")
        if isinstance(ver, bool) or not isinstance(ver, int) or ver < 1:
            errors.append(f"{tag} ({pid}): model_version_recorded harus integer >= 1, ditemukan {ver!r}")
        elif acc and entry:
            expected_model = f"{entry}-model_v{ver}.cif"
            expected_pae = f"{entry}-predicted_aligned_error_v{ver}.json"
            if str(c.get("planned_model_file", "")).strip() != expected_model:
                errors.append(f"{tag} ({pid}): planned_model_file != {expected_model!r}")
            if str(c.get("planned_pae_file", "")).strip() != expected_pae:
                errors.append(f"{tag} ({pid}): planned_pae_file != {expected_pae!r}")

        for key in seen:
            val = str(c.get(key, "")).strip()
            if val:
                seen[key].append(val)

    # Keunikan identifier
    for key, vals in seen.items():
        dupes = sorted({v for v in vals if vals.count(v) > 1})
        if dupes:
            errors.append(f"nilai duplikat pada {key}: {dupes}")

    # Keberagaman kategori
    if len(cats) < MIN_CATEGORIES:
        errors.append(
            f"keberagaman gagal: hanya {len(cats)} kategori berbeda (minimal {MIN_CATEGORIES})"
        )

    return errors, warnings


def build_rows(cands: list[dict]) -> list[dict]:
    """Bentuk baris manifest (urutan kolom tetap, mengikuti urutan kandidat)."""
    rows = []
    for c in cands:
        row = {col: c.get(col, "") for col in MANIFEST_COLUMNS}
        row["sequence_length"] = int(c["sequence_length"])
        rows.append(row)
    return rows


def write_manifest(rows: list[dict], out_path: Path) -> None:
    """Tulis CSV deterministik (LF, tanpa timestamp)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=MANIFEST_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bangun manifest dataset dari metadata kandidat AlphaFold DB (tanpa unduhan)."
    )
    parser.add_argument(
        "--candidates",
        type=Path,
        default=DEFAULT_CANDIDATES,
        help=f"file metadata kandidat (default: {DEFAULT_CANDIDATES})",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=DEFAULT_OUTDIR,
        help=f"folder output manifest (default: {DEFAULT_OUTDIR})",
    )
    parser.add_argument(
        "--manifest-name",
        default=DEFAULT_MANIFEST_NAME,
        help=f"nama file manifest (default: {DEFAULT_MANIFEST_NAME})",
    )
    args = parser.parse_args()

    if not args.candidates.is_file():
        print(f"[!] File metadata kandidat tidak ditemukan: {args.candidates}")
        return 2
    try:
        doc = json.loads(args.candidates.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[!] JSON tidak valid di {args.candidates}: {exc}")
        return 2

    errors, warnings = validate(doc)
    for w in warnings:
        print(f"[WARN] {w}")
    if errors:
        print(f"\n[!] Validasi GAGAL - {len(errors)} masalah:")
        for e in errors:
            print(f"  - {e}")
        print("\nManifest TIDAK ditulis. Perbaiki metadata lalu jalankan ulang.")
        return 1

    rows = build_rows(doc["candidates"])
    out_path = args.outdir / args.manifest_name
    write_manifest(rows, out_path)

    cat_count = Counter(r["category"] for r in rows)
    total_aa = sum(r["sequence_length"] for r in rows)
    src = doc.get("source", {})
    print(f"OK: manifest ditulis -> {out_path}")
    print(f"  kandidat      : {len(rows)} protein ({total_aa} residu total)")
    print("  kategori      : " + ", ".join(f"{k}={v}" for k, v in sorted(cat_count.items())))
    print(f"  sumber        : {src.get('full_name', src.get('name', '?'))}")
    print(f"  lisensi       : {rows[0]['license']} ({rows[0]['license_url']})")
    print(f"  status        : {', '.join(sorted({r['status'] for r in rows}))} (belum ada unduhan)")
    print("  deterministik : ya (tanpa timestamp) - diverifikasi ulang oleh src/test_dataset_manifest.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
