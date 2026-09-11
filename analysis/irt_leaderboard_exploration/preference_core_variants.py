"""Core/weight candidates selected against explicit user ranking preferences.

Preferences select candidates AFTER anonymous scoring. They are never score
terms, row offsets, fixed positions, or edits to source observations. These are
preference-conditioned experiments, not independent validation of model quality.
Production Scheme 18 and the earlier A-D experiments remain unchanged.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from analysis.irt_leaderboard_exploration import core_variants as base

BOARDS = base.scheme18.BOARD_ORDER
OUTPUT = Path(__file__).resolve().parent / "outputs" / "preference_core_variants"
TARGETS = (
    "claude-fable-5-1", "gpt-6-astra", "kimi-k3", "gemini-3-8-flash",
    "gpt-5-5", "muse-spark-1-3", "qwen3-8-max", "qwen3-8-2-4t-a95b", "qwen3-8-flash-next",
)
PAIRS = ((2, 3), (4, 5), (6, 8), (7, 8))
MIN_MARGIN = 0.05
SHARED = {
    "coding": (base.TB,),
    "hard-reasoning": ("CritPt", "GPQA Diamond"),
    "knowledge-science": ("AA-Omniscience Accuracy",),
    "instruction-context": ("AA-LCR v1.1",),
}
VARIANTS = {
    "e_small_change": {
        "label": "E 权重小改", "fallback": "calibrated",
        "core": {**SHARED, "agentic-tool-work": ("AutomationBench-AA", "τ³-Banking")},
        "weights": (10, 20, 25, 25, 20),
    },
    "f_broad": {
        "label": "F 广覆盖", "fallback": "calibrated",
        "core": {**SHARED, "agentic-tool-work": ("τ³-Banking",)},
        "weights": (15, 10, 25, 25, 25),
    },
    "g_scientific_coding": {
        "label": "G 科学编程", "fallback": "calibrated",
        "core": {**SHARED, "coding": (base.TB, "SciCode"), "agentic-tool-work": ("AutomationBench-AA",)},
        "weights": (10, 15, 30, 25, 20),
    },
}


def weighted_rows(rows, weights):
    """Apply benchmark-board weights identically to every row, then sort."""
    if len(weights) != 5 or any(not math.isfinite(x) or x < 0 for x in weights) or not math.isclose(sum(weights), 100):
        raise ValueError("Five finite nonnegative board weights must sum to 100")
    ranked = []
    for source in rows:
        row = dict(source)
        row["equal_board_score"] = source["score"]
        row["score"] = math.fsum(float(row[b + "_score"]) * w / 100 for b, w in zip(BOARDS, weights))
        row["core_only_score"] = math.fsum(float(row[b + "_core"]) * w / 100 for b, w in zip(BOARDS, weights))
        ranked.append(row)
    ranked.sort(key=lambda r: (-r["score"], r["slug"]))
    for rank, row in enumerate(ranked, 1):
        row["rank"] = rank
    return ranked


def constraint_audit(rows, *, targets=TARGETS, pairs=PAIRS, margin_threshold=MIN_MARGIN, labels=None):
    lookup = {r["slug"]: r for r in rows}
    missing = [slug for slug in targets if slug not in lookup]
    checks = []
    for position, slug in enumerate(targets[:2], 1):
        row = lookup.get(slug)
        # First must beat everyone; second must beat every row except first.
        competitors = [r for r in rows if r["slug"] not in targets[:position]]
        competitor = max(competitors, key=lambda r: r["score"], default=None)
        margin = row["score"] - competitor["score"] if row and competitor else None
        checks.append({"condition": f"{slug} rank={position}", "higher": slug,
                       "lower": competitor["slug"] if competitor else None,
                       "margin": margin, "passed": bool(row and row["rank"] == position and margin is not None and margin > margin_threshold)})
    for a, b in pairs:
        high, low = lookup.get(targets[a]), lookup.get(targets[b])
        margin = high["score"] - low["score"] if high and low else None
        checks.append({"condition": f"{targets[a]} > {targets[b]}", "higher": targets[a], "lower": targets[b],
                       "margin": margin, "passed": margin is not None and margin > margin_threshold})
    if labels is not None:
        if len(labels) != len(checks):
            raise ValueError("Preference labels must match the number of checks")
        for check, label in zip(checks, labels):
            check["label"] = label
    return {"passed": not missing and all(c["passed"] for c in checks), "missing_targets": missing,
            "minimum_margin": min((c["margin"] for c in checks if c["margin"] is not None), default=None),
            "checks": checks}


def search_candidates(models, maps):
    """Reproduce the finite Core/weight search; publish its complete extent."""
    weight_grid = np.array([w for w in itertools.product(range(10, 41, 5), repeat=5) if sum(w) == 100], dtype=float) / 100
    options = (
        [(base.TB,), (base.TB, "SciCode")],
        [("AutomationBench-AA",), ("τ³-Banking",), ("AutomationBench-AA", "τ³-Banking")],
        [("CritPt",), ("Humanity's Last Exam", "CritPt"), ("CritPt", "GPQA Diamond"), ("Humanity's Last Exam", "GPQA Diamond")],
        [("AA-Omniscience Accuracy",), ("GPQA Diamond", "AA-Omniscience Accuracy")],
        [("AA-LCR v1.1",), ("AA-LCR v1.1", "GDP.pdf")],
    )
    found, trials, skipped = [], 0, 0
    for slots in itertools.product(*options):
        core = dict(zip(BOARDS, slots))
        eligible, _ = base.prepare(models, {"core": core, "fallback": "calibrated"}, maps)
        if len(eligible) < 100 or not set(TARGETS) <= {m["slug"] for m in eligible}:
            skipped += 1
            continue
        rows, _ = base.score_variant(eligible, core)
        index = {r["slug"]: i for i, r in enumerate(rows)}
        target_index = [index[t] for t in TARGETS]
        values = np.array([[r[b + "_score"] for b in BOARDS] for r in rows])
        scores = values @ weight_grid.T
        gaps = [scores[target_index[a]] - scores[target_index[b]] for a, b in ((0, 1), *PAIRS)]
        other = np.max(np.delete(scores, target_index[:2], axis=0), axis=0)
        gaps = np.vstack([*gaps, scores[target_index[1]] - other])
        trials += len(weight_grid)
        for j in np.flatnonzero(np.all(gaps > MIN_MARGIN, axis=0)):
            found.append({"core": core, "weights": [int(round(w * 100)) for w in weight_grid[j]],
                          "population": len(rows), "minimum_margin": float(gaps[:, j].min()),
                          "weight_l1_distance_from_equal": round(float(abs(weight_grid[j] - .2).sum()), 6)})
    found.sort(key=lambda r: (r["weight_l1_distance_from_equal"], -r["minimum_margin"]))
    return {"core_combinations": math.prod(len(x) for x in options), "skipped_core_combinations": skipped,
            "evaluated_core_weight_combinations": trials, "passing_combinations": len(found),
            "weight_grid_percent": "10..40 in steps of 5, total 100", "minimum_population": 100,
            "minimum_margin": MIN_MARGIN, "candidates": found}


def weight_sensitivity(rows, weights, **audit_kwargs):
    """Transfer one percentage point between boards, using fixed calibration."""
    checks = []
    for src, dst in itertools.permutations(range(5), 2):
        changed = list(weights)
        changed[src] -= 1
        changed[dst] += 1
        audit = constraint_audit(weighted_rows(rows, changed), **audit_kwargs)
        checks.append({"from": BOARDS[src], "to": BOARDS[dst], "passed": audit["passed"], "minimum_margin": audit["minimum_margin"]})
    return {"passing": sum(c["passed"] for c in checks), "total": len(checks), "checks": checks}


def write_report(output, results, common_count, search):
    lines = ["# 按指定排序偏好筛选的 Core 候选", "",
        "本轮偏好：Fable 5.1 第一、GPT-6 Astra 第二；Kimi K3 高于 Gemini 3.8 Flash；GPT-5.5 高于 Muse Spark 1.3；Qwen3.8 Max 和 Qwen3.8 2.4T A95B 均高于 Flash-Next。",
        "这些偏好用于筛选 Core／权重组合，不是对模型能力的独立验证。成绩统一按规则计算，未添加命名模型加减分或排序后挪位。正式 Scheme 18 和前轮 A–D 均不修改。",
        "配置固定为每组 variantPriority 最高的一档：Fable 5.1 使用 max with fallback，Astra/Kimi/Muse 使用 max，Gemini 使用 high，GPT-5.5 使用 xhigh（不混用 Pro/Instant）。",
        "", "## 本轮规则", "",
        "Terminal 优先同配置 v4 实测；缺失则通过重叠样本换算 v2.1，再乘 0.95；再缺失才换算 Hard 后乘 0.90。实测 0 不回退。",
        "Core 仍取几何平均，缺任意必测项不入榜；扩展使用原正残差加分和动态上限；新 Core 与所有 Terminal 版本不再重复获得扩展加分。",
        "本轮将 CritPt 放回推理板块，且只在这一板块使用。Omniscience Accuracy 单独构成知识板块；HLE 不在这三版 Core 中。G 额外使用 SciCode，且只在编程板块使用。",
        "", "| 板块 | E 权重小改 | F 广覆盖 | G 科学编程 |", "|---|---|---|---|"]
    for i, board in enumerate(BOARDS):
        lines.append("| " + base.BOARD_LABELS[board] + " | " + " | ".join(
            f"{', '.join(v['core'][board])} · {v['weights'][i]}%" for v in VARIANTS.values()) + " |")
    lines += ["", "## 名次与分数", "", "| 模型 | E 名次／分数 | F 名次／分数 | G 名次／分数 |", "|---|---:|---:|---:|"]
    lookups = [{r["slug"]: r for r in result["rows"]} for result in results.values()]
    for slug in TARGETS:
        model = next((table[slug]["model"] for table in lookups if slug in table), slug)
        cells = [f"{table[slug]['rank']} / {table[slug]['score']:.3f}" if slug in table else "缺 Core" for table in lookups]
        lines.append("| " + model + " | " + " | ".join(cells) + " |")
    lines += ["", "## 约束与敏感性", "", "每条顺序还要求超过 0.05 分，防止依赖完全相等或显示舍入。", "",
        "| 方案 | 入榜模型数 | 全部约束 | 最小分差 | 共同人群约束 | 权重微调通过数 |", "|---|---:|---|---:|---|---|"]
    for key, result in results.items():
        a, common, sensitivity = result["audit"], result["common_audit"], result["sensitivity"]
        margin = f"{a['minimum_margin']:.3f}" if a["minimum_margin"] is not None else "缺目标"
        lines.append(f"| {VARIANTS[key]['label']} | {len(result['rows'])} | {a['passed']} | {margin} | {common['passed']} | {sensitivity['passing']}/{sensitivity['total']} |")
    lines += ["", f"共同集合为 {common_count} 个固定配置，各方案在此集合重新拟合扩展加分。敏感性检查为在两个板块间转移 1 个百分点，共 20 种；固定成绩和校准，不代表未来数据刷新也保持排序。",
        "最小分差较小时，原始成绩的更新就可能改变结果；本轮未做跨时间留出验证。",
        "", "## 搜索范围与复现", "",
        f"检查 {search['core_combinations']} 套 Core，权重每板 10%–40%、5 个百分点步长、总和 100%。对满足至少 100 个模型且九个指定模型均入榜的组合，共评估 {search['evaluated_core_weight_combinations']} 次，{search['passing_combinations']} 次通过当前偏好。",
        "E/F/G 分别展示接近等权、覆盖更广、增加科学编程证据三种取舍；不是互相独立的验证集。完整通过列表在 search.json，输入哈希和校准在 run.json。",
        "运行：`python -B analysis/irt_leaderboard_exploration/preference_core_variants.py`。各版全量排名见 rankings_*.csv；共同人群排名见 common_*.csv；未入榜及缺项见 excluded_*.csv。",
        ""]
    (output / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def run(input_json, raw_csv, output):
    payload = json.loads(input_json.read_text(encoding="utf-8"))
    with raw_csv.open(encoding="utf-8-sig", newline="") as handle:
        models = base.representatives(base.load_models(payload, list(csv.DictReader(handle))))
    maps = base.fit_terminal_maps(models)
    search = search_candidates(models, maps)
    output.mkdir(parents=True, exist_ok=True)
    (output / "search.json").write_text(json.dumps(search, ensure_ascii=False, indent=2), encoding="utf-8")
    results, prepared = {}, {}
    for key, variant in VARIANTS.items():
        eligible, excluded = base.prepare(models, variant, maps)
        prepared[key] = eligible
        rows, calibration = base.score_variant(eligible, variant["core"])
        weighted = weighted_rows(rows, variant["weights"])
        results[key] = {"rows": weighted, "audit": constraint_audit(weighted), "calibration": calibration,
                        "sensitivity": weight_sensitivity(rows, variant["weights"])}
        base.scheme18.write_csv(output / f"rankings_{key}.csv", weighted)
        base.scheme18.write_csv(output / f"excluded_{key}.csv", excluded)
    common = set.intersection(*({m["slug"] for m in ms} for ms in prepared.values()))
    for key, ms in prepared.items():
        variant = VARIANTS[key]
        rows, calibration = base.score_variant([m for m in ms if m["slug"] in common], variant["core"])
        weighted = weighted_rows(rows, variant["weights"])
        results[key].update(common_audit=constraint_audit(weighted), common_calibration=calibration)
        base.scheme18.write_csv(output / f"common_{key}.csv", weighted)
    audit_rows = [{"variant": key, "population": scope, **check} for key, result in results.items()
                  for scope, audit in (("full", result["audit"]), ("common", result["common_audit"]))
                  for check in audit["checks"]]
    base.scheme18.write_csv(output / "constraints.csv", audit_rows)
    metadata = {
        "selection": "explicit user ranking preferences; no model-specific score terms",
        "input_sha256": {str(p.relative_to(base.ROOT) if p.is_relative_to(base.ROOT) else p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (input_json, raw_csv)},
        "targets": TARGETS, "variants": VARIANTS, "terminal_maps": maps, "common_population": len(common),
        "results": {key: {k: v for k, v in result.items() if k != "rows"} for key, result in results.items()},
    }
    (output / "run.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(output, results, len(common), search)
    return {key: {"population": len(result["rows"]), "audit": result["audit"],
                  "common_passed": result["common_audit"]["passed"],
                  "sensitivity_passed": result["sensitivity"]["passing"]} for key, result in results.items()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=base.ROOT / "docs/data/models.json")
    parser.add_argument("--raw-csv", type=Path, default=base.ROOT / "ArtificialAnalysis/artificialanalysis_raw_scores_wide.csv")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.raw_csv, args.output_dir), ensure_ascii=False, indent=2))
