"""Map of Europe: the ZEN-Europe nodes in ETH blue, all other countries white.

Transparent background (for slides). Countries: Natural Earth 1:50m admin-0
(data/naturalearth/), nodes: data/datasets/zen_europe/energy_system/set_nodes.csv.
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

from ..paths import DATASETS_DIR, NATURAL_EARTH_DIR
from ..style import ETH_BLUE, save_figure

NODES_CSV = DATASETS_DIR / "zen_europe" / "energy_system" / "set_nodes.csv"
COUNTRIES_SHP = NATURAL_EARTH_DIR / "ne_50m_admin_0_countries.shp"

# ZEN node codes (Eurostat) that differ from ISO 3166 alpha-2
NODE_TO_ISO = {"EL": "GR", "UK": "GB"}

# Lambert azimuthal equal-area (EPSG:3035) extent in m: Iceland/Portugal to Finland/Cyprus
EXTENT_X = (2.5e6, 6.6e6)
EXTENT_Y = (1.35e6, 5.45e6)
OUTLINE = "#6F6F6F"


def node_map(name: str) -> None:
    nodes = pd.read_csv(NODES_CSV)["node"]
    iso = {NODE_TO_ISO.get(n, n) for n in nodes}

    countries = gpd.read_file(COUNTRIES_SHP).to_crs(epsg=3035)
    is_node = countries["ISO_A2_EH"].isin(iso)
    missing = iso - set(countries.loc[is_node, "ISO_A2_EH"])
    if missing:
        raise ValueError(f"nodes without a country shape: {sorted(missing)}")

    fig, ax = plt.subplots(figsize=(6.3, 6.3))
    countries[~is_node].plot(ax=ax, color="white", edgecolor=OUTLINE, linewidth=0.4)
    countries[is_node].plot(ax=ax, color=ETH_BLUE, edgecolor="white", linewidth=0.4)
    ax.set_xlim(EXTENT_X)
    ax.set_ylim(EXTENT_Y)
    ax.set_axis_off()
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    save_figure(fig, name)
