"""Module for flagging DSIRE program updates relevant to sub_fed/incentives.csv.

This module does NOT rewrite incentives.csv automatically. Translating a DSIRE
program record into a row of that file requires judgment calls that the DSIRE
API cannot make on its own -- e.g. mapping DSIRE's technology categories onto
Scout's own end use/tech/building type taxonomy, reading eligibility text to
back out a "performance level" and "performance units" (COP, UEF, R-value,
...), deciding "modification"/"scope"/"ira", and setting "applicable fraction"
with a justifying note. Those columns stay a manual, analyst-driven edit.

What this module automates instead: querying the DSIRE Programs API
(https://docs.dsireusa.org/) for financial incentive programs that were
created, updated, or newly expired since the last time incentives.csv was
touched -- nationwide by default, including DC, DSIRE's federal-only "US"
pseudo-state, and US territories (whether those belong in incentives.csv
is an open question this script deliberately doesn't pre-filter out; pass
--states FIFTY for just the 50 US states, via DSIRE's own /states data,
once that's settled) -- and writing the results to a staging CSV in this
same directory (sub_fed/dsire/) for manual review. Treat that staging file
as a worklist, not a replacement for incentives.csv. Pass --states TRACKED
to restrict further, to only the states already present in incentives.csv,
if you specifically want a delta against existing coverage rather than a
full sweep (the default also surfaces states incentives.csv has zero rows
for at all, which a tracked-states-only scope would hide by construction).

This script is not part of the installed scout package -- it lives under
supporting_data alongside its own output, the same way sub_fed's other
by-hand-maintained files do, and is run directly by path rather than as a
`python -m scout...` module.

Requires a DSIRE API key (obtained from https://dsireusa.org/dsire-api/, one
key per subscriber, contact dsire-admin@ncsu.edu to request one). Set it as
DSIRE_API_KEY, either in a .env file at the project root (gitignored -- see
.gitignore) or as a shell environment variable:

    $ echo 'DSIRE_API_KEY=your api key' >> .env

Usage (from the project root):

    $ python scout/supporting_data/sub_fed/dsire/dsire_incentive_checker.py
    $ python scout/supporting_data/sub_fed/dsire/dsire_incentive_checker.py \
        --since 2025-01-01 --states CA NY
    $ python scout/supporting_data/sub_fed/dsire/dsire_incentive_checker.py \
        --states TRACKED --category ALL

"""

import os
import sys
import csv
import argparse
import subprocess
from datetime import date
from pathlib import Path
import requests
import pandas as pd
from backoff import on_exception, expo
from dotenv import load_dotenv
from scout.config import FilePaths as fp

load_dotenv()

BASE_URL = "https://api.dsireusa.org/v1"
PAGE_LIMIT = 100
# The DSIRE program category that maps to incentives.csv; other categories
# (e.g. regulatory policy) are out of scope for this file.
DEFAULT_CATEGORY_NAME = "Financial Incentive"
INCENTIVES_CSV = fp.SUB_FED / "incentives.csv"
DSIRE_DIR = Path(__file__).resolve().parent

# Keyword substrings (matched case-insensitively against DSIRE's free-text
# "technologies" field) covering the equipment/envelope categories actually
# present in incentives.csv's tech(s)/end use(s) columns (ASHP, GSHP,
# central AC, electric WH, furnace, roof/wall/windows conduction, drying,
# cooking) plus DSIRE's own naming variants for the same equipment (e.g.
# "Heat Pump Water Heater", "Ductless Mini-Split Heat Pump"). DSIRE's
# Financial Incentive programs skew heavily toward renewable generation
# (solar PV, wind, biomass) and EVs, which incentives.csv does not track --
# this list exists to filter that majority out rather than to be
# exhaustive, so a false positive (kept but irrelevant) is preferable to a
# false negative (silently dropped).
SCOUT_TECH_KEYWORDS = [
    "heat pump", "ashp", "gshp", "mini-split", "mini split",
    "air-source heat pump", "air source heat pump", "air condition",
    "central ac", "furnace", "boiler", "water heater", "insulation",
    "window", "duct", "air sealing", "weatheriz", "clothes dryer",
    "hvac", "comprehensive measures", "whole building", "envelope",
    "cooking", "stove", "range",
]


def is_scout_relevant(technologies):
    """Flag whether a DSIRE program's technologies overlap Scout's scope.

    Returns True when the technologies field is blank (DSIRE didn't tag it,
    so it can't be safely ruled out) or when any listed technology matches
    SCOUT_TECH_KEYWORDS; False only when technologies were listed and none
    of them matched -- i.e. positive evidence the program is out of scope
    (solar PV, wind, EVs, appliances, etc.).
    """
    if not technologies or not technologies.strip():
        return True
    lowered = technologies.lower()
    return any(keyword in lowered for keyword in SCOUT_TECH_KEYWORDS)


def get_api_key():
    """Get the DSIRE API key from environment variables."""
    api_key = os.environ.get("DSIRE_API_KEY")
    if not api_key:
        print(
            "\nExpected environment variable DSIRE_API_KEY not set.\n"
            "Request an API key from DSIRE at https://dsireusa.org/dsire-api/ "
            "(contact dsire-admin@ncsu.edu).\n"
            "Add it to a .env file at the project root (already gitignored):\n"
            "$ echo 'DSIRE_API_KEY=your api key' >> .env\n"
        )
        sys.exit(1)
    return api_key


@on_exception(
    expo, requests.exceptions.HTTPError, max_tries=5,
    giveup=lambda e: (
        e.response is None
        or e.response.status_code not in (429, 500, 502, 503, 504)
    )
)
def api_get(session, path, params=None):
    """Execute a single DSIRE API GET request and return the parsed JSON body."""
    response = session.get(f"{BASE_URL}{path}", params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def paginate(session, path, params=None):
    """Yield every record from a paginated DSIRE API endpoint."""
    params = dict(params or {})
    offset = 0
    while True:
        params["limit"] = PAGE_LIMIT
        params["offset"] = offset
        body = api_get(session, path, params=params)
        records = body.get("data", [])
        for record in records:
            yield record
        total = body.get("meta", {}).get("total", len(records))
        offset += len(records)
        if not records or offset >= total:
            break


def resolve_category_id(session, name):
    """Look up the numeric id for a DSIRE program category by name.

    Returns None if no match is found, in which case the caller should
    proceed without a category filter rather than fail outright.
    """
    for category in paginate(session, "/categories"):
        if category.get("name", "").strip().lower() == name.strip().lower():
            return category["id"]
    print(f"Warning: could not find a DSIRE category named '{name}'; "
          "proceeding without a category filter.")
    return None


def get_tracked_states(incentives_path):
    """Extract the set of state abbreviations already present in incentives.csv.

    Cells may hold "all", a single state, or a comma/newline-separated list.
    """
    states = set()
    with open(incentives_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for cell in row.get("state(s)", "").split(","):
                code = cell.strip()
                if code and code.lower() != "all":
                    states.add(code)
    return sorted(states)


def get_fifty_states(session):
    """Return the 50 US state abbreviations, per DSIRE's own /states data.

    DSIRE's reference data flags DC, the federal "US" pseudo-state, and
    every actual territory (PR, GU, VI, AS, MP, PW, MH, FM) as
    is_territory=True alongside the 50 states -- filtering on that flag
    gives exactly the 50-states set without hardcoding a list here.
    """
    return sorted(
        s["abbreviation"] for s in paginate(session, "/states")
        if not s.get("is_territory", False)
    )


def get_last_update_date(path):
    """Return the date incentives.csv was last modified in git, as YYYY-MM-DD.

    Falls back to the file's mtime if the file has no git history (e.g. in a
    shallow clone or outside a git repo).
    """
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ad", "--date=short", "--", str(path)],
            capture_output=True, text=True, check=True,
        )
        last_date = result.stdout.strip()
        if last_date:
            return last_date
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return date.fromtimestamp(path.stat().st_mtime).isoformat()


def flatten_program(program, match_reason):
    """Flatten one DSIRE program record into a flat dict for CSV output."""
    param_sets = program.get("parameterSets") or []
    technologies = sorted({
        tech.get("name", "")
        for ps in param_sets for tech in (ps.get("technologies") or [])
        if tech.get("name")
    })
    amounts = [
        f"{p.get('source', '')} {p.get('qualifier', '')}: "
        f"{p.get('amount', '')} {p.get('units', '')}".strip()
        for ps in param_sets for p in (ps.get("parameters") or [])
    ]
    details = [
        f"{d.get('label', '')}: {d.get('value', '')}"
        for d in (program.get("details") or [])
    ]
    technologies_str = "; ".join(technologies)
    return {
        "dsire_id": program.get("id"),
        "match_reason": match_reason,
        "scout_relevant": is_scout_relevant(technologies_str),
        "state": (program.get("stateObj") or {}).get("abbreviation", ""),
        "category": (program.get("categoryObj") or {}).get("name", ""),
        "program_type": (program.get("typeObj") or {}).get("name", ""),
        "implementing_sector": (program.get("sectorObj") or {}).get("name", ""),
        "name": program.get("name", ""),
        "administrator": program.get("administrator", ""),
        "technologies": technologies_str,
        "incentive_amounts": "; ".join(amounts),
        "summary": program.get("summary", ""),
        "details": "; ".join(details),
        "website_url": program.get("websiteUrl", ""),
        "last_updated": program.get("lastUpdated", ""),
        "created_ts": program.get("createdTs", ""),
    }


def fetch_updates(session, since, states, category_id):
    """Query DSIRE for programs updated or newly expired since `since`.

    Returns a de-duplicated list of flattened program rows, tagged with why
    each one matched (updated, expired, or both).
    """
    base_params = {}
    if states:
        base_params["state[]"] = states
    if category_id is not None:
        base_params["category[]"] = category_id

    matches = {}  # dsire_id -> (program, set of reasons)

    updated_params = dict(base_params, **{"updatedfrom[]": since})
    for program in paginate(session, "/programs", params=updated_params):
        matches.setdefault(program["id"], (program, set()))[1].add("updated")

    expired_params = dict(base_params, **{"expiredfrom[]": since})
    for program in paginate(session, "/programs", params=expired_params):
        matches.setdefault(program["id"], (program, set()))[1].add("expired")

    rows = []
    for program, reasons in matches.values():
        rows.append(flatten_program(program, "+".join(sorted(reasons))))
    return rows


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Check DSIRE for financial incentive programs that changed "
            "since incentives.csv was last updated, and write candidates "
            "to a staging CSV for manual review."
        )
    )
    parser.add_argument(
        "--since", metavar="YYYY-MM-DD",
        help="Only include programs updated or expired on/after this date. "
             "Defaults to the date incentives.csv was last modified in git."
    )
    parser.add_argument(
        "--states", nargs="+", metavar="STATE",
        help="State abbreviations to filter on (e.g. CA NY). Defaults to "
             "nationwide (no filter), including DC, federal-only programs, "
             "and US territories -- whether those belong in incentives.csv "
             "is an open question, deliberately not pre-filtered out here. "
             "Pass TRACKED to restrict to only the states already present "
             "in incentives.csv, or FIFTY for just the 50 US states (via "
             "DSIRE's own /states data) once that question is settled."
    )
    parser.add_argument(
        "--category", default=DEFAULT_CATEGORY_NAME,
        help=f"DSIRE program category to filter on (default: "
             f"'{DEFAULT_CATEGORY_NAME}'). Pass ALL to skip category "
             f"filtering."
    )
    parser.add_argument(
        "--output", type=str,
        help="Path to write the staging CSV to. Defaults to "
             "sub_fed/dsire/dsire_incentive_updates_<today>.csv"
    )
    parser.add_argument(
        "--include-unrelated-tech", action="store_true",
        help="Also include programs whose DSIRE technologies don't overlap "
             "Scout's tracked equipment/envelope categories (e.g. solar PV, "
             "wind, EVs, appliances). Excluded by default since the large "
             "majority of DSIRE's Financial Incentive programs are for "
             "renewable generation, not the equipment incentives.csv tracks."
    )
    args = parser.parse_args()

    api_key = get_api_key()
    session = requests.Session()
    session.headers.update({"x-api-key": api_key})

    since = args.since or get_last_update_date(INCENTIVES_CSV)
    print(f"Checking DSIRE for programs updated or expired since {since}...")

    states_arg = [s.upper() for s in args.states] if args.states else []
    if states_arg == ["TRACKED"]:
        states = get_tracked_states(INCENTIVES_CSV)
        print(f"Restricting to {len(states)} state(s) already tracked in "
              f"incentives.csv: {', '.join(states)}")
    elif states_arg == ["FIFTY"]:
        states = get_fifty_states(session)
        print(f"Restricting to the {len(states)} US states (DC/territories/"
              f"federal-only programs excluded).")
    elif states_arg == ["ALL"] or not states_arg:
        states = []
        print("Searching nationwide (no state filter, including DC/"
              "territories/federal-only programs).")
    else:
        states = args.states
        print(f"Restricting to {len(states)} state(s): {', '.join(states)}")

    if args.category.strip().upper() == "ALL":
        category_id = None
    else:
        category_id = resolve_category_id(session, args.category)

    rows = fetch_updates(session, since, states, category_id)

    if not rows:
        print("No matching DSIRE program changes found.")
        return

    total_ct = len(rows)
    if not args.include_unrelated_tech:
        rows = [r for r in rows if r["scout_relevant"]]
    unrelated_ct = total_ct - len(rows)

    if not rows:
        print(f"No matching programs after filtering out {unrelated_ct} "
              "program(s) with no overlap with Scout's tracked technologies. "
              "Re-run with --include-unrelated-tech to see them.")
        return

    # Surface likely-actionable rows first: in-scope tech, then updated vs.
    # merely expired, then alphabetically by state/name.
    rows.sort(key=lambda r: (
        not r["scout_relevant"], "expired" in r["match_reason"] and
        "updated" not in r["match_reason"], r["state"], r["name"],
    ))

    output_path = (
        Path(args.output) if args.output
        else DSIRE_DIR / f"dsire_incentive_updates_{date.today().isoformat()}.csv"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)

    updated_ct = sum(1 for r in rows if "updated" in r["match_reason"])
    expired_ct = sum(1 for r in rows if "expired" in r["match_reason"])
    print(f"\nFound {total_ct} program(s) changed since {since}.")
    if unrelated_ct:
        print(f"Filtered out {unrelated_ct} program(s) with no overlap with "
              f"Scout's tracked technologies (solar/wind/EVs/appliances, "
              f"etc.). Re-run with --include-unrelated-tech to see them.")
    print(f"{len(rows)} program(s) remain: {updated_ct} updated, "
          f"{expired_ct} newly expired.")
    print(f"Wrote staging file to {output_path}")
    print("Review each row and hand-translate the relevant ones into "
          "sub_fed/incentives.csv -- this file does not get written to "
          "automatically.")


if __name__ == "__main__":
    main()
