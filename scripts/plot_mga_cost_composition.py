"""fig7_cost_composition: baseline (cost-optimal, z*) CAPEX-cum proxy next to
net_present_cost (with its own CAPEX/OPEX/carrier/carbon composition), 3ts
only -- see module history below for why this dropped to a single run.

Data availability: only 3ts has its baseline solve's full ZEN-garden Results
files downloaded from Euler (`<run_dir>/<MODEL>/`, the un-suffixed folder next
to `_batch_summary/`); 1ts/10ts only have `_batch_summary/{polytope.npz,
diagnostics.csv}` synced down, with no CAPEX/OPEX/carrier/carbon split
available (that split only exists inside the per-run Results h5 files) --
this was originally a 1ts/3ts/10ts, two-panel comparison for exactly that
reason, but per user request narrowed to 3ts alone (the only run where a real
composition is possible) to keep the figure small and focused on one
question: how does the CAPEX-cum MGA axis relate to CAPEX's own share of NPC.

Two bars, both MEUR, same y-axis:
- **CAPEX-cum proxy**: sum of the north/west/south/east "until_2050"
  node_capex_cumulative axes from polytope.npz's z_star_phys (see
  config_mga_axes_capex_cum.json) -- undiscounted, raw sum over the 7 sampled
  model years (2020, 2025, ..., 2050), node-attributed only (excludes
  inter-node transport/edge investment, a verified ~2.5% undercount of true
  system CAPEX on this run: 6,076,191 MEUR here vs. 6,230,891 MEUR from
  `cost_capex_yearly_total` directly).
- **net_present_cost**, stacked into its 4 real components (CAPEX/OPEX/
  carrier/carbon), each already discounted AND horizon-interval-expanded the
  way constraint_net_present_cost actually builds it (get_annual_cost(...,
  discount=True) in figures_by_scenario.py) -- the stack's total height
  reproduces net_present_cost exactly (13,772,609 + 5,605,833 + 2,705,770 + 0
  = 22,084,212 MEUR, verified).

A dashed reference line at the CAPEX-cum proxy's own height crosses into the
NPC bar's CAPEX segment, which sits noticeably higher (13.77M vs. 6.08M MEUR)
-- visualizing the two effects that separate them (see the module's own
in-figure annotation and the chat explanation this figure was built to
accompany): (1) the proxy excludes edge/transport CAPEX (~2.5%, small), and
(2) far larger, the proxy is a raw undiscounted sum over 7 sampled years,
while NPC's CAPEX component multiplies each sampled year's CAPEX by
`interval_between_years`=5 (representing the ~5 calendar years it stands in
for) before discounting at `discount_rate`=0.05 -- the interval-expansion
factor (~5x) dominates the <1 discount factor, roughly a net ~2.2x for CAPEX
specifically (see constraint_net_present_cost in energy_system.py).

Component colors reuse generate_si_figures.py's COST_COMPONENT_COLORS (ETH
blue/petrol/bronze/red for CAPEX/OPEX/carrier/carbon) rather than the
dashboard's generic COLOR_MAP, for the same reason the SI print figures do
(see feedback_si_figure_colors memory).

Usage:
    python scripts/plot_mga_cost_composition.py
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

import matplotlib.pyplot as plt
import numpy as np
from zen_garden import Results

from plots.figure_settings import apply_font_mode

apply_font_mode()

from plot_mga_results import MGA_ROOT, MODEL, savefig
from plots.figures_by_scenario import get_annual_cost

TS = "3ts"
RUN_SUFFIX = "2020_7a_5a_interval_3ts_MGA_CAPEX_CUM_batch_bbo_share_batch4_tol002"

# CAPEX / OPEX / carrier / carbon -- same order+colors as generate_si_figures.py's
# COST_COMPONENT_COLORS (ETH blue/petrol/bronze/red).
COMPONENTS = [
    ("cost_capex_yearly_total", "CAPEX"),
    ("cost_opex_yearly_total", "OPEX"),
    ("cost_carrier", "Carrier (fuel/import)"),
    ("cost_carbon_emissions_total", "Carbon cost"),
]
COMPONENT_COLORS = ["#215CAF", "#007894", "#8E6713", "#B7352D"]
CAPEX_PROXY_COLOR = "#7DA5D6"  # lighter tint of the CAPEX blue -- same hue
                                # family, visually distinct accounting basis


def load_baseline_z_star() -> dict:
    """(net_present_cost, capex_cum_proxy) in MEUR from _batch_summary/
    polytope.npz's z_star_phys."""
    summary = MGA_ROOT / f"{MODEL}_{RUN_SUFFIX}" / f"{MODEL}_batch_summary" / "polytope.npz"
    p = np.load(summary, allow_pickle=True)
    z = dict(zip(p["name_list"], p["z_star_phys"]))
    capex_proxy = (
        z["north_until_2050"] + z["west_until_2050"] + z["south_until_2050"] + z["east_until_2050"]
    )
    return {"net_present_cost": float(z["net_present_cost"]), "capex_proxy": float(capex_proxy)}


def load_baseline_components() -> dict:
    """{component_var: discounted MEUR sum} for every COMPONENTS entry."""
    baseline_dir = MGA_ROOT / f"{MODEL}_{RUN_SUFFIX}" / MODEL
    r = Results(path=str(baseline_dir))
    years = sorted(int(y) for y in r.get_total("net_present_cost").index)
    return {
        var: float(get_annual_cost(r, years, var, discount=True).sum())
        for var, _ in COMPONENTS
    }


def _figure(z_star: dict, components: dict) -> None:
    fig, ax = plt.subplots(figsize=(5, 5), constrained_layout=True)

    capex_proxy = z_star["capex_proxy"]
    npc = z_star["net_present_cost"]

    # Bar 1: CAPEX-cum proxy, single solid bar.
    ax.bar(0, capex_proxy, width=0.55, color=CAPEX_PROXY_COLOR)
    ax.text(0, capex_proxy * 1.02, f"{capex_proxy:,.1f}", ha="center", va="bottom", fontsize=8)

    # Bar 2: net_present_cost, stacked into its 4 components.
    bottom = 0.0
    for (var, label), color in zip(COMPONENTS, COMPONENT_COLORS):
        val = components[var]
        ax.bar(1, val, width=0.55, bottom=bottom, color=color, label=label)
        if val > npc * 0.02:  # skip labeling near-zero segments (e.g. carbon cost here)
            ax.text(1, bottom + val / 2, f"{val:,.1f}", ha="center", va="center",
                     fontsize=7.5, color="white")
        bottom += val
    ax.text(1, npc * 1.02, f"{npc:,.1f} = NPC", ha="center", va="bottom", fontsize=8, fontweight="bold")

    # Dashed reference line at the CAPEX-cum proxy's own height, crossing into
    # the NPC bar's CAPEX segment -- visualizes the gap the chat explanation
    # accompanying this figure describes (module docstring).
    ax.axhline(capex_proxy, color=CAPEX_PROXY_COLOR, linestyle="--", linewidth=1, zorder=1)
    ax.annotate(
        "",
        xy=(0.72, components["cost_capex_yearly_total"]),
        xytext=(0.72, capex_proxy),
        arrowprops=dict(arrowstyle="<->", color="black", linewidth=0.9),
    )
    gap = components["cost_capex_yearly_total"] - capex_proxy
    ax.text(0.78, (capex_proxy + components["cost_capex_yearly_total"]) / 2,
            f"+{gap:,.1f}\n(interval-expansion\n& discounting)",
            ha="left", va="center", fontsize=6.5)

    ax.set_xticks([0, 1])
    ax.set_xticklabels(["CAPEX-cum proxy\n(4 regions, undiscounted,\nto 2050)",
                         "net_present_cost\n(solver objective)"])
    ax.set_ylabel("MEUR")
    ax.set_ylim(0, npc * 1.18)
    ax.grid(alpha=0.3, axis="y")
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    ax.set_title(f"Baseline (cost-optimal) solution -- {TS}", fontsize=10, fontweight="bold")

    savefig(fig, "fig7_cost_composition")


def main() -> None:
    print(f"Loading {TS} baseline z* and CAPEX/OPEX/carrier/carbon components...")
    z_star = load_baseline_z_star()
    components = load_baseline_components()
    _figure(z_star, components)


if __name__ == "__main__":
    main()
