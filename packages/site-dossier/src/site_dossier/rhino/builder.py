"""Build the .3dm sidecar that drops straight into the designer's Rhino model.

Layers:
- `Site`             : point at origin + true-north arrow + text dot with address/coords
- `Sun_Paths`        : one polyline per key day (4), tip labeled with date
- `Wind_Rose`        : 16-sector radial spokes scaled to a 20 m base
- `Annotations`      : text dots for legend & cardinal directions

Plus a `sun_wind_hourly.csv` next to the .3dm with Ladybug-compatible columns.
"""

from __future__ import annotations

import csv
import math
from datetime import datetime
from pathlib import Path

from ds_common import rhino_export as rx
from ds_common.geocode import ResolvedSite

from site_dossier.models import SunData, WindData

# Sun-path vectors are 10 m so they're visible at building scale.
SUN_VECTOR_LEN = 10.0
WIND_ROSE_RADIUS = 20.0
NORTH_ARROW_LEN = 5.0


def build_rhino_sidecar(
    *,
    site: ResolvedSite,
    sun: SunData,
    wind: WindData,
    output_dir: Path,
) -> tuple[Path, Path]:
    """Build dossier.3dm + sun_wind_hourly.csv. Returns (3dm_path, csv_path)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_3dm = output_dir / "dossier.3dm"
    out_csv = output_dir / "sun_wind_hourly.csv"

    doc = rx.new_doc(lat=site.lat, lon=site.lon, elevation_m=site.elevation_m or 0.0)
    site_layer = rx.add_layer(doc, "Site", color=(0, 0, 0, 255))
    sun_layer = rx.add_layer(doc, "Sun_Paths", color=(255, 200, 0, 255))
    wind_layer = rx.add_layer(doc, "Wind_Rose", color=(50, 130, 200, 255))
    anno_layer = rx.add_layer(doc, "Annotations", color=(80, 80, 80, 255))

    _add_site_marker(doc, site, site_layer, anno_layer)
    if sun.status == "ok" and sun.data:
        _add_sun_paths(doc, sun.data, sun_layer)
    if wind.status == "ok" and wind.data:
        _add_wind_rose(doc, wind.data, wind_layer)

    rx.save(doc, out_3dm)
    _write_csv(out_csv, sun=sun, wind=wind)
    return out_3dm, out_csv


def _add_site_marker(
    doc, site: ResolvedSite, site_layer: int, anno_layer: int
) -> None:
    rx.add_point(doc, (0, 0, 0), site_layer, name="site_origin")
    rx.add_text_dot(
        doc,
        (0, 0, 0),
        f"{site.display_name}\n{site.lat:.5f}, {site.lon:.5f}",
        site_layer,
    )
    # True-north arrow on +Y
    rx.add_line(doc, (0, 0, 0), (0, NORTH_ARROW_LEN, 0), anno_layer, name="north")
    rx.add_text_dot(doc, (0, NORTH_ARROW_LEN + 0.5, 0), "N", anno_layer)
    # Cardinal labels
    for label, xyz in [
        ("E", (NORTH_ARROW_LEN, 0, 0)),
        ("S", (0, -NORTH_ARROW_LEN, 0)),
        ("W", (-NORTH_ARROW_LEN, 0, 0)),
    ]:
        rx.add_text_dot(doc, xyz, label, anno_layer)


def _add_sun_paths(doc, sun_data: dict, sun_layer: int) -> None:
    """One polyline per key day, traced as sun-vector tips on a {SUN_VECTOR_LEN}-radius sphere."""
    for key, track in sun_data["tracks"].items():
        if not track:
            continue
        pts: list[tuple[float, float, float]] = []
        for p in track:
            x, y, z = _sun_xyz(p["altitude_deg"], p["azimuth_deg"], SUN_VECTOR_LEN)
            pts.append((x, y, z))
        rx.add_polyline(doc, pts, sun_layer, name=key)
        # Tag the apex
        date = sun_data["key_dates"].get(key, key)
        apex = max(track, key=lambda p: p["altitude_deg"])
        x, y, z = _sun_xyz(apex["altitude_deg"], apex["azimuth_deg"], SUN_VECTOR_LEN)
        rx.add_text_dot(doc, (x, y, z), f"{key.replace('_', ' ')} {date}", sun_layer)


def _sun_xyz(altitude_deg: float, azimuth_deg: float, r: float) -> tuple[float, float, float]:
    """Convert sun altitude/azimuth into XYZ on a sphere with +Y = north."""
    alt = math.radians(altitude_deg)
    az = math.radians(azimuth_deg)
    horiz = r * math.cos(alt)
    # azimuth 0 = north (+Y), 90 = east (+X), measured clockwise
    x = horiz * math.sin(az)
    y = horiz * math.cos(az)
    z = r * math.sin(alt)
    return x, y, z


def _add_wind_rose(doc, wind_data: dict, wind_layer: int) -> None:
    """One radial spoke per sector, length proportional to that sector's hour share."""
    total = wind_data.get("total_hours", 0)
    if not total:
        return
    sectors = wind_data["sectors"]
    max_pct = max(s["pct"] for s in sectors) or 1.0
    for s in sectors:
        # +Y = north, azimuth measured clockwise
        az = math.radians(s["from_deg"])
        r = WIND_ROSE_RADIUS * (s["pct"] / max_pct)
        x = r * math.sin(az)
        y = r * math.cos(az)
        rx.add_line(doc, (0, 0, 0), (x, y, 0), wind_layer, name=f"wind_{s['cardinal']}")
        if s["pct"] >= 5:  # only label sectors with material flow
            rx.add_text_dot(
                doc,
                (x * 1.05, y * 1.05, 0),
                f"{s['cardinal']} {s['pct']:.1f}%",
                wind_layer,
            )


def _write_csv(out_csv: Path, *, sun: SunData, wind: WindData) -> None:
    """Ladybug-compatible columns. Sun rows are per key-day; wind summary is appended."""
    with out_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "category",
                "key",
                "hour_utc",
                "sun_alt_deg",
                "sun_az_deg",
                "wind_speed_mps",
                "wind_dir_deg",
                "note",
            ]
        )
        if sun.status == "ok" and sun.data:
            for key, track in sun.data["tracks"].items():
                for p in track:
                    w.writerow(
                        [
                            "sun",
                            key,
                            p["hour_utc"],
                            p["altitude_deg"],
                            p["azimuth_deg"],
                            "",
                            "",
                            sun.data["key_dates"].get(key, ""),
                        ]
                    )
        if wind.status == "ok" and wind.data:
            w.writerow(
                [
                    "wind_summary",
                    "10yr",
                    "",
                    "",
                    "",
                    wind.data["mean_speed_mps"],
                    wind.data["prevailing_dir_deg"],
                    f"prevailing {wind.data['prevailing_dir_cardinal']} "
                    f"({wind.data['prevailing_dir_pct']}%)",
                ]
            )
        w.writerow(
            [
                "meta",
                "generated_at",
                datetime.utcnow().isoformat(),
                "",
                "",
                "",
                "",
                "site-dossier",
            ]
        )
