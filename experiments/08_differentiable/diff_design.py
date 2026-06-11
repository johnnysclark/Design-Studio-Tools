"""Differentiable design: gradient-descend a roof to meet a brief.

Thread: New epistemologies / differentiable design (Kind B for architecture:
the autodiff machinery exists, architecture-specific use barely does).
Library: jax 0.10 (CPU), pure autodiff. Headless.

The epistemology: instead of *searching* a parameter space or *solving* a linear
system, you write the brief as a differentiable loss and let the gradient pull the
geometry into shape. Here the brief is a fabric canopy on a fixed rectangular frame:
  - MINIMIZE membrane area (material + a taut, Frei-Otto-like minimal surface), and
  - CLEAR three functional volumes underneath (a stage, an entry, a mast) -- the
    surface must rise to at least a required height over each.
We descend the interior height field with Adam. The mast/clearances are the program;
the minimal surface is what physics + the program agree on. Output: initial vs solved
.3dm canopies you can open in Rhino, plus a loss curve.
"""
from pathlib import Path
import jax, jax.numpy as jnp
from jax import grad, jit
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import rhino3dm

N = 21
SPAN = 12.0
xs = jnp.linspace(0, SPAN, N)
ys = jnp.linspace(0, SPAN, N)
gx, gy = jnp.meshgrid(xs, ys, indexing="ij")

# fixed boundary frame at z=0; interior heights are the free design variables
boundary = jnp.zeros((N, N)).at[1:-1, 1:-1].set(0.0)
free_mask = jnp.zeros((N, N), bool).at[1:-1, 1:-1].set(True)

# program: (x, y, required clearance height) -- the canopy must rise to at least this
clearances = [(3.0, 3.0, 4.5),   # entry
              (9.0, 4.0, 3.0),   # side door
              (6.0, 9.0, 6.0)]   # central mast / stage
def nearest(x, y):
    i = int(round(x / SPAN * (N - 1))); j = int(round(y / SPAN * (N - 1)))
    return i, j
clear_idx = [nearest(x, y) for x, y, _ in clearances]
clear_h = jnp.array([h for *_, h in clearances])

cell = SPAN / (N - 1)

def surface(zfree):
    z = jnp.zeros((N, N))
    z = z.at[free_mask].set(zfree)
    return z

def membrane_area(z):
    # sum of triangle areas over the meshed grid (differentiable)
    p = jnp.stack([gx, gy, z], axis=-1)
    a = p[:-1, :-1]; b = p[1:, :-1]; c = p[1:, 1:]; d = p[:-1, 1:]
    def tri(u, v, w):
        return 0.5 * jnp.linalg.norm(jnp.cross(v - u, w - u), axis=-1)
    return (tri(a, b, c) + tri(a, c, d)).sum()

def loss(zfree):
    z = surface(zfree)
    area = membrane_area(z)
    heights = jnp.array([z[i, j] for i, j in clear_idx])
    clear_pen = jnp.sum(jax.nn.relu(clear_h - heights) ** 2)
    # mild smoothness so the membrane stays fabric-like, not spiky
    smooth = jnp.mean((z[1:, :] - z[:-1, :]) ** 2) + jnp.mean((z[:, 1:] - z[:, :-1]) ** 2)
    return area + 50.0 * clear_pen + 2.0 * smooth, (area, clear_pen)

grad_loss = jit(grad(lambda zf: loss(zf)[0]))
val_loss = jit(loss)

n_free = int(free_mask.sum())
z = jnp.full((n_free,), 0.5)            # start: nearly flat sheet
m = jnp.zeros_like(z); v = jnp.zeros_like(z)
lr, b1, b2, eps = 0.05, 0.9, 0.999, 1e-8

z_init = np.array(surface(z))
history = []
for t in range(1, 601):
    g = grad_loss(z)
    m = b1 * m + (1 - b1) * g
    v = b2 * v + (1 - b2) * g * g
    mh = m / (1 - b1 ** t); vh = v / (1 - b2 ** t)
    z = z - lr * mh / (jnp.sqrt(vh) + eps)
    if t % 50 == 0 or t == 1:
        L, (area, pen) = val_loss(z)
        history.append((t, float(L), float(area), float(pen)))
        print(f"step {t:4d}  loss={float(L):8.3f}  area={float(area):7.3f} m^2  clearance_violation={float(pen):.4f}")

z_final = np.array(surface(z))
flat_area = SPAN * SPAN
print(f"\nFlat sheet area would be {flat_area:.1f} m^2; solved canopy area "
      f"{history[-1][2]:.1f} m^2 while meeting all 3 clearances "
      f"(final violation {history[-1][3]:.4f}).")
ok = all(z_final[i, j] >= h - 0.05 for (i, j), h in zip(clear_idx, [c[2] for c in clearances]))
print("All clearance heights met (independent check):", ok)
for (x, y, h), (i, j) in zip(clearances, clear_idx):
    print(f"  required {h:.1f} m at ({x},{y}) -> achieved {z_final[i,j]:.2f} m")

# --- loss curve + .3dm of initial and solved canopy ------------------------
out = Path(__file__).parent
ts, Ls, As, Ps = zip(*history)
fig, ax1 = plt.subplots(figsize=(7, 4))
ax1.plot(ts, As, "b-o", label="membrane area (m^2)")
ax1.set_xlabel("gradient step"); ax1.set_ylabel("area (m^2)", color="b")
ax2 = ax1.twinx(); ax2.plot(ts, Ps, "r-s", label="clearance violation")
ax2.set_ylabel("clearance violation", color="r")
ax1.set_title("Differentiable canopy: membrane tents up to meet clearances,\nfinding the minimal taut area that satisfies the program")
fig.tight_layout(); fig.savefig(out / "loss_curve.png", dpi=110)

model = rhino3dm.File3dm()
def add(zz, name):
    mesh = rhino3dm.Mesh()
    for i in range(N):
        for j in range(N):
            mesh.Vertices.Add(float(gx[i, j]), float(gy[i, j]), float(zz[i, j]))
    for i in range(N - 1):
        for j in range(N - 1):
            mesh.Faces.AddFace(i * N + j, (i + 1) * N + j, (i + 1) * N + j + 1, i * N + j + 1)
    mesh.Normals.ComputeNormals()
    gid = model.Objects.AddMesh(mesh)
    model.Objects.FindId(gid).Attributes.Name = name
add(z_init, "canopy_initial_flat")
add(z_final, "canopy_solved")
model.Write(str(out / "canopy.3dm"), 8)
print(f"Wrote {out/'canopy.3dm'} and {out/'loss_curve.png'}")
