# PROJECT STATUS — AI-BIOTECH

**Dokumen ini adalah single source of truth status project.**
Dibuat: 2026-10-05. Sumber: README.md, `docs/` (DATASET_PLAN.md, TAHAP_5, TAHAP_6),
serta manifest/hasil yang ada di `results/` dan `data/`. Tidak ada file Stage 1–6 yang
diubah, tidak ada eksperimen baru dijalankan, tidak ada unduhan dilakukan.

---

```
PROJECT STATUS:
STAGE 1–9.3 AUDITED — STAGE 8.2 BENCHMARK LOCKED
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
> Bagian 1, 2, 9, 10, 11, 12, 13, 14, 15, 16, 17 (baru), dan 18 di bawah sudah
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

Yang **BELUM tercapai** (dan tidak diklaim):

- **Belum ada bukti predictive power yang umum.** Baseline Stage 8.2 lemah dan sangat
  heterogen antar-protein: pooled ROC-AUC 0,5368 (XGB) / 0,5062 (RF), sedangkan pooled
  PR-AUC 0,0916 / 0,1028 terhadap baseline prevalensi 0,0419. Pooled mendekati acak;
  median per-fold yang lebih tinggi tidak boleh dibaca sebagai kemampuan generalisasi.
- **Skala belum memadai** — 7 protein, 1098 residu berkorelasi, 46 positif. Ini bukan
  1098 sampel independen, dan 5/7 protein manusia serta semuanya globular/larut/monomer.
- **Belum ada validasi eksternal** pada protein baru, struktur eksperimen, atau dataset
  independen. Belum ada uji kalibrasi probabilitas lintas-protein.
- **Label masih terbatas pada A+B.** Belum ada label multi-kelas, GO terms, EC numbers,
  atau skema label alternatif.
- **Stage 9.2 dan Stage 9.3 bukan validasi eksternal dan bukan klaim generalisasi.**
  14 protein / 129 positif masih kecil dan tidak ada holdout eksternal. Stage 9.3 sudah
  memakai definisi fitur frozen, tetapi pooled ROC-AUC ≈0,64–0,66 pada dataset ini
  belum membuktikan kemampuan prediksi pada protein di luar dataset.

Posisi jujur: **infrastruktur data selesai dan tervalidasi; benchmark ML baseline sudah
ada dan terverifikasi, ditambah ekspansi Stage 9.2 dan realignment Stage 9.3 yang nyata
dan diaudit — tetapi belum ada bukti generalisasi biologis.** Fokus berikutnya adalah
validasi eksternal dan kalibrasi lintas-protein — bukan mengklaim performa.

---

## 2. Overall Project Status

| Dimensi | Status | Bukti ringkas |
|---|---|---|
| Engineering / data pipeline | **BERHASIL** | 4 script utama + 4 test suite, semua exit 0 |
| Penyediaan struktur AlphaFold | **BERHASIL** | 14/14 file AFDB v6, 0 gagal, checksum cocok |
| Validasi integritas data | **BERHASIL** | SHA256 dihitung ulang & cocok; sekuens 7/7 MATCH |
| Feature extraction | **BERHASIL** | 1098 × 29 kolom, 24/24 test PASS |
| Reproducibility | **BERHASIL** | Output dataset byte-identical antar-run |
| Predictive biological AI / ML | **BASELINE ADA; GENERALISASI BELUM** | Stage 8.2 LOGO-CV direproduksi; pooled ROC 0,5368/0,5062; median/IQR di `BENCHMARK_DATASET_LOCK.md` |
| Label biologis (y) | **ADA — A+B** | `target_y` = UniProt Active site + Binding site; 46 positif (Stage 7), 129 positif (Stage 9.2/9.3); audit label 0 mismatch di ketiga dataset |
| Ekspansi dataset (Stage 9.2) | **AUDITED — REAL AFDB, DENGAN CATATAN** | 14 protein / 3.960 residu; fitur struktural & label cocok dengan sumber; 2 definisi fitur menyimpang dari Stage 8.2 (§16) |
| Realignment dataset (Stage 9.3) | **AUDITED — DEFINISI FROZEN** | 14 protein / 3.960 residu; H = `basic`; `pae_local_mean_k10` = `\|i-j\| ≤ 10, j ≠ i`; 0 mismatch fitur/label; median/pooled/gain reproduce, IQR PR tidak (§17) |
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

**Batas tegas antar baris:** sampai Stage 6, semua capaian bersifat
**engineering + integritas data + ekstraksi fitur**. Stage 7 menambahkan **benchmark
terkunci** (dataset + label), dan Stage 8.2 menambahkan **baseline ML yang
direproduksi**. Stage 9.2 menambahkan **ekspansi dataset nyata yang diaudit**; Stage 9.3
merekonstruksinya dengan **definisi fitur frozen**. Keduanya belum menjadi benchmark
terkunci dan belum mengubah status generalisasi. Tidak ada satu pun baris di tabel ini
yang merupakan klaim biologis atau bukti generalisasi.

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
| `docs/` | **`BENCHMARK_DATASET_LOCK.md`** — kontrak benchmark: skema, label A+B, fold map, protokol & metrik Stage 8.2, kebijakan freeze | — |
| `results/` | `01_first_protein_analysis.executed.ipynb`, `notebook_plot_1.png` | output notebook |
| `notebooks/` | `01_first_protein_analysis.ipynb` | materi pembelajaran |

Catatan Stage 9.2/9.3: file mentah audit AFDB (28 file CIF/PAE, ~9,3 MB) dan
`download/stage9_uniprot_metadata.csv` (15 protein, 4.124 baris) **tidak di-commit**;
hanya `stage9_processed_dataset.csv` dan `stage93_realigned_dataset.csv` yang
dipromosikan ke `results/dataset/`. Audit dilakukan independen terhadap AFDB/UniProt
(bukti di §16 dan §17).

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

**Tidak ada script ML di `src/`.** Baseline Stage 8.2 dijalankan dengan harness
verifikasi eksternal (temporary, di luar repo); belum ada training script yang
di-commit. Tidak ada PyTorch/TensorFlow/CUDA.
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

**D. Predictive biological AI sudah diuji sebagai baseline, tetapi belum terbukti
bergeneralisasi.**
Stage 8.2 LOGO-CV sudah dijalankan dan direproduksi (median/IQR dan pooled di
`BENCHMARK_DATASET_LOCK.md`). Namun pooled ROC-AUC mendekati acak (0,5368 XGB / 0,5062
RF), variasi antar-fold sangat besar, dan tidak ada validasi eksternal. Yang terbukti
adalah **reproducibility protokol dan angka baseline**, bukan predictive power biologis.

**E. Tidak ada klaim bahwa fitur saat ini sudah punya predictive power biologis —
TIDAK DIKLAIM.**
Fitur yang ada adalah deskriptor struktural/geomik turunan prediksi (identitas residu,
hidropati, muatan, koordinat, pLDDT, ringkasan PAE). Uji baseline Stage 8.2 menunjukkan
sinyal lemah dan heterogen; hasil itu tidak boleh dibaca sebagai kemampuan model
memprediksi fungsi protein pada umumnya. Tidak ada klaim generalisasi.

**F. 7 protein / 1.098 residu belum merupakan dataset ML yang memadai — DIAKUI.**
Alasannya: (1) hanya 7 sampel protein — jauh di bawah kebutuhan klaim statistik apa pun;
(2) 5 dari 7 protein manusia → bias taksonomi; (3) semua globular/larut, tidak ada
protein membran atau daerah tak terstruktur besar; (4) semua monomer, padahal sebagian
protein in vivo berinteraksi (mis. SOD1); (5) 1098 baris residu **bukan 1098 sampel
independen** — residu dalam satu protein sangat berkorelasi (struktur, sekuens, dan
confidence-nya saling bergantung). Menghitung "N = 1098" sebagai ukuran sampel
statistik adalah keliru. Status 2026-10-20: benchmark sudah dikunci, tetapi
keterbatasan ini tetap; 46 positif pada 7 protein tidak cukup untuk klaim generalisasi.

**G. Stage 7 (label A+B) SELESAI; ekspansi dan pertanyaan biologis lanjutan BELUM.**
Stage 7 menetapkan label biner **Active site + Binding site** dan fold LOGO, lalu
Stage 8.2 menetapkan baseline. Pertanyaan yang lebih luas (GO terms, EC numbers,
multi-label) dan ekspansi 15–100+ protein **belum** dikerjakan; 7 sampel tetap terlalu
sedikit untuk klasifikasi umum. `DATASET_PLAN.md` §9 masih berupa usulan arah.

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
| C3 | **Skala dataset tidak memadai untuk ML.** 7 protein / 1098 residu berkorelasi | Tinggi | Stage 4 plan §6, Stage 6 report | **TETAP:** diakui eksplisit (butir F); benchmark dikunci tetapi belum generalisasi |
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

Catatan: satu-satunya artefak non-deterministik yang diketahui adalah
`data/alphafold_db/metadata/download_log.txt` (timestamp + path absolut lokal) — file
log, bukan output dataset, dan tidak dipakai sebagai input analisis.

---

## 15. Current Project Position

**Posisi: Stage 9.3 dieksekusi dan diaudit — ekspansi AFDB nyata sudah memakai
definisi fitur frozen; benchmark Stage 8.2 tetap terkunci dan tidak berubah.**

- Stage 1–6 selesai dan terdokumentasi; concern C1, C2, C4, dan C5 sudah ditutup
  untuk benchmark (C3 tetap).
- Stage 7 selesai: dataset 1098 × 27, label A+B, 7-fold LOGO, dikunci dengan SHA256.
- Stage 8.2 selesai dan direproduksi: XGB cocok persis, RF dalam toleransi kecil;
  median/IQR + pooled tercatat di `docs/BENCHMARK_DATASET_LOCK.md`.
- Stage 9.2 selesai sebagai ekspansi nyata: 3.960 residu × 12 kolom, 14 protein,
  129 positif; fitur struktural dan label terverifikasi terhadap AFDB/UniProt.
- **Stage 9.3 menyelesaikan deviasi C16–C17:** `pae_local_mean_k10` memakai
  `|i-j| ≤ 10, j ≠ i`, histidin = `basic`; seluruh fitur dan label cocok
  3.960/3.960, dan `target_y` identik dengan Stage 9.2.
- Metrik Stage 9.3: median/pooled/gain reproduce; IQR PR yang dilaporkan tidak
  reproduce (C20). Stage 9.3 tetap **bukan pengganti** benchmark Stage 8.2.
- Dataset AFDB, dataset Stage 7, dan lock Stage 8.2 **tidak diubah**; Stage 9.2 dan
  Stage 9.3 adalah artefak baru.
- Belum ada bukti generalisasi; 14 protein / 129 positif masih terlalu kecil dan
  belum ada validasi eksternal.
- Gate berikutnya: validasi eksternal dan kalibrasi lintas-protein pada dataset
  Stage 9.3; keputusan lock benchmark baru tetap terbuka.

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

## 18. Recommended Next Step — External Validation

**Rekomendasi: validasi eksternal dan kalibrasi lintas-protein, bukan klaim
generalisasi.**

Fokus:

1. **Validasi eksternal** pada protein yang tidak dipakai memilih fitur; uji kalibrasi
   probabilitas lintas-protein.
2. **Pertahankan Stage 8.2 tetap frozen.** Jangan mengubah
   `stage7_processed_dataset.csv` atau `BENCHMARK_DATASET_LOCK.md`.
3. **Pin dependensi ML** (`scikit-learn`, `xgboost`, `scipy`) di `requirements.txt`
   hanya setelah persetujuan user.
4. **Laporkan median + IQR dan pooled secara terpisah;** sediakan fold `unevaluable`
   untuk protein tanpa positif (P01308 di Stage 9.2/9.3; GFP di Stage 8.2). Untuk
   Stage 9.3, gunakan nilai IQR reproduced, bukan nilai klaim.
5. **Putuskan status benchmark Stage 9.3** (lock terpisah atau tetap sebagai artefak
   ekspansi) sebelum memakai metriknya sebagai pembanding resmi.

**Gate Stage 9:** jangan klaim generalisasi sebelum ada validasi eksternal dan metrik
yang direproduksi dari repo bersih.

---

```
NEXT GATE:
STAGE 9.4 — EXTERNAL VALIDATION + CROSS-PROTEIN CALIBRATION
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
