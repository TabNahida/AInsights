"""Production implementation of the selected AIndex Scheme 18.

The method is deliberately model-anonymous.  Five equally weighted capability
boards are scored from complete, common-protocol core observations.  Each core
score is the unweighted geometric partial-credit mastery on the native 0--100
scale.  Independently controlled extension benchmarks may add only a positive
residual over an anonymous cohort-wide OLS trend.  Positive residuals are
combined by a zero-neutral monotone log-sum-exp and capped by one pooled,
population-derived ``mean + sqrt(2) * population SD`` value.

The fit/apply split is important.  The default deduplicated population fits the
extension trends and the shared cap once.  Exact-configuration rows are then
scored on that same ruler; they never refit the OLS trends or cap.  Missing
extension observations remain absent and earn no bonus.  Core observations
must be complete.

No named-model acceptance gate, provider term, product-order rule, or post-hoc
rank adjustment is imported or implemented here.
"""

from __future__ import annotations

import csv
import json
import math
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

try:
    from . import v5_benchmark_policy as benchmark_policy
except ImportError:  # pragma: no cover - direct script imports
    import v5_benchmark_policy as benchmark_policy


ANALYSIS_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = ANALYSIS_DIR / "outputs"

METHOD_ID = "aindex_scheme18"
CANDIDATE_ID = (
    "v5_partial_credit_geometric_logsumexp_residual_t1_"
    "independent_audit_mean_plus_sqrt2_sd"
)
BOARD_ORDER = (
    "coding",
    "agentic-tool-work",
    "hard-reasoning",
    "knowledge-science",
    "instruction-context",
)
BOARD_POINTS = 20.0
CAP_RULE = "mean_plus_sqrt2_sd"
CORE_FIT = "partial_credit_geometric"
EXTENSION_AGGREGATOR = "logsumexp_residual_t1"

OUTPUT_FILENAMES = {
    "full_rankings": "full_rankings_aindex_scheme18.csv",
    "top50": "top50_aindex_scheme18.csv",
    "exact_config_full_rankings": (
        "full_rankings_exact_config_aindex_scheme18.csv"
    ),
    "exact_config_top50": "top50_exact_config_aindex_scheme18.csv",
    "validation": "aindex_scheme18_validation_summary.json",
}

# Exact and Unicode-compatible aliases in the local Artificial Analysis feed.
SCORE_ALIASES: dict[str, tuple[str, ...]] = {
    "tau2-Bench Telecom": ("tau2-Bench Telecom", "τ²-Bench Telecom"),
    "τ²-Bench Telecom": ("τ²-Bench Telecom", "tau2-Bench Telecom"),
    "tau3-Banking": ("tau3-Banking", "τ³-Banking"),
    "τ³-Banking": ("τ³-Banking", "tau3-Banking"),
}


def _policy_item_specs() -> tuple[
    dict[str, tuple[benchmark_policy.BenchmarkPolicy, ...]],
    dict[str, tuple[benchmark_policy.BenchmarkPolicy, ...]],
]:
    """Return the exact Scheme 18 core and independent extension registries."""

    core: dict[str, list[benchmark_policy.BenchmarkPolicy]] = {
        board_id: [] for board_id in BOARD_ORDER
    }
    extension: dict[str, list[benchmark_policy.BenchmarkPolicy]] = {
        board_id: [] for board_id in BOARD_ORDER
    }
    seen_extension_families: dict[str, set[str]] = {
        board_id: set() for board_id in BOARD_ORDER
    }

    for policy in benchmark_policy.BENCHMARK_POLICIES:
        if policy.tier == "core" and policy.publication_eligible:
            for board_id in policy.boards:
                core[board_id].append(policy)
        if policy.tier == "extension" and policy.publication_eligible:
            for board_id in policy.boards:
                if policy.canonical_family in seen_extension_families[board_id]:
                    raise AssertionError(
                        f"duplicate extension family {policy.canonical_family!r} "
                        f"inside {board_id!r}"
                    )
                extension[board_id].append(policy)
                seen_extension_families[board_id].add(policy.canonical_family)

    # Scheme 18's wider review pool admits only benchmarks whose controller is
    # affirmatively independent of every ranked model vendor.  Unknown and
    # vendor-controlled benchmark owners remain out of the score.
    for policy in benchmark_policy.BENCHMARK_POLICIES:
        if not (
            policy.tier == "conditional_extension"
            and policy.exploration_eligible
            and policy.controller_is_ranked_model_vendor is False
        ):
            continue
        for board_id in policy.boards:
            if policy.canonical_family in seen_extension_families[board_id]:
                continue
            extension[board_id].append(policy)
            seen_extension_families[board_id].add(policy.canonical_family)

    result_core = {
        board_id: tuple(policies) for board_id, policies in core.items()
    }
    result_extension = {
        board_id: tuple(policies) for board_id, policies in extension.items()
    }
    if any(not result_core[board_id] for board_id in BOARD_ORDER):
        raise AssertionError("every Scheme 18 board must contain a core item")
    return result_core, result_extension


CORE_POLICIES, EXTENSION_POLICIES = _policy_item_specs()
CORE_ITEMS = {
    board_id: tuple(policy.score_key for policy in CORE_POLICIES[board_id])
    for board_id in BOARD_ORDER
}
EXTENSION_ITEMS = {
    board_id: tuple(
        policy.score_key for policy in EXTENSION_POLICIES[board_id]
    )
    for board_id in BOARD_ORDER
}


def finite_number(value: Any) -> float | None:
    if value is None or isinstance(value, bool) or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def score_value(model: Mapping[str, Any], key: str) -> float | None:
    scores = model.get("scores") or {}
    for alias in SCORE_ALIASES.get(key, (key,)):
        value = finite_number(scores.get(alias))
        if value is None:
            continue
        if not 0.0 <= value <= 100.0:
            raise AssertionError(
                f"{alias!r} is outside the direct 0--100 score scale: {value}"
            )
        return value
    return None


def score_matrix(
    models: Sequence[Mapping[str, Any]],
    keys: Iterable[str],
) -> np.ndarray:
    key_list = tuple(keys)
    return np.asarray(
        [[score_value(model, key) for key in key_list] for model in models],
        dtype=float,
    )


def geometric_core_score(raw: np.ndarray) -> np.ndarray:
    """Return unweighted geometric partial-credit mastery on a 0--100 scale."""

    values = np.asarray(raw, dtype=float)
    if values.ndim != 2 or values.shape[1] == 0:
        raise AssertionError("core matrices must be non-empty two-dimensional arrays")
    if np.any(~np.isfinite(values)):
        raise AssertionError("Scheme 18 core matrices must be complete")
    if np.any((values < 0.0) | (values > 100.0)):
        raise AssertionError("Scheme 18 core observations must be in 0--100")
    scaled = np.clip(values, 1e-6, 100.0) / 100.0
    return 100.0 * np.exp(np.mean(np.log(scaled), axis=1))


def _fit_positive_residuals(
    core: np.ndarray,
    extensions: np.ndarray,
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    """Fit anonymous non-negative-slope OLS trends and positive residuals."""

    core_values = np.asarray(core, dtype=float)
    extension_values = np.asarray(extensions, dtype=float)
    if core_values.ndim != 1:
        raise AssertionError("core board score must be one-dimensional")
    if extension_values.ndim != 2 or len(extension_values) != len(core_values):
        raise AssertionError("extension matrix shape does not match core scores")
    if np.any(~np.isfinite(core_values)):
        raise AssertionError("core board scores must be finite")

    residuals = np.full(extension_values.shape, np.nan, dtype=float)
    trends: list[dict[str, Any]] = []
    for column_index in range(extension_values.shape[1]):
        y = extension_values[:, column_index]
        observed = np.isfinite(y)
        observed_count = int(np.sum(observed))
        if observed_count < 5:
            trends.append(
                {
                    "enabled": False,
                    "observed_count": observed_count,
                    "slope": None,
                    "intercept": None,
                }
            )
            continue
        x_obs = core_values[observed]
        y_obs = y[observed]
        variance = float(np.sum((x_obs - np.mean(x_obs)) ** 2))
        slope = (
            float(
                np.sum(
                    (x_obs - np.mean(x_obs))
                    * (y_obs - np.mean(y_obs))
                )
            )
            / variance
            if variance > 1e-12
            else 0.0
        )
        slope = max(0.0, slope)
        intercept = float(np.mean(y_obs) - slope * np.mean(x_obs))
        predicted = np.clip(
            intercept + slope * core_values[observed],
            0.0,
            100.0,
        )
        residuals[observed, column_index] = np.maximum(
            y_obs - predicted,
            0.0,
        )
        trends.append(
            {
                "enabled": True,
                "observed_count": observed_count,
                "slope": slope,
                "intercept": intercept,
            }
        )
    return residuals, trends


def positive_residuals(core: np.ndarray, extensions: np.ndarray) -> np.ndarray:
    """Return positive extension residuals over anonymous cohort-wide OLS."""

    residuals, _trends = _fit_positive_residuals(core, extensions)
    return residuals


def _apply_extension_trends(
    core: np.ndarray,
    extensions: np.ndarray,
    trends: Sequence[Mapping[str, Any]],
) -> np.ndarray:
    """Apply frozen deduplicated-population OLS trends without refitting."""

    core_values = np.asarray(core, dtype=float)
    extension_values = np.asarray(extensions, dtype=float)
    if extension_values.ndim != 2 or len(extension_values) != len(core_values):
        raise AssertionError("extension matrix shape does not match core scores")
    if extension_values.shape[1] != len(trends):
        raise AssertionError("extension matrix does not match frozen trends")
    residuals = np.full(extension_values.shape, np.nan, dtype=float)
    for column_index, trend in enumerate(trends):
        if not bool(trend.get("enabled")):
            continue
        slope = finite_number(trend.get("slope"))
        intercept = finite_number(trend.get("intercept"))
        if slope is None or intercept is None or slope < 0.0:
            raise AssertionError("enabled extension trend is invalid")
        y = extension_values[:, column_index]
        observed = np.isfinite(y)
        predicted = np.clip(
            intercept + slope * core_values[observed],
            0.0,
            100.0,
        )
        residuals[observed, column_index] = np.maximum(
            y[observed] - predicted,
            0.0,
        )
    return residuals


def derive_cap(
    residuals_by_board: Mapping[str, np.ndarray] | Iterable[np.ndarray],
) -> float:
    """Derive the shared ``mean + sqrt(2) * population SD`` positive cap."""

    arrays = (
        [residuals_by_board[board_id] for board_id in BOARD_ORDER]
        if isinstance(residuals_by_board, Mapping)
        else list(residuals_by_board)
    )
    values: list[float] = []
    for residuals in arrays:
        array = np.asarray(residuals, dtype=float)
        positive = array[np.isfinite(array) & (array > 0.0)]
        values.extend(float(value) for value in positive)
    if not values:
        raise AssertionError("cannot derive Scheme 18 cap without positive evidence")
    observed = np.asarray(values, dtype=float)
    return float(
        np.mean(observed)
        + math.sqrt(2.0) * np.std(observed, ddof=0)
    )


def extension_bonus(residuals: np.ndarray, cap: float) -> np.ndarray:
    """Combine positive residuals with zero-neutral monotone log-sum-exp."""

    values = np.asarray(residuals, dtype=float)
    if values.ndim != 2:
        raise AssertionError("extension residuals must be two-dimensional")
    if not math.isfinite(cap) or cap < 0.0:
        raise AssertionError("Scheme 18 cap must be finite and non-negative")
    bonus = np.zeros(values.shape[0], dtype=float)
    for index, row in enumerate(values):
        observed = row[np.isfinite(row)]
        if not len(observed):
            continue
        positive = np.sort(observed[observed > 0.0])[::-1]
        if not len(positive):
            continue
        raw = math.log1p(float(np.sum(np.expm1(positive))))
        bonus[index] = min(cap, max(0.0, raw))
    if np.any(bonus < -1e-12) or np.any(bonus > cap + 1e-12):
        raise AssertionError("Scheme 18 extension bonus left its valid range")
    return bonus


def _canonical_model_order(
    models: Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    """Match the reviewed v5 calibration population order exactly."""

    return sorted(
        models,
        key=lambda model: (
            str(model.get("creator") or ""),
            str(model.get("model") or ""),
        ),
    )


def fit_calibration(
    models: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Fit Scheme 18 OLS trends and one shared cap on deduplicated models."""

    calibration_models = _canonical_model_order(models)
    if not calibration_models:
        raise AssertionError("Scheme 18 calibration population is empty")
    slugs = [str(model.get("slug") or "") for model in calibration_models]
    groups = [str(model.get("variantGroup") or "") for model in calibration_models]
    if any(not slug for slug in slugs) or len(set(slugs)) != len(slugs):
        raise AssertionError("calibration slugs must be present and unique")
    if any(not group for group in groups) or len(set(groups)) != len(groups):
        raise AssertionError("calibration variant groups must be present and unique")

    residuals_by_board: dict[str, np.ndarray] = {}
    board_calibration: dict[str, dict[str, Any]] = {}
    pooled_positive: list[float] = []
    for board_id in BOARD_ORDER:
        core_raw = score_matrix(calibration_models, CORE_ITEMS[board_id])
        base_score = geometric_core_score(core_raw)
        extension_raw = score_matrix(
            calibration_models,
            EXTENSION_ITEMS[board_id],
        )
        residuals, trends = _fit_positive_residuals(base_score, extension_raw)
        residuals_by_board[board_id] = residuals
        positive = residuals[np.isfinite(residuals) & (residuals > 0.0)]
        pooled_positive.extend(float(value) for value in positive)
        trend_rows = []
        for policy, trend in zip(
            EXTENSION_POLICIES[board_id],
            trends,
            strict=True,
        ):
            trend_rows.append(
                {
                    "item_id": policy.item_id,
                    "score_key": policy.score_key,
                    "canonical_family": policy.canonical_family,
                    **trend,
                }
            )
        board_calibration[board_id] = {
            "core_items": [
                {
                    "item_id": policy.item_id,
                    "score_key": policy.score_key,
                    "canonical_family": policy.canonical_family,
                }
                for policy in CORE_POLICIES[board_id]
            ],
            "extension_items": trend_rows,
            "core_item_count": len(CORE_ITEMS[board_id]),
            "extension_item_count": len(EXTENSION_ITEMS[board_id]),
        }

    cap = derive_cap(residuals_by_board)
    positive_array = np.asarray(pooled_positive, dtype=float)
    return {
        "method_id": METHOD_ID,
        "candidate_id": CANDIDATE_ID,
        "policy_version": benchmark_policy.POLICY_VERSION,
        "core_fit": CORE_FIT,
        "extension_aggregator": EXTENSION_AGGREGATOR,
        "extension_pool": "independent_audit",
        "cap_rule": CAP_RULE,
        "bonus_cap_per_board": cap,
        "pooled_positive_residual_count": len(pooled_positive),
        "pooled_positive_residual_mean": float(np.mean(positive_array)),
        "pooled_positive_residual_population_sd": float(
            np.std(positive_array, ddof=0)
        ),
        "board_order": list(BOARD_ORDER),
        "board_points_max": BOARD_POINTS,
        "population_size": len(calibration_models),
        "population_slugs": slugs,
        "population_variant_groups": groups,
        "missing_policy": (
            "core must be complete; missing extension is absent and earns zero "
            "bonus; no value is imputed"
        ),
        "fit_apply_policy": (
            "fit OLS trends and shared cap once on the deduplicated population; "
            "apply unchanged to exact configurations"
        ),
        "boards": board_calibration,
    }


def _families_observed(
    model: Mapping[str, Any],
) -> tuple[int, int]:
    core_families = {
        policy.canonical_family
        for board_id in BOARD_ORDER
        for policy in CORE_POLICIES[board_id]
    }
    extension_families = {
        policy.canonical_family
        for board_id in BOARD_ORDER
        for policy in EXTENSION_POLICIES[board_id]
        if score_value(model, policy.score_key) is not None
    }
    return len(core_families | extension_families), len(extension_families)


def score_models(
    models: Sequence[Mapping[str, Any]],
    calibration: Mapping[str, Any],
    *,
    ranking_grain: str = "variant_group",
) -> list[dict[str, Any]]:
    """Apply a frozen Scheme 18 calibration and return unranked row records."""

    scoring_models = list(models)
    if not scoring_models:
        return []
    cap = finite_number(calibration.get("bonus_cap_per_board"))
    if cap is None or cap < 0.0:
        raise AssertionError("Scheme 18 calibration has no valid shared cap")
    if list(calibration.get("board_order") or []) != list(BOARD_ORDER):
        raise AssertionError("Scheme 18 calibration board order changed")

    board_base: dict[str, np.ndarray] = {}
    board_bonus: dict[str, np.ndarray] = {}
    board_scores: dict[str, np.ndarray] = {}
    board_points: dict[str, np.ndarray] = {}
    extension_coverage: dict[str, np.ndarray] = {}
    for board_id in BOARD_ORDER:
        core_raw = score_matrix(scoring_models, CORE_ITEMS[board_id])
        base_score = geometric_core_score(core_raw)
        extension_raw = score_matrix(scoring_models, EXTENSION_ITEMS[board_id])
        board_meta = (calibration.get("boards") or {}).get(board_id) or {}
        trends = board_meta.get("extension_items") or []
        residuals = _apply_extension_trends(base_score, extension_raw, trends)
        bonus = extension_bonus(residuals, cap)
        score = np.minimum(100.0, base_score + bonus)
        points = BOARD_POINTS * score / 100.0
        board_base[board_id] = base_score
        board_bonus[board_id] = bonus
        board_scores[board_id] = score
        board_points[board_id] = points
        extension_coverage[board_id] = np.sum(
            np.isfinite(extension_raw),
            axis=1,
        ).astype(int)

    final_score = np.sum(
        np.column_stack([board_points[board_id] for board_id in BOARD_ORDER]),
        axis=1,
    )
    rows: list[dict[str, Any]] = []
    total_pool_slots = sum(
        len(CORE_ITEMS[board_id]) + len(EXTENSION_ITEMS[board_id])
        for board_id in BOARD_ORDER
    )
    for index, model in enumerate(scoring_models):
        score = float(final_score[index])
        unique_families, unique_extension_families = _families_observed(model)
        observed_slots = 0
        point_sum = 0.0
        row: dict[str, Any] = {
            "method": METHOD_ID,
            "candidate_id": CANDIDATE_ID,
            "rank": 0,
            "model": str(model.get("model") or ""),
            "creator": str(model.get("creator") or ""),
            "slug": str(model.get("slug") or ""),
            "variant_group": str(model.get("variantGroup") or ""),
            "ranking_grain": ranking_grain,
            "score_full_precision": format(score, ".17g"),
            "score": round(score, 6),
            "final_score": round(score, 6),
            "score_scale": "0-100 additive five-board points",
            "ranking_key": (
                "unrounded_score_desc_then_slug_model_for_exact_ties"
            ),
            "evidence_tier": "Core complete",
            "unique_benchmark_families": unique_families,
            "unique_extension_families": unique_extension_families,
            "core_tests_total": sum(
                len(CORE_ITEMS[board_id]) for board_id in BOARD_ORDER
            ),
        }
        for board_id in BOARD_ORDER:
            base_score = float(board_base[board_id][index])
            bonus = float(board_bonus[board_id][index])
            board_score = float(board_scores[board_id][index])
            points = float(board_points[board_id][index])
            core_tests = len(CORE_ITEMS[board_id])
            extension_tests = int(extension_coverage[board_id][index])
            total_tests = core_tests + extension_tests
            observed_slots += total_tests
            point_sum += points
            row[f"{board_id}_core_score"] = round(base_score, 6)
            row[f"{board_id}_extension_bonus"] = round(bonus, 6)
            row[f"{board_id}_core_tests"] = core_tests
            row[f"{board_id}_extension_tests"] = extension_tests
            row[f"{board_id}_tests"] = total_tests
            row[f"{board_id}_core_item_pool_size"] = len(
                CORE_ITEMS[board_id]
            )
            row[f"{board_id}_extension_item_pool_size"] = len(
                EXTENSION_ITEMS[board_id]
            )
            row[f"{board_id}_score_full_precision"] = format(
                board_score,
                ".17g",
            )
            row[f"{board_id}_score"] = round(board_score, 6)
            row[f"{board_id}_points_full_precision"] = format(points, ".17g")
            row[f"{board_id}_points"] = round(points, 6)
        if abs(point_sum - score) > 1e-11:
            raise AssertionError("Scheme 18 final score identity failed")
        row["board_test_slots_total"] = observed_slots
        row["board_test_slots_available"] = total_pool_slots
        row["evidence_coverage_score"] = round(
            100.0 * observed_slots / total_pool_slots,
            6,
        )
        row["points_sum_full_precision"] = format(point_sum, ".17g")
        rows.append(row)
    return rows


def rank_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Sort solely by unrounded score, using stable IDs only for exact ties."""

    ranked = [dict(row) for row in rows]
    ranked.sort(
        key=lambda row: (
            -float(row["score_full_precision"]),
            str(row.get("slug") or ""),
            str(row.get("model") or ""),
        )
    )
    for rank, row in enumerate(ranked, start=1):
        row["rank"] = rank
    return ranked


def validate_rankings(
    full_rankings: Sequence[Mapping[str, Any]],
    exact_config_full_rankings: Sequence[Mapping[str, Any]],
    calibration: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate score identities, ordering, coverage, and shared calibration."""

    cap = float(calibration["bonus_cap_per_board"])

    def audit(rows: Sequence[Mapping[str, Any]], grain: str) -> dict[str, Any]:
        failures: list[str] = []
        previous_score = math.inf
        slugs: set[str] = set()
        groups: set[str] = set()
        max_identity_error = 0.0
        for position, row in enumerate(rows, start=1):
            slug = str(row.get("slug") or "")
            group = str(row.get("variant_group") or "")
            score = float(row["score_full_precision"])
            if int(row.get("rank") or 0) != position:
                failures.append(f"rank mismatch at position {position}")
            if score > previous_score + 1e-12:
                failures.append(f"score order increased at position {position}")
            previous_score = score
            if not slug or slug in slugs:
                failures.append(f"missing or duplicate slug {slug!r}")
            slugs.add(slug)
            if group:
                groups.add(group)
            points = 0.0
            for board_id in BOARD_ORDER:
                base_score = float(row[f"{board_id}_core_score"])
                bonus = float(row[f"{board_id}_extension_bonus"])
                board_score = float(row[f"{board_id}_score_full_precision"])
                board_points = float(row[f"{board_id}_points_full_precision"])
                if not 0.0 <= base_score <= 100.0:
                    failures.append(f"{slug}: invalid {board_id} core")
                if not 0.0 <= bonus <= cap + 1e-6:
                    failures.append(f"{slug}: invalid {board_id} bonus")
                if not 0.0 <= board_score <= 100.0:
                    failures.append(f"{slug}: invalid {board_id} score")
                points += board_points
            error = abs(points - score)
            max_identity_error = max(max_identity_error, error)
            if error > 1e-11:
                failures.append(f"{slug}: final score identity error {error:g}")
        return {
            "ranking_grain": grain,
            "row_count": len(rows),
            "unique_slugs": len(slugs),
            "unique_variant_groups": len(groups),
            "max_final_score_identity_error": max_identity_error,
            "passed": not failures,
            "failures": failures,
        }

    group_audit = audit(full_rankings, "variant_group")
    exact_audit = audit(exact_config_full_rankings, "exact_config")
    return {
        "method_id": METHOD_ID,
        "candidate_id": CANDIDATE_ID,
        "calibration_population_size": int(calibration["population_size"]),
        "bonus_cap_per_board": cap,
        "cap_rule": str(calibration["cap_rule"]),
        "exact_reuses_deduplicated_calibration": True,
        "variant_group": group_audit,
        "exact_config": exact_audit,
        "passed": bool(group_audit["passed"] and exact_audit["passed"]),
    }


def _models_for_slugs(
    models: Sequence[Mapping[str, Any]],
    slugs: Sequence[str],
    *,
    label: str,
) -> list[Mapping[str, Any]]:
    by_slug: dict[str, Mapping[str, Any]] = {}
    for model in models:
        slug = str(model.get("slug") or "")
        if not slug:
            continue
        if slug in by_slug:
            raise AssertionError(f"duplicate {label} model slug {slug!r}")
        by_slug[slug] = model
    requested = list(slugs)
    if len(set(requested)) != len(requested):
        raise AssertionError(f"duplicate slug in requested {label} population")
    missing = [slug for slug in requested if slug not in by_slug]
    if missing:
        raise AssertionError(
            f"{label} population references missing slugs: {missing[:5]}"
        )
    return [by_slug[slug] for slug in requested]


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for field in row:
            if field not in seen:
                seen.add(field)
                fieldnames.append(field)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def run_aindex_scheme18_from_payload(
    payload: Mapping[str, Any],
    *,
    calibration_slugs: Sequence[str],
    exact_config_slugs: Sequence[str] = (),
    exact_config_models: Sequence[Mapping[str, Any]] | None = None,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write_outputs: bool = False,
) -> dict[str, Any]:
    """Fit the reviewed deduplicated population and apply it to exact configs."""

    source_models = list(payload.get("models") or [])
    calibration_models = _models_for_slugs(
        source_models,
        calibration_slugs,
        label="calibration",
    )
    calibration = fit_calibration(calibration_models)
    full_rankings = rank_rows(
        score_models(
            calibration_models,
            calibration,
            ranking_grain="variant_group",
        )
    )

    exact_source_models = (
        list(exact_config_models)
        if exact_config_models is not None
        else source_models
    )
    exact_models = _models_for_slugs(
        exact_source_models,
        exact_config_slugs,
        label="exact-config",
    )
    exact_config_full_rankings = rank_rows(
        score_models(
            exact_models,
            calibration,
            ranking_grain="exact_config",
        )
    )
    validation = validate_rankings(
        full_rankings,
        exact_config_full_rankings,
        calibration,
    )
    if not validation["passed"]:
        raise AssertionError("Scheme 18 production validation failed")

    result = {
        "full_rankings": full_rankings,
        "top50": full_rankings[:50],
        "exact_config_full_rankings": exact_config_full_rankings,
        "exact_config_top50": exact_config_full_rankings[:50],
        "calibration": calibration,
        "validation": validation,
    }
    if write_outputs:
        output_dir.mkdir(parents=True, exist_ok=True)
        write_csv(output_dir / OUTPUT_FILENAMES["full_rankings"], full_rankings)
        write_csv(output_dir / OUTPUT_FILENAMES["top50"], full_rankings[:50])
        write_csv(
            output_dir / OUTPUT_FILENAMES["exact_config_full_rankings"],
            exact_config_full_rankings,
        )
        write_csv(
            output_dir / OUTPUT_FILENAMES["exact_config_top50"],
            exact_config_full_rankings[:50],
        )
        validation_payload = {
            **validation,
            "calibration": calibration,
        }
        (output_dir / OUTPUT_FILENAMES["validation"]).write_text(
            json.dumps(validation_payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return result
