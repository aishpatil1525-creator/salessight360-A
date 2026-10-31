# SalesSight 360 — KPI Calculation Methodology & Business Formulas

## 1. Executive Revenue Distinction
A foundational design principle of SalesSight 360 is eliminating ambiguity between cash collection, contracted bookings, and pipeline potential:

1. **Recognized Revenue ($4,440,250)**:
   - Source: `fact_payments` where `payment_status = 'Completed'` (or completed `fact_orders`).
   - Represents: Realized cash received.
   - Guardrail: Never aggregates across multiple tables in the same query to prevent double-counting multi-installment billings.

2. **Closed-Won Deal Value ($4,440,250)**:
   - Source: `fact_opportunities` where `stage = 'Closed Won'` (`is_won = 1`).
   - Represents: Total contracted Annual Contract Value (ACV) signed by sales.

3. **Open Pipeline Value ($15,190,500)**:
   - Source: `fact_opportunities` where `is_closed = 0`.
   - Represents: Active deals currently under negotiation or progression.

4. **Weighted Pipeline Value ($6,334,250)**:
   $$\text{Weighted Pipeline} = \sum (\text{Opportunity Amount} \times \text{Stage Probability})$$
   - Prospecting: 10%
   - Qualification: 25%
   - Proposal: 50%
   - Negotiation: 75%
   - Closed Won: 100%
   - Closed Lost: 0%

---

## 2. Unbiased Win Rate Calculation
Standard win rate metrics often suffer from sample distortion if open opportunities are included in the denominator:

$$\text{Win Rate (\%)} = \frac{\text{Count of Closed Won Deals}}{\text{Count of Closed Won Deals} + \text{Count of Closed Lost Deals}} \times 100$$

- Excludes in-flight open deals.
- Zero-division safe: returns `0.0%` if no closed deals exist in the filtered window.

---

## 3. Rep Quota Attainment
$$\text{Quota Attainment (\%)} = \frac{\text{Closed Won Bookings}}{\text{Annual Quota Target}} \times 100$$

---

## 4. Forecasting & Variance Modeling
- **Time-Series Algorithm**: Holt-Winters Triple Exponential Smoothing and ARIMA.
- **Horizon**: 90-day rolling forward projection with 80% and 95% confidence intervals.
- **Sensitivity Scenarios**:
  - Best Case (+15% acceleration)
  - Expected Base Case
  - Worst Case (-15% deceleration)
