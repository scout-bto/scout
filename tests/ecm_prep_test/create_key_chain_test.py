#!/usr/bin/env python3

"""Tests for CreateKeyChainTest"""

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
    sample_measure = {
        "name": "sample measure 2",
        "active": 1,
        "market_entry_year": None,
        "market_exit_year": None,
        "markets": None,
        "installed_cost": 25,
        "cost_units": "2014$/unit",
        "energy_efficiency": 0.5,
        "energy_efficiency_units": "relative savings (constant)",
        "market_scaling_fractions": None,
        "market_scaling_fractions_source": None,
        "measure_type": "full service",
        "structure_type": ["new", "existing"],
        "climate_zone": ["AIA_CZ1", "AIA_CZ2"],
        "bldg_type": "single family home",
        "fuel_type": {"primary": "electricity", "secondary": "electricity"},
        "fuel_switch_to": None,
        "end_use": {"primary": ["heating", "cooling"], "secondary": "lighting"},
        "technology": {
            "primary": ["resistance heat", "ASHP", "GSHP", "room AC"],
            "secondary": "general service (LED)",
        },
        "mseg_adjust": {
            "contributing mseg keys and values": {},
            "competed choice parameters": {},
            "secondary mseg adjustments": {
                "sub-market": {"original energy (total)": {}, "adjusted energy (sub-market)": {}},
                "stock-and-flow": {
                    "original energy (total)": {},
                    "adjusted energy (previously captured)": {},
                    "adjusted energy (competed)": {},
                    "adjusted energy (competed and captured)": {},
                },
                "market share": {
                    "original energy (total captured)": {},
                    "original energy (competed and captured)": {},
                    "adjusted energy (total captured)": {},
                    "adjusted energy (competed and captured)": {},
                },
            },
        },
    }
    sample_measure_in = Measure(base_dir, handyvars, handyfiles, opts_dict, **sample_measure)
    # Finalize the measure's 'technology_type' attribute (handled by the
    # 'fill_attr' function, which is not run as part of this test)
    sample_measure_in.technology_type = {"primary": "supply", "secondary": "supply"}
    ok_out_primary = [
        (
            "primary",
            "AIA_CZ1",
            "single family home",
            "electricity",
            "heating",
            "supply",
            "resistance heat",
            "new",
        ),
        (
            "primary",
            "AIA_CZ1",
            "single family home",
            "electricity",
            "heating",
            "supply",
            "ASHP",
            "new",
        ),
        (
            "primary",
            "AIA_CZ1",
            "single family home",
            "electricity",
            "heating",
            "supply",
            "GSHP",
            "new",
        ),
        (
            "primary",
            "AIA_CZ1",
            "single family home",
            "electricity",
            "heating",
            "supply",
            "room AC",
            "new",
        ),
        (
            "primary",
            "AIA_CZ1",
            "single family home",
            "electricity",
            "cooling",
            "supply",
            "resistance heat",
            "new",
        ),
        (
            "primary",
            "AIA_CZ1",
            "single family home",
            "electricity",
            "cooling",
            "supply",
            "ASHP",
            "new",
        ),
        (
            "primary",
            "AIA_CZ1",
            "single family home",
            "electricity",
            "cooling",
            "supply",
            "GSHP",
            "new",
        ),
        (
            "primary",
            "AIA_CZ1",
            "single family home",
            "electricity",
            "cooling",
            "supply",
            "room AC",
            "new",
        ),
        (
            "primary",
            "AIA_CZ2",
            "single family home",
            "electricity",
            "heating",
            "supply",
            "resistance heat",
            "new",
        ),
        (
            "primary",
            "AIA_CZ2",
            "single family home",
            "electricity",
            "heating",
            "supply",
            "ASHP",
            "new",
        ),
        (
            "primary",
            "AIA_CZ2",
            "single family home",
            "electricity",
            "heating",
            "supply",
            "GSHP",
            "new",
        ),
        (
            "primary",
            "AIA_CZ2",
            "single family home",
            "electricity",
            "heating",
            "supply",
            "room AC",
            "new",
        ),
        (
            "primary",
            "AIA_CZ2",
            "single family home",
            "electricity",
            "cooling",
            "supply",
            "resistance heat",
            "new",
        ),
        (
            "primary",
            "AIA_CZ2",
            "single family home",
            "electricity",
            "cooling",
            "supply",
            "ASHP",
            "new",
        ),
        (
            "primary",
            "AIA_CZ2",
            "single family home",
            "electricity",
            "cooling",
            "supply",
            "GSHP",
            "new",
        ),
        (
            "primary",
            "AIA_CZ2",
            "single family home",
            "electricity",
            "cooling",
            "supply",
            "room AC",
            "new",
        ),
        (
            "primary",
            "AIA_CZ1",
            "single family home",
            "electricity",
            "heating",
            "supply",
            "resistance heat",
            "existing",
        ),
        (
            "primary",
            "AIA_CZ1",
            "single family home",
            "electricity",
            "heating",
            "supply",
            "ASHP",
            "existing",
        ),
        (
            "primary",
            "AIA_CZ1",
            "single family home",
            "electricity",
            "heating",
            "supply",
            "GSHP",
            "existing",
        ),
        (
            "primary",
            "AIA_CZ1",
            "single family home",
            "electricity",
            "heating",
            "supply",
            "room AC",
            "existing",
        ),
        (
            "primary",
            "AIA_CZ1",
            "single family home",
            "electricity",
            "cooling",
            "supply",
            "resistance heat",
            "existing",
        ),
        (
            "primary",
            "AIA_CZ1",
            "single family home",
            "electricity",
            "cooling",
            "supply",
            "ASHP",
            "existing",
        ),
        (
            "primary",
            "AIA_CZ1",
            "single family home",
            "electricity",
            "cooling",
            "supply",
            "GSHP",
            "existing",
        ),
        (
            "primary",
            "AIA_CZ1",
            "single family home",
            "electricity",
            "cooling",
            "supply",
            "room AC",
            "existing",
        ),
        (
            "primary",
            "AIA_CZ2",
            "single family home",
            "electricity",
            "heating",
            "supply",
            "resistance heat",
            "existing",
        ),
        (
            "primary",
            "AIA_CZ2",
            "single family home",
            "electricity",
            "heating",
            "supply",
            "ASHP",
            "existing",
        ),
        (
            "primary",
            "AIA_CZ2",
            "single family home",
            "electricity",
            "heating",
            "supply",
            "GSHP",
            "existing",
        ),
        (
            "primary",
            "AIA_CZ2",
            "single family home",
            "electricity",
            "heating",
            "supply",
            "room AC",
            "existing",
        ),
        (
            "primary",
            "AIA_CZ2",
            "single family home",
            "electricity",
            "cooling",
            "supply",
            "resistance heat",
            "existing",
        ),
        (
            "primary",
            "AIA_CZ2",
            "single family home",
            "electricity",
            "cooling",
            "supply",
            "ASHP",
            "existing",
        ),
        (
            "primary",
            "AIA_CZ2",
            "single family home",
            "electricity",
            "cooling",
            "supply",
            "GSHP",
            "existing",
        ),
        (
            "primary",
            "AIA_CZ2",
            "single family home",
            "electricity",
            "cooling",
            "supply",
            "room AC",
            "existing",
        ),
    ]
    ok_out_secondary = [
        (
            "secondary",
            "AIA_CZ1",
            "single family home",
            "electricity",
            "lighting",
            "general service (LED)",
            "new",
        ),
        (
            "secondary",
            "AIA_CZ2",
            "single family home",
            "electricity",
            "lighting",
            "general service (LED)",
            "new",
        ),
        (
            "secondary",
            "AIA_CZ1",
            "single family home",
            "electricity",
            "lighting",
            "general service (LED)",
            "existing",
        ),
        (
            "secondary",
            "AIA_CZ2",
            "single family home",
            "electricity",
            "lighting",
            "general service (LED)",
            "existing",
        ),
    ]

    return {
        "sample_measure_in": sample_measure_in,
        "ok_out_primary": ok_out_primary,
        "ok_out_secondary": ok_out_secondary,
    }


def test_primary(test_data):
    """Test 'create_keychain' function given valid inputs.

    Note:
        Tests generation of primary microsegment key chains.

    Raises:
        AssertionError: If function yields unexpected results.
    """
    assert (
        test_data["sample_measure_in"].create_keychain("primary")[0] == test_data["ok_out_primary"]
    )


# Test the generation of a list of secondary mseg key chains


def test_secondary(test_data):
    """Test 'create_keychain' function given valid inputs.

    Note:
        Tests generation of secondary microsegment key chains.

    Raises:
        AssertionError: If function yields unexpected results.
    """
    assert (
        test_data["sample_measure_in"].create_keychain("secondary")[0]
        == test_data["ok_out_secondary"]
    )
