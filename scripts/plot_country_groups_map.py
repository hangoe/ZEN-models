"""Europe map of the countries/nodes implemented in the zen-europe model,
colored by the MGA region group (north/south).

Node codes come straight from the dataset's energy_system/set_nodes.csv
(EU statistical convention: EL = Greece, UK = United Kingdom -- not strict
ISO 3166-1). Country borders come from Natural Earth's 50m admin-0-countries
dataset, downloaded once and cached under data/naturalearth/ (gitignored).

NODE_GROUPS below is the split used by config_mga_axes_total_output_2reg.yaml.

Usage:
    python scripts/plot_country_groups_map.py
"""

import math
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

from plots.figure_settings import apply_font_mode
from plots.mga_capex_periods_common import REGION_COLOR
from plots.natural_earth import EUROPE_EXTENT, ISO_A2_EH_OVERRIDES, ensure_naturalearth_data

# See figure_settings.FONT_MODE for the rationale and for the one-flag
# toggle that switches every figure script in this repo at once.
apply_font_mode()

NODES_CSV = (REPO_ROOT / "data" / "outputs" / "zen-europe-old"
             / "zen_europe_ind_heat_v1_no_flexibility_nodiffusion_export0"
             / "energy_system" / "set_nodes.csv")
FIGURES_DIR = REPO_ROOT / "data" / "outputs" / "figures" / "mga"

# Same split as config_mga_axes_total_output_2reg.yaml.
NODE_GROUPS = {
    "north": ["DK", "EE", "FI", "IE", "LT", "LV", "NO", "SE", "UK", "BE", "NL", "DE", "PL", "CZ"],
    "south": ["ES", "EL", "HR", "IT", "PT", "SI", "FR", "CH", "AT", "LU", "BG", "HU", "RO", "SK"],
}
GROUP_COLORS = {group: REGION_COLOR[group] for group in NODE_GROUPS}


def load_node_groups() -> pd.DataFrame:
    nodes = pd.read_csv(NODES_CSV)["node"].tolist()
    node_to_group = {n: g for g, members in NODE_GROUPS.items() for n in members}
    missing = set(nodes) - node_to_group.keys()
    if missing:
        raise ValueError(f"Nodes missing from NODE_GROUPS: {sorted(missing)}")
    return pd.DataFrame({
        "node": nodes,
        "iso_a2_eh": [ISO_A2_EH_OVERRIDES.get(n, n) for n in nodes],
        "group": [node_to_group[n] for n in nodes],
    })


def main() -> None:
    shp_path = ensure_naturalearth_data()
    world = gpd.read_file(shp_path)[["ISO_A2_EH", "NAME", "geometry"]]

    minx, maxx = EUROPE_EXTENT["lon"]
    miny, maxy = EUROPE_EXTENT["lat"]
    europe = world.cx[minx:maxx, miny:maxy]

    node_groups = load_node_groups()
    europe = europe.merge(
        node_groups, left_on="ISO_A2_EH", right_on="iso_a2_eh", how="left"
    )

    fig, ax = plt.subplots(figsize=(8, 8))
    europe.plot(ax=ax, color="white", edgecolor="#B0B0B0", linewidth=0.5)
    for group, color in GROUP_COLORS.items():
        europe[europe["group"] == group].plot(
            ax=ax, color=color, edgecolor="#B0B0B0", linewidth=0.5, label=group
        )

    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    # A degree of longitude is shorter than a degree of latitude at these
    # latitudes; correct for it at the extent's middle so the map isn't squashed.
    ax.set_aspect(1 / math.cos(math.radians((miny + maxy) / 2)))
    ax.set_axis_off()
    ax.set_title("ZEN-Europe nodes by region group", fontsize=13, fontweight="bold")

    handles = [
        plt.Rectangle((0, 0), 1, 1, facecolor=color, edgecolor="#B0B0B0")
        for color in GROUP_COLORS.values()
    ]
    ax.legend(handles, GROUP_COLORS.keys(), loc="lower left", frameon=False, fontsize=10)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_DIR / "fig_country_groups_map.svg"
    fig.savefig(out_path, bbox_inches="tight")
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
