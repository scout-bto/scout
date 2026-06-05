
import pandas as pd
import os
import warnings
import argparse
import shutil

# Suppress warnings
warnings.filterwarnings("ignore")

# --- DICTIONARIES & MAPPINGS ---

END_USE_MAP = {
    "commercial": {
        "electricity": {
            "heating": [
                "out.electricity.heating.energy_consumption",
                "out.electricity.heat_recovery.energy_consumption"
            ],
            "cooling": [
                "out.electricity.heat_rejection.energy_consumption",
                "out.electricity.cooling.energy_consumption",
                "out.district_cooling.cooling.energy_consumption"
            ],
            "water heating": [
                "out.electricity.water_systems.energy_consumption"
            ],
            "fans and pumps": [
                "out.electricity.fans.energy_consumption",
                "out.electricity.pumps.energy_consumption"
            ],
            "lighting": [
                "out.electricity.interior_lighting.energy_consumption",
                "out.electricity.exterior_lighting.energy_consumption"
            ],
            "refrigeration": [
                "out.electricity.refrigeration.energy_consumption"
            ],
            "misc": [
                "out.electricity.interior_equipment.energy_consumption"
            ]
        },
        "natural gas": {
            "heating": [
                "out.natural_gas.heating.energy_consumption",
                "out.district_heating.heating.energy_consumption"
            ],
            "cooling": ["out.natural_gas.heating.energy_consumption"],
            "water heating": [
                "out.natural_gas.water_systems.energy_consumption",
                "out.district_heating.water_systems.energy_consumption"
            ],
            "misc": [
                "out.natural_gas.interior_equipment.energy_consumption"
            ]
        },
        "distillate": {
            "heating": ["out.other_fuel.heating.energy_consumption"],
            "cooling": ["out.other_fuel.cooling.energy_consumption"],
            "water heating": [
                "out.other_fuel.water_systems.energy_consumption"
            ],
            "misc": [
                "out.natural_gas.interior_equipment.energy_consumption"
            ]
        },
        "other fuel": {
            "misc": [
                "out.natural_gas.interior_equipment.energy_consumption"
            ]
        }
    },
    "residential": {
        "electricity": {
            "heating": [
                "out.electricity.heating.energy_consumption.kwh",
                "out.electricity.heating_hp_bkup.energy_consumption.kwh"
            ],
            "cooling": [
                "out.electricity.cooling.energy_consumption.kwh"
            ],
            "water heating": [
                "out.electricity.hot_water.energy_consumption.kwh"
            ],
            "cooking": [
                "out.electricity.range_oven.energy_consumption.kwh"
            ],
            "drying": [
                "out.electricity.clothes_dryer.energy_consumption.kwh"
            ],
            "clothes washing": [
                "out.electricity.clothes_washer.energy_consumption.kwh"
            ],
            "dishwasher": [
                "out.electricity.dishwasher.energy_consumption.kwh"
            ],
            "lighting": [
                "out.electricity.lighting_exterior.energy_consumption.kwh",
                "out.electricity.lighting_interior.energy_consumption.kwh",
                "out.electricity.lighting_garage.energy_consumption.kwh"
            ],
            "refrigeration": [
                "out.electricity.freezer.energy_consumption.kwh",
                "out.electricity.refrigerator.energy_consumption.kwh"
            ],
            "ceiling fan": [
                "out.electricity.ceiling_fan.energy_consumption.kwh"
            ],
            "misc": [
                "out.electricity.plug_loads.energy_consumption.kwh"
            ],
            "pool heaters": [
                "out.electricity.pool_heater.energy_consumption.kwh"
            ],
            "pool pumps": [
                "out.electricity.pool_pump.energy_consumption.kwh"
            ],
            "portable electric spas": [
                "out.electricity.permanent_spa_heat.energy_consumption.kwh",
                "out.electricity.permanent_spa_pump.energy_consumption.kwh"
            ],
            "fans and pumps": [
                "out.electricity.mech_vent.energy_consumption.kwh",
                "out.electricity.cooling_fans_pumps.energy_consumption.kwh",
                "out.electricity.heating_fans_pumps.energy_consumption.kwh",
                "out.electricity.heating_hp_bkup_fa.energy_consumption.kwh",
                "out.electricity.well_pump.energy_consumption.kwh"
            ],
        },
        "distillate": {
            "heating": [
                "out.fuel_oil.heating.energy_consumption.kwh",
                "out.fuel_oil.heating_hp_bkup.energy_consumption.kwh"
            ],
            "water heating": [
                "out.fuel_oil.hot_water.energy_consumption.kwh"
            ],
            "misc": [
                "out.natural_gas.pool_heater.energy_consumption.kwh"
            ]
        },
        "other fuel": {
            "heating": [
                "out.propane.heating.energy_consumption.kwh",
                "out.propane.heating_hp_bkup.energy_consumption.kwh"
            ],
            "water heating": [
                "out.propane.hot_water.energy_consumption.kwh"
            ],
            "cooking": [
                "out.propane.range_oven.energy_consumption.kwh"
            ],
            "misc": [
                "out.natural_gas.pool_heater.energy_consumption.kwh"
            ],
            "drying": [
                "out.propane.clothes_dryer.energy_consumption.kwh"
            ]
        },
        "natural gas": {
            "heating": [
                "out.natural_gas.heating.energy_consumption.kwh",
                "out.natural_gas.heating_hp_bkup.energy_consumption.kwh"
            ],
            "cooling": [
                "out.natural_gas.heating.energy_consumption.kwh",
                "out.natural_gas.heating_hp_bkup.energy_consumption.kwh"
            ],
            "water heating": [
                "out.natural_gas.hot_water.energy_consumption.kwh"
            ],
            "cooking": [
                "out.natural_gas.grill.energy_consumption.kwh",
                "out.natural_gas.range_oven.energy_consumption.kwh"
            ],
            "drying": [
                "out.natural_gas.clothes_dryer.energy_consumption.kwh"
            ],
            "misc": [
                "out.natural_gas.pool_heater.energy_consumption.kwh"
            ]
        }
    }
}

FUEL_ENDUSE_MAP = {
    "commercial": {
        "electricity": {
            "cooling": [
                "out.electricity.cooling.energy_consumption",
                "out.electricity.heat_rejection.energy_consumption"
            ],
            "heating": [
                "out.electricity.heating.energy_consumption",
                "out.electricity.heat_recovery.energy_consumption"
            ],
        },
    },
    "residential": {
        "electricity": {
            "cooling": [
                "out.electricity.cooling.energy_consumption.kwh"
            ],
            "heating": [
                "out.electricity.heating.energy_consumption.kwh",
                "out.electricity.heating_hp_bkup.energy_consumption.kwh"
            ],
        }
    }
}

DF_ORDER = pd.DataFrame({
    'no': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
           20, 21, 22, 23, 24, 25],
    'emm_intersect': ["TRE", "FRCC", "MISW", "MISC", "MISE", "MISS", "ISNE",
                      "NYCW", "NYUP", "PJME", "PJMW", "PJMC", "PJMD", "SRCA",
                      "SRSE", "SRCE", "SPPS", "SPPC", "SPPN", "SRSG", "CANO",
                      "CASO", "NWPP", "RMRG", "BASN"]
})

# --- HELPER FUNCTIONS ---


def get_scout_geo(base_dir):
    file = os.path.join(base_dir, 'scout_geography.csv')
    df = pd.read_csv(file, dtype=str)
    df['fips_code'] = df['fips_code'].str.zfill(5)
    df['gisjoin'] = df['fips_code'].apply(
        lambda x: 'G' + str(x)[:2] + '0' + str(x)[2:] + '0')
    df.loc[df['state'] == 'AK', 'emm2020_county'] = 'AK_HI'
    df.loc[df['state'] == 'HI', 'emm2020_county'] = 'AK_HI'
    return df


def remove_space(string):
    return string.replace(" ", "")


def transpose(df):
    return df.transpose()


def combine_keys(_dict):
    combined_dict = {}
    for fuel_type, categories in _dict.items():
        for category, values in categories.items():
            combined_key = f"{fuel_type}_{category.replace(' ', '_')}"
            combined_dict[combined_key] = values
    return combined_dict


# --- CORE LOGIC ---


def apply_geographies(df, dfdict, geos):
    df['county'] = df['county'].astype(str)
    df.loc[df['state'] == 'AK', 'county'] = 'G0'
    df.loc[df['state'] == 'HI', 'county'] = 'G1'
    for geo in geos:
        geocol = 'emm2020_county' if geo == 'emm' else geo
        d = dfdict.set_index('gisjoin').T.to_dict('index')[geocol]
        df[geo] = df['county'].map(d)
    df = df.drop('county', axis=1)
    return df


def output_emm(df):
    merged_matrix = df.merge(DF_ORDER, left_on='emm',
                             right_on='emm_intersect', how='left')
    sorted_matrix = merged_matrix.sort_values(by='no')
    sorted_matrix = sorted_matrix.drop(sorted_matrix.columns[-2:], axis=1)
    sorted_matrix.loc['total'] = sorted_matrix.sum()
    sorted_matrix = transpose(sorted_matrix)
    return sorted_matrix


def output_state(df):
    sorted_matrix = df
    sorted_matrix.loc['total'] = sorted_matrix.sum()
    sorted_matrix = transpose(sorted_matrix)
    return sorted_matrix


def replace_col_vals(df, tech):
    df = df.copy()
    df.drop(columns=['Technology'], inplace=True)
    df.insert(0, 'Technology', tech)
    return df


def process_end_use_energy(sector, filedir, filename, weathers, mymap,
                           scoutgeo_df, geos, outdir):
    """Process end-use energy data to create State/EMM disaggregation maps."""
    if sector == "commercial":
        county_col = "in.nhgis_county_gisjoin"
        sec = "Com"
    else:
        county_col = "in.county"
        sec = "Res"

    mykeys = list(mymap[sector])
    for weath in weathers:
        print(f"  Processing {sector} end-use energy for {weath}...")
        df = pd.read_parquet(f"{filedir}{weath}/{filename}",
                             engine='pyarrow')

        df.rename(columns={county_col: 'county'}, inplace=True)
        df.rename(columns={'in.state': 'state'}, inplace=True)

        for eu in mykeys:
            df[eu] = df[mymap[sector][eu]].sum(axis=1)

        df.reset_index(inplace=True)
        df = apply_geographies(df, scoutgeo_df, geos)
        df = df.dropna(subset=geos)
        df = df[geos + mykeys]
        df = df.groupby(['emm', 'state']).sum().reset_index()

        norm_pd = pd.DataFrame()
        for eu in mykeys:
            conversion_matrix = df.pivot(index='emm', columns='state',
                                         values=eu)
            normalized_matrix = conversion_matrix.div(
                conversion_matrix.sum(axis=0), axis=1).reset_index()
            normalized_matrix = output_emm(normalized_matrix)
            normalized_matrix = normalized_matrix.fillna(0)
            normalized_matrix.columns = normalized_matrix.iloc[0]
            normalized_matrix.rename(
                columns={normalized_matrix.columns[-1]: 'Total'},
                inplace=True)
            normalized_matrix = normalized_matrix.iloc[1:]
            normalized_matrix.insert(0, 'State', normalized_matrix.index)
            normalized_matrix.insert(0, 'End use', eu)
            normalized_matrix.drop(columns=['Total'], inplace=True)
            norm_pd = (normalized_matrix if norm_pd.empty
                       else pd.concat([norm_pd, normalized_matrix],
                                      ignore_index=False))

        norm_pd.to_csv(f"{outdir}/{sec}_State_EMM_{weath}.csv",
                       index=False)
        print(f"    Saved {sec}_State_EMM_{weath}.csv")


def process_end_use_stock(sector, filedir, filename, weathers, mymap,
                          scoutgeo_df, geos, outdir):
    """Process end-use stock data to create State/EMM disaggregation maps."""
    def eu_rows(df, category, columns_dict, threshold=1):
        columns = columns_dict.get(category, [])
        mask = (df[columns] != 0).sum(axis=1) >= threshold
        filtered_df = df[mask]
        return filtered_df

    conditions_dict = mymap[sector]
    if sector == "commercial":
        county_col = "in.nhgis_county_gisjoin"
        area_col = "calc.weighted.sqft"
        sec = "Com"
    else:
        county_col = "in.county"
        area_col = "weight"
        sec = "Res"

    for weath in weathers:
        print(f"  Processing {sector} end-use stock for {weath}...")
        alldf = pd.read_parquet(f"{filedir}{weath}/{filename}",
                                engine='pyarrow')
        alldf.rename(columns={county_col: "county"}, inplace=True)
        alldf.rename(columns={"in.state": "state"}, inplace=True)
        alldf.rename(columns={area_col: "warea"}, inplace=True)

        mykeys = list(mymap[sector])
        norm_pd = pd.DataFrame()

        for eu in mykeys:
            df = eu_rows(alldf, eu, conditions_dict)
            df = apply_geographies(df, scoutgeo_df, geos)
            df = df[["warea", "state", "emm"]]

            conversion_matrix = df.pivot_table(
                index='emm', columns='state', values="warea",
                aggfunc='sum')
            normalized_matrix = conversion_matrix.div(
                conversion_matrix.sum(axis=0), axis=1).reset_index()
            normalized_matrix = output_emm(normalized_matrix)
            normalized_matrix = normalized_matrix.fillna(0)
            normalized_matrix.columns = normalized_matrix.iloc[0]
            normalized_matrix.rename(
                columns={normalized_matrix.columns[-1]: 'Total'},
                inplace=True)
            normalized_matrix = normalized_matrix.iloc[1:]
            normalized_matrix.insert(0, 'emm', normalized_matrix.index)
            normalized_matrix.insert(0, 'End use', eu)
            norm_pd = (normalized_matrix if norm_pd.empty
                       else pd.concat([norm_pd, normalized_matrix],
                                      ignore_index=False))

        norm_pd.to_csv(f"{outdir}/{sec}_State_EMM_{weath}_Stock.csv",
                       index=False)
        print(f"    Saved {sec}_State_EMM_{weath}_Stock.csv")


def process_tech_energy(sector, filedir, filename, weathers, mymap,
                        scoutgeo_df, geos, outdir, fdir):
    """Process technology-level energy data (placeholder for now)."""
    print(f"  Tech energy processing for {sector} (not yet implemented)")
    pass


def process_tech_stock(sector, filedir, filename, weathers, mymap, scoutgeo_df,
                       geos, outdir, fdir):
    """Process technology-level stock data (placeholder for now)."""
    print(f"  Tech stock processing for {sector} (not yet implemented)")
    pass


def combine_hvac_and_other(output_dir):
    """Combine HVAC technology files with end-use files."""
    print("Combining HVAC tech and other end-use files...")
    tech_dir = os.path.join(output_dir, "2024_technology")
    end_use_dir = os.path.join(output_dir, "2024_end_use")

    filenames = [
        "Com_Cdiv_EMM_amy2018",
        "Com_Cdiv_State_amy2018",
        "Res_Cdiv_EMM_amy2018",
        "Res_Cdiv_State_amy2018",
        "Com_Cdiv_EMM_amy2018_Stock",
        "Com_Cdiv_State_amy2018_Stock",
        "Res_Cdiv_EMM_amy2018_Stock",
        "Res_Cdiv_State_amy2018_Stock"
    ]

    for filename in filenames:
        if "Stock" in filename:
            filename_eu = (f"{filename.replace('Stock', '')}"
                           f"electricity_Stock.csv")
            filename_tech = f"{filename}_electricity.csv"
        else:
            filename_eu = f"{filename}_electricity.csv"
            filename_tech = f"{filename}_electricity_tech.csv"

        eu_path = os.path.join(end_use_dir, filename_eu)
        tech_path = os.path.join(tech_dir, filename_tech)

        # Only combine if both files exist
        if os.path.exists(eu_path) and os.path.exists(tech_path):
            df_eu = pd.read_csv(eu_path)
            df_tech = pd.read_csv(tech_path)
            combined = pd.concat([df_tech, df_eu], ignore_index=True)
            combined.to_csv(eu_path, index=False)
            print(f"  Combined {filename}")
        elif not os.path.exists(eu_path):
            print(f"  Skipping {filename}: end-use file not found")
        elif not os.path.exists(tech_path):
            print(f"  Skipping {filename}: tech file not found")

    print("Combination complete.")


def fill_na_with_zeros(output_dir):
    """Fill NA values with 0 in all generated CSV files."""
    print("Filling NA values with 0...")
    for folder_name in ["2024_end_use", "2024_technology"]:
        folder_path = os.path.join(output_dir, folder_name)
        if not os.path.exists(folder_path):
            print(f"  Skipping {folder_name}: directory not found")
            continue

        csv_files = [f for f in os.listdir(folder_path)
                     if f.endswith('.csv')]
        for filename in csv_files:
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path)
            df = df.fillna(0)
            df.to_csv(file_path, index=False)

        if csv_files:
            print(f"  Filled NAs in {len(csv_files)} files in "
                  f"{folder_name}")
        else:
            print(f"  No CSV files found in {folder_name}")

    print("NA filling complete.")


def install_files(output_dir, install_dir):
    print(f"Installing generated files to {install_dir}...")
    if not os.path.exists(install_dir):
        os.makedirs(install_dir)

    source_dirs = [
        os.path.join(output_dir, "2024_end_use"),
        os.path.join(output_dir, "2024_technology")
    ]

    for source_dir in source_dirs:
        if os.path.exists(source_dir):
            for filename in os.listdir(source_dir):
                if filename.endswith(".csv"):
                    source_file = os.path.join(source_dir, filename)
                    dest_file = os.path.join(install_dir, filename)
                    shutil.copy2(source_file, dest_file)
                    print(f"  Copied {filename}")
    print("Installation complete.")


def main():
    parser = argparse.ArgumentParser(
        description="Generate geographic disaggregation maps from ResStock and "
                    "ComStock data.")
    parser.add_argument('--weather-year', type=str, default='amy2018',
                        help='Weather year (e.g. amy2018 or tmy3).')
    parser.add_argument('--comstock-path', type=str,
                        default='input/2024_comstock',
                        help='Path to ComStock data directory.')
    parser.add_argument('--resstock-path', type=str,
                        default='input/2024_resstock',
                        help='Path to ResStock data directory.')
    parser.add_argument('--output-dir', type=str, default='output',
                        help='Directory to save the output CSV '
                             'files.')
    parser.add_argument('--all', action='store_true',
                        help='Generate all output files (default behavior).')
    parser.add_argument('--force', action='store_true',
                        help='Overwrite existing output files.')
    parser.add_argument('--install', action='store_true',
                        help='Copy generated files to geo_map directory.')

    args = parser.parse_args()

    # Define base directory relative to the script location
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define output subdirectories
    tech_outdir = os.path.join(args.output_dir, '2024_technology')
    end_use_outdir = os.path.join(args.output_dir, '2024_end_use')
    os.makedirs(tech_outdir, exist_ok=True)
    os.makedirs(end_use_outdir, exist_ok=True)

    scoutgeo_df = get_scout_geo(script_dir)

    print("Starting disaggregation process...")

    # Check if input data exists
    resstock_data_path = os.path.join(args.resstock_path, args.weather_year,
                                      'baseline.parquet')
    comstock_data_path = os.path.join(args.comstock_path, args.weather_year,
                                      'baseline.parquet')

    if not os.path.exists(resstock_data_path):
        print(f"WARNING: ResStock data not found at: {resstock_data_path}")
        print("  Skipping residential processing.")
        print("  To generate residential disaggregation maps, provide "
              "BuildStock parquet files.")
    else:
        print(f"Processing residential data from: {resstock_data_path}")
        weathers = [args.weather_year]
        geos = ['emm', 'state']

        # Process residential end-use energy
        try:
            process_end_use_energy(
                sector='residential',
                filedir=f"{args.resstock_path}/",
                filename='baseline.parquet',
                weathers=weathers,
                mymap=combine_keys(END_USE_MAP['residential']),
                scoutgeo_df=scoutgeo_df,
                geos=geos,
                outdir=end_use_outdir
            )
        except Exception as e:
            print(f"  ERROR processing residential energy: {e}")

        # Process residential end-use stock
        try:
            process_end_use_stock(
                sector='residential',
                filedir=f"{args.resstock_path}/",
                filename='baseline.parquet',
                weathers=weathers,
                mymap=END_USE_MAP['residential'],
                scoutgeo_df=scoutgeo_df,
                geos=geos,
                outdir=end_use_outdir
            )
        except Exception as e:
            print(f"  ERROR processing residential stock: {e}")

    if not os.path.exists(comstock_data_path):
        print(f"WARNING: ComStock data not found at: {comstock_data_path}")
        print("  Skipping commercial processing.")
        print("  To generate commercial disaggregation maps, provide "
              "BuildStock parquet files.")
    else:
        print(f"Processing commercial data from: {comstock_data_path}")
        weathers = [args.weather_year]
        geos = ['emm', 'state']

        # Process commercial end-use energy
        try:
            process_end_use_energy(
                sector='commercial',
                filedir=f"{args.comstock_path}/",
                filename='baseline.parquet',
                weathers=weathers,
                mymap=combine_keys(END_USE_MAP['commercial']),
                scoutgeo_df=scoutgeo_df,
                geos=geos,
                outdir=end_use_outdir
            )
        except Exception as e:
            print(f"  ERROR processing commercial energy: {e}")

        # Process commercial end-use stock
        try:
            process_end_use_stock(
                sector='commercial',
                filedir=f"{args.comstock_path}/",
                filename='baseline.parquet',
                weathers=weathers,
                mymap=END_USE_MAP['commercial'],
                scoutgeo_df=scoutgeo_df,
                geos=geos,
                outdir=end_use_outdir
            )
        except Exception as e:
            print(f"  ERROR processing commercial stock: {e}")

    print("Disaggregation process finished.")

    # Post-processing steps
    combine_hvac_and_other(args.output_dir)
    fill_na_with_zeros(args.output_dir)

    # Install step
    if args.install:
        install_dir = os.path.abspath(
            os.path.join(script_dir, '..', '..', 'convert_data', 'geo_map'))
        install_files(args.output_dir, install_dir)


if __name__ == "__main__":
    main()
