"""Production regression tests for the reviewed AIndex Scheme 18 method.

The reviewed v5 CSV remains an immutable decision record for the frozen
2026-08-08 snapshot.  Production parity is checked against the stable outputs
rebuilt from the current input, so scheduled data refreshes can legitimately
change the population, cap, scores, and order without invalidating the review
record.
"""

from __future__ import annotations

import ast
import copy
import csv
import inspect
import json
import math
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

from analysis.irt_leaderboard_exploration import aindex_scheme18 as scheme18
from analysis.irt_leaderboard_exploration.evidence_only_ranking_analysis import (
    sanitize_models,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "docs" / "data" / "models.json"
REVIEW_DIR = (
    ROOT
    / "analysis"
    / "irt_leaderboard_exploration"
    / "outputs"
    / "candidate_method_review_2026_08_10_v5"
)
REVIEW_CANDIDATE_ID = (
    "v5_partial_credit_geometric_logsumexp_residual_t1_"
    "independent_audit_mean_plus_sqrt2_sd"
)
REVIEW_FULL_RANKING = (
    REVIEW_DIR / "full_rankings" / f"{REVIEW_CANDIDATE_ID}.csv"
)
REVIEW_TOP50 = REVIEW_DIR / "review_top50" / f"{REVIEW_CANDIDATE_ID}.csv"
PRODUCTION_OUTPUT_DIR = (
    ROOT / "analysis" / "irt_leaderboard_exploration" / "outputs"
)
PRODUCTION_FULL_RANKING = (
    PRODUCTION_OUTPUT_DIR / scheme18.OUTPUT_FILENAMES["full_rankings"]
)
PRODUCTION_TOP50 = PRODUCTION_OUTPUT_DIR / scheme18.OUTPUT_FILENAMES["top50"]
BOARD_ORDER = (
    "coding",
    "agentic-tool-work",
    "hard-reasoning",
    "knowledge-science",
    "instruction-context",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def row_score(row: dict) -> float:
    for key in ("score_full_precision", "final_score_full_precision", "score"):
        if key in row and row[key] not in (None, ""):
            return float(row[key])
    raise AssertionError(f"ranking row has no full-precision score field: {row}")


def calibration_cap(calibration) -> float:
    if isinstance(calibration, dict):
        for key in ("bonus_cap", "bonus_cap_per_board", "cap"):
            if key in calibration:
                return float(calibration[key])
    for key in ("bonus_cap", "bonus_cap_per_board", "cap"):
        if hasattr(calibration, key):
            return float(getattr(calibration, key))
    raise AssertionError("Scheme 18 calibration does not expose its shared bonus cap")


class AIndexScheme18FormulaTests(unittest.TestCase):
    def test_geometric_core_score_is_native_percent_and_requires_complete_core(self):
        raw = np.asarray(
            [
                [25.0, 100.0],
                [20.0, 45.0],
                [60.0, 60.0],
            ],
            dtype=float,
        )
        expected = 100.0 * np.exp(
            np.mean(np.log(np.clip(raw, 1e-6, 100.0) / 100.0), axis=1)
        )
        np.testing.assert_allclose(
            scheme18.geometric_core_score(raw),
            expected,
            rtol=0.0,
            atol=1e-12,
        )

        incomplete = raw.copy()
        incomplete[0, 1] = np.nan
        with self.assertRaises((AssertionError, ValueError)):
            scheme18.geometric_core_score(incomplete)

    def test_positive_residual_trend_and_bonus_are_missing_neutral_and_monotone(self):
        # Five observations are the minimum for one extension trend.  Row 5 is
        # intentionally missing and must remain NaN rather than become 0 or 50.
        core = np.asarray([10.0, 20.0, 30.0, 40.0, 50.0, 60.0])
        exact_trend = np.asarray([20.0, 30.0, 40.0, 50.0, 60.0, np.nan])
        one_positive = exact_trend.copy()
        one_positive[4] += 4.0
        two_positive = one_positive.copy()
        two_positive[3] += 2.0

        zero_residuals = scheme18.positive_residuals(
            core,
            exact_trend[:, None],
        )
        one_residuals = scheme18.positive_residuals(
            core,
            one_positive[:, None],
        )
        two_residuals = scheme18.positive_residuals(
            core,
            np.column_stack((one_positive, two_positive)),
        )

        self.assertTrue(np.isnan(zero_residuals[-1, 0]))
        self.assertEqual(float(np.nanmax(zero_residuals)), 0.0)
        self.assertGreater(float(np.nanmax(one_residuals)), 0.0)

        zero_bonus = scheme18.extension_bonus(
            zero_residuals,
            100.0,
        )
        one_bonus = scheme18.extension_bonus(
            one_residuals,
            100.0,
        )
        two_bonus = scheme18.extension_bonus(
            two_residuals,
            100.0,
        )
        self.assertEqual(float(zero_bonus[-1]), 0.0)
        self.assertGreaterEqual(float(one_bonus[4]), float(zero_bonus[4]))
        self.assertGreaterEqual(float(two_bonus[4]), float(one_bonus[4]))

    def test_shared_cap_uses_population_standard_deviation_ddof_zero(self):
        positive_residuals = np.asarray([1.0, 2.0, 4.0, 8.0], dtype=float)
        expected = float(
            np.mean(positive_residuals)
            + math.sqrt(2.0) * np.std(positive_residuals, ddof=0)
        )
        self.assertAlmostEqual(
            scheme18.derive_cap([positive_residuals]),
            expected,
            delta=1e-12,
        )
        self.assertNotAlmostEqual(
            expected,
            float(
                np.mean(positive_residuals)
                + math.sqrt(2.0) * np.std(positive_residuals, ddof=1)
            ),
            delta=1e-6,
        )

    def test_rank_rows_uses_unrounded_score_then_stable_identity(self):
        rows = [
            {
                "model": "Lower after rounding",
                "slug": "model-b",
                "variant_group": "model b",
                "score_full_precision": 61.00000041,
                "final_score": 61.0,
            },
            {
                "model": "Higher after rounding",
                "slug": "model-a",
                "variant_group": "model a",
                "score_full_precision": 61.00000049,
                "final_score": 61.0,
            },
            {
                "model": "Stable tie B",
                "slug": "stable-b",
                "variant_group": "stable b",
                "score_full_precision": 60.0,
                "final_score": 60.0,
            },
            {
                "model": "Stable tie A",
                "slug": "stable-a",
                "variant_group": "stable a",
                "score_full_precision": 60.0,
                "final_score": 60.0,
            },
        ]
        ranked = scheme18.rank_rows(rows)
        self.assertEqual(
            [row["slug"] for row in ranked],
            ["model-a", "model-b", "stable-a", "stable-b"],
        )
        self.assertEqual([row["rank"] for row in ranked], [1, 2, 3, 4])


class AIndexScheme18CoreEligibilityTests(unittest.TestCase):
    @staticmethod
    def complete_models():
        core_keys = {key for keys in scheme18.CORE_ITEMS.values() for key in keys}
        extension_keys = {key for keys in scheme18.EXTENSION_ITEMS.values() for key in keys}
        return [
            {
                "slug": f"model-{index}",
                "model": f"Model {index}",
                "creator": f"Lab {index}",
                "variantGroup": f"group-{index}",
                "scores": {
                    **{key: 10 * (index + 1) for key in extension_keys},
                    **{key: 50.0 for key in core_keys},
                },
            }
            for index in range(6)
        ]

    def test_missing_core_excludes_only_affected_rows_without_changing_calibration(self):
        models = self.complete_models()
        baseline = scheme18.fit_calibration(models)
        missing_key = scheme18.CORE_ITEMS["coding"][0]
        withdrawn = copy.deepcopy(models[0])
        withdrawn.update(slug="withdrawn-model", model="Withdrawn Model", variantGroup="withdrawn-group")
        withdrawn["scores"][missing_key] = None
        models.append(withdrawn)
        payload = {"models": models}
        original = copy.deepcopy(payload)
        exact_models = copy.deepcopy(models)
        exact_missing_key = scheme18.CORE_ITEMS["hard-reasoning"][0]
        del exact_models[0]["scores"][exact_missing_key]
        slugs = [model["slug"] for model in models]

        with mock.patch.object(scheme18, "fit_calibration", wraps=scheme18.fit_calibration) as fit:
            result = scheme18.run_aindex_scheme18_from_payload(
                payload,
                calibration_slugs=slugs,
                exact_config_slugs=slugs,
                exact_config_models=exact_models,
            )

        self.assertEqual(fit.call_count, 1)
        self.assertEqual(result["calibration"], baseline)
        self.assertEqual({row["slug"] for row in result["full_rankings"]}, set(slugs[:-1]))
        self.assertEqual(
            {row["slug"] for row in result["exact_config_full_rankings"]},
            set(slugs[1:-1]),
        )
        self.assertEqual(payload, original)
        audit = result["validation"]["core_eligibility"]
        self.assertEqual(audit["variant_group"]["requested_count"], 7)
        self.assertEqual(audit["variant_group"]["eligible_count"], 6)
        self.assertEqual(audit["variant_group"]["excluded_models"], [
            {"slug": "withdrawn-model", "missing_core": {
                "coding": [missing_key], "knowledge-science": [missing_key],
            }},
        ])
        self.assertEqual(audit["exact_config"]["excluded_count"], 2)
        self.assertTrue(result["validation"]["passed"])

    def test_zero_core_remains_eligible_and_invalid_scale_still_fails(self):
        models = self.complete_models()
        key = scheme18.CORE_ITEMS["coding"][0]
        models[0]["scores"][key] = 0.0
        eligible, audit = scheme18._core_eligible_models(models)
        self.assertEqual(len(eligible), 6)
        self.assertEqual(audit["excluded_count"], 0)
        models[0]["scores"][key] = 101.0
        with self.assertRaisesRegex(AssertionError, "outside the direct 0--100"):
            scheme18._core_eligible_models(models)

    def test_no_complete_calibration_population_fails_without_imputation(self):
        models = self.complete_models()
        for model in models:
            model["scores"][scheme18.CORE_ITEMS["coding"][0]] = None
        with self.assertRaisesRegex(AssertionError, "calibration population is empty"):
            scheme18.run_aindex_scheme18_from_payload(
                {"models": models},
                calibration_slugs=[model["slug"] for model in models],
            )


class AIndexScheme18ReviewedSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(DEFAULT_INPUT.read_text(encoding="utf-8"))
        cls.review_full = read_csv(REVIEW_FULL_RANKING)
        cls.review_top50 = read_csv(REVIEW_TOP50)
        cls.production_full = read_csv(PRODUCTION_FULL_RANKING)
        cls.production_top50 = read_csv(PRODUCTION_TOP50)
        cls.result = scheme18.run_aindex_scheme18_from_payload(
            cls.payload,
            calibration_slugs=[row["slug"] for row in cls.production_full],
            write_outputs=False,
        )

    def test_frozen_review_artifacts_are_self_consistent(self):
        self.assertEqual(len(self.review_full), 154)
        self.assertEqual(len(self.review_top50), 50)
        self.assertEqual(
            [row["slug"] for row in self.review_top50],
            [row["slug"] for row in self.review_full[:50]],
        )
        np.testing.assert_allclose(
            [row_score(row) for row in self.review_top50],
            [row_score(row) for row in self.review_full[:50]],
            rtol=0.0,
            atol=1e-12,
        )

    def test_current_full_ranking_and_top50_match_production_outputs(self):
        actual_full = self.result["full_rankings"]
        actual_top50 = self.result["top50"]
        self.assertGreaterEqual(len(self.production_full), 50)
        self.assertEqual(len(actual_full), len(self.production_full))
        self.assertEqual(len(self.production_top50), 50)
        self.assertEqual(len(actual_top50), len(self.production_top50))
        self.assertEqual(
            [row["slug"] for row in actual_full],
            [row["slug"] for row in self.production_full],
        )
        self.assertEqual(
            [row["slug"] for row in actual_top50],
            [row["slug"] for row in self.production_top50],
        )
        np.testing.assert_allclose(
            [row_score(row) for row in actual_full],
            [row_score(row) for row in self.production_full],
            rtol=0.0,
            atol=1e-10,
        )

    def test_dynamic_cap_and_every_score_identity_are_reproduced(self):
        calibration = self.result["calibration"]
        self.assertAlmostEqual(
            calibration_cap(calibration),
            float(calibration["pooled_positive_residual_mean"])
            + math.sqrt(2.0)
            * float(calibration["pooled_positive_residual_population_sd"]),
            delta=1e-12,
        )
        for row in self.result["full_rankings"]:
            board_scores = []
            points = []
            for board_id in BOARD_ORDER:
                core = float(row[f"{board_id}_core_score"])
                bonus = float(row[f"{board_id}_extension_bonus"])
                score = float(row[f"{board_id}_score_full_precision"])
                point = float(row[f"{board_id}_points_full_precision"])
                # Core and bonus audit columns are displayed to six decimals;
                # score and point columns retain full precision.
                self.assertAlmostEqual(score, min(100.0, core + bonus), delta=1.1e-6)
                self.assertAlmostEqual(point, score / 5.0, delta=1e-11)
                self.assertGreaterEqual(bonus, 0.0)
                self.assertLessEqual(
                    bonus,
                    calibration_cap(self.result["calibration"]) + 5e-7,
                )
                board_scores.append(score)
                points.append(point)
            self.assertAlmostEqual(row_score(row), sum(points), delta=1e-11)
            self.assertAlmostEqual(row_score(row), float(np.mean(board_scores)), delta=1e-11)

    def test_missing_extensions_are_absent_and_never_imputed(self):
        rows = self.result["full_rankings"]
        found_zero_observation_board = False
        for row in rows:
            for board_id in BOARD_ORDER:
                tests = int(row[f"{board_id}_extension_tests"])
                bonus = float(row[f"{board_id}_extension_bonus"])
                if tests == 0:
                    found_zero_observation_board = True
                    self.assertEqual(bonus, 0.0)
                    self.assertAlmostEqual(
                        float(row[f"{board_id}_score_full_precision"]),
                        float(row[f"{board_id}_core_score"]),
                        delta=5.1e-7,
                    )
        self.assertTrue(found_zero_observation_board)

    def test_named_acceptance_gates_are_not_in_the_scoring_module(self):
        source_path = Path(inspect.getsourcefile(scheme18) or "")
        source = source_path.read_text(encoding="utf-8")
        ast.parse(source)
        lowered = source.lower()
        for forbidden in (
            "claude fable",
            "gpt-5.6 sol",
            "muse spark",
            "deepseek v4 flash",
            "gemini",
            "qwen",
            "required_order_target",
            "rank_change_due_to",
            "publication_order_rule",
        ):
            self.assertNotIn(forbidden, lowered)


class AIndexScheme18ExactConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(DEFAULT_INPUT.read_text(encoding="utf-8"))
        cls.production_full = read_csv(PRODUCTION_FULL_RANKING)
        cls.calibration_slugs = [row["slug"] for row in cls.production_full]
        cls.exact_models, cls.exact_sanitation = sanitize_models(
            cls.payload,
            exact_config_only=True,
        )
        cls.exact_slugs = [
            str(model["slug"])
            for model in cls.payload["models"]
            if model.get("exactRankingProfile")
        ]
        cls.result = scheme18.run_aindex_scheme18_from_payload(
            cls.payload,
            calibration_slugs=cls.calibration_slugs,
            exact_config_slugs=cls.exact_slugs,
            exact_config_models=cls.exact_models,
            write_outputs=False,
        )

    def test_exact_configs_reuse_default_deduped_calibration(self):
        validation = self.result["validation"]
        self.assertTrue(validation["exact_reuses_deduplicated_calibration"])
        self.assertEqual(
            validation["calibration_population_size"],
            len(self.result["full_rankings"]),
        )
        self.assertEqual(
            calibration_cap(self.result["calibration"]),
            validation["bonus_cap_per_board"],
        )

        # The production runner must fit exactly once. Exact configurations
        # are an application population, never a second fit population.
        with mock.patch.object(
            scheme18,
            "fit_calibration",
            wraps=scheme18.fit_calibration,
        ) as fit:
            scheme18.run_aindex_scheme18_from_payload(
                self.payload,
                calibration_slugs=self.calibration_slugs,
                exact_config_slugs=self.exact_slugs,
                exact_config_models=self.exact_models,
                write_outputs=False,
            )
        self.assertEqual(fit.call_count, 1)

    def test_exact_config_sanitation_rejects_unscoped_and_shared_family_evidence(self):
        self.assertGreater(
            int(
                self.exact_sanitation[
                    "unscoped_external_score_cells_removed"
                ]
            ),
            0,
        )
        self.assertGreater(
            int(self.exact_sanitation["shared_variant_score_cells_removed"]),
            0,
        )

        # Score the same exact slugs once with raw family evidence and once
        # with the sanitized exact-config evidence. Production must equal the
        # latter. At least one row (currently Fable) must expose the difference
        # so this test cannot pass vacuously.
        calibration = self.result["calibration"]
        raw_by_slug = {
            str(model.get("slug") or ""): model
            for model in self.payload["models"]
        }
        raw_models = [raw_by_slug[slug] for slug in self.exact_slugs]
        raw_rows = {
            row["slug"]: row
            for row in scheme18.rank_rows(
                scheme18.score_models(
                    raw_models,
                    calibration,
                    ranking_grain="exact_config",
                )
            )
        }
        production_rows = {
            row["slug"]: row
            for row in self.result["exact_config_full_rankings"]
        }
        sanitized_rows = {
            row["slug"]: row
            for row in scheme18.rank_rows(
                scheme18.score_models(
                    [
                        model
                        for model in self.exact_models
                        if str(model.get("slug") or "") in set(self.exact_slugs)
                    ],
                    calibration,
                    ranking_grain="exact_config",
                )
            )
        }
        self.assertEqual(set(production_rows), set(sanitized_rows))
        for slug, production in production_rows.items():
            self.assertAlmostEqual(
                row_score(production),
                row_score(sanitized_rows[slug]),
                delta=1e-11,
                msg=slug,
            )
        self.assertTrue(
            any(
                abs(row_score(raw_rows[slug]) - row_score(production_rows[slug]))
                > 1e-9
                for slug in production_rows
            ),
            "unscoped/shared evidence did not affect any raw exact score",
        )


if __name__ == "__main__":
    unittest.main()
