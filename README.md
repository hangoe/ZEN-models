# ZEN-models — industrial heat flexibility runs

[![Static Badge](https://img.shields.io/badge/ZEN--garden_version-v2.2.20-%23627313?labelColor=%23215CAF)](https://github.com/ZEN-universe/ZEN-garden)

ZEN-garden runs of the sector-coupled European energy system with a detailed
industrial heat sector (temperature levels, DSM, thermal storage, technology
diffusion). Current runs use the **zen-europe** datasets.

## Layout

| Path | Content |
|------|---------|
| `run_model.py` | Runs one row of a parameters CSV (`--task_id N`, `--run_on euler\|local`, `--params parameters.csv`). Stages a private copy of the dataset and applies the row's `system` overrides. |
| `parameters.csv` | One row per run (dataset, comment, time-series aggregation, years, ...). |
| `parameters_mga.csv` | MGA run rows (`--params parameters_mga.csv`). |
| `submit_euler.sh`, `submit_euler_mga.sh` | SLURM array scripts for Euler; `setup_euler_env.sh` builds the venv once. |
| `data/config*.json` | ZEN-garden configs (plain and MGA modes / axes). |
| `data/outputs/` | Downloaded run results and figures. |
| `scripts/` | Analysis and figure scripts (`generate_all_figures.py` regenerates everything). |
| `streamlit/` | Interactive dashboard: `streamlit run streamlit/app.py`. |
| `euler/` | Euler setup and run guides. |

## Datasets

Datasets are not stored here. `run_model.py` looks up `my_dataset` in
`../ZEN-creator/outputs` first, then in `data/`.

## Running

```bash
python run_model.py --task_id 49 --run_on local   # one row locally
sbatch --array=47,48 submit_euler.sh              # rows on Euler
```
