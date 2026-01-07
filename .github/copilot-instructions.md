# AI Coding Agent Instructions for Executive Dashboard

These instructions make AI agents immediately productive in this dataset-centric workspace. The repo currently contains data assets and whitepapers, with no code or build system.

## Big Picture
- Purpose: Analyze fraud/waste/abuse (FWA) concepts and summarize provider/claim impacts and paid amounts.
- Assets:
  - Summary tables: [All Hits - Summary Statistics.csv](All%20Hits%20-%20Summary%20Statistics.csv), [Presented Hits - Summary Statistics.csv](Presented%20Hits%20-%20Summary%20Statistics.csv)
  - Provider-level table: [Presented Provider Hits.csv](Presented%20Provider%20Hits.csv)
  - Concept whitepapers: [Whitepapers](Whitepapers)
- Common concepts present in all files: `Concept` values like `Intravitreal_injection_EM`, `Skin_graft`, `Intravitreal_injection_2`, `DME_location`.

## Data Conventions and Gotchas
- Filenames include spaces; quote paths when using CLI or code.
- Currency/integers: values often include `$`, commas, and trailing spaces (e.g., `" $3,069,990 "`). Strip and convert before numeric ops.
- Date: `Date of Client Delivery` appears in summary files; parse as dates.
- IDs: `Billing NPI` should be treated as string to preserve leading zeros.
- Encoding artifact: E/M code ranges show a replacement char in text (`99202�99215`); treat as ASCII/UTF-8 and keep descriptive text as-is unless cleaning.
- Schema differences:
  - [All Hits - Summary Statistics.csv](All%20Hits%20-%20Summary%20Statistics.csv) and [Presented Hits - Summary Statistics.csv](Presented%20Hits%20-%20Summary%20Statistics.csv) share headers like `Number of Provider Hits`, `Number of Claim Hits`, `Number of Members Impacted`, `Total Overpayment`, `Total Paid Amount`.
  - [Presented Provider Hits.csv](Presented%20Provider%20Hits.csv) has provider granularity: `Billing NPI`, `Total Qualifying Paid Amount`, `Total Claim Paid Amount`.
- Irregular rows: [Presented Hits - Summary Statistics.csv](Presented%20Hits%20-%20Summary%20Statistics.csv) contains trailing empty lines and an extra trailing column with blanks; use robust CSV parsing.

## Typical Agent Tasks
- Load and clean the three CSVs; join on `Concept` to reconcile summary and provider views.
- Aggregate by `Concept` (e.g., sums of paid amounts, provider counts) and validate against provided summaries.
- Link `Concept` to relevant whitepaper PDFs in [Whitepapers](Whitepapers) when generating reports.

## Minimal, Robust Loading (Python/pandas)
```python
import pandas as pd
from pathlib import Path
base = Path('.')

all_hits = pd.read_csv(
    base / 'All Hits - Summary Statistics.csv',
    thousands=',',
    dtype={'Number of Provider Hits': 'Int64', 'Number of Claim Hits': 'Int64',
           'Number of Members Impacted': 'Int64'},
    parse_dates=['Date of Client Delivery'],
    engine='python'  # handles edge cases
)

presented_hits = pd.read_csv(
    base / 'Presented Hits - Summary Statistics.csv',
    thousands=',',
    parse_dates=['Date of Client Delivery'],
    engine='python'
)

provider_hits = pd.read_csv(
    base / 'Presented Provider Hits.csv',
    dtype={'Billing NPI': str},
    thousands=',',
    engine='python'
)

# Clean currency columns
for df in (all_hits, presented_hits, provider_hits):
    for col in df.columns:
        if df[col].astype(str).str.contains('\$').any():
            df[col] = (df[col].astype(str)
                .str.replace('$', '', regex=False)
                .str.replace(',', '', regex=False)
                .str.strip())
            df[col] = pd.to_numeric(df[col], errors='coerce')
```

## Patterns and Examples
- Concepts as join keys: group by `Concept` across files to compare totals.
- Provider rollups: sum `Total Qualifying Paid Amount` and `Total Claim Paid Amount` in [Presented Provider Hits.csv](Presented%20Provider%20Hits.csv) to cross-check summary totals.
- Date filtering: use `Date of Client Delivery` to subset recent vs historical deliveries.
- Whitepaper mapping: each `Concept` has a corresponding PDF in [Whitepapers](Whitepapers) (e.g., `DME_location.pdf`).

## Workflows
- No build/test system present; analytics run via your chosen tooling (Python, R, or SQL in notebooks).
- Keep outputs in `reports/` or `analysis/` (create as needed) and reference source filenames.
- When adding code, prefer small, well-scoped scripts/notebooks that read from these CSVs; avoid heavy frameworks.

## Communication & Deliverables
- Cite exact files and columns used (link them when possible).
- Flag any data quality concerns (currency strings, trailing blanks) and document cleaning steps inline.
- For new analyses, include brief validation comparing provider-level aggregates to summary files.
