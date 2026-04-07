#!/usr/bin/env python3

"""Tests for fuel switching, heat pumps, dual-fuel, and cooling features."""

import copy
from collections import OrderedDict
from tests.ecm_prep_test.common import dict_check


def test_mseg_ok_hp_rates_map(market_test_data):
    """Test 'fill_mkts' function given valid inputs.

    Notes:
        Checks the 'master_mseg' and 'mseg_out_break' branches of measure
        'markets' attribute under a max adoption potential scenario with
        EMM regions, fuel splits, and HP measures, where some HPs fuel
        switch under exogenous rates, as well as other non-HP measures
        that are used to ensure HP settings are not erroneously applied
        to other measure types.

    Raises:
        AssertionError: If function yields unexpected results.
    """
    for idx, measure in enumerate(market_test_data["ok_mapmeas_hp_chk_in"]):
        # Handle test measures with and without exogenous HP conversion
        # rates specified
        if "no rates" in measure.name:
            measure.fill_mkts(
                market_test_data["sample_mseg_in_emm"],
                market_test_data["sample_cpl_in_emm"],
                market_test_data["convert_data"],
                market_test_data["tsv_data"],
                market_test_data["opts_hp_no_rates"],
                ctrb_ms_pkg_prep=[],
                tsv_data_nonfs=None,
            )
        else:
            measure.fill_mkts(
                market_test_data["sample_mseg_in_emm"],
                market_test_data["sample_cpl_in_emm"],
                market_test_data["convert_data"],
                market_test_data["tsv_data"],
                market_test_data["opts_hp_rates"],
                ctrb_ms_pkg_prep=[],
                tsv_data_nonfs=None,
            )
        dict_check(
            measure.markets["Max adoption potential"]["master_mseg"],
            market_test_data["ok_hpmeas_rates_mkts_out"][idx],
        )

        # Check output breakouts including fuel splits for the first HP
        # measure (which uses exogenous fuel switching rates) and the last
        # HP measure (which does not use exogenous fuel switching rates)
        if "with rates" in measure.name:
            dict_check(
                measure.markets["Max adoption potential"]["mseg_out_break"],
                market_test_data["ok_hpmeas_rates_breakouts"][0],
            )
        elif "no rates" in measure.name:
            dict_check(
                measure.markets["Max adoption potential"]["mseg_out_break"],
                market_test_data["ok_hpmeas_rates_breakouts"][1],
            )


def test_dual_fuel(market_test_data):
    """Test dual-fuel (STATE breakout, CA) market segmentation.

    Validates that the outputs master_mseg and mseg_out_break are produced,
    contains both Electric and Non-Electric for Heating (Equip.), and
    compares against the expected one.
    """

    # Initialize dummy measure with state-level inputs to draw from
    base_state_meas = market_test_data["ok_tpmeas_partchk_state_in"][0]
    # Pull handyvars from first sample measure and set year range
    hv = copy.deepcopy(base_state_meas.handyvars)
    years = [str(y) for y in hv.aeo_years]

    # Options: split fuel reporting + pick Max adoption potential
    opts = copy.deepcopy(market_test_data["opts_state"])
    opts.split_fuel = True
    opts.adopt_scn_usr = ["Max adoption potential"]

    # Ensure fuel-split breakouts (Electric vs Non-Electric)
    hv.out_break_fuels = OrderedDict(
        [
            ("Electric", ["electricity"]),
            ("Non-Electric", ["natural gas", "distillate", "residual", "other fuel"]),
        ]
    )
    # Rebuild the blank breakout template (mirrors UsefulVars behavior)
    out_levels = [
        list(hv.out_break_czones.keys()),
        list(hv.out_break_bldgtypes.keys()),
        list(hv.out_break_enduses.keys()),
    ]
    hv.out_break_in = OrderedDict()
    for cz in out_levels[0]:
        hv.out_break_in.setdefault(cz, OrderedDict())
        for b in out_levels[1]:
            hv.out_break_in[cz].setdefault(b, OrderedDict())
            for eu in out_levels[2]:
                if (len(hv.out_break_fuels) != 0) and (eu in hv.out_break_eus_w_fsplits):
                    hv.out_break_in[cz][b][eu] = OrderedDict(
                        [(f, OrderedDict()) for f in hv.out_break_fuels.keys()]
                    )
                else:
                    hv.out_break_in[cz][b][eu] = OrderedDict()

    # Seed BY-YEAR carbon price
    carb_prices = hv.ccosts
    carb_prices.update({y: 1 for y in years})

    # Seed BY-YEAR energy price & carbon intensities
    el_prices = hv.ecosts.setdefault("residential", {}).setdefault("electricity", {})
    el_prices.update({y: 60.0 for y in years})
    ng_prices = hv.ecosts["residential"].setdefault("natural gas", {})
    ng_prices.update({y: 11.0 for y in years})

    el_carb = hv.carb_int.setdefault("residential", {}).setdefault("electricity", {})
    el_carb.update({y: 5.0e-08 for y in years})
    ng_carb = hv.carb_int["residential"].setdefault("natural gas", {})
    ng_carb.update({y: 5.0e-08 for y in years})

    hv.ss_conv.setdefault("electricity", {})
    hv.ss_conv.setdefault("natural gas", {})
    for y in years:
        hv.ss_conv["electricity"][y] = 1.0
        hv.ss_conv["natural gas"][y] = 1.0


def test_added_cooling(market_test_data):
    """Test added cooling only (no dual-fuel).

    Constructs a minimal NG→Electric (ASHP) full-service HP measure that
    adds cooling where baseline has (effectively) none.
    Validates that mseg_out_break is populated and contains Cooling (Equip.)
    under the efficient branch for CA.
    """
    # Initialize dummy measure with state-level inputs to draw from
    base_state_meas = market_test_data["ok_tpmeas_partchk_state_in"][0]
    # Pull handyvars from first sample measure and set year range
    hv = copy.deepcopy(base_state_meas.handyvars)
    years = [str(y) for y in hv.aeo_years]

    # Options: split fuel reporting + pick Max adoption potential
    opts = copy.deepcopy(market_test_data["opts_state"])
    opts.split_fuel = True
    opts.adopt_scn_usr = ["Max adoption potential"]

    # Ensure fuel-split breakouts (Electric vs Non-Electric)
    hv.out_break_fuels = OrderedDict(
        [
            ("Electric", ["electricity"]),
            ("Non-Electric", ["natural gas", "distillate", "residual", "other fuel"]),
        ]
    )
    # Rebuild the blank breakout template (mirrors UsefulVars behavior)
    out_levels = [
        list(hv.out_break_czones.keys()),
        list(hv.out_break_bldgtypes.keys()),
        list(hv.out_break_enduses.keys()),
    ]
    hv.out_break_in = OrderedDict()
    for cz in out_levels[0]:
        hv.out_break_in.setdefault(cz, OrderedDict())
        for b in out_levels[1]:
            hv.out_break_in[cz].setdefault(b, OrderedDict())
            for eu in out_levels[2]:
                if (len(hv.out_break_fuels) != 0) and (eu in hv.out_break_eus_w_fsplits):
                    hv.out_break_in[cz][b][eu] = OrderedDict(
                        (f, OrderedDict()) for f in hv.out_break_fuels.keys()
                    )
                else:
                    hv.out_break_in[cz][b][eu] = OrderedDict()

    # Seed BY-YEAR carbon price
    carb_prices = hv.ccosts
    carb_prices.update({y: 1 for y in years})

    # Seed BY-YEAR electricity price & carbon intensities
    el_prices = hv.ecosts.setdefault("residential", {}).setdefault("electricity", {})
    el_prices.update({y: 60.0 for y in years})
    ng_prices = hv.ecosts["residential"].setdefault("natural gas", {})
    ng_prices.update({y: 11.0 for y in years})

    el_carb = hv.carb_int.setdefault("residential", {}).setdefault("electricity", {})
    el_carb.update({y: 5.0e-08 for y in years})
    ng_carb = hv.carb_int["residential"].setdefault("natural gas", {})
    ng_carb.update({y: 5.0e-08 for y in years})

    hv.ss_conv.setdefault("electricity", {})
    hv.ss_conv.setdefault("natural gas", {})
    for y in years:
        hv.ss_conv["electricity"][y] = 1.0
        hv.ss_conv["natural gas"][y] = 1.0


def test_alt_rates(market_test_data):
    """Test 'fill_mkts' function given user-defined alternate electricity rate inputs.

    Notes:
        Alternate rate inputs can be specific to a technology (ASHP) or general across
        an electric end use (e.g., all electric heating).
    """

    # Initialize dummy measure with state-level inputs to draw from
    base_state_meas = market_test_data["ok_tpmeas_partchk_state_in"][0]
    # Pull handyvars from first sample measure and set year range
    hv = copy.deepcopy(base_state_meas.handyvars)
    # Set user-defined alternate electricity rates for CA
    hv.low_volume_rate = [
        [
            "CA",
            "single family home",
            "existing",
            "heating",
            "ASHP",
            "electricity",
            0.06,
            False,
            302,
            2010,
            2050,
            1,
        ],
        [
            "CA",
            "single family home",
            "new",
            "heating",
            "ASHP",
            "electricity",
            False,
            25,
            302,
            2010,
            2050,
            1,
        ],
    ]
    years = [str(y) for y in hv.aeo_years]

    # Seed BY-YEAR carbon price
    carb_prices = hv.ccosts
    carb_prices.update({y: 1 for y in years})

    # Seed BY-YEAR electricity price (before alternate rate) & carbon intensities
    el_prices = hv.ecosts.setdefault("residential", {}).setdefault("electricity", {})
    el_prices.update({y: 60.0 for y in years})
    ng_prices = hv.ecosts["residential"].setdefault("natural gas", {})
    ng_prices.update({y: 11.0 for y in years})

    el_carb = hv.carb_int.setdefault("residential", {}).setdefault("electricity", {})
    el_carb.update({y: 5.0e-08 for y in years})
    ng_carb = hv.carb_int["residential"].setdefault("natural gas", {})
    ng_carb.update({y: 5.0e-08 for y in years})

    hv.ss_conv.setdefault("electricity", {})
    hv.ss_conv.setdefault("natural gas", {})
    for y in years:
        hv.ss_conv["electricity"][y] = 1.0
        hv.ss_conv["natural gas"][y] = 1.0

    # Options: split fuel reporting + pick Max adoption potential
    opts = copy.deepcopy(market_test_data["opts_state"])
    opts.adopt_scn_usr = ["Max adoption potential"]
