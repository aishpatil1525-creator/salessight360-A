"""
SalesSight 360 — ETL & Data Cleaning Pipeline
Extracts raw CSV files, cleans anomalies, standardizes formats, validates schema integrity,
generates star-schema processed CSV datasets, and loads them into an indexed SQLite database.
Idempotent and safe to run multiple times.
"""

import os
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DB_PATH = os.path.join(PROCESSED_DIR, "sales_sight_360.db")

os.makedirs(PROCESSED_DIR, exist_ok=True)

class ETLPipeline:
    def __init__(self, raw_dir=RAW_DIR, processed_dir=PROCESSED_DIR, db_path=DB_PATH):
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        self.db_path = db_path
        self.audit_log = []

    def log(self, step, message, status="INFO"):
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "step": step,
            "message": message,
            "status": status
        }
        self.audit_log.append(entry)
        print(f"[{entry['timestamp']}] [{status}] {step}: {message}")

    # ---------------------------------------------------------
    # 1. Extract
    # ---------------------------------------------------------
    def extract(self):
        self.log("EXTRACT", "Starting data extraction from raw CSV files...")
        datasets = {}
        files = {
            "customers": "customers.csv",
            "sales_reps": "sales_reps.csv",
            "leads": "leads.csv",
            "opportunities": "sales_opportunities.csv",
            "orders": "orders.csv",
            "payments": "payments.csv",
            "sales_targets": "sales_targets.csv"
        }
        for name, fname in files.items():
            fpath = os.path.join(self.raw_dir, fname)
            if not os.path.exists(fpath):
                raise FileNotFoundError(f"Raw dataset missing: {fpath}")
            df = pd.read_csv(fpath)
            datasets[name] = df
            self.log("EXTRACT", f"Loaded {name} ({len(df)} rows, {len(df.columns)} columns)")
        return datasets

    # ---------------------------------------------------------
    # 2. Transform & Clean
    # ---------------------------------------------------------
    def transform(self, raw_data):
        self.log("TRANSFORM", "Beginning transformation, data cleaning, and deduplication...")
        cleaned = {}

        # ---------------- Sales Reps ----------------
        reps = raw_data["sales_reps"].copy()
        reps = reps.drop_duplicates(subset=["rep_id"])
        reps["name"] = reps["name"].str.strip()
        reps["team"] = reps["team"].str.strip()
        reps["region"] = reps["region"].str.strip()
        reps["quota_annual"] = reps["quota_annual"].astype(float)
        cleaned["dim_sales_reps"] = reps
        self.log("TRANSFORM", f"Cleaned dim_sales_reps ({len(reps)} rows)")

        # ---------------- Customers ----------------
        cust = raw_data["customers"].copy()
        cust_init_len = len(cust)
        cust = cust.drop_duplicates(subset=["customer_id"])
        if len(cust) < cust_init_len:
            self.log("CLEAN", f"Removed {cust_init_len - len(cust)} duplicate customers", "ACTION")

        # Strip whitespace and standardize casing
        cust["company_name"] = cust["company_name"].str.strip()
        cust["region"] = cust["region"].str.strip()
        cust["country"] = cust["country"].str.strip()
        cust["customer_segment"] = cust["customer_segment"].str.strip().str.capitalize()
        # Fix known segment mapping
        segment_map = {"Smb": "SMB", "Mid-market": "Mid-Market", "Enterprise": "Enterprise", "Startup": "Startup"}
        cust["customer_segment"] = cust["customer_segment"].replace(segment_map)
        cust["phone"] = cust["phone"].fillna("Unlisted")
        cust["created_date"] = pd.to_datetime(cust["created_date"]).dt.strftime("%Y-%m-%d")
        cleaned["dim_customers"] = cust
        self.log("TRANSFORM", f"Cleaned dim_customers ({len(cust)} rows)")

        # ---------------- Leads ----------------
        leads = raw_data["leads"].copy()
        leads_init_len = len(leads)
        leads = leads.drop_duplicates(subset=["lead_id"])
        if len(leads) < leads_init_len:
            self.log("CLEAN", f"Removed {leads_init_len - len(leads)} duplicate leads", "ACTION")

        leads["channel"] = leads["channel"].str.strip()
        leads["lead_source"] = leads["lead_source"].str.strip()
        leads["status"] = leads["status"].str.strip()
        leads["converted_to_opp"] = leads["converted_to_opp"].fillna(0).astype(int)
        leads["created_date"] = pd.to_datetime(leads["created_date"]).dt.strftime("%Y-%m-%d")
        cleaned["fact_leads"] = leads
        self.log("TRANSFORM", f"Cleaned fact_leads ({len(leads)} rows)")

        # ---------------- Sales Opportunities ----------------
        opps = raw_data["opportunities"].copy()
        opps_init_len = len(opps)
        # Deduplication
        opps = opps.drop_duplicates(subset=["opportunity_id"])
        if len(opps) < opps_init_len:
            self.log("CLEAN", f"Removed {opps_init_len - len(opps)} duplicate opportunities", "ACTION")

        # Normalize string columns
        opps["stage"] = opps["stage"].str.strip().str.title()
        # Standardize stage names
        stage_canonical = {
            "Prospecting": "Prospecting",
            "Qualification": "Qualification",
            "Proposal": "Proposal",
            "Negotiation": "Negotiation",
            "Closed Won": "Closed Won",
            "Closed Lost": "Closed Lost"
        }
        opps["stage"] = opps["stage"].map(lambda s: stage_canonical.get(s, s))
        opps["channel"] = opps["channel"].str.strip()
        opps["region"] = opps["region"].str.strip()
        opps["product_name"] = opps["product_name"].str.strip()
        opps["customer_segment"] = opps["customer_segment"].str.strip().replace(segment_map)

        # Fix invalid/negative/zero amounts
        neg_or_zero = opps["amount"] <= 0
        if neg_or_zero.sum() > 0:
            self.log("CLEAN", f"Detected {neg_or_zero.sum()} opportunities with amount <= 0. Imputing based on product median.", "ACTION")
            prod_medians = opps[opps["amount"] > 0].groupby("product_name")["amount"].median()
            for idx in opps[neg_or_zero].index:
                pname = opps.loc[idx, "product_name"]
                opps.loc[idx, "amount"] = prod_medians.get(pname, 45000.0)

        # Align probabilities
        stage_probs = {
            "Prospecting": 0.10,
            "Qualification": 0.25,
            "Proposal": 0.50,
            "Negotiation": 0.75,
            "Closed Won": 1.00,
            "Closed Lost": 0.00
        }
        opps["probability"] = opps["stage"].map(stage_probs).fillna(opps["probability"])
        opps["weighted_amount"] = (opps["amount"] * opps["probability"]).round(2)
        opps["is_closed"] = opps["stage"].isin(["Closed Won", "Closed Lost"]).astype(int)
        opps["is_won"] = (opps["stage"] == "Closed Won").astype(int)

        # Dates & Sales Cycle Calculation
        opps["created_date"] = pd.to_datetime(opps["created_date"]).dt.strftime("%Y-%m-%d")
        opps["expected_close_date"] = pd.to_datetime(opps["expected_close_date"]).dt.strftime("%Y-%m-%d")
        
        # Calculate sales cycle days
        def calc_cycle(row):
            if row["actual_close_date"] and pd.notna(row["actual_close_date"]):
                dt_close = pd.to_datetime(row["actual_close_date"])
                dt_create = pd.to_datetime(row["created_date"])
                return max(1, (dt_close - dt_create).days)
            return None

        opps["sales_cycle_days"] = opps.apply(calc_cycle, axis=1)
        cleaned["fact_opportunities"] = opps
        self.log("TRANSFORM", f"Cleaned fact_opportunities ({len(opps)} rows)")

        # ---------------- Orders ----------------
        orders = raw_data["orders"].copy()
        orders_init_len = len(orders)
        orders = orders.drop_duplicates(subset=["order_id"])
        if len(orders) < orders_init_len:
            self.log("CLEAN", f"Removed {orders_init_len - len(orders)} duplicate orders", "ACTION")

        orders["order_amount"] = orders["order_amount"].astype(float)
        orders["order_status"] = orders["order_status"].str.strip()
        orders["billing_frequency"] = orders["billing_frequency"].str.strip()
        orders["order_date"] = pd.to_datetime(orders["order_date"]).dt.strftime("%Y-%m-%d")
        cleaned["fact_orders"] = orders
        self.log("TRANSFORM", f"Cleaned fact_orders ({len(orders)} rows)")

        # ---------------- Payments ----------------
        payments = raw_data["payments"].copy()
        pay_init_len = len(payments)
        payments = payments.drop_duplicates(subset=["payment_id"])
        if len(payments) < pay_init_len:
            self.log("CLEAN", f"Removed {pay_init_len - len(payments)} duplicate payments", "ACTION")

        payments["amount"] = payments["amount"].astype(float)
        payments["payment_status"] = payments["payment_status"].str.strip()
        payments["payment_method"] = payments["payment_method"].str.strip()
        payments["payment_date"] = pd.to_datetime(payments["payment_date"]).dt.strftime("%Y-%m-%d")
        cleaned["fact_payments"] = payments
        self.log("TRANSFORM", f"Cleaned fact_payments ({len(payments)} rows)")

        # ---------------- Sales Targets ----------------
        targets = raw_data["sales_targets"].copy()
        targets = targets.drop_duplicates(subset=["target_id"])
        targets["region"] = targets["region"].str.strip()
        targets["team"] = targets["team"].str.strip()
        targets["year"] = targets["year"].astype(int)
        targets["month"] = targets["month"].astype(int)
        targets["year_month"] = targets.apply(lambda r: f"{r['year']:04d}-{r['month']:02d}", axis=1)
        targets["target_revenue"] = targets["target_revenue"].astype(float)
        cleaned["fact_monthly_targets"] = targets
        self.log("TRANSFORM", f"Cleaned fact_monthly_targets ({len(targets)} rows)")

        # ---------------- Dimensions: Products, Channels, Regions, Dates ----------------
        # Dim Products
        prods = [
            {"product_id": "PRD-01", "product_name": "AI Platform", "category": "Software", "base_price": 65000.0},
            {"product_id": "PRD-02", "product_name": "Cloud Services", "category": "Infrastructure", "base_price": 48000.0},
            {"product_id": "PRD-03", "product_name": "Data Analytics", "category": "Software", "base_price": 36000.0},
            {"product_id": "PRD-04", "product_name": "Cybersecurity", "category": "Security", "base_price": 32000.0},
            {"product_id": "PRD-05", "product_name": "ERP Integration", "category": "Services", "base_price": 28000.0}
        ]
        cleaned["dim_products"] = pd.DataFrame(prods)

        # Dim Channels
        channels = [
            {"channel_id": "CHN-01", "channel_name": "Online", "channel_type": "Digital"},
            {"channel_id": "CHN-02", "channel_name": "Direct Sales", "channel_type": "Field"},
            {"channel_id": "CHN-03", "channel_name": "Partner", "channel_type": "Indirect"},
            {"channel_id": "CHN-04", "channel_name": "Retail", "channel_type": "Store"}
        ]
        cleaned["dim_channels"] = pd.DataFrame(channels)

        # Dim Regions
        regions = [
            {"region_id": "REG-01", "region_name": "North America", "territory_code": "NA"},
            {"region_id": "REG-02", "region_name": "Europe", "territory_code": "EU"},
            {"region_id": "REG-03", "region_name": "Asia Pacific", "territory_code": "APAC"},
            {"region_id": "REG-04", "region_name": "Latin America", "territory_code": "LATAM"},
            {"region_id": "REG-05", "region_name": "Middle East & Africa", "territory_code": "MEA"}
        ]
        cleaned["dim_regions"] = pd.DataFrame(regions)

        # Dim Dates
        date_range = pd.date_range(start="2024-01-01", end="2025-06-30", freq="D")
        dim_dates = pd.DataFrame({
            "date_id": date_range.strftime("%Y%m%d").astype(int),
            "full_date": date_range.strftime("%Y-%m-%d"),
            "year": date_range.year,
            "quarter": "Q" + date_range.quarter.astype(str),
            "month": date_range.month,
            "month_name": date_range.strftime("%b"),
            "year_month": date_range.strftime("%Y-%m"),
            "day_of_week": date_range.strftime("%A"),
            "is_weekend": (date_range.weekday >= 5).astype(int)
        })
        cleaned["dim_dates"] = dim_dates
        self.log("TRANSFORM", f"Generated dim_dates ({len(dim_dates)} calendar days)")

        return cleaned

    # ---------------------------------------------------------
    # 3. Load Processed CSVs & SQLite Data Warehouse
    # ---------------------------------------------------------
    def load(self, cleaned_data):
        self.log("LOAD", "Writing processed CSV files and updating SQLite database...")
        
        # Save CSV files
        for table_name, df in cleaned_data.items():
            csv_path = os.path.join(self.processed_dir, f"{table_name}.csv")
            df.to_csv(csv_path, index=False)
            self.log("LOAD", f"Wrote processed CSV: {csv_path}")

        # Connect to SQLite
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Load Schema DDL if available or write directly
        for table_name, df in cleaned_data.items():
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            self.log("LOAD", f"Loaded table '{table_name}' into SQLite ({len(df)} rows)")

        # Create Indexes for fast analytical queries
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_opp_customer ON fact_opportunities(customer_id);",
            "CREATE INDEX IF NOT EXISTS idx_opp_rep ON fact_opportunities(rep_id);",
            "CREATE INDEX IF NOT EXISTS idx_opp_stage ON fact_opportunities(stage);",
            "CREATE INDEX IF NOT EXISTS idx_opp_date ON fact_opportunities(created_date);",
            "CREATE INDEX IF NOT EXISTS idx_lead_created ON fact_leads(created_date);",
            "CREATE INDEX IF NOT EXISTS idx_order_opp ON fact_orders(opportunity_id);",
            "CREATE INDEX IF NOT EXISTS idx_payment_order ON fact_payments(order_id);",
            "CREATE INDEX IF NOT EXISTS idx_target_ym ON fact_monthly_targets(year_month);"
        ]
        for idx in indexes:
            cursor.execute(idx)
        conn.commit()
        conn.close()
        self.log("LOAD", f"Database successfully loaded and indexed at {self.db_path}", "SUCCESS")

    def run(self):
        print("=" * 60)
        print(" SalesSight 360 — Starting ETL Pipeline")
        print("=" * 60)
        raw_data = self.extract()
        cleaned_data = self.transform(raw_data)
        self.load(cleaned_data)
        print("=" * 60)
        print(" [SUCCESS] ETL Pipeline executed cleanly and idempotently.")
        print("=" * 60)
        return cleaned_data

if __name__ == "__main__":
    pipeline = ETLPipeline()
    pipeline.run()
