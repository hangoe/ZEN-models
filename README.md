# ZEN-models: industrial heat and flexibility in ZEN-Europe

Model runs, analysis and figures of the master thesis *Electrification of Low Temperature
Industrial Heating in the European Energy System* by Hanne Goericke (ETH Zurich,
Energy and Process Systems Engineering, 2026).

The thesis extends the European energy system model ZEN-Europe (built with
[ZEN-garden](https://github.com/ZEN-universe/ZEN-garden)) by four industry sectors with
low-temperature process heat (glass, ceramic, paper, food): heat supply on three temperature
levels, demand-side management (DSM), thermal energy storage (TES) and technology diffusion.
It compares flexibility scenarios in cost-optimal runs and explores the near-optimal space of
industrial heat electrification with modelling to generate alternatives (MGA).

## Repository layout

| Path | Content |
|------|---------|
| `run_model.py` | Runs one row of a run table: stages a private copy of the dataset, applies the row's overrides, runs ZEN-garden. |
| `runs/parameters.csv` | Single (cost-optimal) runs of the thesis, one row each. |
| `runs/parameters_mga.csv` | MGA runs (main run, test runs and the ZEN-Europe calibration runs). |
| `runs/mga_runs.csv` | All MGA runs of the thesis appendix with run ID (T, Z, V), Euler job IDs, settings and result folder. |
| `configs/` | ZEN-garden configs: `config.yaml` (single runs), `mga/` (MGA mode and axes). |
| `data/datasets/` | ZEN-Europe datasets of the thesis scenarios. |
| `data/results/single/` | Results of the single runs (see *Data*). |
| `data/results/mga/` | Results of the MGA runs: polytope, convergence diagnostics, Euler resource use. |
| `thesis_figures/` | Figure code (Python package), one module per figure group. |
| `make_figures.py` | Generates all thesis figures into `figures/report/` and `figures/presentation/`. |
| `figures/` | Generated figures (named by thesis figure number), tables, hand-drawn diagrams (`drawio/`). |
| `prep/` | Dataset and data preparation: first-year freeze of the MGA dataset, import of Euler resource use. |
| `euler/` | SLURM scripts and setup for the Euler cluster, run guide, MGA run history. |
| `streamlit/` | Interactive dashboard (still reads the first ZEN-Europe version, `data/results/zen_europe_v1/`). |

## Installation

Python 3.13 with ZEN-garden, ZEN-garden-plugins (MGA plugin) and near_optimal_tools (pyoNearOpt),
installed from source next to this repository:

```bash
conda env create -f environment.yml && conda activate zen-models
git clone -b feature/mga https://github.com/hangoe/ZEN-garden.git ../ZEN-garden
git clone https://github.com/hangoe/ZEN-garden-plugins.git ../ZEN-garden-plugins
git clone https://github.com/evrenmturan/near_optimal_tools.git ../near_optimal_tools
pip install -e ../ZEN-garden -e ../ZEN-garden-plugins -e "../near_optimal_tools[bbo]"
```

Versions used for the thesis: ZEN-garden 3.1.1 (`hangoe/ZEN-garden`, branch `feature/mga`, commit
`44c90074`), ZEN-garden-plugins commit `5dc0ce7`, near_optimal_tools commit `b901134`, Gurobi 13.0.

## Figures

```bash
python make_figures.py                   # all figures, report and presentation version
python make_figures.py fig06 figA07      # selected figures (name prefixes)
python make_figures.py --list            # figure names and thesis numbers
```

Each figure is built in its own process (about 0.7 GB of memory). `FIGURE_MODE` selects the
font: `report` (Computer Modern, as the thesis) or `presentation` (Arial). The SVG output is
deterministic, so a regenerated figure is byte-identical if nothing changed.

| Thesis | File | Content | Runs |
|---|---|---|---|
| Fig. 1 | `figures/drawio/` | Sector diagram (drawn by hand) | – |
| Fig. 2 | `fig02_industry_energy_input_by_carrier` | Energy input by carrier, new vs. existing industry sectors | No-Flex |
| Fig. 3 | `fig03_cost_breakdown_sector_industry_heating` | Total system cost by sector, industry branch, heating technology | Legacy, No-Flex |
| Fig. 4 | `fig04_capacity_and_storage_legacy_vs_no_flex` | Power capacity and storage discharge | Legacy, No-Flex |
| Fig. 5 | `fig05_heat_supply_no_flex` | Industrial heat supply by technology | No-Flex |
| Fig. 6 | `fig06_flexibility_matrix` | Flexibility x temperature levels | No-Flex, ZEN-Europe, both single temp. |
| Fig. 7 | `fig07_mga_limit_radar` | Near-optimal ranges under limits | MGA T1 |
| Fig. A1 | `figA01_emissions_by_source_and_carbon_budget` | Emissions by source, cumulative emissions vs. budget | Legacy, No-Flex |
| Fig. A2 | `figA02_heat_supply_zen_europe` | Industrial heat supply by technology | ZEN-Europe |
| Fig. A3 | `figA03_flexibility_scenarios_table` | Flexibility scenarios vs. ZEN-Europe | five flexibility scenarios |
| Fig. A4 | `figA04_dsm_discharge_by_product` | DSM discharge by product | ZEN-Europe, No-TES-DSM-Pess |
| Fig. A5 | `figA05_flexibility_matrix_time_steps` | Flexibility x time steps per year | No-Flex, ZEN-Europe, 10 and 20 ts |
| Fig. A6 | `figA06_mga_limit_radar_ccs_biomass` | Near-optimal ranges, limits on carbon flows | MGA T1 |
| Fig. A7 | `figA07_mga_limit_radar_test_runs` | As Fig. 7, test runs | MGA T2, T3 |
| Fig. A8 | `figA08_mga_limit_radar_ccs_biomass_test_runs` | As Fig. A6, test runs | MGA T2, T3 |
| Fig. A9 | `figA09_mga_run_tests_convergence` | Convergence of the MGA runs | MGA V, Z, T |
| Fig. A10 | `figA10_mga_run_tests_effort` | Computational effort of the MGA runs | MGA V, Z, T |

`python make_figures.py --tables` also writes the data of the MGA run table in the appendix
(`figures/tables/`).

## Runs

### Scenarios (single runs)

All runs: 2022-2050 in steps of four years, ten representative time steps per year (row 9 and 10:
twenty), Gurobi barrier with NumericFocus 2.

| task_id | Dataset | Thesis scenario |
|---|---|---|
| 0 | `zen_europe_legacy` | ZEN-Europe-Legacy (without the industry heat extension) |
| 1 | `zen_europe_no_flex` | ZEN-Europe-No-Flex (no DSM, no TES) |
| 2 | `zen_europe` | ZEN-Europe (all flexibility options) |
| 5 | `zen_europe_no_dsm` | ZEN-Europe-No-DSM |
| 6 | `zen_europe_no_tes` | ZEN-Europe-No-TES |
| 7 | `zen_europe_no_tes_dsm_pess` | ZEN-Europe-No-TES-DSM-Pess (pessimistic DSM categories) |
| 9, 10 | `zen_europe`, `zen_europe_no_flex` | ZEN-Europe, ZEN-Europe-No-Flex with 20 time steps per year |
| 15 | `zen_europe_no_flex_single_temp_diff_correct` | ZEN-Europe-No-Flex-Single-Temp |
| 16 | `zen_europe_single_temp_diff_correct` | ZEN-Europe-Single-Temp |

The single-temperature datasets carry the suffix `_diff_correct` (technology diffusion corrected
for the single temperature level); result folders keep the dataset names.

### MGA runs

`runs/mga_runs.csv` lists every MGA run of the thesis appendix. T1 (task_id 54) is the main run
(5 time steps per year, tolerance 0.1); T2 (56) and T3 (57) are the test runs with 1 time step
per year and tolerance 0.1 / 0.01; T4 (67) repeats T3 with a cost slack of 0.2 %. All use the
dataset `zen_europe_no_flex_no_diffusion_export0` (no diffusion limit, no exports, capacity
additions of the axis technologies frozen in 2022 with `prep/freeze_first_year_additions.py`)
and the axes `configs/mga/config_mga_axes_ind_heating_thesis.yaml`. Z1-Z7 are calibration runs
with the first ZEN-Europe version (rows 21-47, dataset not included); the rows of the V runs
(earlier model version) no longer exist, `runs/mga_runs.csv` documents their settings.

### Running

```bash
python run_model.py --task_id 1 --run_on local                       # single run on a laptop (needs > 40 GB RAM at 10 ts)
sbatch --array=0-2 euler/submit_euler.sh                             # single runs on Euler
sbatch --array=54 euler/submit_euler_mga.sh                          # MGA run on Euler
```

Submit from the repository root. Euler setup and resources: `euler/README_euler.md`.

## Data

- **Datasets** (`data/datasets/`) were generated with ZEN-Europe (ZEN-creator) and are tracked.
- **Single-run results** (`data/results/single/`): only the small metadata files are tracked;
  the NetCDF result files (`variables.nc`, `parameters.nc`, about 45 MB per run) are too large
  for git and are shared separately. The single-run figures need them.
- **MGA results** (`data/results/mga/`): the polytope (`polytope.npz`), the convergence
  diagnostics and the Euler resource use of each run are tracked, which is all the MGA figures
  need.

## Dashboard

```bash
streamlit run streamlit/app.py
```

The dashboard still reads the runs of the first ZEN-Europe version (`data/results/zen_europe_v1/`);
moving it to the thesis results is a planned next step.
