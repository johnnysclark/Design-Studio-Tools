# POSSIBILITIES.md — A possibility map for computational architectural design

> A living map of what has recently become possible for **one person + AI** in
> Rhino/Grasshopper/Python architectural design. Every thread carries an evidenced
> verdict: **ALIVE** (validated, with a working headless micro-experiment), **DEAD**
> (killed, with the reason), or **BLOCKED** (needs Rhino, the GPU, or a decision from
> you). This is the start of an ongoing exploration, not a final report.

Run environment for all experiments below: **headless, CPU-only Linux, no Rhino**.
`.3dm` written with `rhino3dm`. Reproduce any probe:

```bash
uv venv experiments/.venv --python 3.11
uv pip install --python experiments/.venv/bin/python -r experiments/requirements.txt
bash experiments/run_all.sh          # or run one folder's script
```

---

## The reframe (what the first pass changed about the framing)

The seed list sorted threads by *topic*. Two cycles in, a sharper axis appeared —
**where the aliveness lives**:

- **Kind A — validate a live library.** A maintained ecosystem already exists; the
  experiment proves it runs headless and is useful to *you*. Low effort, high-confidence
  ALIVE. (Form-finding, acoustics, cutting-stock, topology-opt.)
- **Kind B — resurrect dead or unimplemented theory.** No usable library exists — the
  idea lives only in papers or Rhino-locked plugins. The experiment is a **minimal
  self-built interpreter** (~30–250 lines) proving the idea is now one-person-feasible
  *with AI assistance*. (SMT proofs, WFC plans, shape grammars, pattern linting,
  differentiable design, isovists.)

**The key inversion:** a pre-flight library scan marked the most interesting "new
epistemology" threads — WFC, shape grammars, pattern-language critics, SMT layout —
as `MOSTLY-DEAD-CODE`. For your brief that is a **green light, not a stop sign**: "no
maintained library" means the territory is *open*, and AI assistance is exactly what
collapses a former PhD-scale build into an afternoon. **Six of the ten ALIVE threads
below are Kind B — things that did not exist as usable tools, now built and running.**

A second pattern worth naming: the cheap-CPU-headless filter *selects for ALIVE*. The
threads that come back BLOCKED are blocked on **hardware** (your GPU) or **software in
mid-refactor**, almost never on the idea being wrong. The frontier is not "is it
possible" — it's "is it packaged."

---

## Scorecard

| # | Thread | Category | Kind | Verdict | Evidence |
|---|--------|----------|------|---------|----------|
| 01 | Funicular form-finding → compression vault | Form & structure | A | **ALIVE** | one linear solve, `vault.3dm` |
| 02 | SMT layout — *proving* a brief impossible | New epistemology | B | **ALIVE** | SAT plan + proven-UNSAT core |
| 03 | Topology optimization (SIMP) | Form & structure | A | **ALIVE** | compliance 1027→213, `topology.png` |
| 04 | Wave Function Collapse plan fields | Generative w/ rigor | B | **ALIVE** | 3 plans, 0 rule violations, `plan.3dm` |
| 05 | Room acoustics + auralization | Experience & time | A | **ALIVE** | RT60 0.16s vs 3.48s, `.wav` pair |
| 06 | Cutting-stock + sheet nesting | Material logic | A | **ALIVE** | 4.7% waste / 72% sheet use |
| 07 | Isovist + visibility-integration field | Experience & time | B | **ALIVE** | isovist areas, `visibility_field.png` |
| 08 | Differentiable design (gradient-descend a roof) | New epistemology | B | **ALIVE** | loss 2716→167, clearances met, `canopy.3dm` |
| 09 | Shape-grammar interpreter | Generative w/ rigor | B | **ALIVE** | 4→51 segs, `final.svg` + `.3dm` |
| 10 | Pattern-language linter (Alexander as code) | Executable theory | B | **ALIVE** | 2 PASS / 4 FAIL critic report |
| 11 | Thrust-network **optimization** w/ stability (`compas_tno`) | Form & structure | A | **BLOCKED** | PyPI 0.3.0 missing `diagrams`/`shapes` |
| 12 | Graph→floorplan synthesis (House-GAN/diffusion) | Generative w/ rigor | — | **BLOCKED** | GPU; no PyPI package |
| 13 | Gaussian-splat site capture | Drawing & capture | — | **BLOCKED** | GPU + CUDA + phone scan |

**10 ALIVE** (target was ≥5), **3 BLOCKED**, 0 DEAD-on-idea. The BLOCKED threads are
unblockable on *your* Windows+NVIDIA box or by a git install — none are dead ends.

---

## Thread cards

### 01 · Funicular form-finding → compression vault — ALIVE (Kind A)
`experiments/01_thrust_network/` · `compas_fd` 0.5.4 (ETH/BRG)
A net pinned at four corners, loaded down, is solved in **one linear solve** (force-density
method, no iteration); flip it in z and the funicular tension net becomes a funicular
**compression** surface — the masonry-vault / RhinoVAULT logic, headless in ~30 lines.
Writes both meshes to `vault.3dm`.
*Open:* boundary-curve supports and a thrust-line stability check (→ thread 11).

### 02 · SMT layout that can *prove* a brief impossible — ALIVE (Kind B) ⭐
`experiments/02_smt_layout/` · `z3` 4.16 (Microsoft Research)
The epistemic shift: not "here is a plan" but "**does any plan exist?**" An 8×8 envelope
returns a valid, independently-overlap-checked layout (SAT). The *same brief* in a 6×6
envelope returns **UNSAT with a minimal unsat core** — `{living_in_envelope, bed_in_envelope,
no_overlap_living_bed}` — a *proof* that a 5×4 and a 4×4 room cannot coexist there. For
arguing with a program or zoning envelope, "these three requirements are mutually
contradictory" beats "I couldn't find one."
*Open:* doors-as-objects, circulation, integer→continuous, `Optimize` for best (not just feasible) layouts.

### 03 · Topology optimization (SIMP) — ALIVE (Kind A)
`experiments/03_topology_opt/` · pure numpy/scipy, ~140 lines (88-line method)
"Grow structure from a loadcase." Specify supports + one load + a 50% volume budget; the
material distributes itself. MBB beam, 120×40: compliance **1026.8 → 213.0** (≈5× stiffer),
volume pinned at 0.500, 12.6 s, no checkerboarding. Textbook truss in `topology.png`.
*Open:* Heaviside projection to a crisp manufacturable 0/1 design; 3D; stress constraints.

### 04 · Wave Function Collapse plan fields — ALIVE (Kind B)
`experiments/04_wfc_plan/` · self-built ~210 lines, numpy
No maintained Python WFC for architecture exists, so it's built from scratch: room-type
tiles (CORRIDOR/LIVING/KITCHEN/BATH/BED/COURTYARD/WALL) with an adjacency-compatibility
matrix encoding real planning logic; observe/collapse/propagate with min-entropy + restart.
3 seeds, **0 forbidden adjacencies** (independently audited), exports `plan.png` + a 186-box
colored `plan.3dm`.
*Open (honest):* enforces *local* adjacency only — no global topology ("every bedroom
reachable from a corridor"). A flood-fill connectivity pass is the next move.

### 05 · Room acoustics + rough auralization — ALIVE (Kind A)
`experiments/05_acoustics/` · `pyroomacoustics` 0.10.1
Hear a room before it's built. Small absorptive room **RT60 = 0.155 s** vs hard hall
**RT60 = 3.477 s** (22.5× — cathedral-like) via the image-source method; convolves a dry
clap into `auralized_small.wav` / `auralized_hall.wav` that audibly differ.
*Open:* frequency-dependent absorption, real (non-shoebox) geometry, diffraction/scattering.

### 06 · Cutting-stock + sheet nesting — ALIVE (Kind A)
`experiments/06_cutting_stock/` · `ortools` CP-SAT (1D) + `rectpack` (2D)
The unglamorous economics of buildability. A 72-piece timber cut list packs onto 34 stock
boards at **4.67 % waste** (kerf-aware; the `required+kerf+waste = stock` identity is exact);
46 plywood parts nest onto 6 sheets at **72 % utilization**, drawn in `nesting.png`.
*Open:* grain direction, free-form (non-guillotine) CNC nesting, real lumber price lists.

### 07 · Isovist + visibility-integration field — ALIVE (Kind B)
`experiments/07_isovist/` · self-built ray-casting on `shapely`, ~40 lines of math
depthmapX is C++/GUI; the math is a short ray-cast. From any standpoint, what can you see?
Corridor standpoint isovist **99.1 m²** > tucked corner **63.6 m²**; a 40×30 grid sweep
produces the space-syntax signature heatmap (bright corridors, dark corners, a clean
shadow behind a free-standing obstacle) in `visibility_field.png`.
*Open:* 3D / eye-height, agent-based desire-path overlay, serial-vision sequences along a path.

### 08 · Differentiable design — gradient-descend a roof — ALIVE (Kind B) ⭐
`experiments/08_differentiable/` · `jax` 0.10 (CPU)
Write the brief as a differentiable loss; let gradients pull the geometry. A fabric canopy:
loss = membrane area (material → taut minimal surface) + penalty for missing three program
clearances (4.5/3.0/6.0 m). Adam, 600 steps: loss **2716 → 167**, all three clearances met
(4.48/2.98/5.98 m). Tents up into a Frei-Otto-like minimal surface. `canopy.3dm` (initial +
solved), `loss_curve.png`.
*Open:* swap in any differentiable objective — daylight, structural compliance, view; height
field → full mesh with overhangs; hard constraints.

### 09 · Shape-grammar interpreter — ALIVE (Kind B)
`experiments/09_shape_grammar/` · self-built ~250 lines, numpy
Foundational generative theory (Stiny & Gips) that practitioners can't easily run — existing
code is dead or Rhino-locked. A recursive Palladian-facade grammar (`tripartite-split` →
`window`/`door`) derives over 10 rule firings, **4 → 51 segments**, self-terminating, seeded.
Emits architect-usable `final.svg` + `final.3dm`.
*Open (honest):* marker-driven matching, **not** emergent-shape recognition — the genuinely
hard open problem and the reason no general standalone tool exists.

### 10 · Pattern-language linter — Alexander as a running critic — ALIVE (Kind B) ⭐
`experiments/10_pattern_linter/` · `shapely` + `networkx`, ~250 lines, offline (no LLM)
*A Pattern Language* is prose; nobody runs it as checks. Six patterns become computable
predicates over a structured building model — #159 Light on Two Sides, #105 South Facing,
#127 Intimacy Gradient (BFS graph distance from entry), #131 Flow Through Rooms (articulation
points), #109 aspect ratio, #61 m²/occupant. On a deliberately-flawed house: **2 PASS / 4
FAIL, score 33/100**, each finding naming the implicated rooms. A deterministic critic in
milliseconds.
*Open (honest):* heuristic proxies of rich prose — critiques *structure*, never the poetics;
#131 is strict on near-tree plans. Pairs naturally with an LLM critic for the experiential layer.

---

## BLOCKED threads (and exactly what unblocks them)

### 11 · Thrust-network **optimization** with stability (`compas_tno`) — BLOCKED (software)
The layer beyond form-finding: prove a masonry vault stays within its section (lower-bound
limit analysis via convex optimization). Tested honestly — **the PyPI release `compas_tno`
0.3.0 is broken against current COMPAS 2.15**: the optimization machinery imports
(`Analysis`, `Optimiser`, `problems`) but the modules you need to *build the inputs* —
`compas_tno.diagrams` (FormDiagram) and `compas_tno.shapes` (Shape) — are **absent from the
package**, so you cannot construct a problem from the published release. *Unblock:* install
from the GitHub `main`/dev branch rather than PyPI, or wait for the 2.0-compatible release.
The force-density form-finding it builds on is already ALIVE (thread 01).

### 12 · Graph→floorplan synthesis (House-GAN / diffusion) — BLOCKED (GPU)
House-GAN, House-GAN++, GSDiff (AAAI 2025) exist as **research repos, not PyPI packages**;
CPU inference is possible but slow, training is CUDA-only. *Unblock:* clone + run inference
on your **Windows+NVIDIA** box. High-value Kind-B follow-up: pair a generator with the
thread-10 linter and thread-02 SMT solver as a *verifier* — learned generation, proven/critiqued legality.

### 13 · Gaussian-splat / neural site capture — BLOCKED (GPU + decision)
`nerfstudio` / `gsplat` need CUDA 11.8+ compilation; phone → splats → Rhino context is a
GPU pipeline. *Unblock:* run on your GPU box, or use a cloud/app capture (Polycam/Luma) and
import. Needs a decision from you on capture workflow before it's worth a probe.

---

## Threads queued, not yet explored

Honest backlog — chosen *not* to spend cycles here yet, not judged dead:
- **Steadman-style exhaustive plan enumeration / morphospace** (Kind B, pure combinatorics +
  planarity — very buildable; a strong next Kind-B probe).
- **Discrete masonry stability** (`compas_assembly` / `compas_dem` — reported headless-capable;
  untested here).
- **Reciprocal frames, tensegrity, pneumatic form-finding** via custom dynamic relaxation
  (Kangaroo-without-Kangaroo, headless).
- **Stereotomy / voussoir cutting templates**, **parametric timber joinery**, **kerf-bending
  patterns** (geometry-only, cheap — Kind B material logic).
- **Weathering / inhabitation simulation** (desire paths, patina) — no library; bespoke
  agent/particle sim (Kind B; needs a rendering decision).
- **Simulation surrogates** — train a millisecond predictor from an overnight sim farm for
  live Grasshopper feedback (needs your GPU + a sim to farm).
- **LLM adversarial critic** — attacks a scheme before the jury does; complements thread 10.

---

## Reflection — what the cycles changed about the map

1. **The taxonomy flipped from topic to provenance.** The useful axis isn't
   form/generative/experience — it's **Kind A (package exists) vs Kind B (build the dead
   theory)**. Your most-wanted region is almost entirely Kind B, and that's precisely where
   AI assistance changes the economics most.
2. **"Dead academic code" is the richest seam, not a warning.** WFC, shape grammars, pattern
   linting, isovists, SMT layout — all flagged dead/unavailable by a library scan — were the
   most rewarding builds. The pre-flight scan's verdicts were *anti-correlated* with where the
   live opportunities were.
3. **A new epistemology earned its keep: proof, not search** (thread 02). "No layout exists,
   here is the contradiction" is a genuinely different design statement, and z3 makes it a
   30-line call. This is the single most underexploited idea in the map.
4. **The cheap-test filter is biased toward ALIVE.** Everything that could be tested headless
   on CPU came back alive; the only BLOCKs are hardware (GPU) or packaging (mid-refactor). So
   "what's possible" is now mostly a *packaging and integration* question, not a feasibility one.
5. **The compositions are more interesting than the parts.** Several threads want to be wired
   together (see below) — the map's live edges are between nodes, not just the nodes.

---

## The threads I find most alive — and why

1. **SMT spatial proofs (02).** The biggest epistemic novelty for the least code. A solver
   that proves a brief impossible — and *says which requirements collide* — is something an
   architect cannot currently do and would change how briefs and zoning envelopes get argued.
   It's also the natural **verifier** for any generative method. *Start here.*

2. **Differentiable design (08).** "Define a loss, gradient-descend the building" is a general
   key, not a one-off. The same 40-line loop absorbs daylight, structure, view, material — any
   objective you can write as math. It reframes parametric design from *search* to *flow*.

3. **Pattern-language linter (10).** Executable theory as a live critic, running in
   milliseconds, fully offline. It makes a *position* about architecture computable. Pair it
   with an LLM for the experiential half and you have a real design critic.

4. **Funicular form-finding (01).** The cleanest Kind-A win: a structural epistemology
   (equilibrium-first form) that used to need a plugin, now a headless one-liner feeding `.3dm`.

5. **WFC plan fields (04) + shape grammars (09)** as a pair: two complementary rigorous
   generators (constraint-propagation vs rule-rewriting) both proven buildable headless, both
   emitting Rhino geometry, both with an honest next step (connectivity; emergent shapes).

**The live edges — compositions worth a future cycle:**
`WFC/shape-grammar (generate)` → `SMT (prove legal) + pattern-linter (critique)` →
`differentiable design (refine geometry)` → `funicular/topology-opt (resolve structure)` →
`isovist/acoustics (evaluate experience)` → `cutting-stock (cost to build)`. Every arrow is
already ALIVE and headless. The unbuilt thing is the **pipeline that chains them** — a
design loop where generation, proof, gradient, and simulation are all first-class. That, more
than any single tool, is what just became possible for one person.

---

*Map status: open. 10 ALIVE, 3 BLOCKED, a queued backlog, and a clear next cycle (chain the
edges; build the Steadman enumerator; git-install `compas_tno`). Updated as the exploration
continues.*
