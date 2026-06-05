# Design Studio Tools

A kit of small, focused utilities for an architecture & design studio. Each tool tackles one slice of the daily work — site research, environmental analysis, model audits, spec compilation, code checks — and emits outputs that drop straight into our design process: readable reports for the team, citations for the file, and `.3dm` geometry for Rhino.

This is the first of many. The shape is intentionally modular: each tool is independently installable, each follows the same patterns, and each plays nicely with our Rhino-centered workflow.

## Why a kit (and not one big app)

- **Different problems want different tools.** A site-research tool and a daylight study don't belong in the same UI; bundling them creates friction.
- **Tools age at different rates.** Public APIs change, building codes update, modeling conventions evolve. A kit lets us patch one tool without disturbing the others.
- **The studio adds its own.** Anyone on the team can scaffold a new tool from the template in [`docs/adding-a-new-tool.md`](docs/adding-a-new-tool.md) without re-deciding the architecture.

## Principles every tool in the kit follows

1. **CLI + Python library, both.** Designers use the CLI; future automation imports the library. Same code path.
2. **Rhino-friendly outputs.** Where geometry helps, the tool writes a `.3dm` sidecar using `rhino3dm` (pure Python — no Rhino install required to run). Designers drag the file into the model.
3. **Accessibility on by default.** Every human-readable output opens with a plain-language summary for screen readers, generated deterministically from the data. Charts carry alt text. PDFs are tagged.
4. **Graceful degradation.** External APIs fail; the tool keeps going and labels what's missing rather than crashing the run.
5. **Cite your sources.** Every fact in every output names the dataset and the date it was fetched.
6. **Free and open data first.** No API keys required to get a useful result; optional keys (e.g., Census) unlock more detail.

## Tools

### Available now

| Tool | Description |
|---|---|
| [`site-dossier`](packages/site-dossier/) | Pulls climate normals, sun path, prevailing winds, demographics, and zoning for any address or lat/lon. Outputs Markdown + tagged PDF + a `.3dm` sidecar with sun-path curves, wind-rose geometry, and a site/north marker. |

### On the roadmap

These are sketches, not commitments — they show the kind of work this kit is intended to grow into. Anything in this list can be promoted to a real package when the studio needs it.

- **shading-study** — solar exposure & shadow casting against a Rhino massing model across the year.
- **massing-envelope** — generate the zoning envelope (FAR, setbacks, height limits) as Rhino geometry from a parcel address.
- **daylight-factor** — quick daylight metrics from a Rhino interior model.
- **material-takeoff** — bill of materials extracted from a Rhino model's layers/blocks.
- **embodied-carbon** — pair material-takeoff with EPD data for a project-level carbon estimate.
- **code-checker** — flag egress, occupancy, and accessibility issues from a Rhino floor plan against the local code.
- **plant-palette** — climate-appropriate plant lists by hardiness zone + native species filter.
- **view-analysis** — sightline / view-cone studies from points in a Rhino model.
- **permit-checklist** — jurisdiction-specific submittal checklist from an address.
- **project-brief** — structured brief generator from an RFP or client questionnaire.

Suggest more by opening an issue.

## Layout

```
Design-Studio-Tools/
├── packages/
│   ├── ds-common/      # shared helpers reused by every tool (HTTP, cache, geocode, rhino3dm)
│   └── site-dossier/   # the first tool
├── docs/
│   └── adding-a-new-tool.md
└── .github/workflows/  # lint + test across the workspace
```

This is a [`uv`](https://github.com/astral-sh/uv) workspace: one lockfile, per-tool dependency surfaces, each tool independently `pip install`-able. New tools land under `packages/<tool-name>/` and are picked up automatically.

## Install (development)

```bash
# install uv: https://github.com/astral-sh/uv
uv sync
```

## Use a tool

```bash
uv run site-dossier "350 5th Ave, New York, NY"
```

Per-tool flags and library APIs live in each tool's README.

## Tests & lint

```bash
uv run pytest
uv run ruff check .
```

## Contributing a new tool

Read [`docs/adding-a-new-tool.md`](docs/adding-a-new-tool.md). The short version:

1. Copy the `site-dossier` package as a template.
2. Reuse `ds_common` for HTTP, caching, geocoding, and Rhino export.
3. Follow the fetcher pattern (degrades gracefully, caches by lat/lon).
4. Add an accessibility summary at the top of every output.
5. Register the tool in the table above.
