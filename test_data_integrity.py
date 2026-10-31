"""
Unit Tests — Database Referential Integrity & Schema Constraints
Validates foreign key relations, positive values, and valid chronological order.
"""

import os
import unittest
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "processed", "sales_sight_360.db")

class TestDataIntegrity(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(DB_PATH)

    def tearDown(self):
        self.conn.close()

    def test_opportunity_customer_fk(self):
        orphans = self.conn.execute("""
            SELECT COUNT(*) FROM fact_opportunities o
            LEFT JOIN dim_customers c ON o.customer_id = c.customer_id
            WHERE c.customer_id IS NULL;
        """).fetchone()[0]
        self.assertEqual(orphans, 0, "All opportunities must reference a valid customer.")

    def test_opportunity_rep_fk(self):
        orphans = self.conn.execute("""
            SELECT COUNT(*) FROM fact_opportunities o
            LEFT JOIN dim_sales_reps r ON o.rep_id = r.rep_id
            WHERE r.rep_id IS NULL;
        """).fetchone()[0]
        self.assertEqual(orphans, 0, "All opportunities must reference a valid sales representative.")

    def test_order_opportunity_fk(self):
        orphans = self.conn.execute("""
            SELECT COUNT(*) FROM fact_orders ord
            LEFT JOIN fact_opportunities o ON ord.opportunity_id = o.opportunity_id
            WHERE o.opportunity_id IS NULL;
        """).fetchone()[0]
        self.assertEqual(orphans, 0, "All orders must reference a valid opportunity.")

    def test_payment_order_fk(self):
        orphans = self.conn.execute("""
            SELECT COUNT(*) FROM fact_payments p
            LEFT JOIN fact_orders ord ON p.order_id = ord.order_id
            WHERE ord.order_id IS NULL;
        """).fetchone()[0]
        self.assertEqual(orphans, 0, "All payments must reference a valid order.")

    def test_probability_range(self):
        invalid = self.conn.execute("SELECT COUNT(*) FROM fact_opportunities WHERE probability < 0.0 OR probability > 1.0").fetchone()[0]
        self.assertEqual(invalid, 0, "Probabilities must be between 0.0 and 1.0.")

    def test_chronological_close_date(self):
        invalid = self.conn.execute("""
            SELECT COUNT(*) FROM fact_opportunities 
            WHERE actual_close_date IS NOT NULL AND actual_close_date != '' AND actual_close_date < created_date
        """).fetchone()[0]
        self.assertEqual(invalid, 0, "Actual close date cannot precede deal created date.")

if __name__ == "__main__":
    unittest.main()
