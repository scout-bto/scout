"""Validate the results/plots folder structure against results_schema.json.

The schema in docs/results_schema.json defines the expected structure of the
PDF figures that run.py writes to ./results/plots. A run writes only the PDFs,
not a JSON file listing the figures it actually produced, so these tests build
that listing from the plots folder (adoption scenario folder -> metric folder
-> figure file names) and validate it against the schema. The integration
testing workflow commits its plots output to
tests/integration_testing/results/plots, which is used here.

Figure contents (panels, titles, axis labels) are described in the schema but
are not checked here, since they are only available inside the PDFs.
"""

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft7Validator


# ============================================================================
# Constants
# ============================================================================

REPO_ROOT = Path(__file__).parent.parent
SCHEMA_PATH = REPO_ROOT / "docs" / "results_schema.json"
PLOTS_DIR = REPO_ROOT / "tests" / "integration_testing" / "results" / "plots"

# Adoption scenario folders and the tags used in their figure file names
SCENARIO_TAGS = {"max_adopt_potential": "MAP", "tech_potential": "TP"}

# Metric folders and the metric names used in their figure file names
METRIC_NAMES = {
    "energy": {"Energy", "Energy Savings"},
    "co2": {"CO2", "Avoided CO2"},
    "cost": {"Cost", "Cost Savings", "Operation Cost Savings"},
}


# ============================================================================
# Helpers
# ============================================================================

def figure_key(file_name):
    """Return the schema key for a figure file name, or None if unknown."""
    if file_name.endswith("-byECM.pdf"):
        return "byECM"
    if file_name.endswith("-Aggregate.pdf"):
        return "Aggregate"
    if file_name.startswith("Cost Effective "):
        return "CostEffective"
    return None


def figure_metric_and_tag(file_name):
    """Split a figure file name into its metric name and scenario tag.

    For example, 'Total Energy Savings-MAP-Aggregate.pdf' returns
    ('Energy Savings', 'MAP') and 'Cost Effective Avoided CO2-TP.pdf'
    returns ('Avoided CO2', 'TP').
    """
    stem = file_name[:-len(".pdf")]
    for suffix in ("-byECM", "-Aggregate"):
        if stem.endswith(suffix):
            stem = stem[:-len(suffix)]
    name, tag = stem.rsplit("-", 1)
    for prefix in ("Total ", "Cost Effective "):
        if name.startswith(prefix):
            name = name[len(prefix):]
    return name, tag


def build_instance(plots_dir):
    """Describe a plots folder as a JSON instance of the results schema.

    Returns the instance and a list of unexpected PDF files: those that do
    not correspond to any figure in the schema, and any second figure of the
    same kind in one metric folder.
    """
    instance, unexpected = {}, []
    for scenario_dir in sorted(p for p in plots_dir.iterdir() if p.is_dir()):
        scenario = {}
        for metric_dir in sorted(p for p in scenario_dir.iterdir() if p.is_dir()):
            figures = {}
            for pdf in sorted(metric_dir.glob("*.pdf")):
                key = figure_key(pdf.name)
                if key is None or key in figures:
                    unexpected.append(pdf.relative_to(plots_dir))
                else:
                    figures[key] = {"file": pdf.name}
            scenario[metric_dir.name] = figures
        instance[scenario_dir.name] = scenario
    return instance, unexpected


def error_messages(validator, instance):
    """Return readable messages for all schema validation errors."""
    return [
        f"{'/'.join(str(p) for p in err.absolute_path) or '<root>'}: {err.message}"
        for err in sorted(validator.iter_errors(instance), key=str)
    ]


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def schema():
    """Load the results plots schema."""
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def validator(schema):
    """Return a validator for the results plots schema."""
    return Draft7Validator(schema)


@pytest.fixture(scope="module")
def plots_instance():
    """Build the schema instance from the integration test plots output."""
    assert PLOTS_DIR.is_dir(), f"Plots output not found at {PLOTS_DIR}"
    return build_instance(PLOTS_DIR)


# ============================================================================
# Tests
# ============================================================================

def test_schema_is_valid(schema):
    """The schema itself is a valid draft-07 JSON Schema."""
    Draft7Validator.check_schema(schema)


def test_plots_match_schema(validator, plots_instance):
    """The plots folder has the required folders and figure file names."""
    instance, _ = plots_instance
    errors = error_messages(validator, instance)
    assert not errors, "Plots do not match results_schema.json:\n" + "\n".join(errors)


def test_no_unexpected_figures(plots_instance):
    """Every PDF is a figure described by the schema, with one of each kind."""
    _, unexpected = plots_instance
    assert not unexpected, (
        f"PDFs not described by results_schema.json or duplicated: {unexpected}")


def test_figures_are_in_matching_folders(plots_instance):
    """Each figure's file name matches its scenario and metric folders.

    The schema's file name patterns accept any metric and scenario tag, so
    this checks that, e.g., 'Total CO2-MAP-byECM.pdf' is in the co2 folder
    of max_adopt_potential and not elsewhere.
    """
    instance, _ = plots_instance
    mismatches = []
    for scenario, metrics in instance.items():
        for metric, figures in metrics.items():
            for key, figure in figures.items():
                name, tag = figure_metric_and_tag(figure["file"])
                if SCENARIO_TAGS.get(scenario) != tag:
                    mismatches.append(f"{scenario}/{metric}/{figure['file']}: scenario tag")
                if name not in METRIC_NAMES.get(metric, set()):
                    mismatches.append(f"{scenario}/{metric}/{figure['file']}: metric")
    assert not mismatches, "Figures in the wrong folder:\n" + "\n".join(mismatches)


@pytest.mark.parametrize(
    "change, description",
    [
        (lambda i: i["max_adopt_potential"]["energy"].pop("byECM"),
         "missing figure"),
        (lambda i: i["tech_potential"].pop("co2"), "missing metric folder"),
        (lambda i: i["max_adopt_potential"]["cost"]["Aggregate"].update(
            file="Total Cost Savings-MAP-Aggregate.png"), "wrong file extension"),
        (lambda i: i["tech_potential"]["energy"]["CostEffective"].update(
            file="Cost Effective Energy-TP.pdf"), "unexpected figure name"),
        (lambda i: [i.pop(k) for k in list(i)], "no scenario folders"),
    ],
    ids=lambda x: x if isinstance(x, str) else "",
)
def test_schema_rejects_bad_plots(validator, plots_instance, change, description):
    """The schema catches broken plots output, so the checks above are not vacuous."""
    instance = copy.deepcopy(plots_instance[0])
    change(instance)
    assert error_messages(validator, instance), f"Schema accepted {description}"
