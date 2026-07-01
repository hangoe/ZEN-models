"""ZEN-Garden Crystal Ball — Interactive Model Analysis Dashboard.

Run from repo root:  streamlit run streamlit/app.py
Or from this dir:    streamlit run app.py
"""

import matplotlib.pyplot as plt
import streamlit as st
from zen_garden import Results

from utils import get_available_models, get_available_years, load_results
from analyze import (
    fig_boiler_hp_production,
    fig_capacity_heat_supply,
    fig_capacity_production,
    fig_carrier_energy_all,
    fig_carrier_products_production,
    fig_dsm_capacity_addition,
    fig_dsm_charge_discharge,
    fig_heat_demand_by_sector,
    fig_storage_comparison,
    fig_tes_capacity_addition,
    fig_tes_charge_discharge,
)
from compare import (
    fig_costs_heating,
    fig_costs_industry,
    fig_costs_total,
    fig_emissions,
    fig_fuel_consumption,
    fig_natural_gas_balance,
    get_summary_metrics,
)

st.set_page_config(
    page_title="ZEN-Garden Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("ZEN-Garden Crystal Ball — Model Analysis Dashboard")

# ── Model discovery ───────────────────────────────────────────────────────────
available = get_available_models()

if not available:
    st.error("No model outputs found. Expected HDF5 files under `data/outputs/`.")
    st.stop()


@st.cache_resource(show_spinner="Loading model results...")
def cached_load(model_name: str) -> Results:
    return load_results(model_name)


def short(model_name: str) -> str:
    return model_name.replace("Crystal_Ball_HG_", "")


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Model Selection")

    default_b = min(1, len(available) - 1)
    model_a = st.selectbox("Model A", available, index=0, format_func=short, key="sel_a")
    model_b = st.selectbox("Model B", available, index=default_b, format_func=short, key="sel_b")

    if model_a == model_b:
        st.warning("Both models are identical — select different models to see differences.")

    st.divider()

    with st.spinner("Loading..."):
        r_a = cached_load(model_a)
        r_b = cached_load(model_b)

    years_a = get_available_years(r_a)
    years_b = get_available_years(r_b)
    all_years = sorted(set(years_a) | set(years_b))

    comparison_year = st.selectbox(
        "Comparison year",
        all_years,
        help="Year used in the Comparison tab",
    )

    st.divider()
    st.caption(f"**{short(model_a)}** years: {', '.join(str(y) for y in years_a)}")
    st.caption(f"**{short(model_b)}** years: {', '.join(str(y) for y in years_b)}")

name_a = short(model_a)
name_b = short(model_b)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_analysis, tab_compare = st.tabs(["📊 Analysis", "🔍 Comparison"])


# ── Helpers ───────────────────────────────────────────────────────────────────
def _show_pair(fig_fn, title: str) -> None:
    """Render one figure function side-by-side for Model A and Model B."""
    st.markdown(f"#### {title}")
    col1, col2 = st.columns(2)
    for col, r, label in [(col1, r_a, name_a), (col2, r_b, name_b)]:
        with col:
            st.caption(f"**{label}**")
            try:
                fig = fig_fn(r)
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)
            except Exception as exc:
                st.warning(f"Could not render: {exc}")


def _show_compare(fig_fn, title: str) -> None:
    """Render one comparison figure (both models, selected year)."""
    st.markdown(f"#### {title}")
    try:
        fig = fig_fn(r_a, r_b, name_a, name_b, comparison_year)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    except Exception as exc:
        st.warning(f"Could not render: {exc}")


# ── Analysis tab ──────────────────────────────────────────────────────────────
with tab_analysis:
    st.subheader("Industry Heat Analysis")
    st.caption(
        f"Showing **{name_a}** (left) and **{name_b}** (right) independently. "
        "Switch to the Comparison tab for direct A vs B charts."
    )

    with st.expander("Carrier Energy Flows", expanded=True):
        _show_pair(fig_carrier_energy_all,
                   "Industry Heat Carriers — Production & Consumption")
        _show_pair(fig_carrier_products_production,
                   "Product Carriers — Annual Production")
        _show_pair(fig_boiler_hp_production,
                   "Boiler & HP Production (excl. temperature conversion)")

    with st.expander("Capacities & Heat Demand", expanded=True):
        _show_pair(fig_capacity_heat_supply,
                   "Heat Supply Capacity — Boilers, HPs & Temperature Conversion")
        _show_pair(fig_capacity_production,
                   "Production Technology Capacity")
        _show_pair(fig_heat_demand_by_sector,
                   "Heat Demand by Sector (first vs last model year)")

    with st.expander("Storage & DSM", expanded=True):
        _show_pair(fig_tes_capacity_addition, "TES Capacity Addition")
        _show_pair(fig_tes_charge_discharge, "TES Charge & Discharge")
        _show_pair(fig_dsm_capacity_addition, "DSM Capacity Addition")
        _show_pair(fig_dsm_charge_discharge, "DSM Charge & Discharge")
        _show_pair(fig_storage_comparison,
                   "Storage Technologies — Cross-type Capacity Comparison")


# ── Comparison tab ────────────────────────────────────────────────────────────
with tab_compare:
    st.subheader(f"Model Comparison — Year {comparison_year}")
    st.caption(f"**{name_a}** vs **{name_b}**")

    # Summary metrics
    try:
        m = get_summary_metrics(r_a, r_b, comparison_year)
        c1, c2, c3 = st.columns(3)

        def _metric_pair(col, label, val_a, val_b, unit):
            if val_a is not None and val_b is not None:
                delta = val_b - val_a
                col.metric(
                    label=f"{label} ({unit})",
                    value=f"{val_a:,.0f}",
                    delta=f"{delta:+,.0f} (B−A)",
                    delta_color="inverse",
                    help=f"A: {val_a:,.1f}  |  B: {val_b:,.1f}",
                )

        _metric_pair(c1, "Annual Emissions", m.get("em_a"), m.get("em_b"), "Mton CO₂")
        _metric_pair(c2, "Total CAPEX", m.get("capex_a"), m.get("capex_b"), "MEUR")
        _metric_pair(c3, "Total OPEX", m.get("opex_a"), m.get("opex_b"), "MEUR")
    except Exception:
        pass

    st.divider()

    if comparison_year not in years_a or comparison_year not in years_b:
        missing = []
        if comparison_year not in years_a:
            missing.append(f"**{name_a}** (available: {years_a})")
        if comparison_year not in years_b:
            missing.append(f"**{name_b}** (available: {years_b})")
        st.warning(
            f"Year {comparison_year} not available in: {', '.join(missing)}. "
            "Charts for that model will show empty bars."
        )

    _show_compare(fig_emissions, "Total System Emissions")
    _show_compare(fig_costs_total, "Total System Costs (CAPEX & OPEX)")
    _show_compare(fig_costs_industry, "Industry Process Costs")
    _show_compare(fig_costs_heating, "Heating Costs (Heat / District Heat / Industry Heating)")
    _show_compare(fig_fuel_consumption, "Fuel Consumption Breakdown")
    _show_compare(fig_natural_gas_balance, "Natural Gas Balance (Supply vs Consumption)")
