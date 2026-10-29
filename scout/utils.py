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


def check_fraction_sums(entries, source, scenario, wild=(), tol=1e-4, max_report=10):
    """Raise a ValueError if partial-coverage fractions overlap to sum to more than 1.

    Rows with an applicable fraction of 1 (e.g., state-wide policies) are exempt, as are rows
    with a fraction of 0. Among the remaining rows, the fractions of all rows that share a segment
    and are active in the same year must sum to at most 1. Rows with an identical fraction are
    counted once, since the model treats them as tiers of one policy applied to one population.
    Rows that carry a jurisdiction are stages of one policy instead: only the stage with the
    latest start year counts (fractions are cumulative), and distinct jurisdictions are summed.
    Rows of type 'state' are statewide targets that already include any local programs in the
    segment, so the segment total is the larger of the state target and the sum of the other rows.

    Args:
        entries (list): Tuples of (segment key tuple, start year, end year, fraction, origin) with
            an optional sixth element, the jurisdiction (None or absent if not tagged), and an
            optional seventh, the policy type ('state' or 'local'/None). Blank start/end years
            may be None or False (treated as open-ended).
        source (str): Name of the input file, for the error message.
        scenario (str): Name of the scenario being checked, for the error message.
        wild (tuple): Indices in the segment key where "all" overlaps with any other value.
        tol (float): Tolerance on the sum.
        max_report (int): Maximum number of violations to describe in the message.
    """
    inf = float("inf")
    # Tagged rows are kept at any fraction so that a later full or zero stage retires earlier ones
    part = [(e[0], e[1] or -inf, e[2] or inf, float(e[3]), e[4], e[5] if len(e) > 5 else None,
             e[6] if len(e) > 6 else None)
            for e in entries if (len(e) > 5 and e[5] is not None) or 0 < float(e[3]) < 1]

    def overlap(a, b):
        # Whether two segment keys cover some of the same buildings ('wild' fields match 'all')
        return all(x == y or (i in wild and "all" in (x, y)) for i, (x, y) in enumerate(zip(a, b)))

    def yrs(x):
        # Year as text for the message; open-ended bounds print as blank
        return "" if abs(x) == inf else str(int(x))

    def counted(act):
        # Rows that count toward the sum: untagged rows, plus the latest stage of each jurisdiction
        out = [e for e in act if e[5] is None]
        for jur in dict.fromkeys(e[5] for e in act if e[5] is not None):
            stages = [e for e in act if e[5] == jur]
            last = max(e[1] for e in stages)
            top = max((e for e in stages if e[1] == last), key=lambda e: e[3])
            if 0 < top[3] < 1:
                out.append(top)
        return out

    def total(rows):
        # State targets include the local programs, so they replace (not add to) the rest
        state = max([e[3] for e in rows if e[6] == "state"], default=0)
        other = (sum({round(e[3], 4) for e in rows if e[5] is None and e[6] != "state"}) +
                 sum(e[3] for e in rows if e[5] is not None and e[6] != "state"))
        return max(state, other)

    # Test each distinct segment key against every row that overlaps it. Group violations with
    # the same years/fractions/origins (e.g., one policy exploded across
    # fuels or end uses) so that each distinct problem is reported once
    found = {}
    for seg in sorted({e[0] for e in part}, key=str):
        rows = [e for e in part if overlap(e[0], seg)]
        # A lone row cannot overlap with anything
        if len(rows) < 2:
            continue
        # Active rows only gain members at start years, so these are the only years to test
        for yr in sorted({e[1] for e in rows}):
            act = counted([e for e in rows if e[1] <= yr <= e[2]])
            if total(act) > 1 + tol:
                # Signature of the offending rows; segments sharing it are reported together
                sig = tuple(sorted(
                    (e[1], e[2], e[3], str(e[4]), str(e[5]), str(e[6])) for e in act))
                grp = found.setdefault((yr, sig), {"act": act, "segs": []})
                if seg not in grp["segs"]:
                    grp["segs"].append(seg)
    if not found:
        return
    # Describe up to max_report problem groups, one line each
    lines = []
    for (yr, _), grp in list(found.items())[:max_report]:
        # Collapse repeated identical rows (e.g., one policy exploded across fuels) into 'x N'
        counts = {}
        for e in grp["act"]:
            counts.setdefault((round(e[3], 4), e[4], e[1], e[2], e[5], e[6]), [e, 0])[1] += 1
        parts = " + ".join("{:g} ({}, {}-{}{}{}){}".format(
            e[3], e[4], yrs(e[1]), yrs(e[2]), ", " + str(e[5]) if e[5] is not None else "",
            ", state" if e[6] == "state" else "", " x{}".format(n) if n > 1 else "")
            for e, n in counts.values())
        # Join the distinct values of each segment field across the grouped segments with '|'
        seg_txt = tuple("|".join(dict.fromkeys(str(s[i]) for s in grp["segs"]))
                        for i in range(len(grp["segs"][0])))
        lines.append("  - segment {} (from {}): {} -> counts as {:.4g}".format(
            seg_txt, yrs(yr) or "start of file", parts, total(grp["act"])))
    more = len(found) - max_report
    # Fail with a message that lists the problem rows and explains the counting rules
    raise ValueError(
        "Invalid {} input for scenario '{}': applicable fractions below 1 overlap in {} "
        "segment group(s) and sum to more than 1. Fractions below 1 that cover the same "
        "segment and years must sum to at most 1 (rows with fraction 1 are exempt, rows with "
        "identical fractions count once as tiers of one policy, and rows with the same "
        "jurisdiction are cumulative stages of one policy of which only the latest counts; "
        "a state-type target replaces, rather than adds to, the other rows); "
        "revise the fractions or years of the rows listed (each shown as fraction (scenario, "
        "start-end[, jurisdiction][, state]); 'a|b' means the same overlap applies to each listed "
        "value of that field):\n{}{}".format(
            source, scenario, len(found), "\n".join(lines),
            "\n  ... and {} more".format(more) if more > 0 else ""))


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
