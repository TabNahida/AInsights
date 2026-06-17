import unittest
from pathlib import Path


class DocsMarkupTests(unittest.TestCase):
    def test_static_site_has_separate_entry_pages(self):
        docs_dir = Path(__file__).resolve().parents[1] / "docs"

        self.assertIn('data-page="home"', (docs_dir / "index.html").read_text(encoding="utf-8"))
        self.assertIn('data-page="ranking"', (docs_dir / "full-rank.html").read_text(encoding="utf-8"))
        self.assertIn('data-page="model"', (docs_dir / "model.html").read_text(encoding="utf-8"))
        self.assertIn('data-page="provider"', (docs_dir / "provider.html").read_text(encoding="utf-8"))
        self.assertIn('data-page="compare"', (docs_dir / "compare.html").read_text(encoding="utf-8"))
        self.assertIn('data-page="benchmark"', (docs_dir / "benchmark.html").read_text(encoding="utf-8"))
        self.assertIn('data-page="sources"', (docs_dir / "sources.html").read_text(encoding="utf-8"))
        self.assertIn('data-page="contribute"', (docs_dir / "contribute.html").read_text(encoding="utf-8"))
        self.assertIn('data-page="methodology"', (docs_dir / "methodology.html").read_text(encoding="utf-8"))

    def test_page_title_and_footer_name_source(self):
        html = (Path(__file__).resolve().parents[1] / "docs" / "index.html").read_text(encoding="utf-8")

        self.assertIn("<title>AI Insights Analysis</title>", html)
        self.assertIn('name="description"', html)
        self.assertIn("AIndex", html)
        self.assertIn('rel="canonical"', html)
        self.assertIn('property="og:title"', html)
        self.assertIn('application/ld+json', html)
        self.assertIn("<h1>AI Insights Analysis</h1>", html)
        self.assertIn("<footer", html)
        self.assertIn("数据来源", html)
        self.assertIn("Artificial Analysis", html)
        self.assertIn("https://github.com/TabNahida/AInsights", html)

    def test_all_static_pages_expose_search_metadata(self):
        docs_dir = Path(__file__).resolve().parents[1] / "docs"

        for path in docs_dir.glob("*.html"):
            html = path.read_text(encoding="utf-8")
            expected_url = "https://ainsights.tab.homes/" if path.name == "index.html" else f"https://ainsights.tab.homes/{path.name}"
            self.assertIn('name="description"', html, path.name)
            self.assertIn("AIndex", html, path.name)
            self.assertIn(f'rel="canonical" href="{expected_url}"', html, path.name)
            self.assertIn(f'property="og:url" content="{expected_url}"', html, path.name)
            self.assertIn(f'"url":"{expected_url}"', html, path.name)
            self.assertIn('property="og:description"', html, path.name)

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
        self.assertIn("customMinMetricCoverage", app_js)
        self.assertIn("customCalculationMethod", app_js)
        self.assertIn("customNormalizationMethod", app_js)
        self.assertIn("calculation-method-controls", app_js)
        self.assertIn("normalization-method-controls", app_js)
        self.assertIn("Geometric Weight Mean", app_js)
        self.assertIn("Weight Mean", app_js)
        self.assertIn("Best score ratio", app_js)
        self.assertIn("Raw score", app_js)
        self.assertIn('metrics: ["Humanity\'s Last Exam", "GPQA Diamond"]', app_js)
        self.assertIn('metrics: ["AA-LCR"]', app_js)
        self.assertIn('metrics: ["IFBench", "CritPt"]', app_js)
        self.assertIn('metrics: ["GDPval-AA v2", "τ³-Banking"]', app_js)
        self.assertIn('metrics: ["Terminal-Bench v2.1", "SciCode"]', app_js)
        self.assertIn('metrics: ["AA-Omniscience Accuracy", "AA-Omniscience Non-Hallucination Rate"]', app_js)
        self.assertNotIn('metrics: ["GDPval-AA", "τ²-Bench Telecom", "Terminal-Bench Hard"]', app_js)
        self.assertNotIn("当前四类参考项目", app_js)
        self.assertNotIn("four-category AA reference", app_js)
        self.assertIn("metricCoverageFilterOptions", app_js)
        self.assertIn("data-coverage-filter", app_js)
        self.assertIn("visibleGroups", app_js)
        self.assertIn("Evaluation data weights", app_js)
        self.assertIn("Calculation", app_js)
        self.assertNotIn('missingModeTitle: "Missing values"', app_js)
        self.assertNotIn("AA benchmark weights", app_js)
        self.assertIn('max="100" step="0.5"', app_js)
        self.assertIn("customMetricGroupsCache", app_js)
        self.assertIn("customAggregateScore", app_js)
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
        self.assertIn(".metric-coverage-filter", css)
        self.assertIn(".metric-filter-summary", css)
        self.assertIn("grid-template-columns: repeat(var(--option-count), minmax(0, 1fr));", css)
        self.assertIn(".scatter-leader", css)
        self.assertIn(".benchmark-evidence-row", css)
        self.assertNotIn(".source-weight-card", css)
        self.assertNotIn("Open AA page", app_js)

    def test_custom_ainsights_preset_matches_default_ranking_missing_policy(self):
        app_js = (Path(__file__).resolve().parents[1] / "docs" / "app.js").read_text(encoding="utf-8")

        self.assertIn('customMissingMode: "zero"', app_js)
        self.assertIn('customCalculationMethod: "geometric"', app_js)
        self.assertIn('customNormalizationMethod: "relative-best"', app_js)
        self.assertIn("customPenaltyMax: 100", app_js)
        self.assertIn('calculation: "geometric"', app_js)
        self.assertIn('normalization: "relative-best"', app_js)
        self.assertIn("const zeroScore = customAggregateScore(entries, selectedWeight, state.customCalculationMethod, state.customNormalizationMethod);", app_js)
        self.assertIn("score = availableScore + (zeroScore - availableScore) * penaltyRatio;", app_js)
        self.assertIn("if (!Number.isFinite(score) && penaltyRatio >= 1 && coverageRatio >= minCoverage && Number.isFinite(zeroScore)) score = zeroScore;", app_js)
        self.assertIn("const presetWeightedMetrics = group.metrics.filter((metric) => Number(state.data.presets[state.customWeightPresetId]?.weights?.[metric.key] || 0) > 0);", app_js)
        self.assertIn('zero: "缺失记 0"', app_js)
        self.assertIn('zero: "Missing = 0"', app_js)

    def test_methodology_page_is_linked_from_ranking_not_navigation(self):
        docs_dir = Path(__file__).resolve().parents[1] / "docs"
        html = (docs_dir / "methodology.html").read_text(encoding="utf-8")
        full_rank_html = (docs_dir / "full-rank.html").read_text(encoding="utf-8")
        app_js = (docs_dir / "app.js").read_text(encoding="utf-8")
        app_utils = (docs_dir / "app-utils.js").read_text(encoding="utf-8")

        self.assertIn("AInsights Index", html)
        self.assertIn("AIndex", html)
        self.assertIn("Geometric Weighted Mean", html)
        self.assertIn("Best score ratio", html)
        self.assertIn("GDPval-AA v2", html)
        self.assertIn("τ³-Banking", html)
        self.assertIn("Terminal-Bench v2.1", html)
        self.assertIn("Hallucination Rate 权重为 0", html)
        self.assertIn("methodology.html", app_js)
        self.assertIn('href="methodology.html"', full_rank_html)
        self.assertIn('filename === "methodology.html"', app_utils)
        self.assertIn('if (page === "methodology") return "methodology.html";', app_utils)
        self.assertIn('const pageOrder = ["home", "ranking", "compare", "benchmarks", "sources", "contribute"];', app_js)
        self.assertNotIn("presetDescription(state.presetId, preset)", app_js)

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
        self.assertIn("modelSourceCardsHtml", app_js)
        self.assertNotIn("function getInitialLanguage", app_js)
        self.assertIn("function getInitialLanguage", app_utils)

    def test_contribution_page_surface_is_present(self):
        docs_dir = Path(__file__).resolve().parents[1] / "docs"
        html = (docs_dir / "contribute.html").read_text(encoding="utf-8")
        app_js = (docs_dir / "app.js").read_text(encoding="utf-8")
        app_utils = (docs_dir / "app-utils.js").read_text(encoding="utf-8")
        css = (docs_dir / "styles.css").read_text(encoding="utf-8")

        self.assertIn('id="contributeView"', html)
        self.assertIn('id="contributionPreview"', html)
        self.assertIn('id="contributionGithubButton"', html)
        self.assertIn('id="contributionBenchmarkId"', html)
        self.assertIn('id="contributionBenchmarkName"', html)
        self.assertIn('data-contribution-section="benchmark"', html)
        self.assertIn("renderContributePage", app_js)
        self.assertIn("contributionGithubNewFileHref", app_js)
        self.assertIn('const contributionModes = ["score", "model", "benchmark"];', app_js)
        self.assertIn('type: "benchmark"', app_js)
        self.assertIn('filename === "contribute.html"', app_utils)
        self.assertIn('if (page === "contribute") return "contribute.html";', app_utils)
        self.assertIn(".contribute-layout", css)

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
        self.assertIn('class="benchmark-ranking-row" data-card-href', app_js)
        self.assertIn('filename === "benchmark.html"', app_utils)
        self.assertIn(".benchmark-ranking-row", css)

    def test_provider_page_surface_and_latest_home_section_are_present(self):
        docs_dir = Path(__file__).resolve().parents[1] / "docs"
        html = (docs_dir / "index.html").read_text(encoding="utf-8")
        provider_html = (docs_dir / "provider.html").read_text(encoding="utf-8")
        app_js = (docs_dir / "app.js").read_text(encoding="utf-8")
        app_utils = (docs_dir / "app-utils.js").read_text(encoding="utf-8")
        css = (docs_dir / "styles.css").read_text(encoding="utf-8")

        self.assertIn('id="latestModels"', html)
        self.assertIn('data-page="provider"', provider_html)
        self.assertIn('id="providerView"', provider_html)
        self.assertIn('id="providerDetail"', provider_html)
        self.assertIn("renderLatestModels", app_js)
        self.assertIn("renderProviderPage", app_js)
        self.assertIn("providerHref(row.provider)", app_js)
        self.assertIn("renderProviderTextLink(model.creator, \"home\")", app_js)
        self.assertIn('data-card-href="${escapeHtml(modelHref(model, "home"))}"', app_js)
        self.assertIn('class="histogram-row" data-card-href', app_js)
        self.assertIn('class="text-ranking-row" data-card-href', app_js)
        self.assertIn('class="detail-provider-link"', app_js)
        self.assertIn("providerHref(providerName, currentModelBackSource())", app_js)
        self.assertIn("provider.html?${params.toString()}", app_js)
        self.assertNotIn("index.html#provider/", app_js)
        self.assertIn("data-history-back", app_js)
        self.assertIn('filename === "provider.html"', app_utils)
        self.assertIn('if (page === "provider") return "provider.html";', app_utils)
        self.assertIn('hash.startsWith("provider/")', app_utils)
        self.assertIn(".latest-model-card", css)
        self.assertIn(".latest-model-compare", css)
        self.assertIn(".latest-model-score", css)
        self.assertIn(".provider-text-link", css)
        self.assertIn(".provider-detail", css)
        self.assertIn(".detail-provider-link", css)
        self.assertIn(".provider-model-row", css)

    def test_provider_back_context_and_compare_page_are_present(self):
        docs_dir = Path(__file__).resolve().parents[1] / "docs"
        compare_html = (docs_dir / "compare.html").read_text(encoding="utf-8")
        app_js = (docs_dir / "app.js").read_text(encoding="utf-8")
        app_utils = (docs_dir / "app-utils.js").read_text(encoding="utf-8")
        css = (docs_dir / "styles.css").read_text(encoding="utf-8")

        self.assertIn('id="compareView"', compare_html)
        self.assertIn('id="compareModelSelect"', compare_html)
        self.assertIn('type="search"', compare_html)
        self.assertIn('class="compare-search-wrap"', compare_html)
        self.assertIn('id="compareModelOptions"', compare_html)
        self.assertIn('id="compareModelOptions" role="listbox" aria-label="可添加模型" hidden', compare_html)
        self.assertIn('id="compareResults"', compare_html)
        self.assertIn("renderComparePage", app_js)
        self.assertIn("defaultCompareModels", app_js)
        self.assertIn("renderModalitySupportGrid", app_js)
        self.assertIn("renderCompareOption", app_js)
        self.assertIn("renderCompareEntry", app_js)
        self.assertIn("compareSearchPlaceholder", app_js)
        self.assertIn("comparePickerOpen", app_js)
        self.assertIn("els.compareModelOptions.hidden = !isOpen;", app_js)
        self.assertIn("compareHref", app_js)
        self.assertIn("providerBackHref", app_js)
        self.assertIn("providerHref(providerName, currentModelBackSource())", app_js)
        self.assertIn("data-provider-return", app_js)
        self.assertNotIn("latest-model-actions", app_js)
        self.assertIn('class="compare-entry-link"', app_js)
        self.assertIn("models", app_js)
        self.assertIn('filename === "compare.html"', app_utils)
        self.assertIn('if (page === "compare") return "compare.html";', app_utils)
        self.assertIn(".compare-view", css)
        self.assertIn(".compare-option-card", css)
        self.assertIn(".compare-search-wrap", css)
        self.assertIn(".compare-picker-shell", css)
        self.assertIn(".modality-support-grid", css)
        self.assertIn(".modality-support-icon.is-supported", css)
        self.assertIn(".compare-model-facts > span", css)
        self.assertIn(".compare-entry-link", css)
        self.assertIn(".compare-table", css)

    def test_number_formatting_keeps_integer_zeroes(self):
        app_utils = (Path(__file__).resolve().parents[1] / "docs" / "app-utils.js").read_text(encoding="utf-8")

        self.assertIn('return text.includes(".") ? text.replace(/\\.?0+$/, "") : text;', app_utils)

    def test_model_icons_use_local_assets(self):
        data = (Path(__file__).resolve().parents[1] / "docs" / "data" / "models.json").read_text(encoding="utf-8")

        self.assertIn('"src": "assets/logos/', data)
        self.assertNotIn('"src": "https://artificialanalysis.ai/img/logos/', data)


if __name__ == "__main__":
    unittest.main()
