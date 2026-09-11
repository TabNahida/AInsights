import copy
import itertools
from pathlib import Path
import tempfile
import unittest

import numpy as np

from analysis.irt_leaderboard_exploration import task_core_variants as task
from analysis.irt_leaderboard_exploration import core_suitability as quality


def core_fixture():
    return dict(zip(task.BOARDS, (
        (task.base.LATEST_TB, "SciCode"), ("AutomationBench-AA", "τ³-Banking"),
        ("CritPt", "Humanity's Last Exam"), ("AA-Omniscience Accuracy", "MMMU-Pro"),
        ("AA-LCR v1.1", "GDP.pdf"),
    )))


def synthetic_models():
    values = (95, 90, 75, 70, 77, 72, 70, 69, 65, 85, 80, 79, 68, 67)
    return [{"slug": slug, "model": slug, "variantGroup": slug, "variantPriority": 70,
             "creator": "test", "scores": {k: v for p in core_fixture().values() for k in p},
             "externalBenchmarks": []}
            for slug, v in zip(task.previous.CURRENT_TARGETS, values)]


class TaskCoreVariantsTests(unittest.TestCase):
    def test_banned_families_cannot_return_via_new_year_or_alias(self):
        for key in ("AIME 2025", "AIME 2026", "benchmark:aime-2027", "HMMT 2026",
                    "MATH-500", "GSM8K", "LiveCodeBench", "benchmark:livecodebench", "GPQA Diamond", "benchmark:gpqa-diamond"):
            core = core_fixture()
            core["hard-reasoning"] = ("CritPt", key)
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "Forbidden"):
                task.validate_next_core(core)
        task.validate_next_core(core_fixture())

    def test_search_rejects_banned_core_without_changing_extension_policy(self):
        before = copy.deepcopy(task.base.scheme18.EXTENSION_ITEMS)
        core = core_fixture()
        core["hard-reasoning"] = ("CritPt", "AIME 2025")
        result = task.search_candidates(synthetic_models(), {},
            options=tuple((pair,) for pair in core.values()), values=(20,),
            minimum_population=0, minimum_item_coverage=0, diagnose=False)
        self.assertEqual(result["invalid_core_structures"], 1)
        self.assertEqual(result["passing_combinations"], 0)
        self.assertEqual(task.base.scheme18.EXTENSION_ITEMS, before)
        self.assertIn("AIME 2025", task.dual.extension_registry(core_fixture())["hard-reasoning"])

    def test_positive_search_still_checks_full_and_common_populations(self):
        models = synthetic_models()
        result = task.search_candidates(models, {}, options=tuple((p,) for p in core_fixture().values()),
                                       values=(20,), minimum_population=0, minimum_item_coverage=0, diagnose=False)
        self.assertEqual(result["passing_combinations"], 1)
        selected, rejected = task.select_common_passing(result, models, {})
        self.assertEqual(len(selected), 1)
        self.assertFalse(rejected)
        self.assertEqual(next(iter(task.make_variants(selected).values()))["weights"], [20] * 5)

    def test_linear_constraints_match_real_audit_including_unrelated_contenders(self):
        rng = np.random.default_rng(17)
        slugs = (*task.previous.CURRENT_TARGETS, "claude-fable-5", "another-model")
        rows = [{"slug": slug, **{b + "_score": float(value) for b, value in zip(task.BOARDS, rng.uniform(20, 100, 5))}}
                for slug in slugs]
        for row in rows:
            row["score"] = sum(row[b + "_score"] for b in task.BOARDS) / 5
            row.update({b + "_core": row[b + "_score"] for b in task.BOARDS})
        pairs, differences = task.preference_differences(rows)
        self.assertNotIn((slugs[1], slugs[0]), pairs)
        self.assertIn((slugs[1], "claude-fable-5"), pairs)
        for weights in ([20] * 5, [9, 9, 40, 33, 9], [40, 20, 12, 9, 19]):
            ranked = task.preferences.weighted_rows(rows, weights)
            audit = task.preferences.constraint_audit(ranked, **task.previous.AUDIT_KWARGS)
            margin = float((differences @ np.asarray(weights) / 100).min())
            self.assertAlmostEqual(margin, audit["minimum_margin"], places=10)
            self.assertEqual(margin > task.preferences.MIN_MARGIN, audit["passed"])

    def test_analytic_single_pair_maximum_matches_all_polytope_vertices(self):
        difference = np.array([-0.8996, -4.25635, -0.32475, 1.1033, -1.3])
        vertices = []
        for free in range(5):
            for boundary in itertools.product((9, 40), repeat=4):
                remaining = 100 - sum(boundary)
                if 9 <= remaining <= 40:
                    weights = list(boundary)
                    weights.insert(free, remaining)
                    vertices.append(weights)
        expected = max(difference @ v / 100 for v in vertices)
        actual, witness = task.maximum_pair_margin(difference)
        self.assertAlmostEqual(actual, expected, places=12)
        self.assertEqual(sum(witness), 100)
        self.assertTrue(all(9 <= w <= 40 for w in witness))

    def test_empty_search_report_cannot_publish_rejected_top30(self):
        search = {"passing_combinations": 0, "structures": [], "structures_considered": 1,
                  "minimum_item_coverage": 100, "weight_vectors": 1}
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            task.write_search_report(output, search, {"source_generated_at": "2026-09-08"}, 0)
            text = (output / "TOP30_COMPARISON.md").read_text(encoding="utf-8")
            self.assertIn("没有通过全部筛选条件", text)
            self.assertEqual(list(output.glob("rankings_*.csv")), [])

    def test_quality_cohort_uses_dates_and_preserves_real_zero(self):
        models = [{"slug": str(i), "model": str(i), "variantGroup": str(i), "creator": "test",
                   "releaseDate": date, "scores": {"CritPt": value}}
                  for i, (date, value) in enumerate((
                      ("2026-03-12", 0), ("2026-09-08", 80), ("2026-03-11", 60),
                      ("2026-09-09", 10), (None, None), ("invalid", 30))) ]
        result = quality.profile({"generatedAt": "2026-09-08T23:56:02+00:00"}, models * 20, models, ("0", "1"))
        self.assertEqual(result["recent_population"], 2)
        row = result["rows"][0]
        self.assertEqual(row["recent"]["observed"], 2)
        self.assertEqual(row["recent"]["median"], 40)
        self.assertEqual(row["representatives"]["observed"], 5)
        self.assertEqual(len(result["release_date_anomalies"]), 3)


if __name__ == "__main__":
    unittest.main()
