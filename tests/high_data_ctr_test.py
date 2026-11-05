#!/usr/bin/env python3

"""Tests for high_data_ctr baseline selection in ecm_prep and run."""

import unittest
from tests.ecm_prep_test.common import NullOpts
from scout.ecm_prep_vars import UsefulInputFiles as ECMPrepUsefulInputFiles
from scout import run
from scout.config import FilePaths as fp


class TestHighDataCtrFileResolution(unittest.TestCase):
    """Test that toggling high_data_ctr correctly routes microsegment file paths
    in both ecm_prep and run modules across all supported geographic regions."""

    def setUp(self):
        self.opts = NullOpts().opts

    def tearDown(self):
        fp.reset_base_paths()

    def test_ecm_prep_useful_input_files_aia(self):
        """Test mseg file resolution for AIA regions in ecm_prep."""
        self.opts.alt_regions = "AIA"

        # Default (Reference Case)
        self.opts.high_data_ctr = False
        handyfiles_ref = ECMPrepUsefulInputFiles(self.opts)
        self.assertEqual(handyfiles_ref.msegs_in.name, "mseg_res_com_cz.json")
        self.assertTrue(handyfiles_ref.msegs_in.exists())

        # High Electricity Demand Case
        self.opts.high_data_ctr = True
        handyfiles_hdc = ECMPrepUsefulInputFiles(self.opts)
        self.assertEqual(handyfiles_hdc.msegs_in.name, "mseg_res_com_cz_hdc.json")
        self.assertTrue(handyfiles_hdc.msegs_in.exists())

    def test_ecm_prep_useful_input_files_emm(self):
        """Test mseg file resolution for EMM regions in ecm_prep."""
        self.opts.alt_regions = "EMM"

        # Default (Reference Case)
        self.opts.high_data_ctr = False
        handyfiles_ref = ECMPrepUsefulInputFiles(self.opts)
        self.assertEqual(handyfiles_ref.msegs_in.name, "mseg_res_com_emm.gz")
        self.assertTrue(handyfiles_ref.msegs_in.exists())

        # High Electricity Demand Case
        self.opts.high_data_ctr = True
        handyfiles_hdc = ECMPrepUsefulInputFiles(self.opts)
        self.assertEqual(handyfiles_hdc.msegs_in.name, "mseg_res_com_emm_hdc.gz")
        self.assertTrue(handyfiles_hdc.msegs_in.exists())

    def test_ecm_prep_useful_input_files_state(self):
        """Test mseg file resolution for State regions in ecm_prep."""
        self.opts.alt_regions = "State"

        # Default (Reference Case)
        self.opts.high_data_ctr = False
        handyfiles_ref = ECMPrepUsefulInputFiles(self.opts)
        self.assertEqual(handyfiles_ref.msegs_in.name, "mseg_res_com_state.gz")
        self.assertTrue(handyfiles_ref.msegs_in.exists())

        # High Electricity Demand Case
        self.opts.high_data_ctr = True
        handyfiles_hdc = ECMPrepUsefulInputFiles(self.opts)
        self.assertEqual(handyfiles_hdc.msegs_in.name, "mseg_res_com_state_hdc.gz")
        self.assertTrue(handyfiles_hdc.msegs_in.exists())

    def test_run_useful_input_files_aia(self):
        """Test mseg file resolution for AIA regions in run."""
        energy_out = ["fossil_equivalent", "NA", "NA", "NA", "NA"]

        # Default (Reference Case)
        handyfiles_ref = run.UsefulInputFiles(
            energy_out, regions="AIA", grid_decarb=False, high_data_ctr=False
        )
        self.assertEqual(handyfiles_ref.msegs_in.name, "mseg_res_com_cz.json")
        self.assertTrue(handyfiles_ref.msegs_in.exists())

        # High Electricity Demand Case
        handyfiles_hdc = run.UsefulInputFiles(
            energy_out, regions="AIA", grid_decarb=False, high_data_ctr=True
        )
        self.assertEqual(handyfiles_hdc.msegs_in.name, "mseg_res_com_cz_hdc.json")
        self.assertTrue(handyfiles_hdc.msegs_in.exists())

    def test_run_useful_input_files_emm(self):
        """Test mseg file resolution for EMM regions in run."""
        energy_out = ["fossil_equivalent", "NA", "NA", "NA", "NA"]

        # Default (Reference Case)
        handyfiles_ref = run.UsefulInputFiles(
            energy_out, regions="EMM", grid_decarb=False, high_data_ctr=False
        )
        self.assertEqual(handyfiles_ref.msegs_in.name, "mseg_res_com_emm.gz")
        self.assertTrue(handyfiles_ref.msegs_in.exists())

        # High Electricity Demand Case
        handyfiles_hdc = run.UsefulInputFiles(
            energy_out, regions="EMM", grid_decarb=False, high_data_ctr=True
        )
        self.assertEqual(handyfiles_hdc.msegs_in.name, "mseg_res_com_emm_hdc.gz")
        self.assertTrue(handyfiles_hdc.msegs_in.exists())

    def test_run_useful_input_files_state(self):
        """Test mseg file resolution for State regions in run."""
        energy_out = ["fossil_equivalent", "NA", "NA", "NA", "NA"]

        # Default (Reference Case)
        handyfiles_ref = run.UsefulInputFiles(
            energy_out, regions="State", grid_decarb=False, high_data_ctr=False
        )
        self.assertEqual(handyfiles_ref.msegs_in.name, "mseg_res_com_state.gz")
        self.assertTrue(handyfiles_ref.msegs_in.exists())

        # High Electricity Demand Case
        handyfiles_hdc = run.UsefulInputFiles(
            energy_out, regions="State", grid_decarb=False, high_data_ctr=True
        )
        self.assertEqual(handyfiles_hdc.msegs_in.name, "mseg_res_com_state_hdc.gz")
        self.assertTrue(handyfiles_hdc.msegs_in.exists())

    def test_measure_opts_match_high_data_ctr(self):
        """Test that run.measure_opts_match checks consistency of high_data_ctr across measures."""
        opts_matching_1 = {"high_data_ctr": True, "site_energy": False}
        opts_matching_2 = {"high_data_ctr": True, "site_energy": False}
        opts_mismatched = {"high_data_ctr": False, "site_energy": False}

        self.assertTrue(run.measure_opts_match([opts_matching_1, opts_matching_2]))
        self.assertFalse(run.measure_opts_match([opts_matching_1, opts_mismatched]))


if __name__ == "__main__":
    unittest.main()
