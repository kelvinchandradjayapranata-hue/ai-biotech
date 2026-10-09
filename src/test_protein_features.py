#!/usr/bin/env python3
"""
test_protein_features.py - Tahap 3C: validasi dataset feature per-residue (read-only).

Memeriksa hasil src/extract_protein_features.py terhadap sumber mentahnya.
Tidak mengubah file apa pun. Exit code 0 hanya jika SEMUA test PASS.

Test yang dijalankan (sesuai checklist Tahap 3C):
  1. CSV berisi tepat 76 baris data (satu per residu).
  2. residue_id = 1..76 berurutan, chain tunggal 'A'.
  3. Sekuens di CSV identik dengan data/ubiquitin_sequence.fasta.
  4. Tidak ada duplikat residu (chain, residue_id).
  5. Tidak ada residu hilang (dibandingkan ulang dengan file struktur CIF).
  6. pLDDT di CSV konsisten dengan hasil analisis Tahap 2.
  7. Matriks PAE berukuran 76x76.
  8. Pemetaan baris/kolom PAE memakai token_res_ids dari full_data_0.json (1..76).
  9. Feature turunan PAE/contact direkalkulasi ulang dari matriks mentah dan cocok
     (mendeteksi transpose/reshape yang tidak seharusnya).
 10. Setiap kolom CSV punya definisi + unit di <prefix>_structure_features.json.

Test tambahan: jumlah atom, koordinat CA vs CIF, konsistensi file visualisasi.
"""

from __future__ import annotations

import csv
import glob
import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"
DATA_DIR = PROJECT_ROOT / "data"

CSV_PATH = RESULTS_DIR / "ubiquitin_residue_features.csv"
META_PATH = RESULTS_DIR / "ubiquitin_structure_features.json"
STAGE2_PATH = RESULTS_DIR / "ubiquitin_alphafold_structure_analysis.json"
CIF_PATH = PROJECT_ROOT / "structures" / "ubiquitin_alphafold.cif"
FASTA_PATH = DATA_DIR / "ubiquitin_sequence.fasta"
PLOT_PATHS = [
    RESULTS_DIR / "ubiquitin_plddt_per_residue.png",
    RESULTS_DIR / "ubiquitin_pae_heatmap.png",
]

TOL = 0.011  # toleransi pembulatan CSV (<= 3 desimal)

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, bool(ok), detail))
    status = "PASS" if ok else "FAIL"
    line = f"[{status}] {name}"
    if detail and not ok:
        line += f"  -> {detail}"
    print(line)


def find_full_data() -> Path:
    matches = sorted(glob.glob(str(DATA_DIR / "alphafold_downloads" / "*" / "*full_data_0.json")))
    if len(matches) != 1:
        print(f"[!] Diharapkan tepat 1 full_data_0.json, ditemukan {len(matches)}")
        sys.exit(2)
    return Path(matches[0])


def main() -> int:
    for p in (CSV_PATH, META_PATH, STAGE2_PATH, CIF_PATH, FASTA_PATH):
        if not p.is_file():
            print(f"[!] File wajib tidak ada: {p}")
            return 2

    # --- Muat semua sumber
    with CSV_PATH.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        csv_columns = reader.fieldnames or []
        rows = list(reader)
    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    stage2 = json.loads(STAGE2_PATH.read_text(encoding="utf-8"))
    full_data = json.loads(find_full_data().read_text(encoding="utf-8"))
    pae = np.asarray(full_data["pae"], dtype=float)
    contact = np.asarray(full_data["contact_probs"], dtype=float)
    token_res_ids = [int(x) for x in full_data["token_res_ids"]]
    seq_fasta = FASTA_PATH.read_text(encoding="utf-8").strip().splitlines()[1].strip().upper()

    # --- 1. Jumlah baris
    check("1. CSV berisi tepat 76 baris", len(rows) == 76, f"ditemukan {len(rows)} baris")

    # --- 2. residue_id 1..76 + chain tunggal
    ids = [int(r["residue_id"]) for r in rows]
    chains = {r["chain"] for r in rows}
    check("2. residue_id = 1..76 berurutan", ids == list(range(1, 77)), f"ids[:5]={ids[:5]}, ids[-3:]={ids[-3:]}")
    check("2b. chain tunggal 'A'", chains == {"A"}, f"chains={chains}")

    # --- 3. Sekuens identik FASTA
    seq_csv = "".join(r["one_letter_aa"] for r in rows)
    check("3. Sekuens CSV identik dengan FASTA", seq_csv == seq_fasta,
          f"csv({len(seq_csv)}) vs fasta({len(seq_fasta)})")

    # --- 4. Tidak ada duplikat
    pairs = [(r["chain"], int(r["residue_id"])) for r in rows]
    check("4. Tidak ada duplikat residu", len(pairs) == len(set(pairs)),
          f"{len(pairs) - len(set(pairs))} duplikat")

    # --- 5. Tidak ada residu hilang vs CIF (recount dari sumber)
    from Bio.PDB import MMCIFParser
    model = next(iter(MMCIFParser(QUIET=True).get_structure("ubq", str(CIF_PATH))))
    cif_ids = [int(res.id[1]) for res in model.get_residues() if res.id[0] == " "]
    missing = sorted(set(cif_ids) - set(ids))
    check("5. Tidak ada residu hilang (CSV vs CIF)",
          sorted(ids) == sorted(cif_ids) and not missing,
          f"hilang={missing[:10]}, cif={len(cif_ids)} csv={len(ids)}")

    # --- 6. pLDDT konsisten dengan Tahap 2
    plddt_csv = np.array([float(r["plddt_ca"]) for r in rows])
    s2 = stage2["chains"][0]["bfactor_plddt_stats"]
    d_mean = abs(plddt_csv.mean() - s2["mean"])
    d_min = abs(plddt_csv.min() - s2["min"])
    d_max = abs(plddt_csv.max() - s2["max"])
    check("6. pLDDT CSV konsisten dengan Tahap 2",
          max(d_mean, d_min, d_max) <= TOL,
          f"delta mean/min/max = {d_mean:.4f}/{d_min:.4f}/{d_max:.4f}")

    # --- 6b. pLDDT per-residu cocok dengan B-factor CIF (per baris)
    ca_bf = {int(res.id[1]): float(res["CA"].get_bfactor())
             for res in model.get_residues() if res.id[0] == " "}
    per_row_ok = all(abs(float(r["plddt_ca"]) - ca_bf[int(r["residue_id"])]) <= TOL for r in rows)
    check("6b. pLDDT per-residu = B-factor CA file CIF", per_row_ok)

    # --- 7. Dimensi PAE
    check("7. Matriks PAE 76x76", pae.shape == (76, 76), f"shape={pae.shape}")
    check("7b. Matriks contact_probs 76x76", contact.shape == (76, 76), f"shape={contact.shape}")

    # --- 8. Pemetaan token_res_ids
    check("8. token_res_ids = 1..76 berurutan", token_res_ids == list(range(1, 77)),
          f"awal={token_res_ids[:5]} akhir={token_res_ids[-3:]}")

    # --- 9. Rekalkulasi feature PAE/contact dari matriks mentah (anti transpose/reshape)
    n = 76
    K = 10
    row_from_raw = pae.mean(axis=1)
    col_from_raw = pae.mean(axis=0)
    local_from_raw = np.array([
        np.mean([pae[i, j] for j in range(max(0, i - K), min(n, i + K + 1)) if j != i])
        for i in range(n)
    ])
    csv_row = np.array([float(r["pae_mean_row"]) for r in rows])
    csv_col = np.array([float(r["pae_mean_col"]) for r in rows])
    csv_loc = np.array([float(r["pae_local_mean_k10"]) for r in rows])

    ok_row = np.allclose(csv_row, row_from_raw, atol=TOL)
    ok_col = np.allclose(csv_col, col_from_raw, atol=TOL)
    ok_loc = np.allclose(csv_loc, local_from_raw, atol=TOL)
    check("9. pae_mean_row / pae_mean_col / pae_local_mean_k10 = rekalkulasi matriks mentah",
          ok_row and ok_col and ok_loc,
          f"row={ok_row} col={ok_col} local={ok_loc}")

    # PAE asimetris -> pastikan baris dan kolom TIDAK tertukar/di-collapse
    asym = float(np.max(np.abs(pae - pae.T)))
    if asym > 1.0:
        not_swapped = not np.allclose(csv_row, col_from_raw, atol=TOL) or np.allclose(row_from_raw, col_from_raw, atol=TOL)
        row_col_distinct = float(np.max(np.abs(csv_row - csv_col))) > 0.05
        check("9b. Orientasi baris/kolom PAE tidak tertukar (matriks asimetris, maks |PAE-PAE.T| = %.2f)" % asym,
              not_swapped and row_col_distinct,
              f"maks|row-col| di CSV = {np.max(np.abs(csv_row - csv_col)):.4f}")
    else:
        check("9b. Matriks PAE praktis simetris - pengecekan swap tidak relevan", True, f"asym={asym:.3f}")

    # Contact features
    raw_sum = np.array([contact[i].sum() - contact[i, i] for i in range(n)])
    raw_cnt = np.array([int((contact[i] >= 0.5).sum()) - (1 if contact[i, i] >= 0.5 else 0) for i in range(n)])
    csv_sum = np.array([float(r["contact_prob_sum"]) for r in rows])
    csv_cnt = np.array([int(r["n_high_conf_contacts"]) for r in rows])
    check("9c. contact_prob_sum & n_high_conf_contacts = rekalkulasi matriks mentah",
          np.allclose(csv_sum, raw_sum, atol=1e-3) and np.array_equal(csv_cnt, raw_cnt),
          f"sum_ok={np.allclose(csv_sum, raw_sum, atol=1e-3)} cnt_ok={np.array_equal(csv_cnt, raw_cnt)}")

    # --- 10. Definisi + unit setiap kolom
    defs = meta.get("feature_definitions", {})
    missing_defs = [c for c in csv_columns
                    if c not in defs or not defs[c].get("description") or not defs[c].get("unit")]
    check("10. Semua kolom CSV punya definisi + unit di JSON", not missing_defs,
          f"tanpa definisi: {missing_defs}")
    check("10b. Daftar kolom JSON = header CSV", meta.get("columns") == csv_columns,
          "urutan/isi kolom berbeda")

    # --- Test tambahan
    n_atoms_csv = sum(int(r["n_atoms"]) for r in rows)
    n_atoms_cif = sum(1 for _ in model.get_atoms())
    check("E1. Total n_atoms CSV = jumlah atom CIF",
          n_atoms_csv == n_atoms_cif == meta.get("n_atoms"),
          f"csv={n_atoms_csv} cif={n_atoms_cif} meta={meta.get('n_atoms')}")

    res_by_id = {int(res.id[1]): res for res in model.get_residues() if res.id[0] == " "}
    ca_ok = all(
        np.allclose([float(r["ca_x"]), float(r["ca_y"]), float(r["ca_z"])],
                    res_by_id[int(r["residue_id"])]["CA"].get_coord(), atol=1e-3)
        for r in rows
    )
    check("E2. Koordinat CA CSV = koordinat CIF (semua 76 residu)", ca_ok)

    blanks = [(i, c) for i, r in enumerate(rows) for c in csv_columns if r[c] in ("", None)]
    check("E3. Tidak ada nilai kosong di CSV", not blanks, f"contoh: {blanks[:5]}")

    plots_ok = all(p.is_file() and p.stat().st_size > 10_000 for p in PLOT_PATHS)
    check("E4. Kedua file visualisasi ada dan berisi",
          plots_ok, f"{[(p.name, p.stat().st_size if p.is_file() else None) for p in PLOT_PATHS]}")

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
