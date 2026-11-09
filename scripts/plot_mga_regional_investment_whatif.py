"""Regional investment "what-if" figures: fig20 (north capped) and fig21 (south
capped), with that region's cumulative CAPEX capped at absolute bn-EUR values,
until 2030 in the upper block and until 2050 in the lower block. Within a block,
rows are the affected region (north above south) and columns the affected metric
(CAPEX, emissions, transport share, heating share). Answered from the polytope
of MGA run 21 (RUN21_* in plots/mga_capex_periods_common.py), with no re-solving of
ZEN-garden.

Every LP solves over the CONVEX HULL of poly.X (baseline, min/max solves and
iterations). Any convex combination of near-optimal points is near-optimal
because the model is convex, so each bound is achievable, not merely "not yet
ruled out" as with the outer cutting-plane approximation. If the hull cannot
reach a cap, solve_bound_with_fallback uses the outer approximation and the
figure labels it "outer bound only".

Capping one region also lowers other regions' upper bound because the near-
optimality budget is one shared pool: two axes can't both deviate far from
baseline unless their combined cost stays within it.

Usage:
    python scripts/plot_mga_regional_investment_whatif.py
"""

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from scipy.optimize import linprog

from plots.figure_settings import apply_font_mode
from plots.mga_capex_periods_common import (
    METRIC_COLOR,
    RUN21_METRIC_COLUMNS as METRIC_COLUMNS,
    METRIC_IS_CUMULATIVE,
    METRIC_LABEL,
    RUN21_POLY_PATH as POLY_PATH,
    REGION_COLOR,
    RUN21_REGIONS as REGIONS,
    REPO_ROOT,
    RUN21_YEARS as YEARS,
    axis_name,
    display_unit,
    RUN21_FIGURES_SUBDIR,
    savefig,
)

# Match the rest of the MGA scripts / MT_report_HG's font -- see
# figure_settings.FONT_MODE for the rationale and for the one-flag toggle
# that switches every figure script in this repo at once.
apply_font_mode()
from zen_garden_plugins.mga.polytope_io import load_polytope

def load_data():
    """(poly, axis_idx, origin, phys, base): the loaded Polytope (poly.X is
    every certified near-optimal point this run solved -- baseline + VMM
    extremes + iterates -- and poly.A/b its outer cutting-plane system), a
    name->column index map, each solved point's origin label, every solved
    point's physical-unit vector (poly.X is stored normalised; to_phys
    converts back), and the baseline (z_star) vector."""
    if not POLY_PATH.exists():
        raise FileNotFoundError(f"polytope not found at {POLY_PATH}")
    poly = load_polytope(POLY_PATH)
    axis_idx = {n: i for i, n in enumerate(poly.names)}
    origin = list(poly.point_origin)
    phys = np.array([poly.to_phys(x) for x in poly.X])
    base = phys[origin.index("z_star")]
    print(f"  loaded {len(origin)} points from {POLY_PATH.relative_to(REPO_ROOT)} "
          f"(converged={poly.converged}, final_gap={poly.final_gap:.3f})")
    return poly, axis_idx, origin, phys, base


def compute_ranges(poly, axis_idx, origin, phys, base) -> dict:
    """{(region, metric, year): (baseline, lo, hi)} in display units, from each
    axis's own min/max solve. Drawn as each cell's faint backdrop ribbon."""
    ranges = {}
    for region in REGIONS:
        for metric in METRIC_COLUMNS:
            for year in YEARS:
                ax = axis_name(region, metric, year)
                j = axis_idx[ax]
                factor, _ = display_unit(poly.units[j])
                ranges[(region, metric, year)] = (
                    base[j] * factor,
                    phys[origin.index(f"min:{ax}")][j] * factor,
                    phys[origin.index(f"max:{ax}")][j] * factor,
                )
    return ranges


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
    defaults to the star; draw_cell_abs instead reserves the star
    for the baseline (z*) line and marks this cap point with a downward
    triangle (a diamond first, then this, both 2026-09-07 user requests:
    "make the baseline run with the stars and the regions cap with another
    symbol" -- the triangle reads as a lid pressing down onto the cap
    value)."""
    ax.plot(x0, value, marker=marker, markersize=size, color=color, alpha=alpha,
            markeredgecolor=color, linestyle="none", zorder=zorder)


# One region capped at a time, on its cumulative CAPEX until the given year.
# Near-optimal range of those axes [min, max], baseline (bn EUR):
#   north 2030 [3,555, 6,810], 4,169    north 2050 [6,396, 10,751], 7,714
#   south 2030 [3,640, 6,602], 4,014    south 2050 [6,045, 10,365], 7,199
# All caps sit below baseline, so even the cost-optimal path would have to
# change. Loosest first (most translucent).
CAPS_ABS = {
    "north": {"2030": [4000, 3800, 3600], "2050": [7500, 7000, 6500]},
    "south": {"2030": [3900, 3800, 3700], "2050": [7000, 6500, 6100]},
}
_CAP_ALPHAS = [0.25, 0.5, 0.85]


def threshold_abs_norm(poly, axis_idx, region: str, year: str, thresh_bn: float) -> tuple[str, float]:
    """(axis_name, normalised upper bound) for region's `year` axis capped
    directly at `thresh_bn` (bn EUR) -- an absolute value with no
    per-region derivation."""
    ax = f"{region}_until_{year}"
    k = axis_idx[ax]
    return ax, ((thresh_bn * 1000) - poly.offset[k]) / poly.scale[k]


def cell_range_abs(poly, axis_idx, ranges, constrained_region: str, cap_year: str, affected_region: str,
                   metric: str, thresh_bn: float):
    """(lo, hi, method, binding) across YEARS for one affected region and metric,
    in display units, with constrained_region's CAPEX capped at thresh_bn on its
    cap_year axis. None if the cap is below that axis's achievable minimum."""
    _, lo_c, hi_c = ranges[(constrained_region, "capex", cap_year)]
    if thresh_bn < lo_c:
        return None
    axis_name_capped, bound = threshold_abs_norm(poly, axis_idx, constrained_region, cap_year, thresh_bn)
    thresholds_norm = {axis_name_capped: bound}
    lo_out, hi_out, method = [], [], "inner"
    for y in YEARS:
        if metric == "capex" and affected_region == constrained_region and y == cap_year:
            lo_out.append(lo_c)
            hi_out.append(min(thresh_bn, hi_c))
            continue
        target_axis = axis_name(affected_region, metric, y)
        factor, _ = display_unit(poly.units[axis_idx[target_axis]])
        lo_v, m_lo = solve_bound_with_fallback(poly, axis_idx, thresholds_norm, target_axis, "min")
        hi_v, m_hi = solve_bound_with_fallback(poly, axis_idx, thresholds_norm, target_axis, "max")
        lo_out.append(lo_v * factor)
        hi_out.append(hi_v * factor)
        if m_lo == "outer" or m_hi == "outer":
            method = "outer"
    return lo_out, hi_out, method, thresh_bn < hi_c


def draw_cell_abs(ax, poly, axis_idx, ranges, constrained_region: str, cap_year: str, affected_region: str,
                  metric: str, caps: list, style: dict) -> None:
    """One cell: full near-optimal range, baseline, and nested ribbons per cap
    (tightest last and most opaque). Infeasible or non-binding caps are labelled."""
    x = [int(y) for y in YEARS]
    color = REGION_COLOR[affected_region]
    base_y, lo_base, hi_base = zip(*[ranges[(affected_region, metric, y)] for y in YEARS])
    _draw_ribbon(ax, x, lo_base, hi_base, color, alpha=0.15, zorder=1)
    ax.plot(x, base_y, color="black", marker="*", markersize=8, linewidth=1.0,
            linestyle="--", alpha=0.8, zorder=15)

    is_capped_axis = metric == "capex" and affected_region == constrained_region
    cy_idx = YEARS.index(cap_year)
    infeasible_caps, non_binding_caps = [], []
    for zi, cap in enumerate(caps):
        alpha = style[cap]
        result = cell_range_abs(poly, axis_idx, ranges, constrained_region, cap_year, affected_region, metric, cap)
        zorder = 2 + zi
        if result is None:
            infeasible_caps.append(cap)
            continue
        lo_scn, hi_scn, method, binding = result
        if not binding:
            non_binding_caps.append(cap)
        if method == "inner":
            _draw_ribbon(ax, x, lo_scn, hi_scn, color, alpha=alpha, zorder=zorder)
            if is_capped_axis:
                _draw_fixed_star(ax, x[cy_idx], hi_scn[cy_idx], color,
                                 alpha=min(alpha + 0.15, 1.0), size=10, zorder=zorder + 10, marker="v")
        else:
            _draw_ribbon(ax, x, lo_scn, hi_scn, color, alpha=alpha * 0.7, zorder=zorder, linestyle="--")
            ax.text(0.5, 0.06, f"{cap:,.0f} bn EUR: outer bound only", transform=ax.transAxes, ha="center",
                    va="bottom", fontsize=6, style="italic", color="#555555")

    if infeasible_caps:
        labels = ", ".join(f"{c:,.0f}" for c in infeasible_caps)
        ax.text(0.5, 0.94, f"{labels} bn EUR: infeasible\n(below achievable min)", transform=ax.transAxes,
                ha="center", va="top", fontsize=6.5, style="italic", color="#b33333")
    elif non_binding_caps:
        labels = ", ".join(f"{c:,.0f}" for c in non_binding_caps)
        ax.text(0.5, 0.94, f"{labels} bn EUR: not binding\n(above achievable range)", transform=ax.transAxes,
                ha="center", va="top", fontsize=6, style="italic", color="#2a6f2a")

    ax.set_xticks(x)
    ax.set_xlim(x[0] - 2, x[-1] + 2)
    ax.grid(axis="y", alpha=0.3)


def fig_region_abs_cap(poly, axis_idx, ranges, region: str, caps_by_year: dict, fig_name: str) -> None:
    """`region` capped, one block per cap year: rows = affected region, columns = metric."""
    n_rows, n_cols = len(REGIONS), len(METRIC_COLUMNS)
    fig = plt.figure(figsize=(3.2 * n_cols, 2.6 * n_rows * len(caps_by_year) + 1.2))
    outer = fig.add_gridspec(len(caps_by_year), 1, hspace=0.22, left=0.07, right=0.98, top=0.92, bottom=0.1)
    top_axes = {}
    col_axes: list = [None] * n_cols
    for block, (cap_year, caps) in enumerate(caps_by_year.items()):
        print(f"  solving what-if LPs ({region} capped until {cap_year} at "
              f"{', '.join(f'{c:.0f}' for c in caps)} bn EUR)...")
        style = dict(zip(caps, _CAP_ALPHAS))
        inner = outer[block].subgridspec(n_rows, n_cols, hspace=0.1, wspace=0.34)
        for i, affected in enumerate(REGIONS):
            for j, metric in enumerate(METRIC_COLUMNS):
                ax = fig.add_subplot(inner[i, j], sharey=col_axes[j])
                col_axes[j] = col_axes[j] or ax
                draw_cell_abs(ax, poly, axis_idx, ranges, region, cap_year, affected, metric, caps, style)
                ax.tick_params(labelsize=8, labelleft=True, labelbottom=i == n_rows - 1)
                if block == 0 and i == 0:
                    ax.set_title(METRIC_LABEL[metric], fontsize=11, fontweight="bold",
                                 color=METRIC_COLOR[metric], pad=20)
                if i == 0 and j == 0:
                    top_axes[cap_year] = ax
                _, unit_label = display_unit(poly.units[axis_idx[axis_name(affected, metric, YEARS[0])]])
                scope = "until year" if METRIC_IS_CUMULATIVE[metric] else "in year"
                ylabel = f"{scope} [{unit_label}]"
                if j == 0:
                    ylabel = f"$\\bf{{{affected.capitalize()}}}$\n{ylabel}"
                ax.set_ylabel(ylabel, fontsize=8.5)

    for cap_year, caps in caps_by_year.items():
        position = top_axes[cap_year].get_position()
        fig.text(position.x0, position.y1 + 0.006,
                 f"{region.capitalize()} CAPEX until {cap_year} capped at "
                 f"{' / '.join(f'{c:,.0f}' for c in caps)} bn EUR (light to dark)",
                 fontsize=9.5, fontweight="bold", ha="left", va="bottom")

    left_col = [
        Patch(facecolor="#999999", alpha=0.15, label="full near-optimal range"),
        Line2D([0], [0], color="black", marker="*", markersize=9, linewidth=1.0, linestyle="--",
               label="cost-optimal baseline"),
        Line2D([0], [0], marker="v", color="none", markerfacecolor="#999999", markeredgecolor="#999999",
               markersize=10, label="capped region's own cap"),
    ]
    right_col = [Patch(facecolor="#999999", alpha=alpha, label=label)
                 for alpha, label in zip(_CAP_ALPHAS, ("loosest cap", "middle cap", "tightest cap"))]
    fig.suptitle(f"{region.capitalize()} capped: effect of limiting its cumulative CAPEX",
                 fontsize=12, fontweight="bold", y=0.985)
    fig.legend(handles=left_col + right_col, loc="lower center", ncol=2, fontsize=9, frameon=False)
    savefig(fig, fig_name, RUN21_FIGURES_SUBDIR)


def main() -> None:
    poly, axis_idx, origin, phys, base = load_data()
    ranges = compute_ranges(poly, axis_idx, origin, phys, base)
    for number, region in zip((20, 21), REGIONS):
        fig_region_abs_cap(poly, axis_idx, ranges, region, CAPS_ABS[region],
                           fig_name=f"fig{number}_{region}_investment_caps")


if __name__ == "__main__":
    main()
