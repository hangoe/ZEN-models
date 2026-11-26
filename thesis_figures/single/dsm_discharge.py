"""Annual DSM discharge by product, optimistic vs. pessimistic DSM categories (thesis Fig. A4).

Charge and discharge are identical (no storage losses), so only the discharge is shown.
Ammonia and methanol are stored as energy (GWh) and converted to kt with their lower
heating value, so all products share one unit.
"""

import matplotlib.pyplot as plt
import numpy as np

from ..names import SECTOR_COLORS, display_name
from ..results import INDUSTRY_DSM_TECHS, Run, get_available_years, get_storage_flows
from ..style import REPORT_WIDTH, comma_axis, panel_title, report_legend, save_figure, signed_stacked_bars
from .metrics import DSM_ENERGY_CARRIER_TECHS
from .scenarios import FULL, NO_TES_DSM_PESS

# Lower heating values [MWh/t]; 1 GWh / (MWh/t) = 1 kt.
DSM_LHV_MWH_PER_T = {"ammonia_DSM": 18.6 / 3.6,    # 18.6 MJ/kg
                     "methanol_DSM": 19.9 / 3.6}   # 19.9 MJ/kg
# Stack order, by sector group: steel, cement, chemicals, glass and ceramics, paper, food.
PRODUCT_ORDER = ["primary_steel_DSM", "secondary_steel_DSM", "clinker_DSM", "ammonia_DSM", "methanol_DSM",
                 "olefin_DSM", "glass_DSM", "ceramic_DSM", "paper_DSM", "food_DSM"]


def dsm_discharge_by_product(full_run: Run, pessimistic_run: Run, name: str) -> None:
    runs = {FULL: full_run, NO_TES_DSM_PESS: pessimistic_run}
    titles = {FULL: f"(a) Optimistic DSM categories ({FULL})",
              NO_TES_DSM_PESS: f"(b) Pessimistic DSM categories ({NO_TES_DSM_PESS})"}
    color_map = {t: SECTOR_COLORS[t.replace("_DSM", "")] for t in INDUSTRY_DSM_TECHS}

    def label_fn(t: str) -> str:
        return display_name(t) + ("*" if t in DSM_ENERGY_CARRIER_TECHS else "")

    dfs = []
    for run in runs.values():
        r = run.results
        df = get_storage_flows(r, INDUSTRY_DSM_TECHS, "flow_storage_discharge")
        df = df.reindex(columns=get_available_years(r)).fillna(0.0)
        for t, mwh_per_t in DSM_LHV_MWH_PER_T.items():
            if t in df.index:
                df.loc[t] = df.loc[t] / mwh_per_t
        dfs.append(df)
    # products without discharge in both scenarios are dropped
    keep = [t for t in PRODUCT_ORDER if any(t in d.index and d.loc[t].abs().max() > 1e-6 for d in dfs)]
    dfs = [d.reindex(keep).fillna(0.0) for d in dfs]

    fig, axes = plt.subplots(2, 1, figsize=(REPORT_WIDTH, 5.2), sharex=True)
    x = np.arange(len(dfs[0].columns))
    tops = []
    for ax, df, label in zip(axes, dfs, runs):
        top, _ = signed_stacked_bars(ax, df, color_map, x, width=0.72, label_fn=label_fn)
        tops.append(top.max())
        panel_title(ax, titles[label])
        ax.set_ylabel("DSM discharge (kt/a)")
        comma_axis(ax)
    for ax in axes:
        ax.set_ylim(0, max(tops) * 1.05)
    axes[-1].set_xticks(x)
    axes[-1].set_xticklabels([str(y) for y in dfs[0].columns])
    handles, labels = axes[0].get_legend_handles_labels()
    report_legend(axes[0], handles[::-1], labels[::-1])
    axes[1].text(1.01, 0.0, "* converted from GWh\n   with the lower\n   heating value",
                 transform=axes[1].transAxes, fontsize=7, va="bottom", ha="left")
    fig.tight_layout()
    save_figure(fig, name)
