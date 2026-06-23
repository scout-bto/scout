#!/usr/bin/env python3

""" Develop useful metadata from the EIA data files. """

from scout import mseg as rm
from scout import mseg_techdata as rmt
from scout import com_mseg as cm
from scout import com_mseg_tech as cmt
from scout.config import FilePaths as fp

import numpy as np
import re
import json
import types
import argparse
from contextlib import suppress


class UsefulVars(object):
    """Class of variables defining file locations for import

    Specify any additional files to import beyond those used by the
    imported Scout modules.

    Attributes:
        ss_conv_file (str): Path to site-source conversion factor file.
    """

    def __init__(self):
        self.ss_conv_file = (fp.CONVERT_DATA / "site_source_co2_conversions.json")


def json_processor(json_file, min_years, max_years):
    """Import the conversions file and identify the available year range.

    Since the conversions file is JSON-formatted, the other functions
    in this module are not appropriate. This function recursively
    traverses the key-value structure of a JSON file, storing the
    terminal (leaf) nodes in a list.

    This approach thus assumes that the file has terminal node keys
    corresponding to the years for which data in the file are available.

    Args:
        json_file (str): JSON-formatted file relative path and file name.
        min_years (list): The earliest years (as numpy.int64 integers)
            found in the imported data.
        max_years (list): The latest years (as numpy.int64 integers)
            found in the imported data.

    Returns:
        Updated lists of minimum and maximum years with the minimum
        and maximum found in the conversions data file leaf node
        keys (values added to the lists are numpy.int64 integers).
    """
    def recur(db, key_list=[]):
        """Recursively traverse dict and store leaf node keys in list
        """
        for key, item in db.items():
            if isinstance(item, dict):
                recur(item, key_list)
            else:
                key_list.append(key)
        return key_list

    conv = json.load(open(json_file, 'r'))

    # Obtain the leaf node keys
    leaf_keys = recur(conv)

    # Extract just those keys with the format YYYY
    years_list = [a for a in leaf_keys if re.search('[0-9]{4}', a)]

    # Circumvents the action of .append() modifying in place the lists
    # passed to the function
    new_min_years = min_years + [np.int64(min(years_list))]
    new_max_years = max_years + [np.int64(max(years_list))]

    return new_min_years, new_max_years


def extract_year_range(data_array, colnames, min_years, max_years, pivot_yr=0):
    """Determine the minimum and maximum years of data in a given AEO file.

    For a given AEO data file that has been imported and formatted
    into a numpy structured array, this function looks in the column(s)
    specified for the minimum and maximum calendar years reported.
    Ultimately, this function produces a conservative range for the
    minimum and maximum years across those columns, taking the largest
    (latest) of the reported minimum years and the smallest (earliest)
    of the reported maximum years. The handling of column names is done
    based on whether there are one or two columns given. In the case
    where there are two columns, they are assumed to represent low
    (e.g., market entry year) and high (e.g., market exit year) year
    datasets.

    Args:
        data_array (numpy.ndarray): A numpy structured array of EIA AEO
            residential or commercial building energy and stock or
            equipment characteristic data.
        colnames (list): List of strings specifying the name(s) of the
            column(s) containing year data.
        min_years (list): The earliest years found in the imported data.
        max_years (list): The latest years found in the imported data.
        pivot_yr (int): Optional pivot year needed for some data that
            must be adjusted to be in the form YYYY.

    Returns:
        Updated lists of minimum and maximum years with the minimum
        and maximum found in data_array.
    """

    # Preallocate minimum and maximum year variables
    min_yr = 0
    max_yr = 10000

    # If there are two columns given, assume that they represent lower
    # bound and upper bound years, and obtain the min from the lower
    # bound set and the max from the upper bound set of years
    if len(colnames) == 2:
        data_array_min_years = data_array[colnames[0]]
        data_array_max_years = data_array[colnames[1]]

        min_yr = min(data_array_min_years)
        max_yr = max(data_array_max_years)

    # Otherwise, assume all the columns of year data are directly
    # comparable and run through all of them to obtain a _conservative_
    # indication of the min and max years in the data
    else:
        for name in colnames:
            data_array_years = data_array[name]

            min_yr = max(min_yr, min(data_array_years))
            max_yr = min(max_yr, max(data_array_years))

    # Circumvents the action of .append() modifying in place the lists
    # passed to the function
    new_min_years = min_years + [min_yr + pivot_yr]
    new_max_years = max_years + [max_yr + pivot_yr]

    return new_min_years, new_max_years


def dtype_ripper(the_dtype, min_years, max_years):
    """Extract the range of years from the dtype of a structured array.

    Args:
        the_dtype (list): A list of tuples with each tuple containing two
            entries, a column heading string, and a string defining the
            data type for that column. Formatted as a numpy dtype list.
        min_years (list): The earliest years found in the imported data.
        max_years (list): The latest years found in the imported data.

    Returns:
        Updated lists of minimum and maximum years with the minimum
        and maximum found in data_array.
        The minimum and maximum years, as integers, that were contained
        in the column headings of the dtype definition.
    """

    # Strip the dtype into its constituent lists: column names and data formats
    colnames, dtypes = zip(*the_dtype)

    # Preallocate a list for the years extracted from the column names
    year_list = []

    # Loop over the list of column names, identify entries that have
    # the format specified by a regex, and add the matches to a list
    for name in colnames:
        year = re.search('^[1|2][0-9]{3}$', name)
        if year:
            year_list.append(year.group())

    # Identify the minimum and maximum years from the list of the years
    # in the column names and record them as integers instead of strings
    min_yr = int(min(year_list))
    max_yr = int(max(year_list))

    # Circumvents the action of .append() modifying in place the lists
    # passed to the function
    new_min_years = min_years + [min_yr]
    new_max_years = max_years + [max_yr]

    return new_min_years, new_max_years


def EIA_filename_identifier():
    """Create a list of the EIA files identified in the imported modules.

    This function takes a list of all of the imported modules and looks
    within each for a class called EIAData. If such a class is found,
    the strings for the file names of the EIA data imported by that
    module are added to a list of filenames.

    Returns:
        A list of filenames from the classes that identify the EIA data
        files from all of the imported modules.
    """

    # Initialize the list of filenames
    filenames = []

    # Loop over all of the globals present in this module and check
    # each to determine if it is a module
    for name, val in globals().items():
        # Note that 'name' is the reference name for the module, but
        # 'val' is the module reference; for example, in the statement
        # 'import os as kicker', name = 'kicker' and val refers to 'os'
        if isinstance(val, types.ModuleType):
            # Ignore the AttributeError exception raised for modules
            # that do not have an EIAData attribute
            with suppress(AttributeError):
                # Create an EIAData class object for the module
                # identified by 'name'
                data_class = getattr(globals()[name], 'EIAData')
                # Extract the values in __dict__ from the EIAData class
                # and append the resulting list to the existing
                # filenames list
                filenames = filenames + list(data_class().__dict__.values())

    return filenames


def file_processor(file_name, func_name, col_index, files_list,
                   min_yrs, max_yrs, pivot_yr=0, skip_header_lines=None):
    """Import and process data to obtain the year range from a data file.

    To ensure that the EIA data files that are imported are also
    removed from the list of files that should be imported and
    processed in a single step, this function combines those tasks.

    Args:
        file_name (str): The name of the file to be imported.
        func_name (str): The name of the function that contains
            the steps required to import and prepare the named
            file for processing.
        col_index (list): List of strings specifying the name(s)
            of the column(s) containing year data.
        files_list (list): A list of the files that should be
            imported and checked and have not yet been.
        min_years (list): The earliest years found in the imported data.
        max_years (list): The latest years found in the imported data.
        pivot_yr (int): Optional pivot year needed for some data that
            must be adjusted to be in the form YYYY.
        skip_header_lines (int): Optional number of lines in the
            header of the file imported using the function 'func_name'
            to be skipped when importing the data.
    """

    # Call the external function that imports the data at file_name
    # (and passes through the number of header lines to skip in the
    # file, if applicable)
    if skip_header_lines:
        data_object = func_name(file_name, skip_header_lines)
    else:
        data_object = func_name(file_name)

    # Extract the years from the imported data, using the function
    # appropriate for the location of the years in the data, and
    # remove the name of the file with those data from the list
    if type(data_object) is list:
        # For the case where the range of years are reported in the
        # header of the data, scan the dtype to identify the year
        # range for those data
        min_yrs, max_yrs = dtype_ripper(data_object, min_yrs, max_yrs)

    else:
        min_yrs, max_yrs = extract_year_range(data_object, col_index,
                                              min_yrs, max_yrs, pivot_yr)

    # Update the list of files that have yet to be examined
    files_list.remove(file_name)

    return min_yrs, max_yrs


def main():
    """ Each of the AEO data files includes data reported over a range
    of calendar years. These data should ultimately be reported over a
    common range of years. To determine the common range across all of
    the AEO data, the major files are imported here and the minimum and
    maximum years from each file are compared to determine the range
    that is common for all of those files. """

    # Set up to support user option to specify the year for the
    # AEO data being imported (default if the option is not used
    # should be current year)
    parser = argparse.ArgumentParser()
    help_string = 'Specify year of AEO data to be imported'
    parser.add_argument('-y', '--year', type=int, help=help_string)

    # Get import year specified by user (if any)
    aeo_import_year = parser.parse_args().year

    # Specify the number of header and footer lines to skip based on the
    # optional AEO year indicated by the user when this module is called
    if aeo_import_year == 2015:
        nlt_cp_skip_header = 20
        lt_skip_header = 35
    else:
        nlt_cp_skip_header = 2
        lt_skip_header = 37

    # Instantiate lists to store minimum and maximum years identified
    # from the data
    min_yrs = []
    max_yrs = []

    # Generate the list of EIA data filenames from all of the imported modules
    files_ = EIA_filename_identifier()

    # Remove rsclass.txt if it is present, since that file does not
    # have any data reported by year
    files_ = [file_ for file_ in files_ if file_ != 'rsclass.txt']

    def import_residential_energy_stock_data(file_name):
        # The delimiters for RESDBOUT vary depending on the release
        # year of the data
        try:  # comma-delimited
            ns_dtypes = rm.dtype_array(file_name)
            ns_data = rm.data_import(file_name, ns_dtypes, ',',
                                     ['SF', 'ST', 'FP', 'HSHE', 'HSHN',
                                      'HSHA', 'CSHA', 'CSHE', 'CSHN'])
        except (IndexError, ValueError):  # tab-delimited
            ns_dtypes = rm.dtype_array(file_name, '\t')
            ns_data = rm.data_import(file_name, ns_dtypes, '\t',
                                     ['SF', 'ST', 'FP', 'HSHE', 'HSHN',
                                      'HSHA', 'CSHA', 'CSHE', 'CSHN'])
        return ns_data

    def import_residential_cpl_non_lighting_data(file_name, skip_header_lines):
        eia_nlt_cp = np.genfromtxt(file_name, names=rmt.r_nlt_cp_names,
                                   dtype=None, comments=None,
                                   skip_header=skip_header_lines,
                                   encoding="latin1")
        return eia_nlt_cp

    def import_residential_cpl_lighting_data(file_name, skip_header_lines):
        eia_lt = np.genfromtxt(file_name, names=rmt.r_lt_names,
                               dtype=None, comments=None,
                               skip_header=skip_header_lines, skip_footer=52,
                               encoding="latin1")
        return eia_lt

    def import_commercial_service_demand_data(file_name):  # KSDOUT.txt
        serv_dtypes = cm.dtype_array(file_name)
        return serv_dtypes

    def import_commercial_energy_stock_data(file_name):  # KDBOUT.txt
        catg_dtypes = cm.dtype_array(file_name)
        catg_data = cm.data_import(file_name, catg_dtypes)
        return catg_data

    def import_commercial_cpl_data(file_name):  # ktek.csv
        tech_dtypes = cm.dtype_array(file_name, ',',
                                     cmt.UsefulVars().cpl_data_skip_lines - 1)
        col_indices, tech_dtypes = cmt.dtype_reducer(
                                        tech_dtypes,
                                        cmt.UsefulVars().columns_to_keep)
        tech_data = cm.data_import(file_name, tech_dtypes, ',',
                                   cmt.UsefulVars().cpl_data_skip_lines,
                                   col_indices)
        return tech_data

    def import_commercial_time_preference_data(file_name):  # kprem.txt
        tpp_data = cmt.kprem_import(file_name,
                                    cmt.UsefulVars().tpp_dtypes,
                                    cmt.UsefulVars().tpp_data_skip_lines)
        return tpp_data

    min_yrs, max_yrs = file_processor(rm.EIAData().res_energy,
                                      import_residential_energy_stock_data,
                                      ['YEAR'],
                                      files_, min_yrs, max_yrs)

    min_yrs, max_yrs = file_processor(rmt.EIAData().r_nlt_costperf,
                                      import_residential_cpl_non_lighting_data,
                                      ['START_EQUIP_YR', 'END_EQUIP_YR'],
                                      files_, min_yrs, max_yrs,
                                      skip_header_lines=nlt_cp_skip_header)

    min_yrs, max_yrs = file_processor(rmt.EIAData().r_lt_all,
                                      import_residential_cpl_lighting_data,
                                      ['START_EQUIP_YR', 'END_EQUIP_YR'],
                                      files_, min_yrs, max_yrs,
                                      skip_header_lines=lt_skip_header)

    min_yrs, max_yrs = file_processor(cm.EIAData().serv_dmd,
                                      import_commercial_service_demand_data,
                                      '',
                                      files_, min_yrs, max_yrs)

    min_yrs, max_yrs = file_processor(cm.EIAData().catg_dmd,
                                      import_commercial_energy_stock_data,
                                      ['Year'],
                                      files_, min_yrs, max_yrs,
                                      pivot_yr=cm.UsefulVars().pivot_year)

    min_yrs, max_yrs = file_processor(cmt.EIAData().cpl_data,
                                      import_commercial_cpl_data,
                                      ['y1', 'y2'],
                                      files_, min_yrs, max_yrs)

    min_yrs, max_yrs = file_processor(cmt.EIAData().tpp_data,
                                      import_commercial_time_preference_data,
                                      ['Year'],
                                      files_, min_yrs, max_yrs)

    min_yrs, max_yrs = json_processor(UsefulVars().ss_conv_file,
                                      min_yrs, max_yrs)

    # Check that all of the expected files have been imported, and if
    # any files remain, print the filenames to the console
    if files_:
        # Generate a neatly formatted file string
        files_str = ''
        for file_ in files_:
            if file_ != files_[-1]:
                files_str = f'{files_str}{file_}, '
            elif len(files_) == 1:
                files_str = f'{files_str}{file_}'
            else:
                files_str = f'{files_str}and {file_}'

        # Print the unused file names to the console
        print(f'Some EIA residential and/or commercial data files were '
              f'not imported. These files were: {files_str}')

    # Construct a dict with the minimum and maximum years recorded as integers
    year_range_result = {'min year': int(max(min_yrs)),
                         'max year': int(min(max_yrs))}

    # Preserve aeo_base_year from existing metadata if present
    try:
        with open(fp.METADATA_PATH, 'r') as existing:
            existing_meta = json.load(existing)
            if 'aeo_base_year' in existing_meta:
                year_range_result['aeo_base_year'] = existing_meta[
                    'aeo_base_year']
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    # Output a tiny JSON file with year range and base year values
    with open(fp.METADATA_PATH, 'w') as jso:
        json.dump(year_range_result, jso, indent=2)
        jso.write('\n')


if __name__ == '__main__':
    main()
