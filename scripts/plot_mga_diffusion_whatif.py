"""fig51a-c: what would holding a diffusion rate within a band do to emissions and cost?

In the no-diffusion MGA run (parameters_mga.csv task_id 32), the share of one
technology group (industrial heat electrification, EVs or CCS) is held between the
trajectories of two diffusion rates r_diff, in 2030, 2038 and 2050 jointly. The figure
shows the range of cumulative emissions and the cheapest extra cost under that
mandate; the other shares stay free between 0 and 100%, so they are not plotted.
Like fig20 this is answered from the polytope, with no re-solving of ZEN-garden:
every ribbon edge is one LP over the convex hull of the solved designs. Lower and upper edges generally belong
to different designs. 2040 is not a model year, hence 2038.

The bands set a floor and, in the years where the upper rate's trajectory is below
100%, a ceiling, so their ranges are not nested and can sit apart. Each band is one
shade of the mandated technology's hue, darkening with the rates.

The trajectory is ZEN-garden's global diffusion limit (see
technology_diffusion_limit_constraint.py) reduced to share space:

    d = (1 + r_diff)^dy - 1
    K(y+1) = (1 - delta)^dy * K(y) + dK(y),     K(2022) = s(2022), dK(2022) = 0
    dK(y) = d * K(y) + k_free
    s(y) = min(1, s(y-1) + dK(y))

Spillover, market_share_unbounded, lifetimes and retirement are left out. The
technologies of a group are pooled and demand is taken as constant.

The 2022 values are not polytope axes. The baseline and the ranges start from the
run's baseline solve, computed like the axes and checked against the polytope's
baseline point. Without diffusion limits the model chooses those freely: it builds
15.8 GW of electrode boilers in 2022, giving 35.5% electrified heat from 0.4%
existing. Heat and CCS mandates therefore start from existing capacity in the input
data instead, and add the dataset's capacity_addition_unbounded as k_free. EV
mandates start from the baseline's 2022 share, which follows from the input data.

Usage (zen-garden-plugins-env, PYTHONPATH=../ZEN-garden-plugins):
    python scripts/plot_mga_diffusion_whatif.py
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from matplotlib.colors import to_rgba
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from scipy.optimize import linprog

from plots.figure_settings import SCENARIO_PALETTE, apply_font_mode, eth_tint
from plots.mga_capex_periods_common import MGA_ROOT, REPO_ROOT, savefig
from zen_garden.postprocess.results import Results
from zen_garden_plugins.mga.polytope_io import load_polytope

apply_font_mode()

MODEL = "zen_europe_ind_heat_v1_no_flexibility_nodiffusion_export0"
RUN_SUFFIX = (
    "2022_8a_4a_interval_1ts_MGA_AXES_OUTPUT_EXP0_1REG_CO2STORE"
    "_batch_bbofast_minmax_batch16_tol015_eps007"
)
RUN_DIR = MGA_ROOT / f"{MODEL}_{RUN_SUFFIX}"
RUN_32_PATH = RUN_DIR / f"{MODEL}_batch_summary" / "polytope.npz"
BASELINE_PATH = RUN_DIR / MODEL
DATASET_TECHNOLOGIES = REPO_ROOT / "data" / "outputs" / "zen-europe-old" / MODEL / "set_technologies"

REFERENCE_YEAR, LAST_YEAR, INTERVAL = 2022, 2050, 4
YEARS = (2030, 2038, 2050)
PANEL_YEARS = [REFERENCE_YEAR, *YEARS]
KNOWLEDGE_DEPRECIATION = 0.1  # knowledge_depreciation_rate, per year
BUDGET_MT = 23_838.8  # carbon_emissions_budget of the dataset, 23.8388 Gt
SHOW_OUTER = False  # draw the outer bounds as dashed lines (always printed)

RATE_BANDS = ((0.0, 0.05), (0.10, 0.15), (0.20, 0.25), (0.30, 0.35), (0.40, 0.45), (0.50, 0.55))
BAND_TINTS = (0.8, 0.65, 0.5, 0.35, 0.2, 0.0)  # ETH tint per band
BAND_ALPHA = 0.5
LABEL_MIN_GAP = 4.0  # percentage points between rate labels on the mandate panel

AXIS_PREFIX = {
    "heat": "all_industry_heat_electrification",
    "ev": "all_passenger_road_electrification",
    "ccs": "all_co2_storage",
    "co2": "all_co2_until",
}
OTHER_NAME = {"heat": "electrified industrial heat share", "ev": "EV share", "ccs": "CCS utilisation"}
MANDATE_NAME = {"heat": "industrial heat electrification", "ev": "EVs", "ccs": "CCS"}
TITLE = {
    "heat": "Industrial heat electrified share",
    "ev": "EV share of passenger road",
    "ccs": "CCS capacity used",
    "co2": "Cumulative emissions",
}
YLABEL = {
    "heat": "% of industrial heat",
    "ev": "% of passenger road",
    "ccs": "% of CO$_2$ injection limit",
    "co2": "% of 2050 budget (23.8 Gt)",
}
BAND_FIGURES = {"heat": "fig51a_heat_diffusion_ranges", "ev": "fig51b_ev_diffusion_ranges",
                "ccs": "fig51c_ccs_diffusion_ranges"}

_BLUE, _, _, _, _RED, _PURPLE, _GREY = SCENARIO_PALETTE
MANDATE_COLOR = {"heat": _RED, "ev": _BLUE, "ccs": _PURPLE}
INK, MUTED = "#333333", "#6F6F6F"
R_DIFF = r"$r^{\mathrm{diff}}$"


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
    """Axis value in physical units -> percent as plotted."""
    return 100 * value / BUDGET_MT if metric == "co2" else 100 * value


def initial_values(poly) -> dict[str, float]:
    """2022 value of each metric in the baseline solve, in axis units. Computed like
    the axes; raises if the same calculation misses the polytope's baseline point."""
    results = Results(BASELINE_PATH)
    axes = {axis["name"]: axis for axis in poly.axes}
    axis_idx = {name: i for i, name in enumerate(poly.names)}
    output = results.get_total("flow_conversion_output").groupby(level="technology").sum()
    storage = results.get_total("flow_conversion_input").groupby(level="technology").sum()
    annual = results.get_total("carbon_emissions_annual")

    def series(metric: str, year: int):
        axis = axes[f"{AXIS_PREFIX[metric]}_{year}"]
        if metric == "ccs":
            return storage.loc[axis["technologies"]].sum() / axis["limit_utilisation_denominator"]
        return output.reindex(axis["technologies"]).sum() / axis["output_ratio_denominator_baseline"]

    values = {metric: float(series(metric, YEARS[0])[REFERENCE_YEAR]) for metric in ("heat", "ev", "ccs")}
    # until_<year> axes expand each model year over its interval.
    values["co2"] = float(annual[REFERENCE_YEAR]) * INTERVAL
    for metric in ("heat", "ev", "ccs"):
        for year in YEARS:
            computed = float(series(metric, year)[year])
            expected = poly.z_star_phys[axis_idx[f"{AXIS_PREFIX[metric]}_{year}"]]
            if abs(computed - expected) > 1e-3:
                raise RuntimeError(f"{metric} {year}: baseline gives {computed}, polytope has {expected}")
    for year in YEARS:
        # The final model year counts once, it has no interval after it.
        computed = sum(float(annual[y]) * (1 if y == LAST_YEAR else INTERVAL) for y in annual.index if y <= year)
        expected = poly.z_star_phys[axis_idx[f"{AXIS_PREFIX['co2']}_{year}"]]
        if abs(computed - expected) > 1.0:
            raise RuntimeError(f"emissions until {year}: baseline gives {computed}, polytope has {expected}")
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
    start["ev"] = (initial["ev"], 0.0)
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
    ax.set_title(title, fontsize=11, fontweight="bold", color=INK, loc="left")
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=9, color=MUTED)
    ax.tick_params(labelsize=9, colors=MUTED)
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


def draw_ribbon_panel(ax, poly, axis_idx, metric: str, scenarios: list, context: dict) -> None:
    draw_context(ax, poly, axis_idx, metric, context)
    start = to_display(metric, context["initial"][metric])
    for scenario in scenarios:
        if scenario["ranges"] is None:
            continue
        lows = [start] + [scenario["ranges"][metric, y][0] for y in YEARS]
        highs = [start] + [scenario["ranges"][metric, y][1] for y in YEARS]
        ax.fill_between(PANEL_YEARS, lows, highs, color=scenario["fill"], alpha=scenario["alpha"], linewidth=0, zorder=3)
        ax.plot(PANEL_YEARS, lows, color=scenario["color"], linewidth=1.0, zorder=4)
        ax.plot(PANEL_YEARS, highs, color=scenario["color"], linewidth=1.0, zorder=4)
        if SHOW_OUTER and scenario["outer"]:
            for k in (0, 1):
                ax.plot(PANEL_YEARS, [start] + [scenario["outer"][metric, y][k] for y in YEARS],
                        color=scenario["color"], linestyle=":", linewidth=1.0, zorder=4)
    if metric == "co2":
        ax.axhline(100, color=INK, linewidth=0.8, zorder=5)
        ax.text(REFERENCE_YEAR, 101.5, "budget", fontsize=8, color=MUTED, ha="left", va="bottom")
        ax.set_ylim(bottom=0)
    else:
        ax.set_ylim(0, 105)
    style_axes(ax, TITLE[metric], YLABEL[metric])


def draw_mandate_panel(ax, poly, axis_idx, metric: str, scenarios: list, context: dict) -> None:
    draw_context(ax, poly, axis_idx, metric, context)
    for year in YEARS:
        ax.axvline(year, color="#BBBBBB", linewidth=0.8, zorder=2)
    label_floor = -LABEL_MIN_GAP
    for scenario in scenarios:
        path, upper = scenario["path"], scenario["path_upper"]
        ax.plot(list(path), [100 * v for v in path.values()], color=scenario["color"], linewidth=2.2, zorder=8)
        label_value = 100 * path[YEARS[1]]
        if upper:
            ax.plot(list(upper), [100 * v for v in upper.values()], color=scenario["color"], linewidth=2.2, zorder=8)
            ax.fill_between(list(path), [100 * v for v in path.values()], [100 * v for v in upper.values()],
                            color=scenario["fill"], alpha=scenario["alpha"], linewidth=0, zorder=7)
            label_value = 100 * upper[YEARS[1]]
        reachable = scenario["ranges"] is not None
        ax.plot(YEARS, [100 * path[y] for y in YEARS], linestyle="none", marker="^", markersize=7,
                markerfacecolor=scenario["color"] if reachable else "white",
                markeredgecolor=scenario["color"], zorder=9)
        if upper:
            capped = [y for y in YEARS if upper[y] < 1.0]
            ax.plot(capped, [100 * upper[y] for y in capped], linestyle="none", marker="v", markersize=7,
                    markerfacecolor=scenario["color"] if reachable else "white",
                    markeredgecolor=scenario["color"], zorder=9)
        # Rate labels beside the 2038 markers, spread where the lines run close together.
        label_y = max(label_value, label_floor + LABEL_MIN_GAP)
        label_floor = label_y
        ax.annotate(scenario["label"], xy=(YEARS[1], label_y), xytext=(7, 0), textcoords="offset points",
                    ha="left", va="center", fontsize=8.5, color=INK, zorder=12, annotation_clip=False,
                    bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8, "pad": 1})
    start = 100 * scenarios[0]["path"][REFERENCE_YEAR]
    ax.plot(REFERENCE_YEAR, start, marker="o", markersize=7, color=INK, zorder=10, clip_on=False)
    ax.annotate("mandate\nstart", xy=(REFERENCE_YEAR, start), xytext=(6, 12), textcoords="offset points",
                fontsize=8, color=MUTED, ha="left", va="bottom")
    ax.set_ylim(0, 105)
    style_axes(ax, TITLE[metric], YLABEL[metric])


def extra_cost_bn(percent: float, c_star: float) -> float:
    """Cost above the optimum, % -> bn EUR (c_star is in megaEuro)."""
    return percent / 100 * c_star * 1e-3


def draw_cost_panel(ax, scenarios: list, slack_pct: float, c_star: float) -> None:
    for position, scenario in enumerate(scenarios):
        if scenario["ranges"] is None:
            ax.text(position, slack_pct / 2, "not\nreachable", ha="center", va="center", fontsize=8, color=MUTED)
            continue
        low, high = scenario["ranges"]["cost"]
        ax.bar(position, high - low, bottom=low, width=0.62, color=scenario["fill"], alpha=scenario["opacity"],
               linewidth=0, zorder=3)
        ax.text(position, low + 0.12, f"+{low:.2f}%\n+{extra_cost_bn(low, c_star):,.0f} bn", fontsize=8, color=INK,
                ha="center", va="bottom", zorder=5,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8, "pad": 1})
    ax.set_xticks(range(len(scenarios)), [s["label"] for s in scenarios], fontsize=9)
    ax.set_xlabel(f"{R_DIFF} (label: cheapest extra cost, bn EUR)", fontsize=9, color=MUTED)
    ax.set_xlim(-0.6, len(scenarios) - 0.4)
    ax.set_ylim(-slack_pct * 0.03, slack_pct * 1.1)
    ax.set_yticks([0, slack_pct], [f"$C^*$\n{c_star * 1e-3:,.0f} bn EUR",
                                   f"$C^*$ +{slack_pct:.0f}%\n+{extra_cost_bn(slack_pct, c_star):,.0f} bn EUR"])
    ax.axhline(0, color="#BBBBBB", linewidth=0.8, zorder=2)
    style_axes(ax, "Net present cost")
    ax.tick_params(axis="x", colors=INK)


def report(poly, axis_idx, mandated: str, scenarios: list) -> None:
    columns = [axis_idx[f"{AXIS_PREFIX[mandated]}_{y}"] for y in YEARS]
    for scenario in scenarios:
        path, upper = scenario["path"], scenario["path_upper"] or scenario["path"]
        print(f"  {mandated} r_diff {scenario['label']}: " + ", ".join(
            f"{y}: {100 * path[y]:.1f}-{100 * upper[y]:.1f}% (baseline {100 * poly.z_star_phys[j]:.1f}%)"
            for y, j in zip(YEARS, columns)))
        if scenario["ranges"] is None:
            print(f"    not reachable in the hull; outer approximation {'can' if scenario['outer'] else 'cannot either'}")
            continue
        low, high = scenario["ranges"]["cost"]
        print(f"    cost above optimum: {low:.2f}% to {high:.2f}% "
              f"({extra_cost_bn(low, poly.c_star):,.1f} to {extra_cost_bn(high, poly.c_star):,.1f} bn EUR)")
        for key, (lo, hi) in scenario["ranges"].items():
            if key != "cost" and key[0] != mandated:
                outer = scenario["outer"][key] if scenario["outer"] else (float("nan"),) * 2
                print(f"    {key[0]:4s} {key[1]}: inner [{lo:6.1f}, {hi:6.1f}]  outer [{outer[0]:6.1f}, {outer[1]:6.1f}]")


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
    return {"path": path, "path_upper": upper,
            "ranges": solve_all(poly, axis_idx, floors, ceilings, inner_bound, ("co2",)),
            "outer": solve_all(poly, axis_idx, floors, ceilings, outer_bound, ("co2",))}


def band_scenarios(poly, axis_idx, mandated: str, start: tuple[float, float]) -> list[dict]:
    """Bands, not nested, so each is a solid shade that darkens with the rates."""
    hue = MANDATE_COLOR[mandated]
    scenarios = []
    for (low, high), tint in zip(RATE_BANDS, BAND_TINTS):
        label = f"{low:.0%}".rstrip("%") + f"-{high:.0%}"
        scenarios.append(make_scenario(poly, axis_idx, mandated, start, low, high)
                         | {"label": label, "legend": f"{R_DIFF} {label}", "color": eth_tint(hue, tint),
                            "fill": eth_tint(hue, tint), "alpha": BAND_ALPHA, "opacity": BAND_ALPHA})
    return scenarios


def make_figure(poly, axis_idx, mandated: str, initial: dict, scenarios: list, title: str, range_note: str,
                figure_name: str) -> None:
    context = {"initial": initial, "full": solve_all(poly, axis_idx, [], [], inner_bound, (mandated, "co2"))}
    report(poly, axis_idx, mandated, scenarios)

    fig = plt.figure(figsize=(13.5, 5.4))
    grid = fig.add_gridspec(1, 3, width_ratios=[1.15, 1, 1.1], left=0.06, right=0.98, top=0.84, bottom=0.27,
                            wspace=0.3)
    draw_mandate_panel(fig.add_subplot(grid[0]), poly, axis_idx, mandated, scenarios, context)
    draw_ribbon_panel(fig.add_subplot(grid[1]), poly, axis_idx, "co2", scenarios, context)
    draw_cost_panel(fig.add_subplot(grid[2]), scenarios, 100 * poly.epsilon, poly.c_star)

    fig.suptitle(title, fontsize=13, fontweight="bold", color=INK, x=0.06, ha="left", y=0.965)
    handles = [
        Patch(facecolor=to_rgba(s["fill"], s["opacity"]), edgecolor=s["color"], label=s["legend"]) for s in scenarios
    ] + [
        Patch(facecolor=_GREY, alpha=0.13, label=f"Range without mandate (within {poly.epsilon:.0%} of optimal cost)"),
        Line2D([0], [0], color="black", linestyle="--", linewidth=1.0, label="Cost-optimal baseline"),
        Line2D([0], [0], marker="^", color="none", markerfacecolor=MUTED, markeredgecolor=MUTED, markersize=7,
               label="Imposed minimum"),
    ]
    if any(s["path_upper"] for s in scenarios):
        handles.append(Line2D([0], [0], marker="v", color="none", markerfacecolor=MUTED, markeredgecolor=MUTED,
                              markersize=7, label="Imposed maximum"))
    if any(s["ranges"] is None for s in scenarios):
        handles.append(Line2D([0], [0], marker="^", color="none", markerfacecolor="white", markeredgecolor=MUTED,
                              markersize=7, label=f"Not reachable within {poly.epsilon:.0%} of optimal cost"))
    fig.legend(handles=handles, loc="lower center", ncol=-(-len(handles) // 2), fontsize=8.5, frameon=False,
               bbox_to_anchor=(0.52, 0.1), columnspacing=1.4, handletextpad=0.6)
    others = " and ".join(OTHER_NAME[m] for m in ("heat", "ev", "ccs") if m != mandated)
    fig.text(0.06, 0.02, f"Not shown: {others} stay free between 0 and 100% under every band. Mandate path starts from "
             "existing capacity in the input data (heat, CCS) or the no-diffusion baseline's 2022 share (EV).\n"
             f"{range_note} Cumulative emissions plotted at 2038 run through 2041, likewise for the other years. Ribbon "
             "edges come from separate LPs.\nCost labels: cheapest blend of solved designs, an upper limit on the true "
             "extra cost.",
             fontsize=8, color=MUTED, ha="left", va="bottom", linespacing=1.3)
    savefig(fig, figure_name)


def main() -> None:
    poly = load_polytope(RUN_32_PATH)
    print(f"loaded {poly.X.shape[0]} points, converged={poly.converged}, final_gap={poly.final_gap:.3f}")
    axis_idx = {name: i for i, name in enumerate(poly.names)}
    initial = initial_values(poly)
    print("baseline 2022:", {metric: round(value, 4) for metric, value in initial.items()})
    starts = mandate_start(poly, initial)
    for mandated, figure_name in BAND_FIGURES.items():
        start = starts[mandated]
        print(f"bands on {mandated}: 2022 start {100 * start[0]:.2f}%, k_free {100 * start[1]:.2f}% per period")
        make_figure(poly, axis_idx, mandated, initial, band_scenarios(poly, axis_idx, mandated, start),
                    f"Diffusion rate ranges on {MANDATE_NAME[mandated]}: effect on emissions and cost",
                    "Share held between the two rates' trajectories.", figure_name)


if __name__ == "__main__":
    main()
