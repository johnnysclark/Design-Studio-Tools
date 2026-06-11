# experiments/ — possibility-map probes

Throwaway research probes backing [`../POSSIBILITIES.md`](../POSSIBILITIES.md). Each
folder is a self-contained ~30–250 line experiment that runs **headless on CPU** and
records what actually happened in its own `README.md`. These are *not* packages and do
**not** join the `uv` workspace — they're evidence, not product.

## Setup
```bash
uv venv experiments/.venv --python 3.11
uv pip install --python experiments/.venv/bin/python -r experiments/requirements.txt
bash experiments/run_all.sh        # run everything, or run one folder's script
```

## Index
| Folder | Thread | Verdict |
|--------|--------|---------|
| `01_thrust_network` | Funicular form-finding → compression vault (`compas_fd`) | ALIVE |
| `02_smt_layout` | SMT layout that *proves* a brief impossible (`z3`) | ALIVE |
| `03_topology_opt` | Topology optimization, SIMP (numpy/scipy) | ALIVE |
| `04_wfc_plan` | Wave Function Collapse plan fields (self-built) | ALIVE |
| `05_acoustics` | Room acoustics + auralization (`pyroomacoustics`) | ALIVE |
| `06_cutting_stock` | Cutting-stock + sheet nesting (`ortools`/`rectpack`) | ALIVE |
| `07_isovist` | Isovist + visibility field (self-built on `shapely`) | ALIVE |
| `08_differentiable` | Gradient-descend a roof to a brief (`jax`) | ALIVE |
| `09_shape_grammar` | Shape-grammar interpreter (self-built) | ALIVE |
| `10_pattern_linter` | Alexander's patterns as a running critic (offline) | ALIVE |

`.3dm` outputs open directly in Rhino; `.png`/`.wav`/`.svg` are inline evidence.
