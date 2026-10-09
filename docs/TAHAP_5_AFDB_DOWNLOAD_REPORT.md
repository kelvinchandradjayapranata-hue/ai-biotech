# Laporan Tahap 5 — Unduhan Terkontrol AlphaFold DB & Verifikasi Integritas

## 1. STATUS

**SELESAI — 7/7 protein `DOWNLOADED_VALIDATED`; 0 gagal; 16/16 test PASS (+ test Tahap 4 tetap 12/12 PASS).**
BERHENTI menunggu review. Belum ada ekstraksi fitur, belum ada ML.

## 2. Execution date/time

- Tanggal: **2026-10-05**
- Unduhan: **16:57:16 – 16:57:43** (waktu lokal), sekuensial dengan jeda antar-request
- Log bertimestamp: `data/alphafold_db/metadata/download_log.txt`
- Timestamp **tidak** dimasukkan ke CSV mana pun (deterministik, sesuai aturan)

## 3. AFDB API/source

| Hal | Nilai |
|---|---|
| API metadata | `https://alphafold.ebi.ac.uk/api/prediction/<accession>` |
| Sumber file | `https://alphafold.ebi.ac.uk/files/...` — URL diambil **live dari respons API saat eksekusi**, bukan URL lama |
| Sekuens resmi pembanding | `uniprotSequence` dari respons API (respons mentah disimpan: `data/alphafold_db/metadata/api_<accession>.json`) |
| Script unduhan | `src/download_afdb_dataset.py` (hanya urllib stdlib; tanpa credential; tanpa AlphaFold Server) |
| Script validasi | `src/validate_afdb_dataset.py` (offline) |
| Script test | `src/test_afdb_download.py` (offline, hitung ulang semua nilai kritis) |

## 4. Candidate count

**7 protein** — persis daftar yang disetujui di manifest Tahap 4. Tidak ada kandidat ditambahkan.

## 5. Successful downloads

**14/14 file** (7 CIF + 7 PAE). Semua HTTP 200, semua non-zero-byte.

## 6. Failed downloads

**0.** (Semua protein lulus validasi metadata API sebelum unduhan: accession cocok, entry ID cocok, `isComplex=false`, URL resmi.)

## 7. AFDB versions

**v6 untuk semua 7 entri** (`latestVersion` dari API pada hari eksekusi). Tidak ada pemaksaan versi — nama file mengikuti URL yang dikembalikan API.

## 8. File counts

| Lokasi | Isi |
|---|---|
| `data/alphafold_db/raw/` | 14 file dataset (7 `.cif` + 7 `.json`) + `README.txt` penanda |
| `data/alphafold_db/metadata/` | 7 `api_<acc>.json` (mentah) + `download_checksums.csv` (14 baris) + `download_log.txt` |
| `results/dataset/` | `structure_validation.csv` (7) + `pae_validation.csv` (7) + `dataset_download_manifest.csv` (7) |

## 9. Total bytes

**1.469.156 bytes (~1,40 MB)** untuk 14 file dataset — kecil, sesuai perkiraan plan.

## 10. SHA256 verification

Semua SHA256 **dihitung ulang oleh test dari file di disk** dan cocok dengan `download_checksums.csv` **dan** `dataset_download_manifest.csv`. Detail lengkap per file ada di bagian 16.

## 11. Sequence verification

| Pemeriksaan | Hasil |
|---|---|
| CIF (residu model) == `uniprotSequence` API | **7/7 MATCH (identik, bukan hanya panjang)** |
| `sequenceChecksum` API == MD5(sekuens) | **7/7 cocok** |
| Cross-check sumber resmi kedua (UniProt REST): sekuens UniProt == `uniprotSequence` | **7/7 identik** |
| Cross-check CRC64 resmi UniProt vs implementasi CRC64/ISO-3309 | **7/7 cocok** (mis. P61626: `8ECFD276BEB2678A`) |

Catatan: `sequenceChecksum` AlphaFold DB ternyata **MD5** (32 hex), sedangkan UniProt memakai **CRC64** (16 hex) — dua sistem checksum berbeda, keduanya diverifikasi dan cocok.

## 12. PAE verification

- Format nyata (v6): `list[0]["predicted_aligned_error"]` + skalar `max_predicted_aligned_error` (mis. 31.75).
- 7/7 matrix **N×N persegi**, N == panjang sekuens (105–238). Nilai PAE **dibaca apa adanya — tidak diubah, tidak ditranspose, tanpa interpretasi biologis**.
- File PAE tidak zero-byte; JSON valid; ukuran 22–116 KB.

## 13. Test result

```
python src\test_afdb_download.py  -> 16/16 PASS (exit 0)
python src\test_dataset_manifest.py -> 12/12 PASS (manifest Tahap 4 tetap utuh;
  hanya check E4 diperbarui: raw/ kini boleh berisi file kandidat yang disetujui)
```

Cakupan test Tahap 5: jumlah protein, accession unik, CIF & PAE ada, size > 0, SHA256 dihitung ulang, panjang & match sekuens, shape PAE, source, license, tanpa file tambahan, checksums 14 baris HTTP 200, 1 model/1 chain, status manifest, konsistensi versi.

## 14. Concerns

1. **Dua sistem checksum berbeda** (AFDB = MD5, UniProt = CRC64) — sudah didokumentasikan & diverifikasi keduanya; jangan tertukar saat verifikasi ulang manual.
2. **Versi v6 dapat berubah** di masa depan — SHA256 yang tercatat adalah titik referensi; perubahan server akan terdeteksi sebagai hash berbeda.
3. Sebagian sel PAE berisi bilangan bulat (mis. 0, 31) bercampur float — karakter data apa adanya dari AFDB; **tidak diubah**. Nilai min/max di `pae_validation.csv` hanya deskriptif.
4. `structure_validation.csv` mencatat panjang residu yang **dimodelkan**; dalam kasus ini 7/7 sama dengan panjang UniProt penuh (mis. RNase1 1–150 termasuk signal peptide).
5. Semua file adalah **prediksi model** — bukan data eksperimen; tidak ada klaim fungsional/biologis di tahap ini.

## 15. Next step

1. **User review** (sekarang): `dataset_download_manifest.csv`, `download_checksums.csv`, `structure_validation.csv`, `pae_validation.csv`, hasil test, dan SHA256.
2. Setelah otorisasi: ekstraksi fitur multi-protein (reuse skema Tahap 3: 28 kolom per-residu + ringkasan per-protein).
3. Baru setelah itu pertimbangkan eksperimen ML sederhana.

**Jangan lanjut ke Tahap 6 sebelum review selesai.**

---

## 16. Detail per protein

| # | UniProt | AFDB ID | Ver | Length | CIF size | PAE size | Seq match | PAE shape | Status |
|---|---|---|---|---|---|---|---|---|---|
| 1 | P61626 | AF-P61626-F1 | v6 | 148 | 147.439 B | 48.377 B | MATCH | 148×148 | DOWNLOADED_VALIDATED |
| 2 | P02144 | AF-P02144-F1 | v6 | 154 | 151.949 B | 48.352 B | MATCH | 154×154 | DOWNLOADED_VALIDATED |
| 3 | P99999 | AF-P99999-F1 | v6 | 105 | 108.338 B | 22.497 B | MATCH | 105×105 | DOWNLOADED_VALIDATED |
| 4 | P0DP23 | AF-P0DP23-F1 | v6 | 149 | 148.336 B | 57.011 B | MATCH | 149×149 | DOWNLOADED_VALIDATED |
| 5 | P00441 | AF-P00441-F1 | v6 | 154 | 144.236 B | 48.214 B | MATCH | 154×154 | DOWNLOADED_VALIDATED |
| 6 | P61823 | AF-P61823-F1 | v6 | 150 | 145.832 B | 51.759 B | MATCH | 150×150 | DOWNLOADED_VALIDATED |
| 7 | P42212 | AF-P42212-F1 | v6 | 238 | 230.531 B | 116.285 B | MATCH | 238×238 | DOWNLOADED_VALIDATED |

SHA256 (dihitung ulang dari file di disk, cocok dengan checksums CSV):

```
P61626 CIF: 8444ea54dc496d7a8107257040ca7d12476f0508a943b17890b846ecd1e2b99e
P61626 PAE: b3fba0b90f6a79cfa60952a2243a1410cc108438ab998bb50de620014ad26902
P02144 CIF: 5fe127f5047a9bda4eb96759c444b9f12b447b24ec49e82bdae32ea768803d23
P02144 PAE: d32c10446d18a6b375af31e19dceb774ffb81ab6354318e8b58b374742e762af
P99999 CIF: 1b48d4bc17398c7e4f54d18b1c401fedc099aea22adbb8b6e943755acd8e3605
P99999 PAE: b422bfda4884d8c758d00488274ac46e505f913c27f686e052f9cbdc6c3a9faa
P0DP23 CIF: e698114902202d87b9cf6ea7656fbf433db61571d085593905885de6389b475f
P0DP23 PAE: 44c3f6c438ee29fe9d6c7da72e916904f3103c5471aae93747a586f7d1b49652
P00441 CIF: fd186af7f5fdd9214cee40653bed71760fa53f0922d3438f9ce62e74c64f0edb
P00441 PAE: ab6998cc394243b3ad7d5ed29b9ce6ea5b9a65c38584d8d8b98c77bac8e5de90
P61823 CIF: 9f20e86e00ceb3f6d2020cf3ac4b5c17a340be5a2b56dd89e20b9edb9a7dd9b5
P61823 PAE: b3258e465f4edb5f3b9a1db02547927776ec28579dadd5c3e05a47c3b5173b4f
P42212 CIF: 20fee8dd4053d5aa1dc43acd68810faccf68b942f41220d375bfa6307daaa6d2
P42212 PAE: b2838a1e0d38a31e133bec1f176c54578410f4b8a7b009b648b0c621a682ee88
```

Verifikasi ulang manual (contoh, bisa dijalankan sendiri):

```bat
.venv\Scripts\python.exe -c "import hashlib;print(hashlib.sha256(open(r'data\alphafold_db\raw\AF-P61626-F1-model_v6.cif','rb').read()).hexdigest())"
.venv\Scripts\python.exe src\test_afdb_download.py
```
