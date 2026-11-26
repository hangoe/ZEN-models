"""Power generation capacity and storage discharge, Legacy vs. No-Flex (thesis Fig. 4).

Per snapshot year, ZEN-Europe-Legacy as an absolute stack next to the difference of
ZEN-Europe-No-Flex, drawn floating from the top of the Legacy bar (positive segments up,
negative down), with the total difference in absolute terms and in %. Storage discharge
includes industrial TES and DSM (as energy equivalent), which exist only in runs with
the industry heat extension.
"""

import matplotlib.pyplot as plt
import pandas as pd

from ..names import CARRIER_COLORS, display_name
from ..results import BULK_STORAGE_TECHS, INDUSTRY_TES_TECHS, Run, get_capacity, get_storage_flows
from ..style import (
    ETH_GREEN,
    ETH_RED,
    REPORT_VALUE_SIZE,
    REPORT_WIDTH,
    comma_axis,
    eth_tint,
    panel_title,
    report_legend,
    save_figure,
    stack_ordered,
)
from .metrics import DSM_ENERGY_STACK_ORDER, get_dsm_energy_equivalent
from .scenarios import COMPARISON_YEARS, LEGACY, NO_FLEX

POWER_GEN_TECHS = [
    "photovoltaics", "wind_onshore", "wind_offshore", "reservoir_hydro", "run-of-river_hydro", "nuclear",
    "natural_gas_turbine", "natural_gas_turbine_CCS", "hard_coal_plant", "lignite_coal_plant", "oil_plant",
    "biomass_plant", "biomass_plant_CCS", "waste_plant",
]
POWER_GEN_COLOR_MAP = {
    "photovoltaics": CARRIER_COLORS["solar"],
    "wind_onshore": CARRIER_COLORS["wind_onshore"],
    "wind_offshore": CARRIER_COLORS["wind_offshore"],
    "reservoir_hydro": CARRIER_COLORS["hydro_reservoir"],
    "run-of-river_hydro": CARRIER_COLORS["hydro_ror"],
    "nuclear": CARRIER_COLORS["nuclear"],
    "natural_gas_turbine": CARRIER_COLORS["natural_gas"],
    "natural_gas_turbine_CCS": CARRIER_COLORS["natural_gas_ccs"],
    "hard_coal_plant": CARRIER_COLORS["hard_coal"],
    "lignite_coal_plant": CARRIER_COLORS["lignite"],
    "oil_plant": CARRIER_COLORS["oil"],
    "biomass_plant": CARRIER_COLORS["biomass"],
    "biomass_plant_CCS": CARRIER_COLORS["biomass_ccs"],
    "waste_plant": CARRIER_COLORS["waste"],
}
# Bottom to top: fossil (dirtiest first), biomass and waste, nuclear, hydro, VRE.
POWER_GEN_STACK_ORDER = [
    "hard_coal_plant", "lignite_coal_plant", "oil_plant", "natural_gas_turbine", "natural_gas_turbine_CCS",
    "waste_plant", "biomass_plant", "biomass_plant_CCS", "nuclear",
    "reservoir_hydro", "run-of-river_hydro", "wind_onshore", "wind_offshore", "photovoltaics",
]

# Storage coloured by what it stores; industrial TES in ETH red tints (hotter = darker),
# industrial DSM (summed over the products, energy equivalent) in ETH green.
INDUSTRY_DSM_LABEL = "industry DSM (energy equiv.)"
STORAGE_COLOR_MAP = {
    "battery": CARRIER_COLORS["battery"],
    "pumped_hydro": CARRIER_COLORS["pumped_hydro"],
    "natural_gas_storage": CARRIER_COLORS["natural_gas"],
    "oil_storage": CARRIER_COLORS["oil"],
    "salt_cavern_storage": CARRIER_COLORS["hydrogen"],
    "industry_TES_water_0_100": eth_tint(ETH_RED, 0.55),
    "industry_TES_water_100_150": eth_tint(ETH_RED, 0.25),
    "industry_TES_steam_150_200": ETH_RED,
    INDUSTRY_DSM_LABEL: ETH_GREEN,
}
STORAGE_STACK_ORDER = ["battery", "pumped_hydro", "natural_gas_storage", "oil_storage", "salt_cavern_storage",
                       "industry_TES_water_0_100", "industry_TES_water_100_150", "industry_TES_steam_150_200",
                       INDUSTRY_DSM_LABEL]

DELTA_LABEL = rf"$\Delta$ {NO_FLEX}"


def base_and_delta_df(base_series: pd.Series, other_series: pd.Series, base_label: str,
                      delta_label: str) -> pd.DataFrame:
    """Columns [base, other - base] over the union of both indices (missing = 0)."""
    all_idx = base_series.index.union(other_series.index)
    base = base_series.reindex(all_idx, fill_value=0.0)
    other = other_series.reindex(all_idx, fill_value=0.0)
    return pd.DataFrame({base_label: base, delta_label: other - base})


def plot_base_and_floating_delta(dfs_by_year: dict[int, pd.DataFrame], title: str, unit: str, ax: plt.Axes,
                                 color_map: dict, decimals: int = 0) -> None:
    """Per year: the base bar stacked from 0 and the delta bar stacked from the top of the
    base bar, a dashed guide between them and the label "+X (+Y %)". `decimals`: number
    precision (0 for GW in the thousands, 1 for TWh)."""
    years = sorted(dfs_by_year)
    base_label, *delta_labels = dfs_by_year[years[0]].columns.tolist()
    group = len(delta_labels) + 2  # base + deltas + 1 gap slot
    bar_width = 0.8
    labeled: set[str] = set()
    positions_all: list[float] = []
    tick_labels_all: list[str] = []
    year_centers: list[float] = []
    y_max, y_min = 0.0, 0.0  # bar extents, for headroom above the value labels

    def bar(pos, val, bottom, category):
        ax.bar(pos, val, bar_width, bottom=bottom, color=color_map[category],
               label=display_name(category) if category not in labeled else None,
               edgecolor="white", linewidth=0.4, hatch="")
        labeled.add(category)

    for yi, year in enumerate(years):
        df = dfs_by_year[year]
        base_pos = yi * group
        positions_all.extend(base_pos + i for i in range(len(delta_labels) + 1))
        tick_labels_all.extend([base_label, *delta_labels])
        year_centers.append(base_pos + len(delta_labels) / 2)

        bottom = 0.0
        for category in df.index:
            val = df.loc[category, base_label]
            if abs(val) < 1e-6:
                continue
            bar(base_pos, val, bottom, category)
            bottom += val
        base_total = bottom
        ax.text(base_pos, base_total, f"{base_total:,.{decimals}f}", ha="center", va="bottom",
                fontsize=REPORT_VALUE_SIZE)

        for di, delta_label in enumerate(delta_labels):
            delta_pos = base_pos + 1 + di
            top, bot = base_total, base_total
            for category in df.index:
                val = df.loc[category, delta_label]
                if val > 0:
                    bar(delta_pos, val, top, category)
                    top += val
                elif val < 0:
                    bar(delta_pos, val, bot, category)
                    bot += val
            y_max, y_min = max(y_max, base_total, top), min(y_min, bot)
            delta_total = df[delta_label].sum()
            pct = (delta_total / base_total * 100) if base_total else 0.0
            label_y, va = (top, "bottom") if delta_total >= 0 else (bot, "top")
            ax.text(delta_pos, label_y, f"{delta_total:+,.{decimals}f}\n({pct:+.1f} %)",
                    ha="center", va=va, fontsize=REPORT_VALUE_SIZE)
            ax.plot([base_pos + bar_width / 2, delta_pos - bar_width / 2], [base_total, base_total],
                    color="#888888", linestyle="--", linewidth=0.8, zorder=0)

    ax.set_xticks(positions_all)
    ax.set_xticklabels(tick_labels_all, fontsize=7, rotation=25, ha="right", rotation_mode="anchor")
    for yc, year in zip(year_centers, years):
        ax.annotate(str(year), xy=(yc, 0), xycoords=("data", "axes fraction"),
                    xytext=(0, -50), textcoords="offset points",
                    ha="center", va="top", fontsize=9, fontweight="bold")
    ax.set_ylabel(unit)
    panel_title(ax, title)
    span = y_max - y_min  # headroom for the two-line value labels
    ax.set_ylim(y_min - (0.12 * span if y_min < 0 else 0.0), y_max + 0.12 * span)
    ax.axhline(0, color="black", linewidth=0.5)
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        report_legend(ax, handles[::-1], labels[::-1])


def _discharge_twh(r: Run) -> pd.DataFrame:
    """Annual discharge of bulk storage, industrial TES and DSM [TWh] by technology."""
    dis = get_storage_flows(r.results, BULK_STORAGE_TECHS + INDUSTRY_TES_TECHS, "flow_storage_discharge")
    dsm = get_dsm_energy_equivalent(r.results, DSM_ENERGY_STACK_ORDER, COMPARISON_YEARS)
    if not dsm.empty and dsm.values.sum() > 1e-3:
        dis = pd.concat([dis, dsm.sum().rename(INDUSTRY_DSM_LABEL).to_frame().T])
    return dis / 1000.0


def capacity_and_storage(legacy_run: Run, no_flex_run: Run, name: str) -> None:
    empty = pd.Series(dtype=float)
    base_cap = get_capacity(legacy_run.results, POWER_GEN_TECHS, "power")
    nf_cap = get_capacity(no_flex_run.results, POWER_GEN_TECHS, "power")
    base_dis, nf_dis = _discharge_twh(legacy_run), _discharge_twh(no_flex_run)
    gen_by_year, disch_by_year = {}, {}
    for year in COMPARISON_YEARS:
        gen_by_year[year] = stack_ordered(
            base_and_delta_df(base_cap.get(year, empty), nf_cap.get(year, empty), LEGACY, DELTA_LABEL),
            POWER_GEN_STACK_ORDER)
        disch_by_year[year] = base_and_delta_df(base_dis.get(year, empty), nf_dis.get(year, empty),
                                                LEGACY, DELTA_LABEL).reindex(STORAGE_STACK_ORDER).fillna(0.0)

    fig, axes = plt.subplots(2, 1, figsize=(REPORT_WIDTH, 7.0))
    plot_base_and_floating_delta(gen_by_year, "(a) Power generation capacity", "Capacity (GW)", axes[0],
                                 color_map=POWER_GEN_COLOR_MAP)
    plot_base_and_floating_delta(disch_by_year, "(b) Storage discharge", "Annual discharge (TWh)", axes[1],
                                 color_map=STORAGE_COLOR_MAP, decimals=1)
    comma_axis(axes[0])
    fig.tight_layout(h_pad=1.5)
    save_figure(fig, name)
