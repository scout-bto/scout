from __future__ import annotations
from pathlib import Path
from argparse import ArgumentParser
from scout.config import FilePaths as fp
import io
import sys
import logging
import cProfile
import pstats

sys.path.append(str(Path(__file__).parent.parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))
from scout import ecm_prep, run  # noqa: E402
from scout.ecm_prep_args import ecm_args  # noqa: E402
from scout.config import LogConfig  # noqa: E402

LogConfig.configure_logging()
logger = logging.getLogger(__name__)


def run_workflow(config: str = "", run_step: str = None, with_profiler: bool = False) -> None:
    """Runs Scout workflow steps with optional profiling

    Args:
        config (str, optional): Path to yml config file
        run_step (str, optional): Specify which step to run {ecm_prep, run}, if None
                                  then both run. Defaults to None.
        with_profiler (Bool, optional): Run workfow step(s) with profiler to track
                                        compute time and peak memory. Defaults to False.
    """

    # Run ecm_prep.py
    if run_step == "ecm_prep" or run_step is None:
        opts = ecm_args(["-y", config])
        if with_profiler:
            run_with_profiler(ecm_prep.main, opts, fp.RESULTS / "profile_ecm_prep.csv")
        else:
            ecm_prep.main(opts)

    # Run run.py
    if run_step == "run" or run_step is None:
        opts = run.parse_args(["-y", config])
        if with_profiler:
            run_with_profiler(run.main, opts, fp.RESULTS / "profile_run.csv")
        else:
            run.main(opts)


def run_with_profiler(
    func: Callable[[argparse.Namespace], None],  # noqa: F821
    args: argparse.Namespace,  # noqa: F821
    output_file: pathlib.Path,  # noqa: F821
) -> None:
    """Runs a function wrapped in a profiler using the cProfile library, writes profile stats

    Args:
        func (Callable[[argparse.Namespace], None]): A function that takes argsparse.Namespace args
        args (argparse.Namespace): The arguments to the function
        output_file (pathlib.Path): .csv filepath to write profiling stats
    """

    pr = cProfile.Profile()
    pr.enable()
    func(args)
    pr.disable()
    write_profile_stats(pr, output_file)


def write_profile_stats(pr: cProfile.Profile, filepath: pathlib.Path) -> None:  # noqa: F821
    """Writes profile stats and stores a .csv file

    Args:
        pr (cProfile.Profile): Profile instance that has previously been enabled (pr.enable())
        filepath (pathlib.Path): .csv filepath to write profiling stats
    """

    # Capture io stream
    result = io.StringIO()
    pstats.Stats(pr, stream=result).sort_stats("cumulative").print_stats()
    result = result.getvalue()

    # Parse stats and write to csv
    top_data, result = result.split("ncalls")
    top_data = "\n".join([line.strip() for line in top_data.split("\n")])
    result = "ncalls" + result
    result = "\n".join([",".join(line.rstrip().split(None, 5)) for line in result.split("\n")])
    result_out = top_data + result

    f = open(filepath, "w")
    f.write(result_out)
    f.close()
    logger.info(f"Wrote profiler stats to {filepath}")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--run_step", choices=["ecm_prep", "run"], required=False, help="Specify which step to run"
    )
    parser.add_argument(
        "--with_profiler",
        action="store_true",
        required=False,
        help="Run workflow step(s) with profiler",
    )
    parser.add_argument(
        "-y", "--yaml",
        type=str,
        help=("Path to YAML configuration file")
    )
    opts = parser.parse_args()
    run_workflow(config=opts.yaml, run_step=opts.run_step, with_profiler=opts.with_profiler)
