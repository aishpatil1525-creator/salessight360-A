"""
SalesSight 360 — Forecasting & Business Intelligence Engine
Implements weighted pipeline forecasting, moving average baseline projections,
variance calculations against targets, and an explainable rule-based early warning system.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression

class SalesForecaster:
    def __init__(self, opps_df, targets_df, current_date="2025-05-31"):
        self.opps = opps_df.copy()
        self.targets = targets_df.copy()
        self.current_date = pd.to_datetime(current_date)

    def generate_monthly_forecast(self):
        """
        Calculates historical actuals, weighted pipeline projection,
        and statistical moving-average forecast.
        """
        # 1. Historical Actual Won Revenue by Month
        won = self.opps[self.opps["stage"] == "Closed Won"].copy()
        won["date"] = pd.to_datetime(won["actual_close_date"].fillna(won["created_date"]))
        won["year_month"] = won["date"].dt.strftime("%Y-%m")
        monthly_actual = won.groupby("year_month")["amount"].sum().reset_index(name="actual_revenue")

        # 2. Weighted Open Pipeline by Expected Close Month
        open_opps = self.opps[self.opps["is_closed"] == 0].copy()
        open_opps["exp_date"] = pd.to_datetime(open_opps["expected_close_date"])
        open_opps["year_month"] = open_opps["exp_date"].dt.strftime("%Y-%m")
        monthly_pipeline = open_opps.groupby("year_month").agg(
            unweighted_pipeline=("amount", "sum"),
            weighted_forecast=("weighted_amount", "sum")
        ).reset_index()

        # 3. Monthly Targets
        monthly_targets = self.targets.groupby("year_month")["target_revenue"].sum().reset_index()

        # Combine all months
        all_months = sorted(list(set(
            monthly_actual["year_month"].tolist() +
            monthly_pipeline["year_month"].tolist() +
            monthly_targets["year_month"].tolist()
        )))

        forecast_df = pd.DataFrame({"year_month": all_months})
        forecast_df = pd.merge(forecast_df, monthly_actual, on="year_month", how="left").fillna(0.0)
        forecast_df = pd.merge(forecast_df, monthly_pipeline, on="year_month", how="left").fillna(0.0)
        forecast_df = pd.merge(forecast_df, monthly_targets, on="year_month", how="left").fillna(0.0)

        # Baseline Linear Trend Model for Comparison
        historical_subset = forecast_df[forecast_df["actual_revenue"] > 0].copy()
        if len(historical_subset) >= 4:
            X = np.arange(len(historical_subset)).reshape(-1, 1)
            y = historical_subset["actual_revenue"].values
            model = LinearRegression().fit(X, y)
            full_X = np.arange(len(forecast_df)).reshape(-1, 1)
            forecast_df["linear_trend_forecast"] = model.predict(full_X).round(0)
        else:
            forecast_df["linear_trend_forecast"] = forecast_df["actual_revenue"]

        # Combined Projection: Realized Won + Weighted Pipeline for future/current periods
        forecast_df["total_projected"] = forecast_df["actual_revenue"] + forecast_df["weighted_forecast"]
        forecast_df["variance_vs_target"] = forecast_df["total_projected"] - forecast_df["target_revenue"]
        forecast_df["target_achievement_pct"] = np.where(
            forecast_df["target_revenue"] > 0,
            (forecast_df["total_projected"] / forecast_df["target_revenue"]) * 100.0,
            0.0
        ).round(1)

        return forecast_df

    def detect_business_alerts(self):
        """
        Rule-based early warning alerts for executive oversight.
        Explainable logic based on thresholds (no fabricated AI claims).
        """
        alerts = []

        # Alert 1: Overdue Opportunities
        open_opps = self.opps[self.opps["is_closed"] == 0].copy()
        open_opps["exp_date"] = pd.to_datetime(open_opps["expected_close_date"])
        overdue = open_opps[open_opps["exp_date"] < self.current_date]
        if len(overdue) > 0:
            overdue_val = overdue["amount"].sum()
            alerts.append({
                "type": "WARNING",
                "category": "Pipeline Health",
                "title": f"{len(overdue)} Overdue Opportunities Detected",
                "message": f"Identified ${overdue_val:,.0f} in pipeline past scheduled close date without stage resolution.",
                "action": "Trigger sales rep pipeline scrubs to update expected close dates or disqualify stalled deals."
            })

        # Alert 2: Regional Target Underperformance
        won_2025 = self.opps[(self.opps["stage"] == "Closed Won") & (pd.to_datetime(self.opps["created_date"]) >= "2025-01-01")]
        reg_actuals = won_2025.groupby("region")["amount"].sum()
        reg_targets = self.targets[self.targets["year"] == 2025].groupby("region")["target_revenue"].sum()
        
        for reg in reg_targets.index:
            act = reg_actuals.get(reg, 0.0)
            tgt = reg_targets[reg]
            pct = (act / tgt) * 100.0 if tgt > 0 else 0.0
            if pct < 85.0:
                alerts.append({
                    "type": "CRITICAL",
                    "category": "Target Attainment",
                    "title": f"Regional Underperformance: {reg} ({pct:.1f}%)",
                    "message": f"{reg} actual recognized revenue is currently ${(tgt - act):,.0f} below baseline target.",
                    "action": "Reallocate inbound digital marketing budget and enterprise sales rep incentives to underperforming territories."
                })

        # Alert 3: Stage Drop-off Analysis
        total_opps = len(self.opps)
        proposal_opps = len(self.opps[self.opps["stage"].isin(["Proposal", "Negotiation", "Closed Won"])])
        if total_opps > 0:
            qualification_drop = ((total_opps - proposal_opps) / total_opps) * 100.0
            if qualification_drop > 45.0:
                alerts.append({
                    "type": "INFO",
                    "category": "Funnel Conversion",
                    "title": f"High Drop-off at Proposal Stage ({qualification_drop:.1f}%)",
                    "message": "More than 45% of deals do not advance past technical qualification into proposal negotiation.",
                    "action": "Review solution architecture scoping and proposal delivery turnaround times."
                })

        # Alert 4: Top Channel Dominance
        channel_rev = won_2025.groupby("channel")["amount"].sum()
        if not channel_rev.empty:
            top_channel = channel_rev.idxmax()
            top_pct = (channel_rev.max() / channel_rev.sum()) * 100.0
            alerts.append({
                "type": "SUCCESS",
                "category": "Channel Performance",
                "title": f"Top Channel: {top_channel} ({top_pct:.1f}% Revenue Share)",
                "message": f"{top_channel} represents the highest converting distribution channel for current fiscal cycle.",
                "action": "Double down on high-performing channel partnership programs."
            })

        return alerts

if __name__ == "__main__":
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    opps = pd.read_csv(os.path.join(BASE_DIR, "data", "processed", "fact_opportunities.csv"))
    tgts = pd.read_csv(os.path.join(BASE_DIR, "data", "processed", "fact_monthly_targets.csv"))
    fc = SalesForecaster(opps, tgts)
    f_df = fc.generate_monthly_forecast()
    print("Forecast Preview (First 5 Months):")
    print(f_df.head())
    print("\nAlerts Generated:")
    for a in fc.detect_business_alerts():
        print(f"[{a['type']}] {a['title']} -> {a['message']}")
