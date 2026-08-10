"""Multi-method evidence measurement ranked only by observed-score evidence.

All primary methods use the same sanitized model-by-benchmark matrix.  There
are no product-order constraints, named-model adjustments, model-specific
weights, or fixed missing-score penalties.  The five boards receive equal
weight wherever boards are aggregated.  Coverage only controls eligibility
and the Main/Provisional evidence label.

The primary leaderboard score is the disclosed blend of 80% equal-board 2PL
score and 20% sparse-item Rasch score.  Rows are ordered by that score alone,
with a stable identifier used only to make exact score ties deterministic.
Component ranks and their weighted mean remain audit diagnostics and never
change the primary order.

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
    from . import aindex_scheme18 as scheme18
    from . import evidence_only_ranking_analysis as evidence
    from . import irt_leaderboard_analysis as base
except ImportError:  # Direct script execution.
    import aindex_scheme18 as scheme18
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

CONSENSUS_METHOD = "twopl_sparse_80_20_score"
CONSENSUS_METHOD_LABEL = (
    "80% equal-board 2PL and 20% sparse-item Rasch observed-score blend"
)
CONSENSUS_COMPONENT_METHODS: tuple[str, str] = (
    "twopl_equal_board",
    "rasch_sparse_item_sensitivity",
)
CONSENSUS_COMPONENT_WEIGHTS: OrderedDict[str, float] = OrderedDict(
    [
        ("twopl_equal_board", 0.80),
        ("rasch_sparse_item_sensitivity", 0.20),
    ]
)
CONSENSUS_DISPLAY_METHODS: tuple[str, str] = (
    "rasch_equal_board",
    "rasch_dense_item_sensitivity",
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


def main_evidence_mask(
    coverage: np.ndarray,
    board_data: dict[str, dict[str, Any]],
) -> np.ndarray:
    """Apply the Main target without requiring more items than a pool contains."""

    targets = np.asarray(
        [
            min(MAIN_TESTS_PER_BOARD, len(board_data[board_id]["items"]))
            for board_id in base.BOARD_ORDER
        ],
        dtype=int,
    )
    return np.all(coverage >= targets[None, :], axis=1)


def competition_ranks(values: np.ndarray) -> np.ndarray:
    return evidence.competition_ranks(values)


def choose_evidence_representative(
    models: list[dict[str, Any]],
    eligible: np.ndarray,
    main_evidence: np.ndarray,
    scores: np.ndarray,
) -> list[int]:
    """Choose one family representative without altering any observed score.

    A Main configuration is preferred over a Provisional sibling so a sparse
    point estimate cannot represent the whole family when a better-evidenced
    exact configuration exists. Within the preferred tier, the method's own
    untouched score selects the row; stable text is only a score-tie label.
    """

    by_group: dict[str, list[int]] = {}
    for index in np.flatnonzero(eligible):
        group = str(
            models[index].get("variantGroup")
            or models[index].get("slug")
            or models[index].get("model")
            or index
        )
        by_group.setdefault(group, []).append(int(index))

    selected: list[int] = []
    for indexes in by_group.values():
        main_indexes = [index for index in indexes if main_evidence[index]]
        candidates = main_indexes or indexes
        best_score = max(float(scores[index]) for index in candidates)
        tied = [
            index
            for index in candidates
            if math.isclose(
                float(scores[index]),
                best_score,
                rel_tol=0.0,
                abs_tol=1e-12,
            )
        ]
        selected.append(
            min(
                tied,
                key=lambda index: (
                    str(models[index].get("slug") or ""),
                    str(models[index].get("model") or ""),
                ),
            )
        )
    return selected


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
    collapse_variant_groups: bool = True,
    selected_indexes: list[int] | None = None,
) -> list[dict[str, Any]]:
    if selected_indexes is not None:
        selected = list(selected_indexes)
    elif collapse_variant_groups:
        selected = choose_evidence_representative(
            models,
            eligible,
            main_evidence,
            scores,
        )
    else:
        selected = [int(index) for index in np.flatnonzero(eligible)]
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


def _ranking_by_field(
    rows: list[dict[str, Any]],
    *,
    method: str,
    field: str,
) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        identity = str(row.get(field) or "")
        if not identity:
            raise ValueError(f"{method} row has no {field}")
        if identity in indexed:
            raise ValueError(f"{method} has duplicate {field} {identity!r}")
        indexed[identity] = row
    return indexed


def _ranking_by_variant_group(
    rows: list[dict[str, Any]],
    *,
    method: str,
) -> dict[str, dict[str, Any]]:
    return _ranking_by_field(
        rows,
        method=method,
        field="variant_group",
    )


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


def build_twopl_sparse_score_consensus(
    full_rankings: dict[str, list[dict[str, Any]]],
    *,
    primary_pool_sizes: dict[str, int],
    sparse_pool_sizes: dict[str, int],
    identity_field: str = "variant_group",
) -> list[dict[str, Any]]:
    """Build the observed-score 2PL/Sparse-Rasch primary consensus.

    The two component populations and selected exact configurations must match
    exactly.  Missing components are not imputed and no fixed rank penalty is
    introduced.  The weighted component-rank mean is retained only for audit;
    the weighted observed score is the sole ranking value.  A stable identifier
    makes exact score ties deterministic without inspecting model names.
    """

    twopl_method, sparse_method = CONSENSUS_COMPONENT_METHODS
    twopl_rows = full_rankings[twopl_method]
    sparse_rows = full_rankings[sparse_method]
    twopl_by_group = _ranking_by_field(
        twopl_rows,
        method=twopl_method,
        field=identity_field,
    )
    sparse_by_group = _ranking_by_field(
        sparse_rows,
        method=sparse_method,
        field=identity_field,
    )
    twopl_groups = set(twopl_by_group)
    sparse_groups = set(sparse_by_group)
    if twopl_groups != sparse_groups:
        only_twopl = sorted(twopl_groups - sparse_groups)
        only_sparse = sorted(sparse_groups - twopl_groups)
        raise ValueError(
            "2PL/Sparse-Rasch consensus requires identical variant-group "
            f"populations; only 2PL={only_twopl[:5]!r}, "
            f"only sparse={only_sparse[:5]!r}"
        )

    component_maps = {
        method: _ranking_by_field(
            full_rankings[method],
            method=method,
            field=identity_field,
        )
        for method in (*CONSENSUS_COMPONENT_METHODS, *CONSENSUS_DISPLAY_METHODS)
    }
    component_populations = {
        method: len(rows) for method, rows in full_rankings.items()
    }
    pool_sizes = {
        twopl_method: dict(primary_pool_sizes),
        sparse_method: dict(sparse_pool_sizes),
    }
    twopl_weight = CONSENSUS_COMPONENT_WEIGHTS[twopl_method]
    sparse_weight = CONSENSUS_COMPONENT_WEIGHTS[sparse_method]

    rows: list[dict[str, Any]] = []
    for group in twopl_groups:
        twopl = twopl_by_group[group]
        sparse = sparse_by_group[group]
        if ranking_row_id(twopl) != ranking_row_id(sparse):
            raise ValueError(
                "2PL/Sparse-Rasch consensus cannot mix exact configurations for "
                f"{group!r}: 2PL={twopl.get('slug')!r}, "
                f"sparse={sparse.get('slug')!r}"
            )

        twopl_rank = int(twopl["rank"])
        sparse_rank = int(sparse["rank"])
        rank_mean = twopl_weight * twopl_rank + sparse_weight * sparse_rank
        rank_min = min(twopl_rank, sparse_rank)
        rank_max = max(twopl_rank, sparse_rank)
        twopl_score = float(twopl["score"])
        sparse_score = float(sparse["score"])
        raw_composite_score = (
            twopl_weight * twopl_score + sparse_weight * sparse_score
        )
        evidence_tier = (
            "Main"
            if twopl.get("evidence_tier") == "Main"
            and sparse.get("evidence_tier") == "Main"
            else "Provisional"
        )

        row: dict[str, Any] = {
            "method": CONSENSUS_METHOD,
            "method_label": CONSENSUS_METHOD_LABEL,
            "method_scope": "primary_score_consensus",
            # Assigned after the observed-score sort below.
            "rank": 0,
            "model": str(twopl.get("model") or ""),
            "creator": str(twopl.get("creator") or ""),
            "slug": str(twopl.get("slug") or ""),
            "variant_group": str(twopl.get("variant_group") or ""),
            "ranking_grain": (
                "exact_config" if identity_field == "slug" else "variant_group"
            ),
            "evidence_tier": evidence_tier,
            "score": base.rounded(raw_composite_score, 4),
            "_sort_score": raw_composite_score,
            "score_role": "primary_ranking_key_0_100_weighted_method_score",
            "rank_mean": base.rounded(rank_mean, 4),
            "rank_weighted_mean": base.rounded(rank_mean, 4),
            "rank_mean_role": "audit_only_not_ranking_key",
            "rank_min": rank_min,
            "rank_max": rank_max,
            "rank_span": rank_max - rank_min,
            "rank_tie_break_policy": "higher_score_then_stable_id",
            "twopl_rank": twopl_rank,
            "twopl_score": twopl["score"],
            "sparse_rasch_rank": sparse_rank,
            "sparse_rasch_score": sparse["score"],
            "twopl_unique_benchmark_families": int(
                twopl["unique_benchmark_families"]
            ),
            "sparse_unique_benchmark_families": int(
                sparse["unique_benchmark_families"]
            ),
            "unique_benchmark_families": min(
                int(twopl["unique_benchmark_families"]),
                int(sparse["unique_benchmark_families"]),
            ),
            "component_weights": dict(CONSENSUS_COMPONENT_WEIGHTS),
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

        rasch = component_maps["rasch_equal_board"].get(group)
        dense = component_maps["rasch_dense_item_sensitivity"].get(group)
        row.update(
            {
                "rasch_rank": int(rasch["rank"]) if rasch else None,
                "rasch_score": rasch.get("score") if rasch else None,
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
            twopl_board_score = float(twopl[f"{board_id}_score"])
            sparse_board_score = float(sparse[f"{board_id}_score"])
            twopl_tests = int(twopl[f"{board_id}_tests"])
            sparse_tests = int(sparse[f"{board_id}_tests"])
            conservative_tests = min(twopl_tests, sparse_tests)
            board_tests_total += conservative_tests
            min_board_tests = (
                conservative_tests
                if min_board_tests is None
                else min(min_board_tests, conservative_tests)
            )
            if conservative_tests < MAIN_TESTS_PER_BOARD:
                board_below_main += 1

            twopl_denominator = int(primary_pool_sizes[board_id])
            sparse_denominator = int(sparse_pool_sizes[board_id])
            if twopl_denominator <= 0 or sparse_denominator <= 0:
                raise ValueError(f"empty item pool for consensus board {board_id!r}")
            twopl_coverage = min(
                max(twopl_tests / twopl_denominator, 0.0), 1.0
            )
            sparse_coverage = min(
                max(sparse_tests / sparse_denominator, 0.0), 1.0
            )
            board_coverage_score = 100.0 * (
                twopl_weight * twopl_coverage
                + sparse_weight * sparse_coverage
            )
            board_coverages.append(board_coverage_score)

            row[f"{board_id}_score"] = base.rounded(
                twopl_weight * twopl_board_score
                + sparse_weight * sparse_board_score,
                3,
            )
            row[f"{board_id}_tests"] = conservative_tests
            row[f"{board_id}_twopl_score"] = twopl[f"{board_id}_score"]
            row[f"{board_id}_sparse_rasch_score"] = sparse[
                f"{board_id}_score"
            ]
            row[f"{board_id}_twopl_tests"] = twopl_tests
            row[f"{board_id}_sparse_rasch_tests"] = sparse_tests
            row[f"{board_id}_primary_item_pool_size"] = twopl_denominator
            row[f"{board_id}_sparse_item_pool_size"] = sparse_denominator
            row[f"{board_id}_evidence_coverage_score"] = base.rounded(
                board_coverage_score, 3
            )
            row[f"{board_id}_rasch_score"] = (
                rasch.get(f"{board_id}_score") if rasch else None
            )
            row[f"{board_id}_rasch_tests"] = (
                int(rasch[f"{board_id}_tests"]) if rasch else None
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
            -float(row["_sort_score"]),
            ranking_row_id(row),
        )
    )
    population = len(rows)
    for position, row in enumerate(rows, start=1):
        row["rank"] = position
        row["rank_percentile"] = base.rounded(
            normalized_rank_percentile(float(position), population),
            4,
        )
        del row["_sort_score"]
    return rows


def ranking_row_id(row: dict[str, Any]) -> str:
    """Return a stable identifier used only to resolve exact score ties."""

    slug = str(row.get("slug") or "")
    if slug:
        return f"slug:{slug}"
    variant_group = str(row.get("variant_group") or "")
    if variant_group:
        return f"variant_group:{variant_group}"
    raise ValueError("ranking row has neither slug nor variant_group")


def validate_score_ordered_rankings(
    rankings: dict[str, list[dict[str, Any]]],
    top_rankings: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    """Validate the score-only ordering contract for emitted rankings."""

    if set(rankings) != set(top_rankings):
        raise ValueError("full-ranking and top-ranking method sets do not match")

    method_results: dict[str, dict[str, Any]] = {}
    disallowed_fields = {
        "evidence_rank",
        "publication_order_rule",
        "rank_change_due_to_required_order",
        "required_order_target",
    }
    for method, rows in rankings.items():
        top_rows = top_rankings[method]
        row_ids = [ranking_row_id(row) for row in rows]
        display_scores = [float(row["score"]) for row in rows]
        sort_scores = [
            (
                CONSENSUS_COMPONENT_WEIGHTS["twopl_equal_board"]
                * float(row["twopl_score"])
                + CONSENSUS_COMPONENT_WEIGHTS[
                    "rasch_sparse_item_sensitivity"
                ]
                * float(row["sparse_rasch_score"])
            )
            for row in rows
        ]
        expected_top_size = min(50, len(rows))
        sequential_ranks = [int(row["rank"]) for row in rows] == list(
            range(1, len(rows) + 1)
        )
        scores_non_increasing = all(
            left >= right
            for left, right in zip(sort_scores, sort_scores[1:])
        )
        displayed_scores_non_increasing = all(
            left >= right
            for left, right in zip(display_scores, display_scores[1:])
        )
        stable_tie_order = all(
            not math.isclose(left_score, right_score, rel_tol=0.0, abs_tol=1e-12)
            or left_id <= right_id
            for left_score, right_score, left_id, right_id in zip(
                sort_scores,
                sort_scores[1:],
                row_ids,
                row_ids[1:],
            )
        )
        unique_stable_ids = len(set(row_ids)) == len(row_ids)
        top_is_prefix = (
            len(top_rows) == expected_top_size
            and [ranking_row_id(row) for row in top_rows]
            == row_ids[:expected_top_size]
            and [int(row["rank"]) for row in top_rows]
            == list(range(1, expected_top_size + 1))
        )
        has_no_artificial_order_fields = all(
            disallowed_fields.isdisjoint(row) for row in rows
        )
        passed = all(
            (
                sequential_ranks,
                scores_non_increasing,
                displayed_scores_non_increasing,
                stable_tie_order,
                unique_stable_ids,
                top_is_prefix,
                has_no_artificial_order_fields,
            )
        )
        method_results[method] = {
            "passed": passed,
            "full_rows": len(rows),
            "top_rows": len(top_rows),
            "sequential_ranks": sequential_ranks,
            "scores_non_increasing": scores_non_increasing,
            "displayed_scores_non_increasing": displayed_scores_non_increasing,
            "stable_identifier_orders_exact_score_ties": stable_tie_order,
            "unique_stable_ids": unique_stable_ids,
            "top_is_full_ranking_prefix": top_is_prefix,
            "has_no_artificial_order_fields": has_no_artificial_order_fields,
        }

    return {
        "ranking_policy": (
            "descending_unrounded_weighted_component_score_then_stable_id_"
            "for_exact_ties"
        ),
        "method_count": len(method_results),
        "all_methods_pass": all(
            result["passed"] for result in method_results.values()
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


def prepare_method_measurements(
    models: list[dict[str, Any]],
) -> dict[str, Any]:
    """Fit every displayed method for one explicitly scoped model population."""

    board_data = prepare_common_matrix(models)
    coverage, unique_families = coverage_profile(board_data)
    eligible = np.all(coverage >= PROVISIONAL_MIN_TESTS_PER_BOARD, axis=1)
    main_evidence = main_evidence_mask(coverage, board_data)

    rasch_fits = {
        board_id: fit_unweighted_rasch(board_data[board_id])
        for board_id in base.BOARD_ORDER
    }
    twopl_fits = {
        board_id: fit_unweighted_twopl(board_data[board_id])
        for board_id in base.BOARD_ORDER
    }
    percentile_mean_boards = board_percentile_scores(
        board_data,
        reducer="mean",
    )
    percentile_median_boards = board_percentile_scores(
        board_data,
        reducer="median",
    )
    rasch_boards = {
        board_id: rasch_fits[board_id]["scores"]
        for board_id in base.BOARD_ORDER
    }
    twopl_boards = {
        board_id: twopl_fits[board_id]["scores"]
        for board_id in base.BOARD_ORDER
    }
    global_scores, global_counts = global_family_percentiles(board_data)

    sparse_board_data = prepare_common_matrix(
        models,
        item_min_models=SPARSE_ITEM_MIN_MODELS,
        item_min_creators=1,
    )
    sparse_coverage, sparse_unique_families = coverage_profile(
        sparse_board_data
    )
    sparse_eligible = np.all(
        sparse_coverage >= PROVISIONAL_MIN_TESTS_PER_BOARD,
        axis=1,
    )
    sparse_main = main_evidence_mask(sparse_coverage, sparse_board_data)
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
        dense_coverage >= PROVISIONAL_MIN_TESTS_PER_BOARD,
        axis=1,
    )
    dense_main = main_evidence_mask(dense_coverage, dense_board_data)
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
        # The global method has no board contribution. These equal-board
        # means remain transparent diagnostics in its rows.
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
    return {
        "board_data": board_data,
        "coverage": coverage,
        "unique_families": unique_families,
        "eligible": eligible,
        "main_evidence": main_evidence,
        "global_counts": global_counts,
        "sparse_board_data": sparse_board_data,
        "sparse_coverage": sparse_coverage,
        "sparse_unique_families": sparse_unique_families,
        "sparse_eligible": sparse_eligible,
        "sparse_main": sparse_main,
        "dense_board_data": dense_board_data,
        "dense_coverage": dense_coverage,
        "dense_unique_families": dense_unique_families,
        "dense_eligible": dense_eligible,
        "dense_main": dense_main,
        "method_scores": method_scores,
        "method_board_scores": method_board_scores,
        "method_profiles": method_profiles,
    }


def run_multi_method_analysis_from_payload(
    payload: dict[str, Any],
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write_outputs: bool = False,
) -> dict[str, Any]:
    """Analyze an in-memory site payload without reading the generated site file."""

    models, sanitation = evidence.sanitize_models(payload)
    measurement = prepare_method_measurements(models)
    board_data = measurement["board_data"]
    coverage = measurement["coverage"]
    unique_families = measurement["unique_families"]
    eligible = measurement["eligible"]
    main_evidence = measurement["main_evidence"]
    global_counts = measurement["global_counts"]
    sparse_board_data = measurement["sparse_board_data"]
    sparse_coverage = measurement["sparse_coverage"]
    sparse_eligible = measurement["sparse_eligible"]
    dense_board_data = measurement["dense_board_data"]
    dense_coverage = measurement["dense_coverage"]
    dense_eligible = measurement["dense_eligible"]
    method_scores = measurement["method_scores"]
    method_board_scores = measurement["method_board_scores"]
    method_profiles = measurement["method_profiles"]
    representative_methods = (
        "rasch_equal_board",
        "twopl_equal_board",
        "rasch_sparse_item_sensitivity",
        "rasch_dense_item_sensitivity",
    )
    representative_eligible = np.logical_and.reduce(
        [method_profiles[method]["eligible"] for method in representative_methods]
    )
    representative_main = np.logical_and.reduce(
        [method_profiles[method]["main"] for method in representative_methods]
    )
    representative_scores = (
        CONSENSUS_COMPONENT_WEIGHTS["twopl_equal_board"]
        * method_scores["twopl_equal_board"]
        + CONSENSUS_COMPONENT_WEIGHTS["rasch_sparse_item_sensitivity"]
        * method_scores["rasch_sparse_item_sensitivity"]
    )
    representative_indexes = choose_evidence_representative(
        models,
        representative_eligible,
        representative_main,
        representative_scores,
    )

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
            selected_indexes=representative_indexes,
        )
        full_rankings[method] = rows
        top50[method] = rows[:50]

    primary_board_item_pool_sizes = board_item_pool_sizes(board_data)
    sparse_board_item_pool_sizes = board_item_pool_sizes(sparse_board_data)
    dense_board_item_pool_sizes = board_item_pool_sizes(dense_board_data)
    consensus_full_rankings = build_twopl_sparse_score_consensus(
        full_rankings,
        primary_pool_sizes=primary_board_item_pool_sizes,
        sparse_pool_sizes=sparse_board_item_pool_sizes,
    )
    consensus_top50 = consensus_full_rankings[:50]
    consensus_score_order_validation = validate_score_ordered_rankings(
        {CONSENSUS_METHOD: consensus_full_rankings},
        {CONSENSUS_METHOD: consensus_top50},
    )
    if not consensus_score_order_validation["all_methods_pass"]:
        raise AssertionError(
            "the 2PL/Sparse-Rasch consensus failed score-order validation"
        )

    # The deduplicated leaderboard above may use a direct family-level result
    # attached to its source row. The Full Ranking toggle must not attribute
    # that unscoped result to one effort tier. Refit the exact-config population
    # using AA exact rows plus only explicitly variant-scoped external results.
    exact_models, exact_sanitation = evidence.sanitize_models(
        payload,
        exact_config_only=True,
    )
    exact_measurement = prepare_method_measurements(exact_models)
    exact_method_scores = exact_measurement["method_scores"]
    exact_method_board_scores = exact_measurement["method_board_scores"]
    exact_method_profiles = exact_measurement["method_profiles"]
    exact_config_eligible = np.logical_and.reduce(
        [
            exact_method_profiles[method]["eligible"]
            for method in (
                "rasch_equal_board",
                "twopl_equal_board",
                "rasch_sparse_item_sensitivity",
                "rasch_dense_item_sensitivity",
            )
        ]
    )
    exact_primary_board_item_pool_sizes = board_item_pool_sizes(
        exact_measurement["board_data"]
    )
    exact_sparse_board_item_pool_sizes = board_item_pool_sizes(
        exact_measurement["sparse_board_data"]
    )
    exact_dense_board_item_pool_sizes = board_item_pool_sizes(
        exact_measurement["dense_board_data"]
    )
    exact_config_full_rankings: dict[str, list[dict[str, Any]]] = {}
    exact_config_top50: dict[str, list[dict[str, Any]]] = {}
    for method, scores in exact_method_scores.items():
        profile = exact_method_profiles[method]
        rows = method_rows(
            method=method,
            models=exact_models,
            scores=scores,
            board_scores=exact_method_board_scores[method],
            coverage=profile["coverage"],
            unique_families=profile["unique_families"],
            eligible=exact_config_eligible,
            main_evidence=profile["main"],
            method_scope=f"{profile['scope']}_exact_config",
            collapse_variant_groups=False,
        )
        exact_config_full_rankings[method] = rows
        exact_config_top50[method] = rows[:50]

    exact_config_consensus_full_rankings = build_twopl_sparse_score_consensus(
        exact_config_full_rankings,
        primary_pool_sizes=exact_primary_board_item_pool_sizes,
        sparse_pool_sizes=exact_sparse_board_item_pool_sizes,
        identity_field="slug",
    )
    exact_config_consensus_top50 = exact_config_consensus_full_rankings[:50]
    exact_config_score_order_validation = validate_score_ordered_rankings(
        {CONSENSUS_METHOD: exact_config_consensus_full_rankings},
        {CONSENSUS_METHOD: exact_config_consensus_top50},
    )
    if not exact_config_score_order_validation["all_methods_pass"]:
        raise AssertionError(
            "the exact-config 2PL/Sparse-Rasch consensus failed "
            "score-order validation"
        )

    # The legacy four-method analysis above remains the frozen eligibility and
    # representative-slug audit.  Scheme 18 is now the primary score.  Fit it
    # on the raw payload rows for the selected deduplicated slugs so legitimate
    # family-level evidence remains available in the family view.  Apply that
    # exact same calibration and cap to the already-qualified, exact-config-
    # sanitized rows; never refit on the larger exact population.
    scheme18_result = scheme18.run_aindex_scheme18_from_payload(
        payload,
        calibration_slugs=[
            str(row.get("slug") or "") for row in consensus_full_rankings
        ],
        exact_config_slugs=[
            str(row.get("slug") or "")
            for row in exact_config_consensus_full_rankings
        ],
        exact_config_models=exact_models,
        output_dir=output_dir,
        write_outputs=write_outputs,
    )

    coverage_rows = direct_source_coverage(
        list(payload.get("models", [])),
        models,
        board_data,
        list(payload.get("externalSources", [])),
    )
    target_rows = target_method_rows(full_rankings)
    consensus_target_rows = target_method_rows(
        {CONSENSUS_METHOD: consensus_full_rankings}
    )
    target_exact_rows = target_exact_config_rows(
        models=models,
        method_scores=method_scores,
        method_profiles=method_profiles,
    )
    stability_rows = method_stability_rows(full_rankings)
    overlap_rows = pairwise_overlap_rows(models, board_data)
    exact_config_group_counts: dict[str, int] = {}
    for row in exact_config_consensus_full_rankings:
        group = str(row.get("variant_group") or "")
        exact_config_group_counts[group] = exact_config_group_counts.get(group, 0) + 1
    group_consensus_by_slug = {
        str(row.get("slug") or ""): row
        for row in consensus_full_rankings
    }
    exact_consensus_by_slug = {
        str(row.get("slug") or ""): row
        for row in exact_config_consensus_full_rankings
    }
    group_consensus_slugs = set(group_consensus_by_slug)
    exact_config_slugs = set(exact_consensus_by_slug)
    recovered_exact_config_count = len(
        exact_config_slugs - group_consensus_slugs
    )
    deduped_only_config_count = len(
        group_consensus_slugs - exact_config_slugs
    )
    exact_config_visibility_rows: list[dict[str, Any]] = []
    for exact_row in exact_config_consensus_full_rankings:
        slug = str(exact_row.get("slug") or "")
        group = str(exact_row.get("variant_group") or "")
        group_row = group_consensus_by_slug.get(slug)
        exact_config_visibility_rows.append(
            {
                "variant_group": group,
                "eligible_exact_configs_in_group": exact_config_group_counts[group],
                "model": str(exact_row.get("model") or ""),
                "slug": slug,
                "selected_in_deduped_ranking": group_row is not None,
                "recovered_when_dedupe_disabled": group_row is None,
                "exact_rank": int(exact_row["rank"]),
                "exact_score": exact_row.get("score"),
                "exact_rank_mean_audit": exact_row.get("rank_mean"),
                "deduped_rank": (
                    int(group_row["rank"]) if group_row is not None else None
                ),
                "evidence_tier": str(exact_row.get("evidence_tier") or ""),
                "unique_benchmark_families": int(
                    exact_row.get("unique_benchmark_families") or 0
                ),
            }
        )
    summary = {
        "method_count": len(METHOD_LABELS),
        "methods": METHOD_LABELS,
        "default_consensus_method": scheme18.METHOD_ID,
        "default_ranking_method": scheme18.METHOD_ID,
        "ranked_variant_groups": len(scheme18_result["full_rankings"]),
        "ranked_exact_config_rows_primary": len(
            scheme18_result["exact_config_full_rankings"]
        ),
        "aindex_scheme18": {
            "id": scheme18.METHOD_ID,
            "candidate_id": scheme18.CANDIDATE_ID,
            "role": "sole primary ranking score",
            "core_fit": scheme18.CORE_FIT,
            "extension_aggregator": scheme18.EXTENSION_AGGREGATOR,
            "extension_pool": "independent_audit",
            "cap_rule": scheme18.CAP_RULE,
            "bonus_cap_per_board": scheme18_result["calibration"][
                "bonus_cap_per_board"
            ],
            "board_order": list(scheme18.BOARD_ORDER),
            "board_points_max": scheme18.BOARD_POINTS,
            "board_aggregation": (
                "five symmetric boards; board_points=board_score/5; "
                "final_score=sum(board_points)"
            ),
            "board_items": {
                board_id: {
                    "core": list(scheme18.CORE_ITEMS[board_id]),
                    "extension": list(scheme18.EXTENSION_ITEMS[board_id]),
                }
                for board_id in scheme18.BOARD_ORDER
            },
            "missing_policy": scheme18_result["calibration"][
                "missing_policy"
            ],
            "fit_apply_policy": scheme18_result["calibration"][
                "fit_apply_policy"
            ],
            "eligibility_and_representative_source": (
                "legacy four-method common gate and representative slug are "
                "retained as audit inputs only; they do not enter Scheme 18 "
                "scores or ordering"
            ),
            "score_role": (
                "unrounded 0-100 additive five-board score is the sole ranking "
                "key; stable slug/model IDs resolve exact numerical ties only"
            ),
            "ranked_variant_groups": len(scheme18_result["full_rankings"]),
            "ranked_exact_config_rows": len(
                scheme18_result["exact_config_full_rankings"]
            ),
            "exact_reuses_deduplicated_calibration": True,
            "validation": scheme18_result["validation"],
        },
        "consensus_method": {
            "id": CONSENSUS_METHOD,
            "label": CONSENSUS_METHOD_LABEL,
            "role": "audit-only legacy eligibility/representative consensus",
            "component_methods": list(CONSENSUS_COMPONENT_METHODS),
            "component_weights": dict(CONSENSUS_COMPONENT_WEIGHTS),
            "display_methods": list(CONSENSUS_DISPLAY_METHODS),
            "rank_aggregation": (
                "descending 80% equal-board 2PL score plus 20% sparse-item "
                "Rasch score"
            ),
            "tie_break_policy": (
                "stable row identifier for exact unrounded composite-score ties"
            ),
            "score_role": (
                "legacy 0-100 composite retained only for eligibility, "
                "representative selection, and sensitivity audit; it does not "
                "enter the Scheme 18 score or ordering"
            ),
            "score_precision_policy": (
                "rank by the unrounded 80/20 composite, then display score to "
                "four decimal places"
            ),
            "ranked_variant_groups": len(consensus_full_rankings),
            "board_score_policy": (
                "80% equal-board 2PL plus 20% sparse-item Rasch board scores"
            ),
            "evidence_coverage_policy": (
                "for each board, 80/20 weighted mean of primary-pool and "
                "sparse-pool observed canonical-family shares; then equal mean "
                "across five boards"
            ),
        },
        "rank_policy": (
            "no product/model constraints; no named-model corrections; no fixed "
            "missing-score penalty; score descending is the only ranking rule"
        ),
        "weight_policy": (
            "the primary Scheme 18 has no model-specific or benchmark-specific "
            "weights: complete core items enter an unweighted geometric partial-credit "
            "score, observed independent extensions can add only a capped positive "
            "residual, and every board contributes exactly one fifth; the legacy "
            "80% 2PL / 20% sparse-Rasch blend remains audit-only"
        ),
        "coverage_policy": (
            "the legacy four-method common gate selects qualified rows and one "
            "representative slug per variant group; Scheme 18 then requires every "
            "declared core item, while missing extensions remain absent and earn zero "
            "bonus without an imputed score"
        ),
        "configuration_policy": (
            "rank evaluated source-backed product/configuration rows; system or "
            "fallback configurations remain explicitly labeled rather than being "
            "recast as hypothetical pure base-model scores"
        ),
        "variant_group_representative_policy": (
            "for continuity, the audit layer requires the common four-method gate, "
            "prefers a configuration that is Main in all four displayed audit "
            "methods, then selects the highest untouched legacy consensus score "
            "within that evidence tier; this determines population membership and "
            "display slug only, never a Scheme 18 score or rank"
        ),
        "exact_config_evidence_policy": (
            "AA exact rows plus direct external results explicitly marked "
            "variantScoped; family-level external results remain available to the "
            "deduplicated family ranking but are never attributed to one effort tier"
        ),
        "item_min_variant_groups": ITEM_MIN_MODELS,
        "item_min_creators": 3,
        "sparse_sensitivity_item_min_variant_groups": SPARSE_ITEM_MIN_MODELS,
        "sparse_sensitivity_item_min_creators": 1,
        "dense_sensitivity_item_min_variant_groups": DENSE_ITEM_MIN_MODELS,
        "dense_sensitivity_item_min_creators": 3,
        "board_item_pool_sizes": {
            "rasch_equal_board": primary_board_item_pool_sizes,
            "twopl_equal_board": primary_board_item_pool_sizes,
            "rasch_sparse_item_sensitivity": sparse_board_item_pool_sizes,
            "rasch_dense_item_sensitivity": dense_board_item_pool_sizes,
        },
        "exact_config_board_item_pool_sizes": {
            "rasch_equal_board": exact_primary_board_item_pool_sizes,
            "twopl_equal_board": exact_primary_board_item_pool_sizes,
            "rasch_sparse_item_sensitivity": (
                exact_sparse_board_item_pool_sizes
            ),
            "rasch_dense_item_sensitivity": exact_dense_board_item_pool_sizes,
        },
        "main_tests_per_board": MAIN_TESTS_PER_BOARD,
        "provisional_min_tests_per_board": PROVISIONAL_MIN_TESTS_PER_BOARD,
        "twopl_slope_ridge": TWOPL_SLOPE_RIDGE,
        "source_model_rows": len(payload.get("models", [])),
        "ranked_variant_groups_by_method": {
            method: len(rows) for method, rows in full_rankings.items()
        },
        "main_exact_config_rows": int(
            np.sum(exact_measurement["main_evidence"])
        ),
        "eligible_exact_config_rows": int(
            np.sum(exact_measurement["eligible"])
        ),
        "sparse_sensitivity_eligible_exact_config_rows": int(
            np.sum(exact_measurement["sparse_eligible"])
        ),
        "dense_sensitivity_eligible_exact_config_rows": int(
            np.sum(exact_measurement["dense_eligible"])
        ),
        "ranked_exact_config_rows": len(exact_config_consensus_full_rankings),
        "eligible_exact_configs_hidden_by_group_collapse": (
            recovered_exact_config_count
        ),
        "deduped_configs_not_exact_config_eligible": deduped_only_config_count,
        "exact_config_population_net_change": (
            len(exact_config_consensus_full_rankings)
            - len(consensus_full_rankings)
        ),
        "ranked_exact_config_variant_groups": len(exact_config_group_counts),
        "variant_groups_with_multiple_eligible_exact_configs": sum(
            count > 1 for count in exact_config_group_counts.values()
        ),
        "global_family_observation_count_range": {
            "min": int(np.min(global_counts[eligible])),
            "max": int(np.max(global_counts[eligible])),
        },
        **sanitation,
        "exact_config_sanitation": exact_sanitation,
        "target_models": target_rows,
        "consensus_target_models": consensus_target_rows,
        "consensus_score_order_validation": consensus_score_order_validation,
        "exact_config_score_order_validation": (
            exact_config_score_order_validation
        ),
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
        exact_config_combined_full = [
            row
            for method in METHOD_LABELS
            for row in exact_config_full_rankings[method]
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
            output_dir / "exact_config_multi_method_full_rankings.csv",
            exact_config_combined_full,
        )
        base.write_csv(
            output_dir / f"full_rankings_exact_config_{CONSENSUS_METHOD}.csv",
            exact_config_consensus_full_rankings,
        )
        base.write_csv(
            output_dir / f"top50_exact_config_{CONSENSUS_METHOD}.csv",
            exact_config_consensus_top50,
        )
        base.write_csv(output_dir / "target_source_coverage_audit.csv", coverage_rows)
        base.write_csv(
            output_dir / "target_exact_config_comparison.csv", target_exact_rows
        )
        base.write_csv(output_dir / "method_stability.csv", stability_rows)
        base.write_csv(output_dir / "key_pair_overlap_audit.csv", overlap_rows)
        base.write_csv(
            output_dir / "exact_config_score_visibility_audit.csv",
            exact_config_visibility_rows,
        )
        (output_dir / "multi_method_validation_summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output_dir / "score_order_validation_summary.json").write_text(
            json.dumps(
                {
                    "variant_group_consensus": consensus_score_order_validation,
                    "exact_config_consensus": exact_config_score_order_validation,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    return {
        "summary": summary,
        "aindex_scheme18_full_rankings": scheme18_result["full_rankings"],
        "aindex_scheme18_top50": scheme18_result["top50"],
        "exact_config_aindex_scheme18_full_rankings": scheme18_result[
            "exact_config_full_rankings"
        ],
        "exact_config_aindex_scheme18_top50": scheme18_result[
            "exact_config_top50"
        ],
        "aindex_scheme18_calibration": scheme18_result["calibration"],
        "aindex_scheme18_validation": scheme18_result["validation"],
        "full_rankings": full_rankings,
        "top50": top50,
        "consensus_full_rankings": consensus_full_rankings,
        "consensus_top50": consensus_top50,
        "consensus_score_order_validation": consensus_score_order_validation,
        "exact_config_full_rankings": exact_config_full_rankings,
        "exact_config_top50": exact_config_top50,
        "exact_config_consensus_full_rankings": (
            exact_config_consensus_full_rankings
        ),
        "exact_config_consensus_top50": exact_config_consensus_top50,
        "exact_config_score_order_validation": (
            exact_config_score_order_validation
        ),
        "source_coverage": coverage_rows,
        "target_exact_configs": target_exact_rows,
        "method_stability": stability_rows,
        "pairwise_overlap": overlap_rows,
        "exact_config_visibility": exact_config_visibility_rows,
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
