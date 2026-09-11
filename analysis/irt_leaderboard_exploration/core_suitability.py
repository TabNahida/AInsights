"""Reproducible benchmark coverage/score audit, independent of ranking weights."""
from __future__ import annotations

import csv
from datetime import datetime, timedelta
import json
from pathlib import Path

import numpy as np

from analysis.irt_leaderboard_exploration import core_variants as base


RECENT_DAYS = 180
DEFAULT_PROHIBITED = {
    "AIME": "AIME 竞赛题家族全部年度及别名禁止进入 Core；不以换年度恢复准入。",
    "LiveCodeBench": "本轮不进入 Core：冻结数据的匿名近期群体没有直接观测，历史总覆盖不能替代近期覆盖。",
    "GPQA Diamond": "本轮保守选择不进入 Core：关注配置分数集中于高分区，分数分布保留作审计；不能据此认定刷分或污染。",
}


def _date(value):
    return datetime.fromisoformat(str(value).strip().replace("Z", "+00:00")).date()


def _statistics(models, key):
    values = [base.number(model.get("scores", {}).get(key)) for model in models]
    values = [value for value in values if value is not None]
    return {
        "population": len(models),
        "observed": len(values),
        "coverage_percent": 100 * len(values) / len(models) if models else None,
        "median": float(np.median(values)) if values else None,
        "p90": float(np.percentile(values, 90)) if values else None,
        "at_least_90": sum(value >= 90 for value in values),
    }


def _quality_note(key):
    if key in base.OLD_TB:
        return "旧 Terminal 版本：本轮禁止作 Core、回退或扩展。"
    if key == base.TB:
        return "Terminal 兼容槽位；不是独立新测试，不作为新 Core。"
    if key == "AA-LCR":
        return "LCR 兼容别名，不与 v1.1 重复计权。"
    if key == "GDPval-AA":
        return "GDPval 历史留存列，不作为新 Core。"
    if key in {"AA-Briefcase", "GDPval-AA v2"}:
        return "Elo 换算分，非原生通过率；数值分布不能解释为答题正确率。"
    if key == "AA-Omniscience Non-Hallucination Rate":
        return "与 Omniscience Accuracy 属于同一测试家族，不重复占 Core 槽位。"
    if key == "MMMU-Pro":
        return "多模态测试；需区分能力适用性与缺测，缺测不能证明低能力。"
    return "直接观测；覆盖和高分集中仅供质量审计，不自动产生额外准入门槛。"


def profile(payload, all_models, selected, targets):
    """Audit >=100-configuration items on fixed representatives and date cohorts.

    Release dates use calendar-day resolution. The recent interval includes both
    snapshot_date - 180 days and snapshot_date. Missing/invalid/future dates are
    recorded and excluded only from the recent diagnostic cohort, not rankings.
    """
    try:
        snapshot = _date(payload["generatedAt"])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("Coverage audit requires a valid generatedAt snapshot date") from error
    start = snapshot - timedelta(days=RECENT_DAYS)
    selected, all_models = list(selected), list(all_models)
    target_slugs = tuple(dict.fromkeys(targets))
    selected_by_slug = {model["slug"]: model for model in selected}
    target_models = [selected_by_slug[slug] for slug in target_slugs if slug in selected_by_slug]
    recent, anomalies = [], []
    for model in selected:
        raw = model.get("releaseDate")
        reason = None
        if raw is None or str(raw).strip() == "":
            reason = "missing_release_date"
        else:
            try:
                released = _date(raw)
            except (TypeError, ValueError):
                reason = "invalid_release_date"
            else:
                if released > snapshot:
                    reason = "release_after_snapshot"
                elif released >= start:
                    recent.append(model)
        if reason:
            anomalies.append({"slug": model["slug"], "releaseDate": raw, "reason": reason})
    rows = []
    for inventory in base.coverage_inventory(all_models):
        if inventory["configurations"] < 100:
            continue
        key = inventory["benchmark"]
        rows.append({
            **inventory,
            "representatives": _statistics(selected, key),
            "recent": _statistics(recent, key),
            "targets": _statistics(target_models, key),
            "target_missing_slugs": [model["slug"] for model in target_models
                                     if base.number(model["scores"].get(key)) is None],
            "quality_note": _quality_note(key),
        })
    return {
        "generatedAt": payload["generatedAt"],
        "configurations": len(all_models),
        "fixed_representatives": len(selected),
        "recent_days": RECENT_DAYS,
        "recent_start": str(start),
        "recent_end": str(snapshot),
        "recent_interval": "calendar dates; both endpoints inclusive",
        "recent_population": len(recent),
        "target_slugs": list(target_slugs),
        "target_population": len(target_models),
        "target_slugs_absent_from_representatives": [slug for slug in target_slugs if slug not in selected_by_slug],
        "release_date_anomalies": anomalies,
        "inventory_minimum_configurations": 100,
        "rows": rows,
    }


def _prohibition(key, reasons):
    if "aime" in key.lower():
        return reasons.get(key, reasons.get("AIME", DEFAULT_PROHIBITED["AIME"]))
    return reasons.get(key, "")


def _number(value):
    return "—" if value is None else f"{value:.2f}"


def write_report(output, profile, prohibited=None):
    """Write auditable Markdown/JSON/CSV without creating or changing rankings."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    reasons = {**DEFAULT_PROHIBITED, **(prohibited or {})}
    rows = [{**row, "core_prohibition": _prohibition(row["benchmark"], reasons)} for row in profile["rows"]]
    result = {**profile, "core_prohibited_reasons": reasons, "rows": rows}
    (output / "core_quality.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    fields = ["benchmark", "configurations", "variant_groups", "creators",
              "at_least_100_configurations", "at_least_100_groups"]
    metrics = ("population", "observed", "coverage_percent", "median", "p90", "at_least_90")
    fields += [f"{cohort}_{metric}" for cohort in ("representatives", "recent", "targets") for metric in metrics]
    fields += ["target_missing_slugs", "quality_note", "core_prohibition"]
    with (output / "core_quality.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            flat = {key: row[key] for key in fields if key in row}
            flat["target_missing_slugs"] = "; ".join(row["target_missing_slugs"])
            flat.update({f"{cohort}_{metric}": row[cohort][metric]
                         for cohort in ("representatives", "recent", "targets") for metric in metrics})
            writer.writerow(flat)
    lines = [
        "# Core 测试质量与覆盖审计", "",
        f"冻结时间：`{profile['generatedAt']}`。共 {profile['configurations']} 个配置、"
        f"{profile['fixed_representatives']} 个预先固定代表。仅列出至少 100 个配置有实测的项目，"
        "配置数、去重模型组数和固定代表覆盖分别统计，不将它们混为模型数量。", "",
        f"匿名近期群体按发布日期选取，使用日历日期闭区间 **{profile['recent_start']} 至 "
        f"{profile['recent_end']}**（快照日期向前 {profile['recent_days']} 天，含两端），"
        f"共 **{profile['recent_population']}** 个固定代表；"
        f"另外展示 {profile['target_population']} 个关注配置作为诊断对照。"
        "关注名单不单独决定 Core 资格；缺测率、高分分布不直接改变计分或剔除规则。", "",
        "本轮禁止 AIME 全部年度及别名进入 Core；LiveCodeBench 因当前匿名近期覆盖为零移出 Core。"
        "GPQA 按本轮保守选择移出 Core：关注配置分数集中于高分区。"
        "高分集中、测试形式或缺测不能证明模型刷分、训练污染或测试泄漏。"
        "HLE、MMMU 等也不能仅凭名称归入已证实污染的测试。", "",
        "Terminal 只允许 v4 实测；旧版和兼容别名仅供审计，不作为新 Core。"
        "其他项目的局限是质量说明，不任意增加覆盖百分比或高分阈值门槛。", "",
        "## 覆盖", "",
        "| 测试 | 配置 | 去重组 | 固定代表实测 | 近期实测／人数 | 近期覆盖 | 关注实测／人数 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        recent, target = row["recent"], row["targets"]
        lines.append(f"| {row['benchmark']} | {row['configurations']} | {row['variant_groups']} | "
                     f"{row['representatives']['observed']} | {recent['observed']}/{recent['population']} | "
                     f"{_number(recent['coverage_percent'])}% | {target['observed']}/{target['population']} |")
    lines += ["", "## 实测分数分布", "",
              "各格为 **中位数／P90／≥90 数量**，只在该群体有实测的模型上计算；真实零分有效，"
              "缺测不作为零分参与分布。≥90 是透明的描述性统计，不能直接判断饱和，更不是污染检测。"
              "Elo 换算列的 90 不代表 90% 正确率。", "",
              "| 测试 | 固定代表 | 匿名近期群体 | 关注配置 |",
              "|---|---:|---:|---:|"]
    for row in rows:
        cells = [f"{_number(row[cohort]['median'])}／{_number(row[cohort]['p90'])}／"
                 f"{row[cohort]['at_least_90']}/{row[cohort]['observed']}"
                 for cohort in ("representatives", "recent", "targets")]
        lines.append(f"| {row['benchmark']} | " + " | ".join(cells) + " |")
    lines += ["", "## 项目局限与本轮政策", "", "| 测试 | 说明 |", "|---|---|"]
    lines += [f"| {row['benchmark']} | {row['core_prohibition'] or row['quality_note']} |" for row in rows]
    lines += ["", "## 日期与关注配置异常", ""]
    if profile["release_date_anomalies"]:
        lines += ["异常日期只从近期诊断群体排除，不从排名人口剔除。", "",
                  "| 配置 | 原始日期 | 原因 |", "|---|---|---|"]
        lines += [f"| {row['slug']} | {str(row['releaseDate']).replace('|', '/')} | {row['reason']} |"
                  for row in profile["release_date_anomalies"]]
    else:
        lines.append("固定代表均有有效发布日期，未发现晚于快照的发布日期。")
    absent = profile["target_slugs_absent_from_representatives"]
    lines += ["", "关注名单未找到固定代表：" + ("；".join(absent) if absent else "无。"), "",
              "逐项关注配置缺测名单见 `core_quality.json` / `core_quality.csv`。"
              "本审计不生成排行榜、不插补成绩，也不证明通过指定模型顺序即可得到有效的全榜。", ""]
    (output / "CORE_QUALITY.md").write_text("\n".join(lines), encoding="utf-8")
    return result
