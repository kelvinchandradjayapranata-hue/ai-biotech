# Laporan Tahap 6 — Ekstraksi Fitur Multi-Protein (Validasi Pipeline, Bukan ML)

Tanggal: 2026-10-05. Project: `D:\project\ai-biotech`.

## 1. STATUS

**COMPLETE — 7/7 protein diproses, 1098 baris residu x 29 kolom (3 identifier + 26 fitur),
24/24 test PASS; test Tahap 3 (20/20) dan Tahap 5 (16/16) tetap lulus.**

- Tahap ini adalah **validasi pipeline**: membuktikan extractor fitur Tahap 3 konsisten
  saat dijalankan pada 7 protein AlphaFold DB yang sudah tervalidasi di Tahap 5.
- **Bukan tahap ML.** Tidak ada training/klasifikasi/regresi/embedding/clustering, tidak
  ada klaim signifikansi biologis.
- Dataset Tahap 5 (raw CIF/PAE, checksum, `dataset_download_manifest.csv`) **tidak diubah
  sama sekali** (frozen). Tahap ini offline terhadap dataset.

## 2. INPUT DATA

- **Manifest (source of truth):** `results/dataset/dataset_download_manifest.csv` —
  hanya baris dengan status `DOWNLOADED_VALIDATED` yang diproses (7 protein).
- **Struktur:** 7 file CIF di `data/alphafold_db/raw/` (versi AFDB v6).
- **PAE:** 7 file PAE JSON di `data/alphafold_db/raw/`.
- **Metadata API:** `data/alphafold_db/metadata/api_<accession>.json` (untuk cross-check
  accession, chain, sekuens, checksum).
- Guard integritas: extractor memverifikasi SHA256 tiap file mentah terhadap manifest
  sebelum diproses; test memverifikasi ulang (check E3 + E4).
- Tidak ada unduhan baru, tidak ada protein tambahan, tidak memakai output AlphaFold Server.

## 3. PROTEIN COUNT

**7 protein** — tepat sesuai daftar yang disetujui, tidak kurang, tidak lebih:

P99999, P61626, P0DP23, P61823, P02144, P00441, P42212.

Diverifikasi oleh test check 1, 3, dan 14 (tidak ada protein/file ekstra di raw dir).

## 4. TOTAL RESIDUES

**1098 baris** = 105 + 148 + 149 + 150 + 154 + 154 + 238 — **sama persis dengan angka
ekspektasi spec** (tidak ada penyimpangan, tidak ada perbaikan diam-diam). Recompute
independen dari CIF + manifest oleh test check 5 & 6.

## 5. FEATURE SCHEMA

Skema referensi Tahap 3 (**28 kolom**) tetap dipertahankan sebagai historical/reference
schema dan **tidak diubah definisinya**. Skema dataset Tahap 6 = **3 kolom identifier
protein + 26 fitur = 29 kolom**:

- Identifier: `protein_id`, `uniprot_accession`, `afdb_id`
- 26 fitur: seluruh 28 kolom Tahap 3 **kecuali** 2 kolom turunan contact.

**Kolom yang dikecualikan (bukan diimputasi, bukan diproksikan):**

| Kolom | Definisi Tahap 3 | Alasan |
|---|---|---|
| `contact_prob_sum` | jumlah probabilitas kontak antar-token | butuh channel `contact_probs` |
| `n_high_conf_contacts` | jumlah kontak dengan probabilitas > 0.50 | butuh channel `contact_probs` |

Alasan teknis: 2 fitur tersebut bergantung pada `contact_probs` dari output **AlphaFold
Server**, sedangkan dataset frozen **AlphaFold DB tidak menyediakan channel contact**
(tidak ada di daftar file API maupun di file yang terunduh). Karena source channel
berbeda dan output AlphaFold Server tidak boleh dipakai ulang, kolom dikeluarkan.

Dokumentasi eksplisit tertanam di `multi_protein_structure_features.json`
(`schema.historical_reference`, `schema.excluded_features` dengan definisi/unit/ambang/
source_channel/alasan per kolom), termasuk pernyataan berikut (verbatim):

> Stage 3 reference schema contains 28 columns. Two contact-derived columns depend on
> AlphaFold Server `contact_probs`, which are not present in the frozen AlphaFold DB
> dataset. They are therefore excluded from the Stage 6 AFDB feature table rather than
> imputed, approximated, or silently redefined.

**26 fitur lainnya tidak diubah** — definisi, rumus, unit, dan pembulatan diimpor
verbatim dari konstanta `extract_protein_features.py` (Tahap 3), diverifikasi test check 12.

## 6. HASIL EKSTRAKSI

Dijalankan: `python src/extract_multi_protein_features.py` → **7/7 protein OK**,
1098 baris, tanpa FAIL. Output di `results/dataset/`:

| File | Isi | SHA256 |
|---|---|---|
| `multi_protein_residue_features.csv` | 1098 baris x 29 kolom | `390462a42d8befe5588b1019d51b4c4282433b0f712c4377e5191883983d3c1d` |
| `multi_protein_summary.csv` | ringkasan 7 protein, semua PASS | `111a9569ebf8990eeca19673215f1415e828cc00fd2f6c20a16e9048252660e1` |
| `multi_protein_structure_features.json` | metadata + definisi kolom + dokumentasi eksklusi | `7481765648cbd3b5c340cbacadc79635756d4867254b1003b335680a136587bc` |
| `multi_protein_plddt_overview.png` | pLDDT per residu, 7 protein | `365d29134a1ab55f5e3464e1155a89a2f04b747adbc7a762521f2d1b5ab23fc5` |
| `multi_protein_pae_overview.png` | heatmap PAE 7 protein | `3e0d1ef035271453d6aba4e54367df6ce0c41dad53693fe1444448a2b3ad77b0` |

Script: `src/extract_multi_protein_features.py` (baru; memakai ulang konstanta Tahap 3
via import — `extract_protein_features.py` **tidak diubah**).

## 7. HASIL PER PROTEIN

| UniProt | Protein | AFDB ID | Panjang expected | Panjang observed | Row count | Chain | Mean pLDDT | Dimensi PAE | Status |
|---|---|---|---|---|---|---|---|---|---|
| P99999 | Cytochrome c | AF-P99999-F1 | 105 | 105 | 105 | 1 (A) | 97.932 | 105 x 105 | PASS |
| P61626 | Lysozyme C | AF-P61626-F1 | 148 | 148 | 148 | 1 (A) | 94.073 | 148 x 148 | PASS |
| P0DP23 | Calmodulin | AF-P0DP23-F1 | 149 | 149 | 149 | 1 (A) | 85.241 | 149 x 149 | PASS |
| P61823 | Ribonuclease A | AF-P61823-F1 | 150 | 150 | 150 | 1 (A) | 94.043 | 150 x 150 | PASS |
| P02144 | Myoglobin | AF-P02144-F1 | 154 | 154 | 154 | 1 (A) | 97.178 | 154 x 154 | PASS |
| P00441 | Superoxide dismutase 1 | AF-P00441-F1 | 154 | 154 | 154 | 1 (A) | 97.925 | 154 x 154 | PASS |
| P42212 | GFP | AF-P42212-F1 | 238 | 238 | 238 | 1 (A) | 96.640 | 238 x 238 | PASS |

Semua protein: numbering residu 1..N berurutan (terverifikasi per protein, bukan
diasumsikan), sekuens CSV = CIF = `uniprotSequence` API, chain = `chainId` API,
tanpa HETATM. **Tidak ada protein gagal dan tidak ada masalah yang disembunyikan.**

## 8. HASIL TEST

`python src/test_multi_protein_features.py` → **SEMUA 24 TEST PASS**:

19 check utama (jumlah protein; accession unik; ketersediaan protein; rows > 0;
residue count vs manifest; total 1098; chain valid; numbering 1..N; sequence position
+ kecocokan sekuens; rekalkulasi PAE anti-transpose; tanpa NaN; schema 26 fitur + 3
identifier; 2 kolom contact absen + terdokumentasi; tanpa file/protein ekstra;
reproducible byte-identical; summary konsisten; tanpa timestamp/path absolut; Tahap 3
tetap lulus; Tahap 5 tetap lulus) + 5 check tambahan (E1 plddt_ca = B-factor CIF;
E2 total atom; E3 sha256 input = manifest; E4 MD5 sequenceChecksum;
E5 granularitas pLDDT AFDB terkunci).

- Test Tahap 3 (`src/test_protein_features.py`): **20/20 PASS** (tidak rusak).
- Test Tahap 5 (`src/test_afdb_download.py`): **16/16 PASS** (tidak rusak).

## 9. REPRODUCIBILITY

Extraction dijalankan ≥ 3x (2x manual + 1x oleh test check 15 ke direktori temporer):
**semua 5 output byte-identical setiap kali** (3 file data + 2 PNG). Tidak ada timestamp,
tanggal, random seed, path absolut lokal, atau metadata environment di output
deterministik (diverifikasi regex oleh check 17; CSV memakai lineterminator LF + UTF-8;
PNG deterministik via matplotlib Agg; JSON memakai path relatif POSIX).

## 10. CONCERNS

1. **2 fitur contact tidak portable (didokumentasikan, keputusan eksplisit user).**
   `contact_prob_sum` dan `n_high_conf_contacts` bergantung pada channel `contact_probs`
   AlphaFold Server; AFDB tidak menyediakannya. Kolom dikeluarkan — tidak diisi NaN,
   tidak diproksikan, tidak didefinisikan ulang. Dataset Tahap 6 punya 26 fitur, bukan 28.
2. **Granularitas pLDDT AFDB (karakteristik data, bukan error).** File CIF AFDB menulis
   pLDDT per-residu ke **semua atom** residu tersebut; akibatnya di seluruh 1098 baris:
   `plddt_atom_std = 0` dan `plddt_atom_mean = min = max = plddt_ca`. Ini berbeda dari
   full_data AlphaFold Server (pLDDT per-atom terpisah). Konsekuensi: 4 kolom
   `plddt_atom_*` redundan dengan `plddt_ca` di dataset ini. **Tidak diperbaiki/diubah
   diam-diam** — dikunci oleh test E5 dan didokumentasikan di JSON. Keputusan perlakuan
   untuk tahap berikutnya diserahkan ke user.
3. **PAE asimetris (wajar secara matematis).** `pae_mean_row` ≠ `pae_mean_col` di semua
   7 protein (asimetri maks |PAE − PAEᵀ| = 19–24 Å). Arah matriks dipertahankan apa
   adanya; test check 10 memverifikasi tidak ada transpose tak sengaja (anti-transpose).
4. **Semua fitur = prediksi model.** pLDDT/PAE adalah estimasi keyakinan model AlphaFold,
   bukan pengukuran eksperimen. Tidak ada klaim biologis di tahap ini.

## 11. NEXT STEP

**BERHENTI.** Menunggu review user atas hasil Tahap 6 sebelum apa pun selanjutnya.

Sesuai stop condition: tidak lanjut ke ML, tidak memperbesar dataset, tidak mencari
label biologis baru, tidak membuat model.
