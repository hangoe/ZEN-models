"""Total system cost, drilled down sector -> industries -> low-temperature heat (thesis Fig. 3).

Cumulative discounted total system cost (the objective, net_present_cost) of
ZEN-Europe-Legacy and ZEN-Europe-No-Flex, one panel each, in three rows: (top) the whole
system by sector, (middle) the industries by branch, (bottom) low-temperature industrial
heating by technology. Technology CAPEX and OPEX are discounted per year and summed per
technology, then grouped. Carrier (fuel, import) cost is not tied to a technology and
forms its own group; carbon cost is about zero (the carbon budget is a hard constraint).
Technologies not listed in a group fall into "Others" (energy conversion and supply,
CCS, hydrogen, heat for buildings, ...). The lower rows are zoomed by one factor per row,
the same in both panels (magnifier and scale bar). ZEN-Europe-Legacy has no new industry
sectors and no industrial heating technologies, so its lower rows are not like for like.
"""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import to_rgba
from matplotlib.patches import Patch

from ..names import CARRIER_COLORS, HEAT_SUPPLY_COLOR_MAP, HEAT_SUPPLY_STACK_ORDER, SECTOR_COLORS, display_name
from ..results import (
    INDUSTRY_DSM_TECHS,
    INDUSTRY_HEATING_TECHS,
    INDUSTRY_TES_TECHS,
    Run,
    discount_factors,
    get_annual_cost,
    get_annual_total_cost,
    get_available_years,
    get_capex_by_technology,
    get_opex_by_technology,
)
from ..style import ETH_GREY, REPORT_WIDTH, comma_axis, eth_tint, save_figure

SECTOR_TECHS = {
    "Transport": ["BEV", "ICE_diesel", "ICE_petrol", "HDT_BET", "HDT_diesel", "HDT_FCEV", "fuel_cell",  # road
                  "ammonia_ICE_ship", "diesel_ICE_ship", "hydrogen_FC_ship", "methanol_ICE_ship"],  # ships
    "Power generation": [
        "photovoltaics", "wind_onshore", "wind_offshore", "nuclear", "reservoir_hydro", "run-of-river_hydro",
        "lignite_coal_plant", "hard_coal_plant", "oil_plant", "natural_gas_turbine", "natural_gas_turbine_CCS",
        "biomass_plant", "biomass_plant_CCS", "waste_plant",
        "battery", "pumped_hydro", "power_line",  # storage and grid grouped with power
    ],
}
# Industries by branch. Heating (incl. TES) and DSM are their own groups, so DSM is not
# counted in its product's branch.
INDUSTRY_GROUPS = {
    "Steel": ["BF_BOF", "BF_BOF_CCS", "EAF", "NG_DRI", "NG_DRI_CCS", "H2_DRI"],
    "Cement": ["cement_kiln", "cement_post_comb", "biomass_to_cement_fuel", "coal_to_cement_fuel",
               "hydrogen_to_cement_fuel", "waste_to_cement_fuel"],
    "Chemicals": ["haber_bosch", "olefin_from_methanol", "olefin_from_naphtha", "methanol_from_biomass",
                  "methanol_from_hydrogen", "methanol_from_natural_gas"],
    "Paper": ["paper_production"],
    "Food": ["food_production"],
    "Glass & ceramics": ["glass_production", "ceramic_production", "glass_post_comb", "ceramic_post_comb"],
    "Low-T heating (incl. TES)": INDUSTRY_HEATING_TECHS + INDUSTRY_TES_TECHS,
    "DSM (all products)": INDUSTRY_DSM_TECHS,
}
# Top row in greys with only "Industries" highlighted (near-black navy; red is the waste
# boiler's colour in the heating row); the industry row in SECTOR_COLORS; the heating row
# in the heat-supply colours.
HIGHLIGHT = "#1F2A3A"
SECTOR_ROW_COLORS = {
    "Transport": eth_tint(ETH_GREY, 0.2), "Power generation": eth_tint(ETH_GREY, 0.45),
    "Industries": HIGHLIGHT, "Others": eth_tint(ETH_GREY, 0.65),
    "Imported carriers": eth_tint(ETH_GREY, 0.82),
}
INDUSTRY_ROW_COLORS = {
    "Steel": SECTOR_COLORS["steel"], "Cement": SECTOR_COLORS["cement"], "Chemicals": SECTOR_COLORS["chemicals"],
    "Paper": SECTOR_COLORS["paper"], "Food": SECTOR_COLORS["food"], "Glass & ceramics": SECTOR_COLORS["glass"],
    "Low-T heating (incl. TES)": HIGHLIGHT, "DSM (all products)": eth_tint(HIGHLIGHT, 0.6),
}
ZOOM_FILL = 0.82  # the largest zoomed bar of a row type spans this share of the axis
LEGEND_HEIGHT = 1.84  # in, legend block below the panels
PANEL_HEIGHT_PER_UNIT = 0.763  # in per y unit of a panel


def _bn(v: float) -> str:
    return f"{v:,.0f} bn" if abs(v) >= 10 else f"{v:,.1f} bn" if abs(v) >= 0.1 else f"{v:.2f} bn"


def _technology_costs(r: Run) -> tuple[pd.Series, float, float]:
    """(discounted CAPEX + OPEX per technology, total cost, carrier cost), bn EUR."""
    years = get_available_years(r.results)
    dfac = discount_factors(r.results, years)
    c = pd.Series(dtype=float)
    for y in years:
        cy = get_capex_by_technology(r.results, y).add(get_opex_by_technology(r.results, y), fill_value=0.0)
        c = c.add(cy * float(dfac.get(y, 0.0)), fill_value=0.0)
    total = float(get_annual_total_cost(r.results, years, discount=True).sum()) / 1000
    carrier = float(get_annual_cost(r.results, years, "cost_carrier", discount=True).sum()) / 1000
    return c / 1000, total, carrier


def cost_breakdown(legacy_run: Run, no_flex_run: Run, name: str) -> None:
    runs = [legacy_run, no_flex_run]
    labels = [r.label for r in runs]
    costs, npc_totals, carrier_tot = zip(*(_technology_costs(r) for r in runs))

    def grp(c: pd.Series, techs: list[str]) -> float:
        return float(c.reindex(techs).fillna(0.0).sum())

    industry_techs = [t for ts in INDUSTRY_GROUPS.values() for t in ts]
    sector_df = pd.DataFrame({
        lab: {**{s: grp(c, ts) for s, ts in SECTOR_TECHS.items()}, "Industries": grp(c, industry_techs)}
        for lab, c in zip(labels, costs)})
    sector_df.loc["Others"] = [float(c.sum()) for c in costs] - sector_df.sum()
    sector_df.loc["Imported carriers"] = list(carrier_tot)
    sector_df = sector_df.loc[list(SECTOR_ROW_COLORS)]
    ind_df = pd.DataFrame({lab: {g: grp(c, ts) for g, ts in INDUSTRY_GROUPS.items()}
                           for lab, c in zip(labels, costs)})
    heat_techs = [t for t in HEAT_SUPPLY_STACK_ORDER if any(t in c.index for c in costs)] \
        + [t for t in INDUSTRY_TES_TECHS if any(t in c.index for c in costs)]
    heat_df = pd.DataFrame({lab: {t: float(c.get(t, 0.0)) for t in heat_techs}
                            for lab, c in zip(labels, costs)})
    tes_rows = [t for t in heat_df.index if t in INDUSTRY_TES_TECHS]  # all ~0: one legend entry
    if tes_rows:
        heat_df.loc["industry_TES"] = heat_df.loc[tes_rows].sum()
        heat_df = heat_df.drop(index=tes_rows)
    heat_df = heat_df[heat_df.abs().sum(axis=1) > 1e-6]
    heat_colors = {**HEAT_SUPPLY_COLOR_MAP, "industry_TES": CARRIER_COLORS["tes"]}

    x_max = max(npc_totals) * 1.13  # one shared bn-EUR scale for every bar

    def draw_row(ax, y, df_col, colors, names, min_label=0.05, f=1.0):
        """One bar with lengths value * f (f: zoom factor of the row). Segment labels: share
        of this bar and absolute value; the bar total behind the bar.
        Returns {name: (left, right)} in axis units."""
        tot = df_col.sum()
        pos, left = {}, 0.0
        for n in df_col.index:
            v = float(df_col[n])
            if v <= 0:
                continue
            ax.barh(y, v * f, left=left, height=0.56, color=colors[n], edgecolor="white", linewidth=0.6)
            if v * f / x_max >= min_label:  # narrower segments: identified via the legend
                label = names(n)
                r_, g_, b_ = to_rgba(colors[n])[:3]
                txt_color = "black" if 0.299 * r_ + 0.587 * g_ + 0.114 * b_ > 0.62 else "white"
                ax.text(left + v * f / 2, y, (f"{label}\n" if label else "") + f"{100 * v / tot:.1f} %\n{_bn(v)}",
                        ha="center", va="center", fontsize=6.5, color=txt_color, linespacing=1.1)
            pos[n] = (left, left + v * f)
            left += v * f
        ax.text(left + 0.006 * x_max, y + (0.14 if f != 1.0 else 0), _bn(tot), ha="left", va="center",
                fontsize=7.5, fontweight="bold")
        return pos

    def connector(ax, y_top, y_bot, seg, tot_bot):
        for xa, xb in zip(seg, (0, tot_bot)):
            ax.plot([xa, xb], [y_top - 0.25, y_bot + 0.25], color="#555555", linestyle="--", linewidth=0.6)

    f_ind = ZOOM_FILL * x_max / max(float(ind_df[lab].sum()) for lab in labels)
    f_heat = ZOOM_FILL * x_max / max(float(heat_df[lab].sum()) for lab in labels)

    def magnifier(ax, y, f, x0):
        """Magnifier icon, zoom factor and scale bar below the row's total label (at x0)."""
        ax.plot([x0 + 0.01 * x_max], [y - 0.06], marker="o", markersize=5.5, mfc="none", mec="#333333",
                mew=1.0, clip_on=False)
        ax.plot([x0 + 0.017 * x_max, x0 + 0.025 * x_max], [y - 0.13, y - 0.22], color="#333333", lw=1.4,
                solid_capstyle="round")
        ax.text(x0 + 0.035 * x_max, y - 0.06, f"zoom ×{f:.0f}", fontsize=6.5, va="center", ha="left")
        length = min([1, 2, 5, 10, 20, 50, 100, 200], key=lambda b: abs(b * f - 0.08 * x_max))
        ax.plot([x0, x0 + length * f], [y - 0.32, y - 0.32], color="#333333", lw=1.2)
        ax.text(x0 + length * f + 0.005 * x_max, y - 0.32, f"{length} bn", fontsize=6.5, va="center")

    # panels without a heating row (ZEN-Europe-Legacy) are cropped and get less height
    y_lo = [-0.45 if float(heat_df[lab].sum()) > 1e-6 else 0.55 for lab in labels]
    ratios = [3.1 - lo for lo in y_lo]
    fig_h = LEGEND_HEIGHT + PANEL_HEIGHT_PER_UNIT * sum(ratios)
    lf = LEGEND_HEIGHT / fig_h  # legend block's share of the figure height
    fig, axes = plt.subplots(len(runs), 1, figsize=(REPORT_WIDTH, fig_h), gridspec_kw={"height_ratios": ratios})
    for k, (ax, lab) in enumerate(zip(axes, labels)):
        heat_k = float(heat_df[lab].sum())
        ax.text(0, 2.62, f"({'abc'[k]}) {lab}", fontsize=9.5, fontweight="bold", va="bottom")
        pos1 = draw_row(ax, 2, sector_df[lab], SECTOR_ROW_COLORS,
                        lambda n: n.replace("Power generation", "Power\ngeneration")
                        .replace("Imported carriers", "Imported\ncarriers"), min_label=0.09)
        ind_tot = float(ind_df[lab].sum())
        connector(ax, 2, 1, pos1["Industries"], ind_tot * f_ind)
        pos2 = draw_row(ax, 1, ind_df[lab], INDUSTRY_ROW_COLORS,
                        lambda n: n.replace(" (incl. TES)", "").replace(" (all products)", "")
                        .replace("Glass & ceramics", "Glass &\nceramics").replace("Low-T heating", "Low-T\nheating")
                        .replace("Chemicals", "Chem-\nicals"),
                        f=f_ind, min_label=0.075)
        magnifier(ax, 1, f_ind, ind_tot * f_ind + 0.006 * x_max)
        if heat_k > 1e-6:
            connector(ax, 1, 0, pos2["Low-T heating (incl. TES)"], heat_k * f_heat)
            draw_row(ax, 0, heat_df[lab], heat_colors, lambda t: "", min_label=0.06, f=f_heat)
            magnifier(ax, 0, f_heat, heat_k * f_heat + 0.006 * x_max)
        ax.set_xlim(0, x_max)
        ax.set_ylim(y_lo[k], 3.1)
        ax.set_yticks([])
        ax.spines[["left", "right", "top"]].set_visible(False)
        if k < len(labels) - 1:
            ax.spines["bottom"].set_visible(False)
            ax.set_xticks([])
        else:
            ax.set_xlabel("Cumulative discounted cost (bn EUR); axis for the top bars only, "
                          "lower rows zoomed (see scale bars)")
            comma_axis(ax, "x")
    row_handles = ([Patch(color=c, label=n) for n, c in SECTOR_ROW_COLORS.items()]
                   + [Patch(color=c, label=n) for n, c in INDUSTRY_ROW_COLORS.items()
                      if float(ind_df.loc[n].abs().sum()) > 1e-6])
    heat_handles = [Patch(color=heat_colors[n], label=display_name(n)) for n in heat_df.index[::-1]]
    fig.tight_layout(rect=[0, lf, 1, 1], h_pad=0.4)
    legend_kw = dict(loc="upper left", fontsize=7, frameon=False, title_fontsize=7.5,
                     handlelength=1.2, columnspacing=1.2, alignment="left")
    fig.legend(handles=row_handles, bbox_to_anchor=(0.0, 0.95 * lf), ncol=3,
               title="System row (top) and industries row (middle)", **legend_kw)
    fig.legend(handles=heat_handles, bbox_to_anchor=(0.0, 0.49 * lf), ncol=3,
               title="Low-temperature heating row (bottom)", **legend_kw)
    save_figure(fig, name)
