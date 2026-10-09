# Rencana Dataset — Tahap 4: Sumber Dataset dari AlphaFold DB

**Status: PERSIAPAN — belum ada file struktur yang diunduh, belum ada ML.**
Dokumen ini + `results/dataset/dataset_manifest.csv` adalah bahan review.
Unduhan baru dilakukan setelah manifest disetujui.

---

## 1. Tujuan dataset

Menyiapkan dataset multi-protein (7 protein) dari **AlphaFold Protein Structure
Database (AlphaFold DB)** sebagai calon sumber data untuk analisis dan — nanti,
setelah lolos review — machine learning tahap berikutnya.

Tahap 4 hanya mencakup:

1. Memilih kandidat protein dari sumber resmi.
2. Memverifikasi identitas (accession, panjang, fungsi) dari sumber resmi.
3. Mencatat lisensi & atribusi.
4. Membangun pipeline manifest yang deterministik dan bisa divalidasi.

Yang **bukan** bagian tahap ini: unduhan file struktur, ekstraksi fitur
multi-protein, training ML.

## 2. Pemisahan dua sumber data (penting)

Project ini memakai dua sumber data yang **perannya sengaja dipisahkan**:

| Aspek | AlphaFold Server (sudah ada, Tahap 2-3) | AlphaFold DB (dataset ini, Tahap 4+) |
|---|---|---|
| Apa itu | prediksi yang dijalankan user di alphafoldserver.com untuk 1 protein | database publik resmi (EMBL-EBI & Google DeepMind), ratusan juta prediksi |
| Isi | 1 protein + PAE + confidence + MSA + template | per entri UniProt: model struktur + PAE |
| Peran di project | **spesimen pembelajaran & referensi**: demonstrasi analisis struktur + feature extraction per-residu | **kandidat sumber dataset ML** (tahap lanjutan) |
| Dipakai sebagai training data ML? | **TIDAK** | ya — setelah review, unduhan terkontrol, dan verifikasi |
| Lokasi file | `structures/ubiquitin_alphafold.cif`, `data/alphafold_downloads/` | direncanakan: `data/alphafold_db/raw/` |
| Lisensi | terms of use AlphaFold Server | CC BY 4.0 + atribusi |

Konsekuensi: **ubiquitin tidak dimasukkan** sebagai kandidat dataset agar
pemisahan peran tetap jelas — output AlphaFold Server tetap murni sebagai
spesimen pembelajaran.

## 3. Sumber data resmi & status verifikasi

| Hal | Nilai |
|---|---|
| Sumber struktur | AlphaFold Protein Structure Database (EMBL-EBI & Google DeepMind), https://alphafold.ebi.ac.uk/ |
| Sumber anotasi | UniProtKB, https://www.uniprot.org/ |
| API metadata | `https://alphafold.ebi.ac.uk/api/prediction/<accession>` |
| Verifikasi dilakukan | 2026-10-05 (tanpa mengunduh file struktur) |
| Hasil verifikasi | 7/7 accession valid di UniProtKB; 7/7 entri ada di AlphaFold DB; entry ID `AF-<accession>-F1`; `latestVersion = 6`; semua `isComplex = false` (monomer / single-chain) |
| Pola URL unduhan (terverifikasi di API) | model: `.../files/AF-<acc>-F1-model_v6.cif` — PAE: `.../files/AF-<acc>-F1-predicted_aligned_error_v6.json` |
| Catatan ukuran | Tahap ini hanya query metadata (beberapa KB per API call). **Nol byte file struktur diunduh.** |

Cara verifikasi ulang (bisa dijalankan sendiri):

```bat
:: metadata UniProt (nama, panjang, organisme) — ganti/ulangi per accession
curl "https://rest.uniprot.org/uniprotkb/P61626.json?fields=accession,protein_name,length,organism_name"

:: metadata + URL unduhan AlphaFold DB
curl "https://alphafold.ebi.ac.uk/api/prediction/P61626"
```

## 4. Lisensi & atribusi

- **Lisensi data**: CC BY 4.0. Pernyataan resmi situs AlphaFold DB
  (dicek 2026-10-05): *"Data is available for academic and commercial use,
  under a CC-BY-4.0 licence."*
- **Atribusi wajib**: EMBL-EBI, Google DeepMind, dan UniProt saat dataset
  ini dipakai/dibagikan.
- **Sitasi**: halaman resmi AlphaFold DB mencantumkan paper *Nucleic Acids
  Research* 2025 (Bertoni et al.) sebagai sitasi dataset; data anotasi dari
  UniProt Consortium. Cek halaman sitasi resmi saat dataset dipublikasikan.
- Kolom `license` dan `license_url` tercatat **per baris** di manifest.

## 5. Kriteria pemilihan kandidat

1. Entri resmi AlphaFold DB (bukan prediksi baru dari AlphaFold Server).
2. Single-chain / monomer (`isComplex = false`).
3. Panjang kecil-moderat (batas validasi 20-600 aa; kandidat aktual 105-238 aa).
4. Fungsi diketahui dari sumber resmi (UniProtKB).
5. Beragam: minimal 3 kategori fungsi berbeda + organisme berbeda.
6. Bukan ubiquitin (spesimen pembelajaran tetap terpisah).

## 6. Kandidat protein (7 protein)

| # | Protein (gen) | Organisme | UniProt | Entri AlphaFold DB | Panjang | Kategori |
|---|---|---|---|---|---|---|
| 1 | Lysozyme C (LYZ) | Homo sapiens | P61626 | AF-P61626-F1 | 148 aa | enzyme |
| 2 | Myoglobin (MB) | Homo sapiens | P02144 | AF-P02144-F1 | 154 aa | oxygen_binding |
| 3 | Cytochrome c (CYCS) | Homo sapiens | P99999 | AF-P99999-F1 | 105 aa | electron_transfer |
| 4 | Calmodulin-1 (CALM1) | Homo sapiens | P0DP23 | AF-P0DP23-F1 | 149 aa | calcium_signaling |
| 5 | Superoxide dismutase [Cu-Zn] (SOD1) | Homo sapiens | P00441 | AF-P00441-F1 | 154 aa | antioxidant_enzyme |
| 6 | Ribonuclease pancreatic (RNASE1) | Bos taurus | P61823 | AF-P61823-F1 | 150 aa | enzyme |
| 7 | Green fluorescent protein (GFP) | Aequorea victoria | P42212 | AF-P42212-F1 | 238 aa | fluorescent_protein |

Fungsi singkat (dari anotasi UniProtKB):

1. **Lysozyme C** — enzim bakteriolitik (glikosidase) yang memecah peptidoglikan
   dinding bakteri; bagian pertahanan imun bawaan.
2. **Myoglobin** — protein heme monomerik penyimpan & pendifusi oksigen di otot.
3. **Cytochrome c** — pembawa elektron di rantai transpor elektron mitokondria;
   terlibat sinyal apoptosis saat dilepas ke sitosol.
4. **Calmodulin-1** — regulator pensinyalan kalsium; mengikat Ca2+ lalu mengatur
   banyak enzim dan kanal.
5. **SOD1** — enzim antioksidan yang menetralkan radikal superoksida.
6. **RNase1 (bovine)** — endonuklease pemotong RNA di sisi 3' nukleotida pirimidin.
7. **GFP** — protein fluoresen; kromofor memancarkan cahaya hijau memanfaatkan
   energi dari aequorin.

Alasan pemilihan per protein (ringkas):

- **Lysozyme C** — enzim globular kecil klasik, single-chain, anotasi lengkap;
  salah satu struktur protein pertama yang ditentukan secara eksperimen.
- **Myoglobin** — protein pengikat ligan (heme), kontras dengan enzim;
  struktur protein pertama yang ditentukan secara eksperimen (Kendrew, 1958).
- **Cytochrome c** — transpor elektron; terkecil dalam set; heme tidak
  dimodelkan → contoh keterbatasan dataset prediksi.
- **Calmodulin** — pensinyalan; konformasinya bergantung ikatan Ca2+ → bahan
  diskusi dinamika protein vs satu struktur statis.
- **SOD1** — antioksidan; **in vivo homodimer** tetapi entri AlphaFold DB berupa
  monomer → contoh eksplisit gap model vs bentuk biologis.
- **RNase1** — kategori enzim nuklease (kimia berbeda dari glikosidase) +
  organisme non-manusia (Bos taurus).
- **GFP** — protein fluoresen dari ubur-ubur (Aequorea victoria); kategori dan
  organisme paling berbeda; terpanjang dalam set (238 aa).

**Keberagaman**: 6 kategori fungsi berbeda (enzyme, oxygen_binding,
electron_transfer, calcium_signaling, antioxidant_enzyme, fluorescent_protein),
3 organisme (manusia, sapi, ubur-ubur), rentang panjang 105-238 aa.

**Keterbatasan yang diakui jujur** (bukan diklaim sebagai kelebihan):

- Semua kandidat adalah protein globular/larut; tidak ada protein membran atau
  protein dengan daerah tak terstruktur besar.
- 5 dari 7 kandidat adalah protein manusia — mencerminkan bias proteom manusia
  di UniProt/AlphaFold DB, bukan pilihan netral.
- 7 protein **jauh terlalu kecil** untuk klaim statistik apa pun tentang
  "perwakilan protein" — ini titik awal pipeline, bukan sampel ilmiah.
- Semua entri adalah model monomer; protein yang in vivo berinteraksi (mis. SOD1)
  direpresentasikan sebagai rantai tunggal.

## 7. Rencana file yang diunduh (SETELAH review)

Per entri AlphaFold DB, 2 file kecil:

| File | Pola nama (v6, terverifikasi) | Kegunaan |
|---|---|---|
| Model struktur | `AF-<acc>-F1-model_v6.cif` | analisis struktur + fitur per-residu |
| PAE | `AF-<acc>-F1-predicted_aligned_error_v6.json` | fitur/analisis confidence |

- Diunduh **satu per satu** (7 entri × 2 file, masing-masing umumnya < beberapa
  MB) — bukan bulk download, bukan scraping.
- URL final akan di-query ulang dari API saat unduhan (jika AlphaFold DB
  memperbarui versi model, versi baru dicatat dan manifest diperbarui).
- Verifikasi saat unduhan: sha256 dicatat, entry ID dicek, panjang sekuens model
  dicek terhadap `sequence_length` di manifest.
- Status di manifest akan berubah dari `planned_not_downloaded` → `downloaded`
  sebagai bagian tahap unduhan (test tahap ini memverifikasi `raw/` masih kosong).

## 8. Target features (tahap lanjutan, belum dibuat sekarang)

- **Per-residu** — memakai ulang skema Tahap 3 (28 kolom: identitas, sekuens,
  struktur, pLDDT, PAE turunan, contact) untuk tiap protein dataset.
- **Per-protein** — ringkasan (panjang, statistik pLDDT, statistik PAE, dsb).
- **Catatan penting untuk ML** (dari Tahap 3): koordinat mentah (`ca_x/y/z`,
  centroid) **tidak invariant rotasi/translasi** — untuk ML perlu fitur
  jarak/turunan yang invariant. PAE tersedia per entri AlphaFold DB.
- Setiap fitur baru wajib punya definisi + unit (aturan project).

## 9. Target label (jika nanti tersedia)

- **Label awal potensial**: `category` fungsi (6 kategori, sudah tercatat di
  manifest) — tetapi 7 sampel terlalu sedikit untuk klasifikasi; hanya layak
  sebagai ilustrasi struktur data.
- **Masa depan**: label fungsional resmi dari UniProt (mis. GO terms, EC
  numbers) — perlu keputusan desain (multi-label, hierarki, keseimbangan kelas)
  dan catatan lisensi. Belum diputuskan, belum bagian tahap ini.
- **Larangan**: tidak ada klaim prediksi fungsi, drug discovery, atau
  "penemuan" apa pun. Label = anotasi katalog resmi, bukan hasil eksperimen
  project ini.

## 10. Yang TIDAK dilakukan pada tahap ini

- Tidak mengunduh file struktur (hanya query metadata API).
- Tidak mengunduh dataset besar; tidak scraping jutaan protein.
- Tidak membuat model ML, tidak training, tidak PyTorch/TensorFlow/CUDA.
- Tidak docking, screening, molecular dynamics, atau klaim drug discovery.
- Tidak mengubah file mentah AlphaFold Server (tetap read-only).

## 11. Langkah berikutnya (setelah review manifest)

1. **User review** `results/dataset/dataset_manifest.csv` + dokumen ini. ← posisi sekarang
2. Unduh 7×2 file per-entri → `data/alphafold_db/raw/` + update manifest
   (sha256, status, tanggal).
3. Verifikasi unduhan: panjang sekuens model vs manifest, checksum, uji parser
   dengan data nyata (pola sama seperti Tahap 2).
4. Ekstraksi fitur multi-protein (reuse pipeline Tahap 3) → dataset gabungan.
5. Baru setelah itu: pertimbangkan eksperimen ML sederhana.

**Gate**: jangan lanjut ke langkah 2 sebelum manifest direview.
