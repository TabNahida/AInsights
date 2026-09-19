import copy
import json
import tempfile
import unittest
from pathlib import Path

from benchmarks.vision_evidence import attach_vision_evidence, load_vision_evidence


class VisionEvidenceTests(unittest.TestCase):
    def test_static_script_matches_json_and_contains_attached_vision_evidence(self):
        root = Path(__file__).resolve().parents[1]
        payload = json.loads((root / "docs/data/models.json").read_text(encoding="utf-8"))
        script = (root / "docs/data/models.js").read_text(encoding="utf-8")
        self.assertTrue(script.startswith("window.AINSIGHTS_MODELS_DATA = "))
        self.assertEqual(json.loads(script.split("=", 1)[1].strip().removesuffix(";")), payload)
        expected = copy.deepcopy(payload["models"])
        attach_vision_evidence(expected)
        for actual, model in zip(payload["models"], expected):
            self.assertEqual(actual.get("visionBenchmarks"), model["visionBenchmarks"], model["slug"])

    def test_curated_sources_are_valid_and_all_slugs_exist(self):
        rows = load_vision_evidence()
        payload = json.loads((Path(__file__).resolve().parents[1] / "docs/data/models.json").read_text(encoding="utf-8"))
        slugs = {model["slug"] for model in payload["models"]}
        for row in rows:
            self.assertTrue(row["sourceLocator"])
            self.assertTrue(row["sourceLabel"])
            self.assertTrue(row["reviewedAt"])
            for slug in row["modelSlugs"] + row["referenceSlugs"]:
                self.assertIn(slug, slugs)

    def test_visual_evidence_never_changes_ranking_inputs(self):
        models = [{"slug": "gpt-5-2", "scores": {"MMMU-Pro": None, "CritPt": 30},
                   "rankingProfile": {"score": 40}, "externalBenchmarks": []}]
        before = copy.deepcopy(models[0])
        attach_vision_evidence(models)
        evidence = models[0].pop("visionBenchmarks")
        self.assertEqual(models[0], before)
        self.assertEqual(next(row["value"] for row in evidence if row["benchmarkId"] == "mmmu-pro-no-tools"), 79.5)

    def test_max_effort_results_are_reference_only_for_lower_tiers(self):
        models = [{"slug": "claude-fable-5-1"}, {"slug": "claude-fable-5-1-low"}, {"slug": "claude-fable-5-1-unknown"}]
        attach_vision_evidence(models)
        self.assertTrue(all(row["exactConfiguration"] for row in models[0]["visionBenchmarks"]))
        self.assertEqual(models[0]["visionBenchmarks"][0]["value"], 42.6)
        self.assertTrue(all(not row["exactConfiguration"] for row in models[1]["visionBenchmarks"]))
        self.assertEqual(models[2]["visionBenchmarks"], [])

    def test_shared_external_scores_do_not_become_exact_visual_observations(self):
        base = {"benchmarkId": "mmmu-pro", "value": 80.1, "sourceUrl": "https://example.org/source",
                "sourceLabel": "source", "modelScoreEligible": True, "variantScoped": True}
        models = [{"externalBenchmarks": [base]}, {"externalBenchmarks": [{**base, "sharedFromVariant": True}]}]
        attach_vision_evidence(models, [])
        self.assertTrue(models[0]["visionBenchmarks"][0]["exactConfiguration"])
        self.assertFalse(models[1]["visionBenchmarks"][0]["exactConfiguration"])

    def test_release_snapshots_do_not_inherit_preview_or_older_scores(self):
        slugs = ["gpt-4o-2024-05-13", "gpt-4o", "gpt-4-turbo",
                 "gemini-2-0-flash-lite-preview", "gemini-2-0-flash-lite-001"]
        models = [{"slug": slug} for slug in slugs]
        attach_vision_evidence(models)
        for index in (0, 3):
            self.assertTrue(all(row["exactConfiguration"] for row in models[index]["visionBenchmarks"]))
        for index in (1, 2, 4):
            self.assertTrue(models[index]["visionBenchmarks"])
            self.assertTrue(all(not row["exactConfiguration"] for row in models[index]["visionBenchmarks"]))

    def test_mmmu_variants_and_tool_protocols_remain_separate(self):
        models = [{"slug": "apriel-v1-6-15b-thinker"}, {"slug": "gpt-5-2"}]
        attach_vision_evidence(models)
        apriel = {row["benchmarkId"]: row["value"] for row in models[0]["visionBenchmarks"]}
        self.assertEqual(apriel["mmmu-pro-10-choice"], 60.28)
        self.assertEqual(apriel["mmmu-pro-vision-only"], 52.89)
        self.assertNotIn("mmmu-pro", apriel)
        gpt = {row["benchmarkId"]: row["value"] for row in models[1]["visionBenchmarks"]}
        self.assertNotEqual(gpt["mmmu-pro-no-tools"], gpt["mmmu-pro-tools"])

    def test_invalid_scores_and_duplicate_assignments_fail_validation(self):
        row = copy.deepcopy(load_vision_evidence()[0])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "vision.json"
            for value in [True, -1, 101, float("nan"), None]:
                path.write_text(json.dumps({"results": [{**row, "value": value}]}), encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_vision_evidence(path)
            path.write_text(json.dumps({"results": [row, row]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_vision_evidence(path)
