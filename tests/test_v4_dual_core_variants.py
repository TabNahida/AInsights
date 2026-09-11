import copy
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import numpy as np

from analysis.irt_leaderboard_exploration import filtered_dual_core_variants as filtered

dual, base, preferences = filtered.dual, filtered.base, filtered.preferences


def observations(slug, value=60, **scores):
    core = {**dual.DEFAULT_CORE, "coding": (base.LATEST_TB, "SciCode")}
    return {"slug": slug, "model": slug, "creator": "test", "variantGroup": slug,
            "variantPriority": 70, "externalBenchmarks": [],
            "scores": {**{key: value for pair in core.values() for key in pair}, **scores}}


def nine_rule_rows():
    values = (95, 90, 75, 70, 77, 72, 70, 69, 65, 85, 80, 79, 68, 67)
    return [{"slug": slug, "score": value, **{b + suffix: value for b in dual.BOARDS for suffix in ("_score", "_core")}}
            for slug, value in zip(filtered.CURRENT_TARGETS, values)]


class V4DualCoreVariantsTests(unittest.TestCase):
    def test_v4_only_does_not_even_read_legacy_results_or_maps(self):
        class LegacyTrap(dict):
            def get(self, key, default=None):
                if key in base.OLD_TB:
                    raise AssertionError("Legacy score was consulted")
                return super().get(key, default)
        self.assertEqual(base.terminal_score(LegacyTrap(), "v4_only", {}),
                         (None, "missing", None))
        self.assertEqual(base.terminal_score(LegacyTrap({base.LATEST_TB: 0}), "v4_only", {}),
                         (0, base.LATEST_TB, 0))

    def test_missing_v4_keeps_fixed_half_share_and_can_trigger_empty_board(self):
        core = {**dual.DEFAULT_CORE, "coding": (base.LATEST_TB, "SciCode")}
        old = observations("old", **{base.LATEST_TB: None, base.OLD_TB[0]: 99, base.OLD_TB[1]: 99})
        rows, excluded, _, _ = dual.score_variant([old], core, [20]*5, {}, "v4_only")
        self.assertFalse(excluded)
        self.assertEqual(rows[0]["missing_core_count"], 1)
        self.assertEqual(rows[0]["coding_core"], 30)
        self.assertEqual(rows[0]["terminal_source"], "missing")
        self.assertIsNone(rows[0]["terminal_effective"])
        old["scores"]["SciCode"] = None
        rows, excluded, _, _ = dual.score_variant([old], core, [20]*5, {}, "v4_only")
        self.assertFalse(rows)
        self.assertIn("coding", excluded[0]["empty_boards"])

    def test_v4_input_loading_never_fits_legacy_version_maps(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "models.json").write_text("{}", encoding="utf-8")
            (root / "scores.csv").write_text("slug\n", encoding="utf-8")
            with mock.patch.object(base, "load_models", return_value=[]), \
                 mock.patch.object(base, "fit_terminal_maps", side_effect=AssertionError("fit was called")):
                self.assertEqual(dual.load_inputs(root / "models.json", root / "scores.csv",
                                                 terminal_mode="v4_only")[3], {})

    def test_nine_rule_screen_matches_audit_and_each_new_pair_is_required(self):
        rows = nine_rule_rows()
        grid = filtered.weight_grid((10, 20, 30, 40))
        ranked = preferences.weighted_rows(rows, [20]*5)
        audit = preferences.constraint_audit(ranked, **filtered.AUDIT_KWARGS)
        self.assertTrue(audit["passed"])
        self.assertEqual(len(audit["checks"]), 9)
        np.testing.assert_array_equal(filtered.passing_weight_indices(
            rows, grid, targets=filtered.CURRENT_TARGETS, pairs=filtered.CURRENT_PAIRS), np.arange(len(grid)))
        for a, b in filtered.CURRENT_PAIRS[-3:]:
            changed = copy.deepcopy(rows)
            for board in dual.BOARDS:
                changed[a][board + "_score"] = changed[b][board + "_score"] - 1
            audit = preferences.constraint_audit(preferences.weighted_rows(changed, [20]*5), **filtered.AUDIT_KWARGS)
            self.assertFalse(audit["passed"])
            self.assertEqual(filtered.passing_weight_indices(changed, grid,
                targets=filtered.CURRENT_TARGETS, pairs=filtered.CURRENT_PAIRS).tolist(), [])

    def test_any_new_target_missing_fails_and_label_count_is_checked(self):
        rows = nine_rule_rows()
        for slug in filtered.CURRENT_TARGETS[9:]:
            subset = [r for r in rows if r["slug"] != slug]
            self.assertFalse(preferences.constraint_audit(preferences.weighted_rows(subset, [20]*5),
                                                         **filtered.AUDIT_KWARGS)["passed"])
        with self.assertRaises(ValueError):
            preferences.constraint_audit(preferences.weighted_rows(rows, [20]*5), labels=["too short"])

    def test_current_core_never_reuses_terminal_family_as_extension(self):
        core = dict(zip(dual.BOARDS, [options[0] for options in filtered.CORE_OPTIONS]))
        registry = dual.extension_registry(core)
        self.assertIn(base.LATEST_TB, core["coding"])
        self.assertFalse(any(dual.canonical_family(key) == "terminal-bench"
                             for keys in registry.values() for key in keys))
        for legacy in (base.TB, *base.OLD_TB):
            invalid = {**core, "coding": (legacy, "SciCode")}
            with self.assertRaises(ValueError):
                dual.prepare([observations("legacy-core")], invalid, {}, "v4_only")

    def test_old_and_current_gemini_use_the_same_normal_scoring_rules(self):
        old = observations("old-flash")
        old["variantGroup"] = "gemini 3 flash"
        current = observations("current-flash")
        current["variantGroup"] = "gemini 3 8 flash"
        captured = []
        actual = dual.score_variant
        def score(models, *args):
            captured.extend(m["variantGroup"] for m in models)
            return actual(models, *args)
        options = tuple((tuple(pair[0]),) for pair in filtered.CORE_OPTIONS)
        with mock.patch.object(dual, "score_variant", side_effect=score):
            filtered.search_candidates([old, current], {}, options=options,
                                       values=(20,), minimum_population=0)
        self.assertEqual(filtered.EXCLUDED_VARIANT_GROUPS, ())
        self.assertEqual(captured, ["gemini 3 flash", "gemini 3 8 flash"])

    def test_one_core_can_supply_ten_distinct_weight_variants(self):
        core = dict(zip(dual.BOARDS, [options[0] for options in filtered.CORE_OPTIONS]))
        candidates = [{"core": core, "weights": [9, 9, 30+i, 30, 22-i],
                       "distance_from_equal": 40+i, "minimum_margin": 1+i/100,
                       "sensitivity_passing": i, "sensitivity_total": 20}
                      for i in range(11)]
        selected = filtered.select_candidates({"candidates": candidates}, count=10)
        self.assertEqual(len(selected), 10)
        self.assertEqual(len({tuple(c["weights"]) for c, _ in selected}), 10)


if __name__ == "__main__":
    unittest.main()
