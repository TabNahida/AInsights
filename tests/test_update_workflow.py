import unittest
from pathlib import Path


class UpdateWorkflowTests(unittest.TestCase):
    def test_workflow_refreshes_complete_model_and_benchmark_site_daily(self):
        workflow = (
            Path(__file__).resolve().parents[1]
            / ".github"
            / "workflows"
            / "update-artificial-analysis.yml"
        ).read_text(encoding="utf-8")

        self.assertIn("name: Update model and benchmark data", workflow)
        self.assertIn('cron: "0 1 * * *"', workflow)
        self.assertIn("openai-gpt-5-6-release", workflow)
        self.assertIn("kimi-k3-release", workflow)
        self.assertIn("python ArtificialAnalysis/scrape_artificial_analysis.py", workflow)
        self.assertIn("python benchmarks/collect_benchmark_scores.py", workflow)
        self.assertIn("python scripts/build_docs_site.py", workflow)
        self.assertGreaterEqual(workflow.count("python -B -m unittest discover -s tests"), 2)
        self.assertIn("data/benchmarks/benchmark_scores.json", workflow)
        self.assertIn("docs/data/models.json", workflow)
        self.assertIn("docs/data/models.js", workflow)
        self.assertIn('git commit -m "Update model and benchmark data"', workflow)


if __name__ == "__main__":
    unittest.main()
