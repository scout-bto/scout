#!/usr/bin/env python3

"""Extracted test data for Update Measures tests."""

sample_cpl_in_aia = {
    "AIA_CZ1": {
        "single family home": {
            "electricity": {
                "heating": {
                    "demand": {
                        "windows conduction": {
                            "performance": {
                                "typical": {"2009": 1, "2010": 1},
                                "best": {"2009": 1, "2010": 1},
                                "units": "R Value",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 1, "2010": 1},
                                "best": {"2009": 1, "2010": 1},
                                "units": "2014$/ft^2 floor",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 10, "2010": 10},
                                "range": {"2009": 1, "2010": 1},
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
                        "windows solar": {
                            "performance": {
                                "typical": {"2009": 2, "2010": 2},
                                "best": {"2009": 2, "2010": 2},
                                "units": "SHGC",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 2, "2010": 2},
                                "best": {"2009": 2, "2010": 2},
                                "units": "2014$/ft^2 floor",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 20, "2010": 20},
                                "range": {"2009": 2, "2010": 2},
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
                        "infiltration": {
                            "performance": {
                                "typical": {"2009": 2, "2010": 3},
                                "best": {"2009": 2, "2010": 3},
                                "units": "ACH50",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 2, "2010": 2},
                                "best": {"2009": 2, "2010": 2},
                                "units": "2014$/ft^2 floor",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 20, "2010": 20},
                                "range": {"2009": 2, "2010": 2},
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
                    "supply": {
                        "resistance heat": {
                            "performance": {
                                "typical": {"2009": 2, "2010": 2},
                                "best": {"2009": 2, "2010": 2},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 2, "2010": 2},
                                "best": {"2009": 2, "2010": 2},
                                "units": "2014$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 20, "2010": 20},
                                "range": {"2009": 2, "2010": 2},
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
                        "ASHP": {
                            "performance": {
                                "typical": {"2009": 3, "2010": 3},
                                "best": {"2009": 3, "2010": 3},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {
                                    "new": {"2009": 6, "2010": 6},
                                    "existing": {"2009": 3, "2010": 3},
                                },
                                "best": {
                                    "new": {"2009": 6, "2010": 6},
                                    "existing": {"2009": 3, "2010": 3},
                                },
                                "units": "2014$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 30, "2010": 30},
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
                        "GSHP": {
                            "performance": {
                                "typical": {"2009": 4, "2010": 4},
                                "best": {"2009": 4, "2010": 4},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {
                                    "new": {"2009": 8, "2010": 8},
                                    "existing": {"2009": 4, "2010": 4},
                                },
                                "best": {
                                    "new": {"2009": 8, "2010": 8},
                                    "existing": {"2009": 4, "2010": 4},
                                },
                                "units": "2014$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 40, "2010": 40},
                                "range": {"2009": 4, "2010": 4},
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
                "cooling": {
                    "demand": {
                        "windows conduction": {
                            "performance": {
                                "typical": {
                                    "new": {"2009": 8, "2010": 8},
                                    "existing": {"2009": 8, "2010": 8},
                                },
                                "best": {"2009": 8, "2010": 8},
                                "units": "R Value",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 8, "2010": 8},
                                "best": {"2009": 8, "2010": 8},
                                "units": "2014$/ft^2 floor",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 80, "2010": 80},
                                "range": {"2009": 8, "2010": 8},
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
                        "windows solar": {
                            "performance": {
                                "typical": {"2009": 9, "2010": 9},
                                "best": {"2009": 9, "2010": 9},
                                "units": "SHGC",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 9, "2010": 9},
                                "best": {"2009": 9, "2010": 9},
                                "units": "2014$/ft^2 floor",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 90, "2010": 90},
                                "range": {"2009": 9, "2010": 9},
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
                        "infiltration": {
                            "performance": {
                                "typical": {"2009": 2, "2010": 3},
                                "best": {"2009": 2, "2010": 3},
                                "units": "ACH50",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 2, "2010": 2},
                                "best": {"2009": 2, "2010": 2},
                                "units": "2014$/ft^2 floor",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 20, "2010": 20},
                                "range": {"2009": 2, "2010": 2},
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
                    "supply": {
                        "central AC": {
                            "performance": {
                                "typical": {"2009": 10, "2010": 10},
                                "best": {"2009": 10, "2010": 10},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 10, "2010": 10},
                                "best": {"2009": 10, "2010": 10},
                                "units": "2014$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 100, "2010": 100},
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
                        "room AC": {
                            "performance": {
                                "typical": {"2009": 11, "2010": 11},
                                "best": {"2009": 11, "2010": 11},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 11, "2010": 11},
                                "best": {"2009": 11, "2010": 11},
                                "units": "2014$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 110, "2010": 110},
                                "range": {"2009": 11, "2010": 11},
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
                        "ASHP": {
                            "performance": {
                                "typical": {"2009": 12, "2010": 12},
                                "best": {"2009": 12, "2010": 12},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {
                                    "new": {"2009": 24, "2010": 24},
                                    "existing": {"2009": 12, "2010": 12},
                                },
                                "best": {
                                    "new": {"2009": 24, "2010": 24},
                                    "existing": {"2009": 12, "2010": 12},
                                },
                                "units": "2014$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 120, "2010": 120},
                                "range": {"2009": 12, "2010": 12},
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
                        "GSHP": {
                            "performance": {
                                "typical": {"2009": 13, "2010": 13},
                                "best": {"2009": 13, "2010": 13},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {
                                    "new": {"2009": 26, "2010": 26},
                                    "existing": {"2009": 13, "2010": 13},
                                },
                                "best": {
                                    "new": {"2009": 26, "2010": 26},
                                    "existing": {"2009": 13, "2010": 13},
                                },
                                "units": "2014$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 130, "2010": 130},
                                "range": {"2009": 13, "2010": 13},
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
            "natural gas": {
                "water heating": {
                    "performance": {
                        "typical": {"2009": 18, "2010": 18},
                        "best": {"2009": 18, "2010": 18},
                        "units": "EF",
                        "source": "EIA AEO",
                    },
                    "installed cost": {
                        "before incentives": {
                            "typical": {
                                "new": {"2009": 18, "2010": 18},
                                "existing": {"2009": 18, "2010": 18},
                            },
                            "best": {
                                "new": {"2009": 18, "2010": 18},
                                "existing": {"2009": 18, "2010": 18},
                            },
                            "units": "2014$/unit",
                            "source": "EIA AEO",
                        },
                        "incentives": {
                            "by performance tier": {
                                "2009": [[10, 0], [15, 0], [20, 3], [25, 9]],
                                "2010": [[10, 0], [15, 0], [20, 3], [25, 9]],
                            },
                            "performance units": "EF",
                        },
                    },
                    "lifetime": {
                        "average": {"2009": 180, "2010": 180},
                        "range": {"2009": 18, "2010": 18},
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
        }
    },
    "AIA_CZ2": {
        "single family home": {
            "electricity": {
                "heating": {
                    "demand": {
                        "windows conduction": {
                            "performance": {
                                "typical": {"2009": 1, "2010": 1},
                                "best": {"2009": 1, "2010": 1},
                                "units": "R Value",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 1, "2010": 1},
                                "best": {"2009": 1, "2010": 1},
                                "units": "2014$/ft^2 floor",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 10, "2010": 10},
                                "range": {"2009": 1, "2010": 1},
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
                        "windows solar": {
                            "performance": {
                                "typical": {"2009": 2, "2010": 2},
                                "best": {"2009": 2, "2010": 2},
                                "units": "SHGC",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 2, "2010": 2},
                                "best": {"2009": 2, "2010": 2},
                                "units": "2014$/ft^2 floor",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 20, "2010": 20},
                                "range": {"2009": 2, "2010": 2},
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
                        "infiltration": {
                            "performance": {
                                "typical": {"2009": 2, "2010": 3},
                                "best": {"2009": 2, "2010": 3},
                                "units": "ACH50",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 2, "2010": 2},
                                "best": {"2009": 2, "2010": 2},
                                "units": "2014$/ft^2 floor",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 20, "2010": 20},
                                "range": {"2009": 2, "2010": 2},
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
                    "supply": {
                        "resistance heat": {
                            "performance": {
                                "typical": {"2009": 2, "2010": 2},
                                "best": {"2009": 2, "2010": 2},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 2, "2010": 2},
                                "best": {"2009": 2, "2010": 2},
                                "units": "2014$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 20, "2010": 20},
                                "range": {"2009": 2, "2010": 2},
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
                        "ASHP": {
                            "performance": {
                                "typical": {"2009": 3, "2010": 3},
                                "best": {"2009": 3, "2010": 3},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {
                                    "new": {"2009": 6, "2010": 6},
                                    "existing": {"2009": 3, "2010": 3},
                                },
                                "best": {
                                    "new": {"2009": 6, "2010": 6},
                                    "existing": {"2009": 3, "2010": 3},
                                },
                                "units": "2014$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 30, "2010": 30},
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
                        "GSHP": {
                            "performance": {
                                "typical": {"2009": 4, "2010": 4},
                                "best": {"2009": 4, "2010": 4},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {
                                    "new": {"2009": 4, "2010": 4},
                                    "existing": {"2009": 2, "2010": 2},
                                },
                                "best": {
                                    "new": {"2009": 4, "2010": 4},
                                    "existing": {"2009": 2, "2010": 2},
                                },
                                "units": "2014$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 40, "2010": 40},
                                "range": {"2009": 4, "2010": 4},
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
                "cooling": {
                    "demand": {
                        "windows conduction": {
                            "performance": {
                                "typical": {"2009": 8, "2010": 8},
                                "best": {"2009": 8, "2010": 8},
                                "units": "R Value",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 8, "2010": 8},
                                "best": {"2009": 8, "2010": 8},
                                "units": "2014$/ft^2 floor",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 80, "2010": 80},
                                "range": {"2009": 8, "2010": 8},
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
                        "windows solar": {
                            "performance": {
                                "typical": {"2009": 9, "2010": 9},
                                "best": {"2009": 9, "2010": 9},
                                "units": "SHGC",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 9, "2010": 9},
                                "best": {"2009": 9, "2010": 9},
                                "units": "2014$/ft^2 floor",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 90, "2010": 90},
                                "range": {"2009": 9, "2010": 9},
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
                        "infiltration": {
                            "performance": {
                                "typical": {"2009": 2, "2010": 3},
                                "best": {"2009": 2, "2010": 3},
                                "units": "ACH50",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 2, "2010": 2},
                                "best": {"2009": 2, "2010": 2},
                                "units": "2014$/ft^2 floor",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 20, "2010": 20},
                                "range": {"2009": 2, "2010": 2},
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
                    "supply": {
                        "central AC": {
                            "performance": {
                                "typical": {"2009": 10, "2010": 10},
                                "best": {"2009": 10, "2010": 10},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 10, "2010": 10},
                                "best": {"2009": 10, "2010": 10},
                                "units": "2014$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 100, "2010": 100},
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
                        "room AC": {
                            "performance": {
                                "typical": {"2009": 11, "2010": 11},
                                "best": {"2009": 11, "2010": 11},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 11, "2010": 11},
                                "best": {"2009": 11, "2010": 11},
                                "units": "2014$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 110, "2010": 110},
                                "range": {"2009": 11, "2010": 11},
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
                        "ASHP": {
                            "performance": {
                                "typical": {"2009": 12, "2010": 12},
                                "best": {"2009": 12, "2010": 12},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {
                                    "new": {"2009": 24, "2010": 24},
                                    "existing": {"2009": 12, "2010": 12},
                                },
                                "best": {
                                    "new": {"2009": 24, "2010": 24},
                                    "existing": {"2009": 12, "2010": 12},
                                },
                                "units": "2014$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 120, "2010": 120},
                                "range": {"2009": 12, "2010": 12},
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
                        "GSHP": {
                            "performance": {
                                "typical": {"2009": 13, "2010": 13},
                                "best": {"2009": 13, "2010": 13},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {
                                    "new": {"2009": 26, "2010": 26},
                                    "existing": {"2009": 13, "2010": 13},
                                },
                                "best": {
                                    "new": {"2009": 26, "2010": 26},
                                    "existing": {"2009": 13, "2010": 13},
                                },
                                "units": "2014$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 130, "2010": 130},
                                "range": {"2009": 13, "2010": 13},
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
            }
        }
    },
}
