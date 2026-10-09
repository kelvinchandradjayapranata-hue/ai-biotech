#!/usr/bin/env python3
"""
download_afdb_dataset.py - Tahap 5: unduh terkontrol 7 protein dari AlphaFold DB.

Untuk setiap kandidat di data/alphafold_db/metadata/candidates.json:
  1. Query API resmi AlphaFold DB -> respons mentah disimpan ke
     data/alphafold_db/metadata/api_<accession>.json
  2. Validasi metadata API SEBELUM mengunduh: accession cocok, entry ID cocok,
     isComplex=False (monomer), versi model tersedia, URL file resmi
     (https://alphafold.ebi.ac.uk/files/...).
  3. Unduh HANYA 2 file per protein (model CIF + PAE JSON) dari URL yang BARU
     dikembalikan API pada eksekusi ini (tidak memakai URL lama secara buta).
  4. Verifikasi: HTTP status sukses, file tidak zero-byte, hitung SHA256 + size.
  5. Tulis data/alphafold_db/metadata/download_checksums.csv (deterministik,
     tanpa timestamp) + data/alphafold_db/metadata/download_log.txt (bertimestamp).

BATASAN: hanya 7 accession yang disetujui; tidak bulk download; tidak scrape;
tidak menyentuh AlphaFold Server; tidak ada ML; tanpa credential (data publik).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CANDIDATES_PATH = PROJECT_ROOT / "data" / "alphafold_db" / "metadata" / "candidates.json"
META_DIR = PROJECT_ROOT / "data" / "alphafold_db" / "metadata"
RAW_DIR = PROJECT_ROOT / "data" / "alphafold_db" / "raw"
CHECKSUMS_CSV = META_DIR / "download_checksums.csv"
LOG_PATH = META_DIR / "download_log.txt"

CHECKSUM_COLUMNS = [
    "protein_id",
    "uniprot_accession",
    "afdb_id",
    "file_type",
    "filename",
    "url",
    "http_status",
    "file_size_bytes",
    "sha256",
    "afdb_version",
    "download_status",
]

API_PATTERN = "https://alphafold.ebi.ac.uk/api/prediction/{acc}"
ALLOWED_FILE_PREFIX = "https://alphafold.ebi.ac.uk/files/"
USER_AGENT = "ai-biotech-learning-project/0.1 (educational; sequential small downloads)"
TIMEOUT_S = 60
RETRIES = 3
PAUSE_BETWEEN_REQUESTS_S = 0.5


def log(msg: str) -> None:
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def fetch(url: str) -> tuple[int, bytes]:
    """GET dengan retry sederhana. Kembalikan (status, bytes) atau raise RuntimeError."""
    last_err: Exception | None = None
    for attempt in range(1, RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
                return int(resp.status), resp.read()
        except Exception as exc:  # noqa: BLE001 - laporkan semua kegagalan jaringan
            last_err = exc
            log(f"    [retry {attempt}/{RETRIES}] {url} -> {exc}")
            time.sleep(1.5 * attempt)
    raise RuntimeError(f"gagal mengambil {url}: {last_err}")


def sha256_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def download_one(acc: str, file_type: str, url: str, version: int, entry_id: str) -> dict:
    """Unduh 1 file ke RAW_DIR dengan pola file sementara -> replace. Kembalikan baris checksum."""
    filename = url.rsplit("/", 1)[-1]
    row = {
        "protein_id": acc,
        "uniprot_accession": acc,
        "afdb_id": entry_id,
        "file_type": file_type,
        "filename": filename,
        "url": url,
        "http_status": "",
        "file_size_bytes": 0,
        "sha256": "",
        "afdb_version": version,
        "download_status": "FAILED",
    }
    try:
        status, data = fetch(url)
        row["http_status"] = status
        if status != 200:
            log(f"    FAILED {filename}: HTTP {status}")
            return row
        if len(data) == 0:
            log(f"    FAILED {filename}: zero-byte")
            return row
        target = RAW_DIR / filename
        tmp = RAW_DIR / (filename + ".part")
        tmp.write_bytes(data)
        os.replace(tmp, target)
        row["file_size_bytes"] = len(data)
        row["sha256"] = sha256_of(data)
        row["download_status"] = "OK"
        log(f"    OK {filename}: {len(data)} bytes, sha256={row['sha256'][:16]}...")
    except Exception as exc:  # noqa: BLE001
        log(f"    FAILED {filename}: {exc}")
    finally:
        time.sleep(PAUSE_BETWEEN_REQUESTS_S)
    return row


def process_candidate(c: dict, rows: list[dict], failures: list[str]) -> None:
    acc = c["uniprot_accession"]
    api_url = API_PATTERN.format(acc=acc)
    log(f"{acc} ({c['protein_name']}) - query API: {api_url}")

    try:
        status, body = fetch(api_url)
    except RuntimeError as exc:
        failures.append(f"{acc}: API gagal ({exc})")
        return
    time.sleep(PAUSE_BETWEEN_REQUESTS_S)
    if status != 200:
        failures.append(f"{acc}: API HTTP {status}")
        return

    # Simpan respons API mentah
    (META_DIR / f"api_{acc}.json").write_bytes(body)

    payload = json.loads(body)
    rec = payload[0] if isinstance(payload, list) and payload else payload

    problems: list[str] = []
    if rec.get("uniprotAccession") != acc:
        problems.append(f"uniprotAccession={rec.get('uniprotAccession')!r} != {acc!r}")
    entry_id = str(rec.get("entryId", ""))
    if not entry_id.startswith(f"AF-{acc}-"):
        problems.append(f"entryId={entry_id!r} tidak sesuai pola AF-{acc}-*")
    if rec.get("isComplex") is not False:
        problems.append(f"isComplex={rec.get('isComplex')!r} (diharapkan False/monomer)")
    version = rec.get("latestVersion")
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        problems.append(f"latestVersion tidak valid: {version!r}")
        version = 0
    cif_url = str(rec.get("cifUrl", ""))
    pae_url = str(rec.get("paeDocUrl", ""))
    for label, u in (("cifUrl", cif_url), ("paeDocUrl", pae_url)):
        if not u.startswith(ALLOWED_FILE_PREFIX):
            problems.append(f"{label} bukan URL resmi AFDB: {u!r}")

    if problems:
        for p in problems:
            log(f"    TIDAK SESUAI: {p}")
        failures.append(f"{acc}: metadata API tidak sesuai ({'; '.join(problems)})")
        return  # JANGAN unduh bila metadata tidak konsisten

    log(f"    API OK: entry={entry_id}, versi=v{version}, monomer=True")
    rows.append(download_one(acc, "structure_cif", cif_url, version, entry_id))
    rows.append(download_one(acc, "pae_json", pae_url, version, entry_id))


def write_checksums(rows: list[dict]) -> None:
    with CHECKSUMS_CSV.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CHECKSUM_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Unduh terkontrol CIF + PAE dari AlphaFold DB (hanya kandidat yang disetujui).")
    parser.add_argument("--accessions", default="", help="opsi: batasi ke daftar accession koma, mis. P61626,P99999 (default: semua kandidat)")
    args = parser.parse_args()

    if not CANDIDATES_PATH.is_file():
        print(f"[!] Tidak ada: {CANDIDATES_PATH}")
        return 2
    doc = json.loads(CANDIDATES_PATH.read_text(encoding="utf-8"))
    candidates = doc["candidates"]
    if args.accessions:
        wanted = {a.strip() for a in args.accessions.split(",") if a.strip()}
        approved = {c["uniprot_accession"] for c in candidates}
        unknown = wanted - approved
        if unknown:
            print(f"[!] Accession di luar kandidat yang disetujui: {sorted(unknown)}")
            return 2
        candidates = [c for c in candidates if c["uniprot_accession"] in wanted]

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    log("=" * 70)
    log(f"MULAI unduhan terkontrol AlphaFold DB: {len(candidates)} protein")
    log(f"Sumber API: {API_PATTERN.format(acc='<accession>')}")

    rows: list[dict] = []
    failures: list[str] = []
    for c in candidates:
        process_candidate(c, rows, failures)

    write_checksums(rows)
    log(f"Checksums ditulis -> {CHECKSUMS_CSV} ({len(rows)} baris file)")

    ok_files = sum(1 for r in rows if r["download_status"] == "OK")
    total_bytes = sum(r["file_size_bytes"] for r in rows)
    log(f"SELESAI: {ok_files} file OK dari {len(rows)} percobaan; total {total_bytes} bytes")
    if failures:
        for f in failures:
            log(f"GAGAL: {f}")
        return 1
    expected_rows = 2 * len(candidates)
    if len(rows) != expected_rows or ok_files != expected_rows:
        log(f"PERINGATAN: baris checksum {len(rows)} != {expected_rows} atau file OK {ok_files} != {expected_rows}")
        return 1
    log("SEMUA file terunduh & checksum tercatat.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
