#!/usr/bin/env python3

"""Tests for AddKeyValsTest"""

from scout.ecm_prep import Measure
from scout.ecm_prep_vars import UsefulVars, UsefulInputFiles
import pytest
import os
import copy
from tests.ecm_prep_test.common import NullOpts, dict_check


@pytest.fixture(scope="module")
def test_data():
    """Fixture providing test data."""
    # Base directory
    base_dir = os.getcwd()
    # Null user options/options dict
    opts, opts_dict = [NullOpts().opts, NullOpts().opts_dict]
    handyfiles = UsefulInputFiles(opts)
    handyvars = UsefulVars(base_dir, handyfiles, opts)
    sample_measure_in = {
        "name": "sample measure 1",
        "active": 1,
        "market_entry_year": None,
        "market_exit_year": None,
        "market_scaling_fractions": None,
        "market_scaling_fractions_source": None,
        "measure_type": "full service",
        "structure_type": ["new", "existing"],
        "climate_zone": ["AIA_CZ1", "AIA_CZ2"],
        "bldg_type": ["single family home"],
        "fuel_type": {"primary": ["electricity"], "secondary": None},
        "fuel_switch_to": None,
        "end_use": {"primary": ["heating", "cooling"], "secondary": None},
        "technology": {
            "primary": ["resistance heat", "ASHP", "GSHP", "room AC"],
            "secondary": None,
        },
    }
    sample_measure_in = Measure(base_dir, handyvars, handyfiles, opts_dict, **sample_measure_in)
    ok_dict1_in, ok_dict2_in = (
        {
            "level 1a": {"level 2aa": {"2009": 2, "2010": 3}, "level 2ab": {"2009": 4, "2010": 5}},
            "level 1b": {"level 2ba": {"2009": 6, "2010": 7}, "level 2bb": {"2009": 8, "2010": 9}},
        }
        for n in range(2)
    )
    ok_dict3_in, ok_dict4_in = (
        {
            "level 1a": {"level 2aa": {"2009": 2, "2010": 3}, "level 2ab": {"2009": 4, "2010": 5}},
            "lifetime": {"level 2ba": {"2009": 6, "2010": 7}, "level 2bb": {"2009": 8, "2010": 9}},
        }
        for n in range(2)
    )
    fail_dict1_in = {
        "level 1a": {"level 2aa": {"2009": 2, "2010": 3}, "level 2ab": {"2009": 4, "2010": 5}},
        "level 1b": {"level 2ba": {"2009": 6, "2010": 7}, "level 2bb": {"2009": 8, "2010": 9}},
    }
    fail_dict2_in = {
        "level 1a": {"level 2aa": {"2009": 2, "2010": 3}, "level 2ab": {"2009": 4, "2010": 5}},
        "level 1b": {"level 2ba": {"2009": 6, "2010": 7}, "level 2bb": {"2009": 8, "2011": 9}},
    }
    ok_out = {
        "level 1a": {"level 2aa": {"2009": 4, "2010": 6}, "level 2ab": {"2009": 8, "2010": 10}},
        "level 1b": {"level 2ba": {"2009": 12, "2010": 14}, "level 2bb": {"2009": 16, "2010": 18}},
    }
    ok_out_restrict = {
        "level 1a": {"level 2aa": {"2009": 4, "2010": 6}, "level 2ab": {"2009": 8, "2010": 10}},
        "lifetime": {"level 2ba": {"2009": 6, "2010": 7}, "level 2bb": {"2009": 8, "2010": 9}},
    }
    # Test case for when dict2 has extra keys (sub-market scaling) that dict1 doesn't
    restrict_dict1_extra_keys = {
        "level 1a": {"level 2aa": {"2009": 2, "2010": 3}, "level 2ab": {"2009": 4, "2010": 5}},
        "lifetime": {"level 2ba": {"2009": 6, "2010": 7}, "level 2bb": {"2009": 8, "2010": 9}},
    }
    restrict_dict2_extra_keys = {
        "level 1a": {"level 2aa": {"2009": 2, "2010": 3}, "level 2ab": {"2009": 4, "2010": 5}},
        "lifetime": {"level 2ba": {"2009": 6, "2010": 7}, "level 2bb": {"2009": 8, "2010": 9}},
        "sub-market scaling": 0.5,
    }
    ok_out_restrict_extra_keys = {
        "level 1a": {"level 2aa": {"2009": 4, "2010": 6}, "level 2ab": {"2009": 8, "2010": 10}},
        "lifetime": {"level 2ba": {"2009": 6, "2010": 7}, "level 2bb": {"2009": 8, "2010": 9}},
    }

    return {
        "sample_measure_in": sample_measure_in,
        "ok_dict1_in": ok_dict1_in,
        "ok_dict2_in": ok_dict2_in,
        "ok_dict3_in": ok_dict3_in,
        "ok_dict4_in": ok_dict4_in,
        "fail_dict1_in": fail_dict1_in,
        "fail_dict2_in": fail_dict2_in,
        "ok_out": ok_out,
        "ok_out_restrict": ok_out_restrict,
        "restrict_dict1_extra_keys": restrict_dict1_extra_keys,
        "restrict_dict2_extra_keys": restrict_dict2_extra_keys,
        "ok_out_restrict_extra_keys": ok_out_restrict_extra_keys,
    }


def test_ok_add_keyvals(test_data):
    """Test 'add_keyvals' function given valid inputs.

    Raises:
        AssertionError: If function yields unexpected results.
    """
    dict_check(
        test_data["sample_measure_in"].add_keyvals(
            test_data["ok_dict1_in"], test_data["ok_dict2_in"]
        ),
        test_data["ok_out"],
    )


def test_fail_add_keyvals(test_data):
    """Test 'add_keyvals' function given invalid inputs.

    Raises:
        AssertionError: If KeyError is not raised.
    """
    with pytest.raises(KeyError):
        test_data["sample_measure_in"].add_keyvals(
            test_data["fail_dict1_in"], test_data["fail_dict2_in"]
        )


def test_ok_add_keyvals_restrict(test_data):
    """Test 'add_keyvals_restrict' function given valid inputs."""
    dict_check(
        test_data["sample_measure_in"].add_keyvals_restrict(
            test_data["ok_dict3_in"], test_data["ok_dict4_in"]
        ),
        test_data["ok_out_restrict"],
    )


def test_ok_add_keyvals_restrict_with_extra_keys(test_data):
    """Test 'add_keyvals_restrict' function when dict2 has extra keys like 'sub-market scaling'.

    This tests the fix for the cross-platform issue where envelope measures
    (like windows) get 'sub-market scaling' added but HVAC measures don't,
    causing merge failures when packaging.
    """
    # Use deep copies since add_keyvals_restrict modifies dict1 in place
    dict_check(
        test_data["sample_measure_in"].add_keyvals_restrict(
            copy.deepcopy(test_data["restrict_dict1_extra_keys"]),
            copy.deepcopy(test_data["restrict_dict2_extra_keys"])
        ),
        test_data["ok_out_restrict_extra_keys"],
    )
