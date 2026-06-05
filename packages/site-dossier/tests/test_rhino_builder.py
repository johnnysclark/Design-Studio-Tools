import csv

import rhino3dm as r3
from site_dossier.rhino.builder import build_rhino_sidecar


def test_build_sidecar_writes_3dm_and_csv(tmp_path, nyc_site, sun_ok, wind_ok):
    out_3dm, out_csv = build_rhino_sidecar(
        site=nyc_site, sun=sun_ok, wind=wind_ok, output_dir=tmp_path
    )
    assert out_3dm.exists() and out_3dm.stat().st_size > 0
    assert out_csv.exists() and out_csv.stat().st_size > 0

    doc = r3.File3dm.Read(str(out_3dm))
    assert doc is not None

    # Earth anchor matches input
    anchor = doc.Settings.EarthAnchorPoint
    assert abs(anchor.EarthBasepointLatitude - nyc_site.lat) < 1e-6
    assert abs(anchor.EarthBasepointLongitude - nyc_site.lon) < 1e-6

    # All four layers present
    names = {doc.Layers[i].Name for i in range(len(doc.Layers))}
    assert {"Site", "Sun_Paths", "Wind_Rose", "Annotations"}.issubset(names)

    # Objects exist (site point, north arrow, sun polylines, wind spokes, ...)
    assert len(doc.Objects) >= 10

    # CSV has expected columns and at least one sun + one wind row
    with out_csv.open() as f:
        rows = list(csv.DictReader(f))
    categories = {r["category"] for r in rows}
    assert {"sun", "wind_summary", "meta"}.issubset(categories)


def test_build_sidecar_degrades_when_sections_unavailable(tmp_path, nyc_site):
    from site_dossier.models import SunData, WindData

    sun = SunData(status="unavailable", source="x", data=None, notes=["no data"])
    wind = WindData(status="unavailable", source="x", data=None, notes=["no data"])

    out_3dm, out_csv = build_rhino_sidecar(
        site=nyc_site, sun=sun, wind=wind, output_dir=tmp_path
    )
    # Should still produce both files, with site marker but no sun/wind geometry
    assert out_3dm.exists()
    assert out_csv.exists()

    doc = r3.File3dm.Read(str(out_3dm))
    names = {doc.Layers[i].Name for i in range(len(doc.Layers))}
    assert "Site" in names
