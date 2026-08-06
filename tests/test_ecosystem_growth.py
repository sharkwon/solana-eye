"""Unit tests for the 2026-08 ecosystem-growth additions:
Nakamoto coefficient, Dune ecosystem growth, Twitter source wiring.
Run: python3 -m unittest discover tests
"""

import sys
import unittest

sys.path.insert(0, ".")

from solanapulse.metrics import compute_metrics  # noqa: E402
from solanapulse import anomaly  # noqa: E402


def _vote_accounts(stakes):
    """Build a getVoteAccounts-shaped payload from a list of stake lamports."""
    return {
        "current": [
            {
                "votePubkey": f"V{i:042d}",
                "nodePubkey": f"N{i:042d}",
                "activatedStake": s,
                "commission": i % 10,
                "lastVote": 1000 - i,
            }
            for i, s in enumerate(stakes)
        ],
        "delinquent": [],
    }


class NakamotoTest(unittest.TestCase):
    def test_nakamoto_33pct_threshold(self):
        # 8 validators: 12,12,12,4,4,4,4,4 (SOL) -> total 56 SOL.
        # Top 2 = 24 SOL = 42.9% > 33% -> Nakamoto = 2.
        raw = {
            "health": "ok",
            "epoch_info": {"epoch": 1, "slotIndex": 0, "slotsInEpoch": 100},
            "slot": 1, "block_height": 1,
            "perf_samples": [],
            "vote_accounts": _vote_accounts(
                [s * 1_000_000_000 for s in (12, 12, 12, 4, 4, 4, 4, 4)]
            ),
            "supply": {}, "fee_stats": {"fees_lamports": [], "blocks": 0},
            "price": {}, "tvl_history": [], "tvl": None, "dex": {}, "stablecoins": {},
        }
        m = compute_metrics(raw)
        self.assertEqual(m["validators"]["nakamoto_coefficient"], 2)
        # stake shares are percentages of total active stake, descending.
        # The loop stops at the >33% boundary, so shares cover only the top N.
        shares = m["validators"]["stake_distribution_pct"]
        self.assertAlmostEqual(sum(shares), 12 / 56 * 100 * 2, places=2)
        self.assertAlmostEqual(shares[0], 12 / 56 * 100, places=2)

    def test_nakamoto_single_dominant(self):
        raw = {
            "health": "ok",
            "epoch_info": {"epoch": 1, "slotIndex": 0, "slotsInEpoch": 100},
            "slot": 1, "block_height": 1,
            "perf_samples": [],
            "vote_accounts": _vote_accounts([80 * 1_000_000_000, 10 * 1_000_000_000,
                                             10 * 1_000_000_000]),
            "supply": {}, "fee_stats": {"fees_lamports": [], "blocks": 0},
            "price": {}, "tvl_history": [], "tvl": None, "dex": {}, "stablecoins": {},
        }
        m = compute_metrics(raw)
        self.assertEqual(m["validators"]["nakamoto_coefficient"], 1)

    def test_ecosystem_growth_wiring(self):
        raw = {
            "health": "ok",
            "epoch_info": {"epoch": 1, "slotIndex": 0, "slotsInEpoch": 100},
            "slot": 1, "block_height": 1,
            "perf_samples": [],
            "vote_accounts": _vote_accounts([1_000_000_000, 1_000_000_000]),
            "supply": {}, "fee_stats": {"fees_lamports": [], "blocks": 0},
            "price": {}, "tvl_history": [], "tvl": None, "dex": {}, "stablecoins": {},
            "dune": {
                "dau": {"available": True, "value": 1_234_567, "raw": [{}]},
                "tokenized": {"available": True, "volume_usd": 5_000_000.0,
                              "aum_usd": 50_000_000.0, "holders": 12_345,
                              "raw": [{}]},
            },
            "twitter": {"tweets": [{"handle": "solana", "text": "hi", "id": "1"}],
                        "degraded": []},
        }
        m = compute_metrics(raw)
        eg = m["ecosystem_growth"]
        self.assertTrue(eg["daily_active_addresses"]["available"])
        self.assertEqual(eg["daily_active_addresses"]["value"], 1_234_567)
        self.assertEqual(eg["tokenized_equities"]["volume_usd"], 5_000_000.0)
        self.assertEqual(eg["tokenized_equities"]["holders"], 12_345)
        self.assertEqual(m["twitter"]["tweets"][0]["handle"], "solana")


class EcosystemAnomalyTest(unittest.TestCase):
    def _metrics(self, **over):
        base = {
            "tps": {"avg": 1000.0},
            "slot_time_sec": {"avg": 0.42},
            "validators": {"active_count": 700, "delinquent_count": 0,
                           "delinquent_stake_pct": 0.0,
                           "nakamoto_coefficient": 18},
            "economics": {"tvl_24h_change_pct": -1.0,
                          "sol_price_24h_change_pct": -1.0,
                          "dex_volume_24h_change_pct": 1.0},
            "status_page": {"indicator": "none", "description": "ok"},
            "ecosystem_growth": {
                "daily_active_addresses": {"available": True, "value": 1_000_000,
                                           "source": "dune"},
                "tokenized_equities": {"available": True, "volume_usd": 5_000_000.0,
                                       "aum_usd": 50_000_000.0, "holders": 100,
                                       "source": "dune (xStocks)"},
            },
        }
        base.update(over)
        return base

    def test_low_dau_flags(self):
        cfg = {"dau_drop_pct": 15.0, "tokenized_equities_volume_change_pct": 20.0,
               "nakamoto_min": 5}
        m = self._metrics()
        m["ecosystem_growth"]["daily_active_addresses"]["value"] = 50_000  # < 150k
        anoms = anomaly.check_thresholds(m, cfg)
        names = [a["metric"] for a in anoms]
        self.assertIn("daily_active_addresses", names)

    def test_healthy_dau_no_flag(self):
        cfg = {"dau_drop_pct": 15.0, "tokenized_equities_volume_change_pct": 20.0,
               "nakamoto_min": 5}
        m = self._metrics()
        anoms = anomaly.check_thresholds(m, cfg)
        names = [a["metric"] for a in anoms]
        self.assertNotIn("daily_active_addresses", names)

    def test_nakamoto_concentration_flags(self):
        cfg = {"dau_drop_pct": 15.0, "tokenized_equities_volume_change_pct": 20.0,
               "nakamoto_min": 5}
        m = self._metrics()
        m["validators"]["nakamoto_coefficient"] = 2  # highly concentrated
        anoms = anomaly.check_thresholds(m, cfg)
        names = [a["metric"] for a in anoms]
        self.assertIn("nakamoto_coefficient", names)

    def test_low_tokenized_volume_flags(self):
        cfg = {"dau_drop_pct": 15.0, "tokenized_equities_volume_change_pct": 20.0,
               "nakamoto_min": 5}
        m = self._metrics()
        m["ecosystem_growth"]["tokenized_equities"]["volume_usd"] = 50_000.0
        anoms = anomaly.check_thresholds(m, cfg)
        names = [a["metric"] for a in anoms]
        self.assertIn("tokenized_equities_volume", names)


class TwitterSourceTest(unittest.TestCase):
    def test_collect_degrades_gracefully(self):
        """No bearer token + unreachable nitter/syndication -> empty, degraded."""
        import solanapulse.sources.twitter as tw

        original_n = tw._fetch_nitter
        original_s = tw._fetch_syndication
        tw._fetch_nitter = lambda handle, timeout=12: []  # noqa: E731
        tw._fetch_syndication = lambda handle, timeout=10: []  # noqa: E731
        try:
            out = tw.collect(["solana", "SolanaFndn"])
            self.assertEqual(out["tweets"], [])
            self.assertEqual(sorted(out["degraded"]), ["SolanaFndn", "solana"])
        finally:
            tw._fetch_nitter = original_n
            tw._fetch_syndication = original_s

    def test_collect_sorts_newest_first(self):
        import solanapulse.sources.twitter as tw

        original_n = tw._fetch_nitter
        original_s = tw._fetch_syndication
        tw._fetch_nitter = lambda handle, timeout=12: [  # noqa: E731
            {"handle": handle, "text": "older news post", "created_at": "2026-01-01T00:00:00Z"},
            {"handle": handle, "text": "newer news post", "created_at": "2026-08-01T00:00:00Z"},
        ]
        tw._fetch_syndication = lambda handle, timeout=10: []  # noqa: E731
        try:
            out = tw.collect(["solana"])
            self.assertEqual(out["tweets"][0]["text"], "newer news post")
            self.assertEqual(out["degraded"], [])
        finally:
            tw._fetch_nitter = original_n
            tw._fetch_syndication = original_s

    def test_nitter_fallback_to_syndication(self):
        """If nitter fails for a handle, syndication is attempted."""
        import solanapulse.sources.twitter as tw

        original_n = tw._fetch_nitter
        original_s = tw._fetch_syndication
        tw._fetch_nitter = lambda handle, timeout=12: []  # noqa: E731
        tw._fetch_syndication = lambda handle, timeout=10: [  # noqa: E731
            {"handle": handle, "text": "fallback ok", "id": "1", "created_at": None},
        ]
        try:
            out = tw.collect(["solana"])
            self.assertEqual(out["tweets"][0]["text"], "fallback ok")
            self.assertEqual(out["degraded"], [])
        finally:
            tw._fetch_nitter = original_n
            tw._fetch_syndication = original_s

    def test_nitter_parser(self):
        """Parse a realistic Nitter RSS item."""
        import solanapulse.sources.twitter as tw

        xml = ("<rss><channel><item>"
               "<title>Pinned: Hello &amp; welcome to Solana &lt;3</title>"
               "<pubDate>Tue, 04 Aug 2026 08:41:02 GMT</pubDate>"
               "<guid>123456789</guid>"
               "</item></channel></rss>")
        original = tw.http.request_raw
        tw.http.request_raw = lambda url, **kw: xml  # noqa: E731
        try:
            tweets = tw._fetch_nitter("solana")
            self.assertEqual(len(tweets), 1)
            self.assertEqual(tweets[0]["text"], "Pinned: Hello & welcome to Solana <3")
            self.assertEqual(tweets[0]["id"], "123456789")
        finally:
            tw.http.request_raw = original


if __name__ == "__main__":
    unittest.main()
