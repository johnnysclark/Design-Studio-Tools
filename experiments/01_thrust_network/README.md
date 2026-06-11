# 01 · Thrust network / funicular form-finding → compression vault

**Claim:** Equilibrium form-finding of a compression vault is now a ~30-line headless
Python call — no Rhino, no plugin — via the force-density method.

**Verdict: ALIVE** (Kind A — validate a live library).

## Run
```bash
../.venv/bin/python funicular.py    # from this folder
```

## What actually happened
```
Solved 121 vertices, 220 edges in one linear solve.
Funicular sag (lowest point z): -34.252 m
Inverted compression vault rise (highest point z): 34.252 m
Wrote vault.3dm
```
A square net pinned at its four corners, loaded downward, is solved in **one linear
solve** (no iteration) by `compas_fd.solvers.fd_numpy`. Flipping the result in z turns
the funicular tension net into a funicular **compression** surface — the structural
logic behind masonry vaults and RhinoVAULT. `vault.3dm` contains both meshes
(`funicular_hanging_net`, `compression_vault`) and opens in Rhino.

## Library
`compas` 2.15.1 + `compas_fd` 0.5.4 (BlockResearchGroup / ETH Zürich), pure
Python + numpy. Actively maintained.

## Honest limitation
Uniform force density `Q=1` gives a deep sag (tune `Q` to set vault depth). This is
unconstrained force-density: supports are corner points, not a boundary curve, and
there's no thrust-line/stability check against a masonry section yet — that's what
`compas_tno` (thrust network optimisation) adds, the natural next probe.
