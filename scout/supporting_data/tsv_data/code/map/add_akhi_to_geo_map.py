"""
One-time patch that adds Alaska and Hawaii rows to geo_map.csv.

Background: geo_map.csv is the county -> EMM region crosswalk used by
../sql/comstock_data_emm.sql and ../sql/resstock_data_emm.sql (joined via
each county's "stock.county" key). It never covered AK/HI, because EIA's
NEMS EMM regions are only defined for the Lower 48 + DC (AK/HI have
isolated grids outside that system) -- so ComStock/ResStock rows for those
two states were filtered out entirely rather than left to join to nothing.

Data sources:
- scout_geography.csv: added alongside this script. Provides, per AK/Hi
  county, a population and an "emm2020_ba" column -- the best-fit EMM
  region for that county (not a single placeholder region for all of
  AK/HI).
- FIPS_TO_NAME below: Alaska/Hawaii county FIPS codes and names, fetched
  from the Census Bureau's authoritative reference
  (https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt)
  and used to decode the NHGIS GISJOIN codes ComStock uses
  ("G" + 2-digit state FIPS + "0" + 3-digit county FIPS + "0").
- COMSTOCK_GISJOIN / RESSTOCK_COUNTY below: the exact county identifiers
  ComStock and ResStock actually use for AK/HI, confirmed against the live
  Athena tables (`comstock_amy2018_release_2025.3_parquet` /
  `resstock_amy2018_release_2025.1_parquet`, distinct `in.nhgis_county_
  gisjoin` / `in.county` values for state IN ('AK','HI')). ComStock 2024.2
  uses the identical GISJOIN set. ResStock 2024.2 has no AK/HI data at
  all, so it needs no entry here.

Two dataset-specific quirks this script works around:
1. ComStock keys counties by NHGIS GISJOIN code (e.g. "G0200130") in both
   releases. ResStock 2025.1 instead keys AK/HI counties by a
   human-readable "ST, County Name" string (e.g. "AK, Yukon-Koyukuk Census
   Area") -- a different format than the GISJOIN codes it uses for every
   other state. So geo_map.csv needs two rows per AK/HI county: one keyed
   by the GISJOIN code (for ComStock) and one keyed by the county name
   (for ResStock).
2. The "geo_map" Athena table is created with Hive's naive
   `FIELDS TERMINATED BY ','` SerDe (see sql_create_table() in
   ../update_tsv.py), which has no CSV quote-escaping. ResStock's
   "ST, County Name" string contains a literal comma, which would corrupt
   that row's column alignment if stored as-is. So the ResStock-style key
   here is comma-free ("AK Yukon-Koyukuk Census Area"), and
   resstock_data_emm.sql's join strips commas from `in.county` at query
   time (`REPLACE(mc."in.county", ',', '')`) to match -- a no-op for the
   comma-free GISJOIN keys every other state (and ComStock AK/HI) uses.

ComStock's 27 AK / 4 HI GISJOIN codes cover most, but not all, of AK's 30
current census areas: Chugach and Copper River (split from Valdez-Cordova
in 2019) and Kusilvak have no ComStock GISJOIN in the data, so they're
skipped for the ComStock-style rows. ResStock 2025.1 uses pre-2019 AK
boundaries (Valdez-Cordova undivided, Kusilvak present), so its 29 AK
counties are handled separately below. HI is a clean 4-county match in
both datasets (Kalawao County has no building samples in either).

Usage: run from this directory (map/) with `python add_akhi_to_geo_map.py`.
Idempotent -- refuses to run if geo_map.csv already has AK/HI rows.
"""
import csv
import os

GEO_MAP_FILE = "geo_map.csv"
SCOUT_GEOGRAPHY_FILE = "scout_geography.csv"

# Alaska/Hawaii county FIPS -> name, from the Census Bureau's
# national_county2020.txt reference (see module docstring).
FIPS_TO_NAME = {
    ("AK", "013"): "Aleutians East Borough",
    ("AK", "016"): "Aleutians West Census Area",
    ("AK", "020"): "Anchorage Municipality",
    ("AK", "050"): "Bethel Census Area",
    ("AK", "060"): "Bristol Bay Borough",
    ("AK", "063"): "Chugach Census Area",
    ("AK", "066"): "Copper River Census Area",
    ("AK", "068"): "Denali Borough",
    ("AK", "070"): "Dillingham Census Area",
    ("AK", "090"): "Fairbanks North Star Borough",
    ("AK", "100"): "Haines Borough",
    ("AK", "105"): "Hoonah-Angoon Census Area",
    ("AK", "110"): "Juneau City and Borough",
    ("AK", "122"): "Kenai Peninsula Borough",
    ("AK", "130"): "Ketchikan Gateway Borough",
    ("AK", "150"): "Kodiak Island Borough",
    ("AK", "158"): "Kusilvak Census Area",
    ("AK", "164"): "Lake and Peninsula Borough",
    ("AK", "170"): "Matanuska-Susitna Borough",
    ("AK", "180"): "Nome Census Area",
    ("AK", "185"): "North Slope Borough",
    ("AK", "188"): "Northwest Arctic Borough",
    ("AK", "195"): "Petersburg Borough",
    ("AK", "198"): "Prince of Wales-Hyder Census Area",
    ("AK", "220"): "Sitka City and Borough",
    ("AK", "230"): "Skagway Municipality",
    ("AK", "240"): "Southeast Fairbanks Census Area",
    ("AK", "275"): "Wrangell City and Borough",
    ("AK", "282"): "Yakutat City and Borough",
    ("AK", "290"): "Yukon-Koyukuk Census Area",
    ("HI", "001"): "Hawaii County",
    ("HI", "003"): "Honolulu County",
    ("HI", "005"): "Kalawao County",
    ("HI", "007"): "Kauai County",
    ("HI", "009"): "Maui County",
}

# NHGIS GISJOIN codes ComStock uses for AK/HI (identical in 2024.2 and
# 2025.3), confirmed via:
#   SELECT DISTINCT state, "in.nhgis_county_gisjoin"
#   FROM "comstock_amy2018_release_2025.3_parquet"
#   WHERE state IN ('AK','HI')
COMSTOCK_GISJOIN = {
    "AK": ["G0200130", "G0200160", "G0200200", "G0200500", "G0200600",
           "G0200680", "G0200700", "G0200900", "G0201000", "G0201050",
           "G0201100", "G0201220", "G0201300", "G0201500", "G0201640",
           "G0201700", "G0201800", "G0201850", "G0201880", "G0201950",
           "G0201980", "G0202200", "G0202300", "G0202400", "G0202750",
           "G0202820", "G0202900"],
    "HI": ["G1500010", "G1500030", "G1500070", "G1500090"],
}

# Distinct "in.county" county names ResStock 2025.1 uses for AK/HI
# (pre-2019 boundaries), confirmed via:
#   SELECT DISTINCT state, "in.county"
#   FROM "resstock_amy2018_release_2025.1_parquet"
#   WHERE state IN ('AK','HI')
RESSTOCK_COUNTY = {
    "AK": ["Aleutians East Borough", "Aleutians West Census Area",
           "Anchorage Municipality", "Bethel Census Area",
           "Bristol Bay Borough", "Denali Borough", "Dillingham Census Area",
           "Fairbanks North Star Borough", "Haines Borough",
           "Hoonah-Angoon Census Area", "Juneau City and Borough",
           "Kenai Peninsula Borough", "Ketchikan Gateway Borough",
           "Kodiak Island Borough", "Kusilvak Census Area",
           "Lake and Peninsula Borough", "Matanuska-Susitna Borough",
           "Nome Census Area", "North Slope Borough",
           "Northwest Arctic Borough", "Petersburg Borough",
           "Prince of Wales-Hyder Census Area", "Sitka City and Borough",
           "Skagway Municipality", "Southeast Fairbanks Census Area",
           "Valdez-Cordova Census Area", "Wrangell City and Borough",
           "Yakutat City and Borough", "Yukon-Koyukuk Census Area"],
    "HI": ["Hawaii County", "Honolulu County", "Kauai County",
           "Maui County"],
}

REGION_NAME = {"AK": "alaska", "HI": "hawaii"}


def display_name(state, full_name):
    """ geo_map.csv drops the generic " County" suffix elsewhere (e.g.
    "Autauga" not "Autauga County"); AK's Borough/Census Area/Municipality
    suffixes are kept since they're part of the official name, not a
    generic descriptor. """
    return full_name[:-len(" County")] if state == "HI" else full_name


def load_geography(path):
    """ (state, county_name) -> (population, emm2020_ba) for AK/HI rows. """
    geo = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if row["state"] in ("AK", "HI"):
                geo[(row["state"], row["county_name"])] = (
                    row["population"], row["emm2020_ba"])
    return geo


def build_rows(geo):
    rows = []
    # ComStock-style rows, keyed by GISJOIN code.
    for state, codes in COMSTOCK_GISJOIN.items():
        for code in codes:
            county_fips = code[4:7]
            name = FIPS_TO_NAME[(state, county_fips)]
            pop, emm = geo[(state, name)]
            rows.append([state, display_name(state, name), code, emm, pop,
                         display_name(state, name).lower(),
                         REGION_NAME[state]])
    # ResStock-style rows, keyed by comma-free "ST CountyName" (see quirk
    # #2 in the module docstring).
    for state, names in RESSTOCK_COUNTY.items():
        for name in names:
            pop, emm = geo[(state, name)]
            stock_key = f"{state} {name}"
            rows.append([state, display_name(state, name), stock_key, emm,
                         pop, display_name(state, name).lower(),
                         REGION_NAME[state]])
    return rows


def main():
    with open(GEO_MAP_FILE, newline="") as f:
        existing_states = {row["state_abbr"]
                            for row in csv.DictReader(f)}
    if "AK" in existing_states or "HI" in existing_states:
        raise SystemExit(
            f"{GEO_MAP_FILE} already has AK/HI rows -- nothing to do. "
            "Remove them first if you need to regenerate.")

    geo = load_geography(SCOUT_GEOGRAPHY_FILE)
    rows = build_rows(geo)

    for row in rows:
        for field in row:
            assert "," not in field, (
                f"comma in field would corrupt the Athena geo_map table "
                f"(no CSV quote-escaping): {row}")

    with open(GEO_MAP_FILE, "rb") as f:
        ends_crlf = f.read().endswith(b"\r\n")
    if not ends_crlf:
        raise SystemExit(
            f"{GEO_MAP_FILE} doesn't end with \\r\\n as expected -- "
            "check the file hasn't been re-saved with different line "
            "endings before appending.")

    with open(GEO_MAP_FILE, "ab") as f:
        for row in rows:
            f.write((",".join(row) + "\r\n").encode("utf-8"))

    print(f"Appended {len(rows)} AK/HI rows to {GEO_MAP_FILE} "
          f"({sum(1 for r in rows if r[0] == 'AK')} AK, "
          f"{sum(1 for r in rows if r[0] == 'HI')} HI).")


if __name__ == "__main__":
    if not os.path.isfile(GEO_MAP_FILE) or not os.path.isfile(
            SCOUT_GEOGRAPHY_FILE):
        raise SystemExit(
            "Run this script from the map/ directory (needs "
            f"{GEO_MAP_FILE} and {SCOUT_GEOGRAPHY_FILE} in cwd).")
    main()
