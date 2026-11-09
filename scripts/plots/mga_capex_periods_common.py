"""Shared run definition, colours and helpers for the mga_tests figure scripts.

fig1/3/4/10/12 read parameters_mga.csv task_id 32: one region (all), horizons
2030, 2038 and 2050, 13 axes (industrial heat electrification, passenger road
electrification, CO2 storage utilisation, cumulative emissions, cost). To plot
another run, change MODEL/RUN_SUFFIX/RUN_LABEL/REGIONS/YEARS/METRICS here.

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

MODEL = "zen_europe_ind_heat_v1_no_flexibility_nodiffusion_export0"
RUN_SUFFIX = (
    "2022_8a_4a_interval_1ts_MGA_AXES_OUTPUT_EXP0_1REG_CO2STORE"
    "_batch_bbofast_minmax_batch16_tol015_eps007"
)
RUN_DIR = MGA_ROOT / f"{MODEL}_{RUN_SUFFIX}"
POLY_PATH = RUN_DIR / f"{MODEL}_batch_summary" / "polytope.npz"
RUN_LABEL = "ZEN-Europe MGA, run 32"

RUN21_SUFFIX = (
    "2022_8a_4a_interval_1ts_MGA_AXES_OUTPUT_EXP0_2REG_CO2FIX"
    "_batch_bbofast_minmax_batch16_tol03_eps007"
)
RUN21_POLY_PATH = MGA_ROOT / f"{MODEL}_{RUN21_SUFFIX}" / f"{MODEL}_batch_summary" / "polytope.npz"
RUN21_FIGURES_SUBDIR = "archive/run21"

_ETH_BLUE, _ETH_PETROL, _ETH_GREEN, _ETH_BRONZE, _ETH_RED, _ETH_PURPLE, _ETH_GREY = SCENARIO_PALETTE
NEAR_BLACK = "#333333"

REGIONS = ["all"]
YEARS = ["2030", "2038", "2050"]
REGION_COLOR = {"north": _ETH_BLUE, "south": _ETH_BRONZE, "all": NEAR_BLACK}
# Within a colour, year is a tint: 2030 full colour, later years lighter.
YEAR_TINT = {"2030": 0.0, "2038": 0.3, "2050": 0.55}

METRICS = ["heating", "transport", "ccs", "emissions"]
# Panel order of the figures with one column per metric (fig12).
METRIC_COLUMNS = ["emissions", "heating", "transport", "ccs"]

RUN21_REGIONS = ["north", "south"]
RUN21_YEARS = ["2030", "2050"]
RUN21_METRIC_COLUMNS = ["capex", "emissions", "transport", "heating"]

METRIC_COLOR = {
    "capex": _ETH_PETROL,
    "transport": _ETH_GREEN,
    "heating": _ETH_RED,
    "ccs": _ETH_PURPLE,
    "emissions": _ETH_GREY,
    "cost": NEAR_BLACK,
}
METRIC_LABEL = {
    "capex": "CAPEX",
    "transport": "Transport share",
    "heating": "Heating share",
    "ccs": "CCS utilisation",
    "emissions": "CO$_2$ emissions",
    "cost": "Total cost",
}
# Shares are snapshots of one year; CAPEX and emissions accumulate up to it.
METRIC_IS_CUMULATIVE = {"capex": True, "transport": False, "heating": False, "ccs": False, "emissions": True}

# Stored axis unit -> (factor to the unit shown in figures, its label).
_DISPLAY_UNITS = {
    "megaEuro": (1e-3, "bn EUR"),
    "megaton": (1e-3, "Gt CO$_2$"),
    "dimensionless": (100.0, "%"),
}


class AxisInfo(NamedTuple):
    region: str | None
    metric: str
    year: str | None


def parse_axis(name: str) -> AxisInfo:
    """Region, metric and year encoded in one of this run's axis names."""
    if name == "net_present_cost":
        return AxisInfo(None, "cost", None)
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
