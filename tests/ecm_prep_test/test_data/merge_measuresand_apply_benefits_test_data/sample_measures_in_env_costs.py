"""Sample measures data for testing envelope costs in packaging.

This module contains test data for testing envelope cost handling in measure packages.
The measure has competed stock of zero in one year to test edge cases."""

sample_measures_in_env_costs = [
    {
        "name": "sample measure pkg env",
        "market_entry_year": None,
        "market_exit_year": None,
        "market_scaling_fractions": None,
        "market_scaling_fractions_source": None,
        "measure_type": "full service",
        "structure_type": ["new"],
        "climate_zone": ["AIA_CZ1"],
        "bldg_type": ["single family home"],
        "fuel_type": {"primary": ["electricity"], "secondary": None},
        "fuel_switch_to": None,
        "end_use": {"primary": ["heating"], "secondary": None},
        "technology": {"primary": ["windows conduction", "wall"], "secondary": None},
        "technology_type": {"primary": ["demand"], "secondary": None},
        "markets": {
            "Technical potential": {
                "master_mseg": {
                    "stock": {
                        "total": {
                            "all": {"2009": 20, "2010": 20},
                            "measure": {"2009": 20, "2010": 20},
                        },
                        "competed": {
                            "all": {"2009": 20, "2010": 0},
                            "measure": {"2009": 20, "2010": 0},
                        },
                    },
                    "energy": {
                        "total": {
                            "baseline": {"2009": 20, "2010": 20},
                            "efficient": {"2009": 10, "2010": 10},
                        },
                        "competed": {
                            "baseline": {"2009": 20, "2010": 20},
                            "efficient": {"2009": 10, "2010": 10},
                        },
                    },
                    "carbon": {
                        "total": {
                            "baseline": {"2009": 20, "2010": 20},
                            "efficient": {"2009": 10, "2010": 10},
                        },
                        "competed": {
                            "baseline": {"2009": 20, "2010": 20},
                            "efficient": {"2009": 10, "2010": 10},
                        },
                    },
                    "cost": {
                        "stock": {
                            "total": {
                                "baseline": {"2009": 20, "2010": 20},
                                "efficient": {"2009": 20, "2010": 20},
                            },
                            "competed": {
                                "baseline": {"2009": 20, "2010": 0},
                                "efficient": {"2009": 20, "2010": 0},
                            },
                        },
                        "energy": {
                            "total": {
                                "baseline": {"2009": 20, "2010": 20},
                                "efficient": {"2009": 10, "2010": 10},
                            },
                            "competed": {
                                "baseline": {"2009": 20, "2010": 20},
                                "efficient": {"2009": 10, "2010": 10},
                            },
                        },
                        "carbon": {
                            "total": {
                                "baseline": {"2009": 20, "2010": 20},
                                "efficient": {"2009": 10, "2010": 10},
                            },
                            "competed": {
                                "baseline": {"2009": 20, "2010": 20},
                                "efficient": {"2009": 10, "2010": 10},
                            },
                        },
                    },
                    "lifetime": {"baseline": {"2009": 10, "2010": 10}, "measure": 10},
                    "sub-market scaling": 1,
                },
                "mseg_adjust": {
                    "contributing mseg keys and values": {
                        (
                            "('primary', 'AIA_CZ1', 'single family home', "
                            "'electricity', 'heating', 'demand', "
                            "'windows conduction', 'new')"
                        ): {
                            "stock": {
                                "total": {
                                    "all": {"2009": 10, "2010": 10},
                                    "measure": {"2009": 10, "2010": 10},
                                },
                                "competed": {
                                    "all": {"2009": 10, "2010": 0},
                                    "measure": {"2009": 10, "2010": 0},
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
                            "cost": {
                                "stock": {
                                    "total": {
                                        "baseline": {"2009": 10, "2010": 10},
                                        "efficient": {"2009": 10, "2010": 10},
                                    },
                                    "competed": {
                                        "baseline": {"2009": 10, "2010": 0},
                                        "efficient": {"2009": 10, "2010": 0},
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
                            "'electricity', 'heating', 'demand', "
                            "'wall', 'new')"
                        ): {
                            "stock": {
                                "total": {
                                    "all": {"2009": 10, "2010": 10},
                                    "measure": {"2009": 10, "2010": 10},
                                },
                                "competed": {
                                    "all": {"2009": 10, "2010": 0},
                                    "measure": {"2009": 10, "2010": 0},
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
                            "cost": {
                                "stock": {
                                    "total": {
                                        "baseline": {"2009": 10, "2010": 10},
                                        "efficient": {"2009": 15, "2010": 15},
                                    },
                                    "competed": {
                                        "baseline": {"2009": 10, "2010": 0},
                                        "efficient": {"2009": 15, "2010": 0},
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
                    },
                    "competed choice parameters": {
                        (
                            "('primary', 'AIA_CZ1', 'single family home', "
                            "'electricity', 'heating', 'demand', "
                            "'windows conduction', 'new')"
                        ): {"b1": {"2009": 1, "2010": 1}, "b2": {"2009": 1, "2010": 1}},
                        (
                            "('primary', 'AIA_CZ1', 'single family home', "
                            "'electricity', 'heating', 'demand', "
                            "'wall', 'new')"
                        ): {"b1": {"2009": 1, "2010": 1}, "b2": {"2009": 1, "2010": 1}},
                    },
                    "secondary mseg adjustments": {
                        "sub-market": {
                            "original energy (total)": {},
                            "adjusted energy (sub-market)": {},
                        },
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
                "mseg_out_break": {
                    "stock": {
                        "baseline": {
                            "AIA CZ1": {
                                "Residential (New)": {
                                    "Heating (Env.)": {"2009": 20, "2010": 20},
                                    "Heating (Equip.)": {},
                                    "Cooling (Equip.)": {},
                                }
                            }
                        },
                        "efficient": {
                            "AIA CZ1": {
                                "Residential (New)": {
                                    "Heating (Env.)": {"2009": 10, "2010": 10},
                                    "Heating (Equip.)": {},
                                    "Cooling (Equip.)": {},
                                }
                            }
                        },
                    },
                    "energy": {
                        "baseline": {
                            "AIA CZ1": {
                                "Residential (New)": {
                                    "Heating (Env.)": {"2009": 20, "2010": 20},
                                    "Heating (Equip.)": {},
                                    "Cooling (Equip.)": {},
                                }
                            }
                        },
                        "efficient": {
                            "AIA CZ1": {
                                "Residential (New)": {
                                    "Heating (Env.)": {"2009": 10, "2010": 10},
                                    "Heating (Equip.)": {},
                                    "Cooling (Equip.)": {},
                                }
                            }
                        },
                        "savings": {
                            "AIA CZ1": {
                                "Residential (New)": {
                                    "Heating (Env.)": {"2009": 10, "2010": 10},
                                    "Heating (Equip.)": {},
                                    "Cooling (Equip.)": {},
                                }
                            }
                        },
                    },
                    "carbon": {
                        "baseline": {
                            "AIA CZ1": {
                                "Residential (New)": {
                                    "Heating (Env.)": {"2009": 20, "2010": 20},
                                    "Heating (Equip.)": {},
                                    "Cooling (Equip.)": {},
                                }
                            }
                        },
                        "efficient": {
                            "AIA CZ1": {
                                "Residential (New)": {
                                    "Heating (Env.)": {"2009": 10, "2010": 10},
                                    "Heating (Equip.)": {},
                                    "Cooling (Equip.)": {},
                                }
                            }
                        },
                        "savings": {
                            "AIA CZ1": {
                                "Residential (New)": {
                                    "Heating (Env.)": {"2009": 10, "2010": 10},
                                    "Heating (Equip.)": {},
                                    "Cooling (Equip.)": {},
                                }
                            }
                        },
                    },
                    "cost": {
                        "baseline": {
                            "AIA CZ1": {
                                "Residential (New)": {
                                    "Heating (Env.)": {"2009": 20, "2010": 20},
                                    "Heating (Equip.)": {},
                                    "Cooling (Equip.)": {},
                                }
                            }
                        },
                        "efficient": {
                            "AIA CZ1": {
                                "Residential (New)": {
                                    "Heating (Env.)": {"2009": 10, "2010": 10},
                                    "Heating (Equip.)": {},
                                    "Cooling (Equip.)": {},
                                }
                            }
                        },
                        "savings": {
                            "AIA CZ1": {
                                "Residential (New)": {
                                    "Heating (Env.)": {"2009": 10, "2010": 10},
                                    "Heating (Equip.)": {},
                                    "Cooling (Equip.)": {},
                                }
                            }
                        },
                    },
                },
            }
        },
    }
]
