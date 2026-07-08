"""Two-model analysis figure functions for the Streamlit dashboard.

Each function takes two zen_garden Results objects (Model A, Model B) and
returns a matplotlib Figure where every metric is rendered as a pair of
adjacent axes — Model A on the left, Model B on the right — so the two
models can be compared without switching tabs. To avoid duplicated legends,
only the Model B axis of each pair shows a legend (see
`plot_stacked_bars_years_pair` in utils.py).
"""

import matplotlib.pyplot as plt
import pandas as pd
from zen_garden import Results

from utils import (
    HOURS_PER_YEAR,
    add_price_line,
    plot_stacked_bars_years,
    plot_stacked_bars_years_pair,
)

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


def _reorder_conversion_last(cons: pd.DataFrame) -> pd.DataFrame:
    """Push temp-conversion techs to the end of the stack order."""
    if cons.empty:
        return cons
    end_use = [t for t in cons.index if t not in INDUSTRY_HEAT_TECHS_TEMP_CONV]
    conv = [t for t in cons.index if t in INDUSTRY_HEAT_TECHS_TEMP_CONV]
    return cons.loc[end_use + conv]


def _filter_boiler_hp(prod: pd.DataFrame) -> pd.DataFrame:
    if prod.empty:
        return prod
    prod = prod[prod.index.isin(INDUSTRY_HEAT_TECHS_BOILERS_HP)]
    return prod[(prod.abs() > 1e-3).any(axis=1)]


# ── Figure functions ──────────────────────────────────────────────────────────
# Every metric is drawn as a pair of adjacent axes (Model A | Model B).

def fig_carrier_energy_all(
    r_a: Results, r_b: Results, name_a: str, name_b: str
) -> plt.Figure:
    """3 rows × 4 cols: production & consumption for all 3 temperature levels, A|B each."""
    n = len(INDUSTRY_HEAT_CARRIERS_ENERGY)
    fig, axes = plt.subplots(n, 4, figsize=(30, 5.5 * n))
    fig.suptitle("Industry Heat Carriers — Production & Consumption",
                 fontsize=13, fontweight="bold")
    for row, carrier in enumerate(INDUSTRY_HEAT_CARRIERS_ENERGY):
        label = carrier.replace("_", " ").title()
        prod_a = get_carrier_production(r_a, carrier)
        prod_b = get_carrier_production(r_b, carrier)
        cons_a = _reorder_conversion_last(get_carrier_consumption(r_a, carrier))
        cons_b = _reorder_conversion_last(get_carrier_consumption(r_b, carrier))
        plot_stacked_bars_years_pair(axes[row, 0], axes[row, 1], prod_a, prod_b,
                                     f"{label} — Production", "GWh", name_a, name_b)
        plot_stacked_bars_years_pair(axes[row, 2], axes[row, 3], cons_a, cons_b,
                                     f"{label} — Consumption", "GWh", name_a, name_b)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    return fig


def fig_carrier_products_production(
    r_a: Results, r_b: Results, name_a: str, name_b: str
) -> plt.Figure:
    """2 rows × 4 cols: annual production for glass, ceramic, paper, food, A|B each."""
    fig, axes = plt.subplots(2, 4, figsize=(26, 10))
    fig.suptitle("Industry Product Carriers — Annual Production",
                 fontsize=13, fontweight="bold")
    for i, carrier in enumerate(INDUSTRY_HEAT_CARRIERS_PRODUCT):
        row, pair = divmod(i, 2)
        col = pair * 2
        prod_a = get_carrier_production(r_a, carrier)
        prod_b = get_carrier_production(r_b, carrier)
        plot_stacked_bars_years_pair(axes[row, col], axes[row, col + 1], prod_a, prod_b,
                                     carrier.title(), "GWh-eq", name_a, name_b)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


def fig_boiler_hp_production(
    r_a: Results, r_b: Results, name_a: str, name_b: str
) -> plt.Figure:
    """1×6: boiler & HP output per temperature level (A|B) with NG price overlay."""
    ng_price_a = get_import_price_eur_per_mwh(r_a, "natural_gas")
    ng_price_b = get_import_price_eur_per_mwh(r_b, "natural_gas")
    fig, axes = plt.subplots(1, 6, figsize=(36, 7))
    fig.suptitle("Industry Heat — Boiler & HP Production (excl. temp conversion)\n"
                 "Right axis: natural gas import price [EUR/MWh]",
                 fontsize=12, fontweight="bold")
    for i, carrier in enumerate(INDUSTRY_HEAT_CARRIERS_ENERGY):
        col = i * 2
        prod_a = _filter_boiler_hp(get_carrier_production(r_a, carrier))
        prod_b = _filter_boiler_hp(get_carrier_production(r_b, carrier))
        label = carrier.replace("_", " ").title()
        plot_stacked_bars_years_pair(axes[col], axes[col + 1], prod_a, prod_b,
                                     label, "GWh", name_a, name_b)
        add_price_line(axes[col], ng_price_a, "NG import [EUR/MWh]", "#8b0000")
        add_price_line(axes[col + 1], ng_price_b, "NG import [EUR/MWh]", "#8b0000")
    fig.tight_layout(rect=[0, 0, 1, 0.90])
    return fig


def fig_capacity_heat_supply(
    r_a: Results, r_b: Results, name_a: str, name_b: str
) -> plt.Figure:
    """2×4: capacity addition & total for boilers+HPs and temp-conversion, A|B each."""
    fig, axes = plt.subplots(2, 4, figsize=(30, 11))
    fig.suptitle("Industry Heat Supply — Capacity Addition & Total",
                 fontsize=13, fontweight="bold")
    plot_stacked_bars_years_pair(
        axes[0, 0], axes[0, 1],
        get_capacity_addition(r_a, INDUSTRY_HEAT_TECHS_BOILERS_HP),
        get_capacity_addition(r_b, INDUSTRY_HEAT_TECHS_BOILERS_HP),
        "Capacity Addition — Boilers & HPs", "GW", name_a, name_b,
    )
    plot_stacked_bars_years_pair(
        axes[0, 2], axes[0, 3],
        get_capacity_addition(r_a, INDUSTRY_HEAT_TECHS_TEMP_CONV),
        get_capacity_addition(r_b, INDUSTRY_HEAT_TECHS_TEMP_CONV),
        "Capacity Addition — Temp Conversion", "GW", name_a, name_b,
    )
    plot_stacked_bars_years_pair(
        axes[1, 0], axes[1, 1],
        get_capacity(r_a, INDUSTRY_HEAT_TECHS_BOILERS_HP),
        get_capacity(r_b, INDUSTRY_HEAT_TECHS_BOILERS_HP),
        "Total Capacity — Boilers & HPs", "GW", name_a, name_b,
    )
    plot_stacked_bars_years_pair(
        axes[1, 2], axes[1, 3],
        get_capacity(r_a, INDUSTRY_HEAT_TECHS_TEMP_CONV),
        get_capacity(r_b, INDUSTRY_HEAT_TECHS_TEMP_CONV),
        "Total Capacity — Temp Conversion", "GW", name_a, name_b,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    return fig


def fig_capacity_production(
    r_a: Results, r_b: Results, name_a: str, name_b: str
) -> plt.Figure:
    """1×4: capacity addition and total for production techs, A|B each."""
    fig, axes = plt.subplots(1, 4, figsize=(28, 6.5))
    fig.suptitle("Industry Production Technologies — Capacity",
                 fontsize=13, fontweight="bold")
    plot_stacked_bars_years_pair(
        axes[0], axes[1],
        get_capacity_addition(r_a, INDUSTRY_HEAT_TECHS_PRODUCTION),
        get_capacity_addition(r_b, INDUSTRY_HEAT_TECHS_PRODUCTION),
        "Capacity Addition", "ton/h", name_a, name_b,
    )
    plot_stacked_bars_years_pair(
        axes[2], axes[3],
        get_capacity(r_a, INDUSTRY_HEAT_TECHS_PRODUCTION),
        get_capacity(r_b, INDUSTRY_HEAT_TECHS_PRODUCTION),
        "Total Capacity", "ton/h", name_a, name_b,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return fig


def fig_tes_capacity_addition(
    r_a: Results, r_b: Results, name_a: str, name_b: str
) -> plt.Figure:
    """1×4: TES energy and power capacity addition, A|B each."""
    fig, axes = plt.subplots(1, 4, figsize=(28, 6.5))
    fig.suptitle("Industry TES — Capacity Addition", fontsize=13, fontweight="bold")
    plot_stacked_bars_years_pair(
        axes[0], axes[1],
        get_capacity_addition(r_a, INDUSTRY_TES_TECHS, "energy"),
        get_capacity_addition(r_b, INDUSTRY_TES_TECHS, "energy"),
        "Energy Capacity Addition", "GWh", name_a, name_b,
    )
    plot_stacked_bars_years_pair(
        axes[2], axes[3],
        get_capacity_addition(r_a, INDUSTRY_TES_TECHS, "power"),
        get_capacity_addition(r_b, INDUSTRY_TES_TECHS, "power"),
        "Power Capacity Addition", "GW", name_a, name_b,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return fig


def fig_tes_charge_discharge(
    r_a: Results, r_b: Results, name_a: str, name_b: str
) -> plt.Figure:
    """1×4: TES charge and discharge, A|B each."""
    fig, axes = plt.subplots(1, 4, figsize=(28, 6.5))
    fig.suptitle("Industry TES — Charge & Discharge", fontsize=13, fontweight="bold")
    plot_stacked_bars_years_pair(
        axes[0], axes[1],
        get_storage_flows(r_a, INDUSTRY_TES_TECHS, "flow_storage_charge"),
        get_storage_flows(r_b, INDUSTRY_TES_TECHS, "flow_storage_charge"),
        "Charge", "GWh", name_a, name_b,
    )
    plot_stacked_bars_years_pair(
        axes[2], axes[3],
        get_storage_flows(r_a, INDUSTRY_TES_TECHS, "flow_storage_discharge"),
        get_storage_flows(r_b, INDUSTRY_TES_TECHS, "flow_storage_discharge"),
        "Discharge", "GWh", name_a, name_b,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return fig


def fig_heat_demand_by_sector(
    r_a: Results, r_b: Results, name_a: str, name_b: str
) -> plt.Figure:
    """Heat input by temperature level for all production sectors, first vs last year, A|B each."""
    sectors = [
        ("glass_production", "Glass"),
        ("ceramic_production", "Ceramic"),
        ("paper_production", "Paper"),
        ("food_production", "Food"),
    ]
    sector_data_a = {label: get_heat_demand_by_sector(r_a, tech) for tech, label in sectors}
    sector_data_b = {label: get_heat_demand_by_sector(r_b, tech) for tech, label in sectors}
    non_empty = [df for data in (sector_data_a, sector_data_b)
                 for df in data.values() if not df.empty]

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

    def build_df(sector_data: dict, yr) -> pd.DataFrame:
        return pd.DataFrame(
            {lbl: sector_data[lbl][yr]
             for lbl in sector_labels
             if not sector_data[lbl].empty and yr in sector_data[lbl].columns}
        ).fillna(0)

    n_years = len(display_years)
    fig, axes = plt.subplots(1, n_years * 2, figsize=(7.5 * n_years * 2, 7.5),
                             sharey=not single_year)
    axes = list(axes)

    fig.suptitle("Industry Sectors — Heat Input by Temperature Level",
                 fontsize=13, fontweight="bold")
    for i, yr in enumerate(display_years):
        plot_stacked_bars_years_pair(
            axes[2 * i], axes[2 * i + 1],
            build_df(sector_data_a, yr), build_df(sector_data_b, yr),
            str(yr), "GWh", name_a, name_b,
        )
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


def fig_dsm_capacity_addition(
    r_a: Results, r_b: Results, name_a: str, name_b: str
) -> plt.Figure:
    """1×4: DSM energy and power capacity addition, A|B each."""
    fig, axes = plt.subplots(1, 4, figsize=(28, 6.5))
    fig.suptitle("Industry DSM — Capacity Addition", fontsize=13, fontweight="bold")
    plot_stacked_bars_years_pair(
        axes[0], axes[1],
        get_capacity_addition(r_a, INDUSTRY_DSM_TECHS, "energy"),
        get_capacity_addition(r_b, INDUSTRY_DSM_TECHS, "energy"),
        "Energy Capacity Addition", "ktproduct", name_a, name_b,
    )
    plot_stacked_bars_years_pair(
        axes[2], axes[3],
        get_capacity_addition(r_a, INDUSTRY_DSM_TECHS, "power"),
        get_capacity_addition(r_b, INDUSTRY_DSM_TECHS, "power"),
        "Power Capacity Addition", "ktproduct/h", name_a, name_b,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return fig


def fig_dsm_charge_discharge(
    r_a: Results, r_b: Results, name_a: str, name_b: str
) -> plt.Figure:
    """1×4: DSM charge and discharge, A|B each."""
    fig, axes = plt.subplots(1, 4, figsize=(28, 6.5))
    fig.suptitle("Industry DSM — Charge & Discharge", fontsize=13, fontweight="bold")
    plot_stacked_bars_years_pair(
        axes[0], axes[1],
        get_storage_flows(r_a, INDUSTRY_DSM_TECHS, "flow_storage_charge"),
        get_storage_flows(r_b, INDUSTRY_DSM_TECHS, "flow_storage_charge"),
        "Charge", "ktproduct", name_a, name_b,
    )
    plot_stacked_bars_years_pair(
        axes[2], axes[3],
        get_storage_flows(r_a, INDUSTRY_DSM_TECHS, "flow_storage_discharge"),
        get_storage_flows(r_b, INDUSTRY_DSM_TECHS, "flow_storage_discharge"),
        "Discharge", "ktproduct", name_a, name_b,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return fig


def fig_storage_comparison(
    r_a: Results, r_b: Results, name_a: str, name_b: str
) -> plt.Figure:
    """1×6: capacity addition comparison across TES, battery, and DSM, A|B each."""
    fig, axes = plt.subplots(1, 6, figsize=(40, 7))
    fig.suptitle("Storage Technologies — Capacity Addition", fontsize=13, fontweight="bold")
    plot_stacked_bars_years_pair(
        axes[0], axes[1],
        get_capacity_addition(r_a, INDUSTRY_TES_TECHS + ["battery"], "energy"),
        get_capacity_addition(r_b, INDUSTRY_TES_TECHS + ["battery"], "energy"),
        "Energy Capacity\nTES + Battery", "GWh", name_a, name_b,
    )
    plot_stacked_bars_years_pair(
        axes[2], axes[3],
        get_capacity_addition(r_a, INDUSTRY_TES_TECHS + ["battery", "pumped_hydro"], "power"),
        get_capacity_addition(r_b, INDUSTRY_TES_TECHS + ["battery", "pumped_hydro"], "power"),
        "Power Capacity\nTES + Battery + Pumped Hydro", "GW", name_a, name_b,
    )
    plot_stacked_bars_years_pair(
        axes[4], axes[5],
        get_capacity_addition(r_a, INDUSTRY_DSM_TECHS, "power"),
        get_capacity_addition(r_b, INDUSTRY_DSM_TECHS, "power"),
        "DSM Power Capacity", "ktproduct/h", name_a, name_b,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return fig
