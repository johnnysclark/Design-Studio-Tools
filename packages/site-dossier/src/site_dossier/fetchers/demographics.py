"""Demographics: US Census ACS 5-year (tract level via FCC Geo for FIPS) or World Bank (intl)."""

from __future__ import annotations

from ds_common import http
from ds_common.cache import cached
from ds_common.geocode import ResolvedSite

from site_dossier.fetchers.base import degrade_on_failure
from site_dossier.models import FetcherResult

FCC_AREA_URL = "https://geo.fcc.gov/api/census/area"
ACS_URL = "https://api.census.gov/data/2022/acs/acs5"
WORLD_BANK_URL = "https://api.worldbank.org/v2/country/{iso}/indicator/{ind}"

ACS_VARS = {
    "B01001_001E": "total_population",
    "B19013_001E": "median_household_income_usd",
    "B25077_001E": "median_home_value_usd",
    "B25064_001E": "median_gross_rent_usd",
}

WORLD_BANK_INDICATORS = {
    "SP.POP.TOTL": "total_population",
    "NY.GDP.PCAP.CD": "gdp_per_capita_usd",
    "SP.URB.TOTL.IN.ZS": "urban_population_pct",
}


@degrade_on_failure("demographics")
def fetch_demographics(site: ResolvedSite, census_key: str | None = None) -> FetcherResult:
    if site.country_code == "US":
        return _fetch_us(site, census_key)
    return _fetch_world_bank(site)


@cached(key=lambda site, census_key=None: f"fips:{round(site.lat,4)}:{round(site.lon,4)}", ttl_days=365)
def _lookup_fips(site: ResolvedSite, census_key: str | None = None) -> dict | None:
    data = http.get_json(
        FCC_AREA_URL, params={"lat": site.lat, "lon": site.lon, "format": "json"}
    )
    blocks = data.get("results") or []
    if not blocks:
        return None
    b = blocks[0]
    fips = b.get("block_fips") or ""
    if len(fips) < 11:
        return None
    return {
        "state": fips[0:2],
        "county": fips[2:5],
        "tract": fips[5:11],
        "block": fips[11:],
        "county_name": b.get("county_name"),
        "state_code": b.get("state_code"),
    }


def _fetch_us(site: ResolvedSite, census_key: str | None) -> FetcherResult:
    fips = _lookup_fips(site)
    if not fips:
        return FetcherResult(
            status="unavailable",
            source="US Census ACS 5-year (2022)",
            data=None,
            notes=["FCC Geo API returned no block for this lat/lon."],
        )

    var_list = ",".join(["NAME", *ACS_VARS.keys()])
    params: dict = {
        "get": var_list,
        "for": f"tract:{fips['tract']}",
        "in": f"state:{fips['state']} county:{fips['county']}",
    }
    if census_key:
        params["key"] = census_key

    try:
        rows = http.get_json(ACS_URL, params=params)
    except Exception as exc:
        return FetcherResult(
            status="partial",
            source="US Census ACS 5-year (2022)",
            data={"fips": fips},
            notes=[
                "Could not fetch ACS variables (may need CENSUS_API_KEY).",
                f"Underlying error: {exc}",
            ],
        )

    if not rows or len(rows) < 2:
        return FetcherResult(
            status="partial",
            source="US Census ACS 5-year (2022)",
            data={"fips": fips},
            notes=["ACS returned no rows for this tract."],
        )

    header, values = rows[0], rows[1]
    record = dict(zip(header, values, strict=False))
    parsed: dict = {
        "fips": fips,
        "tract_name": record.get("NAME"),
    }
    for code, friendly in ACS_VARS.items():
        raw = record.get(code)
        try:
            parsed[friendly] = int(raw) if raw not in (None, "") else None
        except (TypeError, ValueError):
            parsed[friendly] = None
    return FetcherResult(
        status="ok",
        source="US Census ACS 5-year (2022, tract level)",
        data=parsed,
    )


@cached(key=lambda site: f"wb:{site.country_code}", ttl_days=180)
def _fetch_world_bank(site: ResolvedSite) -> FetcherResult:
    if not site.country_code:
        return FetcherResult(
            status="unavailable",
            source="World Bank Indicators",
            data=None,
            notes=["No country code resolved for this site."],
        )
    out: dict = {"country_code": site.country_code, "country": site.country}
    notes: list[str] = []
    for ind, friendly in WORLD_BANK_INDICATORS.items():
        try:
            payload = http.get_json(
                WORLD_BANK_URL.format(iso=site.country_code, ind=ind),
                params={"format": "json", "per_page": 5, "date": "2018:2023"},
            )
        except Exception as exc:
            notes.append(f"{friendly}: {exc}")
            continue
        if not isinstance(payload, list) or len(payload) < 2 or not payload[1]:
            notes.append(f"{friendly}: no data")
            continue
        # Use most recent non-null observation
        for row in payload[1]:
            if row.get("value") is not None:
                out[friendly] = row["value"]
                out[f"{friendly}_year"] = row["date"]
                break
    status = "ok" if any(k in out for k in WORLD_BANK_INDICATORS.values()) else "partial"
    return FetcherResult(
        status=status,
        source="World Bank Indicators (country level)",
        data=out,
        notes=notes,
    )
