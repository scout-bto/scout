#!/usr/bin/env python3

import re
import numpy
import json
import argparse
import csv
from scout import mseg_techdata as rmt
from scout.config import FilePaths as fp


class EIAData(object):
    """Class of variables naming the EIA data files to be imported.

    Attributes:
        res_energy (str): The file name for the AEO residential energy
            and stock data.
    """
    def __init__(self, data_dir=fp.INPUTS):
        self.res_energy = data_dir / "RDM_DBOUT.txt"
        self.res_generation = data_dir / "RDM_DGENOUT.txt"


class UsefulVars(object):
    """Class of variables that would otherwise be global.

    Attributes:
        json_in (str): JSON file containing the structure to be populated
            with AEO data.
        json_out (str): FIlename of the JSON file to be produced with
            residential energy use, building stock, and equipment stock
            data added.
        res_tloads (str): Filename for the residential building thermal
            load components data.
        aeo_metadata (str): File name for the custom AEO metadata JSON.
        unused_supply_re (str): A string usable as a regular expression
            defining the parameters (and thus the corresponding rows)
            from the AEO data that are not needed for the "supply"
            (i.e., equipment) energy and stock data. The two letter
            codes represent: (Switch From | Switch To | Fuel Pumps).
        unused_demand_re (str): A string usable as a regular expression
            defining the parameters (and thus the corresponding rows)
            from the AEO data that should be retained to calculate the
            demand (i.e., envelope) energy and stock data. Because the
            demand only applies to heating and cooling, this regex is
            configured to exclude every row not coded with one of the
            two letter codes given. These codes represent:
            (Heating | Cooling | Secondary Heating).
    """

    def __init__(self):
        self.json_in = fp.INPUTS / 'microsegments.json'
        self.json_out = fp.INPUTS / 'mseg_res_cdiv.json'
        self.res_tloads = fp.THERMAL_LOADS / 'Res_TLoads_Final.txt'
        self.aeo_metadata = fp.METADATA_PATH
        self.unused_supply_re = r'^\(b\'(SF|ST |FP).*'
        self.unused_demand_re = r'^\(b\'(?!(HT|CL|SH)).*'


class SkipLines(object):
    """Class of variables that would otherwise be global.

    Attributes:
        json_in (str): Filename for empty input JSON with the structure
            to be populated with AEO data.
        json_out (str): Filename for JSON with residential building data added.
        aeo_metadata (str): File name for the custom AEO metadata JSON.
    """
    def __init__(self, aeo_import_year, aeo_versions):
        self.aeo_import_year = aeo_import_year
        if self.aeo_import_year == 2015:
            self.nlt_cp_skip_header = 20
            self.nlt_l_skip_header = 19
            self.lt_skip_header = 35
            self.lt_skip_footer = 54
        elif self.aeo_import_year in [2016, 2017, 2018]:
            self.nlt_cp_skip_header = 25
            self.nlt_l_skip_header = 20
            self.lt_skip_header = 37
            if aeo_import_year in [2016, 2017]:
                self.lt_skip_footer = 54
            else:
                self.lt_skip_footer = 52
        elif self.aeo_import_year in [2019, 2022]:
            self.nlt_cp_skip_header = 2
            self.nlt_l_skip_header = 2
            self.lt_skip_header = 37
            self.lt_skip_footer = 52
        elif self.aeo_import_year in [2020, 2021, 2023, 2025, None]:
            self.nlt_cp_skip_header = 2
            self.nlt_l_skip_header = 2
            self.lt_skip_header = 37
            self.lt_skip_footer = 51

# Define a series of dicts that will translate imported JSON
# microsegment names to AEO microsegment(s)


# Census division dict
cdivdict = {'new england': 1,
            'mid atlantic': 2,
            'east north central': 3,
            'west north central': 4,
            'south atlantic': 5,
            'east south central': 6,
            'west south central': 7,
            'mountain': 8,
            'pacific': 9
            }

# Building type dict (residential)
bldgtypedict = {'single family home': 1,
                'multi family home': 2,
                'mobile home': 3
                }

# Fuel type dict
fueldict = {'electricity (on site)': 'SL',
            'electricity': 'EL',
            'natural gas': 'GS',
            'distillate': 'DS',
            'other fuel': ('LG', 'KS', 'CL', 'GE', 'WD')
            }
# Note that currently in RESDBOUT.txt, electric resistance heaters are
# categorized under GE (geothermal) fuel. Fuel types "SL" and "NG" have
# been removed from the "other fuel" category. "SL" (solar) fuel
# corresponds to solar insolation for solar water heating, and is only
# associated with the "SOLAR" technology type. "NG" is only used by the
# "FP" end use, and in an attempt to avoid problems later if EIA
# changes their natural gas fuel type code to "NG" from "GS", it is
# also left out of the "other fuel" definition.

# # End use dict
# endusedict = {'total square footage': 'SQ',  # AEO reports ft^2 as an end use
#               'new homes': 'HS',
#               'total homes': 'HT',
#               'heating': 'HT',
#               'secondary heating': 'SH',
#               'cooling': 'CL',
#               'fans and pumps': 'FF',
#               'ceiling fan': 'CFN',
#               'lighting': 'LT',
#               'water heating': 'HW',
#               'refrigeration': 'RF',
#               'cooking': 'CK',
#               'drying': 'DR',
#               'TVs': {'TV': 'TVS',
#                       'set top box': 'STB',
#                       'DVD': 'DVD',
#                       'home theater and audio': 'HTS',
#                       'video game consoles': 'VGC'},
#               'computers': {'desktop PC': 'DPC',
#                             'laptop PC': 'LPC',
#                             'monitors': 'MON',
#                             'network equipment': 'NET'},
#               'other': {'clothes washing': 'CW',
#                         'dishwasher': 'DW',
#                         'freezers': 'FZ',
#                         'rechargeables': 'BAT',
#                         'coffee maker': 'COF',
#                         'dehumidifier': 'DEH',
#                         'electric other': 'EO',
#                         'microwave': 'MCO',
#                         'pool heaters and pumps': 'PHP',
#                         'security system': 'SEC',
#                         'portable electric spas': 'SPA',
#                         'wine coolers': 'WCL',
#                         'other appliances': 'OA'}}

# End use dict with revised MELs breakout introduced in AEO 2022
endusedict = {'total square footage': 'SQ',  # AEO reports ft^2 as an end use
              'new homes': 'HS',
              'total homes': 'HT',
              'heating': 'HT',
              'secondary heating': 'SH',
              'cooling': 'CL',
              'fans and pumps': 'FF',
              'ceiling fan': 'CFN',
              'lighting': 'LT',
              'water heating': 'HW',
              'refrigeration': 'RF',
              'cooking': 'CK',
              'drying': 'DR',
              'TVs': {'TV': 'TVS',
                      'set top box': 'STB',
                      'home theater and audio': 'HTS',
                      'OTT streaming devices': 'OTT',
                      'video game consoles': 'VGC'},
              'computers': {'desktop PC': 'DPC',
                            'laptop PC': 'LPC',
                            'monitors': 'MON',
                            'network equipment': 'NET'},
              'other': {'clothes washing': 'CW',
                        'dishwasher': 'DW',
                        'freezers': 'FZ',
                        'rechargeables': 'BAT',
                        'coffee maker': 'COF',
                        'dehumidifier': 'DEH',
                        'electric other': 'EO',
                        'small kitchen appliances': 'KIT',
                        'microwave': 'MCO',
                        'smartphones': 'PHN',
                        'pool heaters': 'PLH',
                        'pool pumps': 'PLP',
                        'security system': 'SEC',
                        'portable electric spas': 'SPA',
                        'smart speakers': 'SPK',
                        'tablets': 'TAB',
                        'wine coolers': 'WCL',
                        'other appliances': 'OA'}}

# Technology types (supply) dict
technology_supplydict = {'solar WH': 'SOLAR_WH',
                         'electric WH': 'ELEC_WH',
                         'total homes (tech level)': 'ELEC_RAD',
                         'resistance heat': 'ELEC_RAD',
                         'ASHP': 'ELEC_HP',
                         'GSHP': 'GEO_HP',
                         'central AC': 'CENT_AIR',
                         'room AC': 'ROOM_AIR',
                         'linear fluorescent (T-12)': ('LFL', 'T12'),
                         'linear fluorescent (T-8)': ('LFL', 'T-8'),
                         'linear fluorescent (LED)': ('LFL', 'LED'),
                         'general service (incandescent)': ('GSL', 'Inc'),
                         'general service (CFL)': ('GSL', 'CFL'),
                         'general service (LED)': ('GSL', 'LED'),
                         'reflector (incandescent)': ('REF', 'Inc'),
                         'reflector (CFL)': ('REF', 'CFL'),
                         'reflector (halogen)': ('REF', 'HAL'),
                         'reflector (LED)': ('REF', 'LED'),
                         'external (incandescent)': ('EXT', 'Inc'),
                         'external (CFL)': ('EXT', 'CFL'),
                         'external (high pressure sodium)': ('EXT', 'HPS'),
                         'external (LED)': ('EXT', 'LED'),
                         'furnace (NG)': 'NG_FA',
                         'boiler (NG)': 'NG_RAD',
                         'NGHP': 'NG_HP',
                         'furnace (distillate)': 'DIST_FA',
                         'boiler (distillate)': 'DIST_RAD',
                         'furnace (kerosene)': 'KERO_FA',
                         'furnace (LPG)': 'LPG_FA',
                         'stove (wood)': 'WOOD_HT',
                         'resistance': 'GE2',
                         'secondary heater (kerosene)': 'KS',
                         'secondary heater (LPG)': 'LG',
                         'secondary heater (wood)': 'WD',
                         'secondary heater (coal)': 'CL',
                         'secondary heater': ''
                         }

# Technology types (demand) dict
technology_demanddict = {'windows conduction': 'WIND_COND',
                         'windows solar': 'WIND_SOL',
                         'wall': 'WALL',
                         'roof': 'ROOF',
                         'ground': 'GRND',
                         'infiltration': 'INFIL',
                         'people gain': 'PEOPLE',
                         'equipment gain': 'EQUIP'}

# Form residential dictlist for use in JSON translator
res_dictlist = [endusedict, cdivdict, bldgtypedict, fueldict,
                technology_supplydict, technology_demanddict]


def json_translator(dictlist, filterformat):
    """Determine filtering keys for finding information in the input data

    This function takes the list of keys corresponding to a location
    in the microsegments JSON (and thus the data to obtain from the
    EIA data file or thermal load components file) and converts it
    into a nested list of strings and integer values that can be
    used to obtain the desired data from those files.

    The translation from the human-readable text strings from the
    microsegments JSON into the values to be used with the input
    data source files is facilitated by the translation dicts
    passed to the function.

    This function also facilitates the combination of data by
    indicating e.g., multiple fuel types for an end use and
    technology type to consolidate the energy use and stock for
    all of those fuel types under a single key series in the
    microsegments JSON.

    Args:
        dictlist (list): A list of the variable names for the dicts
            that relate the strings in the JSON to the codes in the
            EIA data files.
        filterformat (list): A list of strings corresponding to the
            current location in the microsegments JSON file.

    Returns:
        Nested list of string and numeric keys that correspond to the
        indices used in the EIA energy and stock data and the envelope
        load components data.
    """

    # Set base filtering list of lists (1st element supply filter, 2nd demand)
    json_translate = [[], '']

    # Set an indicator for whether a "demand" filtering element has been found
    # (special treatment)
    demand_indicator = 0

    # Set an indicator for whether the technology level is handled on the end
    # use level - i.e., set top boxes (special treatment)
    enduse_techlevel = 0

    # Set an indicator for what level in the microsegment hierarchy we are in:
    # 1) end use, 2) census division, 3) bldg type, 4) fuel type,
    # 5) "supply" tech type, 6) "demand" tech type)
    ms_level = 0

    # Restructure the filterformat variable in the case of a "total homes"
    # update, where "total homes" uses the same filter codes as a heating,
    # electricity, boiler (electric) microsegment in RESDBOUT,
    # but with the relevant data in the "HOUSEHOLDS" column
    if 'total homes' in filterformat and len(filterformat) == 3:
        filterformat = filterformat[0:2]
        filterformat.extend(['electricity', 'total homes',
                             'total homes (tech level)'])
    # Reduce dictlist as appropriate to filtering information (if not a
    # "demand", microsegment, remove "technology_demanddict" from dictlist;
    # if not a "supply" microsegment", remove "technology_supplydict" from
    # dictlist; if a microsegment with no technology level (i.e. water heating)
    # remove "technology_supplydict" and "technology_demanddict" from dictlist;
    # if a microsegment square footage or a new homes update, include only
    # "fueldict", "cdivdict", and "bldgtypedict" (square footage and new
    # homes are included on the fuel type level in the microsegments JSON).
    if 'demand' in filterformat:
        dictlist_loop = dictlist[:(len(dictlist) - 2)]
        dictlist_add = dictlist[-1]
        dictlist_loop.append(dictlist_add)
    elif 'total square footage' in filterformat and len(filterformat) == 3 or \
         'new homes' in filterformat and len(filterformat) == 3:
        dictlist_loop = dictlist[:(len(dictlist) - 3)]
    elif len(filterformat) <= 4:
        dictlist_loop = dictlist[:(len(dictlist) - 2)]
    else:
        dictlist_loop = dictlist[:(len(dictlist) - 1)]

    # Loop through "dictlist" and determine whether any elements of
    # "filterformat" input are in dict keys; if so, add key value to output
    for j in dictlist_loop:
        # Count key matches for given dict
        match_count = 0
        ms_level += 1
        for num, key in enumerate(filterformat):
            # Check whether element is in dict keys
            if key in j.keys():
                match_count += 1
                # "Demand" technologies added to 2nd element of filtering list
                if demand_indicator != 1:
                    # If there are more levels in a keyed item, go down branch
                    if isinstance(j[key], dict):
                        nextkey = filterformat[num + 1]
                        if nextkey in j[key].keys():
                            json_translate[0].append(j[key][nextkey])
                            # Update enduse_techlevel indicator
                            enduse_techlevel = 1
                    else:
                        json_translate[0].append(j[key])
                    break
                else:
                    if isinstance(j[key], dict):
                        nextkey = filterformat[num + 1]
                        if nextkey in j[key].keys():
                            json_translate[1] = str(j[key][nextkey])
                    else:
                        json_translate[1] = str(j[key])
                    break
            # Flag a "demand" microsegment
            elif key == 'demand':
                demand_indicator = 1
        # If there was no key match for given dict and we don't have special
        # case of a technology being handled on the end use level, raise error
        if (match_count == 0 and ms_level != (len(dictlist) - 1)) or \
           (match_count == 0 and ms_level == (len(dictlist) - 1) and
           enduse_techlevel == 0):
            raise (KeyError("Filter list element not found in dict keys!"))

    # Return updated filtering list of lists: [[supply filter],[demand filter]]
    return json_translate


def thermal_load_select(tl_data, sel):
    """Extract a specified thermal load component

    For the census division, building type, and end use specified,
    select the corresponding thermal load component factor/multiplier
    from the thermal load components array. The end uses specified
    for this function will be limited to either heating or cooling,
    given that those are the energy requirements related to the
    building envelope.

    Args:
        tl_data (numpy.ndarray): An array of thermal load component factors.
        sel (list): A nested list of indices for selecting the relevant
            data, created by json_translator.

    Returns:
        A scalar value corresponding to the thermal load component
        factor for the specified end use (heating or cooling),
        census division, and building type.
    """

    # Select the appropriate data from the thermal loads data array
    tl_data_sel = tl_data[numpy.all([tl_data['ENDUSE'] == sel[0][0],
                                     tl_data['CDIV'] == sel[0][1],
                                     tl_data['BLDG'] == sel[0][2]], axis=0)]

    # Extract the demand modifier value (the fraction of heating or
    # cooling load gained/lost through the relevant exterior surface)
    # in the appropriate column using the second value in 'sel'
    tloads_component = tl_data_sel[sel[1]][0]

    return tloads_component


def nrg_stock_select(data, sel):
    """Extract and restructure energy and stock data for a microsegment

    For the specific microsegment identified by 'sel,' this function
    extracts the corresponding energy use and equipment stock data
    from the EIA AEO data array and restructures it into dicts to be
    added to the output JSON database.

    In cases where there are multiple values reported for each year,
    this function will sum those values together such that the energy
    and stock data always have a single key for each year.

    Args:
        data (numpy.ndarray): An array of AEO energy, equipment stock,
            and household count data given by microsegment.
        sel (list): A nested list of indices for selecting the relevant
            data, created by json_translator.

    Returns:
        A dict for energy and a dict for stock data, with keys for
        each year of available data for the specified microsegment.
    """

    # Define initial stock and energy dicts
    group_stock = {}
    group_energy = {}

    # Select data for the specified census division and building type
    data_sel = data[numpy.all([data['CDIV'] == sel[0][1],
                               data['BLDG'] == sel[0][2]], axis=0)]

    # Multiple end uses can be provided, but try first to see if only
    # one end use is provided; if not, select data for all of the
    # end uses given
    if type(sel[0][0]) is not tuple:
        data_sel = data_sel[numpy.all(
            [data_sel['ENDUSE'] == sel[0][0]], axis=0)]
    else:
        data_sel = data_sel[numpy.hstack([numpy.where(
            data_sel['ENDUSE'] == i) for i in sel[0][0]]).flatten()]

    # Multiple fuel types can be provided, but try first to see if only
    # one fuel type is provided and if not, use a different approach to
    # select data for all of the fuel types indicated
    if type(sel[0][3]) is not tuple:
        data_sel = data_sel[numpy.all(
            [data_sel['FUEL'] == sel[0][3]], axis=0)]
    else:
        data_sel = data_sel[numpy.hstack([numpy.where(
            data_sel['FUEL'] == i) for i in sel[0][3]]).flatten()]

    # If an equipment class is specified, select the subset of
    # applicable data as appropriate
    try:
        eqp = sel[0][4]
    except IndexError:
        eqp = False

    if eqp:
        if isinstance(eqp, tuple):  # Lighting
            data_sel = data_sel[
                numpy.all([data_sel['EQPCLASS'] == eqp[0],
                           data_sel['BULBTYPE'] == eqp[1]], axis=0)]
        else:  # Other end uses
            data_sel = data_sel[
                numpy.all([data_sel['EQPCLASS'] == eqp], axis=0)]

    # Loop through the reduced numpy stock and energy array and
    # combine the reported values together
    for idx, row in enumerate(data_sel):
        # If data for the year is already present for the current
        # microsegment (as with microsegments that combine several
        # EIA categories together), add the new stock and consumption
        # values to the existing values (assume that if the year is
        # present in the group_stock dict it is also in group_energy)
        if row['YEAR'] in group_stock:
            # Record energy consumption and stock information
            # (change the year to a string to yield a valid
            # JSON dict, where all keys must be strings)
            group_stock[row['YEAR']] += row['EQSTOCK']
            group_energy[row['YEAR']] += row['CONSUMPTION']

        else:
            group_stock[row['YEAR']] = row['EQSTOCK']
            group_energy[row['YEAR']] = row['CONSUMPTION']

    # Convert the numeric year keys in the energy and stock dicts
    # to strings to be compatible with valid JSON
    group_stock = {str(key): value for key, value in group_stock.items()}
    group_energy = {str(key): value for key, value in group_energy.items()}

    return group_energy, group_stock


def sqft_homes_select(data, sel):
    """Extract and restructure home count or square footage for a microsegment

    Similar to nrg_stock_select, for the microsegment identified by
    'sel,' this function extracts the corresponding house count (total
    homes or new homes) or square footage from the EIA AEO data array
    and restructures it into dicts to be added to the output JSON
    database. The new homes and total square footage data are reported
    with separate end use codes in the AEO data file; the total homes
    values are reported in the "HOUSEHOLDS" column with the first end
    use, building type, and technology type in each census division.

    Args:
        data (numpy.ndarray): An array of AEO energy, equipment stock,
            and household count data given by microsegment.
        sel (list): A nested list of indices for selecting the relevant
            data, created by json_translator.

    Returns:
        A dict with keys for each year of data and the corresponding
        values indicated by the selection input variable 'sel.'
    """

    # Define initial square footage, new homes, or total homes lists
    if (endusedict['total square footage'] in sel[0] or
            endusedict['new homes'] in sel[0] or
            endusedict['total homes'] in sel[0]):
        group_out = {}
    else:
        raise ValueError('Unexpected housing stock filtering information!')

    # Select home count or square footage data based on selection indices
    if technology_supplydict['total homes (tech level)'] in sel[0]:
        data_sel = data[numpy.all([data['ENDUSE'] == sel[0][0],
                                   data['CDIV'] == sel[0][1],
                                   data['BLDG'] == sel[0][2],
                                   data['FUEL'] == sel[0][3],
                                   data['EQPCLASS'] == sel[0][4]], axis=0)]
    else:
        data_sel = data[numpy.all([data['ENDUSE'] == sel[0][0],
                                   data['CDIV'] == sel[0][1],
                                   data['BLDG'] == sel[0][2]], axis=0)]

    # Loop through the reduced numpy stock and energy (and ancillary
    # data) array and restructure the reported values
    for idx, row in enumerate(data_sel):
        if (endusedict['total square footage'] in sel[0] or
            (endusedict['total homes'] in sel[0] and
                technology_supplydict['total homes (tech level)'] in sel[0])):
            # Record square foot or total homes information
            # (from "HOUSEHOLDS" column in RESDBOUT)
            group_out[row['YEAR']] = row['HOUSEHOLDS']
        elif endusedict['new homes'] in sel[0]:
            # Record new homes information (from "EQSTOCK" column in RESDBOUT)
            group_out[row['YEAR']] = row['EQSTOCK']

    # Convert the numeric year keys in the selected home counts or
    # characteristics dicts to strings to be compatible with valid JSON
    group_out = {str(key): value for key, value in group_out.items()}

    return group_out


def list_generator(nrg_stock, tloads, filterdata, aeo_years, lt_factors):
    """Extract the desired energy, equipment stock, or household count data

    Given the data to be obtained, indicated by the keys from the
    current terminal node in the JSON dict structure, this function
    calls a function to convert those keys into the indices that can
    be used to obtain the desired data from the input data files and
    then calls the appropriate helper function to extract those data
    from the energy and stock or thermal load component arrays.

    This function also includes some data setup and special handling
    for the lighting data because the lighting energy use data are
    reported only for the first bulb type for each fixture type.

    Args:
        nrg_stock (numpy.ndarray): An array of AEO energy, equipment
            stock, and household count data given by microsegment.
        loads (numpy.ndarray): An array of thermal load component factors.
        filterdata (list): A list of keys from the microsegments JSON
            indicating the data to be obtained.
        aeo_years (int): The number of years of data reported in the
            RESDBOUT file.
        lt_factors (numpy.ndarray): A numpy structured array with
            lighting efficiency and stock weighted factors to be used
            to break out the lighting energy use data by bulb type.

    Returns:
        In general, this function returns stock and energy dicts,
        though for the demand (envelope component thermal loads)
        microsegments, no stock applies. This function will also
        return a house count or total square footage dict if indicated
        by the JSON keys (in 'filterdata').
    """

    # Find the corresponding text filtering information
    txt_filter = json_translator(res_dictlist, filterdata)

    # Specify the lighting fixture and bulb types with lighting
    # energy data reported, in a format consistent with the output
    # from json_translator, handling the difference in the bulb
    # type string for incandescents between the AEO 2015 and 2017
    # data; this approach might merit revisiting later
    if aeo_years in [42, 36, 31]:  # AEO 2017- formatting
        lt_with_energy = [('GSL', 'INC'), ('LFL', 'T12'),  # AEO 2017-
                          ('REF', 'INC'), ('EXT', 'INC')]
    else:  # AEO 2015 formatting
        lt_with_energy = [('GSL', 'Inc'), ('LFL', 'T12'),
                          ('REF', 'Inc'), ('EXT', 'Inc')]

    # If the end use is lighting, create and prepare an additional
    # text filter for extracting the energy data from the lighting
    # type that has energy data
    lt_nrg_index = ['GSL', 'LFL', 'REF', 'EXT']
    addl_txt_filter = None
    if 'lighting' in filterdata:
        if txt_filter[0][4] not in lt_with_energy:
            # Obtain the lighting tuple for the text filter that
            # matches same fixture type, but for the bulb type that
            # has energy data reported
            new_lt_filt = lt_with_energy[lt_nrg_index.index(
                txt_filter[0][4][0])]

            # Construct a new text filter using the lighting type
            # that has data available, and avoiding the use of
            addl_txt_filter = txt_filter[0][:4]
            addl_txt_filter.append(new_lt_filt)
            addl_txt_filter = [addl_txt_filter, txt_filter[1]]

    # Call the appropriate input data selection function and return
    # the desired result based on the type of data requested
    if 'demand' in filterdata:
        # Find baseline heating or cooling energy microsegment (before
        # application of load component); establish reduced numpy array
        group_energy_base, group_stock = nrg_stock_select(
            nrg_stock, txt_filter)

        # Given the discovered lists of energy/stock values, ensure
        # length is equal to the number of years currently projected
        # by AEO. If not, and the list isn't empty, trigger an error.
        if len(group_energy_base) is not aeo_years:
            if len(group_energy_base) != 0:
                raise (ValueError('Error in length of discovered list!'))

        # If the end use is secondary heating, change the end use
        # in the filter to 'HT' from 'SH', because both primary and
        # secondary heating are coded as 'HT' in the thermal loads file
        if txt_filter[0][0] == 'SH':
            txt_filter[0][0] = 'HT'

        # Find/return appropriate thermal loads component factor
        tloads_component = thermal_load_select(tloads, txt_filter)

        # Apply component value to baseline energy values for final list
        group_energy = {key: val * tloads_component
                        for key, val in group_energy_base.items()}

        # Return combined energy use values and updated version of EIA demand
        # data and thermal loads data with already matched data removed
        return {'stock': 'NA', 'energy': group_energy}

    elif 'total square footage' in filterdata or 'new homes' in filterdata or \
         'total homes' in filterdata:
        # Given input numpy array and 'compare from' list, return sq. footage
        # projection lists and reduced numpy array (with matched rows removed)
        group_sqft_homes = sqft_homes_select(nrg_stock, txt_filter)

        # Given the discovered lists of sq. footage values, ensure
        # length is equal to the number of years currently projected
        # by AEO. If not, and the list isn't empty, trigger an error.
        if len(group_sqft_homes) is not aeo_years:
            if len(group_sqft_homes) != 0:
                raise (ValueError('Error in length of discovered list!'))

        # Return sq. footage values and updated version of EIA
        # supply data with already matched data removed
        return group_sqft_homes

    else:
        # For lighting, obtain and correct the energy data and
        # separately obtain the stock data and do not delete
        # any data, as lighting energy data will need to be called
        # from the input array several times for each fixture type
        if 'lighting' in filterdata:
            # Determine whether the lighting energy information will
            # need to be obtained separately
            if addl_txt_filter:
                # Get the lighting energy data
                group_energy, _ = nrg_stock_select(
                    nrg_stock, addl_txt_filter)

                # Get the lighting stock data
                _, group_stock = nrg_stock_select(
                    nrg_stock, txt_filter)
            else:
                group_energy, group_stock = nrg_stock_select(
                    nrg_stock, txt_filter)

            # Obtain the applicable lighting energy correction factors
            lt_correction = lt_factors[numpy.all(
                [lt_factors['CDIV'] == txt_filter[0][1],
                 lt_factors['BLDG'] == txt_filter[0][2],
                 lt_factors['EQPCLASS'] == txt_filter[0][4][0],
                 lt_factors['BULBTYPE'] == txt_filter[0][4][1]], axis=0)]
            lt_correction = lt_correction['FACTOR']

            # Correct the lighting energy data by applying
            # the appropriate weighting factor for the current
            # fixture and bulb type (note that group_energy is
            # returned by nrg_stock_select() as a dict and
            # thus needs to be disassembled before applying the
            # weighting factor)
            if group_energy:
                group_energy = dict(zip(sorted(group_energy.keys()),
                                        list(group_energy.values())*lt_correction))
        else:
            # Given input numpy array and 'compare from' list, return
            # energy/stock projection lists and reduced numpy array
            # (with matched rows removed)
            group_energy, group_stock = nrg_stock_select(
                nrg_stock, txt_filter)

        # Given the discovered lists of energy/stock values, ensure
        # length is equal to the number of years currently projected
        # by AEO. If not, and the list isn't empty, trigger an error.
        if len(group_energy) is not aeo_years:
            if len(group_energy) != 0:
                raise (ValueError('Error in length of discovered list!'))

        # Return combined stock/energy use values
        return {'stock': group_stock, 'energy': group_energy}


def walk(nrg_stock, loads, json_dict, yrs_range, lt_factors, key_list=[]):
    """Recursively traverse the input dict and obtain the corresponding data

    This function recursively explores the microsegments JSON key
    structure (effectively a nested dict) to each leaf/terminal node
    and, constructing as it goes a list of the keys corresponding to
    the current location in the dict. At each terminal node, a function
    is called to obtain the data from the input data files that
    corresponds to the microsegment given by the keys for that
    terminal node.

    Args:
        nrg_stock (numpy.ndarray): An array of AEO energy, equipment
            stock, and household count data given by microsegment.
        loads (numpy.ndarray): An array of thermal load component factors.
        json_dict (dict): The empty microsegments JSON structure.
        yrs_range (int): The number of years of data reported in the
            RESDBOUT file.
        lt_factors (numpy.ndarray): A numpy structured array with
            lighting efficiency and stock weighted factors to be used
            to break out the lighting energy use data by bulb type.
        key_list (list): A list of keys corresponding to the current
            location in the dict, ultimately indicating the data to
            extract from the applicable input file(s).

    Returns:
        The fully populated JSON file (as a nested dict) to be output
        by this module.
    """

    # Explore the data structure from the current location
    for key, item in json_dict.items():
        # If there are additional levels in the dict, call the function
        # again to advance another level deeper into the data structure
        if isinstance(item, dict):
            walk(nrg_stock, loads, item, yrs_range,
                 lt_factors, key_list + [key])

        # If a leaf node has been reached, check if the second entry in
        # the key list is one of the recognized building types, and if
        # so, finish constructing the key list for the current location
        # and obtain the data to update the dict
        else:
            if key_list[1] in bldgtypedict.keys():
                leaf_node_keys = key_list + [key]
                # Extract data from original data sources
                data_dict = list_generator(nrg_stock, loads, leaf_node_keys,
                                           yrs_range, lt_factors)

                # Set dict key to extracted data
                json_dict[key] = data_dict

    # Return populated database structure
    return json_dict


def lighting_eff_prep(lt_cpl_data, n_years, n_lt_types):
    """Calculate normalized lighting efficiency values

    This function takes the lighting cost, performance, and lifetime
    data from the AEO, extracts the performance data, and calculates
    a normalized efficiency factor. The normalization is performed on
    a fixture type basis (i.e., all GSL, REF, LFL, and EXT are
    normalized separately).

    These values should be combined with stock values to obtain
    weighting factors that can be used to parse the lighting energy
    use data, which are lumped together across all bulb types and then
    reported under a single bulb type for each fixture type.

    Args:
        lt_cpl_data (numpy.ndarray): A numpy structured array of the
            CPL data imported from the AEO source file.
        n_years (int): The number of years over which CPL data are given.
        n_lt_types (int): The number of lighting types (unique
            combinations of fixture type, e.g., GSL, REF, etc. and
            bulb type, e.g., INC, T12, etc.) present in the CPL data.

    Returns:
        A numpy structured array with columns specifying the fixture
        type, bulb type, and year, and rows corresponding to each of
        the unique combinations of fixture and bulb type. In each row,
        the value reported for the year is the normalized efficiency
        factor for that row (fixture and bulb type).
    """

    # Extract the unique fixture types
    fixture_types = numpy.unique(lt_cpl_data['Application'])

    # Extract the final year of reported lighting data (and thus
    # all residential data obtained from the AEO) from the CPL data
    final_year = max(lt_cpl_data['LastYear'])

    # Create range object for the year range from the first to last
    # year in the lighting data based on fixed parameters, since the
    # years reported in the lighting data itself may not be consistent
    # across all lighting types reported in the file
    year_range = range(final_year - n_years + 1,
                       final_year + 1)

    # Construct list of names for numpy structured array
    col_names = ['Application', 'BulbType'] + list(map(str, year_range))

    # Determine dtypes for final numpy array to be returned by this function
    col_dtypes = ['U4', 'U4'] + ['f8'] * len(year_range)

    # Construct complete dtype specification for numpy structured array
    the_dtype = list(zip(col_names, col_dtypes))

    # Initialize numpy structured array for lighting data with the correct
    # number of rows (the dtype specification defines the columns)
    fixture_perf = numpy.zeros(n_lt_types, dtype=the_dtype)

    itr = 0  # Initialize row counter variable

    # Calculate the lighting efficiency for each unique combination
    # of 'Application' and 'BulbType' for each year of data provided
    # and populate a numpy structured array with the resulting values
    for fixture in fixture_types:
        # Identify the unique bulb types for this fixture type
        bulb_types = numpy.unique(
            lt_cpl_data[lt_cpl_data['Application'] == fixture]['BulbType'])

        # Create an empty numpy array to use as an intermediate step
        # to store lighting performance values for each bulb type
        # associated with this fixture type
        fixture_group = numpy.zeros((len(bulb_types), n_years))

        # Create an empty list to which lists of fixture type and
        # bulb type will be added (appended)
        lt_type_codes = []

        for idx, bulb in enumerate(bulb_types):
            # Obtain the subset of the lighting data corresponding
            # to the current bulb and fixture type
            single_lt = lt_cpl_data[numpy.all([
                            lt_cpl_data['Application'] == fixture,
                            lt_cpl_data['BulbType'] == bulb], axis=0)]

            # Calculate the number of times each value should repeat
            # (to reflect the number of years the value stays the same)
            n_repeat_times = single_lt['LastYear'] - single_lt['FirstYear'] + 1

            # Generate numpy array of values using the number of
            # repeats calculated for each value
            bulb_perf_lm_watts, bulb_perf_watts = [numpy.repeat(
              single_lt[x], n_repeat_times) for x in ['lm_per_W', 'Watts']]

            # If more than the expected number of performance values
            # appear in the 1D numpy array, truncate the initial values
            bulb_perf_lm_watts, bulb_perf_watts = [
              bulb_perf_lm_watts[-n_years:], bulb_perf_watts[-n_years:]]
            # Find and remove spurious performance changes in lm/W
            # performance over time, yielding a final performance array
            bulb_perf = chk_false_eff(bulb_perf_lm_watts, bulb_perf_watts)

            # Invert the values in bulb_perf so that higher efficiency
            # bulbs (i.e., more lm/W) have lower values and thus
            # will have lower energy use associated with them (when
            # these efficiency multipliers are applied)
            bulb_perf = 1/bulb_perf

            # Insert the inverted bulb performance (referred to here as
            # bulb efficiency) into the intermediate numpy array
            fixture_group[idx, ] = bulb_perf

            # Insert the fixture type and bulb type codes into an
            # intermediate list of lists for later combination with
            # the normalized bulb efficiency values
            lt_type_codes.append([fixture, bulb])

        # Calculate normalized efficiency weighting factors for each
        # year for all of the bulb types that correspond to this
        # fixture type
        norm_fixture_group = fixture_group/numpy.sum(fixture_group, 0)

        # Combine each row of normalized efficiency weighting factors
        # with their corresponding fixture and bulb type codes and
        # insert them into the final lighting efficiency values
        # structured array
        for idx, row in enumerate(norm_fixture_group):
            fixture_perf[itr] = tuple(lt_type_codes[idx] + list(row))
            itr += 1  # Increment row counter variable

    # Return the final normalized (within each fixture type)
    # efficiency structured numpy array
    return fixture_perf


def chk_false_eff(bulb_perf_lm_watts, bulb_perf_watts):
    """Identify and remove spurious lighting performance changes across time.

    This function identifies and removes spurious changes in lighting
    performance array values in lm/W. Spurious values are flagged when
    a lm/W lighting performance value equals 99 and the corresponding
    lighting performance value in W also equals 99.

    Args:
        bulb_perf_lm_watts (numpy.ndarray): Annual lighting performance (lm/W).
        bulb_perf_watts (numpy.ndarray): Annual lighting performance (W).

    Returns: A numpy structured array of lighting performance values,
        in lm/W, which shows no spurious changes in performance values.
    """

    # Loop through all annual lighting performance values in lm/W
    for idx in range(0, len(bulb_perf_lm_watts)):
        # Identify spurious lm/W values as those equal to 99, where the
        # corresponding W performance value is also 99; set these
        # values to the previous performance value in the array
        if idx > 0 and (bulb_perf_lm_watts[idx] == 99) and (
           bulb_perf_lm_watts[idx] == bulb_perf_watts[idx]):
            bulb_perf_lm_watts[idx] = bulb_perf_lm_watts[idx - 1]

    return bulb_perf_lm_watts


def calc_lighting_factors(nrg_stock_data, lt_eff, n_yrs, n_lt_types):
    """Calculate normalized efficiency and stock weighted lighting multipliers.

    This function takes the normalized efficiency factors and converts
    them into normalized stock and efficiency factors. These factors
    are needed because the AEO data include stock reported for all
    fixture and bulb type combinations, but energy use is reported as
    the sum for all bulb types for a given fixture type, and only
    reported for one of the bulb types. For all other bulb types,
    energy use is indicated as 0.

    Using the normalized efficiency factors to break the energy use
    up by bulb type would fail to take into account the fact that while
    more efficient bulbs use less energy, if there are more of them,
    total energy use might not correspond exactly to the efficiency
    ratio alone.

    For a given fixture type (e.g., 'EXT'), the final multipliers are
    calculated by this function by taking the stock for each bulb type
    and multiplying it by the efficiency factor for that bulb type and
    then dividing each value by the sum of the values calculated for
    all bulb types for the current fixture type. This approach thus
    yields normalized values that can be multiplied by the energy use
    data to obtain energy use for each bulb type.

    Args:
        nrg_stock_data (numpy.ndarray): A structured array of
            residential energy and stock data imported from the
            EIA AEO 'RESDBOUT' file.
        lt_eff (numpy.ndarray): A structured array of efficiency-
            weighted multipliers, given by fixture and bulb type,
            with a column in the array for each year.
        n_yrs (int): The number of years for which energy data are present.
        n_lt_types (int): The number of lighting types (unique
            combinations of fixture type, e.g., GSL, REF, etc. and
            bulb type, e.g., INC, T12, etc.) present in the CPL data.

    Returns:
        A numpy structured array with lighting efficiency and stock
        weighted factors indexed by census division, building type,
        fixture type ('EQPCLASS'), bulb type ('BULBTYPE'), and year.
    """

    # Extract the first year of reported lighting data from the
    # AEO energy and stock data
    first_yr = min(nrg_stock_data[nrg_stock_data['ENDUSE'] == 'LT']['YEAR'])

    # Obtain census divisions from reported lighting data in the
    # AEO energy and stock data
    cdiv_list = set(nrg_stock_data[nrg_stock_data['ENDUSE'] == 'LT']['CDIV'])

    # Obtain building types from reported lighting data in the
    # AEO energy and stock data
    bldg_list = set(nrg_stock_data[nrg_stock_data['ENDUSE'] == 'LT']['BLDG'])

    # Obtain the lighting fixture types from the lighting efficiency
    # factors
    fixture_types = list(set(lt_eff['Application']))

    # Define the dtype for the lighting weighting factors array
    lt_wf_dtype = [('CDIV', 'i4'), ('BLDG', 'i4'), ('EQPCLASS', 'U4'),
                   ('BULBTYPE', 'U4'), ('YEAR', 'i4'), ('FACTOR', 'f8')]

    # Calculate the number of rows for the lighting weighting factors
    # array - unique factors are calculated for each combination of
    # census division, building type, year, fixture type, and bulb type
    n_rows = len(cdiv_list)*len(bldg_list)*n_yrs*n_lt_types

    # Preallocate the structured array for the lighting weighting factors
    lt_wf = numpy.zeros(n_rows, dtype=lt_wf_dtype)

    incr = 0  # Initialize array position increment variable

    # Prepare the lighting weighting factors for each unique census
    # division, building type, fixture type, and bulb type
    for cdiv in cdiv_list:
        for bldg in bldg_list:
            for fixture in fixture_types:
                # Select the subset of the lighting energy and stock
                # data corresponding to the current census division,
                # building type, and fixture type
                lt_nrgst = nrg_stock_data[numpy.all(
                    [nrg_stock_data['ENDUSE'] == 'LT',
                     nrg_stock_data['CDIV'] == cdiv,
                     nrg_stock_data['BLDG'] == bldg,
                     nrg_stock_data['EQPCLASS'] == fixture], axis=0)]

                # Extract the unique (no repeated entries) list of
                # applicable bulb types for this fixture type
                bulb_types = list(set(
                    lt_eff[lt_eff['Application'] == fixture]['BulbType']))

                # Preallocate 1-D array to store total stock for all bulb
                # types for the current lighting type
                total_denom = numpy.zeros(n_yrs)

                # Preallocate intermediate list to store indices for
                # the lighting weighting factors calculated below
                array_indices = []

                # Preallocate intermediate array to store stock-weighted
                # factors for all bulb types for the current lighting
                # type, where each row corresponds to a bulb type and
                # each column to a year
                fixture_array_tmp = numpy.zeros((len(bulb_types), n_yrs))

                for idx, bulb in enumerate(bulb_types):
                    # Obtain the stock for the current bulb type
                    # as a 1-D numpy array (vector with value for each year)
                    x = lt_nrgst[lt_nrgst['BULBTYPE'] == bulb]
                    x = x['EQSTOCK']

                    # Obtain the efficiency factors for the current
                    # bulb type though as a numpy structured array
                    # that is next converted into a form that can be
                    # multiplied by another array
                    y = lt_eff[
                        numpy.all([lt_eff['Application'] == fixture,
                                   lt_eff['BulbType'] == bulb],
                                  axis=0)]

                    # Convert the structured array into a list and strip
                    # off the leading Application and BulbType strings
                    y = list(list(y)[0])[2:]

                    # Multiply the stock for this bulb type with
                    # the corresponding efficiency factors and
                    # insert them into the appropriate row in the
                    # temporary matrix
                    tmp_vals = x*y
                    fixture_array_tmp[idx, ] = tmp_vals

                    # Add the stock for this bulb type multiplied by
                    # the corresponding efficiency factors to the total
                    total_denom += tmp_vals

                    # Develop the array of indices for the current bulb type,
                    # where each row corresponds to a single year
                    for st in range(0, n_yrs):
                        indices = [cdiv, bldg, fixture, bulb, st+first_yr]
                        # Add the index values to the intermediate list
                        array_indices.append(indices)
                    # This loop approach is probably not the most runtime
                    # efficient, but it avoids the need to create a
                    # structured array as the intermediate array, since
                    # the indices are a mix of strings and integers

                # Divide the stock in each row of the intermediate
                # matrix of lighting weighting factors by the total stock
                fixture_array_tmp = fixture_array_tmp/total_denom

                # Recast the 2-D array of weighting factors into a 1-D
                # array to match the number of rows in the indices list
                fixture_array_1d = numpy.reshape(fixture_array_tmp,
                                                 numpy.size(fixture_array_tmp))

                # For each lighting stock multiplier, construct the row
                # from the indices and the value and insert it into the
                # final array
                for idx, val in enumerate(fixture_array_1d):
                    lt_wf[incr+idx, ] = tuple(array_indices[idx] + [val])

                # Update the array position increment variable
                incr += idx+1

    return lt_wf


def onsite_calc(generation_file, json_results):
    """ Calculates net electricity use using EIA's pre-2021 methodology
    and adds a new PV technology type. """

    def array_mult(dct, factor):
        scaled = {key: val * factor for key, val in dct.items()}
        return scaled

    # Factor to convert commercial energy data from TBTU to MMBTU
    to_mmbtu = 1000000

    # Read in AEO's onsite generation file
    gen_dtypes = dtype_array(generation_file)
    gen_dtypes[1] = ('Year', '<U50')
    gen_data = data_import(generation_file, gen_dtypes)

    # Define impacted building type
    res_bld = 'single family home'

    # Pull the onsite generation by census division
    for div in cdivdict:
        cdiv = gen_data[gen_data['Division'] == cdivdict[div]][
            ['Year', 'OwnUse']]
        years = numpy.unique(cdiv['Year'])
        cdiv['OwnUse'] = cdiv['OwnUse']*to_mmbtu
        onsite_gen = dict([(i, cdiv[cdiv['Year'] == i][
                    'OwnUse'].sum()) for i in years])

        # Add in new onsite generation end use
        elec_slice = json_results[div][res_bld]['electricity']
        elec_slice['onsite generation'] = {}
        elec_slice['onsite generation']['energy'] = array_mult(onsite_gen, -1)
        elec_slice['onsite generation']['stock'] = 'NA'

    return json_results


def dtype_eval(entry):
    """ Takes as input an entry from a standard line (row) of a text
    or CSV file and determines its type (only string, float, or
    integer), returning the specified type, which can be added to a
    list to be used in creating a numpy structured array of the data. """

    # Strip leading and trailing spaces off of string
    entry = entry.strip()

    if '.' in entry:
        dtype = 'f8'
    elif 'NA'.lower() in entry.lower():
        dtype = 'f8'
    elif re.search('[a-zA-Z]+', entry):  # At least one letter somewhere
        dtype = '<U50'  # Strings assumed to be no more than 50 characters
    else:
        dtype = 'i4'

    return dtype


def dtype_array(data_file_path, delim_char=',', hl=None):
    """Scan a file to assess the data type

    Using the csv module, read a text data file to develop a data
    type definition for the file. The first line is always read,
    under the assumption that it contains the column names. The
    remainder of the file is scanned to find the next line that
    is the same length as the header row and has a value reported
    for each entry in the row. This second line is then used to
    determine the data type for each column. The column names and
    data types for each column are then converted into a list of
    tuples that can be used to specify the dtype parameter of a
    numpy structured array.

    This function expects that the data file provided has a header
    row, and works only when the data in the first complete row (after
    the header) is exemplary of the type of data in the entirety of
    each column. Columns with data of varying types will not always
    be handled properly by this function.

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
    with open(data_file_path, encoding="latin1") as thefile:

        # This use of csv.reader assumes that the default setting of
        # quotechar '"' is appropriate
        filecont = csv.reader(thefile, delimiter=delim_char)

        # Skip the specified number of extraneous leading lines in
        # the file that do not include the column headers
        if hl:
            for i in range(0, hl):
                next(filecont)

        # Extract header (first) row and remove leading and trailing
        # spaces from all entries
        header_names = [entry.strip() for entry in next(filecont)]

        # Scan through the file until encountering a row with an entry
        # for each value in the row (i.e., no empty strings due to
        # missing values) and a row that has the same number of entries
        # as the header line ("or" condition in the while loop per
        # De Morgan's laws)
        row = next(filecont)
        while '' in row or len(row) != len(header_names):
            row = next(filecont)

        # Determine dtype of the current line in the file
        dtypes = [dtype_eval(col) for col in row]

        # Combine data types and header names into list of tuples
        comb_dtypes = list(zip(header_names, dtypes))

        return comb_dtypes


def data_import(data_file_path, dtype_list, delim_char=',', skip_rows=[]):
    """Import data and convert to a numpy structured array.

    Read the contents of a data file with a header line and convert
    it into a numpy structured array using the provided dtype definition.
    If specified, also skip lines that have values in the first column
    indicated by 'skip_rows.'

    Args:
        data_file_path (str): The full path to the data file to be imported.
        dtype_list (list): A list of tuples with each tuple containing two
            entries, a column heading string, and a string defining the
            data type for that column. Formatted as a numpy dtype list.
        delim_char (str, optional): The delimiting character, defaults to ','.
        skip_rows (list): A list of strings, one of which will appear
            in the first column of each row to be skipped.

    Returns:
        A numpy structured array of the imported data file with the
        columns specified by dtype_list.
    """

    # Open the target CSV formatted data file
    with open(data_file_path) as thefile:

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
                                  delimiter=delim_char, skipinitialspace=True)
        else:  # No NULL bytes, proceed normally
            filecont = csv.reader(thefile,
                                  delimiter=delim_char, skipinitialspace=True)

        # Create list to be populated with tuples of each row of data
        # from the data file
        data = []

        # Skip first line of the file
        next(filecont)

        # Import the data, skipping lines that have an end use
        # indicated that is not needed (or will cause later problems
        # because the data in these rows has a structure inconsistent
        # with the other rows); for any lines with fewer values than
        # expected based on the dtype, add a sufficient number of 0
        # values to complete the line (0 values are added since they
        # can be coerced to strings or floats and empty strings cannot)
        for row in filecont:
            if row[0].strip() not in skip_rows:
                if len(tuple(row)) != len(dtype_list):
                    row = row + [0]*(len(dtype_list)-len(row))
                if not row[8]:
                    row[8] = 0
                data.append(tuple(row))

        # Convert data into numpy structured array, using a try/catch
        # for the case where the data type for a particular column
        # is not identified correctly by the dtype_array function
        try:
            final_struct = numpy.array(data, dtype=dtype_list)
        # Target error "ValueError: invalid literal for int() with base 10: ''"
        except ValueError:
            # In the 2017 AEO data, some consumption data are reported
            # as floating point numbers on the 0.5 for some reason;
            # update the dtype for that column to float
            dtype_list[7] = (dtype_list[7][0], 'f8')

            # With the '' strings replaced with integer coercible
            # values, create the numpy array as originally desired
            final_struct = numpy.array(data, dtype=dtype_list)
        return final_struct


def str_cleaner(data_array, column_name):
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

    Returns:
        The input array with the strings in column_name revised.
    """

    def special_character_handler(text_string):
        """Edit special characters in strings to be written consistently.

        Args:
            text_string (str): A string describing a particular technology.

        Returns:
            The edited text string.
        """

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
        elif html_double_quote_present:
            text_string = re.sub('&quot;', '-inch', text_string)
        elif double_quote_present:
            text_string = re.sub('\"', '-inch', text_string)

        return text_string

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
            entry = special_character_handler(entry)

            # Delete any newly "apparent" (no longer enclosed by the double
            # quotes) trailing or (unlikely) leading spaces and replace the
            # original entry
            data_array[column_name][row_idx] = entry.strip()

    else:
        # Operate on each row in the specified column of the structured array
        for row_idx, entry in enumerate(data_array[column_name]):

            # Clean up strings with special characters to ensure that
            # these characters appear consistently across all imported data
            entry = special_character_handler(entry)

            # Delete any leading and trailing spaces
            data_array[column_name][row_idx] = entry.strip()

    return data_array


def update_lighting_dict():
    """Update the technology_supplydict to be compatible with the 2017 AEO.

    In the 2015 AEO data, incandescent bulbs have their bulb type given
    by the string 'Inc'. The 2017 AEO data use 'INC'. The translation
    dict 'technology_supplydict' is configured by default for the 2015
    AEO. This function updates that dict to be compatible with the
    2017 AEO.

    Because the translation dicts are all global variables, this dict
    does not need to take any arguments or return the updated dicts.
    Rather it simply modifies the existing dict in place.
    """
    technology_supplydict['general service (incandescent)'] = ('GSL', 'INC')
    technology_supplydict['reflector (incandescent)'] = ('REF', 'INC')
    technology_supplydict['external (incandescent)'] = ('EXT', 'INC')


def main():
    """ Import text and JSON files; run through JSON objects; find
    analogous text information; replace JSON values; update JSON """

    # Set up to support user option to specify the year for the
    # AEO data being imported (default if the option is not used
    # should be current year)
    aeo_versions = [2015, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2025]
    parser = argparse.ArgumentParser()
    help_string = 'Specify year of AEO data to be imported'
    parser.add_argument('-y', '--year',
                        type=int,
                        help=help_string,
                        choices=aeo_versions)

    # Get import year specified by user (if any)
    aeo_import_year = parser.parse_args().year

    # Instantiate objects that contain useful variables
    handyvars = UsefulVars()
    eiadata = EIAData()
    skip = SkipLines(aeo_import_year, aeo_versions)

    # Import metadata generated based on EIA AEO data files
    with open(handyvars.aeo_metadata, 'r') as metadata:
        metajson = json.load(metadata)

    # Calculate number of years in the AEO data; expecting 32 years
    # for AEO 2015 data, 42 years in AEO 2017 data (though 38 years
    # are common across all input EIA data files)

    # Use AEO data import year specified by user (if any) to determine
    # how to specify the year range to be used for processing the data
    if aeo_import_year == 2015:
        yrs_range = metajson['max year'] - metajson['min year'] + 1

        # Import EIA RESDBOUT.txt energy use and stock file
        ns_dtypes = dtype_array(eiadata.res_energy, '\t')
        ns_data = data_import(eiadata.res_energy, ns_dtypes, '\t',
                              ['SF', 'ST', 'FP'])
    elif aeo_import_year in [2025, None]:
        yrs_range = metajson['max year'] - metajson['min year'] + 1
        update_lighting_dict()

        # Import EIA RESDBOUT.txt energy use and stock file
        ns_dtypes = dtype_array(eiadata.res_energy)
        ns_data = data_import(eiadata.res_energy, ns_dtypes, ',',
                              ['SF', 'ST', 'FP', 'HSHE', 'HSHN',
                               'HSHA', 'CSHA', 'CSHE', 'CSHN'])

    # THIS APPROACH MAY NEED TO BE REVISITED IN THE FUTURE; AS IS,
    # IT DOES NOT ENSURE CONSISTENCY WITH THE OTHER AEO INPUT DATA
    # IN THE RANGE OF YEARS OF THE DATA REPORTED

    # Clean up all the columns from the imported data that have
    # extraneous spaces in their entries
    ns_data = str_cleaner(ns_data, 'ENDUSE')
    ns_data = str_cleaner(ns_data, 'EQPCLASS')
    ns_data = str_cleaner(ns_data, 'BULBTYPE')

    # Import residential thermal load components data
    tl_dtypes = dtype_array(handyvars.res_tloads, '\t')
    tl_data = data_import(handyvars.res_tloads, tl_dtypes, '\t')

    # Explicitly define the lighting data type (note that special)
    eia_lt_dtype = [('FirstYear', 'i4'), ('LastYear', 'i4'), ('Cost', 'f8'),
                    ('EE_Sub1', 'f8'), ('EE_Sub2', 'f8'), ('EE_Sub3', 'f8'),
                    ('EE_Sub4', 'f8'), ('EE_Sub5', 'f8'), ('EE_Sub6', 'f8'),
                    ('EE_Sub7', 'f8'), ('EE_Sub8', 'f8'), ('EE_Sub9', 'f8'),
                    ('Sub1', 'f8'), ('Sub2', 'f8'), ('Sub3', 'f8'),
                    ('Sub4', 'f8'), ('Sub5', 'f8'), ('Sub6', 'f8'),
                    ('Sub7', 'f8'), ('Sub8', 'f8'), ('Sub9', 'f8'),
                    ('lm_per_W', 'i4'), ('Watts', 'i4'),
                    ('Life_hrs', 'i4'), ('CRI', 'i4'),
                    ('Application', 'U8'), ('BulbType', 'U8'),
                    ('Beta_1', 'f8'), ('Beta_2', 'f8')]

    # Import EIA residential lighting cost, performance, and lifetime
    # data for the purposes of redistributing the energy data, which
    # are reported for only one lighting technology type (bulb type)
    # for each fixture/luminaire type
    eia_lt = numpy.genfromtxt(rmt.EIAData().r_lt_all, dtype=eia_lt_dtype,
                              skip_header=skip.lt_skip_header,
                              skip_footer=skip.lt_skip_footer,
                              encoding="latin1")

    # Compute the number of unique lighting fixture and bulb type combinations
    n_lt_types = sum([len(set(eia_lt[eia_lt['Application'] == x]['BulbType']))
                      for x in set(eia_lt['Application'])])

    # Obtain normalized lighting efficiencies for each fixture and bulb type
    lt_eff = lighting_eff_prep(eia_lt, yrs_range, n_lt_types)

    # Convert the lighting efficiencies into stock and efficiency weighted
    # multipliers that can be used to break out the lighting energy data
    # combined for all bulb types into separate values for each bulb
    # type for a given fixture type
    lt_wt_fac = calc_lighting_factors(ns_data, lt_eff, yrs_range, n_lt_types)

    # json.dump cannot convert ("serialize") numbers of the type
    # np.int64 to integers, but all of the integers in 'result' are
    # formatted as np.int64; this function fixes that problem as the
    # data are serialized and exported
    def fix_ints(num):
        if isinstance(num, numpy.integer):
            return int(num)
        else:
            print(num, type(num))
            raise TypeError

    # Import JSON file and run through updating scheme
    with open(handyvars.json_in, 'r') as jsi, open(
         handyvars.json_out, 'w') as jso:
        msjson = json.load(jsi)

        # Run through JSON objects, determine replacement information
        # to mine from the imported data, and make the replacements
        result = walk(ns_data, tl_data, msjson, yrs_range, lt_wt_fac)

        # Add in onsite generation for SF as a new end-use from
        # RGENOUT.txt
        result = onsite_calc(eiadata.res_generation, result)

        # Write the updated dict of data to a new JSON file
        json.dump(result, jso, indent=2, default=fix_ints)


if __name__ == '__main__':
    main()
