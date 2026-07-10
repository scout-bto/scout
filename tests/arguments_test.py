from __future__ import annotations
import unittest
import copy
import jsonschema
from pathlib import Path, PurePath
from argparse import ArgumentParser
from scout.config import Config, FilePaths as fp
from scout.ecm_prep_args import ecm_args


class Utils:
    """Shared resources with paths to test yml files and a method for asserting argument values
    """

    test_files = Path(__file__).parent / "test_files"
    empty_yml_pth = str(test_files / "empty_config.yml")
    default_yml_pth = str(fp.INPUTS / "config_default.yml")
    valid_yml_pth = str(test_files / "valid_config.yml")

    def _assert_path(self, path: Path, expected_path: str, arg: str = None):
        """Assert expected filepath by checking the two deepest directories of `path`. Only checks
            part of the path to maintain compatibility across systems.

        Args:
            path (Path): Full path to check
            expected_path (str): Deepest two paths expected
            arg (str, optional): The argparse argument with which the check is associated.
                Defaults to None.
        """

        local_path = str(Path(*path.parts[-2:])).replace("\\", "/")
        msg = None
        if arg:
            msg = f"for argument {arg}"
        self.assertEqual(local_path, expected_path, msg)

    def _assert_arg_vals(self, args: argparse.NameSpace, expected_args: dict):  # noqa: F821
        """Generic method to assert generated argparse object against expected

        Args:
            args (argparse.NameSpace): Arguments object generated for ecm_prep.py or run.py
            expected_args (dict): Expected arguments and argument values
        """

        # Get parsed args and compare to args in expected dict individually
        for arg, expected_val in expected_args.items():
            parsed_arg_val = vars(args).get(arg)

            # Ensure consistent sorting between lists
            if isinstance(parsed_arg_val, list):
                parsed_arg_val = [str(v) for v in parsed_arg_val]
                expected_val = [str(v) for v in expected_val]
                parsed_arg_val.sort()
                expected_val.sort()

            # Check deepest two directories for path args
            if isinstance(parsed_arg_val, PurePath):
                self._assert_path(parsed_arg_val, expected_val, arg)
            else:
                self.assertEqual(parsed_arg_val, expected_val, f"for argument {arg}")


class TestConfig(unittest.TestCase, Utils):
    """Tests to process yml configuration files and parse as arguments within the Config class.
        These tests cover only methods in Config, addressing both argument parsing from yml
        files and directly from the command line.
    """

    # Expected ecm_prep and run default values; aligns with test_files/default_config.yml
    default_config = {
        "ecm_prep": {
            "ecm_directory": None,
            "ecm_files": None,
            "ecm_files_regex": [],
            "ecm_packages": [],
            "site_energy": False,
            "captured_energy": False,
            "alt_regions": "EMM",
            "tsv_type": None,
            "tsv_daily_hr_restrict": None,
            "tsv_sys_shape_case": None,
            "tsv_season": None,
            "tsv_energy_agg": None,
            "tsv_power_agg": None,
            "tsv_average_days": None,
            "sect_shapes": False,
            "rp_persist": False,
            "verbose": False,
            "health_costs": False,
            "split_fuel": False,
            "no_scnd_lgt": False,
            "floor_start": None,
            "pkg_env_costs": None,
            "exog_hp_rate_scenario": None,
            "switch_all_retrofit_hp": False,
            "alt_ref_carb": None,
            "grid_decarb_level": None,
            "grid_assessment_timing": None,
            "adopt_scn_restrict": None,
            "retrofit_type": None,
            "retrofit_multiplier": None,
            "retrofit_mult_year": None,
            "add_typ_eff": False,
            "pkg_env_sep": False,
            "detail_brkout": [],
            "fugitive_emissions": [],
            "no_eff_capt": False,
            "no_lnkd_stk_costs": None,
            "no_lnkd_op_costs": False,
            "elec_upgrade_costs": "shares",
            "low_volume_rate": None,
            "incentive_levels": "aeo",
            "incentive_restrictions": None,
            "state_appl_regs": None,
            "bps": None,
            "codes": None,
            "report_stk": None,
            "comstock_gap": False
        },
        "run": {
            "results_directory": None,
            "verbose": False,
            "mkt_fracs": False,
            "trim_vars": False,
            "report_custom_yrs": [],
            "report_cfs": False,
            "no_comp": False,
            "high_res_comp": False,
            "write_elec_conv_fracs": False
        },
    }

    # Expected values for a valid config file; aligns with test_files/valid_config.yml
    valid_config = {
        "ecm_prep": {
            "ecm_directory": "test_files/ecm_definitions",
            "ecm_files": ["Best Com. Air Sealing (Exist)", "Best Com. Air Sealing (New)"],
            "ecm_files_regex": ["^Best Res\\. Air Sealing \\((Exist|New)\\)$"],
            "add_typ_eff": True,
            "rp_persist": True,
            "alt_regions": "EMM",
            "adopt_scn_restrict": "Max adoption potential",
            "fugitive_emissions": ["methane-mid", "typical refrigerant"],
            "retrofit_type": "increasing",
            "retrofit_multiplier": 1.2,
            "retrofit_mult_year": 2030,
            "exog_hp_rate_scenario": "gh-aggressive",
            "switch_all_retrofit_hp": False,
            "grid_decarb_level": "100by2035",
            "grid_assessment_timing": "after",
            "tsv_type": "energy",
            "tsv_daily_hr_restrict": "all",
            "tsv_sys_shape_case": "total reference",
            "tsv_season": "summer",
            "tsv_energy_agg": "average",
            "tsv_average_days": "weekdays",
            "detail_brkout": ["regions", "fuel types"],
            "pkg_env_costs": "include HVAC",
        },
        "run": {"results_directory": "results/test_dir",
                "mkt_fracs": True,
                "trim_vars": False,
                "report_custom_yrs": []},
    }

    def tearDown(self):
        # Reset base filepaths so downstream tests are not affected
        fp.reset_base_paths()

    def _get_cfg_args(self, key: str, cli_args=[]) -> argparse.Namespace:  # noqa: F821
        """Instantiates the Config class and parses args based on cli args

        Args:
            key (str): File for which to parse args, ecm_prep or run
            cli_args (list, optional): Command line arguments for given key. Defaults to [].

        Returns:
            argparse.Namespace: Arguments object that could be used in ecm_prep.py or run.py
        """

        # Instantiate Config class and parse args
        parser = ArgumentParser()
        config = Config(parser, key, cli_args)
        args = config.parse_args()
        return args

    def _check_schema_err(self, expected_err: str, args_update: dict = {}, drop_key: str = None):
        """Generic method to check for expected schema validation error messages that result from
            updates to a valid configuration file.

        Args:
            expected_err (str): Expected error message when validating
            args_update (dict, optional): Changes to valid yml data that should result in a
                validation error. Defaults to {}.
            drop_key (str, optional): Specify key in the valid yml to drop that results in a
                validation error. Defaults to None.
        """

        parser = ArgumentParser()
        c = Config(parser, "ecm_prep", ["--yaml", self.valid_yml_pth])
        c.config_args.update(args_update)
        if drop_key:
            c.config_args.pop(drop_key)

        with self.assertRaises(jsonschema.exceptions.ValidationError) as context:
            c._validate(c.config_args)
        actual_msg = str(context.exception)
        self.assertTrue(expected_err in actual_msg, f"Expected {expected_err} in {actual_msg}")

    def test_empty_args(self):
        # Test defaults from no cfg file (no cli args)
        # ecm_prep.py
        args = self._get_cfg_args("ecm_prep", cli_args=[])
        self._assert_arg_vals(args, self.default_config["ecm_prep"])

        # run.py
        args = self._get_cfg_args("run", cli_args=[])
        self._assert_arg_vals(args, self.default_config["run"])

    def test_minimum_yml(self):
        # Test args that are applied by default for an empty cfg file (yml with no arguments)
        # ecm_prep.py
        args = self._get_cfg_args("ecm_prep", cli_args=["--yaml", self.empty_yml_pth])
        self._assert_arg_vals(args, self.default_config["ecm_prep"])

        # run.py
        args = self._get_cfg_args("run", cli_args=["--yaml", self.empty_yml_pth])
        self._assert_arg_vals(args, self.default_config["run"])

    def test_default_yml(self):
        # Test explicit default values provided via cfg file
        # ecm_prep.py
        args = self._get_cfg_args("ecm_prep", cli_args=["--yaml", self.default_yml_pth])
        self._assert_arg_vals(args, self.default_config["ecm_prep"])

        # run.py
        args = self._get_cfg_args("run", cli_args=["--yaml", self.empty_yml_pth])
        self._assert_arg_vals(args, self.default_config["run"])

    def test_valid_yml_file(self):
        # Test & validate with valid cfg file. Note: _get_cfg_args() will automatically validate
        # when instantiating Config()

        # ecm_prep.py
        args = self._get_cfg_args("ecm_prep", cli_args=["--yaml", self.valid_yml_pth])
        self._assert_arg_vals(args, self.valid_config["ecm_prep"])

        # run.py
        args = self._get_cfg_args("run", cli_args=["--yaml", self.valid_yml_pth])
        self._assert_arg_vals(args, self.valid_config["run"])
        self._assert_path(fp.RESULTS, "results/test_dir")

    def test_cli_overwrite(self):
        # Ensure cli arguments take precedence over yml
        # ecm_prep.py
        cli_args = [
            "--yaml",
            self.valid_yml_pth,
            "--ecm_files",
            "Best Com. Air Sealing (Exist)",
            "--adopt_scn_restrict",
            "Technical potential",
            "--fugitive_emissions",
            "low-gwp refrigerant",
        ]
        args = self._get_cfg_args("ecm_prep", cli_args=cli_args)
        expected_args = copy.deepcopy(self.valid_config["ecm_prep"])
        update_dict = {
            "ecm_files": ["Best Com. Air Sealing (Exist)"],
            "adopt_scn_restrict": "Technical potential",
            "fugitive_emissions": ["low-gwp refrigerant"],
        }
        expected_args.update(update_dict)
        self._assert_arg_vals(args, expected_args)

        # run.py
        cli_args = ["--yaml", self.valid_yml_pth, "--report_cfs"]
        args = self._get_cfg_args("run", cli_args=cli_args)
        expected_args = copy.deepcopy(self.valid_config["run"])
        update_dict = {
            "report_cfs": True,
        }
        expected_args.update(update_dict)
        self._assert_arg_vals(args, expected_args)

    def test_invalid_yml_schema(self):
        # Check that invalid values/keys in the yml schema yield expected exceptions
        args_update = {"ecm_prep": {"alt_regions": "invalid"}}
        expected_err = "'invalid' is not one of ['EMM', 'State', 'AIA']"
        self._check_schema_err(expected_err, args_update)

        args_update = {
            "ecm_prep": {"fugitive_emissions": ["low-gwp refrigerant", "typical refrigerant"]}
        }
        expected_err = "['low-gwp refrigerant', 'typical refrigerant'] should not be valid under"
        self._check_schema_err(expected_err, args_update)

        expected_err = "'description' is a required property"
        self._check_schema_err(expected_err, drop_key="description")

    def _get_cfg_args_err_message(self, key: str, cli_args: []) -> str:
        """Runs _get_cfg_args() for scenarios with expected error messages, returns the error

        Args:
            key (str): File for which to parse args, ecm_prep or run
            cli_args (list, optional): Command line arguments for given key. Defaults to [].

        Returns:
            str: error message as a result of calling Config.parse_args
        """

        with self.assertRaises(ValueError) as context:
            self._get_cfg_args("ecm_prep", cli_args)
        actual_msg = str(context.exception)

        return actual_msg

    def test_invalid_config_args(self):
        # Check that incompatible argument values not specified in the yml schema yield
        # appropriate exceptions
        cli_args = ["--detail_brkout", "fuel types"]
        actual_err = self._get_cfg_args_err_message("ecm_prep", cli_args)
        expected_err = (
            "Detailed breakout (`detail_brkout`) cannot include `fuel types` if split_fuel==False"
        )
        self.assertTrue(expected_err in actual_err, f"Expected {expected_err} in {actual_err}")

        cli_args = ["--tsv_type", "energy"]
        actual_err = self._get_cfg_args_err_message("ecm_prep", cli_args)
        expected_err = (
            "Both `tsv_type` and `tsv_daily_hr_restrict` must be provided if running tsv metrics"
        )
        self.assertTrue(expected_err in actual_err, f"Expected {expected_err} in {actual_err}")

        cli_args = ["--tsv_type", "power",
                    "--tsv_daily_hr_restrict", "all",
                    "--tsv_power_agg", "average"]
        actual_err = self._get_cfg_args_err_message("ecm_prep", cli_args)
        expected_err = ("`tsv_average_days` must be specified if `tsv_power_agg` is 'average'.")
        self.assertTrue(expected_err in actual_err, f"Expected {expected_err} in {actual_err}")

        cli_args = ["--retrofit_type", "increasing",
                    "--retrofit_multiplier", "1"]
        actual_err = self._get_cfg_args_err_message("ecm_prep", cli_args)
        expected_err = (
            "`retrofit_multiplier` and `retrofit_mult_year` must be specified if `retrofit_type`"
            " is 'increasing'."
        )
        self.assertTrue(expected_err in actual_err, f"Expected {expected_err} in {actual_err}")


class TestECMPrepArgsTranslate(unittest.TestCase, Utils):
    """Tests to confirm accurate translation of cli/yml arguments to values used in ecm_prep.py.
        These tests implicitly use the Config class, but focus on methods from ecm_prep_args.py.
    """

    # Expected default values translated in ecm_prep_args; aligns with values translated from
    # test_files/default_config.yml
    default_translated = {
        "ecm_directory": None,
        "ecm_files": [
            file.stem for file in fp.ECM_DEF.iterdir() if file.is_file() and
            file.suffix == '.json' and file.stem != 'package_ecms'],
        "ecm_files_regex": [],
        "ecm_packages": [],
        "site_energy": False,
        "captured_energy": False,
        "alt_regions": "EMM",
        "tsv_type": None,
        "tsv_daily_hr_restrict": None,
        "tsv_sys_shape_case": None,
        "tsv_season": None,
        "tsv_energy_agg": None,
        "tsv_power_agg": None,
        "tsv_average_days": None,
        "sect_shapes": False,
        "rp_persist": False,
        "verbose": False,
        "health_costs": False,
        "split_fuel": False,
        "no_scnd_lgt": False,
        "floor_start": None,
        "pkg_env_costs": False,
        "exog_hp_rate_scenario": None,
        "switch_all_retrofit_hp": False,
        "alt_ref_carb": None,
        "grid_decarb_level": None,
        "grid_assessment_timing": None,
        "adopt_scn_restrict": ["Technical potential", "Max adoption potential"],
        "retrofit_type": None,
        "retrofit_multiplier": None,
        "retrofit_mult_year": None,
        "add_typ_eff": False,
        "pkg_env_sep": False,
        "detail_brkout": False,
        "fugitive_emissions": False,
        "tsv_metrics": False,
        "retro_set": ["1", None, None],
        "exog_hp_rates": False,
        "grid_decarb": False
    }

    # Expected values translated from ecm_prep_args valid config file; aligns with
    # test_files/valid_config.yml
    valid_yml_translated = {
        "ecm_directory": "test_files/ecm_definitions",
        "ecm_files": ["Best Com. Air Sealing (Exist)",
                      "Best Com. Air Sealing (New)",
                      "Best Res. Air Sealing (Exist)",
                      "Best Res. Air Sealing (New)"],
        "ecm_files_regex": ["^Best Res\\. Air Sealing \\((Exist|New)\\)$"],
        "ecm_packages": [],
        "site_energy": True,
        "captured_energy": False,
        "alt_regions": "EMM",
        "tsv_type": "energy",
        "tsv_daily_hr_restrict": "all",
        "tsv_sys_shape_case": "total reference",
        "tsv_season": "summer",
        "tsv_energy_agg": "average",
        "tsv_power_agg": None,
        "tsv_average_days": "weekdays",
        "sect_shapes": False,
        "rp_persist": True,
        "verbose": False,
        "health_costs": False,
        "split_fuel": True,
        "no_scnd_lgt": False,
        "floor_start": None,
        "pkg_env_costs": "1",
        "exog_hp_rate_scenario": "gh-aggressive",
        "switch_all_retrofit_hp": False,
        "alt_ref_carb": None,
        "grid_decarb_level": "100by2035",
        "grid_assessment_timing": "after",
        "adopt_scn_restrict": ["Max adoption potential"],
        "retrofit_type": "increasing",
        "retrofit_multiplier": 1.2,
        "retrofit_mult_year": 2030,
        "add_typ_eff": True,
        "pkg_env_sep": False,
        "detail_brkout": "6",
        "fugitive_emissions": [3, 2, 2],
        "retro_set": ["3", 1.2, 2030],
        "exog_hp_rates": ["gh-aggressive", "2"],
        "grid_decarb": True,
        "tsv_metrics": ["1", "1", "1", "2", "1", "2"],
    }

    def tearDown(self):
        # Reset base filepaths so downstream tests are not affected
        fp.reset_base_paths()

    def test_translate_empty_cli(self):
        # Translation of empty/default arguments
        args = ecm_args([])
        self._assert_arg_vals(args, self.default_translated)

    def test_translate_valid_cli(self):
        # Translation of valid cli inputs
        cli_args = [
            "--ecm_files",
            "Best Com. Air Sealing (Exist)",
            "--ecm_directory",
            "tests/test_files/ecm_definitions",
            "--add_typ_eff",
            "--alt_regions",
            "EMM",
            "--detail_brkout",
            "regions",
            "fuel types",
            "--split_fuel"
        ]
        args = ecm_args(cli_args)
        self.assertEqual(args.add_typ_eff, True)
        self.assertEqual(args.alt_regions, "EMM")
        self.assertEqual(args.detail_brkout, "6")
        self.assertEqual(args.ecm_files, ["Best Com. Air Sealing (Exist)"])
        cli_args = [
            "--detail_brkout",
            "buildings",
            "--retrofit_type",
            "increasing",
            "--retrofit_multiplier",
            "2",
            "--retrofit_mult_year",
            "2030",
        ]
        args = ecm_args(cli_args)
        self.assertEqual(args.detail_brkout, "3")
        self.assertEqual(args.retro_set, ["3", 2.0, 2030])

    def test_missing_ecms(self):
        # Test that missing ECM(s) are omitted from the ECM file list
        with self.assertWarns(UserWarning) as warning_context:
            cli_args = [
                "--ecm_files",
                "Non-Existent ECM",
                "Best Com. Air Sealing (Exist)",
                "--ecm_directory",
                "tests/test_files/ecm_definitions",
            ]
            args = ecm_args(cli_args)
            self.assertEqual(args.ecm_files, ["Best Com. Air Sealing (Exist)"])
            self.assertIn("The following ECMs specified with the `ecm_files` argument are not "
                          "present in", str(warning_context.warnings[0]))

    def test_translate_from_empty_cfg(self):
        # Translation of empty yml (default args)
        args = ecm_args(["--yaml", self.empty_yml_pth])
        self._assert_arg_vals(args, self.default_translated)

    def test_translate_from_valid_cfg(self):
        # Translation of valid yaml args
        args = ecm_args(["--yaml", self.valid_yml_pth])
        self._assert_arg_vals(args, self.valid_yml_translated)

    def test_translate_cli_overwrite(self):
        # Ensure cli arguments take precedence over yml and are correctly translated
        cli_args = [
            "--yaml",
            self.valid_yml_pth,
            "--adopt_scn_restrict",
            "Technical potential",
            "--fugitive_emissions",
            "low-gwp refrigerant",
        ]
        update_dict = {"adopt_scn_restrict": ["Technical potential"],
                       "fugitive_emissions": [2, 3, None]}
        args = ecm_args(cli_args)
        expected_args = copy.deepcopy(self.valid_yml_translated)
        expected_args.update(update_dict)
        self._assert_arg_vals(args, expected_args)


if __name__ == "__main__":
    unittest.main()
