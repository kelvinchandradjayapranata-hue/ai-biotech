#!/usr/bin/env python3
"""
test_dataset_manifest.py - Tahap 4: validasi manifest dataset (read-only).

Memeriksa results/dataset/dataset_manifest.csv terhadap metadata kandidat
(data/alphafold_db/metadata/candidates.json) dan memastikan script
src/prepare_dataset.py mereproduksi manifest yang sama persis.
Exit code 0 hanya jika SEMUA test PASS.

Checklist (sesuai permintaan Tahap 4):
  1. Manifest ada + header sesuai skema kolom.
  2. Jumlah protein 5-10 (kriteria Tahap 4).
  3. protein_id unik (satu baris = satu protein).
  4. Tidak ada duplikat (protein_id, accession, entry AFDB, baris penuh).
  5. Source wajib ada di setiap baris.
  6. sequence_length wajib ada, valid, dan cocok dengan metadata kandidat.
  7. License + source metadata wajib ada (per baris dan di dokumen kandidat).
  8. Manifest reproducible: re-run prepare_dataset.py -> byte-identik.

Test tambahan: konsistensi himpunan protein manifest vs kandidat, pola nama
file rencana, status rencana, dan folder raw/ hanya berisi file kandidat yang
disetujui (hasil unduhan Tahap 5; integritas file diverifikasi penuh oleh
src/test_afdb_download.py).
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC_DIR))
from prepare_dataset import MANIFEST_COLUMNS  # satu sumber kebenaran untuk skema

MANIFEST_PATH = PROJECT_ROOT / "results" / "dataset" / "dataset_manifest.csv"
CANDIDATES_PATH = PROJECT_ROOT / "data" / "alphafold_db" / "metadata" / "candidates.json"
PREPARE_SCRIPT = SRC_DIR / "prepare_dataset.py"
RAW_DIR = PROJECT_ROOT / "data" / "alphafold_db" / "raw"

SEQ_LEN_MIN, SEQ_LEN_MAX = 20, 600
COUNT_MIN, COUNT_MAX = 5, 10

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, bool(ok), detail))
    status = "PASS" if ok else "FAIL"
    line = f"[{status}] {name}"
    if detail and not ok:
        line += f"  -> {detail}"
    print(line)


def main() -> int:
    for p in (MANIFEST_PATH, CANDIDATES_PATH, PREPARE_SCRIPT):
        if not p.is_file():
            print(f"[!] File wajib tidak ada: {p}")
            return 2
    if RAW_DIR.is_dir():
        raw_files = sorted(
            f for f in RAW_DIR.iterdir()
            if f.is_file() and f.suffix.lower() in {".cif", ".mmcif", ".pdb", ".json"}
        )
    else:
        raw_files = []
        print(f"[!] Folder raw tidak ada: {RAW_DIR}")

    # --- Muat sumber
    with MANIFEST_PATH.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        header = reader.fieldnames or []
        rows = list(reader)
    cand_doc = json.loads(CANDIDATES_PATH.read_text(encoding="utf-8"))
    cands = cand_doc.get("candidates", [])
    cand_by_id = {c.get("protein_id"): c for c in cands}

    # --- 1. Header sesuai skema
    check(
        "1. Manifest ada dan header sesuai skema kolom",
        header == MANIFEST_COLUMNS and len(rows) > 0,
        f"header={header[:4]}... ({len(header)} kolom), rows={len(rows)}",
    )

    # --- 2. Jumlah protein 5-10
    check(
        f"2. Jumlah protein {COUNT_MIN}-{COUNT_MAX} (kriteria Tahap 4)",
        COUNT_MIN <= len(rows) <= COUNT_MAX,
        f"ditemukan {len(rows)} baris",
    )

    # --- 3. protein_id unik
    ids = [r["protein_id"] for r in rows]
    check("3. protein_id unik", len(ids) == len(set(ids)), f"{len(ids)} baris, {len(set(ids))} id unik")

    # --- 4. Tidak ada duplikat
    accs = [r["uniprot_accession"] for r in rows]
    entries = [r["afdb_entry_id"] for r in rows]
    full = [tuple(r[c] for c in MANIFEST_COLUMNS) for r in rows]
    check(
        "4. Tidak ada duplikat (protein_id/accession/entry/baris)",
        len(set(accs)) == len(accs) and len(set(entries)) == len(entries) and len(set(full)) == len(full),
        f"acc_unik={len(set(accs))}/{len(accs)}, entry_unik={len(set(entries))}/{len(entries)}, baris_unik={len(set(full))}/{len(full)}",
    )

    # --- 5. Source wajib ada
    sources = {r["source"] for r in rows}
    check(
        "5. Source wajib ada di setiap baris (= 'AlphaFoldDB')",
        sources == {"AlphaFoldDB"} and all(r["source"].strip() for r in rows),
        f"sources={sources}",
    )

    # --- 6. sequence_length ada + valid + cocok dengan metadata
    len_ok = True
    len_detail = ""
    for r in rows:
        raw = r["sequence_length"].strip()
        if not raw.isdigit():
            len_ok, len_detail = False, f"{r['protein_id']}: bukan integer ({raw!r})"
            break
        n = int(raw)
        if not (SEQ_LEN_MIN <= n <= SEQ_LEN_MAX):
            len_ok, len_detail = False, f"{r['protein_id']}: {n} di luar {SEQ_LEN_MIN}-{SEQ_LEN_MAX}"
            break
        c = cand_by_id.get(r["protein_id"])
        if c is None or int(c.get("sequence_length", -1)) != n:
            len_ok, len_detail = False, f"{r['protein_id']}: {n} != metadata"
            break
    check(
        "6. sequence_length wajib ada, valid, cocok dengan metadata kandidat",
        len_ok,
        len_detail,
    )

    # --- 7. License + source metadata wajib ada
    lic_ok = True
    lic_detail = ""
    meta_fields = ("license", "license_url", "source_url", "api_url", "annotation_source", "annotation_url")
    for r in rows:
        for f in meta_fields:
            if not r[f].strip():
                lic_ok, lic_detail = False, f"{r['protein_id']}: field '{f}' kosong"
                break
        if not lic_ok:
            break
        if r["license"] != "CC BY 4.0":
            lic_ok, lic_detail = False, f"{r['protein_id']}: license={r['license']!r}"
            break
        if r["source_url"] != f"https://alphafold.ebi.ac.uk/entry/{r['uniprot_accession']}":
            lic_ok, lic_detail = False, f"{r['protein_id']}: source_url tidak konsisten"
            break
    src = cand_doc.get("source", {})
    top_ok = all(str(src.get(k, "")).strip() for k in ("url", "license", "license_url")) and bool(src.get("citation"))
    check(
        "7. License + source metadata wajib ada (per baris & dokumen kandidat)",
        lic_ok and top_ok,
        lic_detail or "blok source dokumen kandidat tidak lengkap",
    )

    # --- 8. Manifest reproducible (byte-identik)
    with tempfile.TemporaryDirectory() as tmp:
        proc = subprocess.run(
            [
                sys.executable,
                str(PREPARE_SCRIPT),
                "--candidates", str(CANDIDATES_PATH),
                "--outdir", tmp,
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        tmp_manifest = Path(tmp) / "dataset_manifest.csv"
        same = (
            proc.returncode == 0
            and tmp_manifest.is_file()
            and tmp_manifest.read_bytes() == MANIFEST_PATH.read_bytes()
        )
        detail = ""
        if proc.returncode != 0:
            detail = f"prepare exit={proc.returncode}: {proc.stdout.strip()[-200:]} {proc.stderr.strip()[-200:]}"
        elif not same:
            detail = "output re-run berbeda byte-per-byte dengan manifest"
    check("8. Manifest reproducible (re-run prepare_dataset.py byte-identik)", same, detail)

    # --- Test tambahan
    manifest_ids = set(ids)
    cand_ids = set(cand_by_id)
    check(
        "E1. Himpunan protein manifest = himpunan kandidat (tanpa yatim)",
        manifest_ids == cand_ids,
        f"hanya di manifest: {sorted(manifest_ids - cand_ids)[:5]}, hanya di kandidat: {sorted(cand_ids - manifest_ids)[:5]}",
    )

    planned_ok = all(
        r["planned_model_file"].endswith(".cif")
        and "predicted_aligned_error" in r["planned_pae_file"]
        and r["planned_pae_file"].endswith(".json")
        and r["status"] == "planned_not_downloaded"
        for r in rows
    )
    check("E2. Nama file rencana & status 'planned_not_downloaded' konsisten", planned_ok)

    func_ok = all(r["function_summary"].strip() for r in rows)
    check("E3. function_summary terisi untuk semua protein", func_ok)

    expected_raw = set()
    for c in cands:
        expected_raw.add(str(c.get("planned_model_file", "")))
        expected_raw.add(str(c.get("planned_pae_file", "")))
    extra_raw = [f.name for f in raw_files if f.name not in expected_raw]
    check(
        "E4. Folder raw/ hanya berisi file kandidat yang disetujui (Tahap 5)",
        not extra_raw,
        f"file di luar persetujuan: {extra_raw}",
    )

    # --- Ringkasan
    failed = [r for r in results if not r[1]]
    print("\n" + "=" * 68)
    if failed:
        print(f"HASIL: {len(results) - len(failed)}/{len(results)} PASS, {len(failed)} FAIL")
        for name, _, detail in failed:
            print(f"  - {name}: {detail}")
        return 1
    print(f"HASIL: SEMUA {len(results)} TEST PASS")
    print("Catatan: ini validasi struktur/kelengkapan manifest, bukan validasi biologis.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
