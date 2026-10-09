# PROJECT STATUS — AI-BIOTECH

**Dokumen ini adalah single source of truth status project.**
Dibuat: 2026-10-05. Sumber: README.md, `docs/` (DATASET_PLAN.md, TAHAP_5, TAHAP_6),
serta manifest/hasil yang ada di `results/` dan `data/`. Tidak ada file Stage 1–6 yang
diubah, tidak ada eksperimen baru dijalankan, tidak ada unduhan dilakukan.

---

```
PROJECT STATUS:
STAGE 1–6 COMPLETE
DATA PIPELINE: VALIDATED
BIOLOGICAL ML: NOT YET STARTED
```

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

Yang **BELUM tercapai** (dan tidak diklaim):

- **Belum ada machine learning sama sekali.** Tidak ada training, validasi model,
  klasifikasi, regresi, embedding, atau clustering.
- **Belum ada label biologis (y) yang dipilih.**
- **Belum ada bukti predictive power** dari fitur yang diekstrak.
- **1098 residu / 7 protein bukan dataset ML yang memadai** — terlalu kecil, terlalu
  homogen (5/7 protein manusia, semua globular/larut, semua monomer).

Posisi jujur: **infrastruktur data selesai dan tervalidasi; pertanyaan biologis dan
ML belum dimulai.** Stage 6 masih menunggu review user; sesuai stop condition Stage 6,
tidak ada langkah lanjutan yang dijalankan tanpa review.

---

## 2. Overall Project Status

| Dimensi | Status | Bukti ringkas |
|---|---|---|
| Engineering / data pipeline | **BERHASIL** | 4 script utama + 4 test suite, semua exit 0 |
| Penyediaan struktur AlphaFold | **BERHASIL** | 14/14 file AFDB v6, 0 gagal, checksum cocok |
| Validasi integritas data | **BERHASIL** | SHA256 dihitung ulang & cocok; sekuens 7/7 MATCH |
| Feature extraction | **BERHASIL** | 1098 × 29 kolom, 24/24 test PASS |
| Reproducibility | **BERHASIL** | Output dataset byte-identical antar-run |
| Predictive biological AI / ML | **BELUM DIMULAI** | Tidak ada script ML di `src/`, tidak ada model |
| Label biologis (y) | **BELUM ADA** | Baru usulan arah di DATASET_PLAN.md §9; belum diputuskan |
| Klaim ilmiah/biologis | **TIDAK ADA (sengaja)** | Semua laporan menyatakan fitur = prediksi model |

Ringkas: **A/B/C tercapai; D/E/F/G belum dan diakui eksplisit** (lihat bagian 12).

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

**Status: PASS WITH CONCERNS** (COMPLETE + 24/24 test PASS; menunggu review user)

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

**Batas tegas antar baris:** sampai Stage 6, semua capaian bersifat
**engineering + integritas data + ekstraksi fitur**. Tidak ada satu pun baris di tabel
ini yang merupakan hasil ML atau klaim biologis.

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
| `results/` | `01_first_protein_analysis.executed.ipynb`, `notebook_plot_1.png` | output notebook |
| `notebooks/` | `01_first_protein_analysis.ipynb` | materi pembelajaran |

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

**Tidak ada script ML di `src/`.** Tidak ada PyTorch/TensorFlow/CUDA.
Environment: `.venv` Python **3.12.10**; `requirements.txt` hanya biopython, pandas,
numpy, matplotlib, ipykernel, nbclient.

### 10.4 SHA256 terverifikasi (top-level)

Dihitung ulang **read-only** saat dokumen ini dibuat dan **cocok persis** dengan nilai
yang tercatat di report/manifest:

```
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

**D. Predictive biological AI BELUM diuji — TIDAK ADA BUKTI.**
Tidak ada model, tidak ada training, tidak ada split train/test, tidak ada metrik
evaluasi. Tidak ada satu pun artefak di `src/` atau `results/` yang merupakan output ML.

**E. Tidak ada klaim bahwa fitur saat ini sudah punya predictive power — TIDAK DIKLAIM.**
Fitur yang ada adalah deskriptor struktural/geomik turunan prediksi (identitas residu,
hidropati, muatan, koordinat, pLDDT, ringkasan PAE). Belum ada uji terarah apakah
fitur-fitur ini dapat memprediksi apa pun. Korelasi/label belum pernah diuji.

**F. 7 protein / 1.098 residu belum merupakan dataset ML yang memadai — DIAKUI.**
Alasannya: (1) hanya 7 sampel protein — jauh di bawah kebutuhan klaim statistik apa pun;
(2) 5 dari 7 protein manusia → bias taksonomi; (3) semua globular/larut, tidak ada
protein membran atau daerah tak terstruktur besar; (4) semua monomer, padahal sebagian
protein in vivo berinteraksi (mis. SOD1); (5) 1098 baris residu **bukan 1098 sampel
independen** — residu dalam satu protein sangat berkorelasi (struktur, sekuens, dan
confidence-nya saling bergantung). Menghitung "N = 1098" sebagai ukuran sampel
statistik adalah keliru.

**G. Stage 7 berikutnya adalah menentukan biological question dan independent label y —
BELUM DIMULAI.**
`DATASET_PLAN.md` §9 baru mencantumkan *usulan arah* (kategori fungsi dari manifest
sebagai ilustrasi; opsi GO terms / EC numbers di masa depan) — **belum diputuskan**,
dan 7 sampel dinilai sendiri oleh dokumen itu sebagai terlalu sedikit untuk klasifikasi.

Tambahan yang juga **belum** terbukti/dilakukan:
- Tidak ada validasi terhadap struktur eksperimen (PDB) — tidak ada RMSD, tidak ada
  perbandingan dengan kristalografi/NMR/cryo-EM.
- Tidak ada klaim bahwa pLDDT/PAE tinggi berarti struktur benar di dalam sel.
- Tidak ada docking, molecular dynamics, skrining senyawa, atau eksperimen basah.
- Tidak ada model prediksi fungsi, tidak ada "penemuan".

---

## 13. Known Limitations / Concerns

Diurutkan dari yang paling berdampak pada tahap berikutnya.

| # | Concern | Tingkat | Sumber | Status penanganan |
|---|---|---|---|---|
| C1 | **Skema Stage 6 = 26 fitur, bukan 28.** `contact_prob_sum` & `n_high_conf_contacts` dikeluarkan karena `contact_probs` tidak tersedia di AFDB | Tinggi (mempengaruhi desain fitur ML) | Stage 6 report §5, §10.1 | Didokumentasikan eksplisit di JSON (`schema.excluded_features`); **tidak** diimputasi/proksi/didefinisikan ulang. Keputusan perlakuan = user |
| C2 | **Redundansi pLDDT AFDB.** CIF AFDB menulis pLDDT per-residu ke semua atom → di 1098 baris: `plddt_atom_std = 0`, `plddt_atom_mean = min = max = plddt_ca`. 4 kolom `plddt_atom_*` redundan dengan `plddt_ca` | Tinggi (risiko multikolinearitas sempurna bila dipakai ML apa adanya) | Stage 6 report §10.2 | Dikunci test E5 dan didokumentasikan di JSON; **tidak** diperbaiki diam-diam. Keputusan = user |
| C3 | **Skala dataset tidak memadai untuk ML.** 7 protein / 1098 residu berkorelasi | Tinggi | Stage 4 plan §6, Stage 6 report | Diakui eksplisit (butir F) |
| C4 | **Belum ada label (y).** Tidak ada target prediksi yang dipilih | Tinggi (blocker untuk ML) | `DATASET_PLAN.md` §9 | Baru usulan arah; belum diputuskan |
| C5 | **Koordinat mentah tidak invariant rotasi/translasi** (`ca_x/y/z`, `centroid_*`) | Sedang | Stage 3 JSON, `DATASET_PLAN.md` §8 | Sudah dicatat sebagai catatan penting untuk ML; alternatif fitur jarak/turunan belum dibuat |
| C6 | **Versi AFDB v6 dapat berubah** di masa depan | Sedang (eksternal) | Stage 5 report §14.2 | SHA256 tercatat sebagai titik referensi; perubahan server akan terdeteksi sebagai hash berbeda |
| C7 | **Dua sistem checksum berbeda** (AFDB = MD5 32 hex; UniProt = CRC64 16 hex) | Rendah (risiko salah baca manual) | Stage 5 report §11, §14.1 | Keduanya diverifikasi cocok; terdokumentasi |
| C8 | **PAE asimetris** (maks \|PAE − PAEᵀ\| = 19–24 Å di 7/7 protein) | Rendah (wajar matematis) | Stage 6 report §10.3 | Arah matriks dipertahankan; test check 10 memverifikasi tidak ada transpose tak sengaja |
| C9 | **Campuran int/float di sel PAE** (mis. 0, 31 bercampur float) | Rendah (karakter data) | Stage 5 report §14.3 | Tidak diubah; nilai min/max di `pae_validation.csv` hanya deskriptif |
| C10 | **Semua fitur = prediksi model**, bukan pengukuran eksperimen | Fundamental (melekat) | Semua report | Dinyatakan berulang di README, JSON, dan kedua report |
| C11 | **RNase1 memakai prekursor 1–150** (termasuk signal peptide), bukan RNase A mature 124 residu | Rendah | `dataset_manifest.csv` notes, Stage 5 report §14.4 | Tercatat di manifest |
| C12 | **Ligand/ion/kovalen tidak dimodelkan** (heme pada myoglobin & cytochrome c; Cu/Zn pada SOD1; kromofor GFP terbentuk post-translasi) | Sedang (interpretasi) | `dataset_manifest.csv` notes, `DATASET_PLAN.md` §6 | Tercatat per baris di manifest |

---

## 14. Current Reproducibility Status

**Status: KUAT untuk data & fitur; BELUM TERUJI untuk ML (belum ada ML).**

| Aspek | Status | Bukti |
|---|---|---|
| Ekstraksi fitur deterministik | **Ya** | Stage 6 report §9: dijalankan ≥3× (2 manual + 1 oleh test check 15 ke direktori temporer), **semua 5 output byte-identical** |
| Bebas timestamp/seed/path absolut di output | **Ya** | Diverifikasi regex oleh test Stage 6 check 17 (CSV: LF + UTF-8; PNG: matplotlib Agg; JSON: path relatif POSIX) |
| Integritas input dikunci | **Ya** | Extractor memverifikasi SHA256 tiap file mentah terhadap manifest sebelum diproses; test memverifikasi ulang (E3/E4) |
| Checksum dapat diverifikasi ulang oleh siapa pun | **Ya** | `download_checksums.csv` + test Stage 5 menghitung ulang dari disk |
| Test suite saling menjaga | **Ya** | Test Stage 6 (check 18 & 19) menjalankan ulang test Stage 3 & Stage 5; keduanya tetap lulus |
| **Verifikasi dalam dokumen ini** | **Parsial** | Hash top-level (bagian 10.4) **dihitung ulang read-only dan cocok persis**. **Test suite TIDAK dijalankan ulang** saat dokumen ini dibuat, sesuai aturan "jangan menjalankan eksperimen baru" — status PASS yang dilaporkan berasal dari report tertulis |
| Reproducibility ML | **Tidak berlaku** | Belum ada model, split, atau metrik |

Catatan: satu-satunya artefak non-deterministik yang diketahui adalah
`data/alphafold_db/metadata/download_log.txt` (timestamp + path absolut lokal) — file
log, bukan output dataset, dan tidak dipakai sebagai input analisis.

---

## 15. Current Project Position

**Posisi: akhir Stage 6 — BERHENTI menunggu review user.**

- Stage 1–6 selesai secara teknis. **Stage 6 secara eksplisit masih "menunggu review"**
  (dinyatakan di README dan di report Stage 6 §11).
- Stop condition Stage 6 yang berlaku: **tidak lanjut ke ML, tidak memperbesar dataset,
  tidak mencari label biologis baru, tidak membuat model.**
- Dataset AFDB **frozen**: raw CIF/PAE, checksum, dan `dataset_download_manifest.csv`
  tidak diubah oleh Stage 6.
- Belum ada pertanyaan biologis yang dirumuskan, belum ada label, belum ada model.
- Gate berikutnya bersifat **desain ilmiah**, bukan pekerjaan engineering lanjutan:
  definisi pertanyaan + target sebelum menyentuh ML.

---

## 16. Recommended Next Step — Stage 7

**Stage 7 yang direkomendasikan: DATASET & LABEL DESIGN (bukan training).**

Fokus Stage 7 adalah **menentukan pertanyaan biologis dan label independen (y)** sebelum
satu baris pun kode ML ditulis. Usulan cakupan:

1. **Tetapkan pertanyaan biologis eksplisit** — apa yang ingin diprediksi, pada level
   apa (per-protein atau per-residu), dan mengapa itu menarik.
2. **Pilih dan definisikan label y dari sumber resmi** (mis. anotasi UniProtKB: GO terms
   atau EC numbers), termasuk keputusan desain: multi-label vs single-label, hierarki,
   keseimbangan kelas, dan status lisensi. Catatan: `DATASET_PLAN.md` §9 sudah menandai
   `category` (6 kategori) sebagai kandidat **ilustrasi saja** — 7 sampel terlalu sedikit
   untuk klasifikasi.
3. **Selesaikan kebijakan fitur** atas concern C1 dan C2: apakah kolom `plddt_atom_*`
   yang redundan dibuang/dikonsolidasi, dan bagaimana posisi resmi soal 26 vs 28 fitur
   dicatat sebagai keputusan (bukan perubahan diam-diam).
4. **Tentukan strategi independensi data** — jika tetap per-residu, jelaskan dan
   tangani korelasi antar-residu dalam satu protein (butir F); pertimbangkan split
   per-protein, bukan per-residu.
5. **Tentukan skala dataset minimum** untuk membuat klaim apa pun, dan putuskan apakah
   perlu memperbesar dataset AFDB (keputusan user — Stage 6 melarangnya tanpa review).

**Gate Stage 7:** jangan mulai training/model sebelum (a) review Stage 6 selesai,
(b) pertanyaan biologis tertulis, dan (c) definisi label y final beserta sumbernya.

---

```
NEXT GATE:
STAGE 7 — DATASET & LABEL DESIGN
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
