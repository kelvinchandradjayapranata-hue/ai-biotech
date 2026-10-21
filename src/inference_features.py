#!/usr/bin/env python3
"""
inference_features.py - Stage 11: kontrak fitur dan ekstraksi struktur untuk inferensi.

Modul ini adalah SATU-SATUNYA sumber definisi fitur untuk `export_model.py` dan
`predict.py`, sehingga urutan 16 fitur tidak bisa berbeda antara training artefak
dan inferensi.

Kontrak fitur (urutan final, 16 kolom):
  7 fitur struktural:
    hydropathy_kd, charge_ph7, n_atoms, plddt_ca,
    pae_mean_row, pae_mean_col, pae_local_mean_k10
  3 fitur spasial radius 12 A:
    spatial_density_12a, spatial_plddt_mean_12a, spatial_pae_mean_12a
  6 one-hot kategori asam amino (urutan tetap):
    aa_acidic, aa_aromatic, aa_basic, aa_nonpolar, aa_polar, aa_special

Definisi spasial (identik dengan Stage 10.2):
  neighbours(i) = { j != i : ||CA_i - CA_j|| <= 12.0 A }
  spatial_density_12a    = |neighbours(i)|                  (self excluded)
  spatial_plddt_mean_12a = mean pLDDT_CA(j) untuk j tetangga
  spatial_pae_mean_12a   = mean PAE[i, j] untuk j tetangga  (baris i, terarah)

Batas (jangan dilanggar):
  - Tidak ada imputasi. Residu tanpa tetangga pada radius 12 A = error.
  - PAE wajib ada; 6 dari 16 fitur diturunkan dari PAE.
  - Hanya model 1, satu chain, penomoran residu 1..N berurutan.
  - B-factor harus berupa pLDDT (konvensi AlphaFold DB), bukan B-factor eksperimen.
  - Ini bukan validasi biologis; pLDDT/PAE adalah keyakinan model prediksi.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Definisi kimiawi dibekukan di Stage 3; jangan diduplikasi/diubah di sini.
from extract_protein_features import (  # noqa: E402
    AA_TYPE,
    CHARGE_PH7,
    KD_HYDROPATHY,
    PAE_LOCAL_WINDOW,
)

RADIUS_ANGSTROM = 12.0

AA_TYPES = ("acidic", "aromatic", "basic", "nonpolar", "polar", "special")

BASE_FEATURES = [
    "hydropathy_kd",
    "charge_ph7",
    "n_atoms",
    "plddt_ca",
    "pae_mean_row",
    "pae_mean_col",
    "pae_local_mean_k10",
]
SPATIAL_FEATURES = [
    "spatial_density_12a",
    "spatial_plddt_mean_12a",
    "spatial_pae_mean_12a",
]
ONEHOT_FEATURES = [f"aa_{t}" for t in AA_TYPES]
FEATURE_NAMES = BASE_FEATURES + SPATIAL_FEATURES + ONEHOT_FEATURES

RESIDUE_COLUMNS = [
    "sequence_position",
    "amino_acid",
    "amino_acid_type",
] + BASE_FEATURES + SPATIAL_FEATURES

# 20 asam amino standar. Residu non-standar tidak ditebak.
AA3_TO_1 = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C",
    "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I",
    "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P",
    "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
}

AFDB_API = "https://alphafold.ebi.ac.uk/api/prediction/{acc}"
AFDB_HOST = "alphafold.ebi.ac.uk"
ACCESSION_RE = re.compile(r"^[A-Z0-9]{6,10}$")
MAX_API_BYTES = 5 * 1024 * 1024
MAX_CIF_BYTES = 100 * 1024 * 1024
MAX_PAE_BYTES = 250 * 1024 * 1024


class InferenceError(RuntimeError):
    """Kesalahan input/format yang harus dilaporkan eksplisit, tanpa menebak."""


@dataclass(frozen=True)
class ResidueRecord:
    chain: str
    sequence_position: int
    residue_name: str
    amino_acid: str
    n_atoms: int
    ca_xyz: np.ndarray
    plddt_ca: float


@dataclass
class StructureRecord:
    path: Path
    fmt: str
    residues: list[ResidueRecord]
    chain_ids: list[str]
    n_hetatm_records: int = 0
    n_altloc_skipped: int = 0
    warnings: list[str] = field(default_factory=list)

    @property
    def n_residues(self) -> int:
        return len(self.residues)

    @property
    def sequence(self) -> str:
        return "".join(r.amino_acid for r in self.residues)


@dataclass
class AFDBEntry:
    accession: str
    entry_id: str
    version: str
    sequence: str
    sequence_checksum: str
    chain_id: str
    cif_path: Path
    pae_path: Path
    metadata_path: Path
    cache_hit: bool
    metadata: dict


# ---------------------------------------------------------------------------
# Utilitas umum
# ---------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def default_cache_dir() -> Path:
    """Direktori cache AFDB yang bisa ditimpa lewat AI_BIOTECH_CACHE."""
    env = os.environ.get("AI_BIOTECH_CACHE")
    if env:
        return Path(env).expanduser()
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / "ai-biotech" / "cache" / "afdb"
    base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return base / "ai-biotech" / "afdb"


def _as_chain_id(value: str) -> str:
    value = (value or "").strip()
    return value if value and value not in {".", "?"} else "_"


def _residue_sort_key(res: ResidueRecord):
    return (res.chain, res.sequence_position)


def _select_chain(residues: list[ResidueRecord], chain: str | None, path: Path):
    chain_ids = list(dict.fromkeys(r.chain for r in residues))
    if chain is not None:
        if chain not in chain_ids:
            raise InferenceError(
                f"{path.name}: chain {chain!r} tidak ada; chain tersedia: {chain_ids}"
            )
        selected = [r for r in residues if r.chain == chain]
    else:
        if len(chain_ids) != 1:
            raise InferenceError(
                f"{path.name}: ditemukan {len(chain_ids)} chain {chain_ids}; "
                "pilih satu dengan --chain (PAE hanya untuk satu chain)"
            )
        selected = list(residues)

    selected = sorted(selected, key=_residue_sort_key)
    nums = [r.sequence_position for r in selected]
    expected = list(range(1, len(selected) + 1))
    if nums != expected:
        preview = nums[:5] + (["..."] if len(nums) > 8 else []) + nums[-3:]
        raise InferenceError(
            f"{path.name}: penomoran residu chain terpilih bukan 1..{len(selected)} "
            f"(awal/akhir: {preview}). PAE hanya bisa dipetakan ke penomoran 1..N; "
            "tidak ada renumbering otomatis."
        )
    if not selected:
        raise InferenceError(f"{path.name}: tidak ada residu protein pada chain terpilih")
    return selected, chain_ids


def _finalize_structure(
    path: Path,
    fmt: str,
    residues: list[ResidueRecord],
    n_hetatm: int,
    n_altloc: int,
    chain: str | None,
    warnings: list[str],
) -> StructureRecord:
    if not residues:
        raise InferenceError(f"{path.name}: tidak ada record ATOM protein yang terbaca")
    selected, chain_ids = _select_chain(residues, chain, path)
    for res in selected:
        if res.amino_acid not in AA_TYPE:
            raise InferenceError(
                f"{path.name}:{res.sequence_position}: asam amino {res.amino_acid!r} "
                "tidak punya kategori/ hydropathy - berhenti, jangan menebak"
            )
        if not np.all(np.isfinite(res.ca_xyz)):
            raise InferenceError(
                f"{path.name}:{res.sequence_position}: koordinat CA tidak finite"
            )
        if not (0.0 <= res.plddt_ca <= 100.0):
            raise InferenceError(
                f"{path.name}:{res.sequence_position}: B-factor CA {res.plddt_ca} "
                "di luar rentang pLDDT [0,100]"
            )
    return StructureRecord(
        path=path,
        fmt=fmt,
        residues=selected,
        chain_ids=chain_ids,
        n_hetatm_records=n_hetatm,
        n_altloc_skipped=n_altloc,
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# Parser mmCIF (text, float64)
# ---------------------------------------------------------------------------

def _cif_atom_site_columns(lines: list[str]):
    for i, line in enumerate(lines):
        if line.strip() != "loop_":
            continue
        j = i + 1
        tags = []
        while j < len(lines) and lines[j].strip().startswith("_atom_site."):
            tags.append(lines[j].strip())
            j += 1
        if tags:
            return j, tags
    raise InferenceError("loop _atom_site tidak ditemukan (bukan mmCIF atom-site yang dikenali)")


def _field(fields: list[str], col: dict[str, int], name: str, default: str = "") -> str:
    idx = col.get(name)
    if idx is None or idx >= len(fields):
        return default
    return fields[idx]


def parse_cif(path: Path, chain: str | None = None) -> StructureRecord:
    """Parse ATOM record mmCIF sebagai float64; HETATM dilewati eksplisit."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    start, tags = _cif_atom_site_columns(lines)
    col = {tag.split(".", 1)[1]: k for k, tag in enumerate(tags)}

    for required in ("Cartn_x", "Cartn_y", "Cartn_z", "B_iso_or_equiv"):
        if required not in col:
            raise InferenceError(f"{path.name}: kolom _atom_site.{required} tidak ada")

    atom_col = "label_atom_id" if "label_atom_id" in col else "auth_atom_id"
    comp_col = "label_comp_id" if "label_comp_id" in col else "auth_comp_id"
    asym_col = "label_asym_id" if "label_asym_id" in col else "auth_asym_id"
    seq_col = "label_seq_id" if "label_seq_id" in col else "auth_seq_id"
    alt_col = "label_alt_id" if "label_alt_id" in col else None
    ins_col = "pdbx_PDB_ins_code" if "pdbx_PDB_ins_code" in col else None
    model_col = "pdbx_PDB_model_num" if "pdbx_PDB_model_num" in col else None
    if atom_col not in col or comp_col not in col or asym_col not in col or seq_col not in col:
        raise InferenceError(f"{path.name}: kolom identitas atom/residu CIF tidak lengkap")

    residues: dict[tuple[str, int], dict] = {}
    order: list[tuple[str, int]] = []
    n_hetatm = 0
    n_altloc = 0

    for line in lines[start:]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#") or stripped == "loop_" or stripped.startswith("_"):
            if residues:
                break
            continue
        if not line.startswith(("ATOM ", "HETATM ")):
            if residues:
                break
            continue
        fields = line.split()
        if len(fields) < len(tags):
            raise InferenceError(f"{path.name}: baris atom-site pendek/tidak lengkap")

        if model_col is not None:
            model_txt = _field(fields, col, model_col).strip()
            if model_txt not in {"", ".", "?"}:
                try:
                    if int(model_txt) != 1:
                        continue
                except ValueError as exc:
                    raise InferenceError(
                        f"{path.name}: pdbx_PDB_model_num bukan integer: {model_txt!r}"
                    ) from exc

        is_het = line.startswith("HETATM ")
        if is_het:
            n_hetatm += 1
            continue

        alt = _field(fields, col, alt_col).strip() if alt_col else "."
        if alt not in {"", ".", "?", "A"}:
            n_altloc += 1
            continue

        chain_id = _as_chain_id(_field(fields, col, asym_col))
        seq_txt = _field(fields, col, seq_col).strip()
        if seq_txt in {"", ".", "?"}:
            raise InferenceError(f"{path.name}: label_seq_id/auth_seq_id kosong")
        try:
            seq_id = int(seq_txt)
        except ValueError as exc:
            raise InferenceError(
                f"{path.name}: nomor residu bukan integer: {seq_txt!r}"
            ) from exc

        if seq_col == "auth_seq_id" and ins_col is not None:
            ins = _field(fields, col, ins_col).strip()
            if ins not in {"", ".", "?"}:
                raise InferenceError(
                    f"{path.name}: insertion code {ins!r} pada residu {seq_id}; "
                    "tidak bisa dipetakan ke PAE 1..N"
                )

        atom_name = _field(fields, col, atom_col).strip()
        resname = _field(fields, col, comp_col).strip().upper()
        if not atom_name or not resname:
            raise InferenceError(f"{path.name}: nama atom/residu kosong")
        aa = AA3_TO_1.get(resname)
        if aa is None:
            raise InferenceError(
                f"{path.name}: residu {resname!r} (posisi {seq_id}) bukan 20 asam amino standar"
            )

        try:
            x = float(_field(fields, col, "Cartn_x"))
            y = float(_field(fields, col, "Cartn_y"))
            z = float(_field(fields, col, "Cartn_z"))
            b = float(_field(fields, col, "B_iso_or_equiv"))
        except ValueError as exc:
            raise InferenceError(
                f"{path.name}: koordinat/B-factor bukan angka pada posisi {seq_id}"
            ) from exc
        if not (0.0 <= b <= 100.0):
            raise InferenceError(
                f"{path.name}:{seq_id}: B-factor {b} di luar [0,100]; "
                "file ini bukan struktur bergaya AlphaFold (pLDDT di B-factor)?"
            )

        key = (chain_id, seq_id)
        if key not in residues:
            residues[key] = {
                "chain": chain_id,
                "sequence_position": seq_id,
                "residue_name": resname,
                "amino_acid": aa,
                "atoms": {},
                "ca": None,
                "plddt": None,
            }
            order.append(key)
        rec = residues[key]
        if rec["residue_name"] != resname:
            raise InferenceError(
                f"{path.name}: posisi {seq_id} punya dua nama residu "
                f"({rec['residue_name']} vs {resname})"
            )
        # Altloc yang lolos filter di atas: simpan atom pertama per nama atom.
        if atom_name not in rec["atoms"]:
            rec["atoms"][atom_name] = (x, y, z, b)
        if atom_name == "CA" and rec["ca"] is None:
            rec["ca"] = np.asarray([x, y, z], dtype=np.float64)
            rec["plddt"] = b

    records: list[ResidueRecord] = []
    for key in order:
        rec = residues[key]
        if rec["ca"] is None:
            raise InferenceError(
                f"{path.name}: residu {rec['residue_name']} posisi {rec['sequence_position']} "
                "tidak punya atom CA"
            )
        records.append(
            ResidueRecord(
                chain=rec["chain"],
                sequence_position=rec["sequence_position"],
                residue_name=rec["residue_name"],
                amino_acid=rec["amino_acid"],
                n_atoms=len(rec["atoms"]),
                ca_xyz=rec["ca"],
                plddt_ca=round(float(rec["plddt"]), 2),
            )
        )

    warnings = []
    if n_hetatm:
        warnings.append(f"{n_hetatm} record HETATM dilewati (ligan/waters/modified residues)")
    if n_altloc:
        warnings.append(f"{n_altloc} atom altloc selain blank/A dilewati")
    return _finalize_structure(path, "cif", records, n_hetatm, n_altloc, chain, warnings)


# ---------------------------------------------------------------------------
# Parser PDB (fixed-column, float64)
# ---------------------------------------------------------------------------

def parse_pdb(path: Path, chain: str | None = None) -> StructureRecord:
    """Parse ATOM record PDB sebagai float64; HETATM dan model >1 dilewati eksplisit."""
    residues: dict[tuple[str, int], dict] = {}
    order: list[tuple[str, int]] = []
    n_hetatm = 0
    n_altloc = 0
    saw_model = False
    in_first_model = True

    for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="strict").splitlines(), 1):
        rec = line[:6].strip().upper()
        if rec == "MODEL":
            saw_model = True
            if residues:
                break  # model pertama sudah selesai
            in_first_model = True
            continue
        if rec == "ENDMDL":
            if residues:
                break
            continue
        if rec == "HETATM":
            n_hetatm += 1
            continue
        if rec != "ATOM" or not in_first_model:
            continue
        if len(line) < 66:
            raise InferenceError(f"{path.name}:{lineno}: baris ATOM lebih pendek dari 66 kolom")
        alt = line[16:17]
        if alt not in {" ", "A"}:
            n_altloc += 1
            continue
        atom_name = line[12:16].strip()
        resname = line[17:20].strip().upper()
        chain_id = _as_chain_id(line[21:22])
        icode = line[26:27].strip()
        if icode:
            raise InferenceError(
                f"{path.name}:{lineno}: insertion code {icode!r} pada residu "
                f"{line[22:26].strip()}; tidak bisa dipetakan ke PAE 1..N"
            )
        try:
            seq_id = int(line[22:26])
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
            b = float(line[60:66])
        except ValueError as exc:
            raise InferenceError(
                f"{path.name}:{lineno}: kolom PDB tidak bisa dibaca sebagai angka"
            ) from exc
        aa = AA3_TO_1.get(resname)
        if aa is None:
            raise InferenceError(
                f"{path.name}:{lineno}: residu {resname!r} bukan 20 asam amino standar"
            )
        if not (0.0 <= b <= 100.0):
            raise InferenceError(
                f"{path.name}:{lineno}: B-factor {b} di luar [0,100]; "
                "file ini bukan struktur bergaya AlphaFold (pLDDT di B-factor)?"
            )

        key = (chain_id, seq_id)
        if key not in residues:
            residues[key] = {
                "chain": chain_id,
                "sequence_position": seq_id,
                "residue_name": resname,
                "amino_acid": aa,
                "atoms": {},
                "ca": None,
                "plddt": None,
            }
            order.append(key)
        rr = residues[key]
        if rr["residue_name"] != resname:
            raise InferenceError(
                f"{path.name}: posisi {seq_id} punya dua nama residu "
                f"({rr['residue_name']} vs {resname})"
            )
        if atom_name not in rr["atoms"]:
            rr["atoms"][atom_name] = (x, y, z, b)
        if atom_name == "CA" and rr["ca"] is None:
            rr["ca"] = np.asarray([x, y, z], dtype=np.float64)
            rr["plddt"] = b

    if saw_model and not residues:
        raise InferenceError(f"{path.name}: MODEL pertama tidak berisi ATOM protein")

    records: list[ResidueRecord] = []
    for key in order:
        rr = residues[key]
        if rr["ca"] is None:
            raise InferenceError(
                f"{path.name}: residu {rr['residue_name']} posisi {rr['sequence_position']} "
                "tidak punya atom CA"
            )
        records.append(
            ResidueRecord(
                chain=rr["chain"],
                sequence_position=rr["sequence_position"],
                residue_name=rr["residue_name"],
                amino_acid=rr["amino_acid"],
                n_atoms=len(rr["atoms"]),
                ca_xyz=rr["ca"],
                plddt_ca=round(float(rr["plddt"]), 2),
            )
        )

    warnings = []
    if n_hetatm:
        warnings.append(f"{n_hetatm} record HETATM dilewati (ligan/waters/modified residues)")
    if n_altloc:
        warnings.append(f"{n_altloc} atom altloc selain blank/A dilewati")
    return _finalize_structure(path, "pdb", records, n_hetatm, n_altloc, chain, warnings)


def parse_structure(path: Path, chain: str | None = None) -> StructureRecord:
    path = Path(path)
    if not path.is_file():
        raise InferenceError(f"File struktur tidak ditemukan: {path}")
    suffix = path.suffix.lower()
    if suffix in {".cif", ".mmcif"}:
        return parse_cif(path, chain=chain)
    if suffix in {".pdb", ".ent"}:
        return parse_pdb(path, chain=chain)
    raise InferenceError(
        f"{path.name}: format struktur {suffix!r} tidak didukung; gunakan .cif/.mmcif/.pdb/.ent"
    )


# ---------------------------------------------------------------------------
# PAE dan fitur per-residu
# ---------------------------------------------------------------------------

def parse_pae(path: Path, n_res: int) -> np.ndarray:
    """Baca matriks PAE apa adanya; tidak ada transpose/reshape."""
    path = Path(path)
    if not path.is_file():
        raise InferenceError(f"File PAE tidak ditemukan: {path}")
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InferenceError(f"{path.name}: JSON PAE tidak valid: {exc}") from exc

    if isinstance(doc, dict) and "predicted_aligned_error" in doc:
        matrix = doc["predicted_aligned_error"]
    elif isinstance(doc, list) and doc and isinstance(doc[0], dict) and "predicted_aligned_error" in doc[0]:
        matrix = doc[0]["predicted_aligned_error"]
    elif isinstance(doc, list) and doc and all(isinstance(row, list) for row in doc):
        matrix = doc
    else:
        raise InferenceError(f"{path.name}: format PAE tidak dikenali")

    try:
        pae = np.asarray(matrix, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise InferenceError(f"{path.name}: matriks PAE bukan angka") from exc
    if pae.ndim != 2 or pae.shape != (n_res, n_res):
        raise InferenceError(
            f"{path.name}: shape PAE {pae.shape} != ({n_res}, {n_res})"
        )
    if not np.all(np.isfinite(pae)):
        raise InferenceError(f"{path.name}: PAE mengandung nilai non-finite/NaN")
    if float(pae.min()) < 0.0:
        raise InferenceError(f"{path.name}: PAE negatif ({float(pae.min())})")
    return pae


def compute_features(
    structure: StructureRecord,
    pae: np.ndarray,
    radius: float = RADIUS_ANGSTROM,
    window: int = PAE_LOCAL_WINDOW,
) -> pd.DataFrame:
    """Bangun tabel fitur per-residu; error bila ada residu tanpa tetangga."""
    n = structure.n_residues
    if n < 2:
        raise InferenceError(
            f"{structure.path.name}: hanya {n} residu; fitur PAE lokal/spasial tidak terdefinisi"
        )
    if pae.shape != (n, n):
        raise InferenceError(
            f"{structure.path.name}: PAE {pae.shape} != ({n}, {n}) untuk {n} residu"
        )

    coords = np.asarray([r.ca_xyz for r in structure.residues], dtype=np.float64)
    plddt = np.asarray([r.plddt_ca for r in structure.residues], dtype=np.float64)
    if coords.shape != (n, 3):
        raise InferenceError(f"{structure.path.name}: koordinat CA tidak lengkap")

    dist = np.linalg.norm(coords[:, None, :] - coords[None, :, :], axis=2)
    mask = dist <= float(radius)
    np.fill_diagonal(mask, False)
    density = mask.sum(axis=1)
    zero = np.where(density == 0)[0]
    if zero.size:
        positions = (zero + 1)[:10].tolist()
        raise InferenceError(
            f"{structure.path.name}: {zero.size} residu tanpa tetangga pada radius "
            f"{radius:g} A (posisi {positions}); tidak ada imputasi"
        )

    rows = []
    for i, res in enumerate(structure.residues):
        lo = max(0, i - window)
        hi = min(n, i + window + 1)
        local_vals = [pae[i, j] for j in range(lo, hi) if j != i]
        if not local_vals:
            raise InferenceError(
                f"{structure.path.name}:{res.sequence_position}: PAE lokal kosong"
            )
        neigh = mask[i]
        rows.append({
            "sequence_position": i + 1,
            "amino_acid": res.amino_acid,
            "amino_acid_type": AA_TYPE[res.amino_acid],
            "hydropathy_kd": float(KD_HYDROPATHY[res.amino_acid]),
            "charge_ph7": float(CHARGE_PH7.get(res.amino_acid, 0)),
            "n_atoms": int(res.n_atoms),
            "plddt_ca": round(float(res.plddt_ca), 2),
            # Base PAE features di dataset Stage 9.5/10.2 disimpan pada presisi
            # float penuh (tidak dibulatkan); pertahankan definisi itu.
            "pae_mean_row": float(pae[i].mean()),
            "pae_mean_col": float(pae[:, i].mean()),
            "pae_local_mean_k10": float(np.mean(local_vals)),
            "spatial_density_12a": int(density[i]),
            "spatial_plddt_mean_12a": round(float(plddt[neigh].mean()), 3),
            "spatial_pae_mean_12a": round(float(pae[i, neigh].mean()), 3),
        })

    df = pd.DataFrame(rows, columns=RESIDUE_COLUMNS)
    if df.isna().any().any():
        raise InferenceError(f"{structure.path.name}: fitur mengandung NaN")
    return df


def build_model_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Bangun X 16 kolom dengan urutan yang dibekukan; validasi ketat."""
    missing = [c for c in RESIDUE_COLUMNS if c not in df.columns]
    if missing:
        raise InferenceError(f"Tabel fitur kehilangan kolom: {missing}")
    bad_types = sorted(set(df["amino_acid_type"]) - set(AA_TYPES))
    if bad_types:
        raise InferenceError(f"amino_acid_type tidak dikenal: {bad_types}")

    X = df[BASE_FEATURES + SPATIAL_FEATURES].astype(float).copy()
    for t in AA_TYPES:
        X[f"aa_{t}"] = (df["amino_acid_type"] == t).astype(float)
    X = X[FEATURE_NAMES]
    if X.shape[1] != 16:
        raise InferenceError(f"X harus 16 kolom, ditemukan {X.shape[1]}")
    if X.isna().any().any():
        raise InferenceError("X mengandung NaN; tidak ada imputasi")
    if not np.all(np.isfinite(X.to_numpy(dtype=np.float64))):
        raise InferenceError("X mengandung nilai non-finite")
    return X


# ---------------------------------------------------------------------------
# Unduhan AFDB (cache lokal)
# ---------------------------------------------------------------------------

def _validate_afdb_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != AFDB_HOST:
        raise InferenceError(f"URL AFDB tidak aman/tidak dikenal: {url}")


def _http_get(url: str, max_bytes: int) -> bytes:
    _validate_afdb_url(url)
    req = Request(url, headers={"User-Agent": "ai-biotech-stage11/1.0"})
    with urlopen(req, timeout=60) as resp:
        length = resp.headers.get("Content-Length")
        if length is not None and int(length) > max_bytes:
            raise InferenceError(f"Respons {url} melebihi batas {max_bytes} byte")
        data = resp.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise InferenceError(f"Respons {url} melebihi batas {max_bytes} byte")
    return data


def _download_atomic(url: str, dest: Path, max_bytes: int) -> None:
    _validate_afdb_url(url)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".part")
    req = Request(url, headers={"User-Agent": "ai-biotech-stage11/1.0"})
    try:
        with urlopen(req, timeout=60) as resp, tmp.open("wb") as fh:
            length = resp.headers.get("Content-Length")
            if length is not None and int(length) > max_bytes:
                raise InferenceError(f"Respons {url} melebihi batas {max_bytes} byte")
            total = 0
            for chunk in iter(lambda: resp.read(1024 * 1024), b""):
                total += len(chunk)
                if total > max_bytes:
                    raise InferenceError(f"Respons {url} melebihi batas {max_bytes} byte")
                fh.write(chunk)
        if tmp.stat().st_size == 0:
            raise InferenceError(f"Unduhan {url} kosong")
        tmp.replace(dest)
    finally:
        if tmp.exists():
            tmp.unlink()


def fetch_afdb_entry(accession: str, cache_dir: Path | None = None) -> AFDBEntry:
    """Ambil entri kanonik AF-<ACC>-F1 dari AlphaFold DB + PAE, dengan cache."""
    acc = accession.strip().upper()
    if not ACCESSION_RE.fullmatch(acc):
        raise InferenceError(
            f"UniProt accession {accession!r} tidak valid (harus 6-10 karakter A-Z/0-9)"
        )
    cache = Path(cache_dir) if cache_dir is not None else default_cache_dir()
    cache.mkdir(parents=True, exist_ok=True)

    api_url = AFDB_API.format(acc=acc)
    api_bytes = _http_get(api_url, MAX_API_BYTES)
    try:
        api_doc = json.loads(api_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InferenceError(f"Respons API AFDB untuk {acc} bukan JSON valid") from exc
    entries = api_doc if isinstance(api_doc, list) else [api_doc]
    if not entries:
        raise InferenceError(f"AFDB tidak mengembalikan entri untuk {acc}")

    entry_id = f"AF-{acc}-F1"
    entry = next((e for e in entries if e.get("entryId") == entry_id), None)
    if entry is None:
        available = [str(e.get("entryId")) for e in entries]
        raise InferenceError(
            f"{acc}: entri kanonik {entry_id} tidak tersedia di AFDB "
            f"(entri yang ada: {available}). Gunakan --structure/--pae untuk file lokal."
        )
    if str(entry.get("uniprotAccession", "")).upper() != acc:
        raise InferenceError(
            f"{acc}: uniprotAccession API tidak cocok: {entry.get('uniprotAccession')!r}"
        )
    official_seq = str(entry.get("uniprotSequence", "")).upper()
    checksum = str(entry.get("sequenceChecksum", ""))
    if not official_seq or not checksum:
        raise InferenceError(f"{acc}: API AFDB tidak menyertakan sequence/checksum")

    cif_url = str(entry.get("cifUrl", ""))
    pae_url = str(entry.get("paeDocUrl", ""))
    if not cif_url or not pae_url:
        raise InferenceError(f"{acc}: API AFDB tidak menyertakan cifUrl/paeDocUrl")
    _validate_afdb_url(cif_url)
    _validate_afdb_url(pae_url)

    cif_name = Path(urlparse(cif_url).path).name
    pae_name = Path(urlparse(pae_url).path).name
    if not cif_name.endswith(".cif") or not pae_name.endswith(".json"):
        raise InferenceError(f"{acc}: nama file AFDB tidak dikenali ({cif_name}, {pae_name})")
    cif_path = cache / cif_name
    pae_path = cache / pae_name
    meta_path = cache / f"api_{acc}.json"

    cache_hit = cif_path.is_file() and pae_path.is_file()
    if not cif_path.is_file():
        _download_atomic(cif_url, cif_path, MAX_CIF_BYTES)
    if not pae_path.is_file():
        _download_atomic(pae_url, pae_path, MAX_PAE_BYTES)
    meta_path.write_text(
        json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    version_match = re.search(r"-model_v(\d+)\.cif$", cif_name)
    version = version_match.group(1) if version_match else str(entry.get("latestVersion", ""))
    return AFDBEntry(
        accession=acc,
        entry_id=entry_id,
        version=version,
        sequence=official_seq,
        sequence_checksum=checksum,
        chain_id=str(entry.get("chainId", "")),
        cif_path=cif_path,
        pae_path=pae_path,
        metadata_path=meta_path,
        cache_hit=cache_hit,
        metadata=entry,
    )


def verify_afdb_structure(structure: StructureRecord, entry: AFDBEntry) -> None:
    """Validasi sekuens/checksum/chain AFDB; berhenti bila tidak cocok."""
    if structure.sequence != entry.sequence:
        raise InferenceError(
            f"{entry.accession}: sekuens struktur ({len(structure.sequence)} aa) != "
            f"uniprotSequence API ({len(entry.sequence)} aa)"
        )
    md5 = hashlib.md5(structure.sequence.encode("ascii")).hexdigest()
    if md5 != entry.sequence_checksum:
        raise InferenceError(
            f"{entry.accession}: MD5 sekuens {md5} != sequenceChecksum API {entry.sequence_checksum}"
        )
    if entry.chain_id and structure.chain_ids != [entry.chain_id]:
        raise InferenceError(
            f"{entry.accession}: chain struktur {structure.chain_ids} != chainId API "
            f"{entry.chain_id!r}"
        )


def find_sibling_pae(structure_path: Path) -> Path:
    """Cari PAE AFDB di sebelah file struktur (pola nama resmi AFDB)."""
    path = Path(structure_path)
    name = path.name
    match = re.match(r"^(.*)-model_(v\d+)\.(?:cif|pdb)$", name, flags=re.IGNORECASE)
    candidates = []
    if match:
        prefix, version = match.group(1), match.group(2)
        candidates.append(path.with_name(f"{prefix}-predicted_aligned_error_{version}.json"))
    candidates.extend([
        path.with_name(path.stem + ".pae.json"),
        path.with_name(path.stem + "_pae.json"),
    ])
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise InferenceError(
        f"PAE tidak ditemukan untuk {path.name}. PAE wajib karena 6/16 fitur "
        "diturunkan dari matriks PAE. Berikan --pae <file.json>."
    )
