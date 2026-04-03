#!/usr/bin/env python3

"""Extracted test data for Update Measures tests."""

sample_mseg_in_emm = {
    "FRCC": {
        "assembly": {
            "total square footage": {"2009": 11, "2010": 11},
            "new square footage": {"2009": 0, "2010": 0},
            "electricity": {
                "heating": {
                    "demand": {
                        "wall": {"stock": "NA", "energy": {"2009": 0, "2010": 0}},
                        "roof": {"stock": "NA", "energy": {"2009": 1, "2010": 1}},
                        "lighting gain": {"stock": "NA", "energy": {"2009": -7, "2010": -7}},
                    }
                },
                "cooling": {
                    "demand": {
                        "wall": {"stock": "NA", "energy": {"2009": 5, "2010": 5}},
                        "roof": {"stock": "NA", "energy": {"2009": 6, "2010": 6}},
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
            "total square footage": {"2009": 11, "2010": 11},
            "total homes": {"2009": 1000, "2010": 1000},
            "new homes": {"2009": 0, "2010": 0},
            "electricity": {
                "heating": {
                    "demand": {
                        "wall": {"stock": "NA", "energy": {"2009": 0, "2010": 0}},
                        "roof": {"stock": "NA", "energy": {"2009": 1, "2010": 1}},
                    }
                },
                "cooling": {
                    "demand": {
                        "wall": {"stock": "NA", "energy": {"2009": 5, "2010": 5}},
                        "roof": {"stock": "NA", "energy": {"2009": 6, "2010": 6}},
                    }
                },
            },
        },
    },
    "ERCT": {
        "assembly": {
            "total square footage": {"2009": 11, "2010": 11},
            "new square footage": {"2009": 0, "2010": 0},
            "electricity": {
                "heating": {
                    "demand": {
                        "wall": {"stock": "NA", "energy": {"2009": 0, "2010": 0}},
                        "roof": {"stock": "NA", "energy": {"2009": 1, "2010": 1}},
                        "lighting gain": {"stock": "NA", "energy": {"2009": -7, "2010": -7}},
                    }
                },
                "cooling": {
                    "demand": {
                        "wall": {"stock": "NA", "energy": {"2009": 5, "2010": 5}},
                        "roof": {"stock": "NA", "energy": {"2009": 6, "2010": 6}},
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
            "total square footage": {"2009": 11, "2010": 11},
            "total homes": {"2009": 1000, "2010": 1000},
            "new homes": {"2009": 0, "2010": 0},
            "electricity": {
                "heating": {
                    "demand": {
                        "wall": {"stock": "NA", "energy": {"2009": 0, "2010": 0}},
                        "roof": {"stock": "NA", "energy": {"2009": 1, "2010": 1}},
                    }
                },
                "cooling": {
                    "demand": {
                        "wall": {"stock": "NA", "energy": {"2009": 5, "2010": 5}},
                        "roof": {"stock": "NA", "energy": {"2009": 6, "2010": 6}},
                    }
                },
            },
        },
    },
}
