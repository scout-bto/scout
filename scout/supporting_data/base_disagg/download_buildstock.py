"""
Download ComStock/ResStock 2024 baseline parquet from NREL OEDI.
pip install boto3 pyarrow
Public bucket -> UNSIGNED, no AWS credentials required.
"""
import io
import os
import boto3
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
from botocore import UNSIGNED
from botocore.config import Config

BUCKET = "oedi-data-lake"
BASE = "nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock"
WEATHER = "amy2018"
INDIR = "input"
OUT_FILENAME = "baseline.parquet"

# Hard-code the release tags you confirmed exist:
RELEASES = {
    "resstock": f"{BASE}/2024/resstock_amy2018_release_2/",
    "comstock": f"{BASE}/2024/comstock_amy2018_release_2/",
}

# Columns generate_geo_maps.py needs from ComStock (keeps memory low)
COM_END_USE_COLS = sorted({
    c
    for fuel in {
        "out.electricity.heating.energy_consumption",
        "out.electricity.heat_recovery.energy_consumption",
        "out.electricity.heat_rejection.energy_consumption",
        "out.electricity.cooling.energy_consumption",
        "out.district_cooling.cooling.energy_consumption",
        "out.electricity.water_systems.energy_consumption",
        "out.electricity.fans.energy_consumption",
        "out.electricity.pumps.energy_consumption",
        "out.electricity.interior_lighting.energy_consumption",
        "out.electricity.exterior_lighting.energy_consumption",
        "out.electricity.refrigeration.energy_consumption",
        "out.electricity.interior_equipment.energy_consumption",
        "out.natural_gas.heating.energy_consumption",
        "out.district_heating.heating.energy_consumption",
        "out.natural_gas.water_systems.energy_consumption",
        "out.district_heating.water_systems.energy_consumption",
        "out.natural_gas.interior_equipment.energy_consumption",
        "out.other_fuel.heating.energy_consumption",
        "out.other_fuel.cooling.energy_consumption",
        "out.other_fuel.water_systems.energy_consumption",
    }
    for c in (fuel,)
})
COM_NEEDED = ["in.nhgis_county_gisjoin", "in.state",
              "calc.weighted.sqft"] + COM_END_USE_COLS

s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED))


def download_resstock(out_path):
    key = (RELEASES["resstock"]
           + "metadata_and_annual_results/national/parquet/"
             "baseline_metadata_and_annual_results.parquet")
    size = s3.head_object(Bucket=BUCKET, Key=key)["ContentLength"]
    print(f"ResStock national file: {size/1e6:.0f} MB -> {out_path}")
    s3.download_file(BUCKET, key, out_path)

def download_comstock(out_path):
    base = (RELEASES["comstock"]
            + "metadata_and_annual_results/by_state_and_county/full/parquet/")
    paginator = s3.get_paginator("list_objects_v2")
    keys = []
    for page in paginator.paginate(Bucket=BUCKET, Prefix=base):
        for obj in page.get("Contents", []):
            if obj["Key"].endswith("_baseline.parquet"):
                keys.append(obj["Key"])
    if not keys:
        raise RuntimeError(f"No county baseline files under {base}")
    keys = sorted(keys)
    print(f"ComStock: assembling {len(keys)} county files -> {out_path}")

    # ---- pass 1: build the union schema across all files ----
    print("Pass 1: scanning schemas...")
    fields = {}          # column name -> pyarrow type
    order = []           # preserve first-seen column order
    for i, key in enumerate(keys, 1):
        buf = io.BytesIO()
        s3.download_fileobj(BUCKET, key, buf)
        buf.seek(0)
        sch = pq.read_schema(buf)
        for name, typ in zip(sch.names, sch.types):
            if name not in fields:
                fields[name] = typ
                order.append(name)
            else:
                # widen to a common type if they disagree
                fields[name] = _promote(fields[name], typ)
        if i % 200 == 0:
            print(f"  scanned {i}/{len(keys)}")

    master_schema = pa.schema([(n, fields[n]) for n in order])

    # ---- pass 2: read, cast to master schema, write ----
    print("Pass 2: assembling...")
    writer = pq.ParquetWriter(out_path, master_schema)
    try:
        for i, key in enumerate(keys, 1):
            buf = io.BytesIO()
            s3.download_fileobj(BUCKET, key, buf)
            buf.seek(0)
            table = pq.read_table(buf)
            # add any missing columns as nulls, drop nothing, reorder, cast
            table = _conform(table, master_schema)
            writer.write_table(table)
            if i % 200 == 0:
                print(f"  {i}/{len(keys)}")
    finally:
        writer.close()
    print("ComStock assembly done.")


def _promote(t1, t2):
    """Pick a common pyarrow type when two files disagree."""
    if t1 == t2:
        return t1
    # null from an all-empty column loses to any real type
    if pa.types.is_null(t1):
        return t2
    if pa.types.is_null(t2):
        return t1
    # int vs float -> float
    if (pa.types.is_integer(t1) and pa.types.is_floating(t2)) or \
       (pa.types.is_floating(t1) and pa.types.is_integer(t2)):
        return pa.float64()
    # fall back to string for anything genuinely incompatible
    return pa.string()


def _conform(table, schema):
    """Reorder/add-missing/cast a table to match the master schema."""
    arrays = []
    n = table.num_rows
    existing = {name: table.column(name) for name in table.schema.names}
    for field in schema:
        if field.name in existing:
            col = existing[field.name]
            if col.type != field.type:
                col = col.cast(field.type)
            arrays.append(col)
        else:
            arrays.append(pa.nulls(n, type=field.type))
    return pa.Table.from_arrays(arrays, schema=schema)
def main():
    for ds, subdir in [("comstock", "2024_comstock")]:
    # for ds, subdir in [("resstock", "2024_resstock"),
    #                    ("comstock", "2024_comstock")]:
        out_dir = os.path.join(INDIR, subdir, WEATHER)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, OUT_FILENAME)
        print(f"\n=== {ds} ===")
        if ds == "resstock":
            download_resstock(out_path)
        else:
            download_comstock(out_path)


if __name__ == "__main__":
    main()