# Updating `incentives.csv` (sub-federal incentives)

This README describes how `supporting_data/sub_fed/incentives.csv` was updated in October 2026 and how to repeat the update next year. The update was done with Claude in Cowork (drafting and sourcing), Gemini (independent review), and a human reviewer (final decisions). It replaces the earlier DSIRE-API checker/drafter scripts, which were dropped (see [Why not the DSIRE API scripts](#why-not-the-dsire-api-scripts)).

## 1. What the file is and how Scout uses it

Each row modifies the AEO baseline incentive for a set of states, building types, vintages, end uses and technologies in one scenario (`scenario` column; `reference`, `optimistic`, `aggressive`, `aggressive state`, `remove`). `ecm_prep_vars.import_state_data` expands each row into one entry per combination. `ecm_prep.apply_incentives` then applies the entries to each measure and microsegment.

How Scout combines rows (as of PR #659):

- **Replacement (`modification = replace`) rows that qualify for the same microsegment are grouped** by `(program id, scope, ira, applicable fraction)`.
  - Within a group, only the **highest** qualifying incentive is used: tiers, or whole-home vs partial options of one program.
  - Across groups, incentives **add**: different programs (utility + state + federal), or different populations of one program (e.g., low- vs moderate-income tiers, which have different fractions).
  - Rows with a blank `program id` get a unique id and add as before.
- **A row qualifies** if the measure's performance meets `performance level` in `performance units`, the base and switched-to fuels match `base fuel` / `fuel type(s)`, and the year is within `start year`-`end year`.
- **The incentive value is weighted by `applicable fraction`**, the share of the state's stock or energy that the program reaches.
- **Heat-pump rows are duplicated by Scout** for the other end use (heating ↔ cooling) with a zero incentive.

### Column conventions

| Column | Convention |
|---|---|
| `base fuel` | The fuel being replaced. `electricity` = rebate only for replacing electric equipment (e.g., electric resistance to heat pump). `all` = available whatever is replaced. `all fossil` = fuel-switching rebates only. A specific fuel (e.g., `natural gas`, `distillate`) when the program names it. |
| `base fuel backup` | `no` (blank) = backup not allowed; `yes` = allowed but not required; `required` = existing fuel-fired system must stay as backup. Full-electrification measures match `no`/`yes`; dual-fuel measures match `yes`/`required`. All IRA HEEHRA (HEAR) heat-pump rows use `required` (DOE HEEHRA Program Notice 26-2). |
| `ira` | `yes` for IRA-funded (HEAR/HEEHRA) rows; lets Scout suppress them under the `no ira` option. |
| `performance level` / `units` | Residential ASHP: COP from HSPF2 (COP = HSPF2 / 0.85 / 3.412; 7.5 -> 2.59, 7.8 -> 2.69, 8.1 -> 2.79). Central AC: COP from SEER2 (COP = SEER2 / 0.967 / 3.412; 15.2 -> 4.61, 16 -> 4.85, 17 -> 5.15). GSHP COP 3.6 placeholder. HPWH UEF (3.3 default). HP dryer CEF 3.0; electric dryer CEF 2.68. Cooking 0.82 `relative savings (constant)`. Envelope: IECC 2021 R-value strings by climate zone. Commercial: `BTU out/BTU in` placeholders (heat pump 3.3, AC 4.1, GSHP 3.6, HPWH 3.3). |
| `rebate units` | Residential `$/unit` (equipment) or `$/home` (envelope). Commercial `$/kBtu/h heating`, `$/kBtu/h cooling`, or `$/kBtu/h water heating`. |
| `credit pct` | % of installed cost; if a rebate amount is also given it acts as the cap. |
| `applicable fraction` / `fraction notes` | See section 4. Always say in the notes where the fraction came from. |
| `program id` (last column) | `<state>-<program website domain>-<res|com>`, plus `-HEAR` for IRA rows (e.g., `NC-duke-energy-res`, `CO-energyoffice-colorado-res-HEAR`). Rows that are alternatives within one program (tiers, whole-home vs partial) **must** share the id. Different programs **must not**. |

### Representation rules used this cycle

- **One row per program × state × tech × end use × population.**
- **Tiers.** Add higher tiers only if their performance threshold differs in Scout units; the max rule then picks the right tier. If tiers differ only in a metric Scout does not check (e.g., heat-pump tiers defined by SEER2, while Scout checks heating COP), keep only the lowest tier. Otherwise every unit would get the top tier.
- **Conversion bonuses and product-type rows** (e.g., "electric furnace -> heat pump conversion", "mini-split") were not added. They would also apply to like-for-like heat pump replacements.
- **Unit conversions.**
  - Residential `$/ton`: × 3 tons.
  - Commercial `$/ton`: ÷ 12 to give `$/kBtu/h`.
  - Commercial per-unit HVAC: ÷ 60 kBtu/h (5-ton unit).
  - Commercial per-unit HPWH: ÷ 15 kBtu/h.
  - Commercial size classes: use the < 65 kBtu/h (≤ 5.4 ton) class, lowest tier.
- **Not representable** (no row; record why): per-kWh, per-kW or per-MMBtu performance incentives, custom programs, direct install, % of cost with no per-measure amount, financing, tax exemptions.
- **Programs fully reserved or waitlisted** but expected to continue (e.g., TECH Clean California) are kept with a flag.

## 2. Inputs to gather

| Input | Source | Used for |
|---|---|---|
| Current `incentives.csv` | repo | starting point |
| DSIRE program inventory | full dump of DSIRE financial-incentive programs (all states) with program text, incentive amounts, website URL, last-updated and end dates. This cycle: `dsire_incentive_updates_2026-10-21_full_raw_json.csv` (2,988 parameter-set rows / 1,430 programs; strip the `-N` suffix from `dsire_id` to get the program id) plus `dsire_programs_changed_or_expiring_since_<last update>.csv` | finding programs; first-pass amounts |
| EIA-861 "Sales to Ultimate Customers" (latest year) | eia.gov (`Sales_Ult_Cust_<year>.xlsx`) | utility shares of state residential and commercial electricity sales |
| EIA-176 company-level residential gas volumes | EIA natural gas annual respondent query (export as CSV) | fractions for gas-utility rows |
| DOE LEAD tool county/tract files (AMI, SMI) | DOE LEAD (`<ST> AMI Counties <year>.csv`) | income-tier fractions (e.g., HEAR <80% / 80-150% AMI) |
| Scout tech names and cost units | `supporting_data/stock_energy_tech_data/cpl_res_com_cz.gz`, `ecm_prep_vars.py` | valid `tech(s)` names and rebate units |
| Program websites | utility / administrator pages, rebate forms, tech sheets | filling and verifying amounts and efficiency thresholds |

## 3. Process

Work in a Cowork session linked to the computer, with the `sub_fed/dsire/<cycle>/` working folder connected. Keep the scripts that build the file in that folder so each step can be re-run end to end. `with_cowork/scripts_2026/` holds this cycle's scripts as templates.

### Step 1: Update and expire existing rows
1. **Compare.** Match the DSIRE "changed or expiring since the last update" list against the existing rows by program name, state and website.
2. **Update.** Change amounts, end years and eligibility where the program changed, checking the program website.
3. **Remove or mark.** Take out programs that ended, plus federal rows the AEO baseline already handles (e.g., the 25C rows were removed in 2026 because 25C ended and AEO 2026 already excludes it).
4. **Log.** Record every change in a changelog column with the source.

### Step 2: Coverage sweep (new programs)
Coverage target, by state:
- **Residential:** every utility with ≥ 10% of the state's residential electricity sales (EIA-861, bundled + delivery), plus statewide programs (HEAR/HEEHRA, state energy offices, statewide administrators such as Mass Save, Energy Trust, Efficiency Maine, Focus on Energy, Hawaii Energy).
- **Commercial:** every utility or administrator with ≥ 10% of the state's commercial sales, for four Scout techs: `rooftop_ASHP-heat`, `rooftop_AC`, `comm_GSHP-heat`, `HP water heater`.

Work in regional batches: Northeast; Mid-Atlantic/Southeast; Midwest; South Central; West. For each batch:

1. **Build a dossier from DSIRE.**
   - List the ≥ 10% utilities per state from EIA-861.
   - Match them to DSIRE programs by name or administrator (`scripts_2026/comext2.py` writes `dossier_<region>.txt` with each program's full amount text).
   - Search the dump directly for statewide administrators, which keyword matching misses.
2. **Use DSIRE amounts first, then fill gaps from the program website** wherever DSIRE is missing an amount, says "see website" or "varies", is clearly stale, or lacks efficiency requirements (it almost always does).
   - Prefer current-year rebate forms, tech sheets and incentive catalogs.
   - Record the source (`DSIRE <id>` or `program website`) in the description, and caveats in a review-flag column.
3. **Draft rows** with a helper (`scripts_2026/rows_lib.py`) that applies the conventions in section 1 and writes both the CSV and a review workbook.
4. **Parallelize if useful.** The 2026 commercial sweep used one Claude sub-agent per region with a written brief: sources in order (DSIRE dump, then website), lowest-tier rule, unit conversions, and a "not representable" list. The main session then checked the high-share gaps in the browser and fixed anything inconsistent.

### Step 3: Applicable fractions
- **Utility rows:** the utility's share of the state's residential or commercial retail sales in EIA-861 (bundled + delivery). Combine utilities that share one program (e.g., Energy Trust = PGE + PacifiCorp).
  - **Texas ERCOT:** EIA-861 reports retail providers, not delivery utilities, so delivery-utility shares can't be computed this way. Their programs are performance-based anyway.
- **Gas-utility rows:** the company's share of the state's residential gas volume in EIA-176.
- **Income-limited programs:** DOE LEAD energy-expenditure shares for the eligible AMI/SMI band (single family where relevant).
- **Statewide programs:** 1 (or the eligible population share).
- **Write the source** in `fraction notes`.

### Step 4: Program ids, tiers, overlaps
1. **Assign `program id`.** `scripts_2026/p6_final.py` derives it from state + website domain + res/com, with `-HEAR` for IRA rows; adjust by hand if two programs share a domain.
2. **Check overlaps.** Look for groups where more than one row can apply to the same segment: same program id, fraction, tech and end use, with overlapping base fuel, building type, vintage and years. Each group must be a genuine set of alternatives within one program.
3. **Set backup on HEAR heat-pump rows** (`ira = yes`, `ASHP`, base fuel `all`/`all fossil`) to `required`.

### Step 5: Review rounds
1. **Reviewer comments.** Share the review workbook: data sheet, a "Reply to comments" sheet answering each comment, and a "Removed rows" sheet with reasons. Re-run the build scripts after each round so fixes accumulate.
2. **Independent AI review.** In 2026, Gemini reviewed the merged file and proposed corrections and additions.
   - Compare it programmatically (`scripts_2026/gcmp.py`, `progcmp.py`): row-level differences, program coverage, and spot checks of amounts and fractions against program sites and EIA-861.
   - Adopt only verified fixes.
   - Lessons from 2026:
     - The reviewer used outdated EIA-861 vintages.
     - It inverted base fuels (electric-replacement rebates tagged `all fossil`).
     - It used "up to" amounts as rebates.
     - It restored tiers that only work with code changes.
   - It also caught real issues: NM HEAR fractions, missing Mass Save and PSE&G commercial rows, and inherited overlaps.
3. **Coverage audit against DSIRE.** Record which rows are fully in DSIRE vs needed the website (`scripts_2026/cov.py`).

### Step 6: Validate and replace `incentives.csv`
1. **Parse.** Parse the final file with `ecm_prep_vars` for every scenario (`scripts_2026/parse_test.py`). Every entry should have 21 elements with the program id at index 10.
2. **Spot-check.** Replicate the grouping on test cases: a tiered utility program, a whole-home vs partial program, an income-tiered HEAR program with and without backup, and a gas furnace tier.
3. **Commit.** Copy the final CSV to `supporting_data/sub_fed/incentives.csv`. Keep the dated review workbook alongside it for the record.

## 4. Practical notes for the web-checking step

**Pages that only render in a browser.** Use Cowork's built-in browser when a page needs JavaScript or hides its tables. The 2026 cases:
- ComEd's incentive tables (read by walking the page's hidden component tree)
- Xcel's "Rebate Summary Sheet" PDFs (Salesforce links blocked to plain fetching)
- Duke's Smart $aver rebate table
- PDF tech sheets with ambiguous layouts

**Not reachable without credentials or verification**; record these as gaps rather than guessing:
- Evergy (human-verification wall)
- Entergy Mississippi business rebates (login)
- DTE (rates only in an Excel calculator)
- OG&E (login)
- PSO (amounts set by distributors)

**Usually not representable:**
- Texas delivery utilities, Entergy Arkansas, Cleco, LADWP (per-kWh / per-kW)
- Ohio IOUs (no rebates since HB6)
- Con Ed commercial clean heat (per MMBtu)

**DSIRE limitations seen in 2026:**
- Program records last updated 1-2 years ago.
- "See website" or "varies" instead of amounts.
- Ranges with no tier mapping.
- Almost never efficiency thresholds or performance units.

Treat DSIRE as the program inventory and a first-pass amount, not the final source.

**Program status:** check that programs are active in the current year (end dates, "fully reserved", "program concluded", new program-year sheets).

## 5. Why not the DSIRE API scripts

The first approach in PR #659 had two parts. A checker queried the DSIRE Programs API for programs changed since the last update. A drafter then asked an LLM to turn each record into an `incentives.csv` row. It was dropped because:

- **Missing core fields.** The API rarely contains the fields Scout needs: performance level and units, tier thresholds, rebate units. Records usually point to an external standard or the program website instead of giving the numbers.
- **Unusable drafts.** The rows needed so much follow-up that drafting from them saved little.
- **Incomplete coverage.** The changed-since list misses large programs that DSIRE has not touched recently, so it can't serve as a coverage check.
- **Stale amounts.** Many records are out of date relative to program websites.

The DSIRE data is still used, as a full program inventory and first-pass amount source (Step 2). The sourcing, fractions and representation decisions are done in the Cowork workflow above, with a human reviewer and an independent AI cross-check.

## 6. Checklist for next year
- [ ] Download the latest EIA-861, EIA-176 and (if updated) DOE LEAD data
- [ ] Obtain a full DSIRE program dump and the changed/expired list since the last update
- [ ] Step 1: update/expire existing rows
- [ ] Step 2: regional residential and commercial sweeps (DSIRE first, then websites)
- [ ] Step 3: fractions with sources in `fraction notes`
- [ ] Step 4: program ids, tier check, overlap check, HEAR backup `required`
- [ ] Step 5: reviewer comments, independent AI review, coverage audit
- [ ] Step 6: parse/grouping validation, then replace `incentives.csv`

## 7. Files from the 2026 cycle (`sub_fed/dsire/with_cowork/`)

**Final:**
- `incentives_updated_2026-10-23.csv` (identical to the committed `incentives.csv`)
- `incentives_updated_2026-10-23.xlsx` (data with per-row change notes, "Reply to comments", "Removed rows")

**Batches of new rows:**
- `incentives_new_rows_2026-10-21.csv`
- `incentives_new_rows_2026-10-22_northeast.csv`
- `incentives_new_rows_2026-10-22_full_pipeline.csv`
- `incentives_new_rows_2026-10-22_commercial.csv`

**Audits and comparisons:**
- `dsire_coverage_audit_2026-10-22.csv`
- `gemini_comparison_2026-10-23_*.csv`
- PR notes: `pr659_review_comment_draft.md`, `pr659_reply_2026-10-23.md`

**Inputs:**
- `Sales_Ult_Cust_2024.xlsx`
- `export.csv` (EIA-176)
- LEAD `* AMI Counties 2022.csv` files
- DSIRE dumps
- `from_gemini/` (Gemini review files)

**Scripts:**
- `scripts_2026/`, plus the regional DSIRE dossiers.
- The scripts are templates: they hard-code this cycle's row numbers and file names.
- Run order: `fix1.py`, `reply.py`, `p2.py`, `p3_ne.py`, `p4_fp.py`, `p5_com.py`, `p6_final.py`, then `parse_test.py`.
