"""
06_cutting_stock — Material logic / cutting-stock + nesting optimization

Given a real cut list from a parametric model, minimize waste against actual
stock. Two flavors:
  (a) 1D  — linear lumber/timber packed onto fixed stock board lengths.
  (b) 2D  — plywood parts nested onto standard 1220 x 2440 sheets.

The unglamorous optimization that decides whether a design is buildable
affordably. Headless CPU-only; deterministic.
"""

import matplotlib
matplotlib.use("Agg")

import collections
import os

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import colormaps


def get_cmap(name):
    return colormaps[name]

from ortools.sat.python import cp_model
from rectpack import newPacker, PackingMode, PackingBin
import rectpack.guillotine as guillotine

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# (a) 1D CUTTING STOCK  — timber framing cut list
# ---------------------------------------------------------------------------
# A realistic stud/plate/header cut list pulled from a parametric timber frame
# (lengths in mm, with multiplicities). Wall studs, top/bottom plates, headers,
# noggins. We allow several commercial stock lengths and let the solver choose.
KERF = 3  # mm, saw blade kerf — consumed at each internal cut

# (length_mm, count)
CUT_LIST_1D = [
    (2400, 18),  # full-height wall studs
    (2700,  6),  # tall studs (raked wall)
    (1200, 14),  # noggins / blocking
    (900,  10),  # cripple studs / sill blocking
    (3300,  4),  # long top plates
    (1800,  8),  # headers
    (600,  12),  # short cripples
]

# Commercial stock lengths available (mm). Solver picks per board.
STOCK_LENGTHS_1D = [2400, 3600, 4800, 5400]


def solve_1d(cut_list, stock_lengths, kerf):
    """
    Greedy column-generation-style heuristic refined with CP-SAT per board.

    Strategy: we expand the cut list into individual pieces, then repeatedly
    pick the *best stock length + cut pattern* that minimizes waste using a
    bounded-knapsack CP-SAT solve. This is the classic 'pattern at a time'
    approach and gives near-optimal board counts for modest lists.

    Kerf is charged once per cut *between* pieces on a board (n pieces -> n-1
    internal kerfs; the off-cut end is free).
    """
    # remaining demand per unique length
    demand = collections.Counter()
    for length, count in cut_list:
        demand[length] += count

    boards = []  # list of dicts: {stock, pieces:[lengths], used, kerf, waste}

    while sum(demand.values()) > 0:
        best = None
        for stock in stock_lengths:
            # Bounded knapsack: choose how many of each length fit on one board,
            # maximizing consumed length (stock - waste). Kerf modeled by adding
            # KERF to every piece except we credit one kerf back (end off-cut).
            model = cp_model.CpModel()
            lengths = sorted(demand.keys())
            xs = {}
            for L in lengths:
                if L > stock:
                    continue
                xs[L] = model.NewIntVar(0, demand[L], f"x_{L}")

            if not xs:
                continue

            # number of pieces on this board
            n_pieces = model.NewIntVar(0, sum(demand.values()), "n")
            model.Add(n_pieces == sum(xs.values()))

            # total occupied = sum(L * x) + kerf * (n_pieces - 1), floored at 0
            # We require occupancy <= stock. Express kerf term carefully.
            occupied = model.NewIntVar(0, stock, "occ")
            # raw material length used by pieces
            piece_len = sum(L * xs[L] for L in xs)
            # kerf count = exactly max(n_pieces - 1, 0). n_pieces>=1 below, so
            # kerf_count == n_pieces - 1 exactly (no phantom kerf to soak slack).
            kerf_count = model.NewIntVar(0, sum(demand.values()), "kc")
            model.Add(n_pieces >= 1)  # board must hold at least one piece
            model.Add(kerf_count == n_pieces - 1)
            model.Add(occupied == piece_len + kerf * kerf_count)
            model.Add(occupied <= stock)

            # maximize material actually cut into pieces (minimize off-cut).
            # Use piece_len, not occupied, so kerf is treated as loss not gain.
            model.Maximize(piece_len)

            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = 2.0
            solver.parameters.num_search_workers = 4
            status = solver.Solve(model)
            if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                continue

            occ = solver.Value(occupied)
            waste = stock - occ
            # Prefer the pattern that wastes least; tie-break to longer stock so
            # we consume demand faster (fewer boards). Score = waste; lower wins.
            pattern = {L: solver.Value(xs[L]) for L in xs if solver.Value(xs[L]) > 0}
            cand = {
                "stock": stock,
                "pattern": pattern,
                "occupied": occ,
                "waste": waste,
                "n_pieces": solver.Value(n_pieces),
            }
            if best is None or cand["waste"] < best["waste"] or (
                cand["waste"] == best["waste"] and cand["stock"] > best["stock"]
            ):
                best = cand

        if best is None:
            # demand contains a piece longer than every stock length
            raise ValueError("A required length exceeds all stock lengths.")

        # commit best pattern, decrement demand
        pieces = []
        for L, c in best["pattern"].items():
            for _ in range(c):
                pieces.append(L)
            demand[L] -= c
            if demand[L] <= 0:
                del demand[L]
        boards.append({
            "stock": best["stock"],
            "pieces": sorted(pieces, reverse=True),
            "occupied": best["occupied"],
            "waste": best["waste"],
        })

    return boards


def report_1d(cut_list, boards, kerf):
    total_required = sum(L * c for L, c in cut_list)
    total_stock = sum(b["stock"] for b in boards)
    total_waste = sum(b["waste"] for b in boards)
    total_kerf = sum(max(len(b["pieces"]) - 1, 0) * kerf for b in boards)
    n_pieces_required = sum(c for _, c in cut_list)
    n_pieces_placed = sum(len(b["pieces"]) for b in boards)

    waste_pct = 100.0 * total_waste / total_stock

    print("=" * 68)
    print("(a) 1D CUTTING STOCK  — timber framing cut list")
    print("=" * 68)
    print(f"  Stock lengths available : {STOCK_LENGTHS_1D} mm")
    print(f"  Kerf per internal cut   : {kerf} mm")
    print(f"  Distinct pieces required: {len(cut_list)} sizes, "
          f"{n_pieces_required} total pieces")
    print(f"  Total required length   : {total_required:,} mm "
          f"({total_required/1000:.2f} m)")
    print(f"  Boards used             : {len(boards)}")
    print(f"  Total stock length      : {total_stock:,} mm "
          f"({total_stock/1000:.2f} m)")
    print(f"  Kerf loss (sawdust)     : {total_kerf:,} mm")
    print(f"  Waste (off-cuts+kerf)   : {total_waste:,} mm")
    print(f"  Waste %                 : {waste_pct:.2f} %")
    print(f"  Utilization %           : {100 - waste_pct:.2f} %")
    print()
    print("  Cut pattern per board:")
    stock_count = collections.Counter(b["stock"] for b in boards)
    for i, b in enumerate(boards, 1):
        patt = " + ".join(str(p) for p in b["pieces"])
        print(f"   #{i:2d}  [{b['stock']}mm stock]  {patt}"
              f"   (waste {b['waste']}mm)")
    print()
    print("  Stock board tally:")
    for s in sorted(stock_count):
        print(f"   {stock_count[s]:2d} x {s}mm")
    print()

    # self-consistency check
    consumed = total_required + total_kerf + total_waste
    assert consumed == total_stock, (
        f"Inconsistent: required+kerf+waste={consumed} != stock={total_stock}")
    assert n_pieces_placed == n_pieces_required, "piece count mismatch"
    print(f"  [check] required({total_required}) + kerf({total_kerf}) + "
          f"waste({total_waste}) = {consumed} == stock({total_stock})  OK")
    print()
    return {
        "boards": boards,
        "waste_pct": waste_pct,
        "total_stock": total_stock,
        "total_required": total_required,
    }


# ---------------------------------------------------------------------------
# (b) 2D NESTING  — plywood parts onto standard sheets
# ---------------------------------------------------------------------------
SHEET_W, SHEET_H = 1220, 2440  # standard plywood sheet (mm)

# (label, w, h, count) — cabinetry / furniture parts from a parametric model
PARTS_2D = [
    ("Side",      600, 720, 8),
    ("Shelf",     564, 300, 12),
    ("Back",      600, 720, 4),
    ("Door",      297, 720, 8),
    ("Base",      564, 600, 4),
    ("Top",       600, 564, 4),
    ("Divider",   300, 690, 6),
]


def solve_2d(parts, sheet_w, sheet_h):
    packer = newPacker(
        mode=PackingMode.Offline,
        bin_algo=PackingBin.Global,
        pack_algo=guillotine.GuillotineBssfSas,  # guillotine cuts, realistic for panel saw
        rotation=True,
    )

    rid = 0
    rid_meta = {}
    total_parts = 0
    for label, w, h, count in parts:
        for _ in range(count):
            packer.add_rect(w, h, rid=rid)
            rid_meta[rid] = (label, w, h)
            rid += 1
            total_parts += 1

    # add plenty of sheets; packer uses only what it needs
    max_sheets = total_parts  # upper bound
    for _ in range(max_sheets):
        packer.add_bin(sheet_w, sheet_h)

    packer.pack()
    return packer, rid_meta, total_parts


def report_2d(packer, rid_meta, total_parts, sheet_w, sheet_h):
    sheet_area = sheet_w * sheet_h
    placed = 0
    used_area = 0
    bins_used = 0
    layouts = []  # per sheet: list of (label, x, y, w, h)

    for abin in packer:
        rects = list(abin)
        if not rects:
            continue
        bins_used += 1
        sheet_rects = []
        for rect in rects:
            placed += 1
            used_area += rect.width * rect.height
            label = rid_meta[rect.rid][0]
            sheet_rects.append((label, rect.x, rect.y, rect.width, rect.height))
        layouts.append(sheet_rects)

    total_sheet_area = bins_used * sheet_area
    utilization = 100.0 * used_area / total_sheet_area if total_sheet_area else 0.0

    print("=" * 68)
    print("(b) 2D NESTING  — plywood parts onto standard sheets")
    print("=" * 68)
    print(f"  Sheet size              : {sheet_w} x {sheet_h} mm "
          f"({sheet_area/1e6:.3f} m^2 each)")
    print(f"  Parts requested         : {total_parts}")
    print(f"  Parts placed            : {placed}")
    print(f"  Sheets used             : {bins_used}")
    print(f"  Total sheet area        : {total_sheet_area/1e6:.3f} m^2")
    print(f"  Part area placed        : {used_area/1e6:.3f} m^2")
    print(f"  Sheet utilization %     : {utilization:.2f} %")
    print(f"  Offcut / waste %        : {100 - utilization:.2f} %")
    print()
    for i, sheet in enumerate(layouts, 1):
        sused = sum(w * h for _, _, _, w, h in sheet)
        print(f"   Sheet #{i}: {len(sheet)} parts, "
              f"{100*sused/sheet_area:.1f}% used")
    print()

    # consistency checks
    assert placed <= total_parts, "placed more than requested!"
    assert utilization <= 100.0 + 1e-9, "utilization > 100%!"
    print(f"  [check] placed({placed}) <= requested({total_parts})  OK")
    print(f"  [check] utilization({utilization:.2f}%) <= 100%  OK")
    if placed != total_parts:
        print(f"  [warn] {total_parts - placed} parts did not fit "
              f"(would need more sheets).")
    print()
    return layouts, utilization, bins_used


def draw_2d(layouts, sheet_w, sheet_h, out_path):
    n = len(layouts)
    fig, axes = plt.subplots(1, n, figsize=(3.2 * n, 7))
    if n == 1:
        axes = [axes]

    cmap = get_cmap("tab20")
    # stable color per label
    labels = sorted({r[0] for sheet in layouts for r in sheet})
    color_of = {lab: cmap(i % 20) for i, lab in enumerate(labels)}

    for ax, sheet in zip(axes, layouts):
        idx = layouts.index(sheet)
        ax.add_patch(patches.Rectangle((0, 0), sheet_w, sheet_h,
                                       fill=False, edgecolor="black", lw=2))
        used = 0
        for label, x, y, w, h in sheet:
            used += w * h
            ax.add_patch(patches.Rectangle(
                (x, y), w, h, facecolor=color_of[label],
                edgecolor="black", lw=0.6, alpha=0.85))
            ax.text(x + w / 2, y + h / 2, f"{label}\n{int(w)}x{int(h)}",
                    ha="center", va="center", fontsize=6)
        util = 100 * used / (sheet_w * sheet_h)
        ax.set_title(f"Sheet {idx+1}\n{util:.1f}% used", fontsize=9)
        ax.set_xlim(-40, sheet_w + 40)
        ax.set_ylim(-40, sheet_h + 40)
        ax.set_aspect("equal")
        ax.set_xticks([0, sheet_w])
        ax.set_yticks([0, sheet_h])

    fig.suptitle("2D Plywood Nesting — 1220 x 2440 sheets (guillotine, rot. allowed)",
                 fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out_path, dpi=110)
    plt.close(fig)
    print(f"  Saved nesting layout -> {out_path}")


def draw_1d_bar(boards, out_path):
    """Stacked horizontal bar chart of each board's cut pattern + waste."""
    fig, ax = plt.subplots(figsize=(9, max(3, 0.32 * len(boards))))
    cmap = get_cmap("viridis")
    for i, b in enumerate(boards):
        x = 0
        npieces = len(b["pieces"])
        for j, p in enumerate(b["pieces"]):
            ax.barh(i, p, left=x, height=0.7,
                    color=cmap(0.15 + 0.7 * (p / 5400)),
                    edgecolor="white", lw=0.4)
            if p >= 600:
                ax.text(x + p / 2, i, str(p), ha="center", va="center",
                        fontsize=6, color="white")
            x += p
            if j < npieces - 1:
                x += KERF  # kerf gap (tiny, invisible)
        if b["waste"] > 0:
            ax.barh(i, b["waste"], left=x, height=0.7,
                    color="lightcoral", edgecolor="white", lw=0.4)
    ax.set_yticks(range(len(boards)))
    ax.set_yticklabels([f"#{i+1} ({b['stock']}mm)" for i, b in enumerate(boards)],
                       fontsize=7)
    ax.set_xlabel("mm along board (red = waste off-cut)")
    ax.set_title("1D Cutting Stock — cut pattern per board")
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    plt.close(fig)
    print(f"  Saved 1D pattern chart -> {out_path}")


def main():
    boards = solve_1d(CUT_LIST_1D, STOCK_LENGTHS_1D, KERF)
    report_1d(CUT_LIST_1D, boards, KERF)

    packer, rid_meta, total_parts = solve_2d(PARTS_2D, SHEET_W, SHEET_H)
    layouts, utilization, bins_used = report_2d(
        packer, rid_meta, total_parts, SHEET_W, SHEET_H)

    print("=" * 68)
    print("VISUALIZATIONS")
    print("=" * 68)
    draw_2d(layouts, SHEET_W, SHEET_H, os.path.join(HERE, "nesting.png"))
    draw_1d_bar(boards, os.path.join(HERE, "cut_pattern_1d.png"))
    print()


if __name__ == "__main__":
    main()
