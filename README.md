# DPE-Insight

Exploratory analysis of energy performance certificates (DPEs) for existing homes in Seine-Saint-Denis (department 93), using open data from the French Agency for Ecological Transition (ADEME).

## Project scope

- **Territory:** Seine-Saint-Denis (93), at department and municipality level.
- **Source:** [ADEME — Existing homes DPE records since July 2021](https://data.ademe.fr/datasets/meg-83tjwtg8dyz4vv7h1dqe).
- **Working definition of an energy-inefficient home:** a DPE energy label of F or G. This definition uses the energy label, not the greenhouse-gas label.

The project describes recorded DPEs. It does not estimate the full housing stock, identify unique homes, make causal claims, or predict future performance.

## Setup

Use Python 3.11 or later. Create and activate a virtual environment, then install the pinned dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1`.

## Download the data

Raw and processed data are excluded from Git. Each team member downloads a local copy from the [ADEME open-data API](https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/lines). The extraction is filtered to department code `93` and contains selected fields only; it excludes street addresses.

Download the complete current extraction:

```bash
python src/download.py
```

For a small API check, write a separate sample so you do not overwrite the complete extraction:

```bash
python src/download.py --limit 100 --output data/raw/dpe_93_sample.csv.gz
```

The script writes a compressed CSV and a manifest containing its retrieval time, row count, selected columns, and SHA-256 checksum. ADEME updates the source weekly, so agree on one extraction and do not refresh it during the analysis if you need comparable results.

## Project structure

```text
data/raw/                 Local ADEME downloads (not tracked by Git)
data/processed/           Local analysis outputs (not tracked by Git)
src/download.py           Filtered ADEME data download
src/cleaning.py           Data cleaning functions
src/indicators.py         Reusable analysis indicators
notebooks/                Exploratory analysis
app/dashboard.py          Streamlit dashboard entry point
docs/                     Project questions, decisions, anomalies, and post-mortem
```

The analysis modules and dashboard are still being built. The data download can be run with the command above; the dashboard is not available yet.

## Interpretation limits

- One home may have more than one DPE, so diagnosis counts are not unique-home counts.
- Recorded DPEs do not represent the entire housing stock.
- Missing and anomalous values must be documented before analysis.
- An association between a housing characteristic and a poor DPE label does not establish causation.
