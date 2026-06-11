#!/usr/bin/env python3

"""Tests for CleanUpTest"""

from scout.ecm_prep import Measure, MeasurePackage, ECMPrepHelper
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
    benefits = {"energy savings increase": None, "cost reduction": None}
    handyfiles = UsefulInputFiles(opts)
    handyvars = UsefulVars(base_dir, handyfiles, opts)
    sample_measindiv_dicts = [
        {
            "name": "cleanup 1",
            "tsv_features": None,
            "market_entry_year": None,
            "market_exit_year": None,
            "fuel_switch_to": None,
            "measure_type": "full service",
            "end_use": {"primary": ["cooling"], "secondary": None},
            "technology": {"primary": ["central AC"], "secondary": None},
        },
        {
            "name": "cleanup 2",
            "tsv_features": None,
            "market_entry_year": None,
            "market_exit_year": None,
            "fuel_switch_to": None,
            "measure_type": "full service",
            "end_use": {"primary": ["cooling"], "secondary": None},
            "technology": {"primary": ["central AC"], "secondary": None},
        },
    ]
    sample_measlist_in = [
        Measure(base_dir, handyvars, handyfiles, opts_dict, **x) for x in sample_measindiv_dicts
    ]
    sample_full_dat_out = {a_s: True for a_s in ["Technical potential", "Max adoption potential"]}
    # Hard code proper technology type format for use in packaging
    # (normally this format is achieved by running Measures through the
    # 'fill_mkts' function, which isn't tested here)
    for m in sample_measlist_in:
        m.technology_type = {"primary": ["supply"], "secondary": None}
    sample_measpackage = MeasurePackage(
        copy.deepcopy(sample_measlist_in),
        "cleanup 3",
        benefits,
        handyvars,
        handyfiles,
        opts,
        convert_data=None,
    )
    sample_measlist_in.append(sample_measpackage)
    sample_measlist_out_comp_data = [
        {
            "Technical potential": {
                "contributing mseg keys and values": {},
                "competed choice parameters": {},
                "capacity factor": {},
                "secondary mseg adjustments": {
                    "market share": {
                        "original energy (total captured)": {},
                        "original energy (competed and captured)": {},
                        "adjusted energy (total captured)": {},
                        "adjusted energy (competed and captured)": {},
                    }
                },
            },
            "Max adoption potential": {
                "contributing mseg keys and values": {},
                "competed choice parameters": {},
                "capacity factor": {},
                "secondary mseg adjustments": {
                    "market share": {
                        "original energy (total captured)": {},
                        "original energy (competed and captured)": {},
                        "adjusted energy (total captured)": {},
                        "adjusted energy (competed and captured)": {},
                    }
                },
            },
        },
        {
            "Technical potential": {
                "contributing mseg keys and values": {},
                "competed choice parameters": {},
                "capacity factor": {},
                "secondary mseg adjustments": {
                    "market share": {
                        "original energy (total captured)": {},
                        "original energy (competed and captured)": {},
                        "adjusted energy (total captured)": {},
                        "adjusted energy (competed and captured)": {},
                    }
                },
            },
            "Max adoption potential": {
                "contributing mseg keys and values": {},
                "competed choice parameters": {},
                "capacity factor": {},
                "secondary mseg adjustments": {
                    "market share": {
                        "original energy (total captured)": {},
                        "original energy (competed and captured)": {},
                        "adjusted energy (total captured)": {},
                        "adjusted energy (competed and captured)": {},
                    }
                },
            },
        },
        {
            "Technical potential": {
                "contributing mseg keys and values": {},
                "competed choice parameters": {},
                "capacity factor": {},
                "secondary mseg adjustments": {
                    "market share": {
                        "original energy (total captured)": {},
                        "original energy (competed and captured)": {},
                        "adjusted energy (total captured)": {},
                        "adjusted energy (competed and captured)": {},
                    }
                },
            },
            "Max adoption potential": {
                "contributing mseg keys and values": {},
                "competed choice parameters": {},
                "capacity factor": {},
                "secondary mseg adjustments": {
                    "market share": {
                        "original energy (total captured)": {},
                        "original energy (competed and captured)": {},
                        "adjusted energy (total captured)": {},
                        "adjusted energy (competed and captured)": {},
                    }
                },
            },
        },
    ]
    sample_measlist_out_shape_data = [{} for m in range(len(sample_measlist_in))]
    sample_measlist_out_eff_fs_data = [{} for m in range(len(sample_measlist_in))]
    sample_measlist_out_mkt_keys = ["master_mseg", "mseg_out_break"]
    sample_measlist_out_highlev_keys = [
        [
            "market_entry_year",
            "market_exit_year",
            "markets",
            "name",
            "remove",
            "retro_rate",
            "target",
            "tech_switch_to",
            "technology",
            "end_use",
            "technology_type",
            "htcl_tech_link",
            "yrs_on_mkt",
            "measure_type",
            "usr_opts",
            "fuel_switch_to",
            "hp_convert_flag",
            "add_cool_anchor_tech",
            "min_eff_elec_flag",
            "ref_case_flag",
            "backup_fuel_fraction",
        ],
        [
            "market_entry_year",
            "market_exit_year",
            "markets",
            "name",
            "remove",
            "retro_rate",
            "target",
            "tech_switch_to",
            "technology",
            "end_use",
            "technology_type",
            "htcl_tech_link",
            "yrs_on_mkt",
            "measure_type",
            "usr_opts",
            "fuel_switch_to",
            "hp_convert_flag",
            "add_cool_anchor_tech",
            "min_eff_elec_flag",
            "ref_case_flag",
            "backup_fuel_fraction",
        ],
        [
            "benefits",
            "bldg_type",
            "climate_zone",
            "end_use",
            "fuel_type",
            "tech_switch_to",
            "htcl_tech_link",
            "technology",
            "technology_type",
            "market_entry_year",
            "market_exit_year",
            "markets",
            "contributing_ECMs",
            "name",
            "pkg_env_costs",
            "pkg_env_cost_convert_data",
            "remove",
            "structure_type",
            "yrs_on_mkt",
            "meas_typ",
            "usr_opts",
            "fuel_switch_to",
            "min_eff_elec_flag",
            "backup_fuel_fraction",
        ],
    ]
    sample_pkg_meas_names = [x["name"] for x in sample_measindiv_dicts]

    return {
        "handyfiles": handyfiles,
        "handyvars": handyvars,
        "sample_measlist_in": sample_measlist_in,
        "sample_full_dat_out": sample_full_dat_out,
        "sample_measlist_out_comp_data": sample_measlist_out_comp_data,
        "sample_measlist_out_shape_data": sample_measlist_out_shape_data,
        "sample_measlist_out_eff_fs_data": sample_measlist_out_eff_fs_data,
        "sample_measlist_out_mkt_keys": sample_measlist_out_mkt_keys,
        "sample_measlist_out_highlev_keys": sample_measlist_out_highlev_keys,
        "sample_pkg_meas_names": sample_pkg_meas_names,
    }


def test_cleanup(test_data):
    """Test 'split_clean_data' function given valid inputs."""
    # Execute the function
    measures_comp_data, measures_summary_data, measures_shape_data, measures_eff_fs_splt_data = (
        ECMPrepHelper.split_clean_data(
            test_data["sample_measlist_in"], test_data["sample_full_dat_out"]
        )
    )
    # Check function outputs
    for ind in range(0, len(test_data["sample_measlist_in"])):
        # Check measure competition data
        dict_check(test_data["sample_measlist_out_comp_data"][ind], measures_comp_data[ind])
        # Check measure sector shape data
        assert test_data["sample_measlist_out_shape_data"][ind] == measures_shape_data[ind]
        # Check measure efficient fuel split data
        assert test_data["sample_measlist_out_eff_fs_data"][ind] == measures_eff_fs_splt_data[ind]
        # Check measure summary data
        for adopt_scheme in test_data["handyvars"].adopt_schemes_prep:
            assert sorted(list(measures_summary_data[ind].keys())) == sorted(
                test_data["sample_measlist_out_highlev_keys"][ind]
            )
            assert sorted(
                list(measures_summary_data[ind]["markets"][adopt_scheme].keys())
            ) == sorted(test_data["sample_measlist_out_mkt_keys"])
            # Verify correct updating of 'contributing_ECMs'
            # MeasurePackage attribute
            if "Package: " in measures_summary_data[ind]["name"]:
                assert (
                    measures_summary_data[ind]["contributing_ECMs"]
                    == test_data["sample_pkg_meas_names"]
                )
