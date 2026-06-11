# 08 · Differentiable design — gradient-descend a roof to meet a brief

**Claim:** Write the brief as a differentiable loss and let `jax.grad` pull the geometry
into shape — no solver, no search, just gradients flowing through the design.

**Verdict: ALIVE** (Kind B — the autodiff machinery is mature; the architectural
*use* barely exists, so this is a new epistemology to bring into practice).

## Run
```bash
../.venv/bin/python diff_design.py
```

## What actually happened
A fabric canopy on a fixed 12×12 m frame. Loss = membrane area (material, → a taut
minimal surface) + a penalty for failing three program **clearances** (entry 4.5 m,
side door 3.0 m, central mast 6.0 m). Adam descends the interior height field for 600
steps:
```
step    1  loss=2716.374  area=150.925 m^2  clearance_violation=51.3075
step  150  loss= 182.709  area=164.626 m^2  clearance_violation=0.3471
step  600  loss= 166.801  area=165.899 m^2  clearance_violation=0.0014
...
All clearance heights met (independent check): True
  required 4.5 m at (3.0,3.0) -> achieved 4.48 m
  required 3.0 m at (9.0,4.0) -> achieved 2.98 m
  required 6.0 m at (6.0,9.0) -> achieved 5.98 m
```
The membrane tents up from a near-flat sheet to clear all three program volumes while
settling into the **minimal taut area** that satisfies them (a Frei-Otto-like form).
`canopy.3dm` holds `canopy_initial_flat` and `canopy_solved`; `loss_curve.png` shows
the descent.

## Library
`jax` 0.10 on CPU. The surface area is computed by differentiable triangle-area
summation, so gradients flow from "material used" + "program met" straight to the
control heights.

## Honest limitation
This is a height field on a regular grid (single-valued surfaces only — no overhangs).
Soft clearance penalty leaves a ~2 cm residual (tighten with a hard constraint or higher
penalty weight). The point is the *method*: any differentiable objective — daylight
proxy, structural compliance, view — can be dropped into the same loop.
