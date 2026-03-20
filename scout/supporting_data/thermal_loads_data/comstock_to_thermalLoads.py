'''
ComStock to Scout Thermal Loads Converter

This script processes ComStock Building Energy Simulation Outputs
and converts them into thermal loads component data formatted for
use in Scout's building energy analysis tool.

The conversion steps:
1. Create maps for ComStock building characteristics to categories as used in Scout.
2. Aggregate thermal load components by census division, building type, and end use.
3. Compute weighted average based on ComStock sample weights.
4. Normalize component loads as fractions of total thermal load.
5. Obtain normalized component loads for missing building types by applying
a weighted area average of the existing building types.

Output format:
Tab seperated text file with columns:
- ENDUSE: 'HT' for heating, 'CL' for cooling

- CDIV: Census Division code (1: new england, 2: mid atlantic, 3: east north central,
4: west north central, 5: south atlantic, 6: east south central, 7: west south central,
8: mountain, 9: pacific)

- BLDG: Building type code (1: assembly, 2: education, 3: food sales, 4: food service,
5: health care, 6: lodging, 7: large office, 8: small office, 9: mercantile/service,
10: warehouse, 11: other)

- Component fractions: WIND_COND, WIND_SOL, ROOF, WALL, INFIL, PEOPLE, GRND,
EQUIP_ELEC, EQUIP_NELEC, FLOOR, LIGHTS, VENT
'''

import pandas as pd

CDIV_MAX = 9
BLDG_MAX = 11
EUSES = ["HEAT", "COOL"]

# Segment -> category aggregation (intermediate keys)
COMSTOCK_SEGMENT_TO_CATEGORY = {
    # Windows
    "win_cond": "WIND_COND",
    "win_sol": "WIND_SOL",
    # Roof / ceilings
    "roof": "ROOF",
    # Walls / opaque
    "ext_wall": "WALL",
    "fnd_wall": "WALL",
    "door": "WALL",
    # Infiltration / ventilation
    "infil": "INFIL",
    # ventilation
    "vent": "VENT",
    # People
    "people_gain": "PEOPLE",
    # Ground contact
    "gnd_flr": "GRND",
    # equipment gains
    "equip_gain": "EQUIP",
    # refrigeration gains
    "ref_equip_gain": "REFRIG",
    # Floor
    "ext_flr": "FLOOR",
    # Non Electric equipment gains
    "light_gain": "LIGHTS",
}

# state mapping to cencus division
CDIV_MAPPING = {
    # Northeast
    "CT": 1,
    "ME": 1,
    "MA": 1,
    "NH": 1,
    "RI": 1,
    "VT": 1,
    "NJ": 2,
    "NY": 2,
    "PA": 2,

    # Midwest
    "IN": 3,
    "IL": 3,
    "MI": 3,
    "OH": 3,
    "WI": 3,
    "IA": 4,
    "KS": 4,
    "MN": 4,
    "MO": 4,
    "NE": 4,
    "ND": 4,
    "SD": 4,

    # South
    "DE": 5,
    "DC": 5,
    "FL": 5,
    "GA": 5,
    "MD": 5,
    "NC": 5,
    "SC": 5,
    "VA": 5,
    "WV": 5,
    "AL": 6,
    "KY": 6,
    "MS": 6,
    "TN": 6,
    "AR": 7,
    "LA": 7,
    "OK": 7,
    "TX": 7,

    # West
    "AZ": 8,
    "CO": 8,
    "ID": 8,
    "MT": 8,
    "NV": 8,
    "NM": 8,
    "UT": 8,
    "WY": 8,
    "AK": 9,
    "CA": 9,
    "HI": 9,
    "OR": 9,
    "WA": 9,
}

# Education building type has an ID of 2. “SecondarySchool” is
# classified as an education building type,
# but here it is mapped to 12 instead of 2 to calculate
# the component loads for the assembly building type.
BLDG_MAPPING = {
    "Hospital": 5,
    "Outpatient": 5,
    "RetailStripmall": 9,
    "LargeOffice": 7,
    "SmallOffice": 8,
    "MediumOffice": 7,
    "SmallHotel": 6,
    "QuickServiceRestaurant": 4,
    "RetailStandalone": 9,
    "FullServiceRestaurant": 4,
    "LargeHotel": 6,
    "Warehouse": 10,
    "SecondarySchool": 12,
    "PrimarySchool": 2,
    'Grocery': 3,
    }

EUSES = ["HEAT", "COOL"]


def map_to_comstock(df):
    """Convert ComStock output dataframe to format suitable for thermal loads processing"""

    # Map building types and census divisions to codes
    df["BLDG"] = df["in.comstock_building_type"].map(BLDG_MAPPING)
    df["CDIV"] = df["in.state"].map(CDIV_MAPPING)

    print("Length before dropping NAs:", len(df))
    print("Number of None:", df["weight"].isna().sum())
    return df


def convert_to_thermalLoads(data: pd.DataFrame) -> pd.DataFrame:
    """Convert ComStock data to Scout thermal loads format

    This function aggregates ComStock thermal load segments into
    Scout thermal load categories, computes weighted averages based
    on the number of buildings represented, and normalizes the results
    to fractions of total thermal load.

    Parameters:
        data (pd.DataFrame): Input DataFrame containing ComStock simulation outputs with
                             the added following required columns:
            - 'CDIV': Census Division code (1-9)
            - 'BLDG': Building type code (1-12)

    Returns:
        pd.DataFrame: DataFrame formatted for Scout thermal loads with columns:
            - 'ENDUSE': 'HT' for heating, 'CL' for cooling
            - 'CDIV': Census Division code
            - 'BLDG': Building type code
            - 'weighted_sqft': weighted floor area
            - Component fractions: WIND_COND, WIND_SOL, ROOF, WALL, INFIL,
            PEOPLE, GRND, EQUIP_ELEC, EQUIP_NELEC, FLOOR, LIGHTS, VENT

    Process:
        1. Iterate over all combinations of CDIV, BLDG, and EUSE.
        2. For each combination, filter the data and compute weighted sums
           for each thermal load category based on the weight.
        3. Normalize the component loads to fractions of total thermal load.
        4. Compile results into a final DataFrame.
    """
    # Local accumulator for results to avoid relying on a global and fix F823
    final_data = pd.DataFrame()

    categories = sorted(set(COMSTOCK_SEGMENT_TO_CATEGORY.values()))

    for cdiv in range(1, CDIV_MAX + 1):
        for bldg in range(1, BLDG_MAX + 1):
            for euse in EUSES:
                if bldg == 2:
                    subset = data[(data["CDIV"] == cdiv) & (data["BLDG"].isin([bldg, 12]))]
                else:
                    subset = data[(data["CDIV"] == cdiv) & (data["BLDG"] == bldg)]

                # Determine internal end-use selector and output label
                euse_lower = "htg" if euse == "HEAT" else "clg"
                output_enduse = "HT" if euse == "HEAT" else "CL"
                keep_cols = [
                    c
                    for c in subset.columns
                    if (
                        "out.loads." + euse_lower in str(c).lower()
                        or c in ["CDIV", "BLDG", "weight", "calc.weighted.sqft..ft2"]
                    )
                ]
                subset = subset[keep_cols]

                # Compute weights and prepare a category accumulator
                sum_bldgs = subset["weight"].sum()

                # Compute sum of weighted sqft
                sum_weighted_sqft = subset["calc.weighted.sqft..ft2"].sum()
                # Per-row weight; if sum is zero, set weight to 0 (vector of zeros via broadcasting)
                row_weight = subset["weight"] / sum_bldgs if sum_bldgs > 0 else 0.0

                # Accumulate weighted totals per category in this dict
                cat_weighted = {cat: 0.0 for cat in categories}

                for segment, category in COMSTOCK_SEGMENT_TO_CATEGORY.items():
                    seg_cols = [
                        col
                        for col in subset.columns
                        if ("out.loads." + euse_lower in str(col).lower())
                        and (segment in str(col).lower())
                    ]

                    # Row-wise sum across all matched segment columns
                    seg_row_sum = subset[seg_cols].sum(axis=1)
                    seg_weighted_value = float((seg_row_sum * row_weight).sum())
                    cat_weighted[category] += seg_weighted_value

                final_data = pd.concat(
                    [
                        final_data,
                        pd.DataFrame(
                            {
                                "CDIV": cdiv,
                                "BLDG": bldg,
                                "ENDUSE": output_enduse,
                                "weighted_sqft": sum_weighted_sqft,
                            },
                            index=[0],
                        ),
                    ],
                    ignore_index=True,
                )

                # weighted thermal components (compute scalar weighted averages per row)
                row_mask = (
                    (final_data["CDIV"] == cdiv)
                    & (final_data["BLDG"] == bldg)
                    & (final_data["ENDUSE"] == output_enduse)
                )

                for cat, val in cat_weighted.items():
                    final_data.loc[row_mask, cat] = val

                # Normalize to shares (fractions of total)
                share_components = [c for c in categories if c != "TOTAL"]

                # Sum across share components for just this row (Series of length 1)
                row_total = final_data.loc[row_mask, share_components].sum(axis=1)

                # Normalize only if positive (avoid divide-by-zero)
                if not row_total.empty and float(row_total.iloc[0]) != 0:
                    final_data.loc[row_mask, share_components] = final_data.loc[
                        row_mask, share_components
                    ].div(row_total.values, axis=0)

    # Save to CSV with tab separator and txt extension
    # Reorder columns to match original file
    desired_order = [
        "ENDUSE",
        "CDIV",
        "BLDG",
        "weighted_sqft",
        "WIND_COND",
        "WIND_SOL",
        "ROOF",
        "WALL",
        "INFIL",
        "PEOPLE",
        "GRND",
        "EQUIP",
        "REFRIG",
        "FLOOR",
        "LIGHTS",
        "VENT",
    ]

    # Ensure all desired columns exist (create if missing)
    for col in desired_order:
        if col not in final_data.columns:
            final_data[col] = 0.0

    # Select and reorder
    final_data = final_data[desired_order].copy()

    # Round numeric columns to 4 decimal places
    numeric_cols = final_data.select_dtypes(include=["number"]).columns
    final_data[numeric_cols] = final_data[numeric_cols].round(4)

    return final_data


def add_missing_building_type(df: pd.DataFrame) -> pd.DataFrame:
    '''
    The "assembly", "other", and "unspecified" building type in the Scout
    are not exit in ComStock
    This fuction Establish rows for "assembly" building type as an
    weighted average of the rows for "SecondarySchool", "small office",
    and "mercantile/service". Establish rows for "other" and "unspecified"
    building type as an weighted average of the rows for all building types

    Parameters:
        pd.DataFrame: DataFrame formatted for Scout thermal loads with columns:
            - 'ENDUSE': 'HT' for heating, 'CL' for cooling
            - 'CDIV': Census Division code (1-9)
            - 'BLDG': Building type code(1-12)
            - 'weighted_sqft': weighted floor area
            - Component fractions: WIND_COND, WIND_SOL, ROOF, WALL, INFIL,
            PEOPLE, GRND, EQUIP_ELEC, EQUIP_NELEC, FLOOR, LIGHTS, VENT

    Returns:
        pd.DataFrame: DataFrame formatted for Scout thermal loads with columns:
            - 'ENDUSE': 'HT' for heating, 'CL' for cooling
            - 'CDIV': Census Division code (1-9)
            - 'BLDG': Building type code (1-11)
            - Component fractions: WIND_COND, WIND_SOL, ROOF, WALL, INFIL,
            PEOPLE, GRND, EQUIP_ELEC, EQUIP_NELEC, FLOOR, LIGHTS, VENT
    '''

    avg_cols = list(set(COMSTOCK_SEGMENT_TO_CATEGORY.values()))
    result_list = []

    # Iterate over CDIV × ENDUSE combinations
    for cdiv in df['CDIV'].unique():
        for enduse in df['ENDUSE'].unique():
            subset = df[(df['CDIV'] == cdiv) & (df['ENDUSE'] == enduse)]

            # Establish rows for "Assembly" building type as an weighted average of the rows
            # for "SecondarySchool", "Small. Office", and "Merch./Service"
            assembly_sub = subset[subset['BLDG'].isin([8, 9, 12])]
            assembly_avg = (
                assembly_sub[avg_cols].mul(assembly_sub['weighted_sqft'], axis=0).sum()
                / assembly_sub['weighted_sqft'].sum()
                )
            assembly_avg = assembly_avg.round(4)

            # Establish rows for "Other" and "unspecified" building type as
            # an weighted average of the rows for all building types in ComStock
            other_sub = subset[subset['BLDG'].isin([2, 3, 4, 5, 6, 7, 8, 9, 10, 12])]
            other_avg = (
                other_sub[avg_cols].mul(other_sub['weighted_sqft'], axis=0).sum()
                / other_sub['weighted_sqft'].sum()
                )
            other_avg = other_avg.round(4)

            for bldg in subset['BLDG'].unique():
                block = subset[subset['BLDG'] == bldg].copy()

                if bldg == 1:
                    for col in avg_cols:
                        block[col] = assembly_avg[col]
                elif bldg == 11:
                    for col in avg_cols:
                        block[col] = other_avg[col]

                result_list.append(block)

    final_df = pd.concat(result_list, ignore_index=True)
    final_df = final_df.drop(columns=['weighted_sqft'])
    final_df = final_df[final_df['BLDG'] != 12]

    return final_df


def main():
    df = pd.read_csv(
        "scout/supporting_data/thermal_loads_data/upgrade0_agg.csv",
        low_memory=False,
    )
    df = map_to_comstock(df)
    final_data = convert_to_thermalLoads(df)
    final_data = add_missing_building_type(final_data)
    final_data.to_csv(
        "scout/supporting_data/thermal_loads_data/Com_TLoads_Final.txt",
        sep="\t",
        index=False,
    )
    print("Conversion complete! Output saved to Com_TLoads_Final.txt")


if __name__ == "__main__":

    main()
