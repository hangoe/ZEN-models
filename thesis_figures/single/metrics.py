"""Quantities derived from the single runs, shared by several figures.

flexibility_metrics() gives the dimensions compared across the flexibility scenarios:
discounted total system cost, heat-pump share of industrial heat, variable renewable
capacity and the annual discharge of bulk storage, industrial DSM and industrial TES.
DSM of mass products (kt) is converted to an energy equivalent (GWh) with the product's
energy intensity in the same run and year (get_dsm_energy_equivalent).
"""

import numpy as np
import pandas as pd

from ..names import HEAT_SUPPLY_STACK_ORDER
from ..results import (
    BULK_STORAGE_TECHS,
    HOURS_PER_YEAR,
    INDUSTRY_HEAT_TECHS_BOILERS_HP,
    INDUSTRY_TES_TECHS,
    Run,
    get_annual_total_cost,
    get_available_years,
    get_capacity,
    get_storage_flows,
)
from ..style import stack_ordered

METRICS_YEAR = 2050  # snapshot year of capacity, shares and discharge (cost: whole horizon)
VRE_TECHS = ["photovoltaics", "wind_onshore", "wind_offshore", "reservoir_hydro", "run-of-river_hydro"]
# Fixed-profile renewables whose unused potential counts as curtailment (VRE_TECHS without
# reservoir hydro, whose unused inflow is stored or spilled).
CURTAILMENT_TECHS = ["photovoltaics", "wind_onshore", "wind_offshore", "run-of-river_hydro"]

# ammonia_DSM and methanol_DSM store an energy carrier (GWh), the other DSM technologies a
# mass carrier (kt of product).
DSM_ENERGY_CARRIER_TECHS = {"ammonia_DSM", "methanol_DSM"}
PRODUCT_CARRIER_OF_DSM_TECH = {
    "primary_steel_DSM": "primary_steel", "secondary_steel_DSM": "secondary_steel",
    "clinker_DSM": "clinker", "ceramic_DSM": "ceramic", "glass_DSM": "glass",
    "food_DSM": "food", "paper_DSM": "paper", "olefin_DSM": "olefin",
}
DSM_ENERGY_STACK_ORDER = [
    "primary_steel_DSM", "secondary_steel_DSM", "clinker_DSM", "ceramic_DSM",
    "glass_DSM", "food_DSM", "paper_DSM", "olefin_DSM", "ammonia_DSM", "methanol_DSM",
]

_TOTAL_CACHE: dict[tuple[int, str], pd.DataFrame] = {}
_METRICS_CACHE: dict[tuple, object] = {}


def cached_total(results, component: str) -> pd.DataFrame:
    """results.get_total(component), memoised per Results object (several figures read
    the same large flow_conversion_* frames). Do not mutate the returned frame."""
    key = (id(results), component)
    if key not in _TOTAL_CACHE:
        _TOTAL_CACHE[key] = results.get_total(component)
    return _TOTAL_CACHE[key]


def output_avg_gw(r: Run, techs: list[str]) -> pd.DataFrame:
    """Operated output per technology and year as average power [GW] (annual output /
    8760 h), directly comparable to the installed capacity."""
    flow_out = cached_total(r.results, "flow_conversion_output")
    rows = {}
    for t in techs:
        if t not in flow_out.index.get_level_values("technology"):
            continue
        s = flow_out.xs(t, level="technology").sum(axis=0) / HOURS_PER_YEAR
        if (s.abs() > 1e-6).any():
            rows[t] = s
    return pd.DataFrame(rows).T if rows else pd.DataFrame()


def output_annual_twh(r: Run, techs: list[str]) -> pd.DataFrame:
    """Operated output per technology and year [TWh]."""
    return output_avg_gw(r, techs) * HOURS_PER_YEAR / 1000


def electrification_stack(r: Run) -> pd.DataFrame:
    """Share [%] of each electrified technology (electrode boiler, heat pumps) in the
    industrial heat output; index = year, columns in stack order (bottom to top)."""
    df = output_avg_gw(r, INDUSTRY_HEAT_TECHS_BOILERS_HP)
    total = df.sum(axis=0)
    electrified = [t for t in df.index if t == "electrode_boiler_industry" or t.startswith("heat_pump")]
    shares = 100 * df.loc[electrified].div(total, axis=1)
    return stack_ordered(shares, HEAT_SUPPLY_STACK_ORDER).T


def discounted_total_cost_bn(run: Run) -> float:
    """Discounted total system cost over the horizon [bn EUR]."""
    years = get_available_years(run.results)
    return float(get_annual_total_cost(run.results, years, discount=True).sum()) / 1000


def production_energy_intensity(r, carrier: str, flow_in_all: pd.DataFrame) -> pd.Series:
    """Energy input per output of product `carrier` [GWh/kt] by year, over all
    technologies that produce it (total input of all carriers, all in GWh)."""
    flow_out = cached_total(r, "flow_conversion_output")
    if carrier not in flow_out.index.get_level_values("carrier"):
        return pd.Series(dtype=float)
    prod = flow_out.xs(carrier, level="carrier").groupby("technology").sum()
    prod = prod[(prod.abs() > 1e-3).any(axis=1)]
    if prod.empty:
        return pd.Series(dtype=float)
    output_kt = prod.sum()
    input_gwh = pd.Series(0.0, index=output_kt.index)
    for tech in prod.index:
        if tech in flow_in_all.index.get_level_values("technology"):
            input_gwh = input_gwh.add(flow_in_all.xs(tech, level="technology").sum(), fill_value=0.0)
    return (input_gwh / output_kt).replace([np.inf, -np.inf], 0.0).fillna(0.0)


def get_dsm_energy_equivalent(r, dsm_techs: list[str], years: list[int]) -> pd.DataFrame:
    """Annual DSM discharge [GWh] (index = dsm_techs, columns = years): energy carriers
    as they are, mass products times their energy intensity."""
    flow_in_all = cached_total(r, "flow_conversion_input")
    intensity_cache: dict[str, pd.Series] = {}
    rows = {}
    for tech in dsm_techs:
        discharge = get_storage_flows(r, [tech], "flow_storage_discharge")
        if tech in DSM_ENERGY_CARRIER_TECHS:
            rows[tech] = {y: discharge.get(y, pd.Series(dtype=float)).sum() for y in years}
            continue
        carrier = PRODUCT_CARRIER_OF_DSM_TECH[tech]
        if carrier not in intensity_cache:
            intensity_cache[carrier] = production_energy_intensity(r, carrier, flow_in_all)
        intensity = intensity_cache[carrier]
        rows[tech] = {y: discharge.get(y, pd.Series(dtype=float)).sum() * intensity.get(y, 0.0)
                      for y in years}
    return pd.DataFrame(rows).T[years]


def flexibility_metrics(r: Run) -> dict[str, float]:
    """Dimensions compared across the flexibility scenarios, for one run: discounted total
    cost [bn EUR]; in METRICS_YEAR the heat-pump share of industrial heat [%], the
    variable renewable capacity [GW] and the discharge [TWh] of bulk storage, industrial
    DSM (energy equivalent) and industrial TES (0 in runs without them)."""
    key = (id(r.results), METRICS_YEAR)
    if key in _METRICS_CACHE:
        return _METRICS_CACHE[key]

    def discharge_twh(techs: list[str]) -> float:
        return float(get_storage_flows(r.results, techs, "flow_storage_discharge")
                     .get(METRICS_YEAR, pd.Series(dtype=float)).sum()) / 1000.0
    vre = float(get_capacity(r.results, VRE_TECHS, "power").get(METRICS_YEAR, pd.Series(dtype=float)).sum())
    dsm = get_dsm_energy_equivalent(r.results, DSM_ENERGY_STACK_ORDER, [METRICS_YEAR]).sum() \
        .get(METRICS_YEAR, 0.0)
    stack = electrification_stack(r)
    hp_cols = [c for c in stack.columns if c.startswith("heat_pump")]
    _METRICS_CACHE[key] = {"cost": discounted_total_cost_bn(r),
                           "hp_share": float(stack.loc[METRICS_YEAR, hp_cols].sum()),
                           "vre": vre,
                           "storage": discharge_twh(BULK_STORAGE_TECHS),
                           "dsm": float(dsm) / 1000.0,
                           "tes": discharge_twh(INDUSTRY_TES_TECHS)}
    return _METRICS_CACHE[key]


def curtailment_twh(r: Run, year: int = METRICS_YEAR) -> float:
    """Renewable curtailment in `year` [TWh] (thesis appendix, calculation of curtailment).

    ZEN-garden has no curtailment variable, so it is available minus generated
    electricity of CURTAILMENT_TECHS, summed over technologies i and nodes n:

        curtailment_y = sum_{i,n} [ capacity_{i,n,y} * sum_{h in y} max_load_{i,n,h}
                                    - sum_{h in y} flow_conversion_output_{i,electricity,n,h} ]

    max_load is mapped from the representative time steps back onto the 8760 h of the
    year (get_full_ts); flow_conversion_output from get_total is already weighted by the
    duration of the time steps."""
    key = (id(r.results), "curtailment", year)
    if key in _METRICS_CACHE:
        return _METRICS_CACHE[key]
    max_load = r.results.get_full_ts("max_load", year=year, index={"technology": CURTAILMENT_TECHS})
    cap = r.results.get_total("capacity")
    cap = cap[cap.index.get_level_values("capacity_type") == "power"].droplevel("capacity_type")
    available = (cap[year].reindex(max_load.index) * max_load.sum(axis=1)).sum()
    flow_out = cached_total(r.results, "flow_conversion_output")
    generated = flow_out[flow_out.index.get_level_values("technology").isin(CURTAILMENT_TECHS)
                         & (flow_out.index.get_level_values("carrier") == "electricity")][year].sum()
    _METRICS_CACHE[key] = float(available - generated) / 1000.0
    return _METRICS_CACHE[key]


def flexibility_metrics_with_curtailment(r: Run) -> dict[str, float]:
    """flexibility_metrics() plus the curtailment in METRICS_YEAR."""
    return {**flexibility_metrics(r), "curtailment": curtailment_twh(r)}
