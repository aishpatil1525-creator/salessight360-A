-- ==============================================================================
-- SalesSight 360 — Dimensional Data Model (Star Schema)
-- Engine: SQLite / ANSI SQL Compatible
-- ==============================================================================

PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------------------------
-- 1. DIMENSION TABLES
-- ------------------------------------------------------------------------------

-- Dim Customers
CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    contact_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(30),
    region VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    customer_segment VARCHAR(30) NOT NULL,
    industry VARCHAR(50),
    created_date DATE NOT NULL
);

-- Dim Sales Reps
CREATE TABLE IF NOT EXISTS dim_sales_reps (
    rep_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    team VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    hire_date DATE NOT NULL,
    quota_annual DECIMAL(12, 2) NOT NULL
);

-- Dim Products
CREATE TABLE IF NOT EXISTS dim_products (
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    base_price DECIMAL(10, 2) NOT NULL
);

-- Dim Channels
CREATE TABLE IF NOT EXISTS dim_channels (
    channel_id VARCHAR(20) PRIMARY KEY,
    channel_name VARCHAR(50) NOT NULL,
    channel_type VARCHAR(50) NOT NULL
);

-- Dim Regions
CREATE TABLE IF NOT EXISTS dim_regions (
    region_id VARCHAR(20) PRIMARY KEY,
    region_name VARCHAR(50) NOT NULL,
    territory_code VARCHAR(10) NOT NULL
);

-- Dim Dates
CREATE TABLE IF NOT EXISTS dim_dates (
    date_id INTEGER PRIMARY KEY,
    full_date DATE NOT NULL,
    year INTEGER NOT NULL,
    quarter VARCHAR(10) NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(10) NOT NULL,
    year_month VARCHAR(7) NOT NULL,
    day_of_week VARCHAR(15) NOT NULL,
    is_weekend INTEGER NOT NULL
);

-- ------------------------------------------------------------------------------
-- 2. FACT TABLES
-- ------------------------------------------------------------------------------

-- Fact Leads
CREATE TABLE IF NOT EXISTS fact_leads (
    lead_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20),
    lead_source VARCHAR(50) NOT NULL,
    channel VARCHAR(50) NOT NULL,
    rep_id VARCHAR(20) NOT NULL,
    created_date DATE NOT NULL,
    status VARCHAR(30) NOT NULL,
    converted_to_opp INTEGER DEFAULT 0,
    FOREIGN KEY (rep_id) REFERENCES dim_sales_reps(rep_id)
);

-- Fact Opportunities
CREATE TABLE IF NOT EXISTS fact_opportunities (
    opportunity_id VARCHAR(20) PRIMARY KEY,
    opportunity_name VARCHAR(150) NOT NULL,
    customer_id VARCHAR(20) NOT NULL,
    lead_id VARCHAR(20),
    rep_id VARCHAR(20) NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    channel VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    customer_segment VARCHAR(30) NOT NULL,
    stage VARCHAR(30) NOT NULL,
    probability DECIMAL(4, 2) NOT NULL CHECK (probability >= 0.0 AND probability <= 1.0),
    amount DECIMAL(12, 2) NOT NULL CHECK (amount > 0),
    weighted_amount DECIMAL(12, 2) NOT NULL,
    created_date DATE NOT NULL,
    expected_close_date DATE NOT NULL,
    actual_close_date DATE,
    is_closed INTEGER NOT NULL DEFAULT 0,
    is_won INTEGER NOT NULL DEFAULT 0,
    sales_cycle_days INTEGER,
    loss_reason VARCHAR(100),
    FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id),
    FOREIGN KEY (rep_id) REFERENCES dim_sales_reps(rep_id)
);

-- Fact Orders
CREATE TABLE IF NOT EXISTS fact_orders (
    order_id VARCHAR(20) PRIMARY KEY,
    opportunity_id VARCHAR(20) NOT NULL,
    customer_id VARCHAR(20) NOT NULL,
    order_date DATE NOT NULL,
    order_amount DECIMAL(12, 2) NOT NULL CHECK (order_amount > 0),
    order_status VARCHAR(30) NOT NULL,
    billing_frequency VARCHAR(30) NOT NULL,
    FOREIGN KEY (opportunity_id) REFERENCES fact_opportunities(opportunity_id),
    FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id)
);

-- Fact Payments
CREATE TABLE IF NOT EXISTS fact_payments (
    payment_id VARCHAR(20) PRIMARY KEY,
    order_id VARCHAR(20) NOT NULL,
    customer_id VARCHAR(20) NOT NULL,
    payment_date DATE NOT NULL,
    amount DECIMAL(12, 2) NOT NULL CHECK (amount > 0),
    payment_method VARCHAR(50) NOT NULL,
    payment_status VARCHAR(30) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES fact_orders(order_id),
    FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id)
);

-- Fact Monthly Targets
CREATE TABLE IF NOT EXISTS fact_monthly_targets (
    target_id VARCHAR(20) PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    year_month VARCHAR(7) NOT NULL,
    region VARCHAR(50) NOT NULL,
    team VARCHAR(50) NOT NULL,
    target_revenue DECIMAL(12, 2) NOT NULL CHECK (target_revenue > 0)
);

-- ------------------------------------------------------------------------------
-- 3. ANALYTICAL PERFORMANCE INDEXES
-- ------------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_opp_customer ON fact_opportunities(customer_id);
CREATE INDEX IF NOT EXISTS idx_opp_rep ON fact_opportunities(rep_id);
CREATE INDEX IF NOT EXISTS idx_opp_stage ON fact_opportunities(stage);
CREATE INDEX IF NOT EXISTS idx_opp_created_date ON fact_opportunities(created_date);
CREATE INDEX IF NOT EXISTS idx_opp_expected_date ON fact_opportunities(expected_close_date);
CREATE INDEX IF NOT EXISTS idx_leads_rep ON fact_leads(rep_id);
CREATE INDEX IF NOT EXISTS idx_orders_opp ON fact_orders(opportunity_id);
CREATE INDEX IF NOT EXISTS idx_payments_order ON fact_payments(order_id);
CREATE INDEX IF NOT EXISTS idx_targets_ym ON fact_monthly_targets(year_month);
