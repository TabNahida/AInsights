"""Pinned Epoch AI FrontierMath Tier 4 v2 leaderboard observations.

The downloaded Epoch export contains 64 runs.  Only model versions with an
unambiguous match to a site model and reasoning configuration are promoted to
score rows.  The full original CSV is retained so excluded runs remain
auditable.  These benchmark-owner results use their own metric ID; they must
not replace the separate values reported in model vendor release tables.
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
    / "epoch_frontiermath_tier_4_v2_2026-09-23.csv"
)
SNAPSHOT_SHA256 = "f14e2982be08db35d817ebbf2c26af95bdd7b877b30cd4711df8b68d04ac8e36"
BENCHMARK_ID = "frontiermath-tier-4-v2-epoch"
BENCHMARK_LABEL = "FrontierMath Tier 4 v2 (Epoch run)"
SOURCE_ID = "epoch-frontiermath-tier-4-v2-2026-09-23"
SOURCE_URL = "https://epoch.ai/benchmarks/frontiermath-tier-4-v2"
DOWNLOAD_PAGE_URL = "https://epoch.ai/benchmarks/use-this-data"

# Epoch's `Model version` is paired with an exact site modelKey.  Configurations
# without a matching effort or checkpoint, and runs with unclear fallback or
# `32K` settings, are deliberately absent.  In particular, `_promax` is not
# interchangeable with `_max`, and a generic site model does not imply `_high`.
EXACT_CONFIG_MODEL_KEYS = {
    "muse-spark-1.3_max": "Muse Spark 1.3 (max) [R]",
    "muse-spark-1.3_xhigh": "Muse Spark 1.3 (xhigh) [R]",
    "gemini-3.8-flash_high": "Gemini 3.8 Flash (high) [R]",
    "gpt-6-astra_low": "GPT-6 Astra (low) [R]",
    "gpt-6-astra_medium": "GPT-6 Astra (medium) [R]",
    "gpt-6-astra_high": "GPT-6 Astra (high) [R]",
    "gpt-6-astra_xhigh": "GPT-6 Astra (xhigh) [R]",
    "gpt-6-astra_max": "GPT-6 Astra (max) [R]",
    "deepseek-v4-pro-0813_max": "DeepSeek V4 Pro 0813 (max) [R]",
    "gemini-3.7-flash_high": "Gemini 3.7 Flash (high) [R]",
    "grok-4.6_xhigh": "Grok 4.6 (xhigh) [R]",
    "deepseek-v4-flash-0731_max": "DeepSeek V4 Flash 0731 (max) [R]",
    "claude-opus-5_max": "Claude Opus 5 (max) [R]",
    "kimi-k3_max": "Kimi K3 (max) [R]",
    "gpt-5.6-terra_max": "GPT-5.6 Terra (max) [R]",
    "gpt-5.6-luna_max": "GPT-5.6 Luna (max) [R]",
    "gpt-5.6-sol_max": "GPT-5.6 Sol (max) [R]",
    "grok-4.5_high": "Grok 4.5 (high) [R]",
    "claude-sonnet-5_max": "Claude Sonnet 5 (max) [R]",
    "glm-5.2_max": "GLM-5.2 (max) [R]",
    "deepseek-v4-pro_max": "DeepSeek V4 Pro (max) [R]",
    "gpt-5.4-pro-2026-03-05_xhigh": "GPT-5.4 Pro (xhigh) [R]",
    "kimi-k2.7-code": "Kimi K2.7 Code [R]",
    "gpt-5.5-pro_xhigh": "GPT-5.5 Pro (xhigh) [R]",
    "gpt-5-mini-2025-08-07_high": "GPT-5 mini (high) [R]",
    "gpt-5-nano-2025-08-07_high": "GPT-5 nano (high) [R]",
    "gpt-5.4-mini-2026-03-17_xhigh": "GPT-5.4 mini (xhigh) [R]",
    "gemini-3.1-pro-preview": "Gemini 3.1 Pro Preview [R]",
    "gpt-5.4-2026-03-05_xhigh": "GPT-5.4 (xhigh) [R]",
    "gpt-5.5_xhigh": "GPT-5.5 (xhigh) [R]",
    "gpt-5.5-instant": "GPT-5.5 Instant (May 2026) [R]",
    "qwen3.7-max": "Qwen3.7 Max [R]",
    "gpt-5.2-2025-12-11_xhigh": "GPT-5.2 (xhigh) [R]",
    "o3-mini-2025-01-31_high": "o3-mini (high) [R]",
    "o4-mini-2025-04-16_high": "o4-mini (high) [R]",
    "gpt-5-2025-08-07_high": "GPT-5 (high) [R]",
    "claude-opus-4-6_max": "Claude Opus 4.6 (max) [R]",
    "claude-opus-4-7_max": "Claude Opus 4.7 (max) [R]",
    "claude-opus-4-8_max": "Claude Opus 4.8 (max) [R]",
    "kimi-k2.6": "Kimi K2.6 [R]",
}


def load_epoch_frontiermath_snapshot() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Return one pinned source and exact-configuration score rows."""

    raw = SNAPSHOT_PATH.read_bytes()
    actual_hash = hashlib.sha256(raw).hexdigest()
    if actual_hash != SNAPSHOT_SHA256:
        raise ValueError(f"Epoch FrontierMath snapshot hash changed: {actual_hash}")

    with SNAPSHOT_PATH.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        required = {
            "Model version",
            "Best score (across scorers)",
            "Release date",
            "Started at",
            "id",
        }
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Epoch FrontierMath snapshot schema changed")
        source_rows = list(reader)

    by_version = {row["Model version"]: row for row in source_rows}
    if len(by_version) != len(source_rows):
        raise ValueError("Duplicate Epoch FrontierMath model version")
    missing = EXACT_CONFIG_MODEL_KEYS.keys() - by_version.keys()
    if missing:
        raise ValueError(f"Missing mapped Epoch FrontierMath versions: {sorted(missing)}")

    source = {
        "id": SOURCE_ID,
        "label": "Epoch AI FrontierMath Tier 4 v2 benchmark export",
        "url": SOURCE_URL,
        "category": "Benchmark owner leaderboard",
        "collectionStatus": "pinned-official-export; downloaded 2026-09-23",
        "note": (
            "Tier 4 v2, released 2026-06-12 after the corrected problem set. "
            "Scores are the export's Best score (across scorers) column. "
            "Epoch AI co-developed FrontierMath with OpenAI; OpenAI commissioned "
            "the problems and had access to many problems and solutions. "
            "Vendor-reported results are stored under a separate benchmark ID."
        ),
        "snapshotFile": str(SNAPSHOT_PATH.relative_to(SNAPSHOT_PATH.parents[2])).replace("\\", "/"),
        "snapshotSha256": SNAPSHOT_SHA256,
        "downloadPageUrl": DOWNLOAD_PAGE_URL,
        "snapshotRows": len(source_rows),
        "mappedRows": len(EXACT_CONFIG_MODEL_KEYS),
        "benchmarkVersion": "Tier 4 v2",
        "scoreSelection": "Best score (across scorers)",
    }

    results = []
    for epoch_version, model_key in EXACT_CONFIG_MODEL_KEYS.items():
        row = by_version[epoch_version]
        proportion = Decimal(row["Best score (across scorers)"])
        if not Decimal(0) <= proportion <= Decimal(1):
            raise ValueError(f"Invalid Epoch FrontierMath score for {epoch_version}")
        effort = epoch_version.rsplit("_", 1)[-1]
        if effort not in {"low", "medium", "high", "xhigh", "max"}:
            effort = ""
        results.append(
            {
                "benchmarkId": BENCHMARK_ID,
                "benchmarkLabel": BENCHMARK_LABEL,
                "model": model_key,
                "modelAliases": [model_key],
                "value": float(proportion * 100),
                "unit": "%",
                "sourceId": SOURCE_ID,
                "sourceUrl": SOURCE_URL,
                "sourceLabel": source["label"],
                "variantScoped": True,
                "modelScoreEligible": True,
                "evidenceEligible": True,
                "configurationConfidence": "explicit",
                "configurationNote": (
                    f"Epoch model version {epoch_version}; run {row['id']}; "
                    f"started {row['Started at']}."
                ),
                "effort": effort,
                "scoreOrigin": "epoch-ai-published-run",
                "scoreSelection": "Best score (across scorers)",
            }
        )
    return source, results
