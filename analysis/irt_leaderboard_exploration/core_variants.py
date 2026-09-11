"""Small, reproducible Core experiments; never changes production Scheme 18.

Use direct AA observations and exact-scoped external extensions. Select one
configuration per variantGroup BEFORE checking any candidate's Core. Keep the
five equal boards and Scheme 18's geometric Core / residual-only bonus, changing
only the declared Core registry and Terminal-Bench fallback. Missing v4 results
may use the SAME configuration's older result; an observed zero never falls back.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ArtificialAnalysis.scrape_artificial_analysis import SCORE_SPECS
from analysis.irt_leaderboard_exploration import aindex_scheme18 as scheme18
from analysis.irt_leaderboard_exploration.evidence_only_ranking_analysis import sanitize_models

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "outputs" / "core_variants"
TB = "Terminal-Bench effective"
LATEST_TB = "Terminal-Bench v4.0"
OLD_TB = ("Terminal-Bench v2.1", "Terminal-Bench Hard")
BOARD_LABELS = dict(zip(scheme18.BOARD_ORDER, (
    "编程", "Agent／工具工作", "高难推理", "知识／科学", "指令／上下文",
)))
COMMON_CORE = {
    "coding": (TB,),
    "hard-reasoning": ("Humanity's Last Exam", "GPQA Diamond"),
    "knowledge-science": ("GPQA Diamond", "AA-Omniscience Accuracy"),
    "instruction-context": ("AA-LCR v1.1",),
}
VARIANTS = {
    "a_broad": {
        "label": "A 广覆盖", "fallback": "discount",
        "core": {**COMMON_CORE, "agentic-tool-work": ("τ³-Banking",)},
    },
    "b_automation": {
        "label": "B 工作流", "fallback": "discount",
        "core": {**COMMON_CORE, "agentic-tool-work": ("AutomationBench-AA",)},
    },
    "c_documents": {
        "label": "C 工作流＋文档", "fallback": "discount",
        "core": {**COMMON_CORE, "agentic-tool-work": ("AutomationBench-AA",),
                 "instruction-context": ("AA-LCR v1.1", "GDP.pdf")},
    },
    "d_calibrated": {
        "label": "D 工作流＋版本换算", "fallback": "calibrated",
        "core": {**COMMON_CORE, "agentic-tool-work": ("AutomationBench-AA",)},
    },
}


def number(value):
    return scheme18.finite_number(value)


def load_models(payload, raw_rows):
    models, _ = sanitize_models(payload, exact_config_only=True)
    raw = {row["slug"]: row for row in raw_rows}
    keys = [spec.column for spec in SCORE_SPECS]
    for model in models:
        # Restore AA's actual observation, including LiveCodeBench: the site
        # may have filled that field with a fitted external-benchmark value.
        for key in keys:
            model["scores"][key] = number(raw.get(model["slug"], {}).get(key))
    return models


def representatives(models):
    selected = {}
    for model in sorted(models, key=lambda m: (-float(m.get("variantPriority") or 0), m["slug"])):
        selected.setdefault(model["variantGroup"], model)
    return list(selected.values())


def coverage_inventory(models):
    keys = sorted({key for m in models for key in m["scores"]})
    rows = []
    for key in keys:
        observed = [m for m in models if number(m["scores"].get(key)) is not None]
        if not observed:
            continue
        rows.append({
            "benchmark": key, "configurations": len(observed),
            "variant_groups": len({m["variantGroup"] for m in observed}),
            "creators": len({m["creator"] for m in observed}),
            "at_least_100_configurations": len(observed) >= 100,
            "at_least_100_groups": len({m["variantGroup"] for m in observed}) >= 100,
            "note": (
                "历史留存列，不作为新 Core" if key == "GDPval-AA" else
                "当前 AA-LCR v1.1 的兼容别名，不重复计权" if key == "AA-LCR" else
                "Elo 换算分，非原生通过率" if key in {"AA-Briefcase", "GDPval-AA v2"} else
                "同一 Omniscience 家族的另一指标" if key == "AA-Omniscience Non-Hallucination Rate" else
                "直接观测；外部项目仅计确切配置、非复制、非推算成绩"
            ),
        })
    return sorted(rows, key=lambda row: (-row["configurations"], row["benchmark"]))


def fit_terminal_maps(models):
    result = {}
    for key in OLD_TB:
        pairs = [(m["scores"].get(key), m["scores"].get(LATEST_TB)) for m in models]
        pairs = [(x, y) for x, y in pairs if number(x) is not None and number(y) is not None]
        if len(pairs) < 5:
            result[key] = {"pairs": len(pairs), "enabled": False}
            continue
        x, y = np.array(pairs, dtype=float).T
        variance = float(np.sum((x - x.mean()) ** 2))
        slope = max(0.0, float(np.sum((x-x.mean())*(y-y.mean()))) / variance) if variance > 1e-12 else 0.0
        intercept = float(y.mean() - slope * x.mean())
        predicted = np.clip(intercept + slope * x, 0, 100)
        result[key] = {
            "enabled": True, "pairs": len(pairs), "slope": slope, "intercept": intercept,
            "median_old": float(np.median(x)), "median_v4": float(np.median(y)),
            "median_gap": float(np.median(x-y)),
            "in_sample_mae": float(np.mean(np.abs(predicted-y))),
            "fraction_discounted_old_above_observed_v4": float(np.mean(x * (0.95 if key == OLD_TB[0] else 0.90) > y)),
        }
    return result


def terminal_score(scores, mode, maps):
    latest = number(scores.get(LATEST_TB))
    if latest is not None:
        return latest, LATEST_TB, latest
    if mode == "v4_only":
        return None, "missing", None
    for key, factor in zip(OLD_TB, (0.95, 0.90)):
        raw = number(scores.get(key))
        if raw is None:
            continue
        value = raw
        if mode == "calibrated":
            fit = maps[key]
            if not fit["enabled"]:
                continue
            value = float(np.clip(fit["intercept"] + fit["slope"] * raw, 0, 100))
        return factor * value, key, raw
    return None, "missing", None


def prepare(models, variant, maps):
    eligible, excluded = [], []
    for source in models:
        model = {**source, "scores": dict(source["scores"])}
        effective, origin, raw = terminal_score(model["scores"], variant["fallback"], maps)
        model["scores"][TB] = effective
        model["terminal_source"], model["terminal_raw"] = origin, raw
        missing = sorted({key for keys in variant["core"].values() for key in keys
                          if number(model["scores"].get(key)) is None})
        if missing:
            excluded.append({"slug": model["slug"], "missing_core": "; ".join(missing)})
        else:
            eligible.append(model)
    return eligible, excluded


def extension_registry(core):
    core_keys = {key for keys in core.values() for key in keys}
    # Terminal versions represent ONE Core slot; do not also award an old
    # Terminal result as an extension on this or any other board.
    excluded = core_keys | ({LATEST_TB, *OLD_TB} if TB in core_keys else set())
    if "AA-LCR v1.1" in core_keys:
        excluded.add("AA-LCR")
    return {board: tuple(k for k in keys if k not in excluded)
            for board, keys in scheme18.EXTENSION_ITEMS.items()}


def score_variant(models, core):
    if not models:
        return [], {"cap": 0, "population": 0, "extensions": {}}
    bases, residuals, trends = {}, {}, {}
    extensions = extension_registry(core)
    for board in scheme18.BOARD_ORDER:
        bases[board] = scheme18.geometric_core_score(scheme18.score_matrix(models, core[board]))
        values = scheme18.score_matrix(models, extensions[board])
        residuals[board], trends[board] = scheme18._fit_positive_residuals(bases[board], values)
    positive = [x for values in residuals.values() for x in values.flat if np.isfinite(x) and x > 0]
    cap = scheme18.derive_cap(residuals) if positive else 0.0
    bonuses = {b: scheme18.extension_bonus(residuals[b], cap) for b in scheme18.BOARD_ORDER}
    rows = []
    for i, model in enumerate(models):
        row = {"slug": model["slug"], "model": model["model"], "variant_group": model["variantGroup"],
               "terminal_source": model["terminal_source"], "terminal_raw": model["terminal_raw"],
               "terminal_effective": model["scores"][TB]}
        total, core_total = 0.0, 0.0
        for board in scheme18.BOARD_ORDER:
            base, bonus = float(bases[board][i]), float(bonuses[board][i])
            score = min(100.0, base + bonus)
            row.update({board + "_core": base, board + "_bonus": bonus, board + "_score": score})
            total += score / 5
            core_total += base / 5
        row.update(score=total, core_only_score=core_total)
        rows.append(row)
    rows.sort(key=lambda row: (-row["score"], row["slug"]))
    for rank, row in enumerate(rows, 1):
        row["rank"] = rank
    return rows, {"cap": cap, "population": len(models), "extensions": extensions, "trends": trends}


def write_report(output, inventory, results, maps, common_count):
    lines = ["# Core 候选方案实跑", "",
        "这是可重跑的实验，生产榜仍为 Scheme 18。分数保留五板块各 20%、几何 Core 和正残差加分。",
        "去重先固定每组 variantPriority 最高的配置，同优先级按 slug 排序；不按成绩选配置、不跨配置补值。",
        "所有声明的 Core 必须完整。表中配置数和模型组数不同；至少 100 条不代表适合做 Core。", "",
        "## 覆盖至少 100 个配置的全部测试", "",
        "| 测试 | 配置数 | 模型组数 | 厂商数 | 说明 |", "|---|---:|---:|---:|---|"]
    for r in inventory:
        if r["at_least_100_configurations"]:
            lines.append(f"| {r['benchmark']} | {r['configurations']} | {r['variant_groups']} | {r['creators']} | {r['note']} |")
    lines += ["", "LiveCodeBench 使用 CSV 的直接成绩，剔除网站后来拟合补入的值。外部测试按确切配置证据统计，本次无外部测试达到 100 条。",
              "", "## Core 方案", "", "| 板块 | A 广覆盖 | B 工作流 | C 工作流＋文档 | D 版本换算 |", "|---|---|---|---|---|"]
    for board in scheme18.BOARD_ORDER:
        lines.append("| " + BOARD_LABELS[board] + " | " + " | ".join(", ".join(v["core"][board]) for v in VARIANTS.values()) + " |")
    lines += ["", "A/B/C：有 v4.0 就用 v4.0；否则 v2.1 × 0.95；再没有则 Hard × 0.90。扣的是比例，不是百分点。实测 0 分保留，不回退。",
        "D：Core 与 B 完全相同；旧版通过去重重叠样本的非负斜率线性拟合换算到 v4 尺度，限制在 0–100 后再打相同折扣。此值是估算，不是 v4 实测。",
        "扩展池沿用 Scheme 18，但移除已经成为 Core 的项目，以及所有 Terminal-Bench 版本，防止 Core 与加分重复计入。",
        "GPQA 同时支持推理与知识两个板块；这一跨板块重复仍保留。新 Core 不再强制 SciCode/CritPt；IFBench 暂不强制，因为一些最新模型没有结果。",
        "AA-Briefcase、GDPval 是 Elo 换算分，本轮不放入几何通过率 Core。", "",
        "## 版本差异诊断", "", "以下拟合每个模型组最多一条，取预先固定配置；误差为样本内描述，不是泛化验证。", "",
        "| 旧版 | 重叠模型组 | 旧版中位数 | v4 中位数 | 配对分差中位数 | 九五／九折后仍高于实测 v4 | 换算 MAE |", "|---|---:|---:|---:|---:|---:|---:|"]
    for key, fit in maps.items():
        if fit["enabled"]:
            lines.append(f"| {key} | {fit['pairs']} | {fit['median_old']:.2f} | {fit['median_v4']:.2f} | {fit['median_gap']:.2f} | {fit['fraction_discounted_old_above_observed_v4']:.1%} | {fit['in_sample_mae']:.2f} |")
    lines += ["", "轻折扣不能消除旧版较容易的影响；v4 实测低分的模型可能落后于只测旧版的模型。A/B/C 用来检验这一提议，D 提供粗略尺度修正对照。",
        "不同方案的覆盖人群与加分校准都会变化；common_* 文件另外在完全相同的配置集合上分别重算，以减少人群差异。",
        f"共同集合：{common_count} 个模型组。", "", "## 实跑结果", "",
        "| 方案 | 入榜模型组 | 被排除模型组 | v4 实测 | v2.1 回退 | Hard 回退 | 每板加分上限 |", "|---|---:|---:|---:|---:|---:|---:|"]
    for key, result in results.items():
        counts = Counter(r["terminal_source"] for r in result["rows"])
        lines.append(f"| {VARIANTS[key]['label']} | {len(result['rows'])} | {len(result['excluded'])} | {counts[LATEST_TB]} | {counts[OLD_TB[0]]} | {counts[OLD_TB[1]]} | {result['calibration']['cap']:.3f} |")
    for key, result in results.items():
        lines += ["", "### " + VARIANTS[key]["label"] + " · 前十", "",
                  "| 排名 | 模型 | AIndex 候选分 | Core 平均 | Terminal 来源 | 有效 Terminal 分 |", "|---:|---|---:|---:|---|---:|"]
        for row in result["rows"][:10]:
            lines.append(f"| {row['rank']} | {row['model']} | {row['score']:.3f} | {row['core_only_score']:.3f} | {row['terminal_source']} | {row['terminal_effective']:.3f} |")
    lines += ["", "完整数据：coverage.csv、各方案 rankings_*.csv、excluded_*.csv、共同人群 common_*.csv，以及 comparison.csv。",
              "参数、输入 SHA-256 和校准系数见 run.json。所有原始成绩文件保持不变。", ""]
    (output / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def run(input_json, input_csv, output):
    payload = json.loads(input_json.read_text(encoding="utf-8"))
    with input_csv.open(encoding="utf-8-sig", newline="") as handle:
        models = load_models(payload, list(csv.DictReader(handle)))
    selected = representatives(models)
    inventory = coverage_inventory(models)
    maps = fit_terminal_maps(selected)
    output.mkdir(parents=True, exist_ok=True)
    scheme18.write_csv(output / "coverage.csv", inventory)
    results, prepared = {}, {}
    for key, variant in VARIANTS.items():
        eligible, excluded = prepare(selected, variant, maps)
        rows, calibration = score_variant(eligible, variant["core"])
        prepared[key] = eligible
        results[key] = {"rows": rows, "excluded": excluded, "calibration": calibration}
        scheme18.write_csv(output / f"rankings_{key}.csv", rows)
        scheme18.write_csv(output / f"excluded_{key}.csv", excluded)
    common = set.intersection(*({m["slug"] for m in ms} for ms in prepared.values()))
    common_calibrations = {}
    for key, ms in prepared.items():
        rows, calibration = score_variant([m for m in ms if m["slug"] in common], VARIANTS[key]["core"])
        scheme18.write_csv(output / f"common_{key}.csv", rows)
        common_calibrations[key] = calibration
    lookup = {key: {r["slug"]: r for r in value["rows"]} for key, value in results.items()}
    comparison = []
    for model in selected:
        row = {"model": model["model"], "slug": model["slug"], "variant_group": model["variantGroup"]}
        for key, values in lookup.items():
            result = values.get(model["slug"], {})
            row.update({key + "_rank": result.get("rank", ""), key + "_score": result.get("score", "")})
        comparison.append(row)
    scheme18.write_csv(output / "comparison.csv", comparison)
    metadata = {
        "input_sha256": {str(p.relative_to(ROOT) if p.is_relative_to(ROOT) else p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (input_json, input_csv)},
        "models": len(models), "representatives": len(selected), "common_population": len(common),
        "variants": VARIANTS, "fallback_factors": dict(zip(OLD_TB, (0.95, 0.90))),
        "terminal_maps": maps, "calibrations": {k: v["calibration"] for k, v in results.items()},
        "common_calibrations": common_calibrations,
    }
    (output / "run.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(output, inventory, results, maps, len(common))
    return {key: {"models": len(v["rows"]), "top3": [(r["model"], round(r["score"], 3)) for r in v["rows"][:3]]} for key, v in results.items()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "docs/data/models.json")
    parser.add_argument("--raw-csv", type=Path, default=ROOT / "ArtificialAnalysis/artificialanalysis_raw_scores_wide.csv")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.raw_csv, args.output_dir), ensure_ascii=False, indent=2))
