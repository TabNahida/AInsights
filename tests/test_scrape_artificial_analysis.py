import unittest

from ArtificialAnalysis.scrape_artificial_analysis import (
    build_models_metadata_rows,
    build_raw_scores_rows,
    extract_default_data,
)


class ArtificialAnalysisScraperTests(unittest.TestCase):
    def test_extract_default_data_from_next_flight_chunks(self):
        html = (
            '<script>self.__next_f.push([1,"prefix {\\"defaultData\\":[{'
            '\\"short_name\\":\\"Model A\\",\\"slug\\":\\"model-a\\",'
            '\\"intelligence_index\\":42.5}"])</script>'
            '<script>self.__next_f.push([1,"],\\"other\\":true}} suffix"])</script>'
        )

        rows = extract_default_data(html)

        self.assertEqual(rows, [{"short_name": "Model A", "slug": "model-a", "intelligence_index": 42.5}])

    def test_build_raw_scores_rows_formats_scores_and_ranks(self):
        rows = [
            {
                "short_name": "Reasoning Model",
                "reasoning_model": True,
                "gdpval": 1500,
                "terminalbench_hard": 0.5,
                "tau2": 0.25,
                "lcr": 0.75,
                "omniscience_breakdown": {
                    "total": {
                        "accuracy": 0.8,
                        "non_hallucination_rate": 0.9,
                    }
                },
                "hle": 0.1,
                "gpqa": 0.8,
                "scicode": 0.6,
                "ifbench": 0.7,
                "critpt": 0.2,
                "apex_agents": 0.3,
                "it_bench_sre": 0.4,
                "mmmu_pro": 0.55,
                "livecodebench": 0.65,
                "aime25": 0.95,
            },
            {
                "short_name": "Plain Model",
                "reasoning_model": False,
                "gdpval": 1000,
                "terminalbench_hard": 0.25,
                "gpqa": None,
            },
        ]

        output = build_raw_scores_rows(rows)

        self.assertEqual(output[0]["model_key"], "Reasoning Model [R]")
        self.assertEqual(output[0]["model"], "Reasoning Model")
        self.assertEqual(output[0]["is_reasoning"], "true")
        self.assertEqual(output[0]["GDPval-AA"], 50.0)
        self.assertEqual(output[0]["Terminal-Bench Hard"], 50.0)
        self.assertEqual(output[0]["AA-Omniscience Accuracy"], 80.0)
        self.assertEqual(output[0]["AA-Omniscience Non-Hallucination Rate"], 90.0)
        self.assertEqual(output[0]["GPQA Diamond_rank"], 1)
        self.assertEqual(output[1]["model_key"], "Plain Model")
        self.assertEqual(output[1]["GDPval-AA"], 25.0)
        self.assertEqual(output[1]["GDPval-AA_rank"], 2)
        self.assertEqual(output[1]["GPQA Diamond_rank"], "")

    def test_build_models_metadata_rows_matches_existing_csv_shape(self):
        rows = [
            {
                "short_name": "Model A",
                "slug": "model-a",
                "release_date": "2026-01-02",
                "model_creators": {"name": "Lab A"},
                "intelligence_index": 42.5,
                "coding_index": 30.25,
                "agentic_index": 12.75,
                "intelligence_index_cost": {"total_cost": 99.99},
            }
        ]

        output = build_models_metadata_rows(rows)

        self.assertEqual(
            output[0],
            {
                "Model Name": "Model A",
                "Model Slug": "model-a",
                "Release Date": "2026-01-02",
                "Model Creator Name": "Lab A",
                "Artificial Analysis Intelligence Index": 42.5,
                "Artificial Analysis Coding Index": 30.25,
                "Artificial Analysis Agentic Index": 12.75,
                "Intelligence Index Cost (USD)": 99.99,
            },
        )

    def test_build_models_metadata_rows_treats_next_undefined_sentinel_as_blank(self):
        rows = [
            {
                "short_name": "Model B",
                "slug": "model-b",
                "model_creators": {"name": "Lab B"},
                "intelligence_index_cost": "$undefined",
            }
        ]

        output = build_models_metadata_rows(rows)

        self.assertEqual(output[0]["Intelligence Index Cost (USD)"], "")


if __name__ == "__main__":
    unittest.main()
