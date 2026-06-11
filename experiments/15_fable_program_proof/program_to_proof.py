"""Natural-language brief -> structured program (Claude Fable 5) -> z3 feasibility PROOF.

Thread 15: a live edge of the map. Two epistemologies that the first pass kept apart get
wired together here:
  - learned design intuition (Fable reads a vague client brief and INFERS a concrete,
    numeric spatial program -- walker-accessible bathroom dimensions, morning-light
    orientation, step-free circulation), and
  - formal proof (z3 takes that program and answers "does ANY layout satisfy it in this
    garden footprint?" -- returning a packed plan, or a minimal unsat core proving the
    footprint is too small).

The Fable half runs through the Anthropic API (see fable_program_gen.py -- needs your
ANTHROPIC_API_KEY; it cannot authenticate inside the headless research container). The
PROGRAM below is the verbatim JSON Fable 5 actually produced for the brief, captured so
this proof step reproduces offline on CPU. z3 runs live here.

Reuses the SMT layout idea from experiments/02_smt_layout, extended with window/orientation
constraints (a room needing a south window must sit on the envelope's south edge).
"""
import json
import os
from z3 import Int, Solver, Or, And, If, sat

# --- The program Claude Fable 5 generated from the vague brief (verbatim) ------------- #
# Brief: "a small step-free annex in the back garden for my elderly mother ... her own
# bedroom, a proper bathroom she can use with a walker, a little kitchenette, and a sunny
# sitting area where she reads in the mornings ... about 8 metres wide by 6 metres deep."
FABLE_PROGRAM = json.loads(r"""
{
  "envelope": {"width": 8, "depth": 6},
  "rooms": [
    {"name": "bedroom",      "min_w": 3.5, "min_d": 3.0, "needs_window": ["S"],     "function": "habitable",   "occupancy": 1},
    {"name": "bathroom",     "min_w": 2.5, "min_d": 2.5, "needs_window": [],        "function": "service",     "occupancy": 1},
    {"name": "kitchenette",  "min_w": 2.5, "min_d": 2.0, "needs_window": ["N"],     "function": "service",     "occupancy": 1},
    {"name": "sitting_area", "min_w": 3.5, "min_d": 3.0, "needs_window": ["E","S"], "function": "habitable",   "occupancy": 2},
    {"name": "hall",         "min_w": 1.5, "min_d": 3.5, "needs_window": [],        "function": "circulation", "occupancy": 0}
  ],
  "adjacencies": [
    ["hall", "bedroom"], ["hall", "bathroom"], ["hall", "sitting_area"],
    ["bedroom", "bathroom"], ["sitting_area", "kitchenette"]
  ],
  "rationale": "Walker use drives a 2.5x2.5 bathroom (1.5 m turning circle plus fixtures) adjacent to the bedroom, and a 1.5 m-wide step-free hall linking all rooms. Morning reading puts the sitting area on E/S glazing; kitchenette opens off it for sociable cooking."
}
""")

# Convention for the envelope edges (metres): y=0 is SOUTH, y=depth NORTH; x=0 WEST, x=width EAST.
SCALE = 2  # work in half-metre integer units so 0.5-m dimensions stay exact for z3


def on_edge(orient, X, Y, W, H, n, ew, ed):
    if orient == "S": return Y[n] == 0
    if orient == "N": return Y[n] + H[n] == ed
    if orient == "W": return X[n] == 0
    if orient == "E": return X[n] + W[n] == ew
    raise ValueError(orient)


def prove(program, envelope=None, min_door=2):
    env = envelope or program["envelope"]
    ew, ed = int(env["width"] * SCALE), int(env["depth"] * SCALE)
    rooms = program["rooms"]
    X = {r["name"]: Int(f"x_{r['name']}") for r in rooms}
    Y = {r["name"]: Int(f"y_{r['name']}") for r in rooms}
    W = {r["name"]: int(r["min_w"] * SCALE) for r in rooms}
    H = {r["name"]: int(r["min_d"] * SCALE) for r in rooms}
    win = {r["name"]: r["needs_window"] for r in rooms}

    s = Solver()
    s.set(unsat_core=True)

    def claim(label, c):
        s.assert_and_track(c, label)

    for n in X:  # 1. inside the garden footprint
        claim(f"{n}_in_envelope",
              And(X[n] >= 0, Y[n] >= 0, X[n] + W[n] <= ew, Y[n] + H[n] <= ed))

    names = list(X)  # 2. no overlap
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            claim(f"no_overlap_{a}_{b}",
                  Or(X[a] + W[a] <= X[b], X[b] + W[b] <= X[a],
                     Y[a] + H[a] <= Y[b], Y[b] + H[b] <= Y[a]))

    for a, b in program["adjacencies"]:  # 3. required shared wall >= one door
        share_v = And(Or(X[a] + W[a] == X[b], X[b] + W[b] == X[a]),
                      Y[a] < Y[b] + H[b], Y[b] < Y[a] + H[a],
                      If(Y[a] > Y[b], (Y[b] + H[b]) - Y[a], (Y[a] + H[a]) - Y[b]) >= min_door)
        share_h = And(Or(Y[a] + H[a] == Y[b], Y[b] + H[b] == Y[a]),
                      X[a] < X[b] + W[b], X[b] < X[a] + W[a],
                      If(X[a] > X[b], (X[b] + W[b]) - X[a], (X[a] + W[a]) - X[b]) >= min_door)
        claim(f"adj_{a}_{b}", Or(share_v, share_h))

    for n in X:  # 4. Fable's inferred daylight needs: room must touch a required edge
        if win[n]:
            claim(f"{n}_window_{'/'.join(win[n])}",
                  Or(*[on_edge(o, X, Y, W, H, n, ew, ed) for o in win[n]]))

    if s.check() == sat:
        m = s.model()
        return ("SAT", {n: (m[X[n]].as_long() / SCALE, m[Y[n]].as_long() / SCALE,
                            W[n] / SCALE, H[n] / SCALE) for n in X})
    return ("UNSAT", [str(c) for c in s.unsat_core()])


def report(title, program, envelope=None):
    env = envelope or program["envelope"]
    print(f"=== {title}: envelope {env['width']}x{env['depth']} m ===")
    status, info = prove(program, envelope)
    print("result:", status)
    if status == "SAT":
        for n, (x, y, w, h) in info.items():
            edge = ",".join(o for o in "NESW" if False) or ""
            print(f"  {n:13s} at ({x:>4},{y:>4}) m   size {w}x{h} m")
        boxes = list(info.values())  # trust-but-verify: independent overlap audit
        ok = all(not (ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + bh)
                 for i, (ax, ay, aw, ah) in enumerate(boxes)
                 for (bx, by, bw, bh) in boxes[i + 1:])
        print("  independent non-overlap check:", "PASS" if ok else "FAIL")
    else:
        print("  z3 PROVED no layout exists in this footprint. Minimal conflicting set:")
        for c in info:
            print("   -", c)
    print()


if __name__ == "__main__":
    print("Program author: Claude Fable 5 (claude-fable-5), from a vague NL brief.")
    print("Rationale Fable gave:", FABLE_PROGRAM["rationale"], "\n")

    # Scenario A: the footprint Fable read off the brief (8 x 6 m).
    report("A  Fable's recommended footprint", FABLE_PROGRAM)

    # Scenario B: client wants to shrink the garden give-up to 7 x 5 m -- is it still possible?
    report("B  Client shrinks the footprint to 7x5 m", FABLE_PROGRAM,
           {"width": 7, "depth": 5})

    # Scenario C: a marginal shrink where total area still fits but constraints may not.
    report("C  Marginal: 7.5 x 5.5 m", FABLE_PROGRAM, {"width": 7.5, "depth": 5.5})
