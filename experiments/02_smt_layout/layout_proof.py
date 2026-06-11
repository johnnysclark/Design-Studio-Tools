"""SMT spatial reasoning: a layout solver that can PROVE a brief is impossible.

Thread: New epistemologies / SAT-SMT spatial proofs (Kind B: dead/unused in arch practice).
Library: z3-solver 4.16 (Microsoft Research), pure-Python API, headless.

A generate-and-test layout tool answers "here is a plan." An SMT solver answers a
*different* question: "does ANY plan satisfy this brief?" When the answer is no, z3
returns an unsat core -- a minimal subset of requirements that contradict each other.
That is a proof of impossibility, not a failed search. For an architect arguing with a
program or a zoning envelope, "these three requirements cannot coexist" is a stronger
statement than "I tried and couldn't."

We model rooms as axis-aligned rectangles packed in a W x H envelope, non-overlapping,
some with required adjacencies (shared wall length >= door width).
"""
from z3 import (
    Int, Optimize, Solver, Or, And, If, sat, unsat,
)

# room: (name, w, h)
def layout(envelope_w, envelope_h, rooms, adjacencies, min_door=1):
    s = Solver()
    s.set(unsat_core=True)
    X = {r[0]: Int(f"x_{r[0]}") for r in rooms}
    Y = {r[0]: Int(f"y_{r[0]}") for r in rooms}
    W = {r[0]: r[1] for r in rooms}
    H = {r[0]: r[2] for r in rooms}

    track = []  # named assertions so unsat cores are human-readable
    def claim(label, c):
        s.assert_and_track(c, label)
        track.append(label)

    # 1. every room sits inside the envelope
    for n in X:
        claim(f"{n}_in_envelope",
              And(X[n] >= 0, Y[n] >= 0,
                  X[n] + W[n] <= envelope_w, Y[n] + H[n] <= envelope_h))

    # 2. no two rooms overlap
    names = list(X)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            claim(f"no_overlap_{a}_{b}",
                  Or(X[a] + W[a] <= X[b], X[b] + W[b] <= X[a],
                     Y[a] + H[a] <= Y[b], Y[b] + H[b] <= Y[a]))

    # 3. required adjacencies: rooms share a wall segment >= min_door
    for a, b in adjacencies:
        share_v = And(Or(X[a] + W[a] == X[b], X[b] + W[b] == X[a]),
                      Y[a] < Y[b] + H[b], Y[b] < Y[a] + H[a],
                      If(Y[a] > Y[b], (Y[b] + H[b]) - Y[a], (Y[a] + H[a]) - Y[b]) >= min_door)
        share_h = And(Or(Y[a] + H[a] == Y[b], Y[b] + H[b] == Y[a]),
                      X[a] < X[b] + W[b], X[b] < X[a] + W[a],
                      If(X[a] > X[b], (X[b] + W[b]) - X[a], (X[a] + W[a]) - X[b]) >= min_door)
        claim(f"adj_{a}_{b}", Or(share_v, share_h))

    if s.check() == sat:
        m = s.model()
        return ("SAT", {n: (m[X[n]].as_long(), m[Y[n]].as_long(), W[n], H[n]) for n in X})
    return ("UNSAT", [str(c) for c in s.unsat_core()])


rooms = [("living", 5, 4), ("kitchen", 3, 3), ("bath", 2, 2), ("bed", 4, 4)]
adj = [("living", "kitchen"), ("living", "bed"), ("kitchen", "bath")]

print("=== Scenario A: 8x8 envelope (feasible) ===")
status, info = layout(8, 8, rooms, adj)
print("result:", status)
if status == "SAT":
    for n, (x, y, w, h) in info.items():
        print(f"  {n:8s} at ({x},{y}) size {w}x{h}")
    # quick independent overlap check to trust the solver
    boxes = list(info.values())
    ok = all(not (ax < bx+bw and bx < ax+aw and ay < by+bh and by < ay+bh)
             for i,(ax,ay,aw,ah) in enumerate(boxes)
             for (bx,by,bw,bh) in boxes[i+1:])
    print("  independent non-overlap check:", "PASS" if ok else "FAIL")

print("\n=== Scenario B: 6x6 envelope, same brief (over-constrained) ===")
status, core = layout(6, 6, rooms, adj)
print("result:", status)
if status == "UNSAT":
    print("  z3 PROVED no layout exists. Minimal conflicting requirements (unsat core):")
    for c in core:
        print("   -", c)

print("\n=== Scenario C: contradictory adjacency (bath touching everything in a tiny envelope) ===")
status, core = layout(5, 5, [("a",3,3),("b",3,3),("c",3,3)],
                      [("a","b"),("b","c"),("a","c")])
print("result:", status)
if status == "UNSAT":
    print("  Proven impossible.  Core size:", len(core), "requirements")
