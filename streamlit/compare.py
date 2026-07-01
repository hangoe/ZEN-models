"""Two-model comparison figure functions for the Streamlit dashboard.

Each figure function takes two Results objects, short display names, and a year,
and returns a matplotlib Figure. The year parameter replaces the fixed YEAR=2025
constant so multi-timestep models are fully supported.
"""

import matplotlib.pyplot as plt
import pandas as pd
from zen_garden import Results

from utils import plot_stacked_bars

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
    "biomass_boiler_DH", "oil_boiler_DH", "heat_pump_DH", "electrode_boiler_DH",
]


# ── Data helpers ──────────────────────────────────────────────────────────────

def _slice_year(df: pd.DataFrame, year: int) -> pd.Series:
    """Safely extract one year from a grouped DataFrame."""
    if df.empty or year not in df.columns:
        return pd.Series(dtype=float)
    return df[year]


def build_comparison_df(
    series_a: pd.Series, series_b: pd.Series, name_a: str, name_b: str
) -> pd.DataFrame:
    combined = pd.DataFrame({name_a: series_a, name_b: series_b}).fillna(0)
    return combined.sort_values(name_a, ascending=True)


def filter_techs(series: pd.Series, tech_list: list[str]) -> pd.Series:
    present = [t for t in tech_list if t in series.index]
    filtered = series.loc[present]
    return filtered[filtered.abs() > 1e-6].sort_values(ascending=False)


def get_emissions_by_carrier(r: Results, year: int) -> pd.Series:
    df = r.get_total("carbon_emissions_carrier")
    s = _slice_year(df.groupby("carrier").sum(), year)
    return s[s.abs() > 1e-6].sort_values(ascending=False)


def get_emissions_by_technology(r: Results, year: int) -> pd.Series:
    df = r.get_total("carbon_emissions_technology")
    s = _slice_year(df.groupby("technology").sum(), year)
    return s[s.abs() > 1e-6].sort_values(ascending=False)


def get_capex_by_technology(r: Results, year: int) -> pd.Series:
    df = r.get_total("cost_capex_yearly")
    s = _slice_year(df.groupby("technology").sum(), year)
    return s[s.abs() > 1e-6].sort_values(ascending=False)


def get_opex_by_technology(r: Results, year: int) -> pd.Series:
    df = r.get_total("cost_opex_yearly")
    s = _slice_year(df.groupby("technology").sum(), year)
    return s[s.abs() > 1e-6].sort_values(ascending=False)


def get_fuel_consumption(r: Results, carrier: str, year: int) -> pd.Series:
    flow_in = r.get_total("flow_conversion_input")
    if carrier not in flow_in.index.get_level_values("carrier"):
        return pd.Series(dtype=float)
    s = _slice_year(flow_in.xs(carrier, level="carrier").groupby("technology").sum(), year)
    return s[s.abs() > 1e-3].sort_values(ascending=False)


def get_fuel_supply(r: Results, carrier: str, year: int) -> pd.Series:
    pieces: dict[str, float] = {}
    imp = r.get_total("flow_import")
    if carrier in imp.index.get_level_values("carrier"):
        summed = imp.xs(carrier, level="carrier").sum()
        val = float(summed.get(year, 0)) if hasattr(summed, "get") else 0.0
        if abs(val) > 1e-3:
            pieces[f"{carrier} import"] = val
    flow_out = r.get_total("flow_conversion_output")
    if carrier in flow_out.index.get_level_values("carrier"):
        by_tech = _slice_year(
            flow_out.xs(carrier, level="carrier").groupby("technology").sum(), year
        )
        for tech, val in by_tech.items():
            if abs(float(val)) > 1e-3:
                pieces[tech] = float(val)
    return pd.Series(pieces).sort_values(ascending=False)


def get_summary_metrics(r_a: Results, r_b: Results, year: int) -> dict:
    """Return key scalar metrics for display in Streamlit."""
    def _safe(r: Results, var: str) -> float | None:
        try:
            data = r.get_total(var)
            val = data.get(year) if hasattr(data, "get") else data[year]
            return float(val) if val is not None else None
        except Exception:
            return None

    return {
        "em_a": _safe(r_a, "carbon_emissions_annual"),
        "em_b": _safe(r_b, "carbon_emissions_annual"),
        "capex_a": _safe(r_a, "cost_capex_yearly_total"),
        "capex_b": _safe(r_b, "cost_capex_yearly_total"),
        "opex_a": _safe(r_a, "cost_opex_yearly_total"),
        "opex_b": _safe(r_b, "cost_opex_yearly_total"),
    }


# ── Internal plotting helper ──────────────────────────────────────────────────

def _cost_panel(df_capex: pd.DataFrame, df_opex: pd.DataFrame,
                title: str) -> plt.Figure:
    """1×2 figure with CAPEX and OPEX, shared right-side legend."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(title, fontsize=13, fontweight="bold")
    plot_stacked_bars(df_capex, "CAPEX by Technology", "MEUR", axes[0],
                      show_legend=True, show_segment_labels=False)
    plot_stacked_bars(df_opex, "OPEX by Technology", "MEUR", axes[1],
                      show_legend=True, show_segment_labels=False)
    fig.tight_layout()
    return fig


# ── Figure functions ──────────────────────────────────────────────────────────

def fig_emissions(
    r_a: Results, r_b: Results, name_a: str, name_b: str, year: int
) -> plt.Figure:
    """Total system emissions: carriers + technologies, A vs B."""
    em_carrier_a = get_emissions_by_carrier(r_a, year)
    em_carrier_b = get_emissions_by_carrier(r_b, year)
    em_tech_a = get_emissions_by_technology(r_a, year)
    em_tech_b = get_emissions_by_technology(r_b, year)

    em_all_a = pd.concat([
        em_carrier_a.rename(lambda c: f"{c} (carrier)"),
        em_tech_a.rename(lambda t: f"{t} (tech)"),
    ])
    em_all_b = pd.concat([
        em_carrier_b.rename(lambda c: f"{c} (carrier)"),
        em_tech_b.rename(lambda t: f"{t} (tech)"),
    ])
    df = build_comparison_df(em_all_a, em_all_b, name_a, name_b)

    fig, ax = plt.subplots(figsize=(9, 8))
    fig.suptitle(f"Total System Emissions — Year {year}", fontsize=13, fontweight="bold")
    plot_stacked_bars(df, "", "Mton CO₂eq", ax, show_segment_labels=True)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


def fig_costs_total(
    r_a: Results, r_b: Results, name_a: str, name_b: str, year: int
) -> plt.Figure:
    """Total system CAPEX & OPEX, A vs B."""
    capex_a = get_capex_by_technology(r_a, year)
    capex_b = get_capex_by_technology(r_b, year)
    opex_a = get_opex_by_technology(r_a, year)
    opex_b = get_opex_by_technology(r_b, year)
    df_capex = build_comparison_df(capex_a, capex_b, name_a, name_b)
    df_opex = build_comparison_df(opex_a, opex_b, name_a, name_b)
    return _cost_panel(df_capex, df_opex, f"Total System Costs — Year {year}")


def fig_costs_industry(
    r_a: Results, r_b: Results, name_a: str, name_b: str, year: int
) -> plt.Figure:
    """Industry process CAPEX & OPEX, A vs B."""
    capex_a = get_capex_by_technology(r_a, year)
    capex_b = get_capex_by_technology(r_b, year)
    opex_a = get_opex_by_technology(r_a, year)
    opex_b = get_opex_by_technology(r_b, year)
    df_capex = build_comparison_df(
        filter_techs(capex_a, INDUSTRY_PROCESS_TECHS),
        filter_techs(capex_b, INDUSTRY_PROCESS_TECHS),
        name_a, name_b,
    )
    df_opex = build_comparison_df(
        filter_techs(opex_a, INDUSTRY_PROCESS_TECHS),
        filter_techs(opex_b, INDUSTRY_PROCESS_TECHS),
        name_a, name_b,
    )
    return _cost_panel(df_capex, df_opex,
                       f"Industry Process Costs — Year {year}")


def fig_costs_heating(
    r_a: Results, r_b: Results, name_a: str, name_b: str, year: int
) -> plt.Figure:
    """Heating CAPEX & OPEX split into 3 groups (heat / district heat / industry heating)."""
    capex_a = get_capex_by_technology(r_a, year)
    capex_b = get_capex_by_technology(r_b, year)
    opex_a = get_opex_by_technology(r_a, year)
    opex_b = get_opex_by_technology(r_b, year)

    groups = [
        ("Heat", HEAT_TECHS),
        ("District Heat", DISTRICT_HEAT_TECHS),
        ("Industry Heating", INDUSTRY_HEATING_TECHS),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(20, 10))
    fig.suptitle(f"Heating Costs — Year {year}", fontsize=13, fontweight="bold")

    for col, (label, techs) in enumerate(groups):
        df_cx = build_comparison_df(filter_techs(capex_a, techs),
                                    filter_techs(capex_b, techs), name_a, name_b)
        df_ox = build_comparison_df(filter_techs(opex_a, techs),
                                    filter_techs(opex_b, techs), name_a, name_b)
        plot_stacked_bars(df_cx, f"{label} — CAPEX", "MEUR",
                          axes[0, col], show_segment_labels=True)
        plot_stacked_bars(df_ox, f"{label} — OPEX", "MEUR",
                          axes[1, col], show_segment_labels=True)

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


def fig_fuel_consumption(
    r_a: Results, r_b: Results, name_a: str, name_b: str, year: int
) -> plt.Figure:
    """Fuel consumption breakdown for natural_gas, hard_coal, lng, waste."""
    carriers = ["natural_gas", "hard_coal", "lng", "waste"]
    fig, axes = plt.subplots(1, len(carriers), figsize=(6 * len(carriers), 7))
    fig.suptitle(f"Fuel Consumption by Technology — Year {year}",
                 fontsize=13, fontweight="bold")
    for ax, carrier in zip(axes, carriers):
        fa = get_fuel_consumption(r_a, carrier, year)
        fb = get_fuel_consumption(r_b, carrier, year)
        df = build_comparison_df(fa, fb, name_a, name_b)
        plot_stacked_bars(df, carrier.replace("_", " ").title(), "GWh",
                          ax, show_segment_labels=True)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return fig


def fig_natural_gas_balance(
    r_a: Results, r_b: Results, name_a: str, name_b: str, year: int
) -> plt.Figure:
    """Natural gas supply sources vs consumption by technology."""
    ng_supply_a = get_fuel_supply(r_a, "natural_gas", year)
    ng_supply_b = get_fuel_supply(r_b, "natural_gas", year)
    ng_cons_a = get_fuel_consumption(r_a, "natural_gas", year)
    ng_cons_b = get_fuel_consumption(r_b, "natural_gas", year)

    df_supply = build_comparison_df(ng_supply_a, ng_supply_b, name_a, name_b)
    df_cons = build_comparison_df(ng_cons_a, ng_cons_b, name_a, name_b)

    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    fig.suptitle(f"Natural Gas Balance — Year {year}", fontsize=13, fontweight="bold")
    plot_stacked_bars(df_supply, "Supply (imports + conversion)", "GWh",
                      axes[0], show_segment_labels=True)
    plot_stacked_bars(df_cons, "Consumption by Technology", "GWh",
                      axes[1], show_segment_labels=True)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return fig
