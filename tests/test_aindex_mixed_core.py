import copy
import json
import re
from pathlib import Path
import tempfile
import unittest

import numpy as np

from analysis.irt_leaderboard_exploration import aindex_mixed_core as scoring
from analysis.irt_leaderboard_exploration import aindex_scheme18 as historical_scoring
from analysis.irt_leaderboard_exploration import validate_mixed_core_production as validator
from analysis.irt_leaderboard_exploration import validate_scheme18_production as historical_validator
from analysis.irt_leaderboard_exploration.mixed_core_extension_policy import CURRENT_EXTENSION_POLICIES


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
    def test_sparse_trend_threshold_and_scheme18_default(self):
        core = np.asarray([10.0, 20.0, 30.0, 40.0, 50.0])
        values = np.asarray([10.0, 50.0, 35.0, 60.0, 65.0])
        for fit in (historical_scoring._fit_positive_residuals, historical_validator.fit_trends):
            two = values.copy()
            two[2:] = np.nan
            residuals, trends = fit(core, two[:, None], minimum_observed=3)
            self.assertFalse(trends[0]["enabled"])
            self.assertEqual(trends[0]["observed_count"], 2)
            self.assertTrue(np.isnan(residuals).all())

            three = values.copy()
            three[3:] = np.nan
            residuals, trends = fit(core, three[:, None], minimum_observed=3)
            self.assertTrue(trends[0]["enabled"])
            self.assertEqual(trends[0]["observed_count"], 3)
            self.assertGreater(float(np.nanmax(residuals)), 0.0)
            self.assertFalse(fit(core, three[:, None])[1][0]["enabled"])

            four = values.copy()
            four[4:] = np.nan
            self.assertFalse(fit(core, four[:, None])[1][0]["enabled"])
            self.assertTrue(fit(core, values[:, None])[1][0]["enabled"])

    def test_mixed_core_and_independent_validator_enable_three_fit_pairs(self):
        key = scoring.EXTENSION_ITEMS["coding"][0]
        for observed_count in (2, 3):
            models = models_fixture()
            for model in models[observed_count:]:
                model["scores"][key] = None
            production = scoring.fit_calibration(models)["boards"]["coding"]["extension_items"][0]
            independent = validator._calibrate(models)["trends"]["coding"][0]
            self.assertEqual(production["observed_count"], observed_count)
            self.assertEqual(independent["observed_count"], observed_count)
            self.assertIs(production["enabled"], observed_count == 3)
            self.assertIs(independent["enabled"], observed_count == 3)

    def test_fixed_shares_do_not_renormalize_missing_or_floor_observed_zero(self):
        np.testing.assert_array_equal(scoring.fixed_share_base(np.array([[80, np.nan], [0, 60], [0, 0]])),
                                      np.array([40, 30, 0]))
        np.testing.assert_array_equal(scoring.fixed_share_base(np.array([[80], [0]])), np.array([80, 0]))

    def test_registry_has_exact_scheme_and_no_core_family_extensions(self):
        self.assertEqual(list(scoring.BOARD_WEIGHTS.values()), [24, 24, 27, 16, 9])
        self.assertEqual(sum(map(len, scoring.CORE_ITEMS.values())), 8)
        self.assertEqual(sum(len(keys) == 1 for keys in scoring.CORE_ITEMS.values()), 2)
        core_families = {scoring.canonical_family(k) for keys in scoring.CORE_ITEMS.values() for k in keys}
        self.assertEqual(len(core_families), 8)
        for keys in scoring.EXTENSION_ITEMS.values():
            self.assertFalse({scoring.canonical_family(k) for k in keys} & core_families)
            self.assertFalse(any("terminal-bench" == scoring.canonical_family(k) for k in keys))
        extension_keys = {key for keys in scoring.EXTENSION_ITEMS.values() for key in keys}
        self.assertIn("Humanity's Last Exam", scoring.EXTENSION_ITEMS["hard-reasoning"])
        self.assertIn("benchmark:frontiercode-v1-1-main-cognition", scoring.EXTENSION_ITEMS["coding"])
        self.assertIn("benchmark:deepswe-v1-1-owner-mini-swe-agent", scoring.EXTENSION_ITEMS["coding"])
        self.assertIn("benchmark:swe-marathon-v1-1-owner", scoring.EXTENSION_ITEMS["coding"])
        self.assertIn("benchmark:frontiermath-tier-4-v2-epoch", scoring.EXTENSION_ITEMS["hard-reasoning"])
        self.assertIn("benchmark:epoch-chess-puzzles-v1-1-6", scoring.EXTENSION_ITEMS["hard-reasoning"])
        self.assertIn("benchmark:epoch-mystery-game-puzzles-v1-0-4", scoring.EXTENSION_ITEMS["hard-reasoning"])
        self.assertIn("benchmark:epoch-ebr-bench-card-ban-v4", scoring.EXTENSION_ITEMS["hard-reasoning"])
        self.assertIn("benchmark:arc-agi-3-standard", scoring.EXTENSION_ITEMS["agentic-tool-work"])
        self.assertIn("benchmark:agents-last-exam-v1-overall-pass-rate", scoring.EXTENSION_ITEMS["agentic-tool-work"])
        for key in (
            "benchmark:aa-analyst-agent-pass5",
            "benchmark:terminal-bench-science-aa",
            "benchmark:aa-briefcase-rubric-pass-rate",
            "benchmark:harvey-lab-aa-all-pass-rate",
            "benchmark:toolathlon-verified-owner",
            "benchmark:osworld-v2-v2026-06-24-standard-500",
        ):
            self.assertIn(key, scoring.EXTENSION_ITEMS["agentic-tool-work"])
        self.assertEqual(scoring.EXTENSION_ITEMS["knowledge-science"], ("benchmark:mlcr-aa-overall",))
        self.assertEqual(validator.EXTENSIONS["knowledge-science"], ("benchmark:mlcr-aa-overall",))
        self.assertEqual(scoring.canonical_family("benchmark:terminal-bench-science-aa"), "terminal-bench-science")
        self.assertEqual(scoring.EXTENSION_ITEMS["instruction-context"], ("IFBench",))
        self.assertEqual(validator.EXTENSIONS["instruction-context"], ("IFBench",))
        self.assertEqual(scoring.canonical_family("IFBench"), "ifbench")
        self.assertNotIn("IFBench", historical_scoring.EXTENSION_ITEMS["instruction-context"])
        self.assertEqual(len(extension_keys), 19)
        self.assertEqual(sum(map(len, scoring.EXTENSION_ITEMS.values())), 19)
        self.assertIn("APEX-Agents-AA", extension_keys)
        self.assertNotIn("benchmark:hle-tools", extension_keys)
        self.assertFalse(any("aime" in key.casefold() for key in extension_keys))
        self.assertFalse(extension_keys & {
            "benchmark:swe-bench-pro", "benchmark:livecodebench", "τ²-Bench Telecom", "benchmark:osworld-verified",
            "MMMU-Pro", "benchmark:mmlu-pro", "benchmark:charxiv-no-tools",
            "benchmark:mcp-atlas",
        })

    def test_methodology_registry_matches_scoring_registry(self):
        html = (Path(__file__).resolve().parents[1] / "docs/methodology.html").read_text(
            encoding="utf-8"
        )
        listed = re.findall(r'data-extension-key="([^"]+)" data-boards="([^"]+)"', html)
        expected = [(key, board) for board, keys in scoring.EXTENSION_ITEMS.items()
                    for key in keys]
        self.assertCountEqual(listed, expected)
        self.assertEqual(len(listed), len(expected))

    def test_ifbench_uses_the_independent_aa_score_protocol(self):
        policy = next(p for p in CURRENT_EXTENSION_POLICIES if p.score_key == "IFBench")
        self.assertEqual(policy.benchmark_creator_controller, "Ai2 (Allen Institute for AI)")
        self.assertIs(policy.controller_is_ranked_model_vendor, False)
        self.assertEqual(policy.result_operator, "Artificial Analysis")
        self.assertEqual(policy.score_provenance, "direct_observation")
        self.assertEqual(policy.result_protocol, "AA common protocol")
        self.assertIn("58 instruction constraints", policy.version_pin)
        self.assertIn("official loose evaluation", policy.version_pin)
        self.assertIn("prompt-level accuracy", policy.version_pin)
        self.assertEqual(policy.source_url, "https://artificialanalysis.ai/evaluations/ifbench")
        self.assertEqual((policy.observed_groups, policy.observed_creators), (72, 20))
        self.assertNotIn("IFBench", historical_scoring.EXTENSION_ITEMS["instruction-context"])

        models = models_fixture()
        with_ifbench = scoring.run_aindex_mixed_core_from_payload({"models": models})
        self.assertTrue(any(row["instruction-context_extension_bonus"] > 0
                            for row in with_ifbench["full_rankings"]))
        for model in models:
            model["scores"]["IFBench"] = None
        without_ifbench = scoring.run_aindex_mixed_core_from_payload({"models": models})
        self.assertTrue(all(row["instruction-context_extension_bonus"] == 0
                            for row in without_ifbench["full_rankings"]))

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
        self.assertEqual(float(row["coding_points_full_precision"]), 10.8)
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
            summary["calibration"]["board_weights"]["coding"] = 21
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
