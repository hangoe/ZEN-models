from pathlib import Path
from zen_garden import run, Results

my_dataset = str("Crystal_Ball_HG_v2_0")

# DATA_DIR = Path(__file__).parent / "data"

DATA_DIR_CONFIG = Path(__file__).parent / "data"
DATA_DIR = Path(__file__).parent.parent / "ZEN-creator" / "outputs"

if __name__ == "__main__":
    run(
        config=str(DATA_DIR_CONFIG / "config.json"),
        dataset=str(DATA_DIR / my_dataset),
    )

#r = Results(path=DATA_DIR_CONFIG / "outputs" / my_dataset)

print(Results)