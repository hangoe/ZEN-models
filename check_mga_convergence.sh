#!/bin/bash
###############################################################################
# check_mga_convergence.sh — convergence snapshot for task_id 7 of
# parameters_mga.csv (batch_bbo / per_axes / config_mga_axes_total.json,
# added 2026-09-18: "new run with 48 axes added for testing" +
# "adapt solver threads").
#
# Uses config_mga_batch_bbo.json (max_iterations: 5000, tolerance_prob: 0.95
# -- both left at their config defaults; task_id 7 only overrides
# normalisation=per_axes, tolerance_explore=0.1, epsilon=0.07,
# batch_size=n_workers=16, solver_threads=2), so the log reports convergence
# as "CI: [...] | target: 0.95".
#   task 7 — row 7: batch_bbo, per_axes normalisation, batch16,
#            axes_config=config_mga_axes_total.json (48 axes: node_capex_
#            cumulative + node_carbon_emissions_cumulative + node_capacity_
#            ratio), 2020_7a_5a_interval_1ts, tolerance_explore=0.1,
#            epsilon=0.07 -- no prior completed run, so there's no default
#            job id to fall back to; pass the one sbatch actually gave you.
#
# Usage: ./check_mga_convergence.sh JOBID_TASK7
###############################################################################

if [[ -z "${1:-}" ]]; then
  echo "Usage: $0 JOBID_TASK7  (job id sbatch printed when you submitted task_id 7)" >&2
  exit 1
fi
JOBID_T7="$1"
MAXITER=5000

check_task () {
  local jobid="$1" task="$2" label="$3"
  echo "=== SLURM status: task $task (job $jobid) — $label ==="
  squeue -j "$jobid" 2>/dev/null || echo "(no running tasks under this job id)"
  sacct -j "$jobid" --format=JobID,Elapsed,State 2>/dev/null | grep -v "^$"
  echo

  echo "=== task $task: batch_bbo per_axes ($label, cap $MAXITER) ==="
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

check_task "$JOBID_T7" 7 "batch16, per_axes, axes_config=config_mga_axes_total.json"
