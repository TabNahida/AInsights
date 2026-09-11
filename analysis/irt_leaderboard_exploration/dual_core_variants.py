"""Ten two-Core experiments with fixed half shares and explicit missing gates."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
import sys

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from analysis.irt_leaderboard_exploration import core_variants as base
from analysis.irt_leaderboard_exploration import preference_core_variants as preferences

BOARDS = base.scheme18.BOARD_ORDER
OUTPUT = Path(__file__).resolve().parent / "outputs" / "dual_core_variants"
DEFAULT_CORE = {
    "coding": (base.TB, "SciCode"),
    "agentic-tool-work": ("AutomationBench-AA", "τ³-Banking"),
    "hard-reasoning": ("CritPt", "Humanity's Last Exam"),
    "knowledge-science": ("AA-Omniscience Accuracy", "GPQA Diamond"),
    "instruction-context": ("AA-LCR v1.1", "GDP.pdf"),
}


def variant(label, purpose, tradeoff, **changes):
    return {"label": label, "purpose": purpose, "tradeoff": tradeoff,
            "core": {**DEFAULT_CORE, **changes}, "weights": [20]*5, "fallback": "calibrated"}


VARIANTS = {
    "dc01": variant("01 最新任务基线", "采用当前任务型、科学推理与知识测试，作为其他九套的共同参照。",
                    "两项上下文均偏文档理解；GDP.pdf 覆盖较新，较旧模型可能单缺该项。"),
    "dc02": variant("02 Banking＋知识工作", "把 Agent 的 Automation 换成 Briefcase，比较银行操作与长流程知识工作交付。",
                    "Briefcase 为 Elo 换算分，非任务通过率；缺该项保留半份惩罚，例如 Flash-Next。",
                    **{"agentic-tool-work": ("τ³-Banking", "AA-Briefcase")}),
    "dc03": variant("03 自动化＋知识工作", "把 Agent 的 Banking 换成 Briefcase，强调 SaaS 自动化及工作成果交付。",
                    "两项都是较新测试，老模型常同时缺失而被领域门槛剔除；Briefcase 是 Elo 换算分。",
                    **{"agentic-tool-work": ("AutomationBench-AA", "AA-Briefcase")}),
    "dc04": variant("04 自动化＋职业任务", "把 Banking 换成 GDPval v2，观察职业任务能力对 Agent 板块的影响。",
                    "GDPval v2 是 Elo 换算分，任务由 OpenAI 控制；这是本轮显式实验，不代表采用原独立基准准入政策。",
                    **{"agentic-tool-work": ("AutomationBench-AA", "GDPval-AA v2")}),
    "dc05": variant("05 指令遵循对照", "上下文用 LCR＋IFBench，将 PDF 问答替换为指令遵循测试。",
                    "不少最新模型缺 IFBench，其指令／上下文基础分最多只获得 LCR 的半份。",
                    **{"instruction-context": ("AA-LCR v1.1", "IFBench")}),
    "dc06": variant("06 算法编程对照", "用 LiveCodeBench 替代 SciCode，比较算法代码能力与终端任务能力。",
                    "当前新旗舰多缺 LiveCodeBench，编程基础分因此只获得 Terminal 的半份；不会用网站拟合补值。",
                    **{"coding": (base.TB, "LiveCodeBench")}),
    "dc07": variant("07 算法＋指令双替换", "同时采用 LiveCodeBench 和 IFBench，检验两项历史高覆盖测试共同进入 Core 的影响。",
                    "不少新模型会累计缺两项，仍可入榜但两个领域各损失半份；这是缺测规则的压力对照。",
                    **{"coding": (base.TB, "LiveCodeBench"), "instruction-context": ("AA-LCR v1.1", "IFBench")}),
    "dc08": variant("08 数学竞赛对照", "推理用 CritPt＋AIME 2025，将广域 HLE 替换为数学竞赛。",
                    "AIME 2025 的旧模型覆盖较多，新模型缺测较多；推理板块单缺时只计 CritPt 的半份。",
                    **{"hard-reasoning": ("CritPt", "AIME 2025")}),
    "dc09": variant("09 多模态知识对照", "知识用 Omniscience Accuracy＋MMMU-Pro，加入图像与跨学科理解。",
                    "不同模型的图像能力与测评覆盖不同，缺 MMMU-Pro 不自动视为低能力，但会产生明确的半份分数损失。",
                    **{"knowledge-science": ("AA-Omniscience Accuracy", "MMMU-Pro")}),
    "dc10": variant("10 电信＋银行覆盖对照", "Agent 用 Telecom＋Banking，观察较高历史覆盖能保留多少模型。",
                    "新旗舰通常缺 Telecom，旧模型则可能缺新版文档或科学编程结果；较广入榜不代表证据同样完整。",
                    **{"agentic-tool-work": ("τ²-Bench Telecom", "τ³-Banking")}),
}


def validate_core(core):
    if set(core) != set(BOARDS) or any(len(core[b]) != 2 for b in BOARDS):
        raise ValueError("Every one of the five boards must have exactly two Core items")
    keys = [k for b in BOARDS for k in core[b]]
    if len(set(keys)) != 10:
        raise ValueError("The ten Core slots must use distinct benchmark items")
    if "AA-LCR" in keys or "GDPval-AA" in keys:
        raise ValueError("Use current versioned columns, not duplicate or historical aliases")
    families = [canonical_family(k) for k in keys]
    if len(set(families)) != 10:
        raise ValueError("A benchmark family cannot fill multiple Core slots")


def canonical_family(key):
    if key in (base.TB, base.LATEST_TB, *base.OLD_TB) or key.startswith("benchmark:terminal-bench"):
        return "terminal-bench"
    aliases = {
        "LiveCodeBench": "livecodebench", "benchmark:livecodebench": "livecodebench",
        "AA-LCR": "aa-lcr", "AA-LCR v1.1": "aa-lcr",
        "AA-Omniscience Accuracy": "omniscience", "AA-Omniscience Non-Hallucination Rate": "omniscience",
        "GDPval-AA": "gdpval", "GDPval-AA v2": "gdpval",
    }
    if key in aliases:
        return aliases[key]
    for policies in base.scheme18.CORE_POLICIES.values():
        for policy in policies:
            if policy.score_key == key:
                return policy.canonical_family
    for policies in base.scheme18.EXTENSION_POLICIES.values():
        for policy in policies:
            if policy.score_key == key:
                return policy.canonical_family
    return key


def prepare(models, core, maps, mode="calibrated"):
    validate_core(core)
    if mode == "v4_only" and any(canonical_family(key) == "terminal-bench" and key != base.LATEST_TB
                                 for pair in core.values() for key in pair):
        raise ValueError("v4-only Core must use the explicit v4 benchmark column")
    eligible, excluded = [], []
    for source in models:
        model = {**source, "scores": dict(source["scores"])}
        value, origin, raw = base.terminal_score(model["scores"], mode, maps)
        model["scores"][base.TB] = value
        model.update(terminal_source=origin, terminal_raw=raw)
        missing, empty_boards = [], []
        for board in BOARDS:
            absent = [key for key in core[board] if base.number(model["scores"].get(key)) is None]
            missing.extend(absent)
            if len(absent) == 2:
                empty_boards.append(board)
        model["missing_core_count"] = len(missing)
        model["missing_core_items"] = missing
        if empty_boards or len(missing) >= 4:
            excluded.append({"slug": model["slug"], "model": model["model"],
                             "missing_core_count": len(missing), "missing_core_items": "; ".join(missing),
                             "empty_boards": "; ".join(empty_boards),
                             "reason": "; ".join(((["board_missing_both"] if empty_boards else []) + (["missing_at_least_four"] if len(missing) >= 4 else [])))})
        else:
            eligible.append(model)
    return eligible, excluded


def pair_base(raw):
    values = np.asarray(raw, dtype=float)
    if values.ndim != 2 or values.shape[1] != 2:
        raise ValueError("Expected an n-by-2 Core matrix")
    observed = np.isfinite(values)
    if np.any((values[observed] < 0) | (values[observed] > 100)):
        raise ValueError("Core observations must be on the adjusted 0-100 scale")
    # Missing remains NaN in evidence. This zero is only its fixed half-share
    # contribution; do not renormalize the observed item or fabricate a result.
    return np.where(observed, values, 0.0).sum(axis=1) / 2


def extension_registry(core):
    core_families = {canonical_family(key) for keys in core.values() for key in keys}
    return {board: tuple(key for key in keys if canonical_family(key) not in core_families)
            for board, keys in base.scheme18.EXTENSION_ITEMS.items()}


def fit_calibration(models, core):
    validate_core(core)
    registry, boards, residual_arrays = extension_registry(core), {}, []
    for board in BOARDS:
        raw = base.scheme18.score_matrix(models, core[board])
        if len(models) == 0:
            raw = np.empty((0, 2))
        complete = np.isfinite(raw).all(axis=1)
        values = base.scheme18.score_matrix(models, registry[board])
        if len(models) == 0:
            values = np.empty((0, len(registry[board])))
        # Fit only observed complete pairs, never missing contributions.
        residuals, trends = base.scheme18._fit_positive_residuals(pair_base(raw)[complete], values[complete])
        residual_arrays.append(residuals)
        boards[board] = {"core": core[board], "extensions": registry[board], "trends": trends,
                         "complete_core_models": int(complete.sum())}
    positives = [v for array in residual_arrays for v in array.flat if np.isfinite(v) and v > 0]
    cap = base.scheme18.derive_cap(residual_arrays) if positives else 0.0
    return {"cap": cap, "boards": boards, "population": len(models),
            "extension_policy": "fit and award extension bonuses only on boards with both Core items observed"}


def score_models(models, core, weights, calibration):
    validate_core(core)
    if len(weights) != 5 or any(not math.isfinite(w) or w < 0 for w in weights) or not math.isclose(sum(weights), 100):
        raise ValueError("Five nonnegative finite weights must total 100")
    if not models:
        return []
    bases, bonuses, matrices = {}, {}, {}
    for board in BOARDS:
        raw = base.scheme18.score_matrix(models, core[board])
        matrices[board] = raw
        bases[board] = pair_base(raw)
        complete = np.isfinite(raw).all(axis=1)
        meta = calibration["boards"][board]
        if list(meta["core"]) != list(core[board]):
            raise ValueError("Calibration Core registry does not match")
        extensions = base.scheme18.score_matrix(models, meta["extensions"])
        residuals = base.scheme18._apply_extension_trends(bases[board], extensions, meta["trends"])
        residuals[~complete] = np.nan
        bonuses[board] = base.scheme18.extension_bonus(residuals, calibration["cap"])
    rows = []
    for i, model in enumerate(models):
        row = {"slug": model["slug"], "model": model["model"], "variant_group": model["variantGroup"],
               "missing_core_count": model["missing_core_count"], "missing_core_items": "; ".join(model["missing_core_items"]),
               "terminal_source": model["terminal_source"], "terminal_raw": model["terminal_raw"],
               "terminal_effective": model["scores"][base.TB]}
        base_points, final_points = [], []
        for j, board in enumerate(BOARDS):
            b, bonus = float(bases[board][i]), float(bonuses[board][i])
            score = min(100.0, b + bonus)
            row.update({board + "_core": b, board + "_bonus": bonus,
                        board + "_score": score, board + "_weight": weights[j],
                        board + "_points": score * weights[j] / 100})
            for slot, key in enumerate(core[board], 1):
                observed = base.number(model["scores"].get(key))
                row.update({f"{board}_item{slot}": key, f"{board}_item{slot}_adjusted": observed,
                            f"{board}_item{slot}_base_points": (observed or 0) * weights[j] / 200})
            base_points.append(b * weights[j] / 100)
            final_points.append(score * weights[j] / 100)
        row.update(core_only_score=math.fsum(base_points), score=math.fsum(final_points))
        rows.append(row)
    rows.sort(key=lambda row: (-row["score"], row["slug"]))
    for rank, row in enumerate(rows, 1):
        row["rank"] = rank
    return rows


def score_variant(models, core, weights, maps, mode="calibrated"):
    eligible, excluded = prepare(models, core, maps, mode)
    calibration = fit_calibration(eligible, core)
    rows = score_models(eligible, core, weights, calibration)
    return rows, excluded, calibration, eligible


def load_inputs(input_json, raw_csv, *, terminal_mode="calibrated"):
    payload = json.loads(input_json.read_text(encoding="utf-8"))
    with raw_csv.open(encoding="utf-8-sig", newline="") as handle:
        models = base.load_models(payload, list(csv.DictReader(handle)))
    selected = base.representatives(models)
    return payload, models, selected, ({} if terminal_mode == "v4_only" else base.fit_terminal_maps(selected))


def validate_rows(rows, core, weights):
    errors = []
    groups, previous = set(), math.inf
    for rank, row in enumerate(rows, 1):
        if row["rank"] != rank or row["score"] > previous + 1e-12:
            errors.append("rank or score order mismatch")
        previous = row["score"]
        if row["variant_group"] in groups:
            errors.append("duplicate variant group")
        groups.add(row["variant_group"])
        missing = 0
        points, base_points = [], []
        for board, weight in zip(BOARDS, weights):
            values = [row[f"{board}_item{slot}_adjusted"] for slot in (1, 2)]
            count = sum(value is None for value in values)
            missing += count
            if count == 2:
                errors.append("admitted model missing a whole board")
            expected_base = sum(value or 0.0 for value in values) / 2
            if abs(row[board + "_core"] - expected_base) > 1e-10:
                errors.append("half-share identity failed")
            if count and row[board + "_bonus"] != 0:
                errors.append("incomplete board received extension bonus")
            expected_score = min(100.0, expected_base + row[board + "_bonus"])
            if abs(row[board + "_score"] - expected_score) > 1e-10:
                errors.append("board score identity failed")
            points.append(expected_score * weight / 100)
            base_points.append(expected_base * weight / 100)
        if missing >= 4 or missing != row["missing_core_count"]:
            errors.append("missing count or eligibility mismatch")
        if abs(row["score"]-math.fsum(points)) > 1e-10 or abs(row["core_only_score"]-math.fsum(base_points)) > 1e-10:
            errors.append("final score identity failed")
    return {"passed": not errors, "errors": sorted(set(errors)), "row_count": len(rows)}


def require_passing_preferences(results):
    """Do not publish a filtered proposal with a failed full/common audit."""
    failures = [f"{key}:{scope}" for key, result in results.items()
                for scope in ("preference_audit", "common_preference_audit")
                if not result.get(scope, {}).get("passed")]
    if failures:
        raise ValueError("Filtered candidates failed required preferences: " + ", ".join(failures))


def run(input_json, raw_csv, output, *, write_markdown=True, variants=None,
        selection_mode="structural_comparison", search_metadata=None,
        preference_targets=None, preference_pairs=None, preference_labels=None,
        excluded_variant_groups=()):
    variants = VARIANTS if variants is None else variants
    if not variants:
        raise ValueError("At least one variant is required")
    filtered = selection_mode == "preference_filtered"
    modes = {config.get("fallback", "calibrated") for config in variants.values()}
    if len(modes) != 1:
        raise ValueError("A comparison must use one Terminal evidence policy")
    terminal_mode = next(iter(modes))
    audit_kwargs = {}
    if preference_targets is not None:
        audit_kwargs["targets"] = preference_targets
    if preference_pairs is not None:
        audit_kwargs["pairs"] = preference_pairs
    if preference_labels is not None:
        audit_kwargs["labels"] = preference_labels
    payload, models, selected, maps = load_inputs(input_json, raw_csv, terminal_mode=terminal_mode)
    representative_count = len(selected)
    user_exclusions = [{"slug": model["slug"], "model": model["model"],
                        "variant_group": model["variantGroup"], "reason": "user_excluded_legacy_model"}
                       for model in selected if model["variantGroup"] in excluded_variant_groups]
    selected = [model for model in selected if model["variantGroup"] not in excluded_variant_groups]
    output.mkdir(parents=True, exist_ok=True)
    coverage_models = [{**m, "scores": dict(m["scores"])} for m in models]
    for m in coverage_models:
        m["scores"][base.TB] = base.terminal_score(m["scores"], terminal_mode, maps)[0]
    selected_slugs = {m["slug"] for m in selected}
    coverage = base.coverage_inventory(coverage_models)
    for record in coverage:
        record["fixed_representatives"] = sum(m["slug"] in selected_slugs and base.number(m["scores"].get(record["benchmark"])) is not None for m in coverage_models)
        if record["benchmark"] == base.TB:
            record["note"] = ("仅 v4 实测的兼容槽位，无旧版回退，不是额外测试" if terminal_mode == "v4_only"
                              else "合成版本槽位：优先 v4；同配置旧版先尺度换算再折扣，不是独立的直接观测测试")
    results, prepared, validation = {}, {}, {}
    for key, config in variants.items():
        rows, excluded, calibration, eligible = score_variant(selected, config["core"], config["weights"], maps, terminal_mode)
        prepared[key] = eligible
        results[key] = {"rows": rows, "excluded": excluded, "calibration": calibration,
                        "preference_audit": preferences.constraint_audit(rows, **audit_kwargs),
                        "missing_distribution": dict(Counter(r["missing_core_count"] for r in rows))}
        validation[key] = validate_rows(rows, config["core"], config["weights"])
        if not validation[key]["passed"]:
            raise AssertionError(validation[key])
        if filtered:
            results[key]["sensitivity"] = preferences.weight_sensitivity(rows, config["weights"], **audit_kwargs)
    common = set.intersection(*({m["slug"] for m in ms} for ms in prepared.values()))
    for key, ms in prepared.items():
        config = variants[key]
        eligible = [m for m in ms if m["slug"] in common]
        calibration = fit_calibration(eligible, config["core"])
        rows = score_models(eligible, config["core"], config["weights"], calibration)
        results[key].update(common_rows=rows, common_calibration=calibration,
                            common_preference_audit=preferences.constraint_audit(rows, **audit_kwargs))
        validation[key]["common"] = validate_rows(rows, config["core"], config["weights"])
        if not validation[key]["common"]["passed"]:
            raise AssertionError(validation[key]["common"])
    if filtered:
        require_passing_preferences(results)
    # All eligibility, numeric and requested preference gates run before any
    # ranking or report is written, so failing proposals cannot be published.
    base.scheme18.write_csv(output / "coverage.csv", coverage)
    # Also clear a previous run's explicit exclusion list after it is revoked.
    base.scheme18.write_csv(output / "user_exclusions.csv", user_exclusions)
    for key, result in results.items():
        base.scheme18.write_csv(output / f"rankings_{key}.csv", result["rows"])
        base.scheme18.write_csv(output / f"top30_{key}.csv", result["rows"][:30])
        base.scheme18.write_csv(output / f"excluded_{key}.csv", result["excluded"])
        base.scheme18.write_csv(output / f"common_{key}.csv", result["common_rows"])
    audit_rows = [{"variant": key, "population": scope, **check} for key, result in results.items()
                  for scope, audit in (("full", result["preference_audit"]), ("common", result["common_preference_audit"]))
                  for check in audit["checks"]]
    base.scheme18.write_csv(output / "preference_audit.csv", audit_rows)
    combined = [{"variant": key, **row} for key, result in results.items() for row in result["rows"][:30]]
    base.scheme18.write_csv(output / "top30_all.csv", combined)
    metadata = {
        "source_generated_at": payload.get("generatedAt"), "experiment_date": "2026-09-11",
        "source_hashes": {str(p.relative_to(base.ROOT) if p.is_relative_to(base.ROOT) else p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (input_json, raw_csv)},
        "input_model_count": len(models), "representative_count": representative_count,
        "comparison_representative_count": len(selected), "common_population": len(common),
        "terminal_mode": terminal_mode, "user_exclusions": user_exclusions,
        "excluded_variant_groups": list(excluded_variant_groups),
        "preference_targets": preference_targets or preferences.TARGETS,
        "preference_labels": preference_labels,
        "preference_count": 2 + len(preference_pairs if preference_pairs is not None else preferences.PAIRS),
        "selection_mode": selection_mode,
        "selection": ("Core/weight proposals screened on all declared preferences before publication"
                      if filtered else "ten distinct Core configurations, five equal boards; preferences audited without optimizing rank order"),
        "search": search_metadata,
        "variants": variants, "terminal_maps": maps, "coverage": coverage,
        "rule": {"items_per_board": 2, "items_total": 10, "item_share": 0.5, "missing_contribution": 0,
                 "exclude_at_missing": 4, "exclude_empty_board": True, "renormalize_missing": False,
                 "weights": None if filtered else [20]*5,
                 "weights_by_variant": {key: config["weights"] for key, config in variants.items()},
                 "bonus_requires_complete_board": True},
        "results": {key: {k: v for k, v in result.items() if k not in ("rows", "common_rows", "excluded")}
                    for key, result in results.items()}, "validation": validation,
    }
    (output / "run.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    if write_markdown:
        from analysis.irt_leaderboard_exploration.dual_core_reports import write_reports
        write_reports(output, variants, results, metadata)
    return {key: {"population": len(result["rows"]), "missing": result["missing_distribution"],
                  "preference_passed": result["preference_audit"]["passed"],
                  "checks_passed": sum(c["passed"] for c in result["preference_audit"]["checks"]),
                  "top3": [(r["model"], round(r["score"], 3)) for r in result["rows"][:3]]}
            for key, result in results.items()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=base.ROOT / "docs/data/models.json")
    parser.add_argument("--raw-csv", type=Path, default=base.ROOT / "ArtificialAnalysis/artificialanalysis_raw_scores_wide.csv")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.raw_csv, args.output_dir), ensure_ascii=False, indent=2))
