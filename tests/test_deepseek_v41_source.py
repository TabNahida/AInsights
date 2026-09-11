import unittest

from benchmarks.collect_benchmark_scores import (
    OFFICIAL_SOURCE_SPECS,
    build_payload,
    parse_markdown_source_scores,
)


class DeepSeekV41SourceTests(unittest.TestCase):
    def setUp(self):
        self.spec = next(
            source for source in OFFICIAL_SOURCE_SPECS
            if source["id"] == "deepseek-v4-1-flash-release"
        )

    def test_instruct_column_preserves_versions_subsets_and_effort(self):
        text = """
| Benchmark (Metric) | DS-V4.1-Flash-Base |
| --- | ---: |
| GPQA Diamond (Pass@1) | 12.3 |

| Benchmark (Metric) | DS-V4-Flash | DS-V4.1-Flash |
| --- | ---: | ---: |
| GPQA Diamond (Pass@1) | 89.9 | 90.9 |
| HLE (Pass@1) | 37.8 | 36.8 (39.1†) |
| Terminal-Bench 2.1 (Pass@1) | 82.7 | 90.6 |
| Terminal-Bench 3.0 (Pass@1) | 7.6 | 30.0 |
| Terminal-Bench 4.0 (Pass@1) | 7.0 | 31.2 |
| Agent's Last Exam (Pass@1) | 25.2 | 31.8 |
| Chartography w/ tools (Pass@1) | — | 78.9 |
| BabyVision w/ tools (Pass@1) | — | 89.6 |
| ZeroBench-main w/ tools (Pass@5) | — | 49.0 |
| Unreviewed Benchmark | 99 | 99 |

| Benchmark (Metric) | Claude Code | DSH Minimal |
| --- | ---: | ---: |
| Terminal-Bench 2.1 (Pass@1) | 88.0 | 90.6 |
"""
        rows = parse_markdown_source_scores(text, self.spec)
        values = {row["benchmarkId"]: row["value"] for row in rows}
        self.assertEqual(values, {
            "gpqa-diamond": 90.9, "hle": 36.8, "hle-text-only": 39.1,
            "terminal-bench-2-1": 90.6, "terminal-bench-3": 30.0,
            "terminal-bench-4": 31.2, "agents-last-exam-pass1": 31.8,
            "chartography-tools": 78.9, "babyvision-tools": 89.6,
            "zerobench-main-tools-pass5": 49.0,
        })
        for row in rows:
            self.assertEqual(row["model"], "DeepSeek V4.1 Flash (max)")
            self.assertEqual(row["effort"], "max")
            self.assertTrue(row["variantScoped"])
            self.assertEqual(row["configurationConfidence"], "explicit")
            self.assertIn("deepseek-v4-1-flash", row["modelAliases"])
            self.assertNotIn("deepseek-v4-flash", row["modelAliases"])
            self.assertNotIn("deepseek-v4-1-flash-high", row["modelAliases"])

    def test_hle_ambiguous_composite_does_not_silently_merge_subset(self):
        for value in ("39.1†", "36.8 / 39.1 / 42.0"):
            text = (
                "| Benchmark | DS-V4.1-Flash |\n| --- | --- |\n"
                f"| HLE (Pass@1) | {value} |\n"
            )
            self.assertEqual(parse_markdown_source_scores(text, self.spec), [])

    def test_official_seed_rows_have_distinct_benchmarks(self):
        payload = build_payload({}, "seeded")
        rows = [row for row in payload["results"] if row["sourceId"] == self.spec["id"]]
        self.assertEqual(len(rows), 20)
        self.assertEqual(len({row["benchmarkId"] for row in rows}), 20)
        by_id = {row["benchmarkId"]: row for row in rows}
        self.assertEqual(by_id["codeforces-elo"]["value"], 3471)
        self.assertEqual(by_id["codeforces-elo"]["unit"], "Elo")
        self.assertEqual(by_id["hle"]["value"], 36.8)
        self.assertEqual(by_id["hle-text-only"]["value"], 39.1)
        self.assertNotIn("agents-last-exam", by_id)
        self.assertNotIn("babyvision-python", by_id)


if __name__ == "__main__":
    unittest.main()
