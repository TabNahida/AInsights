import json
import tempfile
import unittest
from pathlib import Path
from urllib.error import URLError

from benchmarks.discover_official_vendor_pages import (
    DEEPSEEK_SITEMAP_URL,
    GLM_LLMS_URL,
    KIMI_SITEMAP_URL,
    QWEN_ARTICLE_API_URL,
    discover_manifest,
    parse_deepseek_sitemap,
    parse_glm_llms,
    parse_kimi_sitemap,
    parse_qwen_articles,
    write_manifest,
)


def _qwen_payload():
    return json.dumps(
        {
            "success": True,
            "data": {
                "articles": [
                    {
                        "id": "article-38",
                        "type": "qwen_ai",
                        "language": "en-US",
                        "path": "qwen3.8",
                        "title": "Qwen3.8-Max: A New Bar for Coding and Cowork",
                        "extra": {
                            "date": "2026-08-03T10:00:00+08:00",
                            "author": "QwenTeam",
                            "tags": ["Open-Source"],
                            "readTime": 25,
                            "wordCount": 5068,
                        },
                    },
                    {
                        "id": "image-3",
                        "type": "qwen_ai",
                        "path": "qwen-image-3.0",
                        "title": "Qwen-Image-3.0: Rich Content",
                        "extra": {"tags": ["Release"]},
                    },
                    {
                        "id": "research",
                        "type": "qwen_ai",
                        "path": "qwen-deepresearch",
                        "title": "Qwen DeepResearch: A New Workflow",
                    },
                ]
            },
        }
    )


def _glm_llms():
    return """
# Z.AI docs
- [GLM-5.3](https://docs.z.ai/guides/llm/glm-5.3.md)
- [GLM-5V-Turbo](https://docs.z.ai/guides/vlm/glm-5v-turbo.md)
- [GLM-6](https://docs.z.ai/guides/overview/glm-6.md)
- [GLM-99](https://docs.z.ai.evil.example/guides/llm/glm-99.md)
- [Quick Start](https://docs.z.ai/guides/overview/quick-start.md)
"""


def _kimi_sitemap():
    return """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
  <url>
    <loc>https://www.kimi.com/blog/kimi-k3</loc>
    <news:title>Kimi K3 Tech Blog: Open Frontier Intelligence</news:title>
  </url>
  <url><loc>https://www.kimi.com/resources/kimi-k2-7-code</loc></url>
  <url><loc>https://www.kimi.com/blog/company-update</loc></url>
  <url><loc>https://www.kimi.com.evil.example/blog/kimi-k9</loc></url>
  <url><loc>https://www.kimi.com/blog/kimi-k4?redirect=evil</loc></url>
</urlset>
"""


def _deepseek_sitemap():
    return """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://api-docs.deepseek.com/news/news260813</loc></url>
  <url><loc>https://api-docs.deepseek.com/news/news260900</loc></url>
  <url><loc>https://api-docs.deepseek.com/news/news260901</loc></url>
  <url><loc>https://api-docs.deepseek.com/api/create-chat-completion</loc></url>
  <url><loc>https://api-docs.deepseek.com.evil.example/news/news260999</loc></url>
</urlset>
"""


class OfficialVendorPageDiscoveryTests(unittest.TestCase):
    def test_qwen_json_keeps_llm_release_and_unpacks_metadata(self):
        pages = parse_qwen_articles(_qwen_payload())

        self.assertEqual(len(pages), 1)
        page = pages[0]
        self.assertEqual(page["vendor"], "qwen")
        self.assertEqual(page["name"], "Qwen3.8-Max")
        self.assertEqual(page["displayName"], "Qwen3.8 Max")
        self.assertEqual(page["url"], "https://qwen.ai/blog?id=qwen3.8")
        self.assertEqual(
            page["rawUrl"],
            "https://qwen.ai/api/v2/article/retrieval?language=en-US&path=qwen3.8&type=qwen_ai",
        )
        self.assertEqual(page["sourceKey"], "qwen-article-json")
        self.assertIn("qwen3-8-max", page["aliases"])
        self.assertEqual(page["sourceMetadata"]["articleId"], "article-38")
        self.assertEqual(
            page["sourceMetadata"]["publishedAt"],
            "2026-08-03T10:00:00+08:00",
        )

    def test_glm_llms_accepts_only_fixed_first_party_llm_path(self):
        pages = parse_glm_llms(_glm_llms())

        self.assertEqual([page["name"] for page in pages], ["GLM-5.3"])
        self.assertEqual(
            pages[0]["rawUrl"],
            "https://docs.z.ai/guides/llm/glm-5.3.md",
        )
        self.assertEqual(
            pages[0]["url"],
            "https://docs.z.ai/guides/llm/glm-5.3",
        )

    def test_kimi_sitemap_accepts_only_model_blog_and_resource_paths(self):
        pages = parse_kimi_sitemap(_kimi_sitemap())

        self.assertEqual(
            {page["name"] for page in pages},
            {"Kimi K3", "Kimi K2.7 Code"},
        )
        k3 = next(page for page in pages if page["name"] == "Kimi K3")
        self.assertEqual(k3["sourceKey"], "kimi-blog-sitemap")
        self.assertEqual(
            k3["title"],
            "Kimi K3 Tech Blog: Open Frontier Intelligence",
        )

    def test_kimi_sitemap_index_expands_only_same_host_xml_children(self):
        index = """<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
          <sitemap><loc>https://www.kimi.com/sitemaps/blog.xml</loc></sitemap>
          <sitemap><loc>https://evil.example/kimi.xml</loc></sitemap>
        </sitemapindex>"""
        calls = []

        def fetcher(url, _timeout):
            calls.append(url)
            return _kimi_sitemap()

        pages = parse_kimi_sitemap(index, fetcher=fetcher)

        self.assertEqual(calls, ["https://www.kimi.com/sitemaps/blog.xml"])
        self.assertEqual(len(pages), 2)

    def test_deepseek_resolves_titles_and_filters_non_model_news(self):
        responses = {
            "https://api-docs.deepseek.com/news/news260813": (
                "<html><head><title>DeepSeek-V4-Pro GA Release | "
                "DeepSeek API Docs</title></head></html>"
            ),
            "https://api-docs.deepseek.com/news/news260900": (
                "<html><head><meta property='og:title' "
                "content='Introducing DeepSeek-R2'/></head></html>"
            ),
            "https://api-docs.deepseek.com/news/news260901": (
                "<html><head><title>DeepSeek API Context Caching Update | "
                "DeepSeek API Docs</title></head></html>"
            ),
        }

        pages = parse_deepseek_sitemap(
            _deepseek_sitemap(),
            fetcher=lambda url, _timeout: responses[url],
        )

        self.assertEqual(
            {page["name"] for page in pages},
            {"DeepSeek-V4-Pro", "DeepSeek-R2"},
        )
        self.assertTrue(
            all(page["sourceKey"] == "deepseek-api-docs-sitemap" for page in pages)
        )

    def test_failed_refresh_preserves_valid_previous_source_entries(self):
        previous_page = parse_qwen_articles(_qwen_payload())[0]
        previous = {"pages": [previous_page]}

        def blocked(_url, _timeout):
            raise URLError("temporary")

        manifest, statuses = discover_manifest(previous, fetcher=blocked)

        self.assertEqual(manifest["pages"], [previous_page])
        self.assertNotIn("generatedAt", manifest)
        self.assertIn(
            "preserved 1; refresh blocked: URLError",
            statuses["qwen-article-json"],
        )

    def test_write_manifest_is_stable_and_uses_injected_network(self):
        deep_pages = {
            "https://api-docs.deepseek.com/news/news260813": (
                "<title>DeepSeek-V4-Pro GA Release | DeepSeek API Docs</title>"
            ),
            "https://api-docs.deepseek.com/news/news260900": (
                "<title>Introducing DeepSeek-R2 | DeepSeek API Docs</title>"
            ),
            "https://api-docs.deepseek.com/news/news260901": (
                "<title>DeepSeek API Context Caching Update | DeepSeek API Docs</title>"
            ),
        }
        responses = {
            QWEN_ARTICLE_API_URL: _qwen_payload(),
            GLM_LLMS_URL: _glm_llms(),
            KIMI_SITEMAP_URL: _kimi_sitemap(),
            DEEPSEEK_SITEMAP_URL: _deepseek_sitemap(),
            **deep_pages,
        }

        def fetcher(url, _timeout):
            return responses[url]

        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "official_vendor_pages.json"
            first, first_statuses = write_manifest(output, fetcher=fetcher)
            first_bytes = output.read_bytes()
            second, second_statuses = write_manifest(output, fetcher=fetcher)

            self.assertEqual(first, second)
            self.assertEqual(first_statuses, second_statuses)
            self.assertEqual(first_bytes, output.read_bytes())
            self.assertNotIn("generatedAt", first)
            self.assertEqual(first["version"], 1)
            self.assertEqual(len(first["sources"]), 4)
            self.assertTrue(
                all(
                    {
                        "vendor",
                        "name",
                        "displayName",
                        "url",
                        "rawUrl",
                        "aliases",
                        "sourceKey",
                    }.issubset(page)
                    for page in first["pages"]
                )
            )


if __name__ == "__main__":
    unittest.main()
