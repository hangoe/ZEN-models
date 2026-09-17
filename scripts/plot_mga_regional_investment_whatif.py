"""Regional cumulative-CAPEX investment "what-if" scenarios: fig20 (east)/
fig21 (west), one region constrained at a time, cap expressed as an
absolute bn-EUR ceiling on that region's cumulative-until-2050 investment
-- answered directly from the polytope (no re-solving of ZEN-garden),
against the same batch4 v9_0 regional-CUMULATIVE-CAPEX run, "share"
normalisation, tol=0.02 (data/outputs/euler_outputs_mga/
Crystal_Ball_ind_heat_v9_0_no_flexibility_nodiffusion_2020_7a_5a_interval_3ts_MGA_CAPEX_CUM_batch_bbo_share_batch4_tol002)
that plot_mga_cum_regional_capex.py's fig10/11/12 already use -- see that
script's module docstring for the run's full provenance/switchover history.

This script used to also produce fig13/14/16/17/18/19/22 -- a decile-based
4x4 what-if grid (fig13), a pairwise-dependencies rectangle-vs-hull view
(fig14), 2020-investment-multiple and %GDP-normalised variants of the same
grid split into two 2x4 row-pairings each (fig16/17, fig18/19), and an
east+west joint-feasibility check (fig22). All were deleted by user
request (git history has the code and figures if needed); what remains is
fig20/21's own absolute-bn-EUR single-region-row methodology below.

REGION_COLOR is imported from plots.mga_capex_periods_common -- the same
dict plot_mga_cum_regional_capex.py already uses (north=SCENARIO_PALETTE[0]
/blue, west=[1]/petrol, south=[2]/green, east=[3]/bronze) -- NOT re-derived
from this script's own REGIONS list order (north, east, south, west, for
N/E/S/W row-and-column display order), which an earlier version of this
script did via dict(zip(REGIONS, SCENARIO_PALETTE)) -- that silently
swapped east<->west's colours relative to every other MGA figure in this
repo (2026-09-03 bug, caught by user: "make sure to use the correct colors
for the regions in all figures"). REGIONS' order is now purely a display
choice, decoupled from colour assignment.

METHOD (2026-09-03, revised repeatedly, all user-prompted -- see git
history for earlier versions this superseded):

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
solve_bound_with_fallback (falling back to solve_outer_bound, labelled
"outer bound only") is kept for robustness but is not expected to fire
anywhere in this run.

fig20/21 (single row, one region constrained at CAP_YEAR_EAST/WEST=2050,
one column per affected region): see the module-level CAP_YEAR_EAST/
CAPS_EAST_ABS and CAP_YEAR_WEST/CAPS_WEST_ABS comments below for each
region's own feasibility/binding checks. draw_cell_abs's nested-ribbon,
baseline-star, infeasible/not-binding-labelling conventions are unchanged
from the deleted fig16-19 grids' own draw_cell_factor/draw_cell_gdp, just
against an absolute bn-EUR cap instead of a 2020-multiple or %GDP one.

WHY does capping region R also cap OTHER regions' UPPER bound, not just
raise their lower bound (user question -- "I do not understand why there
is an upper limit... this does not make sense to me")? Checked directly
against this run's own max:west_until_2030/min:west_until_2030 solves:
BOTH sit at net_present_cost = 22,305,054 -- essentially exactly the
epsilon=1% cost ceiling (22,305,054.089), while every other region's 2030
value at those two points is barely off baseline (e.g. north: baseline 539,
508 at max:west, 575 at min:west -- all bn EUR). So pushing west's 2030
value to EITHER of its own extremes already spends the ENTIRE near-
optimality budget alone, leaving ~zero slack for any other axis to reach
ITS OWN individual extreme at the same time. The epsilon budget is one
shared, fungible pool across every axis -- it is not that constraining A
directly "pushes" B's ceiling down, but that A and B cannot BOTH deviate
substantially from baseline (in whichever direction) without their combined
cost impact exceeding the ceiling, unless their deviations happen to be
cost-synergistic (roughly cost-neutral or cost-reducing combined -- which
is exactly what a genuine substitute pair looks like: one region using
cheaper capacity lets another use more of its own without the total
exceeding the budget, which is also why the induced LOWER bound rises).

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


def _draw_ribbon(ax, x, lo, hi, color, *, alpha=0.35, hatch=None, zorder=2, linestyle="-"):
    ax.fill_between(x, lo, hi, color=color, alpha=alpha, hatch=hatch,
                     edgecolor=color, linewidth=1.0, linestyle=linestyle, zorder=zorder)


def _draw_fixed_star(ax, x0, value, color, *, alpha, size, zorder, marker="*"):
    """The single deterministic (constrained_region, cap_year) point -- the
    imposed cap threshold itself (cell_range_abs's hi_scn at cap_year), not
    a solved value -- marked distinctly so it reads as "assumed", separate
    from every solved ribbon in the same cell (2026-09-07, user request:
    mark it with a star, not the earlier cross-hatched bar). `marker`
    defaults to the star; draw_cell_abs (fig20/21) instead reserves the star
    for the baseline (z*) line and marks this cap point with a downward
    triangle (a diamond first, then this, both 2026-09-07 user requests:
    "make the baseline run with the stars and the regions cap with another
    symbol" -- the triangle reads as a lid pressing down onto the cap
    value)."""
    ax.plot(x0, value, marker=marker, markersize=size, color=color, alpha=alpha,
            markeredgecolor=color, linestyle="none", zorder=zorder)


# fig20/21: ONE region only constrained at a time (a single row), cap
# expressed as an ABSOLUTE bn-EUR ceiling on that region's
# cumulative-until-CAP_YEAR investment -- no factor, no GDP derivation, just
# the numbers the user asked for directly -- at CAP_YEAR=2050 for both.
#
# fig20 (east): east's own 2050 near-optimal range is [540.1, 1884.9] bn EUR
# (baseline z*=727.5). 500 was certified INFEASIBLE (below the achievable
# minimum) and is dropped per user request; 600 and 700 are both
# feasible/binding, and 700 in particular sits BELOW east's own cost-optimal
# trajectory value at 2050 -- so even the baseline path would have to
# change, not just the near-optimal ceiling.
CAP_YEAR_EAST = "2050"
CAPS_EAST_ABS = [700, 600]  # loosest first/most translucent, tightest last/most opaque
_CAP_EAST_STYLE = {700: 0.30, 600: 0.85}

# fig21 (west): west's own 2050 near-optimal range is [2079.2, 3649.8] bn
# EUR (baseline z*=2452.5). Both 2200 and 2100 are feasible/binding, and
# both -- like east's 700 above -- sit BELOW west's own cost-optimal
# trajectory value at 2050.
CAP_YEAR_WEST = "2050"
CAPS_WEST_ABS = [2200, 2100]
_CAP_WEST_STYLE = {2200: 0.30, 2100: 0.85}


def threshold_abs_norm(poly, axis_idx, region: str, year: str, thresh_bn: float) -> tuple[str, float]:
    """(axis_name, normalised upper bound) for region's `year` axis capped
    directly at `thresh_bn` (bn EUR) -- an absolute value with no
    per-region derivation."""
    ax = f"{region}_until_{year}"
    k = axis_idx[ax]
    return ax, ((thresh_bn * 1000) - poly.offset[k]) / poly.scale[k]


def cell_range_abs(poly, axis_idx, ranges, constrained_region: str, cap_year: str, affected_region: str, thresh_bn: float):
    """(lo, hi, method, binding) across YEARS for affected_region under
    constrained_region capped at an absolute bn-EUR value on its
    `cap_year` axis (fig20/21 constrain 2050), or None if thresh_bn is
    certified INFEASIBLE (below constrained_region's own achievable
    minimum at cap_year)."""
    _, lo_c, hi_c = ranges[(constrained_region, cap_year)]
    if thresh_bn < lo_c:
        return None
    axis_name, bound = threshold_abs_norm(poly, axis_idx, constrained_region, cap_year, thresh_bn)
    thresholds_norm = {axis_name: bound}
    lo_out, hi_out, method = [], [], "inner"
    for y in YEARS:
        if affected_region == constrained_region and y == cap_year:
            lo_out.append(lo_c)
            hi_out.append(min(thresh_bn, hi_c))
            continue
        target_axis = f"{affected_region}_until_{y}"
        lo_v, m_lo = solve_bound_with_fallback(poly, axis_idx, thresholds_norm, target_axis, "min")
        hi_v, m_hi = solve_bound_with_fallback(poly, axis_idx, thresholds_norm, target_axis, "max")
        lo_out.append(lo_v / 1000)
        hi_out.append(hi_v / 1000)
        if m_lo == "outer" or m_hi == "outer":
            method = "outer"
    return lo_out, hi_out, method, thresh_bn < hi_c


def draw_cell_abs(ax, poly, axis_idx, ranges, constrained_region: str, cap_year: str, affected_region: str,
                   caps: list, style: dict) -> tuple[float, float]:
    """fig20/21's per-cell drawer: nested ribbons (tightest cap drawn
    last/most opaque), with infeasible/not-binding cells labelled directly
    rather than silently dropped, against an absolute bn-EUR cap at
    `cap_year`."""
    x = [int(y) for y in YEARS]
    base_y, lo_base, hi_base = zip(*[ranges[(affected_region, y)] for y in YEARS])
    _draw_ribbon(ax, x, lo_base, hi_base, REGION_COLOR[affected_region], alpha=0.15, zorder=1)
    ax.plot(x, base_y, color="black", marker="*", markersize=8, linewidth=1.0,
            linestyle="--", alpha=0.8, zorder=15)

    is_diagonal = affected_region == constrained_region
    cy_idx = YEARS.index(cap_year)
    color = REGION_COLOR[affected_region]
    infeasible_caps, non_binding_caps = [], []
    for zi, cap in enumerate(caps):
        alpha = style[cap]
        result = cell_range_abs(poly, axis_idx, ranges, constrained_region, cap_year, affected_region, cap)
        zorder = 2 + zi
        if result is None:
            infeasible_caps.append(cap)
            continue
        lo_scn, hi_scn, method, binding = result
        if not binding:
            non_binding_caps.append(cap)
        if method == "inner":
            _draw_ribbon(ax, x, lo_scn, hi_scn, color, alpha=alpha, zorder=zorder)
            if is_diagonal:
                _draw_fixed_star(ax, x[cy_idx], hi_scn[cy_idx], color,
                                 alpha=min(alpha + 0.15, 1.0), size=10, zorder=zorder + 10, marker="v")
        else:
            _draw_ribbon(ax, x, lo_scn, hi_scn, color, alpha=alpha * 0.7, zorder=zorder, linestyle="--")
            ax.text(0.5, 0.06, f"{cap:.0f} bn EUR: outer bound only", transform=ax.transAxes, ha="center",
                    va="bottom", fontsize=6, style="italic", color="#555555")

    if infeasible_caps:
        labels = ", ".join(f"{c:.0f}" for c in infeasible_caps)
        ax.text(0.5, 0.94, f"{labels} bn EUR: infeasible\n(below achievable min)", transform=ax.transAxes,
                ha="center", va="top", fontsize=6.5, style="italic", color="#b33333")
    elif non_binding_caps:
        labels = ", ".join(f"{c:.0f}" for c in non_binding_caps)
        ax.text(0.5, 0.94, f"{labels} bn EUR: not binding\n(above achievable range)", transform=ax.transAxes,
                ha="center", va="top", fontsize=6, style="italic", color="#2a6f2a")

    ax.set_xticks(x)
    ax.set_xlim(x[0] - 2, x[-1] + 2)
    ax.grid(axis="y", alpha=0.3)
    return min(lo_base), max(hi_base)


def fig_region_abs_cap(poly, axis_idx, ranges, region: str, cap_year: str, caps: list, style: dict, fig_name: str) -> None:
    """fig20 (region="east")/fig21 (region="west"): single row (`region`
    constrained only) x 4 columns (effect on every region), cap expressed as
    an absolute bn-EUR ceiling on `region`'s cumulative-until-`cap_year`
    investment -- see CAPS_EAST_ABS/CAPS_WEST_ABS's module-level comments
    for each region's feasibility check."""
    fig = plt.figure(figsize=(3.6 * len(REGIONS), 3.6))
    grid = fig.add_gridspec(1, len(REGIONS), wspace=0.3)
    print(f"  solving absolute-cap what-if LPs ({region} constrained at {cap_year} to "
          f"{', '.join(f'{c:.0f}' for c in caps)} bn EUR, inner-hull certified)...")
    for j, ar in enumerate(REGIONS):
        ax = fig.add_subplot(grid[0, j])
        draw_cell_abs(ax, poly, axis_idx, ranges, region, cap_year, ar, caps, style)
        ax.set_title(ar.capitalize(), fontsize=11, fontweight="bold")
        if j == 0:
            ax.set_ylabel(f"{region.capitalize()} constrained\n(bn EUR)", fontsize=8.5)
        ax.set_xticklabels(YEARS, fontsize=8.5)
        ax.tick_params(labelsize=8)
    print(f"    {region}: done")

    lo = min(a.get_ylim()[0] for a in fig.axes)
    hi = max(a.get_ylim()[1] for a in fig.axes)
    for a in fig.axes:
        a.set_ylim(lo, hi)

    left_col = [
        Patch(facecolor="#999999", alpha=0.15, label="baseline range"),
        Line2D([0], [0], color="black", marker="*", markersize=9, linewidth=1.0, linestyle="--",
               label="baseline (z*)"),
        Line2D([0], [0], marker="v", color="none", markerfacecolor="#999999", markeredgecolor="#999999",
               markersize=10, label="region's own cap"),
    ]
    right_col = [Patch(facecolor="#999999", alpha=style[c], label=f"capped at {c:.0f} bn EUR") for c in caps]
    fig.legend(handles=left_col + right_col, loc="lower center", ncol=2, fontsize=9, frameon=False,
               bbox_to_anchor=(0.5, -0.13))

    fig.suptitle(
        f"{region.capitalize()} Constrained: Absolute Investment Cap at {cap_year}\n"
        f"({region.capitalize()}'s cumulative-until-{cap_year} investment capped at "
        f"{', '.join(f'{c:.0f}' for c in caps)} bn EUR; effect on all 4 regions)",
        fontsize=12.5, fontweight="bold", y=1.08,
    )
    savefig(fig, fig_name)


def main() -> None:
    poly, axis_idx, origin, phys, base = load_data()
    ranges = compute_ranges(axis_idx, origin, phys, base)

    fig_region_abs_cap(poly, axis_idx, ranges, "east", CAP_YEAR_EAST, CAPS_EAST_ABS, _CAP_EAST_STYLE,
                       fig_name="fig20_east_investment_abs2050")
    fig_region_abs_cap(poly, axis_idx, ranges, "west", CAP_YEAR_WEST, CAPS_WEST_ABS, _CAP_WEST_STYLE,
                       fig_name="fig21_west_investment_abs2050")


if __name__ == "__main__":
    main()
