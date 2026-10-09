# Populating cost/performance/lifetime data from BTB

`bss_meas_v2.xlsx` (sheet `meas_in`) is the curated spreadsheet that feeds
`meas_pkg_gen.py` (repo root) to generate Scout measure JSONs. Many rows
cite "Buildings Annual Technology Baseline. NREL, forthcoming" as the
source for their Energy Performance / Installed Cost / Lifetime values --
that dataset has since been published on OpenEI as the **2024 Buildings
Technology Baseline (BTB)** (https://data.openei.org/submissions/8342).
The three scripts here pull directly from the published BTB CSVs instead
of hand-transcribing values from a Google Sheet.

**Scope:** only technologies BTB explicitly covers with clear cost/
performance data -- HVAC, Water Heating, Lighting, Refrigeration, and
Cooking, both residential and commercial. Envelope (windows, walls,
infiltration) and electronics/MELs (laptops, TVs, smart speakers, etc.)
have no BTB coverage and are not touched by this workflow.

**Nothing here ever overwrites `bss_meas_v2.xlsx` directly.** The pipeline
ends in a separate reviewable file with a diff sheet, so a human can
sanity-check every proposed change before merging any of it back into the
curated original by hand.

## 1. Download the BTB data

```
cd scout/supporting_data/btb
python download_btb_data.py
```

Downloads the residential and commercial CSVs (from OpenEI submission
8342) to `raw/btb_residential.csv` and `raw/btb_commercial.csv`. That
directory is git-ignored (large, re-downloadable). Pass `--overwrite` to
re-download; otherwise existing files are left alone.

## 2. Build (and review) the technology crosswalk

```
python build_tech_crosswalk.py
```

Matches every Scout technology token used in `meas_in`'s `Baseline
Technology`/`Switched to Technology` columns against BTB's Display
Name/Component/Technology-Measure/Fuel Type text, using the rule table in
`MATCH_RULES` at the top of the script. Writes/updates `tech_crosswalk.csv`
(checked into git -- this is meant to be hand-curated over time, not
regenerated from scratch each run).

Each matched technology is expanded into the 4 `meas_in` efficiency tiers
(Ref. Case, Min. Efficiency, ESTAR, Best) using a default performance
"bound" (see `TIER_DEFAULTS`) -- **this default is a starting point for
review, not a validated result.** The bound sets which performance level is
used, and cost is then evaluated at that performance:

| Tier | `bound` | Performance | Cost |
|---|---|---|---|
| Ref. Case | Typical | BTB Typical | BTB cost regression at BTB Typical |
| Min. Efficiency, ESTAR | Existing | Left as-is in `meas_in` (set by a standard / ENERGY STAR) | BTB cost regression at the `meas_in` performance |
| Best | High | BTB High | BTB cost regression at BTB High |

All tiers use BTB's 2023 Reference values (2023 values are the same across
scenarios for nearly all technologies). Known limits:

- All 4 tiers currently draw from the *same* matched BTB Technology ID.
  Where BTB has a genuinely distinct higher-efficiency product (e.g. a
  condensing vs. non-condensing gas boiler), this script does not
  auto-detect and switch technology -- those cases surface as
  `needs_review` (ambiguous, multiple candidates) instead, or may need a
  manual crosswalk row pointing a specific tier at a different Technology ID.
- Breakthrough ("Brk.") measures are not sourced from BTB and are skipped.

**Only 48 of the ~100 Scout technology tokens used in `meas_in` have an
authored rule** (see `MATCH_RULES`); the rest print a warning and are left
out of the crosswalk entirely. Add a rule to cover more.

Rows come out flagged `needs_review = True` (and no BTB id filled in) when:
- No BTB row matched the rule (`match_confidence = none`), or
- More than one BTB row matched (`match_confidence = ambiguous` -- the
  `notes` column lists every candidate found).

A token used by both residential and commercial measures (e.g. `HPWH`) has
a rule, and so crosswalk rows, for each sector; the populate step picks the
entry matching the `(R)`/`(C)` prefix of the measure's Name. Tokens that
only have the other sector's entry are left alone (except those deliberately
crosswalked across sectors, `CROSS_SECTOR_TECHS`).

Re-running this script only *adds* missing `(technology, sector, tier)` rows --
existing rows (including ones you've hand-corrected) are left alone. Pass
`--refresh` to recompute everything from scratch (discards manual edits).

## 3. Propose values and review the diff

```
python populate_meas_in_from_btb.py
```

For every `meas_in` row and every technology in it that has a
non-`needs_review` crosswalk entry matching that row's inferred tier
(parsed from the `Name` column), this looks up the matching BTB row
(technology + projection year + scenario) and computes what the Energy
Performance / Installed Cost / Lifetime values would be, converting units
where needed (see `unit_conversions.py` -- anything without a known
conversion rule is silently skipped here, not guessed at).

**Cost** starts from BTB's precomputed Mid installed cost, which is at
Typical performance, and is moved to the tier's performance using BTB's
retail-price regression (see "Installed costs" in `btb_doc.pdf`):

```
retail change = coef2_mid * (performance - typical) * unit_multiplier
installed     = installed_typical + installation_multiplier * retail change
```

This is the same as evaluating the full regression and applying the
installation multiplier/adder (the method of the "BTB Key Costs" sheet), but
always agrees with BTB at Typical. Per the documentation a technology uses
either a multiplier or an adder (an adder is a multiplier of 1 for this
purpose). The residential CSV gives the multiplier; the commercial CSV does
not, so it is recovered from each row's Low/Mid/High retail and installed
prices (this reproduces the sheet's commercial multipliers). Only regression
metric 2 is treated as the performance metric.

**Row guards.** Every row is considered, except breakthrough ("Brk.")
measures, which are not sourced from BTB. An installed cost is proposed only
when:
- the row's `Cost Units` are `2023$/unit` or `2023$/kBtu/h` of heating,
  cooling or water heating capacity, or the same in 2022$ (see below);
- its Cost Source Notes describe no adder or scaling (dual-fuel furnace,
  tank removal, breakthrough half-cost, "switched to" costs, ...);
- the cost is not a `$0` placeholder (often a cost deliberately shared with
  a paired technology).

Per-kBtu/h costs are the whole-unit cost divided by BTB's Typical capacity
in kBtu/h (the "div capacity" columns of the BTB Key Costs sheet).
2022$ rows are only replaced when the cell holds a single cost, and
their `Cost Units` are then changed to 2023$ (BTB costs are $2023).
Costs that can't be evaluated at the tier's performance (e.g. kept
performance that can't be converted to the BTB metric) are skipped. Every
skip is logged in `BTB Diff` with its reason.

A cell holding one bare value (e.g. `2.3`, or `new: X; existing: Y` with no
technology name) is only updated for the row's single Switched-to
technology (or the Baseline technology if there is no switch), never for
the other technologies in the row.

Writes `bss_meas_v2_btb_proposed.xlsx` (git-ignored, not meant to be
committed) containing:
- A copy of `meas_in` with proposed values substituted in for just the
  resolved technology/column combinations -- everything else in a shared
  cell (other technologies, formatting, unrelated columns) is left
  byte-for-byte as it was.
- A `BTB Diff` sheet: one row per changed cell, with the old value, the
  proposed new value, and the matched BTB technology/scenario/year, so
  you can judge each change before copying it into the real file.

**Known gotcha:** a cost of exactly `$0` for a technology in the original
sheet usually means its cost was deliberately zeroed out because it
shares physical equipment with a paired heating/cooling technology in the
same row (e.g. a heat pump's cost entered once under "heat" and zeroed
under "cool" to avoid double-counting). The script recognizes this pattern
and leaves those cells alone (logged in the diff as `(skipped)` with a
note) rather than reintroducing a double-count -- but double-check any
row where this fires, since it's a heuristic, not a certainty.

## After reviewing

There is currently no automated "apply" step -- copy whichever proposed
values you accept from `bss_meas_v2_btb_proposed.xlsx` into
`bss_meas_v2.xlsx` by hand (and update the corresponding Source
Notes/Details columns to cite BTB, e.g. title "2024 Buildings Technology
Baseline", author Guidehouse/NREL, year 2024/2025, url
https://data.openei.org/submissions/8342), then re-export the `meas_in`
sheet to `ecm_definitions/meas_pkg_gen_io/inputs/meas_in.csv` for
`meas_pkg_gen.py` to pick up.
