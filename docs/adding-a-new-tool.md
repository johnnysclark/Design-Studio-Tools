# Adding a new tool to the kit

Every tool in `Design-Studio-Tools` follows the same shape so designers (and future-you) can pick one up without re-learning the layout.

## 1. Scaffold

```
packages/<tool-name>/
├── pyproject.toml          # depends on ds-common; declares a CLI entry point
├── README.md               # one-pager: what it does, install, usage examples
├── src/<tool_module>/
│   ├── __init__.py         # exports the main library function
│   ├── cli.py              # typer app
│   ├── pipeline.py         # orchestrator: input → fetchers → output
│   ├── models.py           # pydantic v2 input/output models
│   ├── fetchers/           # one file per external data source
│   ├── render/             # markdown / pdf / other output formats
│   └── rhino/              # optional: .3dm export, uses ds_common.rhino_export
└── tests/
    ├── conftest.py
    └── test_*.py
```

## 2. Use the shared utilities

Always reach for `ds_common` before writing new infra:

- `ds_common.http` — pre-configured `httpx` session (retries, timeouts, User-Agent).
- `ds_common.cache` — `diskcache`-backed decorator, XDG-aware cache dir.
- `ds_common.geocode` — Census Geocoder + Nominatim fallback, returns `ResolvedSite`.
- `ds_common.rhino_export` — `rhino3dm.File3dm` helpers (layers, units, earth anchor).
- `ds_common.errors` — `FetchError`, `DegradedSection` sentinel.

## 3. Follow the fetcher pattern

Each fetcher returns a `FetcherResult` and is wrapped in `@degrade_on_failure` — network failures degrade the section, not the whole run. See `packages/site-dossier/src/site_dossier/fetchers/climate.py` for the canonical example.

## 4. Accessibility

- Generate a plain-language "screen-reader summary" at the top of every human-readable output, deterministically from the data (no LLM).
- Every chart embedded in markdown has descriptive alt text generated from the underlying data.
- PDFs are tagged (PDF/UA-1 via WeasyPrint).
- Semantic heading hierarchy; never skip levels.

## 5. Register the tool

- Add to the table in the repo-root `README.md`.
- Declare the CLI entry point in `pyproject.toml`:

```toml
[project.scripts]
<tool-name> = "<tool_module>.cli:app"
```

- Add the package to the workspace (it's auto-included via the `packages/*` glob).

## 6. Tests

- Use `vcrpy` cassettes for fetcher tests so CI doesn't hit real APIs.
- Include an end-to-end test that runs the full pipeline against a cached fixture and asserts the output files.
- Add a CLI smoke test (`--version`, `--help`, one fixture run).
