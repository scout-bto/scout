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
  cooling, water heating or cooking capacity, or the same in 2022$ (see
  below);
- the cost is not a `$0` placeholder (a cost deliberately shared with a
  paired technology, or an airflow system anchored on the heating/cooling
  cost), unless the crosswalk turns a zero-cost add-on into a full service
  measure (see "Measure-level rows");
- the Cost Source Notes describe nothing that can't be rebuilt from BTB.

Per-kBtu/h costs are the whole-unit cost divided by a capacity in kBtu/h:
- *Heating, cooling, water heating*: BTB's Typical capacity (the "div
  capacity" columns of the BTB Key Costs sheet).
- *Cooking*: BTB's ranges have no capacity, so the range's Combined Idle
  Energy Rate is used (10.35 kBtu/h for the gas range; 1.4 kW = 4.78 kBtu/h
  for the electric range).
- *Refrigeration*: BTB describes the units by volume, area or ice output, so
  the capacities come from the EIA report "Updated Buildings Sector Appliance
  and Equipment Costs and Efficiencies", Appendix C (2022 typical cooling
  capacity), in `BTB_UNIT_CAPACITY_KBTUH`. Where EIA's typical unit is the
  same size as BTB's the EIA capacity is used as is (reach-in freezer 49 ft3,
  4.34 kBtu/h; reach-in refrigerator 46 ft3, 2.349; beverage merchandiser
  27 ft3, 4.7; vending machine 35 ft3, 1.81; ice machine 700 lb/day, 4.58).
  Two cases don't correspond and are assumptions: the walk-in freezer and
  cooler are 112 sq ft in BTB against EIA's 161 sq ft (23.5 kBtu/h) and 240
  sq ft (41.0 kBtu/h), so their capacities are scaled by floor area (16.35
  and 19.14 kBtu/h); and BTB's display case (51 ft2 of display area) is
  paired with EIA's 12 ft case (11.85 kBtu/h) without a size check.

The zero-cost reference-case refrigeration add-on, which covers eight
technologies in one cost cell, becomes a full service measure with a cost
entry for each technology.

Costs that can't be evaluated at the tier's performance (e.g. kept
performance that can't be converted to the BTB metric) are skipped. Every
skip is logged in `BTB Diff` with its reason.

**Composite costs** are rebuilt from BTB pieces, using the row's Cost Source
Notes:
- *Dual-fuel heat pump* ("also add retail cost of typical gas/oil furnace"):
  new construction = the heat pump plus BTB's typical gas (Furnace Gas-fired)
  or oil (Furnace Oil-Fired) furnace; existing construction = the heat pump
  alone, as the existing backup unit is kept.
- *Oil-tank removal*: existing construction includes $1,030 (2023$) for tank
  removal when the heat pump fully replaces an oil or propane system. This
  comes from the existing notes (2015 EIA report), not BTB. It is not
  counted in the dual-fuel rows above, where the backup furnace is kept and
  so nothing is removed.
- *Electric boiler rows* ("switched to elec boiler"): the baseline boiler's
  cost, performance and lifetime entries describe the electric boiler
  switched to, so the cost comes from BTB's electric boiler and the
  performance and lifetime of those entries are left alone.

**Overrides** (optional crosswalk columns):
- `cost_at = Typical` evaluates the cost at BTB's Typical performance
  whatever the tier (used for the heat pump dryer, whose BTB cost regression
  falls as efficiency rises).
- `keep_lifetime = yes` leaves the existing lifetime alone (used for the
  electric dryer, beverage merchandisers and ice machines, whose BTB
  lifetimes of 22.3, 31 and 21 years are judged implausible and flagged as
  potential BTB issues).
- `lifetime_value` uses a given lifetime instead of BTB's (used for
  induction ranges: 11 years like the electric range, instead of BTB's 17).

**Other rules.** Commercial rows that represent a residential-type furnace
in a commercial setting (their cost notes say "residential furnaces") use the
residential furnace's BTB entry for `oil_furnace` and `gas_furnace`.

**Measure edits.** `MEASURE_EDITS` in `populate_meas_in_from_btb.py` lists
edits to specific measures that came out of review and are not derived from
BTB: the best heat pump dryer measures lose "120V" from their Name and
Description (no 120V products are on the market), and the fuel switch
measure gets `240V circuit: true` for its Electrical Upgrade Costs. They are
applied to the proposed workbook and logged in `BTB Diff`. Renaming a
measure also means regenerating its file under `ecm_definitions/` and
updating the exported `meas_in.csv`.

**Measure-level rows.** Measures whose baseline technology is the
placeholder `all` have no technology to match on, so the crosswalk has rows
keyed by the measure's exact `Name` (the residential gas water heater
measures and the commercial gas/electric range measures). A row with
`measure_type = full service` also changes a zero-cost reference-case
add-on to a full service measure carrying the BTB cost.

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

## Known issues in the BTB data

A running list of places where the BTB data look wrong and the pipeline
departs from them, to be sent to the BTB team for review once the work is
done (see `btb_doc.pdf` for the authors; dataset:
data.openei.org/submissions/8342). Each is marked where it applies: a note on
the `tech_crosswalk.csv` rows, and a note in the `BTB Diff` sheet on the
affected cell. Add new issues here as they come up.

Flagged in review (decision taken):

| BTB entry | What is wrong | What we do |
|---|---|---|
| Clothes Dryer Electric (residential ID 14) | Lifetime 22.33 years, implausibly long | Keep the existing 13 (`keep_lifetime = yes`) |
| Clothes Dryer Heat Pump (residential ID 17) | The CEF cost coefficient is negative (-4.67), so cost falls as efficiency rises: Typical (CEF 5.45) is $1,595 but BTB's High (CEF 11) would be $1,569 | Use the Typical cost for every tier (`cost_at = Typical`) |
| Beverage Merchandisers - Standard (commercial ID 30) | Lifetime 31 years; the existing value is 10, and EIA's Appendix C gives 10 | Keep the existing 10 (`keep_lifetime = yes`) |
| Commercial Ice Machine Standard (commercial ID 18) | Lifetime 21 years; the existing value is 10, and EIA's Appendix C gives 8.5 | Keep the existing 10 (`keep_lifetime = yes`) |
| Cooking Range Electric / Gas / Induction (residential IDs 27 / 28 / 29) | Lifetimes 11 / 15 / 17 years. Gas matches EIA (15) but electric differs from EIA (17), and induction lasting longer than an electric resistance range is not credible | Use 11 for electric (BTB's value) and for induction (`lifetime_value = 11`) |

Observed while building the pipeline, not yet reviewed:

| BTB entry | Observation |
|---|---|
| Boiler Oil (residential ID 8) | The precomputed retail price ($3,767) differs from the price its own regression gives ($3,982); installed costs follow the former |
| Commercial Ground Source Heat Pump (commercial ID 10) | Its Notes say "There is no available efficiency data" and "Typical retail price refers to the total installed cost"; only Heating COP is given |

## After reviewing

There is currently no automated "apply" step -- copy whichever proposed
values you accept from `bss_meas_v2_btb_proposed.xlsx` into
`bss_meas_v2.xlsx` by hand (and update the corresponding Source
Notes/Details columns to cite BTB, e.g. title "2024 Buildings Technology
Baseline", author Guidehouse/NREL, year 2024/2025, url
https://data.openei.org/submissions/8342), then re-export the `meas_in`
sheet to `ecm_definitions/meas_pkg_gen_io/inputs/meas_in.csv` for
`meas_pkg_gen.py` to pick up.
