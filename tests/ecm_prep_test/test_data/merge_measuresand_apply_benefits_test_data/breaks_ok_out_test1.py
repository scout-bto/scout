"""Expected output breaks data for test 1.

This module contains the expected output breaks structure for validating
measure package output attributes in test 1."""

breaks_ok_out_test1 = {
    "stock": {
        "baseline": {
            "AIA CZ1": {
                "Residential (New)": {
                    "Cooling (Equip.)": {"2009": 10, "2010": 10},
                    "Heating (Equip.)": {"2009": 15, "2010": 15},
                    "Heating (Env.)": {},
                },
            },
        },
        "efficient": {
            "AIA CZ1": {
                "Residential (New)": {
                    "Cooling (Equip.)": {"2009": 5, "2010": 5},
                    "Heating (Equip.)": {"2009": 5, "2010": 5},
                    "Heating (Env.)": {},
                },
            },
        },
    },
    "energy": {
        "baseline": {
            "AIA CZ1": {
                "Residential (New)": {
                    "Cooling (Equip.)": {"2009": 10, "2010": 10},
                    "Heating (Equip.)": {"2009": 15, "2010": 15},
                    "Heating (Env.)": {},
                },
            },
        },
        "efficient": {
            "AIA CZ1": {
                "Residential (New)": {
                    "Cooling (Equip.)": {"2009": 5, "2010": 5},
                    "Heating (Equip.)": {"2009": 4.27, "2010": 4.27},
                    "Heating (Env.)": {},
                },
            },
        },
        "savings": {
            "AIA CZ1": {
                "Residential (New)": {
                    "Cooling (Equip.)": {"2009": 5, "2010": 5},
                    "Heating (Equip.)": {"2009": 10.73, "2010": 10.73},
                    "Heating (Env.)": {},
                },
            },
        },
    },
    "carbon": {
        "baseline": {
            "AIA CZ1": {
                "Residential (New)": {
                    "Cooling (Equip.)": {"2009": 10, "2010": 10},
                    "Heating (Equip.)": {"2009": 15, "2010": 15},
                    "Heating (Env.)": {},
                },
            },
        },
        "efficient": {
            "AIA CZ1": {
                "Residential (New)": {
                    "Cooling (Equip.)": {"2009": 5, "2010": 5},
                    "Heating (Equip.)": {"2009": 4.27, "2010": 4.27},
                    "Heating (Env.)": {},
                },
            },
        },
        "savings": {
            "AIA CZ1": {
                "Residential (New)": {
                    "Cooling (Equip.)": {"2009": 5, "2010": 5},
                    "Heating (Equip.)": {"2009": 10.73, "2010": 10.73},
                    "Heating (Env.)": {},
                },
            },
        },
    },
    "energy cost": {
        "baseline": {
            "AIA CZ1": {
                "Residential (New)": {
                    "Cooling (Equip.)": {"2009": 10, "2010": 10},
                    "Heating (Equip.)": {"2009": 15, "2010": 15},
                    "Heating (Env.)": {},
                },
            },
        },
        "efficient": {
            "AIA CZ1": {
                "Residential (New)": {
                    "Cooling (Equip.)": {"2009": 5, "2010": 5},
                    "Heating (Equip.)": {"2009": 4.27, "2010": 4.27},
                    "Heating (Env.)": {},
                },
            },
        },
        "savings": {
            "AIA CZ1": {
                "Residential (New)": {
                    "Cooling (Equip.)": {"2009": 5, "2010": 5},
                    "Heating (Equip.)": {"2009": 10.73, "2010": 10.73},
                    "Heating (Env.)": {},
                },
            },
        },
    },
}
