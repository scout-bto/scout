
import gc
import pandas as pd
import os
import re
import json
import warnings
import argparse
import shutil
import sys
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
            # No natural_gas cooling column exists (gas cooling in ComStock is
            # near-zero); district_cooling is used as a proxy for direct-fired
            # absorption chillers instead.
            "cooling": ["out.district_cooling.cooling.energy_consumption"],
            "water heating": [
                "out.natural_gas.water_systems.energy_consumption",
                "out.district_heating.water_systems.energy_consumption"
            ],
            "misc": [
                "out.natural_gas.interior_equipment.energy_consumption"
            ]
        },
        # NOTE: ComStock 2024 lumped fuel oil and propane together into a
        # single "other_fuel" bucket. Starting with ComStock 2025, that
        # bucket is disaggregated into separate out.fuel_oil.* and
        # out.propane.* columns (mirroring the naming convention residential
        # ResStock already uses below) -- out.other_fuel.* itself is still
        # present in 2025 parquets but is entirely zero for every commercial
        # sample. distillate/other-fuel therefore source directly from
        # fuel_oil/propane, which is real 2025 data; on 2024 data those
        # columns don't exist and ensure_columns() zero-fills them instead
        # (2024 disaggregation for these two fuels is unsupported -- run
        # generate_geo_maps.py --year 2024 if that's ever needed). Neither
        # vintage has a fuel_oil/propane cooling column (genuine zero-stock
        # omission) or a raw (non-intensity) interior_equipment consumption
        # column, so cooling zero-fills and misc keeps pointing at the
        # natural_gas placeholder below.
        "distillate": {
            "heating": ["out.fuel_oil.heating.energy_consumption"],
            "cooling": ["out.fuel_oil.cooling.energy_consumption"],
            "water heating": [
                "out.fuel_oil.water_systems.energy_consumption"
            ],
            # FIXME: distillate "misc" points at a natural_gas column. Likely
            # should be out.fuel_oil.interior_equipment.energy_consumption,
            # but that column doesn't exist as raw consumption (only as
            # _savings/_intensity variants) in ComStock 2025, and doesn't
            # exist at all in ComStock 2024.
            "misc": [
                "out.natural_gas.interior_equipment.energy_consumption"
            ]
        },
        "other fuel": {
            "heating": ["out.propane.heating.energy_consumption"],
            "cooling": ["out.propane.cooling.energy_consumption"],
            "water heating": [
                "out.propane.water_systems.energy_consumption"
            ],
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
            # No fuel_oil misc/pool_heater column exists in ResStock; reuse
            # fuel_oil hot_water as the geographic proxy instead of another
            # fuel's column, since what matters here is where fuel oil
            # itself is delivered, not the end use it's attributed to.
            "misc": [
                "out.fuel_oil.hot_water.energy_consumption"
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
            # No propane misc/pool_heater column exists in ResStock; reuse
            # propane hot_water as the geographic proxy instead of another
            # fuel's column, since what matters here is where propane
            # itself is delivered, not the end use it's attributed to.
            "misc": [
                "out.propane.hot_water.energy_consumption"
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

# Canonical geo membership lists, keyed the same way geo_pivot_settings'
# geo_label/filename_geo values are -- used to reindex pivoted output back
# to full geo coverage, since pandas' pivot() silently drops a geo
# altogether (rather than a zero-valued row/column) when it has zero
# samples for a given end use/tech (e.g. no distillate-heated homes
# sampled in Arkansas). Left as an absent row/column, that gap doesn't
# surface here -- it surfaces as a KeyError deep in
# final_mseg_converter.py, which expects every CDIV/State/EMM to be
# present even when the true value for that geo is zero.
CDIV_LIST = [str(i) for i in range(1, 10)]
EMM_LIST = DF_ORDER['emm_intersect'].tolist()
STATE_LIST = sorted(pd.read_csv(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 'scout_geography.csv'), dtype=str)['state'].unique().tolist())
GEO_LISTS = {'CDIV': CDIV_LIST, 'State': STATE_LIST, 'EMM': EMM_LIST}


def ensure_geo_coverage(df, row_geo, col_geo, context):
    """Reindex df (rows indexed by row_geo values, columns holding col_geo
    values plus any extra non-geo columns like 'Total') against the full
    canonical geo lists in GEO_LISTS, zero-filling any row/column a pivot
    dropped because that geo had zero samples for this eu/tech, and
    printing a note when it does.
    """
    row_list = GEO_LISTS[row_geo]
    missing_rows = [r for r in row_list if r not in df.index]
    if missing_rows:
        print(f"    Note: {context} has no samples in {row_geo}(s) "
              f"{missing_rows}; zero-filling those rows.")
        df = df.reindex(row_list, fill_value=0)

    col_list = GEO_LISTS[col_geo]
    missing_cols = [c for c in col_list if c not in df.columns]
    if missing_cols:
        print(f"    Note: {context} has no samples in {col_geo}(s) "
              f"{missing_cols}; zero-filling those columns.")
        extra_cols = [c for c in df.columns if c not in col_list]
        df = df.reindex(columns=col_list + extra_cols, fill_value=0)
    return df


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


def normalize_county_ids(df, dfdict):
    """Translate 'ST, County Name' county identifiers to GISJOIN codes.

    2025 ResStock identifies AK/HI counties as e.g. 'AK, Yukon-Koyukuk
    Census Area' instead of the GISJOIN codes (e.g. 'G0200130') used for
    every other state and vintage, so those rows fail the GISJOIN-keyed
    join below and silently drop out. Build a (state, county_name) ->
    GISJOIN lookup from the geography crosswalk and rewrite any
    name-formatted county values to GISJOIN before the join runs.
    """
    is_named = df['county'].str.match(r'^[A-Z]{2}, ')
    if not is_named.any():
        return df
    name_key = dfdict['state'] + ', ' + dfdict['county_name']
    name_to_gisjoin = dict(zip(name_key, dfdict['gisjoin']))
    df.loc[is_named, 'county'] = df.loc[is_named, 'county'].map(name_to_gisjoin)
    return df


def apply_geographies(df, dfdict, geos):
    df['county'] = df['county'].astype(str)
    df = normalize_county_ids(df, dfdict)
    for geo in geos:
        if geo == 'emm':
            geocol = 'emm2020_county'
        elif geo == 'cdiv':
            geocol = 'cdiv'
        else:
            geocol = geo
        d = dfdict.set_index('gisjoin').T.to_dict('index')[geocol]
        df[geo] = df['county'].map(d)
        if geo == 'emm':
            # AK/HI have no real NEMS EMM region (see the 'AK_HI'
            # placeholder set in get_scout_geo); exclude them from
            # EMM-based disaggregation while still letting cdiv/state
            # resolve to their real values above.
            df.loc[df[geo] == 'AK_HI', geo] = pd.NA
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


def normalize_by_column_sum(conversion_matrix, context):
    """Divide each geo column of `conversion_matrix` by its own sum, turning
    raw values into shares that sum to 1 -- and warn about any column whose
    sum is zero before doing so.

    A zero column sum turns the divide below into 0/0, which downstream
    fillna(0) calls silently turn into a share of 0, indistinguishable from
    a geo genuinely having no energy/stock for this end use. Most of the
    time a zero column really is that (e.g. a niche end use with no samples
    in a small state), but it's also the signature of a broken data import
    (a renamed/misspelled source column that ensure_columns() silently
    zero-filled). Printing it here, at generation time, means a bad import
    shows up immediately in the console instead of only being spottable by
    later eyeballing the output CSV/JSON for a suspicious all-zero column.
    """
    col_sums = conversion_matrix.sum(axis=0)
    zero_cols = col_sums[col_sums == 0].index.tolist()
    if zero_cols:
        if len(zero_cols) == len(col_sums):
            print(f"    WARNING: {context} sums to ZERO across every geo "
                  f"({len(zero_cols)} column(s)) -- check for a broken or "
                  f"renamed source column rather than assuming genuine zero "
                  f"data. Columns: {zero_cols}")
        else:
            print(f"    Note: {context} sums to zero for "
                  f"{len(zero_cols)} geo column(s) (share reported as 0): "
                  f"{zero_cols}")
    return conversion_matrix.div(col_sums, axis=1)


def finalize_eu_matrix(conversion_matrix, output_func, geo_label, col_geo, eu,
                       drop_total=False):
    """Normalize a raw (geo x geo) conversion matrix for one end use and
    format it into the 'End use'/geo_label-indexed row block used by all of
    the output CSVs.

    Shared by process_end_use_energy, process_end_use_stock, and
    process_gap_end_use so the normalization/output formatting (including
    the CDIV/EMM/state sort order from output_emm/output_state) stays
    identical across all three, even though how each one builds the raw
    conversion_matrix differs. Always emits full geo coverage on both axes
    (see ensure_geo_coverage) -- a geo with zero samples for this end use
    (e.g. no distillate-heated homes in Arkansas) is zero-filled rather
    than left as a missing row/column, which final_mseg_converter.py
    would otherwise fail to look up.
    """
    normalized_matrix = normalize_by_column_sum(
        conversion_matrix, f"end use '{eu}'").reset_index()
    normalized_matrix = output_func(normalized_matrix)
    normalized_matrix = normalized_matrix.fillna(0)
    normalized_matrix.columns = normalized_matrix.iloc[0]
    normalized_matrix.rename(
        columns={normalized_matrix.columns[-1]: 'Total'}, inplace=True)
    normalized_matrix = normalized_matrix.iloc[1:]
    normalized_matrix = ensure_geo_coverage(
        normalized_matrix, geo_label, col_geo, f"end use '{eu}'")
    normalized_matrix.insert(0, geo_label, normalized_matrix.index)
    normalized_matrix.insert(0, 'End use', eu)
    if drop_total:
        normalized_matrix.drop(columns=['Total'], inplace=True)
    return normalized_matrix


def geo_pivot_settings(geos):
    """Return the (group_cols, pivot_index, pivot_col, output_func,
    geo_label, filename_geo) tuple for a given geos combination, matching
    the branching already duplicated across process_end_use_energy and
    process_end_use_stock.
    """
    if 'emm' in geos and 'state' in geos:
        return (['emm', 'state'], 'emm', 'state', output_emm, 'State', 'EMM')
    elif 'cdiv' in geos and 'state' in geos:
        return (['cdiv', 'state'], 'state', 'cdiv', output_state, 'CDIV', 'State')
    elif 'cdiv' in geos and 'emm' in geos:
        return (['cdiv', 'emm'], 'emm', 'cdiv', output_emm, 'CDIV', 'EMM')
    else:
        raise ValueError(f"Unsupported geography combination: {geos}")


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
    needed_cols = list(dict.fromkeys(
        [county_col, 'in.state'] + [c for cols in mymap.values() for c in cols]
    ))
    for weath in weathers:
        print(f"  Processing {sector} end-use energy ({fueltype}) for {weath}...")
        if preloaded_dfs is not None and weath in preloaded_dfs:
            src = preloaded_dfs[weath]
            available = [c for c in needed_cols if c in src.columns]
            df = src[available].copy()
        else:
            df = pd.read_parquet(f"{filedir}{weath}/{filename}",
                                 engine='pyarrow')
            df = normalize_columns(df)
        df = ensure_columns(df, mymap)

        df.rename(columns={county_col: 'county', 'in.state': 'state'}, inplace=True)

        for eu in mykeys:
            df[eu] = df[mymap[eu]].sum(axis=1)

        df.reset_index(inplace=True)
        df = apply_geographies(df, scoutgeo_df, geos)
        df = df.dropna(subset=geos)
        df = df[geos + mykeys]

        # Determine groupby columns based on geos
        group_cols, pivot_index, pivot_col, output_func, geo_label, \
            filename_geo = geo_pivot_settings(geos)

        df = df.groupby(group_cols).sum().reset_index()

        norm_pd = pd.DataFrame()
        for eu in mykeys:
            conversion_matrix = df.pivot(index=pivot_index, columns=pivot_col,
                                         values=eu)
            normalized_matrix = finalize_eu_matrix(
                conversion_matrix, output_func, geo_label, filename_geo, eu,
                drop_total=True)
            norm_pd = (normalized_matrix if norm_pd.empty
                       else pd.concat([norm_pd, normalized_matrix],
                                      ignore_index=False))

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

    needed_cols = list(dict.fromkeys(
        [county_col, "in.state", area_col] +
        [c for cols in mymap.values() for c in cols]
    ))
    for weath in weathers:
        print(f"  Processing {sector} end-use stock ({fueltype}) for {weath}...")
        if preloaded_dfs is not None and weath in preloaded_dfs:
            src = preloaded_dfs[weath]
            available = [c for c in needed_cols if c in src.columns]
            alldf = src[available].copy()
            missing = sorted(set(needed_cols) - set(available))
            for c in missing:
                alldf[c] = 0.0
            if missing:
                print(f"    Zero-filled {len(missing)} absent column(s): {missing}")
        else:
            alldf = pd.read_parquet(f"{filedir}{weath}/{filename}",
                                    engine='pyarrow')
            alldf = normalize_columns(alldf)
            alldf = ensure_columns(alldf, mymap)

        alldf.rename(columns={county_col: "county", "in.state": "state",
                              area_col: "warea"}, inplace=True)

        if "warea" not in alldf.columns:
            raise KeyError(
                f"Area column '{area_col}' not found after normalization. "
                f"Check its exact spelling in the {sector} parquet "
                f"(normalize_columns may have altered it).")

        mykeys = list(mymap)
        norm_pd = pd.DataFrame()

        # Determine groupby columns based on geos
        _, pivot_index, pivot_col, output_func, geo_label, filename_geo = \
            geo_pivot_settings(geos)

        for eu in mykeys:
            df = eu_rows(alldf, eu, conditions_dict)
            df = apply_geographies(df, scoutgeo_df, geos)
            df = df[["warea"] + geos]

            conversion_matrix = df.pivot_table(
                index=pivot_index, columns=pivot_col, values="warea",
                aggfunc='sum')
            del df
            gc.collect()
            normalized_matrix = finalize_eu_matrix(
                conversion_matrix, output_func, geo_label, filename_geo, eu,
                drop_total=False)
            del conversion_matrix
            norm_pd = (normalized_matrix if norm_pd.empty
                       else pd.concat([norm_pd, normalized_matrix],
                                      ignore_index=False))

        fuel_suffix = f"_{remove_space(fueltype)}" if fueltype else ""
        norm_pd.to_csv(f"{outdir}/{sec}_Cdiv_{filename_geo}_{weath}{fuel_suffix}_Stock.csv",
                       index=False)
        print(f"    Saved {sec}_Cdiv_{filename_geo}_{weath}{fuel_suffix}_Stock.csv")


def process_gap_end_use(gap_csv_path, scoutgeo_df, geos, target_paths):
    """Compute a normalized 'gap' End-use row from the ComStock gap model's
    annual county electricity totals, and append it to each already-written
    commercial electricity end-use-level disaggregation CSV in target_paths.

    Real ComStock gap SDR data (commercial_gap_model/by_county/upgrade=0/ on
    the OEDI bucket, see download_buildstock.download_comstock_gap) only
    covers electricity. final_mseg_converter.py reuses this same row as the
    geographic proxy for gap blending across all fuels, since no
    fuel-specific gap geography exists in the source data.

    Only end-use-level files are targeted here -- combine_hvac_and_other()
    (run after this, as part of the `--data-type both` post-processing
    step) already copies every technology-less end-use row, tagged
    Technology == "all", into the corresponding technology-level file; the
    "gap" row added here rides along automatically the same way "misc",
    "lighting", etc. do, without needing its own separate technology-level
    handling.
    """
    if not os.path.exists(gap_csv_path):
        print(f"    WARNING: gap model data not found at {gap_csv_path}; "
              "skipping 'gap' row (run download_buildstock.py to fetch it).")
        return

    df = pd.read_csv(gap_csv_path)
    df = apply_geographies(df, scoutgeo_df, geos)
    df = df.dropna(subset=geos)

    _, pivot_index, pivot_col, output_func, geo_label, filename_geo = \
        geo_pivot_settings(geos)

    grouped = df.groupby([pivot_index, pivot_col])[
        'annual_electricity_kwh'].sum().reset_index()
    conversion_matrix = grouped.pivot(
        index=pivot_index, columns=pivot_col, values='annual_electricity_kwh')
    gap_row = finalize_eu_matrix(
        conversion_matrix, output_func, geo_label, filename_geo, 'gap',
        drop_total=False)

    for path in target_paths:
        if not os.path.exists(path):
            print(f"    WARNING: {path} not found; skipping 'gap' row append.")
            continue
        existing = pd.read_csv(path)
        # Idempotent: drop any previously-appended gap row(s) first, so
        # re-running this step (e.g. a --data-type technology-only rerun
        # against end-use files left over from an earlier run) doesn't pile
        # up duplicates.
        existing = existing[existing['End use'] != 'gap']
        row = gap_row.reindex(columns=existing.columns, fill_value=0.0)
        combined = pd.concat([existing, row], ignore_index=True)
        combined.to_csv(path, index=False)
        print(f"    Appended 'gap' row to {os.path.basename(path)}")


def _apply_tech_map(df, map_df):
    """Assign scout_tech to each row by merging on all non-scout_tech columns."""
    merge_cols = [c for c in map_df.columns if c != 'scout_tech' and c in df.columns]
    df = df.copy()
    df['_orig_idx'] = range(len(df))
    merged = df.merge(map_df[merge_cols + ['scout_tech']], on=merge_cols, how='left')
    # If map rows have overlapping conditions, keep last match (preserves original priority)
    merged = merged.drop_duplicates(subset=['_orig_idx'], keep='last')
    return merged.drop(columns=['_orig_idx'])


def _tech_output_block(normalized_matrix, output_func, col_geo, eu, tech, all_tech):
    """Normalize, format, and accumulate one technology's matrix.

    Always emits one row per CDIV (1-9) and one column per State/EMM,
    zero-filling any geo this tech has zero samples for (conversion_matrix
    simply has no row/column for a geo with no data at all, rather than a
    zero-valued one). This matters because final_mseg_converter.py looks
    up rows by position (cd_num, 0-8) after filtering to a Technology, and
    columns by name (e.g. a state abbreviation) -- a missing CDIV row
    would silently shift every later CDIV into the wrong slot (or raise
    an out-of-bounds error if the gap were CDIV 9), while a missing
    State/EMM column raises a hard KeyError on lookup.
    """
    normalized_matrix = output_func(normalized_matrix)
    normalized_matrix = normalized_matrix.fillna(0)
    normalized_matrix.columns = normalized_matrix.iloc[0]
    normalized_matrix.rename(
        columns={normalized_matrix.columns[-1]: 'Total'}, inplace=True)
    normalized_matrix = normalized_matrix.iloc[1:]

    normalized_matrix = ensure_geo_coverage(
        normalized_matrix, 'CDIV', col_geo, f"tech '{tech}' / end use '{eu}'")

    normalized_matrix.insert(0, 'CDIV', normalized_matrix.index)
    normalized_matrix.insert(0, 'End use', eu.split('_')[1])
    normalized_matrix.insert(0, 'Technology', tech)
    normalized_matrix = normalized_matrix.drop(columns=['Total'])
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
                normalized_matrix = normalize_by_column_sum(
                    conversion_matrix, f"end use '{eu}' / tech '{tech}'"
                ).reset_index()
                all_tech = _tech_output_block(
                    normalized_matrix, output_func, filename_geo, eu, tech,
                    all_tech)
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
                normalized_matrix = normalize_by_column_sum(
                    conversion_matrix, f"end use '{eu}' / tech '{tech}'"
                ).reset_index()
                all_tech = _tech_output_block(
                    normalized_matrix, output_func, filename_geo, eu, tech,
                    all_tech)
            if not all_tech.empty:
                all_eu = (all_tech if all_eu.empty
                          else pd.concat([all_eu, all_tech], ignore_index=False))

        out_file = (f"{sec}_Cdiv_{filename_geo}_{weath}_electricity_Stock_Tech.csv")
        all_eu.to_csv(f"{outdir}/{out_file}", index=False)
        print(f"    Saved {out_file}")


def combine_hvac_and_other(output_dir, year="2025", weather_year="amy2018"):
    """Combine HVAC technology files with end-use files.

    NOTE: Technology-level disaggregation requires HVAC system mapping files
    that map building characteristics to Scout technology types. Without these
    mapping files, only end-use-level disaggregation is available.

    For end-use-level analysis (most common), technology files are not needed.
    """
    tech_dir = os.path.join(output_dir, f"{year}_technology")
    end_use_dir = os.path.join(output_dir, f"{year}_end_use")

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
        f"Com_Cdiv_EMM_{weather_year}",
        f"Com_Cdiv_State_{weather_year}",
        f"Res_Cdiv_EMM_{weather_year}",
        f"Res_Cdiv_State_{weather_year}",
        f"Com_Cdiv_EMM_{weather_year}_Stock",
        f"Com_Cdiv_State_{weather_year}_Stock",
        f"Res_Cdiv_EMM_{weather_year}_Stock",
        f"Res_Cdiv_State_{weather_year}_Stock"
    ]

    combined_count = 0
    for filename in filenames:
        if "Stock" in filename:
            filename_eu = (f"{filename.replace('Stock', '')}"
                           f"electricity_Stock.csv")
            filename_tech = f"{filename.replace('_Stock', '')}_electricity_Stock_Tech.csv"
        else:
            filename_eu = f"{filename}_electricity.csv"
            filename_tech = f"{filename}_electricity_Tech.csv"

        eu_path = os.path.join(end_use_dir, filename_eu)
        tech_path = os.path.join(tech_dir, filename_tech)

        # Only combine if both files exist
        if os.path.exists(eu_path) and os.path.exists(tech_path):
            df_eu = pd.read_csv(eu_path)
            df_tech = pd.read_csv(tech_path)
            # df_eu has no Technology column (it's plain per-CDIV data with
            # no per-technology breakdown). final_mseg_converter.py's envelope/
            # "demand" disaggregation path looks up Technology=='all' for
            # exactly these rows, so label them explicitly rather than leaving
            # them NaN -- fill_na_with_zeros() would otherwise turn a blank
            # Technology into the string "0".
            df_eu.insert(0, 'Technology', 'all')
            # Written to tech_path (not eu_path): final_mseg_converter.py's
            # technology-level disaggregation reads the "_Tech" file expecting
            # it to cover every end use -- Technology-specific rows for
            # heating/cooling plus the plain per-CDIV rows for everything
            # else (misc, lighting, etc.), positionally indexed 1 row per
            # CDIV. Leaving eu_path untouched preserves it for the separate
            # end-use-level disaggregation path, which relies on that same
            # 1-row-per-CDIV positional indexing and would break if
            # Technology-duplicated rows were merged in.
            combined = pd.concat([df_tech, df_eu], ignore_index=True)
            combined.to_csv(tech_path, index=False)
            print(f"  Combined {filename}")
            combined_count += 1

    if combined_count > 0:
        print(f"Combination complete ({combined_count} files combined).")
    else:
        print("No technology files found to combine.")


def fill_na_with_zeros(output_dir, year="2025"):
    """Fill NA values with 0 in all generated CSV files."""
    print("Filling NA values with 0...")
    for folder_name in [f"{year}_end_use", f"{year}_technology"]:
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


SDR_VERSION_FILENAME = "sdr_version.json"


def read_sdr_version(dataset_path, weather_year):
    """Read the SDR release download_buildstock.py recorded for a dataset.

    Returns "unknown" if the dataset predates that metadata file (e.g.
    it was downloaded before this tracking was added), so older data
    can still be processed without erroring here.
    """
    meta_path = os.path.join(dataset_path, weather_year, SDR_VERSION_FILENAME)
    if not os.path.exists(meta_path):
        return "unknown"
    with open(meta_path) as f:
        return json.load(f)["version"]


def write_combined_sdr_version(output_dir, resstock_path, comstock_path,
                               weather_year):
    """Combine the residential/commercial SDR versions into one file
    alongside the generated CSVs, so final_mseg_converter.py can report
    which SDR release the disaggregation factors it reads came from.
    """
    combined = {
        "residential": read_sdr_version(resstock_path, weather_year),
        "commercial": read_sdr_version(comstock_path, weather_year),
    }
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, SDR_VERSION_FILENAME), "w") as f:
        json.dump(combined, f, indent=2)
    print(f"  Saved {SDR_VERSION_FILENAME}: {combined}")


def install_files(output_dir, install_dir, year="2025"):
    print(f"Installing generated files to {install_dir}...")
    if not os.path.exists(install_dir):
        os.makedirs(install_dir)

    source_dirs = [
        os.path.join(output_dir, f"{year}_end_use"),
        os.path.join(output_dir, f"{year}_technology")
    ]

    for source_dir in source_dirs:
        if os.path.exists(source_dir):
            for filename in os.listdir(source_dir):
                if filename.endswith(".csv"):
                    source_file = os.path.join(source_dir, filename)
                    dest_file = os.path.join(install_dir, filename)
                    shutil.copy2(source_file, dest_file)
                    print(f"  Copied {filename}")

    sdr_version_file = os.path.join(output_dir, SDR_VERSION_FILENAME)
    if os.path.exists(sdr_version_file):
        shutil.copy2(sdr_version_file,
                     os.path.join(install_dir, SDR_VERSION_FILENAME))
        print(f"  Copied {SDR_VERSION_FILENAME}")

    print("Installation complete.")


def main():
    parser = argparse.ArgumentParser(
        description="Generate geographic disaggregation maps from ResStock and "
                    "ComStock data.",
        # Without this, an unrecognized flag that happens to be an
        # unambiguous prefix of a real one (e.g. the old --install, now
        # --no-install/--install-only) is silently accepted as that flag
        # instead of erroring -- exactly the kind of mistake this script's
        # own history just demonstrated is easy to make.
        allow_abbrev=False)
    parser.add_argument('--year', type=str, default='2025',
                        choices=['2024', '2025'],
                        help='BuildStock release year (default: 2025).')
    parser.add_argument('--weather-year', type=str, default='amy2018',
                        help='Weather year (e.g. amy2018 or tmy3).')
    parser.add_argument('--comstock-path', type=str, default=None,
                        help='Path to ComStock data directory '
                             '(default: input/<year>_comstock).')
    parser.add_argument('--resstock-path', type=str, default=None,
                        help='Path to ResStock data directory '
                             '(default: input/<year>_resstock).')
    parser.add_argument('--output-dir', type=str, default='output',
                        help='Directory to save the output CSV '
                             'files.')
    parser.add_argument('--data-type', type=str, default=None,
                        choices=['end_use', 'technology', 'both'],
                        help='Which output type to generate: end_use, '
                             'technology, or both. Defaults to both. '
                             'Ignored with --install-only.')
    parser.add_argument('--mapping-dir', type=str, default='input/mapping',
                        help='Directory containing map_*.csv files '
                             '(default: input/mapping).')
    parser.add_argument('--all', action='store_true',
                        help='Generate all output files (default behavior).')
    parser.add_argument('--force', action='store_true',
                        help='Overwrite existing output files.')
    parser.add_argument('--sector', type=str, default='both',
                        choices=['residential', 'commercial', 'both'],
                        help='Which sector to process: residential, commercial, '
                             'or both (default: both).')
    parser.add_argument('--no-install', action='store_true',
                        help='Generate into the scratch output/ directory '
                             'without copying to convert_data/geo_map/.')
    parser.add_argument('--install-only', action='store_true',
                        help='Skip generation; just copy the existing '
                             'output/ files to convert_data/geo_map/.')

    args = parser.parse_args()

    if args.install_only and args.no_install:
        parser.error('--install-only and --no-install cannot both be set.')

    # Collected across every try/except below so a batch run over many
    # sector/geo/fuel combinations can still fail loudly (nonzero exit,
    # printed at the end) instead of always exiting 0 even when every
    # combination silently errored out.
    failures = []

    run_generation = not args.install_only
    do_install = not args.no_install
    if args.data_type is None:
        args.data_type = 'both'

    # Apply year-based defaults for paths not explicitly provided
    if args.comstock_path is None:
        args.comstock_path = f"input/{args.year}_comstock"
    if args.resstock_path is None:
        args.resstock_path = f"input/{args.year}_resstock"

    # Define base directory relative to the script location
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define output subdirectories
    tech_outdir = os.path.join(args.output_dir, f'{args.year}_technology')
    end_use_outdir = os.path.join(args.output_dir, f'{args.year}_end_use')

    if not run_generation:
        # --install-only: skip all data loading and generation.
        install_dir = os.path.abspath(
            os.path.join(script_dir, '..', 'convert_data', 'geo_map'))
        install_files(args.output_dir, install_dir, year=args.year)
        return

    if args.data_type in ('technology', 'both'):
        os.makedirs(tech_outdir, exist_ok=True)
    if args.data_type in ('end_use', 'both'):
        os.makedirs(end_use_outdir, exist_ok=True)

    write_combined_sdr_version(
        args.output_dir, args.resstock_path, args.comstock_path,
        args.weather_year)

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
        if args.sector in ('residential', 'both') and os.path.exists(resstock_data_path):
            print(f"Pre-loading residential data for {weath}...")
            raw = pd.read_parquet(
                f"{args.resstock_path}/{weath}/baseline.parquet",
                engine='pyarrow')
            res_dfs[weath] = normalize_columns(raw)
        if args.sector in ('commercial', 'both') and os.path.exists(comstock_data_path):
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
        if args.sector not in ('residential', 'both'):
            print("Skipping residential end-use processing (--sector commercial).")
        elif not os.path.exists(resstock_data_path):
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
                        msg = f"residential {fuel} energy ({geo_name}): {e}"
                        print(f"    ERROR processing {msg}")
                        traceback.print_exc()
                        failures.append(msg)

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
                        msg = f"residential {fuel} stock ({geo_name}): {e}"
                        print(f"    ERROR processing {msg}")
                        traceback.print_exc()
                        failures.append(msg)

        if args.sector not in ('commercial', 'both'):
            print("Skipping commercial end-use processing (--sector residential).")
        elif not os.path.exists(comstock_data_path):
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
                        msg = f"commercial {fuel} energy ({geo_name}): {e}"
                        print(f"    ERROR processing {msg}")
                        traceback.print_exc()
                        failures.append(msg)

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
                        msg = f"commercial {fuel} stock ({geo_name}): {e}"
                        print(f"    ERROR processing {msg}")
                        traceback.print_exc()
                        failures.append(msg)

    if args.data_type in ('technology', 'both'):
        if args.sector not in ('residential', 'both'):
            print("Skipping residential technology processing (--sector commercial).")
        elif not os.path.exists(resstock_data_path):
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
                    msg = f"residential tech energy ({geo_name}): {e}"
                    print(f"    ERROR processing {msg}")
                    traceback.print_exc()
                    failures.append(msg)
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
                    msg = f"residential tech stock ({geo_name}): {e}"
                    print(f"    ERROR processing {msg}")
                    traceback.print_exc()
                    failures.append(msg)

        if args.sector not in ('commercial', 'both'):
            print("Skipping commercial technology processing (--sector residential).")
        elif not os.path.exists(comstock_data_path):
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
                    msg = f"commercial tech energy ({geo_name}): {e}"
                    print(f"    ERROR processing {msg}")
                    traceback.print_exc()
                    failures.append(msg)
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
                    msg = f"commercial tech stock ({geo_name}): {e}"
                    print(f"    ERROR processing {msg}")
                    traceback.print_exc()
                    failures.append(msg)

    print("\nDisaggregation process finished.")

    # Append the ComStock gap model's electricity "gap" row (see
    # process_gap_end_use) to the commercial electricity end-use-level CSVs
    # (energy + stock, EMM + State). Must run before combine_hvac_and_other
    # below, which copies every technology-less end-use row (tagged
    # Technology == "all") -- now including "gap" -- into the corresponding
    # technology-level file, exactly the way it already does for "misc",
    # "lighting", etc. Real gap SDR data only covers electricity;
    # final_mseg_converter.py reuses this row for all fuels' gap blending,
    # so no other fuel's files get a "gap" row.
    if args.sector in ('commercial', 'both'):
        gap_csv_path = os.path.join(
            args.comstock_path, 'gap', 'annual_electricity_by_county.csv')
        for geos, geo_name in geo_combinations:
            print(f"\nAdding ComStock gap row to {geo_name} "
                  "commercial electricity outputs...")
            _, _, _, _, _, filename_geo = geo_pivot_settings(geos)
            for weath in weathers:
                target_paths = [
                    os.path.join(
                        end_use_outdir,
                        f"Com_Cdiv_{filename_geo}_{weath}_electricity.csv"),
                    os.path.join(
                        end_use_outdir,
                        f"Com_Cdiv_{filename_geo}_{weath}_electricity_Stock.csv"),
                ]
                try:
                    process_gap_end_use(
                        gap_csv_path, scoutgeo_df, geos, target_paths)
                except Exception as e:
                    msg = f"commercial gap row ({geo_name}): {e}"
                    print(f"    ERROR processing {msg}")
                    traceback.print_exc()
                    failures.append(msg)

    # Post-processing steps
    if args.data_type == 'both':
        combine_hvac_and_other(
            args.output_dir, year=args.year, weather_year=args.weather_year)
    fill_na_with_zeros(args.output_dir, year=args.year)

    # Install step
    if do_install:
        install_dir = os.path.abspath(
            os.path.join(script_dir, '..', 'convert_data', 'geo_map'))
        install_files(args.output_dir, install_dir, year=args.year)

    if failures:
        print(f"\n{len(failures)} processing step(s) failed:")
        for msg in failures:
            print(f"  - {msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
