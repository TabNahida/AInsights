import unittest

from ArtificialAnalysis.collect_external_benchmarks import build_payload, parse_openai_scores


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


if __name__ == "__main__":
    unittest.main()
