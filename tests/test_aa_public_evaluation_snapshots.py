import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import benchmarks.aa_public_evaluation_snapshots as aa_snapshots
from benchmarks.aa_public_evaluation_snapshots import (
    METRICS,
    SNAPSHOT_PATH,
    extract_page_rows,
    load_aa_difficult_snapshots,
)


class AAPublicEvaluationSnapshotTests(unittest.TestCase):
    def test_flight_data_extracts_exact_selected_model_score(self):
        model = {
            "slug": "example-max",
            "name": "Example (max)",
            "analystAgent": 0.125,
            "analystAgentPassAt1": 0.5,
            "briefcaseBreakdown": {"rubricPassRate": 0.25, "elo": 1500},
        }
        inner = ["$", "div", None, {"children": {"initialModels": [model]}}]
        script = "self.__next_f.push(" + json.dumps([1, "d:" + json.dumps(inner)]) + ")"
        html = f"<html><script>{script}</script></html>"
        self.assertEqual(
            extract_page_rows(html, ("analystAgent",), 1),
            [{"aaSlug": "example-max", "aaName": "Example (max)", "scoreFraction": 0.125}],
        )
        self.assertEqual(
            extract_page_rows(html, ("briefcaseBreakdown", "rubricPassRate"), 1)[0]["scoreFraction"],
            0.25,
        )

    def test_selected_chart_rejects_larger_decoy_and_ambiguous_equal_size(self):
        selected = [{"slug": "selected", "name": "Selected", "analystAgent": 0.25}]
        decoy = [
            {"slug": "decoy-a", "name": "Decoy A", "analystAgent": 0.8},
            {"slug": "decoy-b", "name": "Decoy B", "analystAgent": 0.9},
        ]

        def page(*model_sets):
            inner = {"charts": [{"initialModels": models} for models in model_sets]}
            script = "self.__next_f.push(" + json.dumps([1, "d:" + json.dumps(inner)]) + ")"
            return f"<html><script>{script}</script></html>"

        self.assertEqual(extract_page_rows(page(selected, decoy), ("analystAgent",), 1)[0]["aaSlug"], "selected")
        with self.assertRaisesRegex(ValueError, "changed from 3 rows"):
            extract_page_rows(page(selected, decoy), ("analystAgent",), 3)
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            extract_page_rows(page(selected, decoy[:1]), ("analystAgent",), 1)

    def test_snapshots_use_strict_native_metrics_and_exact_models(self):
        snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        site = json.loads((Path(__file__).resolve().parents[1] / "docs/data/models.json").read_text(encoding="utf-8"))
        model_keys = {model["modelKey"] for model in site["models"]}
        pairs = load_aa_difficult_snapshots()
        self.assertEqual(len(pairs), len(METRICS))
        by_id = {metric["benchmarkId"]: metric for metric in snapshot["metrics"]}
        for spec, (source, results) in zip(METRICS, pairs, strict=True):
            self.assertEqual(source["url"], spec["url"])
            self.assertEqual(source["snapshotRows"], len(by_id[spec["id"]]["rows"]))
            self.assertEqual(source["mappedRows"], len(results))
            self.assertGreaterEqual(len(results), 9)
            for row in results:
                self.assertEqual(row["benchmarkId"], spec["id"])
                self.assertIn(row["model"], model_keys)
                self.assertEqual(row["modelAliases"], [row["model"]])
                self.assertTrue(row["variantScoped"])
                self.assertTrue(0 <= row["value"] <= 100)
                self.assertEqual(row["scoreSelection"], ".".join(spec["field"]))
        briefcase = next(rows for source, rows in pairs if rows[0]["benchmarkId"] == "aa-briefcase-rubric-pass-rate")
        harvey = next(rows for source, rows in pairs if rows[0]["benchmarkId"] == "harvey-lab-aa-all-pass-rate")
        self.assertAlmostEqual(max(row["value"] for row in briefcase), 61.51515151515151)
        self.assertAlmostEqual(max(row["value"] for row in harvey), 30.833333333333336)

    def test_snapshot_rejects_aa_raw_configuration_drift(self):
        snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        by_slug = {
            row["aaSlug"]: row["siteModelKey"]
            for metric in snapshot["metrics"]
            for row in metric["rows"]
            if row["siteModelKey"] is not None
        }
        first_slug = snapshot["metrics"][0]["rows"][0]["aaSlug"]
        by_slug[first_slug] = "Other model configuration [R]"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "aa_raw.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["slug", "model_key"])
                writer.writeheader()
                writer.writerows({"slug": slug, "model_key": key} for slug, key in by_slug.items())
            with patch.object(aa_snapshots, "AA_RAW_SCORES_PATH", path):
                with self.assertRaisesRegex(ValueError, f"configuration drift for {first_slug}"):
                    load_aa_difficult_snapshots()


if __name__ == "__main__":
    unittest.main()
