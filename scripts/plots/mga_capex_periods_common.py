"""Shared run definition, colours and helpers for the mga_tests figure scripts.

All of them read parameters_mga.csv task_id 21: two regions (north/south),
horizons 2030 and 2050, 17 axes from config_mga_axes_total_output_2reg.yaml
(CAPEX, passenger road and industrial heat output shares, emissions, cost).
To plot another run, change MODEL/RUN_SUFFIX/RUN_LABEL here.
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
    "2022_8a_4a_interval_1ts_MGA_AXES_OUTPUT_EXP0_2REG_CO2FIX"
    "_batch_bbofast_minmax_batch16_tol03_eps007"
)
RUN_DIR = MGA_ROOT / f"{MODEL}_{RUN_SUFFIX}"
POLY_PATH = RUN_DIR / f"{MODEL}_batch_summary" / "polytope.npz"
RUN_LABEL = "ZEN-Europe MGA, run 21"

_ETH_BLUE, _ETH_PETROL, _ETH_GREEN, _ETH_BRONZE, _ETH_RED, _ETH_PURPLE, _ETH_GREY = SCENARIO_PALETTE
NEAR_BLACK = "#333333"

REGIONS = ["north", "south"]
YEARS = ["2030", "2050"]
REGION_COLOR = {"north": _ETH_BLUE, "south": _ETH_BRONZE}
# Within a colour, year is a tint: 2030 full colour, 2050 lighter.
YEAR_TINT = {"2030": 0.0, "2050": 0.5}

METRICS = ["capex", "transport", "heating", "emissions"]
# Panel order of the figures with one column per metric (fig11/12, fig20/21).
METRIC_COLUMNS = ["capex", "emissions", "transport", "heating"]
METRIC_COLOR = {
    "capex": _ETH_PETROL,
    "transport": _ETH_GREEN,
    "heating": _ETH_RED,
    "emissions": _ETH_GREY,
    "cost": NEAR_BLACK,
}
METRIC_LABEL = {
    "capex": "CAPEX",
    "transport": "Transport share",
    "heating": "Heating share",
    "emissions": "CO$_2$ emissions",
    "cost": "Total cost",
}
# Shares are snapshots of one year; CAPEX and emissions accumulate up to it.
METRIC_IS_CUMULATIVE = {"capex": True, "transport": False, "heating": False, "emissions": True}

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
        "emissions": r"(north|south)_co2_until_(\d{4})",
        "transport": r"(north|south)_passenger_road_electrification_(\d{4})",
        "heating": r"(north|south)_industry_heat_electrification_(\d{4})",
        "capex": r"(north|south)_until_(\d{4})",
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


def savefig(fig: plt.Figure, name: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{name}.svg"
    # dpi only affects rasterized artists (fig1's scatter clouds).
    fig.savefig(path, bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"  wrote {path.relative_to(REPO_ROOT)}")
