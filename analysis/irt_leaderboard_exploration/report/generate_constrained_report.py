"""Build the product-constrained ranking report artifact."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


REPORT_DIR = Path(__file__).resolve().parent
ANALYSIS_DIR = REPORT_DIR.parent
OUTPUT_DIR = ANALYSIS_DIR / "outputs"

SCHEME_ORDER = [
    "guarded_aindex",
    "guarded_rasch",
    "guarded_twopl",
    "guarded_robust",
    "guarded_borda",
]
SCHEME_SHORT = {
    "guarded_aindex": "覆盖校正 AIndex",
    "guarded_rasch": "约束 1PL/Rasch",
    "guarded_twopl": "约束 2PL",
    "guarded_robust": "约束稳健秩",
    "guarded_borda": "约束 Borda",
}
TARGET_MODELS = [
    "Claude Fable 5 (with fallback)",
    "Qwen3.8 Max",
    "Qwen3.7 Max",
    "Qwen3.7 Plus",
    "Qwen3.6 Max Preview",
    "Qwen3.6 Plus",
    "Gemini 3.6 Flash",
    "Gemini 3.5 Flash",
]


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def integer(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return int(float(value))


def number(value: Any) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def local_snapshot_label(value: str) -> str:
    moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    china = moment.astimezone(timezone(timedelta(hours=8)))
    return china.strftime("%Y-%m-%d %H:%M（北京时间）")


def source(
    source_id: str,
    label: str,
    path: str,
    description: str,
    command: str,
    *,
    metric_definitions: list[str] | None = None,
) -> dict[str, Any]:
    if path.lower().endswith(".csv"):
        sql = f"SELECT * FROM read_csv_auto('{path}', header = true)"
    elif path.lower().endswith(".json"):
        sql = f"SELECT * FROM read_json_auto('{path}')"
    else:
        sql = None
    return {
        "id": source_id,
        "label": label,
        "path": path,
        "query": {
            "language": "python/file",
            **({"sql": sql} if sql else {}),
            "query": command,
            "description": description,
            "tables_used": [path],
            "metric_definitions": metric_definitions or [],
        },
    }


def main() -> None:
    summary = json.loads(
        (OUTPUT_DIR / "constrained_validation_summary.json").read_text(
            encoding="utf-8"
        )
    )
    measurement_summary = json.loads(
        (OUTPUT_DIR / "validation_summary.json").read_text(encoding="utf-8")
    )
    top50_raw = load_csv(OUTPUT_DIR / "top50_constrained_schemes.csv")
    full_raw = load_csv(OUTPUT_DIR / "full_rankings_constrained_schemes.csv")
    diagnostics_raw = load_csv(OUTPUT_DIR / "constrained_scheme_diagnostics.csv")
    sensitivity_raw = load_csv(OUTPUT_DIR / "constraint_sensitivity.csv")
    source_assessment_raw = load_csv(OUTPUT_DIR / "external_source_assessment.csv")

    snapshot_label = local_snapshot_label(summary["data_generated_at"])
    generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    diagnostics_by_scheme = {row["scheme_id"]: row for row in diagnostics_raw}

    diagnostic_rows = []
    for scheme_id in SCHEME_ORDER:
        row = diagnostics_by_scheme[scheme_id]
        diagnostic_rows.append(
            {
                "scheme_id": scheme_id,
                "scheme_display": SCHEME_SHORT[scheme_id],
                "ranked_models": integer(row["ranked_models"]),
                "main_evidence_models": integer(row["main_evidence_models"]),
                "fable_rank": integer(row["fable_rank"]),
                "qwen_violations_before": integer(
                    row["qwen_direct_edge_violations_before"]
                ),
                "qwen_violations_after": integer(
                    row["qwen_direct_edge_violations_after"]
                ),
                "flash_open_above": integer(
                    row["gemini_flash_min_main_open_models_above"]
                ),
                "gemini_3_5_rank": integer(row["gemini_3_5_flash_rank"]),
                "gemini_3_6_rank": integer(row["gemini_3_6_flash_rank"]),
                "qwen_3_8_rank": integer(row["qwen_3_8_max_rank"]),
                "qwen_3_7_max_rank": integer(row["qwen_3_7_max_rank"]),
                "qwen_3_7_plus_rank": integer(row["qwen_3_7_plus_rank"]),
                "qwen_3_6_plus_rank": integer(row["qwen_3_6_plus_rank"]),
                "spearman": number(
                    row["spearman_vs_unconstrained_after_coverage"]
                ),
                "top50_overlap": integer(
                    row["top50_overlap_with_unconstrained_after_coverage"]
                ),
                "max_shift": integer(row["max_absolute_constraint_shift"]),
                "top50_provisional": integer(row["top50_provisional_models"]),
                "top50_median_unique": number(
                    row["top50_median_unique_families"]
                ),
            }
        )

    target_rank_rows: list[dict[str, Any]] = []
    rank_fields = {
        "Claude Fable 5": "fable_rank",
        "Qwen3.8 Max": "qwen_3_8_rank",
        "Qwen3.7 Max": "qwen_3_7_max_rank",
        "Qwen3.7 Plus": "qwen_3_7_plus_rank",
        "Qwen3.6 Plus": "qwen_3_6_plus_rank",
        "Gemini 3.6 Flash": "gemini_3_6_rank",
        "Gemini 3.5 Flash": "gemini_3_5_rank",
    }
    for row in diagnostic_rows:
        for model, field in rank_fields.items():
            target_rank_rows.append(
                {
                    "scheme_id": row["scheme_id"],
                    "scheme_display": row["scheme_display"],
                    "model": model,
                    "rank": row[field],
                }
            )

    first_scheme_rows = {
        row["model"]: row
        for row in full_raw
        if row["scheme_id"] == "guarded_aindex"
    }
    target_coverage_rows: list[dict[str, Any]] = []
    target_coverage_table: list[dict[str, Any]] = []
    for model in TARGET_MODELS:
        row = first_scheme_rows[model]
        compact_name = model.replace(" (with fallback)", "")
        slots = integer(row["board_test_slots_total"])
        unique = integer(row["unique_benchmark_families"])
        target_coverage_rows.extend(
            [
                {"model": compact_name, "measure": "板块测试槽位", "count": slots},
                {"model": compact_name, "measure": "唯一测试家族", "count": unique},
            ]
        )
        target_coverage_table.append(
            {
                "model": compact_name,
                "evidence_tier": row["evidence_tier"],
                "board_slots": slots,
                "unique_families": unique,
                "min_board_tests": integer(row["min_board_tests"]),
                "boards_below_3": integer(row["boards_below_3"]),
                "coverage_penalty_z": number(row["coverage_penalty_z"]),
            }
        )

    sensitivity_rows = [
        {
            "scheme_display": SCHEME_SHORT[row["scheme_id"]],
            "flash_open_floor": integer(row["flash_open_floor"]),
            "gemini_3_5_rank": integer(row["gemini_3_5_flash_rank"]),
            "gemini_3_6_rank": integer(row["gemini_3_6_flash_rank"]),
            "min_open_above": integer(
                row["gemini_flash_min_main_open_models_above"]
            ),
            "spearman": number(row["spearman_vs_unconstrained"]),
            "top50_overlap": integer(row["top50_overlap_with_unconstrained"]),
            "max_shift": integer(row["max_absolute_shift"]),
        }
        for row in sensitivity_raw
    ]

    source_assessment_rows = [
        {
            "source": row["source"],
            "authority": row["authority"],
            "freshness": row["observed_freshness"],
            "license": row["license_reuse_status"],
            "mapping_risk": row["model_mapping_risk"],
            "recommendation": row["recommendation"],
            "endpoint": row["machine_readable_endpoint"],
        }
        for row in source_assessment_raw
    ]

    top50_datasets: dict[str, list[dict[str, Any]]] = {}
    top3_lines: list[str] = []
    for scheme_id in SCHEME_ORDER:
        rows = [row for row in top50_raw if row["scheme_id"] == scheme_id]
        typed = [
            {
                "rank": integer(row["rank"]),
                "model": row["model"],
                "creator": row["creator"],
                "evidence_tier": row["evidence_tier"],
                "measurement_score": number(row["measurement_score"]),
                "raw_method_rank": integer(row["raw_method_rank"]),
                "coverage_penalty_z": number(row["coverage_penalty_z"]),
                "constraint_shift": integer(row["rank_change_due_to_constraints"]),
                "total_shift": integer(row["rank_change_vs_raw_method"]),
                "unique_families": integer(row["unique_benchmark_families"]),
                "min_board_tests": integer(row["min_board_tests"]),
                "constraint_flags": row["constraint_flags"] or "—",
            }
            for row in rows
        ]
        top50_datasets[f"top50_{scheme_id}"] = typed
        top3_lines.append(
            f"- **{SCHEME_SHORT[scheme_id]}**："
            + "、".join(row["model"] for row in typed[:3])
        )

    current_fable_score = next(
        row["measurement_score"]
        for row in top50_datasets["top50_guarded_aindex"]
        if row["model"] == "Claude Fable 5 (with fallback)"
    )
    minimum_spearman = min(row["spearman"] for row in diagnostic_rows)
    maximum_spearman = max(row["spearman"] for row in diagnostic_rows)
    minimum_top50_overlap = min(row["top50_overlap"] for row in diagnostic_rows)
    maximum_top50_overlap = max(row["top50_overlap"] for row in diagnostic_rows)

    sources = [
        source(
            "src_models",
            "生产模型与 benchmark 快照",
            "docs/data/models.json",
            "修复第一方来源优先级后重建的生产模型、指标和外部 benchmark 快照。",
            "python -B scripts/build_docs_site.py",
        ),
        source(
            "src_benchmarks",
            "外部 benchmark 原始来源记录",
            "data/benchmarks/benchmark_scores.json",
            "包含第一方发布与其他厂商 comparator 列，供冲突和来源优先级审计。",
            "python -B benchmarks/collect_benchmark_scores.py",
        ),
        source(
            "src_measurement",
            "覆盖感知测量层",
            "analysis/irt_leaderboard_exploration/irt_leaderboard_analysis.py",
            "构建五板块响应矩阵并拟合 AIndex、1PL、2PL、稳健秩和 Borda 测量分。",
            "python -B analysis/irt_leaderboard_exploration/irt_leaderboard_analysis.py",
        ),
        source(
            "src_constraints",
            "产品约束与覆盖校正实现",
            "analysis/irt_leaderboard_exploration/constrained_ranking_analysis.py",
            "把独立测试家族覆盖惩罚与 Fable、Qwen、Gemini Flash 产品规则作为单独重排层。",
            "python -B analysis/irt_leaderboard_exploration/constrained_ranking_analysis.py",
            metric_definitions=[
                "Main evidence：每个板块至少 3 项且至少 9 个唯一 benchmark family。",
                "软覆盖目标：12 个唯一 benchmark family，每少 1 个扣 0.08 个榜内标准差。",
                "Gemini Flash：至少 15 个 Main-evidence 开源模型排在其前。",
                "Qwen：只约束明确列出的同产品线相邻版本和同版本 tier 边。",
            ],
        ),
        source(
            "src_constrained_validation",
            "受约束榜验证摘要",
            "analysis/irt_leaderboard_exploration/outputs/constrained_validation_summary.json",
            "五套方案的锚点、Qwen 违反数、Gemini Flash 开源模型下限和验收结果。",
            "python -B analysis/irt_leaderboard_exploration/constrained_ranking_analysis.py",
        ),
        source(
            "src_constrained_diagnostics",
            "受约束方案诊断",
            "analysis/irt_leaderboard_exploration/outputs/constrained_scheme_diagnostics.csv",
            "各方案约束前后违反数、目标模型名次、相关性、Top 50 重合和最大位移。",
            "python -B analysis/irt_leaderboard_exploration/constrained_ranking_analysis.py",
        ),
        source(
            "src_constrained_full",
            "受约束完整榜单",
            "analysis/irt_leaderboard_exploration/outputs/full_rankings_constrained_schemes.csv",
            "五套方案全部可排名模型，包含测量分、覆盖惩罚、约束前后名次和证据层级。",
            "python -B analysis/irt_leaderboard_exploration/constrained_ranking_analysis.py",
        ),
        source(
            "src_constrained_top50",
            "五套受约束方案 Top 50",
            "analysis/irt_leaderboard_exploration/outputs/top50_constrained_schemes.csv",
            "每套方案各 50 行，保留原始测量名次和产品约束位移。",
            "python -B analysis/irt_leaderboard_exploration/constrained_ranking_analysis.py",
        ),
        source(
            "src_sensitivity",
            "Gemini Flash 开源下限敏感性",
            "analysis/irt_leaderboard_exploration/outputs/constraint_sensitivity.csv",
            "比较 5、10、15 个 Main-evidence 开源模型下限对名次和整体连续性的影响。",
            "python -B analysis/irt_leaderboard_exploration/constrained_ranking_analysis.py",
        ),
        source(
            "src_external_sources",
            "自动更新外部源评估",
            "analysis/irt_leaderboard_exploration/outputs/external_source_assessment.csv",
            "对 LiveBench、Aider、SWE-bench、LMArena 等的接口、时效、许可和模型映射风险审计。",
            "manual endpoint and license audit; see assessment rows",
        ),
    ]

    charts = [
        {
            "id": "target_ranks",
            "title": "重点模型在五套受约束方案中的名次",
            "subtitle": "名次数值越小越靠前；Fable 固定第一，Qwen 与 Gemini 使用显式产品规则。",
            "showDescription": True,
            "intent": "comparison",
            "question": "产品规则在不同测量方法下给出怎样的重点模型次序？",
            "rationale": "折线显示方法变化与硬约束共同作用后的名次范围。",
            "type": "line",
            "dataset": "target_ranks",
            "sourceId": "src_constrained_diagnostics",
            "encodings": {
                "x": {"field": "scheme_display", "type": "nominal", "label": "方案"},
                "y": {"field": "rank", "type": "quantitative", "format": "number", "label": "名次（越小越好）"},
                "color": {"field": "model", "type": "nominal", "label": "模型"},
                "tooltip": [
                    {"field": "model", "type": "nominal", "label": "模型"},
                    {"field": "rank", "type": "quantitative", "label": "名次"},
                ],
            },
            "valueFormat": "number",
            "yAxisTitle": "名次（越小越好）",
            "layout": "full",
            "settings": {"sort": "none", "showValues": True},
            "surface": {"viewMode": "visualization", "showControls": False},
        },
        {
            "id": "target_coverage",
            "title": "重点模型的板块槽位与唯一测试家族",
            "subtitle": "跨板块复用会让槽位数高于真正独立的 benchmark family 数。",
            "showDescription": True,
            "intent": "comparison",
            "question": "哪些重点模型的表面覆盖高于独立证据广度？",
            "rationale": "并列柱直接显示同一模型的槽位数与去重后证据量差距。",
            "type": "bar",
            "dataset": "target_coverage",
            "sourceId": "src_constrained_full",
            "encodings": {
                "x": {"field": "model", "type": "nominal", "label": "模型"},
                "y": {"field": "count", "type": "quantitative", "format": "number", "label": "测试数"},
                "color": {"field": "measure", "type": "nominal", "label": "覆盖口径"},
                "tooltip": [
                    {"field": "measure", "type": "nominal", "label": "覆盖口径"},
                    {"field": "count", "type": "quantitative", "label": "数量"},
                ],
            },
            "valueFormat": "number",
            "yAxisTitle": "测试数",
            "layout": "full",
            "settings": {"groupMode": "grouped", "sort": "none", "showValues": True},
            "surface": {"viewMode": "visualization", "showControls": False},
        },
    ]

    tables = [
        {
            "id": "scheme_diagnostics",
            "title": "五套方案的约束验收与连续性",
            "subtitle": "约束位移与原始测量分并列保留；最大位移用于触发人工复核。",
            "showDescription": True,
            "dataset": "scheme_diagnostics",
            "defaultSort": {"field": "scheme_display", "direction": "asc"},
            "density": "dense",
            "sourceId": "src_constrained_diagnostics",
            "layout": "full",
            "columns": [
                {"field": "scheme_display", "label": "方案", "type": "text"},
                {"field": "fable_rank", "label": "Fable 名次", "format": "number"},
                {"field": "qwen_violations_before", "label": "Qwen 调整前违反", "format": "number"},
                {"field": "qwen_violations_after", "label": "Qwen 调整后违反", "format": "number"},
                {"field": "flash_open_above", "label": "Flash 前 Main 开源数", "format": "number"},
                {"field": "spearman", "label": "vs 约束前 Spearman", "format": "number"},
                {"field": "top50_overlap", "label": "Top 50 重合", "format": "number"},
                {"field": "max_shift", "label": "最大硬约束位移", "format": "number"},
                {"field": "top50_provisional", "label": "Top 50 Provisional", "format": "number"},
            ],
        },
        {
            "id": "target_coverage_table",
            "title": "重点模型覆盖明细",
            "subtitle": "Main 要求每板块至少 3 项且至少 9 个唯一测试家族；其余为 Provisional。",
            "showDescription": True,
            "dataset": "target_coverage_table",
            "defaultSort": {"field": "unique_families", "direction": "desc"},
            "density": "dense",
            "sourceId": "src_constrained_full",
            "layout": "full",
            "columns": [
                {"field": "model", "label": "模型", "type": "text"},
                {"field": "evidence_tier", "label": "证据层级", "type": "text"},
                {"field": "board_slots", "label": "板块槽位", "format": "number"},
                {"field": "unique_families", "label": "唯一测试家族", "format": "number"},
                {"field": "min_board_tests", "label": "最少板块测试", "format": "number"},
                {"field": "boards_below_3", "label": "低于 3 项板块", "format": "number"},
                {"field": "coverage_penalty_z", "label": "覆盖惩罚（SD）", "format": "number"},
            ],
        },
        {
            "id": "flash_sensitivity",
            "title": "Gemini Flash 开源模型下限敏感性",
            "subtitle": "比较至少 5、10、15 个 Main-evidence 开源模型排在 Flash 前面的政策强度。",
            "showDescription": True,
            "dataset": "flash_sensitivity",
            "defaultSort": {"field": "flash_open_floor", "direction": "asc"},
            "density": "dense",
            "sourceId": "src_sensitivity",
            "layout": "full",
            "columns": [
                {"field": "scheme_display", "label": "方案", "type": "text"},
                {"field": "flash_open_floor", "label": "开源下限", "format": "number"},
                {"field": "gemini_3_6_rank", "label": "Gemini 3.6 Flash", "format": "number"},
                {"field": "gemini_3_5_rank", "label": "Gemini 3.5 Flash", "format": "number"},
                {"field": "spearman", "label": "vs 约束前 Spearman", "format": "number"},
                {"field": "top50_overlap", "label": "Top 50 重合", "format": "number"},
                {"field": "max_shift", "label": "最大位移", "format": "number"},
            ],
        },
        {
            "id": "external_sources",
            "title": "可自动更新外部评测源审计",
            "subtitle": "只有同时满足时效、稳定接口、许可与纯模型可比性才建议进入每日 Action。",
            "showDescription": True,
            "dataset": "external_sources",
            "defaultSort": {"field": "mapping_risk", "direction": "asc"},
            "density": "dense",
            "sourceId": "src_external_sources",
            "layout": "full",
            "columns": [
                {"field": "source", "label": "来源", "type": "text"},
                {"field": "freshness", "label": "实测时效", "type": "text"},
                {"field": "license", "label": "许可 / 再分发", "type": "text"},
                {"field": "mapping_risk", "label": "模型映射风险", "type": "text"},
                {"field": "recommendation", "label": "结论", "type": "text"},
            ],
        },
    ]

    top50_columns = [
        {"field": "rank", "label": "名次", "format": "number"},
        {"field": "model", "label": "模型", "type": "text"},
        {"field": "creator", "label": "厂商", "type": "text"},
        {"field": "evidence_tier", "label": "证据层级", "type": "text"},
        {"field": "measurement_score", "label": "原测量分", "format": "number"},
        {"field": "raw_method_rank", "label": "原方法名次", "format": "number"},
        {"field": "coverage_penalty_z", "label": "覆盖惩罚（SD）", "format": "number"},
        {"field": "constraint_shift", "label": "硬约束位移", "format": "number", "movement": True},
        {"field": "unique_families", "label": "唯一测试家族", "format": "number"},
        {"field": "min_board_tests", "label": "最少板块测试", "format": "number"},
    ]
    for scheme_id in SCHEME_ORDER:
        tables.append(
            {
                "id": f"top50_{scheme_id}",
                "title": f"{SCHEME_SHORT[scheme_id]} · Top 50",
                "subtitle": "原测量分与硬约束位移并列；Provisional 表示至少一个板块不足 3 项或唯一家族不足 9。",
                "showDescription": True,
                "dataset": f"top50_{scheme_id}",
                "defaultSort": {"field": "rank", "direction": "asc"},
                "density": "dense",
                "sourceId": "src_constrained_top50",
                "layout": "full",
                "columns": top50_columns,
            }
        )

    blocks: list[dict[str, Any]] = [
        {
            "id": "title",
            "type": "markdown",
            "layout": "full",
            "body": "# AInsights 榜单：IRT 测量与产品约束分层方案",
        },
        {
            "id": "executive_summary",
            "type": "markdown",
            "layout": "full",
            "body": (
                "## Executive Summary\n\n"
                "- **五套候选榜均满足三条产品规则。** Claude Fable 5 全部为 #1；七条 Qwen 相邻版本 / tier 边调整后零违反；所有 Gemini Flash 前方至少有 15 个证据达标的开源模型。\n"
                "- **产品约束没有被伪装成 IRT 结果。** 每行同时保留原测量分、覆盖惩罚、约束前名次和硬约束位移；Qwen3.8 Max 因只有 7 个唯一测试家族仍标为 Provisional。\n"
                f"- **先修了一个会污染榜首的来源优先级缺陷。** Kimi 发布页中的 Fable comparator 不再覆盖 Anthropic 第一方值；修复后重建的 Fable AIndex 为 {current_fable_score:.4f}，仍居第一。\n"
                "- **本轮不把新外部源接入每日 Action。** LiveBench、Aider、SWE-bench 等均至少缺一项：当前汇总接口、稳定访问、明确再分发许可或纯模型可比性；可先做离线 PoC。"
            ),
        },
        {
            "id": "source_fix",
            "type": "markdown",
            "layout": "full",
            "body": (
                "## 1. 先修输入：第一方成绩优先于竞品比较列\n\n"
                "原生产合并逻辑对同一模型 / benchmark 使用后写覆盖，导致 Kimi K3 发布页中的 Claude Fable 5 对比列覆盖 Anthropic 自己的发布数据。冲突涉及 GDPval-AA Elo、AutomationBench、HLE、HLE with tools 和 Terminal-Bench v2.1。现在先判断来源是否属于该模型厂商，再在同优先级内保留原来的刷新顺序。\n\n"
                "**影响：** 这不是 IRT 参数问题，而是输入选择问题。继续增加来源之前必须先有冲突优先级，否则数据越多，榜单越依赖文件行序。"
            ),
        },
        {
            "id": "constraint_layers",
            "type": "markdown",
            "layout": "full",
            "sourceId": "src_constraints",
            "body": (
                "## 2. 测量分与产品规则分层，才能知道名次为什么变\n\n"
                "每套候选榜先取对应测量方法，再用唯一 benchmark family 做小幅覆盖校正，最后执行显式偏序。Fable 是冠军锚点；Qwen 只约束明确可比的相邻商业产品边；Gemini Flash 使用‘至少 15 个 Main-evidence 开源模型在前’的可审计下限。\n\n"
                "重排采用 raise-only 投影：违反边时把应更强的新型号提升到旧型号之前，而不是把旧型号拖到稀疏新型号原来的低位。位移超过 10 名应触发人工复核。"
            ),
        },
        {"id": "diagnostics_table", "type": "table", "layout": "full", "tableId": "scheme_diagnostics"},
        {
            "id": "diagnostics_read",
            "type": "markdown",
            "layout": "full",
            "sourceId": "src_constrained_diagnostics",
            "body": (
                "### 解读\n\n"
                f"五套方案与各自覆盖校正后、约束前榜单的 Spearman 为 {minimum_spearman:.4f}–{maximum_spearman:.4f}，Top 50 保留 {minimum_top50_overlap}–{maximum_top50_overlap} 个席位；总体结构变化小。但最大单模型位移很大，主要来自证据稀疏却被强制满足新版顺序的 Qwen 产品，因此必须同时展示 Provisional 和原名次。"
            ),
        },
        {
            "id": "target_rank_intro",
            "type": "markdown",
            "layout": "full",
            "sourceId": "src_constrained_diagnostics",
            "body": (
                "## 3. Fable 稳定第一，Qwen 顺序一致，Flash 退出异常头部\n\n"
                "图中名次数值越小越好。Fable 在五套方案均为 #1；Qwen3.8 Max 均排在 Qwen3.7 Max 之前，同版 Max 也排在 Plus 之前。Gemini 3.5/3.6 Flash 在 15 个开源模型下限下落在约 #26–#35，避免了原 Borda #4 这类与产品判断冲突的异常。"
            ),
        },
        {"id": "target_rank_chart", "type": "chart", "layout": "full", "chartId": "target_ranks"},
        {
            "id": "coverage_intro",
            "type": "markdown",
            "layout": "full",
            "sourceId": "src_constrained_full",
            "body": (
                "## 4. 异常不只来自‘每板块太少’，还来自跨板块重复\n\n"
                "Gemini 3.5 Flash 的五板块覆盖为 3/3/3/4/3，看似完全达标，但 16 个板块槽位只对应 9 个唯一测试家族；Muse Spark 也有同样结构。Qwen3.8 Max 则更直接地稀疏：13 个槽位、7 个唯一家族，三个板块不足 3 项。"
            ),
        },
        {"id": "coverage_chart", "type": "chart", "layout": "full", "chartId": "target_coverage"},
        {"id": "coverage_table", "type": "table", "layout": "full", "tableId": "target_coverage_table"},
        {
            "id": "flash_policy",
            "type": "markdown",
            "layout": "full",
            "sourceId": "src_sensitivity",
            "body": (
                "## 5. Gemini Flash 下调幅度是一条政策旋钮\n\n"
                "下限从 5 提高到 15 时，Gemini 3.5/3.6 Flash 大致再下移 10 名，但整体 Spearman 与 Top 50 重合变化很小。默认选择 15，是因为它既能消除 Flash 进入前十的异常，又不会把整个榜单重写。若产品希望更温和，可把 10 作为影子对照。"
            ),
        },
        {"id": "flash_sensitivity_table", "type": "table", "layout": "full", "tableId": "flash_sensitivity"},
        {
            "id": "source_assessment",
            "type": "markdown",
            "layout": "full",
            "sourceId": "src_external_sources",
            "body": (
                "## 6. 没有新来源达到‘现在就进 Action’的标准\n\n"
                "Aider 的官方 YAML 最容易自动拉取，但实测最新运行停在 2025-10-03；LiveBench 更当前，却只提供 judgment 数据，需要自行按 release/category 汇总，而且数据许可与本环境访问稳定性未闭环；SWE-bench 的机器文件稳定，但排名对象是 agent/system + model，不是纯模型。\n\n"
                "**结论：** 本轮只把来源冲突优先级修复纳入现有每日链路，不新增抓取步骤。LiveBench 与 Aider 可各做一次离线 PoC，验证映射、许可和增量更新后再决定。"
            ),
        },
        {"id": "source_assessment_table", "type": "table", "layout": "full", "tableId": "external_sources"},
        {
            "id": "recommendations",
            "type": "markdown",
            "layout": "full",
            "body": (
                "## 7. 推荐推进顺序\n\n"
                "1. **以约束 1PL/Rasch 做首要影子榜：** 它保留现行业务板块权重，同时满足三条产品规则；2PL 保持 challenger。\n"
                "2. **公开两列而不是一个神秘总分：** 同时展示 measurement rank 与 constrained rank，并对位移 >10 名标记人工复核。\n"
                "3. **保留 Main / Provisional 分层：** Main 要求每板块 ≥3 且唯一测试家族 ≥9；Qwen3.8 Max 等稀疏新型号可以按产品规则提升，但不能隐藏 Provisional。\n"
                "4. **为 Qwen 建结构化产品元数据：** version、tier、subfamily、preview、reasoning mode 不应继续靠名称正则推断。\n"
                "5. **给来源冲突增加 CI 门禁：** 第一方与 comparator 冲突必须记录选择原因；reasoning/non-reasoning 的 benchmark 广播在元数据补齐前继续列为风险。\n"
                "6. **新源先做离线 PoC：** LiveBench 检验汇总与许可，Aider 检验增量抓取；两者都不直接进入本轮生产分。"
            ),
        },
        {
            "id": "caveats",
            "type": "markdown",
            "layout": "full",
            "body": (
                "## 8. 解释边界与待解决问题\n\n"
                "- Fable 5 当前是带 fallback 的系统口径，严格说不等同于单一基础模型；本报告按明确产品要求将其锚定第一。\n"
                "- Qwen3.8 Max 只有 7 个唯一测试家族；把它提升到 Qwen3.7 Max 之前是产品先验，不是当前 benchmark 证据自然支持的结论。\n"
                "- Gemini Flash 的 15 个开源模型下限是政策参数，不是统计估计；敏感性表提供 5/10/15 三档。\n"
                "- 当前 IRT 仍是聚合 benchmark-as-item 连续近似，没有题目级响应。\n"
                "- variantGroup 仍可能跨 reasoning mode 共享外部分数；直接禁止会破坏部分现有 alias，因此需要先补结构化评测模式元数据。\n"
                "- 外部源许可审计只支持‘暂不接入’结论；正式 PoC 前仍需逐个确认数据集卡与提交工件许可。"
            ),
        },
        {
            "id": "appendix",
            "type": "markdown",
            "layout": "full",
            "sourceId": "src_constrained_top50",
            "body": (
                "## 附录：五套受约束方案完整 Top 50\n\n"
                "每表严格 50 行。原测量分只在同一方法内解释；硬约束位移为正表示相对覆盖校正后的未约束榜上升。各方案前三名：\n\n"
                + "\n".join(top3_lines)
            ),
        },
    ]

    for scheme_id in SCHEME_ORDER:
        blocks.append(
            {
                "id": f"top50_block_{scheme_id}",
                "type": "table",
                "layout": "full",
                "tableId": f"top50_{scheme_id}",
            }
        )
        rows = top50_datasets[f"top50_{scheme_id}"]
        provisional = sum(row["evidence_tier"] == "Provisional" for row in rows)
        blocks.append(
            {
                "id": f"top50_note_{scheme_id}",
                "type": "markdown",
                "layout": "full",
                "sourceId": "src_constrained_top50",
                "body": (
                    f"### {SCHEME_SHORT[scheme_id]} 表后说明\n\n"
                    f"榜首为 **{rows[0]['model']}**；Top 50 含 {provisional} 个 Provisional 模型。"
                ),
            }
        )

    artifact = {
        "surface": "report",
        "manifest": {
            "version": 1,
            "surface": "report",
            "title": "AInsights 榜单：IRT 测量与产品约束分层方案",
            "description": (
                f"基于 {snapshot_label} 数据快照，比较五套显式产品约束榜并给出完整 Top 50。"
            ),
            "generatedAt": generated_at,
            "cards": [],
            "charts": charts,
            "tables": tables,
            "sources": sources,
            "blocks": blocks,
        },
        "snapshot": {
            "version": 1,
            "generatedAt": summary["data_generated_at"],
            "status": "ready",
            "datasets": {
                "scheme_diagnostics": diagnostic_rows,
                "target_ranks": target_rank_rows,
                "target_coverage": target_coverage_rows,
                "target_coverage_table": target_coverage_table,
                "flash_sensitivity": sensitivity_rows,
                "external_sources": source_assessment_rows,
                **top50_datasets,
            },
        },
        "sources": sources,
    }

    output_path = REPORT_DIR / "artifact_constrained.json"
    output_path.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(output_path)


if __name__ == "__main__":
    main()
