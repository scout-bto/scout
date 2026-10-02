"""Module for drafting candidate incentives.csv rows from DSIRE program data.

This is the second half of the DSIRE workflow, after
dsire_incentive_checker.py has produced a dsire_incentive_updates_*.csv
staging file. This script sends each candidate DSIRE program in that file
to Claude and asks it to draft one incentives.csv-shaped row, using a
sample of the real, existing incentives.csv rows as few-shot examples of
the file's conventions.

This is a DRAFTING aid, not an auto-writer. It does NOT touch
incentives.csv. It writes a separate review CSV (columns matching
incentives.csv's exact headers, plus dsire_id/source_url/confidence/
open_questions for triage) that a human analyst reviews, corrects, and
hand-copies the accepted rows from into incentives.csv. Every drafted row
carries a confidence level and an open_questions field -- read those before
trusting any drafted value, especially performance_level, rebate_amount,
and applicable_fraction, which usually require judgment the source text
doesn't fully spell out. The model is instructed never to invent a number
that isn't stated in the input, but it can still misread ambiguous text,
so treat "high confidence" as "worth a quick read," not "safe to paste
unchecked."

Supports three providers -- pick with --provider:

- anthropic (default): Claude, via ANTHROPIC_API_KEY
  (https://console.anthropic.com/settings/keys)
- gemini: Gemini, via GOOGLE_API_KEY or GEMINI_API_KEY
  (https://aistudio.google.com/apikey)
- cborg: LBL's internal CBORG proxy (https://cborg.lbl.gov/api_faq/), via
  CBORG_API_KEY. Defaults to lbl/cborg-deepthought, one of CBORG's
  on-prem models -- those are free (no per-token cost, hence no PRICING
  entry needed) but require LBLnet/VPN access and are lower-quality than
  Claude/Gemini, so treat drafts from this provider with extra scrutiny.
  CBORG also proxies many paid third-party models (GPT, Claude, Gemini,
  ...) under other model ids -- those aren't free and aren't covered by
  this script's zero-cost assumption; pass one via --model at your own
  risk and verify its pricing on CBORG's own dashboard first.

Either way, put the key in .env at the project root (already gitignored)
and install the optional "llm" dependency group:

    $ echo 'ANTHROPIC_API_KEY=your api key' >> .env
    $ echo 'GOOGLE_API_KEY=your api key' >> .env
    $ echo 'CBORG_API_KEY=your api key' >> .env
    $ pip install ".[llm]"

Gemini's model lineup and pricing move faster than Claude's and aren't
pinned by a versioned skill the way the Claude defaults are here -- if
the default --model 404s, pass a current model id explicitly (see
https://ai.google.dev/gemini-api/docs/models), and sanity check the
printed cost estimate against https://ai.google.dev/gemini-api/docs/pricing.

Usage (from the project root):

    # Preview the prompt for the first row without spending anything
    $ python scout/supporting_data/sub_fed/dsire/dsire_incentive_drafter.py --dry-run

    # Draft against the most recent dsire_incentive_updates_*.csv (Claude)
    $ python scout/supporting_data/sub_fed/dsire/dsire_incentive_drafter.py

    # Same, but with Gemini or LBL's free CBORG on-prem models instead
    $ python scout/supporting_data/sub_fed/dsire/dsire_incentive_drafter.py \
        --provider gemini
    $ python scout/supporting_data/sub_fed/dsire/dsire_incentive_drafter.py \
        --provider cborg

    # Cap spend while testing
    $ python scout/supporting_data/sub_fed/dsire/dsire_incentive_drafter.py --limit 10

    # Resume an interrupted run without re-drafting or re-paying for rows
    # already in the output file
    $ python scout/supporting_data/sub_fed/dsire/dsire_incentive_drafter.py \
        --output sub_fed/dsire/dsire_incentive_drafts_2026-09-09.csv --resume

"""

import os
import sys
import csv
import json
import argparse
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from dotenv import load_dotenv
from scout.config import FilePaths as fp

load_dotenv()

DEFAULT_MODELS = {
    "anthropic": "claude-opus-5",
    "gemini": "gemini-3.6-flash",
    "cborg": "lbl/cborg-deepthought",
}
CBORG_BASE_URL = "https://api.cborg.lbl.gov"
# $ per token. Anthropic: docs.anthropic.com/en/docs/about-claude/pricing
# (see the claude-api skill for the current authoritative table). Gemini:
# ai.google.dev/gemini-api/docs/pricing -- verify if using a non-default
# --model, since Google's lineup/pricing changes faster than this table
# (gemini-2.5-flash, this script's previous default, was retired for new
# users within months of being set as the default here -- if --model
# 404s with a message naming its replacement, that message is more
# current than this table; update DEFAULT_MODELS and this entry to match
# it). gemini-3.6-flash pricing below is the introductory rate through
# 2026-12-31; it rises to $1.50/$7.50 per 1M on 2027-01-01. CBORG's
# lbl/* on-prem models are free (confirmed $0.0/$0.0 input/output via its
# /model/info endpoint) -- only add a PRICING entry for a non-"lbl/"
# --model on CBORG, which proxies paid third-party models at their own
# rates, not $0.
PRICING = {
    ("anthropic", "claude-opus-5"): (5.00 / 1_000_000, 25.00 / 1_000_000),
    ("gemini", "gemini-3.6-flash"): (0.75 / 1_000_000, 3.75 / 1_000_000),
    ("cborg", "lbl/cborg-deepthought"): (0.0, 0.0),
}

DSIRE_DIR = Path(__file__).resolve().parent
INCENTIVES_CSV = fp.SUB_FED / "incentives.csv"

# Maps Pydantic field names (must be valid Python identifiers) to
# incentives.csv's actual column headers, in the file's own column order.
CSV_COLUMNS = {
    "scenario": "scenario",
    "description": "description",
    "states": "state(s)",
    "building_types": "building type(s)",
    "building_vintages": "building vintage(s)",
    "end_uses": "end use(s)",
    "techs": "tech(s)",
    "fuel_types": "fuel type(s)",
    "base_fuel": "base fuel",
    "base_fuel_backup": "base fuel backup",
    "modification": "modification",
    "scope": "scope",
    "ira": "ira",
    "increase_pct": "increase pct",
    "performance_level": "performance level",
    "performance_units": "performance units",
    "credit_pct": "credit pct",
    "rebate_amount": "rebate amount",
    "rebate_units": "rebate units",
    "start_year": "start year",
    "end_year": "end year",
    "applicable_fraction": "applicable fraction",
    "fraction_notes": "fraction notes",
}

# Review/triage columns written alongside the drafted incentives.csv columns.
META_COLUMNS = [
    "dsire_id", "dsire_name", "dsire_match_reason", "source_url",
    "llm_confidence", "llm_open_questions",
]


class DraftedIncentiveRow(BaseModel):
    """One candidate incentives.csv row drafted from a DSIRE program record.

    Every field has a safe default so a response that omits a key (seen in
    practice from weaker/non-strict-schema providers, usually on thin or
    multi-technology-bundled input) resolves to that default instead of
    raising a hard ValidationError that would discard the whole row. The
    drafting loop in main() separately flags, in open_questions, exactly
    which fields a given response actually omitted (vs. deliberately left
    blank per a field's own instructions) -- defaults here are a safety
    net for the row to survive, not a claim that the default is correct.
    """

    scenario: Literal[
        "reference", "optimistic", "aggressive", "proposed", "remove",
        "aggressive state", "unclear",
    ] = Field(default="unclear", description=(
        "Almost always 'reference' for a currently active, "
        "already-enacted incentive program. Use 'unclear' only if you "
        "genuinely can't tell -- never omit this field."
    ))
    description: str = Field(default="", description=(
        "Program name/administrator plus a citation to its source URL, "
        "in the style of the examples."
    ))
    states: str = Field(default="", description="Comma-separated state abbreviations, or 'all'.")
    building_types: str = ""
    building_vintages: str = ""
    end_uses: str = Field(default="", description=(
        "Prefer Scout's existing vocabulary shown in the examples "
        "(cooking, cooling, drying, heating, water heating, or 'all') "
        "over inventing a new category."
    ))
    techs: str = Field(default="", description=(
        "Prefer Scout's existing vocabulary shown in the examples (ASHP, "
        "GSHP, central AC, electric WH, furnace (NG), roof, wall, "
        "windows conduction, rooftop_ASHP-heat, or 'all'). If nothing "
        "fits, pick the closest match and flag the mismatch in "
        "open_questions rather than leaving this blank."
    ))
    fuel_types: str = ""
    base_fuel: str = ""
    base_fuel_backup: str = ""
    modification: Literal["replace", ""] = ""
    scope: Literal["federal", "non-federal", ""] = ""
    ira: Literal["yes", ""] = ""
    increase_pct: str = ""
    performance_level: str = Field(default="", description=(
        "Leave blank if the input doesn't state a specific numeric "
        "threshold -- never invent one."
    ))
    performance_units: str = ""
    credit_pct: str = ""
    rebate_amount: str = Field(default="", description=(
        "Leave blank if not explicitly stated in the input -- never "
        "invent a number."
    ))
    rebate_units: str = ""
    start_year: str = Field(default="", description=(
        "The year from 'Start date' if given (e.g. '01/26/1986' -> "
        "'1986'). Leave blank if 'Start date' is empty -- never guess a "
        "year from surrounding text instead."
    ))
    end_year: str = Field(default="", description=(
        "The year from 'End date' if given, same rule as start_year. "
        "Leave blank if 'End date' is empty."
    ))
    applicable_fraction: str = Field(default="", description=(
        "Leave blank unless the input supports a specific fraction; do "
        "not default to 1 without justification in fraction_notes. If "
        "'Entire state' is No, this program does NOT cover the whole "
        "state -- do not write 1 here unless the input independently "
        "states what share of the state (or which counties/utility "
        "territory) is covered; otherwise leave blank and flag in "
        "open_questions that a territory-based fraction is needed. "
        "Similarly, if 'Incentive amounts' shows a '[Low Income "
        "Residential]'-tagged amount separate from a general "
        "'Residential' amount, that's an income-restricted tier -- note "
        "in open_questions that this program has a separate low-income "
        "tier (a human should draft it as its own row with its own "
        "income-scoped fraction, the way existing AMI-tiered rows in "
        "incentives.csv do) rather than merging both amounts into one row."
    ))
    fraction_notes: str = ""
    confidence: Literal["low", "medium", "high"] = Field(default="low", description=(
        "'high' only if nearly every field above has direct textual "
        "support in the input; 'low' if several fields are blank or "
        "guessed from thin evidence."
    ))
    open_questions: str = Field(default="", description=(
        "What a human reviewer should check or decide before this row "
        "is added: missing values, judgment calls made, ambiguous "
        "technology mappings, etc. Empty string only if there is truly "
        "nothing to flag."
    ))


def get_client(provider):
    """Construct the API client for the chosen provider, or exit with a
    clear message if the key or package is missing."""
    if provider == "anthropic":
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print(
                "\nExpected environment variable ANTHROPIC_API_KEY not "
                "set.\nGet an API key from "
                "https://console.anthropic.com/settings/keys\n"
                "Add it to a .env file at the project root (already "
                "gitignored):\n$ echo 'ANTHROPIC_API_KEY=your api key' "
                ">> .env\n"
            )
            sys.exit(1)
        try:
            import anthropic
        except ImportError:
            print('\nThe "anthropic" package is required for '
                  "--provider anthropic.\n$ pip install \".[llm]\"\n")
            sys.exit(1)
        return anthropic.Anthropic(api_key=api_key)

    if provider == "gemini":
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get(
            "GEMINI_API_KEY")
        if not api_key:
            print(
                "\nExpected environment variable GOOGLE_API_KEY (or "
                "GEMINI_API_KEY) not set.\nGet an API key from "
                "https://aistudio.google.com/apikey\n"
                "Add it to a .env file at the project root (already "
                "gitignored):\n$ echo 'GOOGLE_API_KEY=your api key' "
                ">> .env\n"
            )
            sys.exit(1)
        try:
            from google import genai
        except ImportError:
            print('\nThe "google-genai" package is required for '
                  "--provider gemini.\n$ pip install \".[llm]\"\n")
            sys.exit(1)
        return genai.Client(api_key=api_key)

    if provider == "cborg":
        api_key = os.environ.get("CBORG_API_KEY")
        if not api_key:
            print(
                "\nExpected environment variable CBORG_API_KEY not set.\n"
                "Request access and an API key per "
                "https://cborg.lbl.gov/api_faq/ (requires LBLnet/VPN).\n"
                "Add it to a .env file at the project root (already "
                "gitignored):\n$ echo 'CBORG_API_KEY=your api key' "
                ">> .env\n"
            )
            sys.exit(1)
        try:
            import openai
        except ImportError:
            print('\nThe "openai" package is required for '
                  "--provider cborg (CBORG is OpenAI-API-compatible).\n"
                  "$ pip install \".[llm]\"\n")
            sys.exit(1)
        return openai.OpenAI(api_key=api_key, base_url=CBORG_BASE_URL)

    raise ValueError(f"Unknown provider: {provider}")


def find_latest_staging_file():
    """Find the most recently written dsire_incentive_updates_*.csv."""
    candidates = sorted(DSIRE_DIR.glob("dsire_incentive_updates_*.csv"))
    if not candidates:
        print(
            "No dsire_incentive_updates_*.csv staging file found in "
            f"{DSIRE_DIR}. Run dsire_incentive_checker.py first, or pass "
            "--input explicitly."
        )
        sys.exit(1)
    return candidates[-1]


def build_few_shot_block(n=6):
    """Sample up to n existing incentives.csv rows, spread across distinct
    tech(s) values, formatted as labeled examples for the system prompt."""
    with open(INCENTIVES_CSV, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    seen_techs = set()
    examples = []
    for row in rows:
        key = row.get("tech(s)", "")
        if key in seen_techs:
            continue
        seen_techs.add(key)
        examples.append(row)
        if len(examples) >= n:
            break

    blocks = []
    for i, row in enumerate(examples, 1):
        lines = [f"Example {i}:"]
        for header in CSV_COLUMNS.values():
            lines.append(f"  {header}: {row.get(header, '')}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def build_system_prompt(few_shot_block):
    return (
        "You are drafting candidate rows for Scout's sub_fed/incentives.csv "
        "file, which tracks sub-federal (and some federal) financial "
        "incentive programs (rebates, tax credits) for specific building "
        "equipment and envelope upgrades. These rows are inputs to the "
        "Scout building energy decarbonization model.\n\n"
        "Given one DSIRE Programs API record (name, state, technologies, "
        "incentive amounts, summary, eligibility details, source URL), "
        "draft ONE candidate row matching the schema and conventions shown "
        "in these real existing rows:\n\n"
        f"{few_shot_block}\n\n"
        "Rules:\n"
        "- Never invent a number (dollar amount, percentage, performance "
        "threshold, year) that is not explicitly present in the input. "
        "Leave the field blank and explain what's missing in "
        "open_questions instead.\n"
        "- Prefer Scout's existing controlled vocabulary for tech(s) and "
        "end use(s), shown in the examples above, over inventing new "
        "category names.\n"
        "- description must cite the source (program name/administrator "
        "and URL), matching the citation style in the examples.\n"
        "- Set confidence honestly: most drafts from a short program "
        "summary should be 'low' or 'medium', not 'high'.\n"
        "- If 'Entire state' is No, this program covers only part of the "
        "state (e.g. one utility's service territory) -- do not set "
        "applicable_fraction to 1 in that case; leave it blank and flag "
        "in open_questions that the territory's share of the state needs "
        "to be researched, unless the input itself states that share.\n"
        "- If 'Incentive amounts' includes a '[Low Income Residential]'-"
        "tagged amount alongside a general one, flag in open_questions "
        "that this program has an income-restricted tier that should be "
        "drafted as its own row.\n"
        "- Take start_year/end_year only from 'Start date'/'End date' if "
        "those are non-empty; don't infer a year from summary/details "
        "text instead, and don't leave them populated with a guess just "
        "because the program is clearly ongoing.\n"
        "- This is a DRAFT for a human analyst to review and edit before "
        "it is added to incentives.csv. It is not the final answer."
    )


ENTIRE_STATE_LABELS = {"True": "Yes", "False": "No"}


def build_user_message(program):
    entire_state = ENTIRE_STATE_LABELS.get(
        (program.get("entire_state") or "").strip(), "Unknown"
    )
    fields = [
        f"Program name: {program.get('name', '')}",
        f"State: {program.get('state', '')}",
        f"Entire state: {entire_state}",
        f"Program type: {program.get('program_type', '')}",
        f"Administrator: {program.get('administrator', '')}",
        f"Technologies (DSIRE taxonomy): {program.get('technologies', '')}",
        f"Incentive amounts: {program.get('incentive_amounts', '')}",
        f"Summary: {program.get('summary', '')}",
        f"Details: {program.get('details', '')}",
        f"Start date: {program.get('start_date', '')}",
        f"End date: {program.get('end_date', '')}",
        f"Source URL: {program.get('website_url', '')}",
        f"DSIRE last updated: {program.get('last_updated', '')}",
    ]
    return "\n".join(fields)


def draft_row_anthropic(client, model, system_prompt, program, effort):
    """Call Claude to draft one candidate row.

    Returns (DraftedIncentiveRow, {"input_tokens": int, "output_tokens": int}).
    """
    system_blocks = [{
        "type": "text",
        "text": system_prompt,
        "cache_control": {"type": "ephemeral"},
    }]
    response = client.messages.parse(
        model=model,
        max_tokens=2000,
        system=system_blocks,
        output_config={"effort": effort},
        messages=[{"role": "user", "content": build_user_message(program)}],
        output_format=DraftedIncentiveRow,
    )
    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
    return response.parsed_output, usage


def draft_row_gemini(client, model, system_prompt, program):
    """Call Gemini to draft one candidate row.

    Returns (DraftedIncentiveRow, {"input_tokens": int, "output_tokens": int}).
    """
    from google.genai import types

    response = client.models.generate_content(
        model=model,
        contents=build_user_message(program),
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_json_schema=DraftedIncentiveRow.model_json_schema(),
        ),
    )
    drafted = DraftedIncentiveRow.model_validate(json.loads(response.text))
    try:
        usage = {
            "input_tokens": response.usage_metadata.prompt_token_count,
            "output_tokens": response.usage_metadata.candidates_token_count,
        }
    except AttributeError:
        # Token usage field names aren't pinned as tightly for this SDK as
        # for Anthropic's -- degrade to an unknown cost rather than crash.
        usage = {"input_tokens": 0, "output_tokens": 0}
    return drafted, usage


def draft_row_cborg(client, model, system_prompt, program):
    """Call a CBORG-hosted model (OpenAI-compatible) to draft one candidate
    row.

    Returns (DraftedIncentiveRow, {"input_tokens": int, "output_tokens": int}).
    Uses non-strict json_schema mode -- CBORG's on-prem models (Gemma/GPT-OSS
    derivatives) don't reliably satisfy OpenAI strict mode's requirement
    that every object set additionalProperties: false, which Pydantic's
    model_json_schema() doesn't emit by default.
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": build_user_message(program)},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "drafted_incentive_row",
                "schema": DraftedIncentiveRow.model_json_schema(),
            },
        },
    )
    drafted = DraftedIncentiveRow.model_validate(
        json.loads(response.choices[0].message.content)
    )
    usage = {
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
    }
    return drafted, usage


def draft_row(provider, client, model, system_prompt, program, effort):
    """Dispatch to the chosen provider's drafting call."""
    if provider == "anthropic":
        return draft_row_anthropic(client, model, system_prompt, program, effort)
    if provider == "gemini":
        return draft_row_gemini(client, model, system_prompt, program)
    if provider == "cborg":
        return draft_row_cborg(client, model, system_prompt, program)
    raise ValueError(f"Unknown provider: {provider}")


def load_processed_ids(output_path):
    """Read dsire_id values already present in an existing output file."""
    if not output_path.exists():
        return set()
    with open(output_path, encoding="utf-8-sig", newline="") as f:
        return {row["dsire_id"] for row in csv.DictReader(f)}


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Draft candidate incentives.csv rows from a "
            "dsire_incentive_updates_*.csv staging file using an LLM. "
            "Writes a separate review CSV; never edits incentives.csv."
        )
    )
    parser.add_argument(
        "--provider", default="anthropic",
        choices=["anthropic", "gemini", "cborg"],
        help="Which LLM provider to draft with (default: anthropic). "
             "'cborg' uses LBL's free on-prem models (requires LBLnet/VPN "
             "and a CBORG_API_KEY) but is lower-quality -- scrutinize its "
             "drafts more than Claude's or Gemini's."
    )
    parser.add_argument(
        "--model", type=str,
        help="Override the provider's default model id. Defaults: "
             f"anthropic={DEFAULT_MODELS['anthropic']}, "
             f"gemini={DEFAULT_MODELS['gemini']}, "
             f"cborg={DEFAULT_MODELS['cborg']}."
    )
    parser.add_argument(
        "--input", type=str,
        help="Path to a dsire_incentive_updates_*.csv staging file. "
             "Defaults to the most recently written one in sub_fed/dsire/."
    )
    parser.add_argument(
        "--output", type=str,
        help="Path to write the drafts CSV to. Defaults to "
             "sub_fed/dsire/dsire_incentive_drafts_<today>.csv"
    )
    parser.add_argument(
        "--limit", type=int,
        help="Only draft the first N rows (useful to bound cost while "
             "testing). Defaults to all rows in the input file."
    )
    parser.add_argument(
        "--effort", default="medium",
        choices=["low", "medium", "high", "xhigh", "max"],
        help="Reasoning effort per row (default: medium). Anthropic only "
             "-- ignored for --provider gemini/cborg."
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Skip DSIRE ids already present in --output, appending only "
             "new drafts instead of starting over."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print the prompt that would be sent for the first input row "
             "and exit, without calling the API or spending anything."
    )
    args = parser.parse_args()
    model = args.model or DEFAULT_MODELS[args.provider]

    input_path = Path(args.input) if args.input else find_latest_staging_file()
    with open(input_path, encoding="utf-8-sig", newline="") as f:
        programs = list(csv.DictReader(f))
    if args.limit:
        programs = programs[:args.limit]
    print(f"Loaded {len(programs)} candidate program(s) from {input_path}")

    few_shot_block = build_few_shot_block()
    system_prompt = build_system_prompt(few_shot_block)

    if args.dry_run:
        if not programs:
            print("Input file is empty; nothing to preview.")
            return
        print(f"Provider: {args.provider}, model: {model}")
        print("=" * 20, "SYSTEM PROMPT", "=" * 20)
        print(system_prompt)
        print("=" * 20, "USER MESSAGE (row 1)", "=" * 20)
        print(build_user_message(programs[0]))
        return

    client = get_client(args.provider)

    output_path = (
        Path(args.output) if args.output
        else DSIRE_DIR / f"dsire_incentive_drafts_{date.today().isoformat()}.csv"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # The SDK already retries transient (429/5xx/connection) errors
    # internally; anything that still raises here is worth logging and
    # skipping rather than aborting the whole batch over one bad row.
    if args.provider == "anthropic":
        import anthropic
        api_error_types = (anthropic.APIStatusError, anthropic.APIConnectionError)
    elif args.provider == "gemini":
        from google.genai import errors as genai_errors
        api_error_types = (genai_errors.APIError,)
    else:
        import openai
        api_error_types = (openai.APIStatusError, openai.APIConnectionError)

    already_processed = load_processed_ids(output_path) if args.resume else set()
    if already_processed:
        print(f"Resuming: skipping {len(already_processed)} already-drafted "
              f"row(s) found in {output_path}")

    write_header = not (args.resume and output_path.exists())
    mode = "a" if args.resume and output_path.exists() else "w"

    fieldnames = META_COLUMNS + list(CSV_COLUMNS.values())

    total_input_tokens = 0
    total_output_tokens = 0
    confidence_counts = {"low": 0, "medium": 0, "high": 0}
    error_count = 0
    consecutive_errors = 0
    max_consecutive_errors = 5

    with open(output_path, mode, encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()

        for i, program in enumerate(programs, 1):
            dsire_id = program.get("dsire_id", "")
            if dsire_id in already_processed:
                continue

            label = f"[{i}/{len(programs)}] {program.get('state', '')} - " \
                    f"{program.get('name', '')}"
            try:
                drafted, usage = draft_row(
                    args.provider, client, model, system_prompt, program,
                    args.effort)
            except api_error_types as e:
                print(f"{label} -> ERROR ({type(e).__name__}): {e}")
                error_count += 1
                consecutive_errors += 1
            except Exception as e:
                # Malformed JSON from the model, a Pydantic ValidationError,
                # etc. -- also worth skipping, not aborting the batch over.
                print(f"{label} -> ERROR ({type(e).__name__}): {e}")
                error_count += 1
                consecutive_errors += 1
            else:
                consecutive_errors = 0

            if consecutive_errors >= max_consecutive_errors:
                print(
                    f"\nAborting after {consecutive_errors} consecutive "
                    "errors -- this looks like a config problem (bad "
                    "model id, expired key, etc.), not a few bad rows. "
                    "Fix the cause above, then re-run with --resume to "
                    "pick up where this stopped."
                )
                break
            if consecutive_errors:
                continue

            # Pydantic defaults keep a response that omits a key from
            # discarding the whole row, but a defaulted field is NOT the
            # same as the model deliberately leaving it blank -- flag
            # exactly which fields were actually missing from the raw
            # response so a reviewer doesn't mistake "model didn't say"
            # for "model checked and found nothing." Works the same
            # regardless of provider, since model_fields_set reflects
            # what model_validate() actually saw, not what the schema
            # declares.
            omitted = sorted(
                set(DraftedIncentiveRow.model_fields) - drafted.model_fields_set
            )
            if omitted:
                drafted.open_questions = (
                    f"[LLM response omitted field(s), filled with a "
                    f"placeholder default -- verify: {', '.join(omitted)}] "
                    + drafted.open_questions
                )

            total_input_tokens += usage["input_tokens"]
            total_output_tokens += usage["output_tokens"]
            confidence_counts[drafted.confidence] += 1
            suffix = f" (omitted: {', '.join(omitted)})" if omitted else ""
            print(f"{label} -> confidence={drafted.confidence}{suffix}")

            row = {
                "dsire_id": dsire_id,
                "dsire_name": program.get("name", ""),
                "dsire_match_reason": program.get("match_reason", ""),
                "source_url": program.get("website_url", ""),
                "llm_confidence": drafted.confidence,
                "llm_open_questions": drafted.open_questions,
            }
            for field, header in CSV_COLUMNS.items():
                row[header] = getattr(drafted, field)
            writer.writerow(row)
            f.flush()

    print(f"\nDrafted {sum(confidence_counts.values())} row(s): "
          f"{confidence_counts['high']} high confidence, "
          f"{confidence_counts['medium']} medium, "
          f"{confidence_counts['low']} low.")
    if error_count:
        print(f"{error_count} row(s) failed and were skipped -- re-run "
              f"with --resume to retry just those.")
    pricing = PRICING.get((args.provider, model))
    if pricing:
        price_in, price_out = pricing
        cost = total_input_tokens * price_in + total_output_tokens * price_out
        print(f"Estimated cost: ${cost:.2f} "
              f"({total_input_tokens} input, {total_output_tokens} output "
              f"tokens)")
    else:
        print(f"Cost estimate unavailable for {args.provider}/{model} -- "
              f"no pricing on file for this model ({total_input_tokens} "
              f"input, {total_output_tokens} output tokens used).")
    print(f"Wrote drafts to {output_path}")
    print("Review every row -- especially performance_level, rebate_amount, "
          "and applicable_fraction -- before hand-copying it into "
          "sub_fed/incentives.csv. This script never edits that file.")


if __name__ == "__main__":
    main()
