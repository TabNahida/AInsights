"""Build the portable-report artifact from reviewed ranking outputs."""

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
    "baseline_aindex",
    "rasch_business",
    "twopl_equal",
    "robust_eb",
    "borda_breadth",
]
SCHEME_SHORT = {
    "baseline_aindex": "现行 AIndex",
    "rasch_business": "1PL/Rasch 近似",
    "twopl_equal": "2PL + 稀疏回退",
    "robust_eb": "稳健秩收缩",
    "borda_breadth": "Borda 广度",
}
SCHEME_ROLE = {
    "baseline_aindex": "对照",
    "rasch_business": "首要影子榜",
    "twopl_equal": "Challenger",
    "robust_eb": "敏感性参照",
    "borda_breadth": "广度辅助榜",
}
BOARD_SHORT = {
    "coding": "Coding",
    "agentic-tool-work": "Agentic / 工具",
    "hard-reasoning": "高难推理",
    "knowledge-science": "知识 / 科学",
    "instruction-context": "指令 / 上下文",
}


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
    *,
    metric_definitions: list[str] | None = None,
) -> dict[str, Any]:
    if path.lower().endswith(".csv"):
        source_sql = f"SELECT * FROM read_csv_auto('{path}', header = true)"
    elif path.lower().endswith(".json"):
        source_sql = f"SELECT * FROM read_json_auto('{path}')"
    else:
        source_sql = None
    return {
        "id": source_id,
        "label": label,
        "path": path,
        "query": {
            "language": "python/file",
            **({"sql": source_sql} if source_sql else {}),
            "query": (
                "python -B analysis/irt_leaderboard_exploration/"
                "irt_leaderboard_analysis.py"
            ),
            "description": description,
            "tables_used": [path],
            "metric_definitions": metric_definitions or [],
        },
    }


def main() -> None:
    summary = json.loads(
        (OUTPUT_DIR / "validation_summary.json").read_text(encoding="utf-8")
    )
    top50_raw = load_csv(OUTPUT_DIR / "top50_all_schemes.csv")
    lobo_raw = load_csv(OUTPUT_DIR / "lobo_stability_by_item.csv")
    diagnostics = {row["scheme_id"]: row for row in summary["schemes"]}

    generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    snapshot_label = local_snapshot_label(summary["data_generated_at"])
    eligible_share = (
        summary["hard_floor_eligible_models"] / summary["deduped_scorable_models"]
    )
    soft_share = (
        summary["all_boards_ge_soft_target_models"]
        / summary["deduped_scorable_models"]
    )

    headline = [
        {
            "eligible_models": summary["hard_floor_eligible_models"],
            "scorable_models": summary["deduped_scorable_models"],
            "eligible_share": eligible_share,
            "all_soft_models": summary["all_boards_ge_soft_target_models"],
            "all_soft_share": soft_share,
            "matrix_density": summary["data_quality"]["score_matrix_density"],
            "active_conflicts": summary["data_quality"][
                "active_conflicting_model_benchmark_groups"
            ],
        }
    ]

    coverage_rows = [
        {
            **row,
            "board_display": BOARD_SHORT[row["board_id"]],
        }
        for row in summary["coverage"]
    ]
    coverage_chart_rows = []
    for row in coverage_rows:
        for threshold, share_field, count_field in [
            ("≥2（硬门槛）", "share_ge_2", "models_ge_2"),
            ("≥3（软目标）", "share_ge_3", "models_ge_3"),
        ]:
            coverage_chart_rows.append(
                {
                    **row,
                    "threshold": threshold,
                    "share": row[share_field],
                    "models_at_threshold": row[count_field],
                }
            )

    scheme_rows = []
    for scheme_id in SCHEME_ORDER:
        row = diagnostics[scheme_id]
        scheme_rows.append(
            {
                "scheme_id": scheme_id,
                "scheme_display": SCHEME_SHORT[scheme_id],
                "role": SCHEME_ROLE[scheme_id],
                "ranked_models": row["ranked_models"],
                "top50_overlap": row["top50_overlap_with_baseline"],
                "spearman_vs_baseline": row["spearman_vs_baseline"],
                "top50_median_unique": row[
                    "top50_median_unique_benchmark_families"
                ],
                "top50_below_soft": row[
                    "top50_models_with_any_board_below_3"
                ],
                "lobo_mean_top50": row["lobo_mean_top50_retention"],
                "lobo_min_top50": row["lobo_min_top50_retention"],
                "lobo_min_population": row[
                    "lobo_min_eligible_population_retention"
                ],
                "unique_coverage_spearman": row[
                    "score_unique_coverage_spearman"
                ],
            }
        )

    overlap_rows = [
        row for row in scheme_rows if row["scheme_id"] != "baseline_aindex"
    ]

    lobo_worst = []
    for scheme_id in SCHEME_ORDER[1:]:
        rows = [row for row in lobo_raw if row["scheme_id"] == scheme_id]
        worst = min(rows, key=lambda row: float(row["top50_retention"]))
        lobo_worst.append(
            {
                "scheme_display": SCHEME_SHORT[scheme_id],
                "omitted_item": worst["omitted_item_id"],
                "affected_boards": worst["affected_boards"],
                "eligible_after": integer(worst["post_omission_eligible_models"]),
                "eligible_retention": number(
                    worst["eligible_population_retention"]
                ),
                "conditional_spearman": number(worst["conditional_spearman"]),
                "top50_retention": number(worst["top50_retention"]),
            }
        )

    top50_datasets: dict[str, list[dict[str, Any]]] = {}
    top3_lines: list[str] = []
    for scheme_id in SCHEME_ORDER:
        rows = [row for row in top50_raw if row["scheme_id"] == scheme_id]
        typed_rows = []
        for row in rows:
            below = integer(row["boards_below_soft_target"]) or 0
            typed_rows.append(
                {
                    "rank": integer(row["rank"]),
                    "model": row["model"],
                    "creator": row["creator"],
                    "score": number(row["score"]),
                    "rank_change": integer(row["rank_change_vs_baseline"]),
                    "unique_families": integer(row["unique_benchmark_families"]),
                    "board_slots": integer(row["board_test_slots_total"]),
                    "min_board_tests": integer(row["min_board_tests"]),
                    "boards_below_soft": below,
                    "coverage_status": (
                        "五板块均 ≥3" if below == 0 else f"{below} 个板块仅 2 项"
                    ),
                    "baseline_rank": integer(row["baseline_rank"]),
                    "coding_tests": integer(row["coding_tests"]),
                    "agentic_tests": integer(row["agentic-tool-work_tests"]),
                    "reasoning_tests": integer(row["hard-reasoning_tests"]),
                    "knowledge_tests": integer(row["knowledge-science_tests"]),
                    "instruction_tests": integer(row["instruction-context_tests"]),
                }
            )
        top50_datasets[f"top50_{scheme_id}"] = typed_rows
        leaders = "、".join(row["model"] for row in typed_rows[:3])
        top3_lines.append(f"- **{SCHEME_SHORT[scheme_id]}**：{leaders}")

    scorable_models = int(summary["deduped_scorable_models"])
    eligible_models = int(summary["hard_floor_eligible_models"])
    all_soft_models = int(summary["all_boards_ge_soft_target_models"])
    item_slots = int(summary["eligible_response_item_slots"])
    unique_families = int(summary["unique_eligible_benchmark_families"])
    active_conflicts = int(
        summary["data_quality"]["active_conflicting_model_benchmark_groups"]
    )
    matrix_density = float(summary["data_quality"]["score_matrix_density"])
    agentic_coverage = next(
        row for row in summary["coverage"] if row["board_id"] == "agentic-tool-work"
    )
    alternative_diagnostics = [diagnostics[scheme_id] for scheme_id in SCHEME_ORDER[1:]]
    spearman_min = min(float(row["spearman_vs_baseline"]) for row in alternative_diagnostics)
    spearman_max = max(float(row["spearman_vs_baseline"]) for row in alternative_diagnostics)
    overlap_min = min(int(row["top50_overlap_with_baseline"]) for row in alternative_diagnostics)
    overlap_max = max(int(row["top50_overlap_with_baseline"]) for row in alternative_diagnostics)
    conditional_min = min(
        float(row["lobo_min_conditional_spearman"]) for row in alternative_diagnostics
    )
    conditional_max = max(
        float(row["lobo_min_conditional_spearman"]) for row in alternative_diagnostics
    )
    worst_population = min(
        lobo_worst, key=lambda row: float(row["eligible_retention"])
    )
    worst_top50_min = min(float(row["top50_retention"]) for row in lobo_worst)
    worst_top50_max = max(float(row["top50_retention"]) for row in lobo_worst)

    def rank_for(scheme_id: str, model_name: str) -> int | None:
        match = next(
            (
                row
                for row in top50_datasets[f"top50_{scheme_id}"]
                if row["model"] == model_name
            ),
            None,
        )
        return int(match["rank"]) if match is not None else None

    movement_examples = []
    for model_name in ("Gemini 3.5 Flash", "Muse Spark"):
        ranks = {scheme_id: rank_for(scheme_id, model_name) for scheme_id in SCHEME_ORDER}
        if all(rank is not None for rank in ranks.values()):
            movement_examples.append(
                f"{model_name} 从基准 #{ranks['baseline_aindex']} 变为 "
                f"1PL #{ranks['rasch_business']}、2PL #{ranks['twopl_equal']}、"
                f"稳健秩 #{ranks['robust_eb']}、Borda #{ranks['borda_breadth']}"
            )
    movement_text = "；".join(movement_examples)

    sources = [
        source(
            "src_models",
            "模型与 benchmark 控制快照",
            "docs/data/models.json",
            "项目站点使用的模型、指标、预设和聚合 benchmark 分数快照。",
        ),
        source(
            "src_analysis",
            "榜单分析实现",
            "analysis/irt_leaderboard_exploration/irt_leaderboard_analysis.py",
            "对模型档位去重，构建五板块响应矩阵，拟合五套方案并运行唯一测试家族留一法。",
            metric_definitions=[
                "硬门槛：五个板块分别至少 2 个 canonical benchmark family。",
                "软目标：板块少于 3 项时扣除标准误保守下界和覆盖短缺项。",
                "LOBO：按唯一 benchmark family 在其出现的所有板块同时删除。",
            ],
        ),
        source(
            "src_validation",
            "验证与数据质量摘要",
            "analysis/irt_leaderboard_exploration/outputs/validation_summary.json",
            "数据密度、门槛人口、方案比较、覆盖分布和唯一测试家族留一法摘要。",
        ),
        source(
            "src_coverage",
            "板块覆盖分布",
            "analysis/irt_leaderboard_exploration/outputs/coverage_profile.csv",
            "各板块达到至少 1、2、3 个 canonical benchmark family 的模型数量与比例。",
        ),
        source(
            "src_diagnostics",
            "方案诊断",
            "analysis/irt_leaderboard_exploration/outputs/scheme_diagnostics.csv",
            "入榜数、与基准的共同人口 Spearman、Top 50 重合、覆盖与留一法稳定性。",
        ),
        source(
            "src_lobo",
            "唯一 benchmark family 留一法明细",
            "analysis/irt_leaderboard_exploration/outputs/lobo_stability_by_item.csv",
            "每次跨板块删除一个唯一测试家族后的合格人口、条件 Spearman 和 Top 50 保留率。",
        ),
        source(
            "src_top50",
            "五套方案 Top 50",
            "analysis/irt_leaderboard_exploration/outputs/top50_all_schemes.csv",
            "五套方案各 50 行，包含名次、分数、相对基准变化和覆盖信息。",
        ),
    ]

    cards = [
        {
            "id": "eligible_models",
            "dataset": "headline",
            "sourceId": "src_validation",
            "description": "五板块均达到每板块至少 2 项的模型。",
            "metrics": [
                {"label": "替代榜合格模型", "field": "eligible_models", "format": "number"},
                {"label": f"占 {scorable_models} 个可评分模型", "field": "eligible_share", "format": "percent"},
            ],
        },
        {
            "id": "all_soft_models",
            "dataset": "headline",
            "sourceId": "src_validation",
            "description": "五板块全部达到软目标 3 项的模型。",
            "metrics": [
                {"label": "全板块均 ≥3", "field": "all_soft_models", "format": "number"},
                {"label": "占可评分模型", "field": "all_soft_share", "format": "percent"},
            ],
        },
        {
            "id": "matrix_density",
            "dataset": "headline",
            "sourceId": "src_validation",
            "description": f"{summary['source_model_rows']} × {summary['data_quality']['score_matrix_cells'] // summary['source_model_rows']} 原始模型—指标矩阵的非空比例。",
            "metrics": [
                {"label": "原始分数矩阵密度", "field": "matrix_density", "format": "percent"},
                {"label": "活跃冲突组", "field": "active_conflicts", "format": "number"},
            ],
        },
    ]

    charts = [
        {
            "id": "coverage_by_board",
            "title": "各板块达到硬门槛与软目标的模型占比",
            "subtitle": "硬门槛为每板块 ≥2；软目标为每板块 ≥3。",
            "showDescription": True,
            "intent": "comparison",
            "question": "哪个能力板块限制了榜单准入？",
            "rationale": "并列柱能直接比较五板块的硬门槛与软目标覆盖缺口。",
            "type": "bar",
            "dataset": "coverage_chart",
            "sourceId": "src_coverage",
            "encodings": {
                "x": {"field": "board_display", "type": "nominal", "label": "能力板块"},
                "y": {
                    "field": "share",
                    "type": "quantitative",
                    "format": "percent",
                    "label": "模型占比",
                },
                "color": {"field": "threshold", "type": "nominal", "label": "覆盖标准"},
                "tooltip": [
                    {"field": "models", "type": "quantitative", "label": "可评分模型"},
                    {"field": "models_at_threshold", "type": "quantitative", "label": "达标模型"},
                    {"field": "canonical_coverage_items", "type": "quantitative", "label": "可用测试槽位"},
                ],
            },
            "valueFormat": "percent",
            "yAxisTitle": "模型占比",
            "layout": "full",
            "settings": {"groupMode": "grouped", "sort": "none", "showValues": True},
            "surface": {"viewMode": "visualization", "showControls": False},
        },
        {
            "id": "top50_overlap",
            "title": "四个替代方案与现行 Top 50 的重合数",
            "subtitle": "50 个席位中仍由现行 Top 50 模型占据的数量。",
            "showDescription": True,
            "intent": "comparison",
            "question": "每套方法会在 Top 50 更换多少个模型？",
            "rationale": "单系列柱状图比相关系数更直接地显示榜单边界变化。",
            "type": "bar",
            "dataset": "overlap",
            "sourceId": "src_diagnostics",
            "encodings": {
                "x": {"field": "scheme_display", "type": "nominal", "label": "方案"},
                "y": {"field": "top50_overlap", "type": "quantitative", "format": "number", "label": "重合席位"},
                "tooltip": [
                    {"field": "spearman_vs_baseline", "type": "quantitative", "format": "number", "label": "共同人口 Spearman"},
                    {"field": "top50_median_unique", "type": "quantitative", "format": "number", "label": "Top 50 唯一测试中位数"},
                    {"field": "top50_below_soft", "type": "quantitative", "format": "number", "label": "任一板块 <3"},
                ],
            },
            "valueFormat": "number",
            "yAxisTitle": "重合席位（最多 50）",
            "layout": "full",
            "referenceLines": [{"axis": "y", "value": 50, "label": "完全一致", "color": "neutral", "lineStyle": "dashed"}],
            "settings": {"sort": "none", "showValues": True},
            "surface": {"viewMode": "visualization", "showControls": False},
        },
    ]

    common_top50_columns = [
        {"field": "rank", "label": "名次", "format": "number"},
        {"field": "model", "label": "模型", "type": "text"},
        {"field": "creator", "label": "厂商", "type": "text"},
        {"field": "score", "label": "方案内分数", "format": "number"},
        {"field": "rank_change", "label": "较基准升降", "format": "number", "movement": True},
        {"field": "unique_families", "label": "唯一测试家族", "format": "number"},
        {"field": "min_board_tests", "label": "最少板块测试", "format": "number"},
        {"field": "coverage_status", "label": "软目标状态", "type": "text"},
    ]

    tables = [
        {
            "id": "scheme_comparison",
            "title": "方案比较与建议角色",
            "subtitle": "Spearman 在两榜共同可排名人口上重新取秩；LOBO 按唯一测试家族跨板块删除。",
            "showDescription": True,
            "dataset": "scheme_comparison",
            "defaultSort": {"field": "top50_overlap", "direction": "desc"},
            "density": "dense",
            "sourceId": "src_diagnostics",
            "layout": "full",
            "columns": [
                {"field": "scheme_display", "label": "方案", "type": "text"},
                {"field": "role", "label": "建议角色", "type": "text"},
                {"field": "ranked_models", "label": "入榜数", "format": "number"},
                {"field": "spearman_vs_baseline", "label": "vs 基准 Spearman", "format": "number"},
                {"field": "top50_overlap", "label": "Top 50 重合", "format": "number"},
                {"field": "top50_median_unique", "label": "Top 50 唯一测试中位", "format": "number"},
                {"field": "top50_below_soft", "label": "Top 50 任一板块 <3", "format": "number"},
                {"field": "lobo_mean_top50", "label": "LOBO 平均 Top 50 保留", "format": "percent"},
                {"field": "lobo_min_top50", "label": "LOBO 最差 Top 50 保留", "format": "percent"},
            ],
        },
        {
            "id": "lobo_worst",
            "title": "每套方案的最差唯一测试家族留一结果",
            "subtitle": "条件 Spearman 只描述删除后仍合格的人口；必须与人口保留率一起读。",
            "showDescription": True,
            "dataset": "lobo_worst",
            "defaultSort": {"field": "top50_retention", "direction": "asc"},
            "density": "dense",
            "sourceId": "src_lobo",
            "layout": "full",
            "columns": [
                {"field": "scheme_display", "label": "方案", "type": "text"},
                {"field": "omitted_item", "label": "删除测试家族", "type": "text"},
                {"field": "affected_boards", "label": "受影响板块", "type": "text"},
                {"field": "eligible_after", "label": "删除后合格模型", "format": "number"},
                {"field": "eligible_retention", "label": "合格人口保留", "format": "percent"},
                {"field": "conditional_spearman", "label": "条件 Spearman", "format": "number"},
                {"field": "top50_retention", "label": "Top 50 保留", "format": "percent"},
            ],
        },
    ]

    for scheme_id in SCHEME_ORDER:
        tables.append(
            {
                "id": f"table_top50_{scheme_id}",
                "title": f"{SCHEME_SHORT[scheme_id]} · Top 50",
                "subtitle": "分数只在本方案内解释；正的升降数表示较现行基准上升。",
                "showDescription": True,
                "dataset": f"top50_{scheme_id}",
                "defaultSort": {"field": "rank", "direction": "asc"},
                "density": "dense",
                "sourceId": "src_top50",
                "layout": "full",
                "columns": common_top50_columns,
            }
        )

    blocks: list[dict[str, Any]] = [
        {
            "id": "title",
            "type": "markdown",
            "layout": "full",
            "body": "# AInsights 榜单：覆盖感知的 IRT 探索",
        },
        {
            "id": "executive_summary",
            "type": "markdown",
            "layout": "full",
            "sourceId": "src_validation",
            "body": (
                "## Executive Summary\n\n"
                "- **IRT 方向值得继续，但当前只能称连续 IRT 近似 / IRT-inspired。** 数据是模型 × 聚合 benchmark 分数，不是题目级作答。\n"
                f"- **先不替换生产主榜。** 建议保留五板块，以每板块 ≥2 为硬门槛、≥3 为软目标；在 {scorable_models} 个可评分模型中，{eligible_models} 个达到硬门槛，只有 {all_soft_models} 个五板块都达到软目标。\n"
                "- **过渡影子榜先用连续 1PL + 现行板块权重，正式候选则应转向 family-capped 的稳健秩正态分层收缩。** 前者便于隔离测量变化，后者对不同 benchmark 量纲更稳健；2PL 只做诊断。\n"
                f"- **治理优先于切榜。** {item_slots} 个板块测试槽位只有 {unique_families} 个唯一测试家族；唯一家族留一后最差只保留 {float(worst_population['eligible_retention']):.1%} 的合格人口。原始矩阵非空率为 {matrix_density:.2%}，另有 {active_conflicts} 组活跃外部结果冲突。"
            ),
        },
        {
            "id": "headline_metrics",
            "type": "metric-strip",
            "layout": "full",
            "cardIds": ["eligible_models", "all_soft_models", "matrix_density"],
        },
        {
            "id": "method_layers",
            "type": "markdown",
            "layout": "full",
            "sourceId": "src_analysis",
            "body": (
                "## 1. 把一个‘总公式’拆成三层决策\n\n"
                "**准入层**决定数据是否足够：每板块至少 2 项才入榜，3 项为软目标。**测量层**决定如何在板块内处理 benchmark 难度、区分度与不确定性：1PL、2PL、稳健秩收缩或 Borda。**合成层**决定五板块如何代表产品价值：现行 40/24/20/8/8、等权，或强调短板的几何均值。\n\n"
                "IRT 主要改善第二层；它不会自动学出 Coding 对业务究竟该占 40% 还是 20%。本轮故意保留多种合成方式，用排名差异暴露政策选择，而不是把权重藏进模型参数。"
            ),
        },
        {
            "id": "coverage_intro",
            "type": "markdown",
            "layout": "full",
            "sourceId": "src_validation",
            "body": (
                "## 2. 覆盖门槛：硬 2、软 3 是当前可落地折中\n\n"
                f"图中比较每个板块达到至少 2 项与至少 3 项的模型占比。若直接把 3 项设为硬门槛，合格模型会从 {eligible_models} 个缩到 {all_soft_models} 个，现阶段会排除大部分可评分模型。"
            ),
        },
        {"id": "coverage_chart_block", "type": "chart", "layout": "full", "chartId": "coverage_by_board"},
        {
            "id": "coverage_read",
            "type": "markdown",
            "layout": "full",
            "sourceId": "src_validation",
            "body": (
                "### 解读\n\n"
                f"Agentic / 工具是决定准入人口的瓶颈：达到 2 项的模型为 {agentic_coverage['models_ge_2']}/{scorable_models}，达到 3 项只有 {agentic_coverage['models_ge_3']}/{scorable_models}。Knowledge / Science 最完整，达到 3 项的比例为 {next(row for row in summary['coverage'] if row['board_id'] == 'knowledge-science')['share_ge_3']:.1%}。因此‘硬 2、软 3’更适合影子运行；若用于公开 Top 10，可额外要求五板块全部达到 3 项。"
            ),
        },
        {
            "id": "comparison_intro",
            "type": "markdown",
            "layout": "full",
            "sourceId": "src_validation",
            "body": (
                "## 3. 五套方案：头部共识存在，Top 50 边界会变化\n\n"
                f"下表把准入人口、与现行榜的共同人口秩相关、Top 50 重合和留一法放在一起。替代方案与基准的 Spearman 为 {spearman_min:.3f}–{spearman_max:.3f}，Top 50 仍会替换 {50 - overlap_max}–{50 - overlap_min} 个席位。"
            ),
        },
        {"id": "scheme_table_block", "type": "table", "layout": "full", "tableId": "scheme_comparison"},
        {
            "id": "comparison_table_read",
            "type": "markdown",
            "layout": "full",
            "sourceId": "src_diagnostics",
            "body": (
                "### 为什么 1PL 先做影子榜\n\n"
                f"1PL 保留现行板块权重，Top 50 与基准重合 {diagnostics['rasch_business']['top50_overlap_with_baseline']} 个，并且 Top 50 中任一板块低于软目标的模型最少（{diagnostics['rasch_business']['top50_models_with_any_board_below_3']} 个）。2PL 的整体连续性相近，但 {item_slots} 个板块测试槽位中有 {summary['twopl_fixed_sparse_discrimination_item_slots']} 个因观测少于 50 而固定区分度；其余斜率也会混入 benchmark 量程和选择性缺失，因此仅适合诊断。下面的柱图更直观展示席位变化。"
            ),
        },
        {"id": "overlap_chart_block", "type": "chart", "layout": "full", "chartId": "top50_overlap"},
        {
            "id": "overlap_read",
            "type": "markdown",
            "layout": "full",
            "sourceId": "src_top50",
            "body": (
                "### 典型重排不是单纯的‘小样本惩罚’\n\n"
                + (
                    f"{movement_text}。" if movement_text else "不同方案仍出现明显重排。"
                )
                + "这说明重排同时来自测量变换、板块权重与合成方式，不能只解释为‘小样本惩罚’；同一测试跨板块复用还会高估证据广度。"
            ),
        },
        {
            "id": "stability_intro",
            "type": "markdown",
            "layout": "full",
            "sourceId": "src_validation",
            "body": (
                "## 4. 稳定性：名次相关很高，不等于门槛稳健\n\n"
                "本次复核按 26 个唯一 benchmark family 做留一法，并在测试跨板块出现时同时删除。表中‘条件 Spearman’只在删除后仍合格的共同人口上重新取秩，因此必须与合格人口保留率一起解释。"
            ),
        },
        {"id": "lobo_table_block", "type": "table", "layout": "full", "tableId": "lobo_worst"},
        {
            "id": "stability_read",
            "type": "markdown",
            "layout": "full",
            "sourceId": "src_validation",
            "body": (
                "### 解读\n\n"
                f"四个替代方案的最差条件 Spearman 仍为 {conditional_min:.3f}–{conditional_max:.3f}，但删除 {worst_population['omitted_item']} 后合格模型只剩 {worst_population['eligible_after']} 个，人口保留率为 {float(worst_population['eligible_retention']):.1%}；最差测试删除时 Top 50 只保留 {worst_top50_min:.0%}–{worst_top50_max:.0%}。所以当前主要风险不是‘留存模型的次序大乱’，而是准入门槛依赖少数覆盖广的测试。生产化需要同时展示人口稳定性与名次稳定性。"
            ),
        },
        {
            "id": "recommendation",
            "type": "markdown",
            "layout": "full",
            "sourceId": "src_validation",
            "body": (
                "## 5. 建议推进顺序\n\n"
                "1. **冻结口径，不立刻切主榜：** 保留五板块，先把‘硬 2、软 3’和‘证据不足不入榜’作为公开规则草案。\n"
                "2. **过渡影子榜用 1PL/Rasch 近似 + 现行 40/24/20/8/8：** 先隔离板块内测量变化，连续观察 2–4 个刷新周期。\n"
                "3. **正式候选改成 family-capped 的稳健秩正态分层收缩：** 同一 benchmark family 的跨板块信息分配之和不超过 1，并固定现行板块权重后再比较；这比直接上 2PL 更能承受异质量纲。\n"
                "4. **2PL 只做诊断，Borda 做透明广度榜：** 前者的区分度不可作经典 IRT 解释，后者用于检查‘无明显短板’的排序。\n"
                "5. **给 Top 10 更高证据标准：** 可试验五板块均 ≥3，或在现有板块门槛之外增加全局唯一测试家族软目标。\n"
                "6. **先完成来源治理：** 清理重复冲突、锁定版本优先级、审计同义指标映射，再决定是否替换生产公式。"
            ),
        },
        {
            "id": "caveats",
            "type": "markdown",
            "layout": "full",
            "sourceId": "src_validation",
            "body": (
                "## 6. 解释边界与数据风险\n\n"
                "- 当前是聚合 benchmark 分数上的连续因子近似，不是经典题目级 IRT；没有题目数、二项方差或逐题响应。\n"
                f"- 原始模型—指标矩阵密度仅 {matrix_density:.2%}，且有外部分数的模型系统性更强，缺失不是随机的；收缩只能表达不确定性，不能识别缺失模型的真实能力。\n"
                f"- 同一 benchmark 跨板块复用造成局部依赖：{item_slots} 个可用板块槽位只有 {unique_families} 个唯一测试家族。\n"
                f"- 2PL 有 {summary['twopl_fixed_sparse_discrimination_item_slots']}/{item_slots} 个槽位使用固定区分度；所谓稳健 EB 使用固定先验精度 2，更准确是固定先验层级收缩。\n"
                f"- {active_conflicts} 组活跃外部结果存在冲突；同义来源的版本和量表一致性仍需逐项审计。\n"
                "- 当前 SE 没有包含 benchmark 参数估计误差，‘LCB’应理解为启发式保守分，而非严格后验可信下界。\n"
                "- 能力值按当期模型重新标准化，会产生 cohort drift；生产版必须冻结 anchor models、参数版本和校准窗口。"
            ),
        },
        {
            "id": "next_experiments",
            "type": "markdown",
            "layout": "full",
            "sourceId": "src_analysis",
            "body": (
                "## 7. 下一轮应做的正交实验\n\n"
                "当前五套方案同时改变了部分测量方法和合成函数，不能把全部名次变化归因于 IRT。下一轮建议完整交叉 **测量方法（1PL / 2PL / 稳健秩）× 板块权重（现行 / 等权）× 合成（潜变量均值 / log 几何 / 严格几何）**，并对硬门槛 1/2/3、软目标 3/4、保守系数 0/0.5/1 和短缺惩罚 0/0.2/0.4 做敏感性网格。另应加入跨板块 family 分配、super-family cap、缺失结果 −0.2/−0.4 SD 压力测试、bootstrap Top 50 入选概率，以及跨刷新周期的 anchor 参数漂移。"
            ),
        },
        {
            "id": "appendix_intro",
            "type": "markdown",
            "layout": "full",
            "sourceId": "src_top50",
            "body": (
                "## 附录：五套方案完整 Top 50\n\n"
                "每张表严格包含 50 个唯一 variant group。不同方法的分数尺度不同，跨方案应比较名次、覆盖与升降，不应直接比较绝对分数。当前各方案前三名如下：\n\n"
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
                "tableId": f"table_top50_{scheme_id}",
            }
        )
        top_rows = top50_datasets[f"top50_{scheme_id}"]
        blocks.append(
            {
                "id": f"top50_note_{scheme_id}",
                "type": "markdown",
                "layout": "full",
                "sourceId": "src_top50",
                "body": (
                    f"### {SCHEME_SHORT[scheme_id]} 表后说明\n\n"
                    f"该方案榜首为 **{top_rows[0]['model']}**；Top 50 的唯一测试家族中位数为 "
                    f"{diagnostics[scheme_id]['top50_median_unique_benchmark_families']}，"
                    f"其中 {diagnostics[scheme_id]['top50_models_with_any_board_below_3']} 个模型至少一个板块只有 2 项测试。"
                ),
            }
        )

    artifact = {
        "surface": "report",
        "manifest": {
            "version": 1,
            "surface": "report",
            "title": "AInsights 榜单：覆盖感知的 IRT 探索",
            "description": (
                f"基于 {snapshot_label} 数据快照，比较五套覆盖感知榜单方案并给出完整 Top 50。"
            ),
            "generatedAt": generated_at,
            "cards": cards,
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
                "headline": headline,
                "coverage": coverage_rows,
                "coverage_chart": coverage_chart_rows,
                "scheme_comparison": scheme_rows,
                "overlap": overlap_rows,
                "lobo_worst": lobo_worst,
                **top50_datasets,
            },
        },
        "sources": sources,
    }

    output_path = REPORT_DIR / "artifact.json"
    output_path.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(output_path)


if __name__ == "__main__":
    main()
