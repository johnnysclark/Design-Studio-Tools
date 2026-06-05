"""Climate normals via Open-Meteo Climate API (CMIP6 downscaled, 1991-2020 baseline)."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from ds_common import http
from ds_common.cache import cached
from ds_common.geocode import ResolvedSite

from site_dossier.fetchers.base import degrade_on_failure
from site_dossier.models import FetcherResult

CLIMATE_URL = "https://climate-api.open-meteo.com/v1/climate"
MODEL = "EC_Earth3P_HR"
START, END = "1991-01-01", "2020-12-31"


@degrade_on_failure("climate")
@cached(key=lambda site: f"climate:{round(site.lat,2)}:{round(site.lon,2)}", ttl_days=365)
def fetch_climate(site: ResolvedSite) -> FetcherResult:
    payload = http.get_json(
        CLIMATE_URL,
        params={
            "latitude": site.lat,
            "longitude": site.lon,
            "start_date": START,
            "end_date": END,
            "models": MODEL,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        },
    )
    daily = payload.get("daily", {})
    times = daily.get("time", [])
    tmax = daily.get("temperature_2m_max", [])
    tmin = daily.get("temperature_2m_min", [])
    pr = daily.get("precipitation_sum", [])

    if not times:
        return FetcherResult(
            status="unavailable",
            source=f"Open-Meteo Climate ({MODEL})",
            data=None,
            notes=["No daily series returned for this location."],
        )

    monthly = _aggregate_monthly(times, tmax, tmin, pr)
    annual = _derive_annual(monthly)

    return FetcherResult(
        status="ok",
        source=f"Open-Meteo Climate ({MODEL}, {START[:4]}-{END[:4]} normals)",
        data={"monthly": monthly, "annual": annual},
    )


def _aggregate_monthly(
    times: list[str], tmax: list[float], tmin: list[float], pr: list[float]
) -> list[dict]:
    """Return [{month: 1..12, tmax_mean_c, tmin_mean_c, tmean_c, precip_sum_mm}]."""
    buckets: dict[int, dict[str, list[float]]] = defaultdict(
        lambda: {"tmax": [], "tmin": [], "pr": []}
    )
    for t, hi, lo, p in zip(times, tmax, tmin, pr, strict=False):
        if hi is None or lo is None or p is None:
            continue
        month = datetime.fromisoformat(t).month
        buckets[month]["tmax"].append(hi)
        buckets[month]["tmin"].append(lo)
        buckets[month]["pr"].append(p)

    out = []
    for m in range(1, 13):
        b = buckets[m]
        if not b["tmax"]:
            out.append(
                {"month": m, "tmax_mean_c": None, "tmin_mean_c": None, "tmean_c": None, "precip_sum_mm": None}
            )
            continue
        tmax_mean = sum(b["tmax"]) / len(b["tmax"])
        tmin_mean = sum(b["tmin"]) / len(b["tmin"])
        # precip_sum_mm = average monthly total (sum across days, average across years)
        years = max(1, len(b["pr"]) // 30)
        precip_sum = sum(b["pr"]) / years
        out.append(
            {
                "month": m,
                "tmax_mean_c": round(tmax_mean, 1),
                "tmin_mean_c": round(tmin_mean, 1),
                "tmean_c": round((tmax_mean + tmin_mean) / 2, 1),
                "precip_sum_mm": round(precip_sum, 1),
            }
        )
    return out


def _derive_annual(monthly: list[dict]) -> dict:
    valid = [m for m in monthly if m["tmean_c"] is not None]
    if not valid:
        return {"mean_temp_c": None, "annual_precip_mm": None, "warmest_month": None, "coldest_month": None}
    mean_temp = sum(m["tmean_c"] for m in valid) / len(valid)
    annual_precip = sum(m["precip_sum_mm"] for m in valid)
    warmest = max(valid, key=lambda m: m["tmean_c"])
    coldest = min(valid, key=lambda m: m["tmean_c"])
    return {
        "mean_temp_c": round(mean_temp, 1),
        "annual_precip_mm": round(annual_precip, 1),
        "warmest_month": warmest["month"],
        "warmest_month_tmean_c": warmest["tmean_c"],
        "coldest_month": coldest["month"],
        "coldest_month_tmean_c": coldest["tmean_c"],
    }
