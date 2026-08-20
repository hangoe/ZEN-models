#!/bin/bash
###############################################################################
# check_mga_convergence.sh — quick convergence snapshot for all tasks in a
# parameters_mga.csv sweep (sampling / bbo / batch_bbo, minmax normalisation).
#
# Usage: ./check_mga_convergence.sh <JOBID>
#   e.g. ./check_mga_convergence.sh 11274066
###############################################################################

JOBID="${1:?Usage: $0 <SLURM_ARRAY_JOB_ID>}"

echo "=== SLURM status ==="
squeue -j "$JOBID" 2>/dev/null || echo "(no running tasks under this job id)"
sacct -j "$JOBID" --format=JobID,Elapsed,State 2>/dev/null | grep -v "^$"
echo

# task_id 0: sampling, minmax -> Iteration X/500
echo "=== task 0: sampling minmax (cap 500) ==="
f="zen_run_mga_${JOBID}_0.out"
if [[ -f "$f" ]]; then
  awk '
  /^Iteration [0-9]+\/500/ { iter=$2; sub("/500","",iter) }
  /^Fraction of directions with gap <= 0.1:/ {
      match($0, /gap <= 0.1: ([0-9.]+), 95.0% CI \[([0-9.]+), ([0-9.]+)\]/, m)
      print "iter="iter, "frac="m[1], "CI="m[2]","m[3]
  }
  ' "$f" | tail -n 5
else
  echo "(log not found: $f)"
fi
echo

# task_id 1: bbo, minmax -> Iteration X/800
echo "=== task 1: bbo minmax (cap 800) ==="
f="zen_run_mga_${JOBID}_1.out"
if [[ -f "$f" ]]; then
  awk '
  /^Iteration [0-9]+\/800/ { iter=$2; sub("/800","",iter) }
  /^Fraction of directions with gap <= 0.1:/ {
      match($0, /gap <= 0.1: ([0-9.]+), 95.0% CI \[([0-9.]+), ([0-9.]+)\]/, m)
      print "iter="iter, "frac="m[1], "CI="m[2]","m[3]
  }
  ' "$f" | tail -n 5
else
  echo "(log not found: $f)"
fi
echo

# task_ids 2,3,4: batch_bbo, minmax, batch4/8/16 -> Iteration X/800 + CI:/target:
for t in 2 3 4; do
  case $t in
    2) label="batch4" ;;
    3) label="batch8" ;;
    4) label="batch16" ;;
  esac
  echo "=== task $t: batch_bbo minmax ($label, cap 800) ==="
  f="zen_run_mga_${JOBID}_${t}.out"
  if [[ -f "$f" ]]; then
    awk '
    /^Iteration [0-9]+\/800/ { iter=$2; sub("/800","",iter) }
    /CI: \[/ {
        match($0, /CI: \[([0-9.]+), ([0-9.]+)\] \| target: ([0-9.]+)/, m)
        print "iter="iter, "CI="m[1]","m[2], "target="m[3]
    }
    ' "$f" | tail -n 5
  else
    echo "(log not found: $f)"
  fi
  echo
done