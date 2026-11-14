"""Shared run definition, colours and helpers for the mga_tests figure scripts.

fig1/3/4/10/12 and fig51/52/60/61 read parameters_mga.csv task_id 57 (run 47 on the new
ZEN-Europe dataset zen_europe_no_flex_no_diffusion_export0; tolerance_explore 0.01,
tolerance_prob 0.95, n_samples 4000; axes config_mga_axes_ind_heating_thesis.yaml):
one region (all), snapshot years 2034 and 2050, 7 axes (industrial heat
electrification share, CO2 storage utilisation, imported biomass, each per year, and
cost). fig70-73 (plot_mga_run_comparison.py) compare run 56 (tolerance_explore 0.1) and
run 57 (COMPARE_RUNS, COMPARE_TAG). Earlier versions (old dataset
zen_europe_ind_heat_v1_no_flexibility_nodiffusion_export0) are in mga_tests/archive/run47/,
archive/run46_vs_47/, archive/run46/ and archive/run45_vs_46/.
To plot another run, change MODEL/RUN_SUFFIX/RUN_LABEL/REGIONS/YEARS/METRICS here.
The run-33 figures (heat/EV/CCS/emissions, 2030/2038/2050) are in
mga_tests/archive/run33/.

The RUN21_* names keep task_id 21 (north/south, 2030/2050, CAPEX, transport and
heating shares, emissions) for fig20/21 and fig30-33/40-43, which are archived
in mga_tests/archive/run21/ and write there.
"""

import re
from pathlib import Path
from typing import NamedTuple

REPO_ROOT = Path(__file__).parent.parent.parent

import matplotlib.pyplot as plt

from .figure_settings import SCENARIO_PALETTE, eth_tint

FIGURES_DIR = REPO_ROOT / "data" / "outputs" / "figures" / "mga_tests"
MGA_ROOT = REPO_ROOT / "data" / "outputs" / "euler_outputs_mga"

MODEL = "zen_europe_no_flex_no_diffusion_export0"
# Dataset of the runs up to 47 (run 21 is still plotted from it).
OLD_MODEL = "zen_europe_ind_heat_v1_no_flexibility_nodiffusion_export0"
RUN56_SUFFIX = (
    "2022_8a_4a_interval_1ts_MGA_IND_HEATING_THESIS"
    "_batch_bbofast_minmax_batch16_tol01_eps001_FREEZE2022_ci095_ns4000"
)
RUN56_LABEL = "run 56 (tolerance 0.1)"
RUN_SUFFIX = (
    "2022_8a_4a_interval_1ts_MGA_IND_HEATING_THESIS"
    "_batch_bbofast_minmax_batch16_tol001_eps001_FREEZE2022_ci095_ns4000"
)
RUN_DIR = MGA_ROOT / f"{MODEL}_{RUN_SUFFIX}"
POLY_PATH = RUN_DIR / f"{MODEL}_batch_summary" / "polytope.npz"
RUN_LABEL = "ZEN-Europe MGA, run 57"
RUN57_LABEL = "run 57 (tolerance 0.01)"

# Runs compared in fig70-73: label -> (run-folder suffix, tint), older run first. Each
# figure draws both runs in one hue (near-black, or the technology's colour), the older
# run as a light tint. COMPARE_TAG goes into the figure names.
COMPARE_RUNS = {
    RUN56_LABEL: (RUN56_SUFFIX, 0.55),
    RUN57_LABEL: (RUN_SUFFIX, 0.0),
}
COMPARE_TAG = "run56_vs_57"

RUN21_SUFFIX = (
    "2022_8a_4a_interval_1ts_MGA_AXES_OUTPUT_EXP0_2REG_CO2FIX"
    "_batch_bbofast_minmax_batch16_tol03_eps007"
)
RUN21_POLY_PATH = MGA_ROOT / f"{OLD_MODEL}_{RUN21_SUFFIX}" / f"{OLD_MODEL}_batch_summary" / "polytope.npz"
RUN21_FIGURES_SUBDIR = "archive/run21"

_ETH_BLUE, _ETH_PETROL, _ETH_GREEN, _ETH_BRONZE, _ETH_RED, _ETH_PURPLE, _ETH_GREY = SCENARIO_PALETTE
NEAR_BLACK = "#333333"

REGIONS = ["all"]
YEARS = ["2034", "2050"]
REGION_COLOR = {"north": _ETH_BLUE, "south": _ETH_BRONZE, "all": NEAR_BLACK}
# Within a colour, year is a tint: 2030 full colour, later years lighter.
YEAR_TINT = {"2030": 0.0, "2034": 0.0, "2038": 0.3, "2050": 0.55}

METRICS = ["heating", "ccs", "biomass"]
# Panel order of the figures with one column per metric (fig12).
METRIC_COLUMNS = ["heating", "ccs", "biomass"]

RUN21_REGIONS = ["north", "south"]
RUN21_YEARS = ["2030", "2050"]
RUN21_METRIC_COLUMNS = ["capex", "emissions", "transport", "heating"]

METRIC_COLOR = {
    "capex": _ETH_PETROL,
    # Technology colours of the mga_tests figures (since runs 46/47, also 56/57): heat magenta, CCS blue,
    # biomass green. EVs (run 33, archived) were blue too; no run plots both.
    "transport": _ETH_BLUE,
    "heating": _ETH_PURPLE,
    "ccs": _ETH_BLUE,
    "biomass": _ETH_GREEN,
    "emissions": _ETH_GREY,
    "cost": NEAR_BLACK,
}
METRIC_LABEL = {
    "capex": "CAPEX",
    "transport": "Transport share",
    "heating": "Heating share",
    "ccs": "CCS utilisation",
    "biomass": "Imported biomass",
    "emissions": "CO$_2$ emissions",
    "cost": "Total cost",
}
# Shares are snapshots of one year; CAPEX and emissions accumulate up to it.
METRIC_IS_CUMULATIVE = {"capex": True, "transport": False, "heating": False, "ccs": False, "biomass": False,
                        "emissions": True}

# Stored axis unit -> (factor to the unit shown in figures, its label).
_DISPLAY_UNITS = {
    "megaEuro": (1e-3, "bn EUR"),
    "megaton": (1e-3, "Gt CO$_2$"),
    "dimensionless": (100.0, "%"),
    "gigawatt * hour": (1e-3, "TWh"),
}


class AxisInfo(NamedTuple):
    region: str | None
    metric: str
    year: str | None


def parse_axis(name: str) -> AxisInfo:
    """Region, metric and year encoded in one of this run's axis names."""
    if name == "net_present_cost":
        return AxisInfo(None, "cost", None)
    match = re.fullmatch(r"imported_biomass_(\d{4})", name)
    if match:
        # Imports are not per region; reported as "all" so labels and axis_name work.
        return AxisInfo("all", "biomass", match[1])
    patterns = {
        "emissions": r"(north|south|all)_co2_until_(\d{4})",
        "transport": r"(north|south|all)_passenger_road_electrification_(\d{4})",
        "heating": r"(north|south|all)_industry_heat_electrification_(\d{4})",
        "ccs": r"(north|south|all)_co2_storage_(\d{4})",
        "capex": r"(north|south|all)_until_(\d{4})",
    }
    for metric, pattern in patterns.items():
        match = re.fullmatch(pattern, name)
        if match:
            return AxisInfo(match[1], metric, match[2])
    raise ValueError(f"unknown axis name {name!r}")


def axis_name(region: str, metric: str, year: str) -> str:
    """Inverse of parse_axis for the region/metric/year axes."""
    if metric == "biomass":
        return f"imported_biomass_{year}"
    middle = {
        "capex": "until",
        "transport": "passenger_road_electrification",
        "heating": "industry_heat_electrification",
        "ccs": "co2_storage",
        "emissions": "co2_until",
    }[metric]
    return f"{region}_{middle}_{year}"


def display_unit(unit: str) -> tuple[float, str]:
    """(factor, label) converting a stored axis unit to the one shown in figures."""
    if unit not in _DISPLAY_UNITS:
        raise ValueError(f"no display unit for {unit!r}")
    return _DISPLAY_UNITS[unit]


def year_tint(color: str, year: str) -> str:
    tint = YEAR_TINT[year]
    return eth_tint(color, tint) if tint else color


def savefig(fig: plt.Figure, name: str, subdir: str | None = None) -> None:
    folder = FIGURES_DIR / subdir if subdir else FIGURES_DIR
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}.svg"
    # dpi only affects rasterized artists (fig1's scatter clouds).
    fig.savefig(path, bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"  wrote {path.relative_to(REPO_ROOT)}")
