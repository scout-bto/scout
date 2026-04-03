#!/usr/bin/env python3

"""Extracted test data for Update Measures tests."""

sample_cpl_in_emm = {
    "FRCC": {
        "assembly": {
            "electricity": {
                "heating": {
                    "demand": {
                        "wall": {
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
                        "roof": {
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
                        "wall": {
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
                        "roof": {
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
                        "wall": {
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
                        "roof": {
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
                    }
                },
                "cooling": {
                    "demand": {
                        "wall": {
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
                        "roof": {
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
                    }
                },
            }
        },
    },
    "ERCT": {
        "assembly": {
            "electricity": {
                "heating": {
                    "demand": {
                        "wall": {
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
                        "roof": {
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
                        "wall": {
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
                        "roof": {
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
                        "wall": {
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
                        "roof": {
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
                    }
                },
                "cooling": {
                    "demand": {
                        "wall": {
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
                        "roof": {
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
                    }
                },
            }
        },
    },
}
