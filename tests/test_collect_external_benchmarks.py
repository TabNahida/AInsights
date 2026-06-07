import unittest

from ArtificialAnalysis.collect_external_benchmarks import (
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


if __name__ == "__main__":
    unittest.main()
