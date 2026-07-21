#!/usr/bin/env python3
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from scout.config import FilePaths as fp
import numpy
import math
import threading
import concurrent.futures
mpl.use("Agg")

# Lock that serialises all pyplot global-state operations (subplots / savefig /
# close).  The Agg backend is thread-safe at the C level but pyplot's Python
# wrapper maintains global figure state, so concurrent threads must take this
# lock for each figure's full create→build→save→close lifecycle.
_pyplot_lock = threading.Lock()


def nicenumber(x, round):
    exp = numpy.floor(numpy.log10(x))
    f = x / 10**exp
    if round:
        if f < 1.5:
            nf = 1.
        elif f < 3.:
            nf = 2.
        elif f < 7.:
            nf = 5.
        else:
            nf = 10.
    else:
        if f <= 1.:
            nf = 1.
        elif f <= 2.:
            nf = 2.
        elif f <= 5.:
            nf = 5.
        else:
            nf = 10.
    return nf * 10.**exp


def pretty(low, high, n):
    range = nicenumber(high - low, False)
    d = nicenumber(range / (n-1), True)
    miny = numpy.floor(low / d) * d
    maxy = numpy.ceil(high / d) * d
    return numpy.arange(miny, maxy+0.5*d, d)


def _mpl_escape(s):
    """Escape unmatched/literal dollar signs in a string for use as a matplotlib label.

    matplotlib treats '$...$' as mathtext.  A lone '$' that is not part of a
    balanced pair causes a ParseException at render time.  This helper splits
    the string on already-escaped '\\$' tokens, then in each plain segment
    escapes any '$' that forms part of an *odd* run (i.e. is not the opening
    or closing delimiter of a balanced mathtext pair '$...$').

    Strategy: scan the string character by character; toggle an in_math flag
    each time we see an unescaped '$'.  If we finish in_math=True, the last
    opening '$' was unmatched — escape it.  Any '$' seen while *not* in math
    mode that would start a valid '$.+$' pair is left alone; any other bare
    '$' is escaped.
    """
    # Split on segments that are already escaped (\$) so we never double-escape.
    # Reassemble after processing the plain segments.
    result = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s) and s[i + 1] == '$':
            # Already escaped — keep as-is
            result.append('\\$')
            i += 2
        elif s[i] == '$':
            # Look ahead: is there a closing '$' later (forming a pair)?
            closing = s.find('$', i + 1)
            if closing != -1:
                # Valid mathtext pair — keep both delimiters and the content
                result.append(s[i:closing + 1])
                i = closing + 1
            else:
                # Unmatched bare '$' — escape it
                result.append('\\$')
                i += 1
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)


def run_plot(meas_summary, a_run, handyvars, measures_objlist, regions,
             codes_bps_objlist, trim_out):
    # Set base directory
    # Set uncompeted ECM energy, carbon, and cost data
    uncompete_results = meas_summary
    # Set competed ECM energy, carbon, and cost data
    compete_results_ecms = a_run.output_ecms
    # Set competed energy, carbon, and cost data summed across all ECMs
    compete_results_agg = a_run.output_all
    # Combine aggregate and individual-level ECM results
    # Combine aggregate and individual-level ECM results
    compete_results = [compete_results_agg, compete_results_ecms]
    # Set ECM adoption scenarios
    adopt_scenarios = handyvars.adopt_schemes
    # Set ECM competition scenarios
    comp_schemes = ['uncompeted', 'competed']
    # Set full list of ECM names from results file
    meas_names_no_all = [m.name for m in measures_objlist]
    # Order the list of ECM names excluding 'All ECMs'
    meas_names_no_all = sorted(meas_names_no_all)
    # Combine the 'All ECMs' name with the ordered list of the individual
    # ECM names
    meas_names = ['All ECMs'] + meas_names_no_all
    # If codes/BPS measures are present, add them to the measure set to be plotted
    if codes_bps_objlist is not None:
        meas_names.extend([mcbps.name for mcbps in codes_bps_objlist])
    # Set years in modeling time horizon and reorganize in ascending order
    years = list(a_run.output_all[meas_names[0]]
                 ['Markets and Savings (Overall)'][adopt_scenarios[0]]
                 ['Baseline Energy Use (MMBtu)'])
    years = [int(i) for i in years]

    start_yr = 2015
    end_yr = max(years)

    # Set the years to take a 'snapshot' of certain results in;
    # if the measure set was prepared with public cost adders, set
    # this year to 2020, as these adders are reflective of current/
    # near term utility conditions from EPA data; also flag for the particular
    # type of public cost adder (low/high), if any
    if "PHC" in meas_names[1]:
        snap_yr = '2020'
        snap_yr_set = ['2020']
        if "low" in meas_names[1]:
            phc_flag = 'low'
        else:
            phc_flag = 'high'
    else:
        snap_yr = '2050'
        snap_yr_set = ['2030', '2050']
        phc_flag = False

    # Filter and order the year range
    years = sorted([yr for yr in years if (yr >= start_yr & yr <= end_yr)])

    # Set region legend names
    czones_out = list(handyvars.out_break_czones.keys())

    # Use region information to create flags for certain graphical settings
    # to be used later on in plotting
    if regions == "AIA":
        # Set alternate region flags
        emm_flag = False
        emm_det_flag = False
        state_flag = False
        state_det_flag = False
    elif regions == "EMM":
        # Set region legend names
        if compete_results_agg["Output Resolution"] == "detail" or \
                "reg" in compete_results_agg["Output Resolution"]:
            emm_det_flag = True
        else:
            emm_det_flag = False
        # Set alternate region flags
        emm_flag = True
        state_flag = False
        state_det_flag = False
    elif regions == "State":
        # Set alternate region flags
        emm_flag = False
        emm_det_flag = False
        state_flag = True
        state_det_flag = True
    else:
        raise ValueError("Unexpected regional setting '" + regions + "'")

    # Set region legend colors; use special handling of the colorpalette
    # to handle region sets that are possibly longer than 20 entries
    clr = plt.get_cmap("tab20").colors
    cmc = mpl.colors.LinearSegmentedColormap.from_list(
        'tab20_c', clr, len(czones_out))
    czones_out_col = [
        mpl.colors.rgb2hex(cmc(i)) for i in range(cmc.N)]

    # Set list of possible building classes and associated colors for aggregate
    # savings plot
    bclasses_out_agg = list(handyvars.out_break_bldgtypes.keys())
    # Set list of possible building classes and associated colors for cost
    # effectiveness plot
    if compete_results_agg["Output Resolution"] == "detail" or \
            "bldg" in compete_results_agg["Output Resolution"]:
        bclasses_out_finmets = [
            ['Single Family Homes (New)', 'Multi Family Homes (New)',
             'Manufactured Homes (New)', 'Single Family Homes (Existing)',
             'Multi Family Homes (Existing)', 'Manufactured Homes (Existing)',
             'Hospitals (Existing)'],
            ['Hospitals (New)',
             'Large Offices (New)', 'Small/Medium Offices (New)',
             'Retail (New)', 'Hospitality (New)', 'Education (New)'
             'Assembly/Other (New)', 'Warehouses (New)',
             'Large Offices (Existing)', 'Small/Medium Offices (Existing)',
             'Retail (Existing)', 'Hospitality (Existing)',
             'Education (Existing)', 'Assembly/Other (Existing)',
             'Warehouses (Existing)']]
    elif "codesbps" in compete_results_agg["Output Resolution"]:
        bclasses_out_finmets = [
            'Single Family/Manufactured Homes (New)',
            'Single Family/Manufactured Homes (Existing)',
            'Multi Family Homes (New)',
            'Multi Family Homes (Existing)',
            'Commercial (New)', 'Commercial (Existing)']
    else:
        bclasses_out_finmets = [
            ['Residential (New)', 'Residential (Existing)'],
            ['Commercial (New)', 'Commercial (Existing)']]

    # Set list of possible fuel types for data aggregation
    ftypes_out = list(handyvars.out_break_fuels.keys())

    cmb = plt.get_cmap("tab20", len(bclasses_out_agg))
    bclasses_out_agg_col = [
        mpl.colors.rgb2hex(cmb(i)) for i in range(cmb.N)]
    # Set list of possible building classes and associated shapes/legend
    # entries for cost effectiveness plot

    bclasses_out_finmets_shp = ["o", "s"]  # circle, square
    bclasses_out_finmets_lgnd = ['Residential', 'Commercial']
    # Set list of possible end uses and associated colors/legend entries for
    # aggregate savings plot
    euses_out_agg = list(handyvars.out_break_enduses.keys())
    cme = plt.get_cmap("tab20", len(euses_out_agg))
    euses_out_agg_col = [
        mpl.colors.rgb2hex(cme(i)) for i in range(cme.N)]

    # Set list of possible end use names from the raw data and associated
    # colors/legend entries for cost effectiveness plot
    euses_out_finmets = [['Heating (Equip.)', 'Cooling (Equip.)',
                          'Ventilation'],
                         ['Heating (Env.)', 'Cooling (Env.)'],
                         ['Lighting'],
                         ['Water Heating'], ['Refrigeration'], ['Cooking'],
                         ['Computers and Electronics'], ['Other']]
    cmef = plt.get_cmap("tab20", len(euses_out_finmets))
    euses_out_finmets_col = [
        mpl.colors.rgb2hex(cmef(i)) for i in range(cmef.N)]
    euses_out_finmets_lgnd = ['HVAC', 'Envelope', 'Lighting', 'Water Heating',
                              'Refrigeration', 'Cooking', 'Electronics',
                              'Other']

    # Determine axis label parameters to use across plots

    # Determine site vs. source energy and (if source) captured vs. fossil
    # site-source conversion calculation methods, to write to label
    if compete_results_agg['Energy Output Type'][0] == "site":
        e_site_source = "Site Energy"
        ss_calc = ""
    elif compete_results_agg['Energy Output Type'][0] == "captured":
        e_site_source = "Primary Energy"
        ss_calc = ", CE S-S"
    else:
        e_site_source = "Primary Energy"
        ss_calc = ", FF S-S"

    # Case without TSV metrics - set conversion factors, units, and
    # axis scaling factors for aggregate savings plots
    if compete_results_agg['Energy Output Type'][1] == 'NA':
        # If results are EMM-resolved and public health cost adders
        # are not present, convert quads to TWh for reporting;
        # if results are state-resolved, used TBtu for reporting
        if emm_flag is True and phc_flag is False:
            e_conv_emm_st = 293.07
            e_axis_units = "TWh"
        elif state_flag is True:
            e_conv_emm_st = 1000
            e_axis_units = "TBtu"
        else:
            e_conv_emm_st = 1
            e_axis_units = "Quads"

        # No further conversions needed for CO2 or cost
        c_conv_emm = 1
        c_axis_units = "Mt"
        cs_conv_emm = 1
        cs_axis_units = "Billion $"
        # No further TSV metric assumptions text to append
        append_txt = ")"
        # Case with TSV metrics - set conversion factors, units, scaling
        # factors for aggregate savings plots, and text to append to axis label
        # indicating TSV metric assumptions
    else:
        # When TSV metrics are present, assume that GW (hourly savings,
        # abbreviated in the output as "Hr.") or GWh (multi-hour savings,
        # abbreviated in the output as "Prd.") is the correct energy unit
        # to use (savings will generally be smaller)
        e_conv_emm_st = 293071.07
        if compete_results_agg['Energy Output Type'][0] == "Prd.":
            e_axis_units = "GWh"
        else:
            e_axis_units = "GW"
        # When TSV metrics are present, convert million metric tons to thousand
        # metric tons and billion $ to million $ (savings will generally
        # be smaller)
        c_conv_emm = 1000
        c_axis_units = "Tt"
        cs_conv_emm = 1000
        cs_axis_units = "Million $"
        # Set text to append to axis label indicating key elements of the TSV
        # metrics assumptions
        append_txt = ", " +\
            compete_results_agg['Energy Output Type'][1] + " " +\
            compete_results_agg['Energy Output Type'][2] + " " +\
            compete_results_agg['Energy Output Type'][3] + " " +\
            compete_results_agg['Energy Output Type'][4] + ")"

    # ==========================================================================
    # Set high-level variables needed to generate individual ECM plots
    # ==========================================================================

    # Set names of plot files and axes
    # Plot of individual ECM energy, carbon, and cost totals
    file_names_ecms = ['Total Energy', 'Total CO2', 'Total Cost']
    # plot_names_ecms = ['Total Energy', 'Total CO2', 'Total Cost']
    # Set individual ECM plot y axis labels
    plot_axis_labels_ecm = [e_site_source + ' (' +
                            e_axis_units + ss_calc + append_txt,
                            r'CO$_2$ Emissions (' + c_axis_units + append_txt,
                            'Energy Cost (' + cs_axis_units + append_txt]
    # Set colors for uncompeted baseline, efficient and low/high results
    plot_col_uc_base = "#999999"
    plot_col_uc_eff = "#cccccc"
    # plot_col_uc_lowhigh = "#e5e5e5"

    # Set variable names to use in accessing all uncompeted energy, carbon,
    # and cost results from JSON data
    var_names_uncompete = ['energy', 'carbon', 'cost']
    results_folder_names = ['energy', 'co2', 'cost']
    tech_potential_dir = fp.PLOTS / "tech_potential"
    max_adopt_potential_dir = fp.PLOTS / "max_adopt_potential"
    for folder in results_folder_names:
        (max_adopt_potential_dir / folder).mkdir(parents=True, exist_ok=True)
        (tech_potential_dir / folder).mkdir(parents=True, exist_ok=True)

    # Set output units for each variable type
    var_units = [e_axis_units, c_axis_units, cs_axis_units]
    # Set variable names to use in accessing competed baseline energy, carbon,
    # and cost results from JSON data. Note that each variable potentially has
    # a '(low)' and '(high)' variant in the JSON.
    var_names_compete_base_m = ['Baseline Energy Use (MMBtu)',
                                'Baseline CO\u2082 Emissions (MMTons)',
                                'Baseline Energy Cost (USD)']
    var_names_compete_base_l = ['Baseline Energy Use (low) (MMBtu)',
                                'Baseline CO\u2082 Emissions (low) (MMTons)',
                                'Baseline Energy Cost (low) (USD)']
    var_names_compete_base_h = ['Baseline Energy Use (high) (MMBtu)',
                                'Baseline CO\u2082 Emissions (high) (MMTons)',
                                'Baseline Energy Cost (high) (USD)']
    # Set variable names to use in accessing competed efficient energy, carbon,
    # and cost results from JSON data. Note that each variable potentially has
    # a '(low)' and '(high)' variant in the JSON.
    var_names_compete_eff_m = ['Efficient Energy Use (MMBtu)',
                               'Efficient CO\u2082 Emissions (MMTons)',
                               'Efficient Energy Cost (USD)']
    var_names_compete_eff_l = ['Efficient Energy Use (low) (MMBtu)',
                               'Efficient CO\u2082 Emissions (low) (MMTons)',
                               'Efficient Energy Cost (low) (USD)']
    var_names_compete_eff_h = ['Efficient Energy Use (high) (MMBtu)',
                               'Efficient CO\u2082 Emissions (high) (MMTons)',
                               'Efficient Energy Cost (high) (USD)']

    # =========================================================================
    # Set high-level variables needed to generate aggregated savings plots
    # =========================================================================

    # File names for aggregated ECM savings plots
    plot_names_agg = ['Total Energy Savings', 'Total Avoided CO2',
                      'Total Cost Savings']
    # Titles for aggregated ECM savings plots
    plot_titles_agg = ['Energy Savings', r'Avoided CO$_2$', 'Cost Savings']
    # Set aggregate annual/cumulative savings plot y axis labels
    plot_axis_labels_agg_ann = \
        ['Annual ' + e_site_source + ' Savings (' + e_axis_units + ss_calc +
         append_txt, r'Annual Avoided CO$_2$ Emissions (' +
         c_axis_units + append_txt, 'Annual Energy Cost Savings (' +
         cs_axis_units + append_txt]
    plot_axis_labels_agg_cum = \
        ['Cumulative ' + e_site_source + ' Savings (' + e_axis_units +
         ss_calc + append_txt, r'Cumulative Avoided CO$_2$ Emissions (' +
         c_axis_units + append_txt, 'Cumulative Energy Cost Savings (' +
         cs_axis_units + append_txt]
    # Set names of variables used to retrieve savings data to aggregate
    var_names_compete_save = \
        ['Energy Savings (MMBtu)', 'Avoided CO\u2082 Emissions (MMTons)',
         'Energy Cost Savings (USD)']
    # Set names of variables to filter aggregated savings
    filter_var = ['Climate Zone', 'Building Class', 'End Use']

    # =========================================================================
    # Set high-level variables needed to generate ECM cost effectiveness plots
    # =========================================================================

    # Names for ECM cost effectiveness plots
    plot_names_finmets = ['Cost Effective Energy Savings',
                          'Cost Effective Avoided CO2',
                          'Cost Effective Operation Cost Savings']
    # X axis labels for cost effectiveness plots
    plot_axis_labels_finmets_x = \
        [snap_yr + " " + e_site_source + ' Savings (Competed, ' +
         e_axis_units + ss_calc + append_txt, snap_yr +
         r' Avoided CO$_2$ Emissions (Competed, ' +
         c_axis_units + append_txt, snap_yr +
         ' Energy Cost Savings (Competed, ' +
         cs_axis_units + append_txt]
    # Y axis labels for cost effectiveness plots
    plot_axis_labels_finmets_y = \
        ["IRR (%)", "Payback (years)", r"CCE (\$/MMBtu saved)",
         r"CCC (\$/t CO$_2$ avoided)"]
    # Financial metric titles
    plot_title_labels_finmets = \
        ["Internal Rate of Return (IRR)", "Simple Payback",
         "Cost of Conserved Energy (CCE)", r"Cost of Conserved CO$_2$ (CCC)"]
    # Default plot limits for each financial metric
    plot_lims_finmets = [[-50, 150], [0, 25], [-50, 150], [-500, 1000]]
    # Cost effectiveness threshold lines for each financial metric
    plot_ablines_finmets = [0, 10, 13, 100]
    # Financial metric type and key names for retrieving JSON data on each;
    # handle case where outputs are trimmed, and only payback is reported
    if not trim_out:
        fin_metrics = ['IRR (%)', 'Payback (years)',
                       'Cost of Conserved Energy ($/MMBtu saved)',
                       'Cost of Conserved CO\u2082 ($/MTon CO\u2082 avoided)']
    else:
        fin_metrics = ['Payback (years)']

    # =========================================================================
    # Set high-level variables needed to generate XLSX data
    # =========================================================================
    # Define cost-effectiveness metrics column names
    xlsx_names_finmets = ["IRR (%)," + snap_yr, "Payback (years)," +
                          snap_yr, "CCE ($/MMBtu saved)," +
                          snap_yr, "CCC ($/tCO2 avoided)," + snap_yr]

    # Loop through all adoption scenarios.
    # The two scenarios are independent (different output dirs, colors, XLSX
    # files) so we run them concurrently.  plt.subplots() calls are serialised
    # with _pyplot_lock to avoid races on pyplot's figure registry; all other
    # matplotlib operations use the object-level API (fig.savefig, etc.) so
    # they never touch pyplot global state and need no lock.
    def _plot_one_scenario(a):
        # a = 1 # Max adoption potential
        # Set plot colors for competed baseline, efficient, and low/high
        # results (varies by adoption scenario); also set Excel summary data
        # file name for adoption scenario
        if adopt_scenarios[a] == "Technical potential":
            # Set plot colors
            plot_col_c_base = "#191970"
            plot_col_c_eff = "#87cefa"
            # Set Excel summary data file name
            xlsx_file_name = tech_potential_dir / "Summary_Data-TP.xlsx"
        else:
            # Set plot colors
            plot_col_c_base = "#cd0000"
            plot_col_c_eff = "#ffc0cb"
            # Set Excel summary data file name
            xlsx_file_name = max_adopt_potential_dir / "Summary_Data-MAP.xlsx"
        # Preallocate list for variable names to be used later to export data
        # to xlsx-formatted Excel files
        xlsx_var_name_list = list()

        # Loop through all plotting variables
        for v in range(len(var_names_uncompete)):
            # Finalize column names for the annual total energy, carbon,
            # or cost results that are written to the XLSX file
            # Append variable units to each year name
            xlsx_names_years = [str(yr) + ' (' + var_units[v] +
                                ')' for yr in years]

            # Define all column names for XLSX file
            col_names_xlsx = ['ECM Name', 'Results Scenario', 'Climate Zones',
                              'Building Classes', 'End Uses']
            col_names_xlsx.extend(xlsx_names_finmets)
            col_names_xlsx.extend(xlsx_names_years)

            # Initialize data frame to write to Excel worksheet
            # (note: number of rows accounts for 3 rows at the top that sum
            # competed baseline/efficient results and savings across all ECMs,
            # breakouts of savings for each of the regions (depends on
            # simulation settings), bldg. types (depends on simulation
            # settings), and end uses (11), and competed and uncompeted
            # baseline/efficient results for each ECM
            xlsx_data = pd.DataFrame(columns=col_names_xlsx,
                                     index=range(3 + len(czones_out) +
                                                 len(bclasses_out_agg) + 11 +
                                                 len(meas_names) * 4))

            # Set a factor to convert the results data to final plotting units
            # for given variable (quads for energy, Mt for CO2,
            # and billion $ for cost)
            if ((var_names_uncompete[v] == "energy") or
                    (var_names_uncompete[v] == "cost")):
                # converts energy from MBtu -> quads or cost from $ -> billion$
                unit_translate = 1/1000000000
                # Layer on a second conversion factor to handle cases where
                # alternate EMM regions are used (energy goes to TWh and/or TSV
                # metrics are used (energy goes to GW/GWh, cost goes
                # to million $))
                if var_names_uncompete[v] == "energy":
                    unit_translate = unit_translate * e_conv_emm_st
                elif var_names_uncompete[v] == "cost":
                    unit_translate = unit_translate * cs_conv_emm
            else:
                # CO2 results data are already imported in Mt units
                unit_translate = 1
                # Layer on a second conversion factor to handle cases where
                # TSV metrics are used (carbon goes to thousand metric tons)
                unit_translate = unit_translate * c_conv_emm

            # Initialize a matrix for storing individual ECM energy, carbon,
            # or cost totals (3 rows accommodate mean, low,
            # and high totals values; 4 columns accommodate 2 outputs
            # (baseline and efficient) x 2 adoption scenarios)

            results = numpy.empty((3, len(comp_schemes) * 2), dtype=object)

            # Initialize a matrix for storing aggregated ECM savings results
            # (3 rows accommodate 3 filtering variables (climate zone,
            # building class, end use); 3 columns accommodate the possible name
            # categories for each filtering variable, the aggregated
            # savings data associated with each of those categories,
            # and the colors associated with those categories

            # Initialize climate zone names, annual by-climate aggregated
            # savings data, and line colors
            # Initialize building class names, annual by-building aggregated
            # savings data and line colors
            # Initialize end use names, annual by-end use aggregated savings
            # data and line colors
            results_agg = numpy.empty((3, 3), dtype=object)
            results_agg[0, 0:3] = [czones_out, [[0] * len(years)
                                   for _ in range(len(czones_out))],
                                   czones_out_col]
            results_agg[1, 0:3] = [bclasses_out_agg, [[0] * len(years)
                                   for _ in range(len(bclasses_out_agg))],
                                   bclasses_out_agg_col]
            results_agg[2, 0:3] = [euses_out_agg, [[0] * len(years)
                                   for _ in range(len(euses_out_agg))],
                                   euses_out_agg_col]

            # Initialize a matrix for storing individual ECM financial metrics/
            # savings and filter variable data
            # meas_names is missing 'On-site Generation'
            results_finmets = \
                numpy.empty((len(meas_names_no_all), len(fin_metrics) + 4),
                            dtype=object)

            # Initialize uncertainty flag for the adoption scenario
            uncertainty = False
            # Set the file name for the plot based on the adoption scenario
            # and plotting variable
            if adopt_scenarios[a] == 'Technical potential':
                plot_dir = tech_potential_dir / results_folder_names[v]
                # ECM energy, carbon, and cost totals
                plot_file_name_ecms = plot_dir / f"{file_names_ecms[v]}-TP"
                # Aggregate energy, carbon, and cost savings
                plot_file_name_agg = plot_dir / f"{plot_names_agg[v]}-TP"
                # ECM cost effectiveness
                plot_file_name_finmets = plot_dir / f"{plot_names_finmets[v]}-TP.pdf"
            else:
                plot_dir = max_adopt_potential_dir / results_folder_names[v]
                # ECM energy, carbon, and cost totals
                plot_file_name_ecms = plot_dir / f"{file_names_ecms[v]}-MAP"
                # Aggregate energy, carbon, and cost savings
                plot_file_name_agg = plot_dir / f"{plot_names_agg[v]}-MAP"
                # ECM cost effectiveness
                plot_file_name_finmets = plot_dir / f"{plot_names_finmets[v]}-MAP.pdf"

            # Determine number of rows for individual ECM plots
            row = math.ceil(len(meas_names) / 4)
            # Initialize individual ECM plots
            with _pyplot_lock:
                fig, axas = plt.subplots(row, 4, figsize=(20, row * 4.5))

            # Remove plots for any unused cells in the plotting matrix
            # Find number of blank plots in last row
            blnks = (row * 4 - len(meas_names))
            for spi in range(blnks):
                # Work backwards to remove plots
                rmv_ind = -1 * (spi + 1)
                if row > 1:
                    axas[-1, rmv_ind].axis('off')
                else:
                    axas[rmv_ind].axis('off')

            # Loop through all ECMs
            # for m in range(len(meas_names)):  # 0..66 the R version 1..66
            for (axa, m) in zip(fig.axes, range(len(meas_names))):
                axa.set_axis_off()
                # Add ECM name to Excel worksheet data frame
                # Set appropriate starting row for the ECM's data
                if meas_names[m] == "All ECMs":
                    # For the 'All ECMs' data, start at the beginning
                    # of the file
                    row_ind_start = 0
                else:
                    # Otherwise, leave the first 5 rows for 4 competed 'All
                    # ECMs' baseline/efficient results rows and one row for
                    # competed savings, another set of rows for breakouts of
                    # savings across all ECMs, broken out by region (#
                    # dependent on region settings and level of detail in
                    # outputs), building type (# dependent on level
                    # of detail in outputs), and end use (11 rows), and finally
                    # 4 rows each for baseline/efficient competed/uncompeted
                    # results per measure that preceded the current one (
                    # excluding the 'All ECMs' measure which is already
                    # accounted for via the above rows)
                    row_ind_start = (
                        5 + len(czones_out) + len(bclasses_out_agg) + 11 +
                        (m - 1) * 4)
                # Add measure name to Excel sheet
                xlsx_data.iloc[row_ind_start:(row_ind_start + 4), 0] = \
                    meas_names[m]

                # Set applicable climate zones, end uses, and building classes
                # for ECM and add to Excel worksheet data frame
                if meas_names[m] == "All ECMs":
                    czones = ''
                    bldg_types = ''
                    end_uses = ''
                else:
                    czones = ', '.join([str(elem) for elem in (
                        compete_results[1][meas_names[m]][
                            'Filter Variables']['Applicable Regions'])])
                    bldg_types = ', '.join([str(elem) for elem in (
                        compete_results[1][meas_names[m]][
                            'Filter Variables'][
                            'Applicable Building Classes'])])
                    end_uses = ', '.join([str(elem) for elem in (
                        compete_results[1][meas_names[m]][
                            'Filter Variables']['Applicable End Uses'])])

                xlsx_data.iloc[row_ind_start:(row_ind_start + 4), 2] = czones
                xlsx_data.iloc[row_ind_start:(row_ind_start + 4), 3] = \
                    bldg_types
                xlsx_data.iloc[row_ind_start:(row_ind_start + 4), 4] = end_uses

                # If there are more than three end use names, set a single
                # end use name of 'Multiple' such that the end use name label
                # will fit easily within each plot region
                if end_uses.count(',') > 1:
                    end_uses = "Multiple"
                # Find the index for accessing the item in the list of
                # uncompeted results that corresponds to energy, carbon,
                # or cost total data for the current ECM.
                # Note: competed energy, carbon, and
                # cost totals are accessed directly by ECM name,
                # and do not require an index
                for uc in range(len(uncompete_results)):
                    if uncompete_results[uc]['name'] == meas_names[m]:
                        uc_name_ind = uc

                # Set the appropriate database of ECM financial metrics data
                # (used across both competition schemes for individual measures;
                # not relevant to aggregated data across all ECMs or to codes/BPS
                # measure data
                if meas_names[m] == "All ECMs" or any([
                        x in meas_names[m] for x in ["Codes", "Standards"]]):
                    results_database_finmets = numpy.nan
                else:
                    results_database_finmets = compete_results[1][
                        meas_names[m]]['Financial Metrics']

                # Loop through all competition schemes
                for cp in range(len(comp_schemes)):
                    # Add name of results scenario (baseline/efficient +
                    # competed/uncompeted) to Excel worksheet data frame
                    xlsx_data.iloc[
                        (row_ind_start + (cp)*2):
                        (row_ind_start + (cp)*2 + 2), 1] = [
                            "Baseline " + comp_schemes[cp],
                            "Efficient " + comp_schemes[cp]]
                    # xlsx_data.iloc[(row_ind_start + cp + 2), 1] = \
                    #     "Efficient " + comp_schemes[cp]
                    # Set matrix for temporarily storing finalized baseline
                    # and efficient results
                    r_temp = numpy.empty((6, len(years)), dtype=object)
                    # Find data for uncompeted energy, carbon, and/or cost;
                    # exclude the 'All ECMs' case
                    # (only competed data may be summed across all ECMs)
                    # and the codes/BPS measures, which do not have uncompeted data
                    if comp_schemes[cp] == "uncompeted" and (
                       meas_names[m] != "All ECMs" and not any([
                            x in meas_names[m] for x in ["Codes", "Standards"]])):
                        # Set the appropriate database of uncompeted energy,
                        # carbon, or cost totals (access keys vary based on
                        # plotted variable)
                        if var_names_uncompete[v] != "cost":
                            results_database = uncompete_results[uc_name_ind][
                                'markets'][adopt_scenarios[a]]['uncompeted'][
                                'master_mseg'][var_names_uncompete[v]]['total']
                        else:
                            results_database = uncompete_results[uc_name_ind][
                                'markets'][adopt_scenarios[a]]['uncompeted'][
                                'master_mseg'][var_names_uncompete[v]][
                                'energy']['total']
                        # Order the uncompeted ECM energy, carbon, or cost
                        # totals by year and determine low/high
                        # bounds on each total value (if applicable)
                        for yr in range(len(years)):
                            r_temp[0:3, yr] = results_database['baseline'][
                                              str(years[yr])]
                            # Set mean, low, and high values for case with
                            # ECM input/output uncertainty
                            if len([results_database['efficient'][
                                    str(years[0])]]) > 1:
                                # Take mean of list of values from uncompeted
                                # results
                                r_temp[3, yr] = numpy.mean(results_database[
                                    'efficient'][str(years[yr])])
                                # Take 5th/95th percentiles of list of values
                                # from uncompeted results
                                r_temp[4:6, yr] = numpy.quantile(
                                    results_database['efficient'][
                                        str(years[yr])], [0.05, 0.95])
                                uncertainty = True
                                # Set mean, low, and high values for case
                                # without ECM input/output uncertainty
                                # (all values equal to mean value)
                            else:
                                r_temp[3:6, yr] = results_database[
                                    'efficient'][str(years[yr])]

                    # Find data for competed energy, carbon, and/or cost
                    elif comp_schemes[cp] == "competed":
                        # Set the appropriate database of ECM competed energy,
                        # carbon, or cost totals
                        if meas_names[m] == "All ECMs":
                            results_database = compete_results[0][
                                meas_names[m]][
                                    'Markets and Savings (Overall)'][
                                    adopt_scenarios[a]]
                        else:
                            results_database = compete_results[1][
                                meas_names[m]][
                                    'Markets and Savings (Overall)'][
                                    adopt_scenarios[a]]
                        # Set the appropriate database of ECM competed energy,
                        # carbon, or cost totals broken down by climate zone,
                        # building class, and end use; exclude the 'All ECMs'
                        # case (breakdowns are not calculated for this case)
                        if meas_names[m] != "All ECMs":
                            # Set the appropriate database of ECM competed
                            # energy, carbon , or cost savings, which are
                            # broken out by each of the three filtering
                            # variables (climate zone, building class, end use)
                            results_database_agg = compete_results[1][
                                meas_names[m]][
                                'Markets and Savings (by Category)'][
                                adopt_scenarios[a]][var_names_compete_save[v]]
                            # Set the appropriate database of ECM data for
                            # categorizing cost effectiveness outcomes
                            # based on climate zone, building type, and end use
                            results_database_filters = compete_results[1][
                                meas_names[m]]['Filter Variables']

                        # Order competed ECM energy, carbon, or cost totals by
                        # year and determine low/high bounds
                        # on each total value (if applicable).
                        # Hoist the uncertainty-flag checks out of the year
                        # loop: results_database.keys() is constant across
                        # years, so computing column_stack once is sufficient.
                        _rdb_keys = list(results_database.keys())
                        base_uncertain_check = numpy.column_stack(
                            ([any(b in s for b in ['Baseline']) for s in _rdb_keys],
                             [any(b in s for b in ['low']) for s in _rdb_keys]))
                        eff_uncertain_check = numpy.column_stack(
                            ([any(b in s for b in ['Efficient']) for s in _rdb_keys],
                             [any(b in s for b in ['low']) for s in _rdb_keys]))
                        _base_has_uncertainty = (numpy.array(numpy.where(
                            base_uncertain_check[:, 0] &
                            base_uncertain_check[:, 1] is True)).size) > 0
                        _eff_has_uncertainty = (numpy.array(numpy.where(
                            eff_uncertain_check[:, 0] &
                            eff_uncertain_check[:, 1:2] is True)).size) > 0
                        for yr in range(len(years)):
                            if _base_has_uncertainty:
                                # Take mean value output directly from competed
                                # results
                                r_temp[1, yr] = results_database[
                                    var_names_compete_base_m[v]][str(
                                        years[yr])]
                                # Take 'low' value output directly from
                                # competed results (represents 5th percentile)
                                r_temp[2, yr] = results_database[
                                    var_names_compete_base_l[v]][str(
                                        years[yr])]
                                # Take 'high' value output directly from
                                # competed results (represents 5th percentile)
                                r_temp[3, yr] = results_database[
                                    var_names_compete_base_h[v]][str(
                                        years[yr])]
                                # Flag output uncertainty in the current plot
                                uncertainty = True
                                # Set mean, low, and high values for case
                                # without ECM input/output uncertainty
                                # (all values equal to mean value)
                            else:
                                # Take 'low' value output directly from
                                # competed results (represents 5th percentile)
                                r_temp[0:3, yr] = results_database[
                                    var_names_compete_base_m[v]][str(
                                        years[yr])]

                            # Set mean, low, and high values for case with ECM
                            # input/output uncertainty
                            if _eff_has_uncertainty:
                                # Take mean value output directly from competed
                                # results
                                r_temp[4, yr] = results_database[
                                    var_names_compete_eff_m[v]][str(
                                        years[yr])]
                                # Take 'low' value output directly from
                                # competed results (represents 5th percentile)
                                r_temp[5, yr] = results_database[
                                    var_names_compete_eff_l[v]][str(
                                        years[yr])]
                                # Take 'high' value output directly from
                                # competed results (represents 95th percentile)
                                r_temp[6, yr] = results_database[
                                    var_names_compete_eff_h[v]][str(
                                        years[yr])]
                                # Flag output uncertainty in the current plot
                                uncertainty = True
                                # Set mean, low, and high values for case
                                # without ECM input/output uncertainty
                                # (all values equal to mean value)
                            else:
                                r_temp[3:6, yr] = results_database[
                                    var_names_compete_eff_m[v]][str(
                                        years[yr])]

                            # Find the amount of the ECM's energy, carbon, or
                            # cost savings that can be attributed to each of
                            # the three aggregate savings filtering variables
                            # (climate zone, building class, end use) and add
                            # those savings to the aggregated total for each
                            # filter variable across all ECMs; exclude the
                            # 'All ECMs' case (filter variable breakdowns are
                            # not calculated for this case)
                            if meas_names[m] != "All ECMs":
                                # Loop through the three variables used to
                                # filter aggregated savings, each represented
                                # by a row in the 'results_agg' matrix
                                for fv in range(results_agg.shape[0]):
                                    # Set the name categories associated with
                                    # the given savings filter variable (
                                    # e.g., 'Residential (New)',
                                    # 'Residential (Existing)', etc. for
                                    # building class)
                                    fv_opts = results_agg[fv, 0]

                                    # Initialize a vector used to store the
                                    # ECM's energy, carbon, or cost savings
                                    # that are attributable to the given filter
                                    # variable; this vector must be as long as
                                    # the number of category names for the
                                    # filter variable, so a savings total can
                                    # be stored for each category
                                    add_val = numpy.zeros(len(fv_opts))

                                    # Retrieve the savings data for the ECM
                                    # that is attributable to each filter
                                    # variable name category. The data are
                                    # stored in a three-level nested dict with
                                    # climate zone at the top level, building
                                    # class at the middle level, and end use at
                                    # the bottom level. All three of these
                                    # levels must be looped through to retrieve
                                    # the savings data.

                                    # Loop through all climate zones
                                    for levone in range(len(
                                            results_agg[0, 0])):
                                        # Set the climate zone name to use in
                                        # proceeding down to the building class
                                        # level of the dict
                                        czone = results_agg[0, 0][levone]
                                        # If region is valid, reduce the
                                        # dict to the building class; otherwise
                                        # proceed to next region
                                        try:
                                            r_agg_temp = results_database_agg[czone]
                                        except KeyError:
                                            continue
                                        # Loop through all building classes
                                        for levtwo in range(len(
                                                results_agg[1, 0])):
                                            # Set the building class name to use in proceeding down
                                            # to the end use level of the dict
                                            bldg = results_agg[1, 0][levtwo]
                                            # If the region/building type are valid, reduce the
                                            # dict to the end use level; otherwise proceed to
                                            # the next building type
                                            try:
                                                r_agg_temp = results_database_agg[czone][bldg]
                                            except KeyError:
                                                continue
                                            # Loop through all end uses
                                            for levthree in range(len(
                                                    results_agg[2, 0])):
                                                # Set the end use name to use
                                                # in retrieving data values
                                                euse = results_agg[2, 0][
                                                    levthree]
                                                # Reset the predefined 'Electronics' end use name
                                                # (short for later use in plot legends) to the
                                                # longer 'Computers and Electronics' name used in
                                                # the dict
                                                if euse == "Electronics":
                                                    euse = ("Computers and Electronics")

                                                # If the region/building type/end use are valid,
                                                # reduce the dict to the final level; otherwise
                                                # proceed to the next end use
                                                try:
                                                    r_agg_temp = \
                                                        results_database_agg[czone][bldg][euse]
                                                except KeyError:
                                                    continue

                                                # If data values exist, add them to the ECM's
                                                # energy/carbon/cost savings-by-filter variable
                                                # vector initialized above

                                                if len(r_agg_temp) != 0:

                                                    # Determine which index to use in adding the
                                                    # retrieved data to the ECM's energy/carbon/
                                                    # cost savings-by-filter variable vector
                                                    if fv == 0:
                                                        index = levone
                                                    elif fv == 1:
                                                        index = levtwo
                                                    else:
                                                        index = levthree
                                                    # Add retrieved data to ECM's savings-by-filter
                                                    # variable vector; handle case where end use
                                                    # savings are further split out by fuel type

                                                    if any([str(years[yr]) in x for x in list(
                                                            r_agg_temp.keys())]):
                                                        add_val[index] = add_val[index] + \
                                                            r_agg_temp[str(years[yr])]
                                                    else:
                                                        for fuel in ftypes_out:
                                                            # Ensure fuel split data are available
                                                            if fuel in (r_agg_temp.keys()):
                                                                try:
                                                                    add_val[index] = \
                                                                        add_val[index] + \
                                                                        r_agg_temp[fuel][str(
                                                                            years[yr])]
                                                                except KeyError:
                                                                    continue

                                    # Add ECM's savings-by-filter variable
                                    # vector data to the aggregated total for
                                    # each filter variable across all ECMs
                                    for fvo in range(len(fv_opts)):
                                        results_agg[fv, 1][fvo][yr] = \
                                            results_agg[fv, 1][fvo][yr] + \
                                            add_val[fvo]

                                # If cycling through the year in which snapshots of ECM cost
                                # effectiveness are taken retrieve the ECM's competed financial
                                # metrics, savings, and filter variable data needed to develop
                                # those snapshots for the cost effectiveness plots. Exclude codes/
                                # BPS ECMs (no cost effectiveness data attached to these ECMs)
                                if str(years[yr]) == snap_yr and not any([
                                        x in meas_names[m] for x in ["Codes", "Standards"]]):
                                    # Retrieve ECM competed portfolio-level
                                    # and consumer-level financial metrics data
                                    for fm in range(len(fin_metrics)):
                                        # Multiply IRR fractions in JSON data
                                        # by 100 to convert to final % units
                                        if fin_metrics[fm] == "IRR (%)":
                                            unit_translate_finmet = 100
                                        else:
                                            unit_translate_finmet = 1

                                        # Consumer-level data are NOT keyed by
                                        # adoption scenario
                                        results_finmets[(m-1), fm] = \
                                            results_database_finmets[
                                            fin_metrics[fm]][str(years[yr])] *\
                                            unit_translate_finmet

                                        # Replace all 99900 values with 999 (
                                        # proxy for NaN)
                                        if results_finmets[(m-1), fm] == 99900:
                                            results_finmets[(m-1), fm] = 999

                                    # Write ECM cost effectiveness metrics data
                                    # to XLSX sheet
                                    xlsx_data.iloc[row_ind_start:(
                                        row_ind_start + 4), 5:(5 + len(
                                            plot_title_labels_finmets))] = \
                                        results_finmets[(m-1), 0:4]

                                    # Retrieve, ECM energy, carbon, or cost
                                    # savings data, convert to final units
                                    results_finmets[(m-1), len(fin_metrics)] =\
                                        results_database[
                                        var_names_compete_save[v]][
                                        str(years[yr])] * unit_translate

                                    # Determine the outline color, shape, and
                                    # fill color parameters needed to
                                    # distinguish ECM points on the cost
                                    # effectiveness plots by their climate
                                    # zone, building type, and end use
                                    # categories

                                    # Set ECM's applicable building type
                                    bldg = results_database_filters[
                                        'Applicable Building Classes']
                                    # Match applicable building classes to
                                    # building type names used in plotting

                                    bldg_match = numpy.empty((len(
                                        bclasses_out_finmets) * len(
                                        bclasses_out_finmets[0])),
                                        dtype=object)

                                    for b in range(len(bclasses_out_finmets)):
                                        if sum([item in bclasses_out_finmets[b]
                                                for item in bldg]) > 0:
                                            bldg_match[b] = b

                                    if pd.Series(bldg_match).nunique() >= 1:
                                        results_finmets[(m-1), (len(fin_metrics) + 2)] = "^"
                                    else:
                                        results_finmets[(m-1), (len(fin_metrics) + 2)] = \
                                            bclasses_out_finmets_shp[
                                            [x for x in list(pd.Series(
                                                bldg_match)) if x is not None][
                                                0]]

                                    # Determine appropriate ECM point fill
                                    # color for applicable end uses
                                    # Set ECM's applicable end uses
                                    euse = results_database_filters[
                                        'Applicable End Uses']
                                    # Match applicable end uses to end use
                                    # names used in plotting

                                    euse_match = numpy.empty(len(
                                        euses_out_finmets), dtype=object)

                                    for e in range(len(euses_out_finmets)):
                                        if sum([item in euses_out_finmets[e]
                                                for item in euse]) > 0:
                                            euse_match[e] = e

                                    # If more than one end use name was
                                    # matched, set the point fill color to
                                    # gray, representative of 'Multiple'
                                    # applicable end uses; otherwise set
                                    # to the point fill color appropriate for
                                    # the matched end use
                                    if pd.Series(euse_match).nunique() >= 1:
                                        results_finmets[
                                            (m-1), (len(fin_metrics) + 3)] = "#7f7f7f"
                                    else:
                                        results_finmets[
                                            (m-1), (len(fin_metrics) + 3)] = \
                                            euses_out_finmets_col[[
                                                x for x in list(
                                                    pd.Series(euse_match)
                                                ) if x is not None][0]]

                    # Set the column start and stop indexes to use in updating
                    # the matrix of ECM energy, carbon or cost totals
                    col_ind_start = ((cp)*(len(comp_schemes)))
                    col_ind_end = col_ind_start + 2
                    # Update results matrix with mean, low, and high baseline
                    # and efficient outcomes
                    results[:, col_ind_start:col_ind_end] = [
                            [list(r_temp[0, :]), list(r_temp[3, :])],
                            [list(r_temp[1, :]), list(r_temp[4, :])],
                            [list(r_temp[2, :]), list(r_temp[5, :])]]

                # Set uncompeted and competed baseline energy, carbon, or cost
                # totals for given adoption scenario, plotting variable,
                # and ECM (mean and low/high values for competed case). Handle
                # possible missing uncompeted values for codes/BPS measures,
                # which are not assessed until the competition module
                base_uc = [y * unit_translate if y else 0 for y in [
                    [] if x is numpy.NaN else x for x in [results[0, 0]]][0]]
                base_c_m = [y * unit_translate for y in [
                    [] if x is numpy.NaN else x for x in [results[0, 2]]][0]]
                base_c_l = [y * unit_translate for y in [
                    [] if x is numpy.NaN else x for x in [results[1, 2]]][0]]
                base_c_h = [y * unit_translate for y in [
                    [] if x is numpy.NaN else x for x in [results[2, 2]]][0]]
                # Set uncompeted and competed efficient energy, carbon, or cost
                # totals for adoption scenario, plotting variable, and ECM
                # (mean and low/high values).  Handle possible missing uncompeted
                # values for codes/BPS measures, which are not assessed until the
                # competition module
                eff_uc_m = [y * unit_translate if y else 0 for y in [
                    [] if x is numpy.NaN else x for x in [results[0, 1]]][0]]
                eff_uc_l = [y * unit_translate if y else 0 for y in [
                    [] if x is numpy.NaN else x for x in [results[1, 1]]][0]]
                eff_uc_h = [y * unit_translate if y else 0 for y in [
                    [] if x is numpy.NaN else x for x in [results[2, 1]]][0]]
                eff_c_m = [y * unit_translate for y in [
                    [] if x is numpy.NaN else x for x in [results[0, 3]]][0]]
                eff_c_l = [y * unit_translate for y in [
                    [] if x is numpy.NaN else x for x in [results[1, 3]]][0]]
                eff_c_h = [y * unit_translate for y in [
                    [] if x is numpy.NaN else x for x in [results[2, 3]]][0]]

                # Add annual ECM energy, carbon, or cost totals to XLSX
                # worksheet data frame
                xlsx_data.iloc[row_ind_start:(row_ind_start + 4),
                               (5 + (len(plot_title_labels_finmets))):len(
                                xlsx_data.columns)] = \
                    [base_uc, eff_uc_m, base_c_m, eff_c_m]

                # Find the min. and max. values in the ECM energy, carbon, or
                # cost totals data to be plotted
                min_val = numpy.amin(
                    [*base_uc, *base_c_m, *base_c_l, *base_c_h, *eff_uc_m,
                     *eff_uc_l, *eff_uc_h, *eff_c_m, *eff_c_l, *eff_c_h])

                max_val = numpy.amax(
                    [*base_uc, *base_c_m, *base_c_l, *base_c_h, *eff_uc_m,
                     *eff_uc_l, *eff_uc_h, *eff_c_m, *eff_c_l, *eff_c_h])

                # Determine legend parameters based on whether uncertainty is
                # present in totals
                if uncertainty is True:
                    # Set legend names for a plot with uncertainty in the
                    # ECM totals
                    legend_param = [
                        "Baseline (Uncompeted)", "Baseline (Competed)",
                        "Efficient (Uncompeted)", "Efficient (Competed)",
                        "Baseline (Competed, 5th/95th PCT)",
                        "Efficient (Uncompeted, 5th/95th PCT)",
                        "Efficient (Competed, 5th/95th PCT)"]
                else:
                    # Set legend names for a plot with no uncertainty in the
                    # ECM totals
                    legend_param = [
                         "Ref. Case (Uncompeted)",
                         "w/ Measure(s) (Uncompeted)",
                         "Ref. Case (Competed)",
                         "w/ Measure(s) (Competed)"]

                # Set limits of y axis for plot based on min. and
                # max. values in data
                try:
                    ylims = pretty(
                        min_val-0.05*max_val, max_val+0.05*max_val, 10)
                except FloatingPointError:
                    continue
                axa.set_ylim(
                    min(ylims)-(0.1*max(ylims)), max(ylims)+(0.1*max(ylims)))

                # Add low/high bounds on uncompeted and competed baseline and
                # efficient ECM energy, carbon, or cost totals, if applicable
                if uncertainty is True:
                    axa.plot(years, eff_uc_l, color=plot_col_uc_eff, lw=1)
                    axa.plot(years, eff_uc_h, color=plot_col_uc_eff, lw=1)
                    axa.plot(years, base_c_l, color=plot_col_c_base, lw=1)
                    axa.plot(years, base_c_h, color=plot_col_c_base, lw=1)
                    axa.plot(years, eff_c_l, color=plot_col_c_eff, lw=1)
                    axa.plot(years, eff_c_h, color=plot_col_c_eff, lw=1)

                # Initialize the plot with uncompeted baseline ECM energy,
                # carbon, or cost totals
                axa.plot(years, base_uc, color=plot_col_uc_base,
                         label="", lw=5)
                # Add mean uncompeted efficient ECM energy, carbon,
                # or cost totals
                axa.plot(years, eff_uc_m, color=plot_col_uc_eff, lw=3)
                # Add mean competed baseline results
                axa.plot(years, base_c_m, color=plot_col_c_base, lw=3.5)
                # Add mean competed efficient results
                axa.plot(years, eff_c_m, color=plot_col_c_eff, lw=2)

                # Add x and y axis labels
                axa.set_xlabel("Year")
                axa.set_xlim(2018, 2052)  # hardcode year range
                axa.set_ylabel(_mpl_escape(plot_axis_labels_ecm[v]))

                # Annotate total savings in a snapshot years for the 'All ECMs'
                # case; otherwise, annotate the applicable ECM end uses

                if meas_names[m] == "All ECMs":
                    # Annotate the plot with snapshot year total savings figure
                    # Find x and y values for annotation
                    for s in range(len(snap_yr_set)):
                        # Set the x value for annotation point
                        xval_snap = int(snap_yr_set[s])
                        # Set y values for annotation point
                        yval_snap_eff = eff_c_m[numpy.where(
                            numpy.array(years) == int(snap_yr_set[s]))[0][0]]
                        yval_snap_base = base_c_m[numpy.where(
                            numpy.array(years) == int(snap_yr_set[s]))[0][0]]

                        marker_style = dict(color='forestgreen',
                                            linestyle='dotted', marker='o',
                                            markersize=8, markeredgewidth=2,
                                            markerfacecoloralt='forestgreen',
                                            fillstyle='none')
                        axa.plot([xval_snap, xval_snap],
                                 [yval_snap_base, yval_snap_eff],
                                 **marker_style)
                        axa.text(x=xval_snap - xval_snap*0.002,
                                 y=yval_snap_eff - max(ylims)*0.05,
                                 s=str(round(yval_snap_base-yval_snap_eff, 1)
                                       ) + " " + _mpl_escape(var_units[v]),
                                 fontdict=dict(color="forestgreen", size=8))
                        axa.legend(labels=legend_param)
                else:
                    # Add ECM end use labels
                    label_text = 'End Uses: ' + end_uses
                    axa.text(0.02, 0.98, label_text, fontsize=10,
                             horizontalalignment='left',
                             verticalalignment='top',
                             color='#7f7f7f',
                             transform=axa.transAxes)

                # Add plot title
                axa.set_title(_mpl_escape(meas_names[m]))
                axa.set_axis_on()

            # Generate individual ECM plot figure
            with _pyplot_lock:
                fig.tight_layout()
                fig.savefig(f"{plot_file_name_ecms}-byECM.pdf", bbox_inches='tight')
                plt.close(fig)
            ###################################################################

            # Plot annual and cumulative energy, carbon, and cost savings
            # across all ECMs, filtered by climate zone, building class,
            # and end use

            # Set the first XLSX row number for writing aggregated savings
            # results; note that these results are ultimately written to the
            # 19 rows that follow the 'All ECMs' total energy, carbon, and
            # cost results written above (19 = 1 row for total savings across
            # climate zones, building types, and end uses, 5 rows for
            # savings by climate zone, 4 rows for savings by building type,
            # and 9 rows for savings by end use)
            agg_row_ind = 4

            # Loop through all three savings filter variables and add plot of
            # aggregated savings
            with _pyplot_lock:
                fig, axbs = plt.subplots(3, 1, figsize=(11, 15))
            for (axb, f) in zip(fig.axes, range(results_agg.shape[0])):
                axb.set_axis_off()
                # Initialize vector for storing total annual savings across
                # all category names for the given filter variable
                total_ann = numpy.zeros(len(years), dtype=object)
                # Initialize vector for storing ranks of annual savings for
                # each categoryfor the given filter variable
                total_ranks = numpy.zeros(len(results_agg[f, 1]), dtype=object)
                # Initialize matrix for determining min./max. y values in plot
                min_max_ann = numpy.zeros([len(results_agg[f, 1]), 2],
                                          dtype=object)

                # Loop through all categories under the filter variable and
                # add aggregate savings under that category to the total
                # aggregate savings for the given filter variable
                for cat in range(len(results_agg[f, 1])):
                    # Add annual savings for category to total annual savings
                    total_ann = total_ann + numpy.multiply(
                        numpy.array(results_agg[f, 1][cat]), unit_translate)
                    # Add final year value of annual savings for category, for
                    # ranking purposes
                    total_ranks[cat] = numpy.multiply(numpy.array(
                        results_agg[f, 1][cat]), unit_translate)[-1]
                    # Record min./max. y values for category
                    min_max_ann[cat, 0:2] = [min(numpy.multiply(
                        numpy.array(results_agg[f, 1][cat]), unit_translate)),
                            max(numpy.multiply(numpy.array(
                                results_agg[f, 1][cat]), unit_translate))]

                # Use the total annual savings data to develop total cumulative
                # savings

                # Initialize vector for storing total cumulative savings across
                # all category names
                total_cum = numpy.zeros(len(total_ann), dtype=object)
                # Loop through each year in the total annual savings data and
                # develop a total cumulative savings value for that year
                for yr in range(len(total_ann)):
                    # For first year, total cumulative savings equals total
                    # annual savings; in subsequent years, total cumulative
                    # savings equals total annual savings plus total cumulative
                    # savings for the year before
                    if yr == 0:
                        total_cum[yr] = total_ann[yr]
                    else:
                        total_cum[yr] = total_ann[yr] + total_cum[yr-1]

                # Develop x limits for the plot
                # xlim = pretty(min(years), max(years), 10)
                # Develop y limits for total annual savings
                min_val_ann = min(
                    [x[0] for x in min_max_ann] + [min(total_ann)])
                max_val_ann = max(
                    [x[1] for x in min_max_ann] + [max(total_ann)])
                # Force very small negative min. y value to zero
                if (max_val_ann > 0) and (
                        (abs(min_val_ann) / max_val_ann) < 0.01):
                    min_val_ann = 0
                # ylim_ann = pretty(min_val_ann, max_val_ann, 10)

                # Initialize plot region for total annual savings and savings
                # by filter variable category, assuming savings aren't zero
                if any([not math.isclose(x, 0, abs_tol=1e-9) for
                        x in total_cum]):
                    axb.plot(
                        years, total_ann, lw=3, color="#4d4d4d", label="")
                    buff_a = 0.05 * abs(max_val_ann - min_val_ann)
                    axb.set_xlim(2018, 2052)  # hardcode years
                    axb.set_ylim(min_val_ann-buff_a, max_val_ann+buff_a)
                    axb.set_ylabel(_mpl_escape(plot_axis_labels_agg_ann[v]))
                    axb.set_xlabel("Year")

                    # Develop y limits for total cumulative savings
                    min_val_cum = min(total_cum)
                    max_val_cum = max(total_cum)
                    # ylim_cum = pretty(min_val_cum, max_val_cum, 10)

                    # Initialize plot region for total cumulative savings
                    axb2 = axb.twinx()
                    # Add total cumulative savings line
                    axb2.plot(
                        years, total_cum, lw=3, color="#7f7f7f", ls='dotted')
                    buff_c = 0.05 * abs(max_val_cum - min_val_cum)
                    axb2.set_ylim(min_val_cum-buff_c, max_val_cum+buff_c)
                    axb2.set_ylabel(_mpl_escape(plot_axis_labels_agg_cum[v]))
                    # Add plot title; force switch 'Climate Zone' variable to
                    # 'Region'
                    if filter_var[f] != 'Climate Zone':
                        axb.set_title(plot_titles_agg[v] + ' by ' +
                                      filter_var[f])
                    else:
                        axb.set_title(plot_titles_agg[v] + ' by ' + 'Region')
                else:  # produce blank plots
                    axb.set_xlim(0, 1)
                    axb.set_ylim(0, 1)

                # Add total aggregate savings data across all climate zones,
                # building types, and end uses to the data frame that will be
                # written to the XLSX file; do so only if the first savings
                # filter variable is being looped through, as the total
                # aggregate savings values do not change across filter
                # variables
                if f == 0:
                    # Set ECM name to 'All ECMs' and results scenario to
                    # baseline minus efficient
                    xlsx_data.iloc[agg_row_ind, 0:2] = \
                        ["All ECMs", "Baseline competed - efficient competed"]
                    # When updating total aggregate savings, each filter
                    # variable cell in the XLSX is flagged 'All' (since the
                    # total values pertain to all filter variable categories)
                    xlsx_data.iloc[agg_row_ind, 2:5] = ["All", "All", "All"]
                    # Add the total aggregate savings values to the appropriate
                    # row/column range
                    xlsx_data.iloc[agg_row_ind, (5 + (len(
                        plot_title_labels_finmets))):len(
                            xlsx_data.columns)] = total_ann
                    # Increment the XLSX row to write to by one
                    agg_row_ind = agg_row_ind + 1
                    # Set the columns in the XLSX that are active/inactive for
                    # the current filter variable
                    col_active = 2
                    col_inactive = [3, 4]
                    # If the second or third savings filter variable is being
                    # looped through, do not write out total aggregate savings
                    # estimates to XLSX, but do flag the column in the XLSX
                    # where the relevant filter variable information will be
                    # written
                elif f == 1:
                    # Set the columns in the XLSX that are active for the
                    # current filter variable
                    col_active = 3
                    # Set the columns in the XLSX that correspond to the
                    # inactive filter variables (
                    # 'All' values will be written to these columns)
                    col_inactive = [2, 4]
                elif f == 2:
                    # Set the columns in the XLSX that are active for the
                    # current filter variable
                    col_active = 4
                    # Set the columns in the XLSX that correspond to the
                    # inactive filter variables ('All' values will be written
                    # to these columns)
                    col_inactive = [2, 3]

                # Loop through each filter variable category name to
                # add to plot
                for catnm in range(len(results_agg[f, 1])):
                    # Add lines for savings by filter variable category
                    if results_agg[f, 1][catnm][-1] != 0:
                        axb.plot(years, numpy.multiply(numpy.array(
                            results_agg[f, 1][catnm]), unit_translate),
                              color=results_agg[f, 2][catnm], lw=3)

                    # Add aggregate savings results broken out by filter
                    # variable to the data frame that will be written to the
                    # XLSX file Set ECM name to 'All ECMs' and results scenario
                    # to baseline minus efficient
                    xlsx_data.iloc[agg_row_ind, 0:2] = \
                        ["All ECMs", "Baseline competed - efficient competed"]
                    # Set the currently active filter variable category name
                    # (e.g., 'AIA CZ1', 'Ventilation,' etc.)
                    xlsx_data.iloc[agg_row_ind, col_active] = \
                        results_agg[f, 0][catnm]
                    # Set inactive filter variable values to 'All'
                    xlsx_data.iloc[agg_row_ind, col_inactive] = \
                        ["All", "All"]
                    # Add aggregate savings values broken out by the current
                    # filter variable category
                    # to the appropriate row/column range
                    xlsx_data.iloc[agg_row_ind, (5 + (len(
                        plot_title_labels_finmets))):len(xlsx_data.columns)] =\
                        numpy.multiply(numpy.array(
                            results_agg[f, 1][catnm]), unit_translate)
                    # Increment the XLSX row to write to by one
                    agg_row_ind = agg_row_ind + 1

                # Add a legend
                # Set legend names
                legend_entries = ['Total (Annual)', 'Total (Cumulative)'] + \
                    [x for r, x in sorted(zip(total_ranks, results_agg[f, 0]),
                                          reverse=True) if r != 0]
                # Set legend colors
                color_entries = ['#4d4d4d', '#7f7f7f'] + \
                    [x for r, x in sorted(zip(total_ranks, results_agg[f, 2]),
                                          reverse=True) if r != 0]
                # Set legend linestyles
                lty_entries = ['solid', 'dotted'] + \
                    ['solid'] * len(color_entries[2:])
                # Set legend thickness
                lw_entries = [3, 3] + [2] * len(color_entries[2:])

                plotsaxb = []
                for i in range(len(legend_entries)):
                    plotsaxb += \
                        axb.plot([], [], color=color_entries[i],
                                 lw=lw_entries[i],
                                 linestyle=lty_entries[i])
                # If needed, set parameter to scale down plot legend for EMM
                # or state regions (relevant only for the first filter
                # variable, region)
                if emm_det_flag is True and f == 0:
                    lg_sz = 8
                    ncol_leg = 2
                elif state_det_flag is True and f == 0:
                    lg_sz = 7
                    ncol_leg = 2
                else:
                    lg_sz = 8
                    ncol_leg = 1
                # Add legend
                axb.legend(plotsaxb, legend_entries, framealpha=0.3,
                           ncol=ncol_leg, prop={'size': lg_sz},
                           loc="upper left")
                axb.set_axis_on()

            # Generate aggregate savings figure
            with _pyplot_lock:
                fig.tight_layout()
                fig.savefig(f"{plot_file_name_agg}-Aggregate.pdf", bbox_inches='tight')
                plt.close(fig)

            with _pyplot_lock:
                fig, axcs = plt.subplots(2, 2, figsize=(10, 7))
            for (axc, fmp) in zip(fig.axes, range(len(fin_metrics))):
                # Shorthands for x and y data on the plot
                s_x, s_y = [results_finmets[:, len(fin_metrics)], results_finmets[:, fmp]]
                # Indices of sorted x data
                sorted_ind = sorted(
                    range(len(s_x)), key=lambda k: s_x[k], reverse=True)
                # Indices of sorted x data constrained to points where
                # associated y data are within pre-defined range for plots
                # and savings are non-zero
                final_index_non_na = [i for i in sorted_ind if (
                    (s_y[i] > -500) and (s_y[i] < 500) and
                    not math.isclose(s_x[i], 0, abs_tol=1e-9))]
                # Indices of sorted x data constrained to points where
                # associated y data are within pre-defined range for plots
                # and meet cost effectiveness threshold
                if fmp == 0:
                    final_index_ce = [i for i in final_index_non_na if (
                        (s_y[i] >= plot_ablines_finmets[fmp]))]
                else:
                    final_index_ce = [i for i in final_index_non_na if (
                        (s_y[i] <= plot_ablines_finmets[fmp]))]

                # Shorthands for rank-ordered measure results and plotting
                # parameters
                results_sort_x, results_sort_y, results_sort_pch, \
                    results_sort_bg = [[
                        results_finmets[:, met][i] for i in final_index_non_na]
                        for met in [
                            len(fin_metrics), fmp, (len(fin_metrics)+2), (len(fin_metrics)+3)]]
                # Shorthands for rank-ordered cost-effective measure results
                results_sort_x_ce, results_sort_y_ce = [[
                        results_finmets[:, met][i] for i in final_index_ce]
                        for met in [len(fin_metrics), fmp]]

                # Sum total cost effective savings
                total_save_ce = sum(s_x[final_index_ce])
                # Handle cases where there are less than 5 cost effective
                # ECMs to rank
                if len(final_index_ce) < 5:
                    ecm_length = len(final_index_ce)
                else:
                    ecm_length = 5
                # Set x axis savings values for top 5 ECMs
                label_vals_x = results_sort_x_ce[0:ecm_length]
                label_vals_x_ranks_str = [str(r+1) for r in range(ecm_length)]
                # Set y axis financial metrics values for top 5 ECMs
                label_vals_y = results_sort_y_ce[0:ecm_length]

                # Construct shorthands for rank-ordered measure names
                meas_names_sort = [
                    meas_names_no_all[i] for i in final_index_ce]
                # Set top 5 ECM names (add rank number next to each name)
                meas_names_lgnd = meas_names_sort[0:ecm_length]
                for mn in range(len(meas_names_lgnd)):
                    meas_names_lgnd[mn] = str(mn + 1) + " " + \
                        meas_names_lgnd[mn]

                # Set y limits for the plot
                ylim_fm = plot_lims_finmets[fmp]

                # Ensure that all of the top 5 ECMs' y values are accommodated
                # by the default y axis range for each financial metric type;
                # if not, adjust y axis range to accommodate out of range y
                # values for top 5 ECMs Adjust top of range as needed
                if len(label_vals_y) != 0:
                    if numpy.isfinite(max(label_vals_y)) and \
                       (max(label_vals_y) > max(plot_lims_finmets[fmp])):
                        plot_lims_finmets[fmp][1] = max(label_vals_y)
                    # Adjust bottom of range as needed
                    if numpy.isfinite(min(label_vals_y)) and \
                       (min(label_vals_y) < min(plot_lims_finmets[fmp])):
                        plot_lims_finmets[fmp][0] = min(label_vals_y)

                if len(results_sort_x) > 0:
                    # Retrieve the data needed to set x and y limits for the
                    # plot and plot individual ECM points, handling cases with
                    # one ECM or multiple ECMs
                    # Set x limits for the plot
                    if min(results_sort_x) > 0:
                        xlim = [0, max(results_sort_x)]
                    else:
                        xlim = [min(results_sort_x), max(results_sort_x)]
                    # Check for cases where points overlap with the
                    # top 5 ECM names listed in upper right
                    overlap_chk = [
                        (x, y) for x, y in zip(results_sort_x, results_sort_y)
                        if (x > 0.5*max(xlim) and y > 0.67 * max(ylim_fm))]

                    # If there are overlaps between any points and the
                    # top 5 ECM names in the upper right of the plot, extend
                    # the y axis upper limit to mitigate the overlaps
                    if len(overlap_chk) > 0:
                        ylim_fm = pretty(min(ylim_fm), (max(ylim_fm) +
                                         (0.5*max(ylim_fm))), 10)

                    if max(xlim) != min(xlim):
                        buff_x = abs((max(xlim) - min(xlim)) * 0.1)
                    else:
                        buff_x = abs(max(xlim) * 0.1)

                    # Initialize plot region for ECM cost effectiveness
                    axc.set_xlim(min(xlim) - buff_x,
                                 max(xlim) + buff_x)
                    axc.set_ylim(min(ylim_fm) - max(ylim_fm) * 0.1,
                                 max(ylim_fm) + max(ylim_fm) * 0.1)
                    axc.set_title(plot_title_labels_finmets[fmp])

                    # Add a polygon (going all the way to the boundaries) to
                    # distinguish the 'cost effective' region on each plot;
                    # again, IRR 'cost effectiveness' is above the threshold
                    # value, while 'cost effectiveness' under all other metrics
                    # is under the threshold value
                    if fmp == 0:
                        axc.axhspan(plot_ablines_finmets[fmp],
                                    max(ylim_fm) + max(ylim_fm) * 0.1,
                                    color='#DBDBDB', alpha=0.5, lw=0,
                                    zorder=0)
                    else:
                        axc.axhspan(plot_ablines_finmets[fmp],
                                    min(ylim_fm) - max(ylim_fm) * 0.1,
                                    color='#DBDBDB', alpha=0.5,
                                    lw=0, zorder=0)

                    # Add a line to distinguish the cost effectiveness
                    # threshold
                    axc.axhline(y=plot_ablines_finmets[fmp], color="black",
                                linestyle='dotted', zorder=1)

                    # Add x axis tick marks and axis labels
                    axc.set_xlabel(_mpl_escape(plot_axis_labels_finmets_x[v]))
                    # Add y axis tick marks and axis labels
                    axc.set_ylabel(_mpl_escape(plot_axis_labels_finmets_y[fmp]))
                    # Add label with total cost effective savings
                    label_text = 'Cost effective impact: ' + \
                                 str(round(total_save_ce, 1)) + \
                                 " " + _mpl_escape(var_units[v])
                    axc.text(0.02, 0.98, label_text, fontsize=7,
                             horizontalalignment='left',
                             verticalalignment='top',
                             transform=axc.transAxes,
                             zorder=1)

                    # Construct top 5 ECM name labels
                    label_meas = ''
                    for i in meas_names_lgnd:
                        label_meas = label_meas + i + '\n'
                    # Plot top 5 ECM name labels
                    axc.text(0.98, 0.98, label_meas, fontsize=7,
                             horizontalalignment='right',
                             verticalalignment='top',
                             transform=axc.transAxes, zorder=1)

                    # Add individual ECM points to the cost effectiveness plot
                    for i in range(len(results_sort_x)):
                        axc.scatter(results_sort_x[i], results_sort_y[i],
                                    color=results_sort_bg[i],
                                    marker=results_sort_pch[i],
                                    label="", zorder=1)

                    # Set parameters that control positioning of top 5 ECM
                    # rank labels (1, 2, 3, etc.) above/below associated points
                    if fmp == 0:
                        buff = 0.05
                        aln = "bottom"
                    else:
                        buff = -0.05
                        aln = "top"
                    # Plot top 5 ECM rank labels
                    for i in range(len(label_vals_x)):
                        axc.text(x=label_vals_x[i],
                                 y=label_vals_y[i] + max(ylim_fm) * buff,
                                 s=label_vals_x_ranks_str[i],
                                 horizontalalignment='center',
                                 verticalalignment=aln,
                                 fontdict=dict(color="black", size=6),
                                 zorder=1)
                else:  # produce blank plots
                    axc.set_xlim(0, 1)
                    axc.set_ylim(0, 1)

            # Add a series of legends to the second page of the PDF device
            # that distinguish the applicable climate zone, building type,
            # and end use of each ECM point on the plot by point outline
            # color, shape, and fill color, respectively
            # Initialize a blank plot region to put the legends in

            # Add legend for applicable building type

            # Building type shape parameter
            bclasses_shp = bclasses_out_finmets_shp + ["^"]
            # Building type legend text
            bclasses_lgnd = bclasses_out_finmets_lgnd + ["Multiple"]
            # End use legend colors
            euses_col = euses_out_finmets_col + ["#7f7f7f"]
            # End use legend text
            euses_lgnd = euses_out_finmets_lgnd + ["Multiple"]
            # Building type plots
            plots1 = []
            for i in range(len(bclasses_shp)):
                plots1.append(axc.scatter([], [], color="black",
                              marker=bclasses_shp[i]))
            # End use plots
            plots2 = []
            for i in range(len(euses_col)):
                plots2.append(axc.scatter([], [], marker="o",
                              color=euses_col[i]))
            # Building type legend
            leg1 = axc.legend(plots1, bclasses_lgnd,
                              loc='lower left',
                              frameon=False,
                              bbox_to_anchor=(0.1, -0.335, 1, 1),
                              bbox_transform=fig.transFigure,
                              title='Building Type')
            # End use legend
            leg2 = axc.legend(plots2, euses_lgnd,
                              loc='lower left',
                              frameon=False,
                              bbox_to_anchor=(0.25, -0.335, 1, 1),
                              bbox_transform=fig.transFigure,
                              title='End Use')
            # Add plot legends
            axc.add_artist(leg1)
            axc.add_artist(leg2)
            # Generate cost effectiveness figure
            with _pyplot_lock:
                fig.tight_layout()
                fig.savefig(plot_file_name_finmets, bbox_inches='tight')
                plt.close(fig)

            # Append Excel data, excluding the first two rows (uncompeted
            # 'All ECMs' results, which are not meaningful)
            xlsx_var_name_list.append(xlsx_data.iloc[2:xlsx_data.shape[0],
                                      0:len(xlsx_data.columns)])
        # Write out Excel results
        writer = pd.ExcelWriter(
            xlsx_file_name, engine='xlsxwriter')
        for i in range(len(xlsx_var_name_list)):
            xlsx_var_name_list[i].to_excel(
                writer, sheet_name=file_names_ecms[i], index=False)
        writer.close()

    # Run both adoption scenarios concurrently.  Each scenario writes to its
    # own output directory and XLSX file so there are no write conflicts.
    # plt.subplots(), tight_layout(), savefig(), and plt.close() are all
    # serialised via _pyplot_lock because matplotlib is not thread-safe:
    # tight_layout() invokes the mathtext parser which has a shared LRU cache,
    # and plt.close() mutates pyplot's global figure registry.
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(adopt_scenarios)) as pool:
        futures = [pool.submit(_plot_one_scenario, a)
                   for a in range(len(adopt_scenarios))]
        # Re-raise any exception from a worker thread in the main thread.
        for f in concurrent.futures.as_completed(futures):
            f.result()


if __name__ == '__main__':
    run_plot()
