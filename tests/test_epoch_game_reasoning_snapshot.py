import json
import statistics
import unittest

from analysis.irt_leaderboard_exploration import aindex_mixed_core
from benchmarks.epoch_game_reasoning_snapshot import (
    EBR_CARD_BAN_RUNS,
    GAME_EXACT_MODEL_KEYS,
    SNAPSHOT_PATH,
    SPECS,
    _score,
    load_epoch_ebr_card_ban_snapshot,
    load_epoch_game_reasoning_snapshots,
)


class EpochGameReasoningSnapshotTests(unittest.TestCase):
    def test_pinned_task_versions_and_exact_run_scores(self):
        snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        pairs = load_epoch_game_reasoning_snapshots()
        self.assertEqual(len(pairs), 2)
        for spec, (source, results) in zip(SPECS, pairs, strict=True):
            task_rows = [row for row in snapshot["rows"]
                         if row["task"] == spec["task"] and row["task version"] == spec["version"]]
            by_run = {row["id_runs"]: row for row in task_rows}
            self.assertEqual(source["snapshotRows"], spec["rows"])
            self.assertEqual(len(results), spec["mapped"])
            self.assertEqual(len({row["model"] for row in results}), len(results))
            for result in results:
                run_id = result["configurationNote"].split("run ", 1)[1].split(";", 1)[0]
                self.assertAlmostEqual(result["value"], _score(by_run[run_id]))
                self.assertEqual(result["benchmarkId"], spec["id"])
                self.assertEqual(result["sourceId"], source["id"])
                self.assertTrue(result["variantScoped"])
                self.assertTrue(result["modelScoreEligible"])

    def test_default_representative_fit_remains_diverse_and_difficult(self):
        site = json.loads(
            (SNAPSHOT_PATH.parents[2] / "docs/data/models.json").read_text(encoding="utf-8")
        )
        representatives, _ = aindex_mixed_core.prepare(
            aindex_mixed_core.representatives(aindex_mixed_core.source_models(site))
        )
        by_key = {model["modelKey"]: model for model in representatives}
        for _, results in load_epoch_game_reasoning_snapshots():
            fitted = [result for result in results if result["model"] in by_key
                      and all(aindex_mixed_core.score_value(by_key[result["model"]], key)
                              is not None for key in aindex_mixed_core.CORE_ITEMS["hard-reasoning"])]
            self.assertGreaterEqual(len(fitted), 3)
            self.assertGreaterEqual(
                len({by_key[result["model"]]["creator"] for result in fitted}), 3,
            )
            self.assertLess(statistics.median(result["value"] for result in fitted), 50)

    def test_game_mapping_uses_existing_exact_site_configurations(self):
        site = json.loads(
            (SNAPSHOT_PATH.parents[2] / "docs/data/models.json").read_text(encoding="utf-8")
        )
        keys = {row["modelKey"] for row in site["models"]}
        self.assertTrue(set(GAME_EXACT_MODEL_KEYS.values()) <= keys)
        self.assertEqual(
            GAME_EXACT_MODEL_KEYS["gpt-5.6-sol_none"],
            "GPT-5.6 Sol (Non-reasoning)",
        )
        self.assertEqual(
            GAME_EXACT_MODEL_KEYS["qwen3-30b-a3b-instruct-2507"],
            "Qwen3 30B A3B 2507 (Non-reasoning)",
        )
        for ambiguous in (
            "claude-fable-5-1_max", "qwen3.8-max_xhigh", "grok-4.3_high",
            "gpt-5.6-sol_promax", "gemini-3.6-flash_high",
        ):
            self.assertNotIn(ambiguous, GAME_EXACT_MODEL_KEYS)

    def test_ebr_uses_only_page_confirmed_card_ban_runs(self):
        snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        by_run = {row["id_runs"]: row for row in snapshot["rows"]
                  if row["task"] == "EBR-bench"}
        source, results = load_epoch_ebr_card_ban_snapshot()
        self.assertEqual(source["snapshotRows"], 23)
        self.assertEqual(source["mappedRows"], 4)
        self.assertEqual(len(results), 4)
        self.assertEqual({row["configurationNote"].split("run ", 1)[1].split(";", 1)[0]
                          for row in results}, set(EBR_CARD_BAN_RUNS))
        for result in results:
            run_id = result["configurationNote"].split("run ", 1)[1].split(";", 1)[0]
            self.assertAlmostEqual(result["value"], _score(by_run[run_id]))
            self.assertEqual(result["effort"], "max")

        site = json.loads(
            (SNAPSHOT_PATH.parents[2] / "docs/data/models.json").read_text(encoding="utf-8")
        )
        representatives, _ = aindex_mixed_core.prepare(
            aindex_mixed_core.representatives(aindex_mixed_core.source_models(site))
        )
        by_key = {model["modelKey"]: model for model in representatives}
        self.assertEqual(len({by_key[result["model"]]["creator"] for result in results}), 2)
        for result in results:
            model = by_key[result["model"]]
            self.assertIsNotNone(aindex_mixed_core.score_value(model, "CritPt"))


if __name__ == "__main__":
    unittest.main()
