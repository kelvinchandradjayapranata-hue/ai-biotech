# PROJECT STATUS — AI-BIOTECH

**Dokumen ini adalah single source of truth status project.**
Dibuat: 2026-10-05. Sumber: README.md, `docs/` (DATASET_PLAN.md, TAHAP_5, TAHAP_6),
serta manifest/hasil yang ada di `results/` dan `data/`. Tidak ada file Stage 1–6 yang
diubah, tidak ada eksperimen baru dijalankan, tidak ada unduhan dilakukan.

---

```
PROJECT STATUS:
STAGE 1–10.1 AUDITED — STAGE 8.2 BENCHMARK LOCKED
DATA PIPELINE: VALIDATED
BIOLOGICAL ML: BASELINE REPRODUCED — NO GENERALIZATION CLAIM
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
> Bagian 1, 2, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20 (Stage 10.1, baru), dan 21
> di bawah sudah diperbarui; bagian 3–8 tetap merupakan catatan historis Stage 1–6.

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

Yang **BELUM tercapai** (dan tidak diklaim):

- **Belum ada bukti predictive power yang umum.** Baseline Stage 8.2 lemah dan sangat
  heterogen antar-protein: pooled ROC-AUC 0,5368 (XGB) / 0,5062 (RF), sedangkan pooled
  PR-AUC 0,0916 / 0,1028 terhadap baseline prevalensi 0,0419. Stage 9.5 mencapai pooled
  ROC 0,7476 (XGB/RF); Stage 10.1 menambah fitur spasial dan menaikkannya ke 0,7676
  (XGB) / 0,7568 (RF), dengan median per-protein 0,7786 / 0,7724. Kenaikan ini juga
  terlihat pada within-protein z-scored ROC (0,7156 / 0,7059), tetapi seluruh evaluasi
  masih **internal** dan belum ada holdout eksternal; pooled ROC tetap dipengaruhi
  perbedaan antar-protein (§19.4, §20.6). Tidak ada klaim kemampuan generalisasi.
- **Skala masih belum memadai untuk klaim statistik.** Stage 9.5/10.1 berisi 102 protein
  / 55.503 residu, tetapi hanya 955 positif (1,72%), 24 protein tanpa positif, dan residu
  dalam satu protein sangat berkorelasi. Ini bukan 55.503 sampel independen; komposisi
  protein juga masih didominasi protein larut/globular dan belum diseleksi sebagai
  holdout eksternal. Stage 10.1 menambah fitur, **bukan** protein baru.
- **Belum ada validasi eksternal** pada protein baru, struktur eksperimen, atau dataset
  independen. Belum ada uji kalibrasi probabilitas lintas-protein. Stage 9.4/9.5 adalah
  pembesaran/pembersihan dataset, dan Stage 10.1 adalah feature engineering; ketiganya
  **bukan** validasi eksternal.
- **Label masih terbatas pada A+B.** Belum ada label multi-kelas, GO terms, EC numbers,
  atau skema label alternatif.
- **Stage 9.2, 9.3, 9.4, 9.5, dan 10.1 bukan validasi eksternal dan bukan klaim
  generalisasi.** Stage 9.2/9.3 berisi 14 protein / 129 positif; Stage 9.4 berisi 103
  protein / 959 positif; Stage 9.5/10.1 berisi 102 protein / 955 positif. Pooled ROC
  Stage 10.1 (0,7676 XGB / 0,7568 RF) lebih tinggi dari Stage 8.2, tetapi dataset,
  fitur, dan prevalensinya berbeda, dan pooled ROC dipengaruhi perbedaan skor
  antar-protein. Belum ada holdout eksternal.
- **P11532 sudah dikeluarkan, bukan diperbaiki.** Tidak ada entri AFDB full-length
  kanonik untuk P11532 (hanya 14 isoform; §18.3), sehingga Stage 9.5 menyelesaikannya
  dengan **exclusion**. Rebuild dari sumber struktur full-length tetap belum dilakukan;
  jika sumber tersebut tersedia, itu harus menjadi artefak baru, bukan suntingan dataset
  bersih (§19.3).

Posisi jujur: **infrastruktur data selesai dan tervalidasi; benchmark ML baseline sudah
ada dan terverifikasi, ditambah ekspansi/realignment Stage 9.2–9.3, production scaling
Stage 9.4 (103 protein), pembersihan Stage 9.5 (102 protein, P11532 dikeluarkan), dan
feature engineering spasial Stage 10.1 yang nyata dan diaudit — tetapi belum ada bukti
generalisasi biologis.** Dataset Stage 10.1 kini bersih secara struktural dan memiliki
tiga fitur lingkungan 3D yang menaikkan metrik internal, termasuk within-protein ROC
(0,7156 XGB / 0,7059 RF); namun pooled ROC masih dipengaruhi perbedaan antar-protein,
dan tidak ada holdout eksternal. Fokus berikutnya adalah validasi eksternal dan
kalibrasi lintas-protein — bukan mengklaim performa.

---

## 2. Overall Project Status

| Dimensi | Status | Bukti ringkas |
|---|---|---|
| Engineering / data pipeline | **BERHASIL** | 4 script utama + 4 test suite, semua exit 0 |
| Penyediaan struktur AlphaFold | **BERHASIL** | 14/14 file AFDB v6, 0 gagal, checksum cocok |
| Validasi integritas data | **BERHASIL** | SHA256 dihitung ulang & cocok; sekuens 7/7 MATCH |
| Feature extraction | **BERHASIL** | 1098 × 29 kolom, 24/24 test PASS |
| Reproducibility | **BERHASIL** | Output dataset byte-identical antar-run |
| Predictive biological AI / ML | **BASELINE ADA; GENERALISASI BELUM** | Stage 8.2 LOGO-CV direproduksi (pooled ROC 0,5368/0,5062); Stage 10.1 XGB pooled ROC 0,7676 / RF 0,7568, within-protein 0,7156/0,7059, tetapi masih evaluasi internal dan bukan perbandingan apple-to-apple (§19.4, §20.6); median/IQR Stage 8.2 di `BENCHMARK_DATASET_LOCK.md` |
| Label biologis (y) | **ADA — A+B** | `target_y` = UniProt Active site + Binding site; 46 positif (Stage 7), 129 (Stage 9.2/9.3), 959 (Stage 9.4), 955 (Stage 9.5); audit label 0 mismatch di kelima dataset |
| Ekspansi dataset (Stage 9.2) | **AUDITED — REAL AFDB, DENGAN CATATAN** | 14 protein / 3.960 residu; fitur struktural & label cocok dengan sumber; 2 definisi fitur menyimpang dari Stage 8.2 (§16) |
| Realignment dataset (Stage 9.3) | **AUDITED — DEFINISI FROZEN** | 14 protein / 3.960 residu; H = `basic`; `pae_local_mean_k10` = `\|i-j\| ≤ 10, j ≠ i`; 0 mismatch fitur/label; median/pooled/gain reproduce, IQR PR tidak (§17) |
| Production scaling (Stage 9.4) | **AUDITED — 103 PROTEIN, DENGAN CATATAN** | 59.188 × 12; 103 protein; 959 positif (1,62%); 79 fold evaluable; XGB exact (median ROC 0,7359; pooled 0,7575 / 0,0606 / 3,74×); RF pooled ROC 0,7471 cocok tetapi median ROC/pooled PR tidak; P11532 isoform mismatch (§18) |
| Cleansed production dataset (Stage 9.5) | **AUDITED — 102 PROTEIN, BERSIH** | 55.503 × 12; 102 protein; 955 positif (1,72%); 0 sel kosong/unmodeled; 78 fold evaluable; XGB median ROC 0,7371, pooled 0,7476 / 0,0640 / 3,72×; RF median 0,7330, pooled 0,7476 / 0,0608 / 3,53×; P11532 dikeluarkan (§19) |
| Spatial feature dataset (Stage 10.1) | **AUDITED — 55.503 × 15, 0 NaN** | 3 fitur radius 8,0 Å; 102 protein; 955 positif; 78 fold evaluable; XGB median ROC 0,7786, pooled 0,7676 / 0,0759 / 4,41×; RF median 0,7724, pooled 0,7568 / 0,0668 / 3,88×; within-protein 0,7156/0,7059; 166.509 nilai baru diverifikasi ulang, 0 mismatch (§20) |
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
| 6 — Multi-protein features | PASS WITH CONCERNS | 1098 residu × 29 kolom (26 fitur); 7/7 protein PASS; 24/24 test | `results/dataset/multi_protein_*.csv|json|png` | Pipeline terbukti **portabel**; dataset fitur siap-analisis, **belum ada nilai prediktif yang diuji** |
| 7 — Dataset & label | PASS (LOCKED 2026-10-20) | 1098 × 27; label A+B; 46 positif (4,19%); 7-fold LOGO; SHA256 `34f9dd…f61` | `results/dataset/stage7_processed_dataset.csv`, `docs/BENCHMARK_DATASET_LOCK.md` | Benchmark resmi terkunci; 25 kolom identik Stage 6; label audit 7/7 |
| 8.2 — LOGO-CV baseline | PASS (VERIFIED) | 13 fitur; XGB median ROC 0,7185 / PR 0,2144; RF 0,6608 / 0,2647; pooled XGB 0,5368 / 0,0916, RF 0,5062 / 0,1028 | `docs/BENCHMARK_DATASET_LOCK.md` §7 | Baseline reproducible; XGB cocok persis dengan ringkasan Stage 8.2; **bukan bukti generalisasi** |
| 9.2 — Real AFDB expansion | AUDITED (2026-10-20) | 3.960 × 12; 14 protein; 129 positif (3,26%); 13 fitur; XGB median ROC 0,7092 / PR 0,1509, RF 0,7305 / 0,1852; pooled XGB 0,6484 / 0,1022, RF 0,6523 / 0,0996 | `results/dataset/stage9_processed_dataset.csv`, §16 | Ekspansi nyata dari AFDB; metrik reproducible; **bukan benchmark terkunci** dan **tidak langsung sebanding** dengan Stage 8.2 karena 2 definisi fitur berbeda |
| 9.3 — Realigned real-AFDB | AUDITED (2026-10-20) | 3.960 × 12; 14 protein; 129 positif (3,26%); 13 fitur frozen; XGB median ROC 0,7264 / PR 0,1684, RF 0,7518 / 0,1763; pooled XGB 0,6411 / 0,0858, RF 0,6575 / 0,0912; SHA256 `6f0357…7f5a` | `results/dataset/stage93_realigned_dataset.csv`, §17 | Definisi fitur Stage 3/8.2 dipulihkan; fitur & label 0 mismatch; median/pooled/gain reproduce; **IQR PR dilaporkan tidak reproduce**; tetap **bukan pengganti benchmark Stage 8.2** |
| 9.4 — Full production scaling | AUDITED (2026-10-20) | 59.188 × 12; 103 protein; 959 positif (1,62%); 79 fold evaluable; XGB median ROC 0,7359, pooled 0,7575 / 0,0606 (3,74×); RF median ROC 0,7339, pooled 0,7471 / 0,0573; SHA256 `8be323f6…bde1` | `results/dataset/production_dataset_100_realigned.csv`, §18 | Dataset produksi nyata teraudit; XGB exact; RF hanya pooled ROC yang exact; **P11532 isoform mismatch**; kenaikan pooled ROC **bukan** bukti generalisasi |
| 9.5 — Dataset cleansing & isoform resolution | AUDITED (2026-10-20) | 55.503 × 12; 102 protein; 955 positif (1,72%); P11532 dikeluarkan; 0 sel kosong/unmodeled; 78 fold evaluable; XGB median ROC 0,7371, pooled 0,7476 / 0,0640 (3,72×); RF median ROC 0,7330, pooled 0,7476 / 0,0608 (3,53×); SHA256 `e47b3635…05a3` | `results/dataset/production_dataset_100_cleaned.csv`, §19 | Dataset produksi bersih; pooled ROC XGB turun karena artefak P11532 hilang; within-protein tetap ~0,689; **bukan** bukti generalisasi |
| 10.1 — Spatial neighborhood features | AUDITED (2026-10-20) | 55.503 × 15; 102 protein; 955 positif; 3 fitur radius 8,0 Å; 0 NaN; 78 fold evaluable; XGB median ROC 0,7786, pooled 0,7676 / 0,0759 (4,41×); RF median ROC 0,7724, pooled 0,7568 / 0,0668 (3,88×); within-protein 0,7156/0,7059; SHA256 `8e215340…3319` | `results/dataset/production_dataset_100_spatial.csv`, §20 | Fitur spasial menaikkan metrik internal termasuk within-protein; tetap **bukan** validasi eksternal dan **bukan** bukti generalisasi |

**Batas tegas antar baris:** sampai Stage 6, semua capaian bersifat
**engineering + integritas data + ekstraksi fitur**. Stage 7 menambahkan **benchmark
terkunci** (dataset + label), dan Stage 8.2 menambahkan **baseline ML yang
direproduksi**. Stage 9.2 menambahkan **ekspansi dataset nyata yang diaudit**; Stage 9.3
merekonstruksinya dengan **definisi fitur frozen**; Stage 9.4 memperbesar skala ke
**103 protein / 59.188 residu** dan mereproduksi XGBoost persis; Stage 9.5 mengeluarkan
P11532 dan menghasilkan dataset **102 protein / 55.503 residu** yang lengkap tanpa sel
kosong; Stage 10.1 menambahkan tiga fitur lingkungan spasial radius 8,0 Å dan
mengevaluasi ulang LOGO-CV. Tidak satu pun dari Stage 9.2–10.1 menjadi benchmark terkunci
atau mengubah status generalisasi. Tidak ada satu pun baris di tabel ini yang merupakan
klaim biologis atau bukti generalisasi.

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
tetap berlaku untuk seluruh 55.503 baris yang tersisa. Stage 10.1 juga **tidak mengunduh
ulang**: `download/` hanya berisi CSV/Markdown/notebook, **tanpa file PDB/CIF/PAE**.
Ekstraksi memakai cache audit Stage 9.4 di luar tracked tree
(`stage94_audit/data/afdb_files`, 102 CIF + 102 PAE) dan `afdb_api` (102 JSON); seluruh
baris dicocokkan ulang dengan dataset sebelum fitur ditulis (§20.3). Audit independen
Stage 9.2–9.4 dibahas di §16–§18; verifikasi Stage 9.5 di §19; Stage 10.1 di §20.

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

**Tidak ada script ML di `src/`.** Baseline Stage 8.2, evaluasi Stage 9.x, dan ekstraksi
fitur spasial Stage 10.1 dijalankan dengan harness verifikasi eksternal (temporary, di
luar repo); belum ada training/extractor script yang di-commit. Tidak ada
PyTorch/TensorFlow/CUDA.
Environment: `.venv` Python **3.12.10**; `requirements.txt` hanya biopython, pandas,
numpy, matplotlib, ipykernel, nbclient. Verifikasi Stage 8.2 memakai scikit-learn
1.9.1, xgboost 3.4.1, scipy 1.18.1, dan numpy 2.5.4 yang dipasang sementara di luar
`.venv` — **belum** dipin di `requirements.txt` (lihat `BENCHMARK_DATASET_LOCK.md` §8).

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

**D. Predictive biological AI sudah diuji sebagai baseline dan dengan fitur spasial,
tetapi belum terbukti bergeneralisasi.**
Stage 8.2 LOGO-CV sudah dijalankan dan direproduksi (median/IQR dan pooled di
`BENCHMARK_DATASET_LOCK.md`). Stage 10.1 menambahkan tiga fitur spasial dan menaikkan
metrik internal (XGB pooled ROC 0,7676, within-protein 0,7156; RF 0,7568 / 0,7059),
tetapi kenaikan itu diukur pada 102 protein yang sama, tanpa holdout eksternal. Yang
terbukti adalah **reproducibility protokol, angka baseline, dan tambahan sinyal dari
fitur geometri lokal**, bukan predictive power biologis umum.

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
bersih, tetapi itu tidak menambah bukti generalisasi. Stage 10.1 menambah tiga fitur
turunan struktur pada **102 protein yang sama**; fitur-fitur itu berkorelasi dengan
pLDDT/PAE yang sudah ada (mis. `spatial_plddt_mean_8a` vs `plddt_ca` ρ = 0,9885) dan
tidak menambah protein atau sampel independen. Menghitung "N = 55.503" sebagai ukuran
sampel statistik adalah keliru. Status 2026-10-20: benchmark Stage 8.2 tetap terkunci,
dan Stage 10.1 belum mengubah status generalisasi.

**G. Stage 7 (label A+B) SELESAI; ekspansi protein SELESAI sampai 102 protein;
feature engineering spasial Stage 10.1 SELESAI; pertanyaan biologis lanjutan BELUM.**
Stage 7 menetapkan label biner **Active site + Binding site** dan fold LOGO, lalu
Stage 8.2 menetapkan baseline. Ekspansi 14 → 103 → 102 protein sudah dikerjakan di
Stage 9.2–9.5, dan Stage 10.1 menambahkan fitur lingkungan 3D pada dataset 102 protein
yang sama. Pertanyaan yang lebih luas (GO terms, EC numbers, multi-label) dan validasi
eksternal **belum** dikerjakan. 102 protein masih terlalu sedikit dan terkorelasi untuk
klasifikasi umum; `DATASET_PLAN.md` §9 masih berupa usulan arah.

Tambahan yang juga **belum** terbukti/dilakukan:
- Tidak ada validasi terhadap struktur eksperimen (PDB) — tidak ada RMSD, tidak ada
  perbandingan dengan kristalografi/NMR/cryo-EM.
- Tidak ada klaim bahwa pLDDT/PAE tinggi berarti struktur benar di dalam sel.
- Tidak ada docking, molecular dynamics, skrining senyawa, atau eksperimen basah.
- Tidak ada model prediksi fungsi yang tervalidasi/generalisasi; baseline Stage 8.2 bukan
  "penemuan".

---

## 13. Known Limitations / Concerns

Diurutkan dari yang paling berdampak pada tahap berikutnya.

| # | Concern | Tingkat | Sumber | Status penanganan |
|---|---|---|---|---|
| C1 | **Skema Stage 6 = 26 fitur, bukan 28.** `contact_prob_sum` & `n_high_conf_contacts` dikeluarkan karena `contact_probs` tidak tersedia di AFDB | Tinggi (mempengaruhi desain fitur ML) | Stage 6 report §5, §10.1 | **SELESAI untuk benchmark:** Stage 7 menetapkan 27 kolom (25 shared + label + fold); Stage 8.2 memakai 13 fitur. Eksperimen fitur lain tetap terbuka |
| C2 | **Redundansi pLDDT AFDB.** CIF AFDB menulis pLDDT per-residu ke semua atom → di 1098 baris: `plddt_atom_std = 0`, `plddt_atom_mean = min = max = plddt_ca`. 4 kolom `plddt_atom_*` redundan dengan `plddt_ca` | Tinggi (risiko multikolinearitas sempurna bila dipakai ML apa adanya) | Stage 6 report §10.2 | **SELESAI:** 4 kolom `plddt_atom_*` dibuang dari dataset benchmark dan tidak dipakai Stage 8.2 |
| C3 | **Skala dataset tidak memadai untuk ML.** Benchmark 7 protein / 1098 residu berkorelasi; Stage 9.5/10.1 berisi 102 protein / 55.503 residu tetapi hanya 955 positif; Stage 10.1 tidak menambah protein | Tinggi | Stage 4 plan §6, Stage 6 report, §19, §20 | **TETAP:** diakui eksplisit (butir F); benchmark dikunci dan Stage 10.1 belum menjadi validasi eksternal |
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
| C14 | **Dependensi ML belum dipin.** scikit-learn, xgboost, scipy, dan numpy verifikasi dipasang sementara di luar `.venv`; tidak ada di `requirements.txt` | Sedang (reproducibility) | `BENCHMARK_DATASET_LOCK.md` §8 | Tercatat; keputusan pin dependency = user |
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
| C25 | **Fitur spasial tidak independen dari fitur yang sudah ada.** `spatial_plddt_mean_8a` berkorelasi sangat tinggi dengan `plddt_ca` (Pearson 0,9885; Spearman 0,9838); `spatial_pae_mean_8a` berkorelasi peringkat dengan `pae_local_mean_k10` (Spearman 0,8800); `spatial_density_8a` berkorelasi sedang dengan pLDDT (Pearson 0,6568). Radius 8,0 Å dipilih tetap, tanpa uji sensitivitas radius. Fitur dihitung dari struktur prediksi AFDB, bukan struktur eksperimen. | Sedang (interpretasi fitur) | Audit Stage 10.1 §20.2–§20.4 | **TERCATAT:** ketiga fitur dilaporkan sebagai turunan struktur; importance dan korelasi didokumentasikan; tidak diklaim sebagai informasi biologis independen. Uji sensitivitas radius dan struktur eksperimen belum dilakukan |
| C26 | **`download/` tidak berisi file PDB/CIF/PAE.** Permintaan Stage 10.1 mengasumsikan file struktur ada di `download/`, tetapi folder itu hanya berisi CSV/Markdown/notebook. Ekstraksi memakai cache audit Stage 9.4 di luar tracked tree (102 CIF + 102 PAE + 102 API JSON); tidak ada unduhan baru. | Rendah–sedang (provenance) | Audit Stage 10.1 §20.3, D12 | **TERCATAT:** seluruh 55.503 baris dicocokkan ulang dengan CIF/PAE sebelum fitur ditulis; hash input per protein dicatat di audit JSON temporer. Cache mentah tidak di-commit |

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

Catatan: satu-satunya artefak non-deterministik yang diketahui adalah
`data/alphafold_db/metadata/download_log.txt` (timestamp + path absolut lokal) — file
log, bukan output dataset, dan tidak dipakai sebagai input analisis.

---

## 15. Current Project Position

**Posisi: Stage 10.1 dieksekusi dan diaudit — dataset spasial 102 protein /
55.503 residu tersedia; benchmark Stage 8.2 tetap terkunci dan tidak berubah.**

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
- **Dampak fitur spasial:** vs Stage 9.5, XGB median ROC +0,0415 / PR +0,0252,
  pooled ROC +0,0200 / PR +0,0119; RF median ROC +0,0394 / PR +0,0162, pooled ROC
  +0,0092 / PR +0,0060. Within-protein z-scored ROC naik 0,6877 → 0,7156 (XGB) dan
  0,6891 → 0,7059 (RF), jadi kenaikan bukan hanya urutan antar-protein; namun
  between-protein AUC tetap ~0,78 dan tidak ada holdout eksternal (C23, C25, §20.6).
- Dataset AFDB, dataset Stage 7, dan lock Stage 8.2 **tidak diubah**; Stage 9.2,
  9.3, 9.4, 9.5, dan 10.1 adalah artefak baru.
- Gate berikutnya: putuskan status benchmark Stage 9.3–10.1, lalu validasi
  eksternal dan kalibrasi lintas-protein. Belum ada klaim generalisasi.

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
  geometri 3D murni dan bukan dari kolinearitas dengan pLDDT/PAE lama; radius 8,0 Å
  adalah pilihan yang optimal (tidak ada sweep radius); kalibrasi probabilitas
  lintas-protein; representativitas 102 protein.
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

## 21. Recommended Next Step — External Validation

**Rekomendasi: validasi eksternal dan kalibrasi lintas-protein, bukan klaim
generalisasi.**

Fokus:

1. **Validasi eksternal** pada protein yang tidak dipakai memilih fitur; uji kalibrasi
   probabilitas lintas-protein.
2. **Pertahankan Stage 8.2 tetap frozen.** Jangan mengubah
   `stage7_processed_dataset.csv` atau `BENCHMARK_DATASET_LOCK.md`.
3. **Pin dependensi ML** (`scikit-learn`, `xgboost`, `scipy`) di `requirements.txt`
   hanya setelah persetujuan user.
4. **P11532 sudah dikeluarkan di Stage 9.5** (C21 selesai untuk dataset bersih). Jika
   ingin dipakai lagi, rebuild dari sumber full-length yang selaras dengan sekuens
   kanonik dan jadikan artefak terpisah — jangan menyunting dataset bersih atau memakai
   525 baris isoform sebagai residu kanonik.
5. **Laporkan median + IQR dan pooled secara terpisah;** sediakan fold `unevaluable`
   untuk protein tanpa positif (24 protein di Stage 9.4; P01308 di Stage 9.2/9.3;
   GFP di Stage 8.2). Untuk Stage 9.3 dan 9.4, gunakan nilai reproduced, bukan nilai
   klaim yang tidak cocok (C20, C22).
6. **Metrik dataset bersih dan spasial sudah dihitung penuh.** Stage 9.5 (retraining
   tanpa P11532): XGB pooled ROC 0,7476 / PR 0,0640, median ROC 0,7371; RF pooled ROC
   0,7476 / PR 0,0608, median ROC 0,7330. Stage 10.1 (16 fitur): XGB pooled ROC
   0,7676 / PR 0,0759, median ROC 0,7786; RF pooled ROC 0,7568 / PR 0,0668, median ROC
   0,7724. Gunakan angka Stage 10.1 untuk model dengan fitur spasial, angka Stage 9.5
   sebagai pembanding fitur, dan angka Stage 9.4 hanya sebagai pembanding historis
   (C24).
7. **Putuskan status benchmark Stage 9.3, 9.4, 9.5, dan 10.1** (lock terpisah atau
   tetap sebagai artefak ekspansi) sebelum memakai metriknya sebagai pembanding resmi.
8. **Jangan memakai pooled ROC sebagai bukti generalisasi.** Laporkan juga metrik
   within-protein dan median per-protein; pooled ROC Stage 10.1 (0,7676/0,7568) masih
   dipengaruhi perbedaan antar-protein, sedangkan within-protein z-scored ROC
   0,7156/0,7059 masih di bawah pooled (C23, C25).
9. **Jadikan fitur spasial kandidat tetap, bukan kesimpulan.** Stage 10.1 adalah
   feature engineering pada dataset yang sama. Sebelum masuk benchmark baru, lakukan
   ablasi/sweep radius, uji stabilitas importance, dan validasi pada protein yang tidak
   dipakai memilih fitur (C25).

**Gate Stage 10.1:** jangan klaim generalisasi sebelum ada validasi eksternal dan
metrik yang direproduksi dari repo bersih. Stage 10.1 belum melewati gate itu; ia hanya
menambah fitur dan mengukur dampaknya pada LOGO-CV internal.

---

```
NEXT GATE:
STAGE 10.2+ — EXTERNAL VALIDATION + CROSS-PROTEIN CALIBRATION
(Stage 10.1 = feature engineering, bukan external validation)
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
