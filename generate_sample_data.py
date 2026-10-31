"""
SalesSight 360 — Sample Data Generator
Generates realistic multi-channel B2B/B2C SaaS sales data with reproducible random seed.
Produces raw CSV datasets with realistic business distributions, valid foreign keys,
and documented intentional anomalies for the ETL data cleaning pipeline.
"""

import os
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Set fixed seed for complete reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

# -------------------------------------------------------------
# Configuration Constants
# -------------------------------------------------------------
REGIONS = {
    "North America": {"weight": 0.33, "countries": ["United States", "Canada"]},
    "Europe": {"weight": 0.25, "countries": ["United Kingdom", "Germany", "France", "Netherlands"]},
    "Asia Pacific": {"weight": 0.19, "countries": ["Singapore", "Australia", "Japan", "India"]},
    "Latin America": {"weight": 0.14, "countries": ["Brazil", "Mexico", "Chile", "Colombia"]},
    "Middle East & Africa": {"weight": 0.09, "countries": ["UAE", "Saudi Arabia", "South Africa"]}
}

CUSTOMER_SEGMENTS = {
    "Enterprise": {"weight": 0.25, "deal_multiplier": 2.8},
    "Mid-Market": {"weight": 0.35, "deal_multiplier": 1.4},
    "SMB": {"weight": 0.28, "deal_multiplier": 0.6},
    "Startup": {"weight": 0.12, "deal_multiplier": 0.4}
}

CHANNELS = {
    "Online": 0.31,
    "Direct Sales": 0.28,
    "Partner": 0.23,
    "Retail": 0.18
}

PRODUCTS = {
    "AI Platform": {"base_price": 65000, "weight": 0.25},
    "Cloud Services": {"base_price": 48000, "weight": 0.22},
    "Data Analytics": {"base_price": 36000, "weight": 0.20},
    "Cybersecurity": {"base_price": 32000, "weight": 0.18},
    "ERP Integration": {"base_price": 28000, "weight": 0.15}
}

SALES_REPS = [
    {"rep_id": "REP-101", "name": "Rohan Sharma", "team": "Enterprise East", "region": "North America", "hire_date": "2022-03-15", "quota_annual": 2500000},
    {"rep_id": "REP-102", "name": "Priya Nair", "team": "Enterprise West", "region": "North America", "hire_date": "2022-06-01", "quota_annual": 2400000},
    {"rep_id": "REP-103", "name": "Amit Verma", "team": "Mid-Market Global", "region": "Asia Pacific", "hire_date": "2023-01-10", "quota_annual": 1800000},
    {"rep_id": "REP-104", "name": "Neha Singh", "team": "Inbound Growth", "region": "Europe", "hire_date": "2023-04-12", "quota_annual": 1600000},
    {"rep_id": "REP-105", "name": "Karan Mehta", "team": "Strategic Accounts", "region": "North America", "hire_date": "2021-11-20", "quota_annual": 2200000},
    {"rep_id": "REP-106", "name": "Elena Rostova", "team": "Enterprise East", "region": "Europe", "hire_date": "2022-08-15", "quota_annual": 2100000},
    {"rep_id": "REP-107", "name": "Marcus Vance", "team": "Strategic Accounts", "region": "Europe", "hire_date": "2022-02-01", "quota_annual": 2000000},
    {"rep_id": "REP-108", "name": "Sophia Chen", "team": "Inbound Growth", "region": "Asia Pacific", "hire_date": "2023-03-15", "quota_annual": 1500000},
    {"rep_id": "REP-109", "name": "Carlos Mendez", "team": "Mid-Market Global", "region": "Latin America", "hire_date": "2023-05-20", "quota_annual": 1400000},
    {"rep_id": "REP-110", "name": "Aisha Al-Mansoor", "team": "Strategic Accounts", "region": "Middle East & Africa", "hire_date": "2023-07-01", "quota_annual": 1600000},
    {"rep_id": "REP-111", "name": "David Miller", "team": "Enterprise West", "region": "North America", "hire_date": "2022-10-01", "quota_annual": 1900000},
    {"rep_id": "REP-112", "name": "Lisa Wang", "team": "Inbound Growth", "region": "Asia Pacific", "hire_date": "2023-09-01", "quota_annual": 1300000}
]

LEAD_SOURCES = ["Website", "Inbound Demo", "Referral", "Cold Outreach", "LinkedIn", "Webinar", "Partner Event"]

START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 5, 31)

def random_date(start, end):
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)

# -------------------------------------------------------------
# 1. Generate Sales Representatives
# -------------------------------------------------------------
def generate_sales_reps():
    reps_df = pd.DataFrame(SALES_REPS)
    reps_df["email"] = reps_df["name"].apply(lambda n: n.lower().replace(" ", ".") + "@salessight360.io")
    return reps_df

# -------------------------------------------------------------
# 2. Generate Customers
# -------------------------------------------------------------
COMPANY_PREFIXES = ["Apex", "Vertex", "Quantum", "Nexus", "Synergy", "Beacon", "Pinnacle", "Vanguard", "Omni", "Horizon", "BlueSky", "CyberCore", "Titan", "Aero", "Pulse", "Nova", "Starlight", "CoreLogic", "Elevate", "Frontier"]
COMPANY_SUFFIXES = ["Technologies", "Solutions", "Global", "Systems", "Health", "Analytics", "Networks", "Enterprises", "Logistics", "Digital", "Financial", "Retail", "Energy", "Labs"]
FIRST_NAMES = ["James", "Emma", "Liam", "Olivia", "Noah", "Ava", "William", "Sophia", "Oliver", "Isabella", "Arjun", "Ananya", "Hiroshi", "Yuki", "Mateo", "Camila", "Lars", "Freja", "Tariq", "Fatima"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Patel", "Sharma", "Tanaka", "Sato", "Silva", "Santos", "Mueller", "Schmidt", "Al-Farsi", "Hassan", "Taylor", "Anderson"]

def generate_customers(n_customers=650):
    customers = []
    region_names = list(REGIONS.keys())
    region_weights = [REGIONS[r]["weight"] for r in region_names]
    segment_names = list(CUSTOMER_SEGMENTS.keys())
    segment_weights = [CUSTOMER_SEGMENTS[s]["weight"] for s in segment_names]
    industries = ["Technology", "Healthcare", "Finance & Banking", "Manufacturing", "Retail & E-commerce", "Professional Services"]

    for i in range(1, n_customers + 1):
        cust_id = f"CUST-{1000 + i}"
        comp_name = f"{random.choice(COMPANY_PREFIXES)} {random.choice(COMPANY_SUFFIXES)}"
        contact_first = random.choice(FIRST_NAMES)
        contact_last = random.choice(LAST_NAMES)
        contact_name = f"{contact_first} {contact_last}"
        email = f"{contact_first.lower()}.{contact_last.lower()}@{comp_name.lower().replace(' ', '').replace('&', '')}.com"
        phone = f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        region = np.random.choice(region_names, p=region_weights)
        country = random.choice(REGIONS[region]["countries"])
        segment = np.random.choice(segment_names, p=segment_weights)
        industry = random.choice(industries)
        created = random_date(START_DATE, datetime(2025, 4, 30))

        customers.append({
            "customer_id": cust_id,
            "company_name": comp_name,
            "contact_name": contact_name,
            "email": email,
            "phone": phone,
            "region": region,
            "country": country,
            "customer_segment": segment,
            "industry": industry,
            "created_date": created.strftime("%Y-%m-%d")
        })
    
    df = pd.DataFrame(customers)
    # Introduce small intentional raw data artifacts (to be resolved by ETL)
    # 1. A few leading/trailing spaces in company names and regions
    df.loc[df.index[:10], "region"] = df.loc[df.index[:10], "region"].apply(lambda x: f" {x} ")
    # 2. Inconsistent casing in a few segments
    df.loc[df.index[11:16], "customer_segment"] = df.loc[df.index[11:16], "customer_segment"].str.lower()
    # 3. Missing phone numbers for ~8 rows
    df.loc[df.index[20:28], "phone"] = np.nan
    return df

# -------------------------------------------------------------
# 3. Generate Leads
# -------------------------------------------------------------
def generate_leads(customers_df, reps_df, n_leads=2400):
    leads = []
    channel_names = list(CHANNELS.keys())
    channel_weights = list(CHANNELS.values())
    rep_ids = reps_df["rep_id"].tolist()
    cust_ids = customers_df["customer_id"].tolist()

    for i in range(1, n_leads + 1):
        lead_id = f"LEAD-{5000 + i}"
        created = random_date(START_DATE, END_DATE)
        channel = np.random.choice(channel_names, p=channel_weights)
        source = random.choice(LEAD_SOURCES)
        rep = random.choice(rep_ids)
        
        # ~65% of leads link to an existing or prospective customer
        has_cust = random.random() < 0.65
        cust_id = random.choice(cust_ids) if has_cust else None
        
        # Lead status distribution
        status_roll = random.random()
        if status_roll < 0.62: # 62% converted or qualified
            status = "Converted"
            converted = 1
        elif status_roll < 0.78:
            status = "Qualified"
            converted = 0
        elif status_roll < 0.90:
            status = "Contacted"
            converted = 0
        else:
            status = "Disqualified"
            converted = 0

        leads.append({
            "lead_id": lead_id,
            "customer_id": cust_id if cust_id else "",
            "lead_source": source,
            "channel": channel,
            "rep_id": rep,
            "created_date": created.strftime("%Y-%m-%d"),
            "status": status,
            "converted_to_opp": converted
        })

    df = pd.DataFrame(leads)
    # Intentional raw data artifacts
    # Inconsistent whitespace in channel
    df.loc[df.index[5:12], "channel"] = df.loc[df.index[5:12], "channel"].apply(lambda x: f"  {x}")
    return df

# -------------------------------------------------------------
# 4. Generate Sales Opportunities (~1,600 opportunities)
# -------------------------------------------------------------
def generate_opportunities(leads_df, customers_df, reps_df):
    converted_leads = leads_df[leads_df["converted_to_opp"] == 1].to_dict("records")
    cust_lookup = customers_df.set_index("customer_id").to_dict("index")
    rep_lookup = reps_df.set_index("rep_id").to_dict("index")

    prod_names = list(PRODUCTS.keys())
    prod_weights = [PRODUCTS[p]["weight"] for p in prod_names]

    stages_open = ["Prospecting", "Qualification", "Proposal", "Negotiation"]
    stage_probs = {
        "Prospecting": 0.10,
        "Qualification": 0.25,
        "Proposal": 0.50,
        "Negotiation": 0.75,
        "Closed Won": 1.00,
        "Closed Lost": 0.00
    }

    opportunities = []
    opp_counter = 1

    # Take ~1,580 opportunities to meet target
    target_count = 1580
    
    for i in range(target_count):
        opp_id = f"OPP-{10000 + opp_counter}"
        opp_counter += 1

        if i < len(converted_leads):
            ld = converted_leads[i]
            lead_id = ld["lead_id"]
            cust_id = ld["customer_id"] if ld["customer_id"] in cust_lookup else random.choice(list(cust_lookup.keys()))
            rep_id = ld["rep_id"]
            lead_created = datetime.strptime(ld["created_date"], "%Y-%m-%d")
            opp_created = lead_created + timedelta(days=random.randint(1, 14))
            channel = ld["channel"].strip()
        else:
            lead_id = None
            cust_id = random.choice(list(cust_lookup.keys()))
            rep_id = random.choice(list(rep_lookup.keys()))
            opp_created = random_date(START_DATE, END_DATE)
            channel = np.random.choice(list(CHANNELS.keys()), p=list(CHANNELS.values()))

        cust_info = cust_lookup[cust_id]
        rep_info = rep_lookup[rep_id]
        region = cust_info["region"].strip()
        segment = cust_info["customer_segment"].strip().capitalize()
        if segment not in CUSTOMER_SEGMENTS:
            segment = "Mid-Market"

        product = np.random.choice(prod_names, p=prod_weights)
        base_val = PRODUCTS[product]["base_price"]
        multiplier = CUSTOMER_SEGMENTS[segment]["deal_multiplier"]
        jitter = random.uniform(0.85, 1.35)
        deal_amount = round(base_val * multiplier * jitter, -2)

        # Sales cycle timing
        cycle_days = random.randint(25, 90)
        expected_close = opp_created + timedelta(days=cycle_days)

        # Stage determination based on date and probability
        now_point = END_DATE
        if expected_close <= now_point - timedelta(days=15):
            # Deal is closed
            is_closed = 1
            # ~28-30% Win rate across closed deals
            win_roll = random.random()
            if win_roll < 0.29:
                stage = "Closed Won"
                is_won = 1
                actual_close = opp_created + timedelta(days=random.randint(20, cycle_days + 15))
                loss_reason = None
            else:
                stage = "Closed Lost"
                is_won = 0
                actual_close = opp_created + timedelta(days=random.randint(15, cycle_days + 10))
                loss_reason = random.choice(["Budget Constraint", "Chose Competitor", "Project Delayed", "No Decision", "Missing Feature"])
        else:
            # Deal is still open
            is_closed = 0
            is_won = 0
            actual_close = None
            loss_reason = None
            # Stage progression based on how close to expected close
            time_ratio = (now_point - opp_created).days / max(1, cycle_days)
            if time_ratio < 0.3:
                stage = "Prospecting"
            elif time_ratio < 0.6:
                stage = "Qualification"
            elif time_ratio < 0.85:
                stage = "Proposal"
            else:
                stage = "Negotiation"

        prob = stage_probs[stage]

        opportunities.append({
            "opportunity_id": opp_id,
            "opportunity_name": f"{cust_info['company_name']} - {product}",
            "customer_id": cust_id,
            "lead_id": lead_id if lead_id else "",
            "rep_id": rep_id,
            "product_name": product,
            "channel": channel,
            "region": region,
            "customer_segment": segment,
            "stage": stage,
            "probability": prob,
            "amount": deal_amount,
            "created_date": opp_created.strftime("%Y-%m-%d"),
            "expected_close_date": expected_close.strftime("%Y-%m-%d"),
            "actual_close_date": actual_close.strftime("%Y-%m-%d") if actual_close else "",
            "is_closed": is_closed,
            "is_won": is_won,
            "loss_reason": loss_reason if loss_reason else ""
        })

    df = pd.DataFrame(opportunities)

    # Intentional raw anomalies for ETL to clean:
    # 1. 5 duplicate rows
    dupes = df.iloc[10:15].copy()
    df = pd.concat([df, dupes], ignore_index=True)
    # 2. Inconsistent casing in stage for 6 rows
    df.loc[df.index[30:36], "stage"] = df.loc[df.index[30:36], "stage"].str.upper()
    # 3. 2 rows with negative or 0 amount anomaly to be caught by validation and cleaned
    df.loc[df.index[50], "amount"] = -15000.0
    df.loc[df.index[51], "amount"] = 0.0

    return df

# -------------------------------------------------------------
# 5. Generate Orders & Payments
# -------------------------------------------------------------
def generate_orders_and_payments(opportunities_df):
    won_opps = opportunities_df[opportunities_df["is_won"] == 1].copy()
    orders = []
    payments = []
    order_counter = 1
    payment_counter = 1

    for _, opp in won_opps.iterrows():
        order_id = f"ORD-{20000 + order_counter}"
        order_counter += 1
        opp_id = opp["opportunity_id"]
        cust_id = opp["customer_id"]
        close_dt = datetime.strptime(opp["actual_close_date"], "%Y-%m-%d") if opp["actual_close_date"] else datetime.strptime(opp["created_date"], "%Y-%m-%d")
        order_date = close_dt + timedelta(days=random.randint(1, 5))
        amount = float(opp["amount"])
        
        # 96% completed, 3% pending, 1% cancelled
        st_roll = random.random()
        if st_roll < 0.96:
            order_status = "Completed"
        elif st_roll < 0.99:
            order_status = "In Fulfillment"
        else:
            order_status = "Cancelled"

        billing_freq = random.choice(["Annual", "Quarterly", "Monthly"])

        orders.append({
            "order_id": order_id,
            "opportunity_id": opp_id,
            "customer_id": cust_id,
            "order_date": order_date.strftime("%Y-%m-%d"),
            "order_amount": amount,
            "order_status": order_status,
            "billing_frequency": billing_freq
        })

        # Generate Payments for completed or in-fulfillment orders
        if order_status in ["Completed", "In Fulfillment"]:
            # Single upfront payment or split installments
            if billing_freq == "Annual" or random.random() < 0.70:
                # 1 full payment
                pay_id = f"PAY-{30000 + payment_counter}"
                payment_counter += 1
                pay_dt = order_date + timedelta(days=random.randint(2, 20))
                payments.append({
                    "payment_id": pay_id,
                    "order_id": order_id,
                    "customer_id": cust_id,
                    "payment_date": pay_dt.strftime("%Y-%m-%d"),
                    "amount": amount,
                    "payment_method": random.choice(["Wire Transfer", "ACH", "Credit Card", "Corporate Cheque"]),
                    "payment_status": "Completed"
                })
            else:
                # 2 installments
                inst1 = round(amount * 0.5, 2)
                inst2 = round(amount - inst1, 2)
                p1_dt = order_date + timedelta(days=random.randint(2, 14))
                p2_dt = order_date + timedelta(days=random.randint(35, 60))

                pay_id1 = f"PAY-{30000 + payment_counter}"
                payment_counter += 1
                payments.append({
                    "payment_id": pay_id1,
                    "order_id": order_id,
                    "customer_id": cust_id,
                    "payment_date": p1_dt.strftime("%Y-%m-%d"),
                    "amount": inst1,
                    "payment_method": random.choice(["Wire Transfer", "ACH", "Credit Card"]),
                    "payment_status": "Completed"
                })

                pay_id2 = f"PAY-{30000 + payment_counter}"
                payment_counter += 1
                payments.append({
                    "payment_id": pay_id2,
                    "order_id": order_id,
                    "customer_id": cust_id,
                    "payment_date": p2_dt.strftime("%Y-%m-%d"),
                    "amount": inst2,
                    "payment_method": random.choice(["Wire Transfer", "ACH", "Credit Card"]),
                    "payment_status": "Completed" if p2_dt <= END_DATE else "Pending"
                })

    orders_df = pd.DataFrame(orders)
    payments_df = pd.DataFrame(payments)

    # Intentional raw anomaly: 3 duplicate payment rows
    p_dupes = payments_df.iloc[:3].copy()
    payments_df = pd.concat([payments_df, p_dupes], ignore_index=True)

    return orders_df, payments_df

# -------------------------------------------------------------
# 6. Generate Sales Targets
# -------------------------------------------------------------
def generate_sales_targets(reps_df):
    targets = []
    target_counter = 1
    teams = reps_df["team"].unique()
    regions = list(REGIONS.keys())

    # Targets for 2024 (12 months) and 2025 (months 1-6)
    periods = [(2024, m) for m in range(1, 13)] + [(2025, m) for m in range(1, 7)]

    for year, month in periods:
        for reg in regions:
            for team in teams:
                tid = f"TGT-{4000 + target_counter}"
                target_counter += 1
                # Base target around $250k - $400k per region-team month with seasonal lift in Q4
                seasonal_mult = 1.25 if month in [11, 12] else (1.1 if month in [6, 9] else 1.0)
                reg_weight = REGIONS[reg]["weight"] * 2.5
                target_rev = round(160000 * reg_weight * seasonal_mult * random.uniform(0.92, 1.08), -3)

                targets.append({
                    "target_id": tid,
                    "year": year,
                    "month": month,
                    "region": reg,
                    "team": team,
                    "target_revenue": target_rev
                })

    return pd.DataFrame(targets)

# -------------------------------------------------------------
# Main Execution
# -------------------------------------------------------------
def main():
    print("=" * 60)
    print(" SalesSight 360 — Synthetic Data Generator")
    print(f" Output Directory: {RAW_DIR}")
    print(f" Random Seed: {SEED}")
    print("=" * 60)

    # 1. Sales Reps
    reps_df = generate_sales_reps()
    reps_path = os.path.join(RAW_DIR, "sales_reps.csv")
    reps_df.to_csv(reps_path, index=False)
    print(f"-> Generated sales_reps.csv: {len(reps_df)} rows")

    # 2. Customers
    cust_df = generate_customers(n_customers=650)
    cust_path = os.path.join(RAW_DIR, "customers.csv")
    cust_df.to_csv(cust_path, index=False)
    print(f"-> Generated customers.csv: {len(cust_df)} rows")

    # 3. Leads
    leads_df = generate_leads(cust_df, reps_df, n_leads=2400)
    leads_path = os.path.join(RAW_DIR, "leads.csv")
    leads_df.to_csv(leads_path, index=False)
    print(f"-> Generated leads.csv: {len(leads_df)} rows")

    # 4. Sales Opportunities
    opps_df = generate_opportunities(leads_df, cust_df, reps_df)
    opps_path = os.path.join(RAW_DIR, "sales_opportunities.csv")
    opps_df.to_csv(opps_path, index=False)
    print(f"-> Generated sales_opportunities.csv: {len(opps_df)} rows")

    # 5. Orders & Payments
    orders_df, payments_df = generate_orders_and_payments(opps_df)
    orders_path = os.path.join(RAW_DIR, "orders.csv")
    orders_df.to_csv(orders_path, index=False)
    print(f"-> Generated orders.csv: {len(orders_df)} rows")

    payments_path = os.path.join(RAW_DIR, "payments.csv")
    payments_df.to_csv(payments_path, index=False)
    print(f"-> Generated payments.csv: {len(payments_df)} rows")

    # 6. Sales Targets
    targets_df = generate_sales_targets(reps_df)
    targets_path = os.path.join(RAW_DIR, "sales_targets.csv")
    targets_df.to_csv(targets_path, index=False)
    print(f"-> Generated sales_targets.csv: {len(targets_df)} rows")

    print("\n[SUCCESS] Raw synthetic datasets generated successfully.")

if __name__ == "__main__":
    main()
