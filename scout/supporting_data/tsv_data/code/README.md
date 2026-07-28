# TSV load-shape update workflow

`update_tsv.py` regenerates Scout's ComStock/ResStock-derived load-shape
files (`tsv_load_EMM.gz`, `tsv_load_State.gz` in `supporting_data/tsv_data/`)
by querying AWS Athena and reshaping the results into the JSON format
`ecm_prep.py` expects.

## Prerequisites

- AWS credentials configured (e.g. via `aws configure` / `AWS_PROFILE`)
  with access to the `scout_tsv` Athena database and the `yujie-bucket` S3
  bucket (both hardcoded in `update_tsv.py` as `DATABASE_NAME` /
  `BUCKET_NAME`) — this is where the ComStock/ResStock Athena tables and
  query results live.
- Python packages: `boto3`, `pandas`, `numpy`.
- Run all commands from this directory (`scout/supporting_data/tsv_data/code/`)
  — the script's `sql/`, `csv/`, `json/`, `map/` paths are relative to cwd.

## Steps

The full rebuild is three stages, run in order. `--bstock` and
`--stock_version` are shared across stages 1 and 2.

### 1. Pull raw data from Athena (`--get_stockdata`)

```bash
python update_tsv.py --get_stockdata
```

Uploads `map/geo_map.csv` as an Athena table (county → EMM region mapping),
then runs the four SQL queries in `sql/` (ComStock/ResStock × EMM/state)
concurrently against Athena and downloads the results to
`csv/{commercial,residential}_{emm,state}_{stock_version}.csv`.

- **`--stock_version {2025,2024}`** (default `2025`) selects which
  ComStock/ResStock release to query:
  - `2025` → ComStock 2025.3 / ResStock 2025.1
  - `2024` → ComStock 2024.2 / ResStock 2024.2

  The version is baked into the cached CSV filename, so switching
  `--stock_version` between runs can't silently reuse a CSV cached from the
  other release.
- If a target CSV already exists, that query is skipped (Athena queries
  scan a lot of data and take a while). Delete the file under `csv/` to
  force a re-run.

Example — pull 2024 data instead of the default 2025:

```bash
python update_tsv.py --get_stockdata --stock_version 2024
```

### 2. Insert into the load-shape JSON (`--insert_scouttsv`)

```bash
python update_tsv.py --insert_scouttsv --bstock commercial
python update_tsv.py --insert_scouttsv --bstock residential
```

**Commercial must run before residential** — residential's output builds
on top of commercial's (`json/tsv_load_{emm,state}_2024_com.json` is read
as the base when processing residential). Running residential first will
fail with a missing-file error.

Each invocation reads the matching `csv/..._{stock_version}.csv` file (so
pass the same `--stock_version` used in step 1) and computes normalized
(sum-to-one) hourly load shapes per building type / end use / region.
After the residential pass, the final gzipped outputs are written to
`../tsv_load_EMM.gz` and `../tsv_load_State.gz` — these are the files
`ecm_prep.py` consumes directly.

### 3. (Optional) Diagnostics (`--diag`)

```bash
python update_tsv.py --diag --bstock commercial
python update_tsv.py --diag --bstock residential
```

Sanity-checks the cached CSVs from step 1 (row counts per region, missing
hourly timestamps) without touching the JSON output.

## Full example (default 2025 release)

```bash
cd scout/supporting_data/tsv_data/code
python update_tsv.py --get_stockdata
python update_tsv.py --insert_scouttsv --bstock commercial
python update_tsv.py --insert_scouttsv --bstock residential
```
