"""Baseline vs true own-axis max/min for the batch4 v9_0 regional-CAPEX-by-
PERIOD VMM run (data/outputs/euler_outputs_mga/
Crystal_Ball_ind_heat_v9_0_no_flexibility_nodiffusion_2020_7a_5a_interval_3ts_MGA_CAPEX_PERIODS_batch_bbo_minmax_batch4).

Context: this replaces the earlier batch16 regional-CAPEX run (config_mga_
axes_capex.json, 4 regions x 3 carrier groups = 12 node_capex_by_technology
axes) with a run against config_mga_axes_capex_periods.json instead: 4 node
clusters (north/west/south/east) x 2 calendar-year periods ([2030, 2039],
[2040, 2049]) = 8 node_capex_period axes, plus net_present_cost (9 axes
total, not 13 -- "include_cost": true in the config). Each axis sums that
region's cost_capex_yearly over ONLY the model years inside its own period,
not the technology-group split the old run used (zen_garden_plugins.mga.
plugin.MGA._design_axis_terms: NODE_CAPEX_PERIOD restricts by
self._axis_year_indices[axis.name] rather than by axis.technologies). This
run also spans a full pathway (2020-2050, 7 optimized periods at a 5-year
interval, 3ts) rather than the earlier single 2050 target-year snapshot --
the "2020_7a_5a_interval_3ts" vs "2050_1a_5a_interval_5ts" prefix -- and
batch_size=4 (batch4), not 16. The old batch16 regional-CAPEX figures
(fig0a/b/c, one per carrier group) were moved to data/outputs/figures/
mga_tests/archive_v9_0_capex_regional_batch16_groups/ rather than deleted --
see that folder if the old carrier-group cross-effects view is wanted again.

Its own polytope.npz (built by solve_axis_bounds/solve_extreme_lps, see
plugin.py) already carries the physical value of EVERY axis at EVERY solved
point, including the 16 VMM solves (4 regions x 2 periods x max/min) and the
baseline (z_star) -- no need to reload each point's own Results h5 files
individually (as of this run's download, the per-point Postprocess folders'
var_dict.h5/dual_dict.h5 are truncated/missing anyway -- see plot_mga_
results.py's axis_value() docstring note -- but fig0a/b never needed them:
everything plotted here comes straight out of the summary polytope).

This script reads that polytope.npz directly and produces fig0a/b (one per
period) -- each a heatmap of that period's 8 own-axis VMM solves (4 regions x
max/min) against every one of the 9 shared-frame axes, i.e. the real "which
region's CAPEX investment moves furthest up/down in this decade, and what
does it drag with it (in this decade AND the other one)" figure.

fig0a/b: each own-axis VMM solve is still a full ZEN-garden solve over the
WHOLE pathway, so it moves every OTHER axis too -- including that region's
OWN other-period axis (e.g. does maxing north's 2030s CAPEX crowd out or pull
forward north's 2040s CAPEX?) and every other region's axes in both periods.
One heatmap per period rather than one 16-column (8 axes x max/min) heatmap,
for the same readability/color-scale reasons as the old carrier-group
version. Cell value = that row axis's value under that column's solve, as a
ratio to baseline (1.0 = no change); log2-scaled color (RdBu_r, centred at 0)
since ratios range from ~0 (axis driven to zero) to very large (the column's
own target axis) -- a linear scale would wash out everything but the
diagonal.

Usage:
    python scripts/plot_mga_periods_regional_capex.py
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

import matplotlib.pyplot as plt
import numpy as np

# Match the rest of the MGA scripts / MT_report_HG's font -- see
# generate_si_figures.py for the rationale.
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["cmr10"],
    "mathtext.fontset": "cm",
    "axes.formatter.use_mathtext": True,
    "axes.unicode_minus": False,
})

from matplotlib.colors import TwoSlopeNorm

from figure_settings import SCENARIO_PALETTE
from zen_garden_plugins.mga.polytope_io import load_polytope

FIGURES_DIR = REPO_ROOT / "data" / "outputs" / "figures" / "mga_tests"
RUN_DIR = (
    REPO_ROOT / "data" / "outputs" / "euler_outputs_mga"
    / "Crystal_Ball_ind_heat_v9_0_no_flexibility_nodiffusion_2020_7a_5a_interval_3ts_MGA_CAPEX_PERIODS_batch_bbo_minmax_batch4"
)
MODEL = "Crystal_Ball_ind_heat_v9_0_no_flexibility_nodiffusion"
POLY_PATH = RUN_DIR / f"{MODEL}_batch_summary" / "polytope.npz"

REGIONS = ["north", "west", "south", "east"]
PERIODS = ["2030_2039", "2040_2049"]
# fig0a/b, in chronological order.
FIG0_LETTER = {"2030_2039": "a", "2040_2049": "b"}


def savefig(fig: plt.Figure, name: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{name}.svg"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {path.relative_to(REPO_ROOT)}")


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


def fig_crosseffects(period: str, names, units, axis_idx, origin, phys, base) -> None:
    """One heatmap for `period` in {"2030_2039", "2040_2049"}: columns are
    that period's 8 own-axis VMM solves (4 regions x max/min), rows are all 9
    shared-frame axes, cells are each row axis's value under that column's
    solve as a ratio to baseline. See module docstring for the log2-color
    rationale."""
    columns = [(region, sense) for region in REGIONS for sense in ("max", "min")]
    col_labels = [f"{region}\n{sense}" for region, sense in columns]
    row_axes = names  # 8 region/period CAPEX axes + net_present_cost, in poly.meta order
    matrix = np.array([
        [phys[origin.index(f"{sense}:{region}_{period}")][axis_idx[row]] / base[axis_idx[row]]
         for region, sense in columns]
        for row in row_axes
    ])
    log_matrix = np.log2(np.clip(matrix, 1e-6, None))
    vmax = max(1.0, np.nanmax(np.abs(log_matrix)))

    fig, ax = plt.subplots(figsize=(0.95 * len(columns) + 2.5, 0.5 * len(row_axes) + 2))
    im = ax.imshow(log_matrix, cmap="RdBu_r", norm=TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax),
                    aspect="auto")
    ax.set_xticks(range(len(columns)))
    ax.set_xticklabels(col_labels, fontsize=9)
    ax.set_yticks(range(len(row_axes)))
    ax.set_yticklabels([r.replace("_", " ") for r in row_axes], fontsize=9)
    for i, row in enumerate(row_axes):
        for j, (region, sense) in enumerate(columns):
            is_own_axis = row == f"{region}_{period}"
            ax.text(j, i, f"{matrix[i, j]:.2f}", ha="center", va="center",
                     fontsize=7.5, fontweight="bold" if is_own_axis else "normal",
                     color="black" if abs(log_matrix[i, j]) < vmax * 0.6 else "white")
            if is_own_axis:
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False,
                                            edgecolor="black", linewidth=2))
    ax.set_xticks(np.arange(-0.5, len(columns), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(row_axes), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.5)
    ax.tick_params(which="minor", length=0)
    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("value / baseline (log$_2$ scale; 1.0 = no change)", fontsize=9)
    period_label = period.replace("_", "-")
    ax.set_title(
        f"MGA batch4 (v9_0): {period_label} VMM Solves -- Effect on Every Axis\n"
        "(columns: that region's own max/min solve for this period; rows: every shared-frame axis's "
        "resulting value / baseline; boxed cell = the solve's own target axis)",
        fontsize=11, fontweight="bold",
    )
    fig.tight_layout()
    savefig(fig, f"fig0{FIG0_LETTER[period]}_{period}_crosseffects")


def main() -> None:
    poly, names, units, axis_idx, origin, phys, base = load_batch4_data()
    for period in PERIODS:
        fig_crosseffects(period, names, units, axis_idx, origin, phys, base)


if __name__ == "__main__":
    main()
