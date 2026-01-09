# AI Coding Agent Instructions — Executive Dashboard

Fast-start guidance for AI agents working in this FWA dashboard repo. The workspace contains CSV data, concept whitepapers, and a Python script that builds an HTML executive dashboard.

## Big Picture
- Purpose: Summarize Fraud/Waste/Abuse (FWA) concepts, provider/claim impacts, and paid amounts; produce an HTML dashboard for executive tracking.
- Key assets:
    - Summary tables: [All Hits - Summary Statistics.csv](All%20Hits%20-%20Summary%20Statistics.csv), [Presented Hits - Summary Statistics.csv](Presented%20Hits%20-%20Summary%20Statistics.csv)
    - Provider-level table: [All Provider Hits.csv](All%20Provider%20Hits.csv) with columns `Concept`, `Billing NPI`, `Number of Provider Hits`, `Number of Claim Hits`, `Total Qualifying Paid Amount`, `Total Claim Paid Amount`
    - Concept whitepapers: [Whitepapers](Whitepapers) (PDFs matching concept names exactly)
    - Brand assets: [visuals](visuals) (Machinify and BCBS NC logos)
    - Dashboard builder: [analysis/generate_dashboard.py](analysis/generate_dashboard.py)
    - Outputs: Script writes to three locations by default—root `executive-dashboard.html`, `reports/executive-dashboard.html` (with copied assets), and optionally `$OUTPUT_DIR/executive-dashboard.html`

## Architecture & Data Flow
- Load CSVs robustly (`engine='python'`, `encoding='latin1'`, `thousands=','`). Treat `Billing NPI` as `str`. Parse `Date of Client Delivery`.
- Clean currency-like columns by stripping `$`, commas, and spaces; convert to numeric.
- Aggregate headline metrics (totals overpayment, providers/claims flagged) from both Presented and All hits.
- Build tables:
    - Concepts with delivery date and description, with per-concept PDF links to [Whitepapers](Whitepapers).
    - Concept-level stats for Presented and All hits, f`2025-11-05`) and average successive interval.
- Visualize provider-level distributions (Plotly histograms) for `Total Overpayment` (mapped from `Total Qualifying Paid Amount`) and `Number of Claim Hits` by `Concept`.
- Generate line charts showing overpayment progression over time with concept labels positioned dynamically (y-axis fixed at 0–12M)
- Visualize provider-level distributions (Plotly histograms) for `Total Overpayment` and `Number of Claim Hits` by `Concept`.

## Workflows
- Environment setup (Python 3.10+):
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```default writes to root, `reports/`, and `$OUTPUT_DIR` if set):
```bash
python analysis/generate_dashboard.py
open reports/executive-dashboard.html
```
- Or with explicit output directory and base path:
```bash
OUTPUT_DIR=docs BASE_PATH="/dashboard" python analysis/generate_dashboard.py
```always quote paths in shell commands.
- Currency/integers often include `$`, commas, and trailing spaces (e.g., " $3,069,990 "); always clean before numeric ops.
- `Presented Hits - Summary Statistics.csv` has trailing empty rows and an extra blank column; robust parsing required.
- Encoding artifact: text may include replacement chars (e.g., `99202�99215`); keep as-is unless explicitly cleaning.
- Use pandas nullable `Int64` for count fields to preserve missing values.
- All CSV column headers may have leading/trailing whitespace; strip with `.str.strip()` after load.
- Baseline date `2025-11-05` is hardcoded in script for delivery cadence delta calculation
- Filenames contain spaces; quote paths in shell commands.
- Currency/integers often include `$`, commas, and trailing spaces (e.g., " $3,069,990 "); always clean before numeric ops.
- `Presented Hits - Summary Statistics.csv` has trailing empty rows and an extra blank column; robust parsing required.
- Encoding artifact: text may include replacement chars (e.g., `99202�99215`); keep as-is unless explicitly cleaning.
- Use pandas nullable `Int64` for count fields to preserve missing values.

## Patterns & Validation
- Join across files by `Concept` to reconcile totals.PDF filenames match `Concept` exactly (e.g., `Skin_graft.pdf`, `DME_location.pdf`).
- Logo images embedded from [visuals](visuals): `Machinify_Logo.jpg` and `BCBS_NorthCarolina_Logo.png`
- Provider rollups: sum `Total Qualifying Paid Amount` and `Total Claim Paid Amount` in [All Provider Hits.csv](All%20Provider%20Hits.csv) to cross-check summary aggregates.
- Verify dashboard numbers by comparing Presented vs All hits totals for overpayment, providers, and claims.
Script outputs to multiple locations: root (for quick checks), `reports/` (recommended for opening), and optionally `$OUTPUT_DIR`.
- Document any data anomalies encountered (encoding, trailing blanks, mismatched concept names) and how they were handled.

## Quick Reference
- Dependencies: `pandas>=2.0`, `plotly>=5.18`
- Primary script: [analysis/generate_dashboard.py](analysis/generate_dashboard.py)
- Key date baseline: `2025-11-05` (for cadence calculations)
- Output HTML: Self-contained with embedded Plotly via CDN; requires copied asset directories for full functionality
- Plotly CDN is used in the report; no local JS bundling needed.
- Whitepaper links target [Whitepapers](Whitepapers)/`<Concept>.pdf`; ensure filenames match `Concept` exactly.

## Deliverables & Communication
- Cite exact source files/columns and note cleaning steps inline.
- Keep generated artifacts in `reports/` (or `OUTPUT_DIR`) and reference their paths.
- Document any data anomalies encountered (encoding, trailing blanks) and how they were handled.
