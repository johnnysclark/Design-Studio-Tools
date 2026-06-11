# 17 — The closed loop: generate → prove → revise → re-prove

**Claim:** the headline composition the whole map kept pointing at. A learned model
**proposes**, a formal method **disposes**, and then — the new part — the model **repairs
its own proposal using the proof as feedback**. Threads 15 (Fable generates → z3 proves) and
02 (z3 proofs) built the halves; this closes the loop with a revision step in the middle.

```
Fable 5 writes a program  →  z3 proves it IMPOSSIBLE (+ localizes the conflict)
        →  proof fed back to Fable 5  →  Fable revises  →  z3 proves it FEASIBLE
```

## Run

```bash
python closed_loop.py        # z3 runs offline; both programs are captured Fable 5 output
```

Writes `solved_plan.png` (the revised, proven-feasible layout). No key needed — the two Fable
programs are embedded verbatim; only the z3 proofs run here, on CPU.

## What actually happened (live run)

```
1. Fable's ORIGINAL program, 8x6 m  ->  z3: UNSAT
   (ablation: dropping adjacencies makes it SAT, so the adjacency graph is the bind)

2. Proof fed back to Fable 5. Its repair:
   "The bind was a short stub hall trying to touch three rooms at once. I stretched it into a
    full-depth (1.5m x 6m) central spine -- a straight, level, walker-width corridor every
    room opens onto, so no hall adjacency was dropped (kitchenette gained one). Bedroom
    reproportioned to 3.0x3.5 (same area, still fits bed plus turning space); sitting keeps its
    east+south corner for morning reading light."

3. Fable's REVISED program, 8x6 m   ->  z3: SAT
     bedroom       (5.0,0.0)  3.0x3.5 m      hall          (3.5,0.0)  1.5x6.0 m
     bathroom      (5.0,3.5)  2.5x2.5 m      sitting_area  (0.0,0.0)  3.5x3.0 m
     kitchenette   (1.0,3.0)  2.5x3.0 m
     independent non-overlap check: PASS

Loop result: proven IMPOSSIBLE -> model repair from the proof -> proven FEASIBLE.  (UNSAT -> SAT)
```

## Why this is the headline

The repair is **real design reasoning driven by the proof**, not trial and error. z3 didn't
just say "no" — its ablation said *the adjacency graph is the binding constraint*. Fable read
that, correctly diagnosed the mechanism ("a short stub hall trying to touch three rooms at
once"), and chose the architect's move: turn the stub into a **full-depth circulation spine**
every room opens onto. It even *strengthened* accessibility (added the hall–kitchenette
adjacency) rather than satisfying the solver by amputating a connection. z3 then certified the
result. Neither half could do this alone: the solver can prove but not design; the model can
design but, as thread 15 showed, ships latent contradictions. Chained, the model proposes and
the proof keeps it honest — and the proof's *explanation* is what makes the repair targeted.

## Honest limitations

- **Same rigid model as thread 15** (fixed-rectangle rooms, edge-touch windows, shared-wall
  adjacency). So "feasible" means "packs as fixed rectangles," a conservative proxy; the value
  is the *loop mechanic*, not millimetre-accurate plans.
- **One revision was enough here** — a harder brief might need several rounds (or prove
  genuinely impossible, which is itself a useful verdict: "no program meeting all these
  requirements fits this footprint"). The loop generalizes to N rounds.
- The revision step ran through the agent harness (which can reach Fable); a fully automated
  version calls `claude-fable-5` via the SDK with the unsat core in the prompt — blocked in
  this container only by the missing key (see thread 15).

## Verdict

**ALIVE.** The full generate → prove → revise → re-prove loop ran end to end and turned a
*proven-impossible* brief into a *proven-feasible* plan, with the model's repair guided by the
solver's own explanation. This is the single clearest answer to "what just became possible for
one person": a design dialogue where intuition and proof correct each other in seconds.
