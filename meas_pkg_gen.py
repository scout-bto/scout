#!/usr/bin/env python3
import ast
import json
import os
from datetime import datetime

import pandas as pd


def main(base_dir):
    """Import measure data from CSV and generate a JSON for each measure."""

    # Set up input CSV column -> attribute mapping
    col_attr_map = {
        "Name": "name",
        "Description": "_description",
        "Measure Type": "measure_type",
        "Market Entry Year": "market_entry_year",
        "Market Exit Year": "market_exit_year",
        "Minimum Efficiency Electric Flag": "min_eff_elec_flag",
        "Ref. Case Flag": "ref_case_flag",
        "Region": "climate_zone",
        "Building Type": "bldg_type",
        "Building Vintage": "structure_type",
        "End Use": "end_use",
        "Baseline Fuel Type": "fuel_type",
        "Switched to Fuel Type": "fuel_switch_to",
        "Backup Fuel Fraction": "backup_fuel_fraction",
        "Baseline Technology": "technology",
        "Baseline Heating and Cooling Technology Pair": "htcl_tech_link",
        "Switched to Technology": "tech_switch_to",
        "Energy Performance": "energy_efficiency",
        "Performance Units": "energy_efficiency_units",
        "Performance Source Notes": ["energy_efficiency_source", "notes"],
        "Performance Source Details": [
            "energy_efficiency_source", "source_data"],
        "Installed Cost": "installed_cost",
        "Cost Units": "cost_units",
        "Cost Source Notes": ["installed_cost_source", "notes"],
        "Cost Source Details": ["installed_cost_source", "source_data"],
        "Electrical Upgrade Costs": "add_elec_infr_cost",
        "Lifetime": "product_lifetime",
        "Lifetime Units": "product_lifetime_units",
        "Lifetime Source Notes": ["product_lifetime_source", "notes"],
        "Lifetime Source Details": ["product_lifetime_source", "source_data"],
        "Market Scaling Fraction": "market_scaling_fractions",
        "Market Scaling Source Notes": [
            "market_scaling_fractions_source", "notes"],
        "Market Scaling Source Details": [
            "market_scaling_fractions_source", "source_data"],
        "Author Details": "_updated_by"
    }

    # Set fields for all measure source data
    srce_flds = ["title", "author", "year", "pages", "url"]
    # Set fields for measure author data (timestamp is added subsequently)
    auth_flds = ["name", "organization", "email"]

    # Set measure generation data folder name
    meas_gen_folder = "ecm_definitions/meas_pkg_gen_io/"

    # Set JSON output folder
    fpo = os.path.join(base_dir, meas_gen_folder, "outputs")

    # Ensure the output directory exists
    os.makedirs(fpo, exist_ok=True)

    # Load individual measure data
    fpi = os.path.join(base_dir, meas_gen_folder, "inputs/meas_in.csv")
    m_in = pd.read_csv(fpi)

    # Load measure package data (if any)
    fpi_pk = os.path.join(base_dir, meas_gen_folder, "inputs/pkg_in.csv")
    m_pk_in = pd.read_csv(fpi_pk)

    # Iterate across all measure rows as native dicts for speed
    for m in m_in.to_dict('records'):
        print(f"Generating measure '{m['Name']}'...", end="", flush=True)
        m_out = {}
        for col, attr in col_attr_map.items():
            i_o_val(col, attr, m_out, m, srce_flds, auth_flds)

        out_path = os.path.join(fpo, f"{m['Name']}.json")
        with open(out_path, "w") as jso:
            json.dump(m_out, jso, indent=2)
        print("Complete.")

    # Initialize output package information
    pkg_out = []
    # Set up input CSV column -> attribute mapping
    col_attr_map_pk = {
        "Name": "name",
        "Measures in Package": "contributing_ECMs",
        "Additional Energy Savings": ["benefits", "energy savings increase"],
        "Energy Savings Source Notes": ["energy_savings_source", "notes"],
        "Energy Savings Source Details": [
            "energy_savings_source", "source_data"],
        "Additional Cost Reductions": ["benefits", "cost reduction"],
        "Cost Reductions Source Notes": ["cost_reduction_source", "notes"],
        "Cost Reductions Source Details": [
            "cost_reduction_source", "source_data"]
    }

    # Iterate across all measure package rows
    for m_pk in m_pk_in.to_dict('records'):
        print(f"Generating package '{m_pk['Name']}'...", end="", flush=True)
        m_pk_out = {}
        for col, attr in col_attr_map_pk.items():
            i_o_val(col, attr, m_pk_out, m_pk, srce_flds, auth_flds)

        pkg_out.append(m_pk_out)
        print("Complete.")

    pkg_out_path = os.path.join(fpo, "package_ecms.json")
    with open(pkg_out_path, 'w+') as jso:
        json.dump(pkg_out, jso, indent=2)


def i_o_val(col, attr, m_out, m, srce_flds, auth_flds):
    """Translate CSV measure data inputs into JSON outputs."""

    val_i = m[col]

    # Replace NA or NaN values with None
    if val_i != 0 and (
            val_i == "NA" or pd.isna(val_i) or val_i == "null" or not val_i):
        val_f = None
    # Handle source data with multiple sources (each on newline in CSV)
    elif ("Source Details" in col and
          isinstance(val_i, str) and "\n" in val_i):
        val_strp_frst = [x.strip() for x in val_i.split("\n")]
        val_f = []
        for v in val_strp_frst:
            val_strip_scnd = [x.strip() for x in v.split(";")]
            val_f.append(
                dlm_nst(col, attr, val_strip_scnd,
                        srce_flds, auth_flds, m["Name"]))
    # Handle values with nested information (denoted by ';' delimiter)
    elif isinstance(val_i, str) and ";" in val_i:
        val_strp = [x.strip() for x in val_i.split(";")]
        val_f = dlm_nst(col, attr, val_strp, srce_flds, auth_flds, m["Name"])
    # Handle package contributing ECM data (each on newline)
    elif "Measures in Package" in col and isinstance(
            val_i, str) and "\n" in val_i:
        val_f = [x.strip() for x in val_i.split("\n")]
    # Check to ensure strings should not be further converted to numbers
    elif isinstance(val_i, str):
        try:
            val_f = float(val_i.strip())
        except ValueError:
            val_f = val_i.strip()
    # Ensure that market entry and exit years are always integers
    elif any(x in col for x in ["Market Entry Year", "Market Exit Year"]):
        val_f = int(val_i)
    # Otherwise finalize CSV value as-is for JSON
    else:
        val_f = val_i

    # Set output value in JSON; handle formatting of sourcing info
    if not isinstance(attr, list):
        m_out[attr] = val_f
    else:
        # Handle existing dict (add to)
        if attr[0] in m_out:
            m_out[attr[0]][attr[1]] = val_f
        else:
            m_out[attr[0]] = {attr[1]: val_f}


def dlm_nst(col, attr, val, srce_flds, auth_flds, meas_name):
    """Manage measure attributes with delimited and/or nested input data.

    Args:
        col (str): Input CSV heading name.
        attr (str or list): Output JSON attribute name(s).
        val (list): CSV data to be assigned across multiple sub-fields.
        srce_flds (list): Sub-fields for sourcing information.
        auth_flds (list): Sub-fields for author information attributes.
        meas_name (str): Measure currently being looped through.

    Returns:
        Nested dict with required information for given attributes.
    """

    # Handle nested performance, cost, lifetime, or market scaling data
    if any((x in col and "Source" not in col) for x in [
        "Performance", "Cost", "Lifetime", "Scaling"]) and any(
            ":" in x for x in val):
        val_dlm_nst = {}
        for vi in val:
            items = [x.strip() for x in vi.split(":")]
            try:
                recurs_val = recursive_dict(items[1:], col)
                if items[0] not in val_dlm_nst:
                    val_dlm_nst[items[0]] = recurs_val
                else:
                    val_dlm_nst[items[0]].update(recurs_val)
            except IndexError:
                raise ValueError(
                    f"Check nested information format in field '{col}' "
                    f"for measure '{meas_name}'")
        val_f = val_dlm_nst

    # Populate source details data
    elif "Source Details" in col:
        if len(val) != len(srce_flds):
            raise ValueError(
                f"Missing information in field '{col}' for measure "
                f"'{meas_name}'")
        val_dlm_nst = {}
        for f_i, f in enumerate(srce_flds):
            if val[f_i] == "NA" or pd.isna(val[f_i]) or \
                    val[f_i] == "null" or not val[f_i]:
                val[f_i] = None
            elif f == "year" or (f == "pages" and "," not in val[f_i]):
                try:
                    val[f_i] = int(val[f_i])
                except ValueError:
                    msg = "year info." if f == "year" else "page info."
                    raise ValueError(
                        f"Check for correct {msg} format in field '{col}' "
                        f"for measure '{meas_name}'")
            elif f == "pages" and "," in val[f_i]:
                try:
                    val[f_i] = ast.literal_eval(val[f_i])
                except ValueError:
                    raise ValueError(
                        f"Check for correct page info. format in field "
                        f"'{col}' for measure '{meas_name}'")
            val_dlm_nst[f] = val[f_i]
        val_f = val_dlm_nst

    # Handle measure author data
    elif "Author" in col:
        if len(val) != len(auth_flds):
            raise ValueError(
                f"Missing information in field '{col}' for measure "
                f"'{meas_name}'")
        val_dlm_nst = {}
        for f_i, f in enumerate(auth_flds):
            if val[f_i] == "NA" or pd.isna(val[f_i]) or \
                    val[f_i] == "null" or not val[f_i]:
                val[f_i] = None
            val_dlm_nst[f] = val[f_i]

        val_f = val_dlm_nst
        val_f["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # All other data set as is
    else:
        val_f = val

    return val_f


def recursive_dict(data, col):
    """Recursively populate dict given nested attribute data.

    Args:
        data (list): Delimited data to translate into nested dict.
        col (str): Input CSV heading name.

    Returns:
        Nested dict with required information for given attributes.
    """

    # At terminal value (one element list)
    if len(data) == 1 and "Units" not in col:
        val_str = data[0].strip()

        # Convert true/false strings to proper booleans for JSON
        if val_str.lower() == 'true':
            return True
        elif val_str.lower() == 'false':
            return False

        # Try to cast to float, fallback to string if it fails
        try:
            return float(val_str)
        except ValueError:
            return val_str

    elif len(data) == 1 and "Units" in col:
        return data[0].strip()

    # Not yet at terminal value; nest recursively
    else:
        first_value = data[0].strip()
        data = {first_value: recursive_dict(data[1:], col)}
        return data


if __name__ == "__main__":
    # Set current working directory
    base_dir = os.getcwd()
    main(base_dir)
