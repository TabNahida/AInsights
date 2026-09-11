"""Production AIndex mixed Core scheme 07, with anonymous fixed weights.

Representatives are fixed before eligibility. Missing observations retain their
fixed share of zero points; they are never filled or borrowed. Extension trends
are fitted on complete boards in the representative cohort and reused unchanged
for exact configurations. No model-name acceptance conditions enter production.
"""
from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

try:
    from . import aindex_scheme18 as math_helpers
    from .evidence_only_ranking_analysis import sanitize_models
except ImportError:  # Direct script imports.
    import aindex_scheme18 as math_helpers
    from evidence_only_ranking_analysis import sanitize_models

METHOD_ID = "aindex_mixed_core"
CANDIDATE_ID = "mixed_core_mc07"
CORE_FIT = "fixed_share_arithmetic"
CAP_RULE = "mean_plus_sqrt2_sd"
EXTENSION_AGGREGATOR = "logsumexp_residual_t1"
BOARD_ORDER = math_helpers.BOARD_ORDER
BOARD_WEIGHTS = dict(zip(BOARD_ORDER, (12, 9, 22, 37, 20), strict=True))
CORE_ITEMS = {
    "coding": ("Terminal-Bench v4.0", "SciCode"),
    "agentic-tool-work": ("AutomationBench-AA", "τ³-Banking"),
    "hard-reasoning": ("CritPt",),
    "knowledge-science": ("AA-Omniscience Accuracy", "GDP.pdf"),
    "instruction-context": ("AA-LCR v1.1",),
}
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_FILENAMES = {
    "full_rankings": "full_rankings_aindex_mixed_core.csv",
    "top50": "top50_aindex_mixed_core.csv",
    "exact_config_full_rankings": "full_rankings_exact_config_aindex_mixed_core.csv",
    "exact_config_top50": "top50_exact_config_aindex_mixed_core.csv",
    "validation": "aindex_mixed_core_validation_summary.json",
}
finite_number = math_helpers.finite_number
score_value = math_helpers.score_value
write_csv = math_helpers.write_csv
rank_rows = math_helpers.rank_rows


def canonical_family(key: str) -> str:
    if key.startswith("Terminal-Bench") or key.startswith("benchmark:terminal-bench"):
        return "terminal-bench"
    aliases = {
        "AA-LCR": "aa-lcr", "AA-LCR v1.1": "aa-lcr",
        "AA-Omniscience Accuracy": "omniscience",
        "AA-Omniscience Non-Hallucination Rate": "omniscience",
        "LiveCodeBench": "livecodebench", "benchmark:livecodebench": "livecodebench",
        "GDPval-AA": "gdpval", "GDPval-AA v2": "gdpval",
    }
    if key in aliases:
        return aliases[key]
    for registry in (math_helpers.CORE_POLICIES, math_helpers.EXTENSION_POLICIES):
        for policies in registry.values():
            for policy in policies:
                if policy.score_key == key:
                    return policy.canonical_family
    return key


_CORE_FAMILIES = {canonical_family(key) for keys in CORE_ITEMS.values() for key in keys}
EXTENSION_POLICIES = {
    board: tuple(policy for policy in policies
                 if canonical_family(policy.score_key) not in _CORE_FAMILIES
                 and canonical_family(policy.score_key) != "terminal-bench")
    for board, policies in math_helpers.EXTENSION_POLICIES.items()
}
EXTENSION_ITEMS = {
    board: tuple(policy.score_key for policy in policies)
    for board, policies in EXTENSION_POLICIES.items()
}


def source_models(payload: Mapping[str, Any], raw_rows=None) -> list[dict[str, Any]]:
    """Retain direct exact-config evidence and restore AA's raw observations.

Only explicitly supplied raw rows are used. Unmatched synthetic/source models
keep their evidence; a matching AA row's blank cell is a missing observation.
"""
    models, _ = sanitize_models(payload, exact_config_only=True)
    if raw_rows is not None:
        from ArtificialAnalysis.scrape_artificial_analysis import SCORE_SPECS
        by_slug = {str(row["slug"]): row for row in raw_rows}
        for model in models:
            raw = by_slug.get(str(model.get("slug") or ""))
            if raw is not None:
                for spec in SCORE_SPECS:
                    model["scores"][spec.column] = finite_number(raw.get(spec.column))
    return models


def representatives(models: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    selected = {}
    slugs = set()
    for model in sorted(models, key=lambda m: (
        -(finite_number(m.get("variantPriority")) or 0.0), str(m.get("slug") or "")
    )):
        slug = str(model.get("slug") or "")
        group = str(model.get("variantGroup") or "")
        if not slug or slug in slugs or not group:
            raise AssertionError("source models need unique slugs and nonempty variant groups")
        slugs.add(slug)
        selected.setdefault(group, model)
    return list(selected.values())


def prepare(models: Sequence[Mapping[str, Any]]):
    eligible, excluded = [], []
    for model in models:
        absent = {board: [key for key in CORE_ITEMS[board] if score_value(model, key) is None]
                  for board in BOARD_ORDER}
        missing = [key for board in BOARD_ORDER for key in absent[board]]
        empty = [board for board in BOARD_ORDER if len(absent[board]) == len(CORE_ITEMS[board])]
        if empty or len(missing) >= 4:
            excluded.append({"slug": model["slug"], "missing_core_items": missing,
                             "missing_core_count": len(missing), "empty_boards": empty,
                             "reason": (["board_missing_all"] if empty else [])
                             + (["missing_at_least_four"] if len(missing) >= 4 else [])})
        else:
            eligible.append(model)
    return eligible, {"requested_count": len(models), "eligible_count": len(eligible),
                      "excluded_count": len(excluded), "excluded_models": excluded}


def score_matrix(models, keys):
    return math_helpers.score_matrix(models, keys).reshape(len(models), len(keys))


def fixed_share_base(raw):
    raw = np.asarray(raw, dtype=float)
    if raw.ndim != 2 or raw.shape[1] not in (1, 2):
        raise AssertionError("Core matrix must have one or two configured items")
    finite = np.isfinite(raw)
    if np.any((raw[finite] < 0) | (raw[finite] > 100)):
        raise AssertionError("Core observations must be on the 0--100 scale")
    return np.where(finite, raw, 0.0).sum(axis=1) / raw.shape[1]


def fit_calibration(models: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if not models:
        raise AssertionError("mixed Core calibration population is empty")
    if len({m["variantGroup"] for m in models}) != len(models):
        raise AssertionError("calibration requires one fixed representative per group")
    eligible, audit = prepare(models)
    if audit["excluded_count"]:
        raise AssertionError("ineligible models cannot fit calibration")
    boards, residual_arrays = {}, []
    for board in BOARD_ORDER:
        raw = score_matrix(eligible, CORE_ITEMS[board])
        complete = np.isfinite(raw).all(axis=1)
        ext = score_matrix(eligible, EXTENSION_ITEMS[board])
        residuals, trends = math_helpers._fit_positive_residuals(fixed_share_base(raw)[complete], ext[complete])
        residual_arrays.append(residuals)
        boards[board] = {
            "core_items": [{"item_id": key, "score_key": key, "canonical_family": canonical_family(key)}
                           for key in CORE_ITEMS[board]],
            "extension_items": [{"item_id": p.item_id, "score_key": p.score_key,
                                 "canonical_family": p.canonical_family, **trend}
                                for p, trend in zip(EXTENSION_POLICIES[board], trends, strict=True)],
            "core_item_count": len(CORE_ITEMS[board]),
            "extension_item_count": len(EXTENSION_ITEMS[board]),
            "complete_core_models": int(complete.sum()), "weight": BOARD_WEIGHTS[board],
        }
    positives = np.asarray([value for array in residual_arrays for value in array.flat
                            if np.isfinite(value) and value > 0], dtype=float)
    cap = math_helpers.derive_cap(residual_arrays) if len(positives) else 0.0
    return {
        "method_id": METHOD_ID, "candidate_id": CANDIDATE_ID,
        "policy_version": "mixed-core-mc07", "core_fit": CORE_FIT,
        "extension_aggregator": EXTENSION_AGGREGATOR, "extension_pool": "independent_audit",
        "cap_rule": CAP_RULE, "bonus_cap_per_board": cap,
        "pooled_positive_residual_count": len(positives),
        "pooled_positive_residual_mean": float(np.mean(positives)) if len(positives) else 0.0,
        "pooled_positive_residual_population_sd": float(np.std(positives)) if len(positives) else 0.0,
        "board_order": list(BOARD_ORDER), "board_weights": dict(BOARD_WEIGHTS),
        "population_size": len(models), "population_slugs": [m["slug"] for m in models],
        "population_variant_groups": [m["variantGroup"] for m in models],
        "representative_policy": "variantPriority descending then slug, before eligibility",
        "missing_policy": "fixed shares; exclude any board with no Core evidence or at least four missing Core items",
        "fit_apply_policy": "fit complete boards of fixed representatives once; apply unchanged to exact configurations",
        "extension_policy": "fit and award only on boards with every configured Core observed; globally exclude Core families and legacy Terminal",
        "boards": boards,
    }


def score_models(models, calibration, *, ranking_grain="variant_group"):
    if not models:
        return []
    _, eligibility = prepare(models)
    if eligibility["excluded_count"]:
        raise AssertionError("ineligible model passed to mixed Core scoring")
    if (calibration.get("method_id") != METHOD_ID
        or calibration.get("candidate_id") != CANDIDATE_ID
        or calibration.get("board_weights") != BOARD_WEIGHTS):
        raise AssertionError("mixed Core calibration identity or weights differ")
    cap = finite_number(calibration.get("bonus_cap_per_board"))
    if cap is None or cap < 0:
        raise AssertionError("invalid mixed Core bonus cap")
    values = {}
    for board in BOARD_ORDER:
        meta = calibration["boards"][board]
        if [i["score_key"] for i in meta["core_items"]] != list(CORE_ITEMS[board]):
            raise AssertionError("mixed Core calibration Core registry differs")
        if [i["score_key"] for i in meta["extension_items"]] != list(EXTENSION_ITEMS[board]):
            raise AssertionError("mixed Core calibration extension registry differs")
        raw = score_matrix(models, CORE_ITEMS[board])
        complete = np.isfinite(raw).all(axis=1)
        base = fixed_share_base(raw)
        ext = score_matrix(models, EXTENSION_ITEMS[board])
        residuals = math_helpers._apply_extension_trends(base, ext, meta["extension_items"])
        residuals[~complete] = np.nan
        bonus = math_helpers.extension_bonus(residuals, cap)
        values[board] = (raw, base, bonus, np.minimum(100, base + bonus), ext)
    rows = []
    total_available = sum(len(CORE_ITEMS[b]) + len(EXTENSION_ITEMS[b]) for b in BOARD_ORDER)
    for index, model in enumerate(models):
        missing = [key for b in BOARD_ORDER for key in CORE_ITEMS[b] if score_value(model, key) is None]
        row = {"method": METHOD_ID, "candidate_id": CANDIDATE_ID, "rank": 0,
               "model": str(model.get("model") or ""), "creator": str(model.get("creator") or ""),
               "slug": model["slug"], "variant_group": model["variantGroup"], "ranking_grain": ranking_grain,
               "missing_core_count": len(missing), "missing_core_items": "; ".join(missing),
               "core_tests_total": 8 - len(missing), "items_total": 8,
               "evidence_tier": "Core complete" if not missing else "Core partial",
               "score_scale": "0-100 weighted additive five-board points",
               "ranking_key": "unrounded_score_desc_then_slug_model_for_exact_ties"}
        points, core_points, slots = [], [], 0
        families, extensions = set(), set()
        for board in BOARD_ORDER:
            raw, base, bonus, scores, ext = values[board]
            weight = BOARD_WEIGHTS[board]
            count, extension_count = int(np.isfinite(raw[index]).sum()), int(np.isfinite(ext[index]).sum())
            score, base_score, bonus_score = float(scores[index]), float(base[index]), float(bonus[index])
            point = score * weight / 100
            points.append(point)
            core_points.append(base_score * weight / 100)
            slots += count + extension_count
            row.update({f"{board}_core_score": base_score, f"{board}_extension_bonus": bonus_score,
                        f"{board}_core_tests": count, f"{board}_extension_tests": extension_count,
                        f"{board}_tests": count + extension_count, f"{board}_weight": weight,
                        f"{board}_core_item_pool_size": len(CORE_ITEMS[board]),
                        f"{board}_extension_item_pool_size": len(EXTENSION_ITEMS[board]),
                        f"{board}_score_full_precision": format(score, ".17g"), f"{board}_score": round(score, 6),
                        f"{board}_points_full_precision": format(point, ".17g"), f"{board}_points": round(point, 6)})
            for slot, key in enumerate(CORE_ITEMS[board], 1):
                value = score_value(model, key)
                row.update({f"{board}_item{slot}": key, f"{board}_item{slot}_adjusted": value,
                            f"{board}_item{slot}_observed": value is not None,
                            f"{board}_item{slot}_base_points": (value or 0) * weight / (100 * len(CORE_ITEMS[board]))})
                if value is not None:
                    families.add(canonical_family(key))
            extensions.update(canonical_family(key) for key in EXTENSION_ITEMS[board] if score_value(model, key) is not None)
        score = math.fsum(points)
        row.update(score_full_precision=format(score, ".17g"), score=round(score, 6), final_score=round(score, 6),
                   core_only_score=math.fsum(core_points), points_sum_full_precision=format(score, ".17g"),
                   board_test_slots_total=slots, board_test_slots_available=total_available,
                   unique_benchmark_families=len(families | extensions), unique_extension_families=len(extensions),
                   evidence_coverage_score=round(100 * slots / total_available, 6))
        rows.append(row)
    return rows


def validate_rankings(full_rankings, exact_config_full_rankings, calibration):
    def audit(rows, grain):
        failures, slugs, groups = [], set(), set()
        previous = (-math.inf, "", "")
        max_error = 0.0
        for rank, row in enumerate(rows, 1):
            slug, score = row["slug"], float(row["score_full_precision"])
            order = (-score, slug, row["model"])
            if rank != row["rank"] or order < previous or not math.isfinite(score):
                failures.append(f"{slug}: invalid rank/order/score")
            previous = order
            if slug in slugs or (grain == "variant_group" and row["variant_group"] in groups):
                failures.append(f"{slug}: duplicate ranking identity")
            slugs.add(slug)
            groups.add(row["variant_group"])
            absent, points = 0, []
            for board in BOARD_ORDER:
                values = [row[f"{board}_item{s}_adjusted"] for s in range(1, len(CORE_ITEMS[board]) + 1)]
                observed = sum(v is not None for v in values)
                absent += len(values) - observed
                base = sum(v or 0.0 for v in values) / len(values)
                bonus = row[f"{board}_extension_bonus"]
                expected = min(100, base + bonus) * BOARD_WEIGHTS[board] / 100
                point = float(row[f"{board}_points_full_precision"])
                if not observed or (observed < len(values) and bonus != 0) or abs(expected - point) > 1e-11:
                    failures.append(f"{slug}: invalid {board} evidence/points")
                points.append(point)
            if absent >= 4 or absent != row["missing_core_count"]:
                failures.append(f"{slug}: invalid missing gate")
            error = abs(math.fsum(points) - score)
            max_error = max(max_error, error)
            if error > 1e-11:
                failures.append(f"{slug}: score identity differs")
        return {"ranking_grain": grain, "row_count": len(rows), "unique_slugs": len(slugs),
                "unique_variant_groups": len(groups), "max_final_score_identity_error": max_error,
                "passed": not failures, "failures": failures}
    grouped, exact = audit(full_rankings, "variant_group"), audit(exact_config_full_rankings, "exact_config")
    return {"method_id": METHOD_ID, "candidate_id": CANDIDATE_ID,
            "calibration_population_size": calibration["population_size"],
            "bonus_cap_per_board": calibration["bonus_cap_per_board"], "cap_rule": CAP_RULE,
            "exact_reuses_deduplicated_calibration": True,
            "variant_group": grouped, "exact_config": exact, "passed": grouped["passed"] and exact["passed"]}


def run_aindex_mixed_core_from_payload(payload, *, raw_rows=None, exact_config_models=None,
                                      output_dir=DEFAULT_OUTPUT_DIR, write_outputs=False):
    models = source_models(payload, raw_rows)
    grouped, group_eligibility = prepare(representatives(models))
    calibration = fit_calibration(grouped)
    full = rank_rows(score_models(grouped, calibration))
    exact_sources = source_models({"models": exact_config_models}, raw_rows) if exact_config_models is not None else models
    exact, exact_eligibility = prepare(exact_sources)
    exact_rows = rank_rows(score_models(exact, calibration, ranking_grain="exact_config"))
    validation = validate_rankings(full, exact_rows, calibration)
    validation["core_eligibility"] = {"variant_group": group_eligibility, "exact_config": exact_eligibility}
    if not validation["passed"]:
        raise AssertionError("mixed Core production validation failed")
    result = {"full_rankings": full, "top50": full[:50], "exact_config_full_rankings": exact_rows,
              "exact_config_top50": exact_rows[:50], "calibration": calibration, "validation": validation}
    if write_outputs:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        for key in ("full_rankings", "top50", "exact_config_full_rankings", "exact_config_top50"):
            write_csv(output_dir / OUTPUT_FILENAMES[key], result[key])
        (output_dir / OUTPUT_FILENAMES["validation"]).write_text(
            json.dumps({**validation, "calibration": calibration}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result
