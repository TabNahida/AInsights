import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from ArtificialAnalysis import scrape_artificial_analysis as scraper
from ArtificialAnalysis.scrape_artificial_analysis import (
    build_raw_scores_rows,
    download_creator_logos,
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
                "slug": "reasoning-model-high",
                "input_modality_text": True,
                "input_modality_image": True,
                "input_modality_speech": False,
                "input_modality_video": None,
                "output_modality_text": True,
                "output_modality_image": False,
                "output_modality_speech": False,
                "output_modality_video": False,
                "release_date": "2026-01-01",
                "model_url": "/models/reasoning-model",
                "model_creators": {
                    "name": "Lab A",
                    "slug": "lab-a",
                    "color": "#123456",
                    "logo_small_url": "/img/logos/lab-a-small.svg",
                    "logo_url": "/img/logos/lab-a.svg",
                },
                "intelligence_index": 55.5,
                "coding_index": 44.4,
                "agentic_index": 33.3,
                "cache_hit_price": 0.25,
                "price_1m_input_tokens": 1.5,
                "price_1m_output_tokens": 10,
                "intelligence_index_cost": {
                    "total_cost": 123.45,
                    "input_cost": 23.45,
                    "output_cost": 100,
                    "reasoning_cost": 75,
                    "answer_cost": 25,
                },
                "gdpval": 1500,
                "gdpval_v2": 1600,
                "terminalbench_hard": 0.5,
                "terminalbench_v2_1": 0.7,
                "tau2": 0.25,
                "tau_banking": 0.35,
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
                "gdpval_v2": 1200,
                "terminalbench_hard": 0.25,
                "terminalbench_v2_1": 0.45,
                "tau_banking": 0.15,
                "gpqa": None,
            },
        ]

        output = build_raw_scores_rows(rows)

        self.assertEqual(output[0]["model_key"], "Reasoning Model [R]")
        self.assertEqual(output[0]["model"], "Reasoning Model")
        self.assertEqual(output[0]["is_reasoning"], "true")
        self.assertEqual(output[0]["slug"], "reasoning-model-high")
        self.assertEqual(output[0]["input_modality_text"], "true")
        self.assertEqual(output[0]["input_modality_image"], "true")
        self.assertEqual(output[0]["input_modality_speech"], "false")
        self.assertEqual(output[0]["input_modality_video"], "")
        self.assertEqual(output[0]["output_modality_text"], "true")
        self.assertEqual(output[0]["output_modality_image"], "false")
        self.assertEqual(output[0]["creator"], "Lab A")
        self.assertEqual(output[0]["creator_slug"], "lab-a")
        self.assertEqual(output[0]["creator_color"], "#123456")
        self.assertEqual(output[0]["creator_logo_small_url"], "https://artificialanalysis.ai/img/logos/lab-a-small.svg")
        self.assertEqual(output[0]["release_date"], "2026-01-01")
        self.assertEqual(output[0]["AA Intelligence Index"], 55.5)
        self.assertEqual(output[0]["AA Coding Index"], 44.4)
        self.assertEqual(output[0]["AA Agentic Index"], 33.3)
        self.assertEqual(output[0]["AA Intelligence Index Cost (USD)"], 123.45)
        self.assertEqual(output[0]["AA Intelligence Index Input Cost (USD)"], 23.45)
        self.assertEqual(output[0]["AA Intelligence Index Output Cost (USD)"], 100.0)
        self.assertEqual(output[0]["AA Intelligence Index Reasoning Cost (USD)"], 75.0)
        self.assertEqual(output[0]["AA Intelligence Index Answer Cost (USD)"], 25.0)
        self.assertEqual(output[0]["Cache Hit Price Per 1M Tokens (USD)"], 0.25)
        self.assertEqual(output[0]["Input Price Per 1M Tokens (USD)"], 1.5)
        self.assertEqual(output[0]["Output Price Per 1M Tokens (USD)"], 10.0)
        self.assertEqual(output[0]["GDPval-AA v2"], 55.0)
        self.assertEqual(output[0]["Terminal-Bench v2.1"], 70.0)
        self.assertEqual(output[0]["τ³-Banking"], 35.0)
        self.assertEqual(output[0]["AA-Omniscience Accuracy"], 80.0)
        self.assertEqual(output[0]["AA-Omniscience Non-Hallucination Rate"], 90.0)
        self.assertEqual(output[0]["GPQA Diamond_rank"], 1)
        self.assertEqual(output[1]["model_key"], "Plain Model")
        self.assertEqual(output[1]["GDPval-AA v2"], 35.0)
        self.assertEqual(output[1]["GDPval-AA v2_rank"], 2)
        self.assertEqual(output[1]["GPQA Diamond_rank"], "")

    def test_build_raw_scores_rows_treats_next_undefined_sentinel_as_blank(self):
        rows = [
            {
                "short_name": "Model B",
                "slug": "model-b",
                "model_creators": {"name": "Lab B"},
                "intelligence_index_cost": "$undefined",
            }
        ]

        output = build_raw_scores_rows(rows)

        self.assertEqual(output[0]["AA Intelligence Index Cost (USD)"], "")
        self.assertEqual(output[0]["AA Intelligence Index Input Cost (USD)"], "")
        self.assertEqual(output[0]["AA Intelligence Index Output Cost (USD)"], "")
        self.assertEqual(output[0]["AA Intelligence Index Reasoning Cost (USD)"], "")
        self.assertEqual(output[0]["AA Intelligence Index Answer Cost (USD)"], "")

    def test_download_creator_logos_writes_deduped_logo_assets(self):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return b"<svg></svg>"

        rows = [
            {"model_creators": {"logo_small_url": "/img/logos/kimi_small.png"}},
            {"model_creators": {"logo_small_url": "/img/logos/kimi_small.png"}},
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(scraper, "urlopen", return_value=FakeResponse()) as mocked:
                count = download_creator_logos(rows, Path(tmpdir), timeout=5)

            self.assertEqual(count, 1)
            self.assertEqual(mocked.call_count, 1)
            self.assertTrue((Path(tmpdir) / "kimi_small.png").exists())


if __name__ == "__main__":
    unittest.main()
