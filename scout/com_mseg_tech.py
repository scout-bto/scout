#!/usr/bin/env python3

# Import commercial microsegments code to use some of its data
# reading and processing functions
from scout import com_mseg as cm

import numpy as np
import numpy.lib.recfunctions as recfn
import re
import warnings
import json
import csv
import itertools as it
from scout.config import FilePaths as fp


class EIAData(object):
    """Class of variables naming the EIA data files to be imported.

    Attributes:
        cpl_data (str): File name for the EIA AEO technology data.
        tpp_data (str): File name for the EIA AEO time preference premium data.
    """

    def __init__(self, data_dir=fp.INPUTS):
        self.cpl_data = data_dir / "ktek.csv"
        self.tpp_data = data_dir / "kprem.txt"


class UsefulVars(object):
    """Set up class to contain what would otherwise be global variables.

    Attributes:
        json_in (str): File name for the input JSON database.
        json_out (str): File name for the JSON output from this script.
        aeo_metadata (str): File name for the custom AEO metadata JSON.
        cpl_data_skip_lines (int): The number of lines of preamble that
            must be skipped at the beginning of the EIA AEO technology
            data file.
        columns_to_keep (list): A list of strings defining the columns
            from the EIA AEO technology data file that are required.
        tpp_data_skip_lines (int): The number of lines of preamble
            that must be skipped before finding data in the EIA AEO
            time preference premium data file.
        tpp_dtypes (list): A list of tuples in the format of a numpy
            dtype definition, specifying the expected dtype and desired
            column headings for the time preference premium data.
        eu_map (dict): Mapping between Scout end use names
            and end use numbers in EIA raw technology cose data.
        cconv (dict): Factors for converting from unit costs to $/ft^2.
    """

    def __init__(self):
        self.json_in = fp.INPUTS / 'cpl_res_cdiv.json'
        self.json_out = fp.INPUTS / 'cpl_res_com_cdiv.json'
        self.aeo_metadata = fp.METADATA_PATH

        self.cpl_data_skip_lines = 68
        self.columns_to_keep = ['t', 'v', 'r', 's', 'f', 'eff', 'c1', 'c2',
                                'c3', 'life', 'y1', 'y2', 'technology name']

        self.tpp_data_skip_lines = 100
        self.tpp_dtypes = [('Proportion', 'f8'), ('Time Pref Premium', 'f8'),
                           ('Year', 'i4'), ('End Use', 'U32')]
        self.eu_map = {
            "heating": 1,
            "cooling": 2,
            "water heating": 3,
            "ventilation": 4,
            "cooking": 5,
            "lighting": 6,
            "refrigeration": 7}

        # Set base directory
        with open(fp.CONVERT_DATA / "ecm_cost_convert.json", 'r') as cc:
            try:
                self.cconv = json.load(cc)
            except ValueError as e:
                raise ValueError(
                    "Error reading in cost conversion data file: " +
                    str(e)) from None


class UsefulDicts(object):
    """Set up class for dicts to relate different data file formats.

    Attributes:
        kprem_endusedict (dict): Keys are the strings found in the time
            preference premium data, and values are the strings used in
            the JSON database. Further conversion to numeric indices
            used in other EIA data files can be performed using the
            dicts found in com_mseg.py.
    """

    def __init__(self):
        self.kprem_endusedict = {
            'heating': 'Space Heating',
            'cooling': 'Space Cooling',
            'water heating': 'Hot Water Heating',
            'ventilation': 'Ventilation',
            'cooking': 'Cooking',
            'lighting': 'Lighting',
            'refrigeration': 'Refrigeration'}


def units_id(sel, flag):
    """Provides a units text string for a specified microsegment.

    Depending on the end use number given in the sel list, which
    specifies the entire microsegment, this function returns the
    string that best describes the units for that end use. Using
    this function ensures that the units are consistent throughout
    the output data. The unit definitions are based on the preamble
    text in the EIA AEO commercial buildings technology data file.

    Args:
        sel (list): A list of four integers that, together, define a
            microsegment, and correspond to the climate zone, building
            type, end use, and fuel type, in that order.
        flag (str): Indicates the type of units to be returned, either
            'cost' or 'performance'.

    Returns:
        A text string of the appropriate units for the input arguments
        to the function.
    """

    # For readability, assign the end use number to a clearly named variable
    enduse = sel[2]

    # Determine units depending on whether this function was called
    # for cost or performance units
    if flag == 'cost':
        if enduse == 4:  # ventilation
            theunits = '2022$/1000 cfm'
        elif enduse == 6:  # lighting
            theunits = '2022$/1000 lm'
        else:
            theunits = '2022$/kBTU out/hr'
    elif flag == 'performance':
        if enduse == 4:  # ventilation
            theunits = 'cfm-hr/BTU in'
        elif enduse == 6:  # lighting
            theunits = 'lm/W'
        else:
            theunits = 'BTU out/BTU in'

    return theunits


def tech_data_selector(tech_data, sel):
    """ From the full structured array of cost, performance, and
    lifetime data from the AEO, extract a group of data using numeric
    indices generated from the text indices at the leaf nodes of the
    input microsegments JSON. Each group of data extracted by this
    function will correspond to multiple technologies and performance
    levels and will require further processing. """

    # Determine whether the data indicated in the 'r' column indicates
    # building type or census division based on the end use indicated
    # (building type for ventilation, lighting, and refrigeration)
    if sel[2] in [4, 6, 7]:
        tmp = sel[1]  # use building type
    else:
        tmp = sel[0]  # use census division

    # Filter technology data based on the specified census
    # division or building type, end use, and fuel type
    filtered = tech_data[np.all([tech_data['r'] == tmp,
                                 tech_data['s'] == sel[2],
                                 tech_data['f'] == sel[3]], axis=0)]

    return filtered


def sd_data_selector(sd_data, sel, years):
    """ From the full structured array of service demand data from the
    AEO, extract just the service demand data corresponding to the
    census division, building type, end use, and fuel type specified by
    each leaf node in the input microsegments JSON. Each group of data
    are converted into two outputs, 1) a numpy array of service demand
    summed across the three specified markets (column named 'd'), with
    rows for each technology and performance level combination and
    columns for each year, and 2) a list of technology names for
    each row of the service demand numpy array (the other output). """

    # Filter service demand data based on the specified census
    # division, building type, end use, and fuel type
    filtered = sd_data[np.all([sd_data['r'] == sel[0],
                               sd_data['b'] == sel[1],
                               sd_data['s'] == sel[2],
                               sd_data['f'] == sel[3]], axis=0)]

    # Identify each technology and performance level using the text
    # in the description field since the technology type and vintage
    # numeric codes are not well-matched to individual technology and
    # performance levels; remove empty strings from the list
    technames = list(np.unique(filtered['Description']))
    technames = [x for x in technames if x != '']

    # Set up numpy array to store restructured data, in which each row
    # will correspond to a single technology
    sd = np.zeros((len(technames), len(years)))

    # Combine the service demand for the three markets ['d'] in the data
    for idx, name in enumerate(technames):

        # Extract entries for a given technology name
        entries = filtered[filtered['Description'] == name]

        # Calculate the sum of all year columns and write it to the
        # appropriate row in the sd array (note that the .view()
        # function converts the structured array into a standard
        # numpy array, which allows the use of the .sum() function)
        sd[idx, ] = np.sum(recfn.structured_to_unstructured(
            entries[list(map(str, years))], dtype='<f8'), axis=0)

    # Note that each row in sd corresponds to a single performance
    # level for a single technology and the rows are in the same order
    # as the technames list
    return sd, technames


def single_tech_selector(tech_array, specific_name):
    """Extracts a single technology from tech data for an entire microsegment.

    Each microsegment is comprised of multiple technologies. Cost,
    performance, and lifetime data are needed for each technology in a
    microsegment. This function separates out those data for a specific
    technology from all of the technologies in the microsegment so that
    they can be processed and further restructured for later output.

    Args:
        tech_array (numpy.ndarray): EIA technology characteristics
            data available for a single microsegment, including cost,
            performance, and lifetime data for (typically multiple)
            performance scenarios for each technology applicable to
            that microsegment.
        specific_name (type): The name of the technology to be extracted.

    Returns:
        A numpy structured array with the same columns as other tech
        data, but with only the rows corresponding to the technology
        indicated by specific_name.
    """

    # Initialize a list of rows to remove from the numpy array
    # that do not correspond to the specified technology
    rows_to_remove = []

    for idx, row in enumerate(tech_array):
        # Identify the technology name from the 'technology name' column
        # in the data using a regex set up to match any text '.+?' that
        # appears before the first occurrence of a space followed by a
        # 2 and three other numbers (i.e., 2009 or 2035)
        tech_name = re.search(r'.+?(?=\s2[0-9]{3})', row['technology name'])

        # If the technology name regex returned a match, check if there
        # is a match for a linear fluorescent lighting technology; in
        # either case (either the linear fluorescent or the more
        # generic technology name regex), if the match is not the same
        # as the name passed to the function, remove the row
        if tech_name:
            # Test whether the technology name corresponds to a linear
            # fluorescent lighting technology in the format 'T# F##',
            # e.g., 'T8 F96', and if it does, extract just that string
            # without any additional text (e.g., 'T8 F96 High Output')
            lfl_tech_name = re.search('^(T[0-9] F[0-9]{2})',
                                      tech_name.group(0))
            if lfl_tech_name:
                if lfl_tech_name.group(0) != specific_name:
                    rows_to_remove.append(idx)
            elif tech_name.group(0) != specific_name:
                rows_to_remove.append(idx)
        # If there's no match, the technology might not have a year
        # included as part of its name, but it nonetheless should be
        # checked to see if it matches the name passed to the function
        # and removed if there is not a match
        elif row['technology name'] != specific_name:
            rows_to_remove.append(idx)
        # Else check to see if the description indicates a placeholder
        # row, which should be deleted before the technologies are
        # summarized and returned from this function
        elif re.search('placeholder', row['technology name']):
            rows_to_remove.append(idx)
        # Implicitly, if the text does not match any regex, it is
        # assumed that it does not need to be edited or removed

    # Delete the placeholder rows
    result = np.delete(tech_array, rows_to_remove, 0)

    return result


def cost_perf_extractor(single_tech_array, sd_array, sd_names, years, flag):
    """Produces a dict of cost or performance data for a single technology.

    From a numpy structured array of data for a single technology
    with several rows corresponding to different performance levels,
    this function converts the reported capital costs or efficiencies
    for all of the different performance levels into a mean (called
    'typical' in the output dict) and a maximum ('best' in the output
    dict) for this technology class. Service demand data for each of
    the performance levels is used to calculate a service demand-
    weighted cost or efficiency for the 'typical' or mean case.
    A unique value is calculated and reported for each year in the
    years vector, which specifies the range of years over which the
    final data are to be output to the cost/performance/lifetime JSON.

    Args:
        single_tech_array (numpy.ndarray): Structured array of EIA
            technology characteristics data reduced to the various
            performance levels (if applicable) for a single technology
            (e.g., 'VAV_Vent' or 'comm_GSHP-heat')
        sd_array (numpy.ndarray): EIA service demand data for the entire
            microsegment associated with the specific technology that
            appears in single_tech_array
        sd_names (list): Strings describing the service demand data, with
            each entry in the list corresponding to that row in sd_array
        years (list): The range of years of interest, each as YYYY integers
        flag (str): String that should be either 'cost' or 'performance'
            to indicate the type of data the function is processing and
            will return

    Returns:
        A top-level dict with keys for the 'typical' and 'maximum' cost
        or performance cases, and child dicts for each case with values
        reported for each year in years. Also a list of technology
        names that didn't match between the technology cost,
        performance, and lifetime data and the service demand data.
    """

    # Using the string in the 'flag' argument, set a variable
    # for the column that contains the desired data to obtain
    # from single_tech_array
    if flag == 'cost':
        col = 'c1'
    elif flag == 'performance':
        col = 'eff'

    # Store the number of rows (different performance levels) in
    # single_tech_array and the number of years in the desired
    # range for the final data
    n_entries = np.shape(single_tech_array)[0]
    n_years = len(years)

    # Preallocate arrays for the technology cost or performance
    # and service demand data
    val = np.zeros([n_entries, n_years])
    select_sd = np.zeros([n_entries, n_years])

    # Preallocate list of non-matching technology names
    non_matching_tech_names = []

    for idx, row in enumerate(single_tech_array):
        # Determine the starting and ending column indices for the
        # desired data (cost or performance) related to the
        # technology associated with this row
        idx_st = row['y1'] - min(years)

        # Calculate end index using the smaller of either the last year
        # of 'years' or the final year of availability for that technology
        idx_en = min(max(years), row['y2']) - min(years) + 1

        # If the indices calculated above are in range, record the data
        # (cost or performance) in the calculated location(s)
        if idx_en > 0:
            if idx_st < 0:
                idx_st = 0
            val[idx, idx_st:idx_en] = row[col]

        # If the final year of availability (market exit year) for the
        # particular technology performance level corresponding to 'row'
        # is before the first year in years, do not update the service
        # demand data array used later to calculate val_mean and val_max
        if idx_en > 0:
            # The technology name from the ktek data must be updated to have
            # formatting consistent with the slightly different service
            # demand data technology names

            # Identify technology name for the current row of the ktek data
            name_from_ktek = row['technology name']

            # Truncate technology name string from technology data to
            # 44 characters since all of the string descriptions in the
            # service demand data are limited to 44 characters; there
            # is an exception for strings that have '-inch' in them,
            # which should be matched to the first n characters, where
            # n is either 43 or 48 characters depending on whether
            # '-inch' was substituted for '"' or '&quot;'; finally
            # remove any trailing spaces that might create text
            # matching problems
            if re.search('-inch', name_from_ktek[:43]):
                length = UsefulVars().trunc_len
            else:
                length = 44
            name_from_ktek = name_from_ktek[:length].strip()
            # The number of characters to use for text matching
            # determined when the service demand data description
            # strings are cleaned up; the substitution of '-inch' for
            # '"' will lengthen the string by four characters, thus the
            # matching should be done with 48 characters; replacing
            # '&quot;' will reduce the length of the string by 1, thus
            # the matching should be performed using 43 characters

            # Find the matching row in service demand data by comparing
            # the row technology name to sd_names and use that index to
            # extract the service demand data and insert them into the
            # service demand array in the same row as the corresponding
            # cost data
            try:
                select_sd[idx, ] = sd_array[sd_names.index(name_from_ktek), ]
            except ValueError:
                # If no match is found, add the unmatched technology
                # name to a list
                non_matching_tech_names.append(name_from_ktek)

    # Normalize the service demand data to simplify the calculation of
    # the service demand-weighted arithmetic mean of the desired data
    # (but perform the calculation only if there is at least one
    # non-zero entry in select_sd)
    if select_sd.any():
        # Suppress any divide by zero warnings
        with np.errstate(divide='ignore', invalid='ignore'):
            # Calculate the normalized service demand
            select_sd = select_sd/np.sum(select_sd, 0)
            select_sd = np.nan_to_num(select_sd)  # Replace nan from 0/0 with 0

    # Using the normalized service demand as the weights, calculate the
    # weighted arithmetic mean for each year (each column)
    val_mean = np.sum(np.transpose(select_sd)*single_tech_array[col], 1)

    # Calculate the maximum cost or performance for each year (each
    # column of the technology data array), adjusting for differences
    # in the calculation method (the arithmetic mean calculation does
    # not take into account market entry and exit years, relying on the
    # service demand weights to zero out technologies that are not
    # available in a given year) that can occasionally lead to the
    # mean being greater than than the maximum
    val_max = np.fmax(np.amax(val, 0), val_mean)

    # Build complete structured dict with 'typical' and 'best' data
    # converted into dicts themselves, indexed by year
    final_dict = {'typical': dict(zip(map(str, years), val_mean)),
                  'best': dict(zip(map(str, years), val_max))}

    return final_dict, non_matching_tech_names


def incentive_extractor(single_tech_array, years):
    """Produces a dict of cost incentives for a single technology.

    From a numpy structured array of data for a single technology
    with several rows corresponding to different performance levels,
    this function converts the reported cost incentive quantities for
    all of the performance levels for that technology. The incentive
    quantities by performance level are reported for each year in the
    years vector, which specifies the range of years over which the
    final data are to be output to the cost/performance/lifetime JSON.

    Args:
        single_tech_array (numpy.ndarray): Structured array of EIA
            technology characteristics data reduced to the various
            performance levels (if applicable) for a single technology
            (e.g., 'VAV_Vent' or 'comm_GSHP-heat')
        years (list): The range of years of interest, each as YYYY integers

    Returns:
        A dict with keys for each year and values containing a nested
        list of incentives by performance level in the format
        [[performance level, incentive quantity], ...]
    """

    # Store the number of rows (different performance levels) in
    # single_tech_array and the number of years in the desired
    # range for the final data
    n_entries = np.shape(single_tech_array)[0]
    n_years = len(years)

    # Preallocate arrays for the technology cost or performance
    # and service demand data
    incentive = np.zeros([n_entries, n_years])
    perf = np.zeros([n_entries, n_years])

    for idx, row in enumerate(single_tech_array):
        # Determine the starting and ending column indices for the
        # desired data (cost or performance) related to the
        # technology associated with this row
        idx_st = row['y1'] - min(years)

        # Calculate end index using the smaller of either the last year
        # of 'years' or the final year of availability for that technology
        idx_en = min(max(years), row['y2']) - min(years) + 1

        # If the indices calculated above are in range, record the data
        # incentive and performance levels in the calculated location(s)
        if idx_en > 0:
            if idx_st < 0:
                idx_st = 0
            incentive[idx, idx_st:idx_en] = row['c3']
            perf[idx, idx_st:idx_en] = row['eff']

    # For each year, construct a nested list of performance level and
    # incentive quantity lists for all non-zero performance levels
    # (performance levels with zero incentives are included)
    final_dict = dict.fromkeys(map(str, years))
    for yr in range(0, n_years):
        # Construct nested list of performance level and incentive value pairs
        incent_nl = [[perf[i, yr], incentive[i, yr]] for i in range(0, n_entries)
                     if perf[i, yr] != 0]
        # Remove duplicates from nested list and set as value for year key
        # https://stackoverflow.com/questions/2213923/removing-duplicates-from-a-list-of-lists
        final_dict[str(years[yr])] = list(k for k, _ in it.groupby(sorted(incent_nl)))

    return final_dict


def life_extractor(single_tech_array, years):
    """Produces a nested dict of lifetime data for a single technology.

    From a numpy structured array with the cost, performance, and
    lifetime data for a specific technology, calculate the arithmetic
    mean lifetime and 'range', which is calculated for the residential
    data as the difference between the maximum and the mean for each
    year. This function accounts for cases where the performance levels
    for a given technology exit the market before another level enters
    with the assumption that the previous lifetime should persist until
    the next performance level enters the market.

    Args:
        single_tech_array (numpy.ndarray): Structured array of EIA
            technology characteristics data reduced to the various
            performance levels (if applicable) for a single technology
            (e.g., 'VAV_Vent' or 'comm_GSHP-heat')
        years (list): The range of years of interest, each as YYYY

    Returns:
        A top-level dict with keys for the 'typical' and 'maximum'
        lifetime cases, and child dicts for each case with values
        reported for each year in years.
    """

    # Store the number of rows (different performance levels) in
    # single_tech_array and the number of years in the desired
    # range for the final data
    n_entries = np.shape(single_tech_array)[0]
    n_years = len(years)

    # Preallocate arrays for the lifetime data
    life = np.zeros([n_entries, n_years])

    for idx, row in enumerate(single_tech_array):
        # Determine the starting and ending column indices for the
        # lifetime of the technology performance level in this row
        idx_st = row['y1'] - min(years)

        # Calculate end index using the smaller of either the last year
        # of 'years' or the final year of availability for that technology
        idx_en = min(max(years), row['y2']) - min(years) + 1

        # If the indices calculated above are in range, record the
        # lifetime in the calculated location(s)
        if idx_en > 0:
            if idx_st < 0:
                idx_st = 0
            life[idx, idx_st:idx_en] = row['life']

    # Calculate the mean lifetime for each column, excluding 0 values
    with warnings.catch_warnings():
        # In cases where a particular technology does not have a
        # performance level defined as available for a given year,
        # excluding 0 values leaves nothing on which to calculate a
        # mean, which triggers a RuntimeWarning that is suppressed
        # here using the warnings package
        warnings.simplefilter("ignore", category=RuntimeWarning)
        life_mean = np.apply_along_axis(
            lambda v: np.mean(v[np.nonzero(v)]), 0, life)

    # In the special case where no performance level is given because
    # the product exits the market before the first year in the 'years'
    # vector, make the entire reported mean lifetime equal to 0 in each
    # year using the life array, which should still be populated with
    # only zeros
    if np.all(np.isnan(life_mean)):
        life_mean = np.mean(life, 0)
    # In the special case where there were years with no performance
    # level indicated in the 'life' array, the mean will be 'nan'; it
    # is assumed that the previous technology's lifetime persists until
    # the next performance level enters the market
    elif np.any(np.isnan(life_mean)):
        # First, identify the numeric values reported
        numbers = life_mean[~np.isnan(life_mean)]

        # Then, generate a vector that, for each entry in the final
        # life_mean vector, has the index for the appropriate number
        # to be pulled from the 'numbers' vector
        indices = np.cumsum(~np.isnan(life_mean)) - 1

        # Use the indices and the numbers to adjust life_mean
        life_mean = numbers[indices]

    # Calculate the lifetime range in each column using the same method
    # as mseg_techdata.py (note that this quantity is not related to
    # any statistical definitions of range) and account for any cases
    # where life_mean was just adjusted to be non-zero in some years
    life_range = np.fmax(np.amax(life, 0), life_mean) - life_mean

    # Build complete structured dict with 'average' and 'range' data
    # converted into dicts that are indexed by year
    final_dict = {'average': dict(zip(map(str, years), life_mean)),
                  'range': dict(zip(map(str, years), life_range))}

    return final_dict


def tech_names_extractor(tech_array):
    """Creates a list of unique technology "names" for a microsegment.

    Text strings are used to identify which cost, performance, and
    lifetime data are associated with what technologies. This function
    identifies appropriate text strings to use for each of the
    technologies in a single microsegment.

    Args:
        tech_array (numpy.ndarray): EIA technology characteristics
            data available for a single microsegment, including cost,
            performance, and lifetime data for (typically multiple)
            performance scenarios for each technology applicable to
            that microsegment.

    Returns:
        A list of strings, where each string represents a technology
        "name" or descriptor that does not include scenario-specific
        details like "2020 high" or "2009 installed base".
    """

    # Create empty list to be populated with technology names
    technames = []

    for row in tech_array:
        # Identify the technology name from the 'technology name' column
        # in the data using a regex set up to match any text '.+?' that
        # appears before the first occurrence of a space followed by a
        # 2 and three other numbers (e.g., 2009 or 2035)
        tech_name = re.search(r'.+?(?=\s2[0-9]{3})', row['technology name'])

        # If the regex matched, check the matching text to see if it
        # corresponds to a linear fluorescent lighting technology
        # represented in the format 'T# F##', e.g., 'T8 F96'; if it does,
        # extract from the match just the 'T# F##' string without any
        # additional modifier text (e.g., 'T8 F96 High Output'); if not,
        # add the text that matched originally, which describes the
        # technology without scenario-specific text like '2003 installed
        # base' to the technames list
        if tech_name:
            lfl_tech_name = re.search('^(T[0-9] F[0-9]{2})',
                                      tech_name.group(0))
            if lfl_tech_name:
                technames.append(lfl_tech_name.group(0))
            else:
                technames.append(tech_name.group(0))
        # Else, if the technology name is not from a placeholder row,
        # add the entire name text to the technames list
        else:
            if not re.search('placeholder', row['technology name']):
                technames.append(row['technology name'])

    # Reduce the list to only the unique entries
    technames = list(np.unique(technames))

    return technames


def tpp_handler(tpp_data, sel, years):
    """Extracts and restructures time preference premium data for an end use.

    Time preference premium data are specific to a year and end use and
    are available for the main end uses in commercial buildings:
    heating, cooling, water heating, ventilation, cooking, lighting,
    and refrigeration. The data are given as the fraction of the total
    population of building owners/customers with a particular time
    preference (related to their discount rate) and the particular time
    preferences for each subset of the population. These two parameters
    are recorded as the 'population fraction' and 'time preference',
    respectively.

    Args:
        tpp_data(numpy.ndarray): A numpy structured array of the time
            preference data.
        sel (list): A list of integers indicating the microsegment.
        years (list): A list of integers representing the range of years
            in the data, precalculated for speed.

    Returns:
        A dict with years as keys and lists of numbers as values for
        both the population fractions and corresponding time preferences
        for each year of data indicated in 'years'. These dicts are
        rolled up to a master dict with keys for each of the types of
        data.
    """

    # From the number for the end use given in 'sel', do reverse
    # lookups in the respective translation dicts to obtain the
    # string that should be used to select time preference data
    # NOTE - reverse lookups on dicts is not typical and can
    # be unstable because unique keys can have identical values,
    # though for the particular dicts used here, there should not
    # be a problem
    end_use_num = sel[2]
    end_use_dict_loc = list(
        cm.CommercialTranslationDicts().endusedict.values()).index(end_use_num)
    end_use_json_str = list(
        cm.CommercialTranslationDicts().endusedict.keys())[end_use_dict_loc]
    end_use_kprem_string = UsefulDicts().kprem_endusedict[end_use_json_str]

    # Obtain the time preference data associated with the end use
    # extracted from the dict lookup
    tpp_subset = tpp_data[tpp_data['End Use'] == end_use_kprem_string]

    # Initialize dicts for the population fraction/proportion data and
    # corresponding time preferences
    proportion_dict = {}
    time_prefs_dict = {}

    # For each year in the data, extract the applicable population
    # fractions and time preferences and, if values are reported for both
    # parameters for that year, add them to their respective dicts using
    # the current year as the key; time preference premiums generally
    # do not vary by year, but they are included by year for completeness
    for yr in years:
        population_frac = tpp_subset[tpp_subset['Year'] == yr]['Proportion']
        premiums = tpp_subset[tpp_subset['Year'] == yr]['Time Pref Premium']
        # If any data are found/present, add to dict
        if population_frac.any() and premiums.any():
            proportion_dict[str(yr)] = list(population_frac)
            time_prefs_dict[str(yr)] = list(premiums)

    # Combine into one the separate dicts for the parameters of interest
    combined_dict = {'time preference': time_prefs_dict,
                     'population fraction': proportion_dict}

    return combined_dict


def mseg_technology_handler(
        tech_data, sd_data, tpp_data, sf_data, sel, years, eu_map):
    """Restructures cost, performance, lifetime, and time preference data.

    Using external functions that process and reformat specific
    categories of data from the EIA source data arrays, this function
    converts the cost, performance, and lifetime data for each
    technology within a particular microsegment to a dict format that
    is consistent with the residential technology data. Those data for
    each technology are then added to a master dict that ultimately
    includes all of the technologies in the microsegment. In addition,
    the time preference premium data associated with each end use and
    year are added to the master dict for the microsegment.

    This function is called for each terminal, or leaf, node in the
    microsegments JSON database that governs the structure of the major
    project input files that are based on EIA Annual Energy Outlook
    data. Each of those leaf nodes corresponds to a single, unique
    microsegment. The dict returned by this function to be placed at
    the leaf node includes the data for all of the technologies
    applicable to that microsegment.

    This function is relevant to all microsegments with a numeric end
    use code <= 7 (i.e., all end uses except for PCs, non-PC office
    electronics, and "other").

    Args:
        tech_data (numpy.ndarray): Imported EIA technology characteristics
            data, with multiple efficiency levels for each technology,
            including technology cost, performance, and service lifetime.
        sd_data (numpy.ndarray): Imported EIA service demand data specified
            over the same efficiency levels for each technology.
        tpp_data (numpy.ndarray): A numpy structured array of the
            EIA commercial market time preference premium data.
        sf_data (numpy.ndarray): Imported EIA data including square
            footage data as a function of census division and
            building type. (Includes the full data file contents.)
        sel (list): A list of integers indicating the microsegment.
        years (list): A list of integers representing the range of years
            in the data, precalculated for speed.
        eu_map (dict): Mapping between Scout end use names
            and end use numbers in EIA raw technology cost data.

    Returns:
        A dict that specifies the cost, performance, and lifetime on
        a technology-specific basis for all of the technologies in the
        microsegment indicated by the 'sel' argument. Also a list of
        the technology names in the microsegment that did not match
        between the cost, performance, and lifetime data and the
        service demand data.
    """

    # Instantiate a master dict for this microsegment
    complete_mseg_tech_data = {}

    # From the imported EIA data, extract the technology and service
    # demand data for the microsegment identified by 'sel'
    filtered_tech_data = tech_data_selector(tech_data, sel)
    (filtered_sd_data, sd_names_list) = sd_data_selector(sd_data, sel, years)

    # Use the 'units_id' function to extract the performance units for
    # the microsegment specified by 'sel' (the same function can also
    # provide units for costs if they have not yet been converted to
    # a per square foot floor area basis)
    the_performance_units = units_id(sel, 'performance')

    # Identify the names (as strings) of all of the technologies
    # included in this microsegment
    tech_names_list = tech_names_extractor(filtered_tech_data)

    # Preallocate a list of non-matching technology names for this microsegment
    mseg_non_matching_names = []

    # Extract the cost, performance, and lifetime data for each
    # technology in this microsegment, insert those data into a dict
    # with the correct structure, and append that dict to the master
    # dict for this microsegment
    for tech in tech_names_list:
        # Extract the cost, performance, and lifetime data specific
        # to a single technology, given by 'tech'
        single_tech_data = single_tech_selector(filtered_tech_data, tech)

        # Extract the cost data in a dict format with 'typical' and
        # 'best' cost cases
        the_cost, cost_non_matching_names = cost_perf_extractor(
            single_tech_data,
            filtered_sd_data,
            sd_names_list,
            years, 'cost')

        # Update the cost data with the conversion factor from
        # $/service capacity (generally $/kBtu/h) to $/ft^2 for both
        # the 'typical' and 'best' cases, then add the units and data
        # source to complete the dict for this technology
        the_cost['typical'] = dict(zip(
            sorted(the_cost['typical'].keys()),
            sorted(the_cost['typical'].values())))
        the_cost['best'] = dict(zip(
            sorted(the_cost['best'].keys()),
            sorted(the_cost['best'].values())))
        # Set the year that should be assumed for EIA cost dollars
        cost_yr = '2022'
        # Find end use service of current microsegment
        eu = [x[0] for x in eu_map.items() if x[1] == sel[2]][0]
        # Set cost units appropriately for the end use service
        if eu == "lighting":
            eu_cost_units = '$/1000 lm'
        elif eu == "ventilation":
            eu_cost_units = '$/1000 CFM'
        else:
            eu_cost_units = '$/kBtu/h ' + eu
        the_cost['units'] = cost_yr + eu_cost_units
        the_cost['source'] = 'EIA AEO'

        # Extract the cost incentive values by performance level
        the_incentives = incentive_extractor(single_tech_data, years)

        # Extract the performance data, restructure into the appropriate
        # dict format, and append the units and data source
        the_perf, _ = cost_perf_extractor(
            single_tech_data,
            filtered_sd_data,
            sd_names_list,
            years, 'performance')
        the_perf['units'] = the_performance_units
        the_perf['source'] = 'EIA AEO'

        # Extract the lifetime data, restructure into the appropriate
        # dict format, and append the units and data source
        the_life = life_extractor(single_tech_data, years)
        the_life['units'] = 'years'
        the_life['source'] = 'EIA AEO'

        # Following the format used for the residential data, combine
        # the cost, performance, and lifetime data for the technology
        # identified by the variable 'tech' into a single dict
        tech_data_dict = {
            'installed cost': {
                'before incentives': the_cost,
                'incentives': {
                    'by performance tier': the_incentives,
                    'performance units': the_performance_units}},
            'performance': the_perf,
            'lifetime': the_life}

        # Add the data for this technology to the master dict for the
        # entire microsegment (limit the technology name length to
        # less than 43 characters to match the stock and energy data)
        complete_mseg_tech_data[tech[:43]] = tech_data_dict

        # If there were any non-matching names identified, replace the
        # preallocated empty list with the list of non-matching names;
        # note that only the non-matching names from the cost case are
        # included here since the list of names will be the same for
        # either the cost or performance data extraction
        if cost_non_matching_names:
            mseg_non_matching_names = cost_non_matching_names

    # Add time preference premium data for the current end use
    # to the complete dict with all of the technology cost,
    # performance, and lifetime data added
    complete_mseg_tech_data['consumer choice'] = tpp_handler(
        tpp_data, sel, years)

    return complete_mseg_tech_data, mseg_non_matching_names


def walk(tech_data, serv_data, tpp_data, db_data, years, json_db, eu_map,
         key_list=[], no_match_names=[]):
    """Recursively explore the JSON structure and add the appropriate data.

    Note that this walk function and the data processing function
    ('mseg_techology_handler') are set up slightly differently than in
    com_mseg. Here, the json_interpreter function is called before the
    data processing function and the numeric indices are passed to the
    function, rather than sending the list of keys from the JSON to
    that function and calling json_interpreter within the function.

    Args:
        tech_data (numpy.ndarray): A numpy structured array of the
            EIA technology data, including the cost, performance,
            and lifetime of individual technologies.
        serv_data (numpy.ndarray): A numpy structured array of the
            EIA service demand data.
        tpp_data (numpy.ndarray): A numpy structured array of the
            EIA commercial market time preference premium data.
        db_data (numpy.ndarray): An array of commercial building data,
            including total energy use by end use/fuel type and all
            MELs types, new and surviving square footage, and other
            parameters. Square footage data are specified as a
            function of census division and building type.
        years (list): A list of the years (YYYY) of data to be converted.
        json_db (dict): The nested dict structure of the empty or
            partially complete database to be populated with new data.
        eu_map (dict): Mapping between Scout end use names
            and end use numbers in EIA raw technology cose data.
        key_list (list): The list of keys that define the current
            location in the database structure.
        no_match_names (list): A list of names of technologies found in
             the cost, performance, and lifetime data, but not in the
             service demand data.

    Returns:
        A complete and populated dict structure for the JSON database,
        and a list of all technology names that did not find a match.
    """

    # Explore data structure from current level
    for key, item in json_db.items():

        # If there are additional levels in the dict, call the function
        # again to advance another level deeper into the data structure
        if isinstance(item, dict):
            walk(tech_data, serv_data, tpp_data, db_data,
                 years, item, eu_map, key_list + [key])

        # If a leaf node has been reached, check if the second entry in
        # the key list is one of the recognized building types and that
        # there are more than two total keys present (to exclude square
        # footage leaf nodes), and if so, finish constructing the key
        # list for the current location and obtain the data to update
        # the dict
        else:
            cd = cm.CommercialTranslationDicts()  # Shortens if statement below
            if key_list[1] in cd.bldgtypedict.keys() and len(key_list) > 2:
                leaf_node_keys = key_list + [key]

                # Convert keys into integers that define the microsegment
                mseg_codes = cm.json_interpreter(leaf_node_keys)

                # Skip all demand microsegments and end uses coded > 7
                if 'demand' not in leaf_node_keys and mseg_codes[2] <= 7:

                    # Extract data from original data sources
                    data_dict, non_matching_names = mseg_technology_handler(
                        tech_data, serv_data, tpp_data, db_data,
                        mseg_codes, years, eu_map)

                    # Set dict key to extracted data
                    json_db[key] = data_dict

                    # If non-matching names are identified, add them to
                    # the existing list of non-matched technology names
                    if non_matching_names:
                        no_match_names.extend(non_matching_names)

    return json_db, no_match_names


def kprem_import(data_file_path, dtype_list, hl):
    """Import data and convert to a numpy structured array.

    Read the contents of the time preference premium data file and
    convert them into a numpy structured array. This function is
    unique from the function used to import other EIA data because
    the formatting of the time preference premium data (kprem) is
    different. In particular, not all of the lines in the data are
    the same length and there are empty lines separating the data
    visually that are not needed when imported.

    Args:
        data_file_path (str): The full path to the data file to be imported.
        dtype_list (list): A list of tuples with each tuple containing two
            entries, a column heading string, and a string defining the
            data type for that column. Formatted as a numpy dtype list.
        hl (int): The number of header lines to skip from the top of
            the file before reading data.

    Returns:
        A numpy structured array of the imported data file with the
        columns specified by dtype_list.
    """

    # Open the target CSV formatted data file
    with open(data_file_path) as thefile:
        # Open the file contents as a csv reader object
        filecont = csv.reader(thefile, delimiter='\t')

        # Create list to be populated with tuples for each row of data
        # from the data file
        data = []

        # Skip the specified number of header lines in the file
        for i in range(0, hl):
            next(filecont)

        # Record data type length for later repeated reference
        dtypelen = len(dtype_list)

        # Import the data, reconstructing the line if it is missing data
        for row in filecont:
            rowlen = len(tuple(row))  # Record current row length

            # If the current row and the data type lengths match,
            # append the data to the list
            if rowlen == dtypelen:
                data.append(tuple(row))

            # If the length of the current row is greater than zero but
            # less than the length of the dtype, and is not an empty
            # row (which appears as a list with two empty strings when
            # imported), use the missing columns from the previous row
            # to complete the row entry and append to the data list
            elif rowlen > 0 and rowlen < dtypelen and row != ['', '']:
                # Determine the number of missing columns of data
                diff = dtypelen - rowlen

                # Construct this line by appending (making a flat list
                # using extend instead of append) any missing columns
                # from the previous line
                row.extend(list(data[len(data)-1][diff:]))

                # Append constructed line, as a tuple, to the data
                data.append(tuple(row))

        # Convert data into numpy structured array
        final_struct = np.array(data, dtype=dtype_list)

        return final_struct


def dtype_reducer(the_dtype, wanted_cols):
    """Remove extraneous columns from the dtype definition.

    In cases where a data file includes some columns of data that are
    not of particular interest or relevance, this function can remove
    those columns that are not needed (or more accurately, retain only
    the columns that are desired). This function was originally created
    for the purpose of importing the EIA ktek data, which may include
    some columns with mixed data types that are difficult to import and
    not relevant to this analysis anyway. Avoiding those columns
    entirely is easier than developing far more sophisticated functions
    to import the data.

    Args:
        the_dtype (list): A list of tuples with each tuple containing two
            entries, a column heading string, and a string defining the
            data type for that column. Formatted as a numpy dtype list.
        wanted_cols (list): A list of strings that represent the names of
            the columns from the ktek data that should be kept.

    Returns:
        col_loc is a list of the numeric indices for the positions of
        the columns retained in the dtype definition (and thus which
        columns should be retained when importing the full data file).
        shortened_dtype is the dtype definition (in numpy dtype format)
        that includes only the desired columns.
    """

    # Strip apart the dtype definition
    headers, dtypes = zip(*the_dtype)

    # Preallocate list for the numeric column indices of the wanted_cols
    col_loc = []

    # Make a list of the numeric index positions of the desired columns
    for entry in wanted_cols:
        try:
            col_loc.append(headers.index(entry))
        except ValueError:
            print('Desired column "' + entry + '" not found in the data.')

    # Update the headers and dtypes by building them as new lists with
    # only the desired columns and then recombining them into the numpy
    # dtype definition format
    headers = [headers[i] for i in col_loc]
    dtypes = [dtypes[i] for i in col_loc]
    shortened_dtype = list(zip(headers, dtypes))

    return col_loc, shortened_dtype


def main():
    """Import external data files, process contents, and generate output data.

    This function imports the required EIA data files with the relevant
    cost, performance, and equipment lifetime data and calls the
    appropriate functions to convert their contents into the JSON file
    format and nested structure expected. After extracting the data
    from the original EIA source files, they are converted from a
    census division to a climate zone basis.

    The census division to climate zone conversion data file appropriate
    for the cost, performance, and lifetime data is formatted such that
    the translation factors act as weights to compute a weighted average
    of the cost, performance, and lifetime values reported. This file is
    different from the file used for the conversion for the energy data
    and is specific to commercial buildings.
    """

    # Instantiate objects that contain useful variables
    handyvars = UsefulVars()
    eiadata = EIAData()

    # Import technology cost, performance, and lifetime data in
    # EIA AEO 'KTEK' data file (2 rows of headers found in ktek.csv)
    tech_dtypes = cm.dtype_array(eiadata.cpl_data, ',',
                                 handyvars.cpl_data_skip_lines - 1)

    col_indices, tech_dtypes = dtype_reducer(tech_dtypes,
                                             handyvars.columns_to_keep)
    tech_data = cm.data_import(eiadata.cpl_data, tech_dtypes, ',',
                               handyvars.cpl_data_skip_lines, col_indices)
    tech_data = cm.str_cleaner(tech_data, 'technology name')

    # Import EIA AEO 'KSDOUT' service demand data
    serv_dtypes = cm.dtype_array(cm.EIAData().serv_dmd)
    serv_data = cm.data_import(cm.EIAData().serv_dmd, serv_dtypes)
    serv_data, tval = cm.str_cleaner(serv_data, 'Description', True)

    # Import EIA AEO 'KDBOUT' additional data file
    catg_dtypes = cm.dtype_array(cm.EIAData().catg_dmd)
    catg_data = cm.data_import(cm.EIAData().catg_dmd, catg_dtypes)
    catg_data = cm.str_cleaner(catg_data, 'Label')

    # Import EIA AEO 'kprem' time preference premium data
    tpp_data = kprem_import(eiadata.tpp_data, handyvars.tpp_dtypes,
                            handyvars.tpp_data_skip_lines)

    # Import metadata generated based on EIA AEO data files
    with open(handyvars.aeo_metadata, 'r') as metadata:
        metajson = json.load(metadata)

    # Assign available string truncation length value to UsefulVars
    # class so that it is available for all class uses
    UsefulVars.trunc_len = tval

    # Define years vector using year data from metadata
    years = list(range(metajson['min year'], metajson['max year'] + 1))

    # Import empty microsegments JSON file and traverse database structure
    try:
        with open(handyvars.json_in, 'r') as jsi, open(handyvars.json_out, 'w') as jso:
            msjson = json.load(jsi)

            # Proceed recursively through database structure
            result, nmtn = walk(tech_data, serv_data, tpp_data, catg_data,
                                years, msjson, handyvars.eu_map)

            # Print warning message to the standard out with a unique
            # (i.e., non-repeating) list of technologies that didn't have
            # a match between the two data sets and thus were not added
            # to the aggregated cost or performance data in the output JSON
            # The technologies that appear in this list might vary from
            # year to year.
            if nmtn:
                text = ('Warning: some technologies reported in the '
                        'technology characteristics data were not found to '
                        'have corresponding service demand data and were '
                        'thus excluded from the reported technology cost '
                        'and performance. These technologies are generally '
                        'absent from or have all zeros for their service '
                        'demand data.')
                print(text)
                for item in sorted(list(set(nmtn))):
                    print('   ' + item)

            # Write the updated dict of data to a new JSON file
            json.dump(result, jso, indent=2)

    except FileNotFoundError:
        errtext = ('Confirm that the expected residential data file ' +
                   handyvars.json_in + ' has already been created and '
                   'is in the current directory.\n')
        print(errtext)


if __name__ == '__main__':
    main()
