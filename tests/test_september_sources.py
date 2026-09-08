"""Keep September release evidence separate by benchmark and configuration."""

import unittest

from benchmarks import collect_benchmark_scores as collector
from scripts.build_docs_site import attach_external_benchmark_scores


class SeptemberSourceTests(unittest.TestCase):
    def test_all_curated_scores_have_unique_benchmark_definitions(self):
        ids = [benchmark["id"] for benchmark in collector.BENCHMARKS]
        self.assertEqual(len(ids), len(set(ids)))
        for source in collector.OFFICIAL_SOURCE_SPECS:
            for scores in source.get("scores", {}).values():
                self.assertFalse(set(scores) - set(ids), source["id"])

    def test_fable_source_keeps_exact_max_product_and_versioned_scores(self):
        source = next(s for s in collector.OFFICIAL_SOURCE_SPECS
                      if s["id"] == "anthropic-claude-fable-5-1-system-card")
        rows = collector.official_seed_results_for_source(source)
        by_benchmark = {r["benchmarkId"]: r for r in rows}
        self.assertEqual(by_benchmark["terminal-bench-4"]["value"], 55.8)
        self.assertEqual(by_benchmark["osworld-2-aug2026-anthropic-partial"]["value"], 77.9)
        self.assertEqual(by_benchmark["osworld-2-aug2026-anthropic-strict"]["value"], 41.7)
        self.assertNotIn("osworld-2", by_benchmark)
        self.assertNotIn("terminal-bench-2-1", by_benchmark)
        for row in rows:
            self.assertEqual(row["effort"], "max")
            self.assertTrue(row["variantScoped"])
            self.assertTrue(row["fallbackConfigured"])
            self.assertFalse(row["pureModelEligible"])
            self.assertNotIn("claude-fable-5-1-high", row["modelAliases"])
            self.assertNotIn("Claude Mythos 5.1", row["modelAliases"])

    def test_google_mixed_effort_evidence_does_not_leak_to_ranked_variants(self):
        source = next(s for s in collector.OFFICIAL_SOURCE_SPECS
                      if s["id"] == "google-gemini-3-8-flash-card")
        rows = collector.official_seed_results_for_source(source)
        eligible = [r for r in rows if r.get("modelScoreEligible")]
        self.assertEqual([r["benchmarkId"] for r in eligible], ["deepswe-v1-1"])
        self.assertEqual(eligible[0]["effort"], "high")
        by_benchmark = {r["benchmarkId"]: r for r in rows}
        self.assertEqual(by_benchmark["hle-verified-1811"]["value"], 54.9)
        self.assertNotIn("hle", by_benchmark)
        self.assertEqual(by_benchmark["lvbench-agentic"]["value"], 87.8)
        self.assertEqual(by_benchmark["lvbench-static"]["value"], 87.1)
        models = [
            {"name": f"Gemini 3.8 Flash ({effort})", "slug": slug,
             "modelKey": f"Gemini 3.8 Flash ({effort})", "scores": {},
             "externalBenchmarks": []}
            for effort, slug in [("high", "gemini-3-8-flash"),
                                 ("low", "gemini-3-8-flash-low")]
        ]
        attach_external_benchmark_scores(models, {"results": rows, "sources": [source]})
        self.assertEqual(models[0]["scores"], {"benchmark:deepswe-v1-1": 73.7})
        self.assertEqual(models[1]["scores"], {})


if __name__ == "__main__":
    unittest.main()
