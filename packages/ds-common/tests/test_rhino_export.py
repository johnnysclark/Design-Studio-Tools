"""Smoke test for the Rhino export helper — produces a .3dm and reads it back."""

import rhino3dm as r3
from ds_common import rhino_export as rx


def test_new_doc_sets_earth_anchor():
    doc = rx.new_doc(lat=40.75, lon=-73.99, elevation_m=10.0)
    anchor = doc.Settings.EarthAnchorPoint
    assert anchor.EarthBasepointLatitude == 40.75
    assert anchor.EarthBasepointLongitude == -73.99
    assert anchor.EarthBasepointElevation == 10.0
    assert doc.Settings.ModelUnitSystem == r3.UnitSystem.Meters


def test_add_layer_and_objects_round_trip(tmp_path):
    doc = rx.new_doc(lat=0.0, lon=0.0)
    site_layer = rx.add_layer(doc, "Site", color=(255, 0, 0, 255))
    sun_layer = rx.add_layer(doc, "Sun_Paths", color=(255, 200, 0, 255))

    rx.add_point(doc, (0, 0, 0), site_layer, name="origin")
    rx.add_polyline(doc, [(0, 0, 0), (1, 1, 1), (2, 0, 2)], sun_layer, name="track")
    rx.add_text_dot(doc, (0, 5, 0), "N", site_layer)
    rx.add_line(doc, (0, 0, 0), (0, 5, 0), site_layer, name="north")

    out = tmp_path / "test.3dm"
    rx.save(doc, out)
    assert out.exists()
    assert out.stat().st_size > 0

    reread = r3.File3dm.Read(str(out))
    assert reread is not None
    layer_names = {reread.Layers[i].Name for i in range(len(reread.Layers))}
    assert {"Site", "Sun_Paths"}.issubset(layer_names)
    # Should have at least the 4 geometry objects we added
    assert len(reread.Objects) >= 4
