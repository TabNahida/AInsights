"""Render screened one/two-Core experiments without changing their scores."""
from __future__ import annotations

from collections import Counter
import math
from pathlib import Path
import re

from analysis.irt_leaderboard_exploration import dual_core_reports as shared
from analysis.irt_leaderboard_exploration import filtered_dual_core_variants as previous

base, dual, BOARDS = previous.base, previous.dual, previous.BOARDS
_table, _number, _lookup = shared._table, shared._number, shared._lookup
_audit, _minimum_margin = shared._audit, shared._minimum_margin
EXTRA_TARGETS = (
    ("gpt-5-mini", "gpt 5 mini", "GPT-5 mini"),
    ("claude-4-5-sonnet-thinking", "claude 4 5 sonnet", "Claude 4.5 Sonnet"),
    ("gemini-3-flash-reasoning", "gemini 3 flash", "Gemini 3 Flash"),
)


def _labels(metadata):
    return tuple(metadata.get("preference_labels", previous.CURRENT_LABELS))


def _targets(metadata):
    return tuple(metadata.get("preference_targets", metadata.get("targets", previous.CURRENT_TARGETS)))


def _threshold(metadata):
    return metadata.get("minimum_preference_margin", metadata.get("preference_min_margin", previous.preferences.MIN_MARGIN))


def _passed(result, common=False):
    return sum(bool(check.get("passed")) for check in _audit(result, common).get("checks", []))


def _core_signature(variant):
    return tuple(tuple(variant["core"][board]) for board in BOARDS)


def _counts(variant):
    singles = sum(len(variant["core"][board]) == 1 for board in BOARDS)
    return singles, len(BOARDS) - singles, sum(map(len, variant["core"].values()))


def _source(lines, metadata):
    lines += [
        f"输入快照：**{metadata.get('source_generated_at', '见 run.json')}**；"
        f"{metadata.get('input_model_count', '见 run.json')} 个配置，"
        f"预先固定 {metadata.get('representative_count', '见 run.json')} 个模型组代表配置。"
        "按 variantPriority、再按 slug 选择代表，先选配置，再检查资格；不因缺测更换档位，也不借同模型其他配置的成绩。",
        "这是实验方案，正式 Scheme 18、网站和日常 Action 未切换。原始输入未改分，"
        "模型名称只参与候选排序筛选，对所有模型应用相同公式与方案权重。"
        "完整输入哈希、参数和拟合结果见 [run.json](run.json)，搜索范围与选择过程见 [SEARCH_REPORT.md](SEARCH_REPORT.md)。",
        "名次按未舍入最终分降序、再按 slug 排序；表中保留三位小数，显示分数相同不代表原值相同。", "",
    ]


def _rules(lines, metadata):
    lines += ["## 共同规则", "",
        "1. 每领域配置一个或两个 Core，同一测试家族不能在任何领域重复占位。单 Core 占领域基础分 100%；双 Core 各占 50%。这次只调整 Core 数量与组合，扩展加分算法沿用此前规则。",
        "2. 某领域全部已配置 Core 缺测，或全部已配置 Core 累计缺测至少四项，均剔除。未配置的第二项不是缺测。单 Core 领域缺唯一项目即触发领域全缺；双 Core 缺一项仍损失固定半份，不能把另一项放大补足。实测 0 是有效观测。",
        "3. AIME、LiveCodeBench、GPQA 及其别名不进入 Core；HMMT、MATH-500、GSM8K 等同类竞赛／旧题测试也不用于替代。它们是否作为扩展仍按既有扩展注册表处理，移出 Core 不等于取消全部影响。",
        "4. Terminal 仅使用固定配置的 v4.0 实测；无 v4 即缺测，不启用 v2.1、Hard、旧版回退或版本回归，旧 Terminal 也不进入扩展。v4 实测 0 不回退。",
        "5. Core 调整值采用 0–100 尺度。百分比项目使用采集后的百分制；AA-Briefcase、GDPval-AA v2 使用 `clip((Elo−500)/2000×100, 0, 100)`。Elo 换算分不是通过率，不同测试也没有天然一致的难度尺度。",
        "6. 所有 Core 家族从全部领域的扩展池移除，避免重复计分。只有领域全部已配置 Core 有观测的模型，才能参与该领域扩展拟合并获得加分；每个扩展至少五个完整观测才拟合，回归斜率非负。双 Core 缺一项的领域扩展固定为 0。",
        "7. 各领域权重在 9%–40% 之间，以 1 个百分点搜索，合计 100%。基础分加扩展后按领域封顶 100，再按该方案权重加权；没有模型专属权重或惩罚。",
        "8. 每套先在自己的合格人群上拟合扩展；再在最终入选方案共同入榜的固定人群上重新拟合、重新排名。两个口径都必须通过全部排序条件。", "",
        "设领域配置数为 `k∈{1,2}`，`aᵢ` 为调整后成绩，`Iᵢ` 表示是否有观测；`w` 为领域百分比权重，`rⱼ=max(0, 扩展实测ⱼ−预测ⱼ)`。", "",
        "```text",
        "领域基础分 B = Σ(Iᵢ × aᵢ) / k",
        "每个 Core 的基础总分贡献 = Iᵢ × aᵢ × w / (100 × k)",
        "扩展上限 C = 全部正残差的均值 + √2 × 总体标准差（无正残差时为 0）",
        "领域扩展 E = min(C, ln(1 + Σexpm1(rⱼ)))，仅该领域全部已配置 Core 有观测时",
        "领域最终分 S = min(100, B + E)",
        "基础总分 = Σ(w_b × B_b / 100)；最终总分 = Σ(w_b × S_b / 100)",
        "```", "",
        "例如权重 20% 的单 Core 得 80 分，贡献基础总分 16 分；双 Core 为 80、60 时，分别贡献 8、6 分。"
        "若双 Core 的第二项缺测，贡献变为 8、0 分并停用该领域扩展；若它是真实 0，则贡献也为 8、0 分，"
        "但不是缺测，仍可拟合及获得扩展。单 Core 的唯一项缺测时，模型直接失去本套资格。", "",
        "**单 Core 的实际取舍：**去掉覆盖较差的第二项，可以消除该项固定半份计零的影响；"
        "但保留项目的总分权重翻倍，该测试的覆盖、尺度、测评误差会更直接地支配领域。"
        "同时失去两项互相补充的证据，原本只测了被删项目的模型还会因领域全缺而被剔除，因此不保证入榜人数增加。"
        "Core 数变化也会改变完整样本、扩展池、拟合参数与动态上限；这不只是机械地删掉一列分数。", "",
    ]


def _selection(lines, variants, results, metadata):
    labels, threshold = _labels(metadata), _threshold(metadata)
    lines += ["## 先筛选，再展示", "",
        f"本轮保留以下 {len(labels)} 条筛选条件，目标模型必须入榜，所有审计分差严格大于 **{threshold:g} 分**。"
        "第一、第二名检查覆盖整个合格榜，不能只在指定模型中相互比较。", ""]
    lines += [f"{i}. {label}。" for i, label in enumerate(labels, 1)]
    lines += ["", "这些模型的已知成绩参与了 Core 组合和权重选择，满足条件是候选入选标准，"
        "不是模型能力或全榜合理性的独立验证。下方保留旧模型的正常资格与实际名次，"
        "用于检查未被指定次序约束的结果；不会为使其靠后再施加人工排除或扣分。", ""]
    search = metadata.get("search", {})
    fields = (
        ("structures_considered", "检查的 Core 结构"),
        ("valid_core_structures", "家族不重复的有效结构"),
        ("evaluated_core_structures", "进入权重筛选的结构"),
        ("weight_vectors", "每结构的权重向量"),
        ("evaluated_core_weight_combinations", "检查的 Core／权重组合"),
        ("passing_combinations", "全量筛选合格组合"),
        ("distinct_core_combinations", "全量合格的不同 Core 结构"),
        ("minimum_population", "最低合格模型数"),
        ("minimum_item_coverage", "每 Core 最低固定代表覆盖"),
        ("selected_count", "最终选择方案数"),
    )
    recorded = [(label, search[key]) for key, label in fields if key in search]
    if recorded:
        _table(lines, ("搜索记录", "结果"), recorded)
    lines += ["权重敏感性检查固定全量人群和拟合参数，将一个领域减 1 个百分点、另一个加 1 个百分点，"
        "共 20 个有向转移，包含越过搜索边界的压力检查。通过次数只说明这组有限扰动下的指定排序，不能保证未来成绩更新后的稳定性。", ""]
    _table(lines, ("方案", "单／双 Core 领域数", "全量／共同集合通过", "全量最小分差", "共同集合最小分差", "±1个百分点通过数"), (
        (f"[{v['label']}](#{key})", f"{_counts(v)[0]}／{_counts(v)[1]}",
         f"{_passed(results[key])}/{len(labels)}／{_passed(results[key], True)}/{len(labels)}",
         _number(_minimum_margin(results[key])), _number(_minimum_margin(results[key], True)),
         shared._sensitivity_label(results[key])) for key, v in variants.items()))


def _audit_table(lines, result, metadata):
    lookup, common_lookup = _lookup(result["rows"]), _lookup(result["common_rows"])
    table = []
    for i, (check, common) in enumerate(zip(_audit(result)["checks"], _audit(result, True)["checks"])):
        def actual(item, source):
            high, low = source.get(item.get("higher")), source.get(item.get("lower"))
            return "；".join(f"{row['model']} #{row['rank']}" for row in (high, low) if row) or "目标未入榜"
        table.append((check.get("label", _labels(metadata)[i]), actual(check, lookup),
                      _number(check.get("margin")), actual(common, common_lookup),
                      _number(common.get("margin")), "两种口径均通过"))
    _table(lines, ("条件", "全量实际名次／比较对象", "全量分差", "共同集合实际名次／比较对象", "共同集合分差", "状态"), table)


def _example(lines, variant, result, metadata):
    row = _lookup(result["rows"]).get(_targets(metadata)[0], result["rows"][0])
    lines += [f"**实际算例：{row['model']}，本套第 {row['rank']} 名**", "",
        "每行是一个已配置 Core，基础总分贡献已经乘领域权重并除以本领域 Core 数；未配置项不显示。", ""]
    cells = []
    for board, weight in zip(BOARDS, variant["weights"]):
        items = variant["core"][board]
        for slot, item in enumerate(items, 1):
            value = row[f"{board}_item{slot}_adjusted"]
            cells.append((base.BOARD_LABELS[board], item, _number(value), f"{weight / len(items):g}%",
                          _number(row[f"{board}_item{slot}_base_points"])))
    _table(lines, ("领域", "已配置 Core", "调整后成绩", "基础总分权重", "基础总分贡献"), cells)
    _table(lines, ("领域", "Core数量", "领域基础分", "领域扩展加分", "领域最终分", "最终总分贡献"), (
        (base.BOARD_LABELS[board], len(variant["core"][board]), _number(row[board + "_core"]),
         _number(row[board + "_bonus"]), _number(row[board + "_score"]), _number(row[board + "_points"]))
        for board in BOARDS))
    lines += [f"{_counts(variant)[2]} 项基础贡献合计 **{_number(row['core_only_score'])} 分**；"
        f"最终合计 **{_number(row['score'])} 分**；计入领域封顶后的扩展净贡献 **{_number(row['score'] - row['core_only_score'])} 分**。"
        f"该配置缺 {row['missing_core_count']} 项。三位小数逐格相加可能有舍入尾差，精确分项见 CSV。", ""]


def _all_rows(results):
    return {row["slug"]: row for result in results.values() for row in (*result["rows"], *result.get("excluded", []))}


def _watch_targets(results, metadata):
    """Use the already fixed representatives; never select a new config here."""
    all_rows = _all_rows(results)
    targets = list(_targets(metadata))
    names = {slug: row["model"] for slug, row in all_rows.items()}
    for expected, group, label in EXTRA_TARGETS:
        matches = [slug for slug, row in all_rows.items() if row.get("variant_group", row.get("variantGroup")) == group]
        slug = expected if expected in all_rows or not matches else sorted(matches)[0]
        if slug not in targets:
            targets.append(slug)
        names.setdefault(slug, label)
    return targets, names


def _missing_text(row):
    missing = row.get("missing_core_items", "")
    return "、".join(missing) if isinstance(missing, (list, tuple)) else str(missing or "无")


def _excluded_reason(row):
    empty = row.get("empty_boards", "")
    boards = empty if isinstance(empty, (list, tuple)) else [s.strip() for s in str(empty).split(";") if s.strip()]
    parts = ["领域全缺：" + "、".join(base.BOARD_LABELS.get(b, b) for b in boards)] if boards else []
    if int(row.get("missing_core_count", 0)) >= 4:
        parts.append("累计缺至少四项")
    return "；".join(parts) or str(row.get("reason", "见剔除 CSV"))


def _legacy_table(lines, variant, result, results, metadata):
    _, names = _watch_targets(results, metadata)
    rows, excluded = _lookup(result["rows"]), _lookup(result.get("excluded", []))
    all_rows = _all_rows(results)
    data = []
    for expected, group, label in EXTRA_TARGETS:
        matches = [slug for slug, row in all_rows.items() if row.get("variant_group", row.get("variantGroup")) == group]
        slug = expected if expected in all_rows or not matches else sorted(matches)[0]
        row = rows.get(slug)
        if row:
            data.append((names.get(slug, label), f"#{row['rank']}", _number(row["score"]),
                         _number(row["core_only_score"]), row["missing_core_count"], _missing_text(row), "正常入榜"))
        elif slug in excluded:
            row = excluded[slug]
            data.append((names.get(slug, label), "未入榜", "—", "—", row["missing_core_count"],
                         _missing_text(row), _excluded_reason(row)))
        else:
            data.append((names.get(slug, label), "快照无此代表", "—", "—", "—", "—", "未作资格判断"))
    lines += ["**此前排名异常涉及的旧模型：**以下完全按本套配置和缺测门槛处理。Gemini 3 Flash 没有人工排除；"
        "如未入榜，表中列出本套实际触发条件。此处名次不是额外筛选条件。", ""]
    _table(lines, ("模型", "名次", "最终分", "基础总分", "缺Core数", "缺项", "资格原因"), data)


def _write_schemes(output, variants, results, metadata):
    lines = [f"# {len(variants)} 套通过筛选的单／双 Core 方案", "",
        (f"本轮固定 **{metadata['search']['single_core_domains_requested']} 个单 Core 领域**，其余领域各用两个 Core。"
         if metadata.get("search", {}).get("single_core_domains_requested") else "本轮允许每领域一个或两个 Core。")
        + f"以下 **{len(variants)} 套方案**使用 "
        f"**{len({_core_signature(v) for v in variants.values()})} 种 Core 结构**，"
        "均通过全量及共同集合的全部筛选条件；同一结构的不同权重版本不算新的结构。",
        "独立的完整 Top30、关注模型与跨方案名次对比见 [TOP30_COMPARISON.md](TOP30_COMPARISON.md)。", ""]
    _source(lines, metadata)
    _rules(lines, metadata)
    _selection(lines, variants, results, metadata)
    lines += [f"所有入选方案共同入榜集合为 **{metadata.get('common_population', len(next(iter(results.values()))['common_rows']))}** 个固定配置。"
        "共同集合会重新拟合扩展；它控制了人群变化，但仍保留 Core 组合、扩展池与权重的差异。", ""]
    baseline = next(iter(variants.values()))
    coverage = {row["benchmark"]: row for row in metadata.get("coverage", [])}
    for key, variant in variants.items():
        result = results[key]
        rows, excluded, calibration = result["rows"], result.get("excluded", []), result["calibration"]
        singles, doubles, total = _counts(variant)
        lines += [f'<a id="{key}"></a>', "", f"## {variant['label']}", "",
            f"**设计目的：**{variant.get('purpose', '比较本 Core 组合和领域权重。')}", "",
            f"本套有 {singles} 个单 Core 领域、{doubles} 个双 Core 领域，共 {total} 项。"
            f"单 Core 领域都必须有观测，因此本套合格者最多可缺 **{min(3, doubles)} 项**，"
            "且缺项必须分散在不同双 Core 领域。累计缺至少四项规则继续保留。", ""]
        changed = [b for b in BOARDS if tuple(variant["core"][b]) != tuple(baseline["core"][b])]
        if variant is baseline:
            lines += ["本套作为组合对照起点，方案编号不代表推荐先后。", ""]
        elif changed:
            lines += ["相对首套更换 Core 的领域：" + "、".join(base.BOARD_LABELS[b] for b in changed) + "。", ""]
        else:
            lines += ["Core 与首套相同，本套比较另一组领域权重。", ""]
        cells = []
        for board, weight in zip(BOARDS, variant["weights"]):
            items = variant["core"][board]
            for item in items:
                cells.append((base.BOARD_LABELS[board], "单 Core" if len(items) == 1 else "双 Core", item,
                              f"{weight:g}%", f"{weight / len(items):g}%", f"{weight / len(items):g} 分",
                              coverage.get(item, {}).get("fixed_representatives", "见覆盖审计")))
        _table(lines, ("领域", "结构", "Core项目", "领域权重", "单项基础总分权重", "单项最高基础贡献", "固定代表可用数"), cells)
        for board in BOARDS:
            lines.append(f"- **{base.BOARD_LABELS[board]}：**" + "；".join(
                f"{item}：{shared.TEST_NOTES.get(item, '使用采集后的调整成绩')}" for item in variant["core"][board]) + "。")
        largest = max((weight / len(variant["core"][b]), item)
                      for b, weight in zip(BOARDS, variant["weights"]) for item in variant["core"][b])
        lines += ["", "**领域权重取舍：**" + shared._weight_interpretation(variant), "",
            f"**单项集中度：**本套最高单项基础权重为 **{largest[0]:g}%**（{largest[1]}；如有并列，仅列一项）。"
            "这也等于该项对基础总分的最高分数贡献；实际贡献须乘该模型调整成绩／100。",
            f"**组合取舍：**{variant.get('tradeoff', '单项结构的证据范围较窄，双项结构仍可能受到单缺计零的影响。')}", ""]
        empty = lambda row: bool(row.get("empty_boards")) or "board_missing" in str(row.get("reason", ""))
        empty_count = sum(empty(row) for row in excluded)
        four_count = sum(int(row.get("missing_core_count", 0)) >= 4 for row in excluded)
        overlap = sum(empty(row) and int(row.get("missing_core_count", 0)) >= 4 for row in excluded)
        distribution = Counter(int(row["missing_core_count"]) for row in rows)
        lines += [f"**覆盖与缺测：**入榜 {len(rows)} 个，剔除 {len(excluded)} 个；剔除中领域全缺 {empty_count} 个、"
            f"累计缺至少四项 {four_count} 个、两者重叠 {overlap} 个，不能将两种原因直接相加。"
            f"入榜者缺 0／1／2／3 项人数为 **{'／'.join(str(distribution[n]) for n in range(4))}**。", ""]
        _table(lines, ("领域", "入榜者Core完整／不完整", "保留扩展项目", "启用拟合／保留数"), (
            (base.BOARD_LABELS[b], f"{calibration['boards'][b]['complete_core_models']}／{len(rows) - calibration['boards'][b]['complete_core_models']}",
             "、".join(calibration["boards"][b]["extensions"]) or "无",
             f"{sum(bool(t.get('enabled')) for t in calibration['boards'][b]['trends'])}／{len(calibration['boards'][b]['extensions'])}")
            for b in BOARDS))
        lines += [f"本套全量拟合的领域扩展上限为 **{_number(calibration['cap'])} 分**；共同集合重新拟合后为 "
            f"**{_number(result['common_calibration']['cap'])} 分**。实际净贡献还受领域 100 分封顶及领域权重限制。", ""]
        _example(lines, variant, result, metadata)
        lines += [f"**{len(_labels(metadata))} 条条件的逐项审计：**", ""]
        _audit_table(lines, result, metadata)
        _legacy_table(lines, variant, result, results, metadata)
        lines += [f"数据：[全量排名与分项](rankings_{key}.csv) · [剔除与缺项](excluded_{key}.csv) · [共同集合重算](common_{key}.csv)。", ""]
    lines += ["## 如何判断这些结果", "",
        "先比较 Core 的任务含义、单项集中度和覆盖，再比较权重与扩展贡献。"
        "减少 Core 数可以缓解不必要的旧测试缺测惩罚，却不会自动消除覆盖偏差或测试可刷分问题。"
        "测试在本轮获准进入 Core，也不表示已经获得独立防污染或抗刷分验证。",
        "这些组合是在同一份冻结成绩上按指定次序筛选的，没有跨时间留出验证；"
        "共同集合和小幅权重扰动也不能替代新数据验证。正式采用前，应检查全榜表现和后续快照，"
        "尤其关注单 Core 高权重测试及缺测引起的资格变化。", ""]
    (output / "SCHEMES.md").write_text("\n".join(lines), encoding="utf-8")


def _write_top30(output, variants, results, metadata):
    keys = list(variants)
    lookups = {key: _lookup(results[key]["rows"]) for key in keys}
    targets, names = _watch_targets(results, metadata)
    lines = [f"# {len(variants)} 套通过筛选的单／双 Core 方案 Top30 对比", "",
        "本文件独立展示每套完整 Top30、指定模型及此前异常旧模型的实际名次，并提供 Top30 并集对照。"
        "完整计分解释、每 Core 权重、缺测审计与实际算例见 [SCHEMES.md](SCHEMES.md)。", "",
        "共同规则：单 Core 占所在领域基础分 100%，双 Core 各占 50%；某领域全部已配置 Core 缺测或累计缺至少四项则剔除。"
        "未配置第二项不算缺测，实测 0 算观测。Terminal 仅 v4；AIME、LiveCodeBench、GPQA 不进入 Core。"
        "扩展仅对 Core 完整领域拟合及加分；五领域权重各在 9%–40%、合计 100%。", "",
        f"全部方案已在全量和共同集合通过 {len(_labels(metadata))} 条排序条件，分差均严格大于 {_threshold(metadata):g} 分。"
        "这些条件参与候选选择，不能视作独立能力验证。单 Core 减少测试覆盖面的同时提高单项影响，"
        "通过偏好也不能排除全榜的覆盖偏差。", ""]
    _source(lines, metadata)
    lines += ["## 方案结构与权重", ""]
    _table(lines, ("方案", *(base.BOARD_LABELS[b] for b in BOARDS), "Core总数", "入榜", "±1个百分点通过数"), (
        (f"[{v['label']}](SCHEMES.md#{key})", *("＋".join(v["core"][b]) + f"（{w:g}%）" for b, w in zip(BOARDS, v["weights"])),
         _counts(v)[2], len(results[key]["rows"]), shared._sensitivity_label(results[key])) for key, v in variants.items()))
    lines += ["## 关注模型的完整榜名次", "",
        "显示实际完整榜名次，低于第 30 名也保留数字。“未入榜”表示本套缺测门槛剔除，"
        "具体缺项见方案说明和 excluded CSV；快照中没有对应代表时单独标明。"
        "Gemini 3 Flash 不做人为排除，mini、Sonnet 的位置也没有额外约束。", ""]
    all_rows = _all_rows(results)
    for start in range(0, len(keys), 5):
        group = keys[start:start + 5]
        lines += [f"### 方案 {start + 1}–{start + len(group)}", ""]
        _table(lines, ("模型／固定代表", *(variants[k]["label"] for k in group)), (
            (names.get(slug, slug), *(shared._rank(lookups[k].get(slug)) if slug in all_rows else "快照无此代表" for k in group))
            for slug in targets))
    target_rows = []
    for slug in targets:
        ranks = [lookup[slug]["rank"] for lookup in lookups.values() if slug in lookup]
        target_rows.append((names.get(slug, slug), min(ranks) if ranks else "—", max(ranks) if ranks else "—",
                            max(ranks) - min(ranks) if ranks else "—", f"{len(ranks)}／{len(keys)}"))
    lines += ["### 名次跨度", "", "跨度只计算实际入榜名次，不把剔除换算成虚构名次。各方案人群可能不同，名次差不能直接解释为能力变化。", ""]
    _table(lines, ("模型", "最佳名次", "最差名次", "跨度", "入榜方案数"), target_rows)
    union = {row["slug"] for result in results.values() for row in result["rows"][:30]}
    union = sorted(union, key=lambda slug: (min(lookup[slug]["rank"] for lookup in lookups.values() if slug in lookup),
        sum(lookup[slug]["rank"] for lookup in lookups.values() if slug in lookup) / sum(slug in lookup for lookup in lookups.values()), names[slug], slug))
    lines += ["## Top30 并集的跨方案名次", "",
        f"本轮 Top30 并集包含 **{len(union)}** 个模型，按最佳名次、在榜平均名次、名称及 slug 排序。"
        "每五套分表且行序一致。数字表示 Top30 内名次；“—（#名次）”表示已入榜但不在 Top30；“未入榜”表示资格剔除。", ""]
    for start in range(0, len(keys), 5):
        group = keys[start:start + 5]
        lines += [f"### 方案 {start + 1}–{start + len(group)} 的 Top30 并集", ""]
        _table(lines, ("模型", *(variants[k]["label"] for k in group)), (
            (names[slug], *(shared._rank(lookups[k].get(slug), top30=True) for k in group)) for slug in union))
    lines += ["## 每套完整 Top30", "",
        "基础总分为本套所有已配置 Core 的固定份额贡献合计；最终分包含领域封顶后的扩展。"
        "Terminal 列只显示 v4 实测，缺测用 —；未选 Terminal 作 Core 的方案中，该列仅作证据对照，不参与计分。", ""]
    for key, variant in variants.items():
        rows = results[key]["rows"]
        lines += [f"### {variant['label']}", "",
            f"共 {len(rows)} 个合格模型，{_counts(variant)[2]} 个已配置 Core。"
            f"[全量与分项](rankings_{key}.csv) · [剔除与缺项](excluded_{key}.csv) · [共同集合重算](common_{key}.csv)。", ""]
        _table(lines, ("名次", "模型／固定配置", "最终分", "基础总分", "扩展净贡献", "缺Core数", "Terminal v4实测"), (
            (r["rank"], r["model"], _number(r["score"]), _number(r["core_only_score"]),
             _number(r["score"] - r["core_only_score"]), r["missing_core_count"], _number(r.get("terminal_effective"))) for r in rows[:30]))
        if len(rows) < 30:
            lines += [f"本套只有 {len(rows)} 个合格模型，已显示全部。", ""]
    lines += [f"各套共同入榜集合有 **{metadata.get('common_population', len(next(iter(results.values()))['common_rows']))}** 个固定配置。"
        "本文件 Top30 来自各方案全量合格榜；共同集合排名已重新拟合，见各 common CSV，不应混用名次。", ""]
    (output / "TOP30_COMPARISON.md").write_text("\n".join(lines), encoding="utf-8")


def _validate(variants, results, metadata):
    if set(variants) != set(results):
        raise ValueError("Mixed-Core reports require matching variant and result registries")
    count, threshold = len(_labels(metadata)), _threshold(metadata)
    forbidden_terminal = {base.TB, *base.OLD_TB}
    for key, variant in variants.items():
        core = variant["core"]
        if set(core) != set(BOARDS) or any(len(core[b]) not in (1, 2) for b in BOARDS):
            raise ValueError(f"Every board must configure one or two Core items: {key}")
        items = [item for b in BOARDS for item in core[b]]
        if len({dual.canonical_family(item) for item in items}) != len(items):
            raise ValueError(f"Core benchmark families cannot repeat: {key}")
        for item in items:
            compact = re.sub(r"[^a-z0-9]", "", item.lower())
            if any(token in compact for token in ("aime", "hmmt", "math500", "gsm8k", "livecodebench", "gpqa")):
                raise ValueError(f"Forbidden Core benchmark: {key}, {item}")
            if dual.canonical_family(item) == "terminal-bench" and item != base.LATEST_TB:
                raise ValueError(f"Only Terminal v4 Core is permitted: {key}")
        weights = variant["weights"]
        if len(weights) != 5 or any(not math.isfinite(w) or not 9 <= w <= 40 for w in weights) or not math.isclose(sum(weights), 100):
            raise ValueError(f"Mixed-Core weights must be 9--40% and total 100: {key}")
        result = results[key]
        for common in (False, True):
            audit = _audit(result, common)
            checks = audit.get("checks", [])
            if not audit.get("passed") or len(checks) != count or any(
                not check.get("passed") or check.get("margin") is None
                or not math.isfinite(check["margin"]) or check["margin"] <= threshold for check in checks
            ):
                raise ValueError(f"Cannot publish failing Mixed-Core candidate: {key}, common={common}")
            rows = result.get("common_rows" if common else "rows", [])
            if not rows:
                raise ValueError(f"Passing Mixed-Core report requires ranked rows: {key}, common={common}")
            for row in rows:
                if row.get("terminal_source") not in (base.LATEST_TB, "missing"):
                    raise ValueError(f"Legacy Terminal source in Mixed-Core report: {key}, {row['slug']}")
            calibration = result.get("common_calibration" if common else "calibration", {})
            for board in calibration.get("boards", {}).values():
                if any(item in forbidden_terminal or (dual.canonical_family(item) == "terminal-bench" and item != base.LATEST_TB)
                       for item in board.get("extensions", [])):
                    raise ValueError(f"Legacy Terminal extension in Mixed-Core report: {key}")


def write_reports(output: Path, variants: dict, results: dict, metadata: dict):
    """Publish only fully screened variants; an empty run gets no rankings."""
    _validate(variants, results, metadata)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    if not variants:
        for filename, title in (("SCHEMES.md", "单／双 Core 方案筛选结果"), ("TOP30_COMPARISON.md", "单／双 Core Top30 对比")):
            lines = [f"# {title}", "",
                "本轮没有同时通过全量和共同集合全部筛选条件的方案，因此不展示不合格方案或 Top30。"
                "这表示本次搜索范围内没有合格结果，不代表所有可能的评分设计都无解。", "",
                "详细搜索范围、通过与淘汰原因见 [SEARCH_REPORT.md](SEARCH_REPORT.md)。"
                "本轮仍采用每领域一或两项、单项占领域基础分 100%、双项各半，"
                "领域全缺或累计缺至少四项剔除；AIME、LiveCodeBench、GPQA 不进入 Core，Terminal 仅 v4。", ""]
            _source(lines, metadata)
            (output / filename).write_text("\n".join(lines), encoding="utf-8")
        return
    _write_schemes(output, variants, results, metadata)
    _write_top30(output, variants, results, metadata)
