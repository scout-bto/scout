from scout.AEO_update_helpers.baseline_comparison import _build_series_tolerance


def test_2026_series_tolerances_cover_current_eia_drift():
    tolerances = _build_series_tolerance(2026)

    assert tolerances["cnsm_NA_resd_wtht_ng_NA_usa_qbtu"] == 0.00025
    assert tolerances["cnsm_NA_comm_NA_prc_othu_usa_qbtu"] == 0.0012
    assert tolerances["cnsm_NA_comm_NA_prc_wtht_usa_qbtu"] == 0.00095
