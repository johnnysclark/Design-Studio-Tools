# 10 — Pattern Linter

**Claim:** Christopher Alexander's *A Pattern Language* can be run as a live linting
system — several patterns encoded as computable predicates over a structured building
model, emitting violations like `eslint` does for code: a deterministic, offline
architectural critic.

## Run

```bash
/home/user/Design-Studio-Tools/experiments/.venv/bin/python \
  /home/user/Design-Studio-Tools/experiments/10_pattern_linter/pattern_linter.py
```

Writes `report.txt` (full lint report) and `plan.png` (color-coded plan, red = violated
room, blue square = window). No network, no LLM — pure rule engine (shapely + networkx).

## Actual lint report

```
========================================================================
PATTERN LINTER  --  A Pattern Language as a running architectural critic
========================================================================
Model: 9 rooms, entry = 'Entry', 8 connections

[FAIL] #159 Light on Two Sides of Every Room
        Habitable rooms lit from <2 sides (gloomy): ['Study', 'MasterBed']

[PASS] #105 South Facing Outdoors (daylight)
        Main living spaces face south for daylight.

[FAIL] #127 Intimacy Gradient
        Private rooms adjacent to entry (no intimacy gradient): ['MasterBed']

[FAIL] #131 The Flow Through Rooms
        Habitable rooms act as sole corridor to others (no flow): ['Kitchen', 'Living', 'Study']

[FAIL] #109 Long Thin House (aspect sanity)
        Rooms with extreme aspect ratio (>3:1), hard to inhabit: ['Gallery']

[PASS] #61 Humane Room Size vs Occupancy
        All rooms give each occupant humane floor area.

------------------------------------------------------------------------
SUMMARY: 2 PASS / 0 WARN / 4 FAIL   ->   compliance score 33/100
------------------------------------------------------------------------
```

## Patterns encoded (computable definitions)

| Pattern | Computable predicate |
|---|---|
| **#159 Light on Two Sides** | Every *habitable* room must have windows on ≥2 distinct orientations (N/E/S/W). |
| **#105 South Facing Outdoors** | Every main living space (habitable, area ≥12 m², occupancy ≥3) must have a `S` window. |
| **#127 Intimacy Gradient** | Private rooms (bedrooms/study) must be graph-distance ≥2 from the entry node in the adjacency graph. |
| **#131 The Flow Through Rooms** | No *habitable* room may be an articulation point of the adjacency graph (i.e. the sole passage to another room). |
| **#109 Long Thin House (aspect)** | No habitable room may have a bounding-box aspect ratio > 3:1. |
| **#61 Humane Room Size** | Floor area per design occupant must be ≥ 2.5 m²/person. |

The example house is **deliberately broken** so findings are real: `Study` and `MasterBed`
each have only one window (#159); `MasterBed` opens straight off the `Entry` (#127);
`Bedroom2` is reachable *only* through `Study` (#131); `Gallery` is 5 m × 1 m → 5:1
aspect (#109). Compliant aspects pass: living spaces face south (#105) and no room is
overcrowded (#61). Mixed PASS/FAIL, score 33/100.

## Honest limitation

These predicates are **heuristic proxies of rich prose, not the patterns themselves.**
Alexander's #159 is about the *quality of light and the absence of glare* across a day;
here it collapses to "≥2 window orientations." The geometric model is axis-aligned bounding
boxes with hand-authored adjacency edges and window lists — it does not derive daylight,
sightlines, or doors from real geometry. And the linter critiques *structure* (graph
topology, counts, ratios), never *poetics* — it cannot tell whether a room "feels alive."
Also note #131 honestly over-reports: in a near-tree plan many rooms are technically
articulation points, so the rule flags real forced-thoroughfares but is strict about it.

## Verdict

**ALIVE.** "Executable pattern language as a running critic" is genuinely feasible for the
structural/topological subset of patterns. The graph- and geometry-based patterns (#127,
#131, #109, #61) compute crisply and the daylight ones (#159, #105) work as proxies. The
linter produces a mixed, defensible report on a real model in milliseconds, offline and
deterministic. The frontier it does *not* cross is the experiential core of the patterns —
that part stays prose.
