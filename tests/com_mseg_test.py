#!/usr/bin/env python3

""" Tests for commercial microsegment data processing code """

# Import code to be tested
from scout import com_mseg as cm

# Import needed packages
import unittest
import numpy as np
import itertools
import os
import csv
import re


# Skip this test if the EIA files are not expected, indicated by the
# EXPECT_EIA_FILES environment variable being set to the string 'true'
@unittest.skipUnless('EXPECT_EIA_FILES' in os.environ and
                     os.environ['EXPECT_EIA_FILES'] == 'true',
                     'EIA Data Files Not Available On This System')
class EIADataFileIntegrityTest(unittest.TestCase):
    """ Test for the presence of the anticipated column headings in
    both the EIA general commercial buildings database and the EIA
    service demand database and report when any required columns are
    missing. Also test whether all of the years for which data are
    reported in both data files are the same. """

    @classmethod
    def setUpClass(self):  # so that set up is run once for the entire class
        # Open each EIA data file, extract the header row, and reformat
        # the text in each entry for easier handling, producing a list
        # of strings for the column titles
        with open(cm.EIAData().serv_dmd, 'r') as sd:
            sd_fl = csv.reader(sd)
            self.sd_head = [entry.strip() for entry in next(sd_fl)]

        with open(cm.EIAData().catg_dmd, 'r') as db:
            db_fl = csv.reader(db)
            self.db_head = [entry.strip() for entry in next(db_fl)]

    # The function catg_data_selector expects certain columns to be
    # present in the commercial building data - this test checks for
    # the presence of those columns; column order does not matter but
    # the test is case-sensitive since the way the column headers are
    # used in the main code is case-sensitive
    def test_integrity_of_main_commercial_database(self):

        # Anticipated column headings in the commercial database
        col_heads = ['Division', 'BldgType', 'EndUse', 'Fuel', 'Year',
                     'Amount', 'Label']

        # Test for the presence of all of the anticipated column headings
        for head in col_heads:
            self.assertTrue(head in self.db_head, msg=head +
                            ' column not found.')

    # Check whether the years reported in the two EIA data files match
    # (This also tests, in a confounded way, whether the pivot year
    # applied to the commercial data years is still correct.)
    def test_years_in_both_commercial_energy_data_files(self):

        # Create a list of column names in the service demand data
        # that correspond to years (converting the years to integers)
        sd_yrs = [int(a) for a in self.sd_head if re.search('^2[0-9]{3}$', a)]

        # Determine which column has the year data
        loc = self.db_head.index('Year')

        years = []  # Initialize list for reported years

        # Read the first 100 data lines to (subsequently) create a
        # unique list of year numbers in the data
        with open(cm.EIAData().catg_dmd, 'r') as db:
            db_fl = csv.reader(db)
            next(db_fl)  # Skip first line
            for row in itertools.islice(db_fl, 100):
                years.append(int(row[loc]))

        # Delete any entries that equal 0
        db_yrs = [a for a in years if a != 0]

        # Create a list of the unique years reported out of the first
        # 100 lines of the main commercial data file and adjust the
        # list based on the expected pivot year of 1989
        db_yrs = np.unique(db_yrs) + cm.UsefulVars().pivot_year

        # Compare the contents of the two lists, where if the lists are
        # exactly the same, the list comprehension will be empty. Each
        # list comprehension only checks one list against the other, so
        # the comparison must be conducted both ways (as below).
        # N.B. db_yrs is a numpy array and sd_yrs is a list.
        cmpr = set(sd_yrs)
        diff_yrs1 = [a for a in db_yrs if a not in cmpr]

        cmpr = set(db_yrs)
        diff_yrs2 = [a for a in sd_yrs if a not in cmpr]

        diff_yrs = diff_yrs1 + diff_yrs2  # Combine the two lists together

        # Set up test that will fail if diff_yrs has any entries
        self.assertFalse(diff_yrs, msg=('The lists of years in the EIA '
                                        'general commercial data file '
                                        'and the service demand data '
                                        'file do not match.'))

    # The function sd_mseg_percent expects that the service demand data
    # will have certain columns that can be used to select the correct
    # data for further processing - this test checks for the presence
    # of those columns
    def test_integrity_of_commercial_service_demand_database(self):

        # Anticipated (non-year) columns in the service demand data
        col_heads = ['r', 'b', 's', 'f', 'd', 't', 'v', 'Description', 'Eff']

        # Check for the presence of each of the anticipated column headings
        for head in col_heads:
            self.assertTrue(head in self.sd_head, msg='Column ' + head +
                            (' is missing from the service demand data file.'))


class StructuredArrayStringProcessingTest(unittest.TestCase):
    """ Test function that processes strings stored in a column of a
    structured array to eliminate extraneous spaces and double quotes. """

    # Define a test array with strings like those in the Description
    # column of KSDOUT (with double quotes and extraneous spaces
    # both inside and outside of the quotes)
    string_format1 = np.array([
        (' "appliance_name 2012 minimum                "', 5),
        (' "other_device-model 2019 design standard    "', 3),
        (' "final product-2010 w/price $50 cond applied"', 9)],
        dtype=[('Column Name', '<U60'), ('Other', '<i4')])

    # Define the corresponding array with the strings cleaned up
    string_format1_clean = np.array([
        ('appliance_name 2012 minimum', 5),
        ('other_device-model 2019 design standard', 3),
        ('final product-2010 w/price $50 cond applied', 9)],
        dtype=[('Column Name', '<U60'), ('Other', '<i4')])

    # Define a test array with strings like those in the Label column
    # of KDBOUT (without double quotes)
    string_format2 = np.array([
        (' GenerallyNoSpaces            ', 12),
        (' With Spaces Just In Case     ', 39),
        (' WithSome&pecial/Chars        ', 16)],
        dtype=[('The Column', '<U50'), ('Other', '<i4')])

    # Define the corresponding array with the strings cleaned up
    string_format2_clean = np.array([
        ('GenerallyNoSpaces', 12),
        ('With Spaces Just In Case', 39),
        ('WithSome&pecial/Chars', 16)],
        dtype=[('The Column', '<U50'), ('Other', '<i4')])

    # Define a test array with strings like those in the Description
    # column of KSDOUT that have characters that appear using HTML
    # character encodings and are rewritten by the function for
    # later matching with the edited technology name strings in KTEK
    string_format3 = np.array([
        (' "F28T8 HE w/ OS &amp; SR 2020 typical        "', 9),
        (' "Range, Electric, 4 burner, oven, 11&quot; gr"', 23),
        (' "Range, Gas, 4 burner, oven, 11&quot; griddle"', 31)],
        dtype=[('Column to Test', '<U50'), ('Other', '<i4')])

    string_format3_clean = np.array([
        ('F28T8 HE w/ OS & SR 2020 typical', 9),
        ('Range, Electric, 4 burner, oven, 11-inch gr', 23),
        ('Range, Gas, 4 burner, oven, 11-inch griddle', 31)],
        dtype=[('Column to Test', '<U50'), ('Other', '<i4')])

    # Test processing of strings that have double quotes
    def test_string_processing_with_double_quotes(self):
        np.testing.assert_array_equal(
            cm.str_cleaner(self.string_format1, 'Column Name'),
            self.string_format1_clean)

    # Test processing of strings that only have extra spaces
    def test_string_processing_with_no_extraneous_quotes(self):
        np.testing.assert_array_equal(
            cm.str_cleaner(self.string_format2, 'The Column'),
            self.string_format2_clean)

    # Test processing of strings with HTML character encodings
    def test_string_processing_with_HTML_characters(self):
        np.testing.assert_array_equal(
            cm.str_cleaner(self.string_format3, 'Column to Test'),
            self.string_format3_clean)


class CommonUnitTest(unittest.TestCase):
    """ For simplicity and completeness in testing all possible cases
    for the subsequent tests, set up a common unittest.TestCase subclass
    that defines the state of data as it is acted on by each function
    tested in the commercial microsegment data processing code. """

    # Throughout, the following cases should be tested
    # [9, 10, 1, 2, 'GRND'] - DEMAND
    # [1, 5, 2, 1, 'PEOPLE'] - DEMAND
    # [4, 6, 10, 1, 11] - MEL
    # [5, 4, 10, 1, 2] - MEL
    # [2, 1, 2, 1] - SD
    # [8, 2, 3, 2] - SD
    # [4, 7, 6, 1] - (NEW) SD
    # [3, 7, 9, 1]
    # [7, 4, 5, 2]

    # Define a list of the end uses found in the service demand data
    sd_end_uses = [1, 2, 3, 4, 6, 7]

    # Set up a list of lists that would be recursively generated by the
    # walk function from the JSON database
    sample_keys = [['pacific', 'warehouse', 'natural gas',
                    'heating', 'demand', 'ground'],
                   ['new england', 'health care', 'electricity',
                    'cooling', 'demand', 'people gain'],
                   ['west north central', 'lodging', 'electricity',
                    'MELs', 'elevators'],
                   ['south atlantic', 'food service', 'electricity',
                    'MELs', 'kitchen ventilation'],
                   ['mid atlantic', 'assembly', 'electricity',
                    'cooling', 'supply'],
                   ['mountain', 'education', 'natural gas',
                    'water heating'],
                   ['west north central', 'large office', 'electricity',
                    'lighting'],
                   ['east north central', 'large office', 'electricity',
                    'non-PC office equipment'],
                   ['west south central', 'food service', 'natural gas',
                    'cooking'],
                   ['east south central', 'food sales', 'new square footage'],
                   ['pacific', 'mercantile/service', 'total square footage']]

    # Define array with identical data format to EIA data file KDBOUT
    # but only a few years for each entry to reduce the total number
    # of rows
    sample_db_array = np.array([
        (9, 10, 1, 2, 30,  1.503, 'EndUseConsump'),
        (9, 10, 1, 2, 31,  1.499, 'EndUseConsump'),
        (9, 10, 1, 2, 32,  1.493, 'EndUseConsump'),
        (1,  5, 2, 1, 30,  0.083, 'EndUseConsump'),
        (1,  5, 2, 1, 31,  0.081, 'EndUseConsump'),
        (1,  5, 2, 1, 32,  0.078, 'EndUseConsump'),
        (4,  6, 11, 1, 30,  0.101, 'MiscElConsump'),
        (4,  6, 11, 1, 31,  0.103, 'MiscElConsump'),
        (4,  6, 11, 1, 32,  0.106, 'MiscElConsump'),
        (5,  4, 2, 1, 30,  1.475, 'MiscElConsump'),
        (5,  4, 2, 1, 31,  1.484, 'MiscElConsump'),
        (5,  4, 2, 1, 32,  1.492, 'MiscElConsump'),
        (2,  1, 2, 1, 30,  2.430, 'EndUseConsump'),
        (2,  1, 2, 1, 31,  2.399, 'EndUseConsump'),
        (2,  1, 2, 1, 32,  2.360, 'EndUseConsump'),
        (8,  2, 3, 2, 30,  9.430, 'EndUseConsump'),
        (8,  2, 3, 2, 31,  9.373, 'EndUseConsump'),
        (8,  2, 3, 2, 32,  9.311, 'EndUseConsump'),
        (4,  7, 6, 1, 30,  3.641, 'EndUseConsump'),
        (4,  7, 6, 1, 31,  3.647, 'EndUseConsump'),
        (4,  7, 6, 1, 32,  3.654, 'EndUseConsump'),
        (3,  7, 9, 1, 30, 11.983, 'EndUseConsump'),
        (3,  7, 9, 1, 31, 12.165, 'EndUseConsump'),
        (3,  7, 9, 1, 32, 12.377, 'EndUseConsump'),
        (7,  4, 5, 2, 30, 24.763, 'EndUseConsump'),
        (7,  4, 5, 2, 31, 24.724, 'EndUseConsump'),
        (7,  4, 5, 2, 32, 24.733, 'EndUseConsump'),
        (6,  3, 0, 0, 30,  2.097, 'CMNewFloorSpace'),
        (6,  3, 0, 0, 31,  2.074, 'CMNewFloorSpace'),
        (6,  3, 0, 0, 32,  2.037, 'CMNewFloorSpace'),
        (9,  9, 0, 0, 30, 64.832, 'CMNewFloorSpace'),
        (9,  9, 0, 0, 31, 61.281, 'CMNewFloorSpace'),
        (9,  9, 0, 0, 32, 62.020, 'CMNewFloorSpace'),
        (9,  9, 0, 0, 30, 2484.2, 'SurvFloorTotal'),
        (9,  9, 0, 0, 31, 2515.2, 'SurvFloorTotal'),
        (9,  9, 0, 0, 32, 2542.1, 'SurvFloorTotal')],
        dtype=[('Division', 'i4'), ('BldgType', 'i4'),
               ('EndUse', 'i4'), ('Fuel', 'i4'), ('Year', 'i4'),
               ('Amount', 'f8'), ('Label', '<U50')])

    # Define array with identical data format to EIA service demand
    # data that provides the relevant supporting data for the cases
    # being tested that involve service demand data; note that for the
    # two sample cases tested, not all of the data were captured from
    # the service demand data in the interest of brevity and test speed;
    # placeholder lines were added to test the effective removal of those lines
    sample_sd_array = np.array([
        (2, 1, 2, 1, 1, 6, 1, 0.0, 0.0, 0.0,
         'rooftop_ASHP-cool 2003 installed base', 2.73),
        (2, 1, 2, 1, 2, 6, 1, 0.0, 0.0, 0.0,
         'rooftop_ASHP-cool 2003 installed base', 2.73),
        (2, 1, 2, 1, 3, 6, 1, 0.013, 0.012, 0.011,
         'rooftop_ASHP-cool 2003 installed base', 2.73),
        (2, 1, 2, 1, 1, 6, 2, 0.0, 0.0, 0.0,
         'rooftop_ASHP-cool 2012 installed base', 2.99),
        (2, 1, 2, 1, 2, 6, 2, 0.0, 0.0, 0.0,
         'rooftop_ASHP-cool 2012 installed base', 2.99),
        (2, 1, 2, 1, 3, 6, 2, 0.0, 0.0, 0.0,
         'rooftop_ASHP-cool 2012 installed base', 2.99),
        (2, 1, 2, 1, 1, 6, 3, 0.0, 0.0, 0.0,
         'rooftop_ASHP-cool 2013 current standard/ typ', 3.22),
        (2, 1, 2, 1, 2, 6, 3, 0.0, 0.0, 0.0,
         'rooftop_ASHP-cool 2013 current standard/ typ', 3.22),
        (2, 1, 2, 1, 3, 6, 3, 0.0, 0.0, 0.0,
         'rooftop_ASHP-cool 2013 current standard/ typ', 3.22),
        (2, 1, 2, 1, 1, 6, 4, 0.001, 0.0, 0.0,
         'rooftop_ASHP-cool 2013 ENERGY STAR', 3.31),
        (2, 1, 2, 1, 2, 6, 4, 0.007, 0.0, 0.0,
         'rooftop_ASHP-cool 2013 ENERGY STAR', 3.31),
        (2, 1, 2, 1, 3, 6, 4, 0.067, 0.069, 0.064,
         'rooftop_ASHP-cool 2013 ENERGY STAR', 3.31),
        (2, 1, 2, 1, 1, 6, 5, 0.0, 0.0, 0.0,
         'rooftop_ASHP-cool 2013 high', 3.52),
        (2, 1, 2, 1, 2, 6, 5, 0.0, 0.0, 0.0,
         'rooftop_ASHP-cool 2013 high', 3.52),
        (2, 1, 2, 1, 3, 6, 5, 0.0, 0.0, 0.0,
         'rooftop_ASHP-cool 2013 high', 3.52),
        (2, 1, 2, 1, 1, 6, 6, 0.0, 0.001, 0.001,
         'rooftop_ASHP-cool 2020 typical', 3.22),
        (2, 1, 2, 1, 2, 6, 6, 0.0, 0.007, 0.007,
         'rooftop_ASHP-cool 2020 typical', 3.22),
        (2, 1, 2, 1, 3, 6, 6, 0.0, 0.0, 0.007,
         'rooftop_ASHP-cool 2020 typical', 3.22),
        (2, 1, 2, 1, 1, 6, 7, 0.0, 0.0, 0.0,
         'rooftop_ASHP-cool 2020 high', 3.52),
        (2, 1, 2, 1, 2, 6, 7, 0.0, 0.0, 0.0,
         'rooftop_ASHP-cool 2020 high', 3.52),
        (2, 1, 2, 1, 3, 6, 7, 0.0, 0.0, 0.0,
         'rooftop_ASHP-cool 2020 high', 3.52),
        (2, 1, 2, 1, 1, 7, 1, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2003 installed base', 4.04),
        (2, 1, 2, 1, 2, 7, 1, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2003 installed base', 4.04),
        (2, 1, 2, 1, 3, 7, 1, 0.009, 0.009, 0.008,
         'comm_GSHP-cool 2003 installed base', 4.04),
        (2, 1, 2, 1, 1, 7, 2, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2012 installed base', 4.1),
        (2, 1, 2, 1, 2, 7, 2, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2012 installed base', 4.1),
        (2, 1, 2, 1, 3, 7, 2, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2012 installed base', 4.1),
        (2, 1, 2, 1, 1, 7, 3, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2013 typical', 5.01),
        (2, 1, 2, 1, 2, 7, 3, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2013 typical', 5.01),
        (2, 1, 2, 1, 3, 7, 3, 0.002, 0.002, 0.002,
         'comm_GSHP-cool 2013 typical', 5.01),
        (2, 1, 2, 1, 1, 7, 4, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2013 mid', 5.16),
        (2, 1, 2, 1, 2, 7, 4, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2013 mid', 5.16),
        (2, 1, 2, 1, 3, 7, 4, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2013 mid', 5.16),
        (2, 1, 2, 1, 1, 7, 5, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2013 high', 6.04),
        (2, 1, 2, 1, 2, 7, 5, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2013 high', 6.04),
        (2, 1, 2, 1, 3, 7, 5, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2013 high', 6.04),
        (2, 1, 2, 1, 1, 7, 6, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2020 typical', 5.28),
        (2, 1, 2, 1, 2, 7, 6, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2020 typical', 5.28),
        (2, 1, 2, 1, 3, 7, 6, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2020 typical', 5.28),
        (2, 1, 2, 1, 1, 7, 7, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2020 high', 6.45),
        (2, 1, 2, 1, 2, 7, 7, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2020 high', 6.45),
        (2, 1, 2, 1, 3, 7, 7, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2020 high', 6.45),
        (2, 1, 2, 1, 1, 7, 8, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2030 typical', 5.86),
        (2, 1, 2, 1, 2, 7, 8, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2030 typical', 5.86),
        (2, 1, 2, 1, 3, 7, 8, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2030 typical', 5.86),
        (2, 1, 2, 1, 1, 7, 9, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2030 high', 7.03),
        (2, 1, 2, 1, 2, 7, 9, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2030 high', 7.03),
        (2, 1, 2, 1, 3, 7, 9, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2030 high', 7.03),
        (2, 1, 2, 1, 1, 7, 10, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2013 typ 10% ITC w MACRS', 5.01),
        (2, 1, 2, 1, 2, 7, 10, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2013 typ 10% ITC w MACRS', 5.01),
        (2, 1, 2, 1, 3, 7, 10, 0.003, 0.002, 0.002,
         'comm_GSHP-cool 2013 typ 10% ITC w MACRS', 5.01),
        (2, 1, 2, 1, 1, 7, 11, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2013 mid 10% ITC w MACRS', 5.16),
        (2, 1, 2, 1, 2, 7, 11, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2013 mid 10% ITC w MACRS', 5.16),
        (2, 1, 2, 1, 3, 7, 11, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2013 mid 10% ITC w MACRS', 5.16),
        (2, 1, 2, 1, 1, 7, 12, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2013 high 10% ITC w MACRS', 6.04),
        (2, 1, 2, 1, 2, 7, 12, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2013 high 10% ITC w MACRS', 6.04),
        (2, 1, 2, 1, 3, 7, 12, 0.0, 0.0, 0.0,
         'comm_GSHP-cool 2013 high 10% ITC w MACRS', 6.04),
        (2, 1, 2, 1, 1, 54, 1, 0.0, 0.0, 0.0,
         'res_type_central_AC 2003 installed base', 3.34),
        (2, 1, 2, 1, 2, 54, 1, 0.0, 0.0, 0.0,
         'res_type_central_AC 2003 installed base', 3.34),
        (2, 1, 2, 1, 3, 54, 1, 0.645, 0.595, 0.549,
         'res_type_central_AC 2003 installed base', 3.34),
        (2, 1, 2, 1, 1, 54, 2, 0.004, 0.004, 0.004,
         'res_type_central_AC 2013 current standard', 3.81),
        (2, 1, 2, 1, 2, 54, 2, 0.082, 0.08, 0.079,
         'res_type_central_AC 2013 current standard', 3.81),
        (2, 1, 2, 1, 3, 54, 2, 0.831, 0.847, 0.86,
         'res_type_central_AC 2013 current standard', 3.81),
        (2, 1, 2, 1, 1, 54, 3, 0.0, 0.0, 0.0,
         'res_type_central_AC 2013 typical', 3.81),
        (2, 1, 2, 1, 2, 54, 3, 0.0, 0.0, 0.0,
         'res_type_central_AC 2013 typical', 3.81),
        (2, 1, 2, 1, 3, 54, 3, 0.0, 0.0, 0.0,
         'res_type_central_AC 2013 typical', 3.81),
        (2, 1, 2, 1, 1, 54, 4, 0.0, 0.0, 0.0,
         'res_type_central_AC 2013 ENERGY STAR', 4.25),
        (2, 1, 2, 1, 2, 54, 4, 0.0, 0.0, 0.0,
         'res_type_central_AC 2013 ENERGY STAR', 4.25),
        (2, 1, 2, 1, 3, 54, 4, 0.013, 0.012, 0.012,
         'res_type_central_AC 2013 ENERGY STAR', 4.25),
        (2, 1, 2, 1, 1, 54, 5, 0.0, 0.0, 0.0,
         'res_type_central_AC 2013 high', 7.03),
        (2, 1, 2, 1, 2, 54, 5, 0.0, 0.0, 0.0,
         'res_type_central_AC 2013 high', 7.03),
        (2, 1, 2, 1, 3, 54, 5, 0.0, 0.0, 0.0,
         'res_type_central_AC 2013 high', 7.03),
        (2, 1, 2, 1, 1, 54, 6, 0.0, 0.0, 0.0,
         'res_type_central_AC 2020 typical', 4.1),
        (2, 1, 2, 1, 2, 54, 6, 0.011, 0.011, 0.011,
         'res_type_central_AC 2020 typical', 4.1),
        (2, 1, 2, 1, 3, 54, 6, 0.105, 0.108, 0.11,
         'res_type_central_AC 2020 typical', 4.1),
        (2, 1, 2, 1, 1, 54, 7, 0.0, 0.0, 0.0,
         'res_type_central_AC 2020 high', 7.03),
        (2, 1, 2, 1, 2, 54, 7, 0.0, 0.0, 0.0,
         'res_type_central_AC 2020 high', 7.03),
        (2, 1, 2, 1, 3, 54, 7, 0.0, 0.0, 0.0,
         'res_type_central_AC 2020 high', 7.03),
        (2, 1, 2, 1, 1, 54, 8, 0.0, 0.0, 0.0,
         'res_type_central_AC 2030 typical', 4.1),
        (2, 1, 2, 1, 2, 54, 8, 0.0, 0.0, 0.0,
         'res_type_central_AC 2030 typical', 4.1),
        (2, 1, 2, 1, 3, 54, 8, 0.0, 0.0, 0.0,
         'res_type_central_AC 2030 typical', 4.1),
        (2, 1, 2, 1, 1, 54, 1, 0.0, 0.0, 0.0,
         'res_type_gasHP-cool placeholder to reconcile', 0.01),
        (2, 1, 2, 1, 2, 54, 1, 0.0, 0.0, 0.0,
         'res_type_gasHP-cool placeholder to reconcile', 0.01),
        (2, 1, 2, 1, 3, 54, 1, 0.0, 0.0, 0.0,
         'res_type_gasHP-cool placeholder to reconcile', 0.01),
        (8, 2, 3, 2, 1, 22, 1, 0.0, 0.0, 0.0,
         'gas_instantaneous_WH 2003 installed base', 0.76),
        (8, 2, 3, 2, 2, 22, 1, 0.0, 0.0, 0.0,
         'gas_instantaneous_WH 2003 installed base', 0.76),
        (8, 2, 3, 2, 3, 22, 1, 0.0, 0.0, 0.0,
         'gas_instantaneous_WH 2003 installed base', 0.76),
        (8, 2, 3, 2, 1, 22, 2, 0.0, 0.0, 0.0,
         'gas_instantaneous_WH 2012 installed base', 0.78),
        (8, 2, 3, 2, 2, 22, 2, 0.0, 0.0, 0.0,
         'gas_instantaneous_WH 2012 installed base', 0.78),
        (8, 2, 3, 2, 3, 22, 2, 0.0, 0.0, 0.0,
         'gas_instantaneous_WH 2012 installed base', 0.78),
        (8, 2, 3, 2, 1, 22, 3, 0.0, 0.0, 0.0,
         'gas_instantaneous_WH 2013 current standard', 0.8),
        (8, 2, 3, 2, 2, 22, 3, 0.0, 0.0, 0.0,
         'gas_instantaneous_WH 2013 current standard', 0.8),
        (8, 2, 3, 2, 3, 22, 3, 0.0, 0.0, 0.0,
         'gas_instantaneous_WH 2013 current standard', 0.8),
        (8, 2, 3, 2, 1, 22, 4, 0.0, 0.0, 0.0,
         'gas_instantaneous_WH 2013 typical', 0.89),
        (8, 2, 3, 2, 2, 22, 4, 0.0, 0.0, 0.0,
         'gas_instantaneous_WH 2013 typical', 0.89),
        (8, 2, 3, 2, 3, 22, 4, 0.0, 0.0, 0.0,
         'gas_instantaneous_WH 2013 typical', 0.89),
        (8, 2, 3, 2, 1, 22, 5, 0.0, 0.0, 0.0,
         'gas_instantaneous_WH 2013 high', 0.97),
        (8, 2, 3, 2, 2, 22, 5, 0.0, 0.0, 0.0,
         'gas_instantaneous_WH 2013 high', 0.97),
        (8, 2, 3, 2, 3, 22, 5, 0.0, 0.0, 0.0,
         'gas_instantaneous_WH 2013 high', 0.97),
        (8, 2, 3, 2, 1, 57, 1, 0.0, 0.0, 0.0,
         'gas_water_heater  2003 installed base', 0.77),
        (8, 2, 3, 2, 2, 57, 1, 0.0, 0.0, 0.0,
         'gas_water_heater  2003 installed base', 0.77),
        (8, 2, 3, 2, 3, 57, 1, 0.624, 0.57, 0.521,
         'gas_water_heater  2003 installed base', 0.77),
        (8, 2, 3, 2, 1, 57, 2, 0.038, 0.037, 0.035,
         'gas_water_heater  2013 current standard/ typ', 0.8),
        (8, 2, 3, 2, 2, 57, 2, 0.151, 0.153, 0.155,
         'gas_water_heater  2013 current standard/ typ', 0.8),
        (8, 2, 3, 2, 3, 57, 2, 2.046, 2.043, 2.04,
         'gas_water_heater  2013 current standard/ typ', 0.8),
        (8, 2, 3, 2, 1, 57, 3, 0.036, 0.035, 0.034,
         'gas_water_heater  2013 high', 0.99),
        (8, 2, 3, 2, 2, 57, 3, 0.144, 0.146, 0.147,
         'gas_water_heater  2013 high', 0.99),
        (8, 2, 3, 2, 3, 57, 3, 0.806, 0.905, 0.995,
         'gas_water_heater  2013 high', 0.99),
        (8, 2, 3, 2, 1, 57, 4, 0.0, 0.0, 0.0,
         'gas_water_heater  2020 typical', 0.8),
        (8, 2, 3, 2, 2, 57, 4, 0.0, 0.0, 0.0,
         'gas_water_heater  2020 typical', 0.8),
        (8, 2, 3, 2, 3, 57, 4, 0.0, 0.0, 0.0,
         'gas_water_heater  2020 typical', 0.8),
        (8, 2, 3, 2, 1, 57, 5, 0.0, 0.0, 0.0,
         'gas_water_heater  2020 high', 0.99),
        (8, 2, 3, 2, 2, 57, 5, 0.0, 0.0, 0.0,
         'gas_water_heater  2020 high', 0.99),
        (8, 2, 3, 2, 3, 57, 5, 0.0, 0.0, 0.0,
         'gas_water_heater  2020 high', 0.99),
        (4, 7, 6, 1, 1, 24, 15, 0, 0, 0,
         '90W Halogen PAR-38 2003 installed base', 13.5),
        (4, 7, 6, 1, 2, 24, 15, 0, 0, 0,
         '90W Halogen PAR-38 2003 installed base', 13.5),
        (4, 7, 6, 1, 3, 24, 15, 0.077, 0.069, 0.062,
         '90W Halogen PAR-38 2003 installed base', 13.5),
        (4, 7, 6, 1, 1, 24, 16, 0, 0, 0,
         '90W Halogen PAR-38 2007 installed base', 13.5),
        (4, 7, 6, 1, 2, 24, 16, 0, 0, 0,
         '90W Halogen PAR-38 2007 installed base', 13.5),
        (4, 7, 6, 1, 3, 24, 16, 0.047, 0.042, 0.038,
         '90W Halogen PAR-38 2007 installed base', 13.5),
        (4, 7, 6, 1, 1, 24, 17, 0, 0, 0,
         '90W Halogen PAR-38 2011 typical', 13.7),
        (4, 7, 6, 1, 2, 24, 17, 0, 0, 0,
         '90W Halogen PAR-38 2011 typical', 13.7),
        (4, 7, 6, 1, 3, 24, 17, 0, 0, 0,
         '90W Halogen PAR-38 2011 typical', 13.7),
        (4, 7, 6, 1, 1, 24, 18, 0, 0, 0,
         '90W Halogen PAR-38 2020 typical', 14.34),
        (4, 7, 6, 1, 2, 24, 18, 0, 0, 0,
         '90W Halogen PAR-38 2020 typical', 14.34),
        (4, 7, 6, 1, 3, 24, 18, 0, 0, 0,
         '90W Halogen PAR-38 2020 typical', 14.34),
        (4, 7, 6, 1, 1, 24, 19, 0, 0, 0,
         '90W Halogen PAR-38 2030 typical', 15.06),
        (4, 7, 6, 1, 2, 24, 19, 0, 0, 0,
         '90W Halogen PAR-38 2030 typical', 15.06),
        (4, 7, 6, 1, 3, 24, 19, 0, 0, 0,
         '90W Halogen PAR-38 2030 typical', 15.06),
        (4, 7, 6, 1, 1, 25, 2, 0, 0, 0,
         'T8 2e),', 59),
        (4, 7, 6, 1, 2, 25, 2, 0, 0, 0,
         'T8 2e),', 59),
        (4, 7, 6, 1, 3, 25, 2, 0.039, 0.036, 0.034,
         'T8 2e),', 59),
        (4, 7, 6, 1, 1, 25, 15, 0.088, 0, 0,
         'F28T8 HE w/ OS &amp; SR 2011 typical', 178.7),
        (4, 7, 6, 1, 2, 25, 15, 0.262, 0, 0,
         'F28T8 HE w/ OS &amp; SR 2011 typical', 178.7),
        (4, 7, 6, 1, 3, 25, 15, 1.868, 2.048, 1.892,
         'F28T8 HE w/ OS &amp; SR 2011 typical', 178.7),
        (4, 7, 6, 1, 1, 25, 16, 0, 0.016, 0.016,
         'F28T8 HE w/ OS &amp; SR 2020 typical', 192.14),
        (4, 7, 6, 1, 2, 25, 16, 0, 0.045, 0.046,
         'F28T8 HE w/ OS &amp; SR 2020 typical', 192.14),
        (4, 7, 6, 1, 3, 25, 16, 0, 0.012, 0.077,
         'F28T8 HE w/ OS &amp; SR 2020 typical', 192.14),
        (4, 7, 6, 1, 1, 25, 17, 0, 0, 0,
         'F28T8 HE w/ OS &amp; SR 2030 typical', 195.29),
        (4, 7, 6, 1, 2, 25, 17, 0, 0, 0,
         'F28T8 HE w/ OS &amp; SR 2030 typical', 195.29),
        (4, 7, 6, 1, 3, 25, 17, 0, 0, 0,
         'F28T8 HE w/ OS &amp; SR 2030 typical', 195.29),
        (4, 7, 6, 1, 1, 27, 2, 0, 0, 0,
         'MH 175_LB 2003 installed base', 31.8),
        (4, 7, 6, 1, 2, 27, 2, 0, 0, 0,
         'MH 175_LB 2003 installed base', 31.8),
        (4, 7, 6, 1, 3, 27, 2, 0.018, 0.016, 0.014,
         'MH 175_LB 2003 installed base', 31.8),
        (4, 7, 6, 1, 1, 27, 3, 0, 0, 0,
         'MH 175_LB 2007 installed base', 34.01),
        (4, 7, 6, 1, 2, 27, 3, 0, 0, 0,
         'MH 175_LB 2007 installed base', 34.01),
        (4, 7, 6, 1, 3, 27, 3, 0, 0, 0,
         'MH 175_LB 2007 installed base', 34.01),
        (4, 7, 6, 1, 1, 27, 4, 0, 0, 0,
         'MH 175_LB 2011 typical', 51.22),
        (4, 7, 6, 1, 2, 27, 4, 0, 0, 0,
         'MH 175_LB 2011 typical', 51.22),
        (4, 7, 6, 1, 3, 27, 4, 0, 0, 0,
         'MH 175_LB 2011 typical', 51.22),
        (4, 7, 6, 1, 1, 27, 5, 0, 0, 0,
         'MH 175_LB 2020 typical/ 2017 standard', 52.76),
        (4, 7, 6, 1, 2, 27, 5, 0, 0, 0,
         'MH 175_LB 2020 typical/ 2017 standard', 52.76),
        (4, 7, 6, 1, 3, 27, 5, 0, 0, 0,
         'MH 175_LB 2020 typical/ 2017 standard', 52.76),
        (4, 7, 6, 1, 1, 27, 6, 0, 0, 0,
         'MH 175_LB 2030 typical', 54.47),
        (4, 7, 6, 1, 2, 27, 6, 0, 0, 0,
         'MH 175_LB 2030 typical', 54.47),
        (4, 7, 6, 1, 3, 27, 6, 0, 0, 0,
         'MH 175_LB 2030 typical', 54.47),
        (4, 7, 6, 1, 1, 27, 11, 0, 0, 0,
         '2L F54T5HO LB', 67.8),
        (4, 7, 6, 1, 2, 27, 11, 0, 0, 0,
         '2L F54T5HO LB', 67.8),
        (4, 7, 6, 1, 3, 27, 11, 0, 0, 0,
         '2L F54T5HO LB', 67.8),
        (1,  1,  7,  1,  1, 45,  1, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 201', 2.85),
        (1,  1,  7,  1,  2, 45,  1, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 201', 2.85),
        (1,  1,  7,  1,  3, 45,  1, 0.055, 0.050, 0.046,
         'Commercial Refrigerated Vending Machines 201', 2.85),
        (1,  1,  7,  1,  1, 45,  2, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 201', 2.70),
        (1,  1,  7,  1,  2, 45,  2, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 201', 2.70),
        (1,  1,  7,  1,  3, 45,  2, 0.030, 0.027, 0.025,
         'Commercial Refrigerated Vending Machines 201', 2.70),
        (1,  1,  7,  1,  1, 45,  3, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 201', 2.85),
        (1,  1,  7,  1,  2, 45,  3, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 201', 2.85),
        (1,  1,  7,  1,  3, 45,  3, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 201', 2.85),
        (1,  1,  7,  1,  1, 45,  4, 0.001, 0.001, 0.001,
         'Commercial Refrigerated Vending Machines 201', 3.09),
        (1,  1,  7,  1,  2, 45,  4, 0.007, 0.007, 0.007,
         'Commercial Refrigerated Vending Machines 201', 3.09),
        (1,  1,  7,  1,  3, 45,  4, 0.008, 0.015, 0.022,
         'Commercial Refrigerated Vending Machines 201', 3.09),
        (1,  1,  7,  1,  1, 45,  5, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 201', 3.09),
        (1,  1,  7,  1,  2, 45,  5, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 201', 3.09),
        (1,  1,  7,  1,  3, 45,  5, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 201', 3.09),
        (1,  1,  7,  1,  1, 45,  6, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 202', 3.42),
        (1,  1,  7,  1,  2, 45,  6, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 202', 3.42),
        (1,  1,  7,  1,  3, 45,  6, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 202', 3.42),
        (1,  1,  7,  1,  1, 45,  7, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 202', 3.60),
        (1,  1,  7,  1,  2, 45,  7, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 202', 3.60),
        (1,  1,  7,  1,  3, 45,  7, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 202', 3.60),
        (1,  1,  7,  1,  1, 45,  8, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 203', 3.52),
        (1,  1,  7,  1,  2, 45,  8, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 203', 3.52),
        (1,  1,  7,  1,  3, 45,  8, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 203', 3.52),
        (1,  1,  7,  1,  1, 45,  9, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 203', 3.71),
        (1,  1,  7,  1,  2, 45,  9, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 203', 3.71),
        (1,  1,  7,  1,  3, 45,  9, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 203', 3.71),
        (1,  1,  7,  1,  1, 45, 10, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 204', 3.59),
        (1,  1,  7,  1,  2, 45, 10, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 204', 3.59),
        (1,  1,  7,  1,  3, 45, 10, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 204', 3.59),
        (1,  1,  7,  1,  1, 45, 11, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 204', 3.78),
        (1,  1,  7,  1,  2, 45, 11, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 204', 3.78),
        (1,  1,  7,  1,  3, 45, 11, 0.000, 0.000, 0.000,
         'Commercial Refrigerated Vending Machines 204', 3.78)],
        dtype=[('r', '<i4'), ('b', '<i4'), ('s', '<i4'), ('f', '<i4'),
               ('d', '<i4'), ('t', '<i4'), ('v', '<i4'),
               ('2019', '<f8'), ('2020', '<f8'), ('2021', '<f8'),
               ('Description', '<U50'), ('Eff', '<f8')])

    # Define list of years over which service demand data are reported
    years = list(range(2019, 2022))

    # Define array similar to the thermal loads data, but with only the
    # data required to test the sample cases explored here (plus an
    # extra that can be added later, if desired)
    sample_tl_array = np.array([
        ('HT', 9, 10, -0.2964, -0.069, 1.0994),
        ('CL', 1, 5, 0.1338, 0.084, 0.0),
        ('CL', 2, 1, 0.448, 0.0956, -0.0427)],
        dtype=[('ENDUSE', '<U50'), ('CDIV', '<i4'), ('BLDG', '<i4'),
               ('WIND_SOL', '<f8'), ('PEOPLE', '<f8'), ('GRND', '<f8')])

    # Define list outputs from the key conversion function
    sample_keys_converted = [[9, 10, 1, 2, 'GRND'],
                             [1, 5, 2, 1, 'PEOPLE'],
                             [4, 6, 10, 1, 11],
                             [5, 4, 10, 1, 2],
                             [2, 1, 2, 1],
                             [8, 2, 3, 2],
                             [4, 7, 6, 1],
                             [3, 7, 9, 1],
                             [7, 4, 5, 2],
                             [6, 3],
                             [9, 9]]

    # Define sample lists that either a) do not have keys in the
    # correct order to be converted (and should not appear in this
    # order in the JSON file) or b) include keys that are not
    # applicable to commercial buildings and should raise an error
    # or exception
    fail_keys = [['new england', 'mobile home', 'electricity',
                  'cooling', 'demand', 'people gain'],
                 ['west south central', 'single family home', 'natural gas',
                  'water heating'],
                 ['west north central', 'cooking', 'natural gas',
                  'drying'],
                 ['pacific', 'large office', 'security systems',
                  'distillate'],
                 ['neptune', 'education', 'distillate',
                  'heating', 'supply'],
                 ['mountain', 'small office', 'lamp oil',
                  'lighting']]

    # Define lists that specify the census division, building type,
    # end use, and fuel type from which to select the desired data
    selections = [[2, 1, 2, 1],
                  [8, 2, 3, 2],
                  [4, 7, 6, 1],
                  [1, 1, 7, 1]]

    technames = [['comm_GSHP-cool',
                  'res_type_central_AC',
                  'rooftop_ASHP-cool'],
                 ['gas_instantaneous_WH',
                  'gas_water_heater'],
                 ['2L F54T5HO LB',
                  '90W Halogen PAR-38',
                  'F28T8 HE w/ OS &amp; SR',
                  'MH 175_LB',
                  'T8 2e),'],
                 ['Commercial Refrigerated Vending Machines']]

    sd_percentages = [np.array([[0.00650618, 0.00623814, 0.0058495],
                                [0.93818754, 0.93660672, 0.93515652],
                                [0.05530627, 0.05715514, 0.05899398]]),
                      np.array([[0.0, 0.0, 0.0],
                                [1.0, 1.0, 1.0]]),
                      np.array([[0.0, 0.0, 0.0],
                                [0.40243356, 0.38827994, 0.37534485],
                                [0.54380509, 0.55914576, 0.57314636],
                                [0.0248, 0.02376012, 0.02230823],
                                [0.02896135, 0.02881418, 0.02920056]])]

    # List of booleans indicating whether the selection comes from the
    # MELs rows in the array
    MEL_status = [False, False, True, True, False, False, False, False, False,
                  False, False]

    # Define list of expected numpy structured arrays generated by
    # the function to be tested
    expected_selection = [np.array([('2019', 1.503),
                                    ('2020', 1.499),
                                    ('2021', 1.493)],
                                   dtype=[('Year', 'U4'), ('Amount', 'f8')]),
                          np.array([('2019', 0.083),
                                    ('2020', 0.081),
                                    ('2021', 0.078)],
                                   dtype=[('Year', 'U4'), ('Amount', 'f8')]),
                          np.array([('2019', 0.101),
                                    ('2020', 0.103),
                                    ('2021', 0.106)],
                                   dtype=[('Year', 'U4'), ('Amount', 'f8')]),
                          np.array([('2019', 1.475),
                                    ('2020', 1.484),
                                    ('2021', 1.492)],
                                   dtype=[('Year', 'U4'), ('Amount', 'f8')]),
                          np.array([('2019', 2.430),
                                    ('2020', 2.399),
                                    ('2021', 2.360)],
                                   dtype=[('Year', 'U4'), ('Amount', 'f8')]),
                          np.array([('2019', 9.430),
                                    ('2020', 9.373),
                                    ('2021', 9.311)],
                                   dtype=[('Year', 'U4'), ('Amount', 'f8')]),
                          np.array([('2019', 3.641),
                                    ('2020', 3.647),
                                    ('2021', 3.654)],
                                   dtype=[('Year', 'U4'), ('Amount', 'f8')]),
                          np.array([('2019', 11.983),
                                    ('2020', 12.165),
                                    ('2021', 12.377)],
                                   dtype=[('Year', 'U4'), ('Amount', 'f8')]),
                          np.array([('2019', 24.763),
                                    ('2020', 24.724),
                                    ('2021', 24.733)],
                                   dtype=[('Year', 'U4'), ('Amount', 'f8')]),
                          np.array([('2019', 2.097),
                                    ('2020', 2.074),
                                    ('2021', 2.037)],
                                   dtype=[('Year', 'U4'), ('Amount', 'f8')]),
                          np.array([('2019', 2484.2),
                                    ('2020', 2515.2),
                                    ('2021', 2542.1)],
                                   dtype=[('Year', 'U4'), ('Amount', 'f8')])]

    # Final dicts in the form that should be produced by the function
    # under test, in the same order as the sample_keys list
    dict_list = [
        {'energy': {'2019': 1652398.2, '2020': 1648000.6, '2021': 1641404.2},
         'stock': 'NA'},
        {'energy': {'2019': 6972, '2020': 6804, '2021': 6552},
         'stock': 'NA'},
        {'energy': {'2019': 101000, '2020': 103000, '2021': 106000},
         'stock': 'NA'},
        {'energy': {'2019': 1475000, '2020': 1484000, '2021': 1492000},
         'stock': 'NA'},
        {'rooftop_ASHP-cool':
            {'energy':
                {'2019': 134394.24, '2020': 137115.18, '2021': 139225.79},
             'stock':
                {'2019': 0.088, '2020': 0.089, '2021': 0.09}},
         'comm_GSHP-cool':
            {'energy':
                {'2019': 15810.03, '2020': 14965.3, '2021': 13804.82},
             'stock':
                {'2019': 0.014, '2020': 0.013, '2021': 0.013}},
         'res_type_central_AC':
            {'energy':
                {'2019': 2279795.73, '2020': 2246919.53, '2021': 2206969.39},
             'stock':
                {'2019': 1.691, '2020': 1.657, '2021': 1.625}}},
        {'gas_instantaneous_WH':
            {'energy':
                {'2019': 0, '2020': 0, '2021': 0},
             'stock':
                {'2019': 0, '2020': 0, '2021': 0}},
         'gas_water_heater':
            {'energy':
                {'2019': 9430000, '2020': 9373000, '2021': 9311000},
             'stock':
                {'2019': 3.845, '2020': 3.889, '2021': 3.927}}},
        {'2L F54T5HO LB':
            {'energy':
                {'2019': 0.0, '2020': 0.0, '2021': 0.0},
             'stock':
                {'2019': 0, '2020': 0, '2021': 0}},
         '90W Halogen PAR-38':
            {'energy':
                {'2019': 1465260.60, '2020': 1416056.94, '2021': 1371510.1},
             'stock':
                {'2019': 0.124, '2020': 0.111, '2021': 0.1}},
         'F28T8 HE w/ OS &amp; SR':
            {'energy':
                {'2019': 1979994.32, '2020': 2039204.6, '2021': 2094276.79},
             'stock':
                {'2019': 2.218, '2020': 2.121, '2021': 2.031}},
         'MH 175_LB':
            {'energy':
                {'2019': 90296.8, '2020': 86653.15, '2021': 81514.28},
             'stock':
                {'2019': 0.018, '2020': 0.016, '2021': 0.014}},
         'T8 2e),':
            {'energy':
                {'2019': 105448.29, '2020': 105085.31, '2021': 106698.84},
             'stock':
                {'2019': 0.039, '2020': 0.036, '2021': 0.034}}},
        {'energy': {'2019': 11983000, '2020': 12165000, '2021': 12377000},
         'stock': 'NA'},
        {'energy': {'2019': 24763000, '2020': 24724000, '2021': 24733000},
         'stock': 'NA'},
        {'2019': 2.097, '2020': 2.074, '2021': 2.037},
        {'2019': 2549.03, '2020': 2576.48, '2021': 2604.12}]


class JSONInterpretationTest(CommonUnitTest):
    """ Test the conversion of lists of keys from the JSON database
    into lists that can be used to select data from the appropriate
    EIA or thermal loads (i.e., "demand") data record """

    # Test that the keys that should convert cleanly do not raise any
    # exceptions
    def test_expected_succesful_key_conversion(self):
        for idx, a_key_list in enumerate(self.sample_keys):
            self.assertEqual(cm.json_interpreter(a_key_list),
                             self.sample_keys_converted[idx])

    # Test that the keys intended to fail all successfully raise the
    # expected KeyError
    def test_expected_failing_key_conversion(self):
        for a_key_list in self.fail_keys:
            with self.assertRaises(KeyError):
                cm.json_interpreter(a_key_list)


class PercentageCalculationTest(CommonUnitTest):
    """ Test function that converts service demand data from the EIA
    data file into percentages of the total reported energy use for the
    specified census division, building type, end use, and fuel type. """
    # Note that the service demand is only characterized for some end uses

    # Run both example selections with the service demand reprocessing
    # function and save outputs for testing
    @classmethod
    def setUpClass(self):  # so that set up is run once for the entire class
        (self.a_abs, self.a_pct, self.b) = cm.sd_mseg_percent(
            self.sample_sd_array, self.selections[0], self.years)
        (self.c_abs, self.c_pct, self.d) = cm.sd_mseg_percent(
            self.sample_sd_array, self.selections[1], self.years)
        (self.e_abs, self.e_pct, self.f) = cm.sd_mseg_percent(
            self.sample_sd_array, self.selections[2], self.years)
        (self.g_abs, self.g_pct, self.h) = cm.sd_mseg_percent(
            self.sample_sd_array, self.selections[3], self.years)

    # Test technology type name capture/identification
    def test_service_demand_name_identification(self):
        self.assertEqual(self.b, self.technames[0])
        self.assertEqual(self.d, self.technames[1])
        self.assertEqual(self.f, self.technames[2])
        self.assertEqual(self.h, self.technames[3])

    # Test energy percentage contribution calculation (correcting for
    # potential floating point precision problems)
    def test_service_demand_percentage_conversion(self):
        self.assertTrue(
            (np.round(
                self.a_pct - self.sd_percentages[0], decimals=5) == 0).all())
        self.assertTrue(
            (np.round(
                self.c_pct - self.sd_percentages[1], decimals=5) == 0).all())
        self.assertTrue(
            (np.round(
                self.e_pct - self.sd_percentages[2], decimals=5) == 0).all())


class CommercialDataSelectionTest(CommonUnitTest):
    """ Test function that selects a subset of data from the combined
    commercial building energy and characteristics array and outputs
    that subset with the years adjusted based on the pivot year """

    # Test correct selection and conversion
    def test_data_selection_and_reduction(self):
        for idx, the_keys in enumerate(self.sample_keys):

            catg_code = self.sample_keys_converted[idx]

            # If the target data are for MELs, modify the numeric
            # indices used to select the appropriate data
            if self.MEL_status[idx]:
                correct_label_str = 'MiscElConsump'
                # Normally performed automatically in the data_handler
                # function prior to calling the catg_data_selector
                # function, implemented slightly differently here to
                # avoid modification of sample_keys_converted
                select_indices = [catg_code[0], catg_code[1], catg_code[4],
                                  catg_code[3], catg_code[4]]
            elif 'new square footage' in the_keys:
                correct_label_str = 'CMNewFloorSpace'
                select_indices = catg_code
            elif 'total square footage' in the_keys:
                # In an actual calculation of the total square footage,
                # both the new and surviving square footage would be
                # required, but since the new square footage data are
                # already being tested, here only the surviving floor
                # space is checked
                correct_label_str = 'SurvFloorTotal'
                select_indices = catg_code
            else:
                correct_label_str = 'EndUseConsump'
                select_indices = catg_code

            np.testing.assert_array_equal(
                cm.catg_data_selector(self.sample_db_array,
                                      select_indices,
                                      correct_label_str,
                                      self.years),
                self.expected_selection[idx])


class DataToFinalDictAtLeafNodeRestructuringTest(CommonUnitTest):
    """ Test function that handles selection of the appropriate data
    and any required restructuring or reprocessing to convert it into a
    dict formatted for insertion into the microsegments JSON """

    def dict_check(self, dict1, dict2, msg=None):
        """Compare two dicts for equality, allowing for floating point error.
        """

        # zip() and zip_longest() produce tuples for the items
        # identified, where in the case of a dict, the first item
        # in the tuple is the key and the second item is the value;
        # in the case where the dicts are not of identical size,
        # zip_longest() will use the fillvalue created below as a
        # substitute in the dict that has missing content; this
        # value is given as a tuple to be of comparable structure
        # to the normal output from zip_longest()
        fill_val = ('substituted entry', 5.2)

        # In this structure, k and k2 are the keys that correspond to
        # the dicts or unitary values that are found in i and i2,
        # respectively, at the current level of the recursive
        # exploration of dict1 and dict2, respectively
        for (k, i), (k2, i2) in itertools.zip_longest(sorted(dict1.items()),
                                                      sorted(dict2.items()),
                                                      fillvalue=fill_val):

            # Confirm that at the current location in the dict structure,
            # the keys are equal; this should fail if one of the dicts
            # is empty, is missing section(s), or has different key names
            self.assertEqual(k, k2)

            # If the recursion has not yet reached the terminal/leaf node
            if isinstance(i, dict):
                # Test that the dicts from the current keys are equal
                self.assertCountEqual(i, i2)
                # Continue to recursively traverse the dict
                self.dict_check(i, i2)

            # At the terminal/leaf node
            else:
                # Compare the values, allowing for floating point inaccuracy
                self.assertAlmostEqual(dict1[k], dict2[k2], places=2)

    # Test each if/else data condition in the data_handler function separately
    def test_restructuring_cases_with_thermal_loads(self):
        for i in [0, 1]:
            self.dict_check(cm.data_handler(self.sample_db_array,
                                            self.sample_sd_array,
                                            self.sample_tl_array,
                                            self.sample_keys[i],
                                            self.sd_end_uses,
                                            self.years),
                            self.dict_list[i])

    def test_restructuring_cases_with_miscellaneous_electric_loads(self):
        for i in [2, 3]:
            self.dict_check(cm.data_handler(self.sample_db_array,
                                            self.sample_sd_array,
                                            self.sample_tl_array,
                                            self.sample_keys[i],
                                            self.sd_end_uses,
                                            self.years),
                            self.dict_list[i])

    def test_restructuring_cases_with_service_demand_data(self):
        for i in [4, 5, 6]:
            self.dict_check(cm.data_handler(self.sample_db_array,
                                            self.sample_sd_array,
                                            self.sample_tl_array,
                                            self.sample_keys[i],
                                            self.sd_end_uses,
                                            self.years),
                            self.dict_list[i])

    def test_restructuring_all_other_cases(self):
        for i in [7, 8]:
            self.dict_check(cm.data_handler(self.sample_db_array,
                                            self.sample_sd_array,
                                            self.sample_tl_array,
                                            self.sample_keys[i],
                                            self.sd_end_uses,
                                            self.years),
                            self.dict_list[i])

    def test_restructuring_square_footage_data(self):
        for i in [9, 10]:
            self.dict_check(cm.data_handler(self.sample_db_array,
                                            self.sample_sd_array,
                                            self.sample_tl_array,
                                            self.sample_keys[i],
                                            self.sd_end_uses,
                                            self.years),
                            self.dict_list[i])


class TestOtherElectricLoadDoubleCountingCleanup(unittest.TestCase):
    """Test function that cleans up double-counting of some electric technologies

    After processing the commercial energy and stock data from NEMS, some commercial building
    types and end uses have double-counted electricity use. This test checks the function that
    cleans up these cases of double counting.

    Electricity use is double-counted in two places.
    1. For all commercial building types except "unspecified", specific named MELs technologies
       are double-counted in the MELs "other" technology type.
    2. For the unspecified building type, the "water systems" and "telecom systems" MELs are
       double-counted in the "unspecified" end use (not MELs > other, which is not present for
       the unspecified building type)
    """

    # Specify list of years (as strings) of dummy data in the test dicts
    years = ['2018', '2019', '2020']

    # Test dict structure matching the structure of the commercial data after processing by
    # com_mseg.py but before any corrections are applied to correct double counting
    # For testing double-counting of specific MELs technologies in other
    mels_other_pre = {
        "new england": {
            "large office": {
                "electricity": {
                    "MELs": {
                        "distribution transformers": {
                            "energy": {
                                "2018": 8,
                                "2019": 6,
                                "2020": 4,
                            },
                            "stock": "NA"
                        },
                        "televisions": {
                            "energy": {
                                "2018": 5,
                                "2019": 6,
                                "2020": 7,
                            },
                            "stock": "NA"
                        },
                        "water services": {
                            "energy": {},
                            "stock": "NA"
                        },
                        "telecom systems": {
                            "energy": {},
                            "stock": "NA"
                        },
                        "other": {
                            "energy": {
                                "2018": 17,
                                "2019": 23,
                                "2020": 24,
                            },
                            "stock": "NA"
                        }
                    }
                }
            },
            "unspecified": {
                "electricity": {
                    "MELs": {
                        "water services": {
                            "energy": {
                                "2018": 10,
                                "2019": 10,
                                "2020": 10,
                            },
                            "stock": "NA"
                        },
                        "telecom systems": {
                            "energy": {
                                "2018": 10,
                                "2019": 10,
                                "2020": 10,
                            },
                            "stock": "NA"
                        }
                    },
                    "unspecified": {
                        "energy": {
                            "2018": 50,
                            "2019": 50,
                            "2020": 50,
                        },
                        "stock": "NA"
                    }
                }
            }
        }}

    # Test dict structure with correction of MELs double-counting
    mels_other_post = {
        "new england": {
            "large office": {
                "electricity": {
                    "MELs": {
                        "distribution transformers": {
                            "energy": {
                                "2018": 8,
                                "2019": 6,
                                "2020": 4,
                            },
                            "stock": "NA"
                        },
                        "televisions": {
                            "energy": {
                                "2018": 5,
                                "2019": 6,
                                "2020": 7,
                            },
                            "stock": "NA"
                        },
                        "water services": {
                            "energy": {},
                            "stock": "NA"
                        },
                        "telecom systems": {
                            "energy": {},
                            "stock": "NA"
                        },
                        "other": {
                            "energy": {
                                "2018": 4,
                                "2019": 11,
                                "2020": 13,
                            },
                            "stock": "NA"
                        }
                    }
                }
            },
            "unspecified": {
                "electricity": {
                    "MELs": {
                        "water services": {
                            "energy": {
                                "2018": 10,
                                "2019": 10,
                                "2020": 10,
                            },
                            "stock": "NA"
                        },
                        "telecom systems": {
                            "energy": {
                                "2018": 10,
                                "2019": 10,
                                "2020": 10,
                            },
                            "stock": "NA"
                        }
                    },
                    "unspecified": {
                        "energy": {
                            "2018": 50,
                            "2019": 50,
                            "2020": 50,
                        },
                        "stock": "NA"
                    }
                }
            }
        }}

    # Test dict structure matching the structure of the commercial data after processing by
    # com_mseg.py but before any corrections are applied to correct double counting
    # For testing double-counting of water systems and telecom systems in the unspecified end use
    mels_unspec_pre = {
        "new england": {
            "large office": {
                "electricity": {
                    "MELs": {
                        "distribution transformers": {
                            "energy": {
                                "2018": 8,
                                "2019": 6,
                                "2020": 4,
                            },
                            "stock": "NA"
                        },
                        "televisions": {
                            "energy": {
                                "2018": 5,
                                "2019": 6,
                                "2020": 7,
                            },
                            "stock": "NA"
                        },
                        "water services": {
                            "energy": {},
                            "stock": "NA"
                        },
                        "telecom systems": {
                            "energy": {},
                            "stock": "NA"
                        },
                        "other": {
                            "energy": {
                                "2018": 17,
                                "2019": 23,
                                "2020": 24,
                            },
                            "stock": "NA"
                        }
                    }
                }
            },
            "unspecified": {
                "electricity": {
                    "MELs": {
                        "water services": {
                            "energy": {
                                "2018": 10,
                                "2019": 10,
                                "2020": 10,
                            },
                            "stock": "NA"
                        },
                        "telecom systems": {
                            "energy": {
                                "2018": 10,
                                "2019": 10,
                                "2020": 10,
                            },
                            "stock": "NA"
                        }
                    },
                    "unspecified": {
                        "energy": {
                            "2018": 50,
                            "2019": 50,
                            "2020": 50,
                        },
                        "stock": "NA"
                    }
                }
            }
        }}

    # Test dict structure with correction of unspecified double-counting
    mels_unspec_post = {
        "new england": {
            "large office": {
                "electricity": {
                    "MELs": {
                        "distribution transformers": {
                            "energy": {
                                "2018": 8,
                                "2019": 6,
                                "2020": 4,
                            },
                            "stock": "NA"
                        },
                        "televisions": {
                            "energy": {
                                "2018": 5,
                                "2019": 6,
                                "2020": 7,
                            },
                            "stock": "NA"
                        },
                        "water services": {
                            "energy": {},
                            "stock": "NA"
                        },
                        "telecom systems": {
                            "energy": {},
                            "stock": "NA"
                        },
                        "other": {
                            "energy": {
                                "2018": 17,
                                "2019": 23,
                                "2020": 24,
                            },
                            "stock": "NA"
                        }
                    }
                }
            },
            "unspecified": {
                "electricity": {
                    "MELs": {
                        "water services": {
                            "energy": {
                                "2018": 10,
                                "2019": 10,
                                "2020": 10,
                            },
                            "stock": "NA"
                        },
                        "telecom systems": {
                            "energy": {
                                "2018": 10,
                                "2019": 10,
                                "2020": 10,
                            },
                            "stock": "NA"
                        }
                    },
                    "unspecified": {
                        "energy": {
                            "2018": 30,
                            "2019": 30,
                            "2020": 30,
                        },
                        "stock": "NA"
                    }
                }
            }
        }
    }

    def test_MELs_removed_from_MELs_other(self):
        self.assertEqual(
            cm.cleanup_calc(self.mels_other_pre, 'new england', 'large office', self.years),
            self.mels_other_post)

    def test_MELs_removed_from_unspecified(self):
        self.assertEqual(
            cm.cleanup_calc(self.mels_unspec_pre, 'new england', 'unspecified', self.years),
            self.mels_unspec_post)


# Offer external code execution (include all lines below this point in all
# test files)
def main():
    # Triggers default behavior of running all test fixtures in the file
    unittest.main()


if __name__ == '__main__':
    main()
