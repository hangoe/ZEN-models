import json
import tempfile
from pathlib import Path
from zen_garden import run, Results

# Which data/*.json config to run with. Available:
#   config.json                    - normal (non-MGA) run
#   config_mga_weights.json        - MGA, weights mode
#   config_mga_oracle.json         - MGA, oracle mode
#   config_mga_probabilistic.json  - MGA, probabilistic mode
config = "config_mga_weights.json"

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
    system_json_path = DATA_DIR / my_dataset / "system.json"

    # Load dataset system.json, apply overrides, restore after run
    with open(system_json_path) as f:
        original_system = json.load(f)
    patched_system = {**original_system, **system_overrides}
    with open(system_json_path, "w") as f:
        json.dump(patched_system, f, indent=2)

    try:
        run(
            config=str(DATA_DIR_CONFIG / config),
            dataset=str(DATA_DIR / my_dataset),
            folder_output=str(DATA_DIR_CONFIG / "outputs" / "local_outputs" / f"{my_dataset}_{my_comment}"),
        )
    finally:
        with open(system_json_path, "w") as f:
            json.dump(original_system, f, indent=2)

#r = Results(path=DATA_DIR_CONFIG / "outputs" / "local_outputs" / f"{my_dataset}_{my_comment}")

print(Results)
