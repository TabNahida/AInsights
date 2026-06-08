import unittest
from pathlib import Path


class DocsMarkupTests(unittest.TestCase):
    def test_static_site_has_separate_entry_pages(self):
        docs_dir = Path(__file__).resolve().parents[1] / "docs"

        self.assertIn('data-page="home"', (docs_dir / "index.html").read_text(encoding="utf-8"))
        self.assertIn('data-page="ranking"', (docs_dir / "full-rank.html").read_text(encoding="utf-8"))
        self.assertIn('data-page="model"', (docs_dir / "model.html").read_text(encoding="utf-8"))
        self.assertIn('data-page="benchmark"', (docs_dir / "benchmark.html").read_text(encoding="utf-8"))
        self.assertIn('data-page="sources"', (docs_dir / "sources.html").read_text(encoding="utf-8"))

    def test_page_title_and_footer_name_source(self):
        html = (Path(__file__).resolve().parents[1] / "docs" / "index.html").read_text(encoding="utf-8")

        self.assertIn("<title>AI Insights Analysis</title>", html)
        self.assertIn("<h1>AI Insights Analysis</h1>", html)
        self.assertIn("<footer", html)
        self.assertIn("数据来源", html)
        self.assertIn("Artificial Analysis", html)

    def test_page_exposes_i18n_views_source_filter_and_rank_surfaces(self):
        html = (Path(__file__).resolve().parents[1] / "docs" / "index.html").read_text(encoding="utf-8")

        self.assertIn('id="languageButtons"', html)
        self.assertIn('id="homeView"', html)
        self.assertIn('id="homeMetrics"', html)
        self.assertIn('id="latestModels"', html)
        self.assertIn('id="modelView"', html)
        self.assertIn('id="modelDetail"', html)
        self.assertIn('id="providerView"', html)
        self.assertIn('id="providerDetail"', html)
        self.assertIn('id="benchmarkView"', html)
        self.assertIn('id="benchmarkDetail"', html)
        self.assertIn('id="sourcesView"', html)
        self.assertIn('id="sourceOverview"', html)
        self.assertIn('id="rankingView"', html)
        self.assertIn('id="top20Chart"', html)
        self.assertIn('id="costScatter"', html)
        self.assertIn('id="viewButtons"', html)
        self.assertIn('id="sourceFilterButtons"', html)
        self.assertIn('id="histogramList"', html)
        self.assertIn('id="textRanking"', html)

    def test_table_omits_raw_aa_columns_and_shows_operational_columns(self):
        html = (Path(__file__).resolve().parents[1] / "docs" / "index.html").read_text(encoding="utf-8")

        self.assertIn('id="sourceHeader"', html)
        self.assertIn('id="speedHeader"', html)
        self.assertIn('id="contextHeader"', html)
        self.assertIn('id="priceHeader"', html)
        self.assertNotIn('id="indexCostHeader"', html)
        self.assertNotIn("<th>AA Intelligence</th>", html)
        self.assertNotIn("<th>AA Coding</th>", html)
        self.assertNotIn("<th>AA Agentic</th>", html)

    def test_custom_weights_are_fine_grained(self):
        html = (Path(__file__).resolve().parents[1] / "docs" / "index.html").read_text(encoding="utf-8")

        self.assertIn('max="100"', html)
        self.assertIn('step="0.01"', html)

    def test_full_ranking_views_are_not_hard_capped(self):
        app_js = (Path(__file__).resolve().parents[1] / "docs" / "app.js").read_text(encoding="utf-8")

        self.assertNotIn("ranked.slice(0, 250)", app_js)
        self.assertNotIn("models.slice(0, 120)", app_js)

    def test_custom_weights_show_metric_coverage_and_scatter_leaders(self):
        app_js = (Path(__file__).resolve().parents[1] / "docs" / "app.js").read_text(encoding="utf-8")
        css = (Path(__file__).resolve().parents[1] / "docs" / "styles.css").read_text(encoding="utf-8")

        self.assertIn("customMetricGroups", app_js)
        self.assertIn("metricGroupCoverageCount", app_js)
        self.assertIn("metric-weight-label", app_js)
        self.assertIn("customMissingMode", app_js)
        self.assertIn("customPenaltyMax", app_js)
        self.assertIn("customMinCoveragePct", app_js)
        self.assertIn('max="100" step="0.5"', app_js)
        self.assertIn("customMetricGroupsCache", app_js)
        self.assertIn("applyMissingModePreset", app_js)
        self.assertIn("customWeightsForPreset", app_js)
        self.assertIn("penalty", app_js)
        self.assertIn("minCoverage", app_js)
        self.assertIn("missing-mode-controls", css)
        self.assertIn("weight-preset-button", css)
        self.assertNotIn("customMissingAsZero", app_js)
        self.assertNotIn("checkbox-setting", css)
        self.assertNotIn("customMissingBase", app_js)
        self.assertNotIn("missingPenaltyMax", app_js)
        self.assertIn("scatter-leader", app_js)
        self.assertIn("benchmarkEvidenceRows", app_js)
        self.assertIn("model.html?${params.toString()}", app_js)
        self.assertIn("benchmark.html?id=", app_js)
        self.assertNotIn("source-weight-controls", app_js)
        self.assertNotIn("combinedMetricWeightsFromSources", app_js)
        self.assertNotIn("Source weights", app_js)
        self.assertIn(".metric-weight-label", css)
        self.assertIn(".scatter-leader", css)
        self.assertIn(".benchmark-evidence-row", css)
        self.assertNotIn(".source-weight-card", css)
        self.assertNotIn("Open AA page", app_js)

    def test_custom_ainsights_preset_matches_default_ranking_missing_policy(self):
        app_js = (Path(__file__).resolve().parents[1] / "docs" / "app.js").read_text(encoding="utf-8")

        self.assertIn('customMissingMode: "zero"', app_js)
        self.assertIn("customPenaltyMax: 100", app_js)
        self.assertIn("const zeroScore = selectedWeight > 0 && selected > 0 && coverageRatio >= minCoverage ? weightedScore / selectedWeight : null;", app_js)
        self.assertIn("score = availableScore + (zeroScore - availableScore) * penaltyRatio;", app_js)
        self.assertIn("if (!Number.isFinite(score) && penaltyRatio >= 1 && Number.isFinite(zeroScore)) score = zeroScore;", app_js)
        self.assertIn("const presetWeightedMetrics = group.metrics.filter((metric) => Number(state.data.presets[state.customWeightPresetId]?.weights?.[metric.key] || 0) > 0);", app_js)
        self.assertIn('zero: "缺失记 0"', app_js)
        self.assertIn('zero: "Missing = 0"', app_js)

    def test_sources_page_and_split_scripts_are_present(self):
        docs_dir = Path(__file__).resolve().parents[1] / "docs"
        html = (docs_dir / "sources.html").read_text(encoding="utf-8")
        app_js = (docs_dir / "app.js").read_text(encoding="utf-8")
        app_utils = (docs_dir / "app-utils.js").read_text(encoding="utf-8")

        self.assertIn('id="sourcesLink"', html)
        self.assertIn('id="sourceMetricMap"', html)
        self.assertIn('<script src="./app-utils.js"></script>', html)
        self.assertIn("renderSourcesPage", app_js)
        self.assertIn("catalogSources", app_js)
        self.assertIn("isOfficialModelSource", app_js)
        self.assertNotIn("function getInitialLanguage", app_js)
        self.assertIn("function getInitialLanguage", app_utils)

    def test_benchmark_page_surface_is_present(self):
        docs_dir = Path(__file__).resolve().parents[1] / "docs"
        html = (docs_dir / "benchmark.html").read_text(encoding="utf-8")
        app_js = (docs_dir / "app.js").read_text(encoding="utf-8")
        app_utils = (docs_dir / "app-utils.js").read_text(encoding="utf-8")
        css = (docs_dir / "styles.css").read_text(encoding="utf-8")

        self.assertIn('id="benchmarkView"', html)
        self.assertIn('id="benchmarkDetail"', html)
        self.assertIn("renderBenchmarkPage", app_js)
        self.assertIn("benchmarkRankingRows", app_js)
        self.assertIn('filename === "benchmark.html"', app_utils)
        self.assertIn(".benchmark-ranking-row", css)

    def test_provider_page_surface_and_latest_home_section_are_present(self):
        docs_dir = Path(__file__).resolve().parents[1] / "docs"
        html = (docs_dir / "index.html").read_text(encoding="utf-8")
        app_js = (docs_dir / "app.js").read_text(encoding="utf-8")
        app_utils = (docs_dir / "app-utils.js").read_text(encoding="utf-8")
        css = (docs_dir / "styles.css").read_text(encoding="utf-8")

        self.assertIn('id="latestModels"', html)
        self.assertIn('id="providerView"', html)
        self.assertIn('id="providerDetail"', html)
        self.assertIn("renderLatestModels", app_js)
        self.assertIn("renderProviderPage", app_js)
        self.assertIn("providerHref(row.provider)", app_js)
        self.assertIn('class="detail-provider-link"', app_js)
        self.assertIn("providerHref(providerName)", app_js)
        self.assertIn("data-history-back", app_js)
        self.assertIn('hash.startsWith("provider/")', app_utils)
        self.assertIn(".latest-model-card", css)
        self.assertIn(".provider-detail", css)
        self.assertIn(".detail-provider-link", css)
        self.assertIn(".provider-model-row", css)

    def test_number_formatting_keeps_integer_zeroes(self):
        app_utils = (Path(__file__).resolve().parents[1] / "docs" / "app-utils.js").read_text(encoding="utf-8")

        self.assertIn('return text.includes(".") ? text.replace(/\\.?0+$/, "") : text;', app_utils)

    def test_model_icons_use_local_assets(self):
        data = (Path(__file__).resolve().parents[1] / "docs" / "data" / "models.json").read_text(encoding="utf-8")

        self.assertIn('"src": "assets/logos/', data)
        self.assertNotIn('"src": "https://artificialanalysis.ai/img/logos/', data)


if __name__ == "__main__":
    unittest.main()
