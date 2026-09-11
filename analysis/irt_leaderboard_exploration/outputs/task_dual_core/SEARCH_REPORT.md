# 任务与高难测试双 Core：本轮筛选结果

冻结快照：2026-09-08T23:56:02+00:00；本轮通过全量筛选的 Core／权重组合 **0** 个，最终通过共同集合复核并展示 **0** 套。

本轮只改变 Core 准入和配对池。AIME（含年度／别名及同类短题数学家族）、LiveCodeBench、GPQA 不得进入 Core；扩展加分沿用原规则，AIME 仍可作为受完整领域条件、正残差和动态上限约束的扩展。

每领域两项各占基础分一半；缺项固定份额计零；领域双缺或累计缺至少四项剔除。只用 Terminal v4，固定配置先于缺测检查，真实零与缺测区分；没有模型专属扣分或人工排除。

## 搜索范围与结果

候选配对共 270 种；200 种因重复家族或准入限制无效，70 种结构合法。每个 Core 至少有 100 个固定代表配置的直接成绩。
0 种未满足单项覆盖门槛；7 种未满足目标模型／总体入榜门槛；63 种进入权重搜索。
每领域 9%–40%，总和 100%，步长 1 个百分点；每结构 367,376 组，实际检查 **23,144,688** 组 Core／权重组合。

九条偏好均保持不变，分差必须严格大于 0.05 分：

1. Fable 5.1 第一。
2. GPT-6 Astra 第二。
3. Kimi K3 高于 Gemini 3.8 Flash。
4. GPT-5.5 高于 Muse Spark 1.3。
5. Qwen3.8 Max 高于 Qwen3.8 Flash-Next。
6. Qwen3.8 2.4T A95B 高于 Qwen3.8 Flash-Next。
7. GPT-5.6 Sol 高于 Claude Opus 5。
8. GPT-5.6 Terra 高于 Muse Spark 1.3。
9. Grok 4.6 高于 Grok 4.5。

## 领域配对依据

编程固定 Terminal v4＋SciCode；Agent 枚举自动化、银行、电信、Briefcase 和 GDPval 的两两组合。推理枚举 CritPt、HLE、LCR；知识固定 Omniscience，再配 HLE、MMMU-Pro 或 GDP.pdf；上下文枚举 LCR、GDP.pdf、IFBench。所有十个槽位必须来自十个不同家族。

LCR 进入推理会增加长上下文成分；GDP.pdf 在来源注册表中归为 Knowledge work vision，进入知识领域有任务定义依据。GDPval 和 Briefcase 的 Elo 线性换算不代表原生通过率。扩池用于检验可行性，不表示这些组合的测量质量等价。

## 独立连续权重诊断

对 63 个可评估结构，额外允许 9%–40% 内任意小数权重，最大化全部排序不等式中的最小分差。所有结构中的最优值为 **-0.488367 分**；门槛是 **严格大于 0.05 分**。

连续范围也没有合格解，所以仅把步长细化为小数无法解决当前冲突。此结论限定于上述 Core 池、冻结成绩和计分规则。

以下仅为冲突诊断，不是可选方案，不发布其 Top30：

- 编程：Terminal-Bench v4.0＋SciCode
- Agent／工具工作：AutomationBench-AA＋GDPval-AA v2
- 高难推理：Humanity's Last Exam＋AA-LCR v1.1
- 知识／科学：AA-Omniscience Accuracy＋MMMU-Pro
- 指令／上下文：GDP.pdf＋IFBench

该最优边界同时受以下排序关系限制：

- GPT-6 Astra (max) − Claude Opus 5 (max)：-0.488367 分。
- GPT-6 Astra (max) − Claude Fable 5 (with fallback)：-0.488367 分。
- GPT-5.6 Sol (max) − Claude Opus 5 (max)：-0.488367 分。
- Grok 4.6 (xhigh) − Grok 4.5 (high)：-0.488367 分。

逐结构的最大分差、单独无法满足的模型对、领域差值和缺测原因均保存在 [search.json](search.json)。

## 本轮结论

本轮没有可展示的合格方案，因此没有生成不合格榜单来凑足十套。下一步应增加覆盖充分且符合 Core 准入的任务／高难测试数据，或明确调整排序条件／计分假设后再搜索。本轮没有替用户放宽这些条件。

测试覆盖、近期群体和分数集中情况见 [CORE_QUALITY.md](CORE_QUALITY.md)。

复现：`python -B analysis/irt_leaderboard_exploration/task_core_variants.py`。整数权重搜索依赖现有 NumPy；连续权重诊断额外使用 SciPy，未安装时只跳过该诊断，仍完整运行整数网格。

来源：冻结 `docs/data/models.json` 与 `ArtificialAnalysis/artificialanalysis_raw_scores_wide.csv`；源哈希、规则、搜索计数见 [run.json](run.json)。正式方案 18、站点和每日 Action 均未切换。
