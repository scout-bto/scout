.. _analysis-approach:

Analysis Approach
=================

A full analysis in Scout has three primary steps, which are detailed further in the sections below. 

1. Develop an initial ECM definition.
2. Finalize ECM definition by retrieving additional performance and market data.
3. Simulate ECM impact across multiple adoption scenarios, with and without ECM competition.

.. .. _scout-overview:
.. .. figure:: images/Scout_OverviewSteps_r1.jpg

..    Scout ECM analyses require establishing an initial ECM definition; finalizing the ECM definition through integration of additional performance data and retrieval of baseline and efficient energy, carbon, and cost markets; and simulating ECM impacts with and without competition among ECMs considered.

.. _analysis-step-1:

Step 1: Develop initial ECM definition(s)
-----------------------------------------

Users may define entirely new ECMs or modify existing ECM definitions located in the |html-filepath| ./ecm_definitions |html-fp-end| directory. Each Scout ECM definition centers around seven user-specified attributes. Three of these seven attributes -- energy efficiency, installed cost, and lifetime -- may be assigned a probability distribution [#]_ instead of a point value; these attributes also require source information from the user. 

.. _ecm-sources:

Acceptable sources for ECM input definitions include: RSMeans_ (for installed cost); databases from EIA_, `ENERGY STAR`_, and national labs; peer-reviewed journal publications or reports; and product literature.

.. Acceptable sources for ECM input definitions include: RSMeans_ (for installed cost); `EnergyPlus/OpenStudio`_ (for energy efficiency, see :ref:`step 2 <analysis-step-2>`); databases from EIA_, `ENERGY STAR`_, and national labs; peer-reviewed journal publications or reports; and product literature.

Selections for the applicable baseline market parameters are used in :ref:`step 2 <analysis-step-2>` to retrieve total energy use, |CO2|, and operating cost data for the baseline market. The ECM can then be applied to that baseline market to calculate savings impacts. The specific values available for all of the applicable baseline market parameters are included in the :ref:`ecm-applicable-baseline-market` section.

.. _RSMeans: https://www.rsmeans.com/
.. _EnergyPlus/OpenStudio: http://apps1.eere.energy.gov/buildings/energyplus/
.. _EIA: https://www.eia.gov/analysis/studies/buildings/equipcosts/
.. _ENERGY STAR: https://www.energystar.gov/products/energy_star_most_efficient

.. _three residential: https://www.eia.gov/outlooks/aeo/assumptions/pdf/residential.pdf
.. _eleven commercial: https://www.eia.gov/outlooks/aeo/assumptions/pdf/commercial.pdf
.. _AEO: https://www.eia.gov/analysis/studies/buildings/equipcosts/pdf/full.pdf

.. _ecm-contents:

* Applicable baseline market parameters

   * Region (correspond to the 25 :ref:`EIA Electricity Market Module (EMM) regions <emm-reg>` by default; alternatively, the :ref:`contiguous U.S. states <state-reg>` or the five :ref:`AIA climate zones <cz-reg>`).
   * Building type (correspond to `three residential`_ and `eleven commercial`_ building types used in the EIA Annual Energy Outlook (AEO)).
   * Building vintage ("new" and/or "existing").
   * Fuel type ("electricity", "natural gas", "distillate", or -- for residential buildings only -- "other fuel").
   * End use (correspond to the major residential__ and commercial__ energy end uses defined in the AEO).
   * Technology name (for envelope components, technology names correspond to the names of residential__ and commercial__ thermal load components; for building equipment, technology names generally correspond to major equipment types used in the AEO_ [#]_).

.. anonymous links for the multiple cases of "residential" or "commercial" as the link text
.. __: https://www.eia.gov/outlooks/aeo/data/browser/#/?id=4-AEO2026&cases=cb2026&sourcekey=0
.. __: https://www.eia.gov/outlooks/aeo/data/browser/#/?id=5-AEO2026&cases=cb2026&sourcekey=0
.. __: https://github.com/trynthink/scout/blob/master/scout/supporting_data/thermal_loads_data/1999%20Residential%20heating%20and%20cooling%20loads%20component%20analysis.pdf
.. __: https://github.com/trynthink/scout/blob/master/scout/supporting_data/thermal_loads_data/1999%20Commercial%20heating%20and%20cooling%20loads%20component%20analysis.pdf

* Market entry and exit year                                

   * Market entry year reflects the first year the ECM is commercially available, while market exit year typically reflects a future efficiency standard that would render the ECM obsolete. 

* Energy efficiency                                        

   * Energy efficiency is specified at the unit level in absolute terms (e.g., U-value and solar heat gain coefficient for a window, or COP for a heat pump) using the :ref:`required units <ecm-performance-units>` or as a percentage relative savings value. 

..   * Relative savings percentages can be drawn from results of EnergyPlus/OpenStudio simulations. In such cases, the user flags the use of EnergyPlus/OpenStudio results in the energy efficiency input definition, and these results are filled in as part of :ref:`step 2 <analysis-step-2>` of the ECM analysis process.

* Installed cost

   * Product or technology :ref:`installed cost <first-ecm-installed-cost>` should be specified in absolute (not incremental) terms.
   * Cost units vary by building sector and technology type, as specified in the :ref:`ECM Definition Reference <ecm-installed-cost-units>`.

* Lifetime

   * Expected lifetime of the ECM in years.

* Additional ECM features

   * Is the ECM a service add-on or replacement?

      * ECMs may either directly replace the service of a comparable "business-as-usual" technology (e.g., a more efficient air source heat pump) or enhance the efficiency of this incumbent technology (e.g., a window film or HVAC controls retrofit).  
      * The choice of whether an ECM is of the "replacement" or "add-on" type has implications for cost calculations. In the former case, the ECM's incremental installed cost is calculated relative to that of the comparable baseline unit; in the latter case, the baseline cost is zero and the ECM's incremental installed cost is equal to its installed cost.

   * Does the ECM require fuel switching?

      * In cases where an ECM has a different fuel type than a comparable "business-as-usual" technology (e.g., an electric cold climate heat pump replacing a gas furnace for heating service), the user must specify the fuel type switched to (e.g., "electricity").

   * Time sensitive valuation of energy efficiency

      * Optionally, a user may specify one or more ECM features that apply efficiency impacts differently according to time of day and season, using hourly baseline energy load shapes, electricity costs, and average |CO2| emissions factors.

   * Will the ECM be combined with other ECMs in a package?

      * Individual ECMs may be combined into :ref:`package ECMs <analysis-packages>` that capture interactions between HVAC equipment and envelope and/or controls improvements, or between lighting equipment and controls improvements.

.. _analysis-step-2:

Step 2: Finalize ECM definition
-------------------------------

ECM definitions from :ref:`step 1 <analysis-step-1>` are finalized using the |html-filepath| ecm_prep.py |html-fp-end| module. The total (stock-wide) energy use, |CO2| emissions, and operating costs of the ECM are calculated for baseline and efficient cases, not accounting for ECM competition.

.. ECM definitions from :ref:`step 1 <analysis-step-1>` are finalized in two ways using the |html-filepath| ecm_prep.py |html-fp-end| script: 1) ECM energy efficiency is updated with results from EnergyPlus/OpenStudio simulations, and 2) the total (stock-wide) energy use, |CO2| emissions, and operating costs of the ECM are calculated for baseline and efficient cases, without accounting for ECM competition. Note that the former is only required when a user has flagged EnergyPlus/OpenStudio as the source of energy efficiency data in :ref:`step 1 <analysis-step-1>`.

.. _OpenStudio Measures: http://nrel.github.io/OpenStudio-user-documentation/getting_started/about_measures/
.. _EnergyPlus whole building energy simulation engine: https://energyplus.net/
.. _commercial reference building models: http://energy.gov/eere/buildings/commercial-reference-buildings
.. _on GitHub: https://github.com/NREL/OpenStudio-PTool/tree/master/design_docs

.. analysis-step-2-energyplus: (CONVERT BACK TO SECTION REFERENCE TAG)

.. Finalizing ECM efficiency input via EnergyPlus/OpenStudio
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. * Scout ECMs applicable to commercial buildings can be represented as `OpenStudio Measures`_ and simulated with the `EnergyPlus whole building energy simulation engine`_. EnergyPlus is capable of representing detailed heating, cooling, lighting, and other energy uses in buildings; it is thus well suited to represent ECMs that may affect energy use across multiple end uses (e.g., advanced envelope materials that affect both heating and cooling loads; high efficiency lighting that reduces cooling loads and increases heating loads; integrated heat pumps that save heating, cooling, and water heating energy; and building controls that save heating, cooling, lighting, and/or plug load energy).
   * OpenStudio Measures are applied to 16 `commercial reference building models`_ across five building vintages [#]_ and eight Building America climate zones [#]_.
   * Measure energy use outputs are specified by climate zone, building type, building vintage, fuel type, and end use. By comparing Measure energy use outputs against the energy use outputs of an equivalent baseline model with no Measures applied and mapping OpenStudio building types and vintages to those of Scout, relative energy savings percentages can be calculated and then used to specify a Scout ECM's energy efficiency.  
   * An initial set of OpenStudio Measures for Scout is under active development `on GitHub`_.  

.. _Annual Energy Outlook (AEO) reference case: https://www.eia.gov/outlooks/aeo/tables_ref.php

Calculating total baseline energy, |CO2|, and cost (uncompeted)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   * Total uncompeted energy use, |CO2| emissions, and operating cost baselines are calculated for each ECM from a projection of U.S. building stock, energy use, and unit characteristics over the _`modeling time horizon`, which runs from the AEO base year (e.g., 2026 for AEO 2026 data) through 2050. These baseline data are mostly drawn from the inputs and outputs of the EIA `Annual Energy Outlook (AEO) reference case`_ simulations. [#]_ Where AEO data are not available, such as for building envelope component and electronics technologies, BTO develops original datasets using multiple sources external to DOE.

      * Baseline stock data represent the total number of units of a certain incumbent or "business-as-usual" technology associated with a given baseline market and year in the projection period. An example is the number of air-source heat pump units in all existing single family homes in mixed dry climates in the year 2020. When a number of units value is not available or not applicable for a baseline market, such as for building envelope component technologies, total building floor area square footage associated with that baseline market and year is used to quantify the baseline stock.
      * Baseline energy use data represent the total energy use attributed to a certain baseline market and year in the projection period. For example, the energy used to provide heating in all existing single family homes in mixed dry climates in the year 2031.
      * Baseline technology characteristics data represent the primary attributes of an incumbent or "business-as-usual" building technology, namely the technology's energy efficiency (in absolute units, e.g., COP), installed cost, and lifetime. Additionally, these data include consumer choice parameters for each technology, which are used for ECM competition (see :ref:`step 3 <analysis-step-3>`).

   * Once baseline energy use numbers are established for each technology, these energy use numbers are by default translated from site to source (or "primary") energy using the fossil fuel equivalence method, with site-source conversion factors calculated from the electricity and electricity related losses data in the `AEO energy consumption by sector and source table`_. Users may instead select the `captured energy method`_ for site-source conversion or report results in site energy terms (see the ``--captured_energy`` and ``--site_energy`` :ref:`ecm_prep.py options <tuts-3-cmd-opts>`).
   * `Fuel-specific energy costs`_ and |CO2| emission intensities, calculated by dividing fuel-specific |CO2| emissions_ by fuel-specific `energy use`_, are also derived from AEO data. When the default EMM regions or states are used, electricity prices and |CO2| emission intensities are resolved by region (e.g., by EMM region from AEO Table 54); otherwise, national values are used. Users may also substitute alternative grid scenarios for the AEO electricity emissions intensities (see the ``--alt_ref_carb`` and ``--grid_decarb`` :ref:`ecm_prep.py options <tuts-3-cmd-opts>`). |CO2| emissions costs are drawn from the U.S. Environmental Protection Agency `social cost of greenhouse gases`_ estimates [#]_.
   * See :ref:`analysis-efficient-equations` for these calculations in equation form.

.. _energy use: 
.. _AEO energy consumption by sector and source table: https://www.eia.gov/outlooks/aeo/data/browser/#/?id=2-AEO2026&cases=cb2026&sourcekey=0
.. _Fuel-specific energy costs: https://www.eia.gov/outlooks/aeo/data/browser/#/?id=3-AEO2026&cases=cb2026&sourcekey=0
.. _emissions: https://www.eia.gov/outlooks/aeo/data/browser/#/?id=17-AEO2026&cases=cb2026&sourcekey=0
.. _stocks-and-flows: https://en.wikipedia.org/wiki/Stock_and_flow
.. _captured energy method: https://www.energy.gov/sites/prod/files/2016/10/f33/Source%20Energy%20Report%20-%20Final%20-%2010.21.16.pdf
.. _social cost of greenhouse gases: https://www.epa.gov/system/files/documents/2023-12/epa_scghg_2023_report_final.pdf

.. ADD LINK TO FIRST BULLET IN THIS SECTION WITH FURTHER DETAILS REGARDING THE DEVELOPMENT OF ORIGINAL DATASETS TO AUGMENT THE AEO DATA

Calculating total efficient energy, |CO2|, and cost (uncompeted)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   * Total uncompeted energy use, |CO2|  emissions, and operating cost baselines calculated for an ECM from the input data are used to generate the total uncompeted energy use, |CO2| emissions, and operating costs with the ECM implemented - herein referred to as the "efficient" case - as follows (see :ref:`analysis-efficient-equations` for the equations):

      * calculate an efficient energy fraction for the ECM; this is the fraction of per unit energy use under a full ECM implementation compared to the per unit energy use of a baseline case with no ECM implementation,
      * multiply the efficient energy fraction by the ECM's total baseline energy use to yield an efficient energy use total, and
      * use the ECM's total efficient energy use to calculate its total efficient |CO2| emissions and operating costs, using |CO2| emission intensities, fuel-specific energy cost data, and the `social cost of greenhouse gases`_.

   * The magnitude of the difference between an ECM's total baseline and efficient energy, |CO2|, and operating costs depends on what portion of the ECM's baseline market it can affect in each year of the projected time period. This available market portion is determined by `stocks-and-flows`_ in the baseline markets over time. The primary stock-and-flow variables accounted for in Scout are listed here.

      * Stock variables (measured at a point in time, i.e., in a given year)

         * Competed stock – defined as the number of technology units that are new or up for retrofit/replacement in a given year.
         * Non-competed stock – defined as the number of existing technology units not up for retrofit/replacement.

      * Flow variables (measured over a period of time, i.e., from year to year)

         * New additions – defined as the technology units associated with new building construction; it is a fraction of the total existing technology units, determined by the ratio of new buildings to total buildings (residential) or new square footage to total square footage (commercial). The NEMS residential__ and commercial__ sub-module documentation outlines the derivation of the new and total buildings stock and square footage data.
         * Retrofits – defined as the technology units up for replacement before the end of their useful lifetime; it is a fraction of the total existing technology units. Early retrofits are not modeled by default (i.e., the retrofit rate is zero); users may enable :ref:`component-specific early retrofit rates <retro-tab>` derived from renovation data in the Commercial Buildings Energy Consumption Survey (CBECS) and the American Housing Survey, either held constant or increasing over time (see the ``--retrofit_type`` :ref:`ecm_prep.py option <tuts-3-cmd-opts>`).
         * Replacements – defined as the technology units at the end of their useful lifetime; it is a fraction of the total existing technology units, determined by 1/lifetime of the existing technology, excepting technical potential cases (see next bullet).

.. __: https://www.eia.gov/analysis/pdfpages/m067index.php
.. __: https://www.eia.gov/analysis/pdfpages/m066index.php

   * _`ECM diffusion` into baseline markets is modeled under technical potential and maximum adoption potential scenarios. In both cases, the available market portion is entirely captured by ECMs (e.g., no competed stock remains with a "business-as-usual" technology). [#]_ The primary difference between the two scenarios is in how they define competed stock for the first year of ECM market entry:

      * in the technical potential case, an ECM competes for all new and existing stock in its market entry year, while 
      * in the maximum adoption potential scenario, an ECM competes for all new stock and existing stock that is up for retrofit or replacement in its market entry year.   

   * Under these two scenarios, the portions of a baseline market that are captured by an ECM never return to a "business-as-usual" technology option. In a technical potential case, this means the complete market saturation an ECM secures upon market entry is sustained across the entire projection period.
   * Because baseline markets are comprised mostly of existing stock (typically 97% or more in each year) and existing stock retrofit rates are zero by default and low when enabled (generally less than 2% in each year), the market diffusion of an ECM in a maximum adoption potential scenario is mostly driven by existing stock replacement rates. As shown in the maximum adoption scenario results of :numref:`ecm-diffusion-example`, replacement of technologies with short lifetimes yields immediate market saturation for an ECM (:numref:`ecm-diffusion-example`\ a) and no difference between the technical potential and maximum adoption potential scenario results, while replacement of technologies with moderate to long lifetimes yields more gradual diffusion of an ECM into its baseline market (:numref:`ecm-diffusion-example`\ b and :numref:`ecm-diffusion-example`\ c).

.. _ecm-diffusion-example:
.. figure:: images/Scout_Diffusion_Example.jpg

   Scout ECMs are applied to a baseline energy market under two technology diffusion scenarios: maximum adoption and technical potential. In a maximum adoption case, diffusion rates depend on realistic rates of new construction and retrofits in a given year, as well as the rate of turnover in the existing baseline equipment that an ECM could replace. The three ECMs shown represent (from left to right) fast, moderate, and slow diffusion rates under a maximum adoption scenario.

   * While the total baseline and efficient ECM energy, |CO2|, and operating costs calculated in this step account for stocks-and-flows, they do not account for competition across multiple ECMs for the same baseline market. ECM competition is handled in :ref:`step 3 <analysis-step-3>`.

.. _analysis-efficient-equations:

Baseline, stock turnover, and efficient-case equations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The baseline and efficient-case calculations above are applied separately to each baseline segment :math:`X` in an ECM's applicable baseline market (a unique combination of region, building type and vintage, fuel type, end use, and technology) in each year :math:`y` of the modeling time horizon, using the following terms:

* :math:`S_{X,y}`, :math:`E_{X,y}`, and :math:`C_{X,y}` are the segment's baseline stock (number of units, or floor area where units are not applicable), energy use, and |CO2| emissions (see :eq:`eq-baseline`);
* :math:`L_{X,y}` is the lifetime of the baseline technology, and :math:`r_{X,y}` is the early retrofit rate (zero by default);
* :math:`RP_{X,y}` is the ECM's relative performance: its per-unit energy use as a fraction of the comparable baseline technology's for units installed in year :math:`y`. It is calculated from the ECM's energy efficiency input as one minus the relative savings, or from absolute efficiency values as the ratio of baseline to ECM efficiency (the inverse for metrics where lower values are better, such as U-value).

**Baseline energy, CO**\ :sub:`2`\ **, and cost.** The segment's baseline energy use, |CO2| emissions, and energy cost are

.. math::
   :label: eq-baseline

   E_{X,y} = E^{site}_{X,y}\, F_{X,y}, \qquad C_{X,y} = E_{X,y}\, I_{X,y}, \qquad P_{X,y} = E_{X,y}\, p_{X,y}

where :math:`E^{site}_{X,y}` is the segment's site energy use from the AEO (split between new and existing buildings by the share of buildings or floor area constructed during the modeling time horizon), :math:`F_{X,y}` is the site-source conversion factor for the segment's fuel (1 if results are reported in site energy), and :math:`I_{X,y}` and :math:`p_{X,y}` are the |CO2| intensity and price of that fuel per unit of energy in the segment's region. |CO2| costs multiply :math:`C_{X,y}` by the `social cost of greenhouse gases`_. An ECM's total baseline in year :math:`y` sums these quantities over all segments in its applicable baseline market (e.g., :math:`E_y = \sum_{X} E_{X,y}`), where each segment is a unique combination of region, building type and vintage, fuel type, end use, and technology.

**Competed stock.** The fraction of the segment's stock that is new or up for replacement or retrofit in year :math:`y` is

.. math::
   :label: eq-competed-fraction

   c_{X,y} =
   \begin{cases}
   \dfrac{S_{X,y}-S_{X,y-1}}{S_{X,y}} + \dfrac{S_{X,y-L}-S_{X,y-L-1}}{S_{X,y}}, & X \text{ in new buildings}\\[2ex]
   \dfrac{1}{L_{X,y}} + r_{X,y}, & X \text{ in existing buildings}
   \end{cases}

For new buildings, the first term is the stock added in year :math:`y` and the second term is the replacement of stock added :math:`L` years earlier, once it reaches the end of its lifetime. For existing buildings, early retrofits stop once all of the existing stock has been competed, while replacements continue as units installed during the modeling time horizon reach the end of their lifetimes. The competed fraction is limited to 1, and in the technical potential scenario it is set to 1 in every year.

**Captured stock.** All competed stock is captured by the ECM once it is on the market, so the stock that the ECM has captured through year :math:`y` and its share of the segment are

.. math::
   :label: eq-captured-stock

   S^{m}_{X,y} = S^{m}_{X,y-1} + \gamma_{X,y}\, c_{X,y}\, S_{X,y}, \qquad \sigma_{X,y} = \frac{S^{m}_{X,y}}{S_{X,y}}

where :math:`\gamma_{X,y}` is 0 before the ECM's market entry year and 1 afterwards, unless it is scaled by exogenous conversion rates (``--exog_hp_rate_scenario``). Captured stock never exceeds the segment's total stock, and in the technical potential scenario :math:`\sigma_{X,y} = 1` from the market entry year onward.

**Relative performance of captured stock.** Units captured in different years may have different relative performance (e.g., as baseline efficiency changes over time), so the relative performance of all stock captured through year :math:`y` is updated each year as

.. math::
   :label: eq-captured-performance

   \overline{RP}_{X,y} = RP_{X,y}\,\Phi_{X,y} + \overline{RP}_{X,y-1}\,(1-\Phi_{X,y}), \qquad \Phi_{X,y} = \frac{\gamma_{X,y}\, c_{X,y}\, S_{X,y}}{S^{m}_{X,y}}

where :math:`\Phi_{X,y}` is the share of the captured stock that was captured in year :math:`y`, and :math:`\overline{RP}_{X,y} = RP_{X,y}` through the market entry year.

**Efficient energy and** |CO2|. The segment's efficient-case energy use and |CO2| emissions combine the captured stock, at the ECM's performance, with the uncaptured stock, at baseline performance:

.. math::
   :label: eq-efficient-energy

   E^{eff}_{X,y} = E_{X,y}\left[\sigma_{X,y}\,\overline{RP}_{X,y}\,k^{ss}_{X,y} + \left(1-\sigma_{X,y}\right)\right]

.. math::
   :label: eq-efficient-carbon

   C^{eff}_{X,y} = C_{X,y}\left[\sigma_{X,y}\,\overline{RP}_{X,y}\,k^{ss}_{X,y}\,k^{CO_2}_{X,y} + \left(1-\sigma_{X,y}\right)\right]

where :math:`k^{ss}_{X,y}` and :math:`k^{CO_2}_{X,y}` are the ratios of the ECM's fuel to the baseline fuel's site-source conversion factor and |CO2| intensity, respectively; both equal 1 unless the ECM switches fuels. Efficient-case energy costs are calculated in the same way using fuel prices, and |CO2| costs multiply :math:`C^{eff}_{X,y}` by the `social cost of greenhouse gases`_. The same equations, with :math:`c_{X,y}` in place of :math:`\sigma_{X,y}`, give the competed portion of the efficient case that is used in ECM competition (:ref:`step 3 <analysis-step-3>`).

The ECM's total uncompeted baseline and efficient results are the sums of these quantities across all of the segments in its applicable baseline market. For clarity, the equations omit several optional adjustments: time sensitive valuation features, backup fuel fractions for fuel switching ECMs, market scaling fractions, and secondary heating and cooling effects of lighting ECMs.

.. _analysis-packages:

Combining ECMs into packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   * Package ECMs combine individual ECMs to represent the interactions among them; see :ref:`package-ecms` for how packages are defined and which types of ECMs can be packaged.
   * The uncompeted baseline and efficient energy, |CO2|, and operating costs of each contributing ECM are first calculated as described above and then merged into a single package, as follows:

      * where contributing ECMs apply to the same baseline market segment (i.e., the same region, building type and vintage, fuel type, end use, and technology), the overlap is removed so that the baseline market is counted once and savings are not double counted (see :eq:`eq-pkg-direct-eff`);
      * where HVAC equipment and envelope ECMs both affect heating or cooling energy use in the same region, building type and vintage, fuel type, and end use, the equipment ECM's energy, |CO2|, and operating costs are further adjusted to reflect the combined performance of the equipment and envelope improvements, rather than the sum of their separate savings (see :eq:`eq-pkg-htcl`); and
      * any user-specified benefits from packaging are applied: an ``energy savings increase`` reduces the package's efficient-case energy use, |CO2| emissions, and associated costs by the given fraction, and a ``cost reduction`` reduces the package's installed cost by the given fraction.

   * The package's market entry year is the earliest, and its market exit year the latest, across its contributing equipment ECMs; its lifetime is the average lifetime of those ECMs.
   * By default, the installed cost of an HVAC equipment and envelope package includes only the HVAC equipment costs. With the ``--pkg_env_costs`` :ref:`option <tuts-3-cmd-opts>`, envelope costs are added (for commercial buildings, after converting them from units of floor area to the heating or cooling service demand units of the equipment costs). Its "include HVAC" setting also keeps the contributing equipment-only ECMs in the analysis to compete with the packages; its "exclude HVAC" setting does not.
   * With the ``--pkg_env_sep`` :ref:`option <tuts-3-cmd-opts>`, each HVAC equipment and envelope package is also prepared as a "(CF)" counterfactual in which the contributing HVAC equipment ECMs are held at baseline performance and cost, so that the impacts of the envelope portion of the package can be isolated.

.. _analysis-package-equations:

Package overlap equations
^^^^^^^^^^^^^^^^^^^^^^^^^

**ECMs that apply to the same segment.** Where ECM :math:`m` and one or more other ECMs :math:`o` in a package apply to the same baseline segment :math:`X`, let :math:`s_m = E_{X,y} - E^{eff}_{X,y,m}` and :math:`s_o` be each ECM's uncompeted energy savings in the segment on its own (subscripts :math:`X,y` are dropped below). ECM :math:`m` is assigned a share of the segment's baseline in proportion to its savings, and its efficient-case results are reduced by the savings of the other ECMs:

.. math::
   :label: eq-pkg-direct-base

   E^{pkg}_{m} = w_m\, E, \qquad w_m = \frac{s_m}{s_m + \sum_{o} s_o}

.. math::
   :label: eq-pkg-direct-eff

   E^{eff,pkg}_{m} = w_m \left( E^{eff}_{m} - RP^{c}_{m}\, \bar{s}_{-m} \right), \qquad RP^{c}_{m} = 1 - \frac{s_m}{\sigma_m\, E}, \qquad \bar{s}_{-m} = \frac{\sum_{o} s_o^{2}}{\sum_{o} s_o}

where :math:`RP^{c}_{m}` is ECM :math:`m`'s relative performance on the stock it captures (:math:`\sigma_m` from :eq:`eq-captured-stock`) and :math:`\bar{s}_{-m}` is the savings-weighted average savings of the other ECMs (equal to :math:`s_o` when there is only one other ECM). The package's baseline and efficient results in the segment are the sums of :math:`E^{pkg}_{m}` and :math:`E^{eff,pkg}_{m}` over its ECMs. The ECM's stock is scaled by :math:`w_m`, and its |CO2| emissions and energy costs are adjusted by the same factors as its energy use.

For example, consider a segment with baseline energy use :math:`E = 100` units, a heat pump ECM (A) that captures half of the segment's stock (:math:`\sigma_A = 0.5`) and saves 30% on it (:math:`\overline{RP}_A = 0.7`), and a controls ECM (B) for the same heat pumps that captures 80% of the stock (:math:`\sigma_B = 0.8`) and saves 10% on it (:math:`\overline{RP}_B = 0.9`).

* On their own (:eq:`eq-efficient-energy`), :math:`E^{eff}_{A} = 100\,(0.5 \times 0.7 + 0.5) = 85` and :math:`E^{eff}_{B} = 100\,(0.8 \times 0.9 + 0.2) = 92`, so :math:`s_A = 15` and :math:`s_B = 8` units, or 23 units in total.
* Baseline shares (:eq:`eq-pkg-direct-base`): :math:`w_A = 15/23 = 0.652` and :math:`w_B = 8/23 = 0.348`, so :math:`E^{pkg}_{A} = 65.2` and :math:`E^{pkg}_{B} = 34.8` units, which sum to the 100-unit baseline.
* Relative performance on captured stock: :math:`RP^{c}_{A} = 1 - 15/(0.5 \times 100) = 0.7` and :math:`RP^{c}_{B} = 1 - 8/(0.8 \times 100) = 0.9`. With only one other ECM, :math:`\bar{s}_{-A} = s_B = 8` and :math:`\bar{s}_{-B} = s_A = 15`.
* Efficient energy use (:eq:`eq-pkg-direct-eff`): :math:`E^{eff,pkg}_{A} = 0.652\,(85 - 0.7 \times 8) = 51.8` and :math:`E^{eff,pkg}_{B} = 0.348\,(92 - 0.9 \times 15) = 27.3` units.

The package's efficient energy use is thus 79.1 units and its savings are 20.9 units, rather than the 23 units from adding the two ECMs' separate savings.

**HVAC equipment and envelope ECMs.** For an HVAC equipment ECM :math:`m` in a package with envelope ECMs, each heating or cooling segment's baseline is unchanged and its efficient-case results are scaled by the relative performance of the envelope ECMs:

.. math::
   :label: eq-pkg-htcl

   E^{eff,pkg}_{X,y,m} = E^{eff}_{X,y,m} \left(1 - \Delta^{env}_{G,y}\right), \qquad \Delta^{env}_{G,y} = \frac{\sum_{e} \left(E_{G,y,e} - E^{eff}_{G,y,e}\right)}{E^{htcl}_{G,y}}

where :math:`G` is the region, building type and vintage, fuel type, and end use (heating or cooling) of segment :math:`X`; :math:`E_{G,y,e}` and :math:`E^{eff}_{G,y,e}` are the baseline and efficient energy use of envelope ECM :math:`e` in :math:`G`; and :math:`E^{htcl}_{G,y}` is the total heating or cooling energy use in :math:`G`. :math:`\Delta^{env}_{G,y}` is limited to between 0 and 1. The envelope ECMs add no baseline markets to the package, and the equipment and envelope savings combine multiplicatively.

For example, if a heat pump ECM on its own reduces a segment's heating energy use from 100 to 60 units, and the envelope ECMs save 20% of the total heating energy use in :math:`G` (:math:`\Delta^{env}_{G,y} = 0.2`), the package's efficient energy use is :math:`60 \times (1 - 0.2) = 48` units: savings of 52%, rather than the 60% from adding the 40% and 20% savings.

For clarity, the equations above show the total (cumulative) results and omit adjustments for market scaling fractions; the competed portion of each ECM's results is adjusted analogously, using the other ECMs' competed savings as a fraction of the competed baseline.

.. Time sensitive adjustment of total energy, |CO2|, and cost
.. ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..    * In cases where an ECM's efficiency impacts differ according to time of day and season, adjustment factors are applied to the annual energy, |CO2|, and cost totals calculated above to reflect these sub-annual effects. [#]_ :numref:`tsv-approach` summarizes the general approach used to develop the adjustments; data sources and preparation are further described below.

..    * The adjustment factors rely on four data sources:

..       * `geographical mapping data`_ developed by the U.S. Department of Energy that associate states, NERC regions and AIA climate zones with U.S. county-level population data,
..       * seasonal hourly `energy load shapes data`_ from the Electric Power Research Institute (EPRI),
..       * monthly `time of use utility rate data`_ from the Utility Rate Database (URDB), and
..       * seasonal hourly `marginal emissions data`_ from a 2012 Carnegie Mellon University (CMU) study of the U.S. electricity system.

..    * The data are translated into the format needed to support adjustment factors as follows:

..       * EPRI hourly load shapes, which are originally specified by NERC region, residential and commercial sector, end use, and peak (Jun--Sep) and off-peak (Oct--May) seasons, are translated to AIA climate zones using the geographical mapping data, then translated to summer (May--Sep), winter (Nov--Feb), and intermediate (all other months) seasons.
..       * URDB rates, which are originally specified by individual utility, residential and commercial sector, and month, are first translated to state-level geographic breakdown using `Form EIA-861`_, and then to AIA climate zones using the geographical mapping data; the monthly data are also aggregated into summer (May--Sep), winter (Nov--Feb), and intermediate (all other months) seasons.
..       * CMU hourly marginal emissions estimates, which are originally specified by NERC region and summer (May--Sep), winter (Nov--Feb), and intermediate (all other months) seasons, are translated to  AIA climate zones using the geographical mapping data.

..    .. _tsv-approach:
..    .. figure:: images/TSV_Approach.* 

..       This figure shows the three types of adjustment factors used to re-weight energy, |CO2|, and cost totals by time of day and season. First, the energy use adjustment distributes the annual energy use of a given climate zone, building type, and end use across all 24 hours of the day in summer, winter, and intermediate seasons (using the type of curves shown at bottom left). Second, the energy cost adjustment multiplies the hourly and seasonal energy use totals by hourly electricity prices for each season (using the type of curves shown at bottom center), which are specified by climate zone and building type. Finally, the |CO2| adjustment multiplies the hourly and seasonal energy use totals by associated hourly marginal emissions factors for each season (using the type of curves shown at bottom right), which are specified by climate zone. Form EIA-861 data are used to map utility rate data from utility region to state, and county-level population data are used to develop mappings from state and NERC region to the AIA climate zones.


.. Once user ECM definitions have been finalized in this step, the names of the ECMs are added to |html-filepath| run_setup.json |html-fp-end|, which contains a list of active ECM names to analyze in :ref:`step 3 <analysis-step-3>`. Users may choose to analyze only a subset of these existing ECMs by moving the names of ECMs that are not of interest in their analysis from the "active" to "inactive" lists in the |html-filepath| run_setup.json |html-fp-end| file. For example, such ECM subsets might exclude "add-on" ECMs, ECMs that involve fuel switching, or ECMs based on prospective cost or efficiency targets. Users may also run the |html-filepath| run_setup.py |html-fp-end| module, which can automatically move ECMs based on keyword searches of ECM names, as well as select ECMs based on the user's desired climate zone(s), building type(s), and structure type(s).

.. .. _geographical mapping data: https://docs.google.com/spreadsheets/d/1zT7DFaBNU8Oq2ofPv4SBKvbhk15n-Daz-ayhpczr8Q4/edit?usp=sharing
.. .. _energy load shapes data: http://loadshape.epri.com/enduse
.. .. _time of use utility rate data: https://openei.org/apps/USURDB/
.. .. _marginal emissions data: https://pubs.acs.org/doi/abs/10.1021/es300145v
.. .. _Form EIA-861: https://www.eia.gov/electricity/data/eia861/


.. _analysis-step-3:

Step 3: Simulate ECM impact
---------------------------

The final step, contained in the |html-filepath| run.py |html-fp-end| module, calculates each ECM's total energy savings, avoided |CO2| emissions, and operating cost savings impacts based on the total uncompeted energy use, |CO2| emissions, and operating costs calculated in :ref:`step 2 <analysis-step-2>`. Cost savings impacts are used to calculate per-unit financial metrics for the ECMs. Here, both competed and uncompeted ECM impacts and financial metrics are calculated. 

Calculating uncompeted ECM energy savings and financial metrics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Uncompeted ECM energy savings, avoided |CO2| emissions, and operating cost savings impacts are calculated by subtracting the total uncompeted efficient energy, |CO2|, and operating costs calculated in :ref:`step 2 <analysis-step-2>` from total uncompeted baseline energy, |CO2|, and operating costs calculated in :ref:`step 2 <analysis-step-2>`. Note that each of these total figures are calculated for technical potential and maximum adoption potential scenarios, and therefore ECM impacts and financial metrics are also described in terms of these scenarios.

* ECM _`financial metrics` are calculated by normalizing ECM savings impacts to the total number of stock units and comparing unit savings to the ECM's incremental capital cost over the comparable "business-as-usual" technology.

   * Internal Rate of Return (IRR) is the discount rate that balances the net present value of the ECM cost (negative cash flow) against the savings realized by the ECM on a per-unit basis (positive effective cash flow). 
   * Simple Payback Period divides the per-unit cost of the ECM by its per-unit annual energy savings compared to the "business-as-usual" unit.
   * Cost of Conserved Energy (CCE) divides the per-unit cost of the ECM by its discounted [#]_ per-unit lifetime savings compared to the "business-as-usual" unit. In one variant of the CCE calculation, discounted lifetime cost savings from avoided |CO2| emissions are added to the numerator of the calculation, using `social cost of greenhouse gases`_ estimates for |CO2| as a carbon tax.
   * Cost of Conserved |CO2| (CCC) follows the same calculation as CCE, but uses avoided |CO2| emissions in the denominator and energy cost savings in the numerator (if applicable).

.. _ECM-competition:

Competing ECMs and updating savings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ECMs with overlaps in their applicable baseline markets compete for the overlapping portions of these markets on the basis of their cost effectiveness from a consumer perspective. In general, ECMs with lower incremental capital costs and higher operational cost savings across their lifetimes capture larger portions of the overlapping baseline markets.
* For example, R-5, R-7, or R-10 window ECMs could each replace the same "business-as-usual" window technology. The initial savings impacts calculated for each of these ECMs will be based on the entire applicable baseline market. Those savings impacts must be scaled by the share of the baseline window market each ECM is modeled as capturing to avoid double counting of savings. Assuming the R-7 window is most cost effective and R-10 is least cost effective, the market shares might be R-5, 35%; R-7, 45%; and R-10, 20%.
* This use of market shares to reflect ECM competition ensures that competing ECMs with similar levels of cost effectiveness will have similar savings impacts after adjusting for competition.
* In general, ECM competition calculations in Scout weigh an ECM's annualized capital and operating costs against the capital and operating costs for competing ECMs to determine each ECM's competed market share. However, the specific calculation steps differ somewhat between the residential and commercial building sectors (see :ref:`analysis-competition-equations`).
* :ref:`Package ECMs <analysis-packages>` compete in the same way as individual ECMs. The individual ECMs that contribute to a package do not compete separately, with the exception of equipment-only ECMs retained using the "include HVAC" setting of the ``--pkg_env_costs`` option.
* Once ECM market shares are determined, uncompeted ECM savings impact estimates are multiplied by these market shares to arrive at competed ECM energy savings, avoided |CO2| emissions, and operating cost savings impacts. 
* For heating and cooling ECMs, a post-competition calculation is needed to ensure that total supply-side heating/cooling energy use (e.g., as consumed by a heat pump, or furnace) equals total demand-side heating/cooling energy use (e.g., that attributable to heat transfer through the envelope and other thermal load components) (see :eq:`eq-htcl-base`). 

.. _analysis-competition-equations:

Competition equations
^^^^^^^^^^^^^^^^^^^^^

Competition is carried out separately for each baseline segment :math:`X` that two or more ECMs apply to. In each year :math:`y`, the market shares of the set of competing ECMs on the market, :math:`M`, are calculated from each ECM's unit installed cost, :math:`U_{X,y,m}`, and unit annual operating (energy) cost, :math:`\psi_{X,y,m}`, adapting the approaches used in the NEMS residential__ and commercial__ demand modules. By default, these unit costs are averaged across all of the segments that the ECM applies to; the ``--high_res_comp`` option of |html-filepath| run.py |html-fp-end| uses the costs for each segment instead.

**Residential market shares** are calculated with a logit model:

.. math::
   :label: eq-comp-res

   \theta_{X,y,m} = \frac{\exp\left(\beta_{1,X,y}\, U_{X,y,m} + \beta_{2,X,y}\, \psi_{X,y,m}\right)}{\sum_{k \in M} \exp\left(\beta_{1,X,y}\, U_{X,y,k} + \beta_{2,X,y}\, \psi_{X,y,k}\right)}

where :math:`\beta_{1,X,y}` and :math:`\beta_{2,X,y}` are the AEO residential choice coefficients that weight the influence of capital and operating costs for the segment's technology, building type, and year (both are negative, so lower costs yield higher market shares).

For example, consider two heat pump ECMs competing for a residential heating segment: ECM A costs $6,000 to install and $700 per year to operate, and ECM B costs $4,500 and $1,000 per year. With the 2030 coefficients for residential air-source heat pumps, :math:`\beta_1 = -0.000169` and :math:`\beta_2 = -0.00260`, the exponents are :math:`-0.000169 \times 6000 - 0.00260 \times 700 = -2.83` for A and :math:`-0.000169 \times 4500 - 0.00260 \times 1000 = -3.36` for B, so :math:`\exp(-2.83) = 0.059` and :math:`\exp(-3.36) = 0.035`. The market shares are :math:`\theta_A = 0.059 / (0.059 + 0.035) = 0.63` and :math:`\theta_B = 0.37`. Because :math:`\beta_2` is about 15 times :math:`\beta_1`, ECM A's lower operating cost outweighs its higher installed cost, but ECM B still receives a share of the market.

**Commercial market shares** are assigned to the ECM with the lowest life cycle (capital plus operating) cost, separately for each of the AEO commercial time preference (discount rate) categories :math:`d`:

.. math::
   :label: eq-comp-com

   \theta_{X,y,m} = \sum_{d} \omega_{X,y,d}\, \frac{\mathbb{1}\left[A_{X,y,m,d} = \min_{k \in M} A_{X,y,k,d}\right]}{n_{X,y,d}}, \qquad A_{X,y,m,d} = U_{X,y,m} + \sum_{t=1}^{L_m} \frac{\psi_{X,y,m}}{(1 + d)^{t}}

where :math:`\omega_{X,y,d}` is the share of commercial adopters in category :math:`d`, :math:`L_m` is the ECM's lifetime, and :math:`n_{X,y,d}` is the number of ECMs that tie for the lowest cost (normally 1). With the ``--high_res_comp`` option, the capital cost is instead annualized over the ECM's lifetime at rate :math:`d` and added to the annual operating cost.

The shares of adopters in each category are fixed for each end use and do not vary by year, region, or building type; for heating, they are 0.263, 0.236, 0.198, 0.187, 0.097, 0.017, and 0.002 for discount rates of 1004.7%, 104.7%, 49.7%, 29.7%, 19.7%, 11.2%, and 4.7%, respectively (time preference premiums from the AEO plus a 4.7% risk-free rate). For example, if the two heat pump ECMs above, each with a 15-year lifetime, compete for a commercial heating segment, their life cycle costs are:

.. table::

   ============= ======================== ============== ============== ========
   :math:`d`     :math:`\omega_d`          ECM A ($)      ECM B ($)      Lowest
   ============= ======================== ============== ============== ========
   1004.7%       0.263                    6,070          4,600          B
   104.7%        0.236                    6,669          5,455          B
   49.7%         0.198                    7,405          6,507          B
   29.7%         0.187                    8,309          7,799          B
   19.7%         0.097                    9,314          9,234          B
   11.2%         0.017                    10,979         11,612         A
   4.7%          0.002                    13,415         15,093         A
   ============= ======================== ============== ============== ========

ECM B has the lowest cost for the five highest discount rates, so :math:`\theta_B = 0.263 + 0.236 + 0.198 + 0.187 + 0.097 = 0.981` and :math:`\theta_A = 0.017 + 0.002 = 0.019`. Most commercial adopters discount future savings heavily, so the same ECM A that captures 63% of the residential market captures only 2% of the commercial market.

In both sectors, an ECM that is not on the market in year :math:`y` has a market share of zero. Where some competing ECMs apply to only part of the segment (because of market scaling fractions or state appliance regulations), the remaining part is divided among the other competing ECMs in proportion to their market shares.

**Market share of captured stock.** The market share :math:`\theta_{X,y,m}` applies to the stock competed in year :math:`y`. The ECM's share of all stock captured through year :math:`y` is the stock-weighted average of its market shares across the years:

.. math::
   :label: eq-comp-adj

   a_{X,y,m} =
   \begin{cases}
   \theta_{X,y,m}, & y = y_0 \text{ or technical potential}\\[1ex]
   c_{X,y}\, \theta_{X,y,m} + \left(1 - c_{X,y}\right) a_{X,y-1,m}, & \text{otherwise}
   \end{cases}

where :math:`y_0` is the earliest market entry year across the competing ECMs and :math:`c_{X,y}` is the competed fraction of the segment's stock (:eq:`eq-competed-fraction`). The ECM's uncompeted baseline and efficient stock, energy use, |CO2| emissions, and costs in the segment (:eq:`eq-baseline` to :eq:`eq-efficient-carbon`) are then multiplied by :math:`a_{X,y,m}`, and its competed portion by :math:`\theta_{X,y,m}`. For an ECM that enters the market after :math:`y_0`, its captured stock and relative performance are further adjusted to exclude the stock competed before its market entry.

**Heating and cooling equipment and envelope overlaps.** After competition, ECMs that affect heating and cooling energy from the supply side (equipment) and the demand side (envelope) are adjusted to remove their overlap. For each heating or cooling segment of ECM :math:`m`, with region, building type and vintage, fuel type, and end use :math:`G`:

.. math::
   :label: eq-htcl-base

   E'_{X,y,m} = E_{X,y,m} \left[(1 - f_{G,y}) + f_{G,y}\, \rho_{G,y}\right]

.. math::
   :label: eq-htcl-eff

   E'^{\,eff}_{X,y,m} = E^{eff}_{X,y,m} \left[(1 - f_{G,y}) + f_{G,y}\, \rho_{G,y}\left(1 - \Delta^{oth}_{G,y}\right)\right], \qquad \rho_{G,y} = \frac{\Delta^{own}_{G,y}}{\Delta^{own}_{G,y} + \Delta^{oth}_{G,y}}

where :math:`f_{G,y}` is the fraction of the total heating or cooling energy use in :math:`G` that is affected by ECMs on the other side (demand side for an equipment ECM, and vice versa), :math:`\Delta^{own}_{G,y}` and :math:`\Delta^{oth}_{G,y}` are the total savings of the ECMs on the ECM's own side and on the other side as fractions of the energy use they affect in :math:`G`, and :math:`\rho_{G,y}` (0.5 if both are zero) assigns the overlapping energy use in proportion to those savings. |CO2| emissions and costs are adjusted by the same factors. This adjustment applies to individual ECMs in the analysis; HVAC equipment and envelope ECMs combined in a package are instead handled as in :eq:`eq-pkg-htcl`.

For example, if an HVAC equipment ECM saves 40% and an envelope ECM saves 20% of the same 100 units of heating energy use (:math:`f_{G,y} = 1`), the equipment ECM is assigned :math:`\rho = 0.4/(0.4 + 0.2) = 2/3` of the overlapping energy use and the envelope ECM :math:`1/3`. The equipment ECM's baseline is :math:`100 \times 2/3 = 66.7` units and its efficient energy use is :math:`60 \times 2/3 \times (1 - 0.2) = 32` units, saving 34.7 units; the envelope ECM's baseline is 33.3 units and its efficient energy use is :math:`80 \times 1/3 \times (1 - 0.4) = 16` units, saving 17.3 units. Together they save 52 units, the same as the package in :eq:`eq-pkg-htcl`, but the savings are reported separately for each ECM. If the envelope ECM affected only half of the heating energy use (:math:`f_{G,y} = 0.5`), only that half would be split, and the rest of the equipment ECM's results would be unchanged.

.. __: https://www.eia.gov/analysis/pdfpages/m067index.php
.. __: https://www.eia.gov/analysis/pdfpages/m066index.php

ECM-specific results from the analysis of the portfolio of ECMs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Filter variables summarize an ECM's applicable region(s), building class(es), and end use(s).
* Baseline and efficient results summarize an ECM's total baseline and efficient energy use, |CO2| emissions, and operating costs, as well as the savings realized by comparing the efficient case to the baseline case. Baseline and efficient results are reported as totals for the ECM and also broken down by region, building class (residential/commercial and new/existing), and end use [#]_. Users may optionally add a breakdown by fuel type and request more detailed region, building type, and fuel type breakdowns (see the ``--split_fuel`` and ``--detail_brkout`` :ref:`ecm_prep.py options <tuts-3-cmd-opts>`).
* Financial metrics summarize an ECM's `financial metrics`_.
* If applicable, average and 5th/95th percentile values are reported for all efficient markets, savings, and financial metrics outputs to accommodate ECM input uncertainty analysis.

.. _ASHRAE 90.1-2004: https://www.ashrae.org/resources--publications/bookstore/standard-90-1-document-history
.. _ASHRAE 90.1-2010: https://www.ashrae.org/resources--publications/bookstore/standard-90-1-document-history
.. _ASHRAE 90.1-2013: https://www.ashrae.org/resources--publications/bookstore/standard-90-1-document-history
.. __: https://www.eia.gov/analysis/pdfpages/m067index.php
.. __: https://www.eia.gov/analysis/pdfpages/m066index.php
.. _real discount rate: https://en.wikipedia.org/wiki/Real_interest_rate
.. _Guidelines and Discount Rates for Benefit-Cost Analysis of Federal Programs: https://www.whitehouse.gov/wp-content/uploads/legacy_drupal_files/omb/circulars/A94/a094.pdf

.. rubric:: Footnotes

.. [#] Currently supported distributions: |supported-distributions|.
.. [#] Note that this document does not cover lighting, where varying bulb types are used, or Miscellaneous Electric Loads (MELs), which are not broken into specific technologies in the Annual Energy Outlook.
.. [#] EIA provides detailed documentation on the assumptions of the National Energy Modeling System (NEMS) it uses to project residential__ and commercial__ sector energy use out to 2050 for the AEO.
.. [#] Data derived from Table A.5 (annual, unrounded social cost of |CO2|) of the EPA 2023 report, assuming a 2% near-term discount rate.
.. [#] This is the default behavior. Users may optionally retain some of the available market portion with "business-as-usual" technology by automatically adding ECMs with typical efficiency to compete with user-defined ECMs (``--add_typ_eff``) or by applying exogenous rates of conversion to heat pumps and other electric equipment (``--exog_hp_rate_scenario``); see the :ref:`ecm_prep.py options <tuts-3-cmd-opts>`.
.. [#] We use a default `real discount rate`_ of 7%, based on the Office of Management and Budget's `Guidelines and Discount Rates for Benefit-Cost Analysis of Federal Programs`_, p. 9 ("Base-Case Analysis"). 
.. [#] End use categories for the markets and savings are not the same as the AEO end uses. The reported categories are: Heating (Equip.), Cooling (Equip.), Heating (Env.), Cooling (Env.), Ventilation, Lighting, Water Heating, Refrigeration, Cooking, Computers and Electronics, and Other. Heating and cooling are split between equipment (e.g., heat pumps, furnaces) and envelope (e.g., windows, insulation) impacts; "Other" includes drying, fans and pumps, ceiling fans, and miscellaneous electric loads.
.. .. [#] The vintages are: pre-1980, 1980-2004, `ASHRAE 90.1-2004`_, `ASHRAE 90.1-2010`_, and `ASHRAE 90.1-2013`_.
.. .. [#] A representative city is simulated for each climate zone: Houston, TX (hot humid); Baltimore, MD (mixed humid); El Paso, TX (hot dry); Albuquerque, NM (mixed dry); San Francisco, CA (marine); Chicago, IL (cold); Duluth, NM (very cold), Fairbanks, AK (sub arctic).
.. .. [#] Effectively, these adjustment factors assign value to ECMs that would not otherwise show any benefits. For example: in the absence of time-sensitive valuation, an ECM that shifted loads from peak periods of energy demand to off-peak periods of demand would not have any value in terms of energy savings, cost, or avoided |CO2|; under time-sensitive valuation, however, the ECM moves energy from a high energy price period to a low energy price period, which will be reflected as energy cost savings for the ECM.
