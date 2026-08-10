"""Independently validate the production AIndex Scheme 18 artifacts.

This validator intentionally does not import :mod:`aindex_scheme18`.  It
reconstructs the policy pools, geometric core scores, OLS trends, pooled cap,
monotone extension bonuses, five-board point identity, and both ranking orders
from the source payload plus the serialized calibration.  It can optionally
compare the deduplicated output with the reviewed v5 candidate CSV.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

try:
    from . import evidence_only_ranking_analysis as evidence
    from . import v5_benchmark_policy as benchmark_policy
except ImportError:  # pragma: no cover - direct CLI execution
    import evidence_only_ranking_analysis as evidence
    import v5_benchmark_policy as benchmark_policy


HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "docs" / "data" / "models.json"
DEFAULT_OUTPUT_DIR = HERE / "outputs"

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
FULL_RANKING_FILENAME = "full_rankings_aindex_scheme18.csv"
TOP50_FILENAME = "top50_aindex_scheme18.csv"
EXACT_FULL_RANKING_FILENAME = "full_rankings_exact_config_aindex_scheme18.csv"
EXACT_TOP50_FILENAME = "top50_exact_config_aindex_scheme18.csv"
SUMMARY_FILENAME = "aindex_scheme18_validation_summary.json"

SCORE_ALIASES: dict[str, tuple[str, ...]] = {
    "tau2-Bench Telecom": ("tau2-Bench Telecom", "τ²-Bench Telecom"),
    "τ²-Bench Telecom": ("τ²-Bench Telecom", "tau2-Bench Telecom"),
    "tau3-Banking": ("tau3-Banking", "τ³-Banking"),
    "τ³-Banking": ("τ³-Banking", "tau3-Banking"),
}


def _independent_policy_items() -> tuple[
    dict[str, tuple[benchmark_policy.BenchmarkPolicy, ...]],
    dict[str, tuple[benchmark_policy.BenchmarkPolicy, ...]],
]:
    core: dict[str, list[benchmark_policy.BenchmarkPolicy]] = {
        board_id: [] for board_id in BOARD_ORDER
    }
    extension: dict[str, list[benchmark_policy.BenchmarkPolicy]] = {
        board_id: [] for board_id in BOARD_ORDER
    }
    seen: dict[str, set[str]] = {board_id: set() for board_id in BOARD_ORDER}
    for policy in benchmark_policy.BENCHMARK_POLICIES:
        if policy.tier == "core" and policy.publication_eligible:
            for board_id in policy.boards:
                core[board_id].append(policy)
        if policy.tier == "extension" and policy.publication_eligible:
            for board_id in policy.boards:
                extension[board_id].append(policy)
                seen[board_id].add(policy.canonical_family)
    for policy in benchmark_policy.BENCHMARK_POLICIES:
        if not (
            policy.tier == "conditional_extension"
            and policy.exploration_eligible
            and policy.controller_is_ranked_model_vendor is False
        ):
            continue
        for board_id in policy.boards:
            if policy.canonical_family in seen[board_id]:
                continue
            extension[board_id].append(policy)
            seen[board_id].add(policy.canonical_family)
    return (
        {board_id: tuple(rows) for board_id, rows in core.items()},
        {board_id: tuple(rows) for board_id, rows in extension.items()},
    )


CORE_POLICIES, EXTENSION_POLICIES = _independent_policy_items()


def finite(value: Any) -> float | None:
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
        value = finite(scores.get(alias))
        if value is not None:
            return value
    return None


def matrix(
    models: Sequence[Mapping[str, Any]],
    keys: Sequence[str],
) -> np.ndarray:
    return np.asarray(
        [[score_value(model, key) for key in keys] for model in models],
        dtype=float,
    )


def geometric_core(raw: np.ndarray) -> np.ndarray:
    if raw.ndim != 2 or raw.shape[1] == 0 or np.any(~np.isfinite(raw)):
        raise AssertionError("independent validator found incomplete core data")
    scaled = np.clip(raw, 1e-6, 100.0) / 100.0
    return 100.0 * np.exp(np.mean(np.log(scaled), axis=1))


def fit_trends(
    core: np.ndarray,
    extensions: np.ndarray,
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    residuals = np.full(extensions.shape, np.nan, dtype=float)
    trends: list[dict[str, Any]] = []
    for column_index in range(extensions.shape[1]):
        y = extensions[:, column_index]
        observed = np.isfinite(y)
        count = int(np.sum(observed))
        if count < 5:
            trends.append(
                {
                    "enabled": False,
                    "observed_count": count,
                    "slope": None,
                    "intercept": None,
                }
            )
            continue
        x_obs = core[observed]
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
        predicted = np.clip(intercept + slope * core[observed], 0.0, 100.0)
        residuals[observed, column_index] = np.maximum(
            y_obs - predicted,
            0.0,
        )
        trends.append(
            {
                "enabled": True,
                "observed_count": count,
                "slope": slope,
                "intercept": intercept,
            }
        )
    return residuals, trends


def apply_trends(
    core: np.ndarray,
    extensions: np.ndarray,
    trends: Sequence[Mapping[str, Any]],
) -> np.ndarray:
    residuals = np.full(extensions.shape, np.nan, dtype=float)
    for column_index, trend in enumerate(trends):
        if not bool(trend.get("enabled")):
            continue
        slope = float(trend["slope"])
        intercept = float(trend["intercept"])
        y = extensions[:, column_index]
        observed = np.isfinite(y)
        predicted = np.clip(intercept + slope * core[observed], 0.0, 100.0)
        residuals[observed, column_index] = np.maximum(
            y[observed] - predicted,
            0.0,
        )
    return residuals


def bonuses(residuals: np.ndarray, cap: float) -> np.ndarray:
    result = np.zeros(residuals.shape[0], dtype=float)
    for index, row in enumerate(residuals):
        positive = np.sort(row[np.isfinite(row) & (row > 0.0)])[::-1]
        if len(positive):
            result[index] = min(
                cap,
                max(
                    0.0,
                    math.log1p(float(np.sum(np.expm1(positive)))),
                ),
            )
    return result


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _models_by_slug(
    models: Sequence[Mapping[str, Any]],
) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for model in models:
        slug = str(model.get("slug") or "")
        if not slug:
            continue
        if slug in result:
            raise AssertionError(f"duplicate model slug {slug!r}")
        result[slug] = model
    return result


def _recompute_calibration(
    models: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    ordered = sorted(
        models,
        key=lambda model: (
            str(model.get("creator") or ""),
            str(model.get("model") or ""),
        ),
    )
    board_residuals: dict[str, np.ndarray] = {}
    board_trends: dict[str, list[dict[str, Any]]] = {}
    positive_values: list[float] = []
    for board_id in BOARD_ORDER:
        core_keys = tuple(
            policy.score_key for policy in CORE_POLICIES[board_id]
        )
        extension_keys = tuple(
            policy.score_key for policy in EXTENSION_POLICIES[board_id]
        )
        core = geometric_core(matrix(ordered, core_keys))
        residuals, trends = fit_trends(core, matrix(ordered, extension_keys))
        board_residuals[board_id] = residuals
        board_trends[board_id] = trends
        positive = residuals[np.isfinite(residuals) & (residuals > 0.0)]
        positive_values.extend(float(value) for value in positive)
    pooled = np.asarray(positive_values, dtype=float)
    cap = float(np.mean(pooled) + math.sqrt(2.0) * np.std(pooled, ddof=0))
    return {
        "cap": cap,
        "mean": float(np.mean(pooled)),
        "sd": float(np.std(pooled, ddof=0)),
        "count": len(positive_values),
        "trends": board_trends,
    }


def _score_population(
    models: Sequence[Mapping[str, Any]],
    calibration: Mapping[str, Any],
) -> tuple[np.ndarray, dict[str, dict[str, np.ndarray]]]:
    cap = float(calibration["bonus_cap_per_board"])
    details: dict[str, dict[str, np.ndarray]] = {}
    points: list[np.ndarray] = []
    for board_id in BOARD_ORDER:
        core_keys = tuple(
            policy.score_key for policy in CORE_POLICIES[board_id]
        )
        extension_keys = tuple(
            policy.score_key for policy in EXTENSION_POLICIES[board_id]
        )
        core = geometric_core(matrix(models, core_keys))
        extension_raw = matrix(models, extension_keys)
        trends = calibration["boards"][board_id]["extension_items"]
        residuals = apply_trends(core, extension_raw, trends)
        bonus = bonuses(residuals, cap)
        score = np.minimum(100.0, core + bonus)
        board_points = score / 5.0
        points.append(board_points)
        details[board_id] = {
            "core": core,
            "bonus": bonus,
            "score": score,
            "points": board_points,
            "extension_coverage": np.sum(
                np.isfinite(extension_raw),
                axis=1,
            ).astype(int),
        }
    final = np.sum(np.column_stack(points), axis=1)
    return final, details


def _audit_rows(
    rows: Sequence[Mapping[str, Any]],
    models: Sequence[Mapping[str, Any]],
    calibration: Mapping[str, Any],
    *,
    label: str,
) -> dict[str, Any]:
    failures: list[str] = []
    maximum_numeric_error = 0.0
    scores, details = _score_population(models, calibration)
    expected_order = sorted(
        range(len(models)),
        key=lambda index: (
            -float(scores[index]),
            str(models[index].get("slug") or ""),
            str(models[index].get("model") or ""),
        ),
    )
    expected_slugs = [str(models[index].get("slug") or "") for index in expected_order]
    actual_slugs = [str(row.get("slug") or "") for row in rows]
    if actual_slugs != expected_slugs:
        failures.append(f"{label} order differs from independent unrounded score sort")

    index_by_slug = {
        str(model.get("slug") or ""): index for index, model in enumerate(models)
    }
    for position, row in enumerate(rows, start=1):
        slug = str(row.get("slug") or "")
        index = index_by_slug.get(slug)
        if index is None:
            failures.append(f"{label} row references unknown slug {slug!r}")
            continue
        if int(row.get("rank") or 0) != position:
            failures.append(f"{label} rank mismatch for {slug}")
        checks: list[tuple[str, float, float, float]] = [
            (
                "score_full_precision",
                float(row["score_full_precision"]),
                float(scores[index]),
                1e-12,
            ),
            (
                "points_sum_full_precision",
                float(row["points_sum_full_precision"]),
                float(scores[index]),
                1e-12,
            ),
            ("final_score", float(row["final_score"]), round(float(scores[index]), 6), 5e-7),
        ]
        for board_id in BOARD_ORDER:
            board = details[board_id]
            checks.extend(
                [
                    (
                        f"{board_id}_core_score",
                        float(row[f"{board_id}_core_score"]),
                        round(float(board["core"][index]), 6),
                        5e-7,
                    ),
                    (
                        f"{board_id}_extension_bonus",
                        float(row[f"{board_id}_extension_bonus"]),
                        round(float(board["bonus"][index]), 6),
                        5e-7,
                    ),
                    (
                        f"{board_id}_score_full_precision",
                        float(row[f"{board_id}_score_full_precision"]),
                        float(board["score"][index]),
                        1e-12,
                    ),
                    (
                        f"{board_id}_points_full_precision",
                        float(row[f"{board_id}_points_full_precision"]),
                        float(board["points"][index]),
                        1e-12,
                    ),
                ]
            )
            actual_coverage = int(row[f"{board_id}_extension_tests"])
            expected_coverage = int(board["extension_coverage"][index])
            if actual_coverage != expected_coverage:
                failures.append(
                    f"{label} {slug} {board_id} extension coverage mismatch"
                )
        for field, actual, expected, tolerance in checks:
            error = abs(actual - expected)
            maximum_numeric_error = max(maximum_numeric_error, error)
            if error > tolerance:
                failures.append(
                    f"{label} {slug} {field}: {actual:.17g} != "
                    f"{expected:.17g} (error {error:g})"
                )
    return {
        "row_count": len(rows),
        "maximum_numeric_error": maximum_numeric_error,
        "passed": not failures,
        "failures": failures,
    }


def _audit_top50(
    full_rows: Sequence[Mapping[str, Any]],
    top_rows: Sequence[Mapping[str, Any]],
    label: str,
) -> dict[str, Any]:
    expected = [str(row.get("slug") or "") for row in full_rows[:50]]
    actual = [str(row.get("slug") or "") for row in top_rows]
    passed = len(top_rows) == min(50, len(full_rows)) and actual == expected
    return {
        "row_count": len(top_rows),
        "is_full_ranking_prefix": passed,
        "passed": passed,
        "failures": [] if passed else [f"{label} Top 50 is not the full-ranking prefix"],
    }


def _audit_review_parity(
    rows: Sequence[Mapping[str, Any]],
    review_csv: Path | None,
) -> dict[str, Any]:
    if review_csv is None:
        return {
            "requested": False,
            "passed": True,
            "failures": [],
        }
    review_rows = read_csv(review_csv)
    failures: list[str] = []
    max_error = 0.0
    if len(rows) != len(review_rows):
        failures.append(
            f"production/review row count differs: {len(rows)} != {len(review_rows)}"
        )
    numeric_fields = ["score_full_precision", "points_sum_full_precision"]
    for board_id in BOARD_ORDER:
        numeric_fields.extend(
            [
                f"{board_id}_core_score",
                f"{board_id}_extension_bonus",
                f"{board_id}_extension_tests",
                f"{board_id}_score_full_precision",
                f"{board_id}_points_full_precision",
            ]
        )
    for production, review in zip(rows, review_rows):
        if (
            str(production.get("rank")) != str(review.get("rank"))
            or str(production.get("slug")) != str(review.get("slug"))
        ):
            failures.append("production/review rank or slug order differs")
            break
        for field in numeric_fields:
            error = abs(float(production[field]) - float(review[field]))
            max_error = max(max_error, error)
            if error > 1e-12:
                failures.append(
                    f"{production.get('slug')} {field} review parity error {error:g}"
                )
    return {
        "requested": True,
        "review_csv": str(review_csv),
        "review_rows": len(review_rows),
        "maximum_numeric_error": max_error,
        "passed": not failures,
        "failures": failures,
    }


def validate_production_outputs(
    *,
    input_path: Path = DEFAULT_INPUT,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    review_csv: Path | None = None,
    write_summary: bool = True,
) -> dict[str, Any]:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    summary_path = output_dir / SUMMARY_FILENAME
    serialized = json.loads(summary_path.read_text(encoding="utf-8"))
    calibration = serialized.get("calibration") or {}
    failures: list[str] = []
    if calibration.get("method_id") != METHOD_ID:
        failures.append("serialized calibration method_id is not Scheme 18")
    if calibration.get("candidate_id") != CANDIDATE_ID:
        failures.append("serialized calibration candidate_id changed")

    full_rows = read_csv(output_dir / FULL_RANKING_FILENAME)
    top50_rows = read_csv(output_dir / TOP50_FILENAME)
    exact_rows = read_csv(output_dir / EXACT_FULL_RANKING_FILENAME)
    exact_top50_rows = read_csv(output_dir / EXACT_TOP50_FILENAME)

    raw_by_slug = _models_by_slug(list(payload.get("models") or []))
    calibration_slugs = list(calibration.get("population_slugs") or [])
    missing_calibration = [slug for slug in calibration_slugs if slug not in raw_by_slug]
    if missing_calibration:
        failures.append(f"calibration slugs missing from payload: {missing_calibration[:5]}")
    calibration_models = [
        raw_by_slug[slug] for slug in calibration_slugs if slug in raw_by_slug
    ]
    recomputed = _recompute_calibration(calibration_models)
    cap_error = abs(
        float(calibration.get("bonus_cap_per_board") or math.nan)
        - recomputed["cap"]
    )
    calibration_failures: list[str] = []
    if cap_error > 1e-12:
        calibration_failures.append(f"shared cap error {cap_error:g}")
    if int(calibration.get("pooled_positive_residual_count") or -1) != recomputed["count"]:
        calibration_failures.append("pooled positive residual count differs")
    for field, expected_key in (
        ("pooled_positive_residual_mean", "mean"),
        ("pooled_positive_residual_population_sd", "sd"),
    ):
        if abs(float(calibration.get(field) or math.nan) - recomputed[expected_key]) > 1e-12:
            calibration_failures.append(f"{field} differs")
    for board_id in BOARD_ORDER:
        serialized_trends = calibration["boards"][board_id]["extension_items"]
        independent_trends = recomputed["trends"][board_id]
        if len(serialized_trends) != len(independent_trends):
            calibration_failures.append(f"{board_id} trend count differs")
            continue
        for position, (actual, expected) in enumerate(
            zip(serialized_trends, independent_trends, strict=True)
        ):
            if bool(actual.get("enabled")) != bool(expected.get("enabled")):
                calibration_failures.append(
                    f"{board_id} trend {position} enabled flag differs"
                )
            if int(actual.get("observed_count") or 0) != int(expected["observed_count"]):
                calibration_failures.append(
                    f"{board_id} trend {position} observed count differs"
                )
            for field in ("slope", "intercept"):
                actual_value = finite(actual.get(field))
                expected_value = finite(expected.get(field))
                if actual_value is None and expected_value is None:
                    continue
                if (
                    actual_value is None
                    or expected_value is None
                    or abs(actual_value - expected_value) > 1e-12
                ):
                    calibration_failures.append(
                        f"{board_id} trend {position} {field} differs"
                    )
    calibration_audit = {
        "population_size": len(calibration_models),
        "cap": recomputed["cap"],
        "serialized_cap": calibration.get("bonus_cap_per_board"),
        "cap_error": cap_error,
        "passed": not calibration_failures,
        "failures": calibration_failures,
    }

    group_models = [raw_by_slug[str(row["slug"])] for row in full_rows]
    exact_sanitized, exact_sanitation = evidence.sanitize_models(
        payload,
        exact_config_only=True,
    )
    exact_by_slug = _models_by_slug(exact_sanitized)
    missing_exact = [
        str(row.get("slug") or "")
        for row in exact_rows
        if str(row.get("slug") or "") not in exact_by_slug
    ]
    if missing_exact:
        failures.append(f"exact slugs missing after sanitation: {missing_exact[:5]}")
    exact_models = [
        exact_by_slug[str(row["slug"])]
        for row in exact_rows
        if str(row["slug"]) in exact_by_slug
    ]

    group_audit = _audit_rows(
        full_rows,
        group_models,
        calibration,
        label="variant-group",
    )
    exact_audit = _audit_rows(
        exact_rows,
        exact_models,
        calibration,
        label="exact-config",
    )
    top50_audit = _audit_top50(full_rows, top50_rows, "variant-group")
    exact_top50_audit = _audit_top50(exact_rows, exact_top50_rows, "exact-config")
    review_audit = _audit_review_parity(full_rows, review_csv)

    policy_failures: list[str] = []
    for board_id in BOARD_ORDER:
        for policy in CORE_POLICIES[board_id]:
            if policy.controller_is_ranked_model_vendor is not False:
                policy_failures.append(
                    f"core controller conflict: {policy.item_id}"
                )
        for policy in EXTENSION_POLICIES[board_id]:
            if policy.controller_is_ranked_model_vendor is not False:
                policy_failures.append(
                    f"extension controller conflict: {policy.item_id}"
                )
    policy_audit = {
        "passed": not policy_failures,
        "failures": policy_failures,
    }

    component_results = (
        calibration_audit,
        group_audit,
        exact_audit,
        top50_audit,
        exact_top50_audit,
        review_audit,
        policy_audit,
    )
    all_failures = [
        *failures,
        *[
            failure
            for result in component_results
            for failure in result.get("failures", [])
        ],
    ]
    result = {
        "method_id": METHOD_ID,
        "candidate_id": CANDIDATE_ID,
        "independent_of_production_scoring_module": True,
        "exact_reuses_serialized_deduplicated_calibration": True,
        "calibration": calibration_audit,
        "variant_group": group_audit,
        "variant_group_top50": top50_audit,
        "exact_config": exact_audit,
        "exact_config_top50": exact_top50_audit,
        "exact_config_sanitation": exact_sanitation,
        "review_parity": review_audit,
        "benchmark_policy": policy_audit,
        "passed": not all_failures,
        "failures": all_failures,
    }
    if write_summary:
        serialized["independent_validation"] = result
        summary_path.write_text(
            json.dumps(serialized, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return result


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--review-csv", type=Path)
    parser.add_argument("--no-write-summary", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    result = validate_production_outputs(
        input_path=args.input,
        output_dir=args.output_dir,
        review_csv=args.review_csv,
        write_summary=not args.no_write_summary,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
