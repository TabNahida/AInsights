import unittest

from benchmarks.collect_benchmark_scores import (
    BENCHMARKS,
    MODEL_ALIASES,
    OFFICIAL_SOURCE_SPECS,
    build_payload,
    official_seed_results_for_source,
    parse_markdown_source_scores,
)
from scripts.build_docs_site import build_site_payload


def source(source_id):
    return next(spec for spec in OFFICIAL_SOURCE_SPECS if spec["id"] == source_id)


class RecentModelReleaseTests(unittest.TestCase):
    def test_deepseek_vision_official_weights_enrich_existing_aa_identity(self):
        collected = build_payload({}, "seeded")
        source_id = "deepseek-v4-flash-vision-exp-card"
        external = {
            "sources": [spec for spec in collected["sources"] if spec["id"] == source_id],
            "benchmarks": [],
            "results": [],
        }
        payload = build_site_payload(
            [{
                "model_key": "DeepSeek V4 Flash Vision (max) [R]",
                "model": "DeepSeek V4 Flash Vision (max)",
                "slug": "deepseek-v4-flash-vision",
                "creator": "DeepSeek",
                "is_reasoning": "true",
                "release_date": "2026-08-21",
                "open_source_categorization": "proprietary",
                "context_window_tokens": "1000000",
                "AA Intelligence Index": "35.0122",
            }],
            external,
            {},
        )

        self.assertEqual(len(payload["models"]), 1)
        model = payload["models"][0]
        self.assertEqual(model["modelKey"], "DeepSeek V4 Flash Vision (max) [R]")
        self.assertEqual(model["model"], "DeepSeek V4 Flash Vision (max)")
        self.assertEqual(model["slug"], "deepseek-v4-flash-vision")
        self.assertEqual(model["releaseDate"], "2026-08-21")
        self.assertEqual(model["aa"]["aa-intelligence"], 35.0122)
        self.assertFalse(model.get("externalOnly", False))
        self.assertEqual(model["openSourceCategorization"], "permissive")
        self.assertEqual(model["openSourceType"], "open")
        self.assertEqual(model["modelDetails"]["license"], "MIT")
        self.assertEqual(model["modelUrl"], "https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-Vision-Exp")
        self.assertEqual(model["contextWindowTokens"], 1048576)
        self.assertEqual(model["inputModalities"], ["Text", "Image"])
        self.assertEqual(model["outputModalities"], ["Text"])
        self.assertEqual(model["officialModelSourceId"], source_id)

    def test_astra_preserves_versions_and_excludes_best_across_efforts_from_ranking(self):
        spec = source("openai-gpt-6-astra-release")
        # The official HTML uses non-breaking hyphens and superscript footnotes.
        html = """
        <table><tr><th>Coding</th><th>GPT‑6 Astra</th><th>GPT‑5.6 Sol</th></tr>
        <tr><td>Terminal-Bench 4.0</td><td>57.9%</td><td>37.3%</td></tr>
        <tr><td>Terminal-Bench 4.1</td><td>99.0%</td><td>99.0%</td></tr>
        <tr><td>FrontierCode 1.1 Extended (score)</td><td>64.5%<sup>8</sup></td><td>60.6%</td></tr>
        <tr><td>ExploitBench</td><td>100.0%</td><td>78.5%</td></tr>
        <tr><td>ExploitBench (June-Aug 2026)</td><td>39.0%</td><td>5.5%</td></tr>
        <tr><td>OSWorld 2.0 (v2026.08.08, offline set, partial score)</td><td>72.6%</td><td>65.7%</td></tr>
        </table>
        """

        rows = parse_markdown_source_scores(html, spec)
        values = {row["benchmarkId"]: row["value"] for row in rows}

        self.assertEqual(values, {
            "terminal-bench-4": 57.9,
            "frontiercode-v1-1-extended": 64.5,
            "exploitbench": 100.0,
            "exploitbench-2026-06-08": 39.0,
            "osworld-2-offline-2026-08-08-partial": 72.6,
        })
        self.assertTrue(all(row["model"] == "GPT-6 Astra" for row in rows))
        for row in rows:
            self.assertFalse(row["modelScoreEligible"])
            self.assertFalse(row["evidenceEligible"])
            self.assertNotIn("effort", row)

    def test_recent_release_metadata_and_reference_scores_reach_model_payload(self):
        collected = build_payload({}, "seeded")
        source_ids = {
            "openai-gpt-6-astra-release",
            "anthropic-claude-fable-5-1-system-card",
            "google-gemini-3-8-flash-card",
            "zai-glm-5-3-flash-release",
        }
        external = {
            "sources": [
                spec for spec in collected["sources"]
                if spec["id"] in source_ids
            ],
            "benchmarks": collected["benchmarks"],
            "results": [
                row for row in collected["results"]
                if row["sourceId"] in source_ids
            ],
        }
        aa_rows = [
            {"model": "GPT-6 Astra (max)", "slug": "gpt-6-astra", "creator": "OpenAI"},
            {"model": "Claude Fable 5.1 (max with fallback)", "slug": "claude-fable-5-1", "creator": "Anthropic"},
            {"model": "Gemini 3.8 Flash (high)", "slug": "gemini-3-8-flash", "creator": "Google"},
            {"model": "Gemini 3.8 Flash (low)", "slug": "gemini-3-8-flash-low", "creator": "Google"},
            {"model": "GLM-5.3-Flash", "slug": "glm-5-3-flash", "creator": "Z AI"},
        ]
        payload = build_site_payload(aa_rows, external, {})
        by_slug = {model["slug"]: model for model in payload["models"]}

        astra = by_slug["gpt-6-astra"]
        self.assertEqual(astra["modelUrl"], "https://openai.com/index/gpt-6-astra/")
        self.assertEqual(astra["officialModelSourceId"], "openai-gpt-6-astra-release")
        self.assertEqual(len(astra["externalBenchmarks"]), 25)
        self.assertTrue(all(not row["modelScoreEligible"] for row in astra["externalBenchmarks"]))
        self.assertTrue(all(astra["scores"].get(row["metricKey"]) is None for row in astra["externalBenchmarks"]))

        fable = by_slug["claude-fable-5-1"]
        self.assertEqual(fable["modelUrl"], "https://www.anthropic.com/claude-fable-and-mythos-5-1")
        self.assertEqual(fable["officialModelSourceId"], "anthropic-claude-fable-5-1-system-card")

        gemini = by_slug["gemini-3-8-flash"]
        self.assertEqual(gemini["officialModelSourceId"], "google-gemini-3-8-flash-card")
        self.assertEqual(gemini["inputModalities"], ["Text", "Image", "Audio", "Video"])
        self.assertEqual(len(gemini["externalBenchmarks"]), 15)
        self.assertEqual(
            sum(row["modelScoreEligible"] for row in gemini["externalBenchmarks"]),
            1,
        )
        self.assertEqual(by_slug["gemini-3-8-flash-low"]["externalBenchmarks"], [])

        glm = by_slug["glm-5-3-flash"]
        self.assertEqual(glm["modelUrl"], "https://docs.z.ai/guides/llm/glm-5.3-flash")
        self.assertEqual(glm["officialModelSourceId"], "zai-glm-5-3-flash-release")
        self.assertEqual(len(glm["externalBenchmarks"]), 6)

    def test_flash_next_preserves_composite_metrics_and_does_not_alias_hosted_flash(self):
        spec = source("qwen-qwen3-8-flash-next-card")
        html = """
        <table><tr><th></th><th>Qwen3.8-Flash-Next</th><th>Qwen3.8-27B</th></tr>
        <tr><td>Frontier agentic tasks Agents' Last Exam</td><td>Pass@1 24.3 Score 51.2</td><td>Pass@1 20.4 Score 42.9</td></tr>
        <tr><td>Multimodal tool use ClawEval-MM</td><td>Pass@3 64.4 Average 60.4</td><td>Pass@3 57.4 Average 56.9</td></tr>
        <tr><td>Computer use OSWorld 2.0</td><td>Binary 19.4 Partial 52.3</td><td>Binary 10.0 Partial 20.0</td></tr>
        <tr><td>Visual math problem solving MathVision</td><td>Without CI 90.6 With CI 95.7</td><td>90.0 / 94.6</td></tr>
        </table>
        """

        rows = parse_markdown_source_scores(html, spec)
        values = {row["benchmarkId"]: row["value"] for row in rows}

        self.assertEqual(values, {
            "agents-last-exam": 51.2, "claw-eval-mm-pass3": 64.4,
            "claw-eval-mm-average": 60.4, "osworld-2": 52.3,
            "mathvision": 90.6, "mathvision-python": 95.7,
        })
        self.assertTrue(all(row["effort"] == "xhigh" for row in rows))
        self.assertTrue(all(row["model"] == "Qwen3.8 Flash-Next" for row in rows))
        self.assertNotIn("Qwen3.8-Flash", MODEL_ALIASES["Qwen3.8 Flash-Next"])
        self.assertNotIn("qwen3-8-flash", MODEL_ALIASES["Qwen3.8 Flash-Next"])

    def test_deepseek_vision_does_not_extend_text_effort_to_multimodal_rows(self):
        spec = source("deepseek-v4-flash-vision-exp-card")
        markdown = """
        | Benchmark | DeepSeek-V4-Flash-Vision-Exp | DeepSeek-V4-Flash-0731 | Opus-4.8 |
        | :--- | :---: | :---: | :---: |
        | Terminal Bench 2.1 | 83.9 | 82.7 | 85.0 |
        | Agents' Last Exam | 27.3 | 25.2† | 25.7 |
        | ZeroBench (Pass@5) | 35.0 | - | 34.0 |
        """

        rows = parse_markdown_source_scores(markdown, spec)
        by_benchmark = {row["benchmarkId"]: row for row in rows}

        self.assertEqual(len(rows), 3)
        self.assertEqual(by_benchmark["terminal-bench-2-1"]["effort"], "max")
        for key in ("agents-last-exam", "zerobench-pass5"):
            self.assertIsNone(by_benchmark[key]["effort"])
            self.assertFalse(by_benchmark[key]["evidenceEligible"])
            self.assertFalse(by_benchmark[key]["modelScoreEligible"])

    def test_glm_flash_keeps_versioned_automation_and_unqualified_agent_metric_separate(self):
        spec = source("zai-glm-5-3-flash-release")
        rows = {row["benchmarkId"]: row for row in official_seed_results_for_source(spec)}

        self.assertEqual(rows["automationbench-v1-0-6"]["value"], 48.8)
        self.assertNotIn("automationbench", rows)
        self.assertEqual(rows["gdpval-aa-v2-elo"]["unit"], "Elo")
        self.assertEqual(rows["terminal-bench-2-1"]["effort"], "max")
        self.assertFalse(rows["agents-last-exam"]["evidenceEligible"])

    def test_new_release_scores_reference_declared_benchmarks(self):
        benchmark_ids = {benchmark["id"] for benchmark in BENCHMARKS}
        for source_id in (
            "openai-gpt-6-astra-release", "qwen-qwen3-8-flash-next-card",
            "zai-glm-5-3-flash-release", "deepseek-v4-flash-vision-exp-card",
        ):
            for row in official_seed_results_for_source(source(source_id)):
                self.assertIn(row["benchmarkId"], benchmark_ids)
                self.assertGreater(len(row["modelAliases"]), 1)


if __name__ == "__main__":
    unittest.main()
