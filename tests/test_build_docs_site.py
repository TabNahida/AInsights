import unittest
import subprocess
import sys
import tempfile
from pathlib import Path

from scripts.build_docs_site import (
    build_site_payload,
    score_model_for_preset,
    variant_group,
    variant_priority,
    write_site_payload,
)


class BuildDocsSiteTests(unittest.TestCase):
    def test_variant_group_removes_common_strength_suffixes(self):
        self.assertEqual(variant_group("GPT-5.5 (xhigh)", "gpt-5-5"), "gpt 5 5")
        self.assertEqual(variant_group("Claude Opus 4.8 (max)", "claude-opus-4-8"), "claude opus 4 8")
        self.assertEqual(variant_group("GPT-5.5 (Non-reasoning)", "gpt-5-5-non-reasoning"), "gpt 5 5")
        self.assertEqual(variant_group("Gemini 3.5 Flash (minimal)", "gemini-3-5-flash-minimal"), "gemini 3 5 flash")

    def test_variant_priority_prefers_stronger_inference_presets(self):
        self.assertGreater(variant_priority("GPT-5.5 (xhigh)", "gpt-5-5-xhigh"), variant_priority("GPT-5.5 (high)", "gpt-5-5-high"))
        self.assertGreater(variant_priority("GPT-5.5 (high)", "gpt-5-5-high"), variant_priority("GPT-5.5", "gpt-5-5"))
        self.assertGreater(variant_priority("Claude Opus 4.8 (max)", "claude-opus-4-8-max"), variant_priority("Claude Opus 4.8 (xhigh)", "claude-opus-4-8-xhigh"))

    def test_build_site_payload_includes_presets_metrics_and_model_groups(self):
        rows = [
            {
                "model_key": "Model A (high) [R]",
                "model": "Model A (high)",
                "is_reasoning": "true",
                "slug": "model-a-high",
                "creator": "Lab A",
                "input_modality_text": "true",
                "input_modality_image": "true",
                "input_modality_speech": "false",
                "input_modality_video": "",
                "output_modality_text": "true",
                "output_modality_image": "false",
                "output_modality_speech": "false",
                "output_modality_video": "false",
                "context_window_tokens": "128000",
                "median_output_speed": "123.4",
                "Input Price Per 1M Tokens (USD)": "1.25",
                "Output Price Per 1M Tokens (USD)": "5",
                "Cache Hit Price Per 1M Tokens (USD)": "0.5",
                "AA Intelligence Index Cost (USD)": "42.25",
                "AA Intelligence Index Input Cost (USD)": "12.25",
                "AA Intelligence Index Output Cost (USD)": "30",
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
        self.assertGreaterEqual(len(payload["externalSources"]), 5)
        self.assertEqual(payload["externalSources"][0]["id"], "artificial-analysis")
        self.assertIn("url", payload["externalSources"][0])
        self.assertEqual(payload["externalSources"][0]["defaultWeight"], 100)
        self.assertEqual(payload["externalSources"][0]["scoreStatus"], "active")
        self.assertIn("GDPval-AA", payload["externalSources"][0]["relatedMetrics"])
        self.assertIn("relatedMetrics", payload["externalSources"][1])
        self.assertEqual(payload["defaultPreset"], "zhihu-adjusted")
        self.assertIn("GDPval-AA", [metric["key"] for metric in payload["metrics"]])
        self.assertEqual(payload["presets"]["zhihu-adjusted"]["kind"], "weighted-metrics")
        self.assertEqual(payload["presets"]["zhihu-adjusted"]["label"], "AInsights Index")
        self.assertGreater(payload["models"][0]["variantPriority"], payload["models"][1]["variantPriority"])
        self.assertEqual(payload["models"][0]["contextWindowTokens"], 128000)
        self.assertEqual(payload["models"][0]["inputModalities"], ["Text", "Image"])
        self.assertEqual(payload["models"][0]["outputModalities"], ["Text"])
        self.assertEqual(payload["models"][0]["modelDetails"]["modalities"]["input"]["image"], True)
        self.assertEqual(payload["models"][0]["modelDetails"]["modalities"]["output"]["video"], False)
        self.assertEqual(payload["models"][0]["medianOutputSpeed"], 123.4)
        self.assertEqual(payload["models"][0]["pricing"]["inputPerMillionTokensUsd"], 1.25)
        self.assertEqual(payload["models"][0]["pricing"]["outputPerMillionTokensUsd"], 5)
        self.assertEqual(payload["models"][0]["pricing"]["cacheHitPerMillionTokensUsd"], 0.5)
        self.assertEqual(payload["models"][0]["pricing"]["aaIndexCostUsd"], 42.25)
        self.assertEqual(payload["models"][0]["pricing"]["aaIndexInputCostUsd"], 12.25)
        self.assertEqual(payload["models"][0]["pricing"]["aaIndexOutputCostUsd"], 30)

    def test_build_site_payload_adds_aa_logo_icons_and_source_types(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "Open Model",
                    "model": "Open Model",
                    "is_reasoning": "false",
                    "slug": "open-model",
                    "creator": "OpenAI",
                    "open_source_categorization": "Open Weights (Permissive License)",
                    "AA Intelligence Index": "50",
                },
                {
                    "model_key": "Closed Model",
                    "model": "Closed Model",
                    "is_reasoning": "false",
                    "slug": "closed-model",
                    "creator": "Lab B",
                    "open_source_categorization": "Proprietary",
                    "AA Intelligence Index": "40",
                },
                {
                    "model_key": "Unknown Model",
                    "model": "Unknown Model",
                    "is_reasoning": "false",
                    "slug": "unknown-model",
                    "creator": "",
                    "AA Intelligence Index": "30",
                },
            ]
        )

        self.assertEqual(payload["models"][0]["openSourceType"], "open")
        self.assertEqual(payload["models"][1]["openSourceType"], "closed")
        self.assertEqual(payload["models"][2]["openSourceType"], "unknown")
        self.assertEqual(payload["models"][0]["modelIcon"]["src"], "assets/logos/openai_small.svg")
        self.assertEqual(payload["models"][0]["modelIcon"]["title"], "OpenAI")
        self.assertEqual(payload["models"][0]["modelIcon"]["fallbackLabel"], "OAI")
        self.assertEqual(payload["models"][1]["modelIcon"]["src"], "assets/logos/lab-b_small.svg")
        self.assertNotIn("sourceSrc", payload["models"][0]["modelIcon"])
        self.assertEqual(payload["models"][1]["modelIcon"]["label"], "LB")
        self.assertEqual(payload["models"][1]["modelIcon"]["fallbackLabel"], "LB")

    def test_build_site_payload_merges_external_benchmark_scores(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "GPT-5.5 (xhigh) [R]",
                    "model": "GPT-5.5 (xhigh)",
                    "is_reasoning": "true",
                    "slug": "gpt-5-5",
                    "creator": "OpenAI",
                    "creator_logo_small_url": "https://artificialanalysis.ai/img/logos/openai_small.svg",
                    "creator_color": "#1f1f1f",
                    "AA Intelligence Index": "60",
                }
            ],
            {
                "version": 1,
                "sources": [
                    {
                        "id": "official-release",
                        "label": "Official release evals",
                        "url": "https://example.com/evals",
                        "category": "Official",
                    }
                ],
                "benchmarks": [
                    {
                        "id": "terminal-bench-2",
                        "label": "Terminal-Bench 2.0",
                        "category": "Agentic coding",
                        "unit": "%",
                        "icon": "TERM",
                    }
                ],
                "results": [
                    {
                        "benchmarkId": "terminal-bench-2",
                        "benchmarkLabel": "Terminal-Bench 2.0",
                        "model": "GPT-5.5",
                        "modelAliases": ["GPT-5.5 (xhigh)", "gpt-5-5"],
                        "value": 82.7,
                        "unit": "%",
                        "sourceId": "official-release",
                        "sourceUrl": "https://example.com/evals",
                        "sourceLabel": "Official release evals",
                    }
                ],
            },
        )

        model = payload["models"][0]
        self.assertIn("benchmark:terminal-bench-2", [metric["key"] for metric in payload["metrics"]])
        self.assertEqual(model["scores"]["benchmark:terminal-bench-2"], 82.7)
        self.assertEqual(model["externalBenchmarks"][0]["label"], "Terminal-Bench 2.0")
        self.assertEqual(model["modelIcon"]["src"], "assets/logos/openai_small.svg")
        self.assertEqual(model["modelIcon"]["color"], "#1f1f1f")
        self.assertEqual(payload["externalSources"][-1]["scoreStatus"], "benchmark")
        self.assertIn("benchmark:terminal-bench-2", payload["externalSources"][-1]["relatedMetrics"])

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
                    "scripts/build_docs_site.py",
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
            self.assertTrue((tmp / "models.js").exists())

    def test_write_site_payload_also_writes_file_loadable_js(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            input_csv = tmp / "raw.csv"
            output_json = tmp / "models.json"
            output_js = tmp / "models.js"
            input_csv.write_text(
                "model_key,model,is_reasoning,slug,creator,AA Intelligence Index,GDPval-AA\n"
                "Model A,Model A,false,model-a,Lab A,50,80\n",
                encoding="utf-8",
            )

            write_site_payload(input_csv, output_json, output_js)

            content = output_js.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("window.AINSIGHTS_MODELS_DATA = "))
            self.assertIn('"modelRows": 1', content)

    def test_default_score_uses_aa_suite_weights_and_corrected_omniscience_rule(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "Correction Model",
                    "model": "Correction Model",
                    "is_reasoning": "true",
                    "slug": "correction-model",
                    "GDPval-AA": "100",
                    "τ²-Bench Telecom": "0",
                    "Terminal-Bench Hard": "0",
                    "SciCode": "0",
                    "AA-LCR": "0",
                    "AA-Omniscience Accuracy": "80",
                    "AA-Omniscience Non-Hallucination Rate": "0",
                    "IFBench": "0",
                    "Humanity's Last Exam": "0",
                    "GPQA Diamond": "0",
                    "CritPt": "0",
                    "APEX-Agents-AA": "100",
                    "ITBench-AA": "100",
                    "MMMU-Pro": "100",
                    "LiveCodeBench": "100",
                    "AIME 2025": "100",
                }
            ]
        )
        model = payload["models"][0]
        preset = payload["presets"]["zhihu-adjusted"]

        score = score_model_for_preset(model, preset, payload["metrics"])

        self.assertAlmostEqual(preset["weights"]["GDPval-AA"], 100 / 6)
        self.assertAlmostEqual(preset["weights"]["τ²-Bench Telecom"], 25 / 3)
        self.assertAlmostEqual(preset["weights"]["Terminal-Bench Hard"], 100 / 6)
        self.assertAlmostEqual(preset["weights"]["SciCode"], 25 / 3)
        self.assertAlmostEqual(preset["weights"]["AA-LCR"], 6.25)
        self.assertAlmostEqual(preset["weights"]["AA-Omniscience Accuracy"], 12.5)
        self.assertAlmostEqual(preset["weights"]["IFBench"], 6.25)
        self.assertAlmostEqual(preset["weights"]["Humanity's Last Exam"], 12.5)
        self.assertAlmostEqual(preset["weights"]["GPQA Diamond"], 6.25)
        self.assertAlmostEqual(preset["weights"]["CritPt"], 6.25)
        self.assertEqual(preset["weights"].get("AIME 2025", 0), 0)
        self.assertEqual(preset["weights"].get("LiveCodeBench", 0), 0)
        self.assertEqual(preset["weights"].get("MMMU-Pro", 0), 0)
        self.assertEqual(preset["weights"].get("APEX-Agents-AA", 0), 0)
        self.assertEqual(preset["weights"].get("ITBench-AA", 0), 0)
        self.assertEqual(preset["weights"].get("AA-Omniscience Non-Hallucination Rate", 0), 0)
        self.assertAlmostEqual(score["score"], (100 * (100 / 6) + 80 * 12.5) / 100)
        self.assertEqual(score["coverage"], 10)

    def test_aa_presets_include_official_component_weights(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "AA Preset Model",
                    "model": "AA Preset Model",
                    "is_reasoning": "false",
                    "slug": "aa-preset-model",
                    "AA Intelligence Index": "50",
                }
            ]
        )

        intelligence = payload["presets"]["aa-intelligence"]["weights"]
        coding = payload["presets"]["aa-coding"]["weights"]
        agentic = payload["presets"]["aa-agentic"]["weights"]

        self.assertAlmostEqual(intelligence["GDPval-AA"], 100 / 6)
        self.assertAlmostEqual(intelligence["τ²-Bench Telecom"], 25 / 3)
        self.assertAlmostEqual(intelligence["Terminal-Bench Hard"], 100 / 6)
        self.assertAlmostEqual(intelligence["SciCode"], 25 / 3)
        self.assertAlmostEqual(intelligence["AA-Omniscience Accuracy"], 6.25)
        self.assertAlmostEqual(intelligence["AA-Omniscience Non-Hallucination Rate"], 6.25)
        self.assertEqual(coding, {"Terminal-Bench Hard": 50, "SciCode": 50})
        self.assertEqual(agentic, {"GDPval-AA": 50, "τ²-Bench Telecom": 50})

    def test_default_score_counts_missing_suite_metrics_in_denominator(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "Sparse Default Model",
                    "model": "Sparse Default Model",
                    "is_reasoning": "false",
                    "slug": "sparse-default-model",
                    "GPQA Diamond": "84",
                }
            ]
        )
        model = payload["models"][0]
        preset = payload["presets"]["zhihu-adjusted"]

        score = score_model_for_preset(model, preset, payload["metrics"])

        self.assertAlmostEqual(score["score"], 84 * 6.25 / 100)
        self.assertEqual(score["coverage"], 1)

    def test_custom_score_counts_missing_metrics_in_denominator(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "Sparse Model",
                    "model": "Sparse Model",
                    "is_reasoning": "true",
                    "slug": "sparse-model",
                    "GPQA Diamond": "84",
                }
            ]
        )
        model = payload["models"][0]
        preset = payload["presets"]["custom"]

        score = score_model_for_preset(model, preset, payload["metrics"])

        self.assertAlmostEqual(score["score"], 84 * 6.25 / 100)
        self.assertEqual(score["coverage"], 1)


if __name__ == "__main__":
    unittest.main()
