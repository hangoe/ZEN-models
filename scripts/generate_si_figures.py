"""Generate print-ready figures for the MT_report SI Results section.

Covers the SI Results subsections in `MT_report_HG/Sections/03_SI.tex`
(`\\label{sec:si-results}`) plus one additional figure, across the 7
case-study scenarios in that section's Table~SIScenarios — 6
Crystal_Ball_HG_v6_0 euler runs (Full flexibility, No flexibility, DSM only,
TES only, Single temperature level, DSM pessimistic) plus the unmodified
"Crystal Ball (base)" reference case (dataset `Crystal_Ball`, plain — no
`Crystal_Ball_HG_v6_0` prefix, staged from data/Crystal_Ball, see
run_model.py):

  0.  fig0_benchmark_comparison       — cost & emissions increase of each v6_0 scenario vs Crystal Ball base
  1a. fig1a_cost_delta                — discounted system cost delta vs Full flexibility
  1b. fig1b_industry_capacity         — industry heat-supply & production capacity, 2050
  2a. fig2a_tes_dsm_utilization       — TES vs DSM lifetime charge/discharge, log scale
  2b. fig2b_dsm_cycles_by_product     — DSM utilization (cycles/yr) by product: optimistic vs pessimistic
  3a. fig3a_temp_sensitivity_summary  — Full flex vs Single-temp: cost/emissions/capacity delta
  3b. fig3b_heat_pathway              — direct vs temp-conversion heat production, 2050
  4.  fig4_flexibility_equivalence    — DSM-only == Full flex, TES-only == No flex, DSM-pessimistic breaks it

The planned "Emissions" subsection (fig3a/3b) is intentionally NOT built as a
standalone comparison across the 6 v6_0 scenarios: their horizon-total
emissions only span ~2.3% of each other (headline_metrics.csv), so an
absolute-scale trajectory or decomposition just shows six overlapping lines/
bars. fig0 carries this finding instead — the 6 v6_0 scenarios cluster
tightly relative to each other there, in visible contrast to the much larger
gap vs "Crystal Ball (base)" — without a dedicated, mostly-flat 3a/3b pair.

"Crystal Ball (base)" only feeds fig0. Its euler run hadn't converged as of
this writing, so fig0 is skipped (with a printed note) until
Crystal_Ball_2025_10a_5a_interval_10ts/ exists under EULER_ROOT — everything
else still generates. It's deliberately NOT a 7th entry in SCENARIOS below or
in any other figure: it has no industry heat/DSM/TES sector at all, so
capacity/utilization figures (1b, 2a, 2b, 3a's capacity term, 3b, 4's
capacity panel) would show a misleading 0 for it rather than a meaningful
absence. Cost and emissions totals, by contrast, are well-defined for any
run regardless of sector structure, which is what makes it fig0 material.

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
    ("Crystal_Ball_HG_v6_0_no_flexibility_2025_10a_5a_interval_10ts", "No flexibility"),
    ("Crystal_Ball_HG_v6_0_2025_10a_5a_interval_10ts", "Full flexibility"),
    ("Crystal_Ball_HG_v6_0_DSM_only_2025_10a_5a_interval_10ts", "DSM only"),
    ("Crystal_Ball_HG_v6_0_TES_only_2025_10a_5a_interval_10ts", "TES only"),
    ("Crystal_Ball_HG_v6_0_single_temp_2025_10a_5a_interval_10ts", "Single temperature level"),
    ("Crystal_Ball_HG_v6_0_DSM_pessimistic_2025_10a_5a_interval_10ts", "DSM pessimistic"),
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


# ── 0: v6_0 scenarios vs unmodified Crystal Ball base ───────────────────────

def fig0_benchmark_comparison(metrics_with_base: pd.DataFrame) -> None:
    """Cost & emissions of each v6_0 scenario relative to the unmodified
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
        (axes[0], cost_pct, "Δ discounted system cost [%]", "System Cost"),
        (axes[1], em_pct, "Δ system emissions, horizon total [%]", "System Emissions"),
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
    savefig(fig, "fig0_benchmark_comparison")


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
    ax.set_ylabel("Δ discounted system cost vs Full flexibility [MEUR]")
    ax.set_title("System Cost Delta vs Full Flexibility\n(discounted, full horizon)",
                  fontsize=12, fontweight="bold")
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    fig.tight_layout()
    savefig(fig, "fig1a_cost_delta")


# ── 1b: Industry capacity, 2050 ─────────────────────────────────────────────

def fig1b_industry_capacity(runs: list[Run]) -> None:
    # temp-conversion capacity excluded here — see industry_heat_capacity() docstring;
    # its own direct-vs-conversion pathway is the subject of fig3b instead.
    heat_series = [(r.label, get_capacity(r.results, INDUSTRY_HEAT_TECHS_BOILERS_HP, "power")
                    .get(YEAR, pd.Series(dtype=float))) for r in runs]
    prod_series = [(r.label, get_capacity(r.results, INDUSTRY_HEAT_TECHS_PRODUCTION, "power")
                    .get(YEAR, pd.Series(dtype=float))) for r in runs]

    fig, axes = plt.subplots(1, 2, figsize=(15, 7))
    fig.suptitle(f"Industry Technology Capacity — Year {YEAR}", fontsize=13, fontweight="bold")
    plot_stacked_bars(build_comparison_df(heat_series), "Heat Supply (boilers & heat pumps)",
                      "GW", axes[0], show_segment_labels=True)
    plot_stacked_bars(build_comparison_df(prod_series), "Production Technologies",
                      "ton/h", axes[1], show_segment_labels=True)
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
    ax.set_title("TES vs DSM — Lifetime Utilization Scale\n"
                  "(mixed units for DSM — see Table SIDSM; TES throughput is ~$10^5$–$10^6\\times$ smaller)",
                  fontsize=11, fontweight="bold")
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
    ax.set_title(f"DSM Utilization by Product — Year {YEAR}\n"
                 "Sensitivity to Demand-Shiftability Assumption", fontsize=12, fontweight="bold")
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

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(labels, values, color="#ff7043", edgecolor="white")
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f"{v:+.2f}%", ha="center", va="bottom" if v >= 0 else "top",
                fontsize=10, fontweight="bold")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("Δ Single temperature level vs Full flexibility [%]")
    ax.set_title("Sensitivity to Temperature-Band Resolution", fontsize=12, fontweight="bold")
    fig.tight_layout()
    savefig(fig, "fig3a_temp_sensitivity_summary")


# ── 3b: Direct vs temperature-conversion heat pathway, 2050 ─────────────────

def heat_pathway_split(r, year: int) -> pd.Series:
    direct, conversion = 0.0, 0.0
    for carrier in INDUSTRY_HEAT_CARRIERS_ENERGY:
        prod = get_carrier_production(r, carrier)
        if prod.empty or year not in prod.columns:
            continue
        direct += prod.loc[prod.index.isin(INDUSTRY_HEAT_TECHS_BOILERS_HP), year].sum()
        conversion += prod.loc[prod.index.isin(INDUSTRY_HEAT_TECHS_TEMP_CONV), year].sum()
    return pd.Series({"Direct (boiler/HP)": direct, "Temp-conversion cascade": conversion})


def fig3b_heat_pathway(runs: list[Run]) -> None:
    scenarios = ["Full flexibility", "Single temperature level"]
    series = [(label, heat_pathway_split(by_label(runs, label).results, YEAR)) for label in scenarios]
    df = build_comparison_df(series)

    fig, ax = plt.subplots(figsize=(7, 6))
    plot_stacked_bars(df, f"Heat Production Pathway — Year {YEAR}", "GWh", ax, show_segment_labels=True)
    ax.set_title(ax.get_title() +
                 "\n(Single-temp routes end-use demand through the conversion cascade;\n"
                 "totals are not directly comparable to end-use demand — see text)",
                 fontsize=10, fontweight="bold")
    fig.tight_layout()
    savefig(fig, "fig3b_heat_pathway")


# ── 4: Flexibility-mechanism equivalence ─────────────────────────────────────

def fig4_flexibility_equivalence(metrics: pd.DataFrame) -> None:
    # Order matches Table SIScenarios (see SCENARIOS above), which still
    # keeps "Full flexibility" and "DSM only" adjacent (the equivalence this
    # figure is named for). "No flexibility" and "TES only" — the other
    # equivalent pair — are no longer adjacent under table order; the
    # equivalence is still readable from the bar heights regardless of
    # x-position. "DSM pessimistic" sits last, matching the table: it reruns
    # "Full flexibility" (DSM+TES both active) with the pessimistic instead
    # of optimistic demand-shiftability categorization, testing whether the
    # DSM-only == Full-flexibility equivalence survives, or is an artifact of
    # the optimistic categorization making DSM cheap enough to fully
    # substitute for TES.
    order = [label for _, label in SCENARIOS]
    m = metrics.loc[order]
    panels = [
        ("npc_total_meur", "Discounted system cost [MEUR]"),
        ("emissions_total_mton", "System emissions, horizon total [Mton]"),
        ("industry_heat_capacity_gw", f"Industry heat capacity, {YEAR} [GW]"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.5))
    for ax, (col, ylabel) in zip(axes, panels):
        colors = [SCENARIO_PALETTE[[l for _, l in SCENARIOS].index(lbl)] for lbl in order]
        ax.bar(order, m[col].values, color=colors, edgecolor="white")
        ax.set_ylabel(ylabel, fontsize=9)
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize=8)
        ax.grid(axis="y", alpha=0.3)
    fig.suptitle("DSM Alone Reproduces Full Flexibility — TES Alone Reproduces No Flexibility\n"
                 "(...Under the Optimistic DSM Assumption)",
                 fontsize=12, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    savefig(fig, "fig4_flexibility_equivalence")


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
        fig0_benchmark_comparison(metrics_with_base)
    else:
        print(f"  skipping fig0_benchmark_comparison: {BASE_SCENARIO[0]} not yet under {EULER_ROOT}")
    fig1a_cost_delta(metrics)
    fig1b_industry_capacity(runs)
    fig2a_tes_dsm_utilization(runs)
    fig2b_dsm_cycles_by_product(runs)
    fig3a_temp_sensitivity_summary(metrics)
    fig3b_heat_pathway(runs)
    fig4_flexibility_equivalence(metrics)
    print(f"Done. Figures in {FIGURES_DIR.relative_to(REPO_ROOT)}/")


if __name__ == "__main__":
    main()
