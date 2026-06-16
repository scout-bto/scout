
import pandas as pd
import os
import re
import warnings
import argparse
import shutil
import traceback

# Suppress warnings
warnings.filterwarnings("ignore")

# --- DICTIONARIES & MAPPINGS ---
# NOTE: All column names below are SUFFIX-FREE. normalize_columns() strips the
# trailing ..<unit> (ComStock) and .<unit> (ResStock) suffixes on load so that
# both sectors reference identical, unit-free names and go through identical
# arithmetic.

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
            # FIXME: maps to .heating, not .cooling. Gas cooling is near-zero in
            # commercial stock; confirm whether this should be a cooling column
            # (likely no such column exists) or removed entirely.
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
            # NOTE: other_fuel.cooling is a genuine zero-stock omission in the
            # parquet; ensure_columns() will zero-fill it.
            "cooling": ["out.other_fuel.cooling.energy_consumption"],
            "water heating": [
                "out.other_fuel.water_systems.energy_consumption"
            ],
            # FIXME: distillate "misc" points at a natural_gas column. Likely
            # should be out.other_fuel.interior_equipment.energy_consumption
            # (which is also a zero-stock omission and will be zero-filled).
            "misc": [
                "out.natural_gas.interior_equipment.energy_consumption"
            ]
        },
        "other fuel": {
            # FIXME: "other fuel" misc points at the same natural_gas column as
            # distillate misc, so gas interior equipment is double-counted.
            # Confirm intended source column.
            "misc": [
                "out.natural_gas.interior_equipment.energy_consumption"
            ]
        }
    },
    "residential": {
        "electricity": {
            "heating": [
                "out.electricity.heating.energy_consumption",
                "out.electricity.heating_hp_bkup.energy_consumption"
            ],
            "cooling": [
                "out.electricity.cooling.energy_consumption"
            ],
            "water heating": [
                "out.electricity.hot_water.energy_consumption"
            ],
            "cooking": [
                "out.electricity.range_oven.energy_consumption"
            ],
            "drying": [
                "out.electricity.clothes_dryer.energy_consumption"
            ],
            "clothes washing": [
                "out.electricity.clothes_washer.energy_consumption"
            ],
            "dishwasher": [
                "out.electricity.dishwasher.energy_consumption"
            ],
            "lighting": [
                "out.electricity.lighting_exterior.energy_consumption",
                "out.electricity.lighting_interior.energy_consumption",
                "out.electricity.lighting_garage.energy_consumption"
            ],
            "refrigeration": [
                "out.electricity.freezer.energy_consumption",
                "out.electricity.refrigerator.energy_consumption"
            ],
            "ceiling fan": [
                "out.electricity.ceiling_fan.energy_consumption"
            ],
            "misc": [
                "out.electricity.plug_loads.energy_consumption"
            ],
            "pool heaters": [
                "out.electricity.pool_heater.energy_consumption"
            ],
            "pool pumps": [
                "out.electricity.pool_pump.energy_consumption"
            ],
            "portable electric spas": [
                "out.electricity.permanent_spa_heat.energy_consumption",
                "out.electricity.permanent_spa_pump.energy_consumption"
            ],
            "fans and pumps": [
                "out.electricity.mech_vent.energy_consumption",
                "out.electricity.cooling_fans_pumps.energy_consumption",
                "out.electricity.heating_fans_pumps.energy_consumption",
                "out.electricity.heating_hp_bkup_fa.energy_consumption",
                "out.electricity.well_pump.energy_consumption"
            ],
        },
        "distillate": {
            "heating": [
                "out.fuel_oil.heating.energy_consumption",
                "out.fuel_oil.heating_hp_bkup.energy_consumption"
            ],
            "water heating": [
                "out.fuel_oil.hot_water.energy_consumption"
            ],
            # FIXME: distillate misc points at natural_gas.pool_heater.
            "misc": [
                "out.natural_gas.pool_heater.energy_consumption"
            ]
        },
        "other fuel": {
            "heating": [
                "out.propane.heating.energy_consumption",
                "out.propane.heating_hp_bkup.energy_consumption"
            ],
            "water heating": [
                "out.propane.hot_water.energy_consumption"
            ],
            "cooking": [
                "out.propane.range_oven.energy_consumption"
            ],
            # FIXME: other fuel misc points at natural_gas.pool_heater.
            "misc": [
                "out.natural_gas.pool_heater.energy_consumption"
            ],
            "drying": [
                "out.propane.clothes_dryer.energy_consumption"
            ]
        },
        "natural gas": {
            "heating": [
                "out.natural_gas.heating.energy_consumption",
                "out.natural_gas.heating_hp_bkup.energy_consumption"
            ],
            # FIXME: gas cooling maps to gas heating columns.
            "cooling": [
                "out.natural_gas.heating.energy_consumption",
                "out.natural_gas.heating_hp_bkup.energy_consumption"
            ],
            "water heating": [
                "out.natural_gas.hot_water.energy_consumption"
            ],
            "cooking": [
                "out.natural_gas.grill.energy_consumption",
                "out.natural_gas.range_oven.energy_consumption"
            ],
            "drying": [
                "out.natural_gas.clothes_dryer.energy_consumption"
            ],
            "misc": [
                "out.natural_gas.pool_heater.energy_consumption"
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
                "out.electricity.cooling.energy_consumption"
            ],
            "heating": [
                "out.electricity.heating.energy_consumption",
                "out.electricity.heating_hp_bkup.energy_consumption"
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


def normalize_columns(df):
    """Strip trailing unit suffixes so commercial (..kwh) and residential
    (.kwh) columns share identical suffix-free names. This is what allows both
    sectors to go through identical map-lookup arithmetic.

    Order matters: strip the double-dot ComStock form first, then the
    single-dot ResStock form. The single-dot strip is restricted to a known
    set of unit tokens so we don't accidentally truncate a legitimate name
    segment (e.g. 'energy_consumption' itself is never a unit token).
    """
    unit_tokens = (
        "kwh", "kbtu", "therm", "therms", "gal", "j", "c", "f",
        "ft2", "tbtu", "kwh_per_ft2", "co2e_kg", "percent", "tons",
        "cop", "eer", "ieer", "seer", "w", "hr"
    )
    single_dot = re.compile(r'\.(' + '|'.join(unit_tokens) + r')$')

    def strip(c):
        c = re.sub(r'\.\.[a-z0-9_]+$', '', c)   # ComStock: ..<unit>
        c = single_dot.sub('', c)               # ResStock: .<unit>
        return c

    df.columns = [strip(c) for c in df.columns]
    return df


def ensure_columns(df, mymap, fill=0.0):
    """Add any mapped columns absent from df as a constant `fill` value.

    Absent commercial columns (e.g. out.other_fuel.cooling.energy_consumption)
    are genuine zero-stock omissions in the ComStock parquet, so zero-filling
    them keeps the per-end-use summation identical in form to residential while
    contributing the correct zero energy.
    """
    expected = {col for cols in mymap.values() for col in cols}
    missing = sorted(c for c in expected if c not in df.columns)
    for c in missing:
        df[c] = fill
    if missing:
        print(f"    Zero-filled {len(missing)} absent column(s):")
        for c in missing:
            print(f"      {c}")
    return df


# --- CORE LOGIC ---


def apply_geographies(df, dfdict, geos):
    df['county'] = df['county'].astype(str)
    df.loc[df['state'] == 'AK', 'county'] = 'G0'
    df.loc[df['state'] == 'HI', 'county'] = 'G1'
    for geo in geos:
        if geo == 'emm':
            geocol = 'emm2020_county'
        elif geo == 'cdiv':
            geocol = 'cdiv'
        else:
            geocol = geo
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
                           scoutgeo_df, geos, outdir, fueltype='electricity',
                           preloaded_dfs=None):
    """Process end-use energy data to create geographic disaggregation maps."""
    if sector == "commercial":
        county_col = "in.nhgis_county_gisjoin"
        sec = "Com"
    else:
        county_col = "in.county"
        sec = "Res"

    mykeys = list(mymap)
    for weath in weathers:
        print(f"  Processing {sector} end-use energy ({fueltype}) for {weath}...")
        if preloaded_dfs is not None and weath in preloaded_dfs:
            df = preloaded_dfs[weath].copy()
        else:
            df = pd.read_parquet(f"{filedir}{weath}/{filename}",
                                 engine='pyarrow')
            df = normalize_columns(df)
        df = ensure_columns(df, mymap)

        df.rename(columns={county_col: 'county'}, inplace=True)
        df.rename(columns={'in.state': 'state'}, inplace=True)

        for eu in mykeys:
            df[eu] = df[mymap[eu]].sum(axis=1)

        df.reset_index(inplace=True)
        df = apply_geographies(df, scoutgeo_df, geos)
        df = df.dropna(subset=geos)
        df = df[geos + mykeys]

        # Determine groupby columns based on geos
        if 'emm' in geos and 'state' in geos:
            group_cols = ['emm', 'state']
            pivot_index = 'emm'
            pivot_col = 'state'
            output_func = output_emm
            geo_label = 'State'
            filename_geo = 'EMM'
        elif 'cdiv' in geos and 'state' in geos:
            group_cols = ['cdiv', 'state']
            pivot_index = 'state'
            pivot_col = 'cdiv'
            output_func = output_state
            geo_label = 'CDIV'
            filename_geo = 'State'
        elif 'cdiv' in geos and 'emm' in geos:
            group_cols = ['cdiv', 'emm']
            pivot_index = 'emm'
            pivot_col = 'cdiv'
            output_func = output_emm
            geo_label = 'CDIV'
            filename_geo = 'EMM'
        else:
            raise ValueError(f"Unsupported geography combination: {geos}")

        df = df.groupby(group_cols).sum().reset_index()

        norm_pd = pd.DataFrame()
        for eu in mykeys:
            conversion_matrix = df.pivot(index=pivot_index, columns=pivot_col,
                                         values=eu)
            normalized_matrix = conversion_matrix.div(
                conversion_matrix.sum(axis=0), axis=1).reset_index()
            normalized_matrix = output_func(normalized_matrix)
            normalized_matrix = normalized_matrix.fillna(0)
            normalized_matrix.columns = normalized_matrix.iloc[0]
            normalized_matrix.rename(
                columns={normalized_matrix.columns[-1]: 'Total'},
                inplace=True)
            normalized_matrix = normalized_matrix.iloc[1:]
            normalized_matrix.insert(0, geo_label, normalized_matrix.index)
            normalized_matrix.insert(0, 'End use', eu)
            normalized_matrix.drop(columns=['Total'], inplace=True)
            norm_pd = (normalized_matrix if norm_pd.empty
                       else pd.concat([norm_pd, normalized_matrix],
                                      ignore_index=False))

        # Add AK/HI columns for residential Cdiv outputs
        if sec == "Res" and 'cdiv' in geos:
            norm_pd['AK'] = 0
            norm_pd['HI'] = 0

        fuel_suffix = f"_{remove_space(fueltype)}" if fueltype else ""
        norm_pd.to_csv(f"{outdir}/{sec}_Cdiv_{filename_geo}_{weath}{fuel_suffix}.csv",
                       index=False)
        print(f"    Saved {sec}_Cdiv_{filename_geo}_{weath}{fuel_suffix}.csv")


def process_end_use_stock(sector, filedir, filename, weathers, mymap,
                          scoutgeo_df, geos, outdir, fueltype='electricity',
                          preloaded_dfs=None):
    """Process end-use stock data to create geographic disaggregation maps."""
    def eu_rows(df, category, columns_dict, threshold=1):
        columns = columns_dict.get(category, [])
        mask = (df[columns] != 0).sum(axis=1) >= threshold
        filtered_df = df[mask]
        return filtered_df

    conditions_dict = mymap
    if sector == "commercial":
        county_col = "in.nhgis_county_gisjoin"
        area_col = "calc.weighted.sqft"
        sec = "Com"
    else:
        county_col = "in.county"
        area_col = "weight"
        sec = "Res"

    for weath in weathers:
        print(f"  Processing {sector} end-use stock ({fueltype}) for {weath}...")
        if preloaded_dfs is not None and weath in preloaded_dfs:
            alldf = preloaded_dfs[weath].copy()
        else:
            alldf = pd.read_parquet(f"{filedir}{weath}/{filename}",
                                    engine='pyarrow')
            alldf = normalize_columns(alldf)
        alldf = ensure_columns(alldf, mymap)

        alldf.rename(columns={county_col: "county"}, inplace=True)
        alldf.rename(columns={"in.state": "state"}, inplace=True)
        alldf.rename(columns={area_col: "warea"}, inplace=True)

        if "warea" not in alldf.columns:
            raise KeyError(
                f"Area column '{area_col}' not found after normalization. "
                f"Check its exact spelling in the {sector} parquet "
                f"(normalize_columns may have altered it).")

        mykeys = list(mymap)
        norm_pd = pd.DataFrame()

        # Determine groupby columns based on geos
        if 'emm' in geos and 'state' in geos:
            pivot_index = 'emm'
            pivot_col = 'state'
            output_func = output_emm
            geo_label = 'State'
            filename_geo = 'EMM'
        elif 'cdiv' in geos and 'state' in geos:
            pivot_index = 'state'
            pivot_col = 'cdiv'
            output_func = output_state
            geo_label = 'CDIV'
            filename_geo = 'State'
        elif 'cdiv' in geos and 'emm' in geos:
            pivot_index = 'emm'
            pivot_col = 'cdiv'
            output_func = output_emm
            geo_label = 'CDIV'
            filename_geo = 'EMM'
        else:
            raise ValueError(f"Unsupported geography combination: {geos}")

        for eu in mykeys:
            df = eu_rows(alldf, eu, conditions_dict)
            df = apply_geographies(df, scoutgeo_df, geos)
            df = df[["warea"] + geos]

            conversion_matrix = df.pivot_table(
                index=pivot_index, columns=pivot_col, values="warea",
                aggfunc='sum')
            normalized_matrix = conversion_matrix.div(
                conversion_matrix.sum(axis=0), axis=1).reset_index()
            normalized_matrix = output_func(normalized_matrix)
            normalized_matrix = normalized_matrix.fillna(0)
            normalized_matrix.columns = normalized_matrix.iloc[0]
            normalized_matrix.rename(
                columns={normalized_matrix.columns[-1]: 'Total'},
                inplace=True)
            normalized_matrix = normalized_matrix.iloc[1:]
            normalized_matrix.insert(0, geo_label, normalized_matrix.index)
            normalized_matrix.insert(0, 'End use', eu)
            norm_pd = (normalized_matrix if norm_pd.empty
                       else pd.concat([norm_pd, normalized_matrix],
                                      ignore_index=False))

        # Add AK/HI columns for residential Cdiv outputs
        if sec == "Res" and 'cdiv' in geos:
            norm_pd['AK'] = 0
            norm_pd['HI'] = 0

        fuel_suffix = f"_{remove_space(fueltype)}" if fueltype else ""
        norm_pd.to_csv(f"{outdir}/{sec}_Cdiv_{filename_geo}_{weath}{fuel_suffix}_Stock.csv",
                       index=False)
        print(f"    Saved {sec}_Cdiv_{filename_geo}_{weath}{fuel_suffix}_Stock.csv")


def _apply_tech_map(df, map_df):
    """Assign scout_tech to each row by merging on all non-scout_tech columns."""
    merge_cols = [c for c in map_df.columns if c != 'scout_tech' and c in df.columns]
    df = df.copy()
    df['_orig_idx'] = range(len(df))
    merged = df.merge(map_df[merge_cols + ['scout_tech']], on=merge_cols, how='left')
    # If map rows have overlapping conditions, keep last match (preserves original priority)
    merged = merged.drop_duplicates(subset=['_orig_idx'], keep='last')
    return merged.drop(columns=['_orig_idx'])


def _tech_output_block(normalized_matrix, output_func, eu, tech, all_tech):
    """Normalize, format, and accumulate one technology's matrix."""
    normalized_matrix = output_func(normalized_matrix)
    normalized_matrix = normalized_matrix.fillna(0)
    normalized_matrix.columns = normalized_matrix.iloc[0]
    normalized_matrix.rename(
        columns={normalized_matrix.columns[-1]: 'Total'}, inplace=True)
    normalized_matrix = normalized_matrix.iloc[1:]
    normalized_matrix.insert(0, 'CDIV', normalized_matrix.index)
    normalized_matrix.insert(0, 'End use', eu.split('_')[1])
    normalized_matrix.insert(0, 'Technology', tech)
    if (normalized_matrix['Total'] != 0).all():
        normalized_matrix.drop(columns=['Total'], inplace=True)
        all_tech = (normalized_matrix if all_tech.empty
                    else pd.concat([all_tech, normalized_matrix],
                                   ignore_index=False))
        if tech == "res_type_central_AC":
            norm2 = replace_col_vals(normalized_matrix, "wall-window_room_AC")
            all_tech = pd.concat([all_tech, norm2], ignore_index=False)
    return all_tech


def process_tech_energy(sector, filedir, filename, weathers, mymap,
                        scoutgeo_df, geos, outdir, mapping_dir,
                        preloaded_dfs=None):
    """Process technology-level energy data for electricity heating/cooling."""
    if sector == "commercial":
        county_col = "in.nhgis_county_gisjoin"
        sec = "Com"
    else:
        county_col = "in.county"
        sec = "Res"

    combined_map = combine_keys(mymap[sector])
    mykeys = list(combined_map)

    if 'emm' in geos and 'cdiv' in geos:
        pivot_index, pivot_col = 'emm', 'cdiv'
        group_cols = ['emm', 'cdiv', 'scout_tech']
        output_func = output_emm
        filename_geo = 'EMM'
    elif 'state' in geos and 'cdiv' in geos:
        pivot_index, pivot_col = 'state', 'cdiv'
        group_cols = ['state', 'cdiv', 'scout_tech']
        output_func = output_state
        filename_geo = 'State'
    else:
        raise ValueError(f"Unsupported geography combination for tech: {geos}")

    # Pre-load map CSVs once — avoid repeated disk I/O inside the eu loop
    map_dfs = {
        eu: pd.read_csv(os.path.join(mapping_dir, f"map_{sector[:3]}_{eu}.csv"))
        for eu in mykeys
        if os.path.exists(os.path.join(mapping_dir, f"map_{sector[:3]}_{eu}.csv"))
    }

    for weath in weathers:
        print(f"  Processing {sector} tech energy for {weath}...")
        if preloaded_dfs is not None and weath in preloaded_dfs:
            df_all = preloaded_dfs[weath].copy()
        else:
            df_all = pd.read_parquet(f"{filedir}{weath}/{filename}", engine='pyarrow')
            df_all = normalize_columns(df_all)
        df_all = ensure_columns(df_all, combined_map)
        df_all.rename(columns={county_col: 'county'}, inplace=True)
        df_all.rename(columns={'in.state': 'state'}, inplace=True)
        df_all.reset_index(inplace=True)
        df_all = apply_geographies(df_all, scoutgeo_df, geos)
        df_all = df_all.dropna(subset=geos)

        all_eu = pd.DataFrame()
        for eu in mykeys:
            if eu not in map_dfs:
                print(f"    Skipping {eu}: map file not found")
                continue

            # Copy only the columns needed for this eu to reduce memory pressure.
            # Include map join columns so _apply_tech_map has attributes to match on.
            eu_source_cols = combined_map[eu]
            map_join_cols = [c for c in map_dfs[eu].columns
                             if c != 'scout_tech' and c in df_all.columns]
            needed_cols = list(dict.fromkeys(geos + eu_source_cols + map_join_cols))
            df = df_all[[c for c in needed_cols if c in df_all.columns]].copy()
            df[eu] = df[eu_source_cols].sum(axis=1)
            df = df[df[eu] > 0]

            df = _apply_tech_map(df, map_dfs[eu])

            df = df[geos + ['scout_tech', eu]]
            tech_list = df['scout_tech'].dropna().unique().tolist()
            df = df.groupby(group_cols).sum().reset_index()

            all_tech = pd.DataFrame()
            for tech in tech_list:
                tdf = df[df['scout_tech'] == tech].drop(columns=['scout_tech'])
                conversion_matrix = tdf.pivot(
                    index=pivot_index, columns=pivot_col, values=eu)
                normalized_matrix = conversion_matrix.div(
                    conversion_matrix.sum(axis=0), axis=1).reset_index()
                all_tech = _tech_output_block(
                    normalized_matrix, output_func, eu, tech, all_tech)
            if not all_tech.empty:
                all_eu = (all_tech if all_eu.empty
                          else pd.concat([all_eu, all_tech], ignore_index=False))

        out_file = (f"{sec}_Cdiv_{filename_geo}_{weath}_electricity_Tech.csv")
        all_eu.to_csv(f"{outdir}/{out_file}", index=False)
        print(f"    Saved {out_file}")


def process_tech_stock(sector, filedir, filename, weathers, mymap, scoutgeo_df,
                       geos, outdir, mapping_dir, preloaded_dfs=None):
    """Process technology-level stock data for electricity heating/cooling."""
    if sector == "commercial":
        county_col = "in.nhgis_county_gisjoin"
        area_col = "calc.weighted.sqft"
        sec = "Com"
    else:
        county_col = "in.county"
        area_col = "in.units_represented"
        sec = "Res"

    combined_map = combine_keys(mymap[sector])
    mykeys = list(combined_map)

    if 'emm' in geos and 'cdiv' in geos:
        pivot_index, pivot_col = 'emm', 'cdiv'
        output_func = output_emm
        filename_geo = 'EMM'
    elif 'state' in geos and 'cdiv' in geos:
        pivot_index, pivot_col = 'state', 'cdiv'
        output_func = output_state
        filename_geo = 'State'
    else:
        raise ValueError(f"Unsupported geography combination for tech: {geos}")

    # Pre-load map CSVs once — avoid repeated disk I/O inside the eu loop
    map_dfs = {
        eu: pd.read_csv(os.path.join(mapping_dir, f"map_{sector[:3]}_{eu}.csv"))
        for eu in mykeys
        if os.path.exists(os.path.join(mapping_dir, f"map_{sector[:3]}_{eu}.csv"))
    }

    for weath in weathers:
        print(f"  Processing {sector} tech stock for {weath}...")
        if preloaded_dfs is not None and weath in preloaded_dfs:
            df_all = preloaded_dfs[weath].copy()
        else:
            df_all = pd.read_parquet(f"{filedir}{weath}/{filename}", engine='pyarrow')
            df_all = normalize_columns(df_all)
        df_all = ensure_columns(df_all, combined_map)
        df_all.rename(columns={county_col: 'county'}, inplace=True)
        df_all.rename(columns={'in.state': 'state'}, inplace=True)
        df_all.rename(columns={area_col: 'warea'}, inplace=True)
        df_all.reset_index(inplace=True)
        df_all = apply_geographies(df_all, scoutgeo_df, geos)
        df_all = df_all.dropna(subset=geos)

        all_eu = pd.DataFrame()
        for eu in mykeys:
            if eu not in map_dfs:
                print(f"    Skipping {eu}: map file not found")
                continue

            # Copy only the columns needed for this eu to reduce memory pressure.
            # Include map join columns so _apply_tech_map has attributes to match on.
            eu_source_cols = combined_map[eu]
            map_join_cols = [c for c in map_dfs[eu].columns
                             if c != 'scout_tech' and c in df_all.columns]
            needed_cols = list(dict.fromkeys(
                geos + ['warea'] + eu_source_cols + map_join_cols))
            df = df_all[[c for c in needed_cols if c in df_all.columns]].copy()
            df[eu] = df[eu_source_cols].sum(axis=1)
            df = df[df[eu] > 0]

            df = _apply_tech_map(df, map_dfs[eu])
            df = df[geos + ['scout_tech', 'warea']]
            tech_list = df['scout_tech'].dropna().unique().tolist()

            # Single groupby across all techs — avoids per-tech pivot_table aggregation
            df_grouped = (
                df.groupby([pivot_index, pivot_col, 'scout_tech'])['warea']
                .sum()
                .reset_index()
            )

            all_tech = pd.DataFrame()
            for tech in tech_list:
                tdf = (df_grouped[df_grouped['scout_tech'] == tech]
                       .drop(columns=['scout_tech']))
                # Use pivot (not pivot_table) since data is already aggregated
                conversion_matrix = tdf.pivot(
                    index=pivot_index, columns=pivot_col, values='warea')
                normalized_matrix = conversion_matrix.div(
                    conversion_matrix.sum(axis=0), axis=1).reset_index()
                all_tech = _tech_output_block(
                    normalized_matrix, output_func, eu, tech, all_tech)
            if not all_tech.empty:
                all_eu = (all_tech if all_eu.empty
                          else pd.concat([all_eu, all_tech], ignore_index=False))

        out_file = (f"{sec}_Cdiv_{filename_geo}_{weath}_Stock_electricity_Tech.csv")
        all_eu.to_csv(f"{outdir}/{out_file}", index=False)
        print(f"    Saved {out_file}")


def combine_hvac_and_other(output_dir):
    """Combine HVAC technology files with end-use files.

    NOTE: Technology-level disaggregation requires HVAC system mapping files
    that map building characteristics to Scout technology types. Without these
    mapping files, only end-use-level disaggregation is available.

    For end-use-level analysis (most common), technology files are not needed.
    """
    tech_dir = os.path.join(output_dir, "2024_technology")
    end_use_dir = os.path.join(output_dir, "2024_end_use")

    # Check if any tech files exist
    tech_files_exist = False
    if os.path.exists(tech_dir):
        tech_files = [f for f in os.listdir(tech_dir) if f.endswith('_Tech.csv')]
        tech_files_exist = len(tech_files) > 0

    if not tech_files_exist:
        print("\nSkipping technology file combination (no tech files generated)")
        print("  Technology-level disaggregation requires HVAC mapping files.")
        print("  Only end-use-level disaggregation files have been generated.")
        print("  This is sufficient for most Scout analyses.\n")
        return

    print("\nCombining HVAC tech and other end-use files...")

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

    combined_count = 0
    for filename in filenames:
        if "Stock" in filename:
            filename_eu = (f"{filename.replace('Stock', '')}"
                           f"electricity_Stock.csv")
            filename_tech = f"{filename}_electricity_Tech.csv"
        else:
            filename_eu = f"{filename}_electricity.csv"
            filename_tech = f"{filename}_electricity_Tech.csv"

        eu_path = os.path.join(end_use_dir, filename_eu)
        tech_path = os.path.join(tech_dir, filename_tech)

        # Only combine if both files exist
        if os.path.exists(eu_path) and os.path.exists(tech_path):
            df_eu = pd.read_csv(eu_path)
            df_tech = pd.read_csv(tech_path)
            combined = pd.concat([df_tech, df_eu], ignore_index=True)
            combined.to_csv(eu_path, index=False)
            print(f"  Combined {filename}")
            combined_count += 1

    if combined_count > 0:
        print(f"Combination complete ({combined_count} files combined).")
    else:
        print("No technology files found to combine.")


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
    parser.add_argument('--data-type', type=str, default='both',
                        choices=['end_use', 'technology', 'both'],
                        help='Which output type to generate: end_use, '
                             'technology, or both (default: both).')
    parser.add_argument('--mapping-dir', type=str, default='input/mapping',
                        help='Directory containing map_*.csv files '
                             '(default: input/mapping).')
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
    if args.data_type in ('technology', 'both'):
        os.makedirs(tech_outdir, exist_ok=True)
    if args.data_type in ('end_use', 'both'):
        os.makedirs(end_use_outdir, exist_ok=True)

    scoutgeo_df = get_scout_geo(script_dir)

    print("Starting disaggregation process...")

    # Check if input data exists
    resstock_data_path = os.path.join(args.resstock_path, args.weather_year,
                                      'baseline.parquet')
    comstock_data_path = os.path.join(args.comstock_path, args.weather_year,
                                      'baseline.parquet')

    weathers = [args.weather_year]

    # Pre-load parquet files once per sector so each process function receives
    # an already-read, normalized DataFrame instead of re-reading from disk.
    res_dfs = {}
    com_dfs = {}
    for weath in weathers:
        if os.path.exists(resstock_data_path):
            print(f"Pre-loading residential data for {weath}...")
            raw = pd.read_parquet(
                f"{args.resstock_path}/{weath}/baseline.parquet",
                engine='pyarrow')
            res_dfs[weath] = normalize_columns(raw)
        if os.path.exists(comstock_data_path):
            print(f"Pre-loading commercial data for {weath}...")
            raw = pd.read_parquet(
                f"{args.comstock_path}/{weath}/baseline.parquet",
                engine='pyarrow')
            com_dfs[weath] = normalize_columns(raw)

    # Define all fuel types to process
    fuel_types = ['electricity', 'natural gas', 'distillate', 'other fuel']

    # Define geography combinations to generate
    # Cdiv/EMM and Cdiv/State outputs are required
    geo_combinations = [
        (['emm', 'cdiv'], 'Cdiv/EMM'),
        (['cdiv', 'state'], 'Cdiv/State')
    ]

    if args.data_type in ('end_use', 'both'):
        if not os.path.exists(resstock_data_path):
            print(f"WARNING: ResStock data not found at: {resstock_data_path}")
            print("  Skipping residential processing.")
            print("  To generate residential disaggregation maps, provide "
                  "BuildStock parquet files.")
        else:
            print(f"Processing residential data from: {resstock_data_path}")

            for geos, geo_name in geo_combinations:
                print(f"\n  Generating {geo_name} outputs...")

                for fuel in fuel_types:
                    if fuel not in END_USE_MAP['residential']:
                        print(f"    Skipping {fuel}: no mapping defined")
                        continue

                    fuel_end_uses = END_USE_MAP['residential'][fuel]

                    try:
                        process_end_use_energy(
                            sector='residential',
                            filedir=f"{args.resstock_path}/",
                            filename='baseline.parquet',
                            weathers=weathers,
                            mymap=fuel_end_uses,
                            scoutgeo_df=scoutgeo_df,
                            geos=geos,
                            outdir=end_use_outdir,
                            fueltype=fuel,
                            preloaded_dfs=res_dfs
                        )
                    except Exception as e:
                        print(f"    ERROR processing residential {fuel} energy ({geo_name}): {e}")
                        traceback.print_exc()

                    try:
                        process_end_use_stock(
                            sector='residential',
                            filedir=f"{args.resstock_path}/",
                            filename='baseline.parquet',
                            weathers=weathers,
                            mymap=fuel_end_uses,
                            scoutgeo_df=scoutgeo_df,
                            geos=geos,
                            outdir=end_use_outdir,
                            fueltype=fuel,
                            preloaded_dfs=res_dfs
                        )
                    except Exception as e:
                        print(f"    ERROR processing residential {fuel} stock ({geo_name}): {e}")

        if not os.path.exists(comstock_data_path):
            print(f"WARNING: ComStock data not found at: {comstock_data_path}")
            print("  Skipping commercial processing.")
            print("  To generate commercial disaggregation maps, provide "
                  "BuildStock parquet files.")
        else:
            print(f"Processing commercial data from: {comstock_data_path}")

            for geos, geo_name in geo_combinations:
                print(f"\n  Generating {geo_name} outputs...")

                for fuel in fuel_types:
                    if fuel not in END_USE_MAP['commercial']:
                        print(f"    Skipping {fuel}: no mapping defined")
                        continue

                    fuel_end_uses = END_USE_MAP['commercial'][fuel]

                    try:
                        process_end_use_energy(
                            sector='commercial',
                            filedir=f"{args.comstock_path}/",
                            filename='baseline.parquet',
                            weathers=weathers,
                            mymap=fuel_end_uses,
                            scoutgeo_df=scoutgeo_df,
                            geos=geos,
                            outdir=end_use_outdir,
                            fueltype=fuel,
                            preloaded_dfs=com_dfs
                        )
                    except Exception as e:
                        print(f"    ERROR processing commercial {fuel} energy ({geo_name}): {e}")

                    try:
                        process_end_use_stock(
                            sector='commercial',
                            filedir=f"{args.comstock_path}/",
                            filename='baseline.parquet',
                            weathers=weathers,
                            mymap=fuel_end_uses,
                            scoutgeo_df=scoutgeo_df,
                            geos=geos,
                            outdir=end_use_outdir,
                            fueltype=fuel,
                            preloaded_dfs=com_dfs
                        )
                    except Exception as e:
                        print(f"    ERROR processing commercial {fuel} stock ({geo_name}): {e}")

    if args.data_type in ('technology', 'both'):
        if not os.path.exists(resstock_data_path):
            print(f"WARNING: ResStock data not found at: {resstock_data_path}")
            print("  Skipping residential technology processing.")
        else:
            print(f"\nProcessing residential technology data from: {resstock_data_path}")
            for geos, geo_name in geo_combinations:
                print(f"\n  Generating {geo_name} tech outputs...")
                try:
                    process_tech_energy(
                        sector='residential',
                        filedir=f"{args.resstock_path}/",
                        filename='baseline.parquet',
                        weathers=weathers,
                        mymap=FUEL_ENDUSE_MAP,
                        scoutgeo_df=scoutgeo_df,
                        geos=geos,
                        outdir=tech_outdir,
                        mapping_dir=args.mapping_dir,
                        preloaded_dfs=res_dfs
                    )
                except Exception as e:
                    print(f"    ERROR processing residential tech energy ({geo_name}): {e}")
                    traceback.print_exc()
                try:
                    process_tech_stock(
                        sector='residential',
                        filedir=f"{args.resstock_path}/",
                        filename='baseline.parquet',
                        weathers=weathers,
                        mymap=FUEL_ENDUSE_MAP,
                        scoutgeo_df=scoutgeo_df,
                        geos=geos,
                        outdir=tech_outdir,
                        mapping_dir=args.mapping_dir,
                        preloaded_dfs=res_dfs
                    )
                except Exception as e:
                    print(f"    ERROR processing residential tech stock ({geo_name}): {e}")
                    traceback.print_exc()

        if not os.path.exists(comstock_data_path):
            print(f"WARNING: ComStock data not found at: {comstock_data_path}")
            print("  Skipping commercial technology processing.")
        else:
            print(f"\nProcessing commercial technology data from: {comstock_data_path}")
            for geos, geo_name in geo_combinations:
                print(f"\n  Generating {geo_name} tech outputs...")
                try:
                    process_tech_energy(
                        sector='commercial',
                        filedir=f"{args.comstock_path}/",
                        filename='baseline.parquet',
                        weathers=weathers,
                        mymap=FUEL_ENDUSE_MAP,
                        scoutgeo_df=scoutgeo_df,
                        geos=geos,
                        outdir=tech_outdir,
                        mapping_dir=args.mapping_dir,
                        preloaded_dfs=com_dfs
                    )
                except Exception as e:
                    print(f"    ERROR processing commercial tech energy ({geo_name}): {e}")
                    traceback.print_exc()
                try:
                    process_tech_stock(
                        sector='commercial',
                        filedir=f"{args.comstock_path}/",
                        filename='baseline.parquet',
                        weathers=weathers,
                        mymap=FUEL_ENDUSE_MAP,
                        scoutgeo_df=scoutgeo_df,
                        geos=geos,
                        outdir=tech_outdir,
                        mapping_dir=args.mapping_dir,
                        preloaded_dfs=com_dfs
                    )
                except Exception as e:
                    print(f"    ERROR processing commercial tech stock ({geo_name}): {e}")
                    traceback.print_exc()

    print("\nDisaggregation process finished.")

    # Post-processing steps
    if args.data_type == 'both':
        combine_hvac_and_other(args.output_dir)
    fill_na_with_zeros(args.output_dir)

    # Install step
    if args.install:
        install_dir = os.path.abspath(
            os.path.join(script_dir, '..', '..', 'convert_data', 'geo_map'))
        install_files(args.output_dir, install_dir)


if __name__ == "__main__":
    main()
