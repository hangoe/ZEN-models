"""Baseline vs true own-axis max/min for the batch4 v9_0 regional-CUMULATIVE-
CAPEX VMM run, "share" normalisation (data/outputs/euler_outputs_mga/
Crystal_Ball_ind_heat_v9_0_no_flexibility_nodiffusion_2020_7a_5a_interval_3ts_MGA_CAPEX_CUM_batch_bbo_share_batch4_tol002).

As of 2026-09-03, RUN_DIR points at the tolerance_explore=0.02 re-run of this
same batch4/share run (task_id 15's retry, task_id 17 -- see
plot_mga_results.py's module docstring for the full failure/retry history),
not the original tolerance_explore=0.01 batch_bbo_share_batch4 (task_id 10).
Only the VMM own-axis max/min bound solves (max:<axis>/min:<axis>, used by
every figure below) and the baseline (z_star) are affected by which of these
two runs is loaded -- both were run with the same axis set/config, so the
own-axis bound solves are the same kind of query either way. What differs is
the "iterate" points (fig12's violin overlay): 892 of them here (223
outer iterations x batch_size=4) instead of the old run's 24 (6 x 4).

Context: this is the cumulative-CAPEX sibling of the (now-deleted) PERIODS
run analysis. Axes come from config_mga_axes_capex_cum.json
(node_capex_cumulative): 4 node clusters (north/west/south/east) x 3
until_years ([2030, 2040, 2050] as of the tol002 run -- the original
batch4_share run only had [2040, 2050]) = 12 node_capex_cumulative axes, plus
net_present_cost (13 axes total -- "include_cost": true). Each axis sums that
region's cost_capex_yearly over every model year UP TO AND INCLUDING its own
until_year (so the until_2050 axis is a superset of until_2040, itself a
superset of until_2030, for the same region -- these are cumulative totals,
not the disjoint calendar periods the PERIODS run used). Every figure below
is written in terms of len(UNTIL_YEARS) (see that constant's own comment),
so a future change to the horizon set needs no further code changes here.

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
point, including the 12 VMM solves (4 regions x 3 until_years x max/min) and
the baseline (z_star) -- no need to reload each point's own Results h5
files individually.

This script reads that polytope.npz directly and produces fig10/fig11/fig12.
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
pushing a region's CAPEX at one horizon (2030, 2040 or 2050) affect the SAME
region differently at another horizon than it affects OTHER regions, and
does that differ by which horizon was pushed? It merges every until_year's
columns (4 regions x len(UNTIL_YEARS) until_years pushed x 2 senses -- 24 as
of the tol002 run's 3 horizons, was 16 under the original 2-horizon
batch4_share run) into ONE matrix against every shared-frame axis (rows, 13
as of tol002), grouped by region then year so each region's own block of
self-effects sits together, with in-between dividers separating each
until_year -- so a row can be compared side-by-side across "same region,
different horizon pushed" columns directly. (An earlier version of this
script produced fig9a/b: the same VMM solves, split one-year-per-figure
instead of merged -- deleted outright, 2026-08-28, once fig10 made it
redundant: fig10 is a strict superset of that data, in the one merged layout
that actually answers the temporal question fig9a/b's split couldn't.)

fig11_temporal_range_absolute complements fig10 with the simpler "same
region, over time" question alone: each region's own achievable range
(baseline + VMM min/max, in bnEUR not ratio -- see plot_mga_regional_
investment.py's module docstring for why absolute beats ratio here, and
for a legend bug this project hit doing exactly this: passing one color
PER REGION into a single ax.bar(..., label=...) call makes the legend
swatch show only the FIRST region's color for every label, regardless of
which region's bar it's meant to describe -- fig11 fixes this the same way
fig7 there did, with neutral-gray Patch legend handles instead of the
per-region-colored bar artists) across until_2030/until_2040/until_2050,
i.e. how much of a region's total flexibility is already locked in by 2030,
how much more accrues through 2040, and how much is still added in the
final decade to 2050.

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
    / "Crystal_Ball_ind_heat_v9_0_no_flexibility_nodiffusion_2020_7a_5a_interval_3ts_MGA_CAPEX_CUM_batch_bbo_share_batch4_tol002"
)
MODEL = "Crystal_Ball_ind_heat_v9_0_no_flexibility_nodiffusion"
POLY_PATH = RUN_DIR / f"{MODEL}_batch_summary" / "polytope.npz"

REGIONS = ["north", "west", "south", "east"]
# As of the tol002 run (2026-09-03), config_mga_axes_capex_cum.json's
# until_years is [2030, 2040, 2050] -- a third horizon added on top of the
# original [2040, 2050] pair every figure below used to assume. Every layout
# below (column/row counts, divider spacing, bar offsets, color/legend
# shading) is written in terms of len(UNTIL_YEARS), so this list is the only
# thing that needs to change if the horizon set changes again.
UNTIL_YEARS = ["until_2030", "until_2040", "until_2050"]
REGION_COLOR = dict(zip(REGIONS, SCENARIO_PALETTE))


def _horizon_tints(n: int) -> np.ndarray:
    """n evenly-spaced tint fractions from 0 (full color, earliest horizon)
    to 0.55 (lightest, latest horizon) -- shared by fig11/fig12's per-region
    bars (tinting REGION_COLOR) and their legend swatches (tinting a neutral
    gray), so the legend's dark-to-light progression always matches the
    bars' own. n=1 degenerates to a single full-color entry."""
    return np.linspace(0, 0.55, n) if n > 1 else np.zeros(1)


def load_batch4_data():
    """(poly, names, units, axis_idx, origin, phys, base): the loaded
    Polytope itself (poly.A/b/X -- needed for rejection sampling/max_separation
    in plot_mga_results.py), the axes (13 as of the tol002 run, see
    UNTIL_YEARS) in poly.meta order, their units, a
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
    ax_own.set_title("Own-axis flexibility, all horizons", fontsize=10, fontweight="bold")
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
    # Region dividers (thick, every len(UNTIL_YEARS)*2 columns / len(UNTIL_YEARS)
    # rows) and until_year dividers within each region (thin dashed, every 2
    # columns -- one per max/min sense pair) -- the whole point of this merged
    # layout is to make these blocks comparable. col_block/row_block generalize
    # the old hardcoded "4 columns"/"2 rows" (both were len(UNTIL_YEARS)==2
    # special cases) to any number of horizons.
    col_block = len(UNTIL_YEARS) * 2
    row_block = len(UNTIL_YEARS)
    for ax in (ax_own, ax_cross):
        for k in range(1, len(REGIONS)):
            ax.axvline(col_block * k - 0.5, color="black", linewidth=1.4)
        for r in range(len(REGIONS)):
            for h in range(1, len(UNTIL_YEARS)):
                ax.axvline(r * col_block + h * 2 - 0.5, color="black", linewidth=0.6,
                           linestyle="--", alpha=0.6)
    for k in range(1, len(REGIONS)):
        ax_cross.axhline(row_block * k - 0.5, color="black", linewidth=1.4)
    cbar = fig.colorbar(im, ax=ax_cross, fraction=0.03, pad=0.02)
    cbar.set_label("value / baseline (log$_2$ scale; hatched = own-axis)", fontsize=8)
    ax_cross.set_title("Cross-axis response, all horizons (dashed = until-year boundary within a region)",
                        fontsize=9.5, fontweight="bold")

    horizon_years = ", ".join(uy[-4:] for uy in UNTIL_YEARS)
    fig.suptitle(
        f"MGA batch4 share tol=0.02 (v9_0): Temporal Cross-Effects -- until {horizon_years} Pushes, Merged",
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
    n = len(UNTIL_YEARS)
    gap = 0.05
    width = (0.85 - (n - 1) * gap) / n
    tints = _horizon_tints(n)

    for i, until_year in enumerate(UNTIL_YEARS):
        offset = (i - (n - 1) / 2) * (width + gap)
        baseline = np.array([base[axis_idx[f"{r}_{until_year}"]] for r in REGIONS]) / 1000
        lo = np.array([phys[origin.index(f"min:{r}_{until_year}")][axis_idx[f"{r}_{until_year}"]]
                       for r in REGIONS]) / 1000
        hi = np.array([phys[origin.index(f"max:{r}_{until_year}")][axis_idx[f"{r}_{until_year}"]]
                       for r in REGIONS]) / 1000
        colors = [REGION_COLOR[r] if tints[i] == 0 else eth_tint(REGION_COLOR[r], tints[i]) for r in REGIONS]

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
        "Absolute Cumulative CAPEX by Horizon Year and Region",
        fontsize=11, fontweight="bold",
    )
    ax.legend(handles=[
        Patch(facecolor=eth_tint("#333333", t) if t else "#333333", edgecolor="black",
              label=f"cumulative by {until_year[-4:]}, baseline")
        for until_year, t in zip(UNTIL_YEARS, tints)
    ], fontsize=9, loc="upper left")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    savefig(fig, "fig11_temporal_range_absolute")


# ── fig12: same-region temporal growth, bars + violin of every actual point ─
# Same bars/whiskers as fig11 (baseline bar, own-axis min/max errorbar), plus
# a violin (KDE) of every OTHER actually-computed point layered on top -- the
# batch BBO "iterate" solves (892 of them as of the tol002 run, see module
# docstring) alongside the 24 own-axis VMM extremes and the baseline, each
# one a genuine ZEN-garden solve that is certainly feasible and near-optimal.
# Deliberately NOT hit-and-run samples from the outer polytope (poly.A @ x <=
# poly.b is only an outer relaxation of the true near-optimal region -- see
# fig2's inner-hull rejection sampling in plot_mga_results.py for why that
# gap matters): every point behind this violin is one of this run's own
# solves, so it is certainly inside the true near-optimal region, not just
# the outer approximation of it. A violin (matplotlib's own KDE) replaced an
# earlier version of this figure that scattered every point directly
# (jittered, so overlapping dots were visible individually) -- with ~900
# points per region/horizon the scatter was mostly a solid black blob with
# no readable internal shape; the violin's smoothed density trades exact
# per-point visibility for a readable "where do most solves sit" shape, still
# layered on top of the bar/whisker so the true baseline and certified VMM
# extremes (which the violin's own empirical tails do NOT represent -- BBO's
# explored points don't necessarily reach the true axis min/max) stay legible.
# showextrema=False on the violin itself for exactly this reason: its default
# min/max whiskers would be the empirical sample extremes, which read as (and
# would be confused for) the errorbar's true VMM-certified ones.
def fig_temporal_range_distribution(axis_idx, origin, phys, base) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    x = np.arange(len(REGIONS))
    n = len(UNTIL_YEARS)
    gap = 0.05
    width = (0.85 - (n - 1) * gap) / n
    tints = _horizon_tints(n)
    # Violin width < bar width so the bar's own black edge stays visible on
    # both sides of the violin body -- reads as "violin inset into its bar"
    # rather than the violin fully occluding the bar it's layered over.
    violin_width = width * 0.7

    for i, until_year in enumerate(UNTIL_YEARS):
        offset = (i - (n - 1) / 2) * (width + gap)
        cols = [axis_idx[f"{r}_{until_year}"] for r in REGIONS]
        baseline = np.array([base[c] for c in cols]) / 1000
        lo = np.array([phys[origin.index(f"min:{r}_{until_year}")][c]
                       for r, c in zip(REGIONS, cols)]) / 1000
        hi = np.array([phys[origin.index(f"max:{r}_{until_year}")][c]
                       for r, c in zip(REGIONS, cols)]) / 1000
        colors = [REGION_COLOR[r] if tints[i] == 0 else eth_tint(REGION_COLOR[r], tints[i]) for r in REGIONS]

        ax.bar(x + offset, baseline, width, color=colors, edgecolor="black", linewidth=0.6, zorder=3)
        yerr = np.vstack([baseline - lo, hi - baseline])
        ax.errorbar(x + offset, baseline, yerr=yerr, fmt="none", ecolor="black",
                     capsize=4, linewidth=1.2, zorder=5)

        for xi, c, color in zip(x + offset, cols, colors):
            data = phys[:, c] / 1000
            violin = ax.violinplot([data], positions=[xi], widths=violin_width,
                                    showmeans=False, showmedians=False, showextrema=False)
            for body in violin["bodies"]:
                body.set_facecolor(color)
                body.set_edgecolor("black")
                body.set_linewidth(0.5)
                body.set_alpha(0.6)
                body.set_zorder(4)

    ax.set_xticks(x)
    ax.set_xticklabels([r.capitalize() for r in REGIONS], fontsize=11)
    ax.set_ylabel("Cumulative regional CAPEX by that year (bn EUR)", fontsize=10)
    ax.set_title("MGA batch4 share tol=0.02 (v9_0): Absolute Cumulative CAPEX by Horizon Year",
                 fontsize=11, fontweight="bold")
    ax.legend(handles=[
        Patch(facecolor=eth_tint("#333333", t) if t else "#333333", edgecolor="black",
              label=f"cumulative by {until_year[-4:]}, baseline")
        for until_year, t in zip(UNTIL_YEARS, tints)
    ] + [Patch(facecolor="#333333", edgecolor="black", alpha=0.6,
               label="explored points (density)")],
              fontsize=9, loc="upper left")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    savefig(fig, "fig12_temporal_range_distribution")


def main() -> None:
    poly, names, units, axis_idx, origin, phys, base = load_batch4_data()
    fig_temporal_crosseffects(names, units, axis_idx, origin, phys, base)
    fig_temporal_range_absolute(axis_idx, origin, phys, base)
    fig_temporal_range_distribution(axis_idx, origin, phys, base)


if __name__ == "__main__":
    main()
