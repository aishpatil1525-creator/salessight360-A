-- ==============================================================================
-- SalesSight 360 — Data Quality & Automated Audit Checks
-- Validates zero defects across warehouse tables: uniqueness, referential integrity,
-- range limits, and temporal consistency.
-- ==============================================================================

-- 1. Primary Key Duplicates
SELECT 'dim_customers' AS table_name, customer_id AS key_val, COUNT(*) AS occurrences 
FROM dim_customers GROUP BY customer_id HAVING COUNT(*) > 1
UNION ALL
SELECT 'dim_sales_reps', rep_id, COUNT(*) FROM dim_sales_reps GROUP BY rep_id HAVING COUNT(*) > 1
UNION ALL
SELECT 'fact_opportunities', opportunity_id, COUNT(*) FROM fact_opportunities GROUP BY opportunity_id HAVING COUNT(*) > 1
UNION ALL
SELECT 'fact_orders', order_id, COUNT(*) FROM fact_orders GROUP BY order_id HAVING COUNT(*) > 1
UNION ALL
SELECT 'fact_payments', payment_id, COUNT(*) FROM fact_payments GROUP BY payment_id HAVING COUNT(*) > 1;

-- 2. Orphaned Foreign Keys (Referential Integrity)
SELECT 'fact_opportunities -> dim_customers' AS foreign_key_test, COUNT(*) AS orphan_count
FROM fact_opportunities o
LEFT JOIN dim_customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL
UNION ALL
SELECT 'fact_opportunities -> dim_sales_reps', COUNT(*)
FROM fact_opportunities o
LEFT JOIN dim_sales_reps r ON o.rep_id = r.rep_id
WHERE r.rep_id IS NULL
UNION ALL
SELECT 'fact_orders -> fact_opportunities', COUNT(*)
FROM fact_orders ord
LEFT JOIN fact_opportunities o ON ord.opportunity_id = o.opportunity_id
WHERE o.opportunity_id IS NULL
UNION ALL
SELECT 'fact_payments -> fact_orders', COUNT(*)
FROM fact_payments p
LEFT JOIN fact_orders ord ON p.order_id = ord.order_id
WHERE ord.order_id IS NULL;

-- 3. Non-Positive Numerical Fields
SELECT 'fact_opportunities.amount <= 0' AS check_name, COUNT(*) AS violation_count
FROM fact_opportunities WHERE amount <= 0
UNION ALL
SELECT 'fact_orders.order_amount <= 0', COUNT(*)
FROM fact_orders WHERE order_amount <= 0
UNION ALL
SELECT 'fact_payments.amount <= 0', COUNT(*)
FROM fact_payments WHERE amount <= 0
UNION ALL
SELECT 'fact_opportunities.probability out of [0, 1]', COUNT(*)
FROM fact_opportunities WHERE probability < 0.0 OR probability > 1.0;

-- 4. Temporal / Date Sequence Violations
SELECT 'Close Date precedes Created Date' AS anomaly_type, COUNT(*) AS count
FROM fact_opportunities 
WHERE actual_close_date IS NOT NULL AND actual_close_date != '' AND actual_close_date < created_date;
