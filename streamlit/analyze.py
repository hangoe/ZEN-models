"""Single-model analysis figure functions for the Streamlit dashboard.

Each function takes a zen_garden Results object and returns a matplotlib Figure.
Figure sizes and styles are tuned for full-width Streamlit display.
"""

import matplotlib.pyplot as plt
import pandas as pd
from zen_garden import Results

from utils import HOURS_PER_YEAR, add_price_line, plot_stacked_bars_years

INDUSTRY_HEAT_CARRIERS_ENERGY = [
    "heat_industry_0_100",
    "heat_industry_100_150",
    "heat_industry_150_200",
]

INDUSTRY_HEAT_CARRIERS_PRODUCT = [
    "glass",
    "ceramic",
    "paper",
    "food",
]

INDUSTRY_HEAT_TECHS_BOILERS_HP = [
    # New models (v4_6+): split by temperature + source
    "heat_pump_industry_0_100_waste_heat",
    "heat_pump_industry_0_100_water",
    "heat_pump_industry_100_150_waste_heat",
    "heat_pump_industry_100_150_water",
    "heat_pump_industry_150_200_waste_heat",
    "heat_pump_industry_150_200_water",
    # Intermediate models (v3_0, v4_0-v4_4): split by temperature only
    "heat_pump_industry_0_100",
    "heat_pump_industry_100_150",
    "heat_pump_industry_150_200",
    # Older models (v2_0): single generic industry HP
    "heat_pump_industry",
    # Boilers (consistent across models)
    "biomass_boiler_industry",
    "electrode_boiler_industry",
    "natural_gas_boiler_industry",
    # Very old models (v1_0): "industrial_" prefix naming
    "industrial_biomass_boiler",
    "industrial_coal_boiler",
    "industrial_electrode_boiler",
    "industrial_natural_gas_boiler",
    "industrial_oil_boiler",
]

INDUSTRY_HEAT_TECHS_TEMP_CONV = [
    "heat_industry_temp_conversion_150",
    "heat_industry_temp_conversion_100",
]

INDUSTRY_HEAT_TECHS_PRODUCTION = [
    "glass_production",
    "ceramic_production",
    "paper_production",
    "food_production",
]

INDUSTRY_TES_TECHS = [
    "industry_TES_water_0_100",
    "industry_TES_water_100_150",
    "industry_TES_steam_100_150",
    "industry_TES_steam_150_200",
]

INDUSTRY_DSM_TECHS = [
    "ammonia_DSM",
    "ceramic_DSM",
    "clinker_DSM",
    "food_DSM",
    "glass_DSM",
    "methanol_DSM",
    "olefin_DSM",
    "paper_DSM",
    "primary_steel_DSM",
    "secondary_steel_DSM",
]


# ── Data helpers ──────────────────────────────────────────────────────────────

def get_carrier_production(r: Results, carrier: str) -> pd.DataFrame:
    flow_out = r.get_total("flow_conversion_output")
    if carrier not in flow_out.index.get_level_values("carrier"):
        return pd.DataFrame()
    df = flow_out.xs(carrier, level="carrier").groupby("technology").sum()
    return df[(df.abs() > 1e-3).any(axis=1)]


def get_carrier_consumption(r: Results, carrier: str) -> pd.DataFrame:
    flow_in = r.get_total("flow_conversion_input")
    if carrier not in flow_in.index.get_level_values("carrier"):
        return pd.DataFrame()
    df = flow_in.xs(carrier, level="carrier").groupby("technology").sum()
    return df[(df.abs() > 1e-3).any(axis=1)]


def get_capacity_addition(
    r: Results, techs: list[str], capacity_type: str = "power"
) -> pd.DataFrame:
    cap_add = r.get_total("capacity_addition")
    cap_add = cap_add[cap_add.index.get_level_values("capacity_type") == capacity_type]
    rows = {}
    for tech in techs:
        if tech in cap_add.index.get_level_values("technology"):
            s = cap_add.xs(tech, level="technology").sum()
            if (s.abs() > 1e-6).any():
                rows[tech] = s
    return pd.DataFrame(rows).T if rows else pd.DataFrame()


def get_capacity(
    r: Results, techs: list[str], capacity_type: str = "power"
) -> pd.DataFrame:
    cap = r.get_total("capacity")
    cap = cap[cap.index.get_level_values("capacity_type") == capacity_type]
    rows = {}
    for tech in techs:
        if tech in cap.index.get_level_values("technology"):
            s = cap.xs(tech, level="technology").sum()
            if (s.abs() > 1e-6).any():
                rows[tech] = s
    return pd.DataFrame(rows).T if rows else pd.DataFrame()


def get_heat_demand_by_sector(r: Results, tech: str) -> pd.DataFrame:
    flow_in = r.get_total("flow_conversion_input")
    rows = {}
    for carrier in INDUSTRY_HEAT_CARRIERS_ENERGY:
        if carrier not in flow_in.index.get_level_values("carrier"):
            continue
        sub = flow_in.xs(carrier, level="carrier")
        if tech not in sub.index.get_level_values("technology"):
            continue
        s = sub.xs(tech, level="technology").sum()
        if (s.abs() > 1e-3).any():
            rows[carrier] = s
    return pd.DataFrame(rows).T if rows else pd.DataFrame()


def get_storage_flows(r: Results, techs: list[str], flow_type: str) -> pd.DataFrame:
    try:
        df = r.get_total(flow_type)
        if df.empty or "technology" not in df.index.names:
            return pd.DataFrame()
        rows = {}
        for tech in techs:
            if tech in df.index.get_level_values("technology"):
                s = df.xs(tech, level="technology").sum()
                if (s.abs() > 1e-3).any():
                    rows[tech] = s
        return pd.DataFrame(rows).T if rows else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def get_import_price_eur_per_mwh(r: Results, carrier: str) -> pd.Series:
    pi = r.get_total("price_import")
    if carrier not in pi.index.get_level_values("carrier"):
        return pd.Series(dtype=float)
    return pi.xs(carrier, level="carrier").mean() / HOURS_PER_YEAR * 1000


# ── Figure functions ──────────────────────────────────────────────────────────

def fig_carrier_energy_all(r: Results) -> plt.Figure:
    """3 rows × 2 cols: production & consumption for all 3 temperature levels."""
    n = len(INDUSTRY_HEAT_CARRIERS_ENERGY)
    fig, axes = plt.subplots(n, 2, figsize=(16, 5 * n))
    fig.suptitle("Industry Heat Carriers — Production & Consumption",
                 fontsize=13, fontweight="bold")
    for row, carrier in enumerate(INDUSTRY_HEAT_CARRIERS_ENERGY):
        label = carrier.replace("_", " ").title()
        prod = get_carrier_production(r, carrier)
        cons = get_carrier_consumption(r, carrier)
        if not cons.empty:
            end_use = [t for t in cons.index if t not in INDUSTRY_HEAT_TECHS_TEMP_CONV]
            conv = [t for t in cons.index if t in INDUSTRY_HEAT_TECHS_TEMP_CONV]
            cons = cons.loc[end_use + conv]
        plot_stacked_bars_years(prod, f"{label} — Production", "GWh", axes[row, 0])
        plot_stacked_bars_years(cons, f"{label} — Consumption", "GWh", axes[row, 1])
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    return fig


def fig_carrier_products_production(r: Results) -> plt.Figure:
    """2×2 grid: annual production for glass, ceramic, paper, food."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle("Industry Product Carriers — Annual Production",
                 fontsize=13, fontweight="bold")
    for ax, carrier in zip(axes.flat, INDUSTRY_HEAT_CARRIERS_PRODUCT):
        prod = get_carrier_production(r, carrier)
        plot_stacked_bars_years(prod, carrier.title(), "GWh-eq", ax)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


def fig_boiler_hp_production(r: Results) -> plt.Figure:
    """1×3: boiler & HP output per temperature level with NG price overlay."""
    ng_price = get_import_price_eur_per_mwh(r, "natural_gas")
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle("Industry Heat — Boiler & HP Production (excl. temp conversion)\n"
                 "Right axis: natural gas import price [EUR/MWh]",
                 fontsize=12, fontweight="bold")
    for ax, carrier in zip(axes, INDUSTRY_HEAT_CARRIERS_ENERGY):
        prod = get_carrier_production(r, carrier)
        if not prod.empty:
            prod = prod[prod.index.isin(INDUSTRY_HEAT_TECHS_BOILERS_HP)]
            prod = prod[(prod.abs() > 1e-3).any(axis=1)]
        label = carrier.replace("_", " ").title()
        plot_stacked_bars_years(prod, label, "GWh", ax)
        add_price_line(ax, ng_price, "NG import [EUR/MWh]", "#8b0000")
    fig.tight_layout(rect=[0, 0, 1, 0.90])
    return fig


def fig_capacity_heat_supply(r: Results) -> plt.Figure:
    """2×2: capacity addition & total for boilers+HPs and temp-conversion."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle("Industry Heat Supply — Capacity Addition & Total",
                 fontsize=13, fontweight="bold")
    plot_stacked_bars_years(get_capacity_addition(r, INDUSTRY_HEAT_TECHS_BOILERS_HP),
                            "Capacity Addition — Boilers & HPs", "GW", axes[0, 0])
    plot_stacked_bars_years(get_capacity_addition(r, INDUSTRY_HEAT_TECHS_TEMP_CONV),
                            "Capacity Addition — Temp Conversion", "GW", axes[0, 1])
    plot_stacked_bars_years(get_capacity(r, INDUSTRY_HEAT_TECHS_BOILERS_HP),
                            "Total Capacity — Boilers & HPs", "GW", axes[1, 0])
    plot_stacked_bars_years(get_capacity(r, INDUSTRY_HEAT_TECHS_TEMP_CONV),
                            "Total Capacity — Temp Conversion", "GW", axes[1, 1])
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    return fig


def fig_capacity_production(r: Results) -> plt.Figure:
    """1×2: capacity addition and total for production techs."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Industry Production Technologies — Capacity",
                 fontsize=13, fontweight="bold")
    plot_stacked_bars_years(get_capacity_addition(r, INDUSTRY_HEAT_TECHS_PRODUCTION),
                            "Capacity Addition", "ton/h", axes[0])
    plot_stacked_bars_years(get_capacity(r, INDUSTRY_HEAT_TECHS_PRODUCTION),
                            "Total Capacity", "ton/h", axes[1])
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return fig


def fig_tes_capacity_addition(r: Results) -> plt.Figure:
    """1×2: TES energy (left) and power (right) capacity addition."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Industry TES — Capacity Addition", fontsize=13, fontweight="bold")
    plot_stacked_bars_years(get_capacity_addition(r, INDUSTRY_TES_TECHS, "energy"),
                            "Energy Capacity Addition", "GWh", axes[0])
    plot_stacked_bars_years(get_capacity_addition(r, INDUSTRY_TES_TECHS, "power"),
                            "Power Capacity Addition", "GW", axes[1])
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return fig


def fig_tes_charge_discharge(r: Results) -> plt.Figure:
    """1×2: TES charge (left) and discharge (right)."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Industry TES — Charge & Discharge", fontsize=13, fontweight="bold")
    plot_stacked_bars_years(get_storage_flows(r, INDUSTRY_TES_TECHS, "flow_storage_charge"),
                            "Charge", "GWh", axes[0])
    plot_stacked_bars_years(get_storage_flows(r, INDUSTRY_TES_TECHS, "flow_storage_discharge"),
                            "Discharge", "GWh", axes[1])
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return fig


def fig_heat_demand_by_sector(r: Results) -> plt.Figure:
    """Heat input by temperature level for all production sectors, first vs last year."""
    sectors = [
        ("glass_production", "Glass"),
        ("ceramic_production", "Ceramic"),
        ("paper_production", "Paper"),
        ("food_production", "Food"),
    ]
    sector_data = {label: get_heat_demand_by_sector(r, tech) for tech, label in sectors}
    non_empty = [df for df in sector_data.values() if not df.empty]

    if not non_empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.suptitle("Industry Sectors — Heat Input by Temperature Level",
                     fontsize=13, fontweight="bold")
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        return fig

    all_years = non_empty[0].columns.tolist()
    year_first, year_last = all_years[0], all_years[-1]
    sector_labels = [s[1] for s in sectors]

    single_year = (year_first == year_last)
    display_years = [year_first] if single_year else [year_first, year_last]
    fig, axes_raw = plt.subplots(1, len(display_years), figsize=(7 * len(display_years), 7),
                                 sharey=not single_year)
    axes = [axes_raw] if single_year else list(axes_raw)

    fig.suptitle("Industry Sectors — Heat Input by Temperature Level",
                 fontsize=13, fontweight="bold")
    for ax, yr in zip(axes, display_years):
        df_yr = pd.DataFrame(
            {lbl: sector_data[lbl][yr]
             for lbl in sector_labels
             if not sector_data[lbl].empty and yr in sector_data[lbl].columns}
        ).fillna(0)
        plot_stacked_bars_years(df_yr, str(yr), "GWh", ax,
                                show_legend=(ax is axes[-1]))
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


def fig_dsm_capacity_addition(r: Results) -> plt.Figure:
    """1×2: DSM energy (left) and power (right) capacity addition."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Industry DSM — Capacity Addition", fontsize=13, fontweight="bold")
    plot_stacked_bars_years(get_capacity_addition(r, INDUSTRY_DSM_TECHS, "energy"),
                            "Energy Capacity Addition", "ktproduct", axes[0])
    plot_stacked_bars_years(get_capacity_addition(r, INDUSTRY_DSM_TECHS, "power"),
                            "Power Capacity Addition", "ktproduct/h", axes[1])
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return fig


def fig_dsm_charge_discharge(r: Results) -> plt.Figure:
    """1×2: DSM charge (left) and discharge (right)."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Industry DSM — Charge & Discharge", fontsize=13, fontweight="bold")
    plot_stacked_bars_years(get_storage_flows(r, INDUSTRY_DSM_TECHS, "flow_storage_charge"),
                            "Charge", "ktproduct", axes[0])
    plot_stacked_bars_years(get_storage_flows(r, INDUSTRY_DSM_TECHS, "flow_storage_discharge"),
                            "Discharge", "ktproduct", axes[1])
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return fig


def fig_storage_comparison(r: Results) -> plt.Figure:
    """1×3: capacity addition comparison across TES, battery, and DSM."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle("Storage Technologies — Capacity Addition", fontsize=13, fontweight="bold")
    plot_stacked_bars_years(
        get_capacity_addition(r, INDUSTRY_TES_TECHS + ["battery"], "energy"),
        "Energy Capacity\nTES + Battery", "GWh", axes[0],
    )
    plot_stacked_bars_years(
        get_capacity_addition(r, INDUSTRY_TES_TECHS + ["battery", "pumped_hydro"], "power"),
        "Power Capacity\nTES + Battery + Pumped Hydro", "GW", axes[1],
    )
    plot_stacked_bars_years(
        get_capacity_addition(r, INDUSTRY_DSM_TECHS, "power"),
        "DSM Power Capacity", "ktproduct/h", axes[2],
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return fig
