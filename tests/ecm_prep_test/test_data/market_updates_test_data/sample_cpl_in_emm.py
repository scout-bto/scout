#!/usr/bin/env python3

"""Extracted test data for Market Updates tests."""

sample_cpl_in_emm = {
    "TRE": {
        "large office": {
            "electricity": {
                "cooling": {
                    "supply": {
                        "rooftop_AC": {
                            "performance": {
                                "typical": {"2009": 1, "2010": 1},
                                "best": {"2009": 1, "2010": 1},
                                "units": "BTU out/BTU in",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 50, "2010": 50},
                                "best": {"2009": 50, "2010": 50},
                                "units": "2009$/kBtu/h cooling",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 15, "2010": 15},
                                "range": {"2009": 10, "2010": 10},
                                "units": "years",
                                "source": "EIA AEO",
                            },
                            "consumer choice": {},
                        },
                        "rooftop_ASHP-cool": {
                            "performance": {
                                "typical": {"2009": 1, "2010": 1},
                                "best": {"2009": 1, "2010": 1},
                                "units": "BTU out/BTU in",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 50, "2010": 50},
                                "best": {"2009": 50, "2010": 50},
                                "units": "2009$/kBtu/h cooling",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 15, "2010": 15},
                                "range": {"2009": 10, "2010": 10},
                                "units": "years",
                                "source": "EIA AEO",
                            },
                            "consumer choice": {},
                        },
                    }
                },
                "heating": {
                    "supply": {
                        "electric_res-heat": {
                            "performance": {
                                "typical": {"2009": 1, "2010": 1},
                                "best": {"2009": 1, "2010": 1},
                                "units": "BTU out/BTU in",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 50, "2010": 50},
                                "best": {"2009": 50, "2010": 50},
                                "units": "2009$/kBtu/h heating",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 15, "2010": 15},
                                "range": {"2009": 10, "2010": 10},
                                "units": "years",
                                "source": "EIA AEO",
                            },
                            "consumer choice": {},
                        },
                        "rooftop_ASHP-heat": {
                            "performance": {
                                "typical": {"2009": 1, "2010": 1},
                                "best": {"2009": 1, "2010": 1},
                                "units": "BTU out/BTU in",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 50, "2010": 50},
                                "best": {"2009": 50, "2010": 50},
                                "units": "2009$/kBtu/h heating",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 15, "2010": 15},
                                "range": {"2009": 10, "2010": 10},
                                "units": "years",
                                "source": "EIA AEO",
                            },
                            "consumer choice": {},
                        },
                    }
                },
                "refrigeration": {
                    "Commercial Ice Machines": {
                        "performance": {
                            "typical": {"2009": 1, "2010": 1},
                            "best": {"2009": 1, "2010": 1},
                            "units": "BTU out/BTU in",
                            "source": "EIA AEO",
                        },
                        "installed cost": {
                            "typical": {"2009": 50, "2010": 50},
                            "best": {"2009": 50, "2010": 50},
                            "units": "2009$/kBtu/h refrigeration",
                            "source": "EIA AEO",
                        },
                        "lifetime": {
                            "average": {"2009": 15, "2010": 15},
                            "range": {"2009": 10, "2010": 10},
                            "units": "years",
                            "source": "EIA AEO",
                        },
                        "consumer choice": {},
                    }
                },
            },
            "natural gas": {
                "heating": {
                    "supply": {
                        "gas_furnace": {
                            "performance": {
                                "typical": {"2009": 1, "2010": 1},
                                "best": {"2009": 1, "2010": 1},
                                "units": "BTU out/BTU in",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 50, "2010": 50},
                                "best": {"2009": 50, "2010": 50},
                                "units": "2009$/kBtu/h heating",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 15, "2010": 15},
                                "range": {"2009": 10, "2010": 10},
                                "units": "years",
                                "source": "EIA AEO",
                            },
                            "consumer choice": {},
                        }
                    }
                }
            },
        },
        "single family home": {
            "electricity": {
                "cooling": {
                    "supply": {
                        "ASHP": {
                            "performance": {
                                "typical": {"2009": 12, "2010": 12},
                                "best": {"2009": 12, "2010": 12},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "before incentives": {
                                    "typical": {
                                        "new": {"2009": 24, "2010": 24},
                                        "existing": {"2009": 12, "2010": 12},
                                    },
                                    "best": {
                                        "new": {"2009": 24, "2010": 24},
                                        "existing": {"2009": 12, "2010": 12},
                                    },
                                    "units": "2009$/unit",
                                    "source": "EIA AEO",
                                },
                                "incentives": {
                                    "by performance tier": {
                                        "new": {
                                            "2009": [[10, 0], [15, 12], [25, 12]],
                                            "2010": [[10, 0], [15, 12], [25, 12]],
                                        },
                                        "existing": {
                                            "2009": [[10, 0], [15, 6], [25, 6]],
                                            "2010": [[10, 0], [15, 6], [25, 6]],
                                        },
                                    },
                                    "performance units": "COP",
                                },
                            },
                            "lifetime": {
                                "average": {"2009": 12, "2010": 12},
                                "range": {"2009": 3, "2010": 3},
                                "units": "years",
                                "source": "EIA AEO",
                            },
                            "consumer choice": {
                                "competed market share": {
                                    "source": "EIA AEO",
                                    "model type": "logistic regression",
                                    "parameters": {
                                        "b1": {"2009": "NA", "2010": "NA"},
                                        "b2": {"2009": "NA", "2010": "NA"},
                                    },
                                },
                                "competed market": {
                                    "source": "COBAM",
                                    "model type": "bass diffusion",
                                    "parameters": {"p": "NA", "q": "NA"},
                                },
                            },
                        },
                        "central AC": {
                            "performance": {
                                "typical": {"2009": 1, "2010": 1},
                                "best": {"2009": 1, "2010": 1},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 1000, "2010": 1000},
                                "best": {"2009": 1000, "2010": 1000},
                                "units": "2009$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 15, "2010": 15},
                                "range": {"2009": 10, "2010": 10},
                                "units": "years",
                                "source": "EIA AEO",
                            },
                            "consumer choice": {
                                "competed market share": {
                                    "source": "EIA AEO",
                                    "model type": "logistic regression",
                                    "parameters": {
                                        "b1": {"2009": "NA", "2010": "NA"},
                                        "b2": {"2009": "NA", "2010": "NA"},
                                    },
                                },
                                "competed market": {
                                    "source": "COBAM",
                                    "model type": "bass diffusion",
                                    "parameters": {"p": "NA", "q": "NA"},
                                },
                            },
                        },
                    }
                },
                "heating": {
                    "supply": {
                        "ASHP": {
                            "performance": {
                                "typical": {"2009": 12, "2010": 12},
                                "best": {"2009": 12, "2010": 12},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "before incentives": {
                                    "typical": {
                                        "new": {"2009": 24, "2010": 24},
                                        "existing": {"2009": 12, "2010": 12},
                                    },
                                    "best": {
                                        "new": {"2009": 24, "2010": 24},
                                        "existing": {"2009": 12, "2010": 12},
                                    },
                                    "units": "2009$/unit",
                                    "source": "EIA AEO",
                                },
                                "incentives": {
                                    "by performance tier": {
                                        "new": {
                                            "2009": [[10, 0], [15, 12], [25, 12]],
                                            "2010": [[10, 0], [15, 12], [25, 12]],
                                        },
                                        "existing": {
                                            "2009": [[10, 0], [15, 6], [25, 6]],
                                            "2010": [[10, 0], [15, 6], [25, 6]],
                                        },
                                    },
                                    "performance units": "COP",
                                },
                            },
                            "lifetime": {
                                "average": {"2009": 12, "2010": 12},
                                "range": {"2009": 3, "2010": 3},
                                "units": "years",
                                "source": "EIA AEO",
                            },
                            "consumer choice": {
                                "competed market share": {
                                    "source": "EIA AEO",
                                    "model type": "logistic regression",
                                    "parameters": {
                                        "b1": {"2009": "NA", "2010": "NA"},
                                        "b2": {"2009": "NA", "2010": "NA"},
                                    },
                                },
                                "competed market": {
                                    "source": "COBAM",
                                    "model type": "bass diffusion",
                                    "parameters": {"p": "NA", "q": "NA"},
                                },
                            },
                        },
                        "resistance heat": {
                            "performance": {
                                "typical": {"2009": 1, "2010": 1},
                                "best": {"2009": 1, "2010": 1},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 1000, "2010": 1000},
                                "best": {"2009": 1000, "2010": 1000},
                                "units": "2009$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 15, "2010": 15},
                                "range": {"2009": 10, "2010": 10},
                                "units": "years",
                                "source": "EIA AEO",
                            },
                            "consumer choice": {
                                "competed market share": {
                                    "source": "EIA AEO",
                                    "model type": "logistic regression",
                                    "parameters": {
                                        "b1": {"2009": "NA", "2010": "NA"},
                                        "b2": {"2009": "NA", "2010": "NA"},
                                    },
                                },
                                "competed market": {
                                    "source": "COBAM",
                                    "model type": "bass diffusion",
                                    "parameters": {"p": "NA", "q": "NA"},
                                },
                            },
                        },
                    }
                },
                "water heating": {
                    "electric WH": {
                        "performance": {
                            "typical": {"2009": 1, "2010": 1},
                            "best": {"2009": 1, "2010": 1},
                            "units": "UEF",
                            "source": "EIA AEO",
                        },
                        "installed cost": {
                            "typical": {"2009": 1000, "2010": 1000},
                            "best": {"2009": 1000, "2010": 1000},
                            "units": "2009$/unit",
                            "source": "EIA AEO",
                        },
                        "lifetime": {
                            "average": {"2009": 15, "2010": 15},
                            "range": {"2009": 10, "2010": 10},
                            "units": "years",
                            "source": "EIA AEO",
                        },
                        "consumer choice": {
                            "competed market share": {
                                "source": "EIA AEO",
                                "model type": "logistic regression",
                                "parameters": {
                                    "b1": {"2009": "NA", "2010": "NA"},
                                    "b2": {"2009": "NA", "2010": "NA"},
                                },
                            },
                            "competed market": {
                                "source": "COBAM",
                                "model type": "bass diffusion",
                                "parameters": {"p": "NA", "q": "NA"},
                            },
                        },
                    }
                },
            },
            "natural gas": {
                "heating": {
                    "supply": {
                        "furnace (NG)": {
                            "performance": {
                                "typical": {"2009": 1, "2010": 1},
                                "best": {"2009": 1, "2010": 1},
                                "units": "AFUE",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 1000, "2010": 1000},
                                "best": {"2009": 1000, "2010": 1000},
                                "units": "2009$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 15, "2010": 15},
                                "range": {"2009": 10, "2010": 10},
                                "units": "years",
                                "source": "EIA AEO",
                            },
                            "consumer choice": {
                                "competed market share": {
                                    "source": "EIA AEO",
                                    "model type": "logistic regression",
                                    "parameters": {
                                        "b1": {"2009": "NA", "2010": "NA"},
                                        "b2": {"2009": "NA", "2010": "NA"},
                                    },
                                },
                                "competed market": {
                                    "source": "COBAM",
                                    "model type": "bass diffusion",
                                    "parameters": {"p": "NA", "q": "NA"},
                                },
                            },
                        }
                    }
                },
                "water heating": {
                    "performance": {
                        "typical": {"2009": 1, "2010": 1},
                        "best": {"2009": 1, "2010": 1},
                        "units": "UEF",
                        "source": "EIA AEO",
                    },
                    "installed cost": {
                        "typical": {"2009": 1000, "2010": 1000},
                        "best": {"2009": 1000, "2010": 1000},
                        "units": "2009$/unit",
                        "source": "EIA AEO",
                    },
                    "lifetime": {
                        "average": {"2009": 15, "2010": 15},
                        "range": {"2009": 10, "2010": 10},
                        "units": "years",
                        "source": "EIA AEO",
                    },
                    "consumer choice": {
                        "competed market share": {
                            "source": "EIA AEO",
                            "model type": "logistic regression",
                            "parameters": {
                                "b1": {"2009": "NA", "2010": "NA"},
                                "b2": {"2009": "NA", "2010": "NA"},
                            },
                        },
                        "competed market": {
                            "source": "COBAM",
                            "model type": "bass diffusion",
                            "parameters": {"p": "NA", "q": "NA"},
                        },
                    },
                },
            },
        },
    },
    "CASO": {
        "single family home": {
            "electricity": {
                "cooling": {
                    "supply": {
                        "ASHP": {
                            "performance": {
                                "typical": {"2009": 12, "2010": 12},
                                "best": {"2009": 12, "2010": 12},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "before incentives": {
                                    "typical": {
                                        "new": {"2009": 24, "2010": 24},
                                        "existing": {"2009": 12, "2010": 12},
                                    },
                                    "best": {
                                        "new": {"2009": 24, "2010": 24},
                                        "existing": {"2009": 12, "2010": 12},
                                    },
                                    "units": "2009$/unit",
                                    "source": "EIA AEO",
                                },
                                "incentives": {
                                    "by performance tier": {
                                        "new": {
                                            "2009": [[10, 0], [15, 12], [25, 12]],
                                            "2010": [[10, 0], [15, 12], [25, 12]],
                                        },
                                        "existing": {
                                            "2009": [[10, 0], [15, 6], [25, 6]],
                                            "2010": [[10, 0], [15, 6], [25, 6]],
                                        },
                                    },
                                    "performance units": "COP",
                                },
                            },
                            "lifetime": {
                                "average": {"2009": 12, "2010": 12},
                                "range": {"2009": 3, "2010": 3},
                                "units": "years",
                                "source": "EIA AEO",
                            },
                            "consumer choice": {
                                "competed market share": {
                                    "source": "EIA AEO",
                                    "model type": "logistic regression",
                                    "parameters": {
                                        "b1": {"2009": "NA", "2010": "NA"},
                                        "b2": {"2009": "NA", "2010": "NA"},
                                    },
                                },
                                "competed market": {
                                    "source": "COBAM",
                                    "model type": "bass diffusion",
                                    "parameters": {"p": "NA", "q": "NA"},
                                },
                            },
                        },
                        "central AC": {
                            "performance": {
                                "typical": {"2009": 1, "2010": 1},
                                "best": {"2009": 1, "2010": 1},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 1000, "2010": 1000},
                                "best": {"2009": 1000, "2010": 1000},
                                "units": "2009$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 15, "2010": 15},
                                "range": {"2009": 10, "2010": 10},
                                "units": "years",
                                "source": "EIA AEO",
                            },
                            "consumer choice": {
                                "competed market share": {
                                    "source": "EIA AEO",
                                    "model type": "logistic regression",
                                    "parameters": {
                                        "b1": {"2009": "NA", "2010": "NA"},
                                        "b2": {"2009": "NA", "2010": "NA"},
                                    },
                                },
                                "competed market": {
                                    "source": "COBAM",
                                    "model type": "bass diffusion",
                                    "parameters": {"p": "NA", "q": "NA"},
                                },
                            },
                        },
                    }
                },
                "heating": {
                    "supply": {
                        "ASHP": {
                            "performance": {
                                "typical": {"2009": 12, "2010": 12},
                                "best": {"2009": 12, "2010": 12},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "before incentives": {
                                    "typical": {
                                        "new": {"2009": 24, "2010": 24},
                                        "existing": {"2009": 12, "2010": 12},
                                    },
                                    "best": {
                                        "new": {"2009": 24, "2010": 24},
                                        "existing": {"2009": 12, "2010": 12},
                                    },
                                    "units": "2009$/unit",
                                    "source": "EIA AEO",
                                },
                                "incentives": {
                                    "by performance tier": {
                                        "new": {
                                            "2009": [[10, 0], [15, 12], [25, 12]],
                                            "2010": [[10, 0], [15, 12], [25, 12]],
                                        },
                                        "existing": {
                                            "2009": [[10, 0], [15, 6], [25, 6]],
                                            "2010": [[10, 0], [15, 6], [25, 6]],
                                        },
                                    },
                                    "performance units": "COP",
                                },
                            },
                            "lifetime": {
                                "average": {"2009": 12, "2010": 12},
                                "range": {"2009": 3, "2010": 3},
                                "units": "years",
                                "source": "EIA AEO",
                            },
                            "consumer choice": {
                                "competed market share": {
                                    "source": "EIA AEO",
                                    "model type": "logistic regression",
                                    "parameters": {
                                        "b1": {"2009": "NA", "2010": "NA"},
                                        "b2": {"2009": "NA", "2010": "NA"},
                                    },
                                },
                                "competed market": {
                                    "source": "COBAM",
                                    "model type": "bass diffusion",
                                    "parameters": {"p": "NA", "q": "NA"},
                                },
                            },
                        },
                        "resistance heat": {
                            "performance": {
                                "typical": {"2009": 1, "2010": 1},
                                "best": {"2009": 1, "2010": 1},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 1000, "2010": 1000},
                                "best": {"2009": 1000, "2010": 1000},
                                "units": "2009$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 15, "2010": 15},
                                "range": {"2009": 10, "2010": 10},
                                "units": "years",
                                "source": "EIA AEO",
                            },
                            "consumer choice": {
                                "competed market share": {
                                    "source": "EIA AEO",
                                    "model type": "logistic regression",
                                    "parameters": {
                                        "b1": {"2009": "NA", "2010": "NA"},
                                        "b2": {"2009": "NA", "2010": "NA"},
                                    },
                                },
                                "competed market": {
                                    "source": "COBAM",
                                    "model type": "bass diffusion",
                                    "parameters": {"p": "NA", "q": "NA"},
                                },
                            },
                        },
                    }
                },
            },
            "natural gas": {
                "heating": {
                    "supply": {
                        "furnace (NG)": {
                            "performance": {
                                "typical": {"2009": 1, "2010": 1},
                                "best": {"2009": 1, "2010": 1},
                                "units": "AFUE",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 1000, "2010": 1000},
                                "best": {"2009": 1000, "2010": 1000},
                                "units": "2009$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 15, "2010": 15},
                                "range": {"2009": 10, "2010": 10},
                                "units": "years",
                                "source": "EIA AEO",
                            },
                            "consumer choice": {
                                "competed market share": {
                                    "source": "EIA AEO",
                                    "model type": "logistic regression",
                                    "parameters": {
                                        "b1": {"2009": "NA", "2010": "NA"},
                                        "b2": {"2009": "NA", "2010": "NA"},
                                    },
                                },
                                "competed market": {
                                    "source": "COBAM",
                                    "model type": "bass diffusion",
                                    "parameters": {"p": "NA", "q": "NA"},
                                },
                            },
                        }
                    }
                }
            },
        }
    },
}
