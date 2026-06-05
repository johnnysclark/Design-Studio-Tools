"""16-sector wind rose: stacked polar bars colored by speed bin."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

BIN_COLORS = ["#cccccc", "#a6cee3", "#1f78b4", "#33a02c", "#ff7f00", "#e31a1c"]


def draw_wind_rose(wind_data: dict, out_path: Path) -> tuple[Path, str]:
    sectors = wind_data["sectors"]
    speed_labels = wind_data["speed_labels"]
    total = wind_data["total_hours"]

    n = len(sectors)
    theta = np.deg2rad([s["from_deg"] for s in sectors])
    width = 2 * math.pi / n

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"projection": "polar"})
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)

    bottoms = np.zeros(n)
    for i, label in enumerate(speed_labels):
        heights = np.array(
            [100 * s["bins"].get(label, 0) / max(total, 1) for s in sectors]
        )
        ax.bar(
            theta,
            heights,
            width=width * 0.9,
            bottom=bottoms,
            color=BIN_COLORS[i],
            edgecolor="white",
            linewidth=0.5,
            label=label,
        )
        bottoms += heights

    ax.set_title(
        f"Wind rose — prevailing {wind_data['prevailing_dir_cardinal']} "
        f"at {wind_data['mean_speed_mps']} m/s mean",
        fontsize=11,
        pad=15,
    )
    ax.legend(
        loc="lower right",
        bbox_to_anchor=(1.3, -0.05),
        fontsize=8,
        title="Beaufort band",
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    alt_text = (
        f"Wind rose. Prevailing wind from {wind_data['prevailing_dir_cardinal']} "
        f"({wind_data['prevailing_dir_pct']}% of hours). "
        f"Mean wind speed {wind_data['mean_speed_mps']} m/s. "
        f"Calm {wind_data['calm_pct']}% of the time. "
        f"Based on {total:,} hourly observations."
    )
    return out_path, alt_text
