"""General geographic overview of the batch4 v9_0 regional-CAPEX-by-PERIOD
MGA run (same run as mga_capex_periods_common.py /
plot_mga_regional_investment.py), tying together three things that were
previously only visible as separate bar charts:

1. **Transport capacity** -- every power_line link drawn on the actual map,
   width ~ total capacity, colour a 3-tier utilisation highlight rather than
   a continuous gradient: saturated (>=95% of capacity_limit, capacity /
   capacity_limit, both directions summed -- see _EDGE_DATA's docstring for
   why summing rather than picking one direction) links are red, moderately
   used links (50-95%) are yellow, everything else is one muted green, each
   tier drawn on top of the previous so red stays visible wherever links
   cross. A continuous green-yellow-red colourmap across 60 links was tried
   first and mostly just added shades to tell apart rather than clarifying
   the pattern; a purely binary saturated/not version was tried next but
   lost the 50-95% "moderately loaded" case entirely -- 3 flat buckets keeps
   that middle tier visible without the original gradient's noise. This is
   the same capacity_limit saturation finding from the "why doesn't baseline
   use north's wind" analysis, but for every link in the model at once
   instead of the dozen north-crossing edges checked by hand: nearly every
   CROSS-REGION link is red (saturated), while INTRA-region links (green,
   e.g. within west) mostly have real remaining potential -- so this map is
   the general version of that finding, not specific to north.

2. **Remaining potential per region, by technology** (icon shape + size) --
   capacity_limit minus baseline 2050 usage, summed to the same 4 regions as
   fig7's headroom bars (same quantity, called "remaining potential" here;
   not per node: with 28 nodes each carrying up to 3 icons, the
   node-level version of this map was unreadably dense -- one icon cluster
   per region keeps the same information at a legible count), split into
   three pictographic icons (custom vector Paths, not font glyphs -- see the
   "<"/"~" note near the bottom of this file for why this codebase doesn't
   rely on non-ASCII glyphs rendering correctly through cmr10) so category is
   read from shape, not just colour: a 3-blade turbine pinwheel = wind
   (onshore+offshore), a sun with rays = photovoltaics, a gear/cog = other
   finite-potential generation (nuclear, reservoir_hydro, run-of-river_hydro,
   pumped_hydro -- the only other technologies with a real, non-infinite
   capacity_limit anywhere in the model; everything else that's technically
   finite -- lng_terminal, district_heating_grid, carbon_storage, the
   waste-heat-limited industry heat pumps -- is grid/storage/heat
   infrastructure, not generation potential, so it's left out rather than
   diluting "other"). All three share ONE size scale (sqrt, against the
   largest single region/category value) specifically so the categories stay
   honestly comparable: "other" ends up visibly small in every region, which
   is itself the finding. Icons are filled with the region's colour and
   placed side by side (left-to-right: wind, PV, other), packed edge-to-edge
   without overlapping regardless of size, near each region's own node
   cluster.

3. **Own-axis CAPEX range per region** (text boxes, from the same
   polytope.npz fig8 uses) -- baseline and VMM min/max for 2040-2049,
   placed near each region's own node cluster, so the map reads as one
   "what can this region's investment do, and why" summary instead of
   needing fig7/fig8 side by side.

Country polygons/extent/ISO-code handling follow plot_country_groups_map.py
exactly (same Natural Earth 50m source, same EL/UK override, same cache dir).

Usage:
    python scripts/plot_mga_investment_map.py
"""

import io
import urllib.request
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.path import Path as MplPath

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["cmr10"],
    "mathtext.fontset": "cm",
    "axes.formatter.use_mathtext": True,
    "axes.unicode_minus": False,
})

from figure_settings import eth_tint
from mga_capex_periods_common import PERIODS, REGION_COLOR, REGIONS, RUN_DIR, load_batch4_data
from plot_mga_regional_investment import REGION_NODES
from zen_garden import Results


def _wind_marker() -> MplPath:
    """3-blade turbine pinwheel: each blade a kite/leaf shape (narrow at the
    hub, wide at the belly, narrow again at the tip -- a thin triangle reads
    as a bare line at small marker sizes, so the belly points give the blade
    actual fillable area), swept forward (tip angle offset from the base
    angle) so it reads as rotating blades rather than a plain star. A small
    hub disc is added as a fourth, unrelated (same-winding, so additive
    rather than a hole) subpath."""
    hub_r, belly_r, tip_r = 0.10, 0.6, 1.0
    half_belly_deg, sweep_deg = 15, 40
    verts, codes = [], []
    for i in range(3):
        base = 2 * np.pi * i / 3
        belly_a = base + np.radians(sweep_deg * 0.5)
        tip_a = base + np.radians(sweep_deg)
        a0 = belly_a - np.radians(half_belly_deg)
        a1 = belly_a + np.radians(half_belly_deg)
        p_hub = (hub_r * np.cos(base), hub_r * np.sin(base))
        verts += [
            p_hub,
            (belly_r * np.cos(a0), belly_r * np.sin(a0)),
            (tip_r * np.cos(tip_a), tip_r * np.sin(tip_a)),
            (belly_r * np.cos(a1), belly_r * np.sin(a1)),
            p_hub,
        ]
        codes += [MplPath.MOVETO, MplPath.LINETO, MplPath.LINETO, MplPath.LINETO, MplPath.CLOSEPOLY]
    hub_pts = [(hub_r * 1.8 * np.cos(a), hub_r * 1.8 * np.sin(a)) for a in np.linspace(0, 2 * np.pi, 12, endpoint=False)]
    verts.append(hub_pts[0])
    codes.append(MplPath.MOVETO)
    for p in hub_pts[1:]:
        verts.append(p)
        codes.append(MplPath.LINETO)
    verts.append(hub_pts[0])
    codes.append(MplPath.CLOSEPOLY)
    return MplPath(verts, codes)


def _sun_marker(n_rays: int = 8, inner_r: float = 0.45) -> MplPath:
    """Sun-with-rays: a single star polygon alternating outer_r=1.0 (ray
    tips) and inner_r (between rays)."""
    n = n_rays * 2
    verts, codes = [], []
    for i in range(n):
        angle = 2 * np.pi * i / n
        r = 1.0 if i % 2 == 0 else inner_r
        verts.append((r * np.cos(angle), r * np.sin(angle)))
        codes.append(MplPath.MOVETO if i == 0 else MplPath.LINETO)
    verts.append(verts[0])
    codes.append(MplPath.CLOSEPOLY)
    return MplPath(verts, codes)


def _gear_marker(n_teeth: int = 8, tooth_r: float = 1.0, root_r: float = 0.68, hole_r: float = 0.32) -> MplPath:
    """Gear/cog: blocky teeth around a rim, with a centre hole. The hole is a
    second closed subpath wound in the OPPOSITE direction from the outer
    silhouette -- under the nonzero fill rule that cancels the winding count
    inside it back to zero, punching a hole rather than adding a second
    filled disc (the standard matplotlib "donut path" trick)."""
    verts, codes = [], []
    for i in range(n_teeth):
        a_root0 = 2 * np.pi * i / n_teeth
        a_tooth0 = a_root0 + 2 * np.pi * 0.15 / n_teeth
        a_tooth1 = a_root0 + 2 * np.pi * 0.35 / n_teeth
        a_root1 = a_root0 + 2 * np.pi * 0.5 / n_teeth
        pts = [
            (root_r * np.cos(a_root0), root_r * np.sin(a_root0)),
            (tooth_r * np.cos(a_tooth0), tooth_r * np.sin(a_tooth0)),
            (tooth_r * np.cos(a_tooth1), tooth_r * np.sin(a_tooth1)),
            (root_r * np.cos(a_root1), root_r * np.sin(a_root1)),
        ]
        for j, p in enumerate(pts):
            verts.append(p)
            codes.append(MplPath.MOVETO if (i == 0 and j == 0) else MplPath.LINETO)
    verts.append(verts[0])
    codes.append(MplPath.CLOSEPOLY)
    hole_pts = [(hole_r * np.cos(-a), hole_r * np.sin(-a)) for a in np.linspace(0, 2 * np.pi, 16, endpoint=False)]
    verts.append(hole_pts[0])
    codes.append(MplPath.MOVETO)
    for p in hole_pts[1:]:
        verts.append(p)
        codes.append(MplPath.LINETO)
    verts.append(hole_pts[0])
    codes.append(MplPath.CLOSEPOLY)
    return MplPath(verts, codes)


# Three remaining-potential categories shown on the map as distinct pictographic icons
# (see module docstring for why "other" is this specific list, not every
# technology with a finite capacity_limit). Dict order is also the
# left-to-right slot order used to lay the icons out side by side per node.
REMAINING_POTENTIAL_CATEGORIES = {
    "wind": (["wind_onshore", "wind_offshore"], _wind_marker()),
    "pv": (["photovoltaics"], _sun_marker()),
    "other": (["nuclear", "reservoir_hydro", "run-of-river_hydro", "pumped_hydro"], _gear_marker()),
}
REMAINING_POTENTIAL_LABELS = {"wind": "wind", "pv": "photovoltaics", "other": "other (nuclear, hydro)"}

# Degrees of longitude per SVG point, for this script's fixed figsize=(11, 11)
# and EUROPE_EXTENT -- needed to convert an icon's rendered radius (matplotlib
# scatter markers: radius_points = sqrt(s)/2, verified by reading the anchor
# dots' actual radius off a rendered SVG) into a data-space (degree) offset,
# so that icons are packed edge-to-edge without overlapping regardless of how
# large the shared sqrt(GW) scale makes any individual one -- a fixed offset
# either overlaps at the largest sizes (NO's wind, ~1,900 GW) or wastes space
# at the smallest. Measured by fitting node longitude against the anchor
# dots' SVG x position in a rendered output of this script; re-measure the
# same way if figsize or EUROPE_EXTENT change.
POINTS_PER_DEGREE_LON = 8.77
ICON_GAP_DEG = 0.05
# Halo background circles (see main()) are drawn at HALO_SCALE times an
# icon's own area -- packing must reserve space for the halo's footprint,
# not the smaller icon inside it, or adjacent halos overlap.
HALO_SCALE = 2.4


def _icon_slot_offsets(sizes: dict) -> dict:
    """Left-to-right (wind, PV, other -- REMAINING_POTENTIAL_CATEGORIES order) offsets
    in degrees lon for the icons present (sizes keyed by category) at one
    node, packed edge-to-edge (by halo footprint, HALO_SCALE times the icon
    area) with ICON_GAP_DEG between them and centred on the node."""
    cats = [c for c in REMAINING_POTENTIAL_CATEGORIES if c in sizes]
    radii = [(np.sqrt(sizes[c] * HALO_SCALE) / 2) / POINTS_PER_DEGREE_LON for c in cats]
    total_width = sum(2 * r for r in radii) + ICON_GAP_DEG * max(len(cats) - 1, 0)
    x = -total_width / 2
    offsets = {}
    for cat, r in zip(cats, radii):
        offsets[cat] = x + r
        x += 2 * r + ICON_GAP_DEG
    return offsets

FIGURES_DIR = REPO_ROOT / "data" / "outputs" / "figures" / "mga_investment"
NODES_CSV = REPO_ROOT / "data" / "Crystal_Ball" / "energy_system" / "set_nodes.csv"
EDGES_CSV = REPO_ROOT / "data" / "Crystal_Ball" / "energy_system" / "set_edges.csv"
MODEL = "Crystal_Ball_ind_heat_v9_0_no_flexibility_nodiffusion"

NATURALEARTH_DIR = REPO_ROOT / "data" / "naturalearth"
NATURALEARTH_URL = "https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_0_countries.zip"
NATURALEARTH_SHP = NATURALEARTH_DIR / "ne_50m_admin_0_countries.shp"
ISO_A2_EH_OVERRIDES = {"EL": "GR", "UK": "GB"}
EUROPE_EXTENT = {"lon": (-25, 45), "lat": (34, 72)}

NODE_TO_REGION = {n: r for r, nodes in REGION_NODES.items() for n in nodes}


def ensure_naturalearth_data() -> Path:
    if NATURALEARTH_SHP.exists():
        return NATURALEARTH_SHP
    NATURALEARTH_DIR.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(NATURALEARTH_URL) as response:
        zip_bytes = response.read()
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        zf.extractall(NATURALEARTH_DIR)
    return NATURALEARTH_SHP


def _node_coords() -> pd.DataFrame:
    return pd.read_csv(NODES_CSV).set_index("node")


def _edge_data(base_r: Results) -> pd.DataFrame:
    """One row per undirected physical link (60 of them, from set_edges.csv's
    120 directional rows), with total capacity and capacity_limit (2050, GW)
    summed over BOTH directions. Direction matters in the raw data --
    e.g. BE-DE carries 3.4 GW baseline capacity, DE-BE only 0.4 GW -- but a
    "general overview" map draws one line per physical link, so both
    directions are pooled into that link's total transfer capacity and total
    limit rather than picking one direction arbitrarily."""
    edges = pd.read_csv(EDGES_CSV)
    cap = base_r.get_total("capacity")
    cap = cap[(cap.index.get_level_values("technology") == "power_line")
              & (cap.index.get_level_values("capacity_type") == "power")]
    lim = base_r.get_total("capacity_limit")
    lim = lim[(lim.index.get_level_values("technology") == "power_line")
              & (lim.index.get_level_values("capacity_type") == "power")]

    seen: dict[frozenset, dict] = {}
    for _, row in edges.iterrows():
        pair = frozenset([row["node_from"], row["node_to"]])
        c = cap[cap.index.get_level_values("location") == row["edge"]]
        l = lim[lim.index.get_level_values("location") == row["edge"]]
        cval = float(c[2050].iloc[0]) if not c.empty else 0.0
        lval = float(l[2050].iloc[0]) if not l.empty else 0.0
        entry = seen.setdefault(pair, {"node_a": row["node_from"], "node_b": row["node_to"],
                                        "capacity": 0.0, "limit": 0.0})
        entry["capacity"] += cval
        entry["limit"] += lval

    out = pd.DataFrame(seen.values())
    out["utilization"] = np.where(out["limit"] > 0, out["capacity"] / out["limit"], np.nan)
    return out


def _region_remaining_potential_by_category(base_r: Results) -> dict[str, pd.Series]:
    """Per-region (REGIONS) capacity_limit minus baseline 2050 usage (GW),
    one Series per entry in REMAINING_POTENTIAL_CATEGORIES -- nodes summed to their
    region first (same aggregation level as fig7's headroom bars), split by
    technology instead of pooled."""
    lim = base_r.get_total("capacity_limit")
    lim = lim[lim.index.get_level_values("capacity_type") == "power"]
    cap = base_r.get_total("capacity")
    cap = cap[cap.index.get_level_values("capacity_type") == "power"]

    out = {}
    for cat, (techs, _marker) in REMAINING_POTENTIAL_CATEGORIES.items():
        l = lim[lim.index.get_level_values("technology").isin(techs)]
        c = cap[cap.index.get_level_values("technology").isin(techs)]
        limit_by_region = l.groupby(l.index.get_level_values("location").map(NODE_TO_REGION))[2050].sum()
        used_by_region = c.groupby(c.index.get_level_values("location").map(NODE_TO_REGION))[2050].sum()
        out[cat] = (limit_by_region - used_by_region).reindex(REGIONS, fill_value=0.0).clip(lower=0)
    return out


def _region_range_text(period: str, axis_idx, origin, phys, base, region: str) -> str:
    lo = phys[origin.index(f"min:{region}_{period}")][axis_idx[f"{region}_{period}"]] / 1000
    hi = phys[origin.index(f"max:{region}_{period}")][axis_idx[f"{region}_{period}"]] / 1000
    bl = base[axis_idx[f"{region}_{period}"]] / 1000
    return f"{region.capitalize()}\nbaseline {bl:,.0f}\nrange {lo:,.0f}-{hi:,.0f} bn EUR"


def main() -> None:
    shp_path = ensure_naturalearth_data()
    world = gpd.read_file(shp_path)[["ISO_A2_EH", "NAME", "geometry"]]
    minx, maxx = EUROPE_EXTENT["lon"]
    miny, maxy = EUROPE_EXTENT["lat"]
    europe = world.cx[minx:maxx, miny:maxy]

    node_iso = {n: ISO_A2_EH_OVERRIDES.get(n, n) for n in NODE_TO_REGION}
    node_region_df = pd.DataFrame({
        "node": list(node_iso), "iso_a2_eh": list(node_iso.values()),
        "region": [NODE_TO_REGION[n] for n in node_iso],
    })
    europe = europe.merge(node_region_df, left_on="ISO_A2_EH", right_on="iso_a2_eh", how="left")

    base_r = Results(path=str(RUN_DIR / MODEL))
    edge_df = _edge_data(base_r)
    remaining_potential = _region_remaining_potential_by_category(base_r)
    remaining_potential_max = max(s.max() for s in remaining_potential.values())
    coords = _node_coords()

    poly, names, units, axis_idx, origin, phys, base = load_batch4_data()

    fig, ax = plt.subplots(figsize=(11, 11))
    europe.plot(ax=ax, color="#f2f2f2", edgecolor="#B0B0B0", linewidth=0.5)
    for region, color in REGION_COLOR.items():
        europe[europe["region"] == region].plot(
            ax=ax, color=eth_tint(color, 0.82), edgecolor="#B0B0B0", linewidth=0.5,
        )

    # Transmission edges: 3-tier utilisation highlight rather than a
    # continuous green-yellow-red gradient across all 60 links (which mostly
    # just added shades to tell apart) or a purely binary saturated/not
    # version (which lost the "moderately loaded" case entirely). Green/
    # yellow/red flat buckets keep that middle tier visible without the
    # original gradient's noise; each tier is drawn on top of the previous
    # (green, then yellow, then red) so the most-congested links stay visible
    # wherever links cross. Width still ~ total capacity. (This also makes
    # the old black cross-region outline redundant -- saturated links
    # already ARE almost exactly the cross-region ones -- so it's dropped
    # rather than adding a second, separate visual layer on top of the
    # highlight.)
    SATURATED_THRESHOLD = 0.95
    MODERATE_THRESHOLD = 0.50
    SATURATED_COLOR = "#b3122a"
    MODERATE_COLOR = "#e8b93a"
    SLACK_COLOR = "#3f9142"
    for _, e in edge_df.sort_values("utilization", na_position="first").iterrows():
        a, b = coords.loc[e["node_a"]], coords.loc[e["node_b"]]
        u = 0.0 if pd.isna(e["utilization"]) else e["utilization"]
        if u >= SATURATED_THRESHOLD:
            color, lw_bump, alpha, zorder = SATURATED_COLOR, 0.5, 1.0, 4
        elif u >= MODERATE_THRESHOLD:
            color, lw_bump, alpha, zorder = MODERATE_COLOR, 0.2, 0.95, 3
        else:
            color, lw_bump, alpha, zorder = SLACK_COLOR, 0.0, 0.8, 2
        lw = 0.6 + 2.6 * np.sqrt(max(e["capacity"], 0.05) / edge_df["capacity"].max())
        ax.plot([a["lon"], b["lon"]], [a["lat"], b["lat"]],
                 color=color, linewidth=lw + lw_bump, solid_capstyle="round",
                 alpha=alpha, zorder=zorder)

    # Node markers: a filled anchor dot (region colour) sized to hold the
    # country-code label CENTRED inside it (rather than below, where it used
    # to collide with edges/icons passing under the node) -- s=90 was sized
    # for an empty dot; a 2-letter label at fontsize 6.5 needs the bigger
    # dot below to stay inside the circle instead of poking out past its edge.
    for node, row in coords.iterrows():
        region = NODE_TO_REGION[node]
        ax.scatter(row["lon"], row["lat"], s=190, color=REGION_COLOR[region],
                   edgecolor="black", linewidth=0.7, zorder=4)
        ax.annotate(node, (row["lon"], row["lat"]), textcoords="offset points",
                    xytext=(0, 0), ha="center", va="center", fontsize=6.5, zorder=6,
                    fontweight="bold", color="white",
                    path_effects=None)

    # Region CAPEX-range annotations (2040-2049, the larger of the two
    # periods) plus one remaining-potential icon cluster, both near each
    # region's own node cluster.
    period = "2040_2049"
    # Small per-region nudges (degrees) so neighbouring boxes (west/east sit
    # close together in central Europe) don't overlap each other or the
    # node markers/labels underneath them.
    box_nudge = {"north": (0, 3.5), "west": (-6.0, 4.5), "south": (-1.0, -6.5), "east": (5.5, 4.5)}
    for region in REGIONS:
        nodes = REGION_NODES[region]
        dx, dy = box_nudge[region]
        cx = coords.loc[nodes, "lon"].mean() + dx
        cy = coords.loc[nodes, "lat"].max() + dy
        txt = _region_range_text(period, axis_idx, origin, phys, base, region)
        ax.text(cx, cy, txt, ha="center", va="bottom", fontsize=8.5,
                bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                          edgecolor=REGION_COLOR[region], linewidth=1.6, alpha=0.92),
                zorder=6)

        # Remaining-potential icon row: anchored at the SAME (cx, cy) point as the box
        # above, just below its bottom edge, rather than at the region's own
        # node centroid -- box_nudge already keeps each box clear of other
        # regions' nodes/lines (e.g. "east"'s box sits up near Scandinavia,
        # nowhere near its own PL/CZ/... nodes), so anchoring to the node
        # centroid instead put icon rows on a collision course with whatever
        # other region's box happened to be nudged into that same area.
        sizes = {}
        for cat, (_techs, _marker) in REMAINING_POTENTIAL_CATEGORIES.items():
            value = remaining_potential[cat].get(region, 0.0)
            if value > 0:
                sizes[cat] = 25 + 500 * np.sqrt(value / remaining_potential_max)
        icon_lat = cy - 1.9
        slot_offset = _icon_slot_offsets(sizes)
        for cat, (_techs, marker) in REMAINING_POTENTIAL_CATEGORIES.items():
            if cat not in sizes:
                continue
            icon_x = cx + slot_offset[cat]
            # Soft white halo behind each icon (region-coloured rim) so the
            # small, region-coloured icon still pops out from the map's
            # background and transmission lines instead of blending in.
            ax.scatter(icon_x, icon_lat, s=sizes[cat] * HALO_SCALE, marker="o",
                       facecolor="white", edgecolor=REGION_COLOR[region], linewidth=0.7,
                       alpha=0.95, zorder=5.5)
            ax.scatter(icon_x, icon_lat, s=sizes[cat], marker=marker,
                       facecolor=REGION_COLOR[region], edgecolor="black", linewidth=0.4, zorder=6)

    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    ax.set_axis_off()
    ax.set_title(
        "MGA batch4 (v9_0): Grid, Remaining Potential by Technology, and Regional CAPEX Range\n"
        "red/yellow = saturated/moderately used link; boxes = 2040-2049 baseline and VMM range",
        fontsize=11, fontweight="bold",
    )

    # Avoid "<" and "~" in any plotted (non-mathtext) text here: with this
    # codebase's shared cmr10 rcParams block, matplotlib's AFM metrics for
    # that font don't follow plain ASCII for those two glyphs -- "<" comes
    # out as an inverted exclamation mark and "~" as a raised, displaced
    # tilde (verified directly by rendering both in isolation), not a
    # viewer-side font-substitution issue since svg.fonttype="path" bakes
    # the (wrong) shapes in at save time. Same reason fig titles elsewhere
    # in this repo write "v9_0" rather than "v9.0": known-safe characters
    # only for any text that isn't wrapped in mathtext ($...$).
    util_handles = [
        Line2D([0], [0], color=SLACK_COLOR, lw=3, label="under 50% used"),
        Line2D([0], [0], color=MODERATE_COLOR, lw=3.2, label="50-95% used"),
        Line2D([0], [0], color=SATURATED_COLOR, lw=3.5, label="saturated (95%+ used)"),
    ]
    shape_handles = [
        Line2D([0], [0], marker=marker, color="w", markerfacecolor="#808080", markeredgecolor="black",
               markeredgewidth=0.8, markersize=13, label=REMAINING_POTENTIAL_LABELS[cat])
        for cat, (_techs, marker) in REMAINING_POTENTIAL_CATEGORIES.items()
    ]
    leg1 = ax.legend(handles=util_handles, loc="lower left", fontsize=8.5, title="line: grid utilisation",
                      title_fontsize=8.5, frameon=True, framealpha=0.9)
    ax.add_artist(leg1)
    leg2 = ax.legend(handles=shape_handles, loc="lower right", fontsize=8.5,
                      title="icon: regional remaining potential by tech (size = GW,\nshared scale; left-to-right = wind, PV, other)",
                      title_fontsize=8.5, frameon=True, framealpha=0.9)
    ax.add_artist(leg2)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_DIR / "fig_vmm_grid_overview_map.svg"
    fig.savefig(out_path, bbox_inches="tight")
    print(f"Saved {out_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
