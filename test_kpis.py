import os
import sys
import unittest
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from python.kpi_calculations import KPICalculator

class TestKPICalculations(unittest.TestCase):

    def setUp(self):
        # Known ground-truth test dataset
        self.known_opps = pd.DataFrame([
            {"opportunity_id": "OPP-1", "stage": "Closed Won", "is_closed": 1, "amount": 100000.0, "probability": 1.0, "weighted_amount": 100000.0},
            {"opportunity_id": "OPP-2", "stage": "Closed Won", "is_closed": 1, "amount": 50000.0, "probability": 1.0, "weighted_amount": 50000.0},
            {"opportunity_id": "OPP-3", "stage": "Closed Lost", "is_closed": 1, "amount": 75000.0, "probability": 0.0, "weighted_amount": 0.0},
            {"opportunity_id": "OPP-4", "stage": "Closed Lost", "is_closed": 1, "amount": 25000.0, "probability": 0.0, "weighted_amount": 0.0},
            {"opportunity_id": "OPP-5", "stage": "Proposal", "is_closed": 0, "amount": 60000.0, "probability": 0.5, "weighted_amount": 30000.0},
            {"opportunity_id": "OPP-6", "stage": "Negotiation", "is_closed": 0, "amount": 40000.0, "probability": 0.75, "weighted_amount": 30000.0}
        ])

        self.known_leads = pd.DataFrame([
            {"lead_id": "L-1", "converted_to_opp": 1},
            {"lead_id": "L-2", "converted_to_opp": 1},
            {"lead_id": "L-3", "converted_to_opp": 0},
            {"lead_id": "L-4", "converted_to_opp": 0},
            {"lead_id": "L-5", "converted_to_opp": 0}
        ])

        self.known_targets = pd.DataFrame([
            {"target_id": "T-1", "target_revenue": 200000.0}
        ])

        self.calc = KPICalculator()

    def test_closed_won_revenue(self):
        # Expected: OPP-1 (100k) + OPP-2 (50k) = 150,000.0
        kpis = self.calc.compute_all_kpis(opps_df=self.known_opps)
        self.assertEqual(kpis["closed_won_revenue"], 150000.0)
        self.assertEqual(kpis["closed_won_count"], 2)

    def test_open_and_weighted_pipeline(self):
        # Open Deals: OPP-5 (60k) + OPP-6 (40k) = 100,000.0
        # Weighted: (60k * 0.5) + (40k * 0.75) = 30k + 30k = 60,000.0
        kpis = self.calc.compute_all_kpis(opps_df=self.known_opps)
        self.assertEqual(kpis["open_pipeline_value"], 100000.0)
        self.assertEqual(kpis["weighted_pipeline_value"], 60000.0)

    def test_win_rate(self):
        # Total closed = 4 (2 won, 2 lost). Win rate = 2 / 4 * 100 = 50.0%
        kpis = self.calc.compute_all_kpis(opps_df=self.known_opps)
        self.assertEqual(kpis["win_rate_pct"], 50.0)

    def test_average_won_deal_size(self):
        # Total won revenue = 150,000 / 2 won deals = 75,000.0
        kpis = self.calc.compute_all_kpis(opps_df=self.known_opps)
        self.assertEqual(kpis["avg_won_deal_size"], 75000.0)

    def test_lead_conversion_rate(self):
        # 2 converted out of 5 leads = 40.0%
        kpis = self.calc.compute_all_kpis(opps_df=self.known_opps, leads_df=self.known_leads)
        self.assertEqual(kpis["lead_to_opp_conversion_pct"], 40.0)

    def test_target_achievement(self):
        # Realized revenue = 150,000, Target = 200,000 -> 75.0%
        kpis = self.calc.compute_all_kpis(opps_df=self.known_opps, targets_df=self.known_targets)
        self.assertEqual(kpis["target_achievement_pct"], 75.0)
        self.assertEqual(kpis["forecast_variance"], -50000.0)

    def test_zero_division_safety(self):
        # Empty dataset should gracefully return 0.0 without throwing ZeroDivisionError
        empty_opps = pd.DataFrame(columns=["opportunity_id", "stage", "is_closed", "amount", "probability"])
        empty_leads = pd.DataFrame(columns=["lead_id", "converted_to_opp"])
        empty_targets = pd.DataFrame(columns=["target_id", "target_revenue"])
        kpis = self.calc.compute_all_kpis(opps_df=empty_opps, leads_df=empty_leads, targets_df=empty_targets)
        self.assertEqual(kpis["win_rate_pct"], 0.0)
        self.assertEqual(kpis["avg_won_deal_size"], 0.0)
        self.assertEqual(kpis["lead_to_opp_conversion_pct"], 0.0)
        self.assertEqual(kpis["target_achievement_pct"], 0.0)

if __name__ == "__main__":
    unittest.main()
