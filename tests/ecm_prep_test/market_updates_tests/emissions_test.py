#!/usr/bin/env python3

"""Tests for fugitive emissions (methane and refrigerant)."""

from tests.ecm_prep_test.common import dict_check


def test_mseg_ok_fmeth_co2_tp(market_test_data):
    """Test 'fill_mkts' function given valid inputs.

    Notes:
        Checks the 'master_mseg' branch of measure 'markets' attribute
        under a technical potential scenario with EMM regions and
        fugitive methane emissions, where some measures have fugitive
        methane emissions impacts and others do not to ensure fugitive
        methane emissions settings are not erroneously applied.

    Raises:
        AssertionError: If function yields unexpected results.
    """
    for idx, measure in enumerate(market_test_data["ok_tp_fmeth_chk_in"]):
        measure.fill_mkts(
            market_test_data["sample_mseg_in_emm"],
            market_test_data["sample_cpl_in_emm"],
            market_test_data["convert_data"],
            market_test_data["tsv_data"],
            market_test_data["opts_fmeth"][idx],
            ctrb_ms_pkg_prep=[],
            tsv_data_nonfs=None,
        )
        dict_check(
            measure.markets["Technical potential"]["master_mseg"]["fugitive emissions"]["methane"],
            market_test_data["ok_tp_fmeth_mkts_out"][idx],
        )


def test_mseg_ok_frefr_co2_map(market_test_data):
    """Test 'fill_mkts' function given valid inputs.

    Notes:
        Checks the 'master_mseg' and 'mseg_out_break' branches of measure
        'markets' attribute under a max adoption potential scenario with
        EMM regions and fugitive refrigerant emissions.

    Raises:
        AssertionError: If function yields unexpected results.
    """
    for idx, measure in enumerate(market_test_data["ok_map_frefr_chk_in"]):
        measure.fill_mkts(
            market_test_data["sample_mseg_in_emm"],
            market_test_data["sample_cpl_in_emm"],
            market_test_data["convert_data"],
            market_test_data["tsv_data"],
            market_test_data["opts_frefr"][idx],
            ctrb_ms_pkg_prep=[],
            tsv_data_nonfs=None,
        )
        dict_check(
            measure.markets["Max adoption potential"]["master_mseg"]["fugitive emissions"][
                "refrigerants"
            ],
            market_test_data["ok_map_frefr_mkts_out"][idx],
        )
