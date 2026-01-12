# Power BI Dashboard Setup

This folder provides Power Query (M) and DAX to build a Power BI version of the Executive Dashboard using the CSVs in this repo.

## What you'll build
- Summary KPIs (concepts delivered, total overpayment, providers flagged, claims flagged)
- Concept tables (Presented vs All)
- Live tracker line charts (cumulative overpayment over time)
- Provider-level distributions (overpayment, claim hits) by concept
- PDF whitepaper links per concept and brand images

## Files here
- queries/AllHits.pq — M query for All Hits - Summary Statistics.csv
- queries/PresentedHits.pq — M query for Presented Hits - Summary Statistics.csv
- queries/PresentedProviderHits.pq — M query for Presented Provider Hits.csv
- measures/DAX.md — DAX measures for KPIs, cumulative lines, and helper fields

## Steps (Power BI Desktop)
1) Parameters (Power Query)
- Create a Text parameter `RootFolder` pointing to your local repo folder (e.g., /Users/you/Documents/FWA/Executive Dashboard)
- Create a Text parameter `WhitepapersBase` (e.g., "/Whitepapers/") — if hosting under a subpath, include it (e.g., "/fwa-dashboard/Whitepapers/")

2) Queries
- New Query > Blank Query > Advanced Editor
- Paste the contents of each .pq file and replace parameter references if needed
- Ensure `Billing NPI` type is Text in PresentedProviderHits

3) Model
- Create relationships by `Concept` where relevant (Presented vs All; optional for provider table)
- Optionally create a Date table (CALENDAR) and relate to `Date of Client Delivery` in both Presented and All for time-intelligence

4) Measures
- Modeling > New measure — paste measures from measures/DAX.md
- Create Card visuals for KPIs using measures

5) Visuals
- Concepts table: `Concept`, `Date of Client Delivery`, `Description`, and the `Whitepaper URL` column (format as Web URL with icon)
- Concept stats tables: use Presented table and All table respectively
- Live tracker: 2 line charts — use date on axis and cumulative measures for Presented and All
- Provider distributions:
  - Create bins on provider `Total Overpayment` (e.g., 100k) and `NumberOfClaimHits` (e.g., 50)
  - Clustered column charts: Bin on X, Count of providers on Y, Legend = `Concept`

6) Branding
- Insert images (Machinify_Logo.jpg, BCBS_NorthCarolina_Logo.png) from visuals folder

## Notes
- CSVs have currency symbols and commas; queries here strip `$` and `,` before numeric conversion
- `Presented Hits - Summary Statistics.csv` may contain trailing blanks; queries drop null/blank rows
- Baseline date for cadence `2025-11-05` is used in the delivered dates helper query in DAX examples
- If embedding on intranet under subpath, set `WhitepapersBase` accordingly so PDF links resolve
