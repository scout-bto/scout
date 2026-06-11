#!/usr/bin/env python3

"""Tests for regional variants (EMM, State, with cost adjustments)."""

from tests.ecm_prep_test.common import dict_check


def test_mseg_ok_part_tp_emm(market_test_data):
    """Test 'fill_mkts' function given valid inputs.

    Notes:
        Checks the 'master_mseg' branch of measure 'markets' attribute
        under a Technical potential scenario with EMM regions specified.

    Raises:
        AssertionError: If function yields unexpected results.
    """
    for idx, measure in enumerate(market_test_data["ok_tpmeas_partchk_emm_in"]):
        # Assert that inputs generate correct warnings and that measure
        # is marked inactive where necessary
        measure.fill_mkts(
            market_test_data["sample_mseg_in_emm"],
            market_test_data["sample_cpl_in_emm"],
            market_test_data["convert_data"],
            market_test_data["tsv_data"],
            market_test_data["opts_emm"],
            ctrb_ms_pkg_prep=[],
            tsv_data_nonfs=None,
        )
        dict_check(
            measure.markets["Technical potential"]["master_mseg"],
            market_test_data["ok_tpmeas_partchk_msegout_emm"][idx],
        )


def test_mseg_ok_part_tp_state(market_test_data):
    """Test 'fill_mkts' function given valid inputs.

    Notes:
        Checks the 'master_mseg' branch of measure 'markets' attribute
        under a Technical potential scenario with states specified.

    Raises:
        AssertionError: If function yields unexpected results.
    """
    for idx, measure in enumerate(market_test_data["ok_tpmeas_partchk_state_in"]):
        measure.fill_mkts(
            market_test_data["sample_mseg_in_state"],
            market_test_data["sample_cpl_in_state"],
            market_test_data["convert_data"],
            market_test_data["tsv_data"],
            market_test_data["opts_state"],
            ctrb_ms_pkg_prep=[],
            tsv_data_nonfs=None,
        )
        dict_check(
            measure.markets["Technical potential"]["master_mseg"],
            market_test_data["ok_tpmeas_partchk_msegout_state"][idx],
        )


def test_mseg_ok_part_tp_state_regadj(market_test_data):
    """Test 'fill_mkts' function given valid inputs.

    Notes:
        Checks the 'master_mseg' branch of measure 'markets' attribute
        under a Technical potential scenario with states specified and regional
        cost adjustments implemented.

    Raises:
        AssertionError: If function yields unexpected results.
    """
    ok_tpmeas_partchk_msegout_state_regadj = market_test_data[
        "ok_tpmeas_partchk_msegout_state_regadj"
    ]

    for idx, measure in enumerate(market_test_data["ok_tpmeas_partchk_state_regadj_in"]):
        measure.fill_mkts(
            market_test_data["sample_mseg_in_state"],
            market_test_data["sample_cpl_in_state"],
            market_test_data["convert_data"],
            market_test_data["tsv_data"],
            market_test_data["opts_state"],
            ctrb_ms_pkg_prep=[],
            tsv_data_nonfs=None,
        )
        dict_check(
            measure.markets["Technical potential"]["master_mseg"],
            ok_tpmeas_partchk_msegout_state_regadj[idx],
        )
