# Regenerating the Cdiv->EMM/State disaggregation

This directory builds the factors used to disaggregate Scout's Census
Division-level baseline stock/energy data down to EMM regions and states,
using NREL ResStock/ComStock building-level data. Rerun this workflow when
a new ResStock/ComStock release should be picked up, or when the
underlying mapping/disaggregation logic changes.

The end-to-end process is four scripts, run in order. **Each one has a
different working-directory requirement — cwd is not optional, it changes
where files get read/written.**

## 1. Download BuildStock data

```
cd scout/supporting_data/base_disagg
python download_buildstock.py
```

No CLI arguments — edit the `YEAR` variable at the top of the file
(`"2025"` or `"2024"`) to pick the release instead. Downloads ResStock/
ComStock baseline parquet files to `input/<year>_resstock/` and
`input/<year>_comstock/` (relative to cwd), and writes a per-dataset
`sdr_version.json` next to each recording the release version.

## 2. Generate the disaggregation CSVs

```
python generate_geo_maps.py --install
```

Run from the same directory as step 1, so its defaults
(`--resstock-path`/`--comstock-path`, both `input/<year>_<ds>` relative to
cwd) line up with where step 1 wrote the data. `--mapping-dir` defaults to
this script's own `input/mapping/` regardless of cwd, since those
`map_*.csv` files are checked into git (see step 0 below) rather than
downloaded.

`--install` is required to actually update the files Scout reads —
without it, output only lands in the scratch `output/` directory here,
not in `../convert_data/geo_map/`. Run `--help` for the full flag list
(`--sector`, `--data-type`, `--year`, etc.); the defaults cover the
common case.

**Gotcha:** if you ever run this script from a different cwd, it creates
a second `output/2025_end_use/` (or `_technology/`) directory relative to
that cwd, and it's easy to check timestamps in the stale one by mistake.
There should only ever be one `output/` under this directory — delete any
duplicates elsewhere before re-running.

## 3. Regenerate the EMM/state baseline JSON

```
cd ../stock_energy_tech_data
python ../../final_mseg_converter.py
```

**Must be run with cwd = `stock_energy_tech_data/`.** The script writes
its output (`mseg_res_com_emm.json`/`.gz`, `mseg_res_com_state.json`/`.gz`)
to a bare relative filename, not an absolute path, so it lands wherever
cwd happens to be.

It's interactive and must be run **twice** — once per region breakdown:

- Prompt 1: `1` (energy, stock, and square footage data)
- Prompt 2: `2` for EMM, or `3` for state
- Prompt 3 (electricity-only vs. all fuels): match whatever the current
  baseline files use — check `_cdiv_disagg_info.prep_settings` in the
  existing `mseg_res_com_emm.gz`/`mseg_res_com_state.gz` before
  overwriting them, unless you're intentionally changing the setting.
  Scout's default baseline files use `2` (all fuels).
- Prompt 4 (technology- vs. end-use-level electricity disaggregation):
  same idea — Scout's default baseline files use `1` (technology-level).

This also stamps a `_cdiv_disagg_info` block (disaggregation choices +
ResStock/ComStock SDR version) into the top of each output file for
provenance (issue #576).

## 4. Regenerate the heating/cooling totals

```
cd ../../..   # back to repo root
python scout/htcl_totals.py
```

No parameters. Reads the AIA/EMM/state baseline files (including the ones
just regenerated in step 3) and rewrites the `htcl_totals*` summary files
in `stock_energy_tech_data/`.

## Step 0 (rare): regenerating the HVAC mapping CSVs

`generate_mapping_csvs.py` regenerates `input/mapping/map_*.csv` from
`input/Stock-Scout mapping.xlsx`. These CSVs are checked into git, so you
only need this if the source Excel mapping itself changes — not as part
of a routine data refresh.

## After regenerating

Commit the updated files: the CSVs and `sdr_version.json` under
`../convert_data/geo_map/`, `mseg_res_com_emm.gz`/`mseg_res_com_state.gz`
under `../stock_energy_tech_data/`, and the `htcl_totals*` files step 4
rewrote.
