#!/usr/bin/env python3

""" Tests for processing microsegment data """

# Import code to be tested
from scout import mseg as rm

# Import needed packages
import unittest
import re
import numpy as np
import os
import itertools


# Skip this test if the EIA files are not expected, indicated by the
# EXPECT_EIA_FILES environment variable being set to the string 'true'
@unittest.skipUnless('EXPECT_EIA_FILES' in os.environ and
                     os.environ['EXPECT_EIA_FILES'] == 'true',
                     'EIA Data Files Not Available On This System')
class ResidentialDataIntegrityTest(unittest.TestCase):
    """ Tests the imported residential equipment energy use data from
    EIA to confirm that the data are in the expected order and that the
    consumption and equipment stock data have the required names """

    def setUp(self):
        # Open the EIA data file for use by all tests
        f = open(rm.EIAData().res_energy, 'r')

        # Read in header line
        self.header = f.readline()

        f.close()  # Close data file

    # The function that parses and assigns the data from the EIA data
    # to the JSON file expects housing stock data with specific
    # header; test for the presence of that header
    def test_for_presence_of_housing_stock_column(self):
        chk_eqstock = re.search('HOUSEHOLDS', self.header, re.IGNORECASE)
        self.assertTrue(chk_eqstock, msg='In a case-insensitive' +
                        'search, the HOUSEHOLDS column header was not' +
                        'found in the EIA data file.')

    # The function that parses and assigns the data from the EIA data
    # to the JSON file expects consumption data with specific header;
    # test for the presence of that header
    def test_for_presence_of_consumption_column(self):
        chk_consumption = re.search('CONSUMPTION', self.header, re.IGNORECASE)
        self.assertTrue(chk_consumption, msg='In a case-insensitive' +
                        'search, the CONSUMPTION column header was not' +
                        'found in the EIA data file.')

    # The function that parses and assigns the data from the EIA data
    # to the JSON file expects equipment stock data with specific
    # header; test for the presence of that header
    def test_for_presence_of_equipment_stock_column(self):
        chk_eqstock = re.search('EQSTOCK', self.header, re.IGNORECASE)
        self.assertTrue(chk_eqstock, msg='In a case-insensitive' +
                        'search, the EQSTOCK column header was not' +
                        'found in the EIA data file.')

    # The function that parses and assigns the data from the EIA data
    # to the JSON file expects bulb type data with specific
    # header; test for the presence of that header
    def test_for_presence_of_bulb_type_column(self):
        chk_eqstock = re.search('BULBTYPE', self.header, re.IGNORECASE)
        self.assertTrue(chk_eqstock, msg='In a case-insensitive' +
                        'search, the BULBTYPE column header was not' +
                        'found in the EIA data file.')

    # Test for the order of the headers in the EIA data file
    def test_order_of_columns_in_header_line(self):
        # Define a regex for the expected order of the columns of data
        # (formatting of regex takes advantage of string concatenation
        # inside parentheses)
        expectregex = (r'\w*[EU]\w*[,\s]+'
                       r'\w*[CD]\w*[,\s]+'
                       r'\w*[BG]\w*[,\s]+'
                       r'\w*[FL]\w*[,\s]+'
                       r'\w*[EQ]\w*[,\s]+'
                       r'\w*[YR]\w*[,\s]+'
                       r'\w*[ST]\w*[,\s]+'
                       r'\w*[CNS]\w*[,\s]+'
                       r'\w*[HS]\w*[,\s]+'
                       r'\w*[BL]\w*')

        # Check for a match between the defined regex and the header line
        match = re.search(expectregex, self.header, re.IGNORECASE)

        # If there is no match, print the header line
        if not match:
            print("Header Line: " + self.header)

        # Run assertTrue to check for match and complete unit test
        self.assertTrue(match, msg="Column headers in the EIA data file" +
                        "are different than expected")


class JSONTranslatorTest(unittest.TestCase):
    """ Test conversion of lists of strings from JSON file into
    restructured lists corresponding to the codes used by EIA in the
    residential microsegment text file """

    # Define example filters for each of the data cases present in
    # the JSON (and handled by the json_translator function)
    ok_filters = [['pacific', 'multi family home', 'natural gas',
                   'heating', 'demand', 'ground'],
                  ['new england', 'mobile home', 'electricity',
                   'cooling', 'demand', 'people gain'],
                  ['mid atlantic', 'single family home', 'electricity',
                   'cooling', 'supply', 'room AC'],
                  ['west south central', 'mobile home', 'electricity',
                   'TVs', 'set top box'],
                  ['east north central', 'mobile home', 'electricity',
                   'lighting', 'general service (LED)'],
                  ['west north central', 'mobile home', 'other fuel',
                   'heating', 'supply', 'resistance'],
                  ['south atlantic', 'multi family home', 'distillate',
                   'secondary heating', 'demand', 'windows solar'],
                  ['new england', 'single family home', 'other fuel',
                   'secondary heating', 'supply', 'secondary heater (coal)'],
                  ['new england', 'single family home', 'natural gas',
                   'water heating'],
                  ['new england', 'single family home',
                   'total square footage'],
                  ['new england', 'single family home', 'other fuel',
                   'secondary heating', 'secondary heater (kerosene)',
                   'demand', 'windows conduction'],
                  ['new england', 'single family home', 'new homes'],
                  ['new england', 'single family home', 'total homes'],
                  ['west south central', 'mobile home', 'electricity',
                   'TVs', 'TV']]

    # Define nonsense filter examples (combinations of building types,
    # end uses, etc. that are not possible and thus wouldn't appear in
    # the microsegments JSON)
    nonsense_filters = [['west north central', 'mobile home', 'natural gas',
                         'lighting', 'room AC'],
                        ['new england', 'single family home',
                         'electricity (on site)', 'cooling', 'supply',
                         'room AC'],
                        ['new england', 'single family home',
                         'electricity', 'refrigeration',
                         'linear fluorescent (T-8)'],
                        ['new england', 'single family home', 'natural gas',
                         'water heating', 'general service (incandescent)']
                        ]

    # Define example filters that do not have information in the
    # correct order to be prepared using json_translator and should
    # raise an error or exception
    fail_filters = [['west north central', 'cooking', 'natural gas',
                     'drying'],
                    ['pacific', 'multi family home', 'electricity',
                     'computers', 'video game consoles'],
                    ['the moon', 'mobile home', 'distillate',
                     'heating', 'supply', 'boiler (distillate)'],
                    ['mountain', 'multi family home', 'natural gas',
                     'resistance'],
                    ['mid atlantic', 'mobile home', 'distillate',
                     'TVs', 'monitors'],
                    ['mid atlantic', 'mobile home', 'electricity',
                     'TVs', 'antennas'],
                    ['west north central', 'mobile home',
                     'electricity', 'cooling', 'supply',
                     'windows solar'],
                    ['west north central', 'mobile home',
                     'heating', 'electricity', 'demand', 'room AC'],
                    ['mountain', 'mobile home', 'sq ft'],
                    ['west north central', 'mobile home',
                     'total square footage',
                     'water heating', 'room AC'],
                    ['new england', 'single family home', 'other fuel',
                     'secondary heating', 'supply',
                     'windows conduction'],
                    ['new england', 'single family home', 'other fuel',
                     'secondary heating', 'demand',
                     'secondary heater (coal)'],
                    ['west north central', 'mobile home', 'new homes',
                     'water heating', 'room AC'],
                    ['west north central', 'mobile home', 'total homes',
                     'water heating', 'room AC']
                    ]
    # Define what json_translator should produce for the given filters;
    # this part is critically important, as these tuples and/or lists
    # will be used by later functions to extract data from the imported
    # data files
    ok_out = [[['HT', 9, 2, 'GS'], 'GRND'],
              [['CL', 1, 3, 'EL'], 'PEOPLE'],
              [['CL', 2, 1, 'EL', 'ROOM_AIR'], ''],
              [['STB', 7, 3, 'EL'], ''],
              [['LT', 3, 3, 'EL', ('GSL', 'LED')], ''],
              [['HT', 4, 3, ('LG', 'KS', 'CL', 'GE', 'WD'),
                'GE2'], ''],
              [['SH', 5, 2, 'DS'], 'WIND_SOL'],
              [['SH', 1, 1, ('LG', 'KS', 'CL', 'GE', 'WD'),
                'CL'], ''],
              [['HW', 1, 1, 'GS'], ''],
              [['SQ', 1, 1], ''],
              [['SH', 1, 1,
               ('LG', 'KS', 'CL', 'GE', 'WD')], 'WIND_COND'],
              [['HS', 1, 1], ''],
              [['HT', 1, 1, 'EL', 'ELEC_RAD'], ''],
              [['TVS', 7, 3, 'EL'], '']]
    nonsense_out = [[['LT', 4, 3, 'GS', 'ROOM_AIR'], ''],
                    [['CL', 1, 1, 'SL', 'ROOM_AIR'], ''],
                    [['RF', 1, 1, 'EL', ('LFL', 'T-8')], ''],
                    [['HW', 1, 1, 'GS', ('GSL', 'Inc')], '']]

    # Test filters that have expected technology definitions and should match
    def test_ok_filters(self):
        for idx, afilter in enumerate(self.ok_filters):
            self.assertEqual(rm.json_translator(rm.res_dictlist, afilter),
                             self.ok_out[idx])

    # Test filters that have nonsensical technology definitions but
    # should nonetheless match
    def test_nonsense_filters(self):
        for idx, afilter in enumerate(self.nonsense_filters):
            self.assertEqual(rm.json_translator(rm.res_dictlist, afilter),
                             self.nonsense_out[idx])

    # Test that filters that don't conform to the structure of the
    # dicts or the expected order of data raise an error or exception
    def test_fail_filters(self):
        for afilter in self.fail_filters:
            with self.assertRaises(KeyError):
                rm.json_translator(rm.res_dictlist, afilter)


class NumpyArrayReductionTest(unittest.TestCase):
    """ Test the operation of the txt_parser function to verify row
    selection or deletion operations produce the expected output """

    # Define sample structured array with the same form as the
    # EIA data and that includes some of the rows to be removed
    EIA_nrg_stock = np.array([
        ('HT', 1, 1, 'EL', 'ELEC_RAD', 2010, 126007.0, 1452680, 3, ''),
        ('HT', 1, 1, 'EL', 'ELEC_RAD', 2011, 125784.0, 1577350, 4, ''),
        ('HT', 1, 1, 'EL', 'ELEC_RAD', 2012, 125386.0, 1324963, 5, ''),
        ('HT', 1, 1, 'EL', 'ELEC_HP', 2010, 126007.0, 1452680, -1, ''),
        ('HT', 1, 1, 'EL', 'ELEC_HP', 2011, 125784.0, 1577350, -1, ''),
        ('HT', 1, 1, 'EL', 'ELEC_HP', 2012, 125386.0, 1324963, -1, ''),
        ('HT', 1, 1, 'GS', 'NGHP', 2010, 126007.0, 1452680, 11, ''),
        ('HT', 1, 1, 'GS', 'NGHP', 2011, 125784.0, 1577350, 12, ''),
        ('HT', 1, 1, 'GS', 'NGHP', 2012, 125386.0, 1324963, 13, ''),
        ('HT', 2, 3, 'KS', 'KERO_FA', 2010, 155340.0, 5955503, -1, ''),
        ('HT', 2, 3, 'KS', 'KERO_FA', 2011, 151349.0, 5550354, -1, ''),
        ('HT', 2, 3, 'KS', 'KERO_FA', 2012, 147470.0, 4490571, -1, ''),
        ('HT', 9, 1, 'EL', 'ELEC_RAD', 2010, 126007.0, 1452680, 3, ''),
        ('HT', 9, 1, 'EL', 'ELEC_RAD', 2011, 125784.0, 1577350, 4, ''),
        ('HT', 9, 1, 'EL', 'ELEC_RAD', 2012, 125386.0, 1324963, 5, ''),
        ('HT', 9, 1, 'GS', 'NGHP', 2010, 126007.0, 1452680, 11, ''),
        ('HT', 9, 1, 'GS', 'NGHP', 2011, 125784.0, 1577350, 12, ''),
        ('HT', 9, 1, 'GS', 'NGHP', 2012, 125386.0, 1324963, 13, ''),
        ('HT', 9, 3, 'KS', 'KERO_FA', 2010, 155340.0, 5955503, -1, ''),
        ('HT', 9, 3, 'KS', 'KERO_FA', 2011, 151349.0, 5550354, -1, ''),
        ('HT', 9, 3, 'KS', 'KERO_FA', 2012, 147470.0, 4490571, -1, ''),
        ('HT', 9, 2, 'GS', 'NG_RAD', 2010, 1, 3, -1, ''),
        ('HT', 9, 2, 'GS', 'NG_RAD', 2011, 2, 2, -1, ''),
        ('HT', 9, 2, 'GS', 'NG_RAD', 2012, 3, 1, -1, ''),
        ('HT', 9, 2, 'GS', 'NG_FA', 2010, 11, 13, -1, ''),
        ('HT', 9, 2, 'GS', 'NG_FA', 2011, 12, 12, -1, ''),
        ('HT', 9, 2, 'GS', 'NG_FA', 2012, 13, 11, -1, ''),
        ('CL', 1, 1, 'EL', 'GEO_HP', 2010, 126007.0, 1452680, -1, ''),
        ('CL', 1, 1, 'EL', 'GEO_HP', 2011, 125784.0, 1577350, -1, ''),
        ('CL', 1, 1, 'EL', 'GEO_HP', 2012, 125386.0, 1324963, -1, ''),
        ('CL', 5, 3, 'EL', 'GEO_HP', 2010, 126007.0, 1452680, -1, ''),
        ('CL', 5, 3, 'EL', 'GEO_HP', 2011, 125784.0, 1577350, -1, ''),
        ('CL', 5, 3, 'EL', 'GEO_HP', 2012, 125386.0, 1324963, -1, ''),
        ('CL', 2, 1, 'EL', 'ELEC_HP', 2010, 126007.0, 1452680, -1, ''),
        ('CL', 2, 1, 'EL', 'ELEC_HP', 2011, 125784.0, 1577350, -1, ''),
        ('CL', 2, 1, 'EL', 'ELEC_HP', 2012, 125386.0, 1324963, -1, ''),
        ('DW', 2, 1, 'EL', 'DS_WASH', 2010, 6423576.0, 9417809, -1, ''),
        ('DW', 2, 1, 'EL', 'DS_WASH', 2011, 6466014.0, 9387396, -1, ''),
        ('DW', 2, 1, 'EL', 'DS_WASH', 2012, 6513706.0, 9386813, -1, ''),
        ('DW', 2, 2, 'EL', 'DS_WASH', 2010, 6423576.0, 9417809, -1, ''),
        ('DW', 2, 2, 'EL', 'DS_WASH', 2011, 6466014.0, 9387396, -1, ''),
        ('DW', 2, 2, 'EL', 'DS_WASH', 2012, 6513706.0, 9386813, -1, ''),
        ('HW', 7, 3, 'GS', 'NG_WH', 2010, 104401.0, 1897629, -1, ''),
        ('HW', 7, 3, 'GS', 'NG_WH', 2011, 101793.0, 1875027, -1, ''),
        ('HW', 7, 3, 'GS', 'NG_WH', 2012, 99374.0, 1848448, -1, ''),
        ('SF', 8, 1, 'EL', 'ELEC_RAD', 2011, 78.0, 0, -1, ''),
        ('SF', 8, 1, 'EL', 'ELEC_HP', 2011, 6.0, 0, -1, ''),
        ('SF', 8, 1, 'GS', 'NG_FA', 2011, 0.0, 0, -1, ''),
        ('SF', 9, 1, 'EL', 'ELEC_RAD', 2011, 78.0, 0, -1, ''),
        ('SF', 9, 1, 'EL', 'ELEC_HP', 2011, 6.0, 0, -1, ''),
        ('SF', 9, 1, 'GS', 'NG_FA', 2011, 0.0, 0, -1, ''),
        ('ST', 3, 1, 'EL', 'ELEC_RAD', 2011, 0.0, 0, -1, ''),
        ('ST', 3, 1, 'EL', 'ELEC_HP', 2011, 3569.0, 0, -1, ''),
        ('ST', 4, 2, 'GS', 'NG_FA', 2011, 3463.0, 0, -1, ''),
        ('ST', 4, 2, 'GS', 'NG_FA', 2012, 0.0, 0, -1, ''),
        ('ST', 4, 2, 'GS', 'NG_FA', 2013, 3569.0, 0, -1, ''),
        ('ST', 3, 2, 'GS', 'NG_FA', 2009, 3463.0, 0, -1, ''),
        ('SQ', 2, 2, 0, 0, 2010, 2262.0, 3, 8245, ''),
        ('SQ', 2, 2, 0, 0, 2011, 2262.0, 2, 8246, ''),
        ('SQ', 2, 2, 0, 0, 2012, 2262.0, 233, 8247, ''),
        ('SQ', 1, 1, 0, 0, 2025, 232.0, 332, 8245, ''),
        ('SQ', 1, 1, 0, 0, 2026, 222.0, 232, 825, ''),
        ('SQ', 1, 1, 0, 0, 2027, 62.0, 332, 845, ''),
        ('HS', 7, 3, 0, 0, 2012, 3434, 0, -1, ''),
        ('HS', 7, 3, 0, 0, 2013, 3353, 0, -1, ''),
        ('HS', 7, 3, 0, 0, 2014, 3242, 0, -1, ''),
        ('HS', 7, 3, 0, 0, 2015, 23233, 0, -1, ''),
        ('HS', 7, 3, 0, 0, 2016, 3666, 0, -1, ''),
        ('HS', 7, 3, 0, 0, 2017, 34434, 0, -1, ''),
        ('HS', 7, 3, 0, 0, 2018, 3868, 0, -1, ''),
        ('HS', 3, 1, 0, 0, 2010, 266, 0, -1, ''),
        ('HS', 3, 1, 0, 0, 2011, 665, 0, -1, ''),
        ('HS', 3, 1, 0, 0, 2012, 66, 0, -1, ''),
        ('HS', 3, 1, 0, 0, 2013, 26, 0, -1, ''),
        ('HS', 3, 1, 0, 0, 2014, 2665, 0, -1, '')],
        dtype=[('ENDUSE', '<U50'), ('CDIV', '<i4'), ('BLDG', '<i4'),
               ('FUEL', '<U50'), ('EQPCLASS', '<U50'), ('YEAR', '<i4'),
               ('EQSTOCK', '<f8'), ('CONSUMPTION', '<i4'),
               ('HOUSEHOLDS', '<i4'), ('BULB TYPE', '<U50')])

    # Define filter to select a subset of the sample EIA supply data
    EIA_nrg_stock_filter = [
      [['DW', 2, 1, 'EL', 'DS_WASH'], ''],
      [['HT', 1, 1, 'EL', 'ELEC_RAD'], ''],
      [['HT', 2, 3, 'KS', 'KERO_FA'], ''],
      [['CL', 1, 1, 'EL', 'GEO_HP'], ''],
      [['HT', 9, 2, 'GS', 'NG_RAD'], '']]

    # Set up selected data from EIA sample array as the basis for comparison
    EIA_nrg_stock_out = [
      ({"2010": 9417809, "2011": 9387396, "2012": 9386813},
       {"2010": 6423576, "2011": 6466014, "2012": 6513706}),
      ({"2010": 1452680, "2011": 1577350, "2012": 1324963},
       {"2010": 126007.0, "2011": 125784.0, "2012": 125386.0}),
      ({"2010": 5955503, "2011": 5550354, "2012": 4490571},
       {"2010": 155340.0, "2011": 151349.0, "2012": 147470.0}),
      ({"2010": 1452680, "2011": 1577350, "2012": 1324963},
       {"2010": 126007, "2011": 125784, "2012": 125386}),
      ({"2010": 3, "2011": 2, "2012": 1},
       {"2010": 1, "2011": 2, "2012": 3})]

    # Define filter to select square footage subset of sample EIA supply data
    EIA_sqft_homes_filter = [[['SQ', 2, 2], ''],
                             [['HT', 1, 1, 'EL', 'ELEC_RAD'], ''],
                             [['HS', 3, 1], ''],
                             ]

    # Set up selected data from EIA sample array as the basis for comparison
    EIA_sqft_homes_out = [
      {"2010": 8245, "2011": 8246, "2012": 8247},
      {"2010": 3, "2011": 4, "2012": 5},
      {"2010": 266, "2011": 665, "2012": 66, "2013": 26, "2014": 2665}]

    # Define sample structured array comparable in form to the thermal
    # loads data (note that the numeric data here do not represent
    # realistic values for these data)
    tloads_example = np.array([
        ('HT', 1, 1, 394.8, 0.28, 0.08, 0.08, 0.25, 0.38, -0.02, 0.22, -0.12),
        ('CL', 1, 1, 394.8, -0.01, 0.51, 0.10, 0.15, 0.14, 0.03, -0.12, 0.19),
        ('HT', 2, 1, 813.3, 0.29, -0.07, 0.10, 0.24, 0.38, 0.01, 0.20, -0.13),
        ('CL', 2, 1, 813.3, -0.01, 0.44, 0.12, 0.14, 0.14, 0.03, -0.09, 0.19),
        ('HT', 3, 2, 409.5, 0.27, -0.06, 0.23, 0.21, 0.48, 0.05, 0.13, -0.23),
        ('CL', 3, 2, 409.5, -0.02, 0.34, 0.13, 0.06, 0.09, 0.13, -0.16, 0.41),
        ('HT', 4, 2, 104.8, 0.29, 0.07, 0.23, 0.23, 0.44, -0.05, 0.17, -0.25),
        ('CL', 4, 2, 104.8, 0.00, 0.31, 0.09, 0.09, 0.13, 0.11, -0.11, 0.37),
        ('HT', 5, 3, 140.9, 0.44, -0.13, 0.11, 0.25, 0.33, -0.02, 0.16, 0.16),
        ('CL', 5, 3, 140.9, 0.00, 0.40, 0.12, 0.11, 0.14, 0.04, -0.03, 0.20),
        ('HT', 6, 3, 684.1, 0.47, 0.14, 0.18, 0.26, 0.39, -0.03, 0.07, -0.21),
        ('CL', 6, 3, 684.1, -0.01, 0.37, 0.14, 0.09, 0.14, 0.04, 0.02, 0.23)],
        dtype=[('ENDUSE', '<U50'), ('CDIV', '<i4'), ('BLDG', '<i4'),
               ('NBLDGS', '<f8'), ('WIND_COND', '<f8'), ('WIND_SOL', '<f8'),
               ('ROOF', '<f8'), ('WALL', '<f8'), ('INFIL', '<f8'),
               ('PEOPLE', '<f8'), ('GRND', '<f8'), ('EQUIP', '<f8')])

    # Specify filter to select thermal load data
    tl_flt = [['HT', 3, 2, 'GS'], 'GRND']

    # Set up selected data from thermal loads sample array
    tloads_sample = 0.13

    # Test restructuring of EIA data into stock and consumption lists
    # using the EIA_Supply option to confirm that both the reported
    # data and the reduced array with the remaining data are correct
    def test_recording_of_EIA_data_tech(self):
        for n in range(0, len(self.EIA_nrg_stock_filter)):
            (a, b) = rm.nrg_stock_select(self.EIA_nrg_stock,
                                         self.EIA_nrg_stock_filter[n])
            # Compare equipment stock
            self.assertEqual(a, self.EIA_nrg_stock_out[n][0])
            # Compare consumption
            self.assertEqual(b, self.EIA_nrg_stock_out[n][1])

    # Test restructuring of EIA data into a square footage list, confirming
    # that both the reported data and the reduced array with the remaining
    # data are correct
    # TEMP - this should also test home count numbers (and comments
    # and variables names should reflect that)
    def test_recording_of_EIA_data_sqft_homes(self):
        for n in range(0, len(self.EIA_sqft_homes_filter)):
            a = rm.sqft_homes_select(self.EIA_nrg_stock,
                                     self.EIA_sqft_homes_filter[n])
            # Compare square footage
            self.assertEqual(a, self.EIA_sqft_homes_out[n])

    # Test extraction of the correct value from the thermal load
    # components data
    def test_recording_of_thermal_loads_data(self):
        self.assertEqual(rm.thermal_load_select(self.tloads_example,
                         self.tl_flt),
                         self.tloads_sample)


class DataToListFormatTest(unittest.TestCase):
    """ Test operation of list_generator function (create dummy inputs
    and test against established outputs) """

    # Define sample AEO time horizon for this test
    aeo_years = 2

    # Define a sample set of stock/energy data
    nrg_stock = [('HT', 1, 1, 'EL', 'ELEC_RAD', 2010, 0, 1, 3, ''),
                 ('HT', 1, 1, 'EL', 'ELEC_RAD', 2011, 0, 1, 4, ''),
                 ('HT', 2, 1, 'GS', 'NG_FA', 2010, 2, 3, -1, ''),
                 ('HT', 2, 1, 'GS', 'NG_FA', 2011, 2, 3, -1, ''),
                 ('HT', 2, 1, 'GS', 'NG_RAD', 2010, 4, 5, -1, ''),
                 ('HT', 2, 1, 'GS', 'NG_RAD', 2011, 4, 5, -1, ''),
                 ('CL', 2, 3, 'GS', 'NG_HP', 2010, 6, 7, -1, ''),
                 ('CL', 2, 3, 'GS', 'NG_HP', 2011, 6, 7, -1, ''),
                 ('CL', 1, 3, 'GS', 'NG_HP', 2010, 8, 9, -1, ''),
                 ('CL', 1, 3, 'GS', 'NG_HP', 2011, 8, 9, -1, ''),
                 ('SH', 1, 1, 'EL', 'EL', 2010, 10, 11, -1, ''),
                 ('SH', 1, 1, 'EL', 'EL', 2011, 10, 11, -1, ''),
                 ('SH', 1, 1, 'GS', 'GS', 2010, 12, 13, -1, ''),
                 ('SH', 1, 1, 'GS', 'GS', 2011, 12, 13, -1, ''),
                 # ('OA ', 1, 1, 'EL', 'EL', 2010, 14, 15, -1),
                 # ('OA ', 1, 1, 'EL', 'EL', 2011, 14, 15, -1),
                 ('SH', 2, 1, 'GS', 'GS', 2010, 16, 17, -1, ''),
                 ('SH', 2, 1, 'GS', 'GS', 2011, 16, 17, -1, ''),
                 ('SH', 3, 1, 'EL', 'EL', 2010, 18, 19, -1, ''),
                 ('SH', 3, 1, 'EL', 'EL', 2011, 18, 19, -1, ''),
                 ('SH', 3, 1, 'WD', 'WD', 2010, 20, 21, -1, ''),
                 ('SH', 3, 1, 'WD', 'WD', 2011, 20, 21, -1, ''),
                 ('STB', 1, 1, 'EL', 'TV&R', 2010, 22, 23, -1, ''),
                 ('STB', 1, 1, 'EL', 'TV&R', 2011, 22, 23, -1, ''),
                 ('STB', 1, 2, 'EL', 'TV&R', 2010, 24, 25, -1, ''),
                 ('STB', 1, 2, 'EL', 'TV&R', 2011, 24, 25, -1, ''),
                 ('EO', 2, 2, 'EL', 'MEL', 2010, 36, 37, -1, ''),
                 ('EO', 2, 2, 'EL', 'MEL', 2011, 36, 37, -1, ''),
                 ('SQ', 1, 1, 0, 0, 2010, 99, 100, 101, ''),
                 ('SQ', 1, 1, 0, 0, 2011, 99, 100, 101, ''),
                 ('LT', 1, 1, 'EL', 'GSL', 2010, 102, 0, -1, 'LED'),
                 ('LT', 1, 1, 'EL', 'GSL', 2011, 103, 0, -1, 'LED'),
                 ('LT', 1, 2, 'EL', 'GSL', 2010, 103, 0, -1, 'LED'),
                 ('LT', 1, 1, 'EL', 'GSL', 2010, 179, 104, -1, 'Inc'),
                 ('LT', 1, 1, 'EL', 'GSL', 2011, 176, 104, -1, 'Inc'),
                 ('LT', 1, 1, 'EL', 'EXT', 2010, 103, 104, -1, 'LED'),
                 ('HS', 1, 1, 0, 0, 2010, 299, 0, 0, ''),
                 ('HS', 1, 1, 0, 0, 2011, 299, 0, 0, ''),
                 ('TVS', 1, 1, 'EL', 'TV&R', 2010, 35, 757, -1, ''),
                 ('TVS', 1, 1, 'EL', 'TV&R', 2011, 355., 787, -1, '')]

    # Convert stock/energy data into numpy array with column names
    nrg_stock_array = np.array(nrg_stock, dtype=[
      ('ENDUSE', '<U50'), ('CDIV', 'i4'), ('BLDG', 'i4'),
      ('FUEL', '<U50'), ('EQPCLASS', '<U50'), ('YEAR', 'i4'),
      ('EQSTOCK', 'i4'), ('CONSUMPTION', 'i4'), ('HOUSEHOLDS', 'i4'),
      ('BULBTYPE', '<U50')])

    # Define a sample set of thermal load components data
    loads_data = [('CL', 2, 3, 100, -0.25, 0.25, 0, 0, 0.25, 0, 0.5, 0),
                  ('CL', 1, 2, 200, -0.1, 0.1, 0, 0, 0.4, 0, 0.6, 0),
                  ('HT', 2, 3, 300, -0.5, 0.5, 0, 0, 0.5, 0, 0.5, 0),
                  ('HT', 2, 1, 400, -0.75, 0.5, 0, 0, 0.25, 0, 1, 0),
                  ('HT', 1, 1, 300, -0.2, 0.1, 0, 0.4, 0.1, 0.3, 0.3, 0),
                  ('CL', 1, 1, 400, -0.3, 0.5, 0.1, 0.1, 0.2, 0, 0.4, 0)]

    # Convert thermal loads data into numpy array with column names
    loads_array = np.array(loads_data, dtype=[('ENDUSE', '<U50'),
                                              ('CDIV', 'i4'),
                                              ('BLDG', 'i4'),
                                              ('NBLDGS', 'f8'),
                                              ('WIND_COND', 'f8'),
                                              ('WIND_SOL', 'f8'),
                                              ('ROOF', 'f8'),
                                              ('WALL', 'f8'),
                                              ('INFIL', 'f8'),
                                              ('PEOPLE', 'f8'),
                                              ('GRND', 'f8'),
                                              ('EQUIP', 'f8')])

    # Define a set of filters that should yield matched microsegment
    # stock/energy data
    ok_filters = [['new england', 'single family home',
                   'electricity', 'heating', 'supply',
                   'resistance heat'],
                  ['new england', 'single family home',
                   'electricity', 'secondary heating',
                   'supply', 'secondary heater'],
                  ['new england', 'single family home',
                   'natural gas', 'secondary heating', 'supply',
                   'secondary heater'],
                  ['east north central', 'single family home',
                   'electricity', 'secondary heating', 'supply',
                   'secondary heater'],
                  ['new england', 'single family home',
                   'electricity', 'TVs', 'set top box'],
                  ['new england', 'multi family home',
                   'electricity', 'TVs', 'set top box'],
                  ['mid atlantic', 'multi family home',
                   'electricity', 'other', 'electric other'],
                  ['new england', 'single family home',
                   'electricity', 'heating',
                   'demand', 'ground'],
                  ['mid atlantic', 'single family home',
                   'natural gas', 'heating', 'demand',
                   'windows conduction'],
                  ['mid atlantic', 'mobile home',
                   'natural gas', 'cooling', 'demand',
                   'windows solar'],
                  ['new england', 'single family home',
                   'total square footage'],
                  ['east north central', 'single family home',
                   'other fuel', 'secondary heating', 'supply',
                   'secondary heater (wood)'],
                  ['new england', 'single family home',
                   'electricity', 'lighting',
                   'general service (LED)'],
                  ['new england', 'single family home', 'new homes'],
                  ['new england', 'single family home', 'total homes'],
                  ['new england', 'single family home',
                   'electricity', 'TVs', 'TV'],
                  ['new england', 'single family home',
                   'electricity', 'lighting',
                   'general service (incandescent)']]

    # Define a set of filters that should yield zeros for stock/energy
    # data because they do not make sense
    nonsense_filters = [['mid atlantic', 'mobile home', 'natural gas',
                         'heating', 'room AC'],
                        ['pacific', 'single family home',
                         'electricity (on site)', 'water heating', 'solar WH'],
                        ['new england', 'single family home',
                         'distillate', 'TVs',
                         'set top box']]

    # Define a set of filters that should raise an error because certain
    # filter elements do not have any match in the microsegment dict keys
    fail_filters = [['the moon', 'single family home',
                     'electricity', 'heating', 'supply',
                     'resistance heat'],
                    ['new england', 'single family cave',
                     'natural gas', 'secondary heating'],
                    ['new england', 'mobile home',
                     'human locomotion', 'lighting', 'reflector'],
                    ['south atlantic', 'single family home',
                     'distillate', 'secondary heating', 'supply',
                     'portable heater'],
                    ['mid atlantic', 'mobile home',
                     'electricity', 'heating',
                     'supply', 'boiler (wood fired)'],
                    ['east north central', 'multi family home',
                     'natural gas', 'cooling', 'demand', 'windows frames'],
                    ['pacific', 'multi family home', 'electricity',
                     'other', 'beer cooler'],
                    ['pacific', 'multi home', 'total square footage'],
                    ['pacific', 'multi family home', 'square foot'],
                    ['mid atlantic', 'mobile home', 'renewables',
                     'water heating', 'solar WH'],
                    ['east north central', 'single family home',
                     'other fuel', 'secondary heating', 'demand',
                     'secondary heater (wood)'],
                    ['pacific', 'multi family home', 'total square footage',
                     'natural gas', 'water heating'],
                    ['pacific', 'multi family home', 'new homes',
                     'natural gas', 'water heating'],
                    ['pacific', 'multi family home', 'total homes',
                     'natural gas', 'water heating']]

    # Define array of lighting weighting factors expected to be output
    # by the function under test
    lt_factor_expected = np.array([
        (1, 1, 'GSL', 'Inc', '2010', 0.91477392),
        (1, 1, 'GSL', 'Inc', '2011', 0.90574519),
        (1, 2, 'GSL', 'Inc', '2010', 0.82494111),
        (1, 2, 'GSL', 'Inc', '2011', 0.81193743),
        (3, 1, 'GSL', 'Inc', '2010', 0.87472457),
        (3, 1, 'GSL', 'Inc', '2011', 0.86130072),
        (3, 2, 'GSL', 'Inc', '2010', 0.87774796),
        (3, 2, 'GSL', 'Inc', '2011', 0.87285453),
        (1, 1, 'GSL', 'LED', '2010', 0.08522608),
        (1, 1, 'GSL', 'LED', '2011', 0.09425481),
        (1, 2, 'GSL', 'LED', '2010', 0.17505889),
        (1, 2, 'GSL', 'LED', '2011', 0.18806257),
        (3, 1, 'GSL', 'LED', '2010', 0.12527543),
        (3, 1, 'GSL', 'LED', '2011', 0.13869928),
        (3, 2, 'GSL', 'LED', '2010', 0.12225204),
        (3, 2, 'GSL', 'LED', '2011', 0.12714547),
        (1, 1, 'LFL', 'T12', '2010', 0.41604117),
        (1, 1, 'LFL', 'T12', '2011', 0.41195155),
        (1, 2, 'LFL', 'T12', '2010', 0.29310758),
        (1, 2, 'LFL', 'T12', '2011', 0.28591929),
        (3, 1, 'LFL', 'T12', '2010', 0.43981098),
        (3, 1, 'LFL', 'T12', '2011', 0.43168629),
        (3, 2, 'LFL', 'T12', '2010', 0.30942591),
        (3, 2, 'LFL', 'T12', '2011', 0.30073385),
        (1, 1, 'LFL', 'T-8', '2010', 0.33771134),
        (1, 1, 'LFL', 'T-8', '2011', 0.33900962),
        (1, 2, 'LFL', 'T-8', '2010', 0.40173711),
        (1, 2, 'LFL', 'T-8', '2011', 0.40616518),
        (3, 1, 'LFL', 'T-8', '2010', 0.30517175),
        (3, 1, 'LFL', 'T-8', '2011', 0.30744705),
        (3, 2, 'LFL', 'T-8', '2010', 0.26764825),
        (3, 2, 'LFL', 'T-8', '2011', 0.276772),
        (1, 1, 'LFL', 'T-5', '2010', 0.24624749),
        (1, 1, 'LFL', 'T-5', '2011', 0.24903882),
        (1, 2, 'LFL', 'T-5', '2010', 0.30515531),
        (1, 2, 'LFL', 'T-5', '2011', 0.30791553),
        (3, 1, 'LFL', 'T-5', '2010', 0.25501727),
        (3, 1, 'LFL', 'T-5', '2011', 0.26086665),
        (3, 2, 'LFL', 'T-5', '2010', 0.42292584),
        (3, 2, 'LFL', 'T-5', '2011', 0.42249415)],
        dtype=[('CDIV', 'i4'), ('BLDG', 'i4'), ('EQPCLASS', 'U4'),
               ('BULBTYPE', 'U4'), ('YEAR', 'i4'), ('FACTOR', 'f8')])

    # Define the set of outputs that should be yielded by the "ok_filters"
    # information above
    ok_out = [[{'stock': {"2010": 0, "2011": 0},
                'energy': {"2010": 1, "2011": 1}},
               nrg_stock_array],
              [{'stock': {"2010": 10, "2011": 10},
                'energy': {"2010": 11, "2011": 11}},
               np.hstack([nrg_stock_array[:10], nrg_stock_array[12:]])],
              [{'stock': {"2010": 12, "2011": 12},
                'energy': {"2010": 13, "2011": 13}},
               np.hstack([nrg_stock_array[:12], nrg_stock_array[14:]])],
              [{'stock': {"2010": 18, "2011": 18},
                'energy': {"2010": 19, "2011": 19}},
               np.hstack([nrg_stock_array[:16], nrg_stock_array[18:]])],
              [{'stock': {"2010": 22, "2011": 22},
                'energy': {"2010": 23, "2011": 23}},
               np.hstack([nrg_stock_array[:20], nrg_stock_array[22:]])],
              [{'stock': {"2010": 24, "2011": 24},
                'energy': {"2010": 25, "2011": 25}},
               np.hstack([nrg_stock_array[:22], nrg_stock_array[24:]])],
              [{'stock': {"2010": 36, "2011": 36},
                'energy': {"2010": 37, "2011": 37}},
               np.hstack([nrg_stock_array[:24], nrg_stock_array[26:]])],
              [{'stock': 'NA',
                'energy': {"2010": 0.3, "2011": 0.3}},
               nrg_stock_array],
              [{'stock': 'NA',
                'energy': {"2010": -6.0, "2011": -6.0}},
               nrg_stock_array],
              [{'stock': 'NA',
                'energy': {"2010": 1.75, "2011": 1.75}},
               nrg_stock_array],
              [{"2010": 101, "2011": 101},
               np.hstack([nrg_stock_array[0:26], nrg_stock_array[28:]])],
              [{'stock': {"2010": 20, "2011": 20},
                'energy': {"2010": 21, "2011": 21}},
               np.hstack([nrg_stock_array[0:18], nrg_stock_array[20:]])],
              [{'stock': {"2010": 102, "2011": 103},
                'energy': {"2010": 8.86351232, "2011": 9.8025002399}},
               nrg_stock_array],
              [{"2010": 299, "2011": 299},
               np.hstack([nrg_stock_array[0:-4], nrg_stock_array[-2:]])],
              [{"2010": 3, "2011": 4}, nrg_stock_array],
              [{'stock': {"2010": 35, "2011": 355},
                'energy': {"2010": 757, "2011": 787}}, nrg_stock_array[:-2]],
              [{'stock': {'2010': 179, '2011': 176},
                'energy': {'2010': 95.13648768, '2011': 94.19749976}},
               nrg_stock_array]]

    # Define the set of outputs (empty dicts) that should be yielded
    # by the "nonsense_filters" given above
    nonsense_out = [{'stock': {}, 'energy': {}},
                    {'stock': {}, 'energy': {}},
                    {'stock': {}, 'energy': {}}]

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

    # Test filter that should match and generate stock/energy data
    def test_ok_filters(self):
        for idx, afilter in enumerate(self.ok_filters):
            # Call the function under test and capture its outputs
            a = rm.list_generator(self.nrg_stock_array,
                                  self.loads_array,
                                  afilter,
                                  self.aeo_years,
                                  self.lt_factor_expected)

            # Check the contents of the output dict
            self.dict_check(a, self.ok_out[idx][0])

    # Test filters that should match but ultimately do not make sense
    def test_nonsense_filters(self):
        for idx, afilter in enumerate(self.nonsense_filters):
            # Call the function under test and capture its outputs
            a = rm.list_generator(self.nrg_stock_array,
                                  self.loads_array,
                                  afilter,
                                  self.aeo_years,
                                  self.lt_factor_expected)

            # Check the contents of the output dict
            self.assertEqual(a, self.nonsense_out[idx])

    # Test filters that should raise an error
    def test_fail_filters(self):
        for idx, afilter in enumerate(self.fail_filters):
            with self.assertRaises(KeyError):
                # Expect the function to raise an error with each call
                # using the filters supplied from fail_filters
                rm.list_generator(self.nrg_stock_array,
                                  self.loads_array,
                                  afilter,
                                  self.aeo_years,
                                  self.lt_factor_expected)


class LightingEfficiencyTablePrepTest(unittest.TestCase):
    """ Test the function that restructures the lighting performance
    data drawn from the AEO cost, performance, and lifetime file for
    residential lighting into a lighting efficiency (inverse of
    lighting performance, units of W/lm instead of lm/W) lookup
    table for each year and each combination of fixture and bulb type. """

    # Array of lighting CPL data with a similar structure to the
    # data obtained from the AEO but with fewer years, fewer
    # lighting types, and excluding columns that are not used
    # by this function (the indicated values are not representative
    # of the performance or anticipated performance improvements
    # in actual lighting technologies)
    lighting_cpl_data = np.array(
        [(2011, 2012, 12, 45, 'GSL', 'INC'),
         (2013, 2020, 22, 24, 'GSL', 'INC'),
         (2011, 2015, 60, 75, 'GSL', 'LED'),
         (2016, 2017, 78, 89, 'GSL', 'LED'),
         (2018, 2020, 105, 200, 'GSL', 'LED'),
         (2011, 2012, 12, 100, 'REF', 'INC'),
         (2013, 2020, 99, 99, 'REF', 'INC'),
         (2011, 2012, 78, 100, 'REF', 'LED'),
         (2013, 2020, 99, 200, 'REF', 'LED'),
         (2011, 2014, 30, 60, 'LFL', 'T12'),
         (2015, 2017, 44, 75, 'LFL', 'T12'),
         (2018, 2020, 56, 100, 'LFL', 'T12'),
         (2011, 2016, 41, 35, 'LFL', 'T-8'),
         (2017, 2020, 49, 77, 'LFL', 'T-8'),
         (2011, 2012, 39, 89, 'LFL', 'T-5'),
         (2013, 2013, 57, 91, 'LFL', 'T-5'),
         (2014, 2016, 62, 99, 'LFL', 'T-5'),
         (2017, 2020, 66, 101, 'LFL', 'T-5')],
        dtype=[('FirstYear', 'i4'), ('LastYear', 'i4'), ('lm_per_W', 'i4'),
               ('Watts', 'i4'), ('Application', 'U8'), ('BulbType', 'U8')])

    # Number of years represented in the synthetic CPL data
    total_n_years = 10

    # Number of lighting types (combinations of fixture and bulb types)
    # in the synthetic CPL data
    n_lighting_types = 7

    # Array of lighting data restructured into a numpy structured
    # array for each fixture type and bulb type
    lighting_eff_result = np.array(
        [('GSL', 'INC', 0.833333333, 0.833333333, 0.731707317, 0.731707317,
          0.731707317, 0.78, 0.78, 0.826771654, 0.826771654, 0.826771654),
         ('GSL', 'LED', 0.166666667, 0.166666667, 0.268292683, 0.268292683,
          0.268292683, 0.22, 0.22, 0.173228346, 0.173228346, 0.173228346),
         ('LFL', 'T12', 0.399849962, 0.399849962, 0.442865264,
          0.451349432, 0.359344077, 0.359344077, 0.389920424,
          0.334298119, 0.334298119, 0.334298119),
         ('LFL', 'T-8', 0.292573143, 0.292573143, 0.324047754,
          0.330255682, 0.385637546, 0.385637546, 0.350132626,
          0.382054993, 0.382054993, 0.382054993),
         ('LFL', 'T-5', 0.307576894, 0.307576894, 0.233086981,
          0.218394886, 0.255018377, 0.255018377, 0.25994695,
          0.283646889, 0.283646889, 0.283646889),
         ('REF', 'INC', 0.8666667, 0.8666667, 0.8918919, 0.8918919, 0.8918919,
          0.8918919, 0.8918919, 0.8918919, 0.8918919, 0.8918919),
         ('REF', 'LED', 0.1333333, 0.1333333, 0.1081081, 0.1081081, 0.1081081,
          0.1081081, 0.1081081, 0.1081081, 0.1081081, 0.1081081)],
        dtype=[('Application', 'U4'), ('BulbType', 'U4'), ('2011', 'f8'),
               ('2012', 'f8'), ('2013', 'f8'), ('2014', 'f8'),
               ('2015', 'f8'), ('2016', 'f8'), ('2017', 'f8'),
               ('2018', 'f8'), ('2019', 'f8'), ('2020', 'f8')])

    # Test that the lighting performance data is correctly restructured
    # into lighting efficiency data for each bulb and fixture type
    def test_lighting_efficiency_table_prep(self):
        result = rm.lighting_eff_prep(self.lighting_cpl_data,
                                      self.total_n_years,
                                      self.n_lighting_types)

        # Extract the numeric entries for matching lighting and bulb
        # types from the reference array and test array and compare
        # the year values
        for row in self.lighting_eff_result:
            # Grab the matching row from the function result array
            fn_result_row = result[np.all([
                result['Application'] == row['Application'],
                result['BulbType'] == row['BulbType']], axis=0)]

            # Compare the numeric values for each year reported in the
            # rows with the matching fixture and bulb types
            self.assertTrue(all(
                [np.allclose(fn_result_row[name], row[name])
                 for name in row.dtype.names
                 if name not in ('Application', 'BulbType')]))


class LightingStockWeightedFactorsTest(unittest.TestCase):
    """ Test the function that takes the normalized bulb efficiency
    weighting factors and the stock data for each fixture and bulb
    type combination and combines them to generate efficiency and
    stock weighted multipliers that can be used to split up the
    energy use data reported in RESDBOUT only for one bulb type
    for each fixture type. """

    # Sample input lighting efficiency factor array
    lighting_eff_result = np.array(
        [('GSL', 'INC', 0.833333333, 0.833333333, 0.731707317),
         ('GSL', 'LED', 0.166666667, 0.166666667, 0.268292683),
         ('LFL', 'T12', 0.399849962, 0.399849962, 0.442865264),
         ('LFL', 'T-8', 0.292573143, 0.292573143, 0.324047754),
         ('LFL', 'T-5', 0.307576894, 0.307576894, 0.233086981)],
        dtype=[('Application', 'U4'), ('BulbType', 'U4'),
               ('2011', 'f8'), ('2012', 'f8'), ('2013', 'f8')])

    # Number of lighting types (combinations of fixture and bulb types)
    # in the synthetic CPL data (equal to the number of rows in the
    # lighting_eff_result test array)
    n_lighting_types = 5

    # Number of years represented in the synthetic CPL data and the
    # synthetic stock and energy data
    total_n_years = 3

    # Sample energy and stock data array
    nrg_stock_array = np.array([
        ('LT', 1, 1, 'EL', 'GSL',
         2011, 164420.0, 1452680, 0, 'INC'),
        ('LT', 1, 1, 'EL', 'GSL',
         2012, 159428.0, 1577350, 0, 'INC'),
        ('LT', 1, 1, 'EL', 'GSL',
         2013, 153895.0, 1324963, 0, 'INC'),
        ('LT', 1, 2, 'EL', 'GSL',
         2011, 92810.0, 1452680, 0, 'INC'),
        ('LT', 1, 2, 'EL', 'GSL',
         2012, 87534.0, 1577350, 0, 'INC'),
        ('LT', 1, 2, 'EL', 'GSL',
         2013, 83958.0, 1324963, 0, 'INC'),
        ('LT', 3, 1, 'EL', 'GSL',
         2011, 103295.0, 1452680, 0, 'INC'),
        ('LT', 3, 1, 'EL', 'GSL',
         2012, 95567.0, 1577350, 0, 'INC'),
        ('LT', 3, 1, 'EL', 'GSL',
         2013, 89356.0, 1324963, 0, 'INC'),
        ('LT', 3, 2, 'EL', 'GSL',
         2011, 177692.0, 1452680, 0, 'INC'),
        ('LT', 3, 2, 'EL', 'GSL',
         2012, 175438.0, 1577350, 0, 'INC'),
        ('LT', 3, 2, 'EL', 'GSL',
         2013, 172984.0, 1324963, 0, 'INC'),
        ('LT', 1, 1, 'EL', 'GSL',
         2011, 76592.0, 1452680, 0, 'LED'),
        ('LT', 1, 1, 'EL', 'GSL',
         2012, 82953.0, 1577350, 0, 'LED'),
        ('LT', 1, 1, 'EL', 'GSL',
         2013, 90485.0, 1324963, 0, 'LED'),
        ('LT', 1, 2, 'EL', 'GSL',
         2011, 98475.0, 1452680, 0, 'LED'),
        ('LT', 1, 2, 'EL', 'GSL',
         2012, 101374.0, 1577350, 0, 'LED'),
        ('LT', 1, 2, 'EL', 'GSL',
         2013, 104884.0, 1324963, 0, 'LED'),
        ('LT', 3, 1, 'EL', 'GSL',
         2011, 73968.0, 1452680, 0, 'LED'),
        ('LT', 3, 1, 'EL', 'GSL',
         2012, 76948.0, 1577350, 0, 'LED'),
        ('LT', 3, 1, 'EL', 'GSL',
         2013, 81524.0, 1324963, 0, 'LED'),
        ('LT', 3, 2, 'EL', 'GSL',
         2011, 123744.0, 1452680, 0, 'LED'),
        ('LT', 3, 2, 'EL', 'GSL',
         2012, 127777.0, 1577350, 0, 'LED'),
        ('LT', 3, 2, 'EL', 'GSL',
         2013, 134395.0, 1324963, 0, 'LED'),
        ('LT', 1, 1, 'EL', 'LFL',
         2011, 172698.0, 1452680, 0, 'T12'),
        ('LT', 1, 1, 'EL', 'LFL',
         2012, 171593.0, 1577350, 0, 'T12'),
        ('LT', 1, 1, 'EL', 'LFL',
         2013, 169985.0, 1324963, 0, 'T12'),
        ('LT', 1, 2, 'EL', 'LFL',
         2011, 92416.0, 1452680, 0, 'T12'),
        ('LT', 1, 2, 'EL', 'LFL',
         2012, 90115.0, 1577350, 0, 'T12'),
        ('LT', 1, 2, 'EL', 'LFL',
         2013, 87888.0, 1324963, 0, 'T12'),
        ('LT', 3, 1, 'EL', 'LFL',
         2011, 185455.0, 1452680, 0, 'T12'),
        ('LT', 3, 1, 'EL', 'LFL',
         2012, 181322.0, 1577350, 0, 'T12'),
        ('LT', 3, 1, 'EL', 'LFL',
         2013, 176931.0, 1324963, 0, 'T12'),
        ('LT', 3, 2, 'EL', 'LFL',
         2011, 76209.0, 1452680, 0, 'T12'),
        ('LT', 3, 2, 'EL', 'LFL',
         2012, 75481.0, 1577350, 0, 'T12'),
        ('LT', 3, 2, 'EL', 'LFL',
         2013, 73852.0, 1324963, 0, 'T12'),
        ('LT', 1, 1, 'EL', 'LFL',
         2011, 191584.0, 1452680, 0, 'T-8'),
        ('LT', 1, 1, 'EL', 'LFL',
         2012, 192987.0, 1577350, 0, 'T-8'),
        ('LT', 1, 1, 'EL', 'LFL',
         2013, 194125.0, 1324963, 0, 'T-8'),
        ('LT', 1, 2, 'EL', 'LFL',
         2011, 173111.0, 1452680, 0, 'T-8'),
        ('LT', 1, 2, 'EL', 'LFL',
         2012, 174952.0, 1577350, 0, 'T-8'),
        ('LT', 1, 2, 'EL', 'LFL',
         2013, 176339.0, 1324963, 0, 'T-8'),
        ('LT', 3, 1, 'EL', 'LFL',
         2011, 175865.0, 1452680, 0, 'T-8'),
        ('LT', 3, 1, 'EL', 'LFL',
         2012, 176488.0, 1577350, 0, 'T-8'),
        ('LT', 3, 1, 'EL', 'LFL',
         2013, 177539.0, 1324963, 0, 'T-8'),
        ('LT', 3, 2, 'EL', 'LFL',
         2011, 90090.0, 1452680, 0, 'T-8'),
        ('LT', 3, 2, 'EL', 'LFL',
         2012, 94938.0, 1577350, 0, 'T-8'),
        ('LT', 3, 2, 'EL', 'LFL',
         2013, 100068.0, 1324963, 0, 'T-8'),
        ('LT', 1, 1, 'EL', 'LFL',
         2011, 132882.0, 1452680, 0, 'T-5'),
        ('LT', 1, 1, 'EL', 'LFL',
         2012, 134854.0, 1577350, 0, 'T-5'),
        ('LT', 1, 1, 'EL', 'LFL',
         2013, 135321.0, 1324963, 0, 'T-5'),
        ('LT', 1, 2, 'EL', 'LFL',
         2011, 125079.0, 1452680, 0, 'T-5'),
        ('LT', 1, 2, 'EL', 'LFL',
         2012, 126162.0, 1577350, 0, 'T-5'),
        ('LT', 1, 2, 'EL', 'LFL',
         2013, 127754.0, 1324963, 0, 'T-5'),
        ('LT', 3, 1, 'EL', 'LFL',
         2011, 139793.0, 1452680, 0, 'T-5'),
        ('LT', 3, 1, 'EL', 'LFL',
         2012, 142444.0, 1577350, 0, 'T-5'),
        ('LT', 3, 1, 'EL', 'LFL',
         2013, 144879.0, 1324963, 0, 'T-5'),
        ('LT', 3, 2, 'EL', 'LFL',
         2011, 135412.0, 1452680, 0, 'T-5'),
        ('LT', 3, 2, 'EL', 'LFL',
         2012, 137854.0, 1577350, 0, 'T-5'),
        ('LT', 3, 2, 'EL', 'LFL',
         2013, 140276.0, 1324963, 0, 'T-5'),
        ('SQ', 2, 2, 0, 0, 2011, 2262.0, 2332, 8245, ''),
        ('SQ', 2, 2, 0, 0, 2012, 2262.0, 2332, 8246, ''),
        ('SQ', 2, 2, 0, 0, 2013, 2262.0, 2332, 8247, ''),
        ('HS', 7, 3, 0, 0, 2012, 3434, 0, -1, ''),
        ('HS', 3, 1, 0, 0, 2012, 3434, 0, -1, '')],
        dtype=[('ENDUSE', '<U50'), ('CDIV', 'i4'),
               ('BLDG', 'i4'), ('FUEL', '<U50'),
               ('EQPCLASS', '<U50'), ('YEAR', 'i4'),
               ('EQSTOCK', 'i4'), ('CONSUMPTION', 'i4'),
               ('HOUSEHOLDS', 'i4'), ('BULBTYPE', '<U50')])

    # Define array of lighting weighting factors expected to be output
    # by the function under test
    lt_factor_expected = np.array([
        (1, 1, 'GSL', 'INC', '2011', 0.91477392),
        (1, 1, 'GSL', 'INC', '2012', 0.90574519),
        (1, 1, 'GSL', 'INC', '2013', 0.82264751),
        (1, 2, 'GSL', 'INC', '2011', 0.82494111),
        (1, 2, 'GSL', 'INC', '2012', 0.81193743),
        (1, 2, 'GSL', 'INC', '2013', 0.68584471),
        (3, 1, 'GSL', 'INC', '2011', 0.87472457),
        (3, 1, 'GSL', 'INC', '2012', 0.86130072),
        (3, 1, 'GSL', 'INC', '2013', 0.74932829),
        (3, 2, 'GSL', 'INC', '2011', 0.87774796),
        (3, 2, 'GSL', 'INC', '2012', 0.87285453),
        (3, 2, 'GSL', 'INC', '2013', 0.7782881),
        (1, 1, 'GSL', 'LED', '2011', 0.08522608),
        (1, 1, 'GSL', 'LED', '2012', 0.09425481),
        (1, 1, 'GSL', 'LED', '2013', 0.17735249),
        (1, 2, 'GSL', 'LED', '2011', 0.17505889),
        (1, 2, 'GSL', 'LED', '2012', 0.18806257),
        (1, 2, 'GSL', 'LED', '2013', 0.31415529),
        (3, 1, 'GSL', 'LED', '2011', 0.12527543),
        (3, 1, 'GSL', 'LED', '2012', 0.13869928),
        (3, 1, 'GSL', 'LED', '2013', 0.25067171),
        (3, 2, 'GSL', 'LED', '2011', 0.12225204),
        (3, 2, 'GSL', 'LED', '2012', 0.12714547),
        (3, 2, 'GSL', 'LED', '2013', 0.2217119),
        (1, 1, 'LFL', 'T12', '2011', 0.41604117),
        (1, 1, 'LFL', 'T12', '2012', 0.41195155),
        (1, 1, 'LFL', 'T12', '2013', 0.44353641),
        (1, 2, 'LFL', 'T12', '2011', 0.29310758),
        (1, 2, 'LFL', 'T12', '2012', 0.28591929),
        (1, 2, 'LFL', 'T12', '2013', 0.30929546),
        (3, 1, 'LFL', 'T12', '2011', 0.43981098),
        (3, 1, 'LFL', 'T12', '2012', 0.43168629),
        (3, 1, 'LFL', 'T12', '2013', 0.46185268),
        (3, 2, 'LFL', 'T12', '2011', 0.30942591),
        (3, 2, 'LFL', 'T12', '2012', 0.30073385),
        (3, 2, 'LFL', 'T12', '2013', 0.33432025),
        (1, 1, 'LFL', 'T-8', '2011', 0.33771134),
        (1, 1, 'LFL', 'T-8', '2012', 0.33900962),
        (1, 1, 'LFL', 'T-8', '2013', 0.37062741),
        (1, 2, 'LFL', 'T-8', '2011', 0.40173711),
        (1, 2, 'LFL', 'T-8', '2012', 0.40616518),
        (1, 2, 'LFL', 'T-8', '2013', 0.45407724),
        (3, 1, 'LFL', 'T-8', '2011', 0.30517175),
        (3, 1, 'LFL', 'T-8', '2012', 0.30744705),
        (3, 1, 'LFL', 'T-8', '2013', 0.33910227),
        (3, 2, 'LFL', 'T-8', '2011', 0.26764825),
        (3, 2, 'LFL', 'T-8', '2012', 0.276772),
        (3, 2, 'LFL', 'T-8', '2013', 0.33146147),
        (1, 1, 'LFL', 'T-5', '2011', 0.24624749),
        (1, 1, 'LFL', 'T-5', '2012', 0.24903882),
        (1, 1, 'LFL', 'T-5', '2013', 0.18583618),
        (1, 2, 'LFL', 'T-5', '2011', 0.30515531),
        (1, 2, 'LFL', 'T-5', '2012', 0.30791553),
        (1, 2, 'LFL', 'T-5', '2013', 0.23662731),
        (3, 1, 'LFL', 'T-5', '2011', 0.25501727),
        (3, 1, 'LFL', 'T-5', '2012', 0.26086665),
        (3, 1, 'LFL', 'T-5', '2013', 0.19904505),
        (3, 2, 'LFL', 'T-5', '2011', 0.42292584),
        (3, 2, 'LFL', 'T-5', '2012', 0.42249415),
        (3, 2, 'LFL', 'T-5', '2013', 0.33421828)],
        dtype=[('CDIV', 'i4'), ('BLDG', 'i4'), ('EQPCLASS', 'U4'),
               ('BULBTYPE', 'U4'), ('YEAR', 'i4'), ('FACTOR', 'f8')])

    # Test the function that combines the lighting efficiency factors
    # and stock data to develop efficiency-and-stock lighting weighting
    # factors
    def test_lighting_weighting_factors_function(self):
        result = rm.calc_lighting_factors(self.nrg_stock_array,
                                          self.lighting_eff_result,
                                          self.total_n_years,
                                          self.n_lighting_types)

        # Extract the numeric entries for matching lighting and bulb
        # types from the reference array and test array and compare
        # the year values
        for expect_row in self.lt_factor_expected:
            # Grab the matching row from the array output by the
            # function under test
            result_row = result[np.all([
                result['CDIV'] == expect_row['CDIV'],
                result['BLDG'] == expect_row['BLDG'],
                result['EQPCLASS'] == expect_row['EQPCLASS'],
                result['BULBTYPE'] == expect_row['BULBTYPE'],
                result['YEAR'] == expect_row['YEAR']], axis=0)]

            # Test that each lighting weighting factor in the array
            # output by the function is the same as in the comparison
            # array of expected values
            np.testing.assert_allclose(
                expect_row['FACTOR'], result_row['FACTOR'])


class LightingDictModificationFunctionTest(unittest.TestCase):
    """ Test the function that converts the technology_supplydict
    from being appropriate for the 2015 AEO, where incandescent bulbs
    are coded with the string 'Inc', to the 2017/2018 AEO, where those
    bulbs are coded with 'INC'. """

    # Define the expected contents of technology_supplydict after
    # being modified by the function under test
    comparison_tech_dict = {'solar WH': 'SOLAR_WH',
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
                            'general service (incandescent)': ('GSL', 'INC'),
                            'general service (CFL)': ('GSL', 'CFL'),
                            'general service (LED)': ('GSL', 'LED'),
                            'reflector (incandescent)': ('REF', 'INC'),
                            'reflector (CFL)': ('REF', 'CFL'),
                            'reflector (halogen)': ('REF', 'HAL'),
                            'reflector (LED)': ('REF', 'LED'),
                            'external (incandescent)': ('EXT', 'INC'),
                            'external (CFL)': ('EXT', 'CFL'),
                            'external (high pressure sodium)': ('EXT', 'HPS'),
                            'external (LED)': ('EXT', 'LED'),
                            'furnace (NG)': 'NG_FA',
                            'boiler (NG)': 'NG_RAD',
                            'NGHP': 'NG_HP',
                            'furnace (distillate)': 'DIST_FA',
                            'boiler (distillate)': 'DIST_RAD',
                            'furnace (LPG)': 'LPG_FA',
                            'stove (wood)': 'WOOD_HT',
                            'resistance': 'GE2',
                            'secondary heater (kerosene)': 'KS',
                            'secondary heater (LPG)': 'LG',
                            'secondary heater (wood)': 'WD',
                            'secondary heater (coal)': 'CL',
                            'secondary heater': ''
                            }

    # Test that before calling the lighting dict update function, the
    # supply-side technology dict and the comparison dict defined in
    # this test are not the same
    def test_difference_without_modification(self):
        self.assertFalse(
            rm.technology_supplydict == self.comparison_tech_dict)

    # Test that after calling the lighting dict update function, the
    # supply-side technology mapping dict and the comparison dict
    # defined in this test are identical
    def test_modification_of_global_dict(self):
        rm.update_lighting_dict()
        self.assertDictEqual(rm.technology_supplydict,
                             self.comparison_tech_dict)


# Offer external code execution (include all lines below this point in all
# test files)
def main():
    # Triggers default behavior of running all test fixtures in the file
    unittest.main()


if __name__ == '__main__':
    main()
