import pytest

from scout.config import AEOInputRegistry as air, FilePaths
from scout.eia_file import EIAFiles


def test_missing_for_mode_rejects_unknown_required_keys(tmp_path):
    with pytest.raises(ValueError, match="Unsupported required_keys"):
        air.missing_for_mode(
            "raw",
            input_dir=tmp_path,
            required_keys=["res_db_srce"],
        )


def test_assert_present_reports_missing_paths_and_hint(tmp_path):
    with pytest.raises(FileNotFoundError, match="Next step: place files") as exc:
        air.assert_present(
            "processed",
            input_dir=tmp_path,
            required_keys=["res_db", "res_dgen"],
            hint="place files",
        )

    message = str(exc.value)
    assert str(tmp_path / "RDM_DBOUT.txt") in message
    assert str(tmp_path / "RDM_DGENOUT.txt") in message


def test_preflight_raw_inputs_has_actionable_error_message(tmp_path):
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    processed_dir.mkdir()

    files = EIAFiles(input_dir=raw_dir, output_dir=processed_dir)
    with pytest.raises(FileNotFoundError, match="Missing required raw AEO inputs") as exc:
        files.preflight_raw_inputs()

    message = str(exc.value)
    assert str(raw_dir / "rsmess.xlsx") in message
    assert str(raw_dir / "ktekx.xlsx") in message
    assert str(raw_dir / "rsmlgt.txt") in message
    assert str(raw_dir / "RDM_DBOUT.txt") in message


def test_processed_path_map_falls_back_to_raw_when_processed_copy_missing(tmp_path, monkeypatch):
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    processed_dir.mkdir()

    raw_file = raw_dir / "CDM_SDOUT.txt"
    raw_file.write_text("dummy", encoding="utf-8")

    monkeypatch.setattr(FilePaths, "INPUTS_RAW", raw_dir)
    monkeypatch.setattr(FilePaths, "INPUTS_PROCESSED", processed_dir)

    paths = air.path_map("processed")

    assert paths["cdm_sd"] == raw_file


def test_processed_kprem_path_falls_back_to_raw_when_processed_copy_missing(tmp_path, monkeypatch):
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    processed_dir.mkdir()

    raw_file = raw_dir / "kprem.txt"
    raw_file.write_text("dummy", encoding="utf-8")

    monkeypatch.setattr(FilePaths, "INPUTS_RAW", raw_dir)
    monkeypatch.setattr(FilePaths, "INPUTS_PROCESSED", processed_dir)

    paths = air.path_map("processed")

    assert paths["kprem"] == raw_file


def test_resdbout_fill_household_reads_raw_and_preserves_raw_file(tmp_path):
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    processed_dir.mkdir()

    raw_file = raw_dir / "RDM_DBOUT.txt"
    raw_contents = "HOUSEHOLDS,BULBTYPE\n,HAL\n"
    raw_file.write_text(raw_contents, encoding="utf-8")

    files = EIAFiles(input_dir=raw_dir, output_dir=processed_dir)
    files.resdbout_fill_household()

    assert raw_file.read_text(encoding="utf-8") == raw_contents
    assert files.r_db_out.exists()
    assert "0,HAL" in files.r_db_out.read_text(encoding="utf-8")


def test_eia_files_writes_processed_outputs_to_processed_directory(tmp_path):
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    processed_dir.mkdir()

    raw_file = raw_dir / "RDM_DBOUT.txt"
    raw_file.write_text("HOUSEHOLDS,BULBTYPE\n,HAL\n", encoding="utf-8")

    files = EIAFiles(input_dir=raw_dir, output_dir=processed_dir)

    assert files.r_db_out == processed_dir / "RDM_DBOUT.txt"
    assert files.r_db_out.parent == processed_dir
