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

.. table:: Valid options for ``--incentive_levels``.

   +----------------------+----------------------------------------------------------------+
   | Option               | Incentives used                                                |
   +======================+================================================================+
   | aeo (default)        | AEO incentives only, with no modifications.                    |
   +----------------------+----------------------------------------------------------------+
   | reference            | Rows with the ``reference`` scenario.                          |
   +----------------------+----------------------------------------------------------------+
   | aggressive           | ``reference`` rows, plus ``aggressive`` rows layered on them.  |
   +----------------------+----------------------------------------------------------------+
   | optimistic,          | ``reference`` rows, plus any rows for the given scenario. The  |
   | aggressive state     | file currently has no rows for these two scenarios, so they    |
   |                      | currently give the same result as ``reference``.               |
   +----------------------+----------------------------------------------------------------+

When scenario rows are layered on ``reference`` rows, a scenario row is dropped for any years in which a ``reference`` row from the same program already provides at least the same incentive, for the same applicable fraction and performance requirements. Rows from different programs, or for different fractions of one program, are kept.

``--incentive_restrictions`` removes selected incentives from the analysis, including those in the AEO baseline. Valid options are:

* "all" removes all incentives.
* "no ira" removes rows tagged as funded by the Inflation Reduction Act (IRA).
* "no federal" and "no sub-federal" remove federal and non-federal incentives.
* "no electric" and "no fossil" remove incentives for electric and non-electric segments.
* "no federal electric", "no federal fossil", "no sub-federal electric", and "no sub-fed fossil" combine these two restrictions.

.. note::
   The "no sub-fed fossil" option currently has no effect, because ``ecm_prep.py`` checks for the name "no sub-federal fossil" instead.

Which rows apply
~~~~~~~~~~~~~~~~

A row applies to a segment in a given year when all of the following are true:

* **Segment:** the state, building type, vintage, end use, and technology match.
* **Year:** the year falls between ``start year`` and ``end year``.
* **Fuel:** ``base fuel`` matches the fuel being replaced, and ``fuel type(s)`` matches the fuel of the technology receiving the incentive.
* **Backup:** for measures that switch fuels, ``base fuel backup`` is compatible with the measure, as shown below.
* **Performance:** the technology meets ``performance level``, in ``performance units`` that match the technology's units.

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
   * - ``state(s)``, ``building type(s)``, ``building vintage(s)``, ``end use(s)``, ``tech(s)``
     - Segments that the row applies to.
   * - ``fuel type(s)``
     - Fuel of the technology receiving the incentive.
   * - ``base fuel``
     - Fuel being replaced: a specific fuel, ``electricity``, ``all``, or ``all fossil``, which limits the row to fuel switching.
   * - ``base fuel backup``
     - Whether the existing system may or must stay as backup: ``no``, ``yes``, or ``required``.
   * - ``modification``
     - ``replace``, ``extend``, or ``remove``.
   * - ``scope``
     - ``federal``, ``non-federal``, or ``all``.
   * - ``ira``
     - ``yes`` if funded by the IRA, otherwise blank.
   * - ``increase pct``
     - Percentage increase to apply to an ``extend`` row.
   * - ``performance level``, ``performance units``
     - Minimum performance needed to qualify, or the maximum for units where a lower value is better.
   * - ``credit pct``
     - Credit as a percentage of installed cost.
   * - ``rebate amount``, ``rebate units``
     - Rebate value and units, which must match the units of the segment's cost data. ``$/home`` is treated as ``$/unit``.
   * - ``start year``, ``end year``
     - First and last years that the row applies.
   * - ``applicable fraction``, ``fraction notes``
     - Share of the state's stock or energy use that the program reaches, and the source of that share.
   * - ``program id``
     - Required identifier for the program, typically in the form ``<state>-<program website domain>-<res|com>``, with ``-HEAR`` added for rows funded by the IRA. Alternatives within one program must share an id, and different programs must not. A missing column or blank value raises an error.

Representation conventions
~~~~~~~~~~~~~~~~~~~~~~~~~~

The current file follows these conventions:

* **Base fuel:** rebates only for replacing electric equipment use ``electricity``, rebates available whatever is replaced use ``all``, and fuel switching rebates use ``all fossil``.
* **Tiers:** a higher tier has its own row only if its performance threshold differs in Scout's units. If tiers differ only in a metric that Scout does not check, only the lowest tier is included. Otherwise, every unit would receive the top tier.
* **IRA heat pump rebates:** these rows use a ``base fuel backup`` of ``required``, following DOE HEEHRA Program Notice 26-2.
* **Fully reserved programs:** programs that are fully reserved or waitlisted but are expected to continue remain in the file.

Limitations
~~~~~~~~~~~

The following programs are not represented in the file:

* programs paid per kWh, kW, or MMBtu, custom programs, direct install programs, financing, and tax exemptions, because Scout has no equivalent per-measure value, and
* commercial programs whose amounts could not be confirmed: DTE, Evergy, Entergy Mississippi, OG&E, PSO, and Efficiency Maine.

Updating the file
~~~~~~~~~~~~~~~~~

The file is updated annually using an LLM agent workflow, not an automated pipeline. An agent drafts rows from a full download of the DSIRE program database and from program websites, a second LLM independently reviews the result, and a human reviewer makes the final decisions. Applicable fractions are calculated from EIA-861, EIA-176, and DOE LEAD data. See the :repo_file:`incentives update README <scout/supporting_data/sub_fed/dsire/README_incentives_update.md>` for the full process and a checklist.
