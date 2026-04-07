#!/usr/bin/env python3

"""Tests for incentives, costs, and electrical infrastructure upgrades."""

import os
import copy
from scout.ecm_prep import Measure
from scout.ecm_prep_vars import UsefulVars, UsefulInputFiles
from tests.ecm_prep_test.common import dict_check


def test_incentives(market_test_data):
    """Test 'apply_incentives' in 'fill_mkts' function given user-defined incentive inputs."""

    # Initialize dummy measure with state-level inputs to draw from
    base_state_meas = market_test_data["ok_tpmeas_partchk_state_in"][0]
    # Pull handyvars from first sample measure and set year range
    hv = copy.deepcopy(base_state_meas.handyvars)
    # Set user-defined incentives information; test stacked federal and non-federal incentives
    hv.incentives = [
        [
            "CA",
            "single family home",
            "existing",
            "heating",
            "ASHP",
            "electricity",
            "natural gas",
            "no",
            "replace",
            "federal",
            False,
            0,
            "warm climates: 2.6; cold climates: 2.8",
            "COP",
            30,
            2000,
            "$/unit",
            2010,
            2050,
            1,
        ],
        [
            "CA",
            "single family home",
            "existing",
            "heating",
            "ASHP",
            "electricity",
            "natural gas",
            "no",
            "replace",
            "non-federal",
            False,
            0,
            2.6,
            "COP",
            50,
            float("nan"),
            "$/unit",
            2010,
            2050,
            1,
        ],
    ]
    years = [str(y) for y in hv.aeo_years]

    # Seed BY-YEAR carbon price
    carb_prices = hv.ccosts
    carb_prices.update({y: 1 for y in years})

    # Seed BY-YEAR electricity price & carbon intensities
    el_prices = hv.ecosts.setdefault("residential", {}).setdefault("electricity", {})
    el_prices.update({y: 60.0 for y in years})
    ng_prices = hv.ecosts["residential"].setdefault("natural gas", {})
    ng_prices.update({y: 11.0 for y in years})

    el_carb = hv.carb_int.setdefault("residential", {}).setdefault("electricity", {})
    el_carb.update({y: 5.0e-08 for y in years})
    ng_carb = hv.carb_int["residential"].setdefault("natural gas", {})
    ng_carb.update({y: 5.0e-08 for y in years})

    hv.ss_conv.setdefault("electricity", {})
    hv.ss_conv.setdefault("natural gas", {})
    for y in years:
        hv.ss_conv["electricity"][y] = 1.0
        hv.ss_conv["natural gas"][y] = 1.0

    # Options: split fuel reporting + pick Max adoption potential
    opts = copy.deepcopy(market_test_data["opts_state"])
    opts.adopt_scn_usr = ["Max adoption potential"]


def test_elec_upgrade_costs(market_test_data):
    """Test 'fill_mkts' function given various user assumptions about panel upgrade costs.

    Notes:
        Panel upgrade costs can be assessed for realistic shares of homes that require them,
        for all homes, or for no homes. This assumption is limited to single family existing
        homes.

        The test verifies that the added electrical infrastructure upgrade costs (see variable
        'elec_infr_costs') are correctly added to the original cost of the measure (see measure
        'meas_def' cost attribute 'installed_cost'). Tests a case when the user indicates
        that only a share of homes (see 'panel_shares') should receive a panel upgrade cost
        (see 'opts_shares'), a case where a user has suppressed electrical upgrade costs
        entirely (see 'opts_ign'), and a case where the user assumes these costs should be
        added to all homes (see 'opts_all').
    """
    # Set base directory
    base_dir = os.getcwd()
    # Set user options
    opts_all, opts_shares, opts_ign = [
        copy.deepcopy(market_test_data['opts_state']) for n in range(3)
    ]
    # Test three scenarios of electric upgrade cost settings
    opts_all.elec_upgrade_costs, opts_shares.elec_upgrade_costs, opts_ign.elec_upgrade_costs = [
        'all', 'shares', 'ignore'
    ]
    # Max adoption potential scenario for all three
    opts_all.adopt_scn_usr, opts_shares.adopt_scn_usr, opts_ign.adopt_scn_usr = [
        'Max adoption potential' for n in range(3)
    ]
    # Set handyfiles, using the first set of options to set file names
    hf = UsefulInputFiles(opts_all)
    # Set handyvars for three test cases
    hv_all, hv_shares, hv_ign = [
        UsefulVars(base_dir, hf, opts) for opts in [opts_all, opts_shares, opts_ign]
    ]
    # Hard code electrical upgrade costs to remove dependency in handyvars
    elec_infr_costs = {
        "panel replacement": 1500,
        "panel management": 500,
        "240V circuit": 1400,
    }
    hv_all.elec_infr_costs, hv_shares.elec_infr_costs, hv_ign.elec_infr_costs = [
        elec_infr_costs for x in range(3)
    ]
    # Verify that correct settings are yielded for panel upgrades handyvar, then hardcode
    # shares data for that case. Note: no shares data should have been pulled in for the
    # cases where all or no homes are assigned panel share calculations
    if all([x.panel_shares is None for x in [hv_all, hv_ign]]) and \
            isinstance(hv_shares.panel_shares, dict):
        hv_shares.panel_shares = {
            "CA": {
                "stock": {
                    "natural gas": {
                        "BAU w/ HPWH": {"no panel": 0.1, "panel": 0.8, "management": 0.1},
                        "BAU": {"no panel": 0.1, "panel": 0.8, "management": 0.1}},
                    "electricity": {
                        "BAU w/ HPWH": {"no panel": 0.9, "panel": 0, "management": 0.05},
                        "BAU": {"no panel": 0.9, "panel": 0, "management": 0.05}}},
                "energy": {
                    "natural gas": {
                        "BAU w/ HPWH": {"no panel": 0.2, "panel": 0.7, "management": 0.1},
                        "BAU": {"no panel": 0.2, "panel": 0.7, "management": 0.1}},
                    "electricity": {
                        "BAU w/ HPWH": {"no panel": 0.4, "panel": 0.5, "management": 0.1},
                        "BAU": {"no panel": 0.4, "panel": 0.5, "management": 0.1}}}}}
    else:
        raise ValueError("Variable 'panel_shares' is set incorrectly within UsefulVars object.")
    # Hard code years
    years = ["2009", "2010"]
    hv_all.aeo_years, hv_shares.aeo_years, hv_ign.aeo_years = (years for n in range(3))
    # Hard code retrofit rate
    hv_all.retro_rate, hv_shares.retro_rate, hv_ign.retro_rate = ({
        yr: 0.01 for yr in years} for n in range(3))
    # Ensure no regional cost adjustment is assessed (this otherwise happens by default)
    hv_all.reg_cost_adj, hv_shares.reg_cost_adj, hv_ign.reg_cost_adj = (None for n in range(3))
    # Hard code cost/conversion variables needed to get the prep routine to run through
    hv_all.ccosts, hv_shares.ccosts, hv_ign.ccosts = (
        {y: 1 for y in years} for n in range(3))
    hv_all.ecosts, hv_shares.ecosts, hv_ign.ecosts = (
        {"residential": {"electricity": {y: 60.0 for y in years},
                         "natural gas": {y: 11.0 for y in years}}} for n in range(3))
    hv_all.carb_int, hv_shares.carb_int, hv_ign.carb_int = (
        {"residential": {"electricity": {y: 5.0e-08 for y in years},
                         "natural gas": {y: 5.0e-08 for y in years}}} for n in range(3))
    hv_all.ss_conv, hv_shares.ss_conv, hv_ign.ss_conv = (
        {"electricity": {y: 1 for y in years},
         "natural gas": {y: 1 for y in years}} for n in range(3))

    # Function to produce year range dict
    def yrs(val): return {y: val for y in years}

    # Set example baseline microsegments (STATE: CA, SFH)
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
                                "stock": {y: 1 for y in years},
                                "energy": {y: 100 for y in years},
                            },
                            "ASHP": {
                                "stock": {y: 1 for y in years},
                                "energy": {y: 100 for y in years},
                            }
                        }
                    },
                    "heating": {
                        "supply": {
                            "ASHP": {
                                "stock": {y: 1 for y in years},
                                "energy": {y: 100 for y in years},
                            }
                        }
                    }
                },
            }
        }
    }

    # C/P/L for baseline NG furnace, baseline central AC,
    # and switched-to ASHP (heating + cooling provided by measure)
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
                                        "new": yrs(2000),
                                        "existing": yrs(2000)},
                                    "best": {
                                        "new": yrs(2000),
                                        "existing": yrs(2000)},
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
                            },
                            "ASHP": {
                                "performance": {
                                    "typical": yrs(4.69), "best": yrs(4.69),
                                    "units": "COP", "source": "addedcooling.json"},
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
                                        "parameters": {"p": "NA", "q": "NA"}},
                                },
                            }
                        }
                    },
                    "heating": {
                        "supply": {
                            "ASHP": {
                                "performance": {
                                    "typical": yrs(2.69), "best": yrs(2.69),
                                    "units": "COP", "source": "addedcooling.json"},
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
                                        "parameters": {"p": "NA", "q": "NA"}},
                                },
                            }
                        }
                    }
                },
            }
        }
    }

    # Measure definition for switching measure subject to panel share calculations
    meas_def = {
        "name": "sample measure with shares",
        "measure_type": "full service",
        "market_entry_year": None, "market_exit_year": None,
        "climate_zone": ["CA"],
        "bldg_type": "single family home",
        "structure_type": ["new", "existing"],
        "end_use": ["heating", "cooling"],
        "fuel_type": ["natural gas", "electricity"],
        "fuel_switch_to": "electricity",
        "technology": ["furnace (NG)", "central AC"],
        "tech_switch_to": "ASHP",
        "energy_efficiency": {"heating": 2.69, "cooling": 4.69},
        "energy_efficiency_units": "COP",
        "installed_cost": 14000,
        "cost_units": "2014$/unit",
        "product_lifetime": 15,
        "market_scaling_fractions": None,
        "market_scaling_fractions_source": None,
    }

    # Stock cost outputs (after applying panel share settings) for 3 test cases
    # (ignore costs, assign all costs, assign costs based on shares of homes needing panels)
    user_master_mseg_stock_cost = [{
        "competed": {
            "baseline": {"2009": 2456.6666666666665, "2010": 2380.0},
            "efficient": {"2009": 17196.66667, "2010": 16660},
        },
        "total": {
            "baseline": {"2009": 2456.6666666666665, "2010": 4836.666666666666},
            "efficient": {"2009": 17196.66667, "2010": 33856.66667},
        },
    }, {
        "competed": {
            "baseline": {"2009": 2456.6666666666665, "2010": 2380.0},
            "efficient": {"2009": 19308.83333, "2010": 18661},
        },
        "total": {
            "baseline": {"2009": 2456.6666666666665, "2010": 4836.666666666666},
            "efficient": {"2009": 19308.83333, "2010": 37969.83333},
        },
    }, {
        "competed": {
            "baseline": {"2009": 2456.6666666666665, "2010": 2380.0},
            "efficient": {"2009": 19126.75, "2010": 18488.5},
        },
        "total": {
            "baseline": {"2009": 2456.6666666666665, "2010": 4836.666666666666},
            "efficient": {"2009": 19126.75, "2010": 37615.25},
        },
    }]

    # Stock output that should be consistent across all three panel share settings
    user_master_mseg_stock = {
        "competed": {
            "all": {"2009": 1.228333333, "2010": 1.19},
            "measure": {"2009": 1.228333333, "2010": 1.19},
        },
        "total": {
            "all": {"2009": 10, "2010": 10},
            "measure": {"2009": 1.228333333, "2010": 2.418333333},
        },
    }

    # Loop through the three sets of panel share settings and test whether output is correct
    # (ignore costs, assign all costs, assign costs based on shares of homes needing panels)
    for ind_p, (hv, opts) in enumerate(
            zip([hv_ign, hv_all, hv_shares], [opts_ign, opts_all, opts_shares])):
        measure = Measure(base_dir, hv, None, vars(opts), **meas_def)
        measure.fill_mkts(
            mseg_in, cpl_in,
            market_test_data["convert_data"],
            market_test_data["tsv_data"],
            opts,
            ctrb_ms_pkg_prep=[],
            tsv_data_nonfs=None,
        )
        dict_check(
            measure.markets["Max adoption potential"]["master_mseg"]["cost"]["stock"],
            user_master_mseg_stock_cost[ind_p],
        )
        dict_check(
            measure.markets["Max adoption potential"]["master_mseg"]["stock"],
            user_master_mseg_stock,
        )
