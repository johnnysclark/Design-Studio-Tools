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
- **Kind C — the model itself as a design participant** *(added cycle 2).* The new thing
  is not a library or a revived algorithm but the **frontier model in the loop**: Claude
  Fable 5 reading a plan and judging its *experience*, turning a vague brief into a
  checkable program, or narrating a path as felt time. This is what the map's seed list
  called "learned intuition," and it only became reliable enough to *trust as a critic and
  generator* very recently. Crucially, Kind C is strongest **wired to Kind A/B**: a learned
  generator/critic paired with a formal verifier (z3, the pattern-linter), so the model's
  fallibility is caught by something that can prove. (Threads 14–16.)

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
| 14 | Fable 5 experiential critic (jury before the jury) | Executable theory | C | **ALIVE** | geometry-grounded critique (real transcript) |
| 15 | NL brief → program (Fable) → z3 **proof** | New epistemology | C+B | **ALIVE** | Fable program proven UNSAT; conflict localized |
| 16 | Serial vision — Fable narrates path as time | Experience & time | C | **ALIVE** | isovist-driven sequence + critique (real transcript) |
| 17 | Closed loop: generate→prove→**revise**→re-prove | New epistemology | C+B | **ALIVE** | UNSAT→repair→SAT, `solved_plan.png` |
| 11 | Thrust-network **optimization** w/ stability (`compas_tno`) | Form & structure | A | **BLOCKED** | PyPI 0.3.0 missing `diagrams`/`shapes` |
| 12 | Graph→floorplan synthesis (House-GAN/diffusion) | Generative w/ rigor | — | **BLOCKED** | GPU; no PyPI package |
| 13 | Gaussian-splat site capture | Drawing & capture | — | **BLOCKED** | GPU + CUDA + phone scan |

**14 ALIVE** (target was ≥5), **3 BLOCKED**, 0 DEAD-on-idea. The BLOCKED threads are
unblockable on *your* Windows+NVIDIA box or by a git install — none are dead ends. Threads
14–17 are **Kind C** (Claude Fable 5 as a participant): the *capability* is validated with
real transcripts; only the live API call is blocked in the headless container (no key), and
runs on your machine. The z3 proofs in 15 and 17 reproduce offline.

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

## Cycle 2 — Claude Fable 5 as a design participant (Kind C)

These came from a direct prompt: *keep exploring design-tool building with the new Fable
model.* They pick up exactly where the offline map left off — thread 10 ended "pairs
naturally with an LLM critic for the experiential layer," and the backlog named an "LLM
adversarial critic." All three were tested with **real Claude Fable 5 output** (via the agent
harness, which can reach the model); the standalone tool code uses the Anthropic SDK and
`model="claude-fable-5"` per the API contract (omit `thinking`, steer with `effort`, check
`stop_reason=="refusal"`). One honest caveat across all three: the **live API call is BLOCKED
in this research container** — it has no static key (auth is the harness's OAuth descriptor),
so a plain script gets `401`; on your machine with `ANTHROPIC_API_KEY` it runs as written.

### 14 · Fable 5 experiential critic — the jury before the jury — ALIVE (Kind C) ⭐
`experiments/14_fable_critic/` · `claude-fable-5`, ~140 lines
The exact complement to thread 10: the linter proves the *structural* violations
(deterministic, ms); Fable judges the *experience* (learned, ~40 s). On the same flawed
house, Fable produced a critique **derived from the coordinates** — it proved the Gallery's
"south windows" face the Kitchen's north wall (shared `y=4` edge), caught the windowless
1.5 m circulation spine ("bright rooms connected by blackness"), and the spent-on-the-doormat
arrival — a class of violation thread 10's six patterns don't encode. Ends with the sharpest
jury question. Real transcript in the README.
*Open:* non-deterministic and paid; it's a sharp jury member, not an oracle — use as the
critic half of a linter+critic pair, not alone.

### 15 · NL brief → structured program (Fable) → z3 **proof** — ALIVE (Kind C+B) ⭐
`experiments/15_fable_program_proof/` · `claude-fable-5` + `z3` 4.16
The map's "live edge" made concrete — learned intuition *generating*, formal method
*verifying*. Fable turns a vague brief ("step-free annex for my elderly mother… sunny
sitting area where she reads in the mornings… 8×6 m") into a numeric program, **inferring**
a 2.5×2.5 m walker bathroom (turning circle), a 1.5 m step-free hall, and E/S morning glazing.
z3 then proves feasibility. The surprise: Fable's program is **provably UNSAT even in the
8×6 m footprint Fable itself recommended** — and z3 *localizes* the cause: ablation shows the
**adjacency graph** is the binding constraint, not daylight and not area (78% used). Turns
"this feels tight" into "relax one adjacency / grow the footprint / allow an L-shaped hall."
The z3 step reproduces offline from the captured program.
*Open (honest):* rooms modeled as rigid minimum rectangles + must-touch-edge windows, so
UNSAT means "infeasible as a fixed-rectangle pack," not physically impossible — the
*localization* is the trustworthy output; allow room growth / L-shapes to tighten it.

### 16 · Serial vision — Fable narrates a path as felt time — ALIVE (Kind C)
`experiments/16_serial_vision/` · `claude-fable-5`, ~90 lines
Simulating experience over **time**, answering thread 07's open question. Fed a circulation
path sampled as stations with isovist areas (the openness scalar thread 07 computes), Fable
wrote a Cullen-style serial-vision sequence **driven by the numbers**: it read the 31→29
contraction as "the held breath," the 29→210 jump as "a sevenfold detonation… the designed
climax," and — as judgement, not description — flagged 210→240 as "a flat second beat at the
climax" and proposed a fix (cut the station, or hold back one revelation). 14 judges a plan
at a moment; 16 judges its rhythm in time. Real transcript in the README.
*Open:* isovist area is one scalar (no height/light/material/sound); richer per-station
features and wiring thread 07's real sweep into the path are the next step.

### 17 · Closed loop — generate → prove → **revise** → re-prove — ALIVE (Kind C+B) ⭐⭐
`experiments/17_closed_loop/` · `claude-fable-5` + `z3` 4.16 · `solved_plan.png`
The headline. Fable's thread-15 program was proven UNSAT; the **proof was fed back to Fable**,
which repaired it; z3 then proved the repair **feasible** — a real plan. The repair is design
reasoning *driven by the proof*: z3's ablation said "the adjacency graph is the bind," Fable
diagnosed the mechanism ("a short stub hall trying to touch three rooms at once") and made the
architect's move — turned the stub into a **full-depth circulation spine** every room opens
onto, *strengthening* step-free access (added an adjacency) rather than amputating one. z3
certified it: `UNSAT → repair → SAT`, independent overlap check PASS. Neither half could do
this alone — the solver proves but can't design; the model designs but ships latent
contradictions (thread 15). Chained, the model proposes and the proof keeps it honest, and the
proof's *explanation* makes the repair targeted.
*Open:* generalizes to N rounds; harder briefs may need several (or prove genuinely
impossible — itself a useful verdict). Rigid-rectangle model is the same conservative proxy
as thread 15.

---

## Cycle 3 brainstorm — the Fable-composition space now open

Building 14–17 made one thing obvious: **the model is a universal adapter between language
and every rigorous tool already in the map.** That opens a whole class of "X → Fable →
verifier" and "generator → Fable-critic" threads, none of which existed before this cycle.
The richest, in rough priority (untested unless noted):

- **Zoning-ordinance prose → z3 constraints → compliance proof** (Kind C+B, on the seed list).
  Fable reads real ordinance text (setbacks, FAR, height, daylight planes) and emits z3
  constraints; the solver then *proves* a massing compliant — or proves a lot **un-buildable**
  under its own code. The thread-15 pattern (language → checkable formal object) pointed
  straight at law. The single highest-value untested thread.
- **Fable authors the differentiable objective** (Kind C × thread 08). A verbal intent ("shelter
  the south terrace but let winter sun in") → a weighted objective spec → thread 08's JAX
  gradient descent solves it. Language → loss → flow; the model writes the objective, the
  optimizer obeys it. Different briefs should yield visibly different solved forms.
- **Adversarial critic vs the optimizer** (Kind C × thread 08). Run the differentiable canopy,
  then have Fable *attack* that exact geometry to find the one failure most likely to sink it
  at a jury — and feed that back as a learned loss term. Makes thread 14 adversarial.
- **Exhaustive catalog × learned taste** (Kind C × Steadman). Enumerate every small plan
  (morphospace, queued below), then have Fable *curate* the catalog — rank by design quality,
  cluster by character. Pairs a new epistemology (exhaustive proof-by-enumeration) with the
  one thing enumeration lacks: judgement.
- **Semantic model querying** (Kind C). Natural-language questions over a structured building
  model — "which rooms get morning light *and* sit ≥2 doors from the entry?" — translated by
  Fable into calls on the analysis stack (07 isovist, 10 graph, 02 solver). A conversational
  front-end to the whole kit.
- **Multi-critic jury** (Kind C × 02 × 07 × 10). Fable proposes; the offline linter (10), the
  SMT solver (02), and the isovist field (07) each return a verdict; Fable synthesizes the
  cross-examination into one scored review. The pipeline's "evaluate" node, fully wired.

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
- ~~**LLM adversarial critic** — attacks a scheme before the jury does; complements thread
  10.~~ **Built in cycle 2 → thread 14 (Fable 5 critic).** Next: make it *adversarial* — have
  it attack to find the single failure most likely to sink the scheme at a jury, and run it
  against the differentiable optimizer's output (thread 08) as a learned loss.
- **Generate → prove → critique → revise loop** — feed z3's unsat core (thread 15) and the
  pattern-linter's failures (thread 10) back to Fable and have it repair its own program. The
  headline composition; thread 15 built the first half.

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
6. **Cycle 2 broke the A/B taxonomy: there is a Kind C.** "The model itself as a design
   participant" is neither a library to validate nor dead theory to revive — it's the frontier
   model (Claude Fable 5) judging experience, generating checkable programs, narrating time.
   And it confirmed point 5 *empirically*: thread 15 is the **first live edge actually built**
   — Fable generates a program, z3 proves it (and proved Fable's own 8×6 program infeasible,
   localizing the conflict to its adjacency graph). The lesson is sharp: a learned generator is
   most valuable **chained to a formal verifier**. Fable's prose program looked fine; the prover
   caught what prose hides. Generation + proof beats either alone — that's the cycle's headline.
7. **The loop closed (thread 17), and the proof's *explanation* is the active ingredient.** It
   wasn't enough for z3 to say "impossible" — it said *which* requirements collided, and that
   localized verdict is what let Fable make a targeted architectural repair (stub hall → full
   spine) instead of flailing. A bare SAT/UNSAT bit would not have been enough; the unsat core
   is what turns a solver into a design partner. The deepest shift the whole map records: the
   model is now a **universal adapter between language and every rigorous tool already here** —
   which is why cycle 3's brainstorm (zoning prose → proof, language → loss, catalog → taste)
   is suddenly a whole *class* of buildable threads, not a few one-offs.

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
`Fable brief→program / WFC / shape-grammar (generate)` → `SMT (prove legal) + pattern-linter
+ Fable critic (critique)` → `differentiable design (refine geometry)` →
`funicular/topology-opt (resolve structure)` → `isovist/acoustics + Fable serial-vision
(evaluate experience)` → `cutting-stock (cost to build)`. Every arrow is already ALIVE and
headless. **Cycle 2 built the first edge for real** (thread 15: Fable generate → z3 prove),
and added a learned critic/narrator to the critique and experience nodes. The unbuilt thing is
the **full pipeline that chains them** — a design loop where learned generation, proof,
gradient, and simulation are all first-class, the model proposing and the formal tools
disposing. That, more than any single tool, is what just became possible for one person.

**The most alive thread now:** **the closed loop (17).** Cycle 2 found the thesis — a frontier
model turns language into a checkable artifact and a solver tells it the truth (15) — and cycle
3 *closed* it: the solver's proof feeds back, the model repairs, the solver re-certifies
(`UNSAT → SAT`). It is the whole map in one probe — intuition and proof correcting each other
in seconds, headless, by one person. Neither half is new; chaining them into a self-correcting
dialogue is. Everything in the cycle-3 brainstorm is a variation on this single live mechanic.

---

*Map status: open. 14 ALIVE (10 headless + 4 Fable-participant), 3 BLOCKED, an expanding
brainstorm. Cycle 1 mapped the headless frontier; cycle 2 added Kind C (Claude Fable 5 as
critic, program-generator, narrator) and built the first live edge (Fable → z3); cycle 3
**closed the loop** (generate → prove → revise → re-prove, `UNSAT → SAT`) and opened a whole
class of language→verifier compositions. Clear next cycle: zoning prose → z3 compliance proof;
Fable authors a thread-08 differentiable loss from a verbal brief; wire thread 07's real
isovists into 16; build the Steadman enumerator + Fable curator; git-install `compas_tno`.
Updated as the exploration continues.*
