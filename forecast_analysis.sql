-- ==============================================================================
-- SalesSight 360 — Forecast & Variance Analytics SQL
-- Reconciles actual revenue, weighted open pipeline projections, sales targets,
-- variances, and identifies operational deal risks.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. Monthly Actual vs. Forecast vs. Target Variance
-- ------------------------------------------------------------------------------
WITH actuals AS (
    SELECT 
        STRFTIME('%Y-%m', actual_close_date) AS year_month,
        SUM(amount) AS realized_won_revenue
    FROM fact_opportunities
    WHERE stage = 'Closed Won'
    GROUP BY STRFTIME('%Y-%m', actual_close_date)
),
pipeline_forecast AS (
    SELECT 
        STRFTIME('%Y-%m', expected_close_date) AS year_month,
        SUM(amount) AS unweighted_pipeline,
        SUM(weighted_amount) AS weighted_pipeline_forecast
    FROM fact_opportunities
    WHERE is_closed = 0
    GROUP BY STRFTIME('%Y-%m', expected_close_date)
),
targets AS (
    SELECT 
        year_month,
        SUM(target_revenue) AS monthly_target
    FROM fact_monthly_targets
    GROUP BY year_month
)
SELECT 
    t.year_month,
    COALESCE(a.realized_won_revenue, 0) AS actual_revenue,
    COALESCE(p.weighted_pipeline_forecast, 0) AS weighted_pipeline_forecast,
    -- Total Projected = Realized Won + Weighted Open
    (COALESCE(a.realized_won_revenue, 0) + COALESCE(p.weighted_pipeline_forecast, 0)) AS total_projected_revenue,
    t.monthly_target,
    -- Variance vs Target = Total Projected - Target
    ROUND(
        (COALESCE(a.realized_won_revenue, 0) + COALESCE(p.weighted_pipeline_forecast, 0)) - t.monthly_target, 
        2
    ) AS forecast_target_variance,
    -- Attainment Status
    CASE 
        WHEN (COALESCE(a.realized_won_revenue, 0) + COALESCE(p.weighted_pipeline_forecast, 0)) >= t.monthly_target THEN 'On Track / Exceeded'
        WHEN (COALESCE(a.realized_won_revenue, 0) + COALESCE(p.weighted_pipeline_forecast, 0)) >= (t.monthly_target * 0.90) THEN 'Slight Risk (90-99%)'
        ELSE 'High Risk (<90%)'
    END AS forecast_health_status
FROM targets t
LEFT JOIN actuals a ON t.year_month = a.year_month
LEFT JOIN pipeline_forecast p ON t.year_month = p.year_month
WHERE t.year_month BETWEEN '2025-01' AND '2025-06'
ORDER BY t.year_month;

-- ------------------------------------------------------------------------------
-- 2. Regional Target Attainment & At-Risk Summary (Current Year 2025)
-- ------------------------------------------------------------------------------
WITH reg_actuals AS (
    SELECT 
        region,
        SUM(amount) AS ytd_actual_revenue
    FROM fact_opportunities
    WHERE stage = 'Closed Won' AND created_date >= '2025-01-01'
    GROUP BY region
),
reg_pipeline AS (
    SELECT 
        region,
        SUM(weighted_amount) AS open_weighted_pipeline
    FROM fact_opportunities
    WHERE is_closed = 0
    GROUP BY region
),
reg_targets AS (
    SELECT 
        region,
        SUM(target_revenue) AS ytd_target
    FROM fact_monthly_targets
    WHERE year = 2025 AND month <= 5
    GROUP BY region
)
SELECT 
    t.region,
    COALESCE(a.ytd_actual_revenue, 0) AS actual_revenue,
    COALESCE(p.open_weighted_pipeline, 0) AS weighted_pipeline,
    t.ytd_target,
    ROUND((COALESCE(a.ytd_actual_revenue, 0) / NULLIF(t.ytd_target, 0)) * 100.0, 1) AS target_achievement_pct,
    ROUND(COALESCE(a.ytd_actual_revenue, 0) - t.ytd_target, 2) AS variance_to_target,
    CASE 
        WHEN (COALESCE(a.ytd_actual_revenue, 0) / NULLIF(t.ytd_target, 0)) >= 1.0 THEN 'Target Achieved'
        WHEN (COALESCE(a.ytd_actual_revenue, 0) / NULLIF(t.ytd_target, 0)) >= 0.88 THEN 'Near Target'
        ELSE 'At Risk'
    END AS risk_tier
FROM reg_targets t
LEFT JOIN reg_actuals a ON t.region = a.region
LEFT JOIN reg_pipeline p ON t.region = p.region
ORDER BY actual_revenue DESC;

-- ------------------------------------------------------------------------------
-- 3. Overdue Open Opportunities (Stalled Deals Requiring Intervention)
-- ------------------------------------------------------------------------------
SELECT 
    o.opportunity_id,
    o.opportunity_name,
    c.company_name,
    r.name AS rep_name,
    r.team,
    o.stage,
    o.probability,
    o.amount,
    o.expected_close_date,
    -- Days Overdue past expected close (evaluated as of 2025-05-31)
    CAST((JULIANDAY('2025-05-31') - JULIANDAY(o.expected_close_date)) AS INTEGER) AS days_overdue
FROM fact_opportunities o
JOIN dim_customers c ON o.customer_id = c.customer_id
JOIN dim_sales_reps r ON o.rep_id = r.rep_id
WHERE o.is_closed = 0 
  AND o.expected_close_date < '2025-05-31'
ORDER BY days_overdue DESC, o.amount DESC;
