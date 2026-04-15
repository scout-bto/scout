#!/usr/bin/env python3

"""Tests for Time-Sensitive Valuation (TSV)"""

from scout.ecm_prep import Measure
from scout.ecm_prep_vars import UsefulVars, UsefulInputFiles
from scout.config import FilePaths as fp
import pytest
import numpy
import os
import copy
import itertools
from tests.ecm_prep_test.common import NullOpts, dict_check

# Import extracted test data
from tests.ecm_prep_test.test_data.time_sensitive_valuation_test_data import (
    sample_tsv_data,
    sample_cost_convert,
    sample_tsv_measures_in_features,
    sample_tsv_measure_in_metrics,
    sample_tsv_metric_settings,
    ok_tsv_facts_out_features_raw,
    ok_tsv_facts_out_metrics_raw,
)


@pytest.fixture(scope="module")
def tsv_test_data():
    """Fixture providing test data for TSV tests."""
    # Base directory
    base_dir = os.getcwd()
    # Null user options/options dict
    opts, opts_dict = [NullOpts().opts, NullOpts().opts_dict]
    # Dummy user settings needed to generate TSV metrics data params below
    opts_tsv_dummy = copy.deepcopy(opts)
    opts_tsv_dummy.alt_regions = "EMM"
    opts_tsv_dummy.tsv_metrics = ["1", "3", "1", "2", "2", "2"]
    handyfiles = UsefulInputFiles(opts_tsv_dummy)
    handyfiles.ash_emm_map = fp.CONVERT_DATA / "test" / "ASH_EMM_Mapping_USAMainland.txt"
    # Set supporting custom TSV shape test data location
    handyfiles.tsv_shape_data = (
        fp.ECM_DEF / "energyplus_data" / "energyplus_test_ok" / "savings_shapes"
    )
    # Set supporting TSV metrics test data location (all versions set to
    # same sample test data file)
    (
        handyfiles.tsv_metrics_data_tot_ref,
        handyfiles.tsv_metrics_data_tot_hr,
        handyfiles.tsv_metrics_data_net_ref,
        handyfiles.tsv_metrics_data_tot_hr,
    ) = ((fp.TSV_DATA / "test" / "tsv_hrs.csv") for n in range(4))
    handyvars = UsefulVars(base_dir, handyfiles, opts_tsv_dummy)
    # Hard code aeo_years to fit test years
    handyvars.aeo_years = ["2009", "2010"]
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
    handyvars.tsv_metrics_data["season days"] = {
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
    handyvars.tsv_metrics_data["peak days"] = {"summer": 270, "winter": 24}
    handyvars.tsv_metrics_data["hourly index"] = list(
        enumerate(itertools.product(range(365), range(24)))
    )
    sample_cost_energy_meas = {yr: 1 for yr in handyvars.aeo_years}
    sample_ash_czone_wts = handyvars.ash_emm_map
    sample_mskeys_features = (
        "primary",
        "FRCC",
        "large office",
        "electricity",
        "heating",
        "supply",
        "ASHP",
        "new",
    )
    sample_mskeys_metrics = numpy.append(
        numpy.tile(
            ("primary", "FRCC", "large office", "electricity", "heating", "supply", "ASHP", "new"),
            (8, 1),
        ),
        numpy.tile(
            ("primary", "ISNE", "large office", "electricity", "heating", "supply", "ASHP", "new"),
            (8, 1),
        ),
        axis=0,
    )
    sample_bldg_sect = "commercial"
    # Use imported sample_cost_convert and sample_tsv_measures_in_features
    # from test_data/tsv_test_data.py

    # Reset user options to reflect settings for TSV features tests
    opts_tsv_features = copy.deepcopy(opts)
    opts_dict_tsv_features = copy.deepcopy(opts_dict)
    opts_tsv_features.alt_regions = "EMM"
    opts_dict_tsv_features["alt_regions"] = "EMM"

    ok_tsv_measures_in_features = [
        Measure(base_dir, handyvars, handyfiles, opts_dict_tsv_features, **x)
        for x in sample_tsv_measures_in_features
    ]
    # Use imported sample_tsv_measure_in_metrics and sample_tsv_metric_settings
    # from test_data/tsv_test_data.py
    # Reset user options to reflect settings for TSV metrics tests
    opts_tsv_metrics_init, opts_dict_tsv_metrics_init = [
        copy.deepcopy(x) for x in [opts, opts_dict]
    ]
    opts_tsv_metrics_init.alt_regions, opts_dict_tsv_metrics_init["alt_regions"] = (
        "EMM" for n in range(2)
    )
    # Translate user metrics options sets to lists with a lengths equal to
    # that of the list of TSV metrics settings (sample_tsv_metric_settings)
    opts_tsv_metrics, opts_dict_tsv_metrics = [
        [copy.deepcopy(x) for n in range(len(sample_tsv_metric_settings))]
        for x in [opts_tsv_metrics_init, opts_dict_tsv_metrics_init]
    ]
    # Set appropriate TSV metrics settings for each element in the
    # lists of user options
    for ind in range(len(sample_tsv_metric_settings)):
        # Settings for user options object
        opts_tsv_metrics[ind].tsv_metrics = sample_tsv_metric_settings[ind]
        # Settings for dict of user options object that is used as
        # an input for Measure initialization
        opts_dict_tsv_metrics[ind]["tsv_metrics"] = sample_tsv_metric_settings[ind]
    # Initialize TSV metric test measures using appropriate input settings
    ok_tsv_measures_in_metrics = [
        Measure(base_dir, handyvars, handyfiles, opts_dict_tsv_metrics[ind], **x)
        for x in sample_tsv_measure_in_metrics
        for ind in range(len(sample_tsv_metric_settings))
    ]
    # Make two copies of user options object for TSV metrics test to match
    # 2 measures that are tested with these options (see
    # sample_tsv_measure_in_metrics)
    opts_tsv_metrics *= 2
    # Use imported ok_tsv_facts_out_features_raw from test_data/tsv_test_data.py
    # and extend it for multiple years
    import copy as copy_module

    ok_tsv_facts_out_features = copy_module.deepcopy(ok_tsv_facts_out_features_raw)
    # Extend expected TSV feature outputs for cost and carbon across
    # multiple projection yrs (assuming same inputs/outputs for each year)
    for meas_out_features in ok_tsv_facts_out_features:
        for var in ["cost", "carbon"]:
            for scn in ["baseline", "efficient"]:
                meas_out_features[var][scn] = {
                    yr: meas_out_features[var][scn] for yr in handyvars.aeo_years
                }
    # Use imported ok_tsv_facts_out_metrics_raw from test_data/tsv_test_data.py
    # and extend it for multiple years
    ok_tsv_facts_out_metrics = copy_module.deepcopy(ok_tsv_facts_out_metrics_raw)
    # Extend expected TSV metrics outputs for cost and carbon across
    # multiple projection yrs (assuming same inputs/outputs for each year)
    for meas_out_metrics in ok_tsv_facts_out_metrics:
        for var in ["cost", "carbon"]:
            for scn in ["baseline", "efficient"]:
                meas_out_metrics[var][scn] = {
                    yr: meas_out_metrics[var][scn] for yr in handyvars.aeo_years
                }

    # Use extracted sample_tsv_data from external file
    # (imported at top of file)

    return {
        "opts_tsv_features": opts_tsv_features,
        "opts_tsv_metrics": opts_tsv_metrics,
        "sample_cost_energy_meas": sample_cost_energy_meas,
        "sample_ash_czone_wts": sample_ash_czone_wts,
        "sample_mskeys_features": sample_mskeys_features,
        "sample_mskeys_metrics": sample_mskeys_metrics,
        "sample_bldg_sect": sample_bldg_sect,
        "sample_cost_convert": sample_cost_convert,
        "sample_tsv_data": sample_tsv_data,
        "ok_tsv_measures_in_features": ok_tsv_measures_in_features,
        "ok_tsv_measures_in_metrics": ok_tsv_measures_in_metrics,
        "ok_tsv_facts_out_features": ok_tsv_facts_out_features,
        "ok_tsv_facts_out_metrics": ok_tsv_facts_out_metrics,
    }


def test_load_modification(tsv_test_data):
    """Test 'gen_tsv_facts' and nested 'apply_tsv' given valid inputs."""
    # Tests for measures with time sensitive valuation features
    for idx, measure in enumerate(tsv_test_data["ok_tsv_measures_in_features"]):
        # Generate and test re-weighting factors against expected values
        gen_tsv_facts_out_features = measure.gen_tsv_facts(
            tsv_test_data["sample_tsv_data"],
            tsv_test_data["sample_mskeys_features"],
            tsv_test_data["sample_bldg_sect"],
            tsv_test_data["sample_cost_convert"],
            tsv_test_data["opts_tsv_features"],
            tsv_test_data["sample_cost_energy_meas"],
        )
        dict_check(gen_tsv_facts_out_features[0], tsv_test_data["ok_tsv_facts_out_features"][idx])
    # Test for measure with time sensitive valuation metrics
    for idx in range(len(tsv_test_data["ok_tsv_measures_in_metrics"])):
        measure = tsv_test_data["ok_tsv_measures_in_metrics"][idx]
        # Generate and test re-weighting factors against expected values
        gen_tsv_facts_out_metrics = measure.gen_tsv_facts(
            tsv_test_data["sample_tsv_data"],
            tsv_test_data["sample_mskeys_metrics"][idx],
            tsv_test_data["sample_bldg_sect"],
            tsv_test_data["sample_cost_convert"],
            tsv_test_data["opts_tsv_metrics"][idx],
            tsv_test_data["sample_cost_energy_meas"],
        )
        dict_check(gen_tsv_facts_out_metrics[0], tsv_test_data["ok_tsv_facts_out_metrics"][idx])
