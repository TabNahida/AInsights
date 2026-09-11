"""Screen proposals with exactly two single-Core and three dual-Core domains.

This is a frozen-data experiment. It does not change the website or daily Action.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import sys

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from analysis.irt_leaderboard_exploration import mixed_core_engine as engine
from analysis.irt_leaderboard_exploration import task_core_variants as task
from analysis.irt_leaderboard_exploration import core_suitability

base, BOARDS, previous, preferences = task.base, task.BOARDS, task.previous, task.preferences
OUTPUT = Path(__file__).resolve().parent / "outputs" / "mixed_core"


def core_options():
    result = []
    for board, pairs in zip(BOARDS, task.CORE_OPTIONS):
        singles = ("AA-Omniscience Accuracy",) if board == "knowledge-science" else tuple(dict.fromkeys(k for pair in pairs for k in pair))
        result.append(tuple(pairs) + tuple((key,) for key in singles))
    return tuple(result)


CORE_OPTIONS = core_options()


def singleton_count(core):
    return sum(len(items) == 1 for items in core.values())


def reasoning_example(models):
    lookup = {m["slug"]: m for m in models}
    slugs = ("gpt-5-6-terra", "muse-spark-1-3")
    values = [[base.number(lookup.get(slug, {}).get("scores", {}).get(key))
               for key in ("CritPt", "Humanity's Last Exam")] for slug in slugs]
    if any(value is None for pair in values for value in pair):
        return ""
    terra, muse = values
    return (f"在本次冻结快照中，Terra的CritPt为{terra[0]:g}、HLE为{terra[1]:g}；"
            f"Muse的CritPt为{muse[0]:g}、HLE为{muse[1]:g}。"
            f"双项平均的领域分差（Terra−Muse）为{(sum(terra)-sum(muse))/2:.5f}，"
            f"仅用CritPt时为{terra[0]-muse[0]:.5f}。这是不同测试证据的取舍，没有型号专属加分；"
            "总榜仍须按全部领域和扩展重新验证。")


def margin_vector(rows, weights):
    """Compute exact unrounded linear margins in bounded-memory batches."""
    _, differences = task.preference_differences(rows)
    return np.concatenate([np.min(differences @ weights[start:start + 4096].T / 100, axis=0)
                           for start in range(0, len(weights), 4096)]) if len(weights) else np.empty(0)


def candidate_shortlist(core_id, core, rows, weights):
    """Keep an explicitly bounded selection pool, retaining all passing weights separately."""
    margins = margin_vector(rows, weights)
    distance = np.abs(weights - 20).sum(axis=1)
    stable = tuple(weights[:, index] for index in reversed(range(5)))
    close = np.lexsort((*stable, -margins, distance))[:16]
    robust = np.lexsort((*stable, distance, -margins))[:16]
    indexes = sorted(set(close.tolist() + robust.tolist()))
    result = []
    for index in indexes:
        vector = weights[index].astype(int).tolist()
        ranked = preferences.weighted_rows(rows, vector)
        audit = preferences.constraint_audit(ranked, **previous.AUDIT_KWARGS)
        if not audit["passed"]:
            raise AssertionError("Grid screen disagrees with full ranking audit")
        sensitivity = preferences.weight_sensitivity(ranked, vector, **previous.AUDIT_KWARGS)
        result.append({"core_id": core_id, "core": core, "weights": vector,
                       "single_core_domains": singleton_count(core), "population": len(rows),
                       "minimum_margin": audit["minimum_margin"], "distance_from_equal": int(distance[index]),
                       "sensitivity_passing": sensitivity["passing"], "sensitivity_total": sensitivity["total"]})
    return result


def select_candidates(candidates, count=10):
    """Prefer fewer singletons, then distinct structures, then contrasting weights."""
    chosen = []
    for singles in sorted({c["single_core_domains"] for c in candidates}):
        groups = {}
        for candidate in candidates:
            if candidate["single_core_domains"] == singles:
                groups.setdefault(candidate["core_id"], []).append(candidate)
        ordered = sorted(groups, key=lambda key: (
            min(c["distance_from_equal"] for c in groups[key]),
            -max(c["minimum_margin"] for c in groups[key]), key))
        per_group = {key: [] for key in ordered}
        for turn in range(max((len(groups[key]) for key in ordered), default=0)):
            for key in ordered:
                available = [c for c in groups[key] if c not in per_group[key]]
                if not available:
                    continue
                tie = lambda c: (-c["minimum_margin"], tuple(c["weights"]))
                if turn == 0:
                    preference = lambda c: (c["distance_from_equal"], *tie(c))
                    role = "接近等权"
                elif turn == 1:
                    preference, role = tie, "分差优先"
                elif turn == 2:
                    preference = lambda c: (-c["sensitivity_passing"], *tie(c))
                    role = "扰动对照"
                else:
                    preference = lambda c: (-min(sum(abs(a - b) for a, b in zip(c["weights"], old["weights"]))
                                                for old in per_group[key]), *tie(c))
                    role = "权重差异对照"
                selected = min(available, key=preference)
                per_group[key].append(selected)
                chosen.append({**selected, "selection_role": role})
                if len(chosen) == count:
                    return chosen
    return chosen


def candidate_identity(candidate):
    return candidate["core_id"], tuple(candidate["weights"])


def common_selection(candidates, prepared, count=10):
    remaining, rejected = list(candidates), []
    while remaining:
        selected = select_candidates(remaining, count)
        common = set.intersection(*({m["slug"] for m in prepared[c["core_id"]]} for c in selected))
        failed = set()
        for candidate in selected:
            models = [m for m in prepared[candidate["core_id"]] if m["slug"] in common]
            cal = engine.fit_calibration(models, candidate["core"])
            rows = engine.score_models(models, candidate["core"], candidate["weights"], cal)
            audit = preferences.constraint_audit(rows, **previous.AUDIT_KWARGS)
            if not audit["passed"]:
                failed.add(candidate_identity(candidate))
                rejected.append({"core_id": candidate["core_id"], "weights": candidate["weights"], "audit": audit})
        if not failed:
            return selected, rejected
        remaining = [c for c in remaining if candidate_identity(c) not in failed]
    return [], rejected


def search(models, *, options=CORE_OPTIONS, values=range(9, 41), single_core_domains=2,
           desired_count=10, minimum_population=100, minimum_item_coverage=100):
    grid = previous.weight_grid(values)
    item_counts = {key: sum(base.number(m["scores"].get(key)) is not None for m in models)
                   for board_options in options for items in board_options for key in items}
    stages, structures, candidates = [], [], []
    prepared, calibrations, passing_weights = {}, {}, {}
    selected, common_rejections = [], []
    if single_core_domains not in range(1, 5):
        raise ValueError("Choose one to four single-Core domains")
    for singletons in (single_core_domains,):
        counts = Counter()
        for entries in itertools.product(*options):
            core = dict(zip(BOARDS, entries))
            if singleton_count(core) != singletons:
                continue
            counts["considered"] += 1
            try:
                engine.validate_core(core)
            except ValueError:
                counts["invalid"] += 1
                continue
            counts["valid"] += 1
            key = f"structure_{len(structures) + 1:04d}"
            record = {"id": key, "core": core, "single_core_domains": singletons}
            if any(item_counts[item] < minimum_item_coverage for items in core.values() for item in items):
                counts["insufficient_item_coverage"] += 1
                structures.append({**record, "status": "insufficient_item_coverage"})
                continue
            rows, excluded, calibration, eligible = engine.score_variant(models, core, [20] * 5)
            missing = sorted(set(previous.CURRENT_TARGETS) - {r["slug"] for r in rows})
            record.update(population=len(rows), missing_targets=missing)
            if missing or len(rows) < minimum_population:
                counts["ineligible"] += 1
                structures.append({**record, "status": "ineligible",
                                   "target_exclusions": [r for r in excluded if r["slug"] in missing]})
                continue
            counts["evaluated"] += 1
            counts["weight_combinations"] += len(grid)
            indices = previous.passing_weight_indices(rows, grid, targets=previous.CURRENT_TARGETS,
                                                      pairs=previous.CURRENT_PAIRS)
            record.update(status="evaluated", passing_weights=len(indices))
            if len(indices):
                counts["passing_structures"] += 1
                counts["passing_weights"] += len(indices)
                weights = grid[indices]
                candidates.extend(candidate_shortlist(key, core, rows, weights))
                passing_weights[key] = weights.astype(np.uint8)
                prepared[key], calibrations[key] = eligible, calibration
            structures.append(record)
        selected, common_rejections = common_selection(candidates, prepared, desired_count)
        stages.append({"single_core_domains": singletons, **dict(counts), "selected_after_common_check": len(selected)})
        print(json.dumps({"stage": stages[-1]}, ensure_ascii=False), flush=True)
        if len(selected) >= desired_count:
            break
    metadata = {
        "stages": stages, "structures": structures,
        "structures_considered": sum(s.get("considered", 0) for s in stages),
        "valid_core_structures": sum(s.get("valid", 0) for s in stages),
        "evaluated_core_structures": sum(s.get("evaluated", 0) for s in stages),
        "evaluated_core_weight_combinations": sum(s.get("weight_combinations", 0) for s in stages),
        "weight_vectors": len(grid), "weight_range": [min(values), max(values)], "weight_step": 1,
        "minimum_population": minimum_population, "minimum_item_coverage": minimum_item_coverage,
        "passing_combinations": sum(s.get("passing_weights", 0) for s in stages),
        "distinct_passing_structures": sum(s.get("passing_structures", 0) for s in stages),
        "distinct_core_combinations": sum(s.get("passing_structures", 0) for s in stages),
        "selected_count": len(selected),
        "single_core_domains_requested": single_core_domains,
        "stopped_after_singletons": stages[-1]["single_core_domains"],
        "stop_reason": "exact_singleton_count_search_complete",
        "candidate_selection_pool_count": len(candidates),
        "candidate_selection_pool": candidates, "common_selection_rejections": common_rejections,
        "core_options": dict(zip(BOARDS, options)),
        "selection_policy": "按用户选择固定两个单Core领域；优先覆盖不同结构，再选不同权重。每结构从全部合格权重中保留最接近等权16个和最小分差最大16个（去重），再审计扰动及共同人群。完整通过权重另存NPZ，不声称穷举了所有十方案组合的共同人群。",
    }
    return metadata, selected, prepared, calibrations, passing_weights


def build_results(selected, prepared, calibrations, all_selected):
    variants, results, validation = {}, {}, {}
    common = set.intersection(*({m["slug"] for m in prepared[c["core_id"]]} for c in selected)) if selected else set()
    for index, candidate in enumerate(selected, 1):
        key, core, weights = f"mc{index:02d}", candidate["core"], candidate["weights"]
        singles = "、".join(base.BOARD_LABELS[b] for b in BOARDS if len(core[b]) == 1)
        variants[key] = {"label": f"{index:02d} {singles}单Core·{candidate['selection_role']}",
                         "purpose": f"仅将{singles}设为单 Core，保留其他领域双 Core；按{candidate['selection_role']}选择权重。",
                         "tradeoff": "单项承担领域全部基础权重，唯一项缺测即剔除；双项各半，缺项不重分配。扩展按相同规则重新拟合。",
                         "core": core, "weights": weights, "fallback": "v4_only",
                         "single_core_domains": candidate["single_core_domains"], "source_structure": candidate["core_id"]}
        models = prepared[candidate["core_id"]]
        cal = calibrations[candidate["core_id"]]
        rows = engine.score_models(models, core, weights, cal)
        _, excluded = engine.prepare(all_selected, core)
        cohort = [m for m in models if m["slug"] in common]
        common_cal = engine.fit_calibration(cohort, core)
        common_rows = engine.score_models(cohort, core, weights, common_cal)
        result = {"rows": rows, "excluded": excluded, "calibration": cal,
                  "preference_audit": preferences.constraint_audit(rows, **previous.AUDIT_KWARGS),
                  "common_rows": common_rows, "common_calibration": common_cal,
                  "common_preference_audit": preferences.constraint_audit(common_rows, **previous.AUDIT_KWARGS),
                  "sensitivity": preferences.weight_sensitivity(rows, weights, **previous.AUDIT_KWARGS)}
        if not result["preference_audit"]["passed"] or not result["common_preference_audit"]["passed"]:
            raise AssertionError("A selected proposal failed a required ranking audit")
        validation[key] = {"full": engine.validate_rows(rows, core, weights),
                           "common": engine.validate_rows(common_rows, core, weights)}
        if not all(check["passed"] for check in validation[key].values()):
            raise AssertionError(validation[key])
        results[key] = result
    return variants, results, validation, len(common)


def write_search_report(output, summary, metadata):
    count = len(metadata["variants"])
    lines = ["# 单／双 Core 混合方案：搜索记录", "",
             f"冻结数据：{metadata['source_generated_at']}。本轮得到 **{count}** 套全量与共同集合九条标准均通过的方案。", "",
             "唯一改变是允许部分领域设置一项 Core，该项承担领域100%基础权重；两项领域仍各50%。"
             "所有已配置 Core 全缺的领域立即剔除；累计缺至少四项也剔除；未配置第二项不算缺测。", "",
             "AIME／LiveCodeBench／GPQA 等禁止进入 Core，Terminal 只用 v4。固定代表先于资格筛选；没有型号专属扣分和人工排除。"
             "扩展沿用现有规则并按当前 Core／人口重新拟合。旧 Terminal 无论有没有进入 Core，均不能作为扩展。", "",
             "## 固定单 Core 领域数的搜索", "",
             f"按用户选择，本轮固定 {summary['single_core_domains_requested']} 个单 Core 领域，"
             f"其余 {5-summary['single_core_domains_requested']} 个领域保持双 Core；检查这个范围的全部合法结构。"
             "知识单项只允许 Omniscience Accuracy，其余单项来自上一轮各领域候选成员。", "",
             "| 单Core领域数 | 考察结构 | 结构无效 | 单项覆盖不足 | 资格不符 | 搜索结构 | 权重组合检查 | 通过结构 | 通过权重 |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for s in summary["stages"]:
        lines.append("| " + " | ".join(str(s.get(key, 0)) for key in (
            "single_core_domains", "considered", "invalid", "insufficient_item_coverage", "ineligible",
            "evaluated", "weight_combinations", "passing_structures", "passing_weights")) + " |")
    lines += ["", f"权重固定为9%–40%、合计100%，1个百分点步长，每结构{summary['weight_vectors']:,}组。"
              "每个Core至少100个固定代表有观测，每方案至少100个模型入榜；九条标准和严格大于0.05分的门槛保留。", "",
              "## 如何理解单 Core 的作用", "",
              "减少一项会改变领域所衡量的能力，也会改变缺测和扩展拟合。" + metadata.get("reasoning_example", ""), "",
              "## 方案选择与复现", "", summary["selection_policy"], "",
              f"完整通过权重共{summary['passing_combinations']:,}组，来自{summary['distinct_passing_structures']}种结构，"
              f"压缩保存于`passing_weights.npz`；每个数组名对应`search.json`中的结构ID，各行依次是编程、Agent、推理、知识、上下文权重。", "",
              "运行：`python -B analysis/irt_leaderboard_exploration/mixed_core_variants.py`。"
              "[方案详解](SCHEMES.md) · [Top30对比](TOP30_COMPARISON.md) · [测试质量与覆盖](CORE_QUALITY.md)。", "",
              "通过具名顺序只是本次筛选条件；单Core更依赖单个测试的可靠性，不等于测量质量自然提高。"
              "正式方案18、站点与每日Action保持原状。", ""]
    (output / "SEARCH_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def run(input_json, raw_csv, output, *, single_core_domains=2):
    payload, all_models, representatives, _ = task.dual.load_inputs(input_json, raw_csv, terminal_mode="v4_only")
    if output.exists() and any(output.glob("rankings_*.csv")):
        raise ValueError("Use a fresh output directory to avoid retaining stale proposal rankings")
    search_summary, selected, prepared, calibrations, all_weights = search(representatives, single_core_domains=single_core_domains)
    if any(singleton_count(c["core"]) != single_core_domains for c in selected):
        raise AssertionError("Selected proposal does not match the requested number of single-Core domains")
    variants, results, validation, common_count = build_results(selected, prepared, calibrations, representatives)
    metadata = {"source_generated_at": payload["generatedAt"], "input_model_count": len(all_models),
                "representative_count": len(representatives), "common_population": common_count,
                "source_hashes": {str(p.relative_to(base.ROOT) if p.is_relative_to(base.ROOT) else p): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in (input_json, raw_csv)},
                "selection_mode": "preference_filtered", "terminal_mode": "v4_only",
                "preference_labels": previous.CURRENT_LABELS, "preference_targets": previous.CURRENT_TARGETS,
                "minimum_preference_margin": preferences.MIN_MARGIN, "variants": variants, "validation": validation,
                "excluded_variant_groups": [], "user_exclusions": [],
                "reasoning_example": reasoning_example(representatives),
                "rules": {"core_items_per_board": [1, 2], "single_item_share": 1.0, "pair_item_share": 0.5,
                          "exclude_empty_board": True, "exclude_at_missing": 4, "renormalize_missing": False,
                          "extension_requires_all_configured_core": True, "excluded_core_policy": task.POLICY},
                "search": {k: v for k, v in search_summary.items() if k not in ("structures", "candidate_selection_pool")},
                "results": {k: {name: value for name, value in result.items() if name not in ("rows", "excluded", "common_rows")}
                            for k, result in results.items()}}
    output.mkdir(parents=True, exist_ok=True)
    quality = core_suitability.write_report(output, core_suitability.profile(payload, all_models, representatives, previous.CURRENT_TARGETS))
    metadata["coverage"] = [{**row, "fixed_representatives": row["representatives"]["observed"]} for row in quality["rows"]]
    metadata["core_quality"] = quality
    for key, result in results.items():
        for name, rows in (("rankings", result["rows"]), ("top30", result["rows"][:30]),
                           ("common", result["common_rows"]), ("excluded", result["excluded"])):
            base.scheme18.write_csv(output / f"{name}_{key}.csv", rows)
    base.scheme18.write_csv(output / "top30_all.csv", [{"variant": key, **row} for key, result in results.items() for row in result["rows"][:30]])
    base.scheme18.write_csv(output / "preference_audit.csv", [
        {"variant": key, "population": scope, **check} for key, result in results.items()
        for scope, name in (("full", "preference_audit"), ("common", "common_preference_audit"))
        for check in result[name]["checks"]])
    np.savez_compressed(output / "passing_weights.npz", **all_weights)
    (output / "search.json").write_text(json.dumps(search_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / "run.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    write_search_report(output, search_summary, metadata)
    from analysis.irt_leaderboard_exploration.mixed_core_reports import write_reports
    write_reports(output, variants, results, metadata)
    return {"selected_count": len(variants), "search_stages": search_summary["stages"], "common_population": common_count}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=base.ROOT / "docs/data/models.json")
    parser.add_argument("--raw-csv", type=Path, default=base.ROOT / "ArtificialAnalysis/artificialanalysis_raw_scores_wide.csv")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    parser.add_argument("--single-core-domains", type=int, choices=range(1, 5), default=2)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.raw_csv, args.output_dir, single_core_domains=args.single_core_domains), ensure_ascii=False, indent=2))
