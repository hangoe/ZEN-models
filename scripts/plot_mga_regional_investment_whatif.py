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
(0.10, 0.01 -- 5% dropped 2026-09-07, user request: "use lowest 1% and 10%
only") in turn -- letting 2040/2050, including that SAME region's own, be
solved for like every other target axis, never assumed. Verified directly:
every one of the 4 regions x deciles x 11 other (region, year) target axes
is feasible within the inner hull at CONSTRAINED_YEAR=2030 -- unlike an
earlier CONSTRAINED_YEAR=2050 version, which needed an outer-approximation
fallback in most cells, and a version before that which jointly
constrained all three years per region and was infeasible almost
everywhere in the inner hull. solve_bound_with_fallback (falling back to
solve_outer_bound, labelled "outer bound only") is kept for robustness but
is not expected to fire anywhere in this run.

fig_whatif (4x4 grid, one row per region): each cell shows region R's
(row) induced effect on region A's (column) range as TWO NESTED ribbons --
one per decile in DECILES, tightest (1%) drawn last/most opaque, loosest
(10%) drawn first/most translucent, since a tighter cap is by construction
a subset of what a looser cap allows (monotonic nesting, verified
numerically: e.g. west capped at 2030's lowest 10%/1% induces north's 2040
range to [916,1040]/[971,983] bn EUR respectively, visibly narrowing and
shifting up as the cap tightens -- from a baseline of [764,1155]). Each
cell also plots affected_region's baseline (cost-optimal z*) trajectory
across YEARS as a black dashed diamond-marker line (2026-09-07, user
request: "add the baseline value in each graph") on top of the faint
baseline near-optimal ribbon, so the reader can see both the full
certified range AND where the actual optimum sits within it. On the
diagonal (R == A), R's own CONSTRAINED_YEAR value is the deterministic
assumption per decile, marked with a star at the imposed cap threshold
(2026-09-07, user request: "show the constrained region in 2030 with a
star *, not the dash" -- replaces the earlier cross-hatched bar); every
other cell/year, including R's own other years, is solved. One region's
colour per cell, no cross-region overlap (an earlier version overlaid all
4 regions in one axes per scenario and read as a muddy blend of
overlapping fills). Two bugs fixed here (2026-09-03, user-caught): the
diagonal's fixed CONSTRAINED_YEAR band used to be drawn with _draw_ribbon
(matplotlib fill_between) on a length-1 x list, which silently renders
nothing -- fill_between needs >=2 points to form a polygon -- so "2030
disappeared" on every diagonal cell; a narrow bar (later replaced by the
star marker above) fixed that. y-limits used to be shared only DOWN EACH
COLUMN (so panels were comparable within a region but not across regions);
now ALL 16 cells share one global y-limit, at the cost of squashing the
smaller regions (east) against the largest (west) -- an explicit trade-off
the user asked for ("make sure all figures have the same axis limits").

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
"In which cases would high investment in other regions still be there?"
-- only where the joint deviation is compatible with the shared budget;
fig14 below visualises exactly this for every region pair.

fig14 (pairwise dependencies, lower-triangular 4x4 grid): for every region
pair at PAIRWISE_YEAR, plots the dashed axis-aligned rectangle spanning
each region's OWN independent [lo, hi] (2026-09-03, user request: "what
would this look like if there were no dependency") against the SOLID
outline of the actual near-optimal region -- the exact 2D projection of the
convex hull of every certified point in poly.X (baseline + VMM extremes +
iterates), i.e. the same ConvexHull-of-poly.X construction fig2_polytope_
samples in plot_mga_results.py already uses for its inner-hull outline, but
of the FULL point set here rather than a rejection-sampled dense cloud
(there is no need for a synthetic sample just to draw an exact hull
outline). Real iterate points are scattered underneath for context, baseline
marked. The outline visibly fails to reach the rectangle's corners where
both regions would be simultaneously at their own extreme (top-right: both
maxed; bottom-left: both minimised) -- the visual answer to the "why is
there an upper limit" question above: a rectangle is what independence
would look like, and this is not a rectangle.

Usage:
    python scripts/plot_mga_regional_investment_whatif.py
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from scipy.optimize import linprog
from scipy.spatial import ConvexHull

from plots.figure_settings import apply_font_mode
from plots.mga_capex_periods_common import REGION_COLOR

# Match the rest of the MGA scripts / MT_report_HG's font -- see
# figure_settings.FONT_MODE for the rationale and for the one-flag toggle
# that switches every figure script in this repo at once.
apply_font_mode()
from zen_garden import Results
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
DECILES = [0.10, 0.01]  # loosest first (drawn first/most translucent) to tightest last (drawn last/most opaque) -- 5% dropped 2026-09-07, user request
_DECILE_STYLE = {0.10: 0.30, 0.01: 0.85}  # decile -> fill alpha
PAIRWISE_YEAR = "2030"  # which year's axes fig14 plots pairwise -- matches CONSTRAINED_YEAR

# fig16: caps expressed as a multiple of the region's own 2020 (first
# model year) investment instead of a decile of its 2030 near-optimal
# range -- see fig_whatif_2020factor's docstring. Loosest (3x) first/most
# translucent, tightest (2.5x) last/most opaque, matching DECILES' nesting
# convention. 2.5x (2026-09-07, user request, replacing an earlier 2x that
# was certified infeasible in EVERY region) is a genuinely MIXED case,
# checked directly: feasible for north (443.8 vs its 2030 near-optimal
# minimum of 441.8 bn EUR -- barely) and east (253.2 vs 222.2), but
# infeasible for west (829.6 vs a minimum of 866.8) and south (459.2 vs
# 470.1) -- kept in the list either way so infeasibility is drawn and
# labelled per-region rather than silently dropped.
FACTORS_2020 = [3, 2.5]
_FACTOR_STYLE = {3: 0.30, 2.5: 0.85}
CAPEX_CUM_CONFIG = json.loads((REPO_ROOT / "data" / "config_mga_axes_capex_cum.json").read_text())
REGION_NODES = {next(iter(d)): next(iter(d.values())) for d in CAPEX_CUM_CONFIG["node_capex_cumulative"]["nodes"]}


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


def compute_region_2020(base_r: Results) -> dict:
    """{region: 2020 investment in bn EUR}: cost_capex_yearly (mEUR,
    indexed by technology/capacity_type/location, columns = model years)
    summed over every technology at every node in the region, restricted
    to the model's FIRST year (2020) -- the same variable and region->node
    mapping (REGION_NODES, from this run's own config_mga_axes_capex_cum.
    json) that this run's until_2030/2040/2050 MGA axes are built from
    (axes.py: "period is (None, until_year) ... the leading None means no
    lower bound, from the first model year"), just isolated to that single
    first year instead of summed up to a horizon. Loaded from the baseline
    (z_star) full solve, not the polytope -- 2020 isn't itself an MGA
    design axis in this run, so this is the only place its value lives."""
    capex = base_r.get_total("cost_capex_yearly")
    out = {}
    for region, nodes in REGION_NODES.items():
        sub = capex[capex.index.get_level_values("location").isin(nodes)]
        out[region] = sub[[c for c in sub.columns if c == 2020]].sum().sum() / 1000
    return out


def threshold_factor_norm(poly, axis_idx, region_2020: dict, region: str, factor: float) -> tuple[str, float, float]:
    """(axis_name, normalised upper bound, threshold in bn EUR) for
    region's CONSTRAINED_YEAR axis capped at `factor` times region's own
    2020 investment (region_2020, from compute_region_2020)."""
    thresh_bn = factor * region_2020[region]
    ax = f"{region}_until_{CONSTRAINED_YEAR}"
    k = axis_idx[ax]
    return ax, ((thresh_bn * 1000) - poly.offset[k]) / poly.scale[k], thresh_bn


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


def cell_range_factor(poly, axis_idx, ranges, region_2020: dict, constrained_region: str, affected_region: str, factor: float):
    """Like cell_range, but the constrained axis is capped at `factor`
    times constrained_region's own 2020 investment instead of a decile of
    its 2030 near-optimal range. Returns (lo, hi, method) as cell_range
    does, or None if the cap is certified INFEASIBLE -- i.e. below
    constrained_region's own certified achievable MINIMUM 2030 cumulative
    investment (ranges' lo), so no near-optimal design can satisfy it at
    all. Checked directly against this run: factor=2 fails this test for
    all 4 regions (e.g. north's cheapest achievable 2030 investment is 442
    bn EUR, already above 2x its 177 bn EUR 2020 investment = 355 bn EUR);
    factor=3 passes for all 4 (north's 3x=532 sits inside its [442,695]
    2030 range) -- see fig_whatif_2020factor's docstring."""
    _, lo_c, hi_c = ranges[(constrained_region, CONSTRAINED_YEAR)]
    thresh_bn = factor * region_2020[constrained_region]
    if thresh_bn < lo_c:
        return None
    axis_name, bound, _ = threshold_factor_norm(poly, axis_idx, region_2020, constrained_region, factor)
    thresholds_norm = {axis_name: bound}
    lo_out, hi_out, method = [], [], "inner"
    for y in YEARS:
        if affected_region == constrained_region and y == CONSTRAINED_YEAR:
            lo_out.append(lo_c)
            hi_out.append(thresh_bn)
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


def _draw_fixed_star(ax, x0, value, color, *, alpha, size, zorder, marker="*"):
    """The single deterministic (constrained_region, CONSTRAINED_YEAR)
    point -- the imposed cap threshold itself (cell_range's hi_scn at
    CONSTRAINED_YEAR), not a solved value -- marked distinctly so it reads
    as "assumed", separate from every solved ribbon in the same cell
    (2026-09-07, user request: mark it with a star, not the earlier
    cross-hatched bar). `marker` defaults to the star used everywhere except
    fig16/17 (draw_cell_factor), which instead reserves the star for the
    baseline (z*) line and marks this cap point with a downward triangle
    (a diamond first, then this, both 2026-09-07 user requests: "make the
    baseline run with the stars and the regions cap with another symbol" --
    the triangle reads as a lid pressing down onto the cap value) -- see
    draw_cell_factor's docstring."""
    ax.plot(x0, value, marker=marker, markersize=size, color=color, alpha=alpha,
            markeredgecolor=color, linestyle="none", zorder=zorder)


def draw_cell(ax, poly, axis_idx, ranges, constrained_region: str, affected_region: str) -> tuple[float, float]:
    """One small-multiple cell: affected_region's baseline ribbon (faint,
    the own-axis near-optimal range) plus its baseline z* trajectory
    (black dashed diamond-marker line) drawn on top, then TWO NESTED
    ribbons, one per decile in DECILES (loosest/10% drawn first & most
    translucent, tightest/1% drawn last & most opaque -- see
    _DECILE_STYLE), each affected_region's range under constrained_region
    being capped at that decile at CONSTRAINED_YEAR: ONE continuous ribbon
    across all three years (cell_range already bakes the deterministic
    CONSTRAINED_YEAR value into the same lo/hi arrays as every solved
    year -- an earlier version instead split the diagonal into a
    disconnected bar at CONSTRAINED_YEAR plus a separate ribbon for the
    other two years, which broke the trajectory into a visibly floating,
    disjointed pair of shapes, the "weird"-looking bug the user caught).
    On the diagonal (affected_region == constrained_region), a star marker
    sits ON TOP of the continuous ribbon exactly at CONSTRAINED_YEAR (at
    the imposed cap threshold, cell_range's hi_scn there) to flag "fixed by
    assumption, not solved" -- every other point, including every other
    point in this same diagonal cell, is genuinely solved via cell_range.
    Falls back to a dashed, lower-alpha "outer bound only" style (verified
    not to occur in this figure -- see module docstring) if the inner hull
    can't certify a given decile. Returns (ymin, ymax) of the baseline
    ribbon, so the caller can share y-limits down each column."""
    x = [int(y) for y in YEARS]
    base_y, lo_base, hi_base = zip(*[ranges[(affected_region, y)] for y in YEARS])
    _draw_ribbon(ax, x, lo_base, hi_base, REGION_COLOR[affected_region], alpha=0.15, zorder=1)
    ax.plot(x, base_y, color="black", marker="D", markersize=3.5, linewidth=1.0,
            linestyle="--", alpha=0.8, zorder=15)

    is_diagonal = affected_region == constrained_region
    cy_idx = YEARS.index(CONSTRAINED_YEAR)
    for zi, decile in enumerate(DECILES):
        alpha = _DECILE_STYLE[decile]
        lo_scn, hi_scn, method = cell_range(poly, axis_idx, ranges, constrained_region, affected_region, decile)
        zorder = 2 + zi
        if method == "inner":
            _draw_ribbon(ax, x, lo_scn, hi_scn, REGION_COLOR[affected_region], alpha=alpha, zorder=zorder)
            if is_diagonal:
                _draw_fixed_star(ax, x[cy_idx], hi_scn[cy_idx], REGION_COLOR[affected_region],
                                 alpha=min(alpha + 0.15, 1.0), size=11, zorder=zorder + 10)
        else:
            _draw_ribbon(ax, x, lo_scn, hi_scn, REGION_COLOR[affected_region], alpha=alpha * 0.7,
                         zorder=zorder, linestyle="--")
            ax.text(0.5, 0.06, f"{decile:.0%}: outer bound only", transform=ax.transAxes, ha="center",
                    va="bottom", fontsize=6, style="italic", color="#555555")

    ax.set_xticks(x)
    ax.set_xlim(x[0] - 2, x[-1] + 2)
    ax.grid(axis="y", alpha=0.3)
    return min(lo_base), max(hi_base)


def draw_cell_factor(ax, poly, axis_idx, ranges, region_2020: dict, constrained_region: str, affected_region: str) -> tuple[float, float]:
    """fig16/17's per-cell drawer -- structurally the same as draw_cell (same
    baseline ribbon + z* line over YEARS only, same nested-ribbon marker
    convention on the diagonal), except (1) the induced ribbons come from
    cell_range_factor (2020-investment-multiple caps, not deciles of the
    2030 near-optimal range), (2) a factor certified infeasible for this
    (constrained_region) row (cell_range_factor returns None -- a
    per-region, per-factor outcome, see that function's docstring) is drawn
    as a red italic annotation instead of a ribbon, rather than silently
    omitted, and (3) the marker convention is swapped relative to draw_cell
    (2026-09-07, user request: "make the baseline run with the stars and
    the regions cap with another symbol visible") -- here the baseline z*
    line is marked with stars and the diagonal's fixed cap point with a
    downward triangle (first tried a diamond, replaced 2026-09-07, user
    request: "I don't like that" -- diamond doubled as the baseline marker
    everywhere else in this repo, so it didn't read as distinctly
    "imposed" here; the downward triangle instead reads as a lid pressing
    down onto the cap value), the reverse of draw_cell's diamond-
    baseline/star-cap pairing. An earlier version also plotted
    2020 as a fixed point with the ribbon pinned to it; dropped 2026-09-07
    (user request) back to YEARS only, matching draw_cell."""
    x = [int(y) for y in YEARS]
    base_y, lo_base, hi_base = zip(*[ranges[(affected_region, y)] for y in YEARS])
    _draw_ribbon(ax, x, lo_base, hi_base, REGION_COLOR[affected_region], alpha=0.15, zorder=1)
    ax.plot(x, base_y, color="black", marker="*", markersize=8, linewidth=1.0,
            linestyle="--", alpha=0.8, zorder=15)

    is_diagonal = affected_region == constrained_region
    cy_idx = YEARS.index(CONSTRAINED_YEAR)
    infeasible_factors = []
    for zi, factor in enumerate(FACTORS_2020):
        alpha = _FACTOR_STYLE[factor]
        result = cell_range_factor(poly, axis_idx, ranges, region_2020, constrained_region, affected_region, factor)
        zorder = 2 + zi
        if result is None:
            infeasible_factors.append(factor)
            continue
        lo_scn, hi_scn, method = result
        if method == "inner":
            _draw_ribbon(ax, x, lo_scn, hi_scn, REGION_COLOR[affected_region], alpha=alpha, zorder=zorder)
            if is_diagonal:
                _draw_fixed_star(ax, x[cy_idx], hi_scn[cy_idx], REGION_COLOR[affected_region],
                                 alpha=min(alpha + 0.15, 1.0), size=10, zorder=zorder + 10, marker="v")
        else:
            _draw_ribbon(ax, x, lo_scn, hi_scn, REGION_COLOR[affected_region], alpha=alpha * 0.7,
                         zorder=zorder, linestyle="--")
            ax.text(0.5, 0.06, f"{factor}x: outer bound only", transform=ax.transAxes, ha="center",
                    va="bottom", fontsize=6, style="italic", color="#555555")

    if infeasible_factors:
        labels = ", ".join(f"{f}x" for f in infeasible_factors)
        ax.text(0.5, 0.94, f"{labels}: infeasible\n(below achievable min)", transform=ax.transAxes,
                ha="center", va="top", fontsize=6.5, style="italic", color="#b33333")

    ax.set_xticks(x)
    ax.set_xlim(x[0] - 2, x[-1] + 2)
    ax.grid(axis="y", alpha=0.3)
    return min(lo_base), max(hi_base)


def fig_pairwise_dependencies(poly, axis_idx, ranges, origin, phys) -> None:
    """Lower-triangular 4x4 grid, one panel per region pair at
    PAIRWISE_YEAR: the dashed rectangle is each region's OWN independent
    [lo, hi] (own-axis VMM min/max, from `ranges`) -- what the achievable
    2D region would look like if the two regions moved independently. The
    solid outline is the ACTUAL near-optimal region: the exact 2D
    projection of the convex hull of every certified point in poly.X
    (baseline + VMM extremes + all real iterate solves) -- a linear
    projection of a convex hull is the hull of the projected vertices, so
    this is just ConvexHull on the two projected columns, no approximation
    (same construction fig2_polytope_samples in plot_mga_results.py uses
    for its inner-hull outline, but of the full point set directly rather
    than a rejection-sampled cloud -- there is nothing to approximate when
    drawing an exact hull outline). Real iterate points scattered
    underneath for context (small, translucent), baseline marked with a
    diamond. See the module docstring's WHY section: the outline visibly
    fails to reach the rectangle's top-right (both regions maxed) and
    bottom-left (both minimised) corners -- the shared, fungible epsilon
    cost budget means two regions generally cannot BOTH sit at their own
    individual extreme simultaneously, which is also why capping one
    region's range measurably tightens another's."""
    is_iter = np.array([o == "iterate" for o in origin])
    n = len(REGIONS)
    fig, axes = plt.subplots(n - 1, n - 1, figsize=(3.6 * (n - 1), 3.6 * (n - 1)), squeeze=False)
    first_legend_done = False
    for i in range(1, n):
        for j in range(0, n - 1):
            ax = axes[i - 1, j]
            if j >= i:
                ax.axis("off")
                continue
            rx, ry = REGIONS[j], REGIONS[i]
            jx, jy = axis_idx[f"{rx}_until_{PAIRWISE_YEAR}"], axis_idx[f"{ry}_until_{PAIRWISE_YEAR}"]

            _, lox, hix = ranges[(rx, PAIRWISE_YEAR)]
            _, loy, hiy = ranges[(ry, PAIRWISE_YEAR)]
            ax.add_patch(Rectangle((lox, loy), hix - lox, hiy - loy, fill=False, linestyle="--",
                                    edgecolor="#666666", linewidth=1.3, zorder=2,
                                    label="if independent (own-axis range x own-axis range)" if not first_legend_done else None))

            proj = poly.X[:, [jx, jy]]
            hull = ConvexHull(proj)
            loop = np.append(hull.vertices, hull.vertices[0])
            hull_x = (proj[loop, 0] * poly.scale[jx] + poly.offset[jx]) / 1000
            hull_y = (proj[loop, 1] * poly.scale[jy] + poly.offset[jy]) / 1000
            ax.fill(hull_x, hull_y, color="#6b1f5c", alpha=0.12, zorder=1)
            ax.plot(hull_x, hull_y, color="#6b1f5c", linewidth=1.6, zorder=3,
                    label="actual near-optimal region (convex hull of certified points)" if not first_legend_done else None)

            ax.scatter(phys[is_iter, jx] / 1000, phys[is_iter, jy] / 1000, s=10, color="black", alpha=0.3,
                       linewidths=0, zorder=4, label="real solved points (iterates)" if not first_legend_done else None)
            base_idx = origin.index("z_star")
            ax.scatter([phys[base_idx, jx] / 1000], [phys[base_idx, jy] / 1000], marker="D", s=60, color="black",
                       zorder=5, label="baseline (cost-optimal)" if not first_legend_done else None)
            first_legend_done = True

            ax.set_xlabel(f"{rx.capitalize()} {PAIRWISE_YEAR} (bn EUR)", fontsize=10)
            ax.set_ylabel(f"{ry.capitalize()} {PAIRWISE_YEAR} (bn EUR)", fontsize=10)
            ax.tick_params(labelsize=8)
            ax.grid(alpha=0.25)

    handles, labels = axes[0, 0].get_legend_handles_labels()
    if handles:
        # Placed in the blank upper-right cells (empty axes above the
        # diagonal), well below the suptitle -- an earlier version's
        # loc="upper right" (figure-level, no bbox_to_anchor) sat at the
        # very top of the figure and visibly overlapped the two-line title.
        fig.legend(handles, labels, loc="upper left", bbox_to_anchor=(0.34, 0.86),
                   fontsize=10.5, frameon=False)
    fig.suptitle(
        f"MGA batch4 share tol=0.02 (v9_0): Pairwise Regional Investment Dependencies at {PAIRWISE_YEAR}\n"
        "(dashed rectangle = independent axis ranges; solid outline = actual achievable region -- "
        "missing corners show why one region's cap tightens another's)",
        fontsize=12, fontweight="bold", y=0.99,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    savefig(fig, "fig14_pairwise_dependencies")


def fig_whatif_2020factor(poly, axis_idx, ranges, region_2020: dict, constrained_regions: list, fig_name: str) -> None:
    """fig16/17: structurally fig13's row-per-constrained-region grid again
    (row = region R capped at CONSTRAINED_YEAR=2030, column = induced effect
    on region A's own 2030-2050 range), but the cap is now expressed as a
    MULTIPLE of R's own 2020 (first model year) investment -- "2030
    cumulative investment will grow 2.5x / 3x" -- rather than a decile of
    R's 2030 near-optimal range (2026-09-07, user request). No 2020
    panel/point is plotted (dropped 2026-09-07, user request -- an earlier
    version showed 2020 as a fixed baseline point per region and had the
    ribbon open up from there); the x-axis is YEARS only, exactly like
    fig13.

    `constrained_regions` restricts only the ROWS to a 2-region subset of
    REGIONS -- columns still show all 4 regions' induced effect, in full
    (2026-09-07, user request, revised: an earlier version also cut the
    columns down to the same 2-region subset, which lost the effect on the
    other regions entirely; "keep all [regions] in the columns, but simply
    divide the 4 rows into two plots ... show the effect on all other 3
    regions + the region itself"). The full 4x4 grid was hard to read at a
    glance, so this now renders as two separate 2x4 pairings instead:
    south+west (fig16) and north+east (fig17) constrained, each against all
    4 regions' columns -- see main() for both calls."""
    fig = plt.figure(figsize=(3.6 * len(REGIONS), 3.4 * len(constrained_regions)))
    grid = fig.add_gridspec(len(constrained_regions), len(REGIONS), hspace=0.55, wspace=0.3)
    print(f"  solving 2020-investment-factor what-if LPs ({'/'.join(constrained_regions)} constrained, region capped by "
          f"{CONSTRAINED_YEAR} at {', '.join(f'{f}x' for f in FACTORS_2020)} of its 2020 investment, inner-hull certified)...")
    for i, cr in enumerate(constrained_regions):
        for j, ar in enumerate(REGIONS):
            ax = fig.add_subplot(grid[i, j])
            draw_cell_factor(ax, poly, axis_idx, ranges, region_2020, cr, ar)
            if i == 0:
                ax.set_title(ar.capitalize(), fontsize=11, fontweight="bold")
            if j == 0:
                ax.set_ylabel(f"{cr.capitalize()}\nconstrained\n(bn EUR)", fontsize=8.5)
            if i == len(constrained_regions) - 1:
                ax.set_xticklabels(YEARS, fontsize=8.5)
            else:
                ax.set_xticklabels([])
            ax.tick_params(labelsize=8)
        print(f"    {cr}: done")

    lo = min(a.get_ylim()[0] for a in fig.axes)
    hi = max(a.get_ylim()[1] for a in fig.axes)
    for a in fig.axes:
        a.set_ylim(lo, hi)

    # Marker convention swapped relative to fig13/14's diamond-baseline
    # (2026-09-07, user request -- see draw_cell_factor's docstring): star
    # for the solved baseline (z*) trajectory, downward triangle for the
    # single fixed cap point on the diagonal.
    handles = [Patch(facecolor="#999999", alpha=0.15, label="baseline range")] + [
        Line2D([0], [0], color="black", marker="*", markersize=9, linewidth=1.0, linestyle="--",
               label="baseline (z*)"),
    ] + [
        Patch(facecolor="#999999", alpha=_FACTOR_STYLE[f],
              label=f"capped at {f}x 2020 investment") for f in FACTORS_2020
    ] + [
        Line2D([0], [0], marker="v", color="none", markerfacecolor="#999999", markeredgecolor="#999999",
               markersize=10, label="region's own cap"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=2, fontsize=9, frameon=False,
               bbox_to_anchor=(0.5, -0.07))

    fig.suptitle(
        "Regional Investment Ranges Capped at a Multiple of 2020 Investment\n"
        f"({' & '.join(r.capitalize() for r in constrained_regions)} constrained, effect on all 4 regions)",
        fontsize=12.5, fontweight="bold", y=0.995,
    )
    savefig(fig, fig_name)


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

    # ALL 16 cells share one global y-limit (not just per-column, an earlier
    # version's choice) -- user request, so every panel is directly visually
    # comparable at a glance, at the cost of squashing the smaller regions
    # (east's ~250-1900 bn EUR range) against the largest (west's ~900-3650).
    lo = min(a.get_ylim()[0] for a in fig.axes)
    hi = max(a.get_ylim()[1] for a in fig.axes)
    for a in fig.axes:
        a.set_ylim(lo, hi)

    handles = [Patch(facecolor="#999999", alpha=0.15, label="baseline near-optimal range")] + [
        Line2D([0], [0], color="black", marker="D", markersize=4.5, linewidth=1.0, linestyle="--",
               label="baseline (cost-optimal, z*)"),
    ] + [
        Patch(facecolor="#999999", alpha=_DECILE_STYLE[d],
              label=f"induced range, region capped at lowest {d:.0%}") for d in DECILES
    ] + [
        Line2D([0], [0], marker="*", color="none", markerfacecolor="#999999", markeredgecolor="#999999",
               markersize=13, label=f"constrained region's own {CONSTRAINED_YEAR} (fixed cap, per decile)"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=2, fontsize=9, frameon=False,
               bbox_to_anchor=(0.5, -0.05))

    fig.suptitle(
        "MGA batch4 share tol=0.02 (v9_0): Regional Investment Ranges and \"What-If\" Scenarios\n"
        f"(rows: region capped at its lowest {' / '.join(f'{d:.0%}' for d in DECILES)} by {CONSTRAINED_YEAR}  |  "
        "columns: induced effect on each region's own range)",
        fontsize=13, fontweight="bold", y=0.995,
    )
    savefig(fig, "fig13_regional_investment_whatif")

    fig_pairwise_dependencies(poly, axis_idx, ranges, origin, phys)

    base_r = Results(path=str(RUN_DIR / MODEL))
    region_2020 = compute_region_2020(base_r)
    print("  2020 baseline investment (bn EUR): "
          + ", ".join(f"{r}={v:.0f}" for r, v in region_2020.items()))
    # Two 2x4 row-pairings instead of one 4x4 grid (2026-09-07, user
    # request) -- rows split, columns (all 4 regions) kept full. See
    # fig_whatif_2020factor's docstring.
    fig_whatif_2020factor(poly, axis_idx, ranges, region_2020,
                           constrained_regions=["south", "west"], fig_name="fig16_regional_investment_2020factor")
    fig_whatif_2020factor(poly, axis_idx, ranges, region_2020,
                           constrained_regions=["north", "east"], fig_name="fig17_regional_investment_2020factor_north_east")


if __name__ == "__main__":
    main()
