"""Typer-based CLI for site-dossier."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import typer
from ds_common.errors import FetchError
from ds_common.logging import configure as configure_logging
from rich.console import Console

from site_dossier import __version__
from site_dossier.pipeline import generate_dossier

app = typer.Typer(
    name="site-dossier",
    help="Generate a site dossier (climate, sun, wind, demographics, zoning) from an address or lat/lon.",
    no_args_is_help=False,
    add_completion=False,
)
console = Console(stderr=True)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"site-dossier {__version__}")
        raise typer.Exit()


@app.command()
def main(
    address: str | None = typer.Argument(
        None, help="Site address. Omit to use --lat/--lon."
    ),
    lat: float | None = typer.Option(None, "--lat", help="Latitude (-90 to 90)."),
    lon: float | None = typer.Option(None, "--lon", help="Longitude (-180 to 180)."),
    output_dir: Path = typer.Option(
        Path("./dossier_output"),
        "--output-dir",
        "-o",
        help="Where to write the dossier files.",
    ),
    formats: str = typer.Option(
        "md,pdf,3dm",
        "--formats",
        "-f",
        help="Comma-separated output formats. Options: md, pdf, 3dm.",
    ),
    sections: str | None = typer.Option(
        None,
        "--sections",
        "-s",
        help="Comma-separated sections to include. Default: all. Options: climate, wind, sun, demographics, zoning.",
    ),
    cache_dir: Path | None = typer.Option(
        None, "--cache-dir", help="Override the disk-cache directory."
    ),
    no_cache: bool = typer.Option(False, "--no-cache", help="Skip the cache for this run."),
    census_key: str | None = typer.Option(
        None,
        "--census-key",
        envvar="CENSUS_API_KEY",
        help="US Census API key. Optional; unlocks tract-level demographics.",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress non-error logging."),
    version: bool = typer.Option(
        False, "--version", callback=_version_callback, is_eager=True, help="Print version and exit."
    ),
) -> None:
    """Generate a site dossier."""
    level = "WARNING" if quiet else ("DEBUG" if verbose else "INFO")
    configure_logging(level)

    if not address and (lat is None or lon is None):
        console.print("[red]Error:[/red] provide an address or --lat/--lon.")
        raise typer.Exit(code=2)

    if no_cache:
        os.environ["DS_CACHE_DISABLE"] = "1"

    fmts = tuple(f.strip().lower() for f in formats.split(",") if f.strip())
    secs = (
        tuple(s.strip().lower() for s in sections.split(",") if s.strip())
        if sections
        else None
    )

    try:
        dossier = generate_dossier(
            address=address,
            lat=lat,
            lon=lon,
            output_dir=output_dir,
            formats=fmts,
            sections=secs,
            cache_dir=cache_dir,
            census_key=census_key,
        )
    except FetchError as e:
        console.print(f"[red]Geocoding failed:[/red] {e}")
        raise typer.Exit(code=3) from e
    except OSError as e:
        console.print(f"[red]Could not write output:[/red] {e}")
        raise typer.Exit(code=4) from e

    console.print(f"[green]Dossier generated for[/green] {dossier.site.display_name}")
    for label, path in (
        ("Markdown", dossier.markdown_path),
        ("PDF", dossier.pdf_path),
        ("Rhino .3dm", dossier.rhino_path),
        ("CSV", dossier.csv_path),
        ("Data JSON", dossier.data_json_path),
    ):
        if path:
            console.print(f"  {label}: {path}")

    degraded = [
        name
        for name, result in dossier.sections().items()
        if result.status != "ok"
    ]
    if degraded:
        console.print(
            f"[yellow]Degraded sections:[/yellow] {', '.join(degraded)} "
            "(see Notes & Data Quality in the dossier)."
        )


if __name__ == "__main__":  # pragma: no cover
    sys.exit(app())
