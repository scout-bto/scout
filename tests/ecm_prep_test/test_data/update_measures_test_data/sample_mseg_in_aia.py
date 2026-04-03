#!/usr/bin/env python3

"""Extracted test data for Update Measures tests."""

sample_mseg_in_aia = {
    "AIA_CZ1": {
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
            },
            "natural gas": {
                "water heating": {
                    "stock": {"2009": 15, "2010": 15},
                    "energy": {"2009": 15, "2010": 15},
                }
            },
        }
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
            },
        }
    },
}
