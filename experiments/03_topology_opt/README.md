# 03 — Topology Optimization (SIMP / 88-line method)

**Claim:** Define supports + a load + a volume budget, and the material distributes
itself into an optimal load-bearing structure — no shape is drawn by hand. This is a
pure-Python/numpy/scipy SIMP optimizer solving the standard half-MBB beam.

## Run

```
/home/user/Design-Studio-Tools/experiments/.venv/bin/python \
  /home/user/Design-Studio-Tools/experiments/03_topology_opt/topopt.py
```

Outputs `topology.png` (black = material) in this folder.

## Actual output

```
MBB beam SIMP topology optimization
  mesh = 120 x 40 (4800 elements), volfrac = 0.5, penal = 3.0, rmin = 2.4
  it   1  c =  1026.8431  vol = 0.500  change = 0.2000
  it   5  c =   325.9695  vol = 0.500  change = 0.2000
  it  30  c =   215.4765  vol = 0.500  change = 0.1015
  it  60  c =   214.0931  vol = 0.500  change = 0.0853
  it  90  c =   213.5145  vol = 0.500  change = 0.1802
  it 120  c =   213.0102  vol = 0.500  change = 0.0198

Converged after 120 iterations in 12.6s
Final compliance = 213.0102
Final volume fraction = 0.5000 (target 0.5)
Saved .../topology.png
```

Compliance falls from **1026.8 → 213.0** (~5x stiffer) and stabilizes; the volume
fraction holds at exactly the **0.5** target throughout. The result is the textbook
half-MBB structure: thick top compression chord, bottom tension chord, and a fan of
diagonal web members.

## Method

Classic SIMP (Andreassen et al. 2011, "Efficient topology optimization in MATLAB using
88 lines of code"): bilinear-quad FE solve, SIMP penalization (p=3), a linear-hat
**density filter** (rmin=2.4) to suppress checkerboarding, and the **Optimality
Criteria** bisection update. Written from scratch, no topology package installed.

## Honest limitations

- The stop criterion is a fixed 120-iteration cap; `change` is still ~0.02 and slowly
  oscillating, so it has effectively converged but is not driven to a tight tolerance.
- Coarse 120x40 mesh — fine members are a few pixels wide and the density field is
  grey-fuzzy at boundaries (no projection/thresholding to a crisp 0/1 design).
- Sensitivity-filtered only; no robust/Heaviside projection, so this is the basic
  (not manufacturing-cleaned) SIMP result. Single load case, linear-elastic, 2D.
