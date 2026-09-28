"""Convert BTB performance metrics into the units used in bss_meas_v2.xlsx.

BTB reports a technology's primary performance metric under the
"Regression metric {1,2} - Metric" column (e.g. "SEER1", "AFUE", "EER",
"Heating COP", "UEF"), with an accompanying "... - Unit" column that is
often just "Unitless" or "Btu/W" rather than the metric name itself -- so
matching must key off the *metric name*, not the unit string.

Within `meas_in`, "COP", "AFUE", and "BTU out/BTU in" are all the same
underlying dimensionless output/input energy ratio -- just labeled
differently depending on which row/end-use they show up in (a row mixing
combustion and compression equipment, e.g. a gas boiler + electric
chiller package, labels both "BTU out/BTU in" even though one behaves
like an AFUE and the other like a COP). This mirrors Scout's own
unit-conversion table for ECM performance data (`HandyVars.tech_units_map`
in scout/ecm_prep_vars.py), which treats AFUE as numerically equivalent to
COP (`"AFUE": {"COP": 1}`) and establishes that SEER/EER/CEER/HSPF-type
metrics -- expressed in Btu of output per watt-hour of input -- convert to
that same dimensionless ratio by dividing by 3.412 (Btu/hr per W; see
`"EER": {"COP": 3.412}` there). That Btu/Wh relationship holds regardless
of the specific metric's name (SEER, SEER2, EER, CEER, HSPF, HSPF2 are all
seasonal or point-in-time variants of the same Btu/Wh basis), so one
conversion factor covers all of them here.

Because the target unit is whatever the destination `meas_in` cell already
uses (not a fixed label per technology), `convert()` takes that target
unit explicitly rather than deciding one itself.

BTB itself reports AFUE on a 0-100 percentage scale (e.g. Typical = 90.0
for a gas furnace, confirmed against raw BTB residential data for
Technology ID 91), while `meas_in` stores it as a 0-1 fraction (e.g. 0.9)
-- this is unrelated to the AFUE/COP unit-label equivalence above and is
handled separately (see PERCENT_METRICS).

Only metrics actually observed in the BTB rows relevant to the
BTB-covered `meas_in` categories (HVAC, Water Heating, Lighting,
Refrigeration, Cooking) are included. Anything not listed here is left for
build_tech_crosswalk.py to flag `needs_review` rather than guessed at.
"""

# Btu of cooling/heating output per watt-hour of electrical input ->
# dimensionless ratio. Source: scout/ecm_prep_vars.py
# HandyVars.tech_units_map ("EER": {"COP": 3.412}).
BTU_PER_WH_TO_RATIO = 3.412

# meas_in unit labels that are all the same dimensionless output/input
# energy ratio (see module docstring).
RATIO_UNIT_LABELS = {"cop", "afue", "btu out/btu in"}

# BTB "Regression metric - Metric" names reported in Btu/Wh (seasonal or
# point-in-time) that convert to the ratio labels above by dividing by
# BTU_PER_WH_TO_RATIO.
BTU_PER_WH_METRICS = {
    "seer", "seer1", "seer2", "eer", "ceer", "hspf", "hspf2",
}

# BTB "Regression metric - Metric" names that are already a dimensionless
# ratio (0-1-ish scale, e.g. a COP) and need no conversion to reach a
# ratio-labeled target unit.
RATIO_METRICS = {"heating cop", "cooling cop"}

# BTB "Regression metric - Metric" names reported as a 0-100 percentage
# (e.g. AFUE Typical value of 90, meaning 90%) that meas_in instead stores
# as a 0-1 fraction -- confirmed against the raw BTB residential furnace
# data (Technology ID 91, "AFUE" Typical = 90.0).
PERCENT_METRICS = {"afue"}

# BTB metric name -> meas_in unit label, for metrics with their own
# dedicated (non-ratio) unit that BTB and meas_in both use as-is.
DIRECT_PASSTHROUGH_METRICS = {
    "uef": "UEF", "sef": "UEF", "suef": "UEF", "cef": "CEF",
    "efficacy": "lm/W",
}


def normalize(name):
    """Lowercase/strip a metric or unit string for lookup."""

    if not isinstance(name, str):
        return None
    return name.strip().lower()


def convert(metric_name, target_unit, value):
    """Convert a BTB performance value into a specific meas_in unit.

    Args:
        metric_name (str): Raw value from a BTB "Regression metric -
            Metric" column (e.g. "SEER1", "Heating COP").
        target_unit (str): The unit label already used in the destination
            meas_in cell (e.g. "COP", "AFUE", "BTU out/BTU in", "UEF").
        value (float): The BTB performance value (e.g. a Typical/Lower
            Bound/Upper Bound regression output) to convert.

    Returns:
        The converted value (float), or None if no conversion rule is
        known for this metric/target-unit pair -- callers should treat
        that case as needing manual review rather than assuming a
        passthrough.
    """

    metric = normalize(metric_name)
    target = normalize(target_unit)
    if metric is None or target is None:
        return None

    try:
        value = float(value)
    except (TypeError, ValueError):
        return None

    if target in RATIO_UNIT_LABELS:
        if metric in BTU_PER_WH_METRICS:
            return value / BTU_PER_WH_TO_RATIO
        if metric in RATIO_METRICS:
            return value
        if metric in PERCENT_METRICS:
            return value / 100
        return None

    if metric in DIRECT_PASSTHROUGH_METRICS and \
            DIRECT_PASSTHROUGH_METRICS[metric].lower() == target:
        return value

    return None
