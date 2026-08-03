"""Smoke tests for renderers + report assembly. Run: python3 -m unittest discover tests"""

import json
import sys
import unittest

sys.path.insert(0, ".")

from solanapulse.render.dashboard import render_dashboard  # noqa: E402
from solanapulse.render.markdown import render_markdown  # noqa: E402
from solanapulse.report import build_report  # noqa: E402

METRICS = {
    "health": "ok",
    "tps": {"avg": 1195.86, "max": 1257.8, "samples": 10},
    "non_vote_tps": {"avg": 511.04},
    "slot_time_sec": {"avg": 0.419},
    "epoch": {"number": 1011, "slot_index": 158940, "slots_in_epoch": 432000,
              "progress_pct": 36.79, "slots_remaining": 273060,
              "transaction_count": 534638464594},
    "slot": 436910941, "block_height": 414966542,
    "supply": {"circulating_sol": 581193163.0, "non_circulating_sol": 50310253.0},
    "validators": {"active_count": 690, "delinquent_count": 13,
                   "active_stake_sol": 432105135.0, "delinquent_stake_sol": 545049.0,
                   "delinquent_stake_pct": 0.13, "avg_commission_pct": 12.22,
                   "top_by_stake": [
                       {"pubkey": "CcaHc2L4" + "x" * 36, "stake_sol": 16803593.0, "commission_pct": 7}]},
    "fees": {"median_fee_lamports": 5000, "median_fee_sol": 0.000005,
             "sampled_blocks": 5, "sampled_txs": 6000,
             "rev_est_24h_sol": 3716.0, "method": "sampled block meta.fee (estimates)"},
    "economics": {"sol_price_usd": 72.85, "sol_price_24h_change_pct": -0.88,
                  "tvl_usd": 4736081164.75, "tvl_24h_change_pct": 0.68,
                  "dex_volume_24h_usd": 5071260163.66, "dex_volume_24h_change_pct": 7.87,
                  "stablecoin_supply_usd": 15723724362.73},
    "status_page": {"indicator": "none", "description": "All Systems Operational",
                    "page_name": "Solana"},
    "simd": [{"number": 525, "title": "Some SIMD", "labels": ["active"], "url": "https://github.com"}],
    "sources_ok": {"rpc_health": True, "coingecko": True, "github_simd": False},
}


class TestRenderers(unittest.TestCase):
    def setUp(self):
        self.report = build_report(METRICS, [{"metric": "tps", "severity": "info",
                                              "message": "TPS high"}],
                                   history=[], cfg={"render": {"refresh_interval_min": 60},
                                                    "rpc": {"url": "https://x"}})

    def test_markdown_has_sections(self):
        md = render_markdown(self.report)
        for section in ("Network Performance", "Validators", "Economics",
                        "Data Sources", "Anomalies Detected"):
            self.assertIn(section, md)
        self.assertIn("1,195.86", md)
        self.assertIn("$4,736,081,164.75", md)

    def test_dashboard_is_valid_html_with_embedded_json(self):
        html = render_dashboard(self.report)
        self.assertTrue(html.lstrip().startswith("<!DOCTYPE html>"))
        self.assertIn("const DATA = {", html)
        # extract embedded JSON and confirm it parses
        start = html.index("const DATA = ") + len("const DATA = ")
        end = html.index(";", start)
        data = json.loads(html[start:end])
        self.assertEqual(data["network"]["health"], "ok")
        self.assertEqual(data["validators"]["active_count"], 690)

    def test_json_report_shape(self):
        self.assertEqual(self.report["network"]["tps"]["avg"], 1195.86)
        self.assertEqual(len(self.report["anomalies"]), 1)
        self.assertIn("sources_ok", self.report)


if __name__ == "__main__":
    unittest.main()
