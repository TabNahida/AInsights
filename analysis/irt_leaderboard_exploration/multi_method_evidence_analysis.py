"""Multi-method evidence measurement with an explicit publication-order layer.

All primary methods use the same sanitized model-by-benchmark matrix.  There
are no product-order constraints, named-model adjustments, model-specific
weights, or fixed missing-score penalties.  The five boards receive equal
weight wherever boards are aggregated.  Coverage only controls eligibility
and the Main/Provisional evidence label.

User-facing candidate rankings are derived from those untouched evidence
rankings by one transparent publication rule: Claude Fable 5 is first and
GPT-5.6 Sol is second.  Scores are never changed, the original rank is retained
as ``evidence_rank``, and every other model keeps its evidence-order position
relative to the other non-anchor models.

The repository contains benchmark-level aggregate scores rather than
question-level responses, so the Rasch and 2PL methods below are continuous
benchmark-as-item approximations.  They are point estimates, not Bayesian
posterior means.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import warnings
from collections import OrderedDict
from pathlib import Path
from statistics import NormalDist
from typing import Any

import numpy as np

try:
    from . import evidence_only_ranking_analysis as evidence
    from . import irt_leaderboard_analysis as base
except ImportError:  # Direct script execution.
    import evidence_only_ranking_analysis as evidence
    import irt_leaderboard_analysis as base


ANALYSIS_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = evidence.DEFAULT_INPUT
DEFAULT_OUTPUT_DIR = ANALYSIS_DIR / "outputs"

ITEM_MIN_MODELS = 8
SPARSE_ITEM_MIN_MODELS = 3
DENSE_ITEM_MIN_MODELS = 20
MAIN_TESTS_PER_BOARD = 3
PROVISIONAL_MIN_TESTS_PER_BOARD = 2
TWOPL_SLOPE_RIDGE = 8.0

METHOD_LABELS: OrderedDict[str, str] = OrderedDict(
    [
        (
            "rasch_equal_board",
            "Unweighted continuous 1PL/Rasch point estimate; five boards equal",
        ),
        (
            "twopl_equal_board",
            "Unweighted continuous 2PL point estimate; five boards equal",
        ),
        (
            "percentile_mean_equal_board",
            "Equal item-percentile mean within board; five boards equal",
        ),
        (
            "percentile_median_equal_board",
            "Equal item-percentile median within board; five boards equal",
        ),
        (
            "global_family_percentile",
            "One equal vote per canonical benchmark family globally",
        ),
        (
            "rasch_sparse_item_sensitivity",
            "1PL/Rasch sensitivity including benchmark items seen for at least 3 models",
        ),
        (
            "rasch_dense_item_sensitivity",
            "1PL/Rasch sensitivity using benchmark items seen for at least 20 models",
        ),
    ]
)

CONSENSUS_METHOD = "rasch_main_sparse_rank_mean"
CONSENSUS_METHOD_LABEL = (
    "Equal mean of the primary Rasch and sparse-item Rasch evidence ranks"
)
CONSENSUS_COMPONENT_METHODS: tuple[str, str] = (
    "rasch_equal_board",
    "rasch_sparse_item_sensitivity",
)
CONSENSUS_DISPLAY_METHODS: tuple[str, str] = (
    "twopl_equal_board",
    "rasch_dense_item_sensitivity",
)

PUBLICATION_RULE_ID = "fable5_first_gpt56sol_second_v1"
REQUIRED_PUBLICATION_ORDER: tuple[tuple[str, str, str], ...] = (
    ("fable_5", "slug", "claude-fable-5"),
    ("gpt_5_6_sol", "variant_group", "gpt 5 6 sol"),
)


def prepare_common_matrix(
    models: list[dict[str, Any]],
    *,
    item_min_models: int = ITEM_MIN_MODELS,
    item_min_creators: int = 3,
) -> dict[str, dict[str, Any]]:
    """Build the common matrix using independent groups, not config-row count.

    The base helper first applies the cheap row-count prefilter.  This function
    then requires the requested number of distinct ``variantGroup`` values and
    creators so a provider with many effort settings cannot make one benchmark
    look broadly observed.
    """

    original_items = base.BOARD_ITEMS
    original_min = base.ITEM_MIN_MODELS
    try:
        base.BOARD_ITEMS = evidence.EVIDENCE_BOARD_ITEMS
        base.ITEM_MIN_MODELS = item_min_models
        boards = base.prepare_board_data(models)
    finally:
        base.BOARD_ITEMS = original_items
        base.ITEM_MIN_MODELS = original_min

    for board in boards.values():
        raw = np.asarray(board["raw"], dtype=float)
        keep: list[bool] = []
        variant_group_counts: list[int] = []
        creator_counts: list[int] = []
        for item_index in range(raw.shape[1]):
            observed_indexes = np.flatnonzero(np.isfinite(raw[:, item_index]))
            variant_groups = {
                str(
                    models[index].get("variantGroup")
                    or models[index].get("slug")
                    or models[index].get("model")
                    or index
                )
                for index in observed_indexes
            }
            creators = {
                str(models[index].get("creator") or "unknown")
                for index in observed_indexes
            }
            variant_group_counts.append(len(variant_groups))
            creator_counts.append(len(creators))
            keep.append(
                len(variant_groups) >= item_min_models
                and len(creators) >= item_min_creators
            )

        keep_array = np.asarray(keep, dtype=bool)
        for item_index, selected in enumerate(keep):
            if selected:
                continue
            spec = board["items"][item_index]
            board["excluded_items"].append(
                {
                    "id": spec["id"],
                    "label": spec["label"],
                    "n_obs": int(board["n_obs"][item_index]),
                    "n_variant_groups": variant_group_counts[item_index],
                    "n_creators": creator_counts[item_index],
                    "reason": (
                        f"fewer than {item_min_models} independent variant groups "
                        f"or {item_min_creators} creators"
                    ),
                }
            )
        board["items"] = [
            spec
            for spec, selected in zip(board["items"], keep, strict=True)
            if selected
        ]
        for key in (
            "raw",
            "probabilities",
            "logits",
            "n_obs",
            "reliability",
            "coverage_eligible",
        ):
            value = np.asarray(board[key])
            board[key] = value[:, keep_array] if value.ndim == 2 else value[keep_array]
        board["n_variant_groups"] = np.asarray(variant_group_counts, dtype=int)[
            keep_array
        ]
        board["n_creators"] = np.asarray(creator_counts, dtype=int)[keep_array]
    return boards


def standardize_active(values: np.ndarray, active: np.ndarray) -> np.ndarray:
    result = np.zeros_like(values, dtype=float)
    if not np.any(active):
        return result
    center = float(np.mean(values[active]))
    scale = float(np.std(values[active]))
    if not math.isfinite(scale) or scale < 1e-9:
        scale = 1.0
    result[active] = (values[active] - center) / scale
    return result


def cdf_scores(values: np.ndarray) -> np.ndarray:
    normal = NormalDist()
    return np.asarray(
        [100.0 * normal.cdf(float(value)) for value in values], dtype=float
    )


def fit_unweighted_rasch(board: dict[str, Any]) -> dict[str, np.ndarray]:
    """Fit z_ij = theta_i - difficulty_j with every observed cell equal."""

    z = np.asarray(board["logits"], dtype=float)
    observed = np.isfinite(z)
    response_counts = np.sum(observed, axis=1).astype(int)
    theta = np.zeros(z.shape[0], dtype=float)
    difficulty = np.zeros(z.shape[1], dtype=float)

    for _ in range(500):
        previous = theta.copy()
        for model_index in range(z.shape[0]):
            mask = observed[model_index]
            if np.any(mask):
                theta[model_index] = float(
                    np.mean(z[model_index, mask] + difficulty[mask])
                )
        active = response_counts > 0
        shift = float(np.mean(theta[active])) if np.any(active) else 0.0
        theta[active] -= shift
        difficulty += shift
        for item_index in range(z.shape[1]):
            mask = observed[:, item_index]
            if np.any(mask):
                difficulty[item_index] = float(
                    np.mean(theta[mask] - z[mask, item_index])
                )
        if float(np.max(np.abs(theta - previous))) < 1e-10:
            break

    active = response_counts > 0
    theta = standardize_active(theta, active)
    return {
        "theta": theta,
        "scores": cdf_scores(theta),
        "response_counts": response_counts,
        "difficulty": difficulty,
    }


def fit_unweighted_twopl(board: dict[str, Any]) -> dict[str, np.ndarray]:
    """Fit a model-anonymous 2PL with equal cells and common slope ridge.

    The item-slope ridge is identical for every benchmark and stabilizes the
    discrimination estimate around the 1PL value of one.  There is no model
    ridge, coverage term, lower-confidence-bound subtraction, or named-model
    parameter.
    """

    z = np.asarray(board["logits"], dtype=float)
    observed = np.isfinite(z)
    response_counts = np.sum(observed, axis=1).astype(int)
    theta = np.asarray(fit_unweighted_rasch(board)["theta"], dtype=float)
    discrimination = np.ones(z.shape[1], dtype=float)
    intercept = np.zeros(z.shape[1], dtype=float)

    for _ in range(250):
        previous = theta.copy()
        for item_index in range(z.shape[1]):
            mask = observed[:, item_index]
            x = theta[mask]
            y = z[mask, item_index]
            if not len(y):
                continue
            x_centered = x - float(np.mean(x))
            y_centered = y - float(np.mean(y))
            denominator = float(np.sum(np.square(x_centered))) + TWOPL_SLOPE_RIDGE
            numerator = float(np.sum(x_centered * y_centered)) + TWOPL_SLOPE_RIDGE
            slope = float(np.clip(numerator / denominator, 0.35, 2.5))
            discrimination[item_index] = slope
            intercept[item_index] = float(np.mean(y - slope * x))

        for model_index in range(z.shape[0]):
            mask = observed[model_index]
            if not np.any(mask):
                continue
            slopes = discrimination[mask]
            denominator = float(np.sum(np.square(slopes)))
            theta[model_index] = float(
                np.sum(slopes * (z[model_index, mask] - intercept[mask]))
                / max(denominator, 1e-12)
            )
        active = response_counts > 0
        shift = float(np.mean(theta[active])) if np.any(active) else 0.0
        theta[active] -= shift
        intercept += discrimination * shift
        if float(np.max(np.abs(theta - previous))) < 1e-10:
            break

    active = response_counts > 0
    theta = standardize_active(theta, active)
    return {
        "theta": theta,
        "scores": cdf_scores(theta),
        "response_counts": response_counts,
        "discrimination": discrimination,
        "intercept": intercept,
    }


def empirical_percentiles(raw: np.ndarray) -> np.ndarray:
    """Return within-item empirical percentiles; higher raw values are better."""

    result = np.full(raw.shape, np.nan, dtype=float)
    for item_index in range(raw.shape[1]):
        mask = np.isfinite(raw[:, item_index])
        values = raw[mask, item_index]
        if len(values):
            result[mask, item_index] = (
                base.average_tie_ranks(values) - 0.5
            ) / len(values) * 100.0
    return result


def board_percentile_scores(
    board_data: dict[str, dict[str, Any]],
    *,
    reducer: str,
) -> dict[str, np.ndarray]:
    scores: dict[str, np.ndarray] = {}
    for board_id in base.BOARD_ORDER:
        percentiles = empirical_percentiles(
            np.asarray(board_data[board_id]["raw"], dtype=float)
        )
        with warnings.catch_warnings(), np.errstate(invalid="ignore"):
            warnings.simplefilter("ignore", category=RuntimeWarning)
            if reducer == "mean":
                values = np.nanmean(percentiles, axis=1)
            elif reducer == "median":
                values = np.nanmedian(percentiles, axis=1)
            else:  # pragma: no cover - protected by internal callers.
                raise ValueError(f"unknown reducer: {reducer}")
        scores[board_id] = values
    return scores


def equal_board_mean(board_scores: dict[str, np.ndarray]) -> np.ndarray:
    """Arithmetic mean with an exact 1/5 share for every board."""

    return np.mean(
        np.column_stack([board_scores[board_id] for board_id in base.BOARD_ORDER]),
        axis=1,
    )


def global_family_percentiles(
    board_data: dict[str, dict[str, Any]],
) -> tuple[np.ndarray, np.ndarray]:
    """Average each canonical benchmark family once, without board weights."""

    family_columns: OrderedDict[str, np.ndarray] = OrderedDict()
    for board_id in base.BOARD_ORDER:
        board = board_data[board_id]
        percentiles = empirical_percentiles(np.asarray(board["raw"], dtype=float))
        for item_index, spec in enumerate(board["items"]):
            family = str(spec.get("family") or spec["id"])
            if family not in family_columns:
                family_columns[family] = percentiles[:, item_index]
    matrix = np.column_stack(list(family_columns.values()))
    with warnings.catch_warnings(), np.errstate(invalid="ignore"):
        warnings.simplefilter("ignore", category=RuntimeWarning)
        scores = np.nanmean(matrix, axis=1)
    counts = np.sum(np.isfinite(matrix), axis=1).astype(int)
    return scores, counts


def coverage_profile(
    board_data: dict[str, dict[str, Any]],
) -> tuple[np.ndarray, np.ndarray]:
    board_counts: list[np.ndarray] = []
    family_presence: OrderedDict[str, np.ndarray] = OrderedDict()
    for board_id in base.BOARD_ORDER:
        board = board_data[board_id]
        observed = np.isfinite(np.asarray(board["raw"], dtype=float))
        board_family_presence: OrderedDict[str, np.ndarray] = OrderedDict()
        for item_index, spec in enumerate(board["items"]):
            family = str(spec.get("family") or spec["id"])
            item_observed = observed[:, item_index]
            if family in board_family_presence:
                board_family_presence[family] |= item_observed
            else:
                board_family_presence[family] = item_observed.copy()
            if family in family_presence:
                family_presence[family] |= item_observed
            else:
                family_presence[family] = item_observed.copy()
        board_counts.append(
            np.sum(
                np.column_stack(list(board_family_presence.values())), axis=1
            ).astype(int)
        )
    total_unique = np.sum(
        np.column_stack(list(family_presence.values())), axis=1
    ).astype(int)
    return np.column_stack(board_counts), total_unique


def competition_ranks(values: np.ndarray) -> np.ndarray:
    return evidence.competition_ranks(values)


def method_rows(
    *,
    method: str,
    models: list[dict[str, Any]],
    scores: np.ndarray,
    board_scores: dict[str, np.ndarray],
    coverage: np.ndarray,
    unique_families: np.ndarray,
    eligible: np.ndarray,
    main_evidence: np.ndarray,
    method_scope: str,
) -> list[dict[str, Any]]:
    selected = evidence.choose_score_best_variant(models, eligible, scores)
    selected_values = np.asarray([scores[index] for index in selected], dtype=float)
    ranks = competition_ranks(selected_values)

    rows: list[dict[str, Any]] = []
    for position, index in enumerate(selected):
        counts = coverage[index]
        row: dict[str, Any] = {
            "method": method,
            "method_label": METHOD_LABELS[method],
            "method_scope": method_scope,
            "rank": int(ranks[position]),
            "model": str(models[index].get("model") or ""),
            "creator": str(models[index].get("creator") or ""),
            "slug": str(models[index].get("slug") or ""),
            "variant_group": str(models[index].get("variantGroup") or ""),
            "evidence_tier": "Main" if main_evidence[index] else "Provisional",
            "score": base.rounded(float(scores[index]), 4),
            "unique_benchmark_families": int(unique_families[index]),
            "board_test_slots_total": int(np.sum(counts)),
            "min_board_tests": int(np.min(counts)),
            "boards_below_main_target": int(
                np.sum(counts < MAIN_TESTS_PER_BOARD)
            ),
        }
        for board_position, board_id in enumerate(base.BOARD_ORDER):
            row[f"{board_id}_tests"] = int(counts[board_position])
            row[f"{board_id}_score"] = base.rounded(
                float(board_scores[board_id][index]), 3
            )
        rows.append(row)
    rows.sort(key=lambda row: (int(row["rank"]), str(row["model"])))
    return rows


def board_item_pool_sizes(
    board_data: dict[str, dict[str, Any]],
) -> dict[str, int]:
    """Return the canonical-family pool size used for each board.

    Coverage counts elsewhere in this module are canonical-family counts, so
    the matching denominator must also deduplicate item slots that belong to
    the same benchmark family.
    """

    return {
        board_id: len(
            {
                str(spec.get("family") or spec["id"])
                for spec in board_data[board_id]["items"]
            }
        )
        for board_id in base.BOARD_ORDER
    }


def normalized_rank_percentile(rank: float, population: int) -> float:
    """Map a rank to 0--100 for display without treating it as ability."""

    if population <= 1:
        return 100.0
    return 100.0 * (population - rank) / (population - 1)


def _ranking_by_variant_group(
    rows: list[dict[str, Any]],
    *,
    method: str,
) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        group = str(row.get("variant_group") or "")
        if not group:
            raise ValueError(f"{method} row has no variant_group")
        if group in indexed:
            raise ValueError(f"{method} has duplicate variant_group {group!r}")
        indexed[group] = row
    return indexed


def _consensus_component(
    row: dict[str, Any] | None,
    *,
    population: int,
) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        "method": str(row.get("method") or ""),
        "rank": int(row["rank"]),
        "score": row.get("score"),
        "rank_percentile": base.rounded(
            normalized_rank_percentile(float(row["rank"]), population), 4
        ),
        "selected_slug": str(row.get("slug") or ""),
        "evidence_tier": str(row.get("evidence_tier") or ""),
        "board_scores": {
            board_id: row.get(f"{board_id}_score")
            for board_id in base.BOARD_ORDER
        },
        "board_tests": {
            board_id: int(row.get(f"{board_id}_tests") or 0)
            for board_id in base.BOARD_ORDER
        },
    }


def build_rasch_rank_consensus(
    full_rankings: dict[str, list[dict[str, Any]]],
    *,
    main_pool_sizes: dict[str, int],
    sparse_pool_sizes: dict[str, int],
) -> list[dict[str, Any]]:
    """Build the equal-rank Rasch consensus before publication ordering.

    The two component populations and selected exact configurations must match
    exactly.  Missing components are not imputed and no fixed rank penalty is
    introduced.  Ties in the arithmetic rank mean use a symmetric consensus
    key: lower worst component rank, then lower best component rank, then the
    stable row identifier.
    """

    main_method, sparse_method = CONSENSUS_COMPONENT_METHODS
    main_rows = full_rankings[main_method]
    sparse_rows = full_rankings[sparse_method]
    main_by_group = _ranking_by_variant_group(main_rows, method=main_method)
    sparse_by_group = _ranking_by_variant_group(
        sparse_rows, method=sparse_method
    )
    main_groups = set(main_by_group)
    sparse_groups = set(sparse_by_group)
    if main_groups != sparse_groups:
        only_main = sorted(main_groups - sparse_groups)
        only_sparse = sorted(sparse_groups - main_groups)
        raise ValueError(
            "Rasch consensus requires identical variant-group populations; "
            f"only primary={only_main[:5]!r}, only sparse={only_sparse[:5]!r}"
        )

    component_maps = {
        method: _ranking_by_variant_group(full_rankings[method], method=method)
        for method in (*CONSENSUS_COMPONENT_METHODS, *CONSENSUS_DISPLAY_METHODS)
    }
    component_populations = {
        method: len(rows) for method, rows in full_rankings.items()
    }
    pool_sizes = {
        main_method: dict(main_pool_sizes),
        sparse_method: dict(sparse_pool_sizes),
    }

    rows: list[dict[str, Any]] = []
    for group in main_groups:
        main = main_by_group[group]
        sparse = sparse_by_group[group]
        if ranking_row_id(main) != ranking_row_id(sparse):
            raise ValueError(
                "Rasch consensus cannot mix exact configurations for "
                f"{group!r}: primary={main.get('slug')!r}, "
                f"sparse={sparse.get('slug')!r}"
            )

        main_rank = int(main["rank"])
        sparse_rank = int(sparse["rank"])
        rank_mean = (main_rank + sparse_rank) / 2.0
        rank_min = min(main_rank, sparse_rank)
        rank_max = max(main_rank, sparse_rank)
        main_score = float(main["score"])
        sparse_score = float(sparse["score"])
        evidence_tier = (
            "Main"
            if main.get("evidence_tier") == "Main"
            and sparse.get("evidence_tier") == "Main"
            else "Provisional"
        )

        row: dict[str, Any] = {
            "method": CONSENSUS_METHOD,
            "method_label": CONSENSUS_METHOD_LABEL,
            "method_scope": "primary_rank_consensus",
            # Assigned after the symmetric consensus sort below.
            "rank": 0,
            "model": str(main.get("model") or ""),
            "creator": str(main.get("creator") or ""),
            "slug": str(main.get("slug") or ""),
            "variant_group": group,
            "evidence_tier": evidence_tier,
            "score": base.rounded((main_score + sparse_score) / 2.0, 4),
            "score_role": "diagnostic_equal_mean_not_ranking_key",
            "rank_mean": base.rounded(rank_mean, 4),
            "rank_min": rank_min,
            "rank_max": rank_max,
            "rank_span": rank_max - rank_min,
            "rank_tie_break_policy": "lower_rank_max_then_rank_min_then_stable_id",
            "rasch_rank": main_rank,
            "rasch_score": main["score"],
            "sparse_rasch_rank": sparse_rank,
            "sparse_rasch_score": sparse["score"],
            "main_unique_benchmark_families": int(
                main["unique_benchmark_families"]
            ),
            "sparse_unique_benchmark_families": int(
                sparse["unique_benchmark_families"]
            ),
            "unique_benchmark_families": min(
                int(main["unique_benchmark_families"]),
                int(sparse["unique_benchmark_families"]),
            ),
            "board_item_pool_sizes": pool_sizes,
        }

        component_methods: dict[str, dict[str, Any] | None] = {}
        for method in (
            *CONSENSUS_COMPONENT_METHODS,
            *CONSENSUS_DISPLAY_METHODS,
        ):
            component_row = component_maps[method].get(group)
            component = _consensus_component(
                component_row,
                population=component_populations[method],
            )
            component_methods[method] = component

        twopl = component_maps["twopl_equal_board"].get(group)
        dense = component_maps["rasch_dense_item_sensitivity"].get(group)
        row.update(
            {
                "twopl_rank": int(twopl["rank"]) if twopl else None,
                "twopl_score": twopl.get("score") if twopl else None,
                "dense_rasch_rank": int(dense["rank"]) if dense else None,
                "dense_rasch_score": dense.get("score") if dense else None,
                "component_methods": component_methods,
            }
        )

        board_coverages: list[float] = []
        board_tests_total = 0
        board_below_main = 0
        min_board_tests: int | None = None
        for board_id in base.BOARD_ORDER:
            main_board_score = float(main[f"{board_id}_score"])
            sparse_board_score = float(sparse[f"{board_id}_score"])
            main_tests = int(main[f"{board_id}_tests"])
            sparse_tests = int(sparse[f"{board_id}_tests"])
            conservative_tests = min(main_tests, sparse_tests)
            board_tests_total += conservative_tests
            min_board_tests = (
                conservative_tests
                if min_board_tests is None
                else min(min_board_tests, conservative_tests)
            )
            if conservative_tests < MAIN_TESTS_PER_BOARD:
                board_below_main += 1

            main_denominator = int(main_pool_sizes[board_id])
            sparse_denominator = int(sparse_pool_sizes[board_id])
            if main_denominator <= 0 or sparse_denominator <= 0:
                raise ValueError(f"empty item pool for consensus board {board_id!r}")
            main_coverage = min(max(main_tests / main_denominator, 0.0), 1.0)
            sparse_coverage = min(
                max(sparse_tests / sparse_denominator, 0.0), 1.0
            )
            board_coverage_score = 100.0 * (
                main_coverage + sparse_coverage
            ) / 2.0
            board_coverages.append(board_coverage_score)

            row[f"{board_id}_score"] = base.rounded(
                (main_board_score + sparse_board_score) / 2.0, 3
            )
            row[f"{board_id}_tests"] = conservative_tests
            row[f"{board_id}_rasch_score"] = main[f"{board_id}_score"]
            row[f"{board_id}_sparse_rasch_score"] = sparse[
                f"{board_id}_score"
            ]
            row[f"{board_id}_rasch_tests"] = main_tests
            row[f"{board_id}_sparse_rasch_tests"] = sparse_tests
            row[f"{board_id}_main_item_pool_size"] = main_denominator
            row[f"{board_id}_sparse_item_pool_size"] = sparse_denominator
            row[f"{board_id}_evidence_coverage_score"] = base.rounded(
                board_coverage_score, 3
            )
            row[f"{board_id}_twopl_score"] = (
                twopl.get(f"{board_id}_score") if twopl else None
            )
            row[f"{board_id}_twopl_tests"] = (
                int(twopl[f"{board_id}_tests"]) if twopl else None
            )
            row[f"{board_id}_dense_rasch_score"] = (
                dense.get(f"{board_id}_score") if dense else None
            )
            row[f"{board_id}_dense_rasch_tests"] = (
                int(dense[f"{board_id}_tests"]) if dense else None
            )

        row["board_test_slots_total"] = board_tests_total
        row["min_board_tests"] = int(min_board_tests or 0)
        row["boards_below_main_target"] = board_below_main
        row["evidence_coverage_score"] = base.rounded(
            float(np.mean(board_coverages)), 3
        )
        rows.append(row)

    rows.sort(
        key=lambda row: (
            float(row["rank_mean"]),
            int(row["rank_max"]),
            int(row["rank_min"]),
            ranking_row_id(row),
        )
    )
    population = len(rows)
    for position, row in enumerate(rows, start=1):
        row["rank"] = position
        row["rank_percentile"] = base.rounded(
            normalized_rank_percentile(float(row["rank_mean"]), population),
            4,
        )
    return rows


def apply_required_publication_order(
    evidence_rows: list[dict[str, Any]],
    *,
    required_order: tuple[tuple[str, str, str], ...] = REQUIRED_PUBLICATION_ORDER,
    rule_id: str = PUBLICATION_RULE_ID,
) -> list[dict[str, Any]]:
    """Apply the required display order without changing evidence scores.

    Targets are matched only by stable identifiers.  A missing or ambiguous
    target is a hard failure so no candidate ranking can be emitted without
    satisfying the publication contract.
    """

    if any("evidence_rank" in row for row in evidence_rows):
        raise ValueError("publication order cannot be applied more than once")

    target_indexes: list[int] = []
    target_by_index: dict[int, str] = {}
    for target_id, field, expected in required_order:
        matches = [
            index
            for index, row in enumerate(evidence_rows)
            if str(row.get(field) or "") == expected
        ]
        if len(matches) != 1:
            raise ValueError(
                f"required publication target {target_id!r} matched "
                f"{len(matches)} rows via {field}={expected!r}"
            )
        index = matches[0]
        if index in target_by_index:
            raise ValueError(
                f"required publication targets {target_by_index[index]!r} and "
                f"{target_id!r} matched the same row"
            )
        target_indexes.append(index)
        target_by_index[index] = target_id

    target_index_set = set(target_indexes)
    ordered_indexes = target_indexes + [
        index
        for index in range(len(evidence_rows))
        if index not in target_index_set
    ]
    published: list[dict[str, Any]] = []
    for rank, index in enumerate(ordered_indexes, start=1):
        source = evidence_rows[index]
        evidence_rank = int(source["rank"])
        row = dict(source)
        row["rank"] = rank
        row["evidence_rank"] = evidence_rank
        row["rank_change_due_to_required_order"] = evidence_rank - rank
        row["publication_order_rule"] = rule_id
        row["required_order_target"] = target_by_index.get(index, "")
        published.append(row)
    return published


def ranking_row_id(row: dict[str, Any]) -> str:
    """Return a stable row identifier for publication-layer validation."""

    slug = str(row.get("slug") or "")
    if slug:
        return f"slug:{slug}"
    variant_group = str(row.get("variant_group") or "")
    if variant_group:
        return f"variant_group:{variant_group}"
    raise ValueError("ranking row has neither slug nor variant_group")


def validate_required_publication_rankings(
    evidence_rankings: dict[str, list[dict[str, Any]]],
    publication_rankings: dict[str, list[dict[str, Any]]],
    publication_top50: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    """Prove that every published method satisfies the required-order layer."""

    method_results: dict[str, dict[str, Any]] = {}
    methods = list(evidence_rankings)
    if set(methods) != set(publication_rankings) or set(methods) != set(
        publication_top50
    ):
        raise ValueError("publication validation method sets do not match")
    for method in methods:
        evidence_rows = evidence_rankings[method]
        published_rows = publication_rankings[method]
        top_rows = publication_top50[method]

        evidence_ids = [ranking_row_id(row) for row in evidence_rows]
        published_ids = [ranking_row_id(row) for row in published_rows]
        top_ids = [ranking_row_id(row) for row in top_rows]
        if len(set(evidence_ids)) != len(evidence_ids):
            raise ValueError(f"duplicate stable row identifier in {method} evidence")
        if len(set(published_ids)) != len(published_ids):
            raise ValueError(f"duplicate stable row identifier in {method} publication")

        evidence_by_id = dict(zip(evidence_ids, evidence_rows, strict=True))
        published_by_id = dict(zip(published_ids, published_rows, strict=True))
        same_population = set(evidence_ids) == set(published_ids)
        scores_unchanged = same_population and all(
            published_by_id[row_id]["score"] == evidence_by_id[row_id]["score"]
            for row_id in evidence_ids
        )
        evidence_ranks_retained = same_population and all(
            int(published_by_id[row_id]["evidence_rank"])
            == int(evidence_by_id[row_id]["rank"])
            for row_id in evidence_ids
        )

        anchor_ids: list[str] = []
        required_ranks: dict[str, int | None] = {}
        for expected_rank, (target_id, field, expected) in enumerate(
            REQUIRED_PUBLICATION_ORDER, start=1
        ):
            matches = [
                row
                for row in published_rows
                if str(row.get(field) or "") == expected
            ]
            required_ranks[target_id] = (
                int(matches[0]["rank"]) if len(matches) == 1 else None
            )
            if len(matches) == 1:
                anchor_ids.append(ranking_row_id(matches[0]))

        anchor_id_set = set(anchor_ids)
        evidence_other_order = [
            row_id for row_id in evidence_ids if row_id not in anchor_id_set
        ]
        publication_other_order = [
            row_id for row_id in published_ids if row_id not in anchor_id_set
        ]
        remaining_order_preserved = (
            evidence_other_order == publication_other_order
        )
        sequential_ranks = [int(row["rank"]) for row in published_rows] == list(
            range(1, len(published_rows) + 1)
        )
        top50_exact = (
            len(top_rows) == 50
            and top_ids == published_ids[:50]
            and [int(row["rank"]) for row in top_rows] == list(range(1, 51))
        )
        required_order_satisfied = all(
            required_ranks[target_id] == expected_rank
            for expected_rank, (target_id, _, _) in enumerate(
                REQUIRED_PUBLICATION_ORDER, start=1
            )
        )
        passed = all(
            (
                same_population,
                scores_unchanged,
                evidence_ranks_retained,
                remaining_order_preserved,
                sequential_ranks,
                top50_exact,
                required_order_satisfied,
            )
        )
        method_results[method] = {
            "passed": passed,
            "top50_rows": len(top_rows),
            "required_ranks": required_ranks,
            "same_population": same_population,
            "scores_unchanged": scores_unchanged,
            "evidence_ranks_retained": evidence_ranks_retained,
            "remaining_evidence_order_preserved": remaining_order_preserved,
            "sequential_publication_ranks": sequential_ranks,
            "top50_is_full_ranking_prefix": top50_exact,
        }

    return {
        "publication_order_rule": PUBLICATION_RULE_ID,
        "required_order": [
            {
                "rank": rank,
                "target": target_id,
                "stable_field": field,
                "stable_value": expected,
            }
            for rank, (target_id, field, expected) in enumerate(
                REQUIRED_PUBLICATION_ORDER, start=1
            )
        ],
        "method_count": len(method_results),
        "all_methods_pass": all(
            result["passed"] for result in method_results.values()
        ),
        "all_methods_have_50_rows": all(
            result["top50_rows"] == 50 for result in method_results.values()
        ),
        "all_scores_unchanged": all(
            result["scores_unchanged"] for result in method_results.values()
        ),
        "all_remaining_evidence_order_preserved": all(
            result["remaining_evidence_order_preserved"]
            for result in method_results.values()
        ),
        "methods": method_results,
    }


def direct_source_coverage(
    original_models: list[dict[str, Any]],
    sanitized_models: list[dict[str, Any]],
    board_data: dict[str, dict[str, Any]],
    external_sources: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Summarize first-party direct rows versus rows used by the common matrix."""

    sanitized_by_slug = {
        str(model.get("slug") or ""): model for model in sanitized_models
    }
    source_aliases = {
        str(source.get("id") or ""): {
            re.sub(r"[^a-z0-9]+", "", str(alias).lower())
            for alias in [
                *(source.get("modelAliases") or []),
                *(source.get("modelKeys") or []),
            ]
            if alias
        }
        for source in external_sources
    }
    used_metric_keys: set[str] = set()
    for board in board_data.values():
        for spec in board["items"]:
            used_metric_keys.update(str(key) for key in spec.get("keys", []))

    rows: list[dict[str, Any]] = []
    for model in original_models:
        slug = str(model.get("slug") or "")
        sanitized = sanitized_by_slug.get(slug)
        if sanitized is None:
            continue
        model_match_keys = {
            re.sub(r"[^a-z0-9]+", "", value.lower())
            for value in (
                str(model.get("model") or ""),
                str(model.get("slug") or ""),
            )
            if value
        }
        direct_entries = [
            entry
            for entry in model.get("externalBenchmarks", []) or []
            if not entry.get("sharedFromVariant")
            and entry.get("evidenceEligible") is not False
            and not evidence.derived_external_entry(entry)
            and bool(
                model_match_keys
                & source_aliases.get(str(entry.get("sourceId") or ""), set())
            )
        ]
        if not direct_entries:
            continue
        retained_keys = {
            str(entry.get("metricKey") or "")
            for entry in direct_entries
            if base.finite_number(
                sanitized.get("scores", {}).get(str(entry.get("metricKey") or ""))
            )
            is not None
        }
        used = retained_keys & used_metric_keys
        rows.append(
            {
                "model": str(model.get("model") or ""),
                "slug": slug,
                "creator": str(model.get("creator") or ""),
                "first_party_direct_rows": len(direct_entries),
                "first_party_direct_metric_families": len(retained_keys),
                "first_party_rows_in_common_protocol": len(used),
                "first_party_rows_outside_common_protocol": len(
                    retained_keys - used
                ),
                "first_party_source_ids": " | ".join(
                    sorted(
                        {
                            str(entry.get("sourceId") or "")
                            for entry in direct_entries
                            if entry.get("sourceId")
                        }
                    )
                ),
            }
        )
    rows.sort(key=lambda row: (str(row["model"]), str(row["slug"])))
    return rows


def target_method_rows(
    full_rankings: dict[str, list[dict[str, Any]]],
) -> dict[str, dict[str, dict[str, Any] | None]]:
    targets = OrderedDict(
        [
            ("fable_5", "Claude Fable 5"),
            ("gpt_5_6_sol", "GPT-5.6 Sol"),
            ("gpt_5_6_terra", "GPT-5.6 Terra"),
            ("gpt_5_6_luna", "GPT-5.6 Luna"),
            ("claude_opus_5", "Claude Opus 5"),
            ("deepseek_v4_flash_0731", "DeepSeek V4 Flash 0731"),
            ("qwen3_8_max", "Qwen3.8 Max"),
        ]
    )
    result: dict[str, dict[str, dict[str, Any] | None]] = {}
    for method, rows in full_rankings.items():
        result[method] = {}
        for target_id, prefix in targets.items():
            result[method][target_id] = next(
                (
                    {
                        "rank": row["rank"],
                        "model": row["model"],
                        "score": row["score"],
                        "evidence_tier": row["evidence_tier"],
                        "board_test_slots_total": row["board_test_slots_total"],
                    }
                    for row in rows
                    if str(row["model"]).startswith(prefix)
                ),
                None,
            )
    return result


def target_exact_config_rows(
    *,
    models: list[dict[str, Any]],
    method_scores: OrderedDict[str, np.ndarray],
    method_profiles: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Track fixed exact configurations so method comparisons do not switch effort."""

    targets = OrderedDict(
        [
            ("fable_5", ("claude-fable-5", "Claude Fable 5 (with fallback)")),
            ("gpt_5_6_sol", ("gpt-5-6-sol", "GPT-5.6 Sol (max)")),
            ("gpt_5_6_terra", ("gpt-5-6-terra", "GPT-5.6 Terra (max)")),
            ("gpt_5_6_luna", ("gpt-5-6-luna", "GPT-5.6 Luna (max)")),
            ("claude_opus_5", ("claude-opus-5", "Claude Opus 5 (max)")),
            (
                "deepseek_v4_flash_0731",
                ("deepseek-v4-flash", "DeepSeek V4 Flash 0731 (max)"),
            ),
            ("qwen3_8_max", ("qwen3-8-max", "Qwen3.8 Max")),
        ]
    )
    target_indexes: dict[str, int | None] = {}
    for target_id, (slug, model_name) in targets.items():
        target_indexes[target_id] = next(
            (
                index
                for index, model in enumerate(models)
                if str(model.get("slug") or "") == slug
                and str(model.get("model") or "") == model_name
            ),
            None,
        )

    rows: list[dict[str, Any]] = []
    for method, scores in method_scores.items():
        profile = method_profiles[method]
        eligible = np.asarray(profile["eligible"], dtype=bool)
        eligible_indexes = np.flatnonzero(eligible)
        ranks = competition_ranks(scores[eligible_indexes])
        rank_by_index = {
            int(index): int(ranks[position])
            for position, index in enumerate(eligible_indexes)
        }
        coverage = np.asarray(profile["coverage"], dtype=int)
        main = np.asarray(profile["main"], dtype=bool)
        for target_id, index in target_indexes.items():
            if index is None or index not in rank_by_index:
                rows.append(
                    {
                        "method": method,
                        "target": target_id,
                        "rank_among_exact_configs": None,
                        "model": None,
                        "slug": None,
                        "score": None,
                        "evidence_tier": None,
                        "board_test_slots_total": None,
                    }
                )
                continue
            rows.append(
                {
                    "method": method,
                    "target": target_id,
                    "rank_among_exact_configs": rank_by_index[index],
                    "model": str(models[index].get("model") or ""),
                    "slug": str(models[index].get("slug") or ""),
                    "score": base.rounded(float(scores[index]), 4),
                    "evidence_tier": "Main" if main[index] else "Provisional",
                    "board_test_slots_total": int(np.sum(coverage[index])),
                }
            )
    return rows


def method_stability_rows(
    full_rankings: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Report rank correlation and Top-50 overlap on common variant groups."""

    methods = list(full_rankings)
    rows: list[dict[str, Any]] = []
    for left_position, left in enumerate(methods):
        left_by_group = {
            str(row.get("variant_group") or row.get("slug")): row
            for row in full_rankings[left]
        }
        left_top = {
            str(row.get("variant_group") or row.get("slug"))
            for row in full_rankings[left][:50]
        }
        for right in methods[left_position:]:
            right_by_group = {
                str(row.get("variant_group") or row.get("slug")): row
                for row in full_rankings[right]
            }
            common = sorted(set(left_by_group) & set(right_by_group))
            left_ranks = np.asarray(
                [float(left_by_group[group]["rank"]) for group in common]
            )
            right_ranks = np.asarray(
                [float(right_by_group[group]["rank"]) for group in common]
            )
            if len(common) > 1:
                spearman = float(np.corrcoef(left_ranks, right_ranks)[0, 1])
            else:
                spearman = math.nan
            right_top = {
                str(row.get("variant_group") or row.get("slug"))
                for row in full_rankings[right][:50]
            }
            rows.append(
                {
                    "method_left": left,
                    "method_right": right,
                    "common_variant_groups": len(common),
                    "spearman_rank_correlation": base.rounded(spearman, 5),
                    "top50_overlap": len(left_top & right_top),
                }
            )
    return rows


def pairwise_overlap_rows(
    models: list[dict[str, Any]],
    board_data: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Expose the actual common benchmark evidence for two diagnostic pairs."""

    pairs = [
        ("sol_vs_opus", "GPT-5.6 Sol (max)", "Claude Opus 5 (max)"),
        (
            "luna_vs_deepseek",
            "GPT-5.6 Luna (max)",
            "DeepSeek V4 Flash 0731 (max)",
        ),
    ]
    model_indexes = {
        str(model.get("model") or ""): index for index, model in enumerate(models)
    }
    rows: list[dict[str, Any]] = []
    for pair_id, left_name, right_name in pairs:
        left_index = model_indexes[left_name]
        right_index = model_indexes[right_name]
        seen_families: set[str] = set()
        for board_id in base.BOARD_ORDER:
            board = board_data[board_id]
            raw = np.asarray(board["raw"], dtype=float)
            for item_index, spec in enumerate(board["items"]):
                family = str(spec.get("family") or spec["id"])
                if family in seen_families:
                    continue
                left_value = raw[left_index, item_index]
                right_value = raw[right_index, item_index]
                if not (math.isfinite(float(left_value)) and math.isfinite(float(right_value))):
                    continue
                seen_families.add(family)
                delta = float(left_value - right_value)
                winner = "tie"
                if delta > 1e-12:
                    winner = "left"
                elif delta < -1e-12:
                    winner = "right"
                rows.append(
                    {
                        "pair": pair_id,
                        "board": board_id,
                        "benchmark_family": family,
                        "benchmark": str(spec.get("label") or spec["id"]),
                        "left_model": left_name,
                        "left_value": base.rounded(float(left_value), 4),
                        "right_model": right_name,
                        "right_value": base.rounded(float(right_value), 4),
                        "left_minus_right": base.rounded(delta, 4),
                        "winner": winner,
                    }
                )
    return rows


def run_multi_method_analysis_from_payload(
    payload: dict[str, Any],
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write_outputs: bool = False,
) -> dict[str, Any]:
    """Analyze an in-memory site payload without reading the generated site file."""

    models, sanitation = evidence.sanitize_models(payload)
    board_data = prepare_common_matrix(models)
    coverage, unique_families = coverage_profile(board_data)
    eligible = np.all(coverage >= PROVISIONAL_MIN_TESTS_PER_BOARD, axis=1)
    main_evidence = np.all(coverage >= MAIN_TESTS_PER_BOARD, axis=1)

    rasch_fits = {
        board_id: fit_unweighted_rasch(board_data[board_id])
        for board_id in base.BOARD_ORDER
    }
    twopl_fits = {
        board_id: fit_unweighted_twopl(board_data[board_id])
        for board_id in base.BOARD_ORDER
    }
    percentile_mean_boards = board_percentile_scores(board_data, reducer="mean")
    percentile_median_boards = board_percentile_scores(
        board_data, reducer="median"
    )
    rasch_boards = {
        board_id: rasch_fits[board_id]["scores"] for board_id in base.BOARD_ORDER
    }
    twopl_boards = {
        board_id: twopl_fits[board_id]["scores"] for board_id in base.BOARD_ORDER
    }
    global_scores, global_counts = global_family_percentiles(board_data)

    sparse_board_data = prepare_common_matrix(
        models,
        item_min_models=SPARSE_ITEM_MIN_MODELS,
        item_min_creators=1,
    )
    sparse_coverage, sparse_unique_families = coverage_profile(sparse_board_data)
    sparse_eligible = np.all(
        sparse_coverage >= PROVISIONAL_MIN_TESTS_PER_BOARD, axis=1
    )
    sparse_main = np.all(sparse_coverage >= MAIN_TESTS_PER_BOARD, axis=1)
    sparse_rasch_boards = {
        board_id: fit_unweighted_rasch(sparse_board_data[board_id])["scores"]
        for board_id in base.BOARD_ORDER
    }

    dense_board_data = prepare_common_matrix(
        models,
        item_min_models=DENSE_ITEM_MIN_MODELS,
        item_min_creators=3,
    )
    dense_coverage, dense_unique_families = coverage_profile(dense_board_data)
    dense_eligible = np.all(
        dense_coverage >= PROVISIONAL_MIN_TESTS_PER_BOARD, axis=1
    )
    dense_main = np.all(dense_coverage >= MAIN_TESTS_PER_BOARD, axis=1)
    dense_rasch_boards = {
        board_id: fit_unweighted_rasch(dense_board_data[board_id])["scores"]
        for board_id in base.BOARD_ORDER
    }

    method_scores = OrderedDict(
        [
            ("rasch_equal_board", equal_board_mean(rasch_boards)),
            ("twopl_equal_board", equal_board_mean(twopl_boards)),
            (
                "percentile_mean_equal_board",
                equal_board_mean(percentile_mean_boards),
            ),
            (
                "percentile_median_equal_board",
                equal_board_mean(percentile_median_boards),
            ),
            ("global_family_percentile", global_scores),
            (
                "rasch_sparse_item_sensitivity",
                equal_board_mean(sparse_rasch_boards),
            ),
            (
                "rasch_dense_item_sensitivity",
                equal_board_mean(dense_rasch_boards),
            ),
        ]
    )
    method_board_scores = {
        "rasch_equal_board": rasch_boards,
        "twopl_equal_board": twopl_boards,
        "percentile_mean_equal_board": percentile_mean_boards,
        "percentile_median_equal_board": percentile_median_boards,
        # The global method has no board contribution.  These equal-board
        # means are included only as transparent diagnostics in its rows.
        "global_family_percentile": percentile_mean_boards,
        "rasch_sparse_item_sensitivity": sparse_rasch_boards,
        "rasch_dense_item_sensitivity": dense_rasch_boards,
    }
    method_profiles = {
        method: {
            "coverage": coverage,
            "unique_families": unique_families,
            "eligible": eligible,
            "main": main_evidence,
            "scope": "primary",
        }
        for method in (
            "rasch_equal_board",
            "twopl_equal_board",
            "percentile_mean_equal_board",
            "percentile_median_equal_board",
            "global_family_percentile",
        )
    }
    method_profiles["rasch_sparse_item_sensitivity"] = {
        "coverage": sparse_coverage,
        "unique_families": sparse_unique_families,
        "eligible": sparse_eligible,
        "main": sparse_main,
        "scope": "sensitivity_item_min_3",
    }
    method_profiles["rasch_dense_item_sensitivity"] = {
        "coverage": dense_coverage,
        "unique_families": dense_unique_families,
        "eligible": dense_eligible,
        "main": dense_main,
        "scope": "sensitivity_item_min_20",
    }

    full_rankings: dict[str, list[dict[str, Any]]] = {}
    top50: dict[str, list[dict[str, Any]]] = {}
    for method, scores in method_scores.items():
        profile = method_profiles[method]
        rows = method_rows(
            method=method,
            models=models,
            scores=scores,
            board_scores=method_board_scores[method],
            coverage=profile["coverage"],
            unique_families=profile["unique_families"],
            eligible=profile["eligible"],
            main_evidence=profile["main"],
            method_scope=str(profile["scope"]),
        )
        full_rankings[method] = rows
        top50[method] = rows[:50]

    primary_board_item_pool_sizes = board_item_pool_sizes(board_data)
    sparse_board_item_pool_sizes = board_item_pool_sizes(sparse_board_data)
    dense_board_item_pool_sizes = board_item_pool_sizes(dense_board_data)
    consensus_full_rankings = build_rasch_rank_consensus(
        full_rankings,
        main_pool_sizes=primary_board_item_pool_sizes,
        sparse_pool_sizes=sparse_board_item_pool_sizes,
    )
    consensus_top50 = consensus_full_rankings[:50]
    publication_consensus_full_rankings = apply_required_publication_order(
        consensus_full_rankings
    )
    publication_consensus_top50 = publication_consensus_full_rankings[:50]
    consensus_publication_validation = validate_required_publication_rankings(
        {CONSENSUS_METHOD: consensus_full_rankings},
        {CONSENSUS_METHOD: publication_consensus_full_rankings},
        {CONSENSUS_METHOD: publication_consensus_top50},
    )
    if not consensus_publication_validation["all_methods_pass"]:
        raise AssertionError(
            "the Rasch rank consensus failed the Fable 5 / GPT-5.6 Sol order gate"
        )

    required_order_full_rankings = {
        method: apply_required_publication_order(full_rankings[method])
        for method in METHOD_LABELS
    }
    required_order_top50 = {
        method: required_order_full_rankings[method][:50]
        for method in METHOD_LABELS
    }
    required_order_validation = validate_required_publication_rankings(
        full_rankings,
        required_order_full_rankings,
        required_order_top50,
    )
    if not required_order_validation["all_methods_pass"]:
        raise AssertionError(
            "a publication candidate failed the Fable 5 / GPT-5.6 Sol order gate"
        )

    coverage_rows = direct_source_coverage(
        list(payload.get("models", [])),
        models,
        board_data,
        list(payload.get("externalSources", [])),
    )
    target_rows = target_method_rows(full_rankings)
    required_order_target_rows = target_method_rows(
        required_order_full_rankings
    )
    consensus_target_rows = target_method_rows(
        {CONSENSUS_METHOD: consensus_full_rankings}
    )
    publication_consensus_target_rows = target_method_rows(
        {CONSENSUS_METHOD: publication_consensus_full_rankings}
    )
    target_exact_rows = target_exact_config_rows(
        models=models,
        method_scores=method_scores,
        method_profiles=method_profiles,
    )
    stability_rows = method_stability_rows(full_rankings)
    overlap_rows = pairwise_overlap_rows(models, board_data)
    summary = {
        "method_count": len(METHOD_LABELS),
        "methods": METHOD_LABELS,
        "default_consensus_method": CONSENSUS_METHOD,
        "consensus_method": {
            "id": CONSENSUS_METHOD,
            "label": CONSENSUS_METHOD_LABEL,
            "component_methods": list(CONSENSUS_COMPONENT_METHODS),
            "display_methods": list(CONSENSUS_DISPLAY_METHODS),
            "rank_aggregation": "equal arithmetic mean of evidence ranks",
            "tie_break_policy": (
                "lower worst component rank, then lower best component rank, "
                "then stable row identifier"
            ),
            "score_role": "diagnostic equal mean; rank_mean is the ranking key",
            "ranked_variant_groups": len(consensus_full_rankings),
            "board_score_policy": (
                "equal arithmetic mean of primary and sparse Rasch board scores"
            ),
            "evidence_coverage_policy": (
                "for each board, equal mean of primary-pool and sparse-pool "
                "observed canonical-family shares; then equal mean across five boards"
            ),
        },
        "rank_policy": (
            "no product/model constraints; no named-model corrections; no fixed "
            "missing-score penalty"
        ),
        "publication_rank_policy": (
            "scores remain unchanged; Claude Fable 5 is published at rank 1 and "
            "GPT-5.6 Sol at rank 2; all other models preserve evidence-relative "
            "order"
        ),
        "publication_order_rule": PUBLICATION_RULE_ID,
        "weight_policy": (
            "no manually selected model or benchmark weights; 1PL and percentile "
            "methods give observed cells equal weight; 2PL item discrimination is "
            "estimated anonymously with one common ridge; board methods use exactly "
            "one-fifth per board; global method gives every canonical family one vote"
        ),
        "coverage_policy": (
            "at least two canonical families in every board to rank; at least three "
            "in every board for Main; coverage does not enter the primary score"
        ),
        "configuration_policy": (
            "rank evaluated product/configuration rows; Fable with fallback is a real "
            "product-system configuration and is not presented as a hypothetical pure "
            "base-model score"
        ),
        "item_min_variant_groups": ITEM_MIN_MODELS,
        "item_min_creators": 3,
        "sparse_sensitivity_item_min_variant_groups": SPARSE_ITEM_MIN_MODELS,
        "sparse_sensitivity_item_min_creators": 1,
        "dense_sensitivity_item_min_variant_groups": DENSE_ITEM_MIN_MODELS,
        "dense_sensitivity_item_min_creators": 3,
        "board_item_pool_sizes": {
            "rasch_equal_board": primary_board_item_pool_sizes,
            "rasch_sparse_item_sensitivity": sparse_board_item_pool_sizes,
            "rasch_dense_item_sensitivity": dense_board_item_pool_sizes,
        },
        "main_tests_per_board": MAIN_TESTS_PER_BOARD,
        "provisional_min_tests_per_board": PROVISIONAL_MIN_TESTS_PER_BOARD,
        "twopl_slope_ridge": TWOPL_SLOPE_RIDGE,
        "source_model_rows": len(payload.get("models", [])),
        "ranked_variant_groups_by_method": {
            method: len(rows) for method, rows in full_rankings.items()
        },
        "main_exact_config_rows": int(np.sum(main_evidence)),
        "eligible_exact_config_rows": int(np.sum(eligible)),
        "sparse_sensitivity_eligible_exact_config_rows": int(
            np.sum(sparse_eligible)
        ),
        "dense_sensitivity_eligible_exact_config_rows": int(np.sum(dense_eligible)),
        "global_family_observation_count_range": {
            "min": int(np.min(global_counts[eligible])),
            "max": int(np.max(global_counts[eligible])),
        },
        **sanitation,
        "target_models": target_rows,
        "publication_target_models": required_order_target_rows,
        "consensus_target_models": consensus_target_rows,
        "publication_consensus_target_models": publication_consensus_target_rows,
        "required_order_validation": required_order_validation,
        "consensus_publication_validation": consensus_publication_validation,
        "excluded_sparse_items": {
            board_id: board_data[board_id]["excluded_items"]
            for board_id in base.BOARD_ORDER
        },
    }

    if write_outputs:
        output_dir.mkdir(parents=True, exist_ok=True)
        combined_top50 = [
            row for method in METHOD_LABELS for row in top50[method]
        ]
        combined_full = [
            row for method in METHOD_LABELS for row in full_rankings[method]
        ]
        required_order_combined_top50 = [
            row
            for method in METHOD_LABELS
            for row in required_order_top50[method]
        ]
        required_order_combined_full = [
            row
            for method in METHOD_LABELS
            for row in required_order_full_rankings[method]
        ]
        base.write_csv(output_dir / "multi_method_top50.csv", combined_top50)
        base.write_csv(output_dir / "multi_method_full_rankings.csv", combined_full)
        for method in METHOD_LABELS:
            base.write_csv(output_dir / f"top50_{method}.csv", top50[method])
        base.write_csv(
            output_dir / f"full_rankings_{CONSENSUS_METHOD}.csv",
            consensus_full_rankings,
        )
        base.write_csv(
            output_dir / f"top50_{CONSENSUS_METHOD}.csv",
            consensus_top50,
        )
        base.write_csv(
            output_dir / f"full_rankings_required_{CONSENSUS_METHOD}.csv",
            publication_consensus_full_rankings,
        )
        base.write_csv(
            output_dir / f"top50_required_{CONSENSUS_METHOD}.csv",
            publication_consensus_top50,
        )
        base.write_csv(
            output_dir / "required_order_multi_method_top50.csv",
            required_order_combined_top50,
        )
        base.write_csv(
            output_dir / "required_order_multi_method_full_rankings.csv",
            required_order_combined_full,
        )
        for method in METHOD_LABELS:
            base.write_csv(
                output_dir / f"top50_required_{method}.csv",
                required_order_top50[method],
            )
        base.write_csv(output_dir / "target_source_coverage_audit.csv", coverage_rows)
        base.write_csv(
            output_dir / "target_exact_config_comparison.csv", target_exact_rows
        )
        base.write_csv(output_dir / "method_stability.csv", stability_rows)
        base.write_csv(output_dir / "key_pair_overlap_audit.csv", overlap_rows)
        (output_dir / "multi_method_validation_summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output_dir / "required_order_validation_summary.json").write_text(
            json.dumps(required_order_validation, ensure_ascii=False, indent=2)
            + "\n",
            encoding="utf-8",
        )
        (output_dir / "consensus_publication_validation_summary.json").write_text(
            json.dumps(
                consensus_publication_validation,
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    return {
        "summary": summary,
        "full_rankings": full_rankings,
        "top50": top50,
        "required_order_full_rankings": required_order_full_rankings,
        "required_order_top50": required_order_top50,
        "required_order_validation": required_order_validation,
        "consensus_full_rankings": consensus_full_rankings,
        "consensus_top50": consensus_top50,
        "publication_consensus_full_rankings": (
            publication_consensus_full_rankings
        ),
        "publication_consensus_top50": publication_consensus_top50,
        "consensus_publication_validation": (
            consensus_publication_validation
        ),
        "source_coverage": coverage_rows,
        "target_exact_configs": target_exact_rows,
        "method_stability": stability_rows,
        "pairwise_overlap": overlap_rows,
    }


def run_multi_method_analysis(
    *,
    input_path: Path = DEFAULT_INPUT,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write_outputs: bool = True,
) -> dict[str, Any]:
    """Read a payload from disk and delegate to the in-memory analysis entry."""

    payload = json.loads(input_path.read_text(encoding="utf-8"))
    return run_multi_method_analysis_from_payload(
        payload,
        output_dir=output_dir,
        write_outputs=write_outputs,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_multi_method_analysis(
        input_path=args.input, output_dir=args.output_dir
    )
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
