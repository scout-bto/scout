#!/usr/bin/env python3

"""Shared fixtures and configuration for market updates tests."""

from scout.ecm_prep import Measure
from scout.ecm_prep_vars import UsefulVars, UsefulInputFiles
import pytest
import numpy
import os
import copy
from pathlib import Path
from tests.ecm_prep_test.common import NullOpts

# Import extracted test data
from tests.ecm_prep_test.test_data.market_updates_test_data import (
    ok_tpmeas_fullchk_break_out,
    sample_cpl_in,
    ok_tpmeas_partchk_msegout,
    sample_cpl_in_state,
    sample_cpl_in_emm,
    sample_mseg_in,
    ok_hpmeas_rates_breakouts,
    ok_partialmeas_in,
    ok_hpmeas_rates_mkts_out,
    ok_tpmeas_fullchk_msegout,
    sample_mseg_in_emm,
    sample_mseg_in_state,
    ok_tpmeas_partchk_msegout_emm,
    ok_tpmeas_partchk_msegout_state,
    ok_tpmeas_partchk_msegout_state_regadj,
    ok_fmeth_measures_in,
    ok_frefr_measures_in,
    frefr_fug_emissions,
    fmeth_fug_emissions,
    frefr_hp_rates,
    fmeth_carb_int,
    frefr_carb_int,
    fmeth_ecosts,
    frefr_ecosts,
    ok_measures_in,
    ok_distmeas_in as ok_distmeas_in_data,
    failmeas_in,
    warnmeas_in as warnmeas_in_data,
    ok_hp_measures_in,
    ok_tpmeas_fullchk_competechoiceout,
    ok_tpmeas_fullchk_supplydemandout,
    ok_mapmas_partchck_msegout,
    ok_partialmeas_out,
    ok_map_frefr_mkts_out,
)


@pytest.fixture(scope="module")
def market_test_data():
    """Fixture providing test data for market updates tests."""
    # Base directory
    base_dir = os.getcwd()
    # Null user options/options dict
    opts, opts_dict = [NullOpts().opts, NullOpts().opts_dict]
    # National-level variables (AIA regions)
    handyfiles = UsefulInputFiles(opts)
    handyvars = UsefulVars(base_dir, handyfiles, opts)
    handyvars.com_eqp_eus_nostk = [
        "lighting",
        "PCs",
        "non-PC office equipment",
        "office equipment",
        "data center",
        "MELs",
    ]
    # Site energy assessment settings
    opts_site_energy, opts_site_energy_dict = [copy.deepcopy(x) for x in [opts, opts_dict]]
    opts_site_energy.site_energy, opts_site_energy_dict["site_energy"] = (True for n in range(2))
    # Regional-level variables (EIA EMM regions)
    opts_emm, opts_emm_dict = [copy.deepcopy(x) for x in [opts, opts_dict]]
    opts_emm.alt_regions, opts_emm_dict["alt_regions"] = ("EMM" for n in range(2))
    opts_emm.site_energy, opts_emm_dict["site_energy"] = (True for n in range(2))
    handyfiles_emm = UsefulInputFiles(opts_emm)
    handyvars_emm = UsefulVars(base_dir, handyfiles_emm, opts_emm)
    # Regional-level variables (states)
    opts_state, opts_state_dict = [copy.deepcopy(x) for x in [opts, opts_dict]]
    opts_state.alt_regions, opts_state_dict["alt_regions"] = ("State" for n in range(2))
    opts_state.site_energy, opts_state_dict["site_energy"] = (True for n in range(2))
    handyfiles_state = UsefulInputFiles(opts_state)
    handyfiles_state.local_cost_adj = (
        Path(__file__).parent.parent.parent / "test_files" / "loc_cost_adj_test.csv"
    )
    handyvars_state = UsefulVars(base_dir, handyfiles_state, opts_state)
    # Save reg_cost_adj before suppressing it; the regadj deep copy is made later,
    # after all other handyvars_state overrides are applied
    _saved_reg_cost_adj = handyvars_state.reg_cost_adj
    handyvars_state.reg_cost_adj = None
    # Fuel switching with exogenous rates
    opts_hp_rates, opts_hp_rates_dict = [copy.deepcopy(x) for x in [opts_emm, opts_emm_dict]]
    opts_hp_rates.split_fuel, opts_hp_rates_dict["split_fuel"] = (True for n in range(2))
    opts_hp_rates.exog_hp_rates, opts_hp_rates_dict["exog_hp_rates"] = (
        ["gh-aggressive", "1"] for n in range(2)
    )
    opts_hp_rates.adopt_scn_usr, opts_hp_rates_dict["adopt_scn_usr"] = (
        ["Max adoption potential"] for n in range(2)
    )
    handyvars_hp_rates = UsefulVars(base_dir, handyfiles_emm, opts_hp_rates)
    handyvars_hp_rates.hp_rates_reg_map = {
        "midwest": ["SPPN", "MISW", "SPPC", "MISC", "PJMW", "PJMC", "MISE"],
        "northeast": ["PJME", "NYCW", "NYUP", "ISNE"],
        "south": ["SPPS", "TRE", "MISS", "SRCE", "PJMD", "SRCA", "SRSE", "FRCC"],
        "west": ["NWPP", "BASN", "RMRG", "SRSG", "CASO", "CANO"],
    }
    handyvars_hp_rates.hp_rates = {
        "data (by scenario)": {
            "gh-aggressive": {
                "south": {
                    "residential": {
                        "electricity": {
                            "heating": {
                                # Assume same rates as NG for simplicity
                                "resistance heat": {
                                    "existing": {"2009": 0.07500000000000001, "2010": 0.1},
                                    "new": {"2009": 0.29, "2010": 0.33},
                                }
                            }
                        },
                        "natural gas": {
                            "heating": {
                                "furnace (NG)": {
                                    "existing": {"2009": 0.07500000000000001, "2010": 0.1},
                                    "new": {"2009": 0.29, "2010": 0.33},
                                }
                            }
                        },
                    }
                }
            }
        }
    }
    # Fuel switching with no exogenous rates
    opts_hp_no_rates, opts_hp_no_rates_dict = [
        copy.deepcopy(x) for x in [opts_hp_rates, opts_hp_rates_dict]
    ]
    opts_hp_no_rates.exog_hp_rates, opts_hp_no_rates_dict["exog_hp_rates"] = (
        False for n in range(2)
    )
    handyvars_hp_norates = UsefulVars(base_dir, handyfiles_emm, opts_hp_no_rates)
    handyvars_hp_rates.out_break_in, handyvars_hp_norates.out_break_in = (
        {
            "TRE": {
                "Residential (Existing)": {
                    "Heating (Equip.)": {"Electric": {}, "Non-Electric": {}},
                    "Cooling (Equip.)": {"Electric": {}, "Non-Electric": {}},
                }
            }
        }
        for n in range(2)
    )
    # Heat pump calculations where cooling costs of comparable baseline equipment
    # are counted alongside heating costs, by removing the 'no_lnkd_stk_costs' option
    # that is attached to other tested heat pump measures
    opts_coolcosts, opts_coolcosts_dict = [
        copy.deepcopy(x) for x in [opts_hp_rates, opts_hp_rates_dict]
    ]
    opts_coolcosts.no_lnkd_stk_costs, opts_coolcosts_dict["no_lnkd_stk_costs"] = (
        None for n in range(2)
    )
    # Fugitive emissions for supply chain methane leakage
    opts_fmeth, opts_fmeth_dict = [
        [copy.deepcopy(n) for x in range(len(ok_fmeth_measures_in))]
        for n in [opts_emm, opts_emm_dict]
    ]
    # Initialize measure-specific handy vars
    handyvars_fmeth = [None for x in range(len(ok_fmeth_measures_in))]
    # Initialize measure-specific low GWP settings
    mth_lkg_settings = [["1", "1", "1"], ["1", "1", "2"], ["1", "1", "3"], ["1", "1", "1"]]
    # Loop through refrigerant emissions measures and hard code user
    # settings and handy vars
    for x in range(len(ok_fmeth_measures_in)):
        # Measure-specific user options
        opts_fmeth[x].adopt_scn_restrict, opts_fmeth_dict[x]["adopt_scn_restrict"] = (
            ["Technical potential"] for n in range(2)
        )
        opts_fmeth[x].fugitive_emissions, opts_fmeth_dict[x]["fugitive_emissions"] = (
            mth_lkg_settings[x] for n in range(2)
        )
        # Measure-specific handy vars
        handyvars_fmeth[x] = UsefulVars(base_dir, handyfiles_emm, opts_fmeth[x])
        handyvars_fmeth[x].fugitive_emissions_map = numpy.array(
            [
                (
                    "TRE",
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                )
            ],
            dtype=[
                ("State", "<U25"),
                ("AL", "<f8"),
                ("AK", "<f8"),
                ("AZ", "<f8"),
                ("AR", "<f8"),
                ("CA", "<f8"),
                ("CO", "<f8"),
                ("CT", "<f8"),
                ("DE", "<f8"),
                ("DC", "<f8"),
                ("FL", "<f8"),
                ("GA", "<f8"),
                ("HI", "<f8"),
                ("ID", "<f8"),
                ("IL", "<f8"),
                ("IN", "<f8"),
                ("IA", "<f8"),
                ("KS", "<f8"),
                ("KY", "<f8"),
                ("LA", "<f8"),
                ("ME", "<f8"),
                ("MD", "<f8"),
                ("MA", "<f8"),
                ("MI", "<f8"),
                ("MN", "<f8"),
                ("MS", "<f8"),
                ("MO", "<f8"),
                ("MT", "<f8"),
                ("NE", "<f8"),
                ("NV", "<f8"),
                ("NH", "<f8"),
                ("NJ", "<f8"),
                ("NM", "<f8"),
                ("NY", "<f8"),
                ("NC", "<f8"),
                ("ND", "<f8"),
                ("OH", "<f8"),
                ("OK", "<f8"),
                ("OR", "<f8"),
                ("PA", "<f8"),
                ("RI", "<f8"),
                ("SC", "<f8"),
                ("SD", "<f8"),
                ("TN", "<f8"),
                ("TX", "<f8"),
                ("UT", "<f8"),
                ("VT", "<f8"),
                ("VA", "<f8"),
                ("WA", "<f8"),
                ("WV", "<f8"),
                ("WI", "<f8"),
                ("WY", "<f8"),
            ],
        )
        handyvars_fmeth[x].fug_emissions = fmeth_fug_emissions
    # Sample refrigerant emissions measures to initialize below
    # Fugitive emissions for refrigerant leakage
    opts_frefr, opts_frefr_dict = [
        [copy.deepcopy(n) for x in range(len(ok_frefr_measures_in))]
        for n in [opts_emm, opts_emm_dict]
    ]
    # Initialize measure-specific handy vars
    handyvars_frefr = [None for x in range(len(ok_frefr_measures_in))]
    # Initialize measure-specific low GWP settings
    low_gwp_settings = [
        ["2", "3"],
        ["2", "2"],
        ["2", "2"],
        ["2", "3"],
        ["2", "3"],
        ["2", "2"],
        ["2", "3"],
        ["2", "3"],
        ["2", "3"],
        ["2", "1", "3"],
    ]
    # Initialize measure-specific exogenous HP rate settings
    exog_hp_rates_settings = (
        [["gh-aggressive", "1"] for n in (range(len(ok_frefr_measures_in) - 2))] + [False] + [False]
    )
    # Sample exogenous HP switching rates to use in fugitive
    # refrigerant emissions calculations; for simplicity, set rates to 1
    # (imported from frefr_hp_rates)
    # Loop through refrigerant emissions measures and hard code user
    # settings and handy vars
    for x in range(len(ok_frefr_measures_in)):
        # Measure-specific user options
        opts_frefr[x].adopt_scn_restrict, opts_frefr_dict[x]["adopt_scn_restrict"] = (
            ["Max adoption potential"] for n in range(2)
        )
        opts_frefr[x].fugitive_emissions, opts_frefr_dict[x]["fugitive_emissions"] = (
            low_gwp_settings[x] for n in range(2)
        )
        opts_frefr[x].exog_hp_rates, opts_frefr_dict[x]["exog_hp_rates"] = (
            exog_hp_rates_settings[x] for n in range(2)
        )
        # Measure-specific handy vars
        handyvars_frefr[x] = UsefulVars(base_dir, handyfiles_emm, opts_frefr[x])
        # Reset exogenous HP rate settings to test vals where applicable
        if handyvars_frefr[x].hp_rates is not None:
            handyvars_frefr[x].hp_rates = frefr_hp_rates
        # Set refrigerant fugitive emissions data
        handyvars_frefr[x].fug_emissions = frefr_fug_emissions
    # Hard code sample fugitive refrigerant emissions input data
    # Hard code aeo_years to fit test years
    (
        handyvars.aeo_years,
        handyvars_emm.aeo_years,
        handyvars_state.aeo_years,
        handyvars_hp_rates.aeo_years,
        handyvars_hp_norates.aeo_years,
        fmeth_aeo_years,
        frefr_aeo_years,
    ) = (["2009", "2010"] for n in range(7))
    for x in range(len(ok_fmeth_measures_in)):
        handyvars_fmeth[x].aeo_years = fmeth_aeo_years
    for x in range(len(ok_frefr_measures_in)):
        handyvars_frefr[x].aeo_years = frefr_aeo_years
    handyvars.retro_rate = {yr: 0.02 for yr in handyvars.aeo_years}
    (
        handyvars_emm.retro_rate,
        handyvars_state.retro_rate,
        handyvars_hp_rates.retro_rate,
        handyvars_hp_norates.retro_rate,
        fmeth_retro_rate,
        frefr_retro_rate,
    ) = ({yr: 0.01 for yr in handyvars.aeo_years} for n in range(6))
    for x in range(len(ok_fmeth_measures_in)):
        handyvars_fmeth[x].retro_rate = fmeth_retro_rate
    for x in range(len(ok_frefr_measures_in)):
        handyvars_frefr[x].retro_rate = frefr_retro_rate
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
            },
            "large office": {
                "heating": 1,
                "cooling": 1,
                "water heating": 1,
                "ventilation": 1,
                "cooking": 1,
                "lighting": 1,
                "refrigeration": 1,
            },
        }
    }
    # Set test capacity factors to dummy values above
    (
        handyvars.cap_facts,
        handyvars_emm.cap_facts,
        handyvars_state.cap_facts,
        handyvars_hp_rates.cap_facts,
        handyvars_hp_norates.cap_facts,
        fmeth_cap_facts,
        frefr_cap_facts,
    ) = (cf_ones for n in range(7))
    for x in range(len(ok_fmeth_measures_in)):
        handyvars_fmeth[x].cap_facts = fmeth_cap_facts
    for x in range(len(ok_frefr_measures_in)):
        handyvars_frefr[x].cap_facts = frefr_cap_facts
    # Hard code carbon intensity, site-source conversion, and cost data for
    # tests such that these data are not dependent on an input file that
    # may change in the future
    handyvars.ss_conv = {
        "electricity": {"2009": 3.19, "2010": 3.20},
        "natural gas": {"2009": 1.01, "2010": 1.01},
        "distillate": {"2009": 1.01, "2010": 1.01},
        "other fuel": {"2009": 1.01, "2010": 1.01},
    }
    handyvars.carb_int = {
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
    handyvars.ecosts = {
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
    # Hard code carbon intensity, site-source conversion, and cost data
    # for tests of regional-level (EMM) analysis.
    (
        handyvars_emm.regions,
        handyvars_hp_rates.regions,
        handyvars_hp_norates.regions,
        fmeth_regions,
        frefr_regions,
    ) = ("EMM" for n in range(5))
    for x in range(len(ok_fmeth_measures_in)):
        handyvars_fmeth[x].regions = fmeth_regions
    for x in range(len(ok_frefr_measures_in)):
        handyvars_frefr[x].regions = frefr_regions
    handyvars_state.regions = "State"
    (
        handyvars_emm.ss_conv,
        handyvars_state.ss_conv,
        handyvars_hp_rates.ss_conv,
        handyvars_hp_norates.ss_conv,
        fmeth_ss_conv,
        frefr_ss_conv,
    ) = (
        {
            "electricity": {"2009": 2.917505, "2010": 2.889269},
            "natural gas": {"2009": 1.01, "2010": 1.01},
            "distillate": {"2009": 1.01, "2010": 1.01},
            "other fuel": {"2009": 1.01, "2010": 1.01},
        }
        for n in range(6)
    )
    for x in range(len(ok_fmeth_measures_in)):
        handyvars_fmeth[x].ss_conv = fmeth_ss_conv
    for x in range(len(ok_frefr_measures_in)):
        handyvars_frefr[x].ss_conv = frefr_ss_conv
    (
        handyvars_emm.carb_int,
        handyvars_hp_rates.carb_int,
        handyvars_hp_rates.carb_int,
        handyvars_hp_norates.carb_int,
    ) = (fmeth_carb_int for n in range(4))
    for x in range(len(ok_fmeth_measures_in)):
        handyvars_fmeth[x].carb_int = fmeth_carb_int
    for x in range(len(ok_frefr_measures_in)):
        handyvars_frefr[x].carb_int = frefr_carb_int
    handyvars_state.carb_int = {
        "residential": {
            "electricity": {
                "NH": {"2009": 3.15e-08, "2010": 2.37e-08},
                "CT": {"2009": 1.306e-07, "2010": 1.199e-07},
            },
            "natural gas": {"2009": 56.51576602, "2010": 54.91762852},
            "distillate": {"2009": 49.5454521, "2010": 52.59751597},
            "other fuel": {"2009": 49.5454521, "2010": 52.59751597},
        },
        "commercial": {
            "electricity": {
                "NH": {"2009": 3.15e-08, "2010": 2.37e-08},
                "CT": {"2009": 1.306e-07, "2010": 1.199e-07},
            },
            "natural gas": {"2009": 56.51576602, "2010": 54.91762852},
            "distillate": {"2009": 49.5454521, "2010": 52.59751597},
            "other fuel": {"2009": 49.5454521, "2010": 52.59751597},
        },
    }
    handyvars_emm.ecosts, handyvars_hp_rates.ecosts, handyvars_hp_norates.ecosts = (
        fmeth_ecosts for n in range(3)
    )
    for x in range(len(ok_fmeth_measures_in)):
        handyvars_fmeth[x].ecosts = fmeth_ecosts
    for x in range(len(ok_frefr_measures_in)):
        handyvars_frefr[x].ecosts = frefr_ecosts
    handyvars_state.ecosts = {
        "residential": {
            "electricity": {
                "NH": {"2009": 57.729191, "2010": 60.453107},
                "CT": {"2009": 29.823857, "2010": 26.964537},
            },
            "natural gas": {"2009": 11.28, "2010": 10.78},
            "distillate": {"2009": 21.23, "2010": 20.59},
            "other fuel": {"2009": 21.23, "2010": 20.59},
        },
        "commercial": {
            "electricity": {
                "NH": {"2009": 51.503224, "2010": 52.344666},
                "CT": {"2009": 27.985639, "2010": 24.313013},
            },
            "natural gas": {"2009": 11.28, "2010": 10.78},
            "distillate": {"2009": 21.23, "2010": 20.59},
            "other fuel": {"2009": 21.23, "2010": 20.59},
        },
    }
    handyvars.ccosts = {"2009": 33, "2010": 33}
    (
        handyvars_emm.ccosts,
        handyvars_state.ccosts,
        handyvars_hp_rates.ccosts,
        handyvars_hp_norates.ccosts,
        fmeth_ccosts,
        frefr_ccosts,
    ) = ({"2009": 41, "2010": 42} for n in range(6))
    for x in range(len(ok_fmeth_measures_in)):
        handyvars_fmeth[x].ccosts = fmeth_ccosts
    for x in range(len(ok_frefr_measures_in)):
        handyvars_frefr[x].ccosts = frefr_ccosts

    # Zero out electrical infrastructure costs for now in tests
    (
        handyvars.elec_infr_costs,
        handyvars_emm.elec_infr_costs,
        handyvars_state.elec_infr_costs,
        handyvars_hp_rates.elec_infr_costs,
        handyvars_hp_norates.elec_infr_costs,
        fmeth_elec_infr_costs,
        frefr_elec_infr_costs,
    ) = (
        {
            "panel replacement": 0,
            "panel management": 0,  # BENEFIT panels cost data, averaged across regions
            "240V circuit": 0,  # BTB "typical" dif., central ASHP w/ and w/o new circuit
        }
        for n in range(7)
    )
    for x in range(len(ok_fmeth_measures_in)):
        handyvars_fmeth[x].elec_infr_costs = fmeth_elec_infr_costs
    for x in range(len(ok_frefr_measures_in)):
        handyvars_frefr[x].elec_infr_costs = frefr_elec_infr_costs
    # Deep copy handyvars_state (after all overrides) for the regadj test;
    # restore the original reg_cost_adj that was saved before suppression
    handyvars_state_regadj = copy.deepcopy(handyvars_state)
    handyvars_state_regadj.reg_cost_adj = _saved_reg_cost_adj
    # Hard code mapping array used to handle alternate regional breakouts
    # of measure performance or cost (e.g., IECC)
    handyvars.alt_attr_brk_map = {
        "IECC": numpy.array(
            [
                (b"IECC_CZ1", 0, 0, 0.125, 0.125, 0.125),
                (b"IECC_CZ2", 0, 0.5, 0.125, 0.125, 0.125),
                (b"IECC_CZ3", 0.25, 0, 0.125, 0.125, 0.125),
                (b"IECC_CZ4", 0.75, 0, 0.125, 0.125, 0.125),
                (b"IECC_CZ5", 0, 0.5, 0.125, 0.125, 0.125),
                (b"IECC_CZ6", 0, 0, 0.125, 0.125, 0.125),
                (b"IECC_CZ7", 0, 0, 0.125, 0.125, 0.125),
                (b"IECC_CZ8", 0, 0, 0.125, 0.125, 0.125),
            ],
            dtype=[
                ("IECC", "<U25"),
                ("AIA_CZ1", "<f8"),
                ("AIA_CZ2", "<f8"),
                ("AIA_CZ3", "<f8"),
                ("AIA_CZ4", "<f8"),
                ("AIA_CZ5", "<f8"),
            ],
        ),
        "levels": str(["IECC_CZ" + str(n + 1) for n in range(8)]),
    }
    # Note that in practice these coefficients are defined separately for each end use;
    # set to same coefficient values for convenience in testing
    handyvars.deflt_res_choice = {
        "electric": {
            x: [-0.01, -0.12]
            for x in [
                "heating",
                "secondary heating",
                "cooling",
                "water heating",
                "cooking",
                "drying",
                "lighting",
                "refrigeration",
                "ceiling fan",
                "fans and pumps",
                "computers",
                "TVs",
                "other",
            ]
        },
        "non-electric": {
            x: [-0.01, -0.12]
            for x in [
                "heating",
                "secondary heating",
                "cooling",
                "water heating",
                "cooking",
                "drying",
            ]
        },
    }
    convert_data = {}
    tsv_data = {}
    ok_tpmeas_fullchk_in = [
        Measure(base_dir, handyvars, handyfiles, opts_dict, **x) for x in ok_measures_in[0:5]
    ]
    ok_tpmeas_partchk_in = [
        Measure(base_dir, handyvars, handyfiles, opts_dict, **x) for x in ok_measures_in[5:24]
    ]
    ok_tpmeas_partchk_emm_in = [
        Measure(base_dir, handyvars_emm, handyfiles_emm, opts_emm_dict, **x)
        for x in ok_measures_in[26:28]
    ]
    ok_tpmeas_partchk_state_in = [
        Measure(base_dir, handyvars_state, handyfiles_state, opts_state_dict, **ok_measures_in[28])
    ]
    ok_tpmeas_partchk_state_regadj_in = [
        Measure(
            base_dir,
            handyvars_state_regadj,
            handyfiles_state,
            opts_state_dict,
            **ok_measures_in[28]
            )
    ]
    ok_mapmeas_partchk_in = [
        Measure(base_dir, handyvars, handyfiles, opts_dict, **x) for x in ok_measures_in[24:26]
    ]
    ok_measures_site_energy = [
        {
            "name": "sample measure 1 - site energy",
            "markets": None,
            "installed_cost": 25,
            "cost_units": "2014$/unit",
            "energy_efficiency": {
                "AIA_CZ1": {"heating": 30, "cooling": 25},
                "AIA_CZ2": {"heating": 30, "cooling": 15},
            },
            "energy_efficiency_units": "COP",
            "market_entry_year": None,
            "market_exit_year": None,
            "product_lifetime": 1,
            "market_scaling_fractions": None,
            "market_scaling_fractions_source": None,
            "measure_type": "full service",
            "structure_type": ["new", "existing"],
            "bldg_type": "single family home",
            "climate_zone": ["AIA_CZ1", "AIA_CZ2"],
            "fuel_type": "electricity",
            "fuel_switch_to": None,
            "end_use": ["heating", "cooling"],
            "technology": ["resistance heat", "ASHP", "GSHP", "room AC"],
        }
    ]
    ok_tpmeas_sitechk_in = [
        Measure(base_dir, handyvars, handyfiles, opts_site_energy_dict, **x)
        for x in ok_measures_site_energy
    ]
    # Seed random number generator to yield consistent retrofit rate
    # results
    numpy.random.seed(1234)
    ok_distmeas_in = [
        Measure(base_dir, handyvars, handyfiles, opts_dict, **x) for x in ok_distmeas_in_data
    ]
    failmeas_inputs_in = [
        Measure(base_dir, handyvars, handyfiles, opts_dict, **x) for x in failmeas_in[0:-1]
    ]
    warnmeas_in = [
        Measure(base_dir, handyvars, handyfiles, opts_dict, **x) for x in warnmeas_in_data
    ]
    ok_mapmeas_hp_chk_in = [
        Measure(base_dir, handyvars_hp_rates, handyfiles_emm, opts_hp_rates_dict, **x)
        for x in ok_hp_measures_in[0:3]
    ]
    ok_mapmeas_hp_chk_in.extend(
        [
            Measure(base_dir, handyvars_hp_norates, handyfiles_emm, opts_hp_rates_dict, **x)
            for x in ok_hp_measures_in[3:]
        ]
    )
    ok_tp_fmeth_chk_in = [
        Measure(base_dir, handyvars_fmeth[ind], handyfiles_emm, opts_fmeth_dict[ind], **x)
        for ind, x in enumerate(ok_fmeth_measures_in)
    ]
    ok_map_frefr_chk_in = [
        Measure(base_dir, handyvars_frefr[ind], handyfiles_emm, opts_frefr_dict[ind], **x)
        for ind, x in enumerate(ok_frefr_measures_in)
    ]
    # Correct consumer choice dict outputs
    ok_tpmeas_fullchk_msegadjout = [
        {
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
        {
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
        {
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
    ]
    ok_distmeas_out = [
        [120.86, 100, 790.91, 100, 1.0, 1, {yr: 0.02 for yr in handyvars.aeo_years}, 1],
        [11.9, 100, 374.73, 100, 1.28, 100, {yr: 0.02 for yr in handyvars.aeo_years}, 1],
        [56.12, 100, 6577018856.89, 100, 1.0, 1, {yr: 0.02 for yr in handyvars.aeo_years}, 1],
        [10.91, 1, 45, 1, 1, 1, {yr: 0.06 for yr in handyvars.aeo_years}, 100],
    ]
    ok_tpmeas_sitechk_msegout = [
        {
            "stock": {
                "total": {"all": {"2009": 32, "2010": 32}, "measure": {"2009": 32, "2010": 32}},
                "competed": {"all": {"2009": 32, "2010": 32}, "measure": {"2009": 32, "2010": 32}},
            },
            "energy": {
                "total": {
                    "baseline": {"2009": 229.68 / 3.19, "2010": 230.4 / 3.20},
                    "efficient": {"2009": 117.0943 / 3.19, "2010": 117.4613 / 3.20},
                },
                "competed": {
                    "baseline": {"2009": 229.68 / 3.19, "2010": 230.4 / 3.20},
                    "efficient": {"2009": 117.0943 / 3.19, "2010": 117.4613 / 3.20},
                },
            },
            "carbon": {
                "total": {
                    "baseline": {"2009": 13056.63, "2010": 12941.16},
                    "efficient": {"2009": 6656.461, "2010": 6597.595},
                },
                "competed": {
                    "baseline": {"2009": 13056.63, "2010": 12941.16},
                    "efficient": {"2009": 6656.461, "2010": 6597.595},
                },
            },
            "cost": {
                "stock": {
                    "total": {
                        "baseline": {"2009": 208, "2010": 208},
                        "efficient": {"2009": 800, "2010": 800},
                    },
                    "competed": {
                        "baseline": {"2009": 208, "2010": 208},
                        "efficient": {"2009": 800, "2010": 800},
                    },
                },
                "energy": {
                    "total": {
                        "baseline": {"2009": 2328.955, "2010": 2227.968},
                        "efficient": {"2009": 1187.336, "2010": 1135.851},
                    },
                    "competed": {
                        "baseline": {"2009": 2328.955, "2010": 2227.968},
                        "efficient": {"2009": 1187.336, "2010": 1135.851},
                    },
                },
                "carbon": {
                    "total": {
                        "baseline": {"2009": 430868.63, "2010": 427058.3},
                        "efficient": {"2009": 219663.21, "2010": 217720.65},
                    },
                    "competed": {
                        "baseline": {"2009": 430868.63, "2010": 427058.3},
                        "efficient": {"2009": 219663.21, "2010": 217720.65},
                    },
                },
            },
            "lifetime": {"baseline": {"2009": 33.75, "2010": 33.75}, "measure": 1},
        }
    ]
    ok_warnmeas_out = [
        [
            (
                "WARNING: 'warn measure 1' has invalid "
                "sub-market scaling fraction source title, author, "
                "organization, and/or year information"
            ),
            (
                "WARNING: 'warn measure 1' has invalid "
                "sub-market scaling fraction source URL information"
            ),
            (
                "WARNING: 'warn measure 1' has invalid "
                "sub-market scaling fraction derivation information"
            ),
            (
                "WARNING (CRITICAL): 'warn measure 1' has "
                "insufficient sub-market source information and "
                "will be removed from analysis"
            ),
        ],
        [
            (
                "WARNING: 'warn measure 2' has invalid "
                "sub-market scaling fraction source URL information"
            ),
            (
                "WARNING: 'warn measure 2' has invalid "
                "sub-market scaling fraction derivation information"
            ),
            (
                "WARNING (CRITICAL): 'warn measure 2' has "
                "insufficient sub-market source information and "
                "will be removed from analysis"
            ),
        ],
        [
            (
                "WARNING: 'warn measure 3' has invalid "
                "sub-market scaling fraction source title, author, "
                "organization, and/or year information"
            )
        ],
    ]
    ok_tp_fmeth_mkts_out = [
        {
            "total": {
                "baseline": {"2009": 0.0000010908390, "2010": 0.0000010908390},
                "efficient": {"2009": 0, "2010": 0},
            },
            "competed": {
                "baseline": {"2009": 0.0000010908390, "2010": 0.0000010908390},
                "efficient": {"2009": 0, "2010": 0},
            },
        },
        {
            "total": {
                "baseline": {"2009": 0.000001472633, "2010": 0.000001472633},
                "efficient": {"2009": 0.000000490878, "2010": 0.000000490878},
            },
            "competed": {
                "baseline": {"2009": 0.000001472633, "2010": 0.000001472633},
                "efficient": {"2009": 0.000000490878, "2010": 0.000000490878},
            },
        },
        {
            "total": {
                "baseline": {"2009": 0.000001908968, "2010": 0.000001908968},
                "efficient": {"2009": 0.000000636323, "2010": 0.000000636323},
            },
            "competed": {
                "baseline": {"2009": 0.000001908968, "2010": 0.000001908968},
                "efficient": {"2009": 0.000000636323, "2010": 0.000000636323},
            },
        },
        {
            "total": {"baseline": {"2009": 0, "2010": 0}, "efficient": {"2009": 0, "2010": 0}},
            "competed": {"baseline": {"2009": 0, "2010": 0}, "efficient": {"2009": 0, "2010": 0}},
        },
    ]

    # Convert ok_partialmeas_in from dicts to Measure objects
    ok_partialmeas_in_measures = [
        Measure(base_dir, handyvars, handyfiles, opts_dict, **x) for x in ok_partialmeas_in
    ]

    # Create ok_coolcost_chk_in from first HP measure with coolcosts options
    ok_coolcost_chk_in = [
        Measure(
            base_dir, handyvars_hp_rates, handyfiles_emm,
            opts_coolcosts_dict, **x) for x in ok_hp_measures_in[0:1]
    ]

    # Expected stock cost output for the cooling cost test
    ok_coolcost_meas_stkcost_out = {
        "total": {
            "baseline": {"2009": 200000, "2010": 200000},
            "efficient": {"2009": 500000, "2010": 500000}},
        "competed": {
            "baseline": {"2009": 200000, "2010": 200000},
            "efficient": {"2009": 500000, "2010": 500000}}}

    # Return all test data (imported + generated)
    return {
        "ok_tpmeas_fullchk_break_out": ok_tpmeas_fullchk_break_out,
        "sample_cpl_in": sample_cpl_in,
        "ok_tpmeas_partchk_msegout": ok_tpmeas_partchk_msegout,
        "sample_cpl_in_state": sample_cpl_in_state,
        "sample_cpl_in_emm": sample_cpl_in_emm,
        "sample_mseg_in": sample_mseg_in,
        "ok_hpmeas_rates_breakouts": ok_hpmeas_rates_breakouts,
        "ok_partialmeas_in": ok_partialmeas_in_measures,
        "ok_hpmeas_rates_mkts_out": ok_hpmeas_rates_mkts_out,
        "ok_tpmeas_fullchk_msegout": ok_tpmeas_fullchk_msegout,
        "sample_mseg_in_emm": sample_mseg_in_emm,
        "sample_mseg_in_state": sample_mseg_in_state,
        "ok_tpmeas_partchk_msegout_emm": ok_tpmeas_partchk_msegout_emm,
        "ok_tpmeas_partchk_msegout_state": ok_tpmeas_partchk_msegout_state,
        "ok_tpmeas_partchk_msegout_state_regadj": ok_tpmeas_partchk_msegout_state_regadj,
        "opts": opts,
        "opts_site_energy": opts_site_energy,
        "opts_emm": opts_emm,
        "opts_state": opts_state,
        "opts_hp_rates": opts_hp_rates,
        "opts_hp_no_rates": opts_hp_no_rates,
        "opts_coolcosts": opts_coolcosts,
        "opts_fmeth": opts_fmeth,
        "opts_frefr": opts_frefr,
        "convert_data": convert_data,
        "tsv_data": tsv_data,
        "ok_tpmeas_fullchk_in": ok_tpmeas_fullchk_in,
        "ok_tpmeas_partchk_in": ok_tpmeas_partchk_in,
        "ok_tpmeas_partchk_emm_in": ok_tpmeas_partchk_emm_in,
        "ok_tpmeas_partchk_state_in": ok_tpmeas_partchk_state_in,
        "ok_tpmeas_partchk_state_regadj_in": ok_tpmeas_partchk_state_regadj_in,
        "ok_mapmeas_partchk_in": ok_mapmeas_partchk_in,
        "ok_tpmeas_sitechk_in": ok_tpmeas_sitechk_in,
        "ok_distmeas_in": ok_distmeas_in,
        "failmeas_inputs_in": failmeas_inputs_in,
        "warnmeas_in": warnmeas_in,
        "ok_mapmeas_hp_chk_in": ok_mapmeas_hp_chk_in,
        "ok_tp_fmeth_chk_in": ok_tp_fmeth_chk_in,
        "ok_map_frefr_chk_in": ok_map_frefr_chk_in,
        "ok_tpmeas_fullchk_competechoiceout": ok_tpmeas_fullchk_competechoiceout,
        "ok_tpmeas_fullchk_msegadjout": ok_tpmeas_fullchk_msegadjout,
        "ok_tpmeas_fullchk_supplydemandout": ok_tpmeas_fullchk_supplydemandout,
        "ok_mapmas_partchck_msegout": ok_mapmas_partchck_msegout,
        "ok_distmeas_out": ok_distmeas_out,
        "ok_tpmeas_sitechk_msegout": ok_tpmeas_sitechk_msegout,
        "ok_partialmeas_out": ok_partialmeas_out,
        "ok_warnmeas_out": ok_warnmeas_out,
        "ok_tp_fmeth_mkts_out": ok_tp_fmeth_mkts_out,
        "ok_map_frefr_mkts_out": ok_map_frefr_mkts_out,
        "ok_coolcost_chk_in": ok_coolcost_chk_in,
        "ok_coolcost_meas_stkcost_out": ok_coolcost_meas_stkcost_out,
    }
