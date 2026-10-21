#!/usr/bin/env python3
"""
export_model.py - Stage 11.1: latih ulang golden LightGBM dan simpan artefak inferensi.

Alur (semua deterministik, tanpa timestamp):
  1. Verifikasi dataset terkalibrasi (SHA256, 55.503 baris, 102 protein, 955 positif).
  2. Hitung ulang OOF 102-fold LOGO dengan konfigurasi golden `lgbm__032c38ffe37f`.
  3. Bandingkan OOF dengan metrik golden Stage 10.3 (gagal keras bila berbeda).
  4. Latih kalibrator sigmoid dan isotonic pada skor OOF; deploy sigmoid.
  5. Latih model final pada SELURUH 55.503 baris.
  6. Simpan model + kalibrator + daftar fitur ke results/models/golden_lightgbm_12a.joblib.

Catatan:
  - Kalibrator dilatih pada OOF (in-sample calibration fit), bukan estimasi performa
    eksternal. Skor model final pada data training juga in-sample, bukan validasi.
  - Sigmoid dipilih karena rank-preserving dan tidak menciptakan ties; isotonic
    disimpan sebagai pembanding audit.
  - Enam kolom `oof_*` di dataset adalah artefak audit Stage 10.2 dan TIDAK PERNAH
    masuk sebagai fitur (C28).

Contoh:
  python src/export_model.py
  python src/export_model.py --reference-oof /path/ke/oof_golden.npz
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import joblib
import lightgbm
import numpy as np
import pandas as pd
import scipy
import sklearn
from scipy.stats import pearsonr, rankdata, spearmanr
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import auc, log_loss, precision_recall_curve, roc_auc_score

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from inference_features import (  # noqa: E402
    AA_TYPE,
    AA_TYPES,
    BASE_FEATURES,
    FEATURE_NAMES,
    RADIUS_ANGSTROM,
    SPATIAL_FEATURES,
    build_model_matrix,
    sha256_file,
)

PROJECT_ROOT = SRC_DIR.parent
DEFAULT_DATASET = PROJECT_ROOT / "results" / "dataset" / "production_dataset_100_calibrated.csv"
DEFAULT_ARTIFACT = PROJECT_ROOT / "results" / "models" / "golden_lightgbm_12a.joblib"

EXPECTED_DATASET_SHA256 = "2c4bcb3da7dfe4de82a95902f6fa3156e656cb5aece521b54d427cb42220ea3a"
EXPECTED_DATASET_BYTES = 9_667_972
EXPECTED_ROWS = 55_503
EXPECTED_PROTEINS = 102
EXPECTED_POSITIVES = 955
EXPECTED_ZERO_POSITIVE = 24
EXPECTED_EVALUABLE_FOLDS = 78

GOLDEN_CONFIG_ID = "lgbm__032c38ffe37f"
GOLDEN_PARAMS = {
    "n_estimators": 100,
    "max_depth": 6,
    "num_leaves": 31,
    "learning_rate": 0.05,
    "subsample": 0.75,
    "subsample_freq": 1,
    "colsample_bytree": 0.9,
    "min_child_samples": 20,
    "scale_pos_weight": 20.0,
}
MODEL_KWARGS = {
    "num_threads": 1,
    "verbosity": -1,
    "force_col_wise": True,
    "deterministic": True,
    "random_state": 42,
}

# Nilai ini harus identik dengan Stage 10.3 final/summary_golden.json.
EXPECTED_OOF_METRICS = {
    "rows": EXPECTED_ROWS,
    "proteins": EXPECTED_PROTEINS,
    "positives": EXPECTED_POSITIVES,
    "evaluable_folds": EXPECTED_EVALUABLE_FOLDS,
    "folds": EXPECTED_PROTEINS,
    "median_roc": 0.8411303035397238,
    "median_pr": 0.16932711453766564,
    "iqr_roc": 0.1445687565934124,
    "iqr_pr": 0.1737486008654875,
    "median_gain": 5.485997679178284,
    "pooled_roc": 0.8130695401753852,
    "pooled_pr": 0.11415424453717186,
    "pooled_gain": 6.634453439315863,
    "within_z_roc": 0.7709452494311173,
    "within_rank_roc": 0.7690198593524623,
    "brier": 0.052005301382412175,
    "log_loss": 0.1917081114320558,
    "ece": 0.12283773089414424,
    "mean_pred": 0.14004400803231695,
    "between_protein_auc": 0.7750865051903114,
    "between_spearman": 0.5270361538563072,
    "between_pearson": 0.476596833370302,
    "zero_positive_proteins": EXPECTED_ZERO_POSITIVE,
}

OOF_COLUMNS = [
    "oof_xgb_raw", "oof_xgb_isotonic", "oof_xgb_sigmoid",
    "oof_rf_raw", "oof_rf_isotonic", "oof_rf_sigmoid",
]

CALIBRATION_EPS = 1e-6


class ExportError(RuntimeError):
    pass


# ---------------------------------------------------------------------------
# Metrik (identik dengan Stage 10.3)
# ---------------------------------------------------------------------------

def pr_auc(y: np.ndarray, p: np.ndarray) -> float:
    prec, rec, _ = precision_recall_curve(y, p)
    return float(auc(rec, prec))


def within_z(groups: np.ndarray, scores: np.ndarray) -> np.ndarray:
    out = np.empty_like(scores, dtype=float)
    for g in np.unique(groups):
        m = groups == g
        s = scores[m]
        sd = s.std()
        out[m] = (s - s.mean()) / sd if sd > 0 else 0.0
    return out


def within_rank(groups: np.ndarray, scores: np.ndarray) -> np.ndarray:
    out = np.empty_like(scores, dtype=float)
    for g in np.unique(groups):
        m = groups == g
        out[m] = rankdata(scores[m]) / m.sum()
    return out


def ece_quantile10(y: np.ndarray, p: np.ndarray, bins: int = 10) -> float:
    edges = np.unique(np.quantile(p, np.linspace(0, 1, bins + 1)))
    if len(edges) < 2:
        return float(abs(y.mean() - p.mean()))
    idx = np.clip(np.searchsorted(edges, p, side="right") - 1, 0, len(edges) - 2)
    total = 0.0
    for b in range(len(edges) - 1):
        m = idx == b
        if m.any():
            total += m.mean() * abs(float(y[m].mean()) - float(p[m].mean()))
    return float(total)


def fold_metrics(y: np.ndarray, groups: np.ndarray, oof: np.ndarray) -> pd.DataFrame:
    rows = []
    for g in sorted(set(groups)):
        m = groups == g
        n = int(m.sum())
        npos = int(y[m].sum())
        rec = {"protein": g, "n": n, "pos": npos, "prev": npos / n if n else np.nan,
               "roc": np.nan, "pr": np.nan}
        if npos:
            rec["roc"] = float(roc_auc_score(y[m], oof[m]))
            rec["pr"] = pr_auc(y[m], oof[m])
        rows.append(rec)
    return pd.DataFrame(rows)


def summarize_oof(y: np.ndarray, groups: np.ndarray, oof: np.ndarray) -> dict:
    folds = fold_metrics(y, groups, oof)
    ev = folds.dropna(subset=["roc", "pr"])
    med = ev[["roc", "pr"]].median()
    q1 = ev[["roc", "pr"]].quantile(0.25)
    q3 = ev[["roc", "pr"]].quantile(0.75)
    per = pd.DataFrame({"g": groups, "s": oof, "y": y}).groupby("g").agg(
        mean_score=("s", "mean"), prev=("y", "mean"), n=("y", "size")
    )
    cls = (per["prev"] > per["prev"].median()).astype(int)
    between_auc = (
        float(roc_auc_score(cls, per["mean_score"])) if cls.nunique() == 2 else None
    )
    return {
        "rows": int(len(y)),
        "proteins": int(len(set(groups))),
        "positives": int(y.sum()),
        "prevalence": float(y.mean()),
        "evaluable_folds": int(len(ev)),
        "folds": int(len(folds)),
        "median_roc": float(med["roc"]),
        "median_pr": float(med["pr"]),
        "iqr_roc": float(q3["roc"] - q1["roc"]),
        "iqr_pr": float(q3["pr"] - q1["pr"]),
        "median_gain": float((ev["pr"] / ev["prev"]).median()),
        "pooled_roc": float(roc_auc_score(y, oof)),
        "pooled_pr": float(pr_auc(y, oof)),
        "pooled_gain": float(pr_auc(y, oof) / y.mean()),
        "within_z_roc": float(roc_auc_score(y, within_z(groups, oof))),
        "within_rank_roc": float(roc_auc_score(y, within_rank(groups, oof))),
        "brier": float(np.mean((oof - y) ** 2)),
        "log_loss": float(log_loss(y, np.clip(oof, 1e-15, 1 - 1e-15), labels=[0, 1])),
        "ece": float(ece_quantile10(y, oof)),
        "mean_pred": float(oof.mean()),
        "between_protein_auc": between_auc,
        "between_spearman": float(spearmanr(per["mean_score"], per["prev"]).statistic),
        "between_pearson": float(pearsonr(per["mean_score"], per["prev"]).statistic),
        "zero_positive_proteins": int((folds["pos"] == 0).sum()),
    }


def probability_metrics(y: np.ndarray, p: np.ndarray) -> dict:
    p = np.asarray(p, dtype=float)
    return {
        "mean": float(p.mean()),
        "min": float(p.min()),
        "max": float(p.max()),
        "brier": float(np.mean((p - y) ** 2)),
        "log_loss": float(log_loss(y, np.clip(p, 1e-15, 1 - 1e-15), labels=[0, 1])),
        "ece_quantile10": float(ece_quantile10(y, p)),
        "unique_values": int(np.unique(p).size),
    }


# ---------------------------------------------------------------------------
# Dataset dan OOF
# ---------------------------------------------------------------------------

def validate_dataset(df: pd.DataFrame, path: Path, allow_change: bool) -> dict:
    if not path.is_file():
        raise ExportError(f"Dataset tidak ditemukan: {path}")

    actual_sha = sha256_file(path)
    actual_bytes = path.stat().st_size
    if not allow_change:
        if actual_sha != EXPECTED_DATASET_SHA256:
            raise ExportError(
                f"SHA256 dataset tidak cocok.\n  diharapkan: {EXPECTED_DATASET_SHA256}\n"
                f"  dihitung  : {actual_sha}\n"
                "Artefak produksi harus dilatih pada dataset Stage 10.2 yang diaudit. "
                "Gunakan --allow-dataset-change hanya bila ini disengaja."
            )
        if actual_bytes != EXPECTED_DATASET_BYTES:
            raise ExportError(
                f"Ukuran dataset {actual_bytes} != {EXPECTED_DATASET_BYTES} byte"
            )

    required = (
        ["uniprot_id", "sequence_position", "amino_acid", "amino_acid_type", "target_y"]
        + BASE_FEATURES + SPATIAL_FEATURES
    )
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ExportError(f"Kolom wajib tidak ada: {missing}")
    leaked = [c for c in OOF_COLUMNS if c in FEATURE_NAMES]
    if leaked:
        raise ExportError(f"Kolom OOF bocor ke daftar fitur: {leaked}")

    if df[required].isna().any().any():
        bad = df[required].isna().sum()
        raise ExportError(f"Dataset mengandung nilai kosong:\n{bad[bad > 0]}")

    y = df["target_y"].astype(int).to_numpy()
    groups = df["uniprot_id"].astype(str).to_numpy()
    zero_positive = int(
        (pd.DataFrame({"g": groups, "y": y}).groupby("g")["y"].sum() == 0).sum()
    )
    evaluable = int(
        (pd.DataFrame({"g": groups, "y": y}).groupby("g")["y"].sum() > 0).sum()
    )
    checks = {
        "rows": len(df),
        "proteins": len(set(groups)),
        "positives": int(y.sum()),
        "zero_positive_proteins": zero_positive,
        "evaluable_folds": evaluable,
    }
    expected = {
        "rows": EXPECTED_ROWS,
        "proteins": EXPECTED_PROTEINS,
        "positives": EXPECTED_POSITIVES,
        "zero_positive_proteins": EXPECTED_ZERO_POSITIVE,
        "evaluable_folds": EXPECTED_EVALUABLE_FOLDS,
    }
    if checks != expected:
        raise ExportError(f"Struktur dataset berbeda dari yang diaudit: {checks} != {expected}")

    if not set(np.unique(y)).issubset({0, 1}):
        raise ExportError(f"target_y bukan 0/1: {sorted(set(np.unique(y)))}")
    duplicates = int(df.duplicated(["uniprot_id", "sequence_position"]).sum())
    if duplicates:
        raise ExportError(f"Ada {duplicates} duplikat (uniprot_id, sequence_position)")

    for acc, part in df.groupby("uniprot_id", sort=True):
        positions = part["sequence_position"].astype(int).tolist()
        if positions != list(range(1, len(part) + 1)):
            raise ExportError(f"{acc}: sequence_position bukan 1..{len(part)} berurutan")
        aa = part["amino_acid"].astype(str).str.upper()
        types = part["amino_acid_type"].astype(str)
        expected_types = aa.map(AA_TYPE.get)
        if expected_types.isna().any():
            raise ExportError(f"{acc}: ada asam amino tidak dikenal")
        mismatch = int((types.to_numpy() != expected_types.to_numpy()).sum())
        if mismatch:
            raise ExportError(f"{acc}: {mismatch} amino_acid_type tidak konsisten dengan definisi beku")

    if not df["plddt_ca"].between(0.0, 100.0).all():
        raise ExportError("plddt_ca di luar [0,100]")
    if not (df["spatial_density_12a"] > 0).all():
        raise ExportError("spatial_density_12a harus > 0 (tidak ada imputasi)")
    for col in ["pae_mean_row", "pae_mean_col", "pae_local_mean_k10",
                "spatial_plddt_mean_12a", "spatial_pae_mean_12a"]:
        if not (df[col] >= 0).all():
            raise ExportError(f"{col} mengandung nilai negatif")

    return {
        "path": str(path),
        "sha256": actual_sha,
        "bytes": actual_bytes,
        "rows": checks["rows"],
        "proteins": checks["proteins"],
        "positives": checks["positives"],
        "prevalence": float(y.mean()),
        "zero_positive_proteins": zero_positive,
        "evaluable_folds": evaluable,
    }


def compute_oof(X: pd.DataFrame, y: np.ndarray, groups: np.ndarray) -> np.ndarray:
    oof = np.empty(len(y), dtype=float)
    unique_groups = sorted(set(groups))
    for k, acc in enumerate(unique_groups, 1):
        te = groups == acc
        tr = ~te
        model = lightgbm.LGBMClassifier(**GOLDEN_PARAMS, **MODEL_KWARGS)
        model.fit(X.loc[tr], y[tr])
        oof[te] = model.predict_proba(X.loc[te])[:, 1]
        if k % 20 == 0 or k == len(unique_groups):
            print(f"  [OOF] {k:3d}/{len(unique_groups)} protein selesai", flush=True)
    if not np.all(np.isfinite(oof)):
        raise ExportError("OOF mengandung nilai non-finite")
    if float(oof.min()) < 0.0 or float(oof.max()) > 1.0:
        raise ExportError("OOF di luar [0,1]")
    return oof


def check_expected_oof(summary: dict) -> None:
    failures = []
    for key, expected in EXPECTED_OOF_METRICS.items():
        actual = summary[key]
        if isinstance(expected, int):
            if actual != expected:
                failures.append(f"{key}: {actual} != {expected}")
        else:
            if abs(float(actual) - float(expected)) > 1e-9:
                failures.append(f"{key}: {actual!r} != {expected!r}")
    if failures:
        raise ExportError(
            "OOF tidak mereproduksi metrik golden Stage 10.3. Artefak TIDAK dibuat.\n  "
            + "\n  ".join(failures)
        )


def load_reference_oof(path: Path):
    ref = np.load(path, allow_pickle=True)
    required = {"oof", "y", "groups"}
    missing = required - set(ref.files)
    if missing:
        raise ExportError(f"Reference OOF kehilangan array: {sorted(missing)}")
    return ref["oof"].astype(float), ref["y"].astype(int), ref["groups"].astype(str)


# ---------------------------------------------------------------------------
# Kalibrasi
# ---------------------------------------------------------------------------

def logit(p: np.ndarray) -> np.ndarray:
    p = np.clip(np.asarray(p, dtype=float), CALIBRATION_EPS, 1.0 - CALIBRATION_EPS)
    return np.log(p / (1.0 - p))


def fit_sigmoid(oof: np.ndarray, y: np.ndarray) -> LogisticRegression:
    z = logit(oof).reshape(-1, 1)
    model = LogisticRegression(C=1e6, solver="lbfgs", max_iter=1000, tol=1e-10)
    model.fit(z, y)
    if float(model.coef_[0, 0]) <= 0.0:
        raise ExportError(
            f"Koefisien kalibrator sigmoid non-positif ({model.coef_[0, 0]}); "
            "kalibrasi tidak monoton"
        )
    return model


def apply_sigmoid(model: LogisticRegression, scores: np.ndarray) -> np.ndarray:
    p = model.predict_proba(logit(scores).reshape(-1, 1))[:, 1]
    return np.clip(p, 0.0, 1.0)


def fit_isotonic(oof: np.ndarray, y: np.ndarray) -> IsotonicRegression:
    model = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
    model.fit(oof, y)
    return model


def apply_isotonic(model: IsotonicRegression, scores: np.ndarray) -> np.ndarray:
    return np.clip(model.predict(scores), 0.0, 1.0)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _rel(path: Path) -> str:
    try:
        return Path(path).resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return Path(path).resolve().as_posix()


def run(args) -> int:
    dataset_path = Path(args.dataset)
    out_path = Path(args.out)

    print(f"[i] Dataset : {dataset_path}")
    df = pd.read_csv(dataset_path)
    dataset_meta = validate_dataset(df, dataset_path, args.allow_dataset_change)
    print(
        f"[i] Verifikasi dataset: {dataset_meta['rows']} baris, "
        f"{dataset_meta['proteins']} protein, {dataset_meta['positives']} positif, "
        f"SHA256 {dataset_meta['sha256'][:12]}..."
    )

    X = build_model_matrix(df)
    if list(X.columns) != FEATURE_NAMES:
        raise ExportError(f"Urutan fitur X tidak sesuai kontrak: {list(X.columns)}")
    y = df["target_y"].astype(int).to_numpy()
    groups = df["uniprot_id"].astype(str).to_numpy()
    print(f"[i] X: {X.shape[0]} x {X.shape[1]} fitur")

    print("[i] Menghitung ulang OOF 102-fold LOGO (golden LightGBM)...")
    oof = compute_oof(X, y, groups)
    oof_summary = summarize_oof(y, groups, oof)
    check_expected_oof(oof_summary)
    print(
        f"[OK] OOF mereproduksi golden: median ROC {oof_summary['median_roc']:.10f}, "
        f"median PR {oof_summary['median_pr']:.10f}, pooled PR {oof_summary['pooled_pr']:.10f}"
    )

    if args.reference_oof is not None:
        ref_oof, ref_y, ref_groups = load_reference_oof(Path(args.reference_oof))
        if not np.array_equal(ref_y, y):
            raise ExportError("Reference OOF: y tidak identik dengan dataset")
        if not np.array_equal(ref_groups, groups):
            raise ExportError("Reference OOF: groups tidak identik dengan dataset")
        max_diff = float(np.max(np.abs(oof - ref_oof)))
        print(f"[OK] Reference OOF: max |diff| = {max_diff:.3e}")
        if max_diff > 1e-12:
            raise ExportError(f"OOF berbeda dari reference (max diff {max_diff:.3e})")

    print("[i] Melatih kalibrator pada skor OOF...")
    sig_model = fit_sigmoid(oof, y)
    iso_model = fit_isotonic(oof, y)
    sig_scores = apply_sigmoid(sig_model, oof)
    iso_scores = apply_isotonic(iso_model, oof)

    raw_metrics = probability_metrics(y, oof)
    sig_metrics = probability_metrics(y, sig_scores)
    iso_metrics = probability_metrics(y, iso_scores)
    print(
        f"[i] Raw      : Brier {raw_metrics['brier']:.6f} | ECE {raw_metrics['ece_quantile10']:.6f} "
        f"| mean {raw_metrics['mean']:.6f}"
    )
    print(
        f"[i] Sigmoid  : Brier {sig_metrics['brier']:.6f} | ECE {sig_metrics['ece_quantile10']:.6f} "
        f"| mean {sig_metrics['mean']:.6f} | unique {sig_metrics['unique_values']}"
    )
    print(
        f"[i] Isotonic : Brier {iso_metrics['brier']:.6f} | ECE {iso_metrics['ece_quantile10']:.6f} "
        f"| mean {iso_metrics['mean']:.6f} | unique {iso_metrics['unique_values']}"
    )

    print("[i] Melatih model final pada seluruh 55.503 baris...")
    final_model = lightgbm.LGBMClassifier(**GOLDEN_PARAMS, **MODEL_KWARGS)
    final_model.fit(X, y)
    if list(final_model.feature_name_) != FEATURE_NAMES:
        raise ExportError(
            f"feature_name_ LightGBM tidak sesuai kontrak: {list(final_model.feature_name_)}"
        )
    raw_in = final_model.predict_proba(X)[:, 1]
    sig_in = apply_sigmoid(sig_model, raw_in)
    iso_in = apply_isotonic(iso_model, raw_in)

    feature_importance = {
        name: float(value)
        for name, value in zip(FEATURE_NAMES, final_model.feature_importances_)
    }
    payload = {
        "artifact_version": "stage11-1.0",
        "artifact_name": "golden_lightgbm_12a",
        "stage": "11.1",
        "config_id": GOLDEN_CONFIG_ID,
        "model_family": "lightgbm",
        "model": final_model,
        "calibrator": {
            "method": "sigmoid",
            "input": "logit(raw_probability)",
            "clip_eps": CALIBRATION_EPS,
            "estimator": sig_model,
        },
        "calibrator_isotonic": {
            "method": "isotonic",
            "input": "raw_probability",
            "estimator": iso_model,
        },
        "calibrator_selection": {
            "deployed": "sigmoid",
            "rule": (
                "Sigmoid dipilih sebelum evaluasi: rank-preserving (tidak mengubah "
                "urutan skor) dan tidak menciptakan ties; isotonic hanya pembanding audit."
            ),
            "isotonic_ties_warning": (
                f"Isotonic hanya menghasilkan {iso_metrics['unique_values']} nilai unik "
                f"pada {len(y)} skor OOF."
            ),
        },
        "feature_names": FEATURE_NAMES,
        "base_feature_names": BASE_FEATURES + SPATIAL_FEATURES,
        "amino_acid_types": list(AA_TYPES),
        "radius_angstrom": RADIUS_ANGSTROM,
        "pae_local_window": 10,
        "model_params": GOLDEN_PARAMS,
        "model_kwargs": MODEL_KWARGS,
        "dataset": {
            "path": _rel(dataset_path),
            "sha256": dataset_meta["sha256"],
            "bytes": dataset_meta["bytes"],
            "rows": dataset_meta["rows"],
            "proteins": dataset_meta["proteins"],
            "positives": dataset_meta["positives"],
            "prevalence": dataset_meta["prevalence"],
            "zero_positive_proteins": dataset_meta["zero_positive_proteins"],
            "evaluable_folds": dataset_meta["evaluable_folds"],
        },
        "oof": {
            "metrics": oof_summary,
            "score_sha256_float64": hashlib.sha256(
                np.ascontiguousarray(oof, dtype=np.float64).tobytes()
            ).hexdigest(),
            "note": (
                "OOF dihitung ulang dari dataset dengan 102-fold LOGO; metrik harus "
                "identik dengan Stage 10.3 (diverifikasi saat export)."
            ),
        },
        "calibration": {
            "deployed": "sigmoid",
            "raw": raw_metrics,
            "sigmoid": sig_metrics,
            "isotonic": iso_metrics,
            "note": (
                "Kalibrator dilatih pada skor OOF yang sama dengan evaluasi; ini "
                "in-sample calibration fit, bukan estimasi performa pada protein baru."
            ),
        },
        "final_model": {
            "trained_on": f"all {len(df)} rows / {dataset_meta['proteins']} proteins",
            "in_sample_raw": probability_metrics(y, raw_in),
            "in_sample_sigmoid": probability_metrics(y, sig_in),
            "in_sample_isotonic": probability_metrics(y, iso_in),
            "warning": (
                "Metrik in-sample hanya sanity check; model final melihat seluruh "
                "label training. Jangan laporkan sebagai performa/validasi."
            ),
        },
        "feature_importance": feature_importance,
        "training_source": {
            "structure_source": "AlphaFold DB v6",
            "dataset_stage": "Stage 10.2 calibrated dataset; golden config Stage 10.3",
            "label_policy": "UniProt Active site + Binding site (A+B)",
        },
        "limitations": [
            "Tidak ada validasi eksternal; seluruh 102 protein pernah dipakai dalam tuning/LOGO.",
            "Kalibrator sigmoid dilatih pada OOF; distribusi skor model final dapat berbeda.",
            "Metrik OOF optimistis (selection optimism; nested median PR Stage 10.3 = 0.1550).",
            "Fitur spasial hanya intra-chain dan memakai koordinat CA; bukan simulasi fisika.",
            "PAE wajib ada; PDB eksperimental tanpa PAE/pLDDT tidak didukung.",
        ],
        "generated_by": "src/export_model.py",
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
            "lightgbm": lightgbm.__version__,
            "scipy": scipy.__version__,
            "joblib": joblib.__version__,
        },
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(payload, out_path, compress=3)
    artifact_sha = sha256_file(out_path)
    artifact_bytes = out_path.stat().st_size

    print(f"[OK] Artefak disimpan: {out_path}")
    print(f"     sha256 {artifact_sha}")
    print(f"     ukuran {artifact_bytes} byte")
    print(
        "[i] Sigmoid: z = %.10f * logit(p) + %.10f"
        % (float(sig_model.coef_[0, 0]), float(sig_model.intercept_[0]))
    )
    print("[i] Catatan: metrik in-sample BUKAN validasi; tidak ada validasi eksternal.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="export_model.py",
        description="Latih ulang golden LightGBM Stage 10.3 dan simpan artefak inferensi Stage 11.1.",
    )
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument(
        "--reference-oof", type=Path, default=None,
        help="opsional: file .npz OOF golden Stage 10.3 untuk verifikasi bit-level",
    )
    parser.add_argument(
        "--allow-dataset-change", action="store_true",
        help="izinkan dataset berbeda dari SHA256 Stage 10.2 (hanya untuk eksperimen)",
    )
    args = parser.parse_args(argv)

    try:
        return run(args)
    except (ExportError, ValueError) as exc:
        print(f"[!] {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
