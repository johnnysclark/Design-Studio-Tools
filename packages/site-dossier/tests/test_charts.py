def test_climograph_writes_png(tmp_path, climate_ok):
    from site_dossier.charts.climograph import draw_climograph

    out = tmp_path / "clim.png"
    path, alt = draw_climograph(climate_ok.data, out)
    assert path.exists() and path.stat().st_size > 0
    assert "millimeters" in alt or "mm" in alt


def test_wind_rose_writes_png(tmp_path, wind_ok):
    from site_dossier.charts.wind_rose import draw_wind_rose

    out = tmp_path / "wind.png"
    path, alt = draw_wind_rose(wind_ok.data, out)
    assert path.exists() and path.stat().st_size > 0
    assert "W" in alt  # prevailing direction


def test_sun_path_writes_png(tmp_path, nyc_site, sun_ok):
    from site_dossier.charts.sun_path import draw_sun_path

    out = tmp_path / "sun.png"
    path, alt = draw_sun_path(sun_ok.data, nyc_site, out)
    assert path.exists() and path.stat().st_size > 0
    assert "summer solstice" in alt
