import copy
import unittest

import numpy as np

from analysis.irt_leaderboard_exploration import dual_core_variants as dual


def model(slug, value=60, **overrides):
    scores = {key: value for pair in dual.DEFAULT_CORE.values() for key in pair}
    # The effective Terminal slot must be recreated from the evaluated version.
    scores.pop(dual.base.TB)
    scores[dual.base.LATEST_TB] = value
    scores.update(overrides)
    return {"slug": slug, "model": slug, "variantGroup": slug,
            "variantPriority": 70, "creator": "Lab", "scores": scores,
            "externalBenchmarks": []}


def missing(source, *keys):
    changed = copy.deepcopy(source)
    for key in keys:
        if key == dual.base.TB:
            key = dual.base.LATEST_TB
        changed["scores"][key] = None
    return changed


def training_models():
    # Constant observed Core with varied extensions creates positive residuals,
    # allowing tests to exercise the bonus policy rather than only zero bonuses.
    return [model(f"training-{i}", 40, **{"benchmark:swe-bench-pro": 10 + 10*i})
            for i in range(7)]


class DualCoreVariantsTests(unittest.TestCase):
    def test_core_requires_five_boards_two_items_and_ten_distinct_families(self):
        dual.validate_core(dual.DEFAULT_CORE)
        invalid = []
        shortened = copy.deepcopy(dual.DEFAULT_CORE)
        shortened.pop(dual.BOARDS[-1])
        invalid.append(shortened)
        one_item = copy.deepcopy(dual.DEFAULT_CORE)
        one_item["coding"] = (dual.base.TB,)
        invalid.append(one_item)
        same_item = copy.deepcopy(dual.DEFAULT_CORE)
        same_item["coding"] = (dual.base.TB, dual.base.TB)
        invalid.append(same_item)
        same_family = copy.deepcopy(dual.DEFAULT_CORE)
        same_family["coding"] = (dual.base.TB, dual.base.OLD_TB[0])
        invalid.append(same_family)
        omniscience_twice = copy.deepcopy(dual.DEFAULT_CORE)
        omniscience_twice["knowledge-science"] = (
            "AA-Omniscience Accuracy", "AA-Omniscience Non-Hallucination Rate")
        invalid.append(omniscience_twice)
        across_boards = copy.deepcopy(dual.DEFAULT_CORE)
        across_boards["coding"] = (dual.base.TB, "LiveCodeBench")
        across_boards["agentic-tool-work"] = ("AutomationBench-AA", "benchmark:livecodebench")
        invalid.append(across_boards)
        old_alias = copy.deepcopy(dual.DEFAULT_CORE)
        old_alias["instruction-context"] = ("AA-LCR", "GDP.pdf")
        invalid.append(old_alias)
        for core in invalid:
            with self.subTest(core=core), self.assertRaises(ValueError):
                dual.validate_core(core)

    def test_missing_zero_and_three_pass_but_four_fail(self):
        complete = model("complete")
        three = missing(model("three"), "SciCode", "AutomationBench-AA", "CritPt")
        four = missing(model("four"), "SciCode", "AutomationBench-AA", "CritPt",
                       "AA-Omniscience Accuracy")
        eligible, excluded = dual.prepare([complete, three, four], dual.DEFAULT_CORE, {})
        self.assertEqual({m["slug"]: m["missing_core_count"] for m in eligible},
                         {"complete": 0, "three": 3})
        self.assertEqual(len(excluded), 1)
        self.assertEqual(excluded[0]["slug"], "four")
        self.assertEqual(excluded[0]["missing_core_count"], 4)
        self.assertIn("missing_at_least_four", excluded[0]["reason"])
        self.assertEqual(excluded[0]["empty_boards"], "")

    def test_board_with_both_items_missing_fails_even_with_only_two_missing(self):
        source = missing(model("empty-coding"), *dual.DEFAULT_CORE["coding"])
        eligible, excluded = dual.prepare([source], dual.DEFAULT_CORE, {})
        self.assertFalse(eligible)
        self.assertEqual(excluded[0]["missing_core_count"], 2)
        self.assertEqual(excluded[0]["empty_boards"], "coding")
        self.assertIn("board_missing_both", excluded[0]["reason"])

    def test_zero_is_observed_and_nonfinite_or_boolean_values_are_missing(self):
        zero = model("zero", 0)
        eligible, excluded = dual.prepare([zero], dual.DEFAULT_CORE, {})
        self.assertFalse(excluded)
        self.assertEqual(eligible[0]["missing_core_count"], 0)
        for absent in (None, "", float("nan"), float("inf"), float("-inf"), True, False):
            with self.subTest(absent=absent):
                source = model("absent", **{"SciCode": absent})
                eligible, excluded = dual.prepare([source], dual.DEFAULT_CORE, {})
                self.assertFalse(excluded)
                self.assertEqual(eligible[0]["missing_core_count"], 1)
        rows, _, _, _ = dual.score_variant([zero], dual.DEFAULT_CORE, [20]*5, {})
        self.assertEqual(rows[0]["score"], 0)

    def test_half_shares_do_not_redistribute_missing_or_zero(self):
        raw = np.array([[80, 20], [80, np.nan], [80, 0], [np.nan, 80], [0, 0]])
        np.testing.assert_allclose(dual.pair_base(raw), [50, 40, 40, 40, 0])
        with self.assertRaises(ValueError):
            dual.pair_base([80, 20])
        with self.assertRaises(ValueError):
            dual.pair_base([[80, 20, 10]])
        for raw in ([[-1, 50]], [[101, 50]]):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                dual.pair_base(raw)

    def test_terminal_uses_latest_zero_then_calibrated_older_versions(self):
        maps = {key: {"enabled": True, "slope": 0.5, "intercept": -10}
                for key in dual.base.OLD_TB}
        latest = model("latest", **{dual.base.LATEST_TB: 0, dual.base.OLD_TB[0]: 80})
        old = model("old", **{dual.base.LATEST_TB: None, dual.base.OLD_TB[0]: 80,
                               dual.base.OLD_TB[1]: 100})
        hard = model("hard", **{dual.base.LATEST_TB: None, dual.base.OLD_TB[1]: 80})
        eligible, excluded = dual.prepare([latest, old, hard], dual.DEFAULT_CORE, maps)
        self.assertFalse(excluded)
        results = {m["slug"]: m for m in eligible}
        self.assertEqual(results["latest"]["scores"][dual.base.TB], 0)
        self.assertEqual(results["latest"]["terminal_source"], dual.base.LATEST_TB)
        self.assertAlmostEqual(results["old"]["scores"][dual.base.TB], 28.5)
        self.assertEqual(results["old"]["terminal_source"], dual.base.OLD_TB[0])
        self.assertAlmostEqual(results["hard"]["scores"][dual.base.TB], 27)
        self.assertEqual(results["hard"]["terminal_source"], dual.base.OLD_TB[1])
        self.assertTrue(all(m["missing_core_count"] == 0 for m in eligible))

    def test_disabled_terminal_maps_leave_the_slot_missing_without_borrowing(self):
        maps = {key: {"enabled": False} for key in dual.base.OLD_TB}
        high = model("high", **{dual.base.LATEST_TB: None, dual.base.OLD_TB[0]: 95})
        low = model("low", **{dual.base.LATEST_TB: 90})
        high["variantGroup"] = low["variantGroup"] = "family"
        high["variantPriority"], low["variantPriority"] = 100, 40
        selected = dual.base.representatives([low, high])
        eligible, excluded = dual.prepare(selected, dual.DEFAULT_CORE, maps)
        self.assertFalse(excluded)
        self.assertEqual([m["slug"] for m in eligible], ["high"])
        self.assertEqual(eligible[0]["missing_core_count"], 1)
        self.assertIsNone(eligible[0]["scores"][dual.base.TB])

    def test_extensions_remove_core_families_even_under_other_column_names(self):
        core = copy.deepcopy(dual.DEFAULT_CORE)
        core["coding"] = (dual.base.TB, "LiveCodeBench")
        registry = dual.extension_registry(core)
        families = {dual.canonical_family(k) for pair in core.values() for k in pair}
        for board, keys in registry.items():
            with self.subTest(board=board):
                self.assertTrue(families.isdisjoint(dual.canonical_family(k) for k in keys))
                self.assertNotIn("benchmark:livecodebench", keys)
                self.assertNotIn(dual.base.OLD_TB[0], keys)
        self.assertIn("benchmark:swe-bench-pro", registry["coding"])

    def test_incomplete_board_is_not_in_extension_fit_and_gets_no_bonus(self):
        full, _ = dual.prepare(training_models(), dual.DEFAULT_CORE, {})
        calibration = dual.fit_calibration(full, dual.DEFAULT_CORE)
        incomplete = missing(model("incomplete", 40, **{"benchmark:swe-bench-pro": 100}), "SciCode")
        combined, _ = dual.prepare(training_models() + [incomplete], dual.DEFAULT_CORE, {})
        fitted = dual.fit_calibration(combined, dual.DEFAULT_CORE)
        self.assertEqual(fitted["boards"]["coding"], calibration["boards"]["coding"])
        self.assertEqual(fitted["boards"]["coding"]["complete_core_models"], 7)
        self.assertEqual(fitted["boards"]["agentic-tool-work"]["complete_core_models"], 8)
        rows = dual.score_models(combined, dual.DEFAULT_CORE, [20]*5, fitted)
        row = next(r for r in rows if r["slug"] == "incomplete")
        self.assertEqual(row["coding_core"], 20)
        self.assertEqual(row["coding_bonus"], 0)
        self.assertGreater(calibration["cap"], 0)

    def test_fixed_calibration_removing_any_one_core_never_increases_score(self):
        full, _ = dual.prepare(training_models(), dual.DEFAULT_CORE, {})
        calibration = dual.fit_calibration(full, dual.DEFAULT_CORE)
        target = model("target", 40, **{"benchmark:swe-bench-pro": 100})
        before, _ = dual.prepare([target], dual.DEFAULT_CORE, {})
        original = dual.score_models(before, dual.DEFAULT_CORE, [20]*5, calibration)[0]
        self.assertGreater(original["coding_bonus"], 0)
        for board, pair in dual.DEFAULT_CORE.items():
            for key in pair:
                with self.subTest(board=board, key=key):
                    prepared, excluded = dual.prepare([missing(target, key)], dual.DEFAULT_CORE, {})
                    self.assertFalse(excluded)
                    result = dual.score_models(prepared, dual.DEFAULT_CORE, [20]*5, calibration)[0]
                    self.assertLessEqual(result["score"], original["score"])
                    self.assertEqual(result[board + "_core"], 20)
                    self.assertEqual(result[board + "_bonus"], 0)

    def test_weighted_points_are_two_fixed_halves_without_extensions(self):
        source = missing(model("halves", 80), "SciCode")
        weights = [10, 15, 20, 25, 30]
        rows, excluded, calibration, _ = dual.score_variant([source], dual.DEFAULT_CORE, weights, {})
        self.assertFalse(excluded)
        self.assertEqual(calibration["cap"], 0)
        row = rows[0]
        self.assertEqual(row["coding_core"], 40)
        self.assertEqual(row["coding_item1_base_points"], 4)
        self.assertEqual(row["coding_item2_base_points"], 0)
        self.assertIsNone(row["coding_item2_adjusted"])
        self.assertAlmostEqual(row["core_only_score"], 76)
        self.assertAlmostEqual(row["score"], 76)
        self.assertAlmostEqual(sum(row[b + "_points"] for b in dual.BOARDS), row["score"])

    def test_scoring_keeps_source_core_maps_and_calibration_unchanged(self):
        sources = training_models() + [missing(model("incomplete"), "SciCode")]
        core = copy.deepcopy(dual.DEFAULT_CORE)
        maps = {key: {"enabled": False} for key in dual.base.OLD_TB}
        originals = copy.deepcopy((sources, core, maps))
        _, _, calibration, eligible = dual.score_variant(sources, core, [20]*5, maps)
        calibration_before = copy.deepcopy(calibration)
        eligible_before = copy.deepcopy(eligible)
        dual.score_models(eligible, core, [10, 15, 20, 25, 30], calibration)
        self.assertEqual((sources, core, maps), originals)
        self.assertEqual(calibration, calibration_before)
        self.assertEqual(eligible, eligible_before)

    def test_names_providers_and_variant_metadata_do_not_change_scores(self):
        sources = training_models()
        rows, _, _, _ = dual.score_variant(sources, dual.DEFAULT_CORE, [20]*5, {})
        renamed = copy.deepcopy(sources)
        for i, source in enumerate(renamed):
            source.update(slug=f"renamed-{i}", model=f"Different label {i}",
                          creator=f"Provider {i}", variantGroup=f"Group {i}",
                          variantPriority=1000-i)
        changed, _, _, _ = dual.score_variant(renamed, dual.DEFAULT_CORE, [20]*5, {})
        initial = {r["slug"].split("-")[-1]: r for r in rows}
        for row in changed:
            first = initial[row["slug"].split("-")[-1]]
            self.assertEqual(row["score"], first["score"])
            for board in dual.BOARDS:
                self.assertEqual(row[board + "_core"], first[board + "_core"])
                self.assertEqual(row[board + "_bonus"], first[board + "_bonus"])

    def test_empty_population_and_invalid_weights_are_handled(self):
        calibration = dual.fit_calibration([], dual.DEFAULT_CORE)
        self.assertEqual(calibration["population"], 0)
        self.assertEqual(calibration["cap"], 0)
        self.assertEqual(dual.score_models([], dual.DEFAULT_CORE, [20]*5, calibration), [])
        for weights in ([20]*4, [20]*4+[21], [-10, 20, 30, 30, 30], [float("nan"), 25, 25, 25, 25]):
            with self.subTest(weights=weights), self.assertRaises(ValueError):
                dual.score_models([], dual.DEFAULT_CORE, weights, calibration)


if __name__ == "__main__":
    unittest.main()
