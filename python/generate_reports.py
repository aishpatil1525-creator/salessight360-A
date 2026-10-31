"""
SalesSight 360 — Automated Executive Report Generator
Extracts data from the processed SQLite warehouse, calculates key business KPIs,
and outputs standardized CSV and Markdown reports to reports/.
"""

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from python.kpi_calculations import KPICalculator

DB_PATH = os.path.join(BASE_DIR, "data", "processed", "sales_sight_360.db")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

def df_to_markdown(df):
    headers = list(df.columns)
    lines = ["| " + " | ".join(str(h) for h in headers) + " |"]
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(val) for val in row) + " |")
    return "\n".join(lines)

def generate():
    print("Generating Executive Analytical Reports...")
    conn = sqlite3.connect(DB_PATH)
    calc = KPICalculator(db_path=DB_PATH)
    kpis = calc.compute_all_kpis()

    # 1. Executive KPI Summary CSV
    kpi_df = pd.DataFrame([kpis])
    kpi_csv_path = os.path.join(REPORTS_DIR, "executive_kpi_summary.csv")
    kpi_df.to_csv(kpi_csv_path, index=False)
    print(f"-> Wrote {kpi_csv_path}")

    # 2. Channel Performance
    channel_query = """
    SELECT 
        o.channel,
        COUNT(DISTINCT o.opportunity_id) AS total_deals,
        SUM(CASE WHEN o.stage = 'Closed Won' THEN 1 ELSE 0 END) AS won_deals,
        ROUND(SUM(CASE WHEN o.stage = 'Closed Won' THEN o.amount ELSE 0 END), 2) AS won_revenue,
        ROUND(AVG(CASE WHEN o.stage = 'Closed Won' THEN o.amount ELSE NULL END), 2) AS avg_deal_size,
        ROUND(100.0 * SUM(CASE WHEN o.stage = 'Closed Won' THEN 1 ELSE 0 END) / 
            NULLIF(SUM(CASE WHEN o.stage IN ('Closed Won', 'Closed Lost') THEN 1 ELSE 0 END), 0), 1) AS win_rate_pct
    FROM fact_opportunities o
    GROUP BY o.channel
    ORDER BY won_revenue DESC;
    """
    channel_df = pd.read_sql_query(channel_query, conn)
    channel_csv_path = os.path.join(REPORTS_DIR, "channel_performance_report.csv")
    channel_df.to_csv(channel_csv_path, index=False)
    print(f"-> Wrote {channel_csv_path}")

    # 3. Rep Performance & Quota Attainment
    rep_query = """
    SELECT 
        r.name AS rep_name,
        r.team,
        r.region,
        r.quota_annual,
        ROUND(SUM(CASE WHEN o.stage = 'Closed Won' THEN o.amount ELSE 0 END), 2) AS closed_won_revenue,
        ROUND(100.0 * SUM(CASE WHEN o.stage = 'Closed Won' THEN o.amount ELSE 0 END) / r.quota_annual, 1) AS quota_attainment_pct
    FROM dim_sales_reps r
    LEFT JOIN fact_opportunities o ON r.rep_id = o.rep_id
    GROUP BY r.rep_id, r.name, r.team, r.region, r.quota_annual
    ORDER BY closed_won_revenue DESC;
    """
    rep_df = pd.read_sql_query(rep_query, conn)
    rep_csv_path = os.path.join(REPORTS_DIR, "rep_quota_attainment_report.csv")
    rep_df.to_csv(rep_csv_path, index=False)
    print(f"-> Wrote {rep_csv_path}")

    # 4. Regional Performance
    region_query = """
    SELECT 
        o.region,
        COUNT(DISTINCT o.opportunity_id) AS total_opportunities,
        ROUND(SUM(CASE WHEN o.stage = 'Closed Won' THEN o.amount ELSE 0 END), 2) AS closed_won_revenue,
        ROUND(100.0 * SUM(CASE WHEN o.stage = 'Closed Won' THEN 1 ELSE 0 END) / 
            NULLIF(SUM(CASE WHEN o.stage IN ('Closed Won', 'Closed Lost') THEN 1 ELSE 0 END), 0), 1) AS win_rate_pct
    FROM fact_opportunities o
    GROUP BY o.region
    ORDER BY closed_won_revenue DESC;
    """
    region_df = pd.read_sql_query(region_query, conn)
    region_csv_path = os.path.join(REPORTS_DIR, "regional_performance_report.csv")
    region_df.to_csv(region_csv_path, index=False)
    print(f"-> Wrote {region_csv_path}")

    # 5. Markdown Executive Summary
    channel_table = df_to_markdown(channel_df)
    rep_table = df_to_markdown(rep_df.head(10))
    region_table = df_to_markdown(region_df)

    md_content = f"""# SalesSight 360 — Executive Revenue Intelligence Report
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Data Warehouse**: `data/processed/sales_sight_360.db` (Star Schema)

---

## 1. Executive Summary & Core KPIs

| Metric | Value |
|---|---|
| **Total Recognized Revenue** | ${kpis.get('total_recognized_revenue', 0):,.2f} |
| **Total Closed-Won Revenue** | ${kpis.get('closed_won_revenue', 0):,.2f} |
| **Total Pipeline Value** | ${kpis.get('total_pipeline_value', 0):,.2f} |
| **Weighted Pipeline** | ${kpis.get('weighted_pipeline_value', 0):,.2f} |
| **Win Rate** | {kpis.get('win_rate', 0):.1f}% |
| **Average Won Deal Size** | ${kpis.get('average_won_deal_size', 0):,.2f} |
| **Overall Quota Attainment** | {kpis.get('quota_attainment_pct', 0):.1f}% |
| **Average Sales Cycle Length** | {kpis.get('avg_sales_cycle_days', 0):.1f} days |

---

## 2. Multi-Channel Performance Breakdown

{channel_table}

---

## 3. Regional Performance Breakdown

{region_table}

---

## 4. Sales Rep Quota Attainment & Leaderboard

{rep_table}

---
*Report generated automatically by SalesSight 360 Analytical Reporting Engine.*
"""
    md_path = os.path.join(REPORTS_DIR, "executive_revenue_report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"-> Wrote {md_path}")
    conn.close()
    print("[SUCCESS] All executive reports generated in reports/")

if __name__ == "__main__":
    generate()
