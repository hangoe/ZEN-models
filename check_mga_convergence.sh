#!/bin/bash
###############################################################################
# check_mga_convergence.sh — convergence snapshot for the historical MGA
# batch sweep still tracked from parameters_mga.csv (batch_bbo / minmax).
#
# Uses config_mga_batch_bbo.json (max_iterations: 5000, cap confirmed live
# in-log — NOT the 800 used by earlier sampling/bbo configs), so the log
# reports convergence as "CI: [...] | target: 0.95".
#   task 7 — row 7: batch_bbo minmax batch4, axes_config override
#            (config_mga_axes_capex_periods.json), 2020_7a_5a_interval_3ts
#            (historical — left untouched by the 2026-08-27 cum_capex
#            cleanup; row 3, formerly also tracked here, was removed from
#            parameters_mga.csv in that cleanup)
#
# Usage: ./check_mga_convergence.sh [JOBID_TASK7]
#   Defaults to the job id running as of 2026-08-25: task 7 -> 11644976
#   Pass an override positionally if that run finishes and gets resubmitted:
#     ./check_mga_convergence.sh 11644976
###############################################################################

JOBID_T7="${1:-11644976}"
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

check_task "$JOBID_T7" 7 "batch4, axes_config=config_mga_axes_capex_periods.json"
