# Executive Dashboard — FWA (BCBS NC)

This repository contains data assets and a script to generate an executive dashboard summarizing Fraud/Waste/Abuse (FWA) deliverables.

## Contents
- All Hits - Summary Statistics.csv
- Presented Hits - Summary Statistics.csv
- All Provider Hits.csv
- Whitepapers/ (PDFs per concept)
- analysis/generate_dashboard.py (builds the HTML dashboard)
- reports/executive-dashboard.html (output, created after running the script)

## Setup
1. Create a Python environment (3.10+ recommended) and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Generate the Dashboard
Run from the repository root:

```bash
python analysis/generate_dashboard.py
open reports/executive-dashboard.html
```

## Notes
- CSVs contain currency strings (e.g., "$3,069,990") which are cleaned before aggregation.
- `Presented Hits - Summary Statistics.csv` contains trailing empty rows and an extra blank column; parsed robustly with `engine="python"`.
- `Billing NPI` is treated as a string to preserve leading zeros.
