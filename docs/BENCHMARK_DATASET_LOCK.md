# BENCHMARK DATASET LOCK — Stage 7 Dataset + Stage 8.2 Official Metrics

**Status: LOCKED**
**Lock date: 2026-10-20**
**Project: ai-biotech**

This document freezes the project's official benchmark dataset and the official
evaluation protocol. It is the reference for every metric reported from this point on.
The dataset is frozen at the byte level; the Stage 8.2 metrics are the only official
ML metrics until a new, explicitly versioned benchmark supersedes them.

---

## 1. Artifact Identity

| Field | Value |
|---|---|
| Authoritative path | `results/dataset/stage7_processed_dataset.csv` |
| Source copy (untracked) | `download/stage7_processed_dataset.csv` |
| SHA256 | `34f9dd27b1d11fb35155f1542e066a50110144cd84c62d91a28caa6ab9d99f61` |
| Size | 149,609 bytes |
| Rows | 1,098 residue records (plus header line; 1,099 lines total) |
| Columns | 27 |
| Proteins | 7 |
| Positives (`target_y = 1`) | 46 (4.19%) |
| Folds | 7 (`fold` 0–6), one protein per fold |
| Label policy | UniProt **Active site + Binding site** (policy A+B) |

The SHA256 was recomputed after copying into `results/dataset/` and matches the source
byte-for-byte. The copy under `download/` is **not** authoritative; it is retained only
as the original delivery artifact.

---

## 2. Provenance

`stage7_processed_dataset.csv` is a per-residue feature/label table derived from the
Stage 6 multi-protein feature extraction output:

- **Structural features:** Stage 6 `results/dataset/multi_protein_residue_features.csv`,
  itself derived from AlphaFold DB v6 CIF/PAE files validated in Stage 5.
- **Labels:** UniProtKB feature annotations fetched per accession; `target_y` marks
  residues annotated as **Active site** or **Binding site**.
- **Folds:** one protein per fold (`fold` 0–6), supporting leave-one-protein-out (LOGO)
  cross-validation with no residue-level leakage.
- **Schema change vs Stage 6:** the four zero-variance `plddt_atom_*` columns were
  dropped; `target_y` and `fold` were added. The remaining 25 columns are value-identical
  to the Stage 6 output.

**Audit evidence (independently checked):**

- 25 shared columns match Stage 6 values row-for-row.
- `target_y` matches UniProt Active site + Binding site positions for **7/7 proteins**
  (46 positions total).
- Fold assignment is one protein per fold; no protein appears in more than one fold.
- No synthetic/random feature columns are present. All structural values trace to the
  Stage 6 AFDB-derived table.

**Provenance gap (recorded honestly):** the script that generated this Stage 7 CSV is
not present in `src/`. The file arrived as a delivered artifact and was audited against
Stage 6 and UniProt. Rebuilding Stage 7 from source is therefore not currently a
one-command operation; the frozen artifact plus this document define the benchmark.

---

## 3. Schema

Column groups (27 total):

| Group | Columns |
|---|---|
| Protein identifiers | `protein_id`, `uniprot_accession`, `afdb_id`, `chain` |
| Residue identifiers | `residue_id`, `residue_name`, `one_letter_aa`, `sequence_position`, `sequence_length`, `amino_acid_type` |
| Sequence-derived features | `hydropathy_kd`, `charge_ph7` |
| Coordinates (non-invariant) | `ca_x`, `ca_y`, `ca_z`, `centroid_x`, `centroid_y`, `centroid_z` |
| Geometry / confidence features | `n_atoms`, `n_backbone_atoms`, `has_full_backbone`, `plddt_ca`, `pae_mean_row`, `pae_mean_col`, `pae_local_mean_k10` |
| Label | `target_y` |
| Fold assignment | `fold` |

Notes and known quirks:

- `n_backbone_atoms` is constant (`4`) and `has_full_backbone` is constant (`True`)
  across all 1,098 rows — zero variance, retained only because the artifact is frozen.
- `plddt_atom_*` columns are absent: they were redundant with `plddt_ca` in AFDB and
  were dropped in Stage 7.
- `charge_ph7` for histidine (H) is `0` (neutral at pH 7 under the Stage 3 rule).
- `ca_x/y/z` and `centroid_x/y/z` are **not** rotation/translation invariant; they are
  excluded from the Stage 8.2 feature set.
- `amino_acid_type` has exactly six categories used by Stage 8.2 one-hot encoding:

  | Category | Amino acids | Count |
  |---|---|---:|
  | nonpolar | A, I, L, M, V | 323 |
  | polar | C, N, Q, S, T | 241 |
  | basic | H, K, R | 169 |
  | acidic | D, E | 147 |
  | special | G, P | 136 |
  | aromatic | F, W, Y | 82 |

- `sequence_position` is 1-based within the UniProt sequence and matches the CIF
  residue numbering for all seven proteins.

---

## 4. Label Policy — A+B (Active site + Binding site)

`target_y = 1` if and only if the residue's `sequence_position` falls inside a UniProtKB
feature of type:

- **Active site**, or
- **Binding site**.

All other feature types are **negative** for this benchmark, including:

- generic **Site** annotations,
- **Metal binding** as a distinct feature type,
- **Modified residue**, **Cross-link**, **Disulfide bond**, and all other feature types.

Rationale: Active site + Binding site are the two annotation types that most directly
describe a residue's functional role and are consistently available for the seven
proteins. The generic `Site` type is broader and would inflate positives
inconsistently; it was therefore excluded.

**Important wording correction:** the Stage 8.2 summary describes the target as
“Active/Binding/Metal Sites.” That wording is imprecise. The audited dataset contains
Active site + Binding site only (46 positives). Metal-binding annotations are not
included as a separate source. Future reports must use the A+B definition, not the
looser wording.

---

## 5. Fold Map (Leave-One-Protein-Out)

| Fold | UniProt | Protein | Residues | Positives | Prevalence |
|---:|---|---|---:|---:|---:|
| 0 | P00441 | Superoxide dismutase [Cu-Zn] (SOD1) | 154 | 7 | 4.55% |
| 1 | P02144 | Myoglobin | 154 | 2 | 1.30% |
| 2 | P0DP23 | Calmodulin-1 | 149 | 20 | 13.42% |
| 3 | P42212 | Green fluorescent protein (GFP) | 238 | 0 | 0.00% |
| 4 | P61626 | Lysozyme C | 148 | 2 | 1.35% |
| 5 | P61823 | Ribonuclease pancreatic (RNase A) | 150 | 11 | 7.33% |
| 6 | P99999 | Cytochrome c | 105 | 4 | 3.81% |
| **Total** | | | **1,098** | **46** | **4.19%** |

GFP (fold 3) has **zero positives**. Its fold is therefore **unevaluable** for ROC-AUC
and PR-AUC; it is excluded from per-fold medians/IQRs but its residues remain in the
pooled evaluation (as negatives). This exclusion must be stated in every report.

---

## 6. Stage 8.2 — Official Evaluation Protocol

### 6.1 Feature set (13 features)

Seven invariant structural features:

1. `hydropathy_kd`
2. `charge_ph7`
3. `n_atoms`
4. `plddt_ca`
5. `pae_mean_row`
6. `pae_mean_col`
7. `pae_local_mean_k10`

Six one-hot columns derived from `amino_acid_type`:
`aa_acidic`, `aa_aromatic`, `aa_basic`, `aa_nonpolar`, `aa_polar`, `aa_special`.

Excluded: `ca_x/y/z`, `centroid_x/y/z` (not invariant), `n_backbone_atoms` and
`has_full_backbone` (zero variance), all identifier columns, and the absent
`plddt_atom_*` columns.

### 6.2 Models and hyperparameters

**XGBoost**

```python
XGBClassifier(
    n_estimators=100,
    max_depth=3,
    learning_rate=0.03,
    scale_pos_weight=(n_negative / n_positive),  # computed on the training folds only
    random_state=42,
    eval_metric="logloss",
)
```

**Random Forest**

```python
RandomForestClassifier(
    n_estimators=100,
    max_depth=4,
    class_weight="balanced_subsample",
    random_state=42,
)
```

### 6.3 Validation and metrics

- For each fold: train on the six other proteins, predict probabilities for the
  held-out protein. No residue from the held-out protein is used in training.
- ROC-AUC via `sklearn.metrics.roc_auc_score`.
- PR-AUC via `sklearn.metrics.precision_recall_curve` followed by trapezoidal
  `sklearn.metrics.auc(recall, precision)`. Baseline PR-AUC = prevalence (0.0419 pooled).
- **Primary reported statistic:** median and IQR (25th/75th percentile, linear
  interpolation) across the **six evaluable folds**. Mean is not the official statistic.
- **Secondary:** pooled metrics on all 1,098 out-of-fold predictions.

---

## 7. Results — Reproduced 2026-10-20

### 7.1 Per-fold

| Fold | Protein | Pos/Total | XGB ROC | XGB PR | RF ROC | RF PR |
|---:|---|---:|---:|---:|---:|---:|
| 0 | P00441 | 7/154 | 0.9621 | 0.8476 | 0.9835 | 0.8081 |
| 1 | P02144 | 2/154 | 0.9375 | 0.0950 | 0.9934 | 0.4167 |
| 2 | P0DP23 | 20/149 | 0.5946 | 0.1568 | 0.5616 | 0.1349 |
| 3 | P42212 | 0/238 | *N/A* | *N/A* | *N/A* | *N/A* |
| 4 | P61626 | 2/148 | 0.8425 | 0.0357 | 0.7363 | 0.0234 |
| 5 | P61823 | 11/150 | 0.5546 | 0.3020 | 0.5853 | 0.2564 |
| 6 | P99999 | 4/105 | 0.3960 | 0.2721 | 0.4257 | 0.2729 |

### 7.2 Median and IQR (six evaluable folds)

| Model | Metric | Median | Q1 | Q3 | IQR |
|---|---|---:|---:|---:|---:|
| XGBoost | ROC-AUC | **0.7185** | 0.5646 | 0.9137 | 0.3491 |
| XGBoost | PR-AUC | **0.2144** | 0.1105 | 0.2945 | 0.1840 |
| Random Forest | ROC-AUC | **0.6608** | 0.5676 | 0.9217 | 0.3541 |
| Random Forest | PR-AUC | **0.2647** | 0.1653 | 0.3807 | 0.2155 |

### 7.3 Pooled (all 1,098 out-of-fold predictions; 46 positives; baseline PR 0.0419)

| Model | ROC-AUC | PR-AUC |
|---|---:|---:|
| XGBoost | 0.5368 | 0.0916 |
| Random Forest | 0.5062 | 0.1028 |

### 7.4 Agreement with the delivered Stage 8.2 summary

The delivered summary (`download/gemini-code-1792488146615.md`) reported:
XGB median ROC 0.7185 / PR 0.2144; RF median ROC 0.6604 / PR 0.2658; pooled XGB
0.5368 / 0.0916; pooled RF 0.5147 / 0.1050.

| Quantity | Summary claim | Reproduction | Difference |
|---|---:|---:|---:|
| XGB median ROC | 0.7185 | 0.7185 | 0.0000 |
| XGB median PR | 0.2144 | 0.2144 | 0.0000 |
| XGB pooled ROC | 0.5368 | 0.5368 | 0.0000 |
| XGB pooled PR | 0.0916 | 0.0916 | 0.0000 |
| RF median ROC | 0.6604 | 0.6608 | +0.0004 |
| RF median PR | 0.2658 | 0.2647 | −0.0011 |
| RF pooled ROC | 0.5147 | 0.5062 | −0.0085 |
| RF pooled PR | 0.1050 | 0.1028 | −0.0022 |

**XGBoost reproduces every reported value exactly** — all six per-fold ROC/PR pairs,
both medians, and both pooled metrics. This confirms the feature definition (seven
structural invariants + one-hot of the existing six `amino_acid_type` categories) and
the fold assignment.

**Random Forest** is identified by the configuration above; the small residual
differences are consistent with scikit-learn version/implementation differences in
`class_weight="balanced_subsample"` (the reproduction environment is listed in §8).
Per-fold RF differences are at most 0.0171 ROC and 0.0187 PR; median differences are
≤0.0011. No contradiction of the delivered summary is present.

### 7.5 Interpretation (do not overclaim)

- The benchmark shows **heterogeneous, protein-dependent signal**, not a general
  predictive capability. Median per-fold values are inflated relative to pooled values.
- Pooled ROC-AUC is close to random (0.54 XGB / 0.51 RF); pooled PR-AUC is about
  2.2–2.5× the 0.0419 baseline, which is weak.
- The median/IQR spread is large (ROC IQR ≈ 0.35). With only six evaluable folds and
  46 positives, these intervals are unstable.
- Probabilities are not calibrated across proteins; pooled metrics mix different
  per-protein score distributions. This is a known limitation of the current protocol,
  not a property of the features alone.
- The benchmark is a **baseline for future comparisons**, not evidence of biological
  function prediction. The 7-protein, 1,098-residue scope remains far too small for
  generalization claims.

---

## 8. Reproduction Environment

Verification was run locally on 2026-10-20 with:

- Python 3.12.10 (repository `.venv`)
- pandas 3.0.6
- numpy 2.5.4
- scipy 1.18.1
- scikit-learn 1.9.1
- xgboost 3.4.1

`scikit-learn`, `xgboost`, `scipy`, and the matching numpy were installed to a temporary
directory for this verification; they are **not** part of the repository `.venv` or
`requirements.txt`. The reproduction command therefore depends on that temporary
environment. This is recorded as a tooling gap: to make Stage 8.2 reproducible from a
clean checkout, these dependencies must be pinned in `requirements.txt` (a separate
decision requiring approval).

---

## 9. Freeze and Change Policy

1. **No in-place edits.** `results/dataset/stage7_processed_dataset.csv` is byte-frozen.
   Any correction or extension must produce a new file (e.g.
   `stage7_processed_dataset_v2.csv`) and a new lock entry with its own SHA256.
2. **Provenance propagation.** Any derived table or model report must cite the SHA256
   above. A derived artifact whose source hash differs is not comparable.
3. **Label policy is part of the benchmark.** Changing the label definition (for example
   adding generic `Site` or `Metal binding`) creates a **new benchmark**, not a revision
   of this one.
4. **Metric policy.** Official comparisons use LOGO-CV median + IQR over evaluable folds,
   with pooled metrics reported separately. GFP (P42212) is always excluded from fold
   medians and always disclosed.
5. **No silent metric changes.** Any new model result must state the feature set, model
   configuration, fold handling, and whether it is directly comparable to Stage 8.2.
6. **Git.** This document and the dataset copy are ready for review but **uncommitted**;
   no commit or push is made without explicit approval.

---

## 10. Known Limitations

- **Scale:** 7 proteins, 1,098 correlated residues, 46 positives. Residues within a
  protein are not independent samples. Any “N = 1,098” independence claim is invalid.
- **Homogeneity:** all seven proteins are globular/soluble monomers; five are human;
  no membrane proteins or large disordered regions. Taxonomic and structural bias.
- **Labels:** A+B annotation coverage is sparse and uneven (GFP has zero positives;
  calmodulin has 20). Annotation completeness varies by protein.
- **Features:** all structural features are AlphaFold predictions, not experimental
  measurements. pLDDT/PAE confidence is not biological truth.
- **No structure-level context:** the model sees per-residue features only; it has no
  explicit 3D neighborhood or sequence-window context. The delivered summary itself
  recommends context-window smoothing as a next step.
- **Provenance gap:** the Stage 7 generating script is not in the repository (§2).

---

## 11. Supersession

This lock supersedes earlier informal references to “Stage 8.2 metrics” in
`download/gemini-code-1792488146615.md`. That file remains as the historical claim;
this document is the authoritative record of what was reproduced and how.

Future dataset expansions (15–100+ proteins) must **not** modify this artifact. They
must build a new dataset from raw AlphaFold DB mmCIF/PDB with the same invariant feature
definitions and the unified A+B label policy, then create a new lock document.
