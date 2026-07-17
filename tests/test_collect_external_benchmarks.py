import json
import unittest
from http.client import IncompleteRead
from unittest.mock import patch

from benchmarks.collect_benchmark_scores import (
    build_payload,
    collect_official_sources,
    parse_markdown_source_scores,
    parse_openai_scores,
    retain_previous_results_on_blocked_refresh,
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

    def test_parse_markdown_source_scores_extracts_next_sheet_data(self):
        sheet = {
            "options": {"variant": "sheet"},
            "data": [
                {
                    "benchmark": "Terminal Bench 2.1",
                    "scores": [
                        {"model": "Kimi K3\n(max)", "value": "88.3"},
                        {"model": "GPT 5.5\n(xhigh)", "value": "83.4"},
                    ],
                },
                {
                    "benchmark": "BrowseComp",
                    "scores": [
                        {"model": "Kimi K3\n(max)", "value": "91.2"},
                        {"model": "GPT 5.5\n(xhigh)", "value": "84.4"},
                    ],
                },
            ],
        }
        html = (
            "<script>self.__next_f.push([1,"
            + json.dumps(json.dumps(sheet))
            + "])</script>"
        )
        spec = {
            "id": "kimi-test",
            "label": "Kimi test",
            "url": "https://www.kimi.com/blog/kimi-k3",
            "columns": {
                "Kimi K3 (max)": "Kimi K3",
                "GPT 5.5 (xhigh)": "GPT-5.5",
            },
            "rowLabels": {
                "Terminal Bench 2.1": "terminal-bench-2-1",
                "BrowseComp": "browsecomp",
            },
        }

        rows = parse_markdown_source_scores(html, spec)
        values = {
            (row["model"], row["benchmarkId"]): row["value"]
            for row in rows
        }

        self.assertEqual(values[("Kimi K3", "terminal-bench-2-1")], 88.3)
        self.assertEqual(values[("GPT-5.5", "browsecomp")], 84.4)

    def test_blocked_refresh_retains_last_successful_source_results(self):
        current = {
            "sources": [
                {
                    "id": "official-source",
                    "collectionStatus": "seeded-official-values; refresh blocked: URLError",
                },
                {"id": "fresh-source", "collectionStatus": "refreshed"},
            ],
            "results": [
                {"sourceId": "official-source", "model": "Model A", "benchmarkId": "seed", "value": 1},
                {"sourceId": "fresh-source", "model": "Model B", "benchmarkId": "fresh", "value": 2},
            ],
        }
        previous = {
            "sources": [{"id": "official-source", "collectionStatus": "refreshed"}],
            "results": [
                {"sourceId": "official-source", "model": "Model A", "benchmarkId": "seed", "value": 3},
                {"sourceId": "official-source", "model": "Model A", "benchmarkId": "extra", "value": 4},
                {"sourceId": "fresh-source", "model": "Model B", "benchmarkId": "stale", "value": 5},
            ],
        }

        retained = retain_previous_results_on_blocked_refresh(current, previous)
        result_values = {
            (row["sourceId"], row["benchmarkId"]): row["value"]
            for row in retained["results"]
        }
        statuses = {source["id"]: source["collectionStatus"] for source in retained["sources"]}

        self.assertEqual(result_values[("official-source", "seed")], 3)
        self.assertEqual(result_values[("official-source", "extra")], 4)
        self.assertNotIn(("fresh-source", "stale"), result_values)
        self.assertEqual(statuses["official-source"], "stale-retained; refresh blocked: URLError")
        self.assertEqual(statuses["fresh-source"], "refreshed")

    def test_incomplete_official_response_falls_back_to_seeded_results(self):
        with patch(
            "benchmarks.collect_benchmark_scores.fetch_html",
            side_effect=IncompleteRead(b"partial response"),
        ):
            results, statuses = collect_official_sources(timeout=1)

        self.assertTrue(results)
        self.assertTrue(statuses)
        self.assertTrue(
            all("refresh blocked: IncompleteRead" in status for status in statuses.values())
        )

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
            "kimi-k3-release",
            "kimi-k2-6-card",
            "kimi-k2-7-code-card",
            "kimi-k2-thinking-card",
            "kimi-k2-5-card",
            "zai-glm-4-6-card",
            "zai-glm-5-1-card",
            "zai-glm-5-2-card",
            "minimax-m3-release",
            "minimax-m2-7-report",
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
        minimax_m3_browse = next(
            row
            for row in results
            if row["model"] == "MiniMax-M3" and row["benchmarkId"] == "browsecomp"
        )
        minimax_m27_terminal = next(
            row
            for row in results
            if row["model"] == "MiniMax-M2.7" and row["benchmarkId"] == "terminal-bench-2"
        )
        minimax_m27_gpqa = next(
            row
            for row in results
            if row["model"] == "MiniMax-M2.7" and row["benchmarkId"] == "gpqa-diamond"
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
        self.assertEqual(minimax_m3_browse["value"], 83.5)
        self.assertEqual(minimax_m27_terminal["value"], 57.0)
        self.assertEqual(minimax_m27_gpqa["value"], 89.8)
        self.assertEqual(nemotron_super_lcb["value"], 78.69)
        self.assertEqual(nemotron_nano_aime["value"], 89.06)

    def test_build_payload_includes_gpt56_official_scores(self):
        payload = build_payload({}, "seeded")
        sources = {source["id"]: source for source in payload["sources"]}
        results = {
            (row["model"], row["benchmarkId"]): row
            for row in payload["results"]
            if row["sourceId"] == "openai-gpt-5-6-release"
        }

        self.assertEqual(
            sources["openai-gpt-5-6-release"]["url"],
            "https://openai.com/index/gpt-5-6/",
        )
        self.assertEqual(results[("GPT-5.6 Sol", "swe-bench-pro")]["value"], 64.6)
        self.assertEqual(results[("GPT-5.6 Terra", "terminal-bench-2-1")]["value"], 87.4)
        self.assertEqual(results[("GPT-5.6 Luna", "gpqa-diamond")]["value"], 92.3)
        self.assertEqual(results[("GPT-5.6 Sol", "agents-last-exam")]["value"], 52.7)
        self.assertEqual(results[("GPT-5.6 Terra", "osworld-2")]["value"], 50.2)
        self.assertEqual(results[("GPT-5.6 Luna", "arc-agi-3")]["value"], 0.18)
        self.assertIn("gpt-5-6-sol", results[("GPT-5.6 Sol", "swe-bench-pro")]["modelAliases"])
        self.assertIn("GPT-5.6 Terra (max)", results[("GPT-5.6 Terra", "swe-bench-pro")]["modelAliases"])

        benchmark_ids = {benchmark["id"] for benchmark in payload["benchmarks"]}
        self.assertTrue(
            {
                "agents-last-exam",
                "management-consulting-internal",
                "big-finance-bench",
                "deepswe-v1-1",
                "genebench-pro",
                "lifescibench",
                "medchembench-internal",
                "osworld-2",
                "benchcad",
                "benchcad-python",
                "capture-the-flag",
                "sec-bench-pro",
                "exploitbench",
                "exploitgym",
                "internal-research-debugging",
                "kernelgen-1p",
                "nanogpt",
                "posttrainbench-lite",
                "rsi-index",
                "mmmu-pro-no-tools",
                "mmmu-pro-tools",
                "frontiermath-tier-1-3-v2",
                "frontiermath-tier-4-v2",
                "openai-mrcr-v2-256k-512k",
                "openai-mrcr-v2-512k-1m",
                "graphwalks-bfs-256k-f1",
                "graphwalks-bfs-1m-f1",
                "arc-agi-3",
            }.issubset(benchmark_ids)
        )

        glm52 = next(
            row
            for row in payload["results"]
            if row["model"] == "GLM-5.2" and row["sourceId"] == "zai-glm-5-2-card"
        )
        self.assertIn("glm-5-2-non-reasoning", glm52["modelAliases"])

    def test_build_payload_includes_kimi_k3_official_scores(self):
        payload = build_payload({}, "seeded")
        sources = {source["id"]: source for source in payload["sources"]}
        results = {
            (row["model"], row["benchmarkId"]): row
            for row in payload["results"]
            if row["sourceId"] == "kimi-k3-release"
        }

        self.assertEqual(
            sources["kimi-k3-release"]["url"],
            "https://www.kimi.com/blog/kimi-k3",
        )
        self.assertEqual(results[("Kimi K3", "terminal-bench-2-1")]["value"], 88.3)
        self.assertEqual(results[("Kimi K3", "browsecomp")]["value"], 91.2)
        self.assertEqual(results[("GPT-5.5", "terminal-bench-2-1")]["value"], 83.4)
        self.assertIn("kimi-k3", results[("Kimi K3", "browsecomp")]["modelAliases"])

        benchmark_ids = {benchmark["id"] for benchmark in payload["benchmarks"]}
        self.assertTrue(
            {
                "job-bench",
                "aa-briefcase-elo",
                "officeqa-pro",
                "spreadsheetbench-2",
                "deck-bench-internal",
                "mmmu-pro-python",
                "mathvision",
                "babyvision-python",
                "zerobench-pass5",
                "zerobench-python-pass5",
                "worldvqa-forceanswer",
                "omnidocbench",
                "perceptionbench",
            }.issubset(benchmark_ids)
        )

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
        kimi27_program = next(
            row
            for row in results
            if row["model"] == "Kimi K2.7 Code" and row["benchmarkId"] == "programbench"
        )
        kimi27_mcp_mark = next(
            row
            for row in results
            if row["model"] == "Kimi K2.7 Code" and row["benchmarkId"] == "mcp-mark-verified"
        )
        glm52_deepswe = next(
            row
            for row in results
            if row["model"] == "GLM-5.2" and row["benchmarkId"] == "deepswe"
        )
        glm52_frontierswe = next(
            row
            for row in results
            if row["model"] == "GLM-5.2" and row["benchmarkId"] == "frontierswe-dominance"
        )
        glm52_terminal = next(
            row
            for row in results
            if row["model"] == "GLM-5.2" and row["benchmarkId"] == "terminal-bench-2-1"
        )

        self.assertEqual(fable_swe["value"], 80.3)
        self.assertEqual(qwen3_aime["value"], 85.7)
        self.assertIn("qwen3-235b-a22b-instruct-reasoning", qwen3_aime["modelAliases"])
        self.assertEqual(qwen25_max_gpqa["value"], 60.1)
        self.assertEqual(qwen25_coder_lcb["value"], 35.9)
        self.assertEqual(qwen2_lcb["value"], 35.7)
        self.assertEqual(kimi_0905_terminal["value"], 44.5)
        self.assertEqual(glm46_tau["value"], 75.9)
        self.assertEqual(kimi27_program["value"], 53.6)
        self.assertEqual(kimi27_mcp_mark["value"], 81.1)
        self.assertIn("kimi-k2-7-code", kimi27_program["modelAliases"])
        self.assertEqual(glm52_deepswe["value"], 46.2)
        self.assertEqual(glm52_frontierswe["value"], 74.4)
        self.assertEqual(glm52_terminal["value"], 81.0)
        self.assertIn("GLM-5.2 (max)", glm52_deepswe["modelAliases"])


if __name__ == "__main__":
    unittest.main()
