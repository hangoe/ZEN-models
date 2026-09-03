"""Shared constants, helpers, and plotting primitives: color/hatch maps, model
discovery, Results loading, and matplotlib plotting primitives. Used by both
the Streamlit dashboard (streamlit/app.py) and standalone figure-generation
scripts (e.g. generate_si_figures.py) — this module owns no UI logic itself."""

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from zen_garden import Results

OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "outputs"
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


# ── ETH color families ──────────────────────────────────────────────────────
# The 7 SCENARIO_PALETTE hues, named for readability below. COLOR_MAP (further
# below) assigns one base hue per physical/fuel family and shades sub-variants
# with eth_tint -- same mechanism generate_si_figures.py's local
# HEAT_SUPPLY_COLOR_MAP/PRODUCTION_COLOR_MAP already use (reused verbatim here
# for the techs that also appear there, e.g. the industry heat pump/boiler
# water-vs-waste-heat-source and per-fuel hue choices). Where several techs of
# the same family appear as adjacent bars in ONE chart (e.g. compare_models.py's
# 16-tech "industry process costs" figure, or the emissions carrier/technology
# panels), each gets a genuinely DIFFERENT hue rather than a tint of the same
# one -- tints of one hue read as near-identical at print size (user feedback
# on an earlier fossil-boiler palette: "coal, oil and NG look very similar,
# and waste and biomass aswell"), so same-hue tints below are reserved for
# variants that are unlikely to share an axis (e.g. different pipeline/storage/
# conversion steps of the same fuel).
_ETH_BLUE, _ETH_PETROL, _ETH_GREEN, _ETH_BRONZE, _ETH_RED, _ETH_PURPLE, _ETH_GREY = SCENARIO_PALETTE

# ── Merged, ETH-only color palette ──────────────────────────────────────────
# This is the ONE color map used everywhere outside the SI print figures
# (which define their own local ETH-derived palettes instead -- see
# generate_si_figures.py's HEAT_SUPPLY_COLOR_MAP etc.): the Streamlit
# dashboard and analyze_model.py/compare_models.py. Replaces the old
# arbitrary-hex COLOR_MAP entirely -- no off-brand colors remain.
COLOR_MAP = {
    # Industry heat carriers -- same water(blue)/waste-heat(petrol) source
    # convention as HEAT_SUPPLY_COLOR_MAP, darker at higher temperature.
    "heat_industry_0_100": eth_tint(_ETH_BLUE, 0.55),
    "heat_industry_100_150": eth_tint(_ETH_BLUE, 0.3),
    "heat_industry_150_200": _ETH_BLUE,
    "heat_industry_temp_conversion_150": eth_tint(_ETH_PETROL, 0.3),
    "heat_industry_temp_conversion_100": eth_tint(_ETH_PETROL, 0.55),
    # TES -- same family/band as the carrier it stores.
    "industry_TES_water_0_100": eth_tint(_ETH_BLUE, 0.55),
    "industry_TES_water_100_150": eth_tint(_ETH_BLUE, 0.3),
    "industry_TES_steam_100_150": eth_tint(_ETH_PETROL, 0.3),
    "industry_TES_steam_150_200": _ETH_PETROL,
    # DSM -- 10 mutually distinguishable hue/tint pairs, loosely tied to each
    # product's own color where one exists (steel=blue, ammonia/paper=petrol,
    # food=green, ceramic=bronze, clinker/glass=grey, methanol/olefin=red);
    # HATCH_MAP's "xx" already flags "this is a DSM bar" on top.
    "ammonia_DSM": _ETH_PETROL,
    "ceramic_DSM": _ETH_BRONZE,
    "clinker_DSM": _ETH_GREY,
    "food_DSM": _ETH_GREEN,
    "glass_DSM": eth_tint(_ETH_GREY, 0.4),
    "methanol_DSM": eth_tint(_ETH_RED, 0.3),
    "olefin_DSM": _ETH_RED,
    "paper_DSM": eth_tint(_ETH_PETROL, 0.4),
    "primary_steel_DSM": _ETH_BLUE,
    "secondary_steel_DSM": eth_tint(_ETH_BLUE, 0.4),
    # Carriers (emissions-by-carrier panel) -- 6 mutually distinct hues, all
    # bars in one chart.
    "crude_oil (carrier)": _ETH_BRONZE,
    "natural_gas (carrier)": _ETH_RED,
    "hard_coal (carrier)": _ETH_GREY,
    "lng (carrier)": _ETH_PETROL,
    "lignite (carrier)": _ETH_GREEN,
    "waste (carrier)": _ETH_PURPLE,
    # Technologies (emissions-by-technology panel) -- own 5-way distinct set,
    # separate panel from the carriers above so no cross-panel collision risk.
    "cement_kiln (tech)": _ETH_GREY,
    "BF_BOF (tech)": eth_tint(_ETH_GREY, 0.35),
    "EAF (tech)": _ETH_BLUE,
    "NG_DRI (tech)": _ETH_RED,
    "glass_production (tech)": _ETH_PURPLE,
    # Fossil / fuel technologies -- one hue per fuel (natural_gas=red,
    # coal=grey, oil=bronze), tint shades context (plant/boiler/pipeline/
    # storage/conversion) within a fuel -- these rarely share an axis.
    "natural_gas_boiler": _ETH_RED,
    "natural_gas_boiler_DH": eth_tint(_ETH_RED, 0.2),
    "natural_gas_boiler_industry": _ETH_RED,
    "natural_gas_turbine": eth_tint(_ETH_RED, 0.35),
    "natural_gas_turbine_CCS": eth_tint(_ETH_RED, 0.5),
    "natural_gas_pipeline": eth_tint(_ETH_RED, 0.65),
    "natural_gas_storage": eth_tint(_ETH_RED, 0.75),
    "SMR": eth_tint(_ETH_RED, 0.4),
    "SMR_CCS": eth_tint(_ETH_RED, 0.55),
    "methanol_from_natural_gas": eth_tint(_ETH_RED, 0.6),
    "methanation": eth_tint(_ETH_RED, 0.7),
    "hard_coal_plant": _ETH_GREY,
    "hard_coal_boiler_DH": eth_tint(_ETH_GREY, 0.2),
    "lignite_coal_plant": eth_tint(_ETH_GREY, 0.35),
    "coal_to_cement_fuel": eth_tint(_ETH_GREY, 0.6),
    "lng_terminal": eth_tint(_ETH_PETROL, 0.2),
    "oil_boiler": _ETH_BRONZE,
    "oil_boiler_DH": eth_tint(_ETH_BRONZE, 0.2),
    "oil_boiler_industry": _ETH_BRONZE,
    "oil_plant": eth_tint(_ETH_BRONZE, 0.35),
    "oil_pipeline": eth_tint(_ETH_BRONZE, 0.5),
    "oil_storage": eth_tint(_ETH_BRONZE, 0.6),
    "oil_to_diesel_conversion": eth_tint(_ETH_BRONZE, 0.45),
    "oil_to_gasoline_conversion": eth_tint(_ETH_BRONZE, 0.55),
    "oil_to_kerosene_conversion": eth_tint(_ETH_BRONZE, 0.65),
    "oil_to_naphtha_conversion": eth_tint(_ETH_BRONZE, 0.75),
    "refining": eth_tint(_ETH_BRONZE, 0.5),
    "crude_oil": _ETH_BRONZE,
    "waste_boiler_DH": _ETH_PURPLE,
    "waste_boiler_industry": _ETH_PURPLE,
    "waste_plant": eth_tint(_ETH_PURPLE, 0.2),
    "waste_to_cement_fuel": eth_tint(_ETH_PURPLE, 0.35),
    # Renewables -- hydro (blue family, 3 distinct tints), wind (petrol
    # family, 2 tints), solar (bronze, warm-ish without a true ETH yellow).
    "photovoltaics": _ETH_BRONZE,
    "wind_onshore": eth_tint(_ETH_PETROL, 0.35),
    "wind_offshore": _ETH_PETROL,
    "reservoir_hydro": _ETH_BLUE,
    "run-of-river_hydro": eth_tint(_ETH_BLUE, 0.35),
    "pumped_hydro": eth_tint(_ETH_BLUE, 0.6),
    # Nuclear -- singleton, purple tint (rarely shares an axis with waste/CCS).
    "nuclear": eth_tint(_ETH_PURPLE, 0.55),
    # Biomass -- green family; boilers reuse HEAT_SUPPLY_COLOR_MAP's exact
    # tint+hatch convention (same hue as electrode, lighter + hatched).
    "biomass_plant": _ETH_GREEN,
    "biomass_plant_CCS": eth_tint(_ETH_GREEN, 0.2),
    "biomass_boiler": eth_tint(_ETH_GREEN, 0.55),
    "biomass_boiler_DH": eth_tint(_ETH_GREEN, 0.55),
    "biomass_boiler_industry": eth_tint(_ETH_GREEN, 0.55),
    "biomass_to_cement_fuel": eth_tint(_ETH_GREEN, 0.35),
    "biomethane_conversion": eth_tint(_ETH_GREEN, 0.45),
    "anaerobic_digestion": eth_tint(_ETH_GREEN, 0.65),
    "methanol_from_biomass": eth_tint(_ETH_GREEN, 0.7),
    "gasification": eth_tint(_ETH_GREEN, 0.5),
    "pyrolysis": eth_tint(_ETH_GREEN, 0.4),
    # Hydrogen -- petrol family.
    "electrolysis": _ETH_PETROL,
    "hydrogen_pipeline": eth_tint(_ETH_PETROL, 0.35),
    "fuel_cell": eth_tint(_ETH_PETROL, 0.2),
    "haber_bosch": eth_tint(_ETH_PETROL, 0.5),
    "hydrogen_to_cement_fuel": eth_tint(_ETH_PETROL, 0.65),
    "hydrogen_FC_ship": eth_tint(_ETH_PETROL, 0.6),
    "salt_cavern_storage": eth_tint(_ETH_PETROL, 0.35),
    "H2_DRI": eth_tint(_ETH_PETROL, 0.15),
    # Electric / heat pump -- grid/electricity = blue, electrode boilers =
    # green (matches HEAT_SUPPLY_COLOR_MAP; "both are the non-fossil boilers").
    "electrode_boiler": _ETH_GREEN,
    "electrode_boiler_DH": eth_tint(_ETH_GREEN, 0.15),
    "electrode_boiler_industry": _ETH_GREEN,
    "coal_boiler_industry": _ETH_GREY,
    "heat_pump": _ETH_BLUE,
    "heat_pump_DH": eth_tint(_ETH_BLUE, 0.2),
    # Old model names (v2: generic industry, v3/v4_0: temp-level only) -- no
    # water/waste_heat split yet, default to the water(blue) convention.
    "heat_pump_industry": eth_tint(_ETH_BLUE, 0.4),
    "heat_pump_industry_0_100": eth_tint(_ETH_BLUE, 0.55),
    "heat_pump_industry_100_150": eth_tint(_ETH_BLUE, 0.3),
    "heat_pump_industry_150_200": _ETH_BLUE,
    # New model names (v4_6+: temp + source) -- matches HEAT_SUPPLY_COLOR_MAP
    # exactly: water source = blue, waste heat source = petrol, darker at
    # higher temperature.
    "heat_pump_industry_0_100_waste_heat": eth_tint(_ETH_PETROL, 0.55),
    "heat_pump_industry_0_100_water": eth_tint(_ETH_BLUE, 0.55),
    "heat_pump_industry_100_150_waste_heat": eth_tint(_ETH_PETROL, 0.3),
    "heat_pump_industry_100_150_water": eth_tint(_ETH_BLUE, 0.3),
    "heat_pump_industry_150_200_waste_heat": _ETH_PETROL,
    "heat_pump_industry_150_200_water": _ETH_BLUE,
    "battery": eth_tint(_ETH_BLUE, 0.45),
    "power_line": eth_tint(_ETH_BLUE, 0.6),
    "district_heating_grid": _ETH_GREY,
    # Transport -- energy source sets the hue (electric=blue, H2=petrol,
    # oil-derived=bronze, methanol=red).
    "BEV": eth_tint(_ETH_BLUE, 0.25),
    "ICE_petrol": _ETH_BRONZE,
    "ICE_diesel": eth_tint(_ETH_BRONZE, 0.2),
    "HDT_diesel": eth_tint(_ETH_BRONZE, 0.35),
    "HDT_BET": eth_tint(_ETH_BLUE, 0.45),
    "HDT_FCEV": eth_tint(_ETH_PETROL, 0.25),
    "ammonia_ICE_ship": eth_tint(_ETH_PETROL, 0.45),
    "methanol_ICE_ship": eth_tint(_ETH_RED, 0.45),
    "diesel_ICE_ship": eth_tint(_ETH_BRONZE, 0.5),
    # Steel -- colored by energy input (BF_BOF=coal/grey, EAF=electric/blue,
    # NG_DRI=gas/red, H2_DRI=hydrogen/petrol above), matching the physical
    # fuel logic used everywhere else in this map.
    "BF_BOF": eth_tint(_ETH_GREY, 0.35),
    "BF_BOF_CCS": eth_tint(_ETH_GREY, 0.5),
    "EAF": _ETH_BLUE,
    "NG_DRI": _ETH_RED,
    "NG_DRI_CCS": eth_tint(_ETH_RED, 0.3),
    "industrial_gas_consumer": eth_tint(_ETH_RED, 0.35),
    # Carbon -- purple/CCS family.
    "DAC": _ETH_PURPLE,
    "carbon_pipeline": eth_tint(_ETH_PURPLE, 0.3),
    "carbon_storage": eth_tint(_ETH_PURPLE, 0.45),
    "cement_post_comb": eth_tint(_ETH_PURPLE, 0.15),
    "glass_post_comb": eth_tint(_ETH_PURPLE, 0.55),
    "ceramic_post_comb": eth_tint(_ETH_PURPLE, 0.65),
    # Very old model names (v1_0: "industrial_" prefix instead of "_industry"
    # suffix) -- mirror their current-name counterpart exactly.
    "industrial_biomass_boiler": eth_tint(_ETH_GREEN, 0.55),
    "industrial_coal_boiler": _ETH_GREY,
    "industrial_electrode_boiler": _ETH_GREEN,
    "industrial_natural_gas_boiler": _ETH_RED,
    "industrial_oil_boiler": _ETH_BRONZE,
    # Cement & industry -- these 5 plus the 6 steel/DRI/carbon-fuel entries
    # above all appear together in compare_models.py's 16-tech "industry
    # process costs" chart, so glass_production here deliberately does NOT
    # reuse PRODUCTION_COLOR_MAP's grey (that would collide with cement_kiln/
    # BF_BOF/coal_to_cement_fuel's grey cluster in that same chart).
    "cement_kiln": _ETH_GREY,
    "glass_production": eth_tint(_ETH_PURPLE, 0.7),
    "ceramic_production": _ETH_BRONZE,
    "paper_production": eth_tint(_ETH_PETROL, 0.4),
    "food_production": _ETH_GREEN,
    # Supply / imports -- same hue as the matching carrier/plain entry above.
    "natural_gas import": _ETH_RED,
    "lng import": _ETH_PETROL,
    "hard_coal import": _ETH_GREY,
    "waste import": _ETH_PURPLE,
    "crude_oil import": _ETH_BRONZE,
    # Chemicals
    "fischer_tropsch": eth_tint(_ETH_BRONZE, 0.4),
    "olefin_from_naphtha": eth_tint(_ETH_BRONZE, 0.55),
    "olefin_from_methanol": eth_tint(_ETH_RED, 0.5),
    "methanol_from_hydrogen": eth_tint(_ETH_PETROL, 0.45),
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

# ETH-only fallback for any tech missing from COLOR_MAP above (replaces
# matplotlib's tab20/tab20b/tab20c, which aren't ETH colors): cycle through
# all 7 hues at 5 tint levels (35 combinations) rather than repeating a
# tech-family's own tints, so a fallback color never collides with the same
# family's real COLOR_MAP entries.
FALLBACK_COLORS = tuple(
    eth_tint(hue, pct)
    for pct in (0.0, 0.2, 0.4, 0.55, 0.7)
    for hue in SCENARIO_PALETTE
)


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
