import copy
from contextlib import redirect_stdout
import io
import unittest
from unittest import mock

import numpy as np

from analysis.irt_leaderboard_exploration import mixed_core_variants as mixed


def fixture():
    core = dict(zip(mixed.BOARDS, (
        (mixed.base.LATEST_TB, "SciCode"), ("AutomationBench-AA", "τ³-Banking"),
        ("CritPt", "Humanity's Last Exam"), ("AA-Omniscience Accuracy", "MMMU-Pro"),
        ("AA-LCR v1.1", "GDP.pdf"),
    )))
    values = (95, 90, 75, 70, 77, 72, 70, 69, 65, 85, 80, 79, 68, 67)
    models = [{"slug": slug, "model": slug, "variantGroup": slug, "variantPriority": 70,
               "creator": "Test", "externalBenchmarks": [],
               "scores": {item: value for items in core.values() for item in items}}
              for slug, value in zip(mixed.previous.CURRENT_TARGETS, values)]
    return core, models


class MixedCoreSearchTests(unittest.TestCase):
    def test_search_uses_exactly_two_singletons_and_preserves_complete_passing_weights(self):
        core, models = fixture()
        options = [(pair,) for pair in core.values()]
        options[2] += (("CritPt",),)
        options[3] += (("AA-Omniscience Accuracy",),)
        before = copy.deepcopy(models)
        with redirect_stdout(io.StringIO()):
            summary, selected, prepared, calibrations, weights = mixed.search(
                models, options=options, values=(20,), single_core_domains=2,
                minimum_population=0, minimum_item_coverage=0)
        self.assertEqual(summary["structures_considered"], 1)
        self.assertEqual(summary["passing_combinations"], 1)
        self.assertEqual(len(selected), 1)
        self.assertEqual(mixed.singleton_count(selected[0]["core"]), 2)
        self.assertEqual(sum(map(len, selected[0]["core"].values())), 8)
        np.testing.assert_array_equal(next(iter(weights.values())), np.array([[20] * 5], dtype=np.uint8))
        self.assertEqual(models, before)
        variants, results, validation, common = mixed.build_results(selected, prepared, calibrations, models)
        self.assertEqual(common, len(models))
        self.assertEqual(len(variants), 1)
        self.assertTrue(results["mc01"]["common_preference_audit"]["passed"])
        self.assertTrue(validation["mc01"]["full"]["passed"])

    def test_common_selection_rejects_full_only_candidates(self):
        core, models = fixture()
        core["hard-reasoning"] = ("CritPt",)
        core["knowledge-science"] = ("AA-Omniscience Accuracy",)
        rows, _, _, eligible = mixed.engine.score_variant(models, core, [20] * 5)
        candidates = mixed.candidate_shortlist("s1", core, rows, np.array([[20] * 5], dtype=float))
        with mock.patch.object(mixed.preferences, "constraint_audit", return_value={"passed": False, "checks": []}):
            selected, rejected = mixed.common_selection(candidates, {"s1": eligible})
        self.assertEqual(selected, [])
        self.assertEqual(len(rejected), 1)

    def test_selection_is_deterministic_and_prioritizes_distinct_structures(self):
        core, models = fixture()
        core["hard-reasoning"] = ("CritPt",)
        core["knowledge-science"] = ("AA-Omniscience Accuracy",)
        rows, _, _, _ = mixed.engine.score_variant(models, core, [20] * 5)
        vectors = np.array([[20] * 5, [19, 20, 20, 20, 21]], dtype=float)
        candidates = [c for key in ("a", "b", "c") for c in mixed.candidate_shortlist(key, core, rows, vectors)]
        selected = mixed.select_candidates(candidates, count=3)
        self.assertEqual({c["core_id"] for c in selected}, {"a", "b", "c"})
        self.assertEqual(selected, mixed.select_candidates(list(reversed(candidates)), count=3))

    def test_linear_margin_matches_full_rank_audit(self):
        core, models = fixture()
        core["hard-reasoning"] = ("CritPt",)
        core["knowledge-science"] = ("AA-Omniscience Accuracy",)
        models[2]["scores"]["CritPt"] = 20
        rows, _, _, _ = mixed.engine.score_variant(models, core, [20] * 5)
        weights = np.array([[9, 18, 26, 21, 26], [20] * 5], dtype=float)
        margins = mixed.margin_vector(rows, weights)
        expected = [mixed.preferences.constraint_audit(mixed.preferences.weighted_rows(rows, w),
                    **mixed.previous.AUDIT_KWARGS)["minimum_margin"] for w in weights]
        np.testing.assert_allclose(margins, expected, atol=1e-12)


if __name__ == "__main__":
    unittest.main()
