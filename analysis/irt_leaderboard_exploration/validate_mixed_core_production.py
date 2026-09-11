"""Independently reconstruct mixed Core 07 eligibility, scores, and site profiles.

No production scoring or experimental search module is imported. The reviewed
registry and weights are repeated here deliberately; the existing independent
OLS arithmetic is reused, with a separately implemented mixed Core mean.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import sys

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ArtificialAnalysis.scrape_artificial_analysis import SCORE_SPECS
from analysis.irt_leaderboard_exploration import validate_scheme18_production as independent
from analysis.irt_leaderboard_exploration.evidence_only_ranking_analysis import sanitize_models

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "docs/data/models.json"
DEFAULT_RAW = ROOT / "ArtificialAnalysis/artificialanalysis_raw_scores_wide.csv"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
METHOD_ID, CANDIDATE_ID = "aindex_mixed_core", "mixed_core_mc07"
CORE = {
    "coding": ("Terminal-Bench v4.0", "SciCode"),
    "agentic-tool-work": ("AutomationBench-AA", "τ³-Banking"),
    "hard-reasoning": ("CritPt",),
    "knowledge-science": ("AA-Omniscience Accuracy", "GDP.pdf"),
    "instruction-context": ("AA-LCR v1.1",),
}
WEIGHTS = dict(zip(CORE, (12, 9, 22, 37, 20), strict=True))
SUMMARY_FILENAME = "aindex_mixed_core_validation_summary.json"
FILES = {"full_rankings": "full_rankings_aindex_mixed_core.csv",
         "top50": "top50_aindex_mixed_core.csv",
         "exact_config_full_rankings": "full_rankings_exact_config_aindex_mixed_core.csv",
         "exact_config_top50": "top50_exact_config_aindex_mixed_core.csv"}


def family(key):
    if key.startswith("Terminal-Bench") or key.startswith("benchmark:terminal-bench"):
        return "terminal-bench"
    if key.startswith("AA-LCR"):
        return "aa-lcr"
    if key.startswith("AA-Omniscience"):
        return "omniscience"
    for registry in (independent.CORE_POLICIES, independent.EXTENSION_POLICIES):
        for policies in registry.values():
            for policy in policies:
                if policy.score_key == key:
                    return policy.canonical_family
    return key


CORE_FAMILIES = {family(key) for keys in CORE.values() for key in keys}
EXTENSIONS = {board: tuple(p.score_key for p in policies
                          if family(p.score_key) not in CORE_FAMILIES
                          and family(p.score_key) != "terminal-bench")
              for board, policies in independent.EXTENSION_POLICIES.items()}


def _read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_models(payload, raw_rows):
    models, _ = sanitize_models(payload, exact_config_only=True)
    raw = {row["slug"]: row for row in raw_rows or []}
    for model in models:
        if model["slug"] in raw:
            for spec in SCORE_SPECS:
                model["scores"][spec.column] = independent.finite(raw[model["slug"]].get(spec.column))
    return models


def _missing(model):
    missing = {board: [key for key in keys if independent.score_value(model, key) is None]
               for board, keys in CORE.items()}
    count = sum(map(len, missing.values()))
    return missing, count, count < 4 and all(len(missing[b]) < len(CORE[b]) for b in CORE)


def _matrix(models, keys):
    result = independent.matrix(models, keys).reshape(len(models), len(keys))
    values = result[np.isfinite(result)]
    if np.any((values < 0) | (values > 100)):
        raise AssertionError("source observation outside 0--100")
    return result


def _base(raw):
    # Every configured item retains exactly 1/n of its board base.
    return np.array([math.fsum(float(v) for v in row if np.isfinite(v)) / len(row)
                     for row in raw], dtype=float)


def _calibrate(models):
    trends, complete_counts, positives = {}, {}, []
    for board in CORE:
        raw = _matrix(models, CORE[board])
        complete = np.isfinite(raw).all(axis=1)
        complete_counts[board] = int(complete.sum())
        ext = _matrix(models, EXTENSIONS[board])
        residuals, trends[board] = independent.fit_trends(_base(raw)[complete], ext[complete])
        positives.extend(float(v) for v in residuals.flat if np.isfinite(v) and v > 0)
    mean = float(np.mean(positives)) if positives else 0.0
    sd = float(np.std(positives, ddof=0)) if positives else 0.0
    return {"trends": trends, "complete_counts": complete_counts, "count": len(positives),
            "mean": mean, "sd": sd, "cap": mean + math.sqrt(2) * sd}


def _score(models, calibration):
    boards = {}
    for board in CORE:
        raw = _matrix(models, CORE[board])
        base = _base(raw)
        complete = np.isfinite(raw).all(axis=1)
        ext = _matrix(models, EXTENSIONS[board])
        residuals = independent.apply_trends(base, ext, calibration["trends"][board])
        residuals[~complete] = np.nan
        bonus = independent.bonuses(residuals, calibration["cap"])
        score = np.minimum(100, base + bonus)
        boards[board] = (raw, base, bonus, score, np.isfinite(ext).sum(axis=1))
    rows = []
    for index, model in enumerate(models):
        missing, count, eligible = _missing(model)
        if not eligible:
            raise AssertionError("independent scoring received ineligible model")
        row = {"slug": model["slug"], "model": model.get("model", ""), "variant_group": model["variantGroup"],
               "missing_core_count": count, "missing_core_items": "; ".join(k for b in CORE for k in missing[b]),
               "core_tests_total": 8 - count, "items_total": 8}
        points = []
        for board, (raw, base, bonus, scores, ext_count) in boards.items():
            point = float(scores[index]) * WEIGHTS[board] / 100
            points.append(point)
            row.update({f"{board}_core_score": float(base[index]), f"{board}_extension_bonus": float(bonus[index]),
                        f"{board}_score_full_precision": float(scores[index]), f"{board}_points_full_precision": point,
                        f"{board}_core_tests": int(np.isfinite(raw[index]).sum()),
                        f"{board}_extension_tests": int(ext_count[index]), f"{board}_weight": WEIGHTS[board]})
            for slot, key in enumerate(CORE[board], 1):
                value = independent.score_value(model, key)
                row[f"{board}_item{slot}"] = key
                row[f"{board}_item{slot}_adjusted"] = value
                row[f"{board}_item{slot}_base_points"] = (value or 0) * WEIGHTS[board] / (100 * len(CORE[board]))
        row["score_full_precision"] = math.fsum(points)
        rows.append(row)
    rows.sort(key=lambda r: (-r["score_full_precision"], r["slug"], r["model"]))
    for rank, row in enumerate(rows, 1):
        row["rank"] = rank
    return rows


def _compare_number(actual, expected, label, failures, tolerance=1e-10):
    value = independent.finite(actual)
    if expected is None:
        if value is not None:
            failures.append(label + ": missing observation became a number")
    elif value is None or abs(value - expected) > tolerance:
        failures.append(label + ": numeric value differs")


def _audit_rows(actual, expected, label, failures):
    if [r.get("slug") for r in actual] != [r["slug"] for r in expected]:
        failures.append(label + ": complete eligible population or rank order differs")
    by_slug = {r.get("slug"): r for r in actual}
    for row in expected:
        saved = by_slug.get(row["slug"])
        if saved is None:
            continue
        for field, value in row.items():
            if isinstance(value, str):
                if saved.get(field) != value:
                    failures.append(f"{label}/{row['slug']}/{field}: text differs")
            else:
                _compare_number(saved.get(field), value, f"{label}/{row['slug']}/{field}", failures)
        if saved.get("method") != METHOD_ID or saved.get("candidate_id") != CANDIDATE_ID:
            failures.append(label + ": method identity differs")


def _audit_profiles(payload, expected, profile_key, failures):
    actual_models = {m["slug"]: m for m in payload.get("models", [])}
    actual_slugs = {m["slug"] for m in actual_models.values() if m.get(profile_key)}
    if actual_slugs != {r["slug"] for r in expected}:
        failures.append(profile_key + ": profile population differs from eligibility")
    for row in expected:
        profile = actual_models[row["slug"]].get(profile_key) or {}
        label = f"{profile_key}/{row['slug']}"
        if profile.get("method") != METHOD_ID or profile.get("candidateId") != CANDIDATE_ID:
            failures.append(label + ": method identity differs")
        for field, expected_value in (("finalScore", row["score_full_precision"]), ("publicationRank", row["rank"]),
                                      ("scoreFullPrecision", row["score_full_precision"]),
                                      ("displayScore", round(row["score_full_precision"], 4)),
                                      ("missingCoreCount", row["missing_core_count"])):
            _compare_number(profile.get(field), expected_value, label + "/" + field, failures)
        if profile.get("boardWeights") != WEIGHTS:
            failures.append(label + ": board weight metadata differs")
        if profile.get("coreComplete") is not (row["missing_core_count"] == 0):
            failures.append(label + ": Core complete flag differs")
        if "missingCoreItems" in profile:
            expected_missing = row["missing_core_items"].split("; ") if row["missing_core_items"] else []
            if profile["missingCoreItems"] != expected_missing:
                failures.append(label + ": missing Core item list differs")
        for board, keys in CORE.items():
            meta = (profile.get("boards") or {}).get(board) or {}
            for public, internal in (("coreScore", "core_score"), ("extensionBonus", "extension_bonus"),
                                     ("score", "score_full_precision"), ("points", "points_full_precision"),
                                     ("weight", "weight"), ("coreTests", "core_tests"), ("extensionTests", "extension_tests")):
                _compare_number(meta.get(public), row[f"{board}_{internal}"], label + f"/{board}/{public}", failures)
            if meta.get("coreComplete") is not (row[f"{board}_core_tests"] == len(keys)):
                failures.append(label + f"/{board}: Core complete flag differs")
            slots = meta.get("coreEvidence") or meta.get("coreItems") or []
            if [s.get("key") for s in slots] != list(keys):
                failures.append(label + f"/{board}: configured item slots differ")
                continue
            for slot, item in enumerate(slots, 1):
                value = row[f"{board}_item{slot}_adjusted"]
                _compare_number(item.get("adjustedScore"), value, label + f"/{board}/item{slot}", failures)
                _compare_number(item.get("basePoints"), row[f"{board}_item{slot}_base_points"], label + f"/{board}/item{slot}/points", failures)
                if item.get("observed") is not (value is not None):
                    failures.append(label + f"/{board}/item{slot}: observed flag differs")


def _audit_leaderboard(payload, full, exact, calibration, failures):
    leaderboard = payload.get("leaderboard") or {}
    if leaderboard.get("defaultMethod") != METHOD_ID or leaderboard.get("candidateId") != CANDIDATE_ID:
        failures.append("website leaderboard method differs")
    if leaderboard.get("boardWeights") != WEIGHTS or leaderboard.get("boardOrder") != list(CORE):
        failures.append("website leaderboard weights or board order differ")
    if leaderboard.get("calibration") != calibration:
        failures.append("website serialized calibration differs from audited artifact")
    _compare_number(leaderboard.get("bonusCap"), calibration.get("bonus_cap_per_board"),
                    "leaderboard/bonusCap", failures)
    for rows_key, identity, count_key, expected in (("rows", "selectedSlug", "populationSize", full),
                                                   ("exactRows", "slug", "exactPopulationSize", exact)):
        actual = leaderboard.get(rows_key) or []
        _compare_number(leaderboard.get(count_key), len(expected), "leaderboard/" + count_key, failures)
        if [row.get(identity) for row in actual] != [row["slug"] for row in expected]:
            failures.append("leaderboard/" + rows_key + ": population or order differs")
            continue
        for saved, row in zip(actual, expected, strict=True):
            label = f"leaderboard/{rows_key}/{row['slug']}"
            if saved.get("variantGroup") != row["variant_group"]:
                failures.append(label + ": variant group differs")
            for public, value in (("publicationRank", row["rank"]),
                                  ("scoreFullPrecision", row["score_full_precision"]),
                                  ("displayScore", round(row["score_full_precision"], 4))):
                _compare_number(saved.get(public), value, label + "/" + public, failures)
    for field, expected in (("coreItems", CORE), ("extensionItems", EXTENSIONS)):
        if leaderboard.get(field) != {board: list(keys) for board, keys in expected.items()}:
            failures.append("leaderboard/" + field + ": displayed registry differs")


def validate_production_outputs(*, input_path=DEFAULT_INPUT, output_dir=DEFAULT_OUTPUT_DIR,
                                raw_path=DEFAULT_RAW, write_summary=True, check_profiles=True):
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    output_dir = Path(output_dir)
    summary_path = output_dir / SUMMARY_FILENAME
    serialized = json.loads(summary_path.read_text(encoding="utf-8"))
    calibration = serialized.get("calibration") or {}
    failures = []
    models = _read_models(payload, _read_csv(raw_path) if raw_path is not None else None)
    selected = {}
    for model in sorted(models, key=lambda m: (-(independent.finite(m.get("variantPriority")) or 0), m["slug"])):
        selected.setdefault(model["variantGroup"], model)
    grouped = [m for m in selected.values() if _missing(m)[2]]
    exact = [m for m in models if _missing(m)[2]]
    if len({m["slug"] for m in models}) != len(models):
        failures.append("source slugs are duplicated")
    if calibration.get("population_slugs") != [m["slug"] for m in grouped]:
        failures.append("calibration population differs from fixed representative eligibility")
    if (calibration.get("method_id") != METHOD_ID or calibration.get("candidate_id") != CANDIDATE_ID
        or calibration.get("board_weights") != WEIGHTS or calibration.get("core_fit") != "fixed_share_arithmetic"):
        failures.append("calibration scheme identity or fixed weights differ")
    recomputed = _calibrate(grouped)
    for field, key in (("bonus_cap_per_board", "cap"), ("pooled_positive_residual_count", "count"),
                       ("pooled_positive_residual_mean", "mean"), ("pooled_positive_residual_population_sd", "sd")):
        _compare_number(calibration.get(field), recomputed[key], "calibration/" + field, failures)
    for board in CORE:
        meta = (calibration.get("boards") or {}).get(board) or {}
        for field, expected in (("core_items", CORE[board]), ("extension_items", EXTENSIONS[board])):
            if [p.get("score_key") for p in meta.get(field, [])] != list(expected):
                failures.append(f"calibration/{board}/{field}: registry differs")
        _compare_number(meta.get("complete_core_models"), recomputed["complete_counts"][board], f"calibration/{board}/complete", failures)
        actual_trends = meta.get("extension_items") or []
        if len(actual_trends) == len(recomputed["trends"][board]):
            for index, (actual, expected) in enumerate(zip(actual_trends, recomputed["trends"][board], strict=True)):
                if actual.get("enabled") is not expected["enabled"]:
                    failures.append(f"calibration/{board}/{index}: trend enable flag differs")
                for field in ("observed_count", "slope", "intercept"):
                    _compare_number(actual.get(field), expected[field], f"calibration/{board}/{index}/{field}", failures)
    full, exact_rows = _score(grouped, recomputed), _score(exact, recomputed)
    for full_key, top_key, expected in (("full_rankings", "top50", full),
                                         ("exact_config_full_rankings", "exact_config_top50", exact_rows)):
        rows = _read_csv(output_dir / FILES[full_key])
        _audit_rows(rows, expected, full_key, failures)
        if _read_csv(output_dir / FILES[top_key]) != rows[:50]:
            failures.append(top_key + ": differs from full ranking prefix")
    if check_profiles:
        _audit_profiles(payload, full, "rankingProfile", failures)
        _audit_profiles(payload, exact_rows, "exactRankingProfile", failures)
        _audit_leaderboard(payload, full, exact_rows, calibration, failures)
    result = {"method_id": METHOD_ID, "candidate_id": CANDIDATE_ID,
              "independent_of_production_scoring_module": True,
              "variant_group_count": len(full), "exact_config_count": len(exact_rows),
              "cap": recomputed["cap"], "profiles_checked": check_profiles,
              "passed": not failures, "failures": failures}
    if write_summary:
        serialized["independent_validation"] = result
        summary_path.write_text(json.dumps(serialized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--raw-csv", type=Path, default=DEFAULT_RAW)
    parser.add_argument("--no-write-summary", action="store_true")
    args = parser.parse_args(argv)
    result = validate_production_outputs(input_path=args.input, output_dir=args.output_dir,
                                        raw_path=args.raw_csv, write_summary=not args.no_write_summary)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
