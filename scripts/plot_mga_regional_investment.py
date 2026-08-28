"""Technology-level regional-CAPEX views for the batch4 v9_0 regional-CAPEX-
by-PERIOD run (data/outputs/euler_outputs_mga/Crystal_Ball_ind_heat_v9_0_
no_flexibility_nodiffusion_2020_7a_5a_interval_3ts_MGA_CAPEX_PERIODS_batch_
bbo_minmax_batch4). These originally complemented that run's own crosseffects
figure (fig4a/b, RATIO-to-baseline view, from the now-deleted plot_mga_
periods_regional_capex.py -- superseded by plot_mga_cum_regional_capex.py's
fig10 and deleted outright, see that script's module docstring); fig7/8
below remain independently useful and still target this same PERIODS run via
the shared loader in mga_capex_periods_common.py. A third, absolute-bnEUR
companion (fig5_regional_investment_absolute, "how much can each region's
own CAPEX actually move, in bnEUR not ratio-to-baseline") was deleted
2026-08-28: its legend was wrong -- passing one color PER REGION into a
single ax.bar(..., label=...) call makes matplotlib's legend swatch take on
just the FIRST region's color (north, blue) for both period entries, even
though the actual bars are west/south/east's own distinct colors -- so the
legend claimed "2030-2039 baseline" was always blue when 3 of 4 regions'
bars for that period were teal/olive/bronze. fig7/8 below use a per-region
color list too, but their legend entries describe a GENERIC light/dark
distinction that holds for every bar regardless of which region's color
illustrates it (see fig7's neutral-swatch fix, same audit), not a claim
about one specific color -- that's the difference that made fig5's legend
actually wrong rather than just illustrative.

fig7 -- the structural "why" for the *wind/PV* component specifically:
technology capacity_limit (input data, constant across years -- verified
directly, not assumed) vs. how much of that limit the baseline (cost-optimal)
design actually uses by 2050. North holds 1,023 of ~1,149 GW (89%) of the
whole model's offshore wind potential and uses only 3.8% of its own share by
2050 -- by far the largest absolute headroom of any region on any of the
three technologies. West and south are the opposite case for photovoltaics
specifically: already at 91%/97% utilisation of their own (smaller) PV
limits.

fig7 alone does NOT explain each region's overall achievable CAPEX range,
though -- west/south's absolute ranges are comparable to (even larger than)
north/east's, which looks like it contradicts fig7's headroom asymmetry.
fig8 resolves this: battery has an INFINITE capacity_limit in every region
(verified directly -- no geographic resource constraint at all, unlike
wind/PV), so it inflates every region's own-axis range by a roughly similar
amount regardless of local renewable potential and swamps the wind/PV signal
in each region's totals. Once battery is subtracted out, wind+PV's own
contribution to the swing IS visibly larger for north (e.g. 248 bnEUR in
2040s) than west/south/east (120-132 bnEUR) -- consistent with fig7 -- it's
just a minority share (7-15%) of a total dominated by a technology fig7
never covered because it isn't geography-constrained in the first place.

fig8 -- the reconciliation: each region's own-axis max delta (needs each VMM
solve's own Results/var_dict.h5, not just the summary polytope.npz's
region-level totals), split into battery / wind+PV / everything else and
shown for all four regions side by side (one stacked bar per region per
period), so the battery-dominance-plus-wind/PV-differentiation story is
visible directly. battery is overwhelmingly the largest single line item
(61-92% of the swing across all 4 regions) -- wind_offshore/wind_onshore/
DAC/electrolysis/heat_pump/BEV/electrode_boiler follow at far smaller
shares.

Usage:
    python scripts/plot_mga_regional_investment.py
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

# Match the rest of the MGA scripts / MT_report_HG's font -- see
# generate_si_figures.py for the rationale.
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["cmr10"],
    "mathtext.fontset": "cm",
    "axes.formatter.use_mathtext": True,
    "axes.unicode_minus": False,
})

from figure_settings import eth_tint
from mga_capex_periods_common import MODEL, PERIODS, REGION_COLOR, REGIONS, RUN_DIR, savefig
from zen_garden import Results

# Single source of truth for region -> node membership: the same JSON the
# MGA run itself was configured from (data/config_mga_axes_capex_periods.json),
# not a hand-copied list that could drift from it.
_CONFIG = json.loads((REPO_ROOT / "data" / "config_mga_axes_capex_periods.json").read_text())
REGION_NODES = {next(iter(d)): next(iter(d.values())) for d in _CONFIG["node_capex_periods"]["nodes"]}


def _solve_path(name: str) -> Path:
    return RUN_DIR / f"{MODEL}_{name}"


def _region_capex_by_tech(r: Results, nodes: list[str], period: tuple[int, int]) -> pd.Series:
    """Sum cost_capex_yearly by technology over `nodes`, restricted to the
    period's own calendar years -- same restriction as MGA's node_capex_period
    axis_value (plot_mga_results.py's axis_value docstring), so this reconciles
    with fig8's own-axis totals rather than a whole-pathway number."""
    capex = r.get_total("cost_capex_yearly")
    capex = capex[capex.index.get_level_values("location").isin(nodes)]
    start, end = period
    capex = capex[[c for c in capex.columns if start <= c <= end]]
    return capex.groupby("technology").sum().sum(axis=1)


# ── fig7: renewable potential headroom by region ───────────────────────────
def fig_renewable_headroom() -> None:
    base_r = Results(path=str(RUN_DIR / MODEL))
    lim = base_r.get_total("capacity_limit")
    lim = lim[lim.index.get_level_values("capacity_type") == "power"]
    cap = base_r.get_total("capacity")
    cap = cap[cap.index.get_level_values("capacity_type") == "power"]

    techs = ["wind_offshore", "wind_onshore", "photovoltaics"]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.8), sharey=False)
    for ax, tech in zip(axes, techs):
        limits, used = [], []
        for r in REGIONS:
            nodes = REGION_NODES[r]
            l = lim[(lim.index.get_level_values("technology") == tech)
                    & (lim.index.get_level_values("location").isin(nodes))]
            c = cap[(cap.index.get_level_values("technology") == tech)
                    & (cap.index.get_level_values("location").isin(nodes))]
            limits.append(l[2050].sum() if not l.empty else 0.0)
            used.append(c[2050].sum() if not c.empty else 0.0)
        limits, used = np.array(limits), np.array(used)
        headroom = limits - used

        x = np.arange(len(REGIONS))
        ax.bar(x, used, color=[REGION_COLOR[r] for r in REGIONS], edgecolor="black", linewidth=0.6, zorder=3)
        ax.bar(x, headroom, bottom=used, color=[eth_tint(REGION_COLOR[r], 0.75) for r in REGIONS],
               edgecolor="black", linewidth=0.6, zorder=3)
        for xi, l, u in zip(x, limits, used):
            pct = 100 * u / l if l else 0.0
            ax.text(xi, l, f"{l:,.0f} GW\n({pct:.0f}% used)", ha="center", va="bottom", fontsize=7.5)
        ax.set_xticks(x)
        ax.set_xticklabels([r.capitalize() for r in REGIONS], fontsize=9.5)
        ax.set_title(tech.replace("_", " "), fontsize=10.5, fontweight="bold")
        ax.set_ylim(0, limits.max() * 1.28)
        ax.grid(axis="y", alpha=0.3)
        if ax is axes[0]:
            ax.set_ylabel("Capacity limit, 2050 (GW)", fontsize=9.5)
            # Manual neutral-gray legend handles, not the bars themselves: each
            # bar is colored per-REGION (see module docstring's legend-audit
            # note), so a handle built from one bar's artist would show only
            # that region's color for a label meant to describe every bar's
            # dark/light distinction, regardless of region.
            ax.legend(handles=[
                Patch(facecolor="#555555", edgecolor="black", label="used by baseline (2050)"),
                Patch(facecolor="#cccccc", edgecolor="black", label="unused headroom"),
            ], fontsize=8, loc="upper right")

    fig.suptitle(
        "Renewable Capacity Potential vs. Baseline Usage by Region (2050)\n"
        "-- north (and, for wind, east) hold the most wind/PV headroom -- see fig8 for how"
        " this fits into each region's overall achievable CAPEX range",
        fontsize=11, fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    savefig(fig, "fig7_renewable_headroom")


# ── fig8: battery vs. wind+PV vs. everything else, all 4 regions ──────────
# fig7 alone doesn't explain why west/south's overall achievable CAPEX range
# looks just as large as north/east's despite having much less wind/PV headroom.
# This decomposes each region's own-axis max delta into battery / wind+PV /
# other, so the resolution is visible directly: battery's capacity_limit is
# INFINITE in every region (verified against capacity_limit directly -- no
# geographic constraint at all), so it dominates 61-92% of every region's
# swing roughly regardless of local renewables, swamping the real but
# smaller wind/PV asymmetry fig7 documents.
_WINDPV_TECHS = ["wind_onshore", "wind_offshore", "photovoltaics"]


def fig_regional_tech_decomposition() -> None:
    base_r = Results(path=str(RUN_DIR / MODEL))

    fig, axes = plt.subplots(1, 2, figsize=(11, 5.5), sharey=False)
    for ax, period in zip(axes, PERIODS):
        start, end = (int(p) for p in period.split("_"))
        x = np.arange(len(REGIONS))
        battery_vals, windpv_vals, other_vals = [], [], []
        for region in REGIONS:
            nodes = REGION_NODES[region]
            max_r = Results(path=str(_solve_path(f"vmm_max_{region}_{period}")))
            b = _region_capex_by_tech(base_r, nodes, (start, end))
            m = _region_capex_by_tech(max_r, nodes, (start, end))
            all_t = b.index.union(m.index)
            delta = m.reindex(all_t, fill_value=0.0) - b.reindex(all_t, fill_value=0.0)
            total = delta.sum()
            battery = delta.get("battery", 0.0)
            windpv = sum(delta.get(t, 0.0) for t in _WINDPV_TECHS)
            battery_vals.append(battery / 1000)
            windpv_vals.append(windpv / 1000)
            other_vals.append((total - battery - windpv) / 1000)
        battery_vals, windpv_vals, other_vals = np.array(battery_vals), np.array(windpv_vals), np.array(other_vals)

        ax.bar(x, battery_vals, color="#7c5ba6", edgecolor="black", linewidth=0.6, label="battery")
        ax.bar(x, windpv_vals, bottom=battery_vals, color="#f0c040", edgecolor="black",
               linewidth=0.6, label="wind + PV")
        ax.bar(x, other_vals, bottom=battery_vals + windpv_vals, color="#999999", edgecolor="black",
               linewidth=0.6, label="everything else")

        total_vals = battery_vals + windpv_vals + other_vals
        for xi, bat, tot in zip(x, battery_vals, total_vals):
            ax.text(xi, tot, f"{tot:,.0f}", ha="center", va="bottom", fontsize=8)
            ax.text(xi, bat / 2, f"{100 * bat / tot:.0f}%", ha="center", va="center",
                    fontsize=7.5, color="white")

        ax.set_xticks(x)
        ax.set_xticklabels([r.capitalize() for r in REGIONS], fontsize=10.5)
        ax.set_title(f"{period.replace('_', '-')}: own-axis max, by technology", fontsize=10.5)
        ax.set_ylabel("$\\Delta$ CAPEX vs. baseline (bn EUR)" if ax is axes[0] else "", fontsize=9.5)
        ax.set_ylim(0, total_vals.max() * 1.12)
        ax.grid(axis="y", alpha=0.3)

    # Every bar reaches roughly the same height in each panel (that's the
    # whole point of the figure), so there's no empty corner for an
    # in-axes legend -- put one shared legend below both panels instead.
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, fontsize=9, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.02))

    fig.suptitle(
        "MGA batch4 (v9_0): Battery vs. Wind+PV vs. Other in Each Region's Own-Axis Swing\n"
        "-- why each region's overall achievable CAPEX range looks similar despite fig7's headroom asymmetry",
        fontsize=11, fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.90))
    savefig(fig, "fig8_regional_tech_decomposition")


def main() -> None:
    fig_renewable_headroom()
    fig_regional_tech_decomposition()


if __name__ == "__main__":
    main()
