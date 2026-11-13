.. _policy-inputs:

Policy Inputs
=============

This section describes the state and local policy data that Scout uses to adjust its baseline, and how to build policy scenarios from them.

Scout represents these policies with five input files in |html-filepath| ./scout/supporting_data/sub_fed/ |html-fp-end|. Each file is turned on by its own option, and Scout reads the files only when ``--alt_regions`` is ``State``.

.. list-table:: Sub-federal policy inputs.
   :header-rows: 1
   :widths: 20 30 50

   * - File
     - Option
     - Contents
   * - ``incentives.csv``
     - ``--incentive_levels``
     - Rebates and tax credits that reduce installed costs. See :ref:`policy-incentives`.
   * - ``rates.csv``
     - ``--low_volume_rate``
     - Lower volumetric electricity rates, possibly with higher fixed charges.
   * - ``appl_regs.csv``
     - ``--state_appl_regs``
     - Regulations that remove certain appliance choices from the market.
   * - ``codes.csv``
     - ``--codes``
     - Building codes for new construction, beyond the model code.
   * - ``bps.csv``
     - ``--bps``
     - Building performance standards for existing buildings.

In a run configuration file, ``incentive_levels`` sits under ``ecm_prep: incentives:`` and the other four options under ``ecm_prep: sub_fed_policy:``.

.. _policy-scenarios:

Policy scenarios
----------------

How scenarios work
~~~~~~~~~~~~~~~~~~

Every row of each file has a ``scenario`` value, and the option for that file selects which scenario's rows to use.

* ``reference`` rows represent currently enacted policies. For incentives, they also include paused or fully reserved programs that are expected to resume, such as some HEAR programs.
* Every other scenario is built on top of the reference case. Selecting it uses the ``reference`` rows plus that scenario's own rows.
* ``null`` turns the input off. For incentives, ``aeo`` (the default) plays this role and keeps the AEO incentives with no modifications.

Because the reference case is always included, a scenario's rows only need to describe how the scenario differs from it, such as programs that run for longer, policies in more states, or higher incentive levels. A file with no rows for a scenario gives the same result as ``reference``.

Scenario rows are combined with ``reference`` rows as follows:

* **Incentives and rates:** each scenario row is trimmed to the years and applicable fraction that the ``reference`` rows for the same segment do not already cover. For incentives, a scenario row is dropped for any years in which a ``reference`` row from the same program already provides at least the same incentive, for the same applicable fraction and performance requirements. Rows from different programs, or for different fractions of one program, are kept, since these add to each other.
* **Appliance regulations, codes, and BPS:** ``reference`` and scenario rows are used together. A scenario row that is identical to a ``reference`` row is dropped.

For every file except ``incentives.csv``, Scout then checks applicable fractions, first for the ``reference`` rows alone and then with the scenario rows added. It stops with an error if fractions below 1 overlap in a segment and year and add up to more than 1.

Creating a scenario
~~~~~~~~~~~~~~~~~~~

#. **Add rows.** Choose a scenario name and add rows with that name to each file that the scenario changes. Do not copy the ``reference`` rows, since they are already included. The same name can be used in several files, so that one setting describes a consistent policy scenario across them.
#. **Allow the name.** Scout only accepts option values listed in |html-filepath| ./scout/supporting_data/config_schema.yml |html-fp-end|. Add the name to the ``enum`` list of each option that should accept it, then run ``docs/generate_readable_cfg.py`` to update ``docs/config_readable.yml``.
#. **Select it.** Set the options to the new name, either on the command line or in a run configuration file:

   .. code-block:: yaml

      ecm_prep:
        alt_regions: State
        sub_fed_policy:
          low_volume_rate: my-scenario
          state_appl_regs: my-scenario
          bps: my-scenario
          codes: my-scenario
        incentives:
          incentive_levels: my-scenario
          incentive_restrictions: null

   Each option is set separately, so a run can mix scenarios, for example ``reference`` codes with ``my-scenario`` incentives. ``--incentive_restrictions`` can further remove incentives from any scenario (see :ref:`policy-incentives`).

Example: BSS scenarios
~~~~~~~~~~~~~~~~~~~~~~

The input files include three scenarios built for the Building Sector Scenarios (BSS) analysis, following the BSS Reference+ Scenario Input Rules. The ``reference`` case maps to the BSS REF and Sens-3 scenarios. Each of the other three adds to it:

* ``aggressive-fuel-neutral`` (BSS Core-2): strong additional efficiency policies that are fuel neutral, with no electrification policies beyond the reference case.
* ``aggressive-electric`` (BSS Core-3): strong electrification policies, with no efficiency policies beyond the reference case.
* ``aggressive`` (BSS Core-4): strong additional policies for both efficiency and electrification.

New policies start in two waves. First-mover states adopt them in 2030, and the remaining U.S. Climate Alliance states follow in 2035. Where a state's reference policy covers only part of the state or only one of the targets, the scenario raises it to the full statewide target. Incentives have their own timing, described in :ref:`policy-incentive-scenarios`.

.. list-table:: What each BSS scenario adds to the reference case, by input.
   :header-rows: 1
   :widths: 16 28 28 28

   * - Input
     - ``aggressive-fuel-neutral``
     - ``aggressive-electric``
     - ``aggressive``
   * - Appliance regulations
     - Nothing (no rows)
     - Emissions limits for residential heating and water heating, based on California Air Resources Board (CARB) rules
     - Same as ``aggressive-electric``
   * - Codes
     - Stretch code with 20% energy savings over the latest base code, with no fossil fuel requirement
     - 100% onsite fossil fuel reduction target, with no efficiency requirement
     - Both the efficiency and the fossil fuel targets
   * - BPS
     - 20% EUI reduction target, with no fossil fuel requirement
     - Onsite fossil fuel reduction target of 20%, rising to 100% ten years later: 2030 to 2040 in first-mover states, 2035 to 2045 in the others. No efficiency requirement.
     - Both the EUI and the fossil fuel targets
   * - Incentives
     - State-wide heating and cooling programs extended to 2050, except those that require fuel switching with no backup. Programs based on Mass Save fill gaps from 2035. Federal 25C-type tax credit for 2030-2040.
     - Extended and Mass Save-based programs require switching from fossil fuels, with no backup. No incentives for replacing electric equipment, envelope, or air conditioning. 25C-type credit for 2030-2040, for heat pumps and heat pump water heaters only.
     - State-wide programs extended to 2050, with most backup requirements made optional. Programs based on Mass Save fill gaps from 2035. 25C-type credit for 2030-2040.
   * - Rates
     - Nothing (no rows)
     - 20% winter rate reduction for residential heat pumps, in the states with appliance regulations, for customers not already covered in the reference case
     - Same as ``aggressive-electric``

:ref:`policy-incentive-scenarios` describes the incentive rows in detail.

The BSS run configuration files in |html-filepath| ./batch/bss-v2/ |html-fp-end| show how these scenarios are combined with the reference case and with other options:

.. list-table:: Policy settings of the BSS run configuration files.
   :header-rows: 1
   :widths: 22 26 26 26

   * - File
     - Rates, appliance regulations, codes, and BPS
     - ``incentive_levels``
     - ``incentive_restrictions``
   * - ``aeo.yml``, ``min_switch.yml``, ``dual_switch.yml``
     - ``null``
     - ``aeo``
     - ``null``
   * - ``ref.yml``
     - ``reference``
     - ``reference``
     - ``null``
   * - ``high_switch.yml``
     - ``reference`` rates; others ``null``
     - ``reference``
     - ``null``
   * - ``fossil.yml``
     - ``null``
     - ``reference``
     - ``no federal electric``
   * - ``state.yml``
     - ``aggressive``
     - ``aggressive state``
     - ``no federal``
   * - ``accel.yml``, ``brk.yml``
     - ``aggressive``
     - ``aggressive``
     - ``null``

``state.yml`` uses ``aggressive state``, which has no rows in ``incentives.csv``. Its incentives are therefore the ``reference`` incentives, with federal incentives removed.

.. _policy-incentives:

Incentives
----------

Scout's baseline includes the equipment incentives represented in the EIA Annual Energy Outlook (AEO). The file |html-filepath| ./scout/supporting_data/sub_fed/incentives.csv |html-fp-end| modifies those incentives to reflect federal, state, and utility programs, such as rebates and tax credits. Incentives reduce the installed cost of both baseline and measure technologies in the applicable segments. Installed costs cannot fall below zero.

Selecting incentives
~~~~~~~~~~~~~~~~~~~~

``--incentive_levels`` selects a scenario from the file, as described in :ref:`policy-scenarios`. The default, ``aeo``, uses the AEO incentives only. ``reference`` uses state, local, and utility programs, including IRA-funded home electrification rebates, but no federal tax credits. For other regions than ``State``, ``--incentive_levels`` has no effect and only the AEO incentives are used.

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
     - Required identifier for the program, typically in the form ``<state>-<program website domain>-<res|com>``, with ``-HEAR`` added for HEAR rows and ``-income`` for a program's income-qualified tier. HEAR programs that have not launched use ``<state>-planned-res-HEAR``. Rows created for the BSS scenarios use ``all-bss-25c-res`` for the federal tax credit and ``<state>-bss-ma-anchor-<res|com>`` for rows based on Mass Save. Alternatives within one program must share an id, and different programs must not. A missing column or blank value raises an error.

Representation conventions
~~~~~~~~~~~~~~~~~~~~~~~~~~

The current file follows these conventions:

* **Base fuel:** rebates only for replacing electric equipment use ``electricity``, rebates available whatever is replaced use ``all``, and fuel switching rebates use ``all fossil``.
* **Backup:** heat pump heating rows use ``yes`` unless the program rules out keeping the existing system. Whole-home offers that require removing it use ``no``.
* **Tiers:** a higher tier has its own row only if its performance threshold differs in Scout's units. If tiers differ only in a metric that Scout does not check, only the lowest tier is included. Otherwise, every unit would receive the top tier.
* **Income-qualified tiers:** a program's income-qualified tier has its own rows, with the full incentive for that group rather than the increase over the market-rate tier. The fraction of the program's market-rate rows is reduced to cover only the remaining households.
* **HEAR rebates:** ``reference`` rows follow DOE Program Notices 26-1 and 26-2. Each measure has two income-band rows: 100% of installed cost for households below 80% of area median income, and 50% for those from 80% to 150%, each capped at the per-measure limit. Cooking, drying, and water heating rows use a ``base fuel`` of ``electricity``. Heat pump heating rows use a ``base fuel`` of ``all`` and a ``base fuel backup`` of ``required``, so a measure that switches from a fossil fuel receives the rebate only if it keeps the existing system as backup.
* **Paused and planned programs:** programs that are fully reserved, waitlisted, or paused but are expected to resume remain in the file. States that have not launched HEAR have planned rows for 2027-2031 at the per-measure caps.

.. _policy-incentive-scenarios:

BSS incentive scenarios
~~~~~~~~~~~~~~~~~~~~~~~

The incentive rows of the BSS scenarios (see :ref:`policy-scenarios`) are an example of how a scenario can build on the reference case. The ``aggressive-fuel-neutral``, ``aggressive-electric``, and ``aggressive`` rows are built from the BSS Reference+ Scenario Input Rules, which each of these rows links to in its ``description``. Each scenario adds three kinds of rows to the ``reference`` rows.

**Extended programs.** State-wide programs continue to 2050, starting the year after the ``reference`` row ends and using the same ``program id``. A program counts as state-wide if its applicable fraction is 1, if it is a statewide income-qualified program such as HEAR, or if it is one of several sub-state programs that together cover more than 80% of the state. Other utility programs end when their ``reference`` rows end.

**Mass Save-based programs.** From 2035 to 2050, segments of U.S. Climate Alliance states with no continuing state-wide program receive rows based on Mass Save's market-rate rebates, with a fraction of 1. For residential heat pumps, these are $7,050 for whole-home installations with no backup, $3,000 for partial-home installations that keep the existing system, and $750 for replacing electric equipment. Income-qualified households receive these rebates in addition to the state's extended HEAR or income-qualified rows. Only Mass Save's market-rate offers are used in other states: Massachusetts keeps its own extended program, including its income-eligible tier, and no HEAR programs are added beyond those in the reference case. These rows use a ``-bss-ma-anchor-`` program id and are not tagged as IRA-funded, so "no ira" does not remove them.

**Federal tax credit.** Rows modeled on the 25C credit apply from 2030 to 2040. They are tagged as federal and IRA-funded, and provide 30% of installed cost up to the ``rebate amount``.

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
     - Backup changed from ``required`` to ``yes`` (allowed, not required)
   * - Other extended rows
     - Heating and cooling only. Keep their conditions, but rows that require fuel switching with no backup are not extended
     - Require fossil fuel switching with no backup; rows for replacing electric equipment, envelope, and air conditioning are dropped
     - Keep their conditions, except that programs that require backup on their own, such as Efficiency Vermont and CenterPoint Energy (MN), change to ``yes``. Mass Save's partial-home tier still requires backup
   * - Mass Save-based rows
     - Heating only: partial-home heat pumps that keep a fossil backup, heat pumps replacing electric heating, commercial rooftop heat pumps, insulation, and windows. No whole-home tier
     - Whole-home and partial-home heat pumps, commercial rooftop heat pumps, water heating, cooking, and drying, all requiring fossil fuel switching with no backup. No envelope or electric-replacement rows
     - All tiers with Mass Save's conditions, including envelope, water heating, cooking, and drying
   * - Federal tax credit
     - Heat pumps, heat pump water heaters, fossil furnaces, boilers and water heaters, central air conditioning, walls, and windows
     - Heat pumps and heat pump water heaters only, for fossil fuel switching with no backup
     - Same as ``aggressive-fuel-neutral``

Limitations
~~~~~~~~~~~

The following programs are not represented in the file:

* programs paid per kWh, kW, or MMBtu, custom programs, direct install programs, financing, and tax exemptions, because Scout has no equivalent per-measure value, and
* commercial programs whose amounts could not be confirmed: DTE, Evergy, Entergy Mississippi, OG&E, PSO, and Efficiency Maine. This applies to the ``reference`` rows. In the BSS scenarios, the Mass Save-based rows provide commercial incentives in some of these programs' states from 2035.

Updating the file
~~~~~~~~~~~~~~~~~

The ``reference`` rows are updated annually using an LLM agent workflow, not an automated pipeline. An agent drafts rows from a full download of the DSIRE program database and from program websites, a second LLM independently reviews the result, and a human reviewer makes the final decisions. Utility and gas service territory fractions are calculated from EIA-861 and EIA-176 data. Income-based and county-based fractions are calculated from ResStock 2025 release 1, as the share of residential site energy in the eligible households. See the :repo_file:`incentives update README <scout/supporting_data/sub_fed/dsire/README_incentives_update.md>` for the full process and a checklist.
