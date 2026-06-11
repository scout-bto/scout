#!/usr/bin/env python3

"""Extracted test data for Market Updates tests."""

sample_mseg_in_emm = {
    "TRE": {
        "large office": {
            "total square footage": {"2009": 1000, "2010": 1000},
            "new square footage": {"2009": 100, "2010": 50},
            "electricity": {
                "cooling": {
                    "supply": {
                        "rooftop_AC": {
                            "stock": {"2009": 100, "2010": 100},
                            "energy": {"2009": 100, "2010": 100},
                        },
                        "rooftop_ASHP-cool": {
                            "stock": {"2009": 100, "2010": 100},
                            "energy": {"2009": 100, "2010": 100},
                        },
                    }
                },
                "heating": {
                    "supply": {
                        "electric_res-heat": {
                            "stock": {"2009": 100, "2010": 100},
                            "energy": {"2009": 100, "2010": 100},
                        },
                        "rooftop_ASHP-heat": {
                            "stock": {"2009": 100, "2010": 100},
                            "energy": {"2009": 100, "2010": 100},
                        },
                    }
                },
                "refrigeration": {
                    "Commercial Ice Machines": {
                        "stock": {"2009": 100, "2010": 100},
                        "energy": {"2009": 100, "2010": 100},
                    }
                },
            },
            "natural gas": {
                "heating": {
                    "supply": {
                        "gas_furnace": {
                            "stock": {"2009": 100, "2010": 100},
                            "energy": {"2009": 100, "2010": 100},
                        }
                    }
                },
            },
        },
        "single family home": {
            "total square footage": {"2009": 100, "2010": 200},
            "total homes": {"2009": 1000, "2010": 1000},
            "new homes": {"2009": 100, "2010": 50},
            "electricity": {
                "cooling": {
                    "supply": {
                        "ASHP": {"stock": {"2009": 9, "2010": 9}, "energy": {"2009": 9, "2010": 9}},
                        "central AC": {
                            "stock": {"2009": 100, "2010": 100},
                            "energy": {"2009": 100, "2010": 100},
                        },
                    }
                },
                "heating": {
                    "supply": {
                        "resistance heat": {
                            "stock": {"2009": 100, "2010": 100},
                            "energy": {"2009": 100, "2010": 100},
                        },
                        "ASHP": {"stock": {"2009": 9, "2010": 9}, "energy": {"2009": 9, "2010": 9}},
                    }
                },
                "water heating": {
                    "electric WH": {
                        "stock": {"2009": 100, "2010": 100},
                        "energy": {"2009": 100, "2010": 100},
                    }
                },
            },
            "natural gas": {
                "heating": {
                    "supply": {
                        "furnace (NG)": {
                            "stock": {"2009": 100, "2010": 100},
                            "energy": {"2009": 100, "2010": 100},
                        }
                    }
                },
                "water heating": {
                    "stock": {"2009": 100, "2010": 100},
                    "energy": {"2009": 100, "2010": 100},
                },
            },
        },
    },
    "CASO": {
        "single family home": {
            "total square footage": {"2009": 500, "2010": 600},
            "total homes": {"2009": 1000, "2010": 1000},
            "new homes": {"2009": 100, "2010": 50},
            "electricity": {
                "cooling": {
                    "supply": {
                        "ASHP": {"stock": {"2009": 9, "2010": 9}, "energy": {"2009": 9, "2010": 9}},
                        "central AC": {
                            "stock": {"2009": 100, "2010": 100},
                            "energy": {"2009": 100, "2010": 100},
                        },
                    }
                },
                "heating": {
                    "supply": {
                        "ASHP": {"stock": {"2009": 9, "2010": 9}, "energy": {"2009": 9, "2010": 9}},
                        "resistance heat": {
                            "stock": {"2009": 100, "2010": 100},
                            "energy": {"2009": 100, "2010": 100},
                        },
                    }
                },
            },
            "natural gas": {
                "heating": {
                    "supply": {
                        "furnace (NG)": {
                            "stock": {"2009": 100, "2010": 100},
                            "energy": {"2009": 100, "2010": 100},
                        }
                    }
                }
            },
        }
    },
}
