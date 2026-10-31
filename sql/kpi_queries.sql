-- ==============================================================================
-- SalesSight 360 — Centralized KPI Queries
-- Comprehensive analytical queries calculating key revenue and pipeline metrics
-- Note: Avoids fan-out / revenue duplication by querying fact tables cleanly.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. Executive Headline KPIs (Jan 01, 2025 - May 31, 2025)
-- ------------------------------------------------------------------------------
WITH period_opps AS (
    SELECT * FROM fact_opportunities
    WHERE created_date BETWEEN '2025-01-01' AND '2025-05-31'
),
period_orders AS (
    SELECT * FROM fact_orders
    WHERE order_date BETWEEN '2025-01-01' AND '2025-05-31'
       OR opportunity_id IN (SELECT opportunity_id FROM period_opps WHERE is_won = 1)
),
period_payments AS (
    SELECT * FROM fact_payments
    WHERE payment_date BETWEEN '2025-01-01' AND '2025-05-31'
      AND payment_status = 'Completed'
)
SELECT 
    -- 1. Total Recognized Revenue (Completed Payments)
    (SELECT COALESCE(SUM(amount), 0) FROM period_payments) AS total_recognized_revenue,
    
    -- 2. Closed-Won Opportunity Deal Value
    (SELECT COALESCE(SUM(amount), 0) FROM period_opps WHERE stage = 'Closed Won') AS closed_won_revenue,
    
    -- 3. Open Pipeline Value
    (SELECT COALESCE(SUM(amount), 0) FROM period_opps WHERE is_closed = 0) AS open_pipeline_value,
    
    -- 4. Weighted Pipeline Value
    (SELECT COALESCE(SUM(weighted_amount), 0) FROM period_opps WHERE is_closed = 0) AS weighted_pipeline_value,
    
    -- 5. Win Rate (%) = (Closed Won / (Closed Won + Closed Lost)) * 100
    ROUND(
        (SELECT CAST(COUNT(*) AS FLOAT) FROM period_opps WHERE stage = 'Closed Won') / 
        NULLIF((SELECT COUNT(*) FROM period_opps WHERE is_closed = 1), 0) * 100.0, 
        2
    ) AS win_rate_percentage,
    
    -- 6. Average Won Deal Size
    ROUND(
        (SELECT SUM(amount) FROM period_opps WHERE stage = 'Closed Won') / 
        NULLIF((SELECT COUNT(*) FROM period_opps WHERE stage = 'Closed Won'), 0), 
        2
    ) AS avg_won_deal_size;

-- ------------------------------------------------------------------------------
-- 2. Monthly Revenue Trend vs. Monthly Target
-- ------------------------------------------------------------------------------
WITH monthly_actuals AS (
    SELECT 
        STRFTIME('%Y-%m', o.order_date) AS year_month,
        SUM(o.order_amount) AS actual_revenue,
        COUNT(DISTINCT o.order_id) AS total_orders
    FROM fact_orders o
    WHERE o.order_status = 'Completed'
    GROUP BY STRFTIME('%Y-%m', o.order_date)
),
monthly_targets AS (
    SELECT 
        year_month,
        SUM(target_revenue) AS target_revenue
    FROM fact_monthly_targets
    GROUP BY year_month
)
SELECT 
    t.year_month,
    COALESCE(a.actual_revenue, 0) AS actual_revenue,
    t.target_revenue,
    ROUND(COALESCE(a.actual_revenue, 0) - t.target_revenue, 2) AS variance_dollars,
    ROUND((COALESCE(a.actual_revenue, 0) / NULLIF(t.target_revenue, 0)) * 100.0, 2) AS target_achievement_pct,
    -- Month over Month Growth
    ROUND(
        ((a.actual_revenue - LAG(a.actual_revenue) OVER (ORDER BY t.year_month)) / 
        NULLIF(LAG(a.actual_revenue) OVER (ORDER BY t.year_month), 0)) * 100.0,
        2
    ) AS mom_growth_pct
FROM monthly_targets t
LEFT JOIN monthly_actuals a ON t.year_month = a.year_month
WHERE t.year_month BETWEEN '2025-01' AND '2025-05'
ORDER BY t.year_month;

-- ------------------------------------------------------------------------------
-- 3. Revenue Breakdown by Region
-- ------------------------------------------------------------------------------
SELECT 
    o.region,
    COUNT(DISTINCT o.opportunity_id) AS total_opportunities,
    SUM(CASE WHEN o.stage = 'Closed Won' THEN 1 ELSE 0 END) AS won_deals,
    SUM(CASE WHEN o.stage = 'Closed Won' THEN o.amount ELSE 0 END) AS won_revenue,
    ROUND(
        SUM(CASE WHEN o.stage = 'Closed Won' THEN o.amount ELSE 0 END) * 100.0 / 
        NULLIF((SELECT SUM(amount) FROM fact_opportunities WHERE stage = 'Closed Won' AND created_date BETWEEN '2025-01-01' AND '2025-05-31'), 0), 
        2
    ) AS revenue_share_pct
FROM fact_opportunities o
WHERE o.created_date BETWEEN '2025-01-01' AND '2025-05-31'
GROUP BY o.region
ORDER BY won_revenue DESC;

-- ------------------------------------------------------------------------------
-- 4. Revenue Breakdown by Sales Channel
-- ------------------------------------------------------------------------------
SELECT 
    o.channel,
    COUNT(DISTINCT o.opportunity_id) AS total_opportunities,
    SUM(CASE WHEN o.stage = 'Closed Won' THEN 1 ELSE 0 END) AS won_deals,
    SUM(CASE WHEN o.stage = 'Closed Won' THEN o.amount ELSE 0 END) AS won_revenue,
    ROUND(
        SUM(CASE WHEN o.stage = 'Closed Won' THEN o.amount ELSE 0 END) * 100.0 / 
        NULLIF((SELECT SUM(amount) FROM fact_opportunities WHERE stage = 'Closed Won' AND created_date BETWEEN '2025-01-01' AND '2025-05-31'), 0), 
        2
    ) AS revenue_share_pct
FROM fact_opportunities o
WHERE o.created_date BETWEEN '2025-01-01' AND '2025-05-31'
GROUP BY o.channel
ORDER BY won_revenue DESC;

-- ------------------------------------------------------------------------------
-- 5. Top 5 Products by Revenue
-- ------------------------------------------------------------------------------
SELECT 
    o.product_name,
    COUNT(DISTINCT o.opportunity_id) AS deal_count,
    SUM(CASE WHEN o.stage = 'Closed Won' THEN o.amount ELSE 0 END) AS product_revenue,
    ROUND(
        SUM(CASE WHEN o.stage = 'Closed Won' THEN o.amount ELSE 0 END) * 100.0 / 
        NULLIF((SELECT SUM(amount) FROM fact_opportunities WHERE stage = 'Closed Won' AND created_date BETWEEN '2025-01-01' AND '2025-05-31'), 0), 
        2
    ) AS revenue_share_pct
FROM fact_opportunities o
WHERE o.created_date BETWEEN '2025-01-01' AND '2025-05-31'
GROUP BY o.product_name
ORDER BY product_revenue DESC;

-- ------------------------------------------------------------------------------
-- 6. Top 5 Sales Representatives Leaderboard
-- ------------------------------------------------------------------------------
SELECT 
    r.name AS rep_name,
    r.team,
    r.region,
    COUNT(DISTINCT o.opportunity_id) AS total_deals,
    SUM(CASE WHEN o.stage = 'Closed Won' THEN 1 ELSE 0 END) AS deals_won,
    ROUND(
        CAST(SUM(CASE WHEN o.stage = 'Closed Won' THEN 1 ELSE 0 END) AS FLOAT) / 
        NULLIF(SUM(CASE WHEN o.is_closed = 1 THEN 1 ELSE 0 END), 0) * 100.0, 
        1
    ) AS win_rate_pct,
    SUM(CASE WHEN o.stage = 'Closed Won' THEN o.amount ELSE 0 END) AS total_won_revenue,
    ROUND(
        SUM(CASE WHEN o.stage = 'Closed Won' THEN o.amount ELSE 0 END) / 
        NULLIF(SUM(CASE WHEN o.stage = 'Closed Won' THEN 1 ELSE 0 END), 0), 
        0
    ) AS avg_deal_size
FROM dim_sales_reps r
LEFT JOIN fact_opportunities o ON r.rep_id = o.rep_id 
    AND o.created_date BETWEEN '2025-01-01' AND '2025-05-31'
GROUP BY r.rep_id, r.name, r.team, r.region
ORDER BY total_won_revenue DESC
LIMIT 5;
