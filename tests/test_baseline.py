"""Unit tests for percentile baselines + correlation rules."""

import sys
import unittest

sys.path.insert(0, ".")

from solanapulse import anomaly  # noqa: E402
from solanapulse.baseline import compute_baselines, percentile_rank  # noqa: E402


class TestPercentileRank(unittest.TestCase):
    def test_rank(self):
        self.assertEqual(percentile_rank([1, 2, 3, 4], 3), 75.0)
        self.assertEqual(percentile_rank([1, 2, 3, 4], 5), 100.0)
        self.assertEqual(percentile_rank([1, 2, 3, 4], 0), 0.0)

    def test_no_history(self):
        self.assertIsNone(percentile_rank([], 5.0))


class TestBaselines(unittest.TestCase):
    def test_baselines_compute(self):
        history = [{"ts": i, "metrics": {"tps": {"avg": 1000.0 + i}}} for i in range(10)]
        cfg = {"series": [{"key": "tps_avg", "path": ["tps", "avg"],
                           "label": "Avg TPS", "higher_is_better": True}]}
        out = compute_baselines({"tps": {"avg": 1005.0}}, history, cfg)
        self.assertIn("tps_avg", out)
        b = out["tps_avg"]
        self.assertEqual(b["samples"], 10)
        self.assertAlmostEqual(b["median"], 1004.5)
        self.assertGreaterEqual(b["percentile"], 0.0)

    def test_missing_current_skipped(self):
        out = compute_baselines({"tps": {}}, [], {"series": [
            {"key": "x", "path": ["tps", "avg"], "label": "X"}]})
        self.assertEqual(out, {})


def _metrics(**over):
    base = {
        "slot_time_sec": {"avg": 0.42},
        "validators": {"delinquent_stake_pct": 0.5},
        "economics": {"sol_price_24h_change_pct": -1.0,
                      "tvl_24h_change_pct": -1.0,
                      "dex_volume_24h_change_pct": -1.0},
    }
    base.update(over)
    return base


class TestCorrelations(unittest.TestCase):
    def _cfg(self):
        return {"correlations": [
            {"name": "drawdown", "severity": "warning", "direction": "below",
             "default_threshold": -3.0, "min_count": 2,
             "message": "Coordinated drawdown",
             "metrics": [
                 {"path": ["economics", "sol_price_24h_change_pct"], "label": "SOL price"},
                 {"path": ["economics", "tvl_24h_change_pct"], "label": "TVL"},
                 {"path": ["economics", "dex_volume_24h_change_pct"], "label": "DEX"},
             ]},
        ]}

    def test_fires_when_two_breach(self):
        m = _metrics(economics={"sol_price_24h_change_pct": -5.0,
                                "tvl_24h_change_pct": -4.0,
                                "dex_volume_24h_change_pct": -1.0})
        a = anomaly.check_correlations(m, self._cfg())
        self.assertTrue(any(x["metric"] == "drawdown" for x in a))
        self.assertIn("SOL price", a[0]["message"])

    def test_does_not_fire_below_min_count(self):
        m = _metrics(economics={"sol_price_24h_change_pct": -5.0,
                                "tvl_24h_change_pct": -1.0,
                                "dex_volume_24h_change_pct": -1.0})
        self.assertEqual(anomaly.check_correlations(m, self._cfg()), [])

    def test_run_includes_correlations(self):
        m = _metrics(economics={"sol_price_24h_change_pct": -5.0,
                                "tvl_24h_change_pct": -4.0,
                                "dex_volume_24h_change_pct": -3.0})
        a = anomaly.run(m, [], self._cfg())
        self.assertTrue(any(x["metric"] == "drawdown" for x in a))


if __name__ == "__main__":
    unittest.main()
