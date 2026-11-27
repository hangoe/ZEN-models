"""Variable renewable generation and industrial electricity demand in 2050 (presentation).

Hourly values are the representative time steps of a run mapped back onto the 8760 hours
of the last modelled year (Results.get_full_ts), summed over all nodes, then averaged over
7-day blocks from 1 January. Generation is the electricity output of wind and solar;
industrial demand is the electricity input of the industry technologies, grouped into
production processes, kiln fuel and process heat. Electrolysis and DAC are not counted as
industry.

- vre_and_industry_electricity_flex: 2x2 slide figure of the flexible run: generation,
  industrial demand (the inflexible run's total as a dashed line) and the use of the
  flexibility options:
  TES discharge (GW heat) and DSM discharge (kt/day; ammonia and methanol, stored as
  energy, converted with their LHV as in thesis Fig. A4).
"""

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from ..names import CARRIER_COLORS, DISPLAY_NAMES, SECTOR_COLORS, display_name
from ..results import INDUSTRY_DSM_TECHS, INDUSTRY_TES_TECHS, Run, get_available_years, strip_sector_suffix
from ..style import (
    ETH_BRONZE,
    ETH_GREY,
    ETH_PURPLE,
    ETH_RED,
    REPORT_WIDTH,
    eth_tint,
    panel_title,
    report_legend,
    save_figure,
)
from .dsm_discharge import DSM_LHV_MWH_PER_T, PRODUCT_ORDER

VRE_TECHS = {"wind_onshore": CARRIER_COLORS["wind_onshore"],
             "wind_offshore": CARRIER_COLORS["wind_offshore"],
             "photovoltaics": CARRIER_COLORS["solar"]}

INDUSTRY_HEAT_ELEC = ["heat_pump_industry_0_100_water", "heat_pump_industry_100_150_water",
                      "heat_pump_industry_150_200_water", "heat_pump_industry_0_100_waste_heat",
                      "heat_pump_industry_100_150_waste_heat", "heat_pump_industry_150_200_waste_heat",
                      "electrode_boiler_industry"]
INDUSTRY_PROCESS_ELEC = ["glass_production", "ceramic_production", "paper_production", "food_production",
                         "EAF", "NG_DRI", "NG_DRI_CCS", "H2_DRI", "BF_BOF", "BF_BOF_CCS",
                         "cement_kiln", "cement_post_comb", "haber_bosch",
                         "methanol_from_natural_gas", "methanol_from_hydrogen", "methanol_from_biomass",
                         "olefin_from_naphtha", "olefin_from_methanol"]
# group label -> (colour, technologies), bottom to top
INDUSTRY_GROUPS = {
    "Production processes": (ETH_GREY, INDUSTRY_PROCESS_ELEC),
    "Kiln fuel (electrified)": (eth_tint(ETH_BRONZE, 0.4), ["electricity_to_kilnfuel"]),
    "Process heat (heat pumps,\nelectrode boilers)": (eth_tint(ETH_RED, 0.3), INDUSTRY_HEAT_ELEC),
}
TES_COLORS = {"industry_TES_water_0_100": eth_tint(ETH_PURPLE, 0.7),
              "industry_TES_water_100_150": eth_tint(ETH_PURPLE, 0.4),
              "industry_TES_steam_150_200": ETH_PURPLE}
TES_LABELS = {"industry_TES_water_0_100": "0–100 °C", "industry_TES_water_100_150": "100–150 °C",
              "industry_TES_steam_150_200": "150–200 °C"}
NO_FLEX_LINE = {"color": "black", "linestyle": (0, (4, 2)), "linewidth": 1.2}
PANEL_HEIGHT = 2.1  # in
SLIDE_FIG_SIZE = (12.0, 5.6)  # in, 2x2 flex figures for a 16:9 slide
LEGEND_SIZE = 7.5
TYPICAL_WEEK_START = "07-18"   # summer week of the week figures (strong day/night rhythm)


def _hourly(r, component: str, techs: list[str], year_index: int, carrier: str | None = None) -> pd.DataFrame:
    """Hourly flow of `techs` (sector-aggregated names) in year `year_index`, summed over
    nodes (and sectors): one column per technology, 8760 rows."""
    raw = r._results.get_total("capacity").index.get_level_values("technology").unique()
    index = {"technology": [t for t in raw if strip_sector_suffix(t) in techs]}
    if carrier is not None:
        index["carrier"] = carrier
    df = r._results.get_full_ts(component, index=index, year=year_index)
    df = df.groupby(df.index.get_level_values("technology").map(strip_sector_suffix)).sum()
    return df.T.reset_index(drop=True)


def _week_start(year: int) -> pd.Timestamp:
    return pd.Timestamp(f"{year}-{TYPICAL_WEEK_START}")


def _series(run: Run, component: str, techs: list[str], carrier: str | None = None,
            week: bool = False) -> pd.DataFrame:
    """_hourly of the last year, either as 7-day averages (from 1 January, indexed by the
    first day) or, with week=True, hourly for the typical week (TYPICAL_WEEK_START)."""
    years = get_available_years(run.results)
    df = _hourly(run.results, component, techs, len(years) - 1, carrier)
    df.index = pd.date_range(f"{years[-1]}-01-01", periods=len(df), freq="h")
    if week:
        start = _week_start(years[-1])
        return df.loc[start:start + pd.Timedelta(hours=167)]
    return df.resample("7D", origin="start").mean()


def weekly_vre(run: Run, week: bool = False) -> pd.DataFrame:
    df = _series(run, "flow_conversion_output", list(VRE_TECHS), "electricity", week)
    return df[[t for t in VRE_TECHS if t in df]]


def weekly_industry(run: Run, week: bool = False) -> pd.DataFrame:
    all_techs = [t for _, techs in INDUSTRY_GROUPS.values() for t in techs]
    df = _series(run, "flow_conversion_input", all_techs, "electricity", week)
    return pd.DataFrame({g: df[[t for t in techs if t in df]].sum(axis=1)
                         for g, (_, techs) in INDUSTRY_GROUPS.items()})


def _stack(ax, df: pd.DataFrame, colors: dict, labels: dict | None = None) -> None:
    ax.stackplot(df.index, *(df[c].values for c in df.columns), colors=[colors[c] for c in df.columns],
                 labels=[(labels or {}).get(c, c) for c in df.columns], linewidth=0)


def _legend(ax, n_stack: int):
    """Legend outside right: the stacked areas top-down (as drawn), then the lines."""
    h, l = ax.get_legend_handles_labels()
    return report_legend(ax, h[:n_stack][::-1] + h[n_stack:], l[:n_stack][::-1] + l[n_stack:],
                         fontsize=LEGEND_SIZE)


def _period_label(year: int, week: bool) -> str:
    if not week:
        return str(year)
    start = _week_start(year)
    return f"{start:%d}–{start + pd.Timedelta(days=6):%d %b} {year}"


def _generation_and_demand(axes, run: Run, year: int, no_flex_total: pd.Series | None = None,
                           week: bool = False) -> list:
    ax_g, ax_d = axes
    vre = weekly_vre(run, week)
    _stack(ax_g, vre, VRE_TECHS, DISPLAY_NAMES)
    ax_g.set_ylabel("Generation (GW)")
    panel_title(ax_g, f"(a) Wind and solar generation, {_period_label(year, week)}")

    ind = weekly_industry(run, week)
    _stack(ax_d, ind, {g: c for g, (c, _) in INDUSTRY_GROUPS.items()})
    if no_flex_total is not None:
        ax_d.plot(no_flex_total.index, no_flex_total.values, label="Total without flexibility", **NO_FLEX_LINE)
    ax_d.set_ylabel("Demand (GW)")
    panel_title(ax_d, f"(b) Industrial electricity demand, {_period_label(year, week)}")
    return [_legend(ax_g, len(vre.columns)), _legend(ax_d, len(ind.columns))]


def _finish(fig, axes, legends, year: int, name: str, week: bool = False, signed: tuple = ()) -> None:
    """signed: indices of axes with charge (< 0) and discharge (> 0), not clipped at 0."""
    for i, ax in enumerate(axes):
        if i in signed:
            ax.axhline(0, color="black", linewidth=0.6)
        else:
            ax.set_ylim(bottom=0)
    if week:
        start = _week_start(year)
        axes[-1].set_xlim(start, start + pd.Timedelta(days=7))
        axes[-1].xaxis.set_major_locator(mdates.DayLocator())
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    else:
        # 7-day blocks from 1 January: the last one starts on 31 December (day 365)
        axes[-1].set_xlim(pd.Timestamp(f"{year}-01-01"), pd.Timestamp(f"{year}-12-31"))
        axes[-1].xaxis.set_major_locator(mdates.MonthLocator())
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    save_figure(fig, name, extra_artists=legends)


def _storage_panel(ax, run: Run, techs: list[str], colors: dict, labels: dict, scale, week: bool) -> int:
    """Discharge stacked upwards; for the week also the charge, stacked downwards.
    `scale(df)` converts the flows to the plotted unit. Returns the number of legend entries."""
    dis = scale(_series(run, "flow_storage_discharge", techs, week=week))
    keep = [t for t in colors if t in dis and dis[t].abs().max() > 1e-3]
    if week:
        cha = scale(_series(run, "flow_storage_charge", techs, week=week))
        keep = [t for t in colors if t in dis and max(dis[t].abs().max(), cha[t].abs().max()) > 1e-3]
        ax.stackplot(cha.index, *(-cha[t].values for t in keep), colors=[colors[t] for t in keep],
                     linewidth=0, alpha=0.6)
    _stack(ax, dis[keep], colors, labels)
    return len(keep)


def _dsm_kt(df: pd.DataFrame, per: float) -> pd.DataFrame:
    """DSM flows in kt per `per` hours (ammonia and methanol: GWh -> kt with their LHV)."""
    df = df.copy()
    for t, mwh_per_t in DSM_LHV_MWH_PER_T.items():
        if t in df:
            df[t] = df[t] / mwh_per_t
    return df * per


def vre_and_industry_electricity_flex(no_flex_run: Run, flex_run: Run, name: str, week: bool = False) -> None:
    """2x2 slide figure. week=False: weekly averages over the year, storage discharge only.
    week=True: the typical week hourly, storage charge (< 0, lighter) and discharge (> 0)."""
    year = get_available_years(flex_run.results)[-1]
    # 2x2 for a slide: (a) generation | (b) demand / (c) TES | (d) DSM, legends right of each panel
    fig, axes = plt.subplots(2, 2, figsize=SLIDE_FIG_SIZE, sharex=True)
    axes = axes.ravel()
    legends = _generation_and_demand(axes[:2], flex_run, year,
                                     no_flex_total=weekly_industry(no_flex_run, week).sum(axis=1), week=week)

    n = _storage_panel(axes[2], flex_run, INDUSTRY_TES_TECHS, TES_COLORS, TES_LABELS, lambda df: df, week)
    axes[2].set_ylabel("Charge (−) / discharge (+)\n(GW)" if week else "Discharge (GW)")
    panel_title(axes[2], "(c) Thermal energy storage" + ("" if week else " discharge"))
    legends.append(_legend(axes[2], n))

    dsm_colors = {t: SECTOR_COLORS[t.replace("_DSM", "")] for t in PRODUCT_ORDER}
    per, unit = (1, "kt/h") if week else (24, "kt/day")
    n = _storage_panel(axes[3], flex_run, INDUSTRY_DSM_TECHS, dsm_colors, {t: display_name(t) for t in PRODUCT_ORDER},
                       lambda df: _dsm_kt(df, per), week)
    axes[3].set_ylabel(f"Charge (−) / discharge (+)\n({unit})" if week else f"Discharge ({unit})")
    panel_title(axes[3], "(d) Demand-side management (shifted production)"
                if week else "(d) Demand-side management discharge (shifted production)")
    legends.append(_legend(axes[3], n))

    fig.subplots_adjust(left=0.07, right=0.86, bottom=0.08, top=0.93, wspace=0.78, hspace=0.32)
    _finish(fig, axes, legends, year, name, week, signed=(2, 3) if week else ())


def vre_seasonal_and_week(run: Run, name: str) -> None:
    """(a) weekly-average wind and solar generation over the last year (as in
    the flex figure), with the week of (b) shaded; (b) that week hourly."""
    years = get_available_years(run.results)
    year = years[-1]
    hourly = _hourly(run.results, "flow_conversion_output", list(VRE_TECHS), len(years) - 1, "electricity")
    hourly.index = pd.date_range(f"{year}-01-01", periods=len(hourly), freq="h")
    hourly = hourly[[t for t in VRE_TECHS if t in hourly]]
    weekly = hourly.resample("7D", origin="start").mean()
    start = pd.Timestamp(f"{year}-{TYPICAL_WEEK_START}")
    week = hourly.loc[start:start + pd.Timedelta(hours=167)]

    fig, (ax_a, ax_b) = plt.subplots(2, 1, figsize=(REPORT_WIDTH, 2 * PANEL_HEIGHT + 0.5))
    _stack(ax_a, weekly, VRE_TECHS, DISPLAY_NAMES)
    ax_a.axvspan(start, start + pd.Timedelta(days=7), color="black", alpha=0.12, linewidth=0)
    ax_a.annotate("(b)", xy=(start + pd.Timedelta(days=3.5), ax_a.get_ylim()[1]), ha="center", va="bottom",
                  fontsize=8, annotation_clip=False)
    ax_a.set_xlim(pd.Timestamp(f"{year}-01-01"), pd.Timestamp(f"{year}-12-31"))
    ax_a.xaxis.set_major_locator(mdates.MonthLocator())
    ax_a.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    panel_title(ax_a, f"(a) Seasonal pattern: weekly average, {year}")

    _stack(ax_b, week, VRE_TECHS, DISPLAY_NAMES)
    ax_b.set_xlim(week.index[0], week.index[-1] + pd.Timedelta(hours=1))
    ax_b.xaxis.set_major_locator(mdates.DayLocator())
    ax_b.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    panel_title(ax_b, f"(b) Typical summer week: hourly, {start:%d} – {start + pd.Timedelta(days=6):%d %b} {year}")

    for ax in (ax_a, ax_b):
        ax.set_ylim(bottom=0)
        ax.set_ylabel("Generation (GW)")
    fig.align_ylabels([ax_a, ax_b])
    fig.tight_layout(h_pad=1.5)
    legend = _legend(ax_a, len(weekly.columns))
    save_figure(fig, name, extra_artists=[legend])
