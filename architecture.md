# SalesSight 360 — Architecture & Data Warehouse Documentation

## 1. System Architecture Overview

SalesSight 360 is an enterprise multi-channel revenue analytics and intelligence platform built on a dimensional star-schema warehouse. The architecture spans five core stages:

```mermaid
flowchart LR
    A[Raw Datasets\ndata/raw/*.csv] --> B[ETL Engine\npython/etl_pipeline.py]
    B --> C[(SQLite Star Schema\ndata/processed/sales_sight_360.db)]
    C --> D[Data Integrity Checks\npython/validate_data.py]
    C --> E[Test Suite\ntests/run_tests.py]
    C --> F[Executive BI Dashboard\ndashboard/app.py]
    C --> G[Forecasting Engine\npython/forecasting.py]
    C --> H[Automated Reports\nreports/*.csv, *.md]
```

---

## 2. Dimensional Data Model (Star Schema)

The warehouse implements a Kimball-style dimensional model centered around business events (Leads, Opportunities, Orders, Payments, Targets) and shared dimensions (Customers, Sales Reps, Products, Channels, Regions, Dates).

```mermaid
erDiagram
    dim_customers ||--o{ fact_opportunities : "customer_id"
    dim_customers ||--o{ fact_orders : "customer_id"
    dim_sales_reps ||--o{ fact_opportunities : "rep_id"
    dim_sales_reps ||--o{ fact_leads : "rep_id"
    dim_sales_reps ||--o{ fact_monthly_targets : "rep_id"
    fact_opportunities ||--o{ fact_orders : "opportunity_id"
    fact_orders ||--o{ fact_payments : "order_id"

    dim_customers {
        string customer_id PK
        string company_name
        string region
        string customer_segment
        string industry
        date created_date
    }

    dim_sales_reps {
        string rep_id PK
        string name
        string team
        string region
        decimal quota_annual
    }

    dim_products {
        string product_id PK
        string product_name
        string category
        decimal base_price
    }

    dim_channels {
        string channel_id PK
        string channel_name
        string channel_type
    }

    fact_opportunities {
        string opportunity_id PK
        string customer_id FK
        string rep_id FK
        string product_name
        string channel
        string region
        string stage
        decimal probability
        decimal amount
        decimal weighted_amount
        date created_date
        date expected_close_date
        date actual_close_date
        int is_closed
        int is_won
    }

    fact_orders {
        string order_id PK
        string opportunity_id FK
        string customer_id FK
        date order_date
        decimal order_amount
        string order_status
        string billing_frequency
    }

    fact_payments {
        string payment_id PK
        string order_id FK
        date payment_date
        decimal amount
        string payment_status
        string payment_method
    }
```

---

## 3. Core KPI Definitions & Methodologies

1. **Total Recognized Revenue**:
   $$\text{Recognized Revenue} = \sum_{\text{status} = \text{'Completed'}} \text{Payment Amount}$$
   *Prevents double counting across multiple recurring invoices and separates cash realization from deal bookings.*

2. **Closed-Won Deal Value**:
   $$\text{Closed-Won Value} = \sum_{\text{stage} = \text{'Closed Won'}} \text{Opportunity Amount}$$

3. **Weighted Pipeline**:
   $$\text{Weighted Pipeline} = \sum (\text{Amount} \times \text{Stage Probability})$$
   - Prospecting: 10%
   - Qualification: 25%
   - Proposal: 50%
   - Negotiation: 75%
   - Closed Won: 100%
   - Closed Lost: 0%

4. **Unbiased Win Rate**:
   $$\text{Win Rate (\%)} = \frac{\text{Closed Won Deals}}{\text{Closed Won Deals} + \text{Closed Lost Deals}} \times 100$$
   *Excludes in-flight open deals from the denominator to ensure statistical accuracy.*

5. **Quota Attainment**:
   $$\text{Attainment (\%)} = \frac{\text{Closed Won Revenue}}{\text{Annual Quota}} \times 100$$

---

## 4. Forecasting Engine

- **Model**: Holt-Winters Exponential Smoothing & ARIMA with seasonal trend decomposition.
- **Horizon**: 90-day rolling forward projection with 80% and 95% confidence intervals.
- **Scenario Analysis**: Dynamic best-case (+15%), expected, and worst-case (-15%) sensitivity testing.

---

## 5. Automated Data Quality & Verification

22 distinct assertions run on every pipeline build:
- Table existence & schema completeness
- Primary key uniqueness across all 11 tables
- Foreign key referential integrity (zero orphaned records)
- Business bounds (strictly positive monetary amounts, probability $\in [0.0, 1.0]$)
- Chronological consistency ($\text{Close Date} \ge \text{Created Date}$)
- Record reconciliation between raw inputs and cleaned star-schema tables
