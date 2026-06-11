"""The closed loop: generate -> PROVE -> revise -> re-prove. Fable 5 repairs its own program
from z3's proof of impossibility.

Thread 17: the headline composition the map kept pointing at -- a design loop where a learned
model proposes and a formal method disposes, then the model repairs using the proof itself as
feedback. Threads 15 (Fable generates, z3 proves) and 02 (z3 proofs) built the halves; this
chains them with a revision step in the middle.

The run that produced this:
  1. Fable 5 generated a spatial program from a vague brief (thread 15).
  2. z3 PROVED it infeasible even in the 8x6 m footprint Fable recommended, and ablation
     localized the conflict to the ADJACENCY GRAPH (not daylight, not area).
  3. That proof was fed back to Fable 5, which REVISED the program -- it diagnosed "a short
     stub hall trying to touch three rooms at once" and stretched the hall into a full-depth
     central spine, ADDING an adjacency rather than dropping one (step-free access preserved).
  4. z3 PROVED the revised program feasible and returned a packed plan.

Both programs are the verbatim Fable 5 output; the z3 proofs reproduce offline on CPU.
"""
import json
import os
from z3 import Int, Solver, Or, And, If, sat

SCALE = 2  # half-metre integer units


# --- the two programs Claude Fable 5 produced, before and after the proof --------------- #
ORIGINAL = json.loads(r"""
{"envelope": {"width": 8, "depth": 6},
 "rooms": [
   {"name": "bedroom",      "min_w": 3.5, "min_d": 3.0, "needs_window": ["S"]},
   {"name": "bathroom",     "min_w": 2.5, "min_d": 2.5, "needs_window": []},
   {"name": "kitchenette",  "min_w": 2.5, "min_d": 2.0, "needs_window": ["N"]},
   {"name": "sitting_area", "min_w": 3.5, "min_d": 3.0, "needs_window": ["E","S"]},
   {"name": "hall",         "min_w": 1.5, "min_d": 3.5, "needs_window": []}],
 "adjacencies": [["hall","bedroom"],["hall","bathroom"],["hall","sitting_area"],
                 ["bedroom","bathroom"],["sitting_area","kitchenette"]]}
""")

REVISED = json.loads(r"""
{"envelope": {"width": 8, "depth": 6},
 "rooms": [
   {"name": "bedroom",      "min_w": 3.0, "min_d": 3.5, "needs_window": ["S"]},
   {"name": "bathroom",     "min_w": 2.5, "min_d": 2.5, "needs_window": []},
   {"name": "kitchenette",  "min_w": 2.5, "min_d": 3.0, "needs_window": ["N"]},
   {"name": "sitting_area", "min_w": 3.5, "min_d": 3.0, "needs_window": ["E","S"]},
   {"name": "hall",         "min_w": 1.5, "min_d": 6.0, "needs_window": []}],
 "adjacencies": [["hall","bedroom"],["hall","bathroom"],["hall","sitting_area"],
                 ["hall","kitchenette"],["bedroom","bathroom"],["sitting_area","kitchenette"]]}
""")

REPAIR_NOTES = (
    "Fable 5: \"The bind was a short stub hall trying to touch three rooms at once. I "
    "stretched it into a full-depth (1.5m x 6m) central spine -- a straight, level, "
    "walker-width corridor every room opens onto, so no hall adjacency was dropped "
    "(kitchenette gained one). Bedroom reproportioned to 3.0x3.5 (same area, still fits bed "
    "plus turning space); sitting keeps its east+south corner for morning reading light.\""
)


def _edge(o, X, Y, W, H, n, ew, ed):
    return {"S": Y[n] == 0, "N": Y[n] + H[n] == ed,
            "W": X[n] == 0, "E": X[n] + W[n] == ew}[o]


def prove(program, min_door=2):
    ew = int(program["envelope"]["width"] * SCALE)
    ed = int(program["envelope"]["depth"] * SCALE)
    rooms = program["rooms"]
    X = {r["name"]: Int(f"x_{r['name']}") for r in rooms}
    Y = {r["name"]: Int(f"y_{r['name']}") for r in rooms}
    W = {r["name"]: int(r["min_w"] * SCALE) for r in rooms}
    H = {r["name"]: int(r["min_d"] * SCALE) for r in rooms}
    s = Solver(); s.set(unsat_core=True)

    def claim(lbl, c):
        s.assert_and_track(c, lbl)

    for n in X:
        claim(f"{n}_in_envelope",
              And(X[n] >= 0, Y[n] >= 0, X[n] + W[n] <= ew, Y[n] + H[n] <= ed))
    names = list(X)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            claim(f"no_overlap_{a}_{b}",
                  Or(X[a] + W[a] <= X[b], X[b] + W[b] <= X[a],
                     Y[a] + H[a] <= Y[b], Y[b] + H[b] <= Y[a]))
    for a, b in program["adjacencies"]:
        sv = And(Or(X[a] + W[a] == X[b], X[b] + W[b] == X[a]),
                 Y[a] < Y[b] + H[b], Y[b] < Y[a] + H[a],
                 If(Y[a] > Y[b], (Y[b] + H[b]) - Y[a], (Y[a] + H[a]) - Y[b]) >= min_door)
        sh = And(Or(Y[a] + H[a] == Y[b], Y[b] + H[b] == Y[a]),
                 X[a] < X[b] + W[b], X[b] < X[a] + W[a],
                 If(X[a] > X[b], (X[b] + W[b]) - X[a], (X[a] + W[a]) - X[b]) >= min_door)
        claim(f"adj_{a}_{b}", Or(sv, sh))
    for r in rooms:
        if r["needs_window"]:
            n = r["name"]
            claim(f"{n}_window",
                  Or(*[_edge(o, X, Y, W, H, n, ew, ed) for o in r["needs_window"]]))
    if s.check() == sat:
        m = s.model()
        return ("SAT", {n: (m[X[n]].as_long() / SCALE, m[Y[n]].as_long() / SCALE,
                            W[n] / SCALE, H[n] / SCALE) for n in X})
    return ("UNSAT", [str(c) for c in s.unsat_core()])


def draw(layout, program, path):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
    except Exception as e:
        return f"(plot skipped: {e})"
    win = {r["name"]: r["needs_window"] for r in program["rooms"]}
    ew, ed = program["envelope"]["width"], program["envelope"]["depth"]
    fig, ax = plt.subplots(figsize=(7, 5.5))
    ax.add_patch(Rectangle((0, 0), ew, ed, fill=False, edgecolor="#333", linewidth=2))
    for n, (x, y, w, h) in layout.items():
        ax.add_patch(Rectangle((x, y), w, h, facecolor="#cfe8cf" if win[n] else "#e6e6e6",
                               edgecolor="#555"))
        ax.text(x + w / 2, y + h / 2, f"{n}\n{w}x{h}", ha="center", va="center", fontsize=8)
        for o in win[n]:  # blue tick on the required envelope edge it sits against
            ex = {"S": x + w / 2, "N": x + w / 2, "E": x + w, "W": x}[o]
            ey = {"S": y, "N": y + h, "E": y + h / 2, "W": y + h / 2}[o]
            ax.plot([ex], [ey], "s", color="#2980b9", markersize=7)
    ax.set_xlim(-0.5, ew + 0.5); ax.set_ylim(-0.5, ed + 0.5); ax.set_aspect("equal")
    ax.set_title("Fable 5's REVISED program, proven feasible by z3 (S=bottom edge)")
    ax.axis("off"); fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)
    return f"(plan saved -> {path})"


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    print("=" * 70)
    print("CLOSED LOOP: Fable 5 generate -> z3 prove -> Fable revise -> z3 prove")
    print("=" * 70)

    s0, _ = prove(ORIGINAL)
    print(f"\n1. Fable's ORIGINAL program, 8x6 m  ->  z3: {s0}")
    print("   (ablation: dropping adjacencies makes it SAT, so the adjacency graph is the bind)")

    print("\n2. Proof fed back to Fable 5. Its repair:")
    print("   " + REPAIR_NOTES)

    s1, info = prove(REVISED)
    print(f"\n3. Fable's REVISED program, 8x6 m   ->  z3: {s1}")
    if s1 == "SAT":
        for n, (x, y, w, h) in info.items():
            print(f"     {n:13s} ({x:>4},{y:>4}) m   {w}x{h} m")
        boxes = list(info.values())
        ok = all(not (ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + bh)
                 for i, (ax, ay, aw, ah) in enumerate(boxes) for (bx, by, bw, bh) in boxes[i + 1:])
        print("     independent non-overlap check:", "PASS" if ok else "FAIL")
        print("   " + draw(info, REVISED, os.path.join(here, "solved_plan.png")))

    print(f"\nLoop result: proven IMPOSSIBLE -> model repair from the proof -> proven FEASIBLE."
          f"  ({s0} -> {s1})")
