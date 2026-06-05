from site_dossier.render.summary import generate_summary


def test_summary_includes_key_facts(
    nyc_site, climate_ok, wind_ok, sun_ok, demographics_ok, zoning_ok
):
    s = generate_summary(
        site=nyc_site,
        climate=climate_ok,
        wind=wind_ok,
        sun=sun_ok,
        demographics=demographics_ok,
        zoning=zoning_ok,
    )
    assert "350 5th Ave" in s
    assert "7.5" in s and "Celsius" in s
    assert "W" in s  # prevailing wind cardinal
    assert "72" in s or "73" in s  # summer solstice max altitude (72.5 rounded)
    assert "C5-3" in s
    assert "successfully" in s  # all sections OK


def test_summary_flags_degraded_sections(
    nyc_site, climate_unavailable, wind_ok, sun_ok, demographics_ok, zoning_degraded
):
    s = generate_summary(
        site=nyc_site,
        climate=climate_unavailable,
        wind=wind_ok,
        sun=sun_ok,
        demographics=demographics_ok,
        zoning=zoning_degraded,
    )
    assert "unavailable or partial" in s
    assert "climate" in s
    assert "zoning" in s


def test_summary_handles_all_unavailable(nyc_site):
    from site_dossier.models import (
        ClimateData,
        DemographicsData,
        SunData,
        WindData,
        ZoningData,
    )

    none = {"status": "unavailable", "source": "x", "data": None, "notes": []}
    s = generate_summary(
        site=nyc_site,
        climate=ClimateData(**none),
        wind=WindData(**none),
        sun=SunData(**none),
        demographics=DemographicsData(**none),
        zoning=ZoningData(**none),
    )
    # Should still produce something coherent that names the location and degradation.
    assert "350 5th Ave" in s
    assert "unavailable" in s
