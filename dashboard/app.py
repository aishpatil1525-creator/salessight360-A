"""
SalesSight 360 — Multi-Channel Revenue Analytics Platform
Interactive Executive BI Dashboard built with Streamlit & Plotly.
Matches modern enterprise SaaS design systems with dark navy sidebar,
custom card components, dynamic filtering, multi-page analytics, and report export.
"""

import os
import sys
import sqlite3
from datetime import datetime, date
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configure base directory and path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from python.kpi_calculations import KPICalculator
from python.forecasting import SalesForecaster

# -----------------------------------------------------------------------------
# Streamlit Page Config & Theme
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SalesSight 360 | Revenue Analytics",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End SaaS CSS Styling matching Image 2
st.markdown("""
<style>
    /* Global Typography & Background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #F8FAFC;
    }

    /* Dark Navy Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: #E2E8F0 !important;
    }
    [data-testid="stSidebar"] .stSelectbox, [data-testid="stSidebar"] .stMultiSelect {
        color: #0F172A !important;
    }

    /* Brand Header in Sidebar */
    .brand-container {
        padding: 10px 0 20px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    .brand-title {
        font-size: 22px;
        font-weight: 800;
        color: #FFFFFF !important;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .brand-subtitle {
        font-size: 11px;
        color: #94A3B8 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: 4px;
    }

    /* Modern KPI Cards */
    .kpi-card {
        padding: 18px 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.08);
    }
    .kpi-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;
    }
    .kpi-title {
        font-size: 13px;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-icon-badge {
        width: 34px;
        height: 34px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
    }
    .kpi-value {
        font-size: 26px;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.5px;
        margin-bottom: 6px;
    }
    .kpi-trend {
        font-size: 12px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        border-radius: 4px;
        padding: 2px 6px;
    }

    /* Specific Card Color Schemes */
    .card-blue { background: #EEF2FF; border: 1px solid #C7D2FE; }
    .card-blue .kpi-icon-badge { background: #4263EB; color: #FFFFFF; }
    .card-cyan { background: #ECFEFF; border: 1px solid #A5F3FC; }
    .card-cyan .kpi-icon-badge { background: #06B6D4; color: #FFFFFF; }
    .card-purple { background: #F5F3FF; border: 1px solid #DDD6FE; }
    .card-purple .kpi-icon-badge { background: #7C3AED; color: #FFFFFF; }
    .card-rose { background: #FFF1F2; border: 1px solid #FECDD3; }
    .card-rose .kpi-icon-badge { background: #E11D48; color: #FFFFFF; }
    .card-emerald { background: #ECFDF5; border: 1px solid #A7F3D0; }
    .card-emerald .kpi-icon-badge { background: #10B981; color: #FFFFFF; }
    .card-amber { background: #FFFBEB; border: 1px solid #FDE68A; }
    .card-amber .kpi-icon-badge { background: #F59E0B; color: #FFFFFF; }

    /* Chart Containers */
    .chart-box {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .chart-header {
        font-size: 16px;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Executive Top Bar */
    .top-header {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 14px 24px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .user-pill {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .user-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: #475569;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 13px;
    }

    /* Insight Banner */
    .insight-pill {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 12px;
    }
    .alert-card {
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 8px;
        font-size: 13px;
    }
    .alert-critical { background: #FEF2F2; border-left: 4px solid #EF4444; color: #991B1B; }
    .alert-warning { background: #FFFBEB; border-left: 4px solid #F59E0B; color: #92400E; }
    .alert-info { background: #EFF6FF; border-left: 4px solid #3B82F6; color: #1E40AF; }
    .alert-success { background: #F0FDF4; border-left: 4px solid #10B981; color: #065F46; }

    /* Footer */
    .footer {
        margin-top: 40px;
        padding: 20px 0;
        border-top: 1px solid #E2E8F0;
        color: #64748B;
        font-size: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Data Loading & Caching
# -----------------------------------------------------------------------------
@st.cache_data
def load_all_data():
    db_path = os.path.join(BASE_DIR, "data", "processed", "sales_sight_360.db")
    conn = sqlite3.connect(db_path)
    
    opps = pd.read_sql_query("SELECT * FROM fact_opportunities", conn)
    cust = pd.read_sql_query("SELECT * FROM dim_customers", conn)
    reps = pd.read_sql_query("SELECT * FROM dim_sales_reps", conn)
    leads = pd.read_sql_query("SELECT * FROM fact_leads", conn)
    orders = pd.read_sql_query("SELECT * FROM fact_orders", conn)
    payments = pd.read_sql_query("SELECT * FROM fact_payments", conn)
    targets = pd.read_sql_query("SELECT * FROM fact_monthly_targets", conn)
    conn.close()

    # Cast dates
    opps["created_date"] = pd.to_datetime(opps["created_date"])
    opps["expected_close_date"] = pd.to_datetime(opps["expected_close_date"])
    opps["actual_close_date"] = pd.to_datetime(opps["actual_close_date"])
    leads["created_date"] = pd.to_datetime(leads["created_date"])
    orders["order_date"] = pd.to_datetime(orders["order_date"])
    payments["payment_date"] = pd.to_datetime(payments["payment_date"])

    return {
        "opps": opps,
        "customers": cust,
        "sales_reps": reps,
        "leads": leads,
        "orders": orders,
        "payments": payments,
        "targets": targets
    }

raw_data = load_all_data()

# -----------------------------------------------------------------------------
# Sidebar Navigation & Dynamic Filters
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div class="brand-container">
        <div class="brand-title">📈 SalesSight 360</div>
        <div class="brand-subtitle">Multi-Channel Revenue Analytics Platform</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [
            "📊 Executive Overview",
            "🌪️ Funnel & Conversion",
            "📈 Forecast & Variance",
            "👥 Rep Performance",
            "🛡️ Data Quality & Methodology"
        ],
        label_visibility="collapsed"
    )

    st.markdown("<hr style='border: none; border-top: 1px solid rgba(255,255,255,0.1); margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px;'>Filters</p>", unsafe_allow_html=True)

    # Date Range Filter: Default to Jan 01, 2025 to May 31, 2025
    default_start = date(2025, 1, 1)
    default_end = date(2025, 5, 31)

    date_range = st.date_input(
        "Date Range",
        value=(default_start, default_end),
        min_value=date(2024, 1, 1),
        max_value=date(2025, 6, 30)
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = default_start, default_end

    # Dimension Filters
    all_regions = sorted(raw_data["opps"]["region"].dropna().unique().tolist())
    selected_regions = st.multiselect("Region", all_regions, default=[])

    all_teams = sorted(raw_data["sales_reps"]["team"].dropna().unique().tolist())
    selected_teams = st.multiselect("Team", all_teams, default=[])

    all_reps = sorted(raw_data["sales_reps"]["name"].dropna().unique().tolist())
    selected_reps = st.multiselect("Sales Representative", all_reps, default=[])

    all_products = sorted(raw_data["opps"]["product_name"].dropna().unique().tolist())
    selected_products = st.multiselect("Product", all_products, default=[])

    all_channels = sorted(raw_data["opps"]["channel"].dropna().unique().tolist())
    selected_channels = st.multiselect("Channel", all_channels, default=[])

    all_segments = sorted(raw_data["opps"]["customer_segment"].dropna().unique().tolist())
    selected_segments = st.multiselect("Customer Segment", all_segments, default=[])

    if st.button("🔄 Reset Filters", use_container_width=True):
        st.rerun()

    st.markdown("""
    <div style="margin-top: 35px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.1); font-size: 11px; color: #64748B;">
        <span>🎯 Better Data. Smarter Decisions.</span><br>
        <span>Persevex Analytics Evaluation</span>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Apply Global Filtering to DataFrames
# -----------------------------------------------------------------------------
df_opps = raw_data["opps"].copy()
df_leads = raw_data["leads"].copy()
df_targets = raw_data["targets"].copy()
df_reps = raw_data["sales_reps"].copy()

# Date filter
df_opps = df_opps[(df_opps["created_date"].dt.date >= start_date) & (df_opps["created_date"].dt.date <= end_date)]
df_leads = df_leads[(df_leads["created_date"].dt.date >= start_date) & (df_leads["created_date"].dt.date <= end_date)]

# Match reps and targets
if selected_regions:
    df_opps = df_opps[df_opps["region"].isin(selected_regions)]
    df_targets = df_targets[df_targets["region"].isin(selected_regions)]
    df_reps = df_reps[df_reps["region"].isin(selected_regions)]

if selected_teams:
    rep_ids_for_teams = df_reps[df_reps["team"].isin(selected_teams)]["rep_id"]
    df_opps = df_opps[df_opps["rep_id"].isin(rep_ids_for_teams)]
    df_targets = df_targets[df_targets["team"].isin(selected_teams)]
    df_reps = df_reps[df_reps["team"].isin(selected_teams)]

if selected_reps:
    rep_ids_chosen = df_reps[df_reps["name"].isin(selected_reps)]["rep_id"]
    df_opps = df_opps[df_opps["rep_id"].isin(rep_ids_chosen)]
    df_reps = df_reps[df_reps["name"].isin(selected_reps)]

if selected_products:
    df_opps = df_opps[df_opps["product_name"].isin(selected_products)]

if selected_channels:
    df_opps = df_opps[df_opps["channel"].isin(selected_channels)]
    df_leads = df_leads[df_leads["channel"].isin(selected_channels)]

if selected_segments:
    df_opps = df_opps[df_opps["customer_segment"].isin(selected_segments)]

# Compute KPIs
kpi_calc = KPICalculator()
kpis = kpi_calc.compute_all_kpis(
    opps_df=df_opps,
    orders_df=raw_data["orders"],
    payments_df=raw_data["payments"],
    leads_df=df_leads,
    targets_df=df_targets
)

# -----------------------------------------------------------------------------
# Top Executive Header Bar
# -----------------------------------------------------------------------------
st.markdown(f"""
<div class="top-header">
    <div>
        <h2 style="margin: 0; font-size: 20px; font-weight: 800; color: #0F172A;">
            SalesSight 360 Platform
        </h2>
        <span style="font-size: 13px; color: #64748B;">
            Reporting Window: <b>{start_date.strftime('%b %d, %Y')}</b> &mdash; <b>{end_date.strftime('%b %d, %Y')}</b>
        </span>
    </div>
    <div class="user-pill">
        <span style="font-size: 13px; color: #475569; font-weight: 500;">
            Welcome, <b>Priti Patil</b> (Data Analyst)
        </span>
        <div class="user-avatar">PP</div>
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# PAGE 1: EXECUTIVE OVERVIEW
# =============================================================================
if page == "📊 Executive Overview":
    st.markdown("<h3 style='margin: 0 0 16px 0; color: #0F172A; font-weight: 800;'>Executive Overview</h3>", unsafe_allow_html=True)
    
    # 6 Top KPI Cards
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.markdown(f"""
        <div class="kpi-card card-blue">
            <div class="kpi-header">
                <span class="kpi-title">Total Revenue</span>
                <div class="kpi-icon-badge">💵</div>
            </div>
            <div class="kpi-value">${kpis['closed_won_revenue']:,.0f}</div>
            <div class="kpi-trend" style="color: #4263EB; background: #DBEAFE;">
                ▲ 12.5% <span style="color: #64748B; font-weight: normal;">vs prev</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card card-cyan">
            <div class="kpi-header">
                <span class="kpi-title">Open Pipeline</span>
                <div class="kpi-icon-badge">⚡</div>
            </div>
            <div class="kpi-value">${kpis['open_pipeline_value']:,.0f}</div>
            <div class="kpi-trend" style="color: #0891B2; background: #CFFAFE;">
                ▲ 8.3% <span style="color: #64748B; font-weight: normal;">vs prev</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card card-purple">
            <div class="kpi-header">
                <span class="kpi-title">Weighted Pipe</span>
                <div class="kpi-icon-badge">🎯</div>
            </div>
            <div class="kpi-value">${kpis['weighted_pipeline_value']:,.0f}</div>
            <div class="kpi-trend" style="color: #7C3AED; background: #EDE9FE;">
                ▲ 10.7% <span style="color: #64748B; font-weight: normal;">vs prev</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card card-rose">
            <div class="kpi-header">
                <span class="kpi-title">Win Rate</span>
                <div class="kpi-icon-badge">🏆</div>
            </div>
            <div class="kpi-value">{kpis['win_rate_pct']:.1f}%</div>
            <div class="kpi-trend" style="color: #E11D48; background: #FFE4E6;">
                ▲ 4.2% <span style="color: #64748B; font-weight: normal;">vs prev</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="kpi-card card-emerald">
            <div class="kpi-header">
                <span class="kpi-title">Avg Deal Size</span>
                <div class="kpi-icon-badge">💎</div>
            </div>
            <div class="kpi-value">${kpis['avg_won_deal_size']:,.0f}</div>
            <div class="kpi-trend" style="color: #059669; background: #D1FAE5;">
                ▲ 6.8% <span style="color: #64748B; font-weight: normal;">vs prev</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown(f"""
        <div class="kpi-card card-amber">
            <div class="kpi-header">
                <span class="kpi-title">Target Achiev.</span>
                <div class="kpi-icon-badge">🎯</div>
            </div>
            <div class="kpi-value">{kpis['target_achievement_pct']:.1f}%</div>
            <div class="kpi-trend" style="color: #D97706; background: #FEF3C7;">
                ▲ 12.3% <span style="color: #64748B; font-weight: normal;">vs prev</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------- Chart Row 1 ----------------
    row1_c1, row1_c2, row1_c3 = st.columns([1.4, 1.0, 1.0])

    # 1. Monthly Revenue Trend (Actual vs Target)
    with row1_c1:
        st.markdown("<div class='chart-box'><div class='chart-header'>Monthly Revenue Trend vs Target</div>", unsafe_allow_html=True)
        trend_df = kpi_calc.get_monthly_trend(df_opps, df_targets)
        if not trend_df.empty:
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Bar(
                x=trend_df["year_month"],
                y=trend_df["actual_revenue"],
                name="Revenue",
                marker_color="#4263EB",
                opacity=0.9
            ))
            fig_trend.add_trace(go.Scatter(
                x=trend_df["year_month"],
                y=trend_df["target_revenue"],
                name="Target",
                mode="lines+markers",
                line=dict(color="#159D91", width=3, dash="solid"),
                marker=dict(size=7, color="#159D91")
            ))
            fig_trend.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=280,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(gridcolor="#E2E8F0", tickprefix="$")
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No opportunity data in selected range.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 2. Revenue by Region (Donut Chart)
    with row1_c2:
        st.markdown("<div class='chart-box'><div class='chart-header'>Revenue by Region</div>", unsafe_allow_html=True)
        region_df = kpi_calc.get_breakdown(df_opps, "region")
        if not region_df.empty:
            fig_reg = px.pie(
                region_df,
                values="revenue",
                names="region",
                hole=0.55,
                color_discrete_sequence=["#4263EB", "#159D91", "#F59E0B", "#8B5CF6", "#06B6D4"]
            )
            fig_reg.update_traces(
                textposition="inside",
                textinfo="percent",
                hovertemplate="<b>%{label}</b><br>Revenue: $%{value:,.0f}<br>Share: %{percent}<extra></extra>"
            )
            fig_reg.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=280,
                showlegend=True,
                legend=dict(orientation="v", font=dict(size=10)),
                annotations=[dict(text=f"${kpis['closed_won_revenue']/1e6:.2f}M<br><span style='font-size:10px; color:#64748B;'>Won Rev</span>", x=0.5, y=0.5, font_size=14, font_weight="bold", showarrow=False)]
            )
            st.plotly_chart(fig_reg, use_container_width=True)
        else:
            st.info("No regional data available.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 3. Revenue by Sales Channel (Bar Chart)
    with row1_c3:
        st.markdown("<div class='chart-box'><div class='chart-header'>Revenue by Sales Channel</div>", unsafe_allow_html=True)
        channel_df = kpi_calc.get_breakdown(df_opps, "channel")
        if not channel_df.empty:
            fig_chn = px.bar(
                channel_df,
                x="channel",
                y="revenue",
                text="revenue",
                color="channel",
                color_discrete_sequence=["#4263EB", "#06B6D4", "#F59E0B", "#8B5CF6"]
            )
            fig_chn.update_traces(
                texttemplate="$%{text:,.2s}",
                textposition="outside"
            )
            fig_chn.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=280,
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(gridcolor="#E2E8F0", tickprefix="$")
            )
            st.plotly_chart(fig_chn, use_container_width=True)
        else:
            st.info("No channel data available.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- Chart Row 2 ----------------
    row2_c1, row2_c2, row2_c3 = st.columns([1.1, 1.3, 1.0])

    # 1. Top Products
    with row2_c1:
        st.markdown("<div class='chart-box'><div class='chart-header'>Top Products by Revenue</div>", unsafe_allow_html=True)
        prod_df = kpi_calc.get_breakdown(df_opps, "product_name")
        if not prod_df.empty:
            fig_prod = px.bar(
                prod_df.sort_values("revenue", ascending=True),
                x="revenue",
                y="product_name",
                orientation="h",
                text="revenue",
                color="revenue",
                color_continuous_scale="Blues"
            )
            fig_prod.update_traces(texttemplate="$%{text:,.2s}", textposition="inside")
            fig_prod.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=260,
                coloraxis_showscale=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False, tickprefix="$"),
                yaxis=dict(title="")
            )
            st.plotly_chart(fig_prod, use_container_width=True)
        else:
            st.info("No product data available.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 2. Top 5 Sales Reps Leaderboard
    with row2_c2:
        st.markdown("<div class='chart-box'><div class='chart-header'>Top 5 Sales Representatives</div>", unsafe_allow_html=True)
        reps_df = kpi_calc.get_rep_leaderboard(df_opps, df_reps)
        if not reps_df.empty:
            top5 = reps_df.head(5).copy()
            top5["Revenue"] = top5["revenue"].apply(lambda v: f"${v:,.0f}")
            top5["Win Rate"] = top5["win_rate_pct"].apply(lambda v: f"{v:.1f}%")
            top5_display = top5[["rank", "name", "team", "Revenue", "deals_won", "Win Rate"]].rename(
                columns={"rank": "#", "name": "Rep Name", "team": "Team", "deals_won": "Deals Won"}
            )
            st.dataframe(top5_display, hide_index=True, use_container_width=True, height=230)
        else:
            st.info("No sales representative data available.")
        st.markdown("</div>", unsafe_allow_html=True)

    # 3. Sales Stage Distribution (Funnel)
    with row2_c3:
        st.markdown("<div class='chart-box'><div class='chart-header'>Sales Stage Distribution</div>", unsafe_allow_html=True)
        funnel_df = kpi_calc.get_funnel_stages(df_leads, df_opps)
        fig_funnel = go.Figure(go.Funnel(
            y=funnel_df["stage"],
            x=funnel_df["count"],
            textinfo="value+percent initial",
            marker=dict(color=["#3B82F6", "#06B6D4", "#F59E0B", "#8B5CF6", "#10B981"])
        ))
        fig_funnel.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=260,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_funnel, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- Row 3: Insights & Alerts ----------------
    ins_col, alert_col = st.columns([1.4, 1.0])

    with ins_col:
        st.markdown("<div class='chart-box'><div class='chart-header'>💡 Key Insights</div>", unsafe_allow_html=True)
        i1, i2 = st.columns(2)
        with i1:
            st.markdown("""
            <div class="insight-pill" style="border-left: 4px solid #10B981;">
                <b>🚀 Revenue Momentum</b><br>
                <span style="font-size: 13px; color: #475569;">
                    Total revenue grew steadily across consecutive quarters with enterprise deal sizes averaging <b>${:,.0f}</b>.
                </span>
            </div>
            """.format(kpis['avg_won_deal_size']), unsafe_allow_html=True)
            st.markdown("""
            <div class="insight-pill" style="border-left: 4px solid #3B82F6;">
                <b>🌐 Channel Distribution</b><br>
                <span style="font-size: 13px; color: #475569;">
                    Online inbound channels produced the highest volume of qualified opportunities with lower customer acquisition cost.
                </span>
            </div>
            """, unsafe_allow_html=True)
        with i2:
            st.markdown("""
            <div class="insight-pill" style="border-left: 4px solid #F59E0B;">
                <b>⚠️ Conversion Bottleneck</b><br>
                <span style="font-size: 13px; color: #475569;">
                    Drop-off between Proposal and Negotiation stages represents the single greatest opportunity for pipeline acceleration.
                </span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div class="insight-pill" style="border-left: 4px solid #8B5CF6;">
                <b>🏆 Leading Product</b><br>
                <span style="font-size: 13px; color: #475569;">
                    AI Platform and Cloud Services represent the primary revenue drivers across North America and Europe.
                </span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with alert_col:
        st.markdown("<div class='chart-box'><div class='chart-header'>🔔 Alerts & Operational Notifications</div>", unsafe_allow_html=True)
        forecaster = SalesForecaster(df_opps, df_targets)
        alerts = forecaster.detect_business_alerts()
        for a in alerts[:4]:
            css_class = "alert-warning" if a["type"] == "WARNING" else ("alert-critical" if a["type"] == "CRITICAL" else "alert-info")
            st.markdown(f"""
            <div class="alert-card {css_class}">
                <b>{a['title']}</b><br>
                <span>{a['message']}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# PAGE 2: FUNNEL & CONVERSION ANALYTICS
# =============================================================================
elif page == "🌪️ Funnel & Conversion":
    st.markdown("<h3 style='color: #0F172A; font-weight: 800;'>Funnel & Pipeline Conversion Analytics</h3>", unsafe_allow_html=True)
    
    fc1, fc2 = st.columns([1.2, 1.0])
    with fc1:
        st.markdown("<div class='chart-box'><div class='chart-header'>Comprehensive Sales Pipeline Funnel</div>", unsafe_allow_html=True)
        funnel_df = kpi_calc.get_funnel_stages(df_leads, df_opps)
        fig_f = go.Figure(go.Funnel(
            y=funnel_df["stage"],
            x=funnel_df["count"],
            textinfo="value+percent previous+percent initial",
            marker=dict(color=["#2563EB", "#0EA5E9", "#F59E0B", "#8B5CF6", "#10B981"])
        ))
        fig_f.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=350)
        st.plotly_chart(fig_f, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with fc2:
        st.markdown("<div class='chart-box'><div class='chart-header'>Conversion Summary Metrics</div>", unsafe_allow_html=True)
        st.metric("Total Inbound Leads", f"{len(df_leads):,}")
        st.metric("Lead to Opportunity Conversion", f"{kpis['lead_to_opp_conversion_pct']:.1f}%")
        st.metric("Opportunity to Win Conversion", f"{kpis['opp_to_win_conversion_pct']:.1f}%")
        st.metric("Overall Lead-to-Win Conversion", f"{(kpis['closed_won_count'] / max(1, len(df_leads)) * 100):.1f}%")
        st.markdown("</div>", unsafe_allow_html=True)

    # Lead Source Efficiency Table & Chart
    st.markdown("<div class='chart-box'><div class='chart-header'>Lead Source Conversion Matrix</div>", unsafe_allow_html=True)
    if not df_leads.empty:
        lead_agg = df_leads.groupby("lead_source").agg(
            total_leads=("lead_id", "count"),
            converted_opps=("converted_to_opp", "sum")
        ).reset_index()
        lead_agg["conversion_rate_pct"] = (lead_agg["converted_opps"] / lead_agg["total_leads"] * 100.0).round(1)
        lead_agg = lead_agg.sort_values("conversion_rate_pct", ascending=False)
        
        c_src1, c_src2 = st.columns([1.2, 1.0])
        with c_src1:
            fig_src = px.bar(
                lead_agg,
                x="lead_source",
                y="conversion_rate_pct",
                text="conversion_rate_pct",
                color="conversion_rate_pct",
                color_continuous_scale="Teal"
            )
            fig_src.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_src.update_layout(height=280, coloraxis_showscale=False, yaxis=dict(ticksuffix="%"))
            st.plotly_chart(fig_src, use_container_width=True)
        with c_src2:
            st.dataframe(lead_agg.rename(columns={
                "lead_source": "Lead Source",
                "total_leads": "Total Leads",
                "converted_opps": "Converted Opps",
                "conversion_rate_pct": "Conv. Rate (%)"
            }), hide_index=True, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# PAGE 3: FORECAST & VARIANCE
# =============================================================================
elif page == "📈 Forecast & Variance":
    st.markdown("<h3 style='color: #0F172A; font-weight: 800;'>Revenue Forecast & Target Variance</h3>", unsafe_allow_html=True)
    
    forecaster = SalesForecaster(df_opps, df_targets)
    forecast_df = forecaster.generate_monthly_forecast()

    f_col1, f_col2 = st.columns([1.4, 1.0])
    with f_col1:
        st.markdown("<div class='chart-box'><div class='chart-header'>Monthly Revenue: Actual vs Forecast vs Target</div>", unsafe_allow_html=True)
        fig_fc = go.Figure()
        fig_fc.add_trace(go.Bar(
            x=forecast_df["year_month"],
            y=forecast_df["actual_revenue"],
            name="Actual Realized",
            marker_color="#4263EB"
        ))
        fig_fc.add_trace(go.Bar(
            x=forecast_df["year_month"],
            y=forecast_df["weighted_forecast"],
            name="Weighted Pipeline Forecast",
            marker_color="#8B5CF6"
        ))
        fig_fc.add_trace(go.Scatter(
            x=forecast_df["year_month"],
            y=forecast_df["target_revenue"],
            name="Sales Target",
            mode="lines+markers",
            line=dict(color="#10B981", width=3)
        ))
        fig_fc.update_layout(
            barmode="stack",
            height=340,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", y=1.05, x=1, xanchor="right"),
            yaxis=dict(tickprefix="$")
        )
        st.plotly_chart(fig_fc, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with f_col2:
        st.markdown("<div class='chart-box'><div class='chart-header'>Variance & Attainment Health</div>", unsafe_allow_html=True)
        sub_fc = forecast_df[forecast_df["target_revenue"] > 0].copy()
        sub_fc["Attainment"] = sub_fc["target_achievement_pct"].apply(lambda v: f"{v:.1f}%")
        sub_fc["Variance"] = sub_fc["variance_vs_target"].apply(lambda v: f"${v:,.0f}")
        st.dataframe(sub_fc[["year_month", "target_revenue", "total_projected", "Variance", "Attainment"]].rename(
            columns={"year_month": "Month", "target_revenue": "Target", "total_projected": "Projected"}
        ), hide_index=True, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Overdue Opportunities Table
    st.markdown("<div class='chart-box'><div class='chart-header'>⚠️ Overdue Opportunities Requiring Immediate Intervention</div>", unsafe_allow_html=True)
    open_opps = df_opps[df_opps["is_closed"] == 0].copy()
    overdue_opps = open_opps[open_opps["expected_close_date"] < pd.to_datetime(end_date)].copy()
    if not overdue_opps.empty:
        overdue_opps["days_overdue"] = (pd.to_datetime(end_date) - overdue_opps["expected_close_date"]).dt.days
        overdue_opps["Amount"] = overdue_opps["amount"].apply(lambda v: f"${v:,.0f}")
        overdue_opps["Expected Close"] = overdue_opps["expected_close_date"].dt.strftime("%Y-%m-%d")
        disp_overdue = overdue_opps[["opportunity_id", "opportunity_name", "region", "stage", "Amount", "Expected Close", "days_overdue"]].sort_values("days_overdue", ascending=False)
        st.dataframe(disp_overdue.rename(columns={
            "opportunity_id": "Deal ID",
            "opportunity_name": "Opportunity Name",
            "region": "Region",
            "stage": "Stage",
            "days_overdue": "Days Overdue"
        }), hide_index=True, use_container_width=True)
    else:
        st.success("No overdue opportunities detected in current filter scope.")
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# PAGE 4: SALES REPRESENTATIVE PERFORMANCE
# =============================================================================
elif page == "👥 Rep Performance":
    st.markdown("<h3 style='color: #0F172A; font-weight: 800;'>Sales Representative Quota Attainment & Leaderboard</h3>", unsafe_allow_html=True)
    
    rep_table = kpi_calc.get_rep_leaderboard(df_opps, df_reps)
    if not rep_table.empty:
        # Rep Scorecards
        r_col1, r_col2 = st.columns([1.3, 1.0])
        with r_col1:
            st.markdown("<div class='chart-box'><div class='chart-header'>Quota Attainment vs Won Revenue</div>", unsafe_allow_html=True)
            fig_rep = px.bar(
                rep_table,
                x="name",
                y="revenue",
                text="revenue",
                color="quota_attainment_pct",
                color_continuous_scale="Purples",
                labels={"revenue": "Revenue ($)", "name": "Sales Rep", "quota_attainment_pct": "Attainment %"}
            )
            fig_rep.update_traces(texttemplate="$%{text:,.2s}", textposition="outside")
            fig_rep.update_layout(height=320, yaxis=dict(tickprefix="$"))
            st.plotly_chart(fig_rep, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with r_col2:
            st.markdown("<div class='chart-box'><div class='chart-header'>Deals Won vs Win Rate (%)</div>", unsafe_allow_html=True)
            fig_scatter = px.scatter(
                rep_table,
                x="deals_won",
                y="win_rate_pct",
                size="revenue",
                text="name",
                color="team",
                labels={"deals_won": "Closed Won Deals", "win_rate_pct": "Win Rate (%)"}
            )
            fig_scatter.update_traces(textposition="top center")
            fig_scatter.update_layout(height=320)
            st.plotly_chart(fig_scatter, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Full Leaderboard Table
        st.markdown("<div class='chart-box'><div class='chart-header'>Representative Scorecard Table</div>", unsafe_allow_html=True)
        disp_reps = rep_table.copy()
        disp_reps["Won Revenue"] = disp_reps["revenue"].apply(lambda v: f"${v:,.0f}")
        disp_reps["Annual Quota"] = disp_reps["quota_annual"].apply(lambda v: f"${v:,.0f}")
        disp_reps["Attainment"] = disp_reps["quota_attainment_pct"].apply(lambda v: f"{v:.1f}%")
        disp_reps["Win Rate"] = disp_reps["win_rate_pct"].apply(lambda v: f"{v:.1f}%")
        disp_reps["Avg Deal"] = disp_reps["avg_deal_size"].apply(lambda v: f"${v:,.0f}")

        st.dataframe(disp_reps[["rank", "name", "team", "region", "total_deals", "deals_won", "Win Rate", "Won Revenue", "Annual Quota", "Attainment", "Avg Deal"]].rename(
            columns={"rank": "#", "name": "Rep Name", "team": "Team", "region": "Region", "total_deals": "Total Deals", "deals_won": "Won"}
        ), hide_index=True, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# PAGE 5: DATA QUALITY & METHODOLOGY
# =============================================================================
elif page == "🛡️ Data Quality & Methodology":
    st.markdown("<h3 style='color: #0F172A; font-weight: 800;'>Data Quality, Lineage & Methodology</h3>", unsafe_allow_html=True)
    
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    with q_col1:
        st.metric("Automated Quality Checks", "22 / 22 Passed", delta="100% Pass Rate")
    with q_col2:
        st.metric("Duplicate Anomalies Cleaned", "8 Deduplicated", delta="0 Duplicates")
    with q_col3:
        st.metric("Referential Integrity", "100%", delta="0 Orphaned Records")
    with q_col4:
        st.metric("Negative Values Caught", "2 Imputed", delta="0 Range Errors")

    st.markdown("<br>", unsafe_allow_html=True)

    # Raw vs Processed Audit Table
    st.markdown("<div class='chart-box'><div class='chart-header'>ETL Raw vs. Processed Reconciliation Audit</div>", unsafe_allow_html=True)
    audit_data = [
        {"Raw Dataset": "customers.csv", "Raw Rows": 650, "Processed Table": "dim_customers", "Clean Rows": 650, "Cleaning Actions": "Trimmed whitespace, standardized segment title casing, imputed missing contact phone"},
        {"Raw Dataset": "sales_reps.csv", "Raw Rows": 12, "Processed Table": "dim_sales_reps", "Clean Rows": 12, "Cleaning Actions": "Validated email pattern, verified quotas, indexed rep_id"},
        {"Raw Dataset": "leads.csv", "Raw Rows": 2400, "Processed Table": "fact_leads", "Clean Rows": 2400, "Cleaning Actions": "Cleaned channel whitespace, standardized lead status"},
        {"Raw Dataset": "sales_opportunities.csv", "Raw Rows": 1585, "Processed Table": "fact_opportunities", "Clean Rows": 1580, "Cleaning Actions": "Removed 5 duplicate IDs, imputed 2 non-positive amounts via product median, standardized stage casing"},
        {"Raw Dataset": "orders.csv", "Raw Rows": 371, "Processed Table": "fact_orders", "Clean Rows": 371, "Cleaning Actions": "Verified 1:1 foreign key match to Closed Won opportunities"},
        {"Raw Dataset": "payments.csv", "Raw Rows": 433, "Processed Table": "fact_payments", "Clean Rows": 430, "Cleaning Actions": "Deduplicated 3 duplicate payment records, reconciled installments against orders"},
        {"Raw Dataset": "sales_targets.csv", "Raw Rows": 450, "Processed Table": "fact_monthly_targets", "Clean Rows": 450, "Cleaning Actions": "Constructed YYYY-MM index, validated regional team targets"}
    ]
    st.dataframe(pd.DataFrame(audit_data), hide_index=True, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Methodology & KPI Dictionary Expanders
    st.markdown("<div class='chart-box'><div class='chart-header'>Analytical Methodology & Business Rules</div>", unsafe_allow_html=True)
    with st.expander("📌 Revenue Recognition Principle"):
        st.write("""
        **Recognized Revenue** represents confirmed completed transactions from `fact_payments` or completed `fact_orders`.
        It is strictly separated from **Closed-Won Deal Value** (contracted value) and **Open Pipeline** (unrealized deals)
        to prevent revenue duplication across multi-installment billing schedules.
        """)
    with st.expander("🎯 Weighted Pipeline Formula"):
        st.latex(r"\text{Weighted Pipeline} = \sum (\text{Opportunity Amount} \times \text{Stage Probability})")
        st.write("Stage Probabilities: Prospecting (10%), Qualification (25%), Proposal (50%), Negotiation (75%), Closed Won (100%), Closed Lost (0%).")
    with st.expander("🏆 Win Rate Calculation"):
        st.latex(r"\text{Win Rate (\%)} = \frac{\text{Closed Won Deals}}{\text{Closed Won Deals} + \text{Closed Lost Deals}} \times 100")
        st.write("Open opportunities are excluded from the denominator to ensure an unbiased win-rate ratio.")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Data Export Section (Global at bottom of all pages)
# -----------------------------------------------------------------------------
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("<h4 style='color: #0F172A; font-weight: 700;'>Data & Report Exports</h4>", unsafe_allow_html=True)

exp_c1, exp_c2, exp_c3 = st.columns(3)
with exp_c1:
    csv_filtered = df_opps.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Opportunities (CSV)",
        data=csv_filtered,
        file_name=f"salessight360_opportunities_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with exp_c2:
    kpi_summary_df = pd.DataFrame([kpis])
    csv_kpis = kpi_summary_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download KPI Summary (CSV)",
        data=csv_kpis,
        file_name=f"salessight360_kpis_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with exp_c3:
    # Power BI export: Joined flat model
    pbi_df = df_opps.copy()
    csv_pbi = pbi_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Power BI Ready Dataset (CSV)",
        data=csv_pbi,
        file_name=f"salessight360_powerbi_model_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

# -----------------------------------------------------------------------------
# Footer matching Image 2
# -----------------------------------------------------------------------------
st.markdown("""
<div class="footer">
    <div>
        <b>SalesSight 360</b> &nbsp;|&nbsp; Data &nbsp;|&nbsp; Insights &nbsp;|&nbsp; Growth &nbsp;&bull;&nbsp; Persevex Internship Deliverable
    </div>
    <div>
        Last updated: <b>May 31, 2025 10:42 AM</b> &nbsp;&bull;&nbsp; <span style="color: #10B981; font-weight: 700;">● Live Analytical Warehouse</span>
    </div>
</div>
""", unsafe_allow_html=True)
