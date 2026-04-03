#!/usr/bin/env python3

"""Refrigerant heat pump rates test data for market updates tests."""

frefr_hp_rates = {
    "data (by scenario)": {
        "gh-aggressive": {
            "south": {
                "residential": {
                    "electricity": {
                        "heating": {
                            "resistance heat": {
                                "existing": {"2009": 1, "2010": 1},
                                "new": {"2009": 1, "2010": 1},
                            }
                        },
                        "water heating": {
                            "all": {
                                "existing": {"2009": 1, "2010": 1},
                                "new": {"2009": 1, "2010": 1},
                            }
                        },
                    },
                    "natural gas": {
                        "heating": {
                            "furnace (NG)": {
                                "existing": {"2009": 1, "2010": 1},
                                "new": {"2009": 1, "2010": 1},
                            }
                        },
                        "water heating": {
                            "all": {
                                "existing": {"2009": 1, "2010": 1},
                                "new": {"2009": 1, "2010": 1},
                            }
                        },
                    },
                },
                "commercial": {
                    "electricity": {
                        "heating": {
                            "RTUs": {
                                "existing": {"2009": 1, "2010": 1},
                                "new": {"2009": 1, "2010": 1},
                            }
                        }
                    },
                    "natural gas": {
                        "heating": {
                            "RTUs": {
                                "existing": {"2009": 1, "2010": 1},
                                "new": {"2009": 1, "2010": 1},
                            }
                        }
                    },
                },
            }
        }
    }
}
