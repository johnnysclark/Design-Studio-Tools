"""Chart generation. Every chart function returns (png_path, alt_text)."""

from __future__ import annotations

from pathlib import Path

from ds_common.geocode import ResolvedSite

from site_dossier.charts.climograph import draw_climograph
from site_dossier.charts.sun_path import draw_sun_path
from site_dossier.charts.wind_rose import draw_wind_rose
from site_dossier.models import ClimateData, SunData, WindData

__all__ = ["generate_charts", "draw_climograph", "draw_sun_path", "draw_wind_rose"]


def generate_charts(
    *,
    site: ResolvedSite,
    climate: ClimateData,
    wind: WindData,
    sun: SunData,
    output_dir: Path,
) -> dict[str, Path]:
    """Generate every available chart; skip those whose source data is unavailable."""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}

    if sun.status == "ok" and sun.data:
        path, _alt = draw_sun_path(sun.data, site, output_dir / "sun_path.png")
        paths["sun_path"] = path

    if wind.status == "ok" and wind.data:
        path, _alt = draw_wind_rose(wind.data, output_dir / "wind_rose.png")
        paths["wind_rose"] = path

    if climate.status == "ok" and climate.data:
        path, _alt = draw_climograph(climate.data, output_dir / "climograph.png")
        paths["climograph"] = path

    return paths
