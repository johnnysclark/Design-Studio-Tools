"""Orchestrator: validates input, geocodes, fans out fetchers, assembles outputs."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from ds_common.cache import set_cache_dir
from ds_common.geocode import geocode
from ds_common.logging import get_logger

from site_dossier.charts import generate_charts
from site_dossier.fetchers import (
    fetch_climate,
    fetch_demographics,
    fetch_sun,
    fetch_wind,
    fetch_zoning,
)
from site_dossier.models import (
    ClimateData,
    DemographicsData,
    Dossier,
    FetcherResult,
    SiteInput,
    SunData,
    WindData,
    ZoningData,
)
from site_dossier.render.markdown import render_markdown
from site_dossier.render.pdf import render_pdf
from site_dossier.render.summary import generate_summary
from site_dossier.rhino.builder import build_rhino_sidecar

log = get_logger(__name__)

ALL_SECTIONS = ("climate", "wind", "sun", "demographics", "zoning")
DEFAULT_FORMATS: tuple[str, ...] = ("md", "pdf", "3dm")

_FETCHERS = {
    "climate": (fetch_climate, ClimateData),
    "wind": (fetch_wind, WindData),
    "sun": (fetch_sun, SunData),
    "demographics": (fetch_demographics, DemographicsData),
    "zoning": (fetch_zoning, ZoningData),
}


def _unavailable(source: str, reason: str, cls: type[FetcherResult]) -> FetcherResult:
    return cls(status="unavailable", source=source, data=None, notes=[reason])


def generate_dossier(
    address: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    output_dir: Path | str = Path("./dossier_output"),
    formats: tuple[str, ...] = DEFAULT_FORMATS,
    sections: tuple[str, ...] | None = None,
    cache_dir: Path | str | None = None,
    census_key: str | None = None,
) -> Dossier:
    """End-to-end dossier generation.

    Args:
        address: free-form address. Mutually exclusive with lat/lon.
        lat, lon: explicit coordinates.
        output_dir: where to write dossier.md, dossier.pdf, dossier.3dm, etc.
        formats: subset of ("md", "pdf", "3dm").
        sections: subset of ALL_SECTIONS. Default: all.
        cache_dir: override the disk cache directory.
        census_key: optional US Census API key for tract-level demographics.

    Returns:
        A fully populated Dossier object with all output paths set.
    """
    inp = SiteInput(address=address, lat=lat, lon=lon)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if cache_dir is not None:
        set_cache_dir(cache_dir)

    selected = tuple(sections) if sections else ALL_SECTIONS
    log.info("dossier.start", site=inp.as_query(), sections=selected, formats=formats)

    # 1. Geocode (mandatory, raises FetchError on failure)
    site = geocode(inp.as_query())
    log.info("dossier.geocoded", lat=site.lat, lon=site.lon, source=site.source)

    # 2. Fetchers in parallel
    results: dict[str, FetcherResult] = {}
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {}
        for name in ALL_SECTIONS:
            fetcher, cls = _FETCHERS[name]
            if name not in selected:
                results[name] = _unavailable(
                    "site-dossier", f"Section {name!r} excluded via --sections.", cls
                )
                continue
            kwargs: dict[str, Any] = {}
            if name == "demographics":
                kwargs["census_key"] = census_key
            futures[name] = pool.submit(fetcher, site, **kwargs)
        for name, fut in futures.items():
            try:
                results[name] = fut.result()
            except Exception as exc:  # pragma: no cover - the decorator catches inside the fetcher
                log.warning("fetcher.failed", section=name, error=str(exc))
                _, cls = _FETCHERS[name]
                results[name] = _unavailable(name, f"Unhandled error: {exc}", cls)

    climate = results["climate"]
    wind = results["wind"]
    sun = results["sun"]
    demographics = results["demographics"]
    zoning = results["zoning"]

    # 3. Charts (PNGs)
    chart_paths = generate_charts(
        site=site,
        climate=climate,
        wind=wind,
        sun=sun,
        output_dir=output_dir / "charts",
    )

    # 4. Screen-reader summary
    summary = generate_summary(
        site=site,
        climate=climate,
        wind=wind,
        sun=sun,
        demographics=demographics,
        zoning=zoning,
    )

    dossier = Dossier(
        site=site,
        climate=climate,
        wind=wind,
        sun=sun,
        demographics=demographics,
        zoning=zoning,
        screen_reader_summary=summary,
        chart_paths=chart_paths,
    )

    # 5. Rhino sidecar (.3dm + CSV)
    if "3dm" in formats:
        rhino_path, csv_path = build_rhino_sidecar(
            site=site, sun=sun, wind=wind, output_dir=output_dir
        )
        dossier.rhino_path = rhino_path
        dossier.csv_path = csv_path

    # 6. Markdown
    if "md" in formats or "pdf" in formats:
        md_path = output_dir / "dossier.md"
        render_markdown(dossier, md_path)
        dossier.markdown_path = md_path

    # 7. PDF
    if "pdf" in formats:
        pdf_path = output_dir / "dossier.pdf"
        render_pdf(dossier.markdown_path, pdf_path)
        dossier.pdf_path = pdf_path

    # 8. Raw data JSON for reproducibility
    data_json_path = output_dir / "data.json"
    data_json_path.write_text(
        json.dumps(
            {
                "site": dossier.site.model_dump(mode="json"),
                "climate": dossier.climate.model_dump(mode="json"),
                "wind": dossier.wind.model_dump(mode="json"),
                "sun": dossier.sun.model_dump(mode="json"),
                "demographics": dossier.demographics.model_dump(mode="json"),
                "zoning": dossier.zoning.model_dump(mode="json"),
                "screen_reader_summary": dossier.screen_reader_summary,
                "generated_at": dossier.generated_at.isoformat(),
            },
            indent=2,
            default=str,
        )
    )
    dossier.data_json_path = data_json_path

    log.info(
        "dossier.done",
        degraded=[n for n, r in dossier.sections().items() if r.status != "ok"],
    )
    return dossier
