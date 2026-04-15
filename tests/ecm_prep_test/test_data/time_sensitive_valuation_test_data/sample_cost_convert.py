#!/usr/bin/env python3

"""
Test data for Time-Sensitive Valuation (TSV) tests.

Extracted from test_time_sensitive_valuation_test.py.
"""

sample_cost_convert = {
    "building type conversions": {
        "original type": "EnergyPlus reference buildings",
        "revised type": "Annual Energy Outlook (AEO) buildings",
        "conversion data": {
            "description": "EPlus->AEO type mapping and weighting factors",
            "value": {
                "residential": {
                    "single family home": {"Single-Family": 1},
                    "mobile home": {"Single-Family": 1},
                    "multi family home": {"Multifamily": 1},
                },
                "commercial": {
                    "assembly": {"Hospital": 1},
                    "education": {"PrimarySchool": 0.26, "SecondarySchool": 0.74},
                    "food sales": {"Supermarket": 1},
                    "food service": {"QuickServiceRestaurant": 0.31, "FullServiceRestaurant": 0.69},
                    "health care": None,
                    "lodging": {"SmallHotel": 0.26, "LargeHotel": 0.74},
                    "large office": {"LargeOffice": 0.9, "MediumOfficeDetailed": 0.1},
                    "small office": {"SmallOffice": 0.12, "OutpatientHealthcare": 0.88},
                    "mercantile/service": {"RetailStandalone": 0.53, "RetailStripmall": 0.47},
                    "warehouse": {"Warehouse": 1},
                    "other": None,
                },
            },
        },
    }
}
