import unittest
import math
import subprocess
import sys
import tempfile
from pathlib import Path

from scripts.build_docs_site import (
    DEFAULT_EXTERNAL_BENCHMARKS_JSON,
    DEFAULT_INPUT_CSV,
    build_site_payload,
    load_external_benchmarks,
    read_csv_rows,
    score_model_for_preset,
    variant_group,
    variant_priority,
    weighted_metric_score,
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
                "GDPval-AA v2": "80",
                "Terminal-Bench v2.1": "40",
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
                "GDPval-AA v2": "60",
                "Terminal-Bench v2.1": "20",
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
        self.assertIn("GDPval-AA v2", payload["externalSources"][0]["relatedMetrics"])
        self.assertIn("relatedMetrics", payload["externalSources"][1])
        self.assertEqual(payload["defaultPreset"], "zhihu-adjusted")
        self.assertIn("GDPval-AA v2", [metric["key"] for metric in payload["metrics"]])
        self.assertEqual(payload["presets"]["zhihu-adjusted"]["kind"], "frontier-groups")
        self.assertEqual(payload["presets"]["zhihu-adjusted"]["label"], "AInsights Index")
        self.assertEqual(payload["presets"]["zhihu-adjusted"]["calculation"], "geometric")
        self.assertEqual(payload["presets"]["zhihu-adjusted"]["normalization"], "relative-best")
        self.assertEqual(payload["presets"]["zhihu-adjusted"]["missingPolicy"], "weak-prior")
        self.assertEqual(payload["presets"]["zhihu-adjusted"]["displayScale"], 100)
        self.assertEqual(payload["presets"]["custom"]["normalization"], "relative-best")
        self.assertEqual(payload["metricBaselines"]["GDPval-AA v2"], 80)
        self.assertEqual(payload["scoreBaselines"]["aaIntelligenceMax"], 50)
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
                "model_key,model,is_reasoning,slug,creator,AA Intelligence Index,GDPval-AA v2\n"
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
                "model_key,model,is_reasoning,slug,creator,AA Intelligence Index,GDPval-AA v2\n"
                "Model A,Model A,false,model-a,Lab A,50,80\n",
                encoding="utf-8",
            )

            write_site_payload(input_csv, output_json, output_js)

            content = output_js.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("window.AINSIGHTS_MODELS_DATA = "))
            self.assertIn('"modelRows": 1', content)

    def test_default_score_uses_frontier_capability_boards(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "Coding Only Model",
                    "model": "Coding Only Model",
                    "is_reasoning": "true",
                    "slug": "coding-only-model",
                    "Terminal-Bench v2.1": "100",
                },
                {
                    "model_key": "Balanced Model",
                    "model": "Balanced Model",
                    "is_reasoning": "true",
                    "slug": "balanced-model",
                    "Terminal-Bench v2.1": "100",
                    "Humanity's Last Exam": "100",
                    "AA-Omniscience Accuracy": "100",
                    "IFBench": "100",
                },
            ],
            {
                "version": 1,
                "sources": [],
                "benchmarks": [
                    {"id": "swe-bench-pro", "label": "SWE-Bench Pro", "category": "Agentic coding"},
                ],
                "results": [
                    {
                        "benchmarkId": "swe-bench-pro",
                        "model": "Balanced Model",
                        "modelAliases": ["Balanced Model", "balanced-model"],
                        "value": 100,
                    },
                ],
            },
        )
        coding_model = next(model for model in payload["models"] if model["slug"] == "coding-only-model")
        balanced_model = next(model for model in payload["models"] if model["slug"] == "balanced-model")
        preset = payload["presets"]["zhihu-adjusted"]

        coding_score = score_model_for_preset(
            coding_model,
            preset,
            payload["metrics"],
            payload["metricBaselines"],
            payload["scoreBaselines"]["aaIntelligenceMax"],
        )
        balanced_score = score_model_for_preset(
            balanced_model,
            preset,
            payload["metrics"],
            payload["metricBaselines"],
            payload["scoreBaselines"]["aaIntelligenceMax"],
        )

        self.assertEqual(preset["kind"], "frontier-groups")
        self.assertEqual(preset["displayScale"], 100)
        self.assertEqual(preset["missingPolicy"], "weak-prior")
        self.assertEqual(preset["weakPriorRatio"], 0.34)
        self.assertEqual([group["id"] for group in preset["groups"]], [
            "coding",
            "agentic-tool-work",
            "hard-reasoning",
            "knowledge-science",
            "instruction-context",
        ])
        self.assertEqual([group["weight"] for group in preset["groups"]], [38, 24, 20, 10, 8])
        hard_metrics = {
            metric["key"]: metric["weight"]
            for metric in next(group for group in preset["groups"] if group["id"] == "hard-reasoning")["metrics"]
        }
        self.assertEqual(hard_metrics["benchmark:aime-2026"], 0.4)
        self.assertEqual(hard_metrics["benchmark:hmmt-2026-feb"], 0.4)
        self.assertNotIn("bonusWeights", preset)
        self.assertGreater(balanced_score["score"], coding_score["score"])
        self.assertEqual(coding_score["coverage"], 2)
        self.assertEqual(balanced_score["coverage"], 5)

    def test_default_score_weights_metrics_inside_frontier_boards(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "Leader Model",
                    "model": "Leader Model",
                    "is_reasoning": "true",
                    "slug": "leader-model",
                    "SciCode": "100",
                },
                {
                    "model_key": "Half SciCode Model",
                    "model": "Half SciCode Model",
                    "is_reasoning": "true",
                    "slug": "half-scicode-model",
                    "SciCode": "50",
                },
            ]
        )
        model = next(model for model in payload["models"] if model["slug"] == "half-scicode-model")
        preset = payload["presets"]["zhihu-adjusted"]

        score = score_model_for_preset(
            model,
            preset,
            payload["metrics"],
            payload["metricBaselines"],
            payload["scoreBaselines"]["aaIntelligenceMax"],
        )

        self.assertIsNotNone(score["score"])
        self.assertGreater(score["score"], 0)
        self.assertEqual(score["coverage"], 2)
        self.assertAlmostEqual(score["availableWeight"], 48)

    def test_default_score_fills_missing_livecodebench_from_external_fit(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "Paired Low Model",
                    "model": "Paired Low Model",
                    "is_reasoning": "true",
                    "slug": "paired-low-model",
                    "LiveCodeBench": "25",
                },
                {
                    "model_key": "Paired High Model",
                    "model": "Paired High Model",
                    "is_reasoning": "true",
                    "slug": "paired-high-model",
                    "LiveCodeBench": "75",
                },
                {
                    "model_key": "Fallback Model",
                    "model": "Fallback Model",
                    "is_reasoning": "true",
                    "slug": "fallback-model",
                },
            ],
            {
                "version": 1,
                "sources": [],
                "benchmarks": [
                    {"id": "livecodebench", "label": "LiveCodeBench", "category": "Coding"},
                ],
                "results": [
                    {
                        "benchmarkId": "livecodebench",
                        "model": "Paired Low Model",
                        "modelAliases": ["Paired Low Model"],
                        "value": 50,
                    },
                    {
                        "benchmarkId": "livecodebench",
                        "model": "Paired High Model",
                        "modelAliases": ["Paired High Model"],
                        "value": 100,
                    },
                    {
                        "benchmarkId": "livecodebench",
                        "model": "Fallback Model",
                        "modelAliases": ["Fallback Model"],
                        "value": 80,
                    },
                ],
            },
        )
        paired = next(model for model in payload["models"] if model["slug"] == "paired-low-model")
        fallback = next(model for model in payload["models"] if model["slug"] == "fallback-model")
        preset = payload["presets"]["zhihu-adjusted"]

        score = score_model_for_preset(
            fallback,
            preset,
            payload["metrics"],
            payload["metricBaselines"],
            payload["scoreBaselines"]["aaIntelligenceMax"],
        )

        self.assertEqual(paired["scores"]["LiveCodeBench"], 25)
        self.assertEqual(fallback["scores"]["LiveCodeBench"], 55)
        self.assertAlmostEqual(payload["metricBaselines"]["LiveCodeBench"], 75)
        self.assertIsNotNone(score["score"])
        self.assertEqual(score["coverage"], 1)
        self.assertAlmostEqual(score["availableWeight"], 38)

    def test_external_benchmarks_are_shared_across_model_variants(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "Variant Model",
                    "model": "Variant Model",
                    "is_reasoning": "false",
                    "slug": "variant-model",
                    "creator": "Lab",
                    "AA Intelligence Index": "50",
                },
                {
                    "model_key": "Variant Model [R]",
                    "model": "Variant Model",
                    "is_reasoning": "true",
                    "slug": "variant-model-reasoning",
                    "creator": "Lab",
                    "AA Intelligence Index": "60",
                },
            ],
            {
                "version": 1,
                "sources": [],
                "benchmarks": [{"id": "bench", "label": "Bench", "category": "Reasoning"}],
                "results": [
                    {
                        "benchmarkId": "bench",
                        "benchmarkLabel": "Bench",
                        "model": "Variant Model",
                        "modelAliases": ["Variant Model"],
                        "value": 88,
                        "sourceId": "official",
                        "sourceLabel": "Official",
                        "sourceUrl": "https://example.com",
                    }
                ],
            },
        )

        non_reasoning = next(model for model in payload["models"] if model["slug"] == "variant-model")
        reasoning = next(model for model in payload["models"] if model["slug"] == "variant-model-reasoning")

        self.assertEqual(non_reasoning["scores"]["benchmark:bench"], 88)
        self.assertEqual(reasoning["scores"]["benchmark:bench"], 88)
        self.assertEqual(reasoning["externalBenchmarks"][0]["sourceLabel"], "Official")
        self.assertTrue(reasoning["externalBenchmarks"][0]["sharedFromVariant"])

    def test_default_ranking_uses_coding_and_hard_problem_signal(self):
        payload = build_site_payload(
            read_csv_rows(DEFAULT_INPUT_CSV),
            load_external_benchmarks(DEFAULT_EXTERNAL_BENCHMARKS_JSON),
        )
        preset = payload["presets"]["zhihu-adjusted"]
        scored = []
        for model in payload["models"]:
            score = score_model_for_preset(
                model,
                preset,
                payload["metrics"],
                payload["metricBaselines"],
                payload["scoreBaselines"]["aaIntelligenceMax"],
            )
            if score["score"] is not None:
                scored.append((score["score"], model))
        scored.sort(key=lambda row: (-row[0], row[1]["model"]))
        ranks = {model["slug"]: index + 1 for index, (_, model) in enumerate(scored)}
        scores = {model["slug"]: score for score, model in scored}

        self.assertLess(ranks["claude-opus-4-7"], ranks["gemini-3-1-pro-preview"])
        self.assertLess(ranks["claude-opus-4-8"], ranks["gpt-5-4"])
        self.assertLess(ranks["gemini-3-1-pro-preview"], ranks["deepseek-v4-pro"])
        self.assertLess(ranks["deepseek-v4-pro"], ranks["gemini-3-5-flash"])
        self.assertLess(ranks["qwen3-7-max"], ranks["deepseek-v4-flash"])
        self.assertLess(ranks["kimi-k2-6"], ranks["deepseek-v4-flash"])
        self.assertGreater(ranks["gemini-3-flash-reasoning"], 15)
        self.assertGreater(ranks["glm-4-7"], 40)
        self.assertGreater(scores["claude-opus-4-8"] - scores["gpt-5-4"], 0.1)
        self.assertGreater(scores["claude-opus-4-7"] - scores["gemini-3-1-pro-preview"], 0.03)
        self.assertGreater(scores["gemini-3-1-pro-preview"] - scores["deepseek-v4-pro"], 1.0)
        self.assertGreater(scores["deepseek-v4-pro"] - scores["gemini-3-5-flash"], 1.5)
        self.assertGreater(scores["qwen3-7-max"] - scores["deepseek-v4-flash"], 2.0)
        self.assertGreater(scores["kimi-k2-6"] - scores["deepseek-v4-flash"], 0.5)
        self.assertGreater(scores["deepseek-v4-flash"], scores["glm-4-7"])
        self.assertGreater(scores["qwen3-7-plus"], scores["qwen3-5-397b-a17b"])
        self.assertGreater(scores["qwen3-7-plus"] - scores["qwen3-5-397b-a17b"], 1.0)
        self.assertGreater(scores["claude-opus-4-6-adaptive"], scores["gemini-3-5-flash"])
        self.assertGreater(scores["minimax-m2-5"], scores["minimax-m2-1"])

    def test_qwen36_default_scores_follow_model_tier_order(self):
        payload = build_site_payload(
            read_csv_rows(DEFAULT_INPUT_CSV),
            load_external_benchmarks(DEFAULT_EXTERNAL_BENCHMARKS_JSON),
        )
        preset = payload["presets"]["zhihu-adjusted"]
        scores = {}
        for model in payload["models"]:
            if model["slug"] not in {"qwen3-6-27b", "qwen3-6-plus", "qwen3-6-max"}:
                continue
            score = score_model_for_preset(
                model,
                preset,
                payload["metrics"],
                payload["metricBaselines"],
                payload["scoreBaselines"]["aaIntelligenceMax"],
            )
            scores[model["slug"]] = score["score"]
            self.assertNotIn("presetMetricFallbacks", model)

        self.assertGreater(scores["qwen3-6-plus"], scores["qwen3-6-27b"])
        self.assertGreater(scores["qwen3-6-max"], scores["qwen3-6-plus"])

    def test_default_score_discounts_sparse_regular_coverage(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "Sparse GPQA Model",
                    "model": "Sparse GPQA Model",
                    "is_reasoning": "true",
                    "slug": "sparse-gpqa-model",
                    "SciCode": "100",
                },
                {
                    "model_key": "Broad Suite Model",
                    "model": "Broad Suite Model",
                    "is_reasoning": "true",
                    "slug": "broad-suite-model",
                    "SciCode": "70",
                    "Terminal-Bench Hard": "70",
                    "LiveCodeBench": "70",
                    "Humanity's Last Exam": "70",
                    "GPQA Diamond": "70",
                    "AIME 2025": "70",
                },
            ]
        )
        preset = payload["presets"]["zhihu-adjusted"]
        sparse = next(model for model in payload["models"] if model["slug"] == "sparse-gpqa-model")
        broad = next(model for model in payload["models"] if model["slug"] == "broad-suite-model")

        sparse_score = score_model_for_preset(
            sparse,
            preset,
            payload["metrics"],
            payload["metricBaselines"],
            payload["scoreBaselines"]["aaIntelligenceMax"],
        )
        broad_score = score_model_for_preset(
            broad,
            preset,
            payload["metrics"],
            payload["metricBaselines"],
            payload["scoreBaselines"]["aaIntelligenceMax"],
        )

        self.assertGreater(broad_score["score"], sparse_score["score"])
        self.assertLess(sparse_score["score"], 70)
        self.assertEqual(sparse_score["coverage"], 2)

    def test_weighted_metric_score_supports_geometric_mean(self):
        model = {"scores": {"A": 100, "B": 25}}

        score = weighted_metric_score(
            model,
            {"A": 1, "B": 1},
            False,
            method="geometric",
        )

        self.assertAlmostEqual(score["score"], math.sqrt(101 * 26) - 1)
        self.assertEqual(score["coverage"], 2)

    def test_weighted_metric_score_supports_relative_best_normalization(self):
        model = {"scores": {"A": 50, "B": 25}}

        score = weighted_metric_score(
            model,
            {"A": 1, "B": 1},
            False,
            method="arithmetic",
            normalization="relative-best",
            metric_baselines={"A": 100, "B": 50},
            display_scale=90,
        )

        self.assertAlmostEqual(score["score"], 45)
        self.assertEqual(score["coverage"], 2)

    def test_weighted_metric_score_supports_custom_missing_policies(self):
        model = {"scores": {"A": 100}}

        coverage_discount = weighted_metric_score(
            model,
            {"A": 1, "B": 1},
            True,
            method="geometric",
            normalization="relative-best",
            metric_baselines={"A": 100, "B": 100},
            display_scale=100,
            missing_policy="coverage-discount",
            coverage_discount_exponent=0.5,
        )
        weak_prior = weighted_metric_score(
            model,
            {"A": 1, "B": 1},
            True,
            method="geometric",
            normalization="relative-best",
            metric_baselines={"A": 100, "B": 100},
            display_scale=100,
            missing_policy="weak-prior",
            weak_prior_ratio=0.35,
        )

        self.assertAlmostEqual(coverage_discount["score"], 100 * (1 / 2) ** 0.5)
        self.assertEqual(coverage_discount["coverage"], 1)
        self.assertAlmostEqual(weak_prior["score"], (math.sqrt(2 * 1.35) - 1) * 100)
        self.assertEqual(weak_prior["coverage"], 1)

    def test_default_score_uses_relative_best_then_aa_intelligence_scale(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "Leader Model",
                    "model": "Leader Model",
                    "is_reasoning": "true",
                    "slug": "leader-model",
                    "AA Intelligence Index": "90",
                    "GDPval-AA v2": "100",
                },
                {
                    "model_key": "Ratio Model",
                    "model": "Ratio Model",
                    "is_reasoning": "true",
                    "slug": "ratio-model",
                    "AA Intelligence Index": "60",
                    "GDPval-AA v2": "50",
                },
            ]
        )
        model = next(model for model in payload["models"] if model["slug"] == "ratio-model")
        preset = payload["presets"]["zhihu-adjusted"]

        score = score_model_for_preset(
            model,
            preset,
            payload["metrics"],
            payload["metricBaselines"],
            payload["scoreBaselines"]["aaIntelligenceMax"],
        )

        self.assertIsNone(score["score"])
        self.assertEqual(score["coverage"], 0)

    def test_geometric_weighted_score_penalizes_missing_without_collapsing_to_zero(self):
        model = {"scores": {"A": 100}}

        score = weighted_metric_score(
            model,
            {"A": 1, "B": 1},
            False,
            method="geometric",
        )

        self.assertAlmostEqual(score["score"], math.sqrt(101) - 1)
        self.assertEqual(score["coverage"], 1)

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

        self.assertAlmostEqual(intelligence["GDPval-AA v2"], 20)
        self.assertAlmostEqual(intelligence["τ³-Banking"], 14)
        self.assertAlmostEqual(intelligence["Terminal-Bench v2.1"], 16)
        self.assertAlmostEqual(intelligence["SciCode"], 8)
        self.assertAlmostEqual(intelligence["AA-LCR"], 6)
        self.assertAlmostEqual(intelligence["AA-Omniscience Accuracy"], 8)
        self.assertAlmostEqual(intelligence["AA-Omniscience Non-Hallucination Rate"], 4)
        self.assertAlmostEqual(intelligence["Humanity's Last Exam"], 12)
        self.assertAlmostEqual(intelligence["GPQA Diamond"], 6)
        self.assertAlmostEqual(intelligence["CritPt"], 6)
        self.assertEqual(coding, {"Terminal-Bench v2.1": 200 / 3, "SciCode": 100 / 3})
        self.assertEqual(agentic, {"GDPval-AA v2": 1000 / 17, "τ³-Banking": 700 / 17})

    def test_default_score_uses_frontier_board_coverage(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "Sparse Default Model",
                    "model": "Sparse Default Model",
                    "is_reasoning": "false",
                    "slug": "sparse-default-model",
                    "SciCode": "84",
                }
            ]
        )
        model = payload["models"][0]
        preset = payload["presets"]["zhihu-adjusted"]

        score = score_model_for_preset(
            model,
            preset,
            payload["metrics"],
            payload["metricBaselines"],
            payload["scoreBaselines"]["aaIntelligenceMax"],
        )

        self.assertIsNotNone(score["score"])
        self.assertEqual(score["coverage"], 2)
        self.assertAlmostEqual(score["availableWeight"], 48)

    def test_custom_score_uses_geometric_coverage_discount_by_default(self):
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

        score = score_model_for_preset(
            model,
            preset,
            payload["metrics"],
            payload["metricBaselines"],
            payload["scoreBaselines"]["aaIntelligenceMax"],
        )

        self.assertEqual(preset["calculation"], "geometric")
        self.assertEqual(preset["missingPolicy"], "coverage-discount")
        available_weight = preset["weights"]["GPQA Diamond"]
        total_weight = sum(weight for weight in preset["weights"].values() if weight > 0)
        expected = 100 * (available_weight / total_weight) ** 0.25
        self.assertAlmostEqual(score["score"], expected)
        self.assertEqual(score["coverage"], 1)


if __name__ == "__main__":
    unittest.main()
