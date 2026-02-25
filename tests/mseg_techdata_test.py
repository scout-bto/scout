#!/usr/bin/env python3

""" Tests for processing microsegment cost, performance, and lifetime data """

# Import code to be tested
from scout import mseg_techdata

# Import needed packages
import unittest
import numpy
import itertools


class CommonMethods(object):
    """Define common methods for use in all tests below."""

    def dict_check(self, dict1, dict2, path=None):
        """Compare two dicts for equality, allowing for floating‑point error,
        and print a helpful message (incl. units, when available) on failure.
        """
        if path is None:
            path = []                       # first call → empty list

        fill_val = ('substituted entry', 5.2)

        for (k, i), (k2, i2) in itertools.zip_longest(
                sorted(dict1.items()), sorted(dict2.items()),
                fillvalue=fill_val):

            self.assertEqual(k, k2)         # keys must match

            if isinstance(i, dict):         # dive deeper
                self.assertCountEqual(i, i2)
                self.dict_check(i, i2, path + [k])

            elif isinstance(i, list):       # compare lists
                if not (type(i) is type(i2) and len(i) == len(i2)):
                    print("Mismatch at key‑path:", '.'.join(path + [k]))
                    print("Expected:", i2)
                    print("Actual:  ", i)
                self.assertTrue(type(i) is type(i2) and len(i) == len(i2))
                for x in range(len(i)):
                    try:
                        self.assertEqual(i[x], i2[x])
                    except TypeError:
                        for x_s in range(len(i[x])):
                            self.assertEqual(i[x][x_s], i2[x][x_s])

            elif isinstance(i, str):        # plain strings
                self.assertEqual(i, i2)

            else:                           # numbers (or anything else)
                try:
                    self.assertAlmostEqual(i, i2, places=2)
                except AssertionError:
                    print("Mismatch at keypath:", '.'.join(path + [k]))
                    print("Expected:", i2)
                    print("Actual:  ", i)
                    raise                        # keep the test failing


class SimpleWalkTest(unittest.TestCase, CommonMethods):
    """ Test operation of a simpler version of the walk_techdata function,
    which is used to walk through all the levels of the microsegments dict
    structure and update the values at the end of each terminal leaf node """

    # Define a test dict to walk through
    in_dict = {
        "cdiv 1": {"bldg 1": {"total square footage": None, "fuel 1": {
            "end use 1": {"tech 1": None}}}},
        "cdiv 2": {"bldg 2": {"total square footage": None, "fuel 2": {
            "end use 2": {"tech 2": None}},
            "fuel 3": {
                "end use 3": {"tech 3": None}}}},
        "cdiv 3": {"bldg 3": {"total square footage": None, "fuel 3": {
            "end use 3": {"tech 4": None}}},
            "bldg 4": {"fuel 4": {
                "end use 4": {"tech 5": None}}}},
        "cdiv 4": {"bldg 4": {"total square footage": None, "fuel 5": {
            "end use 5": {"tech 6": {"sub tech 1": None,
                                     "sub tech 2": None}}}}}}

    # Define an output dict that should be yielded via the walk routine. As
    # an additional check, the key chains leading to each terminal leaf node
    # are set to be the values for those leaf nodes.
    out_dict = {
        "cdiv 1": {"bldg 1": {
            "total square footage": None,
            "fuel 1": {"end use 1": {
                "tech 1":
                ["cdiv 1", "bldg 1", "fuel 1", "end use 1", "tech 1"]}}}},
        "cdiv 2": {"bldg 2": {
            "total square footage": None,
            "fuel 2": {"end use 2": {
                "tech 2":
                ["cdiv 2", "bldg 2", "fuel 2", "end use 2", "tech 2"]}},
            "fuel 3": {"end use 3": {
                "tech 3":
                ["cdiv 2", "bldg 2", "fuel 3", "end use 3", "tech 3"]}}}},
        "cdiv 3": {
            "bldg 3": {
                "total square footage": None,
                "fuel 3": {"end use 3": {
                    "tech 4":
                    ["cdiv 3", "bldg 3", "fuel 3", "end use 3", "tech 4"]}}},
            "bldg 4": {
                "fuel 4": {"end use 4": {
                    "tech 5":
                    ["cdiv 3", "bldg 4", "fuel 4", "end use 4", "tech 5"]}}}},
        "cdiv 4": {
            "bldg 4": {
                "total square footage": None,
                "fuel 5": {"end use 5": {
                    "tech 6": {
                        "sub tech 1":
                        ["cdiv 4", "bldg 4", "fuel 5", "end use 5", "tech 6",
                         "sub tech 1"],
                        "sub tech 2": ["cdiv 4", "bldg 4", "fuel 5",
                                       "end use 5", "tech 6", "sub tech 2"]
                    }}}}}}

    def simple_walk(self, in_dict, key_list=[]):
        """ This function represents a simpler version of the walk_techdata
        function in mseg_techdata_test.py where terminal leaf node values are
        assigned as the key chain that leads to the given leaf node """
        for key, item in sorted(in_dict.items()):
            # If there are additional levels in the dict, call the function
            # again to advance another level deeper into the data structure
            if isinstance(item, dict):
                self.simple_walk(item, key_list + [key])
            # If a leaf node has been reached, finish constructing the key
            # list for the current location and update the data in the dict
            else:
                # Update key chain
                leaf_node_keys = key_list + [key]
                # Avoid updating a "total square footage" leaf node in
                # the input dict; square footage is not relevant to the
                # cost, performance, and lifetime data
                if leaf_node_keys[-1] != "total square footage":
                    # Update dict key value to the updated key chain
                    in_dict[key] = leaf_node_keys

        # Return updated dict
        return in_dict

    # Test that a walk through the in_dict above updates its terminal
    # leaf nodes to the correct values in the out_dict above
    def test_walk_ok(self):
        dict1 = self.simple_walk(self.in_dict)
        dict2 = self.out_dict
        self.dict_check(dict1, dict2)


class ListGeneratorTest(unittest.TestCase, CommonMethods):
    """ Test that the list_generator_techdata function correctly updates the
    terminal leaf node values for an input dictionary with input technology
    performance, cost, lifetime, and consumer choice information """

    # Define a test input array in the format of EIA performance, cost, and
    # consumer choice data on non-lighting technologies
    eia_nlt_cp = numpy.array([
        (1, 2005, 2040, 3, 4.5, 3000, 3000, 0, 0, 0, 0, 2, 3, b"ELEC_RAD2"),
        (1, 2010, 2011, 1, 2.65, 1200, 1200, 0, 0, 0, 0, 1, 2, b"ELEC_HP2"),
        (1, 2011, 2012, 1, 3.1, 1250, 1250, 0, 0, 0, 0, 1, 2, b"ELEC_HP2"),
        (1, 2012, 2014, 1, 4.5, 1450, 1450, 4, 3, 2, 1, 1, 2, b"ELEC_HP2"),
        (1, 2014, 2040, 1, 5, 2000, 2000, 4, 3, 2, 1, 1, 2, b"ELEC_HP2"),
        (1, 2010, 2011, 2, 3.65, 1200, 1200, 0, 0, 0, 0, 5, 6, b"ELEC_HP2"),
        (1, 2011, 2012, 2, 4.1, 1250, 1250, 0, 0, 0, 0, 5, 6, b"ELEC_HP2"),
        (1, 2012, 2014, 2, 5.5, 1450, 1450, 0, 0, 0, 0, 5, 6, b"ELEC_HP2"),
        (1, 2014, 2040, 2, 6, 2000, 2000, 0, 0, 0, 0, 5, 6, b"ELEC_HP2"),
        (1, 2014, 2040, 2, 5, 2000, 2000, 0, 0, 0, 0, 5, 6, b"ELEC_HP2"),
        (2, 2010, 2013, 3, 4.65, 1400, 1400, 0, 0, 0, 0, 3, 4, b"ELEC_HP2"),
        (2, 2013, 2040, 3, 5.1, 1450, 1450, 0, 0, 0, 0, 3, 4, b"ELEC_HP2"),
        (1, 2005, 2040, 1, 2.75, 1200, 1200, 0, 0, 0, 0, 1, 2, b"ELEC_HP3"),
        (1, 2010, 2011, 1, 2.75, 1250, 1250, 0, 0, 0, 0, 1, 2, b"ELEC_HP3"),
        (1, 2011, 2012, 1, 3.2, 1270, 1270, 0, 0, 0, 0, 1, 2, b"ELEC_HP3"),
        (1, 2012, 2014, 1, 4.6, 1800, 1800, 0, 0, 0, 0, 1, 2, b"ELEC_HP3"),
        (1, 2014, 2040, 1, 5.1, 1900, 1900, 0, 0, 0, 0, 1, 2, b"ELEC_HP3"),
        (1, 2005, 2040, 1, 2.8, 1000, 1000, 0, 0, 0, 0, 1, 2, b"ELEC_HP4"),
        (1, 2010, 2011, 1, 2.9, 1300, 1300, 0, 0, 0, 0, 1, 2, b"ELEC_HP4"),
        (1, 2011, 2012, 1, 3.3, 1400, 1400, 0, 0, 0, 0, 1, 2, b"ELEC_HP4"),
        (1, 2012, 2014, 1, 4.8, 1500, 1500, 0, 0, 0, 0, 1, 2, b"ELEC_HP4"),
        (1, 2014, 2040, 1, 6, 2000, 2000, 0, 0, 0, 0, 1, 2, b"ELEC_HP4"),
        (5, 2007, 2040, 4, 3, 1000, 1000, 0, 0, 0, 0, 7, 8, b"ELEC_WH1"),
        (5, 2005, 2009, 4, 2.8, 1000, 1000, 0, 0, 0, 0, 7, 8, b"NG_WH1"),
        (5, 2009, 2040, 4, 2.9, 1300, 1300, 0, 0, 0, 0, 7, 8, b"NG_WH1"),
        (5, 2005, 2009, 4, 2.9, 1000, 1000, 0, 0, 0, 0, 7, 8, b"NG_WH3"),
        (5, 2009, 2040, 4, 3.2, 1300, 1300, 0, 0, 0, 0, 7, 8, b"NG_WH3"),
        (5, 2005, 2009, 4, 3.2, 2000, 2000, 0, 0, 0, 0, 7, 8, b"NG_WH4"),
        (5, 2009, 2040, 4, 3.5, 1500, 1500, 0, 0, 0, 0, 7, 8, b"NG_WH4"),
        (5, 2005, 2009, 5, 2.8, 1000, 1000, 0, 0, 0, 0, 7, 8, b"NG_WH1"),
        (5, 2009, 2040, 5, 2.9, 1300, 1300, 0, 0, 0, 0, 7, 8, b"NG_WH1"),
        (5, 2005, 2009, 5, 2.9, 1000, 1000, 0, 0, 0, 0, 7, 8, b"NG_WH3"),
        (5, 2009, 2040, 5, 3.2, 1300, 1300, 0, 0, 0, 0, 7, 8, b"NG_WH3"),
        (5, 2005, 2009, 5, 3.2, 2000, 2000, 0, 0, 0, 0, 7, 8, b"NG_WH4"),
        (5, 2009, 2040, 5, 3.5, 1500, 1500, 0, 0, 0, 0, 7, 8, b"NG_WH4"),
        (6, 2010, 2011, 2, 28, 100, 100, 0, 0, 0, 0, 6, 7, b"ELEC_STV2"),
        (6, 2012, 2040, 2, 29, 130, 130, 0, 0, 0, 0, 6, 7, b"ELEC_STV2"),
        (6, 2010, 2011, 2, 29, 150, 150, 0, 0, 0, 0, 6, 7, b"NG_STV2"),
        (6, 2012, 2040, 2, 32, 160, 160, 0, 0, 0, 0, 6, 7, b"NG_STV2"),
        (6, 2010, 2011, 2, 31, 200, 200, 0, 0, 0, 0, 6, 7, b"NG_STV4"),
        (6, 2012, 2040, 2, 33, 170, 170, 0, 0, 0, 0, 6, 7, b"NG_STV4"),
        (6, 2010, 2011, 2, 32, 200, 200, 0, 0, 0, 0, 6, 7, b"LPG_STV4"),
        (6, 2012, 2040, 2, 35, 175, 175, 0, 0, 0, 0, 6, 7, b"LPG_STV4"),
        (6, 2010, 2011, 2, 33, 300, 300, 0, 0, 0, 0, 6, 7, b"ELEC_STV4"),
        (6, 2012, 2040, 2, 36, 250, 250, 0, 0, 0, 0, 6, 7, b"ELEC_STV4"),
        (7, 2010, 2011, 2, 128, 1010, 1010, 0, 0, 0, 0, 0, 1, b"ELEC_DRY1"),
        (7, 2012, 2040, 2, 129, 1310, 1310, 0, 0, 0, 0, 0, 1, b"ELEC_DRY1"),
        (7, 2010, 2011, 2, 129, 1510, 1510, 0, 0, 0, 0, 0, 1, b"NG_DRY3"),
        (7, 2012, 2040, 2, 132, 1610, 1610, 0, 0, 0, 0, 0, 1, b"NG_DRY3"),
        (7, 2010, 2011, 2, 131, 2010, 2010, 0, 0, 0, 0, 0, 1, b"NG_DRY4"),
        (7, 2012, 2040, 2, 133, 1710, 1710, 0, 0, 0, 0, 0, 1, b"NG_DRY4"),
        (7, 2010, 2011, 2, 133, 3010, 3010, 0, 0, 0, 0, 0, 1, b"ELEC_DRY"),
        (7, 2012, 2040, 2, 136, 2510, 2510, 0, 0, 0, 0, 0, 1, b"ELEC_DRY"),
        (3, 2010, 2020, 3, 15, 150, 150, 0, 0, 0, 0, 4, 5, b"CL_WASH_T1"),
        (3, 2020, 2040, 3, 15, 150, 150, 0, 0, 0, 0, 4, 5, b"CL_WASH_T1"),
        (3, 2010, 2040, 3, 12, 175, 175, 0, 0, 0, 0, 4, 5, b"CL_WASH_T3"),
        (3, 2010, 2040, 3, 10, 300, 300, 0, 0, 0, 0, 4, 5, b"CL_WASH_T4"),
        (3, 2010, 2040, 3, 15, 150, 150, 0, 0, 0, 0, 4, 5, b"CL_WASH_F2"),
        (3, 2010, 2040, 3, 12, 175, 175, 0, 0, 0, 0, 4, 5, b"CL_WASH_F3"),
        (3, 2010, 2040, 3, 10, 300, 300, 0, 0, 0, 0, 4, 5, b"CL_WASH_F4"),
        (8, 2005, 2009, 3, 200, 300, 300, 0, 0, 0, 0, 6, 6, b"REFR_SF2"),
        (8, 2009, 2013, 3, 300, 250, 250, 0, 0, 0, 0, 6, 6, b"REFR_SF2"),
        (8, 2013, 2040, 3, 400, 200, 200, 0, 0, 0, 0, 6, 6, b"REFR_SF2"),
        (8, 2005, 2009, 3, 300, 400, 400, 0, 0, 0, 0, 7, 7, b"REFR_BF2"),
        (8, 2009, 2013, 3, 400, 300, 300, 0, 0, 0, 0, 7, 7, b"REFR_BF2"),
        (8, 2013, 2040, 3, 500, 200, 200, 0, 0, 0, 0, 7, 7, b"REFR_BF2"),
        (8, 2005, 2009, 3, 500, 500, 500, 0, 0, 0, 0, 8, 8, b"REFR_TF2"),
        (8, 2009, 2013, 3, 600, 400, 400, 0, 0, 0, 0, 8, 8, b"REFR_TF2"),
        (8, 2013, 2040, 3, 700, 300, 300, 0, 0, 0, 0, 8, 8, b"REFR_TF2"),
        (8, 2005, 2009, 3, 800, 800, 800, 0, 0, 0, 0, 6, 6, b"REFR_SF4"),
        (8, 2009, 2013, 3, 900, 700, 700, 0, 0, 0, 0, 6, 6, b"REFR_SF4"),
        (8, 2013, 2040, 3, 1000, 600, 600, 0, 0, 0, 0, 6, 6, b"REFR_SF4"),
        (8, 2005, 2009, 3, 900, 200, 200, 0, 0, 0, 0, 6, 6, b"REFR_BF4"),
        (8, 2009, 2013, 3, 1000, 100, 100, 0, 0, 0, 0, 6, 6, b"REFR_BF4"),
        (8, 2013, 2040, 3, 1100, 50, 50, 0, 0, 0, 0, 6, 6, b"REFR_BF4"),
        (8, 2005, 2009, 3, 900, 1400, 1400, 0, 0, 0, 0, 6, 6, b"REFR_TF3"),
        (8, 2009, 2013, 3, 950, 1200,  1200, 0, 0, 0, 0, 6, 6, b"REFR_TF3"),
        (8, 2013, 2040, 3, 1000, 1100, 1100, 0, 0, 0, 0, 6, 6, b"REFR_TF3"),
        (8, 2005, 2009, 3, 1500, 700, 700, 0, 0, 0, 0, 6, 6, b"REFR_TF4"),
        (8, 2009, 2013, 3, 1600, 650, 650, 0, 0, 0, 0, 6, 6, b"REFR_TF4"),
        (8, 2013, 2040, 3, 1700, 550, 550, 0, 0, 0, 0, 6, 6, b"REFR_TF4"),
        (8, 2005, 2009, 1, 1500, 700, 700, 0, 0, 0, 0, 6, 6, b"REFR_TF4"),
        (8, 2009, 2013, 1, 1600, 650, 650, 0, 0, 0, 0, 6, 6, b"REFR_TF4"),
        (8, 2013, 2040, 1, 1700, 550, 550, 0, 0, 0, 0, 6, 6, b"REFR_TF4"),
        (2, 2005, 2009, 4, 2.75, 500, 500, 0, 0, 0, 0, 6, 6, b"NG_HP2"),
        (2, 2009, 2011, 4, 2.95, 550, 550, 0, 0, 0, 0, 6, 6, b"NG_HP2"),
        (2, 2011, 2050, 4, 3.15, 575, 575, 0, 0, 0, 0, 6, 6, b"NG_HP2"),
        (2, 2005, 2009, 4, 2.75, 500, 500, 0, 0, 0, 0, 6, 6, b"GEO_HP2"),
        (2, 2009, 2011, 4, 2.95, 550, 550, 0, 0, 0, 0, 6, 6, b"GEO_HP2"),
        (2, 2011, 2050, 4, 3.15, 575, 575, 0, 0, 0, 0, 6, 6, b"GEO_HP2"),
        (1, 2005, 2009, 4, 2.75, 500, 500, 0, 0, 0, 0, 6, 6, b"GEO_HP2"),
        (1, 2009, 2011, 4, 2.95, 550, 550, 0, 0, 0, 0, 6, 6, b"GEO_HP2"),
        (1, 2011, 2050, 4, 3.15, 575, 575, 0, 0, 0, 0, 6, 6, b"GEO_HP2"),
        (2, 2005, 2009, 4, 2.75, 500, 500, 0, 0, 0, 0, 6, 6, b"GEO_HP4"),
        (2, 2009, 2011, 4, 2.95, 550, 550, 0, 0, 0, 0, 6, 6, b"GEO_HP4"),
        (2, 2011, 2050, 4, 3.15, 575, 575, 0, 0, 0, 0, 6, 6, b"GEO_HP4"),
        (1, 2005, 2009, 4, 2.75, 500, 500, 0, 0, 0, 0, 6, 6, b"GEO_HP4"),
        (1, 2009, 2011, 4, 2.95, 550, 550, 0, 0, 0, 0, 6, 6, b"GEO_HP4"),
        (1, 2011, 2050, 4, 3.15, 575, 575, 0, 0, 0, 0, 6, 6, b"GEO_HP4"),
        (1, 2009, 2050, 3, 3.15, 575, 575, 0, 0, 0, 0, 6, 6, b"NG_RAD2"),
        (1, 2009, 2011, 11, 2.95, 550, 550, 0, 0, 0, 0, 6, 6, b"NG_FA2"),
        (1, 2011, 2050, 11, 3.15, 575, 575, 0, 0, 0, 0, 6, 6, b"NG_FA2"),
        (1, 2009, 2011, 11, 2.95, 550, 550, 0, 0, 0, 0, 6, 6, b"NG_FA4"),
        (1, 2011, 2050, 11, 3.15, 575, 575, 0, 0, 0, 0, 6, 6, b"NG_FA4")],
        dtype=[
            ("ENDUSE", "<i8"),
            ("START_EQUIP_YR", "<i8"),
            ("END_EQUIP_YR", "<f8"),
            ("CDIV", "<i8"),
            ("BASE_EFF", "<f8"),
            ("INST_COST", "<f8"),
            ("RETAIL_COST", "<f8"),
            ("FD_REPL_SUB", "<f8"),
            ("FD_NEW_SUB", "<f8"),
            ("NF_REPL_SUB", "<f8"),
            ("NF_NEW_SUB", "<f8"),
            ("EFF_CHOICE_P1", "<f8"),
            ("EFF_CHOICE_P2", "<f8"),
            ("NAME", "S10")])

    # Define a test input array in the format of EIA lifetime
    # data on non-lighting technologies
    eia_nlt_l = numpy.array([(1, 3.5, 19.5, b"ELEC_RAD"),
                             (1, 15, 20.1,
                             b"ELEC_HP"),
                             (1, 15.6, 20.6, b"NG_FA"),
                             (2, 18.6, 19.1, b"CENT_AIR"),
                             (2, 18, 25,
                             b"ELEC_HP"),
                             (5, 10, 20.5, b"ELEC_WH"),
                             (5, 8.5, 15.0, b"NG_WH"),
                             (6, 10.5, 12.4, b"ELEC_STV"),
                             (6, 17.9, 25, b"NG_STV"),
                             (6, 14.7, 27, b"LPG_STV"),
                             (7, 13.2, 21.6, b"ELEC_DRY"),
                             (7, 10, 17, b"NG_DRY"),
                             (3, 8.9, 16.7, b"CL_WASH"),
                             (8, 6.5, 11.1, b"REFR"),
                             (9, 5, 10.1, b"FREZ"),
                             (2, 2, 10, b"NG_HP"),
                             (2, 2, 10, b"GEO_HP"),
                             (1, 2, 10, b"GEO_HP"),
                             (1, 2, 10, b"NG_FA")],
                            dtype=[("ENDUSE", "<i8"),
                                   ("LIFE_MIN", "<f8"),
                                   ("LIFE_MAX", "<f8"),
                                   ("NAME", "S10")])

    # Define a test input array in the format of EIA performance, cost, and
    # lifetime data on lighting technologies
    eia_lt = numpy.array([
        (2008, 2012, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.33, 10000, 55,
         b"GSL", b"Inc", -0.95, -0.1),
        (2012, 2013, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.03, 20000, 60,
         b"GSL", b"Inc", -0.95, -0.1),
        (2013, 2017, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.53, 35000, 61.2,
         b"GSL", b"Inc", -0.95, -0.1),
        (2017, 2020, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2.75, 40000, 80.3,
         b"GSL", b"Inc", -0.95, -0.1),
        (2020, 2040, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3.45, 50000, 90,
         b"GSL", b"Inc", -0.95, -0.1),
        (2005, 2008, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.35, 10000, 60,
         b"GSL", b"LED", -0.95, -0.1),
        (2008, 2010, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.13, 30000, 65,
         b"GSL", b"LED", -0.95, -0.1),
        (2010, 2012, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.55, 37000, 63.2,
         b"GSL", b"LED", -0.95, -0.1),
        (2012, 2040, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2.78, 42000, 90.3,
         b"GSL", b"LED", -0.95, -0.1),
        (2010, 2040, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3.71, 8000, 100.3,
         b"REF", b"LED", -0.95, -0.1)],
                         dtype=[("START_EQUIP_YR", "<i8"),
                                ("END_EQUIP_YR", "<f8"),
                                ("EE_Sub1", "<f8"),
                                ("EE_Sub2", "<f8"),
                                ("EE_Sub3", "<f8"),
                                ("EE_Sub4", "<f8"),
                                ("EE_Sub5", "<f8"),
                                ("EE_Sub6", "<f8"),
                                ("EE_Sub7", "<f8"),
                                ("EE_Sub8", "<f8"),
                                ("EE_Sub9", "<f8"),
                                ("BASE_EFF", "<f8"),
                                ("LIFE_HRS", "<f8"),
                                ("INST_COST", "<f8"),
                                ("NAME", "S3"),
                                ("BULB_TYPE", "S3"),
                                ("Beta_1", "<f8"),
                                ("Beta_2", "<f8")])

    # Define a test dict in the format of BTO-defined performance, cost
    # and lifetime data on all technologies not covered by EIA data
    # *** FOR NOW *** do not update any technologies in this routine for which
    # there are no EIA cost, performance, and lifetime characteristics
    tech_non_eia = {}
    # tech_non_eia = {"secondary heating (electric)": [[5, 2, "Source 1"],
    #                                                  [2, 3, "Source 2"],
    #                                                  [50, 70, "Source 3"],
    #                                                  "COP"],
    #                 "secondary heating (natural gas)": [[4, 1, "Source 4"],
    #                                                     [87, 92, "Source 5"],
    #                                                     [60, 80, "Source 6"],
    #                                                     "AFUE"],
    #                 "secondary heating (kerosene)": [[1.1, 2.2, "Source 7"],
    #                                                  [85, 99, "Source 8"],
    #                                                  [100, 200, "Source 9"],
    #                                                  "AFUE"],
    #                 "secondary heating (wood)": [[10, 5, "Source 10"],
    #                                              [70, 85, "Source 11"],
    #                                              [45, 50, "Source 12"],
    #                                              "AFUE"],
    #                 "secondary heating (LPG)": [[5, 5, "Source 13"],
    #                                             [90, 95, "Source 14"],
    #                                             [150, 175, "Source 15"],
    #                                             "AFUE"],
    #                 "secondary heating (coal)": [[15, 10, "Source 16"],
    #                                              [77, 82, "Source 17"],
    #                                              [35, 55, "Source 17"],
    #                                              "AFUE"],
    #                 "TV": [[1, 0.5, "Source 18"], [10.1, 20.4, "Source 18"],
    #                        [500, 605, "Source 19"], "W"],
    #                 "set top box": [[25, 2, "Source 20"],
    #                                 [100, 50, "Source 20"],
    #                                 [60, 43, "Source 20"], "W"],
    #                 "DVD": [[7, 4, "Source 21"],
    #                         [70, 60, "Source 21"], [20, 30, "Source 21"],
    #                         "W"],
    #                 "other MELs": [[0, 0, "NA"], [0, 0, "NA"],
    #                                [0, 0, "NA"], "NA"],
    #                 "windows conduction": [[25, 5, "RS Means"],
    #                                        [7, 10, "NREL Efficiency DB"],
    #                                        [20, 30, "RS Means"], "R Value"],
    #                 "windows solar": [[20, 2, "RS Means"],
    #                                   [0.4, 0.3, "NREL Efficiency DB"],
    #                                   [20, 30, "RS Means"], "SHGC"],
    #                 "wall": [[25, 7, "RS Means"], [
    #                           0, 0, 0, 0, 6, 7, "EnergyStar"],
    #                          [35, 40, "RS Means"], "R Value/sq.in."]}

    # Define the modeling time horizon to test (2009:2013)
    years = [str(i) for i in range(2009, 2013 + 1)]
    project_dict = dict.fromkeys(years)

    # # Define sample technology choice parameters for residential envelope
    # # component technologies (technology choice information is not included
    # # for envelope component technologies in 'tech_non_eia' above)
    # non_eia_env_choice = {"b1": {k: -0.003
    #                              for k in project_dict.keys()},
    #                       "b2": {k: -0.012
    #                              for k in project_dict.keys()}}

    # Define a sample list of full dictionary key chains that are defined
    # while running through the microsegments JSON structure and which will
    # be used to determine what performance, cost, lifetime, and consumer
    # choice data to look for
    tech_ok_keys = [["new england", "single family home",
                     "electricity", "heating", "supply", "ASHP"],
                    ["east north central", "multi family home",
                     "electricity", "refrigeration"],
                    ["east north central", "multi family home",
                     "electricity", "other",
                     "clothes washing"],
                    ["mid atlantic", "single family home",
                     "natural gas", "cooking"],
                    ["mid atlantic", "single family home",
                     "natural gas", "drying"],
                    ["west north central", "mobile home",
                     "natural gas", "water heating"],
                    ["west north central", "mobile home",
                     "electricity", "lighting",
                     "general service (LED)"],
                    ["mid atlantic", "single family home",
                     "electricity", "secondary heating",
                     "supply", "secondary heater"],
                    ["mid atlantic", "single family home",
                     "electricity", "secondary heating",
                     "demand", "windows conduction"],
                    ["west north central", "multi family home",
                     "natural gas", "cooling",
                     "supply", "NGHP"],
                    ["west north central", "multi family home",
                     "electricity", "heating", "supply", "GSHP"],
                    ["west north central", "multi family home",
                     "electricity", "cooling", "supply", "GSHP"],
                    ["west north central", "multi family home",
                     "natural gas", "heating", "supply", "furnace (NG)"]]

    # Define an output dict with leaf node values that should be yielded
    # by the walk_techdata function given the valid inputs above.  Output dict
    # information for a given technology is organized by performance,
    # installed cost, lifetime, and consumer choice.  Within the performance
    # and cost categories, a "typical" and "best" level are provided.  For
    # performance, cost, and lifetime categories, the units of the information
    # are provided.  For all categories, source information is provided.
    ok_datadict_out = [{
        "performance": {
            "typical": {"2009": 2.65, "2010": 2.65, "2011": 3.1, "2012": 4.5,
                        "2013": 4.5},
            "best": {"2009": 2.9, "2010": 2.9, "2011": 3.3, "2012": 4.8,
                     "2013": 4.8},
            "units": "COP",
            "source": "EIA AEO"},
        "installed cost": {
            "before incentives": {
                "typical": {
                    "new": {
                        "2009": 1200, "2010": 1200, "2011": 1250, "2012": 1450,
                        "2013": 1450},
                    "existing": {
                        "2009": 1200, "2010": 1200, "2011": 1250, "2012": 1450,
                        "2013": 1450}},
                "best": {
                    "new": {
                        "2009": 1300, "2010": 1300, "2011": 1400, "2012": 1500,
                        "2013": 1500},
                    "existing": {
                        "2009": 1300, "2010": 1300, "2011": 1400, "2012": 1500,
                        "2013": 1500}},
                "units": "2022$/unit",
                "source": (
                    "EIA AEO (NOTE EIA convention of dividing HP costs "
                    "for existing buildings by 2 while putting all HP costs "
                    "for new construction under the heating end use)")},
            "incentives": {
                "by performance tier": {
                    "new": {
                        "2009": [[2.65, 0], [2.75, 0], [2.9, 0]],
                        "2010": [[2.65, 0], [2.75, 0], [2.9, 0]],
                        "2011": [[3.1, 0], [3.2, 0], [3.3, 0]],
                        "2012": [[4.5, 4], [4.6, 0], [4.8, 0]],
                        "2013": [[4.5, 4], [4.6, 0], [4.8, 0]]},
                    "existing": {
                        "2009": [[2.65, 0], [2.75, 0], [2.9, 0]],
                        "2010": [[2.65, 0], [2.75, 0], [2.9, 0]],
                        "2011": [[3.1, 0], [3.2, 0], [3.3, 0]],
                        "2012": [[4.5, 6], [4.6, 0], [4.8, 0]],
                        "2013": [[4.5, 6], [4.6, 0], [4.8, 0]]}
                },
                "performance units": "COP"
            }},
        "lifetime": {
            "average": {"2009": 17.55, "2010": 17.55, "2011": 17.55,
                        "2012": 17.55, "2013": 17.55},
            "range": {"2009": 2.55, "2010": 2.55, "2011": 2.55, "2012": 2.55,
                      "2013": 2.55},
            "units": "years",
            "source": "EIA AEO"},
        "consumer choice": {
            "competed market share": {
                "model type": "logistic regression",
                "parameters": {
                    "typical": {
                        "b1": {"2009": 1, "2010": 1, "2011": 1,
                               "2012": 1, "2013": 1},
                        "b2": {"2009": 2, "2010": 2, "2011": 2,
                               "2012": 2, "2013": 2}},
                    "best": {
                        "b1": {"2009": 1, "2010": 1, "2011": 1,
                               "2012": 1, "2013": 1},
                        "b2": {"2009": 2, "2010": 2, "2011": 2,
                               "2012": 2, "2013": 2}}},
                "source": "EIA AEO"}}},
        {"performance": {
            "typical": {"2009": 433.33, "2010": 433.33, "2011": 433.33,
                        "2012": 433.33, "2013": 533.33},
            "best": {"2009": 1166.67, "2010": 1166.67, "2011": 1166.67,
                     "2012": 1166.67, "2013": 1266.67},
            "units": "kWh/yr",
            "source": "EIA AEO"},
         "installed cost": {
            "before incentives": {
                "typical": {
                    "new": {"2009": 316.67, "2010": 316.67, "2011": 316.67,
                            "2012": 316.67, "2013": 233.33},
                    "existing": {
                        "2009": 316.67, "2010": 316.67, "2011": 316.67,
                        "2012": 316.67, "2013": 233.33}},
                "best": {
                    "new": {"2009": 483.33, "2010": 483.33, "2011": 483.33,
                            "2012": 483.33, "2013": 400},
                    "existing": {
                        "2009": 483.33, "2010": 483.33, "2011": 483.33,
                        "2012": 483.33, "2013": 400}},
                "units": "2022$/unit",
                "source": "EIA AEO"},
            "incentives": {
                "by performance tier": {
                    "new": {
                        "2009": [[400, 0], [1000, 0],
                                 [300, 0], [900, 0],
                                 [600, 0], [950, 0],
                                 [1600, 0]],
                        "2010": [[400, 0], [1000, 0],
                                 [300, 0], [900, 0],
                                 [600, 0], [950, 0],
                                 [1600, 0]],
                        "2011": [[400, 0], [1000, 0],
                                 [300, 0], [900, 0],
                                 [600, 0], [950, 0],
                                 [1600, 0]],
                        "2012": [[400, 0], [1000, 0],
                                 [300, 0], [900, 0],
                                 [600, 0], [950, 0],
                                 [1600, 0]],
                        "2013": [[500, 0], [1100, 0],
                                 [400, 0], [1000, 0],
                                 [700, 0], [1000, 0],
                                 [1700, 0]]},
                    "existing": {
                        "2009": [[400, 0], [1000, 0],
                                 [300, 0], [900, 0],
                                 [600, 0], [950, 0],
                                 [1600, 0]],
                        "2010": [[400, 0], [1000, 0],
                                 [300, 0], [900, 0],
                                 [600, 0], [950, 0],
                                 [1600, 0]],
                        "2011": [[400, 0], [1000, 0],
                                 [300, 0], [900, 0],
                                 [600, 0], [950, 0],
                                 [1600, 0]],
                        "2012": [[400, 0], [1000, 0],
                                 [300, 0], [900, 0],
                                 [600, 0], [950, 0],
                                 [1600, 0]],
                        "2013": [[500, 0], [1100, 0],
                                 [400, 0], [1000, 0],
                                 [700, 0], [1000, 0],
                                 [1700, 0]]}
                },
                "performance units": "kWh/yr"
            }},
         "lifetime": {
            "average": {"2009": 8.8, "2010": 8.8, "2011": 8.8, "2012": 8.8,
                        "2013": 8.8},
            "range": {"2009": 2.3, "2010": 2.3, "2011": 2.3, "2012": 2.3,
                      "2013": 2.3},
            "units": "years",
            "source": "EIA AEO"},
         "consumer choice": {
            "competed market share": {
                "model type": "logistic regression",
                "parameters": {
                    "typical": {
                        "b1": {"2009": 7, "2010": 7, "2011": 7,
                               "2012": 7, "2013": 7},
                        "b2": {"2009": 7, "2010": 7, "2011": 7,
                               "2012": 7, "2013": 7}},
                    "best": {
                        "b1": {"2009": 6, "2010": 6, "2011": 6,
                               "2012": 6, "2013": 6},
                        "b2": {"2009": 6, "2010": 6, "2011": 6,
                               "2012": 6, "2013": 6}}},
                "source": "EIA AEO"}}},
        {"performance": {
            "typical": {"2009": 13.5, "2010": 13.5, "2011": 13.5, "2012": 13.5,
                        "2013": 13.5},
            "best": {"2009": 10, "2010": 10, "2011": 10, "2012": 10,
                     "2013": 10},
            "units": "kWh/cycle",
            "source": "EIA AEO"},
         "installed cost": {
            "before incentives": {
                "typical": {
                    "new": {"2009": 162.5, "2010": 162.5, "2011": 162.5, "2012": 162.5,
                            "2013": 162.5},
                    "existing": {
                        "2009": 162.5, "2010": 162.5, "2011": 162.5, "2012": 162.5,
                        "2013": 162.5}},
                "best": {
                    "new": {"2009": 300, "2010": 300, "2011": 300, "2012": 300,
                            "2013": 300},
                    "existing": {
                        "2009": 300, "2010": 300, "2011": 300, "2012": 300,
                        "2013": 300}},
                "units": "2022$/unit",
                "source": "EIA AEO"},
            "incentives": {
                "by performance tier": {
                    "new": {
                        "2009": [[15, 0], [12, 0], [10, 0],
                                 [15, 0], [12, 0], [10, 0]],
                        "2010": [[15, 0], [12, 0], [10, 0],
                                 [15, 0], [12, 0], [10, 0]],
                        "2011": [[15, 0], [12, 0], [10, 0],
                                 [15, 0], [12, 0], [10, 0]],
                        "2012": [[15, 0], [12, 0], [10, 0],
                                 [15, 0], [12, 0], [10, 0]],
                        "2013": [[15, 0], [12, 0], [10, 0],
                                 [15, 0], [12, 0], [10, 0]]},
                    "existing": {
                        "2009": [[15, 0], [12, 0], [10, 0],
                                 [15, 0], [12, 0], [10, 0]],
                        "2010": [[15, 0], [12, 0], [10, 0],
                                 [15, 0], [12, 0], [10, 0]],
                        "2011": [[15, 0], [12, 0], [10, 0],
                                 [15, 0], [12, 0], [10, 0]],
                        "2012": [[15, 0], [12, 0], [10, 0],
                                 [15, 0], [12, 0], [10, 0]],
                        "2013": [[15, 0], [12, 0], [10, 0],
                                 [15, 0], [12, 0], [10, 0]]}
                },
                "performance units": "kWh/cycle"
            }},
         "lifetime": {
            "average": {"2009": 12.8, "2010": 12.8, "2011": 12.8, "2012": 12.8,
                        "2013": 12.8},
            "range": {"2009": 3.9, "2010": 3.9, "2011": 3.9, "2012": 3.9,
                      "2013": 3.9},
            "units": "years",
            "source": "EIA AEO"},
         "consumer choice": {
            "competed market share": {
                "model type": "logistic regression",
                "parameters": {
                    "typical": {
                        "b1": {"2009": 4, "2010": 4, "2011": 4,
                               "2012": 4, "2013": 4},
                        "b2": {"2009": 5, "2010": 5, "2011": 5,
                               "2012": 5, "2013": 5}},
                    "best": {
                        "b1": {"2009": 4, "2010": 4, "2011": 4,
                               "2012": 4, "2013": 4},
                        "b2": {"2009": 5, "2010": 5, "2011": 5,
                               "2012": 5, "2013": 5}}},
                "source": "EIA AEO"}}},
        {"performance": {
            "typical": {"2009": 29, "2010": 29, "2011": 29, "2012": 32,
                        "2013": 32},
            "best": {"2009": 31, "2010": 31, "2011": 31, "2012": 33,
                     "2013": 33},
            "units": "TEff",
            "source": "EIA AEO"},
         "installed cost": {
            "before incentives": {
                "typical": {
                    "new": {"2009": 150, "2010": 150, "2011": 150, "2012": 160,
                            "2013": 160},
                    "existing": {
                        "2009": 150, "2010": 150, "2011": 150, "2012": 160,
                        "2013": 160}},
                "best": {
                    "new": {"2009": 200, "2010": 200, "2011": 200, "2012": 170,
                            "2013": 170},
                    "existing": {
                        "2009": 200, "2010": 200, "2011": 200, "2012": 170,
                        "2013": 170}},
                "units": "2022$/unit",
                "source": "EIA AEO"},
            "incentives": {
                "by performance tier": {
                    "new": {
                        "2009": [[29, 0], [31, 0]],
                        "2010": [[29, 0], [31, 0]],
                        "2011": [[29, 0], [31, 0]],
                        "2012": [[32, 0], [33, 0]],
                        "2013": [[32, 0], [33, 0]]},
                    "existing": {
                        "2009": [[29, 0], [31, 0]],
                        "2010": [[29, 0], [31, 0]],
                        "2011": [[29, 0], [31, 0]],
                        "2012": [[32, 0], [33, 0]],
                        "2013": [[32, 0], [33, 0]]}
                },
                "performance units": "TEff"
            }},
         "lifetime": {
            "average": {"2009": 21.45, "2010": 21.45, "2011": 21.45,
                        "2012": 21.45, "2013": 21.45},
            "range": {"2009": 3.55, "2010": 3.55, "2011": 3.55, "2012": 3.55,
                      "2013": 3.55},
            "units": "years",
            "source": "EIA AEO"},
         "consumer choice": {
            "competed market share": {
                "model type": "logistic regression",
                "parameters": {
                    "typical": {
                        "b1": {"2009": 6, "2010": 6, "2011": 6,
                               "2012": 6, "2013": 6},
                        "b2": {"2009": 7, "2010": 7, "2011": 7,
                               "2012": 7, "2013": 7}},
                    "best": {
                        "b1": {"2009": 6, "2010": 6, "2011": 6,
                               "2012": 6, "2013": 6},
                        "b2": {"2009": 7, "2010": 7, "2011": 7,
                               "2012": 7, "2013": 7}}},
                "source": "EIA AEO"}}},
        {"performance": {
            "typical": {"2009": 129, "2010": 129, "2011": 129, "2012": 132,
                        "2013": 132},
            "best": {"2009": 131, "2010": 131, "2011": 131, "2012": 133,
                     "2013": 133},
            "units": "CEF",
            "source": "EIA AEO"},
         "installed cost": {
            "before incentives": {
                "typical": {
                    "new": {"2009": 1510, "2010": 1510, "2011": 1510,
                            "2012": 1610, "2013": 1610},
                    "existing": {
                        "2009": 1510, "2010": 1510, "2011": 1510, "2012": 1610,
                        "2013": 1610}},
                "best": {
                    "new": {"2009": 2010, "2010": 2010, "2011": 2010,
                            "2012": 1710, "2013": 1710},
                    "existing": {
                        "2009": 2010, "2010": 2010, "2011": 2010, "2012": 1710,
                        "2013": 1710}},
                "units": "2022$/unit",
                "source": "EIA AEO"},
            "incentives": {
                "by performance tier": {
                    "new": {
                        "2009": [[129, 0], [131, 0]],
                        "2010": [[129, 0], [131, 0]],
                        "2011": [[129, 0], [131, 0]],
                        "2012": [[132, 0], [133, 0]],
                        "2013": [[132, 0], [133, 0]]},
                    "existing": {
                        "2009": [[129, 0], [131, 0]],
                        "2010": [[129, 0], [131, 0]],
                        "2011": [[129, 0], [131, 0]],
                        "2012": [[132, 0], [133, 0]],
                        "2013": [[132, 0], [133, 0]]}
                },
                "performance units": "CEF"
            }},
         "lifetime": {
            "average": {"2009": 13.5, "2010": 13.5, "2011": 13.5, "2012": 13.5,
                        "2013": 13.5},
            "range": {"2009": 3.5, "2010": 3.5, "2011": 3.5, "2012": 3.5,
                      "2013": 3.5},
            "units": "years",
            "source": "EIA AEO"},
         "consumer choice": {
            "competed market share": {
                "model type": "logistic regression",
                "parameters": {
                    "typical": {
                        "b1": {"2009": 0, "2010": 0, "2011": 0,
                               "2012": 0, "2013": 0},
                        "b2": {"2009": 1, "2010": 1, "2011": 1,
                               "2012": 1, "2013": 1}},
                    "best": {
                        "b1": {"2009": 0, "2010": 0, "2011": 0,
                               "2012": 0, "2013": 0},
                        "b2": {"2009": 1, "2010": 1, "2011": 1,
                               "2012": 1, "2013": 1}}},
                "source": "EIA AEO"}}},
        {"performance": {
            "typical": {"2009": 2.9, "2010": 2.9, "2011": 2.9, "2012": 2.9,
                        "2013": 2.9},
            "best": {"2009": 3.5, "2010": 3.5, "2011": 3.5, "2012": 3.5,
                     "2013": 3.5},
            "units": "UEF",
            "source": "EIA AEO"},
         "installed cost": {
            "before incentives": {
                "typical": {
                    "new": {
                        "2009": 1300, "2010": 1300, "2011": 1300, "2012": 1300,
                        "2013": 1300},
                    "existing": {
                        "2009": 1300, "2010": 1300, "2011": 1300, "2012": 1300,
                        "2013": 1300}},
                "best": {
                    "new": {
                        "2009": 1500, "2010": 1500, "2011": 1500, "2012": 1500,
                        "2013": 1500},
                    "existing": {
                        "2009": 1500, "2010": 1500, "2011": 1500, "2012": 1500,
                        "2013": 1500}},
                "units": "2022$/unit",
                "source": "EIA AEO"},
            "incentives": {
                "by performance tier": {
                    "new": {
                        "2009": [[2.9, 0], [3.2, 0], [3.5, 0]],
                        "2010": [[2.9, 0], [3.2, 0], [3.5, 0]],
                        "2011": [[2.9, 0], [3.2, 0], [3.5, 0]],
                        "2012": [[2.9, 0], [3.2, 0], [3.5, 0]],
                        "2013": [[2.9, 0], [3.2, 0], [3.5, 0]]},
                    "existing": {
                        "2009": [[2.9, 0], [3.2, 0], [3.5, 0]],
                        "2010": [[2.9, 0], [3.2, 0], [3.5, 0]],
                        "2011": [[2.9, 0], [3.2, 0], [3.5, 0]],
                        "2012": [[2.9, 0], [3.2, 0], [3.5, 0]],
                        "2013": [[2.9, 0], [3.2, 0], [3.5, 0]]}
                },
                "performance units": "UEF"
            }},
         "lifetime": {
            "average": {"2009": 11.75, "2010": 11.75, "2011": 11.75,
                        "2012": 11.75, "2013": 11.75},
            "range": {"2009": 3.25, "2010": 3.25, "2011": 3.25, "2012": 3.25,
                      "2013": 3.25},
            "units": "years",
            "source": "EIA AEO"},
         "consumer choice": {
            "competed market share": {
                "model type": "logistic regression",
                "parameters": {
                    "typical": {
                        "b1": {"2009": 7, "2010": 7, "2011": 7,
                               "2012": 7, "2013": 7},
                        "b2": {"2009": 8, "2010": 8, "2011": 8,
                               "2012": 8, "2013": 8}},
                    "best": {
                        "b1": {"2009": 7, "2010": 7, "2011": 7,
                               "2012": 7, "2013": 7},
                        "b2": {"2009": 8, "2010": 8, "2011": 8,
                               "2012": 8, "2013": 8}}},
                "source": "EIA AEO"}}},
        {"performance": {
            "typical": {"2009": 1.13, "2010": 1.55, "2011": 1.55, "2012": 2.78,
                        "2013": 2.78},
            "best": 0,
            "units": "lm/W",
            "source": "EIA AEO"},
         "installed cost": {
            "before incentives": {
                "typical": {
                    "2009": 65, "2010": 63.2, "2011": 63.2, "2012": 90.3,
                    "2013": 90.3},
                "best": 0,
                "units": "2022$/unit",
                "source": "EIA AEO"},
            "incentives": {
                "by performance tier": {
                    "2009": [[1.13, 0]],
                    "2010": [[1.55, 0]],
                    "2011": [[1.55, 0]],
                    "2012": [[2.78, 0]],
                    "2013": [[2.78, 0]]
                },
                "performance units": "lm/W"}},
         "lifetime": {
            "average": {"2009": 3.42, "2010": 4.22, "2011": 4.22, "2012": 4.79,
                        "2013": 4.79},
            "range": 0,
            "units": "years",
            "source": "EIA AEO"},
         "consumer choice": {
            "competed market share": {
                "model type": "logistic regression",
                "parameters": {
                    "typical": {
                        "b1": {"2009": -0.95, "2010": -0.95, "2011": -0.95,
                               "2012": -0.95, "2013": -0.95},
                        "b2": {"2009": -0.1, "2010": -0.1, "2011": -0.1,
                               "2012": -0.1, "2013": -0.1}},
                    "best": {
                        "b1": {"2009": -0.95, "2010": -0.95, "2011": -0.95,
                               "2012": -0.95, "2013": -0.95},
                        "b2": {"2009": -0.1, "2010": -0.1, "2011": -0.1,
                               "2012": -0.1, "2013": -0.1}}},
                "source": "EIA AEO"}}},
        0,
        0,
        {"performance": {
            "typical": {"2009": 2.95, "2010": 2.95, "2011": 3.15, "2012": 3.15,
                        "2013": 3.15},
            "best": {"2009": 2.95, "2010": 2.95, "2011": 3.15, "2012": 3.15,
                     "2013": 3.15},
            "units": "COP",
            "source": "EIA AEO"},
         "installed cost": {
            "before incentives": {
                "typical": {
                    "new": {"2009": 550, "2010": 550, "2011": 575, "2012": 575,
                            "2013": 575},
                    "existing": {
                        "2009": 550, "2010": 550, "2011": 575, "2012": 575,
                        "2013": 575}},
                "best": {
                    "new": {"2009": 550, "2010": 550, "2011": 575, "2012": 575,
                            "2013": 575},
                    "existing": {
                        "2009": 550, "2010": 550, "2011": 575, "2012": 575,
                        "2013": 575}},
                "units": "2022$/unit",
                "source":  (
                    "EIA AEO (NOTE EIA convention of dividing HP costs "
                    "for existing buildings by 2 while putting all HP costs "
                    "for new construction under the heating end use)")},
            "incentives": {
                "by performance tier": {
                    "new": {
                        "2009": [[2.95, 0]],
                        "2010": [[2.95, 0]],
                        "2011": [[3.15, 0]],
                        "2012": [[3.15, 0]],
                        "2013": [[3.15, 0]]},
                    "existing": {
                        "2009": [[2.95, 0]],
                        "2010": [[2.95, 0]],
                        "2011": [[3.15, 0]],
                        "2012": [[3.15, 0]],
                        "2013": [[3.15, 0]]}
                },
                "performance units": "COP"
            }},
         "lifetime": {
            "average": {"2009": 6, "2010": 6, "2011": 6, "2012": 6,
                        "2013": 6},
            "range": {"2009": 4, "2010": 4, "2011": 4, "2012": 4,
                      "2013": 4},
            "units": "years",
            "source": "EIA AEO"},
         "consumer choice": {
            "competed market share": {
                "model type": "logistic regression",
                "parameters": {
                    "typical": {
                        "b1": {"2009": 6, "2010": 6, "2011": 6,
                               "2012": 6, "2013": 6},
                        "b2": {"2009": 6, "2010": 6, "2011": 6,
                               "2012": 6, "2013": 6}},
                    "best": {
                        "b1": {"2009": 6, "2010": 6, "2011": 6,
                               "2012": 6, "2013": 6},
                        "b2": {"2009": 6, "2010": 6, "2011": 6,
                               "2012": 6, "2013": 6}}},
                "source": "EIA AEO"}}},
        {"performance": {
            "typical": {"2009": 2.95, "2010": 2.95, "2011": 3.15, "2012": 3.15,
                        "2013": 3.15},
            "best": {"2009": 2.95, "2010": 2.95, "2011": 3.15, "2012": 3.15,
                     "2013": 3.15},
            "units": "COP",
            "source": "EIA AEO"},
         "installed cost": {
            "before incentives": {
                "typical": {
                    "new": {"2009": 550, "2010": 550, "2011": 575, "2012": 575,
                            "2013": 575},
                    "existing": {
                        "2009": 550, "2010": 550, "2011": 575, "2012": 575,
                        "2013": 575}},
                "best": {
                    "new": {"2009": 550, "2010": 550, "2011": 575, "2012": 575,
                            "2013": 575},
                    "existing": {
                        "2009": 550, "2010": 550, "2011": 575, "2012": 575,
                        "2013": 575}},
                "units": "2022$/unit",
                "source": (
                    "EIA AEO (NOTE EIA convention of dividing HP costs "
                    "for existing buildings by 2 while putting all HP costs "
                    "for new construction under the heating end use)")},
            "incentives": {
                "by performance tier": {
                    "new": {
                        "2009": [[2.95, 0], [2.95, 0]],
                        "2010": [[2.95, 0], [2.95, 0]],
                        "2011": [[3.15, 0], [3.15, 0]],
                        "2012": [[3.15, 0], [3.15, 0]],
                        "2013": [[3.15, 0], [3.15, 0]]},
                    "existing": {
                        "2009": [[2.95, 0], [2.95, 0]],
                        "2010": [[2.95, 0], [2.95, 0]],
                        "2011": [[3.15, 0], [3.15, 0]],
                        "2012": [[3.15, 0], [3.15, 0]],
                        "2013": [[3.15, 0], [3.15, 0]]}
                },
                "performance units": "COP"
            }},
         "lifetime": {
            "average": {"2009": 6, "2010": 6, "2011": 6, "2012": 6,
                        "2013": 6},
            "range": {"2009": 4, "2010": 4, "2011": 4, "2012": 4,
                      "2013": 4},
            "units": "years",
            "source": "EIA AEO"},
         "consumer choice": {
            "competed market share": {
                "model type": "logistic regression",
                "parameters": {
                    "typical": {
                        "b1": {"2009": 6, "2010": 6, "2011": 6,
                               "2012": 6, "2013": 6},
                        "b2": {"2009": 6, "2010": 6, "2011": 6,
                               "2012": 6, "2013": 6}},
                    "best": {
                        "b1": {"2009": 6, "2010": 6, "2011": 6,
                               "2012": 6, "2013": 6},
                        "b2": {"2009": 6, "2010": 6, "2011": 6,
                               "2012": 6, "2013": 6}}},
                "source": "EIA AEO"}}},
        {"performance": {
            "typical": {"2009": 2.95, "2010": 2.95, "2011": 3.15, "2012": 3.15,
                        "2013": 3.15},
            "best": {"2009": 2.95, "2010": 2.95, "2011": 3.15, "2012": 3.15,
                     "2013": 3.15},
            "units": "EER",
            "source": "EIA AEO"},
         "installed cost": {
            "before incentives": {
                "typical": {
                    "new": {"2009": 550, "2010": 550, "2011": 575, "2012": 575,
                            "2013": 575},
                    "existing": {
                        "2009": 550, "2010": 550, "2011": 575, "2012": 575,
                        "2013": 575}},
                "best": {
                    "new": {"2009": 550, "2010": 550, "2011": 575, "2012": 575,
                            "2013": 575},
                    "existing": {
                        "2009": 550, "2010": 550, "2011": 575, "2012": 575,
                        "2013": 575}},
                "units": "2022$/unit",
                "source": (
                    "EIA AEO (NOTE EIA convention of dividing HP costs "
                    "for existing buildings by 2 while putting all HP costs "
                    "for new construction under the heating end use)")},
            "incentives": {
                "by performance tier": {
                    "new": {
                        "2009": [[2.95, 0], [2.95, 0]],
                        "2010": [[2.95, 0], [2.95, 0]],
                        "2011": [[3.15, 0], [3.15, 0]],
                        "2012": [[3.15, 0], [3.15, 0]],
                        "2013": [[3.15, 0], [3.15, 0]]},
                    "existing": {
                        "2009": [[2.95, 0], [2.95, 0]],
                        "2010": [[2.95, 0], [2.95, 0]],
                        "2011": [[3.15, 0], [3.15, 0]],
                        "2012": [[3.15, 0], [3.15, 0]],
                        "2013": [[3.15, 0], [3.15, 0]]}
                },
                "performance units": "EER"
            }},
         "lifetime": {
            "average": {"2009": 6, "2010": 6, "2011": 6, "2012": 6,
                        "2013": 6},
            "range": {"2009": 4, "2010": 4, "2011": 4, "2012": 4,
                      "2013": 4},
            "units": "years",
            "source": "EIA AEO"},
         "consumer choice": {
            "competed market share": {
                "model type": "logistic regression",
                "parameters": {
                    "typical": {
                        "b1": {"2009": 6, "2010": 6, "2011": 6,
                               "2012": 6, "2013": 6},
                        "b2": {"2009": 6, "2010": 6, "2011": 6,
                               "2012": 6, "2013": 6}},
                    "best": {
                        "b1": {"2009": 6, "2010": 6, "2011": 6,
                               "2012": 6, "2013": 6},
                        "b2": {"2009": 6, "2010": 6, "2011": 6,
                               "2012": 6, "2013": 6}}},
                "source": "EIA AEO"}}},
        {"performance": {
            "typical": {"2009": 2.95, "2010": 2.95, "2011": 3.15, "2012": 3.15,
                        "2013": 3.15},
            "best": {"2009": 2.95, "2010": 2.95, "2011": 3.15, "2012": 3.15,
                     "2013": 3.15},
            "units": "AFUE",
            "source": "EIA AEO"},
         "installed cost": {
            "before incentives": {
                "typical": {
                    "new": {"2009": 550, "2010": 550, "2011": 575, "2012": 575,
                            "2013": 575},
                    "existing": {
                        "2009": 550, "2010": 550, "2011": 575, "2012": 575,
                        "2013": 575}},
                "best": {
                    "new": {"2009": 550, "2010": 550, "2011": 575, "2012": 575,
                            "2013": 575},
                    "existing": {
                        "2009": 550, "2010": 550, "2011": 575, "2012": 575,
                        "2013": 575}},
                "units": "2022$/unit",
                "source": "EIA AEO"},
            "incentives": {
                "by performance tier": {
                    "new": {
                        "2009": [[2.95, 0], [2.95, 0]],
                        "2010": [[2.95, 0], [2.95, 0]],
                        "2011": [[3.15, 0], [3.15, 0]],
                        "2012": [[3.15, 0], [3.15, 0]],
                        "2013": [[3.15, 0], [3.15, 0]]},
                    "existing": {
                        "2009": [[2.95, 0], [2.95, 0]],
                        "2010": [[2.95, 0], [2.95, 0]],
                        "2011": [[3.15, 0], [3.15, 0]],
                        "2012": [[3.15, 0], [3.15, 0]],
                        "2013": [[3.15, 0], [3.15, 0]]}
                },
                "performance units": "AFUE"
            }},
         "lifetime": {
            "average": {"2009": 6, "2010": 6, "2011": 6, "2012": 6,
                        "2013": 6},
            "range": {"2009": 4, "2010": 4, "2011": 4, "2012": 4,
                      "2013": 4},
            "units": "years",
            "source": "EIA AEO"},
         "consumer choice": {
            "competed market share": {
                "model type": "logistic regression",
                "parameters": {
                    "typical": {
                        "b1": {"2009": 6, "2010": 6, "2011": 6,
                               "2012": 6, "2013": 6},
                        "b2": {"2009": 6, "2010": 6, "2011": 6,
                               "2012": 6, "2013": 6}},
                    "best": {
                        "b1": {"2009": 6, "2010": 6, "2011": 6,
                               "2012": 6, "2013": 6},
                        "b2": {"2009": 6, "2010": 6, "2011": 6,
                               "2012": 6, "2013": 6}}},
                "source": "EIA AEO"}}}]

    # Test that the walk_techdata function yields a correct output dict
    # given the valid key chain input along with the other sample inputs
    # defined above
    def test_listgen_ok(self):
        for (idx, tk) in enumerate(self.tech_ok_keys):
            dict1 = mseg_techdata.list_generator_techdata(
                self.eia_nlt_cp, self.eia_nlt_l, self.eia_lt,
                mseg_techdata.tech_eia_nonlt, mseg_techdata.tech_eia_lt,
                self.tech_non_eia, tk, self.project_dict)
            dict2 = self.ok_datadict_out[idx]
            if isinstance(dict2, dict):
                self.dict_check(dict1, dict2)
            else:
                self.assertEqual(dict1, dict2)


class FillYrsTest(unittest.TestCase, CommonMethods):
    """ Test that both the fill_years_nlt and fill_years_lt functions yield
    the correct non-lighting and lighting tech. cost, performance, lifetime,
    and consumer choice info. given an input array with these data broken out
    across various time periods. * Note: only the fill_years_nlt function
    accesses consumer choice info. as this is not broken out by census divison,
    building type, or year for lighting technologies; moreover, only the
    fill_years_lt function accesses lifetime info. as lifetime is not broken
    out by year for non-lighting technologies """

    # Define a list of test input arrays with valid EIA data on the cost,
    # performance, and consumer choice parameters for non-lighting technologies
    # to be stitched together into a list of cost, performance, and choice
    # output dicts that each cover the modeling time horizon. * Note: the
    # second element in this list tests the special case of a freezer
    # technology, which has data on multiple configurations that must be
    # consolidated into a single "average" configuration for proper handling
    # by the stitch function.
    in_nonlt = [numpy.array(
        [(2005, 2010, 2.5, 1000, 1000, 0, 0, 0, 0, 1, 2,
         b"ELEC_HP1"),
         (2010, 2011, 2.65, 1200, 1200, 0, 0, 0, 0, 3, 4,
         b"ELEC_HP1"),
         (2011, 2012, 3.1, 1250, 1250, 0, 0, 0, 0, 4.4, 5.5,
         b"ELEC_HP1"),
         (2012, 2014, 4.5, 1450, 1450, 99, 0, 1, 1, 6.7, 8,
         b"ELEC_HP1"),
         (2014, 2040, 5, 2000, 2000, 0, 0, 0, 0, 9, 9.1,
         b"ELEC_HP1")], dtype=[
            ("START_EQUIP_YR", "<i8"),
            ("END_EQUIP_YR", "<f8"),
            ("BASE_EFF", "<f8"),
            ("INST_COST", "<f8"),
            ("RETAIL_COST", "<f8"),
            ("FD_REPL_SUB", "<f8"),
            ("FD_NEW_SUB", "<f8"),
            ("NF_REPL_SUB", "<f8"),
            ("NF_NEW_SUB", "<f8"),
            ("EFF_CHOICE_P1", "<f8"),
            ("EFF_CHOICE_P2", "<f8"),
            ("NAME", "S10")]), numpy.array(
            [(2005, 2010, 2.5, 1000, 1000, 0, 0, 0, 0, 10.1, 11, b"FrzrC#1"),
             (2010, 2011, 2.65, 1200, 1200, 0, 99, 0, 1, 12, 13.2, b"FrzrC#1"),
             (2011, 2012, 3.1, 1250, 1250, 0, 0, 0, 0, 14, 14.5, b"FrzrC#1"),
             (2012, 2014, 4.5, 1450, 1450, 0, 0, 0, 0, 15, 16, b"FrzrC#1"),
             (2014, 2040, 5, 2000, 2000, 0, 0, 0, 0, 17, 18.4, b"FrzrC#1"),
             (2005, 2010, 3, 2000, 2000, 0, 0, 0, 0, 19.1, 20, b"FrzrU#1"),
             (2010, 2011, 3.1, 1500, 1500, 0, 0, 0, 0, 21, 22, b"FrzrU#1"),
             (2011, 2012, 3.7, 1500, 1500, 0, 0, 0, 0, 23.6, 23.7, b"FrzrU#1"),
             (2012, 2014, 3.7, 1600, 1600, 0, 0, 0, 0, 24, 25, b"FrzrU#1"),
             (2014, 2040, 6, 1900, 1900, 0, 0, 0, 0,  25.6, 25.7, b"FrzrU#1")],
            dtype=[
                ("START_EQUIP_YR", "<i8"),
                ("END_EQUIP_YR", "<f8"),
                ("BASE_EFF", "<f8"),
                ("INST_COST", "<f8"),
                ("RETAIL_COST", "<f8"),
                ("FD_REPL_SUB", "<f8"),
                ("FD_NEW_SUB", "<f8"),
                ("NF_REPL_SUB", "<f8"),
                ("NF_NEW_SUB", "<f8"),
                ("EFF_CHOICE_P1", "<f8"),
                ("EFF_CHOICE_P2", "<f8"),
                ("NAME", "S10")])]

    # Define a test input array with valid EIA data on the cost, performance,
    # and lifetime of lighting technologies to be stitched together into
    # a list of cost, performance, and lifetime output dicts that each covers
    # the modeling time horizon
    in_lt = numpy.array([(2008, 2012, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                          0.33, 10000, 55, b"GSL", b"Inc", -0.95, -0.1),
                         (2012, 2013, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.03, 20000,
                          60, b"GSL", b"Inc", -0.95, -0.1),
                         (2013, 2017, 0, 999, 0, 0, 1, 0, 0, 0, 0, 1.53, 35000,
                          61.2, b"GSL", b"Inc", -0.95, -0.1),
                         (2017, 2020, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2.75, 40000,
                          80.3, b"GSL", b"Inc", -0.95, -0.1),
                         (2020, 2040, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3.45, 50000,
                          90, b"GSL", b"Inc", -0.95, -0.1)],
                        dtype=[("START_EQUIP_YR", "<i8"),
                               ("END_EQUIP_YR", "<f8"),
                               ("EE_Sub1", "<f8"),
                               ("EE_Sub2", "<f8"),
                               ("EE_Sub3", "<f8"),
                               ("EE_Sub4", "<f8"),
                               ("EE_Sub5", "<f8"),
                               ("EE_Sub6", "<f8"),
                               ("EE_Sub7", "<f8"),
                               ("EE_Sub8", "<f8"),
                               ("EE_Sub9", "<f8"),
                               ("BASE_EFF", "<f8"),
                               ("LIFE_HRS", "<f8"),
                               ("INST_COST", "<f8"),
                               ("NAME", "S3"),
                               ("BULB_TYPE", "S3"),
                               ("Beta_1", "<f8"),
                               ("Beta_2", "<f8")])

    # Define a test input array with faulty EIA data that should yield an
    # error in the fill_years_nlt and fill_years_lt function executions
    # when paired with the tech_fail_keys below (multiple rows with same
    # starting year and not a special technology case (refrigerators, freezers)
    # or refrigerator/freezer case with inconsistent year bins
    in_fail = [numpy.array([
        (2005, 2010, 2.5, 1000, 1000, 0, 0, 0, 0, b"Fail_Test1"),
        (2010, 2011, 2.65, 1200, 1200, 0, 0, 0, 0, b"Fail_Test1"),
        (2011, 2012, 3.1, 1250, 1250, 0, 0, 0, 0,  b"Fail_Test1"),
        (2012, 2014, 4.5, 1450, 1450, 0, 0, 0, 0,  b"Fail_Test1"),
        (2014, 2040, 5, 2000, 2000, 0, 0, 0, 0,  b"Fail_Test1"),
        (2005, 2010, 3, 2000, 2000, 0, 0, 0, 0,  b"Fail_Test1"),
        (2010, 2011, 3.1, 1500, 1500, 0, 0, 0, 0,  b"Fail_Test1"),
        (2011, 2012, 3.7, 1500, 1500, 0, 0, 0, 0,  b"Fail_Test1"),
        (2012, 2014, 3.7, 1600, 1600, 0, 0, 0, 0,  b"Fail_Test1"),
        (2014, 2040, 6, 1900, 1900, 0, 0, 0, 0,  b"Fail_Test1")],
                           dtype=[("START_EQUIP_YR", "<i8"),
                                  ("END_EQUIP_YR", "<f8"),
                                  ("BASE_EFF", "<f8"),
                                  ("INST_COST", "<f8"),
                                  ("RETAIL_COST", "<f8"),
                                  ("FD_REPL_SUB", "<f8"),
                                  ("FD_NEW_SUB", "<f8"),
                                  ("NF_REPL_SUB", "<f8"),
                                  ("NF_NEW_SUB", "<f8"),
                                  ("NAME", "S10")]),
               numpy.array([(2009, 2013, 1, 500, 500,  0, 0, 0, 0, b"FrzrU#1"),
                            (2013, 2040, 2, 500, 500,  0, 0, 0, 0, b"FrzrU#1"),
                            (2009, 2011, 1, 500, 500,  0, 0, 0, 0, b"FrzrC#1"),
                            (2011, 2013, 1, 500, 500,  0, 0, 0, 0, b"FrzrC#1"),
                            (2013, 2040, 2, 600, 600,  0, 0, 0, 0, b"FrzrC#1")
                            ],
                           dtype=[("START_EQUIP_YR", "<i8"),
                                  ("END_EQUIP_YR", "<f8"),
                                  ("BASE_EFF", "<f8"),
                                  ("INST_COST", "<f8"),
                                  ("RETAIL_COST", "<f8"),
                                  ("FD_REPL_SUB", "<f8"),
                                  ("FD_NEW_SUB", "<f8"),
                                  ("NF_REPL_SUB", "<f8"),
                                  ("NF_NEW_SUB", "<f8"),
                                  ("NAME", "S10")])]

    # Define a sample list of the technology-level keys that are defined while
    # running through the microsegments JSON structure; these keys are used to
    # flag non-lighting technologies that require special handling to update
    # with EIA data because of their unique definitions in these data
    # (i.e. refrigerators, freezers)
    tech_ok_key = ["ASHP", "freezers"]

    # Define a sample list of dictionary keys as above that should cause the
    # fill_years_nonlt function to fail when paired with an input array that
    # includes multiple rows with the same "START_EQUIP_YR" value (this is
    # only allowed when "refrigerators" or "freezers" is in the key list)
    tech_fail_keys = ["ASHP", "freezers"]

    # Define the modeling time horizon to test (2009:2015)
    years = [str(i) for i in range(2009, 2015 + 1)]
    project_dict = dict.fromkeys(years)

    # Define output dicts that should be generated by the
    # fill_years_nlt functions for each year of the modeling time horizon
    # based on the in_nonlt array input above
    out_nonlt_typ_best = [
        [{"2009": 2.65, "2010": 2.65, "2011": 3.1, "2012": 4.5,
          "2013": 4.5, "2014": 5, "2015": 5},
         {"new": {
            "2009": 1200, "2010": 1200, "2011": 1250, "2012": 1450,
            "2013": 1450, "2014": 2000, "2015": 2000},
          "existing": {
            "2009": 1200, "2010": 1200, "2011": 1250, "2012": 1450,
            "2013": 1450, "2014": 2000, "2015": 2000}},  # cost
         {"2009": 3, "2010": 3, "2011": 4.4, "2012": 6.7,
          "2013": 6.7, "2014": 9, "2015": 9},
         {"2009": 4, "2010": 4, "2011": 5.5, "2012": 8,
          "2013": 8, "2014": 9.1, "2015": 9.1}], [
         {"2009": 2.88, "2010": 2.88, "2011": 3.4, "2012": 4.1,
          "2013": 4.1, "2014": 5.5, "2015": 5.5},
         {"new": {
            "2009": 1350, "2010": 1350, "2011": 1375, "2012": 1525,
            "2013": 1525, "2014": 1950, "2015": 1950},
          "existing": {
            "2009": 1350, "2010": 1350, "2011": 1375, "2012": 1525,
            "2013": 1525, "2014": 1950, "2015": 1950}},  # cost
         {"2009": 16.5, "2010": 16.5, "2011": 18.8, "2012": 19.5,
          "2013": 19.5, "2014": 21.3, "2015": 21.3},
         {"2009": 17.6, "2010": 17.6, "2011": 19.1, "2012": 20.5,
          "2013": 20.5, "2014": 22.05, "2015": 22.05}]]
    out_nonlt_incent = [
        {"new": {
            "2009": [[2.65, 0]], "2010": [[2.65, 0]],
            "2011": [[3.1, 0]], "2012": [[4.5, 1]],
            "2013": [[4.5, 1]], "2014": [[5, 0]], "2015": [[5, 0]]},
         "existing": {
            "2009": [[2.65, 0]], "2010": [[2.65, 0]],
            "2011": [[3.1, 0]], "2012": [[4.5, 100]],
            "2013": [[4.5, 100]], "2014": [[5, 0]], "2015": [[5, 0]]}},
        {"new": {
            "2009": [[2.65, 100], [3.1, 0]], "2010": [[2.65, 100], [3.1, 0]],
            "2011": [[3.1, 0], [3.7, 0]], "2012": [[4.5, 0], [3.7, 0]],
            "2013": [[4.5, 0], [3.7, 0]], "2014": [[5, 0], [6, 0]],
            "2015": [[5, 0], [6, 0]]},
         "existing": {
            "2009": [[2.65, 0], [3.1, 0]], "2010": [[2.65, 0], [3.1, 0]],
            "2011": [[3.1, 0], [3.7, 0]], "2012": [[4.5, 0], [3.7, 0]],
            "2013": [[4.5, 0], [3.7, 0]], "2014": [[5, 0], [6, 0]],
            "2015": [[5, 0], [6, 0]]}}]

    # Define output dicts that should be generated by the
    # fill_years_lt functions for each year of the modeling time horizon
    # based on the in_lt array input above
    out_lt_typ_best = [
        {"2009": 0.33, "2010": 0.33, "2011": 0.33, "2012": 1.03,
         "2013": 1.53, "2014": 1.53, "2015": 1.53},
        {"2009": 55, "2010": 55, "2011": 55, "2012": 60,
         "2013": 61.2, "2014": 61.2, "2015": 61.2},
        {"2009": 1.14, "2010": 1.14, "2011": 1.14, "2012": 2.28,
         "2013": 4.00, "2014": 4.00, "2015": 4.00},
        {"2009": -0.95, "2010": -0.95, "2011": -0.95, "2012": -0.95,
         "2013": -0.95, "2014": -0.95, "2015": -0.95},
        {"2009": -0.1, "2010": -0.1, "2011": -0.1, "2012": -0.1,
         "2013": -0.1, "2014": -0.1, "2015": -0.1}]
    out_lt_incent = {
        "2009": [[0.33, 0]], "2010": [[0.33, 0]], "2011": [[0.33, 0]],
        "2012": [[1.03, 0]], "2013": [[1.53, 1000]], "2014": [[1.53, 1000]],
        "2015": [[1.53, 1000]]}

    # Test that the fill_years_nlt function yields a correct output list
    # given the in_nlt numpy array, modeling time horizon, and tech_ok_keys
    # inputs defined above, for a typical/best cost/perf/life/consumer
    # choice data pull
    def test_fill_nlt_typ_best(self):
        for (idx, tk) in enumerate(self.tech_ok_key):
            list1 = mseg_techdata.fill_years_nlt_typ_best(
                self.in_nonlt[idx], self.project_dict, tk)
            list2 = self.out_nonlt_typ_best[idx]
            # Check that the list lengths are equal
            self.assertEqual(len(list1), len(list2))
            # Check that the list values are equal
            for (el1, el2) in zip(list1, list2):
                dict1 = el1
                dict2 = el2
                self.dict_check(dict1, dict2)

    # Test that the fill_years_nlt function yields a correct output list
    # given the in_nlt numpy array, modeling time horizon, and tech_ok_keys
    # inputs defined above, for an incentives data pull
    def test_fill_nlt_incent(self):
        for (idx, tk) in enumerate(self.tech_ok_key):
            dict1 = mseg_techdata.fill_years_nlt_incent(
                self.in_nonlt[idx], self.project_dict, tk)
            dict2 = self.out_nonlt_incent[idx]
            self.dict_check(dict1, dict2)

    # Test that the fill_years_lt function yields a correct output list given
    # the in_lt numpy array and modeling time horizon inputs defined above,
    # for a typical/best cost/perf/life/consumer choice data pull
    def test_fill_lt_typ_best(self):
        list1 = mseg_techdata.fill_years_lt_typ_best(
            self.in_lt, self.project_dict)
        list2 = self.out_lt_typ_best
        # Check that the list lengths are equal
        self.assertEqual(len(list1), len(list2))
        # Check that the list values are equal
        for (el1, el2) in zip(list1, list2):
            dict1 = el1
            dict2 = el2
            self.dict_check(dict1, dict2)

    # Test that the fill_years_lt function yields a correct output list given
    # the in_lt numpy array and modeling time horizon inputs defined above,
    # for an incentives data pull
    def test_fill_lt_incent(self):
        dict1 = mseg_techdata.fill_years_lt_incent(
            self.in_lt, self.project_dict)
        dict2 = self.out_lt_incent
        self.dict_check(dict1, dict2)

    # Test that both the fill_years nlt and fill_years_lt functions yield a
    # ValueError when provided a numpy array input that has multiple rows
    # with the same "START_EQUIP_YR" value or a special case with multiple
    # sub-types of a technology that have inconsistent year bins
    def test_fail(self):
        for idx, x in enumerate(self.tech_fail_keys):
            with self.assertRaises(ValueError):
                mseg_techdata.fill_years_nlt_typ_best(
                    self.in_fail[idx], self.project_dict, x)
                mseg_techdata.fill_years_lt_typ_best(
                    self.in_fail, self.project_dict)


class StitchTest(unittest.TestCase, CommonMethods):
    """ Test operation of stitch function, which reconstructs EIA performance,
    cost, lifetime, and consumer choice projections for a technology between a
    series of time periods (i.e. 2010-2014, 2014-2020, 2020-2040) in a dict
    with annual keys across a given modeling time horizon (i.e. {"2009": XXX,
    "2010": XXX, ..., "2040": XXX}) """

    # Define a test input array with valid EIA data to stitch together
    # across modeling time horizon
    ok_array = numpy.array([
        (2008, 2012, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.33, 14.5, 55,
         b"GSL", b"Inc"),
        (2012, 2013, 50, 0, 25, 0, 0, 25, 0, 0, 0, 1.03, 20, 60,
         b"GSL", b"Inc"),
        (2013, 2017, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.53, 21, 61.2,
         b"GSL", b"Inc"),
        (2017, 2020, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2.75, 22, 80.3,
         b"GSL", b"Inc"),
        (2020, 2040, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3.45, 23, 90,
         b"GSL", b"Inc")],
                           dtype=[("START_EQUIP_YR", "<i8"),
                                  ("END_EQUIP_YR", "<f8"),
                                  ("EE_Sub1", "<f8"),
                                  ("EE_Sub2", "<f8"),
                                  ("EE_Sub3", "<f8"),
                                  ("EE_Sub4", "<f8"),
                                  ("EE_Sub5", "<f8"),
                                  ("EE_Sub6", "<f8"),
                                  ("EE_Sub7", "<f8"),
                                  ("EE_Sub8", "<f8"),
                                  ("EE_Sub9", "<f8"),
                                  ("BASE_EFF", "<f8"),
                                  ("LIFE_HRS", "<f8"),
                                  ("INST_COST", "<f8"),
                                  ("NAME", "S3"),
                                  ("BULB_TYPE", "S3")])

    # Define a test input array with faulty EIA data that should yield an
    # error in the function execution (multiple rows with same starting year)
    fail_array = numpy.array([
        (2008, 2012, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.33, 14.5, 55,
         b"GSL", b"Inc"),
        (2012, 2013, 50, 0, 25, 0, 0, 25, 0, 0, 0, 1.03, 20, 60,
         b"GSL", b"Inc"),
        (2013, 2017, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.53, 21, 61.2,
         b"GSL", b"Inc"),
        (2017, 2020, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2.75, 22, 80.3,
         b"GSL", b"Inc"),
        (2020, 2040, 0, 0, 50, 0, 0, 50, 0, 0, 50, 3.45, 23, 90,
         b"GSL", b"Inc"),
        (2013, 2017, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.53, 21, 61.2,
         b"GSL", b"Inc"),
        (2017, 2020, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2.75, 22, 80.3,
         b"GSL", b"Inc"),
        (2020, 2040, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3.45, 23, 90,
         b"GSL", b"Inc")],
                             dtype=[("START_EQUIP_YR", "<i8"),
                                    ("END_EQUIP_YR", "<f8"),
                                    ("EE_Sub1", "<f8"),
                                    ("EE_Sub2", "<f8"),
                                    ("EE_Sub3", "<f8"),
                                    ("EE_Sub4", "<f8"),
                                    ("EE_Sub5", "<f8"),
                                    ("EE_Sub6", "<f8"),
                                    ("EE_Sub7", "<f8"),
                                    ("EE_Sub8", "<f8"),
                                    ("EE_Sub9", "<f8"),
                                    ("BASE_EFF", "<f8"),
                                    ("LIFE_HRS", "<f8"),
                                    ("INST_COST", "<f8"),
                                    ("NAME", "S3"),
                                    ("BULB_TYPE", "S3")])

    # Define the modeling time horizon to test (2009:2015)
    years = [str(i) for i in range(2009, 2015 + 1)]
    project_dict = dict.fromkeys(years)

    # Define the each variable (column) in the input array with the values that
    # will be reconstructed annually across the modeling time horizon, based on
    # each row"s "START_EQUIP_YR" column value
    col_names = ["BASE_EFF", "INST_COST", "LIFE_HRS"]

    # Define a dict of output values for the above variables in col_names that
    # should be generated by the function for each year of the modeling time
    # horizon based on the ok_array above
    ok_out_typ_best = [
        {"2009": 0.33, "2010": 0.33, "2011": 0.33, "2012": 1.03,
         "2013": 1.53, "2014": 1.53, "2015": 1.53},
        {"2009": 55, "2010": 55, "2011": 55, "2012": 60,
         "2013": 61.2, "2014": 61.2, "2015": 61.2},
        {"2009": 14.5, "2010": 14.5, "2011": 14.5, "2012": 20,
         "2013": 21, "2014": 21, "2015": 21}]
    ok_out_incent = {
        "2009": [0], "2010": [0], "2011": [0], "2012": [50], "2013": [0],
        "2014": [0], "2015": [0]}

    # Test that the function yields a correct output dict for each set of
    # variable values to be stitched together across the modeling time
    # horizon, given the ok_array above as an input, for cost/perf/life/choice
    # data pull
    def test_convert_match_typ_best(self):
        for (idx, col_name) in enumerate(self.col_names):
            dict1 = mseg_techdata.stitch(
                self.ok_array, self.project_dict,
                col_name, incent_flag=False)
            dict2 = self.ok_out_typ_best[idx]
            self.dict_check(dict1, dict2)

    # Test that the function yields a correct output dict for each set of
    # variable values to be stitched together across the modeling time
    # horizon, given the ok_array above as an input, for incentives data pull
    def test_convert_match_incent(self):
        dict1 = mseg_techdata.stitch(
            self.ok_array, self.project_dict, "EE_Sub1", incent_flag=True)
        dict2 = self.ok_out_incent
        self.dict_check(dict1, dict2)

    # Test that the function yields a ValueError given the fail_array above,
    # which includes multiple rows with the same "START_EQUIP_YR" column value
    def test_convert_fail(self):
        for (idx, col_name) in enumerate(self.col_names):
            with self.assertRaises(ValueError):
                mseg_techdata.stitch(self.fail_array, self.project_dict,
                                     col_name, incent_flag=False)


# Offer external code execution (include all lines below this point in all
# test files)
def main():
    # Triggers default behavior of running all test fixtures in the file
    unittest.main()


if __name__ == "__main__":
    main()
