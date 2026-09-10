"""Build/update tech_crosswalk.csv, linking Scout technology tokens to BTB rows.

`meas_in` (the "meas_in" sheet of bss_meas_v2.xlsx) refers to technologies
using Scout's short internal tokens (e.g. "ASHP", "central AC", "furnace
(NG)", "boiler (NG)"). The BTB CSVs (./raw/btb_residential.csv,
./raw/btb_commercial.csv) identify technologies by a "Display Name" plus
Component/Technology-Measure/Fuel Type columns, and only sometimes fill in
a "Mapping to Most Granular EIA/Scout Tech/Measure Name" column -- that
column is informative when present but is blank for some technologies that
are otherwise clearly identifiable (e.g. "Furnace Gas-fired" has no mapping
entry at all), so matching here is keyword-based against the descriptive
columns rather than a hard requirement on that column.

This script is meant to be re-run as BTB data updates, but should not
clobber human edits: any (scout_technology, sector) pair already present in
tech_crosswalk.csv is left untouched unless --refresh is passed.

Each matched Scout technology is expanded into 4 rows, one per meas_in
efficiency tier (Ref. Case, Min. Efficiency, ESTAR, Best), using a default
mapping from tier to BTB "Projection Scenario" + regression/cost "bound"
that the user asked to have proposed here for review rather than trusted
outright -- see TIER_DEFAULTS below and the README. In particular, note
that tiers here always draw from the *same* matched BTB Technology ID,
varying only scenario/bound/year; where BTB has a genuinely distinct
higher-efficiency product class (e.g. condensing vs. non-condensing gas
boilers), this script does not attempt to auto-detect and switch to it --
such cases surface naturally as ambiguous (multiple candidates) matches
that need manual resolution, or should be redirected manually in the CSV.

Usage (from this directory):
    python build_tech_crosswalk.py
    python build_tech_crosswalk.py --refresh   # recompute all rows
"""

import argparse
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "raw"
XLSX_PATH = BASE_DIR / "bss_meas_v2.xlsx"
CROSSWALK_PATH = BASE_DIR / "tech_crosswalk.csv"

# meas_in efficiency tier -> default BTB Projection Scenario/year/bound.
# "bound" uses a canonical Low/Typical/High vocabulary; translated to BTB's
# actual column-naming (regression metrics use Lower Bound/Typical/Upper
# Bound, costs use Low/Mid/High) in populate_meas_in_from_btb.py.
TIER_DEFAULTS = {
    "Ref. Case": {"scenario": "Reference", "year": 2023, "bound": "Typical"},
    "Min. Efficiency": {"scenario": "Reference", "year": 2023, "bound": "Low"},
    "ESTAR": {"scenario": "Advanced", "year": 2023, "bound": "Typical"},
    "Best": {"scenario": "Advanced", "year": 2023, "bound": "High"},
}

# Whichever meas_in unit label (COP, AFUE, BTU out/BTU in, UEF, ...) a given
# row actually uses for a matched technology is only known once
# populate_meas_in_from_btb.py looks at that specific row -- so this script
# just records which BTB regression metric would supply the performance
# value, and leaves the convertibility check (see unit_conversions.py) to
# the populate step.
CROSSWALK_COLUMNS = [
    "scout_technology", "sector", "tier", "btb_technology_id",
    "btb_display_name", "btb_mapping_name", "btb_metric_name",
    "projection_scenario", "projection_year", "bound", "match_confidence",
    "needs_review", "notes",
]

# Rule table: scout_technology -> matching rule(s). Each rule is matched
# against a lowercased concatenation of Display Name / Component /
# Technology-Measure / Fuel Type text in the named sector's BTB CSV.
# "include" keywords must ALL appear; "exclude" keywords must NONE appear.
# Only technologies with a clear, defensible rule are listed here -- every
# other Scout technology used in meas_in falls through to a needs_review
# row with no BTB match, rather than being guessed at.
MATCH_RULES = {
    # -- Residential HVAC --
    "ASHP": [("residential", ["air source heat pump"], ["new circuit"])],
    "GSHP": [("residential", ["ground source heat pump"], [])],
    "boiler (distillate)": [("residential", ["boiler", "oil"], ["gas"])],
    "furnace (NG)": [
        ("residential", ["furnace", "gas"], ["air conditioner"])],
    "furnace (distillate)": [("residential", ["furnace", "oil"], [])],
    "central AC": [
        ("residential", ["central air conditioner"], ["furnace"])],
    "room AC": [("residential", ["room air conditioner"], ["connected"])],
    "resistance heat": [
        ("residential", ["furnace", "electric resistance"], [])],
    # -- Residential Water Heating --
    "HPWH": [
        ("residential", ["water heater", "hp tank"],
         ["new circuit", "240v"])],
    "elec_water_heater": [
        ("residential", ["water heater", "electric instantaneous"], [])],
    # -- Residential Lighting --
    "general service (LED)": [("residential", ["led a19"], [])],
    # -- Residential Appliances --
    "dishwasher": [("residential", ["dishwasher"], ["connected"])],
    "electric dryer": [
        ("residential", ["clothes dryer", "electric"],
         ["compact", "connected", "gas", "heat pump"])],
    # -- Residential Cooking --
    "electric range": [
        ("residential", ["cooking range", "electric"], ["induction"])],
    "induction": [("residential", ["cooking range", "induction"], [])],

    # -- Commercial HVAC --
    "rooftop_ASHP-cool": [("commercial", ["rtu heat pump", "standard"], [])],
    "rooftop_ASHP-heat": [("commercial", ["rtu heat pump", "standard"], [])],
    "rooftop_AC": [
        ("commercial", ["electric rooftop unit"], ["heat pump", "gas heat"])],
    "res_type_central_AC": [
        ("residential", ["central air conditioner"], ["furnace"])],
    "comm_GSHP-cool": [
        ("commercial", ["ground source heat pump"], [])],
    "comm_GSHP-heat": [
        ("commercial", ["ground source heat pump"], [])],
    "centrifugal_chiller": [
        ("commercial", ["centrifugal chiller", "water-cooled"], [])],
    "scroll_chiller": [
        ("commercial", ["scroll chiller", "air-cooled"], [])],
    "screw_chiller": [
        ("commercial", ["screw chiller", "air-cooled"], [])],
    "reciprocating_chiller": [
        ("commercial", ["reciprocating chiller", "air-cooled"], [])],
    "gas_chiller": [
        ("commercial", ["gas-fired chillers", "water cooled"], [])],
    "gas_eng-driven_RTAC": [
        ("commercial", ["gas-fired engine-drive"], [])],
    "pkg_terminal_AC-cool": [
        ("commercial", ["packaged terminal air conditioner"], [])],
    "pkg_terminal_HP-cool": [
        ("commercial", ["heat pump", "packaged terminal"], [])],
    "pkg_terminal_HP-heat": [
        ("commercial", ["heat pump", "packaged terminal"], [])],
    "gas_boiler": [("commercial", ["boiler", "gas-fired"], [])],
    # BTB has separate "Electric Steam" and "Electric Hot Water" commercial
    # boiler entries; hot water is picked as the more common distribution
    # type -- review and repoint to the steam variant if a given measure
    # specifically concerns steam heating.
    "elec_boiler": [("commercial", ["boiler", "electric"], ["steam"])],
    "oil_boiler": [("commercial", ["boiler", "oil-fired"], [])],
    "gas_furnace": [("commercial", ["furnace", "gas-fired"], [])],
    "oil_furnace": [("commercial", ["furnace", "oil-fired"], [])],
    "elec_res-heater": [
        ("commercial", ["unit heater", "electric"], [])],
    "VAV_Vent": [
        ("commercial", ["variable air volume system"], [])],
    "CAV_Vent": [
        ("commercial", ["constant air volume system"], [])],
    # -- Commercial Water Heating --
    "elec_range-combined": [
        ("commercial", ["electric range", "griddle"], [])],

    # -- Commercial Lighting --
    "LED": [("commercial", ["led troffer", "panel"], ["dimming", "control"])],

    # -- Commercial Refrigeration --
    "Commercial Ice Machines": [
        ("commercial", ["ice machine", "standard"], [])],
    "Commercial Beverage Merchandisers": [
        ("commercial", ["beverage merchandisers", "standard"], [])],
    "Commercial Refrigerated Vending Machines": [
        ("commercial", ["refrigerated vending machine", "standard"], [])],
    "Commercial Reach-In Freezers": [
        ("commercial", ["reach-in freezer"], [])],
    "Commercial Reach-In Refrigerators": [
        ("commercial", ["reach-in refrigerator"], [])],
    "Commercial Walk-In Freezers": [
        ("commercial", ["walk-in", "freezer"], [])],
    "Commercial Walk-In Refrigerators": [
        ("commercial", ["walk-in", "cooler"], [])],
    "Commercial Supermarket Display Cases": [
        ("commercial", ["supermarket display cases"], [])],
}


def load_btb(sector):
    """Load a BTB CSV and return it with a normalized 'search_text' column.

    Args:
        sector (str): "residential" or "commercial".

    Returns:
        DataFrame with an added lowercased 'search_text' column and a
        normalized 'tech_id' column (BTB uses different ID column names
        for the two sectors).
    """

    fname = "btb_residential.csv" if sector == "residential" \
        else "btb_commercial.csv"
    path = RAW_DIR / fname
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found -- run download_btb_data.py first.")
    df = pd.read_csv(path, low_memory=False)
    id_col = "Technology ID" if "Technology ID" in df.columns \
        else "Technology/Measure ID"
    df = df.rename(columns={id_col: "tech_id"})
    text_cols = ["Display Name", "Component", "Technology/Measure",
                 "Fuel Type"]
    df["search_text"] = df[text_cols].astype(str).agg(" | ".join, axis=1) \
        .str.lower()
    return df


def find_candidates(df, include_kw, exclude_kw):
    """Return distinct BTB tech_ids whose search_text matches a rule."""

    mask = df["search_text"].apply(
        lambda t: all(kw in t for kw in include_kw)
        and not any(kw in t for kw in exclude_kw))
    matched = df[mask].dropna(subset=["tech_id"])
    return matched.drop_duplicates(subset=["tech_id"])


def scout_technologies_in_use(xlsx_path):
    """Collect every distinct technology token referenced in meas_in."""

    df = pd.read_excel(xlsx_path, sheet_name="meas_in")
    techs = set()
    for col in ["Baseline Technology", "Switched to Technology"]:
        for val in df[col].dropna():
            for part in str(val).split(";"):
                part = part.strip()
                if part:
                    techs.add(part)
    return techs


def performance_metric_for_row(row):
    """Pick whichever of a BTB row's two regression metrics is an
    efficiency-type metric convertible to Scout units (see
    unit_conversions.py), preferring metric 2 (where such metrics were
    observed to live in the source data)."""

    for i in (2, 1):
        metric_name = row.get(f"Regression metric {i} - Metric")
        if pd.notna(metric_name):
            return i, metric_name
    return None, None


def build_rows_for_technology(scout_tech, rules):
    """Match one Scout technology token against BTB data and expand across
    all four meas_in efficiency tiers.

    Returns a list of crosswalk row dicts.
    """

    all_candidates = []
    for sector, include_kw, exclude_kw in rules:
        df = load_btb(sector)
        cands = find_candidates(df, include_kw, exclude_kw)
        for _, cand in cands.iterrows():
            all_candidates.append((sector, cand))

    rows = []
    if len(all_candidates) == 0:
        for tier in TIER_DEFAULTS:
            rows.append({
                "scout_technology": scout_tech, "sector": "",
                "tier": tier, "btb_technology_id": "",
                "btb_display_name": "", "btb_mapping_name": "",
                "btb_metric_name": "",
                "projection_scenario": "", "projection_year": "",
                "bound": "", "match_confidence": "none",
                "needs_review": True,
                "notes": "no BTB row matched the authored search rule(s)",
            })
        return rows

    if len(all_candidates) > 1:
        cand_desc = "; ".join(
            f"{sector}#{cand['tech_id']}:{cand['Display Name']}"
            for sector, cand in all_candidates)
        for tier in TIER_DEFAULTS:
            rows.append({
                "scout_technology": scout_tech, "sector": "",
                "tier": tier, "btb_technology_id": "",
                "btb_display_name": "", "btb_mapping_name": "",
                "btb_metric_name": "",
                "projection_scenario": "", "projection_year": "",
                "bound": "", "match_confidence": "ambiguous",
                "needs_review": True,
                "notes": f"{len(all_candidates)} candidate BTB rows matched: "
                         f"{cand_desc}",
            })
        return rows

    sector, cand = all_candidates[0]
    metric_idx, metric_name = performance_metric_for_row(cand)
    needs_review = metric_name is None
    notes = "" if metric_name is not None else (
        "BTB row has no identified performance metric")
    for tier, defaults in TIER_DEFAULTS.items():
        rows.append({
            "scout_technology": scout_tech, "sector": sector,
            "tier": tier, "btb_technology_id": cand["tech_id"],
            "btb_display_name": cand["Display Name"],
            "btb_metric_name": metric_name or "",
            "btb_mapping_name": cand.get(
                "Mapping to Most Granular EIA/Scout Tech/Measure Name", ""),
            "projection_scenario": defaults["scenario"],
            "projection_year": defaults["year"], "bound": defaults["bound"],
            "match_confidence": "high", "needs_review": needs_review,
            "notes": notes,
        })
    return rows


def main(refresh):
    """Build (or incrementally update) tech_crosswalk.csv."""

    existing = None
    if CROSSWALK_PATH.exists() and not refresh:
        existing = pd.read_csv(CROSSWALK_PATH)
        already_covered = set(
            zip(existing["scout_technology"], existing["tier"]))
    else:
        already_covered = set()

    techs = sorted(scout_technologies_in_use(XLSX_PATH) & set(MATCH_RULES))
    skipped = sorted(scout_technologies_in_use(XLSX_PATH) - set(MATCH_RULES))
    print(f"{len(techs)} technologies have an authored match rule; "
          f"{len(skipped)} technologies have no rule yet and are skipped "
          "(add a rule to MATCH_RULES to cover them).")

    new_rows = []
    for scout_tech in techs:
        rules = MATCH_RULES[scout_tech]
        rows = build_rows_for_technology(scout_tech, rules)
        for row in rows:
            if (row["scout_technology"], row["tier"]) not in already_covered:
                new_rows.append(row)

    if existing is not None:
        out = pd.concat(
            [existing, pd.DataFrame(new_rows, columns=CROSSWALK_COLUMNS)],
            ignore_index=True)
    else:
        out = pd.DataFrame(new_rows, columns=CROSSWALK_COLUMNS)

    out = out.sort_values(["scout_technology", "tier"]).reset_index(drop=True)
    out.to_csv(CROSSWALK_PATH, index=False)
    n_review = int(out["needs_review"].astype(bool).sum())
    print(f"Wrote {len(out)} rows to {CROSSWALK_PATH} "
          f"({n_review} flagged needs_review).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build/update the Scout-technology <-> BTB crosswalk.")
    parser.add_argument(
        "--refresh", action="store_true",
        help="Recompute every row instead of only adding missing ones "
             "(overwrites any manual edits).")
    args = parser.parse_args()
    main(args.refresh)
