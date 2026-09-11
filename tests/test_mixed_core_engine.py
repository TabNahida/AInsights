import copy
import unittest

import numpy as np

from analysis.irt_leaderboard_exploration import mixed_core_engine as mixed


def core_fixture():
    return dict(zip(mixed.BOARDS, (
        (mixed.base.LATEST_TB, "SciCode"), ("AutomationBench-AA", "τ³-Banking"),
        ("CritPt", "Humanity's Last Exam"), ("AA-Omniscience Accuracy", "MMMU-Pro"),
        ("AA-LCR v1.1", "GDP.pdf"),
    )))


def model(slug, value=40, **overrides):
    scores = {key: value for pair in core_fixture().values() for key in pair}
    scores.update(overrides)
    return {"slug": slug, "model": slug, "variantGroup": slug,
            "variantPriority": 70, "creator": "Lab", "scores": scores,
            "externalBenchmarks": []}


def training_models():
    return [model(f"training-{index}", **{"benchmark:swe-bench-pro": 10 + 10 * index})
            for index in range(7)]


class MixedCoreEngineTests(unittest.TestCase):
    def test_full_dual_core_matches_every_original_score_and_calibration_value(self):
        core = core_fixture()
        sources = training_models() + [
            model("three-missing", **{"SciCode": None, "CritPt": None, "GDP.pdf": None}),
            model("four-missing", **{"SciCode": None, "CritPt": None, "GDP.pdf": None,
                                     "MMMU-Pro": None}),
            model("empty-coding", **{mixed.base.LATEST_TB: None, "SciCode": None}),
            model("real-zero", 0),
        ]
        for weights in ([20] * 5, [9, 9, 40, 27, 15], [40, 9, 10, 11, 30]):
            with self.subTest(weights=weights):
                old_rows, old_excluded, old_fit, old_models = mixed.dual.score_variant(
                    sources, core, weights, {}, "v4_only")
                rows, excluded, fitted, prepared = mixed.score_variant(sources, core, weights)
                self.assertEqual(len(rows), len(old_rows))
                for row, original in zip(rows, old_rows):
                    for key, value in original.items():
                        self.assertEqual(row[key], value, key)
                self.assertEqual(fitted["cap"], old_fit["cap"])
                self.assertGreater(fitted["cap"], 0)
                self.assertEqual(fitted["boards"], old_fit["boards"])
                self.assertEqual(fitted["population"], old_fit["population"])
                self.assertEqual([m["slug"] for m in prepared], [m["slug"] for m in old_models])
                self.assertEqual([r["slug"] for r in excluded], [r["slug"] for r in old_excluded])
                self.assertTrue(mixed.validate_rows(rows, core, weights)["passed"])

    def test_single_core_takes_whole_domain_and_unconfigured_item_is_not_missing(self):
        core = core_fixture()
        core["coding"] = (mixed.base.LATEST_TB,)
        source = model("single", 80, **{"SciCode": None})
        rows, excluded, fitted, _ = mixed.score_variant([source], core, [10, 15, 20, 25, 30])
        self.assertFalse(excluded)
        self.assertEqual(fitted["cap"], 0)
        row = rows[0]
        self.assertEqual(row["coding_core"], 80)
        self.assertEqual(row["coding_item1_base_points"], 8)
        self.assertEqual(row["coding_core_count"], 1)
        self.assertEqual(row["items_total"], 9)
        self.assertEqual(row["missing_core_count"], 0)
        self.assertEqual(row["score"], 80)
        self.assertNotIn("coding_item2_adjusted", row)
        self.assertTrue(mixed.validate_rows(rows, core, [10, 15, 20, 25, 30])["passed"])

    def test_five_single_core_domains_have_five_observations_and_equal_domain_weights(self):
        core = {board: (keys[0],) for board, keys in core_fixture().items()}
        rows, excluded, _, _ = mixed.score_variant([model("five", 80)], core, [20] * 5)
        self.assertFalse(excluded)
        self.assertEqual(rows[0]["items_total"], 5)
        self.assertEqual(rows[0]["core_only_score"], 80)
        self.assertTrue(all(rows[0][board + "_core_count"] == 1 for board in mixed.BOARDS))
        self.assertTrue(mixed.validate_rows(rows, core, [20] * 5)["passed"])

    def test_missing_single_core_excludes_even_when_every_other_item_is_observed(self):
        core = core_fixture()
        core["coding"] = (mixed.base.LATEST_TB,)
        sources = [model("missing", **{mixed.base.LATEST_TB: None}), model("zero", 0)]
        prepared, excluded = mixed.prepare(sources, core)
        self.assertEqual([m["slug"] for m in prepared], ["zero"])
        self.assertEqual(prepared[0]["missing_core_count"], 0)
        self.assertEqual(excluded[0]["slug"], "missing")
        self.assertEqual(excluded[0]["missing_core_count"], 1)
        self.assertEqual(excluded[0]["empty_boards"], "coding")
        self.assertEqual(excluded[0]["reason"], "board_missing_all")
        rows, _, _, _ = mixed.score_variant(sources, core, [20] * 5)
        self.assertEqual(rows[0]["score"], 0)

    def test_double_core_missing_keeps_half_share_and_four_missing_still_excludes(self):
        core = core_fixture()
        core["coding"] = (mixed.base.LATEST_TB,)
        three = model("three", 80, **{"τ³-Banking": None, "Humanity's Last Exam": None, "MMMU-Pro": None})
        four = model("four", 80, **{**three["scores"], "GDP.pdf": None})
        rows, excluded, _, _ = mixed.score_variant([three, four], core, [20] * 5)
        self.assertEqual([r["slug"] for r in rows], ["three"])
        self.assertEqual(rows[0]["missing_core_count"], 3)
        self.assertEqual(rows[0]["agentic-tool-work_core"], 40)
        self.assertIsNone(rows[0]["agentic-tool-work_item2_adjusted"])
        self.assertEqual(rows[0]["agentic-tool-work_item2_base_points"], 0)
        self.assertEqual(rows[0]["core_only_score"], 56)
        self.assertEqual(excluded[0]["missing_core_count"], 4)
        self.assertEqual(excluded[0]["empty_boards"], "")
        self.assertEqual(excluded[0]["reason"], "missing_at_least_four")

    def test_extension_fitting_and_bonus_need_all_configured_items_only(self):
        double = core_fixture()
        single = {**double, "coding": (mixed.base.LATEST_TB,)}
        target = model("incomplete-pair", **{"SciCode": None, "benchmark:swe-bench-pro": 100})
        old_prepared, _ = mixed.prepare(training_models(), double)
        old_fit = mixed.fit_calibration(old_prepared, double)
        double_rows, _, double_fit, _ = mixed.score_variant(training_models() + [target], double, [20] * 5)
        single_rows, _, single_fit, _ = mixed.score_variant(training_models() + [target], single, [20] * 5)
        self.assertEqual(double_fit["boards"]["coding"], old_fit["boards"]["coding"])
        self.assertEqual(double_fit["boards"]["coding"]["complete_core_models"], 7)
        self.assertEqual(single_fit["boards"]["coding"]["complete_core_models"], 8)
        self.assertEqual(next(r for r in double_rows if r["slug"] == target["slug"])["coding_bonus"], 0)
        self.assertGreater(next(r for r in single_rows if r["slug"] == target["slug"])["coding_bonus"], 0)
        self.assertEqual(mixed.extension_registry(double), mixed.extension_registry(single))

    def test_terminal_cannot_use_old_version_or_stale_effective_score(self):
        core = core_fixture()
        source = model("old-terminal", **{mixed.base.LATEST_TB: None, mixed.base.TB: 99,
                                           mixed.base.OLD_TB[0]: 88, mixed.base.OLD_TB[1]: 91})
        rows, _, _, prepared = mixed.score_variant([source], core, [20] * 5)
        self.assertIsNone(prepared[0]["scores"][mixed.base.TB])
        self.assertIsNone(rows[0]["coding_item1_adjusted"])
        self.assertEqual(rows[0]["terminal_source"], "missing")
        self.assertEqual(rows[0]["coding_core"], 20)
        for mode in ("calibrated", "discount", "invalid"):
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, "v4_only"):
                mixed.prepare([source], core, mode=mode)

    def test_scicode_single_core_cannot_reenable_legacy_terminal_extensions(self):
        core = {**core_fixture(), "coding": ("SciCode",)}
        before = copy.deepcopy(mixed.base.scheme18.EXTENSION_ITEMS)
        registry = mixed.extension_registry(core)
        self.assertTrue(all(mixed.dual.canonical_family(key) != "terminal-bench"
                            for keys in registry.values() for key in keys))
        source = model("scicode-only", **{mixed.base.LATEST_TB: None})
        plain = training_models() + [source]
        with_old = copy.deepcopy(plain)
        for index, item in enumerate(with_old):
            item["scores"][mixed.base.OLD_TB[0]] = 10 * index
            item["scores"][mixed.base.OLD_TB[1]] = 100 - 10 * index
        rows, _, fitted, _ = mixed.score_variant(plain, core, [20] * 5)
        changed, _, changed_fit, _ = mixed.score_variant(with_old, core, [20] * 5)
        self.assertEqual(rows, changed)
        self.assertEqual(fitted, changed_fit)
        self.assertEqual(mixed.base.scheme18.EXTENSION_ITEMS, before)

    def test_registry_rejects_forbidden_families_duplicate_families_and_invalid_counts(self):
        for key in ("AIME 2027", "benchmark:livecodebench", "GPQA Diamond", "HMMT", "MATH-500", "GSM8K"):
            core = core_fixture()
            core["hard-reasoning"] = (key,)
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "Forbidden"):
                mixed.validate_core(core)
        for key in (mixed.base.TB, *mixed.base.OLD_TB, "benchmark:terminal-bench-v2"):
            core = {**core_fixture(), "coding": (key,)}
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "Terminal v4"):
                mixed.validate_core(core)
        invalid = [
            {**core_fixture(), "coding": ()},
            {**core_fixture(), "coding": (mixed.base.LATEST_TB, "SciCode", "Extra")},
            {**core_fixture(), "coding": "SciCode"},
            {**core_fixture(), "hard-reasoning": ("AA-Omniscience Non-Hallucination Rate",)},
            {**core_fixture(), "instruction-context": ("CritPt",)},
            {board: keys for board, keys in core_fixture().items() if board != "coding"},
        ]
        for core in invalid:
            with self.subTest(core=core), self.assertRaises(ValueError):
                mixed.validate_core(core)

    def test_extensions_and_inputs_are_not_mutated_and_banned_core_is_still_an_extension(self):
        sources, core, maps = training_models(), core_fixture(), {"ignored": "v4_only"}
        before = copy.deepcopy((sources, core, maps, mixed.base.scheme18.EXTENSION_ITEMS))
        _, _, fitted, prepared = mixed.score_variant(sources, core, [20] * 5, maps)
        calibration_before, prepared_before = copy.deepcopy((fitted, prepared))
        mixed.score_models(prepared, core, [9, 9, 40, 27, 15], fitted)
        self.assertEqual((sources, core, maps, mixed.base.scheme18.EXTENSION_ITEMS), before)
        self.assertEqual((fitted, prepared), (calibration_before, prepared_before))
        registry = mixed.extension_registry(core)
        self.assertIn("AIME 2025", registry["hard-reasoning"])
        self.assertIn("benchmark:livecodebench", registry["coding"])
        families = {mixed.dual.canonical_family(key) for keys in core.values() for key in keys}
        self.assertTrue(all(families.isdisjoint(mixed.dual.canonical_family(key) for key in keys)
                            for keys in registry.values()))

    def test_empty_population_invalid_weights_and_fixed_share_bounds(self):
        core = core_fixture()
        fitted = mixed.fit_calibration([], core)
        self.assertEqual(fitted["cap"], 0)
        self.assertEqual(mixed.score_models([], core, [20] * 5, fitted), [])
        for weights in ([20] * 4, [20] * 4 + [21], [-1, 20, 20, 20, 41], [float("nan")] * 5):
            with self.subTest(weights=weights), self.assertRaises(ValueError):
                mixed.score_models([], core, weights, fitted)
        np.testing.assert_array_equal(mixed.fixed_share_base([[80], [0], [np.nan]]), [80, 0, 0])
        np.testing.assert_array_equal(mixed.fixed_share_base([[80, np.nan], [80, 0]]), [40, 40])
        for raw in ([80], [[10, 20, 30]], [[-1]], [[101]]):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                mixed.fixed_share_base(raw)

    def test_validation_detects_redistribution_fabricated_second_slot_and_bad_item_points(self):
        core = {**core_fixture(), "coding": (mixed.base.LATEST_TB,)}
        rows, _, _, _ = mixed.score_variant([model("target")], core, [20] * 5)
        corruptions = (
            {"coding_core": 20}, {"coding_item2_adjusted": None},
            {"coding_item1_base_points": 4}, {"items_total": 10},
            {"missing_core_count": 1}, {"coding_points": 0},
        )
        for corruption in corruptions:
            changed = [{**rows[0], **corruption}]
            with self.subTest(corruption=corruption):
                self.assertFalse(mixed.validate_rows(changed, core, [20] * 5)["passed"])


if __name__ == "__main__":
    unittest.main()
