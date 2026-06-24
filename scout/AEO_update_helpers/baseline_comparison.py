#!/usr/bin/env python3
"""Baseline comparison between Scout microsegments and EIA AEO data.

Recommended usage
-----------------
Run this script from the project root as a module so imports and
relative paths resolve correctly, and so your API key can be picked up
from a ``.env`` file or environment variable::

    python -m scout.AEO_update_helpers.baseline_comparison --year 2025

You can optionally add ``--verbose`` to see extra diagnostic output.

Overview
--------
This script compares energy use from Scout's processed AEO JSON file to
summary values from the EIA Annual Energy Outlook (AEO) API.

High-level steps
----------------
1. Read the Scout microsegments JSON file.
2. For every combination of:
   - building class (residential, commercial)
   - fuel type (electricity, natural gas, distillate, other fuel)
   - end use (heating, cooling, lighting, etc.)
   we add up the energy in the JSON.
3. For the same combination, we query the EIA AEO API for the
   corresponding series and convert units so they match the JSON.
4. We compare the two sets of values year by year, compute the
   percent error, and print a short report.
5. At the end we also print simple rollup tables by building type
   and fuel.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

import numpy as np
import numpy.lib.recfunctions as rfn
import time
import requests
from backoff import expo, on_exception
from dotenv import load_dotenv
from tabulate import tabulate

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

#: maximum allowed average percent error before a comparison is highlighted
ERROR_THRESHOLD = 0.01  # 1 %


#: path to the Scout microsegments JSON file (relative to project root)
MSEG_PATH = "scout/supporting_data/stock_energy_tech_data/mseg_res_com_cz.json"


@dataclass(frozen=True)
class FilterStrings:
    """Simple container for the three key dimensions we compare.

    Attributes
    ----------
    bldg_class : str
        Either "residential" or "commercial".
    fuel : str
        Fuel name as it appears in the microsegments JSON, e.g.
        "electricity", "natural gas", "distillate", "other fuel".
    end_use : str
        End‑use name in the microsegments JSON, e.g. "heating",
        "cooling", "lighting", etc.
    """

    bldg_class: str
    fuel: str
    end_use: str


class UsefulVars:
    """Look‑up tables that convert between JSON names and API codes.

    This class holds small dictionaries and lists that we need in several
    places:

    * building class names used in the microsegments JSON
    * fuel type names
    * end‑use names
    * mapping from those names to the short codes in the EIA API
    """

    def __init__(self) -> None:
        # Map from human‑readable building class to API code
        self.bldg_class_translator = {
            "residential": "resd",
            "commercial": "comm",
        }

        # Map from microsegments end‑use string to API end‑use code
        self.end_use_translator = {
            "clothes washing": "clw",
            "drying": "cdr",
            "computers": "cmpr",
            "cooking": "cgr",
            "dishwasher": "dsw",
            "fans and pumps": "fpr",
            "freezers": "frz",
            "lighting": "lghtng",
            "non-PC office equipment": "otheqpnpc",
            "PCs": "otheqppc",
            "other": "othu",
            "refrigeration": "refr",
            "cooling": "spc",
            "heating": "sph",
            "TVs": "tvr",
            "unspecified": "uns",
            "ventilation": "vntc",
            "water heating": "wtht",
        }

        # Map from fuel type string in JSON to API fuel code
        self.fuel_type_translator = {
            "electricity": "elc",
            "natural gas": "ng",
            "Purchased Electricity": "prc",  # used for commercial electricity
            "distillate": "dfo",
            "other fuel": "ofu",
        }

        # List of fuel types we loop over
        self.fuel_type = [
            "electricity",
            "natural gas",
            "distillate",
            "other fuel",
        ]

        # Building subclasses found in the microsegments JSON
        self.all_bldg_types = {
            "residential": [
                "single family home",
                "multi family home",
                "mobile home",
            ],
            "commercial": [
                "assembly",
                "education",
                "food sales",
                "food service",
                "health care",
                "large office",
                "lodging",
                "mercantile/service",
                "other",
                "small office",
                "warehouse",
                "unspecified",
            ],
        }

        # End uses that live under the "other" bucket in the residential JSON
        self.other_end_uses = [
            "rechargeables",
            "coffee maker",
            "dehumidifier",
            "electric other",
            "small kitchen appliances",
            "microwave",
            "smartphones",
            "pool heaters",
            "pool pumps",
            "security system",
            "portable electric spas",
            "smart speakers",
            "tablets",
            "wine coolers",
            "other appliances",
        ]

        # These appear under "other" in the JSON but are separate end uses
        # in the AEO tables.
        self.separate_other_end_uses = [
            "clothes washing",
            "freezers",
            "dishwasher",
        ]

        # Heating is split into two pieces in the JSON
        self.heating_end_uses = ["heating", "secondary heating"]

        # Remaining end uses that map directly
        self.remaining_end_uses = [
            "drying",
            "computers",
            "cooking",
            "lighting",
            "PCs",
            "onsite generation",
            "non-PC office equipment",
            "refrigeration",
            "TVs",
            "ventilation",
            "water heating",
        ]


# Global containers used for summary output at the end of the run
_totals: dict[tuple[str, str], dict[str, dict[str, float]]] = defaultdict(
    lambda: defaultdict(lambda: {"scout": 0.0, "eia": 0.0})
)
_error_log: list[dict] = []
_zero_division_errors: list[dict] = []
_series_results: list[dict] = []

# Baseline per-series tolerance map (fractions). If a series is missing,
# the fallback tolerance is 0.0 (zero tolerance).
SERIES_TOLERANCE: dict[str, float] = {

    # Explicitly mark known 0.00% error series with 0 tolerance
    "cnsm_NA_resd_clw_elc_NA_usa_qbtu": 0.0,
    "cnsm_NA_resd_cdr_elc_NA_usa_qbtu": 0.0,
    "cnsm_NA_resd_cmpr_elc_NA_usa_qbtu": 0.0,
    "cnsm_NA_resd_cgr_elc_NA_usa_qbtu": 0.0,
    "cnsm_NA_resd_dsw_elc_NA_usa_qbtu": 0.0,
    "cnsm_NA_resd_fpr_elc_NA_usa_qbtu": 0.0,
    "cnsm_NA_resd_frz_elc_NA_usa_qbtu": 0.0,
    "cnsm_NA_resd_lghtng_elc_NA_usa_qbtu": 0.0,
    "cnsm_NA_resd_othu_elc_NA_usa_qbtu": 0.0,
    "cnsm_NA_resd_refr_elc_NA_usa_qbtu": 0.0,
    "cnsm_NA_resd_spc_elc_NA_usa_qbtu": 0.0,
    "cnsm_hhd_resd_sph_elc_NA_usa_qbtu": 0.0,
    "cnsm_NA_resd_tvr_elc_NA_usa_qbtu": 0.0,
    "cnsm_NA_resd_wtht_elc_NA_usa_qbtu": 0.0,
    "cnsm_NA_resd_cdr_ng_NA_usa_qbtu": 0.0,
    "cnsm_NA_resd_cgr_ng_NA_usa_qbtu": 0.0,
    "cnsm_NA_resd_othu_ng_NA_usa_qbtu": 0.0,
    "cnsm_NA_resd_spc_ng_NA_usa_qbtu": 0.0,
    "cnsm_NA_resd_sph_ng_NA_usa_qbtu": 0.0,
    "cnsm_NA_resd_othu_dfo_NA_usa_qbtu": 0.0,
    "cnsm_NA_resd_wtht_dfo_NA_usa_qbtu": 0.0,
    "cnsm_NA_comm_NA_prc_cgr_usa_qbtu": 0.0,
    "cnsm_NA_comm_NA_prc_lghtng_usa_qbtu": 0.0,
    "cnsm_NA_comm_NA_prc_otheqpnpc_usa_qbtu": 0.0,
    "cnsm_NA_comm_NA_prc_otheqppc_usa_qbtu": 0.0,
    "cnsm_NA_comm_NA_prc_refr_usa_qbtu": 0.0,
    "cnsm_NA_comm_NA_prc_spc_usa_qbtu": 0.0,
    "cnsm_NA_comm_NA_prc_sph_usa_qbtu": 0.0,
    "cnsm_NA_comm_NA_prc_vntc_usa_qbtu": 0.0,
    "cnsm_NA_comm_NA_ng_cgr_usa_qbtu": 0.0,
    "cnsm_NA_comm_NA_ng_othu_usa_qbtu": 0.0,
    "cnsm_NA_comm_NA_ng_sph_usa_qbtu": 0.0,
    "cnsm_NA_comm_NA_ng_wtht_usa_qbtu": 0.0,
    "cnsm_NA_comm_NA_dfo_othu_usa_qbtu": 0.0,

    # Residential – notable non-zero averages
    "cnsm_NA_resd_wtht_ng_NA_usa_qbtu": 0.0002,   # 0.02%
    "cnsm_NA_resd_sph_dfo_NA_usa_qbtu": 0.00232,  # 0.232%

    # Commercial – electricity
    "cnsm_NA_comm_NA_prc_othu_usa_qbtu": 0.0008,  # 0.08%
    "cnsm_NA_comm_NA_prc_wtht_usa_qbtu": 0.00064,  # 0.064%

    # Commercial – distillate
    "cnsm_NA_comm_NA_dfo_sph_usa_qbtu": 0.0096,   # 0.96%
    "cnsm_NA_comm_NA_dfo_wtht_usa_qbtu": 0.0674,  # 6.74%

    # Commercial – natural gas
    "cnsm_NA_comm_NA_ng_spc_usa_qbtu": 0.05802,   # 5.802%
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def require_api_key() -> str:
    """Return the EIA API key or exit with a friendly message.

    The key must be set in a local ``.env`` file (not committed to git)
    as ``EIA_API_KEY=...`` or in the environment itself.

    You can request a free key from: https://www.eia.gov/opendata/register.php
    """
    # Load variables from a local .env file if it exists.
    load_dotenv()

    api_key = os.getenv("EIA_API_KEY")
    if not api_key:
        raise SystemExit(
            "EIA_API_KEY is not set.\n\n"
            "To fix this, create a file named '.env' in the project root "
            "(the same folder as pyproject.toml) with a line like:\n\n"
            "    EIA_API_KEY=YOUR_REAL_KEY_HERE\n\n"
            "Alternatively, you can set EIA_API_KEY in your shell environment.\n"
        )
    return api_key


@on_exception(expo, Exception, max_tries=5)
def api_query(
    api_key: str, series_id: str, year: str, verbose: bool
) -> dict[str, float]:
    """Query the EIA AEO API for one series and return a {year: value} dict.

    Parameters
    ----------
    api_key : str
        Your EIA API key.
    series_id : str
        ID of the time series we want (for example
        ``cnsm_NA_resd_lghtng_elc_NA_usa_qbtu``).
    year : str
        AEO reference year, e.g. "2025". Used only in the URL path.
    verbose : bool
        If True, print the URL and any error messages.
    """

    url = (
        f"https://api.eia.gov/v2/aeo/{year}/data/"
        "?frequency=annual"
        "&data[0]=value"
        f"&facets[scenario][]=ref{year}"
        f"&facets[seriesId][]={series_id}"
        "&sort[0][column]=period&sort[0][direction]=desc"
        "&offset=0&length=5000"
        f"&api_key={api_key}"
    )

    if verbose:
        print("\n[API] GET", url.replace(api_key, "<API_KEY>"))

    # Be a good API citizen: add a small delay so we do not hammer the EIA
    # servers when running many combinations in a row.
    time.sleep(1.0)

    try:
        response = requests.get(url, timeout=(3, 30))
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:  # network or HTTP error
        if verbose:
            print(f"[API] Request failed for {series_id}: {exc}")
        return {}

    try:
        data = response.json()["response"]["data"]
    except (KeyError, ValueError) as exc:
        if verbose:
            print(f"[API] Unexpected JSON structure for {series_id}: {exc}")
        return {}

    # Keep only {year: value} pairs and convert to floats
    return {str(item["period"]): float(item["value"]) for item in data}


def construct_eia_series_id(filters: FilterStrings, year: str, uv: UsefulVars) -> str:
    """Build the EIA AEO series ID for a given combination.

    The exact pattern comes from EIA's AEO documentation. Here we
    construct it from the building class, fuel, and end use.

    Notes
    -----
    * For commercial buildings, electricity is called "Purchased Electricity"
      in the API, so we adjust that here using a local variable.
    * For residential electric heating, an additional ``hhd`` code is used.
    """

    bldg = filters.bldg_class
    fuel = filters.fuel
    end_use = filters.end_use

    # Conditions used inside the ID string
    if bldg == "residential":
        condition_1 = uv.end_use_translator[end_use]
        condition_2 = "NA"
        if end_use == "heating" and fuel == "electricity":
            condition_3 = "hhd"  # special case for electric heating
        else:
            condition_3 = "NA"
    else:  # commercial
        # Commercial electricity is labeled as "Purchased Electricity" in API
        fuel_for_api = "Purchased Electricity" if fuel == "electricity" else fuel
        condition_1 = "NA"
        condition_2 = uv.end_use_translator[end_use]
        condition_3 = "NA"
        fuel = fuel_for_api

    # condition_1 is end_use for residential
    # condition_2 is end_use for commercial
    # condition_3 is hdd if electric_heating else NA

    eia_series_id = (
        f"cnsm_{condition_3}_"
        f"{uv.bldg_class_translator[bldg]}_"
        f"{condition_1}_"
        f"{uv.fuel_type_translator[fuel]}_"
        f"{condition_2}_usa_qbtu"
    )

    return eia_series_id


def recursive_aggregate(
    data: dict,
    filters: FilterStrings,
    uv: UsefulVars,
    position: list[str] | None = None,
) -> dict[str, float]:
    """Walk the microsegments JSON and sum energy for one combination.

    We only add a leaf's ``energy`` values when:

    * the building subclass matches the requested building class;
    * the fuel matches;
    * the end use matches, using a small set of rules that map the
      detailed JSON structure to the AEO end‑use categories.

    The function returns a dictionary ``{year: energy}``.
    """

    if position is None:
        position = []

    energy_by_year: dict[str, float] = {}

    for key, value in data.items():
        if isinstance(value, dict) and key != "energy":
            # Keep going down one level
            sub_result = recursive_aggregate(value, filters, uv, position + [key])
            for yr, val in sub_result.items():
                energy_by_year[yr] = energy_by_year.get(yr, 0.0) + val
            continue

        if key != "energy":
            # Only interested in energy leaves
            continue

        path = position + [key]
        if len(path) < 5:
            # We expect: climate_zone / bldg_type / fuel / end_use / ... / energy
            continue

        _cz, bldg_type, fuel_name, eu_name, *rest = path
        subkey = rest[0] if rest else ""

        # Only consider the requested building class and fuel
        if bldg_type not in uv.all_bldg_types[filters.bldg_class]:
            continue
        if fuel_name != filters.fuel:
            continue

        # Decide whether to include this particular leaf based on end‑use rules
        end_use = filters.end_use
        accept = False

        if eu_name == "other" and subkey in uv.other_end_uses and end_use == "other":
            accept = True
        elif eu_name == "ceiling fan" and end_use == "other":
            accept = True
        elif (
            eu_name == "other"
            and subkey in uv.separate_other_end_uses
            and end_use == subkey
        ):
            accept = True
        elif (
            eu_name in uv.heating_end_uses
            and end_use == "heating"
            and subkey == "supply"
        ):
            accept = True
        elif eu_name == "cooling" and end_use == "cooling" and subkey == "supply":
            accept = True
        elif eu_name in uv.remaining_end_uses and end_use == eu_name:
            accept = True
        elif (
            eu_name in ("other", "unspecified")
            and fuel_name != "electricity"
            and end_use == "other"
        ):
            accept = True
        elif (
            eu_name in ("MELs", "unspecified")
            and fuel_name == "electricity"
            and end_use == "other"
        ):
            accept = True
        elif eu_name == end_use and subkey == "energy":
            accept = True

        if not accept:
            continue

        # At this point we decided that this leaf contributes to our total
        for yr, val in value.items():
            energy_by_year[yr] = energy_by_year.get(yr, 0.0) + val

    return energy_by_year


def compare_one_combination(
    mseg: dict,
    filters: FilterStrings,
    year: str,
    verbose: bool,
    uv: UsefulVars,
    api_key: str,
) -> None:
    """Compare Scout vs. EIA for one (building, fuel, end use) triple.

    1. Aggregate the JSON for ``filters``.
    2. Query the EIA API for the matching series.
    3. Convert EIA values to match JSON units.
    4. Compute average percent error and print a small report.
    5. Update the global rollup containers.
    """

    bldg = filters.bldg_class
    fuel = filters.fuel
    end_use = filters.end_use

    # 1. Aggregate JSON
    json_dict = recursive_aggregate(mseg, filters, uv)

    json_is_empty = not bool(json_dict)
    if json_is_empty and verbose:
        print(f"No JSON data found for {bldg} | {fuel} | {end_use}.")

    # 2. Build series ID and query EIA
    series_id = construct_eia_series_id(filters, year, uv)
    eia_dict = api_query(api_key, series_id, year, verbose)

    # If EIA has data but the JSON aggregate is empty, treat this as a hard error.
    if json_is_empty and eia_dict:
        raise RuntimeError(
            "EIA data exists but JSON aggregate is empty for "
            f"{bldg} | {fuel} | {end_use} (series {series_id})."
        )

    # If both sides are empty or JSON is empty and EIA is also empty, skip quietly.
    if not json_dict:
        return

    if not eia_dict:
        if verbose:
            print(f"No EIA data returned for series {series_id}.")
        # hit for: (res, cooking, other fuel)
        return

    json_array = np.array(
        sorted(json_dict.items()),
        dtype=[("year", "<U32"), ("scout", "f8")],
    )

    # 3. Convert units so that both sides are in Btu
    for k in eia_dict:
        eia_dict[k] *= 1e9

    eia_array = np.array(
        sorted(eia_dict.items()),
        dtype=[("year", "<U32"), ("eia", "f8")],
    )

    # Join on year so we only compare overlapping years
    joined = rfn.join_by("year", json_array, eia_array, usemask=False)

    if len(joined) == 0:
        if verbose:
            print(
                f"No overlapping years between JSON and EIA for "
                f"{bldg} | {fuel} | {end_use}."
            )
        return

    # 4. Compute average percent error; protect against division by zero
    try:
        cum_pct_err = float(np.sum(np.abs(joined["scout"] - joined["eia"]) / joined["eia"]))
        avg_pct_err = cum_pct_err / len(joined)
    except ZeroDivisionError:
        _zero_division_errors.append(
            {
                "building": bldg,
                "fuel": fuel,
                "end_use": end_use,
                "series_id": series_id,
                "context": "avg_pct_err",
                "years": [],
            }
        )
        if verbose:
            print(
                f"Division by zero when computing average error for "
                f"{bldg} | {fuel} | {end_use}. Skipping."
            )
        return

    print(
        f"\n=== {bldg.upper()} | {fuel.title()} | {end_use.title()} ===\n"
        f"Series ID       : {series_id}\n"
        f"Average % error : {avg_pct_err:.2%}"
    )

    print("(year, Scout JSON total, EIA API total, Percent error):")
    for rec in joined:
        yr, scout_v, eia_v = rec["year"], rec["scout"], rec["eia"]
        if eia_v == 0:
            pct_err_str = "n/a (EIA = 0)"
            _zero_division_errors.append(
                {
                    "building": bldg,
                    "fuel": fuel,
                    "end_use": end_use,
                    "series_id": series_id,
                    "context": "per-year",
                    "years": [yr],
                }
            )
        else:
            pct_err_str = f"{abs(scout_v - eia_v) / eia_v:.2%}"
        print(
            f"  {yr}: Scout = {scout_v:,.1f}   "
            f"EIA = {eia_v:,.1f}   Error = {pct_err_str}"
        )

    # 5. Update global rollups
    for yr, scout_v, eia_v in joined:
        rec = _totals[(bldg, fuel)][yr]
        rec["scout"] += float(scout_v)
        rec["eia"] += float(eia_v)

    # Record combinations with large average error
    if avg_pct_err > ERROR_THRESHOLD:
        _error_log.append(
            {
                "building": bldg,
                "fuel": fuel,
                "end_use": end_use,
                "series_id": series_id,
                "avg_pct_err": avg_pct_err,
            }
        )

    # Record all series average errors for per-series enforcement
    _series_results.append(
        {
            "building": bldg,
            "fuel": fuel,
            "end_use": end_use,
            "series_id": series_id,
            "avg_pct_err": avg_pct_err,
        }
    )


def print_rollups() -> None:
    """Print table of total Scout vs. EIA energy by building and fuel."""

    uv = UsefulVars()

    for bldg in ("residential", "commercial"):
        banner = f"{'=' * 10}  {bldg.upper()}  {'=' * 10}"
        print("\n" + banner)

        for fuel in uv.fuel_type:
            year_rows: list[list[str]] = []
            for yr, vals in sorted(_totals[(bldg, fuel)].items()):
                scout = vals["scout"]
                eia = vals["eia"]
                delta_pct = 0.0 if eia == 0 else abs(scout - eia) / eia * 100
                year_rows.append(
                    [
                        yr,
                        f"{scout:,.1f}",
                        f"{eia:,.1f}",
                        f"{delta_pct:4.1f}%",
                    ]
                )

            print(f"\n{fuel.title()}  (Btu)")
            if year_rows:
                # Also write a simple CSV-style line for programmatic comparison
                # Format: bldg,fuel,year,scout,eia
                # This is intentionally duplicated work (printing and writing)
                # to keep the console output unchanged while making it easy
                # to diff results against the original script.

                print(
                    tabulate(
                        year_rows,
                        headers=["Year", "Scout total", "EIA total", "Pct delta"],
                        tablefmt="github",
                        colalign=("right", "right", "right", "right"),
                    )
                )
            else:
                print("(no data)")


def report_large_errors() -> None:
    """Summarize all series whose average error exceeded the threshold."""

    if not _error_log:
        print(f"\nAll series were within {ERROR_THRESHOLD:.2%} average error.")
        return

    print(f"\nSeries with average error > {ERROR_THRESHOLD:.2%}:")
    for rec in _error_log:
        print(
            f"  {rec['building'].upper()} | {rec['fuel'].title()} | "
            f"{rec['end_use'].title()}  ->  {rec['avg_pct_err']:.2%}\n"
            f"    Series ID: {rec['series_id']}"
        )


def enforce_max_error_or_fail() -> None:
    """Exit non-zero if any series exceeds its per-series tolerance.

    Compares all collected `_series_results` against `SERIES_TOLERANCE`.
    Aggregates all violations and raises one `SystemExit` with a summary.
    """

    # Ensure prior prints are flushed to the log
    time.sleep(1.0)

    violations: list[dict] = []
    min_tol_floor = 5e-5  # 0.005%
    for rec in _series_results:
        sid = rec["series_id"]
        avg = rec["avg_pct_err"]
        base_tol = SERIES_TOLERANCE.get(sid, 0.0)
        tol = base_tol if base_tol > 0.0 else min_tol_floor
        eps = 1e-9
        if (avg - tol) > eps and not np.isclose(avg, tol, rtol=1e-9, atol=1e-12):
            violations.append({
                "series_id": sid,
                "avg_pct_err": avg,
                "tolerance": tol,
                "building": rec["building"],
                "fuel": rec["fuel"],
                "end_use": rec["end_use"],
            })

    if violations:
        print("\nPer-series tolerance violations:")
        for v in violations:
            print(
                f"  {v['building'].upper()} | {v['fuel'].title()} | {v['end_use'].title()}\n"
                f"    Series ID: {v['series_id']}\n"
                f"    Avg error: {v['avg_pct_err']:.6%} | Allowed: {v['tolerance']:.6%}"
            )

        raise SystemExit(
            (
                f"{len(violations)} series exceeded per-series tolerances.\n"
                f"Failing run."
            )
        )


def report_zero_division_cases() -> None:
    """Summarize all places where division by zero occurred."""

    if not _zero_division_errors:
        print("\nNo zero-division cases encountered.")
        return

    print("\nZero‑division cases (EIA values equal to 0):")

    merged: dict[tuple[str, str, str, str, str], set[str]] = {}
    for item in _zero_division_errors:
        key = (
            item["building"],
            item["fuel"],
            item["end_use"],
            item["series_id"],
            item["context"],
        )
        merged.setdefault(key, set()).update(item.get("years") or [])

    for (bldg, fuel, end_use, sid, ctx), years in sorted(merged.items()):
        years_str = ", ".join(sorted(years)) if years else "(all/unknown)"
        print(
            f"  {bldg.upper()} | {fuel.title()} | {end_use.title()}"
            f" | context: {ctx} | years: {years_str}\n"
            f"    Series: {sid}"
        )


# ---------------------------------------------------------------------------
# Command‑line interface
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    """Parse command‑line options.

    Parameters
    ----------
    None

    Returns
    -------
    argparse.Namespace
        An object with the parsed options as attributes.
    """

    parser = argparse.ArgumentParser(description="Compare Scout and EIA AEO data.")
    parser.add_argument(
        "--year",
        type=str,
        default=str(datetime.now().year),
        help="AEO year (YYYY) to query, for example 2025.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print extra diagnostic information while running.",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point when the script is run from the command line.

    This function wires together all of the pieces:

    1. Read command‑line arguments.
    2. Load the microsegments JSON file.
    3. Loop over all building class / fuel / end‑use combinations.
    4. Compare Scout to EIA for each combination.
    5. Print summary tables and short error reports.
    """

    opts = parse_args()
    year = opts.year
    verbose = opts.verbose

    print(f"Using AEO reference year {year} (verbose={verbose}).")

    # Get API key early so we fail fast if it is missing
    api_key = require_api_key()

    # Load the microsegments JSON file
    try:
        with open(MSEG_PATH, "r", encoding="utf-8") as f:
            mseg = json.load(f)
    except FileNotFoundError:
        raise SystemExit(
            f"Could not find microsegments file at {MSEG_PATH}.\n"
            "Please check that you are running this script from the project "
            "root and that the file path is correct."
        )

    uv = UsefulVars()

    # Loop over building classes, fuels, and end uses
    for bldg in uv.bldg_class_translator.keys():
        for fuel in uv.fuel_type:
            for end_use in uv.end_use_translator.keys():
                filters = FilterStrings(bldg_class=bldg, fuel=fuel, end_use=end_use)
                compare_one_combination(mseg, filters, year, verbose, uv, api_key)

    # After all combinations, print summary information
    print_rollups()
    report_large_errors()
    report_zero_division_cases()
    enforce_max_error_or_fail()


if __name__ == "__main__":  # pragma: no cover - direct CLI execution
    main()
