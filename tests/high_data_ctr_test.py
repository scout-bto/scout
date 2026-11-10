#!/usr/bin/env python3

"""Tests for high_data_ctr baseline selection in ecm_prep and run."""

import unittest
from tests.ecm_prep_test.common import NullOpts
from scout.ecm_prep_vars import UsefulInputFiles as ECMPrepUsefulInputFiles
from scout import run
from scout.config import FilePaths as fp


class TestHighDataCtrFileResolution(unittest.TestCase):
    """Test that toggling high_data_ctr routes microsegment file paths
    in both ecm_prep and run modules across supported geographic regions."""

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
        self.assertEqual(
            handyfiles_hdc.msegs_in.name, "mseg_res_com_cz_hdc.json"
        )
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
        self.assertEqual(
            handyfiles_hdc.msegs_in.name, "mseg_res_com_emm_hdc.gz"
        )
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
        self.assertEqual(
            handyfiles_hdc.msegs_in.name, "mseg_res_com_state_hdc.gz"
        )
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
        self.assertEqual(
            handyfiles_hdc.msegs_in.name, "mseg_res_com_cz_hdc.json"
        )
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
        self.assertEqual(
            handyfiles_hdc.msegs_in.name, "mseg_res_com_emm_hdc.gz"
        )
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
        self.assertEqual(
            handyfiles_hdc.msegs_in.name, "mseg_res_com_state_hdc.gz"
        )
        self.assertTrue(handyfiles_hdc.msegs_in.exists())

    def test_ecm_prep_useful_input_files_htcl_totals(self):
        """Test htcl_totals file resolution in ecm_prep across regions and
        energy metrics."""
        cases = [
            ("AIA", None, "htcl_totals.json", "htcl_totals_hdc.json"),
            (
                "AIA",
                "site_energy",
                "htcl_totals-site.json",
                "htcl_totals-site_hdc.json",
            ),
            (
                "AIA",
                "captured_energy",
                "htcl_totals-ce.json",
                "htcl_totals-ce_hdc.json",
            ),
            (
                "AIA",
                "grid_decarb_level",
                "htcl_totals_decarb.json",
                "htcl_totals_decarb_hdc.json",
            ),
            ("EMM", None, "htcl_totals_emm.json", "htcl_totals_emm_hdc.json"),
            (
                "EMM",
                "site_energy",
                "htcl_totals-site_emm.json",
                "htcl_totals-site_emm_hdc.json",
            ),
            (
                "EMM",
                "captured_energy",
                "htcl_totals-ce_emm.json",
                "htcl_totals-ce_emm_hdc.json",
            ),
            (
                "EMM",
                "grid_decarb_level",
                "htcl_totals_emm_decarb.json",
                "htcl_totals_emm_decarb_hdc.json",
            ),
            (
                "State",
                None,
                "htcl_totals_state.json",
                "htcl_totals_state_hdc.json",
            ),
            (
                "State",
                "site_energy",
                "htcl_totals-site_state.json",
                "htcl_totals-site_state_hdc.json",
            ),
            (
                "State",
                "captured_energy",
                "htcl_totals-ce_state.json",
                "htcl_totals-ce_state_hdc.json",
            ),
        ]

        for reg, flag, ref_exp, hdc_exp in cases:
            with self.subTest(region=reg, flag=flag):
                opts_ref = NullOpts().opts
                opts_ref.alt_regions = reg
                opts_ref.high_data_ctr = False
                if flag == "site_energy":
                    opts_ref.site_energy = True
                elif flag == "captured_energy":
                    opts_ref.captured_energy = True
                elif flag == "grid_decarb_level":
                    opts_ref.grid_decarb_level = "95by2035"
                p_ref = ECMPrepUsefulInputFiles(opts_ref)
                self.assertEqual(p_ref.htcl_totals.name, ref_exp)
                self.assertTrue(p_ref.htcl_totals.exists())

                opts_hdc = NullOpts().opts
                opts_hdc.alt_regions = reg
                opts_hdc.high_data_ctr = True
                if flag == "site_energy":
                    opts_hdc.site_energy = True
                elif flag == "captured_energy":
                    opts_hdc.captured_energy = True
                elif flag == "grid_decarb_level":
                    opts_hdc.grid_decarb_level = "95by2035"
                p_hdc = ECMPrepUsefulInputFiles(opts_hdc)
                self.assertEqual(p_hdc.htcl_totals.name, hdc_exp)
                self.assertTrue(p_hdc.htcl_totals.exists())

    def test_run_useful_input_files_htcl_totals(self):
        """Test htcl_totals file resolution in run across regions and energy
        metrics."""
        cases = [
            (
                "AIA",
                "fossil_equivalent",
                False,
                "htcl_totals.json",
                "htcl_totals_hdc.json",
            ),
            (
                "AIA",
                "site",
                False,
                "htcl_totals-site.json",
                "htcl_totals-site_hdc.json",
            ),
            (
                "AIA",
                "captured",
                False,
                "htcl_totals-ce.json",
                "htcl_totals-ce_hdc.json",
            ),
            (
                "AIA",
                "fossil_equivalent",
                True,
                "htcl_totals_decarb.json",
                "htcl_totals_decarb_hdc.json",
            ),
            (
                "EMM",
                "fossil_equivalent",
                False,
                "htcl_totals_emm.json",
                "htcl_totals_emm_hdc.json",
            ),
            (
                "EMM",
                "site",
                False,
                "htcl_totals-site_emm.json",
                "htcl_totals-site_emm_hdc.json",
            ),
            (
                "EMM",
                "captured",
                False,
                "htcl_totals-ce_emm.json",
                "htcl_totals-ce_emm_hdc.json",
            ),
            (
                "EMM",
                "fossil_equivalent",
                True,
                "htcl_totals_emm_decarb.json",
                "htcl_totals_emm_decarb_hdc.json",
            ),
            (
                "State",
                "fossil_equivalent",
                False,
                "htcl_totals_state.json",
                "htcl_totals_state_hdc.json",
            ),
            (
                "State",
                "site",
                False,
                "htcl_totals-site_state.json",
                "htcl_totals-site_state_hdc.json",
            ),
            (
                "State",
                "captured",
                False,
                "htcl_totals-ce_state.json",
                "htcl_totals-ce_state_hdc.json",
            ),
        ]

        for reg, eng, is_decarb, ref_exp, hdc_exp in cases:
            with self.subTest(region=reg, energy=eng, grid_decarb=is_decarb):
                r_ref = run.UsefulInputFiles(
                    [eng, "NA", "NA", "NA", "NA"],
                    regions=reg,
                    grid_decarb=is_decarb,
                    high_data_ctr=False,
                )
                self.assertEqual(r_ref.htcl_totals.name, ref_exp)
                self.assertTrue(r_ref.htcl_totals.exists())

                r_hdc = run.UsefulInputFiles(
                    [eng, "NA", "NA", "NA", "NA"],
                    regions=reg,
                    grid_decarb=is_decarb,
                    high_data_ctr=True,
                )
                self.assertEqual(r_hdc.htcl_totals.name, hdc_exp)
                self.assertTrue(r_hdc.htcl_totals.exists())

    def test_ecm_prep_useful_input_files_conversions(self):
        """Test conversion and price file resolution in ecm_prep."""
        for reg, price_file in [
            ("EMM", "emm_region_emissions_prices"),
            ("State", "state_emissions_prices"),
        ]:
            with self.subTest(region=reg):
                opts_ref = NullOpts().opts
                opts_ref.alt_regions = reg
                opts_ref.high_data_ctr = False
                p_ref = ECMPrepUsefulInputFiles(opts_ref)
                p_ref.set_decarb_grid_vars(opts_ref)
                self.assertEqual(
                    p_ref.ss_data.name, "site_source_co2_conversions.json"
                )
                self.assertTrue(p_ref.ss_data.exists())
                self.assertEqual(
                    p_ref.ss_data_altreg.name, f"{price_file}.json"
                )
                self.assertTrue(p_ref.ss_data_altreg.exists())

                opts_hdc = NullOpts().opts
                opts_hdc.alt_regions = reg
                opts_hdc.high_data_ctr = True
                p_hdc = ECMPrepUsefulInputFiles(opts_hdc)
                p_hdc.set_decarb_grid_vars(opts_hdc)
                self.assertEqual(
                    p_hdc.ss_data.name, "site_source_co2_conversions_hdc.json"
                )
                self.assertTrue(p_hdc.ss_data.exists())
                self.assertEqual(
                    p_hdc.ss_data_altreg.name, f"{price_file}_hdc.json"
                )
                self.assertTrue(p_hdc.ss_data_altreg.exists())

    def test_run_useful_input_files_conversions(self):
        """Test conversion and price file resolution in run."""
        for reg, price_file in [
            ("AIA", "site_source_co2_conversions"),
            ("EMM", "emm_region_emissions_prices"),
            ("State", "state_emissions_prices"),
        ]:
            with self.subTest(region=reg):
                r_ref = run.UsefulInputFiles(
                    ["fossil_equivalent", "NA", "NA", "NA", "NA"],
                    regions=reg,
                    grid_decarb=False,
                    high_data_ctr=False,
                )
                self.assertEqual(
                    r_ref.ss_data.name, "site_source_co2_conversions.json"
                )
                self.assertTrue(r_ref.ss_data.exists())
                self.assertEqual(
                    r_ref.elec_price_co2.name, f"{price_file}.json"
                )
                self.assertTrue(r_ref.elec_price_co2.exists())

                r_hdc = run.UsefulInputFiles(
                    ["fossil_equivalent", "NA", "NA", "NA", "NA"],
                    regions=reg,
                    grid_decarb=False,
                    high_data_ctr=True,
                )
                self.assertEqual(
                    r_hdc.ss_data.name, "site_source_co2_conversions_hdc.json"
                )
                self.assertTrue(r_hdc.ss_data.exists())
                self.assertEqual(
                    r_hdc.elec_price_co2.name, f"{price_file}_hdc.json"
                )
                self.assertTrue(r_hdc.elec_price_co2.exists())

    def test_measure_opts_match_high_data_ctr(self):
        """Test that run.measure_opts_match checks consistency of
        high_data_ctr across measures."""
        opts_matching_1 = {"high_data_ctr": True, "site_energy": False}
        opts_matching_2 = {"high_data_ctr": True, "site_energy": False}
        opts_mismatched = {"high_data_ctr": False, "site_energy": False}

        self.assertTrue(
            run.measure_opts_match([opts_matching_1, opts_matching_2])
        )
        self.assertFalse(
            run.measure_opts_match([opts_matching_1, opts_mismatched])
        )


if __name__ == "__main__":
    unittest.main()
