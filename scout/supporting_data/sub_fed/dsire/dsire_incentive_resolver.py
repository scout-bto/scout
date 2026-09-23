"""Third-stage tool: try to resolve blank performance level/performance
units cells left by dsire_incentive_drafter.py.

Why this is a separate script, not a drafter option: the drafter works
entirely from the text DSIRE's own API returns, and is instructed to leave
performance level/units blank rather than invent a number -- which,
empirically, it does for almost every row, because DSIRE's own program
records routinely cite an efficiency requirement by NAME (ENERGY STAR
"most efficient", a CEE tier, "as described in tax code") without restating
the actual number. That number usually does exist -- one hop further away,
on the program's own primary source page (the same `source_url` the
drafter already recorded) rather than in DSIRE's summary of it.

This script re-fetches that primary source directly (a plain HTTP GET --
unlike an interactive AI web-fetch tool, it cannot render JavaScript, so a
single-page-app or bot-protected site may return incomplete or blocked
content; that's a real, expected failure mode here, not a bug), asks an LLM
to extract any stated numeric efficiency threshold verbatim (never to
invent or convert one), and then applies a small DETERMINISTIC conversion
step in plain Python -- not the LLM -- to map the extracted value into
Scout's own performance_units vocabulary (COP, UEF, AFUE, R value). Unit
arithmetic is kept out of the LLM's hands deliberately: it is exactly the
kind of step an LLM can silently get wrong, and the conversion factor
(divide a Btu/(W*hr)-type rating -- SEER/SEER2/EER/EER2/HSPF/HSPF2 -- by
3.412 to get a dimensionless COP) is already used by hand elsewhere in
incentives.csv (see the central-AC 25C row's own description), so this
just automates that existing, already-validated method rather than
inventing a new one.

Pass --follow-pdfs to also download and read PDFs linked from the primary
source page (rate schedules and incentive tables routinely live there
rather than in the page's own text -- confirmed by prototyping against a
handful of rows before this was wired in for real). This costs more
(larger prompts, one extra fetch per linked PDF, capped by
--max-pdfs-per-row) and needs MORE scrutiny of its output, not less, for
two reasons the prototype surfaced directly:
- A PDF found via a program's page can cover a DIFFERENT technology than
  the one this row is for (DSIRE's own technology tag can be wrong or
  stale) -- the model is instructed to refuse rather than attribute a
  table to the wrong tech, but that refusal depends on the tag it's given
  actually being checked against the source, so treat a PDF-derived
  "found" result as needing a source_quote read, not a rubber stamp.
- A PDF's table can be far more granular (e.g. six capacity/vintage tiers)
  than any existing incentives.csv row's tier convention (which tops out
  around two, like "warm climates"/"cold climates") -- resolver_notes
  flags this so a human can decide how to collapse it, since this script
  won't invent that judgment call either.

What this does NOT do even with --follow-pdfs:
- Resolve a citation-by-name to an EXTERNAL standard that isn't hosted on
  the program's own site at all (e.g. the federal 25C rows' reference to
  "CEE's highest efficiency tier" -- that number lives on CEE's own site,
  which isn't `source_url` for those rows). Also comes back unresolved.
- Touch any row that already has a non-blank performance level -- this
  only fills gaps, never overwrites an existing drafted value.
- Render JavaScript, or follow more than one hop of links (a PDF linked
  from a PDF, or a page that loads its rate table via an API call, is out
  of scope).

Input: one or more drafts CSVs written by dsire_incentive_drafter.py
(defaults to every dsire_incentive_drafts_*.csv and
dsire_incentive_backfill_drafts_*.csv found in this directory). Output:
two files --
1. The same rows, with performance level/units filled in wherever
   resolved, plus resolver_status/resolver_source_quote/resolver_notes/
   candidate_pdf_links/cites_external_standard columns for review -- same
   "read before trusting" expectation as the drafter's own
   llm_confidence/llm_open_questions.
2. A much narrower "followup" worklist (dsire_incentive_followup_*.csv):
   just the rows still needing a human, or a separate/more thorough AI
   pass, to go look somewhere this script didn't -- each with its
   candidate_pdf_links (every PDF link found on the row's source page,
   ranked, regardless of whether --follow-pdfs was used to actually read
   any of them -- finding them costs nothing beyond the page fetch this
   script already makes) and cites_external_standard (the named standard,
   e.g. "CEE's highest efficiency tier", when that's why nothing was
   found -- that number lives on a different site entirely, not a link on
   this page). This file is rebuilt fresh from the full resolved CSV on
   every run, so it stays accurate across multiple --resume passes. This
   is meant to be a recurring step: expect to run it again each time
   incentives.csv is updated with new candidate rows, same as the checker
   and drafter.

Supports the same two providers as the drafter -- pick with --provider
(anthropic default, gemini via --provider gemini) -- and reuses its
model/pricing tables, so update DEFAULT_MODELS/PRICING in
dsire_incentive_drafter.py, not here, if a model id 404s.

Usage (from the project root):

    # Preview the prompt for the first resolvable row, $0
    $ python scout/supporting_data/sub_fed/dsire/dsire_incentive_resolver.py --dry-run

    # Small paid test batch
    $ python scout/supporting_data/sub_fed/dsire/dsire_incentive_resolver.py --limit 5

    # Full run across every drafts file in this directory
    $ python scout/supporting_data/sub_fed/dsire/dsire_incentive_resolver.py

    # Resume an interrupted run without re-paying for rows already resolved
    $ python scout/supporting_data/sub_fed/dsire/dsire_incentive_resolver.py \\
        --output dsire_incentive_resolved_2026-09-17.csv --resume

"""

import re
import sys
import csv
import json
import argparse
from io import BytesIO
from datetime import date
from pathlib import Path
from typing import Literal
from urllib.parse import urljoin

import requests
from pydantic import BaseModel, Field
from pypdf import PdfReader
from dotenv import load_dotenv

# Reuse the drafter's provider plumbing, model defaults, pricing table, and
# incentives.csv column mapping rather than re-deriving them here.
from dsire_incentive_drafter import (
    CSV_COLUMNS, DEFAULT_MODELS, PRICING, get_client,
)

load_dotenv()

DSIRE_DIR = Path(__file__).resolve().parent
FETCH_TIMEOUT = 20
MAX_PAGE_CHARS = 20_000  # bound token cost per row; plain text, not HTML
MAX_PDF_CHARS = 20_000  # bound token cost per linked PDF, same reasoning
DEFAULT_MAX_PDFS_PER_ROW = 2
USER_AGENT = "Mozilla/5.0 (compatible; ScoutIncentivesResolver/1.0)"

# Efficiency-rating units that are dimensionally Btu/(W*hr), the same as
# EER -- dividing by 3.412 (Btu/hr per W) converts any of them to a
# dimensionless COP. This is the one conversion already used by hand
# elsewhere in incentives.csv; AFUE and R value are Scout's own units
# already and pass through unchanged (AFUE is normalized from a percent-
# style number like 95 to Scout's fractional convention, 0.95).
RATING_UNITS_TO_COP = {"SEER", "SEER2", "EER", "EER2", "HSPF", "HSPF2"}
KNOWN_RAW_UNITS = RATING_UNITS_TO_COP | {"UEF", "AFUE", "R value", "COP"}


class ResolvedEntry(BaseModel):
    """One stated numeric efficiency threshold found on the primary source."""

    tier_label: str = Field(description=(
        "Empty string if the page states a single, uniform threshold for "
        "this technology. Otherwise the label the SOURCE TEXT ITSELF uses "
        "to distinguish multiple thresholds -- e.g. 'cold climates', "
        "'warm climates', 'north', 'south', 'low income', 'moderate "
        "income'. Never invent a split the source doesn't make."
    ))
    raw_value: float = Field(description=(
        "The number exactly as printed on the page -- e.g. 15.2 for "
        "'SEER2 >= 15.2', or 95 for 'AFUE of 95% or greater' (do not "
        "pre-convert a percent to a fraction; that happens later in code)."
    ))
    raw_unit: Literal["SEER", "SEER2", "EER", "EER2", "HSPF", "HSPF2",
                      "UEF", "AFUE", "R value", "COP"] = Field(
        description="The unit exactly as stated on the page.")
    source_quote: str = Field(description=(
        "The verbatim sentence or phrase from the page that states this "
        "threshold, for a human reviewer to check against the live page."
    ))


class ResolvedPerformance(BaseModel):
    """Result of trying to extract a stated performance threshold for one
    drafted incentives.csv-candidate row from its primary source page."""

    found: bool = Field(description=(
        "Whether the page states ANY numeric efficiency/performance "
        "threshold for the technology/end use given in the prompt -- "
        "false if it only names a standard without a number (e.g. "
        "'must be ENERGY STAR certified', 'must meet CEE's highest "
        "tier'), requires an external document not included on this "
        "page, or doesn't cover this technology at all."
    ))
    entries: list[ResolvedEntry] = Field(default_factory=list, description=(
        "Empty if found is false. One entry if there's a single uniform "
        "threshold; multiple only if the source text itself splits the "
        "requirement into clearly labeled tiers (see tier_label)."
    ))
    notes: str = Field(description=(
        "Why nothing was found, or any caveat a human reviewer should "
        "know (e.g. 'page references a linked rate-schedule PDF that "
        "isn't included here', 'page covers commercial equipment, not "
        "the residential program this row is for'). Empty string only if "
        "found is true and there's nothing to flag."
    ))
    cites_external_standard: str = Field(default="", description=(
        "Only when found is false: if the material names a specific "
        "external standard or tier as the qualifying requirement without "
        "stating its actual number (e.g. 'CEE's highest efficiency "
        "tier', 'ENERGY STAR Most Efficient', 'IECC 2021'), name that "
        "standard here verbatim, exactly as printed -- this points a "
        "human at where else to look (CEE's own site, ENERGY STAR's own "
        "criteria page, the IECC code text), since it won't be on this "
        "program's own page. Empty string if no such standard is named."
    ))


def build_system_prompt():
    return (
        "You are checking one financial incentive program's own web page "
        "for a specific piece of information that a prior automated pass "
        "could not find: the numeric energy-efficiency threshold "
        "equipment must meet to qualify (SEER/SEER2/EER/EER2/HSPF/HSPF2/"
        "UEF/AFUE/R value/COP).\n\n"
        "You will be given the technology and end use this threshold is "
        "for, plus visible text from the program's page (HTML tags "
        "stripped) and, when available, text extracted from PDF(s) linked "
        "from that page (rate schedules and incentive tables routinely "
        "live in a linked PDF rather than the page itself). "
        "Extract ONLY a threshold that is explicitly, numerically stated "
        "in this material for that technology. Rules:\n"
        "- Never invent, estimate, or infer a number. If the material "
        "only names a standard ('ENERGY STAR certified', 'CEE's highest "
        "efficiency tier') without giving the actual number, set "
        "found=false, name that standard verbatim in "
        "cites_external_standard, and say so in notes.\n"
        "- Report the raw value and unit exactly as printed -- do not "
        "convert units or percentages yourself.\n"
        "- If the material states different thresholds for different "
        "regions or income tiers, return one entry per tier with the "
        "source text's own label. Do not invent a tier split that isn't "
        "in the text.\n"
        "- CRITICAL: a linked PDF can be for a DIFFERENT, unrelated "
        "equipment or product category than the technology named above "
        "(e.g. a document with tables for packaged terminal units when "
        "this row is about a ground-source heat pump). Check that the "
        "table you're citing actually names or clearly describes the "
        "given technology before using it. If the only efficiency data "
        "present is for a different technology, set found=false and say "
        "so in notes -- do not attribute another technology's table to "
        "this one just because it's the only table available.\n"
        "- If the material is about a different program entirely, or is "
        "a login/error/placeholder page, set found=false and explain in "
        "notes."
    )


def build_user_message(row, page_text):
    return (
        f"Technology: {row.get('tech(s)', '')}\n"
        f"End use: {row.get('end use(s)', '')}\n"
        f"Program name: {row.get('dsire_name', '')}\n"
        f"State: {row.get('state(s)', '')}\n\n"
        f"Page text (truncated to {MAX_PAGE_CHARS} chars):\n{page_text}"
    )


def html_to_text(html):
    """Minimal, dependency-free HTML-to-text: strip script/style blocks and
    tags, unescape a few common entities, collapse whitespace. Good enough
    for an LLM to read; not a rendering engine -- JS-injected content is
    invisible to this, same as to the plain GET that fetched it."""
    html = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", html)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    text = re.sub(r"&#\d+;", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def fetch_page(url):
    """Fetch a primary source page. Returns (visible_text, raw_html) --
    raw_html is only needed to find linked PDFs under --follow-pdfs.

    Plain requests.get -- no JS rendering. Sites that require it, or that
    block non-browser user agents, will fail here; that's surfaced as a
    fetch_failed row, not silently swallowed.
    """
    response = requests.get(
        url, timeout=FETCH_TIMEOUT, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    return html_to_text(response.text)[:MAX_PAGE_CHARS], response.text


# Filename keywords suggesting a PDF holds actual criteria/tables rather
# than marketing copy -- found empirically: a page can link several PDFs
# (overview, brochure, application form, incentive table, ...), and only
# --max-pdfs-per-row of them get fetched, so which ones sort first matters
# as much as whether the right one is linked at all.
PDF_RELEVANCE_KEYWORDS = [
    "incentive", "rebate", "table", "rate", "spec", "eligib", "qualif",
    "requirement", "definition", "schedule", "measure", "efficiency",
]


def find_pdf_links(base_url, html):
    """Absolute URLs of every PDF hyperlink on a fetched page, ranked so a
    filename that looks like it holds actual criteria/tables (contains a
    word like "incentive" or "spec") sorts before a generic one (an
    overview, brochure, FAQ) -- callers only follow the first few, so this
    ordering matters as much as completeness would."""
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', html, re.I)
    urls = list(dict.fromkeys(  # dedupe, preserve first-seen order
        urljoin(base_url, h) for h in hrefs if ".pdf" in h.lower()))

    def relevance(url):
        low = url.lower()
        return -sum(1 for kw in PDF_RELEVANCE_KEYWORDS if kw in low)

    return sorted(urls, key=relevance)  # stable sort keeps ties in order


def extract_pdf_text(pdf_url):
    """Fetch a linked PDF and return its extracted text, or raise.

    Same plain-GET caveat as fetch_page -- no JS, no auth walls -- plus a
    PDF can be image-only (scanned) and yield no extractable text at all,
    which surfaces as an empty string here rather than an exception.
    """
    response = requests.get(
        pdf_url, timeout=FETCH_TIMEOUT * 2, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    reader = PdfReader(BytesIO(response.content))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return re.sub(r"\s+", " ", text).strip()[:MAX_PDF_CHARS]


def gather_source_text(url, follow_pdfs, max_pdfs):
    """Fetch a row's primary source, optionally following linked PDFs.

    Returns (combined_text, used_pdf_urls, pdf_notes, candidate_pdf_links).
    candidate_pdf_links is every PDF link found on the page, ranked by
    find_pdf_links, regardless of follow_pdfs -- finding them costs
    nothing beyond the page fetch already made, so it's always done, even
    on a plain run, so a "not_found" row still leaves a concrete lead
    (see write_followup_worklist). used_pdf_urls is the subset actually
    downloaded and read (--follow-pdfs only). pdf_notes describes any
    linked PDF that was found but failed to fetch/parse -- that failure
    doesn't abort the row, since the page text alone may still be enough,
    or may be all that's honestly available.
    """
    page_text, html = fetch_page(url)
    candidate_pdf_links = find_pdf_links(url, html)
    if not follow_pdfs:
        return page_text, [], "", candidate_pdf_links

    used_pdfs, pdf_sections, pdf_notes = [], [], []
    for pdf_url in candidate_pdf_links[:max_pdfs]:
        try:
            pdf_text = extract_pdf_text(pdf_url)
        except Exception as e:
            # A single bad/protected/scanned PDF shouldn't sink the whole
            # row -- note it and move on to the next linked PDF, if any.
            pdf_notes.append(f"linked PDF {pdf_url} failed: {type(e).__name__}: {e}")
            continue
        if pdf_text:
            used_pdfs.append(pdf_url)
            pdf_sections.append(f"--- Linked PDF: {pdf_url} ---\n{pdf_text}")

    combined = page_text
    if pdf_sections:
        combined += "\n\n" + "\n\n".join(pdf_sections)
    return combined, used_pdfs, "; ".join(pdf_notes), candidate_pdf_links


def convert_to_scout_units(raw_value, raw_unit):
    """Deterministic unit conversion -- see module docstring for why this
    is plain code, not an LLM step."""
    if raw_unit in RATING_UNITS_TO_COP:
        return round(raw_value / 3.412, 3), "COP"
    if raw_unit == "AFUE":
        return (round(raw_value / 100, 3) if raw_value > 1 else raw_value), "AFUE"
    # UEF, COP, R value are already Scout's own units
    return raw_value, raw_unit


def format_performance(entries):
    """Combine resolved entries into incentives.csv's own convention for a
    performance level cell (a bare number, or "label: v; label: v" when the
    source splits by tier -- see the ASHP 25C row's "warm climates: 2.76;
    cold climates: 2.93" for the pattern this mirrors).

    Returns (performance_level, performance_units, problem) where problem
    is None on success or a string explaining why nothing could be safely
    written (in which case the caller leaves the cells blank).
    """
    converted = [
        (e.tier_label.strip(), *convert_to_scout_units(e.raw_value, e.raw_unit))
        for e in entries
    ]
    units_seen = {unit for _, _, unit in converted}
    if len(units_seen) > 1:
        return None, None, (
            "Multiple incompatible units extracted across entries for "
            f"the same technology ({', '.join(sorted(units_seen))}); "
            "needs manual review rather than a guessed single unit."
        )
    unit = next(iter(units_seen))
    if len(converted) == 1 and not converted[0][0]:
        return str(converted[0][1]), unit, None
    if any(not label for label, _, _ in converted):
        return None, None, (
            "Multiple thresholds found but not all clearly labeled by "
            "tier in the source text; needs manual review rather than a "
            "guessed pairing."
        )
    level = "; ".join(f"{label}: {value}" for label, value, _ in converted)
    return level, unit, None


def resolve_row_anthropic(client, model, system_prompt, row, page_text, effort):
    response = client.messages.parse(
        model=model,
        max_tokens=1500,
        system=[{"type": "text", "text": system_prompt,
                "cache_control": {"type": "ephemeral"}}],
        output_config={"effort": effort},
        messages=[{"role": "user", "content": build_user_message(row, page_text)}],
        output_format=ResolvedPerformance,
    )
    usage = {"input_tokens": response.usage.input_tokens,
             "output_tokens": response.usage.output_tokens}
    return response.parsed_output, usage


def resolve_row_gemini(client, model, system_prompt, row, page_text):
    from google.genai import types

    response = client.models.generate_content(
        model=model,
        contents=build_user_message(row, page_text),
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_json_schema=ResolvedPerformance.model_json_schema(),
        ),
    )
    resolved = ResolvedPerformance.model_validate(json.loads(response.text))
    try:
        usage = {"input_tokens": response.usage_metadata.prompt_token_count,
                 "output_tokens": response.usage_metadata.candidates_token_count}
    except AttributeError:
        usage = {"input_tokens": 0, "output_tokens": 0}
    return resolved, usage


def resolve_row(provider, client, model, system_prompt, row, page_text, effort):
    if provider == "anthropic":
        return resolve_row_anthropic(client, model, system_prompt, row, page_text, effort)
    if provider == "gemini":
        return resolve_row_gemini(client, model, system_prompt, row, page_text)
    raise ValueError(f"Unknown provider: {provider}")


def find_input_files():
    patterns = ["dsire_incentive_drafts_*.csv", "dsire_incentive_backfill_drafts_*.csv"]
    files = []
    for pattern in patterns:
        files.extend(sorted(DSIRE_DIR.glob(pattern)))
    return files


def load_candidate_rows(input_paths):
    """Load every row from the given drafts CSVs whose performance level is
    blank (this only fills gaps -- a row the drafter already resolved is
    left untouched), tagged with which file it came from."""
    rows = []
    for path in input_paths:
        with open(path, encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                if not row.get("performance level", "").strip():
                    row["_source_file"] = path.name
                    rows.append(row)
    return rows


def load_processed_ids(output_path):
    if not output_path.exists():
        return set()
    with open(output_path, encoding="utf-8-sig", newline="") as f:
        return {row["dsire_id"] for row in csv.DictReader(f)}


# Rows in these states still need somewhere else looked at -- either a
# candidate document this script found but didn't (fully) read, or a
# named external standard it can't follow at all. "resolved" and
# "ambiguous" are deliberately different: ambiguous already has extracted
# values, just not safely combinable, so it isn't a "go look elsewhere"
# case the same way.
FOLLOWUP_STATUSES = {"not_found"}
FOLLOWUP_COLUMNS = [
    "dsire_id", "dsire_name", "tech(s)", "end use(s)", "state(s)",
    "source_url", "resolver_status", "cites_external_standard",
    "candidate_pdf_links", "resolver_notes",
]


def default_followup_path(output_path):
    stem = output_path.stem
    stem = stem.replace("resolved", "followup") if "resolved" in stem else stem + "_followup"
    return output_path.with_name(stem + output_path.suffix)


def write_followup_worklist(resolved_path, followup_path):
    """Derive a focused hand-off worklist from a resolver output file: just
    the rows still needing a human (or another, separate AI pass) to go
    look somewhere this script didn't, with the concrete leads
    (candidate_pdf_links, cites_external_standard) up front instead of
    buried in the full, much wider resolver CSV.

    Rebuilt fresh from the complete resolved_path every call (not
    appended to), so it stays correct across multiple --resume passes
    regardless of how many separate runs built up resolved_path -- this
    is meant to reflect current cumulative state, not this run's slice
    of it. Returns the row count written.
    """
    with open(resolved_path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    followup_rows = [r for r in rows if r.get("resolver_status") in FOLLOWUP_STATUSES]
    with open(followup_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FOLLOWUP_COLUMNS)
        writer.writeheader()
        for r in followup_rows:
            writer.writerow({col: r.get(col, "") for col in FOLLOWUP_COLUMNS})
    return len(followup_rows)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Try to resolve blank performance level/performance units "
            "cells left by dsire_incentive_drafter.py, by re-fetching "
            "each row's primary source page and asking an LLM to extract "
            "any stated numeric threshold (never to invent one)."
        )
    )
    parser.add_argument(
        "--provider", default="anthropic", choices=["anthropic", "gemini"],
        help="Which LLM provider to resolve with (default: anthropic)."
    )
    parser.add_argument(
        "--model", type=str,
        help="Override the provider's default model id. Defaults: "
             f"anthropic={DEFAULT_MODELS['anthropic']}, "
             f"gemini={DEFAULT_MODELS['gemini']}."
    )
    parser.add_argument(
        "--input", type=str, nargs="+",
        help="One or more drafts CSVs to resolve against. Defaults to "
             "every dsire_incentive_drafts_*.csv and "
             "dsire_incentive_backfill_drafts_*.csv found in this directory."
    )
    parser.add_argument(
        "--output", type=str,
        help="Path to write the resolved CSV to. Defaults to "
             "sub_fed/dsire/dsire_incentive_resolved_<today>.csv"
    )
    parser.add_argument(
        "--followup-output", type=str,
        help="Path to write the narrower followup worklist to (rows still "
             "needing a human/another AI pass to check a candidate PDF or "
             "external standard). Defaults to --output's path with "
             "'resolved' swapped for 'followup' (or '_followup' appended)."
    )
    parser.add_argument(
        "--limit", type=int,
        help="Only attempt the first N candidate rows (rows with a blank "
             "performance level). Defaults to all of them."
    )
    parser.add_argument(
        "--effort", default="medium",
        choices=["low", "medium", "high", "xhigh", "max"],
        help="Reasoning effort per row (default: medium). Anthropic only."
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Skip dsire_ids already present in --output, appending only "
             "newly-attempted rows instead of starting over."
    )
    parser.add_argument(
        "--follow-pdfs", action="store_true",
        help="Also download and read PDFs linked from each row's primary "
             "source page -- costs more per row and needs more scrutiny "
             "of the result, not less (see module docstring)."
    )
    parser.add_argument(
        "--max-pdfs-per-row", type=int, default=DEFAULT_MAX_PDFS_PER_ROW,
        help=f"With --follow-pdfs, at most this many linked PDFs per row "
             f"(default: {DEFAULT_MAX_PDFS_PER_ROW})."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print the prompt for the first candidate row and exit, "
             "without fetching anything or spending money."
    )
    args = parser.parse_args()
    model = args.model or DEFAULT_MODELS[args.provider]

    input_paths = (
        [Path(p) for p in args.input] if args.input else find_input_files())
    if not input_paths:
        print(f"No dsire_incentive*drafts_*.csv files found in {DSIRE_DIR}. "
              "Run dsire_incentive_drafter.py first, or pass --input.")
        sys.exit(1)
    print(f"Reading candidate rows from: "
          f"{', '.join(p.name for p in input_paths)}")

    candidates = load_candidate_rows(input_paths)
    print(f"{len(candidates)} row(s) have a blank performance level.")
    if args.limit:
        candidates = candidates[:args.limit]

    system_prompt = build_system_prompt()

    if args.dry_run:
        if not candidates:
            print("Nothing to preview -- no candidate rows.")
            return
        row = candidates[0]
        print(f"Provider: {args.provider}, model: {model}")
        print("=" * 20, "SYSTEM PROMPT", "=" * 20)
        print(system_prompt)
        print("=" * 20, "CANDIDATE ROW", "=" * 20)
        print(f"dsire_id={row.get('dsire_id')} name={row.get('dsire_name')} "
              f"source_url={row.get('source_url')}")
        print("(page text is fetched live -- not shown here without "
              "actually making the request)")
        return

    client = get_client(args.provider)

    output_path = (
        Path(args.output) if args.output
        else DSIRE_DIR / f"dsire_incentive_resolved_{date.today().isoformat()}.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.provider == "anthropic":
        import anthropic
        api_error_types = (anthropic.APIStatusError, anthropic.APIConnectionError)
    else:
        from google.genai import errors as genai_errors
        api_error_types = (genai_errors.APIError,)

    already_processed = load_processed_ids(output_path) if args.resume else set()
    if already_processed:
        print(f"Resuming: skipping {len(already_processed)} already-"
              f"attempted row(s) found in {output_path}")

    write_header = not (args.resume and output_path.exists())
    mode = "a" if args.resume and output_path.exists() else "w"

    fieldnames = (
        ["drafts_source_file", "dsire_id", "dsire_name", "dsire_match_reason",
         "source_url", "llm_confidence", "llm_open_questions"]
        + list(CSV_COLUMNS.values())
        + ["resolver_status", "resolver_source_quote", "resolver_notes",
           "resolver_pdf_urls", "candidate_pdf_links", "cites_external_standard"]
    )

    total_input_tokens = 0
    total_output_tokens = 0
    status_counts = {"resolved": 0, "not_found": 0, "no_source_url": 0,
                     "fetch_failed": 0, "llm_error": 0, "ambiguous": 0}
    consecutive_errors = 0
    max_consecutive_errors = 5

    with open(output_path, mode, encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()

        for i, row in enumerate(candidates, 1):
            dsire_id = row.get("dsire_id", "")
            if dsire_id in already_processed:
                continue

            label = f"[{i}/{len(candidates)}] {row.get('state(s)', '')} - " \
                    f"{row.get('dsire_name', '')}"
            out_row = dict(row)
            out_row["drafts_source_file"] = out_row.pop("_source_file", "")

            source_url = row.get("source_url", "").strip()
            if not source_url:
                out_row.update(resolver_status="no_source_url",
                               resolver_source_quote="", resolver_notes="",
                               resolver_pdf_urls="", candidate_pdf_links="",
                               cites_external_standard="")
                status_counts["no_source_url"] += 1
                print(f"{label} -> no source_url, skipped")
                writer.writerow(out_row)
                f.flush()
                continue

            try:
                page_text, used_pdfs, pdf_fetch_notes, candidate_links = \
                    gather_source_text(
                        source_url, args.follow_pdfs, args.max_pdfs_per_row)
            except requests.exceptions.RequestException as e:
                out_row.update(resolver_status="fetch_failed",
                               resolver_source_quote="",
                               resolver_notes=f"{type(e).__name__}: {e}",
                               resolver_pdf_urls="", candidate_pdf_links="",
                               cites_external_standard="")
                status_counts["fetch_failed"] += 1
                print(f"{label} -> FETCH FAILED ({type(e).__name__})")
                writer.writerow(out_row)
                f.flush()
                continue
            out_row["candidate_pdf_links"] = "; ".join(candidate_links)
            if used_pdfs:
                print(f"{label} -> followed {len(used_pdfs)} linked PDF(s)")

            try:
                resolved, usage = resolve_row(
                    args.provider, client, model, system_prompt, row,
                    page_text, args.effort)
            except api_error_types as e:
                print(f"{label} -> API ERROR ({type(e).__name__}): {e}")
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    print(f"\nAborting after {consecutive_errors} "
                          "consecutive errors -- fix the cause above, then "
                          "re-run with --resume.")
                    break
                continue
            except Exception as e:
                out_row.update(resolver_status="llm_error",
                               resolver_source_quote="",
                               resolver_notes=f"{type(e).__name__}: {e}",
                               resolver_pdf_urls="; ".join(used_pdfs),
                               cites_external_standard="")
                status_counts["llm_error"] += 1
                print(f"{label} -> LLM/PARSE ERROR ({type(e).__name__})")
                writer.writerow(out_row)
                f.flush()
                continue

            consecutive_errors = 0
            total_input_tokens += usage["input_tokens"]
            total_output_tokens += usage["output_tokens"]
            out_row["resolver_pdf_urls"] = "; ".join(used_pdfs)
            notes_prefix = f"{pdf_fetch_notes}; " if pdf_fetch_notes else ""

            if not resolved.found or not resolved.entries:
                out_row.update(
                    resolver_status="not_found", resolver_source_quote="",
                    resolver_notes=notes_prefix + resolved.notes,
                    cites_external_standard=resolved.cites_external_standard)
                status_counts["not_found"] += 1
                print(f"{label} -> not found on primary source")
            else:
                out_row["cites_external_standard"] = ""
                level, units, problem = format_performance(resolved.entries)
                quotes = " | ".join(e.source_quote for e in resolved.entries)
                if problem:
                    out_row.update(
                        resolver_status="ambiguous", resolver_source_quote=quotes,
                        resolver_notes=notes_prefix + problem)
                    status_counts["ambiguous"] += 1
                    print(f"{label} -> found but ambiguous, needs manual review")
                else:
                    out_row["performance level"] = level
                    out_row["performance units"] = units
                    notes = notes_prefix + resolved.notes
                    if len(resolved.entries) > 3:
                        notes += (
                            f" [resolver: {len(resolved.entries)} tiers "
                            "extracted -- finer-grained than any existing "
                            "incentives.csv row; needs a human decision on "
                            "how to collapse/simplify before use]"
                        ).strip()
                    if used_pdfs:
                        notes += (
                            " [resolver: sourced from a linked PDF, not "
                            "the page itself -- double-check the "
                            "technology match against source_quote before "
                            "using]"
                        )
                    out_row.update(
                        resolver_status="resolved", resolver_source_quote=quotes,
                        resolver_notes=notes.strip())
                    status_counts["resolved"] += 1
                    print(f"{label} -> resolved: {level} {units}")

            writer.writerow(out_row)
            f.flush()

    print(f"\n{sum(status_counts.values())} row(s) attempted: " +
          ", ".join(f"{v} {k}" for k, v in status_counts.items() if v))
    pricing = PRICING.get((args.provider, model))
    if pricing:
        price_in, price_out = pricing
        cost = total_input_tokens * price_in + total_output_tokens * price_out
        print(f"Estimated cost: ${cost:.2f} "
              f"({total_input_tokens} input, {total_output_tokens} output tokens)")
    else:
        print(f"Cost estimate unavailable for {args.provider}/{model} "
              f"({total_input_tokens} input, {total_output_tokens} output tokens used).")
    print(f"Wrote {output_path}")

    followup_path = (
        Path(args.followup_output) if args.followup_output
        else default_followup_path(output_path))
    followup_count = write_followup_worklist(output_path, followup_path)
    print(f"Wrote {followup_count} row(s) needing further follow-up "
          f"(a candidate PDF to check, or a named external standard to "
          f"track down) to {followup_path}")

    print("Review resolver_status/resolver_source_quote/resolver_notes for "
          "every 'resolved' row against the live source_url before copying "
          "into incentives.csv -- this extracts and converts, but doesn't "
          "verify the page was read correctly.")


if __name__ == "__main__":
    main()
