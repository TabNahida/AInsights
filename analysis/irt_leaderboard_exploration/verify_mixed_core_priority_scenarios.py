"""Read-only check of priority model orders under Mixed Core scenarios.

Run from the repository root:
    python -B -m analysis.irt_leaderboard_exploration.verify_mixed_core_priority_scenarios

Every Extra Test subset refits the current representative calibration. Scenarios
only change module settings inside this process. The historical SciCode check is
explicitly hypothetical and never writes a score to the maintained data.
"""

from __future__ import annotations

import copy
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

from . import aindex_mixed_core as mixed


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs" / "data" / "models.json"
HISTORICAL_SCICODE = 56.5972
WEIGHT_ORDER = tuple(mixed.BOARD_ORDER)
LOW_FIT_ITEMS = frozenset({
    "benchmark:swe-marathon-v1-1-owner",
    "benchmark:osworld-v2-v2026-06-24-standard-500",
    "benchmark:arc-agi-3-standard",
    "benchmark:epoch-ebr-bench-card-ban-v4",
    "benchmark:harvey-lab-aa-all-pass-rate",
})
QUALITY_17_EXCLUSIONS = frozenset({
    "benchmark:frontiercode-v1-1-main-cognition",
    "benchmark:epoch-ebr-bench-card-ban-v4",
})


def family_vectors(vectors: dict[str, np.ndarray], prefix: str,
                   excluded_prefix: str = "") -> list[tuple[str, np.ndarray]]:
    rows = [(slug, vector) for slug, vector in vectors.items()
            if slug.startswith(prefix)
            and (not excluded_prefix or not slug.startswith(excluded_prefix))]
    if not rows:
        raise AssertionError(f"no eligible exact configuration for {prefix}")
    return rows


def vectors_for(models: list[dict], included_items: frozenset[str]):
    original_policies = mixed.EXTENSION_POLICIES
    original_items = mixed.EXTENSION_ITEMS
    try:
        mixed.EXTENSION_POLICIES = {
            board: tuple(policy for policy in original_policies[board]
                         if policy.score_key in included_items)
            for board in WEIGHT_ORDER
        }
        mixed.EXTENSION_ITEMS = {
            board: tuple(policy.score_key for policy in mixed.EXTENSION_POLICIES[board])
            for board in WEIGHT_ORDER
        }
        representatives, _ = mixed.prepare(mixed.representatives(models))
        exact, _ = mixed.prepare(models)
        calibration = mixed.fit_calibration(representatives)
        rows = mixed.score_models(exact, calibration, ranking_grain="exact_config")
        vectors = {
            row["slug"]: np.array(
                [float(row[f"{board}_score_full_precision"]) for board in WEIGHT_ORDER]
            ) for row in rows
        }
        return vectors, calibration["bonus_cap_per_board"]
    finally:
        mixed.EXTENSION_POLICIES = original_policies
        mixed.EXTENSION_ITEMS = original_items


def comparison(vectors: dict[str, np.ndarray], weights: tuple[int, ...]) -> dict:
    if len(weights) != 5 or any(weight < 0 for weight in weights) or sum(weights) != 100:
        raise ValueError("weights must contain five nonnegative percentages summing to 100")
    scale = np.asarray(weights, dtype=float) / 100

    def best(prefix: str, excluded_prefix: str = "") -> tuple[str, float]:
        slug, vector = max(
            family_vectors(vectors, prefix, excluded_prefix),
            key=lambda item: float(item[1] @ scale),
        )
        return slug, float(vector @ scale)

    opus_55 = best("claude-opus-5-5")
    opus_5 = best("claude-opus-5", "claude-opus-5-5")
    fable_51 = best("claude-fable-5-1")
    fable_5 = best("claude-fable-5", "claude-fable-5-1")
    show = lambda winner: {"slug": winner[0], "score": round(winner[1], 6)}
    result = {
        "weights": dict(zip(WEIGHT_ORDER, weights, strict=True)),
        "coding_agentic_reasoning_sum": sum(weights[:3]),
        "opus_5_5": show(opus_55),
        "opus_5": show(opus_5),
        "opus_gap": round(opus_55[1] - opus_5[1], 6),
        "fable_5_1": show(fable_51),
        "fable_5": show(fable_5),
        "fable_gap": round(fable_51[1] - fable_5[1], 6),
    }
    if "gpt-5-4" in vectors:
        gpt_54 = ("gpt-5-4", float(vectors["gpt-5-4"] @ scale))
        luna = best("gpt-5-6-luna")
        result.update(gpt_5_4=show(gpt_54), luna=show(luna),
                      gpt_gap=round(gpt_54[1] - luna[1], 6))
    return result


def balanced_grid_count(vectors: dict[str, np.ndarray]) -> int:
    """Search 5-point weights, each 10--35%, with C+A+R above 60%."""
    matches = 0
    for leading in itertools.product(range(10, 36, 5), repeat=4):
        last = 100 - sum(leading)
        weights = (*leading, last)
        if last not in range(10, 36, 5) or sum(weights[:3]) <= 60:
            continue
        result = comparison(vectors, weights)
        matches += result["opus_gap"] > 0 and result["fable_gap"] > 0
    return matches


def max_common_margin(vectors: dict[str, np.ndarray], minimum_weight: int) -> dict:
    """Exact LP for a fixed subset, allowing its winning Claude tier to vary."""
    if "gpt-5-4" not in vectors:
        raise AssertionError("historical sensitivity model must be eligible")
    gpt_54 = vectors["gpt-5-4"]
    luna = [vector for _, vector in family_vectors(vectors, "gpt-5-6-luna")]
    opus_55 = family_vectors(vectors, "claude-opus-5-5")
    opus_5 = [vector for _, vector in family_vectors(vectors, "claude-opus-5", "claude-opus-5-5")]
    fable_51 = family_vectors(vectors, "claude-fable-5-1")
    fable_5 = [vector for _, vector in family_vectors(vectors, "claude-fable-5", "claude-fable-5-1")]
    best = None
    for (opus_slug, opus_vector), (fable_slug, fable_vector) in itertools.product(opus_55, fable_51):
        differences = ([gpt_54 - other for other in luna]
                       + [opus_vector - other for other in opus_5]
                       + [fable_vector - other for other in fable_5])
        # With percentage weights, each difference @ weights / 100 is a score gap.
        # The sixth LP variable is 100 times the common score-gap margin.
        a_ub = [np.r_[-difference, 1] for difference in differences]
        a_ub.append(np.array([-1, -1, -1, 0, 0, 0]))
        b_ub = np.r_[np.zeros(len(differences)), -60.0001]
        lp = linprog(
            [0, 0, 0, 0, 0, -1], A_ub=a_ub, b_ub=b_ub,
            A_eq=[[1, 1, 1, 1, 1, 0]], b_eq=[100],
            bounds=[(minimum_weight, 100)] * 5 + [(None, None)],
            method="highs",
        )
        if lp.success and (best is None or lp.x[-1] > best[0]):
            best = (lp.x[-1], lp.x[:5], opus_slug, fable_slug)
    if best is None:
        raise AssertionError("LP did not find a feasible weight vector")
    return {
        "minimum_each_board": minimum_weight,
        "best_common_margin_points": round(float(best[0] / 100), 6),
        "weights": dict(zip(WEIGHT_ORDER, (round(float(x), 4) for x in best[1]), strict=True)),
        "opus_candidate": best[2],
        "fable_candidate": best[3],
    }


def main() -> None:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    models = mixed.source_models(payload)
    _, eligibility = mixed.prepare(models)
    gpt_exclusion = next((row for row in eligibility["excluded_models"]
                          if row["slug"] == "gpt-5-4"), None)
    all_items = frozenset(key for keys in mixed.EXTENSION_ITEMS.values() for key in keys)
    subsets = {
        "all_19": all_items,
        "quality_17": all_items - QUALITY_17_EXCLUSIONS,
        "fit_at_least_10_14": all_items - LOW_FIT_ITEMS,
    }
    current = {}
    production_weights = tuple(mixed.BOARD_WEIGHTS[board] for board in WEIGHT_ORDER)
    common_weights = (35, 15, 20, 20, 10)
    for name, items in subsets.items():
        vectors, cap = vectors_for(models, items)
        current[name] = {
            "extra_test_count": len(items),
            "excluded_items": sorted(all_items - items),
            "cap": cap,
            "balanced_grid_matches": balanced_grid_count(vectors),
            "production_weights": comparison(vectors, production_weights),
            "common_candidate": comparison(vectors, common_weights),
        }
        if name == "all_19":
            current[name]["additional_candidate"] = comparison(vectors, (30, 15, 20, 25, 10))

    historical_models = copy.deepcopy(models)
    gpt_54 = next(model for model in historical_models if model["slug"] == "gpt-5-4")
    gpt_54["scores"]["SciCode"] = HISTORICAL_SCICODE
    _, historical_eligibility = mixed.prepare(historical_models)
    historical_all, _ = vectors_for(historical_models, all_items)
    result = {
        "source": str(SOURCE),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "current": {"gpt_5_4_exclusion": gpt_exclusion, "cases": current},
        "historical_scicode_sensitivity_only": {
            "scicode_percent": HISTORICAL_SCICODE,
            "gpt_5_4_eligible_after_in_memory_fill": not any(
                row["slug"] == "gpt-5-4" for row in historical_eligibility["excluded_models"]
            ),
            "all_19_unrestricted_lp": max_common_margin(historical_all, 0),
            "all_19_each_board_at_least_5_lp": max_common_margin(historical_all, 5),
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
