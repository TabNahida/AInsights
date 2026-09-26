import csv
import json
import unittest

from benchmarks.epoch_frontiermath_snapshot import (
    BENCHMARK_ID,
    EXACT_CONFIG_MODEL_KEYS,
    SNAPSHOT_PATH,
    SOURCE_ID,
    load_epoch_frontiermath_snapshot,
)


class EpochFrontierMathSnapshotTests(unittest.TestCase):
    def test_pinned_export_keeps_only_exact_configurations(self):
        source, results = load_epoch_frontiermath_snapshot()
        with SNAPSHOT_PATH.open(newline="", encoding="utf-8-sig") as stream:
            raw_rows = list(csv.DictReader(stream))
        by_version = {row["Model version"]: row for row in raw_rows}

        self.assertEqual(source["snapshotRows"], 64)
        self.assertEqual(len(results), len(EXACT_CONFIG_MODEL_KEYS))
        self.assertEqual(len(results), 40)
        self.assertEqual(len({row["model"] for row in results}), len(results))
        self.assertTrue(set(EXACT_CONFIG_MODEL_KEYS) <= set(by_version))
        self.assertNotIn("claude-fable-5-1_max", EXACT_CONFIG_MODEL_KEYS)
        self.assertNotIn("gpt-5.6-sol_promax", EXACT_CONFIG_MODEL_KEYS)
        self.assertNotIn("glm-5.3_max", EXACT_CONFIG_MODEL_KEYS)
        self.assertNotIn("grok-4.3_high", EXACT_CONFIG_MODEL_KEYS)
        for row in results:
            self.assertEqual(row["benchmarkId"], BENCHMARK_ID)
            self.assertEqual(row["sourceId"], SOURCE_ID)
            self.assertEqual(row["modelAliases"], [row["model"]])
            self.assertTrue(row["variantScoped"])
            self.assertTrue(row["modelScoreEligible"])

    def test_mapped_runs_match_current_site_release_and_effort(self):
        data = json.loads(
            (SNAPSHOT_PATH.parents[2] / "docs" / "data" / "models.json").read_text(
                encoding="utf-8"
            )
        )
        site_models = {model["modelKey"]: model for model in data["models"]}
        with SNAPSHOT_PATH.open(newline="", encoding="utf-8-sig") as stream:
            by_version = {row["Model version"]: row for row in csv.DictReader(stream)}

        for epoch_version, model_key in EXACT_CONFIG_MODEL_KEYS.items():
            self.assertIn(model_key, site_models, epoch_version)
            self.assertEqual(
                by_version[epoch_version]["Release date"],
                site_models[model_key]["releaseDate"],
                epoch_version,
            )

    def test_scores_preserve_epoch_precision_and_run_provenance(self):
        source, results = load_epoch_frontiermath_snapshot()
        by_model = {row["model"]: row for row in results}
        sol = by_model["GPT-5.6 Sol (max) [R]"]
        astra = by_model["GPT-6 Astra (max) [R]"]

        self.assertAlmostEqual(sol["value"], 82.92682926829268)
        self.assertEqual(astra["value"], 97.6)
        self.assertEqual(sol["effort"], "max")
        self.assertIn("QJ5rJMVypB4PMxPcBGftc8", sol["configurationNote"])
        self.assertIn("2026-07-09", sol["configurationNote"])
        self.assertEqual(source["benchmarkVersion"], "Tier 4 v2")
        self.assertEqual(source["scoreSelection"], "Best score (across scorers)")
        self.assertNotEqual(BENCHMARK_ID, "frontiermath-tier-4-v2")


if __name__ == "__main__":
    unittest.main()
