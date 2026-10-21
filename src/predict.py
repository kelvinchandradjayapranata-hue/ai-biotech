#!/usr/bin/env python3
"""
predict.py - Stage 11.2: CLI inferensi mandiri untuk prediksi Active/Binding Site.

Input:
  --uniprot <ACC>                  unduh entri kanonik AF-<ACC>-F1 + PAE dari AFDB (cache)
  --structure <file.cif|file.pdb>  struktur lokal + --pae <file.json>
                                   (PAE juga dicari otomatis dengan pola nama AFDB)

Output default: CSV per-residu ke stdout
  protein_id, uniprot_id, sequence_position, amino_acid, plddt_ca,
  probability_raw, probability_calibrated, predicted_active_binding

Syarat input:
  - Satu chain (atau pilih dengan --chain).
  - Penomoran residu 1..N berurutan; tidak ada renumbering otomatis.
  - B-factor = pLDDT bergaya AlphaFold DB (0-100), bukan B-factor eksperimen.
  - Matriks PAE N x N; 6 dari 16 fitur diturunkan dari PAE.
  - Tidak ada imputasi: residu tanpa tetangga radius 12 A = error.

Contoh:
  python src/predict.py --uniprot P02144 --out results/predictions/P02144.csv
  python src/predict.py --structure AF-P02144-F1-model_v6.cif \
      --pae AF-P02144-F1-predicted_aligned_error_v6.json
  python src/predict.py --uniprot P00520 --threshold 0.5 --top 10 --out P00520.csv

Catatan:
  - Probabilitas terkalibrasi berasal dari kalibrator sigmoid yang dilatih pada OOF
    Stage 10.3. Ini bukan validasi eksternal dan bukan klaim biologis.
  - Ambang 0.5 hanya untuk tampilan; belum ada ambang yang divalidasi secara klinis.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import inference_features as inf  # noqa: E402

PROJECT_ROOT = SRC_DIR.parent
DEFAULT_ARTIFACT = PROJECT_ROOT / "results" / "models" / "golden_lightgbm_12a.joblib"


class PredictError(RuntimeError):
    pass


def load_artifact(path: Path) -> dict:
    path = Path(path)
    if not path.is_file():
        raise PredictError(
            f"Artefak tidak ditemukan: {path}\n"
            "Jalankan `python src/export_model.py` terlebih dahulu."
        )
    try:
        payload = joblib.load(path)
    except Exception as exc:  # joblib/pickle dapat gagal karena versi atau file rusak
        raise PredictError(f"Gagal memuat artefak {path.name}: {exc}") from exc
    required = {"model", "calibrator", "feature_names", "model_params", "dataset"}
    missing = required - set(payload)
    if missing:
        raise PredictError(f"Artefak kehilangan field: {sorted(missing)}")
    if list(payload["feature_names"]) != inf.FEATURE_NAMES:
        raise PredictError(
            "feature_names di artefak tidak sama dengan kontrak inference_features.py"
        )
    model = payload["model"]
    if hasattr(model, "feature_name_") and list(model.feature_name_) != inf.FEATURE_NAMES:
        raise PredictError(
            f"feature_name_ model tidak sesuai: {list(model.feature_name_)}"
        )
    if getattr(model, "n_features_in_", 16) != 16:
        raise PredictError(f"Model menerima {model.n_features_in_} fitur, bukan 16")
    return payload


def apply_calibrator(payload: dict, raw: np.ndarray) -> np.ndarray:
    cal = payload["calibrator"]
    method = cal.get("method")
    estimator = cal.get("estimator")
    if estimator is None:
        raise PredictError("Artefak tidak menyertakan estimator kalibrator")
    if method == "sigmoid":
        eps = float(cal.get("clip_eps", 1e-6))
        p = np.clip(np.asarray(raw, dtype=float), eps, 1.0 - eps)
        z = np.log(p / (1.0 - p)).reshape(-1, 1)
        calibrated = estimator.predict_proba(z)[:, 1]
    elif method == "isotonic":
        calibrated = estimator.predict(np.asarray(raw, dtype=float))
    else:
        raise PredictError(f"Metode kalibrator tidak didukung: {method!r}")
    calibrated = np.clip(np.asarray(calibrated, dtype=float), 0.0, 1.0)
    if not np.all(np.isfinite(calibrated)):
        raise PredictError("Kalibrator menghasilkan nilai non-finite")
    return calibrated


def resolve_input(args):
    warnings = []
    if args.uniprot:
        entry = inf.fetch_afdb_entry(args.uniprot, args.cache_dir)
        structure = inf.parse_structure(entry.cif_path, chain=args.chain)
        inf.verify_afdb_structure(structure, entry)
        pae = inf.parse_pae(entry.pae_path, structure.n_residues)
        if entry.version and entry.version != "6":
            warnings.append(
                f"AFDB versi {entry.version}; artefak dilatih pada fitur struktur AFDB v6. "
                "Distribusi fitur/probabilitas dapat bergeser."
            )
        source = f"AFDB v{entry.version} ({entry.entry_id})"
        return {
            "protein_id": entry.entry_id,
            "uniprot_id": entry.accession,
            "source": source,
            "structure": structure,
            "pae": pae,
            "structure_path": entry.cif_path,
            "pae_path": entry.pae_path,
            "afdb_version": entry.version,
            "cache_hit": entry.cache_hit,
            "warnings": warnings,
        }

    structure_path = Path(args.structure)
    structure = inf.parse_structure(structure_path, chain=args.chain)
    pae_path = Path(args.pae) if args.pae else inf.find_sibling_pae(structure_path)
    pae = inf.parse_pae(pae_path, structure.n_residues)
    warnings.extend(structure.warnings)
    warnings.append(
        "Struktur lokal: B-factor diasumsikan pLDDT (AFDB), dan PAE harus berasal "
        "dari prediksi yang sama. Predictor tidak bisa memverifikasi provenance ini."
    )
    if structure.fmt == "pdb":
        warnings.append(
            "PDB lokal: pastikan file dikonversi dari AFDB dan B-factor masih berisi pLDDT, "
            "bukan B-factor eksperimen."
        )
    return {
        "protein_id": args.name or structure_path.stem,
        "uniprot_id": "",
        "source": str(structure_path),
        "structure": structure,
        "pae": pae,
        "structure_path": structure_path,
        "pae_path": pae_path,
        "afdb_version": None,
        "cache_hit": None,
        "warnings": warnings,
    }


def run(args) -> int:
    if not (0.0 < args.threshold < 1.0):
        raise PredictError(f"--threshold harus di antara 0 dan 1, bukan {args.threshold}")
    if args.top < 0:
        raise PredictError("--top tidak boleh negatif")

    artifact_path = Path(args.artifact)
    payload = load_artifact(artifact_path)
    resolved = resolve_input(args)
    structure = resolved["structure"]
    pae = resolved["pae"]

    features = inf.compute_features(structure, pae)
    X = inf.build_model_matrix(features)
    if X.shape[1] != len(payload["feature_names"]):
        raise PredictError("Jumlah fitur X tidak sesuai artefak")

    raw = payload["model"].predict_proba(X)[:, 1]
    calibrated = apply_calibrator(payload, raw)
    labels = (calibrated >= args.threshold).astype(int)

    out_df = pd.DataFrame({
        "protein_id": resolved["protein_id"],
        "uniprot_id": resolved["uniprot_id"],
        "sequence_position": features["sequence_position"].astype(int),
        "amino_acid": features["amino_acid"],
        "plddt_ca": features["plddt_ca"].astype(float),
        "probability_raw": raw,
        "probability_calibrated": calibrated,
        "predicted_active_binding": labels,
    })

    if args.out and str(args.out) != "-":
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(out_path, index=False, lineterminator="\n", float_format="%.6f")
    else:
        out_df.to_csv(sys.stdout, index=False, lineterminator="\n", float_format="%.6f")

    if args.features_out:
        feat_path = Path(args.features_out)
        feat_path.parent.mkdir(parents=True, exist_ok=True)
        feature_table = pd.concat(
            [features[["sequence_position", "amino_acid", "amino_acid_type"]], X],
            axis=1,
        )
        feature_table.to_csv(
            feat_path, index=False, lineterminator="\n", float_format="%.17g"
        )

    max_idx = int(np.argmax(calibrated))
    top_records = []
    if args.top:
        top_idx = np.argsort(-calibrated, kind="stable")[: args.top]
        for i in top_idx:
            top_records.append({
                "sequence_position": int(features["sequence_position"].iloc[i]),
                "amino_acid": str(features["amino_acid"].iloc[i]),
                "probability_calibrated": round(float(calibrated[i]), 6),
            })

    summary = {
        "protein_id": resolved["protein_id"],
        "uniprot_id": resolved["uniprot_id"],
        "source": resolved["source"],
        "n_residues": int(len(out_df)),
        "threshold": float(args.threshold),
        "n_predicted_active_binding": int(labels.sum()),
        "fraction_predicted_active_binding": round(float(labels.mean()), 6),
        "mean_probability_raw": round(float(raw.mean()), 6),
        "mean_probability_calibrated": round(float(calibrated.mean()), 6),
        "max_probability_calibrated": round(float(calibrated[max_idx]), 6),
        "max_residue": {
            "sequence_position": int(features["sequence_position"].iloc[max_idx]),
            "amino_acid": str(features["amino_acid"].iloc[max_idx]),
        },
        "top_residues": top_records,
        "artifact": str(artifact_path),
        "artifact_sha256": inf.sha256_file(artifact_path),
        "structure_sha256": inf.sha256_file(Path(resolved["structure_path"])),
        "pae_sha256": inf.sha256_file(Path(resolved["pae_path"])),
        "afdb_version": resolved["afdb_version"],
        "cache_hit": resolved["cache_hit"],
        "warnings": resolved["warnings"],
        "note": (
            "Probabilitas terkalibrasi (sigmoid pada OOF) bukan validasi eksternal. "
            "Ambang hanya untuk tampilan, bukan cutoff biologis/klinis tervalidasi."
        ),
    }
    if not args.quiet:
        print(json.dumps(summary, indent=2, ensure_ascii=False), file=sys.stderr)
        if args.out and str(args.out) != "-":
            print(f"[OK] {len(out_df)} residu -> {args.out}", file=sys.stderr)
        if args.features_out:
            print(f"[OK] fitur 16 kolom -> {args.features_out}", file=sys.stderr)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="predict.py",
        description="Prediksi Active/Binding Site per-residu dari struktur AlphaFold + PAE.",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--uniprot", metavar="ACC", help="UniProt accession (entri kanonik AFDB)")
    source.add_argument("--structure", type=Path, help="file struktur lokal .cif/.mmcif/.pdb/.ent")
    parser.add_argument(
        "--pae", type=Path, default=None,
        help="file PAE JSON (wajib untuk --structure kecuali nama AFDB terdeteksi otomatis)",
    )
    parser.add_argument("--chain", default=None, help="chain ID (default: harus tepat satu chain)")
    parser.add_argument("--name", default=None, help="protein_id untuk output struktur lokal")
    parser.add_argument("--threshold", type=float, default=0.5,
                        help="ambang tampilan predicted_active_binding (default 0.5)")
    parser.add_argument("--out", type=Path, default=None, help="CSV output (default: stdout)")
    parser.add_argument("--features-out", type=Path, default=None,
                        help="opsional: CSV 16 fitur model per-residu")
    parser.add_argument("--top", type=int, default=5,
                        help="jumlah residu teratas di ringkasan (0 = nonaktif)")
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--cache-dir", type=Path, default=None,
                        help="cache AFDB (default: direktori cache OS / AI_BIOTECH_CACHE)")
    parser.add_argument("--quiet", action="store_true", help="jangan cetak ringkasan JSON")
    args = parser.parse_args(argv)

    if args.uniprot and args.pae:
        parser.error("--pae hanya dipakai dengan --structure (AFDB mengunduh PAE otomatis)")
    if args.structure is None and args.chain:
        parser.error("--chain hanya dipakai dengan --structure")

    try:
        return run(args)
    except (PredictError, inf.InferenceError, OSError) as exc:
        print(f"[!] {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
