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
        if _ORJSON_AVAILABLE:
            # orjson's decoder is substantially faster than stdlib json for
            # large files (e.g. the multi-hundred-MB baseline/measure data
            # used by run.py).
            try:
                with open(filepath, 'rb') as handle:
                    return _orjson.loads(handle.read())
            except ValueError:
                # orjson needs one large contiguous allocation, which can fail
                # on very large files even when the JSON itself is well-formed
                # (e.g. "not enough memory to allocate buffer for parsing").
                # Fall back to stdlib's incremental parser, which tolerates
                # tight memory better despite being slower.
                pass
        with open(filepath, 'r') as handle:
            try:
                data = json.load(handle)
            except ValueError as e:
                raise ValueError(f"Error reading in '{filepath}': {str(e)}") from None
        return data

    @staticmethod
    def loads_bytes(data):
        """Parse JSON from an in-memory bytes/str payload (e.g., decompressed gzip content).

        Args:
            data: JSON payload as bytes, bytearray, or str.

        Returns:
            Parsed JSON data.
        """
        if _ORJSON_AVAILABLE:
            try:
                return _orjson.loads(data)
            except ValueError as e:
                raise ValueError(f"Error parsing JSON data: {str(e)}") from None
        if isinstance(data, (bytes, bytearray)):
            data = data.decode('utf-8')
        try:
            return json.loads(data)
        except ValueError as e:
            raise ValueError(f"Error parsing JSON data: {str(e)}") from None

    @staticmethod
    def dump_json(data, filepath: Path, indent: bool = False):
        """Export data to .json file

        Args:
            data: data to write to .json file
            filepath (pathlib.Path): filepath of .json file
            indent (bool, optional): pretty-print with 2-space indentation.
                Defaults to False (compact output) since most callers write
                multi-hundred-MB generated result files that nothing reads
                for human readability, and indentation adds meaningful
                CPU/memory cost at that size. Pass True for small, hand-
                curated/reviewed files (e.g. supporting_data references)
                where staying diffable in git matters more than write speed.
        """
        if _ORJSON_AVAILABLE:
            # orjson is 5-10x faster than stdlib json for numeric-heavy data.
            # It natively serialises numpy scalars/arrays and does not require
            # a custom encoder. We request non-string keys (e.g. integer year
            # keys) to be serialised.
            option = _orjson.OPT_NON_STR_KEYS
            if indent:
                option |= _orjson.OPT_INDENT_2
            raw = _orjson.dumps(data, option=option, default=_orjson_default)
            Path(filepath).write_bytes(raw)
        else:
            with open(filepath, "w") as handle:
                json.dump(data, handle, indent=2 if indent else None, cls=MyEncoder)


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
