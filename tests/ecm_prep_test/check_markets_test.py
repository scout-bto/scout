#!/usr/bin/env python3

"""Tests for CheckMarketsTest"""

from scout.ecm_prep import Measure
from scout.ecm_prep_vars import UsefulVars, UsefulInputFiles
import pytest
import os
from tests.ecm_prep_test.common import NullOpts


@pytest.fixture(scope="module")
def test_data():
    """Fixture providing test data."""
    # Base directory
    base_dir = os.getcwd()
    # Null user options/options dict
    opts, opts_dict = [NullOpts().opts, NullOpts().opts_dict]
    handyfiles = UsefulInputFiles(opts)
    handyvars = UsefulVars(base_dir, handyfiles, opts)
    sample_measures_fail = [
        {
            "name": "sample measure 5",
            "market_entry_year": None,
            "market_exit_year": None,
            "installed_cost": 999,
            "cost_units": "dummy",
            "energy_efficiency": {"primary": 999, "secondary": None},
            "energy_efficiency_units": {"primary": "dummy", "secondary": None},
            "product_lifetime": 999,
            "climate_zone": "all",
            "bldg_type": "all commercial",
            "structure_type": "all",
            "fuel_type": {"primary": ["electricity", "natty gas"], "secondary": None},
            "fuel_switch_to": None,
            "end_use": {"primary": ["heating", "water heating"], "secondary": None},
            "technology": {"primary": ["all heating", "electric WH"], "secondary": None},
        },
        {
            "name": "sample measure 6",
            "market_entry_year": None,
            "market_exit_year": None,
            "installed_cost": 999,
            "cost_units": "dummy",
            "energy_efficiency": {"primary": 999, "secondary": None},
            "energy_efficiency_units": {"primary": "dummy", "secondary": None},
            "product_lifetime": 999,
            "climate_zone": "all",
            "bldg_type": ["assembling", "education"],
            "structure_type": "all",
            "fuel_type": {"primary": "natural gas", "secondary": None},
            "fuel_switch_to": None,
            "end_use": {"primary": "heating", "secondary": None},
            "technology": {"primary": "all", "secondary": None},
        },
    ]
    sample_measures_fail = [
        Measure(base_dir, handyvars, handyfiles, opts_dict, **x) for x in sample_measures_fail
    ]

    return {
        "sample_measures_fail": sample_measures_fail,
    }


def test_invalid_mkts(test_data):
    """Test 'check_meas_inputs' function given invalid inputs."""
    for m in test_data["sample_measures_fail"]:
        with pytest.raises(Exception):
            m.check_meas_inputs()
