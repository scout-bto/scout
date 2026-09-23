"""Diagnostic tool: reproduce a dsire_incentive_updates_*.csv-shaped staging
file, but scoped to the DSIRE programs behind incentives.csv's EXISTING
"reference" scenario rows, instead of "whatever changed recently" (that's
dsire_incentive_checker.py's job -- see its docstring).

This exists to answer a different question than the normal workflow: "if I
ran the DSIRE pipeline today, in place of whoever originally researched each
row already in incentives.csv, how close would the automated output land to
what's already there?" It is a backtest/comparison tool, not something to
run as part of normal upkeep.

Method: for each distinct "reference"-scenario description in incentives.csv
that cites a source URL, extract that URL's registrable domain (e.g.
"efficiencymaine.com") and the row's state(s), then query DSIRE for
Financial Incentive programs in that state whose own websiteUrl contains the
same domain. Writes matches in the exact column shape
dsire_incentive_checker.py produces, plus one extra "incentives_csv_match"
column (which existing description(s) triggered the match) -- so
dsire_incentive_drafter.py can be pointed at the output unmodified as step 2,
and so you can eyeball which existing row a given DSIRE record is meant to
stand in for.

Match quality is coarse (domain + state), NOT a citation-level pointer. A
state or utility often runs several distinct DSIRE-tracked programs
(residential vs. commercial vs. new construction vs. weatherization, ...),
and this script cannot tell which of several domain-matched hits is the
*right* one for a given incentives.csv row -- it keeps all of them, tagged,
rather than silently picking one. Rows in incentives.csv with no URL in
their description (e.g. "Duke Energy KY from CEE spreadsheet") can't be
matched this way at all and are skipped, printed at the end for visibility.

"all" in incentives.csv's state(s) column is treated as DSIRE's federal-only
"US" pseudo-state (that's how DSIRE tags the IRS 25C-style programs actually
cited by those rows), not a nationwide, unfiltered pull.

Usage (from the project root):

    $ python scout/supporting_data/sub_fed/dsire/dsire_incentive_backfill.py

    # Then run the normal drafter against the result, same as any other
    # staging file:
    $ python scout/supporting_data/sub_fed/dsire/dsire_incentive_drafter.py \\
        --input scout/supporting_data/sub_fed/dsire/dsire_incentive_backfill_<date>.csv \\
        --output scout/supporting_data/sub_fed/dsire/dsire_incentive_backfill_drafts_<date>.csv

Requires DSIRE_API_KEY (see dsire_incentive_checker.py's docstring for how
to get one and where to put it). DSIRE queries aren't billed, so there's no
cost concern running this -- it just makes one API call per distinct
domain/state combination found in incentives.csv.
"""

import csv
import re
import argparse
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
from collections import defaultdict

import requests
from dotenv import load_dotenv
from scout.config import FilePaths as fp

# Reuse the checker's own helpers rather than reimplementing DSIRE API
# plumbing -- this script's directory is on sys.path automatically since
# it's run directly by path (see this module's own docstring for why).
from dsire_incentive_checker import (
    get_api_key, paginate, resolve_category_id, flatten_program,
    DEFAULT_CATEGORY_NAME,
)

load_dotenv()

INCENTIVES_CSV = fp.SUB_FED / "incentives.csv"
DSIRE_DIR = Path(__file__).resolve().parent
URL_PATTERN = re.compile(r'https?://[^\s<>"\')\];]+')


def registrable_domain(url):
    """Best-effort registrable domain (e.g. "efficiencymaine.com") from a URL."""
    parts = urlparse(url).netloc.split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else parts[0]


def load_reference_rows(incentives_path):
    """Dedupe incentives.csv to one row per distinct "reference"-scenario
    description, and split each into (domain, states, description)."""
    with open(incentives_path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    seen = {}
    for row in rows:
        if row["scenario"] != "reference":
            continue
        seen.setdefault(row["description"], row)

    matchable, unmatchable = [], []
    for description, row in seen.items():
        urls = URL_PATTERN.findall(description)
        if not urls:
            unmatchable.append(description)
            continue
        domain = registrable_domain(urls[0])
        states = [s.strip() for s in row["state(s)"].split(",") if s.strip()]
        # "all" in incentives.csv means DSIRE's federal-only "US" pseudo-state
        # for these rows (they're all citing IRS/energy.gov federal programs)
        states = ["US"] if states == ["all"] else states
        matchable.append((domain, tuple(sorted(states)), description))
    return matchable, unmatchable


def find_matches(session, category_id, matchable):
    """Query DSIRE once per distinct (domain, states) pair, returning
    dsire_id -> (flattened program dict, set of matched incentives.csv
    descriptions)."""
    by_domain_states = defaultdict(list)
    for domain, states, description in matchable:
        by_domain_states[(domain, states)].append(description)

    matches = {}  # dsire_id -> (flattened dict, set of descriptions)
    for i, ((domain, states), descriptions) in enumerate(by_domain_states.items(), 1):
        print(f"[{i}/{len(by_domain_states)}] querying DSIRE for domain="
              f"'{domain}' state(s)={states or 'nationwide'}...")
        params = {"category[]": category_id}
        if states:
            params["state[]"] = list(states)
        for program in paginate(session, "/programs", params=params):
            website = program.get("websiteUrl", "") or ""
            if domain not in website:
                continue
            dsire_id = program["id"]
            if dsire_id not in matches:
                matches[dsire_id] = (
                    flatten_program(program, "existing_incentives_match"),
                    set(),
                )
            matches[dsire_id][1].update(descriptions)
    return matches


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Diagnostic: rebuild a dsire_incentive_updates_*.csv-shaped "
            "file scoped to the DSIRE programs behind incentives.csv's "
            "existing 'reference' rows, to compare against what's already "
            "there. Not part of the normal DSIRE workflow."
        )
    )
    parser.add_argument(
        "--output", type=str,
        help="Path to write the staging CSV to. Defaults to "
             "sub_fed/dsire/dsire_incentive_backfill_<today>.csv"
    )
    args = parser.parse_args()

    matchable, unmatchable = load_reference_rows(INCENTIVES_CSV)
    print(f"{len(matchable)} distinct 'reference' description(s) with a "
          f"source URL to match; {len(unmatchable)} without one (skipped).")

    api_key = get_api_key()
    session = requests.Session()
    session.headers.update({"x-api-key": api_key})
    category_id = resolve_category_id(session, DEFAULT_CATEGORY_NAME)

    matches = find_matches(session, category_id, matchable)

    output_path = (
        Path(args.output) if args.output
        else DSIRE_DIR / f"dsire_incentive_backfill_{date.today().isoformat()}.csv"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "dsire_id", "match_reason", "scout_relevant", "state", "category",
        "program_type", "implementing_sector", "name", "administrator",
        "technologies", "incentive_amounts", "summary", "details",
        "website_url", "last_updated", "created_ts", "incentives_csv_match",
    ]
    rows_out = []
    for flat, descriptions in matches.values():
        flat["incentives_csv_match"] = "; ".join(sorted(descriptions))[:500]
        rows_out.append(flat)
    rows_out.sort(key=lambda r: (r["state"], r["name"]))

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)

    matched_descriptions = {d for _, descs in matches.values() for d in descs}
    print(f"\n{len(matches)} DSIRE program(s) matched, covering "
          f"{len(matched_descriptions)}/{len(matchable)} of the matchable "
          "incentives.csv description(s).")
    if unmatchable:
        print(f"\n{len(unmatchable)} 'reference' description(s) had no URL "
              "to match against and were skipped entirely:")
        for d in unmatchable:
            print(f"  - {d[:100]}")
    print(f"\nWrote {output_path}")
    print(
        "Run dsire_incentive_drafter.py with --input pointed at this file "
        "to produce comparable draft rows for step 2."
    )


if __name__ == "__main__":
    main()
