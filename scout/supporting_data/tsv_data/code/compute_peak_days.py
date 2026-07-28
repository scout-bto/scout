"""Find each region's winter and summer peak day (day of year) in the total
buildings electricity load shape derived from the ComStock/ResStock raw
hourly CSVs (see update_tsv.py step 1, ``--get_stockdata``).

Reuses the same winter/summer day-of-year windows ecm_prep.py already
defines (HandyVars.tsv_metrics_data["season days"]) so the output is
directly comparable to the existing fixed national peak days (day 1 / day
183). Within a region's winter window, the "peak day" is the day containing
that region's single highest hourly total load (and similarly for summer).

Usage (run from this directory, after `--get_stockdata` has cached the raw
CSVs in csv/):

    python compute_peak_days.py --stock_version 2025

Writes tsv_peak_days_EMM.csv and tsv_peak_days_State.csv to
supporting_data/tsv_data/.
"""
import os
import datetime
from argparse import ArgumentParser

import pandas as pd

OUTPUT_DIR = "csv"
TSV_DATA_DIR = ".."

# Matches HandyVars.tsv_metrics_data["season days"]["all"] in ecm_prep.py
WINTER_DAYS = set(range(1, 91)) | set(range(335, 366))
SUMMER_DAYS = set(range(152, 274))

# Widened versions of the windows above, used only as a diagnostic to flag
# regions whose in-window peak sits right at a season boundary rather than
# at an interior local max (e.g. hot, low-heating-load climates where total
# load ramps monotonically from winter straight into the summer cooling
# season — the day-90/day-152 boundary then picks up whatever day the
# window happens to end on, not a real seasonal peak). Extends each block by
# 30 days, clipped so winter/summer stay non-overlapping.
BOUNDARY_CHECK_BUFFER_DAYS = 30
WINTER_DAYS_EXTENDED = (
    set(range(1, 91 + BOUNDARY_CHECK_BUFFER_DAYS)) |
    set(range(335 - BOUNDARY_CHECK_BUFFER_DAYS, 366)))
SUMMER_DAYS_EXTENDED = set(range(
    152 - BOUNDARY_CHECK_BUFFER_DAYS, 274 + BOUNDARY_CHECK_BUFFER_DAYS))
# Load must be at least this much higher outside the official window to be
# worth flagging (avoids flagging noise-level differences)
BOUNDARY_FLAG_LOAD_RATIO = 1.05

# Energy columns to sum per source. ComStock's "cooking"/"pcs"/
# "nonpc_office_equipment"/"other_mels" columns (and ResStock's
# "computers"/"tvs"/"other") are all populated from the same underlying
# interior-equipment/plug-load timeseries column (see sql/*.sql) — summing
# all of them would multiply-count that load. Keep a single representative
# column for that category ("other_mels" / "other") and drop the rest.
COMMERCIAL_ENERGY_COLS = [
    "cooling", "heating", "pumps", "ventilation", "water_heating",
    "lighting", "refrigeration", "other_mels"]
RESIDENTIAL_ENERGY_COLS = [
    "cooling", "heating", "water_heating", "cooking", "drying", "lighting",
    "refrigeration", "ceiling_fan", "fans_and_pumps", "other",
    "clothes_washing", "dishwasher", "pool_heaters", "pool_pumps",
    "portable_electric_spas"]


def load_total_hourly(csv_path, region_col, energy_cols, is_commercial):
    """ Read a raw stock CSV and return total load (summed across building
    types and the given energy columns) by region and timestamp. """
    usecols = ["timestamp_hour", region_col] + energy_cols
    df = pd.read_csv(csv_path, usecols=usecols)
    if is_commercial:
        # Drop a spurious wraparound timestamp row (see update_tsv.py)
        df = df[df["timestamp_hour"] != "2019-01-01 01:00:00.000"]
    df["total"] = df[energy_cols].sum(axis=1)
    return df.groupby(
        [region_col, "timestamp_hour"], as_index=False)["total"].sum()


def find_peak_days(combined, region_col):
    """ Given a region_col/timestamp_hour/total dataframe, find the
    winter and summer peak day (day of year) for each region, flagging
    regions where the in-window peak sits at a season boundary rather than
    an interior local max (see BOUNDARY_CHECK_BUFFER_DAYS above). """
    combined = combined.copy()
    combined["dayofyear"] = pd.to_datetime(
        combined["timestamp_hour"]).dt.dayofyear

    out_rows = []
    for season_name, season_days, season_days_ext in (
            ("Winter", WINTER_DAYS, WINTER_DAYS_EXTENDED),
            ("Summer", SUMMER_DAYS, SUMMER_DAYS_EXTENDED)):
        season_df = combined[combined["dayofyear"].isin(season_days)]
        idx = season_df.groupby(region_col)["total"].idxmax()
        peaks = season_df.loc[idx, [region_col, "dayofyear", "total"]]
        peaks = peaks.rename(columns={
            "dayofyear": f"{season_name}PeakDay",
            "total": f"{season_name}PeakLoad"})

        # Boundary robustness check: does a wider window find a higher,
        # different peak day? If so, the official-window peak is likely an
        # artifact of the window edge rather than a true local max.
        ext_df = combined[combined["dayofyear"].isin(season_days_ext)]
        ext_idx = ext_df.groupby(region_col)["total"].idxmax()
        ext_peaks = ext_df.loc[
            ext_idx, [region_col, "dayofyear", "total"]].rename(columns={
                "dayofyear": f"{season_name}ExtendedPeakDay",
                "total": f"{season_name}ExtendedPeakLoad"})
        peaks = peaks.merge(ext_peaks, on=region_col)
        peaks[f"{season_name}PeakAtWindowBoundary"] = (
            (peaks[f"{season_name}ExtendedPeakDay"] !=
             peaks[f"{season_name}PeakDay"]) &
            (peaks[f"{season_name}ExtendedPeakLoad"] >
             peaks[f"{season_name}PeakLoad"] * BOUNDARY_FLAG_LOAD_RATIO))
        flagged = peaks[peaks[f"{season_name}PeakAtWindowBoundary"]]
        for _, row in flagged.iterrows():
            print(
                f"WARNING: {row[region_col]} {season_name.lower()} peak "
                f"(day {int(row[f'{season_name}PeakDay'])}) sits at the "
                f"season window boundary — a {BOUNDARY_CHECK_BUFFER_DAYS}-"
                f"day-wider window finds a "
                f"{row[f'{season_name}ExtendedPeakLoad'] / row[f'{season_name}PeakLoad']:.1f}x"
                f" higher peak on day "
                f"{int(row[f'{season_name}ExtendedPeakDay'])}. Keeping the "
                f"official-window value, but this region likely has no "
                f"real interior {season_name.lower()} peak (e.g. load "
                "ramps straight from winter into the summer cooling "
                "season).")
        out_rows.append(peaks.drop(
            columns=[f"{season_name}ExtendedPeakDay",
                     f"{season_name}ExtendedPeakLoad"]).set_index(
            region_col))

    result = out_rows[0].join(out_rows[1], how="outer").reset_index()
    for season_name in ("Winter", "Summer"):
        result[f"{season_name}PeakDate"] = result[
            f"{season_name}PeakDay"].apply(
            lambda d: (datetime.date(2018, 1, 1) +
                       datetime.timedelta(days=int(d) - 1)).strftime(
                "%b %-d"))
    return result[[
        region_col,
        "WinterPeakDay", "WinterPeakDate", "WinterPeakLoad",
        "WinterPeakAtWindowBoundary",
        "SummerPeakDay", "SummerPeakDate", "SummerPeakLoad",
        "SummerPeakAtWindowBoundary"]]


def compute_for_geography(geo_label, region_col, stock_version):
    com_path = f"{OUTPUT_DIR}/commercial_{geo_label}_{stock_version}.csv"
    res_path = f"{OUTPUT_DIR}/residential_{geo_label}_{stock_version}.csv"
    for p in (com_path, res_path):
        if not os.path.isfile(p):
            raise FileNotFoundError(
                f"{p} not found — run update_tsv.py --get_stockdata first")

    print(f"Loading {com_path}...")
    com_hourly = load_total_hourly(
        com_path, region_col, COMMERCIAL_ENERGY_COLS, is_commercial=True)
    print(f"Loading {res_path}...")
    res_hourly = load_total_hourly(
        res_path, region_col, RESIDENTIAL_ENERGY_COLS, is_commercial=False)

    combined = pd.concat([com_hourly, res_hourly], ignore_index=True)
    combined = combined.groupby(
        [region_col, "timestamp_hour"], as_index=False)["total"].sum()

    return find_peak_days(combined, region_col)


def main(stock_version):
    emm_result = compute_for_geography("emm", "emm", stock_version)
    emm_out = os.path.join(TSV_DATA_DIR, "tsv_peak_days_EMM.csv")
    emm_result.rename(columns={"emm": "Region"}).to_csv(
        emm_out, index=False)
    print(f"{emm_out} is successfully saved!")

    state_result = compute_for_geography("state", "state", stock_version)
    state_out = os.path.join(TSV_DATA_DIR, "tsv_peak_days_State.csv")
    state_result.rename(columns={"state": "Region"}).to_csv(
        state_out, index=False)
    print(f"{state_out} is successfully saved!")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--stock_version", type=str, default="2025",
        choices=["2024", "2025"],
        help="ComStock/ResStock release year whose cached csv/ files to "
        "read (must already be downloaded via update_tsv.py "
        "--get_stockdata).")
    opts = parser.parse_args()
    main(opts.stock_version)
