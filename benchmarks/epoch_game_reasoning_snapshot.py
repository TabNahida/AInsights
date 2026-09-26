"""Pinned Epoch AI run-level results for two difficult game-reasoning tests.

The public export is filtered to the reviewed Chess Puzzles and Mystery Game
Puzzles task versions. Exact Epoch model versions reuse and extend the
FrontierMath mapping, while each task's run set and score definition are
checked separately.
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

try:
    from .epoch_frontiermath_snapshot import EXACT_CONFIG_MODEL_KEYS
except ImportError:  # Direct collector script execution.
    from epoch_frontiermath_snapshot import EXACT_CONFIG_MODEL_KEYS


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = ROOT / "data/benchmarks/epoch_game_reasoning_2026-09-25.json"
SNAPSHOT_SHA256 = "c5e8df2171882b23050390101d51fc4df315541e30f910f8267dfacff12f92a1"
EXPORT_URL = "https://epoch.ai/data/benchmarks.csv"

SPECS = (
    {
        "task": "Chess Puzzles",
        "version": "1.1.6",
        "rows": 186,
        "mapped": 120,
        "id": "epoch-chess-puzzles-v1-1-6",
        "label": "Chess Puzzles v1.1.6 (Epoch run)",
        "url": "https://epoch.ai/benchmarks/chess-puzzles",
        "protocol": "100 generated, unpublished FEN chess positions; unique best next move",
    },
    {
        "task": "Mystery Game Puzzles",
        "version": "1.0.4",
        "rows": 129,
        "mapped": 68,
        "id": "epoch-mystery-game-puzzles-v1-0-4",
        "label": "Mystery Game Puzzles v1.0.4 (Epoch run)",
        "url": "https://epoch.ai/benchmarks/mystery-game-puzzles",
        "protocol": "100 hidden-identity game positions; text state, minimal agent scaffold, unique best next move",
    },
)

# Chess and Mystery have many more published configurations than FrontierMath.
# Match the exact Epoch model/checkpoint/effort to a site configuration here;
# keep entries with uncertain fallback, effort, or release dates excluded.
GAME_EXACT_MODEL_KEYS = {
    **EXACT_CONFIG_MODEL_KEYS,
    "gpt-5.6-sol_none": "GPT-5.6 Sol (Non-reasoning)",
    "gpt-5.6-sol_low": "GPT-5.6 Sol (low) [R]",
    "gpt-5.6-sol_medium": "GPT-5.6 Sol (medium) [R]",
    "gpt-5.6-terra_none": "GPT-5.6 Terra (Non-reasoning)",
    "gpt-5.6-terra_low": "GPT-5.6 Terra (low) [R]",
    "gpt-5.6-terra_medium": "GPT-5.6 Terra (medium) [R]",
    "gpt-5.6-luna_none": "GPT-5.6 Luna (Non-reasoning)",
    "gpt-5.6-luna_low": "GPT-5.6 Luna (low) [R]",
    "gpt-5.6-luna_medium": "GPT-5.6 Luna (medium) [R]",
    "gpt-5.5_none": "GPT-5.5 (Non-reasoning)",
    "gpt-5.5_low": "GPT-5.5 (low) [R]",
    "gpt-5.5_medium": "GPT-5.5 (medium) [R]",
    "gpt-5.5_high": "GPT-5.5 (high) [R]",
    "gpt-5.4-2026-03-05_none": "GPT-5.4 (Non-reasoning)",
    "gpt-5.4-2026-03-05_low": "GPT-5.4 (low) [R]",
    "gpt-5.4-mini-2026-03-17_none": "GPT-5.4 mini (Non-reasoning)",
    "gpt-5.4-mini-2026-03-17_medium": "GPT-5.4 mini (medium) [R]",
    "gpt-5.4-nano-2026-03-17_none": "GPT-5.4 nano (Non-reasoning)",
    "gpt-5.2-2025-12-11_none": "GPT-5.2 (Non-reasoning)",
    "gpt-5.2-2025-12-11_medium": "GPT-5.2 (medium) [R]",
    "gpt-5.1-2025-11-13_none": "GPT-5.1 (Non-reasoning)",
    "gpt-5.1-2025-11-13_high": "GPT-5.1 (high) [R]",
    "gpt-5-2025-08-07_minimal": "GPT-5 (minimal)",
    "gpt-5-2025-08-07_low": "GPT-5 (low) [R]",
    "gpt-5-2025-08-07_medium": "GPT-5 (medium) [R]",
    "gpt-5-mini-2025-08-07_minimal": "GPT-5 mini (minimal)",
    "gpt-5-mini-2025-08-07_medium": "GPT-5 mini (medium) [R]",
    "gpt-5-nano-2025-08-07_minimal": "GPT-5 nano (minimal)",
    "gpt-5-nano-2025-08-07_medium": "GPT-5 nano (medium) [R]",
    "gpt-oss-20b_low": "gpt-oss-20b (low) [R]",
    "gpt-oss-20b_high": "gpt-oss-20b (high) [R]",
    "gpt-oss-120b_high": "gpt-oss-120b (high) [R]",
    "kimi-k3_low": "Kimi K3 (low) [R]",
    "kimi-k2.6_none": "Kimi K2.6 (Non-reasoning)",
    "claude-opus-5_low": "Claude Opus 5 (low) [R]",
    "claude-sonnet-5_xhigh": "Claude Sonnet 5 (xhigh) [R]",
    "claude-sonnet-4-6_max": "Claude Sonnet 4.6 (max) [R]",
    "grok-4.6_high": "Grok 4.6 (high) [R]",
    "deepseek-v4-pro_none": "DeepSeek V4 Pro (Non-reasoning)",
    "deepseek-v4-pro_high": "DeepSeek V4 Pro (high) [R]",
    "qwen3.7-plus": "Qwen3.7 Plus [R]",
    "qwen3.6-plus": "Qwen3.6 Plus [R]",
    "qwen3.6-max-preview": "Qwen3.6 Max Preview [R]",
    "qwen3.6-27b": "Qwen3.6 27B [R]",
    "qwen3.6-27b_none": "Qwen3.6 27B (Non-reasoning)",
    "qwen3.6-35b-a3b": "Qwen3.6 35B A3B [R]",
    "qwen3.6-35b-a3b_none": "Qwen3.6 35B A3B (Non-reasoning)",
    "qwen3.5-397b-a17b": "Qwen3.5 397B A17B [R]",
    "qwen3.5-397b-a17b_none": "Qwen3.5 397B A17B (Non-reasoning)",
    "qwen3.5-122b-a10b_none": "Qwen3.5 122B A10B (Non-reasoning)",
    "qwen3.5-35b-a3b": "Qwen3.5 35B A3B [R]",
    "qwen3.5-35b-a3b_none": "Qwen3.5 35B A3B (Non-reasoning)",
    "qwen3.5-9B": "Qwen3.5 9B [R]",
    "qwen3.5-9B_none": "Qwen3.5 9B (Non-reasoning)",
    "qwen3.5-2b_none": "Qwen3.5 2B (Non-reasoning)",
    "qwen3-4b_none": "Qwen3 4B (Non-reasoning)",
    "qwen3-8b": "Qwen3 8B [R]",
    "qwen3-8b_none": "Qwen3 8B (Non-reasoning)",
    "qwen3-14b": "Qwen3 14B [R]",
    "qwen3-14b_none": "Qwen3 14B (Non-reasoning)",
    "Qwen3-32B": "Qwen3 32B [R]",
    "Qwen3-32B_none": "Qwen3 32B (Non-reasoning)",
    "Qwen3-30B-A3B": "Qwen3 30B [R]",
    "Qwen3-30B-A3B_none": "Qwen3 30B (Non-reasoning)",
    "qwen3-30b-a3b-thinking-2507": "Qwen3 30B A3B 2507 [R]",
    "qwen3-30b-a3b-instruct-2507": "Qwen3 30B A3B 2507 (Non-reasoning)",
    "qwen3-4b-instruct-2507": "Qwen3 4B 2507 (Non-reasoning)",
    "Qwen3-235B-A22B-Thinking-2507": "Qwen3 235B A22B 2507 [R]",
    "MiniMax-M3": "MiniMax-M3 [R]",
    "glm-5.1": "GLM-5.1 [R]",
    "glm-5.2_none": "GLM-5.2 (Non-reasoning)",
    "gemini-3.5-flash_minimal": "Gemini 3.5 Flash (minimal)",
    "gpt-4o-2024-08-06": "GPT-4o (Aug)",
    "gpt-4o-mini-2024-07-18": "GPT-4o mini",
    "gpt-4.1-2025-04-14": "GPT-4.1",
    "gpt-4.1-mini-2025-04-14": "GPT-4.1 mini",
    "claude-opus-4-1-20250805": "Claude 4.1 Opus [R]",
    "claude-sonnet-4-5-20250929": "Claude 4.5 Sonnet [R]",
    "claude-opus-4-5-20251101": "Claude Opus 4.5 [R]",
    "claude-3-opus-20240229": "Claude 3 Opus",
    "DeepSeek-R1-Distill-Qwen-1.5B": "DeepSeek R1 Distill Qwen 1.5B [R]",
    "DeepSeek-R1-Distill-Qwen-14B": "DeepSeek R1 Distill Qwen 14B [R]",
    "DeepSeek-R1-Distill-Qwen-32B": "DeepSeek R1 Distill Qwen 32B [R]",
    "deepseek-r1-0528-qwen3-8b": "DeepSeek R1 0528 Qwen3 8B [R]",
    "deepseek-llm-67b-chat": "DeepSeek LLM 67B (V1)",
    "glm-4.7-flash": "GLM-4.7-Flash [R]",
    "glm-4.7-flash_none": "GLM-4.7-Flash (Non-reasoning)",
    "granite-4.0-1b": "Granite 4.0 1B",
    "granite-4.0-350m": "Granite 4.0 350M",
    "granite-4.0-micro": "Granite 4.0 Micro",
    "gemma-3-1b-it": "Gemma 3 1B",
    "gemma-3-4b-it": "Gemma 3 4B",
    "gemma-3-12b-it": "Gemma 3 12B",
    "gemma-3-27b-it": "Gemma 3 27B",
    "Llama-3.1-8B-Instruct": "Llama 3.1 8B",
    "Llama-3.2-1B-Instruct": "Llama 3.2 1B",
    "Meta-Llama-3-8B-Instruct": "Llama 3 8B",
    "llama-2-7b-chat": "Llama 2 Chat 7B",
    "Llama-2-13b-chat": "Llama 2 Chat 13B",
    "mistral-small-3-2501": "Mistral Small 3",
    "mistral-small-3.1-2503": "Mistral Small 3.1",
    "mistral-small-3.2-2506": "Mistral Small 3.2",
    "nemotron-3-ultra": "Nemotron 3 Ultra [R]",
    "Phi-3-mini-4k-instruct": "Phi-3 Mini",
    "phi-4": "Phi-4",
    "QwQ-32B": "QwQ-32B [R]",
    "qwen2.5-32b-instruct": "Qwen2.5 Instruct 32B",
    "qwen3-1.7b_none": "Qwen3 1.7B (Non-reasoning)",
    "qwen3-max-2025-09-23": "Qwen3 Max",
    "seed-oss-36b-instruct": "Seed-OSS-36B-Instruct [R]",
}

# The Epoch page's 2026-09-22 v4 note identifies GPT-5.6 Sol and Opus 5 as
# retested under Card ban, GPT-6 Astra's published result as Card ban, and all
# later models (including GPT-6 Sol) as Card ban. Older single-agent runs are
# excluded even though the export leaves their per-row task version blank.
EBR_CARD_BAN_RUNS = {
    "GhVYxWxttDxZ7akiJQPYsE": ("gpt-6-astra_max", "GPT-6 Astra (max) [R]"),
    "gM5SADcEixdr2P6PkseLeF": ("gpt-6-sol_max", "GPT-6 Sol (max) [R]"),
    "mtHToEb2uzbaekANakjkJZ": ("claude-opus-5_max", "Claude Opus 5 (max) [R]"),
    "SjeXjsdda4NKRBTrPiJVM8": ("gpt-5.6-sol_max", "GPT-5.6 Sol (max) [R]"),
}
EBR_BENCHMARK_ID = "epoch-ebr-bench-card-ban-v4"
EBR_BENCHMARK_LABEL = "EBR-bench v4 Card-ban (Epoch single-agent)"


def _score(row: dict[str, str]) -> float:
    try:
        score = Decimal(row["mean_score"])
        best = Decimal(row["Best score (across scorers)"])
    except (InvalidOperation, KeyError) as exc:
        raise ValueError(f"Epoch game score is not numeric: {row.get('id_runs')}") from exc
    if not Decimal(0) <= score <= Decimal(1) or score != best:
        raise ValueError(f"Epoch game score changed or conflicts across scorers: {row['id_runs']}")
    return float(score * 100)


def load_epoch_game_reasoning_snapshots() -> tuple[tuple[dict[str, Any], list[dict[str, Any]]], ...]:
    raw = SNAPSHOT_PATH.read_bytes()
    actual_hash = hashlib.sha256(raw).hexdigest()
    if actual_hash != SNAPSHOT_SHA256:
        raise ValueError(f"Epoch game-reasoning snapshot hash changed: {actual_hash}")
    payload = json.loads(raw)
    if payload.get("schemaVersion") != 1 or payload.get("sourceUrl") != EXPORT_URL:
        raise ValueError("Epoch game-reasoning snapshot metadata changed")
    if not isinstance(payload.get("rows"), list):
        raise ValueError("Epoch game-reasoning snapshot has no rows")

    pairs = []
    for spec in SPECS:
        task_rows = [row for row in payload["rows"]
                     if row["task"] == spec["task"] and row["task version"] == spec["version"]]
        if len(task_rows) != spec["rows"]:
            raise ValueError(f"Epoch {spec['task']} reviewed run count changed")
        if any(row["Status"] != "Success" for row in task_rows):
            raise ValueError(f"Epoch {spec['task']} contains a non-success run")
        by_model = {row["model"]: row for row in task_rows}
        ids = [row["id_runs"] for row in task_rows]
        if len(by_model) != len(task_rows) or len(set(ids)) != len(ids):
            raise ValueError(f"Epoch {spec['task']} has duplicate model or run ID")
        mapped = [(epoch_version, GAME_EXACT_MODEL_KEYS[epoch_version], row)
                  for epoch_version, row in by_model.items()
                  if epoch_version in GAME_EXACT_MODEL_KEYS]
        if len(mapped) != spec["mapped"] or len({key for _, key, _ in mapped}) != len(mapped):
            raise ValueError(f"Epoch {spec['task']} exact model mapping changed")

        source_id = f"{spec['id']}-owner-2026-09-25"
        source = {
            "id": source_id,
            "label": f"Epoch AI {spec['task']} benchmark export",
            "url": spec["url"],
            "category": "Benchmark owner leaderboard",
            "collectionStatus": "pinned-official-export; downloaded 2026-09-25",
            "note": (
                f"{spec['protocol']}. Only Success runs on task version {spec['version']} "
                "with exact model/configuration matches are scored. Chess and "
                "Mystery both test one-step game reasoning, so their signals may "
                "be correlated."
            ),
            "dataUrl": EXPORT_URL,
            "snapshotFile": str(SNAPSHOT_PATH.relative_to(ROOT)).replace("\\", "/"),
            "snapshotSha256": SNAPSHOT_SHA256,
            "rawExportSha256": payload["rawExportSha256"],
            "snapshotRows": len(task_rows),
            "mappedRows": len(mapped),
            "taskVersion": spec["version"],
            "scoreSelection": "mean_score (percent); equals Best score (across scorers)",
            "resultProtocol": spec["protocol"],
        }
        results = []
        for epoch_version, site_key, row in mapped:
            effort = epoch_version.rsplit("_", 1)[-1]
            result = {
                "benchmarkId": spec["id"],
                "benchmarkLabel": spec["label"],
                "model": site_key,
                "modelAliases": [site_key],
                "value": _score(row),
                "unit": "%",
                "sourceId": source_id,
                "sourceUrl": spec["url"],
                "sourceLabel": source["label"],
                "variantScoped": True,
                "modelScoreEligible": True,
                "evidenceEligible": True,
                "configurationConfidence": "explicit",
                "scoreOrigin": "epoch-ai-published-run",
                "scoreSelection": "mean_score",
                "configurationNote": (
                    f"Epoch model version {epoch_version}; {spec['task']} {spec['version']}; "
                    f"run {row['id_runs']}; started {row['started_at']}."
                ),
            }
            if effort in {"low", "medium", "high", "xhigh", "max"}:
                result["effort"] = effort
            results.append(result)
        pairs.append((source, results))
    return tuple(pairs)


def load_epoch_ebr_card_ban_snapshot() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Use only four page-confirmed, exact-config Card-ban leaderboard runs."""

    raw = SNAPSHOT_PATH.read_bytes()
    actual_hash = hashlib.sha256(raw).hexdigest()
    if actual_hash != SNAPSHOT_SHA256:
        raise ValueError(f"Epoch EBR snapshot hash changed: {actual_hash}")
    payload = json.loads(raw)
    if (payload.get("schemaVersion") != 1 or payload.get("sourceUrl") != EXPORT_URL
            or payload.get("ebrMethodologyUrl") != "https://epoch.ai/benchmarks/ebr-bench"
            or payload.get("ebrMethodologyPageSha256")
            != "8402eb5493f573776ca474ed60cbd13d2c6513f9ffa355fffb760e4a517cb5f5"):
        raise ValueError("Epoch EBR Card-ban source metadata changed")
    ebr_rows = [row for row in payload["rows"] if row["task"] == "EBR-bench"]
    if len(ebr_rows) != 23:
        raise ValueError("Epoch EBR run count changed")
    by_run = {row["id_runs"]: row for row in ebr_rows}
    if len(by_run) != len(ebr_rows) or set(EBR_CARD_BAN_RUNS) - set(by_run):
        raise ValueError("Epoch EBR run IDs changed or duplicated")
    source_id = "epoch-ebr-bench-card-ban-v4-owner-2026-09-25"
    source = {
        "id": source_id,
        "label": "Epoch AI EBR-bench v4 Card-ban leaderboard",
        "url": payload["ebrMethodologyUrl"],
        "category": "Benchmark owner leaderboard",
        "collectionStatus": "pinned-official-export-and-methodology; checked 2026-09-25",
        "note": (
            "Epoch's September 22 v4 methodology confirms Card-ban for these "
            "four exact leaderboard runs: GPT-5.6 Sol and Opus 5 were retested, "
            "GPT-6 Astra's published score uses the ban, and newer GPT-6 Sol "
            "also uses it. Older pre-ban runs are excluded. The default "
            "single-agent run uses 10 game playthroughs and reports the top "
            "score over its final two, sampled multiple times. CSV task-version "
            "cells are blank, so the protocol selection depends on the "
            "page's explicit methodology statement and pinned run IDs."
        ),
        "dataUrl": EXPORT_URL,
        "methodologyPageSha256": payload["ebrMethodologyPageSha256"],
        "snapshotFile": str(SNAPSHOT_PATH.relative_to(ROOT)).replace("\\", "/"),
        "snapshotSha256": SNAPSHOT_SHA256,
        "snapshotRows": len(ebr_rows),
        "mappedRows": len(EBR_CARD_BAN_RUNS),
        "benchmarkVersion": "v4 Card-ban",
        "scoreSelection": "mean_score of topline objective fraction (percent)",
    }
    results = []
    for run_id, (epoch_version, site_key) in EBR_CARD_BAN_RUNS.items():
        row = by_run[run_id]
        if (row["model"] != epoch_version or row["Status"] != "Success"
                or row["task version"] != ""):
            raise ValueError(f"Epoch EBR Card-ban run protocol changed: {run_id}")
        results.append({
            "benchmarkId": EBR_BENCHMARK_ID,
            "benchmarkLabel": EBR_BENCHMARK_LABEL,
            "model": site_key,
            "modelAliases": [site_key],
            "value": _score(row),
            "unit": "%",
            "sourceId": source_id,
            "sourceUrl": source["url"],
            "sourceLabel": source["label"],
            "variantScoped": True,
            "modelScoreEligible": True,
            "evidenceEligible": True,
            "configurationConfidence": "explicit",
            "effort": "max",
            "agentHarness": "Epoch default single-agent",
            "systemScore": True,
            "scoreOrigin": "epoch-ai-published-run",
            "scoreSelection": "mean_score",
            "configurationNote": (
                f"EBR-bench v4 Card-ban; Epoch model {epoch_version}; "
                f"run {run_id}; started {row['started_at']}."
            ),
        })
    return source, results
