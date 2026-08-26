#!/bin/bash
###############################################################################
# check_mga_convergence.sh — convergence snapshot for the two currently
# running MGA batch sweeps (parameters_mga.csv rows, batch_bbo / minmax).
#
# Both rows use config_mga_batch_bbo.json (max_iterations: 5000, cap
# confirmed live in-log — NOT the 800 used by earlier sampling/bbo configs),
# so both logs report convergence the same way ("CI: [...] | target: 0.95").
# They differ in axes_config, which is why they're tracked as two distinct
# runs rather than two tasks of the same array job:
#   task 3 — row 3: batch_bbo minmax batch8, default axes
#            (config_mga_axes_capex.json, via run_model.py's
#            AXES_CONFIG_DEFAULT), 2050_1a_5a_interval_5ts
#   task 7 — row 7: batch_bbo minmax batch4, axes_config override
#            (config_mga_axes_capex_periods.json), 2020_7a_5a_interval_3ts
# Each was submitted as its own single-task sbatch (own JOBID), not as one
# array spanning both task ids — so each needs its own JOBID.
#
# Usage: ./check_mga_convergence.sh [JOBID_TASK3] [JOBID_TASK7]
#   Defaults to the job ids currently running as of 2026-08-25:
#     task 3 -> 11636632   task 7 -> 11644976
#   Pass overrides positionally if those runs finish and get resubmitted:
#     ./check_mga_convergence.sh 11636632 11644976
###############################################################################

JOBID_T3="${1:-11636632}"
JOBID_T7="${2:-11644976}"
MAXITER=5000

check_task () {
  local jobid="$1" task="$2" label="$3"
  echo "=== SLURM status: task $task (job $jobid) — $label ==="
  squeue -j "$jobid" 2>/dev/null || echo "(no running tasks under this job id)"
  sacct -j "$jobid" --format=JobID,Elapsed,State 2>/dev/null | grep -v "^$"
  echo

  echo "=== task $task: batch_bbo minmax ($label, cap $MAXITER) ==="
  f="zen_run_mga_${jobid}_${task}.out"
  if [[ -f "$f" ]]; then
    awk -v cap="$MAXITER" '
    {
      pat = "^Iteration [0-9]+/" cap
      if ($0 ~ pat) { iter=$2; sub("/" cap, "", iter) }
    }
    /CI: \[/ {
        match($0, /CI: \[([0-9.]+), ([0-9.]+)\] \| target: ([0-9.]+)/, m)
        print "iter="iter, "CI="m[1]","m[2], "target="m[3]
    }
    ' "$f" | tail -n 5
  else
    echo "(log not found: $f)"
  fi
  echo
}

check_task "$JOBID_T3" 3 "batch8, default axes (config_mga_axes_capex.json)"
check_task "$JOBID_T7" 7 "batch4, axes_config=config_mga_axes_capex_periods.json"
