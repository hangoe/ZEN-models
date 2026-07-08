"""Two-model comparison figure functions for the Streamlit dashboard.

Data helpers use xs-per-entity instead of groupby().sum()[year] because
zen_garden's get_total() may return years as index levels (not columns)
depending on the variable and model type. The xs+sum approach works for
both 1ts and multi-timestep models.
"""

import matplotlib.pyplot as plt
import pandas as pd
from zen_garden import Results

from utils import get_available_years, plot_stacked_bars

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

INDUSTRY_PROCESS_TECHS = [
    "cement_kiln", "cement_post_comb", "biomass_to_cement_fuel",
    "coal_to_cement_fuel", "hydrogen_to_cement_fuel", "waste_to_cement_fuel",
    "BF_BOF", "BF_BOF_CCS", "EAF", "NG_DRI", "NG_DRI_CCS", "H2_DRI",
    "glass_production", "ceramic_production", "paper_production", "food_production",
]

INDUSTRY_HEATING_TECHS = [
    # Boilers (consistent across models)
    "natural_gas_boiler_industry", "electrode_boiler_industry", "biomass_boiler_industry",
    # New models (v4_6+): split by temperature + source
    "heat_pump_industry_0_100_waste_heat", "heat_pump_industry_0_100_water",
    "heat_pump_industry_100_150_waste_heat", "heat_pump_industry_100_150_water",
    "heat_pump_industry_150_200_waste_heat", "heat_pump_industry_150_200_water",
    # Intermediate models (v3_0, v4_0-v4_4): split by temperature only
    "heat_pump_industry_0_100", "heat_pump_industry_100_150", "heat_pump_industry_150_200",
    # Older models (v2_0): single generic industry HP
    "heat_pump_industry",
    # Very old models (v1_0): "industrial_" prefix naming
    "industrial_biomass_boiler", "industrial_coal_boiler",
    "industrial_electrode_boiler", "industrial_natural_gas_boiler", "industrial_oil_boiler",
]

HEAT_TECHS = [
    "natural_gas_boiler", "biomass_boiler", "heat_pump",
    "electrode_boiler", "oil_boiler", "district_heating_grid",
]

DISTRICT_HEAT_TECHS = [
    "natural_gas_boiler_DH", "hard_coal_boiler_DH", "waste_boiler_DH",
    "biomass_boiler_DH", "oil_boiler_DH", "heat_pump_DH", "electrode_boiler_DH",
]


# ── Core data access helpers ──────────────────────────────────────────────────

def _xs_get_year(df: pd.DataFrame, level: str, value: str, year: int) -> float:
    """XS-select `value` from `level`, sum all remaining dims, return value for `year`."""
    try:
        s = df.xs(value, level=level).sum()
        if isinstance(s, pd.Series):
            for key in [year, str(year)]:
                if key in s.index:
                    return float(s[key])
            # Try coercing index to int
            try:
                int_idx = {int(k): v for k, v in s.items()}
                return float(int_idx.get(year, 0.0))
            except (TypeError, ValueError):
                pass
        elif isinstance(s, (int, float)):
            return float(s)
    except Exception:
        pass
    return 0.0


def _series_from_level(df: pd.DataFrame, level: str, year: int, threshold: float = 1e-6) -> pd.Series:
    """Build a Series {entity: value_at_year} by xs-ing each unique entity in `level`."""
    try:
        if level not in df.index.names:
            return pd.Series(dtype=float)
        entities = df.index.get_level_values(level).unique()
        results = {e: _xs_get_year(df, level, e, year) for e in entities}
        s = pd.Series({k: v for k, v in results.items() if abs(v) > threshold})
        return s.sort_values(ascending=False)
    except Exception:
        return pd.Series(dtype=float)


def _get_annual_scalar(r: Results, variable: str, year: int) -> float | None:
    """Safely extract a scalar annual metric for a given year."""
    try:
        data = r.get_total(variable)
        if isinstance(data, pd.Series):
            for key in [year, str(year)]:
                if key in data.index:
                    return float(data[key])
            try:
                int_idx = {int(k): v for k, v in data.items()}
                return float(int_idx[year])
            except (KeyError, TypeError, ValueError):
                pass
        elif isinstance(data, pd.DataFrame):
            if year in data.columns:
                return float(data[year].sum())
            elif year in data.index:
                return float(data.loc[year].sum())
    except Exception:
        pass
    return None


# ── Data helpers ──────────────────────────────────────────────────────────────

def get_emissions_by_carrier(r: Results, year: int) -> pd.Series:
    try:
        return _series_from_level(r.get_total("carbon_emissions_carrier"), "carrier", year)
    except Exception:
        return pd.Series(dtype=float)


def get_emissions_by_technology(r: Results, year: int) -> pd.Series:
    try:
        return _series_from_level(r.get_total("carbon_emissions_technology"), "technology", year)
    except Exception:
        return pd.Series(dtype=float)


def get_capex_by_technology(r: Results, year: int) -> pd.Series:
    try:
        return _series_from_level(r.get_total("cost_capex_yearly"), "technology", year)
    except Exception:
        return pd.Series(dtype=float)


def get_opex_by_technology(r: Results, year: int) -> pd.Series:
    try:
        return _series_from_level(r.get_total("cost_opex_yearly"), "technology", year)
    except Exception:
        return pd.Series(dtype=float)


def get_fuel_consumption(r: Results, carrier: str, year: int) -> pd.Series:
    try:
        flow_in = r.get_total("flow_conversion_input")
        if "carrier" not in flow_in.index.names:
            return pd.Series(dtype=float)
        if carrier not in flow_in.index.get_level_values("carrier"):
            return pd.Series(dtype=float)
        sub = flow_in.xs(carrier, level="carrier")
        return _series_from_level(sub, "technology", year, threshold=1e-3)
    except Exception:
        return pd.Series(dtype=float)


def get_fuel_supply(r: Results, carrier: str, year: int) -> pd.Series:
    pieces: dict[str, float] = {}
    try:
        imp = r.get_total("flow_import")
        if "carrier" in imp.index.names and carrier in imp.index.get_level_values("carrier"):
            val = _xs_get_year(imp, "carrier", carrier, year)
            if abs(val) > 1e-3:
                pieces[f"{carrier} import"] = val
    except Exception:
        pass
    try:
        flow_out = r.get_total("flow_conversion_output")
        if "carrier" in flow_out.index.names and carrier in flow_out.index.get_level_values("carrier"):
            sub = flow_out.xs(carrier, level="carrier")
            by_tech = _series_from_level(sub, "technology", year, threshold=1e-3)
            pieces.update(by_tech.to_dict())
    except Exception:
        pass
    return pd.Series(pieces).sort_values(ascending=False)


def get_annual_total_cost(r: Results, years: list[int]) -> pd.Series:
    """Total system cost (CAPEX + OPEX) per year."""
    values = {}
    for y in years:
        capex = _get_annual_scalar(r, "cost_capex_yearly_total", y)
        opex = _get_annual_scalar(r, "cost_opex_yearly_total", y)
        if capex is None and opex is None:
            continue
        values[y] = (capex or 0.0) + (opex or 0.0)
    return pd.Series(values).sort_index()


def get_summary_metrics(r_a: Results, r_b: Results, year: int) -> dict:
    return {
        "em_a":    _get_annual_scalar(r_a, "carbon_emissions_annual", year),
        "em_b":    _get_annual_scalar(r_b, "carbon_emissions_annual", year),
        "capex_a": _get_annual_scalar(r_a, "cost_capex_yearly_total", year),
        "capex_b": _get_annual_scalar(r_b, "cost_capex_yearly_total", year),
        "opex_a":  _get_annual_scalar(r_a, "cost_opex_yearly_total", year),
        "opex_b":  _get_annual_scalar(r_b, "cost_opex_yearly_total", year),
    }


# ── Utility functions ─────────────────────────────────────────────────────────

def build_comparison_df(
    series_a: pd.Series, series_b: pd.Series, name_a: str, name_b: str
) -> pd.DataFrame:
    combined = pd.DataFrame({name_a: series_a, name_b: series_b}).fillna(0)
    return combined.sort_values(name_a, ascending=True)


def filter_techs(series: pd.Series, tech_list: list[str], threshold: float = 1e-6) -> pd.Series:
    present = [t for t in tech_list if t in series.index]
    if not present:
        return pd.Series(dtype=float)
    filtered = series.loc[present]
    return filtered[filtered.abs() > threshold].sort_values(ascending=False)


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

    fig, ax = plt.subplots(figsize=(10, 9))
    fig.suptitle(f"Total System Emissions — Year {year}", fontsize=13, fontweight="bold")
    plot_stacked_bars(df, "", "Mton CO₂eq", ax, show_segment_labels=False)
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

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle(f"Total System Costs — Year {year}", fontsize=13, fontweight="bold")
    plot_stacked_bars(build_comparison_df(capex_a, capex_b, name_a, name_b),
                      "CAPEX by Technology", "MEUR", axes[0])
    plot_stacked_bars(build_comparison_df(opex_a, opex_b, name_a, name_b),
                      "OPEX by Technology", "MEUR", axes[1])
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


def fig_costs_over_time(
    r_a: Results, r_b: Results, name_a: str, name_b: str
) -> plt.Figure:
    """Annual and cumulative total system cost across all years, A vs B.

    Useful to spot cases where a model is cheaper year-by-year early on
    (e.g. lower upfront CAPEX) but the cumulative cost ranking flips later
    once compounding OPEX savings pay off — e.g. flexibility investments
    that look expensive short-term but are cheaper from a system
    perspective over the full horizon.
    """
    years_a = get_available_years(r_a)
    years_b = get_available_years(r_b)
    s_a = get_annual_total_cost(r_a, years_a)
    s_b = get_annual_total_cost(r_b, years_b)

    color_a, color_b = "#1a237e", "#ff7043"

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("Total System Cost Over Time (CAPEX + OPEX)", fontsize=13, fontweight="bold")

    ax1.plot(s_a.index, s_a.values, marker="o", color=color_a, label=name_a)
    ax1.plot(s_b.index, s_b.values, marker="o", color=color_b, label=name_b)
    ax1.set_title("Annual Total Cost", fontsize=11, fontweight="bold")
    ax1.set_ylabel("MEUR")
    ax1.legend(fontsize=8)
    ax1.grid(alpha=0.3)

    cum_a = s_a.cumsum()
    cum_b = s_b.cumsum()
    ax2.plot(cum_a.index, cum_a.values, marker="o", color=color_a, label=name_a)
    ax2.plot(cum_b.index, cum_b.values, marker="o", color=color_b, label=name_b)
    ax2.set_title("Cumulative Total Cost", fontsize=11, fontweight="bold")
    ax2.set_ylabel("MEUR")
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)

    # Mark the year where the cheaper model switches, if it does.
    common_years = sorted(set(cum_a.index) & set(cum_b.index))
    if len(common_years) >= 2:
        diff = (cum_b - cum_a).loc[common_years]
        sign_changes = diff.values[:-1] * diff.values[1:]
        cross_idx = next((i for i, v in enumerate(sign_changes) if v < 0), None)
        if cross_idx is not None:
            cross_year = common_years[cross_idx + 1]
            ax2.axvline(cross_year, color="gray", linestyle="--", linewidth=1)
            ax2.annotate(
                f"Crossover\n{cross_year}", xy=(cross_year, cum_a.loc[cross_year]),
                xytext=(5, 10), textcoords="offset points", fontsize=8, color="gray",
            )

    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return fig


def fig_costs_industry(
    r_a: Results, r_b: Results, name_a: str, name_b: str, year: int
) -> plt.Figure:
    """Industry process CAPEX & OPEX, A vs B."""
    capex_a = get_capex_by_technology(r_a, year)
    capex_b = get_capex_by_technology(r_b, year)
    opex_a = get_opex_by_technology(r_a, year)
    opex_b = get_opex_by_technology(r_b, year)

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle(f"Industry Process Costs — Year {year}", fontsize=13, fontweight="bold")
    plot_stacked_bars(
        build_comparison_df(filter_techs(capex_a, INDUSTRY_PROCESS_TECHS),
                            filter_techs(capex_b, INDUSTRY_PROCESS_TECHS), name_a, name_b),
        "CAPEX", "MEUR", axes[0], show_segment_labels=True,
    )
    plot_stacked_bars(
        build_comparison_df(filter_techs(opex_a, INDUSTRY_PROCESS_TECHS),
                            filter_techs(opex_b, INDUSTRY_PROCESS_TECHS), name_a, name_b),
        "OPEX", "MEUR", axes[1], show_segment_labels=True,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


def fig_costs_heating(
    r_a: Results, r_b: Results, name_a: str, name_b: str, year: int
) -> plt.Figure:
    """Heating costs split into 3 groups: heat / district heat / industry heating."""
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
        plot_stacked_bars(
            build_comparison_df(filter_techs(capex_a, techs),
                                filter_techs(capex_b, techs), name_a, name_b),
            f"{label} — CAPEX", "MEUR", axes[0, col], show_segment_labels=True,
        )
        plot_stacked_bars(
            build_comparison_df(filter_techs(opex_a, techs),
                                filter_techs(opex_b, techs), name_a, name_b),
            f"{label} — OPEX", "MEUR", axes[1, col], show_segment_labels=True,
        )
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


def fig_costs_flexibility(
    r_a: Results, r_b: Results, name_a: str, name_b: str, year: int
) -> plt.Figure:
    """TES + DSM CAPEX & OPEX, A vs B."""
    capex_a = get_capex_by_technology(r_a, year)
    capex_b = get_capex_by_technology(r_b, year)
    opex_a = get_opex_by_technology(r_a, year)
    opex_b = get_opex_by_technology(r_b, year)

    all_flex = INDUSTRY_TES_TECHS + INDUSTRY_DSM_TECHS
    # Use a low threshold so near-zero costs still appear
    threshold = 1e-12

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle(f"Flexibility Costs (TES & DSM) — Year {year}", fontsize=13, fontweight="bold")
    plot_stacked_bars(
        build_comparison_df(filter_techs(capex_a, INDUSTRY_TES_TECHS, threshold),
                            filter_techs(capex_b, INDUSTRY_TES_TECHS, threshold), name_a, name_b),
        "TES — CAPEX", "MEUR", axes[0, 0], show_segment_labels=True,
    )
    plot_stacked_bars(
        build_comparison_df(filter_techs(opex_a, INDUSTRY_TES_TECHS, threshold),
                            filter_techs(opex_b, INDUSTRY_TES_TECHS, threshold), name_a, name_b),
        "TES — OPEX", "MEUR", axes[0, 1], show_segment_labels=True,
    )
    plot_stacked_bars(
        build_comparison_df(filter_techs(capex_a, INDUSTRY_DSM_TECHS, threshold),
                            filter_techs(capex_b, INDUSTRY_DSM_TECHS, threshold), name_a, name_b),
        "DSM — CAPEX", "MEUR", axes[1, 0], show_segment_labels=True,
    )
    plot_stacked_bars(
        build_comparison_df(filter_techs(opex_a, INDUSTRY_DSM_TECHS, threshold),
                            filter_techs(opex_b, INDUSTRY_DSM_TECHS, threshold), name_a, name_b),
        "DSM — OPEX", "MEUR", axes[1, 1], show_segment_labels=True,
    )
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
        df = build_comparison_df(
            get_fuel_consumption(r_a, carrier, year),
            get_fuel_consumption(r_b, carrier, year),
            name_a, name_b,
        )
        plot_stacked_bars(df, carrier.replace("_", " ").title(), "GWh", ax,
                          show_segment_labels=True)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return fig


def fig_natural_gas_balance(
    r_a: Results, r_b: Results, name_a: str, name_b: str, year: int
) -> plt.Figure:
    """Natural gas supply sources vs consumption by technology."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle(f"Natural Gas Balance — Year {year}", fontsize=13, fontweight="bold")
    plot_stacked_bars(
        build_comparison_df(get_fuel_supply(r_a, "natural_gas", year),
                            get_fuel_supply(r_b, "natural_gas", year), name_a, name_b),
        "Supply (imports + conversion)", "GWh", axes[0], show_segment_labels=True,
    )
    plot_stacked_bars(
        build_comparison_df(get_fuel_consumption(r_a, "natural_gas", year),
                            get_fuel_consumption(r_b, "natural_gas", year), name_a, name_b),
        "Consumption by Technology", "GWh", axes[1], show_segment_labels=True,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return fig
