#!/usr/bin/env python3

"""Tests for Year Mapping (tsv_cost_carb_yrmap)"""

from scout.ecm_prep import ECMPrepHelper
import pytest


@pytest.fixture(scope="module")
def yr_map_test_data():
    """Fixture providing test data for year mapping tests."""
    test_tsv_data_in = [
        {yr: {} for yr in [str(x) for x in range(2018, 2051, 4)]},
        {yr: {} for yr in [str(x) for x in range(2018, 2047, 4)]},
        {yr: {} for yr in [str(x) for x in range(2014, 2055, 4)]},
    ]

    test_aeo_years_in = [str(x) for x in range(2015, 2051)]

    test_out_map = [
        {
            "2018": [str(x) for x in range(2015, 2022)],
            "2022": [str(x) for x in range(2022, 2026)],
            "2026": [str(x) for x in range(2026, 2030)],
            "2030": [str(x) for x in range(2030, 2034)],
            "2034": [str(x) for x in range(2034, 2038)],
            "2038": [str(x) for x in range(2038, 2042)],
            "2042": [str(x) for x in range(2042, 2046)],
            "2046": [str(x) for x in range(2046, 2050)],
            "2050": [str(x) for x in range(2050, 2051)],
        },
        {
            "2018": [str(x) for x in range(2015, 2022)],
            "2022": [str(x) for x in range(2022, 2026)],
            "2026": [str(x) for x in range(2026, 2030)],
            "2030": [str(x) for x in range(2030, 2034)],
            "2034": [str(x) for x in range(2034, 2038)],
            "2038": [str(x) for x in range(2038, 2042)],
            "2042": [str(x) for x in range(2042, 2046)],
            "2046": [str(x) for x in range(2046, 2051)],
        },
        {
            "2014": [str(x) for x in range(2014, 2018)],
            "2018": [str(x) for x in range(2018, 2022)],
            "2022": [str(x) for x in range(2022, 2026)],
            "2026": [str(x) for x in range(2026, 2030)],
            "2030": [str(x) for x in range(2030, 2034)],
            "2034": [str(x) for x in range(2034, 2038)],
            "2038": [str(x) for x in range(2038, 2042)],
            "2042": [str(x) for x in range(2042, 2046)],
            "2046": [str(x) for x in range(2046, 2050)],
            "2050": [str(x) for x in range(2050, 2054)],
            "2054": [],
        },
    ]

    return {
        "test_tsv_data_in": test_tsv_data_in,
        "test_aeo_years_in": test_aeo_years_in,
        "test_out_map": test_out_map,
    }


def test_yrmap(yr_map_test_data):
    """Test 'tsv_cost_carb_yrmap' function given valid inputs."""
    from tests.ecm_prep_test.common import dict_check

    # Loop across all tested year input scenarios
    for ind in range(0, len(yr_map_test_data["test_tsv_data_in"])):
        # Execute the function
        out_map = ECMPrepHelper.tsv_cost_carb_yrmap(
            yr_map_test_data["test_tsv_data_in"][ind], yr_map_test_data["test_aeo_years_in"]
        )
        # Check function outputs
        dict_check(out_map, yr_map_test_data["test_out_map"][ind])
