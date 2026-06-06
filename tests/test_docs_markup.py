import unittest
from pathlib import Path


class DocsMarkupTests(unittest.TestCase):
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
        self.assertIn('id="modelView"', html)
        self.assertIn('id="modelDetail"', html)
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

        self.assertIn('max="20"', html)
        self.assertIn('step="0.01"', html)

    def test_full_ranking_views_are_not_hard_capped(self):
        app_js = (Path(__file__).resolve().parents[1] / "docs" / "app.js").read_text(encoding="utf-8")

        self.assertNotIn("ranked.slice(0, 250)", app_js)
        self.assertNotIn("models.slice(0, 120)", app_js)

    def test_custom_weights_include_source_weights_and_scatter_leaders(self):
        app_js = (Path(__file__).resolve().parents[1] / "docs" / "app.js").read_text(encoding="utf-8")
        css = (Path(__file__).resolve().parents[1] / "docs" / "styles.css").read_text(encoding="utf-8")

        self.assertIn("source-weight-controls", app_js)
        self.assertIn("combinedMetricWeightsFromSources", app_js)
        self.assertIn("scatter-leader", app_js)
        self.assertIn(".scatter-leader", css)
        self.assertNotIn("Open AA page", app_js)

    def test_model_icons_use_local_assets(self):
        data = (Path(__file__).resolve().parents[1] / "docs" / "data" / "models.json").read_text(encoding="utf-8")

        self.assertIn('"src": "assets/logos/', data)
        self.assertNotIn('"src": "https://artificialanalysis.ai/img/logos/', data)


if __name__ == "__main__":
    unittest.main()
