"""Attach reviewed visual evaluations for display, never to ranking scores.

Explicit slugs distinguish tested configurations from related configurations.
Neither fuzzy family matching nor cross-benchmark score substitution is allowed.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_PATH = Path(__file__).resolve().parents[1] / "data/benchmarks/vision_evidence.json"
VISUAL_BENCHMARKS = {
    "mmmu-pro": "MMMU-Pro",
    "mmmu-pro-no-tools": "MMMU-Pro (no tools)",
    "mmmu-pro-tools": "MMMU-Pro (with tools)",
    "mmmu-pro-python": "MMMU-Pro (Python)",
    "mmmu-pro-10-choice": "MMMU-Pro (10 choice)",
    "mmmu-pro-vision-only": "MMMU-Pro (vision only)",
    "mmmu": "MMMU",
    "mathvista": "MathVista",
    "charxiv-reasoning": "CharXiv Reasoning (published protocol)",
    "charxiv-no-tools": "CharXiv Reasoning (no tools)",
    "charxiv-tools": "CharXiv Reasoning (with tools)",
    "chartography-no-tools": "Chartography (no tools)",
    "chartography-tools": "Chartography (with tools)",
}


def load_vision_evidence(path: Path = DEFAULT_PATH) -> list[dict]:
    rows = json.loads(path.read_text(encoding="utf-8"))["results"]
    seen = set()
    for row in rows:
        if row["benchmarkId"] not in VISUAL_BENCHMARKS:
            raise ValueError(f"Unknown visual benchmark: {row['benchmarkId']}")
        value = row["value"]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 100:
            raise ValueError("Visual scores must be finite percentages")
        if urlparse(row["sourceUrl"]).scheme != "https" or not row.get("configuration"):
            raise ValueError("Visual evidence requires an HTTPS source and configuration")
        for slug in row["modelSlugs"] + row.get("referenceSlugs", []):
            key = (slug, row["benchmarkId"], row["sourceUrl"])
            if key in seen:
                raise ValueError(f"Duplicate visual evidence: {key}")
            seen.add(key)
    return rows


def attach_vision_evidence(models: list[dict], rows: list[dict] | None = None) -> None:
    rows = load_vision_evidence() if rows is None else rows
    for model in models:
        evidence = []
        for row in rows:
            slug = model.get("slug", "")
            exact = slug in row["modelSlugs"]
            if not exact and slug not in row.get("referenceSlugs", []):
                continue
            evidence.append({
                "benchmarkId": row["benchmarkId"],
                "label": VISUAL_BENCHMARKS[row["benchmarkId"]],
                "value": row["value"], "unit": "%",
                "sourceUrl": row["sourceUrl"], "sourceLabel": row["sourceLabel"],
                "configuration": row["configuration"], "exactConfiguration": exact,
                "reviewedAt": row["reviewedAt"],
            })
        for row in model.get("externalBenchmarks", []):
            key = row.get("benchmarkId")
            if key not in VISUAL_BENCHMARKS or not isinstance(row.get("value"), (int, float)):
                continue
            if any(item["benchmarkId"] == key for item in evidence):
                continue
            evidence.append({
                "benchmarkId": key, "label": VISUAL_BENCHMARKS[key],
                "value": row["value"], "unit": "%",
                "sourceUrl": row["sourceUrl"], "sourceLabel": row["sourceLabel"],
                "configuration": row.get("configurationNote") or row.get("effort") or "Published model configuration; effort unspecified",
                "exactConfiguration": bool(row.get("variantScoped") and row.get("modelScoreEligible", True) and not row.get("sharedFromVariant")),
            })
        model["visionBenchmarks"] = evidence
