"""Render the two-Core experiments from scored results without altering scores."""
from __future__ import annotations

from collections import Counter
import math
from pathlib import Path

from analysis.irt_leaderboard_exploration import core_variants as base
from analysis.irt_leaderboard_exploration import preference_core_variants as preferences

BOARDS = base.scheme18.BOARD_ORDER
TEST_NOTES = {
    base.TB: "终端环境中的编程和工具任务；旧版按共同样本换算后折扣",
    base.LATEST_TB: "终端环境中的编程和工具任务；仅使用 v4.0 同配置实测",
    "SciCode": "科学研究场景中的编程能力",
    "LiveCodeBench": "竞赛型代码问题；只用原始直接成绩",
    "AutomationBench-AA": "自动化工作流执行",
    "τ³-Banking": "银行场景中的交互和工具使用",
    "τ²-Bench Telecom": "电信场景中的交互和工具使用",
    "AA-Briefcase": "工作任务表现；使用 Elo 换算分",
    "GDPval-AA v2": "专业知识工作交付；使用 Elo 换算分",
    "CritPt": "研究级物理推理",
    "Humanity's Last Exam": "跨学科高难问题",
    "GPQA Diamond": "研究生级科学知识与推理",
    "AIME 2025": "竞赛数学推理",
    "AA-Omniscience Accuracy": "知识问答的回答准确率",
    "MMMU-Pro": "多学科多模态理解和推理",
    "AA-LCR v1.1": "长上下文推理",
    "GDP.pdf": "PDF 文档任务；使用 all-pass 成绩",
    "IFBench": "复杂指令遵循",
}
TARGET_NAMES = dict(zip(preferences.TARGETS, (
    "Fable 5.1", "GPT-6 Astra", "Kimi K3", "Gemini 3.8 Flash", "GPT-5.5",
    "Muse Spark 1.3", "Qwen3.8 Max", "Qwen3.8 2.4T A95B", "Qwen3.8 Flash-Next",
)))
PREFERENCE_LABELS = (
    "Fable 5.1 第一", "GPT-6 Astra 第二", "Kimi K3 高于 Gemini 3.8 Flash",
    "GPT-5.5 高于 Muse Spark 1.3", "Qwen3.8 Max 高于 Qwen3.8 Flash-Next",
    "Qwen3.8 2.4T A95B 高于 Qwen3.8 Flash-Next",
)


def _cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def _number(value, digits=3):
    if value is None or not math.isfinite(float(value)):
        return "—"
    return f"{float(value):.{digits}f}"


def _table(lines, headers, rows):
    lines += ["| " + " | ".join(map(_cell, headers)) + " |",
              "| " + " | ".join("---" for _ in headers) + " |"]
    lines += ["| " + " | ".join(map(_cell, row)) + " |" for row in rows]
    lines.append("")


def _lookup(rows):
    return {row["slug"]: row for row in rows}


def _audit(result, common=False):
    key = "common_preference_audit" if common else "preference_audit"
    return result.get(key, result.get("common_audit" if common else "audit", {}))


def _passed(result, common=False):
    audit = _audit(result, common)
    return sum(bool(check.get("passed")) for check in audit.get("checks", []))


def _rank(row, top30=False):
    if row is None:
        return "未入榜"
    rank = int(row["rank"])
    return f"—（#{rank}）" if top30 and rank > 30 else str(rank)


def _terminal(source):
    return {
        base.LATEST_TB: "v4.0 实测", base.OLD_TB[0]: "v2.1 换算×0.95",
        base.OLD_TB[1]: "Hard 换算×0.90", "missing": "缺测",
    }.get(source, source or "缺测")


def _name(slug, lookup):
    return lookup.get(slug, {}).get("model", TARGET_NAMES.get(slug, slug))


def _missing_counts(rows):
    counts = Counter(int(row["missing_core_count"]) for row in rows)
    return "／".join(str(counts[n]) for n in range(4))


def _filtered(metadata):
    return metadata.get("selection_mode") == "preference_filtered"


def _labels(metadata):
    return tuple(metadata.get("preference_labels", PREFERENCE_LABELS))


def _targets(metadata):
    return tuple(metadata.get("preference_targets", preferences.TARGETS))


def _v4_only(metadata):
    return metadata.get("terminal_mode") == "v4_only"


def _terminal_rule(metadata):
    if _v4_only(metadata):
        return ("Terminal 只使用同一固定配置的 v4.0 实测；v4 无成绩即记缺项，实测 0 仍是有效观测。"
                "v2.1 和 Hard 均不用于 Core、回退或扩展，也不借用同模型其他配置的成绩。")
    return ("Terminal 只用同一配置：优先 v4.0 实测；无 v4 时，v2.1 先通过重叠代表配置的非负斜率线性回归换算到 v4 尺度，再乘 0.95；"
            "仍不可用时，Hard 换算后乘 0.90。换算成功算一个 Core 可用。v4 实测 0 不回退，也不借其他配置的成绩。拟合少于五对时停用相应换算。")


def _user_exclusion_lines(metadata):
    exclusions = metadata.get("user_exclusions", [])
    if not exclusions:
        return []
    lines = ["### 本轮指定排除", "",
             "旧 Gemini 3 Flash 模型组按本轮要求整体排除，下面列出被移出的配置。Gemini 3.8 Flash 继续保留，并用于与 Kimi K3 的排序比较。指定排除在 Core 缺测筛选之前执行，不计入各方案缺测剔除人数。", ""]
    _table(lines, ("模型／配置", "slug", "模型组", "原因"), (
        (row.get("model", row.get("slug", "—")), row.get("slug", "—"), row.get("variant_group", "—"),
         "用户指定剔除旧型号" if row.get("reason") == "user_excluded_legacy_model" else row.get("reason", "用户指定排除"))
        for row in exclusions))
    return lines


def _margin_threshold(metadata):
    return metadata.get("minimum_preference_margin", metadata.get("preference_min_margin", preferences.MIN_MARGIN))


def _minimum_margin(result, common=False):
    audit = _audit(result, common)
    margins = [check.get("margin") for check in audit.get("checks", []) if check.get("margin") is not None]
    return audit.get("minimum_margin", min(margins) if margins else None)


def _sensitivity_label(result):
    sensitivity = result.get("sensitivity", {})
    if isinstance(sensitivity, dict):
        return f"{sensitivity.get('passing', sensitivity.get('passed', '—'))}／{sensitivity.get('total', 20)}"
    return f"{sensitivity}／20"


def _weight_description(variant):
    return "、".join(f"{base.BOARD_LABELS[board]} {weight:g}%" for board, weight in zip(BOARDS, variant["weights"]))


def _weight_interpretation(variant):
    above = [f"{base.BOARD_LABELS[board]}（+{weight - 20:g} 个百分点）"
             for board, weight in zip(BOARDS, variant["weights"]) if weight > 20]
    below = [f"{base.BOARD_LABELS[board]}（{weight - 20:g} 个百分点）"
             for board, weight in zip(BOARDS, variant["weights"]) if weight < 20]
    if not above:
        return "本方案领域权重恰为等权，各领域对总分的影响相同。"
    return ("以每领域 20% 作为比较参照，本套提高" + "、".join(above) + "，降低" + "、".join(below)
            + "。提高权重会同时放大该领域的基础成绩、缺一项损失及封顶后的扩展影响；不会改变缺测剔除门槛。")


def _selection_audit(lines, variants, results, metadata):
    margin = _margin_threshold(metadata)
    labels = _labels(metadata)
    count = len(labels)
    lines += ["## 先筛选，再展示", "",
              f"以下 {count} 条是本轮筛选标准；候选方案在各自全量合格人群和最终所有方案的共同入榜人群中，都须 {count} 条全过，才会进入本文。所有目标模型必须入榜。", ""]
    lines += [f"{index}. {label}。" for index, label in enumerate(labels, 1)]
    lines += ["", f"以上名次／高低关系均须成立，且审计分差严格大于 **{margin:g} 分**。第一名与第二名条件的分差分别对照其下一名；其余条件直接比较指定两模型。", "",
              "筛选会使用这些模型的已知表现来选择 Core 组合和领域权重，因此满足偏好是入选条件，不能作为模型能力得到独立验证的证据。每个候选对所有模型采用同一套领域权重，领域内两项始终各占基础分一半。", ""]
    search = metadata.get("search", {})
    if search:
        lines += ["### 候选搜索记录", ""]
        if search.get("range_change_reason"):
            lines += ["**本轮权重范围调整：**" + search["range_change_reason"] + "。", ""]
        search_rows = []
        labels = {"narrow": "较窄权重范围", "expanded": "扩展权重范围", "checked": "检查数量", "passing": "通过数量",
                  "passed": "通过数量", "total": "候选总数", "strategy": "选择策略", "selection_strategy": "选择策略",
                  "weights": "权重", "weight_range": "权重搜索范围", "weight_ranges": "权重搜索范围", "range": "范围",
                  "step": "搜索步长", "min": "最小值", "max": "最大值", "core_combinations": "候选 Core 结构数",
                  "eligible_core_combinations": "可参与权重搜索的 Core 结构数", "skipped_core_combinations": "跳过的 Core 结构数",
                  "evaluated_core_weight_combinations": "实际检查的 Core／权重组合数", "passing_combinations": "全量筛选通过的 Core／权重组合数",
                  "distinct_core_combinations": "全量筛选通过的不同 Core 结构数", "weight_min": "各领域权重下限（%）",
                  "weight_max": "各领域权重上限（%）", "weight_step": "权重步长（百分点）",
                  "minimum_population": "方案最低入榜模型数", "minimum_margin": "严格最小分差（分）",
                  "valid_core_combinations": "家族不重复的有效 Core 结构数", "weight_vectors": "每个可搜索结构的权重组合数",
                  "weight_grid_percent": "权重搜索约束", "coarse_5pp_passing_combinations": "其中落在原 5 个百分点网格的通过数",
                  "core_options": "各领域 Core 候选", "selected_count": "最终入选方案数",
                  "selected_core_groups": "最终入选 Core 结构数", "selection_method": "选择策略",
                  "previous_range_search": "原权重范围检验", "range_change_reason": "权重范围调整原因",
                  **base.BOARD_LABELS}
        def append_search(prefix, value, source_key=None):
            if isinstance(value, dict):
                for child, item in value.items():
                    append_search(f"{prefix}／{labels.get(child, child)}" if prefix else labels.get(child, child), item, child)
            elif isinstance(value, (list, tuple)):
                if source_key in ("weight_range", "range") and len(value) == 2:
                    display = f"{value[0]:g}%–{value[1]:g}%"
                elif value and all(isinstance(item, (list, tuple)) for item in value):
                    display = "；".join("＋".join(str(part) for part in item) for item in value)
                else:
                    display = "；".join(str(item) for item in value)
                search_rows.append((prefix, display))
            else:
                search_rows.append((prefix, value))
        append_search("", search)
        _table(lines, ("项目", "本次记录"), search_rows)
    lines += ["### 入选方案筛选审计", "",
              f"最小分差取 {count} 条审计分差的最小值。敏感性检查固定本方案全量人群及扩展拟合，将任意一个领域减 1 个百分点、另一个领域加 1 个百分点，共 20 种有向调整；两项仍平分该领域权重。"
              f"这 20 次包括越过原搜索边界的压力测试，不因越界而跳过。通过数反映这些小幅改权重后仍满足 {count} 条偏好的次数，并不保证未来数据更新后的次序。", ""]
    _table(lines, ("方案", f"全量 {count} 条", "全量最小分差", f"共同集合 {count} 条", "共同集合最小分差", "±1个百分点检查通过数"), (
        (f"[{variant['label']}](#{key})", f"{_passed(results[key])}／{count}", _number(_minimum_margin(results[key])),
         f"{_passed(results[key], True)}／{count}", _number(_minimum_margin(results[key], True)), _sensitivity_label(results[key]))
        for key, variant in variants.items()))


def _worked_example(lines, result, filtered=False):
    rows = result["rows"]
    if not rows:
        return
    row = _lookup(rows).get(preferences.TARGETS[0], rows[0])
    explanation = ("下表直接读取本方案的分项结果。“基础总分贡献”已经乘本方案所在领域权重的一半；“领域最终总分贡献”已经计入扩展、领域封顶和本方案领域权重。"
                   if filtered else "下表直接读取本方案的分项结果。“基础总分贡献”已经乘所在领域权重的一半（本轮均为 10%）；“领域最终总分贡献”已经计入扩展、领域封顶和 20% 权重。")
    lines += [f"**实际算例：{row['model']}（本方案第 {row['rank']} 名）**", "", explanation, ""]
    example_rows = []
    for board in BOARDS:
        adjusted = [row[f"{board}_item{slot}_adjusted"] for slot in (1, 2)]
        labels = [f"{row[f'{board}_item{slot}']}：" + ("缺测" if adjusted[slot - 1] is None else _number(adjusted[slot - 1]))
                  for slot in (1, 2)]
        example_rows.append((base.BOARD_LABELS[board], labels[0], _number(row[f"{board}_item1_base_points"]),
                             labels[1], _number(row[f"{board}_item2_base_points"]), _number(row[board + "_core"]),
                             _number(row[board + "_bonus"]), _number(row[board + "_points"])))
    _table(lines, ("领域", "Core 1 调整值", "Core 1 基础总分贡献", "Core 2 调整值", "Core 2 基础总分贡献",
                   "领域基础分", "领域扩展加分", "领域最终总分贡献"), example_rows)
    lines += [f"十项基础贡献合计为 **{_number(row['core_only_score'])}**；五项领域最终贡献合计为 **{_number(row['score'])}**；"
              f"封顶后的扩展净贡献为 **{_number(row['score'] - row['core_only_score'])}**。该配置缺 {row['missing_core_count']} 项，"
              f"Terminal 来源为 {_terminal(row['terminal_source'])}。表内显示三位小数，逐格相加可能出现舍入尾差；精确复算使用 CSV 未舍入值。", ""]


def _filtered_comparison(lines, variants, results, metadata):
    by_margin = max(variants, key=lambda key: _minimum_margin(results[key]))
    by_sensitivity = max(variants, key=lambda key: results[key].get("sensitivity", {}).get("passing", -1))
    sensitivity = results[by_sensitivity].get("sensitivity", {})
    sensitivity_limit = ("它仍未通过全部扰动，不能称为对权重不敏感。"
                         if sensitivity.get("passing", 0) < sensitivity.get("total", 20)
                         else "它通过了这组有限扰动，但不能据此保证其他权重或未来数据下的排序。")
    lines += [f"**指定偏好下的指标对照：**[{variants[by_margin]['label']}](#{by_margin}) 在入选方案中 {len(_labels(metadata))} 项筛选的最小分差最大，为 **{_number(_minimum_margin(results[by_margin]), 4)} 分**。"
              f"[{variants[by_sensitivity]['label']}](#{by_sensitivity}) 的 1 个百分点转移检查通过 **{_sensitivity_label(results[by_sensitivity])}**，在入选方案中通过次数最多；{sensitivity_limit}", "",
              "这些指标仅衡量本次冻结数据下的指定排序关系，未验证全榜合理性。仍需检查未被指定顺序约束的模型，以及旧测试覆盖差异造成的排名优势；不能据此推荐正式综合能力榜。", ""]


def _core_coverage_lines(variants, results):
    affected = []
    for key, variant in variants.items():
        for board, weight in zip(BOARDS, variant["weights"]):
            for slot, item in enumerate(variant["core"][board], 1):
                if item != "AIME 2025":
                    continue
                rows = results[key]["rows"]
                missing = sum(row[f"{board}_item{slot}_adjusted"] is None for row in rows)
                if missing:
                    affected.append((weight / 2, missing, len(rows)))
    if not affected:
        return []
    weights, missing_counts, populations = zip(*affected)
    weight_text = (f"{min(weights):g}%" if min(weights) == max(weights)
                   else f"{min(weights):g}%–{max(weights):g}%")
    missing_text = (f"各套 {populations[0]} 个已入榜模型中有 {missing_counts[0]} 个缺测"
                    if len(set(zip(missing_counts, populations))) == 1
                    else f"各套有 {min(missing_counts)}–{max(missing_counts)} 个已入榜模型缺测")
    return [
        f"**Core 覆盖偏差：**含 AIME 2025 且有缺测的方案中，该项占总分 {weight_text}，"
        f"{missing_text}。缺测的固定份额计零，有高分观测的模型可获得显著排名优势。"
        "通过指定排序条件不能排除这种影响；当前结果须结合分项贡献审阅，不能直接当作已验证的综合能力榜。", "",
    ]


def _observations(lines, variants, results):
    gap_rows = []
    for key in ("dc01", "dc03"):
        if key not in results:
            continue
        lookup = _lookup(results[key]["rows"])
        fable, astra = (lookup.get(slug) for slug in preferences.TARGETS[:2])
        if not fable or not astra:
            continue
        base_gap = fable["core_only_score"] - astra["core_only_score"]
        final_gap = fable["score"] - astra["score"]
        gap_rows.append((variants[key]["label"], f"#{fable['rank']}／#{astra['rank']}",
                         _number(fable["core_only_score"]), _number(astra["core_only_score"]),
                         _number(base_gap), _number(final_gap), _number(final_gap - base_gap)))
    if gap_rows:
        lines += ["**本次数据中的分差与扩展影响：**下表的分差统一为 Fable 5.1 减 GPT-6 Astra；正值表示 Fable 分数较高。“扩展造成的分差变化”已计入领域封顶。它展示第一、第二名附近的结果有多少来自基础分、有多少来自扩展。", ""]
        _table(lines, ("方案", "Fable／Astra 名次", "Fable 基础总分", "Astra 基础总分", "基础分差", "最终分差", "扩展造成的分差变化"), gap_rows)
    coverage_notes = []
    for key in ("dc06", "dc08"):
        if key in results:
            top = results[key]["rows"][:30]
            missing = sum(int(row["missing_core_count"]) > 0 for row in top)
            coverage_notes.append(f"{variants[key]['label']} 的 Top30 中，{missing}/{len(top)} 个模型至少缺一项 Core")
    if "dc10" in results:
        rows = results["dc10"]["rows"]
        counts = Counter(int(row["missing_core_count"]) for row in rows)
        coverage_notes.append(f"{variants['dc10']['label']} 的 {len(rows)} 个入榜模型中，十项完整者 {counts[0]} 个，缺三项者 {counts[3]} 个")
    if coverage_notes:
        lines += ["**本次缺测影响：**" + "；".join(coverage_notes) + "。这些人数是本次结果，应结合基础总分和缺项查看。", ""]


def _audit_table(lines, result, margin_threshold, metadata):
    lookup = _lookup(result["rows"])
    checks = _audit(result).get("checks", [])
    common_checks = _audit(result, True).get("checks", [])
    audit_rows = []
    for i, check in enumerate(checks):
        high, low = lookup.get(check.get("higher")), lookup.get(check.get("lower"))
        actual = f"{_name(check.get('higher'), lookup)} " + (f"#{high['rank']}" if high else "未入榜")
        if low:
            actual += f"；{_name(check['lower'], lookup)} #{low['rank']}"
        if high is None or (i >= 2 and low is None):
            status = "未满足：目标未入榜"
        elif check.get("passed"):
            status = "满足"
        elif (i < 2 and high["rank"] == i + 1 or i >= 2 and high["rank"] < low["rank"]):
            status = f"次序满足，分差未超过 {_number(margin_threshold, 2)}"
        else:
            status = "未满足"
        common_status = ("满足" if common_checks[i].get("passed") else "未满足") if i < len(common_checks) else "未提供"
        labels = _labels(metadata)
        audit_rows.append((check.get("label", labels[i] if i < len(labels) else check.get("condition", "")),
                           actual, _number(check.get("margin")), status, common_status))
    _table(lines, ("本轮筛选标准", "实际名次／比较对象", "前者减后者分差", "全量结果", "共同集合结果"), audit_rows)


def _source_lines(metadata):
    return [
        f"输入快照：{metadata.get('source_generated_at', '见 run.json')}。共 {metadata['input_model_count']} 个配置，"
        f"先按模型组固定最高 variantPriority 配置，得到 {metadata['representative_count']} 个代表配置，再对各方案检查缺测；不会因某方案缺测而改选低档配置。",
        ("原始数据和正式 Scheme 18 不变。这是经过偏好筛选的实验榜；模型名称用于筛选审计，入选方案对全部模型使用统一公式和权重。此前仅比较结构、未通过全部偏好的方案不再作为本轮推荐。"
         if _filtered(metadata) else "原始数据和正式 Scheme 18 不变。这是供选择的实验榜；各方案按同一公式评分，模型名称只用于展示和事后审计。"),
        "输入文件哈希、规则参数和拟合结果见 [run.json](run.json)。全量成绩保留未舍入分数；本文显示三位小数，名次仍按原值确定，完全同分按 slug 排序。",
        "",
    ]


def _write_schemes(output, variants, results, metadata):
    common_count = metadata["common_population"]
    margin_threshold = _margin_threshold(metadata)
    filtered = _filtered(metadata)
    v4_only = _v4_only(metadata)
    labels = _labels(metadata)
    count = len(labels)
    keys = list(variants)
    baseline = variants[keys[0]]
    coverage = {row["benchmark"]: row for row in metadata["coverage"]}
    distinct_cores = len({tuple(tuple(variant["core"][board]) for board in BOARDS) for variant in variants.values()})
    title = f"# {len(variants)} 套通过筛选的双 Core 方案：规则、组合与结果" if filtered else f"# {len(variants)} 套双 Core 方案：规则、组合与结果"
    introduction = (f"本轮先按 {count} 条模型排序标准筛选，只展示全量及共同入榜人群均 {count} 条全过的 **{len(variants)} 套方案**。"
                    f"它们使用 **{distinct_cores} 种不同 Core 结构**，同一结构下可以有多个领域权重版本；方案数量不代表 Core 结构数量。"
                    "五领域权重按方案调整、合计 100%；每领域两个不同测试始终各占领域基础分的一半，每套十个槽位来自十个不同测试家族。"
                    if filtered else f"本轮优先比较不同 Core 组合，并如实报告此前的排序偏好。{len(variants)} 套均为五领域各 20%，每领域两个不同测试；每套十个 Core 槽位来自十个不同测试家族。")
    lines = [title, "", introduction,
             "完整 Top30 和跨方案名次对照另见 [TOP30_COMPARISON.md](TOP30_COMPARISON.md)。", ""]
    lines += _source_lines(metadata)
    lines += _user_exclusion_lines(metadata)
    lines += _core_coverage_lines(variants, results)
    if filtered:
        _selection_audit(lines, variants, results, metadata)
    lines += ["## 全部方案共用的计算规则", "",
        "1. 每领域两个 Core 均缺测，立即剔除；或者十项累计缺测至少四项，也剔除。两条规则取并集。因此入榜者允许缺 0–3 项，但不能集中成某领域全缺。实测 0 是有效观测，不计缺测。",
        ("2. 每个 Core 的调整后成绩固定占所在领域基础分的一半。缺一项时，其半份贡献为 0，另一项仍只占一半；缺测标记保留，不伪造原始零分。领域权重为 w% 时，每个 Core 在基础总分中的权重是 w/2%，最高贡献 w/2 分。"
         if filtered else "2. 每个 Core 的调整后成绩固定占所在领域基础分的一半。缺一项时，其半份贡献为 0，另一项仍只占一半；缺测标记保留，不伪造原始零分。五领域各占总分 20%，所以每个 Core 最多贡献总分 10 分。"),
        "3. 调整后值统一在 0–100 分尺度。百分比项目沿用采集后的百分制；AA-Briefcase、GDPval-AA v2 使用 `clip((Elo−500)/2000×100, 0, 100)`。它们是 Elo 的线性换算，并非成功率，纳入 Core 会增加尺度选择对总分的影响。没有为指定模型单独设置权重或加减分。",
        "4. " + _terminal_rule(metadata),
        "5. 扩展池沿用 Scheme 18 的正残差加分，但移除本方案所有 Core 家族，防止同一个测试换名或换版本重复计分。只有某领域两项 Core 都可用的模型，才能用于该领域扩展拟合和获得加分；缺一项时该领域加分固定为 0。每个扩展至少五个完整观测才拟合，斜率限制为非负。",
        ("6. 每领域先将基础分和扩展加分相加，再封顶 100；总分按各方案领域权重求加权平均。每方案按自己的入榜集合拟合扩展，另在所有方案共同入榜的固定集合重新拟合一次；两个口径均须通过筛选。"
         if filtered else "6. 每领域先将基础分和扩展加分相加，再封顶 100；总分取五领域等权平均。每方案按自己的入榜集合拟合扩展，另在所有方案共同入榜的固定集合重新拟合一次，供比较人群变化的影响。"), "",
        "设 `aᵢ` 为 Core 调整后成绩，`Iᵢ` 表示其是否有观测；`rⱼ=max(0, 扩展实测ⱼ−预测ⱼ)`。", "",
        "```text",
        "领域基础分 B = 0.5 × I₁ × a₁ + 0.5 × I₂ × a₂",
        "上限 C = 全部正残差的均值 + √2 × 总体标准差（无正残差时为 0）",
        "领域加分 E = min(C, ln(1 + Σ(expm1(rⱼ))))，仅两项 Core 都可用时",
        "领域最终分 S = min(100, B + E)",
        ("基础总分 = Σ(w_b × B_b / 100)；最终总分 = Σ(w_b × S_b / 100)，Σw_b = 100"
         if filtered else "基础总分 = Σ(0.2 × B)；最终总分 = Σ(0.2 × S)"),
        ("Terminal 调整值 = 同配置 v4.0 实测；无 v4 即缺项" if v4_only else "旧版 Terminal 调整值 = 折扣 × clip(截距 + 非负斜率 × 旧版实测, 0, 100)"),
        "```", "",
        ("例如两项为 80、60，领域基础分为 70，若该领域权重为 w%，则基础总分贡献为 0.7w 分；若 60 那项缺测，领域基础分变成 40，贡献为 0.4w 分，该领域也不能获得扩展加分。真实的 80、0 同样产生基础分 40，但不计缺测，且可参与扩展拟合及加分。"
         if filtered else "例如两项为 80、60，领域基础分为 70，贡献总分 14；若 60 那项缺测，领域基础分变成 40，贡献总分 8，该领域也不能获得扩展加分。真实的 80、0 同样产生基础分 40，但不计缺测，且可参与扩展拟合及加分。"),
        "缺测会同时影响资格、基础分和该领域能否获得扩展加分，因此不能把实验分数理解成已测项目的平均正确率。", ""]
    if v4_only:
        lines += ["### 本次 Terminal 版本范围", "",
                  "所有方案只启用 Terminal-Bench v4.0。v2.1 与 Hard 保留在原始数据文件中供历史查阅，但不进入本轮 Core、扩展池和回归拟合；本轮不拟合旧版到 v4 的映射。", ""]
    else:
        lines += ["### 本次 Terminal 版本映射", "",
                  "下面的参数由同时具有旧版和 v4 实测的固定代表配置拟合，全部方案共用。MAE 是将回归预测截断到 0–100 后、尚未乘折扣时的样本内平均绝对误差；它来自拟合样本自身，不能当作新模型的误差保证。", ""]
        maps = metadata.get("terminal_maps", {})
        _table(lines, ("旧版本", "是否启用", "重叠配置对数", "截距", "非负斜率", "样本内 MAE", "换算后折扣"), (
            (source, "是" if maps.get(source, {}).get("enabled") else "否", maps.get(source, {}).get("pairs", 0),
             _number(maps.get(source, {}).get("intercept"), 6), _number(maps.get(source, {}).get("slope"), 6),
             _number(maps.get(source, {}).get("in_sample_mae")), factor)
            for source, factor in zip(base.OLD_TB, ("0.95", "0.90"))))
        lines += ["旧版换算值属于样本内回归产生的估算，历史版本与 v4 的任务构成、难度差异可能使个别模型偏离这条映射。精确系数保存在 [run.json](run.json)。", ""]
    lines += [f"## {len(variants)} 套{'入选' if filtered else ''}方案概览", ""]
    summary = []
    for key, variant in variants.items():
        result = results[key]
        first = result["rows"][0]["model"] if result["rows"] else "无人入榜"
        summary.append((f"[{variant['label']}](#{key})", variant["purpose"], len(result["rows"]),
                        len(result["excluded"]), _missing_counts(result["rows"]), first,
                        f"{_passed(result)}/{count}", f"{_passed(result, True)}/{count}"))
    _table(lines, ("方案", "组合目的", "入榜", "缺测剔除", "缺0／1／2／3项人数", "第一名", "筛选标准满足", "共同集合满足"), summary)
    if margin_threshold:
        lines += [f"偏好审计沿用前轮稳健门槛：名次关系成立且分差大于 {margin_threshold:g} 分才记“满足”。若次序成立但分差不足，逐项表会明确标注。", ""]
    else:
        lines += ["偏好审计只检查指定名次和严格高低关系，不额外要求最小安全分差。", ""]
    lines += [f"共同集合含 **{common_count}** 个完全相同的代表配置，各方案在此集合重新拟合扩展。全量比较包含 Core 组合、人群和拟合参数的共同变化；共同集合比较固定了人群，仍保留不同 Core 对基础分、扩展池和拟合的影响。", "",
              "## 数据覆盖清单", "",
              ("以下列出至少 100 个配置有数据、且在本轮允许使用的测试；Terminal 仅列 v4.0 直接观测。" if v4_only else "以下列出至少 100 个配置有数据的测试；Terminal effective 一行是回退合成，其余按直接观测口径统计。")
              + "配置数包含推理档位；模型组数为有任一配置成绩的去重数；固定代表数才对应本轮预先选定配置上的可用数。测试有 100 个配置，不等于十项组合能让这些模型全部入榜。", ""]
    _table(lines, ("测试", "配置数", "模型组数", "固定代表数", "机构数", "说明"), (
        (row["benchmark"], row["configurations"], row["variant_groups"], row.get("fixed_representatives", "—"), row["creators"],
         "v4 优先、旧版换算折扣后的合成槽位，含估算" if row["benchmark"] == base.TB else row.get("note", ""))
        for row in metadata["coverage"] if row["configurations"] >= 100
        and (not v4_only or row["benchmark"] not in (base.TB, *base.OLD_TB))))
    lines += [("Terminal 只有 v4.0 实测能填入该槽位，旧版覆盖不计入本轮可用人数。" if v4_only else "Terminal effective 是按上述回退规则合成的一个槽位；原始各版本的覆盖不能相加。")
              + "兼容别名和同家族指标不重复占 Core。完整清单见 [coverage.csv](coverage.csv)。", ""]
    for key, variant in variants.items():
        result = results[key]
        rows, excluded = result["rows"], result["excluded"]
        calibration = result["calibration"]
        lines += [f'<a id="{key}"></a>', "", f"## {variant['label']}", "",
                  f"**设计目的：**{variant['purpose']}", ""]
        changed = [board for board in BOARDS if tuple(variant["core"][board]) != tuple(baseline["core"][board])]
        if key == keys[0]:
            lines += ["本方案作为本轮对照起点；后续变化以此组合为参照，编号不代表推荐顺序。", ""]
        else:
            if filtered and not changed:
                lines += ["Core 结构与首套相同，本方案比较另一组领域权重。各领域内部仍为 50／50，缺测和扩展规则相同。", ""]
            else:
                lines += ["相对首套方案，调整领域为：" + "、".join(base.BOARD_LABELS[b] for b in changed) + "。其余计算规则相同。", ""]
        if filtered:
            lines += [f"**本套领域权重：**{_weight_description(variant)}。两项 Core 分别获得对应领域权重的一半。",
                      _weight_interpretation(variant), ""]
        core_rows = []
        for board, weight in zip(BOARDS, variant["weights"]):
            pair = variant["core"][board]
            counts = [coverage.get(item, {}).get("fixed_representatives", "见覆盖清单") for item in pair]
            complete = calibration["boards"][board]["complete_core_models"]
            core_rows.append((base.BOARD_LABELS[board], pair[0], pair[1], f"{weight:g}%",
                              f"{weight / 2:g}%／{weight / 2:g}%", f"{counts[0]}／{counts[1]}",
                              f"{complete}／{len(rows) - complete}"))
        _table(lines, ("领域", "Core 1", "Core 2", "领域权重", "两项在基础总分的权重", "固定代表可用数1／2", "入榜者双项完整／缺一"), core_rows)
        for board in BOARDS:
            pair = variant["core"][board]
            lines.append(f"- **{base.BOARD_LABELS[board]}：**" + "；".join(f"{item}：{TEST_NOTES.get(item, '使用采集后的调整成绩')}" for item in pair) + "。")
        lines += ["", f"**取舍与适用性：**{variant['tradeoff']}", "",
                  "本方案每领域基础分均为表中两项调整后值各乘 0.5；任一缺测时固定损失该项的半份贡献，该领域加分归零。十项总缺数和领域全缺门槛仍按共用规则执行。", ""]
        has_empty = lambda row: bool(row.get("empty_boards")) or "board_missing_both" in row.get("reason", "")
        empty_count = sum(has_empty(row) for row in excluded)
        four_count = sum(int(row["missing_core_count"]) >= 4 for row in excluded)
        overlap_count = sum(has_empty(row) and int(row["missing_core_count"]) >= 4 for row in excluded)
        lines += [f"**覆盖与缺测：**{len(rows)} 个模型入榜，{len(excluded)} 个剔除；剔除者中 {empty_count} 个触发领域全缺，{four_count} 个累计缺至少四项，其中 {overlap_count} 个同时触发，不能直接相加。入榜者缺 0／1／2／3 项人数分别为 **{_missing_counts(rows)}**。", ""]
        terminal_counts = Counter(row["terminal_source"] for row in rows)
        terminal_sources = (base.LATEST_TB, "missing") if v4_only else (base.LATEST_TB, *base.OLD_TB, "missing")
        lines += ["入榜者 Terminal 来源：" + "；".join(f"{_terminal(source)} {terminal_counts[source]} 个" for source in terminal_sources)
                  + ("。缺 v4 者仍须满足领域不全缺、总缺少于四项的入榜门槛。" if v4_only else "。旧版换算是估算证据，不能当成 v4 实测。"), "",
                  f"**扩展加分：**本方案动态上限为每领域 **{_number(calibration['cap'])}** 分，再受领域 100 分封顶约束。具体扩展项目和当前可拟合数量如下；所有项目仍受双 Core 完整条件限制。", ""]
        _table(lines, ("领域", "保留的扩展项目", "启用拟合／保留项目数"), (
            (base.BOARD_LABELS[board], "、".join(calibration["boards"][board]["extensions"]) or "无",
             f"{sum(bool(t.get('enabled')) for t in calibration['boards'][board]['trends'])}／{len(calibration['boards'][board]['extensions'])}")
            for board in BOARDS))
        _worked_example(lines, result, filtered)
        lines += [f"**本轮 {count} 条筛选标准审计：**", ""]
        _audit_table(lines, result, margin_threshold, metadata)
        common_rows = result.get("common_rows", [])
        if common_rows:
            top = "、".join(f"#{row['rank']} {row['model']}（{_number(row['score'])}）" for row in common_rows[:3])
            changed_checks = [full.get("label", labels[i] if i < count else full.get("condition", "")) for i, (full, common) in enumerate(zip(_audit(result).get("checks", []), _audit(result, True).get("checks", [])))
                              if bool(full.get("passed")) != bool(common.get("passed"))]
            conclusion = f"共同集合与全量的 {count} 条筛选状态一致。" if not changed_checks else "共同集合使以下偏好状态改变：" + "；".join(changed_checks) + "。"
            lines += [f"**共同集合：**重新拟合后的前三名为 {top}。共同集合满足 {_passed(result, True)}/{count} 条标准，全量满足 {_passed(result)}/{count}。{conclusion}", ""]
        else:
            lines += ["**共同集合：**无人可比较，不能给出固定人群的排名结论。", ""]
        lines += [f"数据：[全量排名](rankings_{key}.csv) · [剔除与缺项](excluded_{key}.csv) · [共同集合排名](common_{key}.csv)。各项调整值、实际基础贡献、每领域基础分及加分都在全量 CSV 中。", ""]
    lines += ["## 如何选择", ""]
    _observations(lines, variants, results)
    lines += [
        (f"以上方案都已通过本轮 {count} 条排序标准。可在合格方案中选择最接近实际使用场景的 Core 结构和领域权重，再对照覆盖、缺测、共同集合与权重敏感性结果；同一结构的多个权重版本主要展示领域取舍。偏好本身参与了筛选，不能把通过筛选当成方案质量或模型能力的独立证据。"
         if filtered else "先选择最接近实际使用场景的 Core 组合，再检查覆盖损失和缺测分布；同时对照共同集合、基础总分和最终分，判断变化是否主要由扩展加分带来。此前偏好的满足数量只是事实对照，不构成方案质量的独立证据。"),
        ("当前扩展回归来自同一份横截面数据" if v4_only else "当前换算和扩展回归来自同一份横截面数据")
        + "，没有跨时间留出验证；新模型加入、成绩更新和 Terminal 版本覆盖变化都可能改变拟合与名次。Elo、通过率、多模态和代码成绩也不具有天然相同的难度尺度。", ""]
    if filtered:
        _filtered_comparison(lines, variants, results, metadata)
    (output / "SCHEMES.md").write_text("\n".join(lines), encoding="utf-8")


def _write_top30(output, variants, results, metadata):
    keys = list(variants)
    filtered = _filtered(metadata)
    v4_only = _v4_only(metadata)
    count = len(_labels(metadata))
    targets = _targets(metadata)
    lookups = {key: _lookup(results[key]["rows"]) for key in keys}
    names = {slug: row["model"] for lookup in lookups.values() for slug, row in lookup.items()}
    union = {row["slug"] for result in results.values() for row in result["rows"] if row["rank"] <= 30}
    def order(slug):
        ranks = [lookup[slug]["rank"] for lookup in lookups.values() if slug in lookup]
        return min(ranks), sum(ranks) / len(ranks), names[slug], slug
    union = sorted(union, key=order)
    title = f"# {len(variants)} 套通过筛选的双 Core 方案 Top30 对比" if filtered else f"# {len(variants)} 套双 Core 方案 Top30 对比"
    common_rules = (("共同规则：五领域权重按方案配置、合计 100%；" if filtered else "共同规则：五领域各 20%；")
                    + "每领域两个不同 Core 各占领域基础分一半。单项缺测的半份贡献为 0；任一领域两项全缺或总缺至少四项时剔除。"
                    + _terminal_rule(metadata)
                    + "扩展加分只适用于双 Core 完整的领域；领域最终分按方案权重加权。")
    lines = [title, "",
        f"本文件独立展示各方案的 Top30、关注模型和名次差异。完整 Core 定义、缺测分布及 {count} 条筛选标准逐项解释见 [SCHEMES.md](SCHEMES.md)。",
        common_rules, ""]
    lines += _source_lines(metadata)
    lines += _user_exclusion_lines(metadata)
    lines += _core_coverage_lines(variants, results)
    if filtered:
        distinct_cores = len({tuple(tuple(variant["core"][board]) for board in BOARDS) for variant in variants.values()})
        lines += [f"本文件只展示本轮 {count} 条筛选标准在全量和共同集合均通过的方案，共 **{len(variants)} 套权重／结构方案、{distinct_cores} 种 Core 结构**。"
                  "筛选使用了既有模型表现，通过偏好不能视为独立能力验证；完整标准、搜索范围和逐项分差见方案说明。",
                  "表中 20 次权重敏感性检查包含越过搜索边界的压力测试。它固定全量人群和拟合参数，仅转移两个领域之间的 1 个百分点。", ""]
        _table(lines, ("方案", "编程权重", "Agent权重", "推理权重", "知识权重", "上下文权重", "全量／共同集合", "±1个百分点通过数"), (
            (f"[{variant['label']}](SCHEMES.md#{key})", *(f"{weight:g}%" for weight in variant["weights"]),
             f"{_passed(results[key])}/{count}／{_passed(results[key], True)}/{count}", _sensitivity_label(results[key]))
            for key, variant in variants.items()))
    lines += ["## 方案与覆盖", ""]
    baseline_top = {row["slug"] for row in results[keys[0]]["rows"][:30]}
    _table(lines, ("方案", "编程", "Agent／工具", "高难推理", "知识／科学", "指令／上下文", "入榜", "与首套Top30重合", "筛选标准满足"), (
        (f"[{variant['label']}](SCHEMES.md#{key})", *("＋".join(variant["core"][board]) for board in BOARDS),
         len(results[key]["rows"]), len(baseline_top & {row["slug"] for row in results[key]["rows"][:30]}), f"{_passed(results[key])}/{count}")
        for key, variant in variants.items()))
    lines += [f"## 关注的 {len(targets)} 个模型", "",
        "这里显示完整榜名次，即使低于第 30 名也保留数字。“未入榜”表示触发本方案缺测门槛。", ""]
    for start in range(0, len(keys), 5):
        group = keys[start:start + 5]
        lines += [f"### 方案 {start + 1}–{start + len(group)}", ""]
        _table(lines, ("模型", *(variants[key]["label"] for key in group)), (
            (names.get(slug, TARGET_NAMES.get(slug, slug)), *(_rank(lookups[key].get(slug)) for key in group))
            for slug in targets))
    lines += ["### 关注模型的名次变化", "",
        "跨度为各方案实际入榜名次的最差减最佳；剔除不换算成一个假定名次。不同方案人群不同，所以跨度是展示差异，不能单独解释为能力变化。", ""]
    target_rows = []
    for slug in targets:
        ranks = {key: lookups[key][slug]["rank"] for key in keys if slug in lookups[key]}
        best, worst = (min(ranks.values()), max(ranks.values())) if ranks else (None, None)
        best_labels = "、".join(variants[key]["label"] for key, rank in ranks.items() if rank == best)
        worst_labels = "、".join(variants[key]["label"] for key, rank in ranks.items() if rank == worst)
        target_rows.append((names.get(slug, TARGET_NAMES.get(slug, slug)), f"#{best}：{best_labels}" if ranks else "—",
                            f"#{worst}：{worst_labels}" if ranks else "—", worst - best if ranks else "—",
                            f"{len(ranks)}／{len(keys)}"))
    _table(lines, ("模型", "最佳名次及方案", "最差名次及方案", "名次跨度", "入榜方案数"), target_rows)
    lines += ["## Top30 并集的跨方案对照", "",
        f"{len(variants)} 套 Top30 共涉及 **{len(union)}** 个模型。按最佳名次、在榜平均名次、模型名依次排列；每五套拆为一表，所有表格行序完全相同。",
        "**数字**表示该方案 Top30 内名次；**—（#名次）**表示已入榜但在 Top30 之外；**未入榜**表示触发缺测门槛。这里不会把掉出 Top30 与资格剔除混为一谈。", ""]
    for start in range(0, len(keys), 5):
        group = keys[start:start + 5]
        lines += [f"### 方案 {start + 1}–{start + len(group)} 的 Top30 并集", ""]
        _table(lines, ("模型", *(variants[key]["label"] for key in group)), (
            (names[slug], *(_rank(lookups[key].get(slug), top30=True) for key in group)) for slug in union))
    lines += ["## 每套方案的完整 Top30", "",
        "“基础总分”是十个 Core 固定份额的合计，未含扩展加分；“最终分”包含按领域封顶后的扩展加分。"
        + ("Terminal 分数仅为 v4.0 实测，缺测以 — 表示。" if v4_only else "Terminal 来源中的换算值不是 v4 实测。")
        + "缺项详情及逐项目贡献可点击各方案 CSV 查看。", ""]
    for key, variant in variants.items():
        rows = results[key]["rows"]
        lines += [f"### {variant['label']}", "",
                  f"入榜 {len(rows)} 个模型；本轮 {count} 条筛选标准满足 {_passed(results[key])}/{count}。"
                  f"[全量排名与分项](rankings_{key}.csv) · [剔除名单](excluded_{key}.csv) · [共同集合](common_{key}.csv)。", ""]
        _table(lines, ("名次", "模型／固定配置", "最终分", "基础总分", "缺Core项数", "Terminal来源", "Terminal v4实测分" if v4_only else "Terminal有效分"), (
            (row["rank"], row["model"], _number(row["score"]), _number(row["core_only_score"]),
             row["missing_core_count"], _terminal(row["terminal_source"]), _number(row.get("terminal_effective"))) for row in rows[:30]))
        if len(rows) < 30:
            lines += [f"本方案只有 {len(rows)} 个合格模型，因此展示全部入榜者。", ""]
    lines += [f"所有方案共同入榜集合为 {metadata['common_population']} 个固定配置；共同集合重算结果见各 `common_*.csv`。本文件的 Top30 均对应各方案全量合格人群，不能与共同集合名次混用。", ""]
    (output / "TOP30_COMPARISON.md").write_text("\n".join(lines), encoding="utf-8")


def write_reports(output: Path, variants: dict, results: dict, metadata: dict):
    """Write explanatory and Top30 reports from the same immutable result rows."""
    if not variants or set(variants) != set(results):
        raise ValueError("Reports require matching nonempty variant and result registries")
    if _filtered(metadata):
        for key, result in results.items():
            for common in (False, True):
                audit = _audit(result, common)
                if not audit.get("passed") or _passed(result, common) != len(_labels(metadata)) or len(audit.get("checks", [])) != len(_labels(metadata)):
                    raise ValueError(f"Filtered report cannot contain a failing candidate: {key}, common={common}")
    if _v4_only(metadata):
        forbidden = {base.TB, *base.OLD_TB}
        excluded_groups = set(metadata.get("excluded_variant_groups", []))
        for key, variant in variants.items():
            result = results[key]
            if any(item in forbidden for pair in variant["core"].values() for item in pair):
                raise ValueError(f"v4-only report cannot contain legacy Terminal Core: {key}")
            for calibration_key in ("calibration", "common_calibration"):
                calibration = result.get(calibration_key, {})
                if any(item in forbidden for board in calibration.get("boards", {}).values()
                       for item in board.get("extensions", [])):
                    raise ValueError(f"v4-only report cannot contain legacy Terminal extension: {key}")
            for row in (*result["rows"], *result.get("common_rows", [])):
                if row.get("terminal_source") not in (base.LATEST_TB, "missing"):
                    raise ValueError(f"v4-only report cannot contain legacy Terminal source: {key}, {row['slug']}")
                if row.get("variant_group") in excluded_groups:
                    raise ValueError(f"Report cannot contain a user-excluded model group: {key}, {row['slug']}")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    _write_schemes(output, variants, results, metadata)
    _write_top30(output, variants, results, metadata)
