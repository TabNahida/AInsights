"""Build product-constrained leaderboard variants on top of the IRT exploration.

The measurement layer remains unchanged and auditable.  This module adds a
separate coverage guardrail and an explicit partial-order reranker for product
requirements that are not observations from benchmark data:

* Claude Fable 5 is the overall anchor at rank one.
* Comparable Qwen commercial releases obey the declared version/tier order.
* Every Gemini Flash variant sits below at least fifteen sufficiently covered
  open-weight models.

The output always retains the raw measurement rank and score so these product
constraints cannot be mistaken for a statistical IRT finding.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np

import irt_leaderboard_analysis as base


ANALYSIS_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = ANALYSIS_DIR / "outputs"

UNIQUE_FAMILY_SOFT_TARGET = 12
UNIQUE_FAMILY_PENALTY_Z = 0.08
BASELINE_BOARD_SHORTFALL_PENALTY_Z = 0.15
ALTERNATIVE_BOARD_SHORTFALL_PENALTY_Z = 0.04
MAIN_MIN_TESTS_PER_BOARD = 3
MAIN_MIN_UNIQUE_FAMILIES = 9
GEMINI_FLASH_OPEN_MODEL_FLOOR = 15

GUARDED_SCHEMES = {
    "guarded_aindex": {
        "base": "baseline_aindex",
        "label": "覆盖校正 AIndex + 产品硬约束",
    },
    "guarded_rasch": {
        "base": "rasch_business",
        "label": "连续 1PL/Rasch + 独立覆盖校正 + 产品硬约束",
    },
    "guarded_twopl": {
        "base": "twopl_equal",
        "label": "强收缩连续 2PL + 独立覆盖校正 + 产品硬约束",
    },
    "guarded_robust": {
        "base": "robust_eb",
        "label": "稳健秩收缩 + 独立覆盖校正 + 产品硬约束",
    },
    "guarded_borda": {
        "base": "borda_breadth",
        "label": "收缩 Borda 广度榜 + 独立覆盖校正 + 产品硬约束",
    },
}

# These are deliberately curated comparable product edges.  Open-weight sizes,
# multimodal families, and unrelated Qwen subfamilies are not forced into a
# single total order merely because their names contain a newer version number.
QWEN_ORDER_EDGES = [
    ("Qwen3.8 Max", "Qwen3.7 Max", "newer_max"),
    ("Qwen3.7 Max", "Qwen3.6 Max Preview", "newer_max"),
    ("Qwen3.6 Max Preview", "Qwen3 Max", "newer_max"),
    ("Qwen3.7 Plus", "Qwen3.6 Plus", "newer_plus"),
    ("Qwen3.7 Max", "Qwen3.7 Plus", "same_version_max_gt_plus"),
    ("Qwen3.6 Max Preview", "Qwen3.6 Plus", "same_version_max_gt_plus"),
    ("Qwen3.5 Omni Plus", "Qwen3.5 Omni Flash", "same_version_plus_gt_flash"),
]


def finite_ranks(order: list[int], size: int) -> np.ndarray:
    ranks = np.full(size, np.nan, dtype=float)
    for rank, index in enumerate(order, start=1):
        ranks[index] = rank
    return ranks


def standardized_scores(values: np.ndarray) -> np.ndarray:
    result = np.full(values.shape, np.nan, dtype=float)
    valid = np.isfinite(values)
    if not np.any(valid):
        return result
    mean = float(np.mean(values[valid]))
    std = float(np.std(values[valid]))
    if not math.isfinite(std) or std < 1e-9:
        std = 1.0
    result[valid] = (values[valid] - mean) / std
    return result


def coverage_guarded_scores(
    measurement_scores: np.ndarray,
    coverage_matrix: np.ndarray,
    unique_families: np.ndarray,
    *,
    baseline: bool,
) -> tuple[np.ndarray, np.ndarray]:
    """Apply a small post-hoc penalty for non-independent or missing evidence."""

    score_z = standardized_scores(measurement_scores)
    unique_shortfall = np.maximum(0, UNIQUE_FAMILY_SOFT_TARGET - unique_families)
    board_shortfall = np.sum(
        np.maximum(0, MAIN_MIN_TESTS_PER_BOARD - coverage_matrix), axis=1
    )
    board_coefficient = (
        BASELINE_BOARD_SHORTFALL_PENALTY_Z
        if baseline
        else ALTERNATIVE_BOARD_SHORTFALL_PENALTY_Z
    )
    penalty = (
        UNIQUE_FAMILY_PENALTY_Z * unique_shortfall
        + board_coefficient * board_shortfall
    )
    adjusted = score_z - penalty
    adjusted[~np.isfinite(measurement_scores)] = np.nan
    return adjusted, penalty.astype(float)


def add_edge(
    edge_reasons: dict[tuple[int, int], set[str]],
    higher: int,
    lower: int,
    reason: str,
) -> None:
    if higher != lower:
        edge_reasons.setdefault((higher, lower), set()).add(reason)


def product_constraint_edges(
    models: list[dict[str, Any]],
    adjusted_scores: np.ndarray,
    coverage_matrix: np.ndarray,
    unique_families: np.ndarray,
    *,
    flash_open_floor: int,
) -> dict[tuple[int, int], set[str]]:
    valid = np.isfinite(adjusted_scores)
    names = [str(model.get("model") or "") for model in models]
    by_name = {name: index for index, name in enumerate(names)}
    edges: dict[tuple[int, int], set[str]] = {}

    fable_candidates = [
        index
        for index, name in enumerate(names)
        if valid[index] and name.startswith("Claude Fable 5")
    ]
    if not fable_candidates:
        raise ValueError("Claude Fable 5 is not present in the eligible population")
    fable = max(fable_candidates, key=lambda index: float(adjusted_scores[index]))
    for index in np.flatnonzero(valid):
        add_edge(edges, fable, int(index), "fable_rank_one_anchor")

    for higher_name, lower_name, reason in QWEN_ORDER_EDGES:
        higher = by_name.get(higher_name)
        lower = by_name.get(lower_name)
        if higher is None or lower is None or not valid[higher] or not valid[lower]:
            continue
        add_edge(edges, higher, lower, f"qwen:{reason}")

    main_evidence = (
        np.all(coverage_matrix >= MAIN_MIN_TESTS_PER_BOARD, axis=1)
        & (unique_families >= MAIN_MIN_UNIQUE_FAMILIES)
    )
    open_candidates = [
        index
        for index, model in enumerate(models)
        if valid[index]
        and main_evidence[index]
        and str(model.get("openSourceType") or "") == "open"
    ]
    open_candidates.sort(
        key=lambda index: (-float(adjusted_scores[index]), names[index].lower())
    )
    anchors = open_candidates[:flash_open_floor]
    if len(anchors) < flash_open_floor:
        raise ValueError(
            f"Only {len(anchors)} main-evidence open models are available; "
            f"cannot enforce a floor of {flash_open_floor}."
        )
    flash_models = [
        index
        for index, name in enumerate(names)
        if valid[index] and name.startswith("Gemini ") and "Flash" in name
    ]
    for anchor in anchors:
        for flash in flash_models:
            add_edge(edges, anchor, flash, "gemini_flash_below_open_floor")
    return edges


def stable_topological_order(
    adjusted_scores: np.ndarray,
    names: list[str],
    edges: dict[tuple[int, int], set[str]],
) -> list[int]:
    """Return a deterministic raise-only projection of the raw ranking.

    When a required ``higher -> lower`` edge is violated, the higher model is
    inserted immediately before the lower model.  This makes the product prior
    visible as a promotion of the declared stronger release instead of silently
    dragging a well-measured older release down to the sparse model's old rank.
    """

    valid_indices = np.flatnonzero(np.isfinite(adjusted_scores)).tolist()
    order = sorted(
        valid_indices,
        key=lambda index: (-float(adjusted_scores[index]), names[index].lower()),
    )
    valid_set = set(valid_indices)
    active_edges = [
        (higher, lower)
        for higher, lower in edges
        if higher in valid_set and lower in valid_set
    ]
    iteration_limit = max(1, len(order) * max(1, len(active_edges)))
    for _ in range(iteration_limit):
        position = {index: rank for rank, index in enumerate(order)}
        violations = [
            (higher, lower)
            for higher, lower in active_edges
            if position[higher] >= position[lower]
        ]
        if not violations:
            return order
        higher, lower = min(
            violations,
            key=lambda edge: (
                position[edge[1]],
                position[edge[0]],
                names[edge[0]].lower(),
                names[edge[1]].lower(),
            ),
        )
        order.remove(higher)
        order.insert(order.index(lower), higher)
    raise ValueError("Product constraint graph is cyclic or failed to converge")


def qwen_violation_count(
    ranks: np.ndarray,
    names: list[str],
) -> int:
    by_name = {name: index for index, name in enumerate(names)}
    violations = 0
    for higher_name, lower_name, _ in QWEN_ORDER_EDGES:
        higher = by_name.get(higher_name)
        lower = by_name.get(lower_name)
        if higher is None or lower is None:
            continue
        if not math.isfinite(ranks[higher]) or not math.isfinite(ranks[lower]):
            continue
        violations += int(ranks[higher] >= ranks[lower])
    return violations


def open_models_above_flash(
    ranks: np.ndarray,
    models: list[dict[str, Any]],
    main_evidence: np.ndarray,
    flash_index: int,
) -> int:
    if not math.isfinite(ranks[flash_index]):
        return 0
    return int(
        sum(
            math.isfinite(ranks[index])
            and ranks[index] < ranks[flash_index]
            and bool(main_evidence[index])
            and str(model.get("openSourceType") or "") == "open"
            for index, model in enumerate(models)
        )
    )


def rank_for_name(ranks: np.ndarray, names: list[str], name: str) -> int | None:
    try:
        index = names.index(name)
    except ValueError:
        return None
    return int(ranks[index]) if math.isfinite(ranks[index]) else None


def edge_rows(
    scheme_id: str,
    names: list[str],
    models: list[dict[str, Any]],
    edges: dict[tuple[int, int], set[str]],
    unconstrained_ranks: np.ndarray,
    constrained_ranks: np.ndarray,
    main_evidence: np.ndarray,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for (higher, lower), reasons in sorted(
        edges.items(), key=lambda item: (names[item[0][0]], names[item[0][1]])
    ):
        rows.append(
            {
                "scheme_id": scheme_id,
                "higher_model": names[higher],
                "lower_model": names[lower],
                "reasons": " | ".join(sorted(reasons)),
                "higher_evidence_tier": "Main" if main_evidence[higher] else "Provisional",
                "lower_evidence_tier": "Main" if main_evidence[lower] else "Provisional",
                "higher_unconstrained_rank": int(unconstrained_ranks[higher]),
                "lower_unconstrained_rank": int(unconstrained_ranks[lower]),
                "violated_before": bool(unconstrained_ranks[higher] >= unconstrained_ranks[lower]),
                "higher_constrained_rank": int(constrained_ranks[higher]),
                "lower_constrained_rank": int(constrained_ranks[lower]),
                "satisfied_after": bool(constrained_ranks[higher] < constrained_ranks[lower]),
                "higher_open_source_type": models[higher].get("openSourceType") or "unknown",
                "lower_open_source_type": models[lower].get("openSourceType") or "unknown",
            }
        )
    return rows


def build_constrained_rankings(
    analysis_result: dict[str, Any],
) -> dict[str, Any]:
    models = analysis_result["models"]
    names = [str(model.get("model") or "") for model in models]
    model_count = len(models)
    coverage_matrix = np.column_stack(
        [
            analysis_result["board_fits"]["twopl"][board_id]["coverage_counts"]
            for board_id in base.BOARD_ORDER
        ]
    ).astype(int)
    unique_families = base.unique_family_counts(analysis_result["board_data"])
    eligible = np.asarray(analysis_result["eligible"], dtype=bool)
    main_evidence = (
        eligible
        & np.all(coverage_matrix >= MAIN_MIN_TESTS_PER_BOARD, axis=1)
        & (unique_families >= MAIN_MIN_UNIQUE_FAMILIES)
    )

    aindex_ranks, _ = base.rank_scores(
        np.asarray(analysis_result["scores"]["baseline_aindex"], dtype=float), names
    )
    all_rows: list[dict[str, Any]] = []
    top50_rows: list[dict[str, Any]] = []
    diagnostic_rows: list[dict[str, Any]] = []
    all_edge_rows: list[dict[str, Any]] = []
    sensitivity_rows: list[dict[str, Any]] = []

    for scheme_id, scheme_spec in GUARDED_SCHEMES.items():
        base_scheme = str(scheme_spec["base"])
        measurement_scores = np.asarray(
            analysis_result["scores"][base_scheme], dtype=float
        ).copy()
        measurement_scores[~eligible] = np.nan
        adjusted_scores, coverage_penalty = coverage_guarded_scores(
            measurement_scores,
            coverage_matrix,
            unique_families,
            baseline=base_scheme == "baseline_aindex",
        )
        raw_method_ranks, _ = base.rank_scores(measurement_scores, names)
        unconstrained_ranks, unconstrained_order = base.rank_scores(adjusted_scores, names)
        edges = product_constraint_edges(
            models,
            adjusted_scores,
            coverage_matrix,
            unique_families,
            flash_open_floor=GEMINI_FLASH_OPEN_MODEL_FLOOR,
        )
        constrained_order = stable_topological_order(adjusted_scores, names, edges)
        constrained_ranks = finite_ranks(constrained_order, model_count)
        qwen_before = qwen_violation_count(unconstrained_ranks, names)
        qwen_after = qwen_violation_count(constrained_ranks, names)

        incident_reasons: dict[int, set[str]] = defaultdict(set)
        for (higher, lower), reasons in edges.items():
            incident_reasons[higher].update(reasons)
            incident_reasons[lower].update(reasons)

        flash_indices = [
            index
            for index, name in enumerate(names)
            if math.isfinite(constrained_ranks[index])
            and name.startswith("Gemini ")
            and "Flash" in name
        ]
        flash_floor_counts = {
            index: open_models_above_flash(
                constrained_ranks, models, main_evidence, index
            )
            for index in flash_indices
        }

        for index in constrained_order:
            counts = coverage_matrix[index].astype(int).tolist()
            row = {
                "scheme_id": scheme_id,
                "scheme": scheme_spec["label"],
                "base_scheme_id": base_scheme,
                "rank": int(constrained_ranks[index]),
                "model": names[index],
                "creator": str(models[index].get("creator") or ""),
                "variant_group": str(models[index].get("variantGroup") or ""),
                "release_date": str(models[index].get("releaseDate") or ""),
                "open_source_type": str(models[index].get("openSourceType") or "unknown"),
                "evidence_tier": "Main" if main_evidence[index] else "Provisional",
                "measurement_score": base.rounded(measurement_scores[index], 4),
                "raw_method_rank": int(raw_method_ranks[index]),
                "coverage_adjusted_z": base.rounded(adjusted_scores[index], 6),
                "coverage_penalty_z": base.rounded(coverage_penalty[index], 6),
                "unconstrained_rank_after_coverage": int(unconstrained_ranks[index]),
                "rank_change_due_to_constraints": int(
                    unconstrained_ranks[index] - constrained_ranks[index]
                ),
                "rank_change_vs_raw_method": int(
                    raw_method_ranks[index] - constrained_ranks[index]
                ),
                "baseline_aindex_rank": int(aindex_ranks[index]),
                "constraint_flags": " | ".join(sorted(incident_reasons.get(index, set()))),
                "board_test_slots_total": int(np.sum(counts)),
                "unique_benchmark_families": int(unique_families[index]),
                "min_board_tests": int(min(counts)),
                "boards_below_3": int(sum(count < MAIN_MIN_TESTS_PER_BOARD for count in counts)),
                "main_open_models_above_if_gemini_flash": flash_floor_counts.get(index),
            }
            for board_id, count in zip(base.BOARD_ORDER, counts, strict=True):
                row[f"{board_id}_tests"] = count
            all_rows.append(row)
            if int(constrained_ranks[index]) <= 50:
                top50_rows.append(row)

        raw_top = set(unconstrained_order[:50])
        constrained_top = set(constrained_order[:50])
        shifts = np.abs(unconstrained_ranks - constrained_ranks)
        flash_min = min(flash_floor_counts.values()) if flash_floor_counts else None
        diagnostic_rows.append(
            {
                "scheme_id": scheme_id,
                "scheme": scheme_spec["label"],
                "base_scheme_id": base_scheme,
                "ranked_models": len(constrained_order),
                "main_evidence_models": int(np.sum(main_evidence)),
                "provisional_models": int(len(constrained_order) - np.sum(main_evidence)),
                "fable_rank": rank_for_name(constrained_ranks, names, "Claude Fable 5 (with fallback)"),
                "qwen_direct_edge_violations_before": qwen_before,
                "qwen_direct_edge_violations_after": qwen_after,
                "gemini_flash_min_main_open_models_above": flash_min,
                "gemini_3_5_flash_rank": rank_for_name(constrained_ranks, names, "Gemini 3.5 Flash"),
                "gemini_3_6_flash_rank": rank_for_name(constrained_ranks, names, "Gemini 3.6 Flash"),
                "qwen_3_8_max_rank": rank_for_name(constrained_ranks, names, "Qwen3.8 Max"),
                "qwen_3_7_max_rank": rank_for_name(constrained_ranks, names, "Qwen3.7 Max"),
                "qwen_3_7_plus_rank": rank_for_name(constrained_ranks, names, "Qwen3.7 Plus"),
                "qwen_3_6_plus_rank": rank_for_name(constrained_ranks, names, "Qwen3.6 Plus"),
                "spearman_vs_unconstrained_after_coverage": base.rounded(
                    base.spearman(unconstrained_ranks, constrained_ranks)
                ),
                "top50_overlap_with_unconstrained_after_coverage": len(raw_top & constrained_top),
                "max_absolute_constraint_shift": int(np.nanmax(shifts)),
                "top50_provisional_models": int(
                    sum(not bool(main_evidence[index]) for index in constrained_order[:50])
                ),
                "top50_median_unique_families": base.rounded(
                    float(np.median(unique_families[constrained_order[:50]])), 2
                ),
            }
        )
        all_edge_rows.extend(
            edge_rows(
                scheme_id,
                names,
                models,
                edges,
                unconstrained_ranks,
                constrained_ranks,
                main_evidence,
            )
        )

        for flash_floor in (5, 10, 15):
            sensitivity_edges = product_constraint_edges(
                models,
                adjusted_scores,
                coverage_matrix,
                unique_families,
                flash_open_floor=flash_floor,
            )
            sensitivity_order = stable_topological_order(
                adjusted_scores, names, sensitivity_edges
            )
            sensitivity_ranks = finite_ranks(sensitivity_order, model_count)
            sensitivity_flash = [
                open_models_above_flash(
                    sensitivity_ranks, models, main_evidence, index
                )
                for index in flash_indices
            ]
            sensitivity_rows.append(
                {
                    "scheme_id": scheme_id,
                    "flash_open_floor": flash_floor,
                    "fable_rank": rank_for_name(
                        sensitivity_ranks, names, "Claude Fable 5 (with fallback)"
                    ),
                    "qwen_direct_edge_violations": qwen_violation_count(
                        sensitivity_ranks, names
                    ),
                    "gemini_flash_min_main_open_models_above": min(sensitivity_flash),
                    "gemini_3_5_flash_rank": rank_for_name(
                        sensitivity_ranks, names, "Gemini 3.5 Flash"
                    ),
                    "gemini_3_6_flash_rank": rank_for_name(
                        sensitivity_ranks, names, "Gemini 3.6 Flash"
                    ),
                    "spearman_vs_unconstrained": base.rounded(
                        base.spearman(unconstrained_ranks, sensitivity_ranks)
                    ),
                    "top50_overlap_with_unconstrained": len(
                        set(unconstrained_order[:50]) & set(sensitivity_order[:50])
                    ),
                    "max_absolute_shift": int(
                        np.nanmax(np.abs(unconstrained_ranks - sensitivity_ranks))
                    ),
                }
            )

    validation = {
        "all_schemes_fable_rank_one": all(
            row["fable_rank"] == 1 for row in diagnostic_rows
        ),
        "all_schemes_qwen_constraints_satisfied": all(
            row["qwen_direct_edge_violations_after"] == 0
            for row in diagnostic_rows
        ),
        "all_schemes_gemini_flash_open_floor_satisfied": all(
            int(row["gemini_flash_min_main_open_models_above"])
            >= GEMINI_FLASH_OPEN_MODEL_FLOOR
            for row in diagnostic_rows
        ),
        "each_scheme_has_50_rows": all(
            sum(row["scheme_id"] == scheme_id for row in top50_rows) == 50
            for scheme_id in GUARDED_SCHEMES
        ),
        "constraint_edges_satisfied": all(
            bool(row["satisfied_after"]) for row in all_edge_rows
        ),
    }
    if not all(validation.values()):
        raise AssertionError(f"Constrained ranking validation failed: {validation}")

    summary = {
        "data_generated_at": analysis_result["summary"].get("data_generated_at"),
        "measurement_source": analysis_result["summary"].get(
            "analysis_generated_from"
        ),
        "eligible_models_min_two_per_board": int(np.sum(eligible)),
        "main_evidence_models_min_three_and_unique_nine": int(np.sum(main_evidence)),
        "unique_family_soft_target": UNIQUE_FAMILY_SOFT_TARGET,
        "unique_family_penalty_z_per_missing_family": UNIQUE_FAMILY_PENALTY_Z,
        "baseline_board_shortfall_penalty_z": BASELINE_BOARD_SHORTFALL_PENALTY_Z,
        "alternative_board_shortfall_penalty_z": ALTERNATIVE_BOARD_SHORTFALL_PENALTY_Z,
        "gemini_flash_main_open_model_floor": GEMINI_FLASH_OPEN_MODEL_FLOOR,
        "qwen_constraint_edges": [
            {"higher": higher, "lower": lower, "reason": reason}
            for higher, lower, reason in QWEN_ORDER_EDGES
        ],
        "schemes": diagnostic_rows,
        "validation": validation,
        "interpretation": (
            "Measurement scores are benchmark-derived; coverage penalties and "
            "partial-order constraints are explicit product policy overlays."
        ),
    }
    return {
        "summary": summary,
        "full_rankings": all_rows,
        "top50": top50_rows,
        "diagnostics": diagnostic_rows,
        "constraint_edges": all_edge_rows,
        "sensitivity": sensitivity_rows,
    }


def run(
    *,
    input_path: Path = base.DEFAULT_INPUT,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write_outputs: bool = True,
) -> dict[str, Any]:
    measurement = base.run_analysis(
        input_path=input_path,
        output_dir=output_dir,
        write_outputs=False,
        run_stability=False,
    )
    result = build_constrained_rankings(measurement)
    if write_outputs:
        output_dir.mkdir(parents=True, exist_ok=True)
        base.write_csv(
            output_dir / "top50_constrained_schemes.csv", result["top50"]
        )
        base.write_csv(
            output_dir / "full_rankings_constrained_schemes.csv",
            result["full_rankings"],
        )
        base.write_csv(
            output_dir / "constrained_scheme_diagnostics.csv",
            result["diagnostics"],
        )
        base.write_csv(
            output_dir / "constraint_edges.csv", result["constraint_edges"]
        )
        base.write_csv(
            output_dir / "constraint_sensitivity.csv", result["sensitivity"]
        )
        (output_dir / "constrained_validation_summary.json").write_text(
            json.dumps(result["summary"], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return result


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=base.DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    result = run(input_path=args.input, output_dir=args.output_dir)
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
