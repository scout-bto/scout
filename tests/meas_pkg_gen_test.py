import sys
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

# Dynamically add the parent directory to the Python path so it can find meas_pkg_gen.py
sys.path.append(str(Path(__file__).parent.parent))

from meas_pkg_gen import (  # noqa: E402
    parse_identity,
    parse_integer,
    parse_newline_list,
    parse_boolean,
    parse_nested_value,
    parse_nested_unit,
    parse_source_details,
    parse_author_details,
    clean_dataframe,
    populate_json
)


def test_parse_identity():
    assert parse_identity("  Test String  ") == "Test String"
    assert parse_identity(123.45) == 123.45
    assert parse_identity(None) is None


def test_parse_integer():
    assert parse_integer("2024") == 2024
    assert parse_integer(2024.0) == 2024
    with pytest.raises(ValueError):
        parse_integer("not a number")


def test_parse_newline_list():
    assert parse_newline_list("ECM 1\nECM 2\n ECM 3 ") == [
        "ECM 1", "ECM 2", "ECM 3"]
    assert parse_newline_list("Single ECM") == ["Single ECM"]
    assert parse_newline_list(["Already", "List"]) == ["Already", "List"]


def test_parse_boolean():
    assert parse_boolean("yes") is True
    assert parse_boolean("True") is True
    assert parse_boolean("1") is True
    assert parse_boolean("no") is False
    assert parse_boolean("False") is False
    assert parse_boolean("0") is False
    assert parse_boolean(True) is True
    with pytest.raises(ValueError):
        parse_boolean("maybe")


def test_parse_source_details():
    # Fallback raw string
    assert parse_source_details("Just a string") == "Just a string"

    # Fully populated 5-part string
    res1 = parse_source_details("Doc Title; Jane Doe; 2023; 10, 15; http")
    assert res1 == {
        "title": "Doc Title",
        "author": "Jane Doe",
        "year": 2023,
        "pages": (10, 15),
        "url": "http"
    }

    # Missing values handling
    res2 = parse_source_details("Doc Title; NA; null; ; none")
    assert res2 == {
        "title": "Doc Title",
        "author": None,
        "year": None,
        "pages": None,
        "url": None
    }

    # Multiple sources (newline separated)
    multi = parse_source_details("T1; A1; 2020; 1; u1\nT2; A2; 2021; 2; u2")
    assert isinstance(multi, list)
    assert len(multi) == 2
    assert multi[0]["title"] == "T1"
    assert multi[1]["title"] == "T2"

    # Bad delimiter count
    with pytest.raises(ValueError):
        parse_source_details("Too; Few; Parts")


def test_parse_author_details():
    # Fallback raw string
    res_raw = parse_author_details("Jane Doe")
    assert res_raw["name"] == "Jane Doe"
    assert res_raw["organization"] is None
    assert "timestamp" in res_raw

    # Fully populated 3-part string
    res_full = parse_author_details("Jane Doe; NREL; jane@nrel.gov")
    assert res_full["name"] == "Jane Doe"
    assert res_full["organization"] == "NREL"
    assert res_full["email"] == "jane@nrel.gov"
    assert "timestamp" in res_full


def test_clean_dataframe():
    df = pd.DataFrame({
        "A": [pd.NA, "NA", "null", np.nan, "", "valid_string"],
        "B": [1, 2, 3, 4, 5, 6]
    })
    cleaned = clean_dataframe(df)

    # First 5 rows of column A should be converted to actual None
    for i in range(5):
        assert cleaned.at[i, "A"] is None
    assert cleaned.at[5, "A"] == "valid_string"


def test_parse_nested_value():
    assert parse_nested_value("0.95") == 0.95
    assert parse_nested_value("Text Value") == "Text Value"

    # expect lowercase keys
    assert parse_nested_value("Heating: 0.95; Cooling: 0.85") == {
        "heating": 0.95, "cooling": 0.85}
    assert parse_nested_value("Gas: Heating: 0.95; Gas: Water: 0.8") == {
        "gas": {"heating": 0.95, "water": 0.8}}


def test_parse_nested_unit():
    assert parse_nested_unit("MMBtu") == "MMBtu"

    # expect lowercase keys
    assert parse_nested_unit("Heating: MMBtu; Cooling: kWh") == {
        "heating": "MMBtu", "cooling": "kWh"}
    assert parse_nested_unit("1000") == "1000"


def test_populate_json():
    test_map = {
        "Name": ("name", parse_identity),
        "Entry": ("market_entry_year", parse_integer),
        "Active": ("is_active", parse_boolean),
        "Perf": (["energy", "performance_data"], parse_nested_value),
    }

    record = {
        "Name": " Heat Pump ",
        "Entry": "2025",
        "Active": "yes",
        "Perf": "Heating: 3.5; Cooling: 4.0",
    }

    expected_output = {
        "name": "Heat Pump",
        "market_entry_year": 2025,
        "is_active": True,
        "energy": {
            "performance_data": {
                # lowercase
                "heating": 3.5,
                "cooling": 4.0
            }
        }
    }

    assert populate_json(record, test_map) == expected_output
