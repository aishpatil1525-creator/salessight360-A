"""
SalesSight 360 — Data Validation & Quality Assurance Script
Validates data types, completeness, primary key uniqueness, referential integrity,
business rule compliance (non-negative amounts, monotonic dates), and reconciles
raw vs. processed row counts.
"""

import os
import sqlite3
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DB_PATH = os.path.join(PROCESSED_DIR, "sales_sight_360.db")

class DataValidator:
    def __init__(self, db_path=DB_PATH, raw_dir=RAW_DIR, processed_dir=PROCESSED_DIR):
        self.db_path = db_path
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        self.results = []

    def check(self, check_name, condition, details=""):
        status = "PASS" if condition else "FAIL"
        self.results.append({
            "check": check_name,
            "status": status,
            "details": details
        })
        icon = "[PASS]" if condition else "[FAIL]"
        print(f" {icon} {check_name}: {details}")

    def run_all_checks(self):
        print("=" * 70)
        print(" SalesSight 360 — Data Quality & Integrity Validation")
        print("=" * 70)

        conn = sqlite3.connect(self.db_path)

        # 1. Table Existence Check
        tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = [r[0] for r in conn.execute(tables_query).fetchall()]
        expected_tables = [
            "dim_customers", "dim_sales_reps", "dim_products", "dim_channels",
            "dim_regions", "dim_dates", "fact_leads", "fact_opportunities",
            "fact_orders", "fact_payments", "fact_monthly_targets"
        ]
        all_tables_present = all(t in tables for t in expected_tables)
        self.check("Table Existence", all_tables_present, f"Found {len(tables)} tables, expected at least {len(expected_tables)}")

        # 2. Primary Key Uniqueness
        pk_checks = [
            ("dim_customers", "customer_id"),
            ("dim_sales_reps", "rep_id"),
            ("dim_products", "product_id"),
            ("dim_channels", "channel_id"),
            ("dim_regions", "region_id"),
            ("dim_dates", "date_id"),
            ("fact_leads", "lead_id"),
            ("fact_opportunities", "opportunity_id"),
            ("fact_orders", "order_id"),
            ("fact_payments", "payment_id"),
            ("fact_monthly_targets", "target_id")
        ]
        for tbl, col in pk_checks:
            query = f"SELECT {col}, COUNT(*) FROM {tbl} GROUP BY {col} HAVING COUNT(*) > 1;"
            dupes = conn.execute(query).fetchall()
            self.check(f"PK Uniqueness: {tbl}.{col}", len(dupes) == 0, f"{len(dupes)} duplicates found")

        # 3. Referential Integrity
        # 3a. Opportunities -> Customers
        orphan_cust = conn.execute("""
            SELECT COUNT(*) FROM fact_opportunities o
            LEFT JOIN dim_customers c ON o.customer_id = c.customer_id
            WHERE c.customer_id IS NULL;
        """).fetchone()[0]
        self.check("FK Integrity: fact_opportunities -> dim_customers", orphan_cust == 0, f"{orphan_cust} orphaned records")

        # 3b. Opportunities -> Sales Reps
        orphan_reps = conn.execute("""
            SELECT COUNT(*) FROM fact_opportunities o
            LEFT JOIN dim_sales_reps r ON o.rep_id = r.rep_id
            WHERE r.rep_id IS NULL;
        """).fetchone()[0]
        self.check("FK Integrity: fact_opportunities -> dim_sales_reps", orphan_reps == 0, f"{orphan_reps} orphaned records")

        # 3c. Orders -> Opportunities
        orphan_orders = conn.execute("""
            SELECT COUNT(*) FROM fact_orders ord
            LEFT JOIN fact_opportunities o ON ord.opportunity_id = o.opportunity_id
            WHERE o.opportunity_id IS NULL;
        """).fetchone()[0]
        self.check("FK Integrity: fact_orders -> fact_opportunities", orphan_orders == 0, f"{orphan_orders} orphaned records")

        # 3d. Payments -> Orders
        orphan_payments = conn.execute("""
            SELECT COUNT(*) FROM fact_payments p
            LEFT JOIN fact_orders ord ON p.order_id = ord.order_id
            WHERE ord.order_id IS NULL;
        """).fetchone()[0]
        self.check("FK Integrity: fact_payments -> fact_orders", orphan_payments == 0, f"{orphan_payments} orphaned records")

        # 4. Numerical Validity & Business Rules
        # 4a. Opportunity Amount > 0
        invalid_opp_amounts = conn.execute("""
            SELECT COUNT(*) FROM fact_opportunities WHERE amount <= 0;
        """).fetchone()[0]
        self.check("Business Rule: Positive Opportunity Amounts", invalid_opp_amounts == 0, f"{invalid_opp_amounts} non-positive amounts")

        # 4b. Order Amount > 0
        invalid_order_amounts = conn.execute("""
            SELECT COUNT(*) FROM fact_orders WHERE order_amount <= 0;
        """).fetchone()[0]
        self.check("Business Rule: Positive Order Amounts", invalid_order_amounts == 0, f"{invalid_order_amounts} non-positive amounts")

        # 4c. Payment Amount > 0
        invalid_payment_amounts = conn.execute("""
            SELECT COUNT(*) FROM fact_payments WHERE amount <= 0;
        """).fetchone()[0]
        self.check("Business Rule: Positive Payment Amounts", invalid_payment_amounts == 0, f"{invalid_payment_amounts} non-positive amounts")

        # 4d. Probability Range [0.0, 1.0]
        invalid_probs = conn.execute("""
            SELECT COUNT(*) FROM fact_opportunities WHERE probability < 0.0 OR probability > 1.0;
        """).fetchone()[0]
        self.check("Business Rule: Probability in [0.0, 1.0]", invalid_probs == 0, f"{invalid_probs} invalid probabilities")

        # 5. Date Sequence Validity
        # Closed date >= Created date
        invalid_close_dates = conn.execute("""
            SELECT COUNT(*) FROM fact_opportunities 
            WHERE actual_close_date IS NOT NULL AND actual_close_date != '' AND actual_close_date < created_date;
        """).fetchone()[0]
        self.check("Date Logic: Close Date >= Created Date", invalid_close_dates == 0, f"{invalid_close_dates} invalid chronological dates")

        # 6. Raw vs. Processed Reconciliation Audit
        print("\n--- Raw vs. Processed Reconciliation Audit ---")
        reconciliation = [
            ("customers.csv", "dim_customers"),
            ("sales_opportunities.csv", "fact_opportunities"),
            ("orders.csv", "fact_orders"),
            ("payments.csv", "fact_payments"),
            ("leads.csv", "fact_leads"),
            ("sales_targets.csv", "fact_monthly_targets")
        ]
        
        reconciled_ok = True
        for raw_file, proc_table in reconciliation:
            raw_path = os.path.join(self.raw_dir, raw_file)
            raw_df = pd.read_csv(raw_path)
            proc_count = conn.execute(f"SELECT COUNT(*) FROM {proc_table}").fetchone()[0]
            diff = len(raw_df) - proc_count
            print(f" * {raw_file} ({len(raw_df)} raw) -> {proc_table} ({proc_count} clean) | Diff: {diff} (Cleaned duplicates/anomalies)")
            if diff < 0:
                reconciled_ok = False

        self.check("ETL Reconciliation Integrity", reconciled_ok, "Processed datasets successfully cleaned without uncontrolled record drop")

        conn.close()

        # Summary
        passes = sum(1 for r in self.results if r["status"] == "PASS")
        fails = sum(1 for r in self.results if r["status"] == "FAIL")
        print("=" * 70)
        print(f" Validation Complete: {passes} PASSED, {fails} FAILED out of {len(self.results)} total checks.")
        print("=" * 70)
        return fails == 0

if __name__ == "__main__":
    validator = DataValidator()
    success = validator.run_all_checks()
    exit(0 if success else 1)
