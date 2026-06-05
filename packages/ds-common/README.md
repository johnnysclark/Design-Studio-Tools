# ds-common

Shared utilities reused by every tool in the [Design Studio Tools](../../README.md) kit.

## What lives here

| Module | Purpose |
|---|---|
| `ds_common.http` | Pre-configured `httpx` client with retries, timeouts, and a polite User-Agent. |
| `ds_common.cache` | `diskcache`-backed decorator, XDG-aware cache directory. |
| `ds_common.geocode` | US Census Geocoder (primary) + Nominatim (fallback). Returns a `ResolvedSite`. |
| `ds_common.geometry` | Lat/lon parsing, bbox helpers, distance math. |
| `ds_common.rhino_export` | `rhino3dm.File3dm` helpers: layers, units, earth anchor, simple curves and text dots. |
| `ds_common.logging` | `structlog` configuration. |
| `ds_common.errors` | `FetchError`, `DegradedSection` sentinel. |

This package is not intended for end-users. It exists so each tool package stays small and consistent. See [`docs/adding-a-new-tool.md`](../../docs/adding-a-new-tool.md) for how tools consume it.
