#!/usr/bin/env python3

"""
Test data for Time-Sensitive Valuation (TSV) tests.

Extracted from test_time_sensitive_valuation_test.py.
"""

sample_tsv_measure_in_metrics = [
    {
        "name": "sample peak load tsv metrics",
        "energy_efficiency": 0,
        "energy_efficiency_units": "relative savings (constant)",
        "markets": None,
        "installed_cost": 25,
        "cost_units": "2014$/ft^2 floor",
        "market_entry_year": None,
        "market_exit_year": None,
        "product_lifetime": 1,
        "market_scaling_fractions": None,
        "market_scaling_fractions_source": None,
        "measure_type": "full service",
        "structure_type": ["new", "existing"],
        "bldg_type": "large office",
        "climate_zone": "FRCC",
        "fuel_type": "electricity",
        "fuel_switch_to": None,
        "end_use": "heating",
        "technology": ["resistance heat", "ASHP"],
        "tsv_features": None,
    },
    {
        "name": "sample peak load tsv metrics 2",
        "energy_efficiency": 0,
        "energy_efficiency_units": "relative savings (constant)",
        "markets": None,
        "installed_cost": 25,
        "cost_units": "2014$/unit",
        "market_entry_year": None,
        "market_exit_year": None,
        "product_lifetime": 1,
        "market_scaling_fractions": None,
        "market_scaling_fractions_source": None,
        "measure_type": "full service",
        "structure_type": ["new", "existing"],
        "bldg_type": "single family home",
        "climate_zone": "ISNE",
        "fuel_type": "electricity",
        "fuel_switch_to": None,
        "end_use": "TVs",
        "technology": ["TV"],
        "tsv_features": None,
    },
]
