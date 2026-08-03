"""Unit tests for the metrics engine. Run: python3 -m unittest discover tests"""

import sys
import unittest

sys.path.insert(0, ".")

from solanapulse.metrics import compute_metrics  # noqa: E402


def _raw():
    return {
        "health": "ok",
        "epoch_info": {"epoch": 100, "slotIndex": 50, "slotsInEpoch": 100,
                       "transactionCount": 1_000_000},
        "slot": 500,
        "block_height": 490,
        "perf_samples": [
            {"numTransactions": 1000, "numSlots": 100, "samplePeriodSecs": 60,
             "numNonVoteTransactions": 200},
            {"numTransactions": 2000, "numSlots": 100, "samplePeriodSecs": 60,
             "numNonVoteTransactions": 400},
        ],
        "vote_accounts": {
            "current": [
                {"votePubkey": "A" * 44, "nodePubkey": "B" * 44,
                 "activatedStake": 2_000_000_000, "commission": 10, "lastVote": 500},
                {"votePubkey": "C" * 44, "nodePubkey": "D" * 44,
                 "activatedStake": 1_000_000_000, "commission": 0, "lastVote": 499},
            ],
            "delinquent": [
                {"votePubkey": "E" * 44, "nodePubkey": "F" * 44,
                 "activatedStake": 500_000_000, "commission": 5, "lastVote": 1},
            ],
        },
        "supply": {"circulating": 500_000_000_000_000_000,
                   "nonCirculating": 50_000_000_000_000_000},
        "fee_stats": {"fees_lamports": [5000, 5000, 10_000], "blocks": 2},
        "price": {"usd": 70.0, "usd_24h_change": -2.5},
        "tvl": 5_000_000_000.0,
        "tvl_history": [{"ts": 1_700_000_000, "tvl": 5_100_000_000.0}],
        "dex": {"volume24h": 1_000_000_000.0, "change_1d_pct": 3.0},
        "stablecoins": {"total_usd": 10_000_000_000.0},
        "status": {"indicator": "none", "description": "All good", "page_name": "Solana"},
        "simd": [],
        "sources_ok": {"rpc_health": True},
    }


class TestMetrics(unittest.TestCase):
    def test_tps_and_slot_time(self):
        m = compute_metrics(_raw())
        self.assertAlmostEqual(m["tps"]["avg"], 15.0)      # (1000/100 + 2000/100)/2
        self.assertAlmostEqual(m["tps"]["max"], 20.0)
        self.assertAlmostEqual(m["slot_time_sec"]["avg"], 0.6)  # 60/100

    def test_epoch_progress(self):
        m = compute_metrics(_raw())
        self.assertEqual(m["epoch"]["progress_pct"], 50.0)
        self.assertEqual(m["epoch"]["slots_remaining"], 50)

    def test_validators(self):
        m = compute_metrics(_raw())["validators"]
        self.assertEqual(m["active_count"], 2)
        self.assertEqual(m["delinquent_count"], 1)
        self.assertAlmostEqual(m["active_stake_sol"], 3.0)  # 3e9 lamports
        # delinquent 0.5e9 / total 3.5e9 = 14.29%
        self.assertAlmostEqual(m["delinquent_stake_pct"], 14.29, places=2)
        self.assertAlmostEqual(m["avg_commission_pct"], 5.0)
        self.assertEqual(m["top_by_stake"][0]["stake_sol"], 2.0)

    def test_fees(self):
        m = compute_metrics(_raw())["fees"]
        self.assertEqual(m["median_fee_lamports"], 5000)
        self.assertEqual(m["sampled_blocks"], 2)
        self.assertIsNotNone(m["rev_est_24h_sol"])
        self.assertGreater(m["rev_est_24h_sol"], 0)

    def test_economics(self):
        m = compute_metrics(_raw())["economics"]
        self.assertEqual(m["sol_price_usd"], 70.0)
        self.assertEqual(m["sol_price_24h_change_pct"], -2.5)
        self.assertEqual(m["dex_volume_24h_usd"], 1_000_000_000.0)
        self.assertEqual(m["stablecoin_supply_usd"], 10_000_000_000.0)

    def test_missing_data_degrades_to_none(self):
        m = compute_metrics({})
        self.assertIsNone(m["tps"]["avg"])
        self.assertEqual(m["validators"]["active_count"], 0)
        self.assertIsNone(m["fees"]["median_fee_lamports"])


if __name__ == "__main__":
    unittest.main()
