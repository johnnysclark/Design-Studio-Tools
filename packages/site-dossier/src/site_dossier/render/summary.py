"""Deterministic plain-language summary at the top of every dossier.

Generated from the underlying data — no LLM. The summary is the first thing a screen
reader encounters, so it must convey the key facts and explicitly note any sections that
are unavailable or partial.
"""

from __future__ import annotations

import calendar

from ds_common.geocode import ResolvedSite

from site_dossier.models import (
    ClimateData,
    DemographicsData,
    SunData,
    WindData,
    ZoningData,
)


def generate_summary(
    *,
    site: ResolvedSite,
    climate: ClimateData,
    wind: WindData,
    sun: SunData,
    demographics: DemographicsData,
    zoning: ZoningData,
) -> str:
    """Return a two-paragraph plain-language summary: key facts + caveats."""
    parts = [_location_sentence(site)]
    parts.append(_climate_sentence(climate))
    parts.append(_wind_sentence(wind))
    parts.append(_sun_sentence(sun))
    parts.append(_demographics_sentence(site, demographics))
    parts.append(_zoning_sentence(zoning))
    main = " ".join(p for p in parts if p)

    sections = {
        "climate": climate,
        "wind": wind,
        "sun": sun,
        "demographics": demographics,
        "zoning": zoning,
    }
    degraded = [name for name, result in sections.items() if result.status != "ok"]
    if degraded:
        caveats = (
            f" The following sections are unavailable or partial in this dossier: "
            f"{', '.join(degraded)}. See the Notes & Data Quality section for details."
        )
    else:
        caveats = " All five data sections were retrieved successfully."

    return main + caveats


def _location_sentence(site: ResolvedSite) -> str:
    elev = f", elevation {site.elevation_m:.0f} meters" if site.elevation_m else ""
    return (
        f"{site.display_name} is located at latitude {site.lat:.4f}, "
        f"longitude {site.lon:.4f}{elev}."
    )


def _climate_sentence(climate: ClimateData) -> str:
    if climate.status != "ok" or not climate.data:
        return "Climate data is unavailable."
    a = climate.data.get("annual", {}) or {}
    mean_t = a.get("mean_temp_c")
    annual_p = a.get("annual_precip_mm")
    warm = a.get("warmest_month")
    cold = a.get("coldest_month")
    if mean_t is None:
        return "Climate normals were retrieved but the annual aggregate is empty."
    warm_label = calendar.month_name[warm] if warm else "unknown"
    cold_label = calendar.month_name[cold] if cold else "unknown"
    return (
        f"The 1991-2020 climate normals show a mean annual temperature of {mean_t} "
        f"degrees Celsius and roughly {annual_p:.0f} millimeters of precipitation per year, "
        f"with the warmest month being {warm_label} and the coldest being {cold_label}."
    )


def _wind_sentence(wind: WindData) -> str:
    if wind.status != "ok" or not wind.data:
        return "Wind data is unavailable."
    d = wind.data
    return (
        f"Over the past ten years of hourly observations, prevailing winds come from "
        f"the {d['prevailing_dir_cardinal']} "
        f"({d['prevailing_dir_pct']}% of hours) at a mean speed of "
        f"{d['mean_speed_mps']} meters per second; calm conditions occur "
        f"{d['calm_pct']}% of the time."
    )


def _sun_sentence(sun: SunData) -> str:
    if sun.status != "ok" or not sun.data:
        return "Sun-path data is unavailable."
    ss = sun.data.get("sunrise_sunset", {})
    summer = ss.get("summer_solstice", {})
    winter = ss.get("winter_solstice", {})
    if not summer or summer.get("max_altitude_deg") is None:
        return "Sun-path geometry was computed but key-day altitudes are unavailable."
    return (
        f"On the summer solstice the sun reaches a maximum altitude of "
        f"{summer['max_altitude_deg']:.0f} degrees above the horizon; on the winter "
        f"solstice it tops out at {winter.get('max_altitude_deg', 0):.0f} degrees."
    )


def _demographics_sentence(site: ResolvedSite, demographics: DemographicsData) -> str:
    if demographics.status == "unavailable" or not demographics.data:
        return "Demographic data is unavailable."
    d = demographics.data
    if site.country_code == "US":
        pop = d.get("total_population")
        income = d.get("median_household_income_usd")
        home = d.get("median_home_value_usd")
        tract = d.get("tract_name") or "the surrounding census tract"
        bits = []
        if pop is not None:
            bits.append(f"a tract population near {pop:,}")
        if income is not None:
            bits.append(f"median household income around ${income:,}")
        if home is not None:
            bits.append(f"median home value around ${home:,}")
        if not bits:
            return "US Census data was returned but no population, income, or home-value figures were available."
        return f"At {tract}, demographics show " + ", ".join(bits) + "."
    # World Bank country-level
    pop = d.get("total_population")
    gdp = d.get("gdp_per_capita_usd")
    urban = d.get("urban_population_pct")
    bits = []
    if pop:
        bits.append(f"national population around {int(pop):,}")
    if gdp:
        bits.append(f"GDP per capita around ${int(gdp):,}")
    if urban:
        bits.append(f"{urban:.0f}% urban population")
    if not bits:
        return "World Bank indicators were retrieved but had no recent values."
    return f"Country-level indicators for {d.get('country', 'this country')}: " + ", ".join(bits) + "."


def _zoning_sentence(zoning: ZoningData) -> str:
    if zoning.status == "unavailable" or not zoning.data:
        return "Zoning information is unavailable from automated sources; verify with the local municipality."
    d = zoning.data
    if "zoning_code" in d and d.get("zoning_code"):
        desc = f" ({d['description']})" if d.get("description") else ""
        return f"Zoning is recorded as {d['zoning_code']}{desc}."
    if d.get("landuse"):
        return (
            f"No municipal zoning portal was available, but OpenStreetMap reports the "
            f"surrounding landuse as {d['landuse']}; this is crowd-sourced and should "
            f"be verified with the municipality."
        )
    return (
        "Zoning was not auto-discovered; the dossier includes a search query you can "
        "follow up with the local municipality."
    )
