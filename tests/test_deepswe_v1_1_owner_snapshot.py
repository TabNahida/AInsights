import copy
import json
import statistics
import unittest

from analysis.irt_leaderboard_exploration import aindex_mixed_core
from benchmarks.deepswe_v1_1_owner_snapshot import (
    BENCHMARK_ID,
    EXACT_CONFIG_MODEL_KEYS,
    SNAPSHOT_PATH,
    _selected_rows,
    load_deepswe_v1_1_owner_snapshot,
)


class DeepSWEV11OwnerSnapshotTests(unittest.TestCase):
    def test_owner_pass_at_1_uses_one_common_harness_and_task_set(self):
        source, results = load_deepswe_v1_1_owner_snapshot()
        raw = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        by_model = {row["model"]: row for row in results}
        selected = _selected_rows(raw)

        self.assertEqual(source["snapshotRows"], 70)
        self.assertEqual(source["protocolRows"], 69)
        self.assertEqual(source["mappedRows"], 51)
        self.assertEqual(source["taskCount"], 113)
        self.assertEqual(source["repeats"], 4)
        self.assertEqual(source["harness"], "mini-swe-agent")
        self.assertEqual(len(by_model), len(results))
        self.assertEqual(set(by_model), set(EXACT_CONFIG_MODEL_KEYS.values()))
        self.assertNotIn("DeepSeek V4 Pro (max) [R]", by_model)  # ambiguous release
        self.assertNotIn("Qwen3.8 Max (0902) [R]", by_model)  # ambiguous release
        self.assertNotIn("Claude Opus 4.8 (max) [R]", by_model)  # only 111 tasks

        for identity, site_key in EXACT_CONFIG_MODEL_KEYS.items():
            owner_row = selected[identity]
            result = by_model[site_key]
            self.assertEqual(result["benchmarkId"], BENCHMARK_ID)
            self.assertEqual(result["sourceId"], source["id"])
            self.assertEqual(result["modelAliases"], [site_key])
            self.assertAlmostEqual(result["value"], owner_row["pass_at_1"] * 100)
            self.assertTrue(result["variantScoped"])
            self.assertTrue(result["modelScoreEligible"])
            self.assertTrue(result["systemScore"])
            self.assertEqual(result["agentHarness"], "mini-swe-agent")
            self.assertIn(f"{owner_row['n_passed']}/{owner_row['n_attempted']}",
                          result["configurationNote"])

        self.assertAlmostEqual(by_model["GPT-6 Astra (max) [R]"]["value"],
                               73.23008849557522)
        self.assertAlmostEqual(by_model["Kimi K2.7 Code [R]"]["value"],
                               30.530973451327434)
        self.assertAlmostEqual(statistics.median(row["value"] for row in results),
                               61.06194690265486)

    def test_mapped_rows_are_exact_site_configurations_and_scored_reps_are_core_complete(self):
        site = json.loads(
            (SNAPSHOT_PATH.parents[2] / "docs/data/models.json").read_text(encoding="utf-8")
        )
        representatives, _ = aindex_mixed_core.prepare(
            aindex_mixed_core.representatives(site["models"])
        )
        by_key = {row["modelKey"]: row for row in representatives}
        all_site_keys = {row["modelKey"] for row in site["models"]}
        creators = set()
        for site_key in EXACT_CONFIG_MODEL_KEYS.values():
            self.assertIn(site_key, all_site_keys)
            if site_key not in by_key:
                continue
            model = by_key[site_key]
            creators.add(model["creator"])
            for core_key in aindex_mixed_core.CORE_ITEMS["coding"]:
                self.assertIsNotNone(aindex_mixed_core.score_value(model, core_key))
        self.assertEqual(len(set(EXACT_CONFIG_MODEL_KEYS.values()) & by_key.keys()), 17)
        self.assertEqual(len(creators), 7)

    def test_task_set_and_duplicate_identity_fail_closed(self):
        raw = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        changed = copy.deepcopy(raw)
        changed["n_tasks_in_set"] = 112
        with self.assertRaisesRegex(ValueError, "task count changed"):
            _selected_rows(changed)

        duplicated = copy.deepcopy(raw)
        selected = _selected_rows(duplicated)
        duplicated["rows"].append(copy.deepcopy(selected[("gpt-6-astra", "max")]))
        with self.assertRaisesRegex(ValueError, "Duplicate DeepSWE"):
            _selected_rows(duplicated)


if __name__ == "__main__":
    unittest.main()
