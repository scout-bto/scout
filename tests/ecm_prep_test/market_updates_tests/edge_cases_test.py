#!/usr/bin/env python3

"""Tests for edge cases: error handling, warnings, and special cost cases."""

import warnings
import pytest
from tests.ecm_prep_test.common import dict_check


def test_mseg_fail_inputs(market_test_data):
    """Test 'fill_mkts' function given invalid inputs.

    Raises:
        AssertionError: If ValueError is not raised.
    """
    # Run function on all measure objects and check output
    for idx, measure in enumerate(market_test_data["failmeas_inputs_in"]):
        with pytest.raises(Exception):
            measure.check_meas_inputs()


def test_mseg_warn(market_test_data):
    """Test 'fill_mkts' function given incomplete inputs.

    Raises:
        AssertionError: If function yields unexpected results or
        UserWarning is not raised.
    """
    # Run function on all measure objects and check output
    for idx, mw in enumerate(market_test_data["warnmeas_in"]):
        # Assert that inputs generate correct warnings and that measure
        # is marked inactive where necessary
        with warnings.catch_warnings(record=True) as w:
            mw.fill_mkts(
                market_test_data["sample_mseg_in"],
                market_test_data["sample_cpl_in"],
                market_test_data["convert_data"],
                market_test_data["tsv_data"],
                market_test_data["opts"],
                ctrb_ms_pkg_prep=[],
                tsv_data_nonfs=None,
            )
            # Check correct number of warnings is yielded
            assert all([issubclass(wn.category, UserWarning) for wn in w])
            for wm in market_test_data["ok_warnmeas_out"][idx]:
                assert wm in str([wmt.message for wmt in w])
            # Check that measure is marked inactive when a critical
            # warning message is yielded
            if any(["CRITICAL" in x for x in market_test_data["ok_warnmeas_out"][idx]]):
                assert mw.remove is True
            else:
                assert mw.remove is False


def test_mseg_ok_cool_cost(market_test_data):
    """Test 'fill_mkts' function given valid inputs.

    Notes:
        Borrows measure characteristics and settings from the 'test_mseg_ok_hp_rates_map'
        function; the only difference is the cost calculation options for this test are
        set to ensure that stock costs for both the baseline heating AND cooling equipment
        are counted when comparing against the heat pump measure costs, by removing the
        no_lnkd_stk_costs flag that is assigned in the other test (which limits stock cost
        calculations to just the heating costs in the baseline).

        Also note that the technical potential result for the measure is being checked here
        for simplicity, though the removal of the no_lnkd_stk_costs setting affects all
        adoption scenario results.

    Raises:
        AssertionError: If function yields unexpected results.
    """

    # Use data from fixture
    for idx, measure in enumerate(market_test_data['ok_coolcost_chk_in']):
        measure.fill_mkts(
            market_test_data['sample_mseg_in_emm'],
            market_test_data['sample_cpl_in_emm'],
            market_test_data['convert_data'],
            market_test_data['tsv_data'],
            market_test_data['opts_coolcosts'],
            ctrb_ms_pkg_prep=[],
            tsv_data_nonfs=None,
        )
        dict_check(
            measure.markets['Technical potential']['master_mseg']['cost']['stock'],
            market_test_data["ok_coolcost_meas_stkcost_out"],
        )
