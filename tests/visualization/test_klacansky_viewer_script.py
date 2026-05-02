"""Tests for the Klacansky viewer script wiring."""

from scripts.klacansky_viewer import build_parser, main


def test_parser_defaults_to_fuel_dataset():
    args = build_parser().parse_args([])

    assert args.dataset == "fuel"
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
