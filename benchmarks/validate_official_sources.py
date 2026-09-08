"""Validate first-party source policy for generated benchmark data."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BENCHMARKS_JSON = PROJECT_ROOT / "data" / "benchmarks" / "benchmark_scores.json"
DEFAULT_MANIFEST_JSON = PROJECT_ROOT / "data" / "benchmarks" / "official_model_cards.json"
DEFAULT_VENDOR_MANIFEST_JSON = (
    PROJECT_ROOT / "data" / "benchmarks" / "official_vendor_pages.json"
)

VERIFIED_HF_ORGANIZATIONS = {"Qwen", "zai-org", "moonshotai", "deepseek-ai"}

PRIMARY_VENDOR_SOURCE_URLS = {
    "openai-gpt-6-astra-release": "https://openai.com/index/gpt-6-astra/",
    "zai-glm-5-3-flash-release": "https://docs.z.ai/guides/llm/glm-5.3-flash",
    "deepseek-v4-flash-vision-exp-card": "https://api-docs.deepseek.com/news/news260821",
    "qwen-qwen3-release": "https://qwen.ai/blog?id=qwen3",
    "qwen-qwen2-release": "https://qwen.ai/blog?id=qwen2",
    "qwen-qwen2-5-release": "https://qwen.ai/blog?id=qwen2.5",
    "qwen-qwen2-5-coder-release": "https://qwen.ai/blog?id=qwen2.5-coder",
    "qwen-qwen2-5-max-release": "https://qwen.ai/blog?id=qwen2.5-max",
    "qwen-qwen3-6-27b-card": "https://qwen.ai/blog?id=qwen3.6-27b",
    "qwen-qwen3-6-plus-release": "https://qwen.ai/blog?id=qwen3.6",
    "qwen-qwen3-6-max-preview-release": "https://qwen.ai/blog?id=qwen3.6-max-preview",
    "qwen-qwen3-8-max-release": "https://qwen.ai/blog?id=qwen3.8",
    "deepseek-v4-pro-card": "https://api-docs.deepseek.com/news/news260424",
    "deepseek-v4-pro-0813-card": "https://api-docs.deepseek.com/news/news260813",
    "deepseek-v4-flash-0731-update": "https://api-docs.deepseek.com/updates/",
    "kimi-k3-release": "https://www.kimi.com/blog/kimi-k3",
    "kimi-k2-6-card": "https://www.kimi.com/blog/kimi-k2-6",
    "kimi-k2-7-code-card": "https://www.kimi.com/resources/kimi-k2-7-code",
    "kimi-k2-thinking-card": "https://moonshotai.github.io/Kimi-K2/thinking",
    "kimi-k2-5-card": "https://www.kimi.com/blog/kimi-k2-5",
    "zai-glm-4-6-card": "https://docs.z.ai/guides/llm/glm-4.6",
    "zai-glm-5-1-card": "https://docs.z.ai/guides/llm/glm-5.1",
    "zai-glm-5-2-card": "https://docs.z.ai/guides/llm/glm-5.2",
    "zai-glm-5-3-release": "https://z.ai/blog/glm-5.3",
}

PRIMARY_VENDOR_SOURCE_RAW_URLS = {
    "openai-gpt-6-astra-release": "https://openai.com/index/gpt-6-astra/",
    "zai-glm-5-3-flash-release": "https://docs.z.ai/guides/llm/glm-5.3-flash.md",
    "deepseek-v4-flash-vision-exp-card": "https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-Vision-Exp/raw/main/README.md",
    "qwen-qwen3-release": "https://qwen.ai/blog?id=qwen3",
    "qwen-qwen2-release": "https://qwenlm.github.io/blog/qwen2/",
    "qwen-qwen2-5-release": "https://qwen.ai/blog?id=qwen2.5",
    "qwen-qwen2-5-coder-release": "https://qwen.ai/blog?id=qwen2.5-coder",
    "qwen-qwen2-5-max-release": "https://qwen.ai/blog?id=qwen2.5-max",
    "qwen-qwen3-6-27b-card": "https://qwen.ai/blog?id=qwen3.6-27b",
    "qwen-qwen3-6-plus-release": "https://qwen.ai/blog?id=qwen3.6",
    "qwen-qwen3-6-max-preview-release": "https://qwen.ai/blog?id=qwen3.6-max-preview",
    "qwen-qwen3-8-max-release": (
        "https://qwen.ai/api/v2/article/retrieval?"
        "language=en-US&path=qwen3.8&type=qwen_ai"
    ),
    "deepseek-v4-pro-card": "https://api-docs.deepseek.com/news/news260424",
    "deepseek-v4-pro-0813-card": (
        "https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/raw/main/README.md"
    ),
    "deepseek-v4-flash-0731-update": "https://api-docs.deepseek.com/updates/",
    "kimi-k3-release": "https://huggingface.co/moonshotai/Kimi-K3/raw/main/README.md",
    "kimi-k2-6-card": "https://www.kimi.com/blog/kimi-k2-6",
    "kimi-k2-7-code-card": "https://www.kimi.com/resources/kimi-k2-7-code",
    "kimi-k2-thinking-card": "https://moonshotai.github.io/Kimi-K2/thinking",
    "kimi-k2-5-card": "https://www.kimi.com/blog/kimi-k2-5",
    "zai-glm-4-6-card": "https://docs.z.ai/guides/llm/glm-4.6",
    "zai-glm-5-1-card": "https://docs.z.ai/guides/llm/glm-5.1",
    "zai-glm-5-2-card": "https://huggingface.co/zai-org/GLM-5.2",
    "zai-glm-5-3-release": "https://docs.z.ai/guides/llm/glm-5.3.md",
}

PRIMARY_VENDOR_PAGE_SOURCE_IDS = set(PRIMARY_VENDOR_SOURCE_URLS)

OFFICIAL_HF_SOURCE_ORGS = {
    "qwen-qwen3-8-flash-next-card": "Qwen",
    "qwen-qwen3-8-27b-card": "Qwen",
    "kimi-k2-0905-card": "moonshotai",
}

OFFICIAL_HF_SOURCE_MODELS = {
    "qwen-qwen3-8-flash-next-card": "Qwen3.8-Flash-Next",
    "qwen-qwen3-8-27b-card": "Qwen3.8-27B",
    "kimi-k2-0905-card": "Kimi-K2-Instruct-0905",
}

EXPLICIT_HF_RAW_SOURCES = {
    "qwen-qwen3-8-flash-next-card": ("Qwen", "Qwen3.8-Flash-Next", "readme"),
    "deepseek-v4-flash-vision-exp-card": ("deepseek-ai", "DeepSeek-V4-Flash-Vision-Exp", "readme"),
    "qwen-qwen3-8-27b-card": ("Qwen", "Qwen3.8-27B", "readme"),
    "kimi-k2-0905-card": ("moonshotai", "Kimi-K2-Instruct-0905", "page"),
    "kimi-k3-release": ("moonshotai", "Kimi-K3", "readme"),
    "deepseek-v4-pro-0813-card": (
        "deepseek-ai",
        "DeepSeek-V4-Pro-0813",
        "readme",
    ),
    "zai-glm-5-2-card": ("zai-org", "GLM-5.2", "page"),
}

VENDOR_MANIFEST_SOURCES = {
    "qwen-article-json": (
        "qwen",
        "json-api",
        "https://qwen.ai/api/v2/article/retrieval?language=en-US&type=qwen_ai",
    ),
    "glm-docs-llms": ("glm", "llms-txt", "https://docs.z.ai/llms.txt"),
    "kimi-blog-sitemap": ("kimi", "sitemap", "https://www.kimi.com/sitemap.xml"),
    "deepseek-api-docs-sitemap": (
        "deepseek",
        "sitemap",
        "https://api-docs.deepseek.com/sitemap.xml",
    ),
}


def validate_payload(
    benchmark_payload: dict[str, Any],
    discovery_manifest: dict[str, Any] | None = None,
    vendor_manifest: dict[str, Any] | None = None,
) -> None:
    sources = {
        str(source.get("id") or ""): source
        for source in benchmark_payload.get("sources", [])
        if isinstance(source, dict) and source.get("id")
    }
    required_ids = PRIMARY_VENDOR_PAGE_SOURCE_IDS | set(OFFICIAL_HF_SOURCE_ORGS)
    missing = sorted(required_ids - set(sources))
    if missing:
        raise ValueError(f"required official sources are missing: {', '.join(missing)}")

    for source_id, expected_url in PRIMARY_VENDOR_SOURCE_URLS.items():
        _validate_exact_url(
            str(sources[source_id].get("url") or ""),
            expected_url,
            f"vendor page source {source_id}",
        )
        _validate_exact_url(
            str(sources[source_id].get("rawUrl") or ""),
            PRIMARY_VENDOR_SOURCE_RAW_URLS[source_id],
            f"raw source for {source_id}",
        )

    for source_id, organization in OFFICIAL_HF_SOURCE_ORGS.items():
        _validate_hf_model_url(
            str(sources[source_id].get("url") or ""),
            organization,
            OFFICIAL_HF_SOURCE_MODELS[source_id],
            kind="page",
        )

    for source_id, (organization, model_name, kind) in EXPLICIT_HF_RAW_SOURCES.items():
        _validate_hf_model_url(
            str(sources[source_id].get("rawUrl") or ""),
            organization,
            model_name,
            kind=kind,
        )

    for source in sources.values():
        if not source.get("autoDiscovered"):
            continue
        organization = str(source.get("organization") or "")
        if organization not in VERIFIED_HF_ORGANIZATIONS:
            raise ValueError(
                f"auto-discovered source {source.get('id')} uses unverified org {organization!r}"
            )
        _validate_hf_entry(source, f"auto-discovered source {source.get('id')}")

    for model in (discovery_manifest or {}).get("models", []):
        if not isinstance(model, dict):
            continue
        organization = str(model.get("organization") or "")
        if organization not in VERIFIED_HF_ORGANIZATIONS:
            raise ValueError(
                f"manifest model {model.get('modelId')} uses unverified org {organization!r}"
            )
        _validate_hf_entry(model, f"manifest model {model.get('modelId')}")

    if vendor_manifest is not None:
        validate_vendor_manifest(vendor_manifest)

    _validate_discovered_source_links(
        sources,
        discovery_manifest or {},
        vendor_manifest,
    )


def _strict_https_url(url: str, context: str):
    try:
        parsed = urlparse(url)
        port = parsed.port
    except ValueError as exc:
        raise ValueError(f"{context} has an invalid URL: {url!r}") from exc
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or port is not None
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
    ):
        raise ValueError(f"{context} must use a strict HTTPS URL, got {url!r}")
    return parsed


def _validate_exact_url(url: str, expected: str, context: str) -> None:
    _strict_https_url(url, context)
    if url != expected:
        raise ValueError(f"{context} must use {expected!r}, got {url!r}")


def _validate_hf_url(url: str, organization: str) -> None:
    parsed = _strict_https_url(url, "Hugging Face source")
    expected_prefix = f"/{organization}/"
    if parsed.hostname.lower() != "huggingface.co" or not parsed.path.startswith(expected_prefix):
        raise ValueError(
            f"expected official Hugging Face URL under {organization!r}, got {url!r}"
        )


def _validate_hf_model_url(
    url: str,
    organization: str,
    model_name: str,
    *,
    kind: str,
    revision: str = "",
) -> None:
    _validate_hf_url(url, organization)
    base = f"https://huggingface.co/{organization}/{model_name}"
    if kind == "page":
        valid = url == base
    elif kind == "readme":
        revision_pattern = re.escape(revision) if revision else r"[A-Za-z0-9._-]+"
        valid = re.fullmatch(
            rf"{re.escape(base)}/raw/{revision_pattern}/README\.md",
            url,
        ) is not None
    else:
        raise ValueError(f"unsupported Hugging Face URL kind: {kind!r}")
    if not valid:
        raise ValueError(
            f"expected official Hugging Face {kind} URL for "
            f"{organization}/{model_name}, got {url!r}"
        )


def _validate_hf_entry(entry: dict[str, Any], context: str) -> None:
    organization = str(entry.get("organization") or "")
    model_id = str(entry.get("modelId") or "")
    expected_prefix = f"{organization}/"
    if not organization or not model_id.startswith(expected_prefix):
        raise ValueError(
            f"{context} model id {model_id!r} is outside organization {organization!r}"
        )
    model_name = model_id[len(expected_prefix) :]
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", model_name):
        raise ValueError(f"{context} has invalid model id {model_id!r}")
    revision = str(entry.get("revision") or "")
    if revision and not re.fullmatch(r"[A-Za-z0-9._-]+", revision):
        raise ValueError(f"{context} has invalid revision {revision!r}")
    _validate_hf_model_url(
        str(entry.get("url") or ""),
        organization,
        model_name,
        kind="page",
    )
    _validate_hf_model_url(
        str(entry.get("rawUrl") or ""),
        organization,
        model_name,
        kind="readme",
        revision=revision or "main",
    )


def _canonical_aliases(name: str, display_name: str) -> list[str]:
    spaced = re.sub(r"[-_]+", " ", name).strip()
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    aliases: list[str] = []
    for alias in (display_name, name, spaced, slug):
        if alias and alias not in aliases:
            aliases.append(alias)
    return aliases


def _validate_vendor_page(page: dict[str, Any]) -> None:
    source_key = str(page.get("sourceKey") or "")
    policy = VENDOR_MANIFEST_SOURCES.get(source_key)
    if policy is None:
        raise ValueError(f"vendor manifest page uses unknown source key {source_key!r}")
    expected_vendor = policy[0]
    if page.get("vendor") != expected_vendor:
        raise ValueError(
            f"vendor manifest page {page.get('url')!r} has mismatched vendor"
        )

    name = str(page.get("name") or "")
    display_name = str(page.get("displayName") or "")
    expected_display = re.sub(r"[-_]+", " ", name).strip()
    if not name or display_name != expected_display:
        raise ValueError(f"vendor manifest page has invalid name/displayName: {page!r}")
    if page.get("aliases") != _canonical_aliases(name, display_name):
        raise ValueError(f"vendor manifest page {name!r} has non-canonical aliases")

    url = str(page.get("url") or "")
    raw_url = str(page.get("rawUrl") or "")
    parsed = _strict_https_url(url, f"vendor manifest page {name}")
    raw = _strict_https_url(raw_url, f"vendor manifest raw page {name}")

    if expected_vendor == "qwen":
        query = parse_qs(parsed.query, keep_blank_values=True)
        raw_query = parse_qs(raw.query, keep_blank_values=True)
        page_id = query.get("id", [""])
        valid = (
            parsed.hostname == "qwen.ai"
            and parsed.path == "/blog"
            and set(query) == {"id"}
            and len(page_id) == 1
            and re.fullmatch(r"qwen\d+(?:[.-][a-z0-9]+)*", page_id[0], re.IGNORECASE)
            and raw.hostname == "qwen.ai"
            and raw.path == "/api/v2/article/retrieval"
            and set(raw_query) == {"language", "path", "type"}
            and raw_query.get("language") == ["en-US"]
            and raw_query.get("type") == ["qwen_ai"]
            and raw_query.get("path") == page_id
            and isinstance(page.get("sourceMetadata"), dict)
            and str(page["sourceMetadata"].get("path") or "") == page_id[0]
            and re.fullmatch(r"Qwen\d+(?:[.-][A-Za-z0-9]+)*", name) is not None
        )
    elif expected_vendor == "glm":
        valid = (
            parsed.hostname == "docs.z.ai"
            and not parsed.query
            and re.fullmatch(r"/guides/llm/glm-[a-z0-9.-]+", parsed.path, re.IGNORECASE)
            and raw.hostname == "docs.z.ai"
            and not raw.query
            and raw.path == f"{parsed.path}.md"
            and name.casefold() == parsed.path.rsplit("/", 1)[-1].casefold()
        )
    elif expected_vendor == "kimi":
        valid = (
            parsed.hostname == "www.kimi.com"
            and not parsed.query
            and re.fullmatch(
                r"/(?:blog|resources)/kimi-k\d+(?:[.-][a-z0-9]+)*",
                parsed.path,
                re.IGNORECASE,
            )
            and raw_url == url
            and re.fullmatch(r"Kimi K\d+(?:\.\d+)?(?: [A-Za-z0-9]+)*", name)
        )
    else:
        valid = (
            parsed.hostname == "api-docs.deepseek.com"
            and not parsed.query
            and re.fullmatch(
                r"(?:/news/news\d{4,8}|/updates(?:/[a-z0-9._-]+)?)",
                parsed.path,
                re.IGNORECASE,
            )
            and raw_url == url
            and re.fullmatch(
                r"DeepSeek-(?:V|R)\d+(?:\.\d+)*(?:-[A-Za-z0-9.]+)*",
                name,
                re.IGNORECASE,
            )
        )
    if not valid:
        raise ValueError(f"vendor manifest page {name!r} violates official URL policy")


def validate_vendor_manifest(manifest: dict[str, Any]) -> None:
    source_rows = manifest.get("sources")
    page_rows = manifest.get("pages")
    if not isinstance(source_rows, list) or not isinstance(page_rows, list):
        raise ValueError("official vendor manifest must contain sources and pages lists")

    sources: dict[str, dict[str, Any]] = {}
    for source in source_rows:
        if not isinstance(source, dict):
            raise ValueError("official vendor manifest source must be an object")
        key = str(source.get("key") or "")
        if not key or key in sources:
            raise ValueError(f"duplicate or empty vendor manifest source key {key!r}")
        sources[key] = source
    if set(sources) != set(VENDOR_MANIFEST_SOURCES):
        raise ValueError("official vendor manifest source registry does not match policy")
    for key, (vendor, kind, url) in VENDOR_MANIFEST_SOURCES.items():
        actual = sources[key]
        if (
            actual.get("vendor") != vendor
            or actual.get("kind") != kind
            or actual.get("url") != url
        ):
            raise ValueError(f"official vendor manifest source {key!r} violates policy")
        _strict_https_url(str(actual.get("url") or ""), f"vendor manifest source {key}")

    seen_urls: set[str] = set()
    for page in page_rows:
        if not isinstance(page, dict):
            raise ValueError("official vendor manifest page must be an object")
        url = str(page.get("url") or "")
        if not url or url in seen_urls:
            raise ValueError(f"duplicate or empty vendor manifest page URL {url!r}")
        seen_urls.add(url)
        _validate_vendor_page(page)


def _validate_discovered_source_links(
    sources: dict[str, dict[str, Any]],
    model_manifest: dict[str, Any],
    vendor_manifest: dict[str, Any] | None,
) -> None:
    models_by_id = {
        str(model.get("modelId") or ""): model
        for model in model_manifest.get("models", [])
        if isinstance(model, dict) and model.get("modelId")
    }
    for source in sources.values():
        if not source.get("autoDiscovered"):
            continue
        model_id = str(source.get("modelId") or "")
        model = models_by_id.get(model_id)
        if model is None:
            raise ValueError(
                f"auto-discovered source {source.get('id')} is absent from model manifest"
            )
        for key in ("organization", "url", "rawUrl", "revision"):
            if str(source.get(key) or "") != str(model.get(key) or ""):
                raise ValueError(
                    f"auto-discovered source {source.get('id')} disagrees with "
                    f"model manifest field {key}"
                )

    vendor_sources = [
        source
        for source in sources.values()
        if source.get("autoDiscoveredVendorPage")
    ]
    if not vendor_sources:
        return
    if vendor_manifest is None:
        raise ValueError("vendor-discovered benchmark sources require a vendor manifest")
    pages_by_url = {
        str(page.get("url") or ""): page
        for page in vendor_manifest.get("pages", [])
        if isinstance(page, dict) and page.get("url")
    }
    for source in vendor_sources:
        url = str(source.get("url") or "")
        page = pages_by_url.get(url)
        if page is None:
            raise ValueError(
                f"vendor-discovered source {source.get('id')} is absent from vendor manifest"
            )
        comparisons = {
            "vendor": page.get("vendor"),
            "rawUrl": page.get("rawUrl"),
            "discoverySourceKey": page.get("sourceKey"),
            "modelAliases": page.get("aliases"),
        }
        for key, expected in comparisons.items():
            if source.get(key) != expected:
                raise ValueError(
                    f"vendor-discovered source {source.get('id')} disagrees with "
                    f"vendor manifest field {key}"
                )


def _read_json(path: Path, *, optional: bool = False) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        if optional:
            return {}
        raise
    if not isinstance(payload, dict):
        raise ValueError(f"{path} does not contain a JSON object")
    return payload


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmarks-json", default=str(DEFAULT_BENCHMARKS_JSON))
    parser.add_argument("--manifest-json", default=str(DEFAULT_MANIFEST_JSON))
    parser.add_argument(
        "--vendor-manifest-json",
        default=str(DEFAULT_VENDOR_MANIFEST_JSON),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        payload = _read_json(Path(args.benchmarks_json))
        manifest = _read_json(Path(args.manifest_json))
        vendor_manifest = _read_json(Path(args.vendor_manifest_json))
        validate_payload(payload, manifest, vendor_manifest)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(
        f"Validated {len(PRIMARY_VENDOR_PAGE_SOURCE_IDS)} vendor pages, "
        f"{len(OFFICIAL_HF_SOURCE_ORGS)} explicit official cards, and "
        f"{len(manifest.get('models', []))} discovered cards plus "
        f"{len(vendor_manifest.get('pages', []))} discovered vendor pages."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
