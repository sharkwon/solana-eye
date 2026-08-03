"""Unit tests for anomaly detection. Run: python3 -m unittest discover tests"""

import sys
import unittest

sys.path.insert(0, ".")

from solanapulse import anomaly  # noqa: E402


def _metrics(**over):
    base = {
        "tps": {"avg": 1000.0},
        "slot_time_sec": {"avg": 0.42},
        "validators": {"active_count": 700, "delinquent_count": 0,
                       "delinquent_stake_pct": 0.0},
        "economics": {"tvl_24h_change_pct": -1.0,
                      "sol_price_24h_change_pct": -1.0,
                      "dex_volume_24h_change_pct": 1.0},
        "status_page": {"indicator": "none", "description": "ok"},
    }
    base.update(over)
    return base


class TestZScore(unittest.TestCase):
    def test_basic_z(self):
        z = anomaly.zscore([2.0, 4.0, 6.0, 8.0], 5.0)  # x == mean -> z == 0
        self.assertIsNotNone(z)
        self.assertAlmostEqual(float(z), 0.0, places=6)

    def test_flat_series_deviating_is_anomalous(self):
        z = anomaly.zscore([5.0, 5.0, 5.0], 8.0)
        self.assertIsNotNone(z)
        self.assertGreater(float(z), 10.0)

    def test_too_short_history(self):
        self.assertIsNone(anomaly.zscore([1.0], 2.0))


class TestThresholds(unittest.TestCase):
    def test_slot_time_too_high(self):
        a = anomaly.check_thresholds(_metrics(slot_time_sec={"avg": 0.8}), {"slot_time_sec_max": 0.6})
        self.assertTrue(any(x["metric"] == "slot_time" for x in a))

    def test_high_delinquency(self):
        a = anomaly.check_thresholds(_metrics(validators={"delinquent_stake_pct": 9.0}),
                                     {"delinquent_stake_pct_max": 5.0})
        self.assertTrue(any(x["metric"] == "delinquent_stake" for x in a))

    def test_tvl_crash(self):
        a = anomaly.check_thresholds(_metrics(economics={"tvl_24h_change_pct": -12.0}),
                                     {"tvl_drop_pct": 5.0})
        self.assertTrue(any(x["metric"] == "tvl_24h_change_pct" and x["severity"] == "warning" for x in a))

    def test_status_page_incident(self):
        a = anomaly.check_thresholds(_metrics(status_page={"indicator": "major",
                                                           "description": "outage"}),
                                     {})
        self.assertTrue(any(x["metric"] == "network_status" for x in a))

    def test_clean_metrics_no_anomaly(self):
        self.assertEqual(anomaly.check_thresholds(_metrics(), {}), [])


class TestZscoreChecks(unittest.TestCase):
    def _history(self, series):
        return [{"metrics": {"tps": {"avg": v}}} for v in series]

    def test_flag_high_spike(self):
        hist = self._history([1000.0] * 9 + [2000.0])
        a = anomaly.check_zscore(_metrics(tps={"avg": 2000.0}), hist,
                                 {"zscore_threshold": 3.0, "min_history": 5})
        self.assertTrue(any(x["metric"] == "tps" for x in a))

    def test_steady_state_no_flag(self):
        hist = self._history([1000.0] * 10)
        a = anomaly.check_zscore(_metrics(tps={"avg": 1000.0}), hist,
                                 {"zscore_threshold": 3.0, "min_history": 5})
        self.assertEqual(a, [])

    def test_insufficient_history(self):
        a = anomaly.check_zscore(_metrics(), self._history([1.0, 2.0]),
                                 {"zscore_threshold": 3.0, "min_history": 5})
        self.assertEqual(a, [])


if __name__ == "__main__":
    unittest.main()
