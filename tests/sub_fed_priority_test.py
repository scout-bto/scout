#!/usr/bin/env python3

"""Tests for layering scenario incentive/rate rows on the reference case without overlap."""

import types
import pandas as pd
import pytest
from scout import ecm_prep_vars as epv
from scout.config import FilePaths as fp
from scout.ecm_prep_vars import reconcile_exploded_subfed as reconcile

START, END, FRAC = -3, -2, -1


def inc(start, end, frac=1, rebate=4000, state="CA", bldg="single family home", eu="heating",
        tech="ASHP", mod="replace", scope="non-federal", ira=False, credit=False, increase=0,
        perf_lev=2.69, units="COP", rebate_units="$/unit", pid="p1", backup="no"):
    """Exploded incentives row (21 fields; the program id is the 11th)."""
    return [state, bldg, "existing", eu, tech, "electricity", "natural gas", backup, mod, scope,
            pid, ira, increase, perf_lev, units, credit, rebate, rebate_units, start, end, frac]


def rate(start, end, frac=1, vol_rel=0.2, vol_abs=False, state="CA", bldg="single family home"):
    """Exploded low volume rate row (12 fields)."""
    return [state, bldg, "existing", "heating", "ASHP", "electricity", vol_abs, vol_rel, 0,
            start, end, frac]


def span(row, lo=2020, hi=2050):
    """First and last year of a row, with blank bounds replaced by lo and hi."""
    return (row[START] or lo, row[END] or hi)


def max_coverage(rows, lo=2020, hi=2050):
    """Largest summed applicable fraction in any year across rows."""
    return max(sum(r[FRAC] for r in rows if span(r, lo, hi)[0] <= y <= span(r, lo, hi)[1])
               for y in range(lo, hi + 1))


def test_empty_inputs():
    # With either side empty there is nothing to layer, so the other side comes back as is
    ref, scn = [inc(2024, 2025)], [inc(2026, 2030)]
    assert reconcile([], scn, "incentives") == scn
    assert reconcile(ref, [], "incentives") == ref
    assert reconcile([], [], "low_volume_rate") == []


def test_reference_rows_returned_untouched():
    ref = [inc(2024, 2031, 0.446), inc(2024, 2031, 0.3, rebate=900)]
    res = reconcile(ref, [inc(2025, 2050, 0.446)], "incentives")
    # The reference rows come first, unmodified
    assert res[:2] == ref


def test_ref_expires_and_scenario_extends():
    # The scenario row is trimmed to the years after the reference row ends
    res = reconcile([inc(2024, 2031, 0.446)], [inc(2025, 2050, 0.446)], "incentives")
    assert len(res) == 2
    assert span(res[1]) == (2032, 2050)
    assert res[1][FRAC] == 0.446


def test_scenario_starting_before_ref_keeps_pre_ref_years():
    # A reference row in the middle of the scenario's years splits it into a before and after piece
    res = reconcile([inc(2028, 2031)], [inc(2025, 2050)], "incentives")
    assert [span(r) for r in res[1:]] == [(2025, 2027), (2032, 2050)]


def test_scenario_fully_inside_ref_dropped():
    # A scenario row fully within an equivalent reference row adds nothing and is removed
    ref = [inc(2024, 2031, 0.28, rebate=2000)]
    assert reconcile(ref, [inc(2024, 2029, 0.28, rebate=2000)], "incentives") == ref


def test_scenario_ending_before_ref_starts_kept():
    # No shared years with the reference: the original row object is kept untouched
    scn = inc(2024, 2026)
    res = reconcile([inc(2030, 2035)], [scn], "incentives")
    assert res[1] is scn


def test_open_ended_reference_covers_scenario():
    ref = [inc(2026, False)]
    # Scenario fully covered by an open-ended reference row is dropped
    assert reconcile(ref, [inc(2030, 2040)], "incentives") == ref
    # Scenario with an earlier start keeps only the years before the reference starts
    res = reconcile(ref, [inc(2024, False)], "incentives")
    assert [(r[START], r[END]) for r in res[1:]] == [(2024, 2025)]


def test_open_ended_scenario_blanks_preserved():
    # A scenario row with no start or end year keeps those ends open after being split
    res = reconcile([inc(2024, 2031)], [inc(False, False)], "incentives")
    assert [(r[START], r[END]) for r in res[1:]] == [(False, 2023), (2032, False)]


def test_better_tier_same_fraction_kept_lesser_tier_dropped():
    ref = [inc(2024, 2031, 0.5, rebate=4000)]
    better = inc(2024, 2031, 0.5, rebate=8000)
    worse = inc(2024, 2031, 0.5, rebate=1000)
    # A higher level for the same customers is kept in full; a lower or equal one is dropped
    assert reconcile(ref, [better], "incentives")[1:] == [better]
    assert reconcile(ref, [worse], "incentives") == ref
    assert reconcile(ref, [inc(2024, 2031, 0.5, rebate=4000)], "incentives") == ref


def test_different_perf_requirements_do_not_overwrite_each_other():
    ref = [inc(2024, 2031, 0.5, rebate=4000, perf_lev=3.0)]
    scn = inc(2024, 2031, 0.5, rebate=1000, perf_lev=2.0)
    # A different efficiency requirement is a different program, so the scenario row is kept
    assert reconcile(ref, [scn], "incentives")[1:] == [scn]


def test_statewide_scenario_stacks_on_utility_only_reference():
    # A statewide (fraction 1) program stacks on a utility-only one, so it is kept in full
    scn = inc(2024, 2050, 1.0)
    res = reconcile([inc(2024, 2031, 0.78)], [scn], "incentives")
    assert res[1:] == [scn]


def test_scenario_fraction_kept_in_full_against_multiple_reference_fractions():
    ref = [inc(2024, 2040, 0.0135, rebate=100), inc(2024, 2040, 0.4445, rebate=200)]
    scn = inc(2024, 2040, 1.0, rebate=900)
    # The reference fractions (0.0135, 0.4445) are not summed against the scenario's fraction of 1
    assert reconcile(ref, [scn], "incentives") == ref + [scn]


def test_scenario_with_later_start_against_open_ended_partial_reference():
    # A statewide scenario row starting after a partial open-ended reference row is kept in full
    scn = inc(2030, 2035, 1.0)
    assert reconcile([inc(2025, False, 0.419)], [scn], "incentives")[1:] == [scn]


def test_higher_level_statewide_supersedes_reference_statewide_in_overlap_years():
    ref = [inc(2024, 2035, 1.0, rebate=4000)]
    res = reconcile(ref, [inc(2030, 2040, 1.0, rebate=6000)], "incentives")
    # Kept for its full span at the same fraction (and the same dedup key downstream, where the
    # higher incentive in each year wins over the reference row)
    assert [(span(r), r[-5], r[FRAC]) for r in res[1:]] == [((2030, 2040), 6000, 1.0)]
    # A lower or equal level in the overlap is trimmed to the years the reference doesn't cover
    res = reconcile(ref, [inc(2030, 2040, 1.0, rebate=3000)], "incentives")
    assert [span(r) for r in res[1:]] == [(2036, 2040)]


def test_different_scope_mod_backup_do_not_overlap():
    # Rows that differ in scope (federal vs. not), modifier (replace vs. extend), or backup fuel
    # setting are different programs and are all kept
    ref = [inc(2024, 2031)]
    for scn in (inc(2024, 2031, scope="federal"),
                inc(2024, 2031, mod="extend", rebate=False, increase=0.1)):
        assert reconcile(ref, [scn], "incentives")[1:] == [scn]
    backup = inc(2024, 2031, rebate=9000)
    backup[7] = "yes"
    assert reconcile(ref, [backup], "incentives")[1:] == [backup]


def test_all_wildcard_in_reference_covers_specific_scenario():
    # A reference tech of 'all' covers a specific scenario tech
    ref = [inc(2024, 2031, tech="all")]
    assert reconcile(ref, [inc(2024, 2031, tech="ASHP")], "incentives") == ref
    # Reverse is not treated as covered (reference only covers a subset of the scenario row)
    scn = inc(2024, 2031, tech="all", rebate=9000)
    assert reconcile([inc(2024, 2031, tech="ASHP")], [scn], "incentives")[1:] == [scn]


def test_remove_and_zero_rows_pass_through():
    # Rows that remove incentives or have all-zero levels are never trimmed
    ref = [inc(2024, 2040, rebate=4000)]
    remove = inc(2030, 2035, mod="remove", rebate=False)
    zero = inc(2030, 2035, rebate=0)
    res = reconcile(ref, [remove, zero], "incentives")
    assert res[1] is remove and res[2] is zero
    # Inert reference rows add no coverage to subtract
    scn = inc(2030, 2035)
    assert reconcile([zero, remove], [scn], "incentives")[2:] == [scn]


def test_building_and_state_isolation():
    # Reference rows only affect scenario rows for the same state and building type
    ref = [inc(2024, 2040)]
    scn = [inc(2024, 2040, bldg="mobile home"), inc(2024, 2040, state="NY")]
    assert reconcile(ref, scn, "incentives")[1:] == scn


def test_incentive_programs_with_distinct_fractions_overlap_and_both_count():
    ref = [inc(2024, 2031, 0.5, rebate=100), inc(2026, 2035, 0.3, rebate=200)]
    scn = [inc(2022, 2050, 1.0, rebate=900)]
    # Incentive programs with different fractions stack, so nothing is trimmed
    assert reconcile(ref, scn, "incentives") == ref + scn


def test_rates_partial_fraction_complement_ca():
    # Rates cannot cover more than 100% of customers: a 1.0 scenario row is cut to the 0.22 left
    # after a 0.78 reference row
    res = reconcile([rate(2026, False, 0.78)], [rate(2026, False, 1.0)], "low_volume_rate")
    assert len(res) == 2 and res[1][FRAC] == pytest.approx(0.22)
    assert (res[1][START], res[1][END]) == (2026, False)


def test_rates_multiple_reference_rows_ma():
    ref = [rate(2025, False, 0.0135, vol_rel=0.2), rate(2025, False, 0.4445, vol_rel=0.2),
           rate(2025, False, 0.4787, vol_rel=False, vol_abs=0.07)]
    # Three reference fractions leave the remainder to the scenario row, never above 100% overall
    res = reconcile(ref, [rate(2030, False, 1.0, vol_rel=0.2)], "low_volume_rate")
    assert len(res) == 4 and res[3][FRAC] == pytest.approx(1 - 0.0135 - 0.4445 - 0.4787)
    assert max_coverage(res) <= 1 + 1e-9


def test_rates_scenario_before_ref_and_overwritten_by_ref():
    ref = [rate(2030, 2040, 0.5, vol_rel=0.2)]
    # Only the years outside the reference row remain for an equal-level scenario row
    res = reconcile(ref, [rate(2026, 2045, 0.5, vol_rel=0.2)], "low_volume_rate")
    assert [(r[START], r[END]) for r in res[1:]] == [(2026, 2029), (2041, 2045)]
    # A lower level over years the reference covers is removed entirely
    assert reconcile(ref, [rate(2031, 2035, 0.5, vol_rel=0.1)], "low_volume_rate") == ref


def test_rates_abs_and_rel_do_not_overwrite_each_other():
    ref = [rate(2026, 2040, 0.5, vol_rel=False, vol_abs=0.07)]
    scn = rate(2026, 2040, 0.5, vol_rel=0.2)
    # Not overwritten by the reference row; 50% of the population remains, so the row is kept
    assert reconcile(ref, [scn], "low_volume_rate")[1:] == [scn]


def test_import_state_data_dedupes_and_layers_rates(tmp_path):
    """End-to-end check through the CSV import: repeated states collapse, ref is layered on."""
    import types
    from scout.ecm_prep_vars import UsefulVars
    header = ("scenario,description,state(s),building type(s),building vintage(s),end use(s),"
              "tech(s),fuel type(s),volumetric rate reduction (absolute),"
              "volumetric rate reduction (pct reduction),added annual fixed charge,start year,"
              "end year,applicable fraction,fraction notes\n")
    rows = ("reference,r,CT,single family home,existing,heating,ASHP,electricity,,20,,2026,2030,"
            "0.5,\n"
            "aggressive,a,\"CT, CT\",single family home,existing,heating,ASHP,electricity,,20,,"
            "2026,,1,\n")
    # Write a small rates file and import it for the aggressive scenario
    path = tmp_path / "rates.csv"
    path.write_text(header + rows)
    handyfiles = types.SimpleNamespace(low_volume_rate=str(path))
    opts = types.SimpleNamespace(low_volume_rate="aggressive")
    uv = UsefulVars.__new__(UsefulVars)
    uv.import_state_data(handyfiles, ["low_volume_rate"], ["CT"], opts)
    res = uv.low_volume_rate
    # One reference row, then the scenario split into a 50% complement and a full-coverage tail
    assert [(r[START], r[END], r[FRAC]) for r in res] == [
        (2026, 2030, 0.5), (2026, 2030, 0.5), (2031, False, 1)]


def test_scenario_tiers_with_fractions_unlike_reference_are_kept_in_full():
    # Tiers whose fractions differ from every reference fraction are distinct programs
    ref = [inc(2024, 2032, 0.3177, rebate=9000, ira=True), inc(2024, 2032, 0.3399, rebate=6000,
           ira=True), inc(2024, 2032, 0.3424, rebate=4000)]
    scn = [inc(2024, 2050, 0.3948, rebate=8000), inc(2024, 2050, 0.3566, rebate=6000),
           inc(2024, 2050, 0.2486, rebate=4000)]
    assert reconcile(ref, scn, "incentives") == ref + scn


def test_row_with_start_after_end_passes_through_inactive():
    # A row that ends before it starts is never active, so it is passed through untouched
    ref, bad = [inc(2025, 2031, 0.4856)], inc(2035, 2030, 1.0, rebate=2000)
    assert reconcile(ref, [bad], "incentives") == ref + [bad]


def test_other_program_stacks_but_same_program_is_trimmed():
    ref = [inc(2024, 2031, 0.5, rebate=4000, pid="util-a")]
    # Same program, same population, lower level: already provided by the reference
    assert reconcile(ref, [inc(2026, 2031, 0.5, rebate=1000, pid="util-a")], "incentives") == ref
    # A different program offering the same thing is separate, so it is kept in full
    other = inc(2026, 2031, 0.5, rebate=1000, pid="util-b")
    assert reconcile(ref, [other], "incentives") == ref + [other]


def test_same_program_other_fraction_is_kept_in_full():
    # Other fractions of one program are other customer groups (e.g., income bands)
    ref = [inc(2024, 2031, 0.3, rebate=4000, pid="util-a")]
    scn = [inc(2024, 2031, 0.4, rebate=4000, pid="util-a")]
    assert reconcile(ref, scn, "incentives") == ref + scn


def test_reference_backup_yes_covers_scenario_backup_no_and_required():
    ref = [inc(2024, 2031, 0.5, backup="yes")]
    for backup in ("no", "required"):
        assert reconcile(ref, [inc(2026, 2031, 0.5, rebate=1000, backup=backup)],
                         "incentives") == ref
    # But a reference with backup 'no' does not cover a scenario backup of 'yes'
    scn = [inc(2026, 2031, 0.5, rebate=1000, backup="yes")]
    assert reconcile([inc(2024, 2031, 0.5, backup="no")], scn, "incentives")[1:] == scn


def _incentives_csv(tmp_path, drop_col=False, pid="util-a", **over):
    """Write a one-row incentives file with the real header, optionally breaking program id."""
    import csv
    with open(fp.SUB_FED / "incentives.csv", newline="", encoding="utf-8-sig") as f:
        hdr = next(csv.reader(f))
    row = {c: "" for c in hdr}
    row.update({"scenario": "reference", "state(s)": "CA", "building type(s)": "all residential",
                "building vintage(s)": "existing", "end use(s)": "heating", "tech(s)": "ASHP",
                "fuel type(s)": "electricity", "base fuel": "all fossil", "modification": "replace",
                "scope": "non-federal",
                "performance level": "2.69", "performance units": "COP", "rebate amount": "1000",
                "rebate units": "$/unit", "start year": "2025", "end year": "2030",
                "applicable fraction": "0.5", "program id": pid})
    row.update(over)
    cols = [c for c in hdr if not (drop_col and c == "program id")]
    path = tmp_path / "incentives.csv"
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerow(row)
    return path


def _import_file(path):
    ns = types.SimpleNamespace()
    opts = types.SimpleNamespace(incentive_levels="reference", incentive_restrictions="all")
    epv.UsefulVars.import_state_data(
        ns, types.SimpleNamespace(incentives=path), ["incentives"], STATES, opts)
    return ns.incentives


def test_import_carries_program_id_in_exploded_rows(tmp_path):
    rows = _import_file(_incentives_csv(tmp_path))
    assert rows and all(len(r) == 21 and r[10] == "util-a" for r in rows)


def test_import_extension_increase_pct_is_ninth_from_end(tmp_path):
    # apply_incentives reads an extension's percentage increase at index -9 of the exploded row
    path = _incentives_csv(tmp_path, modification="extend", **{
        "increase pct": "15", "rebate amount": "", "performance level": "2.69"})
    rows = _import_file(path)
    assert rows and all(r[8] == "extend" and r[-9] == 15 and r[-8] == 2.69 for r in rows)


def test_import_requires_program_id(tmp_path):
    with pytest.raises(ValueError, match="program id"):
        _import_file(_incentives_csv(tmp_path, drop_col=True))
    with pytest.raises(ValueError, match="program id"):
        _import_file(_incentives_csv(tmp_path, pid=" "))


STATES = ["AL", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "ID", "IL", "IN", "IA", "KS",
          "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM",
          "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA",
          "WA", "WV", "WI", "WY"]


def _import(scn):
    """Import the real incentives and rates files for all states under the given scenario."""
    ns = types.SimpleNamespace()
    hf = types.SimpleNamespace(incentives=fp.SUB_FED / "incentives.csv",
                               low_volume_rate=fp.SUB_FED / "rates.csv")
    opts = types.SimpleNamespace(incentive_levels=scn, low_volume_rate=scn,
                                 incentive_restrictions="all")
    epv.UsefulVars.import_state_data(ns, hf, ["incentives", "low_volume_rate"], STATES, opts)
    return {"incentives": ns.incentives or [], "low_volume_rate": ns.low_volume_rate or []}


def redundant_scenario_rows(ref, scn, k, same_program=True):
    """Scenario rows that a reference row already fully provides in some year.

    A scenario row is redundant for the years it shares with a reference row that covers the same
    segment (an 'all' end use or tech in the reference covers any specific value), applies to the
    same population (same applicable fraction), offers at least the same level in every level
    field, and has the same performance requirements. Layering should have trimmed or removed
    such rows; rows that improve on the reference or cover a different population are fine. With
    same_program False the program id is ignored, which finds rows that would stack on a
    reference row only because they carry a different id.

    Returns:
        List of (scenario row, reference row) pairs.
    """
    layout = epv._SUBFED_LAYOUT[k]
    n_key, lev_ix, perf_ix = layout["n_key"], layout["levels"], layout["perf"]
    prog_ix = layout["program"]

    def same(a, b):
        # Equality that treats two NaNs (blank cells) as equal
        return a == b or (a != a and b != b)

    # Index reference rows by state/building/vintage; real inputs explode to many thousands of rows
    by_seg = {}
    for r in ref:
        if not epv._is_inert(r, k):
            by_seg.setdefault(tuple(r[:3]), []).append(r)
    out = []
    for s in scn:
        # Skip rows that do nothing or are never active
        if epv._is_inert(s, k) or span(s)[0] > span(s)[1]:
            continue
        # Look for a single reference row that provides everything this scenario row does
        for r in by_seg.get(tuple(s[:3]), []):
            if (all(same(r[i], s[i]) or (i in (3, 4) and r[i] == "all") or (
                    i == 7 and r[i] == "yes") for i in range(n_key))
                    and (prog_ix is None or not same_program or r[prog_ix] == s[prog_ix])
                    and max(span(r)[0], span(s)[0]) <= min(span(r)[1], span(s)[1])
                    and abs(r[FRAC] - s[FRAC]) < 1e-4
                    and all(float(r[i]) >= float(s[i]) for i in lev_ix)
                    and all(same(r[i], s[i]) for i in perf_ix)):
                out.append((s, r))
                break
    return out


def test_redundant_scenario_rows_flags_only_true_repeats():
    ref = [inc(2024, 2031, 0.5, rebate=4000)]
    # Same population, same years, lower or equal level: redundant, even over a partial year range
    assert redundant_scenario_rows(ref, [inc(2026, 2040, 0.5, rebate=1000)], "incentives")
    # Better level, other fraction, other performance requirement, or no shared years: not
    assert not redundant_scenario_rows(ref, [inc(2024, 2031, 0.5, rebate=8000)], "incentives")
    assert not redundant_scenario_rows(ref, [inc(2024, 2031, 1.0, rebate=1000)], "incentives")
    assert not redundant_scenario_rows(
        ref, [inc(2024, 2031, 0.5, rebate=1000, perf_lev=3.0)], "incentives")
    assert not redundant_scenario_rows(ref, [inc(2032, 2040, 0.5, rebate=1000)], "incentives")
    # A reference end use of 'all' covers a specific scenario end use
    assert redundant_scenario_rows([inc(2024, 2031, 0.5, eu="all")],
                                   [inc(2024, 2031, 0.5, rebate=1000)], "incentives")


@pytest.mark.parametrize("k", ["incentives", "low_volume_rate"])
def test_real_files_aggressive_layers_on_reference_without_overlap(k):
    # The import itself runs the rate fraction-sum validation, so it raises if the real rates.csv
    # has overlapping fractions in the reference or after layering the aggressive scenario
    ref, agg = _import("reference")[k], _import("aggressive")[k]
    # The aggressive rows begin with the reference rows and add more after them
    assert agg[:len(ref)] == ref
    assert len(agg) > len(ref)
    n_key, levels = epv._SUBFED_LAYOUT[k]["n_key"], epv._SUBFED_LAYOUT[k]["levels"]
    # Group active (non-inert) rows by segment
    segs = {}
    for r in agg:
        inert = (k == "incentives" and r[8] == "remove") or not any(float(r[i]) for i in levels)
        if not inert:
            segs.setdefault(tuple(map(str, r[:n_key])), []).append(r)
    n_ref = {id(r) for r in ref}
    # No scenario row may repeat what a reference row already provides
    assert not redundant_scenario_rows(ref, agg[len(ref):], k)
    # No row may end before it starts (such a row would silently never apply)
    assert not [r for r in agg if r[START] and r[END] and r[START] > r[END]]
    if k == "incentives":
        # Sub-state programs with different fractions legitimately stack, so no sum check
        return
    # Rates: in segments with both reference and scenario rows, the distinct fractions in force
    # in any year must not exceed 1
    for rows in segs.values():
        if all(id(r) in n_ref for r in rows) or all(id(r) not in n_ref for r in rows):
            continue
        for y in range(2024, 2051):
            live = [r for r in rows if span(r)[0] <= y <= span(r)[1]]
            assert sum({round(r[FRAC], 4) for r in live}) <= 1 + 1e-6, (rows[0][:n_key], y)


def test_real_incentives_aggressive_rows_do_not_stack_on_identical_reference_rows():
    # Rows with different program ids stack, so an aggressive row that repeats a reference row
    # under another id (or without the ira flag) would double the incentive in shared years
    ref, agg = _import("reference")["incentives"], _import("aggressive")["incentives"]
    dups = redundant_scenario_rows(ref, agg[len(ref):], "incentives", same_program=False)
    assert not dups, sorted({(s[0], s[10], r[10]) for s, r in dups})


def test_real_hear_rows_follow_doe_base_fuel_and_backup_rules():
    # HEAR/HEEHR rebates replace existing electric equipment, except heating, where any base fuel
    # qualifies as long as a fossil system that remains is kept only as backup ('required')
    rows = [r for scn in ("reference", "aggressive") for r in _import(scn)["incentives"]
            if str(r[10]).endswith("-HEAR")]
    assert rows
    for r in rows:
        assert r[11] is True, r[10]
        if r[3] in ("cooking", "drying", "water heating"):
            assert r[6] == "electricity", (r[10], r[3], r[6])
        elif r[4] == "ASHP":
            assert r[7] == "required", (r[10], r[3], r[7])


def test_rates_better_level_on_fully_covered_population_kept():
    # A larger reduction for the same (full) population is an improvement and is kept
    res = reconcile([rate(2024, 2035, 1.0, vol_rel=0.2)], [rate(2030, 2035, 1.0, vol_rel=0.3)],
                    "low_volume_rate")
    assert [(r[START], r[END], r[FRAC], r[7]) for r in res[1:]] == [(2030, 2035, 1.0, 0.3)]


def test_rates_worse_or_equal_level_on_fully_covered_population_dropped():
    # Equal or smaller reductions for the same population add nothing and are dropped
    ref = [rate(2024, 2035, 1.0, vol_rel=0.2)]
    assert reconcile(ref, [rate(2030, 2035, 1.0, vol_rel=0.2)], "low_volume_rate") == ref
    assert reconcile(ref, [rate(2030, 2035, 1.0, vol_rel=0.1)], "low_volume_rate") == ref


def test_select_rate_tiers_picks_largest_reduction_per_fraction():
    from scout.ecm_prep import select_rate_tiers
    base = 20.0  # $/MMBtu
    ref, better = rate(2024, 2035, 1.0, vol_rel=20), rate(2030, 2035, 1.0, vol_rel=30)
    # The larger reduction wins regardless of row order
    assert select_rate_tiers([ref, better], base) == [better]
    assert select_rate_tiers([better, ref], base) == [better]
    # Absolute reduction (0.07 $/kWh = ~20.5 $/MMBtu) beats a smaller relative one at 0.5
    half_rel, half_abs = rate(2024, 2035, 0.5, vol_rel=20), rate(
        2024, 2035, 0.5, vol_rel=False, vol_abs=0.07)
    assert select_rate_tiers([half_rel, half_abs], base) == [half_abs]


def test_select_rate_tiers_keeps_distinct_fractions_additive_and_full_supersedes():
    from scout.ecm_prep import select_rate_tiers
    a, b = rate(2024, 2035, 0.4, vol_rel=20), rate(2024, 2035, 0.3, vol_rel=10)
    # Different fractions are different customer groups, so both rows are kept
    assert select_rate_tiers([a, b], 20.0) == [a, b]
    # A row covering everyone (fraction 1) supersedes the partial ones
    full = rate(2024, 2035, 1.0, vol_rel=5)
    assert select_rate_tiers([a, b, full], 20.0) == [full]


# ---- Fraction-sum validation ----

def ent(frac, start=None, end=None, seg=("CA", "all"), origin="reference"):
    """Entry for check_fraction_sums: (segment, start year, end year, fraction, origin)."""
    return (seg, start, end, frac, origin)


def test_check_sums_ok_cases():
    from scout.utils import check_fraction_sums as chk
    # Empty input and fractions summing to exactly 1 pass
    chk([], "f.csv", "reference")
    chk([ent(0.6), ent(0.4)], "f.csv", "reference")
    # Fraction of 1 is exempt, as are identical fractions (tiers of one policy)
    chk([ent(1), ent(0.7), ent(0.6, seg=("NY", "all")), ent(0.6, seg=("NY", "all"))],
        "f.csv", "reference")
    # Non-overlapping years or segments never sum
    chk([ent(0.7, 2024, 2030), ent(0.7, 2031, 2040)], "f.csv", "reference")
    chk([ent(0.7, seg=("CA", "a")), ent(0.7, seg=("CA", "b"))], "f.csv", "reference")


def test_check_sums_flags_overlap_with_informative_message():
    from scout.utils import check_fraction_sums as chk
    entries = [ent(0.6, 2024, 2035), ent(0.5, 2030, 2040, origin="aggressive")]
    with pytest.raises(ValueError) as err:
        chk(entries, "incentives.csv", "aggressive")
    msg = str(err.value)
    # The message names the file, scenario, segment, first bad year, each row, and the total
    for txt in ["incentives.csv", "aggressive", "'CA', 'all'", "from 2030",
                "0.6 (reference, 2024-2035)", "0.5 (aggressive, 2030-2040)", "1.1"]:
        assert txt in msg


def test_check_sums_wildcard_and_distinct_fraction_counting():
    from scout.utils import check_fraction_sums as chk
    wild = [ent(0.6, seg=("CA", "all")), ent(0.5, seg=("CA", "ASHP"))]
    # 'all' only overlaps a specific value when that position is marked as a wildcard
    chk(wild, "f.csv", "reference")
    with pytest.raises(ValueError):
        chk(wild, "f.csv", "reference", wild=(1,))
    # Distinct fractions are added even when one repeats
    with pytest.raises(ValueError):
        chk([ent(0.5), ent(0.5), ent(0.3), ent(0.3), ent(0.4)], "f.csv", "reference")


def test_check_sums_groups_and_caps_report():
    from scout.utils import check_fraction_sums as chk
    # 15 segments each overlap (0.6 + 0.5), but at most max_report lines are described
    entries = [ent(f, seg=("S%d" % i, "all")) for i in range(15) for f in (0.6, 0.5)]
    with pytest.raises(ValueError) as err:
        chk(entries, "f.csv", "reference", max_report=3)
    assert "15 segment group(s)" not in str(err.value) or "and 12 more" in str(err.value)
    assert str(err.value).count("\n  - segment") <= 3


def test_validate_rates_reference_and_scenario_attribution():
    ok_ref = [rate(2024, 2035, 0.6)]
    # A valid scenario (0.6 + 0.4) passes
    epv.validate_rate_fractions(ok_ref, [rate(2030, 2040, 0.4, vol_rel=0.3)], "aggressive")
    # An overlap within the reference alone is attributed to the reference
    with pytest.raises(ValueError, match="scenario 'reference'"):
        epv.validate_rate_fractions(
            [rate(2024, 2035, 0.6), rate(2025, 2030, 0.7, vol_rel=0.3)], [], "aggressive")
    # An overlap introduced by the scenario row is attributed to the scenario
    with pytest.raises(ValueError, match="scenario 'aggressive'.*rates.csv|rates.csv"):
        epv.validate_rate_fractions(ok_ref, [rate(2030, 2040, 0.5, vol_rel=0.3)], "aggressive")


def test_validate_rates_ignores_inert_and_full_rows():
    # A zero-reduction row (inert) and a fraction-1 row do not count toward the sum
    refs = [rate(2024, 2035, 0.6), rate(2024, 2035, 0.7, vol_rel=0), rate(2024, 2035, 1.0)]
    epv.validate_rate_fractions(refs, [], "reference")


def test_reconciled_rate_scenarios_never_trip_validation():
    # Layered scenario rows should always pass the fraction-sum validation
    ref = [rate(2024, 2031, 0.446)]
    res = reconcile(ref, [rate(2025, 2050, 0.446), rate(2025, 2040, 0.3, vol_rel=0.5)],
                    "low_volume_rate")
    epv.validate_rate_fractions(ref, res[len(ref):], "aggressive")


def test_run_validate_state_fractions():
    from scout import run
    vf = run.UsefulVars.validate_state_fractions

    def row(frac, yr=2025, state="CA", bldg="Commercial (New)", typ="local"):
        # Codes/BPS rows are dicts keyed by field name
        return {"reg": state, "bldg": bldg, "onsite_reduce": 0, "lag_reduce": 0,
                "stretch_reduce": 0, "start_yr": yr, "apply_frac": frac, "regu_type": typ,
                "jurisdiction": None}

    # Fractions summing to 1 pass; a fraction of 1 and a different state are not counted
    vf("codes", "reference", [row(0.6), row(0.4)], ["reference"] * 2)
    vf("codes", "reference", [row(0.6), row(1.0), row(0.9, state="NY")], ["reference"] * 3)
    # A state-wide policy split across pathways complements local policies
    vf("codes", "reference", [row(0.8, typ="state"), row(0.2, typ="state"), row(0.6), row(0.4)],
       ["reference"] * 4)
    # A scenario row that overlaps the reference (0.6 + 0.5 from 2030) fails
    with pytest.raises(ValueError, match="codes.csv"):
        vf("codes", "aggressive", [row(0.6), row(0.5, 2030)], ["reference", "aggressive"])
    # Overlap within the reference is attributed to the reference
    with pytest.raises(ValueError, match="scenario 'reference'"):
        vf("bps", "aggressive", [row(0.6), row(0.5)], ["reference"] * 2)
    # Appliance regs: [state, bldg, vint, fuel, eu, tech, start, frac, jurisdiction, type]

    def ar(frac, tech="all", yr=2025, jur=None, typ=None):
        return ["CA", "single family home", "new", "natural gas", "heating", tech, yr, frac, jur,
                typ]

    # Same-tech rows summing to 1 pass; a tech of 'all' overlaps a specific tech (0.6 + 0.5)
    vf("state_appl_regs", "reference", [ar(0.6, "furnace"), ar(0.4, "furnace")], ["reference"] * 2)
    with pytest.raises(ValueError, match="state_appl_regs.csv"):
        vf("state_appl_regs", "reference", [ar(0.6), ar(0.5, "furnace")], ["reference"] * 2)
    # Cumulative stages of one jurisdiction never add; other jurisdictions and untagged rows do
    stages = [ar(0.6, yr=2030, jur="CARB"), ar(0.67, yr=2035, jur="CARB"),
              ar(0.75, yr=2040, jur="CARB")]
    vf("state_appl_regs", "aggressive", stages, ["aggressive"] * 3)
    # A 0.3 reference program in another jurisdiction adds to the latest CARB stage and fails
    with pytest.raises(ValueError, match="CARB"):
        vf("state_appl_regs", "aggressive", stages + [ar(0.3, yr=2030, jur="BAAQMD")],
           ["aggressive"] * 3 + ["reference"])
    # An untagged 0.3 row also adds to the CARB stages
    with pytest.raises(ValueError, match="state_appl_regs.csv"):
        vf("state_appl_regs", "aggressive", stages + [ar(0.3, yr=2030)], ["aggressive"] * 4)
    # A 'state' target already includes local programs, so local rows never overlap it
    st = [ar(f, yr=y, jur="CARB", typ="state") for y, f in ((2030, 0.6), (2035, 0.67))]
    vf("state_appl_regs", "aggressive", st + [ar(0.3, yr=2030, jur="BAAQMD", typ="local")],
       ["aggressive"] * 2 + ["reference"])
    vf("state_appl_regs", "aggressive", st + [ar(0.3, yr=2030, typ="local")],
       ["aggressive"] * 2 + ["reference"])
    # Overlapping state targets do not stack (the larger applies), but local programs that
    # sum past 1 are still caught
    vf("state_appl_regs", "aggressive", [ar(0.6, typ="state"), ar(0.3, typ="state")],
       ["aggressive"] * 2)
    with pytest.raises(ValueError, match="state_appl_regs.csv"):
        vf("state_appl_regs", "aggressive", [ar(0.6, jur="A", typ="local"),
                                             ar(0.5, jur="B", typ="local"), ar(0.3, typ="state")],
           ["aggressive"] * 3)


def _chk_ent(frac, start, jur, seg=("CA", "all"), typ=None):
    """Entry for check_fraction_sums with a jurisdiction and optional policy type."""
    return (seg, start, None, frac, "aggressive", jur) + ((typ,) if typ else ())


def test_check_sums_jurisdiction_stages_are_cumulative():
    from scout.utils import check_fraction_sums as chk
    # Latest stage replaces earlier ones within a jurisdiction
    chk([_chk_ent(0.6, 2030, "CARB"), _chk_ent(0.67, 2035, "CARB"), _chk_ent(0.75, 2040, "CARB")],
        "f.csv", "aggressive")
    # Distinct jurisdictions are summed, including when their fractions are identical
    chk([_chk_ent(0.3, 2030, "A"), _chk_ent(0.3, 2030, "B")], "f.csv", "aggressive")
    with pytest.raises(ValueError, match=r"A\)? \+ 0.6 .*B|B\)? \+ 0.6 .*A|counts as 1.1"):
        chk([_chk_ent(0.5, 2030, "A"), _chk_ent(0.6, 2030, "B")], "f.csv", "aggressive")
    # A later stage can push a sum over 1 even though the earlier stages did not
    with pytest.raises(ValueError, match="from 2035"):
        chk([_chk_ent(0.5, 2030, "A"), _chk_ent(0.5, 2030, "B"), _chk_ent(0.6, 2035, "A")],
            "f.csv", "aggressive")
    # A later full stage retires the partial one
    chk([_chk_ent(0.6, 2030, "A"), _chk_ent(1.0, 2035, "A"), _chk_ent(0.3, 2030, "B")],
        "f.csv", "aggressive")


def _screen(rows, years=range(2025, 2051), fuel_switch=None):
    """Run Engine.state_app_reg_screen for one CA single family gas furnace measure.

    Rows are [tech, start year, fraction, jurisdiction[, type]]; returns the years the measure
    remains on the market and the restricted fraction by year.
    """
    from scout import run
    # Segment of the rows, and the key of the measure's competed market in that segment
    seg = ["CA", "single family home", "existing", "natural gas", "heating"]
    key = str(("primary", "CA", "single family home", "natural gas", "heating", "supply",
               "furnace (NG)", "existing"))
    # Minimal stand-ins for the measure and the engine object that the screen reads from
    meas = types.SimpleNamespace(yrs_on_mkt=[str(y) for y in years], fuel_switch_to=fuel_switch,
                                 backup_fuel_fraction=None)
    me = types.SimpleNamespace(handyvars=types.SimpleNamespace(
        aeo_years=[str(y) for y in years],
        state_appl_regs=[seg + (r + [None])[:5] for r in rows]))
    on_mkt, fracs = run.Engine.state_app_reg_screen(me, [meas], [[key]])
    return on_mkt[0], fracs[0]


def test_state_app_reg_screen_uses_latest_stage_per_jurisdiction():
    # CARB stages are cumulative (replace) and a 'state' target already includes BAAQMD
    gross = [["all", 2030, 0.6, "CARB", "state"], ["all", 2035, 0.67, "CARB", "state"],
             ["all", 2040, 0.75, "CARB", "state"], ["all", 2029, 0.195, "BAAQMD", "local"]]
    _, fracs = _screen(gross)
    # Nothing before the first start year; BAAQMD alone; then the latest CARB stage absorbs it
    assert fracs["2028"] == 0
    assert round(fracs["2029"], 6) == 0.195
    assert round(fracs["2030"], 6) == 0.6
    assert round(fracs["2035"], 6) == 0.67
    assert round(fracs["2050"], 6) == 0.75
    # A state stage smaller than BAAQMD (0.195) would not subtract from it; the larger applies
    small = [["all", 2030, 0.1, "CARB", "state"], ["all", 2029, 0.195, "BAAQMD", "local"]]
    assert round(_screen(small)[1]["2030"], 6) == 0.195
    # Legacy blank type counts as local, so jurisdictions add; this is why a state target that
    # excludes BAAQMD had to be hand-netted (0.405 + 0.195 = 0.6) before the type column
    legacy = [["all", 2030, 0.405, "CARB"], ["all", 2035, 0.475, "CARB"],
              ["all", 2040, 0.555, "CARB"], ["all", 2029, 0.195, "BAAQMD"]]
    _, fracs = _screen(legacy)
    assert round(fracs["2030"], 6) == 0.6 and round(fracs["2035"], 6) == 0.67
    assert round(fracs["2050"], 6) == 0.75


def test_state_app_reg_screen_untagged_rows_keep_additive_behavior_and_full_supplants():
    # No jurisdiction: distinct fractions add and identical ones count once
    _, fracs = _screen([["all", 2030, 0.2, None], ["all", 2035, 0.2, None],
                        ["all", 2035, 0.1, None]])
    assert round(fracs["2030"], 6) == 0.2 and round(fracs["2035"], 6) == 0.3
    # A fraction of 1 removes the measure from the market from its start year and supplants others
    on_mkt, fracs = _screen([["all", 2030, 0.4, "A"], ["all", 2035, 1, "B"]])
    assert "2034" in on_mkt and "2035" not in on_mkt
    assert round(fracs["2030"], 6) == 0.4


def test_state_app_reg_screen_caps_overlapping_fractions_at_full_restriction():
    # Untagged 0.6 + 0.7 and distinct jurisdictions 0.7 + 0.6 would sum to 1.3 if not capped
    for rows in ([["all", 2030, 0.6, None], ["all", 2030, 0.7, None]],
                 [["all", 2030, 0.7, "A"], ["all", 2030, 0.6, "B"]]):
        on_mkt, fracs = _screen(rows)
        assert "2029" in on_mkt and "2030" not in on_mkt
        # No partial-restriction share above 1; a full restriction removes the measure instead
        assert max(fracs.values()) <= 1
        assert fracs["2030"] == 0 or fracs["2030"] == 1
        # A fuel-switching measure avoids the regulation entirely
        on_mkt, fracs = _screen(rows, fuel_switch="electricity")
        assert "2030" in on_mkt and fracs["2030"] == 0


def test_import_appl_regs_reads_jurisdiction_column(tmp_path):
    from scout import run
    import pandas as pd
    # Small appl_regs file with a jurisdiction column: two CARB stages and one untagged row
    hdr = ("scenario,description,state(s),building type(s),building vintage(s),fuel type(s),"
           "end use(s),tech(s),start year,applicable fraction,fraction notes,jurisdiction\n")
    body = ("aggressive,d,CA,single family home,new,natural gas,heating,all,2030,0.6,,CARB\n"
            "aggressive,d,CA,single family home,new,natural gas,heating,all,2035,0.67,,CARB\n"
            "reference,d,CA,single family home,new,natural gas,heating,all,2029,0.2,,\n")
    f = tmp_path / "appl_regs.csv"
    f.write_text(hdr + body)
    assert list(pd.read_csv(f).columns)[-1] == "jurisdiction"
    # Import with minimal stand-ins, then check start year, fraction and jurisdiction of each row
    hv = types.SimpleNamespace(aeo_years=[str(y) for y in range(2024, 2051)])
    hv.validate_state_fractions = run.UsefulVars.validate_state_fractions
    run.UsefulVars.import_state_data(hv, types.SimpleNamespace(state_appl_regs=f),
                                     ["state_appl_regs"], ["aggressive"])
    assert [(r[6], r[7], r[8]) for r in hv.state_appl_regs] == [
        (2029, 0.2, None), (2030, 0.6, "CARB"), (2035, 0.67, "CARB")]


def test_check_sums_state_target_includes_local_rows():
    from scout.utils import check_fraction_sums as chk
    # Local rows (0.5 + 0.4) sum to at most 1 and a 0.6 state target does not add to them: passes
    chk([_chk_ent(0.6, 2030, "CARB", typ="state"), _chk_ent(0.5, 2030, "BAAQMD", typ="local"),
         _chk_ent(0.4, 2030, "SCAQMD", typ="local")], "f.csv", "aggressive")
    # Local rows alone exceeding 1 are still caught, even next to a smaller state target
    with pytest.raises(ValueError, match="state_appl_regs|f.csv"):
        chk([_chk_ent(0.3, 2030, "CARB", typ="state"), _chk_ent(0.7, 2030, "A", typ="local"),
             _chk_ent(0.6, 2030, "B", typ="local")], "f.csv", "aggressive")
    # Two state targets in the same segment do not stack; the larger applies
    chk([_chk_ent(0.6, 2030, None, typ="state"), _chk_ent(0.5, 2030, None, typ="state")],
        "f.csv", "aggressive")


def test_state_app_reg_screen_state_target_is_netted_against_local_programs():
    # Local programs below the state target are absorbed; above it, they set the total
    local = [["all", 2025, 0.2, "BAAQMD", "local"], ["all", 2025, 0.15, "SCAQMD", "local"]]
    state = [["all", 2030, 0.6, "CARB", "state"], ["all", 2035, 0.67, "CARB", "state"]]
    _, fracs = _screen(local + state)
    # Locals alone (0.2 + 0.15) before the state target starts; then the target replaces them
    assert round(fracs["2025"], 6) == 0.35
    assert round(fracs["2030"], 6) == 0.6 and round(fracs["2035"], 6) == 0.67
    # Locals (0.7 in total) above both state stages (0.6, 0.67) set the total in every year
    big = [["all", 2025, 0.4, "A", "local"], ["all", 2025, 0.3, "B", "local"]]
    _, fracs = _screen(big + state)
    assert round(fracs["2025"], 6) == 0.7 and round(fracs["2030"], 6) == 0.7
    assert round(fracs["2035"], 6) == 0.7 and round(fracs["2040"], 6) == 0.7
    # Same totals as the user hand-netting the state row (the pre-'type' convention)
    netted = big + [["all", 2030, 0.0, "CARB", "local"], ["all", 2035, 0.0, "CARB", "local"]]
    assert _screen(netted)[1]["2035"] == _screen(big + state)[1]["2035"]
    # Untagged and blank-type rows add as before, and are also absorbed by a state target
    _, fracs = _screen([["all", 2025, 0.2, None, None], ["all", 2030, 0.6, None, "state"]])
    assert round(fracs["2025"], 6) == 0.2 and round(fracs["2030"], 6) == 0.6


def test_state_app_reg_screen_local_blank_type_adds_to_other_jurisdictions():
    # Blank type is treated as local, so two jurisdictions' fractions add (0.3 + 0.2)
    _, fracs = _screen([["all", 2030, 0.3, "A"], ["all", 2030, 0.2, "B"]])
    assert round(fracs["2030"], 6) == 0.5


def test_import_appl_regs_rejects_invalid_type(tmp_path):
    from scout import run
    # A type other than 'state' or 'local' must raise an error that names the bad value
    hdr = ("scenario,description,state(s),building type(s),building vintage(s),fuel type(s),"
           "end use(s),tech(s),start year,applicable fraction,fraction notes,jurisdiction,type\n")
    f = tmp_path / "appl_regs.csv"
    f.write_text(hdr + "aggressive,d,CA,single family home,new,natural gas,heating,all,2030,0.6,,"
                 "CARB,federal\n")
    hv = types.SimpleNamespace(aeo_years=[str(y) for y in range(2024, 2051)])
    hv.validate_state_fractions = run.UsefulVars.validate_state_fractions
    with pytest.raises(ValueError, match="federal"):
        run.UsefulVars.import_state_data(hv, types.SimpleNamespace(state_appl_regs=f),
                                         ["state_appl_regs"], ["aggressive"])


def test_import_appl_regs_reads_type_column(tmp_path):
    from scout import run
    # Types are read case-insensitively ('State' -> 'state'); a blank type is imported as None
    hdr = ("scenario,description,state(s),building type(s),building vintage(s),fuel type(s),"
           "end use(s),tech(s),start year,applicable fraction,fraction notes,jurisdiction,type\n")
    f = tmp_path / "appl_regs.csv"
    pre = "d,CA,single family home,new,natural gas,heating,all,"
    f.write_text(hdr + "aggressive," + pre + "2030,0.6,,CARB,State\n"
                 "reference," + pre + "2029,0.2,,BAAQMD,local\n"
                 "reference," + pre + "2028,0.1,,,\n")
    hv = types.SimpleNamespace(aeo_years=[str(y) for y in range(2024, 2051)])
    hv.validate_state_fractions = run.UsefulVars.validate_state_fractions
    run.UsefulVars.import_state_data(hv, types.SimpleNamespace(state_appl_regs=f),
                                     ["state_appl_regs"], ["aggressive"])
    assert [(r[6], r[8], r[9]) for r in hv.state_appl_regs] == [
        (2029, "BAAQMD", "local"), (2028, None, None), (2030, "CARB", "state")]


def test_real_appl_regs_gross_targets_and_local_programs_are_typed():
    d = pd.read_csv("scout/supporting_data/sub_fed/appl_regs.csv")
    # The real file must have a type column with only valid values
    assert list(d.columns)[-1] == "type"
    assert d["type"].isin(["state", "local"]).all()
    # Aggressive rows and the CO Clean Heat Standard are statewide targets; other reference rows
    # (city and air-district programs) are local
    assert (d.loc[d["scenario"] == "aggressive", "type"] == "state").all()
    chs = d["jurisdiction"] == "CO Clean Heat Standard"
    assert (d.loc[chs, "type"] == "state").all()
    assert (d.loc[(d["scenario"] == "reference") & ~chs, "type"] == "local").all()
