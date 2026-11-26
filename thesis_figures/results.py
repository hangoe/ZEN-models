"""Loading ZEN-garden results and reading the quantities the figures plot.

ZEN-Europe splits every industry heat technology and carrier by sector
(heat_pump_industry_0_100_water_ceramic, heat_industry_0_100_food, ...). The figures use
the names without the sector suffix: SectorAggregatedResults strips the suffix and sums
over the sectors (intensive parameters are averaged instead).
"""

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from zen_garden import Results

HOURS_PER_YEAR = 8760

# ── Technology sets (names after sector aggregation) ────────────────────────
INDUSTRY_HEAT_PUMPS = [
    "heat_pump_industry_0_100_waste_heat", "heat_pump_industry_0_100_water",
    "heat_pump_industry_100_150_waste_heat", "heat_pump_industry_100_150_water",
    "heat_pump_industry_150_200_waste_heat", "heat_pump_industry_150_200_water",
]
INDUSTRY_BOILERS = [
    "biomass_boiler_industry", "electrode_boiler_industry", "natural_gas_boiler_industry",
    "oil_boiler_industry", "coal_boiler_industry", "waste_boiler_industry",
]
INDUSTRY_HEAT_TECHS_BOILERS_HP = INDUSTRY_HEAT_PUMPS + INDUSTRY_BOILERS
# Same technologies, boilers first (stacking order of the cost breakdown).
INDUSTRY_HEATING_TECHS = [
    "natural_gas_boiler_industry", "electrode_boiler_industry", "biomass_boiler_industry",
    "oil_boiler_industry", "coal_boiler_industry", "waste_boiler_industry", *INDUSTRY_HEAT_PUMPS,
]
INDUSTRY_TES_TECHS = ["industry_TES_water_0_100", "industry_TES_water_100_150", "industry_TES_steam_150_200"]
INDUSTRY_DSM_TECHS = [
    "ammonia_DSM", "ceramic_DSM", "clinker_DSM", "food_DSM", "glass_DSM",
    "methanol_DSM", "olefin_DSM", "paper_DSM", "primary_steel_DSM", "secondary_steel_DSM",
]
BULK_STORAGE_TECHS = ["battery", "pumped_hydro", "natural_gas_storage", "oil_storage", "salt_cavern_storage"]


# ── Loading ─────────────────────────────────────────────────────────────────
_SECTOR_SUFFIX_RE = re.compile(
    r"^(.*(?:_industry|industry_TES|kilnfuel|fuel_to_kiln|heat_industry).*?)_(?:ceramic|food|glass|paper)$")
_AGGREGATED_LEVELS = ("technology", "carrier")
# Per-unit (intensive) parameters are averaged over the sectors, everything else is summed.
_INTENSIVE_PARAMETER_RE = re.compile(
    r"conversion_factor|efficiency|rate|lifetime|share|price|cost|load|factor|ratio|duration|coefficient|self_discharge")
# Large components are read a few technologies at a time (see _get_total_chunked).
_CHUNKED_COMPONENTS = {"flow_conversion_input", "flow_conversion_output"}
_CHUNK_TECHS = 6


def strip_sector_suffix(name):
    """"heat_pump_industry_0_100_water_food" -> "heat_pump_industry_0_100_water"."""
    if not isinstance(name, str):
        return name
    m = _SECTOR_SUFFIX_RE.match(name)
    return m.group(1) if m else name


class SectorAggregatedResults:
    """zen_garden.Results whose get_total / get_full_ts frames have their technology and
    carrier levels sector-aggregated (strip_sector_suffix): summed, except intensive
    parameters, which are averaged. Set components get the suffix stripped from index
    and values and are de-duplicated. Everything else delegates to Results."""

    def __init__(self, results: Results):
        self._results = results
        self._parameters = set(results.get_component_names("parameter"))

    def __getattr__(self, attr):
        return getattr(self._results, attr)

    def _aggregate(self, component: str, df):
        if not isinstance(df, (pd.DataFrame, pd.Series)):
            return df
        names = list(df.index.names)
        levels = [i for i, n in enumerate(names) if n in _AGGREGATED_LEVELS]
        if component.startswith("set_"):
            out = df.copy()
            out.index = out.index.map(strip_sector_suffix)
            if isinstance(out, pd.Series):
                out = out.map(strip_sector_suffix)
            return out[~out.index.duplicated()]
        if not levels:
            return df
        if not any(strip_sector_suffix(v) != v
                   for i in levels for v in df.index.get_level_values(i).unique()):
            return df
        out = df.copy()
        if isinstance(out.index, pd.MultiIndex):
            out.index = pd.MultiIndex.from_arrays(
                [out.index.get_level_values(i).map(strip_sector_suffix) if i in levels
                 else out.index.get_level_values(i) for i in range(len(names))], names=names)
        else:
            out.index = out.index.map(strip_sector_suffix)
        grouped = out.groupby(level=list(range(len(names))), sort=False)
        intensive = component in self._parameters and _INTENSIVE_PARAMETER_RE.search(component)
        return grouped.mean() if intensive else grouped.sum()

    def _get_total_chunked(self, component):
        """Results.get_total, a few technologies at a time: read at once, the dense
        flow_conversion_* arrays take several GB as a pandas Series."""
        techs = self._results.get_total("capacity").index.get_level_values("technology").unique()
        chunks = [self._results.get_total(component, index={"technology": list(techs[i:i + _CHUNK_TECHS])})
                  for i in range(0, len(techs), _CHUNK_TECHS)]
        return pd.concat([c for c in chunks if not c.empty]).sort_index()

    def get_total(self, component, *args, **kwargs):
        if component in _CHUNKED_COMPONENTS and not args and not kwargs:
            return self._aggregate(component, self._get_total_chunked(component))
        return self._aggregate(component, self._results.get_total(component, *args, **kwargs))

    def get_full_ts(self, component, *args, **kwargs):
        return self._aggregate(component, self._results.get_full_ts(component, *args, **kwargs))

    def get_df(self, component, *args, **kwargs):
        """Shim for the older Results API; only used for set components."""
        return self.get_total(component, *args, **kwargs)


def _find_output_dir(path: Path, max_depth: int = 3) -> Path | None:
    """Breadth-first search below `path` for the folder that holds variables.nc
    (or var_dict.h5, older ZEN-garden output format)."""
    if not path.exists():
        return None
    frontier = [path]
    for _ in range(max_depth + 1):
        for d in frontier:
            if (d / "var_dict.h5").exists() or (d / "variables.nc").exists():
                return d
        frontier = [sd for d in frontier for sd in sorted(d.iterdir())
                    if sd.is_dir() and not sd.name.startswith(".")]
    return None


def load_results(root: Path, run_folder: str) -> Results:
    """Results of the run in `root / run_folder` (sector-aggregated for ZEN-Europe)."""
    path = root / run_folder
    if not path.exists():
        raise FileNotFoundError(f"Model output not found: {path}")
    match = _find_output_dir(path)
    if match is None:
        raise FileNotFoundError(f"No var_dict.h5/variables.nc found under {path}")
    if (match / "variables.nc").exists():
        return SectorAggregatedResults(Results(path=str(match)))
    return Results(path=str(match))


@dataclass(frozen=True)
class Run:
    name: str        # run folder name
    label: str       # scenario name used in the thesis
    results: Results


def get_available_years(r: Results) -> list[int]:
    """Calendar years of the run (Results.get_years() returns 0-based indices)."""
    for var in ("flow_conversion_output", "capacity", "carbon_emissions_carrier"):
        try:
            df = r.get_total(var)
        except KeyError:
            continue
        if isinstance(df, pd.DataFrame) and not df.empty:
            years = sorted(int(c) for c in df.columns if isinstance(c, (int, float)) and float(c) > 1000)
            if years:
                return years
    raise ValueError("no calendar years found in the results")


# ── Quantities by technology ────────────────────────────────────────────────

def get_capacity(r: Results, techs: list[str], capacity_type: str = "power") -> pd.DataFrame:
    """Installed capacity per technology (rows) and year (columns), summed over nodes."""
    cap = r.get_total("capacity")
    cap = cap[cap.index.get_level_values("capacity_type") == capacity_type]
    rows = {}
    for tech in techs:
        if tech in cap.index.get_level_values("technology"):
            s = cap.xs(tech, level="technology").sum()
            if (s.abs() > 1e-6).any():
                rows[tech] = s
    return pd.DataFrame(rows).T if rows else pd.DataFrame()


def get_storage_flows(r: Results, techs: list[str], flow_type: str) -> pd.DataFrame:
    """Annual storage flow `flow_type` (e.g. flow_storage_discharge) per technology and year."""
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


def _value_in_year(df: pd.DataFrame, level: str, value: str, year: int) -> float:
    """Select `value` on `level`, sum the other dimensions, return the value of `year`."""
    s = df.xs(value, level=level).sum()
    if isinstance(s, (int, float)):
        return float(s)
    for key in (year, str(year)):
        if key in s.index:
            return float(s[key])
    return float({int(k): v for k, v in s.items()}.get(year, 0.0))


def _series_by_level(df: pd.DataFrame, level: str, year: int, threshold: float = 1e-6) -> pd.Series:
    """{entity of `level`: value in `year`}, largest first, near-zero entries dropped."""
    if level not in df.index.names:
        return pd.Series(dtype=float)
    values = {e: _value_in_year(df, level, e, year) for e in df.index.get_level_values(level).unique()}
    return pd.Series({k: v for k, v in values.items() if abs(v) > threshold}).sort_values(ascending=False)


def get_emissions_by_carrier(r: Results, year: int) -> pd.Series:
    return _series_by_level(r.get_total("carbon_emissions_carrier"), "carrier", year)


def get_emissions_by_technology(r: Results, year: int) -> pd.Series:
    return _series_by_level(r.get_total("carbon_emissions_technology"), "technology", year)


def get_capex_by_technology(r: Results, year: int) -> pd.Series:
    return _series_by_level(r.get_total("cost_capex_yearly"), "technology", year)


def get_opex_by_technology(r: Results, year: int) -> pd.Series:
    return _series_by_level(r.get_total("cost_opex_yearly"), "technology", year)


# ── Costs per year ──────────────────────────────────────────────────────────

def annual_series(r: Results, variable: str, years: list[int]) -> pd.Series:
    """Total of `variable` per year, summed over all other dimensions."""
    data = r.get_total(variable)
    s = data.sum(axis=0) if isinstance(data, pd.DataFrame) else data
    lookup = {}
    for k, v in s.items():
        try:
            lookup[int(k)] = float(v)
        except (TypeError, ValueError):
            continue
    return pd.Series({y: lookup[y] for y in years if y in lookup}).sort_index()


def discount_factors(r: Results, years: list[int]) -> pd.Series:
    """Discount factor per period = net_present_cost / cost_total (ZEN-garden reports the
    discounted, interval-aggregated cost of each period and its undiscounted counterpart)."""
    npc = annual_series(r, "net_present_cost", years)
    ct = annual_series(r, "cost_total", years)
    return npc.divide(ct).replace([np.inf, -np.inf], np.nan).reindex(years).fillna(0.0)


def get_annual_cost(r: Results, years: list[int], variable: str, discount: bool = True) -> pd.Series:
    """Cost `variable` per year, optionally as net present value."""
    s = annual_series(r, variable, years)
    if discount and not s.empty:
        s = s.multiply(discount_factors(r, years)).dropna()
    return s.sort_index()


def get_annual_total_cost(r: Results, years: list[int], discount: bool = True) -> pd.Series:
    """Total system cost per year (technology CAPEX and OPEX, carrier and carbon cost),
    discounted (net_present_cost) or not (cost_total)."""
    return annual_series(r, "net_present_cost" if discount else "cost_total", years)
