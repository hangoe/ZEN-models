"""Summarise Gurobi barrier runs from SLURM logs (zen_run_<JOBID>_<task>.out) as one table.

Usage (on Euler, in ~/ZEN-models):
    python scripts/solver_tests/parse_logs.py zen_run_<JOBID>_*.out
    python scripts/solver_tests/parse_logs.py --csv summary.csv zen_run_*.out

Columns:
  task       task_id (from the "[run_model] task_id=" line, else from the file name)
  comment    my_comment of the row
  status     OPTIMAL / SUBOPT / NUMERIC / TIMELIMIT / RUNNING? (no end line found yet)
  obj        final objective (or last primal objective if the run did not finish)
  it         barrier iterations
  it_1e-4    first iteration with relative primal-dual gap < 1e-4: a big gap between
             it_1e-4 and it means a long tail (degeneracy), a big it_1e-4 means slow
             progress overall
  solve_s    barrier time in seconds (last iteration time if not finished)
  s_per_it   solve_s / it
  rows/cols  after presolve
  dense      dense columns
  factor_nz  nonzeros in the Cholesky factor
  factor_ops floating point ops per iteration (cost of one iteration; BarOrder changes this)
  order_s    ordering time in seconds
  opts       non-default parameters set via "Set parameter" (except Username/Threads)
"""
import argparse
import csv
import re
import sys
from pathlib import Path

RE = {
    "task": re.compile(r"\[run_model\] task_id=(\d+)\s+dataset=(\S+)\s+comment=(\S+)"),
    "presolved": re.compile(r"Presolved: (\d+) rows, (\d+) columns, (\d+) nonzeros"),
    "order": re.compile(r"Ordering time: ([\d.]+)s"),
    "dense": re.compile(r"Dense cols\s*:\s*(\d+)"),
    "fnz": re.compile(r"Factor NZ\s*:\s*([\d.e+]+)"),
    "fops": re.compile(r"Factor Ops\s*:\s*([\d.e+]+)"),
    "iter": re.compile(r"^\s*(\d+)\s+([-+\d.e]+)\s+([-+\d.e]+)\s+[\d.e+-]+\s+[\d.e+-]+\s+[\d.e+-]+\s+(\d+)s\s*$"),
    "solved": re.compile(r"Barrier (?:solved model|performed) (?:in )?(\d+) iterations (?:in )?(?:and )?([\d.]+) seconds"),
    "optimal": re.compile(r"Optimal objective\s+([-+\d.e]+)"),
    "subopt": re.compile(r"Sub-optimal termination - objective\s+([-+\d.e]+)"),
    "param": re.compile(r"Set parameter (\w+) to value (\S+)"),
}
SKIP_PARAMS = {"Username", "Threads", "LogFile", "TimeLimit"}


def parse(path: Path) -> dict:
    r = {"file": path.name, "task": "", "comment": "", "status": "RUNNING?", "obj": "", "it": "",
         "it_1e-4": "", "solve_s": "", "s_per_it": "", "rows": "", "cols": "", "dense": "",
         "factor_nz": "", "factor_ops": "", "order_s": "", "opts": ""}
    m = re.search(r"_(\d+)\.(out|log)$", path.name)
    if m:
        r["task"] = m.group(1)
    params, last_iter = {}, None
    with open(path, errors="replace") as f:
        for line in f:
            if (m := RE["task"].search(line)):
                r["task"], r["comment"] = m.group(1), m.group(3)
            elif (m := RE["param"].search(line)):
                if m.group(1) not in SKIP_PARAMS:
                    params[m.group(1)] = m.group(2)
            elif (m := RE["presolved"].search(line)):
                r["rows"], r["cols"] = m.group(1), m.group(2)
            elif (m := RE["order"].search(line)):
                r["order_s"] = m.group(1)
            elif (m := RE["dense"].search(line)):
                r["dense"] = m.group(1)
            elif (m := RE["fnz"].search(line)):
                r["factor_nz"] = m.group(1)
            elif (m := RE["fops"].search(line)):
                r["factor_ops"] = m.group(1)
            elif (m := RE["iter"].match(line)):
                it, p, d, t = int(m.group(1)), float(m.group(2)), float(m.group(3)), int(m.group(4))
                last_iter = (it, p, t)
                if r["it_1e-4"] == "" and abs(p - d) <= 1e-4 * max(abs(p), 1.0):
                    r["it_1e-4"] = it
            elif (m := RE["solved"].search(line)):
                r["it"], r["solve_s"] = int(m.group(1)), float(m.group(2))
            elif (m := RE["optimal"].search(line)):
                r["status"], r["obj"] = "OPTIMAL", float(m.group(1))
            elif (m := RE["subopt"].search(line)):
                r["status"], r["obj"] = "SUBOPT", float(m.group(1))
            elif "Numerical trouble" in line:
                r["status"] = "NUMERIC"
            elif "Time limit reached" in line or "DUE TO TIME LIMIT" in line:
                r["status"] = "TIMELIMIT"
    if r["it"] == "" and last_iter:
        r["it"], r["obj"], r["solve_s"] = last_iter[0], last_iter[1], float(last_iter[2])
    if r["it"]:
        r["s_per_it"] = round(float(r["solve_s"]) / max(int(r["it"]), 1), 1)
    r["opts"] = ";".join(f"{k}={v}" for k, v in params.items())
    return r


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("logs", nargs="+", type=Path)
    ap.add_argument("--csv", type=Path, help="also write the table to this CSV")
    args = ap.parse_args()
    rows = sorted((parse(p) for p in args.logs), key=lambda r: (int(r["task"]) if str(r["task"]).isdigit() else 1e9))
    cols = ["task", "comment", "status", "obj", "it", "it_1e-4", "solve_s", "s_per_it", "rows", "cols",
            "dense", "factor_nz", "factor_ops", "order_s", "opts", "file"]
    fmt = lambda v: f"{v:.6e}" if isinstance(v, float) and abs(v) > 1e5 else str(v)
    table = [[fmt(r[c]) for c in cols] for r in rows]
    widths = [max(len(c), *(len(t[i]) for t in table)) for i, c in enumerate(cols)]
    print("  ".join(c.ljust(w) for c, w in zip(cols, widths)))
    for t in table:
        print("  ".join(v.ljust(w) for v, w in zip(t, widths)))
    if args.csv:
        with open(args.csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)


if __name__ == "__main__":
    sys.exit(main())
