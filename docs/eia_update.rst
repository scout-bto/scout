.. _eia-update:

EIA Updates
=================

Scout's residential and commercial baseline energy use is anchored to the
U.S. Energy Information Administration (EIA) Annual Energy Outlook (AEO).
When Scout is updated to a new AEO release, we use a small helper script to
compare Scout's internal microsegment totals against the official AEO tables.

The script lives in ``scout/AEO_update_helpers/baseline_comparison.py``.
At a high level it:

* loads Scout's processed AEO microsegments file (``mseg_res_com_cz.json``),
* aggregates energy use by building class, fuel type, and end use,
* queries the EIA AEO API for the matching time-series,
* compares Scout vs. EIA year-by-year, and
* prints summary tables showing any large differences.

Running the EIA update check
----------------------------

1. **Create a local `.env` file (not committed to git)** in the project root
   (the same folder as ``pyproject.toml``) with your EIA API key::

      EIA_API_KEY=YOUR_REAL_KEY_HERE

   You can request a free key from EIA at https://www.eia.gov/opendata/register.php.

2. **Install Scout and its dependencies** into a virtual environment
   (see :ref:`install-guide`).

3. **From the project root, run the helper script**, for example::

      python -m scout.AEO_update_helpers.baseline_comparison --year 2025

   Use ``--verbose`` to see the underlying API calls and any combinations where
   data are missing.

The output includes per-combination comparisons and simple roll-up tables by
building class and fuel type. These reports make it easier to confirm that
Scout's baseline matches the chosen AEO reference.

AEO Update Checklist
--------------------

Use this quick checklist when updating Scout to a new AEO release.

1. **Stage raw AEO files in** ``inputs/``

   Required files:

   * ``RDM_DBOUT.txt``
   * ``RDM_DGENOUT.txt``
   * ``rsmess.xlsx``
   * ``rsmlgt.txt``
   * ``CDM_DBOUT.txt``
   * ``CDM_SDOUT.txt``
   * ``CDM_DGENOUT.txt``
   * ``kprem.txt``
   * ``ktekx.xlsx``

2. **Process raw AEO files**::

   python scout/eia_file.py

3. **Generate Metadata**::

   python -m scout.mseg_meta -y 2026

   Outputs ``inputs/metadata.json``. Confirm it has ``min year``,
   ``max year``, and ``aeo_base_year`` set correctly.

4. **Rebuild microsegment and CPL data products**::

   python tests/com_mseg_test.py
   
   python -m scout.mseg -y 2026

   python -m scout.mseg_techdata -y 2026

   python -m scout.com_mseg -y 2026

   python -m scout.com_mseg_tech -y 2026

   python tests/final_mseg_converter_test.py

   python -m scout.final_mseg_converter
   python scout/final_mseg_converter.py Select options 1,1 when prompted
   Ignore: UserWarning: Key 'solar_water_heater_north' not found in
   add_dict – skipping warnings.warn(f"Key '{k}' not found in add_dict – skipping"),
   there is an issue about this. Outputs mseg_res_com_cz.json
   Also run with the following options
   1,2,2,1
   1,3,2,1
   2,3

   Move these final output files to the
   scout/scout/supporting_data/supporting_data/stock_energy_tech_data folder,
   commit and push to github:
   mseg_res_com_cz.json
   mseg_res_com_emm.gz
   mseg_res_com_state.gz
   cpl_res_com_cdiv.gz

5. **Update emissions/price conversion datasets**::

   python -m scout.state_baseline_data_updater
   python -m scout.converter
   python -m scout.cambium_updater
