"""Sample measures data for testing sector-level savings shapes.

This module contains test data for testing sector-level savings shapes for measure packages.
Includes measures with sector_shapes data for multiple measure types."""

sample_measures_in_sect_shapes = [
    {
        "name": "sample measure pkg env",
        "market_entry_year": None,
        "market_exit_year": None,
        "market_scaling_fractions": None,
        "market_scaling_fractions_source": None,
        "measure_type": "full service",
        "structure_type": ["new"],
        "climate_zone": ["TRE"],
        "bldg_type": ["single family home"],
        "fuel_type": {"primary": ["electricity"], "secondary": None},
        "fuel_switch_to": None,
        "end_use": {"primary": ["heating"], "secondary": None},
        "technology": {"primary": ["windows conduction", "wall"], "secondary": None},
        "technology_type": {"primary": ["demand"], "secondary": None},
        "sector_shapes": {
            "Technical potential": {
                "TRE": {
                    "2010": {
                        "baseline": [(20 / 8760) for h in range(8760)],
                        "efficient": [(10 / 8760) for h in range(8760)],
                    }
                }
            }
        },
        "markets": {
            "Technical potential": {
                "master_mseg": {
                    "stock": {
                        "total": {
                            "all": {"2009": 20, "2010": 20},
                            "measure": {"2009": 20, "2010": 20},
                        },
                        "competed": {
                            "all": {"2009": 20, "2010": 20},
                            "measure": {"2009": 20, "2010": 20},
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
                                "baseline": {"2009": 20, "2010": 20},
                                "efficient": {"2009": 20, "2010": 20},
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
                            "('primary', 'TRE', 'single family home', "
                            "'electricity', 'heating', 'demand', "
                            "'windows conduction', 'new')"
                        ): {
                            "stock": {
                                "total": {
                                    "all": {"2009": 10, "2010": 10},
                                    "measure": {"2009": 10, "2010": 10},
                                },
                                "competed": {
                                    "all": {"2009": 10, "2010": 10},
                                    "measure": {"2009": 10, "2010": 10},
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
                            "('primary', 'TRE', 'single family home', "
                            "'electricity', 'heating', 'demand', "
                            "'wall', 'new')"
                        ): {
                            "stock": {
                                "total": {
                                    "all": {"2009": 10, "2010": 10},
                                    "measure": {"2009": 10, "2010": 10},
                                },
                                "competed": {
                                    "all": {"2009": 10, "2010": 10},
                                    "measure": {"2009": 10, "2010": 10},
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
                    },
                    "competed choice parameters": {
                        (
                            "('primary', 'TRE', 'single family home', "
                            "'electricity', 'heating', 'demand', "
                            "'windows conduction', 'new')"
                        ): {"b1": {"2009": 1, "2010": 1}, "b2": {"2009": 1, "2010": 1}},
                        (
                            "('primary', 'TRE', 'single family home', "
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
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Env.)": {"2009": 20, "2010": 20},
                                    "Heating (Equip.)": {},
                                    "Cooling (Equip.)": {},
                                }
                            }
                        },
                        "efficient": {
                            "TRE": {
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
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Env.)": {"2009": 20, "2010": 20},
                                    "Heating (Equip.)": {},
                                    "Cooling (Equip.)": {},
                                }
                            }
                        },
                        "efficient": {
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Env.)": {"2009": 10, "2010": 10},
                                    "Heating (Equip.)": {},
                                    "Cooling (Equip.)": {},
                                }
                            }
                        },
                        "savings": {
                            "TRE": {
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
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Env.)": {"2009": 20, "2010": 20},
                                    "Heating (Equip.)": {},
                                    "Cooling (Equip.)": {},
                                }
                            }
                        },
                        "efficient": {
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Env.)": {"2009": 10, "2010": 10},
                                    "Heating (Equip.)": {},
                                    "Cooling (Equip.)": {},
                                }
                            }
                        },
                        "savings": {
                            "TRE": {
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
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Env.)": {"2009": 20, "2010": 20},
                                    "Heating (Equip.)": {},
                                    "Cooling (Equip.)": {},
                                }
                            }
                        },
                        "efficient": {
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Env.)": {"2009": 10, "2010": 10},
                                    "Heating (Equip.)": {},
                                    "Cooling (Equip.)": {},
                                }
                            }
                        },
                        "savings": {
                            "TRE": {
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
    },
    {
        "name": "sample measure pkg hvac",
        "market_entry_year": None,
        "market_exit_year": None,
        "market_scaling_fractions": None,
        "market_scaling_fractions_source": None,
        "measure_type": "full service",
        "structure_type": ["new"],
        "climate_zone": ["TRE"],
        "bldg_type": ["single family home"],
        "fuel_type": {"primary": ["electricity"], "secondary": None},
        "fuel_switch_to": None,
        "end_use": {"primary": ["cooling", "heating"], "secondary": None},
        "technology": {"primary": ["ASHP"], "secondary": None},
        "technology_type": {"primary": ["supply"], "secondary": None},
        "sector_shapes": {
            "Technical potential": {
                "TRE": {
                    "2010": {
                        "baseline": [(20 / 8760) for h in range(8760)],
                        "efficient": [(10 / 8760) for h in range(8760)],
                    }
                }
            }
        },
        "markets": {
            "Technical potential": {
                "master_mseg": {
                    "stock": {
                        "total": {
                            "all": {"2009": 20, "2010": 20},
                            "measure": {"2009": 20, "2010": 20},
                        },
                        "competed": {
                            "all": {"2009": 20, "2010": 20},
                            "measure": {"2009": 20, "2010": 20},
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
                                "baseline": {"2009": 20, "2010": 20},
                                "efficient": {"2009": 20, "2010": 20},
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
                            "('primary', 'TRE', 'single family home', "
                            "'electricity', 'cooling', 'supply', "
                            "'ASHP', 'new')"
                        ): {
                            "stock": {
                                "total": {
                                    "all": {"2009": 10, "2010": 10},
                                    "measure": {"2009": 10, "2010": 10},
                                },
                                "competed": {
                                    "all": {"2009": 10, "2010": 10},
                                    "measure": {"2009": 10, "2010": 10},
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
                            "('primary', 'TRE', 'single family home', "
                            "'electricity', 'heating', 'supply', "
                            "'ASHP', 'new')"
                        ): {
                            "stock": {
                                "total": {
                                    "all": {"2009": 10, "2010": 10},
                                    "measure": {"2009": 10, "2010": 10},
                                },
                                "competed": {
                                    "all": {"2009": 10, "2010": 10},
                                    "measure": {"2009": 10, "2010": 10},
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
                    },
                    "competed choice parameters": {
                        (
                            "('primary', 'AIA_CZ1', 'single family home', "
                            "'electricity', 'cooling', 'supply', "
                            "'ASHP', 'new')"
                        ): {"b1": {"2009": 1, "2010": 1}, "b2": {"2009": 1, "2010": 1}},
                        (
                            "('primary', 'AIA_CZ1', 'single family home', "
                            "'electricity', 'heating', 'supply', "
                            "'ASHP', 'new')"
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
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Equip.)": {"2009": 10, "2010": 10},
                                    "Cooling (Equip.)": {"2009": 10, "2010": 10},
                                    "Heating (Env.)": {},
                                }
                            }
                        },
                        "efficient": {
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Equip.)": {"2009": 5, "2010": 5},
                                    "Cooling (Equip.)": {"2009": 5, "2010": 5},
                                    "Heating (Env.)": {},
                                }
                            }
                        },
                    },
                    "energy": {
                        "baseline": {
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Equip.)": {"2009": 10, "2010": 10},
                                    "Cooling (Equip.)": {"2009": 10, "2010": 10},
                                    "Heating (Env.)": {},
                                }
                            }
                        },
                        "efficient": {
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Equip.)": {"2009": 5, "2010": 5},
                                    "Cooling (Equip.)": {"2009": 5, "2010": 5},
                                    "Heating (Env.)": {},
                                }
                            }
                        },
                        "savings": {
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Equip.)": {"2009": 5, "2010": 5},
                                    "Cooling (Equip.)": {"2009": 5, "2010": 5},
                                    "Heating (Env.)": {},
                                }
                            }
                        },
                    },
                    "carbon": {
                        "baseline": {
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Equip.)": {"2009": 10, "2010": 10},
                                    "Cooling (Equip.)": {"2009": 10, "2010": 10},
                                    "Heating (Env.)": {},
                                }
                            }
                        },
                        "efficient": {
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Equip.)": {"2009": 5, "2010": 5},
                                    "Cooling (Equip.)": {"2009": 5, "2010": 5},
                                    "Heating (Env.)": {},
                                }
                            }
                        },
                        "savings": {
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Equip.)": {"2009": 5, "2010": 5},
                                    "Cooling (Equip.)": {"2009": 5, "2010": 5},
                                    "Heating (Env.)": {},
                                }
                            }
                        },
                    },
                    "cost": {
                        "baseline": {
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Equip.)": {"2009": 10, "2010": 10},
                                    "Cooling (Equip.)": {"2009": 10, "2010": 10},
                                    "Heating (Env.)": {},
                                }
                            }
                        },
                        "efficient": {
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Equip.)": {"2009": 5, "2010": 5},
                                    "Cooling (Equip.)": {"2009": 5, "2010": 5},
                                    "Heating (Env.)": {},
                                }
                            }
                        },
                        "savings": {
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Equip.)": {"2009": 5, "2010": 5},
                                    "Cooling (Equip.)": {"2009": 5, "2010": 5},
                                    "Heating (Env.)": {},
                                }
                            }
                        },
                    },
                },
            }
        },
    },
    {
        "name": "sample measure pkg ctl",
        "market_entry_year": None,
        "market_exit_year": None,
        "market_scaling_fractions": 0.5,
        "market_scaling_fractions_source": None,
        "measure_type": "add-on",
        "structure_type": ["new"],
        "climate_zone": ["TRE"],
        "bldg_type": ["single family home", "multi family home"],
        "fuel_type": {"primary": ["electricity"], "secondary": None},
        "fuel_switch_to": None,
        "end_use": {"primary": ["heating"], "secondary": None},
        "technology": {"primary": ["ASHP"], "secondary": None},
        "technology_type": {"primary": ["supply"], "secondary": None},
        "sector_shapes": {
            "Technical potential": {
                "TRE": {
                    "2010": {
                        "baseline": [(10 / 8760) for h in range(8760)],
                        "efficient": [(5 / 8760) for h in range(8760)],
                    }
                },
            }
        },
        "markets": {
            "Technical potential": {
                "master_mseg": {
                    "stock": {
                        "total": {
                            "all": {"2009": 10, "2010": 10},
                            "measure": {"2009": 10, "2010": 10},
                        },
                        "competed": {
                            "all": {"2009": 10, "2010": 10},
                            "measure": {"2009": 10, "2010": 10},
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
                    "sub-market scaling": 0.5,
                },
                "mseg_adjust": {
                    "contributing mseg keys and values": {
                        (
                            "('primary', 'TRE', 'single family home', "
                            "'electricity', 'heating', 'supply', "
                            "'ASHP', 'new')"
                        ): {
                            "stock": {
                                "total": {
                                    "all": {"2009": 5, "2010": 5},
                                    "measure": {"2009": 5, "2010": 5},
                                },
                                "competed": {
                                    "all": {"2009": 5, "2010": 5},
                                    "measure": {"2009": 5, "2010": 5},
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
                            "cost": {
                                "stock": {
                                    "total": {
                                        "baseline": {"2009": 5, "2010": 5},
                                        "efficient": {"2009": 5, "2010": 5},
                                    },
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
                        (
                            "('primary', 'TRE', 'multi family home', "
                            "'electricity', 'heating', 'supply', "
                            "'ASHP', 'new')"
                        ): {
                            "stock": {
                                "total": {
                                    "all": {"2009": 5, "2010": 5},
                                    "measure": {"2009": 5, "2010": 5},
                                },
                                "competed": {
                                    "all": {"2009": 5, "2010": 5},
                                    "measure": {"2009": 5, "2010": 5},
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
                            "cost": {
                                "stock": {
                                    "total": {
                                        "baseline": {"2009": 5, "2010": 5},
                                        "efficient": {"2009": 5, "2010": 5},
                                    },
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
                    },
                    "competed choice parameters": {
                        (
                            "('primary', 'TRE', 'single family home', "
                            "'electricity', 'heating', 'supply', "
                            "'ASHP', 'new')"
                        ): {"b1": {"2009": 1, "2010": 1}, "b2": {"2009": 1, "2010": 1}},
                        (
                            "('primary', 'TRE', 'multi family home', "
                            "'electricity', 'heating', 'supply', "
                            "'ASHP', 'new')"
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
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Equip.)": {"2009": 10, "2010": 10},
                                    "Cooling (Equip.)": {},
                                    "Heating (Env.)": {},
                                }
                            }
                        },
                        "efficient": {
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Equip.)": {"2009": 5, "2010": 5},
                                    "Cooling (Equip.)": {},
                                    "Heating (Env.)": {},
                                }
                            }
                        },
                    },
                    "energy": {
                        "baseline": {
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Equip.)": {"2009": 10, "2010": 10},
                                    "Cooling (Equip.)": {},
                                    "Heating (Env.)": {},
                                }
                            }
                        },
                        "efficient": {
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Equip.)": {"2009": 5, "2010": 5},
                                    "Cooling (Equip.)": {},
                                    "Heating (Env.)": {},
                                }
                            }
                        },
                        "savings": {
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Equip.)": {"2009": 5, "2010": 5},
                                    "Cooling (Equip.)": {},
                                    "Heating (Env.)": {},
                                }
                            }
                        },
                    },
                    "carbon": {
                        "baseline": {
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Equip.)": {"2009": 10, "2010": 10},
                                    "Cooling (Equip.)": {},
                                    "Heating (Env.)": {},
                                }
                            }
                        },
                        "efficient": {
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Equip.)": {"2009": 5, "2010": 5},
                                    "Cooling (Equip.)": {},
                                    "Heating (Env.)": {},
                                }
                            }
                        },
                        "savings": {
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Equip.)": {"2009": 5, "2010": 5},
                                    "Cooling (Equip.)": {},
                                    "Heating (Env.)": {},
                                }
                            }
                        },
                    },
                    "cost": {
                        "baseline": {
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Equip.)": {"2009": 10, "2010": 10},
                                    "Cooling (Equip.)": {},
                                    "Heating (Env.)": {},
                                }
                            }
                        },
                        "efficient": {
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Equip.)": {"2009": 5, "2010": 5},
                                    "Cooling (Equip.)": {},
                                    "Heating (Env.)": {},
                                }
                            }
                        },
                        "savings": {
                            "TRE": {
                                "Residential (New)": {
                                    "Heating (Equip.)": {"2009": 5, "2010": 5},
                                    "Cooling (Equip.)": {},
                                    "Heating (Env.)": {},
                                }
                            }
                        },
                    },
                },
            }
        },
    },
]
