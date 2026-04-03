#!/usr/bin/env python3

"""Tests for Update Measures (update_results function)"""

from scout.ecm_prep import ECMPrepHelper, ECMPrep
from scout.ecm_prep_vars import UsefulVars, UsefulInputFiles
from scout.config import FilePaths as fp
import pytest
import numpy
import os
import copy
import json
import itertools
from pathlib import Path
from tests.ecm_prep_test.common import NullOpts, dict_check
from tests.ecm_prep_test.test_data.time_sensitive_valuation_test_data import (
    sample_tsv_data_update_measures as sample_tsv_data,
)
from tests.ecm_prep_test.test_data.update_measures_test_data import (
    sample_cpl_in_aia,
    sample_cpl_in_emm,
    ok_out_emm_features,
    sample_mseg_in_emm,
    ok_out_emm_metrics_mkts,
    sample_mseg_in_aia,
    base_out_2009,
    base_out_2010,
)


@pytest.fixture(scope="module")
def update_test_data():
    """Fixture providing test data for update measures tests."""
    """Define variables and objects for use across all class functions."""
    # Base directory
    base_dir = os.getcwd()
    # Null user options
    opts = NullOpts().opts
    opts_empty = copy.deepcopy(opts)
    opts_aia = copy.deepcopy(opts)
    sample_tsv_metric_settings = [False, ["2", "2", "1", "1", "2", "2"], False]
    # Reset options for EMM tests
    opts_emm = [copy.deepcopy(opts) for n in range(3)]
    for i in range(3):
        opts_emm[i].alt_regions = "EMM"
        opts_emm[i].tsv_metrics = sample_tsv_metric_settings[i]
        # Set sector shapes for 3rd example
        if i == 2:
            opts_emm[i].sect_shapes = True
    test_files = Path(__file__).parent.parent / "test_files"
    package_ecms_file = test_files / "ecm_definitions" / "package_ecms.json"
    # Reset options for health cost tests
    opts_health = [copy.deepcopy(opts)]
    opts_health[0].alt_regions = "EMM"
    opts_health[0].health_costs = True
    handyfiles_aia = UsefulInputFiles(opts_aia)
    handyfiles_emm = UsefulInputFiles(opts_emm[0])
    handyfiles_emm.ash_emm_map = fp.CONVERT_DATA / "test" / "ASH_EMM_Mapping_USAMainland.txt"
    (
        handyfiles_emm.tsv_metrics_data_tot_ref,
        handyfiles_emm.tsv_metrics_data_tot_hr,
        handyfiles_emm.tsv_metrics_data_net_ref,
        handyfiles_emm.tsv_metrics_data_net_hr,
    ) = ((fp.TSV_DATA / "test" / "tsv_hrs.csv") for n in range(4))
    handyvars_aia = UsefulVars(base_dir, handyfiles_aia, opts_aia)
    # Dummy user settings needed to generate TSV metrics data params below
    opts_tsv_dummy = copy.deepcopy(opts)
    opts_tsv_dummy.alt_regions = "EMM"
    opts_tsv_dummy.tsv_metrics = ["2", "2", "1", "1", "2", "2"]
    # Initialize TSV metrics settings for measures affecting EMM regions
    handyvars_emm = UsefulVars(base_dir, handyfiles_emm, opts_tsv_dummy)
    handyvars_emm.aeo_years_summary = ["2009", "2010"]
    handyvars_health = UsefulVars(base_dir, handyfiles_emm, opts_health[0])
    # Set dummy commercial equipment capacity factors
    cf_ones = {
        "data": {
            "assembly": {
                "heating": 1,
                "cooling": 1,
                "water heating": 1,
                "ventilation": 1,
                "cooking": 1,
                "lighting": 1,
                "refrigeration": 1,
            }
        }
    }
    # Set test capacity factors to dummy values above
    handyvars_aia.cap_facts, handyvars_emm.cap_facts, handyvars_health.cap_facts = (
        cf_ones for n in range(3)
    )
    # Develop weekend day flags
    wknd_day_flags = [0 for n in range(365)]
    current_wkdy = 1
    for d in range(365):
        # Flag weekend day
        if current_wkdy in [1, 7]:
            wknd_day_flags[d] = 1
        # Advance day of week by one unless Saturday (7), in which
        # case day switches back to 1 (Sunday)
        if current_wkdy <= 6:
            current_wkdy += 1
        else:
            current_wkdy = 1
    # Develop lists with seasonal day of year ranges, both with and
    # without weekends
    # Summer days of year
    sum_days = list(range(151, 273))
    sum_days_wkdy = [x for x in sum_days if wknd_day_flags[(x - 1)] != 1]
    sum_days_wknd = [x for x in sum_days if wknd_day_flags[(x - 1)] == 1]
    # Winter days of year
    wint_days = list(range(1, 59)) + list(range(334, 365))
    wint_days_wkdy = [x for x in wint_days if wknd_day_flags[(x - 1)] != 1]
    wint_days_wknd = [x for x in wint_days if wknd_day_flags[(x - 1)] == 1]
    # Intermediate days of year
    inter_days = list(range(59, 151)) + list(range(273, 334))
    inter_days_wkdy = [x for x in inter_days if wknd_day_flags[(x - 1)] != 1]
    inter_days_wknd = [x for x in inter_days if wknd_day_flags[(x - 1)] == 1]
    # Hard code all tsv_metrics_data except net load hours, which are
    # read in from a test CSV file
    handyvars_emm.tsv_metrics_data["season days"] = {
        "all": {"summer": sum_days, "winter": wint_days, "intermediate": inter_days},
        "weekdays": {
            "summer": sum_days_wkdy,
            "winter": wint_days_wkdy,
            "intermediate": inter_days_wkdy,
        },
        "weekends": {
            "summer": sum_days_wknd,
            "winter": wint_days_wknd,
            "intermediate": inter_days_wknd,
        },
    }
    handyvars_emm.tsv_metrics_data["peak days"] = {"summer": 270, "winter": 24}
    handyvars_emm.tsv_metrics_data["hourly index"] = list(
        enumerate(itertools.product(range(365), range(24)))
    )
    # Hard code aeo_years to fit test years
    handyvars_aia.aeo_years, handyvars_emm.aeo_years, handyvars_health.aeo_years = (
        ["2009", "2010"] for n in range(3)
    )
    handyvars_aia.retro_rate, handyvars_emm.retro_rate, handyvars_health.retro_rate = (
        {yr: 0.01 for yr in handyvars_aia.aeo_years} for n in range(3)
    )
    cbecs_sf_byvint = {
        "2004 to 2007": 6524.0,
        "1960 to 1969": 10362.0,
        "1946 to 1959": 7381.0,
        "1970 to 1979": 10846.0,
        "1990 to 1999": 13803.0,
        "2000 to 2003": 7215.0,
        "Before 1920": 3980.0,
        "2008 to 2012": 5726.0,
        "1920 to 1945": 6020.0,
        "1980 to 1989": 15185.0,
    }
    # Hard code carbon intensity, site-source conversion, and cost data for
    # tests such that these data are not dependent on an input file that
    # may change in the future; carbon intensity and cost data have a
    # different structure (broken out by region) when EMM regions are
    # used for the analysis; reflect this in the test data accordingly
    handyvars_aia.ss_conv, handyvars_emm.ss_conv, handyvars_health.ss_conv = (
        {
            "electricity": {"2009": 3.19, "2010": 3.20},
            "natural gas": {"2009": 1.01, "2010": 1.01},
            "distillate": {"2009": 1.01, "2010": 1.01},
            "other fuel": {"2009": 1.01, "2010": 1.01},
        }
        for n in range(3)
    )
    handyvars_aia.carb_int = {
        "residential": {
            "electricity": {"2009": 56.84702689, "2010": 56.16823191},
            "natural gas": {"2009": 56.51576602, "2010": 54.91762852},
            "distillate": {"2009": 49.5454521, "2010": 52.59751597},
            "other fuel": {"2009": 49.5454521, "2010": 52.59751597},
        },
        "commercial": {
            "electricity": {"2009": 56.84702689, "2010": 56.16823191},
            "natural gas": {"2009": 56.51576602, "2010": 54.91762852},
            "distillate": {"2009": 49.5454521, "2010": 52.59751597},
            "other fuel": {"2009": 49.5454521, "2010": 52.59751597},
        },
    }
    handyvars_emm.carb_int, handyvars_health.carb_int = (
        {
            "residential": {
                "electricity": {
                    "FRCC": {"2009": 56.84702689 * 3.19, "2010": 56.16823191 * 3.20},
                    "ERCT": {"2009": 56.84702689 * 3.19, "2010": 56.16823191 * 3.20},
                },
                "natural gas": {"2009": 56.51576602, "2010": 54.91762852},
                "distillate": {"2009": 49.5454521, "2010": 52.59751597},
                "other fuel": {"2009": 49.5454521, "2010": 52.59751597},
            },
            "commercial": {
                "electricity": {
                    "FRCC": {"2009": 56.84702689 * 3.19, "2010": 56.16823191 * 3.20},
                    "ERCT": {"2009": 56.84702689 * 3.19, "2010": 56.16823191 * 3.20},
                },
                "natural gas": {"2009": 56.51576602, "2010": 54.91762852},
                "distillate": {"2009": 49.5454521, "2010": 52.59751597},
                "other fuel": {"2009": 49.5454521, "2010": 52.59751597},
            },
        }
        for n in range(2)
    )
    handyvars_aia.ecosts = {
        "residential": {
            "electricity": {"2009": 10.14, "2010": 9.67},
            "natural gas": {"2009": 11.28, "2010": 10.78},
            "distillate": {"2009": 21.23, "2010": 20.59},
            "other fuel": {"2009": 21.23, "2010": 20.59},
        },
        "commercial": {
            "electricity": {"2009": 9.08, "2010": 8.55},
            "natural gas": {"2009": 8.96, "2010": 8.59},
            "distillate": {"2009": 14.81, "2010": 14.87},
            "other fuel": {"2009": 14.81, "2010": 14.87},
        },
    }
    handyvars_health.ecosts, handyvars_emm.ecosts = (
        {
            "residential": {
                "electricity": {
                    "FRCC": {"2009": 9.08 * 3.19, "2010": 8.55 * 3.20},
                    "ERCT": {"2009": 9.08 * 3.19, "2010": 8.55 * 3.20},
                },
                "natural gas": {"2009": 8.96, "2010": 8.59},
                "distillate": {"2009": 14.81, "2010": 14.87},
                "other fuel": {"2009": 14.81, "2010": 14.87},
            },
            "commercial": {
                "electricity": {
                    "FRCC": {"2009": 9.08 * 3.19, "2010": 8.55 * 3.20},
                    "ERCT": {"2009": 9.08 * 3.19, "2010": 8.55 * 3.20},
                },
                "natural gas": {"2009": 8.96, "2010": 8.59},
                "distillate": {"2009": 14.81, "2010": 14.87},
                "other fuel": {"2009": 14.81, "2010": 14.87},
            },
        }
        for n in range(2)
    )
    handyvars_aia.ccosts, handyvars_emm.ccosts, handyvars_health.ccosts = (
        {"2009": 33, "2010": 33} for n in range(3)
    )
    handyvars_health.health_scn_data = numpy.array(
        [
            ("Southeast", "FRCC", "Uniform EE", 3.098224, 5, 4, 3),
            ("Southeast", "FRCC", "EE at Peak", 3, 4, 5, 6),
            ("Southeast", "SRVC", "Uniform EE", 7, 8, 9, 10),
            ("Southeast", "SRVC", "EE at Peak", 11, 12, 13, 14),
        ],
        dtype=[
            ("AVERT_Region", "<U25"),
            ("EMM_Region", "<U25"),
            ("Category", "<U25"),
            ("2017cents_kWh_3pct_high", "<f8"),
            ("2017cents_kWh_3pct_low", "<f8"),
            ("2017cents_kWh_7pct_low", "<f8"),
            ("2017cents_kWh_7pct_high", "<f8"),
        ],
    )
    convert_data = {
        "building type conversions": {
            "original type": "EnergyPlus reference buildings",
            "revised type": "Annual Energy Outlook (AEO) buildings",
            "conversion data": {
                "description": "EPlus->AEO type mapping and weighting factors",
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
            },
        }
    }
    aia_measures = [
        {
            "name": "sample measure to prepare",
            "markets": None,
            "installed_cost": 25,
            "cost_units": "2014$/unit",
            "energy_efficiency": {"new": 25, "existing": 25},
            "energy_efficiency_units": "EF",
            "market_entry_year": None,
            "market_exit_year": None,
            "product_lifetime": 1,
            "market_scaling_fractions": None,
            "market_scaling_fractions_source": None,
            "measure_type": "full service",
            "structure_type": ["new", "existing"],
            "bldg_type": "single family home",
            "climate_zone": "AIA_CZ1",
            "fuel_type": "natural gas",
            "fuel_switch_to": None,
            "end_use": "water heating",
            "technology": None,
            "tsv_features": None,
        }
    ]
    emm_measures_features = [
        {
            "name": "sample time sens. measure 1 to prepare",
            "markets": None,
            "installed_cost": 1.5,
            "cost_units": "2014$/ft^2 floor",
            "energy_efficiency": 0,
            "energy_efficiency_units": "relative savings (constant)",
            "market_entry_year": None,
            "market_exit_year": None,
            "product_lifetime": 1,
            "market_scaling_fractions": None,
            "market_scaling_fractions_source": None,
            "measure_type": "full service",
            "structure_type": ["new", "existing"],
            "bldg_type": "assembly",
            "climate_zone": "FRCC",
            "fuel_type": "electricity",
            "fuel_switch_to": None,
            "end_use": "heating",
            "technology": ["wall", "roof"],
            "tsv_features": {
                "shed": {"relative energy change fraction": 0.2, "start_hour": 6, "stop_hour": 10}
            },
        },
        {
            "name": "sample time sens. measure 2 to prepare",
            "markets": None,
            "installed_cost": 1.5,
            "cost_units": "2014$/ft^2 floor",
            "energy_efficiency": 0,
            "energy_efficiency_units": "relative savings (constant)",
            "market_entry_year": None,
            "market_exit_year": None,
            "product_lifetime": 1,
            "market_scaling_fractions": None,
            "market_scaling_fractions_source": None,
            "measure_type": "full service",
            "structure_type": ["new", "existing"],
            "bldg_type": "assembly",
            "climate_zone": "FRCC",
            "fuel_type": "electricity",
            "fuel_switch_to": None,
            "end_use": "heating",
            "technology": ["wall", "roof"],
            "tsv_features": {
                "shed": {"relative energy change fraction": 1, "start_hour": 6, "stop_hour": 10}
            },
        },
        {
            "name": "sample time sens. measure 3 to prepare",
            "markets": None,
            "installed_cost": 1.5,
            "cost_units": "2014$/ft^2 floor",
            "energy_efficiency": {"wall": 0, "roof": 0.5},
            "energy_efficiency_units": "relative savings (constant)",
            "market_entry_year": None,
            "market_exit_year": None,
            "product_lifetime": 1,
            "market_scaling_fractions": None,
            "market_scaling_fractions_source": None,
            "measure_type": "full service",
            "structure_type": ["new", "existing"],
            "bldg_type": "assembly",
            "climate_zone": "FRCC",
            "fuel_type": "electricity",
            "fuel_switch_to": None,
            "end_use": "heating",
            "technology": ["wall", "roof"],
            "tsv_features": {
                "shed": {"relative energy change fraction": 1, "start_hour": 6, "stop_hour": 10}
            },
        },
        {
            "name": "sample time sens. measure 3 - res.",
            "markets": None,
            "installed_cost": 1.5,
            "cost_units": "2014$/ft^2 floor",
            "energy_efficiency": {"wall": 0, "roof": 0.5},
            "energy_efficiency_units": "relative savings (constant)",
            "market_entry_year": None,
            "market_exit_year": None,
            "product_lifetime": 1,
            "market_scaling_fractions": None,
            "market_scaling_fractions_source": None,
            "measure_type": "full service",
            "structure_type": ["new", "existing"],
            "bldg_type": "single family home",
            "climate_zone": "FRCC",
            "fuel_type": "electricity",
            "fuel_switch_to": None,
            "end_use": "heating",
            "technology": ["wall", "roof"],
            "tsv_features": {
                "shed": {"relative energy change fraction": 1, "start_hour": 6, "stop_hour": 10}
            },
        },
    ]
    emm_measures_metrics = [
        {
            "name": "sample time sens. metrics measure",
            "markets": None,
            "installed_cost": 1.5,
            "cost_units": "2014$/ft^2 floor",
            "energy_efficiency": 0,
            "energy_efficiency_units": "relative savings (constant)",
            "market_entry_year": None,
            "market_exit_year": None,
            "product_lifetime": 1,
            "market_scaling_fractions": None,
            "market_scaling_fractions_source": None,
            "measure_type": "full service",
            "structure_type": ["new", "existing"],
            "bldg_type": "single family home",
            "climate_zone": "FRCC",
            "fuel_type": "electricity",
            "fuel_switch_to": None,
            "end_use": "heating",
            "technology": ["wall", "roof"],
            "tsv_features": None,
        },
        {
            "name": "sample time sens. metrics measure 2",
            "markets": None,
            "installed_cost": 1.5,
            "cost_units": "2014$/ft^2 floor",
            "energy_efficiency": {"wall": 0, "roof": 0.5},
            "energy_efficiency_units": "relative savings (constant)",
            "market_entry_year": None,
            "market_exit_year": None,
            "product_lifetime": 1,
            "market_scaling_fractions": None,
            "market_scaling_fractions_source": None,
            "measure_type": "full service",
            "structure_type": ["new", "existing"],
            "bldg_type": "single family home",
            "climate_zone": "FRCC",
            "fuel_type": "electricity",
            "fuel_switch_to": None,
            "end_use": "heating",
            "technology": ["wall", "roof"],
            "tsv_features": None,
        },
    ]
    health_cost_measures = [
        {
            "name": "sample health cost measure PHC-EE (high)",
            "markets": None,
            "installed_cost": 1.5,
            "cost_units": "2014$/ft^2 floor",
            "energy_efficiency": {"wall": 0, "roof": 0.5},
            "energy_efficiency_units": "relative savings (constant)",
            "market_entry_year": None,
            "market_exit_year": None,
            "product_lifetime": 1,
            "market_scaling_fractions": None,
            "market_scaling_fractions_source": None,
            "measure_type": "full service",
            "structure_type": ["new", "existing"],
            "bldg_type": "single family home",
            "climate_zone": "FRCC",
            "fuel_type": "electricity",
            "fuel_switch_to": None,
            "end_use": "heating",
            "technology": ["wall", "roof"],
            "tsv_features": {
                "shed": {"relative energy change fraction": 1, "start_hour": 6, "stop_hour": 10}
            },
        }
    ]
    ok_out_aia = [
        {
            "stock": {
                "total": {"all": {"2009": 15, "2010": 15}, "measure": {"2009": 15, "2010": 15}},
                "competed": {"all": {"2009": 15, "2010": 15}, "measure": {"2009": 15, "2010": 15}},
            },
            "energy": {
                "total": {
                    "baseline": {"2009": 15.15, "2010": 15.15},
                    "efficient": {"2009": 10.908, "2010": 10.908},
                },
                "competed": {
                    "baseline": {"2009": 15.15, "2010": 15.15},
                    "efficient": {"2009": 10.908, "2010": 10.908},
                },
            },
            "carbon": {
                "total": {
                    "baseline": {"2009": 856.2139, "2010": 832.0021},
                    "efficient": {"2009": 616.474, "2010": 599.0415},
                },
                "competed": {
                    "baseline": {"2009": 856.2139, "2010": 832.0021},
                    "efficient": {"2009": 616.474, "2010": 599.0415},
                },
            },
            "cost": {
                "stock": {
                    "total": {
                        "baseline": {"2009": 270, "2010": 270},
                        "efficient": {"2009": 240, "2010": 240},
                    },
                    "competed": {
                        "baseline": {"2009": 270, "2010": 270},
                        "efficient": {"2009": 240, "2010": 240},
                    },
                },
                "energy": {
                    "total": {
                        "baseline": {"2009": 170.892, "2010": 163.317},
                        "efficient": {"2009": 123.0422, "2010": 117.5882},
                    },
                    "competed": {
                        "baseline": {"2009": 170.892, "2010": 163.317},
                        "efficient": {"2009": 123.0422, "2010": 117.5882},
                    },
                },
                "carbon": {
                    "total": {
                        "baseline": {"2009": 28255.06, "2010": 27456.07},
                        "efficient": {"2009": 20343.64, "2010": 19768.37},
                    },
                    "competed": {
                        "baseline": {"2009": 28255.06, "2010": 27456.07},
                        "efficient": {"2009": 20343.64, "2010": 19768.37},
                    },
                },
            },
            "lifetime": {"baseline": {"2009": 180, "2010": 180}, "measure": 1},
        }
    ]
    ok_out_health_costs = [
        {
            "stock": {
                "total": {
                    "all": {
                        "2009": 11000000 * 1000 / (11 * 1000000),
                        "2010": 11000000 * 1000 / (11 * 1000000),
                    },
                    "measure": {
                        "2009": 11000000 * 1000 / (11 * 1000000),
                        "2010": 11000000 * 1000 / (11 * 1000000),
                    },
                },
                "competed": {
                    "all": {
                        "2009": 11000000 * 1000 / (11 * 1000000),
                        "2010": 11000000 * 1000 / (11 * 1000000),
                    },
                    "measure": {
                        "2009": 11000000 * 1000 / (11 * 1000000),
                        "2010": 11000000 * 1000 / (11 * 1000000),
                    },
                },
            },
            "energy": {
                "total": {
                    "baseline": {"2009": 3.19, "2010": 3.2},
                    "efficient": {"2009": 1.592371609 / 2, "2010": 1.59736337 / 2},
                },
                "competed": {
                    "baseline": {"2009": 3.19, "2010": 3.2},
                    "efficient": {"2009": 1.592371609 / 2, "2010": 1.59736337 / 2},
                },
            },
            "carbon": {
                "total": {
                    "baseline": {"2009": 176.8610198, "2010": 175.2969732},
                    "efficient": {"2009": 87.79143306 / 2, "2010": 87.01506136 / 2},
                },
                "competed": {
                    "baseline": {"2009": 176.8610198, "2010": 175.2969732},
                    "efficient": {"2009": 87.79143306 / 2, "2010": 87.01506136 / 2},
                },
            },
            "cost": {
                "stock": {
                    "total": {
                        "baseline": {"2009": 16500000, "2010": 16500000},
                        "efficient": {"2009": 16500000, "2010": 16500000},
                    },
                    "competed": {
                        "baseline": {"2009": 16500000, "2010": 16500000},
                        "efficient": {"2009": 16500000, "2010": 16500000},
                    },
                },
                "energy": {
                    "total": {
                        "baseline": {"2009": 62.28564964, "2010": 60.65739794},
                        "efficient": {"2009": 15.54976483, "2010": 15.13911041},
                    },
                    "competed": {
                        "baseline": {"2009": 62.28564964, "2010": 60.65739794},
                        "efficient": {"2009": 15.54976483, "2010": 15.13911041},
                    },
                },
                "carbon": {
                    "total": {
                        "baseline": {"2009": 5836.413654, "2010": 5784.800117},
                        "efficient": {"2009": 2897.117291 / 2, "2010": 2871.497025 / 2},
                    },
                    "competed": {
                        "baseline": {"2009": 5836.413654, "2010": 5784.800117},
                        "efficient": {"2009": 2897.117291 / 2, "2010": 2871.497025 / 2},
                    },
                },
            },
            "lifetime": {"baseline": {"2009": 15, "2010": 15}, "measure": 1},
        }
    ]
    ok_out_emm_metrics_sect_shapes = [
        None,
        {
            "FRCC": {
                "2009": {"baseline": base_out_2009, "efficient": [x * 0.5 for x in base_out_2009]},
                "2010": {"baseline": base_out_2010, "efficient": [x * 0.5 for x in base_out_2010]},
            }
        },
    ]

    # Return all test data
    return {
        "sample_cpl_in_aia": sample_cpl_in_aia,
        "sample_cpl_in_emm": sample_cpl_in_emm,
        "ok_out_emm_features": ok_out_emm_features,
        "sample_mseg_in_emm": sample_mseg_in_emm,
        "ok_out_emm_metrics_mkts": ok_out_emm_metrics_mkts,
        "sample_mseg_in_aia": sample_mseg_in_aia,
        "sample_tsv_data": sample_tsv_data,
        "aia_measures": aia_measures,
        "base_dir": base_dir,
        "base_out_2009": base_out_2009,
        "base_out_2010": base_out_2010,
        "cbecs_sf_byvint": cbecs_sf_byvint,
        "cf_ones": cf_ones,
        "convert_data": convert_data,
        "current_wkdy": current_wkdy,
        "emm_measures_features": emm_measures_features,
        "emm_measures_metrics": emm_measures_metrics,
        "handyfiles_aia": handyfiles_aia,
        "handyfiles_emm": handyfiles_emm,
        "handyvars_aia": handyvars_aia,
        "handyvars_emm": handyvars_emm,
        "handyvars_health": handyvars_health,
        "health_cost_measures": health_cost_measures,
        "inter_days": inter_days,
        "inter_days_wkdy": inter_days_wkdy,
        "inter_days_wknd": inter_days_wknd,
        "ok_out_aia": ok_out_aia,
        "ok_out_emm_metrics_sect_shapes": ok_out_emm_metrics_sect_shapes,
        "ok_out_health_costs": ok_out_health_costs,
        "opts": opts,
        "opts_aia": opts_aia,
        "opts_emm": opts_emm,
        "opts_empty": opts_empty,
        "opts_health": opts_health,
        "opts_tsv_dummy": opts_tsv_dummy,
        "package_ecms_file": package_ecms_file,
        "sample_tsv_metric_settings": sample_tsv_metric_settings,
        "sum_days": sum_days,
        "sum_days_wkdy": sum_days_wkdy,
        "sum_days_wknd": sum_days_wknd,
        "test_files": test_files,
        "wint_days": wint_days,
        "wint_days_wkdy": wint_days_wkdy,
        "wint_days_wknd": wint_days_wknd,
        "wknd_day_flags": wknd_day_flags,
    }


def test_filter_packages(update_test_data):
    """Tests filtering of packages both with the ecm_packages argument and when invalid
    given available ECMs.
    """

    # Scenario with packages that do not have contributing ECMs present
    opts_pkgs = copy.deepcopy(update_test_data["opts_empty"])
    opts_pkgs.ecm_files = [
        "ENERGY STAR Res. ASHP (FS)",
        "Res. Air Sealing (New), IECC c. 2021",
        "Res. Air Sealing (Exist), IECC c. 2021",
        "ENERGY STAR Windows v. 7.0",
        "Residential Walls, IECC c. 2021",
        "Residential Roof, IECC c. 2021",
        "Residential Floors, IECC c. 2021",
        "ENERGY STAR Res. ASHP (FS) CC",
        "ENERGY STAR Res. ASHP (LFL)",
        "ENERGY STAR Res. ASHP (RST)",
    ]
    opts_pkgs.ecm_packages = [
        "ENERGY STAR Res. ASHP (FS) + Env.",
        "ENERGY STAR Res. ASHP (FS) + Env. CC",
        "Prosp. Res. ASHP (FS) + Env. + Ctls.",
    ]
    with open(update_test_data["package_ecms_file"], "r") as f:
        packages = json.load(f)

    # Downselect via the ecm_packages argument
    selected_pkgs = ECMPrepHelper.downselect_packages(packages, opts_pkgs.ecm_packages)

    # Further filter packages that do not have all contributing ECMs
    valid_pkgs, invalid_pkgs = ECMPrepHelper.filter_invalid_packages(
        selected_pkgs, opts_pkgs.ecm_files, opts_pkgs
    )
    # Check list of valid packages
    valid_pkg_names = [pkg["name"] for pkg in valid_pkgs]
    expected_pkgs = ["ENERGY STAR Res. ASHP (FS) + Env.", "ENERGY STAR Res. ASHP (FS) + Env. CC"]
    assert valid_pkg_names == expected_pkgs
    # Check list of invalid packages
    expected_invalid = ["Prosp. Res. ASHP (FS) + Env. + Ctls."]
    assert invalid_pkgs == expected_invalid


def test_ecm_field_updates(update_test_data):
    """Tests that ecm_field_updates argument correctly updates all ECMs"""
    opts = copy.deepcopy(update_test_data["opts_aia"])
    opts.ecm_field_updates = {
        "climate_zone": ["AIA_CZ1", "AIA_CZ2"],
        "another_field": "another_val",
    }
    measures_out_aia = ECMPrep.prepare_measures(
        update_test_data["aia_measures"],
        update_test_data["convert_data"],
        update_test_data["sample_mseg_in_aia"],
        update_test_data["sample_cpl_in_aia"],
        update_test_data["handyvars_aia"],
        update_test_data["handyfiles_aia"],
        update_test_data["cbecs_sf_byvint"],
        update_test_data["sample_tsv_data"],
        update_test_data["base_dir"],
        opts,
        ctrb_ms_pkg_prep=[],
        tsv_data_nonfs=None,
    )

    for measure in measures_out_aia:
        for ecm_field, new_val in opts.ecm_field_updates.items():
            assert getattr(measure, ecm_field) == new_val


def test_contributing_ecm_add(update_test_data):
    """Tests automatic adding of ECMs required for selected package(s)"""

    # Scenario with no ECMs selected and one package
    opts_pkg_no_ecm = copy.deepcopy(update_test_data["opts_empty"])
    opts_pkg_no_ecm.ecm_files = []
    opts_pkg_no_ecm.ecm_packages = ["ENERGY STAR Res. ASHP (FS) + Env."]

    with open(update_test_data["package_ecms_file"], "r") as f:
        packages = json.load(f)

    # Downselect via the ecm_packages argument
    selected_pkgs = ECMPrepHelper.downselect_packages(packages, opts_pkg_no_ecm.ecm_packages)

    # Add ECMs that contribute to package
    ecms = ECMPrepHelper.retrieve_valid_ecms(
        selected_pkgs, opts_pkg_no_ecm, update_test_data["handyfiles_emm"]
    )
    ecms = [ecm.stem for ecm in ecms]
    expected_ecms = [
        "ENERGY STAR Res. ASHP (FS)",
        "Res. Air Sealing (New), IECC c. 2021",
        "Res. Air Sealing (Exist), IECC c. 2021",
        "ENERGY STAR Windows v. 7.0",
        "Residential Walls, IECC c. 2021",
        "Residential Roof, IECC c. 2021",
        "Residential Floors, IECC c. 2021",
    ]

    assert sorted(ecms) == sorted(expected_ecms)


def test_fillmeas_ok(update_test_data):
    """Test 'prepare_measures' function given valid measure inputs.

    Note:
        Ensure that function properly identifies which input measures
        require updating and that the updates are performed correctly.
    """
    # Check for measures using AIA baseline data
    measures_out_aia = ECMPrep.prepare_measures(
        update_test_data["aia_measures"],
        update_test_data["convert_data"],
        update_test_data["sample_mseg_in_aia"],
        update_test_data["sample_cpl_in_aia"],
        update_test_data["handyvars_aia"],
        update_test_data["handyfiles_aia"],
        update_test_data["cbecs_sf_byvint"],
        update_test_data["sample_tsv_data"],
        update_test_data["base_dir"],
        update_test_data["opts_aia"],
        ctrb_ms_pkg_prep=[],
        tsv_data_nonfs=None,
    )
    # Assess AIA-resolved test measures
    for oc_aia in range(0, len(update_test_data["ok_out_aia"])):
        dict_check(
            measures_out_aia[oc_aia].markets["Technical potential"]["master_mseg"],
            update_test_data["ok_out_aia"][oc_aia],
        )
    # Check for measures using EMM baseline data and tsv features
    measures_out_emm_features = ECMPrep.prepare_measures(
        update_test_data["emm_measures_features"],
        update_test_data["convert_data"],
        update_test_data["sample_mseg_in_emm"],
        update_test_data["sample_cpl_in_emm"],
        update_test_data["handyvars_emm"],
        update_test_data["handyfiles_emm"],
        update_test_data["cbecs_sf_byvint"],
        update_test_data["sample_tsv_data"],
        update_test_data["base_dir"],
        update_test_data["opts_emm"][0],
        ctrb_ms_pkg_prep=[],
        tsv_data_nonfs=None,
    )
    # Check for measures using EMM baseline data and public health energy
    # cost adders
    measures_out_health_benefits = ECMPrep.prepare_measures(
        update_test_data["health_cost_measures"],
        update_test_data["convert_data"],
        update_test_data["sample_mseg_in_emm"],
        update_test_data["sample_cpl_in_emm"],
        update_test_data["handyvars_health"],
        update_test_data["handyfiles_emm"],
        update_test_data["cbecs_sf_byvint"],
        update_test_data["sample_tsv_data"],
        update_test_data["base_dir"],
        update_test_data["opts_health"][0],
        ctrb_ms_pkg_prep=[],
        tsv_data_nonfs=None,
    )
    # Assess EMM-resolved test measures with time sensitive features
    for oc_emm in range(0, len(update_test_data["ok_out_emm_features"])):
        dict_check(
            measures_out_emm_features[oc_emm].markets["Technical potential"]["master_mseg"],
            update_test_data["ok_out_emm_features"][oc_emm],
        )
    # Assess EMM-resolved test measures with time sensitive output
    # metrics or sector-level load shape output options
    for oc_emm in range(0, len(update_test_data["emm_measures_metrics"])):
        # Check for measures using EMM baseline data and tsv metrics
        # or sector-level load shape options
        measures_out_emm_metrics = ECMPrep.prepare_measures(
            [update_test_data["emm_measures_metrics"][oc_emm]],
            update_test_data["convert_data"],
            update_test_data["sample_mseg_in_emm"],
            update_test_data["sample_cpl_in_emm"],
            update_test_data["handyvars_emm"],
            update_test_data["handyfiles_emm"],
            update_test_data["cbecs_sf_byvint"],
            update_test_data["sample_tsv_data"],
            update_test_data["base_dir"],
            update_test_data["opts_emm"][(oc_emm + 1)],
            ctrb_ms_pkg_prep=[],
            tsv_data_nonfs=None,
        )
        # Check master microsegment output under technical potential case
        dict_check(
            measures_out_emm_metrics[0].markets["Technical potential"]["master_mseg"],
            update_test_data["ok_out_emm_metrics_mkts"][oc_emm],
        )
        # Check sector-level load shape output under tech. potential case
        # if info. is available; otherwise check for None values
        if update_test_data["ok_out_emm_metrics_sect_shapes"][oc_emm]:
            dict_check(
                measures_out_emm_metrics[0].sector_shapes["Technical potential"],
                update_test_data["ok_out_emm_metrics_sect_shapes"][oc_emm],
            )
        else:
            assert (
                measures_out_emm_metrics[0].sector_shapes
                == update_test_data["ok_out_emm_metrics_sect_shapes"][oc_emm]
            )
    # Assess EMM-resolved test measures with public health benefits
    for oc_ph in range(0, len(update_test_data["ok_out_health_costs"])):
        dict_check(
            measures_out_health_benefits[oc_ph].markets["Technical potential"]["master_mseg"],
            update_test_data["ok_out_health_costs"][oc_ph],
        )
