# 覆盖感知的 IRT 榜单探索

这是一套基于 `docs/data/models.json` 可复现的五板块榜单研究与生产流水线。生产 AIndex 现采用候选审核中的**方案 18**：`partial_credit_geometric` Core + `logsumexp_residual_t1` 独立扩展证据 + 动态 `mean + sqrt(2) * SD` cap。Coding、Agentic/tool work、Hard reasoning、Knowledge/science、Instruction/context 五板严格等权。

- **Core**：每板块必须完成其全部必做测试；在原始 0–100 分数上计算无权重几何均值。缺任一 Core 项则该配置不计 AIndex。
- **扩展证据**：只允许 benchmark 控制方不是被排名模型厂商的项目。每个扩展项在默认去重 cohort 上匿名拟合 Core 到扩展成绩的 OLS 趋势，斜率限制为非负，只保留高于预测的正残差。
- **Bonus**：板块内用零中性、单调的 `log(1 + sum(expm1(positive_residual)))` 累积正残差，再以全 cohort、跨板块 pooled 正残差的 `mean + sqrt(2) * population_SD` 动态封顶。
- **主分**：`board_score = min(100, core_score + capped_bonus)`；`final_score` 精确等于五个 `board_score / 5` 之和，也就是五板算术平均。
- **缺失规则**：扩展缺失保持 absent，不填 0、不填 50、不插入先验，也不扣 Core。低于预期的已观测扩展成绩只产生 0 bonus，不产生负分。
- **排序规则**：只按未舍入 `final_score` 降序，完全相同时才用稳定 ID；没有模型名、厂商、系列顺序、reserved rank 或事后换位。
- **敏感性**：等板块 2PL、Core/Sparse/Dense Rasch 与旧 mean-rank 结果只作对照，不参与方案 18 主分。
- **证据限制**：扩展 benchmark 的控制方独立，并不等于所有 result operator、agent scaffold、prompt、采样和版本完全一致；这些字段继续在来源政策和验证结果中披露。

`constrained_ranking_analysis.py` 是早期产品规则实验，仅保留作历史对照，不是当前推荐榜，也不应当用于证明模型强弱。

## 当前生产方法：AIndex 方案 18

五板必做 Core 为：

| 板块 | Core 测试 |
| --- | --- |
| Coding | SciCode |
| Agentic/tool work | AA-LCR |
| Hard reasoning | Humanity's Last Exam、CritPt、GPQA Diamond |
| Knowledge/science | SciCode、Humanity's Last Exam、GPQA Diamond、AA-Omniscience Accuracy |
| Instruction/context | CritPt、AA-LCR |

设板块 `b` 的必做成绩为 `x_bj`，已观测扩展成绩为 `y_bik`：

```text
core_b = 100 * exp(mean(log(clip(x_bj / 100, 1e-6, 1))))
predicted_bik = clip(alpha_bk + max(beta_bk, 0) * core_bi, 0, 100)
residual_bik = max(y_bik - predicted_bik, 0)
raw_bonus_b = log(1 + sum(expm1(residual_bik)))
cap = mean(all_positive_residuals) + sqrt(2) * population_sd(all_positive_residuals)
board_score_b = min(100, core_b + min(raw_bonus_b, cap))
final_score = sum(board_score_b / 5)
```

OLS 趋势与 cap 都从默认 `variantGroup` 去重 cohort 匿名估计，不包含具名模型参数。cap 随每日数据快照重算，所以文档不固定某个历史数值。生产验证器独立复算 Core、残差、bonus、cap、五板加总、排序和 benchmark policy，并检查 `docs/data/models.json` 中的站点字段与生产输出一致。

旧多方法分析仍并行保留作敏感性审计，包括：

1. 无观测权重的连续 1PL/Rasch 点估计，五板块算术等权。
2. 匿名学习 item discrimination 的连续 2PL 点估计，五板块算术等权；所有残差等权，统一 slope ridge 只用于稳定 item 参数。
3. benchmark 内经验百分位，板块内等权均值，再对五板块等权。
4. benchmark 内经验百分位，板块内稳健中位数，再对五板块等权。
5. 跨板块去重后的 canonical family 全局等权百分位，检查板块复用造成的隐式重权。
6. `variantGroup >= 3` 的稀疏 item Rasch 敏感性，只作补充观察。
7. `variantGroup >= 20` 且 creator >= 3 的保守 Rasch 敏感性。

这些旧方法不会与方案 18 做固定比例混合，也不会改变站点主分。它们用于观察 item discrimination、覆盖密度、稀疏信号和结果稳定性。

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

## 生产限制与后续工作

1. 扩展池中部分成绩仍混合 result operator、agent scaffold、prompt、采样或版本；benchmark 控制方独立并不消除这些协议差异。
2. Bonus 只增不减且由多项正残差累积，因此测试覆盖更广的模型拥有更多产生正信号的机会；动态 cap 和覆盖字段只能限制、不能完全消除这一机会差异。
3. Coding 与 Agentic/tool work 的 Core 当前各只有一项，其他板块分别为 3 / 4 / 2 项；新增 Core 必须先满足控制方、协议、覆盖和可自动更新要求，并做跨周期影子验证。
4. 同一 benchmark family 可能跨板复用，五板并非统计独立。新增或调整板块映射时必须检查隐式重复影响。
5. 方案 18 是 benchmark-as-item / partial-credit measurement，不是题目级经典 IRT。若要称为正式心理测量量表，仍需题目级响应和稳定的校准样本。
