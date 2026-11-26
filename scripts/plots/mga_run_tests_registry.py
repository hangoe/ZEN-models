"""Runs and effect groups of the MGA run tests (figures-*/mga-run-tests).

The runs live in euler/mga_runs.csv: one row per run, short run_id (V = old v9
calibration, Z = ZEN-Europe v1 calibration, T = thesis), its Euler job IDs and
its settings. Thesis runs (T*) only appear here where they give the only clean
comparison.
"""

from pathlib import Path

import pandas as pd

from plots.figure_settings import SCENARIO_PALETTE, eth_tint

RUNS_CSV = Path(__file__).resolve().parents[2] / "euler" / "mga_runs.csv"


def load_runs() -> dict[str, dict]:
    """run_id -> row of euler/mga_runs.csv (NaN cells as None)."""
    table = pd.read_csv(RUNS_CSV, dtype=str, keep_default_na=False)
    runs = {}
    for row in table.to_dict("records"):
        row = {k: (v if v != "" else None) for k, v in row.items()}
        row["thesis"] = row["role"] == "thesis"
        row["jobs"] = tuple((row["other_jobs"] or "").split(";") if row["other_jobs"] else ()) + \
            ((row["job_id"],) if row["job_id"] else ())
        runs[row["run_id"]] = row
    return runs


RUNS = load_runs()

# Effect groups: (file tag, panel title, [(run_id, legend text)]).
# Tolerance and cost slack are pairs (only drawn when both runs of a pair exist).
EFFECTS: list[tuple[str, str, list[tuple[str, str]]]] = [
    ("tolerance", "Tolerance",
     [("Z6", "tol 0.1"), ("Z7", "tol 0.01"), ("T2", "tol 0.1"), ("T3", "tol 0.01")]),
    ("dimensions", "Dimensions",
     [("Z7", "7 axes, tol 0.01, slack 1%"), ("Z2", "13 axes, tol 0.15, slack 7%"),
      ("Z1", "17 axes, tol 0.3, slack 7%")]),
    ("cost_slack", "Cost slack",
     [("T3", "slack 1%"), ("T4", "slack 0.2%")]),
    ("batch_seed", "Batch size and seed",
     [("V1", "batch 4"), ("V2", "batch 4, seed 42"), ("V3", "batch 16")]),
    ("time_resolution", "Time series resolution and periods",
     [("V1", "1 ts, 7 periods"), ("V4", "3 ts, 7 periods"),
      ("V5", "10 ts, 7 periods"), ("V6", "1 ts, 4 periods")]),
]
PAIRED_EFFECTS = {"tolerance", "cost_slack"}

# Colour system: every run_id has its own colour, the same in every figure, and the
# group is visible from the lightness:
#   V (old v9 calibration)        full ETH colours
#   Z (ZEN-Europe v1 calibration) light ETH tints (45 % towards white)
#   T (thesis runs)               black and greys; darker = tighter setting
# No two runs share a colour. ETH palette only.
_BLUE, _PETROL, _GREEN, _BRONZE, _RED, _PURPLE, _GREY = SCENARIO_PALETTE
_Z_TINT = 0.45
NEAR_BLACK = "#1F1F1F"
RUN_COLOR: dict[str, str] = {
    "V1": _BRONZE, "V2": _PURPLE, "V3": _RED, "V4": _GREEN, "V5": _BLUE, "V6": _PETROL,
    "Z1": eth_tint(_PETROL, _Z_TINT), "Z2": eth_tint(_GREEN, _Z_TINT), "Z3": eth_tint(_BRONZE, _Z_TINT),
    "Z4": eth_tint(_GREY, _Z_TINT), "Z5": eth_tint(_RED, _Z_TINT), "Z6": eth_tint(_PURPLE, _Z_TINT),
    "Z7": eth_tint(_BLUE, _Z_TINT),
    "T1": eth_tint(_GREY, 0.3), "T2": _GREY, "T3": NEAR_BLACK, "T4": eth_tint(_GREY, 0.5),
}
assert len(set(RUN_COLOR.values())) == len(RUN_COLOR), "run colours must be unique"
