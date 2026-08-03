"""Unit tests for the composite health score. Run: python3 -m unittest discover tests"""

import sys
import unittest

sys.path.insert(0, ".")

from solanapulse.healthscore import compute_health_score, grade  # noqa: E402


def _metrics(**over):
    base = {
        "tps": {"avg": 1500.0},
        "slot_time_sec": {"avg": 0.4},
        "validators": {"delinquent_stake_pct": 0.0},
        "economics": {"tvl_24h_change_pct": 0.0, "sol_price_24h_change_pct": 0.0},
        "status_page": {"indicator": "none"},
    }
    base.update(over)
    return base


class TestHealthScore(unittest.TestCase):
    def test_perfect_conditions_score_100(self):
        # TPS at target, ideal slot time, zero delinquency, healthy +5% trends
        hs = compute_health_score(_metrics(
            economics={"tvl_24h_change_pct": 5.0, "sol_price_24h_change_pct": 5.0},
        ))
        self.assertEqual(hs["score"], 100.0)
        self.assertEqual(hs["grade"], "excellent")

    def test_neutral_trends_score_middle(self):
        # 0% trends are *neutral*, not perfect — the score reflects that
        hs = compute_health_score(_metrics())
        self.assertGreater(hs["score"], 80.0)
        self.assertLess(hs["score"], 100.0)

    def test_bad_slot_time_and_delinquency_drop_score(self):
        hs = compute_health_score(_metrics(
            slot_time_sec={"avg": 0.8},
            validators={"delinquent_stake_pct": 5.0},
        ))
        self.assertLess(hs["score"], 100.0)
        self.assertGreater(hs["score"], 0.0)

    def test_critical_status_caps_score(self):
        hs = compute_health_score(_metrics(status_page={"indicator": "critical"}))
        self.assertLess(hs["score"], 100.0)

    def test_components_are_reported(self):
        hs = compute_health_score(_metrics())
        self.assertIn("tps", hs["components"])
        self.assertIn("network_status", hs["components"])

    def test_missing_data_uses_available_components(self):
        hs = compute_health_score({})
        self.assertGreaterEqual(hs["score"], 0.0)
        self.assertLessEqual(hs["score"], 100.0)

    def test_grade_boundaries(self):
        self.assertEqual(grade(95), "excellent")
        self.assertEqual(grade(85), "good")
        self.assertEqual(grade(70), "fair")
        self.assertEqual(grade(55), "at-risk")
        self.assertEqual(grade(30), "critical")


if __name__ == "__main__":
    unittest.main()
