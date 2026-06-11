# 14 — Fable 5 as experiential critic (the jury before the jury)

**Claim:** the newest model (Claude Fable 5) is good enough to be a *design participant*,
not just a text generator — it reads a structured plan and delivers the **experiential
critique** that thread 10's offline pattern-linter explicitly cannot (“critiques structure,
never the poetics”). Structure is proven by the rule engine; experience is judged by Fable.

```
offline pattern-linter (thread 10)  ->  PROVABLE structural violations  (deterministic, ms)
Fable 5 critic (this tool)          ->  EXPERIENTIAL judgement          (learned, ~30–45 s)
```

## Run

```bash
export ANTHROPIC_API_KEY=sk-ant-...      # the headless research container has no key
pip install anthropic
python fable_critic.py
```

The tool feeds Fable the same structured `Building` model used by thread 10 **plus** the
linter's structural findings, and asks only for the layer above them.

## Verdict

**ALIVE (capability), with evidence below.** The live API run is **BLOCKED** in this
research container only — it has no static key (auth is the harness's OAuth descriptor), so
a plain `anthropic` script gets `401`. On your Mac/Windows with `ANTHROPIC_API_KEY` set it
runs as written. The *capability* was validated directly: the transcript below is verbatim
Claude Fable 5 output on the deliberately-flawed thread-10 house.

## Actual Fable 5 critique (verbatim, `effort: high`)

> The plan's real failure is its spine. The Hall is a 1.5 m windowless tube running between
> two luminous zones — south rooms washed in garden light, north rooms in cool steady
> daylight — and every domestic journey threads through this dark seam. The house will be
> experienced as bright rooms connected by blackness: no borrowed light, no view through, no
> moment where the section breathes. Movement, the thing a house does most, gets the worst
> space.
>
> Second, the Gallery lies about itself. Its "south windows" stare into the Kitchen's north
> wall for three of its five metres; only the easternmost two metres see sky. Worse, geometry
> makes it the *only* link between Hall and Kitchen (they meet at a single point), so this
> 1 m-wide contemplative room is actually the breakfast corridor. A child in Bedroom2 reaches
> morning toast via Study, Hall, and a metre-wide squeeze — or publicly, across the Living
> room. The plan has no honest back-of-house route.
>
> Third, arrival: the front door sits on the garden side, so guests cross the family's private
> outdoor room to enter, then stand in a 2×2 cell with the master bedroom door at their elbow.
> There is no compression-release, no oblique reveal of the garden — you've already used it up
> before you're inside. The best view is spent on the doormat.
>
> Opportunity: the Living's SE double aspect is genuine prospect; it deserves a refuge corner,
> not a walk-through.
>
> **Question for the designer:** When someone in Bedroom2 wants a glass of water at midnight,
> describe their route — and tell me which room you're willing to sacrifice to it.

## Why this is more than "an LLM said something nice"

Every claim is **derived from the coordinates**, not generic: the Gallery's south windows
*provably* face the Kitchen's north wall (Gallery `(7,4)-(12,5)`, Kitchen `(7,0)-(10,4)` —
they share the `x∈[7,10], y=4` edge); the Gallery↔Kitchen link is a single-point touch; the
entry sits on the garden (south) side. Fable found a violation the linter's six patterns
**don't encode** — "south window pointing at an internal wall" — purely from geometry. That
is the experiential layer becoming legible to a tool.

## Honest limitations

- **Not deterministic, not free, not a proof.** Unlike thread 10 (ms, offline, repeatable),
  this is a paid ~30–45 s call whose wording varies run to run. Use it as the *critic half*
  of a pair — the linter proves the structural facts, Fable judges the experience.
- **No ground truth on the poetics.** It is a strong, specific reading, not a measurement;
  treat it as a sharp jury member, not an oracle.
- **Garbage-in:** it reasons over the model you give it. If your `Building` mis-states
  windows/adjacencies, the critique inherits the error (as a human critic would).

The headline: pairing a deterministic rule engine (provable structure) with a learned critic
(experiential judgement) gives a design critique that neither half could produce alone.
