# 05 — Architectural Acoustics: Rough Auralization

**Claim:** You can simulate the sound of a room before it's built — compute its
impulse response with pyroomacoustics' image-source method, measure RT60, and
auralize by convolving a dry clap with the room response. A small absorptive room
and a large hard-surfaced hall produce audibly and quantitatively different sound.

## Run

```
/home/user/Design-Studio-Tools/experiments/.venv/bin/python \
  /home/user/Design-Studio-Tools/experiments/05_acoustics/room_acoustics.py
```

## Actual output

```
[small] dims=[4.0, 3.0, 2.6] m  absorption=0.45  -> RT60 = 0.155 s
[hall ] dims=[30.0, 20.0, 12.0] m  absorption=0.04  -> RT60 = 3.477 s
wrote rir.png
wrote auralized_small.wav  dur=0.22s
wrote auralized_hall.wav  dur=3.59s
RT60 contrast: hall/small = 22.5x
```

The hall's RT60 (3.48 s) is ~22x longer than the small absorptive room (0.155 s) —
a real, large reverberation contrast (a 3.5 s RT60 is concert-hall/cathedral-like;
0.15 s is a small treated room).

## Files produced

- `room_acoustics.py` — builds two shoebox rooms, computes RIRs, measures RT60, auralizes.
- `rir.png` — the two impulse responses (note the hall's long ringing tail).
- `dry_clap.wav` — the dry source signal (decaying white-noise burst, 0.04 s).
- `auralized_small.wav` (0.22 s) — clap in the dry small room.
- `auralized_hall.wav` (3.59 s) — same clap in the reverberant hall; long audible tail.

## Honest limitation

Shoebox geometry only, with **frequency-independent** absorption (one scalar per
room, not per-band materials). Real rooms have angled/curved surfaces, frequency-
dependent absorption, scattering and diffraction that the pure image-source method
ignores — so RT60 here is a plausible first-order estimate, not a calibrated
prediction.
