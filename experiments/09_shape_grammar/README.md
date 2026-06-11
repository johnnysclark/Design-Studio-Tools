# 09 — Shape Grammar Interpreter (Kind B: a working tool)

**Claim:** A genuine 2D shape-grammar interpreter — LHS→RHS rules applied under
transformation, with a seeded derivation engine — is one-person-feasible in
~180 lines of pure Python, and it produces recognizable architectural pattern,
not noise.

## Run

```bash
/home/user/Design-Studio-Tools/experiments/.venv/bin/python \
  /home/user/Design-Studio-Tools/experiments/09_shape_grammar/shape_grammar.py
```

## What it is

A **shape grammar** (Stiny & Gips, 1971) is a set of rules `LHS -> RHS` over
labeled shapes. A derivation repeatedly finds a sub-shape matching a rule's LHS
(under a transformation) and replaces it with the RHS. This is foundational
generative-design theory that practitioners cannot easily run — existing code is
either dead academic prototypes or locked inside the Rhino SortalGI plugin.

This interpreter implements:

- **Shape** = a collection of labeled 2D line segments + labeled *markers*
  (each marker carries a local frame: position, uniform scale, rotation).
- **Rule** = an LHS marker label and an RHS authored in that marker's local
  frame; it fires under the transformation (translate + uniform scale +
  rotate) carried by the matched marker.
- **Derivation engine** = applies rules for K steps, choosing among applicable
  rules with a seeded RNG (`np.random.default_rng`) for reproducibility, and a
  scale-aware control policy (subdivide large bays, resolve small bays to
  windows/doors).

## The grammar (recursive Palladian-style facade)

Initial shape: a building outline (ground, two corners, roofline) with one open
`bay` marker filling the facade.

- **tripartite-split** : `bay` → a framed bay (ground / 2 piers / cornice) +
  three smaller child `bay` markers side by side. (Recursive — the engine of growth.)
- **window** : `bay` → a punched opening with sill, two jambs, lintel, and a
  central mullion. (Terminal.)
- **door** : `bay` → an arched doorway reaching the ground. (Terminal.)

Control: while a bay is large it tends to split; once small it resolves to a
window or door. Derivation halts when no open `bay` markers remain.

## Actual output

```
Initial shape complexity: (4, 1)
Grammar rules: ['tripartite-split', 'window', 'door']
--------------------------------------------------------
step 1: fired 'tripartite-split'  ->  segments=8, open markers=3
step 2: fired 'window'  ->  segments=13, open markers=2
step 3: fired 'tripartite-split'  ->  segments=17, open markers=4
step 4: fired 'tripartite-split'  ->  segments=21, open markers=6
step 5: fired 'window'  ->  segments=26, open markers=5
step 6: fired 'door'  ->  segments=31, open markers=4
step 7: fired 'window'  ->  segments=36, open markers=3
step 8: fired 'door'  ->  segments=41, open markers=2
step 9: fired 'door'  ->  segments=46, open markers=1
step 10: fired 'window'  ->  segments=51, open markers=0
step 11: no applicable rule, derivation halts
--------------------------------------------------------
Final complexity (segments, open markers): (51, 0)
```

The shape grows monotonically (4 → 51 segments over 10 rule firings) and
terminates cleanly when every open bay is resolved.

## Outputs

- `derivation.png` — a row of subplots showing the design growing step by step
  (red dots = open markers still awaiting a rule).
- `final.svg` — the final facade as clean vector linework (architects want vectors).
- `final.3dm` — the same linework as Rhino line curves (via `rhino3dm`).

## Honest limitation

This is **marker-driven** matching, not full sub-shape detection. Each rule keys
on a labeled marker carrying a frame; the interpreter does *not* search the raw
segment set for arbitrary sub-shapes under arbitrary transformations, and it
does **not** do emergent-shape recognition — noticing new, unlabeled shapes that
appear implicitly when segments overlap (e.g. a square emerging from two
overlapping L-shapes). Emergent-shape recognition is *the* hard open problem in
shape grammars and is what makes general subshape matching expensive. The
marker-driven subclass is a legitimate, tractable, and widely-used simplification
(it is essentially how parametric/labeled shape grammars are run in practice),
but it is a simplification.

## Verdict: ALIVE

A usable, reproducible, headless shape-grammar interpreter is genuinely
one-person-feasible today. Evidence: ~180 lines, no exotic dependencies
(numpy + matplotlib + rhino3dm), seeded reproducibility, monotone derivation
(4→51 segments), and vector + Rhino output an architect can open. The catch is
scope: "alive" means the *labeled/marker-driven* subclass. Full emergent-shape
shape grammars remain a research problem, not a weekend build.
