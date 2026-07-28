"""Generate print-ready figures for the MT_report SI Results section.

Covers the SI Results subsections in `MT_report_HG/Sections/03_SI.tex`
(`\\label{sec:si-results}`), across the 7
case-study scenarios in that section's Table~SIScenarios — 6
Crystal_Ball_HG_v7_0 euler runs (Full flexibility, No flexibility, DSM only,
TES only, Single temperature level, DSM pessimistic) plus the unmodified
"Crystal Ball (base)" reference case (dataset `Crystal_Ball`, plain — no
`Crystal_Ball_HG_v7_0` prefix, staged from data/Crystal_Ball, see
run_model.py):

  0a. fig0a_benchmark_comparison       — cost & emissions increase of each v7_0 scenario vs Crystal Ball base
  0b. fig0b_cost_composition           — CAPEX/OPEX/carrier/carbon-cost breakdown of that increase
  1a. fig1a_cost_delta                — discounted system cost delta vs Full flexibility
  1b. fig1b_industry_capacity         — industry heat-supply & production capacity, 2050
  2a. fig2a_tes_dsm_utilization       — TES vs DSM lifetime charge/discharge, log scale
  2b. fig2b_dsm_cycles_by_product     — DSM utilization (cycles/yr) by product: optimistic vs pessimistic
  3a. fig3a_temp_sensitivity_summary  — Full flex vs Single-temp: cost/emissions/capacity delta
  3b. fig3b_heat_pathway              — direct vs temp-conversion heat production, 2050

The planned "Emissions" subsection (fig3a/3b) is intentionally NOT built as a
standalone comparison across the 6 v7_0 scenarios: their horizon-total
emissions only span ~2.3% of each other (headline_metrics.csv), so an
absolute-scale trajectory or decomposition just shows six overlapping lines/
bars. fig0 carries this finding instead — the 6 v7_0 scenarios cluster
tightly relative to each other there, in visible contrast to the much larger
gap vs "Crystal Ball (base)" — without a dedicated, mostly-flat 3a/3b pair.

"Crystal Ball (base)" only feeds fig0a/0b. `load_base_scenario()` still skips
them gracefully (with a printed note) if Crystal_Ball_2025_10a_5a_interval_10ts/
isn't present under EULER_ROOT, but as of v7_0 it has converged and is loaded
normally. It's deliberately NOT a 7th entry in SCENARIOS below or
in any other figure: it has no industry heat/DSM/TES sector at all, so
capacity/utilization figures (1b, 2a, 2b, 3a's capacity term, 3b)
would show a misleading 0 for it rather than a meaningful
absence. Cost and emissions totals, by contrast, are well-defined for any
run regardless of sector structure, which is what makes it fig0a/0b material.

CAUTION on fig0a/0b's headline numbers (found while building fig0b): the
~15-16% cost / ~20-23% emissions increase in fig0a is NOT evenly spread
across the horizon or across cost components — see fig0b_cost_composition's
docstring for the full breakdown. In short: (1) ~half the cost delta is
concentrated in the single final year 2070, which behaves very differently
between the base run (a smooth declining tail) and every v7_0 scenario (a
sharp late-horizon spike) — a likely end-of-horizon/terminal-value artifact,
not a flexibility-extension cost; (2) of the remaining delta, the majority is
`cost_carbon_emissions_total`, not CAPEX/OPEX — and that variable itself is
~0 in every year except 2050 and 2070, i.e. it behaves like a carbon-BUDGET
shadow price at specific checkpoint years (see carbon_emissions_annual_limit.
csv, identical 0-limit-at-2050 in both datasets) rather than a smooth $/ton
price. This is very likely a real ZEN-garden framework/dataset behavior, not
a bug in this script — the % deltas exactly reproduce the model's own
net_present_cost/carbon_emissions_annual outputs — but it means the headline
fig0a percentages should not be read as "the extension costs 15% more to
build/operate" without this context.

Reuses the data-access helpers and color/plotting primitives shared with the
Streamlit dashboard (`figure_settings.py`, `figures_by_run.py`,
`figures_by_scenario.py`, all in this same scripts/ folder) rather than
re-deriving them.

Usage:
    python scripts/generate_si_figures.py
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Match MT_report_HG's font: 00_Preamble.sty loads no font package, so the
# report is plain LaTeX default (Computer Modern). "cmr10" ships inside
# matplotlib itself (no system LaTeX/font install needed, so this is portable
# to Euler too) and is Computer Modern Roman — the same face. Its bundled
# Type-1 file has no linked bold companion, so fontweight="bold" requests
# below silently render at regular weight rather than a mismatched fallback
# font; that's an acceptable trade-off for font consistency with the report.
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["cmr10"],
    "mathtext.fontset": "cm",
    "axes.formatter.use_mathtext": True,
    "axes.unicode_minus": False,
})

from figures_by_run import (
    INDUSTRY_DSM_TECHS,
    INDUSTRY_HEAT_CARRIERS_ENERGY,
    INDUSTRY_HEAT_TECHS_BOILERS_HP,
    INDUSTRY_HEAT_TECHS_PRODUCTION,
    INDUSTRY_HEAT_TECHS_TEMP_CONV,
    INDUSTRY_TES_TECHS,
    get_capacity,
    get_carrier_production,
    get_storage_flows,
)
from figures_by_scenario import (
    _annual_series,
    build_comparison_df,
    get_annual_cost,
    get_annual_total_cost,
    plot_stacked_bars,
)
from figure_settings import EULER_ROOT, Run, SCENARIO_PALETTE, get_available_years, load_results

FIGURES_DIR = REPO_ROOT / "data" / "outputs" / "figures" / "SI_results"
YEAR = 2050  # single-year snapshot used throughout; horizon totals used where noted

# Thesis-consistent scenario order/labels (Table~SIScenarios), distinct from
# the dashboard's shorter "Baseline" label for the same run. Order matches
# Table SIScenarios (excluding "Crystal Ball (base)", handled separately via
# BASE_SCENARIO below) and figure_settings.EULER_SCENARIO_ORDER, so the same
# scenario gets the same SCENARIO_PALETTE slot 0-5 everywhere; slot 6 (grey)
# is reserved for "Crystal Ball (base)" — see the module docstring for why it
# isn't a 7th entry here.
SCENARIOS = [
    ("Crystal_Ball_ind_heat_v7_1_no_flexibility_2025_10a_5a_interval_10ts", "No flexibility"),
    ("Crystal_Ball_ind_heat_v7_1_2025_10a_5a_interval_10ts", "Full flexibility"),
    ("Crystal_Ball_ind_heat_v7_1_DSM_pessimistic_2025_10a_5a_interval_10ts", "DSM pessimistic"),
    ("Crystal_Ball_ind_heat_v7_1_DSM_only_2025_10a_5a_interval_10ts", "DSM only"),
    ("Crystal_Ball_ind_heat_v7_1_TES_only_2025_10a_5a_interval_10ts", "TES only"),
    ("Crystal_Ball_ind_heat_v7_1_single_temp_2025_10a_5a_interval_10ts", "Single temperature level"),
]

# fig0 only. Uses SCENARIO_PALETTE slot 6 (grey) — see the comment there.
BASE_SCENARIO = ("Crystal_Ball_2025_10a_5a_interval_10ts", "Crystal Ball (base)")


def load_scenarios() -> list[Run]:
    runs = []
    for i, (folder, label) in enumerate(SCENARIOS):
        results = load_results(EULER_ROOT, folder)
        runs.append(Run(name=folder, label=label, mode="euler", results=results,
                         color=SCENARIO_PALETTE[i % len(SCENARIO_PALETTE)]))
    return runs


def load_base_scenario() -> Run | None:
    """Returns None (rather than raising) if the run hasn't landed yet."""
    folder, label = BASE_SCENARIO
    try:
        results = load_results(EULER_ROOT, folder)
    except FileNotFoundError:
        return None
    return Run(name=folder, label=label, mode="euler", results=results,
               color=SCENARIO_PALETTE[6])


def by_label(runs: list[Run], label: str) -> Run:
    return next(r for r in runs if r.label == label)


def savefig(fig: plt.Figure, name: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{name}.svg"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {path.relative_to(REPO_ROOT)}")


# ── Shared metrics (feed figures 1a, 3a, 4) ────────────────────────────────

def industry_heat_capacity(r, year: int) -> float:
    """Total industry heat-supply capacity (boilers + HPs only), GW.

    Deliberately excludes heat_industry_temp_conversion_*: that pathway is a
    near-zero-cost, effectively unconstrained lossless conversion, so its
    "capacity" is a modeling artifact (~37,700 GW, three orders of magnitude
    above the real boiler/HP capacity) rather than a meaningful investment —
    it is examined separately in fig3b's direct-vs-conversion pathway split.
    """
    cap = get_capacity(r, INDUSTRY_HEAT_TECHS_BOILERS_HP, "power")
    return float(cap[year].sum()) if year in cap.columns else 0.0


def compute_headline_metrics(runs: list[Run]) -> pd.DataFrame:
    """Horizon-total discounted cost, horizon-total emissions, and 2050 industry
    heat-supply capacity, one row per scenario."""
    rows = {}
    for r in runs:
        years = get_available_years(r.results)
        npc_total = float(get_annual_total_cost(r.results, years, discount=True).sum())
        em_total = float(_annual_series(r.results, "carbon_emissions_annual", years).sum())
        cap = industry_heat_capacity(r.results, YEAR)
        rows[r.label] = {
            "npc_total_meur": npc_total,
            "emissions_total_mton": em_total,
            "industry_heat_capacity_gw": cap,
        }
    return pd.DataFrame(rows).T


# ── 0a: v7_0 scenarios vs unmodified Crystal Ball base ──────────────────────

def fig0a_benchmark_comparison(metrics_with_base: pd.DataFrame) -> None:
    """Cost & emissions of each v7_0 scenario relative to the unmodified
    Crystal Ball base (Table~SIScenarios) — makes the case that resolving
    industry heat and flexibility is worth the added cost/complexity, by
    showing what it actually changes relative to Mannhardt's original model.
    """
    base_label = BASE_SCENARIO[1]
    baseline = metrics_with_base.loc[base_label]
    others = metrics_with_base.drop(base_label)
    cost_pct = (others["npc_total_meur"] - baseline["npc_total_meur"]) / baseline["npc_total_meur"] * 100
    em_pct = (others["emissions_total_mton"] - baseline["emissions_total_mton"]) / baseline["emissions_total_mton"] * 100
    colors = [SCENARIO_PALETTE[[l for _, l in SCENARIOS].index(lbl)] for lbl in others.index]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for ax, values, ylabel, title in [
        (axes[0], cost_pct, r"$\Delta$ discounted system cost [%]", "System Cost"),
        (axes[1], em_pct, r"$\Delta$ system emissions, horizon total [%]", "System Emissions"),
    ]:
        bars = ax.bar(others.index, values.values, color=colors, edgecolor="white")
        for bar, v in zip(bars, values.values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                    f"{v:+.1f}%", ha="center", va="bottom" if v >= 0 else "top",
                    fontsize=9, fontweight="bold")
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_title(title, fontsize=11, fontweight="bold")
        plt.setp(ax.get_xticklabels(), rotation=25, ha="right", fontsize=8)
        ax.grid(axis="y", alpha=0.3)
    fig.suptitle("Industry Heat & Flexibility Extension vs Unmodified Crystal Ball Base\n"
                 f"(vs {base_label}, discounted full horizon)", fontsize=12, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    savefig(fig, "fig0a_benchmark_comparison")


# ── 0b: Cost-increase composition (CAPEX/OPEX/carrier/carbon) ───────────────

# (variable, display label). Matches the Streamlit dashboard's own CAPEX/OPEX
# metrics (figures_by_scenario.get_summary_metrics) plus the two remaining
# components (carrier, carbon) needed to fully reconstruct net_present_cost —
# verified to sum exactly to it (see the caution note in the module docstring).
COST_COMPONENTS = [
    ("cost_capex_yearly_total", "CAPEX"),
    ("cost_opex_yearly_total", "OPEX"),
    ("cost_carrier", "Carrier (fuel/import)"),
    ("cost_carbon_emissions_total", "Carbon emissions cost"),
]
COST_COMPONENT_COLORS = ["#215CAF", "#007894", "#8E6713", "#B7352D"]  # ETH blue/petrol/bronze/red


def compute_cost_components(runs: list[Run]) -> pd.DataFrame:
    """Discounted, horizon-total cost by component, one row per scenario."""
    rows = {}
    for r in runs:
        years = get_available_years(r.results)
        rows[r.label] = {
            label: float(get_annual_cost(r.results, years, var, discount=True).sum())
            for var, label in COST_COMPONENTS
        }
    return pd.DataFrame(rows).T


# Carbon emissions cost is computed (see compute_cost_components) but
# deliberately excluded from this figure's bars/legend: at ~60% of the total
# delta and behaving like a 2050/2070 budget-checkpoint shadow cost rather
# than a smooth $/ton price (see docstring below), it dwarfs and obscures the
# CAPEX/OPEX/carrier story this figure exists to show.
PLOTTED_COST_COMPONENTS = COST_COMPONENTS[:3]
PLOTTED_COST_COMPONENT_COLORS = COST_COMPONENT_COLORS[:3]


def fig0b_cost_composition(components_with_base: pd.DataFrame) -> None:
    """Decomposes fig0a's cost-increase-vs-base bars into CAPEX/OPEX/carrier
    (carbon emissions cost excluded — see PLOTTED_COST_COMPONENTS above), to
    show what's actually driving the non-carbon part of the increase.

    Built after a real surprise: the total increase is NOT primarily new
    CAPEX/OPEX from the added industry-heat/flexibility technologies (each
    contributes only ~600-800k MEUR here, a few % of baseline total cost) —
    it's overwhelmingly `cost_carbon_emissions_total` (~60% of the total
    delta), which is why that component is excluded from this plot rather
    than swamping it. That variable itself is ~0 in every year except 2050
    and 2070: at 2050 both the base and every v7_0 scenario pay a matching
    ~6712 EUR/ton shadow price for exceeding the shared
    carbon_emissions_annual_limit.csv (limit=0 in 2050, identical file in
    both datasets); at 2070 there is no explicit limit in that file at all,
    yet every v7_0 scenario pays a large cost there (base pays ~0) despite
    NEGATIVE (net-removal) emissions that year — consistent with a
    cumulative/horizon-level carbon-budget cost being attributed entirely to
    the final period, not a real 2070 emissions price. Treat fig0a's
    percentages with that in mind.
    """
    base_label = BASE_SCENARIO[1]
    baseline = components_with_base.loc[base_label]
    others = components_with_base.drop(base_label)
    delta = others.subtract(baseline, axis=1)
    baseline_total_cost = baseline.sum()  # all 4 components, i.e. full net_present_cost

    fig, ax = plt.subplots(figsize=(11, 6.5))
    x = np.arange(len(delta))
    bottom_pos = np.zeros(len(delta))
    bottom_neg = np.zeros(len(delta))
    for (_, comp_label), color in zip(PLOTTED_COST_COMPONENTS, PLOTTED_COST_COMPONENT_COLORS):
        vals = delta[comp_label].to_numpy()
        bottoms = np.where(vals >= 0, bottom_pos, bottom_neg)
        ax.bar(x, vals, bottom=bottoms, label=comp_label, color=color, edgecolor="white")
        bottom_pos += np.clip(vals, 0, None)
        bottom_neg += np.clip(vals, None, 0)
    totals = delta[[label for _, label in PLOTTED_COST_COMPONENTS]].sum(axis=1)
    pct_of_baseline_total = totals / baseline_total_cost * 100
    for xi, t, pct in zip(x, totals, pct_of_baseline_total):
        ax.text(xi, t, f"{pct:+.2f}%", ha="center", va="bottom" if t >= 0 else "top",
                fontsize=9, fontweight="bold")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(delta.index, rotation=25, ha="right", fontsize=9)
    ax.set_ylabel(r"$\Delta$ discounted system cost vs Crystal Ball base [MEUR]")
    ax.set_title("Non-Carbon Cost Increase vs Crystal Ball Base", fontsize=12, fontweight="bold")
    ax.set_ylim(top=ax.get_ylim()[1] * 1.15)  # headroom so the legend clears the bars
    ax.legend(fontsize=9, frameon=True, facecolor="white", framealpha=0.9, loc="upper center", ncol=3)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    savefig(fig, "fig0b_cost_composition")


# ── 1a: Cost delta vs Full flexibility ─────────────────────────────────────

def fig1a_cost_delta(metrics: pd.DataFrame) -> None:
    baseline = metrics.loc["Full flexibility", "npc_total_meur"]
    others = metrics.drop("Full flexibility")
    delta = others["npc_total_meur"] - baseline
    pct = delta / baseline * 100

    fig, ax = plt.subplots(figsize=(7, 5))
    colors = [SCENARIO_PALETTE[list(metrics.index).index(lbl) % len(SCENARIO_PALETTE)]
              for lbl in others.index]
    bars = ax.bar(others.index, delta.values, color=colors, edgecolor="white")
    for bar, p in zip(bars, pct.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f"+{p:.2f}%", ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel(r"$\Delta$ discounted system cost vs Full flexibility [MEUR]")
    ax.set_title("System Cost Delta vs Full Flexibility\n(discounted, full horizon)",
                  fontsize=12, fontweight="bold")
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    fig.tight_layout()
    savefig(fig, "fig1a_cost_delta")


# ── 1b: Industry capacity, 2050 ─────────────────────────────────────────────

def _eth_tint(hex_color: str, pct: float) -> str:
    """Blend hex_color toward white by pct (0=original, 1=white) — mirrors
    ETH's documented 20/40/60/80% corporate-design tint system."""
    from matplotlib.colors import to_rgb
    r, g, b = to_rgb(hex_color)
    r, g, b = (c + (1 - c) * pct for c in (r, g, b))
    return f"#{int(round(r * 255)):02x}{int(round(g * 255)):02x}{int(round(b * 255)):02x}"


# Print-figure-specific palette (does NOT touch the shared, dashboard-wide
# COLOR_MAP in figure_settings.py) — see plot_stacked_bars(color_map=...).
# Heat supply: heat source (water vs. waste heat) sets the hue — blue vs.
# turquoise — since that is the more physically meaningful distinction (waste
# heat is a byproduct/free input, water is an ambient draw); temperature band
# sets the shade within that hue, lighter for lower bands; ALL heat pumps
# get a hatch, so "textured = heat pump" reads at a glance regardless of hue.
# Boilers stay solid (no hatch); electrode boiler is green, the other two
# boilers keep their existing ETH-red-family shades.
_ETH_BLUE, _ETH_TURQUOISE, _ETH_GREEN, _ETH_RED = "#215CAF", "#007894", "#627313", "#B7352D"
_HP_HATCH = "/"  # subtle, sparse diagonal — repeat the character (e.g. "//") for denser hatching
HEAT_SUPPLY_COLOR_MAP = {
    # water source: ETH blue, darker at higher temperature
    "heat_pump_industry_150_200_water": _ETH_BLUE,
    "heat_pump_industry_100_150_water": _eth_tint(_ETH_BLUE, 0.3),
    "heat_pump_industry_0_100_water": _eth_tint(_ETH_BLUE, 0.55),
    # waste heat source: ETH turquoise/petrol, darker at higher temperature
    "heat_pump_industry_150_200_waste_heat": _ETH_TURQUOISE,
    "heat_pump_industry_100_150_waste_heat": _eth_tint(_ETH_TURQUOISE, 0.3),
    "heat_pump_industry_0_100_waste_heat": _eth_tint(_ETH_TURQUOISE, 0.55),
    # boilers: electrode = green, others keep their ETH-red-family shades —
    # oil sits at a tint halfway between natural_gas (0%) and biomass (55%),
    # so its color reads as physically "between" the two.
    "electrode_boiler_industry": _ETH_GREEN,
    "natural_gas_boiler_industry": _ETH_RED,
    "oil_boiler_industry": _eth_tint(_ETH_RED, 0.28),
    "biomass_boiler_industry": _eth_tint(_ETH_RED, 0.55),
}
HEAT_SUPPLY_HATCH_MAP = {tech: _HP_HATCH for tech in [
    "heat_pump_industry_150_200_water", "heat_pump_industry_100_150_water", "heat_pump_industry_0_100_water",
    "heat_pump_industry_150_200_waste_heat", "heat_pump_industry_100_150_waste_heat", "heat_pump_industry_0_100_waste_heat",
]}
# Explicit stack order (bottom → top): all boilers first (darkest→lightest
# red family, electrode-green anchoring the bottom), then heat pumps ordered
# low→high temperature band, water source before waste-heat source within
# each band. Any tech not listed here (future additions) is appended at the
# end in whatever order build_comparison_df produced, so nothing is dropped.
HEAT_SUPPLY_STACK_ORDER = [
    "electrode_boiler_industry",
    "natural_gas_boiler_industry",
    "oil_boiler_industry",
    "biomass_boiler_industry",
    "heat_pump_industry_0_100_water",
    "heat_pump_industry_0_100_waste_heat",
    "heat_pump_industry_100_150_water",
    "heat_pump_industry_100_150_waste_heat",
    "heat_pump_industry_150_200_water",
    "heat_pump_industry_150_200_waste_heat",
]
# Production techs: solid ETH colors only, no hatching (hatch_map={} below).
PRODUCTION_COLOR_MAP = {
    "glass_production": "#215CAF",    # ETH blue
    "ceramic_production": "#007894",  # ETH petrol
    "paper_production": "#8E6713",    # ETH bronze
    "food_production": "#A7117A",     # ETH purple
}


def fig1b_industry_capacity(runs: list[Run]) -> None:
    # temp-conversion capacity excluded here — see industry_heat_capacity() docstring;
    # its own direct-vs-conversion pathway is the subject of fig3b instead.
    heat_series = [(r.label, get_capacity(r.results, INDUSTRY_HEAT_TECHS_BOILERS_HP, "power")
                    .get(YEAR, pd.Series(dtype=float))) for r in runs]
    prod_series = [(r.label, get_capacity(r.results, INDUSTRY_HEAT_TECHS_PRODUCTION, "power")
                    .get(YEAR, pd.Series(dtype=float))) for r in runs]

    heat_df = build_comparison_df(heat_series)
    # See HEAT_SUPPLY_STACK_ORDER: all boilers drawn first -> bottom of the
    # stack, below all heat pumps, which are then ordered low->high temperature.
    heat_df = heat_df.reindex(
        [t for t in HEAT_SUPPLY_STACK_ORDER if t in heat_df.index]
        + [t for t in heat_df.index if t not in HEAT_SUPPLY_STACK_ORDER])

    fig, axes = plt.subplots(1, 2, figsize=(15, 7))
    fig.suptitle(f"Industry Technology Capacity - Year {YEAR}", fontsize=13, fontweight="bold")
    with plt.rc_context({"hatch.linewidth": 0.5}):  # subtler hatch lines than the 1.0 default
        plot_stacked_bars(heat_df, "Heat Supply (boilers & heat pumps)",
                          "GW", axes[0], show_segment_labels=True,
                          color_map=HEAT_SUPPLY_COLOR_MAP, hatch_map=HEAT_SUPPLY_HATCH_MAP)
    plot_stacked_bars(build_comparison_df(prod_series), "Production Technologies",
                      "ton/h", axes[1], show_segment_labels=True,
                      color_map=PRODUCTION_COLOR_MAP, hatch_map={})
    for ax in axes:
        plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    savefig(fig, "fig1b_industry_capacity")


# ── 2a: TES vs DSM lifetime utilization, log scale ─────────────────────────

def _horizon_total(r, techs: list[str], flow_type: str) -> float:
    df = get_storage_flows(r, techs, flow_type)
    return float(df.to_numpy().sum()) if not df.empty else 0.0


def fig2a_tes_dsm_utilization(runs: list[Run]) -> None:
    scenarios = ["Full flexibility", "DSM only", "TES only"]
    categories = ["TES charge\n[GWh]", "TES discharge\n[GWh]",
                  "DSM charge\n[GWh+kt]", "DSM discharge\n[GWh+kt]"]
    data = {}
    for label in scenarios:
        r = by_label(runs, label).results
        data[label] = [
            _horizon_total(r, INDUSTRY_TES_TECHS, "flow_storage_charge"),
            _horizon_total(r, INDUSTRY_TES_TECHS, "flow_storage_discharge"),
            _horizon_total(r, INDUSTRY_DSM_TECHS, "flow_storage_charge"),
            _horizon_total(r, INDUSTRY_DSM_TECHS, "flow_storage_discharge"),
        ]
    df = pd.DataFrame(data, index=categories)

    fig, ax = plt.subplots(figsize=(9, 6))
    n = len(scenarios)
    width = 0.8 / n
    x = np.arange(len(categories))
    zero_bars = []  # (x position, color) for exact zeros — drawn as "0" labels, not floor bars
    for i, label in enumerate(scenarios):
        offsets = x + (i - (n - 1) / 2) * width
        color = SCENARIO_PALETTE[[s for s, _ in SCENARIOS].index(
            next(f for f, l in SCENARIOS if l == label))]
        values = df[label].to_numpy()
        nonzero = values > 0
        # log scale can't render a zero-height bar at all, so exact zeros are
        # skipped here (not floored to a fake small value) and marked below
        # instead, once the axis limits from the real bars are known.
        ax.bar(offsets[nonzero], values[nonzero], width, label=label, color=color, edgecolor="white")
        zero_bars.extend((xi, color) for xi in offsets[~nonzero])
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=9)
    ax.set_ylabel("Lifetime throughput (log scale)")
    ax.set_title("TES vs DSM - Lifetime Utilization Scale", fontsize=11, fontweight="bold")
    ymin, _ = ax.get_ylim()
    for xi, color in zero_bars:
        ax.text(xi, ymin, "0", ha="center", va="bottom", fontsize=9, fontweight="bold", color=color)
    ax.legend(fontsize=9, frameon=False)
    ax.grid(axis="y", alpha=0.3, which="both")
    fig.tight_layout()
    savefig(fig, "fig2a_tes_dsm_utilization")


# ── 2b: DSM cycles by product, 2050 ─────────────────────────────────────────

def dsm_cycles(r, year: int) -> pd.Series:
    discharge = get_storage_flows(r, INDUSTRY_DSM_TECHS, "flow_storage_discharge")
    capacity = get_capacity(r, INDUSTRY_DSM_TECHS, "energy")
    cycles = {}
    for tech in INDUSTRY_DSM_TECHS:
        cap = capacity.loc[tech, year] if tech in capacity.index and year in capacity.columns else 0.0
        dis = discharge.loc[tech, year] if tech in discharge.index and year in discharge.columns else 0.0
        cycles[tech] = dis / cap if cap > 1e-9 else 0.0
    return pd.Series(cycles)


def fig2b_dsm_cycles_by_product(runs: list[Run]) -> None:
    # "Full flexibility" (opt.) vs "DSM pessimistic" (pess.) isolates the
    # demand-shiftability-assumption effect on utilization directly, since
    # both scenarios otherwise share the same industry heat / TES setup
    # (Table SIScenarios, Table SIDSMCategorization) — unlike the previous
    # comparison against "Single temperature level", which also changes the
    # temperature-band resolution and so conflated two different effects.
    scenarios = ["Full flexibility", "DSM pessimistic"]
    legend_labels = {"Full flexibility": "Optimistic (Full flexibility)",
                      "DSM pessimistic": "Pessimistic (DSM pessimistic)"}
    df = pd.DataFrame({label: dsm_cycles(by_label(runs, label).results, YEAR) for label in scenarios})
    df.index = [t.replace("_DSM", "").replace("_", " ") for t in df.index]
    df = df.sort_values(scenarios[0], ascending=False)

    fig, ax = plt.subplots(figsize=(10, 6))
    n = len(scenarios)
    width = 0.8 / n
    x = np.arange(len(df))
    for i, label in enumerate(scenarios):
        offsets = x + (i - (n - 1) / 2) * width
        color = SCENARIO_PALETTE[[l for _, l in SCENARIOS].index(label)]
        ax.bar(offsets, df[label].values, width, label=legend_labels[label], color=color, edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(df.index, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Discharge cycles / year")
    ax.set_title(f"DSM Utilization by Product, {YEAR}\n"
                 "Demand-Shiftability Assumption (DSM Categories)", fontsize=12, fontweight="bold")
    ax.legend(fontsize=9, frameon=False)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    savefig(fig, "fig2b_dsm_cycles_by_product")


# ── 3a: Temperature-resolution sensitivity summary ──────────────────────────

def fig3a_temp_sensitivity_summary(metrics: pd.DataFrame) -> None:
    full = metrics.loc["Full flexibility"]
    single = metrics.loc["Single temperature level"]
    pct = (single - full) / full * 100

    labels = ["Discounted\nsystem cost", "System\nemissions", f"Industry heat\ncapacity ({YEAR})"]
    values = [pct["npc_total_meur"], pct["emissions_total_mton"], pct["industry_heat_capacity_gw"]]

    color = SCENARIO_PALETTE[[l for _, l in SCENARIOS].index("Single temperature level")]
    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(labels, values, color=color, edgecolor="white")
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f"{v:+.2f}%", ha="center", va="bottom" if v >= 0 else "top",
                fontsize=10, fontweight="bold")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel(r"$\Delta$ Single temperature level vs Full flexibility [%]")
    ax.set_title("Sensitivity to Temperature-Band Resolution", fontsize=12, fontweight="bold")
    fig.tight_layout()
    savefig(fig, "fig3a_temp_sensitivity_summary")


# ── 3b: Direct vs temperature-conversion heat pathway, 2050 ─────────────────

def heat_pathway_split_by_band(r, year: int) -> pd.DataFrame:
    """Net (non-double-counted) end-use heat demand met per temperature band,
    split into direct (boiler/HP) vs. conversion-cascade-sourced.

    `get_carrier_production` per carrier is GROSS output onto that carrier,
    which for a mid/high band includes energy that gets immediately consumed
    again as input to the next-lower conversion technology (lossless, 1:1).
    Naively summing gross production across bands therefore double- (or
    triple-) counts any energy that cascades down more than one step — see
    fig3b's module-level note for the numbers this produced. This function
    nets that out: for each band, the amount forwarded to the band below
    (`downstream_draw`, = the conversion-sourced gross production of that
    lower band) is subtracted before splitting into direct/conversion, so
    summing the result across bands gives actual net end-use demand met, not
    an inflated pass-through total. INDUSTRY_HEAT_CARRIERS_ENERGY must be
    ordered low-to-high for the downstream-draw lookup below to be correct.
    """
    bands = INDUSTRY_HEAT_CARRIERS_ENERGY
    gross = {}
    for carrier in bands:
        prod = get_carrier_production(r, carrier)
        if prod.empty or year not in prod.columns:
            gross[carrier] = (0.0, 0.0)
            continue
        direct = prod.loc[prod.index.isin(INDUSTRY_HEAT_TECHS_BOILERS_HP), year].sum()
        conversion = prod.loc[prod.index.isin(INDUSTRY_HEAT_TECHS_TEMP_CONV), year].sum()
        gross[carrier] = (direct, conversion)

    rows = {}
    for i, carrier in enumerate(bands):
        direct, conversion = gross[carrier]
        total = direct + conversion
        downstream_draw = gross[bands[i - 1]][1] if i > 0 else 0.0
        frac_forwarded = downstream_draw / total if total > 1e-9 else 0.0
        rows[carrier] = {
            "Direct (boiler/HP)": direct * (1 - frac_forwarded),
            "Via conversion cascade": conversion * (1 - frac_forwarded),
        }
    return pd.DataFrame(rows).T  # index: carrier (low to high); columns: Direct, Via conversion cascade


BAND_LABELS = {"heat_industry_0_100": "0-100°C", "heat_industry_100_150": "100-150°C",
               "heat_industry_150_200": "150-200°C"}


def fig3b_heat_pathway(runs: list[Run]) -> None:
    scenarios = ["Full flexibility", "Single temperature level"]
    bands = INDUSTRY_HEAT_CARRIERS_ENERGY
    dfs = {label: heat_pathway_split_by_band(by_label(runs, label).results, YEAR) for label in scenarios}
    colors = {"Direct (boiler/HP)": "#215CAF", "Via conversion cascade": "#8E6713"}  # ETH blue / bronze
    hatches = {"Full flexibility": "", "Single temperature level": "//"}

    fig, ax = plt.subplots(figsize=(9, 3.8))
    n = len(scenarios)
    bar_h = 0.8 / n
    y = np.arange(len(bands))
    for i, label in enumerate(scenarios):
        offsets = y + (i - (n - 1) / 2) * bar_h
        df = dfs[label]
        left = np.zeros(len(bands))
        for col in ["Direct (boiler/HP)", "Via conversion cascade"]:
            vals = df.loc[bands, col].to_numpy()
            ax.barh(offsets, vals, left=left, height=bar_h, color=colors[col], edgecolor="white",
                     hatch=hatches[label], label=col if i == 0 else None)
            left += vals
        for yi, t in zip(offsets, left):
            ax.text(t, yi, f" {label} ({t:,.0f})", va="center", fontsize=7.5)
    ax.set_yticks(y)
    ax.set_yticklabels([BAND_LABELS[b] for b in bands], fontsize=9)
    ax.set_xlim(right=ax.get_xlim()[1] * 1.55)  # headroom for the end-of-bar labels
    ax.set_xlabel("Net end-use heat demand met [GWh]")
    ax.set_title(f"Heat Demand Met by Temperature Band, {YEAR}\n"
                 "(equal per-band totals confirm identical end-use demand across scenarios)",
                 fontsize=11, fontweight="bold")
    ax.legend(fontsize=9, frameon=False, loc="lower right")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    savefig(fig, "fig3b_heat_pathway")


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"Loading {len(SCENARIOS)} euler scenarios...")
    runs = load_scenarios()
    print("Computing headline metrics (cost, emissions, capacity)...")
    metrics = compute_headline_metrics(runs)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(FIGURES_DIR / "headline_metrics.csv")
    print(f"  wrote {(FIGURES_DIR / 'headline_metrics.csv').relative_to(REPO_ROOT)}")

    print(f"Loading base scenario ({BASE_SCENARIO[1]})...")
    base_run = load_base_scenario()

    print("Generating figures...")
    if base_run is not None:
        metrics_with_base = compute_headline_metrics([base_run] + runs)
        fig0a_benchmark_comparison(metrics_with_base)
        components_with_base = compute_cost_components([base_run] + runs)
        fig0b_cost_composition(components_with_base)
    else:
        print(f"  skipping fig0a/fig0b: {BASE_SCENARIO[0]} not yet under {EULER_ROOT}")
    fig1a_cost_delta(metrics)
    fig1b_industry_capacity(runs)
    fig2a_tes_dsm_utilization(runs)
    fig2b_dsm_cycles_by_product(runs)
    fig3a_temp_sensitivity_summary(metrics)
    fig3b_heat_pathway(runs)
    print(f"Done. Figures in {FIGURES_DIR.relative_to(REPO_ROOT)}/")


if __name__ == "__main__":
    main()
