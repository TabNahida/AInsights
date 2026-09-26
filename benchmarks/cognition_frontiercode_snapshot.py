"""Pinned benchmark-owner FrontierCode 1.1 Main leaderboard observations.

The CSV is a checked extract of Cognition's *All reasoning levels* table on
2026-09-23. It contains only rows with an explicit effort and an exact model
configuration in the site catalogue. The official table's Score column is a
weighted rubric score; Pass rate is a different statistic. Cognition evaluates
models using different agent harnesses, retained on every result below.

The separate benchmark ID prevents a vendor-run Main score from silently
replacing an owner-run score, or earning another bonus as the same observation.
The scoring registry must select at most one Main representation per board.
"""

from __future__ import annotations

import csv
import hashlib
from decimal import Decimal
from pathlib import Path
from typing import Any


SNAPSHOT_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "benchmarks"
    / "cognition_frontiercode_main_2026-09-23.csv"
)
SNAPSHOT_SHA256 = "8d55e840271ee7ccfd9f6dd3e25c83adbb48c1b0bfba185ba2859fe51ede0c2a"
BENCHMARK_ID = "frontiercode-v1-1-main-cognition"
BENCHMARK_LABEL = "FrontierCode v1.1 Main (Cognition run)"
SOURCE_ID = "cognition-frontiercode-v1-1-main-2026-09-23"
SOURCE_URL = "https://cognition.com/frontiercode"
DATA_URL = "https://cognition.com/data/frontiercode-leaderboard/data.json"
DATA_SHA256 = "edba28c872b94a4abf665ed5443c52a001c75646eb4ae01a2c83a794128893bc"
METHODOLOGY_URL = "https://cognition.com/blog/frontier-code-1.1"

# Keys are literal model names in the official table. A model/effort with no
# exact site counterpart (or with unspecified fallback behavior) is omitted.
SITE_MODEL_PREFIX = {
    "Opus 5": "Claude Opus 5",
    "Opus 4.8": "Claude Opus 4.8",
    "Opus 4.7": "Claude Opus 4.7",
    "Sonnet 5": "Claude Sonnet 5",
    "Sonnet 4.6": "Claude Sonnet 4.6",
    "GPT-6 Astra": "GPT-6 Astra",
    "GPT-6 Sol": "GPT-6 Sol",
    "GPT-6 Luna": "GPT-6 Luna",
    "GPT-5.6 Sol": "GPT-5.6 Sol",
    "GPT-5.6 Terra": "GPT-5.6 Terra",
    "GPT-5.6 Luna": "GPT-5.6 Luna",
    "GPT-5.5": "GPT-5.5",
    "GPT-5.4-mini": "GPT-5.4 mini",
    "Grok 4.6": "Grok 4.6",
    "Grok 4.7": "Grok 4.7",
    "Grok 4.5": "Grok 4.5",
    "Gemini 3.7 Flash": "Gemini 3.7 Flash",
    "Gemini 3.8 Flash": "Gemini 3.8 Flash",
    "GLM 5.3": "GLM-5.3",
}
ALLOWED_EFFORTS = frozenset({"low", "medium", "high", "xhigh", "max"})
ALLOWED_HARNESSES = frozenset({"claude-code", "codex", "grok-build", "chisel"})


def load_cognition_frontiercode_snapshot() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Return the pinned owner source and exact-configuration score rows."""

    raw = SNAPSHOT_PATH.read_bytes()
    actual_hash = hashlib.sha256(raw).hexdigest()
    if actual_hash != SNAPSHOT_SHA256:
        raise ValueError(f"Cognition FrontierCode snapshot hash changed: {actual_hash}")

    with SNAPSHOT_PATH.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["Model", "Effort", "Score", "Harness"]:
            raise ValueError("Cognition FrontierCode snapshot schema changed")
        rows = list(reader)

    if not rows:
        raise ValueError("Cognition FrontierCode snapshot is empty")
    identities = [(row["Model"], row["Effort"]) for row in rows]
    if len(set(identities)) != len(rows):
        raise ValueError("Duplicate Cognition FrontierCode model/effort pair")

    source = {
        "id": SOURCE_ID,
        "label": "Cognition FrontierCode 1.1 Main official leaderboard",
        "url": SOURCE_URL,
        "category": "Benchmark owner leaderboard",
        "collectionStatus": "pinned-official-leaderboard; checked 2026-09-25",
        "note": (
            "Cognition's FrontierCode 1.1 Main 100-task set, All reasoning levels, "
            "Score column (weighted rubric aggregate), checked 2026-09-25 "
            "against the public JSON feed to its displayed 0.1-point precision. "
            "Flagged unfair internet use receives zero. Rows use different agent "
            "harnesses, named per result. Cognition also develops the SWE-2 coding "
            "agent; the benchmark is not an independent common-harness model eval. "
            "Diamond is deprecated; Extended and vendor-reported Main scores are separate."
        ),
        "snapshotFile": str(SNAPSHOT_PATH.relative_to(SNAPSHOT_PATH.parents[2])).replace("\\", "/"),
        "snapshotSha256": SNAPSHOT_SHA256,
        "snapshotRows": len(rows),
        "dataUrl": DATA_URL,
        "ownerDataSha256": DATA_SHA256,
        "benchmarkVersion": "FrontierCode 1.1 Main",
        "scoreSelection": "Score (weighted rubric aggregate)",
        "methodologyUrl": METHODOLOGY_URL,
    }

    results = []
    for row in rows:
        model, effort, harness = row["Model"], row["Effort"], row["Harness"]
        if model not in SITE_MODEL_PREFIX or effort not in ALLOWED_EFFORTS:
            raise ValueError(f"Unmapped Cognition model/effort: {model} {effort}")
        if harness not in ALLOWED_HARNESSES:
            raise ValueError(f"Unknown Cognition harness: {harness}")
        score = Decimal(row["Score"])
        if not Decimal(0) <= score <= Decimal(100):
            raise ValueError(f"Invalid Cognition score: {model} {effort}")
        model_key = f"{SITE_MODEL_PREFIX[model]} ({effort}) [R]"
        results.append(
            {
                "benchmarkId": BENCHMARK_ID,
                "benchmarkLabel": BENCHMARK_LABEL,
                "model": model_key,
                "modelAliases": [model_key],
                "value": float(score),
                "unit": "%",
                "sourceId": SOURCE_ID,
                "sourceUrl": SOURCE_URL,
                "sourceLabel": source["label"],
                "variantScoped": True,
                "modelScoreEligible": True,
                "evidenceEligible": True,
                "configurationConfidence": "explicit",
                "effort": effort,
                "agentHarness": harness,
                "systemScore": True,
                "scoreOrigin": "cognition-owner-run",
                "scoreSelection": "Score (weighted rubric aggregate)",
                "configurationNote": (
                    f"Cognition FrontierCode 1.1 Main; {model} at {effort} effort "
                    f"using the {harness} agent harness."
                ),
            }
        )
    return source, results
