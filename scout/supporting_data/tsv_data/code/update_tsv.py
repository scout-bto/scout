import pandas as pd
import boto3
import json
import datetime
import numpy as np
import warnings
import time
from botocore import UNSIGNED
from botocore.config import Config
import os
from os import getcwd
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.ticker as mticker

warnings.filterwarnings('ignore')
MAP_DIR = "map"
SQL_DIR = "sql"
OUTPUT_DIR = "csv"
JSON_DIR = "json"
EXTERNAL_S3_DIR = "datasets"
DATABASE_NAME = "euss_oedi"
BUCKET_NAME = 'handibucket'


building_map = {
    "commercial": {
        "MediumOfficeDetailed": ["MediumOffice"],
        "LargeOfficeDetailed": ["LargeOffice"],
        "LargeHotel": ["LargeHotel"],
        "RetailStandalone": ["RetailStandalone"],
        "Warehouse": ["Warehouse"]
        },
    "residential": {
        "MF": ['multi-family_with_5plus_units'],
               #'multi-family_with_2_-_4_units'],
        "SF": ['single-family_detached'],
               # 'single-family_attached'],
        "MH": ['mobile_home', 'mobile home']
    }}


enduse_map = {
    "commercial": ["heating","cooling","pumps","ventilation","water heating",
                   "lighting", "refrigeration", "cooking", "PCs", 
                   "non-PC office equipment", "plug loads"],
    "residential": ["heating", "cooling", "water heating", "cooking", "drying",
                    "lighting", "refrigeration", "ceiling fan",
                    "fans and pumps", "plug loads","clothes washing",
                    "dishwasher","pool heaters", "pool pumps",
                    "portable electric spas"]}

replacements = {
    "pcs": "PCs",
    "nonpc_office_equipment": "non-PC office equipment",
    "other_mels": "plug loads", # "other (MELs)"
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


def get_var_char_values(data_dict):
    return [obj['VarCharValue'] for obj in data_dict['Data']]


def fetch_query_results(client, query_execution_id):
    query_result = client.get_query_results(
        QueryExecutionId=query_execution_id)
    result_data = query_result['ResultSet']

    headers = get_var_char_values(result_data['Rows'][0])
    result_rows = []

    while True:
        for row in result_data['Rows'][1:]:
            result_rows.append(dict(zip(headers, get_var_char_values(row))))
        
        if 'NextToken' not in query_result:
            break
        
        query_result = client.get_query_results(
            QueryExecutionId=query_execution_id,
            NextToken=query_result['NextToken'])
        result_data = query_result['ResultSet']
    
    return result_rows


def read_sql_file(sql_file):
    with open(os.path.join(SQL_DIR, sql_file), 'r', encoding='utf-8') as file:
        return file.read()


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
        if is_create:
            return result_loc, None
        else:
            data_rows = \
                fetch_query_results(client, query_execution_id)
            return result_loc, data_rows


def sql_to_csvout(s3_client, athena_client, sql_file):
    query = read_sql_file(sql_file)
    fname = os.path.splitext(sql_file)[0]
    s3_location, query_results = execute_athena_query(
        athena_client, query, False, wait=True)
    if query_results:
        df = pd.DataFrame(query_results)
        df.to_csv(f"{OUTPUT_DIR}/{fname}.csv", index=False)
        print(f"{fname}.csv is successfully saved!")
        print(f"Query results stored: {s3_location}")

    elif s3_location:
        print(f"""Query completed but no results. 
              Results path: {s3_location}""")
    else:
        print("Query {fname} failed or was cancelled.")     


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
    contains_nan = any(isinstance(item, float) and np.isnan(item) for item in example_list)
    if contains_nan:
        # print(f"The list contains NaN. {reg} {eu}")
        # print(example_list)
        updated_list = [0 if isinstance(item, float) and np.isnan(item) else item for item in example_list]
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
        values_to_keep = ['Mobile Home', 'Multi-Family with 5+ Units','Single-Family Detached']
        df = df[df['building_type'].isin(values_to_keep)]
    if opts.bstock == 'commercial':
        df = df[df['timestamp_hour'] != '2019-01-01 01:00:00.000']

    df = replace_strings_in_dataframe(df, replacements)
    json_file = f"{JSON_DIR}/tsv_load_in_2024.json"
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
        values_to_keep = ['Mobile Home', 'Multi-Family with 5+ Units','Single-Family Detached']
        df = df[df['building_type'].isin(values_to_keep)]

    df = replace_strings_in_dataframe(df, replacements)
    json_file = f"{JSON_DIR}/tsv_load_in_2024.json"
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
    emm_file = f"{OUTPUT_DIR}/{opts.bstock}_emm.csv"
    if not os.path.isfile(emm_file):
        return print('File does not exist, please run getdata()')
    df = pd.read_csv(emm_file)
    if opts.bstock == 'residential':
        values_to_keep = ['Mobile Home', 'Multi-Family with 5+ Units','Single-Family Detached']
        df = df[df['building_type'].isin(values_to_keep)]
    if opts.bstock == 'commercial':
        df = df[df['timestamp_hour'] != '2019-01-01 01:00:00.000']

    df = replace_strings_in_dataframe(df, replacements)
    json_file = f"{JSON_DIR}/tsv_load_in_2024.json"
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


def insert_scouttsv_usstate(opts):
    csv_file = f"{OUTPUT_DIR}/{opts.bstock}_state.csv"
    if not os.path.isfile(csv_file):
        return print('File does not exist, please run getdata()')
    df = pd.read_csv(csv_file)
    
    if opts.bstock == 'commercial':
        df = df[df['timestamp_hour'] != '2019-01-01 01:00:00.000']
    if opts.bstock == 'residential':
        values_to_keep = ['Mobile Home', 'Multi-Family with 5+ Units','Single-Family Detached']
        df = df[df['building_type'].isin(values_to_keep)]

    df = replace_strings_in_dataframe(df, replacements)
    json_file = f"{JSON_DIR}/tsv_load_in_2024.json"
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


def countrows_eu(opts):
    geodescs = ['emm', 'state']
    btype = 'Single-Family Detached' if opts.bstock == 'residential' else 'FullServiceRestaurant'

    for geodesc in geodescs:
        # geodesc = 'emm'
        file = f"{OUTPUT_DIR}/{opts.bstock}_{geodesc}.csv"
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
        # s3_create_tables_from_csv(s3_client, athena_client, MAP_DIR, "geo_map.csv")
        # RUN the SQL queries directly on AWS Athena as using Python may risk of losing datapoints due to connection issue
        sql_to_csvout(s3_client, athena_client, "comstock_data_emm.sql")
        sql_to_csvout(s3_client, athena_client, "resstock_data_emm.sql")

        sql_to_csvout(s3_client, athena_client, "comstock_data_state.sql")
        sql_to_csvout(s3_client, athena_client, "resstock_data_state.sql")

    if opts.insert_scouttsv is True:
        # python update_tsv.py --insert_scouttsv --bstock residential
        if opts.bstock in ['commercial', 'residential']:
            insert_scouttsv_emm(opts)
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
    opts = parser.parse_args()
    base_dir = getcwd()
    main(base_dir)
    hours, rem = divmod(time.time() - start_time, 3600)
    minutes, seconds = divmod(rem, 60)
    print("--- Overall Runtime: %s (HH:MM:SS.mm) ---" %
          "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))
