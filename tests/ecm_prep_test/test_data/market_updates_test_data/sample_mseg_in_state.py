#!/usr/bin/env python3

"""Extracted test data for Market Updates tests."""

sample_mseg_in_state = {
    "CT": {
        "single family home": {
            "total square footage": {"2009": 100, "2010": 200},
            "total homes": {"2009": 1000, "2010": 1000},
            "new homes": {"2009": 100, "2010": 50},
            "electricity": {
                "cooling": {
                    "supply": {
                        "ASHP": {"stock": {"2009": 9, "2010": 9}, "energy": {"2009": 9, "2010": 9}}
                    }
                }
            },
        }
    },
    "NH": {
        "single family home": {
            "total square footage": {"2009": 500, "2010": 600},
            "total homes": {"2009": 1000, "2010": 1000},
            "new homes": {"2009": 100, "2010": 50},
            "electricity": {
                "cooling": {
                    "supply": {
                        "ASHP": {"stock": {"2009": 9, "2010": 9}, "energy": {"2009": 9, "2010": 9}}
                    }
                }
            },
        }
    },
}
