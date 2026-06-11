# 06 — Cutting Stock + Nesting Optimization

**Claim:** Given a real cut list from a parametric model, you can minimize material
waste against *actual* commercial stock — 1D linear timber (95.3% utilization,
**4.67% waste**) and 2D plywood sheets (**72.08% utilization**) — the unglamorous
optimization that decides whether a design is buildable affordably.

## Run

```bash
/home/user/Design-Studio-Tools/experiments/.venv/bin/python \
  /home/user/Design-Studio-Tools/experiments/06_cutting_stock/cutting_stock.py
```

Headless, CPU-only, deterministic. Deps: `ortools` (CP-SAT), `rectpack`,
`numpy`, `matplotlib` (Agg).

## What it does

- **(a) 1D cutting stock — timber framing.** A 72-piece stud/plate/header/noggin
  cut list (7 distinct lengths, with multiplicities) packed onto commercial stock
  boards (2400 / 3600 / 4800 / 5400 mm). Solved pattern-at-a-time: each board is a
  bounded-knapsack CP-SAT solve that picks the stock length + cut pattern with
  least off-cut; demand is decremented and repeated. **3 mm saw kerf** charged per
  internal cut (n pieces → n−1 kerfs).
- **(b) 2D nesting — plywood.** 46 cabinetry parts (sides, shelves, doors, etc.)
  nested onto standard 1220 × 2440 mm sheets via `rectpack` with the
  **guillotine** algorithm (`GuillotineBssfSas`, realistic for a panel saw) and
  90° rotation allowed.

## Actual output (this run)

**1D:** 72 pieces / 120.00 m required → **34 boards, 126.00 m stock used**,
kerf loss 114 mm, total waste 5,886 mm → **waste 4.67% / utilization 95.33%**.
Stock tally: 19 × 2400 mm, 14 × 5400 mm, 1 × 4800 mm.

**2D:** 46/46 parts placed onto **6 sheets** (17.861 m² stock, 12.874 m² parts) →
**utilization 72.08% / waste 27.92%**. Per-sheet: 82.3, 82.3, 82.3, 78.2, 73.3,
34.1% (the last sheet holds only the 3 leftover parts).

### Self-consistency (asserted at runtime)
- `required(120000) + kerf(114) + waste(5886) = 126000 == stock(126000)` ✓
- `placed(46) <= requested(46)` ✓
- `utilization(72.08%) <= 100%` ✓

## Files produced

- `cutting_stock.py` — the experiment.
- `nesting.png` — 2D plywood sheet layouts (one panel per sheet, labelled parts).
- `cut_pattern_1d.png` — horizontal stacked bar per timber board (red = off-cut waste).

## Honest limitations

- **2D uses guillotine cuts, not true free-form nesting.** Guillotine matches a
  panel saw but leaves more waste than a CNC router doing free/pocket cuts;
  72% utilization would improve with a MaxRects free-cut model. It also **ignores
  plywood grain direction** — rotation is allowed for packing efficiency, which a
  real veneer-faced panel may forbid. Sheet kerf (~3–4 mm per cut) is **not**
  modelled in 2D (it is in 1D).
- **1D is a greedy pattern-at-a-time heuristic**, near-optimal here but not
  globally proven optimal; each board is solved independently rather than as one
  joint column-generation LP.

## Verdict

**ALIVE.** Both solvers run end-to-end on real-shaped cut lists, produce
self-consistent numbers (the required+kerf+waste = stock identity holds exactly),
and emit inspectable layout images. The 4.67% timber waste and 72% sheet
utilization are believable, actionable buildability figures.
