import pandas as pd
import argparse
import json
import re
from pathlib import Path
import logging
from scout.config import LogConfig
LogConfig.configure_logging()
logger = logging.getLogger(__name__)


class ScoutCompare():
    """Class to compare results from  Scout workflow run. Comparisons are saved as csv files to
        summarize differences in results json files (agg_results.json, ecm_results.json) and/or
        summary report files (Summary_Data-TP.xlsx, Summary_Data-MAP.xlsx)
    """

    @staticmethod
    def load_json(file_path: Path):
        """Load json file as dictionary

        Args:
            file_path (Path): filepath of json file

        Returns:
            dict: json as a dictionary
        """
        with open(file_path, 'r') as file:
            first_line = file.readline()
            if first_line.startswith("version https://git-lfs.github.com"):
                raise ValueError(
                    f"{file_path} is a Git LFS pointer, not the actual file. "
                    "Fetch the file via 'git lfs smudge' before comparing."
                )
            file.seek(0)
            return json.load(file)

    @staticmethod
    def load_summary_report(file_path: Path):
        """Read in a summary report

        Args:
            file_path (Path): filepath of summary report xlsx

        Returns:
            pd.DataFrame: summary report DataFrame
        """
        reports = pd.read_excel(file_path, sheet_name=None, index_col=list(range(5)))
        return reports

    def compare_dict_keys(self,
                          dict1: dict,
                          dict2: dict,
                          paths: list,
                          path: str = '',
                          key_diffs: pd.DataFrame = None):
        """Compares nested keys across two dictionaries by recursively searching each level

        Args:
            dict1 (dict): baseline dictionary to compare
            dict2 (dict): new dictionary to compare
            paths (list): paths to the original files from which the dictionaries are imported
            path (str, optional): current dictionary path at which to compare. Defaults to ''.
            key_diffs (pd.DataFrame, optional): existing summary of difference. Defaults to None.

        Returns:
            pd.DataFrame: summary of differences specifying the file, the unique keys, and the
                path that key is found at.
        """
        if key_diffs is None:
            key_diffs = pd.DataFrame(columns=["Results file", "Unique key(s)", "Found at"])
        keys1, keys2 = set(dict1.keys()), set(dict2.keys())
        only_in_dict1 = keys1 - keys2
        only_in_dict2 = keys2 - keys1

        # Write report rows if keys differ
        diff_entries = []
        if only_in_dict1:
            diff_entries.extend([{"Results file": paths[0].as_posix(),
                                  "Unique key(s)": str(list(only_in_dict1)),
                                  "Found at": path[2:]}])
        if only_in_dict2:
            diff_entries.extend([{"Results file": paths[1].as_posix(),
                                  "Unique key(s)": str(list(only_in_dict2)),
                                  "Found at": path[2:]}])
        if diff_entries:
            key_diffs = pd.concat([key_diffs, pd.DataFrame(diff_entries)], ignore_index=True)

        # Recursively call if keys intersect
        for key in keys1 & keys2:
            if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                key_diffs = self.compare_dict_keys(dict1[key],
                                                   dict2[key],
                                                   paths,
                                                   path=f"{path}: {key}",
                                                   key_diffs=key_diffs)

        return key_diffs

    def compare_dict_values(self, dict1, dict2, percent_threshold=10):
        """Compares values across two dictionary by recursively searching keys until identifying
            values at common paths. The percent difference is only reported if the percentage
            meets or exceeds the threshold and one or both values exceed the absolute value
            threshold, which depends on the units of the values.

        Args:
            dict1 (dict): baseline dictionary to compare
            dict2 (dict): new dictionary to compare
            percent_threshold (int, optional): the percent difference threshold at which
                                               differences are reported. Defaults to 10.

        Returns:
            pd.DataFrame: summary of percent differences that meet thresholds
        """
        diff_report = {}
        abs_threshold_map = {"USD": 1000, "MMBtu": 1000, "MMTons": 10}

        # Recursively navigate dicts until finding numeric values at the same location to compare
        def compare_recursive(d1, d2, path="", units=""):
            for key in d1.keys():
                current_path = f"{path}['{key}']"
                units = next((unit for unit in abs_threshold_map.keys() if unit in key), units)
                valid_nums = (int, float)
                if isinstance(d1[key], dict) and key in d2:
                    compare_recursive(d1[key], d2[key], current_path, units)
                elif isinstance(d1.get(key), valid_nums) and isinstance(d2.get(key), valid_nums):
                    val1, val2 = d1[key], d2[key]
                    if val1 == 0:
                        percent_change = float("inf") if val2 != 0 else 0
                    else:
                        percent_change = ((val2 - val1) / val1) * 100
                    abs_threshold = abs_threshold_map.get(units, float("inf"))
                    if (abs(percent_change) >= percent_threshold) and \
                            (abs(val1) >= abs_threshold or abs(val2) >= abs_threshold):
                        diff_report[current_path] = {"base": val1,
                                                     "new": val2,
                                                     "percent_diff": percent_change}

        compare_recursive(dict1, dict2)
        return diff_report

    def split_json_key_path(self, path: str):
        """Parse a string of nested keys found in a results json file

        Args:
            path (str): string of nested keys seperated by brackets

        Returns:
            list: list of individual keys
        """
        keys = re.findall(r"\['(.*?)'\]", path)
        if len(keys) == 5:
            keys[4:4] = [None, None, None]
        return keys

    def write_dict_key_report(self, diff_report: pd.DataFrame, output_path: Path):
        """Writes a dictionary key report to a csv file

        Args:
            diff_report (pd.DataFrame): report with dictionary key differences
            output_path (Path): csv output path
        """
        if diff_report.empty:
            logger.info(f"No key differences found, {output_path} not written")
            return
        diff_report.to_csv(output_path, index=False)
        logger.info(f"Wrote dictionary key report to {output_path}")

    def write_dict_value_report(self, diff_report: pd.DataFrame, output_path: Path):
        """Writes a dictionary value report to a csv file

        Args:
            diff_report (pd.DataFrame): report with dictionary value differences
            output_path (Path): csv output path
        """
        col_headers = [
            "ECM",
            "Markets and Savings Type",
            "Adoption Scenario",
            "Results Scenario",
            "Climate Zone",
            "Building Class",
            "End Use",
            "Year"
        ]
        df = pd.DataFrame(columns=["Results path"], data=list(diff_report.keys()))
        if df.empty:
            logger.info(f"No changes above the threshold found, {output_path} not written")
            return
        split_df = df["Results path"].apply(self.split_json_key_path).apply(pd.Series)

        # Remove on-site generation diffs as it does not fit the results format
        split_df = split_df[split_df[0] != "On-site Generation"]
        if split_df.empty:
            logger.info(f"No changes above the threshold found, {output_path} not written")
            return
        df[col_headers] = split_df
        df["Percent difference"] = [
            round(diff_dict["percent_diff"], 2) for diff_dict in diff_report.values()]
        df["Base value"] = [round(diff_dict["base"], 2) for diff_dict in diff_report.values()]
        df["New value"] = [round(diff_dict["new"], 2) for diff_dict in diff_report.values()]
        df = df.dropna(axis=1, how="all")
        df.to_csv(output_path, index=False)
        logger.info(f"Wrote dictionary value report to {output_path}")

    def compare_jsons(self,
                      json1_path: Path,
                      json2_path: Path,
                      percent_threshold: float,
                      output_dir: Path = None):
        """Compare two jsons and report differences in keys and in values

        Args:
            json1_path (Path): baseline json file to compare
            json2_path (Path): new json file to compare
            percent_threshold (float): threshold for reporting percent difference if values
            output_dir (Path, optional): output directory where comparison reports are saved.
                                         Defaults to None.
        """
        json1 = self.load_json(json1_path)
        json2 = self.load_json(json2_path)

        # Compare differences in json keys
        key_diffs = self.compare_dict_keys(json1, json2, [json1_path, json2_path])
        if output_dir is None:
            output_dir = json2_path.parent
        self.write_dict_key_report(key_diffs, output_dir / f"{json2_path.stem}_key_diffs.csv")

        # Compare differences in json values
        val_diffs = self.compare_dict_values(json1, json2, percent_threshold=percent_threshold)
        self.write_dict_value_report(val_diffs, output_dir / f"{json2_path.stem}_value_diffs.csv")

    def compare_summary_reports(self,
                                report1_path: Path,
                                report2_path: Path,
                                output_dir: Path = None):
        """Compare Summary_Data-TP.xlsx and Summary_Data-MAP.xlsx with baseline files

        Args:
            report1_path (Path): baseline summary report to compare
            report2_path (Path): new summary report to compare
            output_dir (Path, optional): output directory where comparison report is saved.
                                         Defaults to None.
        """
        reports1 = self.load_summary_report(report1_path)
        reports2 = self.load_summary_report(report2_path)
        if output_dir is None:
            output_dir = report2_path.parent
        output_path = output_dir / f"{report2_path.stem}_percent_diffs.xlsx"
        with pd.ExcelWriter(output_path) as writer:
            for (output_type, report1), (_, report2) in zip(reports1.items(), reports2.items()):
                diff = (100 * (report2 - report1)/report1).round(2)
                diff = diff.reset_index()
                diff.to_excel(writer, sheet_name=output_type, index=False)
        logger.info(f"Wrote Summary_Data percent difference report to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Compare results files for Scout.")
    parser.add_argument("--json-baseline", type=Path, help="Path to the baseline JSON file")
    parser.add_argument("--json-new", type=Path, help="Path to the new JSON file")
    parser.add_argument("--summary-baseline", type=Path,
                        help="Path to the baseline summary report (Excel file)")
    parser.add_argument("--summary-new", type=Path,
                        help="Path to the new summary report (Excel file)")
    parser.add_argument("--new-dir", type=Path, help="Directory containing files to compare")
    parser.add_argument("--base-dir", type=Path, help="Directory containing files to compare")
    parser.add_argument("--threshold", type=float, default=10,
                        help="Threshold for percent difference")
    args = parser.parse_args()

    compare = ScoutCompare()
    if args.base_dir and args.new_dir:
        # Compare all files
        base_dir = args.base_dir.resolve()
        new_dir = args.new_dir.resolve()
        agg_json_base = base_dir / "agg_results.json"
        agg_json_new = new_dir / "agg_results.json"
        compare.compare_jsons(agg_json_base,
                              agg_json_new,
                              percent_threshold=args.threshold,
                              output_dir=new_dir)
        ecm_json_base = base_dir / "ecm_results.json"
        ecm_json_new = new_dir / "ecm_results.json"
        compare.compare_jsons(ecm_json_base,
                              ecm_json_new,
                              percent_threshold=args.threshold,
                              output_dir=new_dir)

        summary_tp_base = base_dir / "Summary_Data-TP.xlsx"
        summary_tp_new = new_dir / "plots" / "tech_potential" / "Summary_Data-TP.xlsx"
        compare.compare_summary_reports(summary_tp_base, summary_tp_new, output_dir=new_dir)
        summary_map_base = base_dir / "Summary_Data-MAP.xlsx"
        summary_map_new = new_dir / "plots" / "max_adopt_potential" / "Summary_Data-MAP.xlsx"
        compare.compare_summary_reports(summary_map_base, summary_map_new, output_dir=new_dir)
    else:
        # Compare only as specified by the arguments
        if args.json_baseline and args.json_new:
            compare.compare_jsons(args.json_baseline,
                                  args.json_new,
                                  percent_threshold=args.threshold)
        if args.summary_baseline and args.summary_new:
            compare.compare_summary_reports(args.summary_baseline, args.summary_new)


if __name__ == "__main__":
    main()
