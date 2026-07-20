"""Generate print-ready figures for the MT_report SI Results section.

Covers the four planned subsections in
`MT_report_HG/Sections/03_SI.tex` (`\\label{sec:si-results}`) plus one
additional figure, across the 5 converged Crystal_Ball_HG_v5_3 euler
scenarios (Full flexibility, No flexibility, DSM only, TES only, Single
temperature level):

  1a. fig1a_cost_delta                — discounted system cost delta vs Full flexibility
  1b. fig1b_industry_capacity         — industry heat-supply & production capacity, 2070
  2a. fig2a_tes_dsm_utilization       — TES vs DSM lifetime charge/discharge, log scale
  2b. fig2b_dsm_cycles_by_product     — DSM utilization (cycles/yr) by product, 2070
  3a. fig3a_emissions_trajectory      — system CO2 emissions, all years, all scenarios
  3b. fig3b_emissions_decomposition   — system-total vs industry-process CO2, 2070
  4a. fig4a_temp_sensitivity_summary  — Full flex vs Single-temp: cost/emissions/capacity delta
  4b. fig4b_heat_pathway              — direct vs temp-conversion heat production, 2070
  5.  fig5_flexibility_equivalence    — DSM-only == Full flex, TES-only == No flex

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
    INDUSTRY_PROCESS_TECHS,
    _annual_series,
    build_comparison_df,
    filter_techs,
    get_annual_total_cost,
    get_emissions_by_technology,
    plot_stacked_bars,
)
from figure_settings import EULER_ROOT, Run, SCENARIO_PALETTE, get_available_years, load_results

FIGURES_DIR = REPO_ROOT / "data" / "outputs" / "figures" / "SI_results"
YEAR = 2070  # single-year snapshot used throughout; horizon totals used where noted

# Thesis-consistent scenario order/labels (Table~SIScenarios), distinct from
# the dashboard's shorter "Baseline" label for the same run.
SCENARIOS = [
    ("Crystal_Ball_HG_v5_3_2025_10a_5a_interval_10ts", "Full flexibility"),
    ("Crystal_Ball_HG_v5_3_no_flexibility_2025_10a_5a_interval_10ts", "No flexibility"),
    ("Crystal_Ball_HG_v5_3_DSM_only_2025_10a_5a_interval_10ts", "DSM only"),
    ("Crystal_Ball_HG_v5_3_TES_only_2025_10a_5a_interval_10ts", "TES only"),
    ("Crystal_Ball_HG_v5_3_single_temp_2025_10a_5a_interval_10ts", "Single temperature level"),
]


def load_scenarios() -> list[Run]:
    runs = []
    for i, (folder, label) in enumerate(SCENARIOS):
        results = load_results(EULER_ROOT, folder)
        runs.append(Run(name=folder, label=label, mode="euler", results=results,
                         color=SCENARIO_PALETTE[i % len(SCENARIO_PALETTE)]))
    return runs


def by_label(runs: list[Run], label: str) -> Run:
    return next(r for r in runs if r.label == label)


def savefig(fig: plt.Figure, name: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{name}.png"
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {path.relative_to(REPO_ROOT)}")


# ── Shared metrics (feed figures 1a, 4a, 5) ────────────────────────────────

def industry_heat_capacity(r, year: int) -> float:
    """Total industry heat-supply capacity (boilers + HPs only), GW.

    Deliberately excludes heat_industry_temp_conversion_*: that pathway is a
    near-zero-cost, effectively unconstrained lossless conversion, so its
    "capacity" is a modeling artifact (~37,700 GW, three orders of magnitude
    above the real boiler/HP capacity) rather than a meaningful investment —
    it is examined separately in fig4b's direct-vs-conversion pathway split.
    """
    cap = get_capacity(r, INDUSTRY_HEAT_TECHS_BOILERS_HP, "power")
    return float(cap[year].sum()) if year in cap.columns else 0.0


def compute_headline_metrics(runs: list[Run]) -> pd.DataFrame:
    """Horizon-total discounted cost, horizon-total emissions, and 2070 industry
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


# ── 1b: Industry capacity, 2070 ─────────────────────────────────────────────

def fig1b_industry_capacity(runs: list[Run]) -> None:
    # temp-conversion capacity excluded here — see industry_heat_capacity() docstring;
    # its own direct-vs-conversion pathway is the subject of fig4b instead.
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
    # log scale can't show exact zeros; floor at a small epsilon for display only
    plot_df = df.clip(lower=1e-6)

    fig, ax = plt.subplots(figsize=(9, 6))
    n = len(scenarios)
    width = 0.8 / n
    x = np.arange(len(categories))
    for i, label in enumerate(scenarios):
        offsets = x + (i - (n - 1) / 2) * width
        color = SCENARIO_PALETTE[[s for s, _ in SCENARIOS].index(
            next(f for f, l in SCENARIOS if l == label))]
        ax.bar(offsets, plot_df[label].values, width, label=label, color=color, edgecolor="white")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=9)
    ax.set_ylabel("Lifetime throughput (log scale)")
    ax.set_title("TES vs DSM — Lifetime Utilization Scale\n"
                  "(mixed units for DSM — see Table SIDSM; TES throughput is ~$10^5$–$10^6\\times$ smaller)",
                  fontsize=11, fontweight="bold")
    ax.legend(fontsize=9, frameon=False)
    ax.grid(axis="y", alpha=0.3, which="both")
    fig.tight_layout()
    savefig(fig, "fig2a_tes_dsm_utilization")


# ── 2b: DSM cycles by product, 2070 ─────────────────────────────────────────

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
    scenarios = ["Full flexibility", "Single temperature level"]
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
        ax.bar(offsets, df[label].values, width, label=label, color=color, edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(df.index, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Discharge cycles / year")
    ax.set_title(f"DSM Utilization by Product — Year {YEAR}", fontsize=12, fontweight="bold")
    ax.legend(fontsize=9, frameon=False)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    savefig(fig, "fig2b_dsm_cycles_by_product")


# ── 3a: System emissions trajectory ─────────────────────────────────────────

def fig3a_emissions_trajectory(runs: list[Run]) -> None:
    fig, ax = plt.subplots(figsize=(9, 6))
    for i, r in enumerate(runs):
        years = get_available_years(r.results)
        s = _annual_series(r.results, "carbon_emissions_annual", years)
        ax.plot(s.index, s.values, marker="o", label=r.label,
                color=SCENARIO_PALETTE[i % len(SCENARIO_PALETTE)])
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Year")
    ax.set_ylabel("System CO$_2$ emissions [Mton/yr]")
    ax.set_title("System-wide Emissions Trajectory", fontsize=12, fontweight="bold")
    ax.legend(fontsize=9, frameon=False)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    savefig(fig, "fig3a_emissions_trajectory")


# ── 3b: System vs industry-process emissions, 2070 ──────────────────────────

def fig3b_emissions_decomposition(runs: list[Run]) -> None:
    rows = {}
    for r in runs:
        system_total = float(_annual_series(r.results, "carbon_emissions_annual", [YEAR]).sum())
        industry = float(filter_techs(get_emissions_by_technology(r.results, YEAR),
                                       INDUSTRY_PROCESS_TECHS).sum())
        rows[r.label] = {"System total": system_total, "Industry process only": industry}
    df = pd.DataFrame(rows).T

    fig, ax = plt.subplots(figsize=(9, 6))
    x = np.arange(len(df))
    width = 0.35
    ax.bar(x - width / 2, df["System total"], width, label="System total",
           color="#455a64", edgecolor="white")
    ax.bar(x + width / 2, df["Industry process only"], width, label="Industry process only\n(cement, steel, glass, ceramic, paper, food)",
           color="#9370db", edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(df.index, rotation=20, ha="right")
    ax.set_ylabel("CO$_2$ emissions [Mton]")
    ax.set_title(f"System vs Industry-Process Emissions — Year {YEAR}", fontsize=12, fontweight="bold")
    ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    savefig(fig, "fig3b_emissions_decomposition")


# ── 4a: Temperature-resolution sensitivity summary ──────────────────────────

def fig4a_temp_sensitivity_summary(metrics: pd.DataFrame) -> None:
    full = metrics.loc["Full flexibility"]
    single = metrics.loc["Single temperature level"]
    pct = (single - full) / full * 100

    labels = ["Discounted\nsystem cost", "System\nemissions", "Industry heat\ncapacity (2070)"]
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
    savefig(fig, "fig4a_temp_sensitivity_summary")


# ── 4b: Direct vs temperature-conversion heat pathway, 2070 ─────────────────

def heat_pathway_split(r, year: int) -> pd.Series:
    direct, conversion = 0.0, 0.0
    for carrier in INDUSTRY_HEAT_CARRIERS_ENERGY:
        prod = get_carrier_production(r, carrier)
        if prod.empty or year not in prod.columns:
            continue
        direct += prod.loc[prod.index.isin(INDUSTRY_HEAT_TECHS_BOILERS_HP), year].sum()
        conversion += prod.loc[prod.index.isin(INDUSTRY_HEAT_TECHS_TEMP_CONV), year].sum()
    return pd.Series({"Direct (boiler/HP)": direct, "Temp-conversion cascade": conversion})


def fig4b_heat_pathway(runs: list[Run]) -> None:
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
    savefig(fig, "fig4b_heat_pathway")


# ── 5: Flexibility-mechanism equivalence ─────────────────────────────────────

def fig5_flexibility_equivalence(metrics: pd.DataFrame) -> None:
    order = ["Full flexibility", "DSM only", "No flexibility", "TES only", "Single temperature level"]
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
    fig.suptitle("DSM Alone Reproduces Full Flexibility — TES Alone Reproduces No Flexibility",
                 fontsize=12, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    savefig(fig, "fig5_flexibility_equivalence")


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> None:
    print("Loading 5 euler scenarios...")
    runs = load_scenarios()
    print("Computing headline metrics (cost, emissions, capacity)...")
    metrics = compute_headline_metrics(runs)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(FIGURES_DIR / "headline_metrics.csv")
    print(f"  wrote {(FIGURES_DIR / 'headline_metrics.csv').relative_to(REPO_ROOT)}")

    print("Generating figures...")
    fig1a_cost_delta(metrics)
    fig1b_industry_capacity(runs)
    fig2a_tes_dsm_utilization(runs)
    fig2b_dsm_cycles_by_product(runs)
    fig3a_emissions_trajectory(runs)
    fig3b_emissions_decomposition(runs)
    fig4a_temp_sensitivity_summary(metrics)
    fig4b_heat_pathway(runs)
    fig5_flexibility_equivalence(metrics)
    print(f"Done. Figures in {FIGURES_DIR.relative_to(REPO_ROOT)}/")


if __name__ == "__main__":
    main()
