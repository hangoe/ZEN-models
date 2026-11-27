"""Write slurm_usage.json into each MGA run folder from a saved sacct dump.

Input: euler/slurm_usage/mga_sacct_<date>.txt, from (on Euler)
    sacct -u $USER -S 2026-08-01 --name=zen_run_mga --parsable2 \
      --format=JobID,JobName,State,Submit,Start,End,Elapsed,ElapsedRaw,TotalCPU,AllocCPUS,ReqMem,MaxRSS
The job -> run mapping is runs/mga_runs.csv (job_id = completed job,
other_jobs = failed/cancelled attempts). Existing slurm_usage.json files are kept; running jobs are skipped.

Usage:
    python prep/import_slurm_usage.py [euler/slurm_usage/mga_sacct_2026-11-27.txt]
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from thesis_figures.mga.run_tests import RUNS  # noqa: E402
from thesis_figures.paths import MGA_RESULTS_DIR as MGA_ROOT  # noqa: E402
from thesis_figures.paths import REPO_ROOT  # noqa: E402

DEFAULT_SACCT = REPO_ROOT / "euler" / "slurm_usage" / "mga_sacct_2026-11-27.txt"


def to_seconds(text: str) -> int:
    """SLURM [D-]HH:MM:SS or MM:SS.mmm -> seconds."""
    days, _, rest = text.rpartition("-")
    parts = [float(p) for p in rest.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0.0)
    h, m, s = parts
    return int(round((int(days) if days else 0) * 86400 + h * 3600 + m * 60 + s))


def to_kb(text: str) -> int | None:
    if not text:
        return None
    factor = {"K": 1, "M": 1024, "G": 1024 ** 2}.get(text[-1].upper())
    return int(float(text[:-1]) * factor) if factor else int(text)


def read_sacct(path: Path) -> dict[str, dict]:
    lines = [line for line in path.read_text().splitlines() if line.strip()]
    header = lines[0].split("|")
    jobs: dict[str, dict] = {}
    for line in lines[1:]:
        row = dict(zip(header, line.split("|")))
        job_id, _, step = row["JobID"].partition(".")
        entry = jobs.setdefault(job_id, {})
        if not step:
            entry["main"] = row
        elif step == "batch":
            entry["batch"] = row
    return jobs


def usage_entry(job_id: str, task_id: int, rec: dict) -> dict:
    main, batch = rec["main"], rec.get("batch", {})
    return {
        "job_id": job_id,
        "task_id": task_id,
        "elapsed": main["Elapsed"],
        "elapsed_seconds": int(main["ElapsedRaw"]),
        "total_cpu": main["TotalCPU"],
        "total_cpu_seconds": to_seconds(main["TotalCPU"]),
        "max_rss_kb": to_kb(batch.get("MaxRSS", "")),
        "alloc_cpus": int(main["AllocCPUS"]),
        "req_mem": main["ReqMem"],
        "state": main["State"].split()[0],
    }


def main() -> None:
    sacct = read_sacct(Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SACCT)
    for key, run in RUNS.items():
        if not run["jobs"] or not run["folder"]:
            continue
        run_dir = MGA_ROOT / run["folder"]
        target = run_dir / "slurm_usage.json"
        missing = [j for j in run["jobs"] if j not in sacct]
        if missing:
            print(f"  {key}: jobs {missing} not in sacct file, skipping")
            continue
        entries = [usage_entry(j, int(run["task_id"]), sacct[j]) for j in run["jobs"]]
        final = entries[-1]
        if final["state"] != "COMPLETED":
            print(f"  {key}: last job {final['job_id']} is {final['state']}, skipping")
            continue
        if not run_dir.exists():
            print(f"  {key}: run folder not on disk, skipping")
            continue
        if target.exists():
            print(f"  {key}: slurm_usage.json exists, kept")
            continue
        final["attempts"] = entries[:-1]
        target.write_text(json.dumps(final, indent=2) + "\n")
        print(f"  {key}: {final['job_id']} {final['elapsed']} {final['alloc_cpus']} CPU/{final['req_mem']} "
              f"MaxRSS {final['max_rss_kb'] / 1024 ** 2:.0f} GiB, {len(entries) - 1} earlier attempt(s)")


if __name__ == "__main__":
    main()
