"""Net industrial CO2 emissions, 2022-2050 (presentation): one stacked bar per year.

ZEN-garden books fuel emissions on the carrier imports (carbon_emissions_carrier), not on
the technologies that burn the fuel, so they are attributed here:

- Process: carbon_emissions_technology of the industry technologies (INDUSTRY_TECHS).
- Fuels: fossil carrier input of the industry technologies x the year's average carrier
  intensity (the carrier's import emissions over its total consumption, so biomethane in
  natural gas and pyrolysis coal lower it). Naphtha is made 1:1 from oil and gets the oil
  intensity. Feedstocks (naphtha for olefins, natural gas for methanol) are counted like
  fuels, as the model counts them at import.
- Captured CO2 of each industrial capture unit is taken off its host technology's process
  and fuel emissions in proportion to the two (CAPTURE_HOSTS), so all bars are net.
- Electricity: electricity input of the industry technologies in each node x the node's
  average grid intensity in that year (generation-based: power-plant emissions over their
  generation, no imports between nodes). Power-plant emissions are fuel input x carrier
  intensity, minus the capture of natural_gas_turbine_CCS; biomass CCS removals are not
  credited to the grid.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..results import Run, get_available_years
from ..style import ETH_BLUE, ETH_BRONZE, ETH_GREY, eth_tint, report_legend, save_figure
from .electricity_profile import INDUSTRY_GROUPS, LEGEND_SIZE

# carrier -> carriers whose import emissions it carries
FOSSIL_CARRIERS = {"hard_coal": ["hard_coal"], "lignite": ["lignite"], "natural_gas": ["natural_gas", "lng"],
                   "oil": ["crude_oil"], "waste": ["waste"]}
SAME_INTENSITY_AS = {"naphtha": "oil"}

# Industry technologies (sector-aggregated names): production, heat, kiln/cement fuels, capture.
INDUSTRY_CAPTURE = ["BF_BOF_CCS", "NG_DRI_CCS", "cement_post_comb", "ceramic_post_comb", "glass_post_comb"]
# capture unit -> (process-emission technologies, fuel-burning technologies) of its host
CAPTURE_HOSTS = {
    "cement_post_comb": (["cement_kiln"], ["coal_to_cement_fuel", "waste_to_cement_fuel"]),
    "glass_post_comb": (["glass_production"], ["glass_production"]),
    "ceramic_post_comb": (["ceramic_production"], ["ceramic_production"]),
    "BF_BOF_CCS": (["BF_BOF"], ["BF_BOF"]),
    "NG_DRI_CCS": (["NG_DRI"], ["NG_DRI"]),
}
INDUSTRY_TECHS = sorted({
    t for _, techs in INDUSTRY_GROUPS.values() for t in techs} | set(INDUSTRY_CAPTURE) | {
    "coal_boiler_industry", "natural_gas_boiler_industry", "oil_boiler_industry", "waste_boiler_industry",
    "biomass_boiler_industry", "coal_to_cement_fuel", "waste_to_cement_fuel", "biomass_to_cement_fuel",
    "hydrogen_to_cement_fuel", "natural_gas_to_kilnfuel", "hydrogen_to_kilnfuel",
})
# Consumers of fossil carriers outside industry (energy supply, buildings, transport).
NON_INDUSTRY_FOSSIL_USERS = {
    "SMR", "SMR_CCS", "refining", "lng_terminal", "natural_gas_boiler", "natural_gas_boiler_DH", "oil_boiler",
    "waste_boiler_DH", "oil_boiler_DH", "oil_to_diesel_conversion", "oil_to_gasoline_conversion",
    "oil_to_kerosene_conversion", "oil_to_naphtha_conversion", "natural_gas_turbine", "natural_gas_turbine_CCS",
    "hard_coal_plant", "lignite_coal_plant", "oil_plant", "waste_plant", "HDT_diesel", "ICE_diesel",
    "diesel_ICE_ship",
}
POWER_PLANTS = ["biomass_plant", "fuel_cell", "hard_coal_plant", "lignite_coal_plant", "natural_gas_turbine",
                "nuclear", "oil_plant", "photovoltaics", "run-of-river_hydro", "waste_plant",
                "wind_offshore", "wind_onshore"]
POWER_CAPTURE = ["natural_gas_turbine_CCS"]
KT_PER_MT = 1000.0
EMISSIONS_FIG_SIZE = (4.2, 4.2)  # in; legend below the axes

# category -> colour, stack order bottom to top
CATEGORY_COLORS = {
    "Process emissions": eth_tint(ETH_GREY, 0.45),
    "Fuel combustion (incl. feedstocks)": eth_tint(ETH_BRONZE, 0.3),
    "Electricity use (grid mix of each node)": eth_tint(ETH_BLUE, 0.35),
}
PROCESS, FUEL, GRID = CATEGORY_COLORS


def carrier_intensity(r, years: list[int]) -> pd.DataFrame:
    """Average emission intensity [Mt/GWh] per fuel carrier (rows) and year (columns)."""
    em = r.get_total("carbon_emissions_carrier").groupby("carrier").sum()
    use = r.get_total("flow_conversion_input").groupby("carrier").sum()
    out = {}
    for c, sources in FOSSIL_CARRIERS.items():
        e = sum(em.loc[s, years] for s in sources if s in em.index)
        u = use.loc[c, years] if c in use.index else pd.Series(0.0, index=years)
        out[c] = (e / u.where(u > 0)).fillna(0.0)
    for c, like in SAME_INTENSITY_AS.items():
        out[c] = out[like]
    return pd.DataFrame(out).T


def direct_emissions(r, years: list[int], intensity: pd.DataFrame) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Net process and net fuel emissions of industry [Mt/a] per year, and the captured CO2."""
    fi = r.get_total("flow_conversion_input")[years].groupby(["technology", "carrier"]).sum()
    fossil = fi[fi.index.get_level_values("carrier").isin(intensity.index)]
    unclassified = sorted({t for t, _ in fossil[fossil.max(axis=1) > 1.0].index}
                          - set(INDUSTRY_TECHS) - NON_INDUSTRY_FOSSIL_USERS)
    if unclassified:
        raise ValueError(f"fossil fuel users neither industry nor non-industry: {unclassified}")
    fossil = fossil[fossil.index.get_level_values("technology").isin(INDUSTRY_TECHS)]
    fuel_by_tech = (fossil.mul(intensity, level="carrier")).groupby("technology").sum()

    te = r.get_total("carbon_emissions_technology")[years].groupby("technology").sum()
    proc_by_tech = te[te.index.isin(INDUSTRY_TECHS)]

    fo = r.get_total("flow_conversion_output")[years]
    carbon = fo.xs("carbon", level="carrier").groupby("technology").sum() / KT_PER_MT
    process, fuel = proc_by_tech.sum(), fuel_by_tech.sum()
    captured = pd.Series(0.0, index=years)
    for unit, (proc_techs, fuel_techs) in CAPTURE_HOSTS.items():
        cap = carbon.loc[unit] if unit in carbon.index else pd.Series(0.0, index=years)
        p = proc_by_tech.reindex(proc_techs).fillna(0.0).sum().clip(lower=0.0)
        f = fuel_by_tech.reindex(fuel_techs).fillna(0.0).sum()
        # A unit can capture more than its host's fossil emissions (BF_BOF_CCS: part of the
        # coal is biogenic pyrolysis coal, which lowers the average coal intensity); the
        # excess is a net removal and lowers the category below the host's emissions.
        share_p = (p / (p + f).where(p + f > 0)).fillna(0.0)
        process -= cap * share_p
        fuel -= cap * (1 - share_p)
        captured += cap
    return process, fuel, captured


def grid_intensity_by_node(r, years: list[int], intensity: pd.DataFrame) -> pd.DataFrame:
    """Average grid emission intensity [Mt/GWh] per node (rows) and year (columns)."""
    fi = r.get_total("flow_conversion_input")[years]
    fi = fi[fi.index.get_level_values("technology").isin(POWER_PLANTS)
            & fi.index.get_level_values("carrier").isin(intensity.index)]
    fuel = (fi.groupby(["carrier", "node"]).sum()
            .mul(intensity.reindex(fi.index.get_level_values("carrier").unique()), level="carrier")
            .groupby("node").sum())
    te = r.get_total("carbon_emissions_technology")[years]
    proc = te[te.index.get_level_values("technology").isin(POWER_PLANTS)].groupby("location").sum()
    proc.index.name = "node"
    fo = r.get_total("flow_conversion_output")[years]
    cap = fo[fo.index.get_level_values("technology").isin(POWER_CAPTURE)
             & (fo.index.get_level_values("carrier") == "carbon")].groupby("node").sum() / KT_PER_MT
    gen = fo[fo.index.get_level_values("technology").isin(POWER_PLANTS)
             & (fo.index.get_level_values("carrier") == "electricity")].groupby("node").sum()
    em = fuel.add(proc, fill_value=0.0).sub(cap, fill_value=0.0).reindex(gen.index).fillna(0.0)
    return (em / gen.where(gen > 0)).fillna(0.0)


def grid_emissions(r, years: list[int], intensity: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Grid emissions of industrial electricity use [Mt/a] per GRID_GROUPS group and year,
    and the generation-weighted European grid intensity [g/kWh] per year."""
    node_int = grid_intensity_by_node(r, years, intensity)
    fi = r.get_total("flow_conversion_input")[years].xs("electricity", level="carrier")
    groups = {**{g: techs for g, (_, techs) in INDUSTRY_GROUPS.items()}, "Carbon capture units": INDUSTRY_CAPTURE}
    rows = {}
    for g, techs in groups.items():
        use = fi[fi.index.get_level_values("technology").isin(techs)].groupby("node").sum()
        rows[g] = (use * node_int.reindex(use.index).fillna(0.0)).sum()
    fo = r.get_total("flow_conversion_output")[years]
    gen = fo[fo.index.get_level_values("technology").isin(POWER_PLANTS)
             & (fo.index.get_level_values("carrier") == "electricity")].groupby("node").sum()
    eu = (node_int.reindex(gen.index) * gen).sum() / gen.sum() * 1e6   # Mt/GWh -> g/kWh
    return pd.DataFrame(rows).T, eu


def industry_emissions(run: Run, name: str) -> None:
    r = run.results
    years = get_available_years(r)
    intensity = carrier_intensity(r, years)
    process, fuel, captured = direct_emissions(r, years, intensity)
    grid, eu_intensity = grid_emissions(r, years, intensity)
    df = pd.DataFrame({PROCESS: process, FUEL: fuel, GRID: grid.sum().clip(lower=0.0)}).T

    fig, ax = plt.subplots(figsize=EMISSIONS_FIG_SIZE)
    x = np.arange(len(years))
    bottom = np.zeros(len(years))
    for cat in df.index:
        ax.bar(x, df.loc[cat].values, 0.7, bottom=bottom, color=CATEGORY_COLORS[cat], edgecolor="white",
               linewidth=0.4, label=cat)
        bottom += df.loc[cat].values
    for xi, total in zip(x, bottom):
        ax.text(xi, total + bottom.max() * 0.015, f"{total:.0f}", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels([str(y) for y in years])
    ax.set_xlim(-0.6, len(x) - 0.4)
    ax.set_ylim(0, bottom.max() * 1.1)
    ax.set_ylabel("Net emissions (Mt CO$_2$/a)")
    ax.set_title("Net industrial CO$_2$ emissions", loc="left",
                 fontsize=9.5, fontweight="bold", pad=5)
    fig.tight_layout()
    h, l = ax.get_legend_handles_labels()
    legend = report_legend(ax, h[::-1], l[::-1], fontsize=LEGEND_SIZE, loc="upper left",
                           bbox_to_anchor=(0.0, -0.1), ncol=1)

    print(f"  {run.label}: process {process.round(0).to_dict()}")
    print(f"  fuel {fuel.round(0).to_dict()}")
    print(f"  grid {grid.sum().round(1).to_dict()}")
    print(f"  captured {captured.round(0).to_dict()}")
    print(f"  European grid intensity g/kWh {eu_intensity.round(0).to_dict()}")
    save_figure(fig, name, extra_artists=[legend])


SHARE_FIG_SIZE = (2.4, 4.2)  # in; one bar, legend right
INDUSTRY_SHARE_COLORS = {"Industry (net, incl. electricity)": ETH_BLUE, "Rest of the energy system": eth_tint(ETH_GREY, 0.45)}


def industry_share_of_total(run: Run, name: str) -> None:
    """Total net emissions of the first modelled year as one bar: industry (process + fuels
    + grid, net of capture, as in industry_emissions) and the rest of the energy system
    (total minus industry)."""
    r = run.results
    years = get_available_years(r)
    year = years[0]
    intensity = carrier_intensity(r, [year])
    process, fuel, _ = direct_emissions(r, [year], intensity)
    grid, _ = grid_emissions(r, [year], intensity)
    industry = float((process + fuel + grid.sum()).iloc[0])
    total = float(r.get_total("carbon_emissions_annual")[year])
    rest = total - industry

    fig, ax = plt.subplots(figsize=SHARE_FIG_SIZE)
    (ind_label, ind_color), (rest_label, rest_color) = INDUSTRY_SHARE_COLORS.items()
    ax.bar(0, industry, 0.6, color=ind_color, edgecolor="white", linewidth=0.4, label=ind_label)
    ax.bar(0, rest, 0.6, bottom=industry, color=rest_color, edgecolor="white", linewidth=0.4, label=rest_label)
    ax.text(0, industry / 2, f"{industry:,.0f} Mt\n{industry / total:.0%}", ha="center", va="center",
            fontsize=9, color="white", fontweight="bold")
    ax.text(0, industry + rest / 2, f"{rest:,.0f} Mt\n{rest / total:.0%}", ha="center", va="center", fontsize=9)
    ax.text(0, total * 1.015, f"{total:,.0f} Mt", ha="center", va="bottom", fontsize=8)
    ax.set_xlim(-0.75, 0.75)
    ax.set_xticks([0])
    ax.set_xticklabels([str(year)])
    ax.set_ylim(0, total * 1.1)
    ax.set_ylabel("Emissions (Mt CO$_2$/a)")
    ax.set_title(f"CO$_2$ emissions in {year}", loc="left", fontsize=9.5, fontweight="bold", pad=5)
    fig.tight_layout()
    h, l = ax.get_legend_handles_labels()
    legend = report_legend(ax, h[::-1], l[::-1], fontsize=LEGEND_SIZE)
    print(f"  {year}: industry {industry:.0f}, rest {rest:.0f}, total {total:.0f}")
    save_figure(fig, name, extra_artists=[legend])
