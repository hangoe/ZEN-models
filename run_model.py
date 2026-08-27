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
  * `--params` selects which CSV to sweep over (default parameters.csv). Each
    row may also set a `config` column (e.g. config_mga_weights.json) to pick
    which data/*.json config to run with; rows without it use config.json, so
    the original parameters.csv/submit_euler.sh path is unaffected.
  * Rows may also set a `normalisation` column (e.g. "relative", "units" or
    "minmax") that overwrites plugins.mga.normalisation in a private staged
    copy of the chosen config -- the shared data/*.json config is never
    touched, so one config_mga_bbo.json / config_mga_sampling.json covers
    all normalisation modes instead of needing a config file per mode.
  * Rows may also set `batch_size` / `n_workers` columns that overwrite the
    matching keys under plugins.mga.batch (batch mode only) in the same
    private staged copy, the same way `normalisation` does.
  * The `axes` block for every MGA mode except `weights` is no longer
    duplicated per config file -- it's merged in from data/config_mga_axes_capex.json
    (the default) into the private staged copy, so all five
    config_mga_{bbo,sampling,oracle,batch_bbo,batch_sampling}.json files
    share one axes definition. A row may set an `axes_config` column (e.g.
    config_mga_axes_capex_cum.json) to merge in a different axes file
    instead, without touching the shared default.
  * Any system_overrides key a row's CSV doesn't set falls back to
    DEFAULT_SYSTEM_OVERRIDES, so a sweep whose rows all share the same
    dataset-processing setup (e.g. parameters_mga.csv) doesn't need to repeat
    those columns in every row -- a row can still override any of them by
    adding that column, the way parameters.csv already does explicitly.

Run one row by hand (local test):   python run_model.py --task_id 0 --run_on local
On Euler it is launched by submit_euler.sh (or submit_euler_mga.sh) via the
SLURM array.
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
META_COLUMNS = {"my_dataset", "my_comment", "config", "normalisation", "batch_size", "n_workers", "axes_config"}

# Fallback system.json overrides, used for any of these keys a CSV row
# doesn't set as its own column. Lets parameters_mga.csv's rows share one
# dataset-processing setup without repeating it in every row -- a row can
# still override any of these by adding that column back, the same way
# parameters.csv (which sets all of them explicitly, to different values)
# already does.
DEFAULT_SYSTEM_OVERRIDES = {
    "conduct_time_series_aggregation": True,
    "aggregated_time_steps_per_year": 5,
    "reference_year": 2050,
    "optimized_years": 1,
    "interval_between_years": 5,
    "use_rolling_horizon": False,
}

# config.json used when a row/CSV has no "config" column (or leaves it
# blank) -- keeps the original non-MGA parameters.csv working unchanged.
DEFAULT_CONFIG = "config.json"

# Default axes definition merged into every MGA config (see
# apply_axes_override) so the axes block isn't duplicated per config file.
# A row's own "axes_config" column (see main()) can point at a different
# axes file instead -- e.g. data/config_mga_axes_capex_cum.json for the
# node_capex_cumulative investigation. data/config_mga_axes_capacity.json
# holds the old technology-capacity axes (kept for reference/rollback -- not
# currently wired in here).
AXES_CONFIG_DEFAULT = DATA_DIR_CONFIG / "config_mga_axes_capex.json"


def apply_axes_override(config_json: dict, config_name: str, axes_config_path: Path = AXES_CONFIG_DEFAULT) -> None:
    """Merge in the axes definition from axes_config_path, in-place.

    No-op if plugins.mga is absent (plain config.json runs). Otherwise
    overwrites plugins.mga.axes with the contents of axes_config_path
    (defaults to data/config_mga_axes_capex.json), so the per-mode config
    files don't each carry their own copy of the axes. "weights" mode also
    needs an axes block now (weight keys reference axis names), so it is no
    longer skipped here.
    """
    mga_cfg = config_json.get("plugins", {}).get("mga")
    if mga_cfg is None:
        return
    with open(axes_config_path) as f:
        mga_cfg["axes"] = json.load(f)


def apply_normalisation_override(config_json: dict, config_name: str, normalisation: str) -> None:
    """Overwrite plugins.mga.normalisation in-place with the CSV row's value.

    Lets one config_mga_bbo.json / config_mga_sampling.json serve both
    normalisation modes -- the CSV row picks the mode, run_model.py bakes
    it into a private staged copy of the config (see main()), the shared
    data/*.json file is never touched.
    """
    mga_cfg = config_json.get("plugins", {}).get("mga")
    if mga_cfg is None:
        raise SystemExit(
            f"[run_model] row sets normalisation={normalisation!r} but "
            f"{config_name} has no plugins.mga block to apply it to."
        )
    mga_cfg["normalisation"] = normalisation


def apply_batch_overrides(config_json: dict, config_name: str, batch_size, n_workers) -> None:
    """Overwrite plugins.mga.batch.{batch_size,n_workers} in-place with the CSV row's values.

    Same private-staged-copy pattern as apply_normalisation_override(): lets
    one config_mga_batch_*.json be swept over different batch_size/n_workers
    values from parameters.csv without touching the shared data/*.json file.
    """
    if batch_size is None and n_workers is None:
        return
    batch_cfg = config_json.get("plugins", {}).get("mga", {}).get("batch")
    if batch_cfg is None:
        raise SystemExit(
            f"[run_model] row sets batch_size/n_workers but "
            f"{config_name} has no plugins.mga.batch block to apply them to."
        )
    if batch_size is not None:
        batch_cfg["batch_size"] = batch_size
    if n_workers is not None:
        batch_cfg["n_workers"] = n_workers


def validate_plugin_config(config_json: dict, config_name: str) -> None:
    """Fail fast on an invalid plugins.mga block, before staging/running.

    The plugin's own validate_config() only runs from an after_solve hook,
    i.e. after the (potentially long) baseline solve has already finished.
    Calling it here catches a bad "normalisation" value or an
    oracle+"units" mismatch before a SLURM array task burns its walltime.
    """
    mga_cfg = config_json.get("plugins", {}).get("mga")
    if mga_cfg is None:
        return
    from zen_garden_plugins.mga.plugin import validate_config
    try:
        validate_config(mga_cfg)
    except ValueError as e:
        raise SystemExit(f"[run_model] invalid plugins.mga config in {config_name}: {e}")


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
    parser.add_argument("--params", type=str, default="parameters.csv",
                        help="CSV file (relative to this repo) to read the sweep "
                             "from, e.g. parameters_mga.csv for an MGA sweep.")
    args = parser.parse_args()

    # --- 1. Read this task's configuration from the CSV --------------------------
    params_path = REPO_DIR / args.params
    table = pd.read_csv(params_path, index_col="task_id")
    if args.task_id not in table.index:
        raise SystemExit(f"task_id {args.task_id} not in {params_path} "
                         f"(available: {list(table.index)})")
    row = table.loc[args.task_id]

    my_dataset = str(row["my_dataset"])
    my_comment = str(row["my_comment"])
    config_name = DEFAULT_CONFIG
    if "config" in table.columns and pd.notna(row["config"]) and str(row["config"]).strip():
        config_name = str(row["config"]).strip()
    axes_config_path = AXES_CONFIG_DEFAULT
    if "axes_config" in table.columns and pd.notna(row["axes_config"]) and str(row["axes_config"]).strip():
        axes_config_path = DATA_DIR_CONFIG / str(row["axes_config"]).strip()
    normalisation = None
    if "normalisation" in table.columns and pd.notna(row["normalisation"]) and str(row["normalisation"]).strip():
        normalisation = str(row["normalisation"]).strip()
    batch_size = None
    if "batch_size" in table.columns and pd.notna(row["batch_size"]) and str(row["batch_size"]).strip():
        batch_size = to_native(row["batch_size"])
    n_workers = None
    if "n_workers" in table.columns and pd.notna(row["n_workers"]) and str(row["n_workers"]).strip():
        n_workers = to_native(row["n_workers"])
    system_overrides = {
        **DEFAULT_SYSTEM_OVERRIDES,
        **{col: to_native(row[col]) for col in table.columns if col not in META_COLUMNS},
    }

    print(f"[run_model] task_id={args.task_id}  dataset={my_dataset}  comment={my_comment}")
    print(f"[run_model] config={config_name}  axes_config={axes_config_path.name}  normalisation={normalisation}")
    print(f"[run_model] batch_size={batch_size}  n_workers={n_workers}")
    print(f"[run_model] system_overrides={system_overrides}")

    with open(DATA_DIR_CONFIG / config_name) as f:
        config_json = json.load(f)
    apply_axes_override(config_json, config_name, axes_config_path)
    if normalisation is not None:
        apply_normalisation_override(config_json, config_name, normalisation)
    apply_batch_overrides(config_json, config_name, batch_size, n_workers)
    validate_plugin_config(config_json, config_name)

    # --- 2. Stage a PRIVATE copy of the dataset (safe for parallel array tasks) --
    work = working_root(args.run_on) / f"task_{args.task_id}"
    staged_dataset = work / my_dataset
    if staged_dataset.exists():
        shutil.rmtree(staged_dataset)
    staged_dataset.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(resolve_dataset_dir(my_dataset), staged_dataset)

    # Write the (possibly normalisation-patched) config to the same private
    # per-task folder, so the shared data/*.json file is never touched and
    # concurrent array tasks never read/write it at once.
    staged_config_path = work / config_name
    with open(staged_config_path, "w") as f:
        json.dump(config_json, f, indent=2)

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
        config=str(staged_config_path),
        dataset=str(staged_dataset),
        folder_output=str(out_dir),
    )
    print(f"[run_model] done task_id={args.task_id}: results in {out_dir}")


if __name__ == "__main__":
    main()
