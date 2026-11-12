"""fig51: what would holding a diffusion rate within a band do to biomass imports and cost?

In the no-diffusion MGA run 47 (parameters_mga.csv task_id 47, industrial-heating thesis
axes, 2022 additions frozen), the share of one technology group (industrial heat
electrification or CCS) is held between the trajectories of two diffusion rates r_diff,
in 2034 and 2050 jointly. The figure shows the range of imported biomass in 2034 and 2050
and the cheapest extra cost under that mandate. Runs 46/47 have no emissions axis, so imported
biomass, its third technology axis, takes the place of run 33's cumulative emissions.
Like fig20 this is answered from the polytope, with no re-solving of ZEN-garden.
Every range edge and cost is one LP over the OUTER approximation (the polytope's cuts
A z <= b; RANGE_BOUND), so ranges are as wide as the near-optimal space can possibly be
and costs are lower limits. The same LPs over the convex hull of the solved designs (inner
approximation) are only printed. With SHOW_OUTER and RANGE_BOUND = inner_bound the figure
shows the inner ranges filled and the outer ones as dashed outlines / open cost dots.

fig51b is fig51 without the biomass column: band paths and cheapest extra cost only, with
the inner hull's cheapest cost (upper limit) as a dashed line and white dot beside the
outer approximation's (lower limit), so the true minimum lies between the two.

fig52 (same bands, same LPs) shows what each mandate does to the other share and to
biomass imports, e.g. CCS use and biomass imports under an industrial heat band, in 2034
and 2050.

The bands set a floor and, in the years where the upper rate's trajectory is below
100%, a ceiling, so their ranges are not nested and can sit apart. Each band is one
shade of the mandated technology's hue, darkening with the rates. The bands are
<10%, 10-20%, 20-30%, 30-50% and 50-70%.

The trajectory is ZEN-garden's global diffusion limit (see
technology_diffusion_limit_constraint.py) reduced to share space:

    d = (1 + r_diff)^dy - 1
    K(y+1) = (1 - delta)^dy * K(y) + dK(y),     K(2022) = s(2022), dK(2022) = 0
    dK(y) = d * K(y) + k_free
    s(y) = min(1, s(y-1) + dK(y))

Spillover, market_share_unbounded, lifetimes and retirement are left out. The
technologies of a group are pooled and demand is taken as constant.

The 2022 values are not polytope axes. Heat and CCS mandates start from existing
capacity in the input data and add the dataset's capacity_addition_unbounded as k_free.
The run's baseline solve is read to check that the axis calculation reproduces the
polytope's baseline point. The run-33 version (heat/EV/CCS, 2030/2038/2050, emissions
column) is in git history; its figures are in mga_tests/archive/run33/.

Usage (zen-garden-plugins-env, PYTHONPATH=../ZEN-garden-plugins):
    python scripts/plot_mga_diffusion_whatif.py
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from contextlib import contextmanager

from matplotlib.colors import to_rgba
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from scipy.optimize import linprog

from plots.figure_settings import REPORT_RC, REPORT_WIDTH, SCENARIO_PALETTE, apply_font_mode, eth_tint
from plots.mga_capex_periods_common import METRIC_COLOR, MODEL, REPO_ROOT, RUN_DIR, savefig
from zen_garden.postprocess.results import Results
from zen_garden_plugins.mga.polytope_io import load_polytope

apply_font_mode()

SHOW_TITLE = False  # figure suptitle; False for the report

RUN_PATH = RUN_DIR / f"{MODEL}_batch_summary" / "polytope.npz"
BASELINE_PATH = RUN_DIR / MODEL
DATASET_TECHNOLOGIES = REPO_ROOT / "data" / "outputs" / "zen-europe-old" / MODEL / "set_technologies"

REFERENCE_YEAR, LAST_YEAR, INTERVAL = 2022, 2050, 4
YEARS = (2034, 2050)
LABEL_YEAR = 2034  # rate labels on the mandate panel sit beside this year's markers
PANEL_YEARS = [REFERENCE_YEAR, *YEARS]
KNOWLEDGE_DEPRECIATION = 0.1  # knowledge_depreciation_rate, per year
SHOW_OUTER = False  # with RANGE_BOUND = inner_bound: also draw the outer bounds as dashed outlines / open dots

# Contiguous bands; None = no upper rate (a minimum only).
RATE_BANDS = ((0.0, 0.10), (0.10, 0.20), (0.20, 0.30), (0.30, 0.50), (0.50, 0.70))
BAND_TINTS = (0.7, 0.52, 0.35, 0.17, 0.0)  # ETH tint per band
BAND_ALPHA = 0.5  # band fills on the mandate panel
BAR_ALPHA = 0.9  # biomass and cost bars, legend
LABEL_MIN_GAP = 7.0  # percentage points between rate labels on the mandate panel
LABEL_TOP_DROP = 6.0  # top rate label sits this far below 100%

AXIS_PREFIX = {
    "heat": "all_industry_heat_electrification",
    "ccs": "all_co2_storage",
    "biomass": "imported_biomass",
}
MANDATE_NAME = {"heat": "industrial heat electrification", "ccs": "CCS"}
TITLE = {
    "heat": "Industrial heat electrified share",
    "ccs": "CCS capacity used",
    "biomass": "Imported biomass",
}
YLABEL = {
    "heat": "% of industrial heat",
    "ccs": "% of CO$_2$ injection limit",
    "biomass": "TWh/yr",
}
FIGURE_NAME = "fig51_diffusion_ranges"
COMPACT_FIGURE_NAME = "fig51b_diffusion_cost"  # fig51 without the biomass column
CROSS_FIGURE_NAME = "fig52_diffusion_cross_shares"  # effect on the other two shares
SHARE_METRICS = ("heat", "ccs")

_GREY = SCENARIO_PALETTE[6]
MANDATE_COLOR = {"heat": METRIC_COLOR["heating"], "ccs": METRIC_COLOR["ccs"]}
INK, MUTED = "#333333", "#6F6F6F"
R_DIFF = r"$r^{\mathrm{diff}}$"

# Sizes of the drawing functions. fig51/52 are screen figures; fig51b (and fig61) are
# report figures at REPORT_WIDTH and use the report sizes (see report_style()).
SIZES = {
    "screen": dict(report=False, title=11, label=9, tick=9, band_label=8.5, value=8, line=2.2, marker=7,
                   dot=9, legend=9),
    "report": dict(report=True, title=9.5, label=9, tick=8, band_label=7, value=7, line=1.4, marker=4,
                   dot=5.5, legend=8),
}
S = dict(SIZES["screen"])


@contextmanager
def report_style():
    """Report sizes and REPORT_RC for the figures built (and saved) inside the block."""
    S.update(SIZES["report"])
    try:
        with plt.rc_context(REPORT_RC):
            yield
    finally:
        S.update(SIZES["screen"])


def panel_title(ax, text: str) -> None:
    ax.set_title(text, fontsize=S["title"], fontweight="bold", color=INK, loc="left")


def diffusion_trajectory(r_diff: float, s0: float, delta: float = KNOWLEDGE_DEPRECIATION,
                         dy: int = INTERVAL, k_free: float = 0.0) -> dict[int, float]:
    """{model year: share}, see the module docstring."""
    d = (1 + r_diff) ** dy - 1
    retained = (1 - delta) ** dy
    stock, added, share = s0, 0.0, s0
    path = {REFERENCE_YEAR: s0}
    for year in range(REFERENCE_YEAR + dy, LAST_YEAR + 1, dy):
        stock = retained * stock + added
        added = d * stock + k_free
        share = min(1.0, share + added)
        path[year] = share
    return path


def to_display(metric: str, value: float) -> float:
    """Axis value in physical units -> as plotted: shares in %, biomass GWh -> TWh."""
    return 1e-3 * value if metric == "biomass" else 100 * value


def initial_values(poly) -> dict[str, float]:
    """2022 value of each metric in the baseline solve, in axis units. Computed like
    the axes; raises if the same calculation misses the polytope's baseline point."""
    results = Results(BASELINE_PATH)
    axes = {axis["name"]: axis for axis in poly.axes}
    axis_idx = {name: i for i, name in enumerate(poly.names)}
    output = results.get_total("flow_conversion_output").groupby(level="technology").sum()
    storage = results.get_total("flow_conversion_input").groupby(level="technology").sum()

    def series(metric: str, year: int):
        axis = axes[f"{AXIS_PREFIX[metric]}_{year}"]
        if metric == "ccs":
            return storage.loc[axis["technologies"]].sum() / axis["limit_utilisation_denominator"]
        return output.reindex(axis["technologies"]).sum() / axis["output_ratio_denominator_baseline"]

    values = {metric: float(series(metric, YEARS[0])[REFERENCE_YEAR]) for metric in SHARE_METRICS}
    for metric in SHARE_METRICS:
        for year in YEARS:
            computed = float(series(metric, year)[year])
            expected = poly.z_star_phys[axis_idx[f"{AXIS_PREFIX[metric]}_{year}"]]
            if abs(computed - expected) > 1e-3:
                raise RuntimeError(f"{metric} {year}: baseline gives {computed}, polytope has {expected}")
    return values


def mandate_start(poly, initial: dict) -> dict[str, tuple[float, float]]:
    """{mandated metric: (2022 share, k_free per period)}, from the input dataset."""
    axes = {axis["name"]: axis for axis in poly.axes}

    def dataset_totals(technologies: list[str]) -> tuple[float, float]:
        """Existing capacity over all nodes, capacity_addition_unbounded per node."""
        existing, unbounded = 0.0, 0.0
        for technology in technologies:
            folder = next(path for path in DATASET_TECHNOLOGIES.rglob(technology) if path.is_dir())
            attributes = yaml.safe_load((folder / "attributes.yaml").read_text())
            unbounded += attributes["capacity_addition_unbounded"]["default_value"]
            if (folder / "capacity_existing.csv").exists():
                existing += pd.read_csv(folder / "capacity_existing.csv")["capacity_existing"].sum()
        return existing, unbounded

    start = {}
    heat = axes[f"{AXIS_PREFIX['heat']}_{YEARS[0]}"]
    existing, unbounded = dataset_totals(heat["technologies"])
    # GW at full load -> GWh/yr, the unit of the denominator.
    to_share = 8760 / heat["output_ratio_denominator_baseline"]
    start["heat"] = (existing * to_share, unbounded * len(heat["members"]) * to_share)
    ccs = axes[f"{AXIS_PREFIX['ccs']}_{YEARS[0]}"]
    existing, unbounded = dataset_totals(ccs["technologies"])
    # tCO2/h -> kt/yr, the unit of the denominator.
    to_share = 8760 / 1000 / ccs["limit_utilisation_denominator"]
    start["ccs"] = (existing * to_share, unbounded * len(ccs["members"]) * to_share)
    return start


def solve_lp(*args, **kwargs):
    """linprog with a retry, since HiGHS can stop on numerics with presolve on. None
    means infeasible; anything else that fails raises."""
    res = linprog(*args, **kwargs, method="highs")
    if res.status not in (0, 2):
        res = linprog(*args, **kwargs, method="highs-ds", options={"presolve": False})
    if res.status == 2:
        return None
    if not res.success:
        raise RuntimeError(f"LP failed: {res.message}")
    return res


def inner_bound(poly, floors, ceilings, j: int, sense: str) -> float | None:
    """Min or max of axis j over the convex hull of poly.X, in physical units."""
    X = poly.X
    rows = [-X[:, k] for k, _ in floors] + [X[:, k] for k, _ in ceilings]
    limits = [-value for _, value in floors] + [value for _, value in ceilings]
    res = solve_lp(X[:, j] * (1.0 if sense == "min" else -1.0),
                   A_ub=np.array(rows) if rows else None, b_ub=limits if rows else None,
                   A_eq=np.ones((1, X.shape[0])), b_eq=[1.0], bounds=(0, None))
    return None if res is None else float(X[:, j] @ res.x) * poly.scale[j] + poly.offset[j]


def outer_bound(poly, floors, ceilings, j: int, sense: str) -> float | None:
    """Min or max of axis j over the outer approximation, in physical units."""
    n = poly.A.shape[1]
    c = np.zeros(n)
    c[j] = 1.0 if sense == "min" else -1.0
    lower, upper = dict(floors), dict(ceilings)
    bounds = [(lower.get(k), upper.get(k)) for k in range(n)]
    res = solve_lp(c, A_ub=poly.A, b_ub=poly.b, bounds=bounds)
    return None if res is None else float(res.x[j]) * poly.scale[j] + poly.offset[j]


RANGE_BOUND = outer_bound  # LPs drawn in fig51/52; inner_bound for the convex hull of the solved designs
RANGE_NAME = "outer approximation" if RANGE_BOUND is outer_bound else "inner hull"
COST_NOTE = " (lower limit)" if RANGE_BOUND is outer_bound else ""


def solve_all(poly, axis_idx, floors, ceilings, bound, metrics: tuple[str, ...]) -> dict | None:
    """{(metric, year): (lo, hi) in %} plus {"cost": (lo, hi) in % above c_star}, or
    None if the mandate cannot be met."""
    ranges = {}
    for metric in metrics:
        for year in YEARS:
            j = axis_idx[f"{AXIS_PREFIX[metric]}_{year}"]
            values = [bound(poly, floors, ceilings, j, s) for s in ("min", "max")]
            if None in values:
                return None
            ranges[metric, year] = tuple(to_display(metric, v) for v in values)
    values = [bound(poly, floors, ceilings, poly.cost_col, s) for s in ("min", "max")]
    if None in values:
        return None
    ranges["cost"] = tuple(100 * (v / poly.c_star - 1) for v in values)
    return ranges


def style_axes(ax, title: str, ylabel: str | None = None) -> None:
    panel_title(ax, title)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=S["label"], color=MUTED)
    ax.tick_params(labelsize=S["tick"], colors=MUTED)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#BBBBBB")


def draw_context(ax, poly, axis_idx, metric: str, context: dict) -> None:
    """Full near-optimal range and the baseline, both from the baseline's 2022 value."""
    start = to_display(metric, context["initial"][metric])
    lows = [start] + [context["full"][metric, y][0] for y in YEARS]
    highs = [start] + [context["full"][metric, y][1] for y in YEARS]
    baseline = [start] + [to_display(metric, poly.z_star_phys[axis_idx[f"{AXIS_PREFIX[metric]}_{y}"]]) for y in YEARS]
    ax.fill_between(PANEL_YEARS, lows, highs, color=_GREY, alpha=0.13, linewidth=0, zorder=1)
    ax.plot(PANEL_YEARS, baseline, color="black", linestyle="--", linewidth=1.0, zorder=6)
    ax.set_xticks(PANEL_YEARS)
    ax.set_xlim(REFERENCE_YEAR - 1, LAST_YEAR + 1)
    ax.grid(axis="y", alpha=0.25)


def draw_mandate_panel(ax, poly, axis_idx, metric: str, scenarios: list, context: dict) -> None:
    draw_context(ax, poly, axis_idx, metric, context)
    for year in YEARS:
        ax.axvline(year, color="#BBBBBB", linewidth=0.8, zorder=2)
    # Rate labels beside the LABEL_YEAR markers, spread downward from the top where lines
    # run close together (several bands reach 100% early).
    # A band whose lower path is already at 100% in LABEL_YEAR is labelled inside its ribbon
    # one period earlier instead, where it is still distinct from the band below.
    inside = {i for i, sc in enumerate(scenarios) if sc["path_upper"] and sc["path"][LABEL_YEAR] >= 0.999}
    # The top label starts a little below 100%, clear of the line along the top.
    label_ys, ceiling = {}, 100 - LABEL_TOP_DROP + LABEL_MIN_GAP
    for i in reversed(range(len(scenarios))):
        path, upper = scenarios[i]["path"], scenarios[i]["path_upper"]
        if i in inside:
            continue
        value = 100 * (upper or path)[LABEL_YEAR]
        label_ys[i] = ceiling = min(value, ceiling - LABEL_MIN_GAP)
    for i, scenario in enumerate(scenarios):
        path, upper = scenario["path"], scenario["path_upper"]
        ax.plot(list(path), [100 * v for v in path.values()], color=scenario["color"], linewidth=S["line"], zorder=8)
        if upper:
            ax.plot(list(upper), [100 * v for v in upper.values()], color=scenario["color"], linewidth=S["line"], zorder=8)
            ax.fill_between(list(path), [100 * v for v in path.values()], [100 * v for v in upper.values()],
                            color=scenario["fill"], alpha=scenario["alpha"], linewidth=0, zorder=7)
        else:
            # A minimum only: everything from its path up to 100% is allowed. Hatched, so
            # the large open area does not hide the other bands.
            ax.fill_between(list(path), [100 * v for v in path.values()], 100, facecolor="none",
                            edgecolor=scenario["fill"], hatch="////", linewidth=0, alpha=0.55, zorder=6)
        reachable = scenario["ranges"] is not None
        ax.plot(YEARS, [100 * path[y] for y in YEARS], linestyle="none", marker="^", markersize=S["marker"],
                markerfacecolor=scenario["color"] if reachable else "white",
                markeredgecolor=scenario["color"], zorder=9)
        if upper:
            capped = [y for y in YEARS if upper[y] < 1.0]
            ax.plot(capped, [100 * upper[y] for y in capped], linestyle="none", marker="v", markersize=S["marker"],
                    markerfacecolor=scenario["color"] if reachable else "white",
                    markeredgecolor=scenario["color"], zorder=9)
        if i in inside:
            mid_year = LABEL_YEAR - INTERVAL
            xy, offset, ha = (mid_year, 50 * (path[mid_year] + upper[mid_year])), (0, 0), "center"
        else:
            xy, offset, ha = (LABEL_YEAR, label_ys[i]), (7, 0), "left"
        ax.annotate(scenario["label"], xy=xy, xytext=offset, textcoords="offset points",
                    ha=ha, va="center", fontsize=S["band_label"], color=INK, zorder=12, annotation_clip=False,
                    bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8, "pad": 1})
    start = 100 * scenarios[0]["path"][REFERENCE_YEAR]
    ax.plot(REFERENCE_YEAR, start, marker="o", markersize=S["marker"], color=INK, zorder=10, clip_on=False)
    ax.set_ylim(0, 105)
    style_axes(ax, TITLE[metric], YLABEL[metric])


def draw_range_bars(ax, poly, axis_idx, metric: str, scenarios: list, context: dict, years) -> None:
    """Range of `metric` per year: the near-optimal range (grey), then one bar per band side
    by side, the outer approximation as dashed outlines (SHOW_OUTER), and the baseline as a
    dashed tick across each group."""
    n = len(scenarios) + 1
    width = 0.84 / n
    full_outer = context.get("full_outer")
    for i, year in enumerate(years):
        bars = [(context["full"][metric, year], full_outer[metric, year] if full_outer else None,
                 _GREY, 0.35, MUTED)] + [
            (s["ranges"][metric, year] if s["ranges"] else None,
             s["outer"][metric, year] if s.get("outer") else None, s["fill"], s["opacity"], s["color"])
            for s in scenarios]
        for b, (span, outer, color, alpha, edge) in enumerate(bars):
            x = i + (b - (n - 1) / 2) * width
            if SHOW_OUTER and outer is not None:
                ax.bar(x, outer[1] - outer[0], bottom=outer[0], width=width * 0.86, facecolor="none",
                       edgecolor=edge, linestyle=(0, (2.5, 1.5)), linewidth=0.9, zorder=4)
            if span is None:
                ax.text(x, 5, "x", ha="center", va="bottom", fontsize=8, color=MUTED)
                continue
            ax.bar(x, span[1] - span[0], bottom=span[0], width=width * 0.86, color=color, alpha=alpha,
                   edgecolor="white", linewidth=0.4, zorder=3)
        baseline = to_display(metric, poly.z_star_phys[axis_idx[f"{AXIS_PREFIX[metric]}_{year}"]])
        ax.plot([i - 0.45, i + 0.45], [baseline] * 2, color="black", linestyle="--", linewidth=1.0, zorder=6)
    ax.set_xticks(range(len(years)), [str(y) for y in years], fontsize=S["tick"])
    ax.set_xlim(-0.55, len(years) - 0.45)
    ax.grid(axis="y", alpha=0.25)


def draw_biomass_bars(ax, poly, axis_idx, scenarios: list, context: dict,
                      title: str | None = TITLE["biomass"], ylabel: str | None = YLABEL["biomass"]) -> None:
    """Imported biomass range per model year."""
    draw_range_bars(ax, poly, axis_idx, "biomass", scenarios, context, YEARS)
    ax.set_ylim(bottom=0)
    style_axes(ax, title or "", ylabel)
    ax.tick_params(axis="x", colors=INK)


def draw_share_bars(ax, poly, axis_idx, metric: str, scenarios: list, context: dict,
                    title: str | None, ylabel: str | None) -> None:
    """Range of another share (not the mandated one) in each model year under each band."""
    draw_range_bars(ax, poly, axis_idx, metric, scenarios, context, YEARS)
    ax.set_ylim(0, 105)
    style_axes(ax, title or "", ylabel)
    ax.tick_params(axis="x", colors=INK)


def extra_cost_bn(percent: float, c_star: float) -> float:
    """Cost above the optimum, % -> bn EUR (c_star is in megaEuro)."""
    return percent / 100 * c_star * 1e-3


INNER_OFFSET = 0.2  # x shift of the inner-hull dot next to the plotted (outer) one


def draw_cost_dots(ax, scenarios: list, c_star: float, top: float, title: str | None,
                   show_inner: bool = False) -> None:
    """Cheapest extra cost of each band as a dot, labelled in bn EUR. The upper end is
    left out: any band can always be met more expensively, up to the cost slack. With
    SHOW_OUTER the outer approximation's cheapest cost is an open dot (a lower bound).
    With show_inner (fig51b) the inner hull's cheapest cost (an upper limit) is drawn
    beside it as a dashed line with a white dot, and the label gives both."""
    for position, scenario in enumerate(scenarios):
        if SHOW_OUTER and scenario.get("outer"):
            ax.plot(position, scenario["outer"]["cost"][0], marker="o", markersize=8, markerfacecolor="white",
                    markeredgecolor=scenario["color"], markeredgewidth=1.4, linestyle="none", zorder=5, clip_on=False)
        if scenario["ranges"] is None:
            ax.text(position, top / 2, "not\nreachable", ha="center", va="center", fontsize=S["value"], color=MUTED)
            continue
        low = scenario["ranges"]["cost"][0]
        if show_inner:
            # fig51b: like fig61, one bar from the outer approximation's cheapest cost (lower
            # limit) to the inner hull's (upper limit); the true minimum lies in between.
            inner = scenario["inner"]
            if inner is None:
                ax.text(position, low, "hull:\nn/a", ha="center", va="bottom", fontsize=S["value"] - 1, color=MUTED)
                continue
            high = inner["cost"][0]
            ax.bar(position, max(high - low, top * 0.01), bottom=low, width=0.5, color=scenario["fill"], alpha=0.8,
                   edgecolor=scenario["color"], linewidth=0.8, zorder=3)
            # (two lines at report width, where five one-line labels would collide)
            label = (f"+{max(0.0, extra_cost_bn(low, c_star)):,.0f} to" + ("\n" if S["report"] else " ")
                     + f"+{max(0.0, extra_cost_bn(high, c_star)):,.0f} bn")
            ax.annotate(label, xy=(position, max(low, high)), xytext=(0, 3), textcoords="offset points",
                        ha="center", va="bottom", fontsize=S["value"], color=INK, linespacing=1.0)
            continue
        ax.plot([position, position], [0, low], color=scenario["fill"], linewidth=S["line"], zorder=3)
        ax.plot(position, low, marker="o", markersize=S["dot"], color=scenario["fill"], markeredgecolor="white",
                markeredgewidth=0.8, zorder=4)
        ax.annotate(f"+{max(0.0, extra_cost_bn(low, c_star)):,.0f} bn", xy=(position, low), xytext=(0, 8),
                    textcoords="offset points", ha="center", va="bottom", fontsize=S["value"], color=INK)
    ax.set_xticks(range(len(scenarios)), [s["label"] for s in scenarios], fontsize=S["tick"])
    ax.set_xlim(-0.6, len(scenarios) - 0.4)
    ax.set_ylim(0, top)
    step = next(step for step in (0.05, 0.1, 0.25, 0.5, 1.0) if top / step <= 6)
    ax.set_yticks(np.arange(0, top, step))
    ax.yaxis.set_major_formatter(lambda v, _: "$C^*$" if v == 0 else f"+{v:g}%")
    ax.grid(axis="y", alpha=0.25)
    style_axes(ax, title or "", "Cost above optimum")
    ax.tick_params(axis="x", colors=INK)


def report(poly, axis_idx, mandated: str, scenarios: list) -> None:
    columns = [axis_idx[f"{AXIS_PREFIX[mandated]}_{y}"] for y in YEARS]
    for scenario in scenarios:
        path, upper = scenario["path"], scenario["path_upper"] or scenario["path"]
        print(f"  {mandated} r_diff {scenario['label']}: " + ", ".join(
            f"{y}: {100 * path[y]:.1f}-{100 * upper[y]:.1f}% (baseline {100 * poly.z_star_phys[j]:.1f}%)"
            for y, j in zip(YEARS, columns)))
        plotted, inner = scenario["ranges"], scenario["inner"]
        if plotted is None:
            print(f"    not reachable ({RANGE_NAME})")
            continue
        low, high = plotted["cost"]
        print(f"    cost above optimum ({RANGE_NAME}): {low:.2f}% to {high:.2f}% "
              f"({extra_cost_bn(low, poly.c_star):,.1f} to {extra_cost_bn(high, poly.c_star):,.1f} bn EUR); "
              + (f"inner hull cheapest {inner['cost'][0]:.2f}%" if inner else "not reachable in the inner hull"))
        nan = (float("nan"),) * 2
        for key, (lo, hi) in plotted.items():
            if key != "cost" and key[0] != mandated:
                i_lo, i_hi = inner[key] if inner else nan
                print(f"    {key[0]:4s} {key[1]}: {RANGE_NAME} [{lo:6.1f}, {hi:6.1f}]  inner [{i_lo:6.1f}, {i_hi:6.1f}]")


def make_scenario(poly, axis_idx, mandated: str, start: tuple[float, float], rate: float,
                  upper_rate: float | None = None) -> dict:
    """Trajectories and ranges of one mandate: at least `rate`, and at most `upper_rate`
    if given. A trajectory at 100% caps nothing, so it adds no ceiling."""
    prefix = AXIS_PREFIX[mandated]
    path = diffusion_trajectory(rate, start[0], k_free=start[1])
    upper = diffusion_trajectory(upper_rate, start[0], k_free=start[1]) if upper_rate else None
    floors, ceilings = [], []
    for year in YEARS:
        k = axis_idx[f"{prefix}_{year}"]
        floors.append((k, (path[year] - poly.offset[k]) / poly.scale[k]))
        if upper and upper[year] < 1.0:
            ceilings.append((k, (upper[year] - poly.offset[k]) / poly.scale[k]))
    metrics = ("biomass",) + tuple(m for m in SHARE_METRICS if m != mandated)
    return {"path": path, "path_upper": upper,
            "ranges": solve_all(poly, axis_idx, floors, ceilings, RANGE_BOUND, metrics),
            "outer": solve_all(poly, axis_idx, floors, ceilings, outer_bound, metrics) if SHOW_OUTER else None,
            "inner": solve_all(poly, axis_idx, floors, ceilings, inner_bound, metrics)}  # printed only


def band_scenarios(poly, axis_idx, mandated: str, start: tuple[float, float]) -> list[dict]:
    """Bands, not nested, so each is a solid shade that darkens with the rates."""
    hue = MANDATE_COLOR[mandated]
    scenarios = []
    for (low, high), tint in zip(RATE_BANDS, BAND_TINTS):
        if high is None:
            label = f">{low:.0%}"
        elif low == 0:
            label = f"$<${high:.0%}"  # mathtext: cmr10 has no "<" glyph
        else:
            label = f"{low:.0%}".rstrip("%") + f"-{high:.0%}"
        scenarios.append(make_scenario(poly, axis_idx, mandated, start, low, high)
                         | {"label": label, "legend": f"{R_DIFF} {label}", "color": eth_tint(hue, tint),
                            "fill": eth_tint(hue, tint), "alpha": BAND_ALPHA, "opacity": BAR_ALPHA})
    return scenarios


def solve_bands(poly, axis_idx, initial: dict, starts: dict) -> dict:
    """{mandated metric: (band scenarios, context)}, shared by fig51, fig51b and fig52."""
    metrics = SHARE_METRICS
    rows = {}
    for metric in metrics:
        print(f"bands on {metric}: 2022 start {100 * starts[metric][0]:.2f}%, k_free {100 * starts[metric][1]:.2f}% per period")
        scenarios = band_scenarios(poly, axis_idx, metric, starts[metric])
        report(poly, axis_idx, metric, scenarios)
        context = {"initial": initial,
                   "full": solve_all(poly, axis_idx, [], [], RANGE_BOUND, (*SHARE_METRICS, "biomass")),
                   "full_outer": solve_all(poly, axis_idx, [], [], outer_bound, (*SHARE_METRICS, "biomass"))
                   if SHOW_OUTER else None}
        rows[metric] = (scenarios, context)
    return rows


def make_figure(rows: dict, poly, axis_idx, with_biomass: bool = True, name: str = FIGURE_NAME) -> None:
    """One row per technology group: band paths, imported biomass (fig51 only), cheapest
    extra cost. Biomass and cost share their y-axis down the column."""
    metrics = SHARE_METRICS
    show_inner = not with_biomass  # fig51b also draws the inner hull's cheapest cost
    cheapest = max(s["ranges"]["cost"][0] for scenarios, _ in rows.values() for s in scenarios if s["ranges"])
    if show_inner:
        cheapest = max([cheapest] + [s["inner"]["cost"][0] for scenarios, _ in rows.values()
                                     for s in scenarios if s["inner"]])
    cost_top = max(cheapest * 1.3, 0.1)  # outer costs can all be ~0

    n_cols = 3 if with_biomass else 2
    n_legend_rows = 3 if show_inner or SHOW_OUTER else 2
    if S["report"]:  # report width; legend rows of 0.2 in under the x tick labels
        height, row_in = 5.6, 0.2
        layout = dict(left=0.1, right=0.99, top=0.95, bottom=(0.42 + n_legend_rows * row_in) / height,
                      wspace=0.42, hspace=0.42)
        fig = plt.figure(figsize=(REPORT_WIDTH, height))
    else:
        height, row_in = 9.0, 0.315
        left = 0.07 if with_biomass else 0.09
        layout = dict(left=left, right=0.98, top=0.91, bottom=0.16 if with_biomass else 0.19, wspace=0.3, hspace=0.38)
        fig = plt.figure(figsize=(13.5 if with_biomass else 10.0, height))
    grid = fig.add_gridspec(len(metrics), n_cols, width_ratios=[1.15, 1, 1][:n_cols], **layout)
    biomass_axes = []
    letters = iter("abcdefgh")
    for r, metric in enumerate(metrics):
        scenarios, context = rows[metric]
        ax = fig.add_subplot(grid[r, 0])
        draw_mandate_panel(ax, poly, axis_idx, metric, scenarios, context)
        if S["report"]:
            panel_title(ax, f"({next(letters)}) {TITLE[metric]}")
        if with_biomass:
            ax = fig.add_subplot(grid[r, 1], sharey=biomass_axes[0] if biomass_axes else None)
            draw_biomass_bars(ax, poly, axis_idx, scenarios, context, title=TITLE["biomass"] if r == 0 else None)
            biomass_axes.append(ax)
        cost_title = "Cheapest extra cost" if show_inner else f"Cheapest extra cost{COST_NOTE}"
        if S["report"]:  # every panel gets its "(x) ..." header
            cost_title = f"({next(letters)}) {cost_title}"
        elif r:
            cost_title = None
        draw_cost_dots(fig.add_subplot(grid[r, n_cols - 1]), scenarios, poly.c_star, cost_top,
                       cost_title, show_inner=show_inner)

    effect = "biomass imports and cost" if with_biomass else "cost"
    approximations = f"{RANGE_NAME}; cost also inner hull" if show_inner else RANGE_NAME
    if SHOW_TITLE:  # off for the thesis figures (caption carries the title)
        fig.suptitle(f"Diffusion rate bands: effect on {effect} ({approximations})", fontsize=14, fontweight="bold",
                     color=INK, x=layout["left"], ha="left", y=0.985)
    labels = [s["label"] for s in rows["heat"][0]]
    # Legend in rows: diffusion rate bands / context and imposed limits / cost markers.
    legend_rows = [
        [Patch(facecolor=eth_tint(_GREY, tint), label=f"{R_DIFF} {label}")
         for label, tint in zip(labels, BAND_TINTS)],
        [
            Patch(facecolor=_GREY, alpha=0.35, label=f"Near-optimal space ({RANGE_NAME})"),
            Line2D([0], [0], color="black", linestyle="--", linewidth=1.0, label="Cost-optimal baseline"),
            Line2D([0], [0], marker="^", color="none", markerfacecolor=MUTED, markeredgecolor=MUTED, markersize=S["marker"],
                   label="Imposed minimum"),
            Line2D([0], [0], marker="v", color="none", markerfacecolor=MUTED, markeredgecolor=MUTED, markersize=S["marker"],
                   label="Imposed maximum"),
        ],
        [],
    ]
    if show_inner:
        legend_rows[2] += [
            Patch(facecolor=eth_tint(_GREY, 0.35), edgecolor=MUTED, linewidth=0.8,
                  label="Cheapest extra cost: from outer approximation (lower limit) "
                        "to inner hull (upper limit)"),
        ]
    if SHOW_OUTER:
        legend_rows[2] += [
            Patch(facecolor="none", edgecolor=MUTED, linestyle=(0, (2.5, 1.5)), linewidth=0.9,
                  label="Outer approximation (biomass)"),
        ] * with_biomass + [
            Line2D([0], [0], marker="o", color="none", markerfacecolor="white", markeredgecolor=MUTED,
                   markeredgewidth=1.4, markersize=8, label="Outer approximation (cost)"),
        ]
    legend_rows = [row for row in legend_rows if row]
    row_height = row_in / height
    for i, row in enumerate(legend_rows):
        fig.legend(handles=row, loc="lower center", ncol=len(row), fontsize=S["legend"], frameon=False,
                   bbox_to_anchor=(0.52, row_height * (len(legend_rows) - 1 - i)),
                   columnspacing=1.2 if S["report"] else 1.6, handlelength=1.2 if S["report"] else 2.0,
                   handletextpad=0.5 if S["report"] else 0.6)
    savefig(fig, name)


def make_cross_figure(rows: dict, poly, axis_idx) -> None:
    """fig52: one row per mandated group; columns: the other share, imported biomass."""
    fig, axes = plt.subplots(len(SHARE_METRICS), 2, figsize=(11, 8.8), sharey="col")
    fig.subplots_adjust(left=0.13, right=0.98, top=0.88, bottom=0.17, wspace=0.22, hspace=0.42)
    for r, mandated in enumerate(SHARE_METRICS):
        scenarios, context = rows[mandated]
        other = next(m for m in SHARE_METRICS if m != mandated)
        draw_share_bars(axes[r, 0], poly, axis_idx, other, scenarios, context, TITLE[other], YLABEL[other])
        draw_biomass_bars(axes[r, 1], poly, axis_idx, scenarios, context)
        axes[r, 0].annotate(f"Band on {MANDATE_NAME[mandated]}", xy=(0, 0.5), xycoords="axes fraction",
                            xytext=(-62, 0), textcoords="offset points", rotation=90, ha="center",
                            va="center", fontsize=11, fontweight="bold", color=MANDATE_COLOR[mandated])
    fig.suptitle(f"Diffusion rate bands: effect on the other share and on biomass imports ({RANGE_NAME})", fontsize=14, fontweight="bold",
                 color=INK, x=0.13, ha="left", y=0.975)
    labels = [s["label"] for s in rows["heat"][0]]
    handles = [Patch(facecolor=eth_tint(_GREY, tint), label=f"{R_DIFF} {label}")
               for label, tint in zip(labels, BAND_TINTS)] + [
        Patch(facecolor=_GREY, alpha=0.35, label=f"Near-optimal space ({RANGE_NAME})"),
        Line2D([0], [0], color="black", linestyle="--", linewidth=1.0, label="Cost-optimal baseline"),
    ]
    if SHOW_OUTER:
        handles.append(Patch(facecolor="none", edgecolor=MUTED, linestyle=(0, (2.5, 1.5)), linewidth=0.9,
                             label="Outer approximation"))
    fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=9, frameon=False, bbox_to_anchor=(0.55, 0.0),
               columnspacing=1.6, handletextpad=0.6,
               title="Bar shade = band on the row's technology, lighter = slower (hue per technology)",
               title_fontsize=9)
    savefig(fig, CROSS_FIGURE_NAME)


def main() -> None:
    poly = load_polytope(RUN_PATH)
    print(f"loaded {poly.X.shape[0]} points, converged={poly.converged}, final_gap={poly.final_gap:.3f}")
    axis_idx = {name: i for i, name in enumerate(poly.names)}
    initial = initial_values(poly)
    print("baseline 2022:", {metric: round(value, 4) for metric, value in initial.items()})
    rows = solve_bands(poly, axis_idx, initial, mandate_start(poly, initial))
    make_figure(rows, poly, axis_idx)
    with report_style():  # fig51b is a report figure
        make_figure(rows, poly, axis_idx, with_biomass=False, name=COMPACT_FIGURE_NAME)
    make_cross_figure(rows, poly, axis_idx)


if __name__ == "__main__":
    main()
