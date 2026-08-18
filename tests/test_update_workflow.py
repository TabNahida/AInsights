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
        self.assertIn("python ArtificialAnalysis/scrape_artificial_analysis.py", workflow)
        self.assertIn("--output-dir ArtificialAnalysis --allow-stale", workflow)
        self.assertIn("python benchmarks/discover_official_model_cards.py", workflow)
        self.assertIn("python benchmarks/discover_official_vendor_pages.py", workflow)
        self.assertIn("python benchmarks/collect_benchmark_scores.py", workflow)
        self.assertIn("python benchmarks/validate_official_sources.py", workflow)
        self.assertIn("python scripts/build_docs_site.py", workflow)
        self.assertIn(
            "python -B analysis/irt_leaderboard_exploration/validate_scheme18_production.py --input docs/data/models.json",
            workflow,
        )
        self.assertIn("pip install --disable-pip-version-check -r requirements.txt", workflow)
        self.assertGreaterEqual(workflow.count("python -B -m unittest discover -s tests"), 2)
        self.assertIn("data/benchmarks/benchmark_scores.json", workflow)
        self.assertIn("data/benchmarks/official_model_cards.json", workflow)
        self.assertIn("data/benchmarks/official_vendor_pages.json", workflow)
        self.assertIn("docs/data/models.json", workflow)
        self.assertIn("docs/data/models.js", workflow)
        generated_html = (
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
        for filename in generated_html:
            self.assertRegex(workflow, rf"git add [^\n]*docs/{filename}(?:\s|$)")
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
        audit_outputs = (
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
        for filename in audit_outputs:
            self.assertIn(
                f"git add analysis/irt_leaderboard_exploration/outputs/{filename}",
                workflow,
            )
        self.assertNotRegex(
            workflow,
            r"(?m)^\s*git add .*analysis/irt_leaderboard_exploration/outputs(?:\s|$)",
        )
        self.assertIn("if ! git diff --quiet; then", workflow)

        discovery_position = workflow.index("python benchmarks/discover_official_model_cards.py")
        vendor_discovery_position = workflow.index(
            "python benchmarks/discover_official_vendor_pages.py"
        )
        collector_position = workflow.index("python benchmarks/collect_benchmark_scores.py")
        policy_position = workflow.index("python benchmarks/validate_official_sources.py")
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
        self.assertLess(discovery_position, collector_position)
        self.assertLess(vendor_discovery_position, collector_position)
        self.assertLess(collector_position, policy_position)
        self.assertLess(policy_position, build_position)
        self.assertLess(build_position, validate_position)
        self.assertLess(validate_position, post_update_tests_position)
        self.assertLess(post_update_tests_position, first_scheme18_stage_position)
        self.assertIn('git commit -m "Update model and benchmark data"', workflow)


if __name__ == "__main__":
    unittest.main()
