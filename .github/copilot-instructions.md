# AI Coding Agent Instructions — Executive Dashboard (FWA)

Practical guide to build/extend this FWA analytics dashboard. The codebase generates a self-contained HTML dashboard from CSVs and whitepapers using Python + Plotly.

## Big Picture
- **Purpose**: Track and visualize delivered FWA concepts for BCBS NC — provider impacts, claim counts, overpayments.
- **Data flow**: [analysis/generate_dashboard.py](analysis/generate_dashboard.py) loads 3 CSVs → cleans currency and dates → aggregates concept-level stats → renders Plotly visuals → writes a single HTML file (and optionally copies whitepapers).
- **Data assets**:
    - [All Hits - Summary Statistics.csv](All%20Hits%20-%20Summary%20Statistics.csv) — all detected hits (presented + unpresented)
    - [Presented Hits - Summary Statistics.csv](Presented%20Hits%20-%20Summary%20Statistics.csv) — delivered concepts + summary metrics
    - [Presented Provider Hits.csv](Presented%20Provider%20Hits.csv) — provider-level detail for presented concepts
    - [Whitepapers/](Whitepapers/) — one PDF per concept (e.g., DME_location.pdf)
- **Join key**: `Concept` links all files.

## Conventions & Pitfalls
- **Filenames with spaces**: use `Path()` or quote in shell.
- **CSV parsing**: always `encoding='latin1'`, `engine='python'`, `thousands=','`.
- **Currency cleaning**: strip `$`, commas, spaces; then `pd.to_numeric(..., errors='coerce')` across all dataframes.
- **Preserve NPI zeros**: load provider data with `dtype={'Billing NPI': str}`.
- **Provider column remaps**: rename provider columns to align visuals:
    - `Total Qualifying Paid Amount` → `Total Overpayment`
    - `Number of Claim Hits` → `NumberOfClaimHits`
- **Irregular CSV**: presented summary has trailing blank rows/columns; code is robust.

## Build & Run
- Setup (macOS):
    - `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Generate dashboard from repo root:
    - `python analysis/generate_dashboard.py`
- **Output**:
    - Default: writes [executive-dashboard.html](executive-dashboard.html) at repo root.
    - With `OUTPUT_DIR`: writes to that subfolder and copies [Whitepapers/](Whitepapers/) into it.
    - Open locally: `open executive-dashboard.html` (or file in `OUTPUT_DIR`).

## Key Patterns in Code
- **Aggregate stats**: sum `Total Overpayment`, `Number of Provider Hits`, `Number of Claim Hits` for presented vs all.
- **Dates**: normalize `Date of Client Delivery` with `pd.to_datetime(..., errors='coerce')`; cadence computed vs baseline 2025-11-05.
- **Whitepaper links**: build `Whitepapers/{Concept}.pdf` links; prefix with `BASE_PATH` when hosting under a subpath.
- **Visuals**: use `pio.to_html(fig, include_plotlyjs='cdn')` for first chart, `include_plotlyjs=False` thereafter. See [provider overpayment histogram](analysis/generate_dashboard.py#L86-L112) and [claim hits histogram](analysis/generate_dashboard.py#L114-L133).
- **Currency display**: format with `f"${x:,.0f}"`; see `format_currency_table()` for consistent table rendering.

## Validation & Cross-Checks
- Reconcile: sum provider `Total Qualifying Paid Amount` (renamed) ≈ summary `Total Overpayment`.
- Compare: summary `Number of Provider Hits` vs unique provider `Billing NPI` counts.
- Spot-check: delivery cadence table and concept list match expected timelines.

## Extending the Dashboard
- Add visuals by following Plotly patterns; embed via `pio.to_html(..., full_html=False)` and append to the main HTML f-string.
- Add concept-level columns using `concept_cols` filtering to remain robust to missing fields.
- Keep existing styling classes (`container`, `summary`, `card`, `table-wrap`) for visual consistency.

## Environment Variables
- `BASE_PATH`: URL prefix for hosted subpaths (affects whitepaper link hrefs).
- `OUTPUT_DIR`: target folder for output; also triggers copying of [Whitepapers/](Whitepapers/) into the output directory.

If anything here seems unclear or incomplete (e.g., output location expectations, additional metrics to track), tell me what you want to change and I’ll refine these instructions.
