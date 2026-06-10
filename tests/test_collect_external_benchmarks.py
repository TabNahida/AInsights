import unittest

from benchmarks.collect_benchmark_scores import (
    build_payload,
    parse_markdown_source_scores,
    parse_openai_scores,
)


class ExternalBenchmarkCollectorTests(unittest.TestCase):
    def test_parse_openai_scores_extracts_target_benchmark_rows(self):
        html = """
        <section>
          <h2>Evaluations</h2>
          <p>SWE-Bench Pro (Public) *</p>
          <p>58.6%</p><p>57.7%</p><p>-</p><p>-</p><p>64.3%</p><p>54.2%</p>
          <p>Terminal-Bench 2.0</p>
          <p>82.7%</p><p>75.1%</p><p>-</p><p>-</p><p>69.4%</p><p>68.5%</p>
        </section>
        """

        scores = parse_openai_scores(html)

        self.assertEqual(scores["swe-bench-pro"], [58.6, 57.7, None, None, 64.3, 54.2])
        self.assertEqual(scores["terminal-bench-2"], [82.7, 75.1, None, None, 69.4, 68.5])

    def test_build_payload_emits_per_model_results_with_aliases(self):
        payload = build_payload({"terminal-bench-2": [82.7, None, None, None, None, None]}, "refreshed")
        result = next(row for row in payload["results"] if row["benchmarkId"] == "terminal-bench-2")

        self.assertEqual(payload["sources"][0]["collectionStatus"], "refreshed")
        self.assertEqual(result["value"], 82.7)
        self.assertIn("gpt-5-5", result["modelAliases"])

    def test_parse_markdown_source_scores_extracts_model_columns(self):
        markdown = """
        | Benchmark | Qwen3.5-27B | Qwen3.6-27B |
        | --- | ---: | ---: |
        | SWE-bench Verified | 75.0 | 77.2 |
        | Terminal-Bench 2.0 | 41.6 | 59.3 |
        """
        spec = {
            "id": "qwen-test",
            "label": "Qwen test",
            "url": "https://example.com/qwen",
            "columns": {"Qwen3.5-27B": "Qwen3.5 27B", "Qwen3.6-27B": "Qwen3.6 27B"},
            "rowLabels": {
                "SWE-bench Verified": "swe-bench-verified",
                "Terminal-Bench 2.0": "terminal-bench-2",
            },
        }

        rows = parse_markdown_source_scores(markdown, spec)
        qwen36_swe = next(
            row
            for row in rows
            if row["model"] == "Qwen3.6 27B" and row["benchmarkId"] == "swe-bench-verified"
        )

        self.assertEqual(qwen36_swe["value"], 77.2)
        self.assertIn("qwen3-6-27b", qwen36_swe["modelAliases"])

    def test_parse_markdown_source_scores_falls_back_to_plain_text_rows(self):
        text = """
        SWE-bench Verified 75.0 76.2 52.0 80.9 73.4 77.2
        Terminal-Bench 2.0 41.6 52.5 42.9 59.3 51.5 59.3
        """
        spec = {
            "id": "qwen-test",
            "label": "Qwen test",
            "url": "https://example.com/qwen",
            "columns": {"Qwen3.5-27B": "Qwen3.5 27B", "Qwen3.6-27B": "Qwen3.6 27B"},
            "textColumns": [
                "Qwen3.5-27B",
                "ignored-a",
                "ignored-b",
                "ignored-c",
                "ignored-d",
                "Qwen3.6-27B",
            ],
            "rowLabels": {
                "SWE-bench Verified": "swe-bench-verified",
                "Terminal-Bench 2.0": "terminal-bench-2",
            },
        }

        rows = parse_markdown_source_scores(text, spec)
        terminal = next(
            row
            for row in rows
            if row["model"] == "Qwen3.6 27B" and row["benchmarkId"] == "terminal-bench-2"
        )

        self.assertEqual(terminal["value"], 59.3)

    def test_parse_markdown_source_scores_extracts_html_tables(self):
        html = """
        <table>
          <tr><th>Benchmark</th><th>Gemini 3.1 Pro</th></tr>
          <tr><td>Terminal-Bench 2.0 Agentic terminal coding</td><td>68.5%</td></tr>
          <tr><td>GPQA Diamond Scientific knowledge</td><td>94.3%</td></tr>
        </table>
        """
        spec = {
            "id": "google-test",
            "label": "Google test",
            "url": "https://deepmind.google/models/model-cards/gemini-3-1-pro/",
            "columns": {"Gemini 3.1 Pro": "Gemini 3.1 Pro"},
            "rowLabels": {
                "Terminal-Bench 2.0": "terminal-bench-2",
                "GPQA Diamond": "gpqa-diamond",
            },
        }

        rows = parse_markdown_source_scores(html, spec)
        terminal = next(row for row in rows if row["benchmarkId"] == "terminal-bench-2")
        gpqa = next(row for row in rows if row["benchmarkId"] == "gpqa-diamond")

        self.assertEqual(terminal["value"], 68.5)
        self.assertEqual(gpqa["value"], 94.3)

    def test_build_payload_includes_official_seed_sources(self):
        payload = build_payload({}, "seeded")

        qwen_result = next(
            row
            for row in payload["results"]
            if row["sourceId"] == "qwen-qwen3-6-27b-card"
            and row["model"] == "Qwen3.6 27B"
            and row["benchmarkId"] == "swe-bench-verified"
        )

        self.assertEqual(qwen_result["value"], 77.2)
        self.assertIn("qwen-qwen3-6-27b-card", [source["id"] for source in payload["sources"]])
        self.assertTrue(qwen_result["sourceUrl"].startswith("https://qwen.ai/"))

    def test_top_vendor_sources_prefer_official_pages_over_hugging_face(self):
        payload = build_payload({}, "seeded")
        top_vendor_ids = {
            "anthropic-claude-opus-4-7-release",
            "qwen-qwen3-release",
            "qwen-qwen2-release",
            "qwen-qwen2-5-release",
            "qwen-qwen2-5-coder-release",
            "qwen-qwen2-5-max-release",
            "qwen-qwen3-6-27b-card",
            "qwen-qwen3-6-plus-release",
            "deepseek-v4-pro-card",
            "kimi-k2-6-card",
            "kimi-k2-thinking-card",
            "kimi-k2-5-card",
            "zai-glm-4-6-card",
            "zai-glm-5-1-card",
            "minimax-m2-5-release",
            "minimax-m2-release",
            "minimax-m1-card",
            "google-gemini-3-1-pro-card",
            "google-gemma-4-card",
            "xiaomi-mimo-v2-5-release",
            "anthropic-claude-fable-5-docs",
            "cohere-north-mini-code-card",
            "xai-grok-4-1-fast-release",
            "nvidia-nemotron-3-super-report",
            "nvidia-nemotron-3-nano-report",
            "nvidia-nemotron-3-ultra-report",
        }

        urls = {
            source["id"]: source["url"]
            for source in payload["sources"]
            if source["id"] in top_vendor_ids
        }

        self.assertEqual(set(urls), top_vendor_ids)
        for url in urls.values():
            self.assertNotIn("huggingface.co", url)

    def test_official_hugging_face_model_cards_are_explicit(self):
        payload = build_payload({}, "seeded")
        sources = {source["id"]: source for source in payload["sources"]}

        kimi_0905 = sources["kimi-k2-0905-card"]

        self.assertEqual(kimi_0905["category"], "Official model card")
        self.assertEqual(kimi_0905["url"], "https://huggingface.co/moonshotai/Kimi-K2-Instruct-0905")

    def test_reference_only_model_cards_keep_model_aliases(self):
        payload = build_payload({}, "seeded")
        sources = {source["id"]: source for source in payload["sources"]}

        self.assertIn("north-mini-code-1-0", sources["cohere-north-mini-code-card"]["modelAliases"])
        self.assertEqual(sources["cohere-north-mini-code-card"]["scoreStatus"], "reference")

    def test_official_release_sources_keep_model_aliases(self):
        payload = build_payload({}, "seeded")
        sources = {source["id"]: source for source in payload["sources"]}

        self.assertIn("Claude Fable 5 (with fallback)", sources["anthropic-claude-fable-5-docs"]["modelAliases"])

    def test_build_payload_includes_new_official_vendor_scores(self):
        payload = build_payload({}, "seeded")
        results = payload["results"]

        gemini_terminal = next(
            row
            for row in results
            if row["model"] == "Gemini 3.1 Pro" and row["benchmarkId"] == "terminal-bench-2"
        )
        claude_swe = next(
            row
            for row in results
            if row["model"] == "Claude Opus 4.7" and row["benchmarkId"] == "swe-bench-verified"
        )
        mimo_swe = next(
            row
            for row in results
            if row["model"] == "MiMo-V2.5-Pro" and row["benchmarkId"] == "swe-bench-pro"
        )
        grok_tau = next(
            row
            for row in results
            if row["model"] == "Grok 4.1 Fast" and row["benchmarkId"] == "tau2-bench-telecom"
        )
        nemotron_mmlu = next(
            row
            for row in results
            if row["model"] == "Nemotron 3 Ultra" and row["benchmarkId"] == "mmlu-pro"
        )
        minimax_m25_swe = next(
            row
            for row in results
            if row["model"] == "MiniMax-M2.5" and row["benchmarkId"] == "swe-bench-verified"
        )
        nemotron_super_lcb = next(
            row
            for row in results
            if row["model"] == "NVIDIA Nemotron 3 Super [R]" and row["benchmarkId"] == "livecodebench"
        )
        nemotron_nano_aime = next(
            row
            for row in results
            if row["model"] == "NVIDIA Nemotron 3 Nano [R]" and row["benchmarkId"] == "aime-2025"
        )

        self.assertEqual(gemini_terminal["value"], 68.5)
        self.assertEqual(claude_swe["value"], 87.6)
        self.assertEqual(mimo_swe["value"], 57.2)
        self.assertEqual(grok_tau["value"], 100.0)
        self.assertEqual(nemotron_mmlu["value"], 86.8)
        self.assertEqual(minimax_m25_swe["value"], 80.2)
        self.assertEqual(nemotron_super_lcb["value"], 78.69)
        self.assertEqual(nemotron_nano_aime["value"], 89.06)

    def test_build_payload_includes_fable_and_older_qwen_official_scores(self):
        payload = build_payload({}, "seeded")
        results = payload["results"]

        fable_swe = next(
            row
            for row in results
            if row["model"] == "Claude Fable 5" and row["benchmarkId"] == "swe-bench-pro"
        )
        qwen3_aime = next(
            row
            for row in results
            if row["model"] == "Qwen3 235B [R]" and row["benchmarkId"] == "aime-2024"
        )
        qwen25_max_gpqa = next(
            row
            for row in results
            if row["model"] == "Qwen2.5 Max" and row["benchmarkId"] == "gpqa-diamond"
        )
        qwen25_coder_lcb = next(
            row
            for row in results
            if row["model"] == "Qwen2.5 Coder 7B" and row["benchmarkId"] == "livecodebench"
        )
        qwen2_lcb = next(
            row
            for row in results
            if row["model"] == "Qwen2 72B" and row["benchmarkId"] == "livecodebench"
        )
        kimi_0905_terminal = next(
            row
            for row in results
            if row["model"] == "Kimi K2 0905" and row["benchmarkId"] == "terminal-bench"
        )
        glm46_tau = next(
            row
            for row in results
            if row["model"] == "GLM-4.6" and row["benchmarkId"] == "tau2-bench-weighted"
        )

        self.assertEqual(fable_swe["value"], 80.3)
        self.assertEqual(qwen3_aime["value"], 85.7)
        self.assertIn("qwen3-235b-a22b-instruct-reasoning", qwen3_aime["modelAliases"])
        self.assertEqual(qwen25_max_gpqa["value"], 60.1)
        self.assertEqual(qwen25_coder_lcb["value"], 35.9)
        self.assertEqual(qwen2_lcb["value"], 35.7)
        self.assertEqual(kimi_0905_terminal["value"], 44.5)
        self.assertEqual(glm46_tau["value"], 75.9)


if __name__ == "__main__":
    unittest.main()
