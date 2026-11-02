"""Run one row of a parameter CSV (parameters.csv or parameters_mga.csv).

Each row is a complete run: dataset, comment, config file and overrides. The
row's dataset is staged as a private copy (on Euler under $SCRATCH), the
row's system columns are applied to that copy, MGA/solver columns are
applied to a private copy of the config, and ZEN-garden runs on both. The
shared dataset and config files are never modified.

Columns other than META_COLUMNS are system.yaml overrides; system keys a row
has no column for fall back to DEFAULT_SYSTEM_OVERRIDES, and a blank cell
keeps the dataset's own value. Column reference: euler/README_euler.md;
history of the sweep driver: euler/MGA_RUN_HISTORY.md.

Run one row by hand:  python run_model.py --task_id 0 --run_on local
On Euler it is launched by submit_euler.sh / submit_euler_mga.sh.

Known ZEN-garden issue (not patched here): for interval_between_years > 1,
constraint_technology_diffusion_limit scales the growth term but not the
"unbounded" terms, so diffusion is slightly over-constrained at dy > 1.
"""

import argparse
import json  # legacy system.json datasets
import logging
import os
import sys
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from zen_garden import run, Results  # noqa: F401  (Results kept for post-processing)

# Own stdout handler: ZEN-garden configures the root logger itself.
logger = logging.getLogger("run_model")
logger.setLevel(logging.INFO)
logger.propagate = False
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(logging.Formatter("[run_model] %(message)s"))
logger.addHandler(_handler)

# --- Fixed locations (same layout as your original script) ----------------------
REPO_DIR = Path(__file__).parent                                  # .../ZEN-models
DATA_DIR_CONFIG = REPO_DIR / "data"                               # config.yaml + local outputs
CONFIG_EULER_DIR = DATA_DIR_CONFIG / "config_euler"               # config_mga_*.yaml (MGA + axes)

# Places `my_dataset` is looked up, in order. ZEN-europe's generated datasets
# (data/outputs/zen-europe-new, named as in ZEN-europe's models.yaml) are the
# primary source; data/outputs/zen-europe-old holds the older generation (old names);
# older pristine copies live in ZEN-creator/outputs; data/ is kept as a fallback
# for one-off/local datasets.
DATASET_SEARCH_DIRS = [
    REPO_DIR / "data" / "outputs" / "zen-europe-new",
    REPO_DIR / "data" / "outputs" / "zen-europe-old",
    REPO_DIR.parent / "ZEN-creator" / "outputs",
    REPO_DIR / "data",
]

# Columns in parameters.csv that are NOT system.json overrides.
# Everything else in a row is applied as a system_overrides key.
META_COLUMNS = {
    "my_dataset", "my_comment", "config", "normalisation", "batch_size",
    "n_workers", "axes_config", "tolerance_explore", "seed_rng",
    "solver_threads", "epsilon", "numeric_focus", "max_iterations",
    "solver_options", "cost_noise", "noise_seed", "flex_cost_fix",
}

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

# config.yaml used when a row/CSV has no "config" column (or leaves it
# blank) -- keeps the original non-MGA parameters.csv working unchanged.
DEFAULT_CONFIG = "config.yaml"

def apply_axes_override(run_config: dict, axes_config_path: Path | None) -> None:
    """Replace plugins.mga.axes with the row's axes file, in-place.

    The axes live in their own files (data/config_euler/config_mga_axes_*.yaml)
    so the mode configs don't each carry a copy. No-op for configs without
    plugins.mga and for rows without an axes_config.
    """
    mga_cfg = run_config.get("plugins", {}).get("mga")
    if mga_cfg is None or axes_config_path is None:
        return
    with open(axes_config_path) as f:
        mga_cfg["axes"] = yaml.safe_load(f)


def apply_normalisation_override(run_config: dict, config_name: str, normalisation: str) -> None:
    """Overwrite plugins.mga.normalisation in-place with the CSV row's value.

    Lets one config_mga_bbo.yaml / config_mga_sampling.yaml serve both
    normalisation modes -- the CSV row picks the mode, run_model.py bakes
    it into a private staged copy of the config (see main()), the shared
    data/*.yaml file is never touched.
    """
    mga_cfg = run_config.get("plugins", {}).get("mga")
    if mga_cfg is None:
        raise SystemExit(
            f"[run_model] row sets normalisation={normalisation!r} but "
            f"{config_name} has no plugins.mga block to apply it to."
        )
    mga_cfg["normalisation"] = normalisation


def apply_epsilon_override(run_config: dict, config_name: str, epsilon) -> None:
    """Overwrite plugins.mga.epsilon in-place with the CSV row's value.

    epsilon sets the near-optimality budget the MGA search explores within:
    total_cost <= (1 + epsilon) * NPC*. The shared config_mga_*.yaml files
    default this to 0.01 (1%), an arbitrary tight budget. For the
    per_axes-normalised total-axes run, epsilon is instead sized from a
    welfare-tolerance estimate:
        525e6 inhabitants x 30 years x 100 EUR/inhabitant/year
            = ~1.575e12 EUR (~1.5 trillion EUR) -- the aggregate extra
            spend society might plausibly accept over the horizon.
        NPC* (this dataset's cost-optimal net present cost) ~= 22e12 EUR.
        epsilon = 1.5e12 / 22e12 ~= 0.068 -> rounded to 0.07 (7%).
    Same private-staged-copy pattern as apply_normalisation_override(): lets
    one config_mga_batch_*.yaml be swept over different epsilon values from
    parameters_mga.csv without touching the shared data/*.yaml file.
    """
    mga_cfg = run_config.get("plugins", {}).get("mga")
    if mga_cfg is None:
        raise SystemExit(
            f"[run_model] row sets epsilon={epsilon!r} but "
            f"{config_name} has no plugins.mga block to apply it to."
        )
    mga_cfg["epsilon"] = epsilon


def apply_batch_overrides(run_config: dict, config_name: str, batch_size, n_workers, tolerance_explore, seed_rng, max_iterations=None) -> None:
    """Overwrite plugins.mga.batch.{batch_size,n_workers,tolerance_explore,seed_rng,max_iterations} in-place with the CSV row's values.

    Same private-staged-copy pattern as apply_normalisation_override(): lets
    one config_mga_batch_*.yaml be swept over different batch_size/n_workers/
    tolerance_explore/seed_rng values from parameters.csv without touching
    the shared data/*.yaml file. tolerance_explore is normalisation-dependent
    (see the MGA plugin's docs): under "share" it trades off how much
    exploration effort larger vs. smaller axes/regions get, so a row may
    need its own value distinct from other rows sharing the same config
    file. seed_rng left unset keeps batch_oracle's default nondeterministic
    seeding (see module docstring) -- set it to pin a row to a specific,
    reproducible draw, e.g. for an explicit random-seed comparison against
    an unpinned row using the same config otherwise.
    """
    if (batch_size is None and n_workers is None and tolerance_explore is None
            and seed_rng is None and max_iterations is None):
        return
    batch_cfg = run_config.get("plugins", {}).get("mga", {}).get("batch")
    if batch_cfg is None:
        raise SystemExit(
            f"[run_model] row sets batch_size/n_workers/tolerance_explore/seed_rng/max_iterations but "
            f"{config_name} has no plugins.mga.batch block to apply them to."
        )
    if batch_size is not None:
        batch_cfg["batch_size"] = batch_size
    if n_workers is not None:
        batch_cfg["n_workers"] = n_workers
    if tolerance_explore is not None:
        batch_cfg["tolerance_explore"] = tolerance_explore
    if seed_rng is not None:
        batch_cfg["seed_rng"] = seed_rng
    if max_iterations is not None:
        batch_cfg["max_iterations"] = max_iterations


def apply_solver_threads_override(run_config: dict, config_name: str, solver_threads) -> None:
    """Overwrite solver.solver_options.Threads in-place with the CSV row's value.

    Same private-staged-copy pattern as the other overrides. Batch mode's
    per-worker Gurobi solves each request this many threads, so
    submit_euler_mga.sh's cpus-per-task needs batch_size x solver_threads
    cores to avoid oversubscribing the node (see module docstring).
    """
    if solver_threads is None:
        return
    solver_options = run_config.get("solver", {}).get("solver_options")
    if solver_options is None:
        raise SystemExit(
            f"[run_model] row sets solver_threads but {config_name} has no "
            f"solver.solver_options block to apply it to."
        )
    solver_options["Threads"] = solver_threads


def apply_numeric_focus_override(run_config: dict, config_name: str, numeric_focus) -> None:
    """Overwrite solver.solver_options.NumericFocus in-place with the CSV row's value.

    Same private-staged-copy pattern as the other overrides. Lets badly scaled
    datasets (e.g. zen_europe, whose barrier path fails at NumericFocus 0) use
    NumericFocus 2 without slowing down every other row sharing config.yaml.
    """
    if numeric_focus is None:
        return
    solver_options = run_config.get("solver", {}).get("solver_options")
    if solver_options is None:
        raise SystemExit(
            f"[run_model] row sets numeric_focus but {config_name} has no "
            f"solver.solver_options block to apply it to."
        )
    solver_options["NumericFocus"] = numeric_focus


def apply_solver_options_override(run_config: dict, config_name: str, solver_options_str) -> None:
    """Merge a row's "Key=val;Key=val" string into solver.solver_options in-place.

    Same private-staged-copy pattern as the other overrides, but generic: one
    column covers any Gurobi parameter (BarOrder, BarHomogeneous, BarConvTol,
    Presolve, ...) for solver-setting sweeps, instead of one column per
    parameter. Values go through to_native, so "1" -> int, "1e-6" -> float.
    """
    if solver_options_str is None:
        return
    solver_options = run_config.get("solver", {}).get("solver_options")
    if solver_options is None:
        raise SystemExit(
            f"[run_model] row sets solver_options but {config_name} has no "
            f"solver.solver_options block to apply it to."
        )
    for item in str(solver_options_str).split(";"):
        if not item.strip():
            continue
        if "=" not in item:
            raise SystemExit(f"[run_model] bad solver_options entry {item!r} (expected Key=value)")
        key, value = item.split("=", 1)
        solver_options[key.strip()] = to_native(value)


# Storage techs touched by cost_noise / flex_cost_fix: the industry
# flexibility options (TES and DSM) suspected of making the LP degenerate.
FLEX_STORAGE_PREFIXES = ("industry_TES_",)
FLEX_STORAGE_SUFFIXES = ("_DSM",)
NOISE_ATTRIBUTES = (
    "capex_specific_storage", "capex_specific_storage_energy",
    "opex_specific_variable", "opex_specific_fixed_energy",
)


def flex_storage_dirs(dataset_dir: Path) -> list[Path]:
    storage_root = dataset_dir / "set_technologies" / "set_storage_technologies"
    if not storage_root.exists():
        return []
    return sorted(
        d for d in storage_root.iterdir()
        if d.is_dir() and (d.name.startswith(FLEX_STORAGE_PREFIXES) or d.name.endswith(FLEX_STORAGE_SUFFIXES))
    )


def apply_flex_cost_fix(dataset_dir: Path) -> None:
    """Give TES/DSM non-zero power capex and TES a non-negligible variable opex, in the STAGED copy.

    Numerical test of the degeneracy hypothesis, NOT final data: as generated,
    TES/DSM have power capex 0 and TES opex_specific_variable 1 Euro/GWh, so
    power capacity and flows are (nearly) free and the LP has a large optimal
    face. Here capex_specific_storage = 0.1 x capex_specific_storage_energy
    ("0.1 h equivalent", same money unit per power unit) and TES
    opex_specific_variable = 0.5 Euro/MWh.
    """
    for tech_dir in flex_storage_dirs(dataset_dir):
        path = tech_dir / "attributes.yaml"
        with open(path) as f:
            attrs = yaml.safe_load(f)
        # capex_specific_storage keeps its own unit (Euro/MW or Euro/(tproduct/h)),
        # the per-power-unit counterpart of the energy capex unit.
        energy_capex = float(attrs["capex_specific_storage_energy"]["default_value"])
        attrs["capex_specific_storage"]["default_value"] = 0.1 * energy_capex
        if tech_dir.name.startswith(FLEX_STORAGE_PREFIXES):
            attrs["opex_specific_variable"]["default_value"] = 0.5
            attrs["opex_specific_variable"]["unit"] = "Euro/MWh"
        with open(path, "w") as f:
            yaml.safe_dump(attrs, f, sort_keys=False)
    logger.info(f"flex_cost_fix applied to {len(flex_storage_dirs(dataset_dir))} TES/DSM techs")


def apply_cost_noise(dataset_dir: Path, eps: float, seed: int) -> None:
    """Multiply TES/DSM cost parameters by (1 + eps*u), u ~ U(-1, 1), per node, in the STAGED copy.

    Tests whether breaking exact cost ties between identical TES/DSM techs
    (and nodes) speeds up the solve. Writes one <attribute>.csv per attribute
    in node,<attribute> format (like capacity_limit.csv), so each node gets
    its own draw; attributes that already have a CSV are left alone. Zero
    costs stay zero. eps must be well above the barrier tolerances
    (~1e-4..1e-2), otherwise it changes nothing.
    """
    rng = np.random.default_rng(seed)
    system_path = next(dataset_dir / n for n in ("system.json", "system.yaml", "system.yml")
                       if (dataset_dir / n).exists())
    with open(system_path) as f:
        system = json.load(f) if system_path.suffix == ".json" else yaml.safe_load(f)
    nodes = system["set_nodes"]
    n_files = 0
    for tech_dir in flex_storage_dirs(dataset_dir):
        with open(tech_dir / "attributes.yaml") as f:
            attrs = yaml.safe_load(f)
        for attr in NOISE_ATTRIBUTES:
            csv_path = tech_dir / f"{attr}.csv"
            if attr not in attrs or csv_path.exists():
                continue
            base = float(attrs[attr]["default_value"])
            if base == 0.0:
                continue
            values = base * (1.0 + eps * rng.uniform(-1.0, 1.0, size=len(nodes)))
            pd.DataFrame({"node": nodes, attr: values}).to_csv(csv_path, index=False)
            n_files += 1
    logger.info(f"cost_noise eps={eps} seed={seed}: wrote {n_files} per-node cost files")


def validate_plugin_config(run_config: dict, config_name: str) -> None:
    """Fail fast on an invalid plugins.mga block, before staging/running.

    The plugin's own validate_config() only runs from an after_solve hook,
    i.e. after the (potentially long) baseline solve has already finished.
    Calling it here catches e.g. a bad "normalisation" value before a SLURM
    array task burns its walltime.
    """
    mga_cfg = run_config.get("plugins", {}).get("mga")
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
    """Convert a CSV/pandas cell to a clean Python bool/int/float/str.

    Integral floats become ints: ZEN-garden v3 validates config.yaml and
    system.yaml strictly, so e.g. batch_size=4.0 (pandas reads an int column
    with blanks as float) would be rejected.
    """
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

    def cell(column):
        """The row's value in ``column``, or None if the column or value is blank."""
        if column not in table.columns or pd.isna(row[column]):
            return None
        return row[column] if str(row[column]).strip() else None

    def native_cell(column):
        value = cell(column)
        return None if value is None else to_native(value)

    my_dataset = str(row["my_dataset"])
    my_comment = str(row["my_comment"])
    config_name = str(cell("config")).strip() if cell("config") is not None else DEFAULT_CONFIG
    axes_config = cell("axes_config")
    axes_config_path = CONFIG_EULER_DIR / str(axes_config).strip() if axes_config is not None else None
    normalisation = str(cell("normalisation")).strip() if cell("normalisation") is not None else None
    batch_size = native_cell("batch_size")
    n_workers = native_cell("n_workers")
    tolerance_explore = native_cell("tolerance_explore")
    seed_rng = native_cell("seed_rng")
    max_iterations = native_cell("max_iterations")
    solver_threads = native_cell("solver_threads")
    numeric_focus = native_cell("numeric_focus")
    epsilon = native_cell("epsilon")
    solver_options_str = str(cell("solver_options")).strip() if cell("solver_options") is not None else None
    cost_noise = float(cell("cost_noise")) if cell("cost_noise") is not None else None
    noise_seed = int(native_cell("noise_seed")) if cell("noise_seed") is not None else 0
    flex_cost_fix = bool(native_cell("flex_cost_fix")) if cell("flex_cost_fix") is not None else False
    # Defaults only fill keys the CSV has no column for; a blank cell in an
    # existing column keeps the dataset's own system.yaml value.
    system_cols = [col for col in table.columns if col not in META_COLUMNS]
    system_overrides = {
        **{k: v for k, v in DEFAULT_SYSTEM_OVERRIDES.items() if k not in system_cols},
        **{col: to_native(row[col]) for col in system_cols
           if pd.notna(row[col]) and str(row[col]).strip()},
    }

    logger.info(f"task_id={args.task_id}  dataset={my_dataset}  comment={my_comment}")
    logger.info(f"config={config_name}  axes_config={axes_config_path.name if axes_config_path else None}  "
                f"normalisation={normalisation}")
    logger.info(f"batch_size={batch_size}  n_workers={n_workers}  tolerance_explore={tolerance_explore}  "
          f"seed_rng={seed_rng}  solver_threads={solver_threads}  epsilon={epsilon}  "
          f"numeric_focus={numeric_focus}  max_iterations={max_iterations}")
    logger.info(f"solver_options={solver_options_str}  cost_noise={cost_noise}  "
          f"noise_seed={noise_seed}  flex_cost_fix={flex_cost_fix}")
    logger.info(f"system_overrides={system_overrides}")

    config_dir = CONFIG_EULER_DIR if config_name.startswith("config_mga") else DATA_DIR_CONFIG
    with open(config_dir / config_name) as f:
        run_config = yaml.safe_load(f)
    apply_axes_override(run_config, axes_config_path)
    if normalisation is not None:
        apply_normalisation_override(run_config, config_name, normalisation)
    apply_batch_overrides(run_config, config_name, batch_size, n_workers, tolerance_explore, seed_rng, max_iterations)
    apply_solver_threads_override(run_config, config_name, solver_threads)
    apply_numeric_focus_override(run_config, config_name, numeric_focus)
    apply_solver_options_override(run_config, config_name, solver_options_str)
    if epsilon is not None:
        apply_epsilon_override(run_config, config_name, epsilon)
    validate_plugin_config(run_config, config_name)

    # --- 2. Stage a PRIVATE copy of the dataset (safe for parallel array tasks) --
    work = working_root(args.run_on) / f"task_{args.task_id}"
    staged_dataset = work / my_dataset
    if staged_dataset.exists():
        shutil.rmtree(staged_dataset)
    staged_dataset.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(resolve_dataset_dir(my_dataset), staged_dataset)
    # Cost fix first, so noise (if both are set) perturbs the fixed values.
    if flex_cost_fix:
        apply_flex_cost_fix(staged_dataset)
    if cost_noise is not None:
        apply_cost_noise(staged_dataset, cost_noise, noise_seed)

    # Write the (possibly normalisation-patched) config to the same private
    # per-task folder, so the shared data/*.yaml file is never touched and
    # concurrent array tasks never read/write it at once.
    staged_config_path = work / config_name
    with open(staged_config_path, "w") as f:
        yaml.safe_dump(run_config, f, sort_keys=False)

    # --- 3. Apply the system.json overrides to the COPY --------------------------
    # ZEN-creator's newer datasets ship system.yaml instead of system.json.
    system_path = next(
        (staged_dataset / n for n in ("system.json", "system.yaml", "system.yml")
         if (staged_dataset / n).exists()),
        staged_dataset / "system.json",
    )
    with open(system_path) as f:
        system = json.load(f) if system_path.suffix == ".json" else yaml.safe_load(f)
    system.update(system_overrides)
    with open(system_path, "w") as f:
        if system_path.suffix == ".json":
            json.dump(system, f, indent=2)
        else:
            yaml.safe_dump(system, f, sort_keys=False)

    # --- 4. Decide the output folder (scratch on Euler) --------------------------
    if args.run_on == "euler":
        out_dir = working_root(args.run_on) / "outputs" / f"{my_dataset}_{my_comment}"
    else:
        out_dir = DATA_DIR_CONFIG / "outputs" / "zen-europe-outputs-new" / f"{my_dataset}_{my_comment}"
    out_dir.parent.mkdir(parents=True, exist_ok=True)

    # --- 5. Run the model --------------------------------------------------------
    run(
        config=str(staged_config_path),
        dataset=str(staged_dataset),
        folder_output=str(out_dir),
    )
    logger.info(f"done task_id={args.task_id}: results in {out_dir}")


if __name__ == "__main__":
    main()
