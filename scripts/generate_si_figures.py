"""Generate print-ready figures for the MT_report SI Results section.

Covers the SI Results subsections in `MT_report_HG/Sections/03_SI.tex`
(`\\label{sec:si-results}`), across the 7
case-study scenarios in that section's Table~SIScenarios — 6
Crystal_Ball_HG_v7_0 euler runs (Full flexibility, No flexibility, DSM only,
TES only, Single temperature level, DSM pessimistic) plus the unmodified
"Crystal Ball (base)" reference case (dataset `Crystal_Ball`, plain — no
`Crystal_Ball_HG_v7_0` prefix, staged from data/Crystal_Ball, see
run_model.py):

  0a. fig0a_cost_composition            — CAPEX/OPEX/carrier/carbon-cost breakdown of each v7_0
                                          scenario's cost increase vs Crystal Ball base
  0b. fig0b_emissions_source_comparison — Full flex vs Crystal Ball base, year 2025: where the
                                          emissions increase comes from vs. only a modest cost delta
  1a. fig1a_cost_delta                — discounted system cost delta vs Full flexibility
  1b. fig1b_industry_capacity         — industry heat-supply & production capacity, 2050
  2.  fig2_dsm_cycles_by_product      — DSM utilization (cycles/yr) by product: optimistic vs pessimistic
  3b. fig3b_heat_pathway              — direct vs temp-conversion heat production, 2050
  4.  fig4_heat_demand_by_sector      — low-temp input heat demand by sector/band, +high-temp fuel by carrier (2023)

fig4 is the odd one out: unlike every other figure here, it does NOT come from
a solved model run. It plots the exogenous low-temperature heat-demand
ASSUMPTION that ZEN-creator computes for glass/ceramic/paper/food
(ProcessParametrizationDataset._heat_cfs × each sector's own demand volume,
FEC_YEAR=2023) — i.e. what goes INTO the model as `demand` on
heat_industry_0_100/100_150/150_200, not what the solved model does with it
(that's fig3b's territory) — plus, stacked on top in grey and split by
carrier, each sector's high-temperature (>200°C) fuel demand (direct
combustion, no heat_industry_* carrier involved — a different supply pathway,
shown only for scale against the colored low-temperature bands). Values are
aggregated across all MODEL_NODES (EU27+CH+NO+UK), not per-country. Since
ZEN-creator needs openpyxl/xlrd (zen-creator-env) and this script needs
matplotlib (zen-garden-env) — the two conda envs are disjoint — the
extraction is a separate script (scripts/extract_heat_demand_by_sector.py,
run under zen-creator-env) that writes heat_demand_by_sector_input.json into
this same FIGURES_DIR; fig4_heat_demand_by_sector() here just reads and
plots it, and is skipped gracefully (like fig0a/fig0b vs. Crystal Ball base)
if that JSON hasn't been generated yet. See extract_heat_demand_by_sector.
py's docstring for the full provenance/validation chain (Rehfeldt2017.csv ->
compute_sector_params(), cross-checked against a materialized dataset's own
demand.csv and attributes.json).

fig2 used to be a pair (fig2a_tes_dsm_utilization, fig2b_dsm_cycles_by_product).
fig2a summed flow_storage_charge/discharge across all INDUSTRY_DSM_TECHS, but
those techs are NOT unit-homogeneous: ammonia_DSM/methanol_DSM are
energy-carrier storage (GWh, confirmed via Results.get_unit()), while the
other 8 (ceramic/clinker/food/glass/olefin/paper/primary_steel/
secondary_steel) are mass-carrier storage (kt-of-product) — its
"[GWh+kt]" axis label was already an admission of an invalid mixed-unit sum.
Removed outright (per user decision) rather than fixed, since its message
(TES negligible vs. DSM once DSM is available) is carried by prose alone in
03_SI.tex. fig2b was renamed to fig2 (dropping the now-meaningless "b"
suffix) and gained hatching to flag which of its bars are the 2
energy-carrier products (ammonia, methanol) vs. the 8 mass-carrier ones —
its "cycles/year" metric was already unit-safe (each product's discharge is
divided by its OWN capacity in the same native unit), but had no visual cue
for readers that the underlying carriers differ in kind.

The planned "Emissions" subsection (fig3b) is intentionally NOT built as a
standalone comparison across the 6 v7_0 scenarios: their horizon-total
emissions only span ~2.3% of each other (headline_metrics.csv), so an
absolute-scale trajectory or decomposition just shows six overlapping lines/
bars. fig0b covers a single-scenario ("Full flexibility") emissions
comparison against Crystal Ball base instead — see
fig0b_emissions_source_comparison's docstring — without a dedicated,
mostly-flat fig3b-only pairing.

fig3a_temp_sensitivity_summary (cost/emissions/capacity delta bars, Single
temperature level vs Full flexibility) was deleted per user request: its cost
and capacity bars only repeated what fig0a/fig1b already show, and the one
new number it carried (emissions delta, ~+0.9%) is reported as prose in
03_SI.tex instead. fig3b (heat pathway) is unchanged and keeps its original
name/label — it was NOT renamed down to "fig3" the way fig2b was, since the
user only asked to drop fig3a this time, not collapse the pair.

"Crystal Ball (base)" only feeds fig0a/0b. `load_base_scenario()` still skips
them gracefully (with a printed note) if Crystal_Ball_2025_10a_5a_interval_10ts/
isn't present under EULER_ROOT, but as of v7_0 it has converged and is loaded
normally. It's deliberately NOT a 7th entry in SCENARIOS below or
in any other figure: it has no industry heat/DSM/TES sector at all, so
capacity/utilization figures (1b, 2, 3b)
would show a misleading 0 for it rather than a meaningful
absence. Cost and emissions totals, by contrast, are well-defined for any
run regardless of sector structure, which is what makes it fig0a/0b material.

CAUTION on fig0a's headline numbers (found while building it): each v7_0
scenario's cost increase vs Crystal Ball base is NOT evenly spread across the
horizon or across cost components — see fig0a_cost_composition's docstring
for the full breakdown. In short: (1) ~half the cost delta is concentrated
in the single final year 2070, which behaves very differently between the
base run (a smooth declining tail) and every v7_0 scenario (a sharp
late-horizon spike) — a likely end-of-horizon/terminal-value artifact, not a
flexibility-extension cost; (2) of the remaining delta, the majority is
`cost_carbon_emissions_total`, not CAPEX/OPEX — and that variable itself is
~0 in every year except 2050 and 2070, i.e. it behaves like a carbon-BUDGET
shadow price at specific checkpoint years (see carbon_emissions_annual_limit.
csv, identical 0-limit-at-2050 in both datasets) rather than a smooth $/ton
price. This is very likely a real ZEN-garden framework/dataset behavior, not
a bug in this script — the % deltas exactly reproduce the model's own
net_present_cost/carbon_emissions_annual outputs — but it means fig0a's
percentages should not be read as "the extension costs X% more to
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
from matplotlib.patches import Patch

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
    get_capacity,
    get_carrier_production,
    get_storage_flows,
)
from figures_by_scenario import (
    _annual_series,
    build_comparison_df,
    get_annual_cost,
    get_annual_total_cost,
    get_emissions_by_carrier,
    get_emissions_by_technology,
    plot_stacked_bars,
)
from figure_settings import (
    EULER_ROOT,
    Run,
    SCENARIO_PALETTE,
    _text_color_for_bg,
    get_available_years,
    load_results,
)

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

# fig0a/fig0b only. Uses SCENARIO_PALETTE slot 6 (grey) — see the comment there.
# Path is under EULER_ROOT's top level, NOT archive/. History of this path
# getting stale twice now: (1) as of "add results of v7.0..." (7697b97) this
# run was moved out of EULER_ROOT's top level into archive/, which silently
# broke load_base_scenario() (it just prints the "not yet under EULER_ROOT"
# skip note and moves on) — fig0a/fig0b on disk were stale from the old
# v6_1-era run for months until that was corrected. (2) As of the
# 2026-07-29 "run model until 2050 only" re-sync (all v7_1 scenarios AND the
# base case re-run with optimized_years=6, i.e. 2025-2050, replacing the
# previous optimized_years=10 / 2025-2070 runs), a FRESH base run landed at
# this top-level path while BASE_SCENARIO still pointed at the archived,
# now-superseded 10-year run — fig0a was silently comparing the v7_1
# scenarios' 6-year (2025-2050) horizon totals against the base run's 10-year
# (2025-2070) horizon totals, an apples-to-oranges sum that produced
# nonsensical deltas. Verify BASE_SCENARIO's optimized_years matches the
# SCENARIOS list's (system.json's "optimized_years") if fig0a/fig0b numbers
# ever look inconsistent with headline_metrics.csv again — this path tends to
# drift whenever the base case gets independently re-run.
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


# ── 0a: Cost-increase composition (CAPEX/OPEX/carrier/carbon) ──────────────

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


def fig0a_cost_composition(components_with_base: pd.DataFrame) -> None:
    """Decomposes each v7_0 scenario's cost increase vs Crystal Ball base into
    CAPEX/OPEX/carrier (carbon emissions cost excluded — see
    PLOTTED_COST_COMPONENTS above), to show what's actually driving the
    non-carbon part of the increase.

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
    the final period, not a real 2070 emissions price. Treat this figure's
    percentages (and fig0b_emissions_source_comparison's) with that in mind.
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
    savefig(fig, "fig0a_cost_composition")


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


# ── 2: DSM cycles by product, 2050 ──────────────────────────────────────────

# ammonia_DSM/methanol_DSM store an energy carrier (GWh); the other 8
# INDUSTRY_DSM_TECHS store a mass carrier (kt-of-product) — confirmed via
# Results.get_unit() against a solved run. dsm_cycles()'s discharge/capacity
# ratio is unit-safe regardless (each tech divides by its OWN capacity in its
# own native unit, so the resulting cycles/year is dimensionless either way),
# but fig2_dsm_cycles_by_product hatches these two bars so a reader isn't left
# assuming all 10 products are moving directly comparable physical quantities.
DSM_ENERGY_CARRIER_TECHS = {"ammonia_DSM", "methanol_DSM"}


def dsm_cycles(r, year: int) -> pd.Series:
    discharge = get_storage_flows(r, INDUSTRY_DSM_TECHS, "flow_storage_discharge")
    capacity = get_capacity(r, INDUSTRY_DSM_TECHS, "energy")
    cycles = {}
    for tech in INDUSTRY_DSM_TECHS:
        cap = capacity.loc[tech, year] if tech in capacity.index and year in capacity.columns else 0.0
        dis = discharge.loc[tech, year] if tech in discharge.index and year in discharge.columns else 0.0
        cycles[tech] = dis / cap if cap > 1e-9 else 0.0
    return pd.Series(cycles)


def fig2_dsm_cycles_by_product(runs: list[Run]) -> None:
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
    is_energy_carrier = {t: t in DSM_ENERGY_CARRIER_TECHS for t in df.index}
    df.index = [t.replace("_DSM", "").replace("_", " ") for t in df.index]
    is_energy_carrier = {t.replace("_DSM", "").replace("_", " "): v for t, v in is_energy_carrier.items()}
    df = df.sort_values(scenarios[0], ascending=False)

    fig, ax = plt.subplots(figsize=(10, 6))
    n = len(scenarios)
    width = 0.8 / n
    x = np.arange(len(df))
    with plt.rc_context({"hatch.linewidth": 0.5}):  # subtler hatch lines than the 1.0 default
        for i, label in enumerate(scenarios):
            offsets = x + (i - (n - 1) / 2) * width
            color = SCENARIO_PALETTE[[l for _, l in SCENARIOS].index(label)]
            bars = ax.bar(offsets, df[label].values, width, label=legend_labels[label],
                          color=color, edgecolor="white")
            for bar, t in zip(bars, df.index):
                if is_energy_carrier[t]:
                    bar.set_hatch("//")
    ax.set_xticks(x)
    ax.set_xticklabels(df.index, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Discharge cycles / year")
    ax.set_title(f"DSM Utilization by Product, {YEAR}\n"
                 "Demand-Shiftability Assumption (DSM Categories)", fontsize=12, fontweight="bold")
    scenario_handles, scenario_labels = ax.get_legend_handles_labels()
    energy_handle = Patch(facecolor="white", edgecolor="black", hatch="//",
                          label="Energy carrier (GWh): ammonia, methanol")
    mass_handle = Patch(facecolor="white", edgecolor="black",
                        label="Mass carrier (kt): others")
    ax.legend(scenario_handles + [energy_handle, mass_handle],
             scenario_labels + [energy_handle.get_label(), mass_handle.get_label()],
             fontsize=9, frameon=False)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    savefig(fig, "fig2_dsm_cycles_by_product")


# ── 3b: Direct vs temperature-conversion heat pathway, 2050 ─────────────────
# (no more 3a: fig3a_temp_sensitivity_summary was deleted per user request —
# its cost and capacity bars duplicated fig0a/fig1b, and the one new number it
# carried, the emissions delta, is reported as prose in 03_SI.tex instead of a
# standalone chart. Recompute via metrics.loc["Single temperature level"] vs
# metrics.loc["Full flexibility"] on "emissions_total_mton" if that % ever
# needs to be regenerated.)

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


# cmr10 (this module's serif font) has no degree-sign glyph, so a raw "°"
# renders as a garbled substitute character — the superscript-circle is built
# in mathtext instead (mathtext.fontset "cm" covers \circ correctly).
BAND_LABELS = {"heat_industry_0_100": r"0-100$^\circ$C", "heat_industry_100_150": r"100-150$^\circ$C",
               "heat_industry_150_200": r"150-200$^\circ$C"}


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
            ax.text(t, yi, f" {label}", va="center", fontsize=7.5)
    ax.set_yticks(y)
    ax.set_yticklabels([BAND_LABELS[b] for b in bands], fontsize=9)
    ax.set_xlim(right=ax.get_xlim()[1] * 1.35)  # headroom for the end-of-bar labels
    ax.set_xlabel("Net end-use heat demand met [GWh]")
    ax.set_title(f"Heat Demand Met by Temperature Band, {YEAR}", fontsize=11, fontweight="bold")
    ax.legend(fontsize=9, frameon=False, loc="lower right")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    savefig(fig, "fig3b_heat_pathway")


# ── 4: Low-temperature input heat demand by sector and temperature band ────

HEAT_DEMAND_INPUT_JSON = FIGURES_DIR / "heat_demand_by_sector_input.json"

# Same 4 sectors/hues as PRODUCTION_COLOR_MAP above, reused here so a sector
# reads as the same color across every SI figure it appears in. Within each
# sector's bar, temperature band sets the tint (darker = higher band), the
# same hue-for-identity / tint-for-temperature convention HEAT_SUPPLY_COLOR_
# MAP uses (source sets hue, band sets tint) — 0.55/0.3/0 tints mirror that
# map's own 0_100/100_150/150_200 tint values exactly.
HEAT_DEMAND_SECTOR_LABELS = {"glass": "Glass", "ceramic": "Ceramic", "paper": "Paper", "food": "Food"}
HEAT_DEMAND_BAND_TINTS = {"0_100": 0.55, "100_150": 0.3, "150_200": 0.0}
HEAT_DEMAND_BAND_LABELS = {"0_100": r"0-100$^\circ$C", "100_150": r"100-150$^\circ$C", "150_200": r"150-200$^\circ$C"}

# High-temperature fuel demand, stacked on top — a DIFFERENT supply pathway
# (direct combustion, no heat_industry_* carrier involved), not a 4th heat-
# demand band, hence one flat grey (not a sector/band hue) rather than a tint
# scale. Carrier sets the HATCH pattern instead (fixed per carrier, so e.g.
# natural_gas has the same pattern in every sector's bar) — hue/tint is
# reserved for "which sector, which temperature band" (the actual question
# this figure answers); hatch alone is enough to tell carriers apart within
# the single "how much fuel, for scale" grey.
_ETH_GREY = "#6F6F6F"
FUEL_CARRIER_HATCHES = {"natural_gas": ".", "hard_coal": "x", "biomass": "/"}
# Denser than FUEL_CARRIER_HATCHES: a legend swatch is a small fraction of a
# bar segment's area, so the same single-character hatch that reads fine on a
# bar all but disappears at swatch size — legend patches get their own,
# denser pattern (plus a thicker hatch linewidth, applied via rc_context
# where the legend is built) purely so the pattern itself stays visible;
# bars keep the lighter version so labels drawn on top stay readable.
FUEL_CARRIER_LEGEND_HATCHES = {"natural_gas": "...", "hard_coal": "xxx", "biomass": "///"}
FUEL_CARRIER_LABELS = {"natural_gas": "Natural gas", "hard_coal": "Hard coal", "biomass": "Biomass"}
# Single-character hatches (sparser than the "xx"/".." used elsewhere in this
# module) plus a white label backing (below) — a dense hatch under white text
# was illegible; a light hatch + opaque label background reads cleanly at both
# small and large segment sizes.
_FUEL_LABEL_BBOX = dict(facecolor="white", edgecolor="none", alpha=0.75, pad=1.5)


def fig4_heat_demand_by_sector() -> None:
    """Low-temperature industry heat-demand assumption by sector and temperature
    band (FEC_YEAR=2023), i.e. the `demand` ZEN-creator writes onto
    heat_industry_0_100/100_150/150_200 for glass/ceramic/paper/food — NOT a
    solved-model result (contrast fig3b, which shows how the model then meets
    this demand). Grey segments on top add each sector's high-temperature
    (>200°C) fuel demand, split by carrier, for scale: that demand is met by
    DIRECT FUEL COMBUSTION, not any heat_industry_* carrier, so it is a
    different supply pathway rather than a 4th heat-demand band — shown here
    only so the colored low-temperature bands can be read against each
    sector's full process-energy intensity, not in isolation.

    Both pieces are demand_volume[sector].sum() (tonproduct/hour) times a
    GW/(tonproduct/hour) conversion factor, from ProcessParametrizationDataset
    itself (self._heat_cfs, self._sector_params[s].cf_fuel, self._fuel_shares)
    — the exact same object/attributes that build each production tech's real
    conversion_factor, not a re-derivation. See extract_heat_demand_by_sector.
    py's docstring for the full provenance chain (Rehfeldt2017.csv per-sub-
    process temperature distributions -> compute_sector_params(), JRC-IDEES
    thermal FEC -> fuel_shares) and for the cross-check against a materialized
    dataset (Crystal_Ball_ind_heat_v7_3): this script's numbers match that
    dataset's demand.csv sums and glass_production's attributes.json
    conversion factors exactly.

    Values are AGGREGATED (summed) ACROSS ALL MODEL_NODES — EU27 (minus MT,
    CY) + CH + NO + UK — not a per-country breakdown. In GW, the same unit as
    each heat_industry_* carrier's own `demand` attribute (energy carrier,
    unit "GW"), so bar heights are directly comparable to fig1b's
    heat-supply-capacity panel.
    """
    if not HEAT_DEMAND_INPUT_JSON.exists():
        print(f"  skipping fig4_heat_demand_by_sector: {HEAT_DEMAND_INPUT_JSON.relative_to(REPO_ROOT)} "
              "not found — run scripts/extract_heat_demand_by_sector.py under zen-creator-env first")
        return
    import json
    data = json.loads(HEAT_DEMAND_INPUT_JSON.read_text())
    sectors = list(HEAT_DEMAND_SECTOR_LABELS)
    bands = list(HEAT_DEMAND_BAND_TINTS)
    fuel_carriers = [c for c in FUEL_CARRIER_HATCHES if any(c in data[s]["fuel_by_carrier"] for s in sectors)]

    fig, ax = plt.subplots(figsize=(9, 6.5))
    x = np.arange(len(sectors))
    heat_vals = {band: np.array([data[s]["heat"][band] for s in sectors]) for band in bands}
    fuel_vals = {c: np.array([data[s]["fuel_by_carrier"].get(c, 0.0) for s in sectors]) for c in fuel_carriers}
    totals = sum(heat_vals.values()) + sum(fuel_vals.values())
    label_threshold = 0.025 * totals.max()  # segments smaller than this would overlap their own text

    bottom = np.zeros(len(sectors))
    for band in bands:
        vals = heat_vals[band]
        colors = [_eth_tint(PRODUCTION_COLOR_MAP[f"{s}_production"], HEAT_DEMAND_BAND_TINTS[band]) for s in sectors]
        for xi, bi, vi, ci in zip(x, bottom, vals, colors):
            ax.bar(xi, vi, 0.6, bottom=bi, color=ci, edgecolor="white", linewidth=0.5)
            if vi > label_threshold:
                ax.text(xi, bi + vi / 2, f"{vi:.2f}", ha="center", va="center", fontsize=8,
                        color=_text_color_for_bg(ci))
        bottom += vals
    heat_top = bottom.copy()
    with plt.rc_context({"hatch.linewidth": 0.5}):
        for carrier in fuel_carriers:
            vals = fuel_vals[carrier]
            hatch = FUEL_CARRIER_HATCHES[carrier]
            for xi, bi, vi in zip(x, bottom, vals):
                ax.bar(xi, vi, 0.6, bottom=bi, color=_ETH_GREY, edgecolor="white", linewidth=0.5, hatch=hatch)
                if vi > label_threshold:
                    ax.text(xi, bi + vi / 2, f"{vi:.2f}", ha="center", va="center", fontsize=8,
                            color="black", bbox=_FUEL_LABEL_BBOX)
            bottom += vals
    for xi, hi in zip(x, heat_top):
        if hi > 0:
            ax.plot([xi - 0.3, xi + 0.3], [hi, hi], color="black", linewidth=1.0, linestyle=":")
    for xi, total in zip(x, bottom):
        ax.text(xi, total, f"{total:.2f}", ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels([HEAT_DEMAND_SECTOR_LABELS[s] for s in sectors], fontsize=10)
    ax.set_ylabel("Heat / fuel demand [GW]")
    ax.set_title("Low-Temperature Industry Heat Demand by Sector and Temperature Band\n"
                  "(input assumption, ZEN-creator base year 2023, aggregated across all nodes)",
                  fontsize=12, fontweight="bold")
    band_handles = [Patch(facecolor=_eth_tint(_ETH_GREY, HEAT_DEMAND_BAND_TINTS[b]),
                           edgecolor="white", label=f"Heat carrier: {HEAT_DEMAND_BAND_LABELS[b]}") for b in bands]
    fuel_handles = [Patch(facecolor=_ETH_GREY, edgecolor="white", linewidth=0.4,
                           hatch=FUEL_CARRIER_LEGEND_HATCHES[c],
                           label=f"Fuel: {FUEL_CARRIER_LABELS[c]}") for c in fuel_carriers]
    with plt.rc_context({"hatch.linewidth": 1.3}):
        ax.legend(handles=band_handles + fuel_handles, fontsize=8.5, frameon=False, loc="upper left",
                  bbox_to_anchor=(1.02, 1.0), handlelength=3.2, handleheight=2.0)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    savefig(fig, "fig4_heat_demand_by_sector")


# ── 0b: Emissions-source comparison, Full flexibility vs Crystal Ball base ──

# Print-figure-specific ETH palette (does NOT touch the shared, dashboard-wide
# COLOR_MAP in figure_settings.py — see plot_stacked_bars(color_map=...)),
# built from the same 7 ETH Zurich corporate-design colors used everywhere
# else in these SI figures (SCENARIO_PALETTE, COST_COMPONENT_COLORS,
# HEAT_SUPPLY_COLOR_MAP/PRODUCTION_COLOR_MAP above) rather than the generic,
# off-brand hues COLOR_MAP happens to hold for some of these same categories
# (e.g. a plain purple for glass_production). glass_production keeps
# PRODUCTION_COLOR_MAP's ETH blue for cross-figure consistency with fig1b.
# Carriers (the larger, primary stacked segments) each get one solid base
# hue; technologies (smaller, secondary segments) get a lighter tint of a
# related hue via _eth_tint (defined above, fig1b's section) — the tint
# makes "technology" read as visually distinct from "carrier" at a glance,
# on top of the legend's " (carrier)"/" (tech)" suffix.
_ETH_BRONZE, _ETH_PURPLE, _ETH_GREY = "#8E6713", "#A7117A", "#6F6F6F"
EMISSIONS_COLOR_MAP = {
    # Carriers (fuel combustion)
    "crude oil (carrier)": _ETH_BRONZE,
    "natural gas (carrier)": _ETH_TURQUOISE,
    "lng (carrier)": _ETH_GREEN,
    "hard coal (carrier)": _ETH_GREY,
    "lignite (carrier)": _ETH_RED,
    "waste (carrier)": _ETH_PURPLE,
    # Technologies (process + carbon capture)
    "glass production (tech)": _ETH_BLUE,
    "cement kiln (tech)": _eth_tint(_ETH_BRONZE, 0.45),
    "BF BOF (tech)": _eth_tint(_ETH_GREY, 0.35),
    "EAF (tech)": _eth_tint(_ETH_BLUE, 0.45),
    "NG DRI (tech)": _eth_tint(_ETH_TURQUOISE, 0.45),
    "carbon storage (tech)": _eth_tint(_ETH_GREEN, 0.45),
}


def fig0b_emissions_source_comparison(full_run: Run, base_run: Run) -> None:
    """Panel A explains the emissions increase for "Full flexibility" vs
    "Crystal Ball (base)" being much larger (proportionally) than the cost
    increase (fig0a): decomposes each run's year-2025 emissions into carrier
    (fuel combustion) and technology (process + carbon capture) components.
    Panel B then shows WHY the system can't just decarbonize its way out of
    that gap: each run's true cumulative emissions vs. its own carbon budget,
    2025-2070.

    Panel A uses year 2025 (the earliest year present in both runs), not a
    horizon-total sum: WRI's own sector-share figures
    (https://www.wri.org/insights/4-charts-explain-greenhouse-gas-emissions-
    countries-and-sectors) are a single year (2023), so a single-year cut is
    the apples-to-apples comparison, not a multi-year sum. It also sidesteps
    a separate distortion — carbon_storage (CCS) captures ~45-50% of GROSS
    emissions by full-horizon totals in both runs, so a horizon-total NET
    percentage (the original ~21% headline figure) is a % change in the
    small residual of two much larger, near-offsetting numbers and comes out
    mechanically inflated vs. a % change in gross emissions. In 2025, CCS has
    barely ramped up (~-15 Mton out of ~2,269 Mton gross, ~0.7%), so gross
    and net nearly coincide here anyway (~+12.1% vs ~+12.2%) — this single
    year is simultaneously the fair comparison on the WRI single-year
    dimension AND avoids needing the gross/net distinction at all.

    Root cause of the gap itself: "Crystal Ball (base)" has NO industry-heat
    or production sector demand at all — no glass/ceramic/paper/food, no
    heat_industry_0_100/100_150/150_200 (confirmed via `results.get_total
    ("demand")`: these carriers are entirely absent from the base run's
    index, not just zero). The "Full flexibility" extension therefore adds
    genuinely new final energy-service demand, not a re-representation of
    demand the base model already met some other way. Meeting that new
    demand pulls in more fossil-carrier combustion (natural_gas/lng/
    hard_coal/crude_oil/waste — mostly industry boilers) plus a small amount
    of new direct process emissions (glass_production). Because that extra
    boiler CAPEX/OPEX is cheap relative to total system cost (see fig0a's
    docstring), this emissions increase shows up as only a modest cost
    increase — the two are not expected to move in the same proportion, and
    the size of the gap here is a real modeling consequence of extending
    scope, not an error.

    Crystal Ball's scope (README.md: EU27+NO+CH+UK-MT-CY, electricity/heat/
    transport/steel/cement/ammonia/methanol/olefins) maps onto WRI's
    "Energy" (76.7%) + "Industrial processes" (6.2%) categories but excludes
    agriculture (12.3%) and land use (0.9%) — so the ~12% figure here is
    plausible next to WRI's ~18.4% global industry share, especially since
    steel/cement/chemicals (already in the base model, and typically the
    dominant slice of that 18.4%) leave a smaller remainder for the
    genuinely new glass/ceramic/paper/food demand modeled here.

    Panel B plots each run's true, interval-weighted cumulative emissions
    (`carbon_emissions_cumulative`, ZEN-garden's own recursive
    E_y^cum = E_{y-1}^cum + (dy-1)*E_{y-1} + E_y, dy=5 here) against each
    run's own `carbon_emissions_budget` cap. This is NOT the same number as
    Panel A's or the naive per-year sum used in compute_headline_metrics:
    that naive sum badly understates true cumulative emissions because it
    never credits the (dy-1)=4 "skipped" years between representative model
    years.

    As of the 2026-07-29 re-sync, ALL scenarios (base included) were re-run
    with a shortened horizon (`optimized_years=6`, i.e. 2025-2050, down from
    the previous 2025-2070 / optimized_years=10). This changes Panel B's
    story: BOTH runs' true cumulative emissions are still transiently above
    their own budget line at the final modeled year (2050) — base is not
    exempt anymore. Under the old 2025-2070 horizon, base fully repaid its
    budget by 2070 (cumulative == budget to 6 sig figs) via a late-horizon
    swing to net-negative annual emissions (heavy CCS/DAC ramping up from
    ~2055 on) that this shorter horizon simply doesn't reach yet: at 2050
    both runs' `carbon_emissions_annual` are still positive (base +72.5,
    full +119.3 Mton), i.e. neither has started its late-horizon repayment
    swing. So the "front-load now, repay later" pattern from the 2070-run is
    still the underlying mechanism, but the repayment leg now falls outside
    the modeled window — both overshoots shown here are a horizon-truncation
    artifact of stopping at 2050, not evidence that base has stopped fully
    decarbonizing. `constraint_carbon_emissions_budget`'s overshoot variable
    is only priced in the FINAL horizon year (`constraint_cost_carbon_
    emissions_total`'s `mask_last_year`) — with 2050 now being that final
    year for every scenario, both runs incur a real (if small, since
    `price_carbon_emissions_budget_overshoot`=5,000 EUR/ton is finite, a SOFT
    constraint) carbon cost at 2050 that a 2070-horizon run would not have
    shown for base. Verified directly: base overshoot 2,525.7 Mton -> carbon
    cost 12.99M EUR; full overshoot 3,889.7 Mton -> carbon cost 20.05M EUR
    (`cost_carbon_emissions_total[2050]`, matches
    `budget_overshoot*5,000 + annual_overshoot*5,000` exactly, the latter
    from the separate `carbon_emissions_annual_limit=0` constraint at 2050
    only, identical in both runs).

    Full's overshoot is still larger than base's in both absolute (+1,364.0
    Mton) and relative terms, consistent with the pre-existing finding that
    the new industry sectors' real cumulative footprint outgrows the
    ZEN-creator-credited budget top-up (see project memory, traced to
    Mannhardt (2026)'s deployment-barrier mechanism: the new sectors' clean
    heat-supply alternative starts from zero real-world existing capacity,
    while their fossil alternative does not) — that mechanism is unaffected
    by the horizon change and still holds. What's new is only that base
    itself is no longer a clean/zero-cost reference point at this horizon;
    any reading of this figure should treat both overshoot numbers as
    "not yet repaid by 2050", not "failed to decarbonize".
    """
    fr, br = full_run.results, base_run.results
    years_full = get_available_years(fr)
    years_base = get_available_years(br)
    # Earliest year present in both runs — closest available model year to
    # WRI's single-year (2023) snapshot (see docstring).
    year0 = min(set(years_full) & set(years_base))

    carrier_full = get_emissions_by_carrier(fr, year0)
    carrier_base = get_emissions_by_carrier(br, year0)
    # H2_DRI is dropped: its emissions are ~0 in both runs (no delta to show),
    # so it only adds clutter to the composition legend.
    tech_full = get_emissions_by_technology(fr, year0).drop("H2_DRI", errors="ignore")
    tech_base = get_emissions_by_technology(br, year0).drop("H2_DRI", errors="ignore")

    # cmr10 (this module's serif font, see the plt.rcParams block up top) has
    # no underscore glyph, so raw "_"-joined category names render as a
    # garbled substitute character — display labels use spaces instead.
    def disp(name: str) -> str:
        return name.replace("_", " ")

    # Panel A: full emissions composition per run (carrier + technology
    # stacked together, suffix-disambiguated) so bar heights reproduce each
    # run's true net total for year0.
    net_base = carrier_base.sum() + tech_base.sum()
    net_full = carrier_full.sum() + tech_full.sum()
    composition = build_comparison_df([
        (f"{base_run.label}\n(net {net_base:,.0f})",
         pd.concat([carrier_base.rename(lambda c: f"{disp(c)} (carrier)"),
                    tech_base.rename(lambda t: f"{disp(t)} (tech)")])),
        (f"{full_run.label}\n(net {net_full:,.0f})",
         pd.concat([carrier_full.rename(lambda c: f"{disp(c)} (carrier)"),
                    tech_full.rename(lambda t: f"{disp(t)} (tech)")])),
    ])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7), gridspec_kw={"width_ratios": [1, 1.3]})
    plot_stacked_bars(composition, "Emissions Composition by Source",
                      f"Mton CO$_2$eq, year {year0}", ax1, show_segment_labels=True,
                      color_map=EMISSIONS_COLOR_MAP)

    # Panel B: cumulative emissions vs. each run's own carbon budget, 2025-2070.
    def _series(r, name):
        s = r.get_total(name)
        return {int(k): float(v) for k, v in s.items()}

    cum_full = _series(fr, "carbon_emissions_cumulative")
    cum_base = _series(br, "carbon_emissions_cumulative")
    budget_full = float(fr.get_total("carbon_emissions_budget").iloc[0])
    budget_base = float(br.get_total("carbon_emissions_budget").iloc[0])
    years = sorted(cum_full)
    base_vals = [cum_base[y] for y in years]
    full_vals = [cum_full[y] for y in years]

    # Transient mid-horizon excess above each run's OWN budget line — real,
    # but costs nothing except at the final year (see docstring). Shown
    # muted/shared so it doesn't read as "this is the penalised amount".
    over_base = np.array([v > budget_base for v in base_vals])
    over_full = np.array([v > budget_full for v in full_vals])
    ax2.fill_between(years, base_vals, budget_base, where=over_base,
                      color=base_run.color, alpha=0.12, interpolate=True,
                      label="excess above own budget, not yet repaid")
    ax2.fill_between(years, full_vals, budget_full, where=over_full,
                      color=full_run.color, alpha=0.12, interpolate=True,
                      label="_nolegend_")

    ax2.plot(years, base_vals, marker="o", color=base_run.color,
             linewidth=2, label=f"{base_run.label} - cumulative emissions")
    ax2.axhline(budget_base, color=base_run.color, linestyle="--", linewidth=1.3,
                label=f"{base_run.label} - carbon budget ({budget_base:,.0f} Mton)")

    ax2.plot(years, full_vals, marker="o", color=full_run.color,
             linewidth=2, label=f"{full_run.label} - cumulative emissions")
    ax2.axhline(budget_full, color=full_run.color, linestyle="--", linewidth=1.3,
                label=f"{full_run.label} - carbon budget ({budget_full:,.0f} Mton)")

    # The only gap that actually costs money: the final-year shortfall.
    # As of the shortened (2025-2050) horizon, BOTH runs land mid-overshoot at
    # the final modeled year — neither has reached its late-horizon
    # net-negative repayment swing yet (see docstring). Carbon cost is pulled
    # directly from the solved model rather than hardcoded, since it depends
    # on which year happens to be "final" for a given horizon.
    final_year = years[-1]
    overshoot_full = cum_full[final_year] - budget_full
    overshoot_base = cum_base[final_year] - budget_base
    cost_full = float(fr.get_total("cost_carbon_emissions_total")[final_year])
    cost_base = float(br.get_total("cost_carbon_emissions_total")[final_year])
    ax2.plot([final_year, final_year], [budget_full, cum_full[final_year]],
             color=_ETH_RED, linewidth=3, solid_capstyle="butt", zorder=5)
    ax2.plot([final_year, final_year], [budget_base, cum_base[final_year]],
             color=_ETH_RED, linewidth=3, solid_capstyle="butt", zorder=5)
    # Short, numbers-only labels placed to the RIGHT of the final data point
    # (off the plotted lines/legend entirely — a longer prose version placed
    # near the top-left previously landed behind the legend and the lines
    # themselves, per user feedback) — set_xlim below opens up the margin
    # these sit in.
    year_step = years[-1] - years[-2]
    label_x = final_year + 0.15 * year_step
    ax2.annotate(f"+{overshoot_full:,.0f} Mt\n{cost_full / 1e6:.1f}M EUR",
        xy=(final_year, cum_full[final_year]), xytext=(label_x, cum_full[final_year]),
        fontsize=8, fontweight="bold", color=_ETH_RED, ha="left", va="center",
        arrowprops=dict(arrowstyle="->", color=_ETH_RED))
    ax2.annotate(f"+{overshoot_base:,.0f} Mt\n{cost_base / 1e6:.1f}M EUR",
        xy=(final_year, cum_base[final_year]), xytext=(label_x, cum_base[final_year]),
        fontsize=8, fontweight="bold", color=base_run.color, ha="left", va="center",
        arrowprops=dict(arrowstyle="->", color=base_run.color))

    ax2.set_xlabel("Year")
    ax2.set_ylabel("Cumulative carbon emissions [Mton CO$_2$eq]")
    ax2.set_title("Cumulative Emissions vs. Carbon Budget", fontsize=11, fontweight="bold")
    ax2.set_xlim(right=final_year + 0.6 * year_step)  # headroom for the RHS labels
    ax2.set_ylim(top=max(full_vals) * 1.1)
    ax2.legend(fontsize=7.5, loc="upper left")
    ax2.grid(alpha=0.3)

    fig.suptitle("Emission Increase Attributable to the Newly Implemented Industry Sectors",
                 fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    savefig(fig, "fig0b_emissions_source_comparison")


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
        components_with_base = compute_cost_components([base_run] + runs)
        fig0a_cost_composition(components_with_base)
        fig0b_emissions_source_comparison(by_label(runs, "Full flexibility"), base_run)
    else:
        print(f"  skipping fig0a/fig0b: {BASE_SCENARIO[0]} not yet under {EULER_ROOT}")
    fig1a_cost_delta(metrics)
    fig1b_industry_capacity(runs)
    fig2_dsm_cycles_by_product(runs)
    fig3b_heat_pathway(runs)
    fig4_heat_demand_by_sector()
    print(f"Done. Figures in {FIGURES_DIR.relative_to(REPO_ROOT)}/")


if __name__ == "__main__":
    main()
