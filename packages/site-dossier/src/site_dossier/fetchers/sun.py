"""Sun-path computation via pvlib. No HTTP — always succeeds."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import pvlib
from ds_common.geocode import ResolvedSite

from site_dossier.fetchers.base import degrade_on_failure
from site_dossier.models import FetcherResult

KEY_DATES = {
    "summer_solstice": "2024-06-21",
    "winter_solstice": "2024-12-21",
    "spring_equinox": "2024-03-20",
    "fall_equinox": "2024-09-22",
}


@degrade_on_failure("sun")
def fetch_sun(site: ResolvedSite) -> FetcherResult:
    tracks = {}
    sunrise_sunset = {}

    for label, day in KEY_DATES.items():
        times = pd.date_range(f"{day} 00:00", f"{day} 23:59", freq="15min", tz="UTC")
        sp = pvlib.solarposition.get_solarposition(
            times, latitude=site.lat, longitude=site.lon
        )
        # local solar time -> we still report UTC offsets; the chart shows altitude vs azimuth
        above = sp[sp["apparent_elevation"] > 0]
        tracks[label] = [
            {
                "hour_utc": ts.strftime("%H:%M"),
                "altitude_deg": round(float(row["apparent_elevation"]), 2),
                "azimuth_deg": round(float(row["azimuth"]), 2),
            }
            for ts, row in above.iterrows()
        ]
        if not above.empty:
            sunrise_sunset[label] = {
                "sunrise_utc": above.index[0].strftime("%H:%M"),
                "sunset_utc": above.index[-1].strftime("%H:%M"),
                "max_altitude_deg": round(float(above["apparent_elevation"].max()), 2),
                "max_alt_azimuth_deg": round(
                    float(above.loc[above["apparent_elevation"].idxmax(), "azimuth"]), 2
                ),
            }
        else:
            sunrise_sunset[label] = {
                "sunrise_utc": None,
                "sunset_utc": None,
                "max_altitude_deg": 0.0,
                "max_alt_azimuth_deg": None,
            }

    return FetcherResult(
        status="ok",
        source="pvlib.solarposition (computed locally)",
        data={
            "tracks": tracks,
            "key_dates": KEY_DATES,
            "sunrise_sunset": sunrise_sunset,
            "computed_at": datetime.utcnow().isoformat(),
        },
    )
