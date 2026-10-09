#!/usr/bin/env python3
"""
extract_protein_features.py - Tahap 3: ekstraksi feature per-residue (read-only).

Mengubah struktur AlphaFold + sekuens + confidence menjadi dataset numerik
per-residue (76 baris untuk ubiquitin) sebagai fondasi tahap dataset/ML.

Input (TIDAK diubah - hanya dibaca):
  - structures/ubiquitin_alphafold.cif        struktur mmCIF (Biopython MMCIFParser)
  - data/alphafold_downloads/**/<job>_full_data_0.json
        - atom_plddts   : pLDDT per atom (urutan sama dengan urutan atom di CIF)
        - pae           : matriks predicted alignment error, token-level
        - contact_probs : matriks probabilitas kontak antar-token
        - token_res_ids : pemetaan indeks token -> nomor residu
  - data/ubiquitin_sequence.fasta             sekuens referensi

Output:
  results/<prefix>_residue_features.csv       satu baris per residue
  results/<prefix>_structure_features.json    metadata + definisi kolom + statistik
  results/<prefix>_plddt_per_residue.png
  results/<prefix>_pae_heatmap.png

Batas (jangan dilanggar):
  - Ini feature extraction dari PREDIKSI AlphaFold, bukan validasi biologis.
  - Tidak ada training ML, docking, MD, atau klaim fungsi biologis di sini.
  - Matriks PAE/contact dipakai APA ADANYA; pemetaan baris/kolom memakai
    token_res_ids dari full_data json yang sama (tidak ada transpose/reshape).

Contoh:
  python src/extract_protein_features.py
  python src/extract_protein_features.py --prefix ubiquitin --outdir results
"""

from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STRUCTURES_DIR = PROJECT_ROOT / "structures"
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
DOWNLOADS_DIR = DATA_DIR / "alphafold_downloads"

DEFAULT_STRUCTURE = STRUCTURES_DIR / "ubiquitin_alphafold.cif"
DEFAULT_FASTA = DATA_DIR / "ubiquitin_sequence.fasta"

BACKBONE_ATOMS = ("N", "CA", "C", "O")
PAE_LOCAL_WINDOW = 10        # k untuk pae_local_mean_k10 (|i-j| <= k, j != i)
CONTACT_THRESHOLD = 0.50     # ambang eksplisit untuk n_high_conf_contacts

# Kategori sifat asam amino (pengelompokan sederhana; lihat definisi di JSON).
AA_TYPE = {
    "A": "nonpolar", "V": "nonpolar", "L": "nonpolar", "I": "nonpolar", "M": "nonpolar",
    "F": "aromatic", "W": "aromatic", "Y": "aromatic",
    "S": "polar", "T": "polar", "C": "polar", "N": "polar", "Q": "polar",
    "K": "basic", "R": "basic", "H": "basic",
    "D": "acidic", "E": "acidic",
    "G": "special", "P": "special",
}

# Indeks hidropati Kyte & Doolittle (1982), tabel standar.
KD_HYDROPATHY = {
    "A": 1.8, "R": -4.5, "N": -3.5, "D": -3.5, "C": 2.5, "Q": -3.5, "E": -3.5,
    "G": -0.4, "H": -3.2, "I": 4.5, "L": 3.8, "K": -3.9, "M": 1.9, "F": 2.8,
    "P": -1.6, "S": -0.8, "T": -0.7, "W": -0.9, "Y": -1.3, "V": 4.2,
}

# Muatan formal sidechain pada pH 7 (penyederhanaan; H dianggap netral).
CHARGE_PH7 = {"D": -1, "E": -1, "K": 1, "R": 1}

COLUMNS = [
    # identitas
    "chain", "residue_id", "residue_name", "one_letter_aa",
    # sekuens
    "sequence_position", "sequence_length", "amino_acid_type",
    "hydropathy_kd", "charge_ph7",
    # struktur
    "ca_x", "ca_y", "ca_z",
    "n_atoms", "n_backbone_atoms", "has_full_backbone",
    "centroid_x", "centroid_y", "centroid_z",
    # confidence
    "plddt_ca", "plddt_atom_mean", "plddt_atom_min", "plddt_atom_max", "plddt_atom_std",
    # turunan PAE (rumus eksplisit - lihat FEATURE_DEFINITIONS)
    "pae_mean_row", "pae_mean_col", "pae_local_mean_k10",
    # turunan contact_probs (ambang eksplisit 0.50)
    "contact_prob_sum", "n_high_conf_contacts",
]

FEATURE_DEFINITIONS: dict[str, dict[str, str]] = {
    "chain": {"description": "ID chain (author) di file mmCIF", "unit": "-"},
    "residue_id": {"description": "nomor residu sesuai penomoran di file struktur", "unit": "-"},
    "residue_name": {"description": "nama residu 3-huruf", "unit": "-"},
    "one_letter_aa": {"description": "kode asam amino 1-huruf", "unit": "-"},
    "sequence_position": {"description": "posisi 1-based dalam urutan residu protein (referensi FASTA)", "unit": "-"},
    "sequence_length": {"description": "panjang total sekuens protein", "unit": "residu"},
    "amino_acid_type": {"description": "kategori sifat: nonpolar/aromatic/polar/basic/acidic/special (pengelompokan sederhana)", "unit": "-"},
    "hydropathy_kd": {"description": "indeks hidropati Kyte-Doolittle (1982), tabel standar", "unit": "skor tanpa satuan"},
    "charge_ph7": {"description": "muatan formal sidechain pada pH 7 (D,E=-1; K,R=+1; lainnya 0; H disederhanakan netral)", "unit": "e (muatan elementer)"},
    "ca_x": {"description": "koordinat X atom CA residu", "unit": "Angstrom"},
    "ca_y": {"description": "koordinat Y atom CA residu", "unit": "Angstrom"},
    "ca_z": {"description": "koordinat Z atom CA residu", "unit": "Angstrom"},
    "n_atoms": {"description": "jumlah atom (berat) dalam residu, dari file struktur", "unit": "atom"},
    "n_backbone_atoms": {"description": "jumlah atom backbone yang ada (N, CA, C, O)", "unit": "atom"},
    "has_full_backbone": {"description": "True jika atom N, CA, C, O lengkap keempatnya", "unit": "boolean"},
    "centroid_x": {"description": "koordinat X centroid residu = rata-rata semua koordinat atom (unweighted)", "unit": "Angstrom"},
    "centroid_y": {"description": "koordinat Y centroid residu = rata-rata semua koordinat atom (unweighted)", "unit": "Angstrom"},
    "centroid_z": {"description": "koordinat Z centroid residu = rata-rata semua koordinat atom (unweighted)", "unit": "Angstrom"},
    "plddt_ca": {"description": "pLDDT atom CA, dibaca dari kolom B-factor file mmCIF (konvensi output AlphaFold)", "unit": "0-100"},
    "plddt_atom_mean": {"description": "rata-rata pLDDT semua atom residu, dari atom_plddts di full_data json", "unit": "0-100"},
    "plddt_atom_min": {"description": "pLDDT minimum antar atom residu (full_data json)", "unit": "0-100"},
    "plddt_atom_max": {"description": "pLDDT maksimum antar atom residu (full_data json)", "unit": "0-100"},
    "plddt_atom_std": {"description": "simpangan baku pLDDT antar atom residu (full_data json)", "unit": "0-100"},
    "pae_mean_row": {"description": "mean_j PAE[i][j] untuk residu ini (baris i matriks PAE apa adanya)", "unit": "Angstrom"},
    "pae_mean_col": {"description": "mean_j PAE[j][i] untuk residu ini (kolom i matriks PAE apa adanya)", "unit": "Angstrom"},
    "pae_local_mean_k10": {"description": "mean PAE[i][j] untuk j dengan |i-j|<=10, j!=i (error lokal residu ini terhadap tetangga sekuens)", "unit": "Angstrom"},
    "contact_prob_sum": {"description": "sum_j!=i contact_probs[i][j] (total probabilitas kontak prediksi, tanpa diagonal)", "unit": "probabilitas (0-1), dijumlahkan"},
    "n_high_conf_contacts": {"description": "jumlah j!=i dengan contact_probs[i][j] >= 0.50 (ambang dipilih eksplisit; ini prediksi, bukan kontak eksperimental)", "unit": "pasangan residu"},
}


# ---------------------------------------------------------------------------
# Utilitas
# ---------------------------------------------------------------------------

def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_full_data(downloads_dir: Path, explicit: Path | None) -> Path:
    """Cari file <job>_full_data_0.json (model_0) di data/alphafold_downloads/."""
    if explicit is not None:
        return Path(explicit)
    matches = sorted(glob.glob(str(downloads_dir / "*" / "*full_data_0.json")))
    if len(matches) != 1:
        raise SystemExit(
            f"[!] Diharapkan tepat 1 file *full_data_0.json di {downloads_dir}, "
            f"ditemukan {len(matches)}: {matches}\n    Pakai --full-data <path> untuk memilih eksplisit."
        )
    return Path(matches[0])


def load_reference_sequence(fasta_path: Path) -> str:
    from Bio import SeqIO

    with fasta_path.open(encoding="utf-8") as fh:
        record = next(SeqIO.parse(fh, "fasta"), None)
    if record is None:
        raise SystemExit(f"[!] Tidak ada record FASTA di {fasta_path}")
    return str(record.seq).upper().strip()


# ---------------------------------------------------------------------------
# Ekstraksi
# ---------------------------------------------------------------------------

def extract_rows(structure_path: Path, full_data_path: Path, fasta_path: Path):
    """Baca ketiga sumber, kembalikan (rows, meta, extras). Tidak menulis apa pun."""
    from Bio.PDB import MMCIFParser
    from Bio.PDB.Polypeptide import protein_letters_3to1

    seq_ref = load_reference_sequence(fasta_path)

    structure = MMCIFParser(QUIET=True).get_structure(structure_path.stem, str(structure_path))
    model = next(iter(structure))  # model pertama (AF Server: satu model per file)

    full_data = json.loads(full_data_path.read_text(encoding="utf-8"))
    for key in ("atom_plddts", "atom_chain_ids", "pae", "contact_probs", "token_res_ids"):
        if key not in full_data:
            raise SystemExit(f"[!] Key '{key}' tidak ada di {full_data_path.name} - format tidak sesuai.")
    atom_plddts = np.asarray(full_data["atom_plddts"], dtype=float)
    pae = np.asarray(full_data["pae"], dtype=float)
    contact = np.asarray(full_data["contact_probs"], dtype=float)
    token_res_ids = [int(x) for x in full_data["token_res_ids"]]

    # -- Kumpulkan residu protein dan atomnya
    all_atoms = list(model.get_atoms())
    n_hetatm = sum(1 for r in model.get_residues() if r.id[0] != " ")
    if n_hetatm:
        raise SystemExit(f"[!] Ada {n_hetatm} grup HETATM; script ini hanya menangani rantai protein murni.")
    if len(all_atoms) != len(atom_plddts):
        raise SystemExit(
            f"[!] Jumlah atom CIF ({len(all_atoms)}) != atom_plddts json ({len(atom_plddts)}) - tidak bisa dipetakan aman."
        )

    # -- Sanity check penyelarasan urutan atom CIF vs json (harusnya selisih ~pembulatan)
    cif_bfactors = np.array([a.get_bfactor() for a in all_atoms])
    align_max_diff = float(np.max(np.abs(cif_bfactors - atom_plddts)))
    align_mean_diff = float(np.mean(np.abs(cif_bfactors - atom_plddts)))
    if align_mean_diff > 0.5:
        raise SystemExit(
            f"[!] atom_plddts json tidak selaras dengan atom CIF (mean selisih {align_mean_diff:.3f}). "
            "Jangan dipaksakan - periksa sumber data."
        )

    residues = []  # (chain_id, res_obj, atom_slice_start, atom_slice_end)
    atom_cursor = 0
    for chain in model:
        for res in chain:
            if res.id[0] != " ":
                continue
            n = len(res)
            residues.append((chain.id, res, atom_cursor, atom_cursor + n))
            atom_cursor += n
    if atom_cursor != len(all_atoms):
        raise SystemExit("[!] Konsistensi internal gagal: jumlah atom residu tidak sama dengan total atom.")

    # -- Sekuens dari struktur + validasi terhadap FASTA (TIDAK auto-perbaiki)
    seq_chars, unknown_names = [], []
    for _, res, _, _ in residues:
        name3 = res.get_resname().strip().upper()
        aa = protein_letters_3to1.get(name3, "X")
        if aa == "X":
            unknown_names.append(name3)
        seq_chars.append(aa)
    if unknown_names:
        raise SystemExit(f"[!] Residu tidak dikenali: {sorted(set(unknown_names))} - berhenti, jangan menebak.")
    seq_struct = "".join(seq_chars)
    if seq_struct != seq_ref:
        raise SystemExit(
            "[!] Sekuens struktur BEDA dengan FASTA referensi - berhenti sesuai kebijakan.\n"
            f"    struktur ({len(seq_struct)} aa) != fasta ({len(seq_ref)} aa)"
        )

    # -- Validasi matriks + pemetaan token -> residu
    n_res = len(residues)
    if pae.shape != (n_res, n_res) or contact.shape != (n_res, n_res):
        raise SystemExit(f"[!] Dimensi matriks PAE {pae.shape} / contact {contact.shape} != ({n_res},{n_res}).")
    if token_res_ids != list(range(1, n_res + 1)):
        raise SystemExit(
            f"[!] token_res_ids bukan 1..{n_res} berurutan: {token_res_ids[:10]}... - pemetaan ambigu, berhenti."
        )
    if residues[0][1].id[1] != 1 or residues[-1][1].id[1] != n_res or \
       [r[1].id[1] for r in residues] != list(range(1, n_res + 1)):
        raise SystemExit("[!] Penomoran residu struktur bukan 1..N berurutan - pemetaan PAE ambigu, berhenti.")

    # -- Baris per-residue
    rows = []
    for pos, (chain_id, res, a0, a1) in enumerate(residues):
        name3 = res.get_resname().strip().upper()
        aa = protein_letters_3to1[name3]
        atom_plddt = atom_plddts[a0:a1]
        coords = np.array([a.get_coord() for a in res])
        centroid = coords.mean(axis=0)
        ca = res["CA"]
        backbone_present = sum(1 for an in BACKBONE_ATOMS if an in res)

        i = pos  # indeks token/residu (0-based) == pos karena token_res_ids = 1..N
        lo, hi = max(0, i - PAE_LOCAL_WINDOW), min(n_res, i + PAE_LOCAL_WINDOW + 1)
        local_vals = [pae[i, j] for j in range(lo, hi) if j != i]
        contact_row = contact[i]
        n_ge = int((contact_row >= CONTACT_THRESHOLD).sum()) - (1 if contact_row[i] >= CONTACT_THRESHOLD else 0)

        rows.append({
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
            "contact_prob_sum": round(float(contact_row.sum() - contact_row[i]), 4),
            "n_high_conf_contacts": n_ge,
        })

    # -- Statistik tingkat-dataset
    plddt_ca = np.array([r["plddt_ca"] for r in rows])
    all_coords = np.array([a.get_coord() for a in all_atoms])
    bbox = all_coords.max(axis=0) - all_coords.min(axis=0)

    flat = pae.flatten()
    bin_edges = list(range(0, int(np.ceil(flat.max())) + 2, 2))
    hist_counts, hist_edges = np.histogram(flat, bins=bin_edges)
    offdiag = contact[~np.eye(n_res, dtype=bool)]
    upper = contact[np.triu_indices(n_res, k=1)]

    meta = {
        "dataset": "ubiquitin residue-level features",
        "generated_on": str(date.today()),
        "generator": "src/extract_protein_features.py",
        "inputs": {
            "structure": {"path": str(structure_path.relative_to(PROJECT_ROOT)), "sha256": sha256_of(structure_path)},
            "full_data_json": {"path": str(full_data_path.relative_to(PROJECT_ROOT)), "sha256": sha256_of(full_data_path)},
            "reference_fasta": {"path": str(fasta_path.relative_to(PROJECT_ROOT)), "sha256": sha256_of(fasta_path)},
        },
        "n_residues": n_res,
        "n_chains": len(list(model.get_chains())),
        "chain_ids": sorted({r["chain"] for r in rows}),
        "n_atoms": len(all_atoms),
        "sequence": seq_struct,
        "columns": COLUMNS,
        "feature_definitions": FEATURE_DEFINITIONS,
        "plddt": {
            "ca_mean": round(float(plddt_ca.mean()), 3),
            "ca_min": round(float(plddt_ca.min()), 3),
            "ca_max": round(float(plddt_ca.max()), 3),
            "ca_frac_ge_70": round(float((plddt_ca >= 70).mean()), 4),
            "ca_frac_ge_90": round(float((plddt_ca >= 90).mean()), 4),
            "atom_mean_global": round(float(atom_plddts.mean()), 3),
            "note": ("plddt_ca dibaca dari kolom B-factor CIF; plddt_atom_* dari atom_plddts json. "
                     "Selisih kedua kanal output AlphaFold Server <= 0.09 (pembulatan internal server, "
                     f"mean selisih terukur {align_mean_diff:.4f}, maks {align_max_diff:.4f})."),
        },
        "pae": {
            "shape": [int(pae.shape[0]), int(pae.shape[1])],
            "token_res_ids": "1..N berurutan (diverifikasi)",
            "min": round(float(flat.min()), 3),
            "max": round(float(flat.max()), 3),
            "mean": round(float(flat.mean()), 3),
            "median": round(float(np.median(flat)), 3),
            "percentiles": {str(p): round(float(np.percentile(flat, p)), 3) for p in (1, 5, 25, 50, 75, 95, 99)},
            "histogram": {"bin_edges": [float(b) for b in hist_edges], "counts": [int(c) for c in hist_counts]},
            "orientation_note": ("Matriks dipakai apa adanya dari full_data json (tanpa transpose/reshape). "
                                 "Baris i dan kolom j dipetakan ke residu via token_res_ids. "
                                 "Interpretasi umum AlphaFold: elemen [i][j] = estimasi error posisi token i "
                                 "bila struktur di-align pada token j."),
        },
        "contact_probs": {
            "shape": [int(contact.shape[0]), int(contact.shape[1])],
            "symmetric_max_diff": round(float(np.max(np.abs(contact - contact.T))), 6),
            "diagonal": {"min": round(float(np.diag(contact).min()), 3),
                         "median": round(float(np.median(np.diag(contact))), 3),
                         "max": round(float(np.diag(contact).max()), 3)},
            "offdiag_mean": round(float(offdiag.mean()), 4),
            "offdiag_median": round(float(np.median(offdiag)), 4),
            "offdiag_max": round(float(offdiag.max()), 4),
            "n_pairs_ge_0.50_unordered": int((upper >= CONTACT_THRESHOLD).sum()),
            "threshold_note": (f"Ambang {CONTACT_THRESHOLD} dipilih eksplisit untuk fitur turunan. "
                               "Ini probabilitas kontak PREDIKSI model, bukan kontak eksperimental."),
        },
        "structure_bbox_angstrom": [round(float(v), 2) for v in bbox],
        "notes": [
            "Dataset berisi 76 residu x 1 chain (ubiquitin, prediksi AlphaFold Server model_0).",
            "Semua feature adalah turunan langsung dari file prediksi; tidak ada data eksperimen.",
            "pLDDT tinggi / PAE rendah = keyakinan MODEL, bukan bukti fungsi atau kebenaran biologis.",
        ],
    }
    extras = {"pae": pae, "contact": contact}
    return rows, meta, extras


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def write_csv(rows: list[dict], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def write_json(meta: dict, path: Path) -> None:
    path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")


def make_plots(rows: list[dict], extras: dict, outdir: Path, prefix: str) -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    saved = []

    x = [r["residue_id"] for r in rows]
    y = [r["plddt_ca"] for r in rows]
    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.plot(x, y, marker="o", markersize=3, linewidth=1, color="#1f77b4")
    ax.axhline(90, color="#2ca02c", linestyle="--", linewidth=1, label="ambang 90 (sangat tinggi)")
    ax.axhline(70, color="#ff7f0e", linestyle="--", linewidth=1, label="ambang 70 (tinggi)")
    ax.set_xlabel("Nomor residu")
    ax.set_ylabel("pLDDT (0-100)")
    ax.set_title("pLDDT per-residu atom CA - ubiquitin, AlphaFold model_0 (prediksi)")
    ax.set_ylim(0, 100)
    ax.set_xlim(0.5, len(x) + 0.5)
    ax.legend(loc="lower left", fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    p1 = outdir / f"{prefix}_plddt_per_residue.png"
    fig.savefig(p1, dpi=150)
    plt.close(fig)
    saved.append(p1)

    pae = extras["pae"]
    vmax = float(np.ceil(pae.max()))
    fig, ax = plt.subplots(figsize=(7.4, 6.4))
    im = ax.imshow(pae, origin="upper", aspect="equal", cmap="magma", vmin=0.0, vmax=vmax)
    ticks = list(range(0, pae.shape[0], 10))
    if ticks[-1] != pae.shape[0] - 1:
        ticks.append(pae.shape[0] - 1)
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(t + 1) for t in ticks], fontsize=8)
    ax.set_yticks(ticks)
    ax.set_yticklabels([str(t + 1) for t in ticks], fontsize=8)
    ax.set_xlabel("Residu j (kolom; indeks = token_res_ids[j])")
    ax.set_ylabel("Residu i (baris; indeks = token_res_ids[i])")
    ax.set_title("PAE model_0 - ubiquitin 76x76 (prediksi, Angstrom)")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cbar.set_label("PAE (Angstrom)")
    fig.tight_layout()
    p2 = outdir / f"{prefix}_pae_heatmap.png"
    fig.savefig(p2, dpi=150)
    plt.close(fig)
    saved.append(p2)

    return saved


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="extract_protein_features.py",
        description="Ekstraksi feature per-residue dari prediksi AlphaFold (read-only).",
    )
    parser.add_argument("--structure", type=Path, default=DEFAULT_STRUCTURE)
    parser.add_argument("--full-data", type=Path, default=None,
                        help="file <job>_full_data_0.json (default: auto-deteksi di data/alphafold_downloads/)")
    parser.add_argument("--fasta", type=Path, default=DEFAULT_FASTA)
    parser.add_argument("--outdir", type=Path, default=RESULTS_DIR)
    parser.add_argument("--prefix", default="ubiquitin")
    args = parser.parse_args(argv)

    for p in (args.structure, args.fasta):
        if not p.is_file():
            print(f"[!] File tidak ditemukan: {p}")
            return 2
    full_data_path = find_full_data(DOWNLOADS_DIR, args.full_data)

    print(f"[i] Struktur   : {args.structure}")
    print(f"[i] Full data  : {full_data_path}")
    print(f"[i] FASTA ref  : {args.fasta}")

    rows, meta, extras = extract_rows(args.structure, full_data_path, args.fasta)
    args.outdir.mkdir(parents=True, exist_ok=True)

    csv_path = args.outdir / f"{args.prefix}_residue_features.csv"
    json_path = args.outdir / f"{args.prefix}_structure_features.json"
    write_csv(rows, csv_path)
    write_json(meta, json_path)
    plots = make_plots(rows, extras, args.outdir, args.prefix)

    aa_counts = Counter(r["one_letter_aa"] for r in rows)
    print(f"\n[i] {len(rows)} residu, {len(COLUMNS)} kolom feature")
    print(f"[i] Sekuens (dari struktur, diverifikasi = FASTA): {meta['sequence'][:30]}...")
    print(f"[i] pLDDT CA: mean {meta['plddt']['ca_mean']} | min {meta['plddt']['ca_min']} | max {meta['plddt']['ca_max']}")
    print(f"[i] PAE {meta['pae']['shape'][0]}x{meta['pae']['shape'][1]}: min {meta['pae']['min']} | max {meta['pae']['max']} | mean {meta['pae']['mean']} | median {meta['pae']['median']}")
    print(f"[i] Komposisi: {dict(sorted(aa_counts.items()))}")
    print("\nHasil disimpan:")
    for p in (csv_path, json_path, *plots):
        print(f"  - {p}")
    print("\n" + "-" * 68)
    print("Catatan: feature dari PREDIKSI AlphaFold - keyakinan model, bukan bukti biologis.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
