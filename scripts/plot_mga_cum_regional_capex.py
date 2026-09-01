"""Baseline vs true own-axis max/min for the batch4 v9_0 regional-CUMULATIVE-
CAPEX VMM run, "share" normalisation (data/outputs/euler_outputs_mga/
Crystal_Ball_ind_heat_v9_0_no_flexibility_nodiffusion_2020_7a_5a_interval_3ts_MGA_CAPEX_CUM_batch_bbo_share_batch4).

Context: this is the cumulative-CAPEX sibling of the (now-deleted) PERIODS
run analysis. Axes come from config_mga_axes_capex_cum.json
(node_capex_cumulative): 4 node clusters (north/west/south/east) x 2
until_years ([2040], [2050]) = 8 node_capex_cumulative axes, plus
net_present_cost (9 axes total -- "include_cost": true). Each axis sums that
region's cost_capex_yearly over every model year UP TO AND INCLUDING its own
until_year (so the until_2050 axis is a superset of the until_2040 axis for
the same region -- these are cumulative totals, not the disjoint calendar
periods the PERIODS run used).

This run also uses "share" normalisation rather than "minmax" (see
polytope_io.py's module docstring): scale is a fixed reference total
(the baseline's total capex across every node/year, rounded to one
significant figure) shared by every node_capex_cumulative axis, rather than
each axis's own near-optimal [min, max] range. That only affects how the
solver's search directions were scaled while exploring -- every physical
value plotted here comes from poly.to_phys(), so the ratios below are
unaffected by which normalisation convention produced this run's polytope.

Its own polytope.npz (built by solve_axis_bounds/solve_extreme_lps, see
plugin.py) already carries the physical value of EVERY axis at EVERY solved
point, including the 8 VMM solves (4 regions x 2 until_years x max/min) and
the baseline (z_star) -- no need to reload each point's own Results h5
files individually.

This script reads that polytope.npz directly and produces fig10/fig11.
Each own-axis VMM solve is still a full ZEN-garden solve over the WHOLE
pathway, so it moves every OTHER axis too -- including that region's OWN
other-until_year axis (e.g. does maxing north's cumulative CAPEX by 2040
crowd out or pull forward north's cumulative CAPEX by 2050?) and every
other region's axes at both horizons. fig10's cross-effects cell value =
that row axis's value under that column's solve, as a ratio to baseline
(1.0 = no change); log2-scaled color (RdBu_r, centred at 0) since ratios
range from ~0 (axis driven to zero) to very large (the column's own target
axis) -- a linear scale would wash out everything but the diagonal.

fig10_temporal_crosseffects answers a genuinely TEMPORAL question: does
pushing a region's CAPEX at one horizon (2040 or 2050) affect the SAME
region differently at the OTHER horizon than it affects OTHER regions, and
does that differ by which horizon was pushed? It merges both until_years'
16 columns (4 regions x 2 until_years pushed x 2 senses) into ONE matrix
against all 9 shared-frame axes (rows), grouped by region then year so
each region's own 2x2 block of self-effects sits together, with an
in-between divider separating the two until_years -- so a row can be
compared side-by-side across "same region, different horizon pushed"
columns directly. (An earlier version of this script produced fig9a/b: the
same 16 VMM solves, split one-year-per-figure instead of merged -- deleted
outright, 2026-08-28, once fig10 made it redundant: fig10 is a strict
superset of that data, in the one merged layout that actually answers the
temporal question fig9a/b's split couldn't.)

fig11_temporal_range_absolute complements fig10 with the simpler "same
region, over time" question alone: each region's own achievable range
(baseline + VMM min/max, in bnEUR not ratio -- see plot_mga_regional_
investment.py's module docstring for why absolute beats ratio here, and
for a legend bug this project hit doing exactly this: passing one color
PER REGION into a single ax.bar(..., label=...) call makes the legend
swatch show only the FIRST region's color for every label, regardless of
which region's bar it's meant to describe -- fig11 fixes this the same way
fig7 there did, with neutral-gray Patch legend handles instead of the
per-region-colored bar artists) at until_2040 vs until_2050, i.e. how much
of a region's total flexibility is already locked in by 2040 vs still
added in the final decade.

Usage:
    python scripts/plot_mga_cum_regional_capex.py
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.colors import TwoSlopeNorm
from matplotlib.patches import Patch

from plots.figure_settings import SCENARIO_PALETTE, apply_font_mode, eth_tint

# Match the rest of the MGA scripts / MT_report_HG's font -- see
# figure_settings.FONT_MODE for the rationale and for the one-flag toggle
# that switches every figure script in this repo at once.
apply_font_mode()
from plots.mga_capex_periods_common import FIGURES_DIR, savefig
from zen_garden_plugins.mga.polytope_io import load_polytope

RUN_DIR = (
    REPO_ROOT / "data" / "outputs" / "euler_outputs_mga"
    / "Crystal_Ball_ind_heat_v9_0_no_flexibility_nodiffusion_2020_7a_5a_interval_3ts_MGA_CAPEX_CUM_batch_bbo_share_batch4"
)
MODEL = "Crystal_Ball_ind_heat_v9_0_no_flexibility_nodiffusion"
POLY_PATH = RUN_DIR / f"{MODEL}_batch_summary" / "polytope.npz"

REGIONS = ["north", "west", "south", "east"]
UNTIL_YEARS = ["until_2040", "until_2050"]
REGION_COLOR = dict(zip(REGIONS, SCENARIO_PALETTE))


def load_batch4_data():
    """(poly, names, units, axis_idx, origin, phys, base): the loaded
    Polytope itself (poly.A/b/X -- needed for rejection sampling/max_separation
    in plot_mga_results.py), the 9 axes in poly.meta order, their units, a
    name->index map, each solved point's origin label, every solved point's
    physical-unit vector (poly.X is stored normalised, see polytope_io.py --
    to_phys converts back), and the baseline (z_star) vector."""
    if not POLY_PATH.exists():
        raise FileNotFoundError(f"batch4 polytope not found at {POLY_PATH}")
    poly = load_polytope(POLY_PATH)
    names = [a["name"] for a in poly.meta["axes"]]
    units = {a["name"]: a["unit"] for a in poly.meta["axes"]}
    axis_idx = {n: i for i, n in enumerate(names)}
    origin = list(poly.point_origin)
    phys = np.array([poly.to_phys(x) for x in poly.X])
    base = phys[origin.index("z_star")]
    print(f"  loaded {len(origin)} points ({sum(1 for o in origin if o.startswith(('max:', 'min:')))} "
          f"own-axis VMM solves) from {POLY_PATH.relative_to(REPO_ROOT)}")
    return poly, names, units, axis_idx, origin, phys, base


# ── fig10: temporal cross-effects -- both until_years merged into one matrix
# (see module docstring for why this replaced an earlier fig9a/b split, one
# year per figure). Merging both years' columns into one matrix (grouped by
# region, then until_year, then sense) makes the temporal comparison direct:
# a row can't be compared side-by-side across "same region, different
# horizon pushed" columns when those columns live in separate figures;
# within each region's 4-column block, the left pair (2040 max/min) and
# right pair (2050 max/min) sit next to each other, separated by a thin
# dashed divider; a thick solid divider separates regions. Reading down a row across one
# region's block shows that row axis's full temporal response profile to
# that one region's investment; reading across regions at a fixed row shows
# the temporal cross-region spillover this project wanted to compare.
def fig_temporal_crosseffects(names, units, axis_idx, origin, phys, base) -> None:
    columns = [(region, until_year, sense)
               for region in REGIONS for until_year in UNTIL_YEARS for sense in ("max", "min")]
    col_labels = [f"{region}\n'{until_year[-2:]} {sense}" for region, until_year, sense in columns]
    row_axes = names
    matrix = np.array([
        [phys[origin.index(f"{sense}:{region}_{until_year}")][axis_idx[row]] / base[axis_idx[row]]
         for region, until_year, sense in columns]
        for row in row_axes
    ])
    is_own = np.array([[row == f"{region}_{until_year}" for region, until_year, sense in columns]
                        for row in row_axes])
    own_ratio = np.array([matrix[axis_idx[f"{region}_{until_year}"], j]
                           for j, (region, until_year, sense) in enumerate(columns)])
    own_log = np.log2(np.clip(own_ratio, 1e-6, None))

    cross_matrix = np.where(is_own, np.nan, matrix)
    log_cross = np.log2(np.clip(cross_matrix, 1e-6, None))
    vmax_cross = max(0.15, np.nanmax(np.abs(log_cross)))

    cross_width_in = 0.75 * len(columns) + 2.5
    own_width_in = 0.5 * cross_width_in
    fig, (ax_own, ax_cross) = plt.subplots(
        1, 2, figsize=(own_width_in + cross_width_in + 1.5, 0.5 * len(row_axes) + 2),
        gridspec_kw={"width_ratios": [own_width_in, cross_width_in]},
    )

    bar_colors = [REGION_COLOR[region] if sense == "max" else eth_tint(REGION_COLOR[region], 0.5)
                  for region, until_year, sense in columns]
    ax_own.bar(range(len(columns)), own_log, color=bar_colors, edgecolor="black", linewidth=0.6)
    ax_own.axhline(0, color="black", lw=1)
    for j, v in enumerate(own_ratio):
        ax_own.text(j, own_log[j], f"{v:.2f}x", ha="center",
                    va="bottom" if own_log[j] >= 0 else "top", fontsize=7)
    ax_own.set_xticks(range(len(columns)))
    ax_own.set_xticklabels(col_labels, fontsize=7.5)
    ax_own.set_ylabel("own-axis value / baseline (log$_2$)", fontsize=9)
    ax_own.set_title("Own-axis flexibility, both horizons", fontsize=10, fontweight="bold")
    ax_own.grid(axis="y", alpha=0.3)

    im = ax_cross.imshow(log_cross, cmap="RdBu_r", norm=TwoSlopeNorm(vmin=-vmax_cross, vcenter=0, vmax=vmax_cross),
                          aspect="auto")
    ax_cross.set_xticks(range(len(columns)))
    ax_cross.set_xticklabels(col_labels, fontsize=7.5)
    ax_cross.set_yticks(range(len(row_axes)))
    ax_cross.set_yticklabels([r.replace("_", " ") for r in row_axes], fontsize=9)
    for i, row in enumerate(row_axes):
        for j, (region, until_year, sense) in enumerate(columns):
            if is_own[i, j]:
                ax_cross.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor="#dddddd",
                                                  edgecolor="black", hatch="//", linewidth=0.6))
                continue
            v = matrix[i, j]
            ax_cross.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=6.5,
                          color="black" if abs(log_cross[i, j]) < vmax_cross * 0.6 else "white")
    ax_cross.set_xticks(np.arange(-0.5, len(columns), 1), minor=True)
    ax_cross.set_yticks(np.arange(-0.5, len(row_axes), 1), minor=True)
    ax_cross.grid(which="minor", color="white", linewidth=1)
    ax_cross.tick_params(which="minor", length=0)
    # Region dividers (thick, every 4 columns / 2 rows) and until_year
    # dividers within each region (thin dashed, every 2 columns) -- the
    # whole point of this merged layout is to make these blocks comparable.
    for ax in (ax_own, ax_cross):
        for k in range(1, len(REGIONS)):
            ax.axvline(4 * k - 0.5, color="black", linewidth=1.4)
        for k in range(0, len(REGIONS) * 2):
            if k % 2 == 1:
                ax.axvline(2 * k - 0.5, color="black", linewidth=0.6, linestyle="--", alpha=0.6)
    for k in range(1, len(REGIONS)):
        ax_cross.axhline(2 * k - 0.5, color="black", linewidth=1.4)
    cbar = fig.colorbar(im, ax=ax_cross, fraction=0.03, pad=0.02)
    cbar.set_label("value / baseline (log$_2$ scale; hatched = own-axis)", fontsize=8)
    ax_cross.set_title("Cross-axis response, both horizons (dashed = until-year boundary within a region)",
                        fontsize=9.5, fontweight="bold")

    fig.suptitle(
        "MGA batch4 share (v9_0): Temporal Cross-Effects -- until 2040 vs. until 2050 Pushes, Merged",
        fontsize=11, fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    savefig(fig, "fig10_temporal_crosseffects")


# ── fig11: same-region temporal growth, absolute bnEUR ────────────────────
# Companion to fig10's cross-region view: for each region alone, how much of
# its own achievable CAPEX range is already present by 2040 vs still added
# in the 2041-2050 decade. Absolute bnEUR, not ratio-to-baseline (see module
# docstring for why, and for a legend bug fixed here: the bars below are
# colored PER REGION, but the legend below them uses manual neutral-gray
# Patch handles rather than the bar artists themselves -- a handle built
# from ax.bar(..., color=[...4 different colors...], label=...) would show
# only the FIRST region's (north's) color for a label meant to describe
# every region's bar, which is what plot_mga_regional_investment.py's
# deleted fig5 got wrong).
def fig_temporal_range_absolute(axis_idx, origin, phys, base) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    x = np.arange(len(REGIONS))
    width = 0.34

    for i, until_year in enumerate(UNTIL_YEARS):
        offset = (i - 0.5) * (width + 0.05)
        baseline = np.array([base[axis_idx[f"{r}_{until_year}"]] for r in REGIONS]) / 1000
        lo = np.array([phys[origin.index(f"min:{r}_{until_year}")][axis_idx[f"{r}_{until_year}"]]
                       for r in REGIONS]) / 1000
        hi = np.array([phys[origin.index(f"max:{r}_{until_year}")][axis_idx[f"{r}_{until_year}"]]
                       for r in REGIONS]) / 1000
        colors = [REGION_COLOR[r] if i == 0 else eth_tint(REGION_COLOR[r], 0.45) for r in REGIONS]

        ax.bar(x + offset, baseline, width, color=colors, edgecolor="black", linewidth=0.6, zorder=3)
        yerr = np.vstack([baseline - lo, hi - baseline])
        ax.errorbar(x + offset, baseline, yerr=yerr, fmt="none", ecolor="black",
                     capsize=4, linewidth=1.2, zorder=4)
        for xi, l, h in zip(x + offset, lo, hi):
            ax.text(xi, h, f"{h:,.0f}", ha="center", va="bottom", fontsize=7)
            ax.text(xi, l, f"{l:,.0f}", ha="center", va="top", fontsize=7)

    ax.set_xticks(x)
    ax.set_xticklabels([r.capitalize() for r in REGIONS], fontsize=11)
    ax.set_ylabel("Cumulative regional CAPEX by that year (bn EUR)", fontsize=10)
    ax.set_title(
        "MGA batch4 share (v9_0): Absolute Cumulative CAPEX by Horizon -- Baseline and Achievable Range\n"
        "(same VMM solves as fig10, in bnEUR -- how much of each region's own flexibility is already\n"
        "locked in by 2040 vs. still added in the final decade)",
        fontsize=11, fontweight="bold",
    )
    ax.legend(handles=[
        Patch(facecolor=shade, edgecolor="black", label=f"cumulative by {until_year[-4:]}, baseline")
        for until_year, shade in zip(UNTIL_YEARS, ("#555555", "#bbbbbb"))
    ], fontsize=9, loc="upper left")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    savefig(fig, "fig11_temporal_range_absolute")


def main() -> None:
    poly, names, units, axis_idx, origin, phys, base = load_batch4_data()
    fig_temporal_crosseffects(names, units, axis_idx, origin, phys, base)
    fig_temporal_range_absolute(axis_idx, origin, phys, base)


if __name__ == "__main__":
    main()
