import json
import logging
from pathlib import Path

import pytest

from scout import converter, state_baseline_data_updater, cambium_updater


def mute_backoff_logger():
    backoff_logger = logging.getLogger('backoff')
    previous_level = backoff_logger.level
    backoff_logger.setLevel(logging.CRITICAL)
    return backoff_logger, previous_level


def test_resolve_output_path_uses_output_dir_when_no_existing_file(tmp_path):
    output_path = state_baseline_data_updater.resolve_output_path(None, "2025", tmp_path)

    assert output_path == tmp_path / "EIA_State_Emissions_Prices_Baselines_2025.csv"


def test_validate_conversion_file_name_accepts_supported_inputs():
    assert (
        converter.validate_conversion_file_name("emm_region_emissions_prices.json")
        == "regional"
    )
    assert (
        converter.validate_conversion_file_name("site_source_co2_conversions.json")
        == "national"
    )


def test_validate_conversion_file_name_rejects_unknown_inputs():
    with pytest.raises(ValueError, match="expected conversion file"):
        converter.validate_conversion_file_name("unexpected_file.json")


def test_validate_cambium_data_dir_requires_csv_files(tmp_path):
    empty_dir = tmp_path / "empty" / "2023" / "MidCase"
    empty_dir.mkdir(parents=True)

    with pytest.raises(ValueError, match="contains no CSV files"):
        cambium_updater.validate_cambium_data_dir(tmp_path / "empty", "2023", "MidCase")


def test_state_baseline_api_query_uses_timeout(monkeypatch):
    calls = {}

    class FakeResponse:
        def __init__(self):
            self._payload = {'response': {'data': [{'period': '2025'}]}}

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    def fake_get(url, timeout):
        calls['timeout'] = timeout
        return FakeResponse()

    monkeypatch.setattr(state_baseline_data_updater.requests, 'get', fake_get)
    assert state_baseline_data_updater.api_query(
        'https://example.com', 'fake-key'
    ) == [{'period': '2025'}]
    assert calls['timeout'] == 30


@pytest.mark.parametrize(
    ('payload', 'expected_error'),
    [
        ({'response': {'data': []}}, ValueError),
        ({'bad': 'payload'}, ValueError),
        ({'response': {'data': []}}, ValueError),
    ],
)
def test_state_baseline_api_query_rejects_invalid_payloads(monkeypatch, payload, expected_error):
    class FakeResponse:
        def __init__(self, payload):
            self._payload = payload
            self.status_code = 200

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    monkeypatch.setattr(
        state_baseline_data_updater.requests,
        'get',
        lambda url, timeout: FakeResponse(payload),
    )

    with pytest.raises(expected_error):
        state_baseline_data_updater.api_query('https://example.com', 'fake-key')


def test_state_baseline_api_query_raises_on_rate_limit(monkeypatch):
    class FakeResponse:
        def __init__(self):
            self.status_code = 429

        def raise_for_status(self):
            raise RuntimeError('429')

        def json(self):
            return {'response': {'data': []}}

    monkeypatch.setattr(
        state_baseline_data_updater.requests,
        'get',
        lambda url, timeout: FakeResponse(),
    )

    with pytest.raises(RuntimeError):
        state_baseline_data_updater.api_query('https://example.com', 'fake-key')


def test_converter_api_query_rejects_invalid_payloads(monkeypatch):
    calls = {}

    class FakeResponse:
        def __init__(self, payload, status_code=200):
            self._payload = payload
            self.status_code = status_code

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    def fake_get(url, timeout):
        calls['timeout'] = timeout
        return FakeResponse({'response': {'data': []}})

    monkeypatch.setattr(converter.requests, 'get', fake_get)
    backoff_logger, previous_level = mute_backoff_logger()
    try:
        with pytest.raises(ValueError):
            converter.api_query('fake-key', 'https://example.com', 1)
    finally:
        backoff_logger.setLevel(previous_level)
    assert calls['timeout'] == 30


def test_converter_api_query_raises_on_rate_limit(monkeypatch):
    class FakeResponse:
        def __init__(self):
            self.status_code = 429

        def raise_for_status(self):
            raise RuntimeError('429')

        def json(self):
            return {'response': {'data': []}}

    monkeypatch.setattr(
        converter.requests,
        'get',
        lambda url, timeout: FakeResponse(),
    )

    backoff_logger, previous_level = mute_backoff_logger()
    try:
        with pytest.raises(RuntimeError):
            converter.api_query('fake-key', 'https://example.com', 1)
    finally:
        backoff_logger.setLevel(previous_level)


def test_validate_update_year_and_converter_inputs():
    assert state_baseline_data_updater.validate_update_year('2025') == '2025'
    assert converter.validate_year('2025') == '2025'
    assert converter.validate_scenario('ref2025', '2025') == 'ref2025'

    with pytest.raises(ValueError):
        state_baseline_data_updater.validate_update_year('1999')
    with pytest.raises(ValueError):
        converter.validate_scenario('bad-scenario', '2025')


def test_should_overwrite_existing_file():
    existing_path = Path('existing.csv')

    assert (
        state_baseline_data_updater.should_overwrite_existing_file(
            existing_path, False, False, None
        )
        is False
    )
    assert (
        state_baseline_data_updater.should_overwrite_existing_file(
            existing_path, True, False, None
        )
        is True
    )
    assert (
        state_baseline_data_updater.should_overwrite_existing_file(
            existing_path, False, True, None
        )
        is True
    )


def test_state_baseline_parser_supports_dry_run_and_yes_flags():
    parser = state_baseline_data_updater.build_parser()
    args = parser.parse_args(['--year', '2025', '--yes', '--dry-run'])

    assert args.year == '2025'
    assert args.yes is True
    assert args.dry_run is True


def test_converter_parser_supports_non_interactive_flags():
    parser = converter.build_parser()
    args = parser.parse_args(
        [
            '-f', 'site_source_co2_conversions.json',
            '-y', '2025',
            '-s_e', 'ref2025',
            '-s_g', 'ref2025',
            '--no-prompt',
            '--dry-run',
        ]
    )

    assert args.f == 'site_source_co2_conversions.json'
    assert args.no_prompt is True
    assert args.dry_run is True


def test_converter_apply_metric_updates_writes_nested_values():
    conv = {'electricity': {'CO2 intensity': {'data': {'residential': {}}}}}

    converter.apply_metric_updates(
        conv,
        ['electricity', 'CO2 intensity', 'data', 'residential'],
        ['2025'],
        [1.23],
        round_digits=2,
    )

    assert conv['electricity']['CO2 intensity']['data']['residential']['2025'] == 1.23


def test_cambium_write_outputs_writes_json_file(tmp_path):
    output_path = tmp_path / 'out.json'

    cambium_updater.write_outputs(output_path, {'a': 1}, 'json')

    assert output_path.exists()
    assert output_path.read_text() == '{\n  "a": 1\n}'


def test_cambium_import_and_update_path(tmp_path):
    data_dir = tmp_path / '2023' / 'MidCase'
    data_dir.mkdir(parents=True)
    sample_csv = data_dir / 'p1_2023.csv'
    sample_csv.write_text(
        'skip\n'
        'skip\n'
        'skip\n'
        'skip\n'
        'skip\n'
        'timestamp,timestamp_local,aer_load_co2_c,total_cost_enduse\n'
        '2023-01-01 00:00:00,2023-01-01 00:00:00,100.0,10.0\n'
        '2023-01-01 01:00:00,2023-01-01 01:00:00,200.0,20.0\n',
        encoding='utf-8',
    )

    df = cambium_updater.cambium_data_import(tmp_path, '2023', 'MidCase')
    assert len(df) == 2

    ss = {
        'electricity': {
            'site to source conversion': {'data': {'2020': 1.0, '2021': 1.0}},
            'CO2 intensity': {'data': {'residential': {}, 'commercial': {}}},
        }
    }
    updated = cambium_updater.annual_factors_updater(df, ss, 'National')
    assert (
        updated['electricity']['CO2 intensity']['data']['residential']['2023'] > 0
    )


def test_converter_updater_with_mocked_eia_responses_snapshot(monkeypatch):
    conv = {
        'site-source calculation method': 'captured energy',
        'electricity': {
            'site to source conversion': {'data': {'2020': 1.0, '2021': 1.0}},
            'CO2 intensity': {
                'data': {
                    'residential': {'2020': 1.0, '2021': 1.0},
                    'commercial': {'2020': 1.0, '2021': 1.0},
                }
            },
            'price': {
                'data': {
                    'residential': {'2020': 1.0, '2021': 1.0},
                    'commercial': {'2020': 1.0, '2021': 1.0},
                }
            },
        },
        'natural gas': {
            'CO2 intensity': {
                'data': {
                    'residential': {'2020': 1.0, '2021': 1.0},
                    'commercial': {'2020': 1.0, '2021': 1.0},
                }
            },
            'price': {
                'data': {
                    'residential': {'2020': 1.0, '2021': 1.0},
                    'commercial': {'2020': 1.0, '2021': 1.0},
                }
            },
        },
        'propane': {
            'CO2 intensity': {
                'data': {
                    'residential': {'2020': 1.0, '2021': 1.0},
                    'commercial': {'2020': 1.0, '2021': 1.0},
                }
            }
        },
        'distillate': {
            'CO2 intensity': {
                'data': {
                    'residential': {'2020': 1.0, '2021': 1.0},
                    'commercial': {'2020': 1.0, '2021': 1.0},
                }
            }
        },
        'other': {
            'CO2 intensity': {
                'data': {
                    'residential': {'2020': 1.0, '2021': 1.0},
                    'commercial': {'2020': 1.0, '2021': 1.0},
                }
            }
        },
    }

    years = converter.np.array(['2020', '2021'])

    fossil_data = {
        'ng_res_energy': converter.np.array([10.0, 20.0]),
        'ng_com_energy': converter.np.array([12.0, 24.0]),
        'ng_res_co2': converter.np.array([100.0, 200.0]),
        'ng_com_co2': converter.np.array([120.0, 240.0]),
        'ng_res_price': converter.np.array([1.0, 1.1]),
        'ng_com_price': converter.np.array([1.2, 1.3]),
        'lpg_res_energy': converter.np.array([2.0, 2.5]),
        'distl_res_energy': converter.np.array([3.0, 3.5]),
        'lpg_com_energy': converter.np.array([2.0, 2.5]),
        'distl_com_energy': converter.np.array([3.0, 3.5]),
        'rsid_com_energy': converter.np.array([4.0, 4.5]),
        'petro_res_energy': converter.np.array([5.0, 6.0]),
        'petro_res_co2': converter.np.array([50.0, 60.0]),
        'petro_com_energy': converter.np.array([7.0, 8.0]),
        'petro_com_co2': converter.np.array([70.0, 80.0]),
        'coal_com_energy': converter.np.array([1.0, 1.5]),
        'coal_com_co2': converter.np.array([10.0, 15.0]),
        'lpg_res_price': converter.np.array([1.4, 1.5]),
        'distl_res_price': converter.np.array([1.6, 1.7]),
        'lpg_com_price': converter.np.array([1.8, 1.9]),
        'distl_com_price': converter.np.array([2.0, 2.1]),
        'rsid_com_price': converter.np.array([2.2, 2.3]),
    }
    elec_data = {
        'elec_renew_hydro': converter.np.array([1.0, 1.1]),
        'elec_renew_geothermal': converter.np.array([1.0, 1.1]),
        'elec_renew_solar_thermal': converter.np.array([1.0, 1.1]),
        'elec_renew_solar_pv': converter.np.array([1.0, 1.1]),
        'elec_renew_wind': converter.np.array([1.0, 1.1]),
        'elec_tot_energy_site': converter.np.array([100.0, 120.0]),
        'elec_tot_energy_loss': converter.np.array([10.0, 12.0]),
        'elec_res_energy_site': converter.np.array([40.0, 48.0]),
        'elec_res_energy_loss': converter.np.array([4.0, 4.8]),
        'elec_com_energy_site': converter.np.array([60.0, 72.0]),
        'elec_com_energy_loss': converter.np.array([6.0, 7.2]),
        'elec_res_co2': converter.np.array([80.0, 96.0]),
        'elec_com_co2': converter.np.array([120.0, 144.0]),
        'elec_res_price': converter.np.array([0.15, 0.16]),
        'elec_com_price': converter.np.array([0.17, 0.18]),
    }

    call_count = {'value': 0}

    def fake_data_getter(api_key, series_names, api_urls, series_table):
        call_count['value'] += 1
        if call_count['value'] == 1:
            return fossil_data, years
        return elec_data, years

    monkeypatch.setattr(converter, 'data_getter', fake_data_getter)
    updated = converter.updater(
        conv, 'fake-key', '2023', 'ref2023', 'ref2023', False
    )

    snapshot = json.dumps(
        updated['electricity']['CO2 intensity']['data']['residential'],
        sort_keys=True,
    )
    assert '2020' in snapshot
    assert '2021' in snapshot
    assert updated['electricity']['site to source conversion']['data']['2021'] > 1.0


def test_get_baseline_data_path_prefers_latest_year(tmp_path, monkeypatch):
    (tmp_path / 'EIA_State_Emissions_Prices_Baselines_2023.csv').write_text('old')
    latest_path = tmp_path / 'EIA_State_Emissions_Prices_Baselines_2025.csv'
    latest_path.write_text('new')

    monkeypatch.setattr(state_baseline_data_updater.fp, 'CONVERT_DATA', tmp_path)

    assert state_baseline_data_updater.get_baseline_data_path() == latest_path


def test_clean_source_disposition_data_vectorizes_total_disposition():
    data = [{
        'period': '2025',
        'state': 'AL',
        'total-net-generation': 1000000,
        'net-interstate-trade': -100000,
        'direct-use': 100000,
        'total-international-imports': 50000,
        'estimated-losses': 10000,
    }]

    df = state_baseline_data_updater.clean_source_disposition_data(data)

    assert df.loc[0, 'total_disposition'] == 1050000
    assert df.loc[0, 'TD_loss_factor'] == 10000 / (1050000 - 100000)


def test_prune_years_from_mapping_removes_outdated_entries(capsys):
    payload = {'2020': 1, '2022': 2, 'extra': {'2021': 3, '2023': 4}}

    removed = converter.prune_years_from_mapping(payload, 2022, 'test payload')

    assert removed == ['2020', '2021']
    assert payload == {'2022': 2, 'extra': {'2023': 4}}
    assert 'test payload' in capsys.readouterr().out


if __name__ == '__main__':
    raise SystemExit(pytest.main([str(Path(__file__))]))
