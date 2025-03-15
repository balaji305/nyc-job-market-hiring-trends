"""Download the official Jobs NYC Postings CSV from NYC Open Data."""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from urllib.request import Request, urlopen

DATASET_ID = "kpav-sd4t"
API_URL = f"https://data.cityofnewyork.us/resource/{DATASET_ID}.csv?$limit=50000"
ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "jobs_nyc_postings_raw.csv"


def download(output: Path = RAW_PATH, url: str = API_URL) -> Path:
    """Download a reproducible raw snapshot without modifying its contents."""
    output.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": "nyc-job-market-portfolio/1.0"})
    with urlopen(request, timeout=90) as response:
        payload = response.read()
    header = payload.removeprefix(b"\xef\xbb\xbf")
    if not (header.startswith(b"job_id,") or header.startswith(b'"job_id",')):
        raise ValueError("Downloaded file does not look like the expected NYC Jobs CSV")
    output.write_bytes(payload)
    logging.info("Saved %.1f KB to %s", len(payload) / 1024, output)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RAW_PATH)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    download(args.output)
