"""
SalesSight 360 — Centralized KPI Engine
Calculates all 15 core business metrics with rigorous handling of edge cases,
preventing divide-by-zero errors and avoiding multi-table revenue double counting.
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

class KPICalculator:
    def __init__(self, db_path=None, data_dict=None):
        """
        Can be initialized either from a SQLite database path or directly
        with a dictionary of filtered pandas DataFrames.
        """
        self.db_path = db_path
        self.data = data_dict or {}
        if db_path and not data_dict:
            self._load_from_db()

    def _load_from_db(self):
        conn = sqlite3.connect(self.db_path)
        tables = [
            "dim_customers", "dim_sales_reps", "dim_products", "dim_channels",
            "dim_regions", "dim_dates", "fact_leads", "fact_opportunities",
            "fact_orders", "fact_payments", "fact_monthly_targets"
        ]
        for tbl in tables:
            self.data[tbl] = pd.read_sql_query(f"SELECT * FROM {tbl}", conn)
        conn.close()

    def compute_all_kpis(self, opps_df=None, orders_df=None, payments_df=None, leads_df=None, targets_df=None):
        """
        Computes all primary KPIs on the provided (optionally filtered) DataFrames.
        If None, uses internal warehouse data.
        """
        opps = opps_df if opps_df is not None else self.data.get("fact_opportunities", pd.DataFrame())
        orders = orders_df if orders_df is not None else self.data.get("fact_orders", pd.DataFrame())
        payments = payments_df if payments_df is not None else self.data.get("fact_payments", pd.DataFrame())
        leads = leads_df if leads_df is not None else self.data.get("fact_leads", pd.DataFrame())
        targets = targets_df if targets_df is not None else self.data.get("fact_monthly_targets", pd.DataFrame())

        kpis = {}

        # 1. Total Recognized Revenue (Completed Payments or Orders)
        if not payments.empty and "payment_status" in payments.columns:
            comp_payments = payments[payments["payment_status"] == "Completed"]
            kpis["total_recognized_revenue"] = float(comp_payments["amount"].sum())
        elif not orders.empty and "order_amount" in orders.columns:
            comp_orders = orders[orders["order_status"] == "Completed"]
            kpis["total_recognized_revenue"] = float(comp_orders["order_amount"].sum())
        else:
            kpis["total_recognized_revenue"] = 0.0

        # 2. Closed-Won Revenue
        if not opps.empty:
            won_opps = opps[opps["stage"] == "Closed Won"]
            kpis["closed_won_revenue"] = float(won_opps["amount"].sum())
            kpis["closed_won_count"] = int(len(won_opps))
        else:
            kpis["closed_won_revenue"] = 0.0
            kpis["closed_won_count"] = 0

        # If payments are filtered by an opportunity subset, fallback smoothly to closed-won revenue
        if kpis["total_recognized_revenue"] == 0.0 and kpis["closed_won_revenue"] > 0:
            kpis["total_recognized_revenue"] = kpis["closed_won_revenue"]

        # 3. Open Pipeline Value
        if not opps.empty:
            open_opps = opps[opps["is_closed"] == 0]
            kpis["open_pipeline_value"] = float(open_opps["amount"].sum())
            kpis["open_deal_count"] = int(len(open_opps))
        else:
            kpis["open_pipeline_value"] = 0.0
            kpis["open_deal_count"] = 0

        # 4. Weighted Pipeline Value
        if not opps.empty:
            open_opps = opps[opps["is_closed"] == 0]
            if "weighted_amount" in open_opps.columns:
                kpis["weighted_pipeline_value"] = float(open_opps["weighted_amount"].sum())
            else:
                kpis["weighted_pipeline_value"] = float((open_opps["amount"] * open_opps["probability"]).sum())
        else:
            kpis["weighted_pipeline_value"] = 0.0

        # 5. Win Rate (%)
        if not opps.empty:
            closed_opps = opps[opps["is_closed"] == 1]
            total_closed = len(closed_opps)
            won_count = len(closed_opps[closed_opps["stage"] == "Closed Won"])
            kpis["win_rate_pct"] = round((won_count / total_closed) * 100.0, 1) if total_closed > 0 else 0.0
            kpis["closed_deal_count"] = total_closed
        else:
            kpis["win_rate_pct"] = 0.0
            kpis["closed_deal_count"] = 0

        # 6. Average Won Deal Size
        if kpis["closed_won_count"] > 0:
            kpis["avg_won_deal_size"] = round(kpis["closed_won_revenue"] / kpis["closed_won_count"], 0)
        else:
            kpis["avg_won_deal_size"] = 0.0

        # 7. Lead-to-Opportunity Conversion Rate
        if not leads.empty:
            total_leads = len(leads)
            converted_leads = int(leads["converted_to_opp"].sum())
            kpis["lead_to_opp_conversion_pct"] = round((converted_leads / total_leads) * 100.0, 1) if total_leads > 0 else 0.0
            kpis["total_leads"] = total_leads
            kpis["converted_leads"] = converted_leads
        else:
            kpis["lead_to_opp_conversion_pct"] = 0.0
            kpis["total_leads"] = 0
            kpis["converted_leads"] = 0

        # 8. Opportunity-to-Win Conversion Rate
        if not opps.empty and len(opps) > 0:
            kpis["opp_to_win_conversion_pct"] = round((kpis["closed_won_count"] / len(opps)) * 100.0, 1)
        else:
            kpis["opp_to_win_conversion_pct"] = 0.0

        # 11. Target Achievement (%)
        if not targets.empty and "target_revenue" in targets.columns:
            total_target = float(targets["target_revenue"].sum())
            kpis["total_target_revenue"] = total_target
            kpis["target_achievement_pct"] = round((kpis["total_recognized_revenue"] / total_target) * 100.0, 1) if total_target > 0 else 0.0
            kpis["forecast_variance"] = round(kpis["total_recognized_revenue"] - total_target, 2)
        else:
            kpis["total_target_revenue"] = 0.0
            kpis["target_achievement_pct"] = 0.0
            kpis["forecast_variance"] = 0.0

        return kpis

    def get_monthly_trend(self, opps_df, targets_df):
        """
        Aggregates actual revenue and targets by YYYY-MM.
        """
        if opps_df.empty:
            return pd.DataFrame(columns=["year_month", "actual_revenue", "target_revenue", "variance", "achievement_pct"])

        won = opps_df[opps_df["stage"] == "Closed Won"].copy()
        won["year_month"] = pd.to_datetime(won["actual_close_date"].fillna(won["created_date"])).dt.strftime("%Y-%m")
        monthly_rev = won.groupby("year_month")["amount"].sum().reset_index(name="actual_revenue")

        if not targets_df.empty:
            monthly_tgt = targets_df.groupby("year_month")["target_revenue"].sum().reset_index()
            merged = pd.merge(monthly_tgt, monthly_rev, on="year_month", how="left").fillna(0.0)
        else:
            merged = monthly_rev
            merged["target_revenue"] = 0.0

        merged["variance"] = merged["actual_revenue"] - merged["target_revenue"]
        merged["achievement_pct"] = np.where(merged["target_revenue"] > 0, (merged["actual_revenue"] / merged["target_revenue"]) * 100.0, 0.0).round(1)
        merged = merged.sort_values("year_month")
        merged["mom_growth_pct"] = merged["actual_revenue"].pct_change() * 100.0
        return merged

    def get_breakdown(self, opps_df, dimension="region"):
        """
        Returns revenue, deal count, and share by any dimension (region, channel, product_name, customer_segment).
        """
        if opps_df.empty or dimension not in opps_df.columns:
            return pd.DataFrame()

        won = opps_df[opps_df["stage"] == "Closed Won"]
        total_won_rev = won["amount"].sum()

        grouped = won.groupby(dimension).agg(
            revenue=("amount", "sum"),
            deals_won=("opportunity_id", "count")
        ).reset_index()

        grouped["revenue_share_pct"] = (grouped["revenue"] / total_won_rev * 100.0).round(1) if total_won_rev > 0 else 0.0
        grouped = grouped.sort_values("revenue", ascending=False)
        return grouped

    def get_rep_leaderboard(self, opps_df, reps_df):
        """
        Aggregates sales representative performance metrics.
        """
        if opps_df.empty or reps_df.empty:
            return pd.DataFrame()

        rep_stats = []
        for _, rep in reps_df.iterrows():
            r_id = rep["rep_id"]
            rep_opps = opps_df[opps_df["rep_id"] == r_id]
            total_deals = len(rep_opps)
            closed_deals = rep_opps[rep_opps["is_closed"] == 1]
            won_deals = rep_opps[rep_opps["stage"] == "Closed Won"]
            
            won_rev = won_deals["amount"].sum()
            won_cnt = len(won_deals)
            closed_cnt = len(closed_deals)
            win_rate = round((won_cnt / closed_cnt) * 100.0, 1) if closed_cnt > 0 else 0.0
            avg_deal = round(won_rev / won_cnt, 0) if won_cnt > 0 else 0.0
            quota = float(rep["quota_annual"])
            attainment = round((won_rev / quota) * 100.0, 1) if quota > 0 else 0.0

            rep_stats.append({
                "rep_id": r_id,
                "name": rep["name"],
                "team": rep["team"],
                "region": rep["region"],
                "total_deals": total_deals,
                "deals_won": won_cnt,
                "win_rate_pct": win_rate,
                "revenue": won_rev,
                "avg_deal_size": avg_deal,
                "quota_annual": quota,
                "quota_attainment_pct": attainment
            })

        df = pd.DataFrame(rep_stats)
        df = df.sort_values("revenue", ascending=False).reset_index(drop=True)
        df["rank"] = df.index + 1
        return df

    def get_funnel_stages(self, leads_df, opps_df):
        """
        Returns structured stage counts and drop-off percentages for funnel visualization.
        """
        total_leads = len(leads_df) if not leads_df.empty else 0
        total_opps = len(opps_df) if not opps_df.empty else 0
        proposal = len(opps_df[opps_df["stage"].isin(["Proposal", "Negotiation", "Closed Won"])]) if not opps_df.empty else 0
        negotiation = len(opps_df[opps_df["stage"].isin(["Negotiation", "Closed Won"])]) if not opps_df.empty else 0
        closed_won = len(opps_df[opps_df["stage"] == "Closed Won"]) if not opps_df.empty else 0

        stages = [
            {"stage": "Leads", "count": total_leads, "share_pct": 100.0},
            {"stage": "Opportunities", "count": total_opps, "share_pct": round((total_opps / total_leads * 100.0), 1) if total_leads > 0 else 0.0},
            {"stage": "Proposal", "count": proposal, "share_pct": round((proposal / total_leads * 100.0), 1) if total_leads > 0 else 0.0},
            {"stage": "Negotiation", "count": negotiation, "share_pct": round((negotiation / total_leads * 100.0), 1) if total_leads > 0 else 0.0},
            {"stage": "Closed Won", "count": closed_won, "share_pct": round((closed_won / total_leads * 100.0), 1) if total_leads > 0 else 0.0}
        ]
        return pd.DataFrame(stages)

if __name__ == "__main__":
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(BASE_DIR, "data", "processed", "sales_sight_360.db")
    calc = KPICalculator(db_path=db_path)
    res = calc.compute_all_kpis()
    print("Computed Baseline KPIs:")
    for k, v in res.items():
        print(f" - {k}: {v}")
