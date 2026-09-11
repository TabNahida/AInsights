import copy
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from analysis.irt_leaderboard_exploration import core_variants as cv
from analysis.irt_leaderboard_exploration import aindex_scheme18 as production


def model(slug, group=None, priority=70, **scores):
    return {"slug": slug, "model": slug, "variantGroup": group or slug,
            "variantPriority": priority, "creator": "Lab", "scores": scores,
            "externalBenchmarks": []}


class CoreVariantsTests(unittest.TestCase):
    def test_fallback_is_latest_first_and_does_not_replace_a_real_zero(self):
        scores = {cv.LATEST_TB: 0, cv.OLD_TB[0]: 90, cv.OLD_TB[1]: 95}
        self.assertEqual(cv.terminal_score(scores, "discount", {}), (0, cv.LATEST_TB, 0))
        scores[cv.LATEST_TB] = None
        self.assertEqual(cv.terminal_score(scores, "discount", {}), (85.5, cv.OLD_TB[0], 90))
        scores[cv.OLD_TB[0]] = None
        self.assertEqual(cv.terminal_score(scores, "discount", {}), (85.5, cv.OLD_TB[1], 95))
        self.assertEqual(cv.terminal_score({}, "discount", {}), (None, "missing", None))

    def test_calibrated_fallback_converts_scale_before_discount(self):
        models = [model(str(i), **{cv.OLD_TB[0]: 20 + 10*i, cv.LATEST_TB: 5*i}) for i in range(6)]
        maps = cv.fit_terminal_maps(models)
        self.assertAlmostEqual(maps[cv.OLD_TB[0]]["slope"], 0.5)
        self.assertAlmostEqual(maps[cv.OLD_TB[0]]["intercept"], -10)
        value, origin, raw = cv.terminal_score({cv.OLD_TB[0]: 80}, "calibrated", maps)
        self.assertEqual((value, origin, raw), (28.5, cv.OLD_TB[0], 80))
        self.assertEqual(cv.terminal_score({cv.OLD_TB[0]: 5}, "calibrated", maps)[0], 0)
        self.assertEqual(cv.terminal_score({cv.LATEST_TB: 7, cv.OLD_TB[0]: 80}, "calibrated", maps)[0], 7)

    def test_deduplication_is_score_independent_and_never_borrows_sibling_core(self):
        high = model("high", "family", 100)
        low = model("low", "family", 40, **{cv.LATEST_TB: 90})
        selected = cv.representatives([low, high])
        self.assertEqual([m["slug"] for m in selected], ["high"])
        before = copy.deepcopy(selected)
        variant = {"fallback": "discount", "core": {"coding": (cv.TB,)}}
        eligible, excluded = cv.prepare(selected, variant, {})
        self.assertEqual(eligible, [])
        self.assertEqual(excluded[0]["missing_core"], cv.TB)
        self.assertEqual(selected, before)

    def test_inventory_counts_zero_and_distinguishes_configs_from_groups(self):
        models = [model(str(i), "family", **{"test": 0}) for i in range(100)]
        rows = cv.coverage_inventory(models)
        self.assertEqual(rows[0]["configurations"], 100)
        self.assertEqual(rows[0]["variant_groups"], 1)
        self.assertTrue(rows[0]["at_least_100_configurations"])
        self.assertFalse(rows[0]["at_least_100_groups"])

    def test_inventory_uses_raw_aa_values_not_site_imputation(self):
        payload = {"models": [model("a", **{"LiveCodeBench": 99}), model("b", **{"LiveCodeBench": 50})]}
        models = cv.load_models(payload, [{"slug": "a", "LiveCodeBench": ""},
                                         {"slug": "b", "LiveCodeBench": "0"}])
        self.assertIsNone(models[0]["scores"]["LiveCodeBench"])
        self.assertEqual(models[1]["scores"]["LiveCodeBench"], 0)
        self.assertEqual(payload["models"][0]["scores"]["LiveCodeBench"], 99)

    def test_core_and_terminal_family_never_receive_duplicate_extension_bonus(self):
        registry = cv.extension_registry(cv.VARIANTS["a_broad"]["core"])
        for keys in registry.values():
            self.assertTrue(set(keys).isdisjoint({cv.LATEST_TB, *cv.OLD_TB, "τ³-Banking", "AA-LCR"}))
        self.assertIn("benchmark:swe-bench-pro", registry["coding"])

    def test_five_board_score_with_absent_extensions_is_plain_core_mean(self):
        variant = cv.VARIANTS["b_automation"]
        scores = {key: 25 for keys in variant["core"].values() for key in keys}
        scores[cv.LATEST_TB] = 50
        eligible, _ = cv.prepare([model("a", **scores)], variant, {})
        rows, calibration = cv.score_variant(eligible, variant["core"])
        self.assertAlmostEqual(rows[0]["score"], 30)
        self.assertAlmostEqual(rows[0]["core_only_score"], 30)
        self.assertEqual(calibration["cap"], 0)

    def test_real_run_is_reproducible_and_keeps_production_inputs_and_registry(self):
        inputs = [cv.ROOT / "docs/data/models.json", cv.ROOT / "ArtificialAnalysis/artificialanalysis_raw_scores_wide.csv"]
        before = [hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs]
        original_core = copy.deepcopy(production.CORE_ITEMS)
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            cv.run(*inputs, output)
            first = {p.name: p.read_bytes() for p in output.iterdir()}
            cv.run(*inputs, output)
            self.assertEqual(first, {p.name: p.read_bytes() for p in output.iterdir()})
            common_slugs = []
            for key in cv.VARIANTS:
                with (output / f"rankings_{key}.csv").open(encoding="utf-8") as handle:
                    rows = list(csv.DictReader(handle))
                self.assertTrue(rows)
                self.assertEqual(len(rows), len({r["variant_group"] for r in rows}))
                self.assertEqual([float(r["score"]) for r in rows], sorted([float(r["score"]) for r in rows], reverse=True))
                for row in rows:
                    total = sum(float(row[b + "_score"]) for b in production.BOARD_ORDER) / 5
                    self.assertAlmostEqual(float(row["score"]), total)
                with (output / f"common_{key}.csv").open(encoding="utf-8") as handle:
                    common_slugs.append({r["slug"] for r in csv.DictReader(handle)})
            self.assertTrue(all(slugs == common_slugs[0] for slugs in common_slugs))
            metadata = json.loads((output / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(len(common_slugs[0]), metadata["common_population"])
        self.assertEqual(before, [hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs])
        self.assertEqual(original_core, production.CORE_ITEMS)


if __name__ == "__main__":
    unittest.main()
