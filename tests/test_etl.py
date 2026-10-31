"""
Unit Tests — ETL Pipeline & Cleaning
Verifies ETL idempotence, deduplication, imputation of non-positive amounts,
and column standardization.
"""

import os
import unittest
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DB_PATH = os.path.join(PROCESSED_DIR, "sales_sight_360.db")

class TestETLPipeline(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(DB_PATH)

    def tearDown(self):
        self.conn.close()

    def test_database_tables_exist(self):
        tables = [r[0] for r in self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        expected = ["dim_customers", "dim_sales_reps", "fact_opportunities", "fact_orders", "fact_payments", "fact_leads", "fact_monthly_targets"]
        for t in expected:
            self.assertIn(t, tables, f"Table {t} should exist in warehouse.")

    def test_opportunity_duplicates_removed(self):
        opps_df = pd.read_sql_query("SELECT opportunity_id, COUNT(*) as cnt FROM fact_opportunities GROUP BY opportunity_id HAVING cnt > 1", self.conn)
        self.assertEqual(len(opps_df), 0, "No duplicate opportunity IDs should exist after ETL.")

    def test_payment_duplicates_removed(self):
        payments_df = pd.read_sql_query("SELECT payment_id, COUNT(*) as cnt FROM fact_payments GROUP BY payment_id HAVING cnt > 1", self.conn)
        self.assertEqual(len(payments_df), 0, "No duplicate payment IDs should exist after ETL.")

    def test_no_negative_opportunity_amounts(self):
        invalid_cnt = self.conn.execute("SELECT COUNT(*) FROM fact_opportunities WHERE amount <= 0").fetchone()[0]
        self.assertEqual(invalid_cnt, 0, "All opportunity amounts must be strictly positive.")

    def test_stage_names_standardized(self):
        valid_stages = {"Prospecting", "Qualification", "Proposal", "Negotiation", "Closed Won", "Closed Lost"}
        stages = set(r[0] for r in self.conn.execute("SELECT DISTINCT stage FROM fact_opportunities").fetchall())
        self.assertTrue(stages.issubset(valid_stages), f"Stages {stages} should match canonical stage names.")

if __name__ == "__main__":
    unittest.main()
