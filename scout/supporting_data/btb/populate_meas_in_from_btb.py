"""Propose BTB-derived cost/performance/lifetime values for meas_in.

Reads bss_meas_v2.xlsx (sheet "meas_in"), tech_crosswalk.csv (see
build_tech_crosswalk.py), and the raw BTB CSVs, and for every (measure row,
technology) pair covered by a non-`needs_review` crosswalk entry, computes
what the Energy Performance / Installed Cost / Lifetime cells for that
technology *would* be if sourced from BTB.

This never modifies bss_meas_v2.xlsx. It writes bss_meas_v2_btb_proposed.xlsx
alongside it: a copy of meas_in with proposed values substituted in (only
for the specific technology substrings that were resolved -- everything
else in a shared cell, e.g. other technologies not covered by the
crosswalk, is left byte-for-byte as-is), plus a "BTB Diff" sheet listing
every change with its old/new value and matched BTB source, for manual
review before merging anything back into the curated original.

Usage (from this directory):
    python populate_meas_in_from_btb.py
"""

import re
from pathlib import Path

import openpyxl
import pandas as pd

from unit_conversions import convert, to_btb_metric

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "raw"
XLSX_PATH = BASE_DIR / "bss_meas_v2.xlsx"
CROSSWALK_PATH = BASE_DIR / "tech_crosswalk.csv"
OUT_PATH = BASE_DIR / "bss_meas_v2_btb_proposed.xlsx"

SHEET_NAME = "meas_in"

TIER_KEYWORDS = [
    # Longer/more specific strings first so e.g. "ESTAR" doesn't also match
    # a "Min. Efficiency ESTAR ..." style name meant for a different tier.
    ("Min. Efficiency", "Min. Efficiency"),
    ("ESTAR", "ESTAR"),
    ("Best", "Best"),
    ("Ref. Case", "Ref. Case"),
]

# Crosswalk "bound" -> BTB regression-metric column suffix, for tiers whose
# performance comes from BTB. The special bound "Existing" (Min. Efficiency
# and ESTAR) instead keeps the performance already in meas_in, which is set
# by a standard/ENERGY STAR spec rather than by BTB.
REGRESSION_BOUND_COL = {"Typical": "Typical", "High": "High"}
EXISTING_BOUND = "Existing"

# Technologies deliberately crosswalked to the other sector's BTB data
# (commercial measures using residential-type equipment), exempt from the
# row-sector check in main().
CROSS_SECTOR_TECHS = {"res_type_central_AC"}

# Technologies covered by build_tech_crosswalk.py that participate in a
# shared "heating"/"cooling"/"ventilation" Performance Units key rather
# than their own tech-name key (seen in combined-package meas_in rows,
# e.g. "(C) Ref. Case NG Boiler & Chiller"). Used only as a fallback when a
# row's Performance Units cell has no key matching the technology name
# directly.
END_USE_FALLBACK = {
    "heating": [
        "gas_boiler", "elec_boiler", "oil_boiler", "gas_furnace",
        "oil_furnace", "elec_res-heater", "rooftop_ASHP-heat",
        "comm_GSHP-heat", "pkg_terminal_HP-heat", "resistance heat",
        "furnace (NG)", "furnace (distillate)", "boiler (distillate)",
        "ASHP", "GSHP", "HPWH"],
    "cooling": [
        "gas_chiller", "centrifugal_chiller", "scroll_chiller",
        "screw_chiller", "reciprocating_chiller", "rooftop_AC",
        "rooftop_ASHP-cool", "comm_GSHP-cool", "pkg_terminal_AC-cool",
        "pkg_terminal_HP-cool", "gas_eng-driven_RTAC", "central AC",
        "room AC", "ASHP", "GSHP"],
    "ventilation": ["VAV_Vent", "CAV_Vent"],
}


def normalize_btb(df, sector):
    """Rename sector-specific columns to a common schema."""

    id_col = "Technology ID" if "Technology ID" in df.columns \
        else "Technology/Measure ID"
    rename = {id_col: "tech_id"}
    if sector == "commercial":
        rename.update({
            "Year": "Projection Year", "Scenario": "Projection Scenario"})
    return df.rename(columns=rename)


def load_btb_data():
    """Load and normalize both BTB CSVs, keyed by sector name."""

    out = {}
    for sector, fname in [
            ("residential", "btb_residential.csv"),
            ("commercial", "btb_commercial.csv")]:
        path = RAW_DIR / fname
        if not path.exists():
            raise FileNotFoundError(
                f"{path} not found -- run download_btb_data.py first.")
        out[sector] = normalize_btb(
            pd.read_csv(path, low_memory=False), sector)
    return out


def tier_for_name(name):
    """Infer a meas_in efficiency tier from a measure's Name string."""

    if not isinstance(name, str):
        return None
    for keyword, tier in TIER_KEYWORDS:
        if keyword in name:
            return tier
    return None


# Cost Units a BTB installed cost can be written into: whole-unit costs
# ("2023$/unit") or costs per kBtu/h of heating, cooling or water heating
# capacity, in 2023$ (BTB's dollar year) or 2022$. A 2022$ row is only
# replaced when it holds a single cost (nothing in the row stays in the old
# dollar year), and its Cost Units are then relabeled as 2023$.
# Per-capacity costs are the whole-unit $2023 cost divided by the BTB
# regression's Typical capacity expressed in kBtu/h (see capacity_kbtuh),
# as done in the "BTB Key Costs" sheet's "div capacity" columns.
_COST_UNITS = re.compile(
    r"(20\d\d)\$/(unit|kBtu/h (?:heating|cooling|water heating))$")
COST_UNITS_YEARS = {2022, 2023}


def cost_units_info(units):
    """Return (dollar year, is_per_capacity) for a supported Cost Units
    string, or None if the units are not supported."""

    match = _COST_UNITS.match(units) if isinstance(units, str) else None
    if not match or int(match.group(1)) not in COST_UNITS_YEARS:
        return None
    return int(match.group(1)), match.group(2) != "unit"


def relabel_cost_units(units):
    """The same Cost Units, in 2023$."""

    return units.replace(units[:4], "2023", 1)

# BTB capacity unit (lowercased) -> multiplier to kBtu/h.
CAPACITY_TO_KBTUH = {
    "tons": 12.0, "kbtu/h": 1.0, "mbh": 1.0, "btu/h": 0.001,
    "btu/hr": 0.001, "kw": 3.412}

# Breakthrough ("Brk.") measures are assumed costs, not taken from BTB.
_BREAKTHROUGH_NAME = re.compile(r"\bBrk\.?\b", re.IGNORECASE)

# Phrases in a row's Cost Source Notes showing its installed cost is not a
# plain BTB cost for the technology (adders such as a typical furnace for
# dual-fuel heat pumps, oil-tank removal, a scaled breakthrough cost, a cost
# for the technology switched to but keyed under the baseline's name, ...).
_COMPOSITE_COST_NOTE = re.compile(
    r"also add|tank removal|half the cost|halve|secondary heater|paired"
    r"|drilling|switched to", re.IGNORECASE)


def capacity_kbtuh(btb_row):
    """The BTB row's Typical capacity (regression metric 1) in kBtu/h, or
    None if metric 1 is not a heating/cooling capacity in a known unit."""

    metric = str(btb_row.get("Regression metric 1 - Metric")).lower()
    if "capacity" not in metric and "heat output" not in metric:
        return None
    factor = CAPACITY_TO_KBTUH.get(
        str(btb_row.get("Regression metric 1 - Unit")).strip().lower())
    value = parse_currency(btb_row.get("Regression metric 1 - Typical"))
    if factor is None or not value:
        return None
    return value * factor


def cost_skip_reason(row):
    """Return why this row's installed cost must not be replaced with a BTB
    cost, or None if it may be."""

    units = row.get("Cost Units")
    if cost_units_info(units) is None:
        return (f"Cost Units are {units!r}, not a whole-unit or "
                "per-heating/cooling/water-heating-capacity cost; "
                "left as-is")
    notes = row.get("Cost Source Notes")
    if isinstance(notes, str) and _COMPOSITE_COST_NOTE.search(notes):
        return ("cost notes describe a composite/adjusted cost (adder or "
                "scaling); left as-is")
    return None


def sector_for_name(name):
    """Infer a meas_in row's sector from the "(R)"/"(C)" prefix of its Name
    (present on every row, and consistent with its Building Type column)."""

    if isinstance(name, str):
        if name.startswith("(R)"):
            return "residential"
        if name.startswith("(C)"):
            return "commercial"
    return None


def techs_for_row(row):
    """Ordered, de-duplicated technology tokens referenced by a meas_in row."""

    seen = []
    for col in ["Baseline Technology", "Switched to Technology"]:
        val = row.get(col)
        if isinstance(val, str):
            for part in val.split(";"):
                part = part.strip()
                if part and part not in seen:
                    seen.append(part)
    return seen


def find_value_for_key(cell, key):
    """Return the raw (unparsed) value substring for `key` in a nested
    "key: value; key2: value2" cell, or the whole cell if it has no nested
    keys at all, or None if `key` is not present in a nested cell."""

    if not isinstance(cell, str):
        return None if pd.isna(cell) else str(cell)
    if ":" not in cell:
        return cell.strip()
    pattern = re.compile(
        re.escape(key) + r"\s*:\s*([^;]+)", re.IGNORECASE)
    match = pattern.search(cell)
    return match.group(1).strip() if match else None


def unit_for_tech(perf_units_cell, tech):
    """Resolve the meas_in performance unit that applies to `tech` in a
    given row, trying a direct tech-name key first and falling back to the
    row's heating/cooling/ventilation end-use key (see END_USE_FALLBACK)."""

    direct = find_value_for_key(perf_units_cell, tech)
    if direct:
        return direct
    if isinstance(perf_units_cell, str):
        for end_use, techs in END_USE_FALLBACK.items():
            if tech in techs:
                via_end_use = find_value_for_key(perf_units_cell, end_use)
                if via_end_use:
                    return via_end_use
    return None


def owner_tech(row):
    """The one technology an un-keyed cell in this row (a bare value, or a
    bare "new: X; existing: Y" cost) describes: the Switched-to technology,
    or the Baseline technology for rows with no switch (e.g. Ref. Case).
    None if that is not a single technology."""

    for col in ["Switched to Technology", "Baseline Technology"]:
        val = row.get(col)
        if isinstance(val, str) and val.strip():
            parts = [p.strip() for p in val.split(";") if p.strip()]
            return parts[0] if len(parts) == 1 else None
    return None


_BARE_COST = re.compile(
    r"\s*new\s*:\s*[^;:]+;\s*existing\s*:\s*[^;:]+", re.IGNORECASE)


def is_unkeyed(cell):
    """True if a meas_in cell holds a single un-keyed value (blank, numeric,
    plain text, or a bare "new: X; existing: Y" cost) rather than
    "technology: value" pairs."""

    if not isinstance(cell, str):
        return True
    return ":" not in cell or bool(_BARE_COST.fullmatch(cell))


# BTB metric names (lowercased) that describe cooling vs. heating output,
# used to pick the right "cooling:"/"heating:" key when a meas_in cell stores
# a technology's performance by end use rather than by technology name
# (e.g. "heating: 2.58; cooling: 4.4" for an ASHP).
COOLING_METRICS = {
    "seer", "seer1", "seer2", "eer", "ceer", "ieer", "cooling cop"}
HEATING_METRICS = {"hspf", "hspf2", "afue", "heating cop"}


def metric_conflicts_with_token(tech, metric_name):
    """True if `tech` is a heating-only or cooling-only token (suffix "-heat"
    or "-cool") and the crosswalk's BTB metric is for the other end use.

    BTB often gives one metric for a row that several Scout tokens map to
    (e.g. only Heating COP for ground source heat pumps), so the metric can't
    be used as the performance of the token for the other end use."""

    metric = metric_name.strip().lower() \
        if isinstance(metric_name, str) else ""
    return (tech.endswith("-cool") and metric in HEATING_METRICS) or \
        (tech.endswith("-heat") and metric in COOLING_METRICS)


def perf_key_for_tech(perf_cell, tech, metric_name, owner):
    """Return the key under which `tech`'s performance is stored in a
    meas_in Energy Performance cell: the technology name, the end-use key
    ("heating"/"cooling") implied by the BTB metric, or None if neither is
    present. A cell with no nesting holds one value, which belongs to `owner`
    (see owner_tech)."""

    if is_unkeyed(perf_cell):
        return tech if tech == owner else None
    flags = re.IGNORECASE
    if re.search(re.escape(tech) + r"\s*:", perf_cell, flags):
        return tech
    metric = metric_name.strip().lower() \
        if isinstance(metric_name, str) else ""
    end_use = "cooling" if metric in COOLING_METRICS else \
        "heating" if metric in HEATING_METRICS else None
    if end_use and re.search(end_use + r"\s*:", perf_cell, flags):
        return end_use
    return None


def replace_value_for_key(cell, key, new_value):
    """Substitute the value for `key` in a nested cell (or replace the
    whole cell if it has no nested keys), leaving all other keys/formatting
    untouched. Returns the original cell unchanged if `key` is not found in
    a nested cell (caller should not have called this in that case)."""

    if not isinstance(cell, str):
        return new_value
    if ":" not in cell:
        return new_value
    pattern = re.compile(
        r"(" + re.escape(key) + r"\s*:\s*)([^;]+)", re.IGNORECASE)
    return pattern.sub(lambda m: m.group(1) + new_value, cell, count=1)


def replace_cost_for_key(cell, key, new_cost):
    """Same as replace_value_for_key, but for the "key: new: X; key:
    existing: Y" nesting used by the Installed Cost column."""

    if is_unkeyed(cell):
        # No existing nested cost structure to preserve -- write a fresh
        # "new: X; existing: Y" pair for this (single) technology.
        return f"new: {new_cost['new']}; existing: {new_cost['existing']}"
    result = cell
    any_found = False
    for sub_key, val in new_cost.items():
        pattern = re.compile(
            r"(" + re.escape(key) + r"\s*:\s*" + re.escape(sub_key) +
            r"\s*:\s*)([^;]+)", re.IGNORECASE)
        if pattern.search(result):
            any_found = True
            result = pattern.sub(
                lambda m: m.group(1) + str(val), result, count=1)
    return result if any_found else cell


def get_btb_row(btb_data, entry):
    """Look up the single BTB row matching a crosswalk entry's technology
    ID, projection year, and projection scenario."""

    df = btb_data[entry["sector"]]
    match = df[
        (df["tech_id"] == entry["btb_technology_id"])
        & (df["Projection Year"] == entry["projection_year"])
        & (df["Projection Scenario"] == entry["projection_scenario"])]
    if len(match) != 1:
        return None
    return match.iloc[0]


def parse_currency(val):
    """Parse a BTB cost value (e.g. "$5,158" or 5158.0) into a float."""

    if pd.isna(val):
        return None
    if isinstance(val, str):
        val = val.replace("$", "").replace(",", "").strip()
        if not val:
            return None
    try:
        return float(val)
    except ValueError:
        return None


def is_zero_cost_placeholder(old_cost):
    """True if a technology's existing cost has a "new" or "existing"
    sub-value of exactly 0. A real installed cost is never $0, so this
    normally means the cost was deliberately zeroed out because the
    technology shares physical equipment with a paired heating/cooling
    technology elsewhere in the same row (e.g. a heat pump's cost entered
    once under the "heat" entry and zeroed under "cool" to avoid double-
    counting total installed cost) -- such rows are left alone rather than
    overwritten with a full BTB cost that would reintroduce that
    double-count.
    """

    if not isinstance(old_cost, str):
        return parse_currency(old_cost) == 0
    if ":" not in old_cost:
        return parse_currency(old_cost) == 0
    for part in old_cost.split(";"):
        if ":" in part:
            val = parse_currency(part.split(":", 1)[1])
            if val == 0:
                return True
    return False


def installation_multiplier(btb_row, kind):
    """Installation cost multiplier (installed = retail * multiplier, or
    retail + adder for adder-based technologies, which have multiplier 1)
    for `kind` "new" or "retrofit".

    Residential BTB rows give it directly. Commercial rows don't, so it is
    recovered from the row's Low/Mid/High retail and installed prices: per
    the BTB documentation a technology uses either an adder or a multiplier,
    so whichever of the two reproduces all three installed prices is used.

    Returns None if it cannot be determined (e.g. no retail price).
    """

    suffix = "New Construction" if kind == "new" else "Retrofit"
    direct = parse_currency(btb_row.get(f"Installation Multiplier - {suffix}"))
    if direct is not None:
        return direct
    installed_col = ("Typical New Construction Installed Cost ($2023)"
                     if kind == "new"
                     else "Typical Retrofit Installed Cost ($2023)")
    retail = [parse_currency(btb_row.get(
        f"Typical Retail Price ($2023) - {q}")) for q in ("Low", "Mid", "High")]
    installed = [parse_currency(btb_row.get(f"{installed_col} - {q}"))
                 for q in ("Low", "Mid", "High")]
    if None in retail or None in installed or retail[1] <= 0:
        return None
    adder = installed[1] - retail[1]
    if all(abs((i - r) - adder) <= 0.5 + 0.002 * abs(i)
           for r, i in zip(retail, installed)):
        return 1.0
    multiplier = installed[1] / retail[1]
    if all(abs(i - multiplier * r) <= 0.5 + 0.005 * abs(i)
           for r, i in zip(retail, installed)):
        return multiplier
    return None


def compute_cost(btb_row, metric_idx=None, perf_value=None):
    """Return {"new": ..., "existing": ...} installed cost ($2023).

    Starts from BTB's precomputed Mid installed cost, which is at the Typical
    performance level, and moves it to `perf_value` (a value of regression
    metric `metric_idx`, in BTB units) using the retail price regression:

        retail change = coef2_mid * (perf_value - typical) * unit_multiplier
        installed     = installed_typical + multiplier * retail change

    (all other regression inputs, e.g. capacity, stay at Typical). This is
    equivalent to evaluating the full regression and applying the
    installation multiplier/adder, but always agrees with BTB at Typical.
    Only regression metric 2 is treated as a performance metric.

    Returns:
        (cost dict or None, True if the cost was moved off the Typical
        performance level using the regression).
    """

    new_val = parse_currency(btb_row.get(
        "Typical New Construction Installed Cost ($2023) - Mid"))
    existing_val = parse_currency(btb_row.get(
        "Typical Retrofit Installed Cost ($2023) - Mid"))
    if new_val is None or existing_val is None:
        return None, False

    typical = parse_currency(btb_row.get("Regression metric 2 - Typical"))
    coef = parse_currency(btb_row.get("Regression metric 2 - Coefficient-Mid"))
    if metric_idx != 2 or perf_value is None or typical is None or \
            coef is None:
        return {"new": round(new_val), "existing": round(existing_val)}, False

    unit_mult = parse_currency(btb_row.get("Typical unit multiplier")) or 1.0
    retail_change = coef * (perf_value - typical) * unit_mult
    if retail_change == 0:
        return {"new": round(new_val), "existing": round(existing_val)}, True
    mult_new = installation_multiplier(btb_row, "new")
    mult_ret = installation_multiplier(btb_row, "retrofit")
    if mult_new is None or mult_ret is None:
        return {"new": round(new_val), "existing": round(existing_val)}, False
    return {"new": round(new_val + mult_new * retail_change),
            "existing": round(existing_val + mult_ret * retail_change)}, True


def main():
    """Build the BTB-proposed workbook and diff sheet."""

    btb_data = load_btb_data()
    crosswalk = pd.read_csv(CROSSWALK_PATH)
    crosswalk = crosswalk[~crosswalk["needs_review"].astype(bool)]
    crosswalk_by_tech_tier = {
        (row["scout_technology"], row["sector"], row["tier"]): row
        for _, row in crosswalk.iterrows()}

    meas_in_df = pd.read_excel(XLSX_PATH, sheet_name=SHEET_NAME)
    col_index = {name: i + 1 for i, name in enumerate(meas_in_df.columns)}

    wb = openpyxl.load_workbook(XLSX_PATH)
    ws = wb[SHEET_NAME]

    diff_rows = []
    for excel_row, (_, row) in enumerate(meas_in_df.iterrows(), start=2):
        if _BREAKTHROUGH_NAME.search(str(row.get("Name"))):
            continue
        tier = tier_for_name(row.get("Name"))
        if tier is None:
            continue
        # Multiple technologies in this row can share the same Energy
        # Performance/Installed Cost/Lifetime cell (e.g. a combined
        # heating+cooling package). Track each cell's contents here and
        # chain edits through it -- writing straight from the original
        # pandas row on every technology would make each technology's
        # edit clobber the previous one's, since they'd all overwrite the
        # same cell starting from its pre-edit text.
        cell_state = {
            "Energy Performance": row.get("Energy Performance"),
            "Installed Cost": row.get("Installed Cost"),
            "Lifetime": row.get("Lifetime"),
        }
        owner = owner_tech(row)
        row_sector = sector_for_name(row.get("Name"))
        skip_cost_reason = cost_skip_reason(row)
        for tech in techs_for_row(row):
            # Tokens shared by residential and commercial measures (e.g.
            # "HPWH") have a crosswalk entry per sector. A token with only
            # the other sector's entry is left alone, unless it is
            # deliberately crosswalked across sectors.
            entry = crosswalk_by_tech_tier.get((tech, row_sector, tier))
            if entry is None and tech in CROSS_SECTOR_TECHS:
                entry = next(
                    (crosswalk_by_tech_tier[(tech, sector, tier)]
                     for sector in ("residential", "commercial")
                     if (tech, sector, tier) in crosswalk_by_tech_tier),
                    None)
            if entry is None:
                continue
            btb_row = get_btb_row(btb_data, entry)
            if btb_row is None:
                continue

            # -- Performance --
            # Ref. Case and Best take performance from BTB (Typical / High).
            # Min. Efficiency and ESTAR ("Existing" bound) keep the
            # standard-defined performance already in meas_in; it is only
            # used below as the point at which cost is evaluated.
            perf_cell = cell_state["Energy Performance"]
            units_cell = row.get("Performance Units")
            metric_idx = None
            for i in (1, 2):
                if btb_row.get(f"Regression metric {i} - Metric") == \
                        entry["btb_metric_name"]:
                    metric_idx = i
                    break
            perf_key = perf_key_for_tech(
                perf_cell, tech, entry["btb_metric_name"], owner)
            metric_conflict = metric_conflicts_with_token(
                tech, entry["btb_metric_name"])
            target_unit = (
                find_value_for_key(units_cell, perf_key) if perf_key
                else None) or unit_for_tech(units_cell, tech)
            old_val = find_value_for_key(perf_cell, perf_key) \
                if perf_key else None
            keep_existing = entry["bound"] == EXISTING_BOUND
            cost_perf = None  # performance (BTB units) to evaluate cost at
            if metric_idx and not keep_existing:
                raw_val = btb_row.get(
                    f"Regression metric {metric_idx} - "
                    f"{REGRESSION_BOUND_COL[entry['bound']]}")
                cost_perf = parse_currency(raw_val)
                converted = convert(
                    entry["btb_metric_name"], target_unit, raw_val) \
                    if target_unit and pd.notna(raw_val) else None
                if metric_conflict and perf_key:
                    diff_rows.append({
                        "Name": row.get("Name"), "technology": tech,
                        "column": "Energy Performance",
                        "old_value": old_val, "new_value": "(skipped)",
                        "btb_technology_id": entry["btb_technology_id"],
                        "btb_display_name": entry["btb_display_name"],
                        "projection_scenario": entry["projection_scenario"],
                        "projection_year": entry["projection_year"],
                        "notes": f"BTB metric {entry['btb_metric_name']!r} "
                                 "is for the other end use than this token; "
                                 "performance left as-is",
                    })
                elif converted is not None and perf_key:
                    new_val_str = f"{converted:.3g}"
                    if old_val != new_val_str:
                        cell_state["Energy Performance"] = \
                            replace_value_for_key(
                                perf_cell, perf_key, new_val_str)
                        ws.cell(
                            row=excel_row,
                            column=col_index["Energy Performance"]).value \
                            = cell_state["Energy Performance"]
                        diff_rows.append({
                            "Name": row.get("Name"), "technology": tech,
                            "column": "Energy Performance",
                            "old_value": old_val, "new_value": new_val_str,
                            "btb_technology_id": entry["btb_technology_id"],
                            "btb_display_name": entry["btb_display_name"],
                            "projection_scenario":
                                entry["projection_scenario"],
                            "projection_year": entry["projection_year"],
                        })
            elif metric_idx and keep_existing and target_unit and old_val \
                    and not metric_conflict:
                cost_perf = to_btb_metric(
                    entry["btb_metric_name"], target_unit, old_val,
                    parse_currency(btb_row.get(
                        f"Regression metric {metric_idx} - Typical")))

            # -- Installed cost --
            units_info = cost_units_info(row.get("Cost Units"))
            cost, used_regression = compute_cost(
                btb_row, metric_idx, cost_perf)
            cost_note = "" if used_regression else (
                "cost is BTB's Mid installed cost at Typical performance")
            # Without a usable regression the cost is only available at
            # Typical performance, which is wrong for other tiers.
            extra_skip = None
            if cost is not None and not used_regression and \
                    entry["bound"] != "Typical" and cost_perf is not None:
                extra_skip = (
                    "BTB cost regression not usable for this row, so cost "
                    "cannot be evaluated at this tier's performance; "
                    "left as-is")
            elif cost is not None and not used_regression and \
                    entry["bound"] == EXISTING_BOUND:
                extra_skip = (
                    "kept performance could not be placed on BTB's metric "
                    "scale, so cost cannot be evaluated at it; left as-is")
            elif cost is not None and units_info and units_info[1]:
                capacity = capacity_kbtuh(btb_row)
                if capacity is None:
                    extra_skip = (
                        "Cost Units are per kBtu/h but BTB capacity is not "
                        "a known heating/cooling capacity unit; left as-is")
                else:
                    cost = {k: round(v / capacity, 2)
                            for k, v in cost.items()}
                    cost_note = (cost_note + "; " if cost_note else "") + \
                        f"divided by BTB typical capacity ({capacity:.4g} " \
                        "kBtu/h)"
            row_skip_reason = skip_cost_reason or extra_skip
            cost_cell = cell_state["Installed Cost"]
            cost_unkeyed = is_unkeyed(cost_cell)
            cost_applies = (tech == owner) if cost_unkeyed else bool(
                re.search(re.escape(tech) + r"\s*:", cost_cell,
                          re.IGNORECASE))
            if cost_applies and not row_skip_reason and cost is not None and \
                    units_info and units_info[0] != 2023 and \
                    not cost_unkeyed:
                row_skip_reason = (
                    f"Cost Units are {row.get('Cost Units')!r} but this row "
                    "has several technology costs; replacing one with a "
                    "$2023 BTB cost would mix dollar years; left as-is")
            if cost_applies and row_skip_reason:
                cost = None
                diff_rows.append({
                    "Name": row.get("Name"), "technology": tech,
                    "column": "Installed Cost",
                    "old_value": cost_cell if cost_unkeyed
                    else find_value_for_key(cost_cell, tech),
                    "new_value": "(skipped)",
                    "btb_technology_id": entry["btb_technology_id"],
                    "btb_display_name": entry["btb_display_name"],
                    "projection_scenario": entry["projection_scenario"],
                    "projection_year": entry["projection_year"],
                    "notes": row_skip_reason,
                })
            if cost is not None:
                if cost_applies:
                    old_cost = cost_cell if cost_unkeyed \
                        else find_value_for_key(cost_cell, tech)
                    if is_zero_cost_placeholder(old_cost):
                        diff_rows.append({
                            "Name": row.get("Name"), "technology": tech,
                            "column": "Installed Cost",
                            "old_value": old_cost, "new_value": "(skipped)",
                            "btb_technology_id": entry["btb_technology_id"],
                            "btb_display_name": entry["btb_display_name"],
                            "projection_scenario":
                                entry["projection_scenario"],
                            "projection_year": entry["projection_year"],
                            "notes": "existing cost is $0 -- likely "
                                     "intentionally shared with a paired "
                                     "heating/cooling technology in this "
                                     "row to avoid double-counting; left "
                                     "unchanged, review manually",
                        })
                    else:
                        new_full_cost_cell = replace_cost_for_key(
                            cost_cell, tech, cost)
                        new_cost_repr = (
                            f"new: {cost['new']}; "
                            f"existing: {cost['existing']}")
                        same_values = cost_unkeyed and isinstance(
                            cost_cell, str) and [
                                float(v) for v in re.findall(
                                    r"-?\d+\.?\d*", cost_cell)] == [
                                float(cost["new"]), float(cost["existing"])]
                        if new_full_cost_cell != cost_cell and \
                                not same_values:
                            cell_state["Installed Cost"] = new_full_cost_cell
                            ws.cell(
                                row=excel_row,
                                column=col_index["Installed Cost"]).value = \
                                new_full_cost_cell
                            diff_rows.append({
                                "Name": row.get("Name"), "technology": tech,
                                "column": "Installed Cost",
                                "old_value": old_cost,
                                "new_value": new_cost_repr,
                                "btb_technology_id":
                                    entry["btb_technology_id"],
                                "btb_display_name":
                                    entry["btb_display_name"],
                                "projection_scenario":
                                    entry["projection_scenario"],
                                "projection_year": entry["projection_year"],
                                "notes": cost_note,
                            })
                            old_units = row.get("Cost Units")
                            if units_info and units_info[0] != 2023:
                                new_units = relabel_cost_units(old_units)
                                ws.cell(
                                    row=excel_row,
                                    column=col_index["Cost Units"]).value = \
                                    new_units
                                diff_rows.append({
                                    "Name": row.get("Name"),
                                    "technology": tech,
                                    "column": "Cost Units",
                                    "old_value": old_units,
                                    "new_value": new_units,
                                    "btb_technology_id":
                                        entry["btb_technology_id"],
                                    "btb_display_name":
                                        entry["btb_display_name"],
                                    "projection_scenario":
                                        entry["projection_scenario"],
                                    "projection_year":
                                        entry["projection_year"],
                                    "notes": "BTB costs are $2023",
                                })

            # -- Lifetime --
            lifetime = btb_row.get("Lifetime (Years)")
            if pd.notna(lifetime):
                lifetime_cell = cell_state["Lifetime"]
                life_unkeyed = is_unkeyed(lifetime_cell)
                old_lifetime = find_value_for_key(lifetime_cell, tech)
                new_lifetime_str = f"{float(lifetime):.3g}"
                if old_lifetime != new_lifetime_str and (
                        tech == owner if life_unkeyed
                        else re.search(re.escape(tech) + r"\s*:",
                                       lifetime_cell, re.IGNORECASE)):
                    cell_state["Lifetime"] = replace_value_for_key(
                        lifetime_cell, tech, new_lifetime_str)
                    ws.cell(row=excel_row,
                            column=col_index["Lifetime"]).value = \
                        cell_state["Lifetime"]
                    diff_rows.append({
                        "Name": row.get("Name"), "technology": tech,
                        "column": "Lifetime",
                        "old_value": old_lifetime,
                        "new_value": new_lifetime_str,
                        "btb_technology_id": entry["btb_technology_id"],
                        "btb_display_name": entry["btb_display_name"],
                        "projection_scenario": entry["projection_scenario"],
                        "projection_year": entry["projection_year"],
                    })

    if "BTB Diff" in wb.sheetnames:
        del wb["BTB Diff"]
    diff_ws = wb.create_sheet("BTB Diff")
    diff_columns = [
        "Name", "technology", "column", "old_value", "new_value",
        "btb_technology_id", "btb_display_name", "projection_scenario",
        "projection_year", "notes"]
    diff_df = pd.DataFrame(diff_rows, columns=diff_columns).fillna("")
    diff_ws.append(diff_columns)
    for _, diff_row in diff_df.iterrows():
        diff_ws.append(list(diff_row))

    wb.save(OUT_PATH)
    print(f"Proposed {len(diff_rows)} cell changes across "
          f"{diff_df['Name'].nunique() if len(diff_df) else 0} measures.")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
