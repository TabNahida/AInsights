import copy
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from analysis.irt_leaderboard_exploration import aindex_mixed_core as scoring
from analysis.irt_leaderboard_exploration import validate_mixed_core_production as validator


def models_fixture():
    models = []
    for index in range(12):
        scores = {key: float(25 + 4 * index + slot)
                  for slot, key in enumerate(key for keys in scoring.CORE_ITEMS.values() for key in keys)}
        # Keep some independent extensions with nonlinear variation so the
        # calibration exercises positive residuals rather than a zero-cap case.
        for board, keys in scoring.EXTENSION_ITEMS.items():
            for slot, key in enumerate(keys):
                scores[key] = float((index * 13 + slot * 11) % 90)
        models.append({"slug": f"model-{index:02}", "model": f"Model {index}", "creator": "Fixture",
                       "variantGroup": f"group-{index:02}", "variantPriority": 10, "scores": scores})
    return models


def attach_profiles(payload, result):
    by_slug = {model["slug"]: model for model in payload["models"]}
    for result_key, profile_key in (("full_rankings", "rankingProfile"),
                                     ("exact_config_full_rankings", "exactRankingProfile")):
        for row in result[result_key]:
            profile = {"method": scoring.METHOD_ID, "candidateId": scoring.CANDIDATE_ID,
                       "finalScore": float(row["score_full_precision"]), "publicationRank": row["rank"],
                       "scoreFullPrecision": row["score_full_precision"],
                       "displayScore": round(float(row["score_full_precision"]), 4),
                       "boardWeights": dict(scoring.BOARD_WEIGHTS),
                       "missingCoreCount": row["missing_core_count"],
                       "coreComplete": row["missing_core_count"] == 0, "boards": {}}
            for board, keys in scoring.CORE_ITEMS.items():
                meta = {"coreComplete": row[f"{board}_core_tests"] == len(keys), "coreEvidence": []}
                for public, internal in (("coreScore", "core_score"), ("extensionBonus", "extension_bonus"),
                                         ("score", "score_full_precision"), ("points", "points_full_precision"),
                                         ("weight", "weight"), ("coreTests", "core_tests"), ("extensionTests", "extension_tests")):
                    meta[public] = float(row[f"{board}_{internal}"])
                for slot, key in enumerate(keys, 1):
                    value = row[f"{board}_item{slot}_adjusted"]
                    meta["coreEvidence"].append({"key": key, "adjustedScore": value, "observed": value is not None,
                                              "basePoints": row[f"{board}_item{slot}_base_points"]})
                profile["boards"][board] = meta
            by_slug[row["slug"]][profile_key] = profile
    payload["leaderboard"] = {
        "defaultMethod": scoring.METHOD_ID, "candidateId": scoring.CANDIDATE_ID,
        "boardWeights": dict(scoring.BOARD_WEIGHTS), "boardOrder": list(scoring.BOARD_ORDER),
        "calibration": result["calibration"], "bonusCap": result["calibration"]["bonus_cap_per_board"],
        "coreItems": {b: list(keys) for b, keys in scoring.CORE_ITEMS.items()},
        "extensionItems": {b: list(keys) for b, keys in scoring.EXTENSION_ITEMS.items()},
        "populationSize": len(result["full_rankings"]), "exactPopulationSize": len(result["exact_config_full_rankings"]),
    }
    for key, result_key, identity in (("rows", "full_rankings", "selectedSlug"),
                                      ("exactRows", "exact_config_full_rankings", "slug")):
        payload["leaderboard"][key] = [
            {identity: row["slug"], "variantGroup": row["variant_group"], "publicationRank": row["rank"],
             "displayScore": round(float(row["score_full_precision"]), 4), "scoreFullPrecision": row["score_full_precision"]}
            for row in result[result_key]
        ]


class MixedCoreProductionTests(unittest.TestCase):
    def test_fixed_shares_do_not_renormalize_missing_or_floor_observed_zero(self):
        np.testing.assert_array_equal(scoring.fixed_share_base(np.array([[80, np.nan], [0, 60], [0, 0]])),
                                      np.array([40, 30, 0]))
        np.testing.assert_array_equal(scoring.fixed_share_base(np.array([[80], [0]])), np.array([80, 0]))

    def test_registry_has_exact_scheme_and_no_core_family_extensions(self):
        self.assertEqual(list(scoring.BOARD_WEIGHTS.values()), [12, 9, 22, 37, 20])
        self.assertEqual(sum(map(len, scoring.CORE_ITEMS.values())), 8)
        self.assertEqual(sum(len(keys) == 1 for keys in scoring.CORE_ITEMS.values()), 2)
        core_families = {scoring.canonical_family(k) for keys in scoring.CORE_ITEMS.values() for k in keys}
        self.assertEqual(len(core_families), 8)
        for keys in scoring.EXTENSION_ITEMS.values():
            self.assertFalse({scoring.canonical_family(k) for k in keys} & core_families)
            self.assertFalse(any("terminal-bench" == scoring.canonical_family(k) for k in keys))
        self.assertTrue(any("AIME" in key for keys in scoring.EXTENSION_ITEMS.values() for key in keys))

    def test_fixed_representative_precedes_eligibility(self):
        models = models_fixture()
        high = copy.deepcopy(models[0])
        high.update(slug="preferred-missing", variantPriority=100)
        high["scores"]["CritPt"] = None
        result = scoring.run_aindex_mixed_core_from_payload({"models": models + [high]})
        self.assertNotIn(models[0]["variantGroup"], {r["variant_group"] for r in result["full_rankings"]})
        self.assertIn(models[0]["slug"], {r["slug"] for r in result["exact_config_full_rankings"]})
        self.assertIn("preferred-missing", {r["slug"] for r in result["validation"]["core_eligibility"]["variant_group"]["excluded_models"]})

    def test_missing_board_and_single_item_zero_are_distinct(self):
        models = models_fixture()
        models[0]["scores"]["CritPt"] = 0
        models[1]["scores"]["CritPt"] = None
        models[2]["scores"]["Terminal-Bench v4.0"] = None
        models[2]["scores"]["SciCode"] = None
        models[2]["scores"]["Terminal-Bench v2.1"] = 100
        result = scoring.run_aindex_mixed_core_from_payload({"models": models})
        rows = {r["slug"]: r for r in result["full_rankings"]}
        self.assertIn(models[0]["slug"], rows)
        self.assertNotIn(models[1]["slug"], rows)
        self.assertNotIn(models[2]["slug"], rows)
        self.assertEqual(rows[models[0]["slug"]]["hard-reasoning_core_score"], 0)

    def test_partial_board_gets_no_bonus_and_keeps_half_share(self):
        models = models_fixture()
        models[0]["scores"]["Terminal-Bench v4.0"] = None
        models[0]["scores"]["SciCode"] = 90
        result = scoring.run_aindex_mixed_core_from_payload({"models": models})
        row = next(r for r in result["full_rankings"] if r["slug"] == models[0]["slug"])
        self.assertEqual(row["coding_core_score"], 45)
        self.assertEqual(row["coding_extension_bonus"], 0)
        self.assertEqual(float(row["coding_points_full_precision"]), 5.4)
        self.assertEqual(row["coding_item1_adjusted"], None)
        self.assertEqual(row["coding_item1_base_points"], 0)
        self.assertEqual(row["coding_core_tests"], 1)
        self.assertEqual(result["calibration"]["boards"]["coding"]["complete_core_models"], 11)
        self.assertNotIn("hard-reasoning_item2", row)

    def test_four_missing_are_excluded(self):
        models = models_fixture()
        for key in ("Terminal-Bench v4.0", "AutomationBench-AA", "AA-Omniscience Accuracy", "GDP.pdf"):
            models[0]["scores"][key] = None
        _, audit = scoring.prepare(models)
        item = audit["excluded_models"][0]
        self.assertEqual(item["missing_core_count"], 4)
        self.assertIn("missing_at_least_four", item["reason"])

    def test_exact_config_uses_representative_calibration_and_never_unscoped_extensions(self):
        models = models_fixture()
        sibling = copy.deepcopy(models[0])
        sibling.update(slug="sibling", variantPriority=1)
        sibling["scores"]["CritPt"] = 99
        baseline = scoring.run_aindex_mixed_core_from_payload({"models": models})
        result = scoring.run_aindex_mixed_core_from_payload({"models": models + [sibling]})
        self.assertEqual(baseline["calibration"], result["calibration"])
        key = next(k for keys in scoring.EXTENSION_ITEMS.values() for k in keys if k.startswith("benchmark:"))
        model = copy.deepcopy(models[0])
        model["externalBenchmarks"] = [{"metricKey": key, "evidenceEligible": True, "variantScoped": False}]
        self.assertIsNone(scoring.source_models({"models": [model]})[0]["scores"][key])

    def test_raw_restoration_matches_only_explicit_source_slugs(self):
        models = models_fixture()
        restored = scoring.source_models({"models": models}, [{"slug": models[0]["slug"], "CritPt": "0"}])
        self.assertEqual(restored[0]["scores"]["CritPt"], 0)
        self.assertIsNone(restored[0]["scores"]["SciCode"])
        self.assertEqual(restored[1]["scores"]["SciCode"], models[1]["scores"]["SciCode"])

    def test_independent_validator_checks_source_scores_calibration_and_site_profiles(self):
        payload = {"models": models_fixture()}
        payload["models"][0]["scores"]["SciCode"] = None
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            result = scoring.run_aindex_mixed_core_from_payload(payload, output_dir=output, write_outputs=True)
            attach_profiles(payload, result)
            path = output / "models.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            kwargs = dict(input_path=path, output_dir=output, raw_path=None, write_summary=False)
            audit = validator.validate_production_outputs(**kwargs)
            self.assertTrue(audit["passed"], audit["failures"])
            payload["models"][0]["rankingProfile"]["boards"]["coding"]["points"] += 1
            path.write_text(json.dumps(payload), encoding="utf-8")
            audit = validator.validate_production_outputs(**kwargs)
            self.assertFalse(audit["passed"])
            self.assertTrue(any("coding/points" in failure for failure in audit["failures"]))

    def test_independent_validator_catches_tampered_weight_and_missing_population(self):
        payload = {"models": models_fixture()}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            scoring.run_aindex_mixed_core_from_payload(payload, output_dir=output, write_outputs=True)
            path = output / "models.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            summary_path = output / scoring.OUTPUT_FILENAMES["validation"]
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary["calibration"]["board_weights"]["coding"] = 20
            summary["calibration"]["population_slugs"].pop()
            summary_path.write_text(json.dumps(summary), encoding="utf-8")
            audit = validator.validate_production_outputs(input_path=path, output_dir=output, raw_path=None,
                                                           write_summary=False, check_profiles=False)
            self.assertFalse(audit["passed"])
            self.assertTrue(any("weights" in failure for failure in audit["failures"]))
            self.assertTrue(any("population" in failure for failure in audit["failures"]))

    def test_independent_validator_rejects_stale_public_leaderboard(self):
        payload = {"models": models_fixture()}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            result = scoring.run_aindex_mixed_core_from_payload(payload, output_dir=output, write_outputs=True)
            attach_profiles(payload, result)
            payload["leaderboard"]["rows"].reverse()
            payload["leaderboard"]["calibration"] = {**result["calibration"], "bonus_cap_per_board": 99}
            path = output / "models.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            audit = validator.validate_production_outputs(input_path=path, output_dir=output, raw_path=None,
                                                           write_summary=False)
            self.assertFalse(audit["passed"])
            self.assertTrue(any("leaderboard/rows" in failure for failure in audit["failures"]))
            self.assertTrue(any("serialized calibration" in failure for failure in audit["failures"]))


if __name__ == "__main__":
    unittest.main()
