"""Near-optimal ranges from the polytope of an MGA run, without re-solving ZEN-garden.

pyoNearOpt (ZEN-garden-plugins) stores the result of an exploration as polytope.npz:
the solved designs X (inner approximation = their convex hull), the cuts A z <= b of the
outer approximation, and per axis an offset and scale (scaled axes run from 0 to 1). The
range of an axis under additional limits is the minimum and maximum of that axis over the
inner or the outer approximation, each a small LP.

Runs (runs/mga_runs.csv): T1 is the main run (5 representative time steps per year,
tolerance 0.1), T2 and T3 are test runs with 1 time step per year and tolerance 0.1 / 0.01,
T4 repeats T3 with a cost slack of 0.2 % instead of 1 %.
"""

from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import linprog
from zen_garden_plugins.mga.polytope_io import load_polytope

from ..paths import MGA_RESULTS_DIR

MODEL = "zen_europe_no_flex_no_diffusion_export0"
RUN_FOLDERS = {
    "T1": f"{MODEL}_2022_8a_4a_interval_5ts_MGA_IND_HEATING_THESIS"
          "_batch_bbofast_minmax_batch16_tol01_eps001_FREEZE2022_ci095_ns4000",
    "T2": f"{MODEL}_2022_8a_4a_interval_1ts_MGA_IND_HEATING_THESIS"
          "_batch_bbofast_minmax_batch16_tol01_eps001_FREEZE2022_ci095_ns4000",
    "T3": f"{MODEL}_2022_8a_4a_interval_1ts_MGA_IND_HEATING_THESIS"
          "_batch_bbofast_minmax_batch16_tol001_eps001_FREEZE2022_ci095_ns4000",
    "T4": f"{MODEL}_2022_8a_4a_interval_1ts_MGA_IND_HEATING_THESIS"
          "_batch_bbofast_minmax_batch16_tol001_eps0002_FREEZE2022_ci095_ns4000",
}
RUN_TOLERANCE = {"T1": "0.1", "T2": "0.1", "T3": "0.01", "T4": "0.01"}


def load_run_polytope(run_id: str):
    return load_polytope(MGA_RESULTS_DIR / RUN_FOLDERS[run_id] / f"{MODEL}_batch_summary" / "polytope.npz")

YEARS = (2034, 2050)
METRICS = ("heat", "ccs", "biomass")
AXIS_PREFIX = {  # axis names in the axes config (configs/mga/config_mga_axes_ind_heating_thesis.yaml)
    "heat": "all_industry_heat_electrification",
    "ccs": "all_co2_storage",
    "biomass": "imported_biomass",
}
LIMITED_UNIT = {"heat": "%", "ccs": "%", "biomass": "TWh"}

# Limits on one axis (in both years), as (scaled low, scaled high): "A" = top, "B" = bottom
# LIMIT_BAND of the axis's range.
LIMIT_BAND = 0.01
AXIS_LIMITS = {"A": (1 - LIMIT_BAND, 1.0), "B": (0.0, LIMIT_BAND)}
# Cost limits: fraction of the cost slack that is kept.
COST_LIMITS = {"20": 0.2, "10": 0.1, "5": 0.05, "1": 0.01}


def to_display(metric: str, value: float) -> float:
    """Axis value in physical units -> as plotted: shares in %, biomass GWh -> TWh."""
    return 1e-3 * value if metric == "biomass" else 100 * value


def extra_cost_bn(percent: float, c_star: float) -> float:
    """Cost above the optimum, % -> bn EUR (c_star in MEUR)."""
    return percent / 100 * c_star * 1e-3


def solve_lp(*args, **kwargs):
    """linprog with a retry without presolve (HiGHS can stop on numerics with presolve).
    None means infeasible; any other failure raises."""
    res = linprog(*args, **kwargs, method="highs")
    if res.status not in (0, 2):
        res = linprog(*args, **kwargs, method="highs-ds", options={"presolve": False})
    if res.status == 2:
        return None
    if not res.success:
        raise RuntimeError(f"LP failed: {res.message}")
    return res


def inner_bound(poly, floors, ceilings, j: int, sense: str) -> float | None:
    """Min or max of axis j over the convex hull of the solved designs, in physical units.
    floors / ceilings: [(axis, scaled value)]."""
    X = poly.X
    rows = [-X[:, k] for k, _ in floors] + [X[:, k] for k, _ in ceilings]
    limits = [-value for _, value in floors] + [value for _, value in ceilings]
    res = solve_lp(X[:, j] * (1.0 if sense == "min" else -1.0),
                   A_ub=np.array(rows) if rows else None, b_ub=limits if rows else None,
                   A_eq=np.ones((1, X.shape[0])), b_eq=[1.0], bounds=(0, None))
    return None if res is None else float(X[:, j] @ res.x) * poly.scale[j] + poly.offset[j]


def outer_bound(poly, floors, ceilings, j: int, sense: str) -> float | None:
    """Min or max of axis j over the outer approximation, in physical units."""
    n = poly.A.shape[1]
    c = np.zeros(n)
    c[j] = 1.0 if sense == "min" else -1.0
    lower, upper = dict(floors), dict(ceilings)
    bounds = [(lower.get(k), upper.get(k)) for k in range(n)]
    res = solve_lp(c, A_ub=poly.A, b_ub=poly.b, bounds=bounds)
    return None if res is None else float(res.x[j]) * poly.scale[j] + poly.offset[j]


def solve_all(poly, axis_idx, floors, ceilings, bound) -> dict | None:
    """{(metric, year): (lo, hi)} in display units plus {"cost": (lo, hi)} in % above C*,
    or None if the limits cannot be met."""
    ranges = {}
    for metric in METRICS:
        for year in YEARS:
            j = axis_idx[f"{AXIS_PREFIX[metric]}_{year}"]
            values = [bound(poly, floors, ceilings, j, s) for s in ("min", "max")]
            if None in values:
                return None
            ranges[metric, year] = tuple(to_display(metric, v) for v in values)
    values = [bound(poly, floors, ceilings, poly.cost_col, s) for s in ("min", "max")]
    if None in values:
        return None
    ranges["cost"] = tuple(100 * (v / poly.c_star - 1) for v in values)
    return ranges


def _ranges(poly, axis_idx, floors, ceilings) -> dict:
    return {name: solve_all(poly, axis_idx, floors, ceilings, bound)
            for name, bound in (("inner", inner_bound), ("outer", outer_bound))}


def axis_limit_ranges(poly, axis_idx, limited: str, band) -> dict:
    """{"inner"/"outer": ranges} with `limited` in `band` (scaled) in both years; band None =
    no limit. A limit at the axis's own min or max adds no constraint."""
    floors, ceilings = [], []
    if band is not None:
        low, high = band
        for year in YEARS:
            k = axis_idx[f"{AXIS_PREFIX[limited]}_{year}"]
            if low > 0:
                floors.append((k, low))
            if high < 1:
                ceilings.append((k, high))
    return _ranges(poly, axis_idx, floors, ceilings)


def cost_limit_ranges(poly, axis_idx, fraction: float) -> dict:
    """{"inner"/"outer": ranges} with the cost limited to `fraction` of the cost slack."""
    return _ranges(poly, axis_idx, [], [(poly.cost_col, fraction)])


def physical_band(poly, axis_idx, limited: str, year: int, band: tuple[float, float]) -> tuple[float, float]:
    """Scaled (low, high) on the limited axis -> display units."""
    k = axis_idx[f"{AXIS_PREFIX[limited]}_{year}"]
    return tuple(to_display(limited, poly.offset[k] + poly.scale[k] * v) for v in band)


@dataclass
class MgaRun:
    """One MGA run: its polytope and the ranges of all limit scenarios (solved on creation).

    Scenarios: "free" (no limit), (metric, "A"/"B") and ("cost", key of COST_LIMITS)."""
    run_id: str
    poly: object = field(init=False)
    idx: dict = field(init=False)
    results: dict = field(init=False)

    def __post_init__(self):
        self.poly = load_run_polytope(self.run_id)
        self.idx = {name: i for i, name in enumerate(self.poly.names)}
        p, idx = self.poly, self.idx
        self.results = {"free": axis_limit_ranges(p, idx, "heat", None)}
        for key, band in AXIS_LIMITS.items():
            for limited in METRICS:
                self.results[limited, key] = axis_limit_ranges(p, idx, limited, band)
        for key, fraction in COST_LIMITS.items():
            self.results["cost", key] = cost_limit_ranges(p, idx, fraction)
