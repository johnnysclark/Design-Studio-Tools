# 04 — WFC Plan Fields

**Claim:** A from-scratch Wave Function Collapse solver (numpy, ~190 lines) generates architectural plan fields where tiles are room/program types and an adjacency-compatibility matrix enforces real planning logic (circulation connects habitable rooms, wet rooms cluster, bedrooms never touch kitchen/living, courtyards never touch wet rooms).

## Run

```bash
/home/user/Design-Studio-Tools/experiments/.venv/bin/python \
  /home/user/Design-Studio-Tools/experiments/04_wfc_plan/wfc_plan.py
```

## Actual output

```
seed=   7  SOLVED  steps= 192  restarts=0  forbidden_adjacencies=0
seed=  42  SOLVED  steps= 192  restarts=0  forbidden_adjacencies=0
seed= 123  SOLVED  steps= 192  restarts=0  forbidden_adjacencies=0

wrote plan.png and plan.3dm (seed 7)

VERDICT: 3 plans, 0 forbidden adjacencies across all -> rules RESPECTED
```

Three distinct seeds (7, 42, 123) all collapse a 12x16 grid in 192 observe steps with
**zero restarts** and **zero forbidden adjacencies**. An independent full-matrix audit
(checking every orthogonal pair against `COMPAT`, not just the curated FORBIDDEN list)
also reports 0 violations on all three seeds. Artifacts written: `plan.png` (color-coded
grid + legend) and `plan.3dm` (186 extruded Brep cells, 7 colored layers, opens in Rhino;
courtyard cells left as open voids, z-height varies by room type).

## ASCII preview (seed 7)

Legend: `#`=WALL `+`=CORRIDOR `L`=LIVING `K`=KITCHEN `B`=BATH `D`=BED `O`=COURTYARD

```
#D######L###L###
#B+B##LLK#BKKBDO
L++#+#L++DD+BDD#
L+#+###LL#D++#D#
+L#L#++##OO##B##
#O####+#LLLLLK##
DD#++D+#O#+KL++L
#++#+B+#D++KLL##
#D#L+#+B++#L###+
##DO##+D#L#L+BB+
B#B#++#B+LLL+#KL
#K###D#D########
```

Spot-check it by eye: every `D` (bed) neighbours only `D`/`B`/`+`/`#`, never `K` or `L`;
every `O` (courtyard) neighbours only `L`/`D`/`O`/`#`, never `K`/`B`.

## Honest limitation

WFC enforces **local** adjacency only. It guarantees no two cells violate the
compatibility matrix, but it does **not** enforce **global topology** — there is no
check that every BED is reachable from a CORRIDOR, that rooms form contiguous regions
rather than scattered single cells, or that the plan is a connected building rather than
disjoint islands. I deliberately did **not** add a connectivity/flood-fill post-check, so
the output is a valid *adjacency field*, not yet a *circulatable floor plan*. Adding a
graph-reachability constraint (or treating multi-cell rooms as macro-tiles) would be the
next honest step toward usable plans.
