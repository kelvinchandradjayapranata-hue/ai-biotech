#!/usr/bin/env python3
"""
analyze_protein.py - analisis deskriptif protein (struktur AlphaFold / PDB / mmCIF, atau sekuens).

Yang dilakukan:
  1. Membaca file struktur protein (.pdb / .cif / .mmcif) ATAU sekuens (.fasta / teks).
  2. Menampilkan: jumlah chain, jumlah residu, sekuens per chain, komposisi asam amino,
     dan statistik B-factor (pada output AlphaFold, kolom B-factor berisi pLDDT).
  3. Menyimpan hasil ke folder results/ (JSON + CSV).

Yang TIDAK dilakukan (jangan diasumsikan ada):
  - Tidak ada docking, simulasi dinamika molekuler, atau skrining obat.
  - Ini bukan drug discovery dan bukan validasi eksperimen.
  - Hasil prediksi AlphaFold adalah MODEL, bukan kebenaran biologis.

Contoh pemakaian (dari folder root project):
  python src/analyze_protein.py                                   # scan otomatis folder structures/
  python src/analyze_protein.py structures/ubiquitin_alphafold.pdb
  python src/analyze_protein.py --fasta data/ubiquitin_sequence.fasta
  python src/analyze_protein.py --sequence MQIFVKTLTGK --name contoh
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

# Folder project dihitung dari posisi file ini, sehingga script bisa dijalankan
# dari folder kerja mana pun tanpa mengubah apa pun.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
STRUCTURES_DIR = PROJECT_ROOT / "structures"
RESULTS_DIR = PROJECT_ROOT / "results"
STRUCTURE_EXTENSIONS = {".pdb", ".cif", ".mmcif"}

DISCLAIMER = (
    "Catatan: analisis deskriptif untuk pembelajaran. Hasil prediksi AlphaFold adalah\n"
    "MODEL, bukan bukti kebenaran biologis. Tidak ada docking / MD / klaim drug discovery."
)

GUIDANCE_NO_STRUCTURE = f"""
[i] Tidak ada file struktur ditemukan di:
    {STRUCTURES_DIR}

    File yang perlu Anda letakkan di folder tersebut:
      - file struktur hasil unduhan AlphaFold Server (format .pdb atau .cif / .mmcif),
        contoh: {STRUCTURES_DIR / 'ubiquitin_alphafold.pdb'}

    Analisis sekuens (tanpa file struktur) tetap bisa dijalankan:
      python src/analyze_protein.py --fasta data/ubiquitin_sequence.fasta
"""


# ---------------------------------------------------------------------------
# Pembacaan input
# ---------------------------------------------------------------------------

def load_sequence_from_fasta(path: Path) -> tuple[str, str]:
    """Kembalikan (nama, sekuens) dari file FASTA (record pertama)."""
    from Bio import SeqIO

    with path.open(encoding="utf-8") as fh:
        record = next(SeqIO.parse(fh, "fasta"), None)
    if record is None:
        raise ValueError(f"tidak ada record FASTA di {path}")
    return record.id, str(record.seq).upper().strip()


def find_structure_files(folder: Path) -> list[Path]:
    """Cari file .pdb/.cif/.mmcif di dalam folder (tidak rekursif)."""
    if not folder.is_dir():
        return []
    return sorted(
        p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in STRUCTURE_EXTENSIONS
    )


# ---------------------------------------------------------------------------
# Analisis
# ---------------------------------------------------------------------------

def analyze_sequence(seq: str) -> dict:
    """Statistik dasar dari sebuah sekuens protein."""
    counts = Counter(seq)
    stats: dict = {
        "length": len(seq),
        "composition": {
            aa: int(n) for aa, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        },
    }
    try:
        # ProteinAnalysis hanya mengenal 20 asam amino standar; kalau ada
        # karakter lain (mis. 'X'), bagian ini dilewati tanpa menggagalkan analisis.
        from Bio.SeqUtils.ProtParam import ProteinAnalysis

        pa = ProteinAnalysis(seq)
        stats["molecular_weight_da"] = round(pa.molecular_weight(), 1)
        stats["isoelectric_point"] = round(pa.isoelectric_point(), 2)
        stats["gravy"] = round(pa.gravy(), 3)  # hidrofobisitas rata-rata (Grand Average of Hydropathy)
    except Exception as exc:
        stats["note"] = f"Perhitungan berat molekul / pI / GRAVY dilewati ({exc})."
    return stats


def analyze_structure(path: Path) -> tuple[dict, list[dict]]:
    """Baca file struktur dengan Biopython -> (ringkasan, baris per-residu untuk CSV)."""
    from Bio.PDB import MMCIFParser, PDBParser
    from Bio.PDB.Polypeptide import protein_letters_3to1

    suffix = path.suffix.lower()
    if suffix in {".cif", ".mmcif"}:
        parser, fmt = MMCIFParser(QUIET=True), "mmCIF"
    elif suffix == ".pdb":
        parser, fmt = PDBParser(QUIET=True), "PDB"
    else:
        raise ValueError(f"format tidak dikenali: {suffix} (didukung: .pdb, .cif, .mmcif)")

    structure = parser.get_structure(path.stem, str(path))
    models = list(structure)
    model = models[0]  # pakai model pertama (umumnya satu-satunya)

    chains: list[dict] = []
    per_residue: list[dict] = []

    for chain in model:
        n_hetatm = 0
        n_atoms = 0
        seq_chars: list[str] = []
        bfactors: list[float] = []

        for res in chain:
            if res.id[0] != " ":  # HETATM (air/ligan/ion) -> dihitung terpisah, bukan residu protein
                n_hetatm += 1
                continue

            name3 = res.get_resname().strip().upper()
            aa1 = protein_letters_3to1.get(name3, "X")
            seq_chars.append(aa1)
            n_atoms += len(res)

            b = None
            if "CA" in res:
                b = float(res["CA"].get_bfactor())
            elif len(res) > 0:
                b = sum(float(a.get_bfactor()) for a in res) / len(res)
            if b is not None:
                bfactors.append(b)
                per_residue.append(
                    {
                        "chain": chain.id,
                        "res_id": res.id[1],
                        "res_name": name3,
                        "aa": aa1,
                        "bfactor_plddt": round(b, 2),
                    }
                )

        info: dict = {
            "chain_id": chain.id,
            "n_residues": len(seq_chars),
            "n_atoms": n_atoms,
            "n_hetatm": n_hetatm,
            "sequence": "".join(seq_chars),
        }
        if bfactors:
            n = len(bfactors)
            info["bfactor_plddt_stats"] = {
                "mean": round(sum(bfactors) / n, 2),
                "min": round(min(bfactors), 2),
                "max": round(max(bfactors), 2),
                "frac_ge_70": round(sum(1 for b in bfactors if b >= 70) / n, 3),
                "frac_ge_90": round(sum(1 for b in bfactors if b >= 90) / n, 3),
            }
        chains.append(info)

    summary: dict = {
        "file": path.name,
        "format": fmt,
        "n_models": len(models),
        "n_chains": len(chains),
        "total_residues": sum(c["n_residues"] for c in chains),
        "chains": chains,
        "note_bfactor": (
            "Nilai B-factor dibaca apa adanya dari file. Pada output AlphaFold Server, "
            "kolom ini umumnya berisi pLDDT (0-100). Verifikasi dengan file Anda sendiri."
        ),
    }
    return summary, per_residue


# ---------------------------------------------------------------------------
# Output ke layar
# ---------------------------------------------------------------------------

def _separator(title: str = "") -> str:
    line = "=" * 68
    return f"\n{line}\n{title}\n{line}" if title else f"\n{line}"


def print_sequence_report(name: str, seq: str, stats: dict) -> None:
    print(_separator(f"ANALISIS SEKUENS - {name}"))
    print(f"Panjang sekuens : {stats['length']} asam amino")
    comp = "  ".join(f"{aa}:{n}" for aa, n in stats["composition"].items())
    print(f"Komposisi       : {comp}")
    if "molecular_weight_da" in stats:
        print(f"Berat molekul   : {stats['molecular_weight_da']:.1f} Da (perkiraan dari sekuens)")
    if "isoelectric_point" in stats:
        print(f"Titik isoelektrik (pI): {stats['isoelectric_point']:.2f}")
    if "gravy" in stats:
        print(f"GRAVY           : {stats['gravy']:+.3f}  (- hidrofilik, + hidrofobik)")
    if "note" in stats:
        print(f"[i] {stats['note']}")
    print(DISCLAIMER)


def print_structure_report(summary: dict) -> None:
    print(_separator(f"ANALISIS STRUKTUR - {summary['file']}"))
    print(f"Format        : {summary['format']}")
    print(f"Jumlah model  : {summary['n_models']} (dipakai: model pertama)")
    print(f"Jumlah chain  : {summary['n_chains']}")
    print(f"Total residu  : {summary['total_residues']}")
    for c in summary["chains"]:
        print(f"\n  Chain '{c['chain_id']}'")
        print(f"    residu      : {c['n_residues']}")
        print(f"    atom        : {c['n_atoms']}")
        if c["n_hetatm"]:
            print(f"    grup HETATM : {c['n_hetatm']} (air/ligan/ion, bukan residu protein)")
        seq = c["sequence"]
        preview = seq if len(seq) <= 70 else seq[:70] + "..."
        print(f"    sekuens     : {preview}")
        st = c.get("bfactor_plddt_stats")
        if st:
            print("    B-factor (pLDDT pada output AlphaFold):")
            print(f"      rata-rata {st['mean']} | min {st['min']} | max {st['max']}")
            print(
                f"      residu dgn nilai >= 70: {st['frac_ge_70'] * 100:.1f}%"
                f" | >= 90: {st['frac_ge_90'] * 100:.1f}%"
            )
    print(f"\n[i] {summary['note_bfactor']}")
    print(DISCLAIMER)


# ---------------------------------------------------------------------------
# Output ke file (results/)
# ---------------------------------------------------------------------------

def _write_json(obj: dict, path: Path) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def save_sequence_outputs(name: str, seq: str, stats: dict, outdir: Path) -> list[Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    payload = {"name": name, "sequence": seq, "analyzed_on": str(date.today()), **stats}
    json_path = outdir / f"{name}_sequence_analysis.json"
    csv_path = outdir / f"{name}_composition.csv"
    _write_json(payload, json_path)
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["asam_amino", "jumlah"])
        writer.writerows(stats["composition"].items())
    return [json_path, csv_path]


def save_structure_outputs(summary: dict, rows: list[dict], outdir: Path) -> list[Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    stem = Path(summary["file"]).stem
    json_path = outdir / f"{stem}_structure_analysis.json"
    csv_path = outdir / f"{stem}_per_residue.csv"
    _write_json({"analyzed_on": str(date.today()), **summary}, json_path)
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["chain", "res_id", "res_name", "aa", "bfactor_plddt"]
        )
        writer.writeheader()
        writer.writerows(rows)
    return [json_path, csv_path]


# ---------------------------------------------------------------------------
# Alur utama
# ---------------------------------------------------------------------------

def _run_sequence_mode(name: str, seq: str, outdir: Path) -> int:
    stats = analyze_sequence(seq)
    print_sequence_report(name, seq, stats)
    saved = save_sequence_outputs(name, seq, stats, outdir)
    print("\nHasil disimpan:")
    for p in saved:
        print(f"  - {p}")
    return 0


def _run_structure_mode(files: list[Path], outdir: Path) -> int:
    exit_code = 0
    for path in files:
        try:
            summary, rows = analyze_structure(path)
        except FileNotFoundError:
            print(f"[!] File tidak ditemukan: {path}")
            exit_code = 2
            continue
        except Exception as exc:
            print(f"[!] Gagal membaca {path.name}: {exc}")
            exit_code = 3
            continue
        print_structure_report(summary)
        saved = save_structure_outputs(summary, rows, outdir)
        print("\nHasil disimpan:")
        for p in saved:
            print(f"  - {p}")
    return exit_code


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="analyze_protein.py",
        description="Analisis deskriptif protein: struktur (PDB/mmCIF) atau sekuens.",
        epilog="Contoh: python src/analyze_protein.py structures/model.pdb",
    )
    parser.add_argument("structure", nargs="?", default=None, help="path file struktur (.pdb/.cif/.mmcif)")
    parser.add_argument("--fasta", type=Path, default=None, help="file FASTA berisi satu sekuens")
    parser.add_argument("--sequence", default=None, help="sekuens protein langsung (huruf satu-kode)")
    parser.add_argument("--name", default=None, help="nama untuk output (default: nama file / 'sequence')")
    parser.add_argument("--outdir", type=Path, default=RESULTS_DIR, help=f"folder output (default: {RESULTS_DIR})")
    args = parser.parse_args(argv)

    if args.sequence and args.fasta:
        parser.error("pilih salah satu: --sequence atau --fasta")

    # Mode 1: sekuens langsung dari command line
    if args.sequence:
        seq = "".join(ch for ch in args.sequence.upper() if ch.isalpha())
        return _run_sequence_mode(args.name or "sequence", seq, args.outdir)

    # Mode 2: sekuens dari file FASTA
    if args.fasta:
        if not args.fasta.is_file():
            print(f"[!] File FASTA tidak ditemukan: {args.fasta}")
            return 2
        name, seq = load_sequence_from_fasta(args.fasta)
        return _run_sequence_mode(args.name or name, seq, args.outdir)

    # Mode 3: file struktur tertentu
    if args.structure:
        files = [Path(args.structure)]
    # Mode 4: scan otomatis folder structures/
    else:
        files = find_structure_files(STRUCTURES_DIR)
        if not files:
            print(GUIDANCE_NO_STRUCTURE)
            return 2
        print(f"[i] Ditemukan {len(files)} file struktur di {STRUCTURES_DIR}")

    return _run_structure_mode(files, args.outdir)


if __name__ == "__main__":
    sys.exit(main())
