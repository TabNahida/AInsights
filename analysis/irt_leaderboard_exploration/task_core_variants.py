"""Next-round task/hard-test Core search; never changes production Scheme 18.

Requires NumPy. SciPy, when installed, supplies an independent continuous-weight
feasibility audit; the actual proposal screen always uses the full 1pp grid.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import re
import sys

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from analysis.irt_leaderboard_exploration import filtered_dual_core_variants as previous

dual, base, preferences, BOARDS = previous.dual, previous.base, previous.preferences, previous.BOARDS
OUTPUT = Path(__file__).resolve().parent / "outputs" / "task_dual_core"
CORE_OPTIONS = (
    ((base.LATEST_TB, "SciCode"),),
    tuple(itertools.combinations(("AutomationBench-AA", "τ³-Banking", "AA-Briefcase",
                                  "GDPval-AA v2", "τ²-Bench Telecom"), 2)),
    tuple(itertools.combinations(("CritPt", "Humanity's Last Exam", "AA-LCR v1.1"), 2)),
    tuple(("AA-Omniscience Accuracy", other)
          for other in ("Humanity's Last Exam", "MMMU-Pro", "GDP.pdf")),
    tuple(itertools.combinations(("AA-LCR v1.1", "GDP.pdf", "IFBench"), 2)),
)
POLICY = {
    "excluded_core_families": ["AIME (all years/aliases)", "HMMT", "MATH-500", "GSM8K",
                               "LiveCodeBench", "GPQA"],
    "scope": "Core only; existing extension policy is unchanged",
    "terminal": "v4_only",
    "weight_bounds_percent": [9, 40], "weight_step_percent": 1,
    "minimum_fixed_representatives_per_core": 100,
    "minimum_eligible_population": 100,
    "explicit_model_exclusions": [],
    "domain_assignment": {
        "coding": "Terminal task execution and scientific programming",
        "agentic-tool-work": "Automation, tool use, or professional work delivery",
        "hard-reasoning": "CritPt, HLE, or long-context reasoning; LCR changes the domain's emphasis",
        "knowledge-science": "Omniscience plus academic, multimodal, or PDF knowledge work",
        "instruction-context": "Long-context reasoning, PDF understanding, or instruction following",
    },
}


def forbidden_core(key):
    """Block families and aliases, rather than just one historical column name."""
    name = re.sub(r"[^a-z0-9]", "", key.lower())
    return any(token in name for token in ("aime", "hmmt", "math500", "gsm8k", "livecodebench", "gpqa"))


def validate_next_core(core):
    dual.validate_core(core)
    rejected = [key for pair in core.values() for key in pair if forbidden_core(key)]
    if rejected:
        raise ValueError("Forbidden next-round Core family: " + ", ".join(rejected))
    if any(dual.canonical_family(key) == "terminal-bench" and key != base.LATEST_TB
           for pair in core.values() for key in pair):
        raise ValueError("Only explicit Terminal v4 is allowed")


def preference_differences(rows):
    """Linear inequalities equivalent to all nine rank and pair conditions.

    Include Fable against all contenders, even though positive Astra margins
    imply these inequalities. This also makes a negative maximin interpretable.
    """
    lookup = {row["slug"]: row for row in rows}
    if not set(previous.CURRENT_TARGETS) <= lookup.keys():
        raise ValueError("All named targets must be eligible before feasibility analysis")
    fable, astra = previous.CURRENT_TARGETS[:2]
    pairs = [(fable, slug) for slug in lookup if slug != fable]
    pairs += [(astra, slug) for slug in lookup if slug not in (fable, astra)]
    pairs += [(previous.CURRENT_TARGETS[a], previous.CURRENT_TARGETS[b])
              for a, b in previous.CURRENT_PAIRS]
    pairs = list(dict.fromkeys(pairs))
    differences = np.array([[lookup[a][b + "_score"] - lookup[c][b + "_score"]
                             for b in BOARDS] for a, c in pairs], dtype=float)
    return pairs, differences


def maximum_pair_margin(difference, lower=9, upper=40):
    """Exact linear optimum on bounded weights summing to 100 (no solver)."""
    weights = np.full(5, float(lower))
    budget = 100 - 5 * lower
    if budget < 0 or 5 * upper < 100:
        raise ValueError("Infeasible weight bounds")
    for index in np.argsort(-np.asarray(difference), kind="stable"):
        add = min(budget, upper - lower)
        weights[index] += add
        budget -= add
    return float(np.asarray(difference) @ weights / 100), weights.tolist()


def continuous_diagnostic(rows):
    pairs, differences = preference_differences(rows)
    impossible = []
    for pair, gap in zip(pairs, differences):
        maximum, weights = maximum_pair_margin(gap)
        if maximum <= preferences.MIN_MARGIN:
            impossible.append({"higher": pair[0], "lower": pair[1], "maximum_margin": maximum,
                               "domain_differences": gap.tolist(), "maximizing_weights": weights})
    result = {"individually_impossible": impossible}
    try:
        from scipy.optimize import linprog
    except ImportError:
        return {**result, "available": False, "reason": "SciPy is not installed; exact grid still runs"}
    gaps = differences / 100
    fit = linprog([0, 0, 0, 0, 0, -1], A_ub=np.c_[-gaps, np.ones(len(gaps))],
                  b_ub=np.zeros(len(gaps)), A_eq=[[1, 1, 1, 1, 1, 0]], b_eq=[100],
                  bounds=[(9, 40)] * 5 + [(None, None)], method="highs")
    if not fit.success:
        raise RuntimeError("Continuous feasibility solver failed: " + fit.message)
    weights, claimed = fit.x[:5], float(fit.x[-1])
    actual = gaps @ weights
    if not (abs(weights.sum() - 100) < 1e-7 and np.all(weights >= 9 - 1e-7)
            and np.all(weights <= 40 + 1e-7) and abs(float(actual.min()) - claimed) < 1e-7):
        raise AssertionError("Continuous feasibility witness failed independent arithmetic checks")
    return {**result, "available": True, "best_minimum_margin": float(actual.min()),
            "weights": weights.tolist(),
            "binding": [{"higher": pair[0], "lower": pair[1], "margin": float(gap)}
                        for pair, gap in zip(pairs, actual) if abs(gap - claimed) < 1e-6]}


def search_candidates(models, maps, *, options=CORE_OPTIONS, values=range(9, 41),
                      minimum_population=100, minimum_item_coverage=100, diagnose=True):
    values = tuple(values)
    grid = previous.weight_grid(values)
    counts = Counter()
    candidates, structures = [], []
    for pairs in itertools.product(*options):
        core = dict(zip(BOARDS, pairs))
        counts["structures_considered"] += 1
        try:
            validate_next_core(core)
        except ValueError:
            counts["invalid_core_structures"] += 1
            continue
        counts["valid_core_structures"] += 1
        inadequate = [key for pair in pairs for key in pair
                      if sum(base.number(m["scores"].get(key)) is not None for m in models) < minimum_item_coverage]
        if inadequate:
            counts["insufficient_benchmark_coverage"] += 1
            structures.append({"core": core, "status": "insufficient_benchmark_coverage", "items": inadequate})
            continue
        rows, excluded, calibration, eligible = dual.score_variant(models, core, [20] * 5, maps, "v4_only")
        missing = sorted(set(previous.CURRENT_TARGETS) - {r["slug"] for r in rows})
        record = {"core": core, "population": len(rows), "missing_targets": missing}
        if len(rows) < minimum_population or missing:
            counts["ineligible_structures"] += 1
            record.update(status="ineligible", target_exclusions=[r for r in excluded if r["slug"] in missing])
            structures.append(record)
            continue
        counts["evaluated_core_structures"] += 1
        counts["evaluated_core_weight_combinations"] += len(grid)
        passing = previous.passing_weight_indices(rows, grid, targets=previous.CURRENT_TARGETS,
                                                  pairs=previous.CURRENT_PAIRS)
        record.update(status="evaluated", passing_weights=len(passing))
        if diagnose:
            if min(values) != 9 or max(values) != 40:
                raise ValueError("Continuous diagnostic bounds are defined for 9--40%")
            record["continuous"] = continuous_diagnostic(rows)
        for index in passing:
            weights = grid[index].astype(int).tolist()
            ranked = dual.score_models(eligible, core, weights, calibration)
            audit = preferences.constraint_audit(ranked, **previous.AUDIT_KWARGS)
            if not audit["passed"]:
                raise AssertionError("Grid screen disagrees with full ranking audit")
            sensitivity = preferences.weight_sensitivity(ranked, weights, **previous.AUDIT_KWARGS)
            candidates.append({"core": core, "weights": weights, "population": len(rows),
                               "minimum_margin": audit["minimum_margin"],
                               "distance_from_equal": sum(abs(w - 20) for w in weights),
                               "sensitivity_passing": sensitivity["passing"], "sensitivity_total": sensitivity["total"],
                               "missing_core_total": sum(r["missing_core_count"] for r in ranked)})
        structures.append(record)
    candidates.sort(key=lambda c: (previous.core_signature(c["core"]), tuple(c["weights"])))
    return {**dict(counts), "weight_vectors": len(grid), "weight_range": [min(values), max(values)],
            "weight_step": 1, "minimum_population": minimum_population,
            "minimum_item_coverage": minimum_item_coverage, "minimum_margin": preferences.MIN_MARGIN,
            "passing_combinations": len(candidates), "distinct_core_combinations": len({previous.core_signature(c["core"]) for c in candidates}),
            "core_options": dict(zip(BOARDS, options)), "candidates": candidates, "structures": structures}


def make_variants(selected):
    return {f"tc{i:02d}": {
        "label": f"{i:02d} 任务与高难测试·{role}",
        "purpose": reason + "仅保留九条排序条件全通过的结果。",
        "tradeoff": "AIME、LiveCodeBench、GPQA 不进入 Core。上下文推理和 PDF 知识工作属于显式领域取舍；"
                    "MMMU-Pro、IFBench、Telecom 仍可能有覆盖偏差，Elo 项目不是原生通过率。详见 CORE_QUALITY.md。",
        "core": candidate["core"], "weights": candidate["weights"], "fallback": "v4_only",
    } for i, (candidate, (role, reason)) in enumerate(selected, 1)}


def select_common_passing(search, models, maps, count=10):
    """Recheck calibration on the common cohort before writing any rankings."""
    remaining = list(search["candidates"])
    rejected = []
    while remaining:
        selected = previous.select_candidates({"candidates": remaining}, count=count)
        prepared = [dual.prepare(models, c["core"], maps, "v4_only")[0] for c, _ in selected]
        common = set.intersection(*({m["slug"] for m in group} for group in prepared))
        failures = []
        for (candidate, _), group in zip(selected, prepared):
            cohort = [m for m in group if m["slug"] in common]
            calibration = dual.fit_calibration(cohort, candidate["core"])
            rows = dual.score_models(cohort, candidate["core"], candidate["weights"], calibration)
            if not preferences.constraint_audit(rows, **previous.AUDIT_KWARGS)["passed"]:
                failures.append(candidate)
        if not failures:
            return selected, rejected
        rejected.extend(failures)
        remaining = [c for c in remaining if c not in failures]
    return [], rejected


def write_search_report(output, search, metadata, selected_count):
    records = [r for r in search["structures"] if r.get("continuous", {}).get("available")]
    best = max(records, key=lambda r: r["continuous"]["best_minimum_margin"], default=None)
    lines = ["# 任务与高难测试双 Core：本轮筛选结果", "",
             f"冻结快照：{metadata['source_generated_at']}；本轮通过全量筛选的 Core／权重组合 **{search['passing_combinations']}** 个，"
             f"最终通过共同集合复核并展示 **{selected_count}** 套。", "",
             "本轮只改变 Core 准入和配对池。AIME（含年度／别名及同类短题数学家族）、LiveCodeBench、GPQA 不得进入 Core；"
             "扩展加分沿用原规则，AIME 仍可作为受完整领域条件、正残差和动态上限约束的扩展。", "",
             "每领域两项各占基础分一半；缺项固定份额计零；领域双缺或累计缺至少四项剔除。"
             "只用 Terminal v4，固定配置先于缺测检查，真实零与缺测区分；没有模型专属扣分或人工排除。", "",
             "## 搜索范围与结果", "",
             f"候选配对共 {search['structures_considered']} 种；{search.get('invalid_core_structures', 0)} 种因重复家族或准入限制无效，"
             f"{search.get('valid_core_structures', 0)} 种结构合法。每个 Core 至少有 {search['minimum_item_coverage']} 个固定代表配置的直接成绩。",
             f"{search.get('insufficient_benchmark_coverage', 0)} 种未满足单项覆盖门槛；"
             f"{search.get('ineligible_structures', 0)} 种未满足目标模型／总体入榜门槛；"
             f"{search.get('evaluated_core_structures', 0)} 种进入权重搜索。",
             f"每领域 9%–40%，总和 100%，步长 1 个百分点；每结构 {search['weight_vectors']:,} 组，"
             f"实际检查 **{search.get('evaluated_core_weight_combinations', 0):,}** 组 Core／权重组合。", "",
             "九条偏好均保持不变，分差必须严格大于 0.05 分：", ""]
    lines += [f"{i}. {label}。" for i, label in enumerate(previous.CURRENT_LABELS, 1)]
    lines += ["", "## 领域配对依据", "",
              "编程固定 Terminal v4＋SciCode；Agent 枚举自动化、银行、电信、Briefcase 和 GDPval 的两两组合。"
              "推理枚举 CritPt、HLE、LCR；知识固定 Omniscience，再配 HLE、MMMU-Pro 或 GDP.pdf；"
              "上下文枚举 LCR、GDP.pdf、IFBench。所有十个槽位必须来自十个不同家族。", "",
              "LCR 进入推理会增加长上下文成分；GDP.pdf 在来源注册表中归为 Knowledge work vision，进入知识领域有任务定义依据。"
              "GDPval 和 Briefcase 的 Elo 线性换算不代表原生通过率。扩池用于检验可行性，不表示这些组合的测量质量等价。", ""]
    if best:
        diag = best["continuous"]
        lines += ["## 独立连续权重诊断", "",
                  f"对 {len(records)} 个可评估结构，额外允许 9%–40% 内任意小数权重，最大化全部排序不等式中的最小分差。"
                  f"所有结构中的最优值为 **{diag['best_minimum_margin']:.6f} 分**；门槛是 **严格大于 0.05 分**。", ""]
        if diag["best_minimum_margin"] < 0.05 - 1e-7:
            lines += ["连续范围也没有合格解，所以仅把步长细化为小数无法解决当前冲突。此结论限定于上述 Core 池、冻结成绩和计分规则。", ""]
        lines += ["以下仅为冲突诊断，不是可选方案，不发布其 Top30：", ""]
        lines += [f"- {base.BOARD_LABELS[b]}：{'＋'.join(best['core'][b])}" for b in BOARDS]
        lines += ["", "该最优边界同时受以下排序关系限制：", ""]
        names = metadata.get("model_names", {})
        lines += [f"- {names.get(r['higher'], r['higher'])} − {names.get(r['lower'], r['lower'])}：{r['margin']:.6f} 分。"
                  for r in diag["binding"]]
        lines += ["", "逐结构的最大分差、单独无法满足的模型对、领域差值和缺测原因均保存在 [search.json](search.json)。", ""]
    lines += ["## 本轮结论", ""]
    if not selected_count:
        lines += ["本轮没有可展示的合格方案，因此没有生成不合格榜单来凑足十套。"
                  "下一步应增加覆盖充分且符合 Core 准入的任务／高难测试数据，或明确调整排序条件／计分假设后再搜索。"
                  "本轮没有替用户放宽这些条件。", ""]
        empty = "# 本轮 Top30 对比\n\n没有通过全部筛选条件的方案，因此本轮没有 Top30。\n\n原因和搜索证据见 [SEARCH_REPORT.md](SEARCH_REPORT.md)；上一轮含 AIME／GPQA Core 的榜单仅保留为历史结果。\n"
        (output / "TOP30_COMPARISON.md").write_text(empty, encoding="utf-8")
        (output / "SCHEMES.md").write_text("# 本轮方案说明\n\n本轮无合格方案。完整规则、候选池及冲突解释见 [SEARCH_REPORT.md](SEARCH_REPORT.md)。\n", encoding="utf-8")
    else:
        lines += ["完整方案见 [SCHEMES.md](SCHEMES.md)，Top30 见 [TOP30_COMPARISON.md](TOP30_COMPARISON.md)。"
                  "通过具名顺序仍不等于综合能力已获独立验证，须结合本轮覆盖审计阅读。", ""]
    lines += ["测试覆盖、近期群体和分数集中情况见 [CORE_QUALITY.md](CORE_QUALITY.md)。", "",
              "复现：`python -B analysis/irt_leaderboard_exploration/task_core_variants.py`。"
              "整数权重搜索依赖现有 NumPy；连续权重诊断额外使用 SciPy，未安装时只跳过该诊断，仍完整运行整数网格。", "",
              "来源：冻结 `docs/data/models.json` 与 `ArtificialAnalysis/artificialanalysis_raw_scores_wide.csv`；"
              "源哈希、规则、搜索计数见 [run.json](run.json)。正式方案 18、站点和每日 Action 均未切换。", ""]
    (output / "SEARCH_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def run(input_json, raw_csv, output):
    from analysis.irt_leaderboard_exploration import core_suitability
    payload, all_models, models, maps = dual.load_inputs(input_json, raw_csv, terminal_mode="v4_only")
    output.mkdir(parents=True, exist_ok=True)
    if list(output.glob("rankings_*.csv")):
        raise ValueError("Use a fresh output directory to avoid retaining old rankings after a failed search")
    core_suitability.write_report(output, core_suitability.profile(payload, all_models, models, previous.CURRENT_TARGETS))
    search = search_candidates(models, maps)
    selected, rejected = select_common_passing(search, models, maps)
    search["common_selection_rejections"] = rejected
    metadata = {"source_generated_at": payload["generatedAt"], "core_policy": POLICY,
                "source_hashes": {str(p.relative_to(base.ROOT) if p.is_relative_to(base.ROOT) else p): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in (input_json, raw_csv)},
                "representative_count": len(models), "selection_count": len(selected),
                "model_names": {model["slug"]: model["model"] for model in models},
                "search": {k: v for k, v in search.items() if k not in ("structures", "candidates")}}
    if selected:
        variants = make_variants(selected)
        dual.run(input_json, raw_csv, output, variants=variants, selection_mode="preference_filtered",
                 search_metadata=metadata["search"], preference_targets=previous.CURRENT_TARGETS,
                 preference_pairs=previous.CURRENT_PAIRS, preference_labels=previous.CURRENT_LABELS,
                 excluded_variant_groups=())
        generated = json.loads((output / "run.json").read_text(encoding="utf-8"))
        metadata = {**generated, "core_policy": POLICY, "selection_count": len(selected)}
    (output / "run.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / "search.json").write_text(json.dumps(search, ensure_ascii=False, indent=2), encoding="utf-8")
    write_search_report(output, search, metadata, len(selected))
    return {"passing_combinations": search["passing_combinations"], "selected_count": len(selected),
            "evaluated_core_structures": search.get("evaluated_core_structures", 0),
            "evaluated_core_weight_combinations": search.get("evaluated_core_weight_combinations", 0)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=base.ROOT / "docs/data/models.json")
    parser.add_argument("--raw-csv", type=Path, default=base.ROOT / "ArtificialAnalysis/artificialanalysis_raw_scores_wide.csv")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.raw_csv, args.output_dir), ensure_ascii=False, indent=2))
