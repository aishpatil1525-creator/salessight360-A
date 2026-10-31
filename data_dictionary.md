# SalesSight 360 — Dimensional Data Dictionary

## 1. Dimension Tables

### `dim_customers`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `customer_id` | VARCHAR(20) | PRIMARY KEY | Unique identifier for customer account |
| `company_name` | VARCHAR(100) | NOT NULL | Registered enterprise business name |
| `contact_name` | VARCHAR(100) | | Primary decision maker / procurement lead |
| `email` | VARCHAR(100) | | Contact email address |
| `phone` | VARCHAR(30) | | Business phone number |
| `region` | VARCHAR(50) | NOT NULL | Geographic sales territory |
| `country` | VARCHAR(50) | NOT NULL | Country of operation |
| `customer_segment` | VARCHAR(30) | NOT NULL | Enterprise, Mid-Market, SMB |
| `industry` | VARCHAR(50) | | Sector (Tech, Finance, Retail, Healthcare) |
| `created_date` | DATE | NOT NULL | Customer account registration date |

### `dim_sales_reps`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `rep_id` | VARCHAR(20) | PRIMARY KEY | Unique sales representative ID |
| `name` | VARCHAR(100) | NOT NULL | Full name of sales rep |
| `email` | VARCHAR(100) | | Corporate email address |
| `team` | VARCHAR(50) | NOT NULL | Assigned team (Enterprise, Inbound, Outbound) |
| `region` | VARCHAR(50) | NOT NULL | Assigned sales territory |
| `hire_date` | DATE | NOT NULL | Start date of employment |
| `quota_annual` | DECIMAL(12,2) | NOT NULL | Annual booked revenue target ($) |

### `dim_products`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `product_id` | VARCHAR(20) | PRIMARY KEY | Product SKU identifier |
| `product_name` | VARCHAR(100) | NOT NULL | SaaS product tier name |
| `category` | VARCHAR(50) | NOT NULL | Tier level (Platform, Add-on, Enterprise) |
| `base_price` | DECIMAL(10,2) | NOT NULL | Standard baseline list price ($) |

### `dim_channels`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `channel_id` | VARCHAR(20) | PRIMARY KEY | Acquisition channel identifier |
| `channel_name` | VARCHAR(50) | NOT NULL | Direct, Inbound, Outbound, Partner |
| `channel_type` | VARCHAR(50) | NOT NULL | Marketing, Field Sales, Partner Network |

### `dim_regions`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `region_id` | VARCHAR(20) | PRIMARY KEY | Territory code |
| `region_name` | VARCHAR(50) | NOT NULL | North America, EMEA, APAC, LATAM |
| `territory_code`| VARCHAR(10) | NOT NULL | NA, EU, AP, LA |

### `dim_dates`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `date_id` | INTEGER | PRIMARY KEY | Surrogate date key (YYYYMMDD) |
| `full_date` | DATE | NOT NULL | Calendar date |
| `year` | INTEGER | NOT NULL | Calendar year (e.g. 2025) |
| `quarter` | VARCHAR(10) | NOT NULL | Quarter string (Q1, Q2, Q3, Q4) |
| `month` | INTEGER | NOT NULL | Month integer (1-12) |
| `month_name` | VARCHAR(10) | NOT NULL | Month string (January, etc) |
| `year_month` | VARCHAR(7) | NOT NULL | YYYY-MM format |
| `day_of_week` | VARCHAR(15) | NOT NULL | Monday, Tuesday, etc |
| `is_weekend` | INTEGER | NOT NULL | 1 if weekend, 0 otherwise |

---

## 2. Fact Tables

### `fact_leads`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `lead_id` | VARCHAR(20) | PRIMARY KEY | Unique inbound/outbound lead ID |
| `customer_id` | VARCHAR(20) | | Associated prospect account |
| `lead_source` | VARCHAR(50) | NOT NULL | Organic, Paid Search, Event, Webinar |
| `channel` | VARCHAR(50) | NOT NULL | Acquisition channel |
| `rep_id` | VARCHAR(20) | FK -> dim_sales_reps | Assigned qualifying representative |
| `created_date` | DATE | NOT NULL | Lead capture date |
| `status` | VARCHAR(30) | NOT NULL | New, Contacted, Qualified, Disqualified |
| `converted_to_opp`| INTEGER | NOT NULL | 1 if opportunity was created, 0 otherwise |

### `fact_opportunities`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `opportunity_id`| VARCHAR(20) | PRIMARY KEY | Unique sales opportunity / deal ID |
| `opportunity_name`| VARCHAR(150) | NOT NULL | Deal title |
| `customer_id` | VARCHAR(20) | FK -> dim_customers | Customer account |
| `lead_id` | VARCHAR(20) | | Originating lead ID |
| `rep_id` | VARCHAR(20) | FK -> dim_sales_reps | Deal owner |
| `product_name` | VARCHAR(100) | NOT NULL | Primary SKU in contract |
| `channel` | VARCHAR(50) | NOT NULL | Sales channel |
| `region` | VARCHAR(50) | NOT NULL | Deal territory |
| `customer_segment`| VARCHAR(30) | NOT NULL | Segment tier |
| `stage` | VARCHAR(30) | NOT NULL | Prospecting, Qualification, Proposal, Negotiation, Closed Won, Closed Lost |
| `probability` | DECIMAL(4,2) | CHECK [0.0, 1.0] | Probability of closing |
| `amount` | DECIMAL(12,2) | CHECK > 0 | Total contract deal value ($) |
| `weighted_amount`| DECIMAL(12,2)| NOT NULL | Amount * Probability |
| `created_date` | DATE | NOT NULL | Opportunity creation date |
| `expected_close_date`| DATE | NOT NULL | Anticipated closing target |
| `actual_close_date`| DATE | | Final closing date |
| `is_closed` | INTEGER | NOT NULL | 1 if Won or Lost, 0 if Open |
| `is_won` | INTEGER | NOT NULL | 1 if Closed Won, 0 otherwise |
| `sales_cycle_days`| INTEGER | | Total days from created to close |
| `loss_reason` | VARCHAR(100) | | Competitor, Price, Budget, Feature Gap |

### `fact_orders`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `order_id` | VARCHAR(20) | PRIMARY KEY | Executed contract purchase order |
| `opportunity_id`| VARCHAR(20) | FK -> fact_opportunities | Linked closed-won deal |
| `customer_id` | VARCHAR(20) | FK -> dim_customers | Purchasing customer |
| `order_date` | DATE | NOT NULL | Order execution date |
| `order_amount` | DECIMAL(12,2) | CHECK > 0 | Billed invoice order total ($) |
| `order_status` | VARCHAR(30) | NOT NULL | Completed, Processing, Cancelled |
| `billing_frequency`| VARCHAR(30)| NOT NULL | Annual, Quarterly, Monthly |

### `fact_payments`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `payment_id` | VARCHAR(20) | PRIMARY KEY | Cash transaction remittance record |
| `order_id` | VARCHAR(20) | FK -> fact_orders | Linked invoice order |
| `payment_date`| DATE | NOT NULL | Date cash was received |
| `amount` | DECIMAL(12,2) | CHECK > 0 | Cash received amount ($) |
| `payment_status`| VARCHAR(30) | NOT NULL | Completed, Pending, Failed |
| `payment_method`| VARCHAR(50) | NOT NULL | Wire Transfer, ACH, Credit Card |

### `fact_monthly_targets`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `target_id` | VARCHAR(20) | PRIMARY KEY | Monthly target entry key |
| `rep_id` | VARCHAR(20) | FK -> dim_sales_reps | Sales representative |
| `year_month` | VARCHAR(7) | NOT NULL | Target period (YYYY-MM) |
| `monthly_target`| DECIMAL(12,2)| NOT NULL | Monthly revenue quota ($) |
