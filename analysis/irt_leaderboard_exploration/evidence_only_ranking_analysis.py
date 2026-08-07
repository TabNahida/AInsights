"""Evidence-only, unconstrained benchmark-as-item 2PL ranking.

This runner deliberately excludes product-order constraints and model-specific
reranking. It also removes scores copied across product variants and avoids the
site's fitted LiveCodeBench fallback. Every ranked configuration needs two
independent benchmark families in every board. Coverage affects the evidence
tier and the ridge-regularized IRT uncertainty, but there is no fixed
missing-test penalty. The mixed Main/Provisional table is ranked by the
ridge-regularized 2PL point estimate; a board-level 0.67-SE lower-bound
sensitivity score and rank are reported separately.
"""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from pathlib import Path
from statistics import NormalDist
from typing import Any

import numpy as np

try:
    from . import irt_leaderboard_analysis as base
except ImportError:  # Direct script execution.
    import irt_leaderboard_analysis as base


ANALYSIS_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = base.DEFAULT_INPUT
DEFAULT_OUTPUT_DIR = ANALYSIS_DIR / "outputs"

MAIN_TESTS_PER_BOARD = 3
PROVISIONAL_MIN_TESTS_PER_BOARD = 2
LCB_MULTIPLIER = 0.67


def evidence_item(
    item_id: str,
    label: str,
    *keys: str,
    scale: str = "percent",
    family: str | None = None,
) -> dict[str, Any]:
    return {
        "id": item_id,
        "family": family or item_id,
        "label": label,
        "keys": list(keys),
        "scale": scale,
    }


# Protocol choices are explicit. In particular, Terminal-Bench 2.1, HLE,
# GPQA, AIME, MMMU-Pro, and IFBench use the common Artificial Analysis fields;
# provider-reported values for the same family stay in the source store but are
# not substituted row-by-row into these common-protocol items. LiveCodeBench
# uses only the raw external value because the site-level AA field can contain a
# fitted fallback.
EVIDENCE_BOARD_ITEMS: dict[str, list[dict[str, Any]]] = {
    "coding": [
        evidence_item("swe-bench-pro", "SWE-Bench Pro", "benchmark:swe-bench-pro"),
        evidence_item("livecodebench", "LiveCodeBench (reported)", "benchmark:livecodebench"),
        evidence_item(
            "swe-bench-verified",
            "SWE-bench Verified",
            "benchmark:swe-bench-verified",
        ),
        evidence_item("terminal-bench-v2-1-aa", "Terminal-Bench v2.1 (AA)", "Terminal-Bench v2.1"),
        evidence_item(
            "swe-bench-multilingual",
            "SWE-bench Multilingual",
            "benchmark:swe-bench-multilingual",
        ),
        evidence_item("scicode-aa", "SciCode (AA)", "SciCode"),
        evidence_item("deepswe-v1-1", "DeepSWE v1.1", "benchmark:deepswe-v1-1"),
    ],
    "agentic-tool-work": [
        evidence_item("swe-bench-pro", "SWE-Bench Pro", "benchmark:swe-bench-pro"),
        evidence_item("browsecomp", "BrowseComp", "benchmark:browsecomp"),
        evidence_item("hle-tools", "HLE w/ tools", "benchmark:hle-tools"),
        evidence_item("mcp-atlas", "MCP-Atlas Public", "benchmark:mcp-atlas"),
        evidence_item("osworld-verified", "OSWorld-Verified", "benchmark:osworld-verified"),
        evidence_item(
            "gdpval-wins-ties",
            "GDPval (wins or ties)",
            "benchmark:gdpval-wins-ties",
        ),
        evidence_item("terminal-bench-v2-1-aa", "Terminal-Bench v2.1 (AA)", "Terminal-Bench v2.1"),
        evidence_item(
            "gdpval-aa-elo",
            "GDPval-AA Elo",
            "benchmark:gdpval-aa-elo",
            scale="rank",
        ),
        evidence_item("toolathlon", "Toolathlon", "benchmark:toolathlon"),
        evidence_item("aa-lcr", "AA-LCR", "AA-LCR"),
        evidence_item("automationbench", "AutomationBench", "benchmark:automationbench"),
    ],
    "hard-reasoning": [
        evidence_item("hle-aa", "Humanity's Last Exam (AA)", "Humanity's Last Exam"),
        evidence_item(
            "frontiermath-tier-4",
            "FrontierMath Tier 4",
            "benchmark:frontiermath-tier-4",
        ),
        evidence_item("critpt-aa", "CritPt (AA)", "CritPt"),
        evidence_item(
            "frontiermath-tier-1-3",
            "FrontierMath Tier 1-3",
            "benchmark:frontiermath-tier-1-3",
        ),
        evidence_item("gpqa-diamond-aa", "GPQA Diamond (AA)", "GPQA Diamond"),
        evidence_item("aime-2025-aa", "AIME 2025 (AA)", "AIME 2025"),
    ],
    "knowledge-science": [
        evidence_item("omniscience-aa", "AA-Omniscience Accuracy", "AA-Omniscience Accuracy"),
        evidence_item("gpqa-diamond-aa", "GPQA Diamond (AA)", "GPQA Diamond"),
        evidence_item("hle-aa", "Humanity's Last Exam (AA)", "Humanity's Last Exam"),
        evidence_item("mmmlu", "MMMLU", "benchmark:mmmlu"),
        evidence_item("mmmu-pro-aa", "MMMU-Pro (AA)", "MMMU-Pro"),
        evidence_item("scicode-aa", "SciCode (AA)", "SciCode"),
        evidence_item("mmlu-pro", "MMLU-Pro", "benchmark:mmlu-pro"),
    ],
    "instruction-context": [
        evidence_item("ifbench-aa", "IFBench (AA)", "IFBench"),
        evidence_item("aa-lcr", "AA-LCR", "AA-LCR"),
        evidence_item("critpt-aa", "CritPt (AA)", "CritPt"),
        evidence_item(
            "charxiv-no-tools",
            "CharXiv Reasoning",
            "benchmark:charxiv-no-tools",
        ),
    ],
}


def derived_external_entry(entry: dict[str, Any]) -> bool:
    """Return whether an external score is explicitly marked as non-observed."""

    if any(
        entry.get(key) is True
        for key in ("derived", "estimated", "fitted", "imputed", "interpolated")
    ):
        return True
    description = " ".join(
        str(entry.get(key) or "").strip().lower()
        for key in (
            "method",
            "provenance",
            "scoreOrigin",
            "scoreType",
            "valueOrigin",
            "valueType",
        )
    )
    return any(
        marker in description
        for marker in (
            "linear-fit",
            "linear fit",
            "interpolat",
            "imput",
            "fitted",
            "estimated",
        )
    )


def sanitize_models(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Remove copied/derived values while retaining direct exact-variant evidence.

    ``variantScoped`` means the direct row belongs only to the evaluated config,
    so it is admissible. A sibling row carrying ``sharedFromVariant`` is not a
    separate observation and is removed. If both metadata rows exist for one
    metric, the direct observation wins and is retained.
    """

    models: list[dict[str, Any]] = []
    removed_shared = 0
    removed_ineligible = 0
    removed_derived = 0
    removed_site_livecode = 0
    retained_variant_scoped = 0
    for source_model in payload.get("models", []):
        model = deepcopy(source_model)
        scores = model.setdefault("scores", {})
        entries_by_key: dict[str, list[dict[str, Any]]] = {}
        for entry in model.get("externalBenchmarks", []) or []:
            key = str(entry.get("metricKey") or "")
            if key:
                entries_by_key.setdefault(key, []).append(entry)
        for key, entries in entries_by_key.items():
            direct_observations = [
                entry
                for entry in entries
                if not entry.get("sharedFromVariant")
                and entry.get("evidenceEligible") is not False
                and not derived_external_entry(entry)
            ]
            if direct_observations:
                if (
                    base.finite_number(scores.get(key)) is not None
                    and any(entry.get("variantScoped") for entry in direct_observations)
                ):
                    retained_variant_scoped += 1
                continue
            if base.finite_number(scores.get(key)) is None:
                continue
            scores[key] = None
            if any(entry.get("sharedFromVariant") for entry in entries):
                removed_shared += 1
            if any(entry.get("evidenceEligible") is False for entry in entries):
                removed_ineligible += 1
            if any(derived_external_entry(entry) for entry in entries):
                removed_derived += 1
        if base.finite_number(scores.get("LiveCodeBench")) is not None:
            scores["LiveCodeBench"] = None
            removed_site_livecode += 1
        models.append(model)
    return models, {
        "shared_variant_score_cells_removed": removed_shared,
        "configuration_ineligible_score_cells_removed": removed_ineligible,
        "derived_external_score_cells_removed": removed_derived,
        "site_livecodebench_cells_excluded": removed_site_livecode,
        "variant_scoped_direct_score_cells_retained": retained_variant_scoped,
    }


def cdf_scores(values: np.ndarray) -> np.ndarray:
    normal = NormalDist()
    return np.asarray([100.0 * normal.cdf(float(value)) for value in values], dtype=float)


def competition_ranks(values: np.ndarray) -> np.ndarray:
    """Assign equal rank to exact ties without using model names as a tiebreaker."""

    order = np.argsort(-values, kind="mergesort")
    ranks = np.full(len(values), np.nan, dtype=float)
    previous_value: float | None = None
    previous_rank = 0
    for position, index in enumerate(order, start=1):
        value = float(values[index])
        if previous_value is None or not math.isclose(
            value, previous_value, rel_tol=0.0, abs_tol=1e-12
        ):
            previous_rank = position
            previous_value = value
        ranks[index] = previous_rank
    return ranks


def choose_score_best_variant(
    models: list[dict[str, Any]],
    eligible: np.ndarray,
    scores: np.ndarray,
) -> list[int]:
    """Choose one exact config per display group using evidence score only."""

    by_group: dict[str, list[int]] = {}
    for index in np.flatnonzero(eligible):
        group = str(
            models[index].get("variantGroup")
            or models[index].get("slug")
            or models[index].get("model")
        )
        by_group.setdefault(group, []).append(int(index))

    selected = []
    for indexes in by_group.values():
        best_score = max(float(scores[index]) for index in indexes)
        tied = [index for index in indexes if math.isclose(float(scores[index]), best_score, abs_tol=1e-12)]
        # This only selects the label shown for a score tie; it cannot alter the rank.
        selected.append(min(tied, key=lambda index: str(models[index].get("model") or "")))
    return selected


def run_evidence_analysis(
    *,
    input_path: Path = DEFAULT_INPUT,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    write_outputs: bool = True,
) -> dict[str, Any]:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    models, sanitation = sanitize_models(payload)

    original_items = base.BOARD_ITEMS
    try:
        base.BOARD_ITEMS = EVIDENCE_BOARD_ITEMS
        board_data = base.prepare_board_data(models)
        board_fits = base.compute_board_fits(board_data)
        unique_counts = base.unique_family_counts(board_data)
    finally:
        base.BOARD_ITEMS = original_items

    coverage = np.column_stack(
        [board_fits["twopl"][board_id]["coverage_counts"] for board_id in base.BOARD_ORDER]
    ).astype(int)
    theta = np.column_stack(
        [board_fits["twopl"][board_id]["theta"] for board_id in base.BOARD_ORDER]
    )
    se = np.column_stack(
        [board_fits["twopl"][board_id]["se"] for board_id in base.BOARD_ORDER]
    )
    twopl_board_scores = {
        board_id: cdf_scores(theta[:, index])
        for index, board_id in enumerate(base.BOARD_ORDER)
    }
    lcb_board_scores = {
        board_id: cdf_scores(theta[:, index] - LCB_MULTIPLIER * se[:, index])
        for index, board_id in enumerate(base.BOARD_ORDER)
    }
    twopl_scores = base.weighted_log1p_mean(
        twopl_board_scores, base.EQUAL_BOARD_WEIGHTS
    )
    lcb_scores = base.weighted_log1p_mean(lcb_board_scores, base.EQUAL_BOARD_WEIGHTS)

    eligible = np.all(coverage >= PROVISIONAL_MIN_TESTS_PER_BOARD, axis=1)
    main_evidence = np.all(coverage >= MAIN_TESTS_PER_BOARD, axis=1)
    selected_indexes = choose_score_best_variant(models, eligible, twopl_scores)
    selected_indexes.sort(
        key=lambda index: (-float(twopl_scores[index]), str(models[index].get("model") or ""))
    )

    selected_scores = np.asarray([twopl_scores[index] for index in selected_indexes])
    selected_lcb = np.asarray([lcb_scores[index] for index in selected_indexes])
    ranks = competition_ranks(selected_scores)
    lcb_ranks = competition_ranks(selected_lcb)

    rows: list[dict[str, Any]] = []
    for position, index in enumerate(selected_indexes):
        counts = coverage[index].tolist()
        row: dict[str, Any] = {
            "rank": int(ranks[position]),
            "model": str(models[index].get("model") or ""),
            "creator": str(models[index].get("creator") or ""),
            "slug": str(models[index].get("slug") or ""),
            "variant_group": str(models[index].get("variantGroup") or ""),
            "evidence_tier": "Main" if main_evidence[index] else "Provisional",
            "twopl_score": base.rounded(twopl_scores[index], 4),
            "lcb_score_sensitivity": base.rounded(lcb_scores[index], 4),
            "lcb_rank_sensitivity": int(lcb_ranks[position]),
            "unique_benchmark_families": int(unique_counts[index]),
            "board_test_slots_total": int(np.sum(coverage[index])),
            "min_board_tests": int(np.min(coverage[index])),
            "boards_below_main_target": int(np.sum(coverage[index] < MAIN_TESTS_PER_BOARD)),
            "mean_board_se": base.rounded(float(np.mean(se[index])), 4),
            "max_board_se": base.rounded(float(np.max(se[index])), 4),
        }
        for board_position, board_id in enumerate(base.BOARD_ORDER):
            row[f"{board_id}_tests"] = counts[board_position]
            row[f"{board_id}_score"] = base.rounded(
                twopl_board_scores[board_id][index], 3
            )
        rows.append(row)

    rows.sort(key=lambda row: (int(row["rank"]), str(row["model"])))
    top50 = rows[:50]
    target_names = ("Claude Opus 5", "Qwen3.8 Max")
    target_rows = {
        target: next(
            (row for row in rows if str(row["model"]).startswith(target)),
            None,
        )
        for target in target_names
    }
    summary = {
        "method": (
            "benchmark-as-item continuous ridge-regularized 2PL point estimate, "
            "five boards equal weight"
        ),
        "rank_policy": "no product/model constraints; no fixed missing-test penalty",
        "uncertainty_policy": (
            "0.67-SE is applied to theta within each board before CDF transformation and "
            "five-board aggregation; the resulting score and rank are sensitivity outputs, "
            "not the primary ranking"
        ),
        "protocol_policy": (
            "common AA protocol retained for Terminal-Bench 2.1, HLE, GPQA, AIME, "
            "MMMU-Pro, and IFBench; provider-reported same-family values are not row-wise substitutes"
        ),
        "source_model_rows": len(payload.get("models", [])),
        "exact_config_rows_fitted": len(models),
        "ranked_variant_groups": len(rows),
        "main_models": sum(row["evidence_tier"] == "Main" for row in rows),
        "provisional_models": sum(row["evidence_tier"] == "Provisional" for row in rows),
        "main_tests_per_board": MAIN_TESTS_PER_BOARD,
        "provisional_min_tests_per_board": PROVISIONAL_MIN_TESTS_PER_BOARD,
        **sanitation,
        "target_models": target_rows,
        "excluded_sparse_items": {
            board_id: board_data[board_id]["excluded_items"] for board_id in base.BOARD_ORDER
        },
    }
    result = {"summary": summary, "full_rankings": rows, "top50": top50}

    if write_outputs:
        output_dir.mkdir(parents=True, exist_ok=True)
        base.write_csv(output_dir / "evidence_only_top50.csv", top50)
        base.write_csv(output_dir / "evidence_only_full_rankings.csv", rows)
        (output_dir / "evidence_only_validation_summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_evidence_analysis(input_path=args.input, output_dir=args.output_dir)
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
