"""ZEN-Garden Crystal Ball — Interactive Model Analysis Dashboard.

Run:  streamlit run streamlit/app.py   (from repo root)
  or  streamlit run app.py             (from streamlit/ directory)

5 thematic tabs:
  1. Carrier Flows   — production, consumption, boiler/HP output
  2. Capacity        — heat supply, production, heat demand by sector
  3. Storage & DSM   — TES and DSM capacity, charge/discharge, cross-comparison
  4. Costs           — CAPEX, OPEX broken down by technology (year-specific, A vs B)
  5. System          — emissions, fuel consumption, natural gas balance (year-specific, A vs B)
"""

import matplotlib.pyplot as plt
import streamlit as st
from zen_garden import Results

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
from utils import get_available_models, get_available_years, load_results

st.set_page_config(
    page_title="ZEN-Garden Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("ZEN-Garden Crystal Ball")

# ── Model discovery ───────────────────────────────────────────────────────────
available = get_available_models()
if not available:
    st.error("No model outputs found. Expected HDF5 files under `data/outputs/`.")
    st.stop()


@st.cache_resource(show_spinner="Loading model data…")
def cached_load(model_name: str) -> Results:
    return load_results(model_name)


def short(name: str) -> str:
    return name.replace("Crystal_Ball_HG_", "")


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Model Selection")

    model_a = st.selectbox("Model A", available, index=0,
                           format_func=short, key="sel_a")
    model_b = st.selectbox("Model B", available, index=min(1, len(available) - 1),
                           format_func=short, key="sel_b")

    if model_a == model_b:
        st.warning("Both selections are the same model.")

    r_a = cached_load(model_a)
    r_b = cached_load(model_b)

    years_a = get_available_years(r_a)
    years_b = get_available_years(r_b)
    all_years = sorted(set(years_a) | set(years_b))

    st.divider()
    st.subheader("Costs & System year")
    year = st.selectbox("Year", all_years,
                        help="Applies to the Costs and System tabs only")

    st.divider()
    st.caption(f"**{short(model_a)}** — years: {', '.join(str(y) for y in years_a)}")
    st.caption(f"**{short(model_b)}** — years: {', '.join(str(y) for y in years_b)}")

name_a = short(model_a)
name_b = short(model_b)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _plot(r: Results, fig_fn, title: str = "") -> None:
    """Render a single-model figure at full width."""
    if title:
        st.markdown(f"##### {title}")
    try:
        fig = fig_fn(r)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    except Exception as exc:
        st.warning(f"Could not render: {exc}")


def _compare(fig_fn, title: str = "") -> None:
    """Render an A-vs-B comparison figure at full width."""
    if title:
        st.markdown(f"##### {title}")
    try:
        fig = fig_fn(r_a, r_b, name_a, name_b, year)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    except Exception as exc:
        st.warning(f"Could not render: {exc}")


def _model_subtabs(plots_a_b: list[tuple]) -> None:
    """Create [Model A | Model B] sub-tabs, each showing the given list of (fig_fn, title)."""
    sub_a, sub_b = st.tabs([f"📊 {name_a}", f"📊 {name_b}"])
    for sub, r in [(sub_a, r_a), (sub_b, r_b)]:
        with sub:
            for fig_fn, title in plots_a_b:
                _plot(r, fig_fn, title)


# ── 5 tabs ────────────────────────────────────────────────────────────────────
tab_carrier, tab_capacity, tab_storage, tab_costs, tab_system = st.tabs([
    "⚡ Carrier Flows",
    "🏭 Capacity",
    "🔋 Storage & DSM",
    "💰 Costs",
    "🌍 System",
])


# ── Tab 1: Carrier Flows ──────────────────────────────────────────────────────
with tab_carrier:
    st.caption("Industry heat carrier production, consumption, and boiler/HP output. "
               "Switch between models with the sub-tabs.")
    _model_subtabs([
        (fig_carrier_energy_all,         "Carrier Energy — Production & Consumption"),
        (fig_carrier_products_production, "Product Carriers — Annual Production"),
        (fig_boiler_hp_production,        "Boiler & HP Production"),
    ])


# ── Tab 2: Capacity ───────────────────────────────────────────────────────────
with tab_capacity:
    st.caption("Installed capacity additions and totals for heat supply, production "
               "technologies, and sector-level heat demand.")
    _model_subtabs([
        (fig_capacity_heat_supply,  "Heat Supply Capacity"),
        (fig_capacity_production,   "Production Technology Capacity"),
        (fig_heat_demand_by_sector, "Heat Demand by Sector (first vs last year)"),
    ])


# ── Tab 3: Storage & DSM ──────────────────────────────────────────────────────
with tab_storage:
    st.caption("Thermal energy storage and demand-side management — capacity, "
               "charge/discharge flows, and cross-technology comparison.")
    _model_subtabs([
        (fig_tes_capacity_addition, "TES Capacity Addition"),
        (fig_tes_charge_discharge,  "TES Charge & Discharge"),
        (fig_dsm_capacity_addition, "DSM Capacity Addition"),
        (fig_dsm_charge_discharge,  "DSM Charge & Discharge"),
        (fig_storage_comparison,    "Storage Technologies — Cross-type Comparison"),
    ])


# ── Tab 4: Costs ──────────────────────────────────────────────────────────────
with tab_costs:
    st.caption(f"CAPEX and OPEX comparison for year **{year}** — "
               f"**{name_a}** vs **{name_b}**")

    if year not in years_a or year not in years_b:
        missing = []
        if year not in years_a:
            missing.append(f"{name_a} (has: {years_a})")
        if year not in years_b:
            missing.append(f"{name_b} (has: {years_b})")
        st.warning(f"Year {year} missing in: {', '.join(missing)}. "
                   "Those bars will be empty.")

    _compare(fig_costs_total,    "Total System Costs (CAPEX & OPEX)")
    _compare(fig_costs_industry, "Industry Process Costs")
    _compare(fig_costs_heating,  "Heating Costs — Heat / District Heat / Industry Heating")


# ── Tab 5: System ─────────────────────────────────────────────────────────────
with tab_system:
    st.caption(f"System-level metrics for year **{year}** — "
               f"**{name_a}** vs **{name_b}**")

    # Summary metrics row
    try:
        m = get_summary_metrics(r_a, r_b, year)

        def _metric_row(label: str, val_a, val_b, unit: str) -> None:
            if val_a is None and val_b is None:
                return
            c1, c2, c3 = st.columns(3)
            c1.metric(f"{label} — {name_a}", f"{val_a:,.0f} {unit}" if val_a is not None else "n/a")
            c2.metric(f"{label} — {name_b}", f"{val_b:,.0f} {unit}" if val_b is not None else "n/a")
            if val_a is not None and val_b is not None:
                delta = val_b - val_a
                pct = delta / val_a * 100 if val_a else 0
                c3.metric("Δ (B − A)", f"{delta:+,.0f} {unit}",
                          delta=f"{pct:+.1f}%", delta_color="inverse")

        _metric_row("Emissions",   m.get("em_a"),    m.get("em_b"),    "Mton CO₂")
        _metric_row("Total CAPEX", m.get("capex_a"), m.get("capex_b"), "MEUR")
        _metric_row("Total OPEX",  m.get("opex_a"),  m.get("opex_b"),  "MEUR")
    except Exception:
        pass

    st.divider()
    _compare(fig_emissions,           "Total System Emissions")
    _compare(fig_fuel_consumption,    "Fuel Consumption by Technology")
    _compare(fig_natural_gas_balance, "Natural Gas Balance (Supply vs Consumption)")
