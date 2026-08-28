"""Shared run-loading infra for the batch4 v9_0 regional-CAPEX-by-PERIOD run
(data/outputs/euler_outputs_mga/
Crystal_Ball_ind_heat_v9_0_no_flexibility_nodiffusion_2020_7a_5a_interval_3ts_MGA_CAPEX_PERIODS_batch_bbo_minmax_batch4).

This used to live inside plot_mga_periods_regional_capex.py, which also
produced that run's own crosseffects figure (fig4a/b: own-axis flexibility +
cross-axis response, one per period). fig4a/b were deleted outright (not
archived) once plot_mga_cum_regional_capex.py's fig10 -- the same analysis
against the newer, currently-swept CAPEX-CUM/share axis set, merged into one
matrix (an intermediate fig9a/b split version was itself deleted once fig10
superseded it too) -- superseded them; see that script's module docstring
for the full switchover history. This module survives that deletion as the
shared piece: plot_mga_regional_investment.py (fig7/8) and plot_mga_
investment_map.py both still target this same PERIODS batch4 run for their
own (still-current) absolute-CAPEX/geographic analyses, independent of
whether fig4's own ratio-based crosseffects view exists.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

import matplotlib.pyplot as plt
import numpy as np

from figure_settings import SCENARIO_PALETTE
from zen_garden_plugins.mga.polytope_io import load_polytope

FIGURES_DIR = REPO_ROOT / "data" / "outputs" / "figures" / "mga_tests"
RUN_DIR = (
    REPO_ROOT / "data" / "outputs" / "euler_outputs_mga"
    / "Crystal_Ball_ind_heat_v9_0_no_flexibility_nodiffusion_2020_7a_5a_interval_3ts_MGA_CAPEX_PERIODS_batch_bbo_minmax_batch4"
)
MODEL = "Crystal_Ball_ind_heat_v9_0_no_flexibility_nodiffusion"
POLY_PATH = RUN_DIR / f"{MODEL}_batch_summary" / "polytope.npz"

REGIONS = ["north", "west", "south", "east"]
PERIODS = ["2030_2039", "2040_2049"]
REGION_COLOR = dict(zip(REGIONS, SCENARIO_PALETTE))


def savefig(fig: plt.Figure, name: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{name}.svg"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {path.relative_to(REPO_ROOT)}")


def load_batch4_data():
    """(poly, names, units, axis_idx, origin, phys, base): the loaded
    Polytope itself (poly.A/b/X -- needed for rejection sampling/max_separation
    in plot_mga_results.py), the 9 axes in poly.meta order, their units, a
    name->index map, each solved point's origin label, every solved point's
    physical-unit vector (poly.X is stored normalised, see polytope_io.py --
    to_phys converts back), and the baseline (z_star) vector."""
    if not POLY_PATH.exists():
        raise FileNotFoundError(f"batch4 polytope not found at {POLY_PATH}")
    poly = load_polytope(POLY_PATH)
    names = [a["name"] for a in poly.meta["axes"]]
    units = {a["name"]: a["unit"] for a in poly.meta["axes"]}
    axis_idx = {n: i for i, n in enumerate(names)}
    origin = list(poly.point_origin)
    phys = np.array([poly.to_phys(x) for x in poly.X])
    base = phys[origin.index("z_star")]
    print(f"  loaded {len(origin)} points ({sum(1 for o in origin if o.startswith(('max:', 'min:')))} "
          f"own-axis VMM solves) from {POLY_PATH.relative_to(REPO_ROOT)}")
    return poly, names, units, axis_idx, origin, phys, base
