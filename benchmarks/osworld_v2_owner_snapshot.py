"""Pinned OSWorld 2.0 owner-run results under one task and tool protocol.

The official leaderboard mixes task releases, dataset scopes, step budgets,
and standard versus batched tool settings. Only the original full 108-task
release at 500 steps with standard tools is eligible here. Its binary task
completion score is separate from partial reward and from OSWorld 1.x.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = ROOT / "data/benchmarks/osworld_v2_owner_2026-09-25.json"
SNAPSHOT_SHA256 = "99fdf3d27a9273b99584e00f8615e26123f5264e1c4b282e427da864aa7f27c8"
SOURCE_URL = "https://osworld-v2.xlang.ai/"
DATA_URL = (
    "https://osworld-v2.xlang.ai/static/data/leaderboard/"
    "official-results.json?v=leaderboard-v21-v1"
)
SOURCE_ID = "osworld-v2-owner-v2026-06-24-standard-2026-09-25"
BENCHMARK_ID = "osworld-v2-v2026-06-24-standard-500"
BENCHMARK_LABEL = "OSWorld 2.0 (v2026.06.24, Standard, 500 steps)"
TASK_VERSION = "v2026.06.24"
DATASET_SCOPE = "full"
STEP_BUDGET = 500
TOOL_SETTING = "standard"
TASK_COUNT = 108


# The leaderboard's exact (model, reasoning) names. The site configurations
# below are default representatives with both agentic Core scores observed.
# Other task releases, batched-tool runs, and unspecified efforts are excluded.
EXACT_CONFIG_MODEL_KEYS = {
    ("Claude Opus 4.8", "max"): "Claude Opus 4.8 (max) [R]",
    ("Claude Opus 4.7", "max"): "Claude Opus 4.7 (max) [R]",
    ("Claude Sonnet 4.6", "max"): "Claude Sonnet 4.6 (max) [R]",
    ("Qwen 3.7-Plus", "thinking"): "Qwen3.7 Plus [R]",
    ("MiniMax M3", "enabled"): "MiniMax-M3 [R]",
    ("Kimi 2.6", "enabled"): "Kimi K2.6 [R]",
}


def _row_version(row: dict[str, Any], payload: dict[str, Any]) -> str | None:
    """Mirror the official leaderboard's version fallback for older rows."""

    return (
        row.get("releaseVersion")
        or row.get("taskVersion")
        or payload.get("defaultResultReleaseVersion")
        or payload.get("taskVersion")
    )


def _selected_rows(payload: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    if payload.get("benchmarkVersion") != "OSWorld 2.0":
        raise ValueError("OSWorld benchmark version changed")
    if payload.get("taskVersion") != TASK_VERSION:
        raise ValueError("OSWorld default task version changed")
    if payload.get("defaultResultReleaseVersion") != TASK_VERSION:
        raise ValueError("OSWorld old-row version fallback changed")
    if payload.get("defaultResultDatasetScope") != DATASET_SCOPE:
        raise ValueError("OSWorld old-row dataset fallback changed")
    if payload.get("datasetSize") != TASK_COUNT:
        raise ValueError("OSWorld task count changed")
    rows = payload.get("results")
    if not isinstance(rows, list) or not rows:
        raise ValueError("OSWorld leaderboard has no results")

    selected: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("OSWorld result is not an object")
        version = _row_version(row, payload)
        scope = row.get("datasetScope") or row.get("scope") or payload["defaultResultDatasetScope"]
        if (version != TASK_VERSION or scope != DATASET_SCOPE
                or row.get("stepBudget") != STEP_BUDGET
                or row.get("toolSetting") != TOOL_SETTING):
            continue
        if row.get("official") is not True:
            raise ValueError("Unofficial OSWorld result in selected protocol")
        model, reasoning = row.get("model"), row.get("reasoning")
        if not isinstance(model, str) or not isinstance(reasoning, str):
            raise ValueError("OSWorld result lacks exact model and reasoning")
        identity = model, reasoning
        if identity in selected:
            raise ValueError(f"Duplicate OSWorld model/effort in selected protocol: {identity}")
        selected[identity] = row
    missing = EXACT_CONFIG_MODEL_KEYS.keys() - selected.keys()
    if missing:
        raise ValueError(f"Missing mapped OSWorld configurations: {sorted(missing)}")
    return selected


def load_osworld_v2_owner_snapshot() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Return exact-configuration, owner-run binary completion scores."""

    raw = SNAPSHOT_PATH.read_bytes()
    actual_hash = hashlib.sha256(raw).hexdigest()
    if actual_hash != SNAPSHOT_SHA256:
        raise ValueError(f"OSWorld owner snapshot hash changed: {actual_hash}")
    payload = json.loads(raw)
    selected = _selected_rows(payload)
    if len(set(EXACT_CONFIG_MODEL_KEYS.values())) != len(EXACT_CONFIG_MODEL_KEYS):
        raise ValueError("OSWorld mapping contains duplicate site configurations")

    source = {
        "id": SOURCE_ID,
        "label": "OSWorld 2.0 official owner leaderboard",
        "url": SOURCE_URL,
        "category": "Benchmark owner leaderboard",
        "collectionStatus": "pinned-official-json; downloaded 2026-09-25",
        "note": (
            "Owner-run OSWorld 2.0, original v2026.06.24 full 108-task set, "
            "500-step standard-tool runs only. Score is binary task completion, "
            "not partial reward. The official page also lists newer task releases, "
            "offline subsets, shorter budgets, and batched-tool runs; none are "
            "merged into this result. Version-absent older rows use the page's "
            "defaultResultReleaseVersion, matching its leaderboard JavaScript."
        ),
        "dataUrl": DATA_URL,
        "snapshotFile": str(SNAPSHOT_PATH.relative_to(ROOT)).replace("\\", "/"),
        "snapshotSha256": SNAPSHOT_SHA256,
        "snapshotRows": len(payload["results"]),
        "protocolRows": len(selected),
        "mappedRows": len(EXACT_CONFIG_MODEL_KEYS),
        "snapshotUpdatedAt": payload.get("updatedAt"),
        "benchmarkVersion": payload["benchmarkVersion"],
        "taskVersion": TASK_VERSION,
        "datasetScope": DATASET_SCOPE,
        "taskCount": TASK_COUNT,
        "stepBudget": STEP_BUDGET,
        "toolSetting": TOOL_SETTING,
        "scoreSelection": "binaryAccuracy (percent)",
    }
    results = []
    for identity, model_key in EXACT_CONFIG_MODEL_KEYS.items():
        row = selected[identity]
        score = row.get("binaryAccuracy")
        if (isinstance(score, bool) or not isinstance(score, (int, float))
                or not math.isfinite(score) or not 0 <= score <= 100):
            raise ValueError(f"Invalid OSWorld binary accuracy for {identity}")
        result = {
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
            "effort": identity[1],
            "agentHarness": "OSWorld 2.0 standard tool setting",
            "systemScore": True,
            "scoreOrigin": "osworld-v2-owner-leaderboard",
            "scoreSelection": "binaryAccuracy (percent)",
            "configurationNote": (
                f"OSWorld 2.0 {TASK_VERSION}; {identity[0]} ({identity[1]}); "
                f"{DATASET_SCOPE} {TASK_COUNT} tasks; {STEP_BUDGET} steps; "
                f"{TOOL_SETTING} tools; binary task completion."
            ),
        }
        results.append(result)
    return source, results
