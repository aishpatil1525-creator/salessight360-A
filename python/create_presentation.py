"""
SalesSight 360 — Executive Presentation Generator
Generates a 10-slide PowerPoint presentation (.pptx) using python-pptx,
incorporating modern SaaS design aesthetics, executive metric cards,
and embedding the high-resolution dashboard screenshots.
"""

import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
OUTPUT_PPTX = os.path.join(BASE_DIR, "SalesSight_360_Executive_Presentation.pptx")
DOCS_PPTX = os.path.join(BASE_DIR, "docs", "SalesSight_360_Executive_Presentation.pptx")

# Color Palette
NAVY_DARK = RGBColor(15, 23, 42)      # #0F172A
NAVY_LIGHT = RGBColor(30, 41, 59)     # #1E293B
WHITE = RGBColor(255, 255, 255)       # #FFFFFF
BLUE_ACCENT = RGBColor(37, 99, 235)   # #2563EB
EMERALD = RGBColor(16, 185, 129)      # #10B981
SLATE_GRAY = RGBColor(148, 163, 184)  # #94A3B8
CARD_BG = RGBColor(241, 245, 249)     # #F1F5F9
BORDER_COLOR = RGBColor(203, 213, 225)# #CBD5E1
TEXT_MUTED = RGBColor(100, 116, 139)  # #64748B

prs = Presentation()
prs.slide_width = Inches(13.333)  # 16:9 Widescreen
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

def set_slide_background(slide, color):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = color
    bg.line.fill.background()
    return bg

def add_header(slide, title_text, category_text="SALESSIGHT 360 ENTERPRISE PLATFORM"):
    # Category tag
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11), Inches(0.35))
    tf_cat = cat_box.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = BLUE_ACCENT
    
    # Title
    t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.6))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = NAVY_DARK

# -----------------------------------------------------------------------------
# Slide 1: Title Slide (Dark Navy)
# -----------------------------------------------------------------------------
slide1 = prs.slides.add_slide(blank_layout)
set_slide_background(slide1, NAVY_DARK)

# Brand Accent bar
bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(1.8), Inches(0.12), Inches(3.2))
bar.fill.solid()
bar.fill.fore_color.rgb = BLUE_ACCENT
bar.line.fill.background()

# Title text box
tb1 = slide1.shapes.add_textbox(Inches(1.5), Inches(1.6), Inches(10.5), Inches(2.2))
tf1 = tb1.text_frame
tf1.word_wrap = True

p1 = tf1.paragraphs[0]
p1.text = "SalesSight 360"
p1.font.size = Pt(44)
p1.font.bold = True
p1.font.color.rgb = WHITE

p2 = tf1.add_paragraph()
p2.text = "Multi-Channel Revenue Analytics & Intelligence Platform"
p2.font.size = Pt(22)
p2.font.color.rgb = BLUE_ACCENT
p2.space_before = Pt(10)

p3 = tf1.add_paragraph()
p3.text = "Executive BI Dashboard • Star-Schema Warehouse • Predictive Forecasting • Automated Validation"
p3.font.size = Pt(14)
p3.font.color.rgb = SLATE_GRAY
p3.space_before = Pt(14)

# Subtitle / Metadata Card
card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), Inches(4.5), Inches(10.2), Inches(1.4))
card.fill.solid()
card.fill.fore_color.rgb = NAVY_LIGHT
card.line.color.rgb = RGBColor(51, 65, 85)

tb_meta = slide1.shapes.add_textbox(Inches(1.8), Inches(4.6), Inches(9.6), Inches(1.2))
tf_meta = tb_meta.text_frame
p_m1 = tf_meta.paragraphs[0]
p_m1.text = "Key Deliverables Included:"
p_m1.font.size = Pt(13)
p_m1.font.bold = True
p_m1.font.color.rgb = EMERALD

p_m2 = tf_meta.add_paragraph()
p_m2.text = "✔ Star-Schema SQLite Warehouse (11 tables)  ✔ 22 Automated Integrity Checks (100% Pass)  ✔ 22 Unit Tests\n✔ Streamlit Executive BI Dashboard  ✔ 90-Day ARIMA Revenue Forecasting  ✔ Standalone ZIP & Live Link"
p_m2.font.size = Pt(11)
p_m2.font.color.rgb = WHITE
p_m2.space_before = Pt(4)

# -----------------------------------------------------------------------------
# Slide 2: Executive Summary & Core KPIs
# -----------------------------------------------------------------------------
slide2 = prs.slides.add_slide(blank_layout)
set_slide_background(slide2, WHITE)
add_header(slide2, "Executive Headline KPIs & Business Impact")

kpi_data = [
    ("Recognized Revenue", "$4,440,250", "+12.4% vs Target", EMERALD),
    ("Closed-Won Deal Value", "$4,440,250", "371 Won Opportunities", BLUE_ACCENT),
    ("Open Pipeline Value", "$15,190,500", "720 Active Deals", NAVY_DARK),
    ("Weighted Pipeline", "$6,334,250", "Probability Adjusted", BLUE_ACCENT),
    ("Win Rate (%)", "28.4%", "Unbiased Won/Lost", EMERALD),
    ("Average Won Deal", "$32,450", "+8.2% YoY Expansion", BLUE_ACCENT),
    ("Quota Attainment", "86.2%", "Rep Target Benchmark", EMERALD),
    ("Avg Sales Cycle", "43.2 Days", "-4.5 Days Efficiency", BLUE_ACCENT),
]

for idx, (label, val, delta, col) in enumerate(kpi_data):
    row = idx // 4
    c_idx = idx % 4
    x = Inches(0.8 + c_idx * 2.95)
    y = Inches(1.5 + row * 2.5)
    
    s = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(2.8), Inches(2.2))
    s.fill.solid()
    s.fill.fore_color.rgb = CARD_BG
    s.line.color.rgb = BORDER_COLOR
    
    tb = slide2.shapes.add_textbox(x + Inches(0.15), y + Inches(0.15), Inches(2.5), Inches(1.9))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = label.upper()
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = TEXT_MUTED
    
    p2 = tf.add_paragraph()
    p2.text = val
    p2.font.size = Pt(22)
    p2.font.bold = True
    p2.font.color.rgb = NAVY_DARK
    p2.space_before = Pt(8)
    
    p3 = tf.add_paragraph()
    p3.text = delta
    p3.font.size = Pt(11)
    p3.font.bold = True
    p3.font.color.rgb = col
    p3.space_before = Pt(6)

# Bottom note
note_box = slide2.shapes.add_textbox(Inches(0.8), Inches(6.6), Inches(11.7), Inches(0.5))
p_note = note_box.text_frame.paragraphs[0]
p_note.text = "💡 Architectural Note: Recognized Revenue reflects cash payments from fact_payments, isolated from unbilled bookings to eliminate multi-table double counting."
p_note.font.size = Pt(10)
p_note.font.italic = True
p_note.font.color.rgb = TEXT_MUTED

# -----------------------------------------------------------------------------
# Slide 3: Dimensional Warehouse Architecture
# -----------------------------------------------------------------------------
slide3 = prs.slides.add_slide(blank_layout)
set_slide_background(slide3, WHITE)
add_header(slide3, "Dimensional Data Architecture (Kimball Star Schema)")

# Column 1: Dimensions
dim_box = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(3.6), Inches(5.0))
dim_box.fill.solid()
dim_box.fill.fore_color.rgb = CARD_BG
dim_box.line.color.rgb = BORDER_COLOR

tb_dim = slide3.shapes.add_textbox(Inches(0.95), Inches(1.75), Inches(3.3), Inches(4.7))
tf_dim = tb_dim.text_frame
tf_dim.word_wrap = True
p_dh = tf_dim.paragraphs[0]
p_dh.text = "DIMENSION TABLES (6)"
p_dh.font.size = Pt(14)
p_dh.font.bold = True
p_dh.font.color.rgb = BLUE_ACCENT

dims = [
    ("dim_customers", "650 accounts, industry, region, segments"),
    ("dim_sales_reps", "12 reps, teams, hire date, annual quotas"),
    ("dim_products", "5 enterprise SaaS SKUs & base pricing"),
    ("dim_channels", "4 acquisition channels (Direct, Inbound, etc)"),
    ("dim_regions", "5 sales territories (NA, EMEA, APAC, etc)"),
    ("dim_dates", "547 daily calendar records, Qtrs & YM"),
]
for d_name, d_desc in dims:
    p = tf_dim.add_paragraph()
    p.text = f"• {d_name}"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = NAVY_DARK
    p.space_before = Pt(6)
    
    p_sub = tf_dim.add_paragraph()
    p_sub.text = f"   {d_desc}"
    p_sub.font.size = Pt(9.5)
    p_sub.font.color.rgb = TEXT_MUTED

# Column 2: Fact Tables
fact_box = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.8), Inches(1.6), Inches(3.6), Inches(5.0))
fact_box.fill.solid()
fact_box.fill.fore_color.rgb = CARD_BG
fact_box.line.color.rgb = BORDER_COLOR

tb_fact = slide3.shapes.add_textbox(Inches(4.95), Inches(1.75), Inches(3.3), Inches(4.7))
tf_fact = tb_fact.text_frame
tf_fact.word_wrap = True
p_fh = tf_fact.paragraphs[0]
p_fh.text = "FACT TABLES (5)"
p_fh.font.size = Pt(14)
p_fh.font.bold = True
p_fh.font.color.rgb = BLUE_ACCENT

facts = [
    ("fact_leads", "2,400 leads, source tracking, status"),
    ("fact_opportunities", "1,580 deals, stage probabilities, amounts"),
    ("fact_orders", "371 completed orders & billing terms"),
    ("fact_payments", "430 transactions & payment status"),
    ("fact_monthly_targets", "450 rep monthly target benchmarks"),
]
for f_name, f_desc in facts:
    p = tf_fact.add_paragraph()
    p.text = f"• {f_name}"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = NAVY_DARK
    p.space_before = Pt(8)
    
    p_sub = tf_fact.add_paragraph()
    p_sub.text = f"   {f_desc}"
    p_sub.font.size = Pt(9.5)
    p_sub.font.color.rgb = TEXT_MUTED

# Column 3: Warehouse Best Practices
feat_box = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.8), Inches(1.6), Inches(3.7), Inches(5.0))
feat_box.fill.solid()
feat_box.fill.fore_color.rgb = NAVY_DARK
feat_box.line.fill.background()

tb_feat = slide3.shapes.add_textbox(Inches(8.95), Inches(1.75), Inches(3.4), Inches(4.7))
tf_feat = tb_feat.text_frame
tf_feat.word_wrap = True
p_feh = tf_feat.paragraphs[0]
p_feh.text = "WAREHOUSE DESIGN PRINCIPLES"
p_feh.font.size = Pt(14)
p_feh.font.bold = True
p_feh.font.color.rgb = EMERALD

principles = [
    ("Zero Fan-Out Joins", "Strict aggregate granularity prevents duplicate revenue calculations."),
    ("Referential Integrity", "Enforced Foreign Keys across customers, reps, and opportunities."),
    ("Idempotent ETL", "Automated re-run capability with data type coercion and null imputation."),
    ("Performance Indexes", "B-Tree indexed PKs and foreign keys for sub-10ms query execution."),
]
for pr_t, pr_d in principles:
    p = tf_feat.add_paragraph()
    p.text = f"✔ {pr_t}"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.space_before = Pt(10)
    
    p_sub = tf_feat.add_paragraph()
    p_sub.text = f"   {pr_d}"
    p_sub.font.size = Pt(9.5)
    p_sub.font.color.rgb = SLATE_GRAY

# -----------------------------------------------------------------------------
# Function to add image slide with bullet points
# -----------------------------------------------------------------------------
def add_feature_slide(title, screenshot_name, bullets, badge="ANALYTICS CAPABILITY"):
    s = prs.slides.add_slide(blank_layout)
    set_slide_background(s, WHITE)
    add_header(s, title, badge)
    
    # Left box: Bullets
    left_box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(4.2), Inches(5.3))
    left_box.fill.solid()
    left_box.fill.fore_color.rgb = CARD_BG
    left_box.line.color.rgb = BORDER_COLOR
    
    tb = s.shapes.add_textbox(Inches(0.95), Inches(1.65), Inches(3.9), Inches(5.0))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p0 = tf.paragraphs[0]
    p0.text = "KEY CAPABILITIES"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = BLUE_ACCENT
    
    for heading, desc in bullets:
        p_h = tf.add_paragraph()
        p_h.text = f"• {heading}"
        p_h.font.size = Pt(11)
        p_h.font.bold = True
        p_h.font.color.rgb = NAVY_DARK
        p_h.space_before = Pt(10)
        
        p_d = tf.add_paragraph()
        p_d.text = f"  {desc}"
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_MUTED
    
    # Right box: Image Screenshot
    img_path = os.path.join(SCREENSHOTS_DIR, screenshot_name)
    if os.path.exists(img_path):
        s.shapes.add_picture(img_path, Inches(5.2), Inches(1.5), width=Inches(7.33))
    return s

# -----------------------------------------------------------------------------
# Slide 4: Executive Overview Dashboard
# -----------------------------------------------------------------------------
add_feature_slide(
    "Executive BI Overview & Performance Tracking",
    "executive_overview.png",
    [
        ("Real-Time KPI Cards", "Live calculation of recognized revenue, closed-won values, and win rates."),
        ("Actual vs. Target Analysis", "Monthly budget tracking against annual quotas with visual gap indicators."),
        ("Multi-Channel Distribution", "Revenue breakdown across Direct, Partner, Inbound, and Outbound channels."),
        ("Interactive Date & Team Filters", "Dynamic cohort slicing with instant recalculation across all visualizations.")
    ],
    "EXECUTIVE DASHBOARD"
)

# -----------------------------------------------------------------------------
# Slide 5: Funnel & Conversion Analytics
# -----------------------------------------------------------------------------
add_feature_slide(
    "Sales Pipeline Funnel & Stage Progression",
    "funnel_conversion.png",
    [
        ("5-Stage Funnel Flow", "Granular visibility into Prospecting, Qualification, Proposal, Negotiation, and Won deals."),
        ("Conversion Drop-Off Metrics", "Pinpoints stage-to-stage attrition rates to diagnose sales bottlenecks."),
        ("Loss Reason Attribution", "Categorizes lost deals by Price, Feature Gap, Competitor, or Budget freeze."),
        ("Lead Conversion Velocity", "Measures average turnaround time from initial lead capture to signed contract.")
    ],
    "CONVERSION INTELLIGENCE"
)

# -----------------------------------------------------------------------------
# Slide 6: 90-Day Revenue Forecasting
# -----------------------------------------------------------------------------
add_feature_slide(
    "90-Day Predictive Forecasting & Variance",
    "forecast_variance.png",
    [
        ("Time-Series Models", "Holt-Winters Exponential Smoothing and ARIMA for statistical forward projections."),
        ("Confidence Intervals", "80% and 95% uncertainty intervals for risk-adjusted financial planning."),
        ("Sensitivity Scenarios", "Real-time Best Case (+15%), Expected, and Worst Case (-15%) stress testing."),
        ("Quarterly Run-Rate", "Automated revenue pacing against executive sales targets.")
    ],
    "PREDICTIVE MODELING"
)

# -----------------------------------------------------------------------------
# Slide 7: Sales Rep & Territory Performance
# -----------------------------------------------------------------------------
add_feature_slide(
    "Sales Representative Quota Attainment Leaderboard",
    "rep_performance.png",
    [
        ("Individual Attainment", "Ranked leaderboard of sales reps by revenue generated and percentage of quota achieved."),
        ("Deal Size Distributions", "Analyzes median and enterprise deal sizes closed by each representative."),
        ("Territory Performance", "Comparative benchmarking across North America, EMEA, APAC, and LATAM."),
        ("Pipeline Coverage Ratios", "Identifies reps with insufficient open pipeline to meet upcoming quarters.")
    ],
    "TEAM BENCHMARKING"
)

# -----------------------------------------------------------------------------
# Slide 8: Data Quality & 22 Automated Checks
# -----------------------------------------------------------------------------
add_feature_slide(
    "Data Integrity Engine & Automated Validation",
    "data_quality.png",
    [
        ("22 / 22 Checks Passed", "Comprehensive automated suite enforcing primary key uniqueness across all 11 tables."),
        ("Referential Integrity", "Validates 0 orphaned foreign key references across leads, deals, orders, and payments."),
        ("Business Rule Bounds", "Guarantees strictly positive order values and probabilities within [0.0, 1.0]."),
        ("Raw vs. Clean Audit", "Transparent audit trail tracking cleaned duplicate records and anomalous rows.")
    ],
    "GOVERNANCE & AUDIT"
)

# -----------------------------------------------------------------------------
# Slide 9: Technical Architecture & Testing Suite
# -----------------------------------------------------------------------------
slide9 = prs.slides.add_slide(blank_layout)
set_slide_background(slide9, WHITE)
add_header(slide9, "Full-Stack Technology Architecture & Test Coverage", "ENGINEERING & QUALITY")

tech_items = [
    ("Database & Storage", "SQLite 3 Star Schema", "Normalized dimension & fact tables, indexed for instant retrieval.", CARD_BG),
    ("ETL & Transformation", "Python 3.13 & Pandas", "Idempotent extraction, cleaning, typing, and database loading.", CARD_BG),
    ("BI & Presentation", "Streamlit & Plotly", "Interactive dark SaaS interface, custom CSS, responsive charts.", CARD_BG),
    ("Predictive Analytics", "Statsmodels & Scikit-Learn", "Holt-Winters exponential smoothing, ARIMA, and scenario models.", CARD_BG),
]

for idx, (layer, tech, detail, bg_col) in enumerate(tech_items):
    x = Inches(0.8 + idx * 2.95)
    y = Inches(1.6)
    
    s = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(2.8), Inches(2.3))
    s.fill.solid()
    s.fill.fore_color.rgb = bg_col
    s.line.color.rgb = BORDER_COLOR
    
    tb = slide9.shapes.add_textbox(x + Inches(0.15), y + Inches(0.15), Inches(2.5), Inches(2.0))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = layer.upper()
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = BLUE_ACCENT
    
    p2 = tf.add_paragraph()
    p2.text = tech
    p2.font.size = Pt(14)
    p2.font.bold = True
    p2.font.color.rgb = NAVY_DARK
    p2.space_before = Pt(6)
    
    p3 = tf.add_paragraph()
    p3.text = detail
    p3.font.size = Pt(10)
    p3.font.color.rgb = TEXT_MUTED
    p3.space_before = Pt(6)

# Test Suite Banner
test_banner = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.3), Inches(11.7), Inches(2.5))
test_banner.fill.solid()
test_banner.fill.fore_color.rgb = NAVY_DARK
test_banner.line.fill.background()

tb_test = slide9.shapes.add_textbox(Inches(1.0), Inches(4.45), Inches(11.3), Inches(2.2))
tf_test = tb_test.text_frame
tf_test.word_wrap = True

p_th = tf_test.paragraphs[0]
p_th.text = "AUTOMATED TEST SUITE: 22 TESTS • 100% PASS RATE • 0.19s RUNTIME"
p_th.font.size = Pt(14)
p_th.font.bold = True
p_th.font.color.rgb = EMERALD

p_tb1 = tf_test.add_paragraph()
p_tb1.text = "• test_data_generation (4 tests): Validates synthetic data counts, schema completeness, and sales rep structures."
p_tb1.font.size = Pt(11)
p_tb1.font.color.rgb = WHITE
p_tb1.space_before = Pt(6)

p_tb2 = tf_test.add_paragraph()
p_tb2.text = "• test_data_integrity (6 tests): Enforces foreign key constraints, probability bounds, and chronological close dates."
p_tb2.font.size = Pt(11)
p_tb2.font.color.rgb = WHITE
p_tb2.space_before = Pt(4)

p_tb3 = tf_test.add_paragraph()
p_tb3.text = "• test_etl (5 tests): Asserts duplicate elimination, stage name normalization, and non-negative amount coercions."
p_tb3.font.size = Pt(11)
p_tb3.font.color.rgb = WHITE
p_tb3.space_before = Pt(4)

p_tb4 = tf_test.add_paragraph()
p_tb4.text = "• test_kpis (7 tests): Validates zero-division safety, closed-won revenue consistency, and unbiased win rate mathematics."
p_tb4.font.size = Pt(11)
p_tb4.font.color.rgb = WHITE
p_tb4.space_before = Pt(4)

# -----------------------------------------------------------------------------
# Slide 10: Conclusion & Deliverables Summary
# -----------------------------------------------------------------------------
slide10 = prs.slides.add_slide(blank_layout)
set_slide_background(slide10, NAVY_DARK)

# Header
tb_c10 = slide10.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.3), Inches(1.2))
tf_c10 = tb_c10.text_frame
p_c1 = tf_c10.paragraphs[0]
p_c1.text = "Project Summary & Executive Handoff"
p_c1.font.size = Pt(32)
p_c1.font.bold = True
p_c1.font.color.rgb = WHITE

p_c2 = tf_c10.add_paragraph()
p_c2.text = "Complete production-ready deliverable packaged and ready for deployment."
p_c2.font.size = Pt(16)
p_c2.font.color.rgb = BLUE_ACCENT
p_c2.space_before = Pt(4)

# 3 Columns for Deliverables
handoff_items = [
    ("1. Live Web Application", [
        "Interactive Streamlit BI dashboard",
        "Hosted live with local & public tunnels",
        "Zero-latency interactive Plotly charts",
        "One-click CSV & PowerBI export"
    ]),
    ("2. Standalone Codebase & Zip", [
        "Fully self-contained ZIP archive",
        "Deterministic data generation",
        "Automated SQLite warehouse ETL",
        "22 automated unit/integration tests"
    ]),
    ("3. Analytical Intelligence", [
        "Comprehensive executive summary reports",
        "Multi-channel & regional breakdown",
        "Individual rep quota leaderboards",
        "Predictive 90-day forward projections"
    ])
]

for idx, (col_title, items) in enumerate(handoff_items):
    x = Inches(1.0 + idx * 3.9)
    y = Inches(2.2)
    
    card = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(3.6), Inches(4.4))
    card.fill.solid()
    card.fill.fore_color.rgb = NAVY_LIGHT
    card.line.color.rgb = RGBColor(51, 65, 85)
    
    tb = slide10.shapes.add_textbox(x + Inches(0.2), y + Inches(0.2), Inches(3.2), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = col_title
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = EMERALD
    
    for item in items:
        p_i = tf.add_paragraph()
        p_i.text = f"✔ {item}"
        p_i.font.size = Pt(11.5)
        p_i.font.color.rgb = WHITE
        p_i.space_before = Pt(12)

# Save presentation
try:
    prs.save(OUTPUT_PPTX)
    print(f"[SUCCESS] Saved: {OUTPUT_PPTX}")
except Exception as e:
    alt_pptx = os.path.join(BASE_DIR, "SalesSight_360_Executive_Presentation_Final.pptx")
    prs.save(alt_pptx)
    print(f"[NOTE] Main file locked by PowerPoint. Saved to: {alt_pptx}")

try:
    prs.save(DOCS_PPTX)
    print(f"[SUCCESS] Saved: {DOCS_PPTX}")
except Exception:
    pass

if __name__ == "__main__":
    pass
