#!/usr/bin/env python3

"""Tests for PartitionMicrosegmentTest"""

from scout.ecm_prep import Measure
from scout.ecm_prep_vars import UsefulVars, UsefulInputFiles
import pytest
import numpy
import os
from tests.ecm_prep_test.common import NullOpts, dict_check
from tests.ecm_prep_test.test_data.partition_microsegment_test_data import (
    ok_out_fraction,
    ok_out_bass,
    ok_out_fraction_string,
    ok_out_bass_string,
    ok_out_bad_string,
    ok_out_bad_values,
    ok_out_wrong_name,
    ok_out,
)


@pytest.fixture(scope="module")
def test_data():
    """Fixture providing test data."""
    # Null user options/options dict
    opts, opts_dict = [NullOpts().opts, NullOpts().opts_dict]
    time_horizons = ["2009", "2010", "2011"]
    # Base directory
    base_dir = os.getcwd()
    handyfiles = UsefulInputFiles(opts)
    handyvars = UsefulVars(base_dir, handyfiles, opts)
    handyvars.aeo_years = ["2009", "2010", "2011"]
    handyvars.ccosts = numpy.array(
        (b"Test", 1, 4, 1),
        dtype=[("Category", "S11"), ("2009", "<f8"), ("2010", "<f8"), ("2011", "<f8")],
    )
    sample_measure_fraction = {
        "name": "sample measure 1 partition",
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
        "diffusion": {"fraction_2006": 0.3, "fraction_2050": 1},
        "retro_rate": 0.02,
    }
    sample_measure_bass = {
        "name": "sample measure 1 partition",
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
        "diffusion": {"bass_model_p": 0.001645368, "bass_model_q": 1.455182},
        "retro_rate": 0.02,
    }
    sample_measure_fraction_string = {
        "name": "sample measure 1 partition",
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
        "diffusion": {"fraction_2020": "0.3", "fraction_2040": "1"},
        "retro_rate": 0.02,
    }
    sample_measure_bass_string = {
        "name": "sample measure 1 partition",
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
        "diffusion": {"bass_model_p": "0.001645368", "bass_model_q": "1.455182"},
        "retro_rate": 0.02,
    }
    sample_measure_bad_string = {
        "name": "sample measure 1 partition",
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
        "diffusion": {"bass_model_p": "aaa", "bass_model_q": "bbb"},
        "retro_rate": 0.02,
    }
    sample_measure_bad_values = {
        "name": "sample measure 1 partition",
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
        "diffusion": {"fraction_2016": -1, "fraction_2050": 2},
        "retro_rate": 0.02,
    }
    sample_measure_wrong_name = {
        "name": "sample measure 1 partition",
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
        "diffusion_": {"fraction_2016": 0.3, "fraction_2050": 1},
        "retro_rate": 0.02,
    }
    measure_instance_fraction = Measure(
        base_dir, handyvars, handyfiles, opts_dict, **sample_measure_fraction
    )
    measure_instance_bass = Measure(
        base_dir, handyvars, handyfiles, opts_dict, **sample_measure_bass
    )
    measure_instance_fraction_string = Measure(
        base_dir, handyvars, handyfiles, opts_dict, **sample_measure_fraction_string
    )
    measure_instance_bass_string = Measure(
        base_dir, handyvars, handyfiles, opts_dict, **sample_measure_bass_string
    )
    measure_instance_bad_string = Measure(
        base_dir, handyvars, handyfiles, opts_dict, **sample_measure_bad_string
    )
    measure_instance_bad_values = Measure(
        base_dir, handyvars, handyfiles, opts_dict, **sample_measure_bad_values
    )
    measure_instance_wrong_name = Measure(
        base_dir, handyvars, handyfiles, opts_dict, **sample_measure_wrong_name
    )
    ok_diffuse_params_in = None
    ok_mskeys_in = [
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
            "resistance heat",
            "existing",
        ),
    ]
    ok_mskeys_swtch_in = ""
    ok_bldg_sect_in = ["residential", "residential"]
    ok_sqft_subst_in = [0, 0]
    ok_mkt_scale_frac_in = 1
    ok_new_bldg_constr = {
        "annual new": {"2009": 10, "2010": 0, "2011": 0},
        "total new": {"2009": 10, "2010": 10, "2011": 10},
    }
    ok_stock_in = {"2009": 100, "2010": 100, "2011": 100}
    ok_energy_scnd_in = {"2009": 10, "2010": 20, "2011": 30}
    ok_energy_in = {"2009": 10, "2010": 20, "2011": 30}
    ok_carb_in = {"2009": 30, "2010": 60, "2011": 90}
    ok_fcarb_in = None

    ok_f_refr_in = None
    ok_base_cost_in = {"2009": 10, "2010": 10, "2011": 10}
    ok_cost_meas_in = {"2009": 20, "2010": 20, "2011": 20}
    ok_cost_energy_base_in, ok_cost_energy_meas_in = (
        numpy.array(
            (b"Test", 1, 2, 2),
            dtype=[("Category", "S11"), ("2009", "<f8"), ("2010", "<f8"), ("2011", "<f8")],
        )
        for n in range(2)
    )
    ok_relperf_in = {"2009": 0.30, "2010": 0.30, "2011": 0.30}
    ok_life_base_in = {"2009": 10, "2010": 10, "2011": 10}
    ok_life_meas_in = 10
    ok_ssconv_base_in, ok_ssconv_meas_in = (
        numpy.array(
            (b"Test", 1, 1, 1),
            dtype=[("Category", "S11"), ("2009", "<f8"), ("2010", "<f8"), ("2011", "<f8")],
        )
        for n in range(2)
    )
    ok_carbint_base_in, ok_carbint_meas_in = (
        numpy.array(
            (b"Test", 1, 1, 1),
            dtype=[("Category", "S11"), ("2009", "<f8"), ("2010", "<f8"), ("2011", "<f8")],
        )
        for n in range(2)
    )
    ok_tsv_scale_fracs_in = {
        "energy": {"baseline": 1, "efficient": 1},
        "cost": {"baseline": 1, "efficient": 1},
        "carbon": {"baseline": 1, "efficient": 1},
    }
    ok_tsv_shapes_in = None
    return {
        "time_horizons": time_horizons,
        "handyfiles": handyfiles,
        "handyvars": handyvars,
        "opts": opts,
        "measure_instance_fraction": measure_instance_fraction,
        "measure_instance_bass": measure_instance_bass,
        "measure_instance_fraction_string": measure_instance_fraction_string,
        "measure_instance_bass_string": measure_instance_bass_string,
        "measure_instance_bad_string": measure_instance_bad_string,
        "measure_instance_bad_values": measure_instance_bad_values,
        "measure_instance_wrong_name": measure_instance_wrong_name,
        "ok_diffuse_params_in": ok_diffuse_params_in,
        "ok_mskeys_in": ok_mskeys_in,
        "ok_mskeys_swtch_in": ok_mskeys_swtch_in,
        "ok_bldg_sect_in": ok_bldg_sect_in,
        "ok_sqft_subst_in": ok_sqft_subst_in,
        "ok_mkt_scale_frac_in": ok_mkt_scale_frac_in,
        "ok_new_bldg_constr": ok_new_bldg_constr,
        "ok_stock_in": ok_stock_in,
        "ok_energy_scnd_in": ok_energy_scnd_in,
        "ok_energy_in": ok_energy_in,
        "ok_carb_in": ok_carb_in,
        "ok_fcarb_in": ok_fcarb_in,
        "ok_f_refr_in": ok_f_refr_in,
        "ok_base_cost_in": ok_base_cost_in,
        "ok_cost_meas_in": ok_cost_meas_in,
        "ok_cost_energy_base_in": ok_cost_energy_base_in,
        "ok_cost_energy_meas_in": ok_cost_energy_meas_in,
        "ok_relperf_in": ok_relperf_in,
        "ok_life_base_in": ok_life_base_in,
        "ok_life_meas_in": ok_life_meas_in,
        "ok_ssconv_base_in": ok_ssconv_base_in,
        "ok_ssconv_meas_in": ok_ssconv_meas_in,
        "ok_carbint_base_in": ok_carbint_base_in,
        "ok_carbint_meas_in": ok_carbint_meas_in,
        "ok_tsv_scale_fracs_in": ok_tsv_scale_fracs_in,
        "ok_tsv_shapes_in": ok_tsv_shapes_in,
        "ok_out_fraction": ok_out_fraction,
        "ok_out_bass": ok_out_bass,
        "ok_out_fraction_string": ok_out_fraction_string,
        "ok_out_bass_string": ok_out_bass_string,
        "ok_out_bad_string": ok_out_bad_string,
        "ok_out_bad_values": ok_out_bad_values,
        "ok_out_wrong_name": ok_out_wrong_name,
        "ok_out": ok_out,
    }


def test_ok(test_data):
    """Test the 'partition_microsegment' function given valid inputs.

    Raises:
        AssertionError: If function yields unexpected results.
    """
    # Loop through 'ok_out' elements
    # Reset AEO time horizon and market entry/exit years
    test_data["measure_instance_fraction"].handyvars.aeo_years = test_data["time_horizons"]
    test_data["measure_instance_fraction"].market_entry_year = int(test_data["time_horizons"][0])
    test_data["measure_instance_fraction"].market_exit_year = (
        int(test_data["time_horizons"][-1]) + 1
    )
    # Reset AEO time horizon and market entry/exit years
    test_data["measure_instance_bass"].handyvars.aeo_years = test_data["time_horizons"]
    test_data["measure_instance_bass"].market_entry_year = int(test_data["time_horizons"][0])
    test_data["measure_instance_bass"].market_exit_year = int(test_data["time_horizons"][-1]) + 1
    # Reset AEO time horizon and market entry/exit years
    test_data["measure_instance_fraction_string"].handyvars.aeo_years = test_data["time_horizons"]
    test_data["measure_instance_fraction_string"].market_entry_year = int(
        test_data["time_horizons"][0]
    )
    test_data["measure_instance_fraction_string"].market_exit_year = (
        int(test_data["time_horizons"][-1]) + 1
    )
    # Reset AEO time horizon and market entry/exit years
    test_data["measure_instance_bass_string"].handyvars.aeo_years = test_data["time_horizons"]
    test_data["measure_instance_bass_string"].market_entry_year = int(test_data["time_horizons"][0])
    test_data["measure_instance_bass_string"].market_exit_year = (
        int(test_data["time_horizons"][-1]) + 1
    )

    # Set measure-specific retrofit rate to test
    meas_retro_rate_fraction = test_data["measure_instance_fraction"].retro_rate
    meas_retro_rate_bass = test_data["measure_instance_bass"].retro_rate
    meas_retro_rate_fraction_string = test_data["measure_instance_fraction_string"].retro_rate
    meas_retro_rate_bass_string = test_data["measure_instance_bass_string"].retro_rate

    warnings_check = [
        [
            "WARNING: Not enough data were provided for first and last years"
            " of the considered simulation period.\n\tThe simulation will "
            "continue assuming plausible diffusion fraction values.",
            "WARNING: Not enough data were provided for first and last "
            "years of the considered simulation period.\n\tThe simulation "
            "will continue assuming plausible diffusion fraction values.",
            "WARNING: Not enough data were provided for first and last years"
            " of the considered simulation period.\n\tThe simulation will "
            "continue assuming plausible diffusion fraction values.",
            "WARNING: Not enough data were provided for first and last years"
            " of the considered simulation period.\n\tThe simulation will "
            "continue assuming plausible diffusion fraction values.",
        ],
        [
            "WARNING: Not enough data were provided for first and last "
            "years of the considered simulation period.\n\tThe simulation"
            " will continue assuming plausible diffusion fraction values.",
            "WARNING: Not enough data were provided for first and last years"
            " of the considered simulation period.\n\tThe simulation will "
            "continue assuming plausible diffusion fraction values.",
            "WARNING: Not enough data were provided for first and last "
            "years of the considered simulation period.\n\tThe simulation"
            " will continue assuming plausible diffusion fraction values.",
            "WARNING: Not enough data were provided for first and last years"
            " of the considered simulation period.\n\tThe simulation will "
            "continue assuming plausible diffusion fraction values.",
        ],
        [
            "WARNING: Not enough data were provided for first and last"
            " years of the considered simulation period.\n\tThe simulation"
            " will continue assuming plausible diffusion fraction values.",
            "WARNING: Not enough data were provided for first and last "
            "years of the considered simulation period.\n\tThe simulation"
            " will continue assuming plausible diffusion fraction values.",
            "WARNING: Not enough data were provided for first and last years"
            " of the considered simulation period.\n\tThe simulation will "
            "continue assuming plausible diffusion fraction values.",
            "WARNING: Not enough data were provided for first and last"
            " years of the considered simulation period.\n\tThe simulation"
            " will continue assuming plausible diffusion fraction values.",
        ],
        [
            "WARNING: Not enough data were provided for first and last"
            " years of the considered simulation period.\n\tThe simulation"
            " will continue assuming plausible diffusion fraction values.",
            "WARNING: Not enough data were provided for first and last years"
            " of the considered simulation period.\n\tThe simulation will "
            "continue assuming plausible diffusion fraction values.",
            "WARNING: Not enough data were provided for first and last years"
            " of the considered simulation period.\n\tThe simulation will "
            "continue assuming plausible diffusion fraction values.",
            "WARNING: Not enough data were provided for first and last years"
            " of the considered simulation period.\n\tThe simulation will "
            "continue assuming plausible diffusion fraction values.",
        ],
    ]

    warn_list = []
    warnings_fraction_measure = []
    warnings_bass_measure = []
    warnings_fraction_string_measure = []
    warnings_bass_string_measure = []

    # Loop through two test schemes (Technical potential and Max
    # adoption potential)
    for scn in range(0, len(test_data["handyvars"].adopt_schemes_prep)):
        # Loop through two microsegment key chains (one applying
        # to new structure type, another to existing structure type)
        for k in range(0, len(test_data["ok_mskeys_in"])):
            # List of output dicts generated by the function
            lists_fraction = test_data["measure_instance_fraction"].partition_microsegment(
                test_data["handyvars"].adopt_schemes_prep[scn],
                test_data["ok_diffuse_params_in"],
                test_data["ok_mskeys_in"][k],
                test_data["ok_mskeys_swtch_in"],
                test_data["ok_bldg_sect_in"][k],
                test_data["ok_sqft_subst_in"][k],
                test_data["ok_mkt_scale_frac_in"],
                test_data["ok_new_bldg_constr"],
                test_data["ok_stock_in"],
                test_data["ok_energy_in"],
                test_data["ok_carb_in"],
                test_data["ok_fcarb_in"],
                test_data["ok_f_refr_in"],
                test_data["ok_base_cost_in"],
                test_data["ok_cost_meas_in"],
                test_data["ok_cost_energy_base_in"],
                test_data["ok_cost_energy_meas_in"],
                test_data["ok_relperf_in"],
                test_data["ok_life_base_in"],
                test_data["ok_life_meas_in"],
                test_data["ok_ssconv_base_in"],
                test_data["ok_ssconv_meas_in"],
                test_data["ok_carbint_base_in"],
                test_data["ok_carbint_meas_in"],
                test_data["ok_energy_scnd_in"],
                test_data["ok_tsv_scale_fracs_in"],
                test_data["ok_tsv_shapes_in"],
                test_data["opts"],
                contrib_mseg_key="",
                ctrb_ms_pkg_prep=[],
                hp_rate=None,
                retro_rate_mseg=meas_retro_rate_fraction,
                calc_sect_shapes="",
                lkg_fmeth_base=None,
                lkg_fmeth_meas=None,
                warn_list=warn_list,
            )
            warnings_fraction_measure.append(lists_fraction[-1])

            lists_bass = test_data["measure_instance_bass"].partition_microsegment(
                test_data["handyvars"].adopt_schemes_prep[scn],
                test_data["ok_diffuse_params_in"],
                test_data["ok_mskeys_in"][k],
                test_data["ok_mskeys_swtch_in"],
                test_data["ok_bldg_sect_in"][k],
                test_data["ok_sqft_subst_in"][k],
                test_data["ok_mkt_scale_frac_in"],
                test_data["ok_new_bldg_constr"],
                test_data["ok_stock_in"],
                test_data["ok_energy_in"],
                test_data["ok_carb_in"],
                test_data["ok_fcarb_in"],
                test_data["ok_f_refr_in"],
                test_data["ok_base_cost_in"],
                test_data["ok_cost_meas_in"],
                test_data["ok_cost_energy_base_in"],
                test_data["ok_cost_energy_meas_in"],
                test_data["ok_relperf_in"],
                test_data["ok_life_base_in"],
                test_data["ok_life_meas_in"],
                test_data["ok_ssconv_base_in"],
                test_data["ok_ssconv_meas_in"],
                test_data["ok_carbint_base_in"],
                test_data["ok_carbint_meas_in"],
                test_data["ok_energy_scnd_in"],
                test_data["ok_tsv_scale_fracs_in"],
                test_data["ok_tsv_shapes_in"],
                test_data["opts"],
                contrib_mseg_key="",
                ctrb_ms_pkg_prep=[],
                hp_rate=None,
                retro_rate_mseg=meas_retro_rate_bass,
                calc_sect_shapes="",
                lkg_fmeth_base=None,
                lkg_fmeth_meas=None,
                warn_list=warn_list,
            )
            warnings_bass_measure.append(lists_bass[-1])

            lists_fraction_string = test_data[
                "measure_instance_fraction_string"
            ].partition_microsegment(
                test_data["handyvars"].adopt_schemes_prep[scn],
                test_data["ok_diffuse_params_in"],
                test_data["ok_mskeys_in"][k],
                test_data["ok_mskeys_swtch_in"],
                test_data["ok_bldg_sect_in"][k],
                test_data["ok_sqft_subst_in"][k],
                test_data["ok_mkt_scale_frac_in"],
                test_data["ok_new_bldg_constr"],
                test_data["ok_stock_in"],
                test_data["ok_energy_in"],
                test_data["ok_carb_in"],
                test_data["ok_fcarb_in"],
                test_data["ok_f_refr_in"],
                test_data["ok_base_cost_in"],
                test_data["ok_cost_meas_in"],
                test_data["ok_cost_energy_base_in"],
                test_data["ok_cost_energy_meas_in"],
                test_data["ok_relperf_in"],
                test_data["ok_life_base_in"],
                test_data["ok_life_meas_in"],
                test_data["ok_ssconv_base_in"],
                test_data["ok_ssconv_meas_in"],
                test_data["ok_carbint_base_in"],
                test_data["ok_carbint_meas_in"],
                test_data["ok_energy_scnd_in"],
                test_data["ok_tsv_scale_fracs_in"],
                test_data["ok_tsv_shapes_in"],
                test_data["opts"],
                contrib_mseg_key="",
                ctrb_ms_pkg_prep=[],
                hp_rate=None,
                retro_rate_mseg=meas_retro_rate_fraction_string,
                calc_sect_shapes="",
                lkg_fmeth_base=None,
                lkg_fmeth_meas=None,
                warn_list=warn_list,
            )
            warnings_fraction_string_measure.append(lists_fraction_string[-1])

            lists_bass_string = test_data["measure_instance_bass_string"].partition_microsegment(
                test_data["handyvars"].adopt_schemes_prep[scn],
                test_data["ok_diffuse_params_in"],
                test_data["ok_mskeys_in"][k],
                test_data["ok_mskeys_swtch_in"],
                test_data["ok_bldg_sect_in"][k],
                test_data["ok_sqft_subst_in"][k],
                test_data["ok_mkt_scale_frac_in"],
                test_data["ok_new_bldg_constr"],
                test_data["ok_stock_in"],
                test_data["ok_energy_in"],
                test_data["ok_carb_in"],
                test_data["ok_fcarb_in"],
                test_data["ok_f_refr_in"],
                test_data["ok_base_cost_in"],
                test_data["ok_cost_meas_in"],
                test_data["ok_cost_energy_base_in"],
                test_data["ok_cost_energy_meas_in"],
                test_data["ok_relperf_in"],
                test_data["ok_life_base_in"],
                test_data["ok_life_meas_in"],
                test_data["ok_ssconv_base_in"],
                test_data["ok_ssconv_meas_in"],
                test_data["ok_carbint_base_in"],
                test_data["ok_carbint_meas_in"],
                test_data["ok_energy_scnd_in"],
                test_data["ok_tsv_scale_fracs_in"],
                test_data["ok_tsv_shapes_in"],
                test_data["opts"],
                contrib_mseg_key="",
                ctrb_ms_pkg_prep=[],
                hp_rate=None,
                retro_rate_mseg=meas_retro_rate_bass_string,
                calc_sect_shapes="",
                lkg_fmeth_base=None,
                lkg_fmeth_meas=None,
                warn_list=warn_list,
            )
            warnings_bass_string_measure.append(lists_fraction_string[-1])

            # Correct list of output dicts
            lists_check_fraction = test_data["ok_out_fraction"][scn][k]
            # Compare each element of the lists of output dicts,
            # except for the warning messages
            for elem2 in range(0, len(lists_check_fraction)):
                # Handle possible NoneTypes or integers in the function output
                if lists_check_fraction[elem2] is not None and not isinstance(
                    lists_check_fraction[elem2], int
                ):
                    dict_check(lists_check_fraction[elem2], lists_fraction[elem2])
                else:
                    assert lists_check_fraction[elem2] == lists_fraction[elem2]

            # Correct list of output dicts
            lists_check_bass = test_data["ok_out_bass"][scn][k]
            # Compare each element of the lists of output dicts
            for elem2 in range(0, len(lists_check_bass)):
                # Handle possible NoneTypes in the function output
                if lists_check_bass[elem2] is not None and not isinstance(
                    lists_check_bass[elem2], int
                ):
                    dict_check(lists_check_bass[elem2], lists_bass[elem2])
                else:
                    assert lists_check_bass[elem2] == lists_bass[elem2]

            # Correct list of output dicts
            lists_check_fraction_string = test_data["ok_out_fraction_string"][scn][k]
            # Compare each element of the lists of output dicts
            for elem2 in range(0, len(lists_check_fraction_string)):
                # Handle possible NoneTypes in the function output
                if lists_check_fraction_string[elem2] is not None and not isinstance(
                    lists_check_fraction_string[elem2], int
                ):
                    dict_check(lists_check_fraction_string[elem2], lists_fraction_string[elem2])
                else:
                    assert lists_check_fraction_string[elem2] == lists_fraction_string[elem2]

            # Correct list of output dicts
            lists_check_bass_string = test_data["ok_out_bass_string"][scn][k]
            # Compare each element of the lists of output dicts
            for elem2 in range(0, len(lists_check_bass_string)):
                # Handle possible NoneTypes in the function output
                if lists_check_bass_string[elem2] is not None and not isinstance(
                    lists_check_bass_string[elem2], int
                ):
                    dict_check(lists_check_bass_string[elem2], lists_bass_string[elem2])
                else:
                    assert lists_check_bass_string[elem2] == lists_bass_string[elem2]

    for elem2 in range(0, len(warnings_check)):
        assert warnings_fraction_measure[elem2] == warnings_check[elem2]

    for elem2 in range(0, len(warnings_check)):
        assert warnings_bass_measure[elem2] == warnings_check[elem2]

    for elem2 in range(0, len(warnings_check)):
        assert warnings_fraction_string_measure[elem2] == warnings_check[elem2]

    for elem2 in range(0, len(warnings_check)):
        assert warnings_bass_string_measure[elem2] == warnings_check[elem2]


def test_overrides(test_data):
    """Test the 'partition_microsegment' function given valid inputs.

    Raises:
       AssertionError: If function yields unexpected results.
    """
    # Loop through 'ok_out' elements

    # Reset AEO time horizon and market entry/exit years
    test_data["measure_instance_bad_string"].handyvars.aeo_years = test_data["time_horizons"]
    test_data["measure_instance_bad_string"].market_entry_year = int(test_data["time_horizons"][0])
    test_data["measure_instance_bad_string"].market_exit_year = (
        int(test_data["time_horizons"][-1]) + 1
    )
    # Reset AEO time horizon and market entry/exit years
    test_data["measure_instance_bad_values"].handyvars.aeo_years = test_data["time_horizons"]
    test_data["measure_instance_bad_values"].market_entry_year = int(test_data["time_horizons"][0])
    test_data["measure_instance_bad_values"].market_exit_year = (
        int(test_data["time_horizons"][-1]) + 1
    )
    # Reset AEO time horizon and market entry/exit years
    test_data["measure_instance_wrong_name"].handyvars.aeo_years = test_data["time_horizons"]
    test_data["measure_instance_wrong_name"].market_entry_year = int(test_data["time_horizons"][0])
    test_data["measure_instance_wrong_name"].market_exit_year = (
        int(test_data["time_horizons"][-1]) + 1
    )

    # Set measure-specific retrofit rate to test
    meas_retro_rate_bad_string = test_data["measure_instance_bad_string"].retro_rate
    meas_retro_rate_bad_values = test_data["measure_instance_bad_values"].retro_rate
    meas_retro_rate_instance_wrong_name = test_data["measure_instance_wrong_name"].retro_rate

    warnings_check = [
        "WARNING: Diffusion parameters are not properly "
        "defined in the measure\n==>diffusion parameters set"
        " to 1 for every year.",
        "WARNING: Some declared "
        "diffusion fractions are greater than 1. Their value "
        "has been changed to 1.",
        "WARNING: Some declared "
        "diffusion fractions are smaller than 0. Their value"
        " has been changed to 0.",
        "WARNING: Not enough data were"
        " provided for first and last years of the considered "
        "simulation period.\n\tThe simulation will continue assuming"
        " plausible diffusion fraction values.",
        "WARNING: Diffusion parameters are not properly "
        "defined in the measure\n==>diffusion parameters set"
        " to 1 for every year.",
        "WARNING: Some declared "
        "diffusion fractions are greater than 1. Their value "
        "has been changed to 1.",
        "WARNING: Some declared "
        "diffusion fractions are smaller than 0. Their value"
        " has been changed to 0.",
        "WARNING: Not enough data were"
        " provided for first and last years of the considered "
        "simulation period.\n\tThe simulation will continue assuming"
        " plausible diffusion fraction values.",
        "WARNING: Diffusion parameters are not properly "
        "defined in the measure\n==>diffusion parameters set"
        " to 1 for every year.",
        "WARNING: Some declared "
        "diffusion fractions are greater than 1. Their value "
        "has been changed to 1.",
        "WARNING: Some declared "
        "diffusion fractions are smaller than 0. Their value"
        " has been changed to 0.",
        "WARNING: Not enough data were"
        " provided for first and last years of the considered "
        "simulation period.\n\tThe simulation will continue assuming"
        " plausible diffusion fraction values.",
        "WARNING: Diffusion parameters are not properly "
        "defined in the measure\n==>diffusion parameters set"
        " to 1 for every year.",
        "WARNING: Some declared "
        "diffusion fractions are greater than 1. Their value "
        "has been changed to 1.",
        "WARNING: Some declared "
        "diffusion fractions are smaller than 0. Their value"
        " has been changed to 0.",
        "WARNING: Not enough data were"
        " provided for first and last years of the considered "
        "simulation period.\n\tThe simulation will continue assuming"
        " plausible diffusion fraction values.",
    ]

    warn_list = []
    warnings_bad_string_measure = []
    warnings_bad_values_measure = []
    warnings_wrong_name_measure = []

    # Loop through two test schemes (Technical potential and Max
    # adoption potential)
    for scn in range(0, len(test_data["handyvars"].adopt_schemes_prep)):
        # Loop through two microsegment key chains (one applying
        # to new structure type, another to existing structure type)
        for k in range(0, len(test_data["ok_mskeys_in"])):
            # List of output dicts generated by the function
            lists_bad_string = test_data["measure_instance_bad_string"].partition_microsegment(
                test_data["handyvars"].adopt_schemes_prep[scn],
                test_data["ok_diffuse_params_in"],
                test_data["ok_mskeys_in"][k],
                test_data["ok_mskeys_swtch_in"],
                test_data["ok_bldg_sect_in"][k],
                test_data["ok_sqft_subst_in"][k],
                test_data["ok_mkt_scale_frac_in"],
                test_data["ok_new_bldg_constr"],
                test_data["ok_stock_in"],
                test_data["ok_energy_in"],
                test_data["ok_carb_in"],
                test_data["ok_fcarb_in"],
                test_data["ok_f_refr_in"],
                test_data["ok_base_cost_in"],
                test_data["ok_cost_meas_in"],
                test_data["ok_cost_energy_base_in"],
                test_data["ok_cost_energy_meas_in"],
                test_data["ok_relperf_in"],
                test_data["ok_life_base_in"],
                test_data["ok_life_meas_in"],
                test_data["ok_ssconv_base_in"],
                test_data["ok_ssconv_meas_in"],
                test_data["ok_carbint_base_in"],
                test_data["ok_carbint_meas_in"],
                test_data["ok_energy_scnd_in"],
                test_data["ok_tsv_scale_fracs_in"],
                test_data["ok_tsv_shapes_in"],
                test_data["opts"],
                contrib_mseg_key="",
                ctrb_ms_pkg_prep=[],
                hp_rate=None,
                retro_rate_mseg=meas_retro_rate_bad_string,
                calc_sect_shapes="",
                lkg_fmeth_base=None,
                lkg_fmeth_meas=None,
                warn_list=warn_list,
            )
            warnings_bad_string_measure.append(lists_bad_string[-1])

            lists_bad_values = test_data["measure_instance_bad_values"].partition_microsegment(
                test_data["handyvars"].adopt_schemes_prep[scn],
                test_data["ok_diffuse_params_in"],
                test_data["ok_mskeys_in"][k],
                test_data["ok_mskeys_swtch_in"],
                test_data["ok_bldg_sect_in"][k],
                test_data["ok_sqft_subst_in"][k],
                test_data["ok_mkt_scale_frac_in"],
                test_data["ok_new_bldg_constr"],
                test_data["ok_stock_in"],
                test_data["ok_energy_in"],
                test_data["ok_carb_in"],
                test_data["ok_fcarb_in"],
                test_data["ok_f_refr_in"],
                test_data["ok_base_cost_in"],
                test_data["ok_cost_meas_in"],
                test_data["ok_cost_energy_base_in"],
                test_data["ok_cost_energy_meas_in"],
                test_data["ok_relperf_in"],
                test_data["ok_life_base_in"],
                test_data["ok_life_meas_in"],
                test_data["ok_ssconv_base_in"],
                test_data["ok_ssconv_meas_in"],
                test_data["ok_carbint_base_in"],
                test_data["ok_carbint_meas_in"],
                test_data["ok_energy_scnd_in"],
                test_data["ok_tsv_scale_fracs_in"],
                test_data["ok_tsv_shapes_in"],
                test_data["opts"],
                contrib_mseg_key="",
                ctrb_ms_pkg_prep=[],
                hp_rate=None,
                retro_rate_mseg=meas_retro_rate_bad_values,
                calc_sect_shapes="",
                lkg_fmeth_base=None,
                lkg_fmeth_meas=None,
                warn_list=warn_list,
            )
            warnings_bad_values_measure.append(lists_bad_values[-1])

            lists_wrong_name = test_data["measure_instance_wrong_name"].partition_microsegment(
                test_data["handyvars"].adopt_schemes_prep[scn],
                test_data["ok_diffuse_params_in"],
                test_data["ok_mskeys_in"][k],
                test_data["ok_mskeys_swtch_in"],
                test_data["ok_bldg_sect_in"][k],
                test_data["ok_sqft_subst_in"][k],
                test_data["ok_mkt_scale_frac_in"],
                test_data["ok_new_bldg_constr"],
                test_data["ok_stock_in"],
                test_data["ok_energy_in"],
                test_data["ok_carb_in"],
                test_data["ok_fcarb_in"],
                test_data["ok_f_refr_in"],
                test_data["ok_base_cost_in"],
                test_data["ok_cost_meas_in"],
                test_data["ok_cost_energy_base_in"],
                test_data["ok_cost_energy_meas_in"],
                test_data["ok_relperf_in"],
                test_data["ok_life_base_in"],
                test_data["ok_life_meas_in"],
                test_data["ok_ssconv_base_in"],
                test_data["ok_ssconv_meas_in"],
                test_data["ok_carbint_base_in"],
                test_data["ok_carbint_meas_in"],
                test_data["ok_energy_scnd_in"],
                test_data["ok_tsv_scale_fracs_in"],
                test_data["ok_tsv_shapes_in"],
                test_data["opts"],
                contrib_mseg_key="",
                ctrb_ms_pkg_prep=[],
                hp_rate=None,
                retro_rate_mseg=meas_retro_rate_instance_wrong_name,
                calc_sect_shapes="",
                lkg_fmeth_base=None,
                lkg_fmeth_meas=None,
                warn_list=warn_list,
            )
            warnings_wrong_name_measure.append(lists_wrong_name[-1])

            # Correct list of output dicts
            lists_check_bad_string = test_data["ok_out_bad_string"][scn][k]
            # Compare each element of the lists of output dicts
            for elem2 in range(0, len(lists_check_bad_string)):
                # Handle possible NoneTypes in the function output
                if lists_check_bad_string[elem2] is not None and not isinstance(
                    lists_check_bad_string[elem2], int
                ):
                    dict_check(lists_check_bad_string[elem2], lists_bad_string[elem2])
                else:
                    assert lists_check_bad_string[elem2] == lists_bad_string[elem2]

            # Correct list of output dicts
            lists_check_bad_values = test_data["ok_out_bad_values"][scn][k]
            # Compare each element of the lists of output dicts
            for elem2 in range(0, len(lists_check_bad_values)):
                # Handle possible NoneTypes in the function output
                if lists_check_bad_values[elem2] is not None and not isinstance(
                    lists_check_bad_values[elem2], int
                ):
                    dict_check(lists_check_bad_values[elem2], lists_bad_values[elem2])
                else:
                    assert lists_check_bad_values[elem2] == lists_bad_values[elem2]

            # Correct list of output dicts
            lists_check_wrong_name = test_data["ok_out_wrong_name"][scn][k]
            # Compare each element of the lists of output dicts
            for elem2 in range(0, len(lists_check_wrong_name)):
                # Handle possible NoneTypes in the function output
                if lists_check_wrong_name[elem2] is not None and not isinstance(
                    lists_check_wrong_name[elem2], int
                ):
                    dict_check(lists_check_wrong_name[elem2], lists_wrong_name[elem2])
                else:
                    assert lists_check_wrong_name[elem2] == lists_wrong_name[elem2]

    for elem2 in range(0, len(warnings_bad_string_measure)):
        assert warnings_bad_string_measure[elem2] == warnings_check

    for elem2 in range(0, len(warnings_bad_values_measure)):
        assert warnings_bad_values_measure[elem2] == warnings_check

    for elem2 in range(0, len(warnings_wrong_name_measure)):
        assert warnings_wrong_name_measure[elem2] == warnings_check
