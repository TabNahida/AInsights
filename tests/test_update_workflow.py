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
        self.assertIn(
            "python -B analysis/irt_leaderboard_exploration/validate_scheme18_production.py --input docs/data/models.json",
            workflow,
        )
        self.assertIn("pip install --disable-pip-version-check -r requirements.txt", workflow)
        self.assertGreaterEqual(workflow.count("python -B -m unittest discover -s tests"), 2)
        self.assertIn("data/benchmarks/benchmark_scores.json", workflow)
        self.assertIn("docs/data/models.json", workflow)
        self.assertIn("docs/data/models.js", workflow)
        scheme18_outputs = (
            "full_rankings_aindex_scheme18.csv",
            "top50_aindex_scheme18.csv",
            "full_rankings_exact_config_aindex_scheme18.csv",
            "top50_exact_config_aindex_scheme18.csv",
            "aindex_scheme18_validation_summary.json",
        )
        for filename in scheme18_outputs:
            self.assertIn(
                f"git add analysis/irt_leaderboard_exploration/outputs/{filename}",
                workflow,
            )
        self.assertNotRegex(
            workflow,
            r"(?m)^\s*git add .*analysis/irt_leaderboard_exploration/outputs(?:\s|$)",
        )

        build_position = workflow.index("python scripts/build_docs_site.py")
        validate_position = workflow.index(
            "python -B analysis/irt_leaderboard_exploration/validate_scheme18_production.py"
        )
        post_update_tests_position = workflow.rindex(
            "python -B -m unittest discover -s tests"
        )
        first_scheme18_stage_position = workflow.index(
            "git add analysis/irt_leaderboard_exploration/outputs/full_rankings_aindex_scheme18.csv"
        )
        self.assertLess(build_position, validate_position)
        self.assertLess(validate_position, post_update_tests_position)
        self.assertLess(post_update_tests_position, first_scheme18_stage_position)
        self.assertIn('git commit -m "Update model and benchmark data"', workflow)


if __name__ == "__main__":
    unittest.main()
