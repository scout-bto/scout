#!/usr/bin/env python3

"""Extracted test data for Market Updates tests."""

sample_mseg_in = {
    "AIA_CZ1": {
        "assembly": {
            "total square footage": {"2009": 11, "2010": 11},
            "new square footage": {"2009": 0, "2010": 0},
            "electricity": {
                "heating": {
                    "demand": {
                        "windows conduction": {"stock": "NA", "energy": {"2009": 0, "2010": 0}},
                        "windows solar": {"stock": "NA", "energy": {"2009": 1, "2010": 1}},
                        "lighting gain": {"stock": "NA", "energy": {"2009": -7, "2010": -7}},
                    }
                },
                "cooling": {
                    "demand": {
                        "windows conduction": {"stock": "NA", "energy": {"2009": 5, "2010": 5}},
                        "windows solar": {"stock": "NA", "energy": {"2009": 6, "2010": 6}},
                        "lighting gain": {"stock": "NA", "energy": {"2009": 6, "2010": 6}},
                    }
                },
                "lighting": {"T5 F28": {"stock": "NA", "energy": {"2009": 11, "2010": 11}}},
                "PCs": {"stock": "NA", "energy": {"2009": 12, "2010": 12}},
                "MELs": {
                    "distribution transformers": {"stock": "NA", "energy": {"2009": 24, "2010": 24}}
                },
            },
        },
        "single family home": {
            "total square footage": {"2009": 100, "2010": 200},
            "total homes": {"2009": 1000, "2010": 1000},
            "new homes": {"2009": 100, "2010": 50},
            "electricity": {
                "heating": {
                    "demand": {
                        "windows conduction": {"stock": "NA", "energy": {"2009": 0, "2010": 0}},
                        "windows solar": {"stock": "NA", "energy": {"2009": 1, "2010": 1}},
                        "infiltration": {"stock": "NA", "energy": {"2009": 10, "2010": 10}},
                    },
                    "supply": {
                        "resistance heat": {
                            "stock": {"2009": 2, "2010": 2},
                            "energy": {"2009": 2, "2010": 2},
                        },
                        "ASHP": {"stock": {"2009": 3, "2010": 3}, "energy": {"2009": 3, "2010": 3}},
                        "GSHP": {"stock": {"2009": 4, "2010": 4}, "energy": {"2009": 4, "2010": 4}},
                    },
                },
                "secondary heating": {
                    "demand": {
                        "windows conduction": {"stock": "NA", "energy": {"2009": 5, "2010": 5}},
                        "windows solar": {"stock": "NA", "energy": {"2009": 6, "2010": 6}},
                        "infiltration": {"stock": "NA", "energy": {"2009": 10, "2010": 10}},
                    },
                    "supply": {"secondary heater": 7},
                },
                "cooling": {
                    "demand": {
                        "windows conduction": {"stock": "NA", "energy": {"2009": 5, "2010": 5}},
                        "windows solar": {"stock": "NA", "energy": {"2009": 6, "2010": 6}},
                        "infiltration": {"stock": "NA", "energy": {"2009": 10, "2010": 10}},
                    },
                    "supply": {
                        "central AC": {
                            "stock": {"2009": 7, "2010": 7},
                            "energy": {"2009": 7, "2010": 7},
                        },
                        "room AC": {
                            "stock": {"2009": 8, "2010": 8},
                            "energy": {"2009": 8, "2010": 8},
                        },
                        "ASHP": {"stock": {"2009": 9, "2010": 9}, "energy": {"2009": 9, "2010": 9}},
                        "GSHP": {
                            "stock": {"2009": 10, "2010": 10},
                            "energy": {"2009": 10, "2010": 10},
                        },
                    },
                },
                "lighting": {
                    "linear fluorescent (LED)": {
                        "stock": {"2009": 11, "2010": 11},
                        "energy": {"2009": 11, "2010": 11},
                    },
                    "general service (LED)": {
                        "stock": {"2009": 12, "2010": 12},
                        "energy": {"2009": 12, "2010": 12},
                    },
                    "reflector (LED)": {
                        "stock": {"2009": 13, "2010": 13},
                        "energy": {"2009": 13, "2010": 13},
                    },
                    "external (LED)": {
                        "stock": {"2009": 14, "2010": 14},
                        "energy": {"2009": 14, "2010": 14},
                    },
                },
                "refrigeration": {
                    "stock": {"2009": 111, "2010": 111},
                    "energy": {"2009": 111, "2010": 111},
                },
                "TVs": {
                    "TVs": {"stock": {"2009": 99, "2010": 99}, "energy": {"2009": 9, "2010": 9}},
                    "set top box": {
                        "stock": {"2009": 99, "2010": 99},
                        "energy": {"2009": 999, "2010": 999},
                    },
                },
                "computers": {
                    "desktop PC": {
                        "stock": {"2009": 44, "2010": 44},
                        "energy": {"2009": 4, "2010": 4},
                    },
                    "laptop PC": {
                        "stock": {"2009": 55, "2010": 55},
                        "energy": {"2009": 5, "2010": 5},
                    },
                },
                "other": {
                    "freezers": {
                        "stock": {"2009": 222, "2010": 222},
                        "energy": {"2009": 222, "2010": 222},
                    },
                    "electric other": {
                        "stock": {"2009": 333, "2010": 333},
                        "energy": {"2009": 333, "2010": 333},
                    },
                },
            },
            "other fuel": {
                "heating": {
                    "supply": {
                        "stove (wood)": {
                            "stock": {"2009": 2, "2010": 2},
                            "energy": {"2009": 2, "2010": 2},
                        }
                    }
                }
            },
            "natural gas": {
                "water heating": {
                    "stock": {"2009": 15, "2010": 15},
                    "energy": {"2009": 15, "2010": 15},
                },
                "heating": {
                    "demand": {
                        "windows conduction": {"stock": "NA", "energy": {"2009": 0, "2010": 0}},
                        "windows solar": {"stock": "NA", "energy": {"2009": 1, "2010": 1}},
                        "infiltration": {"stock": "NA", "energy": {"2009": 10, "2010": 10}},
                    },
                    "supply": {
                        "furnace (NG)": {
                            "stock": {"2009": 100, "2010": 100},
                            "energy": {"2009": 100, "2010": 100},
                        }
                    },
                },
                "secondary heating": {
                    "demand": {
                        "windows conduction": {"stock": "NA", "energy": {"2009": 5, "2010": 5}},
                        "windows solar": {"stock": "NA", "energy": {"2009": 6, "2010": 6}},
                        "infiltration": {"stock": "NA", "energy": {"2009": 10, "2010": 10}},
                    }
                },
                "cooling": {
                    "demand": {
                        "windows conduction": {"stock": "NA", "energy": {"2009": 5, "2010": 5}},
                        "windows solar": {"stock": "NA", "energy": {"2009": 6, "2010": 6}},
                        "infiltration": {"stock": "NA", "energy": {"2009": 10, "2010": 10}},
                    }
                },
            },
        },
        "multi family home": {
            "total square footage": {"2009": 300, "2010": 400},
            "total homes": {"2009": 1000, "2010": 1000},
            "new homes": {"2009": 100, "2010": 50},
            "electricity": {
                "heating": {
                    "demand": {
                        "windows conduction": {"stock": "NA", "energy": {"2009": 0, "2010": 0}},
                        "windows solar": {"stock": "NA", "energy": {"2009": 1, "2010": 1}},
                    },
                    "supply": {
                        "resistance heat": {
                            "stock": {"2009": 2, "2010": 2},
                            "energy": {"2009": 2, "2010": 2},
                        },
                        "ASHP": {"stock": {"2009": 3, "2010": 3}, "energy": {"2009": 3, "2010": 3}},
                        "GSHP": {"stock": {"2009": 4, "2010": 4}, "energy": {"2009": 4, "2010": 4}},
                    },
                },
                "lighting": {
                    "linear fluorescent (LED)": {
                        "stock": {"2009": 11, "2010": 11},
                        "energy": {"2009": 11, "2010": 11},
                    },
                    "general service (LED)": {
                        "stock": {"2009": 12, "2010": 12},
                        "energy": {"2009": 12, "2010": 12},
                    },
                    "reflector (LED)": {
                        "stock": {"2009": 13, "2010": 13},
                        "energy": {"2009": 13, "2010": 13},
                    },
                    "external (LED)": {
                        "stock": {"2009": 14, "2010": 14},
                        "energy": {"2009": 14, "2010": 14},
                    },
                },
            },
        },
    },
    "AIA_CZ2": {
        "single family home": {
            "total square footage": {"2009": 500, "2010": 600},
            "total homes": {"2009": 1000, "2010": 1000},
            "new homes": {"2009": 100, "2010": 50},
            "electricity": {
                "heating": {
                    "demand": {
                        "windows conduction": {"stock": "NA", "energy": {"2009": 0, "2010": 0}},
                        "windows solar": {"stock": "NA", "energy": {"2009": 1, "2010": 1}},
                        "infiltration": {"stock": "NA", "energy": {"2009": 10, "2010": 10}},
                    },
                    "supply": {
                        "resistance heat": {
                            "stock": {"2009": 2, "2010": 2},
                            "energy": {"2009": 2, "2010": 2},
                        },
                        "ASHP": {"stock": {"2009": 3, "2010": 3}, "energy": {"2009": 3, "2010": 3}},
                        "GSHP": {"stock": {"2009": 4, "2010": 4}, "energy": {"2009": 4, "2010": 4}},
                    },
                },
                "secondary heating": {
                    "demand": {
                        "windows conduction": {"stock": "NA", "energy": {"2009": 5, "2010": 5}},
                        "windows solar": {"stock": "NA", "energy": {"2009": 6, "2010": 6}},
                        "infiltration": {"stock": "NA", "energy": {"2009": 10, "2010": 10}},
                    },
                    "supply": {"secondary heater": 7},
                },
                "cooling": {
                    "demand": {
                        "windows conduction": {"stock": "NA", "energy": {"2009": 5, "2010": 5}},
                        "windows solar": {"stock": "NA", "energy": {"2009": 6, "2010": 6}},
                        "infiltration": {"stock": "NA", "energy": {"2009": 10, "2010": 10}},
                    },
                    "supply": {
                        "central AC": {
                            "stock": {"2009": 7, "2010": 7},
                            "energy": {"2009": 7, "2010": 7},
                        },
                        "room AC": {
                            "stock": {"2009": 8, "2010": 8},
                            "energy": {"2009": 8, "2010": 8},
                        },
                        "ASHP": {"stock": {"2009": 9, "2010": 9}, "energy": {"2009": 9, "2010": 9}},
                        "GSHP": {
                            "stock": {"2009": 10, "2010": 10},
                            "energy": {"2009": 10, "2010": 10},
                        },
                    },
                },
                "lighting": {
                    "linear fluorescent (LED)": {
                        "stock": {"2009": 11, "2010": 11},
                        "energy": {"2009": 11, "2010": 11},
                    },
                    "general service (LED)": {
                        "stock": {"2009": 12, "2010": 12},
                        "energy": {"2009": 12, "2010": 12},
                    },
                    "reflector (LED)": {
                        "stock": {"2009": 13, "2010": 13},
                        "energy": {"2009": 13, "2010": 13},
                    },
                    "external (LED)": {
                        "stock": {"2009": 14, "2010": 14},
                        "energy": {"2009": 14, "2010": 14},
                    },
                },
                "TVs": {
                    "TVs": {"stock": {"2009": 99, "2010": 99}, "energy": {"2009": 9, "2010": 9}},
                    "set top box": {
                        "stock": {"2009": 99, "2010": 99},
                        "energy": {"2009": 999, "2010": 999},
                    },
                },
                "computers": {
                    "desktop PC": {
                        "stock": {"2009": 44, "2010": 44},
                        "energy": {"2009": 4, "2010": 4},
                    },
                    "laptop PC": {
                        "stock": {"2009": 55, "2010": 55},
                        "energy": {"2009": 5, "2010": 5},
                    },
                },
            },
            "natural gas": {
                "water heating": {
                    "stock": {"2009": 15, "2010": 15},
                    "energy": {"2009": 15, "2010": 15},
                }
            },
        },
        "multi family home": {
            "total square footage": {"2009": 700, "2010": 800},
            "total homes": {"2009": 1000, "2010": 1000},
            "new homes": {"2009": 100, "2010": 50},
            "electricity": {
                "heating": {
                    "demand": {
                        "windows conduction": {"stock": "NA", "energy": {"2009": 0, "2010": 0}},
                        "windows solar": {"stock": "NA", "energy": {"2009": 1, "2010": 1}},
                    },
                    "supply": {
                        "resistance heat": {
                            "stock": {"2009": 2, "2010": 2},
                            "energy": {"2009": 2, "2010": 2},
                        },
                        "ASHP": {"stock": {"2009": 3, "2010": 3}, "energy": {"2009": 3, "2010": 3}},
                        "GSHP": {"stock": {"2009": 4, "2010": 4}},
                    },
                },
                "lighting": {
                    "linear fluorescent (LED)": {
                        "stock": {"2009": 11, "2010": 11},
                        "energy": {"2009": 11, "2010": 11},
                    },
                    "general service (LED)": {
                        "stock": {"2009": 12, "2010": 12},
                        "energy": {"2009": 12, "2010": 12},
                    },
                    "reflector (LED)": {
                        "stock": {"2009": 13, "2010": 13},
                        "energy": {"2009": 13, "2010": 13},
                    },
                    "external (LED)": {
                        "stock": {"2009": 14, "2010": 14},
                        "energy": {"2009": 14, "2010": 14},
                    },
                },
            },
        },
    },
    "AIA_CZ4": {
        "multi family home": {
            "total square footage": {"2009": 900, "2010": 1000},
            "total homes": {"2009": 1000, "2010": 1000},
            "new homes": {"2009": 100, "2010": 50},
            "electricity": {
                "lighting": {
                    "linear fluorescent (LED)": {
                        "stock": {"2009": 11, "2010": 11},
                        "energy": {"2009": 11, "2010": 11},
                    },
                    "general service (LED)": {
                        "stock": {"2009": 12, "2010": 12},
                        "energy": {"2009": 12, "2010": 12},
                    },
                    "reflector (LED)": {
                        "stock": {"2009": 13, "2010": 13},
                        "energy": {"2009": 13, "2010": 13},
                    },
                    "external (LED)": {
                        "stock": {"2009": 14, "2010": 14},
                        "energy": {"2009": 14, "2010": 14},
                    },
                }
            },
        }
    },
}
