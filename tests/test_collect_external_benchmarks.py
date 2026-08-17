import json
import unittest
from http.client import IncompleteRead
from unittest.mock import patch
from uuid import UUID

from benchmarks.collect_benchmark_scores import (
    OFFICIAL_SOURCE_SPECS,
    build_payload,
    collect_official_sources,
    discovered_model_card_specs,
    discovered_vendor_page_specs,
    fetch_official_source_text,
    parse_markdown_source_scores,
    parse_openai_scores,
    retain_previous_results_on_blocked_refresh,
)


class ExternalBenchmarkCollectorTests(unittest.TestCase):
    @patch("benchmarks.collect_benchmark_scores.fetch_html")
    def test_qwen_article_api_selects_matching_article_and_sends_request_id(self, fetch):
        spec = next(
            source
            for source in OFFICIAL_SOURCE_SPECS
            if source["id"] == "qwen-qwen3-8-max-release"
        )
        fetch.return_value = json.dumps(
            {
                "data": {
                    "articles": [
                        {"path": "unrelated", "content": "wrong article"},
                        {"path": "qwen3.8", "content": "target benchmark table"},
                    ]
                }
            }
        )

        text = fetch_official_source_text(spec, timeout=7)

        self.assertEqual(text, "target benchmark table")
        _, kwargs = fetch.call_args
        self.assertEqual(kwargs["timeout"], 7)
        self.assertEqual(kwargs["headers"]["Accept"], "application/json")
        UUID(kwargs["headers"]["X-Request-Id"])

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

    def test_qwen38_composite_cells_use_the_declared_semantic_component(self):
        spec = next(
            source
            for source in OFFICIAL_SOURCE_SPECS
            if source["id"] == "qwen-qwen3-8-max-release"
        )
        markdown = """
        | Benchmark | Qwen3.8-Max |
        | --- | ---: |
        | Agents' Last Exam (Pass / Score) | 27.0 / 52.4 |
        | MathVision | 95.2 / 97.7 |
        | BabyVision | 82.0 / 91.3 |
        | ZeroBench (Pass@5) | 24.0 / 49.0 |
        | OSWorld 2.0 | 19.4 / 46.7 |
        | HLE | 43.6 |
        | HLE-VL (w/ Tools) | 52.2 |
        | CharXiv (RQ) | 88.4 / 93.5 |
        """

        rows = parse_markdown_source_scores(markdown, spec)
        values = {row["benchmarkId"]: row["value"] for row in rows}

        self.assertEqual(
            values,
            {
                "agents-last-exam": 52.4,
                "mathvision": 95.2,
                "mathvision-python": 97.7,
                "babyvision-python": 91.3,
                "zerobench-pass5": 24.0,
                "zerobench-python-pass5": 49.0,
                "osworld-2": 46.7,
                "hle": 43.6,
                "charxiv-no-tools": 88.4,
                "charxiv-tools": 93.5,
            },
        )
        self.assertIn(
            "second value",
            next(row for row in rows if row["benchmarkId"] == "agents-last-exam")[
                "scoreSelection"
            ],
        )

    def test_qwen38_composite_cell_with_unexpected_arity_is_not_ingested(self):
        spec = next(
            source
            for source in OFFICIAL_SOURCE_SPECS
            if source["id"] == "qwen-qwen3-8-max-release"
        )
        rows = parse_markdown_source_scores(
            """
            | Benchmark | Qwen3.8-Max |
            | --- | ---: |
            | OSWorld 2.0 | 19.4 / 46.7 / 99.9 |
            """,
            spec,
        )

        self.assertEqual(rows, [])

    def test_qwen38_27b_card_parses_labeled_composite_cells(self):
        spec = next(
            source
            for source in OFFICIAL_SOURCE_SPECS
            if source["id"] == "qwen-qwen3-8-27b-card"
        )
        html = """
        <table>
          <tr><th></th><th>Qwen3.8-27B</th></tr>
          <tr><td>Agents' Last Exam</td><td>Pass@1 20.4 Score 42.9</td></tr>
          <tr><td>ClawEval-MM</td><td>Pass@3 57.4 Average 56.9</td></tr>
          <tr><td>MathVision</td><td>Without CI 90.0 With CI 94.6</td></tr>
        </table>
        """

        rows = parse_markdown_source_scores(html, spec)
        values = {row["benchmarkId"]: row["value"] for row in rows}

        self.assertEqual(values["agents-last-exam"], 42.9)
        self.assertEqual(values["claw-eval-mm-pass3"], 57.4)
        self.assertEqual(values["claw-eval-mm-average"], 56.9)
        self.assertEqual(values["mathvision"], 90.0)
        self.assertEqual(values["mathvision-python"], 94.6)

    def test_discovered_future_vendor_card_uses_reviewed_benchmarks_only(self):
        manifest = {
            "models": [
                {
                    "vendor": "glm",
                    "organization": "zai-org",
                    "modelId": "zai-org/GLM-6",
                    "name": "GLM-6",
                    "displayName": "GLM-6",
                    "url": "https://huggingface.co/zai-org/GLM-6",
                    "rawUrl": "https://huggingface.co/zai-org/GLM-6/raw/abc/README.md",
                    "createdAt": "2027-01-01T00:00:00Z",
                    "lastModified": "2027-01-01T00:00:00Z",
                    "revision": "abc",
                    "tags": ["eval-results", "license:apache-2.0"],
                    "aliases": ["GLM-6", "zai-org/GLM-6", "glm-6"],
                }
            ]
        }

        specs = discovered_model_card_specs(manifest)

        self.assertEqual(len(specs), 1)
        spec = specs[0]
        self.assertEqual(spec["id"], "hf-zai-org-glm-6-card")
        self.assertTrue(spec["autoDiscovered"])
        self.assertTrue(spec["variantScoped"])
        self.assertTrue(spec["exactBenchmarkLabelsOnly"])
        self.assertEqual(spec["tags"], ["eval-results", "license:apache-2.0"])
        rows = parse_markdown_source_scores(
            """
            | Benchmark | GLM-6 |
            | --- | ---: |
            | GPQA Diamond | 95.0 |
            | τ-Bench | 63.0 |
            | τ-Bench Airline | 64.0 |
            | τ²-Bench Airline | 65.0 |
            | GDPval-AA v2 | 1666 |
            | SuperGPQA | 71.4 |
            | VitaBench | 76.2 |
            | LVBench | 82.1 |
            | Brand New Unreviewed Eval | 99.0 |
            """,
            spec,
        )
        self.assertEqual(
            [(row["benchmarkId"], row["value"]) for row in rows],
            [
                ("gpqa-diamond", 95.0),
                ("tau-bench", 63.0),
                ("tau-bench-airline", 64.0),
                ("tau2-bench-airline", 65.0),
                ("gdpval-aa-v2-elo", 1666.0),
            ],
        )

    def test_discovered_future_vendor_pages_become_conservative_source_specs(self):
        manifest = {
            "pages": [
                {
                    "vendor": "qwen",
                    "name": "Qwen4-Max",
                    "displayName": "Qwen4 Max",
                    "url": "https://qwen.ai/blog?id=qwen4",
                    "rawUrl": (
                        "https://qwen.ai/api/v2/article/retrieval?"
                        "language=en-US&path=qwen4&type=qwen_ai"
                    ),
                    "aliases": ["Qwen4 Max", "Qwen4-Max", "qwen4-max"],
                    "sourceKey": "qwen-article-json",
                    "sourceMetadata": {
                        "path": "qwen4",
                        "publishedAt": "2027-01-02T03:04:05+08:00",
                    },
                },
                {
                    "vendor": "glm",
                    "name": "GLM-6",
                    "displayName": "GLM-6",
                    "url": "https://docs.z.ai/guides/llm/glm-6",
                    "rawUrl": "https://docs.z.ai/guides/llm/glm-6.md",
                    "aliases": ["GLM-6", "glm-6"],
                    "sourceKey": "glm-docs-llms",
                },
                {
                    "vendor": "kimi",
                    "name": "Kimi K4",
                    "displayName": "Kimi K4",
                    "url": "https://www.kimi.com/blog/kimi-k4",
                    "rawUrl": "https://www.kimi.com/blog/kimi-k4",
                    "aliases": ["Kimi K4", "kimi-k4"],
                    "sourceKey": "kimi-blog-sitemap",
                },
                {
                    "vendor": "deepseek",
                    "name": "DeepSeek-V5",
                    "displayName": "DeepSeek V5",
                    "url": "https://api-docs.deepseek.com/news/news270101",
                    "rawUrl": "https://api-docs.deepseek.com/news/news270101",
                    "aliases": ["DeepSeek V5", "DeepSeek-V5", "deepseek-v5"],
                    "sourceKey": "deepseek-api-docs-sitemap",
                },
            ]
        }

        specs = discovered_vendor_page_specs(manifest, curated_specs=[])

        self.assertEqual(len(specs), 4)
        self.assertTrue(all(spec["autoDiscoveredVendorPage"] for spec in specs))
        self.assertTrue(all(spec["addModelIfMissing"] for spec in specs))
        self.assertTrue(all(spec["exactBenchmarkLabelsOnly"] for spec in specs))
        qwen = next(spec for spec in specs if spec["vendor"] == "qwen")
        self.assertEqual(qwen["jsonArticleSelector"], {"path": "qwen4"})
        self.assertTrue(qwen["allowAttachedFootnoteLabels"])
        self.assertEqual(qwen["modelMetadata"]["releaseDate"], "2027-01-02")
        self.assertEqual(qwen["modelMetadata"]["creator"], "Alibaba")
        qwen_rows = parse_markdown_source_scores(
            """
            | Benchmark | Qwen4 Max |
            | --- | ---: |
            | Tau² Bench 4 | 82.1 |
            | Vita Bench | 40.9 |
            """,
            qwen,
        )
        self.assertEqual(
            [(row["benchmarkId"], row["value"]) for row in qwen_rows],
            [("tau2-bench-weighted", 82.1)],
        )

        glm = next(spec for spec in specs if spec["vendor"] == "glm")
        rows = parse_markdown_source_scores(
            """
            | Benchmark | GLM-6 |
            | --- | ---: |
            | GPQA Diamond | 95.0 |
            | SuperGPQA | 71.4 |
            | VitaBench | 76.2 |
            | LVBench | 82.1 |
            | Brand New Unreviewed Eval | 99.0 |
            """,
            glm,
        )
        self.assertEqual(
            [(row["benchmarkId"], row["value"]) for row in rows],
            [("gpqa-diamond", 95.0)],
        )

    def test_discovered_vendor_page_rejects_unpinned_host(self):
        specs = discovered_vendor_page_specs(
            {
                "pages": [
                    {
                        "vendor": "glm",
                        "name": "GLM-99",
                        "displayName": "GLM-99",
                        "url": "https://docs.z.ai.evil.example/guides/llm/glm-99",
                        "rawUrl": "https://docs.z.ai.evil.example/guides/llm/glm-99.md",
                        "aliases": ["GLM-99"],
                        "sourceKey": "glm-docs-llms",
                    }
                ]
            },
            curated_specs=[],
        )

        self.assertEqual(specs, [])

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

    def test_parse_markdown_source_scores_preserves_rowspan_column_alignment(self):
        html = """
        <table>
          <tr>
            <th>Benchmark</th><th>Notes</th>
            <th>Gemini 3.6 Flash</th><th>Gemini 3.5 Flash</th>
          </tr>
          <tr>
            <td rowspan="2">CharXiv Reasoning</td><td>No tools</td>
            <td>85.2%</td><td>84.2%</td>
          </tr>
          <tr><td>With tools</td><td>89.4%</td><td>84.9%</td></tr>
          <tr>
            <td rowspan="2">GDM-MRCR v2 (8-needle)</td><td>128k (average)</td>
            <td>91.8%</td><td>77.3%</td>
          </tr>
          <tr><td>1M (pointwise)</td><td>54.0%</td><td>26.6%</td></tr>
        </table>
        """
        spec = {
            "id": "google-test",
            "label": "Google test",
            "url": "https://deepmind.google/models/model-cards/gemini-3-6-flash/",
            "columns": {"Gemini 3.6 Flash": "Gemini 3.6 Flash"},
            "rowLabels": {
                "CharXiv Reasoning": "charxiv-no-tools",
                "With tools": "charxiv-tools",
                "GDM-MRCR v2 (8-needle)": "mrcr-v2-128k",
                "1M (pointwise)": "mrcr-v2-1m",
            },
        }

        rows = parse_markdown_source_scores(html, spec)
        values = {row["benchmarkId"]: row["value"] for row in rows}

        self.assertEqual(values["charxiv-no-tools"], 85.2)
        self.assertEqual(values["charxiv-tools"], 89.4)
        self.assertEqual(values["mrcr-v2-128k"], 91.8)
        self.assertEqual(values["mrcr-v2-1m"], 54.0)

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
                    "effort": "max",
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
        self.assertEqual(
            next(
                row
                for row in retained["results"]
                if row["sourceId"] == "official-source"
                and row["benchmarkId"] == "seed"
            )["effort"],
            "max",
        )
        self.assertNotIn(("fresh-source", "stale"), result_values)
        self.assertEqual(statuses["official-source"], "stale-retained; refresh blocked: URLError")
        self.assertEqual(statuses["fresh-source"], "refreshed")

    def test_kimi_blocked_refresh_does_not_restore_removed_comparator_rows(self):
        current = {
            "sources": [
                {
                    "id": "kimi-k3-release",
                    "collectionStatus": "reference-only; refresh blocked: URLError",
                }
            ],
            "results": [
                {
                    "sourceId": "kimi-k3-release",
                    "model": "Kimi K3",
                    "benchmarkId": "browsecomp",
                    "value": 91.2,
                }
            ],
        }
        previous = {
            "sources": [{"id": "kimi-k3-release", "collectionStatus": "refreshed"}],
            "results": [
                {
                    "sourceId": "kimi-k3-release",
                    "model": "Kimi K3",
                    "benchmarkId": "browsecomp",
                    "value": 90.0,
                },
                {
                    "sourceId": "kimi-k3-release",
                    "model": "GPT-5.5",
                    "benchmarkId": "browsecomp",
                    "value": 84.4,
                    "effort": "max",
                },
            ],
        }

        retained = retain_previous_results_on_blocked_refresh(current, previous)

        self.assertEqual(
            {(row["model"], row["benchmarkId"]) for row in retained["results"]},
            {("Kimi K3", "browsecomp")},
        )

    def test_exact_label_policy_migration_drops_previous_fuzzy_matches(self):
        current = {
            "sources": [
                {
                    "id": "auto-source",
                    "collectionStatus": "refreshed",
                    "autoDiscoveredVendorPage": True,
                    "exactBenchmarkLabelsOnly": True,
                }
            ],
            "results": [
                {
                    "sourceId": "auto-source",
                    "model": "Model A",
                    "benchmarkId": "gpqa-diamond",
                    "value": 90.3,
                }
            ],
        }
        previous = {
            "sources": [
                {
                    "id": "auto-source",
                    "collectionStatus": "refreshed",
                    "autoDiscoveredVendorPage": True,
                }
            ],
            "results": [
                {
                    "sourceId": "auto-source",
                    "model": "Model A",
                    "benchmarkId": "gpqa-diamond",
                    "value": 71.4,
                },
                {
                    "sourceId": "auto-source",
                    "model": "Model A",
                    "benchmarkId": "tau-bench",
                    "value": 76.2,
                },
            ],
        }

        retained = retain_previous_results_on_blocked_refresh(current, previous)

        self.assertEqual(
            [(row["benchmarkId"], row["value"]) for row in retained["results"]],
            [("gpqa-diamond", 90.3)],
        )
        self.assertEqual(retained["sources"][0]["collectionStatus"], "refreshed")

    def test_regressed_auto_refresh_keeps_new_values_and_missing_old_rows(self):
        current = {
            "sources": [
                {
                    "id": "auto-source",
                    "collectionStatus": "refreshed",
                    "autoDiscoveredVendorPage": True,
                    "exactBenchmarkLabelsOnly": True,
                }
            ],
            "results": [
                {
                    "sourceId": "auto-source",
                    "model": "Model A",
                    "benchmarkId": "gpqa-diamond",
                    "value": 90.3,
                }
            ],
        }
        previous = {
            "sources": [
                {
                    "id": "auto-source",
                    "collectionStatus": "refreshed",
                    "autoDiscoveredVendorPage": True,
                    "exactBenchmarkLabelsOnly": True,
                }
            ],
            "results": [
                {
                    "sourceId": "auto-source",
                    "model": "Model A",
                    "benchmarkId": "gpqa-diamond",
                    "value": 89.0,
                },
                {
                    "sourceId": "auto-source",
                    "model": "Model A",
                    "benchmarkId": "tau-bench",
                    "value": 63.0,
                },
            ],
        }

        retained = retain_previous_results_on_blocked_refresh(current, previous)
        values = {
            row["benchmarkId"]: row["value"] for row in retained["results"]
        }

        self.assertEqual(values, {"gpqa-diamond": 90.3, "tau-bench": 63.0})
        self.assertIn(
            "parsed score count regressed from 2 to 1",
            retained["sources"][0]["collectionStatus"],
        )

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

    def test_build_payload_includes_deepseek_v4_flash_0731_official_scores(self):
        payload = build_payload({}, "seeded")
        sources = {source["id"]: source for source in payload["sources"]}
        results = {
            row["benchmarkId"]: row
            for row in payload["results"]
            if row["sourceId"] == "deepseek-v4-flash-0731-update"
        }

        self.assertEqual(
            sources["deepseek-v4-flash-0731-update"]["url"],
            "https://api-docs.deepseek.com/updates/",
        )
        self.assertIn(
            "DeepSeek V4 Flash 0731 (max) [R]",
            sources["deepseek-v4-flash-0731-update"]["modelAliases"],
        )
        self.assertNotIn(
            "deepseek-v4-flash",
            sources["deepseek-v4-flash-0731-update"]["modelAliases"],
        )
        self.assertEqual(
            {benchmark_id: row["value"] for benchmark_id, row in results.items()},
            {
                "terminal-bench-2-1": 82.7,
                "nl2repo": 54.2,
                "cybergym": 76.7,
                "deepswe": 54.4,
                "toolathlon": 70.3,
                "agents-last-exam": 25.2,
                "automationbench": 25.1,
            },
        )
        old_flash_max = next(
            row
            for row in payload["results"]
            if row["sourceId"] == "deepseek-v4-pro-card"
            and row["model"] == "DeepSeek V4 Flash (Max)"
        )
        self.assertIn("deepseek-v4-flash-0420", old_flash_max["modelAliases"])
        self.assertNotIn("deepseek-v4-flash", old_flash_max["modelAliases"])

    def test_build_payload_includes_glm53_and_deepseek_v4_pro_0813(self):
        payload = build_payload({}, "seeded")
        sources = {source["id"]: source for source in payload["sources"]}
        results = {
            (row["sourceId"], row["benchmarkId"]): row
            for row in payload["results"]
            if row["sourceId"]
            in {"zai-glm-5-3-release", "deepseek-v4-pro-0813-card"}
        }

        self.assertEqual(
            sources["zai-glm-5-3-release"]["url"],
            "https://z.ai/blog/glm-5.3",
        )
        self.assertEqual(
            results[("zai-glm-5-3-release", "terminal-bench-3")]["value"],
            28.3,
        )
        self.assertEqual(
            results[("zai-glm-5-3-release", "gdpval-aa-v2-elo")]["value"],
            1769,
        )
        self.assertTrue(
            results[("zai-glm-5-3-release", "deepswe-v1-1")]["variantScoped"]
        )

        deepseek = results[("deepseek-v4-pro-0813-card", "terminal-bench-2-1")]
        self.assertEqual(deepseek["value"], 87.9)
        self.assertEqual(deepseek["effort"], "max")
        self.assertTrue(deepseek["variantScoped"])
        self.assertEqual(
            results[("deepseek-v4-pro-0813-card", "hle-tools")]["value"],
            60.0,
        )
        self.assertEqual(
            results[("deepseek-v4-pro-0813-card", "dsbench-hard")]["value"],
            67.2,
        )
        self.assertEqual(
            sources["deepseek-v4-pro-0813-card"]["rawUrl"],
            "https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/raw/main/README.md",
        )

    def test_build_payload_includes_hy3_public_official_scores(self):
        payload = build_payload({}, "seeded")
        sources = {source["id"]: source for source in payload["sources"]}
        results = {
            row["benchmarkId"]: row["value"]
            for row in payload["results"]
            if row["sourceId"] == "tencent-hy3-repository"
        }

        self.assertEqual(sources["tencent-hy3-repository"]["url"], "https://github.com/Tencent-Hunyuan/Hy3")
        self.assertIn("Hy3 [R]", sources["tencent-hy3-repository"]["modelAliases"])
        self.assertEqual(
            results,
            {
                "swe-bench-multilingual": 75.8,
                "swe-bench-verified": 78.0,
                "swe-bench-pro": 57.9,
                "terminal-bench-2-1": 71.7,
                "nl2repo": 45.6,
                "deepswe": 28.0,
                "browsecomp": 84.2,
                "mcp-atlas": 79.1,
                "toolathlon": 48.5,
                "hle-tools": 53.2,
                "gpqa-diamond": 90.4,
                "hle": 37.0,
                "imoanswerbench": 90.0,
                "aa-lcr": 73.4,
            },
        )
        self.assertNotIn("apex-agents", results)
        self.assertNotIn("claw-eval", results)
        self.assertNotIn("skillsbench", results)

    def test_glm52_max_sources_keep_the_specific_target_model(self):
        specs = {spec["id"]: spec for spec in OFFICIAL_SOURCE_SPECS}
        payload = build_payload({}, "seeded")
        glm_result = next(
            row
            for row in payload["results"]
            if row["sourceId"] == "zai-glm-5-2-card" and row["benchmarkId"] == "hle"
        )

        self.assertNotIn("GLM-5.2 (max)", specs["kimi-k3-release"]["columns"])
        self.assertEqual(specs["zai-glm-5-2-card"]["columns"]["GLM-5.2"], "GLM-5.2 (max)")
        self.assertEqual(
            specs["zai-glm-5-2-card"]["columns"]["DeepSeek-V4-Pro"],
            "DeepSeek V4 Pro (Max)",
        )
        self.assertEqual(glm_result["model"], "GLM-5.2 (max)")
        self.assertIn("GLM-5.2 (max) [R]", glm_result["modelAliases"])

    def test_top_vendor_sources_prefer_official_pages_over_hugging_face(self):
        payload = build_payload({}, "seeded")
        top_vendor_ids = {
            "anthropic-claude-opus-4-7-release",
            "anthropic-claude-sonnet-5-release",
            "qwen-qwen3-release",
            "qwen-qwen2-release",
            "qwen-qwen2-5-release",
            "qwen-qwen2-5-coder-release",
            "qwen-qwen2-5-max-release",
            "qwen-qwen3-6-27b-card",
            "qwen-qwen3-6-plus-release",
            "qwen-qwen3-8-max-release",
            "deepseek-v4-pro-card",
            "deepseek-v4-pro-0813-card",
            "deepseek-v4-flash-0731-update",
            "tencent-hy3-repository",
            "kimi-k3-release",
            "kimi-k2-6-card",
            "kimi-k2-7-code-card",
            "kimi-k2-thinking-card",
            "kimi-k2-5-card",
            "zai-glm-4-6-card",
            "zai-glm-5-1-card",
            "zai-glm-5-2-card",
            "zai-glm-5-3-release",
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
        g9v3 = sources["ai9stars-g9v3-3b-card"]
        qwen38_27b = sources["qwen-qwen3-8-27b-card"]

        self.assertEqual(kimi_0905["category"], "Official model card")
        self.assertEqual(kimi_0905["url"], "https://huggingface.co/moonshotai/Kimi-K2-Instruct-0905")
        self.assertEqual(g9v3["category"], "Official model card")
        self.assertEqual(g9v3["url"], "https://huggingface.co/ai9stars/G9v3-3B")
        self.assertEqual(qwen38_27b["category"], "Official model card")
        self.assertEqual(
            qwen38_27b["url"],
            "https://huggingface.co/Qwen/Qwen3.8-27B",
        )
        self.assertEqual(qwen38_27b["organization"], "Qwen")
        self.assertTrue(qwen38_27b["addModelIfMissing"])
        self.assertEqual(
            qwen38_27b["modelMetadata"]["modelKey"],
            "Qwen3.8 27B (xhigh) [R]",
        )
        self.assertEqual(
            sources["zai-glm-5-3-release"]["modelMetadata"]["modelKey"],
            "GLM-5.3 (max) [R]",
        )
        self.assertEqual(sources["zai-glm-5-3-release"]["effort"], "max")

    def test_reference_only_model_cards_keep_model_aliases(self):
        payload = build_payload({}, "seeded")
        sources = {source["id"]: source for source in payload["sources"]}

        self.assertIn("north-mini-code-1-0", sources["cohere-north-mini-code-card"]["modelAliases"])
        self.assertEqual(sources["cohere-north-mini-code-card"]["scoreStatus"], "reference")
        self.assertIn("g9v3-3b", sources["ai9stars-g9v3-3b-card"]["modelAliases"])
        self.assertEqual(sources["ai9stars-g9v3-3b-card"]["scoreStatus"], "reference")
        self.assertIn("motif-0714", sources["motif-motif-3-beta-hub"]["modelAliases"])
        self.assertEqual(sources["motif-motif-3-beta-hub"]["scoreStatus"], "reference")

    def test_official_release_sources_keep_model_aliases(self):
        payload = build_payload({}, "seeded")
        sources = {source["id"]: source for source in payload["sources"]}

        self.assertIn(
            "Claude Mythos 5 / Fable 5 (higher of two)",
            sources["anthropic-claude-fable-5-docs"]["modelAliases"],
        )
        self.assertIn(
            "Claude Fable 5 (with fallback)",
            sources["anthropic-claude-fable-5-system-card"]["modelAliases"],
        )
        self.assertIn("Claude Sonnet 5 (max)", sources["anthropic-claude-sonnet-5-release"]["modelAliases"])
        self.assertIn("Claude Opus 5 (max)", sources["anthropic-claude-opus-5-release"]["modelAliases"])
        self.assertIn("gemini-3-6-flash", sources["google-gemini-3-6-flash-card"]["modelAliases"])
        self.assertIn(
            "agnes-2-5-pro-alpha",
            sources["sapiens-agnes-2-5-pro-alpha-docs"]["modelAliases"],
        )

    def test_build_payload_includes_claude_sonnet_5_official_scores(self):
        payload = build_payload({}, "seeded")
        sources = {source["id"]: source for source in payload["sources"]}
        results = {
            row["benchmarkId"]: row
            for row in payload["results"]
            if row["sourceId"] == "anthropic-claude-sonnet-5-release"
        }

        self.assertEqual(
            sources["anthropic-claude-sonnet-5-release"]["url"],
            "https://www.anthropic.com/news/claude-sonnet-5",
        )
        self.assertEqual(results["swe-bench-pro"]["value"], 63.2)
        self.assertEqual(results["terminal-bench-2-1"]["value"], 80.4)
        self.assertEqual(results["hle"]["value"], 43.2)
        self.assertEqual(results["hle-tools"]["value"], 57.4)
        self.assertEqual(results["osworld-verified"]["value"], 81.2)
        self.assertEqual(results["gdpval-aa-elo"]["value"], 1618)
        self.assertIn("claude-sonnet-5", results["swe-bench-pro"]["modelAliases"])

    def test_build_payload_includes_latest_models_official_scores(self):
        payload = build_payload({}, "seeded")
        sources = {source["id"]: source for source in payload["sources"]}
        by_source = {}
        for row in payload["results"]:
            by_source.setdefault(row["sourceId"], {})[row["benchmarkId"]] = row

        opus = by_source["anthropic-claude-opus-5-release"]
        gemini36 = by_source["google-gemini-3-6-flash-card"]
        gemini35_lite = by_source["google-gemini-3-5-flash-lite-card"]
        agnes = by_source["sapiens-agnes-2-5-pro-alpha-docs"]

        self.assertEqual(
            sources["anthropic-claude-opus-5-release"]["url"],
            "https://www.anthropic.com/news/claude-opus-5",
        )
        self.assertEqual(opus["frontier-bench-v0-1"]["value"], 43.3)
        self.assertEqual(opus["gdpval-aa-elo"]["value"], 1861)
        self.assertEqual(opus["hle"]["value"], 56.3)
        self.assertEqual(opus["hle-tools"]["value"], 64.7)
        self.assertEqual(opus["biomysterybench-human-solved"]["value"], 90.1)
        self.assertEqual(opus["browsecomp"]["model"], "Claude Opus 5")
        self.assertEqual(opus["arc-agi-3"]["model"], "Claude Opus 5 (high)")
        self.assertIn("Opus 4.8", opus["frontier-bench-v0-1"]["model"])

        self.assertEqual(gemini36["swe-bench-pro"]["value"], 58.7)
        self.assertEqual(gemini36["mle-bench"]["value"], 63.9)
        self.assertEqual(gemini36["mrcr-v2-1m"]["value"], 54.0)
        self.assertEqual(gemini35_lite["swe-bench-pro"]["value"], 54.2)
        self.assertEqual(gemini35_lite["mle-bench"]["value"], 39.2)
        self.assertEqual(gemini35_lite["mrcr-v2-1m"]["value"], 21.3)

        self.assertEqual(
            sources["sapiens-agnes-2-5-pro-alpha-docs"]["category"],
            "Official provider documentation",
        )
        self.assertIn("Artificial Analysis snapshot", sources["sapiens-agnes-2-5-pro-alpha-docs"]["note"])
        self.assertEqual(agnes["gpqa-diamond"]["value"], 87.6)
        self.assertEqual(agnes["aa-omniscience"]["value"], -26.3)
        self.assertEqual(agnes["terminal-bench-2-1"]["value"], 67.0)
        self.assertEqual(agnes["gdpval-aa-elo"]["value"], 1170)

        benchmark_ids = {benchmark["id"] for benchmark in payload["benchmarks"]}
        self.assertTrue(
            {
                "frontier-bench-v0-1",
                "frontiercode-v1-1-main",
                "mle-bench",
                "aa-omniscience",
                "aa-omniscience-accuracy",
                "aa-omniscience-non-hallucination",
                "tau3-banking",
            }.issubset(benchmark_ids)
        )

    def test_build_payload_includes_qwen38_and_opus5_system_card_scores(self):
        payload = build_payload({}, "seeded")
        sources = {source["id"]: source for source in payload["sources"]}
        by_source = {}
        for row in payload["results"]:
            by_source.setdefault(row["sourceId"], {})[row["benchmarkId"]] = row

        qwen = by_source["qwen-qwen3-8-max-release"]
        qwen27 = by_source["qwen-qwen3-8-27b-card"]
        opus = by_source["anthropic-claude-opus-5-system-card"]

        self.assertEqual(
            sources["qwen-qwen3-8-max-release"]["url"],
            "https://qwen.ai/blog?id=qwen3.8",
        )
        self.assertEqual(qwen["swe-bench-pro"]["value"], 67.7)
        self.assertEqual(qwen["terminal-bench-2-1"]["value"], 86.6)
        self.assertEqual(qwen["ifbench"]["value"], 82.8)
        self.assertEqual(qwen["charxiv-tools"]["value"], 93.5)
        self.assertIn("partial", qwen["osworld-2"]["scoreSelection"])
        self.assertIn("qwen3-8-max", qwen["swe-bench-pro"]["modelAliases"])

        self.assertEqual(
            sources["qwen-qwen3-8-27b-card"]["url"],
            "https://huggingface.co/Qwen/Qwen3.8-27B",
        )
        self.assertEqual(qwen27["terminal-bench-2-1"]["value"], 73.0)
        self.assertEqual(qwen27["swe-bench-pro"]["value"], 61.7)
        self.assertEqual(qwen27["agents-last-exam"]["value"], 42.9)
        self.assertEqual(qwen27["claw-eval-mm-average"]["value"], 56.9)
        self.assertEqual(qwen27["mathvision-python"]["value"], 94.6)
        self.assertEqual(qwen27["erqa"]["value"], 65.5)
        self.assertTrue(qwen27["swe-bench-pro"]["variantScoped"])
        self.assertEqual(qwen27["swe-bench-pro"]["effort"], "xhigh")
        self.assertIn("qwen3-8-27b", qwen27["swe-bench-pro"]["modelAliases"])

        self.assertEqual(opus["swe-bench-verified"]["value"], 96.0)
        self.assertEqual(opus["swe-bench-pro"]["value"], 79.2)
        self.assertEqual(opus["swe-bench-multilingual"]["value"], 89.5)
        self.assertEqual(opus["mcp-atlas"]["value"], 85.8)
        self.assertEqual(opus["toolathlon"]["value"], 80.6)
        self.assertTrue(opus["swe-bench-pro"]["variantScoped"])
        self.assertTrue(sources["anthropic-claude-opus-5-system-card"]["variantScoped"])

        opus_release = by_source["anthropic-claude-opus-5-release"]
        self.assertEqual(opus_release["arc-agi-3"]["model"], "Claude Opus 5 (high)")
        self.assertEqual(opus_release["arc-agi-3"]["effort"], "high")
        self.assertTrue(opus_release["arc-agi-3"]["evidenceEligible"])
        self.assertFalse(opus_release["browsecomp"]["evidenceEligible"])
        self.assertFalse(opus_release["frontier-bench-v0-1"]["modelScoreEligible"])
        self.assertFalse(opus_release["frontier-bench-v0-1"]["evidenceEligible"])
        self.assertTrue(opus_release["frontier-bench-v0-1"]["systemScore"])
        self.assertIn("Opus 4.8", opus_release["frontier-bench-v0-1"]["model"])

    def test_payload_results_reference_declared_benchmarks_without_duplicates(self):
        payload = build_payload({}, "seeded")
        benchmark_ids = {benchmark["id"] for benchmark in payload["benchmarks"]}
        result_keys = [
            (row["sourceId"], row["model"], row["benchmarkId"])
            for row in payload["results"]
        ]

        self.assertTrue(all(row["benchmarkId"] in benchmark_ids for row in payload["results"]))
        self.assertEqual(len(result_keys), len(set(result_keys)))

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

    def test_build_payload_includes_grok45_official_scores_only(self):
        payload = build_payload({}, "seeded")
        sources = {source["id"]: source for source in payload["sources"]}
        results = {
            row["benchmarkId"]: row
            for row in payload["results"]
            if row["sourceId"] == "spacexai-grok-4-5-release"
        }

        self.assertEqual(
            sources["spacexai-grok-4-5-release"]["url"],
            "https://x.ai/news/grok-4-5",
        )
        self.assertEqual(
            set(results),
            {"deepswe", "deepswe-v1-1", "swe-marathon", "terminal-bench-2-1", "swe-bench-pro"},
        )
        self.assertEqual(results["deepswe"]["value"], 62.0)
        self.assertEqual(results["deepswe-v1-1"]["value"], 53.0)
        self.assertEqual(results["swe-marathon"]["value"], 29.0)
        self.assertEqual(results["terminal-bench-2-1"]["value"], 83.3)
        self.assertEqual(results["swe-bench-pro"]["value"], 64.7)
        self.assertIn("Grok 4.5 (high)", results["swe-bench-pro"]["modelAliases"])
        self.assertIn("grok-4-5", results["swe-bench-pro"]["modelAliases"])

    def test_build_payload_includes_inkling_and_celeris_official_scores(self):
        payload = build_payload({}, "seeded")
        sources = {source["id"]: source for source in payload["sources"]}
        results = {
            (row["model"], row["benchmarkId"]): row
            for row in payload["results"]
            if row["sourceId"] == "thinking-machines-inkling-small-release"
        }
        celeris = next(
            row
            for row in payload["results"]
            if row["sourceId"] == "celeris-celeris-1-benchmarks"
        )

        self.assertEqual(
            sources["thinking-machines-inkling-small-release"]["url"],
            "https://thinkingmachines.ai/news/inkling-small/",
        )
        self.assertEqual(results[("Inkling Small", "swe-bench-verified")]["value"], 80.2)
        self.assertEqual(results[("Inkling", "terminal-bench-2-1")]["value"], 63.8)
        self.assertEqual(results[("Inkling Small", "mcp-atlas")]["value"], 79.6)
        self.assertEqual(results[("Inkling", "gdpval-aa-elo")]["value"], 1238)
        self.assertEqual(len(results), 44)
        self.assertIn("inkling-small", results[("Inkling Small", "hle")]["modelAliases"])

        self.assertEqual(
            sources["celeris-celeris-1-benchmarks"]["url"],
            "https://celeris.ai/blog-benchmarks.html",
        )
        self.assertEqual(celeris["model"], "Celeris-1")
        self.assertEqual(celeris["benchmarkId"], "mmlu-pro")
        self.assertEqual(celeris["value"], 75.9)
        self.assertIn("celeris-1", celeris["modelAliases"])

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
        self.assertEqual(results[("GPT-5.6 Sol (max)", "swe-bench-pro")]["value"], 64.6)
        self.assertEqual(results[("GPT-5.6 Terra (max)", "terminal-bench-2-1")]["value"], 87.4)
        self.assertEqual(results[("GPT-5.6 Luna (max)", "gpqa-diamond")]["value"], 92.3)
        self.assertEqual(results[("GPT-5.6 Sol (max)", "agents-last-exam")]["value"], 52.7)
        self.assertEqual(results[("GPT-5.6 Terra (max)", "osworld-2")]["value"], 50.2)
        self.assertEqual(results[("GPT-5.6 Luna (max)", "arc-agi-3")]["value"], 0.18)
        sol_swe = results[("GPT-5.6 Sol (max)", "swe-bench-pro")]
        terra_swe = results[("GPT-5.6 Terra (max)", "swe-bench-pro")]
        self.assertIn("gpt-5-6-sol", sol_swe["modelAliases"])
        self.assertIn("GPT-5.6 Terra (max)", terra_swe["modelAliases"])
        self.assertTrue(sol_swe["variantScoped"])
        self.assertEqual(sol_swe["effort"], "max")
        self.assertEqual(sol_swe["configurationConfidence"], "inferred")
        self.assertNotIn("gpt-5-6-sol-xhigh", sol_swe["modelAliases"])

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
            if row["model"] == "GLM-5.2 (max)" and row["sourceId"] == "zai-glm-5-2-card"
        )
        self.assertIn("glm-5-2", glm52["modelAliases"])
        self.assertNotIn("glm-5-2-non-reasoning", glm52["modelAliases"])

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
        self.assertEqual(
            sources["kimi-k3-release"]["rawUrl"],
            "https://huggingface.co/moonshotai/Kimi-K3/raw/main/README.md",
        )
        self.assertEqual(results[("Kimi K3", "terminal-bench-2-1")]["value"], 88.3)
        self.assertEqual(results[("Kimi K3", "browsecomp")]["value"], 91.2)
        self.assertEqual(results[("Kimi K3", "gdpval-aa-v2-elo")]["value"], 1686)
        self.assertEqual(results[("Kimi K3", "toolathlon")]["value"], 76.5)
        self.assertEqual(results[("Kimi K3", "job-bench")]["value"], 54.3)
        self.assertEqual(results[("Kimi K3", "apex-agents")]["value"], 41.0)
        self.assertIn("kimi-k3", results[("Kimi K3", "browsecomp")]["modelAliases"])
        self.assertTrue(results[("Kimi K3", "browsecomp")]["variantScoped"])
        self.assertEqual(len(results), 50)
        self.assertEqual({model for model, _benchmark in results}, {"Kimi K3"})
        self.assertTrue(all(row["effort"] == "max" for row in results.values()))

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

        fable_composite_swe = next(
            row
            for row in results
            if row["model"] == "Claude Mythos 5 / Fable 5 (higher of two)"
            and row["benchmarkId"] == "swe-bench-pro"
        )
        fable_swe = next(
            row
            for row in results
            if row["sourceId"] == "anthropic-claude-fable-5-system-card"
            and row["model"] == "Claude Fable 5 (with fallback)"
            and row["benchmarkId"] == "swe-bench-pro"
        )
        fable_terminal = next(
            row
            for row in results
            if row["sourceId"] == "anthropic-claude-fable-5-system-card"
            and row["benchmarkId"] == "terminal-bench-2-1"
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
            if row["model"] == "GLM-5.2 (max)" and row["benchmarkId"] == "deepswe"
        )
        glm52_frontierswe = next(
            row
            for row in results
            if row["model"] == "GLM-5.2 (max)" and row["benchmarkId"] == "frontierswe-dominance"
        )
        glm52_terminal = next(
            row
            for row in results
            if row["model"] == "GLM-5.2 (max)" and row["benchmarkId"] == "terminal-bench-2-1"
        )

        self.assertEqual(fable_composite_swe["value"], 80.3)
        self.assertFalse(fable_composite_swe["modelScoreEligible"])
        self.assertFalse(fable_composite_swe["evidenceEligible"])
        self.assertTrue(fable_composite_swe["composite"])
        self.assertEqual(fable_swe["value"], 80.0)
        self.assertTrue(fable_swe["variantScoped"])
        self.assertTrue(fable_swe["productEvidenceEligible"])
        self.assertFalse(fable_swe["pureModelEligible"])
        self.assertEqual(fable_terminal["value"], 84.3)
        self.assertTrue(fable_terminal["fallbackObserved"])
        self.assertEqual(fable_terminal["fallbackRate"], 0.209)
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
