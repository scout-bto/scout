#!/usr/bin/env python3

"""Tests for base market segmentation (fill_mkts function)."""

import pytest
import numpy
from tests.ecm_prep_test.common import dict_check


def test_mseg_ok_full_tp(market_test_data):
    """Test 'fill_mkts' function given valid inputs.

    Notes:
        Checks the all branches of measure 'markets' attribute
        under a Technical potential scenario.

    Raises:
        AssertionError: If function yields unexpected results.
    """
    # Run function on all measure objects and check output
    for idx, measure in enumerate(market_test_data["ok_tpmeas_fullchk_in"]):
        measure.fill_mkts(
            market_test_data["sample_mseg_in"],
            market_test_data["sample_cpl_in"],
            market_test_data["convert_data"],
            market_test_data["tsv_data"],
            market_test_data["opts"],
            ctrb_ms_pkg_prep=[],
            tsv_data_nonfs=None,
        )
        # Restrict the full check of all branches of 'markets' to only
        # the first three measures in this set. For the remaining two
        # measures, only check the competed choice parameter outputs.
        # These last two measures are intended to test a special case where
        # measure cost units are in $/ft^2 floor rather than $/unit and
        # competed choice parameters must be scaled accordingly
        if idx < 3:
            dict_check(
                measure.markets["Technical potential"]["master_mseg"],
                market_test_data["ok_tpmeas_fullchk_msegout"][idx],
            )
            dict_check(
                measure.markets["Technical potential"]["mseg_adjust"]["secondary mseg adjustments"],
                market_test_data["ok_tpmeas_fullchk_msegadjout"][idx],
            )
            dict_check(
                measure.markets["Technical potential"]["mseg_out_break"],
                market_test_data["ok_tpmeas_fullchk_break_out"][idx],
            )
        dict_check(
            measure.markets["Technical potential"]["mseg_adjust"]["competed choice parameters"],
            market_test_data["ok_tpmeas_fullchk_competechoiceout"][idx],
        )


def test_mseg_ok_part_tp(market_test_data):
    """Test 'fill_mkts' function given valid inputs.

    Notes:
        Checks the 'master_mseg' branch of measure 'markets' attribute
        under a Technical potential scenario with AIA regions specified.

    Raises:
        AssertionError: If function yields unexpected results.
    """
    for idx, measure in enumerate(market_test_data["ok_tpmeas_partchk_in"]):
        measure.fill_mkts(
            market_test_data["sample_mseg_in"],
            market_test_data["sample_cpl_in"],
            market_test_data["convert_data"],
            market_test_data["tsv_data"],
            market_test_data["opts"],
            ctrb_ms_pkg_prep=[],
            tsv_data_nonfs=None,
        )
        dict_check(
            measure.markets["Technical potential"]["master_mseg"],
            market_test_data["ok_tpmeas_partchk_msegout"][idx],
        )


def test_mseg_ok_part_map(market_test_data):
    """Test 'fill_mkts' function given valid inputs.

    Notes:
        Checks the 'master_mseg' branch of measure 'markets' attribute
        under a Max adoption potential scenario.

    Raises:
        AssertionError: If function yields unexpected results.
    """
    # Run function on all measure objects and check for correct
    # output
    for idx, measure in enumerate(market_test_data["ok_mapmeas_partchk_in"]):
        measure.fill_mkts(
            market_test_data["sample_mseg_in"],
            market_test_data["sample_cpl_in"],
            market_test_data["convert_data"],
            market_test_data["tsv_data"],
            market_test_data["opts"],
            ctrb_ms_pkg_prep=[],
            tsv_data_nonfs=None,
        )
        dict_check(
            measure.markets["Max adoption potential"]["master_mseg"],
            market_test_data["ok_mapmas_partchck_msegout"][idx],
        )


def test_mseg_ok_distrib(market_test_data):
    """Test 'fill_mkts' function given valid inputs.

    Notes:
        Valid input measures are assigned distributions on
        their cost, performance, and/or lifetime attributes.

    Raises:
        AssertionError: If function yields unexpected results.
    """
    # Seed random number generator to yield repeatable cost, performance
    # and lifetime results
    numpy.random.seed(1234)
    for idx, measure in enumerate(market_test_data["ok_distmeas_in"]):
        # Generate lists of energy and cost output values
        measure.fill_mkts(
            market_test_data["sample_mseg_in"],
            market_test_data["sample_cpl_in"],
            market_test_data["convert_data"],
            market_test_data["tsv_data"],
            market_test_data["opts"],
            ctrb_ms_pkg_prep=[],
            tsv_data_nonfs=None,
        )
        test_outputs = measure.markets["Technical potential"]["master_mseg"]
        test_e = test_outputs["energy"]["total"]["efficient"]["2009"]
        test_c = test_outputs["cost"]["stock"]["total"]["efficient"]["2009"]
        test_l = test_outputs["lifetime"]["measure"]
        test_r = measure.retro_rate
        test_e, test_c, test_l, test_r = [
            [x] if type(x) is float else x for x in [test_e, test_c, test_l, test_r]
        ]
        # Calculate mean values from output lists for testing
        param_e = round(sum(test_e) / len(test_e), 2)
        param_c = round(sum(test_c) / len(test_c), 2)
        param_l = round(sum(test_l) / len(test_l), 2)
        param_r = {}
        for ind, k in enumerate(test_r.keys()):
            # Pull out the retrofit rate value; find mean value for cases
            # with a distribution of values
            if not isinstance(test_r[k], float):
                # Pull out the length of the first year's retrofit value
                if ind == 0:
                    len_test_r = len(test_r[k])
                param_r[k] = round(sum(test_r[k]) / len(test_r[k]), 2)
            else:
                # Case where retrofit value is a float of length 1
                if ind == 0:
                    len_test_r = 1
                param_r[k] = test_r[k]

        # Check mean values and length of output lists to ensure
        # correct
        assert [
            param_e,
            len(test_e),
            param_c,
            len(test_c),
            param_l,
            len(test_l),
            param_r,
            len_test_r,
        ] == market_test_data["ok_distmeas_out"][idx]


def test_mseg_sitechk(market_test_data):
    """Test 'fill_mkts' function given site energy output.

    Raises:
        AssertionError: If function yields unexpected results.
    """
    # Run function on all measure objects and check output
    for idx, measure in enumerate(market_test_data["ok_tpmeas_sitechk_in"]):
        measure.fill_mkts(
            market_test_data["sample_mseg_in"],
            market_test_data["sample_cpl_in"],
            market_test_data["convert_data"],
            market_test_data["tsv_data"],
            market_test_data["opts_site_energy"],
            ctrb_ms_pkg_prep=[],
            tsv_data_nonfs=None,
        )
        dict_check(
            measure.markets["Technical potential"]["master_mseg"],
            market_test_data["ok_tpmeas_sitechk_msegout"][idx],
        )


def test_mseg_partial(market_test_data):
    """Test 'fill_mkts' function given partially valid inputs.

    Raises:
        AssertionError: If function yields unexpected results.
    """
    # Run function on all measure objects and check output
    for idx, measure in enumerate(market_test_data["ok_partialmeas_in"]):
        measure.fill_mkts(
            market_test_data["sample_mseg_in"],
            market_test_data["sample_cpl_in"],
            market_test_data["convert_data"],
            market_test_data["tsv_data"],
            market_test_data["opts"],
            ctrb_ms_pkg_prep=[],
            tsv_data_nonfs=None,
        )
        dict_check(
            measure.markets["Technical potential"]["master_mseg"],
            market_test_data["ok_partialmeas_out"][idx],
        )
