import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = PROJECT_ROOT / ".github" / "workflows"
STABLE_WORKFLOW = WORKFLOW_DIR / "update-artificial-analysis.yml"
RISKY_WORKFLOW = WORKFLOW_DIR / "refresh-external-benchmarks.yml"

GENERATED_HTML = (
    "index.html",
    "full-rank.html",
    "sources.html",
    "contribute.html",
    "providers.html",
    "compare.html",
    "provider.html",
    "benchmark.html",
    "model.html",
)

ANALYSIS_OUTPUTS = (
    "full_rankings_aindex_scheme18.csv",
    "top50_aindex_scheme18.csv",
    "full_rankings_exact_config_aindex_scheme18.csv",
    "top50_exact_config_aindex_scheme18.csv",
    "aindex_scheme18_validation_summary.json",
    "exact_config_multi_method_full_rankings.csv",
    "exact_config_score_visibility_audit.csv",
    "full_rankings_exact_config_twopl_sparse_80_20_score.csv",
    "full_rankings_twopl_sparse_80_20_score.csv",
    "key_pair_overlap_audit.csv",
    "method_stability.csv",
    "multi_method_full_rankings.csv",
    "multi_method_top50.csv",
    "multi_method_validation_summary.json",
    "score_order_validation_summary.json",
    "target_exact_config_comparison.csv",
    "target_source_coverage_audit.csv",
    "top50_exact_config_twopl_sparse_80_20_score.csv",
    "top50_global_family_percentile.csv",
    "top50_percentile_mean_equal_board.csv",
    "top50_percentile_median_equal_board.csv",
    "top50_rasch_dense_item_sensitivity.csv",
    "top50_rasch_equal_board.csv",
    "top50_rasch_sparse_item_sensitivity.csv",
    "top50_twopl_equal_board.csv",
    "top50_twopl_sparse_80_20_score.csv",
)


class UpdateWorkflowTests(unittest.TestCase):
    def read_workflow(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def assert_common_writer_safety(self, workflow: str) -> None:
        self.assertIn("group: model-data-writer-${{ github.ref }}", workflow)
        self.assertIn("cancel-in-progress: false", workflow)
        self.assertIn('PYTHONDONTWRITEBYTECODE: "1"', workflow)
        self.assertIn("uses: actions/checkout@v7", workflow)
        self.assertIn("uses: actions/setup-python@v7", workflow)
        self.assertIn("git ls-files --others --exclude-standard", workflow)
        self.assertIn('git fetch --no-tags origin "$GITHUB_REF_NAME"', workflow)
        self.assertIn("git merge --ff-only FETCH_HEAD", workflow)
        self.assertIn('echo "UPDATE_BASE_SHA=$(git rev-parse HEAD)"', workflow)
        self.assertIn('if [ "$remote_sha" != "$UPDATE_BASE_SHA" ]; then', workflow)
        self.assertNotIn("git pull --rebase", workflow)
        self.assertNotRegex(
            workflow,
            r"(?m)^\s*git add -- analysis/irt_leaderboard_exploration/outputs\s*$",
        )

    def assert_generated_site_paths_are_staged(self, workflow: str) -> None:
        self.assertIn("git add -- docs/data/models.json docs/data/models.js", workflow)
        for filename in GENERATED_HTML:
            self.assertRegex(workflow, rf"git add -- [^\n]*docs/{filename}(?:\s|$)")
        for filename in ANALYSIS_OUTPUTS:
            self.assertIn(
                f"git add -- analysis/irt_leaderboard_exploration/outputs/{filename}",
                workflow,
            )

    def test_daily_workflow_only_refreshes_stable_model_data(self):
        workflow = self.read_workflow(STABLE_WORKFLOW)

        self.assertIn("name: Update Artificial Analysis model data", workflow)
        self.assertIn('cron: "0 1 * * *"', workflow)
        self.assertIn(
            "python ArtificialAnalysis/scrape_artificial_analysis.py --output-dir ArtificialAnalysis --allow-stale",
            workflow,
        )
        self.assertIn("python scripts/build_docs_site.py", workflow)
        self.assertIn(
            "python -B analysis/irt_leaderboard_exploration/validate_scheme18_production.py --input docs/data/models.json",
            workflow,
        )
        self.assertEqual(workflow.count("python -B -m unittest discover -s tests"), 1)
        self.assertNotIn("python benchmarks/discover_official_model_cards.py", workflow)
        self.assertNotIn("python benchmarks/discover_official_vendor_pages.py", workflow)
        self.assertNotIn("python benchmarks/collect_benchmark_scores.py", workflow)
        self.assertNotIn("data/benchmarks/", workflow)
        self.assertIn(
            "git add -- ArtificialAnalysis/artificialanalysis_raw_scores_wide.csv",
            workflow,
        )
        self.assertIn("docs/assets/logos", workflow)
        self.assert_generated_site_paths_are_staged(workflow)
        self.assert_common_writer_safety(workflow)

        scrape_position = workflow.index("python ArtificialAnalysis/scrape_artificial_analysis.py")
        build_position = workflow.index("python scripts/build_docs_site.py")
        validate_position = workflow.index("validate_scheme18_production.py")
        tests_position = workflow.index("python -B -m unittest discover -s tests")
        commit_position = workflow.index('git commit -m "Update Artificial Analysis model data"')
        self.assertLess(scrape_position, build_position)
        self.assertLess(build_position, validate_position)
        self.assertLess(validate_position, tests_position)
        self.assertLess(tests_position, commit_position)

    def test_weekly_workflow_isolates_external_source_refreshes(self):
        workflow = self.read_workflow(RISKY_WORKFLOW)

        self.assertIn("name: Refresh external benchmark sources", workflow)
        self.assertIn('cron: "15 3 * * 1"', workflow)
        self.assertNotIn("scrape_artificial_analysis.py", workflow)
        self.assertIn("python benchmarks/discover_official_model_cards.py", workflow)
        self.assertIn("python benchmarks/discover_official_vendor_pages.py", workflow)
        self.assertIn("python benchmarks/collect_benchmark_scores.py", workflow)
        self.assertIn("python benchmarks/validate_official_sources.py", workflow)
        self.assertIn("python scripts/build_docs_site.py", workflow)
        self.assertIn("python -B -m unittest discover -s tests", workflow)
        self.assertIn("git add -- data/benchmarks/official_model_cards.json", workflow)
        self.assertIn("git add -- data/benchmarks/official_vendor_pages.json", workflow)
        self.assertIn("git add -- data/benchmarks/benchmark_scores.json", workflow)
        self.assertNotIn("ArtificialAnalysis/artificialanalysis_raw_scores_wide.csv", workflow)
        self.assert_generated_site_paths_are_staged(workflow)
        self.assert_common_writer_safety(workflow)

        discovery_position = workflow.index("discover_official_model_cards.py")
        vendor_discovery_position = workflow.index("discover_official_vendor_pages.py")
        collector_position = workflow.index("collect_benchmark_scores.py")
        policy_position = workflow.index("validate_official_sources.py")
        build_position = workflow.index("python scripts/build_docs_site.py")
        tests_position = workflow.index("python -B -m unittest discover -s tests")
        commit_position = workflow.index('git commit -m "Refresh external benchmark data"')
        self.assertLess(discovery_position, collector_position)
        self.assertLess(vendor_discovery_position, collector_position)
        self.assertLess(collector_position, policy_position)
        self.assertLess(policy_position, build_position)
        self.assertLess(build_position, tests_position)
        self.assertLess(tests_position, commit_position)


if __name__ == "__main__":
    unittest.main()
