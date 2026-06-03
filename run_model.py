from pathlib import Path

from zen_garden import run

DATA_DIR = Path(__file__).parent / "data"

if __name__ == "__main__":
    run(
        config=str(DATA_DIR / "config.json"),
        dataset=str(DATA_DIR / "Crystal_Ball"),
    )
