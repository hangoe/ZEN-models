"""Compare Crystal Ball v8.0 vs v9.0, "No flexibility" scenario only.

v9.0's defining change (ZEN-creator commit 1687533, "first version of glass/
ceramic fuel switch") replaces v8.0's ceramic_production/glass_production
kilns -- which combusted natural_gas directly, with no alternative -- with a
new intermediate carrier `fuel_to_kiln`, produced by three interchangeable
technologies: natural_gas_to_kilnfuel, electricity_to_kilnfuel and
hydrogen_to_kilnfuel. This is a genuine new fuel-switching option that did
not exist in v8.0. These 3 figures visualize (1) the kiln fuel mix itself,
(2) a temporary, fully-transient BEV-to-ICE transport mode shift in
2034-2038 that this change appears to trigger (see fig_crude_oil_transport_shift's
docstring for the root-cause chain), and its knock-on effect on refining
throughput/crude_oil emissions, and (3) total system emissions -- comparing
only the "No flexibility" euler runs of each version, per user request.

Run standalone: python scripts/compare_version_v8_v9.py
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import matplotlib.pyplot as plt
import pandas as pd

from figure_settings import (
    EULER_ROOT,
    SCENARIO_PALETTE,
    Run,
    apply_font_mode,
    eth_tint,
    get_available_years,
    load_results,
)

# Match the SI print figures' font (see figure_settings.FONT_MODE) for visual
# consistency with the rest of SI_results/ — toggle FONT_MODE there to switch
# every figure script in this repo (report/Computer Modern vs. presentation/Arial) at once.
apply_font_mode()
from figures_by_scenario import _annual_series, get_emissions_by_carrier

FIGURES_DIR = REPO_ROOT / "data" / "outputs" / "figures" / "SI_results" / "archive"

RUN_FOLDERS = [
    ("Crystal_Ball_ind_heat_v8_0_no_flexibility_2020_15a_2a_interval_10ts", "v8.0"),
    ("Crystal_Ball_ind_heat_v9_0_no_flexibility_2020_15a_2a_interval_10ts", "v9.0"),
]

# ETH corporate-design colors only (SCENARIO_PALETTE), per repo convention for
# print-ready SI figures -- see feedback memory "SI print figures must use
# ETH-only palette, never the dashboard's generic COLOR_MAP".
ETH_BLUE, ETH_PETROL, ETH_GREEN, ETH_BRONZE, ETH_RED, ETH_PURPLE, ETH_GREY = SCENARIO_PALETTE

COLOR_V8 = ETH_BLUE
COLOR_V9 = ETH_RED


def savefig(fig: plt.Figure, name: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{name}.svg"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {path}")


def load_runs() -> list[Run]:
    runs = []
    for folder, label in RUN_FOLDERS:
        results = load_results(EULER_ROOT, folder)
        color = COLOR_V8 if label == "v8.0" else COLOR_V9
        runs.append(Run(name=folder, label=label, mode="euler", results=results, color=color))
    return runs


def _stacked_by_year(ax: plt.Axes, df: pd.DataFrame, color_map: dict, title: str, unit: str,
                      show_legend: bool = False, show_total: bool = True) -> None:
    """Local stacked-bar-over-years plotter (categories x years), using a
    figure-local ETH-only color_map instead of the shared dashboard palette."""
    years = df.columns.tolist()
    cats = df.index.tolist()
    bar_width = 0.65
    for yi, year in enumerate(years):
        bottom = 0.0
        for cat in cats:
            val = df.loc[cat, year]
            if val <= 1e-6:
                continue
            ax.bar(yi, val, bar_width, bottom=bottom, color=color_map.get(cat, ETH_GREY),
                   label=cat, edgecolor="white", linewidth=0.4)
            bottom += val
        if show_total:
            ax.text(yi, bottom, f"{bottom:,.0f}", ha="center", va="bottom",
                    fontsize=6, fontweight="bold")
    ax.set_xticks(range(len(years)))
    ax.set_xticklabels([str(y) for y in years], fontsize=8, rotation=45, ha="right")
    ax.set_ylabel(unit, fontsize=10)
    ax.set_title(title, fontsize=11, fontweight="bold")
    if show_legend:
        handles, labels = ax.get_legend_handles_labels()
        seen = set()
        h2, l2 = [], []
        for h, l in zip(handles, labels):
            if l not in seen:
                h2.append(h)
                l2.append(l)
                seen.add(l)
        ax.legend(h2, l2, bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8, frameon=False)


# ── Figure 1: kiln fuel switch ──────────────────────────────────────────────

KILN_FUEL_COLORS = {
    "Natural gas": ETH_BRONZE,
    "Electricity": ETH_BLUE,
    "Hydrogen": ETH_PETROL,
}


def kiln_fuel_by_year(r, years: list[int]) -> pd.DataFrame:
    """Energy supplied to ceramic+glass kilns, split by fuel source.

    v8.0: glass_production/ceramic_production burn natural_gas directly
    (flow_conversion_input). v9.0: glass_production/ceramic_production draw
    from the fuel_to_kiln carrier, produced by 3 alternative technologies
    (flow_conversion_output); ceramic_production also keeps a small residual
    direct natural_gas input (see ZEN-creator diff), added into "Natural gas"
    here so totals stay comparable across versions."""
    rows = {"Natural gas": pd.Series(0.0, index=years),
            "Electricity": pd.Series(0.0, index=years),
            "Hydrogen": pd.Series(0.0, index=years)}

    fi = r.get_total("flow_conversion_input")
    if "natural_gas" in fi.index.get_level_values("carrier"):
        ng = fi.xs("natural_gas", level="carrier")
        for tech in ("glass_production", "ceramic_production"):
            if tech in ng.index.get_level_values("technology"):
                s = ng.xs(tech, level="technology").sum()
                rows["Natural gas"] = rows["Natural gas"].add(
                    pd.Series({int(y): float(s.get(y, s.get(str(y), 0.0))) for y in years}), fill_value=0.0)

    fo = r.get_total("flow_conversion_output")
    if "fuel_to_kiln" in fo.index.get_level_values("carrier"):
        sub = fo.xs("fuel_to_kiln", level="carrier")
        mapping = {
            "natural_gas_to_kilnfuel": "Natural gas",
            "electricity_to_kilnfuel": "Electricity",
            "hydrogen_to_kilnfuel": "Hydrogen",
        }
        for tech, cat in mapping.items():
            if tech in sub.index.get_level_values("technology"):
                s = sub.xs(tech, level="technology").sum()
                rows[cat] = rows[cat].add(
                    pd.Series({int(y): float(s.get(y, s.get(str(y), 0.0))) for y in years}), fill_value=0.0)

    return pd.DataFrame(rows).T[years]


def fig_kiln_fuel_switch(runs: list[Run]) -> None:
    years = get_available_years(runs[0].results)
    dfs = [kiln_fuel_by_year(r.results, years) for r in runs]

    fig, axes = plt.subplots(1, 2, figsize=(13, 6), sharey=True)
    fig.suptitle(
        "Ceramic & Glass Kiln Fuel Supply -- v8.0 vs v9.0 (No flexibility)",
        fontsize=13, fontweight="bold",
    )
    for ax, r, df in zip(axes, runs, dfs):
        _stacked_by_year(ax, df, KILN_FUEL_COLORS, r.label, "GWh/yr",
                          show_legend=(ax is axes[-1]))
    fig.text(0.5, -0.02,
              "v9.0 introduces fuel_to_kiln, a switchable intermediate carrier (natural gas / electricity / hydrogen)\n"
              "replacing v8.0's natural-gas-only kiln combustion in ceramic_production and glass_production.",
              ha="center", fontsize=8, style="italic")
    fig.tight_layout(rect=[0, 0.03, 1, 0.93])
    savefig(fig, "compare_version_kiln_fuel_switch")


# ── Figure 2: why crude_oil emissions spike (2034-2038 BEV/ICE mode shift) ──
#
# Root-caused by direct data investigation (not the kiln fuel switch itself):
# passenger_mileage demand is bit-identical between v8.0/v9.0 every year
# (get_total("demand")). But BEV's capacity_addition is ~50 GW lower in 2034
# and BEV capacity ends up ~63 GW short by 2036 in v9.0 -- a temporary ~2-4
# year delay in the BEV buildout ramp, fully caught up by 2040 (both versions
# converge on identical 904.13 GW BEV capacity from 2040 onward). The exact
# same mileage is covered by ICE_petrol/ICE_diesel in the interim
# (+162,655.75 / +88,717.12 mileage-units in 2036, summing to exactly BEV's
# -251,372.87 shortfall). That extra ICE mileage needs more gasoline/diesel,
# so refining throughput (crude_oil input) rises (+164,948 GWh in 2036),
# driving crude_oil emissions up by as much as +43.5 Mton in 2036 alone before
# fully resolving by 2040 -- a transient side effect of a delayed BEV rollout,
# not a permanent structural change.
#
# NOT a deployment/diffusion-rate barrier (ruled out, not just unconfirmed):
# BEV's own diffusion-limit constraint has deep slack in 2034 in BOTH
# versions -- reconstructing constraint_technology_diffusion_limit's RHS by
# hand (((1+max_diffusion_rate)^dy - 1) * capacity_previous, ignoring the
# smaller market-share/spillover terms) gives ~485 GW allowed vs. only ~94 GW
# actually built in v9.0 2034 -- nowhere near binding. capacity_addition_max
# and capacity_limit are both inf (unconstrained) for BEV too. This rules out
# the "competing for constrained buildout headroom" story that explained the
# heat-pump case in addenda #9-11 -- that mechanism does NOT apply here. The
# mode shift is therefore most likely a genuine cost-optimal reallocation
# (e.g. a relative electricity-vs-oil-product cost shift from kiln
# electrification's added demand), not a hard constraint -- but pinning down
# the exact price mechanism needs actual dual values, which these runs don't
# have (`solver.json`: save_duals=false for both v8.0 and v9.0 -- confirmed
# via `Results.get_component_names("dual")` returning []). Re-running with
# save_duals=True and selecting the relevant carrier-balance/capacity duals
# would give a real answer; not done here since it requires a new Euler run.

TRANSPORT_TECH_COLORS = {
    "BEV": ETH_GREEN,
    "ICE_petrol": ETH_GREY,
    "ICE_diesel": eth_tint(ETH_GREY, 0.4),
}


def _tech_output_by_year(r, tech: str, years: list[int]) -> pd.Series:
    fo = r.get_total("flow_conversion_output")
    if tech not in fo.index.get_level_values("technology"):
        return pd.Series(0.0, index=years)
    s = fo.xs(tech, level="technology").sum()
    return pd.Series({int(y): float(s.get(y, s.get(str(y), 0.0))) for y in years})


def fig_crude_oil_transport_shift(runs: list[Run]) -> None:
    years = get_available_years(runs[0].results)
    r8, r9 = runs[0].results, runs[1].results

    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    fig.suptitle(
        "Why Crude Oil Emissions Spike -- Temporary BEV to ICE Mode Shift, v9.0 vs v8.0 (No flexibility)",
        fontsize=13, fontweight="bold",
    )

    # Panel A: BEV / ICE_petrol / ICE_diesel output, both versions overlaid.
    # Two SEPARATE legends (color = technology, linestyle = version) instead
    # of one combined 6-entry legend ("BEV (v8.0)", "BEV (v9.0)", ...) -- the
    # combined legend read as 6 similar-looking labels and made it hard to
    # tell which line was which version at a glance.
    ax = axes[0]
    for tech, color in TRANSPORT_TECH_COLORS.items():
        s8 = _tech_output_by_year(r8, tech, years)
        s9 = _tech_output_by_year(r9, tech, years)
        ax.plot(years, s8.values / 1e6, color=color, linestyle="--", marker="o", markersize=3)
        ax.plot(years, s9.values / 1e6, color=color, linestyle="-", marker="o", markersize=3)
    ax.set_ylabel("Passenger mileage output [Mpkm/yr]", fontsize=9)
    ax.set_title("Transport mode output\n(identical mileage demand both versions)",
                 fontsize=10, fontweight="bold")
    ax.grid(alpha=0.3)

    tech_handles = [plt.Line2D([], [], color=color, linewidth=2, label=tech)
                    for tech, color in TRANSPORT_TECH_COLORS.items()]
    tech_legend = ax.legend(handles=tech_handles, title="Technology", loc="upper left",
                             fontsize=8, title_fontsize=8, frameon=False)
    ax.add_artist(tech_legend)
    version_handles = [
        plt.Line2D([], [], color="black", linestyle="--", marker="o", markersize=3, label="v8.0"),
        plt.Line2D([], [], color="black", linestyle="-", marker="o", markersize=3, label="v9.0"),
    ]
    ax.legend(handles=version_handles, title="Version", loc="upper left",
              bbox_to_anchor=(0.0, 0.62), fontsize=8, title_fontsize=8, frameon=False)

    # Panel B: resulting crude_oil emissions delta
    ax = axes[1]
    e8 = r8.get_total("carbon_emissions_carrier").xs("crude_oil", level="carrier").sum()[years]
    e9 = r9.get_total("carbon_emissions_carrier").xs("crude_oil", level="carrier").sum()[years]
    delta = e9 - e8
    ax.bar(years, delta.values, width=1.4, color=ETH_RED, edgecolor="white", linewidth=0.4)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("Mton CO$_2$eq / yr", fontsize=9)
    ax.set_title(r"Resulting crude_oil emissions $\Delta$" + "\n(v9.0 - v8.0)", fontsize=10, fontweight="bold")
    peak_year = delta.idxmax()
    ax.annotate(f"peak: {delta.max():,.1f} Mton ({peak_year})",
                xy=(peak_year, delta.max()), xytext=(0.98, 0.92),
                textcoords="axes fraction", ha="right", va="top", fontsize=8,
                arrowprops=dict(arrowstyle="->", color="black", lw=0.8,
                                 shrinkA=0, shrinkB=4))
    ax.grid(alpha=0.3)

    fig.text(0.5, -0.03,
              "Both versions converge on identical BEV capacity (904.13 GW) and mode split by 2040 --\n"
              "the crude oil / emissions spike is a temporary 2034-2038 transition effect, not a lasting change.",
              ha="center", fontsize=8, style="italic")
    fig.tight_layout(rect=[0, 0.03, 1, 0.92])
    savefig(fig, "compare_version_crude_oil_transport_shift")


# ── Figure 3: total system emissions ────────────────────────────────────────

SNAPSHOT_YEAR = 2036  # same relative-horizon snapshot convention as generate_si_figures.py's YEAR

EMISSIONS_CARRIER_COLORS = {
    "natural_gas": ETH_BRONZE,
    "crude_oil": ETH_GREY,
    "lng": eth_tint(ETH_BRONZE, 0.4),
    "hard_coal": ETH_PURPLE,
    "waste": ETH_GREEN,
    "lignite": eth_tint(ETH_GREY, 0.4),
}


def fig_emissions(runs: list[Run]) -> None:
    years = get_available_years(runs[0].results)
    em = [_annual_series(r.results, "carbon_emissions_annual", years) for r in runs]
    delta = em[1] - em[0]

    fig, axes = plt.subplots(1, 3, figsize=(19, 6), gridspec_kw={"width_ratios": [1, 1, 1]})
    fig.suptitle(
        "Total System Emissions -- v8.0 vs v9.0 (No flexibility)",
        fontsize=13, fontweight="bold",
    )

    ax = axes[0]
    for r, s in zip(runs, em):
        ax.plot(s.index, s.values, marker="o", color=r.color, label=r.label)
    ax.axhline(0, color="black", linewidth=0.6)
    ax.set_ylabel("Mton CO$_2$eq / yr", fontsize=10)
    ax.set_title("Annual system emissions", fontsize=11, fontweight="bold")
    ax.legend(fontsize=9, frameon=False)
    ax.grid(alpha=0.3)

    ax = axes[1]
    colors = [ETH_GREEN if v < 0 else ETH_RED for v in delta.values]
    ax.bar(delta.index, delta.values, width=1.4, color=colors, edgecolor="white", linewidth=0.4)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("Mton CO$_2$eq / yr", fontsize=10)
    ax.set_title(r"$\Delta$ Annual emissions (v9.0 - v8.0)", fontsize=11, fontweight="bold")
    ax.grid(alpha=0.3)

    ax = axes[2]
    e8 = get_emissions_by_carrier(runs[0].results, SNAPSHOT_YEAR)
    e9 = get_emissions_by_carrier(runs[1].results, SNAPSHOT_YEAR)
    cats = sorted(set(e8.index) | set(e9.index), key=lambda c: -max(e8.get(c, 0), e9.get(c, 0)))
    cat_delta = pd.Series({c: e9.get(c, 0.0) - e8.get(c, 0.0) for c in cats})
    colors = [EMISSIONS_CARRIER_COLORS.get(c, ETH_GREY) for c in cat_delta.index]
    ax.barh(cat_delta.index, cat_delta.values, color=colors, edgecolor="white", linewidth=0.4)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.invert_yaxis()
    ax.set_xlabel("Mton CO$_2$eq", fontsize=10)
    ax.set_title(rf"$\Delta$ by carrier, {SNAPSHOT_YEAR}", fontsize=11, fontweight="bold")

    fig.tight_layout(rect=[0, 0, 1, 0.93])
    savefig(fig, "compare_version_emissions")


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    print("Loading v8.0 and v9.0 'No flexibility' runs ...")
    runs = load_runs()
    for r in runs:
        print(f"  {r.label}: {r.name}")

    fig_kiln_fuel_switch(runs)
    fig_crude_oil_transport_shift(runs)
    fig_emissions(runs)


if __name__ == "__main__":
    main()
