#!/usr/bin/env python3

"""Tests of linked cooling/heating cost calculations."""

import pytest
import os
import copy
from scout.ecm_prep import Measure
from scout.ecm_prep_vars import UsefulVars, UsefulInputFiles
from tests.ecm_prep_test.common import NullOpts


@pytest.fixture(scope="module")
def test_settings():
    """Set up the common directory context and handyvars / handyfiles."""
    base_dir = os.getcwd()
    null_opts = NullOpts()
    opts = copy.deepcopy(null_opts.opts)
    opts_dict = copy.deepcopy(null_opts.opts_dict)

    # Ensure options allow linked cost calculations (i.e. not suppressed)
    opts.no_lnkd_stk_costs = None
    opts.no_lnkd_op_costs = False
    opts_dict["no_lnkd_stk_costs"] = None
    opts_dict["no_lnkd_op_costs"] = False

    # Set up for State breakout
    opts.alt_regions = "State"
    opts_dict["alt_regions"] = "State"

    handyfiles = UsefulInputFiles(opts)
    handyvars = UsefulVars(base_dir, handyfiles, opts)
    # AEO years and retrofit rate use minimal test values
    handyvars.aeo_years = ["2009", "2010"]
    handyvars.retro_rate = {yr: 0.02 for yr in handyvars.aeo_years}

    return {
        "base_dir": base_dir,
        "handyfiles": handyfiles,
        "handyvars": handyvars,
        "opts": opts,
        "opts_dict": opts_dict
    }


def test_set_lnkd_cost_exclude(test_settings):
    """Test `set_lnkd_cost_exclude` to verify that flags are correctly calculated."""
    base_dir = test_settings["base_dir"]
    handyvars = test_settings["handyvars"]
    handyfiles = test_settings["handyfiles"]
    opts_dict = test_settings["opts_dict"]

    measure_dict = {
        "name": "test linked cost measure",
        "measure_type": "full service",
        "market_entry_year": None,
        "market_exit_year": None,
        "climate_zone": ["AIA_CZ1"],
        "bldg_type": ["single family home"],
        "structure_type": ["new"],
        "end_use": {"primary": ["heating", "cooling"], "secondary": None},
        "fuel_type": {"primary": ["electricity"], "secondary": None},
        "technology": {"primary": ["resistance heat", "ASHP", "room AC"], "secondary": None},
        "tech_switch_to": "ASHP",
        "energy_efficiency": 0.5,
        "energy_efficiency_units": "relative savings (constant)",
        "installed_cost": 100,
        "cost_units": "2014$/unit",
        "product_lifetime": 15
    }

    measure = Measure(base_dir, handyvars, handyfiles, opts_dict, **measure_dict)
    measure.linked_htcl_tover = True
    measure.linked_htcl_tover_anchor_eu = "heating"
    measure.linked_htcl_tover_linked_tech = "ASHP"

    # CASE 1: Baseline is ASHP (which has "HP" in name), switch is ASHP
    mskeys_hp = ("primary", "AIA_CZ1", "single family home", "electricity",
                 "heating", "supply", "ASHP", "new")
    flags = measure.set_lnkd_cost_exclude(mskeys_hp)
    # flags: rmv_hp_dblct_base_stkcosts, rmv_hp_dblct_meas_stkcosts, rmv_scnd_hvac_stkcosts,
    # rmv_lnkd_tech_costs
    assert flags[0] is True  # rmv_hp_dblct_base_stkcosts
    assert flags[1] is True  # rmv_hp_dblct_meas_stkcosts
    assert flags[2] is False  # rmv_scnd_hvac_stkcosts
    assert flags[3] is False  # mskeys[-2] is "ASHP", which matches linked_htcl_tover_linked_tech

    # CASE 2: Baseline is resistance heat (no "HP"), switch is ASHP, and
    # end use is non-anchor ("cooling")
    mskeys_non_hp = ("primary", "AIA_CZ1", "single family home", "electricity", "cooling", "supply",
                     "resistance heat", "new")
    flags = measure.set_lnkd_cost_exclude(mskeys_non_hp)
    assert flags[0] is False  # rmv_hp_dblct_base_stkcosts
    assert flags[1] is True  # rmv_hp_dblct_meas_stkcosts (since tech_switch_to is ASHP)
    assert flags[2] is False  # rmv_scnd_hvac_stkcosts
    assert flags[3] is True  # resistance heat is not "ASHP" and cooling is non-anchor end use

    # CASE 2b: Baseline is resistance heat, switch is ASHP, and end use is anchor ("heating")
    mskeys_non_hp_anchor = ("primary", "AIA_CZ1", "single family home", "electricity", "heating",
                            "supply", "resistance heat", "new")
    flags = measure.set_lnkd_cost_exclude(mskeys_non_hp_anchor)
    assert flags[0] is False  # rmv_hp_dblct_base_stkcosts
    assert flags[1] is True  # rmv_hp_dblct_meas_stkcosts
    assert flags[2] is False  # rmv_scnd_hvac_stkcosts
    assert flags[3] is False  # heating is anchor end use, so we do not exclude it here

    # CASE 3: Baseline is room AC (minor hvac tech)
    mskeys_room_ac = ("primary", "AIA_CZ1", "single family home", "electricity", "cooling",
                      "supply", "room AC", "new")
    flags = measure.set_lnkd_cost_exclude(mskeys_room_ac)
    assert flags[0] is False  # "room AC" has no "HP"
    assert flags[1] is True  # rmv_hp_dblct_meas_stkcosts
    assert flags[2] is True  # rmv_scnd_hvac_stkcosts is True because "room AC" is secondary and
    # "resistance heat" in technology["primary"] is not
    assert flags[3] is True  # tech is "room AC", which is not "ASHP"

    # CASE 4: Representative linked tech is "all"
    measure.linked_htcl_tover_linked_tech = "all"
    flags = measure.set_lnkd_cost_exclude(mskeys_room_ac)
    assert flags[3] is False

    # CASE 5: Representative linked tech is None
    measure.linked_htcl_tover_linked_tech = None
    flags = measure.set_lnkd_cost_exclude(mskeys_room_ac)
    assert flags[3] is False


def test_rec_lnkd_costs(test_settings):
    """Test `rec_lnkd_costs` to verify that costs are correctly calculated and transferred."""
    base_dir = test_settings["base_dir"]
    handyvars = test_settings["handyvars"]
    handyfiles = test_settings["handyfiles"]
    opts_dict = test_settings["opts_dict"]
    opts = test_settings["opts"]

    measure_dict = {
        "name": "test linked cost transfer measure",
        "measure_type": "full service",
        "market_entry_year": None,
        "market_exit_year": None,
        "climate_zone": ["AIA_CZ1"],
        "bldg_type": ["single family home"],
        "structure_type": ["new"],
        "end_use": {"primary": ["heating", "cooling"], "secondary": None},
        "fuel_type": {"primary": ["electricity"], "secondary": None},
        "technology": {"primary": ["ASHP"], "secondary": None},
        "tech_switch_to": "ASHP",
        "energy_efficiency": 0.5,
        "energy_efficiency_units": "relative savings (constant)",
        "installed_cost": 100,
        "cost_units": "2014$/unit",
        "product_lifetime": 15
    }

    measure = Measure(base_dir, handyvars, handyfiles, opts_dict, **measure_dict)
    measure.linked_htcl_tover = True
    measure.linked_htcl_tover_anchor_eu = "heating"
    measure.linked_htcl_tover_linked_tech = "ASHP"

    adopt_scheme = "Technical potential"
    mskeys = ("primary", "AIA_CZ1", "single family home", "electricity",
              "cooling", "supply", "ASHP", "new")
    contrib_mseg_key = ("('primary', 'AIA_CZ1', 'single family home', 'electricity', 'cooling', "
                        "'supply', 'ASHP', 'new')")

    add_dict = {
        "stock": {
            "competed": {
                "measure": {
                    "2009": 50.0,
                    "2010": 50.0
                }
            }
        },
        "cost": {
            "stock": {
                "competed": {
                    "efficient": {
                        "2009": 1000.0,
                        "2010": 1000.0
                    }
                }
            },
            "energy": {
                "competed": {
                    "efficient": {
                        "2009": 500.0,
                        "2010": 500.0
                    }
                }
            }
        }
    }

    anchor_mseg_key = ("('primary', 'AIA_CZ1', 'single family home', 'electricity', 'heating', "
                       "'supply', 'ASHP', 'new')")
    measure.markets = {
        adopt_scheme: {
            "mseg_adjust": {
                "contributing mseg keys and values": {
                    anchor_mseg_key: {
                        "stock": {
                            "competed": {
                                "measure": {
                                    "2009": 100.0,
                                    "2010": 100.0
                                }
                            }
                        }
                    }
                },
                "capacity factor": {
                    anchor_mseg_key: 0.8
                },
                "linked mseg values": {}
            }
        }
    }

    stk_cap_fact = 1.0
    lnkd_cost_adj_fact = {"2009": 1.0, "2010": 1.0}
    dmd_meas = False
    is_in_package = False

    rmv_hp_dblct_meas_stkcosts = False
    rmv_scnd_hvac_stkcosts = False
    rmv_lnkd_tech_costs = False

    # Execute rec_lnkd_costs with default allowed settings
    measure.rec_lnkd_costs(
        adopt_scheme, mskeys, contrib_mseg_key, add_dict,
        rmv_hp_dblct_meas_stkcosts, rmv_scnd_hvac_stkcosts, rmv_lnkd_tech_costs,
        opts, stk_cap_fact, lnkd_cost_adj_fact, dmd_meas, is_in_package
    )

    linked_values = measure.markets[adopt_scheme]["mseg_adjust"]["linked mseg values"]
    assert anchor_mseg_key in linked_values

    # Check cost stock:
    # (1000.0 / (50.0 * 1.0 * 1.0)) * (100.0 * 0.8) = 20.0 * 80.0 = 1600.0
    assert linked_values[anchor_mseg_key]["stock"]["2009"] == 1600.0
    assert linked_values[anchor_mseg_key]["stock"]["2010"] == 1600.0

    # Check cost energy:
    # (500.0 / (50.0 * 1.0 * 1.0)) * (100.0 * 0.8) = 10.0 * 80.0 = 800.0
    assert linked_values[anchor_mseg_key]["energy"]["2009"] == 800.0
    assert linked_values[anchor_mseg_key]["energy"]["2010"] == 800.0

    # Subcase 2: Suppress stock costs but not operating costs
    opts_suppress_stk = copy.deepcopy(opts)
    opts_suppress_stk.no_lnkd_stk_costs = "in_adopt_and_report"
    measure.markets[adopt_scheme]["mseg_adjust"]["linked mseg values"] = {}

    measure.rec_lnkd_costs(
        adopt_scheme, mskeys, contrib_mseg_key, add_dict,
        rmv_hp_dblct_meas_stkcosts, rmv_scnd_hvac_stkcosts, rmv_lnkd_tech_costs,
        opts_suppress_stk, stk_cap_fact, lnkd_cost_adj_fact, dmd_meas, is_in_package
    )
    linked_values = measure.markets[adopt_scheme]["mseg_adjust"]["linked mseg values"]
    assert anchor_mseg_key in linked_values
    assert linked_values[anchor_mseg_key]["stock"]["2009"] == 0.0  # Suppressed
    assert linked_values[anchor_mseg_key]["energy"]["2009"] == 800.0  # Op cost is not suppressed

    # Subcase 3: Suppress operating costs but not stock costs
    opts_suppress_op = copy.deepcopy(opts)
    opts_suppress_op.no_lnkd_op_costs = True
    measure.markets[adopt_scheme]["mseg_adjust"]["linked mseg values"] = {}
    measure.rec_lnkd_costs(
        adopt_scheme, mskeys, contrib_mseg_key, add_dict,
        rmv_hp_dblct_meas_stkcosts, rmv_scnd_hvac_stkcosts, rmv_lnkd_tech_costs,
        opts_suppress_op, stk_cap_fact, lnkd_cost_adj_fact, dmd_meas, is_in_package
    )
    linked_values = measure.markets[adopt_scheme]["mseg_adjust"]["linked mseg values"]
    assert anchor_mseg_key in linked_values
    assert linked_values[anchor_mseg_key]["stock"]["2009"] == 1600.0  # Stock cost is not suppressed
    assert linked_values[anchor_mseg_key]["energy"]["2009"] == 0.0  # Operating cost is suppressed

    # Subcase 4: Package tracking
    is_in_package = True
    measure.markets[adopt_scheme]["mseg_adjust"]["paired heat/cool mseg adjustments"] = {
        "linked cost adjustments": {}
    }
    measure.rec_lnkd_costs(
        adopt_scheme, mskeys, contrib_mseg_key, add_dict,
        rmv_hp_dblct_meas_stkcosts, rmv_scnd_hvac_stkcosts, rmv_lnkd_tech_costs,
        opts, stk_cap_fact, lnkd_cost_adj_fact, dmd_meas, is_in_package
    )
    package_tracking = measure.markets[adopt_scheme]["mseg_adjust"][
        "paired heat/cool mseg adjustments"]["linked cost adjustments"][contrib_mseg_key]
    assert package_tracking["capacity factor"] == stk_cap_fact
    assert package_tracking["stock alignment"] == lnkd_cost_adj_fact


def test_integrated_linked_costs(test_settings):
    """Integrated test to verify that linked cost information is correctly computed and reported
    in 'linked mseg values' when `no_lnkd_stk_costs` and `no_lnkd_op_costs` are both False/None."""
    base_dir = test_settings["base_dir"]
    handyvars = test_settings["handyvars"]
    handyfiles = test_settings["handyfiles"]
    opts_dict = test_settings["opts_dict"]
    opts = test_settings["opts"]

    # Seed UsefulVars parameters so that fill_mkts runs with mock baseline segments smoothly
    years = ["2009", "2010"]
    handyvars.aeo_years = years
    handyvars.ccosts = {y: 1 for y in years}

    # Initialize cap_facts for residential single family home
    handyvars.cap_facts = {
        "data": {
            "single family home": {
                "heating": 1.0,
                "cooling": 1.0
            }
        }
    }

    # Setup baseline electricity cost and carbon intensity
    el_prices = handyvars.ecosts.setdefault("residential", {}).setdefault("electricity", {})
    el_prices.update({y: 60.0 for y in years})
    ng_prices = handyvars.ecosts["residential"].setdefault("natural gas", {})
    ng_prices.update({y: 11.0 for y in years})

    el_carb = handyvars.carb_int.setdefault("residential", {}).setdefault("electricity", {})
    el_carb.update({y: 5.0e-08 for y in years})
    ng_carb = handyvars.carb_int["residential"].setdefault("natural gas", {})
    ng_carb.update({y: 5.0e-08 for y in years})

    handyvars.ss_conv.setdefault("electricity", {})
    handyvars.ss_conv.setdefault("natural gas", {})
    for y in years:
        handyvars.ss_conv["electricity"][y] = 1.0
        handyvars.ss_conv["natural gas"][y] = 1.0

    # Shorthand helper for year range
    def yrs(val):
        return {y: val for y in years}

    # Set up our baseline segments (msegs)
    mseg_in = {
        "CA": {
            "single family home": {
                "total square footage": {y: 100 for y in years},
                "total homes": {y: 1000 for y in years},
                "new homes": {y: 50 for y in years},
                "natural gas": {
                    "heating": {
                        "supply": {
                            "furnace (NG)": {
                                "stock": {y: 10 for y in years},
                                "energy": {y: 100.0 for y in years},
                            }
                        }
                    }
                },
                "electricity": {
                    "cooling": {
                        "supply": {
                            "central AC": {
                                "stock": {y: 10 for y in years},
                                "energy": {y: 100.0 for y in years},
                            }
                        }
                    },
                    "heating": {
                        "supply": {
                            "resistance heat": {
                                "stock": {y: 1 for y in years},
                                "energy": {y: 100 for y in years},
                            }
                        }
                    }
                }
            }
        }
    }

    # Set up baseline technology details (cpl)
    cpl_in = {
        "pacific": {
            "single family home": {
                "natural gas": {
                    "heating": {
                        "supply": {
                            "furnace (NG)": {
                                "performance": {
                                    "typical": yrs(0.8), "best": yrs(0.8),
                                    "units": "AFUE", "source": "stub"},
                                "installed cost": {
                                    "typical": {
                                        "new": yrs(2000), "existing": yrs(2000)},
                                    "best": {
                                        "new": yrs(2000), "existing": yrs(2000)},
                                    "units": "2014$/unit", "source": "stub"},
                                "lifetime": {
                                    "average": yrs(15), "range": yrs(5),
                                    "units": "years", "source": "stub"},
                                "consumer choice": {
                                    "competed market share": {
                                        "source": "stub",
                                        "model type": "logistic regression",
                                        "parameters": {
                                            "b1": yrs("NA"), "b2": yrs("NA")}},
                                    "competed market": {
                                        "source": "stub",
                                        "model type": "bass diffusion",
                                        "parameters": {
                                            "p": "NA", "q": "NA"}},
                                },
                            }
                        }
                    }
                },
                "electricity": {
                    "cooling": {
                        "supply": {
                            "central AC": {
                                "performance": {
                                    "typical": yrs(3.5), "best": yrs(3.5),
                                    "units": "COP", "source": "stub"},
                                "installed cost": {
                                    "typical": {
                                        "new": yrs(3000), "existing": yrs(3000)},
                                    "best": {
                                        "new": yrs(3000), "existing": yrs(3000)},
                                    "units": "2014$/unit", "source": "stub"},
                                "lifetime": {
                                    "average": yrs(12), "range": yrs(3),
                                    "units": "years", "source": "stub"},
                                "consumer choice": {
                                    "competed market share": {
                                        "source": "stub",
                                        "model type": "logistic regression",
                                        "parameters": {
                                            "b1": yrs("NA"), "b2": yrs("NA")}},
                                    "competed market": {
                                        "source": "stub",
                                        "model type": "bass diffusion",
                                        "parameters": {
                                            "p": "NA", "q": "NA"}},
                                },
                            }
                        }
                    },
                    "heating": {
                        "supply": {
                            "resistance heat": {
                                "performance": {
                                    "typical": yrs(2.69), "best": yrs(2.69),
                                    "units": "COP", "source": "stub"},
                                "installed cost": {
                                    "typical": {
                                        "new": yrs(6000), "existing": yrs(6000)},
                                    "best": {
                                        "new": yrs(6000), "existing": yrs(6000)},
                                    "units": "2014$/unit", "source": "stub"},
                                "lifetime": {
                                    "average": yrs(15), "range": yrs(5),
                                    "units": "years", "source": "stub"},
                                "consumer choice": {
                                    "competed market share": {
                                        "source": "stub",
                                        "model type": "logistic regression",
                                        "parameters": {
                                            "b1": yrs("NA"), "b2": yrs("NA")}},
                                    "competed market": {
                                        "source": "stub",
                                        "model type": "bass diffusion",
                                        "parameters": {
                                            "p": "NA", "q": "NA"}},
                                },
                            }
                        }
                    }
                }
            }
        }
    }

    # Define a Measure that covers heating and cooling, no switching (gas furnace + central AC)
    meas_def = {
        "name": "sample hvac and cooling linked cost measure",
        "measure_type": "full service",
        "market_entry_year": None,
        "market_exit_year": None,
        "climate_zone": ["CA"],
        "bldg_type": "single family home",
        "structure_type": ["new", "existing"],
        "end_use": ["heating", "cooling"],
        "fuel_type": ["natural gas", "electricity"],
        "fuel_switch_to": None,
        "technology": ["furnace (NG)", "central AC"],
        "tech_switch_to": None,
        "energy_efficiency": {"heating": 0.95, "cooling": 4.69},
        "energy_efficiency_units": {"heating": "AFUE", "cooling": "COP"},
        "installed_cost": 14000,
        "cost_units": "2014$/unit",
        "product_lifetime": 15,
        "market_scaling_fractions": None,
        "market_scaling_fractions_source": None,
    }

    measure = Measure(base_dir, handyvars, handyfiles, opts_dict, **meas_def)

    # Execute fill_mkts
    measure.fill_mkts(
        mseg_in, cpl_in,
        convert_data={},
        tsv_data_init={},
        opts=opts,
        ctrb_ms_pkg_prep=[],
        tsv_data_nonfs=None
    )

    # Verify that linked mseg values contains the transferred costs from cooling segment to heating
    linked_values = measure.markets["Technical potential"]["mseg_adjust"]["linked mseg values"]
    assert len(linked_values) == 2

    key_new = (
        "('primary', 'CA', 'single family home', 'natural gas', 'heating', "
        "'supply', 'furnace (NG)', 'new')")
    key_existing = (
        "('primary', 'CA', 'single family home', 'natural gas', 'heating', "
        "'supply', 'furnace (NG)', 'existing')")

    assert key_new in linked_values
    assert key_existing in linked_values

    # Check 'new' mseg values
    assert linked_values[key_new]["stock"]["2009"] == pytest.approx(7000.0, rel=1e-5)
    assert linked_values[key_new]["stock"]["2010"] == pytest.approx(14000.0, rel=1e-5)
    assert linked_values[key_new]["energy"]["2009"] == pytest.approx(223.880597, rel=1e-5)
    assert linked_values[key_new]["energy"]["2010"] == pytest.approx(447.761194, rel=1e-5)

    # Check 'existing' mseg values
    assert linked_values[key_existing]["stock"]["2009"] == pytest.approx(133000.0, rel=1e-5)
    assert linked_values[key_existing]["stock"]["2010"] == pytest.approx(126000.0, rel=1e-5)
    assert linked_values[key_existing]["energy"]["2009"] == pytest.approx(4253.731343, rel=1e-5)
    assert linked_values[key_existing]["energy"]["2010"] == pytest.approx(4029.850746, rel=1e-5)
