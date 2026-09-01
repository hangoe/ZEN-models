"""Argues and visualizes a technology-grouping rule for investment analysis,
built directly on top of plot_carrier_flows.py's data: every technology that
touches hydrogen OR carbon (even if it also touches electricity) is grouped
under that carrier in full; electricity keeps only the technologies that
are EXCLUSIVELY electricity. Four final groups (per user request, storage
folded into "producers"  -- it's supply-side infrastructure, not a distinct
demand story):
    1. Electricity -- producers & storage
    2. Electricity -- consumers (no hydrogen/carbon overlap)
    3. Hydrogen -- all technologies touching hydrogen
    4. Carbon -- all technologies touching carbon

Why this asymmetry (H2/carbon "claim" their overlaps, electricity doesn't)
makes sense for an investment-clustering read, not just a bookkeeping
choice: electricity is the base/background carrier -- huge exogenous demand
(2.76M GWh), a large generation fleet, and a long tail of ordinary sector-
coupling consumers (heat pumps, EVs, industrial process heat) that are
simply "more electricity demand", not a distinct infrastructure story.
Hydrogen and carbon, by contrast, have ZERO exogenous demand of their own
(confirmed in plot_carrier_flows.py) -- every GWh/kt they carry exists
purely because SOME technology was built to produce or use it. A technology
that draws electricity to make hydrogen (electrolysis) or to capture carbon
(DAC, the CCS retrofits) is not "electricity demand" in the same sense
heat_pump is -- its electricity draw IS the cost of building the hydrogen/
carbon economy. Folding it back into "electricity" would double-count that
story and dilute electricity's group into something no longer just "the
grid". So: hydrogen and carbon absorb every technology that touches them
(including from each other -- methanol_from_hydrogen touches both and is
counted in BOTH, not forced into one), and electricity is left as the
residual: only what's exclusively electricity.

This version replaces the earlier 3-circle Venn (data/outputs/figures/
mga_investment/fig_technology_groups.svg, same file, overwritten) with two
genuinely quantitative panels instead, per explicit request for "something
different" and "more quantitative" than an admittedly-indicative,
not-area-proportional Venn:

  1. A Marimekko-style mosaic: column WIDTH is exactly proportional to each
     group's technology count (a real proportional area, unlike the old
     Venn's disclaimed "indicative" circles), and each column's internal
     stacking shows what fraction of ITS OWN members also touch another
     carrier -- reusing the exact cross-carrier hatch/tint visual language
     from plot_carrier_flows.py (light diagonal hatch in the other
     carrier's tinted color) so this figure reads as part of the same
     series rather than a one-off style.
  2. A magnitude roll-up: each group's actual annual flow total (GWh for
     the two electricity groups and for hydrogen, kt CO2eq for carbon --
     see plot_carrier_flows.py's own unit note; the two units are NOT
     combined into one chart). Storage's contribution to the electricity
     "producers & storage" group is its NET (discharge minus charge) --
     battery/pumped_hydro are both small NET CONSUMERS here due to round-
     trip losses, which is worth seeing honestly rather than only ever
     showing their gross discharge.

Usage:
    python scripts/plot_carrier_groups.py
"""

from collections import defaultdict

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.patheffects import withStroke
from matplotlib.ticker import FuncFormatter

from figure_settings import apply_font_mode

# See figure_settings.FONT_MODE for the rationale and for the one-flag
# toggle that switches every figure script in this repo at once.
apply_font_mode()
from plot_carrier_flows import (
    CARRIER_COLOR,
    CARRIER_UNIT,
    CARRIERS,
    CROSS_CARRIER_HATCHES,
    CROSS_CARRIER_HATCH_COLOR,
    FIGURES_DIR,
    REPO_ROOT,
    build_active_carriers,
    build_groups,
    demand_row_label,
    get_carrier_flows,
    load_base_run,
)

E, H, C = "electricity", "hydrogen", "carbon"


def print_group_summary(groups: dict[str, list[str]]) -> None:
    print("\nFinal groups (4):")
    print(f"  1. Electricity -- producers & storage ({len(groups['electricity_producers_storage'])}): "
          f"{groups['electricity_producers_storage']}")
    print(f"  2. Electricity -- consumers, no H2/carbon overlap ({len(groups['electricity_consumers'])}): "
          f"{groups['electricity_consumers']}")
    print(f"  3. Hydrogen -- all ({len(groups['hydrogen'])}): {groups['hydrogen']}")
    print(f"  4. Carbon -- all ({len(groups['carbon'])}): {groups['carbon']}")
    overlap = sorted(set(groups["hydrogen"]) & set(groups["carbon"]))
    print(f"  (hydrogen ∩ carbon, counted in both 3 and 4: {len(overlap)}: {overlap})")


# ── Magnitudes ───────────────────────────────────────────────────────────

def compute_group_magnitudes(all_flows: dict, groups: dict[str, list[str]]) -> dict[str, float]:
    producers, consumers, storage = {}, {}, {}
    for carrier in CARRIERS:
        p, c, s = all_flows[carrier]
        producers[carrier], consumers[carrier], storage[carrier] = p, c, s

    def sum_members(series, members: set[str]) -> float:
        return float(series[series.index.isin(members)].sum())

    elec_group = set(groups["electricity_producers_storage"])
    elec_storage_members = elec_group & set(storage[E].keys())
    elec_supply = sum_members(producers[E], elec_group)
    elec_supply += sum(storage[E][t][1] for t in elec_storage_members)   # + discharge
    elec_supply -= sum(storage[E][t][0] for t in elec_storage_members)   # - charge (net storage contribution)

    elec_demand = sum_members(consumers[E], set(groups["electricity_consumers"]))

    h2_group = set(groups["hydrogen"])
    h2_storage_members = h2_group & set(storage[H].keys())
    h2_produced = sum_members(producers[H], h2_group) + sum(storage[H][t][1] for t in h2_storage_members)
    h2_consumed = sum_members(consumers[H], h2_group) + sum(storage[H][t][0] for t in h2_storage_members)

    c_group = set(groups["carbon"])
    c_produced = sum_members(producers[C], c_group)
    c_consumed = sum_members(consumers[C], c_group)

    return {
        "electricity_producers_storage": elec_supply,
        "electricity_consumers": elec_demand,
        "hydrogen_produced": h2_produced,
        "hydrogen_consumed": h2_consumed,
        "carbon_produced": c_produced,
        "carbon_consumed": c_consumed,
    }


# ── Mosaic panel ─────────────────────────────────────────────────────────

MOSAIC_COLUMNS = [
    ("Electricity\nproducers & storage", E, "electricity_producers_storage"),
    ("Electricity\nconsumers", E, "electricity_consumers"),
    ("Hydrogen\n(all)", H, "hydrogen"),
    ("Carbon\n(all)", C, "carbon"),
]


def _composition(carrier: str, members: list[str], active_carriers: dict[str, set[str]]) -> list[tuple[frozenset, list[str]]]:
    """Group `members` by which OTHER carriers each also touches (empty
    frozenset = exclusive to `carrier`). Storage technologies are never
    keys in active_carriers (single-carrier by construction), so they fall
    through to "exclusive" automatically. Sorted: exclusive first, then by
    number of other carriers, then by CARRIERS order."""
    buckets: dict[frozenset, list[str]] = defaultdict(list)
    for t in members:
        others = frozenset(active_carriers.get(t, set())) - {carrier}
        buckets[others].append(t)

    def sort_key(item):
        others = item[0]
        return (len(others), [CARRIERS.index(c) for c in sorted(others, key=CARRIERS.index)])

    return sorted(buckets.items(), key=sort_key)


def plot_mosaic(ax: plt.Axes, groups: dict[str, list[str]], active_carriers: dict[str, set[str]]) -> None:
    counts = [len(groups[key]) for _, _, key in MOSAIC_COLUMNS]
    total = sum(counts)
    n = len(MOSAIC_COLUMNS)
    gap = 0.02
    usable = 1 - gap * (n - 1)

    x = 0.0
    for (title, carrier, key), count in zip(MOSAIC_COLUMNS, counts):
        width = count / total * usable
        comp = _composition(carrier, groups[key], active_carriers)

        y = 0.0
        for others, techs in comp:
            h = len(techs) / count
            ax.add_patch(Rectangle((x, y), width, h, facecolor=CARRIER_COLOR[carrier],
                                     edgecolor="white", linewidth=1.3))
            other_order = [c for c in CARRIERS if c in others]
            for hatch, other_carrier in zip(CROSS_CARRIER_HATCHES, other_order):
                ax.add_patch(Rectangle((x, y), width, h, facecolor="none",
                                         edgecolor=CROSS_CARRIER_HATCH_COLOR[other_carrier],
                                         hatch=hatch, linewidth=0))
            if h > 0.045:
                label = f"{len(techs)}" if not others else f"{len(techs)} also {'+'.join(other_order)}"
                ax.text(x + width / 2, y + h / 2, label, ha="center", va="center",
                         fontsize=7.3, fontweight="bold", color="#1a1a1a",
                         path_effects=[withStroke(linewidth=2.2, foreground="white")])
            y += h

        ax.text(x + width / 2, 1.05, title, ha="center", va="bottom", fontsize=9.5,
                 fontweight="bold", color=CARRIER_COLOR[carrier])
        ax.text(x + width / 2, -0.05, f"n = {count}", ha="center", va="top", fontsize=8.5, color="#444444")
        x += width + gap

    ax.set_xlim(-0.01, 1.01)
    ax.set_ylim(-0.16, 1.2)
    ax.axis("off")


# ── Magnitude panel ──────────────────────────────────────────────────────

def _format_value(x: float) -> str:
    if abs(x) >= 1e6:
        return f"{x / 1e6:.2f}M"
    if abs(x) >= 1e3:
        return f"{x / 1e3:.0f}k"
    return f"{x:.0f}"


def _draw_magnitude_bars(ax: plt.Axes, rows: list[tuple[str, str, float]], unit: str, title: str) -> None:
    labels = [r[0] for r in rows]
    colors = [CARRIER_COLOR[r[1]] for r in rows]
    vals = [r[2] for r in rows]
    y = range(len(rows))
    ax.barh(list(y), vals, color=colors, edgecolor="white", height=0.62)
    xmax = max(abs(v) for v in vals) * 1.35 if vals else 1
    for i, v in zip(y, vals):
        ax.text(v + (xmax * 0.02 if v >= 0 else -xmax * 0.02), i, _format_value(v),
                 va="center", ha="left" if v >= 0 else "right", fontsize=8.5)
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=8.5)
    ax.set_ylim(len(rows) - 0.5, -0.5)
    ax.set_xlim(min(0, -xmax * 0.05), xmax)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _pos: _format_value(v)))
    ax.set_xlabel(f"annual flow, 2050 [{unit}]", fontsize=8.5)
    ax.axvline(0, color="black", linewidth=0.6)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="x", labelsize=7.5)
    ax.set_title(title, fontsize=10, fontweight="bold", loc="left")


def plot_magnitudes(ax_gwh: plt.Axes, ax_kt: plt.Axes, mag: dict[str, float]) -> None:
    """One row per group (per user request) -- production-side value only.
    Each group's consumption-side total is a little lower (storage/
    conversion losses), not a separate bar; see the figure caption."""
    gwh_rows = [
        ("Electricity\nproducers & storage (net)", E, mag["electricity_producers_storage"]),
        ("Electricity\nconsumers", E, mag["electricity_consumers"]),
        ("Hydrogen\nproduced", H, mag["hydrogen_produced"]),
    ]
    kt_rows = [
        ("Carbon\ncaptured", C, mag["carbon_produced"]),
    ]
    _draw_magnitude_bars(ax_gwh, gwh_rows, CARRIER_UNIT[E], "Electricity & hydrogen totals per group")
    _draw_magnitude_bars(ax_kt, kt_rows, CARRIER_UNIT[C], "Carbon totals per group")


# ── Figure ───────────────────────────────────────────────────────────────

def plot_carrier_groups(groups: dict[str, list[str]], active_carriers: dict[str, set[str]],
                          mag: dict[str, float]) -> plt.Figure:
    # Every element below is sized in inches and stacked via an explicit
    # top-down cursor (mirrors plot_carrier_flows.py's row_h/top_margin/gap
    # discipline) -- titles/xlabels render OUTSIDE their axes rect in
    # matplotlib, so the gaps between rects must be sized to fit them
    # explicitly or they overlap the neighbour (this figure's first two
    # drafts both hit exactly that bug).
    top_margin = 1.15       # suptitle (2 lines) + subtitle (2 lines), above the mosaic
    mosaic_h = 3.3           # mosaic axes rect (column titles/n= labels live inside its own ylim padding)
    gap_1 = 0.5              # mosaic's bottom whitespace + magnitude panels' own titles, above them
    row_pitch = 0.5          # inches per bar in the magnitude panels
    gwh_bars_h = row_pitch * 3
    kt_bars_h = row_pitch * 1
    mag_h = gwh_bars_h        # the band reserved for bars = the taller (GWh) panel; kt is shorter & top-aligned
    gap_2 = 0.55              # magnitude panels' xlabel/ticks, below them
    caption_h = 0.85
    bottom_margin = 0.1
    fig_h = top_margin + mosaic_h + gap_1 + mag_h + gap_2 + caption_h + bottom_margin
    fig_w = 11

    fig = plt.figure(figsize=(fig_w, fig_h))
    y_cursor = fig_h - top_margin
    y_cursor -= mosaic_h
    ax_mosaic = fig.add_axes([0.06, y_cursor / fig_h, 0.9, mosaic_h / fig_h])
    y_cursor -= gap_1
    y_cursor -= mag_h
    ax_gwh = fig.add_axes([0.08, y_cursor / fig_h, 0.4, gwh_bars_h / fig_h])
    ax_kt = fig.add_axes([0.58, (y_cursor + gwh_bars_h - kt_bars_h) / fig_h, 0.36, kt_bars_h / fig_h])
    y_cursor -= gap_2
    y_cursor -= caption_h

    plot_mosaic(ax_mosaic, groups, active_carriers)
    plot_magnitudes(ax_gwh, ax_kt, mag)

    fig.suptitle(
        "Technology groups for investment analysis -- Crystal Ball v8.0,\n"
        "no flexibility / no diffusion, cost-optimal 2050",
        fontsize=14, fontweight="bold", y=1 - 0.12 / fig_h,
    )
    fig.text(
        0.5, 1 - 0.62 / fig_h,
        "Group membership, by technology count -- column width AND internal stacking are both exactly\n"
        "proportional (unlike a Venn diagram's indicative circles)",
        fontsize=10.5, fontweight="bold", ha="center", va="top", color="#333333",
    )
    fig.text(
        0.06, (y_cursor + caption_h) / fig_h,
        "Rule: a technology touching hydrogen or carbon is grouped there IN FULL, even if it also touches "
        "electricity -- its electricity draw is the cost of that hydrogen/carbon story, not ordinary grid "
        "demand. Electricity keeps only what's exclusively electricity. hydrogen ∩ carbon technologies "
        "(methanol_from_hydrogen) are counted in BOTH groups. Storage's magnitude above is its NET "
        "contribution (discharge minus charge) -- both battery and pumped_hydro are small net electricity "
        "consumers here due to round-trip losses. Hydrogen/carbon bars show the PRODUCTION side only "
        "(electrolysis output / captured carbon), not shown alongside a separate consumption-side bar: "
        "hydrogen's consumption total is ~1% lower (salt_cavern_storage round-trip loss); carbon's is "
        "essentially identical (captured = stored + utilized, a closed mass balance -- no loss to speak of). "
        "See plot_carrier_flows.py's own figure for the full production/consumption breakdown per technology.",
        fontsize=7.8, color="#444444", ha="left", va="top", wrap=True,
    )
    return fig


def main() -> None:
    print(f"Loading base run (see plot_carrier_flows.BASE_RUN_DIR)")
    r = load_base_run()
    all_flows = {carrier: get_carrier_flows(r, carrier) for carrier in CARRIERS}
    active_carriers = build_active_carriers(all_flows)
    groups = build_groups(all_flows, active_carriers)
    mag = compute_group_magnitudes(all_flows, groups)

    print_group_summary(groups)
    print("\nGroup magnitudes:")
    for k, v in mag.items():
        unit = CARRIER_UNIT[C] if k.startswith("carbon") else CARRIER_UNIT[E]
        print(f"  {k:<32s} {_format_value(v):>8s} {unit}")

    fig = plot_carrier_groups(groups, active_carriers, mag)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FIGURES_DIR / "fig_technology_groups.svg"
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"\nSaved {out_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
