"""Climograph: monthly precipitation bars + temperature range line."""

from __future__ import annotations

import calendar
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def draw_climograph(climate_data: dict, out_path: Path) -> tuple[Path, str]:
    months = list(range(1, 13))
    month_labels = [calendar.month_abbr[m] for m in months]
    monthly = climate_data["monthly"]

    pr = [m["precip_sum_mm"] or 0 for m in monthly]
    tmax = [m["tmax_mean_c"] for m in monthly]
    tmin = [m["tmin_mean_c"] for m in monthly]

    fig, ax_pr = plt.subplots(figsize=(8, 4.5))
    ax_pr.bar(months, pr, color="#4682b4", alpha=0.6, label="Precipitation (mm)")
    ax_pr.set_xlabel("Month")
    ax_pr.set_ylabel("Precipitation (mm)", color="#4682b4")
    ax_pr.tick_params(axis="y", labelcolor="#4682b4")
    ax_pr.set_xticks(months)
    ax_pr.set_xticklabels(month_labels)
    ax_pr.grid(axis="y", linestyle="--", alpha=0.3)

    ax_t = ax_pr.twinx()
    ax_t.plot(months, tmax, color="#d62728", marker="o", label="Mean daily max (°C)")
    ax_t.plot(months, tmin, color="#1f77b4", marker="o", label="Mean daily min (°C)")
    ax_t.fill_between(months, tmin, tmax, color="#d62728", alpha=0.08)
    ax_t.set_ylabel("Temperature (°C)")

    lines1, labels1 = ax_pr.get_legend_handles_labels()
    lines2, labels2 = ax_t.get_legend_handles_labels()
    ax_pr.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=8)

    annual = climate_data.get("annual") or {}
    ax_pr.set_title(
        f"Climate normals 1991-2020 — "
        f"mean {annual.get('mean_temp_c', '?')}°C, "
        f"{annual.get('annual_precip_mm', '?')} mm/yr"
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    wettest = max(monthly, key=lambda m: m["precip_sum_mm"] or 0)
    driest = min(monthly, key=lambda m: m["precip_sum_mm"] or 0)
    alt_text = (
        f"Climograph showing monthly climate normals. "
        f"Annual mean temperature {annual.get('mean_temp_c', 'unknown')} degrees Celsius. "
        f"Annual precipitation {annual.get('annual_precip_mm', 'unknown')} millimeters. "
        f"Wettest month: {calendar.month_name[wettest['month']]} "
        f"({wettest['precip_sum_mm']} mm). "
        f"Driest month: {calendar.month_name[driest['month']]} "
        f"({driest['precip_sum_mm']} mm)."
    )
    return out_path, alt_text
