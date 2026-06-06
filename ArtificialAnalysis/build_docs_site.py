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

ARTICLE_URL = "https://zhuanlan.zhihu.com/p/2032797597627311070?share_code=YgrFlZy1McBQ&utm_psn=2043622787617641823"
SOURCE_URL = "https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index"

AA_PRESET_COLUMNS = {
    "aa-intelligence": "AA Intelligence Index",
    "aa-coding": "AA Coding Index",
    "aa-agentic": "AA Agentic Index",
}

AA_SUITE_WEIGHT_BY_METRIC = {
    "GDPval-AA": 12.5,
    "τ²-Bench Telecom": 12.5,
    "Terminal-Bench Hard": 12.5,
    "SciCode": 12.5,
    "AA-LCR": 25 / 3,
    "AA-Omniscience Accuracy": 25 / 3,
    "IFBench": 25 / 3,
    "Humanity's Last Exam": 25 / 3,
    "GPQA Diamond": 25 / 3,
    "CritPt": 25 / 3,
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
ICON_TONES = ("tone-1", "tone-2", "tone-3", "tone-4", "tone-5", "tone-6")

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
                "weights: four 25% categories split across their member evaluations. The AA-Omniscience "
                "correction uses Accuracy only, assigning zero weight to the non-hallucination component."
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
        "aaCostUsd": _number_or_none(row.get("AA Intelligence Index Cost (USD)")),
        "scores": scores,
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
    return {
        "label": label,
        "title": title,
        "tone": _icon_tone(title),
    }


def _initials(value: str) -> str:
    tokens = re.findall(r"[A-Za-z0-9]+", value)
    if not tokens:
        return "AI"
    if len(tokens) == 1:
        return tokens[0][:3].upper()
    return "".join(token[0].upper() for token in tokens[:3])


def _icon_tone(value: str) -> str:
    return ICON_TONES[sum(ord(char) for char in value) % len(ICON_TONES)]


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
            "description": "按 AA Intelligence Index evaluation suite 的四类 25% 权重计算；AA-Omniscience 按修正规则只计 Accuracy，非幻觉率权重为 0。",
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
            "description": "按用户设置的评测权重实时计算，缺失项按 0 计入分母。",
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
