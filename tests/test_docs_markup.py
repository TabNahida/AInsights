import json
import re
import unittest
from pathlib import Path


class DocsMarkupTests(unittest.TestCase):
    def test_radar_axes_read_six_direct_ranking_profile_values(self):
        root = Path(__file__).resolve().parents[1]
        app_js = (root / "docs" / "app.js").read_text(encoding="utf-8")
        radar_source = app_js.split("function radarAxes()", 1)[1].split("function renderRadarBasisNotes()", 1)[0]
        value_source = app_js.split("function radarAxisValue(model, axis)", 1)[1].split(
            "function radarAxisCoverage(model, axis)", 1
        )[0]
        coverage_source = app_js.split("function radarAxisCoverage(model, axis)", 1)[1].split(
            "function radarHasCompleteProfile(model, axes", 1
        )[0]

        self.assertEqual(
            re.findall(r'id: "([^"]+)"', radar_source),
            [
                "coding",
                "agentic-tool-work",
                "hard-reasoning",
                "knowledge-science",
                "instruction-context",
                "evidence-coverage",
            ],
        )
        self.assertEqual(
            re.findall(r'boardId: "([^"]+)"', radar_source),
            [
                "coding",
                "agentic-tool-work",
                "hard-reasoning",
                "knowledge-science",
                "instruction-context",
            ],
        )
        self.assertIn('profileKey: "evidenceCoverageScore"', radar_source)
        self.assertIn("model?.rankingProfile?.boards?.[boardId]", app_js)
        self.assertIn("model?.rankingProfile?.[axis.profileKey]", value_source)
        self.assertNotIn("frontierGroupValue", value_source)
        self.assertNotIn("axis.metrics", radar_source + value_source)
        self.assertIn("board?.sparseTests", coverage_source)
        self.assertIn("board?.sparseItemPoolSize", coverage_source)
        self.assertIn("boardItemPoolSizesByMethod?.sparseRasch", coverage_source)
        self.assertIn('tr("radarDualCoverage", coverage)', coverage_source)
        self.assertIn("function radarHasCompleteProfile(model, axes", app_js)
        self.assertIn(
            "values.some((value) => !Number.isFinite(value))",
            app_js,
        )

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

    def test_default_ranking_is_precomputed_and_keeps_global_publication_ranks(self):
        root = Path(__file__).resolve().parents[1]
        app_js = (root / "docs" / "app.js").read_text(encoding="utf-8")
        payload = json.loads(
            (root / "docs" / "data" / "models.json").read_text(encoding="utf-8")
        )
        default_preset = payload["presets"][payload["defaultPreset"]]
        profiles = [
            model["rankingProfile"]
            for model in payload["models"]
            if model.get("rankingProfile")
        ]

        self.assertEqual(default_preset["kind"], "precomputed-ranking")
        self.assertEqual(len(profiles), payload["leaderboard"]["populationSize"])
        self.assertEqual(
            sorted(profile["publicationRank"] for profile in profiles),
            list(range(1, len(profiles) + 1)),
        )
        self.assertIn('if (preset.kind === "precomputed-ranking")', app_js)
        self.assertIn("function scoreModelForPrecomputedRanking(model)", app_js)
        precomputed_source = app_js.split(
            "function scoreModelForPrecomputedRanking(model)", 1
        )[1].split("\nfunction ", 1)[0]
        for field in (
            "displayScore",
            "publicationRank",
            "evidenceRank",
            "evidenceMeanRank",
        ):
            self.assertIn(field, precomputed_source)

        rank_source = app_js.split("function rankRows(models)", 1)[1].split(
            "\nfunction ", 1
        )[0]
        self.assertIn("publicationRank", rank_source)
        render_results_source = app_js.split("function renderResults(preset)", 1)[
            1
        ].split("\nfunction ", 1)[0]
        self.assertRegex(
            render_results_source,
            r"rankRows\(rankingUniverse\).*?filter\(matchesQuery\).*?filter\(matchesSourceFilter\)",
        )

    def test_full_ranking_has_ten_columns_and_sensitivity_ranks(self):
        docs_dir = Path(__file__).resolve().parents[1] / "docs"
        html = (docs_dir / "full-rank.html").read_text(encoding="utf-8")
        app_js = (docs_dir / "app.js").read_text(encoding="utf-8")
        table_head = html.split("<thead>", 1)[1].split("</thead>", 1)[0]

        self.assertEqual(len(re.findall(r"<th\b", table_head)), 10)
        self.assertIn('id="twoplRankHeader"', table_head)
        self.assertIn('id="denseRaschRankHeader"', table_head)

        render_table_source = app_js.split("function renderTable(models)", 1)[
            1
        ].split("\nfunction renderRow(model)", 1)[0]
        self.assertIn('colspan="10"', render_table_source)
        render_row_source = app_js.split("function renderRow(model)", 1)[1].split(
            "\nfunction ", 1
        )[0]
        self.assertEqual(
            render_row_source.count("<td")
            + render_row_source.count("${renderMethodRankCell("),
            10,
        )
        self.assertEqual(render_row_source.count("${renderMethodRankCell("), 2)
        self.assertIn("twopl", render_row_source)
        self.assertIn("denseRasch", render_row_source)
        self.assertIn("${model.rank}", render_row_source)

    def test_custom_lab_exposes_three_separate_tools_and_actions(self):
        app_js = (Path(__file__).resolve().parents[1] / "docs" / "app.js").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            'const customToolModeOrder = ["method-rank", "board-score", "benchmark-lab"]',
            app_js,
        )
        self.assertIn('data-custom-tool-mode="${mode}"', app_js)
        for mode in ("method-rank", "board-score", "benchmark-lab"):
            self.assertRegex(
                app_js,
                rf"state\.customToolMode\s*===\s*\"{re.escape(mode)}\"",
            )

        self.assertIn(
            '["equalize", "normalize", "clear", "restore", "export"]',
            app_js,
        )
        self.assertIn('data-custom-action="${action}"', app_js)
        for action in ("equalize", "normalize", "clear", "restore", "export"):
            self.assertRegex(
                app_js,
                rf'action\s*===\s*"{action}"|case\s+"{action}"',
            )
        self.assertIn('querySelectorAll("[data-custom-action]")', app_js)
        self.assertIn("function exportCustomConfiguration()", app_js)
        self.assertIn("new Blob", app_js)
        self.assertIn("link.download", app_js)

    def test_custom_method_and_board_tools_use_ranking_profile_evidence(self):
        app_js = (Path(__file__).resolve().parents[1] / "docs" / "app.js").read_text(
            encoding="utf-8"
        )

        for method in ("rasch", "sparseRasch", "twopl", "denseRasch"):
            self.assertIn(method, app_js)
        for board in (
            "coding",
            "agentic-tool-work",
            "hard-reasoning",
            "knowledge-science",
            "instruction-context",
        ):
            self.assertIn(board, app_js)
        self.assertIn("rankingProfile", app_js)
        self.assertIn("evidenceRank", app_js)
        self.assertIn("model?.rankingProfile?.methods?.[methodId]?.evidenceRank", app_js)
        self.assertIn("model?.rankingProfile?.boards?.[boardId]?.score", app_js)
        self.assertIn("function scoreModelForCustomMethodRanks(model)", app_js)
        self.assertIn("function scoreModelForCustomBoards(model)", app_js)
        self.assertIn("rasch: 0", app_js)
        self.assertIn("sparseRasch: 30", app_js)
        self.assertIn("twopl: 70", app_js)
        self.assertIn("denseRasch: 0", app_js)
        self.assertIn('customMethodAggregator: "mean"', app_js)
        self.assertIn('customBoardAggregator: "arithmetic"', app_js)
        self.assertIn("customMetricGroups", app_js)
        self.assertIn("customMissingMode", app_js)

    def test_benchmark_lab_manual_controls_preserve_base_missing_strategy(self):
        app_js = (Path(__file__).resolve().parents[1] / "docs" / "app.js").read_text(
            encoding="utf-8"
        )
        score_source = app_js.split("function scoreModelForBenchmarkWeights(model)", 1)[
            1
        ].split("\nfunction ", 1)[0]
        prior_source = app_js.split("function customMetricGroupPriorValue(", 1)[1].split(
            "\nfunction ", 1
        )[0]
        export_source = app_js.split("function exportCustomConfiguration()", 1)[
            1
        ].split("\nfunction ", 1)[0]

        self.assertIn('customMissingBaseMode: "coverage025"', app_js)
        self.assertIn('state.customMissingBaseMode === "weakPrior"', score_source)
        self.assertIn("state.customCoverageDiscountExponent", score_source)
        self.assertIn("score *= weightCoverageRatio ** coverageExponent", score_source)
        self.assertIn("score += (zeroScore - score) * penaltyRatio", score_source)
        self.assertLess(
            score_source.index('state.customMissingBaseMode === "weakPrior"'),
            score_source.index("score *= weightCoverageRatio ** coverageExponent"),
        )
        self.assertLess(
            score_source.index("score *= weightCoverageRatio ** coverageExponent"),
            score_source.index("score += (zeroScore - score) * penaltyRatio"),
        )
        self.assertNotIn('state.customMissingMode === "coverage', score_source)
        self.assertIn('normalization === "relative-best"', prior_source)
        self.assertIn("baseline * priorRatio", prior_source)
        for field in (
            "missingBaseMode",
            "penaltyMax",
            "coverageDiscountExponent",
            "weakPriorRatio",
            "minCoveragePct",
        ):
            self.assertIn(field, export_source)

    def test_benchmark_lab_manual_weights_do_not_switch_metric_aliases(self):
        app_js = (Path(__file__).resolve().parents[1] / "docs" / "app.js").read_text(
            encoding="utf-8"
        )
        value_source = app_js.split("function customMetricGroupValue(", 1)[1].split(
            "\nfunction ", 1
        )[0]

        self.assertIn('const customManualWeightPresetId = "manual"', app_js)
        self.assertIn("state.customWeightPresetId = customManualWeightPresetId", app_js)
        self.assertNotIn('state.customWeightPresetId = "custom"', app_js)
        self.assertIn("state.data.presets.custom?.weights", value_source)
        self.assertIn("canonicalMetrics", value_source)
        self.assertNotIn("state.customWeightPresetId", value_source)

    def test_all_three_custom_tools_apply_the_publication_order(self):
        app_js = (Path(__file__).resolve().parents[1] / "docs" / "app.js").read_text(
            encoding="utf-8"
        )
        for function_name in (
            "scoreModelForCustomMethodRanks",
            "scoreModelForCustomBoards",
            "scoreModelForBenchmarkWeights",
        ):
            source = app_js.split(f"function {function_name}(model)", 1)[1].split(
                "\nfunction ", 1
            )[0]
            self.assertIn("customPublicationRanking: true", source)

        publication_source = app_js.split("function applyCustomPublicationLayer(", 1)[
            1
        ].split("\nfunction ", 1)[0]
        self.assertIn('model.slug === "claude-fable-5"', publication_source)
        self.assertIn('model.variantGroup === "gpt 5 6 sol"', publication_source)
        self.assertIn("if (!fable || !sol) return evidenceRows;", publication_source)
        self.assertIn("publicationRank: index + 1", publication_source)
        benchmark_ui = app_js.split("function renderBenchmarkWeightLab(", 1)[1].split(
            "\nfunction ", 1
        )[0]
        self.assertIn('tr("publicationLayerNote")', benchmark_ui)
        self.assertIn("均有真实可计算结果", app_js)
        self.assertIn("both models have observed, calculable results", app_js)

    def test_unranked_sibling_variants_do_not_render_null_rank(self):
        app_js = (Path(__file__).resolve().parents[1] / "docs" / "app.js").read_text(
            encoding="utf-8"
        )
        sibling_source = app_js.split("function renderSiblingVariants(", 1)[1].split(
            "\nfunction ", 1
        )[0]

        self.assertIn("Number.isFinite(row.rank)", sibling_source)
        self.assertIn('escapeHtml(tr("notAvailable"))', sibling_source)
        self.assertNotIn("<span>#${row.rank}</span>", sibling_source)

    def test_methodology_page_is_linked_from_ranking_not_navigation(self):
        docs_dir = Path(__file__).resolve().parents[1] / "docs"
        html = (docs_dir / "methodology.html").read_text(encoding="utf-8")
        full_rank_html = (docs_dir / "full-rank.html").read_text(encoding="utf-8")
        app_js = (docs_dir / "app.js").read_text(encoding="utf-8")
        app_utils = (docs_dir / "app-utils.js").read_text(encoding="utf-8")
        methodology_source = app_js.split("function renderMethodologyPage()", 1)[
            1
        ].split("\nfunction ", 1)[0]

        self.assertIn("AInsights Index", html)
        self.assertIn("AIndex", html)
        self.assertIn('<html lang="en">', html)
        for section in (
            "Default Ranking at a Glance",
            "Capability Boards",
            "Item Pools and Sensitivity Methods",
            "Calculation Formula",
            "Evidence Eligibility and Coverage",
            "Publication Order",
            "Radar Profile",
            "Metric Weights and Custom Tools",
        ):
            self.assertIn(section, html)

        self.assertIn(
            "rank_mean = 0.70 × twopl_evidence_rank + 0.30 × sparse_evidence_rank",
            html,
        )
        self.assertIn("Core Rasch", html)
        self.assertIn("Sparse Rasch", html)
        self.assertIn("Equal-board 2PL", html)
        self.assertIn("Dense Rasch", html)
        self.assertEqual(html.count("<td>20%</td>"), 5)
        self.assertIn("at least two canonical benchmark families", html)
        self.assertIn("at least three in every board", html)
        self.assertIn("Coverage controls eligibility and labels", html)
        self.assertIn("it does not modify a qualified model's observed IRT score", html)
        self.assertIn("Claude Fable 5", html)
        self.assertIn("GPT-5.6 Sol", html)
        self.assertIn("evidence_rank", html)
        self.assertIn("there is no 40 / 24 / 20 / 8 / 8 board weighting", html)
        for runtime_term in (
            "Core Rasch",
            "Sparse Rasch",
            "Equal-board 2PL",
            "Dense Rasch",
            "rank_mean",
            "Claude Fable 5",
            "GPT-5.6 Sol",
        ):
            self.assertIn(runtime_term, methodology_source)

        for obsolete in (
            "Coding 40、Agentic/tool work 24、Hard reasoning 20",
            "Coding 40, Agentic/tool work 24, Hard reasoning 20",
            "重点提高 Coding、Agentic/tool work 和 Hard reasoning 对最终排名的影响",
            "with extra emphasis on Coding, Agentic/tool work, and Hard reasoning",
            "再进入最终几何加权总分",
            "then those board scores enter the final geometric weighted mean",
            "<td>40</td>",
            "<td>24</td>",
            "AIndex = AA Intelligence max *",
            "默认 AIndex 使用五板块弱先验口径",
            "default AIndex uses five weak-prior capability boards",
            "AInsights Index / AIndex 默认使用几何加权均值",
            "AInsights Index / AIndex defaults to geometric weighted mean",
            "boards enter the final geometric weighted mean",
        ):
            self.assertNotIn(obsolete, html)
            self.assertNotIn(obsolete, app_js)

        self.assertIn("methodology.html", app_js)
        self.assertIn('href="methodology.html"', full_rank_html)
        self.assertIn('filename === "methodology.html"', app_utils)
        self.assertIn('if (page === "methodology") return "methodology.html";', app_utils)
        self.assertIn('const pageOrder = ["home", "ranking", "compare", "benchmarks", "sources", "contribute"];', app_js)

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
        self.assertIn("detail-nav", app_js)
        self.assertIn("detail-compare-link", app_js)
        self.assertIn("modelCompareHref(model)", app_js)
        self.assertIn('class="back-link detail-compare-link"', app_js)
        self.assertIn('renderIcon("arrowRight")', app_js)
        self.assertIn('arrowRight:', app_js)
        self.assertNotIn('compare-entry-link detail-compare-link', app_js)
        self.assertIn("applyRankingStateFromUrl", app_js)
        self.assertIn("syncRankingUrl", app_js)
        self.assertIn("rankingHref(source)", app_js)
        self.assertIn('params.set("preset", presetId)', app_js)
        self.assertIn('params.set("view", viewMode)', app_js)
        self.assertIn('params.set("q", query)', app_js)
        self.assertIn('params.set("source", sourceFilter)', app_js)
        self.assertIn('params.set("dedupe", dedupe ? "1" : "0")', app_js)
        self.assertIn("data-provider-return", app_js)
        self.assertNotIn("latest-model-actions", app_js)
        self.assertIn('class="compare-entry-link"', app_js)
        self.assertIn(".detail-nav", css)
        self.assertIn(".detail-compare-link", css)
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
