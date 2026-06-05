"""Hourly winds from Open-Meteo Archive, aggregated into 16-sector × 6-bin wind-rose stats."""

from __future__ import annotations

from datetime import date, timedelta

from ds_common import http
from ds_common.cache import cached
from ds_common.geocode import ResolvedSite
from ds_common.geometry import cardinal_from_deg

from site_dossier.fetchers.base import degrade_on_failure
from site_dossier.models import FetcherResult

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
N_SECTORS = 16
SECTOR_WIDTH = 360 / N_SECTORS  # 22.5
SPEED_BINS_MPS = [0.0, 1.5, 3.3, 5.4, 7.9, 10.7, float("inf")]
SPEED_LABELS = ["calm", "light", "gentle", "moderate", "fresh", "strong"]


@degrade_on_failure("wind")
@cached(key=lambda site: f"wind:{round(site.lat,2)}:{round(site.lon,2)}", ttl_days=90)
def fetch_wind(site: ResolvedSite) -> FetcherResult:
    end = date.today() - timedelta(days=7)  # archive usually has a 5-7 day lag
    start = end.replace(year=end.year - 10)
    payload = http.get_json(
        ARCHIVE_URL,
        params={
            "latitude": site.lat,
            "longitude": site.lon,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "hourly": "wind_speed_10m,wind_direction_10m",
            "wind_speed_unit": "ms",
        },
    )
    hourly = payload.get("hourly", {})
    speeds = hourly.get("wind_speed_10m") or []
    dirs = hourly.get("wind_direction_10m") or []
    if not speeds:
        return FetcherResult(
            status="unavailable",
            source="Open-Meteo Archive (hourly winds)",
            data=None,
            notes=["No hourly wind data returned."],
        )

    stats = _aggregate(speeds, dirs)
    return FetcherResult(
        status="ok",
        source=f"Open-Meteo Archive (10-year hourly, {start.year}-{end.year})",
        data=stats,
    )


def _aggregate(speeds: list[float | None], dirs: list[float | None]) -> dict:
    # 16 x 6 grid of hour counts
    grid = [[0] * len(SPEED_LABELS) for _ in range(N_SECTORS)]
    total = 0
    calm = 0
    sum_speed = 0.0
    n_speed = 0
    for s, d in zip(speeds, dirs, strict=False):
        if s is None or d is None:
            continue
        total += 1
        sum_speed += s
        n_speed += 1
        if s < SPEED_BINS_MPS[1]:
            calm += 1
            continue
        sector = int(((d + SECTOR_WIDTH / 2) % 360) // SECTOR_WIDTH)
        bin_idx = 0
        for i in range(1, len(SPEED_BINS_MPS) - 1):
            if s >= SPEED_BINS_MPS[i]:
                bin_idx = i
            else:
                break
        grid[sector][bin_idx] += 1

    if total == 0:
        return {"total_hours": 0}

    sector_totals = [sum(row) for row in grid]
    prevailing_idx = max(range(N_SECTORS), key=lambda i: sector_totals[i])
    prevailing_deg = prevailing_idx * SECTOR_WIDTH
    prevailing_pct = round(100 * sector_totals[prevailing_idx] / total, 1)

    return {
        "total_hours": total,
        "calm_hours": calm,
        "calm_pct": round(100 * calm / total, 1),
        "mean_speed_mps": round(sum_speed / n_speed, 2),
        "prevailing_dir_deg": prevailing_deg,
        "prevailing_dir_cardinal": cardinal_from_deg(prevailing_deg),
        "prevailing_dir_pct": prevailing_pct,
        "sectors": [
            {
                "sector": i,
                "from_deg": i * SECTOR_WIDTH,
                "cardinal": cardinal_from_deg(i * SECTOR_WIDTH),
                "total_hours": sector_totals[i],
                "pct": round(100 * sector_totals[i] / total, 2),
                "bins": dict(zip(SPEED_LABELS, grid[i], strict=False)),
            }
            for i in range(N_SECTORS)
        ],
        "speed_bins_mps": SPEED_BINS_MPS,
        "speed_labels": SPEED_LABELS,
    }
