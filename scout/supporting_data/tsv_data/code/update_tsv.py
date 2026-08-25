import pandas as pd
import boto3
import json
import gzip
import datetime
import numpy as np
import warnings
import time
import os
import textwrap
from os import getcwd
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor

from compute_peak_days import (
    COMMERCIAL_ENERGY_COLS, RESIDENTIAL_ENERGY_COLS, WINTER_DAYS,
    SUMMER_DAYS, WINTER_DAYS_EXTENDED, SUMMER_DAYS_EXTENDED,
    BOUNDARY_CHECK_BUFFER_DAYS, load_combined_hourly, find_peak_days)

warnings.filterwarnings('ignore')
MAP_DIR = "map"
SQL_DIR = "sql"
OUTPUT_DIR = "csv"
JSON_DIR = "json"
DIAG_DIR = "diagnostics"
# Base template lives alongside this script (not in JSON_DIR), since
# JSON_DIR holds only large generated output that's gitignored.
BASE_TEMPLATE = "tsv_load_in_2024.json"
EXTERNAL_S3_DIR = "datasets"
# Dedicated Athena database for Scout's tsv data
DATABASE_NAME = "scout_tsv"
BUCKET_NAME = 'yujie-bucket'
# Final gzipped load shape files consumed directly by Scout's ecm_prep.py
# live one level up from this script, in supporting_data/tsv_data/
TSV_DATA_DIR = ".."
# ComStock/ResStock release versions queried by --stock_version. 2025 is the
# default; 2024 is kept for backwards compatibility/comparison.
STOCK_RELEASES = {
    "2025": {"comstock": "2025.3", "resstock": "2025.1"},
    "2024": {"comstock": "2024.2", "resstock": "2024.2"},
}

# Standard-time (no-DST) UTC offset in hours for each state's dominant legal
# time zone. ComStock/ResStock publish every timeseries on an Eastern
# Standard Time clock regardless of where the building actually is (see the
# ComStock/ResStock FAQ: "timestamps of all load profiles have been
# converted to Eastern Standard Time, to prevent issues when aggregating
# across time zones"), so an EMM region or state whose local standard time
# isn't Eastern needs its load shape rolled to match -- see
# _region_tz_shift_hours/_apply_tz_shift below. A handful of states split
# across two zones (FL, IN, KY, MI, TN, TX, ND, SD, NE, KS, ID) are assigned
# their population-majority zone here; that's already an approximation,
# same as the EMM-region-level dominant-zone approximation those functions
# make for regions spanning multiple states.
STATE_TZ_OFFSET = {
    'CT': -5, 'DE': -5, 'FL': -5, 'GA': -5, 'IN': -5, 'KY': -5, 'ME': -5,
    'MD': -5, 'MA': -5, 'MI': -5, 'NH': -5, 'NJ': -5, 'NY': -5, 'NC': -5,
    'OH': -5, 'PA': -5, 'RI': -5, 'SC': -5, 'VT': -5, 'VA': -5, 'WV': -5,
    'DC': -5,
    'AL': -6, 'AR': -6, 'IL': -6, 'IA': -6, 'KS': -6, 'LA': -6, 'MN': -6,
    'MS': -6, 'MO': -6, 'ND': -6, 'NE': -6, 'OK': -6, 'SD': -6, 'TN': -6,
    'TX': -6, 'WI': -6,
    'AZ': -7, 'CO': -7, 'ID': -7, 'MT': -7, 'NM': -7, 'UT': -7, 'WY': -7,
    'CA': -8, 'NV': -8, 'OR': -8, 'WA': -8,
    'AK': -9,
    'HI': -10,
}
EST_OFFSET = -5


def _region_tz_shift_hours(geo_map_path):
    """ Population-weighted dominant timezone shift (hours, relative to
    Eastern Standard Time) for every EMM region and state found in
    geo_map.csv. For a region straddling multiple time zones (e.g. NWPP
    spans WA/OR/MT), the shift used is whichever single zone holds the most
    population in that region -- an approximation, but a closer match to
    reality than applying no shift at all (the status quo). Returns
    (emm_shift, state_shift), each {region_code: shift_hours}. """
    geo = pd.read_csv(geo_map_path)
    geo['tz_offset'] = geo['state_abbr'].map(STATE_TZ_OFFSET)

    def dominant_shift(grp):
        pop_by_offset = grp.groupby('tz_offset')['population'].sum()
        return int(pop_by_offset.idxmax() - EST_OFFSET)

    emm_shift = geo.groupby('emm2020_county').apply(dominant_shift).to_dict()
    state_shift = geo.groupby('state_abbr').apply(dominant_shift).to_dict()
    return emm_shift, state_shift


def _apply_tz_shift(vals, shift_hours):
    """ Roll an 8760-hour load shape by shift_hours to convert it from
    Eastern Standard Time (the clock ComStock/ResStock publish on) into a
    region's own local standard time: the value ComStock recorded at EST
    hour (t - shift_hours) becomes this shape's value at hour t, i.e. what
    that region's own clock actually read at hour t. """
    if not shift_hours:
        return vals
    return vals[-shift_hours:] + vals[:-shift_hours]


building_map = {
    "commercial": {
        "MediumOfficeDetailed": ["MediumOffice"],
        "LargeOfficeDetailed": ["LargeOffice"],
        "LargeHotel": ["LargeHotel"],
        "RetailStandalone": ["RetailStandalone"],
        "Warehouse": ["Warehouse"]
        },
    "residential": {
        # "MF": also excludes 'multi-family_with_2_-_4_units'
        "MF": ['multi-family_with_5plus_units'],
        # "SF": also excludes 'single-family_attached'
        "SF": ['single-family_detached'],
        "MH": ['mobile_home', 'mobile home']
    }}


enduse_map = {
    "commercial": ["heating", "cooling", "pumps", "ventilation",
                   "water heating", "lighting", "refrigeration", "cooking",
                   "PCs", "non-PC office equipment", "plug loads"],
    "residential": ["heating", "cooling", "water heating", "cooking", "drying",
                    "lighting", "refrigeration", "ceiling fan",
                    "fans and pumps", "plug loads", "clothes washing",
                    "dishwasher", "pool heaters", "pool pumps",
                    "portable electric spas"]}

replacements = {
    "pcs": "PCs",
    "nonpc_office_equipment": "non-PC office equipment",
    "other_mels": "plug loads",  # "other (MELs)"
    "water_heating": "water heating",
    "ceiling_fan": "ceiling fan",
    "fans_and_pumps": "fans and pumps",
    "tvs": "TVs",
    "other": "plug loads",
    "clothes_washing": "clothes washing",
    "pool_heaters": "pool heaters",
    "pool_pumps": "pool pumps",
    "portable_electric_spas": "portable electric spas",
    "Multi-Family with 5+ Units": "multi-family_with_5plus_units",
    "Multi-Family with 2 - 4 Units": "multi-family_with_2_-_4_units",
    "Single-Family Detached": "single-family_detached",
    "Single-Family Attached": "single-family_attached",
    "Mobile Home": "mobile_home"
}


def replace_strings_in_dataframe(df, replacements):
    # Replace strings in column names
    df.rename(columns=replacements, inplace=True)

    # Replace strings in the data
    df.replace(replacements, inplace=True)

    return df


def wait_for_query_to_complete(client, query_execution_id):
    status = 'RUNNING'
    max_attempts = 360
    while max_attempts > 0:
        max_attempts -= 1
        query_status = client.get_query_execution(
            QueryExecutionId=query_execution_id)
        status = query_status['QueryExecution']['Status']['State']
        print(f"Query status: {status}, Attempts left: {max_attempts}")

        if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            return status, query_status
        time.sleep(5)


def download_query_result(s3_client, result_loc, local_path):
    """ Download an Athena query's CSV result directly from S3. Far faster
    than paginating GetQueryResults row-by-row for large result sets
    (Athena already writes the full CSV to result_loc on completion). """
    bucket, key = result_loc[len("s3://"):].split("/", 1)
    s3_client.download_file(bucket, key, local_path)


def sql_template_vars(bstock_source, version):
    """ Build the {placeholder}: value substitutions the SQL templates in
    SQL_DIR need to target a given ResStock/ComStock release. The 2025
    releases changed relative to 2024 in ways that reach beyond the table
    name: the by_state "timestamp" column is now a native TIMESTAMP instead
    of an epoch-nanosecond bigint, and (ResStock only) the metadata table
    was renamed from "..._metadata" to "..._parquet", its sqft column from
    "in.sqft" to "in.sqft..ft2", and its energy_consumption columns gained a
    "..kwh" suffix. """
    release = STOCK_RELEASES[version][bstock_source]
    by_state_table = f"{bstock_source}_amy2018_release_{release}_by_state"
    if version == "2025":
        ts_trunc = "DATE_TRUNC('hour', ts.\"timestamp\")"
    else:
        ts_trunc = ("DATE_TRUNC('hour', "
                    "from_unixtime(ts.\"timestamp\" / 1000000000))")

    if bstock_source == "comstock":
        meta_table = f"{bstock_source}_amy2018_release_{release}_parquet"
        kwh, sqft_col = "", "in.sqft..ft2"
    else:
        if version == "2025":
            meta_table = f"{bstock_source}_amy2018_release_{release}_parquet"
            kwh, sqft_col = "..kwh", "in.sqft..ft2"
        else:
            meta_table = f"{bstock_source}_amy2018_release_{release}_metadata"
            kwh, sqft_col = "", "in.sqft"

    return {
        "by_state_table": by_state_table,
        "meta_table": meta_table,
        "ts_trunc": ts_trunc,
        "kwh": kwh,
        "sqft_col": sqft_col,
    }


def read_sql_file(sql_file, version):
    bstock_source = "comstock" if sql_file.startswith("comstock") \
        else "resstock"
    with open(os.path.join(SQL_DIR, sql_file), 'r', encoding='utf-8') as file:
        template = file.read()
    return template.format(**sql_template_vars(bstock_source, version))


def execute_athena_query(client, query, is_create, wait=True):
    response = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': DATABASE_NAME},
        ResultConfiguration={'OutputLocation': f"s3://{BUCKET_NAME}/configs/"}
    )
    query_execution_id = response['QueryExecutionId']

    if not wait:
        return query_execution_id, None

    status, query_status = wait_for_query_to_complete(
        client, query_execution_id)

    if status in ['FAILED', 'CANCELLED']:
        print(query_status['QueryExecution']['Status'].
              get('StateChangeReason', 'Unknown failure reason'))
        return False, None

    if status == "SUCCEEDED":
        result_loc = query_status['QueryExecution'][
            'ResultConfiguration']['OutputLocation']
        print(f"SQL query succeeded and results are stored in {result_loc}")
        return result_loc, query_execution_id


def sql_to_csvout(s3_client, athena_client, sql_file, version, out_name=None):
    fname = out_name or os.path.splitext(sql_file)[0]
    out_path = f"{OUTPUT_DIR}/{fname}.csv"
    if os.path.isfile(out_path):
        print(f"{out_path} already exists, skipping re-query "
              "(delete the file to force a re-run).")
        return
    query_start = time.time()
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] "
          f"Starting Athena query ({version} release): {sql_file}")
    query = read_sql_file(sql_file, version)
    s3_location, query_execution_id = execute_athena_query(
        athena_client, query, False, wait=True)
    elapsed = time.time() - query_start
    if query_execution_id:
        download_query_result(s3_client, s3_location, out_path)
        print(f"{out_path} is successfully saved! ({elapsed:.0f}s)")
        print(f"Query results stored: {s3_location}")
    elif s3_location:
        print(f"""Query completed but no results.
              Results path: {s3_location}""")
    else:
        print(f"Query {sql_file} failed or was cancelled.")


def upload_file_to_s3(client, local_path, bucket, s3_path):
    client.upload_file(local_path, bucket, s3_path)
    print(f"""UPLOADED {os.path.basename(local_path)}
          to s3://{bucket}/{s3_path}""")


def sql_create_table(df, table_name):
    columns_sql = ',\n'.join([f"`{col}` STRING" for col in df.columns])
    sql_str = f"""
    CREATE EXTERNAL TABLE IF NOT EXISTS {table_name} (
        {columns_sql}
    )
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY ','
    LOCATION 's3://{BUCKET_NAME}/{EXTERNAL_S3_DIR}/{table_name}/'
    TBLPROPERTIES ('skip.header.line.count'='1');
    """
    return sql_str


def s3_create_tables_from_csv(s3_client, athena_client, dir_name, file_name):
    local_path = os.path.join(dir_name, file_name)
    file_no_ext = os.path.splitext(file_name)[0]
    if os.path.isfile(local_path):
        s3_path = f"{EXTERNAL_S3_DIR}/{file_no_ext}/{file_name}"
        upload_file_to_s3(s3_client, local_path, BUCKET_NAME, s3_path)
        sql_query = sql_create_table(
            pd.read_csv(local_path),
            os.path.splitext(os.path.basename(local_path))[0])
        _, _ = execute_athena_query(athena_client, sql_query, True)


def nested_set(adict, keys, value):
    for key in keys[:-1]:
        adict = adict.setdefault(key, {})
    adict[keys[-1]] = value


def write_gzip_json(data, filename):
    """ Gzip-compress a JSON-serializable dict to supporting_data/tsv_data/,
    matching the format Scout's ecm_prep.py reads via gzip.GzipFile. """
    out_path = os.path.join(TSV_DATA_DIR, filename)
    with gzip.GzipFile(out_path, 'w') as gz_file:
        gz_file.write(json.dumps(data, indent=2).encode('utf-8'))
    print(f"{filename} is successfully saved!")


def read_gzip_json(filename):
    """ Inverse of write_gzip_json: load one of the final
    tsv_load_{EMM,State}.gz outputs from TSV_DATA_DIR. """
    with gzip.GzipFile(os.path.join(TSV_DATA_DIR, filename), 'r') as gz_file:
        return json.loads(gz_file.read().decode('utf-8'))


def load_json_maybe_gz(path):
    """ Load a JSON file that may be gzip-compressed (.gz) or plain,
    for pointing --diag_compare_file at either a tsv_load_*.gz output or
    one of the uncompressed json/tsv_load_*_{stock_version}*.json
    intermediates. """
    if path.endswith('.gz'):
        with gzip.GzipFile(path, 'r') as gz_file:
            return json.loads(gz_file.read().decode('utf-8'))
    with open(path, 'r') as f:
        return json.load(f)


def round_floats(obj):
    """ Recursively round floats in a JSON object to 6 decimal places. """
    if isinstance(obj, float):
        return round(obj, 6)
    elif isinstance(obj, dict):
        return {k: round_floats(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [round_floats(i) for i in obj]
    return obj


def findNan(reg, eu, example_list):
    contains_nan = any(
        isinstance(item, float) and np.isnan(item) for item in example_list)
    if contains_nan:
        # print(f"The list contains NaN. {reg} {eu}")
        # print(example_list)
        updated_list = [
            0 if isinstance(item, float) and np.isnan(item) else item
            for item in example_list]
    else:
        # print("The list does not contain NaN.")
        updated_list = example_list
    return updated_list


def insert_scouttsv_emm(opts):
    emm_file = f"{OUTPUT_DIR}/{opts.bstock}_emm_{opts.stock_version}.csv"
    if not os.path.isfile(emm_file):
        return print('File does not exist, please run getdata()')
    emm_shift, _ = _region_tz_shift_hours(
        os.path.join(MAP_DIR, "geo_map.csv"))
    df = pd.read_csv(emm_file)
    if opts.bstock == 'residential':
        values_to_keep = ['Mobile Home', 'Multi-Family with 5+ Units', 'Single-Family Detached']
        df = df[df['building_type'].isin(values_to_keep)]
    if opts.bstock == 'commercial':
        df = df[df['timestamp_hour'] != '2019-01-01 01:00:00.000']

    df = replace_strings_in_dataframe(df, replacements)
    json_file = BASE_TEMPLATE
    if opts.bstock == 'residential':
        json_file = f"{JSON_DIR}/tsv_load_emm_{opts.stock_version}_com.json"
    with open(json_file, "r") as jsi:
        lsjson = json.load(jsi)
    emm_regions = df['emm'].unique()

    for bldg in building_map[opts.bstock]:
        print(f"EMM {bldg}")
        bm_vals = [
            item.split('_', 1)[0] for item in building_map[opts.bstock][bldg]]
        lsh = df[df['building_type'
                    ].str.contains("|".join(bm_vals))]
        for eu in enduse_map[opts.bstock]:
            print(f"  {bldg} - {eu} ({len(emm_regions)} EMM regions)")
            # Whether this (building type, end use) combination is actually
            # kept: nested_set discards commercial combos outside the list
            # below, and MF/MH pool heaters & pumps get overwritten with
            # SF's values further down regardless of what's computed here.
            will_write = (
                opts.bstock == 'residential' and not (
                    bldg in ('MF', 'MH') and
                    eu in ('pool heaters', 'pool pumps'))
            ) or (
                opts.bstock == 'commercial' and (
                    (bldg == 'MediumOfficeDetailed' and eu in (
                        'heating', 'lighting', 'plug loads',
                        'water heating', 'other')) or
                    (bldg == 'LargeHotel' and eu == 'refrigeration') or
                    eu in ('cooling', 'ventilation', 'pumps')))
            for emm in emm_regions:
                es60 = lsh.loc[lsh.loc[:, 'emm'] == emm, eu].to_frame()
                es60 = es60.sum(axis=1)
                es60 = es60 / es60.sum()
                es60 = findNan(emm, eu, es60)

                llen = len(es60)
                if llen != 8760:
                    print(f"{emm} {eu} {llen}")
                    es60 = [0] * 8760

                if will_write and abs(sum(es60) - 1) > 0.01:
                    print(f"""LOAD SHAPE DOESN'T SUM TO ONE! {sum(es60)}
                          for {eu} {emm} {opts.bstock}""")
                # Round to 6 decimals: full float64 precision here is far
                # more than these normalized (sum-to-one) shapes need, and
                # the extra digits are high-entropy noise that gzip can't
                # compress, bloating tsv_load_EMM.gz several-fold for no
                # accuracy benefit.
                es60 = [round(float(v), 6) for v in es60]
                es60 = _apply_tz_shift(es60, emm_shift.get(emm, 0))
                if opts.bstock == 'commercial' and (
                     (bldg == 'MediumOfficeDetailed' and (
                      eu == 'heating' or eu == 'lighting' or
                      eu == 'plug loads' or eu == 'water heating' or
                      eu == 'other')) or
                     (bldg == 'LargeHotel' and eu == 'refrigeration') or
                     eu == 'cooling' or eu == 'ventilation' or eu == 'pumps'):
                    nested_set(lsjson,
                               [opts.bstock, eu, bldg, 'load shape', emm],
                               es60)
                elif opts.bstock == 'residential':
                    nested_set(lsjson,
                               [opts.bstock, eu, bldg,
                                'represented building types'], bldg)
                    nested_set(lsjson,
                               [opts.bstock, eu, bldg, 'load shape', emm],
                               es60)
    if opts.bstock == 'residential':
        # copy values from SF to MF and MH
        poolvars = ['pool heaters', 'pool pumps']
        for p in poolvars:
            vals_replace = lsjson[opts.bstock][p]['SF']['load shape']
            nested_set(lsjson, [
                opts.bstock, p, 'MF', 'load shape'],
                vals_replace)
            nested_set(lsjson, [
                opts.bstock, p, 'MH', 'load shape'],
                vals_replace)
    if opts.bstock == 'residential':
        json.dump(lsjson, open(
            f"{JSON_DIR}/tsv_load_emm_{opts.stock_version}.json", 'w'),
            indent=2)
        write_gzip_json(lsjson, "tsv_load_EMM.gz")
    if opts.bstock == 'commercial':
        json.dump(lsjson, open(
            f"{JSON_DIR}/tsv_load_emm_{opts.stock_version}_com.json", 'w'),
            indent=2)
    print(f"FINISHED INSERT {opts.bstock} data into EMM")


def insert_scouttsv_usstate(opts):
    csv_file = f"{OUTPUT_DIR}/{opts.bstock}_state_{opts.stock_version}.csv"
    if not os.path.isfile(csv_file):
        return print('File does not exist, please run getdata()')
    _, state_shift = _region_tz_shift_hours(
        os.path.join(MAP_DIR, "geo_map.csv"))
    df = pd.read_csv(csv_file)

    if opts.bstock == 'commercial':
        df = df[df['timestamp_hour'] != '2019-01-01 01:00:00.000']
    if opts.bstock == 'residential':
        values_to_keep = ['Mobile Home', 'Multi-Family with 5+ Units', 'Single-Family Detached']
        df = df[df['building_type'].isin(values_to_keep)]

    df = replace_strings_in_dataframe(df, replacements)
    json_file = BASE_TEMPLATE
    if opts.bstock == 'residential':
        json_file = f"{JSON_DIR}/tsv_load_state_{opts.stock_version}_com.json"
    with open(json_file, "r") as jsi:
        lsjson = json.load(jsi)
    us_states = np.unique(df['state'])
    for bldg in building_map[opts.bstock]:
        print(f"State {bldg}")
        bm_vals = [
            item.split('_', 1)[0] for item in building_map[opts.bstock][bldg]]
        lsh = df[df['building_type'
                    ].str.contains("|".join(bm_vals))]
        for eu in enduse_map[opts.bstock]:
            print(f"  {bldg} - {eu} ({len(us_states)} states)")
            # Whether this (building type, end use) combination is actually
            # kept: nested_set discards commercial combos outside the list
            # below, and MF/MH pool heaters & pumps get overwritten with
            # SF's values further down regardless of what's computed here.
            will_write = (
                opts.bstock == 'residential' and not (
                    bldg in ('MF', 'MH') and
                    eu in ('pool heaters', 'pool pumps'))
            ) or (
                opts.bstock == 'commercial' and (
                    (bldg == 'MediumOfficeDetailed' and eu in (
                        'heating', 'lighting', 'plug loads',
                        'water heating', 'other')) or
                    (bldg == 'LargeHotel' and eu == 'refrigeration') or
                    eu in ('cooling', 'ventilation', 'pumps')))
            for state in us_states:
                es60 = lsh.loc[lsh.loc[:, 'state'] == state, eu].to_frame()
                es60 = es60.sum(axis=1)
                es60 = es60 / es60.sum()
                es60 = findNan(state, eu, es60)

                llen = len(es60)
                if llen != 8760:
                    print(f"{state} {eu} {llen}")
                    es60 = [0] * 8760

                if will_write and abs(sum(es60) - 1) > 0.01:
                    print(f"""LOAD SHAPE DOESN'T SUM TO ONE! {sum(es60)}
                          for {eu} {state} {opts.bstock}""")
                # Round to 6 decimals: full float64 precision here is far
                # more than these normalized (sum-to-one) shapes need, and
                # the extra digits are high-entropy noise that gzip can't
                # compress, bloating tsv_load_State.gz several-fold for no
                # accuracy benefit.
                es60 = [round(float(v), 6) for v in es60]
                es60 = _apply_tz_shift(es60, state_shift.get(state, 0))
                if opts.bstock == 'commercial' and (
                     (bldg == 'MediumOfficeDetailed' and (
                      eu == 'heating' or eu == 'lighting' or
                      eu == 'plug loads' or eu == 'water heating' or
                      eu == 'other')) or
                     (bldg == 'LargeHotel' and eu == 'refrigeration') or
                     eu == 'cooling' or eu == 'ventilation' or eu == 'pumps'):
                    nested_set(lsjson,
                               [opts.bstock, eu, bldg, 'load shape', state],
                               es60)
                elif opts.bstock == 'residential':
                    nested_set(lsjson,
                               [opts.bstock, eu, bldg,
                                'represented building types'], bldg)
                    nested_set(lsjson,
                               [opts.bstock, eu, bldg, 'load shape', state],
                               es60)
    if opts.bstock == 'residential':
        # copy values from SF to MF and MH
        poolvars = ['pool heaters', 'pool pumps']
        for p in poolvars:
            vals_replace = lsjson[opts.bstock][p]['SF']['load shape']
            nested_set(lsjson, [
                opts.bstock, p, 'MF', 'load shape'],
                vals_replace)
            nested_set(lsjson, [
                opts.bstock, p, 'MH', 'load shape'],
                vals_replace)
    if opts.bstock == 'residential':
        json.dump(lsjson, open(
            f"{JSON_DIR}/tsv_load_state_{opts.stock_version}.json", 'w'),
            indent=2)
        write_gzip_json(lsjson, "tsv_load_State.gz")
    if opts.bstock == 'commercial':
        json.dump(lsjson, open(
            f"{JSON_DIR}/tsv_load_state_{opts.stock_version}_com.json", 'w'),
            indent=2)
    print(f"FINISHED INSERT {opts.bstock} data into US STATE")


def countrows_eu(opts):
    """ For each (building type, geo) combination, flag cases where the raw
    stock CSV doesn't have exactly one row per hour of the year (8760) or is
    missing specific hours within its own min/max timestamp range. Only
    problems are printed; a clean run prints nothing beyond the header. """
    geodescs = ['emm', 'state']
    btypes = _diag_canonical_building_types(opts.bstock)
    HOURS_PER_YEAR = 8760

    for geodesc in geodescs:
        # geodesc = 'emm'
        file = f"{OUTPUT_DIR}/{opts.bstock}_{geodesc}_{opts.stock_version}.csv"
        if not os.path.isfile(file):
            return print('File does not exist, please run getdata()')
        df = pd.read_csv(file)
        geo_list = df[geodesc].unique()
        n_flagged = 0
        for btype in btypes:
            for geo in geo_list:
                filtered_df = df[
                    (df[geodesc] == geo) &
                    (df['building_type'] == btype)
                ]
                if filtered_df.empty:
                    print(f"{geodesc}={geo} bt={btype}: 0 rows")
                    n_flagged += 1
                    continue
                if len(filtered_df) != HOURS_PER_YEAR:
                    print(f"{geodesc}={geo} bt={btype}: "
                          f"{len(filtered_df)} rows (expected "
                          f"{HOURS_PER_YEAR})")
                    n_flagged += 1

                filtered_df = filtered_df.copy()
                filtered_df['timestamp_hour'] = pd.to_datetime(filtered_df['timestamp_hour'])
                start_time = filtered_df['timestamp_hour'].min()
                end_time = filtered_df['timestamp_hour'].max()
                expected_timestamps = pd.date_range(start=start_time, end=end_time, freq='H')
                actual_timestamps = set(filtered_df['timestamp_hour'])
                missing_timestamps = [ts for ts in expected_timestamps if ts not in actual_timestamps]
                if missing_timestamps:
                    print(f"{geodesc}={geo} bt={btype}: "
                          f"{len(missing_timestamps)} missing timestamps:")
                    for ts in missing_timestamps:
                        print(f"  {ts}")
                    n_flagged += 1
        print(f"{file}: {n_flagged} flagged (geo, building_type) "
              "combination(s) out of "
              f"{len(btypes) * len(geo_list)} checked.")


def check_nan(opts):
    """ Diagnose NaNs in both the raw stock CSVs (step 1 output) and the
    final gzipped load-shape JSON outputs (step 2 output). Ported from
    _diag_length_and_sumtoone.ipynb. NaNs in the raw CSV are expected (they
    get zeroed out by findNan() during --insert_scouttsv); NaNs surviving
    into the final gz would indicate that safeguard failed. """
    for geodesc in ('emm', 'state'):
        csv_file = (f"{OUTPUT_DIR}/{opts.bstock}_{geodesc}_"
                    f"{opts.stock_version}.csv")
        if not os.path.isfile(csv_file):
            print(f"{csv_file} not found, skipping raw-CSV NaN check.")
            continue
        df = pd.read_csv(csv_file)
        nan_cols = df.columns[df.isna().any()].tolist()
        if nan_cols:
            print(f"{csv_file}: columns containing NaN: {nan_cols}")
        else:
            print(f"{csv_file}: no NaN columns.")

    def find_nan_keys(d, parent_key=''):
        found = []
        if isinstance(d, dict):
            for key, value in d.items():
                found += find_nan_keys(
                    value, f"{parent_key}.{key}" if parent_key else key)
        elif isinstance(d, list):
            for i, item in enumerate(d):
                found += find_nan_keys(item, f"{parent_key}[{i}]")
        elif isinstance(d, float) and np.isnan(d):
            found.append(parent_key)
        return found

    for gz_name in ('tsv_load_EMM.gz', 'tsv_load_State.gz'):
        gz_path = os.path.join(TSV_DATA_DIR, gz_name)
        if not os.path.isfile(gz_path):
            print(f"{gz_path} not found, skipping final-JSON NaN check "
                  "(run --insert_scouttsv --bstock residential to produce "
                  "it, since that pass writes the final gz).")
            continue
        nan_keys = find_nan_keys(read_gzip_json(gz_name))
        if nan_keys:
            print(f"{gz_path}: {len(nan_keys)} NaN values found:")
            for k in nan_keys:
                print(f"  {k}")
        else:
            print(f"{gz_path}: no NaN values found.")


def check_sum_and_length(opts):
    """ Verify every load shape in the final gzipped JSON outputs is
    length 8760 and sums to ~1. Ported from
    _diag_length_and_sumtoone.ipynb; unlike the notebook (which printed
    every combination checked), only failing combinations are printed here
    since a full run checks thousands of load shapes. The same sum-to-one
    check already runs inline during --insert_scouttsv (see "LOAD SHAPE
    DOESN'T SUM TO ONE!" there); this re-checks the final gz on demand,
    independent of a fresh insert run. """
    for gz_name in ('tsv_load_EMM.gz', 'tsv_load_State.gz'):
        gz_path = os.path.join(TSV_DATA_DIR, gz_name)
        if not os.path.isfile(gz_path):
            print(f"{gz_path} not found, skipping.")
            continue
        data = read_gzip_json(gz_name)
        n_checked = n_bad = 0
        # Top level also carries non-sectional metadata (start day, DST,
        # leap year, weather basis) alongside the residential/commercial
        # dicts; only descend into the latter.
        for sec in ('residential', 'commercial'):
            sec_v = data.get(sec, {})
            for eu, eu_v in sec_v.items():
                for bt, bt_v in eu_v.items():
                    shapes = bt_v.get('load shape') \
                        if isinstance(bt_v, dict) else None
                    if not shapes:
                        continue
                    for region, shape in shapes.items():
                        n_checked += 1
                        llen = len(shape)
                        total = sum(shape)
                        if llen != 8760 or abs(total - 1) > 0.01:
                            n_bad += 1
                            print(f"{gz_path}: {sec}/{eu}/{bt}/{region} "
                                  f"length={llen} sum={total:.4f}")
        print(f"{gz_path}: checked {n_checked} load shapes, {n_bad} failed "
              "length/sum-to-one checks.")


def _diag_canonical_building_types(bstock):
    """ The subset of raw (pre-`replacements`) building_type values in the
    stock CSVs that update_tsv.py actually keeps, as used elsewhere in this
    script (e.g. insert_scouttsv_emm's values_to_keep filter). """
    if bstock == 'residential':
        return ['Mobile Home', 'Multi-Family with 5+ Units',
                'Single-Family Detached']
    return sum(building_map['commercial'].values(), [])


def plot_peakday_hourly(opts):
    """ For each region, find the winter/summer peak day (highest total
    load day in that season's window) in the raw stock CSV and plot every
    end use's hourly load on that day, one subplot per (end use, building
    type) pair with regions overlaid as separate lines. Saves PNGs to
    DIAG_DIR. Ported from _diag_hourly.ipynb, using the same
    winter/summer windows and duplicate-column-free energy columns as
    compute_peak_days.py (rather than recomputing them). """
    import matplotlib.pyplot as plt

    bts = _diag_canonical_building_types(opts.bstock)
    energy_cols = (RESIDENTIAL_ENERGY_COLS if opts.bstock == 'residential'
                   else COMMERCIAL_ENERGY_COLS)
    os.makedirs(DIAG_DIR, exist_ok=True)

    for geodesc in ('emm', 'state'):
        csv_file = (f"{OUTPUT_DIR}/{opts.bstock}_{geodesc}_"
                    f"{opts.stock_version}.csv")
        if not os.path.isfile(csv_file):
            print(f"{csv_file} not found, skipping peak-day plot.")
            continue
        df = pd.read_csv(csv_file)
        if opts.bstock == 'commercial':
            df = df[df['timestamp_hour'] != '2019-01-01 01:00:00.000']
        df = df[df['building_type'].isin(bts)].copy()
        df['timestamp_hour'] = pd.to_datetime(df['timestamp_hour'])
        df['dayofyear'] = df['timestamp_hour'].dt.dayofyear
        df['total'] = df[energy_cols].sum(axis=1)
        regions = sorted(df[geodesc].unique())

        for season_name, season_days in (
                ('winter', WINTER_DAYS), ('summer', SUMMER_DAYS)):
            season_df = df[df['dayofyear'].isin(season_days)]
            daily = season_df.groupby(
                [geodesc, 'dayofyear'])['total'].sum().reset_index()
            if daily.empty:
                print(f"{csv_file}: no {season_name} data, skipping.")
                continue
            peak_day = daily.loc[
                daily.groupby(geodesc)['total'].idxmax()
            ].set_index(geodesc)['dayofyear']

            # Pre-slice each region's peak-day rows once (one filter pass
            # per region over the full df) rather than re-filtering the
            # full df inside the (end use x building type x region) plot
            # loop below, which is orders of magnitude slower.
            peakday_by_region = {}
            for region in regions:
                if region not in peak_day.index:
                    continue
                region_day_df = df[
                    (df[geodesc] == region) &
                    (df['dayofyear'] == peak_day.loc[region])
                ]
                peakday_by_region[region] = {
                    bt: sub.sort_values('timestamp_hour')
                    for bt, sub in region_day_df.groupby('building_type')}

            nrows, ncols = len(energy_cols), len(bts)
            fig, ax = plt.subplots(
                nrows, ncols, figsize=(ncols * 4, nrows * 2.5),
                sharex=True, sharey=False, squeeze=False)
            for i, eu in enumerate(energy_cols):
                for j, bt in enumerate(bts):
                    axij = ax[i, j]
                    for region, bt_data in peakday_by_region.items():
                        data = bt_data.get(bt)
                        if data is None or data.empty:
                            continue
                        axij.plot(range(len(data)), data[eu], label=region)
                    axij.set_title(f'eu={eu}\nbt={bt}', fontsize=8)
                    if i == nrows - 1:
                        axij.set_xlabel("Hour")
                    if j == 0:
                        axij.set_ylabel("Load [kWh]")
            plt.tight_layout()
            out_path = (f"{DIAG_DIR}/peakday_{opts.bstock[:3]}_"
                        f"{season_name}_{geodesc}.png")
            plt.savefig(out_path, dpi=100, bbox_inches='tight')
            plt.close(fig)
            print(f"{out_path} is successfully saved!")


# A second boundary_trend variant that shows PLOT_EXTRA_BUFFER_DAYS more
# days on both edges than WINTER_DAYS_EXTENDED/SUMMER_DAYS_EXTENDED, purely
# for extra visual context beyond compute_peak_days.py's own
# BOUNDARY_CHECK_BUFFER_DAYS (which drives the flagging logic and stays
# unchanged here).
PLOT_EXTRA_BUFFER_DAYS = 30
_WIDE_BUFFER_DAYS = BOUNDARY_CHECK_BUFFER_DAYS + PLOT_EXTRA_BUFFER_DAYS
WINTER_DAYS_WIDE = (
    set(range(1, 91 + _WIDE_BUFFER_DAYS)) |
    set(range(335 - _WIDE_BUFFER_DAYS, 366)))
SUMMER_DAYS_WIDE = set(range(
    152 - _WIDE_BUFFER_DAYS, 274 + _WIDE_BUFFER_DAYS))


def plot_boundary_trend(opts):
    """ For each region, plot the day-by-day trend of the combined
    (commercial + residential) load's daily max hourly value across a
    widened season window, to show directly whether a region's official
    winter/summer peak day is an interior local max or an artifact of the
    window edge — i.e. to visualize compute_peak_days.py's
    PeakAtWindowBoundary flag rather than just take its word for it.
    Unlike the other --diag plots, this always combines both building
    sectors to match compute_peak_days.py's own methodology, so it ignores
    --bstock and needs both raw commercial/residential CSVs cached.

    Two variants are saved per season/geography: the default (matching
    compute_peak_days.py's own BOUNDARY_CHECK_BUFFER_DAYS window) and a
    "_wide" version extended by another PLOT_EXTRA_BUFFER_DAYS on both
    edges, for cases where even the default window doesn't show enough of
    the curve to tell a real local max from a still-rising edge. """
    import matplotlib.pyplot as plt
    from matplotlib import colormaps

    os.makedirs(DIAG_DIR, exist_ok=True)
    # variant_suffix -> {season_name: day-of-year set to plot}
    window_variants = [
        ("", {"Winter": WINTER_DAYS_EXTENDED, "Summer": SUMMER_DAYS_EXTENDED}),
        ("_wide", {"Winter": WINTER_DAYS_WIDE, "Summer": SUMMER_DAYS_WIDE}),
    ]
    # Official window start/end day(s) a still-rising curve would be
    # artificially cut off at (see WINTER_DAYS/SUMMER_DAYS in
    # compute_peak_days.py). Winter is defined as day 1-90 plus day
    # 335-365, which — on the shifted x-axis below — is one continuous
    # span from day 335 (x=-30) to day 90 (x=90), so those are its two
    # edges; summer is a single day 152-273 span.
    official_edges = {"Winter": [335, 90], "Summer": [152, 273]}

    for geodesc in ('emm', 'state'):
        try:
            combined = load_combined_hourly(
                geodesc, geodesc, opts.stock_version)
        except FileNotFoundError as e:
            print(f"{e}, skipping boundary-trend plot.")
            continue
        combined = combined.copy()
        combined['dayofyear'] = pd.to_datetime(
            combined['timestamp_hour']).dt.dayofyear
        peaks = find_peak_days(combined, geodesc, keep_extended=True)
        regions = sorted(combined[geodesc].unique())
        # 'hsv' cycles hue at constant saturation/value, so no line ends up
        # near-white (invisible on this white background) or near-black
        # (indistinguishable from the axes/text) the way sequential-looking
        # colormaps like 'gist_ncar' do at their endpoints. Sample at
        # i/n rather than i/(n-1) (what .resampled() does) since hsv wraps
        # (hue 0 == hue 1 == red), which would otherwise put near-duplicate
        # colors on the first and last region.
        hsv = colormaps['hsv']
        colors = [hsv(i / len(regions)) for i in range(len(regions))]

        for variant_suffix, windows in window_variants:
            for season_name, ext_days in windows.items():
                # Shift winter's wraparound days (335-365) to negative x
                # values so its two disjoint day-of-year blocks plot as one
                # continuous trend leading up to the year boundary;
                # summer's window is already contiguous, so this is a
                # no-op there.
                def to_x(d, season_name=season_name):
                    return d - 365 if (
                        season_name == "Winter" and d > 200) else d

                season_df = combined[combined['dayofyear'].isin(ext_days)]
                daily_max = season_df.groupby(
                    [geodesc, 'dayofyear'])['total'].max().reset_index()
                daily_max['x'] = daily_max['dayofyear'].apply(to_x)
                flag_col = f"{season_name}PeakAtWindowBoundary"
                flagged_regions = sorted(
                    peaks.loc[peaks[flag_col], geodesc])

                def _draw(region_subset, out_suffix, title_extra):
                    fig, ax = plt.subplots(figsize=(11, 6))
                    for region in region_subset:
                        i = regions.index(region)
                        rdat = daily_max[
                            daily_max[geodesc] == region].sort_values('x')
                        if rdat.empty:
                            continue
                        color = colors[i]
                        ax.plot(rdat['x'], rdat['total'], color=color,
                                linewidth=1, label=region)
                        prow = peaks[peaks[geodesc] == region]
                        if prow.empty:
                            continue
                        peak_day = prow[f"{season_name}PeakDay"].iloc[0]
                        peak_load = prow[f"{season_name}PeakLoad"].iloc[0]
                        is_flagged = prow[flag_col].iloc[0]
                        # Circle = official (window-constrained) peak —
                        # always shown, this is what's actually in
                        # tsv_peak_days_{EMM,State}.csv
                        ax.plot(
                            to_x(peak_day), peak_load, marker='o',
                            markersize=6, markeredgecolor='black',
                            markerfacecolor=color, zorder=5)
                        # Star = the higher peak a widened window finds —
                        # only meaningfully different from the circle when
                        # flagged (otherwise it's the same point, so skip)
                        if is_flagged:
                            ext_day = prow[
                                f"{season_name}ExtendedPeakDay"].iloc[0]
                            ext_load = prow[
                                f"{season_name}ExtendedPeakLoad"].iloc[0]
                            ax.plot(
                                to_x(ext_day), ext_load, marker='*',
                                markersize=16, markeredgecolor='black',
                                markerfacecolor=color, zorder=5)

                    for edge in official_edges[season_name]:
                        ax.axvline(
                            to_x(edge), color='black', linestyle='--',
                            linewidth=1, alpha=0.6)
                    ax.set_xlabel(
                        "Day of year (winter's Nov-Dec block shown as "
                        "negative days before Jan 1)"
                        if season_name == "Winter" else "Day of year")
                    ax.set_ylabel("Daily max hourly total load [kWh]")
                    ax.set_title(textwrap.fill(
                        f"{season_name} season daily max hourly load by "
                        f"region ({geodesc}){title_extra}. Dashed = "
                        "official window start/end. Circle = official "
                        "(in-window) peak. Star = higher peak found by a "
                        "widened window (only shown when flagged as a "
                        "boundary artifact).", width=100))
                    ax.legend(fontsize=6, ncol=3, loc='center left',
                              bbox_to_anchor=(1.0, 0.5))
                    plt.tight_layout()
                    out_path = (f"{DIAG_DIR}/boundary_trend_"
                                f"{season_name.lower()}_{geodesc}"
                                f"{variant_suffix}{out_suffix}.png")
                    plt.savefig(out_path, dpi=100, bbox_inches='tight')
                    plt.close(fig)
                    print(f"{out_path} is successfully saved!")

                _draw(regions, "", "")
                if flagged_regions:
                    _draw(
                        flagged_regions, "_flagged_only",
                        f" — flagged regions only ({len(flagged_regions)}"
                        f" of {len(regions)})")
                else:
                    print(f"No {season_name.lower()}/{geodesc}"
                          f"{variant_suffix} regions flagged as "
                          "window-boundary artifacts, skipping "
                          "flagged-only plot.")


def plot_annual_fraction(opts):
    """ Plot cumulative fraction of annual load consumed per (end use,
    building type), one line per region, from the final gzipped
    load-shape JSON. Saves PNGs to DIAG_DIR. Ported from
    _diag_annual_fraction.ipynb (grid size there was hardcoded per bstock;
    here it's sized dynamically from what's actually in the JSON). """
    import matplotlib.pyplot as plt

    os.makedirs(DIAG_DIR, exist_ok=True)
    for geodesc, gz_name in (
            ('emm', 'tsv_load_EMM.gz'), ('state', 'tsv_load_State.gz')):
        gz_path = os.path.join(TSV_DATA_DIR, gz_name)
        if not os.path.isfile(gz_path):
            print(f"{gz_path} not found, skipping annual-fraction plot.")
            continue
        sec_data = read_gzip_json(gz_name).get(opts.bstock, {})
        combos = [(eu, bt) for eu, eu_v in sec_data.items() for bt in eu_v]
        if not combos:
            print(f"{gz_path}: no {opts.bstock} data, skipping.")
            continue
        ncols = 4
        nrows = -(-len(combos) // ncols)
        fig, ax = plt.subplots(
            nrows, ncols, figsize=(ncols * 4, nrows * 3),
            sharex=True, sharey=True, squeeze=False)
        for idx, (eu, bt) in enumerate(combos):
            i, j = divmod(idx, ncols)
            shapes = sec_data[eu][bt].get('load shape', {})
            for region, vals in shapes.items():
                ax[i, j].plot(np.cumsum(vals), label=region)
            ax[i, j].set_title(f'eu={eu}\nbt={bt}', fontsize=16)
            if i == nrows - 1:
                ax[i, j].set_xlabel("Hour of Year")
        for idx in range(len(combos), nrows * ncols):
            i, j = divmod(idx, ncols)
            ax[i, j].axis('off')
        # One shared y-axis label spanning all facet rows, instead of
        # repeating it on every row's leftmost facet.
        fig.text(
            0.02, 0.5, "Fraction Annual Load Consumed", va='center',
            ha='center', rotation='vertical', fontsize=18)
        plt.tight_layout(rect=(0.03, 0, 1, 1))
        out_path = (f"{DIAG_DIR}/annual_fraction_{opts.bstock[:3]}_"
                    f"{geodesc}.png")
        plt.savefig(out_path, dpi=100, bbox_inches='tight')
        plt.close(fig)
        print(f"{out_path} is successfully saved!")


def plot_annual_fraction_by_building(opts):
    """ Plot cumulative fraction of annual load consumed for each (end use,
    region) combination, one line per building type, from the final
    gzipped load-shape JSON. This is the same underlying data as
    `plot_annual_fraction`, just transposed: rows are end uses, columns
    are a handful of representative regions, and building type is the
    hue — matching the style of the DOE Commercial Reference Buildings
    cumulative-load-shape figure used elsewhere for reference. Unlike
    that figure's ~16 DOE prototype buildings, this only has as many
    lines as `building_map[opts.bstock]` (e.g. 5 for commercial), since
    `insert_scouttsv_emm`/`insert_scouttsv_usstate` only keep
    building-type-specific shapes for end uses where they meaningfully
    differ (cooling/ventilation/pumps for commercial); the rest share one
    representative building type's shape, so those rows show a single
    line. Saves PNGs to DIAG_DIR. """
    import matplotlib.pyplot as plt

    os.makedirs(DIAG_DIR, exist_ok=True)
    for geodesc, gz_name in (
            ('emm', 'tsv_load_EMM.gz'), ('state', 'tsv_load_State.gz')):
        gz_path = os.path.join(TSV_DATA_DIR, gz_name)
        if not os.path.isfile(gz_path):
            print(f"{gz_path} not found, skipping annual-fraction-by-"
                  "building-type plot.")
            continue
        sec_data = read_gzip_json(gz_name).get(opts.bstock, {})
        if not sec_data:
            print(f"{gz_path}: no {opts.bstock} data, skipping.")
            continue

        if opts.diag_enduses:
            end_uses = [eu for eu in opts.diag_enduses if eu in sec_data]
            missing = set(opts.diag_enduses) - set(end_uses)
            if missing:
                print(f"{gz_path}: requested end use(s) {sorted(missing)} "
                      "not found among available end uses, skipping those.")
        else:
            end_uses = list(sec_data.keys())
        if not end_uses:
            print(f"{gz_path}: no valid end uses to plot, skipping.")
            continue

        all_regions = sorted({
            region for eu, eu_v in sec_data.items() if eu in end_uses
            for bt_v in eu_v.values()
            for region in bt_v.get('load shape', {})})
        if opts.diag_regions:
            regions = [r for r in opts.diag_regions if r in all_regions]
            missing = set(opts.diag_regions) - set(regions)
            if missing:
                print(f"{gz_path}: requested region(s) {sorted(missing)} "
                      "not found among available regions, skipping those.")
        else:
            # No regions specified: auto-pick a handful spread evenly
            # across the sorted region list so the grid stays readable
            # without requiring climate-zone knowledge up front.
            n = min(3, len(all_regions))
            idxs = np.linspace(
                0, len(all_regions) - 1, n).round().astype(int)
            regions = sorted({all_regions[i] for i in idxs})
        if not regions:
            print(f"{gz_path}: no valid regions to plot, skipping.")
            continue
        print(f"{gz_path}: plotting regions {regions}")

        nrows, ncols = len(end_uses), len(regions)
        fig, ax = plt.subplots(
            nrows, ncols, figsize=(ncols * 7, nrows * 6),
            sharex=True, sharey=True, squeeze=False)
        building_types = sorted({
            bt for eu in end_uses for bt in sec_data[eu]})
        bt_colors = dict(zip(
            building_types,
            plt.cm.tab10(np.linspace(0, 1, len(building_types)))))

        for i, eu in enumerate(end_uses):
            # Multi-word end use names (e.g. "water heating") wrap onto a
            # second line at large font sizes rather than overflowing.
            eu_label = eu.replace(' ', '\n') if ' ' in eu else eu
            for j, region in enumerate(regions):
                for bt, bt_v in sec_data[eu].items():
                    vals = bt_v.get('load shape', {}).get(region)
                    if vals is None:
                        continue
                    ax[i, j].plot(
                        np.cumsum(vals), label=bt, color=bt_colors[bt],
                        linewidth=1.5)
                ax[i, j].tick_params(labelsize=34)
                if i == 0:
                    ax[i, j].set_title(region, fontsize=50)
                if i == nrows - 1:
                    ax[i, j].set_xlabel("Hour of Year", fontsize=42)
                if j == 0:
                    ax[i, j].set_ylabel(eu_label, fontsize=46)
        handles = [
            plt.Line2D([0], [0], color=bt_colors[bt], label=bt)
            for bt in building_types]
        fig.legend(
            handles=handles, loc='center left', bbox_to_anchor=(1.0, 0.5),
            fontsize=40, title="Building Type",
            title_fontsize=44)
        plt.tight_layout()
        out_path = (f"{DIAG_DIR}/annual_fraction_by_bldgtype_"
                    f"{opts.bstock[:3]}_{geodesc}.png")
        plt.savefig(out_path, dpi=100, bbox_inches='tight')
        plt.close(fig)
        print(f"{out_path} is successfully saved!")


# Day-of-year (0-indexed) that each representative month starts on, and
# each month's length; used by plot_seasonal_factors to pull out weekday
# hourly averages for Jan/Apr/Jul/Oct without loading a full calendar lib.
_SEASONAL_MONTH_STARTS = {
    'January': 0,
    'April': 31 + 28 + 31,
    'July': 31 + 28 + 31 + 30 + 31,
    'October': 31 + 28 + 31 + 30 + 31 + 30 + 31 + 31 + 30,
}
_SEASONAL_MONTH_DAYS = {
    'January': 31, 'April': 30, 'July': 31, 'October': 31}


def _weekday_hourly_avg(values, month_start_hour, days_in_month):
    """ Average hourly profile (24 values) across the weekdays (Mon-Fri)
    of a `days_in_month`-day block starting at `month_start_hour`. Assumes
    values[] starts on a Monday (true for 2018, the ComStock/ResStock AMY
    year), matching _diag_factorsplot.ipynb's day-of-week assumption. """
    month_start_day = month_start_hour // 24
    hourly = np.array(
        values[month_start_hour:month_start_hour + days_in_month * 24]
    ).reshape(-1, 24)
    weekday_mask = [
        (month_start_day + d) % 7 < 5 for d in range(days_in_month)]
    return hourly[weekday_mask].mean(axis=0)


def plot_seasonal_factors(opts):
    """ Plot weekday-average hourly load shape for Jan/Apr/Jul/Oct, one
    line per region, for every (end use, building type) present in the
    final gzipped JSON. Saves PNGs to DIAG_DIR. If opts.diag_compare_file
    is given, overlay that file's mean +/- 1 std dev across regions for a
    before/after comparison. Ported from _diag_factorsplot.ipynb
    (draw_plot/compare_plot), generalized to iterate every combination
    present instead of a hardcoded call list. """
    import matplotlib.pyplot as plt

    os.makedirs(DIAG_DIR, exist_ok=True)
    compare_data = (
        load_json_maybe_gz(opts.diag_compare_file)
        if opts.diag_compare_file else None)

    for geodesc, gz_name in (
            ('emm', 'tsv_load_EMM.gz'), ('state', 'tsv_load_State.gz')):
        gz_path = os.path.join(TSV_DATA_DIR, gz_name)
        if not os.path.isfile(gz_path):
            print(f"{gz_path} not found, skipping seasonal-factor plot.")
            continue
        sec_data = read_gzip_json(gz_name).get(opts.bstock, {})
        n_saved = 0
        for eu, eu_v in sec_data.items():
            for bt, bt_v in eu_v.items():
                shapes = bt_v.get('load shape', {})
                if not shapes:
                    continue
                cmp_shapes = {}
                if compare_data:
                    cmp_shapes = compare_data.get(
                        opts.bstock, {}).get(eu, {}).get(bt, {}).get(
                        'load shape', {})

                fig, axs = plt.subplots(1, 4, figsize=(20, 4), sharey=True)
                for idx, (month_name, month_start_day) in enumerate(
                        _SEASONAL_MONTH_STARTS.items()):
                    month_start_hour = month_start_day * 24
                    days = _SEASONAL_MONTH_DAYS[month_name]
                    for region, vals in shapes.items():
                        avg = _weekday_hourly_avg(
                            vals, month_start_hour, days)
                        axs[idx].plot(avg, label=region, linewidth=0.8)
                    if cmp_shapes:
                        mat = np.array([
                            _weekday_hourly_avg(v, month_start_hour, days)
                            for v in cmp_shapes.values()])
                        mean, std = mat.mean(axis=0), mat.std(axis=0)
                        axs[idx].plot(mean, '--', color='black',
                                      label='compare mean', linewidth=1.5)
                        axs[idx].fill_between(
                            range(24), mean - std, mean + std,
                            color='black', alpha=0.15)
                    axs[idx].set_title(month_name)
                    axs[idx].set_xlabel('Hour of Day')
                    axs[idx].set_xticks(np.arange(0, 24, 4))
                    axs[idx].grid(True)
                    if idx == 0:
                        axs[idx].set_ylabel('Fraction')
                handles, labels = axs[-1].get_legend_handles_labels()
                fig.legend(handles, labels, fontsize=6, ncol=3,
                           loc='center left', bbox_to_anchor=(1.0, 0.5))
                plt.suptitle(f'{opts.bstock} / {eu} / {bt} ({geodesc})')
                plt.tight_layout()
                out_path = (f"{DIAG_DIR}/seasonal_{opts.bstock[:3]}_"
                            f"{geodesc}_{eu.replace(' ', '')}_{bt}.png")
                plt.savefig(out_path, dpi=100, bbox_inches='tight')
                plt.close(fig)
                n_saved += 1
        print(f"{n_saved} seasonal-factor plots for {opts.bstock}/"
              f"{geodesc} saved to {DIAG_DIR}/")


def main(base_dir):

    if opts.get_stockdata is True:
        session = boto3.Session()
        s3_client = session.client('s3')
        athena_client = session.client('athena')
        print("Uploading geo_map.csv and creating Athena table...")
        s3_create_tables_from_csv(
            s3_client, athena_client, MAP_DIR, "geo_map.csv")
        # RUN the SQL queries directly on AWS Athena, as using Python may
        # risk losing datapoints due to connection issues.
        # The four queries are independent (different sources, different
        # output files), so run them concurrently instead of waiting on
        # each one in turn; boto3 clients are thread-safe for API calls.
        # out_name matches the {bstock}_{emm|state}_{version}.csv naming
        # that insert_scouttsv_emm/usstate expect. The version is baked
        # into the filename so switching --stock_version can't silently
        # reuse a CSV cached from a different release.
        sql_files = [("comstock_data_emm.sql", "commercial_emm"),
                     ("resstock_data_emm.sql", "residential_emm"),
                     ("comstock_data_state.sql", "commercial_state"),
                     ("resstock_data_state.sql", "residential_state")]
        print(f"Running {len(sql_files)} Athena queries concurrently "
              f"against the {opts.stock_version} release: "
              f"{', '.join(f for f, _ in sql_files)}")
        with ThreadPoolExecutor(max_workers=len(sql_files)) as executor:
            futures = [executor.submit(
                sql_to_csvout, s3_client, athena_client, f,
                opts.stock_version, f"{out_name}_{opts.stock_version}")
                for f, out_name in sql_files]
            for future in futures:
                future.result()

    if opts.insert_scouttsv is True:
        # python update_tsv.py --insert_scouttsv --bstock residential
        if opts.bstock in ['commercial', 'residential']:
            print(f"Inserting {opts.bstock} data into EMM regions...")
            insert_scouttsv_emm(opts)
            print(f"Inserting {opts.bstock} data into US states...")
            insert_scouttsv_usstate(opts)
        else:
            print('Missing correct arguments')
    if opts.diag is True:
        diag_types = set(opts.diag_type)
        if 'all' in diag_types:
            diag_types = {'rowcount', 'nan', 'sumcheck', 'peakday_plot',
                          'annual_plot', 'annual_by_bldg_plot',
                          'seasonal_plot', 'boundary_trend'}
        # boundary_trend always combines both commercial and residential
        # raw CSVs (to match compute_peak_days.py's own methodology), so
        # unlike the other diag types it doesn't need --bstock
        if 'boundary_trend' in diag_types:
            plot_boundary_trend(opts)
        if opts.bstock in ['commercial', 'residential']:
            if 'rowcount' in diag_types:
                countrows_eu(opts)
            if 'nan' in diag_types:
                check_nan(opts)
            if 'sumcheck' in diag_types:
                check_sum_and_length(opts)
            if 'peakday_plot' in diag_types:
                plot_peakday_hourly(opts)
            if 'annual_plot' in diag_types:
                plot_annual_fraction(opts)
            if 'annual_by_bldg_plot' in diag_types:
                plot_annual_fraction_by_building(opts)
            if 'seasonal_plot' in diag_types:
                plot_seasonal_factors(opts)
        elif diag_types - {'boundary_trend'}:
            print('Missing correct arguments')


if __name__ == '__main__':
    start_time = time.time()
    parser = ArgumentParser()
    parser.add_argument("--test", action="store_true",
                        help="test")

    parser.add_argument("--get_stockdata", action="store_true",
                        help="Get data from NREL data lake")
    parser.add_argument("--insert_scouttsv", action="store_true",
                        help="Insert stock data to tsv_load.json")
    parser.add_argument("--diag", action="store_true",
                        help="diagnose downloaded data")
    parser.add_argument("--diag_type", nargs="+", default=["all"],
                        choices=["rowcount", "nan", "sumcheck",
                                 "peakday_plot", "annual_plot",
                                 "annual_by_bldg_plot", "seasonal_plot",
                                 "boundary_trend", "all"],
                        help="Which diagnostic(s) to run under --diag "
                        "(default: all). rowcount/nan/sumcheck print "
                        "text reports; peakday_plot/annual_plot/"
                        "annual_by_bldg_plot/seasonal_plot/boundary_trend "
                        "save PNGs to diagnostics/. annual_by_bldg_plot "
                        "is annual_plot transposed: rows are end uses, "
                        "columns are regions (see --diag_regions), lines "
                        "are building types. boundary_trend always "
                        "combines commercial + residential (matching "
                        "compute_peak_days.py) and doesn't need --bstock; "
                        "the others require --bstock.")
    parser.add_argument("--diag_compare_file", type=str, default=None,
                        help="Path to an older tsv_load_*.gz/.json file "
                        "to overlay on seasonal_plot as a before/after "
                        "comparison (mean +/- 1 std dev across regions).")
    parser.add_argument("--diag_regions", nargs="+", default=None,
                        help="Region codes (EMM regions or state "
                        "abbreviations, matching whichever gzipped file "
                        "is being read) to use as the columns in "
                        "annual_by_bldg_plot. Defaults to 3 regions "
                        "spread evenly across the sorted region list.")
    parser.add_argument("--diag_enduses", nargs="+", default=None,
                        help="End use names (matching keys in the "
                        "gzipped load-shape JSON, e.g. 'cooling', "
                        "'plug loads') to use as the rows in "
                        "annual_by_bldg_plot, in the given order. "
                        "Defaults to all end uses present.")
    parser.add_argument("--bstock", type=str,
                        help="Determine building stock ")
    parser.add_argument("--stock_version", type=str, default="2025",
                        choices=list(STOCK_RELEASES.keys()),
                        help="ComStock/ResStock release year to query "
                        "(2025 = ComStock 2025.3/ResStock 2025.1, "
                        "2024 = ComStock 2024.2/ResStock 2024.2). "
                        "Defaults to 2025.")
    opts = parser.parse_args()
    base_dir = getcwd()
    main(base_dir)
    hours, rem = divmod(time.time() - start_time, 3600)
    minutes, seconds = divmod(rem, 60)
    print("--- Overall Runtime: %s (HH:MM:SS.mm) ---" %
          "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))
