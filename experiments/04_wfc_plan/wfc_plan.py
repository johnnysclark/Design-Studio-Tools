"""Wave Function Collapse for architectural PLAN FIELDS (Kind B, built from scratch).

Tiles are program/room types. An adjacency-compatibility matrix encodes real
planning logic (wet rooms cluster, circulation connects everything, bedrooms not
adjacent to kitchen, habitable rooms need exterior contact via WALL). The solver
runs observe / collapse / propagate with a min-entropy heuristic and
restart-on-contradiction with a fresh seed.
"""
import sys
import numpy as np

# ---- Tileset: architectural cell types -------------------------------------
WALL, CORRIDOR, LIVING, KITCHEN, BATH, BED, COURTYARD = range(7)
NAMES = ["WALL", "CORRIDOR", "LIVING", "KITCHEN", "BATH", "BED", "COURTYARD"]
GLYPH = ["#", "+", "L", "K", "B", "D", "O"]            # ASCII preview
RGB = [(0.25, 0.25, 0.25), (0.95, 0.85, 0.25), (0.40, 0.70, 0.95),
       (0.95, 0.55, 0.25), (0.30, 0.85, 0.80), (0.70, 0.45, 0.85),
       (0.55, 0.80, 0.45)]                              # plan.png / .3dm colors
ZHEIGHT = [3.0, 0.3, 3.0, 3.0, 3.0, 3.0, 0.0]           # 3dm extrusion by type
N = len(NAMES)

# ---- Adjacency rules: COMPAT[a,b]=1 means a may sit next to b (orthogonally) -
# Planning logic encoded below; symmetric matrix.
COMPAT = np.zeros((N, N), dtype=np.uint8)


def allow(a, b):
    COMPAT[a, b] = COMPAT[b, a] = 1


# WALL is the connective tissue / exterior; it borders everything.
for t in range(N):
    allow(WALL, t)
# CORRIDOR is circulation: connects to all habitable rooms (not courtyard interior).
allow(CORRIDOR, CORRIDOR)
allow(CORRIDOR, LIVING)
allow(CORRIDOR, KITCHEN)
allow(CORRIDOR, BATH)
allow(CORRIDOR, BED)
# Wet rooms cluster: KITCHEN and BATH may touch each other and themselves.
allow(KITCHEN, KITCHEN); allow(BATH, BATH); allow(KITCHEN, BATH)
# Social core.
allow(LIVING, LIVING); allow(LIVING, KITCHEN)
# Bedrooms: cluster, touch bath (en-suite), but NOT kitchen, NOT living directly.
allow(BED, BED); allow(BED, BATH)
# Courtyard: open void, ringed by living/bed/wall (private outlook), not wet rooms.
allow(COURTYARD, LIVING); allow(COURTYARD, BED)
# (COURTYARD-COURTYARD intentionally allowed so courts can be larger than 1 cell)
allow(COURTYARD, COURTYARD)

# Explicit FORBIDDEN pairs we will verify never appear:
FORBIDDEN = [(BED, KITCHEN), (BED, LIVING), (BATH, LIVING),
             (COURTYARD, KITCHEN), (COURTYARD, BATH)]

# Weights bias the mix (more wall/corridor structure, fewer courtyards).
WEIGHT = np.array([4.0, 3.0, 3.0, 1.5, 1.5, 3.0, 0.8])

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def solve(H, W, seed, max_restarts=40):
    """Return (grid, steps, restarts) or raise RuntimeError if it never settles."""
    rng = np.random.default_rng(seed)
    total_steps = 0
    for restart in range(max_restarts):
        # wave[y,x,t] = tile t still possible at cell (y,x)
        wave = np.ones((H, W, N), dtype=bool)
        # Border bias: force the outer ring toward WALL to give exterior envelope.
        ok = True
        steps = 0
        while True:
            ent = wave.sum(axis=2)
            undecided = ent > 1
            if not undecided.any():
                break  # fully collapsed
            if (ent == 0).any():
                ok = False
                break  # contradiction
            # Min-entropy heuristic with tiny noise to break ties deterministically.
            noisy = np.where(undecided, ent + rng.random((H, W)) * 0.1, np.inf)
            y, x = np.unravel_index(np.argmin(noisy), noisy.shape)
            # Observe: collapse this cell to one tile, weighted by WEIGHT.
            choices = np.flatnonzero(wave[y, x])
            w = WEIGHT[choices]
            # Border preference: outer ring strongly prefers WALL/COURTYARD void.
            if y in (0, H - 1) or x in (0, W - 1):
                w = w * np.where(choices == WALL, 6.0, 1.0)
            pick = rng.choice(choices, p=w / w.sum())
            wave[y, x] = False
            wave[y, x, pick] = True
            steps += 1
            total_steps += 1
            # Propagate constraints from the just-collapsed cell.
            stack = [(y, x)]
            while stack:
                cy, cx = stack.pop()
                cur = wave[cy, cx]
                # Tiles allowed next to ANY tile currently possible at (cy,cx).
                allowed_neighbor = (COMPAT[cur].any(axis=0))
                for dy, dx in DIRS:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < H and 0 <= nx < W:
                        before = wave[ny, nx].copy()
                        wave[ny, nx] &= allowed_neighbor
                        if not np.array_equal(before, wave[ny, nx]):
                            if not wave[ny, nx].any():
                                ok = False
                                stack.clear()
                                break
                            stack.append((ny, nx))
                if not ok:
                    break
            if not ok:
                break
        if ok:
            grid = wave.argmax(axis=2).astype(int)
            return grid, total_steps, restart
        # else: contradiction -> reseed and restart
        rng = np.random.default_rng(seed + 1000 * (restart + 1))
    raise RuntimeError(f"no solution after {max_restarts} restarts (seed {seed})")


def verify(grid):
    """Spot-check: return list of forbidden adjacencies actually present."""
    H, W = grid.shape
    hits = []
    fset = {frozenset(p) for p in FORBIDDEN}
    for y in range(H):
        for x in range(W):
            for dy, dx in [(1, 0), (0, 1)]:
                ny, nx = y + dy, x + dx
                if ny < H and nx < W:
                    if frozenset((grid[y, x], grid[ny, nx])) in fset:
                        hits.append(((y, x), (ny, nx),
                                     NAMES[grid[y, x]], NAMES[grid[ny, nx]]))
    return hits


def ascii_plan(grid):
    return "\n".join("".join(GLYPH[t] for t in row) for row in grid)


def save_png(grid, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    from matplotlib.patches import Patch
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.imshow(grid, cmap=ListedColormap(RGB), vmin=0, vmax=N - 1)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("WFC architectural plan field")
    ax.legend(handles=[Patch(color=RGB[i], label=NAMES[i]) for i in range(N)],
              loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)


def save_3dm(grid, path):
    import rhino3dm as r3
    model = r3.File3dm()
    layers = []
    for i, name in enumerate(NAMES):
        ly = r3.Layer()
        ly.Name = name
        ly.Color = (int(RGB[i][0] * 255), int(RGB[i][1] * 255),
                    int(RGB[i][2] * 255), 255)
        layers.append(model.Layers.Add(ly))
    H, W = grid.shape
    for y in range(H):
        for x in range(W):
            t = int(grid[y, x])
            z = ZHEIGHT[t]
            if z <= 0:  # courtyard void: skip solid, leave open
                continue
            box = r3.Box(r3.BoundingBox(x, H - 1 - y, 0.0,
                                        x + 0.98, H - 1 - y + 0.98, z))
            brep = r3.Brep.CreateFromBox(box)
            att = r3.ObjectAttributes()
            att.LayerIndex = layers[t]
            model.Objects.AddBrep(brep, att)
    model.Write(path, 7)


def main():
    H, W = 12, 16
    base = "/home/user/Design-Studio-Tools/experiments/04_wfc_plan/"
    seeds = [7, 42, 123]
    results = []
    for seed in seeds:
        grid, steps, restarts = solve(H, W, seed)
        hits = verify(grid)
        results.append((seed, grid, steps, restarts, hits))
        print(f"seed={seed:4d}  SOLVED  steps={steps:4d}  restarts={restarts}  "
              f"forbidden_adjacencies={len(hits)}")
    # Save artifacts from the first seed.
    seed0, grid0, *_ = results[0]
    save_png(grid0, base + "plan.png")
    save_3dm(grid0, base + "plan.3dm")
    print(f"\nwrote plan.png and plan.3dm (seed {seed0})")
    print(f"\nASCII preview (seed {seed0}):  "
          + "  ".join(f"{GLYPH[i]}={NAMES[i]}" for i in range(N)))
    print(ascii_plan(grid0))
    total_hits = sum(len(r[4]) for r in results)
    print(f"\nVERDICT: {len(results)} plans, {total_hits} forbidden adjacencies "
          f"across all -> rules {'RESPECTED' if total_hits == 0 else 'VIOLATED'}")


if __name__ == "__main__":
    main()
