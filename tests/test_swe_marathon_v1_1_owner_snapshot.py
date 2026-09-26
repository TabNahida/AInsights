import json
import statistics
import unittest

from analysis.irt_leaderboard_exploration import aindex_mixed_core
from benchmarks.swe_marathon_v1_1_owner_snapshot import (
    EXACT_CONFIGS,
    SNAPSHOT_PATH,
    load_swe_marathon_v1_1_owner_snapshot,
)


class SWEMarathonV11OwnerSnapshotTests(unittest.TestCase):
    def test_all_tasks_and_trials_make_the_official_binary_result(self):
        source, results = load_swe_marathon_v1_1_owner_snapshot()
        snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(source["taskCount"], 20)
        self.assertEqual(source["trialsPerTask"], 8)
        self.assertEqual(len(snapshot["tasks"]), 20)
        self.assertEqual(len(results), 7)
        self.assertEqual({row["model"] for row in results},
                         {config[0] for config in EXACT_CONFIGS.values()})

        for variant, (site_key, _, expected_agent) in EXACT_CONFIGS.items():
            row = next(row for row in results if row["model"] == site_key)
            configs = [next(config for config in task["configs"]
                            if config["modelVariant"] == variant)
                       for task in snapshot["tasks"].values()]
            self.assertTrue(all(len(config["trials"]) == 8 for config in configs))
            wins = sum(trial["reward"] for config in configs for trial in config["trials"])
            self.assertEqual(row["value"], wins * 100 / 160)
            self.assertEqual(row["agentHarness"], expected_agent)
            self.assertEqual(row["effort"], "max")
            self.assertTrue(row["variantScoped"])
        glm = next(row for row in results if row["model"] == "GLM-5.3 (max) [R]")
        self.assertEqual(glm["value"], 42.5)
        self.assertIn("50 trials are labeled error", glm["configurationNote"])

    def test_selected_models_are_core_complete_default_representatives(self):
        site = json.loads(
            (SNAPSHOT_PATH.parents[2] / "docs/data/models.json").read_text(encoding="utf-8")
        )
        representatives, _ = aindex_mixed_core.prepare(
            aindex_mixed_core.representatives(aindex_mixed_core.source_models(site))
        )
        by_key = {model["modelKey"]: model for model in representatives}
        _, results = load_swe_marathon_v1_1_owner_snapshot()
        self.assertEqual(len({by_key[row["model"]]["creator"] for row in results}), 4)
        self.assertEqual(statistics.median(row["value"] for row in results), 32.5)
        for result in results:
            model = by_key[result["model"]]
            for core_key in aindex_mixed_core.CORE_ITEMS["coding"]:
                self.assertIsNotNone(aindex_mixed_core.score_value(model, core_key))


if __name__ == "__main__":
    unittest.main()
