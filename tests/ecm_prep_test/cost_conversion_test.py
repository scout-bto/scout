#!/usr/bin/env python3

"""Tests for CostConversionTest"""

from scout.ecm_prep import Measure
from scout.ecm_prep_vars import UsefulVars, UsefulInputFiles
import pytest
import numpy
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
    # Hardcode AEO years – first year in AEO time horizon (which is set
    # to the current year in actual runs of ecm_prep) is the
    # year that cost conversion assumes when no year is given in measure
    # or baseline cost units
    handyvars.aeo_years = ["2016", "2017", "2018", "2019", "2020"]
    # Set sample consumer price index data to ensure the test is not
    # dependent on any external price data files
    handyvars.consumer_price_ind = numpy.array(
        [
            ("2008-01-01", 211.398),
            ("2008-02-01", 211.398),
            ("2008-03-01", 211.398),
            ("2008-04-01", 211.398),
            ("2008-05-01", 211.398),
            ("2008-06-01", 211.398),
            ("2008-07-01", 211.398),
            ("2008-08-01", 211.398),
            ("2008-09-01", 211.398),
            ("2008-10-01", 211.398),
            ("2008-11-01", 211.398),
            ("2008-12-01", 211.398),
            ("2009-01-01", 217.347),
            ("2009-02-01", 217.347),
            ("2009-03-01", 217.347),
            ("2009-04-01", 217.347),
            ("2009-05-01", 217.347),
            ("2009-06-01", 217.347),
            ("2009-07-01", 217.347),
            ("2009-08-01", 217.347),
            ("2009-09-01", 217.347),
            ("2009-10-01", 217.347),
            ("2009-11-01", 217.347),
            ("2009-12-01", 217.347),
            ("2010-01-01", 220.472),
            ("2010-02-01", 220.472),
            ("2010-03-01", 220.472),
            ("2010-04-01", 220.472),
            ("2010-05-01", 220.472),
            ("2010-06-01", 220.472),
            ("2010-07-01", 220.472),
            ("2010-08-01", 220.472),
            ("2010-09-01", 220.472),
            ("2010-10-01", 220.472),
            ("2010-11-01", 220.472),
            ("2010-12-01", 220.472),
            ("2011-01-01", 227.223),
            ("2011-02-01", 227.223),
            ("2011-03-01", 227.223),
            ("2011-04-01", 227.223),
            ("2011-05-01", 227.223),
            ("2011-06-01", 227.223),
            ("2011-07-01", 227.223),
            ("2011-08-01", 227.223),
            ("2011-09-01", 227.223),
            ("2011-10-01", 227.223),
            ("2011-11-01", 227.223),
            ("2011-12-01", 227.223),
            ("2012-01-01", 231.272),
            ("2012-02-01", 231.272),
            ("2012-03-01", 231.272),
            ("2012-04-01", 231.272),
            ("2012-05-01", 231.272),
            ("2012-06-01", 231.272),
            ("2012-07-01", 231.272),
            ("2012-08-01", 231.272),
            ("2012-09-01", 231.272),
            ("2012-10-01", 231.272),
            ("2012-11-01", 231.272),
            ("2012-12-01", 231.272),
            ("2013-01-01", 234.847),
            ("2013-02-01", 234.847),
            ("2013-03-01", 234.847),
            ("2013-04-01", 234.847),
            ("2013-05-01", 234.847),
            ("2013-06-01", 234.847),
            ("2013-07-01", 234.847),
            ("2013-08-01", 234.847),
            ("2013-09-01", 234.847),
            ("2013-10-01", 234.847),
            ("2013-11-01", 234.847),
            ("2013-12-01", 234.847),
            ("2014-01-01", 236.464),
            ("2014-02-01", 236.464),
            ("2014-03-01", 236.464),
            ("2014-04-01", 236.464),
            ("2014-05-01", 236.464),
            ("2014-06-01", 236.464),
            ("2014-07-01", 236.464),
            ("2014-08-01", 236.464),
            ("2014-09-01", 236.464),
            ("2014-10-01", 236.464),
            ("2014-11-01", 236.464),
            ("2014-12-01", 236.464),
            ("2015-01-01", 238.041),
            ("2015-02-01", 238.041),
            ("2015-03-01", 238.041),
            ("2015-04-01", 238.041),
            ("2015-05-01", 238.041),
            ("2015-06-01", 238.041),
            ("2015-07-01", 238.041),
            ("2015-08-01", 238.041),
            ("2015-09-01", 238.041),
            ("2015-10-01", 238.041),
            ("2015-11-01", 238.041),
            ("2015-12-01", 238.041),
            ("2016-01-01", 239.41),
            ("2016-02-01", 239.41),
            ("2016-03-01", 239.41),
            ("2016-04-01", 239.41),
            ("2016-05-01", 239.41),
        ],
        dtype=[("DATE", "<U50"), ("VALUE", "<f8")],
    )

    sample_measure_in = {
        "name": "sample measure cost convert",
        "remove": False,
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
        "bldg_type": ["single family home"],
        "fuel_type": {"primary": ["electricity"], "secondary": ["electricity"]},
        "fuel_switch_to": None,
        "end_use": {"primary": ["heating", "cooling"], "secondary": ["lighting"]},
        "technology": {
            "primary": ["resistance heat", "ASHP", "GSHP", "room AC"],
            "secondary": ["general service (LED)"],
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
    verbose = None
    sample_measure_in = Measure(base_dir, handyvars, handyfiles, opts_dict, **sample_measure_in)
    sample_convertdata_ok_in = {
        "building type conversions": {
            "original type": "EnergyPlus reference buildings",
            "revised type": "Annual Energy Outlook (AEO) buildings",
            "conversion data": {
                "description": "sample",
                "value": {
                    "residential": {
                        "single family home": {"Single-Family": 1},
                        "mobile home": {"Single-Family": 1},
                        "multi family home": {"Multifamily": 1},
                    },
                    "commercial": {
                        "assembly": {"Hospital": 1},
                        "education": {"PrimarySchool": 0.26, "SecondarySchool": 0.74},
                        "food sales": {"Supermarket": 1},
                        "food service": {
                            "QuickServiceRestaurant": 0.31,
                            "FullServiceRestaurant": 0.69,
                        },
                        "health care": None,
                        "lodging": {"SmallHotel": 0.26, "LargeHotel": 0.74},
                        "large office": {"LargeOffice": 0.9, "MediumOfficeDetailed": 0.1},
                        "small office": {"SmallOffice": 0.12, "OutpatientHealthcare": 0.88},
                        "mercantile/service": {"RetailStandalone": 0.53, "RetailStripmall": 0.47},
                        "warehouse": {"Warehouse": 1},
                        "other": None,
                    },
                },
                "source": {"residential": "sample", "commercial": "sample"},
                "notes": {"residential": "sample", "commercial": "sample"},
            },
        },
        "cost unit conversions": {
            "whole building": {
                "wireless sensor network": {
                    "original units": "$/node",
                    "revised units": "$/ft^2 floor",
                    "conversion factor": {
                        "description": "sample",
                        "value": {
                            "residential": {
                                "single family home": 0.0021,
                                "mobile home": 0.0021,
                                "multi family home": 0.0041,
                            },
                            "commercial": 0.002,
                        },
                        "units": "nodes/ft^2 floor",
                        "source": {"residential": "sample", "commercial": "sample"},
                        "notes": "sample",
                    },
                },
                "occupant-centered sensing and controls": {
                    "original units": "$/occupant",
                    "revised units": "$/ft^2 floor",
                    "conversion factor": {
                        "description": "sample",
                        "value": {
                            "residential": {
                                "single family home": {"Single-Family": 0.001075},
                                "mobile home": {"Single-Family": 0.001075},
                                "multi family home": {"Multifamily": 0.00215},
                            },
                            "commercial": {
                                "assembly": {"Hospital": 0.005},
                                "education": {"PrimarySchool": 0.02, "SecondarySchool": 0.02},
                                "food sales": {"Supermarket": 0.008},
                                "food service": {
                                    "QuickServiceRestaurant": 0.07,
                                    "FullServiceRestaurant": 0.07,
                                },
                                "health care": 0.005,
                                "lodging": {"SmallHotel": 0.005, "LargeHotel": 0.005},
                                "large office": {
                                    "LargeOffice": 0.005,
                                    "MediumOfficeDetailed": 0.005,
                                },
                                "small office": {
                                    "SmallOffice": 0.005,
                                    "OutpatientHealthcare": 0.02,
                                },
                                "mercantile/service": {
                                    "RetailStandalone": 0.01,
                                    "RetailStripmall": 0.01,
                                },
                                "warehouse": {"Warehouse": 0.0001},
                                "other": 0.005,
                            },
                        },
                        "units": "occupants/ft^2 floor",
                        "source": {"residential": "sample", "commercial": "sample"},
                        "notes": "",
                    },
                },
            },
            "heating and cooling": {
                "supply": {
                    "heating equipment": {
                        "original units": "$/kBtu/h heating",
                        "revised units": "$/ft^2 floor",
                        "conversion factor": {
                            "description": "sample",
                            "value": 0.020,
                            "units": "kBtu/h heating/ft^2 floor",
                            "source": "Rule of thumb",
                            "notes": "sample",
                        },
                    },
                    "cooling equipment": {
                        "original units": "$/kBtu/h cooling",
                        "revised units": "$/ft^2 floor",
                        "conversion factor": {
                            "description": "sample",
                            "value": 0.036,
                            "units": "kBtu/h cooling/ft^2 floor",
                            "source": "Rule of thumb",
                            "notes": "sample",
                        },
                    },
                },
                "demand": {
                    "windows": {
                        "original units": "$/ft^2 glazing",
                        "revised units": "$/ft^2 wall",
                        "conversion factor": {
                            "description": "Window to wall ratio",
                            "value": {
                                "residential": {
                                    "single family home": {"Single-Family": 0.15},
                                    "mobile home": {"Single-Family": 0.15},
                                    "multi family home": {"Multifamily": 0.10},
                                },
                                "commercial": {
                                    "assembly": {"Hospital": 0.15},
                                    "education": {"PrimarySchool": 0.35, "SecondarySchool": 0.33},
                                    "food sales": {"Supermarket": 0.11},
                                    "food service": {
                                        "QuickServiceRestaurant": 0.14,
                                        "FullServiceRestaurant": 0.17,
                                    },
                                    "health care": 0.2,
                                    "lodging": {"SmallHotel": 0.11, "LargeHotel": 0.27},
                                    "large office": {
                                        "LargeOffice": 0.38,
                                        "MediumOfficeDetailed": 0.33,
                                    },
                                    "small office": {
                                        "SmallOffice": 0.21,
                                        "OutpatientHealthcare": 0.19,
                                    },
                                    "mercantile/service": {
                                        "RetailStandalone": 0.07,
                                        "RetailStripmall": 0.11,
                                    },
                                    "warehouse": {"Warehouse": 0.006},
                                    "other": 0.2,
                                },
                            },
                            "units": None,
                            "source": {"residential": "sample", "commercial": "sample"},
                            "notes": "sample",
                        },
                    },
                    "walls": {
                        "original units": "$/ft^2 wall",
                        "revised units": "$/ft^2 floor",
                        "conversion factor": {
                            "description": "Wall to floor ratio",
                            "value": {
                                "residential": {
                                    "single family home": {"Single-Family": 1},
                                    "mobile home": {"Single-Family": 1},
                                    "multi family home": {"Multifamily": 1},
                                },
                                "commercial": {
                                    "assembly": {"Hospital": 0.26},
                                    "education": {"PrimarySchool": 0.20, "SecondarySchool": 0.16},
                                    "food sales": {"Supermarket": 0.38},
                                    "food service": {
                                        "QuickServiceRestaurant": 0.80,
                                        "FullServiceRestaurant": 0.54,
                                    },
                                    "health care": 0.4,
                                    "lodging": {"SmallHotel": 0.40, "LargeHotel": 0.38},
                                    "large office": {
                                        "LargeOffice": 0.26,
                                        "MediumOfficeDetailed": 0.40,
                                    },
                                    "small office": {
                                        "SmallOffice": 0.55,
                                        "OutpatientHealthcare": 0.35,
                                    },
                                    "mercantile/service": {
                                        "RetailStandalone": 0.51,
                                        "RetailStripmall": 0.57,
                                    },
                                    "warehouse": {"Warehouse": 0.53},
                                    "other": 0.4,
                                },
                            },
                            "units": None,
                            "source": {"residential": "sample", "commercial": "sample"},
                            "notes": "sample",
                        },
                    },
                    "footprint": {
                        "original units": "$/ft^2 footprint",
                        "revised units": "$/ft^2 floor",
                        "conversion factor": {
                            "description": "sample",
                            "value": {
                                "residential": {
                                    "single family home": {"Single-Family": 0.5},
                                    "mobile home": {"Single-Family": 0.5},
                                    "multi family home": {"Multifamily": 0.33},
                                },
                                "commercial": {
                                    "assembly": {"Hospital": 0.20},
                                    "education": {"PrimarySchool": 1, "SecondarySchool": 0.5},
                                    "food sales": {"Supermarket": 1},
                                    "food service": {
                                        "QuickServiceRestaurant": 1,
                                        "FullServiceRestaurant": 1,
                                    },
                                    "health care": 0.2,
                                    "lodging": {"SmallHotel": 0.25, "LargeHotel": 0.17},
                                    "large office": {
                                        "LargeOffice": 0.083,
                                        "MediumOfficeDetailed": 0.33,
                                    },
                                    "small office": {
                                        "SmallOffice": 1,
                                        "OutpatientHealthcare": 0.33,
                                    },
                                    "mercantile/service": {
                                        "RetailStandalone": 1,
                                        "RetailStripmall": 1,
                                    },
                                    "warehouse": {"Warehouse": 1},
                                    "other": 1,
                                },
                            },
                            "units": None,
                            "source": {"residential": "sample", "commercial": "sample"},
                            "notes": "sample",
                        },
                    },
                    "roof": {
                        "original units": "$/ft^2 roof",
                        "revised units": "$/ft^2 footprint",
                        "conversion factor": {
                            "description": "sample",
                            "value": {"residential": 1.05, "commercial": 1},
                            "units": None,
                            "source": "Rule of thumb",
                            "notes": "sample",
                        },
                    },
                },
            },
            "ventilation": {
                "original units": "$/1000 CFM",
                "revised units": "$/ft^2 floor",
                "conversion factor": {
                    "description": "sample",
                    "value": 0.001,
                    "units": "1000 CFM/ft^2 floor",
                    "source": "Rule of thumb",
                    "notes": "sample",
                },
            },
            "lighting": {
                "original units": "$/1000 lm",
                "revised units": "$/ft^2 floor",
                "conversion factor": {
                    "description": "sample",
                    "value": 0.049,
                    "units": "1000 lm/ft^2 floor",
                    "source": "sample",
                    "notes": "sample",
                },
            },
            "water heating": {
                "original units": "$/kBtu/h water heating",
                "revised units": "$/ft^2 floor",
                "conversion factor": {
                    "description": "sample",
                    "value": 0.012,
                    "units": "kBtu/h water heating/ft^2 floor",
                    "source": "sample",
                    "notes": "sample",
                },
            },
            "refrigeration": {
                "original units": "$/kBtu/h refrigeration",
                "revised units": "$/ft^2 floor",
                "conversion factor": {
                    "description": "sample",
                    "value": 0.02,
                    "units": "kBtu/h refrigeration/ft^2 floor",
                    "source": "sample",
                    "notes": "sample",
                },
            },
            "cooking": {},
            "MELs": {},
        },
    }
    sample_bldgsect_ok_in = [
        "residential",
        "commercial",
        "commercial",
        "commercial",
        "commercial",
        "commercial",
        "commercial",
        "commercial",
        "residential",
    ]
    sample_mskeys_ok_in = [
        (
            "primary",
            "marine",
            "single family home",
            "electricity",
            "cooling",
            "demand",
            "windows conduction",
            "existing",
        ),
        (
            "primary",
            "marine",
            "assembly",
            "electricity",
            "heating",
            "supply",
            "rooftop_ASHP-heat",
            "new",
        ),
        ("primary", "marine", "food sales", "electricity", "cooling", "demand", "ground", "new"),
        ("primary", "marine", "education", "electricity", "cooling", "demand", "roof", "existing"),
        ("primary", "marine", "lodging", "electricity", "cooling", "demand", "wall", "new"),
        ("primary", "marine", "food service", "electricity", "ventilation", "CAV_Vent", "existing"),
        (
            "primary",
            "mixed humid",
            "health care",
            "electricity",
            "cooling",
            "demand",
            "roof",
            "existing",
        ),
        ("primary", "marine", "food service", "electricity", "ventilation", "CAV_Vent", "existing"),
        (
            "primary",
            "marine",
            "single family home",
            "electricity",
            "cooling",
            "demand",
            "windows conduction",
            "existing",
        ),
    ]
    sample_mskeys_fail_in = [
        (
            "primary",
            "marine",
            "single family home",
            "electricity",
            "cooling",
            "demand",
            "windows conduction",
            "existing",
        ),
        ("primary", "marine", "assembly", "electricity", "PCs", None, "new"),
        (
            "primary",
            "marine",
            "assembly",
            "electricity",
            "heating",
            "supply",
            "rooftop_ASHP-heat",
            "new",
        ),
        (
            "primary",
            "marine",
            "assembly",
            "electricity",
            "heating",
            "supply",
            "rooftop_ASHP-heat",
            "new",
        ),
    ]
    cost_meas_ok_in = 10
    cost_meas_units_ok_in_yronly = "2008$/ft^2 floor"
    cost_meas_units_ok_in_all = [
        "$/ft^2 glazing",
        "2013$/ft^2 floor",
        "2010$/ft^2 footprint",
        "2016$/ft^2 roof",
        "2013$/ft^2 wall",
        "2010$/ft^2 floor",
        "2013$/ft^2 roof",
        "2017$/ft^2 floor",
        "2010$/ft^2 floor",
    ]
    cost_meas_units_fail_in = ["$/ft^2 facade", "$/kWh", "$/occupant", "$/node"]
    cost_base_units_fail_in = [
        "2013$/ft^2 floor",
        "2013$/kBtu/h heating",
        "2017$/kBtu/h cooling",
        "2017$/1000 lm",
    ]
    cost_base_units_ok_in = [
        "$/ft^2 floor",
        "2013$/kBtu/h heating",
        "2010$/ft^2 floor",
        "2016$/ft^2 floor",
        "2013$/ft^2 floor",
        "2012$/1000 CFM",
        "2013$/ft^2 floor",
        "2017$/1000 CFM",
        "$/unit",
    ]
    cost_meas_units_ok_out = [
        "2016$/ft^2 floor",
        "2013$/kBtu/h heating",
        "2010$/ft^2 floor",
        "2016$/ft^2 floor",
        "2013$/ft^2 floor",
        "2012$/1000 CFM",
        "2013$/ft^2 floor",
        "2017$/1000 CFM",
        "2016$/ft^2 floor",
    ]
    ok_out_costs_yronly = 11.325  # last row in 2016 vs. last row 2008
    ok_out_costs_all = [1.5, 500, 10, 6.3, 3.85, 10489.86, 2, 10000, 10.85898]

    return {
        "verbose": verbose,
        "sample_measure_in": sample_measure_in,
        "sample_convertdata_ok_in": sample_convertdata_ok_in,
        "sample_bldgsect_ok_in": sample_bldgsect_ok_in,
        "sample_mskeys_ok_in": sample_mskeys_ok_in,
        "sample_mskeys_fail_in": sample_mskeys_fail_in,
        "cost_meas_ok_in": cost_meas_ok_in,
        "cost_meas_units_ok_in_yronly": cost_meas_units_ok_in_yronly,
        "cost_meas_units_ok_in_all": cost_meas_units_ok_in_all,
        "cost_meas_units_fail_in": cost_meas_units_fail_in,
        "cost_base_units_fail_in": cost_base_units_fail_in,
        "cost_base_units_ok_in": cost_base_units_ok_in,
        "cost_meas_units_ok_out": cost_meas_units_ok_out,
        "ok_out_costs_yronly": ok_out_costs_yronly,
        "ok_out_costs_all": ok_out_costs_all,
    }


def test_convertcost_ok_yronly(test_data):
    """Test 'convert_costs' function for year only conversion."""
    func_output = test_data["sample_measure_in"].convert_costs(
        test_data["sample_convertdata_ok_in"],
        test_data["sample_bldgsect_ok_in"][0],
        test_data["sample_mskeys_ok_in"][0],
        test_data["cost_meas_ok_in"],
        test_data["cost_meas_units_ok_in_yronly"],
        test_data["cost_base_units_ok_in"][0],
        test_data["verbose"],
    )
    numpy.testing.assert_almost_equal(func_output[0], test_data["ok_out_costs_yronly"], decimal=2)
    assert func_output[1] == test_data["cost_meas_units_ok_out"][0]


def test_convertcost_ok_all(test_data):
    """Test 'convert_costs' function for year/units conversion."""
    for k in range(0, len(test_data["sample_mskeys_ok_in"])):
        func_output = test_data["sample_measure_in"].convert_costs(
            test_data["sample_convertdata_ok_in"],
            test_data["sample_bldgsect_ok_in"][k],
            test_data["sample_mskeys_ok_in"][k],
            test_data["cost_meas_ok_in"],
            test_data["cost_meas_units_ok_in_all"][k],
            test_data["cost_base_units_ok_in"][k],
            test_data["verbose"],
        )
        numpy.testing.assert_almost_equal(
            func_output[0], test_data["ok_out_costs_all"][k], decimal=2
        )
        assert func_output[1] == test_data["cost_meas_units_ok_out"][k]


def test_convertcost_fail(test_data):
    """Test 'convert_costs' function given invalid inputs."""
    for k in range(0, len(test_data["sample_mskeys_fail_in"])):
        with pytest.raises(KeyError):
            test_data["sample_measure_in"].convert_costs(
                test_data["sample_convertdata_ok_in"],
                test_data["sample_bldgsect_ok_in"][k],
                test_data["sample_mskeys_fail_in"][k],
                test_data["cost_meas_ok_in"],
                test_data["cost_meas_units_fail_in"][k],
                test_data["cost_base_units_fail_in"][k],
                test_data["verbose"],
            )
