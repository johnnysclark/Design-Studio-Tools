# site-dossier

Generate a **Site Dossier** for any address or lat/lon: climate normals, sun path, prevailing winds, demographics, and zoning — assembled into a Markdown report, a tagged PDF, and a `.3dm` sidecar that drops straight into Rhino.

Part of the [Design Studio Tools](../../README.md) kit.

## What you get

For each input site, the tool produces:

```
dossier_output/
├── dossier.md            # human-readable report (with screen-reader summary on top)
├── dossier.pdf           # tagged PDF (PDF/UA-1), same content
├── dossier.3dm           # Rhino sidecar: site point, sun-path curves, wind rose
├── sun_wind_hourly.csv   # raw hourly data, Ladybug-compatible columns
├── charts/
│   ├── sun_path.png
│   ├── wind_rose.png
│   └── climograph.png
└── data.json             # raw FetcherResult dump for reproducibility
```

## CLI

```bash
# By address
uv run site-dossier "350 5th Ave, New York, NY"

# By coordinates
uv run site-dossier --lat 40.7484 --lon -73.9857

# Specific sections only, custom output dir
uv run site-dossier "Sydney Opera House" -o ./out --sections climate,sun

# Skip PDF and 3dm, just Markdown
uv run site-dossier "1600 Pennsylvania Ave" --formats md
```

Flags:

| Flag | Default | Notes |
|---|---|---|
| positional `address` OR `--lat`/`--lon` | — | One required |
| `--output-dir`, `-o` | `./dossier_output` | |
| `--formats`, `-f` | `md,pdf,3dm` | csv subset |
| `--sections`, `-s` | all | csv: `climate,wind,sun,demographics,zoning` |
| `--cache-dir` | XDG default | also via `DS_CACHE_DIR` env |
| `--no-cache` | off | skip the disk cache for this run |
| `--census-key` | `$CENSUS_API_KEY` | optional; unlocks tract-level US demographics |
| `--verbose`, `-v` / `--quiet`, `-q` | INFO | log level |

Exit codes: `0` produced (even if some sections are degraded), `2` invalid input, `3` geocode failed, `4` write failed.

## Library

```python
from site_dossier import generate_dossier

d = generate_dossier(address="350 5th Ave, New York, NY")
print(d.markdown_path, d.pdf_path, d.rhino_path)
print(d.screen_reader_summary)
print(d.climate.data["annual"]["mean_temp_c"])
```

Build pieces yourself:

```python
from ds_common.geocode import geocode
from site_dossier.fetchers import fetch_climate

site = geocode("Sydney Opera House")
climate = fetch_climate(site)
```

## Data sources

| Section | Source |
|---|---|
| Geocoding | US Census Geocoder → Nominatim (OSM) |
| Climate normals | Open-Meteo Climate API (1991-2020) |
| Winds | Open-Meteo Archive (10-year hourly) |
| Sun path | `pvlib` (computed locally) |
| Demographics | US Census ACS 5-year (with `CENSUS_API_KEY`) → World Bank fallback |
| Zoning | Municipal portals (NYC, LA, SF, Chicago, Boston, Seattle) → OSM Overpass landuse → web-search citation |

Every section degrades gracefully: if an API fails, the section renders as an "unavailable" panel with the reason, and the rest of the dossier still generates.

## Accessibility

Every dossier opens with a deterministic plain-language summary for screen-reader users. Charts carry alt text generated from the underlying data. The PDF is tagged (PDF/UA-1) so headings and alt text are exposed to assistive tech. Color is never the sole carrier of meaning.

## Caching

Disk-cache keyed by rounded lat/lon (~1 km cells). TTLs: climate 365d, wind 90d, demographics 30d, zoning 7d, geocoding 30d. Cache dir defaults to `$XDG_CACHE_HOME/design-studio-tools/`.
