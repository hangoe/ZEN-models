import json
import tempfile
from pathlib import Path
from zen_garden import run, Results
from run_model import apply_axes_override

# Which data/*.json config to run with. Available:
#   config.json                - normal (non-MGA) run
#   config_mga_weights.json    - MGA, weights mode (normalisation has no effect)
#   config_mga_oracle.json     - MGA, oracle mode (normalisation always "relative")
#   config_mga_sampling.json   - MGA, sampling mode
#   config_mga_bbo.json        - MGA, bbo mode
config = "config_mga_weights.json"

# Overrides plugins.mga.normalisation ("relative", "units" or "minmax") in a
# private staged copy of `config` -- the shared data/*.json file is never
# touched.
# Set to None to leave the config's own default in place.
normalisation = None

my_dataset = str("Crystal_Ball_ind_heat_v8_0_no_flexibility")
my_comment = "2050_1a_5a_interval_5ts_MGA_weights"

DATA_DIR_CONFIG = Path(__file__).parent / "data"
DATA_DIR = Path(__file__).parent.parent / "ZEN-creator" / "outputs"

# System config overrides — edit these to change run behavior
system_overrides = {
    "conduct_time_series_aggregation": True,
    "aggregated_time_steps_per_year": 5,
    "reference_year": 2050,
    "optimized_years": 1,
    "interval_between_years": 5,
    "use_rolling_horizon": False,
}

if __name__ == "__main__":
    with open(DATA_DIR_CONFIG / config) as f:
        config_json = json.load(f)
    apply_axes_override(config_json, config)
    mga_cfg = config_json.get("plugins", {}).get("mga")
    if normalisation is not None:
        if mga_cfg is None:
            raise SystemExit(f"normalisation={normalisation!r} but {config} has no plugins.mga block.")
        mga_cfg["normalisation"] = normalisation
    if mga_cfg is not None:
        from zen_garden_plugins.mga.plugin import validate_config
        validate_config(mga_cfg)  # fail fast, before system.json is patched below

    # Stage the (possibly normalisation-patched) config to a temp file so
    # the shared data/*.json file is never touched.
    staged_config_dir = tempfile.mkdtemp(prefix="zen_config_")
    staged_config_path = Path(staged_config_dir) / config
    with open(staged_config_path, "w") as f:
        json.dump(config_json, f, indent=2)

    system_json_path = DATA_DIR / my_dataset / "system.json"

    # Load dataset system.json, apply overrides, restore after run
    with open(system_json_path) as f:
        original_system = json.load(f)
    patched_system = {**original_system, **system_overrides}
    with open(system_json_path, "w") as f:
        json.dump(patched_system, f, indent=2)

    try:
        run(
            config=str(staged_config_path),
            dataset=str(DATA_DIR / my_dataset),
            folder_output=str(DATA_DIR_CONFIG / "outputs" / "local_outputs" / f"{my_dataset}_{my_comment}"),
        )
    finally:
        with open(system_json_path, "w") as f:
            json.dump(original_system, f, indent=2)

#r = Results(path=DATA_DIR_CONFIG / "outputs" / "local_outputs" / f"{my_dataset}_{my_comment}")

print(Results)
