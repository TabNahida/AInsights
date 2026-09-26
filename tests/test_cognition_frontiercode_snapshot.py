import json
import unittest
from pathlib import Path

from benchmarks.cognition_frontiercode_snapshot import (
    BENCHMARK_ID,
    SOURCE_URL,
    load_cognition_frontiercode_snapshot,
)


class CognitionFrontierCodeSnapshotTests(unittest.TestCase):
    def test_pinned_owner_scores_match_exact_site_configurations(self):
        source, results = load_cognition_frontiercode_snapshot()
        site = json.loads((Path(__file__).resolve().parents[1] / "docs/data/models.json").read_text(encoding="utf-8"))
        site_keys = {model["modelKey"] for model in site["models"]}

        self.assertEqual(source["url"], SOURCE_URL)
        self.assertEqual(source["snapshotRows"], 61)
        self.assertEqual(len(results), 61)
        self.assertTrue({result["model"] for result in results} <= site_keys)
        self.assertEqual(len({result["model"] for result in results}), len(results))
        self.assertEqual({result["benchmarkId"] for result in results}, {BENCHMARK_ID})
        self.assertEqual(
            {result["agentHarness"] for result in results},
            {"claude-code", "codex", "grok-build", "chisel"},
        )
        self.assertTrue(all(result["variantScoped"] and result["configurationConfidence"] == "explicit" for result in results))
        self.assertFalse(any("fallback" in result["model"].lower() for result in results))

    def test_score_column_and_effort_are_distinct_from_pass_rate_and_best_mode(self):
        _, results = load_cognition_frontiercode_snapshot()
        by_model = {result["model"]: result for result in results}

        self.assertEqual(by_model["GPT-6 Astra (max) [R]"]["value"], 53.3)
        self.assertEqual(by_model["GPT-6 Astra (high) [R]"]["value"], 50.9)
        self.assertEqual(by_model["GPT-6 Sol (xhigh) [R]"]["value"], 48.4)
        self.assertEqual(by_model["Claude Opus 5 (medium) [R]"]["value"], 53.4)
        self.assertEqual(by_model["Grok 4.6 (medium) [R]"]["agentHarness"], "grok-build")
        self.assertIn("codex agent harness", by_model["GPT-6 Sol (xhigh) [R]"]["configurationNote"])


if __name__ == "__main__":
    unittest.main()
