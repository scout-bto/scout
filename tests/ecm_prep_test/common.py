#!/usr/bin/env python3

"""Common helper classes and methods for ECM preparation tests."""

# Import needed packages
import numpy
import itertools
from pathlib import Path
from scout.ecm_prep_args import ecm_args


def dict_check(dict1, dict2):
    """Check the equality of two dicts (standalone function for pytest).

    Args:
        dict1 (dict): First dictionary to be compared
        dict2 (dict): Second dictionary to be compared

    Raises:
        AssertionError: If dictionaries are not equal.
    """
    fill_val = ("substituted entry", 5.2)

    def normalize_key(key):
        """Convert numpy strings to Python strings for comparison."""
        if isinstance(key, tuple):
            return tuple(str(k) for k in key)
        return str(key)

    def keys_equal(k1, k2):
        """Check if two keys are equal, handling numpy strings."""
        # Handle case where one key is a string representation of a tuple
        # and the other is an actual tuple
        # This can happen when tuple keys are serialized/deserialized or converted via str()
        if isinstance(k1, str) and isinstance(k2, tuple):
            # Convert tuple to its string representation for comparison
            return k1 == str(k2)
        if isinstance(k1, tuple) and isinstance(k2, str):
            # Convert tuple to its string representation for comparison
            return str(k1) == k2
        # For string keys (like in 'competed choice parameters'),
        # normalize numpy string representations
        if isinstance(k1, str) and isinstance(k2, str):
            # Normalize numpy string representations like "np.str_('value')" to "'value'"
            k1_norm = k1.replace("np.str_('", "'").replace("')'", "'")
            k2_norm = k2.replace("np.str_('", "'").replace("')'", "'")
            return k1_norm == k2_norm

        # For tuple keys, handle numpy strings by converting all elements to strings
        if isinstance(k1, tuple) and isinstance(k2, tuple):
            if len(k1) != len(k2):
                return False
            # Convert each element to string for comparison to handle numpy strings
            return all(str(a) == str(b) for a, b in zip(k1, k2))
        # For other types, try direct comparison first
        try:
            return k1 == k2
        except Exception:
            # Fallback to string comparison if direct comparison fails
            return str(k1) == str(k2)

    # Sort using normalized keys for consistent ordering
    def sort_key(item):
        return normalize_key(item[0])

    for (k, i), (k2, i2) in itertools.zip_longest(
        sorted(dict1.items(), key=sort_key), sorted(dict2.items(), key=sort_key), fillvalue=fill_val
    ):
        # Check keys are equal (handling numpy strings in both tuple and string keys)
        assert keys_equal(
            k, k2
        ), f"Keys don't match: {k} (type: {type(k)}) != {k2} (type: {type(k2)})"
        if isinstance(i, dict):
            assert sorted(i.keys()) == sorted(i2.keys()), "Dict keys don't match"
            dict_check(i, i2)
        elif isinstance(i, numpy.ndarray) or isinstance(i, list):
            assert type(i) is type(i2) and len(i) == len(i2), (
                f"Types or lengths don't match: {type(i)} vs {type(i2)}, " f"{len(i)} vs {len(i2)}"
            )
            for x in range(0, len(i)):
                if isinstance(i[x], str):
                    assert (
                        i[x] == i2[x]
                    ), f"String values don't match at index {x}: {i[x]} != {i2[x]}"
                elif round(i[x], 5) != 0:
                    assert abs(i[x] - i2[x]) < 10 ** (
                        -5
                    ), f"Values don't match at index {x}: {i[x]} != {i2[x]}"
                else:
                    assert abs(i[x] - i2[x]) < 10 ** (
                        -10
                    ), f"Values don't match at index {x}: {i[x]} != {i2[x]}"
        elif isinstance(i, str):
            assert i == i2, f"String values don't match: {i} != {i2}"
        else:
            if round(i, 1) != 0:
                assert abs(i - i2) < 10 ** (-2), f"Values don't match: {i} != {i2}"
            else:
                assert abs(i - i2) < 10 ** (-10), f"Values don't match: {i} != {i2}"


class CommonMethods(object):
    """Define common methods for use in all tests below."""

    def dict_check(self, dict1, dict2):
        """Check the equality of two dicts.

        Args:
            dict1 (dict): First dictionary to be compared
            dict2 (dict): Second dictionary to be compared

        Raises:
            AssertionError: If dictionaries are not equal.
        """
        # zip() and zip_longest() produce tuples for the items
        # identified, where in the case of a dict, the first item
        # in the tuple is the key and the second item is the value;
        # in the case where the dicts are not of identical size,
        # zip_longest() will use the fill value created below as a
        # substitute in the dict that has missing content; this
        # value is given as a tuple to be of comparable structure
        # to the normal output from zip_longest()
        fill_val = ("substituted entry", 5.2)

        # In this structure, k and k2 are the keys that correspond to
        # the dicts or unitary values that are found in i and i2,
        # respectively, at the current level of the recursive
        # exploration of dict1 and dict2, respectively
        for (k, i), (k2, i2) in itertools.zip_longest(
            sorted(dict1.items()), sorted(dict2.items()), fillvalue=fill_val
        ):

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
            # At the terminal/leaf node, formatted as a numpy array or list
            # (for time sensitive valuation test cases)
            elif isinstance(i, numpy.ndarray) or isinstance(i, list):
                self.assertTrue(type(i) is type(i2) and len(i) == len(i2))
                for x in range(0, len(i)):
                    # Handle lists of strings
                    if isinstance(i[x], str):
                        self.assertEqual(i[x], i2[x])
                    # Ensure that very small numbers do not reduce to 0
                    elif round(i[x], 5) != 0:
                        self.assertAlmostEqual(i[x], i2[x], places=5)
                    else:
                        self.assertAlmostEqual(i[x], i2[x], places=10)
            elif isinstance(i, str):
                self.assertEqual(i, i2)
            # At the terminal/leaf node, formatted as a point value
            else:
                # Compare the values, allowing for floating point inaccuracy.
                # Ensure that very small numbers do not reduce to 0
                if round(i, 1) != 0:
                    self.assertAlmostEqual(i, i2, places=2)
                else:
                    self.assertAlmostEqual(i, i2, places=10)


class UserOptions(object):
    """Generate sample user-specified execution options."""

    def __init__(
        self,
        site_energy,
        capt_energy,
        regions,
        tsv_metrics,
        sect_shapes,
        rp_persist,
        health_costs,
        split_fuel,
        no_scnd_lgt,
        floor_start,
        pkg_env_costs,
        exog_hp_rates,
        grid_decarb,
        adopt_scn_restrict,
        retro_set,
        add_typ_eff,
        pkg_env_sep,
        alt_ref_carb,
        detail_brkout,
        fugitive_emissions,
        warnings,
        no_eff_capt,
        no_lnkd_stk,
        no_lnkd_op,
        elec_upgrade_costs,
        low_volume_rate,
        state_appl_regs,
        bps,
        codes,
        incentive_levels,
        incentive_restrictions,
    ):
        # Options include site energy outputs, captured energy site-source
        # calculation method, alternate regions, time sensitive output metrics,
        # sector-level load shapes, and verbose mode that prints all warnings
        self.site_energy = site_energy
        self.captured_energy = capt_energy
        self.alt_regions = regions
        self.rp_persist = rp_persist
        self.verbose = warnings
        self.tsv_metrics = tsv_metrics
        self.health_costs = health_costs
        self.sect_shapes = sect_shapes
        self.split_fuel = split_fuel
        self.no_scnd_lgt = no_scnd_lgt
        self.floor_start = floor_start
        self.pkg_env_costs = pkg_env_costs
        self.exog_hp_rates = exog_hp_rates
        self.grid_decarb = grid_decarb
        self.adopt_scn_restrict = adopt_scn_restrict
        self.retro_set = retro_set
        self.add_typ_eff = add_typ_eff
        self.pkg_env_sep = pkg_env_sep
        self.alt_ref_carb = alt_ref_carb
        self.detail_brkout = detail_brkout
        self.fugitive_emissions = fugitive_emissions
        self.no_eff_capt = no_eff_capt
        self.no_lnkd_stk_costs = no_lnkd_stk
        self.no_lnkd_op_costs = no_lnkd_op
        self.elec_upgrade_costs = elec_upgrade_costs
        self.low_volume_rate = low_volume_rate
        self.state_appl_regs = state_appl_regs
        self.bps = bps
        self.codes = codes
        self.incentive_levels = incentive_levels
        self.incentive_restrictions = incentive_restrictions


class NullOpts(object):
    """Generate null set of user-specified execution options.

    Attributes:
        opts (object): Sample null user options.
        opts_dict (dict): Dict-formatted sample null user options.
    """

    def __init__(self):
        # Note: technically, the 'detail_brkout' opt should be set to
        # False for this null case; however, because tests in this suite
        # were previously developed using the most detailed regional
        # breakouts, the option is set to continue using those breakouts
        # for regions only
        test_ecms = Path(__file__).parent.parent / "test_files" / "ecm_definitions"
        self.opts = ecm_args(
            [
                "--ecm_directory",
                str(test_ecms),
                "--detail_brkout",
                "regions",
                "--alt_regions",
                "AIA",
                "--no_eff_capt",
                "--no_lnkd_stk_costs",
                "in_adopt_and_report",
                "--elec_upgrade_costs",
                "ignore",
            ]
        )
        self.opts_dict = vars(self.opts)
