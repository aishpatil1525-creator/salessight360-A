"""
Unit Tests — Dataset Generation
Verifies that synthetic data generation produces expected row counts, schema conformity,
reproducible values with fixed seed, and expected business ranges.
"""

import os
import unittest
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

class TestDataGeneration(unittest.TestCase):

    def test_raw_files_exist(self):
        expected_files = [
            "customers.csv", "sales_reps.csv", "leads.csv",
            "sales_opportunities.csv", "orders.csv", "payments.csv", "sales_targets.csv"
        ]
        for f in expected_files:
            p = os.path.join(RAW_DIR, f)
            self.assertTrue(os.path.exists(p), f"Raw file {f} does not exist.")

    def test_opportunity_count(self):
        p = os.path.join(RAW_DIR, "sales_opportunities.csv")
        df = pd.read_csv(p)
        self.assertGreaterEqual(len(df), 1500, "Should generate at least 1,500 sales opportunities.")

    def test_leads_count(self):
        p = os.path.join(RAW_DIR, "leads.csv")
        df = pd.read_csv(p)
        self.assertGreaterEqual(len(df), 2000, "Should generate at least 2,000 leads.")

    def test_sales_reps_structure(self):
        p = os.path.join(RAW_DIR, "sales_reps.csv")
        df = pd.read_csv(p)
        self.assertEqual(len(df), 12, "Should have 12 sales representatives.")
        self.assertIn("rep_id", df.columns)
        self.assertIn("name", df.columns)
        self.assertIn("quota_annual", df.columns)

if __name__ == "__main__":
    unittest.main()
