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
- There is no Brk. (breakthrough) tier; those rows are skipped.

**Only 48 of the ~100 Scout technology tokens used in `meas_in` have an
authored rule** (see `MATCH_RULES`); the rest print a warning and are left
out of the crosswalk entirely. Add a rule to cover more.

Rows come out flagged `needs_review = True` (and no BTB id filled in) when:
- No BTB row matched the rule (`match_confidence = none`), or
- More than one BTB row matched (`match_confidence = ambiguous` -- the
  `notes` column lists every candidate found).

Re-running this script only *adds* missing `(technology, tier)` rows --
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

**Cost** is evaluated from BTB's retail-price regression at the tier's
performance (as in the "BTB Key Costs" sheet that the existing BTB-sourced
`meas_in` costs came from):

```
retail    = coef1_mid * metric1_typical + coef2_mid * performance + intercept_mid
installed = retail * installation_multiplier + installation_adder   # new / retrofit
```

This needs the multiplier/adder columns, which only the residential BTB CSV
has, and the performance to be regression metric 2. Otherwise (commercial,
or other metric layouts) the cost falls back to BTB's precomputed Mid
installed cost at Typical performance, and the `BTB Diff` `notes` column says
so. Where the performance kept for Min. Efficiency/ESTAR cannot be converted
to the BTB metric, cost is left alone (`(skipped)`).

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
