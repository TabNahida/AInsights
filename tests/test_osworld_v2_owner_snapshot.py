import copy
import json
import unittest

from analysis.irt_leaderboard_exploration import aindex_mixed_core
from benchmarks.osworld_v2_owner_snapshot import (
    BENCHMARK_ID,
    EXACT_CONFIG_MODEL_KEYS,
    SNAPSHOT_PATH,
    _selected_rows,
    load_osworld_v2_owner_snapshot,
)


class OSWorldV2OwnerSnapshotTests(unittest.TestCase):
    def test_only_original_full_standard_500_step_binary_scores_are_imported(self):
        source, results = load_osworld_v2_owner_snapshot()
        raw = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        by_model = {row["model"]: row for row in results}

        self.assertEqual(source["snapshotRows"], 50)
        self.assertEqual(source["protocolRows"], 7)
        self.assertEqual(source["mappedRows"], 6)
        self.assertEqual(source["taskVersion"], "v2026.06.24")
        self.assertEqual(source["taskCount"], 108)
        self.assertEqual(source["stepBudget"], 500)
        self.assertEqual(source["toolSetting"], "standard")
        self.assertEqual(len(by_model), len(results))
        self.assertEqual(set(by_model), set(EXACT_CONFIG_MODEL_KEYS.values()))
        self.assertNotIn("GPT-5.5 (xhigh) [R]", by_model)  # batch tools

        selected = _selected_rows(raw)
        for identity, site_key in EXACT_CONFIG_MODEL_KEYS.items():
            result = by_model[site_key]
            owner_row = selected[identity]
            self.assertEqual(result["benchmarkId"], BENCHMARK_ID)
            self.assertEqual(result["sourceId"], source["id"])
            self.assertEqual(result["modelAliases"], [site_key])
            self.assertEqual(result["value"], owner_row["binaryAccuracy"])
            self.assertNotEqual(result["value"], owner_row["partialScore"])
            self.assertTrue(result["variantScoped"])
            self.assertTrue(result["modelScoreEligible"])
            self.assertTrue(result["systemScore"])
            self.assertIn(identity[1], result["configurationNote"])

        self.assertEqual(by_model["Claude Opus 4.8 (max) [R]"]["value"], 18.52)
        self.assertEqual(by_model["Kimi K2.6 [R]"]["value"], 4.6)

    def test_mapped_site_models_are_exact_and_scored_reps_are_core_complete(self):
        site = json.loads(
            (SNAPSHOT_PATH.parents[2] / "docs/data/models.json").read_text(encoding="utf-8")
        )
        representatives, _ = aindex_mixed_core.prepare(
            aindex_mixed_core.representatives(site["models"])
        )
        by_key = {row["modelKey"]: row for row in representatives}
        all_site_keys = {row["modelKey"] for row in site["models"]}
        for site_key in EXACT_CONFIG_MODEL_KEYS.values():
            self.assertIn(site_key, all_site_keys)
            if site_key not in by_key:
                continue
            for core_key in aindex_mixed_core.CORE_ITEMS["agentic-tool-work"]:
                self.assertIsNotNone(aindex_mixed_core.score_value(by_key[site_key], core_key))
        self.assertEqual(len(set(EXACT_CONFIG_MODEL_KEYS.values()) & by_key.keys()), 5)

    def test_protocol_drift_and_duplicate_identity_fail_closed(self):
        raw = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        drifted = copy.deepcopy(raw)
        drifted["defaultResultReleaseVersion"] = "v2.1"
        with self.assertRaisesRegex(ValueError, "fallback changed"):
            _selected_rows(drifted)

        duplicated = copy.deepcopy(raw)
        selected = _selected_rows(duplicated)
        duplicated["results"].append(copy.deepcopy(selected[("Claude Opus 4.8", "max")]))
        with self.assertRaisesRegex(ValueError, "Duplicate OSWorld"):
            _selected_rows(duplicated)


if __name__ == "__main__":
    unittest.main()
