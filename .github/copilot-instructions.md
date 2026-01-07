# AI Coding Agent Instructions — Executive Dashboard

Fast-start guidance for AI agents working in this FWA dashboard repo. The workspace contains CSV data, concept whitepapers, and a Python script that builds an HTML executive dashboard.

## Big Picture
- Purpose: Summarize Fraud/Waste/Abuse (FWA) concepts, provider/claim impacts, and paid amounts; produce an HTML dashboard for executive tracking.
- Key assets:
    - Summary tables: [All Hits - Summary Statistics.csv](All%20Hits%20-%20Summary%20Statistics.csv), [Presented Hits - Summary Statistics.csv](Presented%20Hits%20-%20Summary%20Statistics.csv)
    - Provider-level table: [All Provider Hits.csv](All%20Provider%20Hits.csv)
    - Concept whitepapers: [Whitepapers](Whitepapers)
    - Dashboard builder: [analysis/generate_dashboard.py](analysis/generate_dashboard.py)
    - Output: [reports/executive-dashboard.html](reports/executive-dashboard.html) or [executive-dashboard.html](executive-dashboard.html)

## Architecture & Data Flow
- Load CSVs robustly (`engine='python'`, `encoding='latin1'`, `thousands=','`). Treat `Billing NPI` as `str`. Parse `Date of Client Delivery`.
- Clean currency-like columns by stripping `$`, commas, and spaces; convert to numeric.
- Aggregate headline metrics (totals overpayment, providers/claims flagged) from both Presented and All hits.
- Build tables:
    - Concepts with delivery date and description, with per-concept PDF links to [Whitepapers](Whitepapers).
    - Concept-level stats for Presented and All hits, formatted with currency.
    - Delivery cadence table with days since baseline (2025-11-05) and average successive interval.
- Visualize provider-level distributions (Plotly histograms) for `Total Overpayment` and `Number of Claim Hits` by `Concept`.

## Workflows
- Environment setup (Python 3.10+):
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
- Generate dashboard (recommended output path in `reports/`):
```bash
OUTPUT_DIR=reports BASE_PATH="" python analysis/generate_dashboard.py
open reports/executive-dashboard.html
```
- Hosting under a subpath (for static sites): set `BASE_PATH="/subpath"` to prefix whitepaper links; script copies [Whitepapers](Whitepapers) when `OUTPUT_DIR` is set.

## Conventions & Gotchas
- Filenames contain spaces; quote paths in shell commands.
- Currency/integers often include `$`, commas, and trailing spaces (e.g., " $3,069,990 "); always clean before numeric ops.
- `Presented Hits - Summary Statistics.csv` has trailing empty rows and an extra blank column; robust parsing required.
- Encoding artifact: text may include replacement chars (e.g., `99202�99215`); keep as-is unless explicitly cleaning.
- Use pandas nullable `Int64` for count fields to preserve missing values.

## Patterns & Validation
- Join across files by `Concept` to reconcile totals.
- Provider rollups: sum `Total Qualifying Paid Amount` and `Total Claim Paid Amount` in [All Provider Hits.csv](All%20Provider%20Hits.csv) to cross-check summary aggregates.
- Verify dashboard numbers by comparing Presented vs All hits totals for overpayment, providers, and claims.

## Integration Points
- Plotly CDN is used in the report; no local JS bundling needed.
- Whitepaper links target [Whitepapers](Whitepapers)/`<Concept>.pdf`; ensure filenames match `Concept` exactly.

## Deliverables & Communication
- Cite exact source files/columns and note cleaning steps inline.
- Keep generated artifacts in `reports/` (or `OUTPUT_DIR`) and reference their paths.
- Document any data anomalies encountered (encoding, trailing blanks) and how they were handled.
