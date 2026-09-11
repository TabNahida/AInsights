import copy
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import numpy as np

from analysis.irt_leaderboard_exploration import filtered_dual_core_variants as filtered


dual = filtered.dual
preferences = filtered.preferences


def synthetic_rows():
    # These are invented observations, independent of the live model snapshot.
    values = ([90]*5, [85]*5, [80, 60, 70, 70, 70], [60, 80, 70, 70, 70],
              [70, 80, 60, 70, 70], [70, 60, 80, 70, 70],
              [75]*5, [74]*5, [65]*5)
    rows = []
    for slug, board_values in zip(preferences.TARGETS, values):
        row = {"slug": slug, "score": sum(board_values)/5}
        for board, value in zip(dual.BOARDS, board_values):
            row[board + "_score"] = value
            row[board + "_core"] = value
        rows.append(row)
    rival = {"slug": "unrelated-competitor", "score": 80}
    for board, value in zip(dual.BOARDS, [100, 75, 75, 75, 75]):
        rival[board + "_score"] = value
        rival[board + "_core"] = value
    return rows + [rival]


def candidate(core, weights, margin, sensitivity):
    return {"core": copy.deepcopy(core), "weights": weights,
            "minimum_margin": margin, "sensitivity_passing": sensitivity,
            "sensitivity_total": 20,
            "distance_from_equal": sum(abs(w-20) for w in weights),
            "population": 120, "missing_core_total": 0}


class FilteredDualCoreVariantsTests(unittest.TestCase):
    def test_fast_screen_matches_full_audit_across_grid_and_row_order(self):
        rows = synthetic_rows()
        grid = filtered.weight_grid((10, 20, 30, 40))
        expected = [i for i, weights in enumerate(grid)
                    if preferences.constraint_audit(
                        preferences.weighted_rows(rows, weights))["passed"]]
        self.assertGreater(len(expected), 0)
        self.assertLess(len(expected), len(grid))
        np.testing.assert_array_equal(filtered.passing_weight_indices(rows, grid), expected)
        np.testing.assert_array_equal(filtered.passing_weight_indices(list(reversed(rows)), grid), expected)

    def test_first_and_second_must_beat_non_target_competitors(self):
        rows = synthetic_rows()
        weights = np.asarray([[30, 20, 10, 20, 20]], dtype=float)
        self.assertEqual(filtered.passing_weight_indices(rows, weights).tolist(), [0])
        # Every named pair still has the desired relative order, but an unrelated
        # contender displaces either Astra alone or both of the intended top two.
        for rival_score, intended_ranks in ((87, [1, 3]), (95, [2, 3])):
            with self.subTest(rival_score=rival_score):
                modified = copy.deepcopy(rows)
                for board in dual.BOARDS:
                    modified[-1][board + "_score"] = rival_score
                ranked = preferences.weighted_rows(modified, weights[0])
                lookup = {row["slug"]: row for row in ranked}
                self.assertEqual([lookup[s]["rank"] for s in preferences.TARGETS[:2]], intended_ranks)
                for a, b in ((0, 1), *preferences.PAIRS):
                    self.assertGreater(lookup[preferences.TARGETS[a]]["score"],
                                       lookup[preferences.TARGETS[b]]["score"])
                self.assertFalse(preferences.constraint_audit(ranked)["passed"])
                self.assertEqual(filtered.passing_weight_indices(modified, weights).tolist(), [])

    def test_missing_any_required_target_rejects_all_weights(self):
        rows = synthetic_rows()
        grid = filtered.weight_grid((10, 20, 30, 40))
        for target in preferences.TARGETS:
            with self.subTest(target=target):
                incomplete = [row for row in rows if row["slug"] != target]
                self.assertEqual(filtered.passing_weight_indices(incomplete, grid).tolist(), [])

    def test_screen_and_audit_apply_the_same_strict_minimum_gap(self):
        grid = np.asarray([[20]*5], dtype=float)
        for gap, accepted in ((0.049, False), (0.051, True)):
            rows = synthetic_rows()
            for row, score in zip(rows, [90, 85, 75, 70, 70+gap, 70, 75, 74, 65, 80]):
                for board in dual.BOARDS:
                    row[board + "_score"] = score
            audit = preferences.constraint_audit(preferences.weighted_rows(rows, grid[0]))
            with self.subTest(gap=gap):
                self.assertEqual(audit["passed"], accepted)
                self.assertEqual(filtered.passing_weight_indices(rows, grid).tolist(), [0] if accepted else [])

    def test_publication_requires_full_and_common_audits_and_explicit_pass(self):
        passing = {"preference_audit": {"passed": True},
                   "common_preference_audit": {"passed": True}}
        dual.require_passing_preferences({"first": passing, "second": copy.deepcopy(passing)})
        for scope in passing:
            for failure in ("false", "missing_audit", "missing_passed"):
                with self.subTest(scope=scope, failure=failure):
                    invalid = copy.deepcopy(passing)
                    if failure == "false":
                        invalid[scope]["passed"] = False
                    elif failure == "missing_audit":
                        invalid.pop(scope)
                    else:
                        invalid[scope].pop("passed")
                    with self.assertRaisesRegex(ValueError, "second:" + scope):
                        dual.require_passing_preferences({"first": passing, "second": invalid})

    def test_filtered_run_writes_nothing_when_either_audit_fails(self):
        scores = {key: 60 for pair in dual.DEFAULT_CORE.values() for key in pair}
        scores.pop(dual.base.TB)
        scores[dual.base.LATEST_TB] = 60
        source = {"slug": "synthetic", "model": "Synthetic", "variantGroup": "synthetic",
                  "variantPriority": 70, "creator": "Test", "scores": scores,
                  "externalBenchmarks": []}
        config = {"core": dual.DEFAULT_CORE, "weights": [20]*5, "label": "synthetic"}
        # Keep real eligibility, scoring, common-cohort fitting and validation.
        # Control only the two audits to exercise each publication failure path.
        for full_pass, common_pass in ((False, True), (True, False)):
            audits = [{"passed": full_pass, "checks": []}, {"passed": common_pass, "checks": []}]
            with self.subTest(full_pass=full_pass), tempfile.TemporaryDirectory() as temp:
                output = Path(temp) / "unpublished"
                with mock.patch.object(dual, "load_inputs", return_value=({}, [source], [source], {})), \
                     mock.patch.object(preferences, "constraint_audit", side_effect=audits), \
                     mock.patch.object(preferences, "weight_sensitivity", return_value={}), \
                     mock.patch.object(dual.base.scheme18, "write_csv") as write_csv, \
                     mock.patch("analysis.irt_leaderboard_exploration.dual_core_reports.write_reports") as write_reports:
                    with self.assertRaisesRegex(ValueError, "Filtered candidates failed"):
                        dual.run(Path(temp)/"unused.json", Path(temp)/"unused.csv", output,
                                 variants={"test": config}, selection_mode="preference_filtered")
                    write_csv.assert_not_called()
                    write_reports.assert_not_called()
                    self.assertEqual(list(output.rglob("*")), [])

    def test_weight_grid_has_only_unique_allowed_vectors_summing_to_one_hundred(self):
        values = (10, 20, 30, 40)
        grid = filtered.weight_grid(values)
        self.assertEqual(grid.shape[1], 5)
        self.assertTrue(np.isin(grid, values).all())
        self.assertTrue((grid.sum(axis=1) == 100).all())
        self.assertEqual(len(grid), len({tuple(weights) for weights in grid}))
        self.assertIn((20, 20, 20, 20, 20), {tuple(weights) for weights in grid})
        # An allowed set can be infeasible without producing a malformed matrix.
        self.assertEqual(filtered.weight_grid((40,)).shape, (0, 5))

    def test_selection_is_distinct_deterministic_and_preserves_core_structures(self):
        alternative = copy.deepcopy(dual.DEFAULT_CORE)
        alternative["coding"] = (dual.base.TB, "LiveCodeBench")
        vectors = ([20]*5, [10, 20, 20, 20, 30], [20, 10, 20, 30, 20],
                   [10, 30, 20, 20, 20], [30, 10, 20, 20, 20], [10, 10, 30, 30, 20])
        candidates = [candidate(core, list(weights), 0.1+i/100, (i*7) % 21)
                      for core in (dual.DEFAULT_CORE, alternative)
                      for i, weights in enumerate(vectors)]
        # A repeated identical search record must not be published twice.
        candidates.append(copy.deepcopy(candidates[0]))
        selected = filtered.select_candidates({"candidates": candidates}, count=10)
        reversed_selection = filtered.select_candidates({"candidates": list(reversed(candidates))}, count=10)
        self.assertEqual(selected, reversed_selection)
        self.assertEqual(len(selected), 10)
        identities = [(filtered.core_signature(c["core"]), tuple(c["weights"])) for c, _ in selected]
        self.assertEqual(len(set(identities)), 10)
        self.assertEqual(len({structure for structure, _ in identities}), 2)
        self.assertEqual(filtered.select_candidates({"candidates": []}), [])
        self.assertEqual(len(filtered.select_candidates({"candidates": candidates}, count=3)), 3)


if __name__ == "__main__":
    unittest.main()
