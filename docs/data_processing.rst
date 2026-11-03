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

.. _data-peak-periods:

Peak period definitions
-----------------------

Scout uses two separate inputs to define peak periods: *peak days*, which are based on building electricity load, and *peak and low demand hours*, which are based on electric system load.

Peak days
~~~~~~~~~

Scout previously used one fixed peak day for all regions: January 1 (day 1) in winter and July 2 (day 183) in summer. It now uses the actual winter and summer peak days for each region.

A region's peak day is the day containing its highest hourly total of commercial and residential electricity load in that season. Peak days apply to :ref:`time sensitive valuation metrics <tsv-metrics-opt>` that report maximum power, where ``--tsv_type`` is "power" and ``--tsv_power_agg`` is "peak".

Peak days are stored in two files in |html-filepath| ./scout/supporting_data/tsv_data\ |html-fp-end|:

* When regions are set to EMM, Scout uses each EMM region's peak day from ``tsv_peak_days_EMM.csv``.
* When regions are set to State, Scout uses each state's own peak day from ``tsv_peak_days_State.csv``. That file has no rows for Alaska or Hawaii, so those states use the peak day of their representative EMM region. A missing peak day for any other region raises an error.

Season windows
^^^^^^^^^^^^^^

Peak days are found within the following windows. The winter window is narrower than the winter season used for time sensitive valuation metrics, which runs through March 31. With the wider window, the highest "winter" load in warm and western regions can fall at the end of March, as load rises toward the cooling season.

.. table:: Windows used to find peak days, compared with the seasons used for time sensitive valuation metrics.

   +--------+-------------------------------+-------------------------------+
   | Season | Peak day window               | Metrics season                |
   +========+===============================+===============================+
   | Winter | Dec 1--Feb 28 (days 335--365, | Dec 1--Mar 31 (days 335--365, |
   |        | 1--59)                        | 1--90)                        |
   +--------+-------------------------------+-------------------------------+
   | Summer | Jun 1--Sep 30 (days 152--273) | Jun 1--Sep 30 (days 152--273) |
   +--------+-------------------------------+-------------------------------+

Flagged regions
^^^^^^^^^^^^^^^

A peak near the edge of a window may reflect the window rather than a true seasonal peak. To check for this, the calculation extends each window by 30 days. If the extended window gives a different peak day with load more than 5% higher than the peak inside the official window, the region is flagged in the ``WinterPeakAtWindowBoundary`` or ``SummerPeakAtWindowBoundary`` column. The flag does not change the peak day that Scout uses.

Regenerating the peak days
^^^^^^^^^^^^^^^^^^^^^^^^^^

After downloading the source data with the first ``update_tsv.py`` command in the previous section, run the following: ::

   python compute_peak_days.py --stock_version 2025

Peak and low demand hours
~~~~~~~~~~~~~~~~~~~~~~~~~

Peak and low demand hours are daily hour ranges, set by season, EMM region, and year using system-level load profiles. They are separate from peak days, and they apply when ``--tsv_daily_hr_restrict`` is "peak" or "low". The ``tsv_hrs_tot_*.csv`` files are based on total system demand and the ``tsv_hrs_net_*.csv`` files are based on system demand net of renewable generation. The ``base`` files use the AEO Reference Case and the ``lowogs`` files use the AEO Low Oil and Gas Supply side case.

State-level analyses use the hour ranges of each state's representative EMM region. See :numref:`tsv-nl-tab` for an example of these periods by climate zone.
