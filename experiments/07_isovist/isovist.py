"""Isovist / visibility analysis for an architectural floor plan.

We quantify how a plan is *experienced*: from any standpoint, what can you see?
- isovist(): cast N rays from a point, clip on walls -> visible polygon, area, perimeter.
- visibility_field(): sample a grid of standpoints, compute isovist area at each
  -> a space-syntax-style integration field predicting where space feels open.

Pure Python + shapely ray-casting (~the math depthmapX wraps in a C++/GUI tool).
"""
import os
import time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point, LineString, MultiPolygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Floor plan: an outer boundary with interior walls forming two rooms
# joined by a corridor, plus a free-standing obstacle. Coordinates in metres.
# ---------------------------------------------------------------------------
OUTER = Polygon([(0, 0), (20, 0), (20, 12), (0, 12)])

# Interior walls modelled as thin rectangles (obstacles that block sight).
WALLS = [
    # Vertical spine wall splitting left rooms from corridor, with a doorway gap
    Polygon([(7.0, 0.0), (7.4, 0.0), (7.4, 5.0), (7.0, 5.0)]),     # lower segment
    Polygon([(7.0, 7.0), (7.4, 7.0), (7.4, 12.0), (7.0, 12.0)]),   # upper segment (gap 5-7 = doorway)
    # Wall splitting the left side into two stacked rooms, doorway near spine
    Polygon([(0.0, 5.8), (5.0, 5.8), (5.0, 6.2), (0.0, 6.2)]),
    # Right-hand room partition off the corridor, doorway at top
    Polygon([(13.0, 0.0), (13.4, 0.0), (13.4, 9.0), (13.0, 9.0)]),
    # Free-standing obstacle (column / furniture cluster) in the big right room
    Polygon([(16.5, 4.5), (18.0, 4.5), (18.0, 6.5), (16.5, 6.5)]),
]

# The corridor is the vertical band x in [7.4,13.0] connecting the rooms.
OBSTACLES = unary_union(WALLS)
WALKABLE = OUTER.difference(OBSTACLES)

# Named standpoints to compare.
STANDPOINTS = {
    "corridor (open)": (10.0, 6.0),    # in the connecting corridor, sees far
    "left-room corner": (1.0, 1.0),    # tucked in a corner of the lower-left room
    "right-room behind obstacle": (17.2, 9.0),  # large room but obstacle nearby
}


def isovist(px, py, n_rays=540, max_r=60.0):
    """Visible polygon from (px,py): cast n_rays, clip each on the obstacle set."""
    origin = Point(px, py)
    blockers = OBSTACLES.boundary.union(OUTER.boundary)
    pts = []
    for theta in np.linspace(0, 2 * np.pi, n_rays, endpoint=False):
        end = (px + max_r * np.cos(theta), py + max_r * np.sin(theta))
        ray = LineString([(px, py), end])
        hit = ray.intersection(blockers)
        if hit.is_empty:
            pts.append(end)
            continue
        # nearest intersection along the ray
        coords = []
        if hit.geom_type == "Point":
            coords = [(hit.x, hit.y)]
        elif hit.geom_type == "MultiPoint":
            coords = [(g.x, g.y) for g in hit.geoms]
        else:  # lines (ray grazing a wall) -> take all endpoints
            coords = list(getattr(hit, "coords", []))
            for g in getattr(hit, "geoms", []):
                coords.extend(list(getattr(g, "coords", [])))
        if not coords:
            pts.append(end)
            continue
        nearest = min(coords, key=lambda c: (c[0] - px) ** 2 + (c[1] - py) ** 2)
        pts.append(nearest)
    poly = Polygon(pts)
    if not poly.is_valid:
        poly = poly.buffer(0)
    # keep only the part actually inside the walkable envelope
    poly = poly.intersection(OUTER).difference(OBSTACLES)
    if isinstance(poly, MultiPolygon):
        poly = max(poly.geoms, key=lambda g: g.area)
    return poly


def visibility_field(nx=40, ny=30, n_rays=180):
    """Isovist area at each walkable grid standpoint -> integration field."""
    xs = np.linspace(0.3, 19.7, nx)
    ys = np.linspace(0.3, 11.7, ny)
    field = np.full((ny, nx), np.nan)
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            if not WALKABLE.contains(Point(x, y)):
                continue
            field[j, i] = isovist(x, y, n_rays=n_rays).area
    return xs, ys, field


def _draw_plan(ax):
    ax.set_aspect("equal")
    ax.set_xlim(-0.5, 20.5)
    ax.set_ylim(-0.5, 12.5)
    ax.plot(*OUTER.exterior.xy, color="black", lw=1.5)
    for w in WALLS:
        ax.fill(*w.exterior.xy, color="0.25")


def main():
    print("=" * 64)
    print("ISOVIST / VISIBILITY ANALYSIS")
    print(f"plan: 20x12 m, walkable area = {WALKABLE.area:.1f} m^2")
    print("=" * 64)

    results = {}
    for name, (x, y) in STANDPOINTS.items():
        iso = isovist(x, y, n_rays=540)
        results[name] = iso
        print(f"{name:<32s} pt=({x:4.1f},{y:4.1f})  "
              f"area={iso.area:7.2f} m^2  perimeter={iso.length:7.2f} m")

    open_a = results["corridor (open)"].area
    enc_a = results["left-room corner"].area
    print("-" * 64)
    print(f"SANITY: corridor area ({open_a:.1f}) > corner area ({enc_a:.1f})? "
          f"{'YES' if open_a > enc_a else 'NO'}")

    # --- PNG 1: single isovist over the plan ---
    fig, ax = plt.subplots(figsize=(8, 5))
    _draw_plan(ax)
    name = "corridor (open)"
    iso = results[name]
    x, y = STANDPOINTS[name]
    ax.fill(*iso.exterior.xy, color="gold", alpha=0.55, label="isovist")
    ax.plot(x, y, "ro", ms=7)
    ax.set_title(f"Isovist from {name}  (area={iso.area:.1f} m^2)")
    ax.legend(loc="upper right")
    p1 = os.path.join(HERE, "isovist_single.png")
    fig.tight_layout(); fig.savefig(p1, dpi=120); plt.close(fig)
    print(f"wrote {p1}")

    # --- PNG 2: visibility field heatmap ---
    t0 = time.time()
    xs, ys, field = visibility_field(nx=40, ny=30, n_rays=180)
    print(f"visibility field 40x30 computed in {time.time()-t0:.1f}s  "
          f"(min={np.nanmin(field):.1f}, max={np.nanmax(field):.1f} m^2)")
    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.pcolormesh(xs, ys, field, cmap="inferno", shading="auto")
    _draw_plan(ax)
    for name, (x, y) in STANDPOINTS.items():
        ax.plot(x, y, "co", ms=6, mec="black")
    fig.colorbar(im, ax=ax, label="isovist area (m^2) — visibility integration")
    ax.set_title("Visibility field: bright = sees more (corridors), dark = enclosed")
    p2 = os.path.join(HERE, "visibility_field.png")
    fig.tight_layout(); fig.savefig(p2, dpi=120); plt.close(fig)
    print(f"wrote {p2}")


if __name__ == "__main__":
    main()
