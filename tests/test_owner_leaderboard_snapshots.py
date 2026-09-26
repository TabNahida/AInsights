import json
import unittest

from benchmarks.owner_leaderboard_snapshots import (
    ALE_BENCHMARK_ID,
    ALE_EXACT_CONFIG_MODEL_KEYS,
    ALE_SNAPSHOT_PATH,
    ARC_BENCHMARK_ID,
    ARC_EXACT_CONFIG_MODEL_KEYS,
    ARC_SNAPSHOT_PATH,
    TOOLATHLON_BENCHMARK_ID,
    TOOLATHLON_EXACT_CONFIG_MODEL_KEYS,
    TOOLATHLON_SNAPSHOT_PATH,
    load_ale_v1_overall_pass_rate_snapshot,
    load_arc_agi_3_standard_snapshot,
    load_toolathlon_verified_owner_snapshot,
)


class OwnerLeaderboardSnapshotTests(unittest.TestCase):
    def test_arc_standard_is_separate_from_provider_adapter(self):
        source, results = load_arc_agi_3_standard_snapshot()
        raw = json.loads(ARC_SNAPSHOT_PATH.read_text(encoding="utf-8"))
        by_id = {row["modelId"]: row for row in raw["evaluations"]}
        by_model = {row["model"]: row for row in results}

        self.assertEqual(source["snapshotRows"], 57)
        self.assertEqual(len(results), len(ARC_EXACT_CONFIG_MODEL_KEYS))
        self.assertEqual(len(results), 34)
        self.assertEqual(len(by_model), len(results))
        self.assertEqual(source["harness"], "Standard")
        self.assertEqual(source["snapshotGeneratedAt"], raw["generatedAt"])
        self.assertTrue(all("provider-adapter" not in key for key in ARC_EXACT_CONFIG_MODEL_KEYS))
        self.assertNotIn("openai-gpt-6-astra-high-provider-adapter", ARC_EXACT_CONFIG_MODEL_KEYS)
        self.assertNotIn("openai-gpt-5-4-2026-03-05-high", ARC_EXACT_CONFIG_MODEL_KEYS)
        for arc_id, model_key in ARC_EXACT_CONFIG_MODEL_KEYS.items():
            result = by_model[model_key]
            self.assertEqual(result["benchmarkId"], ARC_BENCHMARK_ID)
            self.assertEqual(result["sourceId"], source["id"])
            self.assertEqual(result["harness"], "Standard")
            self.assertEqual(result["value"], by_id[arc_id]["score"] * 100)
            self.assertIn(arc_id, result["configurationNote"])
            self.assertEqual(result["modelAliases"], [model_key])
            self.assertTrue(result["variantScoped"])
            self.assertTrue(result["modelScoreEligible"])
        self.assertAlmostEqual(by_model["GPT-6 Astra (max) [R]"]["value"], 62.71280210060628)
        self.assertAlmostEqual(by_model["GPT-6 Luna (max) [R]"]["value"], 0.10360997760319558)
        self.assertGreater(
            by_id["openai-gpt-6-astra-high-provider-adapter"]["score"] * 100,
            by_model["GPT-6 Astra (high) [R]"]["value"],
        )

    def test_ale_uses_named_full_overall_runs_not_display_maxima(self):
        source, results = load_ale_v1_overall_pass_rate_snapshot()
        raw = json.loads(ALE_SNAPSHOT_PATH.read_text(encoding="utf-8"))
        full_overall = {
            (row["model"], row["harness"], row.get("harnessVariant")): row
            for row in raw["rows"] if row["split"] == "full/overall"
        }
        by_model = {row["model"]: row for row in results}

        self.assertEqual(source["snapshotRows"], 1013)
        self.assertEqual(source["fullOverallRows"], 84)
        self.assertEqual(len(results), len(ALE_EXACT_CONFIG_MODEL_KEYS))
        self.assertEqual(len(results), 46)
        self.assertEqual(len(by_model), len(results))
        self.assertNotIn(("gpt-5-5", "codex", None), ALE_EXACT_CONFIG_MODEL_KEYS)
        self.assertNotIn(("kimi-k3", "claude_code", "thinking-max"), ALE_EXACT_CONFIG_MODEL_KEYS)
        self.assertIn(("kimi-k3", "kimi_code", "thinking-max"), ALE_EXACT_CONFIG_MODEL_KEYS)
        for key, model_key in ALE_EXACT_CONFIG_MODEL_KEYS.items():
            result = by_model[model_key]
            original = full_overall[key]
            self.assertEqual(result["benchmarkId"], ALE_BENCHMARK_ID)
            self.assertEqual(result["sourceId"], source["id"])
            self.assertEqual(result["harness"], key[1])
            self.assertEqual(result["harnessVariant"], key[2])
            self.assertEqual(result["value"], original["passRate"] * 100)
            self.assertEqual(original["splitTasks"], 152)
            self.assertIn(str(original["runs"]), result["configurationNote"])
            self.assertEqual(result["modelAliases"], [model_key])
            self.assertTrue(result["variantScoped"])
            self.assertTrue(result["modelScoreEligible"])
        self.assertAlmostEqual(by_model["GPT-6 Astra (max) [R]"]["value"], 34.21052631578947)
        self.assertAlmostEqual(by_model["GPT-5.6 Sol (xhigh) [R]"]["value"], 30.592105263157894)
        self.assertAlmostEqual(by_model["GPT-5.6 Sol (max) [R]"]["value"], 29.605263157894733)

    def test_toolathlon_verified_owner_is_distinct_from_vendor_and_legacy_scores(self):
        source, results = load_toolathlon_verified_owner_snapshot()
        raw = json.loads(TOOLATHLON_SNAPSHOT_PATH.read_text(encoding="utf-8"))
        by_owner_name = {row["Model"]: row for row in raw["rows"]}
        by_model = {row["model"]: row for row in results}

        self.assertEqual(source["snapshotRows"], 25)
        self.assertEqual(source["mappedRows"], 17)
        self.assertEqual(len(results), len(TOOLATHLON_EXACT_CONFIG_MODEL_KEYS))
        self.assertEqual(len(by_model), len(results))
        self.assertEqual(source["url"], raw["sourceUrl"])
        self.assertEqual(source["sourcePageSha256"], raw["pageSha256"])
        self.assertNotIn("Gemini Gemini 3.5 Flash (high) ✓", TOOLATHLON_EXACT_CONFIG_MODEL_KEYS)
        self.assertNotIn("Hy3 (high) ✓", TOOLATHLON_EXACT_CONFIG_MODEL_KEYS)
        for owner_name, model_key in TOOLATHLON_EXACT_CONFIG_MODEL_KEYS.items():
            original = by_owner_name[owner_name]
            result = by_model[model_key]
            self.assertEqual(result["benchmarkId"], TOOLATHLON_BENCHMARK_ID)
            self.assertEqual(result["sourceId"], source["id"])
            self.assertEqual(result["value"], float(original["Pass@1"].split(" ± ")[0]))
            self.assertEqual(result["harness"], "Default agent")
            self.assertEqual(result["modelAliases"], [model_key])
            self.assertTrue(result["variantScoped"])
            self.assertTrue(result["modelScoreEligible"])
            self.assertIn(owner_name, result["configurationNote"])
        self.assertEqual(by_model["DeepSeek V4 Pro 0813 (max) [R]"]["value"], 74.4)
        self.assertEqual(by_model["GPT-5.5 (xhigh) [R]"]["value"], 73.5)

    def test_every_model_key_is_present_at_exact_site_configuration(self):
        models = json.loads(
            (ARC_SNAPSHOT_PATH.parents[2] / "docs/data/models.json").read_text(encoding="utf-8")
        )["models"]
        site_keys = {model["modelKey"] for model in models}
        for model_key in (*ARC_EXACT_CONFIG_MODEL_KEYS.values(), *ALE_EXACT_CONFIG_MODEL_KEYS.values(),
                          *TOOLATHLON_EXACT_CONFIG_MODEL_KEYS.values()):
            self.assertIn(model_key, site_keys)
        for arc_id, model_key in ARC_EXACT_CONFIG_MODEL_KEYS.items():
            effort = "max" if arc_id.endswith("-max-effort") else arc_id.rsplit("-", 1)[-1]
            self.assertIn("Non-reasoning" if effort == "none" else f"({effort})", model_key)
        for (_, _, variant), model_key in ALE_EXACT_CONFIG_MODEL_KEYS.items():
            effort = variant.rsplit("-", 1)[-1]
            self.assertIn("Non-reasoning" if effort == "none" else f"({effort})", model_key)
        for owner_name, model_key in TOOLATHLON_EXACT_CONFIG_MODEL_KEYS.items():
            if "(" in owner_name:
                self.assertIn(owner_name.rsplit("(", 1)[-1].split(")", 1)[0], model_key)


if __name__ == "__main__":
    unittest.main()
