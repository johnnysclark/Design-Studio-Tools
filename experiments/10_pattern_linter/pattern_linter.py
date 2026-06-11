#!/usr/bin/env python3
"""Pattern Linter -- Christopher Alexander's A Pattern Language as a live rule engine.

Encodes several patterns as computable predicates over a structured building model
and "lints" a design, emitting violations like a code linter. Deterministic, offline.
"""
import os
from dataclasses import dataclass, field
from shapely.geometry import box, Polygon
import networkx as nx

# --------------------------------------------------------------------------- #
# Structured building model
# --------------------------------------------------------------------------- #
@dataclass
class Room:
    name: str
    bbox: tuple            # (minx, miny, maxx, maxy) in metres
    windows: list = field(default_factory=list)   # orientations on exterior walls: N/E/S/W
    function: str = "habitable"  # habitable | circulation | service | entry | outdoor
    occupancy: int = 1           # design occupancy (people)

    @property
    def poly(self) -> Polygon:
        return box(*self.bbox)

    @property
    def area(self) -> float:
        return self.poly.area

    @property
    def dims(self):
        minx, miny, maxx, maxy = self.bbox
        return (maxx - minx, maxy - miny)

    @property
    def aspect(self) -> float:
        w, h = self.dims
        return max(w, h) / max(min(w, h), 1e-9)

    @property
    def is_habitable(self) -> bool:
        return self.function == "habitable"


@dataclass
class Building:
    rooms: list
    entry_name: str
    adjacencies: list  # list of (roomA, roomB) sharing a usable connection/door

    def by_name(self, n):
        return next(r for r in self.rooms if r.name == n)

    def graph(self) -> nx.Graph:
        g = nx.Graph()
        for r in self.rooms:
            g.add_node(r.name, room=r)
        g.add_edges_from(self.adjacencies)
        return g


# --------------------------------------------------------------------------- #
# Example building: a small house, deliberately part-compliant, part-broken.
# Footprint roughly 12m x 9m. Some rooms touch the exterior, some do not.
# --------------------------------------------------------------------------- #
def example_building() -> Building:
    rooms = [
        Room("Entry",       (0, 0, 2, 2),     windows=["S"],      function="entry"),
        # Living room: south-facing, light on two sides -> should PASS most things
        Room("Living",      (2, 0, 7, 4),     windows=["S", "E"], function="habitable", occupancy=6),
        Room("Kitchen",     (7, 0, 10, 4),    windows=["S", "E"], function="habitable", occupancy=3),
        Room("Hall",        (2, 4, 7, 5.5),   windows=[],         function="circulation"),
        # Dark interior study: only ONE window -> violates #159; no south -> #105 not triggered (small)
        Room("Study",       (2, 5.5, 5, 8),   windows=["N"],      function="habitable", occupancy=1),
        # Master bedroom sits RIGHT off the entry -> violates intimacy gradient #127
        Room("MasterBed",   (0, 2, 2, 6),     windows=["W"],      function="habitable", occupancy=2),
        # Bedroom2 reachable ONLY through the Study -> #131 flow (Study is sole passage)
        Room("Bedroom2",    (5, 5.5, 9, 8),   windows=["N", "E"], function="habitable", occupancy=2),
        # Long thin gallery -> violates aspect-ratio sanity #109
        Room("Gallery",     (7, 4, 12, 5),    windows=["S", "N"], function="habitable", occupancy=2),
        Room("Garden",      (0, -4, 12, 0),   windows=[],         function="outdoor"),
    ]
    adj = [
        ("Entry", "Living"), ("Entry", "MasterBed"),
        ("Living", "Kitchen"), ("Living", "Hall"),
        ("Kitchen", "Gallery"),
        ("Hall", "Study"),
        ("Study", "Bedroom2"),          # Bedroom2 ONLY reachable through Study
        ("Living", "Garden"),
    ]
    return Building(rooms, entry_name="Entry", adjacencies=adj)


# --------------------------------------------------------------------------- #
# Pattern predicates. Each returns (status, message, implicated_rooms).
# status in {"PASS","WARN","FAIL"}.
# --------------------------------------------------------------------------- #
def p159_light_two_sides(b: Building):
    """#159 Light on Two Sides of Every Room: habitable rooms need windows on >=2 orientations."""
    bad = [r.name for r in b.rooms if r.is_habitable and len(set(r.windows)) < 2]
    if bad:
        return "FAIL", f"Habitable rooms lit from <2 sides (gloomy): {bad}", bad
    return "PASS", "All habitable rooms have light on two or more sides.", []


def p105_south_facing(b: Building):
    """#105 South Facing Outdoors / daylight: main living spaces should have a south window."""
    living = [r for r in b.rooms if r.is_habitable and r.area >= 12 and r.occupancy >= 3]
    bad = [r.name for r in living if "S" not in r.windows]
    if bad:
        return "FAIL", f"Main living spaces lack a south-facing window: {bad}", bad
    return "PASS", "Main living spaces face south for daylight.", []


def p127_intimacy_gradient(b: Building):
    """#127 Intimacy Gradient: private rooms should be DEEP in the plan (far from entry)."""
    g = b.graph()
    dist = nx.single_source_shortest_path_length(g, b.entry_name)
    private = {"MasterBed", "Bedroom2", "Study"}
    bad = [r.name for r in b.rooms
           if r.name in private and dist.get(r.name, 99) <= 1]
    if bad:
        return "FAIL", f"Private rooms adjacent to entry (no intimacy gradient): {bad}", bad
    return "PASS", "Private rooms are buffered from the entry by public space.", []


def p131_flow_through_rooms(b: Building):
    """#131 The Flow Through Rooms: no habitable room should be the SOLE passage to another."""
    g = b.graph()
    cut = set(nx.articulation_points(g))
    bad = sorted(name for name in cut if b.by_name(name).is_habitable)
    if bad:
        return "FAIL", f"Habitable rooms act as sole corridor to others (no flow): {bad}", bad
    return "PASS", "Circulation flows; no habitable room is a forced thoroughfare.", []


def p109_long_thin(b: Building):
    """#109 Long Thin House / aspect sanity: rooms should not be absurdly thin (>3:1)."""
    bad = [r.name for r in b.rooms if r.is_habitable and r.aspect > 3.0]
    if bad:
        return "FAIL", f"Rooms with extreme aspect ratio (>3:1), hard to inhabit: {bad}", bad
    return "PASS", "All habitable rooms have workable proportions.", []


def p61_room_size_occupancy(b: Building):
    """#61 Small Public Squares (proxy): humane floor area per person (>=2.5 m^2/person)."""
    PER_PERSON = 2.5
    bad = [r.name for r in b.rooms
           if r.is_habitable and r.occupancy > 0 and (r.area / r.occupancy) < PER_PERSON]
    if bad:
        return "FAIL", f"Rooms overcrowded (<2.5 m^2/person): {bad}", bad
    return "PASS", "All rooms give each occupant humane floor area.", []


PATTERNS = [
    ("#159 Light on Two Sides of Every Room", p159_light_two_sides),
    ("#105 South Facing Outdoors (daylight)", p105_south_facing),
    ("#127 Intimacy Gradient",                p127_intimacy_gradient),
    ("#131 The Flow Through Rooms",           p131_flow_through_rooms),
    ("#109 Long Thin House (aspect sanity)",  p109_long_thin),
    ("#61 Humane Room Size vs Occupancy",     p61_room_size_occupancy),
]


# --------------------------------------------------------------------------- #
# Runner
# --------------------------------------------------------------------------- #
def lint(b: Building):
    L = []
    L.append("=" * 72)
    L.append("PATTERN LINTER  --  A Pattern Language as a running architectural critic")
    L.append("=" * 72)
    L.append(f"Model: {len(b.rooms)} rooms, entry = '{b.entry_name}', "
             f"{len(b.adjacencies)} connections")
    L.append("")
    results = []
    for label, fn in PATTERNS:
        status, msg, rooms = fn(b)
        results.append((label, status, msg, rooms))
        L.append(f"[{status:<4}] {label}")
        L.append(f"        {msg}")
        L.append("")

    n_pass = sum(1 for _, s, _, _ in results if s == "PASS")
    n_fail = sum(1 for _, s, _, _ in results if s == "FAIL")
    n_warn = sum(1 for _, s, _, _ in results if s == "WARN")
    score = round(100 * n_pass / len(results))
    L.append("-" * 72)
    L.append(f"SUMMARY: {n_pass} PASS / {n_warn} WARN / {n_fail} FAIL"
             f"   ->   compliance score {score}/100")
    L.append("-" * 72)
    return "\n".join(L), results


def draw_plan(b: Building, results, path):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
    except Exception as e:
        return f"(plot skipped: {e})"

    flagged = set()
    for _, status, _, rooms in results:
        if status in ("FAIL", "WARN"):
            flagged.update(rooms)

    colors = {"habitable": "#cfe8cf", "circulation": "#e6e6e6",
              "service": "#dbe4f0", "entry": "#f5e2c0", "outdoor": "#d6efd6"}
    fig, ax = plt.subplots(figsize=(9, 7))
    for r in b.rooms:
        minx, miny, maxx, maxy = r.bbox
        fc = colors.get(r.function, "#ffffff")
        ec = "#c0392b" if r.name in flagged else "#555555"
        lw = 2.6 if r.name in flagged else 1.0
        ax.add_patch(Rectangle((minx, miny), maxx - minx, maxy - miny,
                               facecolor=fc, edgecolor=ec, linewidth=lw))
        cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
        mark = "  X" if r.name in flagged else ""
        ax.text(cx, cy, f"{r.name}{mark}\n{r.area:.0f}m2", ha="center", va="center",
                fontsize=8, color=("#c0392b" if r.name in flagged else "#222"))
        for w in r.windows:
            wx = {"N": cx, "S": cx, "E": maxx, "W": minx}[w]
            wy = {"N": maxy, "S": miny, "E": cy, "W": cy}[w]
            ax.plot([wx], [wy], marker="s", color="#2980b9", markersize=6)

    ax.set_xlim(-1, 13); ax.set_ylim(-5, 9)
    ax.set_aspect("equal")
    ax.set_title("Pattern-lint plan  (red = pattern violation, blue = window)")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return f"(plan saved -> {path})"


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    b = example_building()
    report, results = lint(b)
    print(report)
    with open(os.path.join(here, "report.txt"), "w") as f:
        f.write(report + "\n")
    note = draw_plan(b, results, os.path.join(here, "plan.png"))
    print(note)
