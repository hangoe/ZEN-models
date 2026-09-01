"""Shared constants, helpers, and plotting primitives: color/hatch maps, model
discovery, Results loading, and matplotlib plotting primitives. Used by both
the Streamlit dashboard (streamlit/app.py) and standalone figure-generation
scripts (e.g. generate_si_figures.py) — this module owns no UI logic itself."""

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from zen_garden import Results

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "outputs"
LOCAL_ROOT = OUTPUT_DIR / "local_outputs"
EULER_ROOT = OUTPUT_DIR / "euler_outputs"
HOURS_PER_YEAR = 8760

# ── Font mode ────────────────────────────────────────────────────────────────
# Every figure script in this repo (generate_si_figures.py, compare_version_v8_
# v9.py, plot_mga_results.py, plot_mga_cum_regional_capex.py, plot_mga_regional_
# investment.py, plot_mga_investment_map.py) used to inline its own identical
# rcParams block for this. Centralized here so switching every script's fonts
# at once is a ONE-LINE change: flip FONT_MODE below, nothing else. Each
# figure's own fontsize=N calls are untouched by this toggle either way —
# only the font FAMILY (and matching mathtext glyph set) changes.
#   "report"       — matches MT_report_HG's LaTeX default (plain Computer
#                     Modern, no font package loaded by 00_Preamble.sty).
#                     cmr10 ships inside matplotlib itself (no system LaTeX/
#                     font install needed, portable to Euler too). Its bundled
#                     Type-1 file has no linked bold companion, so
#                     fontweight="bold" requests silently render at regular
#                     weight rather than a mismatched fallback font.
#   "presentation"  — Arial, for slide decks. No exact "Arial" mathtext glyph
#                     set ships with matplotlib, so mathtext ($...$ content —
#                     subscripts like CO$_2$, etc.) falls back to
#                     "dejavusans", the closest built-in sans-serif match.
FONT_MODE = "presentation"  # "report" or "presentation"


def apply_font_mode() -> None:
    """Call once per script, right after `import matplotlib.pyplot as plt`
    (before any figure is built) — see FONT_MODE's comment above for what
    each mode does and why."""
    if FONT_MODE == "presentation":
        plt.rcParams.update({
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial"],
            "mathtext.fontset": "dejavusans",
            "axes.formatter.use_mathtext": True,
            "axes.unicode_minus": True,
        })
    else:
        plt.rcParams.update({
            "font.family": "serif",
            "font.serif": ["cmr10"],
            "mathtext.fontset": "cm",
            "axes.formatter.use_mathtext": True,
            "axes.unicode_minus": False,
        })


# ── Euler scenario metadata ────────────────────────────────────────────────────
# 6 of the 7 case-study scenarios (MT_report_HG/Sections/03_SI.tex, Table
# SIScenarios) are the same model version (Crystal_Ball_HG_v7_0), differing
# only in which flexibility technologies / DSM categorization are included
# (see parameters.csv). The 7th, the unmodified "Crystal Ball (base)" dataset
# (data/Crystal_Ball, run as bare "Crystal_Ball" with no Crystal_Ball_HG_v7_0
# prefix — see run_model.py), is the pre-industry-heat-extension reference
# point and is intentionally NOT in this list: it has no industry heat/DSM/TES
# sector, doesn't match this prefix scheme, and its euler run hadn't completed
# as of this writing. Once its output folder exists, it needs deliberate
# handling in generate_si_figures.py rather than folding it in here — see the
# comment on SCENARIOS in that file.
# Order matches Table SIScenarios (excluding "Crystal Ball (base)", the row
# before "No flexibility" there — see the module docstring above).
EULER_SCENARIO_ORDER = [
    "Crystal_Ball_ind_heat_v9_0_no_flexibility",
    "Crystal_Ball_ind_heat_v9_0",
    "Crystal_Ball_ind_heat_v9_0_DSM_pessimistic",
    "Crystal_Ball_ind_heat_v9_0_DSM_only",
    "Crystal_Ball_ind_heat_v9_0_TES_only",
    "Crystal_Ball_ind_heat_v9_0_single_temp",
    # Not one of the 6 Table~SIScenarios entries — a side investigation run
    # (technology diffusion-rate constraint disabled entirely). Listed here,
    # even though generate_si_figures.py's SCENARIOS doesn't include it,
    # purely so _match_scenario_base's longest-prefix-wins logic doesn't
    # mis-sort/mislabel it as "Baseline" (it otherwise shares the
    # "Crystal_Ball_ind_heat_v9_0_" prefix with the base run).
    "Crystal_Ball_ind_heat_v9_0_nodiffusion",
]
EULER_SCENARIO_LABELS = {
    "Crystal_Ball_ind_heat_v9_0_no_flexibility": "No Flexibility",
    "Crystal_Ball_ind_heat_v9_0": "Baseline",
    "Crystal_Ball_ind_heat_v9_0_DSM_pessimistic": "DSM Pessimistic",
    "Crystal_Ball_ind_heat_v9_0_DSM_only": "DSM Only",
    "Crystal_Ball_ind_heat_v9_0_TES_only": "TES Only",
    "Crystal_Ball_ind_heat_v9_0_single_temp": "Single-Temp",
    "Crystal_Ball_ind_heat_v9_0_nodiffusion": "No Diffusion Limit",
}
# Positional per-run colors (run slot -> color), independent of the
# technology-keyed COLOR_MAP below. Used for run-identity lines/swatches only
# (e.g. cost-over-time curves, sidebar scenario list). The 7 ETH Zurich
# corporate design colors (https://ethz.ch/staffnet/en/service/communication/
# corporate-design/colours.html: blue, petrol, green, bronze, red, purple,
# grey), in that order. 7th slot (ETH grey) is reserved for the future
# "Crystal Ball (base)" reference run — grey reads as "the neutral baseline"
# against the six saturated extension-scenario colors.
SCENARIO_PALETTE = ["#215CAF", "#007894", "#627313", "#8E6713", "#B7352D", "#A7117A", "#6F6F6F"]


def eth_tint(hex_color: str, pct: float) -> str:
    """Blend hex_color toward white by pct (0=original, 1=white) — mirrors
    ETH's documented 20/40/60/80% corporate-design tint system. Shared by
    every script that needs a lighter/darker variant of an ETH color rather
    than inventing an off-palette one (see generate_si_figures.py,
    plot_carrier_flows.py)."""
    from matplotlib.colors import to_rgb
    r, g, b = to_rgb(hex_color)
    r, g, b = (c + (1 - c) * pct for c in (r, g, b))
    return f"#{int(round(r * 255)):02x}{int(round(g * 255)):02x}{int(round(b * 255)):02x}"


# ── Merged color palette ──────────────────────────────────────────────────────
# Base: compare_models.py (system-wide coverage)
# Added: analyze_model.py entries not present in base (industry heat carriers,
#        temp conversion, TES, DSM)
COLOR_MAP = {
    # Industry heat carriers
    "heat_industry_0_100": "#1a237e",
    "heat_industry_100_150": "#64b5f6",
    "heat_industry_150_200": "#ff7043",
    "heat_industry_temp_conversion_150": "#ffab91",
    "heat_industry_temp_conversion_100": "#ffcc80",
    # TES
    "industry_TES_water_0_100": "#5aacff",
    "industry_TES_water_100_150": "#6495ed",
    "industry_TES_steam_100_150": "#ff7043",
    "industry_TES_steam_150_200": "#ef5350",
    # DSM — 10 mutually distinguishable hues, loosely tied to each product's
    # colour where one exists (steel=blue, glass/ceramic=purple, food=warm).
    "ammonia_DSM": "#00897b",          # teal (H2/ammonia family)
    "ceramic_DSM": "#ab47bc",          # violet (ceramic_production is purple)
    "clinker_DSM": "#757575",          # grey (cement/clinker)
    "food_DSM": "#ff8f00",             # amber (food = warm)
    "glass_DSM": "#7e57c2",            # deep purple (glass_production is purple)
    "methanol_DSM": "#8d6e63",         # brown (chemicals)
    "olefin_DSM": "#afb42b",           # olive-lime (chemicals, distinct from methanol)
    "paper_DSM": "#d81b60",            # rose-pink
    "primary_steel_DSM": "#1565c0",    # strong blue (steel)
    "secondary_steel_DSM": "#4fc3f7",  # light blue (steel)
    # Carriers (emissions plot)
    "crude_oil (carrier)": "#a0795c",
    "natural_gas (carrier)": "#d4a017",
    "hard_coal (carrier)": "#8b6e5a",
    "lng (carrier)": "#e8a838",
    "lignite (carrier)": "#a89070",
    "waste (carrier)": "#a0a0a0",
    # Technologies (emissions plot)
    "cement_kiln (tech)": "#a0a0a0",
    "BF_BOF (tech)": "#4682b4",
    "EAF (tech)": "#87ceeb",
    "NG_DRI (tech)": "#b0c4de",
    "glass_production (tech)": "#9370db",
    # Fossil / fuel technologies
    "natural_gas_boiler": "#d4a017",
    "natural_gas_boiler_DH": "#c49000",
    "natural_gas_boiler_industry": "#b8860b",
    "natural_gas_turbine": "#ffd700",
    "natural_gas_turbine_CCS": "#e6c200",
    "natural_gas_pipeline": "#f0e68c",
    "natural_gas_storage": "#eee8aa",
    "SMR": "#cd853f",
    "SMR_CCS": "#d2a679",
    "methanol_from_natural_gas": "#c9a96e",
    "methanation": "#bdb76b",
    "hard_coal_plant": "#5d4037",
    "hard_coal_boiler_DH": "#9c7f6b",
    "lignite_coal_plant": "#a1887f",
    "coal_to_cement_fuel": "#9a8070",
    "lng_terminal": "#e8a838",
    "oil_boiler": "#b8956e",
    "oil_boiler_DH": "#c4a07a",
    "oil_boiler_industry": "#8d6a42",
    "oil_plant": "#3e2723",
    "oil_pipeline": "#b08a6e",
    "oil_storage": "#c0a080",
    "oil_to_diesel_conversion": "#b89878",
    "oil_to_gasoline_conversion": "#c4a488",
    "oil_to_kerosene_conversion": "#d0b098",
    "oil_to_naphtha_conversion": "#d8bca0",
    "refining": "#b08a6e",
    "crude_oil": "#a0795c",
    "waste_boiler_DH": "#a0a0a0",
    "waste_plant": "#b0b0b0",
    "waste_to_cement_fuel": "#909090",
    # Renewables
    "photovoltaics": "#f0c040",        # solar yellow
    "wind_onshore": "#4ca6a8",         # teal
    "wind_offshore": "#1b7e9a",        # deep blue-teal (distinct from onshore)
    "reservoir_hydro": "#1e88e5",      # blue
    "run-of-river_hydro": "#64b5f6",   # light blue
    "pumped_hydro": "#0d47a1",         # navy (storage)
    # Nuclear
    "nuclear": "#c850c0",
    # Biomass
    "biomass_plant": "#4caf50",
    "biomass_plant_CCS": "#43a047",
    "biomass_boiler": "#56b870",
    "biomass_boiler_DH": "#3cb371",
    "biomass_boiler_industry": "#4caf50",
    "biomass_to_cement_fuel": "#7cb342",
    "biomethane_conversion": "#76c76e",
    "anaerobic_digestion": "#8fbc8f",
    "methanol_from_biomass": "#9ccc65",
    "gasification": "#8bc34a",
    "pyrolysis": "#7cb342",
    # Hydrogen
    "electrolysis": "#00bcd4",
    "hydrogen_pipeline": "#4dd0e1",
    "fuel_cell": "#26c6da",
    "haber_bosch": "#00acc1",
    "hydrogen_to_cement_fuel": "#00acc1",
    "hydrogen_FC_ship": "#0288d1",
    "salt_cavern_storage": "#4dd0e1",
    "H2_DRI": "#26c6da",
    # Electric / heat pump
    "electrode_boiler": "#ff7043",
    "electrode_boiler_DH": "#f4511e",
    "electrode_boiler_industry": "#e64a19",
    "heat_pump": "#e91e63",
    "heat_pump_DH": "#c2185b",
    # Old model names (v2: generic industry, v3/v4_0: temp-level only)
    "heat_pump_industry": "#f06292",
    "heat_pump_industry_0_100": "#f06292",
    "heat_pump_industry_100_150": "#ec407a",
    "heat_pump_industry_150_200": "#c2185b",
    # New model names (v4_6+: temp + source)
    "heat_pump_industry_0_100_waste_heat": "#f06292",
    "heat_pump_industry_0_100_water": "#f8bbd0",
    "heat_pump_industry_100_150_waste_heat": "#ec407a",
    "heat_pump_industry_100_150_water": "#f48fb1",
    "heat_pump_industry_150_200_waste_heat": "#c2185b",
    "heat_pump_industry_150_200_water": "#e91e63",
    "battery": "#7e57c2",
    "power_line": "#9575cd",
    "district_heating_grid": "#ef5350",
    # Transport
    "BEV": "#558b2f",
    "ICE_petrol": "#bdbdbd",
    "ICE_diesel": "#9e9e9e",
    "HDT_diesel": "#9e9e9e",
    "HDT_BET": "#66bb6a",
    "HDT_FCEV": "#26a69a",
    "ammonia_ICE_ship": "#5c6bc0",
    "methanol_ICE_ship": "#7986cb",
    "diesel_ICE_ship": "#9e9e9e",
    # Steel
    "BF_BOF": "#4682b4",
    "BF_BOF_CCS": "#6a9fc8",
    "EAF": "#87ceeb",
    "NG_DRI": "#b0c4de",
    "NG_DRI_CCS": "#9ab0c8",
    "industrial_gas_consumer": "#d4a017",
    # Carbon
    "DAC": "#b39ddb",
    "carbon_pipeline": "#90a4ae",
    "carbon_storage": "#78909c",
    "cement_post_comb": "#90a4ae",
    "glass_post_comb": "#a99bc2",
    "ceramic_post_comb": "#b98bc2",
    # Very old model names (v1_0: "industrial_" prefix instead of "_industry" suffix)
    "industrial_biomass_boiler": "#4caf50",
    "industrial_coal_boiler": "#8b6e5a",
    "industrial_electrode_boiler": "#e64a19",
    "industrial_natural_gas_boiler": "#b8860b",
    "industrial_oil_boiler": "#b8956e",
    # Cement & industry
    "cement_kiln": "#a0a0a0",
    "glass_production": "#9370db",
    "ceramic_production": "#ba68c8",
    "paper_production": "#ce93d8",
    "food_production": "#f48fb1",
    # Supply / imports
    "natural_gas import": "#d4a017",
    "lng import": "#e8a838",
    "hard_coal import": "#8b6e5a",
    "waste import": "#a0a0a0",
    "crude_oil import": "#a0795c",
    # Chemicals
    "fischer_tropsch": "#8d6e63",
    "olefin_from_naphtha": "#a1887f",
    "olefin_from_methanol": "#bcaaa4",
    "methanol_from_hydrogen": "#80cbc4",
}

# ── Hatch map ─────────────────────────────────────────────────────────────────
# Explicit entries for industry-heat techs (from analyze_model.py)
HATCH_MAP: dict[str, str] = {
    "natural_gas_boiler_industry": "//",
    "biomass_boiler_industry": "//",
    "oil_boiler_industry": "//",
    "electrode_boiler_industry": "**",
    "heat_pump_industry_0_100_waste_heat": "\\\\",
    "heat_pump_industry_0_100_water": "//",
    "heat_pump_industry_100_150_waste_heat": "\\\\",
    "heat_pump_industry_100_150_water": "//",
    "heat_pump_industry_150_200_waste_heat": "\\\\",
    "heat_pump_industry_150_200_water": "//",
    "heat_industry_temp_conversion_150": "||",
    "heat_industry_temp_conversion_100": "||",
    "glass_production": "oo",
    "ceramic_production": "oo",
    "paper_production": "oo",
    "food_production": "oo",
    "industry_TES_water_0_100": "--",
    "industry_TES_water_100_150": "--",
    "industry_TES_steam_100_150": "--",
    "industry_TES_steam_150_200": "--",
    "ammonia_DSM": "xx",
    "ceramic_DSM": "xx",
    "clinker_DSM": "xx",
    "food_DSM": "xx",
    "glass_DSM": "xx",
    "methanol_DSM": "xx",
    "olefin_DSM": "xx",
    "paper_DSM": "xx",
    "primary_steel_DSM": "xx",
    "secondary_steel_DSM": "xx",
    "battery": "..",
    "pumped_hydro": "//",
    # Post-combustion CCS retrofits -- same "xx" family as the other CCS
    # retrofits below, added explicitly because their names don't contain
    # the substring "CCS" so the pattern-loop's `"CCS" in _name` rule below
    # never catches them.
    "cement_post_comb": "xx",
    "glass_post_comb": "xx",
    "ceramic_post_comb": "xx",
}
# Pattern-based for everything else in COLOR_MAP
for _name in COLOR_MAP:
    if _name in HATCH_MAP:
        continue
    if "boiler" in _name and "DH" in _name:
        HATCH_MAP[_name] = "///"
    elif "boiler" in _name:
        HATCH_MAP[_name] = "//"
    elif "turbine" in _name:
        HATCH_MAP[_name] = ".."
    elif "_DH" in _name or "district_heating" in _name:
        HATCH_MAP[_name] = "///"
    elif "_plant" in _name and "CCS" in _name:
        HATCH_MAP[_name] = "xx"
    elif "CCS" in _name:
        HATCH_MAP[_name] = "xx"
    elif "pipeline" in _name:
        HATCH_MAP[_name] = "||"
    elif "storage" in _name:
        HATCH_MAP[_name] = "--"
    elif "heat_pump" in _name:
        HATCH_MAP[_name] = "\\\\"
    elif "electrode" in _name:
        HATCH_MAP[_name] = "**"

FALLBACK_COLORS = plt.cm.tab20.colors + plt.cm.tab20b.colors + plt.cm.tab20c.colors


def _get_color(name: str, fallback_idx: int) -> str | tuple:
    return COLOR_MAP.get(name, FALLBACK_COLORS[fallback_idx % len(FALLBACK_COLORS)])


def _get_hatch(name: str) -> str:
    return HATCH_MAP.get(name, "")


def _text_color_for_bg(bg_color) -> str:
    from matplotlib.colors import to_rgb
    r, g, b = to_rgb(bg_color)
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return "white" if luminance < 0.45 else "black"


# ── Model discovery ───────────────────────────────────────────────────────────
# local_outputs/ and euler_outputs/ are two separate roots (not the flat
# OUTPUT_DIR itself), each searched independently so neither root directory is
# ever mistaken for a model name.

_NON_MODEL_DIRS = {"figures", "solver_files", "archive"}


def _search_var_dict(path: Path, max_depth: int = 2) -> Path | None:
    """BFS from `path` down to `max_depth` levels for a dir containing var_dict.h5.

    Depth 0 = `path` itself. Returns the first match found (dirs visited in
    sorted order at each level), or None if nothing is found within depth.
    """
    if not path.exists():
        return None
    frontier = [path]
    for _ in range(max_depth + 1):
        for d in frontier:
            if (d / "var_dict.h5").exists():
                return d
        next_frontier = []
        for d in frontier:
            try:
                next_frontier.extend(
                    sd for sd in sorted(d.iterdir())
                    if sd.is_dir() and not sd.name.startswith(".")
                )
            except PermissionError:
                continue
        frontier = next_frontier
    return None


def load_results(root: Path, model_name: str) -> Results:
    """Load a Results object for `model_name` under `root` (LOCAL_ROOT or EULER_ROOT)."""
    path = root / model_name
    if not path.exists():
        raise FileNotFoundError(f"Model output not found: {path}")
    match = _search_var_dict(path, max_depth=3)
    if match is None:
        raise FileNotFoundError(f"No var_dict.h5 found under {path}")
    return Results(path=str(match))


def get_available_models(root: Path, max_depth: int = 3) -> list[str]:
    """Names of `root`'s immediate subdirectories that resolve to a var_dict.h5
    within `max_depth` levels. `root` is LOCAL_ROOT or EULER_ROOT."""
    if not root.exists():
        return []
    models = []
    for d in sorted(root.iterdir()):
        if not d.is_dir() or d.name in _NON_MODEL_DIRS or d.name.startswith("."):
            continue
        if _search_var_dict(d, max_depth=max_depth) is not None:
            models.append(d.name)
    return models


def _match_scenario_base(name: str) -> str | None:
    """Match a discovered folder name (which may carry a run-comment suffix,
    e.g. "Crystal_Ball_HG_v7_0_no_flexibility_2025_10a_5a_interval_10ts") to
    its EULER_SCENARIO_ORDER base name. Longest matching prefix wins, since
    "Crystal_Ball_HG_v7_0" is itself a prefix of the other 5 scenario names."""
    matches = [b for b in EULER_SCENARIO_ORDER if name == b or name.startswith(b + "_")]
    return max(matches, key=len) if matches else None


def sort_euler_scenarios(names: list[str]) -> list[str]:
    """Order discovered euler model names by EULER_SCENARIO_ORDER; unrecognized
    names (e.g. a future 6th scenario) are appended alphabetically at the end."""
    def sort_key(name: str) -> tuple:
        base = _match_scenario_base(name)
        if base is not None:
            return (0, EULER_SCENARIO_ORDER.index(base))
        return (1, name)
    return sorted(names, key=sort_key)


def euler_label(name: str) -> str:
    base = _match_scenario_base(name)
    if base is not None:
        return EULER_SCENARIO_LABELS[base]
    return name.replace("Crystal_Ball_HG_", "")


@dataclass(frozen=True)
class Run:
    name: str          # folder name under LOCAL_ROOT or EULER_ROOT
    label: str         # short display label
    mode: str          # "local" | "euler"
    results: Results
    color: str          # positional slot color from SCENARIO_PALETTE


def fig_width_for_runs(n_runs: int, per_run: float = 3.4, legend_margin: float = 2.5) -> float:
    """Total figure width for a rows x n_runs comparison grid."""
    return legend_margin + per_run * max(n_runs, 1)


def get_available_years(r: Results) -> list[int]:
    # r.get_years() returns 0-based indices, not calendar years.
    # Derive calendar years from actual data columns (always > 1000).
    for var in ("flow_conversion_output", "capacity", "carbon_emissions_carrier"):
        try:
            df = r.get_total(var)
            if isinstance(df, pd.DataFrame) and not df.empty:
                years = sorted(
                    int(c) for c in df.columns
                    if isinstance(c, (int, float)) and float(c) > 1000
                )
                if years:
                    return years
        except Exception:
            continue
    return [2025]


# ── Plotting primitives ───────────────────────────────────────────────────────

def plot_stacked_bars_years(
    df: pd.DataFrame,
    title: str,
    unit: str,
    ax: plt.Axes,
    show_legend: bool = True,
    show_segment_labels: bool = False,
    compact: bool = False,
) -> None:
    title_fs = 10 if compact else 12
    tick_fs = 8 if compact else 9
    total_fs = 6 if compact else 7

    if df.empty:
        ax.set_title(title, fontsize=title_fs - 1, fontweight="bold")
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        return

    years = df.columns.tolist()
    techs = df.index.tolist()
    bar_width = 0.6
    labeled: set[str] = set()

    for year_idx, year in enumerate(years):
        bottom = 0.0
        for tech_idx, tech in enumerate(techs):
            val = df.loc[tech, year]
            if val < 1e-6:
                continue
            color = _get_color(tech, tech_idx)
            hatch = _get_hatch(tech)
            ax.bar(
                year_idx, val, bar_width, bottom=bottom,
                color=color, label=tech if tech not in labeled else None,
                edgecolor="white", linewidth=0.5, hatch=hatch,
            )
            if show_segment_labels and val > 0:
                ax.text(year_idx, bottom + val / 2, f"{val:,.0f}",
                        ha="center", va="center", fontsize=5,
                        color=_text_color_for_bg(color))
            bottom += val
            labeled.add(tech)
        ax.text(year_idx, bottom, f"{bottom:,.0f}",
                ha="center", va="bottom", fontsize=total_fs, fontweight="bold")

    ax.set_xticks(range(len(years)))
    ax.set_xticklabels([str(y) for y in years], fontsize=tick_fs)
    ax.set_ylabel(unit, fontsize=title_fs - 1)
    ax.set_title(title, fontsize=title_fs, fontweight="bold")
    ax.axhline(0, color="black", linewidth=0.5)

    if show_legend:
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(handles[::-1], labels[::-1],
                      bbox_to_anchor=(1.02, 1), loc="upper left",
                      fontsize=10, frameon=False)


def _stacked_extent(df: pd.DataFrame) -> tuple[float, float]:
    """Return (negative_bottom, positive_top) of the per-year stacked totals.

    For a stacked bar chart the visually relevant magnitude is the sum of all
    positive segments (top of the stack) and the sum of all negative segments
    (bottom of the stack) within each year/column. Returns (0.0, 0.0) for an
    empty dataframe.
    """
    if df is None or df.empty:
        return 0.0, 0.0
    numeric = df.apply(pd.to_numeric, errors="coerce")
    pos_top = numeric.clip(lower=0).sum(axis=0).max()
    neg_bottom = numeric.clip(upper=0).sum(axis=0).min()
    pos_top = float(pos_top) if pd.notna(pos_top) else 0.0
    neg_bottom = float(neg_bottom) if pd.notna(neg_bottom) else 0.0
    return neg_bottom, pos_top


def _apply_shared_ylim(axes: list, dfs: list, headroom: float = 0.08) -> None:
    """Give every axis in ``axes`` a common y-limit derived from ``dfs``.

    The limit spans from the most-negative stacked bottom to the most-positive
    stacked top across all supplied dataframes, with a little headroom. Does
    nothing when there is no non-zero data to bound.
    """
    bottoms, tops = zip(*(_stacked_extent(df) for df in dfs))
    bottom = min(bottoms)
    top = max(tops)
    if bottom == 0.0 and top == 0.0:
        return
    span = top - bottom
    pad = span * headroom if span > 0 else abs(top or bottom) * headroom
    lo = bottom - pad if bottom < 0 else bottom
    hi = top + pad if top > 0 else top
    if lo == hi:
        return
    for ax in axes:
        ax.set_ylim(lo, hi)


def plot_stacked_bars_years_n(
    axes: list,
    dfs: list,
    title: str,
    unit: str,
    names: list,
    show_segment_labels: bool = False,
) -> None:
    """Plot the same time-series chart for N runs in adjacent axes.

    Each run's name is put on its own title line (below the metric name) so
    titles stay short and don't force the subplot to shrink. Legend is only
    drawn on the last axis to avoid duplicating it, since all axes share the
    same technology categories.

    All axes are given a shared y-limit (computed from the per-year stacked
    totals across *all* dataframes) so runs are directly comparable by eye.
    Titles/ticks automatically shrink (`compact`) once there are more than 2
    runs, to keep narrow N-wide columns readable.
    """
    n = len(axes)
    compact = n > 2
    for i, (ax, df, name) in enumerate(zip(axes, dfs, names)):
        plot_stacked_bars_years(df, f"{title}\n{name}", unit, ax,
                                show_legend=(i == n - 1),
                                show_segment_labels=show_segment_labels,
                                compact=compact)
    _apply_shared_ylim(list(axes), list(dfs))


def plot_stacked_bars_years_pair(
    ax_a: plt.Axes,
    ax_b: plt.Axes,
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    title: str,
    unit: str,
    name_a: str,
    name_b: str,
    show_segment_labels: bool = False,
) -> None:
    """Backward-compatible 2-run wrapper around plot_stacked_bars_years_n."""
    plot_stacked_bars_years_n([ax_a, ax_b], [df_a, df_b], title, unit,
                              [name_a, name_b], show_segment_labels)


def add_price_line(ax: plt.Axes, price_series: pd.Series, label: str, color: str) -> None:
    if price_series.empty or (price_series.abs() < 1e-9).all():
        return
    ax2 = ax.twinx()
    ax2.plot(range(len(price_series)), price_series.values,
             color=color, linewidth=2, marker="o", markersize=5, label=label, zorder=5)
    ax2.set_ylabel(label, fontsize=9, color=color)
    ax2.tick_params(axis="y", labelcolor=color)
    ax2.legend(loc="upper right", fontsize=7, frameon=False)


def plot_stacked_bars(
    df: pd.DataFrame,
    title: str,
    unit: str,
    ax: plt.Axes,
    show_legend: bool = True,
    show_segment_labels: bool = False,
    color_map: dict | None = None,
    hatch_map: dict | None = None,
) -> None:
    """color_map/hatch_map override the global COLOR_MAP/HATCH_MAP for this
    call only (e.g. a print-figure-specific palette) — omit for the default,
    dashboard-shared look-up used everywhere else."""
    if df.empty:
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        return

    bar_width = 0.6
    models = df.columns.tolist()
    positive_df = df.clip(lower=0)
    negative_df = df.clip(upper=0)
    labeled: set[str] = set()

    def get_color(category: str, idx: int) -> str | tuple:
        if color_map is not None:
            return color_map.get(category, FALLBACK_COLORS[idx % len(FALLBACK_COLORS)])
        return _get_color(category, idx)

    def get_hatch(category: str) -> str:
        if hatch_map is not None:
            return hatch_map.get(category, "")
        return _get_hatch(category)

    for model_idx, model in enumerate(models):
        bottom_pos = 0.0
        bottom_neg = 0.0
        for cat_idx, category in enumerate(df.index):
            val_pos = positive_df.loc[category, model]
            val_neg = negative_df.loc[category, model]
            color = get_color(category, cat_idx)
            hatch = get_hatch(category)
            add_label = category not in labeled

            if val_pos > 0:
                ax.bar(model_idx, val_pos, bar_width, bottom=bottom_pos,
                       color=color, label=category if add_label else None,
                       edgecolor="white", linewidth=0.5, hatch=hatch)
                if show_segment_labels:
                    ax.text(model_idx, bottom_pos + val_pos / 2, f"{val_pos:,.0f}",
                            ha="center", va="center", fontsize=6,
                            color=_text_color_for_bg(color))
                bottom_pos += val_pos
                labeled.add(category)

            if val_neg < 0:
                ax.bar(model_idx, val_neg, bar_width, bottom=bottom_neg,
                       color=color, label=category if add_label else None,
                       edgecolor="white", linewidth=0.5, hatch=hatch if hatch else "//")
                if show_segment_labels:
                    ax.text(model_idx, bottom_neg + val_neg / 2, f"{val_neg:,.0f}",
                            ha="center", va="center", fontsize=6,
                            color=_text_color_for_bg(color))
                bottom_neg += val_neg
                labeled.add(category)

        ax.text(model_idx, bottom_pos, f"{positive_df[model].sum():,.0f}",
                ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_xticks(range(len(models)))
    if len(models) > 3:
        ax.set_xticklabels(models, fontsize=9, rotation=20, ha="right")
    else:
        ax.set_xticklabels(models, fontsize=9)
    ax.set_ylabel(unit, fontsize=11)
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.axhline(0, color="black", linewidth=0.5)

    if show_legend:
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(handles[::-1], labels[::-1],
                      bbox_to_anchor=(1.02, 1), loc="upper left",
                      fontsize=10, frameon=False)
