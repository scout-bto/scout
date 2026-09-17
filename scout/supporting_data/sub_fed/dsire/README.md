# Finding candidate updates for sub_fed/incentives.csv from DSIRE

`../incentives.csv` tracks sub-federal (and some federal) financial
incentive programs (rebates, tax credits) for specific building
equipment/envelope upgrades, and has historically been updated by hand
when new programs are found. This directory automates the *finding*
half of that process against the
[DSIRE Programs API](https://docs.dsireusa.org/) and optionally drafts
a first-pass translation into `incentives.csv`'s schema — but **nothing
here writes to `incentives.csv` directly**. Every script writes a
separate CSV for a human to review.

Two scripts, run in order:

1. `dsire_incentive_checker.py` — queries DSIRE, filters, writes a
   staging CSV of candidate programs.
2. `dsire_incentive_drafter.py` — (optional) sends each candidate to an
   LLM to draft a candidate `incentives.csv` row, writes a drafts CSV.

Then you review and hand-copy accepted rows into `../incentives.csv`.

## Setup

Both scripts need API keys in a `.env` file at the project root
(gitignored — see `.gitignore`) and the optional `llm` dependency group
if you're running the drafter:

```
$ echo 'DSIRE_API_KEY=your api key' >> .env       # required for step 1
$ echo 'ANTHROPIC_API_KEY=your api key' >> .env    # step 2, --provider anthropic (default)
$ echo 'GOOGLE_API_KEY=your api key' >> .env       # step 2, --provider gemini
$ uv pip install -e ".[llm]"                       # step 2 only
```

(`uv pip install` adds the `llm` extra's packages to the existing
`.venv` without touching anything else already installed. `uv sync
--extra llm` looks equivalent but isn't — with no other extras named it
prunes any package not in that extra, e.g. it'll uninstall the `dev`
group's flake8/openpyxl/tabulate. Use `uv sync --extra llm --extra dev`
if you want `uv sync`'s exact-match behavior instead.)

- DSIRE key: request one from DSIRE (contact dsire-admin@ncsu.edu,
  see https://dsireusa.org/dsire-api/) — an annual-fee subscription,
  not self-serve.
- Anthropic key: https://console.anthropic.com/settings/keys
- Google AI Studio key: https://aistudio.google.com/apikey

Commands below are shown as `uv run python ...` rather than plain
`python ...` — this project uses `uv` (`uv.lock` at the repo root), and
`uv run` always resolves to this project's `.venv` regardless of
whether you've activated it in your current shell, so it won't
silently fall back to a different Python that's missing these
dependencies. If your shell already has `.venv` activated (check with
`which python3`), plain `python ...` works identically.

## 1. Check DSIRE for changes

```
cd scout/supporting_data/sub_fed/dsire
uv run python dsire_incentive_checker.py
```

Queries DSIRE's `/programs` endpoint for **Financial Incentive**
programs that were updated or newly expired since `incentives.csv` was
last modified in git, nationwide by default (DSIRE queries aren't
per-call billed, so there's no cost reason to narrow the state scope —
and narrowing it would hide states `incentives.csv` has zero coverage
for at all, which is exactly the kind of gap this tool should surface).
That default includes DC, DSIRE's federal-only `US` pseudo-state, and
US territories — whether those belong in `incentives.csv` is an open
question, deliberately left unfiltered here rather than decided by this
script. Two narrower options once that's settled: `--states FIFTY`
(just the 50 US states, via DSIRE's own `/states` data) or
`--states TRACKED` (only the states already present in `incentives.csv`
— useful if you specifically want a delta against existing rows rather
than a full sweep). `--states CA NY` filters to an explicit list;
`--since` is also overridable.

Results are filtered again against a keyword allowlist derived from
Scout's own tracked tech(s)/end use(s) vocabulary (heat pumps, central
AC, water heaters, furnaces, envelope measures, ...) — DSIRE's
Financial Incentive category skews heavily toward solar/wind/biomass/EV
programs that `incentives.csv` doesn't track, and this cuts that
majority out. Pass `--include-unrelated-tech` to see everything DSIRE
returned instead. The filter is deliberately biased toward false
positives over false negatives (a program with no DSIRE technology tag
at all is kept, not dropped), so expect to skim past a few
still-irrelevant rows by eye.

Nationwide, `state` also comes back as territory/federal codes DSIRE
uses that aren't 2-letter US states (seen so far: `GU` Guam, `VI` U.S.
Virgin Islands, `US` federal-level programs not tied to one state) —
whether those belong in `incentives.csv` at all is a scope call, not
something this script decides for you.

Writes `dsire_incentive_updates_<date>.csv`, with a `match_reason`
column (`updated` / `expired` / `expired+updated`) — `expired`-only
rows mean "check whether an existing `incentives.csv` row needs an end
year," not "add a new row." Run `--help` for the full flag list.

## 2. Draft candidate rows (optional, costs money)

```
uv run python dsire_incentive_drafter.py --dry-run          # preview the prompt, $0
uv run python dsire_incentive_drafter.py --limit 5           # small paid test batch
uv run python dsire_incentive_drafter.py                     # full batch, defaults to the latest staging file
uv run python dsire_incentive_drafter.py --provider gemini    # use Gemini instead of Claude
```

For each candidate program from step 1, asks an LLM to draft one
`incentives.csv`-shaped row — using a live sample of `incentives.csv`'s
own existing rows as few-shot examples, so the drafted format tracks
whatever conventions are currently in the file. Writes
`dsire_incentive_drafts_<date>.csv`: the drafted columns (exact
`incentives.csv` headers, so they can be copy-pasted directly), plus
`dsire_id`/`source_url` for traceability and `llm_confidence`/
`llm_open_questions` for triage.

**Read `llm_confidence` and `llm_open_questions` before trusting a
drafted value** — especially `performance level`, `rebate amount`, and
`applicable fraction`, which usually require judgment the DSIRE text
doesn't fully spell out (DSIRE gives you eligibility text; Scout needs
a specific performance threshold, a stacking assumption, an
`applicable fraction` with a justifying note — those are analyst
judgment calls, and the model is instructed to leave a field blank and
explain rather than invent a number, but it can still misread ambiguous
source text). "High confidence" means "worth a quick read," not "safe
to paste unchecked."

Runs `--limit N`-many paid API calls, one per candidate row — costs
real money and prints an estimated `$` total at the end (token-based,
from each response's usage). Use `--dry-run` first to sanity-check the
prompt, then `--limit` for a small test batch before running the full
file. `--resume` (pointed at an existing `--output` file) skips rows
already drafted, so an interrupted run doesn't re-pay for what it
already finished.

`--provider gemini`'s default model/pricing are best-effort — Gemini's
model lineup moves faster than this script's pricing table can track.
This has already bitten once: the original default, `gemini-2.5-flash`,
was retired for new users within months of being set as the default
here. If `--model` 404s, Google's error message names the current
replacement directly (e.g. `"...no longer available to new users.
Please update your code to use models/gemini-3.6-flash"`) — pass that
via `--model`, and update `DEFAULT_MODELS`/`PRICING` in
`dsire_incentive_drafter.py` to match so the next run doesn't hit the
same wall. Check https://ai.google.dev/gemini-api/docs/pricing for that
model's current rate. The script aborts after 5 consecutive row
failures rather than burning through the whole batch on a bad model id
or expired key — `--resume` picks back up once the underlying problem
is fixed.

```
uv run python dsire_incentive_drafter.py --provider gemini --resume --output <the output file from your last run>
```

## 3. Try to resolve blank performance level/units (optional, costs money)

```
uv run python dsire_incentive_resolver.py --dry-run          # preview the prompt, $0
uv run python dsire_incentive_resolver.py --limit 5           # small paid test batch
uv run python dsire_incentive_resolver.py                     # full run over every drafts_*.csv in this dir
uv run python dsire_incentive_resolver.py --follow-pdfs        # also read PDFs linked from each source page
```

The drafter (step 2) leaves `performance level`/`performance units`
blank far more often than not — empirically, DSIRE's own program text
routinely names a standard ("ENERGY STAR certified", "CEE's highest
efficiency tier") without stating the actual number. This script
re-fetches each blank row's `source_url` directly and asks an LLM to
extract a stated numeric threshold from the primary source itself
(never to invent one), then applies a **deterministic, non-LLM**
conversion (dividing a Btu/(W·hr)-type rating — SEER/SEER2/EER/EER2/
HSPF/HSPF2 — by 3.412 to get a dimensionless COP, the same conversion
already used by hand elsewhere in `incentives.csv`) to map it into
Scout's own units.

`--follow-pdfs` also downloads and reads PDFs linked from the source
page, since rate schedules and incentive tables often live there
instead. It costs more and needs *more* scrutiny of a "resolved" row,
not less: a linked PDF can cover a different, unrelated technology than
the row is for (the model is instructed to refuse rather than guess,
but check `resolver_source_quote` anyway), and a PDF's table can be far
more granular (e.g. six capacity tiers) than any existing
`incentives.csv` row's convention — `resolver_notes` flags both cases
for a human to actually decide, since this script won't.

Writes `dsire_incentive_resolved_<date>.csv`: the same rows, with
`performance level`/`units` filled in wherever resolved (never
overwriting a value the drafter already filled in), plus
`resolver_status`/`resolver_source_quote`/`resolver_notes`/
`resolver_pdf_urls` for review. Same cost/`--resume`/`--limit`/
`--provider` conventions as the drafter.

## 4. Review and copy into incentives.csv

Open the drafts (or resolved) CSV, check each row against its
`source_url` (and `resolver_source_quote`, if you ran step 3), fix or
fill in whatever the model left blank or flagged in
`llm_open_questions`/`resolver_notes`, then copy the accepted rows'
`incentives.csv` columns into `../incentives.csv` by hand. The
`dsire_id`/`source_url`/`llm_confidence`/`llm_open_questions`/
`resolver_*` columns are for your review only — don't copy those into
`incentives.csv`.

## Notes

- The staging/drafts CSVs written here are dated, regenerable run
  artifacts (like `results/` elsewhere in this repo) — not something
  this repo currently gitignores, so decide per-run whether to commit
  them or clean them up once their rows have been triaged.
- Re-run step 1 periodically (e.g. before each `incentives.csv` review
  pass) — `--since` defaults to whatever `incentives.csv`'s git history
  says was last touched, so each run only surfaces what's new since
  last time.
