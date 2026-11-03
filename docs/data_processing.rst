.. _data-processing:

Data Processing
===============

This section describes how three of Scout's data inputs are derived from NREL ComStock and ResStock data: the factors that disaggregate baseline data from census divisions to EMM regions and states, the hourly load shapes, and the peak days. Each section summarizes the method and points to a README with the full steps for regenerating the data.

.. _data-disagg:

Disaggregation from census divisions to EMM regions and states
--------------------------------------------------------------

Purpose
~~~~~~~

The EIA Annual Energy Outlook (AEO) data behind Scout's baseline are resolved by census division, while Scout analyses run on :ref:`EMM regions or states <ecm-baseline_climate-zone>`. Scout therefore splits each census division's stock and energy data across the regions it overlaps, using factors derived from ComStock and ResStock building-level data.

Method
~~~~~~

For each census division, a factor is the share of that division's total that falls in a given EMM region or state. Factors are calculated from the ComStock and ResStock data and normalized so that the factors for each census division sum to 1. They are calculated separately for:

* the residential and commercial sectors,
* EMM regions and states,
* electricity, natural gas, distillate, and other fuels,
* energy use and stock, and
* end uses and, for electric heating and cooling, technologies.

Energy factors use modeled energy consumption. Stock factors use weighted floor area for commercial buildings and dwelling unit weights for residential buildings.

Factor files
~~~~~~~~~~~~

Factors are stored in |html-filepath| ./scout/supporting_data/convert_data/geo_map |html-fp-end|, in files named as follows: ::

   <Res|Com>_Cdiv_<EMM|State>_amy2018_<fuel>[_Stock][_Tech].csv

Files with ``_Stock`` in the name hold stock factors, and all others hold energy factors. Files with ``_Tech`` in the name hold the technology-level electricity factors. The ComStock and ResStock releases used are recorded in |html-filepath| ./scout/supporting_data/convert_data/geo_map/sdr_version.json\ |html-fp-end|.

The factors are applied by ``final_mseg_converter.py``, which prompts for the level of disaggregation to use. Scout's default baseline files use factors for all fuels and technology-level factors for electricity. These choices and the data release are written to the ``_cdiv_disagg_info`` key at the top of each output file.

Regenerating the factors
~~~~~~~~~~~~~~~~~~~~~~~~

Rerun this process when a new ComStock or ResStock release should be used, or when the mapping or disaggregation logic changes. The process has four steps, and each must be run from a specific directory:

#. Download the data using ``download_buildstock.py``, run from |html-filepath| ./scout/supporting_data/base_disagg\ |html-fp-end|.
#. Generate the factors using ``generate_geo_maps.py``, run from the same directory. With no flags, this regenerates the factors and copies them to the directory that Scout reads them from. Use ``--no-install`` to write them to the local ``output/`` directory without copying them, ``--install-only`` to copy files already in ``output/`` without regenerating them, or ``--help`` to see all options.
#. Regenerate the baseline files using ``final_mseg_converter.py``, run from the repository root. This script is interactive and must be run twice: once for EMM regions and once for states.
#. Regenerate the heating and cooling totals using ``htcl_totals.py``, run from the repository root.

See the :repo_file:`disaggregation README <scout/supporting_data/base_disagg/README.md>` for the commands, prompt selections, and files to commit.

.. _data-load-shapes:

Hourly load shape data
----------------------

Purpose
~~~~~~~

Hourly load shapes describe how annual baseline electricity use is distributed across the 8760 hours of the year. Scout uses them to support :ref:`time sensitive ECM features <ecm-features-tsv>`, :ref:`time sensitive valuation metrics <tsv-metrics-opt>`, and :ref:`sector-level hourly energy loads <sect-shapes-opt>`.

Source and processing
~~~~~~~~~~~~~~~~~~~~~

The load shapes are derived from ComStock and ResStock timeseries data, using AMY 2018 weather. By default, the data come from ComStock release 2025.3 and ResStock release 2025.1.

The source data are reported at 15-minute intervals, but Scout's load shapes are hourly. The data are processed as follows:

#. Each 15-minute value is assigned to the hour in which its interval falls, and each hour is labeled by its start time.
#. ComStock and ResStock report all timeseries in Eastern Standard Time, so each region's shape is shifted to that region's local standard time. Where a region spans multiple time zones, the time zone that covers most of its population is used.
#. Each shape is normalized so that its 8760 values sum to approximately 1.

Load shape files
~~~~~~~~~~~~~~~~

Scout reads |html-filepath| ./scout/supporting_data/tsv_data/tsv_load_EMM.gz |html-fp-end| when regions are set to EMM and |html-filepath| ./scout/supporting_data/tsv_data/tsv_load_State.gz |html-fp-end| when regions are set to State. Both files use the same structure: ::

   {"residential" or "commercial": {
      <end use>: {
        <building type>: {
          "represented building types": ...,
          "load shape": {
            <region>: [<8760 hourly values>]}}}}}

The top level of each file also records the assumptions behind the data, including the weather basis, the time zone treatment, and the starting day of the week.

The EMM file covers all 25 EMM regions. The state file covers the 48 contiguous states and the District of Columbia, and has no data for Alaska or Hawaii.

Regenerating the load shapes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The load shapes are regenerated using ``update_tsv.py``, which requires access to the project's AWS Athena database. Run these commands from |html-filepath| ./scout/supporting_data/tsv_data/code\ |html-fp-end|, and run the commercial step before the residential step: ::

   python update_tsv.py --get_stockdata
   python update_tsv.py --insert_scouttsv --bstock commercial
   python update_tsv.py --insert_scouttsv --bstock residential

Use ``--stock_version`` to select a different ComStock and ResStock release, and ``--diag`` to run diagnostic checks on the results. See the :repo_file:`load shape README <scout/supporting_data/tsv_data/code/README.md>` for details.
