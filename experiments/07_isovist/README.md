# 07 — Isovist / Visibility Analysis

**Claim:** A floor plan can be quantified by *what it lets you see*. Casting rays
from a standpoint and clipping them on walls yields an isovist (the visible
polygon); sweeping that across a grid produces a visibility-integration field
that predicts where a space feels open and where people tend to gather — the
core space-syntax move that the C++/GUI tool *depthmapX* wraps, here ~40 lines
of shapely ray-casting.

## Run

```
/home/user/Design-Studio-Tools/experiments/.venv/bin/python \
  /home/user/Design-Studio-Tools/experiments/07_isovist/isovist.py
```

Runs headless (CPU-only) in ~20 s.

## Actual output

```
================================================================
ISOVIST / VISIBILITY ANALYSIS
plan: 20x12 m, walkable area = 227.4 m^2
================================================================
corridor (open)                  pt=(10.0, 6.0)  area=  99.06 m^2  perimeter=  68.79 m
left-room corner                 pt=( 1.0, 1.0)  area=  63.64 m^2  perimeter=  51.72 m
right-room behind obstacle       pt=(17.2, 9.0)  area=  74.67 m^2  perimeter=  58.07 m
----------------------------------------------------------------
SANITY: corridor area (99.1) > corner area (63.6)? YES
visibility field 40x30 computed in 19.0s  (min=28.8, max=143.4 m^2)
```

The open corridor standpoint sees **99.1 m²** — more than the tucked left-room
corner (**63.6 m²**) and the right room shadowed by the free-standing obstacle
(**74.7 m²**). The model behaves the way visibility should.

## Files produced

- `isovist.py` — plan definition + `isovist()` (ray-cast visible polygon, area,
  perimeter) + `visibility_field()` (grid sweep -> integration field).
- `isovist_single.png` — the plan with the corridor isovist shaded; visible
  region fans through the spine doorway into the left rooms and the right
  partition's top doorway, with clean wall shadows.
- `visibility_field.png` — heatmap over a 40×30 grid: bright hotspots at the
  doorway/corridor junctions (where sightlines from multiple rooms converge),
  a dark shadow behind the free-standing obstacle, dark enclosed corners.

## Honest limitation

This is **2D plan geometry only** — no eye height, no 3D, no transparent or
partial-height elements; every wall is an opaque floor-to-ceiling blocker. Ray
density is uniform (540 rays for single isovists, 180 for the field), so very
thin sightlines through narrow gaps can be under- or over-counted, and the
field is a coarse grid sample rather than a continuous surface.
