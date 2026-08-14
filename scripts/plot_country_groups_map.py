"""Europe map of the countries/nodes implemented in the Crystal Ball model,
colored by placeholder region group (north/west/south/east).

Node codes come straight from data/Crystal_Ball/energy_system/set_nodes.csv
(EU statistical convention: EL = Greece, UK = United Kingdom -- not strict
ISO 3166-1). Country borders come from Natural Earth's 50m admin-0-countries
dataset, downloaded once and cached under data/naturalearth/ (gitignored).

NODE_GROUPS below is a placeholder split -- north/west/south/east assigned by
rough geography, not any real modelling criterion. Replace it once real
groups are defined.

Usage:
    python scripts/plot_country_groups_map.py
"""

import io
import zipfile
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

from figure_settings import SCENARIO_PALETTE

NODES_CSV = REPO_ROOT / "data" / "Crystal_Ball" / "energy_system" / "set_nodes.csv"
FIGURES_DIR = REPO_ROOT / "data" / "outputs" / "figures" / "mga_investment"

NATURALEARTH_DIR = REPO_ROOT / "data" / "naturalearth"
NATURALEARTH_URL = "https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_0_countries.zip"
NATURALEARTH_SHP = NATURALEARTH_DIR / "ne_50m_admin_0_countries.shp"

# Placeholder region groups -- sorted by rough geography, to be replaced once
# the user specifies real groups.
NODE_GROUPS = {
    "north": ["DK", "EE", "FI", "LT", "LV", "NO", "SE"],
    "west": ["AT", "BE", "CH", "DE", "FR", "IE", "LU", "NL", "UK"],
    "south": ["ES", "EL", "HR", "IT", "PT", "SI"],
    "east": ["BG", "CZ", "HU", "PL", "RO", "SK"],
}
GROUP_COLORS = dict(zip(NODE_GROUPS, SCENARIO_PALETTE))

# set_nodes.csv follows the EU statistical convention (EL, UK), which differs
# from Natural Earth's ISO_A2_EH codes (GR, GB) for those two.
ISO_A2_EH_OVERRIDES = {"EL": "GR", "UK": "GB"}

EUROPE_EXTENT = {"lon": (-25, 45), "lat": (34, 72)}


def ensure_naturalearth_data() -> Path:
    if NATURALEARTH_SHP.exists():
        return NATURALEARTH_SHP
    NATURALEARTH_DIR.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(NATURALEARTH_URL) as response:
        zip_bytes = response.read()
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        zf.extractall(NATURALEARTH_DIR)
    return NATURALEARTH_SHP


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
    ax.set_axis_off()
    ax.set_title("Crystal Ball nodes by region group", fontsize=13, fontweight="bold")

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
