import json
import numpy
import logging
from pathlib import Path, PurePath

try:
    import orjson as _orjson
    _ORJSON_AVAILABLE = True
except ImportError:
    _ORJSON_AVAILABLE = False


def _orjson_default(obj):
    """Fallback serializer for orjson: handles PurePath, numpy arrays, and numpy scalars."""
    if isinstance(obj, PurePath):
        return str(obj)
    if isinstance(obj, numpy.ndarray):
        return obj.tolist()
    if isinstance(obj, numpy.integer):
        return int(obj)
    if isinstance(obj, numpy.floating):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


class JsonIO:
    @staticmethod
    def load_json(filepath: Path) -> dict:
        """Loads data from a .json file

        Args:
            filepath (pathlib.Path): filepath of .json file

        Returns:
            dict: .json data as a dict
        """
        with open(filepath, 'r') as handle:
            try:
                data = json.load(handle)
            except ValueError as e:
                raise ValueError(f"Error reading in '{filepath}': {str(e)}") from None
        return data

    @staticmethod
    def dump_json(data, filepath: Path):
        """Export data to .json file

        Args:
            data: data to write to .json file
            filepath (pathlib.Path): filepath of .json file
        """
        if _ORJSON_AVAILABLE:
            # orjson is 5-10x faster than stdlib json for numeric-heavy data.
            # It natively serialises numpy scalars/arrays and does not require
            # a custom encoder.  We request non-string keys (e.g. integer year
            # keys) to be serialised and pretty-print with 2-space indent to
            # stay consistent with the previous output format.
            raw = _orjson.dumps(
                data,
                option=_orjson.OPT_NON_STR_KEYS,
                default=_orjson_default,
            )
            Path(filepath).write_bytes(raw)
        else:
            with open(filepath, "w") as handle:
                json.dump(data, handle, indent=2, cls=MyEncoder)


class MyEncoder(json.JSONEncoder):
    """Convert numpy arrays to list for JSON serializing."""

    def default(self, obj):
        """Modify 'default' method from JSONEncoder."""
        # Case where object to be serialized is numpy array
        if isinstance(obj, numpy.ndarray):
            return obj.tolist()
        if isinstance(obj, PurePath):
            return str(obj)
        # All other cases
        else:
            return super(MyEncoder, self).default(obj)


class PrintFormat:
    """Class for customizing print messages."""

    @staticmethod
    def custom_showwarning(message, category, filename, lineno, file=None, line=None):
        """Define a custom warning message format."""
        # Other message details suppressed because error location and type are not relevant
        print(message)

    @staticmethod
    def verboseprint(verbose, msg, log_type, logger=None):
        """Print input message when the code is run in verbose mode.

        Args:
            verbose (boolean): Indicator of verbose mode
            msg (string): Message to print to console when in verbose mode
            logger: Logger instance to use for logging
        """
        if not verbose:
            return
        if not logger:
            logger = logging.getLogger(__name__)

        if log_type == "info":
            logger.info(msg)
        elif log_type == "warning":
            logger.warning(msg)
        elif log_type == "error":
            logger.error(msg)

    @staticmethod
    def format_console_list(list_to_format):
        return [f"  {elem}\n" for elem in list_to_format]
