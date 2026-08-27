#!/usr/bin/env python3
import ast
import json
import os
from datetime import datetime
import pandas as pd

# ==========================
# PARSER FUNCTIONS
# ==========================


def parse_boolean(val):
    """Parses various truthy/falsy string representations into Python booleans."""
    if isinstance(val, bool):
        return val

    val_str = str(val).strip().lower()
    if val_str in ("true", "yes", "y", "1"):
        return True
    if val_str in ("false", "no", "n", "0"):
        return False

    raise ValueError(f"Cannot interpret '{val}' as a boolean.")


def parse_identity(val):
    """Pass-through for standard text/numeric fields; strips strings."""
    return val.strip() if isinstance(val, str) else val


def parse_integer(val):
    """Explicitly converts strings/floats to integers."""
    return int(val)


def parse_newline_list(val):
    """Parses newline-separated strings into a list."""
    if isinstance(val, list):
        return val
    if not isinstance(val, str):
        return [val]
    return [x.strip() for x in val.split("\n") if x.strip()]


def _parse_terminal_value(val_str, is_unit):
    """Helper: Converts strings to float/bool when applicable."""
    val_str = str(val_str).strip()
    if is_unit:
        return val_str
    if val_str.lower() == 'true':
        return True
    if val_str.lower() == 'false':
        return False
    try:
        return float(val_str)
    except ValueError:
        return val_str


def _recursive_dict(parts, is_unit):
    """Helper: Recursively nests fields separated by colons."""
    if len(parts) == 1:
        return _parse_terminal_value(parts[0], is_unit)
    # Force the generated key to lowercase
    return {parts[0].strip().lower(): _recursive_dict(parts[1:], is_unit)}


def _parse_dynamic_nested(val, is_unit):
    """Handles both simple values and nested dictionaries."""
    if not isinstance(val, str):
        return val

    if ";" in val and ":" not in val:
        return [_parse_terminal_value(x, is_unit) for x in val.split(";")]

    if ":" not in val:
        return _parse_terminal_value(val, is_unit)

    res = {}
    for p in val.split(";"):
        p = p.strip()
        if not p or ":" not in p:
            continue
        sub = [x.strip() for x in p.split(":")]

        # Force the top-level nested key to lowercase
        key = sub[0].lower()
        nested = _recursive_dict(sub[1:], is_unit)

        if key not in res:
            res[key] = nested
        else:
            if isinstance(res[key], dict) and isinstance(nested, dict):
                res[key].update(nested)
            else:
                res[key] = nested
    return res


def parse_nested_value(val):
    """Parses standard values utilizing dynamic dict nesting."""
    return _parse_dynamic_nested(val, is_unit=False)


def parse_nested_unit(val):
    """Parses unit identifiers utilizing dynamic dict nesting."""
    return _parse_dynamic_nested(val, is_unit=True)


def parse_source_details(val):
    """Parses semicolon-delimited source documentation metadata.
    Falls back to raw string if no delimiters are present."""
    if not isinstance(val, str):
        return val

    def _parse_single(s):
        # Fallback: if no semicolon is present, return the string as-is
        if ";" not in s:
            return s.strip()

        fields = ["title", "author", "year", "pages", "url"]
        parts = [x.strip() for x in s.split(";")]
        if len(parts) != len(fields):
            raise ValueError(
                f"Expected {len(fields)} fields, got {len(parts)} in '{s}'")

        res = {}
        for f, p in zip(fields, parts):
            if p in ("NA", "null", "") or pd.isna(p) or p.lower() == 'none':
                res[f] = None
            elif f == "year" or (f == "pages" and "," not in p):
                res[f] = int(p) if p else None
            elif f == "pages" and "," in p:
                res[f] = ast.literal_eval(p)
            else:
                res[f] = p
        return res

    # Handle multiple sources split by newline
    lines = [x.strip() for x in val.split("\n") if x.strip()]
    if len(lines) > 1:
        return [_parse_single(line) for line in lines]
    return _parse_single(lines[0])


def parse_author_details(val):
    """Parses semicolon-delimited author details and applies timestamp.
    Falls back to raw string + timestamp if no delimiters are present."""
    if not isinstance(val, str):
        return val

    # Fallback: if no semicolon is present, map the raw text to 'name'
    if ";" not in val:
        return {
            "name": val.strip(),
            "organization": None,
            "email": None,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    fields = ["name", "organization", "email"]
    parts = [x.strip() for x in val.split(";")]
    if len(parts) != len(fields):
        raise ValueError(
            f"Expected {len(fields)} fields, got {len(parts)} in '{val}'")

    res = {
        f: (None if p in ("NA", "null", "") or pd.isna(p) else p)
        for f, p in zip(fields, parts)
    }
    res["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return res


# ==========================================
# CONFIGURATION & DISPATCH MAPPING
# ==========================================


COL_ATTR_MAP = {
    "Name": ("name", parse_identity),
    "Description": ("_description", parse_identity),
    "Measure Type": ("measure_type", parse_identity),
    "Market Entry Year": ("market_entry_year", parse_integer),
    "Market Exit Year": ("market_exit_year", parse_integer),
    "Minimum Efficiency Electric Flag": ("min_eff_elec_flag", parse_boolean),
    "Ref. Case Flag": ("ref_case_flag", parse_boolean),
    "Region": ("climate_zone", parse_identity),
    "Building Type": ("bldg_type", parse_identity),
    "Building Vintage": ("structure_type", parse_identity),
    "End Use": ("end_use", parse_identity),
    "Baseline Fuel Type": ("fuel_type", parse_identity),
    "Switched to Fuel Type": ("fuel_switch_to", parse_identity),
    "Backup Fuel Fraction": ("backup_fuel_fraction", parse_nested_value),
    "Baseline Technology": ("technology", parse_identity),
    "Baseline Heating and Cooling Technology Pair": (
        "htcl_tech_link", parse_identity),
    "Switched to Technology": ("tech_switch_to", parse_identity),
    "Energy Performance": ("energy_efficiency", parse_nested_value),
    "Performance Units": ("energy_efficiency_units", parse_nested_unit),
    "Performance Source Notes": (
        ["energy_efficiency_source", "notes"], parse_identity),
    "Performance Source Details": (
        ["energy_efficiency_source", "source_data"], parse_source_details),
    "Installed Cost": ("installed_cost", parse_nested_value),
    "Cost Units": ("cost_units", parse_nested_unit),
    "Cost Source Notes": (
        ["installed_cost_source", "notes"], parse_identity),
    "Cost Source Details": (
        ["installed_cost_source", "source_data"], parse_source_details),
    "Electrical Upgrade Costs": ("add_elec_infr_cost", parse_nested_value),
    "Lifetime": ("product_lifetime", parse_nested_value),
    "Lifetime Units": ("product_lifetime_units", parse_nested_unit),
    "Lifetime Source Notes": (
        ["product_lifetime_source", "notes"], parse_identity),
    "Lifetime Source Details": (
        ["product_lifetime_source", "source_data"], parse_source_details),
    "Market Scaling Fraction": (
        "market_scaling_fractions", parse_nested_value),
    "Market Scaling Source Notes": (
        ["market_scaling_fractions_source", "notes"], parse_identity),
    "Market Scaling Source Details": (
        ["market_scaling_fractions_source", "source_data"],
        parse_source_details),
    "Author Details": ("_updated_by", parse_author_details)
}

PKG_COL_ATTR_MAP = {
    "Name": ("name", parse_identity),
    "Measures in Package": ("contributing_ECMs", parse_newline_list),
    "Additional Energy Savings": (
        ["benefits", "energy savings increase"], parse_nested_value),
    "Energy Savings Source Notes": (
        ["energy_savings_source", "notes"], parse_identity),
    "Energy Savings Source Details": (
        ["energy_savings_source", "source_data"], parse_source_details),
    "Additional Cost Reductions": (
        ["benefits", "cost reduction"], parse_nested_value),
    "Cost Reductions Source Notes": (
        ["cost_reduction_source", "notes"], parse_identity),
    "Cost Reductions Source Details": (
        ["cost_reduction_source", "source_data"], parse_source_details)
}

CSV_DTYPES = {
    "Name": str,
    "Market Entry Year": "Int64",
    "Market Exit Year": "Int64",
    "Minimum Efficiency Electric Flag": str,
    "Ref. Case Flag": str,
    "Backup Fuel Fraction": str,
    "Energy Performance": str,
    "Performance Units": str,
    "Performance Source Details": str,
    "Installed Cost": str,
    "Cost Units": str,
    "Cost Source Details": str,
    "Electrical Upgrade Costs": str,
    "Lifetime": str,
    "Lifetime Units": str,
    "Lifetime Source Details": str,
    "Market Scaling Fraction": str,
    "Market Scaling Source Details": str,
    "Author Details": str,
}

PKG_CSV_DTYPES = {
    "Name": str,
    "Measures in Package": str,
    "Additional Energy Savings": str,
    "Energy Savings Source Details": str,
    "Additional Cost Reductions": str,
    "Cost Reductions Source Details": str
}

# ==========================================
# MAIN EXECUTION
# ==========================================


def clean_dataframe(df):
    """Normalizes missing values before iteration to avoid logic checks."""
    return df.replace(
        {pd.NA: None, "NA": None, "null": None, float('nan'): None, "": None}
    )


def populate_json(record_dict, mapping_config):
    """Processes a single row dictionary into a formatted JSON structure."""
    output_dict = {}

    for col, (json_key, parser_func) in mapping_config.items():
        if col in record_dict and record_dict[col] is not None:
            try:
                parsed_val = parser_func(record_dict[col])
            except ValueError as e:
                meas_name = record_dict.get('Name', 'Unknown')
                raise ValueError(
                    f"Error parsing '{col}' for '{meas_name}': {e}"
                )

            if isinstance(json_key, list):
                if json_key[0] not in output_dict:
                    output_dict[json_key[0]] = {}
                output_dict[json_key[0]][json_key[1]] = parsed_val
            else:
                output_dict[json_key] = parsed_val

    return output_dict


def main(base_dir):
    """Import measure data from CSV and generate a JSON for each measure."""

    meas_gen_folder = "ecm_definitions/meas_pkg_gen_io/"
    fpo = os.path.join(base_dir, meas_gen_folder, "outputs")
    os.makedirs(fpo, exist_ok=True)

    fpi = os.path.join(base_dir, meas_gen_folder, "inputs/meas_in.csv")
    fpi_pk = os.path.join(base_dir, meas_gen_folder, "inputs/pkg_in.csv")

    # --- PROCESS INDIVIDUAL MEASURES ---
    raw_df = pd.read_csv(fpi, dtype=CSV_DTYPES)
    m_in_df = clean_dataframe(raw_df)
    for m in m_in_df.to_dict('records'):
        print(f"Generating measure '{m['Name']}'...", end="", flush=True)
        m_out = populate_json(m, COL_ATTR_MAP)

        out_path = os.path.join(fpo, f"{m['Name']}.json")
        with open(out_path, "w") as jso:
            json.dump(m_out, jso, indent=2)
        print("Complete.")

    # --- PROCESS PACKAGE MEASURES ---
    if os.path.exists(fpi_pk):
        pkg_out = []
        raw_pkg_df = pd.read_csv(fpi_pk, dtype=PKG_CSV_DTYPES)
        m_pk_in_df = clean_dataframe(raw_pkg_df)

        for m_pk in m_pk_in_df.to_dict('records'):
            print(f"Generating package '{m_pk['Name']}'...", end="", flush=True)
            m_pk_out = populate_json(m_pk, PKG_COL_ATTR_MAP)
            pkg_out.append(m_pk_out)
            print("Complete.")

        pkg_out_path = os.path.join(fpo, "package_ecms.json")
        with open(pkg_out_path, 'w+') as jso:
            json.dump(pkg_out, jso, indent=2)


if __name__ == "__main__":
    base_dir = os.getcwd()
    main(base_dir)
