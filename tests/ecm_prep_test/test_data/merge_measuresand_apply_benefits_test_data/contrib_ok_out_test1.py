"""Expected output contributing measures data for test 1.

This module contains the expected contributing measures structure for validating
measure package output attributes in test 1."""

contrib_ok_out_test1 = {
    (
        "('primary', 'AIA_CZ1', 'single family home', "
        "'electricity', 'cooling', 'supply', "
        "'ASHP', 'new')"
    ): {
        "stock": {
            "total": {"all": {"2009": 10, "2010": 10}, "measure": {"2009": 10, "2010": 10}},
            "competed": {"all": {"2009": 10, "2010": 10}, "measure": {"2009": 10, "2010": 10}},
        },
        "energy": {
            "total": {"baseline": {"2009": 10, "2010": 10}, "efficient": {"2009": 5, "2010": 5}},
            "competed": {"baseline": {"2009": 10, "2010": 10}, "efficient": {"2009": 5, "2010": 5}},
        },
        "carbon": {
            "total": {"baseline": {"2009": 10, "2010": 10}, "efficient": {"2009": 5, "2010": 5}},
            "competed": {"baseline": {"2009": 10, "2010": 10}, "efficient": {"2009": 5, "2010": 5}},
        },
        "cost": {
            "stock": {
                "total": {
                    "baseline": {"2009": 10, "2010": 10},
                    "efficient": {"2009": 10, "2010": 10},
                },
                "competed": {
                    "baseline": {"2009": 10, "2010": 10},
                    "efficient": {"2009": 10, "2010": 10},
                },
            },
            "energy": {
                "total": {
                    "baseline": {"2009": 10, "2010": 10},
                    "efficient": {"2009": 5, "2010": 5},
                },
                "competed": {
                    "baseline": {"2009": 10, "2010": 10},
                    "efficient": {"2009": 5, "2010": 5},
                },
            },
            "carbon": {
                "total": {
                    "baseline": {"2009": 10, "2010": 10},
                    "efficient": {"2009": 5, "2010": 5},
                },
                "competed": {
                    "baseline": {"2009": 10, "2010": 10},
                    "efficient": {"2009": 5, "2010": 5},
                },
            },
        },
        "lifetime": {"baseline": {"2009": 10, "2010": 10}, "measure": 10},
        "sub-market scaling": 1,
    },
    (
        "('primary', 'AIA_CZ1', 'single family home', "
        "'electricity', 'heating', 'supply', "
        "'ASHP', 'new')"
    ): {
        "stock": {
            "total": {"all": {"2009": 10, "2010": 10}, "measure": {"2009": 10, "2010": 10}},
            "competed": {"all": {"2009": 10, "2010": 10}, "measure": {"2009": 10, "2010": 10}},
        },
        "energy": {
            "total": {
                "baseline": {"2009": 10, "2010": 10},
                "efficient": {"2009": 1.77, "2010": 1.77},
            },
            "competed": {
                "baseline": {"2009": 10, "2010": 10},
                "efficient": {"2009": 1.77, "2010": 1.77},
            },
        },
        "carbon": {
            "total": {
                "baseline": {"2009": 10, "2010": 10},
                "efficient": {"2009": 1.77, "2010": 1.77},
            },
            "competed": {
                "baseline": {"2009": 10, "2010": 10},
                "efficient": {"2009": 1.77, "2010": 1.77},
            },
        },
        "cost": {
            "stock": {
                "total": {
                    "baseline": {"2009": 10, "2010": 10},
                    "efficient": {"2009": 10, "2010": 10},
                },
                "competed": {
                    "baseline": {"2009": 10, "2010": 10},
                    "efficient": {"2009": 10, "2010": 10},
                },
            },
            "energy": {
                "total": {
                    "baseline": {"2009": 10, "2010": 10},
                    "efficient": {"2009": 1.77, "2010": 1.77},
                },
                "competed": {
                    "baseline": {"2009": 10, "2010": 10},
                    "efficient": {"2009": 1.77, "2010": 1.77},
                },
            },
            "carbon": {
                "total": {
                    "baseline": {"2009": 10, "2010": 10},
                    "efficient": {"2009": 1.77, "2010": 1.77},
                },
                "competed": {
                    "baseline": {"2009": 10, "2010": 10},
                    "efficient": {"2009": 1.77, "2010": 1.77},
                },
            },
        },
        "lifetime": {"baseline": {"2009": 20, "2010": 20}, "measure": 20},
        "sub-market scaling": 1,
    },
    (
        "('primary', 'AIA_CZ1', 'multi family home', "
        "'electricity', 'heating', 'supply', "
        "'ASHP', 'new')"
    ): {
        "stock": {
            "total": {"all": {"2009": 5, "2010": 5}, "measure": {"2009": 5, "2010": 5}},
            "competed": {"all": {"2009": 5, "2010": 5}, "measure": {"2009": 5, "2010": 5}},
        },
        "energy": {
            "total": {"baseline": {"2009": 5, "2010": 5}, "efficient": {"2009": 2.5, "2010": 2.5}},
            "competed": {
                "baseline": {"2009": 5, "2010": 5},
                "efficient": {"2009": 2.5, "2010": 2.5},
            },
        },
        "carbon": {
            "total": {"baseline": {"2009": 5, "2010": 5}, "efficient": {"2009": 2.5, "2010": 2.5}},
            "competed": {
                "baseline": {"2009": 5, "2010": 5},
                "efficient": {"2009": 2.5, "2010": 2.5},
            },
        },
        "cost": {
            "stock": {
                "total": {"baseline": {"2009": 5, "2010": 5}, "efficient": {"2009": 5, "2010": 5}},
                "competed": {
                    "baseline": {"2009": 5, "2010": 5},
                    "efficient": {"2009": 5, "2010": 5},
                },
            },
            "energy": {
                "total": {
                    "baseline": {"2009": 5, "2010": 5},
                    "efficient": {"2009": 2.5, "2010": 2.5},
                },
                "competed": {
                    "baseline": {"2009": 5, "2010": 5},
                    "efficient": {"2009": 2.5, "2010": 2.5},
                },
            },
            "carbon": {
                "total": {
                    "baseline": {"2009": 5, "2010": 5},
                    "efficient": {"2009": 2.5, "2010": 2.5},
                },
                "competed": {
                    "baseline": {"2009": 5, "2010": 5},
                    "efficient": {"2009": 2.5, "2010": 2.5},
                },
            },
        },
        "lifetime": {"baseline": {"2009": 10, "2010": 10}, "measure": 10},
        "sub-market scaling": 1,
    },
}
