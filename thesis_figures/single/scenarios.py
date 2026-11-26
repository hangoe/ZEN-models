"""Scenarios of the single (cost-optimal) model runs and how they are loaded.

Every scenario is one run in data/results/single/<run folder> (runs/parameters.csv
defines them). All runs model 2022-2050 in steps of four years, with ten representative
time steps per year unless stated otherwise. Labels are the scenario names of the thesis.
"""

from ..paths import SINGLE_RESULTS_DIR
from ..results import Run, get_available_years, load_results

NO_FLEX = "ZEN-Europe-No-Flex"
FULL = "ZEN-Europe"
LEGACY = "ZEN-Europe-Legacy"
NO_TES = "ZEN-Europe-No-TES"
NO_DSM = "ZEN-Europe-No-DSM"
NO_TES_DSM_PESS = "ZEN-Europe-No-TES-DSM-Pess"
SINGLE_TEMP = "ZEN-Europe-Single-Temp"
NO_FLEX_SINGLE_TEMP = "ZEN-Europe-No-Flex-Single-Temp"
FULL_20TS = f"{FULL} (20 ts)"
NO_FLEX_20TS = f"{NO_FLEX} (20 ts)"

RUN_FOLDERS = {
    NO_FLEX: "zen_europe_no_flex_2022_8a_4a_interval_10ts",
    FULL: "zen_europe_2022_8a_4a_interval_10ts",
    LEGACY: "zen_europe_legacy_2022_8a_4a_interval_10ts",
    NO_TES: "zen_europe_no_tes_2022_8a_4a_interval_10ts",
    NO_DSM: "zen_europe_no_dsm_2022_8a_4a_interval_10ts",
    NO_TES_DSM_PESS: "zen_europe_no_tes_dsm_pess_2022_8a_4a_interval_10ts",
    SINGLE_TEMP: "zen_europe_single_temp_diff_correct",
    NO_FLEX_SINGLE_TEMP: "zen_europe_no_flex_single_temp_diff_correct_2022_8a_4a_interval_10ts",
    FULL_20TS: "zen_europe_2022_8a_4a_interval_20ts",
    NO_FLEX_20TS: "zen_europe_no_flex_2022_8a_4a_interval_20ts",
}

MODELLED_YEARS = list(range(2022, 2051, 4))
COMPARISON_YEARS = [2030, 2038, 2050]  # snapshot years of the multi-year panels


def load_runs(labels: list[str]) -> list[Run]:
    """Load the runs of `labels`, in that order."""
    runs = [Run(name=RUN_FOLDERS[label], label=label,
                results=load_results(SINGLE_RESULTS_DIR, RUN_FOLDERS[label])) for label in labels]
    for run in runs:
        years = get_available_years(run.results)
        if years != MODELLED_YEARS:
            raise ValueError(f"{run.name} models {years}, expected {MODELLED_YEARS}")
    return runs


def by_label(runs: list[Run], label: str) -> Run:
    return next(r for r in runs if r.label == label)
