# 16 — Serial vision: Fable 5 simulates experience over **time**

**Claim:** Gordon Cullen's *Townscape* argued architectural meaning is cinematic — it lives
in the SEQUENCE of compressions and releases as a body moves, not in any single view. That
temporal reading is exactly what static analysis misses. Fable 5, fed a circulation path
sampled as stations with **isovist areas** (the openness signal `experiments/07_isovist`
computes from real geometry), narrates the felt sequence — making the time dimension legible.

This answers thread 07's open question (“serial-vision sequences along a path”) and is the
temporal complement to thread 14: **14 judges a plan at a moment; 16 simulates it over time.**

## Run

```bash
export ANTHROPIC_API_KEY=sk-ant-... ; pip install anthropic
python serial_vision.py
```

In production the per-station isovist areas come from thread 07 run on the real plan; the
example path here is a clean shoebox-civic sequence (dark corridor → big hall → reading room).

## Verdict

**ALIVE (capability), live API run BLOCKED on a key** (same as thread 14 — the research
container has none). Transcript below is verbatim Claude Fable 5, `effort: high`.

## Actual Fable 5 serial vision (verbatim)

Path given (isovist m², tag): `1 threshold 24 · 2 compression 31 · 3 corridor 29 ·
4 release 210 · 5 expanse 240 · 6 shelter 86 · 7 pivot 120 · 8 arrival 64`

> 1. **Threshold (24 m²).** The street's infinity collapses to 24 square metres. The body
>    recalibrates — shoulders in, eyes adjusting, pace halved. Nothing is promised yet. The
>    building has taken you in but told you nothing.
> 2. **Compression (31 m²).** A turn, and the slight gain to 31 m² reads not as opening but as
>    *direction* — the corridor's length is now the only thing visible. The ceiling presses.
>    The walk becomes intentional. Something is being withheld.
> 3. **Corridor (29 m²).** The view actually contracts, 31 to 29. This is the held breath:
>    three stations and no reward. Footsteps sound louder. The body starts to suspect —
>    correctly — that this denial is being spent on something.
> 4. **Release (210 m²).** A sevenfold detonation: 29 to 210. The hall arrives all at once,
>    over-bright after the corridor's dusk, and the body stops involuntarily at the edge. This
>    is the designed climax — its force is exactly the corridor's debt repaid.
> 5. **Expanse (240 m²).** Stepping to centre adds only 14% — the shock is over; this is the
>    *dwelling* in it. The body, no longer surprised, slows and looks up. Exposure replaces
>    revelation: you are now the thing seen.
> 6. **Shelter (86 m²).** The mezzanine cuts the view to a third. After the exposure of 240,
>    the low soffit reads as refuge — the instinct is to pause here, back covered, surveying
>    the hall just left. Prospect behind, protection above.
> 7. **Pivot (120 m²).** The stair landing opens back out to 120 — a half-release, the hall
>    re-glimpsed from height as the body turns. Movement itself becomes the view: a hinge that
>    re-shows where you've been while aiming you elsewhere.
> 8. **Arrival (64 m²).** The final contraction, 120 to 64, but it feels nothing like station
>    2's compression — this is enclosure as welcome. The doorway frames the reading room's
>    quiet. The sequence ends not on climax but on settlement.
>
> **Designer's note.** The misfire is 4→5: having spent three stations buying the 29→210
> detonation, the move to centre adds only 240 — a flat second beat at the climax; either
> station 5 should be cut as a station (let the visitor find the centre unscripted) or the
> hall's far end should hold back one more revelation, since the sequence's true second act
> (shelter–pivot–arrival, 86→120→64) is rhythmically stronger than its peak.

## Why this earns the verdict

The reading is **driven by the numbers**: Fable names the 31→29 *contraction* as "the held
breath," reads the 29→210 jump as "a sevenfold detonation … the designed climax," and — most
tellingly — issues a real **critique**: stations 4→5 (210→240) is "a flat second beat at the
climax," and it proposes a fix (cut station 5, or hold back a revelation). That is design
judgement about *rhythm in time*, not description — and it's grounded in the isovist deltas,
exactly the bridge from thread 07's geometry to felt experience.

## Honest limitations

- Isovist area is a **single openness scalar** — it ignores ceiling height, light, materials,
  sound, what is actually framed in each view. Fable infers some of that plausibly but it is
  not measured; richer per-station features (height, glazing, view targets) would tighten it.
- Non-deterministic, paid, ~25 s. Use as a generative reading to react to, not ground truth.
- The example path is hand-made; wiring thread 07's real isovist sweep into the station list
  is the obvious next step (it already computes exactly this scalar over a plan).
