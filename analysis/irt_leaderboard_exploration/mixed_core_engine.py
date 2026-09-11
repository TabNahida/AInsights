"""Independent one/two-Core scoring with fixed shares and observed evidence.

Inputs already contain one fixed representative per model group. This module
does not select configurations, fit missing Core scores, or alter Scheme 18's
extension pool. A configured single item takes the whole domain base; two
configured items retain equal halves even when one observation is missing.
"""
from __future__ import annotations

import math

import numpy as np

from analysis.irt_leaderboard_exploration import dual_core_variants as dual
from analysis.irt_leaderboard_exploration import task_core_variants as task

base, BOARDS = dual.base, dual.BOARDS


def validate_core(core):
    """Check the registry, including globally unique benchmark families."""
    if set(core) != set(BOARDS) or any(
        not isinstance(core[board], (tuple, list)) or len(core[board]) not in (1, 2)
        for board in BOARDS
    ):
        raise ValueError("Every one of the five boards must have one or two Core items")
    keys = [key for board in BOARDS for key in core[board]]
    if any(not isinstance(key, str) or not key for key in keys):
        raise ValueError("Core benchmark names must be nonempty strings")
    if "AA-LCR" in keys or "GDPval-AA" in keys:
        raise ValueError("Use current versioned columns, not duplicate or historical aliases")
    rejected = [key for key in keys if task.forbidden_core(key)]
    if rejected:
        raise ValueError("Forbidden next-round Core family: " + ", ".join(rejected))
    families = [dual.canonical_family(key) for key in keys]
    if len(set(families)) != len(keys):
        raise ValueError("A benchmark family cannot fill multiple Core slots")
    if any(family == "terminal-bench" and key != base.LATEST_TB
           for key, family in zip(keys, families)):
        raise ValueError("Only explicit Terminal v4 is allowed")


def prepare(models, core, maps=None, mode="v4_only"):
    """Apply missing gates without mutating inputs or borrowing observations."""
    validate_core(core)
    if mode != "v4_only":
        raise ValueError("Mixed Core supports only v4_only Terminal evidence")
    eligible, excluded = [], []
    items_total = sum(len(core[board]) for board in BOARDS)
    for source in models:
        model = {**source, "scores": dict(source["scores"])}
        value, origin, raw = base.terminal_score(model["scores"], mode, maps or {})
        model["scores"][base.TB] = value
        model.update(terminal_source=origin, terminal_raw=raw)
        missing, empty_boards = [], []
        for board in BOARDS:
            absent = [key for key in core[board] if base.number(model["scores"].get(key)) is None]
            missing.extend(absent)
            if len(absent) == len(core[board]):
                empty_boards.append(board)
        model.update(missing_core_count=len(missing), missing_core_items=missing,
                     items_total=items_total)
        if empty_boards or len(missing) >= 4:
            reasons = (["board_missing_all"] if empty_boards else [])
            reasons += ["missing_at_least_four"] if len(missing) >= 4 else []
            excluded.append({"slug": model["slug"], "model": model["model"],
                             "missing_core_count": len(missing), "items_total": items_total,
                             "missing_core_items": "; ".join(missing),
                             "empty_boards": "; ".join(empty_boards),
                             "reason": "; ".join(reasons)})
        else:
            eligible.append(model)
    return eligible, excluded


def core_matrix(models, keys):
    """Read exact configured columns, preserving missing observations as NaN."""
    return np.asarray([[base.number(model["scores"].get(key)) for key in keys]
                       for model in models], dtype=float).reshape(len(models), len(keys))


def fixed_share_base(raw):
    values = np.asarray(raw, dtype=float)
    if values.ndim != 2 or values.shape[1] not in (1, 2):
        raise ValueError("Expected an n-by-1 or n-by-2 Core matrix")
    observed = np.isfinite(values)
    if np.any((values[observed] < 0) | (values[observed] > 100)):
        raise ValueError("Core observations must be on the adjusted 0-100 scale")
    # Zero is only a missing item's contribution, never an imputed observation.
    return np.where(observed, values, 0.0).sum(axis=1) / values.shape[1]


def extension_registry(core):
    """Keep Core-family deduplication and the existing v4-only Terminal rule.

    Without this explicit version gate, dropping Terminal from a Core would
    re-enable the old v2.1 entry in the unchanged Scheme 18 extension pool.
    """
    validate_core(core)
    return {board: tuple(key for key in keys
                         if dual.canonical_family(key) != "terminal-bench" or key == base.LATEST_TB)
            for board, keys in dual.extension_registry(core).items()}


def fit_calibration(models, core):
    validate_core(core)
    registry, boards, residual_arrays = extension_registry(core), {}, []
    for board in BOARDS:
        raw = core_matrix(models, core[board])
        complete = np.isfinite(raw).all(axis=1)
        values = base.scheme18.score_matrix(models, registry[board]).reshape(len(models), len(registry[board]))
        residuals, trends = base.scheme18._fit_positive_residuals(
            fixed_share_base(raw)[complete], values[complete])
        residual_arrays.append(residuals)
        boards[board] = {"core": core[board], "extensions": registry[board], "trends": trends,
                         "complete_core_models": int(complete.sum())}
    positives = [value for array in residual_arrays for value in array.flat
                 if np.isfinite(value) and value > 0]
    cap = base.scheme18.derive_cap(residual_arrays) if positives else 0.0
    return {"cap": cap, "boards": boards, "population": len(models),
            "extension_policy": "fit and award extension bonuses only on boards with all configured Core items observed"}


def _validate_weights(weights):
    if (len(weights) != len(BOARDS)
        or any(not math.isfinite(weight) or weight < 0 for weight in weights)
        or not math.isclose(sum(weights), 100)):
        raise ValueError("Five nonnegative finite weights must total 100")


def score_models(models, core, weights, calibration):
    validate_core(core)
    _validate_weights(weights)
    if not models:
        return []
    bases, bonuses = {}, {}
    for board in BOARDS:
        raw = core_matrix(models, core[board])
        bases[board] = fixed_share_base(raw)
        complete = np.isfinite(raw).all(axis=1)
        meta = calibration["boards"][board]
        if list(meta["core"]) != list(core[board]):
            raise ValueError("Calibration Core registry does not match")
        extensions = base.scheme18.score_matrix(models, meta["extensions"])
        residuals = base.scheme18._apply_extension_trends(bases[board], extensions, meta["trends"])
        residuals[~complete] = np.nan
        bonuses[board] = base.scheme18.extension_bonus(residuals, calibration["cap"])
    rows = []
    items_total = sum(len(core[board]) for board in BOARDS)
    for index, model in enumerate(models):
        row = {"slug": model["slug"], "model": model["model"], "variant_group": model["variantGroup"],
               "missing_core_count": model["missing_core_count"],
               "missing_core_items": "; ".join(model["missing_core_items"]), "items_total": items_total,
               "terminal_source": model["terminal_source"], "terminal_raw": model["terminal_raw"],
               "terminal_effective": model["scores"][base.TB]}
        base_points, final_points = [], []
        for board, weight in zip(BOARDS, weights):
            value, bonus = float(bases[board][index]), float(bonuses[board][index])
            score = min(100.0, value + bonus)
            count = len(core[board])
            row.update({board + "_core": value, board + "_core_count": count,
                        board + "_bonus": bonus, board + "_score": score,
                        board + "_weight": weight, board + "_points": score * weight / 100})
            for slot, key in enumerate(core[board], 1):
                observed = base.number(model["scores"].get(key))
                row.update({f"{board}_item{slot}": key, f"{board}_item{slot}_adjusted": observed,
                            f"{board}_item{slot}_base_points": (observed or 0) * weight / (100 * count)})
            base_points.append(value * weight / 100)
            final_points.append(score * weight / 100)
        row.update(core_only_score=math.fsum(base_points), score=math.fsum(final_points))
        rows.append(row)
    rows.sort(key=lambda row: (-row["score"], row["slug"]))
    for rank, row in enumerate(rows, 1):
        row["rank"] = rank
    return rows


def score_variant(models, core, weights, maps=None, mode="v4_only"):
    eligible, excluded = prepare(models, core, maps, mode)
    calibration = fit_calibration(eligible, core)
    rows = score_models(eligible, core, weights, calibration)
    return rows, excluded, calibration, eligible


def validate_rows(rows, core, weights):
    """Recompute evidence shares and eligibility, including unused-slot absence."""
    validate_core(core)
    _validate_weights(weights)
    errors, groups = [], set()
    previous = (-math.inf, "")
    items_total = sum(len(core[board]) for board in BOARDS)
    for rank, row in enumerate(rows, 1):
        order = (-row["score"], row["slug"])
        if row["rank"] != rank or order < previous or not math.isfinite(row["score"]):
            errors.append("rank or score order mismatch")
        previous = order
        if row["variant_group"] in groups:
            errors.append("duplicate variant group")
        groups.add(row["variant_group"])
        missing, points, base_points = [], [], []
        if row["items_total"] != items_total:
            errors.append("configured item total mismatch")
        for board, weight in zip(BOARDS, weights):
            count = len(core[board])
            values = [row[f"{board}_item{slot}_adjusted"] for slot in range(1, count + 1)]
            absent = sum(value is None for value in values)
            if any(value is not None and (base.number(value) is None or not 0 <= value <= 100)
                   for value in values):
                errors.append("invalid Core observation")
            if absent == count:
                errors.append("admitted model missing a whole board")
            if row[board + "_core_count"] != count or row[board + "_weight"] != weight:
                errors.append("board configuration mismatch")
            if count == 1 and any(f"{board}_item2{suffix}" in row
                                  for suffix in ("", "_adjusted", "_base_points")):
                errors.append("unconfigured Core slot emitted")
            for slot, (key, value) in enumerate(zip(core[board], values), 1):
                if value is None:
                    missing.append(key)
                if row[f"{board}_item{slot}"] != key:
                    errors.append("Core item mismatch")
                expected = (value or 0.0) * weight / (100 * count)
                if not math.isclose(row[f"{board}_item{slot}_base_points"], expected, abs_tol=1e-10):
                    errors.append("item fixed-share identity failed")
            expected_base = sum(value or 0.0 for value in values) / count
            if not math.isclose(row[board + "_core"], expected_base, abs_tol=1e-10):
                errors.append("fixed-share identity failed")
            bonus = row[board + "_bonus"]
            if not math.isfinite(bonus) or bonus < 0:
                errors.append("invalid extension bonus")
            if absent and bonus != 0:
                errors.append("incomplete board received extension bonus")
            expected_score = min(100.0, expected_base + bonus)
            if not math.isclose(row[board + "_score"], expected_score, abs_tol=1e-10):
                errors.append("board score identity failed")
            point = expected_score * weight / 100
            if not math.isclose(row[board + "_points"], point, abs_tol=1e-10):
                errors.append("weighted board points mismatch")
            points.append(point)
            base_points.append(expected_base * weight / 100)
        if (len(missing) >= 4 or len(missing) != row["missing_core_count"]
            or row["missing_core_items"] != "; ".join(missing)):
            errors.append("missing count or eligibility mismatch")
        if (not math.isclose(row["score"], math.fsum(points), abs_tol=1e-10)
            or not math.isclose(row["core_only_score"], math.fsum(base_points), abs_tol=1e-10)):
            errors.append("final score identity failed")
    return {"passed": not errors, "errors": sorted(set(errors)), "row_count": len(rows)}
