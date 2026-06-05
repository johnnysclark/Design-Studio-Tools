"""rhino3dm helpers — shared so every tool in the kit writes consistent .3dm files.

Conventions:
- Units: meters
- Origin: site location (earth-anchor set so Rhino knows the lat/lon)
- Layers named with snake_case category prefixes (e.g., "Site", "Sun_Paths", "Wind_Rose")
- One File3dm per tool output; tools merge their geometry into it via the builder helpers.
"""

from __future__ import annotations

from pathlib import Path

import rhino3dm as r3


def new_doc(lat: float, lon: float, elevation_m: float = 0.0) -> r3.File3dm:
    """Create a fresh File3dm in meters with an earth anchor at the given lat/lon.

    rhino3dm exposes EarthAnchorPoint as a settable property on Settings, but in-place
    mutation of the returned anchor doesn't persist — we have to assign it back.
    """
    doc = r3.File3dm()
    doc.Settings.ModelUnitSystem = r3.UnitSystem.Meters

    anchor = doc.Settings.EarthAnchorPoint
    anchor.EarthBasepointLatitude = lat
    anchor.EarthBasepointLongitude = lon
    anchor.EarthBasepointElevation = elevation_m
    doc.Settings.EarthAnchorPoint = anchor
    return doc


def add_layer(
    doc: r3.File3dm,
    name: str,
    color: tuple[int, int, int, int] = (0, 0, 0, 255),
) -> int:
    """Add a layer; return its index (used as Attributes.LayerIndex on objects).

    `color` is (r, g, b, a) with 0-255 channels.
    """
    layer = r3.Layer()
    layer.Name = name
    layer.Color = color
    return doc.Layers.Add(layer)


def attrs(layer_index: int, name: str | None = None) -> r3.ObjectAttributes:
    a = r3.ObjectAttributes()
    a.LayerIndex = layer_index
    if name:
        a.Name = name
    return a


def add_polyline(
    doc: r3.File3dm,
    points: list[tuple[float, float, float]],
    layer_index: int,
    name: str | None = None,
) -> None:
    pl = r3.Polyline(len(points))
    for x, y, z in points:
        pl.Add(x, y, z)
    curve = pl.ToPolylineCurve()
    doc.Objects.AddCurve(curve, attrs(layer_index, name))


def add_point(
    doc: r3.File3dm,
    xyz: tuple[float, float, float],
    layer_index: int,
    name: str | None = None,
) -> None:
    p = r3.Point3d(*xyz)
    doc.Objects.AddPoint(p, attrs(layer_index, name))


def add_text_dot(
    doc: r3.File3dm,
    xyz: tuple[float, float, float],
    text: str,
    layer_index: int,
) -> None:
    # rhino3dm 8 takes (text, location, attributes) — not a constructed TextDot.
    doc.Objects.AddTextDot(text, r3.Point3d(*xyz), attrs(layer_index, text))


def add_line(
    doc: r3.File3dm,
    a: tuple[float, float, float],
    b: tuple[float, float, float],
    layer_index: int,
    name: str | None = None,
) -> None:
    line = r3.LineCurve(r3.Point3d(*a), r3.Point3d(*b))
    doc.Objects.AddCurve(line, attrs(layer_index, name))


def save(doc: r3.File3dm, path: Path | str) -> None:
    """Write the doc to disk in Rhino 7+ format."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.Write(str(path), 7)
