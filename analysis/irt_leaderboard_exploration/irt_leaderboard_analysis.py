"""Coverage-aware benchmark-as-item ranking exploration.

The repository has model-by-benchmark aggregate scores, not question-level
responses.  The Rasch and 2PL variants here are therefore continuous,
benchmark-as-item approximations rather than classical item-level IRT.

The analysis is deterministic and writes inspectable CSV/JSON outputs.  It
requires NumPy but does not require network access.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from statistics import NormalDist
from typing import Any, Iterable

import numpy as np

sys.dont_write_bytecode = True


ANALYSIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = ANALYSIS_DIR.parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "docs" / "data" / "models.json"

BOARD_ORDER = [
    "coding",
    "agentic-tool-work",
    "hard-reasoning",
    "knowledge-science",
    "instruction-context",
]
BOARD_LABELS = {
    "coding": "Coding",
    "agentic-tool-work": "Agentic/tool work",
    "hard-reasoning": "Hard reasoning",
    "knowledge-science": "Knowledge/science",
    "instruction-context": "Instruction/context",
}
CURRENT_BOARD_WEIGHTS = {
    "coding": 40.0,
    "agentic-tool-work": 24.0,
    "hard-reasoning": 20.0,
    "knowledge-science": 8.0,
    "instruction-context": 8.0,
}
EQUAL_BOARD_WEIGHTS = {board_id: 20.0 for board_id in BOARD_ORDER}

# Item calibration and model coverage use different thresholds.  Sparse items
# can inform a 1PL estimate after reliability down-weighting, but their 2PL
# discrimination is fixed unless at least 50 model families are observed.
ITEM_MIN_MODELS = 8
TWOPL_FREE_DISCRIMINATION_MIN_MODELS = 50
HARD_MIN_TESTS_PER_BOARD = 2
SOFT_TARGET_TESTS_PER_BOARD = 3

SCHEME_ORDER = [
    "baseline_aindex",
    "rasch_business",
    "twopl_equal",
    "robust_eb",
    "borda_breadth",
]
SCHEME_LABELS = {
    "baseline_aindex": "现行 AIndex（基准）",
    "rasch_business": "连续 1PL/Rasch 近似 + 现行板块权重",
    "twopl_equal": "强收缩连续 2PL 近似 + 五板块等权",
    "robust_eb": "稳健秩变换 + 贝叶斯式收缩",
    "borda_breadth": "收缩 Borda + 广度优先合成",
}


def item(item_id: str, label: str, *keys: str, scale: str = "percent") -> dict[str, Any]:
    return {"id": item_id, "label": label, "keys": list(keys), "scale": scale}


# Aliases for the same benchmark inside one board are collapsed into a single
# test family.  A family can still appear in more than one capability board,
# because the production taxonomy uses the same evaluation as evidence for
# different capabilities.  That cross-board local dependence is reported as a
# caveat rather than silently pretending the five board counts are independent.
BOARD_ITEMS: dict[str, list[dict[str, Any]]] = {
    "coding": [
        item("swe-bench-pro", "SWE-Bench Pro", "benchmark:swe-bench-pro"),
        item("livecodebench", "LiveCodeBench", "LiveCodeBench"),
        item("swe-bench-verified", "SWE-bench Verified", "benchmark:swe-bench-verified"),
        item("terminal-bench-hard", "Terminal-Bench Hard", "Terminal-Bench Hard"),
        item("terminal-bench-v2-1", "Terminal-Bench v2.1", "Terminal-Bench v2.1"),
        item("swe-bench-multilingual", "SWE-bench Multilingual", "benchmark:swe-bench-multilingual"),
        item("scicode", "SciCode", "SciCode"),
    ],
    "agentic-tool-work": [
        item("swe-bench-pro", "SWE-Bench Pro", "benchmark:swe-bench-pro"),
        item("browsecomp", "BrowseComp", "benchmark:browsecomp"),
        item("hle-tools", "HLE w/ tools", "benchmark:hle-tools"),
        item("mcp-atlas", "MCP-Atlas Public", "benchmark:mcp-atlas"),
        item("osworld-verified", "OSWorld-Verified", "benchmark:osworld-verified"),
        item("gdpval-wins-ties", "GDPval (wins or ties)", "benchmark:gdpval-wins-ties"),
        item("terminal-bench-hard", "Terminal-Bench Hard", "Terminal-Bench Hard"),
        item("gdpval-aa-elo", "GDPval-AA Elo", "benchmark:gdpval-aa-elo", scale="rank"),
        item("toolathlon", "Toolathlon", "benchmark:toolathlon"),
        item("terminal-bench-v2-1", "Terminal-Bench v2.1", "Terminal-Bench v2.1"),
        item("aa-lcr", "AA-LCR", "AA-LCR"),
    ],
    "hard-reasoning": [
        item("hle", "Humanity's Last Exam", "Humanity's Last Exam", "benchmark:hle"),
        item("frontiermath-tier-4", "FrontierMath Tier 4", "benchmark:frontiermath-tier-4"),
        item("critpt", "CritPt", "CritPt"),
        item("frontiermath-tier-1-3", "FrontierMath Tier 1-3", "benchmark:frontiermath-tier-1-3"),
        item("gpqa-diamond", "GPQA Diamond", "GPQA Diamond", "benchmark:gpqa-diamond"),
        item("aime-2025", "AIME 2025", "AIME 2025", "benchmark:aime-2025"),
        item("aime-2026", "AIME 2026", "benchmark:aime-2026"),
        item("hmmt-2026-feb", "HMMT Feb 2026", "benchmark:hmmt-2026-feb"),
    ],
    "knowledge-science": [
        item("omniscience", "AA-Omniscience Accuracy", "AA-Omniscience Accuracy"),
        item("gpqa-diamond", "GPQA Diamond", "GPQA Diamond", "benchmark:gpqa-diamond"),
        item("hle", "Humanity's Last Exam", "Humanity's Last Exam", "benchmark:hle"),
        item("mmmlu", "MMMLU", "benchmark:mmmlu"),
        item("mmmu-pro", "MMMU-Pro", "benchmark:mmmu-pro"),
        item("scicode", "SciCode", "SciCode"),
        item("mmlu-pro", "MMLU-Pro", "benchmark:mmlu-pro"),
    ],
    "instruction-context": [
        item("ifbench", "IFBench", "IFBench", "benchmark:ifbench"),
        item("aa-lcr", "AA-LCR", "AA-LCR"),
        item("critpt", "CritPt", "CritPt"),
        item("charxiv-tools", "CharXiv Reasoning w/ tools", "benchmark:charxiv-tools"),
        item("charxiv-no-tools", "CharXiv Reasoning", "benchmark:charxiv-no-tools"),
    ],
}

def finite_number(value: Any) -> float | None:
    if isinstance(value, bool) or value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def rounded(value: Any, digits: int = 6) -> Any:
    number = finite_number(value)
    return round(number, digits) if number is not None else None


def load_scoring_module(project_root: Path):
    root = str(project_root)
    if root not in sys.path:
        sys.path.insert(0, root)
    from scripts import build_docs_site  # pylint: disable=import-outside-toplevel

    return build_docs_site


def current_score(model: dict[str, Any], payload: dict[str, Any], scoring_module: Any) -> float | None:
    result = scoring_module.score_model_for_preset(
        model,
        payload["presets"]["zhihu-adjusted"],
        payload["metrics"],
        payload.get("metricBaselines"),
        payload.get("scoreBaselines", {}).get("aaIntelligenceMax"),
    )
    return finite_number(result.get("score"))


def dedupe_models(payload: dict[str, Any], scoring_module: Any) -> list[dict[str, Any]]:
    """Match the site's tier-priority rule, with current AIndex as tie-breaker."""

    best: dict[str, tuple[dict[str, Any], float]] = {}
    for model in payload["models"]:
        score = current_score(model, payload, scoring_module)
        if score is None:
            continue
        group = str(model.get("variantGroup") or model.get("slug") or model.get("model"))
        key = (int(model.get("variantPriority") or 0), score)
        if group not in best:
            best[group] = (model, score)
            continue
        current_model, current_value = best[group]
        current_key = (
            int(current_model.get("variantPriority") or 0),
            current_value,
        )
        if key > current_key:
            best[group] = (model, score)

    models: list[dict[str, Any]] = []
    for model, score in best.values():
        copy = dict(model)
        copy["_baseline_native"] = score
        models.append(copy)
    return sorted(models, key=lambda row: (str(row.get("creator") or ""), str(row.get("model") or "")))


def item_value(model: dict[str, Any], spec: dict[str, Any]) -> float | None:
    scores = model.get("scores", {})
    for key in spec["keys"]:
        value = finite_number(scores.get(key))
        if value is not None:
            return value
    return None


def average_tie_ranks(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        ranks[order[start:end]] = (start + 1 + end) / 2.0
        start = end
    return ranks


def probabilities_for_item(values: np.ndarray, scale: str) -> np.ndarray:
    result = np.full(values.shape, np.nan, dtype=float)
    observed = np.isfinite(values)
    raw = values[observed]
    if not len(raw):
        return result
    if scale == "rank":
        probabilities = (average_tie_ranks(raw) - 0.5) / len(raw)
    else:
        probabilities = raw / 100.0
    result[observed] = np.clip(probabilities, 0.01, 0.99)
    return result


def prepare_board_data(models: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    boards: dict[str, dict[str, Any]] = {}
    for board_id in BOARD_ORDER:
        specs = BOARD_ITEMS[board_id]
        raw = np.full((len(models), len(specs)), np.nan, dtype=float)
        for model_index, model in enumerate(models):
            for item_index, spec in enumerate(specs):
                value = item_value(model, spec)
                if value is not None:
                    raw[model_index, item_index] = value

        observed_counts = np.sum(np.isfinite(raw), axis=0)
        keep = observed_counts >= ITEM_MIN_MODELS
        kept_specs = [spec for spec, selected in zip(specs, keep, strict=True) if selected]
        kept_raw = raw[:, keep]
        probabilities = np.full(kept_raw.shape, np.nan, dtype=float)
        logits = np.full(kept_raw.shape, np.nan, dtype=float)
        for item_index, spec in enumerate(kept_specs):
            probabilities[:, item_index] = probabilities_for_item(kept_raw[:, item_index], spec["scale"])
            observed = np.isfinite(probabilities[:, item_index])
            p = probabilities[observed, item_index]
            logits[observed, item_index] = np.log(p / (1.0 - p))

        n_obs = np.sum(np.isfinite(kept_raw), axis=0).astype(int)
        reliability = n_obs / (n_obs + 20.0)
        coverage_eligible = np.ones(len(kept_specs), dtype=bool)
        boards[board_id] = {
            "id": board_id,
            "label": BOARD_LABELS[board_id],
            "items": kept_specs,
            "excluded_items": [
                {
                    "id": spec["id"],
                    "label": spec["label"],
                    "n_obs": int(count),
                    "reason": f"fewer than {ITEM_MIN_MODELS} model observations",
                }
                for spec, count, selected in zip(specs, observed_counts, keep, strict=True)
                if not selected
            ],
            "raw": kept_raw,
            "probabilities": probabilities,
            "logits": logits,
            "n_obs": n_obs,
            "reliability": reliability,
            "coverage_eligible": coverage_eligible,
        }
    return boards


def robust_sigma(residuals: Iterable[float]) -> float:
    values = np.asarray([value for value in residuals if math.isfinite(float(value))], dtype=float)
    if not len(values):
        return 1.0
    center = float(np.median(values))
    estimate = float(np.median(np.abs(values - center))) / 0.6744897501960817
    if not math.isfinite(estimate) or estimate < 0.25:
        estimate = float(np.sqrt(np.mean(np.square(values))))
    return float(np.clip(estimate, 0.35, 2.5))


def observation_counts(board: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    observed = np.isfinite(board["logits"])
    response_counts = np.sum(observed, axis=1).astype(int)
    coverage_counts = np.sum(observed & board["coverage_eligible"][None, :], axis=1).astype(int)
    return observed, response_counts, coverage_counts


def standardize_ability(
    theta: np.ndarray,
    se: np.ndarray,
    response_counts: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, float, float]:
    active = response_counts > 0
    if not np.any(active):
        return np.zeros_like(theta), np.ones_like(se), 0.0, 1.0
    mean = float(np.mean(theta[active]))
    std = float(np.std(theta[active]))
    if not math.isfinite(std) or std < 1e-6:
        std = 1.0
    standardized = (theta - mean) / std
    standardized[~active] = 0.0
    return standardized, se / std, mean, std


def coverage_adjusted_scores(
    theta: np.ndarray,
    se: np.ndarray,
    coverage_counts: np.ndarray,
    *,
    lcb_multiplier: float,
    shortfall_penalty: float,
) -> np.ndarray:
    adjusted = theta - lcb_multiplier * se
    adjusted -= shortfall_penalty * np.maximum(
        0, SOFT_TARGET_TESTS_PER_BOARD - coverage_counts
    )
    normal = NormalDist()
    return np.asarray([100.0 * normal.cdf(float(value)) for value in adjusted], dtype=float)


def fit_rasch(board: dict[str, Any]) -> dict[str, Any]:
    """Penalized continuous 1PL fit on empirical logits."""

    z = np.asarray(board["logits"], dtype=float)
    reliability = np.asarray(board["reliability"], dtype=float)
    observed, response_counts, coverage_counts = observation_counts(board)
    theta = np.zeros(z.shape[0], dtype=float)
    difficulty = np.zeros(z.shape[1], dtype=float)
    theta_ridge = 1.75
    item_ridge = 0.5

    for _ in range(120):
        previous = theta.copy()
        for model_index in range(z.shape[0]):
            mask = observed[model_index]
            if not np.any(mask):
                theta[model_index] = 0.0
                continue
            weights = reliability[mask]
            theta[model_index] = float(
                np.sum(weights * (z[model_index, mask] + difficulty[mask]))
                / (theta_ridge + np.sum(weights))
            )
        active = response_counts > 0
        shift = float(np.mean(theta[active])) if np.any(active) else 0.0
        theta[active] -= shift
        difficulty += shift
        for item_index in range(z.shape[1]):
            mask = observed[:, item_index]
            if np.any(mask):
                difficulty[item_index] = float(
                    np.sum(theta[mask] - z[mask, item_index]) / (np.sum(mask) + item_ridge)
                )
        if float(np.max(np.abs(theta - previous))) < 1e-8:
            break

    residual_values: list[float] = []
    for item_index in range(z.shape[1]):
        mask = observed[:, item_index]
        residual_values.extend(
            (z[mask, item_index] - (theta[mask] - difficulty[item_index])).tolist()
        )
    sigma = robust_sigma(residual_values)
    information = theta_ridge + np.sum(observed * reliability[None, :], axis=1)
    se = sigma / np.sqrt(np.maximum(information, 1e-9))
    theta_z, se_z, theta_mean, theta_std = standardize_ability(theta, se, response_counts)
    scores = coverage_adjusted_scores(
        theta_z,
        se_z,
        coverage_counts,
        lcb_multiplier=0.45,
        shortfall_penalty=0.45,
    )

    params = []
    for item_index, spec in enumerate(board["items"]):
        params.append(
            {
                "item_id": spec["id"],
                "item_label": spec["label"],
                "n_obs": int(board["n_obs"][item_index]),
                "reliability_weight": float(reliability[item_index]),
                "difficulty": float((difficulty[item_index] - theta_mean) / theta_std),
                # The raw 1PL slope is fixed at one. After reporting theta on
                # a standardized scale, the common reconstructed slope is the
                # pre-standardization theta SD rather than one.
                "discrimination": float(theta_std),
                "discrimination_status": "common_1pl_transformed",
            }
        )
    return {
        "theta": theta_z,
        "se": se_z,
        "response_counts": response_counts,
        "coverage_counts": coverage_counts,
        "scores": scores,
        "sigma": sigma,
        "params": params,
    }


def fit_twopl(board: dict[str, Any]) -> dict[str, Any]:
    """Strongly regularized 2PL; sparse-item discrimination stays fixed at 1."""

    z = np.asarray(board["logits"], dtype=float)
    reliability = np.asarray(board["reliability"], dtype=float)
    observed, response_counts, coverage_counts = observation_counts(board)
    theta = np.asarray(fit_rasch(board)["theta"], dtype=float)
    discrimination = np.ones(z.shape[1], dtype=float)
    intercept = np.zeros(z.shape[1], dtype=float)
    theta_ridge = 2.25
    discrimination_ridge = 12.0

    for _ in range(100):
        previous = theta.copy()
        for item_index in range(z.shape[1]):
            mask = observed[:, item_index]
            x = theta[mask]
            y = z[mask, item_index]
            if len(y) < 2:
                continue
            if int(board["n_obs"][item_index]) < TWOPL_FREE_DISCRIMINATION_MIN_MODELS:
                slope = 1.0
                constant = float(np.mean(y - x))
            else:
                design = np.column_stack([x, np.ones(len(x), dtype=float)])
                normal_matrix = design.T @ design
                normal_matrix[0, 0] += discrimination_ridge
                target = design.T @ y
                target[0] += discrimination_ridge
                try:
                    slope, constant = np.linalg.solve(normal_matrix, target)
                except np.linalg.LinAlgError:
                    slope, constant = 1.0, float(np.mean(y))
                slope = float(np.clip(slope, 0.35, 2.5))
                constant = float(np.mean(y - slope * x))
            discrimination[item_index] = slope
            intercept[item_index] = constant

        for model_index in range(z.shape[0]):
            mask = observed[model_index]
            if not np.any(mask):
                theta[model_index] = 0.0
                continue
            weights = reliability[mask]
            slopes = discrimination[mask]
            numerator = np.sum(weights * slopes * (z[model_index, mask] - intercept[mask]))
            denominator = theta_ridge + np.sum(weights * np.square(slopes))
            theta[model_index] = float(numerator / denominator)

        active = response_counts > 0
        shift = float(np.mean(theta[active])) if np.any(active) else 0.0
        theta[active] -= shift
        intercept += discrimination * shift
        if float(np.max(np.abs(theta - previous))) < 1e-8:
            break

    residual_values: list[float] = []
    per_item_rmse: list[float] = []
    for item_index in range(z.shape[1]):
        mask = observed[:, item_index]
        residual = z[mask, item_index] - (
            discrimination[item_index] * theta[mask] + intercept[item_index]
        )
        residual_values.extend(residual.tolist())
        per_item_rmse.append(
            float(np.sqrt(np.mean(np.square(residual)))) if len(residual) else math.nan
        )
    sigma = robust_sigma(residual_values)
    information = theta_ridge + np.sum(
        observed * reliability[None, :] * np.square(discrimination)[None, :], axis=1
    )
    se = sigma / np.sqrt(np.maximum(information, 1e-9))
    theta_z, se_z, theta_mean, theta_std = standardize_ability(theta, se, response_counts)
    scores = coverage_adjusted_scores(
        theta_z,
        se_z,
        coverage_counts,
        lcb_multiplier=0.67,
        shortfall_penalty=0.55,
    )

    params = []
    for item_index, spec in enumerate(board["items"]):
        adjusted_slope = float(discrimination[item_index] * theta_std)
        adjusted_intercept = float(intercept[item_index] + discrimination[item_index] * theta_mean)
        difficulty = -adjusted_intercept / adjusted_slope if adjusted_slope else math.nan
        free = int(board["n_obs"][item_index]) >= TWOPL_FREE_DISCRIMINATION_MIN_MODELS
        params.append(
            {
                "item_id": spec["id"],
                "item_label": spec["label"],
                "n_obs": int(board["n_obs"][item_index]),
                "reliability_weight": float(reliability[item_index]),
                "difficulty": float(difficulty),
                "discrimination": adjusted_slope,
                "discrimination_status": "estimated" if free else "fixed_sparse",
                "rmse": per_item_rmse[item_index],
            }
        )
    return {
        "theta": theta_z,
        "se": se_z,
        "response_counts": response_counts,
        "coverage_counts": coverage_counts,
        "scores": scores,
        "sigma": sigma,
        "params": params,
    }


def fit_robust_empirical_bayes(board: dict[str, Any]) -> dict[str, Any]:
    """Rank-normalize each item, then shrink sparse board means to the prior."""

    raw = np.asarray(board["raw"], dtype=float)
    reliability = np.asarray(board["reliability"], dtype=float)
    observed = np.isfinite(raw)
    response_counts = np.sum(observed, axis=1).astype(int)
    coverage_counts = np.sum(
        observed & board["coverage_eligible"][None, :], axis=1
    ).astype(int)
    z = np.full(raw.shape, np.nan, dtype=float)
    normal = NormalDist()
    for item_index in range(raw.shape[1]):
        mask = observed[:, item_index]
        values = raw[mask, item_index]
        if not len(values):
            continue
        ranks = average_tie_ranks(values)
        probabilities = (ranks - 0.375) / (len(values) + 0.25)
        z[mask, item_index] = [normal.inv_cdf(float(value)) for value in probabilities]

    theta = np.zeros(raw.shape[0], dtype=float)
    se = np.ones(raw.shape[0], dtype=float)
    prior_precision = 2.0
    for model_index in range(raw.shape[0]):
        mask = observed[model_index]
        weights = reliability[mask]
        if not np.any(mask):
            theta[model_index] = 0.0
            se[model_index] = 1.0 / math.sqrt(prior_precision)
            continue
        theta[model_index] = float(
            np.sum(weights * np.clip(z[model_index, mask], -2.5, 2.5))
            / (prior_precision + np.sum(weights))
        )
        se[model_index] = 1.0 / math.sqrt(prior_precision + float(np.sum(weights)))

    theta_z, se_z, _, _ = standardize_ability(theta, se, response_counts)
    scores = coverage_adjusted_scores(
        theta_z,
        se_z,
        coverage_counts,
        lcb_multiplier=0.50,
        shortfall_penalty=0.50,
    )
    return {
        "theta": theta_z,
        "se": se_z,
        "response_counts": response_counts,
        "coverage_counts": coverage_counts,
        "scores": scores,
        "sigma": 1.0,
        "params": [],
    }


def fit_shrunken_borda(board: dict[str, Any]) -> dict[str, Any]:
    """Transparent percentile baseline with small-sample and coverage shrinkage."""

    raw = np.asarray(board["raw"], dtype=float)
    reliability = np.asarray(board["reliability"], dtype=float)
    observed = np.isfinite(raw)
    response_counts = np.sum(observed, axis=1).astype(int)
    coverage_counts = np.sum(
        observed & board["coverage_eligible"][None, :], axis=1
    ).astype(int)
    percentiles = np.full(raw.shape, np.nan, dtype=float)
    pseudo_count = 20.0
    for item_index in range(raw.shape[1]):
        mask = observed[:, item_index]
        values = raw[mask, item_index]
        n_obs = len(values)
        if not n_obs:
            continue
        raw_percentile = (average_tie_ranks(values) - 0.5) / n_obs
        percentiles[mask, item_index] = (
            n_obs * raw_percentile + pseudo_count * 0.5
        ) / (n_obs + pseudo_count)

    theta = np.zeros(raw.shape[0], dtype=float)
    se = np.ones(raw.shape[0], dtype=float)
    normal = NormalDist()
    prior_precision = 2.0
    for model_index in range(raw.shape[0]):
        mask = observed[model_index]
        weights = reliability[mask]
        if not np.any(mask):
            theta[model_index] = 0.0
            se[model_index] = 1.0 / math.sqrt(prior_precision)
            continue
        mean_percentile = float(np.sum(weights * percentiles[model_index, mask]) / np.sum(weights))
        rank_z = normal.inv_cdf(float(np.clip(mean_percentile, 0.01, 0.99)))
        evidence = float(np.sum(weights))
        theta[model_index] = rank_z * evidence / (evidence + prior_precision)
        se[model_index] = 1.0 / math.sqrt(evidence + prior_precision)

    theta_z, se_z, _, _ = standardize_ability(theta, se, response_counts)
    scores = coverage_adjusted_scores(
        theta_z,
        se_z,
        coverage_counts,
        lcb_multiplier=0.50,
        shortfall_penalty=0.50,
    )
    return {
        "theta": theta_z,
        "se": se_z,
        "response_counts": response_counts,
        "coverage_counts": coverage_counts,
        "scores": scores,
        "sigma": 1.0,
        "params": [],
    }


def weighted_log1p_mean(
    board_scores: dict[str, np.ndarray], weights: dict[str, float]
) -> np.ndarray:
    numerator = np.zeros_like(next(iter(board_scores.values())), dtype=float)
    denominator = 0.0
    for board_id in BOARD_ORDER:
        weight = float(weights[board_id])
        numerator += weight * np.log1p(np.clip(board_scores[board_id] / 100.0, 0.0, None))
        denominator += weight
    return 100.0 * np.expm1(numerator / denominator)


def breadth_geometric_mean(board_scores: dict[str, np.ndarray]) -> np.ndarray:
    matrix = np.column_stack(
        [np.clip(board_scores[board_id], 0.1, 100.0) for board_id in BOARD_ORDER]
    )
    return np.exp(np.mean(np.log(matrix), axis=1))


def compute_board_fits(board_data: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        "rasch": {board_id: fit_rasch(board_data[board_id]) for board_id in BOARD_ORDER},
        "twopl": {board_id: fit_twopl(board_data[board_id]) for board_id in BOARD_ORDER},
        "robust": {
            board_id: fit_robust_empirical_bayes(board_data[board_id]) for board_id in BOARD_ORDER
        },
        "borda": {board_id: fit_shrunken_borda(board_data[board_id]) for board_id in BOARD_ORDER},
    }


def build_scheme_scores(
    models: list[dict[str, Any]],
    payload: dict[str, Any],
    board_fits: dict[str, dict[str, Any]],
) -> tuple[dict[str, np.ndarray], dict[str, dict[str, np.ndarray]], np.ndarray]:
    baseline_native = np.asarray([float(model["_baseline_native"]) for model in models], dtype=float)
    rasch_boards = {board_id: board_fits["rasch"][board_id]["scores"] for board_id in BOARD_ORDER}
    twopl_boards = {board_id: board_fits["twopl"][board_id]["scores"] for board_id in BOARD_ORDER}
    robust_boards = {board_id: board_fits["robust"][board_id]["scores"] for board_id in BOARD_ORDER}
    borda_boards = {board_id: board_fits["borda"][board_id]["scores"] for board_id in BOARD_ORDER}
    coverage_counts = np.column_stack(
        [board_fits["twopl"][board_id]["coverage_counts"] for board_id in BOARD_ORDER]
    )
    eligible = np.all(coverage_counts >= HARD_MIN_TESTS_PER_BOARD, axis=1)

    scores = {
        "baseline_aindex": baseline_native,
        "rasch_business": weighted_log1p_mean(rasch_boards, CURRENT_BOARD_WEIGHTS),
        "twopl_equal": weighted_log1p_mean(twopl_boards, EQUAL_BOARD_WEIGHTS),
        "robust_eb": weighted_log1p_mean(robust_boards, EQUAL_BOARD_WEIGHTS),
        "borda_breadth": breadth_geometric_mean(borda_boards),
    }
    for scheme_id in SCHEME_ORDER[1:]:
        scores[scheme_id] = scores[scheme_id].astype(float)
        scores[scheme_id][~eligible] = np.nan
    board_scores = {
        "baseline_aindex": {},
        "rasch_business": rasch_boards,
        "twopl_equal": twopl_boards,
        "robust_eb": robust_boards,
        "borda_breadth": borda_boards,
    }
    return scores, board_scores, eligible


def rank_scores(scores: np.ndarray, model_names: list[str]) -> tuple[np.ndarray, list[int]]:
    valid = np.isfinite(scores)
    order = sorted(
        np.flatnonzero(valid).tolist(),
        key=lambda index: (-float(scores[index]), model_names[index].lower()),
    )
    ranks = np.full(len(scores), np.nan, dtype=float)
    for rank, index in enumerate(order, start=1):
        ranks[index] = rank
    return ranks, order


def pearson(values_x: Iterable[float], values_y: Iterable[float]) -> float | None:
    x = np.asarray(list(values_x), dtype=float)
    y = np.asarray(list(values_y), dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    if np.sum(mask) < 3:
        return None
    x = x[mask] - np.mean(x[mask])
    y = y[mask] - np.mean(y[mask])
    denominator = math.sqrt(float(np.sum(np.square(x)) * np.sum(np.square(y))))
    if denominator <= 0:
        return None
    return float(np.sum(x * y) / denominator)


def spearman(values_x: Iterable[float], values_y: Iterable[float]) -> float | None:
    """Spearman correlation with pairwise finite filtering and average ties."""

    x = np.asarray(list(values_x), dtype=float)
    y = np.asarray(list(values_y), dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    if np.sum(mask) < 3:
        return None
    return pearson(average_tie_ranks(x[mask]), average_tie_ranks(y[mask]))


def drop_item_family(board: dict[str, Any], item_id: str) -> dict[str, Any]:
    """Drop one canonical benchmark family from a capability board."""

    keep = np.asarray([spec["id"] != item_id for spec in board["items"]], dtype=bool)
    return {
        **board,
        "items": [
            spec
            for spec, selected in zip(board["items"], keep, strict=True)
            if selected
        ],
        "raw": board["raw"][:, keep],
        "probabilities": board["probabilities"][:, keep],
        "logits": board["logits"][:, keep],
        "n_obs": board["n_obs"][keep],
        "reliability": board["reliability"][keep],
        "coverage_eligible": board["coverage_eligible"][keep],
    }


def leave_one_benchmark_out_stability(
    board_data: dict[str, dict[str, Any]],
    full_fits: dict[str, dict[str, Any]],
    full_scores: dict[str, np.ndarray],
    model_names: list[str],
) -> tuple[dict[str, dict[str, float | int | None]], list[dict[str, Any]]]:
    """Delete each unique benchmark family everywhere it appears.

    Correlations are conditional on models that remain eligible after an
    omission. Eligible-population retention is reported beside them so a high
    conditional correlation cannot hide a collapsing coverage gate.
    """

    full_ranks = {
        scheme_id: rank_scores(full_scores[scheme_id], model_names)[0]
        for scheme_id in SCHEME_ORDER
    }
    full_top50 = {
        scheme_id: set(rank_scores(full_scores[scheme_id], model_names)[1][:50])
        for scheme_id in SCHEME_ORDER
    }
    full_eligible = np.isfinite(full_scores[SCHEME_ORDER[1]])
    full_eligible_count = int(np.sum(full_eligible))
    results: dict[str, list[dict[str, float]]] = {
        scheme_id: [] for scheme_id in SCHEME_ORDER[1:]
    }
    detail_rows: list[dict[str, Any]] = []

    fitters = {
        "rasch": fit_rasch,
        "twopl": fit_twopl,
        "robust": fit_robust_empirical_bayes,
        "borda": fit_shrunken_borda,
    }
    item_ids = list(
        dict.fromkeys(
            spec["id"]
            for board_id in BOARD_ORDER
            for spec in board_data[board_id]["items"]
        )
    )
    for item_id in item_ids:
        affected_boards = [
            board_id
            for board_id in BOARD_ORDER
            if any(spec["id"] == item_id for spec in board_data[board_id]["items"])
        ]
        alternative_fits = {method: dict(full_fits[method]) for method in fitters}
        for board_id in affected_boards:
            reduced_board = drop_item_family(board_data[board_id], item_id)
            for method, fitter in fitters.items():
                alternative_fits[method][board_id] = fitter(reduced_board)

        coverage_counts = np.column_stack(
            [
                alternative_fits["twopl"][candidate]["coverage_counts"]
                for candidate in BOARD_ORDER
            ]
        )
        eligible = np.all(coverage_counts >= HARD_MIN_TESTS_PER_BOARD, axis=1)
        eligible_count = int(np.sum(eligible))
        eligible_retention = (
            float(np.sum(eligible & full_eligible)) / full_eligible_count
            if full_eligible_count
            else math.nan
        )
        rasch_boards = {
            candidate: alternative_fits["rasch"][candidate]["scores"]
            for candidate in BOARD_ORDER
        }
        twopl_boards = {
            candidate: alternative_fits["twopl"][candidate]["scores"]
            for candidate in BOARD_ORDER
        }
        robust_boards = {
            candidate: alternative_fits["robust"][candidate]["scores"]
            for candidate in BOARD_ORDER
        }
        borda_boards = {
            candidate: alternative_fits["borda"][candidate]["scores"]
            for candidate in BOARD_ORDER
        }
        alternatives = {
            "rasch_business": weighted_log1p_mean(rasch_boards, CURRENT_BOARD_WEIGHTS),
            "twopl_equal": weighted_log1p_mean(twopl_boards, EQUAL_BOARD_WEIGHTS),
            "robust_eb": weighted_log1p_mean(robust_boards, EQUAL_BOARD_WEIGHTS),
            "borda_breadth": breadth_geometric_mean(borda_boards),
        }
        for scheme_id, values in alternatives.items():
            values = values.astype(float)
            values[~eligible] = np.nan
            ranks, order = rank_scores(values, model_names)
            correlation = spearman(full_ranks[scheme_id], ranks)
            overlap = len(full_top50[scheme_id] & set(order[:50])) / 50.0
            metrics = {
                "conditional_spearman": (
                    correlation if correlation is not None else math.nan
                ),
                "top50_retention": overlap,
                "eligible_retention": eligible_retention,
            }
            results[scheme_id].append(metrics)
            detail_rows.append(
                {
                    "omitted_item_id": item_id,
                    "affected_boards": " | ".join(affected_boards),
                    "scheme_id": scheme_id,
                    "scheme": SCHEME_LABELS[scheme_id],
                    "full_eligible_models": full_eligible_count,
                    "post_omission_eligible_models": eligible_count,
                    "eligible_population_retention": rounded(eligible_retention),
                    "conditional_spearman": rounded(correlation),
                    "top50_retention": rounded(overlap),
                }
            )

    summary: dict[str, dict[str, float | int | None]] = {}
    for scheme_id, values in results.items():
        correlations = np.asarray(
            [value["conditional_spearman"] for value in values], dtype=float
        )
        overlaps = np.asarray(
            [value["top50_retention"] for value in values], dtype=float
        )
        eligible_retentions = np.asarray(
            [value["eligible_retention"] for value in values], dtype=float
        )
        summary[scheme_id] = {
            "mean_conditional_spearman": rounded(float(np.nanmean(correlations))),
            "min_conditional_spearman": rounded(float(np.nanmin(correlations))),
            "mean_top50_retention": rounded(float(np.nanmean(overlaps))),
            "min_top50_retention": rounded(float(np.nanmin(overlaps))),
            "mean_eligible_population_retention": rounded(
                float(np.nanmean(eligible_retentions))
            ),
            "min_eligible_population_retention": rounded(
                float(np.nanmin(eligible_retentions))
            ),
            "omissions": len(values),
        }
    return summary, detail_rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def coverage_profile(
    board_data: dict[str, dict[str, Any]],
    board_fits: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    model_count = len(next(iter(board_fits["twopl"].values()))["coverage_counts"])
    for board_id in BOARD_ORDER:
        counts = np.asarray(
            board_fits["twopl"][board_id]["coverage_counts"], dtype=int
        )
        response_counts = np.asarray(
            board_fits["twopl"][board_id]["response_counts"], dtype=int
        )
        rows.append(
            {
                "board_id": board_id,
                "board": BOARD_LABELS[board_id],
                "eligible_response_items": len(board_data[board_id]["items"]),
                "canonical_coverage_items": int(np.sum(board_data[board_id]["coverage_eligible"])),
                "excluded_sparse_items": len(board_data[board_id]["excluded_items"]),
                "models": model_count,
                "models_ge_1": int(np.sum(counts >= 1)),
                "models_ge_2": int(np.sum(counts >= 2)),
                "models_ge_3": int(np.sum(counts >= 3)),
                "share_ge_2": rounded(float(np.mean(counts >= 2))),
                "share_ge_3": rounded(float(np.mean(counts >= 3))),
                "median_canonical_tests": rounded(float(np.median(counts)), 2),
                "median_response_items": rounded(float(np.median(response_counts)), 2),
            }
        )
    return rows


def unique_family_counts(board_data: dict[str, dict[str, Any]]) -> np.ndarray:
    """Count observed canonical benchmark families once across all boards."""

    model_count = next(iter(board_data.values()))["raw"].shape[0]
    family_presence: dict[str, np.ndarray] = {}
    for board_id in BOARD_ORDER:
        board = board_data[board_id]
        for item_index, spec in enumerate(board["items"]):
            observed = np.isfinite(board["raw"][:, item_index])
            if spec["id"] in family_presence:
                family_presence[spec["id"]] |= observed
            else:
                family_presence[spec["id"]] = observed.copy()
    if not family_presence:
        return np.zeros(model_count, dtype=int)
    return np.sum(np.column_stack(list(family_presence.values())), axis=1).astype(int)


def build_rank_rows(
    models: list[dict[str, Any]],
    scores: dict[str, np.ndarray],
    board_scores: dict[str, dict[str, np.ndarray]],
    board_data: dict[str, dict[str, Any]],
    board_fits: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, np.ndarray]]:
    model_names = [str(model.get("model") or "") for model in models]
    ranks: dict[str, np.ndarray] = {}
    orders: dict[str, list[int]] = {}
    for scheme_id in SCHEME_ORDER:
        ranks[scheme_id], orders[scheme_id] = rank_scores(scores[scheme_id], model_names)
    baseline_ranks = ranks["baseline_aindex"]
    coverage_counts = {
        board_id: np.asarray(
            board_fits["twopl"][board_id]["coverage_counts"], dtype=int
        )
        for board_id in BOARD_ORDER
    }
    unique_counts = unique_family_counts(board_data)

    full_rows: list[dict[str, Any]] = []
    for scheme_id in SCHEME_ORDER:
        population = len(orders[scheme_id])
        for index in orders[scheme_id]:
            counts = [int(coverage_counts[board_id][index]) for board_id in BOARD_ORDER]
            row: dict[str, Any] = {
                "scheme_id": scheme_id,
                "scheme": SCHEME_LABELS[scheme_id],
                "rank": int(ranks[scheme_id][index]),
                "model": model_names[index],
                "creator": str(models[index].get("creator") or ""),
                "variant_group": str(models[index].get("variantGroup") or ""),
                "score": rounded(scores[scheme_id][index], 4),
                "rank_percentile": rounded(
                    100.0
                    if population <= 1
                    else 100.0
                    * (population - int(ranks[scheme_id][index]))
                    / (population - 1),
                    2,
                ),
                "baseline_rank": (
                    int(baseline_ranks[index])
                    if math.isfinite(baseline_ranks[index])
                    else None
                ),
                "rank_change_vs_baseline": (
                    int(baseline_ranks[index] - ranks[scheme_id][index])
                    if math.isfinite(baseline_ranks[index])
                    else None
                ),
                "board_test_slots_total": sum(counts),
                "unique_benchmark_families": int(unique_counts[index]),
                "min_board_tests": min(counts),
                "boards_below_soft_target": sum(
                    count < SOFT_TARGET_TESTS_PER_BOARD for count in counts
                ),
            }
            if scheme_id == "baseline_aindex":
                row["native_aindex"] = rounded(models[index]["_baseline_native"], 4)
            for board_id, count in zip(BOARD_ORDER, counts, strict=True):
                row[f"{board_id}_tests"] = count
                if board_scores[scheme_id]:
                    row[f"{board_id}_score"] = rounded(
                        board_scores[scheme_id][board_id][index], 3
                    )
            full_rows.append(row)
    top50_rows = [row for row in full_rows if int(row["rank"]) <= 50]
    return full_rows, top50_rows, ranks


def scheme_diagnostics(
    scores: dict[str, np.ndarray],
    ranks: dict[str, np.ndarray],
    top50_rows: list[dict[str, Any]],
    eligible: np.ndarray,
    stability: dict[str, dict[str, Any]],
    board_slot_coverage: np.ndarray,
    unique_coverage: np.ndarray,
) -> list[dict[str, Any]]:
    baseline_top = {
        row["variant_group"]
        for row in top50_rows
        if row["scheme_id"] == "baseline_aindex"
    }
    rows = []
    for scheme_id in SCHEME_ORDER:
        scheme_top = [row for row in top50_rows if row["scheme_id"] == scheme_id]
        scheme_groups = {row["variant_group"] for row in scheme_top}
        top_slot_coverage = np.asarray(
            [row["board_test_slots_total"] for row in scheme_top], dtype=float
        )
        top_unique_coverage = np.asarray(
            [row["unique_benchmark_families"] for row in scheme_top], dtype=float
        )
        rows.append(
            {
                "scheme_id": scheme_id,
                "scheme": SCHEME_LABELS[scheme_id],
                "ranked_models": int(np.sum(np.isfinite(scores[scheme_id]))),
                "top50_overlap_with_baseline": len(scheme_groups & baseline_top),
                "spearman_vs_baseline": rounded(
                    spearman(ranks[scheme_id], ranks["baseline_aindex"])
                ),
                "score_unique_coverage_spearman": rounded(
                    spearman(scores[scheme_id], unique_coverage)
                ),
                "score_board_slot_coverage_spearman": rounded(
                    spearman(scores[scheme_id], board_slot_coverage)
                ),
                "top50_median_unique_benchmark_families": rounded(
                    float(np.median(top_unique_coverage))
                    if len(top_unique_coverage)
                    else None,
                    2,
                ),
                "top50_median_board_test_slots": rounded(
                    float(np.median(top_slot_coverage))
                    if len(top_slot_coverage)
                    else None,
                    2,
                ),
                "top50_models_with_any_board_below_3": sum(
                    int(row["boards_below_soft_target"]) > 0 for row in scheme_top
                ),
                "hard_floor_eligible_models": int(np.sum(eligible)),
                "lobo_mean_conditional_spearman": stability.get(scheme_id, {}).get(
                    "mean_conditional_spearman"
                ),
                "lobo_min_conditional_spearman": stability.get(scheme_id, {}).get(
                    "min_conditional_spearman"
                ),
                "lobo_mean_top50_retention": stability.get(scheme_id, {}).get(
                    "mean_top50_retention"
                ),
                "lobo_min_top50_retention": stability.get(scheme_id, {}).get(
                    "min_top50_retention"
                ),
                "lobo_mean_eligible_population_retention": stability.get(
                    scheme_id, {}
                ).get("mean_eligible_population_retention"),
                "lobo_min_eligible_population_retention": stability.get(
                    scheme_id, {}
                ).get("min_eligible_population_retention"),
            }
        )
    return rows


def pairwise_rank_rows(ranks: dict[str, np.ndarray]) -> list[dict[str, Any]]:
    return [
        {
            "scheme_left": left,
            "scheme_left_label": SCHEME_LABELS[left],
            "scheme_right": right,
            "scheme_right_label": SCHEME_LABELS[right],
            "spearman": rounded(spearman(ranks[left], ranks[right])),
        }
        for left in SCHEME_ORDER
        for right in SCHEME_ORDER
    ]


def item_parameter_rows(
    board_data: dict[str, dict[str, Any]],
    board_fits: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for method in ("rasch", "twopl"):
        for board_id in BOARD_ORDER:
            for spec, param in zip(
                board_data[board_id]["items"],
                board_fits[method][board_id]["params"],
                strict=True,
            ):
                rows.append(
                    {
                        "method": method,
                        "board_id": board_id,
                        "board": BOARD_LABELS[board_id],
                        "item_id": spec["id"],
                        "item": spec["label"],
                        "source_keys": " | ".join(spec["keys"]),
                        "scale": spec["scale"],
                        "counts_for_board_gate": True,
                        "n_obs": param["n_obs"],
                        "reliability_weight": rounded(param["reliability_weight"]),
                        "difficulty": rounded(param["difficulty"]),
                        "discrimination": rounded(param["discrimination"]),
                        "discrimination_status": param["discrimination_status"],
                        "rmse": rounded(param.get("rmse")),
                        "board_residual_sigma": rounded(
                            board_fits[method][board_id]["sigma"]
                        ),
                    }
                )
    return rows


def data_quality_summary(payload: dict[str, Any], project_root: Path) -> dict[str, Any]:
    metric_keys = [str(metric["key"]) for metric in payload.get("metrics", [])]
    non_null = sum(
        finite_number(model.get("scores", {}).get(key)) is not None
        for model in payload.get("models", [])
        for key in metric_keys
    )
    cells = len(payload.get("models", [])) * len(metric_keys)
    has_external = []
    aa_values_with_external = []
    aa_values_without_external = []
    for model in payload.get("models", []):
        external = any(
            key.startswith("benchmark:")
            and finite_number(model.get("scores", {}).get(key)) is not None
            for key in metric_keys
        )
        has_external.append(external)
        intelligence = finite_number(model.get("aa", {}).get("aa-intelligence"))
        if intelligence is not None:
            (aa_values_with_external if external else aa_values_without_external).append(
                intelligence
            )

    benchmark_path = project_root / "data" / "benchmarks" / "benchmark_scores.json"
    benchmark_payload = json.loads(benchmark_path.read_text(encoding="utf-8"))
    groups: dict[tuple[str, str], list[float]] = {}
    for result in benchmark_payload.get("results", []):
        key = (
            str(result.get("benchmarkId") or ""),
            " ".join(str(result.get("model") or "").lower().split()),
        )
        value = finite_number(result.get("value"))
        if value is not None:
            groups.setdefault(key, []).append(value)
    duplicate_groups = {key: values for key, values in groups.items() if len(values) > 1}
    conflict_groups = {
        key: values for key, values in duplicate_groups.items() if len(set(values)) > 1
    }
    active_ids = {
        key.removeprefix("benchmark:")
        for board_id in BOARD_ORDER
        for spec in BOARD_ITEMS[board_id]
        for key in spec["keys"]
        if key.startswith("benchmark:")
    }
    active_conflicts = {
        key: values for key, values in conflict_groups.items() if key[0] in active_ids
    }
    return {
        "score_matrix_non_null": non_null,
        "score_matrix_cells": cells,
        "score_matrix_density": rounded(non_null / cells if cells else None),
        "model_rows_with_external_score": int(sum(has_external)),
        "model_rows_without_external_score": int(len(has_external) - sum(has_external)),
        "aa_intelligence_median_with_external": rounded(
            float(np.median(aa_values_with_external)) if aa_values_with_external else None, 4
        ),
        "aa_intelligence_median_without_external": rounded(
            float(np.median(aa_values_without_external))
            if aa_values_without_external
            else None,
            4,
        ),
        "external_result_rows": len(benchmark_payload.get("results", [])),
        "external_duplicate_model_benchmark_groups": len(duplicate_groups),
        "external_conflicting_model_benchmark_groups": len(conflict_groups),
        "active_conflicting_model_benchmark_groups": len(active_conflicts),
    }


def run_analysis(
    *,
    input_path: Path = DEFAULT_INPUT,
    output_dir: Path = ANALYSIS_DIR / "outputs",
    write_outputs: bool = True,
    run_stability: bool = True,
) -> dict[str, Any]:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    scoring_module = load_scoring_module(PROJECT_ROOT)
    models = dedupe_models(payload, scoring_module)
    board_data = prepare_board_data(models)
    board_fits = compute_board_fits(board_data)
    scores, board_scores, eligible = build_scheme_scores(models, payload, board_fits)
    model_names = [str(model.get("model") or "") for model in models]
    if run_stability:
        stability, stability_rows = leave_one_benchmark_out_stability(
            board_data, board_fits, scores, model_names
        )
    else:
        stability, stability_rows = {}, []
    full_rows, top50_rows, ranks = build_rank_rows(
        models, scores, board_scores, board_data, board_fits
    )
    coverage_rows = coverage_profile(board_data, board_fits)
    coverage_matrix = np.column_stack(
        [
            board_fits["twopl"][board_id]["coverage_counts"]
            for board_id in BOARD_ORDER
        ]
    )
    board_slot_coverage = np.sum(coverage_matrix, axis=1)
    unique_coverage = unique_family_counts(board_data)
    diagnostic_rows = scheme_diagnostics(
        scores,
        ranks,
        top50_rows,
        eligible,
        stability,
        board_slot_coverage,
        unique_coverage,
    )
    pairwise_rows = pairwise_rank_rows(ranks)
    parameter_rows = item_parameter_rows(board_data, board_fits)
    excluded_items = [
        {"board_id": board_id, "board": BOARD_LABELS[board_id], **entry}
        for board_id in BOARD_ORDER
        for entry in board_data[board_id]["excluded_items"]
    ]
    quality = data_quality_summary(payload, PROJECT_ROOT)

    summary = {
        "data_generated_at": payload.get("generatedAt"),
        "analysis_generated_from": str(input_path.relative_to(PROJECT_ROOT)).replace(
            "\\", "/"
        ),
        "source_model_rows": len(payload.get("models", [])),
        "source_variant_groups": payload.get("summary", {}).get("variantGroups"),
        "deduped_scorable_models": len(models),
        "hard_floor_eligible_models": int(np.sum(eligible)),
        "item_min_models": ITEM_MIN_MODELS,
        "twopl_free_discrimination_min_models": TWOPL_FREE_DISCRIMINATION_MIN_MODELS,
        "hard_min_tests_per_board": HARD_MIN_TESTS_PER_BOARD,
        "soft_target_tests_per_board": SOFT_TARGET_TESTS_PER_BOARD,
        "production_metric_slots_before_alias_collapse": sum(
            len(group.get("metrics", []))
            for group in payload.get("presets", {})
            .get("zhihu-adjusted", {})
            .get("groups", [])
        ),
        "canonical_board_item_slots_before_filter": sum(
            len(BOARD_ITEMS[board_id]) for board_id in BOARD_ORDER
        ),
        "eligible_response_item_slots": sum(
            len(board_data[board_id]["items"]) for board_id in BOARD_ORDER
        ),
        "canonical_coverage_item_slots": sum(
            int(np.sum(board_data[board_id]["coverage_eligible"]))
            for board_id in BOARD_ORDER
        ),
        "unique_eligible_benchmark_families": len(
            {
                spec["id"]
                for board_id in BOARD_ORDER
                for spec in board_data[board_id]["items"]
            }
        ),
        "cross_board_duplicate_item_slots": sum(
            len(board_data[board_id]["items"]) for board_id in BOARD_ORDER
        )
        - len(
            {
                spec["id"]
                for board_id in BOARD_ORDER
                for spec in board_data[board_id]["items"]
            }
        ),
        "excluded_sparse_item_slots": len(excluded_items),
        "all_boards_ge_soft_target_models": int(
            np.sum(np.all(coverage_matrix >= SOFT_TARGET_TESTS_PER_BOARD, axis=1))
        ),
        "twopl_estimated_discrimination_item_slots": sum(
            param["discrimination_status"] == "estimated"
            for board_id in BOARD_ORDER
            for param in board_fits["twopl"][board_id]["params"]
        ),
        "twopl_fixed_sparse_discrimination_item_slots": sum(
            param["discrimination_status"] == "fixed_sparse"
            for board_id in BOARD_ORDER
            for param in board_fits["twopl"][board_id]["params"]
        ),
        "classic_item_level_irt_supported": False,
        "modeling_scope": "benchmark-as-item continuous IRT / IRT-inspired",
        "stability_scope": (
            "leave one unique benchmark family out across every board; rank "
            "correlations are conditional on post-omission eligible models"
        ),
        "data_quality": quality,
        "schemes": diagnostic_rows,
        "coverage": coverage_rows,
        "excluded_items": excluded_items,
        "stability": stability,
    }
    result = {
        "summary": summary,
        "models": models,
        "board_data": board_data,
        "board_fits": board_fits,
        "scores": scores,
        "board_scores": board_scores,
        "eligible": eligible,
        "full_rankings": full_rows,
        "top50": top50_rows,
        "coverage_profile": coverage_rows,
        "scheme_diagnostics": diagnostic_rows,
        "pairwise_ranks": pairwise_rows,
        "item_parameters": parameter_rows,
        "lobo_stability_by_item": stability_rows,
    }

    if write_outputs:
        output_dir.mkdir(parents=True, exist_ok=True)
        write_csv(output_dir / "top50_all_schemes.csv", top50_rows)
        write_csv(output_dir / "full_rankings_all_schemes.csv", full_rows)
        write_csv(output_dir / "coverage_profile.csv", coverage_rows)
        write_csv(output_dir / "scheme_diagnostics.csv", diagnostic_rows)
        write_csv(output_dir / "pairwise_rank_correlations.csv", pairwise_rows)
        write_csv(output_dir / "item_parameters.csv", parameter_rows)
        write_csv(output_dir / "lobo_stability_by_item.csv", stability_rows)
        (output_dir / "validation_summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=ANALYSIS_DIR / "outputs")
    parser.add_argument("--skip-stability", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_analysis(
        input_path=args.input,
        output_dir=args.output_dir,
        write_outputs=True,
        run_stability=not args.skip_stability,
    )
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
