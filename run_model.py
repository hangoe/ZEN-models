"""
ZEN-models run, adapted to run as a SLURM array sweep.

CHANGES:
  * `my_dataset`, `my_comment` and every `system_overrides` value now come from
    ONE ROW of `parameters.csv`, selected by --task_id. So each row is a complete
    run configuration and a SLURM array can run them all in parallel.
  * Instead of patching the dataset's shared system.json in place (which races
    when several array tasks run at once, and can leave the file corrupted if a
    job is killed), each task STAGES A PRIVATE COPY of the dataset, patches that
    copy, and runs on it. Your pristine dataset (in ZEN-creator/outputs or
    data/) is never modified.
  * On Euler, the staged dataset and the results go to $SCRATCH.

Run one row by hand (local test):   python run_model.py --task_id 0 --run_on local
On Euler it is launched by submit_euler.sh via the SLURM array.
"""

import argparse
import json
import os
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
from zen_garden import run, Results  # noqa: F401  (Results kept for post-processing)

# --- Fixed locations (same layout as your original script) ----------------------
REPO_DIR = Path(__file__).parent                                  # .../ZEN-models
DATA_DIR_CONFIG = REPO_DIR / "data"                               # config.json + local outputs

# Places `my_dataset` is looked up, in order. Most datasets are pristine,
# version-numbered copies living in ZEN-creator/outputs; a few one-off/local
# datasets (e.g. data/Crystal_Ball) live directly in this repo instead.
DATASET_SEARCH_DIRS = [
    REPO_DIR.parent / "ZEN-creator" / "outputs",
    REPO_DIR / "data",
]

# Columns in parameters.csv that are NOT system.json overrides.
# Everything else in a row is applied as a system_overrides key.
META_COLUMNS = {"my_dataset", "my_comment"}


def resolve_dataset_dir(name: str) -> Path:
    for base in DATASET_SEARCH_DIRS:
        candidate = base / name
        if candidate.exists():
            return candidate
    searched = ", ".join(str(base) for base in DATASET_SEARCH_DIRS)
    raise SystemExit(f"Dataset '{name}' not found in any of: {searched}")


def to_native(v):
    """Convert a CSV/pandas cell to a clean Python bool/int/float/str for JSON."""
    if isinstance(v, str):
        s = v.strip()
        if s.lower() in ("true", "false"):
            return s.lower() == "true"
        try:
            return int(s)
        except ValueError:
            try:
                return float(s)
            except ValueError:
                return s
    if isinstance(v, (bool, np.bool_)):
        return bool(v)
    if isinstance(v, np.integer):
        return int(v)
    if isinstance(v, np.floating):
        f = float(v)
        return int(f) if f.is_integer() else f
    return v


def working_root(run_on: str) -> Path:
    """Where staged datasets + results live. Scratch on Euler, local folder otherwise."""
    if run_on == "euler":
        return Path(os.environ.get("SCRATCH", Path.home() / "scratch")) / "zen_runs"
    return REPO_DIR / "_runs"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one row of the ZEN-garden sweep.")
    parser.add_argument("--task_id", type=int, required=True,
                        help="Row index (task_id) in parameters.csv to run.")
    parser.add_argument("--run_on", type=str, default="euler",
                        choices=["local", "euler"],
                        help="Controls where staged data + results are written.")
    args = parser.parse_args()

    # --- 1. Read this task's configuration from the CSV --------------------------
    params_path = REPO_DIR / "parameters.csv"
    table = pd.read_csv(params_path, index_col="task_id")
    if args.task_id not in table.index:
        raise SystemExit(f"task_id {args.task_id} not in {params_path} "
                         f"(available: {list(table.index)})")
    row = table.loc[args.task_id]

    my_dataset = str(row["my_dataset"])
    my_comment = str(row["my_comment"])
    system_overrides = {col: to_native(row[col])
                        for col in table.columns if col not in META_COLUMNS}

    print(f"[run_model] task_id={args.task_id}  dataset={my_dataset}  comment={my_comment}")
    print(f"[run_model] system_overrides={system_overrides}")

    # --- 2. Stage a PRIVATE copy of the dataset (safe for parallel array tasks) --
    work = working_root(args.run_on) / f"task_{args.task_id}"
    staged_dataset = work / my_dataset
    if staged_dataset.exists():
        shutil.rmtree(staged_dataset)
    staged_dataset.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(resolve_dataset_dir(my_dataset), staged_dataset)

    # --- 3. Apply the system.json overrides to the COPY --------------------------
    system_json_path = staged_dataset / "system.json"
    with open(system_json_path) as f:
        system = json.load(f)
    system.update(system_overrides)
    with open(system_json_path, "w") as f:
        json.dump(system, f, indent=2)

    # --- 4. Decide the output folder (scratch on Euler) --------------------------
    if args.run_on == "euler":
        out_dir = working_root(args.run_on) / "outputs" / f"{my_dataset}_{my_comment}"
    else:
        out_dir = DATA_DIR_CONFIG / "outputs" / f"{my_dataset}_{my_comment}"
    out_dir.parent.mkdir(parents=True, exist_ok=True)

    # --- 5. Run the model --------------------------------------------------------
    run(
        config=str(DATA_DIR_CONFIG / "config.json"),
        dataset=str(staged_dataset),
        folder_output=str(out_dir),
    )
    print(f"[run_model] done task_id={args.task_id}: results in {out_dir}")


if __name__ == "__main__":
    main()
