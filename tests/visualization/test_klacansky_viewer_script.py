"""Tests for the Klacansky viewer script wiring."""

from scripts.klacansky_viewer import build_parser, main


def test_parser_defaults_to_fuel_dataset():
    args = build_parser().parse_args([])

    assert args.dataset == "fuel"
    assert args.file is None
    assert args.shape is None
    assert args.dtype == "uint8"
    assert args.isovalue is None
    assert args.no_freudenthal is False


def test_main_passes_cli_options_to_viewer(monkeypatch):
    calls = []

    def fake_show(dataset_name, **kwargs):
        calls.append((dataset_name, kwargs))
        return "plotter"

    monkeypatch.setattr("scripts.klacansky_viewer.show_klacansky_viewer", fake_show)

    result = main(["nucleon", "--isovalue", "42", "--no-freudenthal"])

    assert result == "plotter"
    assert calls == [
        (
            "nucleon",
            {"initial_isovalue": 42.0, "freudenthal": False},
        )
    ]


def test_main_passes_raw_file_options_to_raw_viewer(monkeypatch):
    calls = []

    def fake_show(file_path, shape_whd, **kwargs):
        calls.append((file_path, shape_whd, kwargs))
        return "plotter"

    monkeypatch.setattr("scripts.klacansky_viewer.show_raw_file_viewer", fake_show)

    result = main(["--file", "demo.raw", "--shape", "2", "2", "2", "--dtype", "uint16", "--isovalue", "7"])

    assert result == "plotter"
    assert calls == [
        (
            "demo.raw",
            (2, 2, 2),
            {"dtype": "uint16", "initial_isovalue": 7.0, "freudenthal": True},
        )
    ]


def test_main_requires_shape_for_raw_file():
    try:
        main(["--file", "demo.raw"])
    except SystemExit as exc:
        assert "--shape W H D is required" in str(exc)
    else:
        raise AssertionError("expected --shape requirement for raw file viewer")
