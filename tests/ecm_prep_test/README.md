# ECM Prep Test Suite

This directory contains pytest-based tests for the Scout ECM preparation module, refactored from the original monolithic `ecm_prep_test.py` file (130,412 lines).

## Test Status Summary

**✅ All Tests Passing: 49 passed, 0 xfailed**

### Test Files (49 total tests)

- `market_updates_tests/` - **20 passed** - 560 lines (Market fill_mkts function - modular structure) - **94% reduction**:
  - `base_segmentation_test.py` - **6 tests**
  - `regional_variants_test.py` - **3 tests**
  - `fuel_energy_features_test.py` - **4 tests**
  - `emissions_test.py` - **2 tests**
  - `costs_incentives_test.py` - **2 tests**
  - `edge_cases_test.py` - **3 tests**
- `merge_measuresand_apply_benefits_test.py` - **5 passed** - 560 lines (Measure merging and packaging) - **84% reduction**
- `update_measures_test.py` - **4 passed** - 900 lines (Update results function) - **98% reduction**
- `partition_microsegment_test.py` - **2 passed** - 922 lines (Microsegment partitioning) - **76% reduction**
- `time_sensitive_valuation_test.py` - **1 passed** - 245 lines (TSV calculations) - **99.5% reduction**
- `add_key_vals_test.py` - **3 passed** (Add key values function)
- `cost_conversion_test.py` - **3 passed** (Cost conversion)
- `create_key_chain_test.py` - **2 passed** (Key chain creation)
- `div_key_vals_float_test.py` - **2 passed** (Divide key values float)
- `append_key_vals_test.py` - **1 passed** (Append key values function)
- `check_markets_test.py` - **1 passed** (Market validation)
- `clean_up_test.py` - **1 passed** (Result cleanup)
- `div_key_vals_test.py` - **1 passed** (Divide key values)
- `fill_parameters_test.py` - **1 passed** (Parameter filling)
- `yr_map_test.py` - **1 passed** (Year mapping)
- `state_import_test.py` - **1 passed** (State import)

## Directory Structure

```
tests/ecm_prep_test/
├── __init__.py                                # Package marker
├── README.md                                  # This file
├── common.py                                  # Shared fixtures and helpers (dict_check, NullOpts)
│
├── # Test Files (pytest format, 49 tests - all passing!)
├── add_key_vals_test.py                      # 3 tests passing
├── append_key_vals_test.py                   # 1 test passing
├── check_markets_test.py                     # 1 test passing
├── clean_up_test.py                          # 1 test passing
├── cost_conversion_test.py                   # 3 tests passing
├── create_key_chain_test.py                  # 2 tests passing
├── div_key_vals_float_test.py                # 2 tests passing
├── div_key_vals_test.py                      # 1 test passing
├── fill_parameters_test.py                   # 1 test passing
├── market_updates_tests/                     # 20 tests passing (modular structure)
│   ├── conftest.py                           # Shared fixture for all market tests
│   ├── base_segmentation_test.py             # 6 tests - Base market segmentation
│   ├── regional_variants_test.py             # 3 tests - Regional variants (EMM, State, regadj)
│   ├── fuel_energy_features_test.py          # 4 tests - Fuel switching & HP measures
│   ├── emissions_test.py                     # 2 tests - Emissions (methane & refrigerant)
│   ├── costs_incentives_test.py              # 2 tests - Incentives & electrical upgrades
│   └── edge_cases_test.py                    # 3 tests - Error handling & special cases
├── merge_measuresand_apply_benefits_test.py  # 5 tests passing
├── partition_microsegment_test.py            # 2 tests passing
├── state_import_test.py                      # 1 test passing
├── time_sensitive_valuation_test.py          # 1 test passing
├── update_measures_test.py                   # 4 tests passing
├── yr_map_test.py                            # 1 test passing
│
└── test_data/                                 # Refactored test data (modular structure)
    ├── __init__.py                            # Package marker
    │
    ├── market_updates_test_data/              # Market updates test data (31 variables)
    │   ├── ok_tpmeas_fullchk_break_out.py     # Tech potential full check breakout
    │   ├── ok_tpmeas_fullchk_competechoiceout.py  # Consumer choice output
    │   ├── ok_tpmeas_fullchk_msegout.py       # Full check microseg output
    │   ├── ok_tpmeas_fullchk_supplydemandout.py   # Supply/demand output
    │   ├── ok_tpmeas_partchk_msegout.py       # Partial check microseg output
    │   ├── ok_tpmeas_partchk_msegout_emm.py   # EMM partial check output
    │   ├── ok_tpmeas_partchk_msegout_state_regadj.py # State partial check output
    │   ├── ok_tpmeas_partchk_msegout_state.py # State partial check output    
    │   ├── sample_cpl_in.py                   # Competition data
    │   ├── sample_cpl_in_emm.py               # EMM region competition data
    │   ├── sample_cpl_in_state.py             # State-level competition data
    │   ├── sample_mseg_in.py                  # Microsegment input data
    │   ├── sample_mseg_in_emm.py              # EMM microsegment data
    │   ├── sample_mseg_in_state.py            # State microsegment data
    │   └── warnmeas_in.py                     # Warning test measures
    │
    ├── merge_measuresand_apply_benefits_test_data/  # Merge measures test data (6 variables)
    │   ├── __init__.py                        # Auto-imports all variables
    │   ├── breaks_ok_out_test1.py             # Expected output breaks data
    │   ├── contrib_ok_out_test1.py            # Expected contributing measures data
    │   ├── markets_ok_out_test1.py            # Expected markets output data
    │   ├── sample_measures_in_env_costs.py    # Sample measures for envelope costs
    │   ├── sample_measures_in_mkts.py         # Sample measures for market testing
    │   └── sample_measures_in_sect_shapes.py  # Sample measures for sector shapes
    │
    ├── partition_microsegment_test_data/      # Partition microsegment test data (8 variables)
    │   ├── __init__.py                        # Auto-imports all variables
    │   ├── ok_out.py                          # Standard output
    │   ├── ok_out_bad_string.py               # Bad string test output
    │   ├── ok_out_bad_values.py               # Bad values test output
    │   ├── ok_out_bass.py                     # Bass diffusion output
    │   ├── ok_out_bass_string.py              # Bass string output
    │   ├── ok_out_fraction.py                 # Fraction retrofit rate output
    │   ├── ok_out_fraction_string.py          # Fraction string output
    │   └── ok_out_wrong_name.py               # Wrong name test output
    │
    ├── time_sensitive_valuation_test_data/    # TSV test data (8 variables)
    │   ├── __init__.py                        # Auto-imports all variables
    │   ├── ok_tsv_facts_out_features_raw.py   # Expected features output
    │   ├── ok_tsv_facts_out_metrics_raw.py    # Expected metrics output
    │   ├── sample_cost_convert.py             # Building type conversions
    │   ├── sample_tsv_data.py                 # Main TSV load shape data
    │   ├── sample_tsv_data_update_measures.py # Update measures TSV data
    │   ├── sample_tsv_measure_in_metrics.py   # Metrics test measures
    │   └── sample_tsv_measures_in_features.py # Feature test measures
    │
    └── update_measures_test_data/             # Update measures test data (10 variables)
        ├── __init__.py                        # Auto-imports all variables
        ├── base_out_2009.py                   # Baseline output 2009
        ├── base_out_2010.py                   # Baseline output 2010
        ├── ok_tpmeas_partchk_msegout.py       # Partial check microseg output
        ├── ok_tpmeas_partchk_msegout_emm.py   # EMM partial check output
        ├── ok_tpmeas_partchk_msegout_state.py # State partial check output
        ├── sample_cpl_in.py                   # Competition data
        ├── sample_cpl_in_emm.py               # EMM region competition data
        ├── sample_cpl_in_state.py             # State-level competition data
        ├── sample_mseg_in_emm.py              # EMM microsegment data
        └── sample_mseg_in_state.py            # State microsegment data
```

## Achievements

### Successful Migration & Refactoring

- ✅ **100% test coverage maintained** - All 49 functional tests passing
- ✅ **Converted from unittest to pytest** - Modern testing framework
- ✅ **Refactored test data structure** - Modular folder-based organization

### File Size Reductions

| File | Original Lines | After Refactor | Reduction | Additional Notes |
|------|----------------|----------------|-----------|------------------|
| market_updates - Full Suite | 19,935 | ~1,220 (6 files) | **94%** | Split into 6 focused test files + conftest |
| time_sensitive_valuation_test.py | 44,698 | 245 | **99.5%** | — |
| update_measures_test.py | 55,717 | 900 | **98%** | — |
| merge_measuresand_apply_benefits_test.py | 3,506 | 560 | **84%** | — |
| partition_microsegment_test.py | 3,883 | 922 | **76%** | — |


## Running Tests

### Run all tests
```bash
pytest tests/ecm_prep_test/ -v
```

Expected output: `49 passed` ✅

### Run specific test file
```bash
# Market updates tests (all 20 tests in modular structure)
pytest tests/ecm_prep_test/market_updates_tests/ -v

# Specific market updates test file
pytest tests/ecm_prep_test/market_updates_tests/base_segmentation_test.py -v

# Other test files
pytest tests/ecm_prep_test/time_sensitive_valuation_test.py -v
```

## Migration from unittest to pytest

### Key Changes

1. **Test Classes → Functions**: Converted class-based tests to function-based tests
2. **setUpClass → Fixtures**: Module-scoped pytest fixtures replace class setup
3. **Assertions**: `self.assertEqual()` → `assert ==`, `self.assertTrue()` → `assert`
4. **Data Extraction**: Large inline data moved to separate modules in `test_data/`
5. **Removed unittest imports**: No longer depend on `unittest.TestCase`

### Common Patterns

**Before (unittest):**
```python
class MyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = {...}

    def test_something(self):
        self.assertEqual(result, self.data)
```

**After (pytest):**
```python
@pytest.fixture(scope="module")
def test_data():
    data = {...}
    return {"data": data}

def test_something(test_data):
    assert result == test_data["data"]
```

## Test Data Organization

Test data has been refactored into a **modular folder structure** for improved maintainability. Each test data module is now a folder containing individual variable files.

### Structure

Each test data folder follows this pattern:
```
test_data_folder/
├── __init__.py          # Auto-imports all variables for backward compatibility
├── _helpers.py          # Shared helper functions (if needed)
├── variable1.py         # Individual variable definition
├── variable2.py
└── ...
```

## References

- Original file: `tests/ecm_prep_test.py` (retained for reference)
- pytest documentation: https://docs.pytest.org/
- Scout ECM module: `scout/ecm_prep.py`
