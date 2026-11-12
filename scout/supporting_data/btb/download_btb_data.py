"""Download the NREL Buildings Technology Baseline (BTB) dataset from OpenEI.

BTB (https://data.openei.org/submissions/8342) is a public NREL/Guidehouse
dataset of current and projected cost, performance, and lifetime data for
residential and commercial building energy technologies. It is the intended
source for the Energy Performance / Installed Cost / Lifetime columns in
./bss_meas_v2.xlsx (sheet "meas_in") that currently cite "Buildings Annual
Technology Baseline. NREL, forthcoming" but were transcribed by hand.

This script just downloads the two flat CSV files (residential and
commercial) into ./raw/, which is git-ignored since the files are large and
re-downloadable. Run this before build_tech_crosswalk.py or
populate_meas_in_from_btb.py.

No API key required -- OpenEI serves these as public direct file links.

Usage (from this directory, or any cwd -- paths are relative to this file):
    python download_btb_data.py
    python download_btb_data.py --overwrite
"""

import argparse
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "raw"

# Direct file links taken from the OpenEI submission page (id 8342).
SOURCES = {
    "residential": {
        "url": (
            "https://data.openei.org/files/8342/"
            "btb2024_residential_dataset%20(3).csv"
        ),
        "filename": "btb_residential.csv",
    },
    "commercial": {
        "url": (
            "https://data.openei.org/files/8342/"
            "btb2024_commercial_dataset%20(4).csv"
        ),
        "filename": "btb_commercial.csv",
    },
}


def download_file(url, out_path, overwrite):
    """Download a single BTB CSV file if it is not already present.

    Args:
        url (str): Direct download URL for the file.
        out_path (Path): Local destination path.
        overwrite (bool): Re-download and replace an existing file.
    """

    if out_path.exists() and not overwrite:
        print(f"  {out_path.name} already exists, skipping "
              "(use --overwrite to re-download).")
        return

    print(f"  Downloading {out_path.name}...", end="", flush=True)
    resp = requests.get(url, timeout=(5, 60))
    resp.raise_for_status()
    out_path.write_bytes(resp.content)
    print(f" done ({len(resp.content) / 1e6:.2f} MB).")


def main(overwrite):
    """Download all BTB source CSVs into ./raw/."""

    OUT_DIR.mkdir(exist_ok=True)
    print(f"Writing BTB CSVs to {OUT_DIR}")
    for sector, cfg in SOURCES.items():
        print(f"Sector: {sector}")
        download_file(cfg["url"], OUT_DIR / cfg["filename"], overwrite)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download BTB residential/commercial CSVs from OpenEI.")
    parser.add_argument(
        "-o", "--overwrite", action="store_true",
        help="Re-download files even if they already exist in ./raw/.")
    args = parser.parse_args()
    main(args.overwrite)
