# 10 套通过筛选的单／双 Core 方案

本轮固定 **2 个单 Core 领域**，其余领域各用两个 Core。以下 **10 套方案**使用 **10 种 Core 结构**，均通过全量及共同集合的全部筛选条件；同一结构的不同权重版本不算新的结构。
独立的完整 Top30、关注模型与跨方案名次对比见 [TOP30_COMPARISON.md](TOP30_COMPARISON.md)。

输入快照：**2026-09-08T23:56:02+00:00**；644 个配置，预先固定 471 个模型组代表配置。按 variantPriority、再按 slug 选择代表，先选配置，再检查资格；不因缺测更换档位，也不借同模型其他配置的成绩。
这是实验方案，正式 Scheme 18、网站和日常 Action 未切换。原始输入未改分，模型名称只参与候选排序筛选，对所有模型应用相同公式与方案权重。完整输入哈希、参数和拟合结果见 [run.json](run.json)，搜索范围与选择过程见 [SEARCH_REPORT.md](SEARCH_REPORT.md)。
名次按未舍入最终分降序、再按 slug 排序；表中保留三位小数，显示分数相同不代表原值相同。

## 共同规则

1. 每领域配置一个或两个 Core，同一测试家族不能在任何领域重复占位。单 Core 占领域基础分 100%；双 Core 各占 50%。这次只调整 Core 数量与组合，扩展加分算法沿用此前规则。
2. 某领域全部已配置 Core 缺测，或全部已配置 Core 累计缺测至少四项，均剔除。未配置的第二项不是缺测。单 Core 领域缺唯一项目即触发领域全缺；双 Core 缺一项仍损失固定半份，不能把另一项放大补足。实测 0 是有效观测。
3. AIME、LiveCodeBench、GPQA 及其别名不进入 Core；HMMT、MATH-500、GSM8K 等同类竞赛／旧题测试也不用于替代。它们是否作为扩展仍按既有扩展注册表处理，移出 Core 不等于取消全部影响。
4. Terminal 仅使用固定配置的 v4.0 实测；无 v4 即缺测，不启用 v2.1、Hard、旧版回退或版本回归，旧 Terminal 也不进入扩展。v4 实测 0 不回退。
5. Core 调整值采用 0–100 尺度。百分比项目使用采集后的百分制；AA-Briefcase、GDPval-AA v2 使用 `clip((Elo−500)/2000×100, 0, 100)`。Elo 换算分不是通过率，不同测试也没有天然一致的难度尺度。
6. 所有 Core 家族从全部领域的扩展池移除，避免重复计分。只有领域全部已配置 Core 有观测的模型，才能参与该领域扩展拟合并获得加分；每个扩展至少五个完整观测才拟合，回归斜率非负。双 Core 缺一项的领域扩展固定为 0。
7. 各领域权重在 9%–40% 之间，以 1 个百分点搜索，合计 100%。基础分加扩展后按领域封顶 100，再按该方案权重加权；没有模型专属权重或惩罚。
8. 每套先在自己的合格人群上拟合扩展；再在最终入选方案共同入榜的固定人群上重新拟合、重新排名。两个口径都必须通过全部排序条件。

设领域配置数为 `k∈{1,2}`，`aᵢ` 为调整后成绩，`Iᵢ` 表示是否有观测；`w` 为领域百分比权重，`rⱼ=max(0, 扩展实测ⱼ−预测ⱼ)`。

```text
领域基础分 B = Σ(Iᵢ × aᵢ) / k
每个 Core 的基础总分贡献 = Iᵢ × aᵢ × w / (100 × k)
扩展上限 C = 全部正残差的均值 + √2 × 总体标准差（无正残差时为 0）
领域扩展 E = min(C, ln(1 + Σexpm1(rⱼ)))，仅该领域全部已配置 Core 有观测时
领域最终分 S = min(100, B + E)
基础总分 = Σ(w_b × B_b / 100)；最终总分 = Σ(w_b × S_b / 100)
```

例如权重 20% 的单 Core 得 80 分，贡献基础总分 16 分；双 Core 为 80、60 时，分别贡献 8、6 分。若双 Core 的第二项缺测，贡献变为 8、0 分并停用该领域扩展；若它是真实 0，则贡献也为 8、0 分，但不是缺测，仍可拟合及获得扩展。单 Core 的唯一项缺测时，模型直接失去本套资格。

**单 Core 的实际取舍：**去掉覆盖较差的第二项，可以消除该项固定半份计零的影响；但保留项目的总分权重翻倍，该测试的覆盖、尺度、测评误差会更直接地支配领域。同时失去两项互相补充的证据，原本只测了被删项目的模型还会因领域全缺而被剔除，因此不保证入榜人数增加。Core 数变化也会改变完整样本、扩展池、拟合参数与动态上限；这不只是机械地删掉一列分数。

## 先筛选，再展示

本轮保留以下 9 条筛选条件，目标模型必须入榜，所有审计分差严格大于 **0.05 分**。第一、第二名检查覆盖整个合格榜，不能只在指定模型中相互比较。

1. Fable 5.1 第一。
2. GPT-6 Astra 第二。
3. Kimi K3 高于 Gemini 3.8 Flash。
4. GPT-5.5 高于 Muse Spark 1.3。
5. Qwen3.8 Max 高于 Qwen3.8 Flash-Next。
6. Qwen3.8 2.4T A95B 高于 Qwen3.8 Flash-Next。
7. GPT-5.6 Sol 高于 Claude Opus 5。
8. GPT-5.6 Terra 高于 Muse Spark 1.3。
9. Grok 4.6 高于 Grok 4.5。

这些模型的已知成绩参与了 Core 组合和权重选择，满足条件是候选入选标准，不是模型能力或全榜合理性的独立验证。下方保留旧模型的正常资格与实际名次，用于检查未被指定次序约束的结果；不会为使其靠后再施加人工排除或扣分。

| 搜索记录 | 结果 |
| --- | --- |
| 检查的 Core 结构 | 2295 |
| 家族不重复的有效结构 | 1165 |
| 进入权重筛选的结构 | 498 |
| 每结构的权重向量 | 367376 |
| 检查的 Core／权重组合 | 182953248 |
| 全量筛选合格组合 | 18834 |
| 全量合格的不同 Core 结构 | 21 |
| 最低合格模型数 | 100 |
| 每 Core 最低固定代表覆盖 | 100 |
| 最终选择方案数 | 10 |

权重敏感性检查固定全量人群和拟合参数，将一个领域减 1 个百分点、另一个加 1 个百分点，共 20 个有向转移，包含越过搜索边界的压力检查。通过次数只说明这组有限扰动下的指定排序，不能保证未来成绩更新后的稳定性。

| 方案 | 单／双 Core 领域数 | 全量／共同集合通过 | 全量最小分差 | 共同集合最小分差 | ±1个百分点通过数 |
| --- | --- | --- | --- | --- | --- |
| [01 高难推理、知识／科学单Core·接近等权](#mc01) | 2／3 | 9/9／9/9 | 0.117 | 0.117 | 12／20 |
| [02 高难推理、知识／科学单Core·接近等权](#mc02) | 2／3 | 9/9／9/9 | 0.129 | 0.129 | 12／20 |
| [03 高难推理、知识／科学单Core·接近等权](#mc03) | 2／3 | 9/9／9/9 | 0.096 | 0.096 | 9／20 |
| [04 高难推理、知识／科学单Core·接近等权](#mc04) | 2／3 | 9/9／9/9 | 0.183 | 0.157 | 17／20 |
| [05 高难推理、知识／科学单Core·接近等权](#mc05) | 2／3 | 9/9／9/9 | 0.185 | 0.154 | 17／20 |
| [06 高难推理、知识／科学单Core·接近等权](#mc06) | 2／3 | 9/9／9/9 | 0.113 | 0.084 | 11／20 |
| [07 高难推理、指令／上下文单Core·接近等权](#mc07) | 2／3 | 9/9／9/9 | 0.132 | 0.132 | 12／20 |
| [08 编程、高难推理单Core·接近等权](#mc08) | 2／3 | 9/9／9/9 | 0.144 | 0.144 | 15／20 |
| [09 知识／科学、指令／上下文单Core·接近等权](#mc09) | 2／3 | 9/9／9/9 | 0.109 | 0.109 | 9／20 |
| [10 高难推理、指令／上下文单Core·接近等权](#mc10) | 2／3 | 9/9／9/9 | 0.088 | 0.088 | 7／20 |

所有入选方案共同入榜集合为 **107** 个固定配置。共同集合会重新拟合扩展；它控制了人群变化，但仍保留 Core 组合、扩展池与权重的差异。

<a id="mc01"></a>

## 01 高难推理、知识／科学单Core·接近等权

**设计目的：**仅将高难推理、知识／科学设为单 Core，保留其他领域双 Core；按接近等权选择权重。

本套有 2 个单 Core 领域、3 个双 Core 领域，共 8 项。单 Core 领域都必须有观测，因此本套合格者最多可缺 **3 项**，且缺项必须分散在不同双 Core 领域。累计缺至少四项规则继续保留。

本套作为组合对照起点，方案编号不代表推荐先后。

| 领域 | 结构 | Core项目 | 领域权重 | 单项基础总分权重 | 单项最高基础贡献 | 固定代表可用数 |
| --- | --- | --- | --- | --- | --- | --- |
| 编程 | 双 Core | Terminal-Bench v4.0 | 9% | 4.5% | 4.5 分 | 102 |
| 编程 | 双 Core | SciCode | 9% | 4.5% | 4.5 分 | 121 |
| Agent／工具工作 | 双 Core | AutomationBench-AA | 18% | 9% | 9 分 | 110 |
| Agent／工具工作 | 双 Core | τ³-Banking | 18% | 9% | 9 分 | 145 |
| 高难推理 | 单 Core | CritPt | 26% | 26% | 26 分 | 357 |
| 知识／科学 | 单 Core | AA-Omniscience Accuracy | 21% | 21% | 21 分 | 354 |
| 指令／上下文 | 双 Core | AA-LCR v1.1 | 26% | 13% | 13 分 | 354 |
| 指令／上下文 | 双 Core | GDP.pdf | 26% | 13% | 13 分 | 109 |

- **编程：**Terminal-Bench v4.0：终端环境中的编程和工具任务；仅使用 v4.0 同配置实测；SciCode：科学研究场景中的编程能力。
- **Agent／工具工作：**AutomationBench-AA：自动化工作流执行；τ³-Banking：银行场景中的交互和工具使用。
- **高难推理：**CritPt：研究级物理推理。
- **知识／科学：**AA-Omniscience Accuracy：知识问答的回答准确率。
- **指令／上下文：**AA-LCR v1.1：长上下文推理；GDP.pdf：PDF 文档任务；使用 all-pass 成绩。

**领域权重取舍：**以每领域 20% 作为比较参照，本套提高高难推理（+6 个百分点）、知识／科学（+1 个百分点）、指令／上下文（+6 个百分点），降低编程（-11 个百分点）、Agent／工具工作（-2 个百分点）。提高权重会同时放大该领域的基础成绩、缺一项损失及封顶后的扩展影响；不会改变缺测剔除门槛。

**单项集中度：**本套最高单项基础权重为 **26%**（CritPt；如有并列，仅列一项）。这也等于该项对基础总分的最高分数贡献；实际贡献须乘该模型调整成绩／100。
**组合取舍：**单项承担领域全部基础权重，唯一项缺测即剔除；双项各半，缺项不重分配。扩展按相同规则重新拟合。

**覆盖与缺测：**入榜 121 个，剔除 350 个；剔除中领域全缺 350 个、累计缺至少四项 349 个、两者重叠 349 个，不能将两种原因直接相加。入榜者缺 0／1／2／3 项人数为 **98／11／3／9**。

| 领域 | 入榜者Core完整／不完整 | 保留扩展项目 | 启用拟合／保留数 |
| --- | --- | --- | --- |
| 编程 | 102／19 | benchmark:swe-bench-pro、benchmark:livecodebench | 1／2 |
| Agent／工具工作 | 109／12 | τ²-Bench Telecom、APEX-Agents-AA、benchmark:swe-bench-pro、benchmark:hle-tools、benchmark:mcp-atlas、benchmark:osworld-verified | 4／6 |
| 高难推理 | 121／0 | AIME 2025 | 1／1 |
| 知识／科学 | 121／0 | MMMU-Pro、benchmark:mmlu-pro | 1／2 |
| 指令／上下文 | 108／13 | benchmark:charxiv-no-tools | 0／1 |

本套全量拟合的领域扩展上限为 **30.938 分**；共同集合重新拟合后为 **30.910 分**。实际净贡献还受领域 100 分封顶及领域权重限制。

**实际算例：Claude Fable 5.1 (max with fallback)，本套第 1 名**

每行是一个已配置 Core，基础总分贡献已经乘领域权重并除以本领域 Core 数；未配置项不显示。

| 领域 | 已配置 Core | 调整后成绩 | 基础总分权重 | 基础总分贡献 |
| --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench v4.0 | 52.020 | 4.5% | 2.341 |
| 编程 | SciCode | 63.079 | 4.5% | 2.839 |
| Agent／工具工作 | AutomationBench-AA | 59.376 | 9% | 5.344 |
| Agent／工具工作 | τ³-Banking | 47.217 | 9% | 4.249 |
| 高难推理 | CritPt | 29.714 | 26% | 7.726 |
| 知识／科学 | AA-Omniscience Accuracy | 67.233 | 21% | 14.119 |
| 指令／上下文 | AA-LCR v1.1 | 85.333 | 13% | 11.093 |
| 指令／上下文 | GDP.pdf | 26.200 | 13% | 3.406 |

| 领域 | Core数量 | 领域基础分 | 领域扩展加分 | 领域最终分 | 最终总分贡献 |
| --- | --- | --- | --- | --- | --- |
| 编程 | 2 | 57.549 | 2.362 | 59.911 | 5.392 |
| Agent／工具工作 | 2 | 53.296 | 8.873 | 62.169 | 11.190 |
| 高难推理 | 1 | 29.714 | 0.000 | 29.714 | 7.726 |
| 知识／科学 | 1 | 67.233 | 0.000 | 67.233 | 14.119 |
| 指令／上下文 | 2 | 55.767 | 0.000 | 55.767 | 14.499 |

8 项基础贡献合计 **51.117 分**；最终合计 **52.926 分**；计入领域封顶后的扩展净贡献 **1.810 分**。该配置缺 0 项。三位小数逐格相加可能有舍入尾差，精确分项见 CSV。

**9 条条件的逐项审计：**

| 条件 | 全量实际名次／比较对象 | 全量分差 | 共同集合实际名次／比较对象 | 共同集合分差 | 状态 |
| --- | --- | --- | --- | --- | --- |
| Fable 5.1 第一 | Claude Fable 5.1 (max with fallback) #1；GPT-6 Astra (max) #2 | 1.923 | Claude Fable 5.1 (max with fallback) #1；GPT-6 Astra (max) #2 | 1.923 | 两种口径均通过 |
| GPT-6 Astra 第二 | GPT-6 Astra (max) #2；Claude Fable 5 (with fallback) #3 | 0.694 | GPT-6 Astra (max) #2；Claude Fable 5 (with fallback) #3 | 0.694 | 两种口径均通过 |
| Kimi K3 高于 Gemini 3.8 Flash | Kimi K3 (max) #9；Gemini 3.8 Flash (high) #10 | 0.699 | Kimi K3 (max) #9；Gemini 3.8 Flash (high) #10 | 0.681 | 两种口径均通过 |
| GPT-5.5 高于 Muse Spark 1.3 | GPT-5.5 (xhigh) #7；Muse Spark 1.3 (max) #8 | 0.117 | GPT-5.5 (xhigh) #7；Muse Spark 1.3 (max) #8 | 0.117 | 两种口径均通过 |
| Qwen3.8 Max 高于 Qwen3.8 Flash-Next | Qwen3.8 Max #15；Qwen3.8-Flash-Next #28 | 4.736 | Qwen3.8 Max #14；Qwen3.8-Flash-Next #28 | 4.716 | 两种口径均通过 |
| Qwen3.8 2.4T A95B 高于 Qwen3.8 Flash-Next | Qwen3.8 2.4T A95B #21；Qwen3.8-Flash-Next #28 | 2.178 | Qwen3.8 2.4T A95B #21；Qwen3.8-Flash-Next #28 | 2.081 | 两种口径均通过 |
| GPT-5.6 Sol 高于 Claude Opus 5 | GPT-5.6 Sol (max) #4；Claude Opus 5 (max) #5 | 0.120 | GPT-5.6 Sol (max) #4；Claude Opus 5 (max) #5 | 0.120 | 两种口径均通过 |
| GPT-5.6 Terra 高于 Muse Spark 1.3 | GPT-5.6 Terra (max) #6；Muse Spark 1.3 (max) #8 | 0.828 | GPT-5.6 Terra (max) #6；Muse Spark 1.3 (max) #8 | 0.865 | 两种口径均通过 |
| Grok 4.6 高于 Grok 4.5 | Grok 4.6 (xhigh) #12；Grok 4.5 (high) #13 | 0.461 | Grok 4.6 (xhigh) #12；Grok 4.5 (high) #13 | 0.461 | 两种口径均通过 |

**此前排名异常涉及的旧模型：**以下完全按本套配置和缺测门槛处理。Gemini 3 Flash 没有人工排除；如未入榜，表中列出本套实际触发条件。此处名次不是额外筛选条件。

| 模型 | 名次 | 最终分 | 基础总分 | 缺Core数 | 缺项 | 资格原因 |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-5 mini (high) | #39 | 29.522 | 19.469 | 0 | 无 | 正常入榜 |
| Claude 4.5 Sonnet | #47 | 27.179 | 22.811 | 0 | 无 | 正常入榜 |
| Gemini 3 Flash | 未入榜 | — | — | 4 | Terminal-Bench v4.0; SciCode; AutomationBench-AA; GDP.pdf | 领域全缺：编程；累计缺至少四项 |

数据：[全量排名与分项](rankings_mc01.csv) · [剔除与缺项](excluded_mc01.csv) · [共同集合重算](common_mc01.csv)。

<a id="mc02"></a>

## 02 高难推理、知识／科学单Core·接近等权

**设计目的：**仅将高难推理、知识／科学设为单 Core，保留其他领域双 Core；按接近等权选择权重。

本套有 2 个单 Core 领域、3 个双 Core 领域，共 8 项。单 Core 领域都必须有观测，因此本套合格者最多可缺 **3 项**，且缺项必须分散在不同双 Core 领域。累计缺至少四项规则继续保留。

相对首套更换 Core 的领域：Agent／工具工作。

| 领域 | 结构 | Core项目 | 领域权重 | 单项基础总分权重 | 单项最高基础贡献 | 固定代表可用数 |
| --- | --- | --- | --- | --- | --- | --- |
| 编程 | 双 Core | Terminal-Bench v4.0 | 15% | 7.5% | 7.5 分 | 102 |
| 编程 | 双 Core | SciCode | 15% | 7.5% | 7.5 分 | 121 |
| Agent／工具工作 | 双 Core | τ³-Banking | 9% | 4.5% | 4.5 分 | 145 |
| Agent／工具工作 | 双 Core | AA-Briefcase | 9% | 4.5% | 4.5 分 | 112 |
| 高难推理 | 单 Core | CritPt | 26% | 26% | 26 分 | 357 |
| 知识／科学 | 单 Core | AA-Omniscience Accuracy | 22% | 22% | 22 分 | 354 |
| 指令／上下文 | 双 Core | AA-LCR v1.1 | 28% | 14% | 14 分 | 354 |
| 指令／上下文 | 双 Core | GDP.pdf | 28% | 14% | 14 分 | 109 |

- **编程：**Terminal-Bench v4.0：终端环境中的编程和工具任务；仅使用 v4.0 同配置实测；SciCode：科学研究场景中的编程能力。
- **Agent／工具工作：**τ³-Banking：银行场景中的交互和工具使用；AA-Briefcase：工作任务表现；使用 Elo 换算分。
- **高难推理：**CritPt：研究级物理推理。
- **知识／科学：**AA-Omniscience Accuracy：知识问答的回答准确率。
- **指令／上下文：**AA-LCR v1.1：长上下文推理；GDP.pdf：PDF 文档任务；使用 all-pass 成绩。

**领域权重取舍：**以每领域 20% 作为比较参照，本套提高高难推理（+6 个百分点）、知识／科学（+2 个百分点）、指令／上下文（+8 个百分点），降低编程（-5 个百分点）、Agent／工具工作（-11 个百分点）。提高权重会同时放大该领域的基础成绩、缺一项损失及封顶后的扩展影响；不会改变缺测剔除门槛。

**单项集中度：**本套最高单项基础权重为 **26%**（CritPt；如有并列，仅列一项）。这也等于该项对基础总分的最高分数贡献；实际贡献须乘该模型调整成绩／100。
**组合取舍：**单项承担领域全部基础权重，唯一项缺测即剔除；双项各半，缺项不重分配。扩展按相同规则重新拟合。

**覆盖与缺测：**入榜 121 个，剔除 350 个；剔除中领域全缺 350 个、累计缺至少四项 348 个、两者重叠 348 个，不能将两种原因直接相加。入榜者缺 0／1／2／3 项人数为 **95／14／3／9**。

| 领域 | 入榜者Core完整／不完整 | 保留扩展项目 | 启用拟合／保留数 |
| --- | --- | --- | --- |
| 编程 | 102／19 | benchmark:swe-bench-pro、benchmark:livecodebench | 1／2 |
| Agent／工具工作 | 106／15 | τ²-Bench Telecom、APEX-Agents-AA、benchmark:swe-bench-pro、benchmark:hle-tools、benchmark:mcp-atlas、benchmark:osworld-verified | 4／6 |
| 高难推理 | 121／0 | AIME 2025 | 1／1 |
| 知识／科学 | 121／0 | MMMU-Pro、benchmark:mmlu-pro | 1／2 |
| 指令／上下文 | 108／13 | benchmark:charxiv-no-tools | 0／1 |

本套全量拟合的领域扩展上限为 **29.727 分**；共同集合重新拟合后为 **29.702 分**。实际净贡献还受领域 100 分封顶及领域权重限制。

**实际算例：Claude Fable 5.1 (max with fallback)，本套第 1 名**

每行是一个已配置 Core，基础总分贡献已经乘领域权重并除以本领域 Core 数；未配置项不显示。

| 领域 | 已配置 Core | 调整后成绩 | 基础总分权重 | 基础总分贡献 |
| --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench v4.0 | 52.020 | 7.5% | 3.902 |
| 编程 | SciCode | 63.079 | 7.5% | 4.731 |
| Agent／工具工作 | τ³-Banking | 47.217 | 4.5% | 2.125 |
| Agent／工具工作 | AA-Briefcase | 58.091 | 4.5% | 2.614 |
| 高难推理 | CritPt | 29.714 | 26% | 7.726 |
| 知识／科学 | AA-Omniscience Accuracy | 67.233 | 22% | 14.791 |
| 指令／上下文 | AA-LCR v1.1 | 85.333 | 14% | 11.947 |
| 指令／上下文 | GDP.pdf | 26.200 | 14% | 3.668 |

| 领域 | Core数量 | 领域基础分 | 领域扩展加分 | 领域最终分 | 最终总分贡献 |
| --- | --- | --- | --- | --- | --- |
| 编程 | 2 | 57.549 | 2.362 | 59.911 | 8.987 |
| Agent／工具工作 | 2 | 52.654 | 4.356 | 57.010 | 5.131 |
| 高难推理 | 1 | 29.714 | 0.000 | 29.714 | 7.726 |
| 知识／科学 | 1 | 67.233 | 0.000 | 67.233 | 14.791 |
| 指令／上下文 | 2 | 55.767 | 0.000 | 55.767 | 15.615 |

8 项基础贡献合计 **51.503 分**；最终合计 **52.249 分**；计入领域封顶后的扩展净贡献 **0.746 分**。该配置缺 0 项。三位小数逐格相加可能有舍入尾差，精确分项见 CSV。

**9 条条件的逐项审计：**

| 条件 | 全量实际名次／比较对象 | 全量分差 | 共同集合实际名次／比较对象 | 共同集合分差 | 状态 |
| --- | --- | --- | --- | --- | --- |
| Fable 5.1 第一 | Claude Fable 5.1 (max with fallback) #1；GPT-6 Astra (max) #2 | 1.676 | Claude Fable 5.1 (max with fallback) #1；GPT-6 Astra (max) #2 | 1.676 | 两种口径均通过 |
| GPT-6 Astra 第二 | GPT-6 Astra (max) #2；Claude Fable 5 (with fallback) #3 | 0.604 | GPT-6 Astra (max) #2；Claude Fable 5 (with fallback) #3 | 0.604 | 两种口径均通过 |
| Kimi K3 高于 Gemini 3.8 Flash | Kimi K3 (max) #9；Gemini 3.8 Flash (high) #10 | 1.354 | Kimi K3 (max) #9；Gemini 3.8 Flash (high) #10 | 1.334 | 两种口径均通过 |
| GPT-5.5 高于 Muse Spark 1.3 | GPT-5.5 (xhigh) #7；Muse Spark 1.3 (max) #8 | 0.159 | GPT-5.5 (xhigh) #7；Muse Spark 1.3 (max) #8 | 0.159 | 两种口径均通过 |
| Qwen3.8 Max 高于 Qwen3.8 Flash-Next | Qwen3.8 Max #15；Qwen3.8-Flash-Next #32 | 7.791 | Qwen3.8 Max #15；Qwen3.8-Flash-Next #32 | 7.771 | 两种口径均通过 |
| Qwen3.8 2.4T A95B 高于 Qwen3.8 Flash-Next | Qwen3.8 2.4T A95B #24；Qwen3.8-Flash-Next #32 | 4.383 | Qwen3.8 2.4T A95B #24；Qwen3.8-Flash-Next #32 | 4.282 | 两种口径均通过 |
| GPT-5.6 Sol 高于 Claude Opus 5 | GPT-5.6 Sol (max) #4；Claude Opus 5 (max) #5 | 0.129 | GPT-5.6 Sol (max) #4；Claude Opus 5 (max) #5 | 0.129 | 两种口径均通过 |
| GPT-5.6 Terra 高于 Muse Spark 1.3 | GPT-5.6 Terra (max) #6；Muse Spark 1.3 (max) #8 | 0.499 | GPT-5.6 Terra (max) #6；Muse Spark 1.3 (max) #8 | 0.538 | 两种口径均通过 |
| Grok 4.6 高于 Grok 4.5 | Grok 4.6 (xhigh) #16；Grok 4.5 (high) #17 | 0.232 | Grok 4.6 (xhigh) #16；Grok 4.5 (high) #17 | 0.232 | 两种口径均通过 |

**此前排名异常涉及的旧模型：**以下完全按本套配置和缺测门槛处理。Gemini 3 Flash 没有人工排除；如未入榜，表中列出本套实际触发条件。此处名次不是额外筛选条件。

| 模型 | 名次 | 最终分 | 基础总分 | 缺Core数 | 缺项 | 资格原因 |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-5 mini (high) | #38 | 29.760 | 20.417 | 0 | 无 | 正常入榜 |
| Claude 4.5 Sonnet | #48 | 27.169 | 23.392 | 0 | 无 | 正常入榜 |
| Gemini 3 Flash | 未入榜 | — | — | 4 | Terminal-Bench v4.0; SciCode; AA-Briefcase; GDP.pdf | 领域全缺：编程；累计缺至少四项 |

数据：[全量排名与分项](rankings_mc02.csv) · [剔除与缺项](excluded_mc02.csv) · [共同集合重算](common_mc02.csv)。

<a id="mc03"></a>

## 03 高难推理、知识／科学单Core·接近等权

**设计目的：**仅将高难推理、知识／科学设为单 Core，保留其他领域双 Core；按接近等权选择权重。

本套有 2 个单 Core 领域、3 个双 Core 领域，共 8 项。单 Core 领域都必须有观测，因此本套合格者最多可缺 **3 项**，且缺项必须分散在不同双 Core 领域。累计缺至少四项规则继续保留。

相对首套更换 Core 的领域：Agent／工具工作。

| 领域 | 结构 | Core项目 | 领域权重 | 单项基础总分权重 | 单项最高基础贡献 | 固定代表可用数 |
| --- | --- | --- | --- | --- | --- | --- |
| 编程 | 双 Core | Terminal-Bench v4.0 | 15% | 7.5% | 7.5 分 | 102 |
| 编程 | 双 Core | SciCode | 15% | 7.5% | 7.5 分 | 121 |
| Agent／工具工作 | 双 Core | τ³-Banking | 9% | 4.5% | 4.5 分 | 145 |
| Agent／工具工作 | 双 Core | GDPval-AA v2 | 9% | 4.5% | 4.5 分 | 170 |
| 高难推理 | 单 Core | CritPt | 24% | 24% | 24 分 | 357 |
| 知识／科学 | 单 Core | AA-Omniscience Accuracy | 21% | 21% | 21 分 | 354 |
| 指令／上下文 | 双 Core | AA-LCR v1.1 | 31% | 15.5% | 15.5 分 | 354 |
| 指令／上下文 | 双 Core | GDP.pdf | 31% | 15.5% | 15.5 分 | 109 |

- **编程：**Terminal-Bench v4.0：终端环境中的编程和工具任务；仅使用 v4.0 同配置实测；SciCode：科学研究场景中的编程能力。
- **Agent／工具工作：**τ³-Banking：银行场景中的交互和工具使用；GDPval-AA v2：专业知识工作交付；使用 Elo 换算分。
- **高难推理：**CritPt：研究级物理推理。
- **知识／科学：**AA-Omniscience Accuracy：知识问答的回答准确率。
- **指令／上下文：**AA-LCR v1.1：长上下文推理；GDP.pdf：PDF 文档任务；使用 all-pass 成绩。

**领域权重取舍：**以每领域 20% 作为比较参照，本套提高高难推理（+4 个百分点）、知识／科学（+1 个百分点）、指令／上下文（+11 个百分点），降低编程（-5 个百分点）、Agent／工具工作（-11 个百分点）。提高权重会同时放大该领域的基础成绩、缺一项损失及封顶后的扩展影响；不会改变缺测剔除门槛。

**单项集中度：**本套最高单项基础权重为 **24%**（CritPt；如有并列，仅列一项）。这也等于该项对基础总分的最高分数贡献；实际贡献须乘该模型调整成绩／100。
**组合取舍：**单项承担领域全部基础权重，唯一项缺测即剔除；双项各半，缺项不重分配。扩展按相同规则重新拟合。

**覆盖与缺测：**入榜 121 个，剔除 350 个；剔除中领域全缺 350 个、累计缺至少四项 331 个、两者重叠 331 个，不能将两种原因直接相加。入榜者缺 0／1／2／3 项人数为 **98／14／9／0**。

| 领域 | 入榜者Core完整／不完整 | 保留扩展项目 | 启用拟合／保留数 |
| --- | --- | --- | --- |
| 编程 | 102／19 | benchmark:swe-bench-pro、benchmark:livecodebench | 1／2 |
| Agent／工具工作 | 121／0 | τ²-Bench Telecom、APEX-Agents-AA、benchmark:swe-bench-pro、benchmark:hle-tools、benchmark:mcp-atlas、benchmark:osworld-verified | 4／6 |
| 高难推理 | 121／0 | AIME 2025 | 1／1 |
| 知识／科学 | 121／0 | MMMU-Pro、benchmark:mmlu-pro | 1／2 |
| 指令／上下文 | 108／13 | benchmark:charxiv-no-tools | 0／1 |

本套全量拟合的领域扩展上限为 **28.862 分**；共同集合重新拟合后为 **29.031 分**。实际净贡献还受领域 100 分封顶及领域权重限制。

**实际算例：Claude Fable 5.1 (max with fallback)，本套第 1 名**

每行是一个已配置 Core，基础总分贡献已经乘领域权重并除以本领域 Core 数；未配置项不显示。

| 领域 | 已配置 Core | 调整后成绩 | 基础总分权重 | 基础总分贡献 |
| --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench v4.0 | 52.020 | 7.5% | 3.902 |
| 编程 | SciCode | 63.079 | 7.5% | 4.731 |
| Agent／工具工作 | τ³-Banking | 47.217 | 4.5% | 2.125 |
| Agent／工具工作 | GDPval-AA v2 | 63.182 | 4.5% | 2.843 |
| 高难推理 | CritPt | 29.714 | 24% | 7.131 |
| 知识／科学 | AA-Omniscience Accuracy | 67.233 | 21% | 14.119 |
| 指令／上下文 | AA-LCR v1.1 | 85.333 | 15.5% | 13.227 |
| 指令／上下文 | GDP.pdf | 26.200 | 15.5% | 4.061 |

| 领域 | Core数量 | 领域基础分 | 领域扩展加分 | 领域最终分 | 最终总分贡献 |
| --- | --- | --- | --- | --- | --- |
| 编程 | 2 | 57.549 | 2.362 | 59.911 | 8.987 |
| Agent／工具工作 | 2 | 55.199 | 7.055 | 62.254 | 5.603 |
| 高难推理 | 1 | 29.714 | 0.000 | 29.714 | 7.131 |
| 知识／科学 | 1 | 67.233 | 0.000 | 67.233 | 14.119 |
| 指令／上下文 | 2 | 55.767 | 0.000 | 55.767 | 17.288 |

8 项基础贡献合计 **52.138 分**；最终合计 **53.128 分**；计入领域封顶后的扩展净贡献 **0.989 分**。该配置缺 0 项。三位小数逐格相加可能有舍入尾差，精确分项见 CSV。

**9 条条件的逐项审计：**

| 条件 | 全量实际名次／比较对象 | 全量分差 | 共同集合实际名次／比较对象 | 共同集合分差 | 状态 |
| --- | --- | --- | --- | --- | --- |
| Fable 5.1 第一 | Claude Fable 5.1 (max with fallback) #1；GPT-6 Astra (max) #2 | 2.099 | Claude Fable 5.1 (max with fallback) #1；GPT-6 Astra (max) #2 | 2.099 | 两种口径均通过 |
| GPT-6 Astra 第二 | GPT-6 Astra (max) #2；Claude Fable 5 (with fallback) #3 | 0.281 | GPT-6 Astra (max) #2；Claude Fable 5 (with fallback) #3 | 0.281 | 两种口径均通过 |
| Kimi K3 高于 Gemini 3.8 Flash | Kimi K3 (max) #9；Gemini 3.8 Flash (high) #10 | 1.052 | Kimi K3 (max) #9；Gemini 3.8 Flash (high) #10 | 1.033 | 两种口径均通过 |
| GPT-5.5 高于 Muse Spark 1.3 | GPT-5.5 (xhigh) #7；Muse Spark 1.3 (max) #8 | 0.101 | GPT-5.5 (xhigh) #7；Muse Spark 1.3 (max) #8 | 0.119 | 两种口径均通过 |
| Qwen3.8 Max 高于 Qwen3.8 Flash-Next | Qwen3.8 Max #15；Qwen3.8-Flash-Next #30 | 5.573 | Qwen3.8 Max #15；Qwen3.8-Flash-Next #30 | 5.554 | 两种口径均通过 |
| Qwen3.8 2.4T A95B 高于 Qwen3.8 Flash-Next | Qwen3.8 2.4T A95B #25；Qwen3.8-Flash-Next #30 | 2.122 | Qwen3.8 2.4T A95B #25；Qwen3.8-Flash-Next #30 | 2.025 | 两种口径均通过 |
| GPT-5.6 Sol 高于 Claude Opus 5 | GPT-5.6 Sol (max) #4；Claude Opus 5 (max) #5 | 0.096 | GPT-5.6 Sol (max) #4；Claude Opus 5 (max) #5 | 0.096 | 两种口径均通过 |
| GPT-5.6 Terra 高于 Muse Spark 1.3 | GPT-5.6 Terra (max) #6；Muse Spark 1.3 (max) #8 | 0.399 | GPT-5.6 Terra (max) #6；Muse Spark 1.3 (max) #8 | 0.436 | 两种口径均通过 |
| Grok 4.6 高于 Grok 4.5 | Grok 4.6 (xhigh) #16；Grok 4.5 (high) #17 | 0.169 | Grok 4.6 (xhigh) #16；Grok 4.5 (high) #17 | 0.169 | 两种口径均通过 |

**此前排名异常涉及的旧模型：**以下完全按本套配置和缺测门槛处理。Gemini 3 Flash 没有人工排除；如未入榜，表中列出本套实际触发条件。此处名次不是额外筛选条件。

| 模型 | 名次 | 最终分 | 基础总分 | 缺Core数 | 缺项 | 资格原因 |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-5 mini (high) | #42 | 29.959 | 22.233 | 0 | 无 | 正常入榜 |
| Claude 4.5 Sonnet | #51 | 27.990 | 24.828 | 0 | 无 | 正常入榜 |
| Gemini 3 Flash | 未入榜 | — | — | 4 | Terminal-Bench v4.0; SciCode; GDPval-AA v2; GDP.pdf | 领域全缺：编程；累计缺至少四项 |

数据：[全量排名与分项](rankings_mc03.csv) · [剔除与缺项](excluded_mc03.csv) · [共同集合重算](common_mc03.csv)。

<a id="mc04"></a>

## 04 高难推理、知识／科学单Core·接近等权

**设计目的：**仅将高难推理、知识／科学设为单 Core，保留其他领域双 Core；按接近等权选择权重。

本套有 2 个单 Core 领域、3 个双 Core 领域，共 8 项。单 Core 领域都必须有观测，因此本套合格者最多可缺 **3 项**，且缺项必须分散在不同双 Core 领域。累计缺至少四项规则继续保留。

相对首套更换 Core 的领域：Agent／工具工作。

| 领域 | 结构 | Core项目 | 领域权重 | 单项基础总分权重 | 单项最高基础贡献 | 固定代表可用数 |
| --- | --- | --- | --- | --- | --- | --- |
| 编程 | 双 Core | Terminal-Bench v4.0 | 14% | 7% | 7 分 | 102 |
| 编程 | 双 Core | SciCode | 14% | 7% | 7 分 | 121 |
| Agent／工具工作 | 双 Core | AutomationBench-AA | 9% | 4.5% | 4.5 分 | 110 |
| Agent／工具工作 | 双 Core | GDPval-AA v2 | 9% | 4.5% | 4.5 分 | 170 |
| 高难推理 | 单 Core | CritPt | 26% | 26% | 26 分 | 357 |
| 知识／科学 | 单 Core | AA-Omniscience Accuracy | 22% | 22% | 22 分 | 354 |
| 指令／上下文 | 双 Core | AA-LCR v1.1 | 29% | 14.5% | 14.5 分 | 354 |
| 指令／上下文 | 双 Core | GDP.pdf | 29% | 14.5% | 14.5 分 | 109 |

- **编程：**Terminal-Bench v4.0：终端环境中的编程和工具任务；仅使用 v4.0 同配置实测；SciCode：科学研究场景中的编程能力。
- **Agent／工具工作：**AutomationBench-AA：自动化工作流执行；GDPval-AA v2：专业知识工作交付；使用 Elo 换算分。
- **高难推理：**CritPt：研究级物理推理。
- **知识／科学：**AA-Omniscience Accuracy：知识问答的回答准确率。
- **指令／上下文：**AA-LCR v1.1：长上下文推理；GDP.pdf：PDF 文档任务；使用 all-pass 成绩。

**领域权重取舍：**以每领域 20% 作为比较参照，本套提高高难推理（+6 个百分点）、知识／科学（+2 个百分点）、指令／上下文（+9 个百分点），降低编程（-6 个百分点）、Agent／工具工作（-11 个百分点）。提高权重会同时放大该领域的基础成绩、缺一项损失及封顶后的扩展影响；不会改变缺测剔除门槛。

**单项集中度：**本套最高单项基础权重为 **26%**（CritPt；如有并列，仅列一项）。这也等于该项对基础总分的最高分数贡献；实际贡献须乘该模型调整成绩／100。
**组合取舍：**单项承担领域全部基础权重，唯一项缺测即剔除；双项各半，缺项不重分配。扩展按相同规则重新拟合。

**覆盖与缺测：**入榜 121 个，剔除 350 个；剔除中领域全缺 350 个、累计缺至少四项 349 个、两者重叠 349 个，不能将两种原因直接相加。入榜者缺 0／1／2／3 项人数为 **98／11／3／9**。

| 领域 | 入榜者Core完整／不完整 | 保留扩展项目 | 启用拟合／保留数 |
| --- | --- | --- | --- |
| 编程 | 102／19 | benchmark:swe-bench-pro、benchmark:livecodebench | 1／2 |
| Agent／工具工作 | 109／12 | τ²-Bench Telecom、τ³-Banking、APEX-Agents-AA、benchmark:swe-bench-pro、benchmark:hle-tools、benchmark:mcp-atlas、benchmark:osworld-verified | 5／7 |
| 高难推理 | 121／0 | AIME 2025 | 1／1 |
| 知识／科学 | 121／0 | MMMU-Pro、benchmark:mmlu-pro | 1／2 |
| 指令／上下文 | 108／13 | benchmark:charxiv-no-tools | 0／1 |

本套全量拟合的领域扩展上限为 **23.835 分**；共同集合重新拟合后为 **23.909 分**。实际净贡献还受领域 100 分封顶及领域权重限制。

**实际算例：Claude Fable 5.1 (max with fallback)，本套第 1 名**

每行是一个已配置 Core，基础总分贡献已经乘领域权重并除以本领域 Core 数；未配置项不显示。

| 领域 | 已配置 Core | 调整后成绩 | 基础总分权重 | 基础总分贡献 |
| --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench v4.0 | 52.020 | 7% | 3.641 |
| 编程 | SciCode | 63.079 | 7% | 4.416 |
| Agent／工具工作 | AutomationBench-AA | 59.376 | 4.5% | 2.672 |
| Agent／工具工作 | GDPval-AA v2 | 63.182 | 4.5% | 2.843 |
| 高难推理 | CritPt | 29.714 | 26% | 7.726 |
| 知识／科学 | AA-Omniscience Accuracy | 67.233 | 22% | 14.791 |
| 指令／上下文 | AA-LCR v1.1 | 85.333 | 14.5% | 12.373 |
| 指令／上下文 | GDP.pdf | 26.200 | 14.5% | 3.799 |

| 领域 | Core数量 | 领域基础分 | 领域扩展加分 | 领域最终分 | 最终总分贡献 |
| --- | --- | --- | --- | --- | --- |
| 编程 | 2 | 57.549 | 2.362 | 59.911 | 8.388 |
| Agent／工具工作 | 2 | 61.279 | 8.374 | 69.653 | 6.269 |
| 高难推理 | 1 | 29.714 | 0.000 | 29.714 | 7.726 |
| 知识／科学 | 1 | 67.233 | 0.000 | 67.233 | 14.791 |
| 指令／上下文 | 2 | 55.767 | 0.000 | 55.767 | 16.172 |

8 项基础贡献合计 **52.261 分**；最终合计 **53.346 分**；计入领域封顶后的扩展净贡献 **1.084 分**。该配置缺 0 项。三位小数逐格相加可能有舍入尾差，精确分项见 CSV。

**9 条条件的逐项审计：**

| 条件 | 全量实际名次／比较对象 | 全量分差 | 共同集合实际名次／比较对象 | 共同集合分差 | 状态 |
| --- | --- | --- | --- | --- | --- |
| Fable 5.1 第一 | Claude Fable 5.1 (max with fallback) #1；GPT-6 Astra (max) #2 | 1.534 | Claude Fable 5.1 (max with fallback) #1；GPT-6 Astra (max) #2 | 1.534 | 两种口径均通过 |
| GPT-6 Astra 第二 | GPT-6 Astra (max) #2；Claude Fable 5 (with fallback) #3 | 0.777 | GPT-6 Astra (max) #2；Claude Fable 5 (with fallback) #3 | 0.777 | 两种口径均通过 |
| Kimi K3 高于 Gemini 3.8 Flash | Kimi K3 (max) #9；Gemini 3.8 Flash (high) #10 | 0.866 | Kimi K3 (max) #9；Gemini 3.8 Flash (high) #10 | 0.845 | 两种口径均通过 |
| GPT-5.5 高于 Muse Spark 1.3 | GPT-5.5 (xhigh) #7；Muse Spark 1.3 (max) #8 | 0.215 | GPT-5.5 (xhigh) #7；Muse Spark 1.3 (max) #8 | 0.225 | 两种口径均通过 |
| Qwen3.8 Max 高于 Qwen3.8 Flash-Next | Qwen3.8 Max #13；Qwen3.8-Flash-Next #30 | 5.855 | Qwen3.8 Max #13；Qwen3.8-Flash-Next #29 | 5.838 | 两种口径均通过 |
| Qwen3.8 2.4T A95B 高于 Qwen3.8 Flash-Next | Qwen3.8 2.4T A95B #24；Qwen3.8-Flash-Next #30 | 2.374 | Qwen3.8 2.4T A95B #25；Qwen3.8-Flash-Next #29 | 2.273 | 两种口径均通过 |
| GPT-5.6 Sol 高于 Claude Opus 5 | GPT-5.6 Sol (max) #4；Claude Opus 5 (max) #5 | 0.183 | GPT-5.6 Sol (max) #4；Claude Opus 5 (max) #5 | 0.157 | 两种口径均通过 |
| GPT-5.6 Terra 高于 Muse Spark 1.3 | GPT-5.6 Terra (max) #6；Muse Spark 1.3 (max) #8 | 0.554 | GPT-5.6 Terra (max) #6；Muse Spark 1.3 (max) #8 | 0.620 | 两种口径均通过 |
| Grok 4.6 高于 Grok 4.5 | Grok 4.6 (xhigh) #15；Grok 4.5 (high) #17 | 0.297 | Grok 4.6 (xhigh) #15；Grok 4.5 (high) #17 | 0.320 | 两种口径均通过 |

**此前排名异常涉及的旧模型：**以下完全按本套配置和缺测门槛处理。Gemini 3 Flash 没有人工排除；如未入榜，表中列出本套实际触发条件。此处名次不是额外筛选条件。

| 模型 | 名次 | 最终分 | 基础总分 | 缺Core数 | 缺项 | 资格原因 |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-5 mini (high) | #44 | 28.568 | 21.077 | 0 | 无 | 正常入榜 |
| Claude 4.5 Sonnet | #48 | 27.844 | 23.705 | 0 | 无 | 正常入榜 |
| Gemini 3 Flash | 未入榜 | — | — | 5 | Terminal-Bench v4.0; SciCode; AutomationBench-AA; GDPval-AA v2; GDP.pdf | 领域全缺：编程、Agent／工具工作；累计缺至少四项 |

数据：[全量排名与分项](rankings_mc04.csv) · [剔除与缺项](excluded_mc04.csv) · [共同集合重算](common_mc04.csv)。

<a id="mc05"></a>

## 05 高难推理、知识／科学单Core·接近等权

**设计目的：**仅将高难推理、知识／科学设为单 Core，保留其他领域双 Core；按接近等权选择权重。

本套有 2 个单 Core 领域、3 个双 Core 领域，共 8 项。单 Core 领域都必须有观测，因此本套合格者最多可缺 **3 项**，且缺项必须分散在不同双 Core 领域。累计缺至少四项规则继续保留。

相对首套更换 Core 的领域：Agent／工具工作。

| 领域 | 结构 | Core项目 | 领域权重 | 单项基础总分权重 | 单项最高基础贡献 | 固定代表可用数 |
| --- | --- | --- | --- | --- | --- | --- |
| 编程 | 双 Core | Terminal-Bench v4.0 | 14% | 7% | 7 分 | 102 |
| 编程 | 双 Core | SciCode | 14% | 7% | 7 分 | 121 |
| Agent／工具工作 | 双 Core | AutomationBench-AA | 9% | 4.5% | 4.5 分 | 110 |
| Agent／工具工作 | 双 Core | AA-Briefcase | 9% | 4.5% | 4.5 分 | 112 |
| 高难推理 | 单 Core | CritPt | 25% | 25% | 25 分 | 357 |
| 知识／科学 | 单 Core | AA-Omniscience Accuracy | 23% | 23% | 23 分 | 354 |
| 指令／上下文 | 双 Core | AA-LCR v1.1 | 29% | 14.5% | 14.5 分 | 354 |
| 指令／上下文 | 双 Core | GDP.pdf | 29% | 14.5% | 14.5 分 | 109 |

- **编程：**Terminal-Bench v4.0：终端环境中的编程和工具任务；仅使用 v4.0 同配置实测；SciCode：科学研究场景中的编程能力。
- **Agent／工具工作：**AutomationBench-AA：自动化工作流执行；AA-Briefcase：工作任务表现；使用 Elo 换算分。
- **高难推理：**CritPt：研究级物理推理。
- **知识／科学：**AA-Omniscience Accuracy：知识问答的回答准确率。
- **指令／上下文：**AA-LCR v1.1：长上下文推理；GDP.pdf：PDF 文档任务；使用 all-pass 成绩。

**领域权重取舍：**以每领域 20% 作为比较参照，本套提高高难推理（+5 个百分点）、知识／科学（+3 个百分点）、指令／上下文（+9 个百分点），降低编程（-6 个百分点）、Agent／工具工作（-11 个百分点）。提高权重会同时放大该领域的基础成绩、缺一项损失及封顶后的扩展影响；不会改变缺测剔除门槛。

**单项集中度：**本套最高单项基础权重为 **25%**（CritPt；如有并列，仅列一项）。这也等于该项对基础总分的最高分数贡献；实际贡献须乘该模型调整成绩／100。
**组合取舍：**单项承担领域全部基础权重，唯一项缺测即剔除；双项各半，缺项不重分配。扩展按相同规则重新拟合。

**覆盖与缺测：**入榜 111 个，剔除 360 个；剔除中领域全缺 360 个、累计缺至少四项 359 个、两者重叠 359 个，不能将两种原因直接相加。入榜者缺 0／1／2／3 项人数为 **95／12／4／0**。

| 领域 | 入榜者Core完整／不完整 | 保留扩展项目 | 启用拟合／保留数 |
| --- | --- | --- | --- |
| 编程 | 102／9 | benchmark:swe-bench-pro、benchmark:livecodebench | 1／2 |
| Agent／工具工作 | 104／7 | τ²-Bench Telecom、τ³-Banking、APEX-Agents-AA、benchmark:swe-bench-pro、benchmark:hle-tools、benchmark:mcp-atlas、benchmark:osworld-verified | 5／7 |
| 高难推理 | 111／0 | AIME 2025 | 1／1 |
| 知识／科学 | 111／0 | MMMU-Pro、benchmark:mmlu-pro | 1／2 |
| 指令／上下文 | 107／4 | benchmark:charxiv-no-tools | 0／1 |

本套全量拟合的领域扩展上限为 **25.497 分**；共同集合重新拟合后为 **25.518 分**。实际净贡献还受领域 100 分封顶及领域权重限制。

**实际算例：Claude Fable 5.1 (max with fallback)，本套第 1 名**

每行是一个已配置 Core，基础总分贡献已经乘领域权重并除以本领域 Core 数；未配置项不显示。

| 领域 | 已配置 Core | 调整后成绩 | 基础总分权重 | 基础总分贡献 |
| --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench v4.0 | 52.020 | 7% | 3.641 |
| 编程 | SciCode | 63.079 | 7% | 4.416 |
| Agent／工具工作 | AutomationBench-AA | 59.376 | 4.5% | 2.672 |
| Agent／工具工作 | AA-Briefcase | 58.091 | 4.5% | 2.614 |
| 高难推理 | CritPt | 29.714 | 25% | 7.429 |
| 知识／科学 | AA-Omniscience Accuracy | 67.233 | 23% | 15.464 |
| 指令／上下文 | AA-LCR v1.1 | 85.333 | 14.5% | 12.373 |
| 指令／上下文 | GDP.pdf | 26.200 | 14.5% | 3.799 |

| 领域 | Core数量 | 领域基础分 | 领域扩展加分 | 领域最终分 | 最终总分贡献 |
| --- | --- | --- | --- | --- | --- |
| 编程 | 2 | 57.549 | 2.362 | 59.911 | 8.388 |
| Agent／工具工作 | 2 | 58.733 | 6.093 | 64.827 | 5.834 |
| 高难推理 | 1 | 29.714 | 0.000 | 29.714 | 7.429 |
| 知识／科学 | 1 | 67.233 | 0.000 | 67.233 | 15.464 |
| 指令／上下文 | 2 | 55.767 | 0.000 | 55.767 | 16.172 |

8 项基础贡献合计 **52.407 分**；最终合计 **53.287 分**；计入领域封顶后的扩展净贡献 **0.879 分**。该配置缺 0 项。三位小数逐格相加可能有舍入尾差，精确分项见 CSV。

**9 条条件的逐项审计：**

| 条件 | 全量实际名次／比较对象 | 全量分差 | 共同集合实际名次／比较对象 | 共同集合分差 | 状态 |
| --- | --- | --- | --- | --- | --- |
| Fable 5.1 第一 | Claude Fable 5.1 (max with fallback) #1；GPT-6 Astra (max) #2 | 1.207 | Claude Fable 5.1 (max with fallback) #1；GPT-6 Astra (max) #2 | 1.207 | 两种口径均通过 |
| GPT-6 Astra 第二 | GPT-6 Astra (max) #2；Claude Fable 5 (with fallback) #3 | 1.058 | GPT-6 Astra (max) #2；Claude Fable 5 (with fallback) #3 | 1.058 | 两种口径均通过 |
| Kimi K3 高于 Gemini 3.8 Flash | Kimi K3 (max) #9；Gemini 3.8 Flash (high) #10 | 0.866 | Kimi K3 (max) #9；Gemini 3.8 Flash (high) #10 | 0.853 | 两种口径均通过 |
| GPT-5.5 高于 Muse Spark 1.3 | GPT-5.5 (xhigh) #7；Muse Spark 1.3 (max) #8 | 0.217 | GPT-5.5 (xhigh) #7；Muse Spark 1.3 (max) #8 | 0.237 | 两种口径均通过 |
| Qwen3.8 Max 高于 Qwen3.8 Flash-Next | Qwen3.8 Max #13；Qwen3.8-Flash-Next #32 | 8.169 | Qwen3.8 Max #14；Qwen3.8-Flash-Next #32 | 8.144 | 两种口径均通过 |
| Qwen3.8 2.4T A95B 高于 Qwen3.8 Flash-Next | Qwen3.8 2.4T A95B #25；Qwen3.8-Flash-Next #32 | 4.487 | Qwen3.8 2.4T A95B #25；Qwen3.8-Flash-Next #32 | 4.498 | 两种口径均通过 |
| GPT-5.6 Sol 高于 Claude Opus 5 | GPT-5.6 Sol (max) #4；Claude Opus 5 (max) #5 | 0.185 | GPT-5.6 Sol (max) #4；Claude Opus 5 (max) #5 | 0.154 | 两种口径均通过 |
| GPT-5.6 Terra 高于 Muse Spark 1.3 | GPT-5.6 Terra (max) #6；Muse Spark 1.3 (max) #8 | 0.586 | GPT-5.6 Terra (max) #6；Muse Spark 1.3 (max) #8 | 0.626 | 两种口径均通过 |
| Grok 4.6 高于 Grok 4.5 | Grok 4.6 (xhigh) #16；Grok 4.5 (high) #17 | 0.261 | Grok 4.6 (xhigh) #16；Grok 4.5 (high) #17 | 0.303 | 两种口径均通过 |

**此前排名异常涉及的旧模型：**以下完全按本套配置和缺测门槛处理。Gemini 3 Flash 没有人工排除；如未入榜，表中列出本套实际触发条件。此处名次不是额外筛选条件。

| 模型 | 名次 | 最终分 | 基础总分 | 缺Core数 | 缺项 | 资格原因 |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-5 mini (high) | #43 | 28.846 | 20.471 | 0 | 无 | 正常入榜 |
| Claude 4.5 Sonnet | #48 | 27.673 | 23.398 | 0 | 无 | 正常入榜 |
| Gemini 3 Flash | 未入榜 | — | — | 5 | Terminal-Bench v4.0; SciCode; AutomationBench-AA; AA-Briefcase; GDP.pdf | 领域全缺：编程、Agent／工具工作；累计缺至少四项 |

数据：[全量排名与分项](rankings_mc05.csv) · [剔除与缺项](excluded_mc05.csv) · [共同集合重算](common_mc05.csv)。

<a id="mc06"></a>

## 06 高难推理、知识／科学单Core·接近等权

**设计目的：**仅将高难推理、知识／科学设为单 Core，保留其他领域双 Core；按接近等权选择权重。

本套有 2 个单 Core 领域、3 个双 Core 领域，共 8 项。单 Core 领域都必须有观测，因此本套合格者最多可缺 **3 项**，且缺项必须分散在不同双 Core 领域。累计缺至少四项规则继续保留。

相对首套更换 Core 的领域：Agent／工具工作。

| 领域 | 结构 | Core项目 | 领域权重 | 单项基础总分权重 | 单项最高基础贡献 | 固定代表可用数 |
| --- | --- | --- | --- | --- | --- | --- |
| 编程 | 双 Core | Terminal-Bench v4.0 | 14% | 7% | 7 分 | 102 |
| 编程 | 双 Core | SciCode | 14% | 7% | 7 分 | 121 |
| Agent／工具工作 | 双 Core | AA-Briefcase | 9% | 4.5% | 4.5 分 | 112 |
| Agent／工具工作 | 双 Core | GDPval-AA v2 | 9% | 4.5% | 4.5 分 | 170 |
| 高难推理 | 单 Core | CritPt | 30% | 30% | 30 分 | 357 |
| 知识／科学 | 单 Core | AA-Omniscience Accuracy | 21% | 21% | 21 分 | 354 |
| 指令／上下文 | 双 Core | AA-LCR v1.1 | 26% | 13% | 13 分 | 354 |
| 指令／上下文 | 双 Core | GDP.pdf | 26% | 13% | 13 分 | 109 |

- **编程：**Terminal-Bench v4.0：终端环境中的编程和工具任务；仅使用 v4.0 同配置实测；SciCode：科学研究场景中的编程能力。
- **Agent／工具工作：**AA-Briefcase：工作任务表现；使用 Elo 换算分；GDPval-AA v2：专业知识工作交付；使用 Elo 换算分。
- **高难推理：**CritPt：研究级物理推理。
- **知识／科学：**AA-Omniscience Accuracy：知识问答的回答准确率。
- **指令／上下文：**AA-LCR v1.1：长上下文推理；GDP.pdf：PDF 文档任务；使用 all-pass 成绩。

**领域权重取舍：**以每领域 20% 作为比较参照，本套提高高难推理（+10 个百分点）、知识／科学（+1 个百分点）、指令／上下文（+6 个百分点），降低编程（-6 个百分点）、Agent／工具工作（-11 个百分点）。提高权重会同时放大该领域的基础成绩、缺一项损失及封顶后的扩展影响；不会改变缺测剔除门槛。

**单项集中度：**本套最高单项基础权重为 **30%**（CritPt；如有并列，仅列一项）。这也等于该项对基础总分的最高分数贡献；实际贡献须乘该模型调整成绩／100。
**组合取舍：**单项承担领域全部基础权重，唯一项缺测即剔除；双项各半，缺项不重分配。扩展按相同规则重新拟合。

**覆盖与缺测：**入榜 121 个，剔除 350 个；剔除中领域全缺 350 个、累计缺至少四项 345 个、两者重叠 345 个，不能将两种原因直接相加。入榜者缺 0／1／2／3 项人数为 **95／14／3／9**。

| 领域 | 入榜者Core完整／不完整 | 保留扩展项目 | 启用拟合／保留数 |
| --- | --- | --- | --- |
| 编程 | 102／19 | benchmark:swe-bench-pro、benchmark:livecodebench | 1／2 |
| Agent／工具工作 | 106／15 | τ²-Bench Telecom、τ³-Banking、APEX-Agents-AA、benchmark:swe-bench-pro、benchmark:hle-tools、benchmark:mcp-atlas、benchmark:osworld-verified | 5／7 |
| 高难推理 | 121／0 | AIME 2025 | 1／1 |
| 知识／科学 | 121／0 | MMMU-Pro、benchmark:mmlu-pro | 1／2 |
| 指令／上下文 | 108／13 | benchmark:charxiv-no-tools | 0／1 |

本套全量拟合的领域扩展上限为 **23.677 分**；共同集合重新拟合后为 **23.750 分**。实际净贡献还受领域 100 分封顶及领域权重限制。

**实际算例：Claude Fable 5.1 (max with fallback)，本套第 1 名**

每行是一个已配置 Core，基础总分贡献已经乘领域权重并除以本领域 Core 数；未配置项不显示。

| 领域 | 已配置 Core | 调整后成绩 | 基础总分权重 | 基础总分贡献 |
| --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench v4.0 | 52.020 | 7% | 3.641 |
| 编程 | SciCode | 63.079 | 7% | 4.416 |
| Agent／工具工作 | AA-Briefcase | 58.091 | 4.5% | 2.614 |
| Agent／工具工作 | GDPval-AA v2 | 63.182 | 4.5% | 2.843 |
| 高难推理 | CritPt | 29.714 | 30% | 8.914 |
| 知识／科学 | AA-Omniscience Accuracy | 67.233 | 21% | 14.119 |
| 指令／上下文 | AA-LCR v1.1 | 85.333 | 13% | 11.093 |
| 指令／上下文 | GDP.pdf | 26.200 | 13% | 3.406 |

| 领域 | Core数量 | 领域基础分 | 领域扩展加分 | 领域最终分 | 最终总分贡献 |
| --- | --- | --- | --- | --- | --- |
| 编程 | 2 | 57.549 | 2.362 | 59.911 | 8.388 |
| Agent／工具工作 | 2 | 60.636 | 4.375 | 65.012 | 5.851 |
| 高难推理 | 1 | 29.714 | 0.000 | 29.714 | 8.914 |
| 知识／科学 | 1 | 67.233 | 0.000 | 67.233 | 14.119 |
| 指令／上下文 | 2 | 55.767 | 0.000 | 55.767 | 14.499 |

8 项基础贡献合计 **51.047 分**；最终合计 **51.771 分**；计入领域封顶后的扩展净贡献 **0.724 分**。该配置缺 0 项。三位小数逐格相加可能有舍入尾差，精确分项见 CSV。

**9 条条件的逐项审计：**

| 条件 | 全量实际名次／比较对象 | 全量分差 | 共同集合实际名次／比较对象 | 共同集合分差 | 状态 |
| --- | --- | --- | --- | --- | --- |
| Fable 5.1 第一 | Claude Fable 5.1 (max with fallback) #1；GPT-6 Astra (max) #2 | 1.684 | Claude Fable 5.1 (max with fallback) #1；GPT-6 Astra (max) #2 | 1.684 | 两种口径均通过 |
| GPT-6 Astra 第二 | GPT-6 Astra (max) #2；Claude Fable 5 (with fallback) #3 | 0.525 | GPT-6 Astra (max) #2；Claude Fable 5 (with fallback) #3 | 0.525 | 两种口径均通过 |
| Kimi K3 高于 Gemini 3.8 Flash | Kimi K3 (max) #9；Gemini 3.8 Flash (high) #10 | 1.230 | Kimi K3 (max) #9；Gemini 3.8 Flash (high) #10 | 1.203 | 两种口径均通过 |
| GPT-5.5 高于 Muse Spark 1.3 | GPT-5.5 (xhigh) #7；Muse Spark 1.3 (max) #8 | 0.115 | GPT-5.5 (xhigh) #7；Muse Spark 1.3 (max) #8 | 0.132 | 两种口径均通过 |
| Qwen3.8 Max 高于 Qwen3.8 Flash-Next | Qwen3.8 Max #12；Qwen3.8-Flash-Next #32 | 8.543 | Qwen3.8 Max #12；Qwen3.8-Flash-Next #32 | 8.497 | 两种口径均通过 |
| Qwen3.8 2.4T A95B 高于 Qwen3.8 Flash-Next | Qwen3.8 2.4T A95B #24；Qwen3.8-Flash-Next #32 | 5.128 | Qwen3.8 2.4T A95B #24；Qwen3.8-Flash-Next #32 | 5.003 | 两种口径均通过 |
| GPT-5.6 Sol 高于 Claude Opus 5 | GPT-5.6 Sol (max) #4；Claude Opus 5 (max) #5 | 0.113 | GPT-5.6 Sol (max) #4；Claude Opus 5 (max) #5 | 0.084 | 两种口径均通过 |
| GPT-5.6 Terra 高于 Muse Spark 1.3 | GPT-5.6 Terra (max) #6；Muse Spark 1.3 (max) #8 | 0.506 | GPT-5.6 Terra (max) #6；Muse Spark 1.3 (max) #8 | 0.554 | 两种口径均通过 |
| Grok 4.6 高于 Grok 4.5 | Grok 4.6 (xhigh) #15；Grok 4.5 (high) #17 | 0.390 | Grok 4.6 (xhigh) #15；Grok 4.5 (high) #17 | 0.412 | 两种口径均通过 |

**此前排名异常涉及的旧模型：**以下完全按本套配置和缺测门槛处理。Gemini 3 Flash 没有人工排除；如未入榜，表中列出本套实际触发条件。此处名次不是额外筛选条件。

| 模型 | 名次 | 最终分 | 基础总分 | 缺Core数 | 缺项 | 资格原因 |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-5 mini (high) | #41 | 27.877 | 19.324 | 0 | 无 | 正常入榜 |
| Claude 4.5 Sonnet | #47 | 26.725 | 22.102 | 0 | 无 | 正常入榜 |
| Gemini 3 Flash | 未入榜 | — | — | 5 | Terminal-Bench v4.0; SciCode; AA-Briefcase; GDPval-AA v2; GDP.pdf | 领域全缺：编程、Agent／工具工作；累计缺至少四项 |

数据：[全量排名与分项](rankings_mc06.csv) · [剔除与缺项](excluded_mc06.csv) · [共同集合重算](common_mc06.csv)。

<a id="mc07"></a>

## 07 高难推理、指令／上下文单Core·接近等权

**设计目的：**仅将高难推理、指令／上下文设为单 Core，保留其他领域双 Core；按接近等权选择权重。

本套有 2 个单 Core 领域、3 个双 Core 领域，共 8 项。单 Core 领域都必须有观测，因此本套合格者最多可缺 **3 项**，且缺项必须分散在不同双 Core 领域。累计缺至少四项规则继续保留。

相对首套更换 Core 的领域：知识／科学、指令／上下文。

| 领域 | 结构 | Core项目 | 领域权重 | 单项基础总分权重 | 单项最高基础贡献 | 固定代表可用数 |
| --- | --- | --- | --- | --- | --- | --- |
| 编程 | 双 Core | Terminal-Bench v4.0 | 12% | 6% | 6 分 | 102 |
| 编程 | 双 Core | SciCode | 12% | 6% | 6 分 | 121 |
| Agent／工具工作 | 双 Core | AutomationBench-AA | 9% | 4.5% | 4.5 分 | 110 |
| Agent／工具工作 | 双 Core | τ³-Banking | 9% | 4.5% | 4.5 分 | 145 |
| 高难推理 | 单 Core | CritPt | 22% | 22% | 22 分 | 357 |
| 知识／科学 | 双 Core | AA-Omniscience Accuracy | 37% | 18.5% | 18.5 分 | 354 |
| 知识／科学 | 双 Core | GDP.pdf | 37% | 18.5% | 18.5 分 | 109 |
| 指令／上下文 | 单 Core | AA-LCR v1.1 | 20% | 20% | 20 分 | 354 |

- **编程：**Terminal-Bench v4.0：终端环境中的编程和工具任务；仅使用 v4.0 同配置实测；SciCode：科学研究场景中的编程能力。
- **Agent／工具工作：**AutomationBench-AA：自动化工作流执行；τ³-Banking：银行场景中的交互和工具使用。
- **高难推理：**CritPt：研究级物理推理。
- **知识／科学：**AA-Omniscience Accuracy：知识问答的回答准确率；GDP.pdf：PDF 文档任务；使用 all-pass 成绩。
- **指令／上下文：**AA-LCR v1.1：长上下文推理。

**领域权重取舍：**以每领域 20% 作为比较参照，本套提高高难推理（+2 个百分点）、知识／科学（+17 个百分点），降低编程（-8 个百分点）、Agent／工具工作（-11 个百分点）。提高权重会同时放大该领域的基础成绩、缺一项损失及封顶后的扩展影响；不会改变缺测剔除门槛。

**单项集中度：**本套最高单项基础权重为 **22%**（CritPt；如有并列，仅列一项）。这也等于该项对基础总分的最高分数贡献；实际贡献须乘该模型调整成绩／100。
**组合取舍：**单项承担领域全部基础权重，唯一项缺测即剔除；双项各半，缺项不重分配。扩展按相同规则重新拟合。

**覆盖与缺测：**入榜 120 个，剔除 351 个；剔除中领域全缺 351 个、累计缺至少四项 349 个、两者重叠 349 个，不能将两种原因直接相加。入榜者缺 0／1／2／3 项人数为 **98／10／3／9**。

| 领域 | 入榜者Core完整／不完整 | 保留扩展项目 | 启用拟合／保留数 |
| --- | --- | --- | --- |
| 编程 | 101／19 | benchmark:swe-bench-pro、benchmark:livecodebench | 1／2 |
| Agent／工具工作 | 108／12 | τ²-Bench Telecom、APEX-Agents-AA、benchmark:swe-bench-pro、benchmark:hle-tools、benchmark:mcp-atlas、benchmark:osworld-verified | 4／6 |
| 高难推理 | 120／0 | AIME 2025 | 1／1 |
| 知识／科学 | 108／12 | MMMU-Pro、benchmark:mmlu-pro | 1／2 |
| 指令／上下文 | 120／0 | benchmark:charxiv-no-tools | 0／1 |

本套全量拟合的领域扩展上限为 **30.870 分**；共同集合重新拟合后为 **30.724 分**。实际净贡献还受领域 100 分封顶及领域权重限制。

**实际算例：Claude Fable 5.1 (max with fallback)，本套第 1 名**

每行是一个已配置 Core，基础总分贡献已经乘领域权重并除以本领域 Core 数；未配置项不显示。

| 领域 | 已配置 Core | 调整后成绩 | 基础总分权重 | 基础总分贡献 |
| --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench v4.0 | 52.020 | 6% | 3.121 |
| 编程 | SciCode | 63.079 | 6% | 3.785 |
| Agent／工具工作 | AutomationBench-AA | 59.376 | 4.5% | 2.672 |
| Agent／工具工作 | τ³-Banking | 47.217 | 4.5% | 2.125 |
| 高难推理 | CritPt | 29.714 | 22% | 6.537 |
| 知识／科学 | AA-Omniscience Accuracy | 67.233 | 18.5% | 12.438 |
| 知识／科学 | GDP.pdf | 26.200 | 18.5% | 4.847 |
| 指令／上下文 | AA-LCR v1.1 | 85.333 | 20% | 17.067 |

| 领域 | Core数量 | 领域基础分 | 领域扩展加分 | 领域最终分 | 最终总分贡献 |
| --- | --- | --- | --- | --- | --- |
| 编程 | 2 | 57.549 | 2.362 | 59.911 | 7.189 |
| Agent／工具工作 | 2 | 53.296 | 8.873 | 62.169 | 5.595 |
| 高难推理 | 1 | 29.714 | 0.000 | 29.714 | 6.537 |
| 知识／科学 | 2 | 46.717 | 0.000 | 46.717 | 17.285 |
| 指令／上下文 | 1 | 85.333 | 0.000 | 85.333 | 17.067 |

8 项基础贡献合计 **52.592 分**；最终合计 **53.674 分**；计入领域封顶后的扩展净贡献 **1.082 分**。该配置缺 0 项。三位小数逐格相加可能有舍入尾差，精确分项见 CSV。

**9 条条件的逐项审计：**

| 条件 | 全量实际名次／比较对象 | 全量分差 | 共同集合实际名次／比较对象 | 共同集合分差 | 状态 |
| --- | --- | --- | --- | --- | --- |
| Fable 5.1 第一 | Claude Fable 5.1 (max with fallback) #1；GPT-6 Astra (max) #2 | 1.366 | Claude Fable 5.1 (max with fallback) #1；GPT-6 Astra (max) #2 | 1.366 | 两种口径均通过 |
| GPT-6 Astra 第二 | GPT-6 Astra (max) #2；Claude Fable 5 (with fallback) #3 | 1.090 | GPT-6 Astra (max) #2；Claude Fable 5 (with fallback) #3 | 1.090 | 两种口径均通过 |
| Kimi K3 高于 Gemini 3.8 Flash | Kimi K3 (max) #9；Gemini 3.8 Flash (high) #10 | 1.206 | Kimi K3 (max) #9；Gemini 3.8 Flash (high) #10 | 1.206 | 两种口径均通过 |
| GPT-5.5 高于 Muse Spark 1.3 | GPT-5.5 (xhigh) #7；Muse Spark 1.3 (max) #8 | 0.132 | GPT-5.5 (xhigh) #7；Muse Spark 1.3 (max) #8 | 0.132 | 两种口径均通过 |
| Qwen3.8 Max 高于 Qwen3.8 Flash-Next | Qwen3.8 Max #14；Qwen3.8-Flash-Next #27 | 4.057 | Qwen3.8 Max #14；Qwen3.8-Flash-Next #27 | 4.057 | 两种口径均通过 |
| Qwen3.8 2.4T A95B 高于 Qwen3.8 Flash-Next | Qwen3.8 2.4T A95B #25；Qwen3.8-Flash-Next #27 | 0.700 | Qwen3.8 2.4T A95B #25；Qwen3.8-Flash-Next #27 | 0.700 | 两种口径均通过 |
| GPT-5.6 Sol 高于 Claude Opus 5 | GPT-5.6 Sol (max) #4；Claude Opus 5 (max) #5 | 0.932 | GPT-5.6 Sol (max) #4；Claude Opus 5 (max) #5 | 0.932 | 两种口径均通过 |
| GPT-5.6 Terra 高于 Muse Spark 1.3 | GPT-5.6 Terra (max) #6；Muse Spark 1.3 (max) #8 | 0.755 | GPT-5.6 Terra (max) #6；Muse Spark 1.3 (max) #8 | 0.755 | 两种口径均通过 |
| Grok 4.6 高于 Grok 4.5 | Grok 4.6 (xhigh) #16；Grok 4.5 (high) #17 | 0.138 | Grok 4.6 (xhigh) #16；Grok 4.5 (high) #17 | 0.138 | 两种口径均通过 |

**此前排名异常涉及的旧模型：**以下完全按本套配置和缺测门槛处理。Gemini 3 Flash 没有人工排除；如未入榜，表中列出本套实际触发条件。此处名次不是额外筛选条件。

| 模型 | 名次 | 最终分 | 基础总分 | 缺Core数 | 缺项 | 资格原因 |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-5 mini (high) | #41 | 32.707 | 23.968 | 0 | 无 | 正常入榜 |
| Claude 4.5 Sonnet | #54 | 29.592 | 26.241 | 0 | 无 | 正常入榜 |
| Gemini 3 Flash | 未入榜 | — | — | 4 | Terminal-Bench v4.0; SciCode; AutomationBench-AA; GDP.pdf | 领域全缺：编程；累计缺至少四项 |

数据：[全量排名与分项](rankings_mc07.csv) · [剔除与缺项](excluded_mc07.csv) · [共同集合重算](common_mc07.csv)。

<a id="mc08"></a>

## 08 编程、高难推理单Core·接近等权

**设计目的：**仅将编程、高难推理设为单 Core，保留其他领域双 Core；按接近等权选择权重。

本套有 2 个单 Core 领域、3 个双 Core 领域，共 8 项。单 Core 领域都必须有观测，因此本套合格者最多可缺 **3 项**，且缺项必须分散在不同双 Core 领域。累计缺至少四项规则继续保留。

相对首套更换 Core 的领域：编程、知识／科学。

| 领域 | 结构 | Core项目 | 领域权重 | 单项基础总分权重 | 单项最高基础贡献 | 固定代表可用数 |
| --- | --- | --- | --- | --- | --- | --- |
| 编程 | 单 Core | SciCode | 12% | 12% | 12 分 | 121 |
| Agent／工具工作 | 双 Core | AutomationBench-AA | 9% | 4.5% | 4.5 分 | 110 |
| Agent／工具工作 | 双 Core | τ³-Banking | 9% | 4.5% | 4.5 分 | 145 |
| 高难推理 | 单 Core | CritPt | 36% | 36% | 36 分 | 357 |
| 知识／科学 | 双 Core | AA-Omniscience Accuracy | 20% | 10% | 10 分 | 354 |
| 知识／科学 | 双 Core | Humanity's Last Exam | 20% | 10% | 10 分 | 437 |
| 指令／上下文 | 双 Core | AA-LCR v1.1 | 23% | 11.5% | 11.5 分 | 354 |
| 指令／上下文 | 双 Core | GDP.pdf | 23% | 11.5% | 11.5 分 | 109 |

- **编程：**SciCode：科学研究场景中的编程能力。
- **Agent／工具工作：**AutomationBench-AA：自动化工作流执行；τ³-Banking：银行场景中的交互和工具使用。
- **高难推理：**CritPt：研究级物理推理。
- **知识／科学：**AA-Omniscience Accuracy：知识问答的回答准确率；Humanity's Last Exam：跨学科高难问题。
- **指令／上下文：**AA-LCR v1.1：长上下文推理；GDP.pdf：PDF 文档任务；使用 all-pass 成绩。

**领域权重取舍：**以每领域 20% 作为比较参照，本套提高高难推理（+16 个百分点）、指令／上下文（+3 个百分点），降低编程（-8 个百分点）、Agent／工具工作（-11 个百分点）。提高权重会同时放大该领域的基础成绩、缺一项损失及封顶后的扩展影响；不会改变缺测剔除门槛。

**单项集中度：**本套最高单项基础权重为 **36%**（CritPt；如有并列，仅列一项）。这也等于该项对基础总分的最高分数贡献；实际贡献须乘该模型调整成绩／100。
**组合取舍：**单项承担领域全部基础权重，唯一项缺测即剔除；双项各半，缺项不重分配。扩展按相同规则重新拟合。

**覆盖与缺测：**入榜 121 个，剔除 350 个；剔除中领域全缺 350 个、累计缺至少四项 327 个、两者重叠 327 个，不能将两种原因直接相加。入榜者缺 0／1／2／3 项人数为 **105／7／9／0**。

| 领域 | 入榜者Core完整／不完整 | 保留扩展项目 | 启用拟合／保留数 |
| --- | --- | --- | --- |
| 编程 | 121／0 | benchmark:swe-bench-pro、benchmark:livecodebench | 1／2 |
| Agent／工具工作 | 109／12 | τ²-Bench Telecom、APEX-Agents-AA、benchmark:swe-bench-pro、benchmark:hle-tools、benchmark:mcp-atlas、benchmark:osworld-verified | 4／6 |
| 高难推理 | 121／0 | AIME 2025 | 1／1 |
| 知识／科学 | 121／0 | MMMU-Pro、benchmark:mmlu-pro | 1／2 |
| 指令／上下文 | 108／13 | benchmark:charxiv-no-tools | 0／1 |

本套全量拟合的领域扩展上限为 **30.596 分**；共同集合重新拟合后为 **30.443 分**。实际净贡献还受领域 100 分封顶及领域权重限制。

**实际算例：Claude Fable 5.1 (max with fallback)，本套第 1 名**

每行是一个已配置 Core，基础总分贡献已经乘领域权重并除以本领域 Core 数；未配置项不显示。

| 领域 | 已配置 Core | 调整后成绩 | 基础总分权重 | 基础总分贡献 |
| --- | --- | --- | --- | --- |
| 编程 | SciCode | 63.079 | 12% | 7.569 |
| Agent／工具工作 | AutomationBench-AA | 59.376 | 4.5% | 2.672 |
| Agent／工具工作 | τ³-Banking | 47.217 | 4.5% | 2.125 |
| 高难推理 | CritPt | 29.714 | 36% | 10.697 |
| 知识／科学 | AA-Omniscience Accuracy | 67.233 | 10% | 6.723 |
| 知识／科学 | Humanity's Last Exam | 59.129 | 10% | 5.913 |
| 指令／上下文 | AA-LCR v1.1 | 85.333 | 11.5% | 9.813 |
| 指令／上下文 | GDP.pdf | 26.200 | 11.5% | 3.013 |

| 领域 | Core数量 | 领域基础分 | 领域扩展加分 | 领域最终分 | 最终总分贡献 |
| --- | --- | --- | --- | --- | --- |
| 编程 | 1 | 63.079 | 0.779 | 63.858 | 7.663 |
| Agent／工具工作 | 2 | 53.296 | 8.873 | 62.169 | 5.595 |
| 高难推理 | 1 | 29.714 | 0.000 | 29.714 | 10.697 |
| 知识／科学 | 2 | 63.181 | 0.000 | 63.181 | 12.636 |
| 指令／上下文 | 2 | 55.767 | 0.000 | 55.767 | 12.826 |

8 项基础贡献合计 **48.526 分**；最终合计 **49.418 分**；计入领域封顶后的扩展净贡献 **0.892 分**。该配置缺 0 项。三位小数逐格相加可能有舍入尾差，精确分项见 CSV。

**9 条条件的逐项审计：**

| 条件 | 全量实际名次／比较对象 | 全量分差 | 共同集合实际名次／比较对象 | 共同集合分差 | 状态 |
| --- | --- | --- | --- | --- | --- |
| Fable 5.1 第一 | Claude Fable 5.1 (max with fallback) #1；GPT-6 Astra (max) #2 | 1.706 | Claude Fable 5.1 (max with fallback) #1；GPT-6 Astra (max) #2 | 1.706 | 两种口径均通过 |
| GPT-6 Astra 第二 | GPT-6 Astra (max) #2；Claude Fable 5 (with fallback) #3 | 0.369 | GPT-6 Astra (max) #2；Claude Fable 5 (with fallback) #3 | 0.369 | 两种口径均通过 |
| Kimi K3 高于 Gemini 3.8 Flash | Kimi K3 (max) #9；Gemini 3.8 Flash (high) #10 | 2.334 | Kimi K3 (max) #9；Gemini 3.8 Flash (high) #10 | 2.334 | 两种口径均通过 |
| GPT-5.5 高于 Muse Spark 1.3 | GPT-5.5 (xhigh) #7；Muse Spark 1.3 (max) #8 | 0.144 | GPT-5.5 (xhigh) #7；Muse Spark 1.3 (max) #8 | 0.144 | 两种口径均通过 |
| Qwen3.8 Max 高于 Qwen3.8 Flash-Next | Qwen3.8 Max #16；Qwen3.8-Flash-Next #29 | 4.570 | Qwen3.8 Max #16；Qwen3.8-Flash-Next #29 | 4.572 | 两种口径均通过 |
| Qwen3.8 2.4T A95B 高于 Qwen3.8 Flash-Next | Qwen3.8 2.4T A95B #19；Qwen3.8-Flash-Next #29 | 3.478 | Qwen3.8 2.4T A95B #19；Qwen3.8-Flash-Next #29 | 3.415 | 两种口径均通过 |
| GPT-5.6 Sol 高于 Claude Opus 5 | GPT-5.6 Sol (max) #4；Claude Opus 5 (max) #5 | 0.154 | GPT-5.6 Sol (max) #4；Claude Opus 5 (max) #5 | 0.154 | 两种口径均通过 |
| GPT-5.6 Terra 高于 Muse Spark 1.3 | GPT-5.6 Terra (max) #6；Muse Spark 1.3 (max) #8 | 0.453 | GPT-5.6 Terra (max) #6；Muse Spark 1.3 (max) #8 | 0.453 | 两种口径均通过 |
| Grok 4.6 高于 Grok 4.5 | Grok 4.6 (xhigh) #14；Grok 4.5 (high) #17 | 1.062 | Grok 4.6 (xhigh) #14；Grok 4.5 (high) #17 | 1.062 | 两种口径均通过 |

**此前排名异常涉及的旧模型：**以下完全按本套配置和缺测门槛处理。Gemini 3 Flash 没有人工排除；如未入榜，表中列出本套实际触发条件。此处名次不是额外筛选条件。

| 模型 | 名次 | 最终分 | 基础总分 | 缺Core数 | 缺项 | 资格原因 |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-5 mini (high) | #31 | 32.049 | 19.595 | 0 | 无 | 正常入榜 |
| Claude 4.5 Sonnet | #48 | 26.996 | 21.618 | 0 | 无 | 正常入榜 |
| Gemini 3 Flash | 未入榜 | — | — | 3 | SciCode; AutomationBench-AA; GDP.pdf | 领域全缺：编程 |

数据：[全量排名与分项](rankings_mc08.csv) · [剔除与缺项](excluded_mc08.csv) · [共同集合重算](common_mc08.csv)。

<a id="mc09"></a>

## 09 知识／科学、指令／上下文单Core·接近等权

**设计目的：**仅将知识／科学、指令／上下文设为单 Core，保留其他领域双 Core；按接近等权选择权重。

本套有 2 个单 Core 领域、3 个双 Core 领域，共 8 项。单 Core 领域都必须有观测，因此本套合格者最多可缺 **3 项**，且缺项必须分散在不同双 Core 领域。累计缺至少四项规则继续保留。

相对首套更换 Core 的领域：高难推理、指令／上下文。

| 领域 | 结构 | Core项目 | 领域权重 | 单项基础总分权重 | 单项最高基础贡献 | 固定代表可用数 |
| --- | --- | --- | --- | --- | --- | --- |
| 编程 | 双 Core | Terminal-Bench v4.0 | 9% | 4.5% | 4.5 分 | 102 |
| 编程 | 双 Core | SciCode | 9% | 4.5% | 4.5 分 | 121 |
| Agent／工具工作 | 双 Core | AutomationBench-AA | 18% | 9% | 9 分 | 110 |
| Agent／工具工作 | 双 Core | τ³-Banking | 18% | 9% | 9 分 | 145 |
| 高难推理 | 双 Core | CritPt | 37% | 18.5% | 18.5 分 | 357 |
| 高难推理 | 双 Core | AA-LCR v1.1 | 37% | 18.5% | 18.5 分 | 354 |
| 知识／科学 | 单 Core | AA-Omniscience Accuracy | 22% | 22% | 22 分 | 354 |
| 指令／上下文 | 单 Core | GDP.pdf | 14% | 14% | 14 分 | 109 |

- **编程：**Terminal-Bench v4.0：终端环境中的编程和工具任务；仅使用 v4.0 同配置实测；SciCode：科学研究场景中的编程能力。
- **Agent／工具工作：**AutomationBench-AA：自动化工作流执行；τ³-Banking：银行场景中的交互和工具使用。
- **高难推理：**CritPt：研究级物理推理；AA-LCR v1.1：长上下文推理。
- **知识／科学：**AA-Omniscience Accuracy：知识问答的回答准确率。
- **指令／上下文：**GDP.pdf：PDF 文档任务；使用 all-pass 成绩。

**领域权重取舍：**以每领域 20% 作为比较参照，本套提高高难推理（+17 个百分点）、知识／科学（+2 个百分点），降低编程（-11 个百分点）、Agent／工具工作（-2 个百分点）、指令／上下文（-6 个百分点）。提高权重会同时放大该领域的基础成绩、缺一项损失及封顶后的扩展影响；不会改变缺测剔除门槛。

**单项集中度：**本套最高单项基础权重为 **22%**（AA-Omniscience Accuracy；如有并列，仅列一项）。这也等于该项对基础总分的最高分数贡献；实际贡献须乘该模型调整成绩／100。
**组合取舍：**单项承担领域全部基础权重，唯一项缺测即剔除；双项各半，缺项不重分配。扩展按相同规则重新拟合。

**覆盖与缺测：**入榜 109 个，剔除 362 个；剔除中领域全缺 362 个、累计缺至少四项 349 个、两者重叠 349 个，不能将两种原因直接相加。入榜者缺 0／1／2／3 项人数为 **98／8／3／0**。

| 领域 | 入榜者Core完整／不完整 | 保留扩展项目 | 启用拟合／保留数 |
| --- | --- | --- | --- |
| 编程 | 99／10 | benchmark:swe-bench-pro、benchmark:livecodebench | 1／2 |
| Agent／工具工作 | 106／3 | τ²-Bench Telecom、APEX-Agents-AA、benchmark:swe-bench-pro、benchmark:hle-tools、benchmark:mcp-atlas、benchmark:osworld-verified | 4／6 |
| 高难推理 | 108／1 | AIME 2025 | 1／1 |
| 知识／科学 | 109／0 | MMMU-Pro、benchmark:mmlu-pro | 1／2 |
| 指令／上下文 | 109／0 | benchmark:charxiv-no-tools | 0／1 |

本套全量拟合的领域扩展上限为 **30.975 分**；共同集合重新拟合后为 **30.800 分**。实际净贡献还受领域 100 分封顶及领域权重限制。

**实际算例：Claude Fable 5.1 (max with fallback)，本套第 1 名**

每行是一个已配置 Core，基础总分贡献已经乘领域权重并除以本领域 Core 数；未配置项不显示。

| 领域 | 已配置 Core | 调整后成绩 | 基础总分权重 | 基础总分贡献 |
| --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench v4.0 | 52.020 | 4.5% | 2.341 |
| 编程 | SciCode | 63.079 | 4.5% | 2.839 |
| Agent／工具工作 | AutomationBench-AA | 59.376 | 9% | 5.344 |
| Agent／工具工作 | τ³-Banking | 47.217 | 9% | 4.249 |
| 高难推理 | CritPt | 29.714 | 18.5% | 5.497 |
| 高难推理 | AA-LCR v1.1 | 85.333 | 18.5% | 15.787 |
| 知识／科学 | AA-Omniscience Accuracy | 67.233 | 22% | 14.791 |
| 指令／上下文 | GDP.pdf | 26.200 | 14% | 3.668 |

| 领域 | Core数量 | 领域基础分 | 领域扩展加分 | 领域最终分 | 最终总分贡献 |
| --- | --- | --- | --- | --- | --- |
| 编程 | 2 | 57.549 | 2.362 | 59.911 | 5.392 |
| Agent／工具工作 | 2 | 53.296 | 8.873 | 62.169 | 11.190 |
| 高难推理 | 2 | 57.524 | 0.000 | 57.524 | 21.284 |
| 知识／科学 | 1 | 67.233 | 0.000 | 67.233 | 14.791 |
| 指令／上下文 | 1 | 26.200 | 0.000 | 26.200 | 3.668 |

8 项基础贡献合计 **54.516 分**；最终合计 **56.326 分**；计入领域封顶后的扩展净贡献 **1.810 分**。该配置缺 0 项。三位小数逐格相加可能有舍入尾差，精确分项见 CSV。

**9 条条件的逐项审计：**

| 条件 | 全量实际名次／比较对象 | 全量分差 | 共同集合实际名次／比较对象 | 共同集合分差 | 状态 |
| --- | --- | --- | --- | --- | --- |
| Fable 5.1 第一 | Claude Fable 5.1 (max with fallback) #1；GPT-6 Astra (max) #2 | 2.328 | Claude Fable 5.1 (max with fallback) #1；GPT-6 Astra (max) #2 | 2.328 | 两种口径均通过 |
| GPT-6 Astra 第二 | GPT-6 Astra (max) #2；Claude Fable 5 (with fallback) #3 | 0.409 | GPT-6 Astra (max) #2；Claude Fable 5 (with fallback) #3 | 0.409 | 两种口径均通过 |
| Kimi K3 高于 Gemini 3.8 Flash | Kimi K3 (max) #9；Gemini 3.8 Flash (high) #10 | 0.643 | Kimi K3 (max) #9；Gemini 3.8 Flash (high) #10 | 0.637 | 两种口径均通过 |
| GPT-5.5 高于 Muse Spark 1.3 | GPT-5.5 (xhigh) #7；Muse Spark 1.3 (max) #8 | 0.109 | GPT-5.5 (xhigh) #7；Muse Spark 1.3 (max) #8 | 0.109 | 两种口径均通过 |
| Qwen3.8 Max 高于 Qwen3.8 Flash-Next | Qwen3.8 Max #14；Qwen3.8-Flash-Next #28 | 4.062 | Qwen3.8 Max #14；Qwen3.8-Flash-Next #28 | 4.077 | 两种口径均通过 |
| Qwen3.8 2.4T A95B 高于 Qwen3.8 Flash-Next | Qwen3.8 2.4T A95B #22；Qwen3.8-Flash-Next #28 | 1.331 | Qwen3.8 2.4T A95B #22；Qwen3.8-Flash-Next #28 | 1.386 | 两种口径均通过 |
| GPT-5.6 Sol 高于 Claude Opus 5 | GPT-5.6 Sol (max) #4；Claude Opus 5 (max) #5 | 0.182 | GPT-5.6 Sol (max) #4；Claude Opus 5 (max) #5 | 0.182 | 两种口径均通过 |
| GPT-5.6 Terra 高于 Muse Spark 1.3 | GPT-5.6 Terra (max) #6；Muse Spark 1.3 (max) #8 | 0.497 | GPT-5.6 Terra (max) #6；Muse Spark 1.3 (max) #8 | 0.487 | 两种口径均通过 |
| Grok 4.6 高于 Grok 4.5 | Grok 4.6 (xhigh) #12；Grok 4.5 (high) #13 | 0.130 | Grok 4.6 (xhigh) #12；Grok 4.5 (high) #13 | 0.130 | 两种口径均通过 |

**此前排名异常涉及的旧模型：**以下完全按本套配置和缺测门槛处理。Gemini 3 Flash 没有人工排除；如未入榜，表中列出本套实际触发条件。此处名次不是额外筛选条件。

| 模型 | 名次 | 最终分 | 基础总分 | 缺Core数 | 缺项 | 资格原因 |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-5 mini (high) | #57 | 29.676 | 23.781 | 0 | 无 | 正常入榜 |
| Claude 4.5 Sonnet | #52 | 30.400 | 27.084 | 0 | 无 | 正常入榜 |
| Gemini 3 Flash | 未入榜 | — | — | 4 | Terminal-Bench v4.0; SciCode; AutomationBench-AA; GDP.pdf | 领域全缺：编程、指令／上下文；累计缺至少四项 |

数据：[全量排名与分项](rankings_mc09.csv) · [剔除与缺项](excluded_mc09.csv) · [共同集合重算](common_mc09.csv)。

<a id="mc10"></a>

## 10 高难推理、指令／上下文单Core·接近等权

**设计目的：**仅将高难推理、指令／上下文设为单 Core，保留其他领域双 Core；按接近等权选择权重。

本套有 2 个单 Core 领域、3 个双 Core 领域，共 8 项。单 Core 领域都必须有观测，因此本套合格者最多可缺 **3 项**，且缺项必须分散在不同双 Core 领域。累计缺至少四项规则继续保留。

相对首套更换 Core 的领域：Agent／工具工作、知识／科学、指令／上下文。

| 领域 | 结构 | Core项目 | 领域权重 | 单项基础总分权重 | 单项最高基础贡献 | 固定代表可用数 |
| --- | --- | --- | --- | --- | --- | --- |
| 编程 | 双 Core | Terminal-Bench v4.0 | 11% | 5.5% | 5.5 分 | 102 |
| 编程 | 双 Core | SciCode | 11% | 5.5% | 5.5 分 | 121 |
| Agent／工具工作 | 双 Core | τ³-Banking | 9% | 4.5% | 4.5 分 | 145 |
| Agent／工具工作 | 双 Core | GDPval-AA v2 | 9% | 4.5% | 4.5 分 | 170 |
| 高难推理 | 单 Core | CritPt | 21% | 21% | 21 分 | 357 |
| 知识／科学 | 双 Core | AA-Omniscience Accuracy | 39% | 19.5% | 19.5 分 | 354 |
| 知识／科学 | 双 Core | GDP.pdf | 39% | 19.5% | 19.5 分 | 109 |
| 指令／上下文 | 单 Core | AA-LCR v1.1 | 20% | 20% | 20 分 | 354 |

- **编程：**Terminal-Bench v4.0：终端环境中的编程和工具任务；仅使用 v4.0 同配置实测；SciCode：科学研究场景中的编程能力。
- **Agent／工具工作：**τ³-Banking：银行场景中的交互和工具使用；GDPval-AA v2：专业知识工作交付；使用 Elo 换算分。
- **高难推理：**CritPt：研究级物理推理。
- **知识／科学：**AA-Omniscience Accuracy：知识问答的回答准确率；GDP.pdf：PDF 文档任务；使用 all-pass 成绩。
- **指令／上下文：**AA-LCR v1.1：长上下文推理。

**领域权重取舍：**以每领域 20% 作为比较参照，本套提高高难推理（+1 个百分点）、知识／科学（+19 个百分点），降低编程（-9 个百分点）、Agent／工具工作（-11 个百分点）。提高权重会同时放大该领域的基础成绩、缺一项损失及封顶后的扩展影响；不会改变缺测剔除门槛。

**单项集中度：**本套最高单项基础权重为 **21%**（CritPt；如有并列，仅列一项）。这也等于该项对基础总分的最高分数贡献；实际贡献须乘该模型调整成绩／100。
**组合取舍：**单项承担领域全部基础权重，唯一项缺测即剔除；双项各半，缺项不重分配。扩展按相同规则重新拟合。

**覆盖与缺测：**入榜 120 个，剔除 351 个；剔除中领域全缺 351 个、累计缺至少四项 331 个、两者重叠 331 个，不能将两种原因直接相加。入榜者缺 0／1／2／3 项人数为 **98／13／9／0**。

| 领域 | 入榜者Core完整／不完整 | 保留扩展项目 | 启用拟合／保留数 |
| --- | --- | --- | --- |
| 编程 | 101／19 | benchmark:swe-bench-pro、benchmark:livecodebench | 1／2 |
| Agent／工具工作 | 120／0 | τ²-Bench Telecom、APEX-Agents-AA、benchmark:swe-bench-pro、benchmark:hle-tools、benchmark:mcp-atlas、benchmark:osworld-verified | 4／6 |
| 高难推理 | 120／0 | AIME 2025 | 1／1 |
| 知识／科学 | 108／12 | MMMU-Pro、benchmark:mmlu-pro | 1／2 |
| 指令／上下文 | 120／0 | benchmark:charxiv-no-tools | 0／1 |

本套全量拟合的领域扩展上限为 **28.835 分**；共同集合重新拟合后为 **28.819 分**。实际净贡献还受领域 100 分封顶及领域权重限制。

**实际算例：Claude Fable 5.1 (max with fallback)，本套第 1 名**

每行是一个已配置 Core，基础总分贡献已经乘领域权重并除以本领域 Core 数；未配置项不显示。

| 领域 | 已配置 Core | 调整后成绩 | 基础总分权重 | 基础总分贡献 |
| --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench v4.0 | 52.020 | 5.5% | 2.861 |
| 编程 | SciCode | 63.079 | 5.5% | 3.469 |
| Agent／工具工作 | τ³-Banking | 47.217 | 4.5% | 2.125 |
| Agent／工具工作 | GDPval-AA v2 | 63.182 | 4.5% | 2.843 |
| 高难推理 | CritPt | 29.714 | 21% | 6.240 |
| 知识／科学 | AA-Omniscience Accuracy | 67.233 | 19.5% | 13.110 |
| 知识／科学 | GDP.pdf | 26.200 | 19.5% | 5.109 |
| 指令／上下文 | AA-LCR v1.1 | 85.333 | 20% | 17.067 |

| 领域 | Core数量 | 领域基础分 | 领域扩展加分 | 领域最终分 | 最终总分贡献 |
| --- | --- | --- | --- | --- | --- |
| 编程 | 2 | 57.549 | 2.362 | 59.911 | 6.590 |
| Agent／工具工作 | 2 | 55.199 | 7.055 | 62.254 | 5.603 |
| 高难推理 | 1 | 29.714 | 0.000 | 29.714 | 6.240 |
| 知识／科学 | 2 | 46.717 | 0.000 | 46.717 | 18.219 |
| 指令／上下文 | 1 | 85.333 | 0.000 | 85.333 | 17.067 |

8 项基础贡献合计 **52.825 分**；最终合计 **53.719 分**；计入领域封顶后的扩展净贡献 **0.895 分**。该配置缺 0 项。三位小数逐格相加可能有舍入尾差，精确分项见 CSV。

**9 条条件的逐项审计：**

| 条件 | 全量实际名次／比较对象 | 全量分差 | 共同集合实际名次／比较对象 | 共同集合分差 | 状态 |
| --- | --- | --- | --- | --- | --- |
| Fable 5.1 第一 | Claude Fable 5.1 (max with fallback) #1；GPT-6 Astra (max) #2 | 2.022 | Claude Fable 5.1 (max with fallback) #1；GPT-6 Astra (max) #2 | 2.022 | 两种口径均通过 |
| GPT-6 Astra 第二 | GPT-6 Astra (max) #2；Claude Fable 5 (with fallback) #3 | 0.398 | GPT-6 Astra (max) #2；Claude Fable 5 (with fallback) #3 | 0.398 | 两种口径均通过 |
| Kimi K3 高于 Gemini 3.8 Flash | Kimi K3 (max) #9；Gemini 3.8 Flash (high) #10 | 1.459 | Kimi K3 (max) #9；Gemini 3.8 Flash (high) #10 | 1.459 | 两种口径均通过 |
| GPT-5.5 高于 Muse Spark 1.3 | GPT-5.5 (xhigh) #7；Muse Spark 1.3 (max) #8 | 0.095 | GPT-5.5 (xhigh) #7；Muse Spark 1.3 (max) #8 | 0.113 | 两种口径均通过 |
| Qwen3.8 Max 高于 Qwen3.8 Flash-Next | Qwen3.8 Max #14；Qwen3.8-Flash-Next #26 | 4.183 | Qwen3.8 Max #14；Qwen3.8-Flash-Next #26 | 4.183 | 两种口径均通过 |
| Qwen3.8 2.4T A95B 高于 Qwen3.8 Flash-Next | Qwen3.8 2.4T A95B #25；Qwen3.8-Flash-Next #26 | 0.298 | Qwen3.8 2.4T A95B #25；Qwen3.8-Flash-Next #26 | 0.298 | 两种口径均通过 |
| GPT-5.6 Sol 高于 Claude Opus 5 | GPT-5.6 Sol (max) #4；Claude Opus 5 (max) #5 | 0.775 | GPT-5.6 Sol (max) #4；Claude Opus 5 (max) #5 | 0.775 | 两种口径均通过 |
| GPT-5.6 Terra 高于 Muse Spark 1.3 | GPT-5.6 Terra (max) #6；Muse Spark 1.3 (max) #8 | 0.128 | GPT-5.6 Terra (max) #6；Muse Spark 1.3 (max) #8 | 0.128 | 两种口径均通过 |
| Grok 4.6 高于 Grok 4.5 | Grok 4.6 (xhigh) #16；Grok 4.5 (high) #17 | 0.088 | Grok 4.6 (xhigh) #16；Grok 4.5 (high) #17 | 0.088 | 两种口径均通过 |

**此前排名异常涉及的旧模型：**以下完全按本套配置和缺测门槛处理。Gemini 3 Flash 没有人工排除；如未入榜，表中列出本套实际触发条件。此处名次不是额外筛选条件。

| 模型 | 名次 | 最终分 | 基础总分 | 缺Core数 | 缺项 | 资格原因 |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-5 mini (high) | #43 | 32.229 | 24.670 | 0 | 无 | 正常入榜 |
| Claude 4.5 Sonnet | #55 | 29.610 | 26.849 | 0 | 无 | 正常入榜 |
| Gemini 3 Flash | 未入榜 | — | — | 4 | Terminal-Bench v4.0; SciCode; GDPval-AA v2; GDP.pdf | 领域全缺：编程；累计缺至少四项 |

数据：[全量排名与分项](rankings_mc10.csv) · [剔除与缺项](excluded_mc10.csv) · [共同集合重算](common_mc10.csv)。

## 如何判断这些结果

先比较 Core 的任务含义、单项集中度和覆盖，再比较权重与扩展贡献。减少 Core 数可以缓解不必要的旧测试缺测惩罚，却不会自动消除覆盖偏差或测试可刷分问题。测试在本轮获准进入 Core，也不表示已经获得独立防污染或抗刷分验证。
这些组合是在同一份冻结成绩上按指定次序筛选的，没有跨时间留出验证；共同集合和小幅权重扰动也不能替代新数据验证。正式采用前，应检查全榜表现和后续快照，尤其关注单 Core 高权重测试及缺测引起的资格变化。
