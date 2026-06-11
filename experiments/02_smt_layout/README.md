# 02 · SMT spatial reasoning — a layout solver that can *prove* a brief impossible

**Claim:** An SMT solver doesn't just generate a plan; it answers "does *any* plan
satisfy this brief?" — and when none does, it returns a proof (the minimal set of
contradictory requirements).

**Verdict: ALIVE** (Kind B — a new epistemology for design: proof, not search).

## Run
```bash
../.venv/bin/python layout_proof.py
```

## What actually happened
```
=== Scenario A: 8x8 envelope (feasible) ===
result: SAT
  living   at (0,4) size 5x4
  kitchen  at (5,2) size 3x3
  bath     at (5,5) size 2x2
  bed      at (0,0) size 4x4
  independent non-overlap check: PASS

=== Scenario B: 6x6 envelope, same brief (over-constrained) ===
result: UNSAT
  z3 PROVED no layout exists. Minimal conflicting requirements (unsat core):
   - living_in_envelope
   - no_overlap_living_bed
   - bed_in_envelope

=== Scenario C: contradictory adjacency (tiny envelope) ===
result: UNSAT
  Proven impossible.  Core size: 3 requirements
```
Rooms are axis-aligned rectangles; constraints encode envelope containment,
non-overlap, and required adjacencies (shared wall ≥ door width). In the 8×8 case z3
returns coordinates (independently re-checked for overlap here). Shrink the envelope to
6×6 and z3 proves **UNSAT** with a human-readable **unsat core**: a 5×4 living room and
a 4×4 bedroom genuinely cannot both fit without overlapping inside 6×6 — that subset of
three requirements is the contradiction. That is the epistemic shift: *"no plan exists"*
with a certificate, versus *"I searched and didn't find one."*

## Library
`z3-solver` 4.16 (Microsoft Research), pure-Python API, headless.

## Honest limitation
Axis-aligned rectangles on an integer grid; adjacency is wall-sharing only (no doors as
objects, no circulation). Scales to dozens of rooms comfortably; hundreds need an
optimisation formulation (z3 `Optimize`, or CP-SAT) rather than pure feasibility.
