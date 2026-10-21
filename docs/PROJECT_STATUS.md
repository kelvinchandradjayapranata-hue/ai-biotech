# PROJECT STATUS — AI-BIOTECH

**Dokumen ini adalah single source of truth status project.**
Dibuat: 2026-10-05. Sumber: README.md, `docs/` (DATASET_PLAN.md, TAHAP_5, TAHAP_6),
serta manifest/hasil yang ada di `results/` dan `data/`. Tidak ada file Stage 1–6 yang
diubah, tidak ada eksperimen baru dijalankan, tidak ada unduhan dilakukan.

---

```
PROJECT STATUS:
STAGE 1–11 AUDITED — STAGE 8.2 BENCHMARK LOCKED
DATA PIPELINE: VALIDATED
BIOLOGICAL ML: BASELINE REPRODUCED — NO GENERALIZATION CLAIM
PRODUCTION ARTIFACT: EXPORTED + INFERENCE CLI TESTED — NOT EXTERNALLY VALIDATED
```

> **Update 2026-10-20.** Stage 7 (dataset & label) dan Stage 8.2 (LOGO-CV baseline)
> sudah selesai. Dataset benchmark dikunci di
> `results/dataset/stage7_processed_dataset.csv` (SHA256
> `34f9dd27b1d11fb35155f1542e066a50110144cd84c62d91a28caa6ab9d99f61`), dan metrik
> resmi Stage 8.2 telah direproduksi serta dicatat di
> `docs/BENCHMARK_DATASET_LOCK.md`.
>
> **Update 2026-10-20 — Stage 9.2.** Ekspansi dataset nyata dari AlphaFold DB
> (14 protein, 3.960 residu) telah diaudit independen dan disalin ke
> `results/dataset/stage9_processed_dataset.csv` (SHA256
> `58e55a293b66c13dd4ca4437f1d268f69fc212c93376f58488a692998255e10c`). Seluruh
> fitur struktural cocok dengan CIF/PAE AFDB asli dan label A+B cocok 100% dengan
> UniProt; metrik LOGO-CV direproduksi (XGB persis, RF dalam toleransi ≤0,0011).
> **Dua definisi fitur menyimpang dari Stage 3/8.2** (`pae_local_mean_k10` dan
> klasifikasi histidin), sehingga Stage 9.2 adalah dataset terpisah dan **tidak
> langsung sebanding** dengan benchmark Stage 8.2. Rincian bukti di §16.
>
> **Update 2026-10-20 — Stage 9.3.** Dataset Stage 9.2 direkonsiliasi dengan definisi
> frozen Stage 3/8.2: `pae_local_mean_k10` dihitung `|i-j| ≤ 10, j ≠ i` dan histidin
> dikembalikan ke `basic`. Artefak diaudit independen dan disalin ke
> `results/dataset/stage93_realigned_dataset.csv` (SHA256
> `6f0357858638c57630e0276fb8e46339a16f001e54005dba34adb5b5e3f37f5a`; 3.960 × 12;
> 14 protein; 129 positif). Seluruh fitur struktural dan label cocok 3.960/3.960
> dengan AFDB/UniProt; `target_y` identik dengan Stage 9.2. Metrik LOGO-CV: XGB median
> ROC 0,7264 / PR 0,1684, pooled 0,6411 / 0,0858; RF median 0,7518 / 0,1763, pooled
> 0,6575 / 0,0912. Median, pooled, dan gain reproduce; **IQR PR yang dilaporkan tidak
> reproduce** (lihat §17.4). Stage 8.2 tetap benchmark beku; Stage 9.3 adalah ekspansi
> terpisah, bukan pengganti benchmark.
>
> **Update 2026-10-20 — Stage 9.4.** Full production scaling ke **103 protein /
> 59.188 residu / 959 positif (1,62%)** telah diaudit independen dan disalin ke
> `results/dataset/production_dataset_100_realigned.csv` (SHA256
> `8be323f64d1b5f8dbcfff743d378392bafc72e944f051cac5c835f6f54b1bde1`; LF, 4.619.447 B).
> Seluruh fitur turunan sekuens dan label cocok 59.188/59.188 dengan UniProt; fitur
> struktural cocok persis untuk 56.028 baris yang dimodelkan. **XGBoost LOGO-CV
> reproduce persis** (median ROC 0,7359; pooled ROC 0,7575 / PR 0,0606 / gain 3,74×).
> Random Forest cocok untuk pooled ROC 0,7471, tetapi **median ROC 0,7397 dan pooled
> PR 0,0592 tidak reproduce** (reproduced: 0,7339 dan 0,0573). Dua catatan penting:
> (1) P11532 memakai entri isoform AFDB `AF-P11532-9-F1` (525 aa) yang berbeda pada
> 496/525 posisi dari sekuens kanonik, sehingga 525 baris strukturalnya tidak selaras
> dan 3.160 baris lainnya kosong; (2) kenaikan pooled ROC 0,5368 → 0,7575 **bukan
> perbandingan apple-to-apple** dan sebagian dipengaruhi perbedaan antar-protein —
> lihat §18.5. Stage 9.4 adalah milestone data, bukan bukti generalisasi.
>
> **Update 2026-10-20 — Stage 9.5.** Pembersihan dataset produksi: **P11532 dikeluarkan**
> seluruhnya (3.685 baris; isoform AFDB tidak selaras, §18.3), menghasilkan
> `results/dataset/production_dataset_100_cleaned.csv` (SHA256
> `e47b3635a7e904107094afde02a1ece656e25491c8721865501b6a76562b05a3`; **55.503 × 12**;
> **102 protein**; **955 positif / 1,7206%**; LF, 4.457.124 B). Tidak ada sel kosong,
> baris `n_atoms = 0`, posisi duplikat, atau gap penomoran yang tersisa; 24 protein tetap
> zero-positive dan 78 fold evaluable. LOGO-CV dijalankan ulang penuh (retraining, bukan
> sekadar membuang baris evaluasi). **XGBoost:** median ROC 0,7371 / PR 0,0673, pooled
> ROC 0,7476 / PR 0,0640 / gain 3,72×. **Random Forest:** median ROC 0,7330 / PR 0,0731,
> pooled ROC 0,7476 / PR 0,0608 / gain 3,53×. Dampak pembersihan: pooled ROC XGB turun
> 0,7575 → 0,7476 (−0,0099) karena baris P11532 menginflasi pooled ROC; pooled PR naik
> 0,0606 → 0,0640; median per-protein nyaris tidak berubah (+0,0012 ROC). Within-protein
> z-scored ROC tetap 0,6877 (XGB) / 0,6891 (RF), jauh di bawah pooled. Stage 9.5 adalah
> dataset bersih pertama pada skala 102 protein, tetap **bukan** validasi eksternal dan
> bukan bukti generalisasi.
>
> **Update 2026-10-20 — Stage 10.1.** Fitur lingkungan spasial 3D ditambahkan ke dataset
> bersih: radius **8,0 Å** dari koordinat Cα, dengan tiga fitur baru
> `spatial_density_8a`, `spatial_plddt_mean_8a`, dan `spatial_pae_mean_8a` (definisi di
> §20.2). Dataset `results/dataset/production_dataset_100_spatial.csv` berisi
> **55.503 × 15** (102 protein, 955 positif), **0 NaN** pada ketiga kolom baru, LF murni,
> 5.313.161 B, SHA256
> `8e21534055132c8cf4eb823e1abda224a15776b437b94bbc851f1ea4a99a3319`. Seluruh
> 55.503 baris diverifikasi ulang terhadap CIF/PAE AFDB; parser independen mereproduksi
> seluruh **166.509 nilai fitur baru tanpa selisih**. LOGO-CV dengan 16 fitur (13 frozen
> + 3 spasial): **XGBoost** median ROC 0,7786 / PR 0,0925, pooled ROC 0,7676 / PR 0,0759
> / gain 4,41×; **Random Forest** median ROC 0,7724 / PR 0,0894, pooled ROC 0,7568 / PR
> 0,0668 / gain 3,88×. Peningkatan vs Stage 9.5 juga terlihat pada within-protein
> z-scored ROC (0,7156 XGB / 0,7059 RF vs 0,6877 / 0,6891), tetapi tetap **bukan**
> validasi eksternal dan **bukan** bukti generalisasi. Rincian di §20.
>
> **Update 2026-10-20 — Stage 10.2.** Sweep radius spasial **6, 8, 10, 12 Å** dan kalibrasi
> probabilitas out-of-fold dijalankan pada dataset bersih 102 protein. Aturan pemilihan
> radius ditetapkan sebelum melihat hasil (XGB median ROC → RF median ROC → XGB pooled PR);
> radius **12 Å** terpilih. LOGO-CV 78 fold evaluable: **XGB** median ROC 0,8120 / PR 0,1255,
> pooled ROC 0,7956 / PR 0,0881 / gain 5,12×, within-protein z-scored ROC 0,7495; **RF**
> median ROC 0,8089 / PR 0,1051, pooled ROC 0,7759 / PR 0,0711 / gain 4,13×, within-protein
> 0,7338. Friedman test lintas empat radius signifikan (XGB ROC p = 1,49e-06; RF ROC
> p = 3,32e-14), dan r12 vs r8 juga signifikan pada kedua model. Dataset terkalibrasi
> `results/dataset/production_dataset_100_calibrated.csv` berisi **55.503 × 21** — 15 fitur
> (12 Stage 9.5 + 3 spasial r12) ditambah **6 kolom skor OOF** (raw/isotonic/sigmoid untuk XGB
> dan RF); 0 NaN, LF murni, 9.667.972 B, SHA256
> `2c4bcb3da7dfe4de82a95902f6fa3156e656cb5aece521b54d427cb42220ea3a`. Kalibrasi
> isotonic/sigmoid memperbaiki skala absolut secara dramatis (Brier XGB 0,1820 → 0,0163;
> ECE 0,3569 → 0,0016; mean predicted 0,3741 → 0,0176 vs prevalensi 0,0172) tetapi **tidak**
> memperbaiki metrik berbasis peringkat dan tidak menutup inflasi antar-protein (pooled ROC
> XGB 0,7956 → 0,7900 isotonic / 0,7947 sigmoid; within-z 0,7495 → 0,7418 / 0,7475;
> between-protein AUC hanya bergeser kecil: XGB 0,7828 → 0,7889 / 0,7859, RF 0,7870 →
> 0,7847 / 0,7839). Sigmoid bersifat rank-preserving (0 fold berubah); isotonic
> menciptakan tie dan mengubah 34/43 fold XGB. Tidak ada commit/push untuk Stage 10.2. Rincian
> di §21.
>
> **Update 2026-10-21 — Stage 10.3.** Tuning hiperparameter berarah dan perbandingan strategi
> imbalansi dijalankan pada dataset terkalibrasi radius 12 Å (16 fitur latih; 102 protein;
> 55.503 baris; 955 positif = 1,7206%; 78 fold evaluable). Total **101 konfigurasi unik**
> dievaluasi dengan 102-fold LOGO-CV: 44 konfigurasi XGBoost (2 pass), 46 LightGBM (2 pass),
> dan 8 Random Forest (1 pass), ditambah tiga konfigurasi hasil seleksi-pass yang dievaluasi
> ulang sebagai konfigurasi tetap. Perbandingan imbalansi menunjukkan **tidak ada strategi
> yang menang di semua metrik**: `scale_pos_weight=1` memberi pooled PR dan kalibrasi terbaik
> pada baseline pass 1 (XGB gain 5,71×, Brier 0,0162; LGBM 5,90×, 0,0162), sedangkan bobot
> besar menaikkan median PR per-protein tetapi menurunkan pooled PR, between-protein AUC, dan
> Brier (XGB spw=100: median PR 0,1272 tetapi gain 5,06×, Brier 0,2747; LGBM spw=100: 0,1305,
> 5,45×, 0,2354). `is_unbalance=True` identik dengan `scale_pos_weight="ratio"` pada LightGBM.
> Untuk Random Forest, `class_weight=None` mengungguli `balanced`/`balanced_subsample` pada
> median PR (0,1301 vs 0,1029/0,1051), pooled PR (0,0912 vs 0,0692/0,0711), dan kalibrasi
> (Brier 0,0164 vs 0,1942/0,1902). **Golden model** dipilih dengan aturan pra-deklarasi
> (median PR tertinggi; dalam 0,005 pooled gain tertinggi; dalam 0,05× Brier terendah):
> **LightGBM `lgbm__032c38ffe37f`** (`max_depth=6`, `num_leaves=31`, `learning_rate=0,05`,
> `subsample=0,75`, `colsample_bytree=0,9`, `min_child_samples=20`,
> `scale_pos_weight=20`). Metrik LOGO-CV: median ROC **0,8411** (IQR 0,1446) / PR **0,1693**
> (IQR 0,1737); pooled ROC **0,8131** / PR **0,1142** / gain **6,63×**; within-protein
> z-scored ROC **0,7709**; Brier **0,0520**; ECE **0,1228**; mean predicted 0,1400 vs
> prevalensi 0,0172. XGBoost terbaik menurut aturan yang sama: `xgb__496d370641fb`
> (median ROC 0,8303 / PR 0,1508; pooled 0,8156 / 0,1156 / 6,72×; within-z 0,7662;
> Brier 0,0209; ECE 0,0373). Nested LOGO-CV dengan inner `GroupKFold(5)` memberi median ROC
> 0,8303 / PR 0,1550, pooled ROC 0,7961 / PR 0,0784 / gain 4,55×, within-z 0,7680, Brier
> 0,0340; prosedur memilih XGB 81/102 fold dan LGBM 11+10 fold. Gap median PR global vs
> nested (0,1693 → 0,1550) dan pooled gain (6,63× → 4,55×) mengukur optimisme seleksi;
> kandidat nested masih berasal dari tuning global sehingga tetap optimistis. **Tidak ada
> validasi eksternal**, tidak ada dataset baru, dan kalibrasi tidak di-fit ulang — Brier/ECE
> adalah skor mentah model. Nama "Stage 10.3" di sini adalah tuning internal, bukan validasi
> eksternal yang sebelumnya direncanakan (D14). Rincian di §22.
>
> **Update 2026-10-21 — Stage 11.** Golden LightGBM `lgbm__032c38ffe37f` dilatih pada seluruh
> **55.503 baris / 102 protein** dataset terkalibrasi, lalu disimpan bersama dua kalibrator ke
> `results/models/golden_lightgbm_12a.joblib` (**157.432 B**, SHA256
> `98c86efbebcb7e7986921386a07ca76319c453536dd8e4a2afd2a9b8085445da`). OOF Stage 10.3
> direproduksi ulang dengan selisih maksimum **0,0** sebelum kalibrator di-fit. Sigmoid
> (deployed, dipilih sebelum evaluasi karena rank-preserving dan tanpa tie) memberi Brier
> **0,016072** / ECE **0,000811** / mean predicted **0,017206** pada skor OOF; isotonic
> pembanding memberi Brier 0,015955 tetapi hanya 45 nilai unik dari 55.503 skor. Artefak
> menyimpan model, sigmoid + isotonic, 16 nama fitur, parameter, metadata dataset, metrik OOF,
> feature importance, limitations, dan environment. CLI baru `src/predict.py` menerima
> `--uniprot` atau `--structure` + `--pae`, menghitung ulang 16 fitur (termasuk radius 12 Å),
> dan mengeluarkan probabilitas per-residu terkalibrasi. Diuji pada **P02144** (154 residu;
> CIF lokal, PDB lokal, unduhan AFDB, dan cache — output numerik identik; paritas fitur vs
> dataset maksimum 3,55e-15, **0 nilai > 1e-12**, probabilitas model identik bit) dan
> **P00520** (1.123 residu); error path PAE hilang dan multi-chain menghasilkan exit 2.
> Ambang 0,5 hanya tampilan: kedua protein mendapat 0 panggilan (maksimum 0,1471 / 0,1548).
> Kalibrator di-fit pada OOF protein yang sama dan model final melihat seluruh label training;
> **tidak ada validasi eksternal**. Rincian di §23.
>
> Bagian 1, 2, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20 (Stage 10.1), 21 (Stage 10.2),
> 22 (Stage 10.3), 23 (Stage 11, baru), 24 (rekomendasi, renumber), dan Appendix sudah
> diperbarui; bagian 3–8 tetap merupakan catatan historis Stage 1–6.

---

## 1. Executive Summary

Project ini membangun **pipeline data protein** dari sekuens sampai tabel fitur
per-residu siap-analisis, memakai prediksi struktur AlphaFold (Server dan DB) dan
Python (Biopython, pandas, matplotlib).

Yang **sudah tercapai** dan terverifikasi:

- Pipeline analisis sekuens → struktur → fitur per-residu berjalan dan reproducible.
- 7 protein dari AlphaFold DB (versi v6) terunduh terkontrol dan tervalidasi penuh
  (checksum, sekuens, bentuk PAE).
- Ekstraksi fitur multi-protein menghasilkan tabel **1098 baris residu × 29 kolom**
  (3 identifier protein + 26 fitur numerik) dari 7 protein, dengan 24/24 test PASS.
- Seluruh test Stage 3 (20/20), Stage 4 (12/12), Stage 5 (16/16) tetap lulus.
- Semua output dataset deterministik dan **byte-identical** antar-run (hash tercatat).
- **Stage 7:** dataset benchmark **1098 × 27** dengan label biner **Active site +
  Binding site** (46 positif, 4,19%) dan 7 fold leave-one-protein-out; dikunci dengan
  SHA256 dan diaudit 7/7 terhadap UniProt serta 25 kolom bersama Stage 6.
- **Stage 8.2:** baseline LOGO-CV (7 fitur struktural invarian + 6 one-hot AA)
  direproduksi. XGBoost cocok persis dengan ringkasan Stage 8.2 di semua nilai
  per-fold, median, dan pooled; Random Forest cocok dalam toleransi kecil. Median/IQR
  resmi tercatat di `docs/BENCHMARK_DATASET_LOCK.md`.
- **Stage 9.2:** ekspansi dataset nyata dari AlphaFold DB untuk **14 protein /
  3.960 residu / 129 positif**. Audit independen memverifikasi bahwa seluruh fitur
  struktural (pLDDT, PAE row/col, `n_atoms`) berasal dari CIF/PAE AFDB asli, sekuens
  dan checksum cocok 14/14, dan label A+B cocok 100% dengan UniProt (14 protein;
  metadata 15 protein juga 0 mismatch). Metrik LOGO-CV direproduksi: XGBoost persis,
  Random Forest dalam toleransi ≤0,0011. **Catatan penting:** dua definisi fitur
  berbeda dari benchmark Stage 3/8.2 (lihat §16), sehingga angka Stage 9.2 tidak
  boleh dibandingkan langsung dengan Stage 8.2.
- **Stage 9.3:** realignment dataset Stage 9.2 ke definisi frozen Stage 3/8.2.
  `pae_local_mean_k10` memakai `|i-j| ≤ 10, j ≠ i` dan histidin = `basic`; seluruh
  fitur struktural dan label cocok 3.960/3.960 dengan AFDB/UniProt, dan `target_y`
  identik dengan Stage 9.2. Metrik LOGO-CV: XGB median ROC 0,7264 / PR 0,1684,
  pooled 0,6411 / 0,0858; RF median 0,7518 / 0,1763, pooled 0,6575 / 0,0912.
  Median/pooled/gain reproduce; IQR PR yang dilaporkan tidak reproduce (§17.4).
  Stage 9.3 adalah artefak baru, **bukan** pengganti benchmark Stage 8.2.
- **Stage 9.4:** full production scaling ke **103 protein / 59.188 residu / 959 positif**.
  Audit independen (206 file AFDB CIF/PAE, 103 API JSON, 103 UniProt JSON) menemukan
  **0 mismatch** untuk seluruh fitur turunan sekuens dan label (59.188/59.188) serta
  fitur struktural pada 56.028 baris yang dimodelkan. XGBoost LOGO-CV reproduce persis:
  median ROC 0,7359; pooled ROC 0,7575 / PR 0,0606 / gain 3,74×. Random Forest hanya
  sebagian: pooled ROC 0,7471 cocok, tetapi median ROC 0,7397 dan pooled PR 0,0592
  tidak reproduce (0,7339 / 0,0573). **P11532 bermasalah:** entri AFDB yang dipakai
  adalah isoform 525 aa yang berbeda pada 496/525 posisi dari sekuens kanonik; 3.160
  baris lainnya tidak punya fitur struktural. Kenaikan pooled ROC dari Stage 8.2
  **bukan** bukti generalisasi (§18.5).
- **Stage 9.5:** pembersihan dataset produksi dengan mengeluarkan **P11532** (isoform
  mismatch, §18.3). Dataset bersih: **102 protein / 55.503 residu / 955 positif
  (1,7206%)**, 24 protein zero-positive, 78 fold evaluable; **0 sel kosong** dan **0 baris
  unmodeled**. LOGO-CV dijalankan ulang penuh: XGBoost median ROC 0,7371 / PR 0,0673,
  pooled ROC 0,7476 / PR 0,0640 / gain 3,72×; Random Forest median ROC 0,7330 / PR 0,0731,
  pooled ROC 0,7476 / PR 0,0608 / gain 3,53×. Pooled ROC XGB turun −0,0099 dari Stage 9.4
  (artefak P11532 hilang), pooled PR naik +0,0034, median per-protein hampir tidak berubah
  (+0,0012); within-protein z-scored ROC tetap 0,6877/0,6891 — pembersihan memperbaiki
  validitas, bukan generalisasi (§19).
- **Stage 10.1:** tiga fitur lingkungan spasial radius **8,0 Å** ditambahkan ke dataset
  bersih: `spatial_density_8a`, `spatial_plddt_mean_8a`, `spatial_pae_mean_8a`. Dataset
  **55.503 × 15**, 102 protein, 955 positif, **0 NaN** pada kolom baru; seluruh nilai
  diverifikasi ulang terhadap CIF/PAE AFDB (0 mismatch). LOGO-CV 16 fitur: XGBoost
  median ROC 0,7786 / PR 0,0925, pooled ROC 0,7676 / PR 0,0759 / gain 4,41×; RF median
  ROC 0,7724 / PR 0,0894, pooled ROC 0,7568 / PR 0,0668 / gain 3,88×. Within-protein
  z-scored ROC naik ke 0,7156 (XGB) / 0,7059 (RF), jadi peningkatan tidak hanya berasal
  dari urutan antar-protein; tetapi ini masih evaluasi internal, bukan validasi
  eksternal (§20).
- **Stage 10.2:** sweep radius spasial 6/8/10/12 Å dan kalibrasi probabilitas out-of-fold.
  Radius **12 Å** terpilih dengan aturan yang ditetapkan sebelum melihat hasil. Pada 78
  fold evaluable, XGB median ROC 0,8120 / PR 0,1255, pooled ROC 0,7956 / PR 0,0881 /
  gain 5,12×, within-protein z-scored ROC 0,7495; RF median ROC 0,8089 / PR 0,1051,
  pooled ROC 0,7759 / PR 0,0711 / gain 4,13×, within-protein 0,7338. Uji Friedman lintas
  radius signifikan untuk ROC dan PR pada kedua model (semua p < 1,5e-06). Dataset
  `production_dataset_100_calibrated.csv` (**55.503 × 21**) memuat 15 fitur ditambah enam
  kolom skor OOF (raw/isotonic/sigmoid × XGB/RF), 0 NaN, LF murni, SHA256 `2c4bcb3d…ea3a`.
  Isotonic dan sigmoid memperbaiki skala probabilitas absolut (Brier XGB 0,1820 → 0,0163;
  ECE 0,3569 → 0,0016) tetapi **tidak** memperbaiki pooled ROC/PR, within-protein ROC,
  atau inflasi antar-protein; sigmoid rank-preserving, isotonic tidak (§21).
- **Stage 10.3:** tuning hiperparameter berarah + perbandingan strategi imbalansi pada dataset
  radius 12 Å yang sama (16 fitur latih; 102 protein; 55.503 baris; 955 positif = 1,7206%).
  Sebanyak **101 konfigurasi unik** dievaluasi dengan 102-fold LOGO-CV: XGBoost 44, LightGBM 46,
  Random Forest 8, ditambah 3 konfigurasi seleksi-pass yang dihitung ulang sebagai konfigurasi
  tetap. **Golden model** menurut aturan pra-deklarasi (median PR → pooled gain → Brier):
  **LightGBM `lgbm__032c38ffe37f`** (`max_depth=6`, `learning_rate=0,05`, `subsample=0,75`,
  `colsample_bytree=0,9`, `scale_pos_weight=20`). LOGO-CV: median ROC **0,8411** / PR
  **0,1693**; pooled ROC **0,8131** / PR **0,1142** / gain **6,63×**; within-protein z-scored
  ROC **0,7709**; Brier **0,0520**; ECE **0,1228**. XGBoost terbaik `xgb__496d370641fb`:
  median ROC 0,8303 / PR 0,1508; pooled 0,8156 / 0,1156 / 6,72×; Brier 0,0209. Nested
  LOGO-CV (inner `GroupKFold(5)`) menurunkan median PR ke 0,1550 dan pooled gain ke 4,55×,
  mengukur optimisme seleksi. Tidak ada dataset baru, tidak ada kalibrasi ulang, dan tetap
  **bukan** validasi eksternal (§22).
- **Stage 11:** ekspor artefak produksi + CLI inferensi mandiri. Golden LightGBM dilatih pada
  seluruh **55.503 baris / 102 protein**; sigmoid di-fit pada skor OOF (Brier **0,016072**,
  ECE **0,000811**, mean predicted **0,017206** vs prevalensi 0,017206), dan model + dua
  kalibrator + kontrak 16 fitur disimpan ke
  `results/models/golden_lightgbm_12a.joblib` (**157.432 B**, SHA256
  `98c86efbebcb7e7986921386a07ca76319c453536dd8e4a2afd2a9b8085445da`). `src/predict.py`
  menerima UniProt atau CIF/PDB lokal + PAE, menghitung 16 fitur, dan menghasilkan probabilitas
  per-residu terkalibrasi. Diuji pada P02144 (154 residu) dan P00520 (1.123 residu) tanpa
  error; paritas fitur P02144 maksimum 3,55e-15 dengan **0 nilai > 1e-12**, dan probabilitas
  model identik bit. Ini **deployment, bukan validasi eksternal** (§23).

Yang **BELUM tercapai** (dan tidak diklaim):

- **Belum ada bukti predictive power yang umum.** Baseline Stage 8.2 lemah dan sangat
  heterogen antar-protein: pooled ROC-AUC 0,5368 (XGB) / 0,5062 (RF), sedangkan pooled
  PR-AUC 0,0916 / 0,1028 terhadap baseline prevalensi 0,0419. Stage 9.5 mencapai pooled
  ROC 0,7476 (XGB/RF); Stage 10.1 menambah fitur spasial dan menaikkannya ke 0,7676
  (XGB) / 0,7568 (RF), dengan median per-protein 0,7786 / 0,7724. Stage 10.2 menaikkan
  lagi ke pooled ROC 0,7956 / 0,7759. Stage 10.3 memilih golden LightGBM dengan median PR
  0,1693, pooled ROC 0,8131 / PR 0,1142 / gain 6,63×, tetapi nested LOGO-CV hanya
  memberi median PR 0,1550 / gain 4,55×. Seluruh evaluasi masih **internal** dan belum
  ada holdout eksternal; pooled ROC tetap dipengaruhi perbedaan antar-protein
  (§19.4, §20.6, §21.6, §22.6). Tidak ada klaim kemampuan generalisasi.
- **Skala masih belum memadai untuk klaim statistik.** Stage 9.5/10.1 berisi 102 protein
  / 55.503 residu, tetapi hanya 955 positif (1,72%), 24 protein tanpa positif, dan residu
  dalam satu protein sangat berkorelasi. Ini bukan 55.503 sampel independen; komposisi
  protein juga masih didominasi protein larut/globular dan belum diseleksi sebagai
  holdout eksternal. Stage 10.1 menambah fitur dan Stage 10.3 menambah tuning/konfigurasi,
  **bukan** protein baru.
- **Belum ada validasi eksternal** pada protein baru, struktur eksperimen, atau dataset
  independen. Stage 10.2 menguji kalibrasi isotonic/sigmoid secara out-of-fold pada 102
  protein yang sama, bukan kalibrasi pada protein eksternal. Stage 9.4/9.5 adalah
  pembesaran/pembersihan dataset, Stage 10.1 adalah feature engineering, Stage 10.2
  adalah sweep radius + kalibrasi internal, Stage 10.3 adalah tuning hiperparameter +
  pemilihan golden model, dan Stage 11 adalah ekspor artefak + kalibrasi pada OOF yang sama —
  semuanya **bukan** validasi eksternal.
- **Label masih terbatas pada A+B.** Belum ada label multi-kelas, GO terms, EC numbers,
  atau skema label alternatif.
- **Stage 9.2, 9.3, 9.4, 9.5, 10.1, 10.2, dan 10.3 bukan validasi eksternal dan bukan
  klaim generalisasi.** Stage 9.2/9.3 berisi 14 protein / 129 positif; Stage 9.4 berisi
  103 protein / 959 positif; Stage 9.5/10.1/10.2/10.3 berisi 102 protein / 955 positif.
  Pooled ROC Stage 10.3 (0,8131 golden LightGBM) lebih tinggi dari Stage 8.2, 10.1, dan
  10.2, tetapi dataset, fitur, radius, dan prevalensinya sama dengan Stage 10.2 — yang
  berubah hanya konfigurasi model — dan pooled ROC tetap dipengaruhi perbedaan skor
  antar-protein. Kalibrasi Stage 10.2 hanya memperbaiki skala probabilitas, bukan
  peringkat; Stage 10.3 tidak mengulang kalibrasi, sehingga Brier/ECE-nya adalah skor
  mentah (0,0520/0,1228) dan tidak sebanding dengan skor terkalibrasi Stage 10.2. Stage 11
  mengekspor model dan mem-fit sigmoid pada OOF, tetapi itu tetap **in-sample calibration
  fit** pada 102 protein yang sama; model final melihat seluruh label training. Belum ada
  holdout eksternal.
- **P11532 sudah dikeluarkan, bukan diperbaiki.** Tidak ada entri AFDB full-length
  kanonik untuk P11532 (hanya 14 isoform; §18.3), sehingga Stage 9.5 menyelesaikannya
  dengan **exclusion**. Rebuild dari sumber struktur full-length tetap belum dilakukan;
  jika sumber tersebut tersedia, itu harus menjadi artefak baru, bukan suntingan dataset
  bersih (§19.3).

Posisi jujur: **infrastruktur data selesai dan tervalidasi; benchmark ML baseline sudah
ada dan terverifikasi, ditambah ekspansi/realignment Stage 9.2–9.3, production scaling
Stage 9.4 (103 protein), pembersihan Stage 9.5 (102 protein, P11532 dikeluarkan), feature
engineering spasial Stage 10.1, sweep radius + kalibrasi out-of-fold Stage 10.2, tuning
hiperparameter + pemilihan golden model Stage 10.3, dan ekspor artefak + CLI inferensi Stage 11
yang nyata dan diaudit — tetapi belum ada bukti generalisasi biologis.** Dataset Stage 10.2
memakai radius 12 Å yang dipilih lewat aturan pra-deklarasi dan meningkatkan metrik internal
lebih lanjut (within-protein z-scored ROC 0,7495 XGB / 0,7338 RF). Stage 10.3 menaikkan median
PR golden LightGBM ke 0,1693 dan within-z ke 0,7709 pada 102 protein yang sama, tetapi nested
LOGO-CV menurunkan median PR ke 0,1550 dan pooled gain ke 4,55× — bukti bahwa sebagian
kenaikan berasal dari optimisme seleksi. Kalibrasi isotonic/sigmoid berhasil memperbaiki skala
probabilitas absolut (ECE 0,357 → 0,002), tetapi tidak memperbaiki diskriminasi peringkat atau
inflasi antar-protein. Stage 11 mem-fit sigmoid pada OOF dan mengekspornya bersama model final
yang dilatih pada seluruh baris; ini membuat inferensi reproducible, bukan tervalidasi. Pooled
ROC masih dipengaruhi perbedaan antar-protein, dan tidak ada holdout eksternal. Fokus
berikutnya adalah validasi eksternal pada protein baru — bukan mengklaim performa.

---

## 2. Overall Project Status

| Dimensi | Status | Bukti ringkas |
|---|---|---|
| Engineering / data pipeline | **BERHASIL** | 4 script utama + 4 test suite, semua exit 0 |
| Penyediaan struktur AlphaFold | **BERHASIL** | 14/14 file AFDB v6, 0 gagal, checksum cocok |
| Validasi integritas data | **BERHASIL** | SHA256 dihitung ulang & cocok; sekuens 7/7 MATCH |
| Feature extraction | **BERHASIL** | 1098 × 29 kolom, 24/24 test PASS |
| Reproducibility | **BERHASIL** | Output dataset byte-identical antar-run |
| Predictive biological AI / ML | **BASELINE ADA; GENERALISASI BELUM** | Stage 8.2 LOGO-CV direproduksi (pooled ROC 0,5368/0,5062); Stage 10.2 XGB pooled ROC 0,7956 / RF 0,7759, within-protein 0,7495/0,7338; Stage 10.3 golden LightGBM pooled ROC 0,8131 / PR 0,1142 / gain 6,63×, median PR 0,1693, within-z 0,7709, tetapi nested LOGO-CV hanya 0,1550 / 4,55×. Semua masih evaluasi internal dan bukan perbandingan apple-to-apple (§19.4, §20.6, §21.7, §22.6); median/IQR Stage 8.2 di `BENCHMARK_DATASET_LOCK.md` |
| Label biologis (y) | **ADA — A+B** | `target_y` = UniProt Active site + Binding site; 46 positif (Stage 7), 129 (Stage 9.2/9.3), 959 (Stage 9.4), 955 (Stage 9.5); audit label 0 mismatch di kelima dataset |
| Ekspansi dataset (Stage 9.2) | **AUDITED — REAL AFDB, DENGAN CATATAN** | 14 protein / 3.960 residu; fitur struktural & label cocok dengan sumber; 2 definisi fitur menyimpang dari Stage 8.2 (§16) |
| Realignment dataset (Stage 9.3) | **AUDITED — DEFINISI FROZEN** | 14 protein / 3.960 residu; H = `basic`; `pae_local_mean_k10` = `\|i-j\| ≤ 10, j ≠ i`; 0 mismatch fitur/label; median/pooled/gain reproduce, IQR PR tidak (§17) |
| Production scaling (Stage 9.4) | **AUDITED — 103 PROTEIN, DENGAN CATATAN** | 59.188 × 12; 103 protein; 959 positif (1,62%); 79 fold evaluable; XGB exact (median ROC 0,7359; pooled 0,7575 / 0,0606 / 3,74×); RF pooled ROC 0,7471 cocok tetapi median ROC/pooled PR tidak; P11532 isoform mismatch (§18) |
| Cleansed production dataset (Stage 9.5) | **AUDITED — 102 PROTEIN, BERSIH** | 55.503 × 12; 102 protein; 955 positif (1,72%); 0 sel kosong/unmodeled; 78 fold evaluable; XGB median ROC 0,7371, pooled 0,7476 / 0,0640 / 3,72×; RF median 0,7330, pooled 0,7476 / 0,0608 / 3,53×; P11532 dikeluarkan (§19) |
| Spatial feature dataset (Stage 10.1) | **AUDITED — 55.503 × 15, 0 NaN** | 3 fitur radius 8,0 Å; 102 protein; 955 positif; 78 fold evaluable; XGB median ROC 0,7786, pooled 0,7676 / 0,0759 / 4,41×; RF median 0,7724, pooled 0,7568 / 0,0668 / 3,88×; within-protein 0,7156/0,7059; 166.509 nilai baru diverifikasi ulang, 0 mismatch (§20) |
| Radius sweep & calibrated dataset (Stage 10.2) | **AUDITED — 55.503 × 21, 0 NaN** | Radius 6/8/10/12 Å; **12 Å terpilih**; 78 fold evaluable; XGB median ROC 0,8120, pooled 0,7956 / 0,0881 / 5,12×; RF median 0,8089, pooled 0,7759 / 0,0711 / 4,13×; within-protein 0,7495/0,7338; Friedman p < 1,5e-06; kalibrasi isotonic/sigmoid memperbaiki Brier/ECE tetapi tidak memperbaiki pooled/within dan tidak menutup gap antar-protein; 6 kolom OOF diverifikasi, 0 mismatch (§21) |
| Tuning & golden model (Stage 10.3) | **AUDITED — 101 KONFIGURASI, GOLDEN LIGHTGBM** | 102-fold LOGO-CV / 78 evaluable; 16 fitur latih; XGB 44 + LGBM 46 + RF 8 konfigurasi (+3 re-eval konfigurasi seleksi-pass); golden `lgbm__032c38ffe37f`: median ROC 0,8411 / PR 0,1693, pooled ROC 0,8131 / PR 0,1142 / gain 6,63×, within-z 0,7709, Brier 0,0520, ECE 0,1228; nested LOGO-CV median PR 0,1550 / gain 4,55×; bukan validasi eksternal (§22) |
| Artefak produksi & CLI inferensi (Stage 11) | **TESTED — JOBLIB + CLI, BUKAN VALIDASI EKSTERNAL** | Model dilatih pada 55.503 baris / 102 protein; OOF Stage 10.3 direproduksi (selisih maks 0,0); sigmoid OOF Brier 0,016072 / ECE 0,000811 / mean 0,017206 vs prevalensi 0,017206; isotonic pembanding 0,015955 tetapi 45 nilai unik; artefak 157.432 B, SHA256 `98c86efb…45da`; CLI P02144/P00520 exit 0; paritas fitur P02144 0 nilai > 1e-12, probabilitas identik bit; ambang 0,5 tidak tervalidasi (§23) |
| Klaim ilmiah/biologis | **TIDAK ADA (sengaja)** | Semua laporan menyatakan fitur = prediksi model; baseline bukan klaim fungsi |

Ringkas: **A/B/C tercapai; D ada sebagai baseline terverifikasi tetapi belum
menunjukkan generalisasi; E/F/G tetap belum dan diakui eksplisit** (lihat bagian 12).

---

## 3. Stage 1 — Protein Sequence Analysis

**Status: PASS**

| Aspek | Isi |
|---|---|
| **Tujuan** | Scaffold project + analisis dasar sekuens protein (ubiquitin) |
| **Input** | `data/ubiquitin_sequence.fasta` (76 aa) |
| **Output** | `results/ubiquitin_sequence_analysis.json`, `results/ubiquitin_composition.csv` |
| **Script** | `src/analyze_protein.py` |
| **Angka penting** | Panjang 76 aa; MW 8.564,7 Da; pI 6,56; GRAVY −0,489; residu terbanyak L (9), I/K/T (7) |
| **Validation/test** | Tidak ada test suite tersendiri di Stage 1. Verifikasi silang: sekuens FASTA identik dengan sekuens CIF struktur (`ubiquitin_sequence_match_check.json`, status IDENTICAL). |
| **Kesimpulan** | Pipeline baca-sekuens dan hitung properti dasar berjalan; FASTA referensi konsisten dengan struktur yang dipakai di Stage 2–3. |
| **Limitations** | Properti (MW, pI, GRAVY) dihitung dari tabel standar, bukan pengukuran eksperimen. Satu protein saja. |

---

## 4. Stage 2 — AlphaFold Structure Analysis

**Status: PASS**

| Aspek | Isi |
|---|---|
| **Tujuan** | Menganalisis struktur prediksi AlphaFold Server (chain → residu → atom) |
| **Input** | `structures/ubiquitin_alphafold.cif` (prediksi AlphaFold Server, model_0) |
| **Output** | `results/ubiquitin_alphafold_structure_analysis.json`, `results/ubiquitin_alphafold_per_residue.csv`, `results/ubiquitin_sequence_match_check.json` |
| **Script** | `src/analyze_protein.py --help` (mode struktur) |
| **Angka penting** | 1 model, 1 chain (A), 76 residu, 602 atom, 0 HETATM, 0 residu tak dikenal; bbox 37,93 × 25,38 × 29,62 Å; pLDDT (B-factor CA) mean 95,31 / min 53,2 / max 98,75; fraksi ≥70 = 97,4 %; fraksi ≥90 = 92,1 % |
| **Validation/test** | Pengecekan kecocokan sekuens struktur vs FASTA: panjang 76 = 76 = 76 (FASTA, CIF, output parser), `structure_vs_fasta = IDENTICAL`, residu pertama MET1, terakhir GLY76, 1 chain. |
| **Kesimpulan** | Parser mmCIF bekerja benar pada data nyata; identitas struktur (sekuens, jumlah chain/residu/atom) konsisten dengan referensi. |
| **Limitations** | Ini **prediksi AlphaFold Server**, bukan struktur eksperimen. Satu protein, satu model. `plddt_cif_vs_full_data_json_identical = false` — dua kanal pLDDT (B-factor CIF vs `atom_plddts` full_data) tidak identik byte-per-byte, selisih terbaca ≤ 0,09 (pembulatan internal server; didokumentasikan di Stage 3 JSON), bukan konflik data. |

---

## 5. Stage 3 — Protein Feature Extraction

**Status: PASS**

| Aspek | Isi |
|---|---|
| **Tujuan** | Mengubah prediksi struktur + confidence menjadi tabel numerik per-residu siap-ML |
| **Input** | `structures/ubiquitin_alphafold.cif`, `data/alphafold_downloads/fold_2026_10_05_10_26/fold_2026_10_05_10_26_full_data_0.json`, `data/ubiquitin_sequence.fasta` (semua read-only) |
| **Output** | `results/ubiquitin_residue_features.csv` (76 × 28), `results/ubiquitin_structure_features.json` (definisi + unit tiap kolom), `results/ubiquitin_plddt_per_residue.png`, `results/ubiquitin_pae_heatmap.png` |
| **Script** | `src/extract_protein_features.py`; validasi `src/test_protein_features.py` |
| **Angka penting** | 76 residu × 28 kolom; PAE 76×76 (min 0,8 / max 26,1 / mean 2,636 / median 1,6 Å); contact_probs 76×76 (simetris, maks selisih 0,0; off-diagonal mean 0,1173; 335 pasangan ≥ 0,50); pLDDT CA mean 95,315 (channel atom global mean 92,002) |
| **Validation/test** | `python src/test_protein_features.py` → **20/20 PASS (exit 0)**. Cakupan: jumlah baris, penomoran 1..76, chain tunggal, sekuens = FASTA, tanpa duplikat/hilang, rekalkulasi PAE & contact dari matriks mentah, anti-transpose, definisi+unit lengkap, konsistensi dengan CIF/n_atoms/koordinat CA, tanpa nilai kosong. |
| **Kesimpulan** | Skema 28 kolom terdefinisi penuh (rumus + unit + ambang eksplisit) dan terverifikasi silang terhadap sumber mentah. Ini menjadi **skema referensi historis** untuk Stage 6. |
| **Limitations** | Semua fitur turunan prediksi model (bukan eksperimen). Koordinat mentah `ca_x/y/z` dan `centroid_*` **tidak invariant rotasi/translasi** — dicatat di DATASET_PLAN §8 sebagai catatan penting untuk ML. 2 fitur bergantung pada `contact_probs` yang hanya ada di output AlphaFold Server (menjadi masalah portabilitas di Stage 6). |

---

## 6. Stage 4 — AlphaFold DB Dataset Planning

**Status: PASS (APPROVED)**

| Aspek | Isi |
|---|---|
| **Tujuan** | Memilih & memverifikasi kandidat protein AlphaFold DB sebagai calon sumber dataset ML; mencatat lisensi/atribusi. **Tanpa unduhan.** |
| **Input** | UniProtKB REST API + AlphaFold DB API (query metadata saja; nol byte file struktur diunduh) |
| **Output** | `docs/DATASET_PLAN.md`, `results/dataset/dataset_manifest.csv` (7 baris), `data/alphafold_db/metadata/candidates.json` |
| **Script** | `src/prepare_dataset.py`; validasi `src/test_dataset_manifest.py` |
| **Angka penting** | 7 kandidat; 6 kategori fungsi; 3 organisme (manusia, sapi, ubur-ubur); panjang 105–238 aa; semua `isComplex = false`; `latestVersion = 6`; lisensi CC BY 4.0 (atribusi EMBL-EBI, Google DeepMind, UniProt) |
| **Validation/test** | `python src/test_dataset_manifest.py` → **12/12 PASS**. |
| **Kesimpulan** | Manifest kandidat terverifikasi dari sumber resmi dan disetujui (APPROVED) sebagai dasar unduhan Stage 5. Pemisahan peran sumber data ditetapkan: AlphaFold Server = spesimen pembelajaran (bukan training data), AlphaFold DB = kandidat dataset ML. |
| **Limitations** | 7 protein jauh terlalu kecil untuk klaim statistik apa pun. Semua kandidat globular/larut (tidak ada protein membran atau daerah tak terstruktur besar). 5/7 protein manusia (bias proteom UniProt). Semua entri monomer, sedangkan beberapa protein in vivo berinteraksi (mis. SOD1 homodimer) — gap model vs bentuk biologis diakui eksplisit. |

---

## 7. Stage 5 — AFDB Download & Validation

**Status: PASS** (7/7 `DOWNLOADED_VALIDATED`; 0 gagal)

| Aspek | Isi |
|---|---|
| **Tujuan** | Mengunduh terkontrol 7 entri AlphaFold DB (2 file per entri) dan memverifikasi integritas penuh secara offline |
| **Input** | Manifest Stage 4 (7 kandidat disetujui); API resmi `alphafold.ebi.ac.uk/api/prediction/<accession>` |
| **Output** | `data/alphafold_db/raw/` (14 file dataset + `README.txt`), `data/alphafold_db/metadata/` (7 `api_<acc>.json` + `download_checksums.csv` 14 baris + `download_log.txt`), `results/dataset/{structure_validation,pae_validation,dataset_download_manifest}.csv` |
| **Script** | `src/download_afdb_dataset.py`, `src/validate_afdb_dataset.py`; test `src/test_afdb_download.py` |
| **Angka penting** | 14/14 file HTTP 200, total **1.469.156 bytes**; semua **v6**; 7/7 sekuens CIF == `uniprotSequence` (identik, bukan hanya panjang); 7/7 `sequenceChecksum` (MD5) cocok; 7/7 CRC64 UniProt cocok; PAE 7/7 matriks N×N persegi (105–238) |
| **Validation/test** | `python src/test_afdb_download.py` → **16/16 PASS (exit 0)**; `python src/test_dataset_manifest.py` → **12/12 PASS** (hanya check E4 diperbarui: `raw/` kini boleh berisi file kandidat yang disetujui). |
| **Kesimpulan** | Dataset AFDB terkunci dan terverifikasi dari dua sistem checksum independen (AFDB = MD5, UniProt = CRC64). Siap dijadikan input Stage 6. |
| **Limitations** | (1) Versi v6 dapat berubah di masa depan — SHA256 tercatat adalah titik referensi. (2) Sebagian sel PAE berisi bilangan bulat bercampur float (karakter data apa adanya, tidak diubah). (3) Dipakai apa adanya tanpa interpretasi biologis. (4) Semua file = prediksi model. (5) `download_log.txt` berisi timestamp & path absolut lokal (satu-satunya artefak non-deterministik; tidak masuk ke CSV/JSON output). |

---

## 8. Stage 6 — Multi-Protein Feature Extraction

**Status: PASS WITH CONCERNS** (COMPLETE + 24/24 test PASS; concern C1/C2 ditutup untuk benchmark Stage 7, C3 tetap)

| Aspek | Isi |
|---|---|
| **Tujuan** | **Validasi pipeline**: membuktikan extractor Stage 3 konsisten saat dijalankan pada 7 protein AFDB yang sudah frozen. **Bukan tahap ML.** |
| **Input** | `results/dataset/dataset_download_manifest.csv` (hanya baris `DOWNLOADED_VALIDATED`), 7 CIF + 7 PAE di `data/alphafold_db/raw/`, metadata `api_<acc>.json` |
| **Output** | `results/dataset/multi_protein_residue_features.csv` (1098 × 29), `multi_protein_summary.csv` (7 protein, semua PASS), `multi_protein_structure_features.json`, `multi_protein_plddt_overview.png`, `multi_protein_pae_overview.png` |
| **Script** | `src/extract_multi_protein_features.py` (baru; mengimpor konstanta Stage 3 — `extract_protein_features.py` tidak diubah) |
| **Angka penting** | **1098 baris = 105+148+149+150+154+154+238** (persis angka ekspektasi); 29 kolom = 3 identifier + 26 fitur; mean pLDDT per protein 85,241 (P0DP23, terendah) … 97,932 (P99999, tertinggi); semua chain tunggal (A); penomoran 1..N berurutan 7/7 |
| **Validation/test** | `python src/test_multi_protein_features.py` → **24/24 PASS** (19 check utama + 5 check tambahan E1–E5). Test Stage 3 (20/20) dan Stage 5 (16/16) diverifikasi ulang **dari dalam** test ini (check 18 & 19) dan tetap lulus. |
| **Kesimpulan** | Pipeline ekstraksi Stage 3 **portabel**: skema yang sama berjalan konsisten pada 7 protein AFDB tanpa modifikasi pada extractor aslinya. Dataset Tahap 5 **tidak diubah sama sekali** (frozen). |
| **Limitations** | (1) **Skema menyusut 28 → 26 fitur**: `contact_prob_sum` dan `n_high_conf_contacts` dikeluarkan karena `contact_probs` tidak tersedia di AFDB — tidak diimputasi, tidak diproksikan, tidak didefinisikan ulang (terdokumentasi di JSON). (2) **Granularitas pLDDT AFDB**: CIF AFDB menulis pLDDT per-residu ke semua atom, sehingga di seluruh 1098 baris `plddt_atom_std = 0` dan `plddt_atom_mean = min = max = plddt_ca` → 4 kolom `plddt_atom_*` **redundan** dengan `plddt_ca` (dikunci test E5; keputusan perlakuan diserahkan ke user). (3) PAE asimetris di 7/7 protein (maks \|PAE − PAEᵀ\| = 19–24 Å) — wajar secara matematis, arah matriks dipertahankan. (4) Semua fitur = prediksi model. |

---

## 9. Consolidated Results Table

| Stage | Status | Main Result | Evidence | Scientific Meaning |
|---|---|---|---|---|
| 1 — Sequence analysis | PASS | Ubiquitin 76 aa; MW 8.564,7 Da; pI 6,56; GRAVY −0,489 | `results/ubiquitin_sequence_analysis.json` | Sekuens terbaca & properti dasar terhitung; belum ada makna biologis baru |
| 2 — Structure analysis | PASS | 1 model, 1 chain, 76 residu, 602 atom; pLDDT mean 95,31 (92,1 % residu ≥90) | `results/ubiquitin_alphafold_structure_analysis.json`, `ubiquitin_sequence_match_check.json` | Model AlphaFold konsisten secara internal — **bukan** validasi eksperimen |
| 3 — Feature extraction | PASS | 76 × 28 kolom; PAE 76×76; contact 76×76; 20/20 test | `results/ubiquitin_residue_features.csv`, `ubiquitin_structure_features.json`, `test_protein_features.py` | Fitur turunan prediksi terdefinisi penuh (rumus + unit + ambang) |
| 4 — Dataset planning | PASS (APPROVED) | 7 kandidat, 6 kategori fungsi, 3 organisme, 105–238 aa; 12/12 test | `results/dataset/dataset_manifest.csv`, `docs/DATASET_PLAN.md` | Rencana dataset terverifikasi dari sumber resmi; lisensi CC BY 4.0 |
| 5 — AFDB download & validation | PASS | 14/14 file v6 tervalidasi, 1.469.156 bytes, 0 gagal; 16/16 test | `data/alphafold_db/raw/`, `download_checksums.csv`, `results/dataset/*_validation.csv` | Struktur AlphaFold resmi diperoleh & **integritasnya terbukti** (checksum + sekuens) |
| 6 — Multi-protein features | PASS WITH CONCERNS | 1098 residu × 29 kolom (26 fitur); 7/7 protein PASS; 24/24 test | `results/dataset/multi_protein_*.csv`, `.json`, `.png` | Pipeline terbukti **portabel**; dataset fitur siap-analisis, **belum ada nilai prediktif yang diuji** |
| 7 — Dataset & label | PASS (LOCKED 2026-10-20) | 1098 × 27; label A+B; 46 positif (4,19%); 7-fold LOGO; SHA256 `34f9dd…f61` | `results/dataset/stage7_processed_dataset.csv`, `docs/BENCHMARK_DATASET_LOCK.md` | Benchmark resmi terkunci; 25 kolom identik Stage 6; label audit 7/7 |
| 8.2 — LOGO-CV baseline | PASS (VERIFIED) | 13 fitur; XGB median ROC 0,7185 / PR 0,2144; RF 0,6608 / 0,2647; pooled XGB 0,5368 / 0,0916, RF 0,5062 / 0,1028 | `docs/BENCHMARK_DATASET_LOCK.md` §7 | Baseline reproducible; XGB cocok persis dengan ringkasan Stage 8.2; **bukan bukti generalisasi** |
| 9.2 — Real AFDB expansion | AUDITED (2026-10-20) | 3.960 × 12; 14 protein; 129 positif (3,26%); 13 fitur; XGB median ROC 0,7092 / PR 0,1509, RF 0,7305 / 0,1852; pooled XGB 0,6484 / 0,1022, RF 0,6523 / 0,0996 | `results/dataset/stage9_processed_dataset.csv`, §16 | Ekspansi nyata dari AFDB; metrik reproducible; **bukan benchmark terkunci** dan **tidak langsung sebanding** dengan Stage 8.2 karena 2 definisi fitur berbeda |
| 9.3 — Realigned real-AFDB | AUDITED (2026-10-20) | 3.960 × 12; 14 protein; 129 positif (3,26%); 13 fitur frozen; XGB median ROC 0,7264 / PR 0,1684, RF 0,7518 / 0,1763; pooled XGB 0,6411 / 0,0858, RF 0,6575 / 0,0912; SHA256 `6f0357…7f5a` | `results/dataset/stage93_realigned_dataset.csv`, §17 | Definisi fitur Stage 3/8.2 dipulihkan; fitur & label 0 mismatch; median/pooled/gain reproduce; **IQR PR dilaporkan tidak reproduce**; tetap **bukan pengganti benchmark Stage 8.2** |
| 9.4 — Full production scaling | AUDITED (2026-10-20) | 59.188 × 12; 103 protein; 959 positif (1,62%); 79 fold evaluable; XGB median ROC 0,7359, pooled 0,7575 / 0,0606 (3,74×); RF median ROC 0,7339, pooled 0,7471 / 0,0573; SHA256 `8be323f6…bde1` | `results/dataset/production_dataset_100_realigned.csv`, §18 | Dataset produksi nyata teraudit; XGB exact; RF hanya pooled ROC yang exact; **P11532 isoform mismatch**; kenaikan pooled ROC **bukan** bukti generalisasi |
| 9.5 — Dataset cleansing & isoform resolution | AUDITED (2026-10-20) | 55.503 × 12; 102 protein; 955 positif (1,72%); P11532 dikeluarkan; 0 sel kosong/unmodeled; 78 fold evaluable; XGB median ROC 0,7371, pooled 0,7476 / 0,0640 (3,72×); RF median ROC 0,7330, pooled 0,7476 / 0,0608 (3,53×); SHA256 `e47b3635…05a3` | `results/dataset/production_dataset_100_cleaned.csv`, §19 | Dataset produksi bersih; pooled ROC XGB turun karena artefak P11532 hilang; within-protein tetap ~0,689; **bukan** bukti generalisasi |
| 10.1 — Spatial neighborhood features | AUDITED (2026-10-20) | 55.503 × 15; 102 protein; 955 positif; 3 fitur radius 8,0 Å; 0 NaN; 78 fold evaluable; XGB median ROC 0,7786, pooled 0,7676 / 0,0759 (4,41×); RF median ROC 0,7724, pooled 0,7568 / 0,0668 (3,88×); within-protein 0,7156/0,7059; SHA256 `8e215340…3319` | `results/dataset/production_dataset_100_spatial.csv`, §20 | Fitur spasial menaikkan metrik internal termasuk within-protein; tetap **bukan** validasi eksternal dan **bukan** bukti generalisasi |
| 10.2 — Multi-radius sweep & OOF calibration | AUDITED (2026-10-20) | 55.503 × 21; 102 protein; 955 positif; radius 6/8/10/12 Å, **12 Å terpilih**; 78 fold evaluable; XGB median ROC 0,8120, pooled 0,7956 / 0,0881 (5,12×); RF median ROC 0,8089, pooled 0,7759 / 0,0711 (4,13×); within-protein 0,7495/0,7338; kalibrasi isotonic/sigmoid: Brier XGB 0,1820 → 0,0163, ECE 0,3569 → 0,0016, tetapi pooled/within turun tipis; SHA256 `2c4bcb3d…ea3a` | `results/dataset/production_dataset_100_calibrated.csv`, §21 | Sweep radius menaikkan metrik internal; kalibrasi memperbaiki skala absolut tetapi **tidak** diskriminasi atau inflasi antar-protein; tetap **bukan** validasi eksternal |
| 10.3 — Hyperparameter tuning & golden model | AUDITED (2026-10-21) | 101 konfigurasi unik; 102 fold / 78 evaluable; 16 fitur; golden LGBM `lgbm__032c38ffe37f`: median ROC 0,8411 / PR 0,1693, pooled ROC 0,8131 / PR 0,1142 (6,63×), within-z 0,7709, Brier 0,0520, ECE 0,1228 (mentah); nested median PR 0,1550 / gain 4,55× | Tidak ada dataset baru; artefak evaluasi di luar repo, §22 | Tuning internal pada 102 protein yang sama; **bukan** validasi eksternal dan tidak mengubah klaim generalisasi |
| 11 — Artefak produksi & CLI inferensi | TESTED (2026-10-21) | Model dilatih 55.503 baris / 102 protein; OOF identik (selisih 0,0); sigmoid OOF Brier 0,016072 / ECE 0,000811 / mean 0,017206; isotonic 0,015955 (45 nilai unik); artefak 157.432 B SHA256 `98c86efb…45da`; CLI P02144/P00520 exit 0; paritas fitur P02144 0 nilai > 1e-12 | `results/models/golden_lightgbm_12a.joblib`, `src/export_model.py`, `src/predict.py`, §23 | Deployment reproducible + kalibrasi in-sample; **bukan** validasi eksternal; ambang 0,5 hanya tampilan |

**Batas tegas antar baris:** sampai Stage 6, semua capaian bersifat
**engineering + integritas data + ekstraksi fitur**. Stage 7 menambahkan **benchmark
terkunci** (dataset + label), dan Stage 8.2 menambahkan **baseline ML yang
direproduksi**. Stage 9.2 menambahkan **ekspansi dataset nyata yang diaudit**; Stage 9.3
merekonstruksinya dengan **definisi fitur frozen**; Stage 9.4 memperbesar skala ke
**103 protein / 59.188 residu** dan mereproduksi XGBoost persis; Stage 9.5 mengeluarkan
P11532 dan menghasilkan dataset **102 protein / 55.503 residu** yang lengkap tanpa sel
kosong; Stage 10.1 menambahkan tiga fitur lingkungan spasial radius 8,0 Å dan
mengevaluasi ulang LOGO-CV; Stage 10.2 melakukan sweep empat radius, memilih 12 Å dengan
aturan pra-deklarasi, lalu menguji kalibrasi isotonic/sigmoid out-of-fold; Stage 10.3 men-tuning
model dan memilih golden LightGBM; Stage 11 mengekspor model + kalibrator dan menambahkan CLI
inferensi. Tidak satu pun dari Stage 9.2–11 menjadi benchmark terkunci atau mengubah status
generalisasi. Tidak ada satu pun baris di tabel ini yang merupakan klaim biologis atau bukti
generalisasi.

---

## 10. Data Inventory

### 10.1 Data mentah / input

| Lokasi | Isi | Ukuran |
|---|---|---|
| `data/ubiquitin_sequence.fasta` | Sekuens ubiquitin (76 aa) | 88 B |
| `structures/ubiquitin_alphafold.cif` | Struktur AlphaFold Server (model_0) | 54.073 B |
| `data/alphafold_downloads/fold_2026_10_05_10_26/` | Arsip unduhan AlphaFold Server: 5 CIF, 5 full_data JSON, 5 summary_confidences JSON, job_request, `msas/`, `templates/`, `terms_of_use.md` | ~600 KB |
| `data/alphafold_db/raw/` | **14 file dataset AFDB v6** (7 CIF + 7 PAE JSON) + `README.txt` | **1.469.156 B** (14 file) |
| `data/alphafold_db/metadata/` | 7 `api_<acc>.json` (respons API mentah), `candidates.json`, `download_checksums.csv` (14 baris), `download_log.txt` | ~26 KB |

### 10.2 Output hasil analisis

| Lokasi | Isi | Ukuran |
|---|---|---|
| `results/` | `ubiquitin_sequence_analysis.json`, `ubiquitin_composition.csv`, `ubiquitin_alphafold_structure_analysis.json`, `ubiquitin_alphafold_per_residue.csv`, `ubiquitin_sequence_match_check.json` | kecil (JSON/CSV) |
| `results/` | `ubiquitin_residue_features.csv` (76 × 28), `ubiquitin_structure_features.json`, `ubiquitin_plddt_per_residue.png`, `ubiquitin_pae_heatmap.png` | 10.622 B / 7.780 B / 51.470 B / 62.653 B |
| `results/dataset/` | `dataset_manifest.csv` (7), `structure_validation.csv` (7), `pae_validation.csv` (7), `dataset_download_manifest.csv` (7) | 4.364 / 512 / 944 / 2.193 B |
| `results/dataset/` | `multi_protein_residue_features.csv` (**1098 × 29**), `multi_protein_summary.csv` (7), `multi_protein_structure_features.json`, `multi_protein_plddt_overview.png`, `multi_protein_pae_overview.png` | 169.141 B / 742 B / 25.597 B / 136.884 B / 926.520 B |
| `results/dataset/` | **`stage7_processed_dataset.csv`** — benchmark terkunci (**1098 × 27**, 46 positif), SHA256 `34f9dd27…d99f61` | 149.609 B |
| `results/dataset/` | **`stage9_processed_dataset.csv`** — ekspansi Stage 9.2 teraudit (**3.960 × 12**, 14 protein, 129 positif), SHA256 `58e55a29…e10c` | 363.717 B |
| `results/dataset/` | **`stage93_realigned_dataset.csv`** — realignment Stage 9.3 teraudit (**3.960 × 12**, 14 protein, 129 positif), SHA256 `6f035785…7f5a` | 319.050 B |
| `results/dataset/` | **`production_dataset_100_realigned.csv`** — Stage 9.4 production dataset teraudit (**59.188 × 12**, 103 protein, 959 positif), SHA256 `8be323f6…bde1`, LF | 4.619.447 B |
| `results/dataset/` | **`production_dataset_100_cleaned.csv`** — Stage 9.5 cleaned dataset, P11532 dikeluarkan (**55.503 × 12**, 102 protein, 955 positif), SHA256 `e47b3635…05a3`, LF | 4.457.124 B |
| `results/dataset/` | **`production_dataset_100_spatial.csv`** — Stage 10.1 cleaned dataset + 3 fitur spasial radius 8,0 Å (**55.503 × 15**, 102 protein, 955 positif), 0 NaN, SHA256 `8e215340…3319`, LF | 5.313.161 B |
| `results/dataset/` | **`production_dataset_100_calibrated.csv`** — Stage 10.2 features radius 12 Å + 6 kolom skor OOF raw/isotonic/sigmoid (**55.503 × 21**, 102 protein, 955 positif), 0 NaN, SHA256 `2c4bcb3d…ea3a`, LF | 9.667.972 B |
| `results/models/` | **`golden_lightgbm_12a.joblib`** — Stage 11.1 artefak: LightGBM golden, sigmoid + isotonic, 16 nama fitur, parameter, metadata dataset, metrik OOF/in-sample, feature importance, environment; SHA256 `98c86efb…45da` | 157.432 B |
| `docs/` | **`BENCHMARK_DATASET_LOCK.md`** — kontrak benchmark: skema, label A+B, fold map, protokol & metrik Stage 8.2, kebijakan freeze | — |
| `results/` | `01_first_protein_analysis.executed.ipynb`, `notebook_plot_1.png` | output notebook |
| `notebooks/` | `01_first_protein_analysis.ipynb` | materi pembelajaran |

Catatan Stage 9.2/9.3/9.4/9.5: file mentah audit AFDB dan metadata **tidak di-commit**.
Untuk Stage 9.4, audit mengunduh ulang **206 file CIF/PAE (103 protein, ~175 MB)**,
103 respons AFDB API, dan 103 respons UniProt JSON; hanya
`production_dataset_100_realigned.csv` yang dipromosikan ke `results/dataset/`.
`download/stage9_uniprot_metadata.csv` (15 protein, 4.124 baris) tetap tidak
di-commit. Stage 9.5 **tidak mengunduh ulang apa pun**: dataset bersih adalah filter
baris P11532 dari CSV Stage 9.4 yang telah diaudit, sehingga provenance AFDB/UniProt
tetap berlaku untuk seluruh 55.503 baris yang tersisa. Stage 10.1 dan Stage 10.2 juga
**tidak mengunduh ulang**: `download/` hanya berisi CSV/Markdown/notebook, **tanpa file
PDB/CIF/PAE**. Ekstraksi Stage 10.1/10.2 memakai cache audit Stage 9.4 di luar tracked
tree (`stage94_audit/data/afdb_files`, 102 CIF + 102 PAE) dan `afdb_api` (102 JSON);
seluruh baris dicocokkan ulang dengan dataset sebelum fitur ditulis (§20.3, §21.4).
Empat CSV fitur radius 6/8/10/12 Å disimpan di area audit temporer
(`stage102_audit/data`), bukan di tracked tree; hanya CSV terkalibrasi yang dipromosikan.
Audit independen Stage 9.2–9.4 dibahas di §16–§18; verifikasi Stage 9.5 di §19; Stage
10.1 di §20; Stage 10.2 di §21; Stage 10.3 di §22; Stage 11 di §23. Stage 11 tidak membuat
dataset baru: `export_model.py` hanya membaca `production_dataset_100_calibrated.csv` dan
menulis artefak ke `results/models/`. `predict.py --uniprot` mengunduh CIF + PAE AFDB ke cache
OS (atau `--cache-dir`); cache dan file uji P02144/P00520 berada di area temporer, bukan
tracked tree. `download/` tetap tidak berisi CIF/PAE.

### 10.3 Script

| File | Peran |
|---|---|
| `src/analyze_protein.py` | Analisis sekuens (Stage 1) + struktur (Stage 2) |
| `src/extract_protein_features.py` | Ekstraksi fitur per-residu (Stage 3) |
| `src/test_protein_features.py` | Test Stage 3 — 20 check |
| `src/prepare_dataset.py` | Bangun manifest kandidat (Stage 4) |
| `src/test_dataset_manifest.py` | Test Stage 4 — 12 check |
| `src/download_afdb_dataset.py` | Unduhan terkontrol (Stage 5, **sudah dijalankan**) |
| `src/validate_afdb_dataset.py` | Validasi offline CIF/PAE/manifest (Stage 5) |
| `src/test_afdb_download.py` | Test Stage 5 — 16 check |
| `src/extract_multi_protein_features.py` | Ekstraksi fitur multi-protein (Stage 6) |
| `src/test_multi_protein_features.py` | Test Stage 6 — 24 check |
| `src/inference_features.py` | Stage 11 — kontrak 16 fitur, parser CIF/PDB/PAE, fetch + verifikasi AFDB, cache |
| `src/export_model.py` | Stage 11.1 — validasi dataset, reproduksi OOF, fit sigmoid/isotonic, latih final model, tulis joblib |
| `src/predict.py` | Stage 11.2 — CLI inferensi per-residu (UniProt atau struktur lokal + PAE) |

**Script ML pertama di `src/` baru ada di Stage 11.** Baseline Stage 8.2, evaluasi Stage 9.x,
ekstraksi fitur spasial Stage 10.1, sweep radius/kalibrasi Stage 10.2, dan tuning + pemilihan
golden model Stage 10.3 masih dijalankan dengan harness verifikasi eksternal (temporary, di luar
repo). Stage 11 meng-commit tiga script produksi: `inference_features.py`, `export_model.py`,
dan `predict.py`. Tidak ada PyTorch/TensorFlow/CUDA. Environment: `.venv` Python **3.12.10**;
`requirements.txt` kini memuat biopython, pandas, numpy, matplotlib, ipykernel, nbclient, plus
pin Stage 11 `scikit-learn==1.9.1`, `lightgbm==4.6.0`, `scipy==1.18.1`, dan `joblib==1.6.0`.
Verifikasi Stage 8.2 dan Stage 10.3 memakai scikit-learn 1.9.1, xgboost 3.4.1, lightgbm 4.6.0,
scipy 1.18.1, pandas 3.0.6, dan numpy 2.5.3/2.5.4; `xgboost`, `numpy`, dan `pandas` masih berupa
rentang versi, bukan pin eksak (lihat `BENCHMARK_DATASET_LOCK.md` §8).

### 10.4 SHA256 terverifikasi (top-level)

Dihitung ulang **read-only** saat dokumen ini dibuat dan **cocok persis** dengan nilai
yang tercatat di report/manifest:

```
# Benchmark Stage 7 (dihitung ulang 2026-10-20; sumber: download/)
34f9dd27b1d11fb35155f1542e066a50110144cd84c62d91a28caa6ab9d99f61  results/dataset/stage7_processed_dataset.csv

# Realignment Stage 9.3 (dihitung ulang 2026-10-20; sumber: download/)
6f0357858638c57630e0276fb8e46339a16f001e54005dba34adb5b5e3f37f5a  results/dataset/stage93_realigned_dataset.csv

# Production Stage 9.4 (dihitung ulang 2026-10-20; sumber: download/)
8be323f64d1b5f8dbcfff743d378392bafc72e944f051cac5c835f6f54b1bde1  results/dataset/production_dataset_100_realigned.csv

# Cleaned Stage 9.5 (dihitung ulang 2026-10-20; P11532 dikeluarkan)
e47b3635a7e904107094afde02a1ece656e25491c8721865501b6a76562b05a3  results/dataset/production_dataset_100_cleaned.csv

# Spatial Stage 10.1 (dihitung ulang 2026-10-20; radius 8,0 A)
8e21534055132c8cf4eb823e1abda224a15776b437b94bbc851f1ea4a99a3319  results/dataset/production_dataset_100_spatial.csv

# Calibrated Stage 10.2 (dihitung ulang 2026-10-20; radius 12,0 A + 6 skor OOF)
2c4bcb3da7dfe4de82a95902f6fa3156e656cb5aece521b54d427cb42220ea3a  results/dataset/production_dataset_100_calibrated.csv

# Stage 10.3 (2026-10-21): tidak ada dataset baru; hash calibrated di atas diverifikasi ulang

# Stage 11.1 (2026-10-21): artefak model + kalibrator
98c86efbebcb7e7986921386a07ca76319c453536dd8e4a2afd2a9b8085445da  results/models/golden_lightgbm_12a.joblib

# Output Stage 6 (cocok dengan docs/TAHAP_6_MULTI_PROTEIN_FEATURE_REPORT.md §6)
390462a42d8befe5588b1019d51b4c4282433b0f712c4377e5191883983d3c1d  multi_protein_residue_features.csv
111a9569ebf8990eeca19673215f1415e828cc00fd2f6c20a16e9048252660e1  multi_protein_summary.csv
7481765648cbd3b5c340cbacadc79635756d4867254b1003b335680a136587bc  multi_protein_structure_features.json
365d29134a1ab55f5e3464e1155a89a2f04b747adbc7a762521f2d1b5ab23fc5  multi_protein_plddt_overview.png
3e0d1ef035271453d6aba4e54367df6ce0c41dad53693fe1444448a2b3ad77b0  multi_protein_pae_overview.png

# Manifest & input (cocok dengan input_manifest / inputs di JSON terkait)
67ed8a389d29782f0f67edbb49c1a95385fddca00e3f3f9d20db3b4f1d16c3a8  results/dataset/dataset_download_manifest.csv
adc6c6e825893e57590c5c5a2921875c9f06d8279025091b38fc88ad2968aa5d  structures/ubiquitin_alphafold.cif
35100b2cfcb5300b6f969e5b2393ef1c9f644d73f7ac23e49a426d1ec238cff1  data/ubiquitin_sequence.fasta
09178e510be8f5176bb3aeac92935e0f33d2a238346e073fd0668f6a687da61d  fold_2026_10_05_10_26_full_data_0.json
```

14 SHA256 file dataset AFDB (7 CIF + 7 PAE) tercatat lengkap di
`data/alphafold_db/metadata/download_checksums.csv` dan
`docs/TAHAP_5_AFDB_DOWNLOAD_REPORT.md` §16.

---

## 11. Scientific Conclusions

Klaim yang **didukung bukti** di project ini:

1. **Pipeline data end-to-end berjalan.** Sekuens → struktur → fitur per-residu →
   tabel multi-protein, dengan definisi kolom, unit, dan rumus eksplisit.
2. **Ekstraksi fitur bersifat portabel.** Skema Stage 3 berjalan konsisten pada 7
   protein AFDB tanpa mengubah extractor aslinya (dibuktikan 24/24 test Stage 6).
3. **Integritas data terbukti.** 14 file AFDB v6 terverifikasi lewat checksum
   (SHA256 + MD5 + CRC64) dan pencocokan sekuens identik terhadap sumber resmi.
4. **Reproducibility terbukti.** Output dataset deterministik dan byte-identical
   antar-run; tidak ada timestamp/seed/path absolut di output deterministik.
5. **Homogenitas confidence dalam set ini.** Semua 7 protein berprediksi
   high-confidence pada mayoritas residu (mean pLDDT 85,2–97,9). Nilai terendah ada
   pada P0DP23 (calmodulin, mean 85,241; min 41,81).
6. **Benchmark ML baseline sudah dikunci dan reproducible.** Stage 8.2 LOGO-CV pada
   dataset Stage 7 mereproduksi XGBoost persis dan Random Forest dalam toleransi kecil;
   median, IQR, dan pooled tercatat di `BENCHMARK_DATASET_LOCK.md`. Namun pooled ROC
   mendekati acak dan variasi antar-fold besar — ini **baseline pembanding**, bukan
   bukti predictive power biologis.
7. **Stage 9.4 membuktikan integritas data pada skala produksi, bukan generalisasi.**
   59.188 baris memiliki fitur turunan sekuens dan label yang cocok 100% dengan
   UniProt; 56.028 baris yang dimodelkan memiliki fitur struktural yang cocok persis
   dengan AFDB CIF/PAE; dan metrik XGBoost dapat direproduksi persis. Ini adalah bukti
   **engineering, provenance, dan reproducibility** pada 103 protein. P11532 masih
   bermasalah secara struktural (§18.3) dan kemudian dikeluarkan di Stage 9.5 (§19);
   kenaikan pooled ROC tidak boleh dibaca sebagai bukti predictive power biologis
   (§18.5).
8. **Stage 9.5 mengukur dampak pembersihan dan mengoreksi artefak pooled ROC.**
   Mengeluarkan P11532 dan me-retrain model menurunkan pooled ROC XGB dari 0,7575 ke
   0,7476, tetapi **menaikkan** pooled PR dari 0,0606 ke 0,0640 dan median per-protein
   ROC dari 0,7359 ke 0,7371. Within-protein z-scored ROC tetap 0,6877 (XGB) / 0,6891
   (RF), jauh di bawah pooled ROC 0,7476. Artinya sebagian kenaikan pooled ROC Stage 9.4
   berasal dari artefak isoform/missingness P11532, bukan dari diskriminasi biologis
   yang lebih baik. Dataset Stage 9.5 lengkap secara struktural (0 sel kosong) dan lebih
   valid sebagai titik awal analisis berikutnya, tetapi tetap bukan bukti generalisasi
   (§19).
9. **Stage 10.1 menunjukkan fitur lingkungan spasial menambah sinyal internal.** Dengan
   tiga fitur radius 8,0 Å, XGBoost median ROC naik 0,7371 → 0,7786 dan pooled ROC
   0,7476 → 0,7676; RF median ROC 0,7330 → 0,7724 dan pooled ROC 0,7476 → 0,7568.
   Kenaikan juga terjadi pada within-protein z-scored ROC (XGB 0,6877 → 0,7156; RF
   0,6891 → 0,7059) dan pada 49/78 (XGB) serta 54/78 (RF) fold evaluable. Ini bukti
   bahwa informasi geometri lokal tidak sepenuhnya terkandung dalam fitur 1D/PAE
   sebelumnya. Namun dataset, protein, dan label sama dengan Stage 9.5; tidak ada
   protein baru atau holdout eksternal, sehingga hasil ini tetap **bukan** bukti
   generalisasi biologis (§20.6).
10. **Stage 10.2 memisahkan skala probabilitas dari diskriminasi.** Sweep radius menunjukkan
    sinyal spasial meningkat sampai 12 Å: XGB median ROC 0,7437 (6 Å) → 0,7786 (8 Å) → 0,8049
    (10 Å) → 0,8120 (12 Å), dengan Friedman p = 1,49e-06; pola RF serupa (0,7331 → 0,8089,
    p = 3,32e-14). Namun kalibrasi isotonic/sigmoid hanya memperbaiki **skala absolut**:
    mean predicted XGB turun dari 0,3741 ke 0,0176 (prevalensi 0,0172), Brier dari 0,1820 ke
    0,0163, ECE dari 0,3569 ke 0,0016. Metrik peringkat justru sedikit turun (pooled ROC XGB
    0,7956 → 0,7900 isotonic / 0,7947 sigmoid; within-z 0,7495 → 0,7418 / 0,7475), dan
    between-protein AUC tidak meningkat secara konsisten (XGB 0,7828 → 0,7889 / 0,7859;
    RF 0,7870 → 0,7847 / 0,7839). Artinya **score inflation
    antar-protein adalah masalah peringkat/skor rata-rata protein, bukan masalah kalibrasi
    skala**; kalibrasi tidak boleh diklaim sebagai perbaikan generalisasi (§21.5–§21.7).
11. **Stage 10.3 memilih golden LightGBM secara internal, dengan optimisme seleksi yang
    terukur.** Dari 101 konfigurasi unik, `lgbm__032c38ffe37f` memberi median ROC 0,8411 / PR
    0,1693 dan pooled ROC 0,8131 / PR 0,1142 / gain 6,63× pada 78 fold evaluable. Nested
    LOGO-CV menurunkan median PR ke 0,1550 dan pooled gain ke 4,55×; kandidat nested tetap
    berasal dari tuning global. Brier/ECE golden (0,0520/0,1228) adalah skor mentah, bukan
    probabilitas terkalibrasi, dan seluruh evaluasi memakai 102 protein yang sama (§22).
12. **Stage 11 membuktikan artefak dan CLI reproducible, bukan performa biologis.** OOF Stage
    10.3 direproduksi dengan selisih 0,0; model final dilatih pada 55.503 baris; sigmoid
    di-fit pada OOF dan memberi Brier 0,016072 / ECE 0,000811 dengan mean predicted 0,017206
    setara prevalensi. `predict.py` menghasilkan fitur P02144 yang cocok dengan dataset
    (maksimum 3,55e-15; 0 nilai > 1e-12) dan probabilitas model identik bit, serta berjalan
    tanpa error pada P02144 dan P00520 dari UniProt, CIF lokal, dan PDB lokal. Ini bukti
    **reproducibility engineering dan deployment**, bukan validasi eksternal: kalibrator
    in-sample terhadap protein yang sama, model final melihat semua label, dan ambang 0,5
    tidak tervalidasi (§23).

**Tidak ada** kesimpulan biologis atau fungsional yang ditarik dari data ini, dan itu
memang keputusan desain project — lihat bagian 12.

---

## 12. What Has NOT Been Proven

Bagian ini adalah pembatas tegas antara apa yang **sudah** dan **belum** terbukti.
Tujuh butir A–G berikut dipertahankan eksplisit:

**A. Engineering/data pipeline berhasil — TERBUKTI.**
Empat script inti + empat test suite berjalan exit 0; output deterministik.

**B. Struktur AlphaFold berhasil diperoleh/divalidasi — TERBUKTI (dalam arti
integritas data, bukan kebenaran biologis).**
14/14 file AFDB v6 tervalidasi; sekuens 7/7 identik dengan `uniprotSequence` resmi.
Yang tervalidasi adalah **keutuhan file dan identitas sekuens**, bukan kebenaran
struktur 3D di dalam sel.

**C. Feature extraction berhasil — TERBUKTI.**
1098 × 29 kolom dihasilkan dengan 24/24 test PASS dan rekalkulasi independen
terhadap matriks PAE mentah.

**D. Predictive biological AI sudah diuji sebagai baseline, dengan fitur spasial, sweep
radius, dan kalibrasi out-of-fold, tetapi belum terbukti bergeneralisasi.**
Stage 8.2 LOGO-CV sudah dijalankan dan direproduksi (median/IQR dan pooled di
`BENCHMARK_DATASET_LOCK.md`). Stage 10.1 menambahkan tiga fitur spasial radius 8,0 Å, dan
Stage 10.2 memilih radius 12 Å lewat aturan pra-deklarasi serta menguji kalibrasi
isotonic/sigmoid per fold. Metrik internal naik lagi (XGB pooled ROC 0,7956, within-protein
0,7495; RF 0,7759 / 0,7338), dan kalibrasi memperbaiki skala absolut (ECE 0,3569 → 0,0016),
tetapi semuanya diukur pada 102 protein yang sama, tanpa holdout eksternal. Yang terbukti
adalah **reproducibility protokol, angka baseline, tambahan sinyal dari fitur geometri
lokal, dan pemisahan antara kalibrasi skala dan diskriminasi peringkat**, bukan predictive
power biologis umum.

**E. Tidak ada klaim bahwa fitur saat ini sudah punya predictive power biologis —
TIDAK DIKLAIM.**
Fitur yang ada adalah deskriptor struktural/geomik turunan prediksi (identitas residu,
hidropati, muatan, koordinat, pLDDT, ringkasan PAE). Uji baseline Stage 8.2 menunjukkan
sinyal lemah dan heterogen; hasil itu tidak boleh dibaca sebagai kemampuan model
memprediksi fungsi protein pada umumnya. Tidak ada klaim generalisasi.

**F. Dataset ML masih belum memadai untuk klaim generalisasi — DIAKUI.**
Benchmark Stage 8.2 hanya berisi 7 protein / 1.098 residu / 46 positif. Stage 9.4
memperbesar skala ke **103 protein / 59.188 residu / 959 positif**, dan Stage 9.5
membersihkannya menjadi **102 protein / 55.503 residu / 955 positif (1,72%)**, tetapi
keterbatasan dasarnya tetap: (1) hanya 955 positif dan 24 protein tanpa positif;
(2) residu dalam satu protein sangat berkorelasi — 55.503 baris **bukan** 55.503 sampel
independen; (3) komposisi protein belum diseleksi sebagai holdout eksternal dan belum
tentu mewakili protein membran, kompleks, atau daerah tak terstruktur; (4) semua fitur
dan label masih berasal dari prediksi/annotation, bukan validasi eksperimen. P11532
sudah dikeluarkan di Stage 9.5 sehingga masalah isoform tidak lagi mencemari dataset
bersih, tetapi itu tidak menambah bukti generalisasi. Stage 10.1/10.2 menambah fitur
turunan struktur pada **102 protein yang sama**; fitur-fitur itu tetap berkorelasi dengan
pLDDT/PAE yang sudah ada (pada radius 12 Å: `spatial_plddt_mean_12a` vs `plddt_ca`
Pearson 0,9730; `spatial_pae_mean_12a` vs `pae_local_mean_k10` Spearman 0,8956) dan tidak
menambah protein atau sampel independen. Sweep radius memilih 12 Å secara internal, bukan
lewat holdout. Menghitung "N = 55.503" sebagai ukuran sampel statistik adalah keliru.
Status 2026-10-20: benchmark Stage 8.2 tetap terkunci, dan Stage 10.2 belum mengubah status
generalisasi.

**G. Stage 7 (label A+B) SELESAI; ekspansi protein SELESAI sampai 102 protein;
feature engineering spasial Stage 10.1, sweep radius + kalibrasi Stage 10.2, tuning Stage 10.3,
dan ekspor artefak + CLI Stage 11 SELESAI; pertanyaan biologis lanjutan BELUM.**
Stage 7 menetapkan label biner **Active site + Binding site** dan fold LOGO, lalu
Stage 8.2 menetapkan baseline. Ekspansi 14 → 103 → 102 protein sudah dikerjakan di
Stage 9.2–9.5, Stage 10.1 menambahkan fitur lingkungan 3D pada dataset 102 protein yang
sama, Stage 10.2 memilih radius 12 Å serta menguji kalibrasi out-of-fold pada protein yang
sama, Stage 10.3 men-tuning dan memilih golden LightGBM, dan Stage 11 mengekspor model +
kalibrator serta menambahkan CLI inferensi. Pertanyaan yang lebih luas (GO terms, EC numbers,
multi-label) dan validasi eksternal **belum** dikerjakan. Menjalankan `predict.py` pada
protein baru menghasilkan skor, bukan evaluasi: tanpa label independen, itu bukan validasi. 102 protein masih terlalu sedikit dan terkorelasi untuk
klasifikasi umum; `DATASET_PLAN.md` §9 masih berupa usulan arah.

Tambahan yang juga **belum** terbukti/dilakukan:
- Tidak ada validasi terhadap struktur eksperimen (PDB) — tidak ada RMSD, tidak ada
  perbandingan dengan kristalografi/NMR/cryo-EM.
- Tidak ada klaim bahwa pLDDT/PAE tinggi berarti struktur benar di dalam sel.
- Tidak ada docking, molecular dynamics, skrining senyawa, atau eksperimen basah.
- Tidak ada model prediksi fungsi yang tervalidasi/generalisasi; baseline Stage 8.2 bukan
  "penemuan".
- Tidak ada evaluasi berlabel pada protein baru. Stage 11 hanya mendemonstrasikan bahwa model
  yang sudah ada dapat dijalankan; P02144 dan P00520 adalah protein training, sehingga skor
  keduanya **bukan** validasi eksternal.

---

## 13. Known Limitations / Concerns

Diurutkan dari yang paling berdampak pada tahap berikutnya.

| # | Concern | Tingkat | Sumber | Status penanganan |
|---|---|---|---|---|
| C1 | **Skema Stage 6 = 26 fitur, bukan 28.** `contact_prob_sum` & `n_high_conf_contacts` dikeluarkan karena `contact_probs` tidak tersedia di AFDB | Tinggi (mempengaruhi desain fitur ML) | Stage 6 report §5, §10.1 | **SELESAI untuk benchmark:** Stage 7 menetapkan 27 kolom (25 shared + label + fold); Stage 8.2 memakai 13 fitur. Eksperimen fitur lain tetap terbuka |
| C2 | **Redundansi pLDDT AFDB.** CIF AFDB menulis pLDDT per-residu ke semua atom → di 1098 baris: `plddt_atom_std = 0`, `plddt_atom_mean = min = max = plddt_ca`. 4 kolom `plddt_atom_*` redundan dengan `plddt_ca` | Tinggi (risiko multikolinearitas sempurna bila dipakai ML apa adanya) | Stage 6 report §10.2 | **SELESAI:** 4 kolom `plddt_atom_*` dibuang dari dataset benchmark dan tidak dipakai Stage 8.2 |
| C3 | **Skala dataset tidak memadai untuk ML.** Benchmark 7 protein / 1098 residu berkorelasi; Stage 9.5/10.1/10.2/10.3/11 berisi 102 protein / 55.503 residu tetapi hanya 955 positif; Stage 10.1–11 tidak menambah protein | Tinggi | Stage 4 plan §6, Stage 6 report, §19, §20, §21, §22, §23 | **TETAP:** diakui eksplisit (butir F); benchmark dikunci dan Stage 10.1–11 belum menjadi validasi eksternal |
| C4 | **Belum ada label (y).** Tidak ada target prediksi yang dipilih | Tinggi (blocker untuk ML) | `DATASET_PLAN.md` §9 | **SELESAI:** label A+B (Active site + Binding site), 46 positif, audit 7/7 protein |
| C5 | **Koordinat mentah tidak invariant rotasi/translasi** (`ca_x/y/z`, `centroid_*`) | Sedang | Stage 3 JSON, `DATASET_PLAN.md` §8 | **DIHINDARI di benchmark:** koordinat tidak dipakai Stage 8.2; tetap ada di CSV beku sebagai dokumentasi |
| C6 | **Versi AFDB v6 dapat berubah** di masa depan | Sedang (eksternal) | Stage 5 report §14.2 | SHA256 tercatat sebagai titik referensi; perubahan server akan terdeteksi sebagai hash berbeda |
| C7 | **Dua sistem checksum berbeda** (AFDB = MD5 32 hex; UniProt = CRC64 16 hex) | Rendah (risiko salah baca manual) | Stage 5 report §11, §14.1 | Keduanya diverifikasi cocok; terdokumentasi |
| C8 | **PAE asimetris** (maks \|PAE − PAEᵀ\| = 19–24 Å di 7/7 protein) | Rendah (wajar matematis) | Stage 6 report §10.3 | Arah matriks dipertahankan; test check 10 memverifikasi tidak ada transpose tak sengaja |
| C9 | **Campuran int/float di sel PAE** (mis. 0, 31 bercampur float) | Rendah (karakter data) | Stage 5 report §14.3 | Tidak diubah; nilai min/max di `pae_validation.csv` hanya deskriptif |
| C10 | **Semua fitur = prediksi model**, bukan pengukuran eksperimen | Fundamental (melekat) | Semua report | Dinyatakan berulang di README, JSON, dan kedua report |
| C11 | **RNase1 memakai prekursor 1–150** (termasuk signal peptide), bukan RNase A mature 124 residu | Rendah | `dataset_manifest.csv` notes, Stage 5 report §14.4 | Tercatat di manifest |
| C12 | **Ligand/ion/kovalen tidak dimodelkan** (heme pada myoglobin & cytochrome c; Cu/Zn pada SOD1; kromofor GFP terbentuk post-translasi) | Sedang (interpretasi) | `dataset_manifest.csv` notes, `DATASET_PLAN.md` §6 | Tercatat per baris di manifest |
| C13 | **Provenance gap Stage 7.** Script pembuat `stage7_processed_dataset.csv` tidak ada di `src/`; file datang sebagai artefak dan diaudit ulang terhadap Stage 6 + UniProt | Sedang | `BENCHMARK_DATASET_LOCK.md` §2 | Tercatat; rebuild from source belum one-command |
| C14 | **Dependensi ML belum sepenuhnya dipin.** Stage 11 mem-pin scikit-learn 1.9.1, lightgbm 4.6.0, scipy 1.18.1, dan joblib 1.6.0 di `requirements.txt`; xgboost, numpy, dan pandas masih berupa rentang versi | Sedang (reproducibility) | `BENCHMARK_DATASET_LOCK.md` §8; §10.3 | **SEBAGIAN SELESAI:** pin Stage 11 ditambahkan; xgboost/numpy/pandas masih terbuka |
| C15 | **Toleransi reproduksi RF.** XGB cocok persis; RF median berbeda ≤0,0011 dan pooled ≤0,0085, konsisten dengan perbedaan versi/implementasi scikit-learn | Rendah | `BENCHMARK_DATASET_LOCK.md` §7.4 | Tercatat; nilai resmi dan perbandingan didokumentasikan |
| C16 | **Definisi `pae_local_mean_k10` Stage 9.2 menyimpang.** Nilai CSV adalah mean `PAE[i, i-5:i+6]` **termasuk residu sendiri** (jendela ±5), bukan `\|i-j\| ≤ 10, j ≠ i` seperti Stage 3/8.2. Seluruh 3.960 nilai berbeda dari definisi frozen (selisih maks 8,1 Å) | Tinggi (komparabilitas) | Audit Stage 9.2 §16 | **SELESAI di Stage 9.3:** seluruh 3.960 nilai dihitung ulang dengan definisi frozen (0 mismatch). Stage 9.2 tetap disimpan sebagai artefak historis |
| C17 | **Klasifikasi histidin Stage 9.2 berbeda.** H diberi `amino_acid_type = aromatic` (108 residu), sedangkan tabel frozen Stage 3/8.2 = `basic` | Sedang (fitur one-hot) | Audit Stage 9.2 §16 | **SELESAI di Stage 9.3:** 108 residu H dikembalikan ke `basic`; satu-satunya perubahan kategori vs Stage 9.2 |
| C18 | **P00720 tidak ada di AFDB.** Endolysin (164 aa) tidak punya entri AFDB (HTTP 404), sehingga dataset processed berisi 14 protein, bukan 15; metadata 15 protein tetap mencakup P00720 | Rendah–sedang (cakupan) | Audit Stage 9.2 §16 | **TERCATAT:** 14 fold, 13 evaluable (P01308 nol positif) |
| C19 | **Ringkasan Stage 9.2 salah hitung positif.** Markdown menyebut 123 positif, sedangkan CSV berisi 129 (3,26%). Metrik tetap reproduce karena dihitung dari CSV | Rendah (dokumentasi) | Audit Stage 9.2 §16 | **TERCATAT:** angka yang benar = 129 |
| C20 | **IQR PR Stage 9.3 tidak reproduce.** Ringkasan menyebut XGB 0,1348 dan RF 0,2259; perhitungan ulang dari per-fold PR (semua metode kuantil yang diuji) menghasilkan 0,1796 dan 0,2461. Median, pooled, dan gain cocok | Sedang (dokumentasi metrik) | Audit Stage 9.3 §17.4 | **TERCATAT:** docs memakai nilai reproduced; nilai klaim dicantumkan sebagai pembanding |
| C21 | **P11532 memakai isoform AFDB yang tidak selaras.** `/api/prediction/P11532` mengembalikan 14 entri isoform, tanpa entri kanonik 3.685 aa; dataset memakai entri pertama `AF-P11532-9-F1` (525 aa). Sekuens CIF berbeda pada **496/525 posisi** dari sekuens kanonik, sehingga 525 baris struktural tidak selaras; 3.160 baris lainnya kosong dan 4 positifnya tidak punya fitur struktural | Tinggi (validitas data) | Audit Stage 9.4 §18.3 | **SELESAI di Stage 9.5:** seluruh 3.685 baris P11532 dikeluarkan; dataset bersih 102 protein / 55.503 baris / 955 positif, 0 sel kosong (§19) |
| C22 | **Metrik RF Stage 9.4 hanya sebagian reproduce.** Pooled ROC 0,7471 cocok persis, tetapi median ROC klaim 0,7397 vs reproduced 0,7339; pooled PR klaim 0,0592 vs 0,0573; gain klaim 3,65× vs 3,53×. Konfigurasi alternatif yang diuji tidak menghasilkan 0,7397 persis | Sedang (dokumentasi metrik) | Audit Stage 9.4 §18.4 | **TERCATAT:** docs memakai nilai reproduced dan mencantumkan nilai klaim sebagai pembanding |
| C23 | **Pooled ROC Stage 9.4 tidak sebanding dan dapat terinflasi.** 0,7575 vs Stage 8.2 0,5368 berasal dari dataset, prevalensi, dan jumlah fold berbeda; pooled ROC dipengaruhi urutan skor antar-protein. Within-protein z-scored ROC 0,6876; between-protein AUC 0,7922; median per-protein hanya naik +0,0174 dari Stage 8.2. Setelah P11532 dikeluarkan, Stage 9.5 pooled ROC 0,7476 dengan within-protein 0,6877 dan between-protein AUC 0,7851. Stage 10.1 menaikkan pooled ROC ke 0,7676 (XGB) / 0,7568 (RF), tetapi within-protein baru 0,7156/0,7059 dan between-protein AUC 0,7785/0,7824 — inflasi antar-protein tetap ada | Tinggi (interpretasi) | Audit Stage 9.4 §18.5, Stage 9.5 §19.4, Stage 10.1 §20.6 | **TERCATAT:** kenaikan pooled dicatat sebagai angka, tetapi **tidak** diklaim sebagai bukti generalisasi; metrik within-protein tetap dilaporkan sebagai pembanding |
| C24 | **Pembersihan P11532 mengubah metrik pooled.** Stage 9.4 pooled ROC XGB 0,7575 → Stage 9.5 0,7476 (−0,0099) setelah P11532 dikeluarkan dan model di-retrain; pooled PR naik 0,0606 → 0,0640, median ROC naik 0,7359 → 0,7371. Random Forest pooled ROC 0,7471 → 0,7476, pooled PR 0,0573 → 0,0608, median ROC 0,7339 → 0,7330. | Sedang (interpretasi) | Audit Stage 9.5 §19.3–§19.4 | **TERCATAT:** metrik dataset bersih dilaporkan terpisah; Stage 9.4 tetap menjadi artefak historis, bukan angka resmi dataset bersih |
| C25 | **Fitur spasial tidak independen dari fitur yang sudah ada.** Pada radius 12 Å, `spatial_plddt_mean_12a` vs `plddt_ca` Pearson 0,9730 / Spearman 0,9674; `spatial_pae_mean_12a` vs `pae_local_mean_k10` Pearson 0,6795 / Spearman 0,8956; `spatial_density_12a` vs `plddt_ca` Pearson 0,7048. Sweep radius 6/8/10/12 Å sudah dilakukan di Stage 10.2 dan memilih 12 Å, tetapi ablasi fitur dan uji stabilitas importance belum dijalankan. Fitur dihitung dari struktur prediksi AFDB, bukan struktur eksperimen. | Sedang (interpretasi fitur) | Audit Stage 10.1 §20.4, Stage 10.2 §21.3 | **SEBAGIAN SELESAI:** sensitivitas radius sudah diuji dan 12 Å dipilih dengan aturan pra-deklarasi; kolinearitas tetap tinggi dan tidak diklaim sebagai informasi biologis independen. Ablasi fitur, stabilitas importance, dan struktur eksperimen belum dilakukan |
| C26 | **`download/` tidak berisi file PDB/CIF/PAE.** Permintaan Stage 10.1 mengasumsikan file struktur ada di `download/`, tetapi folder itu hanya berisi CSV/Markdown/notebook. Ekstraksi memakai cache audit Stage 9.4 di luar tracked tree (102 CIF + 102 PAE + 102 API JSON); tidak ada unduhan baru. | Rendah–sedang (provenance) | Audit Stage 10.1 §20.3, D12 | **TERCATAT:** seluruh 55.503 baris dicocokkan ulang dengan CIF/PAE sebelum fitur ditulis; hash input per protein dicatat di audit JSON temporer. Cache mentah tidak di-commit |
| C27 | **Kalibrasi tidak memperbaiki inflasi antar-protein.** Isotonic/sigmoid out-of-fold memperbaiki skala absolut secara dramatis (XGB mean predicted 0,3741 → 0,0176; Brier 0,1820 → 0,0163; ECE 0,3569 → 0,0016), tetapi pooled ROC 0,7956 → 0,7900/0,7947, within-protein z-scored ROC 0,7495 → 0,7418/0,7475, dan between-protein AUC hanya bergeser kecil serta tidak konsisten arahnya (XGB 0,7828 → 0,7889/0,7859; RF 0,7870 → 0,7847/0,7839). Urutan rata-rata skor protein hampir tidak berubah (Spearman vs raw 0,9895 isotonic / 0,9955 sigmoid). | Tinggi (interpretasi kalibrasi) | Audit Stage 10.2 §21.5–§21.7 | **TERCATAT:** kalibrasi dilaporkan sebagai perbaikan skala probabilitas, bukan perbaikan diskriminasi atau generalisasi. Metrik within-protein dan between-protein tetap dilaporkan terpisah |
| C28 | **Enam kolom OOF adalah artefak audit, bukan fitur latih.** `production_dataset_100_calibrated.csv` memuat `oof_{xgb,rf}_{raw,isotonic,sigmoid}`; setiap nilai berasal dari model yang tidak melihat protein baris tersebut, tetapi memakai kolom itu sebagai fitur tanpa nested CV akan menyebabkan leakage. | Tinggi (risiko misuse dataset) | Audit Stage 10.2 §21.4 | **TERCATAT:** header/README menyatakan kolom 16–21 adalah skor OOF; dataset tidak boleh dipakai sebagai feature table tanpa protokol nested CV baru |
| C29 | **Kalibrator Stage 11 in-sample dan model final melihat seluruh label.** Sigmoid di-fit pada skor OOF 102 protein yang sama yang dipakai memilih fitur/radius/tuning; model final dilatih pada seluruh 55.503 baris. Brier 0,016072 / ECE 0,000811 adalah diagnostik kalibrasi, bukan estimasi performa pada protein baru. Ambang 0,5 tidak tervalidasi; P02144/P00520 mendapat 0 panggilan. | Tinggi (risiko salah tafsir) | Audit Stage 11 §23 | **TERCATAT:** artefak menyimpan `limitations` dan README/docs menyatakan deployment ≠ validasi; gate validasi eksternal tetap terbuka |
| C30 | **Kontrak input inferensi sempit.** `predict.py` mewajibkan PAE N×N, pLDDT di kolom B-factor [0,100], satu chain (atau `--chain`), penomoran 1..N tanpa insertion code, dan tidak melakukan imputasi; residu tanpa tetangga radius 12 Å = error. PDB eksperimental umumnya tidak didukung. File joblib adalah pickle dan hanya boleh dimuat dari sumber tepercaya; AFDB versi selain v6 memicu warning pergeseran distribusi. | Sedang (batasan penggunaan) | Audit Stage 11 §23 | **TERCATAT:** syarat didokumentasikan di CLI `--help`, README, dan §23; tidak ada klaim dukungan struktur eksperimen |

---

## 14. Current Reproducibility Status

**Status: KUAT untuk data & fitur; BASELINE ML TERVERIFIKASI DENGAN CATATAN.**

| Aspek | Status | Bukti |
|---|---|---|
| Ekstraksi fitur deterministik | **Ya** | Stage 6 report §9: dijalankan ≥3× (2 manual + 1 oleh test check 15 ke direktori temporer), **semua 5 output byte-identical** |
| Bebas timestamp/seed/path absolut di output | **Ya** | Diverifikasi regex oleh test Stage 6 check 17 (CSV: LF + UTF-8; PNG: matplotlib Agg; JSON: path relatif POSIX) |
| Integritas input dikunci | **Ya** | Extractor memverifikasi SHA256 tiap file mentah terhadap manifest sebelum diproses; test memverifikasi ulang (E3/E4) |
| Checksum dapat diverifikasi ulang oleh siapa pun | **Ya** | `download_checksums.csv` + test Stage 5 menghitung ulang dari disk |
| Test suite saling menjaga | **Ya** | Test Stage 6 (check 18 & 19) menjalankan ulang test Stage 3 & Stage 5; keduanya tetap lulus |
| **Verifikasi dalam dokumen ini** | **Parsial** | Hash top-level (bagian 10.4) **dihitung ulang read-only dan cocok persis**. Test suite pipeline data tidak dijalankan ulang; satu-satunya eksperimen baru adalah verifikasi Stage 8.2 (lihat `BENCHMARK_DATASET_LOCK.md` §7) |
| Reproducibility ML | **Sebagian** | Stage 8.2: XGB cocok persis dengan ringkasan, RF dalam toleransi; harness verifikasi di luar repo dan dependensi belum dipin (`BENCHMARK_DATASET_LOCK.md` §8) |
| Reproducibility Stage 9.2 | **YA untuk metrik, dengan catatan** | XGB median/pooled cocok persis; RF IQR ROC selisih 0,0011 dan pooled ROC 0,0001; environment pinned (numpy 2.5.4, pandas 3.0.6, scipy 1.18.1, scikit-learn 1.9.1, xgboost 3.4.1) |
| Reproducibility Stage 9.3 | **YA untuk median/pooled/gain; TIDAK untuk IQR PR** | XGB median/pooled/gain persis; RF median persis, pooled ROC 0,6575 vs klaim 0,6577, pooled PR 0,0912 vs 0,0913; IQR PR reproduced 0,1796/0,2461 vs klaim 0,1348/0,2259 (C20); environment sama |
| Reproducibility Stage 9.4 (XGB) | **YA — persis** | Median ROC 0,7359; pooled ROC 0,7575; pooled PR 0,0606; gain 3,7384×; 79/103 fold evaluable; environment sama |
| Reproducibility Stage 9.4 (RF) | **SEBAGIAN** | Pooled ROC 0,7471 cocok persis; median ROC 0,7339 vs klaim 0,7397; pooled PR 0,0573 vs klaim 0,0592; gain 3,53× vs klaim 3,65× (C22) |
| Reproducibility Stage 9.5 (XGB) | **DIHITUNG LANGSUNG DARI CSV BERSIH** | 102 fold / 78 evaluable; median ROC 0,7371, PR 0,0673; pooled ROC 0,7476, PR 0,0640, gain 3,7174×; 55.503 baris; environment sama |
| Reproducibility Stage 9.5 (RF) | **DIHITUNG LANGSUNG DARI CSV BERSIH** | 102 fold / 78 evaluable; median ROC 0,7330, PR 0,0731; pooled ROC 0,7476, PR 0,0608, gain 3,5331×; konfigurasi default yang sama |
| Reproducibility Stage 10.1 (XGB) | **DIHITUNG LANGSUNG DARI CSV SPASIAL** | 102 fold / 78 evaluable; 16 fitur; median ROC 0,7786, PR 0,0925; pooled ROC 0,7676, PR 0,0759, gain 4,4089×; 55.503 baris; environment sama |
| Reproducibility Stage 10.1 (RF) | **DIHITUNG LANGSUNG DARI CSV SPASIAL** | 102 fold / 78 evaluable; 16 fitur; median ROC 0,7724, PR 0,0894; pooled ROC 0,7568, PR 0,0668, gain 3,8824×; konfigurasi default yang sama |
| Reproducibility Stage 10.2 — radius sweep | **DIHITUNG LANGSUNG, 4 RADIUS × 2 MODEL** | 78 fold evaluable pada setiap radius; r6/r8/r10/r12; XGB median ROC 0,7437/0,7786/0,8049/0,8120; RF 0,7331/0,7724/0,7946/0,8089; Friedman ROC XGB p=1,49e-06, RF p=3,32e-14; environment sama; fitur radius 6/8/10/12 direproduksi independen (0 mismatch) |
| Reproducibility Stage 10.2 — kalibrasi | **OUT-OF-FOLD, INNER GROUPKFOLD 3** | Per fold LOGO: base model pada 101 protein latih, kalibrator pada inner out-of-fold (GroupKFold 3, grouped by protein), `CalibratedClassifierCV(..., ensemble=False)`; protein uji tidak pernah dipakai. 78 fold; Brier/ECE/mean predicted/slope dan pooled/within-z direproduksi dari CSV terkalibrasi; selisih metrik probabilitas < 1e-10 |
| Reproducibility Stage 10.2 — dataset | **VERIFIKASI INDEPENDEN** | 55.503 × 21; 15 kolom fitur string-identik dengan CSV r12; 6 kolom OOF = npz sumber (selisih maks ≤ 5e-11); 0 NaN; LF murni; SHA256 `2c4bcb3d…ea3a`; rank pooled RF isotonic bergeser ~1e-6 hanya karena pembulatan 10 desimal menciptakan tie |
| Reproducibility Stage 10.3 — tuning | **DIHITUNG LANGSUNG; 101 KONFIGURASI** | 102 fold / 78 evaluable; 44 XGB + 46 LGBM + 8 RF (+3 re-eval); LightGBM pass 1 dijalankan ulang penuh dan 23/23 konfigurasi mereproduksi seluruh 8 metrik hingga 1e-12; tiga konfigurasi seleksi-pass (derived) dievaluasi ulang sebagai konfigurasi tetap; environment sama dengan Stage 10.2 |
| Reproducibility Stage 10.3 — golden | **EVAL ULANG KONFIGURASI TETAP, OOF IDENTIK** | `lgbm__032c38ffe37f`; 102 fold / 78 evaluable; median ROC 0,8411 / PR 0,1693; pooled ROC 0,8131 / PR 0,1142 / gain 6,6345×; within-z 0,7709; Brier 0,0520; ECE 0,1228; OOF 55.503 baris, 0 NaN, 955 positif; perbedaan vs OOF tuning = 0,0 (bit-identik) |
| Reproducibility Stage 10.3 — nested | **NESTED LOGO-CV, INNER GROUPKFOLD 5** | Outer 102 fold; 4 kandidat (3 efektif unik); median ROC 0,8303 / PR 0,1550; pooled ROC 0,7961 / PR 0,0784 / gain 4,5549×; within-z 0,7680; Brier 0,0340; XGB dipilih 81 fold, LGBM 11+10; kandidat berasal dari tuning global sehingga masih mengandung komponen optimistis |
| Reproducibility Stage 11 — export | **OOF DIREPRODUKSI, ARTEFAK DIHASH** | 55.503 baris / 102 protein / 955 positif; OOF golden dihitung ulang dengan selisih maksimum 0,0 vs Stage 10.3; dataset divalidasi terhadap SHA256 `2c4bcb3d…ea3a`, 9.667.972 B, 55.503 baris, 102 protein, 955 positif; artefak 157.432 B, SHA256 `98c86efb…45da`; environment Python 3.12.10, numpy 2.5.3, pandas 3.0.6, scikit-learn 1.9.1, lightgbm 4.6.0, scipy 1.18.1, joblib 1.6.0 |
| Reproducibility Stage 11 — kalibrasi | **FIT PADA OOF, BUKAN HOLDOUT** | Sigmoid (`C=1e6`, lbfgs, max_iter 1000, tol 1e-10) pada logit OOF; koefisien 0,8216068, intercept −2,7257097; Brier 0,016072 / ECE 0,000811 / mean 0,017206 vs prevalensi 0,017206; isotonic pembanding Brier 0,015955 tetapi 45 nilai unik; metrik ini diagnostik in-sample, bukan estimasi protein baru |
| Reproducibility Stage 11 — CLI | **UJI END-TO-END, 0 ERROR** | P02144 154 residu dari CIF lokal, PDB lokal, unduhan AFDB, dan cache — kolom numerik identik; paritas fitur vs dataset maksimum 3,55e-15 (0 nilai > 1e-12), probabilitas raw/calibrated identik bit; P00520 1.123 residu exit 0; PAE hilang dan multi-chain tanpa `--chain` exit 2; `--chain A` exit 0 |

Catatan: satu-satunya artefak non-deterministik yang diketahui adalah
`data/alphafold_db/metadata/download_log.txt` (timestamp + path absolut lokal) — file
log, bukan output dataset, dan tidak dipakai sebagai input analisis.

---

## 15. Current Project Position

**Posisi: Stage 11 dieksekusi dan diuji — golden LightGBM diekspor bersama kalibrator
sigmoid ke artefak joblib, dan CLI `predict.py` berjalan end-to-end pada P02144/P00520;
benchmark Stage 8.2 tetap terkunci dan tidak berubah. Ini deployment, bukan validasi
eksternal.**

- Stage 1–6 selesai dan terdokumentasi; concern C1, C2, C4, dan C5 sudah ditutup
  untuk benchmark (C3 tetap).
- Stage 7 selesai: dataset 1098 × 27, label A+B, 7-fold LOGO, dikunci dengan SHA256.
- Stage 8.2 selesai dan direproduksi: XGB cocok persis, RF dalam toleransi kecil;
  median/IQR + pooled tercatat di `docs/BENCHMARK_DATASET_LOCK.md`.
- Stage 9.2 dan Stage 9.3 selesai sebagai ekspansi/realignment 14 protein / 3.960
  residu; fitur dan label terverifikasi terhadap AFDB/UniProt.
- **Stage 9.4 menyelesaikan production scaling:** 103 protein / 59.188 residu /
  959 positif; seluruh fitur turunan sekuens dan label cocok 100% dengan UniProt,
  dan fitur struktural 56.028 baris cocok persis dengan AFDB CIF/PAE; XGBoost
  reproduce persis, RF hanya pooled ROC yang exact (C22).
- **Stage 9.5 menyelesaikan pembersihan:** P11532 (3.685 baris) dikeluarkan karena
  isoform AFDB tidak selaras; dataset bersih **55.503 × 12**, 102 protein, 955
  positif (1,7206%), **0 sel kosong/unmodeled**, 24 protein zero-positive, 78 fold
  evaluable. Tidak ada baris lain yang perlu dibersihkan.
- **Stage 10.1 menyelesaikan feature engineering spasial:** tiga fitur radius 8,0 Å
  (`spatial_density_8a`, `spatial_plddt_mean_8a`, `spatial_pae_mean_8a`) ditambahkan;
  dataset **55.503 × 15**, **0 NaN**, LF murni, SHA256 `8e215340…3319`; seluruh
  166.509 nilai baru diverifikasi ulang dengan parser independen (0 mismatch).
- **Metrik Stage 10.1 (retraining penuh):** XGB median ROC 0,7786 / PR 0,0925,
  pooled ROC 0,7676 / PR 0,0759 / gain 4,41×; RF median ROC 0,7724 / PR 0,0894,
  pooled ROC 0,7568 / PR 0,0668 / gain 3,88×.
- **Stage 10.2 menyelesaikan sweep radius:** fitur radius 6/8/10/12 Å diekstrak dari
  cache AFDB yang sama dan diverifikasi independen (0 mismatch); aturan pemilihan
  ditetapkan sebelum hasil; **12 Å terpilih**. XGB median ROC 0,7437/0,7786/0,8049/
  0,8120 dan RF 0,7331/0,7724/0,7946/0,8089 untuk r6/r8/r10/r12; Friedman ROC
  p=1,49e-06 (XGB) dan p=3,32e-14 (RF); r12 vs r8 signifikan pada kedua model.
- **Stage 10.2 menyelesaikan kalibrasi OOF:** isotonic dan sigmoid di-fit per fold
  dengan inner GroupKFold 3 pada protein latih saja (`ensemble=False`). Kalibrasi
  memperbaiki skala absolut (XGB Brier 0,1820 → 0,0163; ECE 0,3569 → 0,0016; mean
  predicted 0,3741 → 0,0176 vs prevalensi 0,0172) tetapi tidak memperbaiki pooled ROC
  (0,7956 → 0,7900/0,7947) maupun within-z (0,7495 → 0,7418/0,7475), dan tidak menutup gap
  antar-protein (between-protein AUC hanya bergeser: XGB 0,7828 → 0,7889/0,7859; RF 0,7870 →
  0,7847/0,7839). Sigmoid rank-preserving; isotonic menciptakan tie dan
  memperbaiki/memperburuk ROC pada 34/43 fold XGB (C27).
- **Metrik Stage 10.2 (radius 12, tanpa kalibrasi):** XGB median ROC 0,8120 / PR
  0,1255, pooled ROC 0,7956 / PR 0,0881 / gain 5,12×; RF median ROC 0,8089 / PR
  0,1051, pooled ROC 0,7759 / PR 0,0711 / gain 4,13×; within-protein 0,7495/0,7338.
- **Dataset terkalibrasi:** `production_dataset_100_calibrated.csv` **55.503 × 21**
  (15 fitur radius 12 Å + 6 skor OOF), **0 NaN**, LF murni, 9.667.972 B, SHA256
  `2c4bcb3d…ea3a`; 15 kolom fitur string-identik dengan CSV r12 dan 6 kolom OOF cocok
  dengan npz sumber. Kolom OOF adalah artefak audit, bukan fitur latih (C28).
- **Stage 10.3 menyelesaikan tuning + pemilihan golden:** **101 konfigurasi unik**
  (XGB 44, LGBM 46, RF 8, plus 3 re-eval konfigurasi derived) dievaluasi pada 102-fold
  LOGO-CV / 78 fold evaluable dengan 16 fitur latih. Perbandingan imbalansi: bobot kelas
  besar menaikkan median PR per-protein tetapi menurunkan pooled PR/gain, between-protein
  AUC, dan kalibrasi; `scale_pos_weight=1` unggul pada pooled PR dan Brier di baseline
  pass 1, sedangkan RF justru terbaik tanpa `class_weight`.
- **Golden model Stage 10.3:** LightGBM `lgbm__032c38ffe37f` (`max_depth=6`,
  `num_leaves=31`, `learning_rate=0,05`, `subsample=0,75`, `colsample_bytree=0,9`,
  `scale_pos_weight=20`). Median ROC **0,8411** / PR **0,1693**; pooled ROC **0,8131** /
  PR **0,1142** / gain **6,63×**; within-z **0,7709**; Brier **0,0520**; ECE **0,1228**.
  XGBoost terbaik `xgb__496d370641fb`: median ROC 0,8303 / PR 0,1508, pooled 0,8156 /
  0,1156 / 6,72×, Brier 0,0209. RF terbaik `rf__7d4e21346df6`: median PR 0,1256,
  pooled PR 0,0945 / 5,49×, Brier 0,0162.
- **Nested LOGO-CV Stage 10.3:** inner `GroupKFold(5)`, kandidat dari tuning global.
  Median ROC 0,8303 / PR 0,1550; pooled ROC 0,7961 / PR 0,0784 / gain 4,55×; within-z
  0,7680; Brier 0,0340. Gap vs evaluasi global (median PR 0,1693 → 0,1550; gain 6,63× →
  4,55×) mengukur optimisme seleksi; kandidat tetap berasal dari tuning global sehingga
  nested masih optimistis.
- **Kalibrasi tidak diulang di Stage 10.3.** Brier/ECE golden (0,0520/0,1228) adalah skor
  mentah dan tidak sebanding dengan skor terkalibrasi Stage 10.2 (0,0163/0,0016). Stage
  10.2 sudah menunjukkan kalibrasi memperbaiki skala, bukan peringkat.
- **Stage 11.1 mengekspor artefak produksi:** golden LightGBM dilatih ulang pada seluruh
  55.503 baris; OOF Stage 10.3 direproduksi dengan selisih maksimum 0,0; sigmoid di-fit pada
  OOF (Brier 0,016072; ECE 0,000811; mean 0,017206 vs prevalensi 0,017206) dan dipilih
  sebelum evaluasi karena rank-preserving. Artefak
  `results/models/golden_lightgbm_12a.joblib` berukuran **157.432 B**, SHA256
  `98c86efb…45da`, dan memuat model, sigmoid + isotonic, 16 nama fitur, parameter, metadata
  dataset, metrik OOF/in-sample, feature importance, limitations, dan environment.
- **Stage 11.2 menambahkan CLI mandiri:** `src/inference_features.py` memegang kontrak 16
  fitur + parser CIF/PDB/PAE + fetch AFDB; `src/predict.py` menerima `--uniprot` atau
  `--structure` + `--pae` dan menulis CSV per-residu. Diuji pada P02144 (154 residu; CIF
  lokal, PDB lokal, AFDB, cache — output numerik identik; paritas fitur maksimum 3,55e-15,
  0 nilai > 1e-12, probabilitas identik bit) dan P00520 (1.123 residu). Error path: PAE
  hilang dan multi-chain exit 2; `--chain A` exit 0. Ambang 0,5 hanya tampilan dan memberi
  0 panggilan pada kedua protein.
- **Stage 11 tetaplah bukan validasi eksternal.** Kalibrator in-sample terhadap 102 protein
  yang sama, model final melihat seluruh label training, dan tidak ada protein baru dengan
  label independen. Artefak joblib adalah pickle dan hanya boleh dimuat dari sumber
  tepercaya (C29, C30).
- Dataset AFDB, dataset Stage 7, lock Stage 8.2, dan dataset Stage 9.x/10.1/10.2 **tidak
  diubah**; Stage 10.3/11 tidak membuat dataset baru — hanya artefak evaluasi + artefak
  model.
- Gate berikutnya: putuskan status benchmark Stage 9.3–10.3, jalankan ablasi dan
  importance-stability, lalu validasi eksternal pada protein baru; kalibrasi sudah
  diuji internal tetapi **belum** lintas-protein eksternal. Belum ada klaim generalisasi.
- **Status commit:** dokumentasi Stage 10.3 sudah di-commit dan di-push sebagai `628e178`.
  Script/dokumentasi Stage 11 masih di working tree dan **menunggu persetujuan user**;
  tidak ada commit/push Stage 11 pada sesi ini.

---

## 16. Stage 9.2 — Real AFDB Expansion (Audited 2026-10-20)

**Status: AUDITED — REAL AFDB DATA, DENGAN CATATAN DEFINISI FITUR.**

### 16.1 Artifact identity

| Field | Value |
|---|---|
| Authoritative path | `results/dataset/stage9_processed_dataset.csv` |
| Source artifact (untracked) | `download/stage9_processed_dataset.csv` |
| SHA256 | `58e55a293b66c13dd4ca4437f1d268f69fc212c93376f58488a692998255e10c` |
| Size | 363.717 bytes |
| Rows | 3.960 residue records (plus header) |
| Columns | 12 |
| Proteins | 14 |
| Positives (`target_y = 1`) | 129 (3,26%) |
| Folds | 14 LOGO folds; 13 evaluable (P01308 has 0 positives) |
| Label policy | UniProt Active site + Binding site (A+B) |
| ML features | 13 (7 structural invariants + 6 one-hot of `amino_acid_type`) |

### 16.2 Verification performed (independent)

- AFDB v6 CIF + PAE files were re-downloaded for all 14 proteins (28 files, ~9,3 MB)
  and the API metadata (`entryId`, `latestVersion`, `chainId`, `sequenceChecksum`)
  was re-queried on 2026-10-20.
- Sequence identity: 14/14 CIF sequences match the AFDB `uniprotSequence`; MD5
  `sequenceChecksum` matches 14/14; residue numbering is 1..N in all proteins.
- Structural features recomputed row-by-row from the raw CIF/PAE:
  - `plddt_ca`: 3.960/3.960 numeric match (387 rows differ only in float formatting,
    e.g. `42.5` vs `42.50`; max absolute difference 0,0).
  - `pae_mean_row`, `pae_mean_col`: 3.960/3.960 match (max difference 0,0).
  - `n_atoms`, `hydropathy_kd`, `charge_ph7`, `amino_acid`: 3.960/3.960 match.
- Labels: `target_y` matches live UniProt Active site + Binding site annotations for
  3.960/3.960 rows (0 mismatch). The 15-protein metadata file also has 0 mismatches
  (135 positives across 15 proteins; the processed file excludes P00720 with 6
  positives).
- Metrics: LOGO-CV reproduced from the CSV with the pinned environment (§16.4).
  XGBoost exact; Random Forest within ≤0,0011.

### 16.3 Deviations from the frozen Stage 3/8.2 feature definitions

| # | Finding | Evidence | Impact |
|---|---|---|---|
| D9.2-1 | `pae_local_mean_k10` is **not** the frozen definition. CSV values equal `mean(PAE[i, max(0,i-5):min(N,i+6)])` (window ±5, **including self**); the frozen definition is `\|i-j\| ≤ 10, j ≠ i`. All 3.960 values differ from the frozen definition (max 8,1 Å). | Recomputed both definitions row-by-row; observed formula matches 3.960/3.960. | Stage 9.2 metrics are internally reproducible but **not directly comparable** to Stage 8.2. |
| D9.2-2 | Histidine is classified `aromatic` (108 rows), not `basic` as in the frozen `AA_TYPE` table. | Count of `amino_acid_type` vs frozen table. | The six one-hot AA features differ for H-containing proteins. |
| D9.2-3 | The Stage 9.2 markdown says **123 positives**; the CSV contains **129** (3,26%). | `download/gemini-code-1792491213449.md` vs CSV. | Documentation error; metrics are reproducible from the CSV, so the computed values correspond to 129 positives. |
| D9.2-4 | P00720 (Endolysin) is absent from the processed dataset; AFDB returns HTTP 404 for this accession. | AFDB API query; 4.124 metadata rows − 164 P00720 rows = 3.960. | The pilot batch is 15 proteins at metadata level, 14 in the processed dataset. |

### 16.4 Reproduction of Stage 9.2 metrics

Protocol: 14-fold LOGO (13 evaluable), 13 features, XGBoost/RF configurations as in
§6.2 of the Stage 8.2 lock document; median/IQR across evaluable folds; pooled over
all 3.960 OOF predictions. Environment: numpy 2.5.4, pandas 3.0.6, scipy 1.18.1,
scikit-learn 1.9.1, xgboost 3.4.1.

| Model | Median ROC (IQR) | Median PR (IQR) | Pooled ROC | Pooled PR | PR gain (pooled) |
|---|---:|---:|---:|---:|---:|
| XGBoost | **0,7092** (0,1580) | **0,1509** (0,1260) | **0,6484** | **0,1022** | 3,14× |
| Random Forest | **0,7305** (0,1423; claimed 0,1412) | **0,1852** (0,2622) | **0,6523** (claimed 0,6524) | **0,0996** | 3,06× |

- Median gain: XGB 3,74× and RF 3,08× using the median of per-fold PR/prevalence
  ratios, matching the delivered markdown.
- XGBoost reproduces every claimed value exactly.
- RF median ROC/PR, IQR PR, and pooled PR reproduce exactly; the only differences are
  IQR ROC (0,0011) and pooled ROC (0,0001), consistent with the RF tolerance already
  recorded for Stage 8.2.

### 16.5 Status and interpretation

- **What is proven:** the structural features and A+B labels are real, traceable to
  AFDB v6 and UniProt, and the reported metrics are reproducible from the delivered
  CSV under the documented configuration.
- **What is not proven:** generalization to new proteins. The dataset has 14 proteins
  / 129 positives and no external holdout; pooled ROC-AUC ≈0,65 is not evidence of
  biological function prediction.
- **Comparability:** Stage 9.2 is a separate dataset. Because of D9.2-1 and D9.2-2,
  its metrics must not be placed in the same table as Stage 8.2 without a clear
  footnote. Stage 8.2 remains the frozen benchmark.
- **Not locked:** no SHA256-bearing lock document analogous to
  `BENCHMARK_DATASET_LOCK.md` has been created for Stage 9.2. Stage 9.2 remains a
  historical artifact; see §17 for the realigned Stage 9.3.

### 16.6 Audit provenance

The audit used temporary local scripts and downloaded AFDB files outside the tracked
tree; these are **not committed**. Only the audited CSV is promoted to
`results/dataset/`. The reproducible evidence is the SHA256 above plus the definitions
and comparisons recorded in this section.

---

## 17. Stage 9.3 — Realigned Real-AFDB Expansion (Audited 2026-10-20)

**Status: AUDITED — DEFINISI FITUR FROZEN; BUKAN PENGGANTI BENCHMARK STAGE 8.2.**

### 17.1 Artifact identity

| Field | Value |
|---|---|
| Authoritative path | `results/dataset/stage93_realigned_dataset.csv` |
| Source artifact (untracked) | `download/stage93_realigned_dataset.csv` |
| SHA256 | `6f0357858638c57630e0276fb8e46339a16f001e54005dba34adb5b5e3f37f5a` |
| Size | 319.050 bytes |
| Rows | 3.960 residue records (plus header) |
| Columns | 12 (`target_y` di kolom terakhir; urutan berbeda dari Stage 9.2) |
| Proteins | 14 (sama dengan Stage 9.2) |
| Positives (`target_y = 1`) | 129 (3,26%) |
| Folds | 14 LOGO folds; 13 evaluable (P01308 nol positif) |
| Label policy | UniProt Active site + Binding site (A+B) |
| ML features | 13 (7 struktural + 6 one-hot dari `amino_acid_type`) |

### 17.2 Verification performed (independent)

- 28 file AFDB v6 CIF/PAE diunduh ulang dari nol pada 2026-10-20, bersama respons
  API dan UniProt JSON; tidak memakai file audit Stage 9.2.
- Identitas: sekuens CIF = `uniprotSequence` 14/14, MD5 `sequenceChecksum` cocok
  14/14, UniProt = AFDB 14/14, penomoran 1..N, bentuk PAE = (N, N), jumlah baris CSV
  = jumlah residu CIF. Tidak ada error identitas.
- Fitur per baris: `amino_acid`, `amino_acid_type` (H = `basic`), `hydropathy_kd`,
  `charge_ph7`, `n_atoms`, `plddt_ca`, `pae_mean_row`, `pae_mean_col`, dan
  `pae_local_mean_k10` dengan definisi frozen `|i-j| ≤ 10, j ≠ i` — **0 mismatch dari
  3.960 baris** (selisih maksimum 0,0 untuk seluruh kolom).
- Definisi ±5 termasuk-self (yang dipakai Stage 9.2) sengaja diuji sebagai pembanding:
  seluruh 3.960 nilai **tidak** cocok dengannya (selisih maks 8,1 Å), sehingga kolom
  ini benar-benar dihitung ulang, bukan disalin.
- Label: `target_y` cocok dengan anotasi UniProt A+B live untuk 3.960/3.960 baris
  (0 mismatch).
- Diff terhadap Stage 9.2: **hanya** `pae_local_mean_k10` (3.960 baris) dan
  `amino_acid_type` (108 residu H); `target_y` dan seluruh fitur lain identik.
  Ini konsisten dengan realignment yang dimaksud dan tidak ada perubahan tak terjelaskan.

### 17.3 Reproduction of Stage 9.3 metrics

Protokol: 14-fold LOGO (13 evaluable), 13 fitur, konfigurasi XGBoost/RF yang sama
dengan Stage 8.2/9.2; median/IQR across evaluable folds; pooled dari 3.960 OOF.
Environment: numpy 2.5.4, pandas 3.0.6, scipy 1.18.1, scikit-learn 1.9.1,
xgboost 3.4.1.

| Model | Median ROC (IQR) | Median PR (IQR) | Median gain | Pooled ROC | Pooled PR (gain) |
|---|---:|---:|---:|---:|---:|
| XGBoost | **0,7264** (0,0974; klaim 0,0975) | **0,1684** (0,1796; klaim 0,1348) | **2,60×** | **0,6411** | **0,0858** (2,63×) |
| Random Forest | **0,7518** (0,1531; klaim 0,1524) | **0,1763** (0,2461; klaim 0,2259) | **2,39×** | **0,6575** (klaim 0,6577) | **0,0912** (2,80×; klaim 0,0913) |

- XGBoost: median ROC/PR, pooled ROC/PR, dan gain reproduce persis (perbedaan hanya
  pembulatan IQR ROC 0,0001).
- Random Forest: median ROC/PR dan gain reproduce; pooled ROC berbeda 0,0002 dan
  pooled PR 0,0001 — dalam toleransi RF yang sudah tercatat (C15).
- **IQR PR tidak reproduce** untuk kedua model; lihat §17.4.

### 17.4 Discrepancy — IQR PR

Ringkasan yang diserahkan mencantumkan IQR PR XGB 0,1348 dan RF 0,2259. Perhitungan
ulang dari 13 nilai PR per-fold menghasilkan **0,1796** (XGB) dan **0,2461** (RF).
Semua metode kuantil yang diuji (linear, lower, higher, midpoint, nearest, serta
median-split) menghasilkan nilai yang sama atau lebih jauh; tidak ada yang mendekati
0,1348/0,2259. Median, pooled, dan gain cocok, sehingga discrepancy ini terbatas pada
statistik IQR dan tidak memengaruhi klaim utama. Docs memakai nilai reproduced;
nilai klaim dicantumkan sebagai pembanding (C20).

### 17.5 Status and interpretation

- **What is proven:** dataset Stage 9.3 memakai definisi fitur frozen Stage 3/8.2,
  seluruh fitur struktural dan labelnya cocok dengan AFDB/UniProt, dan
  median/pooled/gain LOGO-CV dapat direproduksi dari CSV.
- **What is not proven:** generalisasi. Stage 9.3 memakai 14 protein yang sama dengan
  Stage 9.2; realignment hanya mengubah dua definisi fitur, bukan menambah data atau
  protein baru. Pooled ROC-AUC ≈0,64–0,66 bukan bukti prediksi fungsi pada protein
  di luar dataset.
- **Comparability:** definisi fitur sekarang sebanding dengan Stage 3/8.2, tetapi
  komposisi protein dan ukuran dataset berbeda (14 protein / 3.960 residu vs 7 /
  1.098). Metrik tidak boleh disatukan dengan tabel Stage 8.2 tanpa footnote.
- **Bukan pengganti benchmark:** `stage7_processed_dataset.csv` dan
  `BENCHMARK_DATASET_LOCK.md` tidak diubah. Stage 9.3 adalah artefak baru yang
  dikunci byte-nya lewat SHA256, bukan benchmark resmi baru.

### 17.6 Audit provenance

Audit memakai script dan unduhan AFDB di direktori temporer di luar tracked tree;
tidak ada yang di-commit. Bukti yang reproducible adalah SHA256 di atas, definisi
frozen, dan tabel perbandingan di §17.2–§17.4.

---

## 18. Stage 9.4 — Full Production Scaling, 103 Protein (Audited 2026-10-20)

**Status: AUDITED — 103 PROTEIN / 59.188 RESIDU; XGB REPRODUCE PERSIS, RF SEBAGIAN;
P11532 BELUM VALID SECARA STRUKTURAL; BUKAN BUKTI GENERALISASI.**

### 18.1 Artifact identity

| Field | Value |
|---|---|
| Authoritative path | `results/dataset/production_dataset_100_realigned.csv` |
| Source artifact (untracked) | `download/production_dataset_100_realigned.csv` |
| SHA256 | `8be323f64d1b5f8dbcfff743d378392bafc72e944f051cac5c835f6f54b1bde1` |
| Size | 4.619.447 bytes |
| Rows | 59.188 residue records (plus header) |
| Columns | 12 (`uniprot_id`, `sequence_position`, `amino_acid`, `amino_acid_type`, `hydropathy_kd`, `charge_ph7`, `n_atoms`, `plddt_ca`, `pae_mean_row`, `pae_mean_col`, `pae_local_mean_k10`, `target_y`) |
| Proteins | 103 |
| Positives (`target_y = 1`) | 959 (1,6203%) |
| Zero-positive proteins | 24; 79 protein yang evaluable |
| Folds | 103 LOGO folds; 79 evaluable |
| Label policy | UniProt Active site + Binding site (A+B) |
| ML features | 13 (7 struktural + 6 one-hot dari `amino_acid_type`) |
| Line endings | **LF** — 0 CR, 59.189 LF, final newline, tanpa BOM; sesuai `.gitattributes` (`text eol=lf`) |

### 18.2 Verification performed (independent)

- Audit mengunduh ulang **206 file AFDB v6 CIF/PAE** (103 protein, ~175 MB), 103
  respons `/api/prediction/<acc>`, dan 103 respons UniProtKB JSON pada 2026-10-20.
- **Fitur turunan sekuens dan label:** `amino_acid`, `amino_acid_type` (H = `basic`),
  `hydropathy_kd`, `charge_ph7`, dan `target_y` cocok **59.188/59.188** baris dengan
  sekuens dan anotasi A+B UniProt kanonik — 0 mismatch.
- **Fitur struktural:** `n_atoms`, `plddt_ca`, `pae_mean_row`, `pae_mean_col`, dan
  `pae_local_mean_k10` (definisi frozen `|i-j| ≤ 10, j ≠ i`) cocok persis untuk
  **56.028/56.028** baris yang dimodelkan; selisih absolut maksimum **0,0**.
- **Baris tanpa struktur:** 3.160 baris (P11532 posisi 526–3685) memiliki
  `n_atoms = 0` dan empat kolom struktural kosong — persis jumlah yang diharapkan
  dari cakupan entri AFDB yang dipakai. Tidak ada baris malformed.
- **102/103 protein bersih penuh** (fitur sekuens, struktur, dan label). Satu-satunya
  protein bermasalah adalah P11532 (§18.3).
- Traceability checksum: sekuens CIF = `uniprotSequence` untuk 102 protein kanonik;
  MD5 `sequenceChecksum` cocok; penomoran 1..N; bentuk PAE = (N, N); jumlah baris CSV
  = panjang sekuens UniProt.

### 18.3 Critical finding — P11532 tidak selaras dengan sekuens kanonik

- Endpoint `/api/prediction/P11532` mengembalikan **14 entri isoform** dan **tidak**
  mengembalikan entri kanonik penuh 3.685 aa (DMD/dystrophin melebihi batas panjang
  entri AFDB yang tersedia). Dataset memakai entri **pertama**:
  `AF-P11532-9-F1`, panjang **525 aa**.
- Sekuens CIF entri tersebut berbeda dari sekuens kanonik P11532 pada **496 dari 525
  posisi**. Artinya 525 baris P11532 yang “dimodelkan” memasangkan fitur sekuens dan
  label dari residu kanonik dengan fitur struktural dari residu isoform yang berbeda
  pada posisi baris yang sama — **tidak selaras**.
- 3.160 baris P11532 lainnya tidak memiliki data struktural sama sekali. **Seluruh 4
  positif P11532 (posisi 3313, 3316, 3337, 3340) berada di daerah tanpa struktur.**
- Dampak: P11532 menyumbang 3.685 baris (6,2% dataset) tetapi **0 baris positif yang
  memiliki fitur struktural**. Pada XGBoost, 3.160 baris tersebut masuk sebagai NaN
  native; pada Random Forest, nilainya harus diimputasi atau dibuang.
- **Rekomendasi:** keluarkan P11532 dari benchmark Stage 9.4, atau rebuild dengan
  alignment sekuens ke sumber full-length yang benar. Jangan memperlakukan 525 baris
  strukturalnya sebagai representasi residu kanonik. Rekomendasi ini **dieksekusi di
  Stage 9.5** melalui exclusion (§19). Metrik di §18.4 masih memuat P11532 karena itu
  adalah isi artefak yang diserahkan; sebagai sensitivitas, menghapus baris OOF P11532
  menurunkan pooled ROC XGB dari 0,7575 ke **0,7451** (55.503 baris, 955 positif).

### 18.4 Reproduction of Stage 9.4 metrics

Protokol: 103-fold LOGO (79 evaluable), 13 fitur, konfigurasi XGBoost/RF yang sama
dengan Stage 8.2/9.2/9.3; median/IQR across evaluable folds; pooled dari 59.188 OOF.
Environment: numpy 2.5.4, pandas 3.0.6, scipy 1.18.1, scikit-learn 1.9.1,
xgboost 3.4.1.

| Model | Median ROC (IQR) | Median PR (IQR) | Median gain | Pooled ROC | Pooled PR (gain) |
|---|---:|---:|---:|---:|---:|
| XGBoost | **0,7359** (0,2299) | **0,0656** (0,1025) | **2,27×** | **0,7575** | **0,0606** (3,74×) |
| Random Forest | **0,7339** (0,2029) | **0,0762** (0,1430) | **2,50×** | **0,7471** | **0,0573** (3,53×) |

Perbandingan klaim vs reproduced:

| Model | Metric | Klaim | Reproduced | Status |
|---|---|---:|---:|---|
| XGBoost | Pooled ROC-AUC | 0,7575 | **0,7575** | exact |
| XGBoost | Pooled PR-AUC | 0,0606 | **0,0606** | exact |
| XGBoost | Pooled gain | 3,74× | **3,7384×** | exact |
| XGBoost | Median ROC (79 fold) | 0,7359 | **0,7359** | exact |
| Random Forest | Pooled ROC-AUC | 0,7471 | **0,7471** | exact |
| Random Forest | Pooled PR-AUC | 0,0592 | **0,0573** | **tidak reproduce** (−0,0019) |
| Random Forest | Pooled gain | 3,65× | **3,5343×** | **tidak reproduce** |
| Random Forest | Median ROC (79 fold) | 0,7397 | **0,7339** | **tidak reproduce** (−0,0058) |

- **XGBoost exact** untuk semua nilai yang diklaim. Pooled ROC 0,7575, pooled PR
  0,0606, dan gain 3,7384× dihitung ulang dari OOF; median ROC 0,7359.
- **Random Forest** memakai konfigurasi default (`n_estimators=100`, `max_depth=4`,
  `class_weight='balanced_subsample'`, `max_features='sqrt'`, `random_state=42`) dan
  imputasi mean global untuk empat kolom struktural yang kosong. Konfigurasi inilah
  yang menghasilkan pooled ROC **0,7471** persis. Imputasi mean per-fold menghasilkan
  0,7470; median ROC tetap 0,7339.
- Konfigurasi RF alternatif yang diuji (seed 0/2024, depth 5, `n_estimators=200`,
  `class_weight='balanced'`/`None`, imputasi median/fill-0/drop, `max_features=None`)
  menghasilkan median ROC 0,7160–0,7479 dan pooled ROC 0,7356–0,7513. **Tidak ada
  konfigurasi yang menghasilkan median ROC 0,7397 persis**; konfigurasi yang
  mencocokkan pooled ROC 0,7471 menghasilkan median 0,7339. Median ROC 0,7397
  karenanya tidak dapat dikonfirmasi; docs memakai nilai reproduced 0,7339 (C22).

### 18.5 Interpretation — kenaikan pooled ROC bukan bukti generalisasi

Angka yang diminta untuk dicatat memang benar sebagai deskripsi OOF pada dataset ini:
pooled ROC XGBoost naik dari **0,5368** (Stage 8.2, 7 protein) ke **0,7575** (Stage
9.4, 103 protein), selisih +0,2207. Namun audit ini **tidak** dapat menerimanya
sebagai bukti tunggal bahwa strategi pembesaran data berhasil meningkatkan
generalisasi, karena:

1. **Bukan perbandingan apple-to-apple.** Stage 8.2 memakai 7 protein / 1.098 residu
   / 46 positif (prevalensi 4,19%) dengan 6 fold evaluable; Stage 9.4 memakai 103
   protein / 59.188 residu / 959 positif (prevalensi 1,62%) dengan 79 fold evaluable.
   Komposisi protein, prevalensi, dan jumlah fold berbeda.
2. **Pooled ROC dipengaruhi perbedaan antar-protein.** Diagnosis pada OOF XGBoost:
   - pooled ROC mentah: **0,7575**
   - tanpa baris P11532: **0,7451**
   - tanpa protein zero-positive: **0,7364**
   - within-protein z-scored pooled ROC: **0,6876**
   - within-protein rank-normalized pooled ROC: **0,6847**
   - between-protein AUC (prevalensi di atas median vs mean score): **0,7922**
   - Spearman antara mean score protein dan prevalensi: **0,5223** (Pearson 0,4584)

   Pola ini menunjukkan sebagian dari pooled ROC berasal dari kemampuan model
   mengurutkan **protein** berdasarkan prevalensi, bukan dari diskriminasi residu
   **di dalam** protein. Pooled ROC bukan ukuran generalisasi per-protein.
3. **Median per-protein hanya naik tipis.** Median ROC XGB Stage 8.2 → 9.4:
   **0,7185 → 0,7359** (+0,0174), dengan IQR 0,2299 dan rentang per-protein
   0,4133–0,9800. Tidak ada lompatan besar pada level protein.
4. **PR absolut justru turun.** Pooled PR XGB Stage 8.2 0,0916 → Stage 9.4 0,0606;
   median PR 0,2144 → 0,0656. “Gain 3,74×” naik terutama karena prevalensi turun
   dari 4,19% ke 1,62% (baseline acak 1/0,0419 = 23,9× vs 1/0,016203 = 61,7×),
   bukan karena precision absolut membaik.

**Kesimpulan:** Stage 9.4 adalah milestone **data engineering dan reproducibility**
(103 protein, 59.188 residu, XGB exact), bukan bukti generalisasi biologis. Kenaikan
pooled ROC dicatat sebagai angka, tetapi tidak boleh dipakai sebagai satu-satunya
bukti keberhasilan scaling. Validasi eksternal dan metrik per-protein tetap wajib.
Setelah P11532 dikeluarkan di Stage 9.5, pooled ROC XGB turun ke 0,7476 sementara
within-protein z-scored ROC tetap 0,6877 — lihat §19.4.

### 18.6 Status and interpretation

- **What is proven:** dataset identity dan LF; fitur turunan sekuens serta label
  cocok 100% dengan UniProt; fitur struktural 56.028 baris cocok persis dengan AFDB;
  XGBoost LOGO-CV reproduce persis; RF pooled ROC reproduce persis.
- **What is not proven:** generalisasi ke protein baru; validitas struktural P11532;
  median ROC dan pooled PR RF; klaim bahwa kenaikan pooled ROC disebabkan oleh
  scaling.
- **Bukan benchmark terkunci:** `stage7_processed_dataset.csv` dan
  `BENCHMARK_DATASET_LOCK.md` tidak diubah. Stage 9.4 adalah artefak baru dengan
  SHA256, bukan benchmark resmi baru.

### 18.7 Audit provenance

Audit memakai script dan unduhan AFDB/UniProt di direktori temporer di luar tracked
tree; tidak ada yang di-commit. Bukti yang reproducible adalah SHA256 di atas,
definisi fitur frozen, dan tabel perbandingan di §18.2–§18.5.

---

## 19. Stage 9.5 — Dataset Cleansing & Isoform Resolution, 102 Protein (Audited 2026-10-20)

**Status: AUDITED — DATASET BERSIH 102 PROTEIN / 55.503 RESIDU; P11532 DIKELUARKAN;
0 SEL KOSONG; METRIK LOGO-CV DIHITUNG ULANG; BUKAN BUKTI GENERALISASI.**

### 19.1 Artifact identity

| Field | Value |
|---|---|
| Authoritative path | `results/dataset/production_dataset_100_cleaned.csv` |
| Derived from | `results/dataset/production_dataset_100_realigned.csv` (Stage 9.4) |
| SHA256 | `e47b3635a7e904107094afde02a1ece656e25491c8721865501b6a76562b05a3` |
| Size | 4.457.124 bytes |
| Rows | 55.503 residue records (plus header) |
| Columns | 12 (schema identik Stage 9.4) |
| Proteins | 102 |
| Positives (`target_y = 1`) | 955 (1,7206%) |
| Negative:positive | 54.548 : 955 = 57,1183 : 1 (1 : 57,1) |
| Zero-positive proteins | 24; 78 protein evaluable |
| Folds | 102 LOGO folds; 78 evaluable |
| Excluded protein | P11532 — 3.685 baris, 4 positif (§18.3) |
| Missing/unmodeled rows | **0** — tidak ada sel kosong, `n_atoms = 0`, atau NaN |
| Line endings | **LF** — 0 CR, 55.504 LF, final newline, tanpa BOM; sesuai `.gitattributes` |

### 19.2 Verification performed

- **Derivasi eksak:** output dibandingkan baris-per-baris dengan sumber; hasilnya persis
  header Stage 9.4 + seluruh baris dengan `uniprot_id != P11532`, dalam urutan yang sama
  (55.503 baris). Tidak ada baris P11532 yang tersisa.
- **Kelengkapan:** 0 sel kosong di seluruh 12 kolom; 0 nilai non-numerik pada kolom
  numerik; 0 baris `n_atoms = 0`; 0 baris dengan `plddt_ca`/`pae_*` kosong.
- **Struktur per protein:** 0 protein dengan posisi duplikat; 0 protein dengan gap
  penomoran; setiap protein memiliki posisi 1..N yang lengkap.
- **Provenance:** Stage 9.4 sudah diaudit terhadap 206 file AFDB CIF/PAE + UniProt
  (59.188/59.188 fitur sekuens & label; 56.028/56.028 baris struktural). Karena Stage
  9.5 hanya memfilter baris dan tidak mengubah nilai, audit tersebut berlaku untuk
  seluruh baris yang dipertahankan; tidak ada unduhan ulang.
- **Klasifikasi:** 24 protein zero-positive tetap sama; jumlah fold evaluable turun dari
  79 menjadi 78 karena P11532 memiliki 4 positif.

### 19.3 Reproduction of Stage 9.5 metrics

Protokol: 102-fold LOGO (78 evaluable), 13 fitur, konfigurasi XGBoost/RF identik
Stage 8.2/9.2/9.3/9.4; model **di-retrain penuh** pada 102 protein (bukan hanya
membuang baris P11532 dari OOF Stage 9.4). Environment: numpy 2.5.4, pandas 3.0.6,
scipy 1.18.1, scikit-learn 1.9.1, xgboost 3.4.1.

| Model | Median ROC (IQR) | Median PR (IQR) | Median gain | Pooled ROC | Pooled PR (gain) |
|---|---:|---:|---:|---:|---:|
| XGBoost | **0,7371** (0,2300) | **0,0673** (0,1070) | **2,28×** | **0,7476** | **0,0640** (3,72×) |
| Random Forest | **0,7330** (0,2096) | **0,0731** (0,1250) | **2,70×** | **0,7476** | **0,0608** (3,53×) |

Catatan: pooled ROC XGB = 0,74762515 dan RF = 0,74763638; keduanya dibulatkan menjadi
0,7476 pada empat desimal.

Perbandingan dengan Stage 9.4 (semua 103 protein) dan dengan OOF Stage 9.4 yang
dievaluasi hanya pada 102 protein yang sama (model masih dilatih dengan P11532):

| Metric | 9.4 semua 103 | 9.4 eval 102* | 9.5 retrain 102 | Δ 9.5 vs 9.4 semua |
|---|---:|---:|---:|---:|
| XGB median ROC | 0,7359 | 0,7399 | 0,7371 | +0,0012 |
| XGB median PR | 0,0656 | 0,0667 | 0,0673 | +0,0017 |
| XGB pooled ROC | 0,7575 | 0,7451 | 0,7476 | −0,0099 |
| XGB pooled PR | 0,0606 | 0,0608 | 0,0640 | +0,0034 |
| XGB pooled gain | 3,7384× | 3,5330× | 3,7174× | −0,0210 |
| RF median ROC | 0,7339 | 0,7344 | 0,7330 | −0,0009 |
| RF median PR | 0,0762 | 0,0766 | 0,0731 | −0,0031 |
| RF pooled ROC | 0,7471 | 0,7470 | 0,7476 | +0,0005 |
| RF pooled PR | 0,0573 | 0,0582 | 0,0608 | +0,0035 |
| RF pooled gain | 3,5343× | 3,3823× | 3,5331× | −0,0012 |

\* Evaluasi pada 102 protein non-P11532 memakai OOF Stage 9.4; model masih melihat
P11532 saat training. Kolom ini memisahkan efek "menghapus baris evaluasi" dari efek
"retraining tanpa P11532".

- **Efek menghapus baris evaluasi (XGB):** pooled ROC 0,7575 → 0,7451. Ini menunjukkan
  baris P11532 (3.160 baris tanpa struktur + 525 baris isoform) menaikkan pooled ROC
  Stage 9.4.
- **Efek retraining (XGB):** pooled ROC 0,7451 → 0,7476; pooled PR 0,0608 → 0,0640.
  Jadi retraining tanpa P11532 tidak merusak model; justru sedikit membaik.
- **Random Forest** hampir tidak berubah: pooled ROC 0,7471 → 0,7476, pooled PR
  0,0573 → 0,0608. Model RF memakai imputasi mean untuk baris kosong, sehingga baris
  P11532 tidak memberi sinyal ekstrem seperti pada XGBoost (NaN native).
- **Pairing per fold** (78 protein evaluable yang sama, 9.5 vs OOF 9.4): XGB median
  ΔROC +0,0030 (44 naik / 33 turun / 1 seri), median ΔPR +0,0017; RF median ΔROC
  +0,0025 (44 naik / 32 turun / 2 seri), median ΔPR +0,0002.

### 19.4 Interpretation — pembersihan memperbaiki validitas, bukan generalisasi

1. **Tidak ada sel kosong tersisa.** Dataset Stage 9.5 adalah dataset produksi pertama
   yang seluruh 55.503 barisnya memiliki fitur struktural lengkap. Ini menghilangkan
   masalah imputasi/drop yang membedakan XGBoost dan RF di Stage 9.4.
2. **Pooled ROC turun karena artefak hilang, bukan karena model memburuk.** Penurunan
   XGB −0,0099 seluruhnya berasal dari penghapusan baris P11532 dari evaluasi; setelah
   retraining, pooled ROC justru 0,7476 vs 0,7451 pada evaluasi subset. Within-protein
   z-scored ROC tetap 0,6877 (XGB) / 0,6891 (RF), praktis tidak berubah dari Stage 9.4
   (0,6876 XGB).
3. **Median per-protein nyaris tidak berubah.** XGB median ROC +0,0012 dan median PR
   +0,0017 vs Stage 9.4; RF median ROC −0,0009 dan median PR −0,0031. Tidak ada
   lompatan performa dari pembersihan.
4. **Pooled PR membaik, tetapi absolutnya masih rendah.** XGB pooled PR 0,0606 → 0,0640
   (+0,0034); RF 0,0573 → 0,0608 (+0,0035). Gain XGB 3,72× dan RF 3,53× masih terhadap
   prevalensi rendah 1,72%.
5. **Inflasi antar-protein tetap ada.** Between-protein AUC 0,7851 (XGB) / 0,7824 (RF);
   Spearman skor rata-rata vs prevalensi 0,5142 / 0,5105; within-protein z-scored ROC
   0,6877 / 0,6891 jauh di bawah pooled 0,7476. Pooled ROC Stage 9.5 tetap **bukan**
   ukuran generalisasi per-protein.
6. **Imbalance sedikit membaik tetapi tetap ekstrem.** 54.548 negatif : 955 positif =
   57,1 : 1 (Stage 9.4: 60,7 : 1); prevalensi 1,7206%.

**Kesimpulan:** Stage 9.5 berhasil menghilangkan artefak isoform dan missingness P11532;
dataset kini lengkap dan lebih valid. Namun pembersihan **tidak** meningkatkan
diskriminasi biologis secara material: median per-protein hampir tetap, within-protein
ROC tetap ~0,69, dan pooled ROC justru turun karena artefak yang menginflasinya hilang.
Stage 9.5 tetap merupakan milestone data engineering, bukan bukti generalisasi.

### 19.5 Status and interpretation

- **What is proven:** identitas dan LF dataset bersih; derivasi eksak dari Stage 9.4;
  kelengkapan 55.503/55.503 baris; metrik LOGO-CV dihitung ulang dari CSV bersih dengan
  konfigurasi frozen; tidak ada baris lain yang perlu dibersihkan.
- **What is not proven:** generalisasi ke protein baru; representativitas 102 protein;
  bahwa pooled ROC 0,7476 berasal dari sinyal biologis dan bukan urutan antar-protein;
  kalibrasi probabilitas lintas-protein.
- **Bukan benchmark terkunci:** Stage 8.2 dan `BENCHMARK_DATASET_LOCK.md` tidak diubah.
  Stage 9.5 adalah artefak baru dengan SHA256; statusnya sebagai benchmark masih perlu
  keputusan terpisah.
- **P11532:** diselesaikan dengan exclusion, bukan rebuild. Tidak ada entri AFDB
  full-length kanonik; rebuild memerlukan sumber struktur full-length eksternal dan
  harus menjadi artefak baru.

### 19.6 Audit provenance

Script cleansing, verifikasi, dan LOGO-CV dijalankan di direktori temporer di luar
tracked tree dan tidak di-commit. Bukti yang reproducible adalah SHA256 dataset,
perbandingan baris-per-baris terhadap sumber Stage 9.4, dan tabel metrik di §19.3.

---

## 20. Stage 10.1 — Spatial Neighborhood Feature Engineering, 102 Protein (Audited 2026-10-20)

**Status: AUDITED — 3 FITUR SPASIAL RADIUS 8,0 Å DITAMBAHKAN; DATASET 55.503 × 15;
166.509 NILAI BARU DIVERIFIKASI ULANG; LOGO-CV 16 FITUR DIHITUNG; BUKAN VALIDASI
EKSTERNAL DAN BUKAN BUKTI GENERALISASI.**

### 20.1 Artifact identity

| Field | Value |
|---|---|
| Authoritative path | `results/dataset/production_dataset_100_spatial.csv` |
| Derived from | `results/dataset/production_dataset_100_cleaned.csv` (Stage 9.5) |
| SHA256 | `8e21534055132c8cf4eb823e1abda224a15776b437b94bbc851f1ea4a99a3319` |
| Size | 5.313.161 bytes |
| Rows | 55.503 residue records (plus header) |
| Columns | **15** — 12 kolom Stage 9.5 tanpa perubahan + 3 kolom spasial baru |
| Proteins | 102 |
| Positives (`target_y = 1`) | 955 (1,7206%) — identik dengan Stage 9.5 |
| New columns | `spatial_density_8a`, `spatial_plddt_mean_8a`, `spatial_pae_mean_8a` |
| Missing values in new columns | **0** (0 sel kosong/NaN pada ketiga kolom) |
| `spatial_density_8a` | min 2, max 21, mean 8,8064; 0 residu tanpa tetangga |
| Line endings | **LF** — 0 CRLF, 0 lone CR, 55.504 LF, final newline, tanpa BOM |

### 20.2 Feature definitions (fixed for this stage)

Untuk setiap protein dengan N residu dan koordinat Cα `CA_i`:

```
Neighbours(i) = { j != i : ||CA_i - CA_j||_2 <= 8.0 Å }     (self excluded)
```

| Feature | Definition |
|---|---|
| `spatial_density_8a` | `\|Neighbours(i)\|` — jumlah residu lain dalam radius 8,0 Å (integer) |
| `spatial_plddt_mean_8a` | rata-rata `pLDDT_CA(j)` untuk `j ∈ Neighbours(i)`; dibulatkan 3 desimal |
| `spatial_pae_mean_8a` | rata-rata `PAE[i, j]` untuk `j ∈ Neighbours(i)` — **baris i (directed)**, bukan simetris; dibulatkan 3 desimal |

Catatan definisi:

- Radius 8,0 Å diukur Euclidean antar-Cα, bukan jarak sekuens; tetangga bisa berasal
  dari segmen/domain yang berjauhan dalam sekuens.
- Diri sendiri selalu dikeluarkan dari `Neighbours(i)`, termasuk dari rata-rata pLDDT
  dan PAE.
- `spatial_pae_mean_8a` memakai `PAE[i, j]` (arah baris i → kolom j), konsisten dengan
  `pae_mean_row`; tidak disimetriskan.
- Tidak ada imputasi: seluruh 102 protein harus lolos verifikasi input sebelum fitur
  ditulis; kegagalan satu protein membatalkan seluruh output.
- Ketiga fitur ini **tidak** menggantikan `plddt_ca`, `pae_mean_row`, `pae_mean_col`,
  atau `pae_local_mean_k10`; keduanya dipertahankan sehingga model menerima 13 fitur
  frozen + 3 fitur spasial = **16 fitur**.

### 20.3 Input provenance & verification

**Provenance penting:** permintaan Stage 10.1 menyebut file PDB/PAE di `download/`,
tetapi `download/` **tidak berisi file struktur** (hanya 6 CSV, 4 Markdown, dan 1
notebook; lihat D12). Ekstraksi memakai cache audit Stage 9.4 di luar tracked tree:

- `C:\Users\walet\AppData\Local\Temp\stage94_audit\data\afdb_files` — 102 CIF
  `AF-{acc}-F1-model_v6.cif` + 102 PAE `AF-{acc}-F1-predicted_aligned_error_v6.json`.
- `C:\Users\walet\AppData\Local\Temp\stage94_audit\data\afdb_api` — 102 respons API
  AFDB untuk verifikasi sekuens kanonik dan checksum.
- **Tidak ada unduhan baru** pada Stage 10.1; file yang dipakai adalah file yang sama
  dengan audit Stage 9.4/9.5.

Verifikasi yang dilakukan sebelum fitur dihitung (per protein):

- Entri AFDB harus kanonik `AF-{acc}-F1` (bukan isoform), sekuens CSV harus identik
  dengan `uniprotSequence`, dan MD5 sekuens harus sama dengan `sequenceChecksum`.
- Satu model, satu chain, tanpa HETATM; penomoran residu 1..N; sekuens CIF identik
  dengan sekuens CSV.
- Shape PAE harus `(N, N)`.
- Setiap baris harus cocok dengan CIF/PAE: `n_atoms`, `plddt_ca`, `pae_mean_row`,
  `pae_mean_col`, dan `pae_local_mean_k10` (toleransi 1e-9). Tidak ada baris yang
  diizinkan berbeda.

Hasil: **102/102 protein lolos**, 55.503/55.503 baris cocok. Verifikasi independen
kedua memakai parser CIF teks-biasa (tanpa Bio.PDB) dan loop tetangga naif
per-residu:

- 102/102 protein, 55.503 baris, 15 kolom, header persis.
- Seluruh **166.509 nilai baru** (55.503 × 3) direproduksi dengan **0 mismatch**;
  selisih maksimum `plddt_ca` = 0, `spatial_plddt_mean_8a` = 0,
  `spatial_pae_mean_8a` = 0.
- Kolom lama dibandingkan string-per-string dengan CSV Stage 9.5: identik, urutan baris
  sama.

### 20.4 Distribution & collinearity

| Statistic | `spatial_density_8a` | `spatial_plddt_mean_8a` | `spatial_pae_mean_8a` |
|---|---:|---:|---:|
| Min | 2 | 21,890 | 1,000 |
| Q25 | 6 | — | — |
| Median | 9 | — | — |
| Q75 | 11 | — | — |
| Max | 21 | 98,973 | 21,714 |
| Mean | 8,8064 | 81,771 | 1,806 |

Korelasi tingkat baris (Pearson / Spearman):

| Pair | Pearson | Spearman |
|---|---:|---:|
| `spatial_plddt_mean_8a` vs `plddt_ca` | 0,9885 | 0,9838 |
| `spatial_pae_mean_8a` vs `pae_local_mean_k10` | 0,6451 | 0,8800 |
| `spatial_plddt_mean_8a` vs `spatial_pae_mean_8a` | −0,5296 | −0,8537 |
| `spatial_density_8a` vs `plddt_ca` | 0,6568 | 0,6006 |
| `spatial_density_8a` vs `spatial_pae_mean_8a` | −0,2540 | −0,4308 |

**Interpretasi kolinearitas:** `spatial_plddt_mean_8a` sangat berkorelasi dengan
`plddt_ca` (0,9885), sehingga sebagian sinyalnya redundant; `spatial_pae_mean_8a`
berkorelasi tinggi secara rank dengan `pae_local_mean_k10` (0,8800) tetapi hanya
sedang secara linear (0,6451). Kontribusi unik fitur spasial harus dibaca dari
perbandingan model dan importance, bukan dari korelasi ini saja (C25).

### 20.5 Reproduction of Stage 10.1 metrics

Protokol: 102-fold LOGO (78 evaluable), **16 fitur** (13 frozen + 3 spasial),
konfigurasi XGBoost/RF identik Stage 8.2/9.2/9.3/9.4/9.5; model di-retrain penuh.
Environment: numpy 2.5.4, pandas 3.0.6, scipy 1.18.1, scikit-learn 1.9.1,
xgboost 3.4.1.

| Model | Median ROC (IQR) | Median PR (IQR) | Median gain | Pooled ROC | Pooled PR (gain) |
|---|---:|---:|---:|---:|---:|
| XGBoost | **0,7786** (0,1987) | **0,0925** (0,1155) | **3,93×** | **0,7676** | **0,0759** (4,41×) |
| Random Forest | **0,7724** (0,2138) | **0,0894** (0,1752) | **3,19×** | **0,7568** | **0,0668** (3,88×) |

Nilai eksak: XGB median ROC 0,7786497337 / PR 0,0924593292; pooled ROC 0,7676193444 /
PR 0,0758605902. RF median ROC 0,7723624097 / PR 0,0893675842; pooled ROC 0,7567553357
/ PR 0,0668017447.

Perbandingan langsung dengan Stage 9.5 (dataset dan folds yang sama, hanya fitur
berbeda):

| Metric | Stage 9.5 | Stage 10.1 | Δ |
|---|---:|---:|---:|
| XGB median ROC | 0,7371 | **0,7786** | **+0,0415** |
| XGB median PR | 0,0673 | **0,0925** | **+0,0252** |
| XGB IQR ROC | 0,2300 | 0,1987 | −0,0313 |
| XGB IQR PR | 0,1070 | 0,1155 | +0,0085 |
| XGB median gain | 2,28× | **3,93×** | **+1,65×** |
| XGB pooled ROC | 0,7476 | **0,7676** | **+0,0200** |
| XGB pooled PR | 0,0640 | **0,0759** | **+0,0119** |
| XGB pooled gain | 3,72× | **4,41×** | **+0,69×** |
| RF median ROC | 0,7330 | **0,7724** | **+0,0394** |
| RF median PR | 0,0731 | **0,0894** | **+0,0162** |
| RF IQR ROC | 0,2096 | 0,2138 | +0,0042 |
| RF IQR PR | 0,1250 | 0,1752 | +0,0502 |
| RF median gain | 2,70× | **3,19×** | **+0,49×** |
| RF pooled ROC | 0,7476 | **0,7568** | **+0,0091** |
| RF pooled PR | 0,0608 | **0,0668** | **+0,0060** |
| RF pooled gain | 3,53× | **3,88×** | **+0,35×** |

**Paired per-fold deltas (78 fold evaluable yang sama):**

| Model | Median ΔROC | Fold naik/turun/seri | Median ΔPR | Fold naik/turun/seri |
|---|---:|---:|---:|---:|
| XGBoost | **+0,0194** (mean +0,0227) | 49 / 29 / 0 | **+0,0158** (mean +0,0337) | 57 / 21 / 0 |
| Random Forest | **+0,0105** (mean +0,0141) | 54 / 24 / 0 | **+0,0072** (mean +0,0208) | 48 / 30 / 0 |

Kuartil delta per fold: XGB ROC −0,0225 / +0,0194 / +0,0602; PR −0,0001 / +0,0158 /
+0,0533. RF ROC −0,0034 / +0,0105 / +0,0400; PR −0,0061 / +0,0072 / +0,0290. Jadi
perbaikan bukan hanya dari beberapa fold ekstrem, tetapi distribusinya condong positif
pada mayoritas fold.

**Within-protein / between-protein diagnostics:**

| Metric | XGB 9.5 | XGB 10.1 | RF 9.5 | RF 10.1 |
|---|---:|---:|---:|---:|
| Within-protein z-scored pooled ROC | 0,6877 | **0,7156** | 0,6891 | **0,7059** |
| Within-protein rank-normalized pooled ROC | — | 0,7153 | — | 0,7109 |
| Between-protein AUC | 0,7851 | 0,7785 | 0,7824 | 0,7824 |
| Spearman mean score vs prevalence | 0,5142 | 0,5068 | 0,5105 | 0,5121 |
| Pearson mean score vs prevalence | — | 0,4515 | — | 0,4435 |

**Mean feature importance (10 teratas):**

| Rank | XGBoost feature | Mean importance | Random Forest feature | Mean importance |
|---:|---|---:|---|---:|
| 1 | `pae_mean_row` | 0,1950 | `pae_mean_col` | 0,2581 |
| 2 | `pae_mean_col` | 0,1822 | `pae_mean_row` | 0,1978 |
| 3 | `aa_nonpolar` | 0,1262 | **`spatial_plddt_mean_8a`** | **0,1123** |
| 4 | `hydropathy_kd` | 0,0894 | `plddt_ca` | 0,1037 |
| 5 | `charge_ph7` | 0,0829 | `aa_nonpolar` | 0,0793 |
| 6 | **`spatial_density_8a`** | **0,0798** | `hydropathy_kd` | 0,0708 |
| 7 | `plddt_ca` | 0,0578 | **`spatial_density_8a`** | **0,0620** |
| 8 | **`spatial_plddt_mean_8a`** | **0,0374** | `pae_local_mean_k10` | 0,0528 |
| 9 | **`spatial_pae_mean_8a`** | **0,0309** | **`spatial_pae_mean_8a`** | **0,0211** |
| 10 | `pae_local_mean_k10` | 0,0283 | `n_atoms` | 0,0164 |

Total importance ketiga fitur spasial: **14,8%** (XGB) dan **19,5%** (RF). Pada RF,
`spatial_plddt_mean_8a` menempati peringkat 3 dan `spatial_density_8a` peringkat 7.

### 20.6 Interpretation — perbaikan within-protein, inflasi antar-protein tetap

1. **Perbaikan konsisten pada kedua model dan kedua metrik utama.** Median ROC naik
   +0,0415 (XGB) / +0,0394 (RF); median PR +0,0252 / +0,0162; pooled ROC +0,0200 /
   +0,0091; pooled PR +0,0119 / +0,0060. Semua arah positif.
2. **Kenaikan bukan hanya urutan antar-protein.** Within-protein z-scored ROC naik
   0,6877 → 0,7156 (XGB, +0,0279) dan 0,6891 → 0,7059 (RF, +0,0168). Ini bukti
   bahwa fitur spasial menambah sinyal untuk membedakan residu **di dalam** protein
   yang sama, bukan sekadar memindahkan peringkat protein.
3. **Mayoritas fold membaik.** 49/78 (XGB) dan 54/78 (RF) fold naik pada ROC;
   57/78 dan 48/78 naik pada PR. Median delta positif pada keduanya.
4. **Between-protein ordering tidak berubah banyak.** Between-protein AUC 0,7785
   (XGB, turun tipis dari 0,7851) dan 0,7824 (RF, tetap); Spearman ~0,51. Pooled ROC
   0,7676/0,7568 masih memuat komponen antar-protein dan **tidak boleh** dibaca sebagai
   generalisasi per-protein.
5. **Kolinearitas membatasi klaim kausal.** `spatial_plddt_mean_8a` sangat mirip
   `plddt_ca` (r = 0,9885), sehingga sebagian kenaikan bisa berasal dari pengukuran
   kualitas lokal yang lebih halus, bukan geometri baru. `spatial_pae_mean_8a`
   berkorelasi rank tinggi dengan `pae_local_mean_k10` (0,8800). Yang paling unik
   adalah `spatial_density_8a` (korelasi sedang dengan fitur lama).
6. **Tidak ada validasi eksternal.** Seluruh 102 protein masih dipakai dalam LOGO-CV;
   belum ada holdout protein yang tidak terlibat dalam pemilihan fitur. Tidak ada
   kalibrasi probabilitas lintas-protein.
7. **Biaya komputasi:** ekstraksi O(102 × N²) jarak Cα; untuk 102 protein / 55.503
   residu selesai dalam hitungan detik–menit di CPU. Tidak ada perubahan dependensi.

**Kesimpulan:** Stage 10.1 menunjukkan bahwa fitur lingkungan spasial radius 8,0 Å
memberi perbaikan yang konsisten dan measurable pada diskriminasi per-residu, termasuk
di dalam protein yang sama. Namun ini tetap **feature engineering pada dataset yang
sama**, bukan validasi eksternal; klaim generalisasi tetap belum boleh dibuat.

### 20.7 Status and interpretation

- **What is proven:** identitas, dimensi (55.503 × 15), LF, dan 0 NaN dataset spasial;
  definisi fitur yang eksplisit; seluruh 166.509 nilai baru direproduksi independen
  dengan 0 mismatch; metrik LOGO-CV 16 fitur dihitung ulang dengan konfigurasi frozen;
  perbaikan median/pooled dan within-protein vs Stage 9.5 terukur pada kedua model.
- **What is not proven:** generalisasi ke protein baru; bahwa kenaikan berasal dari
  geometri 3D murni dan bukan dari kolinearitas dengan pLDDT/PAE lama; bahwa radius
  mana pun optimal secara eksternal. Sweep radius 6/8/10/12 Å dan kalibrasi out-of-fold
  **dilakukan di Stage 10.2** dan memilih 12 Å, sehingga radius 8,0 Å Stage 10.1 bukan
  pilihan final (§21); kalibrasi pada protein eksternal dan representativitas 102
  protein tetap belum terbukti.
- **Bukan benchmark terkunci:** Stage 8.2 dan `BENCHMARK_DATASET_LOCK.md` tidak diubah.
  Stage 10.1 adalah artefak baru; status benchmark-nya perlu keputusan terpisah.
- **Belum di-commit:** dataset dan dokumentasi Stage 10.1 masih di working tree dan
  menunggu persetujuan user.

### 20.8 Audit provenance

Ekstraktor `make_spatial.py`, verifier independen `verify_spatial.py`, harness
`metrics101.py`, dan `diagnostics101.py` dijalankan di
`C:\Users\walet\AppData\Local\Temp\stage101_audit` (di luar tracked tree) dengan
`python -I`, path input/output sebagai argumen. Tidak ada perubahan pada `src/`,
`requirements.txt`, atau dataset Stage 7/8.2/9.x. Bukti reproducible: SHA256 dataset,
audit JSON per protein (SHA256 CIF/PAE/API + statistik fitur), dan tabel metrik §20.5.
Audit JSON lengkap: `C:\Users\walet\AppData\Local\Temp\stage101_audit\spatial_extraction_audit.json`.

---

## 21. Stage 10.2 — Multi-Radius Neighborhood Sweep & Cross-Protein OOF Calibration, 102 Protein (Audited 2026-10-20)

**Status: AUDITED — RADIUS 6/8/10/12 Å DIEVALUASI, 12 Å TERPILIH; KALIBRASI
ISOTONIC/SIGMOID OUT-OF-FOLD DIUJI; DATASET 55.503 × 21; BUKAN VALIDASI EKSTERNAL
DAN BUKAN BUKTI GENERALISASI.**

### 21.1 Artifact identity

| Field | Value |
|---|---|
| Authoritative path | `results/dataset/production_dataset_100_calibrated.csv` |
| Derived from | `production_dataset_100_spatial_r12a.csv` (15 fitur, untracked) + 6 file OOF `.npz` |
| SHA256 | `2c4bcb3da7dfe4de82a95902f6fa3156e656cb5aece521b54d427cb42220ea3a` |
| Size | 9.667.972 bytes |
| Rows | 55.503 residue records (plus header) |
| Columns | **21** — 15 kolom fitur + 6 kolom skor OOF |
| Feature columns | 12 kolom Stage 9.5 tanpa perubahan + `spatial_density_12a`, `spatial_plddt_mean_12a`, `spatial_pae_mean_12a`; model menerima **16 fitur** (13 frozen + 3 spasial) setelah one-hot `amino_acid_type` |
| OOF columns | `oof_xgb_raw`, `oof_xgb_isotonic`, `oof_xgb_sigmoid`, `oof_rf_raw`, `oof_rf_isotonic`, `oof_rf_sigmoid` |
| Proteins | 102 |
| Positives (`target_y = 1`) | 955 (1,7206%) — identik dengan Stage 9.5/10.1 |
| Zero-positive proteins | 24; 78 protein evaluable |
| Folds | 102 LOGO folds; 78 evaluable |
| Missing values | **0** di seluruh 21 kolom |
| Line endings | **LF** — 0 CRLF, 0 lone CR, 55.504 LF, final newline, tanpa BOM |

### 21.2 Experimental design

**Radius sweep.** Untuk setiap protein dengan N residu dan koordinat Cα `CA_i`:

```
Neighbours_R(i) = { j != i : ||CA_i - CA_j||_2 <= R },  R in {6, 8, 10, 12} Å
```

| Feature | Definition |
|---|---|
| `spatial_density_{R}a` | `\|Neighbours_R(i)\|` — jumlah residu lain dalam radius R |
| `spatial_plddt_mean_{R}a` | rata-rata `pLDDT_CA(j)` untuk `j ∈ Neighbours_R(i)`; 3 desimal |
| `spatial_pae_mean_{R}a` | rata-rata `PAE[i, j]` untuk `j ∈ Neighbours_R(i)`; baris i (directed); 3 desimal |

Diri sendiri selalu dikeluarkan; tidak ada imputasi; satu protein gagal verifikasi akan
membatalkan seluruh output. Empat CSV fitur (r6/r8/r10/r12) mempertahankan 12 kolom
Stage 9.5 string-for-string, dan seluruh nilai baru diverifikasi ulang oleh parser
independen (0 mismatch, lihat §21.4).

**Aturan pemilihan radius — ditetapkan sebelum hasil dilihat:**

1. median ROC XGBoost tertinggi pada 78 fold evaluable;
2. jika selisih ≤ 0,002, median ROC Random Forest tertinggi;
3. jika masih ≤ 0,002, pooled PR XGBoost tertinggi.

**Protokol LOGO-CV.** 102 fold; setiap protein diuji sekali dan tidak pernah dipakai
melatih modelnya. Konfigurasi XGBoost dan Random Forest identik dengan Stage 8.2–10.1:
XGB `n_estimators=100, max_depth=3, learning_rate=0.03, scale_pos_weight=neg/pos,
random_state=42, n_jobs=1`; RF `n_estimators=100, max_depth=4,
class_weight='balanced_subsample', max_features='sqrt', random_state=42, n_jobs=1`.
Metrik median/IQR dihitung atas 78 fold; pooled dihitung atas seluruh OOF.

**Protokol kalibrasi.** Untuk setiap fold LOGO:

1. base model dilatih pada 101 protein latih;
2. kalibrator dilatih **hanya** dari prediksi out-of-fold di dalam training set, memakai
   `GroupKFold(n_splits=3)` yang dikelompokkan per protein;
3. `CalibratedClassifierCV(estimator=base, method={'isotonic'|'sigmoid'}, cv=inner_splits,
   n_jobs=1, ensemble=False)`;
4. protein uji diprediksi oleh model terkalibrasi dan tidak pernah menyentuh base model
   maupun kalibrator.

`ensemble=False` dipilih agar satu base model dilatih pada seluruh protein latih dan
kalibrator hanya memetakan probabilitasnya; `ensemble=True` akan merata-ratakan tiga
sub-model dan mencampur efek kalibrasi dengan bagging.

### 21.3 Radius sweep results

**XGBoost (78 fold evaluable):**

| Radius | Median ROC (IQR) | Median PR (IQR) | Pooled ROC | Pooled PR | Pooled gain | Within-protein z-ROC | Between-protein AUC |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 6 Å | 0,7437 (0,2264) | 0,0692 (0,1049) | 0,7495 | 0,0584 | 3,39× | 0,6879 | 0,7828 |
| 8 Å | 0,7786 (0,1987) | 0,0925 (0,1155) | 0,7676 | 0,0759 | 4,41× | 0,7156 | 0,7785 |
| 10 Å | 0,8049 (0,1768) | 0,1000 (0,1272) | 0,7923 | 0,0818 | 4,76× | 0,7426 | 0,7820 |
| **12 Å** | **0,8120 (0,2090)** | **0,1255 (0,1588)** | **0,7956** | **0,0881** | **5,12×** | **0,7495** | 0,7828 |

**Random Forest (78 fold evaluable):**

| Radius | Median ROC (IQR) | Median PR (IQR) | Pooled ROC | Pooled PR | Pooled gain | Within-protein z-ROC | Between-protein AUC |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 6 Å | 0,7331 (0,2204) | 0,0762 (0,1407) | 0,7462 | 0,0575 | 3,34× | 0,6880 | 0,7889 |
| 8 Å | 0,7724 (0,2138) | 0,0894 (0,1752) | 0,7568 | 0,0668 | 3,88× | 0,7059 | 0,7824 |
| 10 Å | 0,7946 (0,2077) | 0,0905 (0,1542) | 0,7696 | 0,0637 | 3,70× | 0,7231 | 0,7862 |
| **12 Å** | **0,8089 (0,2094)** | **0,1051 (0,1505)** | **0,7759** | **0,0711** | **4,13×** | **0,7338** | 0,7870 |

**Pemilihan:** median ROC XGB tertinggi ada pada 12 Å (0,81197), sehingga aturan
tie-break tidak diperlukan. **Radius terpilih: 12,0 Å.** Radius 12 Å adalah batas atas
grid yang diuji; belum ada uji 14/16 Å, jadi angka ini tidak boleh disebut radius optimal
secara global.

**Friedman test lintas empat radius (78 fold yang sama):**

| Model | Metric | Statistic | p | Mean rank r6 / r8 / r10 / r12 |
|---|---|---:|---:|---|
| XGBoost | ROC | 29,842 | 1,49e-06 | 2,000 / 2,231 / 2,788 / 2,981 |
| XGBoost | PR | 35,472 | 9,68e-08 | 1,821 / 2,500 / 2,660 / 3,019 |
| Random Forest | ROC | 65,837 | 3,32e-14 | 1,731 / 2,218 / 2,731 / 3,321 |
| Random Forest | PR | 60,324 | 5,01e-13 | 1,667 / 2,372 / 2,744 / 3,218 |

**Paired per-fold Wilcoxon (median delta, fold naik/turun/seri):**

| Comparison | Model | ΔROC | p (ROC) | ΔPR | p (PR) |
|---|---|---|---:|---:|---:|
| r12 vs r10 | XGBoost | +0,0065 (46/31/1) | 0,0838 | +0,0071 (48/29/1) | 0,0158 |
| r12 vs r8 | XGBoost | +0,0360 (54/24/0) | 1,15e-06 | +0,0091 (51/27/0) | 0,0130 |
| r10 vs r8 | XGBoost | +0,0266 (56/22/0) | 6,93e-07 | +0,0031 (44/34/0) | 0,2721 |
| r6 vs r8 | XGBoost | −0,0217 (28/50/0) | 0,0087 | −0,0174 (22/56/0) | 1,75e-04 |
| r12 vs r10 | Random Forest | +0,0137 (55/23/0) | 3,76e-05 | +0,0072 (54/24/0) | 0,0110 |
| r12 vs r8 | Random Forest | +0,0236 (64/14/0) | 1,03e-08 | +0,0110 (53/25/0) | 0,0125 |
| r10 vs r8 | Random Forest | +0,0144 (50/27/1) | 8,77e-05 | +0,0039 (50/28/0) | 0,1244 |
| r6 vs r8 | Random Forest | −0,0165 (23/52/3) | 9,66e-04 | −0,0077 (23/53/2) | 1,86e-03 |

r12 mengungguli r8 secara signifikan pada ROC dan PR untuk kedua model. Kenaikan r12 vs
r10 pada XGB ROC tidak signifikan (p = 0,0838), tetapi PR signifikan; pada RF keduanya
signifikan. r6 jelas lebih buruk dari r8. Arah perbaikan konsisten, tetapi besarnya
keunggulan 12 Å atas 10 Å masih moderat.

**Korelasi antar-radius (Pearson / Spearman):**

| Feature | 6–8 | 6–10 | 6–12 | 8–10 | 8–12 | 10–12 |
|---|---:|---:|---:|---:|---:|---:|
| `spatial_density` | 0,7388 / 0,7292 | 0,6758 / 0,6567 | 0,6297 / 0,6162 | 0,8973 / 0,9003 | 0,8552 / 0,8615 | 0,9478 / 0,9486 |
| `spatial_plddt_mean` | 0,9959 / 0,9939 | 0,9904 / 0,9868 | 0,9820 / 0,9783 | 0,9961 / 0,9944 | 0,9893 / 0,9871 | 0,9959 / 0,9947 |
| `spatial_pae_mean` | 0,8035 / 0,8398 | 0,7067 / 0,7989 | 0,6384 / 0,7716 | 0,9108 / 0,9488 | 0,8406 / 0,9222 | 0,9442 / 0,9733 |

Density dan PAE berubah cukup banyak antara 6 Å dan 12 Å (Pearson 0,63–0,64), sedangkan
pLDDT hampir invarian (≥0,98 di semua pasangan). Radius yang lebih besar bukan sekadar
"versi lebih halus" dari radius kecil untuk density/PAE.

**Kolinearitas dengan fitur frozen:**

| Radius | `spatial_plddt` vs `plddt_ca` | `spatial_pae` vs `pae_local_mean_k10` | `density` vs `plddt_ca` |
|---|---:|---:|---:|
| 6 Å | 0,9910 / 0,9868 | 0,4680 / 0,7362 | 0,6149 / 0,5364 |
| 8 Å | 0,9885 / 0,9838 | 0,6451 / 0,8800 | 0,6568 / 0,6006 |
| 10 Å | 0,9822 / 0,9760 | 0,6570 / 0,8933 | 0,7041 / 0,6341 |
| 12 Å | 0,9730 / 0,9674 | 0,6795 / 0,8956 | 0,7048 / 0,6389 |

(Pearson / Spearman.) Radius lebih besar sedikit **menurunkan** kolinearitas linear
pLDDT (0,9910 → 0,9730) tetapi **menaikkan** kolinearitas peringkat PAE (0,7362 →
0,8956). Ketiga fitur tetap sangat terkait dengan pLDDT/PAE lama; sweep radius tidak
menghilangkan kolinearitas (C25).

**Distribusi fitur pada radius 12 Å:**

| Statistic | `spatial_density_12a` | `spatial_plddt_mean_12a` | `spatial_pae_mean_12a` |
|---|---:|---:|---:|
| Min | 3 | 23,588 | 1,000 |
| Q25 | 16 | 77,135 | 1,207 |
| Median | 25 | 91,131 | 1,875 |
| Q75 | 34 | 96,483 | 3,167 |
| Max | 60 | 98,922 | 25,333 |
| Mean | 25,0106 | 82,0873 | 2,6852 |

**Mean feature importance (radius 12):** XGB menempatkan `spatial_density_12a` di
peringkat 3 (0,1454), `spatial_pae_mean_12a` peringkat 9 (0,0365), dan
`spatial_plddt_mean_12a` peringkat 11 (0,0257); total ketiga fitur spasial **20,77%**.
RF menempatkan `spatial_density_12a` peringkat 2 (0,1789), `spatial_plddt_mean_12a`
peringkat 4 (0,0926), dan `spatial_pae_mean_12a` peringkat 9 (0,0270); total **29,84%**.

### 21.4 Dataset construction & verification

`production_dataset_100_calibrated.csv` menggabungkan 15 kolom fitur CSV r12 dengan enam
kolom skor OOF. Verifikasi independen (parser terpisah, `csv` + NumPy, bukan penulis
dataset):

- **55.503 baris × 21 kolom**, header persis `15 fitur + 6 OOF`, 0 sel kosong/NaN.
- **15 kolom fitur string-identik** dengan `production_dataset_100_spatial_r12a.csv`
  (0 mismatch dari 832.545 sel fitur).
- **6 kolom OOF** sama dengan array `.npz` sumbernya; selisih maksimum ≤ 5e-11
  (pembulatan 10 desimal).
- Semua probabilitas berada di [0, 1]; isotonic boleh menghasilkan tepat 0 atau 1.
- **LF murni**: 0 CRLF, 0 lone CR, 55.504 LF, tanpa BOM, final newline.
- SHA256 `2c4bcb3da7dfe4de82a95902f6fa3156e656cb5aece521b54d427cb42220ea3a`;
  9.667.972 B.
- Metrik Brier, log loss, ECE, mean predicted, pooled ROC/PR, dan within-z dihitung ulang
  dari CSV dan cocok dengan ringkasan tiap run: metrik probabilitas < 1e-10; pooled ROC/PR
  RF isotonic bergeser ~2,8e-07 / 1,8e-06 karena pembulatan 10 desimal menciptakan tie
  tambahan pada skor piecewise-constant isotonic.
- `target_y` 955 positif, 102 protein, 24 zero-positive, 78 fold evaluable — identik
  dengan Stage 9.5/10.1.

**Hash empat CSV fitur radius:**

| Radius | SHA256 | Bytes |
|---:|---|---:|
| 6 Å | `68617f2d6580e6360390725ca6cb51cbf956a934f15cce905e333eaeeb869f8d` | 5.290.210 |
| 8 Å | `8e21534055132c8cf4eb823e1abda224a15776b437b94bbc851f1ea4a99a3319` | 5.313.161 |
| 10 Å | `6ad922a69444084f87ab7791c811ec2ec2eeefef4069fb854f6a2cfaaf0f2097` | 5.334.434 |
| 12 Å | `2871ce252a188cc13e6e3eb5ae80e7d8394fe682c3c0482d8a01ce9dbef2f914` | 5.338.651 |

CSV r8 identik byte-per-byte dengan dataset Stage 10.1, sehingga ekstraksi ulang
tervalidasi silang terhadap artefak yang sudah diaudit. CSV r6/r10/r12 hanya berada di
area audit temporer dan tidak dipromosikan ke repo.

**Peringatan penggunaan:** enam kolom OOF adalah **artefak audit**, bukan fitur latih.
Setiap skor berasal dari model yang tidak melihat protein baris tersebut, tetapi memakai
kolom itu sebagai input model baru tanpa nested CV akan menyebabkan leakage. Dataset ini
adalah feature table 15 kolom + hasil evaluasi, bukan dataset 21 kolom untuk training
(C28).

### 21.5 Calibration results (radius 12)

**Metrik diskriminasi/peringkat:**

| Model | Method | Median ROC | Median PR | Pooled ROC | Pooled PR | Within-z ROC | Between AUC | Between Spearman |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| XGBoost | raw | 0,8120 | 0,1255 | 0,7956 | 0,0881 | 0,7495 | 0,7828 | 0,5255 |
| XGBoost | isotonic | 0,8120 | 0,1227 | 0,7900 | 0,0833 | 0,7418 | 0,7889 | 0,5406 |
| XGBoost | sigmoid | 0,8120 | 0,1255 | 0,7947 | 0,0828 | 0,7475 | 0,7859 | 0,5376 |
| Random Forest | raw | 0,8089 | 0,1051 | 0,7759 | 0,0711 | 0,7338 | 0,7870 | 0,5209 |
| Random Forest | isotonic | 0,7948 | 0,1106 | 0,7699 | 0,0685 | 0,7228 | 0,7847 | 0,5237 |
| Random Forest | sigmoid | 0,8089 | 0,1051 | 0,7744 | 0,0653 | 0,7333 | 0,7839 | 0,5189 |

**Metrik skala probabilitas:**

| Model | Method | Brier | Log loss | ECE (10 quantile bins) | Mean predicted | Prevalence-on-score slope | Per-protein Brier (median) | Per-protein \|mean−prev\| (median) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| XGBoost | raw | 0,1820 | 0,5284 | 0,3569 | 0,3741 | 0,0865 | 0,2061 | 0,4194 |
| XGBoost | isotonic | **0,0163** | 0,0812 | **0,0016** | 0,0176 | 0,9055 | 0,0136 | 0,0120 |
| XGBoost | sigmoid | **0,0164** | **0,0763** | 0,0020 | 0,0176 | 0,8933 | 0,0136 | 0,0116 |
| Random Forest | raw | 0,1902 | 0,5440 | 0,3681 | 0,3853 | 0,0839 | 0,2502 | 0,4451 |
| Random Forest | isotonic | **0,0165** | 0,0798 | **0,0017** | 0,0176 | 0,8762 | 0,0134 | 0,0128 |
| Random Forest | sigmoid | **0,0165** | **0,0781** | 0,0021 | 0,0178 | 0,8643 | 0,0133 | 0,0129 |

Prevalensi aktual = 0,017206. Skala absolut sebelum kalibrasi sangat inflasi: rata-rata
prediksi XGB 0,3741 vs prevalensi 0,0172 (≈21,7× lebih tinggi), dengan slope prevalensi
terhadap skor hanya 0,0865. Setelah kalibrasi, mean predicted ≈ prevalensi dan slope
mendekati 1. Brier turun >10× dan log loss turun ≈6,5–7×; ECE turun >150×. Per-protein Brier dan
per-protein |mean − prevalence| membaik pada **102/102 protein** untuk isotonic dan
sigmoid, pada kedua model.

**Korelasi skala absolut antar-protein** (Pearson antara rata-rata skor protein dan
prevalensi protein): XGB raw 0,4484 → isotonic 0,4370 → sigmoid 0,4357; RF raw 0,4366 →
isotonic 0,4166 → sigmoid 0,4172. Kalibrasi tidak meningkatkan korelasi ini; ketiganya
sedikit menurun, konsisten dengan antara-protein AUC yang hanya bergeser kecil.

**Inflation gap (pooled ROC − within-z ROC):**

| Model | Raw | Isotonic | Sigmoid |
|---|---:|---:|---:|
| XGBoost | 0,0461 | 0,0482 | 0,0471 |
| Random Forest | 0,0421 | 0,0470 | 0,0410 |

Kalibrasi **tidak** menutup gap ini; pada XGB dan RF isotonic gap justru melebar.

**Efek per fold dan peringkat:**

| Model | Method | max \|ΔROC\| vs raw | max \|ΔPR\| vs raw | Fold ROC naik/turun | Fold PR naik/turun | Reorder mean-score protein (Spearman) |
|---|---|---:|---:|---:|---:|---:|
| XGBoost | isotonic | 0,0793 | 0,2686 | 34/43 | 29/49 | 0,9895 |
| XGBoost | sigmoid | 0,0000 | 0,0000 | 0/0 | 0/0 | 0,9955 |
| Random Forest | isotonic | 0,1380 | 0,2934 | 18/58 | 34/43 | 0,9911 |
| Random Forest | sigmoid | 0,0000 | 0,0000 | 0/0 | 0/0 | 0,9944 |

**Sigmoid bersifat strictly monotone per fold**, sehingga ROC/PR di dalam setiap fold
tidak berubah sama sekali; pergeseran pooled ROC/PR berasal dari pemetaan yang berbeda
antar-fold. **Isotonic tidak strictly monotone** (piecewise-constant), menciptakan tie,
dan karena itu dapat mengubah peringkat di dalam fold: 34 fold XGB membaik dan 43 memburuk
pada ROC; RF 18 membaik dan 58 memburuk. Peringkat rata-rata skor antar-protein hampir
tidak berubah (Spearman ≥ 0,9895 untuk isotonic, ≥ 0,9944 untuk sigmoid), yang menjelaskan
mengapa between-protein AUC dan Spearman tidak membaik secara berarti.

### 21.6 Interpretation — kalibrasi memperbaiki skala, bukan diskriminasi

1. **Sweep radius memberi perbaikan monoton sampai 12 Å.** XGB median ROC 0,7437 → 0,7786
   → 0,8049 → 0,8120; RF 0,7331 → 0,7724 → 0,7946 → 0,8089. Within-protein z-scored ROC
   juga naik (XGB 0,6879 → 0,7495; RF 0,6880 → 0,7338), jadi kenaikan bukan hanya urutan
   antar-protein. Friedman test menolak kesamaan keempat radius pada ROC dan PR untuk
   kedua model (p ≤ 1,49e-06).
2. **12 Å didukung, tetapi bukan "optimum global".** 12 Å adalah batas grid; r12 vs r10
   pada XGB ROC tidak signifikan (p = 0,0838), meski PR dan RF ROC signifikan. Diperlukan
   uji radius lebih besar (14/16 Å) dan ablasi fitur sebelum menyebut 12 Å final.
3. **Kolinearitas tidak hilang.** `spatial_plddt` vs `plddt_ca` masih 0,9730 (Pearson)
   pada 12 Å; `spatial_pae` vs `pae_local_mean_k10` 0,8956 (Spearman); `spatial_density`
   vs `plddt_ca` 0,7048. Kenaikan metrik tidak boleh diatribusikan seluruhnya pada
   "geometri 3D baru" (C25).
4. **Kalibrasi adalah perbaikan skala, bukan perbaikan model.** Brier 0,1820 → 0,0163,
   ECE 0,3569 → 0,0016, mean predicted 0,3741 → 0,0176. Namun pooled ROC turun tipis
   (0,7956 → 0,7900 isotonic / 0,7947 sigmoid), within-z turun (0,7495 → 0,7418/0,7475),
   dan between-protein AUC hanya bergeser kecil dengan arah tidak konsisten (XGB 0,7828 →
   0,7889/0,7859; RF 0,7870 → 0,7847/0,7839). Tidak ada dasar untuk mengklaim kalibrasi
   meningkatkan predictive power.
5. **Score inflation antar-protein adalah masalah peringkat, bukan skala.** Between-protein
   AUC mengukur apakah rata-rata skor protein mengurutkan prevalensi protein; kalibrasi
   yang monotone per fold hampir tidak mengubah urutan itu (reorder Spearman ≥ 0,9895).
   Pooled ROC tetap lebih tinggi dari within-protein ROC karena komponen antar-protein,
   bukan karena probabilitas tidak terkalibrasi (C27).
6. **Sigmoid lebih aman daripada isotonic untuk penggunaan peringkat.** Sigmoid
   rank-preserving dan tidak mengubah satu pun fold; isotonic menciptakan tie dan pada
   RF menurunkan median ROC 0,8089 → 0,7948 serta memperburuk 58/78 fold ROC. Jika tujuan
   hanya probabilitas absolut, keduanya sangat baik; jika peringkat dipertahankan,
   sigmoid adalah pilihan yang lebih konservatif.
7. **Tidak ada validasi eksternal.** Semua 102 protein yang sama dipakai untuk sweep,
   pemilihan radius, dan evaluasi kalibrasi. Tidak ada protein holdout yang tidak terlibat
   dalam keputusan desain. Hasil Stage 10.2 adalah evaluasi internal, bukan bukti
   generalisasi.
8. **Biaya komputasi.** Empat radius × dua model × 102 fold LOGO, ditambah 102 fold × dua
   metode kalibrasi × dua model dengan inner GroupKFold 3; seluruhnya CPU, tanpa
   perubahan dependensi atau GPU.

### 21.7 Status and interpretation

- **What is proven:** radius 6/8/10/12 Å diekstrak dan diverifikasi independen (0
  mismatch); aturan pemilihan radius ditetapkan sebelum hasil dan memilih 12 Å; LOGO-CV
  78 fold dihitung untuk empat radius dan dua model; Friedman/paired tests dilaporkan;
  kalibrasi isotonic/sigmoid dijalankan out-of-fold tanpa memakai protein uji; dataset
  21 kolom diverifikasi (0 NaN, LF, hash, fitur identik, OOF cocok); metrik skala dan
  peringkat dihitung ulang dari CSV.
- **What is not proven:** generalisasi ke protein baru; bahwa 12 Å optimal secara global;
  bahwa fitur spasial menambah informasi independen di luar pLDDT/PAE; bahwa kalibrasi
  memperbaiki diskriminasi atau inflasi antar-protein; kalibrasi lintas-protein eksternal;
  representativitas 102 protein.
- **Bukan benchmark terkunci:** Stage 8.2 dan `BENCHMARK_DATASET_LOCK.md` tidak diubah.
  Stage 10.2 adalah artefak baru; status benchmark-nya perlu keputusan terpisah.
- **Belum di-commit:** dataset dan dokumentasi Stage 10.2 masih di working tree dan
  menunggu persetujuan user; tidak ada commit/push.

### 21.8 Audit provenance

Ekstraktor `extract_multi_radius.py`, verifier `verify_multi_radius.py`, harness
`metrics_radius.py`, `calibrate_radius.py`, `analyze_radius.py`,
`analyze_calibration.py`, `correlations_radius.py`, `build_calibrated_dataset.py`, dan
`verify_calibrated_dataset.py` dijalankan di
`C:\Users\walet\AppData\Local\Temp\stage102_audit` (di luar tracked tree) dengan
`python -I`, path input/output sebagai argumen. Tidak ada perubahan pada `src/`,
`requirements.txt`, atau dataset Stage 7/8.2/9.x/10.1. Bukti reproducible: SHA256 dataset
dan empat CSV fitur, `radius_comparison.json`, `calibration_comparison.json`,
`radius_feature_correlations.json`, `calibrated_dataset_audit.json`, dan
`calibrated_verification.json` (semua di area audit temporer).

---

## 22. Stage 10.3 — Hyperparameter Tuning, Imbalance Strategy & Golden Model Selection (Audited 2026-10-21)

**Status: AUDITED — TUNING INTERNAL DAN PEMILIHAN GOLDEN; BUKAN VALIDASI EKSTERNAL.**

### 22.1 Artifact identity

| Aspek | Nilai |
|---|---|
| Dataset | `results/dataset/production_dataset_100_calibrated.csv` |
| SHA256 / ukuran | `2c4bcb3da7dfe4de82a95902f6fa3156e656cb5aece521b54d427cb42220ea3a`; 9.667.972 B; LF murni |
| Bentuk | 55.503 baris × 21 kolom (15 kolom identifier/label/fitur + 6 kolom skor OOF audit) |
| Protein / positif | 102 protein; 955 positif; prevalensi **1,7206277138%**; 24 protein zero-positive |
| Fold evaluable | **78** dari 102 fold LOGO |
| Fitur latih | **16**: 7 struktural + 3 spasial radius 12 Å + 6 one-hot asam amino |
| Dikecualikan | 6 kolom `oof_*` (artefak audit, bukan fitur latih; C28) |
| Environment | Python 3.12.10; numpy 2.5.4; pandas 3.0.6; scipy 1.18.1; scikit-learn 1.9.1; xgboost 3.4.1; lightgbm 4.6.0 |
| Repo | commit `f995c8c`; working tree hanya `download/` yang untracked dan sudah ada sebelumnya |
| Dataset baru | **Tidak ada** — seluruh keluaran Stage 10.3 adalah artefak evaluasi di luar tracked tree |

Dataset dan urutan baris diverifikasi ulang: label dan `uniprot_id` pada OOF harus identik
dengan CSV terkalibrasi (assert), OOF berisi 55.503 nilai, 0 NaN, 955 positif, 102 protein.
Hash dataset sama dengan Stage 10.2; Stage 10.3 tidak menulis ulang dataset.

### 22.2 Experimental design

**LOGO-CV.** Setiap fold melatih model pada 101 protein dan memprediksi satu protein yang
tidak pernah dilihat. Dari 102 fold, **78 evaluable** (fold dengan minimal satu positif dan
satu negatif); 24 protein zero-positive tetap dilaporkan sebagai `unevaluable`.

**Tuning berarah (OFAT).** XGBoost dan LightGBM menjalani **2 pass**; Random Forest **1 pass**.
Setiap pass mengevaluasi satu perubahan parameter terhadap konfigurasi basis, lalu semua
perubahan yang diterima secara individual diterapkan bersamaan. Grid yang dipakai:

| Model | Pass | Konfigurasi/pass | Parameter yang dipindai |
|---|---:|---:|---|
| XGBoost | 2 | 22 | `scale_pos_weight` [1, 5, 10, 20, 40, `ratio`, 80, 100]; `max_depth` 2–6; `learning_rate` [0,01, 0,02, 0,03, 0,05, 0,08]; `subsample` [0,6, 0,75, 0,9, 1,0]; `colsample_bytree` [0,6, 0,75, 0,9, 1,0] |
| LightGBM | 2 | 23 | sama dengan XGBoost, ditambah `is_unbalance=True`; `num_leaves=31`, `min_child_samples=20` tetap |
| Random Forest | 1 | 8 | `class_weight` [None, `balanced`, `balanced_subsample`]; `max_depth` 3–6; `max_features` [`sqrt`, 0,5, 1,0] |

**Aturan penerimaan.** Perubahan diterima bila **median PR meningkat > 0,002**, atau bila
selisihnya dalam 0,002 **dan** pooled gain meningkat > 0,05×. Jika seri, Brier lebih rendah
menang. Aturan ini sengaja memprioritaskan median PR per-protein, dengan pooled gain sebagai
penjaga; konsekuensinya beberapa perubahan diterima meskipun pooled gain turun.

**Konfigurasi derived.** Karena pass menerapkan semua perubahan yang diterima sekaligus,
konfigurasi hasil seleksi-pass adalah **kombinasi yang belum tentu pernah dievaluasi**.
Ketiga konfigurasi hasil seleksi-pass karena itu dihitung ulang sebagai konfigurasi tetap
(`eval_one.py`); tanpa langkah ini, metriknya tidak sah. Total kandidat seleksi: 98 konfigurasi
hasil tuning + 3 konfigurasi re-eval = **101 konfigurasi unik** (XGB 45, LGBM 47, RF 9).

**Aturan golden (ditetapkan sebelum hasil).** (1) median PR tertinggi; (2) di antara kandidat
dalam **0,005** median PR, pooled gain tertinggi; (3) di antara kandidat dalam **0,05×** pooled
gain, Brier terendah; (4) tie-break deterministik pada `config_id`. Aturan yang sama diterapkan
per arsitektur.

**Nested validation.** Outer LOGO 102 fold; inner `GroupKFold(5)` pada 101 protein latih.
Setiap kandidat di-fit hanya pada protein inner-training, dipilih berdasarkan median PR inner
(dalam 0,002 → pooled gain dalam 0,05× → Brier), lalu di-fit ulang pada 101 protein dan
memprediksi protein uji. Kandidat diambil dari 3 konfigurasi non-RF teratas ditambah XGB dan
LGBM terbaik dari tuning global; konstruksi kandidat ini memakai seluruh protein sehingga
nested masih mengandung komponen optimistis.

### 22.3 Imbalance strategy comparison

Dibandingkan pada konfigurasi baseline pass 1 masing-masing model (XGB/LGBM: `max_depth=3`,
`learning_rate=0,03`, `subsample=1,0`, `colsample_bytree=1,0`; RF: `max_depth=4`,
`max_features=sqrt`), 102-fold LOGO-CV.

**XGBoost**

| `scale_pos_weight` | Median ROC | Median PR | Pooled PR | Gain | Between AUC | Brier | ECE |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0,8321 | 0,1206 | **0,0982** | **5,708×** | **0,7882** | **0,0162** | **0,0027** |
| 5 | 0,8272 | 0,1133 | 0,0956 | 5,559× | 0,7862 | 0,0219 | 0,0609 |
| 10 | 0,8264 | 0,1194 | 0,0905 | 5,258× | 0,7809 | 0,0360 | 0,1140 |
| 20 | 0,8218 | 0,1238 | 0,0920 | 5,344× | 0,7809 | 0,0697 | 0,1929 |
| 40 | 0,8207 | 0,1265 | 0,0878 | 5,101× | 0,7805 | 0,1346 | 0,2970 |
| `ratio` | 0,8120 | 0,1255 | 0,0881 | 5,123× | 0,7828 | 0,1820 | 0,3569 |
| 80 | 0,8119 | **0,1274** | 0,0858 | 4,988× | 0,7782 | 0,2358 | 0,4159 |
| 100 | 0,8140 | 0,1272 | 0,0870 | 5,058× | 0,7759 | 0,2747 | 0,4546 |

**LightGBM**

| `scale_pos_weight` | Median ROC | Median PR | Pooled PR | Gain | Between AUC | Brier | ECE |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0,8357 | 0,1181 | 0,1015 | 5,900× | **0,7924** | **0,0162** | **0,0030** |
| 5 | 0,8267 | 0,1109 | 0,0966 | 5,617× | 0,7843 | 0,0213 | 0,0528 |
| 10 | 0,8299 | 0,1172 | 0,0959 | 5,571× | 0,7816 | 0,0342 | 0,1020 |
| 20 | 0,8191 | 0,1212 | 0,0994 | 5,778× | 0,7793 | 0,0630 | 0,1726 |
| 40 | 0,8179 | 0,1234 | 0,0966 | 5,617× | 0,7743 | 0,1177 | 0,2645 |
| `ratio` | 0,8171 | 0,1173 | **0,1042** | **6,053×** | 0,7766 | 0,1569 | 0,3178 |
| 80 | 0,8283 | 0,1096 | 0,0942 | 5,475× | 0,7820 | 0,2033 | 0,3732 |
| 100 | 0,8029 | **0,1305** | 0,0937 | 5,447× | 0,7747 | 0,2354 | 0,4078 |
| `is_unbalance=True` | 0,8171 | 0,1173 | **0,1042** | **6,053×** | 0,7766 | 0,1569 | 0,3178 |

`is_unbalance=True` identik dengan `scale_pos_weight="ratio"` pada seluruh delapan metrik
(selisih 0). Ini konsisten dengan implementasi LightGBM yang menetapkan
`scale_pos_weight = n_negatif / n_positif` secara internal; keduanya bukan strategi terpisah.

**Random Forest**

| `class_weight` | Median ROC | Median PR | Pooled PR | Gain | Between AUC | Brier | ECE |
|---|---:|---:|---:|---:|---:|---:|---:|
| `None` | 0,8109 | **0,1301** | **0,0912** | **5,298×** | **0,7982** | **0,0164** | **0,0040** |
| `balanced` | 0,8135 | 0,1029 | 0,0692 | 4,020× | 0,7885 | 0,1942 | 0,3725 |
| `balanced_subsample` | 0,8089 | 0,1051 | 0,0711 | 4,131× | 0,7870 | 0,1902 | 0,3681 |

**Temuan utama.**

- **Tidak ada strategi yang menang di semua metrik.** Pada XGB dan LGBM, `scale_pos_weight=1`
  memberi pooled PR, between-protein AUC, dan kalibrasi terbaik, tetapi median PR-nya bukan
  yang tertinggi. Bobot besar (40–100) menaikkan median PR per-protein sedikit, tetapi
  menurunkan pooled PR, between-protein AUC, dan sangat merusak Brier/ECE.
- **Pola yang sama di ketiga model:** kenaikan median PR dari pembobotan kelas dibayar dengan
  penurunan kualitas skor lintas-protein. Contoh ekstrem: LGBM `spw=100` median PR 0,1305
  (tertinggi) tetapi pooled PR 0,0937 dan Brier 0,2354; LGBM `spw=1` median PR 0,1181 tetapi
  pooled PR 0,1015 dan Brier 0,0162.
- **Random Forest justru terbaik tanpa pembobotan** pada baseline ini: `class_weight=None`
  unggul pada median PR, pooled PR, between-protein AUC, dan Brier dibanding kedua opsi
  `balanced`. Ini berlawanan dengan resep umum untuk data imbalanced dan menunjukkan bahwa
  efek pembobotan bergantung pada model, kedalaman, dan metrik yang dioptimalkan.
- Konsekuensinya, pemilihan "strategi imbalansi terbaik" tidak valid tanpa menyebut metrik.
  Golden rule memakai median PR sebagai primer dengan pooled gain dan Brier sebagai penjaga;
  strategi akhir yang terpilih adalah `scale_pos_weight=20` pada LightGBM pass 2, bukan
  strategi dengan pooled PR terbaik.

### 22.4 Directed tuning results

Baseline Stage 10.2 dan hasil seleksi-pass:

| Model | Baseline Stage 10.2 (median ROC / PR) | Pass-1 selected (derived) | Pass-2 selected (derived) | Re-eval konfigurasi pass terpilih (median PR / gain / Brier) | Median PR terbaik yang pernah dievaluasi |
|---|---|---|---:|---:|---:|
| XGBoost | 0,8120 / 0,1255 | `xgb__5c030c8d7c7d` | `xgb__496d370641fb` | 0,1508 / 6,716× / 0,0209 | 0,1523 (`xgb__94b7eeb26f8e`; gain 3,772×, Brier 0,2020) |
| LightGBM | 0,8171 / 0,1173 | `lgbm__b8bcbf3e4ca3` | `lgbm__f44f0031b2c3` | 0,1522 / 6,478× / 0,0590 | **0,1693** (`lgbm__032c38ffe37f`) |
| Random Forest | 0,8089 / 0,1051 | `rf__7d4e21346df6` | — | 0,1256 / 5,494× / 0,0162 | 0,1301 (`rf__af1481c35450`; gain 5,298×, Brier 0,0164) |

**Keputusan pass.** XGBoost pass 1 menerima `max_depth=6` (Δmedian PR +0,0229; Δgain
+1,197×), `learning_rate=0,01` (+0,0268; −1,351×), `subsample=0,6` (+0,0079; +0,040×), dan
`colsample_bytree=0,75` (+0,0080; +0,075×); `scale_pos_weight=40` ditolak (+0,0010; −0,022×).
Pass 2 menerima `scale_pos_weight=5` (+0,0073; +0,321×) dan `learning_rate=0,08` (+0,0066;
+0,159×), tetapi menolak `max_depth=5` (−0,0045), `subsample=1,0` (+0,0015; −0,466×), dan
`colsample_bytree=0,9` (−0,0023).

LightGBM pass 1 menerima `scale_pos_weight=100` (+0,0132; −0,606×), `max_depth=6` (+0,0286;
+0,685×), `learning_rate=0,05` (+0,0196; +0,117×), `subsample=0,75` (+0,0355; +0,055×), dan
`colsample_bytree=0,9` (+0,0078; +0,107×). Pass 2 menerima `scale_pos_weight=20` (+0,0389;
+0,292×), `max_depth=4` (+0,0123; −0,077×), `learning_rate=0,03` (+0,0246; +0,469×),
`subsample=1,0` (+0,0131; −0,212×), dan `colsample_bytree=0,75` (+0,0234; −0,149×). Semua
perubahan pass 2 diterima karena kenaikan median PR melewati ambang, meskipun tiga di antaranya
menurunkan pooled gain. Konfigurasi golden `lgbm__032c38ffe37f` adalah **kandidat variasi
`scale_pos_weight=20`** yang dievaluasi pada pass 2 terhadap basis pass 1, bukan konfigurasi
derived hasil seleksi pass 2 (`lgbm__f44f0031b2c3`). Aturan golden meranking seluruh konfigurasi
yang pernah dievaluasi, sehingga kandidat antara ini bisa menang; konfigurasi derived tidak
otomatis menjadi golden.

Random Forest menerima `class_weight=None` (+0,0250; +1,167×), `max_depth=6` (+0,0227;
+0,848×), dan `max_features=1,0` (+0,0055; −0,232×).

**Catatan penting tentang `xgb__94b7eeb26f8e`.** Konfigurasi ini punya median PR tertinggi di
XGB (0,1523), tetapi pooled gain hanya 3,772× dan Brier 0,2020 — lebih buruk daripada baseline
Stage 10.2 pada pooled PR. Golden rule tidak memilihnya karena guardrail pooled gain dan Brier;
arsitektur XGB terbaik menjadi `xgb__496d370641fb` (median PR 0,1508; gain 6,716×; Brier 0,0209).
Ini contoh konkret mengapa median PR saja tidak cukup.

**LightGBM pass 1 reproducibility.** Pass 1 dijalankan ulang penuh dari awal dan **23/23
konfigurasi mereproduksi seluruh 8 metrik hingga selisih ≤ 1e-12** dibandingkan backup; konfigurasi
terpilih juga identik. Pass 2 selesai 23/23 tanpa error setelah dijalankan dengan 3 worker.

### 22.5 Golden model selection and final LOGO-CV

Kandidat seleksi: 101 konfigurasi unik. Aturan golden memilih:

| Model | Config | Median ROC (IQR) | Median PR (IQR) | Pooled ROC | Pooled PR | Gain | Within-z | Brier | ECE |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| XGBoost | `xgb__496d370641fb` | 0,8303 (0,1346) | 0,1508 (0,1825) | 0,8156 | 0,1156 | 6,716× | 0,7662 | 0,0209 | 0,0373 |
| **LightGBM** | **`lgbm__032c38ffe37f`** | **0,8411 (0,1446)** | **0,1693 (0,1737)** | **0,8131** | **0,1142** | **6,634×** | **0,7709** | 0,0520 | 0,1228 |
| Random Forest | `rf__7d4e21346df6` | 0,8002 (0,1580) | 0,1256 (0,1572) | 0,7895 | 0,0945 | 5,494× | 0,7380 | **0,0162** | **0,0014** |

**Golden model: LightGBM `lgbm__032c38ffe37f`.**

| Parameter | Nilai |
|---|---|
| `n_estimators` | 100 |
| `max_depth` | 6 |
| `num_leaves` | 31 |
| `learning_rate` | 0,05 |
| `subsample` / `subsample_freq` | 0,75 / 1 |
| `colsample_bytree` | 0,9 |
| `min_child_samples` | 20 |
| `scale_pos_weight` | 20 |

Metrik LOGO-CV lengkap (78 fold evaluable):

| Metrik | Nilai |
|---|---:|
| Median ROC (IQR) | **0,8411** (0,1446) |
| Median PR (IQR) | **0,1693** (0,1737) |
| Pooled ROC | **0,8131** |
| Pooled PR | **0,1142** |
| Pooled PR gain | **6,634×** |
| Within-protein z-scored ROC | **0,7709** |
| Within-protein rank ROC | 0,7690 |
| Brier | 0,0520 |
| Log loss | 0,1917 |
| ECE (10 bin kuantil) | 0,1228 |
| Mean predicted probability | 0,1400 |
| Prevalensi aktual | 0,0172 |
| Rasio mean predicted / prevalensi | 8,14× |
| Between-protein AUC | 0,7751 |
| Between-protein Spearman | 0,5270 |
| Between-protein Pearson | 0,4766 |
| Fold evaluable | 78 |

**Perbandingan berpasangan per fold** (Wilcoxon dua sisi, 78 fold):

| Pembanding | ΔROC median (p) | ΔPR median (p) | Fold PR naik / turun |
|---|---|---|---:|
| Stage 10.2 XGB raw | +0,0003 (0,3478) | **+0,0086 (0,0466)** | 45 / 33 |
| Stage 10.2 RF raw | +0,0158 (0,0862) | **+0,0108 (0,0107)** | 47 / 31 |
| LightGBM baseline Stage 10.3 | −0,0033 (0,8989) | **+0,0120 (0,0316)** | 44 / 34 |

**Interpretasi.**

- Golden menaikkan **median PR** dari 0,1255 (Stage 10.2 XGB) menjadi 0,1693 (+0,0438; +34,9%)
  dan **within-protein z-scored ROC** dari 0,7495 menjadi 0,7709 (+0,0214). Pooled ROC naik
  0,7956 → 0,8131 (+0,0174), pooled PR 0,0881 → 0,1142 (+0,0260), gain 5,123× → 6,634×.
- Kenaikan **bukan** hanya antar-protein: within-z juga naik. Namun between-protein AUC sedikit
  **turun** (0,7828 → 0,7751 vs Stage 10.2 XGB; 0,7870 → 0,7751 vs RF), dan gap
  pooled-minus-within masih 0,0422 (0,8131 − 0,7709), hanya sedikit lebih sempit dari 0,0461
  pada Stage 10.2 XGB. Inflasi antar-protein belum hilang.
- Uji berpasangan menunjukkan kenaikan yang konsisten terutama pada **PR**; ROC golden hampir
  identik dengan Stage 10.2 XGB (p = 0,3478) dan tidak berbeda signifikan dari RF pada ROC
  (p = 0,0862). Jadi klaim yang tepat adalah "PR ranking membaik pada protein yang sama",
  bukan "model jauh lebih baik secara umum".
- **Kalibrasi tidak di-fit ulang.** Mean predicted 0,1400 adalah 8,14× prevalensi; Brier
  0,0520 dan ECE 0,1228 adalah skor mentah. Stage 10.2 sudah menunjukkan isotonic/sigmoid
  dapat menurunkan Brier/ECE ke ≈0,016/≈0,002 tanpa memperbaiki peringkat. Karena itu Brier
  golden **tidak boleh** dibandingkan langsung dengan Brier terkalibrasi Stage 10.2, dan jika
  probabilitas absolut dibutuhkan, kalibrasi harus di-fit per fold pada protein latih.
- Pemilihan golden memakai 102 protein yang sama untuk tuning dan evaluasi. Angka 0,1693
  adalah **optimistic selection estimate**; §22.6 mengukur sebagian optimisme itu.

### 22.6 Nested validation

Outer LOGO 102 fold; inner `GroupKFold(5)` pada 101 protein latih. Kandidat: 3 konfigurasi
non-RF teratas dari tuning global + XGB dan LGBM terbaik = 4 entri, tetapi
`lgbm__4e9ac82cd5df` (`ratio`) dan `lgbm__bbe856f87d0b` (`is_unbalance=True`) adalah konfigurasi
efektif yang sama; yang terakhir tidak pernah dipilih (0 fold), sehingga hasil tidak berubah.
Tiga konfigurasi efektif: `lgbm__032c38ffe37f`, `lgbm__4e9ac82cd5df`, `xgb__496d370641fb`.

| Metrik | Golden global (dipilih pada 102 protein) | Nested LOGO-CV |
|---|---:|---:|
| Median ROC (IQR) | 0,8411 (0,1446) | 0,8303 (0,1316) |
| Median PR (IQR) | 0,1693 (0,1737) | 0,1550 (0,1839) |
| Pooled ROC | 0,8131 | 0,7961 |
| Pooled PR | 0,1142 | 0,0784 |
| Pooled PR gain | 6,634× | **4,555×** |
| Within-protein z-scored ROC | 0,7709 | 0,7680 |
| Brier | 0,0520 | 0,0340 |
| ECE | 0,1228 | 0,0653 |
| Mean predicted | 0,1400 | 0,0824 |
| Between-protein AUC | 0,7751 | 0,7343 |
| Fold evaluable | 78 | 78 |

**Pilihan konfigurasi per fold:** `xgb__496d370641fb` **81/102**, `lgbm__032c38ffe37f` **11/102**,
`lgbm__4e9ac82cd5df` **10/102**, `lgbm__bbe856f87d0b` **0/102**.

**Interpretasi.**

- Gap global vs nested: median PR 0,1693 → 0,1550 (−0,0144), pooled PR 0,1142 → 0,0784
  (−0,0358), pooled gain 6,634× → 4,555× (−2,08×), median ROC 0,8411 → 0,8303 (−0,0109).
  Ini adalah estimasi optimisme seleksi yang lebih jujur daripada angka global.
- Gap **pooled PR jauh lebih besar** daripada gap median per-fold. Perbandingan berpasangan
  nested vs golden global memberi median ΔPR 0,0000 dengan 36 fold naik, 36 turun, dan 6 tie.
  Artinya ranking per-protein tidak jauh berubah; yang rusak adalah **komparabilitas skala
  skor antar-fold**, karena setiap fold dapat memilih konfigurasi berbeda. Pooled PR
  mengagregasi skor dari model yang berbeda per protein, sehingga sangat sensitif terhadap
  perbedaan skala. Metrik median per-protein dan within-protein harus dilaporkan bersama
  pooled, tidak menggantikannya.
- Nested masih lebih baik daripada Stage 10.2 RF pada PR (Δ +0,0153; p = 0,0194) dan tidak
  berbeda signifikan dari Stage 10.2 XGB pada PR (Δ +0,0083; p = 0,1093) maupun ROC
  (Δ +0,0171; p = 0,0742). Klaim yang benar: prosedur tuning menghasilkan keunggulan PR yang
  modest dan tidak konsisten secara statistik terhadap XGB Stage 10.2.
- **Keterbatasan nested:** kandidat berasal dari tuning global yang memakai seluruh 102
  protein. Pipeline yang sepenuhnya nested (tuning di dalam setiap outer fold) tidak
  dijalankan; itu akan jauh lebih mahal dan tetap tidak menghilangkan bias pemilihan fitur
  atau radius dari stage sebelumnya.

### 22.7 Interpretation and limitations

- **Golden Stage 10.3 adalah tuned LightGBM, bukan model baru secara arsitektur.** Tidak ada
  fitur baru, protein baru, atau dataset baru; yang berubah hanya konfigurasi dan strategi
  imbalansi.
- **Peningkatan terutama pada PR, bukan ROC.** Median PR +34,9% relatif terhadap Stage 10.2
  XGB, tetapi median ROC +0,0292 dan ΔROC berpasangan tidak signifikan. Jangan mengutip
  kenaikan PR sebagai bukti generalisasi.
- **Pemilihan strategi imbalansi bergantung metrik.** Bobot kelas besar menaikkan median PR
  tetapi menurunkan pooled PR/gain, between-protein AUC, dan kalibrasi. Stage 10.3 tidak
  menemukan "strategi terbaik" universal.
- **Brier/ECE golden adalah skor mentah.** Tidak ada kalibrasi ulang; angka ini tidak
  sebanding dengan Stage 10.2 terkalibrasi (0,0163/0,0016). Jika probabilitas absolut
  diperlukan, gunakan kalibrasi per fold pada protein latih dan laporkan terpisah.
- **Selection bias terukur tetapi belum hilang.** Nested menurunkan median PR ke 0,1550 dan
  pooled gain ke 4,555×; kandidat nested masih berasal dari tuning global, dan radius 12 Å
  serta fitur spasial sudah dipilih pada stage sebelumnya memakai protein yang sama.
- **Tidak ada validasi eksternal.** Seluruh 102 protein terlibat dalam desain (fitur, radius,
  tuning, seleksi). Tidak ada holdout protein baru.
- **12 Å masih batas grid.** Stage 10.3 tidak menguji radius 14/16 Å atau ablasi fitur.
- **Tidak ada analisis stabilitas seed.** XGBoost dan LightGBM dijalankan single-thread dengan
  parameter tetap; Random Forest memakai `n_jobs=-1`. Golden OOF direproduksi bit-identik
  dalam environment ini, tetapi stabilitas lintas seed/BLAS tidak diuji.
- **Konfigurasi derived sudah dihitung ulang.** Tanpa re-eval, metrik konfigurasi hasil
  seleksi-pass tidak sah karena kombinasi tersebut belum tentu pernah dievaluasi.
- **Jangan memakai kolom `oof_*` sebagai fitur.** Peringatan C28 tetap berlaku.

### 22.8 Audit provenance

- Harness eksternal (di luar repo): `stage103_common.py`, `tune_model.py`, `select_golden.py`,
  `eval_one.py`, `nested_validate.py`, `compare_final.py`, `summarize_tuning.py`,
  `provenance.py`, `make_report.py`.
- Artefak: `tuning/{xgb,lgbm,rf}/best_config.json`; `selection/golden_selection.json`;
  `final/summary_golden.json` (SHA256 `8fed6bed…e367a6`) dan `final/oof_golden.npz`
  (`93cb9276…218d9d`); `nested/nested_summary.json` (`880b2d45…a48c`) dan
  `nested/nested_oof.npz` (`ca9364b7…267a`); `final/provenance.json` (17 artefak).
- Verifikasi: OOF golden 55.503 baris, 0 NaN, 955 positif, 102 protein, urutan baris = CSV;
  OOF golden identik dengan OOF tuning `lgbm__032c38ffe37f` (selisih maksimum 0,0).
- Environment: Python 3.12.10; numpy 2.5.4; pandas 3.0.6; scipy 1.18.1; scikit-learn 1.9.1;
  xgboost 3.4.1; lightgbm 4.6.0. Repo commit `f995c8c`; tidak ada file tracked yang berubah.
- LightGBM pass 1 dijalankan ulang: 23/23 konfigurasi identik hingga 1e-12. Pass 2 selesai
  23/23 tanpa error setelah dijalankan dengan 3 worker.

---

## 23. Stage 11 — Production Artifact & Standalone Inference Pipeline (Tested 2026-10-21)

**Status: TESTED — ARTEFAK REPRODUCIBLE DAN CLI BERJALAN END-TO-END; BUKAN VALIDASI
EKSTERNAL.**

### 23.1 Artifact identity

| Field | Value |
|---|---|
| Artefak | `results/models/golden_lightgbm_12a.joblib` |
| Ukuran | **157.432 B** |
| SHA256 | `98c86efbebcb7e7986921386a07ca76319c453536dd8e4a2afd2a9b8085445da` |
| `artifact_version` / `stage` | `stage11-1.0` / `11.1` |
| `artifact_name` | `golden_lightgbm_12a` |
| Model | LightGBM `lgbm__032c38ffe37f` (Stage 10.3 golden) |
| Dataset latih | `results/dataset/production_dataset_100_calibrated.csv`, SHA256 `2c4bcb3d…ea3a`, 9.667.972 B |
| Baris / protein / positif | **55.503 / 102 / 955** (prevalensi 0,017206277138172712) |
| Fitur | 16, urutan tetap (7 struktural + 3 spasial radius 12 Å + 6 one-hot AA) |
| Kalibrator deployed | sigmoid pada logit skor OOF |
| Kalibrator pembanding | isotonic pada skor OOF |
| Environment | Python 3.12.10; numpy 2.5.3; pandas 3.0.6; scikit-learn 1.9.1; lightgbm 4.6.0; scipy 1.18.1; joblib 1.6.0; biopython 1.88 |

Artefak memuat `model`, `calibrator` (sigmoid), `calibrator_isotonic`, `feature_names`,
`model_params`, `model_kwargs`, `dataset`, `oof` (metrics + SHA256 skor float64
`9d05419659ef6c26f023e3e48474b988eabfb5d651d7932889817a7c0309a192`), `calibration`,
`final_model` (metrik in-sample + warning), `feature_importance`, `limitations`,
`training_source`, dan `environment`. Model final dilatih pada **seluruh 55.503 baris**;
metrik OOF adalah evaluasi cross-validation, bukan performa model final.

### 23.2 Export protocol (`src/export_model.py`)

1. **Validasi dataset sebelum menyentuh model.** Hash SHA256, ukuran byte, jumlah baris,
   jumlah protein/positif, 24 protein zero-positive, 78 fold evaluable, kolom wajib, tidak ada
   NaN, tidak ada duplikat `(uniprot_id, sequence_position)`, penomoran 1..N, konsistensi
   `amino_acid_type`, pLDDT ∈ [0, 100], density ≥ 1, dan PAE non-negatif. Dataset yang berbeda
   ditolak, bukan diterima diam-diam.
2. **Reproduksi OOF Stage 10.3.** 102-fold LOGO dengan konfigurasi golden dan kwargs
   deterministik (`num_threads=1`, `force_col_wise=True`, `deterministic=True`,
   `random_state=42`). Metrik dibandingkan dengan nilai Stage 10.3 yang diharapkan pada
   `atol=1e-9`; OOF direproduksi dengan selisih maksimum **0,0**. Loop memakan ~54 detik.
3. **Fit kalibrator pada skor OOF.** Sigmoid = `LogisticRegression(C=1e6, solver="lbfgs",
   max_iter=1000, tol=1e-10)` pada `logit(p_raw)` dengan clip 1e-6; isotonic =
   `IsotonicRegression(out_of_bounds="clip", y_min=0, y_max=1)`. Sigmoid dipilih **sebelum
   evaluasi** karena rank-preserving dan tidak menciptakan tie; isotonic hanya pembanding.
4. **Latih ulang model final pada semua baris**, lalu tulis payload dengan
   `joblib.dump(compress=3)`. Script mencetak SHA256 dan ukuran artefak.

Koefisien sigmoid yang tersimpan: **0,8216068** (logit) dan intercept **−2,7257097**, yaitu
`sigmoid(0,8216068 × logit(p_raw) − 2,7257097)`.

### 23.3 Calibration results (OOF, 55.503 skor)

| Metode | Mean predicted | Min | Max | Brier | Log loss | ECE (10 bins) | Nilai unik |
|---|---:|---:|---:|---:|---:|---:|---:|
| raw | 0,140044 | 0,000346 | 0,919933 | 0,052005 | 0,191708 | 0,122838 | 53.670 |
| **sigmoid (deployed)** | **0,017206** | 0,000094 | 0,327435 | **0,016072** | 0,073974 | **0,000811** | 53.670 |
| isotonic (pembanding) | 0,017206 | 0,0 | 1,0 | 0,015955 | 0,073141 | ≈0 (2,2e-18) | **45** |

Prevalensi OOF = 0,0172063. Sigmoid memindahkan mean predicted tepat ke prevalensi tanpa
mengubah urutan skor; isotonic sedikit lebih rendah Brier-nya tetapi meruntuhkan 55.503 skor
menjadi 45 nilai, sehingga tidak dipakai. **Ini in-sample calibration fit pada skor OOF yang
juga dipakai mengevaluasi**, bukan estimasi pada protein baru.

Model final (dilatih pada semua baris) menyimpan metrik in-sample sebagai sanity check:
raw Brier 0,045595 / ECE 0,121765; sigmoid Brier 0,014528 / ECE 0,012303; isotonic Brier
0,014142 / ECE 0,011578. Artefak menyertakan warning bahwa model final melihat seluruh label
training dan angka ini tidak boleh dilaporkan sebagai performa/validasi.

### 23.4 Inference pipeline (`src/inference_features.py`, `src/predict.py`)

`inference_features.py` adalah satu-satunya sumber definisi fitur untuk export dan predict:
konstanta kimia diimpor dari `extract_protein_features.py` (`AA_TYPE`, `CHARGE_PH7`,
`KD_HYDROPATHY`, `PAE_LOCAL_WINDOW`), radius 12,0 Å, 16 nama fitur dalam urutan tetap, parser
mmCIF/PDB, parser PAE, fetch + verifikasi AFDB, dan cache. `predict.py` memuat artefak,
memvalidasi kontrak fitur, menghitung fitur, menerapkan kalibrator, dan menulis CSV.

Output default (stdout) / `--out`:

```
protein_id, uniprot_id, sequence_position, amino_acid, plddt_ca,
probability_raw, probability_calibrated, predicted_active_binding
```

Ringkasan JSON ke stderr memuat jumlah residu, ambang, jumlah panggilan, mean/max
probabilitas, top residu, SHA256 artefak/struktur/PAE, versi AFDB, cache hit, warning, dan
catatan bahwa kalibrasi bukan validasi eksternal. `--features-out` menulis 16 fitur + tiga
kolom identitas dengan presisi `%.17g`. Error input mengembalikan exit code **2**.

Contoh:

```bash
python src/predict.py --uniprot P02144 --out results/predictions/P02144.csv
python src/predict.py --structure AF-P02144-F1-model_v6.cif \
    --pae AF-P02144-F1-predicted_aligned_error_v6.json --out P02144.csv
python src/predict.py --structure AF-P02144-F1-model_v6.pdb --out P02144_pdb.csv
python src/predict.py --uniprot P00520 --threshold 0.5 --top 10 \
    --features-out P00520_features.csv --out P00520.csv
```

**Syarat input.** Satu chain (atau `--chain`); penomoran residu tepat 1..N tanpa renumbering;
B-factor = pLDDT AFDB ∈ [0, 100]; matriks PAE N×N; HETATM dan altloc selain blank/A dilewati;
insertion code ditolak; residu dengan nol tetangga radius 12 Å = error (tidak ada imputasi).
PDB eksperimental umumnya tidak memenuhi syarat pLDDT/PAE dan **tidak didukung** kecuali file
dikonversi dari prediksi AlphaFold. Struktur lokal diasumsikan berasal dari prediksi yang sama
dengan PAE-nya; provenance tidak bisa diverifikasi. AFDB selain v6 memicu warning pergeseran
distribusi.

### 23.5 Test evidence

| Uji | Hasil |
|---|---|
| Export dari dataset committed | 55.503 baris / 102 protein / 955 positif; OOF identik dengan Stage 10.3 (selisih maks **0,0**); artefak 157.432 B, SHA256 `98c86efb…45da` |
| Paritas fitur P02144 vs dataset | 154/154 baris; 16 fitur X selisih maksimum **3,55e-15**, **0 nilai > 1e-12**; probabilitas raw dan calibrated selisih **0,0** |
| P02144 — CIF lokal | exit 0; 154 residu; mean calibrated 0,032184; max 0,147086 di H25; 0 panggilan pada ambang 0,5 |
| P02144 — PDB lokal (konversi Biopython dari CIF AFDB) | exit 0; kolom numerik identik dengan CIF lokal |
| P02144 — unduhan AFDB | exit 0; kolom numerik identik; CIF + PAE + API JSON ter-cache |
| P02144 — cache hit | exit 0; kolom numerik identik dengan unduhan pertama |
| P00520 — AFDB | exit 0; 1.123 residu; mean calibrated 0,006964; max 0,154756 di G251; 0 panggilan pada ambang 0,5 |
| PAE hilang | exit **2** dengan pesan error; tidak ada output CSV |
| PDB dua chain tanpa `--chain` | exit **2**: "ditemukan 2 chain ['A', 'B']"; dengan `--chain A` exit 0 |

P02144 adalah protein training dengan dua label positif A+B (H65 dan H94). H65 berada di
peringkat keempat skor terkalibrasi, tetapi ini **bukan** bukti validasi: label tersebut sudah
dilihat model dan seluruh proses desain. P00520 juga protein training. Kedua uji hanya
menunjukkan bahwa pipeline mengeluarkan skor yang konsisten, bukan bahwa skor itu benar secara
biologis.

### 23.6 Limitations and interpretation

- **Deployment, bukan validasi.** Model final dilatih pada seluruh 102 protein; kalibrator
  di-fit pada OOF protein yang sama. Tidak ada protein baru dengan label independen. Nested
  Stage 10.3 (median PR 0,1550 / pooled gain 4,55×) tetap menjadi estimasi internal yang lebih
  konservatif.
- **Ambang 0,5 tidak tervalidasi.** Ini hanya konvensi tampilan. P02144 dan P00520 mendapat
  nol panggilan karena probabilitas terkalibrasi maksimum hanya 0,1471 dan 0,1548. Jangan
  menafsirkan "tidak ada panggilan" sebagai "tidak ada binding site".
- **Kalibrasi tidak memperbaiki diskriminasi.** Stage 10.2 sudah menunjukkan kalibrasi
  memperbaiki skala, bukan pooled/within-protein ROC. Stage 11 mewarisi batas itu.
- **Kontrak input sempit.** PAE wajib, pLDDT harus ada di B-factor, hanya satu chain,
  penomoran 1..N, dan tidak ada imputasi. Struktur eksperimen, kompleks, ligan, dan PTM tidak
  didukung.
- **Ketergantungan AFDB v6.** Artefak dilatih pada fitur AFDB v6. Versi lain hanya memberi
  warning, bukan jaminan kompatibilitas.
- **Artefak joblib adalah pickle.** Hanya muat dari sumber tepercaya; jangan memuat file yang
  tidak dikenal.
- **Belum ada test suite Stage 11 yang di-commit.** Bukti di atas berasal dari harness
  eksternal (temporary). `src/export_model.py` dan `src/predict.py` belum memiliki file
  `test_*.py` di repo.
- **Tidak ada jaminan stabilitas lintas environment.** Artefak menyimpan versi library, tetapi
  pickle LightGBM/scikit-learn dapat berperilaku berbeda di versi lain; gunakan pin di
  `requirements.txt`.

### 23.7 Audit provenance

- File baru: `src/inference_features.py`, `src/export_model.py`, `src/predict.py`, dan
  `results/models/golden_lightgbm_12a.joblib`.
- Perubahan pendukung: `requirements.txt` (pin scikit-learn 1.9.1, lightgbm 4.6.0, scipy
  1.18.1, joblib 1.6.0), `README.md`, dan dokumen ini.
- Harness uji eksternal (di luar repo):
  `C:\Users\walet\AppData\Local\Temp\stage111_audit\` — `repro_check.py`, `feature_parity.py`,
  CSV/summary P02144 dan P00520, cache AFDB, `two_chain.pdb`, `no_pae/`, dan artefak uji
  lainnya. Tidak ada file uji ini yang di-commit.
- Environment: Python 3.12.10; numpy 2.5.3; pandas 3.0.6; scikit-learn 1.9.1; lightgbm 4.6.0;
  scipy 1.18.1; joblib 1.6.0; biopython 1.88.
- Repo HEAD saat audit: `628e178`. Stage 11 belum di-commit; `git status` menunjukkan
  `results/models/`, `src/export_model.py`, `src/inference_features.py`, `src/predict.py`
  sebagai untracked, plus `download/` yang tidak terkait.
- OOF dicek ulang terhadap referensi Stage 10.3
  (`C:\Users\walet\AppData\Local\Temp\stage103_audit\final\oof_golden.npz`): 55.503 baris,
  `y` dan grup identik, selisih maksimum 0,0.

---

## 24. Recommended Next Step — External Validation

**Rekomendasi: validasi eksternal pada protein yang tidak terlibat dalam desain, bukan
klaim generalisasi. Sweep radius dan kalibrasi out-of-fold diselesaikan di Stage 10.2, tuning
+ pemilihan golden diselesaikan di Stage 10.3, dan ekspor artefak + CLI diselesaikan di
Stage 11; semuanya masih evaluasi internal pada 102 protein yang sama.**

Fokus:

1. **Validasi eksternal** pada protein yang tidak dipakai memilih fitur, radius, atau
   kalibrator; uji kalibrasi probabilitas lintas-protein pada protein baru.
2. **Pertahankan Stage 8.2 tetap frozen.** Jangan mengubah
   `stage7_processed_dataset.csv` atau `BENCHMARK_DATASET_LOCK.md`.
3. **Lengkapi pin dependensi ML.** Stage 11 sudah mem-pin `scikit-learn==1.9.1`,
   `lightgbm==4.6.0`, `scipy==1.18.1`, dan `joblib==1.6.0`; `xgboost`, `numpy`, dan `pandas`
   masih berupa rentang versi. Pin sisanya hanya setelah persetujuan user.
4. **P11532 sudah dikeluarkan di Stage 9.5** (C21 selesai untuk dataset bersih). Jika
   ingin dipakai lagi, rebuild dari sumber full-length yang selaras dengan sekuens
   kanonik dan jadikan artefak terpisah — jangan menyunting dataset bersih atau memakai
   525 baris isoform sebagai residu kanonik.
5. **Laporkan median + IQR dan pooled secara terpisah;** sediakan fold `unevaluable`
   untuk protein tanpa positif (24 protein). Gunakan nilai reproduced, bukan nilai klaim
   yang tidak cocok (C20, C22).
6. **Metrik internal terbaru adalah Stage 10.3 golden LightGBM (radius 12 Å, 16 fitur).**
   Median ROC 0,8411 / PR 0,1693; pooled ROC 0,8131 / PR 0,1142 / gain 6,63×;
   within-protein z-scored ROC 0,7709; Brier 0,0520 dan ECE 0,1228 (skor mentah, belum
   terkalibrasi); between-protein AUC 0,7751. Nested LOGO-CV memberi median PR 0,1550 /
   pooled gain 4,55× — gunakan angka nested sebagai estimasi internal yang lebih
   konservatif. Stage 11 tidak mengubah urutan skor: sigmoid hanya memetakan ulang skor OOF
   (Brier 0,016072, ECE 0,000811, mean 0,017206), dan isotonic pembanding (Brier 0,015955)
   meruntuhkan skor menjadi 45 nilai unik. Bandingkan dengan Stage 10.2 (XGB pooled 0,7956 /
   0,0881; RF 0,7759 / 0,0711), Stage 10.1 (radius 8 Å: XGB 0,7676 / 0,0759; RF 0,7568 /
   0,0668), Stage 9.5 (XGB 0,7476 / 0,0640; RF 0,7476 / 0,0608), dan Stage 9.4 hanya sebagai
   pembanding historis (C24).
7. **Putuskan status benchmark Stage 9.3, 9.4, 9.5, 10.1, 10.2, dan 10.3** (lock terpisah
   atau tetap sebagai artefak ekspansi) sebelum memakai metriknya sebagai pembanding resmi.
8. **Jangan memakai pooled ROC sebagai bukti generalisasi.** Laporkan juga metrik
   within-protein dan median per-protein; pooled ROC Stage 10.3 (0,8131) masih lebih
   tinggi dari within-protein z-scored ROC (0,7709), jadi inflation antar-protein tetap
   ada; between-protein AUC golden (0,7751) bahkan sedikit lebih rendah dari Stage 10.2
   XGB (0,7828). Nested juga menunjukkan pooled PR sangat sensitif terhadap skala skor
   antar-fold (C23, C25, C27).
9. **Jadikan fitur spasial kandidat tetap, bukan kesimpulan.** Sweep radius sudah
   dilakukan (Stage 10.2) dan tuning sudah dilakukan (Stage 10.3), tetapi ablasi fitur
   penuh, uji stabilitas importance lintas-seed, dan uji radius 14/16 Å belum. 12 Å adalah
   batas grid, bukan optimum global yang terbukti (C25).
10. **Jika membutuhkan probabilitas absolut, gunakan sigmoid, bukan isotonic.** Keduanya
    memperbaiki skala (Brier 0,18 → 0,016; ECE 0,36 → 0,002), tetapi isotonic menciptakan
    tie dan menurunkan median ROC RF 0,8089 → 0,7948 pada evaluasi ini; sigmoid
    rank-preserving per fold. Kalibrasi tidak memperbaiki pooled ROC dan tidak menutup gap
    antar-protein; between-protein AUC hanya bergeser < 0,007 (C27).
11. **Enam kolom OOF pada dataset terkalibrasi bukan fitur latih.** Jangan memakainya
    sebagai input model tanpa nested CV; kolom itu adalah artefak audit (C28).
12. **Perlakukan `results/models/golden_lightgbm_12a.joblib` sebagai kandidat deployment,
    bukan model tervalidasi.** Artefak dilatih pada seluruh 102 protein dan kalibratornya
    di-fit pada OOF protein yang sama. Hasil `predict.py` pada P02144/P00520 hanya bukti
    pipeline, bukan bukti biologis. Sebelum dipakai untuk keputusan nyata, jalankan validasi
    eksternal, tetapkan ambang pada data berlabel baru, dan dokumentasikan provenance input.

**Gate Stage 10.3/11:** jangan klaim generalisasi sebelum ada validasi eksternal dan metrik
yang direproduksi dari repo bersih. Stage 10.2 sudah melewati sweep radius dan kalibrasi OOF
internal; Stage 10.3 sudah melewati tuning dan pemilihan golden internal, termasuk nested
LOGO-CV; Stage 11 sudah melewati ekspor artefak dan uji CLI end-to-end. Ketiganya belum
melewati gate validasi eksternal dan tidak menguji satu pun protein baru berlabel.

---

```
NEXT GATE:
EXTERNAL VALIDATION (STAGE 12+)
(Stage 11 = production artifact + inference CLI on the same 102 proteins, tested
 end-to-end, not external validation; Stage 10.3 = tuning + golden selection;
 Stage 10.2 = radius sweep + OOF calibration)
```

---

## Appendix — Discrepancy Register

Perbedaan yang ditemukan antar file/dokumen saat penyusunan dokumen ini. **Tidak
ditebak maksudnya; dicatat apa adanya.** Semua adalah isu dokumentasi/nama-field, bukan
indikasi kerusakan data (semua checksum & test tetap konsisten).

| # | Deskripsi | Bukti | Dampak |
|---|---|---|---|
| D1 | **Status di dua manifest berbeda.** `results/dataset/dataset_manifest.csv` (Stage 4) masih berisi `status = planned_not_downloaded` untuk seluruh 7 baris. Sementara `results/dataset/dataset_download_manifest.csv` (Stage 5) berisi `status = DOWNLOADED_VALIDATED`. `DATASET_PLAN.md` §7 dan Stage 5 report §7 menyebut status manifest akan berubah dari `planned_not_downloaded` → `downloaded`; yang terjadi adalah dibuatnya manifest kedua yang terpisah. | `dataset_manifest.csv` vs `dataset_download_manifest.csv` | Sedang — pembaca bisa salah menyimpulkan unduhan belum dilakukan. Butuh keputusan: perbarui field di manifest Stage 4 atau tambahkan catatan silang |
| D2 | **`data/alphafold_db/raw/README.txt` masih menyatakan folder "KOSONG dengan sengaja"**, padahal folder kini berisi 14 file dataset + README itu sendiri. | `data/alphafold_db/raw/README.txt` vs isi direktori | Rendah — file penanda sudah kedaluwarsa. Test Stage 5 check E4 sudah diperbarui untuk mengizinkan file di `raw/` |
| D3 | **Dua besaran berbeda bernama mirip untuk PAE.** Stage 5 report §12 menyebut `max_predicted_aligned_error` (skalar API, mis. 31,75), sedangkan `pae_validation.csv` kolom `max_pae` berisi maksimum **yang teramati di matriks** (31, 29, 23, …). | Stage 5 report §12 vs `pae_validation.csv` | Rendah — bukan kontradiksi (kuantitas berbeda), tetapi berpotensi membingungkan saat verifikasi manual |
| D4 | **Stage 1–3 tidak punya report mandiri di `docs/`.** `docs/` hanya berisi `DATASET_PLAN.md`, `TAHAP_5_*`, `TAHAP_6_*`. Bukti Stage 1–3 hanya tersebar di README + artefak `results/`. | Isi `docs/` | Rendah — celah dokumentasi, bukan celah data. Bagian 3–5 dokumen ini menutup sebagian celah tersebut |
| D5 | **Wording label Stage 8.2 tidak presisi.** Ringkasan menyebut "Active/Binding/Metal Sites", sedangkan dataset terkunci hanya memakai **Active site + Binding site** (46 positif); metal binding tidak dimasukkan sebagai tipe terpisah. | `download/gemini-code-1792488146615.md` vs `BENCHMARK_DATASET_LOCK.md` §4 | Rendah — lock doc mengoreksi; semua laporan baru harus memakai definisi A+B |
| D6 | **Ringkasan Stage 9 tidak konsisten dengan artefaknya.** Ringkasan menyebut 15 protein / 4.124 residu / 27 fitur (7 struktural + 20 one-hot), tetapi `download/production_dataset_100.csv` hanya berisi 6 kolom tanpa fitur struktural; beberapa nama protein juga salah (P00720 Endolysin disebut Endothiapepsin; P00644 Thermonuclease disebut RNase T1). | `download/gemini-code-1792488647858.md`, `download/production_dataset_100.csv` | Sedang — Stage 9 lama bukan benchmark resmi; **superseded oleh audit Stage 9.2 (§16)** |
| D7 | **Ringkasan Stage 9.2 tidak konsisten dengan CSV-nya.** Markdown menyebut 123 positif, sedangkan CSV berisi 129; dua definisi fitur (`pae_local_mean_k10`, klasifikasi histidin) juga berbeda dari Stage 3/8.2. | `download/gemini-code-1792491213449.md` vs `results/dataset/stage9_processed_dataset.csv`; §16 | Sedang — metrik reproduce dari CSV, tetapi komparabilitas dengan Stage 8.2 terbatas |
| D8 | **IQR PR Stage 9.3 tidak konsisten dengan data per-fold.** Ringkasan menyebut XGB 0,1348 dan RF 0,2259; perhitungan ulang semua metode kuantil menghasilkan 0,1796 dan 0,2461. Median/pooled/gain cocok. | `download/gemini-code-1792492604689.md` vs `results/dataset/stage93_realigned_dataset.csv`; §17.4 | Sedang — docs memakai nilai reproduced; nilai klaim dicatat sebagai pembanding |
| D9 | **P11532 Stage 9.4 memakai isoform AFDB yang tidak selaras.** API mengembalikan 14 isoform, tanpa entri kanonik 3.685 aa; CSV memakai `AF-P11532-9-F1` (525 aa) yang berbeda pada 496/525 posisi dari sekuens kanonik. 3.160 baris lainnya kosong; 4 positifnya tidak punya fitur struktural. | `data/afdb_api/P11532.json`, CIF vs UniProt P11532, `results/dataset/production_dataset_100_realigned.csv`; §18.3 | **RESOLVED di Stage 9.5:** seluruh 3.685 baris P11532 dikeluarkan; dataset bersih 102 protein / 55.503 baris / 955 positif (§19) |
| D10 | **Metrik RF Stage 9.4 tidak konsisten dengan data per-fold.** Klaim median ROC 0,7397 / pooled PR 0,0592 / gain 3,65×; reproduced dengan konfigurasi yang menghasilkan pooled ROC exact 0,7471: 0,7339 / 0,0573 / 3,53×. XGBoost exact. | `results/dataset/production_dataset_100_realigned.csv`; §18.4 | Sedang — docs memakai nilai reproduced; nilai klaim dicatat sebagai pembanding |
| D11 | **Pembersihan P11532 mengubah metrik pooled vs Stage 9.4.** Setelah P11532 dikeluarkan dan model di-retrain: XGB pooled ROC 0,7575 → 0,7476, pooled PR 0,0606 → 0,0640, median ROC 0,7359 → 0,7371; RF pooled ROC 0,7471 → 0,7476, pooled PR 0,0573 → 0,0608, median ROC 0,7339 → 0,7330. | `results/dataset/production_dataset_100_cleaned.csv`; §19.3 | Rendah — bukan error; dampak pembersihan diukur dan didokumentasikan |
| D12 | **`download/` tidak berisi file PDB/CIF/PAE untuk Stage 10.1.** Permintaan Stage 10.1 mengasumsikan file struktur ada di `download/`, tetapi folder itu hanya berisi 6 CSV, 4 Markdown, dan 1 notebook. Ekstraksi memakai cache audit Stage 9.4 di luar tracked tree (102 CIF + 102 PAE + 102 respons API AFDB); tidak ada unduhan baru. | Isi `download/`; `C:\Users\walet\AppData\Local\Temp\stage94_audit\data\`; §20.3 | Rendah — provenance jelas dan file yang dipakai adalah file audit Stage 9.4 yang sama; tetapi ekstraktor tidak dapat direproduksi hanya dari repo tanpa menyediakan file struktur |
| D13 | **Boundary radius 10 Å sensitif terhadap presisi koordinat Cα.** `Bio.PDB` menyimpan koordinat sebagai `float32`, sedangkan Stage 10.2 mem-parse teks CIF penuh sebagai `float64`. Dua pasangan residu P01024 tepat di ambang 10,0 Å (posisi 531 dan 631) berubah status tetangga antara kedua representasi; radius 6/8/12 Å tidak terpengaruh. | Perbandingan `float64` CIF vs `Bio.PDB` `float32` pada P01024 (Stage 10.2); `extract_multi_radius.py`; §21.2–§21.3 | Rendah — hanya memengaruhi radius 10 Å pada satu protein; radius terpilih (12 Å) dan CSV r8 identik byte-per-byte dengan Stage 10.1. Angka radius 10 Å tidak boleh dianggap identik dengan ekstraksi `float32` |
| D14 | **Nama "Stage 10.3" bertabrakan dengan rencana lama.** Dokumen Stage 10.2 menetapkan `STAGE 10.3+ — EXTERNAL VALIDATION`. Permintaan Stage 10.3 (2026-10-21) berisi tuning hiperparameter + pemilihan golden pada 102 protein yang sama, bukan validasi eksternal. Audit ini memakai nama Stage 10.3 sesuai permintaan dan memindahkan gate validasi eksternal ke setelah Stage 11. | §15, §22, §24; blok `NEXT GATE` sebelum dan sesudah audit | Rendah — bukan error data; risiko salah baca bahwa Stage 10.3 adalah validasi eksternal. Semua bagian baru menyatakan eksplisit bahwa Stage 10.3 = tuning internal dan tidak menguji protein baru |
| D15 | **Tidak ada Stage 10.4; penomoran melompat ke Stage 11.** Dokumen Stage 10.2/10.3 menyebut gate berikutnya `STAGE 10.4+ — EXTERNAL VALIDATION`, sedangkan permintaan berikutnya (2026-10-21) adalah ekspor artefak + CLI inferensi, yang secara kronologis menjadi **Stage 11**, dan validasi eksternal tetap belum dikerjakan. Bagian baru ditempatkan sebagai §23; rekomendasi lama (sebelumnya §23) di-renumber menjadi §24. | §15, §23 (baru), §24; blok `NEXT GATE` | Rendah — bukan error data; risiko salah kira bahwa Stage 10.4 atau validasi eksternal sudah ada. Stage 11 adalah deployment dan tidak menguji protein baru berlabel |
