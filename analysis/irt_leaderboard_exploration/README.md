# AIndex 生产计分与历史实验

当前网站采用用户选定的 **Mixed Core 07（第 7 套）**，生产模块为 `aindex_mixed_core.py`，独立校验为 `validate_mixed_core_production.py`。实验搜索模块与模型顺序偏好不进入生产导入链，也不决定每日发布是否通过。

| 领域 | Core 项目 | 权重 |
| --- | --- | ---: |
| 编程 | Terminal-Bench v4.0、SciCode | 12% |
| Agent／工具工作 | AutomationBench-AA、τ³-Banking | 9% |
| 高难推理 | CritPt | 22% |
| 知识／科学 | AA-Omniscience Accuracy、GDP.pdf | 37% |
| 指令／上下文 | AA-LCR v1.1 | 20% |

单 Core 占本领域基础分 100%，双 Core 各占 50%。缺项的份额不重新分配、贡献为零，原始观测仍保持缺失；观测到的零分有效。任一领域 Core 全缺，或累计缺少至少 4 个已配置 Core 项目，即不排名。先按 variantPriority 降序、slug 升序选定系列代表，再判断准入；不能通过改选配置或跨配置借分补齐。

Terminal 只用 v4，不使用 v2.1 或 Hard，也不把旧版作为扩展。AIME、LiveCodeBench、GPQA 及旧短数学测试不进入 Core。本轮只变更 Core，扩展准入和算法延续原规则：全局去除 Core 家族后，独立控制的扩展测试仅在本领域 Core 完整时拟合／发放奖励。

```text
core_b = sum(observed_score_or_zero) / configured_core_count
residual_bik = max(y_bik - clip(alpha_bk + max(beta_bk, 0) * core_bi, 0, 100), 0)
raw_bonus_b = log(1 + sum(expm1(residual_bik)))
cap = mean(all_positive_residuals) + sqrt(2) * population_sd(all_positive_residuals)
bonus_b = min(raw_bonus_b, cap) if complete_board_core else 0
board_score_b = min(100, core_b + bonus_b)
final_score = sum(board_score_b * board_weight_b / 100)
```

OLS 趋势与统一 cap 在符合准入的固定代表集合上按领域 Core 完整子集拟合，精确配置使用同一标尺、不重新拟合。只按未舍入分数降序，完全相同时用稳定 ID。生产校验独立复算原始 Core、残差、cap、加权贡献、去重与精确配置排名，以及站点序列化结果；不包含具名模型名次门槛。

历史 Scheme 18、2PL 和 Rasch 等审计文件继续输出用于对照，其资格条件不会阻止符合新规则的模型获得主分。下面保留历史分析过程和实验说明；其中方案 18 的描述仅适用于旧方法。

## 证据审计：纯证据 2PL

对需要复核单一 2PL 设定的计算过程，可运行 `evidence_only_ranking_analysis.py`。它是补充审计方法，不替代方案 18 主分。该版本：

- 不读取任何产品顺序规则，不固定任何模型名次。
- 不使用固定缺项扣分；每板块至少 2 个可比 benchmark family 才入榜。Main 目标为每板 3 项，若整个 scoped item pool 少于 3 项则以跑满该板为准。
- 排名使用带 ridge 正则的连续 2PL 点估计（MAP-like，不是贝叶斯后验均值）；LCB 敏感性先在每个板块计算 `theta - 0.67 × SE`，再经 CDF 与五板块聚合，另报敏感性分数和名次但不改变主榜。
- 排除跨 effort/变体复制的 `sharedFromVariant` 成绩、站点拟合的 LiveCodeBench 回填，以及 effort 或 fallback 无法映射到单一模型配置的厂商成绩。
- Terminal-Bench 2.1、HLE、GPQA、AIME、MMMU-Pro、IFBench 对所有模型统一使用 Artificial Analysis 协议，不逐模型择高混用不同 harness。

当前官方数据快照下，Claude Opus 5 (max) 为第 1（Provisional，五板块覆盖 `5 / 5 / 3 / 5 / 2`），Qwen3.8 Max 为第 10（Main，`3 / 7 / 3 / 5 / 3`）。这是证据自然产生的结果，不是名次规则。

## 重要边界

源数据只有模型在整项 benchmark 上的聚合分数，没有题目级 0/1 作答。因此方案 18 的 partial-credit Core、匿名残差扩展，以及保留的 Rasch / 2PL 审计都属于 **benchmark-as-item measurement / IRT-inspired**，不是经典题目级 IRT。它们适合做相对榜单和方法审计，不应把参数解释为正式量表中的题目难度或模型绝对能力。

同一 benchmark family 在同一板块内的同义来源会合并，例如 HLE、GPQA Diamond 和 AIME 2025 的常规列与外部列只占一个覆盖槽位。同一 benchmark 仍可能跨板块出现，这是现有能力分类法的延续，也意味着板块间存在局部相关性。

## 历史五套实验（非生产）

以下内容解释早期覆盖校正与板块权重实验，只为复现实验文件；它们不参与当前站点主榜，也不是推荐方法。

### 1. 当时的 AIndex（历史基准）

直接调用项目当前的 `zhihu-adjusted` 计分逻辑，并按站点的 variant-priority 规则对同一模型的不同档位去重。基准方案的 `score` 与 `native_aindex` 都是站点当前 AIndex 原始分。

### 2. 连续 1PL/Rasch + 现行板块权重

对百分制 benchmark 先计算 `logit(clip(x / 100, 0.01, 0.99))`；只有相对名次含义的指标先转成样本内百分位。板块内拟合：

```text
z_mj = theta_m - difficulty_j + error_mj
```

观测较少的 benchmark 使用 `n / (n + 20)` 降权，并对能力和难度使用 ridge 收缩。板块分使用能力的保守下界：

```text
board_score = 100 * Phi(theta_z - 0.45 * SE_z - 0.45 * max(0, 3 - coverage))
```

五板块按现行 `40 / 24 / 20 / 8 / 8` 权重做 `log1p` 几何式合成。

### 3. 强收缩 2PL + 五板块等权

板块内拟合：

```text
z_mj = discrimination_j * theta_m + intercept_j + error_mj
```

少于 50 个模型观测的 benchmark 将区分度固定为 1；其余区分度用强 ridge 收缩并限制在 `[0.35, 2.5]`。板块分使用更保守的 `0.67 * SE` 和 `0.55 * shortfall`，五板块等权合成。

### 4. 稳健秩变换 + 贝叶斯式收缩

先在每个 benchmark 内做秩正态变换，再用固定先验精度 2 收缩模型的板块均值。板块分扣除 `0.50 * SE` 和 `0.50 * shortfall`，五板块等权合成。该方案不依赖不同 benchmark 的原始分数尺度，作为模型设定稳健性参照；先验强度并非从当前样本估计，因此不把它宣称为严格的经验贝叶斯。

### 5. 收缩 Borda + 广度优先合成

每个 benchmark 的百分位先以 20 个伪观测向 50% 收缩，板块内再做小样本收缩与覆盖惩罚。五板块通过几何均值合成，任何明显短板都会更强地拉低总分，因此它更接近“能力广度榜”。

## 历史产品约束实验（已停用）

本节只记录 `constrained_ranking_analysis.py` 的旧实验。当前生产榜不执行这些产品边、软扣分或 raise-only 投影。

- `Main`：五个板块均至少 3 项，且至少覆盖 9 个唯一 benchmark family。
- `Provisional`：已满足每板块至少 2 项的入榜门槛，但未达到 Main；允许展示和按产品规则调整，必须同时展示证据标签。
- 独立家族软目标为 12；每缺 1 个家族扣 `0.08` 个榜内标准差。
- Qwen 只约束明确可比的产品边，不把所有开放权重尺寸、模态或子系列强行排成一条总序。
- 硬约束使用 raise-only 投影：提升声明中更强的新型号，并保留原始测量名次和位移供复核。

当前 Qwen 边为：Qwen3.8 Max > Qwen3.7 Max > Qwen3.6 Max Preview > Qwen3 Max；Qwen3.7 Plus > Qwen3.6 Plus；同版本 Max > Plus；Qwen3.5 Omni Plus > Flash。

## 历史方法的数据与覆盖规则

- 少于 8 个去重模型家族有观测的 benchmark 不进入拟合。
- 每个板块的覆盖数按 canonical family 计算，不按同义来源重复计算。
- 替代榜的“未入榜”表示证据不足，不表示能力为零。
- 跨板块复用同一 benchmark 会形成多个“板块测试槽位”；因此总和应解释为 `board test slots`，而不是统计独立的测试数。
- 稳定性分析按 26 个唯一 benchmark family 逐个删除，并在该 family 出现的所有板块同时删除。秩相关只在删除后仍合格的人口上计算，因此必须与合格人口保留率、Top 50 保留率一起阅读。

## 运行

在项目根目录运行：

```powershell
python -B analysis\irt_leaderboard_exploration\irt_leaderboard_analysis.py
python -B analysis\irt_leaderboard_exploration\constrained_ranking_analysis.py
python -B analysis\irt_leaderboard_exploration\evidence_only_ranking_analysis.py
python -B analysis\irt_leaderboard_exploration\multi_method_evidence_analysis.py
python scripts\build_docs_site.py
python -B analysis\irt_leaderboard_exploration\validate_scheme18_production.py --input docs\data\models.json
```

分析和验证脚本只依赖 Python 标准库和 NumPy，不访问网络。`build_docs_site.py` 在读取已刷新数据后生成方案 18 站点 profile 与生产 CSV/JSON；独立 validator 随后从 `docs/data/models.json` 复算并校验。Notebook 是历史分析的可执行伴随文件：

```text
analysis/irt_leaderboard_exploration/irt_leaderboard_exploration.ipynb
```

## 输出

- `outputs/full_rankings_aindex_scheme18.csv`：默认 `variantGroup` 去重人口的方案 18 全榜，包含五板 Core、bonus、扩展覆盖与未舍入最终分。
- `outputs/top50_aindex_scheme18.csv`：同一真实分数顺序下的 Top 50。
- `outputs/full_rankings_exact_config_aindex_scheme18.csv`：关闭去重时使用的逐配置方案 18 全榜；外部成绩必须明确为 `variantScoped` 才能进入对应配置。
- `outputs/top50_exact_config_aindex_scheme18.csv`：逐配置方案 18 Top 50。
- `outputs/aindex_scheme18_validation_summary.json`：方法 ID、动态 cap、输入人口、分数恒等式、排序、benchmark policy、站点 join 与关键回归检查。

以下文件属于旧 2PL/Rasch 或其他探索方法，只作敏感性审计：

- `outputs/full_rankings_twopl_sparse_80_20_score.csv`、`outputs/top50_twopl_sparse_80_20_score.csv`：上一代 80/20 能力分结果。
- `outputs/exact_config_multi_method_full_rankings.csv`、`outputs/full_rankings_exact_config_twopl_sparse_80_20_score.csv`、`outputs/top50_exact_config_twopl_sparse_80_20_score.csv`：上一代逐配置对照。
- `outputs/exact_config_score_visibility_audit.csv`：上一代逐配置可见性审计。

- `outputs/top50_all_schemes.csv`：五套方案各 50 行，共 250 行。
- `outputs/full_rankings_all_schemes.csv`：全部可排名模型。
- `outputs/coverage_profile.csv`：五板块覆盖分布。
- `outputs/scheme_diagnostics.csv`：与基准的相关性、Top 50 重合和留一法稳定性。
- `outputs/pairwise_rank_correlations.csv`：方案两两名次相关。
- `outputs/item_parameters.csv`：1PL/2PL benchmark 参数与样本量。
- `outputs/lobo_stability_by_item.csv`：按唯一 benchmark family 跨板块删除后的合格人口、条件秩相关和 Top 50 保留率。
- `outputs/validation_summary.json`：数据质量、覆盖、稳定性和验证摘要。
- `report/irt_leaderboard_exploration.html`：面向产品决策者的中文主报告。
- `outputs/top50_constrained_schemes.csv`：五套“覆盖校正 + 产品约束”方案各 50 行，共 250 行。
- `outputs/full_rankings_constrained_schemes.csv`：五套约束方案的全量榜单，含原测量分、约束前名次和位移。
- `outputs/constrained_validation_summary.json`：历史产品约束与 Top 50 行数等验收结果。
- `outputs/constraint_sensitivity.csv`：Gemini Flash 开源下限 5 / 10 / 15 的敏感性结果。
- `outputs/external_source_assessment.csv`：外部权威来源的接口、时效、许可与模型映射风险审计。
- `report/constrained_leaderboard_exploration.html`：历史产品约束版报告，仅作产品规则对照，不再作为纯证据榜入口。
- `outputs/evidence_only_top50.csv`：纯证据 2PL Top 50 审计文件，不作为发布候选榜。
- `outputs/evidence_only_full_rankings.csv`：纯证据版全部合格 variant group。
- `outputs/evidence_only_validation_summary.json`：纯证据口径、清洗计数、目标模型覆盖和不确定性摘要。
- `outputs/multi_method_top50.csv`：七法原始证据 Top 50 审计合表，不作为发布候选榜。
- `outputs/top50_<method>.csv`：每种无模型修正方法的原始证据 Top 50 审计文件。
- `outputs/multi_method_full_rankings.csv`：七法原始证据层的全部合格 variant group。
- `outputs/multi_method_validation_summary.json`：方法、门槛、清洗计数与目标模型名次。
- `outputs/target_exact_config_comparison.csv`：固定 exact config 的跨方法对照，避免不同方案切换 effort。
- `outputs/target_source_coverage_audit.csv`：官方直接成绩进入/未进入共同协议的数量。
- `outputs/key_pair_overlap_audit.csv`：Sol/Opus、Luna/DeepSeek 的共同原始 benchmark 明细。
- `outputs/method_stability.csv`：方法两两 Spearman 与 Top 50 重合。

## 外部来源与每日 Action

每日 Action 先运行 `benchmarks/collect_benchmark_scores.py`，再由 `scripts/build_docs_site.py` 用最新快照重算方案 18 和站点数据，最后显式运行 `validate_scheme18_production.py`。只有 validator 通过，五个稳定命名的方案 18 生产输出与 `docs/data/models.json` / `models.js` 才会进入自动提交；321 种 v5 探索目录不会被 broad-stage。

Qwen3.8-Max、GPT-5.6、Claude Opus 5 与 Fable 5 System Card 已纳入同一来源库。Qwen 使用官方 article-retrieval JSON API 获取文章表格，并对 `Pass / Score`、`without / with Code Interpreter`、`binary / partial` 等复合单元格做显式语义选值；当前在线解析值与审计 seed 必须一致。GPT-5.6 官方成绩按 exact configuration 绑定，禁止向其他 effort 广播。Fable 新闻图的 higher-of-two 结果保留在来源库但不作为可拆分配置的 Core；榜单使用可映射到具体配置的 System Card 成绩。图片/PDF 表无法可靠解析时继续使用已审计、带来源和版本说明的 seed。

## 2026-09-09 Core 小规模候选实验

运行 `python -B analysis/irt_leaderboard_exploration/core_variants.py`，查看
`outputs/core_variants/REPORT.md`。A/B/C 分别比较 Banking、AutomationBench
和增加 GDP.pdf 的 Core；D 与 B 使用同一 Core，但将旧版 Terminal 成绩先
换算到 v4 尺度再折扣。参数集中在 `core_variants.py` 的 `VARIANTS`。

实验保留五板等权、几何 Core 和正残差加分，固定每组配置后才检查完整性，
并输出覆盖清单、全量排名、缺项清单和共同人群排名。旧版回退只读取同一
配置；v4 实测零分不会触发回退。扩展中剔除新 Core 和 Terminal 版本重复项。
这些文件是试算产物，未接入生产评分或每日 Action 的自动生成路径。

后续按用户指定排序偏好筛选的 E/F/G 见
`outputs/preference_core_variants/REPORT.md`；运行
`python -B analysis/irt_leaderboard_exploration/preference_core_variants.py`
可复现 Core／权重搜索和逐项约束审计。模型偏好只在评分后检查，不作为模型
加减分或排序覆盖；这些试算未替换生产榜。测试仅验证计算和审计机制，
不要求未来每日快照必须继续符合本轮命名模型的顺序。

## 2026-09-11 十套双 Core 组合实验

本节保留此前的结构对照。当前结果见“两个单 Core 领域的混合方案”；
未满足全部排序偏好的结构对照不再作为本轮推荐。

运行 `python -B analysis/irt_leaderboard_exploration/dual_core_variants.py`，生成：

- [十套方案完整说明](outputs/dual_core_variants/SCHEMES.md)：每套十个 Core、权重、调整公式、缺测与扩展规则、实际算例、覆盖及旧排序偏好审计。
- [独立 Top30 对比](outputs/dual_core_variants/TOP30_COMPARISON.md)：跨方案名次矩阵、十套完整 Top30、共同入榜模型的对比。
- `outputs/dual_core_variants/top30_all.csv`：十套 Top30，共 300 行；各套另有全榜、剔除原因及共同人口 CSV。
- `outputs/dual_core_variants/run.json`：输入 SHA-256、Terminal 版本换算参数、校准值及数值验证结果。

五领域各占 20%，每领域恰好两项不同家族 Core；两项调整分各占该领域基础分的 50%，
即每项向总基础分贡献调整分 × 10%。单项缺测保留缺测标记，计算时其固定份额为零，
不重新分配权重；任一领域双缺，或十项累计缺至少四项，即剔除。真实零分视为已观测。
Terminal 优先 v4，同配置旧版先换算尺度，再对 v2.1／Hard 分别乘 0.95／0.90。
扩展拟合与加分只在本领域两项 Core 都有观测时进行，Core 家族不重复作为扩展加分。

按用户最新选择，这十套优先比较 Core 结构，五领域始终等权，逐项披露旧模型排序偏好是否满足。
本轮沿用 2026-09-08 的冻结输入；每套入榜人口与扩展校准可能不同，另以 112 个共同模型重算作参照。
这些结果是候选实验，未替换生产方案 18 或每日 Action 的评分路径。

验证命令：`python -B -m unittest discover -s tests -p '*core_variants.py' -v`。

## 2026-09-11 先筛选的双 Core 方案（此前六条标准）

此前采用六条标准和旧版 Terminal 回退的冻结结果保留在：

- [通过筛选的十套完整说明](outputs/filtered_dual_core_variants/SCHEMES.md)。
- [通过筛选的十套 Top30 对比](outputs/filtered_dual_core_variants/TOP30_COMPARISON.md)。

先要求 Fable 5.1 第一、GPT-6 Astra 第二、Kimi K3 高于 Gemini 3.8 Flash、
GPT-5.5 高于 Muse Spark 1.3，以及 Qwen3.8 Max／2.4T A95B 分别高于 Flash-Next；
六条分差均须严格大于 0.05 分。入选方案在全量及共同入榜人群中都必须通过，
否则脚本在写出排名和文档前终止。该筛选仅用于当前候选实验，不是每日 Action 的命名模型名次断言。

双 Core 的固定半份、领域双缺剔除、累计缺至少四项剔除、同配置 Terminal 回退及完整领域扩展规则继续保留。
领域权重仍限制 10%–40%，总和 100%；步长从 5 个百分点细化为 1 个百分点，未放宽分差门槛。
当前搜索 240 种组合，其中 160 种满足十个不同测试家族要求，144 种通过入榜人口／目标可用性预筛，
总计检查 39,164,544 个 Core／权重组合，65 个通过全量筛选。它们只有两种不同 Core 结构，
各选五个不同权重方案，共十套；所有十套在 127 个共同模型上也通过。

`search.json` 保存搜索边界及全部通过组合，`run.json` 保存输入哈希、校准、各项筛选和权重敏感性。
20 种正负 1 个百分点转移包含越过搜索范围的压力测试，不是额外入选条件。
通过偏好意味着适合本次用户约束，不构成模型能力的独立验证；正式方案 18 尚未切换。

## 2026-09-11 仅用 Terminal v4 的九条筛选方案（历史候选）

运行 `python -B analysis/irt_leaderboard_exploration/filtered_dual_core_variants.py`，查看：

- [新版十套完整说明](outputs/filtered_dual_core_v4/SCHEMES.md)。
- [新版十套 Top30 对比](outputs/filtered_dual_core_v4/TOP30_COMPARISON.md)。
- [排名异常审计](outputs/filtered_dual_core_v4/RANKING_AUDIT.md)：GPT-5 mini、Claude 4.5 Sonnet 的分项贡献，以及 Gemini 3 Flash 的正常缺测处理。

Terminal 只用同一固定配置的 v4.0 实测，无成绩记缺项，实测零分仍有效。
v2.1 与 Hard 不进入本轮 Core、回退、扩展或版本映射拟合。Gemini 3 Flash
（模型组 `gemini 3 flash`）已撤销人工排除，和 Gemini 3.8 Flash 一样按统一规则处理。
本快照的固定代表配置缺 Terminal v4、SciCode、AutomationBench-AA、GDP.pdf，
因此仍因编程领域双缺、累计缺四项而未入榜；没有额外扣分或固定名次。
`user_exclusions.csv` 现为空，`excluded_*.csv` 列出正常双 Core 缺测剔除。

在此前六条偏好上新增 GPT-5.6 Sol > Claude Opus 5、GPT-5.6 Terra > Muse Spark 1.3、
Grok 4.6 > Grok 4.5。九条均须有超过 0.05 分的分差，全量和共同集合都必须通过。
目标配置仍由预先固定的 variantPriority 决定，不借其他推理档位的成绩；Grok 4.6 使用 xhigh。

原 10%–40% 权重范围检查 19,310,296 组后零通过，因此将搜索下限小幅扩至 9%，
上限仍为 40%，步长 1 个百分点。9%–40% 范围检查 26,083,696 组，30 组通过，
仅有一种合格 Core 结构，从中选十组权重，均有 112 个入榜模型。这个下限变化是显式的搜索参数调整，
九条排序标准、分差门槛、每领域双 Core 各半、领域双缺或总缺至少四项剔除规则保持不变。
`search.json` 与 `run.json` 同时保留原范围零通过的记录和新范围参数。

本轮已确认明显的覆盖偏差：AIME 2025 单项占总分 15%–20%，旧模型有高分、
多数关注的新旗舰缺测计零。例如方案 05 中，GPT-5 mini 与 Claude 4.5 Sonnet
分别由 AIME 获得 18.13、17.60 分，而 GPT-5.6 Sol／Terra、GPT-5.5、Kimi K3 此项贡献为零。
逐项复算未发现本地成绩映射、加权求和或排序错误，但通过九条指定顺序不足以证明全榜合理。
当前十套只保留为方法对照，不宜直接选作正式综合能力榜；审计详见上方文档。
这仍是基于 2026-09-08 快照的候选实验，未修改正式方案 18 或每日 Action。

## 2026-09-11 任务与高难测试双 Core 下一轮（上一轮结果）

运行 `python -B analysis/irt_leaderboard_exploration/task_core_variants.py`，生成：

- [本轮筛选结果与冲突诊断](outputs/task_dual_core/SEARCH_REPORT.md)。
- [Core 质量、近期覆盖和分数分布](outputs/task_dual_core/CORE_QUALITY.md)。
- [本轮 Top30 状态](outputs/task_dual_core/TOP30_COMPARISON.md)：当前没有合格方案，不展示不合格榜单。

本轮从 Core 禁止 AIME 全年度／别名及同类短题数学家族、LiveCodeBench、GPQA。
旧实验保留以便追溯；新的准入在 `task_core_variants.py` 中集中校验，不靠型号专属扣分。
扩展政策不变，AIME 仍可作为受完整领域、正残差和动态封顶限制的扩展项。
Terminal 仅 v4、九条指定顺序、严格大于 0.05 的分差、9%–40% 权重以及双 Core 缺测门槛均保留。

候选池扩展为 270 种配对，70 种满足十个不同家族要求；每项都有至少 100 个固定代表配置的成绩。
7 种因目标模型触发缺测门槛退出，63 种进入搜索；每种枚举 367,376 组权重，
总计检查 23,144,688 组，**零组通过**。额外的连续权重线性规划也全部无解，
全局最优最小分差为 −0.488367 分；仅细化步长不能解决本候选池中的条件冲突。
该结果限定于当前 Core 池及冻结快照，不表示任何可能的评分体系均无解。

Core 质量审计按发布日期选择匿名近期群体（2026-03-12 至 2026-09-08，闭区间，124 个固定代表）；
AIME、LiveCodeBench 在该群体都没有观测，GPQA 在 14 个关注配置上全部达到 90 分以上。
这分别说明覆盖断层和前沿高分集中，不能据此认定刷分或污染。

新脚本不会写正式站点或 Action。整数权重搜索只需项目现有 NumPy；可选的连续权重诊断使用 SciPy，
未安装时明确跳过该诊断，整数搜索照常完整执行。`run.json` 保存源哈希与规则，
`search.json` 保存逐结构资格、完整通过集和连续诊断。

## 2026-09-11 两个单 Core 领域的混合方案（当前候选）

按用户选择，本轮固定两个领域各一项 Core、三个领域各两项，共八项；单项承担领域基础分100%，
双项仍各50%。唯一Core缺测即领域全缺剔除；双Core缺一项保持半份计零；未配置的第二项不算缺测，
累计缺至少四项规则保留。AIME、LiveCodeBench、GPQA不进入Core，Terminal仍仅v4，无人工排除。

运行 `python -B analysis/irt_leaderboard_exploration/mixed_core_variants.py`：

- [十套方案完整解释](outputs/mixed_core/SCHEMES.md)。
- [独立 Top30 对比](outputs/mixed_core/TOP30_COMPARISON.md)。
- [搜索范围、选择过程](outputs/mixed_core/SEARCH_REPORT.md)。
- [Core质量与覆盖](outputs/mixed_core/CORE_QUALITY.md)。

本轮考察2,295种配对；1,165种家族不重复，498种满足资格条件后搜索182,953,248组Core／权重组合。
21种结构的18,834组权重通过全量九条标准；最终选出十种不同结构，各一套权重，
均在全量及107个共同模型重算后通过九条标准。每领域权重仍为9%–40%，1个百分点步长，严格分差>0.05。
每结构先保留最接近等权16组与最小分差最大16组（去重），再择不同结构并复核共同人群；
完整合格权重保存在`passing_weights.npz`，不将有限选择池说成穷举所有十方案组合。

方案01以CritPt、Omniscience分别作为推理和知识单Core，编程保留Terminal v4＋SciCode，
Agent保留Automation＋Banking，上下文保留LCR＋GDP.pdf；可作为理解新规则的起点。
十套中GPT-5 mini自然排31–57，Claude 4.5 Sonnet排47–55，无模型专属降权。
Gemini 3 Flash仍按正常编程全缺规则不入榜。

实现另外封住了SciCode单Core会使旧Terminal扩展重新出现的路径：无论Terminal是否被选作Core，
v2.1／Hard均不得进入扩展。其他扩展规则不变，但会随Core及合格人群重新拟合。
全双Core配置经冻结数据与原引擎逐字段等价验证；十套全榜与共同集合还独立核对了原始成绩、
固定份额、缺测、总分和排序，见`independent_validation.json`。
这些方案依然是按指定顺序筛选的实验，未修改正式方案18、站点和每日Action。

## 生产限制与后续工作

1. 扩展池中部分成绩仍混合 result operator、agent scaffold、prompt、采样或版本；benchmark 控制方独立并不消除这些协议差异。
2. Bonus 只增不减且由多项正残差累积，因此测试覆盖更广的模型拥有更多产生正信号的机会；动态 cap 和覆盖字段只能限制、不能完全消除这一机会差异。
3. Coding 与 Agentic/tool work 的 Core 当前各只有一项，其他板块分别为 3 / 4 / 2 项；新增 Core 必须先满足控制方、协议、覆盖和可自动更新要求，并做跨周期影子验证。
4. 同一 benchmark family 可能跨板复用，五板并非统计独立。新增或调整板块映射时必须检查隐式重复影响。
5. 方案 18 是 benchmark-as-item / partial-credit measurement，不是题目级经典 IRT。若要称为正式心理测量量表，仍需题目级响应和稳定的校准样本。
