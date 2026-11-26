"""Emissions by source and cumulative emissions vs. carbon budget (thesis Fig. A1).

ZEN-Europe-Legacy vs. ZEN-Europe-No-Flex. (a) Annual emissions in the snapshot years,
split into fuel combustion (by carrier) and process emissions and capture (by
technology); each bar's label is the net total. (b) Cumulative emissions
(carbon_emissions_cumulative, which also counts the years between the modelled years)
against each run's carbon budget; the shaded area is above the budget and not yet repaid
at the end of the horizon.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from ..names import CARRIER_COLORS, SECTOR_COLORS, display_name
from ..results import Run, get_available_years, get_emissions_by_carrier, get_emissions_by_technology
from ..style import (
    ETH_BLUE,
    ETH_GREY,
    REPORT_WIDTH,
    comma_axis,
    eth_tint,
    panel_title,
    report_legend,
    save_figure,
    signed_stacked_bars,
)
from .scenarios import COMPARISON_YEARS

# Stack order bottom to top; "c:" carrier (combustion), "t:" technology (process,
# capture). Technologies in tints, so they read as distinct from the carriers.
EMISSIONS_COLOR_MAP = {
    "c:hard_coal": CARRIER_COLORS["hard_coal"],
    "c:lignite": CARRIER_COLORS["lignite"],
    "c:crude_oil": CARRIER_COLORS["oil"],
    "c:natural_gas": CARRIER_COLORS["natural_gas"],
    "c:lng": CARRIER_COLORS["lng"],
    "c:waste": CARRIER_COLORS["waste"],
    "t:BF_BOF": SECTOR_COLORS["steel"],
    "t:EAF": eth_tint(SECTOR_COLORS["steel"], 0.45),
    "t:NG_DRI": eth_tint(SECTOR_COLORS["steel"], 0.7),
    "t:cement_kiln": eth_tint(SECTOR_COLORS["cement"], 0.7),
    "t:glass_production": eth_tint(SECTOR_COLORS["glass"], 0.45),
    "t:ceramic_production": eth_tint(SECTOR_COLORS["glass"], 0.75),
    "t:carbon_storage": CARRIER_COLORS["carbon_storage"],
}
NEGLIGIBLE_TECHS = ["H2_DRI"]  # ~0 emissions in every run and year


def _year_series(results, component: str) -> dict[int, float]:
    return {int(k): float(v) for k, v in results.get_total(component).items()}


def emissions_and_budget(legacy_run: Run, no_flex_run: Run, name: str) -> None:
    fig_runs = [legacy_run, no_flex_run]
    years_common = sorted(set.intersection(*(set(get_available_years(r.results)) for r in fig_runs)))
    panel_a_years = [y for y in COMPARISON_YEARS if y in years_common]

    # (a) composition per run and year, grouped scenario-major / year-minor
    comp = {}
    for run in fig_runs:
        for year in panel_a_years:
            carrier = get_emissions_by_carrier(run.results, year)
            tech = get_emissions_by_technology(run.results, year).drop(NEGLIGIBLE_TECHS, errors="ignore")
            comp[(run.label, year)] = pd.concat([carrier.rename(lambda c: f"c:{c}"),
                                                 tech.rename(lambda t: f"t:{t}")])
    composition = pd.DataFrame(comp).fillna(0.0)
    composition = composition[composition.abs().max(axis=1) > 1e-3]
    order = [k for k in EMISSIONS_COLOR_MAP if k in composition.index] + \
        [k for k in composition.index if k not in EMISSIONS_COLOR_MAP]
    composition = composition.loc[order]
    colors = {k: EMISSIONS_COLOR_MAP.get(k, eth_tint(ETH_GREY, 0.7)) for k in composition.index}

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(REPORT_WIDTH, 6.8), gridspec_kw={"height_ratios": [1.15, 1]})
    n_years = len(panel_a_years)
    x = np.array([i * (n_years + 1) + j for i in range(len(fig_runs)) for j in range(n_years)], dtype=float)
    top, bot = signed_stacked_bars(ax1, composition, colors, x, width=0.8,
                                   label_fn=lambda k: display_name(k.split(":", 1)[1]))
    net = composition.sum().to_numpy()
    for xi, t, n in zip(x, top, net):
        ax1.text(xi, t + 0.01 * top.max(), f"{n:,.0f}".replace("-", "−"), ha="center", va="bottom",
                 fontsize=6.5)
    ax1.axhline(0, color="black", linewidth=0.6)
    ax1.set_xticks(x)
    ax1.set_xticklabels([str(y) for _ in fig_runs for y in panel_a_years], fontsize=7)
    for i, run in enumerate(fig_runs):
        ax1.annotate(run.label, xy=(i * (n_years + 1) + (n_years - 1) / 2, 0),
                     xycoords=("data", "axes fraction"), xytext=(0, -16), textcoords="offset points",
                     ha="center", va="top", fontsize=8)
    ax1.set_ylim(min(bot.min(), 0) * 1.1, top.max() * 1.1)
    ax1.set_ylabel("Emissions (Mt CO$_2$-eq/a)")
    comma_axis(ax1)
    panel_title(ax1, "(a) Emissions by source")
    h, lab = ax1.get_legend_handles_labels()
    report_legend(ax1, h[::-1], lab[::-1])

    # (b) cumulative emissions vs. each run's own carbon budget
    labels = [run.label for run in fig_runs]
    cum = {run.label: _year_series(run.results, "carbon_emissions_cumulative") for run in fig_runs}
    budget = {run.label: float(run.results.get_total("carbon_emissions_budget").iloc[0]) for run in fig_runs}
    years = sorted(cum[no_flex_run.label])
    vals = {lab: [c[y] for y in years] for lab, c in cum.items()}
    color = {legacy_run.label: ETH_GREY, no_flex_run.label: ETH_BLUE}
    for lab in labels:
        over = np.array([v > budget[lab] for v in vals[lab]])
        ax2.fill_between(years, vals[lab], budget[lab], where=over, color=color[lab],
                         alpha=0.12, interpolate=True, linewidth=0)
    line_style = {legacy_run.label: dict(marker="o", linestyle="-"),
                  no_flex_run.label: dict(marker="s", linestyle="-")}
    for lab in labels:
        ax2.plot(years, vals[lab], color=color[lab], linewidth=1.2, markersize=3, **line_style[lab])
        ax2.axhline(budget[lab], color=color[lab], linestyle="--", linewidth=1.0)

    ax2.set_ylabel("Cumulative emissions (Mt CO$_2$-eq)")
    ax2.set_ylim(top=max(max(v) for v in vals.values()) * 1.1)
    comma_axis(ax2)
    ax2.grid(alpha=0.3, linewidth=0.5)
    panel_title(ax2, "(b) Cumulative emissions and carbon budget")
    handles = [Line2D([], [], color=color[lab], linewidth=1.2, label=lab, **line_style[lab], markersize=3)
               for lab in labels]
    handles += [Line2D([], [], color="black", linewidth=1.2, label="Cumulative emissions"),
                Line2D([], [], color="black", linewidth=1.0, linestyle="--", label="Carbon budget"),
                Patch(facecolor="black", alpha=0.12, label="Above own budget,\nnot yet repaid")]
    report_legend(ax2, handles)
    fig.tight_layout(h_pad=1.5)
    save_figure(fig, name)
