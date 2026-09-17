"""Shared FIGURES_DIR/savefig/REGION_COLOR for the mga_tests figure scripts.

Originally also held the batch4 v9_0 regional-CAPEX-by-PERIOD run's own
loading infra (RUN_DIR/POLY_PATH/load_batch4_data), used by
plot_mga_regional_investment.py (fig7/8) and plot_mga_investment_map.py.
Both were deleted outright (fig7/8/fig_vmm_grid_overview_map by user
request, mga_investment/ folder cleanup) along with that run-loading code,
which had no other caller left -- plot_mga_cum_regional_capex.py's own
load_batch4_data (same name, different run: the newer CAPEX-CUM/share axis
set) is a separate function local to that script, not this module.
REGION_COLOR survives as the one piece still shared -- currently only by
plot_mga_regional_investment_whatif.py, which imports it directly rather
than re-deriving it from its own REGIONS list (see that script's module
docstring for why: REGIONS' display order and REGION_COLOR's colour
assignment are deliberately decoupled).
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent

import matplotlib.pyplot as plt

from .figure_settings import SCENARIO_PALETTE

FIGURES_DIR = REPO_ROOT / "data" / "outputs" / "figures" / "mga_tests"

REGIONS = ["north", "west", "south", "east"]
REGION_COLOR = dict(zip(REGIONS, SCENARIO_PALETTE))


def savefig(fig: plt.Figure, name: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{name}.svg"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {path.relative_to(REPO_ROOT)}")
