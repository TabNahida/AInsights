"""Build the static ranking data used by the docs site."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ArtificialAnalysis.scrape_artificial_analysis import RAW_SCORES_FILENAME, SCORE_SPECS


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_CSV = PROJECT_ROOT / "ArtificialAnalysis" / RAW_SCORES_FILENAME
DEFAULT_OUTPUT_JSON = PROJECT_ROOT / "docs" / "data" / "models.json"
DEFAULT_OUTPUT_JS = PROJECT_ROOT / "docs" / "data" / "models.js"
DEFAULT_EXTERNAL_BENCHMARKS_JSON = PROJECT_ROOT / "data" / "benchmarks" / "benchmark_scores.json"
LOCAL_LOGO_DIR = "assets/logos"

ARTICLE_URL = "https://zhuanlan.zhihu.com/p/2032797597627311070?share_code=YgrFlZy1McBQ&utm_psn=2043622787617641823"
SOURCE_URL = "https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index"

AA_PRESET_COLUMNS = {
    "aa-intelligence": "AA Intelligence Index",
    "aa-coding": "AA Coding Index",
    "aa-agentic": "AA Agentic Index",
}

AA_SUITE_WEIGHT_BY_METRIC = {
    "GDPval-AA v2": 20,
    "τ³-Banking": 14,
    "Terminal-Bench v2.1": 16,
    "SciCode": 8,
    "AA-LCR": 6,
    "AA-Omniscience Accuracy": 12,
    "Humanity's Last Exam": 12,
    "GPQA Diamond": 6,
    "CritPt": 6,
}
AA_INTELLIGENCE_SUITE_WEIGHTS = {
    "GDPval-AA v2": 20,
    "τ³-Banking": 14,
    "Terminal-Bench v2.1": 16,
    "SciCode": 8,
    "AA-LCR": 6,
    "AA-Omniscience Accuracy": 8,
    "AA-Omniscience Non-Hallucination Rate": 4,
    "Humanity's Last Exam": 12,
    "GPQA Diamond": 6,
    "CritPt": 6,
}
AA_CODING_SUITE_WEIGHTS = {
    "Terminal-Bench v2.1": 200 / 3,
    "SciCode": 100 / 3,
}
AA_AGENTIC_SUITE_WEIGHTS = {
    "GDPval-AA v2": 1000 / 17,
    "τ³-Banking": 700 / 17,
}
FRONTIER_INDEX_GROUPS = [
    {
        "id": "aa-suite",
        "label": "AA suite",
        "weight": 60,
        "metrics": [
            "GDPval-AA v2",
            "τ³-Banking",
            "Terminal-Bench v2.1",
            "SciCode",
            "AA-LCR",
            "AA-Omniscience Accuracy",
            "Humanity's Last Exam",
            "GPQA Diamond",
            "CritPt",
        ],
    },
    {
        "id": "agentic-coding",
        "label": "Agentic coding",
        "weight": 40 / 3,
        "metrics": [
            "Terminal-Bench v2.1",
            "SciCode",
            "benchmark:swe-bench-pro",
            "benchmark:swe-bench-verified",
            "benchmark:swe-bench-multilingual",
            "benchmark:terminal-bench-2",
            "benchmark:terminal-bench-2-1",
            "benchmark:livecodebench",
            "benchmark:frontiercode-diamond",
        ],
    },
    {
        "id": "tools-work",
        "label": "Tools/work",
        "weight": 10,
        "metrics": [
            "benchmark:browsecomp",
            "benchmark:hle-tools",
            "benchmark:mcp-atlas",
            "benchmark:toolathlon",
            "benchmark:osworld-verified",
            "benchmark:gdpval-wins-ties",
            "benchmark:gdpval-aa-elo",
            "GDPval-AA v2",
            "τ³-Banking",
        ],
    },
    {
        "id": "reasoning",
        "label": "Reasoning",
        "weight": 40 / 3,
        "metrics": [
            "benchmark:hle",
            "Humanity's Last Exam",
            "benchmark:gpqa-diamond",
            "GPQA Diamond",
            "benchmark:mmlu-pro",
            "benchmark:aime-2025",
            "benchmark:aime-2026",
            "benchmark:frontiermath-tier-1-3",
            "benchmark:frontiermath-tier-4",
            "benchmark:hmmt-2026-feb",
            "AA-Omniscience Accuracy",
        ],
    },
    {
        "id": "instruction-long-context",
        "label": "Instruction/long-context",
        "weight": 10 / 3,
        "metrics": [
            "AA-LCR",
            "CritPt",
            "benchmark:ifbench",
            "benchmark:mmmlu",
            "benchmark:mmmu-pro",
            "benchmark:charxiv-no-tools",
            "benchmark:charxiv-tools",
        ],
    },
]
FRONTIER_GROUP_WEIGHTS = {
    group["id"]: group["weight"]
    for group in FRONTIER_INDEX_GROUPS
}
DEFAULT_FRONTIER_WEIGHTS: dict[str, float] = {}
for group in FRONTIER_INDEX_GROUPS:
    group_weight = float(group["weight"])
    metrics = list(group["metrics"])
    per_metric_weight = group_weight / len(metrics)
    for metric in metrics:
        DEFAULT_FRONTIER_WEIGHTS[metric] = DEFAULT_FRONTIER_WEIGHTS.get(metric, 0.0) + per_metric_weight

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
    "Kimi": "KIMI",
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
    "Kimi": "kimi",
    "NVIDIA": "nvidia",
    "OpenAI": "openai",
    "Perplexity": "perplexity",
    "StepFun": "stepfun",
    "xAI": "xai",
    "Z AI": "zai",
}
MODEL_DETAIL_OVERRIDES = {
    "minimax-m3": {
        "inputModalities": ["Text", "Image", "Video"],
        "outputModalities": ["Text"],
        "modelDetails": {
            "parameters": "427B",
            "activeParameters": "23B",
            "reasoningModes": ["thinking", "non-thinking"],
            "architecture": "MiniMax Sparse Attention (MSA), MoE",
            "apiAccess": ["MiniMax API", "OpenAI-compatible", "Anthropic-compatible", "open weights"],
            "license": "minimax-community",
            "contextNote": "1M context window; MiniMax API documents a guaranteed minimum of 512K.",
        },
    },
}
MODALITY_SPECS = [
    ("text", "Text", "text"),
    ("image", "Image", "image"),
    ("speech", "Audio", "audio"),
    ("video", "Video", "video"),
]
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


def load_external_benchmarks(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "sources": [], "benchmarks": [], "results": []}
    return json.loads(path.read_text(encoding="utf-8"))


def external_metric_key(benchmark_id: str) -> str:
    return f"benchmark:{benchmark_id}"


def build_site_payload(
    rows: Iterable[dict[str, Any]],
    external_benchmark_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_rows = list(rows)
    external_benchmark_data = external_benchmark_data or load_external_benchmarks(DEFAULT_EXTERNAL_BENCHMARKS_JSON)
    external_benchmarks = external_benchmark_data.get("benchmarks", [])
    metric_keys = [spec.column for spec in SCORE_SPECS] + [
        external_metric_key(benchmark["id"]) for benchmark in external_benchmarks
    ]
    models = [_model_payload(row, metric_keys) for row in source_rows]
    attach_external_benchmark_scores(models, external_benchmark_data)
    baselines = metric_baselines(models, metric_keys)
    aa_intelligence_max = aa_score_baseline(models, "aa-intelligence")

    return {
        "version": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": {
            "label": "Artificial Analysis Intelligence Evaluations",
            "url": SOURCE_URL,
            "defaultCorrectionReference": ARTICLE_URL,
            "defaultCorrectionNote": (
                "AInsights Index follows the Artificial Analysis Intelligence Index evaluation suite "
                "weights. The AA-Omniscience correction assigns the full 12% component weight to "
                "Accuracy and zero weight to the non-hallucination component."
            ),
        },
        "defaultPreset": "zhihu-adjusted",
        "defaultDedupe": True,
        "metrics": [
            {
                "key": key,
                "label": key,
                "defaultWeight": DEFAULT_FRONTIER_WEIGHTS.get(key, 0),
            }
            for key in [spec.column for spec in SCORE_SPECS]
        ]
        + [
            {
                "key": external_metric_key(benchmark["id"]),
                "label": benchmark.get("label") or benchmark["id"],
                "defaultWeight": DEFAULT_FRONTIER_WEIGHTS.get(external_metric_key(benchmark["id"]), 0),
                "source": "benchmark",
                "category": benchmark.get("category") or "Benchmark",
                "unit": benchmark.get("unit") or "%",
                "icon": benchmark.get("icon") or "",
            }
            for benchmark in external_benchmarks
        ],
        "presets": _presets(),
        "metricBaselines": baselines,
        "scoreBaselines": {
            "aaIntelligenceMax": aa_intelligence_max,
        },
        "externalSources": external_sources_payload(external_benchmark_data),
        "externalBenchmarks": external_benchmarks,
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
    metric_baselines: dict[str, Any] | None = None,
    display_scale: float | None = None,
) -> dict[str, float | int | None]:
    if preset["kind"] == "aa-column":
        score = _number_or_none(model.get("aa", {}).get(preset["column"]))
        return {
            "score": score,
            "coverage": 1 if score is not None else 0,
            "availableWeight": 1 if score is not None else 0,
        }

    if preset["kind"] == "frontier-groups":
        return frontier_group_score(
            model,
            preset.get("groups", []),
            method=str(preset.get("calculation") or "geometric"),
            normalization=str(preset.get("normalization") or "relative-best"),
            missing_policy=str(preset.get("missingPolicy") or "coverage-discount"),
            coverage_discount_exponent=float(preset.get("coverageDiscountExponent") or 0),
            group_metric_coverage_discount_exponent=float(
                preset.get("groupMetricCoverageDiscountExponent") or 0
            ),
            weak_prior_ratio=float(preset.get("weakPriorRatio") or 0.35),
            metric_baselines=metric_baselines,
            display_scale=display_scale,
        )

    return weighted_metric_score(
        model,
        preset.get("weights", {}),
        bool(preset.get("ignoreMissing")),
        int(preset.get("minCoverage") or 0),
        method=str(preset.get("calculation") or "arithmetic"),
        normalization=str(preset.get("normalization") or "raw"),
        metric_baselines=metric_baselines,
        display_scale=display_scale,
        missing_policy=preset.get("missingPolicy"),
        coverage_discount_exponent=float(preset.get("coverageDiscountExponent") or 0),
        weak_prior_ratio=float(preset.get("weakPriorRatio") or 0.35),
    )


def frontier_group_score(
    model: dict[str, Any],
    groups: Iterable[dict[str, Any]],
    method: str = "geometric",
    normalization: str = "relative-best",
    missing_policy: str = "coverage-discount",
    coverage_discount_exponent: float = 0.25,
    group_metric_coverage_discount_exponent: float = 0.0,
    weak_prior_ratio: float = 0.35,
    metric_baselines: dict[str, Any] | None = None,
    display_scale: float | None = None,
) -> dict[str, float | int | None]:
    entries: list[tuple[float, float]] = []
    denominator = 0.0
    available_weight = 0.0
    total_weight = 0.0
    coverage = 0

    for group in groups:
        weight = _number_or_none(group.get("weight")) or 0.0
        if weight <= 0:
            continue
        total_weight += weight
        group_value = frontier_group_value(
            model,
            group.get("metrics", []),
            method=method,
            normalization=normalization,
            coverage_discount_exponent=group_metric_coverage_discount_exponent,
            metric_baselines=metric_baselines,
        )
        if group_value is None:
            if missing_policy == "zero":
                entries.append((0.0, weight))
                denominator += weight
            elif missing_policy == "weak-prior":
                entries.append((weak_prior_ratio, weight))
                denominator += weight
            continue
        entries.append((group_value, weight))
        denominator += weight
        available_weight += weight
        coverage += 1

    if denominator <= 0:
        score = None
    else:
        score = aggregate_weighted_values(entries, denominator, method)
        if score is not None and normalization == "relative-best":
            score *= 100.0 if display_scale is None else display_scale
        if score is not None and missing_policy == "coverage-discount":
            coverage_ratio = available_weight / total_weight if total_weight > 0 else 0.0
            score *= coverage_ratio ** coverage_discount_exponent

    return {
        "score": score,
        "coverage": coverage,
        "availableWeight": available_weight,
    }


def frontier_group_value(
    model: dict[str, Any],
    metric_keys: Iterable[Any],
    method: str = "geometric",
    normalization: str = "relative-best",
    coverage_discount_exponent: float = 0.0,
    metric_baselines: dict[str, Any] | None = None,
) -> float | None:
    entries: list[tuple[float, float]] = []
    keys = [str(key_value) for key_value in metric_keys]
    for key in keys:
        value = _number_or_none(model.get("scores", {}).get(key))
        if value is None:
            continue
        entries.append((normalized_metric_value(key, value, normalization, metric_baselines), 1.0))
    if not entries:
        return None
    value = aggregate_weighted_values(entries, float(len(entries)), method)
    if value is not None and coverage_discount_exponent > 0 and keys:
        value *= (len(entries) / len(keys)) ** coverage_discount_exponent
    return value


def aggregate_weighted_values(
    entries: Iterable[tuple[float, float]],
    denominator: float,
    method: str = "arithmetic",
) -> float | None:
    values = list(entries)
    if denominator <= 0 or not values:
        return None
    if method == "geometric":
        return math.exp(
            sum(math.log(max(value, 0.0) + 1) * weight for value, weight in values) / denominator
        ) - 1
    return sum(value * weight for value, weight in values) / denominator


def weighted_metric_score(
    model: dict[str, Any],
    weights: dict[str, Any],
    ignore_missing: bool,
    min_coverage: int = 0,
    method: str = "arithmetic",
    normalization: str = "raw",
    metric_baselines: dict[str, Any] | None = None,
    display_scale: float | None = None,
    missing_policy: Any = None,
    coverage_discount_exponent: float = 0.0,
    weak_prior_ratio: float = 0.35,
) -> dict[str, float | int | None]:
    entries: list[tuple[float, float]] = []
    denominator = 0.0
    available_weight = 0.0
    total_weight = 0.0
    coverage = 0
    policy = str(missing_policy or "").strip()

    for key, raw_weight in weights.items():
        weight = _number_or_none(raw_weight) or 0.0
        if weight <= 0:
            continue
        total_weight += weight
        value = _number_or_none(model.get("scores", {}).get(key))
        if value is None:
            if policy == "weak-prior":
                entries.append((weak_prior_ratio, weight))
                denominator += weight
            elif policy == "zero" or (not policy and not ignore_missing):
                entries.append((0.0, weight))
                denominator += weight
            continue
        score_value = normalized_metric_value(key, value, normalization, metric_baselines)
        entries.append((score_value, weight))
        denominator += weight
        available_weight += weight
        coverage += 1
    if denominator <= 0 or coverage < min_coverage:
        score = None
    else:
        score = aggregate_weighted_values(entries, denominator, method)
    if score is not None and normalization == "relative-best":
        score *= 100.0 if display_scale is None else display_scale
    if score is not None and policy == "coverage-discount":
        coverage_ratio = available_weight / total_weight if total_weight > 0 else 0.0
        score *= coverage_ratio ** coverage_discount_exponent

    return {
        "score": score,
        "coverage": coverage,
        "availableWeight": available_weight,
    }


def metric_baselines(models: list[dict[str, Any]], metric_keys: Iterable[str]) -> dict[str, float]:
    baselines: dict[str, float] = {}
    for key in metric_keys:
        values = [
            value
            for model in models
            if (value := _number_or_none(model.get("scores", {}).get(key))) is not None
        ]
        if values:
            baselines[key] = max(values)
    return baselines


def aa_score_baseline(models: list[dict[str, Any]], aa_key: str) -> float:
    values = [
        value
        for model in models
        if (value := _number_or_none(model.get("aa", {}).get(aa_key))) is not None
    ]
    return max(values) if values else 100.0


def normalized_metric_value(
    key: str,
    value: float,
    normalization: str = "raw",
    metric_baselines: dict[str, Any] | None = None,
) -> float:
    if normalization != "relative-best":
        return value
    baseline = _number_or_none((metric_baselines or {}).get(key))
    if baseline is None or baseline <= 0:
        return 0.0
    return max(value, 0.0) / baseline


def write_site_payload(
    input_csv: Path,
    output_json: Path,
    output_js: Path | None = None,
    external_benchmarks_json: Path | None = DEFAULT_EXTERNAL_BENCHMARKS_JSON,
) -> dict[str, Any]:
    external_benchmarks = (
        load_external_benchmarks(external_benchmarks_json)
        if external_benchmarks_json is not None
        else {"version": 1, "sources": [], "benchmarks": [], "results": []}
    )
    payload = build_site_payload(read_csv_rows(input_csv), external_benchmarks)
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
    parser.add_argument(
        "--external-benchmarks-json",
        default=str(DEFAULT_EXTERNAL_BENCHMARKS_JSON),
        help="Benchmark scores JSON to merge into the site payload.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    output_json = Path(args.output_json)
    output_js = Path(args.output_js) if args.output_js else output_json.with_suffix(".js")
    payload = write_site_payload(
        Path(args.input_csv),
        output_json,
        output_js,
        Path(args.external_benchmarks_json) if args.external_benchmarks_json else None,
    )
    print(
        f"Wrote {output_json} with {payload['summary']['modelRows']} rows "
        f"across {payload['summary']['variantGroups']} dedupe groups."
    )
    return 0


def external_sources_payload(external_benchmark_data: dict[str, Any]) -> list[dict[str, Any]]:
    sources = [dict(source) for source in EXTERNAL_SOURCES]
    benchmarks = {
        benchmark["id"]: benchmark
        for benchmark in external_benchmark_data.get("benchmarks", [])
        if benchmark.get("id")
    }
    results_by_source: dict[str, list[dict[str, Any]]] = {}
    for result in external_benchmark_data.get("results", []):
        source_id = result.get("sourceId")
        if source_id:
            results_by_source.setdefault(source_id, []).append(result)

    for source in external_benchmark_data.get("sources", []):
        source_id = source.get("id")
        if not source_id:
            continue
        results = results_by_source.get(source_id, [])
        benchmark_ids = sorted({result.get("benchmarkId") for result in results if result.get("benchmarkId")})
        related_metrics = [external_metric_key(benchmark_id) for benchmark_id in benchmark_ids]
        benchmark_labels = [
            benchmarks[benchmark_id].get("label", benchmark_id)
            for benchmark_id in benchmark_ids
            if benchmark_id in benchmarks
        ]
        focus = ", ".join(benchmark_labels[:6])
        if len(benchmark_labels) > 6:
            focus += f", +{len(benchmark_labels) - 6}"
        model_aliases = [str(alias) for alias in source.get("modelAliases", []) if alias]
        model_keys = [str(key) for key in source.get("modelKeys", []) if key]
        coverage = f"{len(results)} model-benchmark scores"
        if not results:
            coverage = source.get("coverage") or (
                f"{len(model_aliases) + len(model_keys)} model references"
                if model_aliases or model_keys
                else "0 model-benchmark scores"
            )
        sources.append(
            {
                "id": source_id,
                "label": source.get("label") or source_id,
                "icon": _initials(source.get("label") or source_id),
                "url": source.get("url") or "",
                "category": source.get("category") or "Benchmark",
                "coverage": coverage,
                "focus": focus or source.get("note") or "Benchmark evaluation reference.",
                "note": source.get("note") or source.get("collectionStatus") or "",
                "scoreStatus": "benchmark" if related_metrics else source.get("scoreStatus") or "reference",
                "defaultWeight": 0,
                "relatedMetrics": related_metrics,
                "benchmarkIds": benchmark_ids,
                "modelAliases": model_aliases,
                "modelKeys": model_keys,
            }
        )
    return sources


def attach_external_benchmark_scores(
    models: list[dict[str, Any]],
    external_benchmark_data: dict[str, Any],
) -> None:
    for model in models:
        model["externalBenchmarks"] = []

    for result in external_benchmark_data.get("results", []):
        value = _number_or_none(result.get("value"))
        benchmark_id = result.get("benchmarkId")
        if value is None or not benchmark_id:
            continue
        model = find_external_benchmark_model(models, result.get("modelAliases") or [result.get("model")])
        if model is None:
            continue
        key = external_metric_key(str(benchmark_id))
        model["scores"][key] = value
        model["externalBenchmarks"].append(
            {
                "benchmarkId": benchmark_id,
                "metricKey": key,
                "label": result.get("benchmarkLabel") or benchmark_id,
                "value": value,
                "unit": result.get("unit") or "%",
                "sourceId": result.get("sourceId") or "",
                "sourceLabel": result.get("sourceLabel") or "",
                "sourceUrl": result.get("sourceUrl") or "",
            }
        )


def find_external_benchmark_model(
    models: list[dict[str, Any]],
    aliases: Iterable[Any],
) -> dict[str, Any] | None:
    model_keys: dict[str, dict[str, Any]] = {}
    for model in models:
        for value in (model.get("slug"), model.get("modelKey"), model.get("model")):
            key = _match_key(value)
            if key and key not in model_keys:
                model_keys[key] = model

    for alias in aliases:
        key = _match_key(alias)
        if key in model_keys:
            return model_keys[key]
    return None


def _model_payload(row: dict[str, Any], metric_keys: list[str]) -> dict[str, Any]:
    model = str(row.get("model") or "")
    slug = str(row.get("slug") or "")
    creator = str(row.get("creator") or "")
    open_source_categorization = str(row.get("open_source_categorization") or "")
    scores = {key: _number_or_none(row.get(key)) for key in metric_keys}
    aa_scores = {key: _number_or_none(row.get(column)) for key, column in AA_PRESET_COLUMNS.items()}
    pricing = pricing_payload(row)
    detail_payload = model_detail_payload(row)

    payload = {
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
        "modelIcon": model_icon(creator, model, row),
        "medianOutputSpeed": _number_or_none(row.get("median_output_speed")),
        "aa": aa_scores,
        "aaCostUsd": pricing["aaIndexCostUsd"],
        "pricing": pricing,
        "scores": scores,
        "externalBenchmarks": [],
    }
    if detail_payload:
        payload.update(detail_payload)
    return payload


def model_detail_payload(row: dict[str, Any]) -> dict[str, Any]:
    slug = str(row.get("slug") or "").strip()
    model = str(row.get("model") or "").strip()
    model_key = str(row.get("model_key") or "").strip()
    override = (
        MODEL_DETAIL_OVERRIDES.get(slug)
        or MODEL_DETAIL_OVERRIDES.get(model)
        or MODEL_DETAIL_OVERRIDES.get(model_key)
        or {}
    )
    input_flags = modality_flags_from_row(row, "input")
    output_flags = modality_flags_from_row(row, "output")
    if input_flags is None and override.get("inputModalities"):
        input_flags = modality_flags_from_list(override.get("inputModalities") or [])
    if output_flags is None and override.get("outputModalities"):
        output_flags = modality_flags_from_list(override.get("outputModalities") or [])

    if not override and input_flags is None and output_flags is None:
        return {}
    details = dict(override.get("modelDetails") or {})
    if input_flags is not None or output_flags is not None:
        details["modalities"] = {
            "input": input_flags or {},
            "output": output_flags or {},
        }
    return {
        "inputModalities": modality_labels(input_flags, override.get("inputModalities") or ["Text"]),
        "outputModalities": modality_labels(output_flags, override.get("outputModalities") or ["Text"]),
        "modelDetails": details,
    }


def modality_flags_from_row(row: dict[str, Any], direction: str) -> dict[str, bool] | None:
    values: dict[str, bool] = {}
    saw_value = False
    for key, _label, _icon in MODALITY_SPECS:
        raw = row.get(f"{direction}_modality_{key}")
        parsed = _bool_or_none(raw)
        if parsed is None:
            continue
        values[key] = parsed
        saw_value = True
    return values if saw_value else None


def modality_flags_from_list(values: Iterable[Any]) -> dict[str, bool]:
    normalized = {_match_key(value) for value in values}
    flags: dict[str, bool] = {}
    for key, label, icon in MODALITY_SPECS:
        aliases = {key, _match_key(label), _match_key(icon)}
        if key == "speech":
            aliases.update({"audio", "sound", "voice"})
        flags[key] = bool(normalized & aliases)
    return flags


def modality_labels(flags: dict[str, bool] | None, fallback: Iterable[Any]) -> list[str]:
    if flags is None:
        return [str(value) for value in fallback if value]
    labels = [label for key, label, _icon in MODALITY_SPECS if flags.get(key)]
    return labels


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


def model_icon(creator: str, model: str = "", row: dict[str, Any] | None = None) -> dict[str, str]:
    title = creator.strip() or model.strip() or "Unknown"
    label = PROVIDER_ICON_LABELS.get(title) or _initials(title)
    logo_filename = _logo_filename_from_row(row or {})
    slug = provider_logo_slug(title)
    icon = {
        "label": label,
        "fallbackLabel": label,
        "title": title,
        "src": f"{LOCAL_LOGO_DIR}/{logo_filename or f'{slug}_small.svg'}",
    }
    color = str((row or {}).get("creator_color") or "").strip()
    if color:
        icon["color"] = color
    return icon


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


def _logo_filename_from_row(row: dict[str, Any]) -> str:
    for key in ("creator_logo_small_url", "creator_logo_url"):
        value = str(row.get(key) or "").strip()
        if not value:
            continue
        filename = Path(urlparse(value).path).name
        if filename and "." in filename:
            return filename
    return ""


def _match_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


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
            "kind": "frontier-groups",
            "description": "Frontier 综合口径：60% AA suite，剩余 40% 按原 Frontier 非 AA 组比例分配。每个测试项先除以该项最高分，组内和组间使用几何加权均值；组内证据覆盖率和缺失组覆盖率都按 0.25 次方折扣。",
            "calculation": "geometric",
            "normalization": "relative-best",
            "missingPolicy": "coverage-discount",
            "coverageDiscountExponent": 0.25,
            "groupMetricCoverageDiscountExponent": 0.25,
            "groupWeights": FRONTIER_GROUP_WEIGHTS,
            "groups": FRONTIER_INDEX_GROUPS,
            "weights": DEFAULT_FRONTIER_WEIGHTS,
        },
        "aa-intelligence": {
            "label": "AA Intelligence",
            "kind": "aa-column",
            "column": "aa-intelligence",
            "description": "Artificial Analysis 官方 Intelligence Index。",
            "weights": AA_INTELLIGENCE_SUITE_WEIGHTS,
        },
        "aa-coding": {
            "label": "AA Coding",
            "kind": "aa-column",
            "column": "aa-coding",
            "description": "Artificial Analysis 官方 Coding Index。",
            "weights": AA_CODING_SUITE_WEIGHTS,
        },
        "aa-agentic": {
            "label": "AA Agentic",
            "kind": "aa-column",
            "column": "aa-agentic",
            "description": "Artificial Analysis 官方 Agentic Index。",
            "weights": AA_AGENTIC_SUITE_WEIGHTS,
        },
        "custom": {
            "label": "自定义占比",
            "kind": "weighted-metrics",
            "description": "默认使用 AInsights Index Frontier 配置；按用户设置的分数基线、均值方式、缺失处理、覆盖率门槛和逐项权重实时计算。",
            "ignoreMissing": True,
            "calculation": "geometric",
            "normalization": "relative-best",
            "missingPolicy": "coverage-discount",
            "coverageDiscountExponent": 0.25,
            "groupMetricCoverageDiscountExponent": 0.25,
            "weights": DEFAULT_FRONTIER_WEIGHTS,
        },
    }


def _number_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _bool_or_none(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    text = str(value or "").strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n"}:
        return False
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
