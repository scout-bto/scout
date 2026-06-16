"""
Generate input/mapping/map_*.csv files from diagnostics/Stock-Scout mapping.xlsx.

The notebook 2024_Convert_All.ipynb reads these CSVs to map parquet column values
to scout technology names. The Excel file contains a "Map using multiple relevant
columns" section per sector/end-use that provides the multi-condition mappings.
"""

import os
import pandas as pd
import openpyxl

EXCEL_PATH = "input/Stock-Scout mapping.xlsx"
OUT_DIR = "input/mapping"


def extract_section(rows, header_marker_col0, n_cols, search_after="Map using multiple relevant columns"):
    """
    Scan rows for header_marker_col0 only within the section that starts after
    'search_after', treat that as the header, then collect data rows until a
    blank row or end.  Returns a DataFrame with only the first n_cols columns.
    """
    # Find the start of the multi-column section first
    section_start = 0
    if search_after:
        for i, row in enumerate(rows):
            if row and row[0] == search_after:
                section_start = i
                break

    header_idx = None
    for i, row in enumerate(rows[section_start:], start=section_start):
        if row and row[0] == header_marker_col0:
            header_idx = i
            break

    if header_idx is None:
        raise ValueError(f"Header '{header_marker_col0}' not found after row {section_start}")

    header = list(rows[header_idx][:n_cols])
    data = []
    for row in rows[header_idx + 1:]:
        # stop at blank row
        if not row or all(v is None for v in row):
            break
        data.append(list(row[:n_cols]))

    return pd.DataFrame(data, columns=header)


def load_sheet_rows(excel_path, sheet_name):
    wb = openpyxl.load_workbook(excel_path, read_only=True)
    ws = wb[sheet_name]
    return list(ws.iter_rows(values_only=True))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # ── ComStock ────────────────────────────────────────────────────────────
    com_rows = load_sheet_rows(EXCEL_PATH, "ComStock techs")

    # Cooling: header starts with 'in.hvac_cool_type'; 5 real columns (6th is duplicate)
    com_cool = extract_section(com_rows, "in.hvac_cool_type", n_cols=5)
    out_path = os.path.join(OUT_DIR, "map_com_electricity_cooling.csv")
    com_cool.to_csv(out_path, index=False)
    print(f"Wrote {out_path}  ({len(com_cool)} rows, cols: {list(com_cool.columns)})")

    # Heating: header starts with 'in.hvac_heat_type'; 5 real columns (6th is duplicate)
    com_heat = extract_section(com_rows, "in.hvac_heat_type", n_cols=5)
    out_path = os.path.join(OUT_DIR, "map_com_electricity_heating.csv")
    com_heat.to_csv(out_path, index=False)
    print(f"Wrote {out_path}  ({len(com_heat)} rows, cols: {list(com_heat.columns)})")

    # ── ResStock ─────────────────────────────────────────────────────────────
    res_rows = load_sheet_rows(EXCEL_PATH, "ResStock techs")

    # Cooling: header starts with 'in.hvac_cooling_type'; 2 columns
    res_cool = extract_section(res_rows, "in.hvac_cooling_type", n_cols=2)
    out_path = os.path.join(OUT_DIR, "map_res_electricity_cooling.csv")
    res_cool.to_csv(out_path, index=False)
    print(f"Wrote {out_path}  ({len(res_cool)} rows, cols: {list(res_cool.columns)})")

    # Heating: header starts with 'in.hvac_heating_type'; 3 columns
    res_heat = extract_section(res_rows, "in.hvac_heating_type", n_cols=3)
    out_path = os.path.join(OUT_DIR, "map_res_electricity_heating.csv")
    res_heat.to_csv(out_path, index=False)
    print(f"Wrote {out_path}  ({len(res_heat)} rows, cols: {list(res_heat.columns)})")


if __name__ == "__main__":
    main()
