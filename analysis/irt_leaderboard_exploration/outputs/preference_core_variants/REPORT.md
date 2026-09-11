# 按指定排序偏好筛选的 Core 候选

本轮偏好：Fable 5.1 第一、GPT-6 Astra 第二；Kimi K3 高于 Gemini 3.8 Flash；GPT-5.5 高于 Muse Spark 1.3；Qwen3.8 Max 和 Qwen3.8 2.4T A95B 均高于 Flash-Next。
这些偏好用于筛选 Core／权重组合，不是对模型能力的独立验证。成绩统一按规则计算，未添加命名模型加减分或排序后挪位。正式 Scheme 18 和前轮 A–D 均不修改。
配置固定为每组 variantPriority 最高的一档：Fable 5.1 使用 max with fallback，Astra/Kimi/Muse 使用 max，Gemini 使用 high，GPT-5.5 使用 xhigh（不混用 Pro/Instant）。

## 本轮规则

Terminal 优先同配置 v4 实测；缺失则通过重叠样本换算 v2.1，再乘 0.95；再缺失才换算 Hard 后乘 0.90。实测 0 不回退。
Core 仍取几何平均，缺任意必测项不入榜；扩展使用原正残差加分和动态上限；新 Core 与所有 Terminal 版本不再重复获得扩展加分。
本轮将 CritPt 放回推理板块，且只在这一板块使用。Omniscience Accuracy 单独构成知识板块；HLE 不在这三版 Core 中。G 额外使用 SciCode，且只在编程板块使用。

| 板块 | E 权重小改 | F 广覆盖 | G 科学编程 |
|---|---|---|---|
| 编程 | Terminal-Bench effective · 10% | Terminal-Bench effective · 15% | Terminal-Bench effective, SciCode · 10% |
| Agent／工具工作 | AutomationBench-AA, τ³-Banking · 20% | τ³-Banking · 10% | AutomationBench-AA · 15% |
| 高难推理 | CritPt, GPQA Diamond · 25% | CritPt, GPQA Diamond · 25% | CritPt, GPQA Diamond · 30% |
| 知识／科学 | AA-Omniscience Accuracy · 25% | AA-Omniscience Accuracy · 25% | AA-Omniscience Accuracy · 25% |
| 指令／上下文 | AA-LCR v1.1 · 20% | AA-LCR v1.1 · 25% | AA-LCR v1.1 · 20% |

## 名次与分数

| 模型 | E 名次／分数 | F 名次／分数 | G 名次／分数 |
|---|---:|---:|---:|
| Claude Fable 5.1 (max with fallback) | 1 / 64.933 | 1 / 65.129 | 1 / 66.223 |
| GPT-6 Astra (max) | 2 / 62.147 | 2 / 62.623 | 2 / 64.393 |
| Kimi K3 (max) | 9 / 52.947 | 9 / 52.257 | 9 / 55.702 |
| Gemini 3.8 Flash (high) | 10 / 52.712 | 10 / 51.866 | 10 / 55.041 |
| GPT-5.5 (xhigh) | 7 / 54.002 | 7 / 54.261 | 7 / 56.907 |
| Muse Spark 1.3 (max) | 8 / 53.696 | 8 / 53.752 | 8 / 56.330 |
| Qwen3.8 Max | 15 / 49.174 | 14 / 49.238 | 14 / 52.060 |
| Qwen3.8 2.4T A95B | 21 / 46.404 | 28 / 45.283 | 20 / 48.992 |
| Qwen3.8-Flash-Next | 27 / 45.162 | 29 / 44.695 | 29 / 46.955 |

## 约束与敏感性

每条顺序还要求超过 0.05 分，防止依赖完全相等或显示舍入。

| 方案 | 入榜模型数 | 全部约束 | 最小分差 | 共同人群约束 | 权重微调通过数 |
|---|---:|---|---:|---|---|
| E 权重小改 | 109 | True | 0.236 | True | 19/20 |
| F 广覆盖 | 143 | True | 0.391 | True | 20/20 |
| G 科学编程 | 108 | True | 0.577 | True | 20/20 |

共同集合为 108 个固定配置，各方案在此集合重新拟合扩展加分。敏感性检查为在两个板块间转移 1 个百分点，共 20 种；固定成绩和校准，不代表未来数据刷新也保持排序。
最小分差较小时，原始成绩的更新就可能改变结果；本轮未做跨时间留出验证。

## 搜索范围与复现

检查 96 套 Core，权重每板 10%–40%、5 个百分点步长、总和 100%。对满足至少 100 个模型且九个指定模型均入榜的组合，共评估 79296 次，509 次通过当前偏好。
E/F/G 分别展示接近等权、覆盖更广、增加科学编程证据三种取舍；不是互相独立的验证集。完整通过列表在 search.json，输入哈希和校准在 run.json。
运行：`python -B analysis/irt_leaderboard_exploration/preference_core_variants.py`。各版全量排名见 rankings_*.csv；共同人群排名见 common_*.csv；未入榜及缺项见 excluded_*.csv。
