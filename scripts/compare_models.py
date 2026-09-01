"""Compare two ZEN-garden model outputs side by side.

Produces stacked bar plots for:
  1. Total system emissions (carrier + technology)
  2. Total system costs (CAPEX + OPEX)
  3. Industry process costs
  4. Industry heating costs
  5. Fuel consumption breakdown (natural_gas, hard_coal, lng, waste)

Usage:
    python scripts/compare_models.py [model_a] [model_b]
"""

import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from zen_garden import Results

from plots.figure_settings import (
    apply_font_mode,
    load_results as _load_results,
    plot_stacked_bars,
)

# Match the rest of the figure scripts' font -- see figure_settings.FONT_MODE
# for the rationale and for the one-flag toggle that switches every figure
# script in this repo at once.
apply_font_mode()

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "outputs"
FIGURES_DIR = OUTPUT_DIR / "figures"
DEFAULT_MODEL_A = "Crystal_Ball_HG_v4_4_2025_1a_1a_interval_1ts"
DEFAULT_MODEL_B = "Crystal_Ball_HG_v4_6_2025_1a_1a_interval_1ts"
YEAR = 2025

INDUSTRY_PROCESS_TECHS = [
    "cement_kiln", "cement_post_comb", "biomass_to_cement_fuel",
    "coal_to_cement_fuel", "hydrogen_to_cement_fuel", "waste_to_cement_fuel",
    "BF_BOF", "BF_BOF_CCS", "EAF", "NG_DRI", "NG_DRI_CCS", "H2_DRI",
    "glass_production", "ceramic_production", "paper_production", "food_production",
]

INDUSTRY_HEATING_TECHS = [
    "natural_gas_boiler_industry", "electrode_boiler_industry", "biomass_boiler_industry",
    "heat_pump_industry_0_100_waste_heat", "heat_pump_industry_0_100_water",
    "heat_pump_industry_100_150_waste_heat", "heat_pump_industry_100_150_water",
    "heat_pump_industry_150_200_waste_heat", "heat_pump_industry_150_200_water",
]

HEAT_TECHS = [
    "natural_gas_boiler", "biomass_boiler", "heat_pump",
    "electrode_boiler", "oil_boiler", "district_heating_grid",
]

DISTRICT_HEAT_TECHS = [
    "natural_gas_boiler_DH", "hard_coal_boiler_DH", "waste_boiler_DH",
    "biomass_boiler_DH", "oil_boiler_DH", "heat_pump_DH",
    "electrode_boiler_DH",
]

# ── Data helpers ─────────────────────────────────────────────────────────────

def load_results(model_name: str) -> Results:
    # figure_settings.load_results's var_dict.h5 BFS (max_depth=3) already
    # handles the "descend into the one subdirectory" case this used to do
    # by hand (and deeper nesting besides), so just delegate straight to it.
    return _load_results(OUTPUT_DIR, model_name)


def get_emissions_by_carrier(r: Results) -> pd.Series:
    df = r.get_total("carbon_emissions_carrier")
    series = df.groupby("carrier").sum()[YEAR]
    return series[series.abs() > 1e-6].sort_values(ascending=False)


def get_emissions_by_technology(r: Results) -> pd.Series:
    df = r.get_total("carbon_emissions_technology")
    series = df.groupby("technology").sum()[YEAR]
    return series[series.abs() > 1e-6].sort_values(ascending=False)


def get_capex_by_technology(r: Results) -> pd.Series:
    df = r.get_total("cost_capex_yearly")
    series = df.groupby("technology").sum()[YEAR]
    return series[series.abs() > 1e-6].sort_values(ascending=False)


def get_opex_by_technology(r: Results) -> pd.Series:
    df = r.get_total("cost_opex_yearly")
    series = df.groupby("technology").sum()[YEAR]
    return series[series.abs() > 1e-6].sort_values(ascending=False)


def get_fuel_consumption(r: Results, carrier: str) -> pd.Series:
    flow_in = r.get_total("flow_conversion_input")
    if carrier not in flow_in.index.get_level_values("carrier"):
        return pd.Series(dtype=float)
    series = flow_in.xs(carrier, level="carrier").groupby("technology").sum()[YEAR]
    return series[series.abs() > 1e-3].sort_values(ascending=False)


def get_fuel_supply(r: Results, carrier: str) -> pd.Series:
    pieces = {}
    imp = r.get_total("flow_import")
    if carrier in imp.index.get_level_values("carrier"):
        total_import = imp.xs(carrier, level="carrier").sum()[YEAR]
        if abs(total_import) > 1e-3:
            pieces[f"{carrier} import"] = total_import
    flow_out = r.get_total("flow_conversion_output")
    if carrier in flow_out.index.get_level_values("carrier"):
        by_tech = flow_out.xs(carrier, level="carrier").groupby("technology").sum()[YEAR]
        for tech, val in by_tech.items():
            if abs(val) > 1e-3:
                pieces[tech] = val
    return pd.Series(pieces).sort_values(ascending=False)


def get_carrier_production(r: Results, carrier: str) -> pd.Series:
    flow_out = r.get_total("flow_conversion_output")
    if carrier not in flow_out.index.get_level_values("carrier"):
        return pd.Series(dtype=float)
    series = flow_out.xs(carrier, level="carrier").groupby("technology").sum()[YEAR]
    return series[series.abs() > 1e-3].sort_values(ascending=False)


def filter_techs(series: pd.Series, tech_list: list[str]) -> pd.Series:
    present = [t for t in tech_list if t in series.index]
    filtered = series.loc[present]
    return filtered[filtered.abs() > 1e-6].sort_values(ascending=False)


def build_comparison_df(
    series_a: pd.Series, series_b: pd.Series, name_a: str, name_b: str
) -> pd.DataFrame:
    combined = pd.DataFrame({name_a: series_a, name_b: series_b}).fillna(0)
    return combined.sort_values(name_a, ascending=True)


# ── Plotting ─────────────────────────────────────────────────────────────────

def plot_cost_figure(
    df_capex: pd.DataFrame,
    df_opex: pd.DataFrame,
    title: str,
    save_path: Path,
    show_segment_labels: bool = False,
):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(title, fontsize=14, fontweight="bold")
    plot_stacked_bars(df_capex, "CAPEX by Technology", "MEUR", axes[0],
                      show_legend=False, show_segment_labels=show_segment_labels)
    plot_stacked_bars(df_opex, "OPEX by Technology", "MEUR", axes[1],
                      show_legend=False, show_segment_labels=show_segment_labels)

    handles_all, labels_all = {}, {}
    for ax in axes:
        for h, l in zip(*ax.get_legend_handles_labels()):
            if l not in labels_all:
                handles_all[l] = h
                labels_all[l] = l
    ordered = sorted(labels_all.keys())
    ncol = 2 if len(ordered) > 10 else 1
    fig.legend(
        [handles_all[l] for l in reversed(ordered)],
        list(reversed(ordered)),
        loc="upper center", bbox_to_anchor=(0.5, -0.02),
        fontsize=7, frameon=False, ncol=ncol,
    )
    fig.tight_layout(rect=[0, 0.05 + 0.02 * len(ordered) / ncol / 10, 1, 0.93])
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"Plot saved to {save_path}")
    return fig


def plot_fuel_consumption(
    r_a: Results,
    r_b: Results,
    model_a: str,
    model_b: str,
    carriers: list[str],
    save_path: Path,
):
    n = len(carriers)
    fig, axes = plt.subplots(1, n, figsize=(6 * n, 7))
    if n == 1:
        axes = [axes]
    fig.suptitle(
        f"Fuel Consumption by Technology: {model_a} vs {model_b}  (Year {YEAR})",
        fontsize=14, fontweight="bold",
    )
    for ax, carrier in zip(axes, carriers):
        fa = get_fuel_consumption(r_a, carrier)
        fb = get_fuel_consumption(r_b, carrier)
        df = build_comparison_df(fa, fb, model_a, model_b)
        plot_stacked_bars(df, carrier.replace("_", " ").title(), "GWh",
                          ax, show_segment_labels=True)

    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"Plot saved to {save_path}")
    return fig


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    model_a = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODEL_A
    model_b = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_MODEL_B

    print(f"Loading {model_a} ...")
    r_a = load_results(model_a)
    print(f"Loading {model_b} ...")
    r_b = load_results(model_b)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = FIGURES_DIR / f"{timestamp}_{model_a}_{model_b}"
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"Comparing year {YEAR} across Europe ...")
    print(f"Saving figures to {run_dir}\n")

    # --- Emissions ---
    em_carrier_a = get_emissions_by_carrier(r_a)
    em_carrier_b = get_emissions_by_carrier(r_b)
    em_tech_a = get_emissions_by_technology(r_a)
    em_tech_b = get_emissions_by_technology(r_b)

    # --- Costs ---
    capex_a = get_capex_by_technology(r_a)
    capex_b = get_capex_by_technology(r_b)
    df_capex = build_comparison_df(capex_a, capex_b, model_a, model_b)
    opex_a = get_opex_by_technology(r_a)
    opex_b = get_opex_by_technology(r_b)
    df_opex = build_comparison_df(opex_a, opex_b, model_a, model_b)

    df_capex_ind = build_comparison_df(
        filter_techs(capex_a, INDUSTRY_PROCESS_TECHS),
        filter_techs(capex_b, INDUSTRY_PROCESS_TECHS), model_a, model_b)
    df_opex_ind = build_comparison_df(
        filter_techs(opex_a, INDUSTRY_PROCESS_TECHS),
        filter_techs(opex_b, INDUSTRY_PROCESS_TECHS), model_a, model_b)

    df_capex_heat = build_comparison_df(
        filter_techs(capex_a, INDUSTRY_HEATING_TECHS),
        filter_techs(capex_b, INDUSTRY_HEATING_TECHS), model_a, model_b)
    df_opex_heat = build_comparison_df(
        filter_techs(opex_a, INDUSTRY_HEATING_TECHS),
        filter_techs(opex_b, INDUSTRY_HEATING_TECHS), model_a, model_b)

    # --- Print summary ---
    annual_em_a = r_a.get_total("carbon_emissions_annual")[YEAR]
    annual_em_b = r_b.get_total("carbon_emissions_annual")[YEAR]
    capex_total_a = r_a.get_total("cost_capex_yearly_total")[YEAR]
    capex_total_b = r_b.get_total("cost_capex_yearly_total")[YEAR]
    opex_total_a = r_a.get_total("cost_opex_yearly_total")[YEAR]
    opex_total_b = r_b.get_total("cost_opex_yearly_total")[YEAR]

    print(f"{'':30s} {model_a:>20s} {model_b:>20s}")
    print("-" * 72)
    print(f"{'Annual emissions (Mton CO2)':30s} {annual_em_a:>20,.1f} {annual_em_b:>20,.1f}")
    print(f"{'Total CAPEX (MEUR)':30s} {capex_total_a:>20,.1f} {capex_total_b:>20,.1f}")
    print(f"{'Total OPEX (MEUR)':30s} {opex_total_a:>20,.1f} {opex_total_b:>20,.1f}")

    # --- Figure 1: Total system emissions ---
    em_all_a = pd.concat([
        em_carrier_a.rename(lambda c: f"{c} (carrier)"),
        em_tech_a.rename(lambda t: f"{t} (tech)"),
    ])
    em_all_b = pd.concat([
        em_carrier_b.rename(lambda c: f"{c} (carrier)"),
        em_tech_b.rename(lambda t: f"{t} (tech)"),
    ])
    df_em_all = build_comparison_df(em_all_a, em_all_b, model_a, model_b)

    fig1, ax1 = plt.subplots(figsize=(8, 8))
    fig1.suptitle(
        f"Total System Emissions: {model_a} vs {model_b}  (Year {YEAR})",
        fontsize=14, fontweight="bold",
    )
    plot_stacked_bars(df_em_all, "", "Mton CO2eq", ax1, show_segment_labels=True)
    fig1.tight_layout(rect=[0, 0, 1, 0.95])
    fig1.savefig(run_dir / f"emissions_{model_a}_vs_{model_b}.png",
                 dpi=150, bbox_inches="tight")
    print(f"\nEmissions plot saved")

    # --- Figure 2: Total system costs ---
    plot_cost_figure(
        df_capex, df_opex,
        f"Total System Costs: {model_a} vs {model_b}  (Year {YEAR})",
        run_dir / f"costs_total_{model_a}_vs_{model_b}.png",
    )

    # --- Figure 3: Industry process costs ---
    plot_cost_figure(
        df_capex_ind, df_opex_ind,
        f"Industry Process Costs: {model_a} vs {model_b}  (Year {YEAR})",
        run_dir / f"costs_industry_{model_a}_vs_{model_b}.png",
        show_segment_labels=True,
    )

    # --- Figure 4: Heating costs (industry heating + heat + district heat) ---
    df_capex_ht = build_comparison_df(
        filter_techs(capex_a, HEAT_TECHS),
        filter_techs(capex_b, HEAT_TECHS), model_a, model_b)
    df_opex_ht = build_comparison_df(
        filter_techs(opex_a, HEAT_TECHS),
        filter_techs(opex_b, HEAT_TECHS), model_a, model_b)
    df_capex_dh = build_comparison_df(
        filter_techs(capex_a, DISTRICT_HEAT_TECHS),
        filter_techs(capex_b, DISTRICT_HEAT_TECHS), model_a, model_b)
    df_opex_dh = build_comparison_df(
        filter_techs(opex_a, DISTRICT_HEAT_TECHS),
        filter_techs(opex_b, DISTRICT_HEAT_TECHS), model_a, model_b)

    heating_groups = [
        ("Heat", df_capex_ht, df_opex_ht),
        ("District Heat", df_capex_dh, df_opex_dh),
        ("Industry Heating", df_capex_heat, df_opex_heat),
    ]
    fig4, axes4 = plt.subplots(2, 3, figsize=(20, 10))
    fig4.suptitle(
        f"Heating Costs: {model_a} vs {model_b}  (Year {YEAR})",
        fontsize=14, fontweight="bold",
    )
    for col, (label, df_cx, df_ox) in enumerate(heating_groups):
        plot_stacked_bars(df_cx, f"{label} — CAPEX", "MEUR",
                          axes4[0, col], show_segment_labels=True)
        plot_stacked_bars(df_ox, f"{label} — OPEX", "MEUR",
                          axes4[1, col], show_segment_labels=True)
    fig4.tight_layout(rect=[0, 0, 1, 0.95])
    heat_path = run_dir / f"costs_heating_{model_a}_vs_{model_b}.png"
    fig4.savefig(heat_path, dpi=150, bbox_inches="tight")
    print(f"Plot saved to {heat_path}")

    # --- Figure 5: Fuel consumption shift ---
    plot_fuel_consumption(
        r_a, r_b, model_a, model_b,
        ["natural_gas", "hard_coal", "lng", "waste"],
        run_dir / f"fuel_consumption_{model_a}_vs_{model_b}.png",
    )

    # --- Figure 6: Natural gas supply vs consumption ---
    ng_supply_a = get_fuel_supply(r_a, "natural_gas")
    ng_supply_b = get_fuel_supply(r_b, "natural_gas")
    df_ng_supply = build_comparison_df(ng_supply_a, ng_supply_b, model_a, model_b)

    ng_cons_a = get_fuel_consumption(r_a, "natural_gas")
    ng_cons_b = get_fuel_consumption(r_b, "natural_gas")
    df_ng_cons = build_comparison_df(ng_cons_a, ng_cons_b, model_a, model_b)

    fig6, axes6 = plt.subplots(1, 2, figsize=(14, 7))
    fig6.suptitle(
        f"Natural Gas Balance: {model_a} vs {model_b}  (Year {YEAR})",
        fontsize=14, fontweight="bold",
    )
    plot_stacked_bars(df_ng_supply, "Supply (imports + conversion)", "GWh",
                      axes6[0], show_segment_labels=True)
    plot_stacked_bars(df_ng_cons, "Consumption by Technology", "GWh",
                      axes6[1], show_segment_labels=True)
    fig6.tight_layout(rect=[0, 0, 1, 0.93])
    fig6.savefig(run_dir / f"natural_gas_balance_{model_a}_vs_{model_b}.png",
                 dpi=150, bbox_inches="tight")
    print(f"Plot saved to {run_dir / 'natural_gas_balance_...'}")

    plt.show()


if __name__ == "__main__":
    main()
