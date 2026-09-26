"""Reproduce read-only Mixed Core weight and Extra Test sensitivity cases.

Run from the repository root with
``python -m analysis.irt_leaderboard_exploration.verify_mixed_core_scenarios``.
This changes module settings only inside this process; production files are not
written. Every Extra Test subset refits the production OLS trends and cap.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from . import aindex_mixed_core as mixed


ROOT = Path(__file__).resolve().parents[2]
PAYLOAD = ROOT / "docs" / "data" / "models.json"

LOW_FIT_ITEMS = (
    "benchmark:swe-marathon-v1-1-owner",
    "benchmark:osworld-v2-v2026-06-24-standard-500",
    "benchmark:arc-agi-3-standard",
    "benchmark:epoch-ebr-bench-card-ban-v4",
    "benchmark:harvey-lab-aa-all-pass-rate",
)

SCENARIOS = (
    ("all_19_minimum_knowledge", (), (14, 5, 5, 66, 10)),
    ("all_19_more_grok_margin", (), (16, 5, 5, 69, 5)),
    ("without_frontiercode_and_ebr", (
        "benchmark:frontiercode-v1-1-main-cognition",
        "benchmark:epoch-ebr-bench-card-ban-v4",
    ), (15, 5, 5, 69, 6)),
    ("fit_at_least_10", LOW_FIT_ITEMS, (15, 5, 5, 68, 7)),
)

FAMILIES = {
    "grok_47": ("grok-4-7", ()),
    "grok_46": ("grok-4-6", ()),
    "grok_45": ("grok-4-5", ()),
    "mimo_pro": ("mimo-v2-6-pro", ()),
    "deepseek_41_flash": ("deepseek-v4-1-flash", ()),
    "deepseek_4_flash": ("deepseek-v4-flash", ()),
    "opus_55": ("claude-opus-5-5", ()),
    "opus_5": ("claude-opus-5", ("claude-opus-5-5",)),
    "fable_51": ("claude-fable-5-1", ()),
    "fable_5": ("claude-fable-5", ("claude-fable-5-1",)),
}

COMPARISONS = (
    ("grok_47_over_46", "grok_47", "grok_46"),
    ("grok_46_over_45", "grok_46", "grok_45"),
    ("deepseek_41_over_mimo", "deepseek_41_flash", "mimo_pro"),
    ("deepseek_41_over_all_v4_flash", "deepseek_41_flash", "deepseek_4_flash"),
    ("opus_55_over_5", "opus_55", "opus_5"),
    ("fable_51_over_5", "fable_51", "fable_5"),
)


def best_exact_configuration(rows: list[dict], prefix: str, excluded_prefixes: tuple[str, ...]) -> dict:
    candidates = [
        row for row in rows
        if row["slug"].startswith(prefix)
        and not any(row["slug"].startswith(value) for value in excluded_prefixes)
    ]
    if not candidates:
        raise AssertionError(f"no eligible exact configuration for {prefix}")
    return max(candidates, key=lambda row: float(row["score_full_precision"]))


def evaluate(models: list[dict], excluded_items: tuple[str, ...], weights: tuple[int, ...]) -> dict:
    original_policies = mixed.EXTENSION_POLICIES
    original_items = mixed.EXTENSION_ITEMS
    original_weights = mixed.BOARD_WEIGHTS
    try:
        mixed.EXTENSION_POLICIES = {
            board: tuple(policy for policy in original_policies[board]
                         if policy.score_key not in excluded_items)
            for board in mixed.BOARD_ORDER
        }
        mixed.EXTENSION_ITEMS = {
            board: tuple(policy.score_key for policy in mixed.EXTENSION_POLICIES[board])
            for board in mixed.BOARD_ORDER
        }
        mixed.BOARD_WEIGHTS = dict(zip(mixed.BOARD_ORDER, weights, strict=True))

        grouped, _ = mixed.prepare(mixed.representatives(models))
        exact, _ = mixed.prepare(models)
        calibration = mixed.fit_calibration(grouped)
        grouped_rows = mixed.rank_rows(mixed.score_models(grouped, calibration))
        exact_rows = mixed.rank_rows(mixed.score_models(exact, calibration, ranking_grain="exact_config"))
        validation = mixed.validate_rankings(grouped_rows, exact_rows, calibration)
        if not validation["passed"]:
            raise AssertionError(validation)

        winners = {
            family: best_exact_configuration(exact_rows, *selector)
            for family, selector in FAMILIES.items()
        }
        gaps = {
            name: round(
                float(winners[a]["score_full_precision"])
                - float(winners[b]["score_full_precision"]),
                6,
            )
            for name, a, b in COMPARISONS
        }
        return {
            "weights": dict(mixed.BOARD_WEIGHTS),
            "extra_test_count": sum(map(len, mixed.EXTENSION_ITEMS.values())),
            "excluded_extra_tests": list(excluded_items),
            "cap": calibration["bonus_cap_per_board"],
            "ranked_exact_configurations": len(exact_rows),
            "highest_scoring_configurations": {
                family: {"slug": row["slug"], "score": row["score"]}
                for family, row in winners.items()
            },
            "score_gaps": gaps,
            "all_six_comparable_conditions_met": all(value > 0 for value in gaps.values()),
        }
    finally:
        mixed.EXTENSION_POLICIES = original_policies
        mixed.EXTENSION_ITEMS = original_items
        mixed.BOARD_WEIGHTS = original_weights


def main() -> None:
    payload = json.loads(PAYLOAD.read_text(encoding="utf-8"))
    models = mixed.source_models(payload)
    _, eligibility = mixed.prepare(models)
    excluded_slugs = {row["slug"] for row in eligibility["excluded_models"]}
    result = {
        "source": str(PAYLOAD),
        "source_sha256": hashlib.sha256(PAYLOAD.read_bytes()).hexdigest(),
        "gpt_5_4_xhigh_eligible": "gpt-5-4" not in excluded_slugs,
        "scenarios": {
            name: evaluate(models, excluded_items, weights)
            for name, excluded_items, weights in SCENARIOS
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
