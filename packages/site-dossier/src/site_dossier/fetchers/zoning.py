"""Zoning: tiered lookup — municipal API → OSM Overpass landuse → web-search citation.

Municipal portals are registered in `data/municipal_portals.yml`. Each entry includes the
city, a match key (county or city name as Nominatim returns it), and an HTTP recipe.
"""

from __future__ import annotations

import urllib.parse
from importlib import resources
from typing import Any

import yaml
from ds_common import http
from ds_common.cache import cached
from ds_common.geocode import ResolvedSite

from site_dossier.fetchers.base import degrade_on_failure
from site_dossier.models import FetcherResult

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def _load_portals() -> list[dict]:
    with resources.files("site_dossier.data").joinpath("municipal_portals.yml").open("rb") as f:
        return yaml.safe_load(f) or []


@degrade_on_failure("zoning")
def fetch_zoning(site: ResolvedSite) -> FetcherResult:
    # Tier 1: known municipal portal
    portal = _match_portal(site)
    if portal:
        result = _query_portal(site, portal)
        if result is not None:
            return result

    # Tier 2: OSM landuse tags via Overpass
    osm = _query_overpass(site)
    if osm is not None and osm.data and osm.data.get("tags"):
        return osm

    # Tier 3: web-search citation — we don't scrape, just hand the user the query.
    return _web_search_pointer(site)


def _match_portal(site: ResolvedSite) -> dict | None:
    portals = _load_portals()
    name_targets = {
        (site.admin2 or "").lower(),
        (site.admin1 or "").lower(),
    }
    for p in portals:
        keys = {k.lower() for k in p.get("match", [])}
        if keys & name_targets:
            return p
    return None


@cached(key=lambda site, portal: f"zoning:portal:{portal['id']}:{round(site.lat,4)}:{round(site.lon,4)}", ttl_days=7)
def _query_portal(site: ResolvedSite, portal: dict) -> FetcherResult | None:
    """Call a city zoning endpoint described by the registry entry."""
    url = portal["url"].format(lat=site.lat, lon=site.lon)
    try:
        data = http.get_json(url)
    except Exception as exc:
        return FetcherResult(
            status="partial",
            source=f"{portal['name']} zoning portal",
            data={"portal": portal["id"], "query_url": url},
            notes=[
                "Could not query municipal zoning portal.",
                f"Underlying error: {exc}",
            ],
        )

    # Different portals return different shapes. Each entry declares which field
    # carries the zoning code; we extract it generically.
    records = data if isinstance(data, list) else data.get("features") or data.get("records") or []
    code_field = portal.get("code_field", "zonedist")
    description_field = portal.get("description_field")

    if not records:
        return FetcherResult(
            status="partial",
            source=f"{portal['name']} zoning portal",
            data={"portal": portal["id"], "query_url": url},
            notes=["Portal returned no records for this lat/lon."],
        )

    first = records[0]
    flat = first.get("properties", first) if isinstance(first, dict) else {}
    code = flat.get(code_field)
    description = flat.get(description_field) if description_field else None

    return FetcherResult(
        status="ok",
        source=f"{portal['name']} zoning portal",
        data={
            "portal": portal["id"],
            "zoning_code": code,
            "description": description,
            "raw_first_record": flat,
            "query_url": url,
        },
    )


@cached(key=lambda site: f"zoning:osm:{round(site.lat,4)}:{round(site.lon,4)}", ttl_days=30)
def _query_overpass(site: ResolvedSite) -> FetcherResult | None:
    query = (
        f"[out:json][timeout:25];"
        f"(way(around:50,{site.lat},{site.lon})[landuse];"
        f"relation(around:50,{site.lat},{site.lon})[landuse];);"
        f"out tags;"
    )
    try:
        data = http.get_json(OVERPASS_URL, params={"data": query})
    except Exception as exc:
        return FetcherResult(
            status="partial",
            source="OpenStreetMap (landuse via Overpass)",
            data=None,
            notes=[f"Overpass query failed: {exc}"],
        )

    elements = data.get("elements", []) if isinstance(data, dict) else []
    tags: dict[str, Any] = {}
    for el in elements:
        for k, v in (el.get("tags") or {}).items():
            tags.setdefault(k, v)
    if not tags:
        return None

    landuse = tags.get("landuse")
    return FetcherResult(
        status="partial" if not landuse else "ok",
        source="OpenStreetMap (landuse tags, 50 m radius)",
        data={"tags": tags, "landuse": landuse},
        notes=[
            "OSM landuse tags are crowd-sourced and may not match official zoning.",
            "Verify with the municipality before relying on these for design decisions.",
        ],
    )


def _web_search_pointer(site: ResolvedSite) -> FetcherResult:
    locality = site.admin2 or site.admin1 or site.country or "the local jurisdiction"
    query = f"zoning {site.display_name}"
    return FetcherResult(
        status="partial",
        source="manual lookup required",
        data={
            "search_query": query,
            "search_url": f"https://duckduckgo.com/?q={urllib.parse.quote(query)}",
            "locality": locality,
        },
        notes=[
            f"No municipal zoning API is registered for {locality} and no OSM landuse "
            f"tags were found within 50 m. Run a web search and verify with the municipality.",
        ],
    )
