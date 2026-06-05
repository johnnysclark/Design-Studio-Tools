"""Shared fixtures for site-dossier tests.

We avoid live network calls by patching the fetchers via the public API surface.
The fixtures here construct minimal but realistic FetcherResults for each section.
"""

from __future__ import annotations

from datetime import datetime

import pytest
from ds_common.geocode import ResolvedSite
from site_dossier.models import (
    ClimateData,
    DemographicsData,
    SunData,
    WindData,
    ZoningData,
)


@pytest.fixture
def nyc_site() -> ResolvedSite:
    return ResolvedSite(
        lat=40.7484,
        lon=-73.9857,
        display_name="350 5th Ave, New York, NY 10118, USA",
        address="350 5th Ave, New York, NY 10118",
        admin1="New York",
        admin2="New York County",
        country="United States",
        country_code="US",
        elevation_m=10.0,
        source="us-census",
    )


@pytest.fixture
def climate_ok() -> ClimateData:
    monthly = [
        {
            "month": m,
            "tmax_mean_c": 5 + m,
            "tmin_mean_c": -3 + m,
            "tmean_c": 1 + m,
            "precip_sum_mm": 80 + (m % 3) * 10,
        }
        for m in range(1, 13)
    ]
    annual = {
        "mean_temp_c": 7.5,
        "annual_precip_mm": 1020.0,
        "warmest_month": 7,
        "warmest_month_tmean_c": 25.0,
        "coldest_month": 1,
        "coldest_month_tmean_c": -1.0,
    }
    return ClimateData(
        status="ok",
        source="Open-Meteo Climate (test fixture)",
        fetched_at=datetime.utcnow(),
        data={"monthly": monthly, "annual": annual},
    )


@pytest.fixture
def wind_ok() -> WindData:
    sectors = [
        {
            "sector": i,
            "from_deg": i * 22.5,
            "cardinal": ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                         "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"][i],
            "total_hours": 500 if i != 12 else 2000,  # W dominant
            "pct": 2.3 if i != 12 else 22.7,
            "bins": {"calm": 0, "light": 100, "gentle": 200, "moderate": 150, "fresh": 40, "strong": 10},
        }
        for i in range(16)
    ]
    return WindData(
        status="ok",
        source="Open-Meteo Archive (test fixture)",
        fetched_at=datetime.utcnow(),
        data={
            "total_hours": sum(s["total_hours"] for s in sectors),
            "calm_hours": 200,
            "calm_pct": 1.8,
            "mean_speed_mps": 4.1,
            "prevailing_dir_deg": 270.0,
            "prevailing_dir_cardinal": "W",
            "prevailing_dir_pct": 22.7,
            "sectors": sectors,
            "speed_bins_mps": [0.0, 1.5, 3.3, 5.4, 7.9, 10.7, float("inf")],
            "speed_labels": ["calm", "light", "gentle", "moderate", "fresh", "strong"],
        },
    )


@pytest.fixture
def sun_ok() -> SunData:
    # Two hours of altitude/azimuth for the summer solstice; enough to render and chart.
    summer = [
        {"hour_utc": "12:00", "altitude_deg": 72.5, "azimuth_deg": 180.0},
        {"hour_utc": "15:00", "altitude_deg": 50.0, "azimuth_deg": 240.0},
    ]
    winter = [
        {"hour_utc": "12:00", "altitude_deg": 26.0, "azimuth_deg": 180.0},
    ]
    return SunData(
        status="ok",
        source="pvlib (test fixture)",
        data={
            "tracks": {
                "summer_solstice": summer,
                "winter_solstice": winter,
                "spring_equinox": [{"hour_utc": "12:00", "altitude_deg": 49.0, "azimuth_deg": 180.0}],
                "fall_equinox": [{"hour_utc": "12:00", "altitude_deg": 49.0, "azimuth_deg": 180.0}],
            },
            "key_dates": {
                "summer_solstice": "2024-06-21",
                "winter_solstice": "2024-12-21",
                "spring_equinox": "2024-03-20",
                "fall_equinox": "2024-09-22",
            },
            "sunrise_sunset": {
                "summer_solstice": {"sunrise_utc": "05:24", "sunset_utc": "20:30",
                                    "max_altitude_deg": 72.5, "max_alt_azimuth_deg": 180.0},
                "winter_solstice": {"sunrise_utc": "07:17", "sunset_utc": "16:32",
                                    "max_altitude_deg": 26.0, "max_alt_azimuth_deg": 180.0},
                "spring_equinox": {"sunrise_utc": "06:50", "sunset_utc": "19:00",
                                   "max_altitude_deg": 49.0, "max_alt_azimuth_deg": 180.0},
                "fall_equinox": {"sunrise_utc": "06:48", "sunset_utc": "18:58",
                                 "max_altitude_deg": 49.0, "max_alt_azimuth_deg": 180.0},
            },
        },
    )


@pytest.fixture
def demographics_ok() -> DemographicsData:
    return DemographicsData(
        status="ok",
        source="US Census ACS (test fixture)",
        data={
            "fips": {"state": "36", "county": "061", "tract": "008600", "block": "1000"},
            "tract_name": "Census Tract 86, New York County, New York",
            "total_population": 4500,
            "median_household_income_usd": 120000,
            "median_home_value_usd": 1800000,
            "median_gross_rent_usd": 3200,
        },
    )


@pytest.fixture
def zoning_ok() -> ZoningData:
    return ZoningData(
        status="ok",
        source="NYC ZoLa (test fixture)",
        data={
            "portal": "nyc",
            "zoning_code": "C5-3",
            "description": "Special Midtown District",
            "raw_first_record": {"zonedist1": "C5-3"},
            "query_url": "https://example.com/zola?lat=40.74&lon=-73.98",
        },
    )


@pytest.fixture
def zoning_degraded() -> ZoningData:
    return ZoningData(
        status="partial",
        source="manual lookup required",
        data={
            "search_query": "zoning 350 5th Ave, New York, NY",
            "search_url": "https://duckduckgo.com/?q=zoning+...",
            "locality": "New York County",
        },
        notes=["No municipal zoning API is registered for this locality."],
    )


@pytest.fixture
def climate_unavailable() -> ClimateData:
    return ClimateData(
        status="unavailable",
        source="Open-Meteo Climate",
        data=None,
        notes=["ConnectionError: Network unreachable"],
    )
