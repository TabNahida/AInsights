import unittest
import subprocess
import sys
import tempfile
from pathlib import Path

from ArtificialAnalysis.build_docs_site import build_site_payload, variant_group


class BuildDocsSiteTests(unittest.TestCase):
    def test_variant_group_removes_common_strength_suffixes(self):
        self.assertEqual(variant_group("GPT-5.5 (xhigh)", "gpt-5-5"), "gpt 5 5")
        self.assertEqual(variant_group("Claude Opus 4.8 (max)", "claude-opus-4-8"), "claude opus 4 8")
        self.assertEqual(variant_group("GPT-5.5 (Non-reasoning)", "gpt-5-5-non-reasoning"), "gpt 5 5")

    def test_build_site_payload_includes_presets_metrics_and_model_groups(self):
        rows = [
            {
                "model_key": "Model A (high) [R]",
                "model": "Model A (high)",
                "is_reasoning": "true",
                "slug": "model-a-high",
                "creator": "Lab A",
                "AA Intelligence Index": "50",
                "AA Coding Index": "60",
                "AA Agentic Index": "70",
                "GDPval-AA": "80",
                "Terminal-Bench Hard": "40",
            },
            {
                "model_key": "Model A (low) [R]",
                "model": "Model A (low)",
                "is_reasoning": "true",
                "slug": "model-a-low",
                "creator": "Lab A",
                "AA Intelligence Index": "45",
                "AA Coding Index": "55",
                "AA Agentic Index": "65",
                "GDPval-AA": "60",
                "Terminal-Bench Hard": "20",
            },
        ]

        payload = build_site_payload(rows)

        self.assertEqual(payload["models"][0]["variantGroup"], "model a")
        self.assertEqual(payload["models"][1]["variantGroup"], "model a")
        self.assertIn("zhihu-adjusted", payload["presets"])
        self.assertIn("aa-intelligence", payload["presets"])
        self.assertIn("aa-coding", payload["presets"])
        self.assertIn("aa-agentic", payload["presets"])
        self.assertEqual(payload["defaultPreset"], "zhihu-adjusted")
        self.assertIn("GDPval-AA", [metric["key"] for metric in payload["metrics"]])

    def test_build_docs_site_runs_when_invoked_by_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            input_csv = tmp / "raw.csv"
            output_json = tmp / "models.json"
            input_csv.write_text(
                "model_key,model,is_reasoning,slug,creator,AA Intelligence Index,GDPval-AA\n"
                "Model A,Model A,false,model-a,Lab A,50,80\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    "ArtificialAnalysis/build_docs_site.py",
                    "--input-csv",
                    str(input_csv),
                    "--output-json",
                    str(output_json),
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output_json.exists())


if __name__ == "__main__":
    unittest.main()
