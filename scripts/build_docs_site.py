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
DEFAULT_RANKING_OUTPUT_DIR = (
    PROJECT_ROOT / "analysis" / "irt_leaderboard_exploration" / "outputs"
)

PRIMARY_RANKING_METHOD = "twopl_sparse_70_30_rank_mean"
PRIMARY_COMPONENT_WEIGHTS = {
    "twopl": 0.70,
    "sparseRasch": 0.30,
}
RANKING_METHOD_KEYS = {
    "rasch": "rasch_equal_board",
    "sparseRasch": "rasch_sparse_item_sensitivity",
    "twopl": "twopl_equal_board",
    "denseRasch": "rasch_dense_item_sensitivity",
}
RANKING_BOARD_IDS = (
    "coding",
    "agentic-tool-work",
    "hard-reasoning",
    "knowledge-science",
    "instruction-context",
)

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
AINDEX_REGULAR_WEIGHTS = {
    "Terminal-Bench v2.1": 28,
    "Terminal-Bench Hard": 22,
    "SciCode": 6,
    "LiveCodeBench": 20,
    "Humanity's Last Exam": 5,
    "GPQA Diamond": 2,
    "AIME 2025": 2,
    "AA-Omniscience Accuracy": 1,
    "CritPt": 13,
    "AA-LCR": 1,
    "IFBench": 0,
}
AINDEX_METRIC_TRANSFORMS = [
    {
        "type": "log1p",
        "factor": 5,
        "metrics": [
            "Terminal-Bench Hard",
            "SciCode",
            "Humanity's Last Exam",
            "CritPt",
        ],
    },
]
AINDEX_BONUS_WEIGHTS = {
    "benchmark:swe-bench-pro": 1.8,
    "benchmark:swe-bench-verified": 1.5,
    "benchmark:swe-bench-multilingual": 1.0,
    "benchmark:terminal-bench-2": 1.5,
    "benchmark:terminal-bench-2-1": 1.2,
    "benchmark:frontiercode-diamond": 1.5,
    "benchmark:frontiermath-tier-1-3": 1.0,
    "benchmark:frontiermath-tier-4": 1.2,
    "benchmark:browsecomp": 1.0,
    "benchmark:hle-tools": 1.0,
    "benchmark:mcp-atlas": 0.8,
    "benchmark:osworld-verified": 0.7,
}
AINDEX_BONUS_CAP = 2
AINDEX_METRIC_FALLBACKS = [
    {
        "type": "linear-fit",
        "source": "benchmark:livecodebench",
        "target": "LiveCodeBench",
        "minimumPairs": 2,
        "min": 0,
        "max": 100,
    },
]
AINDEX_GROUPS = [
    {
        "id": "coding",
        "label": "Coding",
        "weight": 40,
        "metrics": [
            {"key": "benchmark:swe-bench-pro", "weight": 1.5},
            {"key": "LiveCodeBench", "weight": 1.2},
            {"key": "benchmark:swe-bench-verified", "weight": 1.1},
            {"key": "Terminal-Bench Hard", "weight": 1.0},
            {"key": "Terminal-Bench v2.1", "weight": 0.9},
            {"key": "benchmark:swe-bench-multilingual", "weight": 0.8},
            {"key": "SciCode", "weight": 0.8},
        ],
    },
    {
        "id": "agentic-tool-work",
        "label": "Agentic/tool work",
        "weight": 24,
        "metrics": [
            {"key": "benchmark:swe-bench-pro", "weight": 1.3},
            {"key": "benchmark:browsecomp", "weight": 1.0},
            {"key": "benchmark:hle-tools", "weight": 1.0},
            {"key": "benchmark:mcp-atlas", "weight": 0.9},
            {"key": "benchmark:osworld-verified", "weight": 0.8},
            {"key": "benchmark:gdpval-wins-ties", "weight": 0.8},
            {"key": "Terminal-Bench Hard", "weight": 0.8},
            {"key": "benchmark:gdpval-aa-elo", "weight": 0.7},
            {"key": "benchmark:toolathlon", "weight": 0.6},
            {"key": "Terminal-Bench v2.1", "weight": 0.5},
            {"key": "AA-LCR", "weight": 0.5},
        ],
    },
    {
        "id": "hard-reasoning",
        "label": "Hard reasoning",
        "weight": 20,
        "metrics": [
            {"key": "Humanity's Last Exam", "weight": 1.3},
            {"key": "benchmark:hle", "weight": 1.2},
            {"key": "benchmark:frontiermath-tier-4", "weight": 1.2},
            {"key": "CritPt", "weight": 1.1},
            {"key": "benchmark:frontiermath-tier-1-3", "weight": 1.0},
            {"key": "GPQA Diamond", "weight": 0.9},
            {"key": "benchmark:gpqa-diamond", "weight": 0.8},
            {"key": "AIME 2025", "weight": 0.7},
            {"key": "benchmark:aime-2025", "weight": 0.7},
            {"key": "benchmark:aime-2026", "weight": 0.3},
            {"key": "benchmark:hmmt-2026-feb", "weight": 0.3},
        ],
    },
    {
        "id": "knowledge-science",
        "label": "Knowledge/science",
        "weight": 8,
        "metrics": [
            {"key": "AA-Omniscience Accuracy", "weight": 1.0},
            {"key": "GPQA Diamond", "weight": 0.9},
            {"key": "Humanity's Last Exam", "weight": 0.8},
            {"key": "benchmark:mmmlu", "weight": 0.7},
            {"key": "benchmark:mmmu-pro", "weight": 0.7},
            {"key": "SciCode", "weight": 0.5},
            {"key": "benchmark:mmlu-pro", "weight": 0.2},
        ],
    },
    {
        "id": "instruction-context",
        "label": "Instruction/context",
        "weight": 8,
        "metrics": [
            {"key": "IFBench", "weight": 1.0},
            {"key": "AA-LCR", "weight": 0.9},
            {"key": "CritPt", "weight": 0.7},
            {"key": "benchmark:charxiv-tools", "weight": 0.6},
            {"key": "benchmark:charxiv-no-tools", "weight": 0.5},
        ],
    },
]
FRONTIER_INDEX_GROUPS = [
    {
        "id": "aa-suite",
        "label": "AA suite",
        "weight": 90,
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
        "weight": 10 / 3,
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
        "weight": 2.5,
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
        "weight": 10 / 3,
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
        "weight": 5 / 6,
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
DEFAULT_AINDEX_WEIGHTS: dict[str, float] = {}
for group in AINDEX_GROUPS:
    group_weight = float(group["weight"])
    metrics = list(group["metrics"])
    total_metric_weight = sum(
        float(metric.get("weight") or 0.0)
        for metric in metrics
        if isinstance(metric, dict)
    )
    if total_metric_weight <= 0:
        continue
    for metric in metrics:
        key = str(metric.get("key") or "") if isinstance(metric, dict) else str(metric)
        metric_weight = float(metric.get("weight") or 0.0) if isinstance(metric, dict) else 1.0
        if not key or not metric_weight or metric_weight <= 0:
            continue
        DEFAULT_AINDEX_WEIGHTS[key] = DEFAULT_AINDEX_WEIGHTS.get(key, 0.0) + (
            group_weight * metric_weight / total_metric_weight
        )

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
    r"\s*\((?:(?:x?high|medium|low|max|min|minimal|default|fast|thinking|non[- ]reasoning|reasoning)(?:\s*,\s*|\s+)*)+\)\s*$",
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
    apply_metric_fallbacks(models, AINDEX_METRIC_FALLBACKS)
    baselines = metric_baselines(models, metric_keys)
    aa_intelligence_max = aa_score_baseline(models, "aa-intelligence")

    return {
        "version": 2,
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": {
            "label": "Artificial Analysis Intelligence Evaluations",
            "url": SOURCE_URL,
            "methodologyUrl": "methodology.html",
            "methodologyNote": (
                "AInsights Index ranks each evaluated configuration by the arithmetic mean of its "
                "equal-board Rasch rank and sparse-item Rasch rank. Coverage is an eligibility and "
                "evidence-tier signal, not a model-specific score correction."
            ),
        },
        "defaultPreset": "zhihu-adjusted",
        "defaultDedupe": True,
        "metrics": [
            {
                "key": key,
                "label": key,
                "defaultWeight": DEFAULT_AINDEX_WEIGHTS.get(key, 0),
            }
            for key in [spec.column for spec in SCORE_SPECS]
        ]
        + [
            {
                "key": external_metric_key(benchmark["id"]),
                "label": benchmark.get("label") or benchmark["id"],
                "defaultWeight": DEFAULT_AINDEX_WEIGHTS.get(external_metric_key(benchmark["id"]), 0),
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
    preset_display_scale = _number_or_none(preset.get("displayScale"))
    effective_display_scale = preset_display_scale if preset_display_scale is not None else display_scale
    if preset["kind"] == "aa-column":
        score = _number_or_none(model.get("aa", {}).get(preset["column"]))
        return {
            "score": score,
            "coverage": 1 if score is not None else 0,
            "availableWeight": 1 if score is not None else 0,
        }

    if preset["kind"] == "precomputed-ranking":
        profile = model.get("rankingProfile") or {}
        score = _number_or_none(profile.get("displayScore"))
        return {
            "score": score,
            "coverage": int(profile.get("boardTestSlotsTotal") or 0),
            "availableWeight": 0,
            "rank": int(profile["publicationRank"])
            if profile.get("publicationRank") is not None
            else None,
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
            single_metric_coverage_discount_exponent=float(
                preset.get("singleMetricCoverageDiscountExponent")
                if preset.get("singleMetricCoverageDiscountExponent") is not None
                else preset.get("groupMetricCoverageDiscountExponent") or 0
            ),
            weak_prior_ratio=float(preset.get("weakPriorRatio") or 0.35),
            metric_baselines=metric_baselines,
            display_scale=effective_display_scale,
        )

    if preset["kind"] == "regular-plus-bonus":
        return regular_plus_bonus_score(
            model,
            preset.get("regularWeights", {}),
            preset.get("bonusWeights", {}),
            bonus_cap=float(preset.get("bonusCap") or 0),
            method=str(preset.get("calculation") or "geometric"),
            normalization=str(preset.get("normalization") or "relative-best"),
            coverage_discount_exponent=float(preset.get("coverageDiscountExponent") or 0),
            metric_baselines=metric_baselines,
            display_scale=effective_display_scale,
            metric_transforms=preset.get("metricTransforms", []),
        )

    return weighted_metric_score(
        model,
        preset.get("weights", {}),
        bool(preset.get("ignoreMissing")),
        int(preset.get("minCoverage") or 0),
        method=str(preset.get("calculation") or "arithmetic"),
        normalization=str(preset.get("normalization") or "raw"),
        metric_baselines=metric_baselines,
        display_scale=effective_display_scale,
        missing_policy=preset.get("missingPolicy"),
        coverage_discount_exponent=float(preset.get("coverageDiscountExponent") or 0),
        weak_prior_ratio=float(preset.get("weakPriorRatio") or 0.35),
    )


def regular_plus_bonus_score(
    model: dict[str, Any],
    regular_weights: dict[str, Any],
    bonus_weights: dict[str, Any],
    bonus_cap: float = AINDEX_BONUS_CAP,
    method: str = "geometric",
    normalization: str = "relative-best",
    coverage_discount_exponent: float = 0.25,
    metric_baselines: dict[str, Any] | None = None,
    display_scale: float | None = None,
    metric_transforms: Iterable[dict[str, Any]] | None = None,
    metric_fallbacks: dict[str, Any] | None = None,
) -> dict[str, float | int | None]:
    regular = weighted_metric_score(
        model,
        regular_weights,
        True,
        method=method,
        normalization=normalization,
        metric_baselines=metric_baselines,
        display_scale=display_scale,
        missing_policy="coverage-discount",
        coverage_discount_exponent=coverage_discount_exponent,
        metric_transforms=metric_transforms,
        metric_fallbacks=metric_fallbacks,
    )
    base_score = regular["score"]
    if base_score is None:
        return {
            "score": None,
            "coverage": regular["coverage"],
            "availableWeight": regular["availableWeight"],
        }

    bonus_total_weight = sum(
        _number_or_none(weight) or 0.0
        for weight in bonus_weights.values()
        if (_number_or_none(weight) or 0.0) > 0
    )
    bonus_points = 0.0
    bonus_coverage = 0
    if bonus_cap > 0 and bonus_total_weight > 0:
        for key, raw_weight in bonus_weights.items():
            weight = _number_or_none(raw_weight) or 0.0
            if weight <= 0:
                continue
            value = score_metric_value(model, key, metric_fallbacks)
            if value is None:
                continue
            bonus_points += (
                bonus_cap
                * weight
                * normalized_metric_value(key, value, normalization, metric_baselines)
                / bonus_total_weight
            )
            bonus_coverage += 1

    return {
        "score": base_score + bonus_points,
        "coverage": int(regular["coverage"] or 0) + bonus_coverage,
        "availableWeight": regular["availableWeight"],
    }


def frontier_group_score(
    model: dict[str, Any],
    groups: Iterable[dict[str, Any]],
    method: str = "geometric",
    normalization: str = "relative-best",
    missing_policy: str = "coverage-discount",
    coverage_discount_exponent: float = 0.25,
    group_metric_coverage_discount_exponent: float = 0.0,
    single_metric_coverage_discount_exponent: float | None = None,
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
            single_metric_coverage_discount_exponent=single_metric_coverage_discount_exponent,
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

    if denominator <= 0 or coverage <= 0:
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
    single_metric_coverage_discount_exponent: float | None = None,
    metric_baselines: dict[str, Any] | None = None,
) -> float | None:
    entries: list[tuple[float, float]] = []
    metrics = frontier_group_metric_items(metric_keys)
    total_weight = sum(weight for _, weight in metrics if weight > 0)
    available_weight = 0.0
    metric_count = 0
    for key, weight in metrics:
        if weight <= 0:
            continue
        value = _number_or_none(model.get("scores", {}).get(key))
        if value is None:
            continue
        entries.append((normalized_metric_value(key, value, normalization, metric_baselines), weight))
        available_weight += weight
        metric_count += 1
    if not entries:
        return None
    value = aggregate_weighted_values(entries, available_weight, method)
    discount_exponent = (
        single_metric_coverage_discount_exponent
        if metric_count == 1 and single_metric_coverage_discount_exponent is not None
        else coverage_discount_exponent
    )
    if value is not None and discount_exponent > 0 and total_weight > 0:
        value *= (available_weight / total_weight) ** discount_exponent
    return value


def frontier_group_metric_items(metric_keys: Iterable[Any]) -> list[tuple[str, float]]:
    items: list[tuple[str, float]] = []
    for raw_item in metric_keys:
        if isinstance(raw_item, dict):
            key = str(raw_item.get("key") or "").strip()
            weight = _number_or_none(raw_item.get("weight")) or 0.0
        else:
            key = str(raw_item).strip()
            weight = 1.0
        if key and weight > 0:
            items.append((key, weight))
    return items


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
    metric_transforms: Iterable[dict[str, Any]] | None = None,
    metric_fallbacks: dict[str, Any] | None = None,
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
        value = score_metric_value(model, key, metric_fallbacks)
        if value is None:
            if policy == "weak-prior":
                entries.append((weak_prior_ratio, weight))
                denominator += weight
            elif policy == "zero" or (not policy and not ignore_missing):
                entries.append((0.0, weight))
                denominator += weight
            continue
        score_value = transformed_metric_value(key, value, normalization, metric_baselines, metric_transforms)
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


def score_metric_value(
    model: dict[str, Any],
    key: str,
    metric_fallbacks: dict[str, Any] | None = None,
) -> float | None:
    value = _number_or_none(model.get("scores", {}).get(key))
    if value is not None:
        return value
    if not metric_fallbacks:
        return None
    return _number_or_none(metric_fallbacks.get(key))


def transformed_metric_value(
    key: str,
    value: float,
    normalization: str = "raw",
    metric_baselines: dict[str, Any] | None = None,
    metric_transforms: Iterable[dict[str, Any]] | None = None,
) -> float:
    score = normalized_metric_value(key, value, normalization, metric_baselines)
    for transform in metric_transforms or []:
        metrics = transform.get("metrics") or []
        if key not in metrics:
            continue
        transform_type = str(transform.get("type") or "").strip().lower()
        if transform_type == "log1p":
            factor = _number_or_none(transform.get("factor")) or 0.0
            if factor > 0:
                return math.log1p(factor * max(score, 0.0)) / math.log1p(factor)
    return score


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
    *,
    include_irt_ranking: bool | None = None,
    write_analysis_outputs: bool | None = None,
) -> dict[str, Any]:
    external_benchmarks = (
        load_external_benchmarks(external_benchmarks_json)
        if external_benchmarks_json is not None
        else {"version": 1, "sources": [], "benchmarks": [], "results": []}
    )
    payload = build_site_payload(read_csv_rows(input_csv), external_benchmarks)
    is_default_output = output_json.resolve() == DEFAULT_OUTPUT_JSON.resolve()
    should_attach_ranking = (
        is_default_output if include_irt_ranking is None else include_irt_ranking
    )
    if should_attach_ranking:
        from analysis.irt_leaderboard_exploration.multi_method_evidence_analysis import (
            run_multi_method_analysis_from_payload,
        )

        should_write_analysis = (
            is_default_output
            if write_analysis_outputs is None
            else write_analysis_outputs
        )
        analysis_result = run_multi_method_analysis_from_payload(
            payload,
            output_dir=DEFAULT_RANKING_OUTPUT_DIR,
            write_outputs=should_write_analysis,
        )
        attach_irt_ranking_profiles(payload, analysis_result)
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
    parser.add_argument(
        "--skip-irt-ranking",
        action="store_true",
        help="Build the raw site payload without attaching the precomputed IRT ranking.",
    )
    parser.add_argument(
        "--skip-analysis-outputs",
        action="store_true",
        help="Attach the IRT ranking without refreshing analysis CSV/JSON artifacts.",
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
        include_irt_ranking=not args.skip_irt_ranking,
        write_analysis_outputs=not args.skip_analysis_outputs,
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

    sources_by_id = {
        str(source.get("id") or ""): source
        for source in external_benchmark_data.get("sources", [])
        if source.get("id")
    }
    _attach_external_benchmark_scores_impl(
        models,
        external_benchmark_data,
        sources_by_id,
    )


def attach_irt_ranking_profiles(
    payload: dict[str, Any],
    analysis_result: dict[str, Any],
) -> dict[str, Any]:
    """Attach the precomputed publication ranking to exact selected configs.

    The IRT analysis ranks one exact configuration per ``variantGroup``.  A
    family rank must never be copied to sibling effort/configuration rows, so
    this join is deliberately strict on both variant group and selected slug.
    """

    consensus_rows = _analysis_rows(
        analysis_result,
        "publication_consensus_full_rankings",
        "required_order_consensus_full_rankings",
        "consensus_publication_full_rankings",
    )
    if not consensus_rows:
        raise ValueError("IRT analysis did not return a publication consensus ranking")

    evidence_methods = analysis_result.get("full_rankings") or {}
    publication_methods = analysis_result.get("required_order_full_rankings") or {}
    for method_id in RANKING_METHOD_KEYS.values():
        if method_id not in evidence_methods or method_id not in publication_methods:
            raise ValueError(f"IRT analysis is missing required method {method_id!r}")

    evidence_by_method = {
        method_id: _unique_rows_by_variant_group(evidence_methods[method_id], method_id)
        for method_id in RANKING_METHOD_KEYS.values()
    }
    publication_by_method = {
        method_id: _unique_rows_by_variant_group(publication_methods[method_id], method_id)
        for method_id in RANKING_METHOD_KEYS.values()
    }

    summary = analysis_result.get("summary") or {}
    board_item_pool_sizes = _board_item_pool_sizes(summary, consensus_rows)
    sparse_board_item_pool_sizes = _summary_method_pool_sizes(
        summary,
        "rasch_sparse_item_sensitivity",
    )
    rasch_board_item_pool_sizes = _summary_method_pool_sizes(
        summary,
        "rasch_equal_board",
    )
    dense_board_item_pool_sizes = _summary_method_pool_sizes(
        summary,
        "rasch_dense_item_sensitivity",
    )
    twopl_weight = PRIMARY_COMPONENT_WEIGHTS["twopl"]
    sparse_weight = PRIMARY_COMPONENT_WEIGHTS["sparseRasch"]
    model_by_slug: dict[str, dict[str, Any]] = {}
    for model in payload.get("models", []):
        slug = str(model.get("slug") or "")
        if not slug:
            continue
        if slug in model_by_slug:
            raise ValueError(f"duplicate model slug in site payload: {slug!r}")
        model_by_slug[slug] = model

    population_size = len(consensus_rows)
    attached_slugs: set[str] = set()
    leaderboard_rows: list[dict[str, Any]] = []
    for consensus in consensus_rows:
        variant_group_id = str(consensus.get("variant_group") or "")
        if not variant_group_id:
            raise ValueError("consensus ranking row has no variant_group")

        component_rows = {
            key: evidence_by_method[method_id].get(variant_group_id)
            for key, method_id in RANKING_METHOD_KEYS.items()
        }
        published_components = {
            key: publication_by_method[method_id].get(variant_group_id)
            for key, method_id in RANKING_METHOD_KEYS.items()
        }
        if any(row is None for row in component_rows.values()) or any(
            row is None for row in published_components.values()
        ):
            raise ValueError(
                f"consensus group {variant_group_id!r} is missing a component method row"
            )

        rasch = component_rows["rasch"]
        sparse = component_rows["sparseRasch"]
        twopl = component_rows["twopl"]
        selected_slug = str(consensus.get("slug") or twopl.get("slug") or "")
        for method_key, method_row in component_rows.items():
            method_slug = str(method_row.get("slug") or "")
            if selected_slug != method_slug:
                raise ValueError(
                    f"consensus configuration mismatch for {variant_group_id!r}: "
                    f"selected={selected_slug!r}, {method_key}={method_slug!r}"
                )
        model = model_by_slug.get(selected_slug)
        if model is None:
            raise ValueError(f"ranked slug {selected_slug!r} is absent from site payload")
        if str(model.get("variantGroup") or "") != variant_group_id:
            raise ValueError(
                f"ranked slug {selected_slug!r} has mismatched variant group"
            )
        if selected_slug in attached_slugs:
            raise ValueError(f"ranked slug {selected_slug!r} was attached twice")
        attached_slugs.add(selected_slug)

        boards: dict[str, dict[str, Any]] = {}
        for board_id in RANKING_BOARD_IDS:
            twopl_score = _required_number(twopl, f"{board_id}_score")
            sparse_score = _required_number(sparse, f"{board_id}_score")
            twopl_tests = int(twopl.get(f"{board_id}_tests") or 0)
            sparse_tests = int(sparse.get(f"{board_id}_tests") or 0)
            boards[board_id] = {
                "score": round(
                    twopl_weight * twopl_score + sparse_weight * sparse_score,
                    3,
                ),
                "tests": twopl_tests,
                "sparseTests": sparse_tests,
                "itemPoolSize": board_item_pool_sizes[board_id],
                "sparseItemPoolSize": sparse_board_item_pool_sizes[board_id],
            }

        evidence_coverage_score = _number_or_none(
            consensus.get("evidence_coverage_score")
        )
        if evidence_coverage_score is None:
            evidence_coverage_score = sum(
                100.0
                * (
                    twopl_weight
                    * min(
                        boards[board_id]["tests"]
                        / board_item_pool_sizes[board_id],
                        1.0,
                    )
                    + sparse_weight
                    * min(
                        boards[board_id]["sparseTests"]
                        / sparse_board_item_pool_sizes[board_id],
                        1.0,
                    )
                )
                for board_id in RANKING_BOARD_IDS
            ) / len(RANKING_BOARD_IDS)

        method_profiles: dict[str, dict[str, Any]] = {}
        for key, method_id in RANKING_METHOD_KEYS.items():
            evidence_row = component_rows[key]
            publication_row = published_components[key]
            method_profiles[key] = {
                "id": method_id,
                "publicationRank": int(publication_row["rank"]),
                "evidenceRank": int(evidence_row["rank"]),
                "score": _required_number(evidence_row, "score"),
                "evidenceTier": str(evidence_row.get("evidence_tier") or ""),
                "boards": {
                    board_id: {
                        "score": _required_number(evidence_row, f"{board_id}_score"),
                        "tests": int(evidence_row.get(f"{board_id}_tests") or 0),
                    }
                    for board_id in RANKING_BOARD_IDS
                },
            }

        rank_mean = _number_or_none(
            consensus.get("rank_mean")
            if consensus.get("rank_mean") is not None
            else consensus.get("evidence_mean_rank")
        )
        if rank_mean is None:
            rank_mean = (
                twopl_weight * method_profiles["twopl"]["evidenceRank"]
                + sparse_weight
                * method_profiles["sparseRasch"]["evidenceRank"]
            )
        component_ranks = [
            method_profiles["twopl"]["evidenceRank"],
            method_profiles["sparseRasch"]["evidenceRank"],
        ]
        rank_min = min(component_ranks)
        rank_max = max(component_ranks)
        display_score = _number_or_none(consensus.get("score"))
        if display_score is None:
            display_score = (
                twopl_weight * method_profiles["twopl"]["score"]
                + sparse_weight * method_profiles["sparseRasch"]["score"]
            )

        profile = {
            "method": PRIMARY_RANKING_METHOD,
            "publicationRank": int(consensus["rank"]),
            "evidenceRank": int(
                consensus.get("evidence_rank")
                if consensus.get("evidence_rank") is not None
                else consensus["rank"]
            ),
            "evidenceMeanRank": round(rank_mean, 4),
            "rankMin": rank_min,
            "rankMax": rank_max,
            "rankSpan": rank_max - rank_min,
            "rankPercentile": round(
                100.0 * (population_size - rank_mean) / max(population_size - 1, 1),
                4,
            ),
            "displayScore": round(display_score, 4),
            "evidenceTier": str(
                consensus.get("evidence_tier") or twopl.get("evidence_tier") or ""
            ),
            "publicationOrderRule": str(
                consensus.get("publication_order_rule")
                or summary.get("publication_order_rule")
                or ""
            ),
            "requiredOrderTarget": str(consensus.get("required_order_target") or ""),
            "rankChangeDueToRequiredOrder": int(
                consensus.get("rank_change_due_to_required_order") or 0
            ),
            "uniqueBenchmarkFamilies": int(
                consensus.get("unique_benchmark_families")
                or twopl.get("unique_benchmark_families")
                or 0
            ),
            "boardTestSlotsTotal": int(
                consensus.get("board_test_slots_total")
                or twopl.get("board_test_slots_total")
                or 0
            ),
            "minBoardTests": int(
                consensus.get("min_board_tests") or twopl.get("min_board_tests") or 0
            ),
            "boardsBelowMainTarget": int(
                consensus.get("boards_below_main_target")
                or twopl.get("boards_below_main_target")
                or 0
            ),
            "boards": boards,
            "boardItemPoolSizes": dict(board_item_pool_sizes),
            "boardItemPoolSizesByMethod": {
                "rasch": dict(rasch_board_item_pool_sizes),
                "sparseRasch": dict(sparse_board_item_pool_sizes),
                "twopl": dict(board_item_pool_sizes),
                "denseRasch": dict(dense_board_item_pool_sizes),
            },
            "componentWeights": dict(PRIMARY_COMPONENT_WEIGHTS),
            "evidenceCoverageScore": round(evidence_coverage_score, 3),
            "methods": method_profiles,
        }
        model["rankingProfile"] = profile
        leaderboard_rows.append(
            {
                "publicationRank": profile["publicationRank"],
                "evidenceRank": profile["evidenceRank"],
                "evidenceMeanRank": profile["evidenceMeanRank"],
                "selectedSlug": selected_slug,
                "variantGroup": variant_group_id,
            }
        )

    if len(attached_slugs) != population_size:
        raise ValueError("not every consensus row attached to a unique site model")

    payload["leaderboard"] = {
        "defaultMethod": PRIMARY_RANKING_METHOD,
        "publicationOrderRule": str(summary.get("publication_order_rule") or ""),
        "populationSize": population_size,
        "boardOrder": list(RANKING_BOARD_IDS),
        "boardItemPoolSizes": dict(board_item_pool_sizes),
        "boardItemPoolSizesByMethod": {
            method_id: {
                board_id: int(size)
                for board_id, size in method_sizes.items()
            }
            for method_id, method_sizes in (
                summary.get("board_item_pool_sizes") or {}
            ).items()
            if isinstance(method_sizes, dict)
        },
        "methods": {
            "primary": ["twopl_equal_board", "rasch_sparse_item_sensitivity"],
            "primaryWeights": {
                "twopl_equal_board": twopl_weight,
                "rasch_sparse_item_sensitivity": sparse_weight,
            },
            "comparison": ["rasch_equal_board", "rasch_dense_item_sensitivity"],
            "labels": dict(summary.get("methods") or {}),
        },
        "rows": leaderboard_rows,
    }
    payload.setdefault("summary", {})["rankedVariantGroups"] = population_size
    return payload


def _analysis_rows(analysis_result: dict[str, Any], *keys: str) -> list[dict[str, Any]]:
    for key in keys:
        rows = analysis_result.get(key)
        if rows is not None:
            return list(rows)
    return []


def _unique_rows_by_variant_group(
    rows: Iterable[dict[str, Any]],
    method_id: str,
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = str(row.get("variant_group") or "")
        if not key:
            raise ValueError(f"{method_id} ranking row has no variant_group")
        if key in result:
            raise ValueError(f"{method_id} has duplicate variant group {key!r}")
        result[key] = row
    return result


def _board_item_pool_sizes(
    summary: dict[str, Any],
    consensus_rows: list[dict[str, Any]],
) -> dict[str, int]:
    summary_pools = summary.get("board_item_pool_sizes")
    consensus_pools = (
        consensus_rows[0].get("board_item_pool_sizes")
        if consensus_rows
        else None
    )
    candidates = (
        summary.get("core_board_item_pool_sizes"),
        summary_pools.get("twopl_equal_board")
        if isinstance(summary_pools, dict)
        else None,
        summary_pools.get("rasch_equal_board")
        if isinstance(summary_pools, dict)
        else None,
        summary_pools,
        consensus_pools.get("twopl_equal_board")
        if isinstance(consensus_pools, dict)
        else None,
        consensus_pools.get("rasch_equal_board")
        if isinstance(consensus_pools, dict)
        else None,
        consensus_pools,
    )
    raw = next((value for value in candidates if isinstance(value, dict)), None)
    if raw is None:
        raise ValueError("IRT analysis did not report primary board item-pool sizes")
    sizes = {board_id: int(raw.get(board_id) or 0) for board_id in RANKING_BOARD_IDS}
    if any(size <= 0 for size in sizes.values()):
        raise ValueError(f"invalid IRT board item-pool sizes: {sizes}")
    return sizes


def _summary_method_pool_sizes(
    summary: dict[str, Any],
    method_id: str,
) -> dict[str, int]:
    all_sizes = summary.get("board_item_pool_sizes") or {}
    raw = all_sizes.get(method_id) if isinstance(all_sizes, dict) else None
    if not isinstance(raw, dict):
        raise ValueError(f"IRT analysis did not report item-pool sizes for {method_id}")
    sizes = {board_id: int(raw.get(board_id) or 0) for board_id in RANKING_BOARD_IDS}
    if any(size <= 0 for size in sizes.values()):
        raise ValueError(f"invalid {method_id} board item-pool sizes: {sizes}")
    return sizes


def _required_number(row: dict[str, Any], key: str) -> float:
    value = _number_or_none(row.get(key))
    if value is None:
        raise ValueError(f"ranking row is missing numeric {key!r}")
    return value


def _attach_external_benchmark_scores_impl(
    models: list[dict[str, Any]],
    external_benchmark_data: dict[str, Any],
    sources_by_id: dict[str, dict[str, Any]],
) -> None:
    selected: dict[
        tuple[int, str],
        tuple[tuple[int, int, int, int], dict[str, Any], float],
    ] = {}
    model_by_identity = {id(model): model for model in models}

    for ordinal, result in enumerate(external_benchmark_data.get("results", [])):
        if result.get("modelScoreEligible") is False:
            continue
        value = _number_or_none(result.get("value"))
        benchmark_id = result.get("benchmarkId")
        if value is None or not benchmark_id:
            continue
        model = find_external_benchmark_model(models, result.get("modelAliases") or [result.get("model")])
        if model is None:
            continue
        key = external_metric_key(str(benchmark_id))
        source = sources_by_id.get(str(result.get("sourceId") or ""), {})
        priority = external_result_priority(result, source, ordinal)
        selection_key = (id(model), key)
        current = selected.get(selection_key)
        if current is None or priority > current[0]:
            selected[selection_key] = (priority, result, value)

    for (model_identity, key), (_, result, value) in sorted(
        selected.items(), key=lambda entry: entry[1][0][-1]
    ):
        model = model_by_identity[model_identity]
        benchmark_id = result.get("benchmarkId")
        model["scores"][key] = value
        entry = {
            "benchmarkId": benchmark_id,
            "metricKey": key,
            "label": result.get("benchmarkLabel") or benchmark_id,
            "value": value,
            "unit": result.get("unit") or "%",
            "sourceId": result.get("sourceId") or "",
            "sourceLabel": result.get("sourceLabel") or "",
            "sourceUrl": result.get("sourceUrl") or "",
            "variantScoped": bool(result.get("variantScoped")),
            "evidenceEligible": result.get("evidenceEligible") is not False,
            "effort": result.get("effort") or "",
            "systemScore": bool(result.get("systemScore")),
            "configurationNote": result.get("configurationNote") or "",
        }
        for metadata_key in (
            "derived",
            "estimated",
            "fitted",
            "imputed",
            "interpolated",
            "method",
            "provenance",
            "scoreOrigin",
            "scoreType",
            "valueOrigin",
            "valueType",
            "scoreSelection",
            "configurationConfidence",
            "composite",
            "compositeModelResult",
            "fallbackConfigured",
            "fallbackObserved",
            "fallbackRate",
            "productEvidenceEligible",
            "pureModelEligible",
        ):
            if metadata_key in result:
                entry[metadata_key] = result[metadata_key]
        model["externalBenchmarks"].append(entry)
    share_external_benchmarks_with_variants(models)


def external_result_priority(
    result: dict[str, Any],
    source: dict[str, Any],
    ordinal: int,
) -> tuple[int, int, int, int]:
    """Prefer model-owner evidence over comparator columns from other vendors.

    Official release tables often include competitor columns. Those rows are
    useful when no first-party value exists, but they must not overwrite the
    model owner's own release data merely because they appear later in the
    collector output. Remaining ties intentionally preserve the previous
    last-row-wins behavior so existing refresh ordering stays stable.
    """

    result_aliases = {
        key
        for alias in [result.get("model"), *(result.get("modelAliases") or [])]
        if (key := _match_key(alias))
    }
    source_aliases = {
        key
        for alias in [
            *(source.get("modelAliases") or []),
            *(source.get("modelKeys") or []),
        ]
        if (key := _match_key(alias))
    }
    first_party = int(bool(result_aliases & source_aliases))
    explicit_priority = int(
        _number_or_none(result.get("sourcePriority"))
        or _number_or_none(source.get("sourcePriority"))
        or 0
    )
    official = int("official" in str(source.get("category") or "").lower())
    return first_party, explicit_priority, official, ordinal


def apply_metric_fallbacks(
    models: list[dict[str, Any]],
    fallback_specs: Iterable[dict[str, Any]],
) -> None:
    for spec in fallback_specs:
        if str(spec.get("type") or "").strip().lower() != "linear-fit":
            continue
        source_key = str(spec.get("source") or "").strip()
        target_key = str(spec.get("target") or "").strip()
        if not source_key or not target_key:
            continue
        pairs = [
            (source_value, target_value)
            for model in models
            if (source_value := _number_or_none(model.get("scores", {}).get(source_key))) is not None
            and (target_value := _number_or_none(model.get("scores", {}).get(target_key))) is not None
        ]
        minimum_pairs = int(_number_or_none(spec.get("minimumPairs")) or 2)
        if len(pairs) < minimum_pairs:
            continue
        mean_source = sum(source_value for source_value, _ in pairs) / len(pairs)
        mean_target = sum(target_value for _, target_value in pairs) / len(pairs)
        variance = sum((source_value - mean_source) ** 2 for source_value, _ in pairs)
        if variance <= 0:
            continue
        covariance = sum(
            (source_value - mean_source) * (target_value - mean_target)
            for source_value, target_value in pairs
        )
        slope = covariance / variance
        intercept = mean_target - slope * mean_source
        lower_bound = _number_or_none(spec.get("min"))
        upper_bound = _number_or_none(spec.get("max"))
        for model in models:
            scores = model.get("scores", {})
            if _number_or_none(scores.get(target_key)) is not None:
                continue
            source_value = _number_or_none(scores.get(source_key))
            if source_value is None:
                continue
            fallback_value = intercept + slope * source_value
            if lower_bound is not None:
                fallback_value = max(lower_bound, fallback_value)
            if upper_bound is not None:
                fallback_value = min(upper_bound, fallback_value)
            scores[target_key] = round(fallback_value, 4)


def share_external_benchmarks_with_variants(models: list[dict[str, Any]]) -> None:
    groups: dict[str, list[dict[str, Any]]] = {}
    for model in models:
        variant_key = str(model.get("variantGroup") or "")
        if variant_key:
            groups.setdefault(variant_key, []).append(model)

    for siblings in groups.values():
        benchmark_entries: dict[str, dict[str, Any]] = {}
        benchmark_scores: dict[str, float] = {}
        for sibling in siblings:
            for entry in sibling.get("externalBenchmarks", []):
                if entry.get("variantScoped"):
                    continue
                key = str(entry.get("metricKey") or "")
                value = _number_or_none(entry.get("value"))
                if key and value is not None and key not in benchmark_scores:
                    benchmark_scores[key] = value
                    benchmark_entries[key] = entry

        if not benchmark_scores:
            continue

        for sibling in siblings:
            existing_entries = {
                str(entry.get("metricKey") or "")
                for entry in sibling.get("externalBenchmarks", [])
            }
            for key, value in benchmark_scores.items():
                if _number_or_none(sibling.get("scores", {}).get(key)) is None:
                    sibling["scores"][key] = value
                if key in existing_entries:
                    continue
                entry = dict(benchmark_entries[key])
                entry["sharedFromVariant"] = True
                sibling["externalBenchmarks"].append(entry)
                existing_entries.add(key)


def find_external_benchmark_model(
    models: list[dict[str, Any]],
    aliases: Iterable[Any],
) -> dict[str, Any] | None:
    normalized_aliases = [
        key
        for alias in aliases
        if (key := _match_key(alias))
    ]
    by_model_key: dict[str, dict[str, Any]] = {}
    by_model: dict[str, dict[str, Any]] = {}
    by_slug: dict[str, dict[str, Any]] = {}
    for model in models:
        for value, index in (
            (model.get("modelKey"), by_model_key),
            (model.get("model"), by_model),
            (model.get("slug"), by_slug),
        ):
            key = _match_key(value)
            if key and key not in index:
                index[key] = model

    for key in normalized_aliases:
        for index in (by_model_key, by_model, by_slug):
            if key in index:
                return index[key]
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
    if normalized in {"permissive", "commercial-license"} or "open" in normalized:
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
            "id": "zhihu-adjusted",
            "label": "AInsights Index",
            "kind": "precomputed-ranking",
            "description": "主榜以等板块 2PL 证据名次的 70% 与稀疏项 Rasch 证据名次的 30% 加权排序；测试太少的配置不进入榜单，覆盖度只决定 Main/Provisional 证据标签。Fable 5 第一、GPT-5.6 Sol 第二由透明发布层执行，不改真实分数或证据名次。",
            "calculation": "weighted-rank-mean",
            "normalization": "none",
            "missingPolicy": "eligibility-gate",
            "componentMethods": [
                "twopl_equal_board",
                "rasch_sparse_item_sensitivity",
            ],
            "componentWeights": {
                "twopl_equal_board": 0.70,
                "rasch_sparse_item_sensitivity": 0.30,
            },
            "comparisonMethods": [
                "rasch_equal_board",
                "rasch_dense_item_sensitivity",
            ],
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
            "description": "提供 IRT 方法名次混合、五个能力板块混合，以及逐测试项高级计算；自定义计算不会改变底层真实成绩。",
            "ignoreMissing": True,
            "calculation": "geometric",
            "normalization": "relative-best",
            "missingPolicy": "coverage-discount",
            "coverageDiscountExponent": 0.25,
            "weights": DEFAULT_AINDEX_WEIGHTS,
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
    if normalized == "non-reasoning" or normalized.startswith("non-reasoning-"):
        return "non-reasoning"
    return normalized


if __name__ == "__main__":
    raise SystemExit(main())
