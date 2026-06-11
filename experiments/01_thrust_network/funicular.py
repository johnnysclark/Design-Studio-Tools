"""Force-density form-finding: a hanging net inverts into a compression vault.

Thread: Form & structure / thrust-network & graphic statics (Kind A: validate a live lib).
Library: compas_fd 0.5.4 (BlockResearchGroup / ETH), pure-Python + numpy, headless.

The force-density method (Schek 1974) solves the equilibrium shape of a pin-jointed
net in one linear solve -- no iteration. A net hanging under gravity finds a funicular
(tension-only) surface; flip it in z and you have a funicular *compression* surface --
the logic behind masonry vaults and RhinoVAULT. This is the move that used to require a
plugin; here it's ~30 lines headless, and we write a .3dm you can open in Rhino.
"""
from pathlib import Path
import numpy as np
from compas_fd.solvers import fd_numpy
import rhino3dm

N = 11            # grid is N x N vertices
SPAN = 10.0       # metres
Q = 1.0           # force density (uniform) -- higher = flatter
LOAD = -1.0       # downward load per free vertex (z)

# --- build a square grid of vertices + edges -------------------------------
xs = np.linspace(0, SPAN, N)
ys = np.linspace(0, SPAN, N)
idx = lambda i, j: i * N + j
vertices = [[x, y, 0.0] for x in xs for y in ys]

edges = []
for i in range(N):
    for j in range(N):
        if i < N - 1:
            edges.append((idx(i, j), idx(i + 1, j)))
        if j < N - 1:
            edges.append((idx(i, j), idx(i, j + 1)))

# fix the four corners as supports; everything else is free to find form
fixed = [idx(0, 0), idx(0, N - 1), idx(N - 1, 0), idx(N - 1, N - 1)]
free = [k for k in range(N * N) if k not in fixed]

loads = [[0.0, 0.0, 0.0] for _ in range(N * N)]
for k in free:
    loads[k] = [0.0, 0.0, LOAD]

forcedensities = [Q] * len(edges)

# --- one linear solve -------------------------------------------------------
result = fd_numpy(
    vertices=vertices, fixed=fixed, edges=edges,
    forcedensities=forcedensities, loads=loads,
)
hang = np.asarray(result.vertices)
sag = float(hang[:, 2].min())
print(f"Solved {N*N} vertices, {len(edges)} edges in one linear solve.")
print(f"Funicular sag (lowest point z): {sag:.3f} m")

# invert -> compression vault rising from the four supports
vault = hang.copy()
vault[:, 2] = -vault[:, 2]
rise = float(vault[:, 2].max())
print(f"Inverted compression vault rise (highest point z): {rise:.3f} m")

# --- write a .3dm with both the funicular net and the vault mesh -----------
model = rhino3dm.File3dm()

def add_mesh(coords, name):
    m = rhino3dm.Mesh()
    for x, y, z in coords:
        m.Vertices.Add(float(x), float(y), float(z))
    for i in range(N - 1):
        for j in range(N - 1):
            m.Faces.AddFace(idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1))
    m.Normals.ComputeNormals()
    a = model.Objects.AddMesh(m)
    obj = model.Objects.FindId(a)
    obj.Attributes.Name = name

add_mesh(hang, "funicular_hanging_net")
add_mesh(vault, "compression_vault")
out = Path(__file__).parent / "vault.3dm"
model.Write(str(out), 8)
print(f"Wrote {out}")
