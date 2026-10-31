-- ==============================================================================
-- SalesSight 360 — Funnel & Conversion Analytics SQL
-- Analyzes pipeline velocity, stage conversion, drop-offs, lead source efficiency,
-- and monthly lead cohort maturation.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. Global Sales Funnel Stage Distribution & Drop-off Rates
-- ------------------------------------------------------------------------------
WITH stage_counts AS (
    SELECT 
        (SELECT COUNT(*) FROM fact_leads WHERE created_date BETWEEN '2025-01-01' AND '2025-05-31') AS total_leads,
        (SELECT COUNT(*) FROM fact_opportunities WHERE created_date BETWEEN '2025-01-01' AND '2025-05-31') AS total_opportunities,
        (SELECT COUNT(*) FROM fact_opportunities WHERE created_date BETWEEN '2025-01-01' AND '2025-05-31' AND stage IN ('Proposal', 'Negotiation', 'Closed Won')) AS stage_proposal_plus,
        (SELECT COUNT(*) FROM fact_opportunities WHERE created_date BETWEEN '2025-01-01' AND '2025-05-31' AND stage IN ('Negotiation', 'Closed Won')) AS stage_negotiation_plus,
        (SELECT COUNT(*) FROM fact_opportunities WHERE created_date BETWEEN '2025-01-01' AND '2025-05-31' AND stage = 'Closed Won') AS stage_closed_won
)
SELECT 
    '1. Leads' AS funnel_stage,
    total_leads AS count,
    100.0 AS retention_from_top_pct,
    ROUND((1.0 - (CAST(total_opportunities AS FLOAT) / NULLIF(total_leads, 0))) * 100.0, 1) AS drop_off_to_next_pct
FROM stage_counts
UNION ALL
SELECT 
    '2. Opportunities',
    total_opportunities,
    ROUND((CAST(total_opportunities AS FLOAT) / NULLIF(total_leads, 0)) * 100.0, 1),
    ROUND((1.0 - (CAST(stage_proposal_plus AS FLOAT) / NULLIF(total_opportunities, 0))) * 100.0, 1)
FROM stage_counts
UNION ALL
SELECT 
    '3. Proposal',
    stage_proposal_plus,
    ROUND((CAST(stage_proposal_plus AS FLOAT) / NULLIF(total_leads, 0)) * 100.0, 1),
    ROUND((1.0 - (CAST(stage_negotiation_plus AS FLOAT) / NULLIF(stage_proposal_plus, 0))) * 100.0, 1)
FROM stage_counts
UNION ALL
SELECT 
    '4. Negotiation',
    stage_negotiation_plus,
    ROUND((CAST(stage_negotiation_plus AS FLOAT) / NULLIF(total_leads, 0)) * 100.0, 1),
    ROUND((1.0 - (CAST(stage_closed_won AS FLOAT) / NULLIF(stage_negotiation_plus, 0))) * 100.0, 1)
FROM stage_counts
UNION ALL
SELECT 
    '5. Closed Won',
    stage_closed_won,
    ROUND((CAST(stage_closed_won AS FLOAT) / NULLIF(total_leads, 0)) * 100.0, 1),
    0.0
FROM stage_counts;

-- ------------------------------------------------------------------------------
-- 2. Lead Source Conversion Performance Matrix
-- ------------------------------------------------------------------------------
SELECT 
    l.lead_source,
    COUNT(DISTINCT l.lead_id) AS total_leads_generated,
    SUM(l.converted_to_opp) AS opportunities_created,
    ROUND(CAST(SUM(l.converted_to_opp) AS FLOAT) / NULLIF(COUNT(DISTINCT l.lead_id), 0) * 100.0, 1) AS lead_to_opp_conversion_pct,
    COUNT(DISTINCT o.opportunity_id) AS opps_tracked,
    SUM(CASE WHEN o.stage = 'Closed Won' THEN 1 ELSE 0 END) AS won_deals,
    ROUND(
        CAST(SUM(CASE WHEN o.stage = 'Closed Won' THEN 1 ELSE 0 END) AS FLOAT) / 
        NULLIF(SUM(CASE WHEN o.is_closed = 1 THEN 1 ELSE 0 END), 0) * 100.0, 
        1
    ) AS opp_to_win_rate_pct,
    COALESCE(SUM(CASE WHEN o.stage = 'Closed Won' THEN o.amount ELSE 0 END), 0) AS total_revenue_generated
FROM fact_leads l
LEFT JOIN fact_opportunities o ON l.lead_id = o.lead_id
WHERE l.created_date BETWEEN '2025-01-01' AND '2025-05-31'
GROUP BY l.lead_source
ORDER BY total_revenue_generated DESC;

-- ------------------------------------------------------------------------------
-- 3. Monthly Lead Cohort Maturation Analysis
-- ------------------------------------------------------------------------------
SELECT 
    STRFTIME('%Y-%m', l.created_date) AS lead_cohort_month,
    COUNT(DISTINCT l.lead_id) AS cohort_lead_volume,
    SUM(l.converted_to_opp) AS converted_to_opportunity,
    ROUND(CAST(SUM(l.converted_to_opp) AS FLOAT) / NULLIF(COUNT(DISTINCT l.lead_id), 0) * 100.0, 1) AS opp_conversion_rate_pct,
    SUM(CASE WHEN o.stage = 'Closed Won' THEN 1 ELSE 0 END) AS deals_won,
    ROUND(
        CAST(SUM(CASE WHEN o.stage = 'Closed Won' THEN 1 ELSE 0 END) AS FLOAT) / 
        NULLIF(COUNT(DISTINCT l.lead_id), 0) * 100.0, 
        1
    ) AS cohort_lead_to_win_pct,
    COALESCE(SUM(CASE WHEN o.stage = 'Closed Won' THEN o.amount ELSE 0 END), 0) AS total_cohort_revenue,
    ROUND(AVG(o.sales_cycle_days), 1) AS avg_days_to_close
FROM fact_leads l
LEFT JOIN fact_opportunities o ON l.lead_id = o.lead_id
WHERE l.created_date BETWEEN '2024-01-01' AND '2025-05-31'
GROUP BY STRFTIME('%Y-%m', l.created_date)
ORDER BY lead_cohort_month;
