# 十套双 Core 方案：规则、组合与结果

本轮优先比较不同 Core 组合，并如实报告此前的排序偏好。十套均为五领域各 20%，每领域两个不同测试；每套十个 Core 槽位来自十个不同测试家族。
完整 Top30 和跨方案名次对照另见 [TOP30_COMPARISON.md](TOP30_COMPARISON.md)。

输入快照：2026-09-08T23:56:02+00:00。共 644 个配置，先按模型组固定最高 variantPriority 配置，得到 471 个代表配置，再对各方案检查缺测；不会因某方案缺测而改选低档配置。
原始数据和正式 Scheme 18 不变。这是供选择的实验榜；各方案按同一公式评分，模型名称只用于展示和事后审计。
输入文件哈希、换算参数和拟合结果见 [run.json](run.json)。全量成绩保留未舍入分数；本文显示三位小数，名次仍按原值确定，完全同分按 slug 排序。

## 全部方案共用的计算规则

1. 每领域两个 Core 均缺测，立即剔除；或者十项累计缺测至少四项，也剔除。两条规则取并集。因此入榜者允许缺 0–3 项，但不能集中成某领域全缺。实测 0 是有效观测，不计缺测。
2. 每个 Core 的调整后成绩固定占所在领域基础分的一半。缺一项时，其半份贡献为 0，另一项仍只占一半；缺测标记保留，不伪造原始零分。五领域各占总分 20%，所以每个 Core 最多贡献总分 10 分。
3. 调整后值统一在 0–100 分尺度。百分比项目沿用采集后的百分制；AA-Briefcase、GDPval-AA v2 使用 `clip((Elo−500)/2000×100, 0, 100)`。它们是 Elo 的线性换算，并非成功率，纳入 Core 会增加尺度选择对总分的影响。没有为指定模型单独设置权重或加减分。
4. Terminal 只用同一配置：优先 v4.0 实测；无 v4 时，v2.1 先通过重叠代表配置的非负斜率线性回归换算到 v4 尺度，再乘 0.95；仍不可用时，Hard 换算后乘 0.90。换算成功算一个 Core 可用。v4 实测 0 不回退，也不借其他配置的成绩。拟合少于五对时停用相应换算。
5. 扩展池沿用 Scheme 18 的正残差加分，但移除本方案所有 Core 家族，防止同一个测试换名或换版本重复计分。只有某领域两项 Core 都可用的模型，才能用于该领域扩展拟合和获得加分；缺一项时该领域加分固定为 0。每个扩展至少五个完整观测才拟合，斜率限制为非负。
6. 每领域先将基础分和扩展加分相加，再封顶 100；总分取五领域等权平均。每方案按自己的入榜集合拟合扩展，另在所有方案共同入榜的固定集合重新拟合一次，供比较人群变化的影响。

设 `aᵢ` 为 Core 调整后成绩，`Iᵢ` 表示其是否有观测；`rⱼ=max(0, 扩展实测ⱼ−预测ⱼ)`。

```text
领域基础分 B = 0.5 × I₁ × a₁ + 0.5 × I₂ × a₂
上限 C = 全部正残差的均值 + √2 × 总体标准差（无正残差时为 0）
领域加分 E = min(C, ln(1 + Σ(expm1(rⱼ))))，仅两项 Core 都可用时
领域最终分 S = min(100, B + E)
基础总分 = Σ(0.2 × B)；最终总分 = Σ(0.2 × S)
旧版 Terminal 调整值 = 折扣 × clip(截距 + 非负斜率 × 旧版实测, 0, 100)
```

例如两项为 80、60，领域基础分为 70，贡献总分 14；若 60 那项缺测，领域基础分变成 40，贡献总分 8，该领域也不能获得扩展加分。真实的 80、0 同样产生基础分 40，但不计缺测，且可参与扩展拟合及加分。
缺测会同时影响资格、基础分和该领域能否获得扩展加分，因此不能把实验分数理解成已测项目的平均正确率。

### 本次 Terminal 版本映射

下面的参数由同时具有旧版和 v4 实测的固定代表配置拟合，十套方案共用。MAE 是将回归预测截断到 0–100 后、尚未乘折扣时的样本内平均绝对误差；它来自拟合样本自身，不能当作新模型的误差保证。

| 旧版本 | 是否启用 | 重叠配置对数 | 截距 | 非负斜率 | 样本内 MAE | 换算后折扣 |
| --- | --- | --- | --- | --- | --- | --- |
| Terminal-Bench v2.1 | 是 | 102 | -6.199444 | 0.268522 | 6.056 | 0.95 |
| Terminal-Bench Hard | 是 | 65 | -4.502315 | 0.277955 | 3.938 | 0.90 |

旧版换算值属于样本内回归产生的估算，历史版本与 v4 的任务构成、难度差异可能使个别模型偏离这条映射。精确系数保存在 [run.json](run.json)。

## 十套方案概览

| 方案 | 组合目的 | 入榜 | 剔除 | 缺0／1／2／3项人数 | 第一名 | 旧偏好满足 | 共同集合满足 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [01 最新任务基线](#dc01) | 采用当前任务型、科学推理与知识测试，作为其他九套的共同参照。 | 144 | 327 | 105／7／10／22 | Claude Fable 5.1 (max with fallback) | 4/6 | 4/6 |
| [02 Banking＋知识工作](#dc02) | 把 Agent 的 Automation 换成 Briefcase，比较银行操作与长流程知识工作交付。 | 148 | 323 | 102／10／11／25 | Claude Fable 5.1 (max with fallback) | 4/6 | 4/6 |
| [03 自动化＋知识工作](#dc03) | 把 Agent 的 Banking 换成 Briefcase，强调 SaaS 自动化及工作成果交付。 | 118 | 353 | 100／11／0／7 | Claude Fable 5.1 (max with fallback) | 5/6 | 5/6 |
| [04 自动化＋职业任务](#dc04) | 把 Banking 换成 GDPval v2，观察职业任务能力对 Agent 板块的影响。 | 168 | 303 | 105／7／10／46 | Claude Fable 5.1 (max with fallback) | 5/6 | 5/6 |
| [05 指令遵循对照](#dc05) | 上下文用 LCR＋IFBench，将 PDF 问答替换为指令遵循测试。 | 144 | 327 | 69／42／32／1 | Claude Fable 5 (with fallback) | 3/6 | 3/6 |
| [06 算法编程对照](#dc06) | 用 LiveCodeBench 替代 SciCode，比较算法代码能力与终端任务能力。 | 144 | 327 | 29／78／17／20 | Claude Fable 5.1 (max with fallback) | 4/6 | 4/6 |
| [07 算法＋指令双替换](#dc07) | 同时采用 LiveCodeBench 和 IFBench，检验两项历史高覆盖测试共同进入 Core 的影响。 | 144 | 327 | 30／52／50／12 | Claude Fable 5 (with fallback) | 3/6 | 3/6 |
| [08 数学竞赛对照](#dc08) | 推理用 CritPt＋AIME 2025，将广域 HLE 替换为数学竞赛。 | 133 | 338 | 28／78／7／20 | Claude Fable 5.1 (max with fallback) | 4/6 | 4/6 |
| [09 多模态知识对照](#dc09) | 知识用 Omniscience Accuracy＋MMMU-Pro，加入图像与跨学科理解。 | 139 | 332 | 52／54／10／23 | GPT-6 Astra (max) | 2/6 | 2/6 |
| [10 电信＋银行覆盖对照](#dc10) | Agent 用 Telecom＋Banking，观察较高历史覆盖能保留多少模型。 | 332 | 139 | 68／43／32／189 | Claude Fable 5 (with fallback) | 4/6 | 4/6 |

偏好审计沿用前轮稳健门槛：名次关系成立且分差大于 0.05 分才记“满足”。若次序成立但分差不足，逐项表会明确标注。

共同集合含 **112** 个完全相同的代表配置，各方案在此集合重新拟合扩展。全量比较包含 Core 组合、人群和拟合参数的共同变化；共同集合比较固定了人群，仍保留不同 Core 对基础分、扩展池和拟合的影响。

## 数据覆盖清单

以下列出至少 100 个配置有数据的测试；Terminal effective 一行是回退合成，其余按直接观测口径统计。配置数包含推理档位；模型组数为有任一配置成绩的去重数；固定代表数才对应本轮预先选定配置上的可用数。测试有 100 个配置，不等于十项组合能让这些模型全部入榜。

| 测试 | 配置数 | 模型组数 | 固定代表数 | 机构数 | 说明 |
| --- | --- | --- | --- | --- | --- |
| GPQA Diamond | 612 | 445 | 445 | 58 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| Humanity's Last Exam | 607 | 437 | 437 | 58 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| Terminal-Bench effective | 528 | 362 | 362 | 55 | v4 优先、旧版换算折扣后的合成槽位，含估算 |
| CritPt | 520 | 357 | 357 | 55 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| AA-Omniscience Accuracy | 519 | 354 | 354 | 55 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| AA-Omniscience Non-Hallucination Rate | 519 | 354 | 354 | 55 | 同一 Omniscience 家族的另一指标 |
| AA-LCR | 516 | 357 | 354 | 54 | 当前 AA-LCR v1.1 的兼容别名，不重复计权 |
| AA-LCR v1.1 | 516 | 357 | 354 | 54 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| IFBench | 450 | 321 | 321 | 49 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| τ²-Bench Telecom | 440 | 313 | 313 | 48 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| Terminal-Bench Hard | 432 | 305 | 305 | 48 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| LiveCodeBench | 343 | 269 | 269 | 40 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| AIME 2025 | 270 | 199 | 199 | 36 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| MMMU-Pro | 258 | 152 | 147 | 28 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| GDPval-AA | 239 | 174 | 170 | 40 | 历史留存列，不作为新 Core |
| GDPval-AA v2 | 239 | 174 | 170 | 40 | Elo 换算分，非原生通过率 |
| Terminal-Bench v2.1 | 236 | 176 | 172 | 40 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| τ³-Banking | 204 | 149 | 145 | 36 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| SciCode | 167 | 122 | 121 | 35 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| AA-Briefcase | 159 | 113 | 112 | 28 | Elo 换算分，非原生通过率 |
| AutomationBench-AA | 153 | 111 | 110 | 27 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| GDP.pdf | 147 | 110 | 109 | 26 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| Terminal-Bench v4.0 | 142 | 103 | 102 | 26 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |

Terminal effective 是按上述回退规则合成的一个槽位；原始各版本的覆盖不能相加。兼容别名和同家族指标不重复占 Core。完整清单见 [coverage.csv](coverage.csv)。

<a id="dc01"></a>

## 01 最新任务基线

**设计目的：**采用当前任务型、科学推理与知识测试，作为其他九套的共同参照。

本方案作为本轮对照起点；后续变化以此组合为参照，编号不代表推荐顺序。

| 领域 | Core 1 | Core 2 | 领域权重 | 两项在基础总分的权重 | 固定代表可用数1／2 | 入榜者双项完整／缺一 |
| --- | --- | --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench effective | SciCode | 20% | 10%／10% | 362／121 | 121／23 |
| Agent／工具工作 | AutomationBench-AA | τ³-Banking | 20% | 10%／10% | 110／145 | 110／34 |
| 高难推理 | CritPt | Humanity's Last Exam | 20% | 10%／10% | 357／437 | 144／0 |
| 知识／科学 | AA-Omniscience Accuracy | GPQA Diamond | 20% | 10%／10% | 354／445 | 144／0 |
| 指令／上下文 | AA-LCR v1.1 | GDP.pdf | 20% | 10%／10% | 354／109 | 108／36 |

- **编程：**Terminal-Bench effective：终端环境中的编程和工具任务；旧版按共同样本换算后折扣；SciCode：科学研究场景中的编程能力。
- **Agent／工具工作：**AutomationBench-AA：自动化工作流执行；τ³-Banking：银行场景中的交互和工具使用。
- **高难推理：**CritPt：研究级物理推理；Humanity's Last Exam：跨学科高难问题。
- **知识／科学：**AA-Omniscience Accuracy：知识问答的回答准确率；GPQA Diamond：研究生级科学知识与推理。
- **指令／上下文：**AA-LCR v1.1：长上下文推理；GDP.pdf：PDF 文档任务；使用 all-pass 成绩。

**取舍与适用性：**两项上下文均偏文档理解；GDP.pdf 覆盖较新，较旧模型可能单缺该项。

本方案每领域基础分均为表中两项调整后值各乘 0.5；任一缺测时固定损失该项的半份贡献，该领域加分归零。十项总缺数和领域全缺门槛仍按共用规则执行。

**覆盖与缺测：**144 个模型入榜，327 个剔除；剔除者中 327 个触发领域全缺，327 个累计缺至少四项，其中 327 个同时触发，不能直接相加。入榜者缺 0／1／2／3 项人数分别为 **105／7／10／22**。

入榜者 Terminal 来源：v4.0 实测 102 个；v2.1 换算×0.95 41 个；Hard 换算×0.90 1 个；缺测 0 个。旧版换算是估算证据，不能当成 v4 实测。

**扩展加分：**本方案动态上限为每领域 **28.827** 分，再受领域 100 分封顶约束。具体扩展项目和当前可拟合数量如下；所有项目仍受双 Core 完整条件限制。

| 领域 | 保留的扩展项目 | 启用拟合／保留项目数 |
| --- | --- | --- |
| 编程 | benchmark:swe-bench-pro、benchmark:livecodebench | 1／2 |
| Agent／工具工作 | τ²-Bench Telecom、APEX-Agents-AA、benchmark:swe-bench-pro、benchmark:hle-tools、benchmark:mcp-atlas、benchmark:osworld-verified | 4／6 |
| 高难推理 | AIME 2025 | 1／1 |
| 知识／科学 | MMMU-Pro、benchmark:mmlu-pro | 1／2 |
| 指令／上下文 | benchmark:charxiv-no-tools | 0／1 |

**实际算例：Claude Fable 5.1 (max with fallback)（本方案第 1 名）**

下表直接读取本方案的分项结果。“基础总分贡献”已经乘所在领域权重的一半（本轮均为 10%）；“领域最终总分贡献”已经计入扩展、领域封顶和 20% 权重。

| 领域 | Core 1 调整值 | Core 1 基础总分贡献 | Core 2 调整值 | Core 2 基础总分贡献 | 领域基础分 | 领域扩展加分 | 领域最终总分贡献 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench effective：52.020 | 5.202 | SciCode：63.079 | 6.308 | 57.549 | 2.370 | 11.984 |
| Agent／工具工作 | AutomationBench-AA：59.376 | 5.938 | τ³-Banking：47.217 | 4.722 | 53.296 | 8.873 | 12.434 |
| 高难推理 | CritPt：29.714 | 2.971 | Humanity's Last Exam：59.129 | 5.913 | 44.422 | 0.000 | 8.884 |
| 知识／科学 | AA-Omniscience Accuracy：67.233 | 6.723 | GPQA Diamond：93.737 | 9.374 | 80.485 | 0.000 | 16.097 |
| 指令／上下文 | AA-LCR v1.1：85.333 | 8.533 | GDP.pdf：26.200 | 2.620 | 55.767 | 0.000 | 11.153 |

十项基础贡献合计为 **58.304**；五项领域最终贡献合计为 **60.552**；封顶后的扩展净贡献为 **2.248**。该配置缺 0 项，Terminal 来源为 v4.0 实测。表内显示三位小数，逐格相加可能出现舍入尾差；精确复算使用 CSV 未舍入值。

**此前六条偏好审计：**

| 此前偏好 | 实际名次／比较对象 | 前者减后者分差 | 全量结果 | 共同集合结果 |
| --- | --- | --- | --- | --- |
| Fable 5.1 第一 | Claude Fable 5.1 (max with fallback) #1；GPT-6 Astra (max) #2 | 2.329 | 满足 | 满足 |
| GPT-6 Astra 第二 | GPT-6 Astra (max) #2；Claude Fable 5 (with fallback) #3 | 0.662 | 满足 | 满足 |
| Kimi K3 高于 Gemini 3.8 Flash | Kimi K3 (max) #9；Gemini 3.8 Flash (high) #8 | -0.099 | 未满足 | 未满足 |
| GPT-5.5 高于 Muse Spark 1.3 | GPT-5.5 (xhigh) #11；Muse Spark 1.3 (max) #6 | -3.413 | 未满足 | 未满足 |
| Qwen3.8 Max 高于 Qwen3.8 Flash-Next | Qwen3.8 Max #14；Qwen3.8-Flash-Next #23 | 2.693 | 满足 | 满足 |
| Qwen3.8 2.4T A95B 高于 Qwen3.8 Flash-Next | Qwen3.8 2.4T A95B #19；Qwen3.8-Flash-Next #23 | 1.000 | 满足 | 满足 |

**共同集合：**重新拟合后的前三名为 #1 Claude Fable 5.1 (max with fallback)（60.552）、#2 GPT-6 Astra (max)（58.223）、#3 Claude Fable 5 (with fallback)（57.561）。共同集合满足 4/6 条偏好，全量满足 4/6。共同集合与全量的六条偏好状态一致。

数据：[全量排名](rankings_dc01.csv) · [剔除与缺项](excluded_dc01.csv) · [共同集合排名](common_dc01.csv)。各项调整值、实际基础贡献、每领域基础分及加分都在全量 CSV 中。

<a id="dc02"></a>

## 02 Banking＋知识工作

**设计目的：**把 Agent 的 Automation 换成 Briefcase，比较银行操作与长流程知识工作交付。

相对首套方案，调整领域为：Agent／工具工作。其余计算规则相同。

| 领域 | Core 1 | Core 2 | 领域权重 | 两项在基础总分的权重 | 固定代表可用数1／2 | 入榜者双项完整／缺一 |
| --- | --- | --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench effective | SciCode | 20% | 10%／10% | 362／121 | 121／27 |
| Agent／工具工作 | τ³-Banking | AA-Briefcase | 20% | 10%／10% | 145／112 | 108／40 |
| 高难推理 | CritPt | Humanity's Last Exam | 20% | 10%／10% | 357／437 | 148／0 |
| 知识／科学 | AA-Omniscience Accuracy | GPQA Diamond | 20% | 10%／10% | 354／445 | 148／0 |
| 指令／上下文 | AA-LCR v1.1 | GDP.pdf | 20% | 10%／10% | 354／109 | 108／40 |

- **编程：**Terminal-Bench effective：终端环境中的编程和工具任务；旧版按共同样本换算后折扣；SciCode：科学研究场景中的编程能力。
- **Agent／工具工作：**τ³-Banking：银行场景中的交互和工具使用；AA-Briefcase：工作任务表现；使用 Elo 换算分。
- **高难推理：**CritPt：研究级物理推理；Humanity's Last Exam：跨学科高难问题。
- **知识／科学：**AA-Omniscience Accuracy：知识问答的回答准确率；GPQA Diamond：研究生级科学知识与推理。
- **指令／上下文：**AA-LCR v1.1：长上下文推理；GDP.pdf：PDF 文档任务；使用 all-pass 成绩。

**取舍与适用性：**Briefcase 为 Elo 换算分，非任务通过率；缺该项保留半份惩罚，例如 Flash-Next。

本方案每领域基础分均为表中两项调整后值各乘 0.5；任一缺测时固定损失该项的半份贡献，该领域加分归零。十项总缺数和领域全缺门槛仍按共用规则执行。

**覆盖与缺测：**148 个模型入榜，323 个剔除；剔除者中 323 个触发领域全缺，323 个累计缺至少四项，其中 323 个同时触发，不能直接相加。入榜者缺 0／1／2／3 项人数分别为 **102／10／11／25**。

入榜者 Terminal 来源：v4.0 实测 102 个；v2.1 换算×0.95 43 个；Hard 换算×0.90 3 个；缺测 0 个。旧版换算是估算证据，不能当成 v4 实测。

**扩展加分：**本方案动态上限为每领域 **27.213** 分，再受领域 100 分封顶约束。具体扩展项目和当前可拟合数量如下；所有项目仍受双 Core 完整条件限制。

| 领域 | 保留的扩展项目 | 启用拟合／保留项目数 |
| --- | --- | --- |
| 编程 | benchmark:swe-bench-pro、benchmark:livecodebench | 1／2 |
| Agent／工具工作 | τ²-Bench Telecom、APEX-Agents-AA、benchmark:swe-bench-pro、benchmark:hle-tools、benchmark:mcp-atlas、benchmark:osworld-verified | 4／6 |
| 高难推理 | AIME 2025 | 1／1 |
| 知识／科学 | MMMU-Pro、benchmark:mmlu-pro | 1／2 |
| 指令／上下文 | benchmark:charxiv-no-tools | 0／1 |

**实际算例：Claude Fable 5.1 (max with fallback)（本方案第 1 名）**

下表直接读取本方案的分项结果。“基础总分贡献”已经乘所在领域权重的一半（本轮均为 10%）；“领域最终总分贡献”已经计入扩展、领域封顶和 20% 权重。

| 领域 | Core 1 调整值 | Core 1 基础总分贡献 | Core 2 调整值 | Core 2 基础总分贡献 | 领域基础分 | 领域扩展加分 | 领域最终总分贡献 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench effective：52.020 | 5.202 | SciCode：63.079 | 6.308 | 57.549 | 2.370 | 11.984 |
| Agent／工具工作 | τ³-Banking：47.217 | 4.722 | AA-Briefcase：58.091 | 5.809 | 52.654 | 4.356 | 11.402 |
| 高难推理 | CritPt：29.714 | 2.971 | Humanity's Last Exam：59.129 | 5.913 | 44.422 | 0.000 | 8.884 |
| 知识／科学 | AA-Omniscience Accuracy：67.233 | 6.723 | GPQA Diamond：93.737 | 9.374 | 80.485 | 0.000 | 16.097 |
| 指令／上下文 | AA-LCR v1.1：85.333 | 8.533 | GDP.pdf：26.200 | 2.620 | 55.767 | 0.000 | 11.153 |

十项基础贡献合计为 **58.175**；五项领域最终贡献合计为 **59.520**；封顶后的扩展净贡献为 **1.345**。该配置缺 0 项，Terminal 来源为 v4.0 实测。表内显示三位小数，逐格相加可能出现舍入尾差；精确复算使用 CSV 未舍入值。

**此前六条偏好审计：**

| 此前偏好 | 实际名次／比较对象 | 前者减后者分差 | 全量结果 | 共同集合结果 |
| --- | --- | --- | --- | --- |
| Fable 5.1 第一 | Claude Fable 5.1 (max with fallback) #1；Claude Fable 5 (with fallback) #2 | 2.773 | 满足 | 满足 |
| GPT-6 Astra 第二 | GPT-6 Astra (max) #3；Claude Fable 5 (with fallback) #2 | -0.064 | 未满足 | 未满足 |
| Kimi K3 高于 Gemini 3.8 Flash | Kimi K3 (max) #8；Gemini 3.8 Flash (high) #10 | 1.542 | 满足 | 满足 |
| GPT-5.5 高于 Muse Spark 1.3 | GPT-5.5 (xhigh) #11；Muse Spark 1.3 (max) #6 | -4.314 | 未满足 | 未满足 |
| Qwen3.8 Max 高于 Qwen3.8 Flash-Next | Qwen3.8 Max #12；Qwen3.8-Flash-Next #34 | 7.806 | 满足 | 满足 |
| Qwen3.8 2.4T A95B 高于 Qwen3.8 Flash-Next | Qwen3.8 2.4T A95B #19；Qwen3.8-Flash-Next #34 | 5.535 | 满足 | 满足 |

**共同集合：**重新拟合后的前三名为 #1 Claude Fable 5.1 (max with fallback)（59.520）、#2 Claude Fable 5 (with fallback)（56.748）、#3 GPT-6 Astra (max)（56.684）。共同集合满足 4/6 条偏好，全量满足 4/6。共同集合与全量的六条偏好状态一致。

数据：[全量排名](rankings_dc02.csv) · [剔除与缺项](excluded_dc02.csv) · [共同集合排名](common_dc02.csv)。各项调整值、实际基础贡献、每领域基础分及加分都在全量 CSV 中。

<a id="dc03"></a>

## 03 自动化＋知识工作

**设计目的：**把 Agent 的 Banking 换成 Briefcase，强调 SaaS 自动化及工作成果交付。

相对首套方案，调整领域为：Agent／工具工作。其余计算规则相同。

| 领域 | Core 1 | Core 2 | 领域权重 | 两项在基础总分的权重 | 固定代表可用数1／2 | 入榜者双项完整／缺一 |
| --- | --- | --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench effective | SciCode | 20% | 10%／10% | 362／121 | 111／7 |
| Agent／工具工作 | AutomationBench-AA | AA-Briefcase | 20% | 10%／10% | 110／112 | 104／14 |
| 高难推理 | CritPt | Humanity's Last Exam | 20% | 10%／10% | 357／437 | 118／0 |
| 知识／科学 | AA-Omniscience Accuracy | GPQA Diamond | 20% | 10%／10% | 354／445 | 118／0 |
| 指令／上下文 | AA-LCR v1.1 | GDP.pdf | 20% | 10%／10% | 354／109 | 107／11 |

- **编程：**Terminal-Bench effective：终端环境中的编程和工具任务；旧版按共同样本换算后折扣；SciCode：科学研究场景中的编程能力。
- **Agent／工具工作：**AutomationBench-AA：自动化工作流执行；AA-Briefcase：工作任务表现；使用 Elo 换算分。
- **高难推理：**CritPt：研究级物理推理；Humanity's Last Exam：跨学科高难问题。
- **知识／科学：**AA-Omniscience Accuracy：知识问答的回答准确率；GPQA Diamond：研究生级科学知识与推理。
- **指令／上下文：**AA-LCR v1.1：长上下文推理；GDP.pdf：PDF 文档任务；使用 all-pass 成绩。

**取舍与适用性：**两项都是较新测试，老模型常同时缺失而被领域门槛剔除；Briefcase 是 Elo 换算分。

本方案每领域基础分均为表中两项调整后值各乘 0.5；任一缺测时固定损失该项的半份贡献，该领域加分归零。十项总缺数和领域全缺门槛仍按共用规则执行。

**覆盖与缺测：**118 个模型入榜，353 个剔除；剔除者中 353 个触发领域全缺，343 个累计缺至少四项，其中 343 个同时触发，不能直接相加。入榜者缺 0／1／2／3 项人数分别为 **100／11／0／7**。

入榜者 Terminal 来源：v4.0 实测 102 个；v2.1 换算×0.95 14 个；Hard 换算×0.90 2 个；缺测 0 个。旧版换算是估算证据，不能当成 v4 实测。

**扩展加分：**本方案动态上限为每领域 **23.201** 分，再受领域 100 分封顶约束。具体扩展项目和当前可拟合数量如下；所有项目仍受双 Core 完整条件限制。

| 领域 | 保留的扩展项目 | 启用拟合／保留项目数 |
| --- | --- | --- |
| 编程 | benchmark:swe-bench-pro、benchmark:livecodebench | 1／2 |
| Agent／工具工作 | τ²-Bench Telecom、τ³-Banking、APEX-Agents-AA、benchmark:swe-bench-pro、benchmark:hle-tools、benchmark:mcp-atlas、benchmark:osworld-verified | 5／7 |
| 高难推理 | AIME 2025 | 1／1 |
| 知识／科学 | MMMU-Pro、benchmark:mmlu-pro | 1／2 |
| 指令／上下文 | benchmark:charxiv-no-tools | 0／1 |

**实际算例：Claude Fable 5.1 (max with fallback)（本方案第 1 名）**

下表直接读取本方案的分项结果。“基础总分贡献”已经乘所在领域权重的一半（本轮均为 10%）；“领域最终总分贡献”已经计入扩展、领域封顶和 20% 权重。

| 领域 | Core 1 调整值 | Core 1 基础总分贡献 | Core 2 调整值 | Core 2 基础总分贡献 | 领域基础分 | 领域扩展加分 | 领域最终总分贡献 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench effective：52.020 | 5.202 | SciCode：63.079 | 6.308 | 57.549 | 2.370 | 11.984 |
| Agent／工具工作 | AutomationBench-AA：59.376 | 5.938 | AA-Briefcase：58.091 | 5.809 | 58.733 | 6.093 | 12.965 |
| 高难推理 | CritPt：29.714 | 2.971 | Humanity's Last Exam：59.129 | 5.913 | 44.422 | 0.000 | 8.884 |
| 知识／科学 | AA-Omniscience Accuracy：67.233 | 6.723 | GPQA Diamond：93.737 | 9.374 | 80.485 | 0.000 | 16.097 |
| 指令／上下文 | AA-LCR v1.1：85.333 | 8.533 | GDP.pdf：26.200 | 2.620 | 55.767 | 0.000 | 11.153 |

十项基础贡献合计为 **59.391**；五项领域最终贡献合计为 **61.084**；封顶后的扩展净贡献为 **1.693**。该配置缺 0 项，Terminal 来源为 v4.0 实测。表内显示三位小数，逐格相加可能出现舍入尾差；精确复算使用 CSV 未舍入值。

**此前六条偏好审计：**

| 此前偏好 | 实际名次／比较对象 | 前者减后者分差 | 全量结果 | 共同集合结果 |
| --- | --- | --- | --- | --- |
| Fable 5.1 第一 | Claude Fable 5.1 (max with fallback) #1；GPT-6 Astra (max) #2 | 1.695 | 满足 | 满足 |
| GPT-6 Astra 第二 | GPT-6 Astra (max) #2；Claude Fable 5 (with fallback) #3 | 1.037 | 满足 | 满足 |
| Kimi K3 高于 Gemini 3.8 Flash | Kimi K3 (max) #8；Gemini 3.8 Flash (high) #10 | 0.623 | 满足 | 满足 |
| GPT-5.5 高于 Muse Spark 1.3 | GPT-5.5 (xhigh) #12；Muse Spark 1.3 (max) #6 | -4.648 | 未满足 | 未满足 |
| Qwen3.8 Max 高于 Qwen3.8 Flash-Next | Qwen3.8 Max #11；Qwen3.8-Flash-Next #33 | 9.044 | 满足 | 满足 |
| Qwen3.8 2.4T A95B 高于 Qwen3.8 Flash-Next | Qwen3.8 2.4T A95B #18；Qwen3.8-Flash-Next #33 | 6.635 | 满足 | 满足 |

**共同集合：**重新拟合后的前三名为 #1 Claude Fable 5.1 (max with fallback)（61.084）、#2 GPT-6 Astra (max)（59.389）、#3 Claude Fable 5 (with fallback)（58.351）。共同集合满足 5/6 条偏好，全量满足 5/6。共同集合与全量的六条偏好状态一致。

数据：[全量排名](rankings_dc03.csv) · [剔除与缺项](excluded_dc03.csv) · [共同集合排名](common_dc03.csv)。各项调整值、实际基础贡献、每领域基础分及加分都在全量 CSV 中。

<a id="dc04"></a>

## 04 自动化＋职业任务

**设计目的：**把 Banking 换成 GDPval v2，观察职业任务能力对 Agent 板块的影响。

相对首套方案，调整领域为：Agent／工具工作。其余计算规则相同。

| 领域 | Core 1 | Core 2 | 领域权重 | 两项在基础总分的权重 | 固定代表可用数1／2 | 入榜者双项完整／缺一 |
| --- | --- | --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench effective | SciCode | 20% | 10%／10% | 362／121 | 121／47 |
| Agent／工具工作 | AutomationBench-AA | GDPval-AA v2 | 20% | 10%／10% | 110／170 | 110／58 |
| 高难推理 | CritPt | Humanity's Last Exam | 20% | 10%／10% | 357／437 | 168／0 |
| 知识／科学 | AA-Omniscience Accuracy | GPQA Diamond | 20% | 10%／10% | 354／445 | 168／0 |
| 指令／上下文 | AA-LCR v1.1 | GDP.pdf | 20% | 10%／10% | 354／109 | 108／60 |

- **编程：**Terminal-Bench effective：终端环境中的编程和工具任务；旧版按共同样本换算后折扣；SciCode：科学研究场景中的编程能力。
- **Agent／工具工作：**AutomationBench-AA：自动化工作流执行；GDPval-AA v2：专业知识工作交付；使用 Elo 换算分。
- **高难推理：**CritPt：研究级物理推理；Humanity's Last Exam：跨学科高难问题。
- **知识／科学：**AA-Omniscience Accuracy：知识问答的回答准确率；GPQA Diamond：研究生级科学知识与推理。
- **指令／上下文：**AA-LCR v1.1：长上下文推理；GDP.pdf：PDF 文档任务；使用 all-pass 成绩。

**取舍与适用性：**GDPval v2 是 Elo 换算分，任务由 OpenAI 控制；这是本轮显式实验，不代表采用原独立基准准入政策。

本方案每领域基础分均为表中两项调整后值各乘 0.5；任一缺测时固定损失该项的半份贡献，该领域加分归零。十项总缺数和领域全缺门槛仍按共用规则执行。

**覆盖与缺测：**168 个模型入榜，303 个剔除；剔除者中 303 个触发领域全缺，303 个累计缺至少四项，其中 303 个同时触发，不能直接相加。入榜者缺 0／1／2／3 项人数分别为 **105／7／10／46**。

入榜者 Terminal 来源：v4.0 实测 102 个；v2.1 换算×0.95 65 个；Hard 换算×0.90 1 个；缺测 0 个。旧版换算是估算证据，不能当成 v4 实测。

**扩展加分：**本方案动态上限为每领域 **22.469** 分，再受领域 100 分封顶约束。具体扩展项目和当前可拟合数量如下；所有项目仍受双 Core 完整条件限制。

| 领域 | 保留的扩展项目 | 启用拟合／保留项目数 |
| --- | --- | --- |
| 编程 | benchmark:swe-bench-pro、benchmark:livecodebench | 1／2 |
| Agent／工具工作 | τ²-Bench Telecom、τ³-Banking、APEX-Agents-AA、benchmark:swe-bench-pro、benchmark:hle-tools、benchmark:mcp-atlas、benchmark:osworld-verified | 5／7 |
| 高难推理 | AIME 2025 | 1／1 |
| 知识／科学 | MMMU-Pro、benchmark:mmlu-pro | 2／2 |
| 指令／上下文 | benchmark:charxiv-no-tools | 0／1 |

**实际算例：Claude Fable 5.1 (max with fallback)（本方案第 1 名）**

下表直接读取本方案的分项结果。“基础总分贡献”已经乘所在领域权重的一半（本轮均为 10%）；“领域最终总分贡献”已经计入扩展、领域封顶和 20% 权重。

| 领域 | Core 1 调整值 | Core 1 基础总分贡献 | Core 2 调整值 | Core 2 基础总分贡献 | 领域基础分 | 领域扩展加分 | 领域最终总分贡献 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench effective：52.020 | 5.202 | SciCode：63.079 | 6.308 | 57.549 | 2.370 | 11.984 |
| Agent／工具工作 | AutomationBench-AA：59.376 | 5.938 | GDPval-AA v2：63.182 | 6.318 | 61.279 | 8.374 | 13.931 |
| 高难推理 | CritPt：29.714 | 2.971 | Humanity's Last Exam：59.129 | 5.913 | 44.422 | 0.000 | 8.884 |
| 知识／科学 | AA-Omniscience Accuracy：67.233 | 6.723 | GPQA Diamond：93.737 | 9.374 | 80.485 | 0.000 | 16.097 |
| 指令／上下文 | AA-LCR v1.1：85.333 | 8.533 | GDP.pdf：26.200 | 2.620 | 55.767 | 0.000 | 11.153 |

十项基础贡献合计为 **59.900**；五项领域最终贡献合计为 **62.049**；封顶后的扩展净贡献为 **2.149**。该配置缺 0 项，Terminal 来源为 v4.0 实测。表内显示三位小数，逐格相加可能出现舍入尾差；精确复算使用 CSV 未舍入值。

**此前六条偏好审计：**

| 此前偏好 | 实际名次／比较对象 | 前者减后者分差 | 全量结果 | 共同集合结果 |
| --- | --- | --- | --- | --- |
| Fable 5.1 第一 | Claude Fable 5.1 (max with fallback) #1；GPT-6 Astra (max) #2 | 2.570 | 满足 | 满足 |
| GPT-6 Astra 第二 | GPT-6 Astra (max) #2；Claude Fable 5 (with fallback) #3 | 0.281 | 满足 | 满足 |
| Kimi K3 高于 Gemini 3.8 Flash | Kimi K3 (max) #8；Gemini 3.8 Flash (high) #9 | 0.318 | 满足 | 满足 |
| GPT-5.5 高于 Muse Spark 1.3 | GPT-5.5 (xhigh) #11；Muse Spark 1.3 (max) #6 | -4.382 | 未满足 | 未满足 |
| Qwen3.8 Max 高于 Qwen3.8 Flash-Next | Qwen3.8 Max #12；Qwen3.8-Flash-Next #22 | 3.734 | 满足 | 满足 |
| Qwen3.8 2.4T A95B 高于 Qwen3.8 Flash-Next | Qwen3.8 2.4T A95B #18；Qwen3.8-Flash-Next #22 | 1.298 | 满足 | 满足 |

**共同集合：**重新拟合后的前三名为 #1 Claude Fable 5.1 (max with fallback)（62.049）、#2 GPT-6 Astra (max)（59.480）、#3 Claude Fable 5 (with fallback)（59.198）。共同集合满足 5/6 条偏好，全量满足 5/6。共同集合与全量的六条偏好状态一致。

数据：[全量排名](rankings_dc04.csv) · [剔除与缺项](excluded_dc04.csv) · [共同集合排名](common_dc04.csv)。各项调整值、实际基础贡献、每领域基础分及加分都在全量 CSV 中。

<a id="dc05"></a>

## 05 指令遵循对照

**设计目的：**上下文用 LCR＋IFBench，将 PDF 问答替换为指令遵循测试。

相对首套方案，调整领域为：指令／上下文。其余计算规则相同。

| 领域 | Core 1 | Core 2 | 领域权重 | 两项在基础总分的权重 | 固定代表可用数1／2 | 入榜者双项完整／缺一 |
| --- | --- | --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench effective | SciCode | 20% | 10%／10% | 362／121 | 121／23 |
| Agent／工具工作 | AutomationBench-AA | τ³-Banking | 20% | 10%／10% | 110／145 | 110／34 |
| 高难推理 | CritPt | Humanity's Last Exam | 20% | 10%／10% | 357／437 | 144／0 |
| 知识／科学 | AA-Omniscience Accuracy | GPQA Diamond | 20% | 10%／10% | 354／445 | 144／0 |
| 指令／上下文 | AA-LCR v1.1 | IFBench | 20% | 10%／10% | 354／321 | 92／52 |

- **编程：**Terminal-Bench effective：终端环境中的编程和工具任务；旧版按共同样本换算后折扣；SciCode：科学研究场景中的编程能力。
- **Agent／工具工作：**AutomationBench-AA：自动化工作流执行；τ³-Banking：银行场景中的交互和工具使用。
- **高难推理：**CritPt：研究级物理推理；Humanity's Last Exam：跨学科高难问题。
- **知识／科学：**AA-Omniscience Accuracy：知识问答的回答准确率；GPQA Diamond：研究生级科学知识与推理。
- **指令／上下文：**AA-LCR v1.1：长上下文推理；IFBench：复杂指令遵循。

**取舍与适用性：**不少最新模型缺 IFBench，其指令／上下文基础分最多只获得 LCR 的半份。

本方案每领域基础分均为表中两项调整后值各乘 0.5；任一缺测时固定损失该项的半份贡献，该领域加分归零。十项总缺数和领域全缺门槛仍按共用规则执行。

**覆盖与缺测：**144 个模型入榜，327 个剔除；剔除者中 326 个触发领域全缺，137 个累计缺至少四项，其中 136 个同时触发，不能直接相加。入榜者缺 0／1／2／3 项人数分别为 **69／42／32／1**。

入榜者 Terminal 来源：v4.0 实测 102 个；v2.1 换算×0.95 41 个；Hard 换算×0.90 1 个；缺测 0 个。旧版换算是估算证据，不能当成 v4 实测。

**扩展加分：**本方案动态上限为每领域 **28.827** 分，再受领域 100 分封顶约束。具体扩展项目和当前可拟合数量如下；所有项目仍受双 Core 完整条件限制。

| 领域 | 保留的扩展项目 | 启用拟合／保留项目数 |
| --- | --- | --- |
| 编程 | benchmark:swe-bench-pro、benchmark:livecodebench | 1／2 |
| Agent／工具工作 | τ²-Bench Telecom、APEX-Agents-AA、benchmark:swe-bench-pro、benchmark:hle-tools、benchmark:mcp-atlas、benchmark:osworld-verified | 4／6 |
| 高难推理 | AIME 2025 | 1／1 |
| 知识／科学 | MMMU-Pro、benchmark:mmlu-pro | 1／2 |
| 指令／上下文 | benchmark:charxiv-no-tools | 0／1 |

**实际算例：Claude Fable 5.1 (max with fallback)（本方案第 3 名）**

下表直接读取本方案的分项结果。“基础总分贡献”已经乘所在领域权重的一半（本轮均为 10%）；“领域最终总分贡献”已经计入扩展、领域封顶和 20% 权重。

| 领域 | Core 1 调整值 | Core 1 基础总分贡献 | Core 2 调整值 | Core 2 基础总分贡献 | 领域基础分 | 领域扩展加分 | 领域最终总分贡献 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench effective：52.020 | 5.202 | SciCode：63.079 | 6.308 | 57.549 | 2.370 | 11.984 |
| Agent／工具工作 | AutomationBench-AA：59.376 | 5.938 | τ³-Banking：47.217 | 4.722 | 53.296 | 8.873 | 12.434 |
| 高难推理 | CritPt：29.714 | 2.971 | Humanity's Last Exam：59.129 | 5.913 | 44.422 | 0.000 | 8.884 |
| 知识／科学 | AA-Omniscience Accuracy：67.233 | 6.723 | GPQA Diamond：93.737 | 9.374 | 80.485 | 0.000 | 16.097 |
| 指令／上下文 | AA-LCR v1.1：85.333 | 8.533 | IFBench：缺测 | 0.000 | 42.667 | 0.000 | 8.533 |

十项基础贡献合计为 **55.684**；五项领域最终贡献合计为 **57.932**；封顶后的扩展净贡献为 **2.248**。该配置缺 1 项，Terminal 来源为 v4.0 实测。表内显示三位小数，逐格相加可能出现舍入尾差；精确复算使用 CSV 未舍入值。

**此前六条偏好审计：**

| 此前偏好 | 实际名次／比较对象 | 前者减后者分差 | 全量结果 | 共同集合结果 |
| --- | --- | --- | --- | --- |
| Fable 5.1 第一 | Claude Fable 5.1 (max with fallback) #3；Claude Fable 5 (with fallback) #1 | -3.576 | 未满足 | 未满足 |
| GPT-6 Astra 第二 | GPT-6 Astra (max) #5；Claude Fable 5 (with fallback) #1 | -6.385 | 未满足 | 未满足 |
| Kimi K3 高于 Gemini 3.8 Flash | Kimi K3 (max) #16；Gemini 3.8 Flash (high) #15 | -0.199 | 未满足 | 未满足 |
| GPT-5.5 高于 Muse Spark 1.3 | GPT-5.5 (xhigh) #7；Muse Spark 1.3 (max) #11 | 4.712 | 满足 | 满足 |
| Qwen3.8 Max 高于 Qwen3.8 Flash-Next | Qwen3.8 Max #23；Qwen3.8-Flash-Next #34 | 2.233 | 满足 | 满足 |
| Qwen3.8 2.4T A95B 高于 Qwen3.8 Flash-Next | Qwen3.8 2.4T A95B #31；Qwen3.8-Flash-Next #34 | 1.000 | 满足 | 满足 |

**共同集合：**重新拟合后的前三名为 #1 Claude Fable 5 (with fallback)（61.508）、#2 GPT-5.6 Sol (max)（59.334）、#3 Claude Fable 5.1 (max with fallback)（57.932）。共同集合满足 3/6 条偏好，全量满足 3/6。共同集合与全量的六条偏好状态一致。

数据：[全量排名](rankings_dc05.csv) · [剔除与缺项](excluded_dc05.csv) · [共同集合排名](common_dc05.csv)。各项调整值、实际基础贡献、每领域基础分及加分都在全量 CSV 中。

<a id="dc06"></a>

## 06 算法编程对照

**设计目的：**用 LiveCodeBench 替代 SciCode，比较算法代码能力与终端任务能力。

相对首套方案，调整领域为：编程。其余计算规则相同。

| 领域 | Core 1 | Core 2 | 领域权重 | 两项在基础总分的权重 | 固定代表可用数1／2 | 入榜者双项完整／缺一 |
| --- | --- | --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench effective | LiveCodeBench | 20% | 10%／10% | 362／269 | 42／102 |
| Agent／工具工作 | AutomationBench-AA | τ³-Banking | 20% | 10%／10% | 110／145 | 110／34 |
| 高难推理 | CritPt | Humanity's Last Exam | 20% | 10%／10% | 357／437 | 144／0 |
| 知识／科学 | AA-Omniscience Accuracy | GPQA Diamond | 20% | 10%／10% | 354／445 | 144／0 |
| 指令／上下文 | AA-LCR v1.1 | GDP.pdf | 20% | 10%／10% | 354／109 | 108／36 |

- **编程：**Terminal-Bench effective：终端环境中的编程和工具任务；旧版按共同样本换算后折扣；LiveCodeBench：竞赛型代码问题；只用原始直接成绩。
- **Agent／工具工作：**AutomationBench-AA：自动化工作流执行；τ³-Banking：银行场景中的交互和工具使用。
- **高难推理：**CritPt：研究级物理推理；Humanity's Last Exam：跨学科高难问题。
- **知识／科学：**AA-Omniscience Accuracy：知识问答的回答准确率；GPQA Diamond：研究生级科学知识与推理。
- **指令／上下文：**AA-LCR v1.1：长上下文推理；GDP.pdf：PDF 文档任务；使用 all-pass 成绩。

**取舍与适用性：**当前新旗舰多缺 LiveCodeBench，编程基础分因此只获得 Terminal 的半份；不会用网站拟合补值。

本方案每领域基础分均为表中两项调整后值各乘 0.5；任一缺测时固定损失该项的半份贡献，该领域加分归零。十项总缺数和领域全缺门槛仍按共用规则执行。

**覆盖与缺测：**144 个模型入榜，327 个剔除；剔除者中 327 个触发领域全缺，199 个累计缺至少四项，其中 199 个同时触发，不能直接相加。入榜者缺 0／1／2／3 项人数分别为 **29／78／17／20**。

入榜者 Terminal 来源：v4.0 实测 102 个；v2.1 换算×0.95 41 个；Hard 换算×0.90 1 个；缺测 0 个。旧版换算是估算证据，不能当成 v4 实测。

**扩展加分：**本方案动态上限为每领域 **29.516** 分，再受领域 100 分封顶约束。具体扩展项目和当前可拟合数量如下；所有项目仍受双 Core 完整条件限制。

| 领域 | 保留的扩展项目 | 启用拟合／保留项目数 |
| --- | --- | --- |
| 编程 | benchmark:swe-bench-pro | 0／1 |
| Agent／工具工作 | τ²-Bench Telecom、APEX-Agents-AA、benchmark:swe-bench-pro、benchmark:hle-tools、benchmark:mcp-atlas、benchmark:osworld-verified | 4／6 |
| 高难推理 | AIME 2025 | 1／1 |
| 知识／科学 | MMMU-Pro、benchmark:mmlu-pro | 1／2 |
| 指令／上下文 | benchmark:charxiv-no-tools | 0／1 |

**实际算例：Claude Fable 5.1 (max with fallback)（本方案第 1 名）**

下表直接读取本方案的分项结果。“基础总分贡献”已经乘所在领域权重的一半（本轮均为 10%）；“领域最终总分贡献”已经计入扩展、领域封顶和 20% 权重。

| 领域 | Core 1 调整值 | Core 1 基础总分贡献 | Core 2 调整值 | Core 2 基础总分贡献 | 领域基础分 | 领域扩展加分 | 领域最终总分贡献 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench effective：52.020 | 5.202 | LiveCodeBench：缺测 | 0.000 | 26.010 | 0.000 | 5.202 |
| Agent／工具工作 | AutomationBench-AA：59.376 | 5.938 | τ³-Banking：47.217 | 4.722 | 53.296 | 8.873 | 12.434 |
| 高难推理 | CritPt：29.714 | 2.971 | Humanity's Last Exam：59.129 | 5.913 | 44.422 | 0.000 | 8.884 |
| 知识／科学 | AA-Omniscience Accuracy：67.233 | 6.723 | GPQA Diamond：93.737 | 9.374 | 80.485 | 0.000 | 16.097 |
| 指令／上下文 | AA-LCR v1.1：85.333 | 8.533 | GDP.pdf：26.200 | 2.620 | 55.767 | 0.000 | 11.153 |

十项基础贡献合计为 **51.996**；五项领域最终贡献合计为 **53.771**；封顶后的扩展净贡献为 **1.775**。该配置缺 1 项，Terminal 来源为 v4.0 实测。表内显示三位小数，逐格相加可能出现舍入尾差；精确复算使用 CSV 未舍入值。

**此前六条偏好审计：**

| 此前偏好 | 实际名次／比较对象 | 前者减后者分差 | 全量结果 | 共同集合结果 |
| --- | --- | --- | --- | --- |
| Fable 5.1 第一 | Claude Fable 5.1 (max with fallback) #1；GPT-6 Astra (max) #2 | 1.196 | 满足 | 满足 |
| GPT-6 Astra 第二 | GPT-6 Astra (max) #2；Claude Fable 5 (with fallback) #3 | 2.151 | 满足 | 满足 |
| Kimi K3 高于 Gemini 3.8 Flash | Kimi K3 (max) #9；Gemini 3.8 Flash (high) #8 | -0.388 | 未满足 | 未满足 |
| GPT-5.5 高于 Muse Spark 1.3 | GPT-5.5 (xhigh) #11；Muse Spark 1.3 (max) #6 | -3.112 | 未满足 | 未满足 |
| Qwen3.8 Max 高于 Qwen3.8 Flash-Next | Qwen3.8 Max #14；Qwen3.8-Flash-Next #23 | 2.497 | 满足 | 满足 |
| Qwen3.8 2.4T A95B 高于 Qwen3.8 Flash-Next | Qwen3.8 2.4T A95B #19；Qwen3.8-Flash-Next #23 | 0.723 | 满足 | 满足 |

**共同集合：**重新拟合后的前三名为 #1 Claude Fable 5.1 (max with fallback)（53.771）、#2 GPT-6 Astra (max)（52.575）、#3 Claude Fable 5 (with fallback)（50.423）。共同集合满足 4/6 条偏好，全量满足 4/6。共同集合与全量的六条偏好状态一致。

数据：[全量排名](rankings_dc06.csv) · [剔除与缺项](excluded_dc06.csv) · [共同集合排名](common_dc06.csv)。各项调整值、实际基础贡献、每领域基础分及加分都在全量 CSV 中。

<a id="dc07"></a>

## 07 算法＋指令双替换

**设计目的：**同时采用 LiveCodeBench 和 IFBench，检验两项历史高覆盖测试共同进入 Core 的影响。

相对首套方案，调整领域为：编程、指令／上下文。其余计算规则相同。

| 领域 | Core 1 | Core 2 | 领域权重 | 两项在基础总分的权重 | 固定代表可用数1／2 | 入榜者双项完整／缺一 |
| --- | --- | --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench effective | LiveCodeBench | 20% | 10%／10% | 362／269 | 42／102 |
| Agent／工具工作 | AutomationBench-AA | τ³-Banking | 20% | 10%／10% | 110／145 | 110／34 |
| 高难推理 | CritPt | Humanity's Last Exam | 20% | 10%／10% | 357／437 | 144／0 |
| 知识／科学 | AA-Omniscience Accuracy | GPQA Diamond | 20% | 10%／10% | 354／445 | 144／0 |
| 指令／上下文 | AA-LCR v1.1 | IFBench | 20% | 10%／10% | 354／321 | 92／52 |

- **编程：**Terminal-Bench effective：终端环境中的编程和工具任务；旧版按共同样本换算后折扣；LiveCodeBench：竞赛型代码问题；只用原始直接成绩。
- **Agent／工具工作：**AutomationBench-AA：自动化工作流执行；τ³-Banking：银行场景中的交互和工具使用。
- **高难推理：**CritPt：研究级物理推理；Humanity's Last Exam：跨学科高难问题。
- **知识／科学：**AA-Omniscience Accuracy：知识问答的回答准确率；GPQA Diamond：研究生级科学知识与推理。
- **指令／上下文：**AA-LCR v1.1：长上下文推理；IFBench：复杂指令遵循。

**取舍与适用性：**不少新模型会累计缺两项，仍可入榜但两个领域各损失半份；这是缺测规则的压力对照。

本方案每领域基础分均为表中两项调整后值各乘 0.5；任一缺测时固定损失该项的半份贡献，该领域加分归零。十项总缺数和领域全缺门槛仍按共用规则执行。

**覆盖与缺测：**144 个模型入榜，327 个剔除；剔除者中 326 个触发领域全缺，120 个累计缺至少四项，其中 119 个同时触发，不能直接相加。入榜者缺 0／1／2／3 项人数分别为 **30／52／50／12**。

入榜者 Terminal 来源：v4.0 实测 102 个；v2.1 换算×0.95 41 个；Hard 换算×0.90 1 个；缺测 0 个。旧版换算是估算证据，不能当成 v4 实测。

**扩展加分：**本方案动态上限为每领域 **29.516** 分，再受领域 100 分封顶约束。具体扩展项目和当前可拟合数量如下；所有项目仍受双 Core 完整条件限制。

| 领域 | 保留的扩展项目 | 启用拟合／保留项目数 |
| --- | --- | --- |
| 编程 | benchmark:swe-bench-pro | 0／1 |
| Agent／工具工作 | τ²-Bench Telecom、APEX-Agents-AA、benchmark:swe-bench-pro、benchmark:hle-tools、benchmark:mcp-atlas、benchmark:osworld-verified | 4／6 |
| 高难推理 | AIME 2025 | 1／1 |
| 知识／科学 | MMMU-Pro、benchmark:mmlu-pro | 1／2 |
| 指令／上下文 | benchmark:charxiv-no-tools | 0／1 |

**实际算例：Claude Fable 5.1 (max with fallback)（本方案第 3 名）**

下表直接读取本方案的分项结果。“基础总分贡献”已经乘所在领域权重的一半（本轮均为 10%）；“领域最终总分贡献”已经计入扩展、领域封顶和 20% 权重。

| 领域 | Core 1 调整值 | Core 1 基础总分贡献 | Core 2 调整值 | Core 2 基础总分贡献 | 领域基础分 | 领域扩展加分 | 领域最终总分贡献 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench effective：52.020 | 5.202 | LiveCodeBench：缺测 | 0.000 | 26.010 | 0.000 | 5.202 |
| Agent／工具工作 | AutomationBench-AA：59.376 | 5.938 | τ³-Banking：47.217 | 4.722 | 53.296 | 8.873 | 12.434 |
| 高难推理 | CritPt：29.714 | 2.971 | Humanity's Last Exam：59.129 | 5.913 | 44.422 | 0.000 | 8.884 |
| 知识／科学 | AA-Omniscience Accuracy：67.233 | 6.723 | GPQA Diamond：93.737 | 9.374 | 80.485 | 0.000 | 16.097 |
| 指令／上下文 | AA-LCR v1.1：85.333 | 8.533 | IFBench：缺测 | 0.000 | 42.667 | 0.000 | 8.533 |

十项基础贡献合计为 **49.376**；五项领域最终贡献合计为 **51.151**；封顶后的扩展净贡献为 **1.775**。该配置缺 2 项，Terminal 来源为 v4.0 实测。表内显示三位小数，逐格相加可能出现舍入尾差；精确复算使用 CSV 未舍入值。

**此前六条偏好审计：**

| 此前偏好 | 实际名次／比较对象 | 前者减后者分差 | 全量结果 | 共同集合结果 |
| --- | --- | --- | --- | --- |
| Fable 5.1 第一 | Claude Fable 5.1 (max with fallback) #3；Claude Fable 5 (with fallback) #1 | -3.220 | 未满足 | 未满足 |
| GPT-6 Astra 第二 | GPT-6 Astra (max) #5；Claude Fable 5 (with fallback) #1 | -4.895 | 未满足 | 未满足 |
| Kimi K3 高于 Gemini 3.8 Flash | Kimi K3 (max) #23；Gemini 3.8 Flash (high) #18 | -0.488 | 未满足 | 未满足 |
| GPT-5.5 高于 Muse Spark 1.3 | GPT-5.5 (xhigh) #6；Muse Spark 1.3 (max) #12 | 5.013 | 满足 | 满足 |
| Qwen3.8 Max 高于 Qwen3.8 Flash-Next | Qwen3.8 Max #31；Qwen3.8-Flash-Next #47 | 2.037 | 满足 | 满足 |
| Qwen3.8 2.4T A95B 高于 Qwen3.8 Flash-Next | Qwen3.8 2.4T A95B #42；Qwen3.8-Flash-Next #47 | 0.723 | 满足 | 满足 |

**共同集合：**重新拟合后的前三名为 #1 Claude Fable 5 (with fallback)（54.370）、#2 GPT-5.6 Sol (max)（53.628）、#3 Claude Fable 5.1 (max with fallback)（51.151）。共同集合满足 3/6 条偏好，全量满足 3/6。共同集合与全量的六条偏好状态一致。

数据：[全量排名](rankings_dc07.csv) · [剔除与缺项](excluded_dc07.csv) · [共同集合排名](common_dc07.csv)。各项调整值、实际基础贡献、每领域基础分及加分都在全量 CSV 中。

<a id="dc08"></a>

## 08 数学竞赛对照

**设计目的：**推理用 CritPt＋AIME 2025，将广域 HLE 替换为数学竞赛。

相对首套方案，调整领域为：高难推理。其余计算规则相同。

| 领域 | Core 1 | Core 2 | 领域权重 | 两项在基础总分的权重 | 固定代表可用数1／2 | 入榜者双项完整／缺一 |
| --- | --- | --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench effective | SciCode | 20% | 10%／10% | 362／121 | 121／12 |
| Agent／工具工作 | AutomationBench-AA | τ³-Banking | 20% | 10%／10% | 110／145 | 110／23 |
| 高难推理 | CritPt | AIME 2025 | 20% | 10%／10% | 357／199 | 41／92 |
| 知识／科学 | AA-Omniscience Accuracy | GPQA Diamond | 20% | 10%／10% | 354／445 | 133／0 |
| 指令／上下文 | AA-LCR v1.1 | GDP.pdf | 20% | 10%／10% | 354／109 | 108／25 |

- **编程：**Terminal-Bench effective：终端环境中的编程和工具任务；旧版按共同样本换算后折扣；SciCode：科学研究场景中的编程能力。
- **Agent／工具工作：**AutomationBench-AA：自动化工作流执行；τ³-Banking：银行场景中的交互和工具使用。
- **高难推理：**CritPt：研究级物理推理；AIME 2025：竞赛数学推理。
- **知识／科学：**AA-Omniscience Accuracy：知识问答的回答准确率；GPQA Diamond：研究生级科学知识与推理。
- **指令／上下文：**AA-LCR v1.1：长上下文推理；GDP.pdf：PDF 文档任务；使用 all-pass 成绩。

**取舍与适用性：**AIME 2025 的旧模型覆盖较多，新模型缺测较多；推理板块单缺时只计 CritPt 的半份。

本方案每领域基础分均为表中两项调整后值各乘 0.5；任一缺测时固定损失该项的半份贡献，该领域加分归零。十项总缺数和领域全缺门槛仍按共用规则执行。

**覆盖与缺测：**133 个模型入榜，338 个剔除；剔除者中 327 个触发领域全缺，338 个累计缺至少四项，其中 327 个同时触发，不能直接相加。入榜者缺 0／1／2／3 项人数分别为 **28／78／7／20**。

入榜者 Terminal 来源：v4.0 实测 102 个；v2.1 换算×0.95 30 个；Hard 换算×0.90 1 个；缺测 0 个。旧版换算是估算证据，不能当成 v4 实测。

**扩展加分：**本方案动态上限为每领域 **27.472** 分，再受领域 100 分封顶约束。具体扩展项目和当前可拟合数量如下；所有项目仍受双 Core 完整条件限制。

| 领域 | 保留的扩展项目 | 启用拟合／保留项目数 |
| --- | --- | --- |
| 编程 | benchmark:swe-bench-pro、benchmark:livecodebench | 1／2 |
| Agent／工具工作 | τ²-Bench Telecom、APEX-Agents-AA、benchmark:swe-bench-pro、benchmark:hle-tools、benchmark:mcp-atlas、benchmark:osworld-verified | 4／6 |
| 高难推理 | 无 | 0／0 |
| 知识／科学 | MMMU-Pro、benchmark:mmlu-pro | 1／2 |
| 指令／上下文 | benchmark:charxiv-no-tools | 0／1 |

**实际算例：Claude Fable 5.1 (max with fallback)（本方案第 1 名）**

下表直接读取本方案的分项结果。“基础总分贡献”已经乘所在领域权重的一半（本轮均为 10%）；“领域最终总分贡献”已经计入扩展、领域封顶和 20% 权重。

| 领域 | Core 1 调整值 | Core 1 基础总分贡献 | Core 2 调整值 | Core 2 基础总分贡献 | 领域基础分 | 领域扩展加分 | 领域最终总分贡献 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench effective：52.020 | 5.202 | SciCode：63.079 | 6.308 | 57.549 | 2.370 | 11.984 |
| Agent／工具工作 | AutomationBench-AA：59.376 | 5.938 | τ³-Banking：47.217 | 4.722 | 53.296 | 8.873 | 12.434 |
| 高难推理 | CritPt：29.714 | 2.971 | AIME 2025：缺测 | 0.000 | 14.857 | 0.000 | 2.971 |
| 知识／科学 | AA-Omniscience Accuracy：67.233 | 6.723 | GPQA Diamond：93.737 | 9.374 | 80.485 | 0.000 | 16.097 |
| 指令／上下文 | AA-LCR v1.1：85.333 | 8.533 | GDP.pdf：26.200 | 2.620 | 55.767 | 0.000 | 11.153 |

十项基础贡献合计为 **52.391**；五项领域最终贡献合计为 **54.639**；封顶后的扩展净贡献为 **2.248**。该配置缺 1 项，Terminal 来源为 v4.0 实测。表内显示三位小数，逐格相加可能出现舍入尾差；精确复算使用 CSV 未舍入值。

**此前六条偏好审计：**

| 此前偏好 | 实际名次／比较对象 | 前者减后者分差 | 全量结果 | 共同集合结果 |
| --- | --- | --- | --- | --- |
| Fable 5.1 第一 | Claude Fable 5.1 (max with fallback) #1；GPT-6 Astra (max) #2 | 1.885 | 满足 | 满足 |
| GPT-6 Astra 第二 | GPT-6 Astra (max) #2；Claude Fable 5 (with fallback) #3 | 0.740 | 满足 | 满足 |
| Kimi K3 高于 Gemini 3.8 Flash | Kimi K3 (max) #10；Gemini 3.8 Flash (high) #9 | -0.006 | 未满足 | 未满足 |
| GPT-5.5 高于 Muse Spark 1.3 | GPT-5.5 (xhigh) #11；Muse Spark 1.3 (max) #6 | -3.121 | 未满足 | 未满足 |
| Qwen3.8 Max 高于 Qwen3.8 Flash-Next | Qwen3.8 Max #14；Qwen3.8-Flash-Next #22 | 2.176 | 满足 | 满足 |
| Qwen3.8 2.4T A95B 高于 Qwen3.8 Flash-Next | Qwen3.8 2.4T A95B #19；Qwen3.8-Flash-Next #22 | 0.562 | 满足 | 满足 |

**共同集合：**重新拟合后的前三名为 #1 Claude Fable 5.1 (max with fallback)（54.639）、#2 GPT-6 Astra (max)（52.755）、#3 Claude Fable 5 (with fallback)（52.014）。共同集合满足 4/6 条偏好，全量满足 4/6。共同集合与全量的六条偏好状态一致。

数据：[全量排名](rankings_dc08.csv) · [剔除与缺项](excluded_dc08.csv) · [共同集合排名](common_dc08.csv)。各项调整值、实际基础贡献、每领域基础分及加分都在全量 CSV 中。

<a id="dc09"></a>

## 09 多模态知识对照

**设计目的：**知识用 Omniscience Accuracy＋MMMU-Pro，加入图像与跨学科理解。

相对首套方案，调整领域为：知识／科学。其余计算规则相同。

| 领域 | Core 1 | Core 2 | 领域权重 | 两项在基础总分的权重 | 固定代表可用数1／2 | 入榜者双项完整／缺一 |
| --- | --- | --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench effective | SciCode | 20% | 10%／10% | 362／121 | 121／18 |
| Agent／工具工作 | AutomationBench-AA | τ³-Banking | 20% | 10%／10% | 110／145 | 110／29 |
| 高难推理 | CritPt | Humanity's Last Exam | 20% | 10%／10% | 357／437 | 139／0 |
| 知识／科学 | AA-Omniscience Accuracy | MMMU-Pro | 20% | 10%／10% | 354／147 | 74／65 |
| 指令／上下文 | AA-LCR v1.1 | GDP.pdf | 20% | 10%／10% | 354／109 | 108／31 |

- **编程：**Terminal-Bench effective：终端环境中的编程和工具任务；旧版按共同样本换算后折扣；SciCode：科学研究场景中的编程能力。
- **Agent／工具工作：**AutomationBench-AA：自动化工作流执行；τ³-Banking：银行场景中的交互和工具使用。
- **高难推理：**CritPt：研究级物理推理；Humanity's Last Exam：跨学科高难问题。
- **知识／科学：**AA-Omniscience Accuracy：知识问答的回答准确率；MMMU-Pro：多学科多模态理解和推理。
- **指令／上下文：**AA-LCR v1.1：长上下文推理；GDP.pdf：PDF 文档任务；使用 all-pass 成绩。

**取舍与适用性：**不同模型的图像能力与测评覆盖不同，缺 MMMU-Pro 不自动视为低能力，但会产生明确的半份分数损失。

本方案每领域基础分均为表中两项调整后值各乘 0.5；任一缺测时固定损失该项的半份贡献，该领域加分归零。十项总缺数和领域全缺门槛仍按共用规则执行。

**覆盖与缺测：**139 个模型入榜，332 个剔除；剔除者中 327 个触发领域全缺，332 个累计缺至少四项，其中 327 个同时触发，不能直接相加。入榜者缺 0／1／2／3 项人数分别为 **52／54／10／23**。

入榜者 Terminal 来源：v4.0 实测 102 个；v2.1 换算×0.95 36 个；Hard 换算×0.90 1 个；缺测 0 个。旧版换算是估算证据，不能当成 v4 实测。

**扩展加分：**本方案动态上限为每领域 **32.874** 分，再受领域 100 分封顶约束。具体扩展项目和当前可拟合数量如下；所有项目仍受双 Core 完整条件限制。

| 领域 | 保留的扩展项目 | 启用拟合／保留项目数 |
| --- | --- | --- |
| 编程 | benchmark:swe-bench-pro、benchmark:livecodebench | 1／2 |
| Agent／工具工作 | τ²-Bench Telecom、APEX-Agents-AA、benchmark:swe-bench-pro、benchmark:hle-tools、benchmark:mcp-atlas、benchmark:osworld-verified | 4／6 |
| 高难推理 | AIME 2025 | 1／1 |
| 知识／科学 | benchmark:mmlu-pro | 0／1 |
| 指令／上下文 | benchmark:charxiv-no-tools | 0／1 |

**实际算例：Claude Fable 5.1 (max with fallback)（本方案第 4 名）**

下表直接读取本方案的分项结果。“基础总分贡献”已经乘所在领域权重的一半（本轮均为 10%）；“领域最终总分贡献”已经计入扩展、领域封顶和 20% 权重。

| 领域 | Core 1 调整值 | Core 1 基础总分贡献 | Core 2 调整值 | Core 2 基础总分贡献 | 领域基础分 | 领域扩展加分 | 领域最终总分贡献 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench effective：52.020 | 5.202 | SciCode：63.079 | 6.308 | 57.549 | 2.370 | 11.984 |
| Agent／工具工作 | AutomationBench-AA：59.376 | 5.938 | τ³-Banking：47.217 | 4.722 | 53.296 | 8.873 | 12.434 |
| 高难推理 | CritPt：29.714 | 2.971 | Humanity's Last Exam：59.129 | 5.913 | 44.422 | 0.000 | 8.884 |
| 知识／科学 | AA-Omniscience Accuracy：67.233 | 6.723 | MMMU-Pro：缺测 | 0.000 | 33.617 | 0.000 | 6.723 |
| 指令／上下文 | AA-LCR v1.1：85.333 | 8.533 | GDP.pdf：26.200 | 2.620 | 55.767 | 0.000 | 11.153 |

十项基础贡献合计为 **48.930**；五项领域最终贡献合计为 **51.179**；封顶后的扩展净贡献为 **2.248**。该配置缺 1 项，Terminal 来源为 v4.0 实测。表内显示三位小数，逐格相加可能出现舍入尾差；精确复算使用 CSV 未舍入值。

**此前六条偏好审计：**

| 此前偏好 | 实际名次／比较对象 | 前者减后者分差 | 全量结果 | 共同集合结果 |
| --- | --- | --- | --- | --- |
| Fable 5.1 第一 | Claude Fable 5.1 (max with fallback) #4；GPT-6 Astra (max) #1 | -6.126 | 未满足 | 未满足 |
| GPT-6 Astra 第二 | GPT-6 Astra (max) #1；Claude Opus 5 (max) #2 | 1.407 | 未满足 | 未满足 |
| Kimi K3 高于 Gemini 3.8 Flash | Kimi K3 (max) #7；Gemini 3.8 Flash (high) #6 | -0.436 | 未满足 | 未满足 |
| GPT-5.5 高于 Muse Spark 1.3 | GPT-5.5 (xhigh) #10；Muse Spark 1.3 (max) #16 | 4.576 | 满足 | 满足 |
| Qwen3.8 Max 高于 Qwen3.8 Flash-Next | Qwen3.8 Max #12；Qwen3.8-Flash-Next #18 | 3.089 | 满足 | 满足 |
| Qwen3.8 2.4T A95B 高于 Qwen3.8 Flash-Next | Qwen3.8 2.4T A95B #30；Qwen3.8-Flash-Next #18 | -5.624 | 未满足 | 未满足 |

**共同集合：**重新拟合后的前三名为 #1 GPT-6 Astra (max)（57.305）、#2 Claude Opus 5 (max)（55.898）、#3 GPT-5.6 Sol (max)（53.716）。共同集合满足 2/6 条偏好，全量满足 2/6。共同集合与全量的六条偏好状态一致。

数据：[全量排名](rankings_dc09.csv) · [剔除与缺项](excluded_dc09.csv) · [共同集合排名](common_dc09.csv)。各项调整值、实际基础贡献、每领域基础分及加分都在全量 CSV 中。

<a id="dc10"></a>

## 10 电信＋银行覆盖对照

**设计目的：**Agent 用 Telecom＋Banking，观察较高历史覆盖能保留多少模型。

相对首套方案，调整领域为：Agent／工具工作。其余计算规则相同。

| 领域 | Core 1 | Core 2 | 领域权重 | 两项在基础总分的权重 | 固定代表可用数1／2 | 入榜者双项完整／缺一 |
| --- | --- | --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench effective | SciCode | 20% | 10%／10% | 362／121 | 121／211 |
| Agent／工具工作 | τ²-Bench Telecom | τ³-Banking | 20% | 10%／10% | 313／145 | 93／239 |
| 高难推理 | CritPt | Humanity's Last Exam | 20% | 10%／10% | 357／437 | 332／0 |
| 知识／科学 | AA-Omniscience Accuracy | GPQA Diamond | 20% | 10%／10% | 354／445 | 332／0 |
| 指令／上下文 | AA-LCR v1.1 | GDP.pdf | 20% | 10%／10% | 354／109 | 108／224 |

- **编程：**Terminal-Bench effective：终端环境中的编程和工具任务；旧版按共同样本换算后折扣；SciCode：科学研究场景中的编程能力。
- **Agent／工具工作：**τ²-Bench Telecom：电信场景中的交互和工具使用；τ³-Banking：银行场景中的交互和工具使用。
- **高难推理：**CritPt：研究级物理推理；Humanity's Last Exam：跨学科高难问题。
- **知识／科学：**AA-Omniscience Accuracy：知识问答的回答准确率；GPQA Diamond：研究生级科学知识与推理。
- **指令／上下文：**AA-LCR v1.1：长上下文推理；GDP.pdf：PDF 文档任务；使用 all-pass 成绩。

**取舍与适用性：**新旗舰通常缺 Telecom，旧模型则可能缺新版文档或科学编程结果；较广入榜不代表证据同样完整。

本方案每领域基础分均为表中两项调整后值各乘 0.5；任一缺测时固定损失该项的半份贡献，该领域加分归零。十项总缺数和领域全缺门槛仍按共用规则执行。

**覆盖与缺测：**332 个模型入榜，139 个剔除；剔除者中 133 个触发领域全缺，139 个累计缺至少四项，其中 133 个同时触发，不能直接相加。入榜者缺 0／1／2／3 项人数分别为 **68／43／32／189**。

入榜者 Terminal 来源：v4.0 实测 102 个；v2.1 换算×0.95 65 个；Hard 换算×0.90 165 个；缺测 0 个。旧版换算是估算证据，不能当成 v4 实测。

**扩展加分：**本方案动态上限为每领域 **27.062** 分，再受领域 100 分封顶约束。具体扩展项目和当前可拟合数量如下；所有项目仍受双 Core 完整条件限制。

| 领域 | 保留的扩展项目 | 启用拟合／保留项目数 |
| --- | --- | --- |
| 编程 | benchmark:swe-bench-pro、benchmark:livecodebench | 1／2 |
| Agent／工具工作 | APEX-Agents-AA、benchmark:swe-bench-pro、benchmark:hle-tools、benchmark:mcp-atlas、benchmark:osworld-verified | 2／5 |
| 高难推理 | AIME 2025 | 1／1 |
| 知识／科学 | MMMU-Pro、benchmark:mmlu-pro | 2／2 |
| 指令／上下文 | benchmark:charxiv-no-tools | 0／1 |

**实际算例：Claude Fable 5.1 (max with fallback)（本方案第 5 名）**

下表直接读取本方案的分项结果。“基础总分贡献”已经乘所在领域权重的一半（本轮均为 10%）；“领域最终总分贡献”已经计入扩展、领域封顶和 20% 权重。

| 领域 | Core 1 调整值 | Core 1 基础总分贡献 | Core 2 调整值 | Core 2 基础总分贡献 | 领域基础分 | 领域扩展加分 | 领域最终总分贡献 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 编程 | Terminal-Bench effective：52.020 | 5.202 | SciCode：63.079 | 6.308 | 57.549 | 2.370 | 11.984 |
| Agent／工具工作 | τ²-Bench Telecom：缺测 | 0.000 | τ³-Banking：47.217 | 4.722 | 23.608 | 0.000 | 4.722 |
| 高难推理 | CritPt：29.714 | 2.971 | Humanity's Last Exam：59.129 | 5.913 | 44.422 | 0.000 | 8.884 |
| 知识／科学 | AA-Omniscience Accuracy：67.233 | 6.723 | GPQA Diamond：93.737 | 9.374 | 80.485 | 0.000 | 16.097 |
| 指令／上下文 | AA-LCR v1.1：85.333 | 8.533 | GDP.pdf：26.200 | 2.620 | 55.767 | 0.000 | 11.153 |

十项基础贡献合计为 **52.366**；五项领域最终贡献合计为 **52.840**；封顶后的扩展净贡献为 **0.474**。该配置缺 1 项，Terminal 来源为 v4.0 实测。表内显示三位小数，逐格相加可能出现舍入尾差；精确复算使用 CSV 未舍入值。

**此前六条偏好审计：**

| 此前偏好 | 实际名次／比较对象 | 前者减后者分差 | 全量结果 | 共同集合结果 |
| --- | --- | --- | --- | --- |
| Fable 5.1 第一 | Claude Fable 5.1 (max with fallback) #5；Claude Fable 5 (with fallback) #1 | -7.043 | 未满足 | 未满足 |
| GPT-6 Astra 第二 | GPT-6 Astra (max) #7；Claude Fable 5 (with fallback) #1 | -8.510 | 未满足 | 未满足 |
| Kimi K3 高于 Gemini 3.8 Flash | Kimi K3 (max) #16；Gemini 3.8 Flash (high) #17 | 0.067 | 满足 | 满足 |
| GPT-5.5 高于 Muse Spark 1.3 | GPT-5.5 (xhigh) #4；Muse Spark 1.3 (max) #12 | 7.992 | 满足 | 满足 |
| Qwen3.8 Max 高于 Qwen3.8 Flash-Next | Qwen3.8 Max #24；Qwen3.8-Flash-Next #44 | 3.355 | 满足 | 满足 |
| Qwen3.8 2.4T A95B 高于 Qwen3.8 Flash-Next | Qwen3.8 2.4T A95B #37；Qwen3.8-Flash-Next #44 | 0.833 | 满足 | 满足 |

**共同集合：**重新拟合后的前三名为 #1 Claude Fable 5 (with fallback)（59.883）、#2 GPT-5.6 Sol (max)（57.289）、#3 GPT-5.6 Terra (max)（55.241）。共同集合满足 4/6 条偏好，全量满足 4/6。共同集合与全量的六条偏好状态一致。

数据：[全量排名](rankings_dc10.csv) · [剔除与缺项](excluded_dc10.csv) · [共同集合排名](common_dc10.csv)。各项调整值、实际基础贡献、每领域基础分及加分都在全量 CSV 中。

## 如何选择

**本次数据中的分差与扩展影响：**下表的分差统一为 Fable 5.1 减 GPT-6 Astra；正值表示 Fable 分数较高。“扩展造成的分差变化”已计入领域封顶。它展示第一、第二名附近的结果有多少来自基础分、有多少来自扩展。

| 方案 | Fable／Astra 名次 | Fable 基础总分 | Astra 基础总分 | 基础分差 | 最终分差 | 扩展造成的分差变化 |
| --- | --- | --- | --- | --- | --- | --- |
| 01 最新任务基线 | #1／#2 | 58.304 | 58.223 | 0.081 | 2.329 | 2.248 |
| 03 自动化＋知识工作 | #1／#2 | 59.391 | 59.389 | 0.003 | 1.695 | 1.693 |

**本次缺测影响：**06 算法编程对照 的 Top30 中，30/30 个模型至少缺一项 Core；08 数学竞赛对照 的 Top30 中，30/30 个模型至少缺一项 Core；10 电信＋银行覆盖对照 的 332 个入榜模型中，十项完整者 68 个，缺三项者 189 个。这些人数是本次结果，应结合基础总分和缺项查看。

先选择最接近实际使用场景的 Core 组合，再检查覆盖损失和缺测分布；同时对照共同集合、基础总分和最终分，判断变化是否主要由扩展加分带来。此前偏好的满足数量只是事实对照，不构成方案质量的独立证据。
当前换算和扩展回归来自同一份横截面数据，没有跨时间留出验证；新模型加入、成绩更新和 Terminal 版本覆盖变化都可能改变拟合与名次。Elo、通过率、多模态和代码成绩也不具有天然相同的难度尺度。
