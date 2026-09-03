"""Regional cumulative-CAPEX investment ranges over 2030/2040/2050: four
single-region "what-if" scenarios, each shown at three nested severities --
what if region R's 2030 investment is capped at its lowest 10%, 5%, or 1%?
-- answered directly from the polytope (no re-solving of ZEN-garden),
against the same batch4 v9_0 regional-CUMULATIVE-CAPEX run, "share"
normalisation, tol=0.02 (data/outputs/euler_outputs_mga/
Crystal_Ball_ind_heat_v9_0_no_flexibility_nodiffusion_2020_7a_5a_interval_3ts_MGA_CAPEX_CUM_batch_bbo_share_batch4_tol002)
that plot_mga_cum_regional_capex.py's fig10/11/12 already use -- see that
script's module docstring for the run's full provenance/switchover history.

This run's polytope carries THREE cumulative horizons per region
(until_2030/2040/2050, 12 design axes + net_present_cost = 13 -- one more
horizon than plot_mga_cum_regional_capex.py touches, which only reads the
until_2040/until_2050 columns and leaves until_2030 unused). This script
plots all three (YEARS), unlike that one.

REGION_COLOR is imported from plots.mga_capex_periods_common -- the same
dict plot_mga_investment_map.py and plot_mga_cum_regional_capex.py already
use (north=SCENARIO_PALETTE[0]/blue, west=[1]/petrol, south=[2]/green,
east=[3]/bronze) -- NOT re-derived from this script's own REGIONS list
order (north, east, south, west, for N/E/S/W row-and-column display order),
which an earlier version of this script did via dict(zip(REGIONS,
SCENARIO_PALETTE)) -- that silently swapped east<->west's colours relative
to every other MGA figure in this repo (2026-09-03 bug, caught by user:
"make sure to use the correct colors for the regions in all figures").
REGIONS' order is now purely a display choice, decoupled from colour
assignment.

METHOD (2026-09-03, revised repeatedly, all user-prompted -- see git
history for the two earlier versions this superseded):

Every what-if LP solves over the CONVEX HULL of poly.X (baseline + VMM
extremes + all 892 "iterate" solves this run actually computed) rather than
the polytope's own OUTER cutting-plane approximation (A x <= b) alone. The
outer approximation is a valid but often far-from-tight superset of the
true near-optimal region -- comparing against the real solves shows every
region-pair's cumulative CAPEX is genuinely negatively correlated (e.g.
corr(north, west) = -0.35 at 2040, i.e. regions substitute for each other),
a compensating effect the outer-approximation LP mostly failed to surface
(this run's cutting planes aren't refined tightly enough yet in those
specific cross-directions, even though the run overall is well-converged,
final_gap=0.027). solve_inner_hull_bound instead poses an LP directly over
poly.X's convex combinations (the "inner approximation" construction from
Steen2026_Thesis Sec 3.3 / the ORACLE slide deck pp. 7-9, already used by
rejection_sample_inner in plot_mga_results.py as a membership check, here
as an optimisation): any convex combination of certified near-optimal
points is itself near-optimal (the model is convex), so every value
returned is a CERTIFIED ACHIEVABLE bound, not merely "not yet ruled out".

CONSTRAINED_YEAR=2030 (not 2050, an earlier version's choice): each what-if
constrains ONLY that region's until_2030 axis, at each of DECILES
(0.10, 0.05, 0.01) in turn -- letting 2040/2050, including that SAME
region's own, be solved for like every other target axis, never assumed.
Verified directly: every one of the 4 regions x 3 deciles x 11 other
(region, year) target axes (132 checks total) is feasible within the inner
hull at CONSTRAINED_YEAR=2030 -- unlike an earlier CONSTRAINED_YEAR=2050
version, which needed an outer-approximation fallback in most cells, and a
version before that which jointly constrained all three years per region
and was infeasible almost everywhere in the inner hull. solve_bound_with_
fallback (falling back to solve_outer_bound, labelled "outer bound only")
is kept for robustness but is not expected to fire anywhere in this run.

fig_whatif (4x4 grid, one row per region): each cell shows region R's
(row) induced effect on region A's (column) range as THREE NESTED ribbons
-- one per decile in DECILES, tightest (1%) drawn last/most opaque, loosest
(10%) drawn first/most translucent, since a tighter cap is by construction
a subset of what a looser cap allows (monotonic nesting, verified
numerically: e.g. west capped at 2030's lowest 10%/5%/1% induces north's
2040 range to [916,1040]/[947,1009]/[971,983] bn EUR respectively, visibly
narrowing and shifting up as the cap tightens -- from a baseline of
[764,1155]). On the diagonal (R == A), R's own CONSTRAINED_YEAR value is
the deterministic assumption per decile (cross-hatched, "imposed", tiny
nested slivers); every other cell/year, including R's own other years, is
solved. One region's colour per cell, no cross-region overlap (an earlier
version overlaid all 4 regions in one axes per scenario and read as a
muddy blend of overlapping fills).

Usage:
    python scripts/plot_mga_regional_investment_whatif.py
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from scipy.optimize import linprog

from plots.figure_settings import apply_font_mode
from plots.mga_capex_periods_common import REGION_COLOR

# Match the rest of the MGA scripts / MT_report_HG's font -- see
# figure_settings.FONT_MODE for the rationale and for the one-flag toggle
# that switches every figure script in this repo at once.
apply_font_mode()
from zen_garden_plugins.mga.polytope_io import load_polytope

FIGURES_DIR = REPO_ROOT / "data" / "outputs" / "figures" / "mga_tests"
RUN_DIR = (
    REPO_ROOT / "data" / "outputs" / "euler_outputs_mga"
    / "Crystal_Ball_ind_heat_v9_0_no_flexibility_nodiffusion_2020_7a_5a_interval_3ts_MGA_CAPEX_CUM_batch_bbo_share_batch4_tol002"
)
MODEL = "Crystal_Ball_ind_heat_v9_0_no_flexibility_nodiffusion"
POLY_PATH = RUN_DIR / f"{MODEL}_batch_summary" / "polytope.npz"

REGIONS = ["north", "east", "south", "west"]  # display order (N, E, S, W); colours come from REGION_COLOR, not this order
YEARS = ["2030", "2040", "2050"]
CONSTRAINED_YEAR = "2030"  # each what-if fixes only this year's axis per constrained region -- see module docstring
DECILES = [0.10, 0.05, 0.01]  # loosest first (drawn first/most translucent) to tightest last (drawn last/most opaque)
_DECILE_STYLE = {0.10: 0.30, 0.05: 0.55, 0.01: 0.85}  # decile -> fill alpha


def savefig(fig: plt.Figure, name: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{name}.svg"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {path.relative_to(REPO_ROOT)}")


def load_data():
    """(poly, axis_idx, origin, phys, base): the loaded Polytope (poly.X is
    every certified near-optimal point this run solved -- baseline + VMM
    extremes + iterates -- and poly.A/b its outer cutting-plane system), a
    name->column index map, each solved point's origin label, every solved
    point's physical-unit vector (poly.X is stored normalised; to_phys
    converts back), and the baseline (z_star) vector."""
    if not POLY_PATH.exists():
        raise FileNotFoundError(f"batch4 polytope not found at {POLY_PATH}")
    poly = load_polytope(POLY_PATH)
    axis_idx = {n: i for i, n in enumerate(poly.names)}
    origin = list(poly.point_origin)
    phys = np.array([poly.to_phys(x) for x in poly.X])
    base = phys[origin.index("z_star")]
    print(f"  loaded {len(origin)} points from {POLY_PATH.relative_to(REPO_ROOT)} "
          f"(converged={poly.converged}, final_gap={poly.final_gap:.3f})")
    return poly, axis_idx, origin, phys, base


def own_axis_range(axis_idx, origin, phys, base, region, year):
    """(baseline, lo, hi) in mEUR for one region/year's own cumulative-CAPEX
    axis -- the certified own-axis VMM min/max, exactly as fig11_temporal_
    range_absolute in plot_mga_cum_regional_capex.py reads them."""
    ax = f"{region}_until_{year}"
    j = axis_idx[ax]
    lo = phys[origin.index(f"min:{ax}")][j]
    hi = phys[origin.index(f"max:{ax}")][j]
    return base[j], lo, hi


def compute_ranges(axis_idx, origin, phys, base) -> dict:
    """{(region, year): (baseline, lo, hi)} in bn EUR for every region/year,
    read off the same own-axis VMM min/max points fig11_temporal_range_
    absolute in plot_mga_cum_regional_capex.py already plots on its own --
    not redrawn here as a standalone panel, just reused as each cell's
    faint backdrop ribbon and as the source range for every threshold."""
    return {
        (r, y): tuple(v / 1000 for v in own_axis_range(axis_idx, origin, phys, base, r, y))
        for r in REGIONS for y in YEARS
    }


def threshold_norm(poly, axis_idx, ranges, region: str, year: str, decile: float) -> tuple[str, float]:
    """(axis_name, normalised upper bound) for region/year at
    lo + decile*(hi-lo) (ranges values are bn EUR; converted to normalised
    coords via poly.scale/offset, see polytope_io.py)."""
    _, lo, hi = ranges[(region, year)]
    thresh_phys = (lo + decile * (hi - lo)) * 1000
    ax = f"{region}_until_{year}"
    k = axis_idx[ax]
    return ax, (thresh_phys - poly.offset[k]) / poly.scale[k]


def solve_inner_hull_bound(poly, axis_idx, thresholds_norm: dict, target_axis: str, sense: str) -> float:
    """min or max of target_axis's physical value, over the CONVEX HULL of
    poly.X (every certified near-optimal point -- baseline, VMM extremes,
    iterates), subject to each axis in thresholds_norm being <= its bound:
        minimize/maximize  X[:, target]^T @ lambda
        s.t.               X[:, ax]^T @ lambda <= bound   for ax in thresholds_norm
                            sum(lambda) = 1,  lambda >= 0
    Every feasible lambda is a certified near-optimal design (convexity), so
    the result is a genuinely ACHIEVABLE bound, unlike solve_outer_bound's.
    Raises if no certified combination reaches the requested threshold --
    verified not to happen anywhere in this figure (see module docstring),
    but solve_bound_with_fallback still guards against it."""
    X = poly.X
    m = X.shape[0]
    j = axis_idx[target_axis]
    c = X[:, j] * (1.0 if sense == "min" else -1.0)
    A_ub = np.array([X[:, axis_idx[ax]] for ax in thresholds_norm])
    b_ub = np.array(list(thresholds_norm.values()))
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=np.ones((1, m)), b_eq=[1.0],
                   bounds=[(0, None)] * m, method="highs")
    if not res.success:
        raise RuntimeError(f"inner-hull LP infeasible for {target_axis} ({sense}): {res.message}")
    val_norm = float(X[:, j] @ res.x)
    return val_norm * poly.scale[j] + poly.offset[j]


def solve_outer_bound(poly, axis_idx, thresholds_norm: dict, target_axis: str, sense: str) -> float:
    """min or max of target_axis's physical value, over the polytope's own
    OUTER approximation alone (A x <= b) -- a valid but not necessarily
    tight bound (see module docstring); used only where the inner hull
    cannot certify an answer."""
    n = poly.A.shape[1]
    j = axis_idx[target_axis]
    c = np.zeros(n)
    c[j] = 1.0 if sense == "min" else -1.0
    bounds = [(None, None)] * n
    for ax, ub in thresholds_norm.items():
        bounds[axis_idx[ax]] = (None, ub)
    res = linprog(c, A_ub=poly.A, b_ub=poly.b, bounds=bounds, method="highs")
    if not res.success:
        raise RuntimeError(f"outer-approximation LP infeasible for {target_axis} ({sense}): {res.message}")
    val_norm = res.x[j]
    return val_norm * poly.scale[j] + poly.offset[j]


def solve_bound_with_fallback(poly, axis_idx, thresholds_norm: dict, target_axis: str, sense: str) -> tuple[float, str]:
    """(value, method): tries solve_inner_hull_bound first, falls back to
    solve_outer_bound ("outer") if the inner hull's finite sample doesn't
    reach that corner -- a real "not enough data to certify" event, not a
    bug (see module docstring; verified not to fire anywhere in this
    figure, kept as a guard)."""
    try:
        return solve_inner_hull_bound(poly, axis_idx, thresholds_norm, target_axis, sense), "inner"
    except RuntimeError:
        return solve_outer_bound(poly, axis_idx, thresholds_norm, target_axis, sense), "outer"


def cell_range(poly, axis_idx, ranges, constrained_region: str, affected_region: str, decile: float) -> tuple[list, list, str]:
    """(lo, hi, method) across YEARS for affected_region under
    constrained_region being capped at `decile` at CONSTRAINED_YEAR only.
    The one deterministic entry is affected_region's own CONSTRAINED_YEAR
    value when affected_region == constrained_region (fixed by assumption,
    [lo, threshold]); every other (region, year) -- including that SAME
    region's other years -- is solved for via solve_bound_with_fallback.
    method is "outer" if ANY year in the result needed the fallback (so one
    ribbon is drawn with one consistent, honestly-labelled method rather
    than mixing certified and merely-valid segments)."""
    axis_name, bound = threshold_norm(poly, axis_idx, ranges, constrained_region, CONSTRAINED_YEAR, decile)
    thresholds_norm = {axis_name: bound}
    lo_out, hi_out, method = [], [], "inner"
    for y in YEARS:
        if affected_region == constrained_region and y == CONSTRAINED_YEAR:
            _, lo_b, hi_b = ranges[(affected_region, y)]
            lo_out.append(lo_b)
            hi_out.append(lo_b + decile * (hi_b - lo_b))
            continue
        target_axis = f"{affected_region}_until_{y}"
        lo_v, m_lo = solve_bound_with_fallback(poly, axis_idx, thresholds_norm, target_axis, "min")
        hi_v, m_hi = solve_bound_with_fallback(poly, axis_idx, thresholds_norm, target_axis, "max")
        lo_out.append(lo_v / 1000)
        hi_out.append(hi_v / 1000)
        if m_lo == "outer" or m_hi == "outer":
            method = "outer"
    return lo_out, hi_out, method


def _draw_ribbon(ax, x, lo, hi, color, *, alpha=0.35, hatch=None, zorder=2, linestyle="-"):
    ax.fill_between(x, lo, hi, color=color, alpha=alpha, hatch=hatch,
                     edgecolor=color, linewidth=1.0, linestyle=linestyle, zorder=zorder)


def draw_cell(ax, poly, axis_idx, ranges, constrained_region: str, affected_region: str) -> tuple[float, float]:
    """One small-multiple cell: affected_region's baseline ribbon (faint)
    plus THREE NESTED ribbons, one per decile in DECILES (loosest/10% drawn
    first & most translucent, tightest/1% drawn last & most opaque -- see
    _DECILE_STYLE), each affected_region's range under constrained_region
    being capped at that decile at CONSTRAINED_YEAR. On the diagonal
    (affected_region == constrained_region), each decile's own
    CONSTRAINED_YEAR band is drawn cross-hatched instead (fixed by
    assumption, not solved) -- every other year/cell is solved via
    cell_range. Falls back to a dashed, lower-alpha "outer bound only" style
    (verified not to occur in this figure -- see module docstring) if the
    inner hull can't certify a given decile. Returns (ymin, ymax) of the
    baseline ribbon, so the caller can share y-limits down each column."""
    x = [int(y) for y in YEARS]
    base_y, lo_base, hi_base = zip(*[ranges[(affected_region, y)] for y in YEARS])
    _draw_ribbon(ax, x, lo_base, hi_base, REGION_COLOR[affected_region], alpha=0.15, zorder=1)

    is_diagonal = affected_region == constrained_region
    cy_idx = YEARS.index(CONSTRAINED_YEAR)
    for zi, decile in enumerate(DECILES):
        alpha = _DECILE_STYLE[decile]
        lo_scn, hi_scn, method = cell_range(poly, axis_idx, ranges, constrained_region, affected_region, decile)
        zorder = 2 + zi
        if is_diagonal and method == "inner":
            _draw_ribbon(ax, x[cy_idx:cy_idx + 1], lo_scn[cy_idx:cy_idx + 1], hi_scn[cy_idx:cy_idx + 1],
                         REGION_COLOR[affected_region], alpha=alpha, hatch="xxx", zorder=zorder + 10)
            other = [i for i in range(len(YEARS)) if i != cy_idx]
            _draw_ribbon(ax, [x[i] for i in other], [lo_scn[i] for i in other], [hi_scn[i] for i in other],
                         REGION_COLOR[affected_region], alpha=alpha, zorder=zorder)
        elif method == "inner":
            _draw_ribbon(ax, x, lo_scn, hi_scn, REGION_COLOR[affected_region], alpha=alpha, zorder=zorder)
        else:
            _draw_ribbon(ax, x, lo_scn, hi_scn, REGION_COLOR[affected_region], alpha=alpha * 0.7,
                         zorder=zorder, linestyle="--")
            ax.text(0.5, 0.06, f"{decile:.0%}: outer bound only", transform=ax.transAxes, ha="center",
                    va="bottom", fontsize=6, style="italic", color="#555555")

    ax.set_xticks(x)
    ax.set_xlim(x[0] - 2, x[-1] + 2)
    ax.grid(axis="y", alpha=0.3)
    return min(lo_base), max(hi_base)


def main() -> None:
    poly, axis_idx, origin, phys, base = load_data()
    ranges = compute_ranges(axis_idx, origin, phys, base)

    fig = plt.figure(figsize=(14, 13))
    grid = fig.add_gridspec(4, 4, hspace=0.55, wspace=0.3)
    print(f"  solving what-if LPs (region capped by {CONSTRAINED_YEAR} at "
          f"{', '.join(f'{d:.0%}' for d in DECILES)}, inner-hull certified)...")
    for i, cr in enumerate(REGIONS):
        for j, ar in enumerate(REGIONS):
            ax = fig.add_subplot(grid[i, j])
            draw_cell(ax, poly, axis_idx, ranges, cr, ar)
            if i == 0:
                ax.set_title(ar.capitalize(), fontsize=11, fontweight="bold")
            if j == 0:
                ax.set_ylabel(f"{cr.capitalize()}\nconstrained\n(bn EUR)", fontsize=8.5)
            if i == len(REGIONS) - 1:
                ax.set_xticklabels(YEARS, fontsize=8.5)
            else:
                ax.set_xticklabels([])
            ax.tick_params(labelsize=8)
        print(f"    {cr}: done")

    # Share y-limits down each column so a region's own scale is comparable
    # across every scenario.
    for j, ar in enumerate(REGIONS):
        col_axes = [fig.axes[i * 4 + j] for i in range(len(REGIONS))]
        lo = min(a.get_ylim()[0] for a in col_axes)
        hi = max(a.get_ylim()[1] for a in col_axes)
        for a in col_axes:
            a.set_ylim(lo, hi)

    handles = [Patch(facecolor="#999999", alpha=0.15, label="baseline near-optimal range")] + [
        Patch(facecolor="#999999", alpha=_DECILE_STYLE[d],
              label=f"induced range, region capped at lowest {d:.0%}") for d in DECILES
    ] + [
        Patch(facecolor="#999999", alpha=0.85, hatch="xxx", edgecolor="#999999",
              label=f"constrained region's own {CONSTRAINED_YEAR} (fixed by assumption, per decile)"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=2, fontsize=9, frameon=False,
               bbox_to_anchor=(0.5, -0.05))

    fig.suptitle(
        "MGA batch4 share tol=0.02 (v9_0): Regional Investment Ranges and \"What-If\" Scenarios\n"
        f"(rows: region capped at its lowest 10% / 5% / 1% by {CONSTRAINED_YEAR}  |  "
        "columns: induced effect on each region's own range)",
        fontsize=13, fontweight="bold", y=0.995,
    )
    savefig(fig, "fig13_regional_investment_whatif")


if __name__ == "__main__":
    main()
