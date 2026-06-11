"""
SIMP topology optimization of an MBB beam.

Pure numpy/scipy port of the classic 88-line MATLAB code
(Andreassen et al., "Efficient topology optimization in MATLAB
using 88 lines of code", Struct Multidisc Optim, 2011).

Minimizes compliance subject to a volume constraint using:
  - SIMP material interpolation (penalty p)
  - a density (convolution) filter to avoid checkerboarding
  - the Optimality Criteria (OC) update
"""
import time
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def lk():
    """8x8 element stiffness matrix for a unit bilinear quad (plane stress, E=1, nu=0.3)."""
    E, nu = 1.0, 0.3
    k = np.array([
        0.5 - nu / 6, 0.125 + nu / 8, -0.25 - nu / 12, -0.125 + 3 * nu / 8,
        -0.25 + nu / 12, -0.125 - nu / 8, nu / 6, 0.125 - 3 * nu / 8,
    ])
    KE = E / (1 - nu ** 2) * np.array([
        [k[0], k[1], k[2], k[3], k[4], k[5], k[6], k[7]],
        [k[1], k[0], k[7], k[6], k[5], k[4], k[3], k[2]],
        [k[2], k[7], k[0], k[5], k[6], k[3], k[4], k[1]],
        [k[3], k[6], k[5], k[0], k[7], k[2], k[1], k[4]],
        [k[4], k[5], k[6], k[7], k[0], k[1], k[2], k[3]],
        [k[5], k[4], k[3], k[2], k[1], k[0], k[7], k[6]],
        [k[6], k[3], k[4], k[1], k[2], k[7], k[0], k[5]],
        [k[7], k[2], k[1], k[4], k[3], k[6], k[5], k[0]],
    ])
    return KE


def build_filter(nelx, nely, rmin):
    """Build the (sparse) density-filter weight matrix H and its row sums Hs."""
    nele = nelx * nely
    iH, jH, sH = [], [], []
    r = int(np.ceil(rmin)) - 1
    for i in range(nelx):
        for j in range(nely):
            e1 = i * nely + j
            for ii in range(max(i - r, 0), min(i + r + 1, nelx)):
                for jj in range(max(j - r, 0), min(j + r + 1, nely)):
                    e2 = ii * nely + jj
                    w = rmin - np.sqrt((i - ii) ** 2 + (j - jj) ** 2)
                    if w > 0:
                        iH.append(e1)
                        jH.append(e2)
                        sH.append(w)
    H = coo_matrix((sH, (iH, jH)), shape=(nele, nele)).tocsr()
    Hs = np.asarray(H.sum(axis=1)).flatten()
    return H, Hs


def optimize(nelx=120, nely=40, volfrac=0.5, penal=3.0, rmin=2.4, maxiter=120):
    print(f"MBB beam SIMP topology optimization")
    print(f"  mesh = {nelx} x {nely} ({nelx*nely} elements), "
          f"volfrac = {volfrac}, penal = {penal}, rmin = {rmin}")
    t0 = time.time()

    KE = lk()
    nele = nelx * nely
    ndof = 2 * (nelx + 1) * (nely + 1)

    # Element -> global dof connectivity
    nodenrs = np.arange((nelx + 1) * (nely + 1)).reshape(nelx + 1, nely + 1)
    edofMat = np.zeros((nele, 8), dtype=int)
    for i in range(nelx):
        for j in range(nely):
            e = i * nely + j
            n1 = nodenrs[i, j]      # top-left node of element
            n2 = nodenrs[i + 1, j]  # top-right node
            edofMat[e] = np.array([
                2 * n1, 2 * n1 + 1,
                2 * n2, 2 * n2 + 1,
                2 * n2 + 2, 2 * n2 + 3,
                2 * n1 + 2, 2 * n1 + 3,
            ])
    iK = np.kron(edofMat, np.ones((8, 1), dtype=int)).flatten()
    jK = np.kron(edofMat, np.ones((1, 8), dtype=int)).flatten()

    # Loads and supports (MBB beam: vertical load at top-left corner,
    # symmetry roller on left edge, single roller at bottom-right corner).
    F = np.zeros(ndof)
    F[2 * nodenrs[0, 0] + 1] = -1.0  # downward unit load at top-left
    fixeddofs = np.union1d(
        2 * nodenrs[0, :],                 # x of all left-edge nodes (symmetry)
        np.array([2 * nodenrs[nelx, nely] + 1]),  # y of bottom-right node
    )
    alldofs = np.arange(ndof)
    freedofs = np.setdiff1d(alldofs, fixeddofs)

    H, Hs = build_filter(nelx, nely, rmin)

    x = volfrac * np.ones(nele)
    xphys = x.copy()
    loop = 0
    change = 1.0

    while change > 0.01 and loop < maxiter:
        loop += 1

        # --- FE analysis ---
        sK = ((KE.flatten()[:, None] *
               (1e-9 + xphys ** penal * (1.0 - 1e-9))).T).flatten()
        K = coo_matrix((sK, (iK, jK)), shape=(ndof, ndof)).tocsc()
        K = (K + K.T) / 2.0
        U = np.zeros(ndof)
        U[freedofs] = spsolve(K[freedofs, :][:, freedofs], F[freedofs])

        # --- compliance and sensitivities ---
        ce = (np.dot(U[edofMat], KE) * U[edofMat]).sum(axis=1)
        c = float((((1e-9 + xphys ** penal * (1.0 - 1e-9))) * ce).sum())
        dc = -penal * (1.0 - 1e-9) * xphys ** (penal - 1) * ce
        dv = np.ones(nele)

        # --- density filtering of sensitivities ---
        dc = np.asarray(H.dot(dc / Hs)).flatten()
        dv = np.asarray(H.dot(dv / Hs)).flatten()

        # --- Optimality Criteria update ---
        l1, l2, move = 0.0, 1e9, 0.2
        while (l2 - l1) / (0.5 * (l1 + l2)) > 1e-3:
            lmid = 0.5 * (l1 + l2)
            xnew = np.maximum(0.0, np.maximum(
                x - move, np.minimum(1.0, np.minimum(
                    x + move, x * np.sqrt(-dc / dv / lmid)))))
            xphys = np.asarray(H.dot(xnew) / Hs).flatten()
            if xphys.mean() > volfrac:
                l1 = lmid
            else:
                l2 = lmid

        change = float(np.max(np.abs(xnew - x)))
        x = xnew

        if loop % 5 == 0 or loop == 1:
            print(f"  it {loop:3d}  c = {c:10.4f}  vol = {xphys.mean():.3f}  "
                  f"change = {change:.4f}")

    elapsed = time.time() - t0
    print(f"\nConverged after {loop} iterations in {elapsed:.1f}s")
    print(f"Final compliance = {c:.4f}")
    print(f"Final volume fraction = {xphys.mean():.4f} (target {volfrac})")
    return xphys.reshape(nelx, nely).T, c, loop


def main():
    xphys, c, loop = optimize()
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.imshow(-xphys, cmap="gray", interpolation="nearest",
              vmin=-1, vmax=0, aspect="equal")
    ax.set_title(f"MBB beam, c={c:.1f}, {loop} its")
    ax.axis("off")
    out = "/home/user/Design-Studio-Tools/experiments/03_topology_opt/topology.png"
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
