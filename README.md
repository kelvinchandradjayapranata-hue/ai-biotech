# AI + Biotech — Pipeline Analisis Protein

Project pembelajaran: menghubungkan prediksi struktur protein (AlphaFold) dengan
analisis data memakai Python — fondasi menuju dataset dan machine learning.

> **Status: Tahap 2-6 selesai — 7 protein AlphaFold DB tervalidasi; dataset fitur
> multi-protein 1098 residu x 29 kolom (3 identifier + 26 fitur), 24 test PASS.**
> Test Tahap 3 (20/20) dan Tahap 5 (16/16) tetap lulus. **Menunggu review Tahap 6;
> belum ada model ML.**
> Lihat *"Tahap 5 — unduhan & validasi dataset"*, *"Tahap 6 — ekstraksi fitur multi-protein"*,
> `docs/TAHAP_5_AFDB_DOWNLOAD_REPORT.md`, dan `docs/TAHAP_6_MULTI_PROTEIN_FEATURE_REPORT.md`.

---

## Pipeline

```
AlphaFold (prediksi struktur dari sekuens)
   |
   v
protein sequence  [input — mis. ubiquitin, 76 asam amino]
   |
   v
predicted structure  [model 3D + confidence: pLDDT, PAE, pTM]
   |
   v
file PDB / mmCIF  [unduhan hasil AlphaFold Server]
   |
   v
Python + BioPython  [membaca: chain -> residu -> atom]
   |
   v
structural analysis  [chains, residu, sekuens, komposisi, statistik pLDDT]   <-- src/analyze_protein.py
   |
   v
feature extraction   [76 residu x 28 kolom; + fitur turunan PAE/contact]   <-- src/extract_protein_features.py
   |
   v
machine learning     [TAHAP BERIKUTNYA — belum dibuat]
```

## Struktur folder

```
ai-biotech/
|-- data/          # input data (FASTA; arsip unduhan AlphaFold Server di data/alphafold_downloads/;
|                  #   dataset AlphaFold DB di data/alphafold_db/ - raw/ 14 file tervalidasi, v6)
|-- structures/    # file struktur hasil AlphaFold Server (ubiquitin_alphafold.cif)
|-- docs/          # dokumen rencana (DATASET_PLAN.md)
|-- notebooks/     # notebook pembelajaran
|-- src/           # script python
|-- results/       # output analisis (JSON/CSV/PNG; manifest dataset di results/dataset/)
|-- .venv/         # virtual environment (Python 3.12)
|-- requirements.txt
`-- README.md
```

## Setup (sekali saja)

Environment sudah dibuat (`.venv`, Python 3.12.10). Kalau perlu setup ulang di mesin lain:

```bat
cd D:\project\ai-biotech
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Menjalankan analisis sekuens (sudah bisa sekarang)

```bat
cd D:\project\ai-biotech
.venv\Scripts\activate
python src\analyze_protein.py --fasta data\ubiquitin_sequence.fasta
```

Output: ringkasan di layar + file JSON/CSV di `results/`.

## Menjalankan analisis struktur (data sudah tersedia)

```bat
python src\analyze_protein.py                     # scan otomatis folder structures/
python src\analyze_protein.py structures\ubiquitin_alphafold.cif
python src\analyze_protein.py --help              # semua opsi
```

## Notebook

`notebooks\01_first_protein_analysis.ipynb` — penjelasan konsep (asam amino, sekuens,
struktur, pLDDT, PAE, pTM) + demo membaca data dengan Python.

- **VS Code:** buka file notebook → pilih kernel **.venv (Python 3.12.x)** → Run All.
- **Browser (opsional):** `pip install jupyter` lalu `jupyter notebook`.

## Tahap 3 — feature extraction (dataset per-residu)

Mengubah prediksi struktur + confidence menjadi tabel numerik siap dianalisis/ML:

```bat
python src\extract_protein_features.py     # buat dataset dari struktur + full_data json
python src\test_protein_features.py        # validasi dataset (exit 0 = semua PASS)
```

Output di `results/`:

- `ubiquitin_residue_features.csv` — 76 baris (1 per residu) x 28 kolom feature
- `ubiquitin_structure_features.json` — metadata, definisi + unit tiap kolom, statistik PAE/contact
- `ubiquitin_plddt_per_residue.png` — grafik pLDDT per residu
- `ubiquitin_pae_heatmap.png` — heatmap PAE 76x76 dari data model_0

Script hanya **membaca** file mentah (struktur CIF, full_data json, FASTA) — tidak
mengubahnya. Semua fitur turunan (PAE/contact) punya rumus + ambang eksplisit di JSON.

### Konsep singkat

- **Dataset per-residu (residue-level dataset):** satu baris per asam amino. Tiap baris
  menggabungkan identitas (residu apa, posisi berapa), properti sekuens, koordinat 3D,
  dan nilai confidence — bentuk data yang cocok untuk ML tabular nanti.
- **pLDDT (0-100, per residu):** estimasi keyakinan model terhadap struktur lokal tiap
  residu. Kasar: >90 sangat tinggi, 70-90 tinggi, 50-70 rendah, <50 sangat rendah.
- **PAE (Predicted Alignment Error, Angstrom):** matriks 76x76 — estimasi error posisi
  residu i jika struktur di-align pada residu j. Di sini PAE diringkas per-residu dengan
  rumus eksplisit (`pae_mean_row`, `pae_mean_col`, `pae_local_mean_k10` — lihat definisi
  kolom di `ubiquitin_structure_features.json`).
- **Contact probability:** probabilitas kontak antar-token hasil prediksi (0-1). Fitur
  turunannya memakai ambang eksplisit 0.50 (`n_high_conf_contacts`) — ini prediksi model,
  bukan kontak hasil eksperimen.
- **Confidence model != validasi eksperimen:** pLDDT/pTM/PAE tinggi berarti model
  konsisten secara internal, BUKAN berarti struktur terbukti benar di dalam sel atau
  fungsinya terbukti. Verifikasi nyata butuh eksperimen (kristalografi, NMR, cryo-EM, dll).

## Tahap 4 — dataset dari AlphaFold DB (persiapan, belum unduh)

**Pemisahan sumber data (penting):**

- **AlphaFold Server** (Tahap 2-3, `structures/ubiquitin_alphafold.cif`) = spesimen
  pembelajaran & referensi. Outputnya **TIDAK dipakai sebagai training data ML.**
- **AlphaFold DB** (https://alphafold.ebi.ac.uk, EMBL-EBI & Google DeepMind) =
  kandidat sumber dataset ML. Lisensi **CC BY 4.0**; wajib atribusi EMBL-EBI,
  Google DeepMind, UniProt. Rencana lengkap + kandidat protein: `docs/DATASET_PLAN.md`.

```bat
python src\prepare_dataset.py          # bangun manifest dari metadata kandidat (tanpa unduhan)
python src\test_dataset_manifest.py    # validasi manifest (exit 0 = semua PASS)
```

Output: `results/dataset/dataset_manifest.csv` — 7 kandidat protein (single-chain,
105-238 aa, 6 kategori fungsi; accession & panjang terverifikasi di UniProtKB +
AlphaFold DB API).

**Status:** disetujui (Tahap 4 PASS/APPROVED) — unduhan dilakukan di Tahap 5.

## Tahap 5 — unduhan & validasi dataset (selesai, menunggu review)

```bat
python src\download_afdb_dataset.py    # unduh 14 file (7 CIF + 7 PAE) dari API resmi — sudah dijalankan
python src\validate_afdb_dataset.py    # validasi CIF/PAE + manifest unduhan (offline)
python src\test_afdb_download.py       # 16 test integritas (exit 0 = semua PASS)
python src\test_dataset_manifest.py    # test Tahap 4 (masih 12 test PASS)
```

Hasil: `data/alphafold_db/raw/` (14 file, semua v6), checksums di
`data/alphafold_db/metadata/download_checksums.csv`, validasi di
`results/dataset/{structure_validation,pae_validation,dataset_download_manifest}.csv`.
Laporan lengkap: `docs/TAHAP_5_AFDB_DOWNLOAD_REPORT.md`.

## Tahap 6 — ekstraksi fitur multi-protein (selesai, menunggu review)

Memvalidasi pipeline ekstraksi Tahap 3 pada 7 protein AFDB yang sudah frozen di Tahap 5
(raw CIF/PAE, checksum, manifest **tidak diubah**; tahap ini offline terhadap dataset):

```bat
python src\extract_multi_protein_features.py    # baca manifest DOWNLOADED_VALIDATED + file mentah
python src\test_multi_protein_features.py       # 24 test integritas (exit 0 = semua PASS)
```

Output di `results/dataset/`:

- `multi_protein_residue_features.csv` — 1098 baris (residu) x 29 kolom = 3 identifier protein + 26 fitur
- `multi_protein_summary.csv` — ringkasan 7 protein (semua status PASS)
- `multi_protein_structure_features.json` — metadata + definisi kolom + dokumentasi fitur yang dikecualikan
- `multi_protein_plddt_overview.png`, `multi_protein_pae_overview.png` — visualisasi 7 protein

Catatan skema: referensi Tahap 3 = 28 kolom; 2 kolom turunan contact
(`contact_prob_sum`, `n_high_conf_contacts`) bergantung pada `contact_probs` AlphaFold
Server yang tidak tersedia di dataset AFDB — kolom ini **dikeluarkan** (bukan diisi
NaN/proxy, bukan didefinisikan ulang) dan didokumentasikan eksplisit di JSON.
26 fitur lainnya tidak diubah. Output reproducible byte-identical.
Laporan: `docs/TAHAP_6_MULTI_PROTEIN_FEATURE_REPORT.md`.

## Batasan (baca dulu)

- Ini **bukan drug discovery**. Tidak ada docking, simulasi dinamika molekuler,
  skrining senyawa, atau eksperimen basah di project ini.
- Hasil AlphaFold adalah **prediksi/model**, bukan kebenaran biologis.
  Skor pLDDT/pTM tinggi tidak otomatis berarti struktur benar di dalam sel.
- Tujuan project: belajar membangun pipeline data yang benar, bisa dijalankan
  ulang, dan jujur soal batasannya.

## Roadmap

| Tahap | Isi | Status |
|---|---|---|
| 1 | Scaffold + analisis sekuens | selesai |
| 2 | Analisis struktur AlphaFold (chain/residu/pLDDT) | selesai (2026-10-05) |
| 3 | Feature extraction per-residu | selesai — 76 residu x 28 feature, 20 test PASS |
| 4 | Dataset kecil — rencana (AlphaFold DB, 7 kandidat) | selesai — APPROVED |
| 5 | Unduhan & validasi dataset (7 protein) | selesai — 14/14 file v6 tervalidasi, 16 test PASS |
| 6 | Ekstraksi fitur multi-protein (7 protein AFDB) | selesai (2026-10-05) — 1098 residu x 29 kolom, 24 test PASS; menunggu review |
| 7 | Eksperimen ML sederhana | belum — menunggu review Tahap 6 |
#   a i - b i o t e c h  
 