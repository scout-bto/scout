#!/usr/bin/env python3

import numpy as np
import numpy.lib.recfunctions as recfn
import re
import csv
import json
import io
from functools import reduce
from scout.config import FilePaths as fp


class EIAData(object):
    """Class of variables naming the EIA data files to be imported.

    Attributes:
        serv_dmd (str): Filename for the commercial service demand data.
        catg_dmd (str): Filename for the commercial energy and stock data.
        com_generation (str): Filename for the commercial building
            microsegment generation data.
    """

    def __init__(self, data_dir=fp.INPUTS):
        self.serv_dmd = data_dir / "CDM_SDOUT.txt"
        self.catg_dmd = data_dir / "CDM_DBOUT.txt"
        self.com_generation = data_dir / "CDM_DGENOUT.txt"


class UsefulVars(object):
    """Class of variables that would otherwise be global.

    Attributes:
        json_in (str): Filename for input JSON that has only residential data.
        json_out (str): Filename for JSON with commercial building data added.
        com_tloads (str): Filename for the commercial thermal load components.
        aeo_metadata (str): File name for the custom AEO metadata JSON.
        pivot_year (int): The pivot year is the value that should be
            added to the year numbers reported in DBOUT to convert
            the values to actual calendar years.
    """

    def __init__(self):
        self.json_in = fp.INPUTS / 'mseg_res_cdiv.json'
        self.json_out = fp.INPUTS / 'mseg_res_com_cdiv.json'
        self.com_tloads = fp.THERMAL_LOADS / 'Com_TLoads_Final.txt'
        self.aeo_metadata = fp.METADATA_PATH
        self.pivot_year = 1989


class CommercialTranslationDicts(object):
    """Class of dicts that relate the JSON strings with numeric indices.

    For each set defining a microsegment, e.g., census divisions,
    climate zones, building types, the members of that set are recorded
    using human-readable strings in the microsegments JSON files and
    indexed numerically (in general) in the EIA AEO data files. Each
    dict here provides the translation between the string and numeric
    indices for a single set of indices. Demand data are the exception;
    those data use short string indices instead of numbers.

    Attributes:
        cdivdict (dict): Translation for census divisions.
        bldgtypedict (dict): Translation for commercial building types.
        endusedict (dict): Translation for commercial building end uses.
        mels_techdict (dict): Translation for miscellaneous electric
            loads (MELs). The numeric translation should be updated
            each year based on the interpretation given in the AEO
            commercial buildings microdata file. If there are
            conspicuously missing MEL codes in the microdata, EIA
            should be contacted to verify the translation between
            numeric codes and descriptive names. Additionally, the
            numeric codes in the end use column in DBOUT.txt in the
            rows labeled 'MiscElConsump' should be compared against
            the codes in the microdata to see if any of the codes are
            missing from DBOUT.txt.
        fueldict (dict): Translation for fuel types.
        demand_typedict (dict): Translation for components of thermal load.
    """

    def __init__(self):
        self.cdivdict = {'new england': 1,
                         'mid atlantic': 2,
                         'east north central': 3,
                         'west north central': 4,
                         'south atlantic': 5,
                         'east south central': 6,
                         'west south central': 7,
                         'mountain': 8,
                         'pacific': 9
                         }

        self.bldgtypedict = {'assembly': 1,
                             'education': 2,
                             'food sales': 3,
                             'food service': 4,
                             'health care': 5,
                             'lodging': 6,
                             'large office': 7,
                             'small office': 8,
                             'mercantile/service': 9,
                             'warehouse': 10,
                             'other': 11,
                             'unspecified': 12  # for some "other" energy
                             }

        self.endusedict = {'heating': 1,
                           'cooling': 2,
                           'water heating': 3,
                           'ventilation': 4,
                           'cooking': 5,
                           'lighting': 6,
                           'refrigeration': 7,
                           'PCs': 8,
                           'non-PC office equipment': 9,
                           'other': 10,
                           'MELs': 10,
                           'unspecified': 11
                           }

        # self.mels_techdict = {'distribution transformers': 1,
        #                       'security systems': 2,
        #                       'elevators': 3,
        #                       'escalators': 4,
        #                       'non-road electric vehicles': 5,
        #                       'coffee brewers': 6,
        #                       'kitchen ventilation': 7,
        #                       'laundry': 8,
        #                       'lab fridges and freezers': 9,
        #                       'fume hoods': 10,
        #                       'medical imaging': 11,
        #                       'large video boards': 12,
        #                       'IT equipment': 13,
        #                       'office UPS': 14,
        #                       'data center UPS': 15,
        #                       'shredders': 16,
        #                       'private branch exchanges': 17,
        #                       'voice-over-IP telecom': 18,
        #                       'water services': 19,  # non-building
        #                       'telecom systems': 20  # non-building
        #                       }

        self.mels_techdict = {'distribution transformers': 1,
                              'kitchen ventilation': 2,
                              'security systems': 3,
                              'lab fridges and freezers': 4,
                              'medical imaging': 5,
                              'large video boards': 6,
                              'coffee brewers': 7,
                              'non-road electric vehicles': 8,
                              'fume hoods': 9,
                              'laundry': 10,
                              'elevators': 11,
                              'escalators': 12,
                              'IT equipment': 13,
                              'office UPS': 14,
                              'data center UPS': 15,
                              'shredders': 16,
                              'private branch exchanges': 17,
                              'voice-over-IP telecom': 18,
                              'point-of-sale systems': 19,
                              'warehouse robots': 20,
                              'televisions': 21,
                              'water services': 22,  # non-building
                              'telecom systems': 23  # non-building
                              }

        self.fueldict = {'electricity': 1,
                         'natural gas': 2,
                         'distillate': 3,
                         'other fuel': (4, 5, 6, 7, 8)
                         }
        # Other fuel includes residual oil (4), propane (5), steam from coal (6),
        # motor gasoline (7), and kerosene (8)

        self.demand_typedict = {'windows conduction': 'WIND_COND',
                                'windows solar': 'WIND_SOL',
                                'wall': 'WALL',
                                'roof': 'ROOF',
                                'ground': 'GRND',
                                'floor': 'FLOOR',
                                'infiltration': 'INFIL',
                                'ventilation': 'VENT',
                                'people gain': 'PEOPLE',
                                'equipment gain': 'EQUIP',
                                'lighting gain': 'LIGHTS',
                                'other heat gain': 'REFRIG'
                                }


def json_interpreter(key_series):
    """Convert strings in JSON database into codes for data extraction.

    From a list of strings acquired from the JSON database, this
    function converts them into a format that can be used to extract
    data from the applicable array.

    This function is configured with the assumption that the keys are
    provided in the order: census division, building type, fuel type,
    and end use (and optionally MEL type or 'demand' and demand type).
    This function reverses fuel type and end use to be in the order
    used in the EIA data files.

    Args:
        key_series (list): A list of strings assembled by the walk
            function representing the definition of a leaf node in
            the microsegments JSON data structure.

    Returns:
        A list of numbers and (sometimes) strings that are used to
        extract data from the relevant files. There may be up to four
        numeric entries in the first four positions in the list,
        specifying the census division, building type, fuel type,
        and end use, with a fifth position occupied by a string or
        number in the case of demand or MELs data, respectively.
    """

    # Create an instance of the commercial data translation dicts object
    # to be able to use the translation dicts
    cd = CommercialTranslationDicts()

    # Separate handling for key_series for square footage data, where
    # key_series has only three entries, and complete microsegments,
    # which have at least four entries
    if 'total square footage' in key_series or \
       'new square footage' in key_series:
        # Set up a list of dict names for the square footage data,
        # which are only specified on a census division and building
        # type basis
        dict_names = [cd.cdivdict, cd.bldgtypedict]

        # Replicate key_series as keys
        keys = key_series
    else:
        # Create a copy of key_series that can be modified without
        # changing the original contents in key_series
        keys = key_series.copy()

        # Since the JSON database is formatted with fuel type before
        # end use, switch the order of the end use and fuel type
        # entries in the keys list
        keys[2], keys[3] = keys[3], keys[2]

        # Set up list of dict names in the order specified in the
        # function docstring
        dict_names = [cd.cdivdict, cd.bldgtypedict, cd.endusedict, cd.fueldict]

    # Convert keys from the JSON into a new list using the translation
    # dicts defined at the top of this file
    interpreted_values = []
    for idx, dict_name in enumerate(dict_names):
        interpreted_values.append(dict_name[keys[idx]])

    # If the end use is heating or cooling, either demand or supply
    # will be specified in the 5th position in the list; if demand is
    # indicated, the demand component should be included in the output
    if 'demand' in keys:
        # Interpret the demand component specified and append to the list
        interpreted_values.append(cd.demand_typedict[keys[5]])

    # If the end use is miscellaneous electric loads ('MELs'),
    # keys will have one additional entry, which should be
    # processed against the dict 'mels_techdict'
    if 'MELs' in keys:
        # MELs "other" captures the total "other" electricity not reported
        # as a specific MEL device under MiscElConsump in the data; this
        # case should extract the total "other" to be adjusted later to
        # deduct the electricity under specific MELs
        if not keys[4] == 'other':
            # Interpret the MEL type specified and append to the list
            interpreted_values.append(cd.mels_techdict[keys[4]])

    return interpreted_values


def sd_mseg_percent(sd_array, sel, yrs):
    """Calculate technology-specific fractions of energy use in a microsegment.

    This function uses the technology type, vintage, and construction
    status/type reported in SDOUT into percentage energy use each year
    associated with each technology type. Technology types are not
    determined using the technology type numbers provided in SDOUT,
    but rather using a regex search of the 'Description' field in the
    data, since the technology type numbers are sometimes used for
    multiple technologies, based on an inspection of the technology
    description text (this is especially true with lighting). This
    function is called for unique combinations of census divisions,
    building types, end uses, and fuel types, but only in the cases
    where the end use has available service demand data.

    Args:
        sd_array (numpy.ndarray): Service demand data for commercial
            building equipment, specified by technology, building
            vintage, performance level, and the other microsegment
            parameters that appear in 'sel'.
        sel (list): A list of integers that specifies the desired
            census division, building type, end use, and fuel type.
        yrs (list): A list of integers representing the range of years
            common to all of the AEO data, precalculated for speed.

    Returns:
        A numpy array of the fractional contribution to energy in the
        specified microsegment from each technology (row in the array)
        for each year (column in the array) in 'yrs'. Also, a list of
        technology names in the same order as the rows in the numpy array.
    """

    # Convert the years list from a list of integers to a list of strings
    yrs = [str(yr) for yr in yrs]

    # Filter service demand data based on the specified census
    # division, building type, end use, and fuel type
    filtered = sd_array[np.all([sd_array['r'] == sel[0],
                                sd_array['b'] == sel[1],
                                sd_array['s'] == sel[2],
                                sd_array['f'] == sel[3]], axis=0)]

    # Initialize list of rows to remove from 'filtered' based on a
    # regex search of the 'Description' text
    rows_to_remove = []

    # Replace technology descriptions in the array 'filtered' with
    # generalized names, removing any text describing the vintage or
    # efficiency level and preparing to delete placeholder rows
    # (placeholder rows are in the data as imported)
    for idx, row in enumerate(filtered):

        # Identify the technology name from the 'Description' column in
        # the data using a regex set up to match any text '.+?' that
        # appears before the first occurrence of one or more spaces
        # followed by a 2 and three other numbers (i.e., 2009 or 2035)
        tech_name = re.search(r'.+?(?=\s+2[0-9]{3})', row['Description'])

        # Also check the special case where the technology name is so
        # long that the year number is partially truncated at the end
        # of the string
        exc_tech_name = re.search(
            r'.+?(?=\s+2[0-9]{1,2}$)',
            row['Description'])

        # If the regex matched, overwrite the original description with
        # the matching text, which describes the technology without
        # scenario-specific text like '2003 installed base'
        if tech_name:
            filtered['Description'][idx] = tech_name.group(0)
        # Else check to see if the description indicates a placeholder
        # row, which should be deleted before the technologies are
        # summarized and returned from this function
        elif re.search('placeholder', row['Description']):
            rows_to_remove.append(idx)
        # Else check to see if the description is an empty string,
        # and if so, add it to the list of rows to remove
        elif re.search(r'^(?![\s\S])', row['Description']):
            rows_to_remove.append(idx)
        # Else check for a special case where the year in the
        # technology name sought by the tech_name regex didn't match
        # because the year in the name is partially truncated at
        # the end of the technology name string
        elif exc_tech_name:
            filtered['Description'][idx] = exc_tech_name.group(0)
        # Implicitly, if the text does not match either regex, it
        # is assumed that it does not need to be edited or removed

    # Delete the placeholder rows from the filtered array
    filtered = np.delete(filtered, rows_to_remove, 0)

    # Special filtering for lighting to drop special modifier text
    # in the descriptions of linear fluorescent bulb types (e.g.,
    # replace 'T8 F32 Commodity' with 'T8 F32') now that year
    # details have been removed
    if sel[2] == CommercialTranslationDicts().endusedict['lighting']:
        for idx, row in enumerate(filtered):
            # Identify linear fluorescent types
            tech_name = re.search('^(T[0-9] F[0-9]{2})', row['Description'])
            if tech_name:
                filtered['Description'][idx] = tech_name.group(0)

    # Because different technologies are sometimes coded with the same
    # technology type number (especially in lighting, where lighting
    # types are often differentiated by vintage and technology type
    # numbers), technologies must be identified using the simplified
    # names now recorded in the 'Description' field
    technames = list(np.unique(filtered['Description']))

    # Truncate the technology names to 43 characters to match the
    # truncated strings used for the cost, performance, and lifetime data
    trunc_technames = [entry[:43] for entry in technames]

    # Set up numpy array to store restructured data, in which each row
    # will correspond to a single technology
    tval, tval_pct = (
        np.zeros((len(trunc_technames), len(yrs))) for n in range(2))

    # Combine the data recorded for each unique technology
    for idx, name in enumerate(technames):

        # Extract entries for a given technology type number
        entries = filtered[filtered['Description'] == name]

        # Calculate the sum of all year columns and write it to the
        # appropriate row in the tval array (note that the recfn module
        # introduces the structured_to_unstructured function to
        # convert the structured array into a standard numpy array,
        # which allows the use of the .sum() function)
        tval[idx, ] = np.sum(recfn.structured_to_unstructured(
            entries[yrs], dtype='<f8'), axis=0)

        # Calculate the sum of all the year columns (service demand
        # values) weighted by the equipment efficiency for each equipment
        # type and performance level using the same recfn function used
        # for the service demand array 'tval'
        tval_pct[idx, ] = np.sum(recfn.structured_to_unstructured(
            entries[yrs], dtype='<f8')/entries['Eff'][:, np.newaxis], axis=0)

    # If at least one entry in tval_pct is non-zero (tval_pct.any() == True),
    # suppress any divide by zero warnings and calculate the percentage
    # contribution of each technology by year (since tval_pct is initially
    # a measure of absolute energy service weighted by equipment efficiency)
    if tval_pct.any():
        with np.errstate(divide='ignore', invalid='ignore'):
            tval_pct = tval_pct / np.sum(tval_pct, axis=0)
            tval_pct = np.nan_to_num(tval_pct)  # Replace nan from 0/0 with 0

    return (tval, tval_pct, trunc_technames)


def catg_data_selector(db_array, sel, section_label, yrs):
    """Extracts a specified subset from the commercial building data array.

    This function generally extracts a subset of the data available in
    the commercial building data file. The particular subset is based
    on type of data, indicated in the 'Label' column of the array and
    specified by the variable 'section_label', and the 'sel' variable,
    which specifies the desired census division and building type, and
    if applicable, end use/MEL type, and fuel type.

    Args:
        db_array (numpy.ndarray): An array of commercial building data,
            including total energy use by end use/fuel type and all
            MELs types, new and surviving square footage, and other
            parameters.
        sel (list): A list of integers that specifies the desired
            census division, building type, end use, and fuel type.
        section_label (str): The name of the particular data to be extracted.
        yrs (list): A list of integers representing the range of years
            common to all of the AEO data, precalculated for speed.

    Returns:
        A numpy structured array with columns for only the year and
        magnitude of the data corresponding to 'sel' and 'section_label'.
        The years are limited to only those that appear in 'yrs'.
    """

    # Filter main EIA commercial data array based on the relevant
    # section label, and then filter further based on the specified
    # division, building type, end use, and fuel type - unless the
    # section_label indicates square footage data, which are specified
    # by only census division and building type
    # Also separately handle other fuel types, which must be filtered
    # using a different method since multiple numeric indices for fuel type
    # are combined together
    if 'SurvFloorTotal' in section_label or 'CMNewFloorSpace' in section_label:
        filtered = db_array[np.all([db_array['Label'] == section_label,
                                    db_array['Division'] == sel[0],
                                    db_array['BldgType'] == sel[1]], axis=0)]
    elif isinstance(sel[3], tuple):  # Tuple of fuel type codes present
        filtered = db_array[np.all([db_array['Label'] == section_label,
                                    db_array['Division'] == sel[0],
                                    db_array['BldgType'] == sel[1],
                                    db_array['EndUse'] == sel[2]], axis=0)]
        filtered = filtered[np.isin(filtered['Fuel'], sel[3])]
        # Sum over all fuel types selected
        tyr = np.unique(filtered['Year'])
        filtered = np.array([(i, filtered[filtered['Year'] == i]['Amount'].sum()) for i in tyr],
                            dtype=[('Year', 'i4'), ('Amount', 'f8')])
    else:
        filtered = db_array[np.all([db_array['Label'] == section_label,
                                    db_array['Division'] == sel[0],
                                    db_array['BldgType'] == sel[1],
                                    db_array['EndUse'] == sel[2],
                                    db_array['Fuel'] == sel[3]], axis=0)]

    # Adjust years reported based on the pivot year
    filtered['Year'] = filtered['Year'] + UsefulVars().pivot_year

    # Further reduce the data by including only those years that are
    # common to all AEO data (based on the custom AEO metadata JSON)
    filtered = filtered[np.isin(filtered['Year'], yrs)]

    # From the filtered data, select only the two needed columns,
    # the year and the data
    desired_cols = filtered[['Year', 'Amount']]

    # Recast the year column as string type instead of integer, since
    # the years will become keys in the dicts output to the JSON, and
    # valid JSON cannot have integers are keys
    desired_cols = desired_cols.astype([('Year', 'U4'), ('Amount', '<f8')])

    return desired_cols


def data_handler(db_array, sd_array, load_array, key_series, sd_end_uses, yrs):
    """Restructure data for each terminal node in the microsegments JSON.

    At each leaf/terminal node in the microsegments JSON, this
    function is used to convert data from the source arrays into dicts
    to be written to the microsegments database at the current node.
    The applicable data is obtained for a given semi-microsegment
    (census division and building type for square footage data, and
    end use and fuel type for energy use data) from the commercial
    building energy data and, if applicable, the thermal load
    components and technology-specific performance (i.e., service
    demand) data.

    This function also converts the units of the energy data from
    TBTU (10^12 BTU) to MMBTU (10^6 BTU.)

    Args:
        db_array (numpy.ndarray): An array of commercial building data,
            including total energy use by end use/fuel type and all
            MELs types, new and surviving square footage, and other
            parameters.
        sd_array (numpy.ndarray): Service demand data for commercial
            building equipment, given by technology and performance level.
        load_array (numpy.ndarray): Thermal load components data
            (i.e., energy exchange between buildings and their
            surroundings through walls, foundations, etc.) for
            commercial buildings, specified by census division,
            building type, and heating/cooling season.
        key_series (list): The set of strings that describe the
            current terminal node in the JSON database for which data
            should be generated.
        sd_end_uses (list): The numbers corresponding to the end uses
            that have service demand data.
        yrs (list): A list of integers representing the range of years
            common to all of the AEO data, precalculated for speed.

    Returns:
        A dict with data appropriate for the current location in the
        JSON specified by 'key_series'.
    """

    def array_mult(dct, factor):
        scaled = {key: val * factor for key, val in dct.items()}
        return scaled

    # Convert the list of keys into a list of numeric indices that can
    # be used to select the appropriate data
    idx_series = json_interpreter(key_series)

    # Factor to convert commercial energy data from TBTU to MMBTU
    to_mmbtu = 1000000  # 1e6

    # Call the appropriate functions depending on the keys associated
    # with a given leaf node in the JSON database; each of the four
    # cases in this if/else structure require slightly different
    # handling due either to differences in the source array or post-
    # data-subset additional manipulation for the data to be in the
    # desired final format
    if 'demand' in key_series:
        # Get the data from DBOUT
        subset = catg_data_selector(db_array, idx_series, 'EndUseConsump', yrs)

        # The thermal load data end uses are coded as text strings 'HT'
        # and 'CL' instead of numbers; the numbers in idx_series are
        # thus converted to the appropriate strings
        if idx_series[2] == 1:
            idx_series[2] = 'HT'
        elif idx_series[2] == 2:
            idx_series[2] = 'CL'
        else:
            raise ValueError(
                'No thermal load data for end use ' + str(idx_series[2]))

        # Get the contribution of the particular thermal load component
        # for the current end use (heating or cooling), census division,
        # and building type (note that in the case of these thermal
        # load microsegments, the final field in idx_series has the
        # text to select the correct thermal load component column)
        tl_multiplier = load_array[np.all([
            load_array['CDIV'] == idx_series[0],
            load_array['BLDG'] == idx_series[1],
            load_array['ENDUSE'] == idx_series[2]],
            axis=0)][idx_series[-1]]
        # N.B. tl_multiplier is a 1x1 numpy array

        # Multiply together the thermal load multiplier and energy use
        # data and construct the dict with years as keys
        final_dict = {'energy': dict(zip(
            subset['Year'], subset['Amount'] * tl_multiplier * to_mmbtu)),
            'stock': 'NA'}
    elif 'MELs' in key_series:
        # Miscellaneous Electric Loads (MELs) energy use data are
        # stored in db_array in a separate section with a different
        # label 'MiscElConsump' and with the MEL technology number
        # coded in the 'EndUse' column. Since the MEL end use number
        # in the 'EndUseConsump' section is 10, but technology specific
        # in the 'MiscElConsump' section, the MEL-specific number is
        # written over the 10 in the 'EndUse' position in idx_series
        if not key_series[4] == 'other':
            idx_series[2] = idx_series[4]

            # Extract the data from DBOUT
            subset = catg_data_selector(db_array, idx_series, 'MiscElConsump',
                                        yrs)
        # Extract the total electricity listed as "other"
        else:
            # Extract the electricity "other" from DBOUT
            subset = catg_data_selector(db_array, idx_series, 'EndUseConsump',
                                        yrs)

        # Convert into dict with years as keys and energy as values
        final_dict = {'energy': dict(zip(subset['Year'],
                                         subset['Amount'] * to_mmbtu)),
                      'stock': 'NA'}
    elif 'new square footage' in key_series:
        # Extract the relevant data from DBOUT
        subset = catg_data_selector(db_array, idx_series, 'CMNewFloorSpace',
                                    yrs)

        # Convert into dict with years as keys and new square footage as values
        final_dict = dict(zip(subset['Year'],
                              subset['Amount']))
    elif 'total square footage' in key_series:
        # Extract the relevant data from DBOUT
        sub1 = catg_data_selector(db_array, idx_series, 'CMNewFloorSpace', yrs)
        sub2 = catg_data_selector(db_array, idx_series, 'SurvFloorTotal', yrs)

        # Combine the surviving floor space and new floor space
        # quantities and construct into final dict
        final_dict = dict(zip(sub1['Year'],
                              sub1['Amount'] + sub2['Amount']))
    elif idx_series[2] in sd_end_uses:
        # Extract the relevant data from DBOUT
        subset = catg_data_selector(db_array, idx_series, 'EndUseConsump', yrs)

        # Get percentage contributions for each equipment type that
        # appears in the service demand data
        [tech_sd, tech_pct, tech_names] = sd_mseg_percent(
            sd_array, idx_series, yrs)

        # Declare empty list to store dicts generated for each technology
        tech_dict_list = []

        # For each technology extracted from the service demand data,
        # multiply the corresponding row of data in tech_pct with the
        # total consumption for that end use and fuel type reported in
        # the 'Amount' column in subset, and in the same step, convert
        # the years and calculated technology-specific energy use data
        # into a dict; also report out absolute service demand values
        # for each technology under the 'stock' key
        for t_i in range(len(tech_pct)):
            tech_dict_list.append(
                {'energy': dict(zip(subset['Year'],
                                    tech_pct[t_i] *
                                    subset['Amount'] * to_mmbtu)),
                 'stock': dict(zip(subset['Year'],
                                   tech_sd[t_i]))})

        # The final dict should be {technology: {year: data, ...}, ...}
        final_dict = dict(zip(tech_names, tech_dict_list))
    else:
        # Regular case with no supply/demand separation or service demand data

        # Extract the desired data from the DBOUT array
        subset = catg_data_selector(db_array, idx_series, 'EndUseConsump', yrs)

        # Convert into dict with years as keys and energy as values
        final_dict = {'energy': dict(zip(subset['Year'],
                                         subset['Amount'] * to_mmbtu)),
                      'stock': 'NA'}

    # Return the dict that should end up at the leaf node in the exported JSON
    return final_dict


def walk(db_array, sd_array, load_array, sd_end_uses, json_db, years, key_list=[]):
    """ Proceed recursively through the microsegment data structure
    (formatted as a nested dict) to each leaf/terminal node in the
    structure, constructing a list of the applicable keys that define
    the location of the terminal node and then call the appropriate
    functions to process the imported data. """

    # Explore data structure from current level
    for key, item in json_db.items():

        # If there are additional levels in the dict, call the function
        # again to advance another level deeper into the data structure
        if isinstance(item, dict):
            walk(db_array, sd_array, load_array,
                 sd_end_uses, item, years, key_list + [key])

        # If a leaf node has been reached, check if the second entry in
        # the key list is one of the recognized building types, and if
        # so, finish constructing the key list for the current location
        # and obtain the data to update the dict
        else:
            if key_list[1] in CommercialTranslationDicts().bldgtypedict.keys():
                leaf_node_keys = key_list + [key]

                # Extract data from original data sources
                data_dict = data_handler(db_array, sd_array, load_array,
                                         leaf_node_keys, sd_end_uses, years)

                # Set dict key to extracted data
                json_db[key] = data_dict

    # Return filled database structure
    return json_db


def cleanup_calc(dr, cdiv, bld, years):
    """Fix double-counting of electricity use in MELs and other/unspecified end uses

    This function addresses double-counting of electricity use in two locations in
    commercial buildings.
    1. For all commercial building types except "unspecified", specific named MELs technologies
       are double-counted in the MELs "other" technology type.
    2. For the unspecified building type, the "water systems" and "telecom systems" MELs are
       double-counted in the "unspecified" end use (not MELs > other, which is not present for
       the unspecified building type).

    Args:
        dr (dict): Complete microsegments dict fully populated with residential
            and commercial energy and stock data (and building counts/floor areas).
        cdiv (str): Name of single census division.
        bld (str): Name of single commercial building type.
        years (dict_keys): Iterable of years present in the data.

    Returns:
        Updated microsegments dict with revised values for the census division
        and building type passed to the function.
    """

    # Instantiate temporary data structure
    zc = {k: 0 for k in years}

    # Obtain sum of all MEL technologies except "other"
    for mels in dr[cdiv][bld]['electricity']['MELs'].keys():
        if mels != 'other':
            zml = dr[cdiv][bld]['electricity']['MELs'][mels]['energy']
            # Sum dicts together
            # https://stackoverflow.com/a/46128481
            zc = reduce(reducer, [zc, zml])

    # Remove sum of all MELs from the correct location
    # Make values negative to effect subtraction
    zcneg = {k: -v for k, v in zc.items()}
    if bld != 'unspecified':
        # Remove sum of all specific named MELs from MELs > other
        dr[cdiv][bld]['electricity']['MELs']['other']['energy'] = reduce(
            reducer, [dr[cdiv][bld]['electricity']['MELs']['other']['energy'], zcneg])
    else:
        # Remove sum of all MELs from unspecified
        dr[cdiv][bld]['electricity']['unspecified']['energy'] = reduce(
            reducer, [dr[cdiv][bld]['electricity']['unspecified']['energy'], zcneg])

    return dr


def reducer(accumulator, element):
    """Sum an arbitrary collection of dictionaries

    https://stackoverflow.com/a/46128481

    Args:
        accumulator (dict): Dict to be updated with values from element.
        element (dict): Dict to be added to accumulator.

    Returns:
        Dict that is an element (key)-wise sum of the dicts provided.
    """
    for key, value in element.items():
        accumulator[key] = accumulator.get(key, 0) + value
    return accumulator


def double_count_cleanup(dr):
    """Manage cleanup of double-counted electricity use

    This function addresses two cases where electricity use is double-counted when the
    data are initially extracted from the EIA data files. This function orchestrates the
    correction, relying on helper functions to calculate the correct values.

    Args:
        dr (dict): Complete microsegments dict fully populated with residential
            and commercial energy and stock data (and building counts/floor areas).

    Returns:
        Full output dict with the same structure as the input argument.
    """

    # Create an instance of the commercial data translation dicts object
    # to be able to use the translation dicts
    cd = CommercialTranslationDicts()

    # Get the years included in the data
    yrs = dr[list(cd.cdivdict)[0]][list(cd.bldgtypedict)
                                   [0]]['new square footage'].keys()

    # Clean up the double-counted electricity use
    for cdiv in cd.cdivdict:
        for bld in cd.bldgtypedict:
            dr = cleanup_calc(dr, cdiv, bld, yrs)

    return dr


def dtype_eval(entry, prev_dtype=None):
    """Determine data type for a single value

    This function takes as an input an entry from a standard line (row)
    of a text or CSV file and determines its type (only string, float,
    or integer), returning the specified type, which can be added to a
    list to be used in creating a numpy structured array of the data.

    Args:
        entry (str): String corresponding to a single cell (row, column)
            in the data file being scanned.
        prev_dtype (str): Previously identified data type for the
            values in the same column.

    Returns:
        Data type string definition for 'entry.'
    """

    # Strip leading and trailing spaces off of string
    entry = entry.strip()

    if '.' in entry:
        dtype = 'f8'
    elif 'NA'.lower() in entry.lower():
        dtype = 'f8'
    elif re.search('[a-zA-Z]+', entry):  # At least one letter somewhere
        dtype = '<U50'  # Assumed to be no more than 50 characters
    else:
        dtype = 'i4'

    # Prevent float dtype set for the current column from reverting to int
    if prev_dtype == 'f8' and dtype == 'i4':
        dtype = 'f8'

    return dtype


def dtype_array(data_file_path, delim_char=',', hl=None):
    """Use the first two lines (generally) of a file to assess the data type.

    Using the csv module, read the header line of a text data file
    or, if specified, the first and third lines after skipping the
    header lines specified by variable 'hl'; read all subsequent lines.
    Use the first line to set the column names and the subsequent lines
    to determine the data type for each column.

    Args:
        data_file_path (str): The full path to the data file to be imported.
        delim_char (str, optional): The delimiting character, defaults to ','.
        hl (int, optional): The number of header lines to skip from the
            top of the file before reading data.

    Returns:
        A numpy structured array dtype definition, which takes the form
        of a list of tuples, where each tuple containing two entries, a
        column heading string, and a string specifying the data type
        for that column.
    """

    # Open the target CSV formatted data file
    with open(data_file_path) as thefile:

        # Read the text file, handling two cases: (1) a file with
        # NULL bytes and (2) a file with no NULL bytes. In the former
        # case, the loop inside csv.reader is used to detect NULL
        # characters and act appropriately (by removing them prior to
        # converting to a csv.reader object) if they are encountered.
        # The skipinitialspace option ensures proper reading of
        # double-quoted text strings in the AEO data that have the
        # delimiter inside them (e.g., cooking equipment descriptions).
        if '\0' in open(data_file_path).read():  # NULL bytes detected
            filecont = csv.reader((x.replace('\0', '') for x in thefile),
                                  delimiter=delim_char, skipinitialspace=True,
                                  escapechar='\\')
        else:  # No NULL bytes, proceed normally
            filecont = csv.reader(thefile,
                                  delimiter=delim_char, skipinitialspace=True,
                                  escapechar='\\')

        # Skip the specified number of extraneous leading lines in
        # the file that do not include the column headers
        if hl:
            for i in range(0, hl):
                next(filecont)

        # Extract header (first) row and remove leading and trailing
        # spaces from all entries
        header_names = [entry.strip() for entry in next(filecont)]

        # Skip the blank line between the header and the first row
        # of data in the ktek data file
        if hl:
            next(filecont)
            next(filecont)

        # Determine dtype using the second line of the file (since the
        # first line is a header row)
        dtypes = [dtype_eval(col) for col in next(filecont)]

        # Scan the rest of the file in case there are floating point
        # precision values not in the first row that would otherwise
        # be incorrectly typed as integers
        for row in filecont:
            if len(dtypes) == len(row):
                # Check if row consists entirely of empty strings
                if all(col == '' for col in row):
                    break
                dtypes = [dtype_eval(col, dtypes[idx])
                          for idx, col in enumerate(row)]

        # Combine data types and header names into list of tuples
        comb_dtypes = list(zip(header_names, dtypes))

        return comb_dtypes


def data_import(data_file_path, dtype_list, delim_char=',', hl=None, cols=[]):
    """Import data and convert to a numpy structured array.

    Read the contents of a data file with a header line and convert
    it into a numpy structured array using the provided dtype definition,
    skipping any non-conforming informational lines at the end of the
    file. If specified, skip lines at the beginning of the file, for the
    case where informational content appears there instead. Also support
    capture of only the specified columns from the original data file.

    Args:
        data_file_path (str): The full path to the data file to be imported.
        dtype_list (list): A list of tuples with each tuple containing two
            entries, a column heading string, and a string defining the
            data type for that column. Formatted as a numpy dtype list.
        delim_char (str, optional): The delimiting character, defaults to ','.
        hl (int, optional): The number of header lines to skip from the
            top of the file before reading data.
        cols (list): A list of numbers representing the indices for the
            positions of the columns retained in the dtype definition
            (and thus the columns to include from each row of the data).

    Returns:
        A numpy structured array of the imported data file with the
        columns specified by dtype_list.
    """

    # Open the target CSV formatted data file
    with open(data_file_path) as thefile:
        # For some cooking equipment descriptions in the service demand
        # data, 11 inches is encoded as 11", which by default leaves
        # the closing double-quote character in the description strings
        # while removing the " that denoted inches; by inserting an
        # escape character before the " denoting inches, the text will
        # be handled correctly by csv.reader
        if re.match('.*SDOUT', re.escape(str(data_file_path))):
            cont = thefile.read().replace('11"', '11\\"')
            thefile = io.StringIO(cont)

        # This use of csv.reader assumes that the default setting of
        # quotechar '"' is appropriate; the skipinitialspace option
        # ensures proper reading of double-quoted text strings in the
        # AEO data that have the delimiter inside them (e.g., cooking
        # equipment descriptions); the loop which csv.reader is called
        # is used to detect NULL characters and act appropriately (by
        # removing them prior to converting to a csv.reader object)
        # if they are encountered
        if '\0' in open(data_file_path).read():  # NULL bytes detected
            filecont = csv.reader((x.replace('\0', '') for x in thefile),
                                  delimiter=delim_char, skipinitialspace=True,
                                  escapechar='\\')
        else:  # No NULL bytes, proceed normally
            filecont = csv.reader(thefile,
                                  delimiter=delim_char, skipinitialspace=True,
                                  escapechar='\\')

        # Create list to be populated with tuples of each row of data
        # from the data file
        data = []

        # Skip first line of the file
        next(filecont)

        # If a number of header lines to skip (variable 'hl') is
        # specified, skip those lines, plus one to accommodate
        # the empty line between the header line and the first
        # row of data in the ktek file (which is the intended
        # target for these lines of code).
        if hl:
            for i in range(0, hl + 1):
                next(filecont)

        # Import the data, skipping lines that are not the correct length
        for row in filecont:
            if len(tuple(row)) == len(dtype_list):
                data.append(tuple(row))
            # If there are specific columns of interest specified, select
            # only those columns from the row of data and append the result
            elif cols:
                shorter = [row[i] for i in cols]
                data.append(tuple(shorter))

        # Convert data into numpy structured array, using the
        # try/catch in the case where the data include the string 'NA',
        # which has to be changed to an 'nan' to be able to be coerced
        # to a float or integer by np.array
        for r_i, row in enumerate(data):
            for f_i, (field, (_, np_type)) in enumerate(zip(row, dtype_list)):
                if field == '' and np.issubdtype(np_type, np.integer):
                    print(f"⚠️  Empty int at row {r_i+1}, col {f_i} ")

        try:
            final_struct = np.array(data, dtype=dtype_list)
        # Targeted error "ValueError: could not convert string to float: 'NA'"
        except ValueError:
            for i, row in enumerate(data):
                row = list(row)  # Make row mutable
                for k, entry in enumerate(row):
                    # Replace 'NA' with 'nan'
                    if entry == 'NA':
                        row[k] = 'nan'
                # Overwrite existing tuple with new tuple
                data[i] = tuple(row)
            # With the 'NA' strings replaced, create the numpy array as
            # originally desired
            final_struct = np.array(data, dtype=dtype_list)

        return final_struct


def str_cleaner(data_array, column_name, return_str_len=False):
    """Clean up formatting of technology description strings in imported data.

    In the imported EIA data, the strings that describe the technology
    and performance level have inconsistent formatting and often have
    leading or trailing spaces that make later string matching to link
    data together difficult. This function edits those strings to have
    consistent formatting and removes unusual formatting of special
    characters and extraneous double quotes.

    Args:
        data_array (numpy.ndarray): A numpy structured array of imported data.
        column_name (str): The name of the column in data_array to edit.
        return_str_len (bool): If true, this function returns an
            additional integer used for string truncation.

    Returns:
        The input array with the strings in column_name revised.
        If return_str_len is true, then the function also returns an
        integer for the string length to use to truncate the cooking
        technology strings from ktek (the technology cost, performance,
        and lifetime data file) to match the length of the modified
        technology strings in SDOUT (the service demand data) when
        combining those data.
    """

    def special_character_handler(text_string):
        """Edit special characters in strings to be written consistently.

        Args:
            text_string (str): A string describing a particular technology.

        Returns:
            The edited text string and the string truncation length,
            explained in the parent function docstring.
        """

        # Replace 'SodiumVapor' with 'Sodium Vapor'
        text_string = re.sub('SodiumVapor', 'Sodium Vapor', text_string)

        # Check to see if an HTML character reference ampersand or
        # double-quote, or standard double-quote character is in
        # the string
        html_ampersand_present = re.search('&amp;', text_string)
        html_double_quote_present = re.search('&quot;', text_string)
        double_quote_present = re.search('\"', text_string)

        # For data matching purposes, replace the ampersand and quote
        # symbols with consistent characters/strings and eliminate the
        # use of the standalone double-quote character
        if html_ampersand_present:
            text_string = re.sub('&amp;', '&', text_string)
            str_trunc_len = 50  # Not used in com_mseg_tech
        elif html_double_quote_present:
            text_string = re.sub('&quot;', '-inch', text_string)
            str_trunc_len = 43
        elif double_quote_present:
            text_string = re.sub('\"', '-inch', text_string)
            str_trunc_len = 48
        else:
            str_trunc_len = 50

        return text_string, str_trunc_len

    # Store the indicated string truncation lengths in a list
    str_trunc_list = []

    # Check for double quotes in the first entry in the specified column
    # and, assuming all entries in the column are the same, revise all
    # of the entries using the appropriate procedure for the formatting
    if re.search('(?<=\")([^\"]+)', data_array[column_name][0]):
        # Operate on each row in the specified column of the structured array
        for row_idx, entry in enumerate(data_array[column_name]):

            # Delete leading and trailing spaces
            entry = entry.strip()

            # Delete quotes (should now be first and last characters of string)
            entry = entry[1:-1]

            # Clean up strings with special characters to ensure that
            # these characters appear consistently across all imported data
            entry, str_trunc_len = special_character_handler(entry)

            # Record string truncation length
            str_trunc_list.append(str_trunc_len)

            # Delete any newly "apparent" (no longer enclosed by the double
            # quotes) trailing or (unlikely) leading spaces and replace the
            # original entry
            data_array[column_name][row_idx] = entry.strip()

    else:
        # Operate on each row in the specified column of the structured array
        for row_idx, entry in enumerate(data_array[column_name]):

            # Clean up strings with special characters to ensure that
            # these characters appear consistently across all imported data
            entry, str_trunc_len = special_character_handler(entry)

            # Record string truncation length
            str_trunc_list.append(str_trunc_len)

            # Delete any leading and trailing spaces
            data_array[column_name][row_idx] = entry.strip()

    # Clean up indicated string truncation lengths, discarding 50
    str_trunc_list = list(set(str_trunc_list))
    str_trunc_list = [x for x in str_trunc_list if x != 50]
    if len(str_trunc_list) > 1:
        # If this condition has been satisfied, both '&quot;' and
        # '"' were present in the technology description strings
        # in the imported text, which suggests a single truncation
        # length might not work to match the strings in these data
        text = ('Warning: undesired behavior might occur when '
                'attempting to match technology characteristics '
                'data (ktek) with service demand data (sdout).')
        print(text)

    # Return the appropriate objects based on the return_str_len option
    if return_str_len:
        try:
            # Obtain standalone integer from list
            str_trunc_len_final = str_trunc_list[0]
        except IndexError:
            # If the list is empty, all of the truncation lengths were
            # equal to 50, so set the truncation length to 50
            str_trunc_len_final = 50
        return data_array, str_trunc_len_final
    else:
        return data_array


def onsite_prep(generation_file):
    """ Preps the onsite generation file for commercial
    by adding together all technologies by segment and
    converting building and census division names to
    stings for easier querying"""

    bldgtypedict = {'Assembly': 'assembly',
                    'Education': 'education',
                    'Food Sales': 'food sales',
                    'Food Service': 'food service',
                    'Health Care': 'health care',
                    'Lodging': 'lodging',
                    'Office-Large': 'large office',
                    'Office-Small': 'small office',
                    'Merc/Service': 'mercantile/service',
                    'Warehouse': 'warehouse',
                    'Other': 'other'
                    }

    # Read in AEO's onsite generation file
    gen_dtypes = dtype_array(generation_file)
    gen_dtypes[1] = ('Year', '<U50')
    gen_data = data_import(generation_file, gen_dtypes)

    # Pull all the unique microsegment combinations
    years = np.unique(gen_data['Year'])
    div = np.unique(gen_data['Division'])
    bld = np.unique(gen_data['BldgType'])

    # Define datatypes of OwnUse aggregated
    gen_dtypes = [('Year', '<U50'),
                  ('Division', '<i4'),
                  ('BldgType', '<U50'),
                  ('OwnUse', '<f8')]

    # Sum all onsite generation by microsegment
    gen_data = np.array([(i, j, k, gen_data[(gen_data['Year'] == i) &
                                            (gen_data['Division'] == j) &
                                            (gen_data['BldgType'] == k)][
                                                'OwnUse'].sum())
                         for i in years for j in div
                         for k in bld], dtype=gen_dtypes)

    # Factor to convert commercial energy data from TBTU to MMBTU
    to_mmbtu = 1000000  # 1e6

    # Convert census division to names
    cdiv_dct = {str(v): k for k, v in
                CommercialTranslationDicts().cdivdict.items()}

    gen_dtypes = [('Year', '<U50'), ('Division', '<U50'),
                  ('BldgType', '<U50'),
                  ('OwnUse', '<f8')]
    gen_data = gen_data.astype(gen_dtypes)

    # Unit conversion of TBTU to MMBTU
    gen_data['OwnUse'] = gen_data['OwnUse'] * to_mmbtu

    def name_map(data_array, trans_dict):
        newArray = np.copy(data_array)
        for k, v in trans_dict.items():
            newArray[data_array == k] = v
        return newArray

    gen_data['Division'] = name_map(gen_data['Division'], cdiv_dct)
    gen_data['BldgType'] = np.char.rstrip(gen_data['BldgType'])
    gen_data['BldgType'] = name_map(gen_data['BldgType'], bldgtypedict)

    return gen_data


def onsite_calc(generation_file, json_results):
    """ Calculates net electricity use using EIA's pre-2021 methodology
    and adds a new PV technology type. """

    def array_mult(dct, factor):
        scaled = {key: val * factor for key, val in dct.items()}
        return scaled

    def onsite_pull(cdiv, bld):
        pull = generation_file[np.all([generation_file['Division'] == cdiv,
                                       generation_file['BldgType'] == bld],
                                      axis=0)]
        years = np.unique(pull['Year'])
        pull = dict([(i, pull[pull['Year'] == i]['OwnUse'].sum())
                     for i in years])
        pull = array_mult(pull, -1)
        return pull

    # Pull the onsite generation by census division and building type
    cdiv = np.unique(generation_file['Division'])
    bldtype = np.unique(generation_file['BldgType'])

    for div in cdiv:
        for bld in bldtype:
            gen = onsite_pull(div, bld)

            # Add onsite generation as new end use
            elec_slice = json_results[div][bld]['electricity']
            elec_slice['onsite generation'] = {}
            elec_slice['onsite generation']['energy'] = gen
            elec_slice['onsite generation']['stock'] = 'NA'

    return json_results


def main():
    """ Import input data files and do other things """

    # Instantiate objects that contain useful variables
    handyvars = UsefulVars()
    eiadata = EIAData()

    # Import EIA AEO 'SDOUT' service demand file
    serv_dtypes = dtype_array(eiadata.serv_dmd)
    serv_data = data_import(eiadata.serv_dmd, serv_dtypes)
    serv_data = str_cleaner(serv_data, 'Description')

    # Import EIA AEO 'DBOUT' additional data file
    catg_dtypes = dtype_array(eiadata.catg_dmd)
    catg_data = data_import(eiadata.catg_dmd, catg_dtypes)
    catg_data = str_cleaner(catg_data, 'Label')

    # Import thermal loads data
    load_dtypes = dtype_array(handyvars.com_tloads, '\t')
    load_data = data_import(handyvars.com_tloads, load_dtypes, '\t')

    # Import and process onsite generation from DGENOUT.txt
    onsite_gen = onsite_prep(eiadata.com_generation)

    # Not all end uses are broken down by equipment type and vintage in
    # SDOUT; determine which end uses are present so that the service
    # demand data are not explored unnecessarily when they are not even
    # available for a particular end use
    serv_data_end_uses = np.unique(serv_data['s'])

    # Import metadata generated based on EIA AEO data files
    with open(handyvars.aeo_metadata, 'r') as metadata:
        metajson = json.load(metadata)

    # Define years vector using year data from metadata
    years = list(range(metajson['min year'], metajson['max year'] + 1))

    # Import empty microsegments JSON file and traverse database structure
    try:
        with open(handyvars.json_in, 'r') as jsi, open(handyvars.json_out,
                                                       'w') as jso:
            msjson = json.load(jsi)

            # Proceed recursively through database structure
            result = walk(catg_data, serv_data, load_data,
                          serv_data_end_uses, msjson, years)

            # Clean up double-counted unspecified and other energy use
            result = double_count_cleanup(result)

            # Add in onsite generation
            result = onsite_calc(onsite_gen, result)

            # Write the updated dict of data to a new JSON file
            json.dump(result, jso, indent=2)

    except FileNotFoundError:
        errtext = ('Confirm that the expected residential data file ' +
                   handyvars.json_in + ' has already been created and '
                   'is in the current directory.\n')
        print(errtext)


if __name__ == '__main__':
    main()
