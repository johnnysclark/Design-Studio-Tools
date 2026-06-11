#!/usr/bin/env bash
# Reproduce every ALIVE probe in the possibility map, headless on CPU.
# Setup (once):
#   uv venv experiments/.venv --python 3.11
#   uv pip install --python experiments/.venv/bin/python -r experiments/requirements.txt
# Then:  bash experiments/run_all.sh
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$HERE/.venv/bin/python"
export MPLBACKEND=Agg

run () {  # run <dir> <script>
  echo; echo "=============================================================="
  echo "RUN  $1/$2"; echo "=============================================================="
  ( cd "$HERE/$1" && "$PY" "$2" ) || echo "!! $1/$2 FAILED"
}

run 01_thrust_network funicular.py
run 02_smt_layout     layout_proof.py
run 03_topology_opt   topopt.py
run 04_wfc_plan       wfc_plan.py
run 05_acoustics      room_acoustics.py
run 06_cutting_stock  cutting_stock.py
run 07_isovist        isovist.py
run 08_differentiable diff_design.py
run 09_shape_grammar  shape_grammar.py
run 10_pattern_linter pattern_linter.py

# Claude Fable 5 design-participant probes. 15's z3 proof reproduces offline from the captured
# program; 14 and 16 make live Fable calls and degrade gracefully without ANTHROPIC_API_KEY.
run 14_fable_critic        fable_critic.py
run 15_fable_program_proof program_to_proof.py
run 16_serial_vision       serial_vision.py
run 17_closed_loop         closed_loop.py

echo; echo "All probes attempted. See each folder's README.md for recorded results."
