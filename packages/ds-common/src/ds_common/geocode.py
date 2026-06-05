"""Geocoding: US Census Geocoder (primary) + Nominatim/OpenStreetMap (fallback).

Census is free, no key, and ground-truth for US addresses. Nominatim works globally but is
rate-limited (1 req/s, polite UA required). We always reverse-geocode via Nominatim after
to fill in admin hierarchy (county, state, country, ISO code).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from ds_common import http
from ds_common.cache import cached
from ds_common.errors import FetchError
from ds_common.geometry import parse_lat_lon

CENSUS_GEOCODE_URL = (
    "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
)
NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"


class ResolvedSite(BaseModel):
    """The canonical site object every tool downstream operates on."""

    lat: float
    lon: float
    display_name: str
    address: str | None = None
    admin1: str | None = Field(None, description="State / region")
    admin2: str | None = Field(None, description="County / city")
    country: str | None = None
    country_code: str | None = Field(None, description="ISO 3166-1 alpha-2")
    elevation_m: float | None = None
    source: str = "unknown"


@cached(key=lambda q: f"geocode_fwd:{q.lower().strip()}", ttl_days=30)
def _census_geocode(query: str) -> tuple[float, float, str] | None:
    try:
        data = http.get_json(
            CENSUS_GEOCODE_URL,
            params={
                "address": query,
                "benchmark": "Public_AR_Current",
                "format": "json",
            },
        )
    except Exception:
        return None
    matches = data.get("result", {}).get("addressMatches", [])
    if not matches:
        return None
    m = matches[0]
    coords = m["coordinates"]
    return float(coords["y"]), float(coords["x"]), m.get("matchedAddress", query)


@cached(key=lambda q: f"nominatim_fwd:{q.lower().strip()}", ttl_days=30)
def _nominatim_geocode(query: str) -> tuple[float, float, str] | None:
    try:
        data = http.get_json(
            NOMINATIM_SEARCH_URL,
            params={"q": query, "format": "jsonv2", "limit": 1, "addressdetails": 1},
        )
    except Exception:
        return None
    if not data:
        return None
    r = data[0]
    return float(r["lat"]), float(r["lon"]), r.get("display_name", query)


@cached(key=lambda lat, lon: f"nominatim_rev:{round(lat,4)}:{round(lon,4)}", ttl_days=30)
def _nominatim_reverse(lat: float, lon: float) -> dict | None:
    try:
        data = http.get_json(
            NOMINATIM_REVERSE_URL,
            params={
                "lat": lat,
                "lon": lon,
                "format": "jsonv2",
                "addressdetails": 1,
                "zoom": 14,
            },
        )
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def geocode(query: str) -> ResolvedSite:
    """Resolve an address or 'lat,lon' string into a ResolvedSite.

    Raises FetchError if nothing resolves.
    """
    # Fast path: explicit coordinates.
    coords = parse_lat_lon(query)
    if coords:
        lat, lon = coords
        rev = _nominatim_reverse(lat, lon) or {}
        return _from_nominatim(lat, lon, query, rev, source="direct-coords")

    # Try Census first (US-focused).
    census = _census_geocode(query)
    if census:
        lat, lon, display = census
        rev = _nominatim_reverse(lat, lon) or {}
        site = _from_nominatim(lat, lon, display, rev, source="us-census")
        site.address = display
        return site

    # Fall back to Nominatim worldwide.
    nom = _nominatim_geocode(query)
    if nom:
        lat, lon, display = nom
        rev = _nominatim_reverse(lat, lon) or {}
        site = _from_nominatim(lat, lon, display, rev, source="nominatim")
        site.address = query
        return site

    raise FetchError(f"Could not geocode: {query!r}")


def _from_nominatim(
    lat: float, lon: float, display: str, rev: dict, *, source: str
) -> ResolvedSite:
    addr = rev.get("address", {}) if rev else {}
    admin1 = addr.get("state") or addr.get("region")
    admin2 = (
        addr.get("county")
        or addr.get("city")
        or addr.get("town")
        or addr.get("village")
        or addr.get("municipality")
    )
    country = addr.get("country")
    cc = addr.get("country_code", "").upper() or None
    return ResolvedSite(
        lat=lat,
        lon=lon,
        display_name=rev.get("display_name") if rev else display,
        admin1=admin1,
        admin2=admin2,
        country=country,
        country_code=cc,
        source=source,
    )
