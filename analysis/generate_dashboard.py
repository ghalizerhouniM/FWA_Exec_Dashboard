import os
import shutil
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from pathlib import Path
from datetime import timedelta

BASE = Path('.')
DATA_DIR = BASE
REPORTS_DIR = BASE / 'reports'
REPORTS_DIR.mkdir(exist_ok=True)
BASE_PATH = os.environ.get('BASE_PATH', '').rstrip('/')
OUTPUT_DIR = os.environ.get('OUTPUT_DIR', '').strip()

# Robust CSV loading
all_hits = pd.read_csv(
  DATA_DIR / 'All Hits - Summary Statistics.csv',
  thousands=',',
  dtype={
    'Number of Provider Hits': 'Int64',
    'Number of Claim Hits': 'Int64',
    'Number of Members Impacted': 'Int64'
  },
  engine='python',
  encoding='latin1'
)

presented_hits = pd.read_csv(
  DATA_DIR / 'Presented Hits - Summary Statistics.csv',
  thousands=',',
  engine='python',
  encoding='latin1'
)

provider_hits = pd.read_csv(
  DATA_DIR / 'All Provider Hits.csv',
  dtype={'Billing NPI': str},
  thousands=',',
  engine='python',
  encoding='latin1'
)

# Normalize column headers (strip accidental leading/trailing spaces)
for df in (all_hits, presented_hits, provider_hits):
  df.columns = df.columns.str.strip()

# Clean currency columns across all dataframes
for df in (all_hits, presented_hits, provider_hits):
    for col in df.columns:
        if df[col].astype(str).str.contains('\$').any():
            df[col] = (df[col].astype(str)
                .str.replace('$', '', regex=False)
                .str.replace(',', '', regex=False)
                .str.strip())
            df[col] = pd.to_numeric(df[col], errors='coerce')

# Normalize date columns if present
for df in (all_hits, presented_hits):
    if 'Date of Client Delivery' in df.columns:
        df['Date of Client Delivery'] = pd.to_datetime(df['Date of Client Delivery'], errors='coerce')

# Known columns for concept stats
concept_cols = [
    'Concept',
    'Date of Client Delivery',
    'Number of Provider Hits',
    'Number of Claim Hits',
    'Number of Members Impacted',
    'Total Overpayment',
    'Total Paid Amount',
    'Average Overpayment Per Provider',
    'Average Overpayment Per Claim'
]

# Aggregate statements
concepts_delivered = presented_hits['Concept'].dropna().nunique()

total_overpayment_presented = pd.to_numeric(presented_hits.get('Total Overpayment'), errors='coerce').sum()

total_overpayment_all = pd.to_numeric(all_hits.get('Total Overpayment'), errors='coerce').sum()

providers_flagged_presented = pd.to_numeric(presented_hits.get('Number of Provider Hits'), errors='coerce').sum()
providers_flagged_all = pd.to_numeric(all_hits.get('Number of Provider Hits'), errors='coerce').sum()

claims_flagged_presented = pd.to_numeric(presented_hits.get('Number of Claim Hits'), errors='coerce').sum()
claims_flagged_all = pd.to_numeric(all_hits.get('Number of Claim Hits'), errors='coerce').sum()

# Concept descriptions (presented)
# Concept descriptions with delivery date
concept_descriptions = presented_hits[['Concept', 'Date of Client Delivery', 'Description']].dropna(subset=['Concept']).drop_duplicates()
concept_descriptions['Date of Client Delivery'] = pd.to_datetime(concept_descriptions['Date of Client Delivery']).dt.date

# Concept-level stats tables (robust to missing columns)
presented_stats_cols = [c for c in concept_cols if c in presented_hits.columns]
presented_stats = presented_hits[presented_stats_cols].dropna(subset=['Concept'])
all_stats_cols = [c for c in concept_cols if c in all_hits.columns]
all_stats = all_hits[all_stats_cols].dropna(subset=['Concept'])

# Progress over time (intervals between deliveries)
presented_dates = presented_hits[['Concept', 'Date of Client Delivery']].dropna().drop_duplicates().sort_values('Date of Client Delivery')
# Compute delta days against baseline to avoid NaN for first entry
baseline = pd.Timestamp('2025-11-05')
presented_dates['Delta Days'] = (pd.to_datetime(presented_dates['Date of Client Delivery']) - baseline).dt.days
# Average successive cadence for context
avg_interval_days = pd.to_datetime(presented_dates['Date of Client Delivery']).diff().dt.days.dropna().mean()

# Distributions for provider-level metrics
# Ensure numeric types already cleaned; rename for clarity
provider_metrics = provider_hits.rename(columns={
  'Total Qualifying Paid Amount': 'Total Overpayment',
  'Number of Claim Hits': 'NumberOfClaimHits'
})

# Histogram: Total Overpayment per Provider (by Concept)
fig_paid_hist = px.histogram(
  provider_metrics,
  x='Total Overpayment',
  color='Concept',
  barmode='overlay',
  nbins=50,
  title='Distribution of Total Overpayment per Provider'
)
fig_paid_hist.update_layout(
  margin=dict(l=40, r=40, t=60, b=40),
  legend_title_text='Concept',
  xaxis_title='Total Overpayment ($)',
  yaxis_title='Count of Providers'
)
fig_paid_hist.update_traces(opacity=0.75)

# Histogram: Number of Claim Hits per Concept
fig_claims_hist = px.histogram(
  provider_metrics,
  x='NumberOfClaimHits',
  color='Concept',
  barmode='overlay',
  nbins=50,
  title='Distribution of Number of Claim Hits per Provider',
  labels={'NumberOfClaimHits': 'Number of Claim Hits'}
)
fig_claims_hist.update_layout(
  margin=dict(l=40, r=40, t=60, b=40),
  legend_title_text='Concept',
  xaxis_title='Number of Claim Hits',
  yaxis_title='Count of Providers'
)
fig_claims_hist.update_traces(opacity=0.75)

# Live tracker: Simplified "arrow of time" timelines
# Aggregate by delivery date: sum overpayment, list concepts per date
def _date_summary(df: pd.DataFrame) -> pd.DataFrame:
  d = df[['Date of Client Delivery', 'Concept', 'Total Overpayment']].copy()
  d['Date of Client Delivery'] = pd.to_datetime(d['Date of Client Delivery'], errors='coerce')
  d = d.dropna(subset=['Date of Client Delivery'])
  d['Concept'] = d['Concept'].fillna('')
  # Per-date, per-concept sums
  per_concept = (
    d.groupby(['Date of Client Delivery', 'Concept'])['Total Overpayment']
     .sum()
     .reset_index()
  )
  per_concept = per_concept[per_concept['Concept'] != '']
  # Build labels with comma-separated concept names and total per date in parentheses
  names_by_date = (
    per_concept.groupby('Date of Client Delivery')['Concept']
      .apply(lambda s: ', '.join(sorted(set(s))))
      .rename('ConceptNames')
      .reset_index()
  )
  # Total overpayment per date
  totals_by_date = (
    per_concept.groupby('Date of Client Delivery')['Total Overpayment']
      .sum()
      .rename('Total_Overpayment')
      .reset_index()
  )
  summary = totals_by_date.merge(names_by_date, on='Date of Client Delivery', how='left')
  _fmt_cur = lambda x: f"${x:,.0f}" if pd.notna(x) else "—"
  summary['ConceptLabels'] = summary.apply(
    lambda r: f"{r['ConceptNames']} ({_fmt_cur(r['Total_Overpayment'])})" if pd.notna(r['ConceptNames']) else f"({_fmt_cur(r['Total_Overpayment'])})",
    axis=1
  )
  summary = summary.sort_values('Date of Client Delivery')
  return summary

presented_summary = _date_summary(presented_hits)
all_summary = _date_summary(all_hits)

def build_timeline_html(df: pd.DataFrame, title: str, line_color: str = '#94a3b8', tick_color: str = '#0b5cab') -> str:
  if df.empty:
    return f"<div class='timeline'><div class='timeline-title'>{title}</div><div class='small'>No data available.</div></div>"
  dates = pd.to_datetime(df['Date of Client Delivery'])
  min_d, max_d = dates.min(), dates.max()
  span = (max_d - min_d).days or 1
  items = []
  for _, r in df.iterrows():
    d = pd.to_datetime(r['Date of Client Delivery'])
    pos = ((d - min_d).days / span) * 100
    date_str = pd.to_datetime(r['Date of Client Delivery']).date().isoformat()
    label = f"{date_str}<br>{r['Label']}"
    items.append(f"<div class='timeline-label' style='left:{pos}%'>{label}</div><div class='timeline-tick' style='left:{pos}%; background:{tick_color}'></div>")
  line_style = f"background:{line_color}"
  return f"<div class='timeline'><div class='timeline-title'>{title}</div><div class='timeline-line' style='{line_style}'>{''.join(items)}</div></div>"

# Line charts: Total Overpayment over time with concept labels
def build_overpayment_line_chart(df: pd.DataFrame, title: str) -> go.Figure:
  fig = go.Figure()
  if df.empty:
    fig.update_layout(title=title)
    return fig
  x = pd.to_datetime(df['Date of Client Delivery'])
  y = df['Total_Overpayment']
  text = df['ConceptLabels']
  # Position labels below the marker if near the top to avoid clipping
  top_threshold = 10_800_000  # 90% of 12M
  text_positions = ['bottom center' if (pd.notna(v) and v >= top_threshold) else 'top center' for v in y]
  fig.add_trace(go.Scatter(
    x=x,
    y=y,
    mode='lines+markers+text',
    text=text,
    textposition=text_positions,
    textfont=dict(size=11),
    cliponaxis=False,
    hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Total Overpayment: $%{y:,}<br>%{text}<extra></extra>'
  ))
  fig.update_layout(
    title=title,
    margin=dict(l=60, r=60, t=100, b=60),
    xaxis_title='Date of Client Delivery',
    yaxis_title='Total Overpayment ($)',
    showlegend=False
  )
  # Pad x-range by 10 days on each side
  min_d, max_d = x.min(), x.max()
  fig.update_xaxes(range=[min_d - timedelta(days=10), max_d + timedelta(days=10)])
  # Fix y-range to 0..12M
  fig.update_yaxes(range=[0, 12_000_000])
  return fig

fig_presented_line = build_overpayment_line_chart(presented_summary, 'Total Overpayment over Time for Presented Hits')
fig_all_line = build_overpayment_line_chart(all_summary, 'Total Overpayment over Time for All Identified Hits')

presented_line_html = pio.to_html(fig_presented_line, include_plotlyjs='cdn', full_html=False, div_id='overpayment_presented')
all_line_html = pio.to_html(fig_all_line, include_plotlyjs=False, full_html=False, div_id='overpayment_all')

# Build HTML report
style = """
<style>
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #222; }
h1, h2, h3 { color: #0b5cab; }
.container { max-width: 1100px; margin: 0 auto; padding: 20px; }
.summary { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; }
.small { color: #475569; font-size: 0.9em; }
.table-wrap { overflow-x: auto; margin: 12px 0; }
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #e2e8f0; padding: 8px 10px; text-align: left; }
th { background: #eff6ff; }
.caption { font-weight: 600; margin: 8px 0; }
.note { background: #fff7ed; border: 1px solid #fed7aa; padding: 8px; border-radius: 6px; }
.chart-grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; align-items: start; }
.timeline { margin: 8px 0 24px; }
.timeline-title { font-weight: 600; margin-bottom: 6px; }
.timeline-line { position: relative; height: 4px; background: #e2e8f0; border-radius: 2px; }
.timeline-line::after { content: ''; position: absolute; right: -12px; top: -6px; border-top: 10px solid transparent; border-bottom: 10px solid transparent; border-left: 12px solid #94a3b8; }
.timeline-tick { position: absolute; top: -6px; width: 12px; height: 12px; background: #0b5cab; border-radius: 50%; transform: translateX(-50%); }
.timeline-label { position: absolute; top: -36px; transform: translateX(-50%); white-space: normal; font-size: 0.85em; color: #334155; background: #f8fafc; padding: 4px 8px; border: 1px solid #e2e8f0; border-radius: 6px; max-width: 320px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
.brand-bar { display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 8px; }
.brand-bar img { height: 96px; object-fit: contain; }
</style>
"""
fmt_cur = lambda x: f"${x:,.0f}" if pd.notna(x) else "—"
fmt_int = lambda x: f"{int(x):,}" if pd.notna(x) else "—"
today_str = pd.Timestamp.today().strftime('%B %d, %Y')

summary_html = f"""
<div class='summary'>
  <div class='card'>
    <div class='caption'>Number of Concepts Delivered to Date</div>
    <div><strong>{concepts_delivered}</strong></div>
    <div class='small'>Distinct concepts in Presented Hits.</div>
  </div>
  <div class='card'>
    <div class='caption'>Total Estimated Overpayment</div>
    <div><strong>{fmt_cur(total_overpayment_presented)}</strong> (presented)</div>
    <div class='small'>Overall: {fmt_cur(total_overpayment_all)}</div>
  </div>
  <div class='card'>
    <div class='caption'>Providers Flagged</div>
    <div><strong>{fmt_int(providers_flagged_presented)}</strong> presented</div>
    <div class='small'>Overall flagged: {fmt_int(providers_flagged_all)}</div>
  </div>
  <div class='card'>
    <div class='caption'>Claims Flagged</div>
    <div><strong>{fmt_int(claims_flagged_presented)}</strong> presented</div>
    <div class='small'>Overall flagged: {fmt_int(claims_flagged_all)}</div>
  </div>
</div>
"""

# Build concepts table with delivery date and PDF links
concepts_df = presented_hits[['Concept', 'Date of Client Delivery', 'Description']].dropna(subset=['Concept']).drop_duplicates()
concepts_df['Date of Client Delivery'] = pd.to_datetime(concepts_df['Date of Client Delivery']).dt.date
concepts_df = concepts_df.sort_values('Date of Client Delivery')
def _concept_pdf_link(name: str) -> str:
  # Prefer relative links so both root and reports pages work; allow BASE_PATH override
  href = f"{BASE_PATH}/Whitepapers/{name}.pdf" if BASE_PATH else f"Whitepapers/{name}.pdf"
  return f"<a href='{href}' target='_blank'>{name}</a>"
concepts_df['White paper'] = concepts_df['Concept'].apply(
  lambda n: f"<a href='{(BASE_PATH + '/Whitepapers/' + n + '.pdf') if BASE_PATH else 'Whitepapers/' + n + '.pdf'}' target='_blank'>📄</a>"
)
# Keep concept names as plain text (no link)
concepts_df = concepts_df[['White paper', 'Concept', 'Date of Client Delivery', 'Description']]
concept_table_html = concepts_df.to_html(index=False, classes=['concept-table'], escape=False)

def format_currency_table(df: pd.DataFrame) -> pd.DataFrame:
  df = df.copy()
  if 'Date of Client Delivery' in df.columns:
    df['Date of Client Delivery'] = pd.to_datetime(df['Date of Client Delivery']).dt.date
  for col in ['Total Overpayment', 'Total Paid Amount', 'Average Overpayment Per Provider', 'Average Overpayment Per Claim']:
    if col in df.columns:
      df[col] = df[col].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "—")
  return df

presented_display = format_currency_table(
  presented_stats.sort_values('Date of Client Delivery') if 'Date of Client Delivery' in presented_stats.columns else presented_stats
)
presented_display = presented_display.drop(columns=['Date of Client Delivery'], errors='ignore')
presented_table_html = presented_display.to_html(index=False)
all_display = format_currency_table(
  all_stats.sort_values('Date of Client Delivery') if 'Date of Client Delivery' in all_stats.columns else all_stats
)
all_display = all_display.drop(columns=['Date of Client Delivery'], errors='ignore')
all_table_html = all_display.to_html(index=False)

# Progress intervals table
progress_df = presented_dates.copy()
progress_df['Date of Client Delivery'] = progress_df['Date of Client Delivery'].dt.date
progress_table_html = progress_df.to_html(index=False)

paid_hist_html = pio.to_html(fig_paid_hist, include_plotlyjs='cdn', full_html=False, div_id='paid_hist')
claims_hist_html = pio.to_html(fig_claims_hist, include_plotlyjs=False, full_html=False, div_id='claims_hist')

html = f"""
<!doctype html>
<html>
<head>
<meta charset='utf-8'>
<title>Executive Dashboard — FWA (BCBS NC)</title>
{style}
</head>
<body>
<div class='container'>
  <div class='brand-bar'>
    <img src='visuals/Machinify_Logo.jpg' alt='Machinify Logo'>
    <img src='visuals/BCBS_NorthCarolina_Logo.png' alt='BCBS North Carolina Logo'>
  </div>
  <h1>FWA Deliverables (BCBS NC) —  Executive Tracking Dashboard</h1>
  <p class='small'>This dashboard summarizes delivered FWA concepts, key statistics, and provider-level distributions.</p>
  <p class='small'>As of {today_str}</p>

  <h2>Aggregate Summary</h2>
  {summary_html}

  <h2>FWA Concepts Presented to BCBS NC</h2>
  <div class='table-wrap'>
    {concept_table_html}
  </div>

  <h2>Concept-Level Statistics — Presented Hits to BCBS NC</h2>
  <div class='table-wrap'>
    {presented_table_html}
  </div>

  <h2>Concept-Level Statistics — All Identified Hits</h2>
  <div class='table-wrap'>
    {all_table_html}
  </div>

  <h2>Live Tracker — Estimated Identified Overpayment Over Time</h2>
  <p class='small'>Live tracking of total overpayments identified over time.</p>
  <h3>Delivery Cadence</h3>
  <p class='small'>Days since baseline (2025-11-05); average successive cadence: <strong>{avg_interval_days:.1f} days</strong>.</p>
  <div class='table-wrap'>
    {progress_table_html}
  </div>
  <h3>Presented Hits</h3>
  {presented_line_html}
  <h3>All Identified Hits</h3>
  {all_line_html}

  

  <h2>Provider-Level Distributions Across All Identified Hits</h2>
  <p class='small'>Distribution of Total Overpayment and Number of Claim Hits per provider, shown by concept.</p>
  {paid_hist_html}
  {claims_hist_html}

</div>
</body>
</html>
"""

# Always write root-level dashboard
root_output = BASE / 'executive-dashboard.html'
root_output.write_text(html, encoding='utf-8')

written_paths = [root_output]

# Always write to reports directory as well
reports_dir = REPORTS_DIR
reports_dir.mkdir(parents=True, exist_ok=True)
# Copy Whitepapers into reports dir
src_wp = BASE / 'Whitepapers'
dst_wp = reports_dir / 'Whitepapers'
if src_wp.exists():
  if dst_wp.exists():
    shutil.rmtree(dst_wp)
  shutil.copytree(src_wp, dst_wp)
# Copy visuals into reports dir
src_vis = BASE / 'visuals'
dst_vis = reports_dir / 'visuals'
if src_vis.exists():
  if dst_vis.exists():
    shutil.rmtree(dst_vis)
  shutil.copytree(src_vis, dst_vis)
reports_output = reports_dir / 'executive-dashboard.html'
reports_output.write_text(html, encoding='utf-8')
written_paths.append(reports_output)

# Additionally write to OUTPUT_DIR when provided (and copy assets)
if OUTPUT_DIR:
  out_dir = BASE / OUTPUT_DIR
  out_dir.mkdir(parents=True, exist_ok=True)
  # Copy Whitepapers into output dir for static site completeness
  src_wp = BASE / 'Whitepapers'
  dst_wp = out_dir / 'Whitepapers'
  if src_wp.exists():
    if dst_wp.exists():
      shutil.rmtree(dst_wp)
    shutil.copytree(src_wp, dst_wp)
  # Copy visuals into output dir for static hosting of logos
  src_vis = BASE / 'visuals'
  dst_vis = out_dir / 'visuals'
  if src_vis.exists():
    if dst_vis.exists():
      shutil.rmtree(dst_vis)
    shutil.copytree(src_vis, dst_vis)
  # Avoid duplicating the reports write if OUTPUT_DIR is 'reports'
  target_output = out_dir / 'executive-dashboard.html'
  if out_dir.resolve() != reports_dir.resolve():
    target_output.write_text(html, encoding='utf-8')
    written_paths.append(target_output)

print("Wrote dashboard to: " + ", ".join(str(p) for p in written_paths))
