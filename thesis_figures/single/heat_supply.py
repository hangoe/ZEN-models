"""Industrial heat supply by technology (thesis Fig. 5 and A2, one presentation figure).

Annual operated output of the industrial boilers and heat pumps [TWh] per modelled year,
stacked by technology. The heat demand is fixed, so every bar has the same height.
"""

import matplotlib.pyplot as plt
import numpy as np

from ..names import CARRIER_COLORS, HEAT_SUPPLY_COLOR_MAP, HEAT_SUPPLY_STACK_ORDER, display_name
from ..results import INDUSTRY_HEAT_TECHS_BOILERS_HP, Run, get_available_years
from ..style import (
    ETH_BLUE,
    ETH_GREY,
    REPORT_WIDTH,
    panel_title,
    report_legend,
    save_figure,
    signed_stacked_bars,
    stack_ordered,
)
from .metrics import output_annual_twh

# Technology groups of the aggregated presentation figure, bottom to top:
# name -> (colour, membership test). The waste boiler (2022 only) counts as fossil.
AGGREGATED_GROUPS = {
    "Fossil boilers": (ETH_GREY, lambda t: t in {
        "natural_gas_boiler_industry", "oil_boiler_industry", "coal_boiler_industry", "waste_boiler_industry"}),
    "Biomass boiler": (CARRIER_COLORS["biomass"], lambda t: t == "biomass_boiler_industry"),
    "Electrode boiler": (CARRIER_COLORS["electrode_boiler"], lambda t: t == "electrode_boiler_industry"),
    "Heat pumps": (ETH_BLUE, lambda t: t.startswith("heat_pump_industry")),
}


def heat_supply(r: Run, name: str) -> None:
    """Heat supply of one scenario, by technology, legend on the right."""
    years = get_available_years(r.results)
    output_df = stack_ordered(output_annual_twh(r, INDUSTRY_HEAT_TECHS_BOILERS_HP),
                              HEAT_SUPPLY_STACK_ORDER, years)
    output_df = output_df[output_df.abs().max(axis=1) > 1e-3]

    fig, ax = plt.subplots(figsize=(REPORT_WIDTH, 3.2))
    x = np.arange(len(output_df.columns))
    top, _ = signed_stacked_bars(ax, output_df, HEAT_SUPPLY_COLOR_MAP, x, width=0.72, label_fn=display_name)
    ax.set_ylim(0, top.max() * 1.03)
    ax.set_xticks(x)
    ax.set_xticklabels([str(y) for y in output_df.columns])
    ax.set_xlim(-0.6, len(x) - 0.4)
    ax.set_ylabel("Industrial heat supply (TWh)")
    handles, labels = ax.get_legend_handles_labels()
    report_legend(ax, handles[::-1], labels[::-1], loc="upper left", bbox_to_anchor=(1.01, 1.0))
    fig.tight_layout()
    save_figure(fig, name)


def heat_supply_aggregated(no_flex_run: Run, full_run: Run, name: str) -> None:
    """Presentation: two scenarios side by side, technologies aggregated to
    AGGREGATED_GROUPS, shared y axis and one legend."""
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.4), sharey=True)
    colors = {g: c for g, (c, _) in AGGREGATED_GROUPS.items()}
    y_max = 0.0
    for letter, ax, r in zip("ab", axes, (no_flex_run, full_run)):
        techs = output_annual_twh(r, INDUSTRY_HEAT_TECHS_BOILERS_HP)
        group_of = {t: [g for g, (_, member) in AGGREGATED_GROUPS.items() if member(t)] for t in techs.index}
        unassigned = [t for t, g in group_of.items() if len(g) != 1]
        if unassigned:
            raise ValueError(f"technologies without exactly one group: {unassigned}")
        df = techs.groupby({t: g[0] for t, g in group_of.items()}).sum()
        df = df.reindex(list(AGGREGATED_GROUPS)).fillna(0.0)[get_available_years(r.results)]
        x = np.arange(len(df.columns))
        top, _ = signed_stacked_bars(ax, df, colors, x, width=0.72)
        y_max = max(y_max, top.max())
        ax.set_xticks(x)
        ax.set_xticklabels([str(y) for y in df.columns])
        ax.set_xlim(-0.6, len(x) - 0.4)
        panel_title(ax, f"({letter}) {r.label}")
    axes[0].set_ylim(0, y_max * 1.03)
    axes[0].set_ylabel("Industrial heat supply (TWh)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.tight_layout()
    report_legend(axes[1], handles[::-1], labels[::-1])
    save_figure(fig, name)
