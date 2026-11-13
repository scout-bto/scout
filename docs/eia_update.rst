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
   Replace ``YOUR_REAL_KEY_HERE`` with the value from your EIA account, and keep
   the file at the repository root so Scout can load it automatically.

2. **Install Scout and its dependencies** into a virtual environment
   (see :ref:`install-guide`).

3. **From the project root, run the helper script**, for example:

   **Windows** ::

      python -m scout.AEO_update_helpers.baseline_comparison --year 2025

   **Mac** ::

      python3 -m scout.AEO_update_helpers.baseline_comparison --year 2025

   Use ``--verbose`` to see the underlying API calls and any combinations where
   data are missing.

The output includes per-combination comparisons and simple roll-up tables by
building class and fuel type. These reports make it easier to confirm that
Scout's baseline matches the chosen AEO reference.

AEO Update Checklist
--------------------

Use this quick checklist when updating Scout to a new AEO release.

1. **Stage raw AEO files in** ``inputs/raw``

   Required files, covering both the Reference Case and High Electricity Demand (high data center load growth, or `_hdc`) cases:

   * ``RDM_DBOUT.txt``
   * ``RDM_DGENOUT.txt``
   * ``rsmess.xlsx``
   * ``rsmlgt.txt``
   * ``CDM_DBOUT.txt``
   * ``CDM_DBOUT_hdc.txt``
   * ``CDM_SDOUT.txt``
   * ``CDM_SDOUT_hdc.txt``
   * ``CDM_DGENOUT.txt``
   * ``CDM_DGENOUT_hdc.txt``
   * ``kprem.txt``
   * ``ktekx.xlsx``

   .. note::

      The ``_hdc.txt`` files included in the list above are available alongside the Reference Case EIA input files in the Scout MS Teams Project.

2. **Process raw AEO files**:

   **Windows** ::

      python -m scout.eia_file

   **Mac** ::

      python3 -m scout.eia_file

   This step reads from ``inputs/raw`` and writes processed tabular files to
   ``inputs/processed``.

3. **Generate Metadata**:

   **Windows** ::

      python -m scout.mseg_meta -y 2026

   **Mac** ::

      python3 -m scout.mseg_meta -y 2026

   Outputs ``inputs/metadata.json``. Confirm it has ``min year``,
   ``max year``, and ``aeo_base_year`` set correctly.

4. **Rebuild microsegment and CPL data products**:

   Generate intermediate microsegment and CPL data:

   **Windows** ::

      python -m scout.mseg -y 2026
      python -m scout.mseg_techdata -y 2026
      python -m scout.com_mseg -y 2026
      python -m scout.com_mseg_tech -y 2026

   **Mac** ::

      python3 -m scout.mseg -y 2026
      python3 -m scout.mseg_techdata -y 2026
      python3 -m scout.com_mseg -y 2026
      python3 -m scout.com_mseg_tech -y 2026

   Intermediate JSON artifacts are written to ``inputs/derived``
   (for example ``mseg_res_cdiv.json``, ``mseg_res_com_cdiv.json``,
   ``cpl_res_cdiv.json``, and ``cpl_res_com_cdiv.json``).

   Run the final microsegment converter:

   **Windows** ::

      python -m scout.final_mseg_converter

   **Mac** ::

      python3 -m scout.final_mseg_converter

   First, update the microsegment products: 

   Select options ``1,1`` when prompted. This develops climate zone-specific data.

   After this first run, run again with the following options, which develop EMM-resolved and state-resolved data:

   * ``1,2,2,1``
   * ``1,3,2,1``

   Then, update the cost, performance, and lifetime (CPL) products for all three geographic region types:

   * ``2,1``
   * ``2,2``
   * ``2,3``

   .. note::

      Ignore this warning for now:

      ``UserWarning: Key 'solar_water_heater_north' not found in add_dict``

      There is an open issue for this warning.

   Expected output includes the following files:

   * ``mseg_res_com_cz.json``
   * ``mseg_res_com_cz_hdc.json``
   * ``mseg_res_com_emm.gz``
   * ``mseg_res_com_emm_hdc.gz``
   * ``mseg_res_com_state.gz``
   * ``mseg_res_com_state_hdc.gz``
   * ``cpl_res_com_cz.gz``
   * ``cpl_res_com_emm.gz``
   * ``cpl_res_com_cdiv.gz``

   Move these final output files to
   ``scout/supporting_data/stock_energy_tech_data``.

5. **Rebuild heating and cooling total data products**:

   Recalculate heating and cooling energy totals across climate zones, EMM
   regions, and states under various site-source accounting conventions:

   **Windows** ::

      python -m scout.htcl_totals

   **Mac** ::

      python3 -m scout.htcl_totals

   This routine reads the baseline microsegment files from
   ``scout/supporting_data/stock_energy_tech_data`` and writes heating and cooling
   energy total files directly to that folder:

   * ``htcl_totals.json``, ``htcl_totals_hdc.json``
   * ``htcl_totals_decarb.json``, ``htcl_totals_decarb_hdc.json``
   * ``htcl_totals-ce.json``, ``htcl_totals-ce_hdc.json``
   * ``htcl_totals-site.json``, ``htcl_totals-site_hdc.json``
   * ``htcl_totals_emm.json``, ``htcl_totals_emm_hdc.json``
   * ``htcl_totals_emm_decarb.json``, ``htcl_totals_emm_decarb_hdc.json``
   * ``htcl_totals-ce_emm.json``, ``htcl_totals-ce_emm_hdc.json``
   * ``htcl_totals-site_emm.json``, ``htcl_totals-site_emm_hdc.json``
   * ``htcl_totals_state.json``, ``htcl_totals_state_hdc.json``
   * ``htcl_totals-ce_state.json``, ``htcl_totals-ce_state_hdc.json``
   * ``htcl_totals-site_state.json``, ``htcl_totals-site_state_hdc.json``

   Once generated, commit and push these files alongside the microsegment and CPL
   data products to the repository.

6. **Update emissions/price conversion datasets**:

   Ensure ``EIA_API_KEY`` is set in the project-root ``.env`` file
   (as described earlier in this document).

   Run the updater validation tests:

   **Windows** ::

      python tests\updater_validation_test.py

   **Mac** ::

      python3 tests/updater_validation_test.py

   Update state baseline snapshots:

   **Windows** ::

      python -m scout.state_baseline_data_updater

   **Mac** ::

      python3 -m scout.state_baseline_data_updater

   Update EIA conversion files (run separately per file):

   **Windows** ::

      python -m scout.converter -f FILE_NAME

   **Mac** ::

      python3 -m scout.converter -f FILE_NAME

   Use this for files beginning with ``emm_region_`` or ``site_source_`` in
   ``scout/supporting_data/convert_data``.

   Download hourly Balancing Authority emissions data from
   https://scenarioviewer.nlr.gov/, then run Cambium updates:

   **Windows** ::

      python -m scout.cambium_updater

   **Mac** ::

      python3 -m scout.cambium_updater

   Follow the prompts to select the Cambium year/scenario and to update
   files beginning with ``emm_region_`` or ``state_``.
