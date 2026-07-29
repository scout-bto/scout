import pandas as pd
import boto3
import json
import gzip
import datetime
import numpy as np
import warnings
import time
import os
from os import getcwd
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor

warnings.filterwarnings('ignore')
MAP_DIR = "map"
SQL_DIR = "sql"
OUTPUT_DIR = "csv"
JSON_DIR = "json"
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


def insert_scouttsv_emm0(opts):
    emm_file = f"{OUTPUT_DIR}/{opts.bstock}_emm.csv"
    if not os.path.isfile(emm_file):
        return print('File does not exist, please run getdata()')
    df = pd.read_csv(emm_file)
    if opts.bstock == 'residential':
        values_to_keep = ['Mobile Home', 'Multi-Family with 5+ Units', 'Single-Family Detached']
        df = df[df['building_type'].isin(values_to_keep)]
    if opts.bstock == 'commercial':
        df = df[df['timestamp_hour'] != '2019-01-01 01:00:00.000']

    df = replace_strings_in_dataframe(df, replacements)
    json_file = BASE_TEMPLATE
    if opts.bstock == 'residential':
        json_file = f"{JSON_DIR}/tsv_load_emm_2024_com.json"
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
            for emm in emm_regions:
                es60 = lsh.loc[lsh.loc[:, 'emm'] == emm, eu].to_frame()
                es60 = es60.sum(axis=1)
                es60 = es60 / es60.sum()
                es60 = findNan(emm, eu, es60)

                llen = len(es60)
                if llen != 8760:
                    print(f"{emm} {eu} {llen}")
                    es60 = [0] * 8760

                if abs(sum(es60) - 1) > 0.01:
                    print(f"""LOAD SHAPE DOESN'T SUM TO ONE! {sum(es60)}
                          for {eu} {emm} {opts.bstock}""")
                # es60 = round_floats(es60)
                if opts.bstock == 'commercial' and (
                     (bldg == 'MediumOfficeDetailed' and (
                      eu == 'heating' or eu == 'lighting' or
                      eu == 'plug loads' or eu == 'water heating' or
                      eu == 'other')) or
                     (bldg == 'LargeHotel' and eu == 'refrigeration') or
                     eu == 'cooling' or eu == 'ventilation' or eu == 'pumps'):
                    nested_set(lsjson,
                               [opts.bstock, eu, bldg, 'load shape', emm],
                               list(es60))
                elif opts.bstock == 'residential':
                    nested_set(lsjson,
                               [opts.bstock, eu, bldg,
                                'represented building types'], bldg)
                    nested_set(lsjson,
                               [opts.bstock, eu, bldg, 'load shape', emm],
                               list(es60))
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
            f"{JSON_DIR}/tsv_load_emm_2024.json", 'w'), indent=2)
    if opts.bstock == 'commercial':
        json.dump(lsjson, open(
            f"{JSON_DIR}/tsv_load_emm_2024_com.json", 'w'), indent=2)
    print(f"FINISHED INSERT {opts.bstock} data into EMM")


def insert_scouttsv_usstate0(opts):
    csv_file = f"{OUTPUT_DIR}/{opts.bstock}_state.csv"
    if not os.path.isfile(csv_file):
        return print('File does not exist, please run getdata()')
    df = pd.read_csv(csv_file)

    if opts.bstock == 'commercial':
        df = df[df['timestamp_hour'] != '2019-01-01 01:00:00.000']
    if opts.bstock == 'residential':
        values_to_keep = ['Mobile Home', 'Multi-Family with 5+ Units', 'Single-Family Detached']
        df = df[df['building_type'].isin(values_to_keep)]

    df = replace_strings_in_dataframe(df, replacements)
    json_file = BASE_TEMPLATE
    if opts.bstock == 'residential':
        json_file = f"{JSON_DIR}/tsv_load_state_2024_com.json"
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
            for state in us_states:
                es60 = lsh.loc[lsh.loc[:, 'state'] == state, eu].to_frame()
                es60 = es60.sum(axis=1)
                es60 = es60 / es60.sum()
                es60 = findNan(state, eu, es60)

                llen = len(es60)
                if llen != 8760:
                    print(f"{state} {eu} {llen}")
                    es60 = [0] * 8760

                if abs(sum(es60) - 1) > 0.01:
                    print(f"""LOAD SHAPE DOESN'T SUM TO ONE! {sum(es60)}
                          for {eu} {state} {opts.bstock}""")
                # es60 = round_floats(es60)
                if opts.bstock == 'commercial' and (
                     (bldg == 'MediumOfficeDetailed' and (
                      eu == 'heating' or eu == 'lighting' or
                      eu == 'plug loads' or eu == 'water heating' or
                      eu == 'other')) or
                     (bldg == 'LargeHotel' and eu == 'refrigeration') or
                     eu == 'cooling' or eu == 'ventilation' or eu == 'pumps'):
                    nested_set(lsjson,
                               [opts.bstock, eu, bldg, 'load shape', state],
                               list(es60))
                elif opts.bstock == 'residential':
                    nested_set(lsjson,
                               [opts.bstock, eu, bldg,
                                'represented building types'], bldg)
                    nested_set(lsjson,
                               [opts.bstock, eu, bldg, 'load shape', state],
                               list(es60))
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
            f"{JSON_DIR}/tsv_load_state_2024.json", 'w'), indent=2)
    if opts.bstock == 'commercial':
        json.dump(lsjson, open(
            f"{JSON_DIR}/tsv_load_state_2024_com.json", 'w'), indent=2)
    print(f"FINISHED INSERT {opts.bstock} data into US STATE")


def insert_scouttsv_emm(opts):
    emm_file = f"{OUTPUT_DIR}/{opts.bstock}_emm_{opts.stock_version}.csv"
    if not os.path.isfile(emm_file):
        return print('File does not exist, please run getdata()')
    df = pd.read_csv(emm_file)
    if opts.bstock == 'residential':
        values_to_keep = ['Mobile Home', 'Multi-Family with 5+ Units', 'Single-Family Detached']
        df = df[df['building_type'].isin(values_to_keep)]
    if opts.bstock == 'commercial':
        df = df[df['timestamp_hour'] != '2019-01-01 01:00:00.000']

    df = replace_strings_in_dataframe(df, replacements)
    json_file = BASE_TEMPLATE
    if opts.bstock == 'residential':
        json_file = f"{JSON_DIR}/tsv_load_emm_2024_com.json"
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
            f"{JSON_DIR}/tsv_load_emm_2024.json", 'w'), indent=2)
        write_gzip_json(lsjson, "tsv_load_EMM.gz")
    if opts.bstock == 'commercial':
        json.dump(lsjson, open(
            f"{JSON_DIR}/tsv_load_emm_2024_com.json", 'w'), indent=2)
    print(f"FINISHED INSERT {opts.bstock} data into EMM")


def insert_scouttsv_usstate(opts):
    csv_file = f"{OUTPUT_DIR}/{opts.bstock}_state_{opts.stock_version}.csv"
    if not os.path.isfile(csv_file):
        return print('File does not exist, please run getdata()')
    df = pd.read_csv(csv_file)

    if opts.bstock == 'commercial':
        df = df[df['timestamp_hour'] != '2019-01-01 01:00:00.000']
    if opts.bstock == 'residential':
        values_to_keep = ['Mobile Home', 'Multi-Family with 5+ Units', 'Single-Family Detached']
        df = df[df['building_type'].isin(values_to_keep)]

    df = replace_strings_in_dataframe(df, replacements)
    json_file = BASE_TEMPLATE
    if opts.bstock == 'residential':
        json_file = f"{JSON_DIR}/tsv_load_state_2024_com.json"
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
            f"{JSON_DIR}/tsv_load_state_2024.json", 'w'), indent=2)
        write_gzip_json(lsjson, "tsv_load_State.gz")
    if opts.bstock == 'commercial':
        json.dump(lsjson, open(
            f"{JSON_DIR}/tsv_load_state_2024_com.json", 'w'), indent=2)
    print(f"FINISHED INSERT {opts.bstock} data into US STATE")


def countrows_eu(opts):
    geodescs = ['emm', 'state']
    btype = 'Single-Family Detached' if opts.bstock == 'residential' else 'FullServiceRestaurant'

    for geodesc in geodescs:
        # geodesc = 'emm'
        file = f"{OUTPUT_DIR}/{opts.bstock}_{geodesc}_{opts.stock_version}.csv"
        if not os.path.isfile(file):
            return print('File does not exist, please run getdata()')
        df = pd.read_csv(file)
        geo_list = df[geodesc].unique()
        for geo in geo_list:
            filtered_df = df[
                (df[geodesc] == geo) &
                (df['building_type'] == btype)
            ]
            print(f"{geo} | {len(filtered_df)}")

            # if geo == 'BASN':
            filtered_df['timestamp_hour'] = pd.to_datetime(filtered_df['timestamp_hour'])
            start_time = filtered_df['timestamp_hour'].min()
            end_time = filtered_df['timestamp_hour'].max()
            # print(f"{start_time} {end_time}")
            expected_timestamps = pd.date_range(start=start_time, end=end_time, freq='H')
            actual_timestamps = set(filtered_df['timestamp_hour'])
            missing_timestamps = [ts for ts in expected_timestamps if ts not in actual_timestamps]
            if missing_timestamps:
                print("Missing timestamps:")
                for ts in missing_timestamps:
                    print(ts)
            else:
                print("No missing timestamps found.")


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
        if opts.bstock in ['commercial', 'residential']:
            countrows_eu(opts)


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
