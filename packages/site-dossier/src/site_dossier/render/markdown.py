"""Render the Dossier into a Markdown file using a Jinja2 template."""

from __future__ import annotations

import calendar
from importlib import resources
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from site_dossier.charts.climograph import draw_climograph as _alt_clim  # noqa: F401
from site_dossier.charts.sun_path import draw_sun_path as _alt_sun  # noqa: F401
from site_dossier.charts.wind_rose import draw_wind_rose as _alt_wind  # noqa: F401
from site_dossier.models import Dossier


def _env() -> Environment:
    template_dir = resources.files("site_dossier.render").joinpath("templates")
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(default=False),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["month_name"] = lambda m: calendar.month_name[m] if m else ""
    env.filters["month_abbr"] = lambda m: calendar.month_abbr[m] if m else ""
    return env


def render_markdown(dossier: Dossier, out_path: Path) -> Path:
    env = _env()
    template = env.get_template("dossier.md.j2")

    # Compute alt text inline (charts module returns it; we just need the strings here)
    alts: dict[str, str] = {}
    if "sun_path" in dossier.chart_paths and dossier.sun.data:
        alts["sun_path"] = _sun_alt(dossier)
    if "wind_rose" in dossier.chart_paths and dossier.wind.data:
        alts["wind_rose"] = _wind_alt(dossier)
    if "climograph" in dossier.chart_paths and dossier.climate.data:
        alts["climograph"] = _climograph_alt(dossier)

    text = template.render(
        d=dossier,
        site=dossier.site,
        climate=dossier.climate,
        wind=dossier.wind,
        sun=dossier.sun,
        demographics=dossier.demographics,
        zoning=dossier.zoning,
        alts=alts,
        chart_relpaths={
            k: f"charts/{v.name}" for k, v in dossier.chart_paths.items()
        },
        generated_at=dossier.generated_at,
        summary=dossier.screen_reader_summary,
    )
    out_path.write_text(text)
    return out_path


def _sun_alt(d: Dossier) -> str:
    ss = (d.sun.data or {}).get("sunrise_sunset", {})
    summer = ss.get("summer_solstice", {}).get("max_altitude_deg", 0) or 0
    winter = ss.get("winter_solstice", {}).get("max_altitude_deg", 0) or 0
    return (
        f"Polar sun-path diagram for {d.site.display_name}. "
        f"Maximum solar altitude: {summer:.0f} degrees on the summer solstice, "
        f"{winter:.0f} degrees on the winter solstice."
    )


def _wind_alt(d: Dossier) -> str:
    w = d.wind.data or {}
    return (
        f"Wind rose. Prevailing wind from {w.get('prevailing_dir_cardinal', 'N/A')} "
        f"({w.get('prevailing_dir_pct', 0)}% of hours). "
        f"Mean speed {w.get('mean_speed_mps', 0)} m/s. "
        f"Calm {w.get('calm_pct', 0)}% of the time."
    )


def _climograph_alt(d: Dossier) -> str:
    a = (d.climate.data or {}).get("annual", {}) or {}
    return (
        f"Climograph of monthly normals. "
        f"Annual mean temperature {a.get('mean_temp_c', 'unknown')} degrees Celsius. "
        f"Annual precipitation {a.get('annual_precip_mm', 'unknown')} millimeters."
    )
