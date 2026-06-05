"""Markdown rendering test — uses fixtures and a stubbed Dossier."""

from site_dossier.models import Dossier
from site_dossier.render.markdown import render_markdown
from site_dossier.render.summary import generate_summary


def test_render_markdown_contains_all_sections(
    tmp_path, nyc_site, climate_ok, wind_ok, sun_ok, demographics_ok, zoning_ok
):
    summary = generate_summary(
        site=nyc_site,
        climate=climate_ok,
        wind=wind_ok,
        sun=sun_ok,
        demographics=demographics_ok,
        zoning=zoning_ok,
    )
    dossier = Dossier(
        site=nyc_site,
        climate=climate_ok,
        wind=wind_ok,
        sun=sun_ok,
        demographics=demographics_ok,
        zoning=zoning_ok,
        screen_reader_summary=summary,
    )
    out = tmp_path / "dossier.md"
    render_markdown(dossier, out)
    text = out.read_text()

    assert text.startswith("# Site Dossier:")
    assert "Summary for screen readers" in text
    for heading in (
        "## 1. Location",
        "## 2. Climate normals",
        "## 3. Sun path",
        "## 4. Prevailing winds",
        "## 5. Demographics",
        "## 6. Zoning & land use",
        "## 7. Rhino sidecar",
        "## 8. Notes & data quality",
    ):
        assert heading in text, f"missing heading: {heading}"

    # Key data values flow through
    assert "C5-3" in text
    assert "350 5th Ave" in text


def test_render_markdown_renders_unavailable_sections(
    tmp_path, nyc_site, climate_unavailable, wind_ok, sun_ok, demographics_ok, zoning_degraded
):
    summary = generate_summary(
        site=nyc_site,
        climate=climate_unavailable,
        wind=wind_ok,
        sun=sun_ok,
        demographics=demographics_ok,
        zoning=zoning_degraded,
    )
    dossier = Dossier(
        site=nyc_site,
        climate=climate_unavailable,
        wind=wind_ok,
        sun=sun_ok,
        demographics=demographics_ok,
        zoning=zoning_degraded,
        screen_reader_summary=summary,
    )
    out = tmp_path / "dossier.md"
    render_markdown(dossier, out)
    text = out.read_text()
    assert "Section unavailable" in text
    # Degraded zoning panel shows the suggested search
    assert "duckduckgo.com" in text or "Suggested search" in text
