"""A minimal but genuine 2D shape grammar interpreter (Stiny & Gips style).

A Shape is a collection of labeled line segments plus labeled markers.
A Rule is LHS -> RHS keyed on a marker label; it fires under a transformation
T (translation + uniform scale + rotation) carried by the matched marker.
The derivation engine repeatedly picks an applicable rule (seeded RNG) and
rewrites the shape, growing an architectural pattern step by step.

Marker-driven matching (a legitimate, tractable subclass of shape grammars):
each marker stores a local frame (position, scale, angle); a rule's RHS is
authored in that local frame and mapped into world space by the marker frame.
"""
import math
import numpy as np


# ----------------------------- geometry core -----------------------------
def frame(x, y, scale=1.0, angle_deg=0.0):
    """A marker frame: where/how big/which way a future rule will draw."""
    return {"pos": np.array([x, y], float), "scale": float(scale),
            "angle": float(angle_deg)}


def apply_frame(frame_, pt):
    """Map a point authored in unit-frame coords into world coords."""
    a = math.radians(frame_["angle"])
    c, s = math.cos(a), math.sin(a)
    R = np.array([[c, -s], [s, c]])
    return frame_["pos"] + frame_["scale"] * (R @ np.asarray(pt, float))


class Shape:
    """Segments: list of (p0, p1, label). Markers: list of (frame, label)."""
    def __init__(self):
        self.segments = []   # (np[2], np[2], str)
        self.markers = []    # (frame_dict, str)

    def add_seg(self, p0, p1, label="wall"):
        self.segments.append((np.asarray(p0, float), np.asarray(p1, float), label))

    def add_marker(self, frame_, label):
        self.markers.append((frame_, label))

    def copy(self):
        s = Shape()
        s.segments = [(p0.copy(), p1.copy(), l) for p0, p1, l in self.segments]
        s.markers = [(dict(f, pos=f["pos"].copy()), l) for f, l in self.markers]
        return s

    def complexity(self):
        return len(self.segments), len(self.markers)


# ----------------------------- rules -----------------------------
class Rule:
    """LHS = a marker with `label`. RHS = a function(frame) -> (segs, markers)
    authored in the matched marker's local frame."""
    def __init__(self, name, label, rhs):
        self.name = name
        self.label = label
        self.rhs = rhs

    def matches(self, shape):
        return [i for i, (_, lab) in enumerate(shape.markers) if lab == self.label]

    def apply(self, shape, marker_index):
        out = shape.copy()
        f, _ = out.markers.pop(marker_index)          # consume the LHS marker
        segs, new_markers = self.rhs(f)
        for p0, p1, lab in segs:
            out.add_seg(apply_frame(f, p0), apply_frame(f, p1), lab)
        for local_frame, lab in new_markers:
            # compose marker's local frame with parent frame f
            wpos = apply_frame(f, local_frame["pos"])
            out.add_marker(frame(wpos[0], wpos[1],
                                 f["scale"] * local_frame["scale"],
                                 f["angle"] + local_frame["angle"]), lab)
        return out


# ----------------------------- derivation engine -----------------------------
def derive(shape, rules, k_steps, seed=0, verbose=True):
    rng = np.random.default_rng(seed)
    history = [shape.copy()]
    fired = []
    cur = shape
    for step in range(k_steps):
        applicable = [(r, idx) for r in rules for idx in r.matches(cur)]
        if not applicable:
            if verbose:
                print(f"step {step+1}: no applicable rule, derivation halts")
            break
        # control: prefer splitting large bays; resolve small bays to terminals.
        # a marker's frame scale encodes how big the bay is -> drives rule choice.
        weights = []
        for r, idx in applicable:
            f, _ = cur.markers[idx]
            big = f["scale"] > 0.9            # still room to subdivide
            if r.name == "tripartite-split":
                weights.append(3.0 if big else 0.0)
            else:                             # window / door are terminals
                weights.append(0.2 if big else 1.0)
        w = np.array(weights, float)
        if w.sum() == 0:
            w[:] = 1.0
        choice = int(rng.choice(len(applicable), p=w / w.sum()))
        r, idx = applicable[choice]
        cur = r.apply(cur, idx)
        history.append(cur.copy())
        fired.append(r.name)
        ns, nm = cur.complexity()
        if verbose:
            print(f"step {step+1}: fired '{r.name}'  ->  "
                  f"segments={ns}, open markers={nm}")
    return history, fired


# ----------------------------- a real architectural grammar -----------------------------
# Recursive Palladian-style facade: an open bay (marker 'bay') splits into a
# wall frame + 3 narrower bays; a bay can instead resolve to a window or a door.
def make_facade_grammar():
    def r_tripart(f):
        # frame the bay and emit 3 child bays side by side inside it
        segs = [((0, 0), (1, 0), "ground"),
                ((0, 0), (0, 1), "pier"),
                ((1, 0), (1, 1), "pier"),
                ((0, 1), (1, 1), "cornice")]
        m = [(frame(0.06, 0.10, 0.28, 0), "bay"),
             (frame(0.36, 0.10, 0.28, 0), "bay"),
             (frame(0.66, 0.10, 0.28, 0), "bay")]
        return segs, m

    def r_window(f):
        # a punched window with a sill and a mullion
        segs = [((0.15, 0.15), (0.85, 0.15), "sill"),
                ((0.15, 0.15), (0.15, 0.80), "jamb"),
                ((0.85, 0.15), (0.85, 0.80), "jamb"),
                ((0.15, 0.80), (0.85, 0.80), "lintel"),
                ((0.50, 0.15), (0.50, 0.80), "mullion")]
        return segs, []

    def r_door(f):
        # arched-ish doorway (chamfered top) reaching the ground
        segs = [((0.20, 0.0), (0.20, 0.70), "jamb"),
                ((0.80, 0.0), (0.80, 0.70), "jamb"),
                ((0.20, 0.70), (0.40, 0.92), "arch"),
                ((0.40, 0.92), (0.60, 0.92), "arch"),
                ((0.60, 0.92), (0.80, 0.70), "arch")]
        return segs, []

    return [Rule("tripartite-split", "bay", r_tripart),
            Rule("window", "bay", r_window),
            Rule("door", "bay", r_door)]


def initial_facade():
    s = Shape()
    # outer building outline
    s.add_seg((0, 0), (6, 0), "ground")
    s.add_seg((0, 0), (0, 4), "corner")
    s.add_seg((6, 0), (6, 4), "corner")
    s.add_seg((0, 4), (6, 4), "roofline")
    # one big open bay filling the facade
    s.add_marker(frame(0.3, 0.3, 5.4, 0), "bay")
    return s


# ----------------------------- output -----------------------------
def _draw(ax, shape, title):
    import matplotlib.pyplot as plt  # noqa
    for p0, p1, _ in shape.segments:
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], "-", color="#1a1a1a", lw=1.1)
    for f, lab in shape.markers:
        ax.plot(*f["pos"], "o", color="#cc3333", ms=4)
    ax.set_aspect("equal")
    ax.set_xlim(-0.5, 6.5)
    ax.set_ylim(-0.5, 4.7)
    ax.set_title(title, fontsize=9)
    ax.axis("off")


def save_derivation_png(history, fired, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    n = len(history)
    fig, axes = plt.subplots(1, n, figsize=(3.0 * n, 3.2))
    if n == 1:
        axes = [axes]
    for i, (ax, sh) in enumerate(zip(axes, history)):
        title = "initial" if i == 0 else f"{i}: {fired[i-1]}"
        _draw(ax, sh, title)
    fig.suptitle("Shape-grammar derivation: recursive facade", fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def save_final_svg(shape, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 4))
    for p0, p1, _ in shape.segments:
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], "-", color="black", lw=1.2)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, format="svg")
    plt.close(fig)


def save_final_3dm(shape, path):
    try:
        import rhino3dm as r3
    except Exception as e:
        print(f"rhino3dm unavailable, skipping 3dm: {e}")
        return False
    model = r3.File3dm()
    for p0, p1, _ in shape.segments:
        a = r3.Point3d(float(p0[0]), float(p0[1]), 0.0)
        b = r3.Point3d(float(p1[0]), float(p1[1]), 0.0)
        model.Objects.AddLine(a, b)
    model.Write(path, 7)
    return True


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    rules = make_facade_grammar()
    shape = initial_facade()
    print("Initial shape complexity:", shape.complexity())
    print("Grammar rules:", [r.name for r in rules])
    print("-" * 56)
    history, fired = derive(shape, rules, k_steps=12, seed=7)
    print("-" * 56)
    final = history[-1]
    print("Rules fired in order:", fired)
    print("Final complexity (segments, open markers):", final.complexity())

    png = os.path.join(here, "derivation.png")
    svg = os.path.join(here, "final.svg")
    dm = os.path.join(here, "final.3dm")
    # show a legible 6-frame subset of the derivation
    idxs = sorted(set(np.linspace(0, len(history) - 1, 6).astype(int)))
    sub_hist = [history[i] for i in idxs]
    sub_fired = [fired[i - 1] if i > 0 else "" for i in idxs]
    save_derivation_png(sub_hist, sub_fired, png)
    save_final_svg(final, svg)
    ok3 = save_final_3dm(final, dm)
    print(f"wrote {png}")
    print(f"wrote {svg}")
    print(f"wrote {dm}" if ok3 else "skipped final.3dm")
