"""Pydantic models for inputs, fetcher results, and the assembled dossier."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from ds_common.geocode import ResolvedSite
from pydantic import BaseModel, Field, model_validator

Status = Literal["ok", "partial", "unavailable"]


class SiteInput(BaseModel):
    """Either an address or a lat/lon pair must be supplied."""

    address: str | None = None
    lat: float | None = None
    lon: float | None = None

    @model_validator(mode="after")
    def _one_of(self) -> SiteInput:
        if self.address is None and (self.lat is None or self.lon is None):
            raise ValueError("Provide either `address` or both `lat` and `lon`.")
        if self.lat is not None and not (-90 <= self.lat <= 90):
            raise ValueError("lat must be between -90 and 90")
        if self.lon is not None and not (-180 <= self.lon <= 180):
            raise ValueError("lon must be between -180 and 180")
        return self

    def as_query(self) -> str:
        if self.address:
            return self.address
        return f"{self.lat},{self.lon}"


class FetcherResult(BaseModel):
    """Every fetcher returns one of these — never raises on network failure."""

    status: Status
    source: str
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    data: dict[str, Any] | None = None
    notes: list[str] = Field(default_factory=list)


# Per-section aliases for readability at call sites. Each is just FetcherResult —
# the section identity is carried by where the value lives on the Dossier.
ClimateData = FetcherResult
WindData = FetcherResult
SunData = FetcherResult
DemographicsData = FetcherResult
ZoningData = FetcherResult


class Dossier(BaseModel):
    """The full assembled dossier returned by `generate_dossier()`."""

    site: ResolvedSite
    climate: FetcherResult
    wind: FetcherResult
    sun: FetcherResult
    demographics: FetcherResult
    zoning: FetcherResult
    screen_reader_summary: str
    chart_paths: dict[str, Path] = Field(default_factory=dict)
    markdown_path: Path | None = None
    pdf_path: Path | None = None
    rhino_path: Path | None = None
    csv_path: Path | None = None
    data_json_path: Path | None = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    def sections(self) -> dict[str, FetcherResult]:
        return {
            "climate": self.climate,
            "wind": self.wind,
            "sun": self.sun,
            "demographics": self.demographics,
            "zoning": self.zoning,
        }
