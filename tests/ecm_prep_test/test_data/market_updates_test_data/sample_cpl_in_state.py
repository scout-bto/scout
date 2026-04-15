#!/usr/bin/env python3

"""Extracted test data for Market Updates tests."""

sample_cpl_in_state = {
    "new england": {
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
                        }
                    }
                }
            }
        }
    }
}
