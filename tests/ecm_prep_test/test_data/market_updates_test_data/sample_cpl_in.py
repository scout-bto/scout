#!/usr/bin/env python3

"""Extracted test data for Market Updates tests."""

sample_cpl_in = {
    "AIA_CZ1": {
        "assembly": {
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
                        "lighting gain": 0,
                    }
                },
                "cooling": {
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
                        "lighting gain": 0,
                    }
                },
                "lighting": {
                    "T5 F28": {
                        "performance": {
                            "typical": {"2009": 14, "2010": 14},
                            "best": {"2009": 14, "2010": 14},
                            "units": "lm/W",
                            "source": "EIA AEO",
                        },
                        "installed cost": {
                            "typical": {"2009": 14, "2010": 14},
                            "best": {"2009": 14, "2010": 14},
                            "units": "2014$/ft^2 floor",
                            "source": "EIA AEO",
                        },
                        "lifetime": {
                            "average": {"2009": 140, "2010": 140},
                            "range": {"2009": 14, "2010": 14},
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
                "PCs": 0,
                "MELs": {"distribution transformers": 0},
            }
        },
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
                                "typical": {"2009": 4 / 0.2930712, "2010": 4 / 0.2930712},
                                "best": {"2009": 4, "2010": 4},
                                "units": "EER",
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
                "secondary heating": {
                    "demand": {
                        "windows conduction": {
                            "performance": {
                                "typical": {"2009": 5, "2010": 5},
                                "best": {"2009": 5, "2010": 5},
                                "units": "R Value",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 5, "2010": 5},
                                "best": {"2009": 5, "2010": 5},
                                "units": "2014$/ft^2 floor",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 50, "2010": 50},
                                "range": {"2009": 5, "2010": 5},
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
                                "typical": {"2009": 6, "2010": 6},
                                "best": {"2009": 6, "2010": 6},
                                "units": "SHGC",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 6, "2010": 6},
                                "best": {"2009": 6, "2010": 6},
                                "units": "2014$/ft^2 floor",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 60, "2010": 60},
                                "range": {"2009": 6, "2010": 6},
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
                        "secondary heater": {
                            "performance": {
                                "typical": {"2009": 7, "2010": 7},
                                "best": {"2009": 7, "2010": 7},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 7, "2010": 7},
                                "best": {"2009": 7, "2010": 7},
                                "units": "2014$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 70, "2010": 70},
                                "range": {"2009": 7, "2010": 7},
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
                "lighting": {
                    "linear fluorescent (LED)": {
                        "performance": {
                            "typical": {"2009": 14, "2010": 14},
                            "best": {"2009": 14, "2010": 14},
                            "units": "lm/W",
                            "source": "EIA AEO",
                        },
                        "installed cost": {
                            "typical": {"2009": 14, "2010": 14},
                            "best": {"2009": 14, "2010": 14},
                            "units": "2014$/unit",
                            "source": "EIA AEO",
                        },
                        "lifetime": {
                            "average": {"2009": 140 * (3 / 24), "2010": 140 * (3 / 24)},
                            "range": {"2009": 14, "2010": 14},
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
                    "general service (LED)": {
                        "performance": {
                            "typical": {"2009": 15, "2010": 15},
                            "best": {"2009": 15, "2010": 15},
                            "units": "lm/W",
                            "source": "EIA AEO",
                        },
                        "installed cost": {
                            "typical": {"2009": 15, "2010": 15},
                            "best": {"2009": 15, "2010": 15},
                            "units": "2014$/unit",
                            "source": "EIA AEO",
                        },
                        "lifetime": {
                            "average": {"2009": 150 * (3 / 24), "2010": 150 * (3 / 24)},
                            "range": {"2009": 15, "2010": 15},
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
                    "reflector (LED)": {
                        "performance": {
                            "typical": {"2009": 16, "2010": 16},
                            "best": {"2009": 16, "2010": 16},
                            "units": "lm/W",
                            "source": "EIA AEO",
                        },
                        "installed cost": {
                            "typical": {"2009": 16, "2010": 16},
                            "best": {"2009": 16, "2010": 16},
                            "units": "2014$/unit",
                            "source": "EIA AEO",
                        },
                        "lifetime": {
                            "average": {"2009": 160 * (3 / 24), "2010": 160 * (3 / 24)},
                            "range": {"2009": 16, "2010": 16},
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
                    "external (LED)": {
                        "performance": {
                            "typical": {"2009": 17, "2010": 17},
                            "best": {"2009": 17, "2010": 17},
                            "units": "lm/W",
                            "source": "EIA AEO",
                        },
                        "installed cost": {
                            "typical": {"2009": 17, "2010": 17},
                            "best": {"2009": 17, "2010": 17},
                            "units": "2014$/unit",
                            "source": "EIA AEO",
                        },
                        "lifetime": {
                            "average": {"2009": 170 * (3 / 24), "2010": 170 * (3 / 24)},
                            "range": {"2009": 17, "2010": 17},
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
                "refrigeration": {
                    "performance": {
                        "typical": {"2009": 550, "2010": 550},
                        "best": {"2009": 450, "2010": 450},
                        "units": "kWh/yr",
                        "source": "EIA AEO",
                    },
                    "installed cost": {
                        "typical": {"2009": 300, "2010": 300},
                        "best": {"2009": 600, "2010": 600},
                        "units": "2010$/unit",
                        "source": "EIA AEO",
                    },
                    "lifetime": {
                        "average": {"2009": 17, "2010": 17},
                        "range": {"2009": 6, "2010": 6},
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
                "TVs": {
                    "TVs": {
                        "performance": {
                            "typical": {"2009": "NA", "2010": "NA"},
                            "best": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
                        },
                        "installed cost": {
                            "typical": {"2009": "NA", "2010": "NA"},
                            "best": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
                        },
                        "lifetime": {
                            "average": {"2009": "NA", "2010": "NA"},
                            "range": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
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
                    "set top box": {
                        "performance": {
                            "typical": {"2009": "NA", "2010": "NA"},
                            "best": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
                        },
                        "installed cost": {
                            "typical": {"2009": "NA", "2010": "NA"},
                            "best": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
                        },
                        "lifetime": {
                            "average": {"2009": "NA", "2010": "NA"},
                            "range": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
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
                "computers": {
                    "desktop PC": {
                        "performance": {
                            "typical": {"2009": "NA", "2010": "NA"},
                            "best": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
                        },
                        "installed cost": {
                            "typical": {"2009": "NA", "2010": "NA"},
                            "best": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
                        },
                        "lifetime": {
                            "average": {"2009": "NA", "2010": "NA"},
                            "range": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
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
                    "laptop PC": {
                        "performance": {
                            "typical": {"2009": "NA", "2010": "NA"},
                            "best": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
                        },
                        "installed cost": {
                            "typical": {"2009": "NA", "2010": "NA"},
                            "best": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
                        },
                        "lifetime": {
                            "average": {"2009": "NA", "2010": "NA"},
                            "range": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
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
                "other": {
                    "freezers": {
                        "performance": {
                            "typical": {"2009": 550, "2010": 550},
                            "best": {"2009": 450, "2010": 450},
                            "units": "kWh/yr",
                            "source": "EIA AEO",
                        },
                        "installed cost": {
                            "typical": {"2009": 100, "2010": 100},
                            "best": {"2009": 200, "2010": 200},
                            "units": "2014$/unit",
                            "source": "EIA AEO",
                        },
                        "lifetime": {
                            "average": {"2009": 15, "2010": 15},
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
                    "electric other": {
                        "performance": {
                            "typical": {"2009": "NA", "2010": "NA"},
                            "best": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
                        },
                        "installed cost": {
                            "typical": {"2009": "NA", "2010": "NA"},
                            "best": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
                        },
                        "lifetime": {
                            "average": {"2009": "NA", "2010": "NA"},
                            "range": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
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
            "other fuel": {
                "heating": {
                    "supply": {
                        "stove (wood)": {
                            "performance": {
                                "typical": {"2009": 2, "2010": 2},
                                "best": {"2009": 2, "2010": 2},
                                "units": "HHV",
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
                        }
                    }
                }
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
                        "typical": {"2009": 18, "2010": 18},
                        "best": {"2009": 18, "2010": 18},
                        "units": "2014$/unit",
                        "source": "EIA AEO",
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
                },
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
                        "furnace (NG)": {
                            "performance": {
                                "typical": {"2009": 0.8, "2010": 0.8},
                                "best": {"2009": 0.9, "2010": 0.9},
                                "units": "AFUE",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 1000, "2010": 1000},
                                "best": {"2009": 1000, "2010": 1000},
                                "units": "$/unit",
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
                                "competed market": {},
                            },
                        }
                    },
                },
                "secondary heating": {
                    "demand": {
                        "windows conduction": {
                            "performance": {
                                "typical": {"2009": 5, "2010": 5},
                                "best": {"2009": 5, "2010": 5},
                                "units": "R Value",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 5, "2010": 5},
                                "best": {"2009": 5, "2010": 5},
                                "units": "2014$/ft^2 floor",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 50, "2010": 50},
                                "range": {"2009": 5, "2010": 5},
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
                                "typical": {"2009": 6, "2010": 6},
                                "best": {"2009": 6, "2010": 6},
                                "units": "SHGC",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 6, "2010": 6},
                                "best": {"2009": 6, "2010": 6},
                                "units": "2014$/ft^2 floor",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 60, "2010": 60},
                                "range": {"2009": 6, "2010": 6},
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
                    }
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
                    }
                },
            },
        },
        "multi family home": {
            "electricity": {
                "heating": {
                    "demand": {
                        "windows conduction": {
                            "performance": {
                                "typical": {"2009": 19, "2010": 19},
                                "best": {"2009": 19, "2010": 19},
                                "units": "R Value",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 19, "2010": 19},
                                "best": {"2009": 19, "2010": 19},
                                "units": "2014$/ft^2 floor",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 190, "2010": 190},
                                "range": {"2009": 19, "2010": 19},
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
                                "typical": {"2009": 20, "2010": 20},
                                "best": {"2009": 20, "2010": 20},
                                "units": "SHGC",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 20, "2010": 20},
                                "best": {"2009": 20, "2010": 20},
                                "units": "2014$/ft^2 floor",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 200, "2010": 200},
                                "range": {"2009": 20, "2010": 20},
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
                                "typical": {"2009": 21, "2010": 21},
                                "best": {"2009": 21, "2010": 21},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 21, "2010": 21},
                                "best": {"2009": 21, "2010": 21},
                                "units": "2014$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 210, "2010": 210},
                                "range": {"2009": 21, "2010": 21},
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
                                "typical": {"2009": 22, "2010": 22},
                                "best": {"2009": 22, "2010": 22},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {
                                    "new": {"2009": 44, "2010": 44},
                                    "existing": {"2009": 22, "2010": 22},
                                },
                                "best": {
                                    "new": {"2009": 44, "2010": 44},
                                    "existing": {"2009": 22, "2010": 22},
                                },
                                "units": "2014$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 220, "2010": 220},
                                "range": {"2009": 22, "2010": 22},
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
                                "typical": {"2009": 23, "2010": 23},
                                "best": {"2009": 23, "2010": 23},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {
                                    "new": {"2009": 46, "2010": 46},
                                    "existing": {"2009": 23, "2010": 23},
                                },
                                "best": {
                                    "new": {"2009": 46, "2010": 46},
                                    "existing": {"2009": 23, "2010": 23},
                                },
                                "units": "2014$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 230, "2010": 230},
                                "range": {"2009": 23, "2010": 23},
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
                "lighting": {
                    "linear fluorescent (LED)": {
                        "performance": {
                            "typical": {"2009": 24, "2010": 24},
                            "best": {"2009": 24, "2010": 24},
                            "units": "lm/W",
                            "source": "EIA AEO",
                        },
                        "installed cost": {
                            "typical": {"2009": 24, "2010": 24},
                            "best": {"2009": 24, "2010": 24},
                            "units": "2014$/unit",
                            "source": "EIA AEO",
                        },
                        "lifetime": {
                            "average": {"2009": 240 * (3 / 24), "2010": 240 * (3 / 24)},
                            "range": {"2009": 24, "2010": 24},
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
                    "general service (LED)": {
                        "performance": {
                            "typical": {"2009": 25, "2010": 25},
                            "best": {"2009": 25, "2010": 25},
                            "units": "lm/W",
                            "source": "EIA AEO",
                        },
                        "installed cost": {
                            "typical": {"2009": 25, "2010": 25},
                            "best": {"2009": 25, "2010": 25},
                            "units": "2014$/unit",
                            "source": "EIA AEO",
                        },
                        "lifetime": {
                            "average": {"2009": 250 * (3 / 24), "2010": 250 * (3 / 24)},
                            "range": {"2009": 25, "2010": 25},
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
                    "reflector (LED)": {
                        "performance": {
                            "typical": {"2009": 25, "2010": 25},
                            "best": {"2009": 25, "2010": 25},
                            "units": "lm/W",
                            "source": "EIA AEO",
                        },
                        "installed cost": {
                            "typical": {"2009": 25, "2010": 25},
                            "best": {"2009": 25, "2010": 25},
                            "units": "2014$/unit",
                            "source": "EIA AEO",
                        },
                        "lifetime": {
                            "average": {"2009": 250 * (3 / 24), "2010": 250 * (3 / 24)},
                            "range": {"2009": 25, "2010": 25},
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
                    "external (LED)": {
                        "performance": {
                            "typical": {"2009": 25, "2010": 25},
                            "best": {"2009": 25, "2010": 25},
                            "units": "lm/W",
                            "source": "EIA AEO",
                        },
                        "installed cost": {
                            "typical": {"2009": 25, "2010": 25},
                            "best": {"2009": 25, "2010": 25},
                            "units": "2014$/unit",
                            "source": "EIA AEO",
                        },
                        "lifetime": {
                            "average": {"2009": 250 * (3 / 24), "2010": 250 * (3 / 24)},
                            "range": {"2009": 25, "2010": 25},
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
            }
        },
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
                "secondary heating": {
                    "demand": {
                        "windows conduction": {
                            "performance": {
                                "typical": {"2009": 5, "2010": 5},
                                "best": {"2009": 5, "2010": 5},
                                "units": "R Value",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 5, "2010": 5},
                                "best": {"2009": 5, "2010": 5},
                                "units": "2014$/ft^2 floor",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 50, "2010": 50},
                                "range": {"2009": 5, "2010": 5},
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
                                "typical": {"2009": 6, "2010": 6},
                                "best": {"2009": 6, "2010": 6},
                                "units": "SHGC",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 6, "2010": 6},
                                "best": {"2009": 6, "2010": 6},
                                "units": "2014$/ft^2 floor",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 60, "2010": 60},
                                "range": {"2009": 6, "2010": 6},
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
                        "secondary heater": {
                            "performance": {
                                "typical": {"2009": 7, "2010": 7},
                                "best": {"2009": 7, "2010": 7},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 7, "2010": 7},
                                "best": {"2009": 7, "2010": 7},
                                "units": "2014$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 70, "2010": 70},
                                "range": {"2009": 7, "2010": 7},
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
                "lighting": {
                    "linear fluorescent (LED)": {
                        "performance": {
                            "typical": {"2009": 14, "2010": 14},
                            "best": {"2009": 14, "2010": 14},
                            "units": "lm/W",
                            "source": "EIA AEO",
                        },
                        "installed cost": {
                            "typical": {"2009": 14, "2010": 14},
                            "best": {"2009": 14, "2010": 14},
                            "units": "2014$/unit",
                            "source": "EIA AEO",
                        },
                        "lifetime": {
                            "average": {"2009": 140 * (3 / 24), "2010": 140 * (3 / 24)},
                            "range": {"2009": 14, "2010": 14},
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
                    "general service (LED)": {
                        "performance": {
                            "typical": {"2009": 15, "2010": 15},
                            "best": {"2009": 15, "2010": 15},
                            "units": "lm/W",
                            "source": "EIA AEO",
                        },
                        "installed cost": {
                            "typical": {"2009": 15, "2010": 15},
                            "best": {"2009": 15, "2010": 15},
                            "units": "2014$/unit",
                            "source": "EIA AEO",
                        },
                        "lifetime": {
                            "average": {"2009": 150 * (3 / 24), "2010": 150 * (3 / 24)},
                            "range": {"2009": 15, "2010": 15},
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
                    "reflector (LED)": {
                        "performance": {
                            "typical": {"2009": 16, "2010": 16},
                            "best": {"2009": 16, "2010": 16},
                            "units": "lm/W",
                            "source": "EIA AEO",
                        },
                        "installed cost": {
                            "typical": {"2009": 16, "2010": 16},
                            "best": {"2009": 16, "2010": 16},
                            "units": "2014$/unit",
                            "source": "EIA AEO",
                        },
                        "lifetime": {
                            "average": {"2009": 160 * (3 / 24), "2010": 160 * (3 / 24)},
                            "range": {"2009": 16, "2010": 16},
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
                    "external (LED)": {
                        "performance": {
                            "typical": {"2009": 17, "2010": 17},
                            "best": {"2009": 17, "2010": 17},
                            "units": "lm/W",
                            "source": "EIA AEO",
                        },
                        "installed cost": {
                            "typical": {"2009": 17, "2010": 17},
                            "best": {"2009": 17, "2010": 17},
                            "units": "2014$/unit",
                            "source": "EIA AEO",
                        },
                        "lifetime": {
                            "average": {"2009": 170 * (3 / 24), "2010": 170 * (3 / 24)},
                            "range": {"2009": 17, "2010": 17},
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
                "TVs": {
                    "TVs": {
                        "performance": {
                            "typical": {"2009": "NA", "2010": "NA"},
                            "best": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
                        },
                        "installed cost": {
                            "typical": {"2009": "NA", "2010": "NA"},
                            "best": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
                        },
                        "lifetime": {
                            "average": {"2009": "NA", "2010": "NA"},
                            "range": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
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
                    "set top box": {
                        "performance": {
                            "typical": {"2009": "NA", "2010": "NA"},
                            "best": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
                        },
                        "installed cost": {
                            "typical": {"2009": "NA", "2010": "NA"},
                            "best": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
                        },
                        "lifetime": {
                            "average": {"2009": "NA", "2010": "NA"},
                            "range": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
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
                "computers": {
                    "desktop PC": {
                        "performance": {
                            "typical": {"2009": "NA", "2010": "NA"},
                            "best": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
                        },
                        "installed cost": {
                            "typical": {"2009": "NA", "2010": "NA"},
                            "best": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
                        },
                        "lifetime": {
                            "average": {"2009": "NA", "2010": "NA"},
                            "range": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
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
                    "laptop PC": {
                        "performance": {
                            "typical": {"2009": "NA", "2010": "NA"},
                            "best": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
                        },
                        "installed cost": {
                            "typical": {"2009": "NA", "2010": "NA"},
                            "best": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
                        },
                        "lifetime": {
                            "average": {"2009": "NA", "2010": "NA"},
                            "range": {"2009": "NA", "2010": "NA"},
                            "units": "NA",
                            "source": "NA",
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
            "natural gas": {
                "water heating": {
                    "performance": {
                        "typical": {"2009": 18, "2010": 18},
                        "best": {"2009": 18, "2010": 18},
                        "units": "EF",
                        "source": "EIA AEO",
                    },
                    "installed cost": {
                        "typical": {"2009": 18, "2010": 18},
                        "best": {"2009": 18, "2010": 18},
                        "units": "2014$/unit",
                        "source": "EIA AEO",
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
        },
        "multi family home": {
            "electricity": {
                "heating": {
                    "demand": {
                        "windows conduction": {
                            "performance": {
                                "typical": {"2009": 19, "2010": 19},
                                "best": {"2009": 19, "2010": 19},
                                "units": "R Value",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 19, "2010": 19},
                                "best": {"2009": 19, "2010": 19},
                                "units": "2014$/ft^2 floor",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 190, "2010": 190},
                                "range": {"2009": 19, "2010": 19},
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
                                "typical": {"2009": 20, "2010": 20},
                                "best": {"2009": 20, "2010": 20},
                                "units": "SHGC",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 20, "2010": 20},
                                "best": {"2009": 20, "2010": 20},
                                "units": "2014$/ft^2 floor",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 200, "2010": 200},
                                "range": {"2009": 20, "2010": 20},
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
                                "typical": {"2009": 21, "2010": 21},
                                "best": {"2009": 21, "2010": 21},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {"2009": 21, "2010": 21},
                                "best": {"2009": 21, "2010": 21},
                                "units": "2014$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 210, "2010": 210},
                                "range": {"2009": 21, "2010": 21},
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
                                "typical": {"2009": 22, "2010": 22},
                                "best": {"2009": 22, "2010": 22},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {
                                    "new": {"2009": 44, "2010": 44},
                                    "existing": {"2009": 22, "2010": 22},
                                },
                                "best": {
                                    "new": {"2009": 44, "2010": 44},
                                    "existing": {"2009": 22, "2010": 22},
                                },
                                "units": "2014$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 220, "2010": 220},
                                "range": {"2009": 22, "2010": 22},
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
                                "typical": {"2009": 23, "2010": 23},
                                "best": {"2009": 23, "2010": 23},
                                "units": "COP",
                                "source": "EIA AEO",
                            },
                            "installed cost": {
                                "typical": {
                                    "new": {"2009": 46, "2010": 46},
                                    "existing": {"2009": 23, "2010": 23},
                                },
                                "best": {
                                    "new": {"2009": 46, "2010": 46},
                                    "existing": {"2009": 23, "2010": 23},
                                },
                                "units": "2014$/unit",
                                "source": "EIA AEO",
                            },
                            "lifetime": {
                                "average": {"2009": 230, "2010": 230},
                                "range": {"2009": 23, "2010": 23},
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
                "lighting": {
                    "linear fluorescent (LED)": {
                        "performance": {
                            "typical": {"2009": 24, "2010": 24},
                            "best": {"2009": 24, "2010": 24},
                            "units": "lm/W",
                            "source": "EIA AEO",
                        },
                        "installed cost": {
                            "typical": {"2009": 24, "2010": 24},
                            "best": {"2009": 24, "2010": 24},
                            "units": "2014$/unit",
                            "source": "EIA AEO",
                        },
                        "lifetime": {
                            "average": {"2009": 240 * (3 / 24), "2010": 240 * (3 / 24)},
                            "range": {"2009": 24, "2010": 24},
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
                    "general service (LED)": {
                        "performance": {
                            "typical": {"2009": 25, "2010": 25},
                            "best": {"2009": 25, "2010": 25},
                            "units": "lm/W",
                            "source": "EIA AEO",
                        },
                        "installed cost": {
                            "typical": {"2009": 25, "2010": 25},
                            "best": {"2009": 25, "2010": 25},
                            "units": "2014$/unit",
                            "source": "EIA AEO",
                        },
                        "lifetime": {
                            "average": {"2009": 250 * (3 / 24), "2010": 250 * (3 / 24)},
                            "range": {"2009": 25, "2010": 25},
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
                    "reflector (LED)": {
                        "performance": {
                            "typical": {"2009": 25, "2010": 25},
                            "best": {"2009": 25, "2010": 25},
                            "units": "lm/W",
                            "source": "EIA AEO",
                        },
                        "installed cost": {
                            "typical": {"2009": 25, "2010": 25},
                            "best": {"2009": 25, "2010": 25},
                            "units": "2014$/unit",
                            "source": "EIA AEO",
                        },
                        "lifetime": {
                            "average": {"2009": 250 * (3 / 24), "2010": 250 * (3 / 24)},
                            "range": {"2009": 25, "2010": 25},
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
                    "external (LED)": {
                        "performance": {
                            "typical": {"2009": 25, "2010": 25},
                            "best": {"2009": 25, "2010": 25},
                            "units": "lm/W",
                            "source": "EIA AEO",
                        },
                        "installed cost": {
                            "typical": {"2009": 25, "2010": 25},
                            "best": {"2009": 25, "2010": 25},
                            "units": "2014$/unit",
                            "source": "EIA AEO",
                        },
                        "lifetime": {
                            "average": {"2009": 250 * (3 / 24), "2010": 250 * (3 / 24)},
                            "range": {"2009": 25, "2010": 25},
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
            }
        },
    },
    "AIA_CZ4": {
        "multi family home": {
            "electricity": {
                "lighting": {
                    "linear fluorescent (LED)": {
                        "performance": {
                            "typical": {"2009": 24, "2010": 24},
                            "best": {"2009": 24, "2010": 24},
                            "units": "lm/W",
                            "source": "EIA AEO",
                        },
                        "installed cost": {
                            "typical": {"2009": 24, "2010": 24},
                            "best": {"2009": 24, "2010": 24},
                            "units": "2014$/unit",
                            "source": "EIA AEO",
                        },
                        "lifetime": {
                            "average": {"2009": 240, "2010": 240},
                            "range": {"2009": 24, "2010": 24},
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
                    "general service (LED)": {
                        "performance": {
                            "typical": {"2009": 25, "2010": 25},
                            "best": {"2009": 25, "2010": 25},
                            "units": "lm/W",
                            "source": "EIA AEO",
                        },
                        "installed cost": {
                            "typical": {"2009": 25, "2010": 25},
                            "best": {"2009": 25, "2010": 25},
                            "units": "2014$/unit",
                            "source": "EIA AEO",
                        },
                        "lifetime": {
                            "average": {"2009": 250, "2010": 250},
                            "range": {"2009": 25, "2010": 25},
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
                    "reflector (LED)": {
                        "performance": {
                            "typical": {"2009": 26, "2010": 26},
                            "best": {"2009": 26, "2010": 26},
                            "units": "lm/W",
                            "source": "EIA AEO",
                        },
                        "installed cost": {
                            "typical": {"2009": 26, "2010": 26},
                            "best": {"2009": 26, "2010": 26},
                            "units": "2014$/unit",
                            "source": "EIA AEO",
                        },
                        "lifetime": {
                            "average": {"2009": 260, "2010": 260},
                            "range": {"2009": 26, "2010": 26},
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
                    "external (LED)": {
                        "performance": {
                            "typical": {"2009": 27, "2010": 27},
                            "best": {"2009": 27, "2010": 27},
                            "units": "lm/W",
                            "source": "EIA AEO",
                        },
                        "installed cost": {
                            "typical": {"2009": 27, "2010": 27},
                            "best": {"2009": 27, "2010": 27},
                            "units": "2014$/unit",
                            "source": "EIA AEO",
                        },
                        "lifetime": {
                            "average": {"2009": 270, "2010": 270},
                            "range": {"2009": 27, "2010": 27},
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
            }
        }
    },
}
