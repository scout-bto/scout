#!/usr/bin/env python3

"""Tests for 'import_state_data' function."""

import os
from pathlib import Path
import pytest

from scout.ecm_prep_vars import UsefulVars, UsefulInputFiles
from scout.ecm_prep_args import ecm_args


class NullOpts:
    """Generate null set of user-specified execution options.

    Attributes:
        opts (object): Sample null user options.
        opts_dict (dict): Dict-formatted sample null user options.
    """

    def __init__(self):
        test_ecms = Path(__file__).parent.parent / "test_files" / "ecm_definitions"
        self.opts = ecm_args(["--ecm_directory", str(test_ecms),
                              "--detail_brkout", "regions", "--alt_regions", "AIA",
                              "--no_eff_capt", "--no_lnkd_stk_costs", "in_adopt_and_report",
                              "--elec_upgrade_costs", "ignore"])
        self.opts_dict = vars(self.opts)


@pytest.fixture(scope="module")
def setup_data():
    """Define variables and objects for use across all test functions."""
    base_dir = os.getcwd()
    opts = NullOpts().opts
    handyfiles = UsefulInputFiles(opts)
    hvobj = UsefulVars(base_dir, handyfiles, opts)
    
    test_opts = [
        {"incentives": "aggressive", "low_volume_rate": "aggressive"},
        {"incentives": "aeo", "low_volume_rate": "reference"},
        {"incentives": "reference", "low_volume_rate": None}]
    
    test_paths = {
        "incentives": Path(__file__).parent.parent / "test_files" / "incentives_test.csv",
        "low_volume_rate": Path(__file__).parent.parent / "test_files" / "rates_test.csv"}
    
    for k in test_paths.keys():
        setattr(handyfiles, k, test_paths[k])
    
    valid_regions = ["CA", "NY"]
    
    incentives_out = [[
            ['CA', 'single family home', 'new', 'heating', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 30.0, 2000, '$/unit', 2024, 2025, 1.0],
            ['CA', 'single family home', 'existing', 'heating', 'ASHP', 'electricity',
             'natural gas', 'yes', 'replace', 'federal', True, 0,
             'warm climates: 2.76; cold climates: 2.93',
             'COP', 30.0, 2000, '$/unit', 2024, 2025, 1.0],
            ['CA', 'multi family home', 'new', 'heating', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 30.0, 2000, '$/unit', 2024, 2025, 1.0],
            ['CA', 'multi family home', 'existing', 'heating', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 30.0, 2000, '$/unit', 2024, 2025, 1.0],
            ['CA', 'mobile home', 'new', 'heating', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 30.0, 2000, '$/unit', 2024, 2025, 1.0],
            ['CA', 'mobile home', 'existing', 'heating', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 30.0, 2000, '$/unit', 2024, 2025, 1.0],
            ['NY', 'single family home', 'new', 'heating', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 30.0, 2000, '$/unit', 2024, 2025, 1.0],
            ['NY', 'single family home', 'existing', 'heating', 'ASHP', 'electricity',
             'natural gas', 'yes', 'replace', 'federal', True, 0,
             'warm climates: 2.76; cold climates: 2.93',
             'COP', 30.0, 2000, '$/unit', 2024, 2025, 1.0],
            ['NY', 'multi family home', 'new', 'heating', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 30.0, 2000, '$/unit', 2024, 2025, 1.0],
            ['NY', 'multi family home', 'existing', 'heating', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 30.0, 2000, '$/unit', 2024, 2025, 1.0],
            ['NY', 'mobile home', 'new', 'heating', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 30.0, 2000, '$/unit', 2024, 2025, 1.0],
            ['NY', 'mobile home', 'existing', 'heating', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 30.0, 2000, '$/unit', 2024, 2025, 1.0],
            ['CA', 'single family home', 'new', 'cooling', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 0, 0, '$/unit', 2024, 2025, 1.0],
            ['CA', 'single family home', 'existing', 'cooling', 'ASHP', 'electricity',
             'natural gas', 'yes', 'replace', 'federal', True, 0,
             'warm climates: 2.76; cold climates: 2.93',
             'COP', 0, 0, '$/unit', 2024, 2025, 1.0],
            ['CA', 'multi family home', 'new', 'cooling', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 0, 0, '$/unit', 2024, 2025, 1.0],
            ['CA', 'multi family home', 'existing', 'cooling', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 0, 0, '$/unit', 2024, 2025, 1.0],
            ['CA', 'mobile home', 'new', 'cooling', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 0, 0, '$/unit', 2024, 2025, 1.0],
            ['CA', 'mobile home', 'existing', 'cooling', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 0, 0, '$/unit', 2024, 2025, 1.0],
            ['NY', 'single family home', 'new', 'cooling', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 0, 0, '$/unit', 2024, 2025, 1.0],
            ['NY', 'single family home', 'existing', 'cooling', 'ASHP', 'electricity',
             'natural gas', 'yes', 'replace', 'federal', True, 0,
             'warm climates: 2.76; cold climates: 2.93',
             'COP', 0, 0, '$/unit', 2024, 2025, 1.0],
            ['NY', 'multi family home', 'new', 'cooling', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 0, 0, '$/unit', 2024, 2025, 1.0],
            ['NY', 'multi family home', 'existing', 'cooling', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 0, 0, '$/unit', 2024, 2025, 1.0],
            ['NY', 'mobile home', 'new', 'cooling', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 0, 0, '$/unit', 2024, 2025, 1.0],
            ['NY', 'mobile home', 'existing', 'cooling', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 0, 0, '$/unit', 2024, 2025, 1.0],
            ['CA', 'single family home', 'existing', 'heating', 'ASHP', 'electricity',
             'other fuel', 'no', 'replace', 'non-federal', False, 0, '2.69',
             'COP', 0, 8000, '$/unit', 2024, 2031, 0.244],
            ['CA', 'single family home', 'existing', 'cooling', 'ASHP', 'electricity',
             'other fuel', 'no', 'replace', 'non-federal', False, 0, '2.69',
             'COP', 0, 0, '$/unit', 2024, 2031, 0.244]
            ],
            None,
            [
            ['CA', 'single family home', 'new', 'heating', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 30.0, 2000, '$/unit', 2024, 2025, 1.0],
            ['CA', 'single family home', 'existing', 'heating', 'ASHP', 'electricity',
             'natural gas', 'yes', 'replace', 'federal', True, 0,
             'warm climates: 2.76; cold climates: 2.93',
             'COP', 30.0, 2000, '$/unit', 2024, 2025, 1.0],
            ['CA', 'multi family home', 'new', 'heating', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 30.0, 2000, '$/unit', 2024, 2025, 1.0],
            ['CA', 'multi family home', 'existing', 'heating', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 30.0, 2000, '$/unit', 2024, 2025, 1.0],
            ['CA', 'mobile home', 'new', 'heating', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 30.0, 2000, '$/unit', 2024, 2025, 1.0],
            ['CA', 'mobile home', 'existing', 'heating', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 30.0, 2000, '$/unit', 2024, 2025, 1.0],
            ['NY', 'single family home', 'new', 'heating', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 30.0, 2000, '$/unit', 2024, 2025, 1.0],
            ['NY', 'single family home', 'existing', 'heating', 'ASHP', 'electricity',
             'natural gas', 'yes', 'replace', 'federal', True, 0,
             'warm climates: 2.76; cold climates: 2.93',
             'COP', 30.0, 2000, '$/unit', 2024, 2025, 1.0],
            ['NY', 'multi family home', 'new', 'heating', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 30.0, 2000, '$/unit', 2024, 2025, 1.0],
            ['NY', 'multi family home', 'existing', 'heating', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 30.0, 2000, '$/unit', 2024, 2025, 1.0],
            ['NY', 'mobile home', 'new', 'heating', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 30.0, 2000, '$/unit', 2024, 2025, 1.0],
            ['NY', 'mobile home', 'existing', 'heating', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 30.0, 2000, '$/unit', 2024, 2025, 1.0],
            ['CA', 'single family home', 'new', 'cooling', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 0, 0, '$/unit', 2024, 2025, 1.0],
            ['CA', 'single family home', 'existing', 'cooling', 'ASHP', 'electricity',
             'natural gas', 'yes', 'replace', 'federal', True, 0,
             'warm climates: 2.76; cold climates: 2.93',
             'COP', 0, 0, '$/unit', 2024, 2025, 1.0],
            ['CA', 'multi family home', 'new', 'cooling', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 0, 0, '$/unit', 2024, 2025, 1.0],
            ['CA', 'multi family home', 'existing', 'cooling', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 0, 0, '$/unit', 2024, 2025, 1.0],
            ['CA', 'mobile home', 'new', 'cooling', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 0, 0, '$/unit', 2024, 2025, 1.0],
            ['CA', 'mobile home', 'existing', 'cooling', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 0, 0, '$/unit', 2024, 2025, 1.0],
            ['NY', 'single family home', 'new', 'cooling', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 0, 0, '$/unit', 2024, 2025, 1.0],
            ['NY', 'single family home', 'existing', 'cooling', 'ASHP', 'electricity',
             'natural gas', 'yes', 'replace', 'federal', True, 0,
             'warm climates: 2.76; cold climates: 2.93',
             'COP', 0, 0, '$/unit', 2024, 2025, 1.0],
            ['NY', 'multi family home', 'new', 'cooling', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 0, 0, '$/unit', 2024, 2025, 1.0],
            ['NY', 'multi family home', 'existing', 'cooling', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 0, 0, '$/unit', 2024, 2025, 1.0],
            ['NY', 'mobile home', 'new', 'cooling', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 0, 0, '$/unit', 2024, 2025, 1.0],
            ['NY', 'mobile home', 'existing', 'cooling', 'ASHP', 'electricity', 'natural gas',
             'yes', 'replace', 'federal', True, 0, 'warm climates: 2.76; cold climates: 2.93',
             'COP', 0, 0, '$/unit', 2024, 2025, 1.0],
            ['CA', 'single family home', 'existing', 'heating', 'ASHP', 'electricity',
             'other fuel', 'no', 'replace', 'non-federal', True, 0, '2.69',
             'COP', 0, 4000, '$/unit', 2024, 2031, 0.308],
            ['CA', 'single family home', 'existing', 'cooling', 'ASHP', 'electricity',
             'other fuel', 'no', 'replace', 'non-federal', True, 0, '2.69',
             'COP', 0, 0, '$/unit', 2024, 2031, 0.308]
            ]]
    
    low_volume_rate_out = [[
            ['CA', 'multi family home', 'new', 'all', 'all', 'electricity', 0.06,
             False, 302, 2026, False, 1],
            ['CA', 'multi family home', 'existing', 'all', 'all', 'electricity', 0.06,
             False, 302, 2026, False, 1],
            ['NY', 'single family home', 'new', 'heating', 'ASHP', 'electricity',
             False, 20.0, 0, 2030, False, 1],
            ['NY', 'single family home', 'new', 'heating', 'GSHP', 'electricity',
             False, 20.0, 0, 2030, False, 1],
            ['NY', 'single family home', 'existing', 'heating', 'ASHP', 'electricity',
             False, 20.0, 0, 2030, False, 1],
            ['NY', 'single family home', 'existing', 'heating', 'GSHP', 'electricity',
             False, 20.0, 0, 2030, False, 1],
            ['NY', 'multi family home', 'new', 'heating', 'ASHP', 'electricity',
             False, 20.0, 0, 2030, False, 1],
            ['NY', 'multi family home', 'new', 'heating', 'GSHP', 'electricity',
             False, 20.0, 0, 2030, False, 1],
            ['NY', 'multi family home', 'existing', 'heating', 'ASHP', 'electricity',
             False, 20.0, 0, 2030, False, 1],
            ['NY', 'multi family home', 'existing', 'heating', 'GSHP', 'electricity',
             False, 20.0, 0, 2030, False, 1],
            ['NY', 'mobile home', 'new', 'heating', 'ASHP', 'electricity',
             False, 20.0, 0, 2030, False, 1],
            ['NY', 'mobile home', 'new', 'heating', 'GSHP', 'electricity',
             False, 20.0, 0, 2030, False, 1],
            ['NY', 'mobile home', 'existing', 'heating', 'ASHP', 'electricity',
             False, 20.0, 0, 2030, False, 1],
            ['NY', 'mobile home', 'existing', 'heating', 'GSHP', 'electricity',
             False, 20.0, 0, 2030, False, 1]],
            [
            ['CA', 'single family home', 'new', 'all', 'all', 'electricity', 0.06,
             False, 302, 2026, False, 1],
            ['CA', 'single family home', 'existing', 'all', 'all', 'electricity', 0.06,
             False, 302, 2026, False, 1]],
            None]
    
    return {
        'opts': opts,
        'handyfiles': handyfiles,
        'hvobj': hvobj,
        'test_opts': test_opts,
        'test_paths': test_paths,
        'valid_regions': valid_regions,
        'incentives_out': incentives_out,
        'low_volume_rate_out': low_volume_rate_out
    }


def test_import_state_data(setup_data):
    """Test 'import_state_data' function with sample inputs.
    
    Ensure that state-level incentives and rate information are correctly 
    imported and initialized.
    """
    for case_ind, case in enumerate(range(len(setup_data['test_opts']))):
        for k in setup_data['test_paths'].keys():
            if k == "incentives":
                setup_data['opts'].incentive_levels = setup_data['test_opts'][case_ind][k]
            else:
                setup_data['opts'].low_volume_rate = setup_data['test_opts'][case_ind][k]
        
        setup_data['hvobj'].import_state_data(
            setup_data['handyfiles'], 
            setup_data['test_paths'].keys(),
            setup_data['valid_regions'], 
            setup_data['opts'])
        
        for output, expected in zip(
                [setup_data['hvobj'].incentives, setup_data['hvobj'].low_volume_rate],
                [setup_data['incentives_out'][case_ind], setup_data['low_volume_rate_out'][case_ind]]):
            assert output == expected
