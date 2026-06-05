"""Lightweight lat/lon helpers shared across tools."""

from __future__ import annotations

import math
import re

LAT_LON_RE = re.compile(r"^\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*$")


def parse_lat_lon(text: str) -> tuple[float, float] | None:
    """Parse 'lat,lon' strings. Returns (lat, lon) or None if not a coord string."""
    m = LAT_LON_RE.match(text)
    if not m:
        return None
    lat = float(m.group(1))
    lon = float(m.group(2))
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None
    return lat, lon


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two points in meters."""
    r = 6_371_000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def cardinal_from_deg(deg: float) -> str:
    """Convert a 0-360 bearing into a 16-point compass label."""
    labels = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
    ]
    idx = int((deg % 360) / 22.5 + 0.5) % 16
    return labels[idx]
