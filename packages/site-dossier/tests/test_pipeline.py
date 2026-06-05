"""End-to-end pipeline test with all fetchers stubbed — no network."""

import json

import pytest
from site_dossier import pipeline as pipeline_mod
from site_dossier.pipeline import generate_dossier


@pytest.fixture
def stubbed_pipeline(
    monkeypatch,
    nyc_site,
    climate_ok,
    wind_ok,
    sun_ok,
    demographics_ok,
    zoning_ok,
):
    """Patch every external entry point (geocode + fetchers) with fixture data."""
    monkeypatch.setattr(pipeline_mod, "geocode", lambda q: nyc_site)
    # Replace each fetcher in the _FETCHERS registry with a no-network stub.
    fakes = {
        "climate": (lambda site, **kw: climate_ok, type(climate_ok)),
        "wind": (lambda site, **kw: wind_ok, type(wind_ok)),
        "sun": (lambda site, **kw: sun_ok, type(sun_ok)),
        "demographics": (lambda site, **kw: demographics_ok, type(demographics_ok)),
        "zoning": (lambda site, **kw: zoning_ok, type(zoning_ok)),
    }
    monkeypatch.setattr(pipeline_mod, "_FETCHERS", fakes)
    return fakes


def test_end_to_end_md_3dm(tmp_path, stubbed_pipeline):
    d = generate_dossier(
        address="350 5th Ave, New York, NY",
        output_dir=tmp_path,
        formats=("md", "3dm"),  # skip PDF in unit tests (heavier deps)
    )
    assert d.markdown_path and d.markdown_path.exists()
    assert d.rhino_path and d.rhino_path.exists()
    assert d.csv_path and d.csv_path.exists()
    assert d.data_json_path and d.data_json_path.exists()
    assert d.pdf_path is None

    text = d.markdown_path.read_text()
    assert "Summary for screen readers" in text
    assert "## 2. Climate normals" in text

    # data.json round-trips
    payload = json.loads(d.data_json_path.read_text())
    assert payload["site"]["lat"] == 40.7484
    assert payload["screen_reader_summary"] == d.screen_reader_summary


def test_end_to_end_section_filter(tmp_path, stubbed_pipeline):
    d = generate_dossier(
        lat=40.7484,
        lon=-73.9857,
        output_dir=tmp_path,
        formats=("md",),
        sections=("climate", "sun"),
    )
    # Excluded sections degrade to "unavailable"
    assert d.wind.status == "unavailable"
    assert d.demographics.status == "unavailable"
    assert d.zoning.status == "unavailable"
    assert d.climate.status == "ok"
    assert d.sun.status == "ok"
