# 覆盖感知的 IRT 榜单探索

这是一套基于 `docs/data/models.json` 快照的可复现榜单实验。它保留 Coding、Agentic/tool work、Hard reasoning、Knowledge/science、Instruction/context 五个能力板块。当前推荐入口是 `multi_method_evidence_analysis.py`，并严格分成两层：

- **证据层**：七种方法只用真实成绩计算，分数不做模型级修正。
- **发布层**：所有候选榜统一要求 Claude Fable 5 为第 1、GPT-5.6 Sol 为第 2；分数不变，原名次写入 `evidence_rank`，其余模型保持原证据相对顺序。

- 硬门槛：每个板块至少有 2 个 canonical benchmark family，否则不入榜。
- Main 目标：每个板块至少 3 项；未达到时标为 `Provisional`，但覆盖本身不进入主分数。
- Core item 至少覆盖 8 个独立 `variantGroup` 和 3 个 creator，避免一个产品的多个 effort 行虚增样本量。
- 证据分不使用产品顺序、模型名修正、固定缺项扣分或手工板块权重；板块方案均严格五等分。
- 发布排序只按稳定 ID 定位两个锚点：Fable 使用 `slug=claude-fable-5`，Sol 使用 `variant_group=gpt 5 6 sol`，不依赖显示名或某个固定 effort。

`constrained_ranking_analysis.py` 是早期产品规则实验，仅保留作历史对照，不是当前推荐榜，也不应当用于证明模型强弱。

## 当前推荐：等板块 2PL 70% / 稀疏 Rasch 30% 加权名次

同一份净化后的成绩矩阵仍并行运行七种真实成绩方法用于审计，但站点主榜只采用一个明确的共识口径：先分别生成等板块 2PL 与稀疏项 Rasch 的未锚定证据名次，再计算

```text
rank_mean = 0.70 * twopl_equal_board_rank + 0.30 * sparse_item_rasch_rank
```

加权名次越低越好。完全相同时依次比较 2PL 名次、稀疏 Rasch 名次和稳定 ID；不平均发布层名次，也不引入模型修正。70/30 只是在两个匿名证据方法之间公开固定的合成比例，不是模型特定或 benchmark 特定加权。完成证据排序后，才单独应用 Fable #1、GPT-5.6 Sol #2 的透明发布层。七种审计方法为：

1. 无观测权重的连续 1PL/Rasch 点估计，五板块算术等权。
2. 匿名学习 item discrimination 的连续 2PL 点估计，五板块算术等权；所有残差等权，统一 slope ridge 只用于稳定 item 参数。
3. benchmark 内经验百分位，板块内等权均值，再对五板块等权。
4. benchmark 内经验百分位，板块内稳健中位数，再对五板块等权。
5. 跨板块去重后的 canonical family 全局等权百分位，检查板块复用造成的隐式重权。
6. `variantGroup >= 3` 的稀疏 item Rasch 敏感性，只作补充观察。
7. `variantGroup >= 20` 且 creator >= 3 的保守 Rasch 敏感性。

主口径不调用旧版 `coverage_adjusted_scores`，也不使用 SE、shortfall、pseudo-count、先验均值或 LCB 改写分数。等板块 2PL 进入 `rank_mean` 的 70%，稀疏项 Rasch 进入 30%；Core Rasch 与密集项 Rasch 作为敏感性对照。固定 exact config 对照、方法相关性、Top 50 重合和关键模型共同 benchmark 明细均单独输出。

当前主共识榜与七种方法对照均通过发布层硬校验：Fable 5 为第 1、5.6 Sol 为第 2。这里的前两位是明确的产品发布顺序，不伪装成统计估计；CSV 同时保留 `score`、`evidence_rank`、`rank_mean` 和 `rank_change_due_to_required_order`。原始证据排序继续输出，用于审计方法与数据覆盖。

## 证据审计：纯证据 2PL（非对外候选榜）

对需要复核“只看真实成绩”的计算过程，可运行 `evidence_only_ranking_analysis.py`。它是审计层，不满足发布前两位规则，因此不作为对外候选榜。该版本：

- 不读取 Fable、Qwen、Gemini 或其他产品顺序规则，不固定任何模型名次。
- 不使用固定缺项扣分；每板块至少 2 个可比 benchmark family 才入榜，每板块至少 3 项仅决定 `Main / Provisional` 标签。
- 排名使用带 ridge 正则的连续 2PL 点估计（MAP-like，不是贝叶斯后验均值）；LCB 敏感性先在每个板块计算 `theta - 0.67 × SE`，再经 CDF 与五板块聚合，另报敏感性分数和名次但不改变主榜。
- 排除跨 effort/变体复制的 `sharedFromVariant` 成绩、站点拟合的 LiveCodeBench 回填，以及 effort 或 fallback 无法映射到单一模型配置的厂商成绩。
- Terminal-Bench 2.1、HLE、GPQA、AIME、MMMU-Pro、IFBench 对所有模型统一使用 Artificial Analysis 协议，不逐模型择高混用不同 harness。

当前官方数据快照下，Claude Opus 5 (max) 为第 1（Provisional，五板块覆盖 `5 / 5 / 3 / 5 / 2`），Qwen3.8 Max 为第 10（Main，`3 / 7 / 3 / 5 / 3`）。这是证据自然产生的结果，不是名次规则。

## 重要边界

源数据只有模型在整项 benchmark 上的聚合分数，没有题目级 0/1 作答。因此这里的 Rasch 和 2PL 是 **benchmark-as-item continuous IRT / IRT-inspired**，不是经典题目级 IRT。它适合做方法探索和影子榜，不应把当前参数解释为正式量表中的题目难度或模型绝对能力。

同一 benchmark family 在同一板块内的同义来源会合并，例如 HLE、GPQA Diamond 和 AIME 2025 的常规列与外部列只占一个覆盖槽位。同一 benchmark 仍可能跨板块出现，这是现有能力分类法的延续，也意味着板块间存在局部相关性。

## 历史五套实验（非生产）

以下内容解释早期覆盖校正与板块权重实验，只为复现实验文件；它们不参与当前站点主榜，也不是推荐方法。

### 1. 现行 AIndex（基准）

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

## 数据与覆盖规则

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
```

脚本只依赖 Python 标准库和 NumPy，不访问网络。Notebook 是相同分析的可执行伴随文件：

```text
analysis/irt_leaderboard_exploration/irt_leaderboard_exploration.ipynb
```

## 输出

- `outputs/full_rankings_twopl_sparse_70_30_rank_mean.csv`：2PL 70% / 稀疏 Rasch 30% 加权证据名次的全榜。
- `outputs/top50_twopl_sparse_70_30_rank_mean.csv`：未锚定共识 Top 50 审计文件。
- `outputs/full_rankings_required_twopl_sparse_70_30_rank_mean.csv`：应用透明发布层后的主榜全量结果。
- `outputs/top50_required_twopl_sparse_70_30_rank_mean.csv`：站点主口径 Top 50。
- `outputs/consensus_publication_validation_summary.json`：加权公式、前两位发布层和其余相对顺序的校验。

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
- `outputs/constrained_validation_summary.json`：Fable、Qwen、Gemini Flash、Top 50 行数等验收结果。
- `outputs/constraint_sensitivity.csv`：Gemini Flash 开源下限 5 / 10 / 15 的敏感性结果。
- `outputs/external_source_assessment.csv`：外部权威来源的接口、时效、许可与模型映射风险审计。
- `report/constrained_leaderboard_exploration.html`：历史产品约束版报告，仅作产品规则对照，不再作为纯证据榜入口。
- `outputs/evidence_only_top50.csv`：纯证据 2PL Top 50 审计文件，不作为发布候选榜。
- `outputs/evidence_only_full_rankings.csv`：纯证据版全部合格 variant group。
- `outputs/evidence_only_validation_summary.json`：纯证据口径、清洗计数、目标模型覆盖和不确定性摘要。
- `outputs/required_order_multi_method_top50.csv`：当前推荐的七法发布 Top 50 合表，共 350 行；每法均为 Fable #1、Sol #2。
- `outputs/top50_required_<method>.csv`：每种方法通过前两位硬门槛后的独立 Top 50。
- `outputs/required_order_multi_method_full_rankings.csv`：七法发布层的全部合格 variant group，保留 `evidence_rank` 与规则位移。
- `outputs/required_order_validation_summary.json`：逐方法验证 50 行、Fable #1、Sol #2、分数不变和其余相对顺序不变。
- `outputs/multi_method_top50.csv`：七法原始证据 Top 50 审计合表，不作为发布候选榜。
- `outputs/top50_<method>.csv`：每种无模型修正方法的原始证据 Top 50 审计文件。
- `outputs/multi_method_full_rankings.csv`：七法原始证据层的全部合格 variant group。
- `outputs/multi_method_validation_summary.json`：方法、门槛、清洗计数与目标模型名次。
- `outputs/target_exact_config_comparison.csv`：固定 exact config 的跨方法对照，避免不同方案切换 effort。
- `outputs/target_source_coverage_audit.csv`：官方直接成绩进入/未进入共同协议的数量。
- `outputs/key_pair_overlap_audit.csv`：Sol/Opus、Luna/DeepSeek 的共同原始 benchmark 明细。
- `outputs/method_stability.csv`：方法两两 Spearman 与 Top 50 重合。

## 外部来源与每日 Action

每日 Action 已经运行 `benchmarks/collect_benchmark_scores.py`；Qwen3.8-Max、GPT-5.6、Claude Opus 5 与 Fable 5 System Card 已纳入同一来源库。Qwen 使用官方 article-retrieval JSON API 获取文章表格，并对 `Pass / Score`、`without / with Code Interpreter`、`binary / partial` 等复合单元格做显式语义选值；当前 27 项在线解析值与审计 seed 全部一致。GPT-5.6 三个型号各 37 条官方成绩只挂到 `max`，标记 `configurationConfidence=inferred`，禁止向其他 effort 广播。Fable 新闻图的 15 条 higher-of-two 结果保留在来源库但不参与模型计分；榜单改用 System Card 的 14 条分列 Fable 产品配置成绩，其中 Terminal-Bench 明示 20.9% fallback。Anthropic 暂未发现同等方便、稳定的结构化成绩接口，图片/PDF 表无法可靠解析时继续使用已审计的官方 seed。

## 生产化前仍需完成

1. 继续扩充来源优先级和变体元数据测试；当前已实现模型第一方来源优先，并修复 Fable comparator 覆盖第一方成绩的问题。
2. 做测量方法 × 板块权重 × 合成函数的正交实验，避免一次同时改变多个因素。
3. 对硬门槛、软目标、LCB 系数和短缺惩罚做敏感性分析。
4. 用多个数据刷新周期做影子运行，并版本化校准参数与榜单快照。
5. 若要称为正式 IRT，补齐题目级响应或至少更细粒度、可链接的评测样本。
