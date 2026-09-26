"""Pinned, exact-configuration results from two benchmark-owner leaderboards.

ARC Prize's ARC-AGI-3 Standard harness is a different protocol from its
Provider Adapter harness.  ALE-V1 measures an agent and its harness, and its
web page can select the best variant for display.  The mappings below instead
select named individual runs from the original exports.  They are intentionally
separate from vendor-reported results and from other ALE metrics.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any


_ROOT = Path(__file__).resolve().parents[1]

ARC_SNAPSHOT_PATH = _ROOT / "data/benchmarks/arc_agi_3_owner_2026-09-25.json"
ARC_SNAPSHOT_SHA256 = "e7ef61251688748529fd984fdf33bbade176f8096f3fcaefd43eb26ca79e16f4"
ARC_BENCHMARK_ID = "arc-agi-3-standard"
ARC_BENCHMARK_LABEL = "ARC-AGI-3 (Standard harness)"
ARC_SOURCE_ID = "arc-prize-arc-agi-3-standard-2026-09-25"
ARC_SOURCE_URL = "https://arcprize.org/leaderboard"
ARC_DATA_URL = "https://arcprize.org/media/data/leaderboard/v3.json"

# ARC's model ID, rather than its display label or approximate release-date
# metadata, identifies an exact model and effort.  The provider-adapter IDs are
# never selected.  IDs without a corresponding site effort are omitted.
ARC_EXACT_CONFIG_MODEL_KEYS = {
    "anthropic-opus-4-6-max-effort": "Claude Opus 4.6 (max) [R]",
    "openai-gpt-5-5-2026-04-23-high": "GPT-5.5 (high) [R]",
    "openai-gpt-5-6-sol-low": "GPT-5.6 Sol (low) [R]",
    "openai-gpt-5-6-sol-medium": "GPT-5.6 Sol (medium) [R]",
    "openai-gpt-5-6-sol-high": "GPT-5.6 Sol (high) [R]",
    "openai-gpt-5-6-sol-xhigh": "GPT-5.6 Sol (xhigh) [R]",
    "openai-gpt-5-6-sol-max": "GPT-5.6 Sol (max) [R]",
    "openai-gpt-5-6-terra-low": "GPT-5.6 Terra (low) [R]",
    "openai-gpt-5-6-terra-medium": "GPT-5.6 Terra (medium) [R]",
    "openai-gpt-5-6-terra-high": "GPT-5.6 Terra (high) [R]",
    "openai-gpt-5-6-terra-xhigh": "GPT-5.6 Terra (xhigh) [R]",
    "openai-gpt-5-6-terra-max": "GPT-5.6 Terra (max) [R]",
    "openai-gpt-5-6-luna-low": "GPT-5.6 Luna (low) [R]",
    "openai-gpt-5-6-luna-medium": "GPT-5.6 Luna (medium) [R]",
    "openai-gpt-5-6-luna-high": "GPT-5.6 Luna (high) [R]",
    "openai-gpt-5-6-luna-xhigh": "GPT-5.6 Luna (xhigh) [R]",
    "openai-gpt-5-6-luna-max": "GPT-5.6 Luna (max) [R]",
    "xai-grok-4-5-high": "Grok 4.5 (high) [R]",
    "anthropic-claude-opus-5-high": "Claude Opus 5 (high) [R]",
    "xai-grok-4-6-xhigh": "Grok 4.6 (xhigh) [R]",
    "openai-gpt-6-astra-low": "GPT-6 Astra (low) [R]",
    "openai-gpt-6-astra-medium": "GPT-6 Astra (medium) [R]",
    "openai-gpt-6-astra-high": "GPT-6 Astra (high) [R]",
    "openai-gpt-6-astra-xhigh": "GPT-6 Astra (xhigh) [R]",
    "openai-gpt-6-astra-max": "GPT-6 Astra (max) [R]",
    "openai-gpt-6-luna-low": "GPT-6 Luna (low) [R]",
    "openai-gpt-6-luna-medium": "GPT-6 Luna (medium) [R]",
    "openai-gpt-6-luna-high": "GPT-6 Luna (high) [R]",
    "openai-gpt-6-luna-xhigh": "GPT-6 Luna (xhigh) [R]",
    "openai-gpt-6-luna-max": "GPT-6 Luna (max) [R]",
    "openai-gpt-6-luna-none": "GPT-6 Luna (Non-reasoning)",
    "google-gemini-3-8-flash-low": "Gemini 3.8 Flash (low) [R]",
    "google-gemini-3-8-flash-medium": "Gemini 3.8 Flash (medium) [R]",
    "google-gemini-3-8-flash-high": "Gemini 3.8 Flash (high) [R]",
}

ALE_SNAPSHOT_PATH = _ROOT / "data/benchmarks/agents_last_exam_v1_owner_2026-09-25.json"
ALE_SNAPSHOT_SHA256 = "6ffb1d1ce3caf37e7d372c673e6fd02f5b142e8f272cef51c3c0dde4a3f70977"
ALE_BENCHMARK_ID = "agents-last-exam-v1-overall-pass-rate"
ALE_BENCHMARK_LABEL = "Agents' Last Exam V1 (Overall Pass Rate)"
ALE_SOURCE_ID = "ale-v1-owner-overall-pass-rate-2026-09-25"
ALE_SOURCE_URL = "https://agents-last-exam.org/leaderboard"
ALE_DATA_URL = "https://agents-last-exam.org/api/demo/leaderboard"

# (API model, agent harness, explicit harness variant) -> site modelKey.
# Every selected configuration appears once.  Rows with an absent/ambiguous
# effort are omitted.  Where the same model/effort appears with two harnesses,
# the model supplier's own CLI is preferred (Kimi Code over Claude Code).
ALE_EXACT_CONFIG_MODEL_KEYS = {
    ("gpt-6-astra", "codex", "reasoning-low"): "GPT-6 Astra (low) [R]",
    ("gpt-6-astra", "codex", "reasoning-medium"): "GPT-6 Astra (medium) [R]",
    ("gpt-6-astra", "codex", "reasoning-high"): "GPT-6 Astra (high) [R]",
    ("gpt-6-astra", "codex", "reasoning-xhigh"): "GPT-6 Astra (xhigh) [R]",
    ("gpt-6-astra", "codex", "reasoning-max"): "GPT-6 Astra (max) [R]",
    ("gpt-6-sol", "codex", "reasoning-none"): "GPT-6 Sol (Non-reasoning)",
    ("gpt-6-sol", "codex", "reasoning-low"): "GPT-6 Sol (low) [R]",
    ("gpt-6-sol", "codex", "reasoning-medium"): "GPT-6 Sol (medium) [R]",
    ("gpt-6-sol", "codex", "reasoning-high"): "GPT-6 Sol (high) [R]",
    ("gpt-6-sol", "codex", "reasoning-xhigh"): "GPT-6 Sol (xhigh) [R]",
    ("gpt-6-sol", "codex", "reasoning-max"): "GPT-6 Sol (max) [R]",
    ("gpt-6-luna", "codex", "reasoning-none"): "GPT-6 Luna (Non-reasoning)",
    ("gpt-6-luna", "codex", "reasoning-low"): "GPT-6 Luna (low) [R]",
    ("gpt-6-luna", "codex", "reasoning-medium"): "GPT-6 Luna (medium) [R]",
    ("gpt-6-luna", "codex", "reasoning-high"): "GPT-6 Luna (high) [R]",
    ("gpt-6-luna", "codex", "reasoning-xhigh"): "GPT-6 Luna (xhigh) [R]",
    ("gpt-6-luna", "codex", "reasoning-max"): "GPT-6 Luna (max) [R]",
    ("claude-opus-5", "claude_code", "thinking-low"): "Claude Opus 5 (low) [R]",
    ("claude-opus-5", "claude_code", "thinking-medium"): "Claude Opus 5 (medium) [R]",
    ("claude-opus-5", "claude_code", "thinking-high"): "Claude Opus 5 (high) [R]",
    ("claude-opus-5", "claude_code", "thinking-xhigh"): "Claude Opus 5 (xhigh) [R]",
    ("claude-opus-5", "claude_code", "thinking-max"): "Claude Opus 5 (max) [R]",
    ("muse-spark-1-3", "codex", "reasoning-xhigh"): "Muse Spark 1.3 (xhigh) [R]",
    ("muse-spark-1-3", "codex", "reasoning-max"): "Muse Spark 1.3 (max) [R]",
    ("GPT-5.6-Sol", "codex", "reasoning-low"): "GPT-5.6 Sol (low) [R]",
    ("GPT-5.6-Sol", "codex", "reasoning-medium"): "GPT-5.6 Sol (medium) [R]",
    ("GPT-5.6-Sol", "codex", "reasoning-high"): "GPT-5.6 Sol (high) [R]",
    ("GPT-5.6-Sol", "codex", "reasoning-xhigh"): "GPT-5.6 Sol (xhigh) [R]",
    ("GPT-5.6-Sol", "codex", "reasoning-max"): "GPT-5.6 Sol (max) [R]",
    ("GPT-5.6-Terra", "codex", "reasoning-low"): "GPT-5.6 Terra (low) [R]",
    ("GPT-5.6-Terra", "codex", "reasoning-medium"): "GPT-5.6 Terra (medium) [R]",
    ("GPT-5.6-Terra", "codex", "reasoning-high"): "GPT-5.6 Terra (high) [R]",
    ("GPT-5.6-Terra", "codex", "reasoning-xhigh"): "GPT-5.6 Terra (xhigh) [R]",
    ("GPT-5.6-Terra", "codex", "reasoning-max"): "GPT-5.6 Terra (max) [R]",
    ("GPT-5.6-Luna", "codex", "reasoning-low"): "GPT-5.6 Luna (low) [R]",
    ("GPT-5.6-Luna", "codex", "reasoning-medium"): "GPT-5.6 Luna (medium) [R]",
    ("GPT-5.6-Luna", "codex", "reasoning-high"): "GPT-5.6 Luna (high) [R]",
    ("GPT-5.6-Luna", "codex", "reasoning-xhigh"): "GPT-5.6 Luna (xhigh) [R]",
    ("GPT-5.6-Luna", "codex", "reasoning-max"): "GPT-5.6 Luna (max) [R]",
    ("kimi-k3", "kimi_code", "thinking-max"): "Kimi K3 (max) [R]",
    ("grok-4-5", "grok_build", "reasoning-high"): "Grok 4.5 (high) [R]",
    ("gpt-5-5", "codex", "reasoning-low"): "GPT-5.5 (low) [R]",
    ("gpt-5-5", "codex", "reasoning-medium"): "GPT-5.5 (medium) [R]",
    ("gpt-5-5", "codex", "reasoning-xhigh"): "GPT-5.5 (xhigh) [R]",
    ("claude-opus-4-8", "claude_code", "thinking-max"): "Claude Opus 4.8 (max) [R]",
    ("glm-5-2", "claude_code", "max"): "GLM-5.2 (max) [R]",
}

TOOLATHLON_SNAPSHOT_PATH = _ROOT / "data/benchmarks/toolathlon_verified_owner_2026-09-25.json"
TOOLATHLON_SNAPSHOT_SHA256 = "34d23b97e6b32f8931d66a0109ae123b211369bced08f878e8f324721500ede9"
TOOLATHLON_BENCHMARK_ID = "toolathlon-verified-owner"
TOOLATHLON_BENCHMARK_LABEL = "Toolathlon-Verified (official Pass@1)"
TOOLATHLON_SOURCE_ID = "toolathlon-verified-owner-2026-09-25"
TOOLATHLON_SOURCE_URL = "https://hkust.mintlify.app/docs/leaderboard"

# These are the exact rendered model cells in the official Verified table. The
# organization icon titles and independent-evaluation badges are retained in
# the snapshot, so this mapping deliberately does not normalize model names.
# Models with a stated effort absent from the site are omitted. The owner does
# not specify effort for some base-model rows, which map only to the site's
# corresponding base configurations, never to an effort-labelled variant.
TOOLATHLON_EXACT_CONFIG_MODEL_KEYS = {
    "Kimi Kimi K3 (max) ✓": "Kimi K3 (max) [R]",
    "Claude Claude Opus 4.8 (max) ✓": "Claude Opus 4.8 (max) [R]",
    "Meta Muse Spark 1.2 (xhigh) ✓": "Muse Spark 1.2 (xhigh) [R]",
    "Meta Muse Spark 1.1 (xhigh) ✓": "Muse Spark 1.1 (xhigh) [R]",
    "DeepSeek V4 Pro 0813 (max) ✓": "DeepSeek V4 Pro 0813 (max) [R]",
    "OpenAI icon GPT-5.5 (xhigh) ✓": "GPT-5.5 (xhigh) [R]",
    "Claude Claude Sonnet 5 (max) ✓": "Claude Sonnet 5 (max) [R]",
    "DeepSeek V4 Flash 0731 (max) ✓": "DeepSeek V4 Flash 0731 (max) [R]",
    "Z.ai GLM 5.2 (max) ✓": "GLM-5.2 (max) [R]",
    "Kimi Kimi K2.6 ✓": "Kimi K2.6 [R]",
    "Kimi Kimi K2.7 Code ✓": "Kimi K2.7 Code [R]",
    "MiMo V2.5 ✓": "MiMo-V2.5 [R]",
    "MiniMax M2.7 ✓": "MiniMax-M2.7 [R]",
    "DeepSeek DeepSeek V4 Pro (max) ✓": "DeepSeek V4 Pro (max) [R]",
    "DeepSeek DeepSeek V4 Flash (max) ✓": "DeepSeek V4 Flash (max) [R]",
    "Qwen3.5 397B-A17B ✓": "Qwen3.5 397B A17B [R]",
    "NVIDIA Nemotron 3 Ultra ✓": "Nemotron 3 Ultra [R]",
}


def _load_pinned_json(path: Path, expected_hash: str) -> Any:
    raw = path.read_bytes()
    actual_hash = hashlib.sha256(raw).hexdigest()
    if actual_hash != expected_hash:
        raise ValueError(f"Benchmark owner snapshot hash changed: {path.name}: {actual_hash}")
    return json.loads(raw)


def _percent(proportion: Any, source_key: str) -> float:
    if not isinstance(proportion, (int, float)) or isinstance(proportion, bool):
        raise ValueError(f"Invalid score for {source_key}")
    if not math.isfinite(proportion) or not 0 <= proportion <= 1:
        raise ValueError(f"Score outside [0, 1] for {source_key}")
    return proportion * 100


def _base_result(benchmark_id: str, benchmark_label: str, source: dict[str, Any],
                 model_key: str, value: float) -> dict[str, Any]:
    return {
        "benchmarkId": benchmark_id,
        "benchmarkLabel": benchmark_label,
        "model": model_key,
        "modelAliases": [model_key],
        "value": value,
        "unit": "%",
        "sourceId": source["id"],
        "sourceUrl": source["url"],
        "sourceLabel": source["label"],
        "variantScoped": True,
        "modelScoreEligible": True,
        "evidenceEligible": True,
        "configurationConfidence": "explicit",
    }


def load_arc_agi_3_standard_snapshot() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Return ARC Prize's named Standard-harness model/effort observations."""

    payload = _load_pinned_json(ARC_SNAPSHOT_PATH, ARC_SNAPSHOT_SHA256)
    if payload.get("version") != "v3" or not isinstance(payload.get("evaluations"), list):
        raise ValueError("ARC Prize v3 leaderboard snapshot schema changed")
    rows = [row for row in payload["evaluations"] if row.get("datasetId") == "v3_Semi_Private"]
    by_id = {row["modelId"]: row for row in rows}
    if len(by_id) != len(rows):
        raise ValueError("Duplicate ARC Prize ARC-AGI-3 model ID")
    missing = ARC_EXACT_CONFIG_MODEL_KEYS.keys() - by_id.keys()
    if missing:
        raise ValueError(f"Missing mapped ARC Prize model IDs: {sorted(missing)}")
    if len(set(ARC_EXACT_CONFIG_MODEL_KEYS.values())) != len(ARC_EXACT_CONFIG_MODEL_KEYS):
        raise ValueError("ARC Prize mapping contains duplicate site models")
    source = {
        "id": ARC_SOURCE_ID,
        "label": "ARC Prize ARC-AGI-3 official leaderboard",
        "url": ARC_SOURCE_URL,
        "category": "Benchmark owner leaderboard",
        "collectionStatus": "pinned-official-export; downloaded 2026-09-25",
        "note": (
            "ARC-AGI-3 semi-private evaluations on the Standard harness, which carries "
            "model-selected notes through the environment. Provider Adapter runs preserve "
            "reasoning state and compact longer conversations, and are excluded here. "
            "Scores are the export's score field (fraction converted to percent)."
        ),
        "dataUrl": ARC_DATA_URL,
        "snapshotFile": str(ARC_SNAPSHOT_PATH.relative_to(_ROOT)).replace("\\", "/"),
        "snapshotSha256": ARC_SNAPSHOT_SHA256,
        "snapshotGeneratedAt": payload.get("generatedAt"),
        "snapshotRows": len(rows),
        "mappedRows": len(ARC_EXACT_CONFIG_MODEL_KEYS),
        "benchmarkVersion": "ARC-AGI-3 semi-private",
        "harness": "Standard",
        "scoreSelection": "Named model and effort; score",
    }
    results = []
    for arc_id, model_key in ARC_EXACT_CONFIG_MODEL_KEYS.items():
        if "provider-adapter" in arc_id:
            raise ValueError(f"Provider Adapter cannot enter Standard metric: {arc_id}")
        row = by_id[arc_id]
        result = _base_result(
            ARC_BENCHMARK_ID, ARC_BENCHMARK_LABEL, source, model_key,
            _percent(row["score"], arc_id),
        )
        effort = (
            "max" if arc_id.endswith("-max-effort")
            else "none" if arc_id.endswith("-none")
            else arc_id.rsplit("-", 1)[-1]
        )
        if effort not in {"none", "low", "medium", "high", "xhigh", "max"}:
            raise ValueError(f"Unrecognized ARC Prize effort: {arc_id}")
        result.update({
            "configurationNote": (
                f"ARC Prize model ID {arc_id}; {row['modelDisplayName']}; "
                "ARC-AGI-3 semi-private; Standard harness."
            ),
            "effort": effort,
            "harness": "Standard",
            "scoreOrigin": "arc-prize-official-leaderboard",
            "scoreSelection": "Named model and effort; score",
        })
        results.append(result)
    return source, results


def load_ale_v1_overall_pass_rate_snapshot() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Return named ALE-V1 full-set Overall Pass Rate agent/harness runs."""

    payload = _load_pinned_json(ALE_SNAPSHOT_PATH, ALE_SNAPSHOT_SHA256)
    if not isinstance(payload.get("rows"), list):
        raise ValueError("ALE-V1 leaderboard snapshot schema changed")
    rows = [row for row in payload["rows"] if row.get("split") == "full/overall"]
    by_key = {(row["model"], row["harness"], row.get("harnessVariant")): row for row in rows}
    if len(by_key) != len(rows):
        raise ValueError("Duplicate ALE-V1 full/overall model/harness/variant")
    missing = ALE_EXACT_CONFIG_MODEL_KEYS.keys() - by_key.keys()
    if missing:
        raise ValueError(f"Missing mapped ALE-V1 configurations: {sorted(missing)}")
    if len(set(ALE_EXACT_CONFIG_MODEL_KEYS.values())) != len(ALE_EXACT_CONFIG_MODEL_KEYS):
        raise ValueError("ALE-V1 mapping contains duplicate site models")
    source = {
        "id": ALE_SOURCE_ID,
        "label": "UC Berkeley Agents' Last Exam V1 official leaderboard",
        "url": ALE_SOURCE_URL,
        "category": "Benchmark owner leaderboard",
        "collectionStatus": "pinned-official-api; downloaded 2026-09-25",
        "note": (
            "ALE-V1 full/overall Pass Rate over 152 benchmark tasks. Individual API rows "
            "fix the model, agent harness, and explicit thinking/reasoning variant; "
            "a supplier CLI is preferred when the same model and effort has another "
            "harness row. The website's best-variant display is not used. A result measures the "
            "model plus its named agent harness. Source passRate fractions are converted "
            "to percent; incomplete or repeated runs retain the owner's denominator."
        ),
        "dataUrl": ALE_DATA_URL,
        "snapshotFile": str(ALE_SNAPSHOT_PATH.relative_to(_ROOT)).replace("\\", "/"),
        "snapshotSha256": ALE_SNAPSHOT_SHA256,
        "snapshotRows": len(payload["rows"]),
        "fullOverallRows": len(rows),
        "mappedRows": len(ALE_EXACT_CONFIG_MODEL_KEYS),
        "benchmarkVersion": "ALE-V1",
        "scoreSelection": "full/overall; named model, harness, and effort; passRate",
    }
    results = []
    for key, model_key in ALE_EXACT_CONFIG_MODEL_KEYS.items():
        model_id, harness, variant = key
        row = by_key[key]
        if row["splitTasks"] != 152:
            raise ValueError(f"Unexpected ALE-V1 full task count for {key}")
        result = _base_result(
            ALE_BENCHMARK_ID, ALE_BENCHMARK_LABEL, source, model_key,
            _percent(row["passRate"], str(key)),
        )
        effort = variant.rsplit("-", 1)[-1]
        if effort not in {"none", "low", "medium", "high", "xhigh", "max"}:
            raise ValueError(f"Unrecognized ALE-V1 effort: {key}")
        result.update({
            "configurationNote": (
                f"ALE-V1 API model {model_id}; harness {harness}; variant {variant}; "
                f"full/overall; {row['runs']} runs covering {row['tasks']} of "
                f"{row['splitTasks']} tasks."
            ),
            "effort": effort,
            "harness": harness,
            "harnessVariant": variant,
            "scoreOrigin": "ale-v1-official-leaderboard",
            "scoreSelection": "full/overall; passRate",
        })
        results.append(result)
    return source, results


def load_toolathlon_verified_owner_snapshot() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Return independently evaluated Toolathlon-Verified Pass@1 rows."""

    payload = _load_pinned_json(TOOLATHLON_SNAPSHOT_PATH, TOOLATHLON_SNAPSHOT_SHA256)
    if payload.get("schemaVersion") != 1 or payload.get("sourceUrl") != TOOLATHLON_SOURCE_URL:
        raise ValueError("Toolathlon-Verified owner snapshot schema or source changed")
    expected_headers = [
        "Model", "Type", "Agent", "Date", "Pass@1", "Pass@3",
        "Pass^3", "# Turns", "# Tool Calls",
    ]
    if payload.get("headers") != expected_headers or not isinstance(payload.get("rows"), list):
        raise ValueError("Toolathlon-Verified owner snapshot table changed")
    rows = payload["rows"]
    if len(rows) != 25 or any(not isinstance(row, dict) for row in rows):
        raise ValueError("Toolathlon-Verified owner snapshot row count changed")
    if any(set(row) != set(expected_headers) for row in rows):
        raise ValueError("Toolathlon-Verified owner snapshot columns changed")
    by_name = {row["Model"]: row for row in rows}
    if len(by_name) != len(rows):
        raise ValueError("Duplicate Toolathlon-Verified owner model cell")
    missing = TOOLATHLON_EXACT_CONFIG_MODEL_KEYS.keys() - by_name.keys()
    if missing:
        raise ValueError(f"Missing mapped Toolathlon-Verified models: {sorted(missing)}")
    if len(set(TOOLATHLON_EXACT_CONFIG_MODEL_KEYS.values())) != len(TOOLATHLON_EXACT_CONFIG_MODEL_KEYS):
        raise ValueError("Toolathlon-Verified owner mapping contains duplicate site models")
    source = {
        "id": TOOLATHLON_SOURCE_ID,
        "label": "HKUST Toolathlon-Verified official leaderboard",
        "url": TOOLATHLON_SOURCE_URL,
        "category": "Benchmark owner leaderboard",
        "collectionStatus": "pinned-official-page; downloaded 2026-09-25",
        "note": (
            "Official Toolathlon-Verified series released June 30, 2026: 108 tasks, "
            "independent evaluations, Default agent. This series is not comparable "
            "with pre-Verified Toolathlon. The mapped score is the table's Pass@1 "
            "point estimate in percent, excluding its displayed uncertainty, not "
            "Pass@3 or Pass^3. Named effort is matched exactly; unqualified base "
            "models map only to corresponding unqualified site configurations."
        ),
        "snapshotFile": str(TOOLATHLON_SNAPSHOT_PATH.relative_to(_ROOT)).replace("\\", "/"),
        "snapshotSha256": TOOLATHLON_SNAPSHOT_SHA256,
        "sourcePageSha256": payload["pageSha256"],
        "snapshotCapturedAt": payload["capturedAt"],
        "snapshotRows": len(rows),
        "mappedRows": len(TOOLATHLON_EXACT_CONFIG_MODEL_KEYS),
        "benchmarkVersion": "Toolathlon-Verified (108 tasks)",
        "harness": "Default agent",
        "scoreSelection": "Independently evaluated Default agent; Pass@1 point estimate",
    }
    results = []
    for owner_model, model_key in TOOLATHLON_EXACT_CONFIG_MODEL_KEYS.items():
        row = by_name[owner_model]
        if row["Agent"] != "Default" or not owner_model.endswith(" ✓"):
            raise ValueError(f"Toolathlon-Verified row is not a Default independent evaluation: {owner_model}")
        score_match = re.fullmatch(r"(\d+(?:\.\d+)?) ± (\d+(?:\.\d+)?)", row["Pass@1"])
        if not score_match:
            raise ValueError(f"Invalid Toolathlon-Verified Pass@1 cell: {owner_model}")
        score, uncertainty = map(float, score_match.groups())
        if not math.isfinite(score) or not 0 <= score <= 100 or not 0 <= uncertainty <= 100:
            raise ValueError(f"Toolathlon-Verified Pass@1 outside [0, 100]: {owner_model}")
        result = _base_result(TOOLATHLON_BENCHMARK_ID, TOOLATHLON_BENCHMARK_LABEL,
                              source, model_key, score)
        result.update({
            "configurationNote": (
                f"Owner table model {owner_model}; Agent {row['Agent']}; evaluated "
                f"{row['Date']}; Pass@1 {row['Pass@1']}."
            ),
            "harness": "Default agent",
            "passAt1Uncertainty": uncertainty,
            "scoreOrigin": "toolathlon-verified-official-leaderboard",
            "scoreSelection": "Pass@1 point estimate",
        })
        effort_match = re.search(r"\((low|medium|high|xhigh|max)\) ✓$", owner_model)
        if effort_match:
            effort = effort_match.group(1)
            if f"({effort})" not in model_key:
                raise ValueError(f"Toolathlon-Verified effort mismatch: {owner_model} -> {model_key}")
            result["effort"] = effort
        else:
            if "(" in model_key:
                raise ValueError(f"Unqualified Toolathlon-Verified model mapped to effort: {owner_model}")
            result["configurationConfidence"] = "model-card-default"
        results.append(result)
    return source, results
