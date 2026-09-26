"""Pinned DeepSWE v1.1 owner runs using the common mini-swe-agent harness.

DataCurve publishes a versioned JSON leaderboard of its original 113-task
software-engineering benchmark. This module uses only exact model/effort rows
that attempted all 113 tasks under the owner's four-run mini-swe-agent setup.
Vendor-reported DeepSWE scores and differently named agent systems remain
separate observations.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = ROOT / "data/benchmarks/deepswe_v1_1_owner_2026-09-25.json"
SNAPSHOT_SHA256 = "a7c15d66288fd249c020b9931c017b92d1a3b90e480b3ff34974b752bd030019"
SOURCE_ID = "datacurve-deepswe-v1-1-owner-mini-swe-agent-2026-09-25"
SOURCE_URL = "https://deepswe.datacurve.ai/"
DATA_URL = "https://deepswe.datacurve.ai/artifacts/v1.1/leaderboard-live.json"
METHODOLOGY_URL = "https://deepswe.datacurve.ai/blog/deepswe#methodology"
BENCHMARK_ID = "deepswe-v1-1-owner-mini-swe-agent"
BENCHMARK_LABEL = "DeepSWE v1.1 (DataCurve mini-swe-agent)"
TASK_COUNT = 113
REPEATS = 4
HARNESS = "mini-swe-agent"


# Exact owner (model ID, effort) to site configuration. Ambiguous version
# aliases (for example unversioned DeepSeek V4 and Qwen3.8 Max) and site rows
# without a corresponding named effort are intentionally absent.
EXACT_CONFIG_MODEL_KEYS = {
    ("gpt-6-astra", "max"): "GPT-6 Astra (max) [R]",
    ("gpt-6-astra", "xhigh"): "GPT-6 Astra (xhigh) [R]",
    ("gpt-6-astra", "high"): "GPT-6 Astra (high) [R]",
    ("gpt-6-astra", "medium"): "GPT-6 Astra (medium) [R]",
    ("gpt-6-astra", "low"): "GPT-6 Astra (low) [R]",
    ("gemini-3-8-flash", "high"): "Gemini 3.8 Flash (high) [R]",
    ("gemini-3-8-flash", "medium"): "Gemini 3.8 Flash (medium) [R]",
    ("claude-opus-5", "max"): "Claude Opus 5 (max) [R]",
    ("claude-opus-5", "xhigh"): "Claude Opus 5 (xhigh) [R]",
    ("claude-opus-5", "high"): "Claude Opus 5 (high) [R]",
    ("claude-opus-5", "medium"): "Claude Opus 5 (medium) [R]",
    ("claude-opus-5", "low"): "Claude Opus 5 (low) [R]",
    ("gpt-5-6-sol", "max"): "GPT-5.6 Sol (max) [R]",
    ("gpt-5-6-sol", "xhigh"): "GPT-5.6 Sol (xhigh) [R]",
    ("gpt-5-6-sol", "high"): "GPT-5.6 Sol (high) [R]",
    ("gpt-5-6-sol", "medium"): "GPT-5.6 Sol (medium) [R]",
    ("gpt-5-6-sol", "low"): "GPT-5.6 Sol (low) [R]",
    ("gpt-5-6-terra", "max"): "GPT-5.6 Terra (max) [R]",
    ("gpt-5-6-terra", "xhigh"): "GPT-5.6 Terra (xhigh) [R]",
    ("gpt-5-6-terra", "high"): "GPT-5.6 Terra (high) [R]",
    ("gpt-5-6-terra", "medium"): "GPT-5.6 Terra (medium) [R]",
    ("gpt-5-6-terra", "low"): "GPT-5.6 Terra (low) [R]",
    ("glm-5-3", "max"): "GLM-5.3 (max) [R]",
    ("kimi-k3", "max"): "Kimi K3 (max) [R]",
    ("grok-4-6", "xhigh"): "Grok 4.6 (xhigh) [R]",
    ("grok-4-6", "high"): "Grok 4.6 (high) [R]",
    ("grok-4-6", "medium"): "Grok 4.6 (medium) [R]",
    ("grok-4-6", "low"): "Grok 4.6 (low) [R]",
    ("gpt-5-6-luna", "max"): "GPT-5.6 Luna (max) [R]",
    ("gpt-5-6-luna", "xhigh"): "GPT-5.6 Luna (xhigh) [R]",
    ("gpt-5-6-luna", "high"): "GPT-5.6 Luna (high) [R]",
    ("gpt-5-6-luna", "medium"): "GPT-5.6 Luna (medium) [R]",
    ("gpt-5-6-luna", "low"): "GPT-5.6 Luna (low) [R]",
    ("gpt-5-5", "xhigh"): "GPT-5.5 (xhigh) [R]",
    ("gpt-5-5", "high"): "GPT-5.5 (high) [R]",
    ("gpt-5-5", "medium"): "GPT-5.5 (medium) [R]",
    ("gpt-5-5", "low"): "GPT-5.5 (low) [R]",
    ("gemini-3-7-flash", "high"): "Gemini 3.7 Flash (high) [R]",
    ("gemini-3-7-flash", "medium"): "Gemini 3.7 Flash (medium) [R]",
    ("gemini-3-7-flash", "low"): "Gemini 3.7 Flash (low) [R]",
    ("muse-spark-1-2", "xhigh"): "Muse Spark 1.2 (xhigh) [R]",
    ("muse-spark-1-1", "xhigh"): "Muse Spark 1.1 (xhigh) [R]",
    ("claude-sonnet-5", "max"): "Claude Sonnet 5 (max) [R]",
    ("claude-sonnet-5", "xhigh"): "Claude Sonnet 5 (xhigh) [R]",
    ("claude-sonnet-5", "high"): "Claude Sonnet 5 (high) [R]",
    ("claude-sonnet-5", "medium"): "Claude Sonnet 5 (medium) [R]",
    ("claude-sonnet-5", "low"): "Claude Sonnet 5 (low) [R]",
    ("grok-4-5", "high"): "Grok 4.5 (high) [R]",
    ("glm-5-2", "max"): "GLM-5.2 (max) [R]",
    ("gpt-5-4", "xhigh"): "GPT-5.4 (xhigh) [R]",
    ("kimi-k2-7-code", None): "Kimi K2.7 Code [R]",
}


def _selected_rows(payload: dict[str, Any]) -> dict[tuple[str, str | None], dict[str, Any]]:
    if payload.get("n_tasks_in_set") != TASK_COUNT:
        raise ValueError("DeepSWE v1.1 task count changed")
    if payload.get("unit", "").split(".")[0] != "pass@1 is attempt pass rate over scored rollout attempts":
        raise ValueError("DeepSWE v1.1 score definition changed")
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("DeepSWE v1.1 leaderboard has no rows")

    selected: dict[tuple[str, str | None], dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("DeepSWE result is not an object")
        if (row.get("harness") != HARNESS or row.get("source") != "deep-swe"
                or row.get("n_tasks_attempted") != TASK_COUNT
                or row.get("n_runs") != REPEATS):
            continue
        model, effort = row.get("model"), row.get("reasoning_effort")
        if not isinstance(model, str) or (effort is not None and not isinstance(effort, str)):
            raise ValueError("DeepSWE result lacks exact model/effort identity")
        identity = model, effort
        if identity in selected:
            raise ValueError(f"Duplicate DeepSWE model/effort under common harness: {identity}")
        selected[identity] = row
    missing = EXACT_CONFIG_MODEL_KEYS.keys() - selected.keys()
    if missing:
        raise ValueError(f"Missing mapped DeepSWE configurations: {sorted(missing, key=str)}")
    return selected


def load_deepswe_v1_1_owner_snapshot() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Return exact site configurations from the pinned common-harness run."""

    raw = SNAPSHOT_PATH.read_bytes()
    actual_hash = hashlib.sha256(raw).hexdigest()
    if actual_hash != SNAPSHOT_SHA256:
        raise ValueError(f"DeepSWE owner snapshot hash changed: {actual_hash}")
    payload = json.loads(raw)
    selected = _selected_rows(payload)
    if len(set(EXACT_CONFIG_MODEL_KEYS.values())) != len(EXACT_CONFIG_MODEL_KEYS):
        raise ValueError("DeepSWE mapping contains duplicate site configurations")

    source = {
        "id": SOURCE_ID,
        "label": "DataCurve DeepSWE v1.1 official leaderboard",
        "url": SOURCE_URL,
        "category": "Benchmark owner leaderboard",
        "collectionStatus": "pinned-official-json; downloaded 2026-09-25",
        "note": (
            "Owner-run original DeepSWE v1.1 113-task corpus, mini-swe-agent on "
            "Modal, four repeats per task. Pass@1 is the proportion of scored "
            "attempts that pass; provider, verifier, and network errors are "
            "excluded from the denominator. Selected rows attempted all 113 "
            "tasks. Vendor reports and alternate harnesses are separate."
        ),
        "dataUrl": DATA_URL,
        "methodologyUrl": METHODOLOGY_URL,
        "snapshotFile": str(SNAPSHOT_PATH.relative_to(ROOT)).replace("\\", "/"),
        "snapshotSha256": SNAPSHOT_SHA256,
        "snapshotRows": len(payload["rows"]),
        "protocolRows": len(selected),
        "mappedRows": len(EXACT_CONFIG_MODEL_KEYS),
        "snapshotGeneratedAt": payload.get("generated_at"),
        "benchmarkVersion": "DeepSWE v1.1",
        "taskCount": TASK_COUNT,
        "repeats": REPEATS,
        "harness": HARNESS,
        "scoreSelection": "pass_at_1 (scored attempt pass rate)",
    }
    results = []
    for identity, model_key in EXACT_CONFIG_MODEL_KEYS.items():
        row = selected[identity]
        score = row.get("pass_at_1")
        if (isinstance(score, bool) or not isinstance(score, (int, float))
                or not math.isfinite(score) or not 0 <= score <= 1):
            raise ValueError(f"Invalid DeepSWE pass@1 for {identity}")
        if not math.isclose(score, row.get("pass_rate", -1), abs_tol=1e-12):
            raise ValueError(f"DeepSWE pass@1 and pass rate disagree for {identity}")
        attempted, passed = row.get("n_attempted"), row.get("n_passed")
        if (not isinstance(attempted, int) or isinstance(attempted, bool)
                or not isinstance(passed, int) or isinstance(passed, bool)
                or not 0 <= passed <= attempted <= TASK_COUNT * REPEATS
                or attempted == 0
                or not math.isclose(score, passed / attempted, abs_tol=1e-12)):
            raise ValueError(f"DeepSWE scored-attempt counts disagree for {identity}")
        effort_text = identity[1] if identity[1] is not None else "base configuration"
        result = {
            "benchmarkId": BENCHMARK_ID,
            "benchmarkLabel": BENCHMARK_LABEL,
            "model": model_key,
            "modelAliases": [model_key],
            "value": score * 100,
            "unit": "%",
            "sourceId": SOURCE_ID,
            "sourceUrl": SOURCE_URL,
            "sourceLabel": source["label"],
            "variantScoped": True,
            "modelScoreEligible": True,
            "evidenceEligible": True,
            "configurationConfidence": "explicit",
            "agentHarness": HARNESS,
            "systemScore": True,
            "scoreOrigin": "datacurve-owner-run",
            "scoreSelection": "pass_at_1 (scored attempt pass rate)",
            "configurationNote": (
                f"DeepSWE v1.1; owner model {identity[0]}, {effort_text}; "
                f"{HARNESS}; {TASK_COUNT} tasks, {REPEATS} repeats; "
                f"{passed}/{attempted} scored attempts passed."
            ),
        }
        if identity[1] is not None:
            result["effort"] = identity[1]
        results.append(result)
    return source, results
