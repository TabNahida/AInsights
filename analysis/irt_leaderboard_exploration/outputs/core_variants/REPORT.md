# Core 候选方案实跑

这是可重跑的实验，生产榜仍为 Scheme 18。分数保留五板块各 20%、几何 Core 和正残差加分。
去重先固定每组 variantPriority 最高的配置，同优先级按 slug 排序；不按成绩选配置、不跨配置补值。
所有声明的 Core 必须完整。表中配置数和模型组数不同；至少 100 条不代表适合做 Core。

## 覆盖至少 100 个配置的全部测试

| 测试 | 配置数 | 模型组数 | 厂商数 | 说明 |
|---|---:|---:|---:|---|
| GPQA Diamond | 612 | 445 | 58 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| Humanity's Last Exam | 607 | 437 | 58 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| CritPt | 520 | 357 | 55 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| AA-Omniscience Accuracy | 519 | 354 | 55 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| AA-Omniscience Non-Hallucination Rate | 519 | 354 | 55 | 同一 Omniscience 家族的另一指标 |
| AA-LCR | 516 | 357 | 54 | 当前 AA-LCR v1.1 的兼容别名，不重复计权 |
| AA-LCR v1.1 | 516 | 357 | 54 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| IFBench | 450 | 321 | 49 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| τ²-Bench Telecom | 440 | 313 | 48 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| Terminal-Bench Hard | 432 | 305 | 48 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| LiveCodeBench | 343 | 269 | 40 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| AIME 2025 | 270 | 199 | 36 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| MMMU-Pro | 258 | 152 | 28 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| GDPval-AA | 239 | 174 | 40 | 历史留存列，不作为新 Core |
| GDPval-AA v2 | 239 | 174 | 40 | Elo 换算分，非原生通过率 |
| Terminal-Bench v2.1 | 236 | 176 | 40 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| τ³-Banking | 204 | 149 | 36 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| SciCode | 167 | 122 | 35 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| AA-Briefcase | 159 | 113 | 28 | Elo 换算分，非原生通过率 |
| AutomationBench-AA | 153 | 111 | 27 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| GDP.pdf | 147 | 110 | 26 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |
| Terminal-Bench v4.0 | 142 | 103 | 26 | 直接观测；外部项目仅计确切配置、非复制、非推算成绩 |

LiveCodeBench 使用 CSV 的直接成绩，剔除网站后来拟合补入的值。外部测试按确切配置证据统计，本次无外部测试达到 100 条。

## Core 方案

| 板块 | A 广覆盖 | B 工作流 | C 工作流＋文档 | D 版本换算 |
|---|---|---|---|---|
| 编程 | Terminal-Bench effective | Terminal-Bench effective | Terminal-Bench effective | Terminal-Bench effective |
| Agent／工具工作 | τ³-Banking | AutomationBench-AA | AutomationBench-AA | AutomationBench-AA |
| 高难推理 | Humanity's Last Exam, GPQA Diamond | Humanity's Last Exam, GPQA Diamond | Humanity's Last Exam, GPQA Diamond | Humanity's Last Exam, GPQA Diamond |
| 知识／科学 | GPQA Diamond, AA-Omniscience Accuracy | GPQA Diamond, AA-Omniscience Accuracy | GPQA Diamond, AA-Omniscience Accuracy | GPQA Diamond, AA-Omniscience Accuracy |
| 指令／上下文 | AA-LCR v1.1 | AA-LCR v1.1 | AA-LCR v1.1, GDP.pdf | AA-LCR v1.1 |

A/B/C：有 v4.0 就用 v4.0；否则 v2.1 × 0.95；再没有则 Hard × 0.90。扣的是比例，不是百分点。实测 0 分保留，不回退。
D：Core 与 B 完全相同；旧版通过去重重叠样本的非负斜率线性拟合换算到 v4 尺度，限制在 0–100 后再打相同折扣。此值是估算，不是 v4 实测。
扩展池沿用 Scheme 18，但移除已经成为 Core 的项目，以及所有 Terminal-Bench 版本，防止 Core 与加分重复计入。
GPQA 同时支持推理与知识两个板块；这一跨板块重复仍保留。新 Core 不再强制 SciCode/CritPt；IFBench 暂不强制，因为一些最新模型没有结果。
AA-Briefcase、GDPval 是 Elo 换算分，本轮不放入几何通过率 Core。

## 版本差异诊断

以下拟合每个模型组最多一条，取预先固定配置；误差为样本内描述，不是泛化验证。

| 旧版 | 重叠模型组 | 旧版中位数 | v4 中位数 | 配对分差中位数 | 九五／九折后仍高于实测 v4 | 换算 MAE |
|---|---:|---:|---:|---:|---:|---:|
| Terminal-Bench v2.1 | 102 | 52.62 | 0.51 | 46.25 | 98.0% | 6.06 |
| Terminal-Bench Hard | 65 | 27.27 | 0.00 | 26.01 | 98.5% | 3.94 |

轻折扣不能消除旧版较容易的影响；v4 实测低分的模型可能落后于只测旧版的模型。A/B/C 用来检验这一提议，D 提供粗略尺度修正对照。
不同方案的覆盖人群与加分校准都会变化；common_* 文件另外在完全相同的配置集合上分别重算，以减少人群差异。
共同集合：105 个模型组。

## 实跑结果

| 方案 | 入榜模型组 | 被排除模型组 | v4 实测 | v2.1 回退 | Hard 回退 | 每板加分上限 |
|---|---:|---:|---:|---:|---:|---:|
| A 广覆盖 | 143 | 328 | 101 | 41 | 1 | 29.585 |
| B 工作流 | 109 | 362 | 101 | 8 | 0 | 25.376 |
| C 工作流＋文档 | 105 | 366 | 98 | 7 | 0 | 24.812 |
| D 工作流＋版本换算 | 109 | 362 | 101 | 8 | 0 | 25.161 |

### A 广覆盖 · 前十

| 排名 | 模型 | AIndex 候选分 | Core 平均 | Terminal 来源 | 有效 Terminal 分 |
|---:|---|---:|---:|---|---:|
| 1 | Claude Fable 5.1 (max with fallback) | 71.306 | 67.681 | Terminal-Bench v4.0 | 52.020 |
| 2 | Claude Opus 5 (max) | 66.881 | 63.447 | Terminal-Bench v4.0 | 48.990 |
| 3 | Qwen3.8-Flash-Next | 66.860 | 62.738 | Terminal-Bench v2.1 | 81.835 |
| 4 | Claude Fable 5 (with fallback) | 66.830 | 62.476 | Terminal-Bench v4.0 | 42.424 |
| 5 | GPT-6 Astra (max) | 66.244 | 66.244 | Terminal-Bench v4.0 | 59.091 |
| 6 | GPT-5.4 (xhigh) | 65.560 | 65.560 | Terminal-Bench v2.1 | 74.363 |
| 7 | Claude Opus 4.7 (max) | 64.266 | 64.266 | Terminal-Bench v2.1 | 78.989 |
| 8 | GPT-5.6 Sol (max) | 62.253 | 62.253 | Terminal-Bench v4.0 | 39.899 |
| 9 | Kimi K2.6 | 60.020 | 55.973 | Terminal-Bench v2.1 | 62.622 |
| 10 | Muse Spark 1.3 (max) | 59.638 | 59.638 | Terminal-Bench v4.0 | 33.333 |

### B 工作流 · 前十

| 排名 | 模型 | AIndex 候选分 | Core 平均 | Terminal 来源 | 有效 Terminal 分 |
|---:|---|---:|---:|---|---:|
| 1 | Claude Fable 5.1 (max with fallback) | 74.151 | 70.113 | Terminal-Bench v4.0 | 52.020 |
| 2 | GPT-6 Astra (max) | 71.654 | 71.654 | Terminal-Bench v4.0 | 59.091 |
| 3 | Claude Opus 5 (max) | 69.858 | 66.350 | Terminal-Bench v4.0 | 48.990 |
| 4 | Claude Fable 5 (with fallback) | 69.847 | 65.662 | Terminal-Bench v4.0 | 42.424 |
| 5 | Qwen3.8-Flash-Next | 67.840 | 64.847 | Terminal-Bench v2.1 | 81.835 |
| 6 | GPT-5.6 Sol (max) | 65.590 | 65.403 | Terminal-Bench v4.0 | 39.899 |
| 7 | Muse Spark 1.3 (max) | 62.787 | 61.106 | Terminal-Bench v4.0 | 33.333 |
| 8 | GLM-5.3 (max) | 61.493 | 60.353 | Terminal-Bench v4.0 | 41.919 |
| 9 | GPT-5.6 Terra (max) | 61.364 | 61.364 | Terminal-Bench v4.0 | 35.353 |
| 10 | GLM-5.2 (max) | 61.066 | 57.618 | Terminal-Bench v2.1 | 74.007 |

### C 工作流＋文档 · 前十

| 排名 | 模型 | AIndex 候选分 | Core 平均 | Terminal 来源 | 有效 Terminal 分 |
|---:|---|---:|---:|---|---:|
| 1 | Claude Fable 5.1 (max with fallback) | 66.541 | 62.503 | Terminal-Bench v4.0 | 52.020 |
| 2 | GPT-6 Astra (max) | 65.522 | 65.522 | Terminal-Bench v4.0 | 59.091 |
| 3 | Claude Fable 5 (with fallback) | 62.271 | 58.086 | Terminal-Bench v4.0 | 42.424 |
| 4 | Claude Opus 5 (max) | 62.270 | 58.762 | Terminal-Bench v4.0 | 48.990 |
| 5 | Qwen3.8-Flash-Next | 58.874 | 55.964 | Terminal-Bench v2.1 | 81.835 |
| 6 | GPT-5.6 Sol (max) | 58.266 | 58.163 | Terminal-Bench v4.0 | 39.899 |
| 7 | Muse Spark 1.3 (max) | 55.504 | 53.903 | Terminal-Bench v4.0 | 33.333 |
| 8 | GPT-5.6 Terra (max) | 53.690 | 53.690 | Terminal-Bench v4.0 | 35.353 |
| 9 | Gemini 3.8 Flash (high) | 52.357 | 52.113 | Terminal-Bench v4.0 | 19.697 |
| 10 | Gemini 3.7 Flash (high) | 51.831 | 51.831 | Terminal-Bench v4.0 | 13.636 |

### D 工作流＋版本换算 · 前十

| 排名 | 模型 | AIndex 候选分 | Core 平均 | Terminal 来源 | 有效 Terminal 分 |
|---:|---|---:|---:|---|---:|
| 1 | Claude Fable 5.1 (max with fallback) | 72.734 | 70.113 | Terminal-Bench v4.0 | 52.020 |
| 2 | GPT-6 Astra (max) | 71.654 | 71.654 | Terminal-Bench v4.0 | 59.091 |
| 3 | Claude Fable 5 (with fallback) | 68.964 | 65.662 | Terminal-Bench v4.0 | 42.424 |
| 4 | Claude Opus 5 (max) | 68.609 | 66.350 | Terminal-Bench v4.0 | 48.990 |
| 5 | GPT-5.6 Sol (max) | 65.590 | 65.403 | Terminal-Bench v4.0 | 39.899 |
| 6 | Muse Spark 1.3 (max) | 62.787 | 61.106 | Terminal-Bench v4.0 | 33.333 |
| 7 | GLM-5.3 (max) | 61.493 | 60.353 | Terminal-Bench v4.0 | 41.919 |
| 8 | GPT-5.6 Terra (max) | 61.364 | 61.364 | Terminal-Bench v4.0 | 35.353 |
| 9 | Gemini 3.8 Flash (high) | 60.442 | 60.114 | Terminal-Bench v4.0 | 19.697 |
| 10 | Gemini 3.7 Flash (high) | 59.385 | 59.385 | Terminal-Bench v4.0 | 13.636 |

完整数据：coverage.csv、各方案 rankings_*.csv、excluded_*.csv、共同人群 common_*.csv，以及 comparison.csv。
参数、输入 SHA-256 和校准系数见 run.json。所有原始成绩文件保持不变。
