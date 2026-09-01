"""Every technology that produces or consumes a given carrier, system-wide,
in the cost-optimal 2050 no-flexibility/no-diffusion run -- ranked so
relative importance is legible at a glance, not just "is this technology
present". Generates one figure each for the three carriers that came out of
the "Power, Hydrogen, Carbon" sector-map conversation this script follows
on from -- electricity, hydrogen, carbon -- the three carriers with their
own cross-border transport technology (power_line/hydrogen_pipeline/
carbon_pipeline; see that conversation for why natural_gas/oil, which also
have pipelines, were deliberately left out of this series).

Source run: the MGA baseline (z*) solve for
Crystal_Ball_ind_heat_v8_0_no_flexibility_nodiffusion, i.e. the un-suffixed
folder under .../euler_outputs_mga/..._MGA_bbo/ -- the actual cost-optimal
model, not one of the *_supf_iter_N near-optimal MGA exploration points.
weights/sampling/bbo/oracle all re-solve the identical baseline (see
plot_mga_results.py's module docstring), so bbo's copy is as good as any;
this script just picks it via the same MODEL/RUN_PREFIX/*_DIR constants
plot_mga_results.py already uses, for one shared naming convention across
both scripts.

Color scheme: per-user-request, this figure does NOT use figure_settings'
per-technology COLOR_MAP/HATCH_MAP (too many technologies for distinct
colors to carry any real meaning here) -- instead every bar in a given
carrier's figure is that carrier's own ETH corporate-design color
(CARRIER_COLOR: electricity=ETH blue, hydrogen=ETH green, carbon=ETH
purple -- the same SCENARIO_PALETTE this repo's other figures already use,
per this project's "never invent a separate palette" convention). A
technology that ALSO appears (post-threshold) in another carrier's figure
gets a dashed hatch overlay in THAT other carrier's color on top of its
main solid color -- e.g. electrolysis is solid green in the hydrogen figure
(its main color there) with blue "--" dashes added because it's also active
in the electricity figure; in the electricity figure it's the reverse: solid
blue with green dashes. A technology active in all three (e.g.
methanol_from_hydrogen, which consumes hydrogen+carbon+electricity all at
once) gets two overlays: "--" dashes in one other color, "||" dashes in the
other. See build_active_carriers()/_draw_bar() for the implementation, and
CROSS_CARRIER_HATCHES for the two overlay patterns. The demand row is exempt
from all of this -- it's not a technology, always plain grey.

Three things a naive flow_conversion_input/output pass over a carrier would
get wrong, all handled explicitly here:

1. Unit isn't the same across carriers. Results.get_total() returns the
   full year's hourly flow already SUMMED to an annual total, but
   Results.get_unit() naively still reports the pre-summation per-hour
   label (see project memory on get_unit()/convert_to_yearly_unit, and
   generate_si_figures.py's _tech_fuel_by_carrier docstring for the same
   gotcha) -- electricity and hydrogen are power carriers (GW/h -> annual
   GWh), but carbon's own attributes.json declares "kilotCO2eq/hour", so
   its annual total is kt CO2eq, not GWh. CARRIER_UNIT below is read once
   from that fact, not assumed.

2. Exogenous final demand. electricity is one of the few carriers with a
   real demand.csv; hydrogen and carbon are pure intermediates with zero
   exogenous demand (confirmed on both here: r.get_total("demand") sums to
   0 for both). Demand never shows up in flow_conversion_input for any
   technology -- it's satisfied directly, off the carrier balance. For
   electricity this is in fact the SINGLE LARGEST offtake in the whole
   system (~2.76M GWh, bigger than electrolysis) -- a plot that only walked
   conversion technologies would silently misrepresent what actually
   consumes it. The demand row is only added when it's actually nonzero
   (electricity only, in practice), and is visually distinguished (grey,
   italic label) from every real technology bar so it's never mistaken for
   one.

3. Storage gets its OWN third panel, not folded into producers/consumers.
   A technology whose reference carrier is the one being plotted has both a
   charge (input) and a discharge (output) flow -- i.e. per the user's own
   framing, "if a tech is in producer and consumer, it's a storage tech".
   STORAGE_TECH_CARRIER is the (small, static) map from each of the 5
   storage technologies in this model to its own carrier, used to fetch
   flow_storage_charge/discharge directly rather than rediscovering the
   charge/consumer overlap at runtime -- equivalent for this dataset (no
   non-storage technology has the same carrier as both an input AND an
   output), but avoids a fragile heuristic doing double duty as a data
   lookup. carbon_storage is NOT a storage technology in this model (it's
   an ordinary conversion technology with input_carrier=[carbon],
   output_carrier=[] -- a pure sink), so it stays a normal consumer row.

Transport technologies (power_line/hydrogen_pipeline/carbon_pipeline) are
deliberately excluded from all three figures -- they redistribute a carrier
between nodes rather than producing or consuming it, so they net to ~0
system-wide and aren't a "how important is this technology" question the
way every other row here is.

Completeness check: before plotting, every technology this run actually
touches for a carrier is cross-checked against ZEN-creator's own technology
definitions for this exact model (input_carrier/output_carrier in each
set_technologies/*/attributes.json under
../ZEN-creator/outputs/<model>/, the sibling-repo convention already used by
scripts/extract_heat_demand_by_sector.py and run_model_local.py) -- so a
technology that's defined but never showed up active (or vice versa) prints
a warning instead of silently vanishing from the figure. This is what
confirmed, e.g., that glass_post_comb/ceramic_post_comb (post-combustion CCS
retrofits for glass/ceramic production -- not present in the older
data/Crystal_Ball/ base dataset this repo also ships, only in ZEN-creator's
v8_0 industry-heat extension) are real, active carbon-producing
technologies, not an omission.

Below THRESHOLD (1, in whatever unit the carrier uses -- i.e. essentially
solver-noise zeros around 1e-6 to 1e-9, not small-but-real technologies) a
technology is dropped from a figure entirely rather than shown as an
invisible sliver; the console table printed alongside each figure lists
exactly which technologies were dropped and why. This threshold is also
what "also active in another carrier's figure" means for the cross-carrier
hatch overlays above -- a technology whose flow in another carrier rounds
to ~0 does not get a dash for it.

Usage:
    python scripts/plot_carrier_flows.py
"""

import json
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch

from plots.figure_settings import SCENARIO_PALETTE, apply_font_mode, eth_tint
from zen_garden import Results

# See figure_settings.FONT_MODE for the rationale and for the one-flag
# toggle that switches every figure script in this repo at once.
apply_font_mode()

# Hatch lines default to a hairline 1.0pt (matplotlib's hatch.linewidth
# rcParam) -- far too faint to read as "dashes" at this figure's scale, so
# every hatch overlay this script draws gets a heavier stroke.
plt.rcParams["hatch.linewidth"] = 2.2

FIGURES_DIR = REPO_ROOT / "data" / "outputs" / "figures" / "mga_investment"
MGA_ROOT = REPO_ROOT / "data" / "outputs" / "euler_outputs_mga"
ZEN_CREATOR_OUTPUTS = REPO_ROOT.parent / "ZEN-creator" / "outputs"

MODEL = "Crystal_Ball_ind_heat_v8_0_no_flexibility_nodiffusion"
RUN_PREFIX = f"{MODEL}_2050_1a_5a_interval_5ts_MGA"
# The bbo run's own folder got renamed on Euler mid-project (plain "_bbo" ->
# "_bbo_relative", the old one moved under euler_outputs_mga/archive/) --
# try both suffixes rather than hardcoding one, so a future rename doesn't
# silently break this script again.
_BBO_SUFFIXES = ["_bbo_relative", "_bbo"]
_bbo_dir = next((MGA_ROOT / f"{RUN_PREFIX}{suffix}" for suffix in _BBO_SUFFIXES
                  if (MGA_ROOT / f"{RUN_PREFIX}{suffix}").exists()), MGA_ROOT / f"{RUN_PREFIX}{_BBO_SUFFIXES[0]}")
BASE_RUN_DIR = _bbo_dir / MODEL

CARRIERS = ["electricity", "hydrogen", "carbon"]

# Read off each carrier's own set_carriers/<carrier>/attributes.json
# ("demand" unit): electricity/hydrogen are power carriers (GW -> annual
# GWh after get_total's implicit integration); carbon is mass-rate
# ("kilotCO2eq/hour" -> annual kt CO2eq). See point 1 in the module
# docstring -- Results.get_unit() would NOT tell you this correctly.
CARRIER_UNIT = {"electricity": "GWh", "hydrogen": "GWh", "carbon": "kt CO2eq"}

# SCENARIO_PALETTE = [blue, petrol, green, bronze, red, purple, grey], the 7
# ETH corporate-design colors this repo's other figures already use (see
# figure_settings.py). power=blue, hydrogen=green, carbon=purple ("pink" in
# the user's own words -- ETH's palette has no true pink; purple/magenta is
# the closest official swatch, confirmed with the user).
CARRIER_COLOR = {
    "electricity": SCENARIO_PALETTE[0],  # ETH blue   #215CAF
    "hydrogen": SCENARIO_PALETTE[2],     # ETH green  #627313
    "carbon": SCENARIO_PALETTE[5],       # ETH purple #A7117A
}
# The cross-carrier dash overlays use a LIGHTER tint of the other carrier's
# color (ETH's own 40%-toward-white tint step, via figure_settings.eth_tint)
# rather than the full-saturation CARRIER_COLOR -- the raw colors are dark
# enough that a same-color-family hatch on top of a dark bar barely reads as
# a separate mark at all.
CROSS_CARRIER_HATCH_COLOR = {c: eth_tint(color, 0.4) for c, color in CARRIER_COLOR.items()}
# Overlay hatch pattern for the 1st vs. 2nd "other carrier" a technology
# also touches (order = CARRIERS, excluding the carrier of the current
# figure) -- forward-slash diagonal, then back-slash diagonal, so two
# overlaid other-carrier colors stay visually distinguishable from each
# other. Tripled (vs. a single "/"/"\") for a denser, more visible pattern.
CROSS_CARRIER_HATCHES = ["/" * 3, "\\" * 3]

# Short form used in the ratio annotations next to each bar (see
# build_tech_carrier_value/_ratio_str) -- full carrier names make that
# annotation too long to sit next to the value label.
CARRIER_ABBR = {"electricity": "elec", "hydrogen": "H2", "carbon": "CO2"}

# The 5 storage technologies in this model, each keyed to its own reference
# carrier -- only battery/pumped_hydro (electricity) and salt_cavern_storage
# (hydrogen) are relevant to the 3 carriers this script plots.
STORAGE_TECH_CARRIER = {
    "battery": "electricity",
    "pumped_hydro": "electricity",
    "salt_cavern_storage": "hydrogen",
    "natural_gas_storage": "natural_gas",
    "oil_storage": "oil",
}

THRESHOLD = 1.0  # drops ~1e-6..1e-9 solver-noise entries, keeps every real one

DEMAND_COLOR = "#9AA0A6"  # neutral grey, deliberately outside CARRIER_COLOR -- not a technology


def demand_row_label(carrier: str) -> str:
    return f"{carrier} (final demand)"


# ── Data ──────────────────────────────────────────────────────────────────

def load_base_run() -> Results:
    if not BASE_RUN_DIR.exists():
        raise FileNotFoundError(f"Base run not found: {BASE_RUN_DIR}")
    return Results(path=str(BASE_RUN_DIR))


def get_carrier_flows(r: Results, carrier: str) -> tuple[pd.Series, pd.Series, dict[str, tuple[float, float]]]:
    """(producers, consumers, storage) for `carrier`. producers/consumers are
    ordinary conversion technologies (+ the demand row on consumers, if
    nonzero) -- storage technologies are pulled out into their own dict of
    {tech: (charge, discharge)}, not duplicated into producers/consumers.
    All three thresholded to THRESHOLD and producers/consumers sorted
    descending."""
    flow_out = r.get_total("flow_conversion_output")
    flow_in = r.get_total("flow_conversion_input")
    producers = pd.Series(dtype=float)
    consumers = pd.Series(dtype=float)
    if carrier in flow_out.index.get_level_values("carrier"):
        producers = flow_out.xs(carrier, level="carrier").groupby("technology").sum().sum(axis=1)
    if carrier in flow_in.index.get_level_values("carrier"):
        consumers = flow_in.xs(carrier, level="carrier").groupby("technology").sum().sum(axis=1)

    demand = r.get_total("demand")
    if carrier in demand.index.get_level_values("carrier"):
        demand_total = demand.xs(carrier, level="carrier").sum().sum()
        if demand_total > THRESHOLD:
            consumers[demand_row_label(carrier)] = demand_total

    charge_all = r.get_total("flow_storage_charge")
    discharge_all = r.get_total("flow_storage_discharge")
    storage: dict[str, tuple[float, float]] = {}
    for tech, tech_carrier in STORAGE_TECH_CARRIER.items():
        if tech_carrier != carrier:
            continue
        chg = charge_all.xs(tech, level="technology").sum().sum() if tech in charge_all.index.get_level_values("technology") else 0.0
        dis = discharge_all.xs(tech, level="technology").sum().sum() if tech in discharge_all.index.get_level_values("technology") else 0.0
        if chg > THRESHOLD or dis > THRESHOLD:
            storage[tech] = (chg, dis)

    producers = producers[producers > THRESHOLD].sort_values(ascending=False)
    consumers = consumers[consumers > THRESHOLD].sort_values(ascending=False)
    return producers, consumers, storage


def build_active_carriers(all_flows: dict[str, tuple[pd.Series, pd.Series, dict]]) -> dict[str, set[str]]:
    """tech -> set of carriers it's active in (post-threshold), across
    producers and consumers only (not the demand row, not storage -- every
    storage technology in this model is single-carrier by construction, see
    STORAGE_TECH_CARRIER). Drives the cross-carrier hatch overlays."""
    active: dict[str, set[str]] = defaultdict(set)
    for carrier, (producers, consumers, _storage) in all_flows.items():
        for tech in producers.index:
            active[tech].add(carrier)
        for tech in consumers.index:
            if tech != demand_row_label(carrier):
                active[tech].add(carrier)
    return active


GROUP_ORDER = ["hydrogen", "carbon", "electricity_producers_storage", "electricity_consumers"]
GROUP_LABEL = {
    "hydrogen": "1. Hydrogen -- all producers, consumers & storage",
    "carbon": "2. Carbon -- all producers & consumers",
    "electricity_producers_storage": "3. Electricity -- producers & storage",
    "electricity_consumers": "4. Electricity -- other consumers",
}
# Which carrier's own producers/consumers/storage series a group's members
# are valued against -- both electricity groups obviously use electricity,
# but so does every group: a group is BY DEFINITION all valued in its own
# carrier (see build_groups) -- kept explicit here rather than inferred, so
# plot_by_group doesn't have to guess.
GROUP_CARRIER = {
    "hydrogen": "hydrogen", "carbon": "carbon",
    "electricity_producers_storage": "electricity", "electricity_consumers": "electricity",
}


def build_groups(all_flows: dict[str, tuple[pd.Series, pd.Series, dict]],
                   active_carriers: dict[str, set[str]]) -> dict[str, list[str]]:
    """Four investment-relevant groups (see plot_carrier_groups.py's module
    docstring for the full argument): a technology touching hydrogen or
    carbon is grouped there IN FULL (even if it also touches electricity);
    electricity keeps only its producers/storage and the consumers that
    touch NEITHER hydrogen nor carbon. hydrogen ∩ carbon technologies
    (e.g. methanol_from_hydrogen) are counted in BOTH groups 1 and 2, not
    split between them."""
    producers, consumers, storage = {}, {}, {}
    for carrier in CARRIERS:
        p, c, s = all_flows[carrier]
        producers[carrier], consumers[carrier], storage[carrier] = p, c, s

    elec_producers = [t for t in producers["electricity"].index if active_carriers[t] == {"electricity"}]
    elec_storage = list(storage["electricity"].keys())  # single-carrier by construction
    elec_consumers = [t for t in consumers["electricity"].index
                       if t != demand_row_label("electricity") and active_carriers[t] == {"electricity"}]

    hydrogen_all = sorted(set(producers["hydrogen"].index) |
                           {t for t in consumers["hydrogen"].index if t != demand_row_label("hydrogen")} |
                           set(storage["hydrogen"].keys()))
    carbon_all = sorted(set(producers["carbon"].index) |
                         {t for t in consumers["carbon"].index if t != demand_row_label("carbon")} |
                         set(storage["carbon"].keys()))

    return {
        "electricity_producers_storage": sorted(elec_producers) + sorted(elec_storage),
        "electricity_consumers": sorted(elec_consumers),
        "hydrogen": hydrogen_all,
        "carbon": carbon_all,
    }


def build_tech_carrier_value(all_flows: dict[str, tuple[pd.Series, pd.Series, dict]]) -> dict[tuple[str, str], float]:
    """(tech, carrier) -> that tech's flow value in that carrier's own
    figure (whichever of producers/consumers it's in there -- a tech can be
    a producer in one carrier and a consumer in another, e.g. electrolysis).
    Storage/demand excluded, same as build_active_carriers. Drives the
    per-bar cross-carrier ratio annotations (_ratio_str)."""
    values: dict[tuple[str, str], float] = {}
    for carrier, (producers, consumers, _storage) in all_flows.items():
        for tech, val in producers.items():
            values[(tech, carrier)] = val
        for tech, val in consumers.items():
            if tech != demand_row_label(carrier):
                values[(tech, carrier)] = val
    return values


def _fmt_ratio_num(x: float) -> str:
    return f"{x:.0f}" if x >= 10 else f"{x:.1f}"


def _ratio_str(val_this: float, val_other: float) -> str:
    """Compact 'a:1' / '1:b' ratio between two carriers' own flow values for
    the SAME technology -- a raw magnitude ratio, not unit-normalized (e.g.
    carbon is kt CO2eq, electricity/hydrogen are GWh; the ratio is only
    meaningful as "which figure is this technology's number bigger in",
    not as a physical conversion factor)."""
    r = val_this / val_other
    return f"{_fmt_ratio_num(r)}:1" if r >= 1 else f"1:{_fmt_ratio_num(1 / r)}"


def _ratio_annotation(tech: str, carrier: str, val: float, active_carriers: dict[str, set[str]],
                        tech_carrier_value: dict[tuple[str, str], float]) -> str:
    """' (1.9:1 vs H2)' / ' (1:64 vs H2, 1:14 vs CO2)' -- empty string for a
    technology that's single-carrier (nothing to compare against)."""
    others = [c for c in CARRIERS if c != carrier and c in active_carriers.get(tech, set())]
    if not others:
        return ""
    parts = [f"{_ratio_str(val, tech_carrier_value[(tech, other)])} vs {CARRIER_ABBR[other]}" for other in others]
    return f"  ({', '.join(parts)})"


def _carrier_touching_techs(model: str, carrier: str) -> tuple[set[str], set[str]]:
    """(input_techs, output_techs) that ZEN-creator's own attributes.json
    declares as touching `carrier` for `model`, scanning both
    set_conversion_technologies and its set_retrofitting_technologies
    subfolder. Empty sets (not an error) if the sibling repo/model isn't
    present -- the completeness check degrades to a no-op rather than
    failing the whole script over a machine-local sibling checkout."""
    tech_root = ZEN_CREATOR_OUTPUTS / model / "set_technologies"
    if not tech_root.exists():
        return set(), set()

    conv_dirs = [tech_root / "set_conversion_technologies"]
    retrofit_dir = conv_dirs[0] / "set_retrofitting_technologies"
    if retrofit_dir.exists():
        conv_dirs.append(retrofit_dir)

    input_techs, output_techs = set(), set()
    for conv_dir in conv_dirs:
        for tech_dir in sorted(conv_dir.iterdir()):
            if not tech_dir.is_dir() or tech_dir.name == "set_retrofitting_technologies":
                continue
            attrs_path = tech_dir / "attributes.json"
            if not attrs_path.exists():
                continue
            attrs = json.loads(attrs_path.read_text())

            def carriers(key: str) -> list[str]:
                val = attrs.get(key)
                val = val.get("default_value") if isinstance(val, dict) else val
                return val or []

            if carrier in carriers("input_carrier"):
                input_techs.add(tech_dir.name)
            if carrier in carriers("output_carrier"):
                output_techs.add(tech_dir.name)
    return input_techs, output_techs


def print_completeness_check(carrier: str, producers: pd.Series, consumers: pd.Series) -> None:
    """Cross-check the technologies this run actually shows against what
    ZEN-creator's own dataset declares as `carrier`-touching for the same
    model -- flags anything defined-but-missing or active-but-undeclared.
    producers/consumers no longer include storage technologies (they get
    their own panel -- see get_carrier_flows), so no subtraction needed
    here beyond the demand row."""
    defined_in, defined_out = _carrier_touching_techs(MODEL, carrier)
    if not defined_in and not defined_out:
        print(f"  (skipped: no ZEN-creator dataset found at {ZEN_CREATOR_OUTPUTS / MODEL})")
        return

    active_out = set(producers.index)
    active_in = set(consumers.index) - {demand_row_label(carrier)}

    missing_out = defined_out - active_out
    missing_in = defined_in - active_in
    extra_out = active_out - defined_out
    extra_in = active_in - defined_in

    if not (missing_out or missing_in or extra_out or extra_in):
        print(f"  OK: {len(defined_out)} producer + {len(defined_in)} consumer technologies "
              f"declared in ZEN-creator all match technologies active in the run.")
        return
    if missing_out:
        print(f"  declared but inactive (<= {THRESHOLD} {CARRIER_UNIT[carrier]}) as producers: {sorted(missing_out)}")
    if missing_in:
        print(f"  declared but inactive (<= {THRESHOLD} {CARRIER_UNIT[carrier]}) as consumers: {sorted(missing_in)}")
    if extra_out:
        print(f"  active as producers but not declared in ZEN-creator: {sorted(extra_out)}")
    if extra_in:
        print(f"  active as consumers but not declared in ZEN-creator: {sorted(extra_in)}")


def _format_value(x: float) -> str:
    if x >= 1e6:
        return f"{x / 1e6:.2f}M"
    if x >= 1e3:
        return f"{x / 1e3:.0f}k"
    return f"{x:.0f}"


def print_ranked_table(
    carrier: str, producers: pd.Series, consumers: pd.Series, storage: dict[str, tuple[float, float]],
    active_carriers: dict[str, set[str]], tech_carrier_value: dict[tuple[str, str], float],
) -> None:
    unit = CARRIER_UNIT[carrier]
    demand_label = demand_row_label(carrier)
    prod_total, cons_total = producers.sum(), consumers.sum()
    print(f"\n  Producers ({len(producers)} technologies, {_format_value(prod_total)} {unit} total):")
    for tech, val in producers.items():
        ratio = _ratio_annotation(tech, carrier, val, active_carriers, tech_carrier_value)
        print(f"    {tech:<40s} {_format_value(val):>8s} {unit}  ({100 * val / prod_total:5.1f}%){ratio}")
    print(f"\n  Consumers ({len(consumers)} technologies, {_format_value(cons_total)} {unit} total):")
    for tech, val in consumers.items():
        flag = "  <- final demand, not a technology" if tech == demand_label else ""
        ratio = _ratio_annotation(tech, carrier, val, active_carriers, tech_carrier_value)
        print(f"    {tech:<40s} {_format_value(val):>8s} {unit}  ({100 * val / cons_total:5.1f}%){flag}{ratio}")
    if storage:
        print(f"\n  Storage ({len(storage)} technologies -- both consumer AND producer, see module docstring):")
        for tech, (chg, dis) in sorted(storage.items(), key=lambda kv: -max(kv[1])):
            print(f"    {tech:<40s} charge {_format_value(chg):>8s} {unit}  |  discharge {_format_value(dis):>8s} {unit}")


# ── Plot ──────────────────────────────────────────────────────────────────

def _draw_bar(ax: plt.Axes, i: int, val: float, carrier: str, tech: str,
              active_carriers: dict[str, set[str]], demand_label: str) -> None:
    if tech == demand_label:
        ax.barh(i, val, color=DEMAND_COLOR, edgecolor="white", linewidth=0.5, height=0.72)
        return

    ax.barh(i, val, color=CARRIER_COLOR[carrier], edgecolor="white", linewidth=0.5, height=0.72)
    others = [c for c in CARRIERS if c != carrier and c in active_carriers.get(tech, set())]
    for hatch, other_carrier in zip(CROSS_CARRIER_HATCHES, others):
        ax.barh(i, val, facecolor="none", edgecolor=CROSS_CARRIER_HATCH_COLOR[other_carrier],
                 hatch=hatch, linewidth=0, height=0.72)


def _combined_legend(fig: plt.Figure, y_frac: float) -> None:
    """Unlike the old per-carrier figures (one fixed base color per figure),
    this combined figure's base color changes PER SECTION -- so the legend
    just spells out the general rule once (solid = this section's own
    carrier; tinted hatch = also active in another carrier, see that bar's
    own ratio annotation for which) rather than enumerating which specific
    carrier-pairs appear where."""
    handles = [Patch(facecolor=CARRIER_COLOR[c], edgecolor="white", label=c) for c in CARRIERS]
    handles.append(Patch(facecolor="white", edgecolor="#888888", hatch=CROSS_CARRIER_HATCHES[0],
                          label="also active in another carrier (tinted hatch; see ratio note)"))
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, y_frac),
               fontsize=8, frameon=False, ncols=4, handlelength=2.0, columnspacing=1.4)


def build_group_rows(
    carrier: str, members: list[str], producers: pd.Series, consumers: pd.Series,
    storage: dict[str, tuple[float, float]], demand_label: str | None,
) -> list[tuple[str, float, str]]:
    """(label, value, tech) rows for one group's section, sorted descending
    by value. `label` is what's shown on the y-axis (storage gets a
    charge/discharge suffix); `tech` is the plain technology name, kept
    separately so hatch/ratio lookups (keyed by real tech name) still work."""
    rows: list[tuple[str, float, str]] = []
    storage_techs = set(storage.keys())
    for tech in members:
        if tech in storage_techs:
            chg, dis = storage[tech]
            if dis > THRESHOLD:
                rows.append((f"{tech}  (discharge)", dis, tech))
            if chg > THRESHOLD:
                rows.append((f"{tech}  (charge)", chg, tech))
        elif tech in producers.index:
            rows.append((tech, float(producers[tech]), tech))
        elif tech in consumers.index:
            rows.append((tech, float(consumers[tech]), tech))
    if demand_label is not None and demand_label in consumers.index:
        rows.append((demand_label, float(consumers[demand_label]), demand_label))
    return sorted(rows, key=lambda row: -row[1])


def _plot_group_panel(
    ax: plt.Axes, rows: list[tuple[str, float, str]], title: str, xmax: float, unit: str,
    carrier: str, demand_label: str | None, active_carriers: dict[str, set[str]],
    tech_carrier_value: dict[tuple[str, str], float],
) -> None:
    for i, (_label, val, tech) in enumerate(rows):
        _draw_bar(ax, i, val, carrier, tech, active_carriers, demand_label or "")
        ratio = "" if tech == demand_label else _ratio_annotation(tech, carrier, val, active_carriers, tech_carrier_value)
        ax.text(val * 1.15, i, f"{_format_value(val)}{ratio}", va="center", ha="left", fontsize=7.5)

    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows], fontsize=8, fontfamily="monospace")
    for label_obj, (_label, _val, tech) in zip(ax.get_yticklabels(), rows):
        if tech == demand_label:
            label_obj.set_fontstyle("italic")
            label_obj.set_fontfamily("sans-serif")
            label_obj.set_color("#555555")
    ax.set_ylim(len(rows) - 0.5, -0.5)
    ax.set_xscale("log")
    ax.set_xlim(THRESHOLD * 0.8, xmax)
    ax.set_xlabel(f"annual flow, 2050 [{unit}]", fontsize=9)
    ax.set_title(f"{title}  (n={len(rows)} rows)", fontsize=11, fontweight="bold", loc="left",
                 color=CARRIER_COLOR[carrier])
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="x", labelsize=8)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", which="major", linewidth=0.4, alpha=0.4)


def plot_by_group(
    groups: dict[str, list[str]], all_flows: dict[str, tuple[pd.Series, pd.Series, dict]],
    active_carriers: dict[str, set[str]], tech_carrier_value: dict[tuple[str, str], float],
) -> plt.Figure:
    producers, consumers, storage = {}, {}, {}
    for carrier in CARRIERS:
        p, c, s = all_flows[carrier]
        producers[carrier], consumers[carrier], storage[carrier] = p, c, s

    sections = []
    for key in GROUP_ORDER:
        carrier = GROUP_CARRIER[key]
        demand_label = demand_row_label(carrier) if key == "electricity_consumers" else None
        rows = build_group_rows(carrier, groups[key], producers[carrier], consumers[carrier],
                                  storage[carrier], demand_label)
        sections.append((key, carrier, demand_label, rows))

    row_h = 0.26           # inches per bar -- see plot_carrier_flows' section-height comment below
    top_margin = 1.75      # suptitle (2 lines) + legend (1 row) + 1st section's own title, above section 1
    gap = 0.7               # a section's xlabel/ticks + next section's title
    bottom_margin = 1.15   # last section's xlabel/ticks + footer caption, below it

    section_heights = [row_h * len(rows) for *_row_meta, rows in sections]
    fig_h = top_margin + sum(section_heights) + gap * (len(sections) - 1) + bottom_margin

    fig = plt.figure(figsize=(9.5, fig_h))
    y_cursor = fig_h - top_margin
    axes = []
    for h in section_heights:
        y_cursor -= h
        axes.append(fig.add_axes([0.03, y_cursor / fig_h, 0.94, h / fig_h]))
        y_cursor -= gap
    y_cursor += gap  # undo the trailing gap subtracted after the last section

    for (key, carrier, demand_label, rows), ax in zip(sections, axes):
        unit = CARRIER_UNIT[carrier]
        xmax = max(val for _l, val, _t in rows) * 5
        _plot_group_panel(ax, rows, GROUP_LABEL[key], xmax, unit, carrier, demand_label,
                            active_carriers, tech_carrier_value)

    _combined_legend(fig, 1 - 0.95 / fig_h)

    fig.suptitle(
        "Technologies by investment group -- Crystal Ball v8.0,\n"
        "no flexibility / no diffusion, cost-optimal 2050",
        fontsize=13, fontweight="bold", y=1 - 0.2 / fig_h,
    )
    fig.text(
        0.03, (y_cursor - 0.4) / fig_h,
        "Same per-technology values as the earlier per-carrier figures, reorganized into the four investment "
        "groups (see plot_carrier_groups.py): hydrogen and carbon absorb every technology that touches them, "
        "in full -- methanol_from_hydrogen appears in BOTH groups 1 and 2, with its own value in each, not "
        "split between them. Electricity keeps only what's exclusively electricity, split into its producers "
        "& storage vs. its other consumers. Ratio annotations and hatch colors carry the same meaning as "
        "before. Storage rows show charge and discharge separately. Transport technologies are excluded; "
        f"technologies at or below {THRESHOLD:.0f} (native unit)/yr are omitted.",
        fontsize=7.5, color="#555555", ha="left", va="top", wrap=True,
    )
    return fig


def main() -> None:
    print(f"Loading base run: {BASE_RUN_DIR.relative_to(REPO_ROOT)}")
    r = load_base_run()

    all_flows = {carrier: get_carrier_flows(r, carrier) for carrier in CARRIERS}
    active_carriers = build_active_carriers(all_flows)
    tech_carrier_value = build_tech_carrier_value(all_flows)
    groups = build_groups(all_flows, active_carriers)

    for carrier in CARRIERS:
        producers, consumers, storage = all_flows[carrier]
        print(f"\n{'=' * 60}\n{carrier.upper()}\n{'=' * 60}")
        print("Completeness check vs. ZEN-creator technology definitions:")
        print_completeness_check(carrier, producers, consumers)
        print_ranked_table(carrier, producers, consumers, storage, active_carriers, tech_carrier_value)

    fig = plot_by_group(groups, all_flows, active_carriers, tech_carrier_value)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_DIR / "fig_producers_consumers_by_group.svg"
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"\nSaved {out_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
