"""Discover model-release pages from official Qwen, GLM, Kimi, and DeepSeek indexes.

The manifest produced here is intentionally deterministic: it contains no scan
timestamp, and a temporarily unavailable vendor index retains that source's
previously discovered entries.  Only tightly scoped first-party URL shapes are
accepted, so an official index cannot accidentally turn this into a general
web crawler.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from html.parser import HTMLParser
from http.client import IncompleteRead
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_JSON = PROJECT_ROOT / "data" / "benchmarks" / "official_vendor_pages.json"

QWEN_ARTICLE_API_URL = (
    "https://qwen.ai/api/v2/article/retrieval?language=en-US&type=qwen_ai"
)
GLM_LLMS_URL = "https://docs.z.ai/llms.txt"
KIMI_SITEMAP_URL = "https://www.kimi.com/sitemap.xml"
DEEPSEEK_SITEMAP_URL = "https://api-docs.deepseek.com/sitemap.xml"


@dataclass(frozen=True)
class VendorSource:
    key: str
    vendor: str
    kind: str
    url: str


OFFICIAL_SOURCES = (
    VendorSource("qwen-article-json", "qwen", "json-api", QWEN_ARTICLE_API_URL),
    VendorSource("glm-docs-llms", "glm", "llms-txt", GLM_LLMS_URL),
    VendorSource("kimi-blog-sitemap", "kimi", "sitemap", KIMI_SITEMAP_URL),
    VendorSource(
        "deepseek-api-docs-sitemap",
        "deepseek",
        "sitemap",
        DEEPSEEK_SITEMAP_URL,
    ),
)

FetchText = Callable[[str, float], str]

QWEN_PATH_RE = re.compile(r"^qwen\d+(?:[.-][a-z0-9]+)*$", re.IGNORECASE)
QWEN_MODEL_RE = re.compile(
    r"\bQwen\s*\d+(?:\.\d+)*(?:-[A-Za-z0-9.]+)*",
    re.IGNORECASE,
)
QWEN_NON_LLM_RE = re.compile(
    r"(?:^|[-_.])(?:"
    r"asr|audio|embedding|forcedaligner|image|livetranslate|omni|reranker|"
    r"robot|tts|video|vl|vla"
    r")(?:$|[-_.])",
    re.IGNORECASE,
)
GLM_RAW_PATH_RE = re.compile(
    r"^/guides/llm/(glm-[a-z0-9.-]+)\.md$",
    re.IGNORECASE,
)
GLM_PAGE_PATH_RE = re.compile(
    r"^/guides/llm/glm-[a-z0-9.-]+$",
    re.IGNORECASE,
)
GLM_TITLE_RE = re.compile(r"^GLM[- ]?\d", re.IGNORECASE)
KIMI_PATH_RE = re.compile(
    r"^/(?:blog|resources)/(kimi-k\d+(?:[.-][a-z0-9]+)*)/?$",
    re.IGNORECASE,
)
DEEPSEEK_PATH_RE = re.compile(
    r"^(?:/news/news\d{4,8}|/updates(?:/[a-z0-9._-]+)?)/?$",
    re.IGNORECASE,
)
DEEPSEEK_MODEL_RE = re.compile(
    r"\bDeepSeek(?:\s*-\s*|\s+)((?:V|R)\d+(?:\.\d+)*(?:-[A-Za-z0-9.]+)*)",
    re.IGNORECASE,
)
MARKDOWN_LINK_RE = re.compile(r"^\s*-\s*\[([^\]]+)\]\(([^)]+)\)", re.MULTILINE)


def fetch_text(url: str, timeout: float = 30) -> str:
    """Fetch UTF-8-ish text with a crawler-specific, non-browser identity."""

    request = Request(
        url,
        headers={
            "User-Agent": "AInsights official-vendor-page discovery/1.0",
            "Accept": "application/json,text/plain,application/xml,text/xml,text/html,*/*",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def _split_strict_https(url: str, host: str):
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError:
        return None
    if (
        parsed.scheme != "https"
        or parsed.hostname != host
        or port is not None
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
    ):
        return None
    return parsed


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", html.unescape(str(value or ""))).strip()


def _display_name(name: str) -> str:
    return re.sub(r"[-_]+", " ", name).strip()


def _aliases(name: str, display_name: str, *extra: str) -> list[str]:
    spaced = re.sub(r"[-_]+", " ", name).strip()
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    aliases: list[str] = []
    for alias in (display_name, name, spaced, slug, *extra):
        alias = _clean_text(alias)
        if alias and alias not in aliases:
            aliases.append(alias)
    return aliases


def _entry(
    source: VendorSource,
    *,
    name: str,
    url: str,
    raw_url: str,
    title: str = "",
    aliases: list[str] | None = None,
    source_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    display_name = _display_name(name)
    result: dict[str, Any] = {
        "vendor": source.vendor,
        "name": name,
        "displayName": display_name,
        "url": url,
        "rawUrl": raw_url,
        "aliases": aliases or _aliases(name, display_name),
        "sourceKey": source.key,
    }
    if title:
        result["title"] = title
    if source_metadata:
        result["sourceMetadata"] = source_metadata
    return result


def _qwen_raw_url(path: str) -> str:
    query = urlencode(
        {
            "language": "en-US",
            "path": path,
            "type": "qwen_ai",
        }
    )
    return f"https://qwen.ai/api/v2/article/retrieval?{query}"


def _normalise_qwen_name(token: str) -> str:
    token = re.sub(r"^qwen\s*", "Qwen", token, flags=re.IGNORECASE)
    parts = token.split("-")
    normalised = [parts[0]]
    for part in parts[1:]:
        if re.fullmatch(r"\d+[bB]", part):
            normalised.append(part.upper())
        elif re.fullmatch(r"[aA]\d+[bB]", part):
            normalised.append(part.upper())
        else:
            normalised.append(part[:1].upper() + part[1:])
    return "-".join(normalised)


def parse_qwen_articles(text: str) -> list[dict[str, Any]]:
    """Parse the Qwen article API and retain language-model release articles."""

    payload = json.loads(text)
    if not isinstance(payload, dict) or payload.get("success") is False:
        raise ValueError("Qwen returned an unsuccessful or non-object payload")
    data = payload.get("data")
    articles = data.get("articles") if isinstance(data, dict) else None
    if not isinstance(articles, list):
        raise ValueError("Qwen payload has no articles list")

    source = OFFICIAL_SOURCES[0]
    pages: list[dict[str, Any]] = []
    for article in articles:
        if not isinstance(article, dict):
            continue
        path = str(article.get("path") or "").strip()
        title = _clean_text(article.get("title"))
        if (
            not QWEN_PATH_RE.fullmatch(path)
            or QWEN_NON_LLM_RE.search(path)
            or QWEN_NON_LLM_RE.search(title)
            or (article.get("type") not in (None, "", "qwen_ai"))
        ):
            continue
        match = QWEN_MODEL_RE.search(title)
        if not match:
            continue
        name = _normalise_qwen_name(match.group(0))
        url = f"https://qwen.ai/blog?{urlencode({'id': path})}"
        extra = article.get("extra") if isinstance(article.get("extra"), dict) else {}
        metadata: dict[str, Any] = {
            "articleId": str(article.get("id") or ""),
            "path": path,
            "type": str(article.get("type") or "qwen_ai"),
            "language": str(article.get("language") or ""),
        }
        metadata_map = {
            "date": "publishedAt",
            "author": "author",
            "tags": "tags",
            "description": "description",
            "readTime": "readTime",
            "wordCount": "wordCount",
        }
        for source_key, output_key in metadata_map.items():
            value = extra.get(source_key)
            if value not in (None, "", []):
                if source_key == "tags" and isinstance(value, list):
                    value = sorted(
                        {
                            str(tag)
                            for tag in value
                            if isinstance(tag, str) and tag.strip()
                        }
                    )
                metadata[output_key] = value
        pages.append(
            _entry(
                source,
                name=name,
                url=url,
                raw_url=_qwen_raw_url(path),
                title=title,
                source_metadata=metadata,
            )
        )
    return _deduplicate_pages(pages)


def parse_glm_llms(text: str) -> list[dict[str, Any]]:
    """Parse only GLM LLM guide links from Z.AI's llms.txt."""

    source = OFFICIAL_SOURCES[1]
    pages: list[dict[str, Any]] = []
    for raw_title, raw_url in MARKDOWN_LINK_RE.findall(text):
        title = _clean_text(raw_title)
        raw_url = html.unescape(raw_url.strip())
        parsed = _split_strict_https(raw_url, "docs.z.ai")
        if (
            parsed is None
            or parsed.query
            or not GLM_TITLE_RE.search(title)
            or not GLM_RAW_PATH_RE.fullmatch(parsed.path)
        ):
            continue
        page_path = parsed.path[:-3]
        url = urlunsplit(("https", "docs.z.ai", page_path, "", ""))
        pages.append(
            _entry(
                source,
                name=title,
                url=url,
                raw_url=raw_url,
                title=title,
            )
        )
    return _deduplicate_pages(pages)


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _parse_sitemap_document(text: str) -> tuple[str, list[tuple[str, str]]]:
    if "<!DOCTYPE" in text.upper():
        raise ValueError("Sitemap document types are not accepted")
    root = ET.fromstring(text)
    kind = _local_name(root.tag)
    if kind not in {"urlset", "sitemapindex"}:
        raise ValueError(f"Unexpected sitemap root: {kind}")

    records: list[tuple[str, str]] = []
    expected_item = "url" if kind == "urlset" else "sitemap"
    for item in root:
        if _local_name(item.tag) != expected_item:
            continue
        loc = ""
        title = ""
        for child in item:
            child_name = _local_name(child.tag)
            if child_name == "loc" and not loc:
                loc = _clean_text(child.text)
            elif child_name == "title" and not title:
                title = _clean_text(child.text)
        if loc:
            records.append((loc, title))
    return kind, records


def _sitemap_records(
    text: str,
    *,
    host: str,
    timeout: float,
    fetcher: FetchText,
) -> list[tuple[str, str]]:
    kind, records = _parse_sitemap_document(text)
    if kind == "urlset":
        return records

    expanded: list[tuple[str, str]] = []
    for child_url, _title in records:
        parsed = _split_strict_https(child_url, host)
        if (
            parsed is None
            or parsed.query
            or not parsed.path.lower().endswith(".xml")
        ):
            continue
        child_kind, child_records = _parse_sitemap_document(
            fetcher(child_url, timeout)
        )
        if child_kind != "urlset":
            raise ValueError("Nested sitemap indexes are not accepted")
        expanded.extend(child_records)
    return expanded


def _kimi_name_from_path(path: str) -> str:
    match = KIMI_PATH_RE.fullmatch(path)
    if not match:
        return ""
    slug = match.group(1).lower()
    tokens = re.split(r"[-.]", slug[len("kimi-k") :])
    if not tokens or not tokens[0].isdigit():
        return ""
    version = tokens.pop(0)
    if tokens and tokens[0].isdigit() and len(tokens[0]) <= 2:
        version += f".{tokens.pop(0)}"
    suffix = " ".join(token.upper() if token in {"ai"} else token.title() for token in tokens)
    return f"Kimi K{version}" + (f" {suffix}" if suffix else "")


def parse_kimi_sitemap(
    text: str,
    *,
    timeout: float = 30,
    fetcher: FetchText = fetch_text,
) -> list[dict[str, Any]]:
    """Parse Kimi model blog/resource URLs from its official sitemap."""

    source = OFFICIAL_SOURCES[2]
    records = _sitemap_records(
        text,
        host="www.kimi.com",
        timeout=timeout,
        fetcher=fetcher,
    )
    pages: list[dict[str, Any]] = []
    for raw_url, sitemap_title in records:
        parsed = _split_strict_https(raw_url, "www.kimi.com")
        if parsed is None or parsed.query or not KIMI_PATH_RE.fullmatch(parsed.path):
            continue
        name = _kimi_name_from_path(parsed.path)
        if not name:
            continue
        canonical_url = urlunsplit(("https", "www.kimi.com", parsed.path.rstrip("/"), "", ""))
        pages.append(
            _entry(
                source,
                name=name,
                url=canonical_url,
                raw_url=canonical_url,
                title=sitemap_title,
            )
        )
    return _deduplicate_pages(pages)


class _HTMLTitleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._in_title = False
        self._title_parts: list[str] = []
        self.meta_title = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "title":
            self._in_title = True
        if tag.lower() != "meta" or self.meta_title:
            return
        values = {key.lower(): value or "" for key, value in attrs}
        if values.get("property", "").lower() == "og:title":
            self.meta_title = values.get("content", "")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_parts.append(data)

    @property
    def title(self) -> str:
        return _clean_text("".join(self._title_parts) or self.meta_title)


def extract_html_title(text: str) -> str:
    parser = _HTMLTitleParser()
    parser.feed(text)
    return re.sub(r"\s*\|\s*DeepSeek API Docs\s*$", "", parser.title).strip()


def _deepseek_name_from_title(title: str) -> str:
    match = DEEPSEEK_MODEL_RE.search(title)
    if not match:
        return ""
    suffix = match.group(1)
    parts = suffix.split("-")
    parts[0] = parts[0].upper().replace("V", "V").replace("R", "R")
    return "DeepSeek-" + "-".join(parts)


def parse_deepseek_sitemap(
    text: str,
    *,
    timeout: float = 30,
    fetcher: FetchText = fetch_text,
    previous: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Resolve DeepSeek news titles, then keep explicit V/R model releases."""

    source = OFFICIAL_SOURCES[3]
    records = _sitemap_records(
        text,
        host="api-docs.deepseek.com",
        timeout=timeout,
        fetcher=fetcher,
    )
    previous_by_url = {
        str(page.get("url") or ""): page
        for page in previous or []
        if isinstance(page, dict)
    }
    candidates: list[tuple[str, str]] = []
    for raw_url, sitemap_title in records:
        parsed = _split_strict_https(raw_url, "api-docs.deepseek.com")
        if parsed is None or parsed.query or not DEEPSEEK_PATH_RE.fullmatch(parsed.path):
            continue
        canonical_url = urlunsplit(
            ("https", "api-docs.deepseek.com", parsed.path.rstrip("/"), "", "")
        )
        candidates.append((canonical_url, sitemap_title))

    def resolve(record: tuple[str, str]) -> tuple[str, str, bool]:
        url, sitemap_title = record
        if sitemap_title:
            return url, sitemap_title, True
        try:
            return url, extract_html_title(fetcher(url, timeout)), True
        except Exception:
            return url, "", False

    pages: list[dict[str, Any]] = []
    max_workers = min(6, len(candidates)) or 1
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        resolved = list(executor.map(resolve, candidates))
    for url, title, refreshed in resolved:
        if not refreshed:
            prior = previous_by_url.get(url)
            if prior and _candidate_is_official(prior, source):
                pages.append(dict(prior))
            continue
        name = _deepseek_name_from_title(title)
        if not name:
            continue
        pages.append(
            _entry(
                source,
                name=name,
                url=url,
                raw_url=url,
                title=title,
            )
        )
    return _deduplicate_pages(pages)


def _deduplicate_pages(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_url = {str(page["url"]): page for page in pages if page.get("url")}
    return sorted(
        by_url.values(),
        key=lambda page: (
            str(page.get("name") or "").casefold(),
            str(page.get("url") or ""),
        ),
    )


def _qwen_candidate_is_official(page: dict[str, Any]) -> bool:
    url = _split_strict_https(str(page.get("url") or ""), "qwen.ai")
    raw = _split_strict_https(str(page.get("rawUrl") or ""), "qwen.ai")
    if url is None or raw is None or url.path != "/blog" or raw.path != "/api/v2/article/retrieval":
        return False
    page_query = parse_qs(url.query, keep_blank_values=True)
    raw_query = parse_qs(raw.query, keep_blank_values=True)
    return (
        set(page_query) == {"id"}
        and len(page_query["id"]) == 1
        and QWEN_PATH_RE.fullmatch(page_query["id"][0]) is not None
        and set(raw_query) == {"language", "path", "type"}
        and raw_query.get("language") == ["en-US"]
        and raw_query.get("type") == ["qwen_ai"]
        and raw_query.get("path") == page_query.get("id")
    )


def _candidate_is_official(page: dict[str, Any], source: VendorSource) -> bool:
    if page.get("vendor") != source.vendor or page.get("sourceKey") != source.key:
        return False
    if not all(page.get(key) for key in ("name", "displayName", "url", "rawUrl", "aliases")):
        return False
    if source.vendor == "qwen":
        return _qwen_candidate_is_official(page)
    if source.vendor == "glm":
        url = _split_strict_https(str(page["url"]), "docs.z.ai")
        raw = _split_strict_https(str(page["rawUrl"]), "docs.z.ai")
        return bool(
            url
            and raw
            and not url.query
            and not raw.query
            and GLM_PAGE_PATH_RE.fullmatch(url.path)
            and GLM_RAW_PATH_RE.fullmatch(raw.path)
            and raw.path[:-3] == url.path
        )
    if source.vendor == "kimi":
        url = _split_strict_https(str(page["url"]), "www.kimi.com")
        raw = _split_strict_https(str(page["rawUrl"]), "www.kimi.com")
        return bool(
            url
            and raw
            and not url.query
            and not raw.query
            and KIMI_PATH_RE.fullmatch(url.path)
            and raw.path == url.path
        )
    if source.vendor == "deepseek":
        url = _split_strict_https(str(page["url"]), "api-docs.deepseek.com")
        raw = _split_strict_https(str(page["rawUrl"]), "api-docs.deepseek.com")
        return bool(
            url
            and raw
            and not url.query
            and not raw.query
            and DEEPSEEK_PATH_RE.fullmatch(url.path)
            and raw.path == url.path
        )
    return False


def _discover_source(
    source: VendorSource,
    text: str,
    *,
    timeout: float,
    fetcher: FetchText,
    previous: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if source.vendor == "qwen":
        return parse_qwen_articles(text)
    if source.vendor == "glm":
        return parse_glm_llms(text)
    if source.vendor == "kimi":
        return parse_kimi_sitemap(text, timeout=timeout, fetcher=fetcher)
    if source.vendor == "deepseek":
        return parse_deepseek_sitemap(
            text,
            timeout=timeout,
            fetcher=fetcher,
            previous=previous,
        )
    raise ValueError(f"Unsupported vendor source: {source.vendor}")


def discover_manifest(
    previous: dict[str, Any] | None = None,
    *,
    timeout: float = 30,
    fetcher: FetchText = fetch_text,
) -> tuple[dict[str, Any], dict[str, str]]:
    """Refresh every source independently and preserve prior entries on failure."""

    previous_pages = [
        page
        for page in (previous or {}).get("pages", [])
        if isinstance(page, dict)
    ]
    previous_by_source: dict[str, list[dict[str, Any]]] = {}
    for source in OFFICIAL_SOURCES:
        previous_by_source[source.key] = [
            dict(page)
            for page in previous_pages
            if _candidate_is_official(page, source)
        ]

    pages: list[dict[str, Any]] = []
    statuses: dict[str, str] = {}
    for source in OFFICIAL_SOURCES:
        prior = previous_by_source[source.key]
        try:
            text = fetcher(source.url, timeout)
            if not isinstance(text, str):
                raise ValueError("Fetcher returned non-text content")
            discovered = _discover_source(
                source,
                text,
                timeout=timeout,
                fetcher=fetcher,
                previous=prior,
            )
            discovered = [
                page for page in discovered if _candidate_is_official(page, source)
            ]
            if not discovered:
                raise ValueError("No explicit model-release pages were discovered")
        except (
            HTTPError,
            URLError,
            TimeoutError,
            OSError,
            IncompleteRead,
            json.JSONDecodeError,
            ET.ParseError,
            ValueError,
        ) as exc:
            pages.extend(prior)
            statuses[source.key] = (
                f"preserved {len(prior)}; refresh blocked: {exc.__class__.__name__}"
            )
            continue
        pages.extend(discovered)
        statuses[source.key] = f"refreshed; discovered {len(discovered)}"

    source_order = {source.key: index for index, source in enumerate(OFFICIAL_SOURCES)}
    pages.sort(
        key=lambda page: (
            source_order.get(str(page.get("sourceKey") or ""), len(source_order)),
            str(page.get("name") or "").casefold(),
            str(page.get("url") or ""),
        )
    )
    if not pages:
        raise RuntimeError(
            "No official vendor pages were discovered and no prior manifest exists"
        )

    manifest = {
        "version": 1,
        "sources": [
            {
                "key": source.key,
                "vendor": source.vendor,
                "kind": source.kind,
                "url": source.url,
            }
            for source in OFFICIAL_SOURCES
        ],
        "pages": pages,
    }
    return manifest, statuses


def load_previous_manifest(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def write_manifest(
    path: Path = DEFAULT_OUTPUT_JSON,
    *,
    timeout: float = 30,
    fetcher: FetchText = fetch_text,
) -> tuple[dict[str, Any], dict[str, str]]:
    manifest, statuses = discover_manifest(
        load_previous_manifest(path),
        timeout=timeout,
        fetcher=fetcher,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest, statuses


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Discover first-party Qwen, GLM, Kimi, and DeepSeek release pages."
    )
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--timeout", type=float, default=30)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        manifest, statuses = write_manifest(
            Path(args.output_json),
            timeout=args.timeout,
        )
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    details = "; ".join(
        f"{source_key}: {status}" for source_key, status in statuses.items()
    )
    print(
        f"Wrote {args.output_json} with {len(manifest['pages'])} official pages "
        f"({details})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
