.. _policy-inputs:

Policy Inputs
=============

This section describes the policy data that Scout uses to adjust its baseline.

.. _policy-incentives:

Incentives
----------

Scout's baseline includes the equipment incentives represented in the EIA Annual Energy Outlook (AEO). The file |html-filepath| ./scout/supporting_data/sub_fed/incentives.csv |html-fp-end| modifies those incentives to reflect federal, state, and utility programs, such as rebates and tax credits. Incentives reduce the installed cost of both baseline and measure technologies in the applicable segments. Installed costs cannot fall below zero.

Selecting incentives
~~~~~~~~~~~~~~~~~~~~

``--incentive_levels`` selects which rows of the file to use, based on the ``scenario`` column.

.. note::
   Scout reads the file only when ``--alt_regions`` is ``State``. For other regions, ``--incentive_levels`` has no effect and only the AEO incentives are used.

.. list-table:: Valid options for ``--incentive_levels``.
   :header-rows: 1
   :widths: 30 70

   * - Option
     - Incentives used
   * - aeo (default)
     - AEO incentives only, with no modifications.
   * - reference
     - Rows with the ``reference`` scenario: state, local, and utility programs, including IRA-funded home electrification rebates. These rows include no federal tax credits.
   * - aggressive-fuel-neutral
     - ``reference`` rows, plus ``aggressive-fuel-neutral`` rows layered on them.
   * - aggressive-electric
     - ``reference`` rows, plus ``aggressive-electric`` rows layered on them.
   * - aggressive
     - ``reference`` rows, plus ``aggressive`` rows layered on them.
   * - aggressive state
     - ``reference`` rows, plus any rows for this scenario. The file currently has no such rows, so this option gives the same result as ``reference``.

:ref:`policy-incentive-scenarios` describes what the non-reference scenarios add.

When scenario rows are layered on ``reference`` rows, a scenario row is dropped for any years in which a ``reference`` row from the same program already provides at least the same incentive, for the same applicable fraction and performance requirements. Rows from different programs, or for different fractions of one program, are kept.

``--incentive_restrictions`` removes selected incentives from the analysis, including those in the AEO baseline. Valid options are:

* "all" removes all incentives.
* "no ira" removes rows tagged as funded by the Inflation Reduction Act (IRA). These are the Home Electrification and Appliance Rebates (HEAR) rows and the federal tax credit rows in the non-reference scenarios.
* "no federal" and "no sub-federal" remove federal and non-federal incentives. Rows in the file are removed based on their ``scope``, and rows with a ``scope`` of ``all`` count as both.
* "no electric" and "no fossil" remove incentives for electric and non-electric technologies. Rows in the file are removed based on ``fuel type(s)``, the fuel of the technology receiving the incentive.
* "no federal electric", "no federal fossil", "no sub-federal electric", and "no sub-federal fossil" (or "no sub-fed fossil") combine these two restrictions.

Restrictions never remove rows with a ``modification`` of ``remove``, since these rows add no incentive.

.. note::
   The baseline cost data combine federal and non-federal AEO incentives into a single value, which Scout treats as federal. "no federal" removes it, and "no sub-federal" keeps it.

Which rows apply
~~~~~~~~~~~~~~~~

A row applies to a segment in a given year when all of the following are true:

* **Segment:** the state, building type, vintage, end use, and technology match.
* **Year:** the year falls between ``start year`` and ``end year``.
* **Fuel:** ``base fuel`` matches the fuel being replaced, and ``fuel type(s)`` matches the fuel of the technology receiving the incentive.
* **Backup:** for measures that switch fuels, ``base fuel backup`` is compatible with the measure, as shown below.
* **Performance:** the technology meets ``performance level``, in ``performance units`` that match the technology's units.

Unit mismatches are handled as follows:

* If ``performance units`` do not match the technology's units, the row gives no incentive. Scout reports this only as a warning when ``--verbose`` is set, so check the units of new rows carefully.
* If ``rebate units`` do not match the units of the segment's cost data, Scout stops with an error.

.. table:: Measures that can receive an incentive, by ``base fuel backup`` value.

   +-------------------------------------------+-------------------------+-----------+
   | ``base fuel backup`` value                | Full electrification    | Dual fuel |
   +===========================================+=========================+===========+
   | ``no`` or blank: backup not allowed       | Yes                     | No        |
   +-------------------------------------------+-------------------------+-----------+
   | ``yes``: backup allowed but not required  | Yes                     | Yes       |
   +-------------------------------------------+-------------------------+-----------+
   | ``required``: existing fuel-fired system  | No                      | Yes       |
   | must stay as backup                       |                         |           |
   +-------------------------------------------+-------------------------+-----------+

Performance levels may be a single value or may vary by climate. Values that vary by warm and cold climate use the value for the segment's region, and dual fuel measures use the warm climate value. Values that vary by IECC climate zone use the value for the largest IECC zone in the region.

How incentives are calculated
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``modification`` column sets how a row changes the AEO incentive. All rows in the current file use ``replace``.

* ``remove`` removes the incentive for the segment and takes priority over the other two types.
* ``replace`` sets the incentive to the value calculated below.
* ``extend`` applies only if no ``replace`` rows apply. It continues the highest AEO incentive available up to that year, with any increase set by ``increase pct``.

The value of a ``replace`` row is its ``rebate amount``, or ``credit pct`` as a percentage of installed cost. If a row has both, the rebate amount caps the credit. This value is then multiplied by ``applicable fraction``, the share of the state's stock or energy use that the program reaches.

Where several ``replace`` rows apply to one segment, they are combined as follows:

#. Rows are grouped by ``program id`` and ``applicable fraction``.
#. Within a group, only the highest incentive is used. These rows are alternatives within one program, such as tiers.
#. Incentives from different groups are added together. These rows represent different programs, or different customer groups of one program, such as income bands.

For example, take a measure that qualifies for two tiers of a utility program, worth $300 and $500, each with a fraction of 0.4, and for a statewide program worth $1000 with a fraction of 1. The incentive is $500 x 0.4 + $1000 x 1 = $1200.

When a row applies to heat pumps for one of the heating or cooling end uses, Scout adds a zero-value copy of the row for the other end use. This prevents the row from combining with any AEO incentive for that other end use.

File format
~~~~~~~~~~~

Each row of the file represents one program for one set of states, building types, vintages, end uses, technologies, and customers.

.. list-table:: Columns in ``incentives.csv``.
   :header-rows: 1
   :widths: 25 75

   * - Column
     - Contents
   * - ``scenario``
     - Scenario that the row belongs to.
   * - ``description``
     - Program description and source.
   * - ``state(s)``
     - States that the row applies to, separated by commas. ``all`` means every state in the run, and ``USCA`` means the 21 U.S. Climate Alliance states that Scout models (all but HI).
   * - ``building type(s)``
     - Building types, separated by commas. ``all``, ``all residential``, and ``all commercial`` are expanded to the matching Scout building types. ``unspecified`` is ignored.
   * - ``building vintage(s)``
     - ``new``, ``existing``, or ``all``.
   * - ``end use(s)``
     - End uses, separated by commas. ``all`` matches any end use, and ``all fossil`` means heating, water heating, cooking, drying, and other.
   * - ``tech(s)``
     - Technologies, separated by commas. ``all`` matches any technology.
   * - ``fuel type(s)``
     - Fuel of the technology receiving the incentive. ``all`` means all four Scout fuels, and ``all fossil`` means natural gas, distillate, and other fuel.
   * - ``base fuel``
     - Fuel being replaced: one or more specific fuels separated by commas (for example, ``distillate, other fuel``), ``electricity``, ``all``, or ``all fossil``, which limits the row to fuel switching. If blank, the value of ``fuel type(s)`` is used.
   * - ``base fuel backup``
     - Whether the existing system may or must stay as backup: ``no``, ``yes``, or ``required``.
   * - ``modification``
     - ``replace``, ``extend``, or ``remove``.
   * - ``scope``
     - ``federal``, ``non-federal``, or ``all``. A blank or other value is read as ``all``. Used by the federal and sub-federal options of ``--incentive_restrictions``, where ``all`` counts as both.
   * - ``ira``
     - ``yes`` if funded by the IRA, otherwise blank.
   * - ``increase pct``
     - Percentage increase to apply to an ``extend`` row. If blank, 0.
   * - ``performance level``, ``performance units``
     - Minimum performance needed to qualify, or the maximum for units where a lower value is better.
   * - ``credit pct``
     - Credit as a percentage of installed cost.
   * - ``rebate amount``, ``rebate units``
     - Rebate value and units, which must match the units of the segment's cost data. ``$/home`` is treated as ``$/unit``.
   * - ``start year``, ``end year``
     - First and last years that the row applies. If blank, the row has no start or end limit.
   * - ``applicable fraction``, ``fraction notes``
     - Share of the state's stock or energy use that the program reaches, and the source of that share. A blank fraction is read as 1.
   * - ``program id``
     - Required identifier for the program, typically in the form ``<state>-<program website domain>-<res|com>``, with ``-HEAR`` added for HEAR rows. Rows created for the non-reference scenarios use ``all-bss-25c-res`` for the federal tax credit and ``<state>-bss-ny-<hear|util>-anchor-<res|com>`` for rows based on New York programs. Alternatives within one program must share an id, and different programs must not. A missing column or blank value raises an error.

Representation conventions
~~~~~~~~~~~~~~~~~~~~~~~~~~

The current file follows these conventions:

* **Base fuel:** rebates only for replacing electric equipment use ``electricity``, rebates available whatever is replaced use ``all``, and fuel switching rebates use ``all fossil``.
* **Tiers:** a higher tier has its own row only if its performance threshold differs in Scout's units. If tiers differ only in a metric that Scout does not check, only the lowest tier is included. Otherwise, every unit would receive the top tier.
* **HEAR rebates:** ``reference`` rows follow DOE Program Notices 26-1 and 26-2. Cooking, drying, and water heating rows use a ``base fuel`` of ``electricity``. Heat pump heating rows use a ``base fuel`` of ``all`` and a ``base fuel backup`` of ``required``, so a measure that switches from a fossil fuel receives the rebate only if it keeps the existing system as backup.
* **Fully reserved programs:** programs that are fully reserved or waitlisted but are expected to continue remain in the file.

.. _policy-incentive-scenarios:

Non-reference scenarios
~~~~~~~~~~~~~~~~~~~~~~~

The ``aggressive-fuel-neutral``, ``aggressive-electric``, and ``aggressive`` rows are built from the BSS Reference+ Scenario Input Rules, which each of these rows links to in its ``description``. Each scenario adds three kinds of rows to the ``reference`` rows.

**Extended programs.** State-level programs continue to 2050, starting the year after the ``reference`` row ends and using the same ``program id``. State-level programs are all HEAR programs and a set of statewide programs, such as Mass Save, Efficiency Maine, and Energy Trust of Oregon. Utility programs are not extended, so they end when their ``reference`` rows end.

**New York-based programs.** Other U.S. Climate Alliance states receive rows for 2035-2050, based on New York's programs, for building types where they have no continuing program of the same kind:

* An income-limited tier uses New York's HEAR levels, with a fraction equal to the state's share in the same income band. These rows use a ``-bss-ny-hear-anchor-`` program id and are not tagged as IRA-funded, so "no ira" does not remove them.
* A market-rate tier uses New York's utility program levels, weighted by each utility's share of New York's service territory, with a fraction of 1.

**Federal tax credit.** Rows modeled on the 25C credit start in 2030. They are tagged as federal and IRA-funded, and provide 30% of installed cost up to the ``rebate amount``.

The scenarios differ as follows:

.. list-table:: Differences between the non-reference incentive scenarios.
   :header-rows: 1
   :widths: 25 25 25 25

   * -
     - ``aggressive-fuel-neutral``
     - ``aggressive-electric``
     - ``aggressive``
   * - HEAR rows
     - Keep their ``reference`` conditions
     - Require fossil fuel switching with no backup; envelope rows are dropped
     - Backup changed to ``yes`` (allowed, not required), except on envelope rows
   * - Other extended rows
     - Keep their conditions, but rows that require fuel switching with no backup are not extended
     - Require fossil fuel switching with no backup; envelope and air conditioning rows are dropped
     - Keep their conditions
   * - Federal tax credit
     - 2030-2040: heat pumps, heat pump water heaters, fossil furnaces, boilers and water heaters, central air conditioning, walls, and windows
     - 2030-2050: heat pumps and heat pump water heaters only
     - 2030-2040: same as ``aggressive-fuel-neutral``

Limitations
~~~~~~~~~~~

The following programs are not represented in the file:

* programs paid per kWh, kW, or MMBtu, custom programs, direct install programs, financing, and tax exemptions, because Scout has no equivalent per-measure value, and
* commercial programs whose amounts could not be confirmed: DTE, Evergy, Entergy Mississippi, OG&E, PSO, and Efficiency Maine. This applies to the ``reference`` rows. In the non-reference scenarios, the New York-based rows provide commercial incentives in some of these programs' states from 2035.

Updating the file
~~~~~~~~~~~~~~~~~

The ``reference`` rows are updated annually using an LLM agent workflow, not an automated pipeline. An agent drafts rows from a full download of the DSIRE program database and from program websites, a second LLM independently reviews the result, and a human reviewer makes the final decisions. Utility and gas service territory fractions are calculated from EIA-861 and EIA-176 data. Income-based and county-based fractions are calculated from ResStock 2025 release 1, as the share of residential site energy in the eligible households. See the :repo_file:`incentives update README <scout/supporting_data/sub_fed/dsire/README_incentives_update.md>` for the full process and a checklist.
