"""Build the static ranking data used by the docs site."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ArtificialAnalysis.scrape_artificial_analysis import RAW_SCORES_FILENAME, SCORE_SPECS


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_CSV = PROJECT_ROOT / "ArtificialAnalysis" / RAW_SCORES_FILENAME
DEFAULT_OUTPUT_JSON = PROJECT_ROOT / "docs" / "data" / "models.json"
DEFAULT_OUTPUT_JS = PROJECT_ROOT / "docs" / "data" / "models.js"
LOCAL_LOGO_DIR = "assets/logos"

ARTICLE_URL = "https://zhuanlan.zhihu.com/p/2032797597627311070?share_code=YgrFlZy1McBQ&utm_psn=2043622787617641823"
SOURCE_URL = "https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index"

AA_PRESET_COLUMNS = {
    "aa-intelligence": "AA Intelligence Index",
    "aa-coding": "AA Coding Index",
    "aa-agentic": "AA Agentic Index",
}

AA_SUITE_WEIGHT_BY_METRIC = {
    "GDPval-AA": 100 / 6,
    "τ²-Bench Telecom": 25 / 3,
    "Terminal-Bench Hard": 100 / 6,
    "SciCode": 25 / 3,
    "AA-LCR": 6.25,
    "AA-Omniscience Accuracy": 12.5,
    "IFBench": 6.25,
    "Humanity's Last Exam": 12.5,
    "GPQA Diamond": 6.25,
    "CritPt": 6.25,
}
DEFAULT_CORRECTED_WEIGHTS = {
    spec.column: AA_SUITE_WEIGHT_BY_METRIC.get(spec.column, 0)
    for spec in SCORE_SPECS
}
VARIANT_PRIORITY_BY_SUFFIX = {
    "max": 100,
    "xhigh": 90,
    "extra-high": 90,
    "high": 80,
    "default": 70,
    "thinking": 70,
    "reasoning": 70,
    "medium": 60,
    "fast": 50,
    "low": 40,
    "minimal": 30,
    "min": 30,
    "non-reasoning": 20,
}
PROVIDER_ICON_LABELS = {
    "AI21 Labs": "AI21",
    "Alibaba": "QW",
    "Anthropic": "ANT",
    "ByteDance Seed": "SEED",
    "Cohere": "CO",
    "DeepSeek": "DS",
    "Google": "G",
    "Meta": "META",
    "Mistral": "M",
    "Moonshot AI": "KIMI",
    "OpenAI": "OAI",
    "Perplexity": "PPLX",
    "xAI": "xAI",
    "Z AI": "ZAI",
}
PROVIDER_LOGO_SLUGS = {
    "AI21 Labs": "ai21",
    "Alibaba": "alibaba",
    "Anthropic": "anthropic",
    "Baidu": "baidu",
    "ByteDance Seed": "bytedance-seed",
    "Cohere": "cohere",
    "DeepSeek": "deepseek",
    "Google": "google",
    "IBM": "ibm",
    "Meta": "meta",
    "Microsoft": "microsoft",
    "Mistral": "mistral",
    "Moonshot AI": "moonshot",
    "NVIDIA": "nvidia",
    "OpenAI": "openai",
    "Perplexity": "perplexity",
    "StepFun": "stepfun",
    "xAI": "xai",
    "Z AI": "z-ai",
}
EXTERNAL_SOURCES = [
    {
        "id": "artificial-analysis",
        "label": "Artificial Analysis",
        "icon": "AA",
        "url": SOURCE_URL,
        "category": "Composite benchmark",
        "coverage": "520+ model rows",
        "focus": "Composite intelligence, coding, agentic scores, token usage, cost, release date.",
        "note": "Primary source for AInsights Index scoring and operational metrics.",
        "scoreStatus": "active",
        "defaultWeight": 100,
        "relatedMetrics": [spec.column for spec in SCORE_SPECS],
    },
    {
        "id": "arena",
        "label": "Arena / LMArena",
        "icon": "AR",
        "url": "https://arena.ai/leaderboard/",
        "category": "Human preference",
        "coverage": "Text, code, vision, document, search, image and video arenas",
        "focus": "Blind side-by-side human preference rankings across real user prompts.",
        "note": "Useful as a general-experience cross-check, but not directly comparable to fixed benchmark scores.",
        "scoreStatus": "mapped",
        "defaultWeight": 0,
        "relatedMetrics": ["IFBench", "CritPt"],
    },
    {
        "id": "livebench",
        "label": "LiveBench",
        "icon": "LB",
        "url": "https://livebench.ai/",
        "category": "Contamination-resistant benchmark",
        "coverage": "Global, reasoning, coding, math, data analysis, language, IF",
        "focus": "Fresh benchmark releases intended to reduce training-data leakage.",
        "note": "Useful for checking whether static benchmark wins still hold on newer tasks.",
        "scoreStatus": "mapped",
        "defaultWeight": 0,
        "relatedMetrics": ["LiveCodeBench", "AIME 2025", "GPQA Diamond", "IFBench"],
    },
    {
        "id": "swe-bench",
        "label": "SWE-bench",
        "icon": "SWE",
        "url": "https://www.swebench.com/",
        "category": "Software engineering",
        "coverage": "Full, Verified, Lite, Multilingual, Multimodal",
        "focus": "Real GitHub issue resolution, commonly reported as percent resolved.",
        "note": "Best treated as an agent/tooling benchmark rather than a pure base-model leaderboard.",
        "scoreStatus": "mapped",
        "defaultWeight": 0,
        "relatedMetrics": ["Terminal-Bench Hard", "SciCode", "LiveCodeBench", "APEX-Agents-AA", "ITBench-AA"],
    },
    {
        "id": "helm",
        "label": "Stanford HELM",
        "icon": "HELM",
        "url": "https://crfm.stanford.edu/helm/index.html",
        "category": "Holistic evaluation",
        "coverage": "Capabilities, safety, transparency, domain leaderboards",
        "focus": "Transparent, scenario-based evaluation with reproducibility emphasis.",
        "note": "Useful as a methodology benchmark and source for caveats beyond headline rank.",
        "scoreStatus": "mapped",
        "defaultWeight": 0,
        "relatedMetrics": ["Humanity's Last Exam", "GPQA Diamond", "MMMU-Pro", "IFBench", "CritPt"],
    },
    {
        "id": "huggingface-leaderboards",
        "label": "Hugging Face Leaderboards",
        "icon": "HF",
        "url": "https://huggingface.co/docs/leaderboards/index",
        "category": "Community and reproducible evals",
        "coverage": "Eval Results, community Spaces, Open LLM Leaderboard archive",
        "focus": "Hub-hosted model eval results and community-maintained leaderboards.",
        "note": "Useful for open-model reproducibility checks and benchmark result discovery.",
        "scoreStatus": "mapped",
        "defaultWeight": 0,
        "relatedMetrics": ["MMMU-Pro", "AIME 2025", "GPQA Diamond", "LiveCodeBench"],
    },
]

STRENGTH_SUFFIX_RE = re.compile(
    r"\s*\((?:x?high|medium|low|max|min|minimal|default|fast|thinking|non[- ]reasoning|reasoning)\)\s*$",
    re.IGNORECASE,
)
SLUG_SUFFIX_RE = re.compile(
    r"-(?:x?high|medium|low|max|min|minimal|default|fast|thinking|non-reasoning|reasoning)$",
    re.IGNORECASE,
)
MODEL_SUFFIX_RE = re.compile(r"\(([^()]*)\)\s*$")
NON_WORD_RE = re.compile(r"[^a-z0-9]+")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def build_site_payload(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    source_rows = list(rows)
    metric_keys = [spec.column for spec in SCORE_SPECS]
    models = [_model_payload(row, metric_keys) for row in source_rows]

    return {
        "version": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": {
            "label": "Artificial Analysis Intelligence Evaluations",
            "url": SOURCE_URL,
            "defaultCorrectionReference": ARTICLE_URL,
            "defaultCorrectionNote": (
                "AInsights Index follows the Artificial Analysis Intelligence Index evaluation suite "
                "weights. The AA-Omniscience correction assigns the full 12.5% component weight to "
                "Accuracy and zero weight to the non-hallucination component."
            ),
        },
        "defaultPreset": "zhihu-adjusted",
        "defaultDedupe": True,
        "metrics": [
            {
                "key": key,
                "label": key,
                "defaultWeight": DEFAULT_CORRECTED_WEIGHTS.get(key, 0),
            }
            for key in metric_keys
        ],
        "presets": _presets(),
        "externalSources": EXTERNAL_SOURCES,
        "models": models,
        "summary": {
            "modelRows": len(models),
            "variantGroups": len({model["variantGroup"] for model in models}),
            "sourceTypes": _source_type_counts(models),
        },
    }


def variant_group(model: str, slug: str = "") -> str:
    base = STRENGTH_SUFFIX_RE.sub("", model or "").strip()
    if not base and slug:
        base = SLUG_SUFFIX_RE.sub("", slug).replace("-", " ")
    normalized = NON_WORD_RE.sub(" ", base.lower()).strip()
    return normalized or (slug or model or "").lower()


def variant_priority(model: str, slug: str = "") -> int:
    suffix = _variant_suffix(model, slug)
    if suffix is None:
        return VARIANT_PRIORITY_BY_SUFFIX["default"]
    return VARIANT_PRIORITY_BY_SUFFIX.get(suffix, VARIANT_PRIORITY_BY_SUFFIX["default"])


def score_model_for_preset(
    model: dict[str, Any],
    preset: dict[str, Any],
    metrics: list[dict[str, Any]],
) -> dict[str, float | int | None]:
    if preset["kind"] == "aa-column":
        score = _number_or_none(model.get("aa", {}).get(preset["column"]))
        return {
            "score": score,
            "coverage": 1 if score is not None else 0,
            "availableWeight": 1 if score is not None else 0,
        }

    return weighted_metric_score(
        model,
        preset.get("weights", {}),
        bool(preset.get("ignoreMissing")),
        int(preset.get("minCoverage") or 0),
    )


def weighted_metric_score(
    model: dict[str, Any],
    weights: dict[str, Any],
    ignore_missing: bool,
    min_coverage: int = 0,
) -> dict[str, float | int | None]:
    weighted_score = 0.0
    denominator = 0.0
    available_weight = 0.0
    coverage = 0

    for key, raw_weight in weights.items():
        weight = _number_or_none(raw_weight) or 0.0
        if weight <= 0:
            continue
        value = _number_or_none(model.get("scores", {}).get(key))
        if value is None:
            if not ignore_missing:
                denominator += weight
            continue
        weighted_score += value * weight
        denominator += weight
        available_weight += weight
        coverage += 1

    return {
        "score": weighted_score / denominator if denominator > 0 and coverage >= min_coverage else None,
        "coverage": coverage,
        "availableWeight": available_weight,
    }


def write_site_payload(input_csv: Path, output_json: Path, output_js: Path | None = None) -> dict[str, Any]:
    payload = build_site_payload(read_csv_rows(input_csv))
    output_json.parent.mkdir(parents=True, exist_ok=True)
    payload_text = json.dumps(payload, ensure_ascii=False, indent=2)
    output_json.write_text(payload_text, encoding="utf-8")
    if output_js is not None:
        output_js.parent.mkdir(parents=True, exist_ok=True)
        output_js.write_text(
            "window.AINSIGHTS_MODELS_DATA = " + payload_text + ";\n",
            encoding="utf-8",
        )
    return payload


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build docs/data/models.json for the static ranking site.")
    parser.add_argument("--input-csv", default=str(DEFAULT_INPUT_CSV), help="Raw scores CSV to read.")
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON), help="JSON payload to write.")
    parser.add_argument(
        "--output-js",
        help="JS payload to write for file:// loading. Defaults to output-json with a .js suffix.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    output_json = Path(args.output_json)
    output_js = Path(args.output_js) if args.output_js else output_json.with_suffix(".js")
    payload = write_site_payload(Path(args.input_csv), output_json, output_js)
    print(
        f"Wrote {output_json} with {payload['summary']['modelRows']} rows "
        f"across {payload['summary']['variantGroups']} dedupe groups."
    )
    return 0


def _model_payload(row: dict[str, Any], metric_keys: list[str]) -> dict[str, Any]:
    model = str(row.get("model") or "")
    slug = str(row.get("slug") or "")
    creator = str(row.get("creator") or "")
    open_source_categorization = str(row.get("open_source_categorization") or "")
    scores = {key: _number_or_none(row.get(key)) for key in metric_keys}
    aa_scores = {key: _number_or_none(row.get(column)) for key, column in AA_PRESET_COLUMNS.items()}
    pricing = pricing_payload(row)

    return {
        "modelKey": row.get("model_key") or model,
        "model": model,
        "variantGroup": variant_group(model, slug),
        "variantPriority": variant_priority(model, slug),
        "isReasoning": str(row.get("is_reasoning") or "").lower() == "true",
        "slug": slug,
        "creator": creator,
        "releaseDate": row.get("release_date") or "",
        "modelUrl": row.get("model_url") or "",
        "contextWindowTokens": _number_or_none(row.get("context_window_tokens")),
        "openSourceCategorization": open_source_categorization,
        "openSourceType": open_source_type(open_source_categorization),
        "modelIcon": model_icon(creator, model),
        "medianOutputSpeed": _number_or_none(row.get("median_output_speed")),
        "aa": aa_scores,
        "aaCostUsd": pricing["aaIndexCostUsd"],
        "pricing": pricing,
        "scores": scores,
    }


def pricing_payload(row: dict[str, Any]) -> dict[str, float | None]:
    return {
        "inputPerMillionTokensUsd": _number_or_none(row.get("Input Price Per 1M Tokens (USD)")),
        "outputPerMillionTokensUsd": _number_or_none(row.get("Output Price Per 1M Tokens (USD)")),
        "cacheHitPerMillionTokensUsd": _number_or_none(row.get("Cache Hit Price Per 1M Tokens (USD)")),
        "aaIndexCostUsd": _number_or_none(row.get("AA Intelligence Index Cost (USD)")),
        "aaIndexInputCostUsd": _number_or_none(row.get("AA Intelligence Index Input Cost (USD)")),
        "aaIndexOutputCostUsd": _number_or_none(row.get("AA Intelligence Index Output Cost (USD)")),
        "aaIndexReasoningCostUsd": _number_or_none(row.get("AA Intelligence Index Reasoning Cost (USD)")),
        "aaIndexAnswerCostUsd": _number_or_none(row.get("AA Intelligence Index Answer Cost (USD)")),
    }


def open_source_type(category: str) -> str:
    normalized = category.strip().lower()
    if not normalized:
        return "unknown"
    if "open" in normalized:
        return "open"
    if "proprietary" in normalized or "closed" in normalized:
        return "closed"
    return "unknown"


def model_icon(creator: str, model: str = "") -> dict[str, str]:
    title = creator.strip() or model.strip() or "Unknown"
    label = PROVIDER_ICON_LABELS.get(title) or _initials(title)
    slug = provider_logo_slug(title)
    return {
        "label": label,
        "fallbackLabel": label,
        "title": title,
        "src": f"{LOCAL_LOGO_DIR}/{slug}_small.svg",
    }


def provider_logo_slug(creator: str) -> str:
    return PROVIDER_LOGO_SLUGS.get(creator.strip()) or re.sub(
        r"-+",
        "-",
        re.sub(r"[^a-z0-9]+", "-", creator.strip().lower()),
    ).strip("-") or "unknown"


def _initials(value: str) -> str:
    tokens = re.findall(r"[A-Za-z0-9]+", value)
    if not tokens:
        return "AI"
    if len(tokens) == 1:
        return tokens[0][:3].upper()
    return "".join(token[0].upper() for token in tokens[:3])


def _source_type_counts(models: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"open": 0, "closed": 0, "unknown": 0}
    for model in models:
        source_type = str(model.get("openSourceType") or "unknown")
        counts[source_type if source_type in counts else "unknown"] += 1
    return counts


def _presets() -> dict[str, dict[str, Any]]:
    return {
        "zhihu-adjusted": {
            "label": "AInsights Index",
            "kind": "weighted-metrics",
            "description": "按 AA Intelligence Index evaluation suite 原始占比计算；AA-Omniscience 修正为 12.5% 全部计入 Accuracy，非幻觉率权重为 0。",
            "ignoreMissing": False,
            "weights": DEFAULT_CORRECTED_WEIGHTS,
        },
        "aa-intelligence": {
            "label": "AA Intelligence",
            "kind": "aa-column",
            "column": "aa-intelligence",
            "description": "Artificial Analysis 官方 Intelligence Index。",
        },
        "aa-coding": {
            "label": "AA Coding",
            "kind": "aa-column",
            "column": "aa-coding",
            "description": "Artificial Analysis 官方 Coding Index。",
        },
        "aa-agentic": {
            "label": "AA Agentic",
            "kind": "aa-column",
            "column": "aa-agentic",
            "description": "Artificial Analysis 官方 Agentic Index。",
        },
        "custom": {
            "label": "自定义占比",
            "kind": "weighted-metrics",
            "description": "默认使用 AInsights Index 配置；可按用户设置的评测权重实时计算，缺失项按 0 计入分母。",
            "ignoreMissing": False,
            "weights": DEFAULT_CORRECTED_WEIGHTS,
        },
    }


def _number_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _variant_suffix(model: str, slug: str) -> str | None:
    match = MODEL_SUFFIX_RE.search(model or "")
    if match:
        return _normalize_variant_suffix(match.group(1))

    normalized_slug = (slug or "").lower()
    for suffix in sorted(VARIANT_PRIORITY_BY_SUFFIX, key=len, reverse=True):
        slug_suffix = suffix.replace(" ", "-")
        if normalized_slug.endswith(f"-{slug_suffix}"):
            return suffix
    return None


def _normalize_variant_suffix(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if normalized in {"x-high", "extra-high", "extra-high-reasoning"}:
        return "xhigh"
    if normalized == "non-reasoning":
        return "non-reasoning"
    return normalized


if __name__ == "__main__":
    raise SystemExit(main())
