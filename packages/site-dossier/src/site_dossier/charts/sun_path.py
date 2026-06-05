"""Polar sun-path diagram. Altitude on the radial axis, azimuth on the angular axis."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from ds_common.geocode import ResolvedSite  # noqa: E402

LABEL_FOR_KEY = {
    "summer_solstice": "Summer solstice",
    "winter_solstice": "Winter solstice",
    "spring_equinox": "Spring equinox",
    "fall_equinox": "Fall equinox",
}
COLOR_FOR_KEY = {
    "summer_solstice": "#d62728",
    "winter_solstice": "#1f77b4",
    "spring_equinox": "#2ca02c",
    "fall_equinox": "#ff7f0e",
}


def draw_sun_path(
    sun_data: dict, site: ResolvedSite, out_path: Path
) -> tuple[Path, str]:
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"projection": "polar"})
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_rlim(90, 0)  # zenith at center
    ax.set_rticks([15, 30, 45, 60, 75])
    ax.set_rlabel_position(135)

    max_alt_overall = 0.0
    summer_alt = winter_alt = 0.0

    for key, label in LABEL_FOR_KEY.items():
        track = sun_data["tracks"].get(key, [])
        if not track:
            continue
        thetas = [math.radians(p["azimuth_deg"]) for p in track]
        rs = [90 - p["altitude_deg"] for p in track]
        ax.plot(thetas, rs, label=label, color=COLOR_FOR_KEY[key], linewidth=2)
        max_alt = max(p["altitude_deg"] for p in track)
        max_alt_overall = max(max_alt_overall, max_alt)
        if key == "summer_solstice":
            summer_alt = max_alt
        elif key == "winter_solstice":
            winter_alt = max_alt

    ax.legend(loc="lower right", bbox_to_anchor=(1.25, -0.05), fontsize=8)
    ax.set_title(
        f"Sun path at {site.lat:.3f}, {site.lon:.3f}", fontsize=11, pad=15
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    alt_text = (
        f"Polar sun-path diagram for {site.display_name}. "
        f"Maximum solar altitude: {summer_alt:.0f} degrees on the summer solstice, "
        f"{winter_alt:.0f} degrees on the winter solstice. "
        f"North is at the top; the sun arcs from east through south to west."
    )
    return out_path, alt_text
