"""Pinned SWE-Marathon v1.1 owner results from all 20 public task bundles.

Each selected exact model effort has eight binary trials on every task. The
benchmark's agent differs by model and is retained in the result metadata.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = ROOT / "data/benchmarks/swe_marathon_v1_1_owner_2026-09-25.json"
SNAPSHOT_SHA256 = "f2fae63bf5c41fa69716290c9c24d1657ccfb2d916b37f41ebc1b6cc7de40e36"
SOURCE_ID = "swe-marathon-v1-1-owner-2026-09-25"
SOURCE_URL = "https://www.swe-marathon.org/"
BENCHMARK_ID = "swe-marathon-v1-1-owner"
BENCHMARK_LABEL = "SWE-Marathon v1.1 (official 20-task run)"
TASK_COUNT = 20
TRIALS_PER_TASK = 8

EXACT_CONFIGS = {
    "openai/gpt-6-astra@max": ("GPT-6 Astra (max) [R]", "GPT-6 Astra", "Codex"),
    "openai/gpt-5.6-sol@max": ("GPT-5.6 Sol (max) [R]", "GPT-5.6-sol", "Codex"),
    "openai/gpt-5.6-terra@max": ("GPT-5.6 Terra (max) [R]", "GPT-5.6-terra", "Codex"),
    "openai/gpt-5.6-luna@max": ("GPT-5.6 Luna (max) [R]", "GPT-5.6-luna", "Codex"),
    "anthropic/claude-sonnet-5@max": ("Claude Sonnet 5 (max) [R]", "Claude Sonnet 5", "Claude Code"),
    "meta/joyful_jello138@max": ("Muse Spark 1.3 (max) [R]", "Muse Spark 1.3", "Muse Code"),
    "zai/glm-5.3@max": ("GLM-5.3 (max) [R]", "GLM 5.3", "Claude Code"),
}


def load_swe_marathon_v1_1_owner_snapshot() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    raw = SNAPSHOT_PATH.read_bytes()
    actual_hash = hashlib.sha256(raw).hexdigest()
    if actual_hash != SNAPSHOT_SHA256:
        raise ValueError(f"SWE-Marathon v1.1 snapshot hash changed: {actual_hash}")
    payload = json.loads(raw)
    if (payload.get("schemaVersion") != 1 or payload.get("benchmarkVersion") != "v1.1"
            or payload.get("taskCount") != TASK_COUNT or payload.get("sourceUrl") != SOURCE_URL):
        raise ValueError("SWE-Marathon v1.1 snapshot metadata changed")
    tasks = payload.get("tasks")
    if not isinstance(tasks, dict) or len(tasks) != TASK_COUNT:
        raise ValueError("SWE-Marathon v1.1 task set changed")
    if len({config[0] for config in EXACT_CONFIGS.values()}) != len(EXACT_CONFIGS):
        raise ValueError("SWE-Marathon exact site configurations are duplicated")

    wins = {variant: 0 for variant in EXACT_CONFIGS}
    trials = {variant: 0 for variant in EXACT_CONFIGS}
    errors = {variant: 0 for variant in EXACT_CONFIGS}
    seen_trial_ids = set()
    for task_id, task in tasks.items():
        if not isinstance(task, dict) or task.get("task") != task_id:
            raise ValueError(f"SWE-Marathon task identity changed: {task_id}")
        configs = task.get("configs")
        if not isinstance(configs, list):
            raise ValueError(f"SWE-Marathon task lacks configurations: {task_id}")
        by_variant = {config.get("modelVariant"): config for config in configs}
        if len(by_variant) != len(configs) or set(by_variant) != set(EXACT_CONFIGS):
            raise ValueError(f"SWE-Marathon exact configuration set changed: {task_id}")
        for variant, (_, expected_model, expected_agent) in EXACT_CONFIGS.items():
            config = by_variant[variant]
            if (config.get("model") != expected_model or config.get("agent") != expected_agent
                    or config.get("reasoningEffort") != "max"
                    or config.get("n") != TRIALS_PER_TASK):
                raise ValueError(f"SWE-Marathon model/agent/effort drift: {task_id}, {variant}")
            task_trials = config.get("trials")
            if not isinstance(task_trials, list) or len(task_trials) != TRIALS_PER_TASK:
                raise ValueError(f"SWE-Marathon trial count changed: {task_id}, {variant}")
            task_wins = 0
            for trial in task_trials:
                trial_id = trial.get("id")
                reward = trial.get("reward")
                status = trial.get("status")
                if (not isinstance(trial_id, str) or trial_id in seen_trial_ids
                        or trial.get("modelVariant") != variant
                        or trial.get("reasoningEffort") != "max"
                        or trial.get("agent") != expected_agent
                        or isinstance(reward, bool) or reward not in (0, 0.0, 1, 1.0)
                        or status not in ("success", "error")):
                    raise ValueError(f"SWE-Marathon trial identity/outcome changed: {task_id}, {variant}")
                seen_trial_ids.add(trial_id)
                task_wins += int(reward)
                errors[variant] += status == "error"
            if config.get("binary") != f"{task_wins} / {TRIALS_PER_TASK}":
                raise ValueError(f"SWE-Marathon task binary total changed: {task_id}, {variant}")
            wins[variant] += task_wins
            trials[variant] += TRIALS_PER_TASK

    source = {
        "id": SOURCE_ID,
        "label": "SWE-Marathon v1.1 official current leaderboard",
        "url": SOURCE_URL,
        "category": "Benchmark owner leaderboard",
        "collectionStatus": "pinned-public-page-bundle; downloaded 2026-09-25",
        "note": (
            "All 20 v1.1 long software-engineering tasks and eight trials per "
            "task are included. Published binary rewards are summed over 160 "
            "attempts; some GLM trials carry an error status despite a binary "
            "reward, so status is not used to recalculate the official score. "
            "The owner uses model-specific "
            "Codex, Claude Code, or Muse Code agents, so this is a system result. "
            "The page bundle contains the current leaderboard even though older "
            "README/SEO text says results are pending."
        ),
        "bundleUrl": payload["bundleUrl"],
        "bundleSha256": payload["bundleSha256"],
        "snapshotFile": str(SNAPSHOT_PATH.relative_to(ROOT)).replace("\\", "/"),
        "snapshotSha256": SNAPSHOT_SHA256,
        "benchmarkVersion": "v1.1",
        "taskCount": TASK_COUNT,
        "trialsPerTask": TRIALS_PER_TASK,
        "mappedRows": len(EXACT_CONFIGS),
        "scoreSelection": "binary wins / 160 trials (percent)",
    }
    results = []
    for variant, (site_key, _, agent) in EXACT_CONFIGS.items():
        if trials[variant] != TASK_COUNT * TRIALS_PER_TASK:
            raise ValueError(f"SWE-Marathon incomplete trial set: {variant}")
        results.append({
            "benchmarkId": BENCHMARK_ID,
            "benchmarkLabel": BENCHMARK_LABEL,
            "model": site_key,
            "modelAliases": [site_key],
            "value": 100 * wins[variant] / trials[variant],
            "unit": "%",
            "sourceId": SOURCE_ID,
            "sourceUrl": SOURCE_URL,
            "sourceLabel": source["label"],
            "variantScoped": True,
            "modelScoreEligible": True,
            "evidenceEligible": True,
            "configurationConfidence": "explicit",
            "effort": "max",
            "agentHarness": agent,
            "systemScore": True,
            "scoreOrigin": "swe-marathon-owner-leaderboard",
            "scoreSelection": source["scoreSelection"],
            "configurationNote": (
                f"SWE-Marathon v1.1; {variant}; {agent}; "
                f"{wins[variant]}/{trials[variant]} binary wins, "
                f"{errors[variant]} trials are labeled error in the bundle."
            ),
        })
    return source, results
