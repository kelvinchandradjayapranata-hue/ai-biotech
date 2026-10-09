#!/usr/bin/env python3
"""
test_multi_protein_features.py - Tahap 6: validasi dataset fitur multi-protein (read-only).

Memeriksa hasil src/extract_multi_protein_features.py terhadap file mentah AFDB
(CIF, PAE json, api metadata) dan manifest Tahap 5. Semua nilai kritis DIHITUNG ULANG
dari file mentah, bukan sekadar membaca CSV.

Skema Tahap 6: 3 kolom identitas protein + 26 fitur = referensi Tahap 3 (28 kolom)
minus 2 kolom contact (contact_prob_sum, n_high_conf_contacts) yang bergantung pada
matriks contact_probs AlphaFold Server - tidak tersedia di dataset AFDB yang frozen.
Kolom contact DIKELUARKAN (bukan diimputasi/diproksikan) dan didokumentasikan eksplisit.

Checklist:
  1. Tepat 7 protein sesuai daftar yang disetujui (manifest DOWNLOADED_VALIDATED).
  2. Semua accession unik.
  3. Semua 7 protein expected tersedia di residue CSV & summary; tanpa protein tambahan.
  4. Semua 7 protein menghasilkan rows (>0).
  5. Residue count per protein cocok dengan sequence_length manifest.
  6. Total residue rows = 1098.
  7. Chain valid (1 chain/protein; = chainId API).
  8. Residue numbering valid (1..N berurutan; recompute CIF).
  9. Sequence position valid (1..N; sekuens CSV = uniprotSequence API).
 10. PAE matrix N x N + rekalkulasi fitur PAE (anti-transpose).
 11. Tidak ada NaN/kosong pada mandatory fields (3 identifier + 26 fitur).
 12. Feature columns = 26 fitur + 3 identifier (referensi 28 Tahap 3 minus 2 contact).
 13. 2 kolom contact memang tidak ada + terdokumentasi eksplisit di JSON.
 14. Tidak ada protein/file tambahan di luar yang disetujui.
 15. Output reproducible (rerun byte-identical: 3 file data + 2 PNG).
 16. Summary konsisten dengan residue CSV.
 17. Tidak ada timestamp/path absolut di output deterministik.
 18. Test Tahap 3 tetap lulus (20/20).
 19. Test Tahap 5 tetap lulus (16/16).
Tambahan: E1 plddt_ca = B-factor CA CIF; E2 total atom; E3 sha256 input = manifest;
E4 sequenceChecksum MD5; E5 granularitas pLDDT AFDB (std antar-atom = 0) terkunci.

Tidak mengakses jaringan. Tidak mengubah file apa pun. Exit code 0 hanya jika SEMUA PASS.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC_DIR))

from extract_multi_protein_features import (  # noqa: E402
    CONTACT_COLUMNS,
    EXPECTED_ACCESSIONS,
    EXPECTED_PROTEIN_COUNT,
    FEATURE_COLUMNS,
    ID_COLUMNS,
    OUTPUT_COLUMNS,
    SUMMARY_COLUMNS,
)

RESULTS = PROJECT_ROOT / "results" / "dataset"
MANIFEST = RESULTS / "dataset_download_manifest.csv"
RAW_DIR = PROJECT_ROOT / "data" / "alphafold_db" / "raw"
META_DIR = PROJECT_ROOT / "data" / "alphafold_db" / "metadata"
RESIDUE_CSV = RESULTS / "multi_protein_residue_features.csv"
SUMMARY_CSV = RESULTS / "multi_protein_summary.csv"
STRUCT_JSON = RESULTS / "multi_protein_structure_features.json"
PLOTS = [
    RESULTS / "multi_protein_plddt_overview.png",
    RESULTS / "multi_protein_pae_overview.png",
]
STAGE3_CSV = PROJECT_ROOT / "results" / "ubiquitin_residue_features.csv"
EXTRACT_SCRIPT = SRC_DIR / "extract_multi_protein_features.py"
TEST_STAGE3 = SRC_DIR / "test_protein_features.py"
TEST_STAGE5 = SRC_DIR / "test_afdb_download.py"

CONTACT_SET = set(CONTACT_COLUMNS)
EXPECTED_TOTAL = 1098
TOL = 1e-3
PAE_WINDOW = 10
RAW_SUFFIXES = {".cif", ".mmcif", ".pdb", ".json"}
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
ABS_PATH_RE = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]|/home/|/Users/")

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, bool(ok), detail))
    status = "PASS" if ok else "FAIL"
    line = f"[{status}] {name}"
    if detail and not ok:
        line += f"  -> {detail}"
    print(line)


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        return list(reader.fieldnames or []), list(reader)


def cif_recompute(path: Path) -> dict:
    """Hitung ulang ringkasan CIF secara independen: model, chain, residu, sekuens, atom, B-factor CA."""
    from Bio.PDB import MMCIFParser
    from Bio.PDB.Polypeptide import protein_letters_3to1

    structure = MMCIFParser(QUIET=True).get_structure("m", str(path))
    models = list(structure.get_models())
    model = models[0]
    chains = list(model.get_chains())
    nums, seq, ca_bf = [], [], {}
    n_atoms = 0
    for ch in chains:
        for res in ch.get_residues():
            if res.id[0] != " ":
                continue
            nums.append(int(res.id[1]))
            aa = protein_letters_3to1.get(res.resname.strip().upper())
            seq.append(aa or "X")
            ca_bf[int(res.id[1])] = float(res["CA"].get_bfactor())
            n_atoms += len(res)
    return {
        "n_models": len(models),
        "chain_ids": [c.id for c in chains],
        "nums": nums,
        "seq": "".join(seq),
        "n_atoms": n_atoms,
        "ca_bf": ca_bf,
    }


def pae_recompute(path: Path) -> np.ndarray:
    """Ekstrak matriks PAE dari json (format eksplisit; tanpa transpose/reshape)."""
    doc = json.loads(path.read_text(encoding="utf-8"))
    matrix = None
    if isinstance(doc, dict) and "predicted_aligned_error" in doc:
        matrix = doc["predicted_aligned_error"]
    elif isinstance(doc, list) and doc and isinstance(doc[0], dict) and "predicted_aligned_error" in doc[0]:
        matrix = doc[0]["predicted_aligned_error"]
    elif isinstance(doc, list) and doc and all(isinstance(r, list) for r in doc):
        matrix = doc
    if matrix is None:
        raise ValueError(f"format PAE tidak dikenali: {path.name}")
    return np.asarray(matrix, dtype=float)


def main() -> int:
    required = [MANIFEST, RESIDUE_CSV, SUMMARY_CSV, STRUCT_JSON, STAGE3_CSV, EXTRACT_SCRIPT,
                TEST_STAGE3, TEST_STAGE5, *PLOTS]
    for p in required:
        if not p.is_file():
            print(f"[!] File wajib tidak ada: {p}")
            return 2

    # --- Muat sumber
    _, manifest_all = read_csv(MANIFEST)
    manifest_rows = [r for r in manifest_all if r.get("status") == "DOWNLOADED_VALIDATED"]
    manifest_by_acc = {r["uniprot_accession"]: r for r in manifest_rows}
    order_accs = [r["uniprot_accession"] for r in manifest_rows]

    residue_header, residue_rows = read_csv(RESIDUE_CSV)
    summary_header, summary_rows = read_csv(SUMMARY_CSV)
    summary_by_acc = {r["uniprot_accession"]: r for r in summary_rows}
    doc = json.loads(STRUCT_JSON.read_text(encoding="utf-8"))
    doc_by_acc = {p["uniprot_accession"]: p for p in doc.get("proteins", [])}
    stage3_header, _ = read_csv(STAGE3_CSV)

    grouped: dict[str, list[dict]] = {}
    for r in residue_rows:
        grouped.setdefault(r["uniprot_accession"], []).append(r)

    # Recompute independen dari file mentah
    cif_cache = {acc: cif_recompute(RAW_DIR / manifest_by_acc[acc]["structure_filename"]) for acc in order_accs}
    pae_cache = {acc: pae_recompute(RAW_DIR / manifest_by_acc[acc]["pae_filename"]) for acc in order_accs}
    api_cache = {
        acc: (json.loads((META_DIR / f"api_{acc}.json").read_text(encoding="utf-8")))
        for acc in order_accs
    }
    api_cache = {acc: (v[0] if isinstance(v, list) else v) for acc, v in api_cache.items()}

    # --- 1. Tepat 7 protein sesuai daftar yang disetujui
    check(
        "1. Tepat 7 protein sesuai daftar yang disetujui (manifest DOWNLOADED_VALIDATED)",
        len(manifest_rows) == EXPECTED_PROTEIN_COUNT and set(order_accs) == set(EXPECTED_ACCESSIONS),
        f"manifest={sorted(order_accs)}",
    )

    # --- 2. Accession unik
    check(
        "2. Semua accession unik",
        len(order_accs) == len(set(order_accs)) == EXPECTED_PROTEIN_COUNT,
        f"{len(order_accs)} baris, {len(set(order_accs))} unik",
    )

    # --- 3. Semua 7 protein expected tersedia; tanpa protein tambahan
    res_accs = set(grouped)
    sum_accs = set(summary_by_acc)
    check(
        "3. Semua 7 protein expected tersedia di residue CSV & summary; tanpa protein tambahan",
        res_accs == sum_accs == set(EXPECTED_ACCESSIONS) and len(summary_rows) == EXPECTED_PROTEIN_COUNT,
        f"residue={sorted(res_accs)}, summary={sorted(sum_accs)}",
    )

    # --- 4. Semua 7 protein menghasilkan rows
    empty = [acc for acc in order_accs if len(grouped.get(acc, [])) == 0]
    check("4. Semua 7 protein menghasilkan rows (row count > 0)", not empty, f"tanpa rows: {empty}")

    # --- 5. Residue count per protein cocok dengan manifest (termasuk recompute CIF)
    per_acc_bad = []
    for acc in order_accs:
        m = manifest_by_acc[acc]
        cif = cif_cache[acc]
        s = summary_by_acc.get(acc, {})
        counts = {
            len(grouped.get(acc, [])),
            int(m["sequence_length"]),
            int(s.get("observed_residue_count", -1)),
            len(cif["nums"]),
            int(s.get("feature_row_count", -1)),
        }
        if len(counts) != 1:
            per_acc_bad.append(f"{acc}: {counts}")
    check(
        "5. Residue count per protein cocok dengan sequence_length manifest (recompute CIF)",
        not per_acc_bad,
        "; ".join(per_acc_bad),
    )

    # --- 6. Total residue rows = 1098
    total = len(residue_rows)
    total_manifest = sum(int(r["sequence_length"]) for r in manifest_rows)
    check(
        "6. Total residue rows = 1098",
        total == EXPECTED_TOTAL == total_manifest == doc.get("total_residue_rows"),
        f"csv={total}, manifest={total_manifest}, json={doc.get('total_residue_rows')}",
    )

    # --- 7. Chain valid: 1 chain per protein, konsisten CSV = CIF = API
    chain_bad = []
    for acc in order_accs:
        cif = cif_cache[acc]
        chain_api = str(api_cache[acc].get("chainId", ""))
        csv_chains = {r["chain"] for r in grouped[acc]}
        if not (cif["n_models"] == 1 and cif["chain_ids"] == [chain_api]
                and csv_chains == {chain_api}):
            chain_bad.append(f"{acc}: cif={cif['chain_ids']}, csv={csv_chains}, api={chain_api}")
    check("7. Chain valid (1 chain per protein; CSV = CIF = chainId API)", not chain_bad, "; ".join(chain_bad))

    # --- 8. Residue numbering valid: 1..N berurutan (recompute CIF + CSV)
    num_bad = []
    for acc in order_accs:
        cif = cif_cache[acc]
        n = len(cif["nums"])
        csv_ids = [int(r["residue_id"]) for r in grouped[acc]]
        if cif["nums"] != list(range(1, n + 1)) or csv_ids != list(range(1, n + 1)):
            num_bad.append(f"{acc}: cif_ok={cif['nums'] == list(range(1, n + 1))}, csv_ok={csv_ids == list(range(1, n + 1))}")
    check("8. Residue numbering valid: 1..N berurutan (recompute CIF)", not num_bad, "; ".join(num_bad))

    # --- 9. Sequence position valid + sekuens CSV = CIF = uniprotSequence API
    seq_bad = []
    for acc in order_accs:
        pos = [int(r["sequence_position"]) for r in grouped[acc]]
        n = len(pos)
        seq_csv = "".join(r["one_letter_aa"] for r in grouped[acc])
        official = str(api_cache[acc]["uniprotSequence"]).upper()
        if not (pos == list(range(1, n + 1)) and seq_csv == cif_cache[acc]["seq"] == official):
            seq_bad.append(f"{acc}: pos_ok={pos == list(range(1, n + 1))}, csv==cif={seq_csv == cif_cache[acc]['seq']}, cif==api={cif_cache[acc]['seq'] == official}")
    check("9. Sequence position valid (1..N) & sekuens CSV = CIF = uniprotSequence API", not seq_bad, "; ".join(seq_bad))

    # --- 10. PAE matrix N x N + rekalkulasi fitur PAE (anti-transpose)
    pae_bad = []
    for acc in order_accs:
        m = pae_cache[acc]
        rows = grouped[acc]
        n = len(rows)
        if m.shape != (n, n):
            pae_bad.append(f"{acc}: shape={m.shape} != ({n},{n})")
            continue
        row_raw = m.mean(axis=1)
        col_raw = m.mean(axis=0)
        local_raw = np.array([
            np.mean([m[i, j] for j in range(max(0, i - PAE_WINDOW), min(n, i + PAE_WINDOW + 1)) if j != i])
            for i in range(n)
        ])
        csv_row = np.array([float(r["pae_mean_row"]) for r in rows])
        csv_col = np.array([float(r["pae_mean_col"]) for r in rows])
        csv_loc = np.array([float(r["pae_local_mean_k10"]) for r in rows])
        ok_row = np.allclose(csv_row, row_raw, atol=TOL)
        ok_col = np.allclose(csv_col, col_raw, atol=TOL)
        ok_loc = np.allclose(csv_loc, local_raw, atol=TOL)
        asym = float(np.max(np.abs(m - m.T)))
        swapped = asym > 1.0 and np.allclose(csv_row, col_raw, atol=TOL) and not np.allclose(row_raw, col_raw, atol=TOL)
        if not (ok_row and ok_col and ok_loc) or swapped:
            pae_bad.append(f"{acc}: row={ok_row}, col={ok_col}, local={ok_loc}, swapped={swapped}")
    check("10. PAE matrix N x N + rekalkulasi fitur PAE = matriks mentah (anti-transpose)", not pae_bad, "; ".join(pae_bad))

    # --- 11. Tidak ada NaN/kosong pada mandatory fields
    blanks = [
        (r["uniprot_accession"], r["residue_id"], c)
        for r in residue_rows for c in residue_header
        if str(r[c]).strip() == "" or str(r[c]).strip().lower() in ("nan", "na", "none")
    ]
    check(
        "11. Tidak ada NaN/kosong pada mandatory fields (3 identifier + 26 fitur)",
        not blanks,
        f"contoh: {blanks[:5]}",
    )

    # --- 12. Feature columns sesuai schema (referensi Tahap 3 minus 2 contact + 3 identifier)
    expected_cols = list(ID_COLUMNS) + [c for c in stage3_header if c not in CONTACT_SET]
    js = doc.get("schema", {})
    schema_ok = (
        len(stage3_header) == 28
        and len(FEATURE_COLUMNS) == 26
        and residue_header == expected_cols == OUTPUT_COLUMNS
        and js.get("output_columns") == OUTPUT_COLUMNS
        and js.get("feature_columns") == FEATURE_COLUMNS
        and js.get("identifier_columns") == list(ID_COLUMNS)
        and js.get("historical_reference", {}).get("columns") == stage3_header
    )
    check(
        "12. Feature columns = 26 fitur + 3 identifier (referensi 28 Tahap 3 minus 2 contact)",
        schema_ok,
        f"csv={residue_header[:4]}...({len(residue_header)}); stage3=(28? {len(stage3_header) == 28})",
    )

    # --- 13. 2 kolom contact memang tidak ada + terdokumentasi di JSON
    exc = js.get("excluded_features", [])
    exc_names = [e.get("name") for e in exc]
    note = str(js.get("historical_reference", {}).get("note", ""))
    contact_ok = (
        all(c not in residue_header for c in CONTACT_COLUMNS)
        and all(c not in FEATURE_COLUMNS for c in CONTACT_COLUMNS)
        and all(c not in js.get("feature_definitions", {}) for c in CONTACT_COLUMNS)
        and sorted(exc_names) == sorted(CONTACT_COLUMNS)
        and all(e.get("reason") and e.get("source_channel") and e.get("stage3_definition") for e in exc)
        and "not present in the frozen AlphaFold DB dataset" in note
    )
    check(
        "13. 2 kolom contact tidak ada di output + terdokumentasi eksplisit di JSON",
        contact_ok,
        f"excluded_features={exc_names}, note_ok={'not present in the frozen' in note}",
    )

    # --- 14. Tidak ada protein/file tambahan di luar yang disetujui
    expected_raw = {
        manifest_by_acc[acc]["structure_filename"] for acc in order_accs
    } | {
        manifest_by_acc[acc]["pae_filename"] for acc in order_accs
    }
    actual_raw = {
        f.name for f in RAW_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in RAW_SUFFIXES
    }
    extra_files = sorted(actual_raw - expected_raw)
    missing_files = sorted(expected_raw - actual_raw)
    check(
        "14. Tidak ada protein/file tambahan di luar yang disetujui",
        not extra_files and not missing_files and res_accs == set(EXPECTED_ACCESSIONS),
        f"ekstra={extra_files[:5]}, hilang={missing_files[:5]}",
    )

    # --- 15. Output reproducible (rerun byte-identical)
    repro_detail = ""
    repro_ok = False
    with tempfile.TemporaryDirectory() as tmp:
        proc = subprocess.run(
            [
                sys.executable, str(EXTRACT_SCRIPT),
                "--manifest", str(MANIFEST),
                "--raw-dir", str(RAW_DIR),
                "--meta-dir", str(META_DIR),
                "--outdir", tmp,
            ],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        names = [RESIDUE_CSV.name, SUMMARY_CSV.name, STRUCT_JSON.name] + [p.name for p in PLOTS]
        mismatches = [
            name for name in names
            if not (Path(tmp) / name).is_file()
            or (Path(tmp) / name).read_bytes() != (RESULTS / name).read_bytes()
        ]
        repro_ok = proc.returncode == 0 and not mismatches
        if proc.returncode != 0:
            repro_detail = f"exit={proc.returncode}: {proc.stdout.strip()[-200:]} {proc.stderr.strip()[-200:]}"
        elif mismatches:
            repro_detail = f"file berbeda: {mismatches}"
    check("15. Output reproducible (rerun byte-identical: 3 file data + 2 PNG)", repro_ok, repro_detail)

    # --- 16. Summary konsisten dengan residue CSV
    summary_bad = []
    for acc in order_accs:
        s = summary_by_acc[acc]
        m = manifest_by_acc[acc]
        if not (
            s["status"] == "PASS"
            and int(s["feature_row_count"]) == len(grouped[acc])
            and int(s["observed_residue_count"]) == len(grouped[acc])
            and int(s["sequence_length"]) == int(m["sequence_length"])
            and s["afdb_id"] == m["afdb_id"]
            and s["protein_id"] == m["protein_id"]
        ):
            summary_bad.append(f"{acc}: status={s['status']}, rows={s['feature_row_count']}")
    check(
        "16. Summary konsisten dengan residue CSV (feature_row_count, status PASS, id)",
        not summary_bad and summary_header == SUMMARY_COLUMNS,
        "; ".join(summary_bad) or f"header_ok={summary_header == SUMMARY_COLUMNS}",
    )

    # --- 17. Tidak ada timestamp/path absolut di output deterministik
    offenders = []
    for p in (RESIDUE_CSV, SUMMARY_CSV, STRUCT_JSON):
        text = p.read_text(encoding="utf-8")
        m_date = DATE_RE.search(text)
        if m_date:
            offenders.append(f"{p.name}: tanggal '{m_date.group(0)}'")
        m_path = ABS_PATH_RE.search(text)
        if m_path:
            offenders.append(f"{p.name}: path lokal '{m_path.group(0)}'")
    if "generated_on" in STRUCT_JSON.read_text(encoding="utf-8"):
        offenders.append("JSON: field generated_on")
    check("17. Tidak ada timestamp/path absolut di output deterministik", not offenders, "; ".join(offenders))

    # --- 18. Test Tahap 3 tetap lulus
    proc3 = subprocess.run([sys.executable, str(TEST_STAGE3)], capture_output=True, text=True, cwd=str(PROJECT_ROOT))
    check(
        "18. Test Tahap 3 tetap lulus (20/20 PASS)",
        proc3.returncode == 0 and "TEST PASS" in proc3.stdout,
        f"exit={proc3.returncode}: {proc3.stdout.strip()[-200:]}",
    )

    # --- 19. Test Tahap 5 tetap lulus
    proc5 = subprocess.run([sys.executable, str(TEST_STAGE5)], capture_output=True, text=True, cwd=str(PROJECT_ROOT))
    check(
        "19. Test Tahap 5 tetap lulus (16/16 PASS)",
        proc5.returncode == 0 and "TEST PASS" in proc5.stdout,
        f"exit={proc5.returncode}: {proc5.stdout.strip()[-200:]}",
    )

    # --- E1. plddt_ca per row = B-factor CA CIF (recompute)
    e1_bad = []
    for acc in order_accs:
        ca_bf = cif_cache[acc]["ca_bf"]
        for r in grouped[acc]:
            exp = round(ca_bf[int(r["residue_id"])], 2)
            if abs(float(r["plddt_ca"]) - exp) > 1e-9:
                e1_bad.append(f"{acc}:{r['residue_id']} csv={r['plddt_ca']} exp={exp}")
                break
    check("E1. plddt_ca tiap row = B-factor CA file CIF (recompute)", not e1_bad, "; ".join(e1_bad[:5]))

    # --- E2. Total atom per protein = jumlah atom CIF (recompute)
    e2_bad = []
    for acc in order_accs:
        n_csv = sum(int(r["n_atoms"]) for r in grouped[acc])
        n_cif = cif_cache[acc]["n_atoms"]
        n_json = doc_by_acc[acc].get("n_atoms")
        if not (n_csv == n_cif == n_json):
            e2_bad.append(f"{acc}: csv={n_csv}, cif={n_cif}, json={n_json}")
    check("E2. Total atom per protein = jumlah atom CIF = JSON", not e2_bad, "; ".join(e2_bad))

    # --- E3. sha256 input di JSON = manifest (frozen) + recompute api metadata
    e3_bad = []
    for acc in order_accs:
        m = manifest_by_acc[acc]
        pj = doc_by_acc[acc]["inputs"]
        api_actual = sha256_of(META_DIR / f"api_{acc}.json")
        if not (
            pj["structure"]["sha256"] == m["structure_sha256"]
            and pj["pae_doc"]["sha256"] == m["pae_sha256"]
            and pj["api_metadata"]["sha256"] == api_actual
        ):
            e3_bad.append(acc)
    check("E3. sha256 input di JSON = manifest (frozen) + api metadata (recompute)", not e3_bad, f"beda: {e3_bad}")

    # --- E4. sequenceChecksum MD5 API cocok dengan sekuens dataset (recompute)
    e4_bad = []
    for acc in order_accs:
        seq = "".join(r["one_letter_aa"] for r in grouped[acc])
        md5 = hashlib.md5(seq.encode("ascii")).hexdigest()
        if md5 != str(api_cache[acc].get("sequenceChecksum", "")):
            e4_bad.append(acc)
    check("E4. sequenceChecksum MD5 API cocok dengan sekuens dataset (recompute)", not e4_bad, f"beda: {e4_bad}")

    # --- E5. Granularitas pLDDT AFDB terkunci: semua atom residu membawa pLDDT per-residu (std = 0)
    e5_bad = [
        (r["uniprot_accession"], r["residue_id"])
        for r in residue_rows
        if not (float(r["plddt_atom_std"]) == 0.0
                and float(r["plddt_atom_mean"]) == float(r["plddt_ca"]))
    ]
    check(
        "E5. Granularitas AFDB terkunci: pLDDT per-residu di semua atom (std=0, atom-mean=plddt_ca)",
        not e5_bad,
        f"anomali: {e5_bad[:5]}",
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
    print("Catatan: validasi ini memeriksa konsistensi dataset terhadap sumber prediksi,")
    print("bukan validasi biologis.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
