#!/usr/bin/env python3
"""
extract_multi_protein_features.py - Tahap 6: ekstraksi fitur per-residu multi-protein (read-only).

Pipeline validation: menguji apakah skema extractor Tahap 3 bekerja konsisten pada
dataset multi-protein AlphaFold DB yang sudah divalidasi (Tahap 5, frozen).

Skema kolom:
  - Referensi historis : 28 kolom Tahap 3 (results/ubiquitin_residue_features.csv) - TIDAK diubah.
  - Output Tahap 6     : 3 kolom identitas protein + 26 fitur.
  - 2 kolom contact (contact_prob_sum, n_high_conf_contacts) DIKELUARKAN karena
    sumbernya (matriks contact_probs) hanya ada di output AlphaFold Server dan tidak
    tersedia di dataset AFDB yang frozen. Tidak diimputasi, tidak diproksikan, tidak
    didefinisikan ulang. Dokumentasi eksplisit ada di JSON output (schema.excluded_features).

Input (TIDAK diubah - hanya dibaca):
  - results/dataset/dataset_download_manifest.csv   (source of truth; status DOWNLOADED_VALIDATED)
  - data/alphafold_db/raw/AF-<accession>-F1-model_v6.cif
  - data/alphafold_db/raw/AF-<accession>-F1-predicted_aligned_error_v6.json
  - data/alphafold_db/metadata/api_<accession>.json (sekuens resmi + verifikasi)

Output (deterministik - tanpa timestamp, tanpa absolute local path):
  results/dataset/multi_protein_residue_features.csv
  results/dataset/multi_protein_summary.csv
  results/dataset/multi_protein_structure_features.json
  results/dataset/multi_protein_plddt_overview.png
  results/dataset/multi_protein_pae_overview.png

Batas (jangan dilanggar):
  - Ini BUKAN tahap ML: tidak ada training/model/klasifikasi/klaim biologis.
  - pLDDT per-atom dibaca dari kolom B-factor file CIF (channel resmi AFDB; definisi fitur sama).
  - Matriks PAE dipakai APA ADANYA (tanpa transpose/reshape).
  - File mentah diperiksa sha256-nya terhadap manifest; mismatch = protein dilaporkan FAIL.

Contoh:
  python src/extract_multi_protein_features.py
  python src/extract_multi_protein_features.py --outdir tmp_out
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Reuse definisi & konstanta Tahap 3 APA ADANYA (file Tahap 3 tidak diubah).
from extract_protein_features import (  # noqa: E402
    AA_TYPE,
    BACKBONE_ATOMS,
    CHARGE_PH7,
    COLUMNS as STAGE3_COLUMNS,
    FEATURE_DEFINITIONS as STAGE3_FEATURE_DEFINITIONS,
    KD_HYDROPATHY,
    PAE_LOCAL_WINDOW,
)

PROJECT_ROOT = SRC_DIR.parent
DEFAULT_MANIFEST = PROJECT_ROOT / "results" / "dataset" / "dataset_download_manifest.csv"
DEFAULT_RAW_DIR = PROJECT_ROOT / "data" / "alphafold_db" / "raw"
DEFAULT_META_DIR = PROJECT_ROOT / "data" / "alphafold_db" / "metadata"
DEFAULT_OUTDIR = PROJECT_ROOT / "results" / "dataset"

# 2 kolom contact dikeluarkan: sumber (contact_probs) hanya ada di output AlphaFold Server.
CONTACT_COLUMNS = ("contact_prob_sum", "n_high_conf_contacts")
ID_COLUMNS = ("protein_id", "uniprot_accession", "afdb_id")
FEATURE_COLUMNS = [c for c in STAGE3_COLUMNS if c not in CONTACT_COLUMNS]  # 26 fitur
OUTPUT_COLUMNS = list(ID_COLUMNS) + FEATURE_COLUMNS

EXPECTED_ACCESSIONS = ("P99999", "P61626", "P0DP23", "P61823", "P02144", "P00441", "P42212")
EXPECTED_PROTEIN_COUNT = 7

SUMMARY_COLUMNS = [
    "protein_id", "uniprot_accession", "afdb_id", "sequence_length",
    "observed_residue_count", "chain_count",
    "mean_plddt", "min_plddt", "max_plddt",
    "mean_pae", "min_pae", "max_pae",
    "feature_row_count", "status", "notes",
]

EXCLUDED_NOTE_EN = (
    "Stage 3 reference schema contains 28 columns. Two contact-derived columns depend on "
    "AlphaFold Server `contact_probs`, which are not present in the frozen AlphaFold DB "
    "dataset. They are therefore excluded from the Stage 6 AFDB feature table rather than "
    "imputed, approximated, or silently redefined."
)


# ---------------------------------------------------------------------------
# Utilitas
# ---------------------------------------------------------------------------

def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel_posix(path: Path) -> str:
    """Path relatif (POSIX) terhadap PROJECT_ROOT; fallback absolut POSIX bila di luar root."""
    resolved = path.resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def load_manifest(manifest_path: Path) -> list[dict]:
    """Baris status DOWNLOADED_VALIDATED; berhenti eksplisit bila tidak sesuai 7 protein yang disetujui."""
    rows = [r for r in read_csv(manifest_path) if r.get("status") == "DOWNLOADED_VALIDATED"]
    if len(rows) != EXPECTED_PROTEIN_COUNT:
        raise SystemExit(
            f"[!] Diharapkan {EXPECTED_PROTEIN_COUNT} protein DOWNLOADED_VALIDATED di manifest, "
            f"ditemukan {len(rows)}. Berhenti - jangan memperbaiki / mengganti protein diam-diam."
        )
    accs = [r["uniprot_accession"] for r in rows]
    if len(set(accs)) != len(accs):
        raise SystemExit("[!] Ada accession duplikat di manifest.")
    if set(accs) != set(EXPECTED_ACCESSIONS):
        raise SystemExit(
            "[!] Himpunan protein manifest tidak sama dengan daftar yang disetujui Tahap 6.\n"
            f"    manifest : {sorted(accs)}\n    disetujui: {sorted(EXPECTED_ACCESSIONS)}\n"
            "    Berhenti - jangan menambah protein lain."
        )
    return rows


def parse_pae_doc(pae_path: Path, n_res: int, acc: str) -> np.ndarray:
    """Ekstrak matriks PAE via format yang diterima eksplisit (tanpa transpose/reshape)."""
    doc = json.loads(pae_path.read_text(encoding="utf-8"))
    matrix = None
    if isinstance(doc, dict) and "predicted_aligned_error" in doc:
        matrix = doc["predicted_aligned_error"]
    elif isinstance(doc, list) and doc and isinstance(doc[0], dict) and "predicted_aligned_error" in doc[0]:
        matrix = doc[0]["predicted_aligned_error"]
    elif isinstance(doc, list) and doc and all(isinstance(r, list) for r in doc):
        matrix = doc
    if matrix is None:
        raise ValueError(f"{acc}: format PAE tidak dikenali")
    pae = np.asarray(matrix, dtype=float)
    if pae.shape != (n_res, n_res):
        raise ValueError(f"{acc}: shape PAE {pae.shape} != ({n_res}, {n_res})")
    return pae


# ---------------------------------------------------------------------------
# Ekstraksi per protein
# ---------------------------------------------------------------------------

def process_protein(row: dict, raw_dir: Path, meta_dir: Path):
    """Proses satu protein. Return (rows, summary_row, protein_doc, pae_matrix).

    Raise ValueError dengan pesan eksplisit (mengandung accession) bila ada masalah;
    tidak ada perbaikan diam-diam.
    """
    from Bio.PDB import MMCIFParser
    from Bio.PDB.Polypeptide import protein_letters_3to1

    acc = row["uniprot_accession"]
    protein_id = row["protein_id"]
    afdb_id = row["afdb_id"]
    expected_len = int(row["sequence_length"])

    struct_path = raw_dir / row["structure_filename"]
    pae_path = raw_dir / row["pae_filename"]
    api_path = meta_dir / f"api_{acc}.json"
    for p in (struct_path, pae_path, api_path):
        if not p.is_file():
            raise ValueError(f"{acc}: file tidak ada: {p.name}")

    # -- Integritas: file mentah harus identik dengan yang divalidasi Tahap 5 (frozen).
    for p, expected_sha, label in (
        (struct_path, row["structure_sha256"], "CIF"),
        (pae_path, row["pae_sha256"], "PAE"),
    ):
        actual = sha256_of(p)
        if actual != expected_sha:
            raise ValueError(
                f"{acc}: sha256 {label} TIDAK cocok dengan manifest "
                f"(diharapkan {expected_sha[:12]}..., dihitung {actual[:12]}...) - file mentah berubah?"
            )

    # -- Metadata resmi (sekuens pembanding + identitas)
    api = json.loads(api_path.read_text(encoding="utf-8"))
    api = api[0] if isinstance(api, list) else api
    if api.get("uniprotAccession") != acc:
        raise ValueError(f"{acc}: uniprotAccession API = {api.get('uniprotAccession')!r}")
    if api.get("entryId") != afdb_id:
        raise ValueError(f"{acc}: entryId API {api.get('entryId')!r} != manifest {afdb_id!r}")
    if str(api.get("latestVersion")) != str(row["afdb_version"]):
        raise ValueError(f"{acc}: latestVersion API {api.get('latestVersion')} != manifest {row['afdb_version']}")
    official_seq = str(api["uniprotSequence"]).upper()
    chain_api = str(api.get("chainId", ""))

    # -- Parse CIF
    structure = MMCIFParser(QUIET=True).get_structure(protein_id, str(struct_path))
    models = list(structure.get_models())
    if len(models) != 1:
        raise ValueError(f"{acc}: jumlah model = {len(models)} (harus 1)")
    model = models[0]
    chains = list(model.get_chains())
    if len(chains) != 1:
        raise ValueError(f"{acc}: jumlah chain = {len(chains)} (harus 1)")
    chain_id = chains[0].id
    if chain_api and chain_id != chain_api:
        raise ValueError(f"{acc}: chain CIF {chain_id!r} != chainId API {chain_api!r}")
    het = [r for r in model.get_residues() if r.id[0] != " "]
    if het:
        raise ValueError(f"{acc}: ada {len(het)} HETATM - tidak ditangani (protein murni saja)")
    residues = [r for r in chains[0].get_residues() if r.id[0] == " "]
    n_res = len(residues)

    # -- Sekuens dari struktur + validasi (TIDAK auto-perbaiki)
    seq_chars, unknown = [], []
    for res in residues:
        name3 = res.get_resname().strip().upper()
        aa = protein_letters_3to1.get(name3)
        if aa is None:
            unknown.append(name3)
        seq_chars.append(aa or "X")
        if "CA" not in res:
            raise ValueError(f"{acc}: residu {res.id[1]} tidak punya atom CA")
    if unknown:
        raise ValueError(f"{acc}: residu tidak dikenali: {sorted(set(unknown))} - berhenti, jangan menebak")
    seq_struct = "".join(seq_chars)
    if seq_struct != official_seq:
        raise ValueError(
            f"{acc}: sekuens CIF ({len(seq_struct)} aa) != uniprotSequence API ({len(official_seq)} aa)"
        )
    if n_res != expected_len:
        raise ValueError(f"{acc}: jumlah residu {n_res} != sequence_length manifest {expected_len}")

    # -- Penomoran residu: diverifikasi per protein (tidak diasumsikan universal)
    nums = [int(r.id[1]) for r in residues]
    if nums != list(range(1, n_res + 1)):
        raise ValueError(
            f"{acc}: penomoran residu bukan 1..{n_res} berurutan (awal {nums[:5]}, akhir {nums[-3:]}) - "
            "pemetaan PAE ambigu, berhenti"
        )

    # -- Checksum sekuens resmi AFDB (MD5)
    md5_ok = hashlib.md5(seq_struct.encode("ascii")).hexdigest() == str(api.get("sequenceChecksum", ""))
    if not md5_ok:
        raise ValueError(f"{acc}: sequenceChecksum MD5 API tidak cocok dengan sekuens struktur")

    # -- pLDDT per-atom dari kolom B-factor CIF (channel resmi AFDB)
    all_bf = np.array([a.get_bfactor() for a in model.get_atoms()], dtype=float)
    if all_bf.size and (all_bf.min() < 0.0 or all_bf.max() > 100.0):
        raise ValueError(
            f"{acc}: B-factor di luar rentang pLDDT [0,100]: [{all_bf.min():.2f}, {all_bf.max():.2f}] - "
            "asumsi channel pLDDT tidak berlaku, berhenti"
        )

    # -- PAE
    pae = parse_pae_doc(pae_path, n_res, acc)

    # -- Baris per-residu (26 fitur; lihat FEATURE_COLUMNS)
    rows = []
    for pos, res in enumerate(residues):
        name3 = res.get_resname().strip().upper()
        aa = protein_letters_3to1[name3]
        atom_plddt = np.array([a.get_bfactor() for a in res], dtype=float)
        coords = np.array([a.get_coord() for a in res])
        centroid = coords.mean(axis=0)
        ca = res["CA"]
        backbone_present = sum(1 for an in BACKBONE_ATOMS if an in res)

        i = pos  # penomoran 1..N sudah diverifikasi -> indeks == posisi
        lo, hi = max(0, i - PAE_LOCAL_WINDOW), min(n_res, i + PAE_LOCAL_WINDOW + 1)
        local_vals = [pae[i, j] for j in range(lo, hi) if j != i]

        rows.append({
            "protein_id": protein_id,
            "uniprot_accession": acc,
            "afdb_id": afdb_id,
            "chain": chain_id,
            "residue_id": int(res.id[1]),
            "residue_name": name3,
            "one_letter_aa": aa,
            "sequence_position": pos + 1,
            "sequence_length": n_res,
            "amino_acid_type": AA_TYPE.get(aa, "unknown"),
            "hydropathy_kd": KD_HYDROPATHY.get(aa, ""),
            "charge_ph7": CHARGE_PH7.get(aa, 0),
            "ca_x": round(float(ca.get_coord()[0]), 3),
            "ca_y": round(float(ca.get_coord()[1]), 3),
            "ca_z": round(float(ca.get_coord()[2]), 3),
            "n_atoms": len(res),
            "n_backbone_atoms": backbone_present,
            "has_full_backbone": backbone_present == len(BACKBONE_ATOMS),
            "centroid_x": round(float(centroid[0]), 3),
            "centroid_y": round(float(centroid[1]), 3),
            "centroid_z": round(float(centroid[2]), 3),
            "plddt_ca": round(float(ca.get_bfactor()), 2),
            "plddt_atom_mean": round(float(atom_plddt.mean()), 2),
            "plddt_atom_min": round(float(atom_plddt.min()), 2),
            "plddt_atom_max": round(float(atom_plddt.max()), 2),
            "plddt_atom_std": round(float(atom_plddt.std()), 3),
            "pae_mean_row": round(float(pae[i].mean()), 3),
            "pae_mean_col": round(float(pae[:, i].mean()), 3),
            "pae_local_mean_k10": round(float(np.mean(local_vals)), 3),
        })

    # -- Statistik tingkat-protein (dari nilai yang sama dengan CSV -> konsisten)
    plddt_ca = np.array([r["plddt_ca"] for r in rows], dtype=float)
    flat = pae.flatten()
    all_coords = np.array([a.get_coord() for a in model.get_atoms()])
    bbox = all_coords.max(axis=0) - all_coords.min(axis=0)

    summary = {
        "protein_id": protein_id,
        "uniprot_accession": acc,
        "afdb_id": afdb_id,
        "sequence_length": expected_len,
        "observed_residue_count": n_res,
        "chain_count": len(chains),
        "mean_plddt": round(float(plddt_ca.mean()), 3),
        "min_plddt": round(float(plddt_ca.min()), 3),
        "max_plddt": round(float(plddt_ca.max()), 3),
        "mean_pae": round(float(flat.mean()), 3),
        "min_pae": round(float(flat.min()), 3),
        "max_pae": round(float(flat.max()), 3),
        "feature_row_count": len(rows),
        "status": "PASS",
        "notes": "",
    }

    protein_doc = {
        "protein_id": protein_id,
        "uniprot_accession": acc,
        "afdb_id": afdb_id,
        "afdb_version": row["afdb_version"],
        "inputs": {
            "structure": {"path": rel_posix(struct_path), "sha256": sha256_of(struct_path)},
            "pae_doc": {"path": rel_posix(pae_path), "sha256": sha256_of(pae_path)},
            "api_metadata": {"path": rel_posix(api_path), "sha256": sha256_of(api_path)},
        },
        "n_residues": n_res,
        "n_chains": len(chains),
        "chain_ids": sorted({r["chain"] for r in rows}),
        "n_atoms": int(all_bf.size),
        "sequence": seq_struct,
        "residue_numbering": "1..N berurutan (diverifikasi); residue_id == sequence_position",
        "sequence_checksum_md5_match": True,
        "plddt": {
            "ca_mean": round(float(plddt_ca.mean()), 3),
            "ca_min": round(float(plddt_ca.min()), 3),
            "ca_max": round(float(plddt_ca.max()), 3),
            "ca_frac_ge_70": round(float((plddt_ca >= 70).mean()), 4),
            "ca_frac_ge_90": round(float((plddt_ca >= 90).mean()), 4),
            "atom_mean_global": round(float(all_bf.mean()), 3),
            "source_channel": ("kolom B-factor file CIF (channel resmi AFDB; pLDDT disimpan di B-factor). "
                               "Definisi fitur Tahap 3 tidak diubah."),
        },
        "pae": {
            "shape": [int(pae.shape[0]), int(pae.shape[1])],
            "min": round(float(flat.min()), 3),
            "max": round(float(flat.max()), 3),
            "mean": round(float(flat.mean()), 3),
            "median": round(float(np.median(flat)), 3),
            "percentiles": {str(p): round(float(np.percentile(flat, p)), 3) for p in (1, 5, 25, 50, 75, 95, 99)},
            "orientation_note": ("Matriks dipakai apa adanya dari paeDocUrl AFDB (tanpa transpose/reshape). "
                                 "Baris i dan kolom j = posisi residu 1..N (penomoran terverifikasi). "
                                 "Interpretasi umum AlphaFold: elemen [i][j] = estimasi error posisi residu i "
                                 "bila struktur di-align pada residu j."),
        },
        "structure_bbox_angstrom": [round(float(v), 2) for v in bbox],
        "status": "PASS",
    }
    return rows, summary, protein_doc, pae


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def write_csv(rows: list[dict], columns: list[str], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def make_overview_plots(grouped_rows: dict, protein_docs: list[dict], pae_matrices: list,
                        outdir: Path) -> list[Path]:
    """2 PNG ringkas (bukan fokus tahap ini): pLDDT overview + PAE overview. Deterministik."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    saved = []
    cmap = plt.get_cmap("tab10")

    # -- pLDDT overview
    fig, ax = plt.subplots(figsize=(12.0, 5.0))
    for k, doc in enumerate(protein_docs):
        acc = doc["uniprot_accession"]
        ys = [float(r["plddt_ca"]) for r in grouped_rows[doc["protein_id"]]]
        ax.plot(range(1, len(ys) + 1), ys, linewidth=1.2, color=cmap(k % 10),
                label=f"{acc} ({len(ys)} aa)")
    ax.axhline(90, color="#2ca02c", linestyle="--", linewidth=1, label="ambang 90 (sangat tinggi)")
    ax.axhline(70, color="#ff7f0e", linestyle="--", linewidth=1, label="ambang 70 (tinggi)")
    ax.set_xlabel("Posisi residu dalam protein")
    ax.set_ylabel("pLDDT atom CA (0-100)")
    ax.set_title("pLDDT per-residu (CA) - 7 protein AlphaFold DB v6 (prediksi)")
    ax.set_ylim(0, 100)
    ax.legend(loc="lower left", fontsize=8, ncol=3)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    p1 = outdir / "multi_protein_plddt_overview.png"
    fig.savefig(p1, dpi=150)
    plt.close(fig)
    saved.append(p1)

    # -- PAE overview (grid)
    n = len(protein_docs)
    ncols, nrows = 2, (n + 1) // 2
    fig, axes = plt.subplots(nrows, ncols, figsize=(9.5, 3.5 * nrows))
    axes_flat = list(np.ravel(np.array(axes, dtype=object)))
    im = None
    vmax = 32.0  # ceil dari max matriks 7 protein (31) + margin; skala bersama agar sebanding
    for k, (doc, pae) in enumerate(zip(protein_docs, pae_matrices)):
        ax = axes_flat[k]
        acc = doc["uniprot_accession"]
        im = ax.imshow(pae, origin="upper", aspect="equal", cmap="magma", vmin=0.0, vmax=vmax)
        size = pae.shape[0]
        ticks = [0, size - 1]
        ax.set_xticks(ticks)
        ax.set_xticklabels([str(t + 1) for t in ticks], fontsize=7)
        ax.set_yticks(ticks)
        ax.set_yticklabels([str(t + 1) for t in ticks], fontsize=7)
        ax.set_title(f"{acc} ({size}x{size})", fontsize=10)
    for k in range(n, len(axes_flat)):
        axes_flat[k].set_visible(False)
    fig.suptitle("PAE per protein - AlphaFold DB v6 (prediksi, Angstrom; matriks apa adanya)", y=1.0)
    fig.tight_layout()
    cax = fig.add_axes([0.92, 0.15, 0.015, 0.7])
    fig.colorbar(im, cax=cax, label="PAE (Angstrom)")
    p2 = outdir / "multi_protein_pae_overview.png"
    fig.savefig(p2, dpi=150)
    plt.close(fig)
    saved.append(p2)

    return saved


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="extract_multi_protein_features.py",
        description="Ekstraksi fitur per-residu multi-protein dari dataset AFDB tervalidasi (read-only).",
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--meta-dir", type=Path, default=DEFAULT_META_DIR)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    args = parser.parse_args(argv)

    if not args.manifest.is_file():
        print(f"[!] Manifest tidak ditemukan: {args.manifest}")
        return 2

    rows_manifest = load_manifest(args.manifest)
    print(f"[i] Manifest : {rel_posix(args.manifest)} ({len(rows_manifest)} protein DOWNLOADED_VALIDATED)")
    print(f"[i] Skema    : {len(ID_COLUMNS)} identifier + {len(FEATURE_COLUMNS)} fitur "
          f"(referensi Tahap 3: {len(STAGE3_COLUMNS)} kolom; 2 kolom contact dikeluarkan - tidak tersedia di AFDB)")

    all_rows, summaries, protein_docs, pae_matrices = [], [], [], []
    failed: list[tuple[str, str]] = []

    for row in rows_manifest:
        acc = row["uniprot_accession"]
        try:
            rows, summary, pdoc, pae = process_protein(row, args.raw_dir, args.meta_dir)
        except Exception as exc:  # dilaporkan eksplisit per protein; tidak mengganti/menambal diam-diam
            reason = f"{type(exc).__name__}: {exc}"
            failed.append((acc, reason))
            print(f"[FAIL] {acc}: {reason}")
            summaries.append({
                "protein_id": row["protein_id"], "uniprot_accession": acc, "afdb_id": row["afdb_id"],
                "sequence_length": row["sequence_length"],
                "observed_residue_count": "", "chain_count": "",
                "mean_plddt": "", "min_plddt": "", "max_plddt": "",
                "mean_pae": "", "min_pae": "", "max_pae": "",
                "feature_row_count": 0, "status": "FAIL", "notes": reason,
            })
            continue
        all_rows.extend(rows)
        summaries.append(summary)
        protein_docs.append(pdoc)
        pae_matrices.append(pae)
        print(f"[OK]   {acc}: {len(rows)} residu | PAE {pae.shape[0]}x{pae.shape[1]} | "
              f"mean pLDDT {summary['mean_plddt']} | PAE max {summary['max_pae']}")

    expected_total = sum(int(r["sequence_length"]) for r in rows_manifest)
    if not failed and len(all_rows) != expected_total:
        reason = f"total rows {len(all_rows)} != expected {expected_total}"
        failed.append(("TOTAL", reason))
        print(f"[FAIL] {reason}")

    args.outdir.mkdir(parents=True, exist_ok=True)

    # -- CSV per-residu
    residue_csv = args.outdir / "multi_protein_residue_features.csv"
    write_csv(all_rows, OUTPUT_COLUMNS, residue_csv)

    # -- CSV summary per-protein
    summary_csv = args.outdir / "multi_protein_summary.csv"
    write_csv(summaries, SUMMARY_COLUMNS, summary_csv)

    # -- JSON struktur & skema
    grouped_rows: dict[str, list[dict]] = {}
    for r in all_rows:
        grouped_rows.setdefault(r["protein_id"], []).append(r)

    doc = {
        "dataset": "multi-protein residue-level features (AlphaFold DB, 7 protein, v6)",
        "generator": "src/extract_multi_protein_features.py",
        "protein_count": len(protein_docs),
        "total_residue_rows": len(all_rows),
        "schema": {
            "historical_reference": {
                "file": "results/ubiquitin_residue_features.csv",
                "columns": list(STAGE3_COLUMNS),
                "note": EXCLUDED_NOTE_EN,
            },
            "identifier_columns": list(ID_COLUMNS),
            "identifier_column_notes": {
                "protein_id": "ID protein internal project (source of truth: manifest Tahap 5)",
                "uniprot_accession": "accession UniProtKB",
                "afdb_id": "entry ID AlphaFold DB (AF-<accession>-F1)",
            },
            "feature_columns": list(FEATURE_COLUMNS),
            "output_columns": list(OUTPUT_COLUMNS),
            "feature_definitions": {c: STAGE3_FEATURE_DEFINITIONS[c] for c in FEATURE_COLUMNS},
            "excluded_features": [
                {
                    "name": "contact_prob_sum",
                    "stage3_definition": STAGE3_FEATURE_DEFINITIONS["contact_prob_sum"]["description"],
                    "stage3_unit": STAGE3_FEATURE_DEFINITIONS["contact_prob_sum"]["unit"],
                    "source_channel": "contact_probs (hanya di output AlphaFold Server full_data json)",
                    "reason": ("Tidak tersedia di dataset AFDB yang frozen (AFDB tidak menyediakan matriks "
                               "contact_probs); dikeluarkan dari tabel Tahap 6 - bukan diimputasi/diproksikan."),
                },
                {
                    "name": "n_high_conf_contacts",
                    "stage3_definition": STAGE3_FEATURE_DEFINITIONS["n_high_conf_contacts"]["description"],
                    "stage3_unit": STAGE3_FEATURE_DEFINITIONS["n_high_conf_contacts"]["unit"],
                    "stage3_threshold": 0.50,
                    "source_channel": "contact_probs (hanya di output AlphaFold Server full_data json)",
                    "reason": ("Tidak tersedia di dataset AFDB yang frozen (AFDB tidak menyediakan matriks "
                               "contact_probs); dikeluarkan dari tabel Tahap 6 - bukan diimputasi/diproksikan."),
                },
            ],
            "source_channel_notes": {
                "plddt": ("plddt_ca & plddt_atom_* dibaca dari kolom B-factor file CIF (channel resmi AFDB). "
                          "Definisi fitur tidak berubah; verifikasi: mean pLDDT CA per protein cocok dengan "
                          "globalMetricValue API (selisih <= 0.03). Catatan granularitas: file CIF AFDB "
                          "menulis pLDDT per-residu ke SEMUA atom residu tersebut (std antar-atom = 0 di "
                          "dataset ini) - berbeda dari full_data AlphaFold Server yang menyimpan pLDDT "
                          "per-atom secara terpisah."),
                "pae": "Matriks PAE dari paeDocUrl AFDB dipakai apa adanya (tanpa transpose/reshape).",
                "sequence": "Sekuens struktur diverifikasi terhadap uniprotSequence API + sequenceChecksum MD5.",
            },
        },
        "input_manifest": {"path": rel_posix(args.manifest), "sha256": sha256_of(args.manifest)},
        "proteins": protein_docs,
        "notes": [
            "Dataset ini hanya berisi 7 protein AFDB yang disetujui pada manifest Tahap 5 (frozen); tidak ada protein tambahan.",
            "Semua fitur adalah turunan PREDIKSI AlphaFold DB v6; tidak ada data eksperimen.",
            "2 fitur turunan contact dari skema Tahap 3 (28 kolom) tidak disertakan karena sumbernya "
            "(contact_probs) tidak tersedia di AFDB - lihat schema.excluded_features.",
            "pLDDT tinggi / PAE rendah = keyakinan MODEL, bukan bukti fungsi atau kebenaran biologis.",
            "Ini pipeline validation, bukan tahap ML dan bukan klaim biologis.",
        ],
    }
    json_path = args.outdir / "multi_protein_structure_features.json"
    json_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")

    plots = make_overview_plots(grouped_rows, protein_docs, pae_matrices, args.outdir)

    print(f"\n[i] Total: {len(protein_docs)}/{EXPECTED_PROTEIN_COUNT} protein, {len(all_rows)} baris residu "
          f"(expected {expected_total}), {len(OUTPUT_COLUMNS)} kolom ({len(ID_COLUMNS)} identifier + {len(FEATURE_COLUMNS)} fitur)")
    print("Hasil disimpan:")
    for p in (residue_csv, summary_csv, json_path, *plots):
        print(f"  - {p}")

    if failed:
        print("\n" + "=" * 68)
        print(f"HASIL: {len(failed)} protein GAGAL - dilaporkan eksplisit (tanpa penggantian/perbaikan diam-diam):")
        for acc, reason in failed:
            print(f"  - {acc}: {reason}")
        return 1

    print("\n" + "-" * 68)
    print("Catatan: fitur dari PREDIKSI AlphaFold DB v6 - keyakinan model, bukan bukti biologis.")
    print("Pipeline validation selesai; tidak ada training/model ML di tahap ini.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
