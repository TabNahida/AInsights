const LANGUAGE_STORAGE_KEY = "ainsights-language";
const DEFAULT_LANGUAGE = "zh-CN";

const copy = {
  "zh-CN": {
    pageTitle: "AI Insights Analysis",
    loading: "加载中",
    source: "数据源",
    updatedAt: "更新于 {date}",
    unknownTime: "未知时间",
    languageLabel: "语言",
    pages: {
      home: "首页",
      ranking: "完整排名",
      compare: "模型对比",
      benchmarks: "测试项",
      sources: "数据源",
      contribute: "贡献",
    },
    back: "返回",
    backToRanking: "返回完整排名",
    modelNotFound: "没有找到这个模型",
    search: "搜索",
    searchPlaceholder: "模型或机构",
    dedupe: "去除重复档位",
    customTitle: "自定义计算实验室",
    customToolTitle: "计算工具",
    customToolSubtitle: "选择同量纲数据进行组合；方法名次、能力板块分和逐项 benchmark 不会混算。",
    customToolModes: {
      methodRank: "方法名次",
      boardScore: "能力板块",
      benchmarkLab: "逐项 Benchmark",
    },
    customToolDescriptions: {
      methodRank: "组合四种 IRT 方法的真实证据名次；默认采用等板块 2PL 70% 与稀疏 Rasch 30%。",
      boardScore: "组合五个能力板块的真实 IRT 分数；默认板块分由等板块 2PL 占 70%、稀疏 Rasch 占 30%。",
      benchmarkLab: "直接组合原始公开测试成绩，可继续控制归一化、缺失处理与覆盖门槛。",
    },
    customAggregatorTitle: "聚合器",
    customMethodAggregators: {
      mean: "加权平均名次",
      median: "加权中位名次",
      worst: "最弱方法名次",
    },
    customBoardAggregators: {
      arithmetic: "加权算术平均",
      geometric: "加权几何平均",
      weakest: "最弱板块",
    },
    customMethodWeightsTitle: "IRT 方法名次权重",
    customMethodWeightsSubtitle: "使用未经过发布层调整的 evidence rank；权重为 0 即不纳入。",
    customBoardWeightsTitle: "能力板块权重",
    customBoardWeightsSubtitle: "每个板块都来自真实测试成绩的 IRT 板块分，不做模型特定修正。",
    customWeightSum: "权重合计 {total}",
    customActions: {
      equalize: "等权",
      normalize: "归一到 100",
      clear: "清零",
      restore: "恢复默认",
      export: "导出配置",
      exported: "已导出 JSON",
    },
    customMethodNames: {
      rasch: "等板块 Rasch",
      sparseRasch: "稀疏项 Rasch",
      twopl: "等板块 2PL",
      denseRasch: "密集项 Rasch",
    },
    customBoardNames: {
      coding: "代码编程",
      agenticToolWork: "智能体与工具工作",
      hardReasoning: "高难推理",
      knowledgeScience: "知识与科学",
      instructionContext: "指令与上下文",
    },
    evidenceRankLabel: "证据名次",
    publicationLayerNote: "当 Fable 5 与 GPT-5.6 Sol 在当前 Custom 配置中均有真实可计算结果时，才独立套用 Fable 5 #1、GPT-5.6 Sol #2 的发布层；否则保留证据顺序，不补造缺失成绩。",
    metricWeightsTitle: "测试项数据权重",
    metricWeightsSubtitle: "直接参与当前自定义排名的逐项权重，按已有模型数据量排序",
    metricCoverage: "{count} 个模型",
    metricCoverageFilterLabel: "折叠低覆盖项目",
    metricCoverageFilterAll: "显示全部",
    metricCoverageFilterOption: "少于 {count} 个模型",
    metricCoverageFilterSummary: "已折叠 {hidden} 项，正在显示 {visible}/{total} 项",
    metricCoverageFilterEmpty: "没有达到该覆盖门槛的测试项",
    metricGroupMeta: "{count} 个模型 · {metrics} 个数据项",
    customWeightPresetTitle: "权重预设",
    customWeightPresetSubtitle: "从均衡 Benchmark Lab 或 AA 三个方向开始，再微调下方逐项测试权重；这些预设不改变 IRT 主榜。",
    customWeightPresetMeta: "{count} 项",
    missingModeTitle: "计算方式",
    missingModeSubtitle: "逐项 Benchmark Lab 可选择分数基线、均值方式和缺失处理策略；这些设置只影响自定义实验，不影响 IRT 主榜。",
    normalizationMethodTitle: "分数基线",
    normalizationMethodHint: "Benchmark Lab 的相对最高分模式先除以各测试项观察最高分，再按 AA Intelligence 最高分缩放展示；仅用于逐项实验。",
    normalizationMethods: {
      "relative-best": "最佳分数比例",
      raw: "原始分数",
    },
    calculationMethodTitle: "均值方式",
    calculationMethodHint: "逐项 Benchmark Lab 可比较几何加权均值与普通加权均值；IRT 主榜不使用这套逐项聚合。",
    meanMethods: {
      geometric: "几何加权均值",
      arithmetic: "普通加权均值",
    },
    missingPresetTitle: "处理预设",
    penaltyLabel: "缺失扣分强度",
    penaltyHint: "手动扣分模式使用该强度；0 表示只按可用项，100 表示缺失按 0 进入总权重。",
    minCoverageLabel: "最低覆盖率",
    minCoverageHint: "低于该覆盖率的模型不进入排名；100% 等同全覆盖",
    currentCustomStrategy: "当前策略",
    manualCustomStrategy: "手动配置",
    missingModes: {
      available: "可用项",
      coverage025: "覆盖折扣 0.25",
      coverageSqrt: "覆盖折扣 sqrt",
      weakPrior: "弱先验",
      penalty: "轻度扣分",
      zero: "缺失记 0",
      complete: "要求全覆盖",
    },
    sourceWeightStatuses: {
      active: "主数据源",
      mapped: "映射到现有子项",
      external: "外部分数源",
      reference: "参考源",
    },
    relatedMetrics: "{count} 个相关子项",
    detailSourceCoverage: "{available}/{total} 个相关子项有分数",
    sourcesBadge: "{count} 个数据源",
    sourcesPageTitle: "独立测评与参考源",
    sourcesPageSubtitle: "这里展示第三方或其他机构的测评源；厂商官方发布页和模型卡仅作为具体分数来源出现在模型/测试项详情里。",
    sourceMetricMapTitle: "数据源与测试项映射",
    sourceMetricMapSubtitle: "每个来源对应的 benchmark、覆盖模型数和在当前数据中的结果数量。",
    sourceStats: {
      metrics: "测试项",
      models: "模型覆盖",
      results: "分数记录",
    },
    contributePageTitle: "贡献工作台",
    contributePageSubtitle: "在这里整理新增模型、模型数据或测试项目，生成可提交到 GitHub 的 PR payload。",
    contributeModeLabel: "贡献类型",
    contributeModeModel: "新增模型",
    contributeModeScore: "补充模型数据",
    contributeModeBenchmark: "新增测试项目",
    contributeModelName: "模型名称",
    contributeCreator: "机构",
    contributeReleaseDate: "发布日期",
    contributeModelUrl: "模型链接",
    contributeOpenSource: "开放状态",
    contributeBenchmark: "测试项",
    contributeBenchmarkId: "测试项 ID",
    contributeBenchmarkName: "测试项名称",
    contributeBenchmarkCategory: "测试项分类",
    contributeBenchmarkUnit: "单位",
    contributeBenchmarkIcon: "短标签",
    contributeValue: "分数",
    contributeSourceUrl: "官方来源 URL",
    contributeSourceLabel: "来源名称",
    contributeNotes: "备注",
    contributePreviewTitle: "PR payload",
    contributePreviewEmpty: "填写左侧字段后会生成 payload。",
    contributeCopy: "复制 payload",
    contributeCopied: "已复制",
    contributeGithubPr: "登录 GitHub 提交 PR",
    contributeGithubDev: "打开 GitHub.dev",
    contributeEditBenchmarks: "编辑 benchmark 数据",
    contributeEditCollector: "编辑来源脚本",
    contributeEditAaCsv: "编辑 AA 模型 CSV",
    contributeRequired: "名称和官方来源 URL 是必填项。",
    contributeSelectBenchmark: "选择测试项",
    reset: "重置",
    empty: "没有符合条件的模型",
    loadFailed: "数据加载失败：{message}",
    unknownCreator: "Unknown",
    reasoning: "Reasoning",
    methodologyLink: "AInsights Index 计算方式",
    footerPrefix: "数据来源：",
    footerSuffix: "。AInsights Index 基于其公开评测数据重新计算。",
    repository: "仓库",
    rankingItems: "个排名项",
    scorableModels: "个可评分模型",
    removedPrefix: "已去除",
    removedSuffix: "个重复档位",
    allTiers: "显示全部档位",
    sourceFilter: "来源",
    top20Title: "AInsights Index Top {count}",
    top20Subtitle: "按等板块 2PL 70% 与稀疏 Rasch 30% 的加权证据名次排序；柱宽表示证据名次百分位",
    latestModelsTitle: "最新模型",
    latestModelsSubtitle: "按发布日期展示最近进入数据集的去重模型",
    fullRanking: "查看完整排名",
    costScatterTitle: "智能 vs 运行成本",
    costScatterSubtitle: "横轴为运行 AA Intelligence Index 的美元成本，使用对数刻度",
    scatterXAxis: "运行 Intelligence Index 的成本（USD，对数）",
    scatterYAxis: "证据名次百分位",
    attractiveQuadrant: "高分低成本区域",
    noCostData: "没有足够的成本数据可绘制散点图",
    scoreBandsTitle: "证据名次百分位分布",
    scoreBandsSubtitle: "去重模型在平均证据名次百分位上的集中区间",
    providerChartTitle: "机构覆盖",
    providerChartSubtitle: "按可评分去重模型数量和最高分展示",
    providerModelCount: "模型数量",
    providerBestScore: "最佳平均名次",
    providerPageTitle: "{provider} 模型概览",
    providerPageSubtitle: "{count} 个主榜去重模型 · 最佳平均名次 {bestScore}",
    providerNotFound: "没有找到这个机构",
    providerSummaryModels: "可评分模型",
    providerSummaryBest: "最佳平均名次",
    providerSummaryAverage: "平均证据名次均值",
    providerSummaryOpen: "开源模型",
    providerModelsTitle: "模型列表",
    providerModelsSubtitle: "按主榜发布名次排序，展示平均证据名次、发布日期、来源类型和运行指标",
    comparePageTitle: "模型对比",
    comparePageSubtitle: "选择多个模型，横向查看分数、排名、成本、速度、上下文和各项测试数据",
    comparePickerTitle: "选择模型",
    compareModelSelectLabel: "模型",
    compareSearchPlaceholder: "搜索模型或供应商",
    compareSearchEmpty: "没有匹配的可添加模型",
    compareAdd: "添加",
    compareClear: "清空",
    compareEntry: "对比",
    modelDetails: "详情",
    compareSelectedTitle: "已选模型",
    compareEmpty: "请选择至少一个模型",
    compareCoreTitle: "核心数据",
    compareRadarTitle: "能力雷达对比",
    compareRadarSubtitle: "叠加对比五个 IRT 能力板块与证据覆盖度；证据轴不参与排名",
    compareBenchmarkTitle: "测试项数据",
    compareMetricColumn: "指标",
    compareRemove: "移除",
    compareRows: {
      provider: "供应商",
      score: "平均证据名次",
      rank: "排名",
      source: "来源",
      releaseDate: "发布日期",
      speed: "输出速度",
      context: "上下文",
      inputModality: "输入模态",
      outputModality: "输出模态",
      inputPrice: "输入价格",
      outputPrice: "输出价格",
      runCost: "AA 运行成本",
      coverage: "覆盖率",
    },
    sourceExplorerTitle: "测评源地图",
    sourceExplorerSubtitle: "AA 主数据之外的常用公开测评，用来交叉理解模型强弱项",
    detailRankTitle: "排名快照",
    detailRadarSubtitle: "五个 IRT 能力板块加证据覆盖度；外圈为 100 分，橙色为入榜模型平均值",
    detailBenchmarkTitle: "Benchmark Lab 参考项目",
    detailBenchmarkSubtitle: "均衡逐项实验模板中的测试项；它们不作为主榜固定权重。",
    detailExternalTitle: "非参考项目分数",
    detailExternalSubtitle: "均衡 Benchmark Lab 参考集之外的 AA 子项、官方发布页或其他公开测评；它们不进入默认 IRT 排名",
    detailCostTitle: "Detail",
    detailVariantsTitle: "同模型档位",
    detailSourcesTitle: "外部测评参考",
    radarAverage: "入榜模型平均值",
    radarDataSource: "数据来源",
    radarSourceText: "AInsights IRT 排行榜 / 真实 benchmark 成绩",
    radarBasisTitle: "雷达维度口径",
    radarBasisSubtitle: "五个能力轴直接读取排行榜的 IRT 板块分；证据覆盖轴只反映测试广度，不修正能力分，也不参与排名。",
    radarCoverage: "{available}/{total} 项测试",
    radarTestCount: "{available} 项测试",
    radarDualCoverage: "Core {coreAvailable}/{coreTotal} · Sparse {sparseAvailable}/{sparseTotal}",
    radarNoData: "该配置暂无完整的排行榜能力数据",
    radarAxes: {
      coding: "代码编程",
      agenticToolWork: "智能体与工具工作",
      hardReasoning: "高难推理",
      knowledgeScience: "知识与科学",
      instructionContext: "指令与上下文",
      evidenceCoverage: "证据覆盖度",
    },
    radarAxisNotes: {
      coding: "coding_score：软件工程、代码生成与执行能力。",
      agenticToolWork: "agentic-tool-work_score：工具、浏览器、终端与工作流执行能力。",
      hardReasoning: "hard-reasoning_score：高难数学、科学与复合推理能力。",
      knowledgeScience: "knowledge-science_score：知识与科学问题表现。",
      instructionContext: "instruction-context_score：指令遵循与长上下文稳定性。",
      evidenceCoverage: "evidenceCoverageScore：五板块测试覆盖广度，仅作证据充分度参考。",
    },
    detailRows: {
      provider: "供应商",
      inputTypes: "输入模态",
      outputTypes: "输出模态",
      parameters: "参数规模",
      activeParameters: "激活参数",
      reasoningModes: "推理模式",
      architecture: "架构",
      apiAccess: "访问方式",
      license: "许可",
      contextNote: "上下文说明",
      scoreRank: "当前排名",
      speedRank: "速度排名",
      contextRank: "上下文排名",
      inputRank: "输入价排名",
      outputRank: "输出价排名",
      cacheRank: "缓存价排名",
      runCostRank: "运行成本排名",
      lowerBetter: "越低越好",
      higherBetter: "越高越好",
      supported: "支持",
    },
    releaseDate: "发布日期",
    currentPreset: "当前预设",
    noBenchmarks: "没有可展示的子项得分",
    benchmarkPageTitle: "单项测试排名",
    benchmarkPageSubtitle: "查看每一项测试下所有有分数模型的具体排名和来源",
    benchmarkPickerTitle: "选择测试项",
    benchmarkRankingTitle: "{label} 排名",
    benchmarkRankingSubtitle: "{count} 个模型有分数 · {category}",
    benchmarkReference: "AInsights 参考项",
    benchmarkNonReference: "非参考项",
    benchmarkSourcesOnly: "来源",
    notAvailable: "暂无",
    homeStats: {
      leader: "领先模型",
      topOpen: "开源领先",
      bestValue: "高分低成本",
      modelCount: "去重模型",
      byScore: "按平均证据名次",
      perRun: "运行成本",
      source: "来源",
    },
    headers: {
      model: "模型",
      score: "综合分",
      rankMean: "平均证据名次",
      twoplRank: "2PL 名次",
      denseRaschRank: "密集 Rasch 名次",
      speed: "速度",
      context: "上下文",
      price: "价格",
      source: "来源",
      coverage: "覆盖",
    },
    table: {
      input: "入",
      output: "出",
      cache: "缓存",
      perMillion: "/ 1M",
      tokensPerSecond: "tok/s",
      tokens: "tokens",
    },
    languages: {
      "zh-CN": "中",
      "en-US": "EN",
    },
    views: {
      histogram: "直方图",
      table: "表格",
      text: "纯文本",
    },
    sourceFilters: {
      all: "全部",
      open: "开源",
      closed: "闭源",
      unknown: "未知",
    },
    sourceTypes: {
      open: "开源权重",
      closed: "闭源",
      unknown: "未知来源",
    },
    presets: {
      "zhihu-adjusted": {
        label: "AInsights Index",
        calculation: "rank-mean",
        normalization: "none",
        description: "主榜取等板块 2PL 真实证据名次的 70% 与稀疏项 Rasch 证据名次的 30% 加权平均；同分时依次比较 2PL 名次、稀疏 Rasch 名次和稳定 ID。Fable 5 #1、GPT-5.6 Sol #2 由独立发布层执行，不修改真实成绩。",
      },
      "aa-intelligence": {
        label: "AA Intelligence",
        description: "Artificial Analysis 官方 Intelligence Index。",
      },
      "aa-coding": {
        label: "AA Coding",
        description: "Artificial Analysis 官方 Coding Index。",
      },
      "aa-agentic": {
        label: "AA Agentic",
        description: "Artificial Analysis 官方 Agentic Index。",
      },
      custom: {
        label: "自定义工具",
        calculation: "multi-tool",
        normalization: "mode-specific",
        description: "分别组合四种 IRT 方法名次、五个 IRT 能力板块，或逐项公开 benchmark；不同量纲不会混算。",
      },
      "benchmark-lab": {
        label: "均衡 Benchmark Lab",
        description: "逐项测试实验室的均衡起点；只用于自定义探索，不是主榜固定权重。",
      },
    },
  },
  "en-US": {
    pageTitle: "AI Insights Analysis",
    loading: "Loading",
    source: "Source",
    updatedAt: "Updated {date}",
    unknownTime: "unknown time",
    languageLabel: "Language",
    pages: {
      home: "Home",
      ranking: "Full ranking",
      compare: "Compare",
      benchmarks: "Benchmarks",
      sources: "Sources",
      contribute: "Contribute",
    },
    back: "Back",
    backToRanking: "Back to full ranking",
    modelNotFound: "Model not found",
    search: "Search",
    searchPlaceholder: "Model or lab",
    dedupe: "Remove duplicate tiers",
    customTitle: "Custom calculation lab",
    customToolTitle: "Calculation tool",
    customToolSubtitle: "Combine like-for-like evidence; method ranks, capability-board scores, and benchmark scores are never mixed in one calculation.",
    customToolModes: {
      methodRank: "Method ranks",
      boardScore: "Capability boards",
      benchmarkLab: "Benchmark lab",
    },
    customToolDescriptions: {
      methodRank: "Combine observed evidence ranks from four IRT methods; the default is 70% Equal-board 2PL and 30% Sparse Rasch.",
      boardScore: "Combine five observed IRT capability scores; each default board is 70% Equal-board 2PL and 30% Sparse Rasch.",
      benchmarkLab: "Combine raw public benchmark results with optional normalization, missing-data handling, and coverage gates.",
    },
    customAggregatorTitle: "Aggregator",
    customMethodAggregators: {
      mean: "Weighted mean rank",
      median: "Weighted median rank",
      worst: "Worst method rank",
    },
    customBoardAggregators: {
      arithmetic: "Weighted arithmetic mean",
      geometric: "Weighted geometric mean",
      weakest: "Weakest board",
    },
    customMethodWeightsTitle: "IRT method-rank weights",
    customMethodWeightsSubtitle: "Uses evidence ranks before the publication layer; a zero weight excludes the method.",
    customBoardWeightsTitle: "Capability-board weights",
    customBoardWeightsSubtitle: "Every board is an IRT score based on observed benchmark results, without model-specific score correction.",
    customWeightSum: "Weight total {total}",
    customActions: {
      equalize: "Equalize",
      normalize: "Normalize to 100",
      clear: "Clear",
      restore: "Restore defaults",
      export: "Export config",
      exported: "JSON exported",
    },
    customMethodNames: {
      rasch: "Core Rasch",
      sparseRasch: "Sparse-item Rasch",
      twopl: "Equal-board 2PL",
      denseRasch: "Dense-item Rasch",
    },
    customBoardNames: {
      coding: "Coding",
      agenticToolWork: "Agentic & tool work",
      hardReasoning: "Hard reasoning",
      knowledgeScience: "Knowledge & science",
      instructionContext: "Instruction & context",
    },
    evidenceRankLabel: "Evidence rank",
    publicationLayerNote: "The separate Fable 5 #1 / GPT-5.6 Sol #2 publication layer applies only when both models have observed, calculable results in the current Custom configuration; otherwise the evidence order is preserved and no missing score is invented.",
    metricWeightsTitle: "Evaluation data weights",
    metricWeightsSubtitle: "Fine-grained weights used directly by the custom ranking, sorted by model coverage",
    metricCoverage: "{count} models",
    metricCoverageFilterLabel: "Collapse low-coverage fields",
    metricCoverageFilterAll: "Show all fields",
    metricCoverageFilterOption: "Fewer than {count} models",
    metricCoverageFilterSummary: "{hidden} fields collapsed · showing {visible}/{total}",
    metricCoverageFilterEmpty: "No fields meet this coverage threshold",
    metricGroupMeta: "{count} models · {metrics} data fields",
    customWeightPresetTitle: "Weight presets",
    customWeightPresetSubtitle: "Start from the Balanced Benchmark Lab or one of three AA directions, then tune per-benchmark weights; these presets do not change the IRT primary ranking.",
    customWeightPresetMeta: "{count} fields",
    missingModeTitle: "Calculation",
    missingModeSubtitle: "The per-benchmark lab can vary score basis, mean method, and missing-value policy; these settings affect custom experiments only, not the IRT primary ranking.",
    normalizationMethodTitle: "Score basis",
    normalizationMethodHint: "Benchmark Lab's best-score mode divides each benchmark by its observed maximum, then scales display values by the highest AA Intelligence score; this is only a per-item experiment.",
    normalizationMethods: {
      "relative-best": "Best score ratio",
      raw: "Raw score",
    },
    calculationMethodTitle: "Mean method",
    calculationMethodHint: "The per-benchmark lab can compare geometric and arithmetic weighted means; the IRT primary ranking does not use this per-item aggregation.",
    meanMethods: {
      geometric: "Geometric Weight Mean",
      arithmetic: "Weight Mean",
    },
    missingPresetTitle: "Treatment presets",
    penaltyLabel: "Missing penalty strength",
    penaltyHint: "0 averages available scores only; 100 counts missing fields as 0 in the selected total weight.",
    minCoverageLabel: "Minimum coverage",
    minCoverageHint: "Models below this coverage are excluded; 100% equals full coverage",
    currentCustomStrategy: "Current strategy",
    manualCustomStrategy: "Manual",
    missingModes: {
      available: "Available only",
      coverage025: "Coverage discount 0.25",
      coverageSqrt: "Coverage discount sqrt",
      weakPrior: "Weak prior",
      penalty: "Light penalty",
      zero: "Missing = 0",
      complete: "Full coverage",
    },
    sourceWeightStatuses: {
      active: "Primary source",
      mapped: "Mapped to available metrics",
      external: "External score source",
      reference: "Reference source",
    },
    relatedMetrics: "{count} related metrics",
    detailSourceCoverage: "{available}/{total} related metrics scored",
    sourcesBadge: "{count} sources",
    sourcesPageTitle: "Independent evaluation sources",
    sourcesPageSubtitle: "This page shows third-party or cross-lab evaluation sources. Vendor launch pages and model cards appear only as score sources inside model and benchmark details.",
    sourceMetricMapTitle: "Source-to-benchmark map",
    sourceMetricMapSubtitle: "Benchmarks, model coverage, and score records represented by each source.",
    sourceStats: {
      metrics: "Benchmarks",
      models: "Model coverage",
      results: "Score records",
    },
    contributePageTitle: "Contribution workbench",
    contributePageSubtitle: "Draft a new model, model data update, or benchmark and generate a GitHub-ready PR payload.",
    contributeModeLabel: "Contribution type",
    contributeModeModel: "New model",
    contributeModeScore: "Model data",
    contributeModeBenchmark: "New benchmark",
    contributeModelName: "Model name",
    contributeCreator: "Provider",
    contributeReleaseDate: "Release date",
    contributeModelUrl: "Model URL",
    contributeOpenSource: "Open status",
    contributeBenchmark: "Benchmark",
    contributeBenchmarkId: "Benchmark ID",
    contributeBenchmarkName: "Benchmark name",
    contributeBenchmarkCategory: "Benchmark category",
    contributeBenchmarkUnit: "Unit",
    contributeBenchmarkIcon: "Short label",
    contributeValue: "Score",
    contributeSourceUrl: "Official source URL",
    contributeSourceLabel: "Source label",
    contributeNotes: "Notes",
    contributePreviewTitle: "PR payload",
    contributePreviewEmpty: "Fill in the fields to generate a payload.",
    contributeCopy: "Copy payload",
    contributeCopied: "Copied",
    contributeGithubPr: "Log in to GitHub and PR",
    contributeGithubDev: "Open GitHub.dev",
    contributeEditBenchmarks: "Edit benchmark data",
    contributeEditCollector: "Edit source collector",
    contributeEditAaCsv: "Edit AA model CSV",
    contributeRequired: "Name and official source URL are required.",
    contributeSelectBenchmark: "Choose benchmark",
    reset: "Reset",
    empty: "No models match the current filters",
    loadFailed: "Failed to load data: {message}",
    unknownCreator: "Unknown",
    reasoning: "Reasoning",
    methodologyLink: "AInsights Index methodology",
    footerPrefix: "Source: ",
    footerSuffix: ". AInsights Index recalculates the public benchmark data.",
    repository: "Repository",
    rankingItems: "ranked items",
    scorableModels: "scorable models",
    removedPrefix: "Removed",
    removedSuffix: "duplicate tiers",
    allTiers: "Showing every tier",
    sourceFilter: "Source",
    top20Title: "AInsights Index Top {count}",
    top20Subtitle: "Ranked by a 70% Equal-board 2PL / 30% Sparse Rasch evidence-rank blend; bar width is evidence-rank percentile",
    latestModelsTitle: "Latest models",
    latestModelsSubtitle: "Recently released deduplicated models in the dataset",
    fullRanking: "View full ranking",
    costScatterTitle: "Intelligence vs. Cost to Run",
    costScatterSubtitle: "X-axis is the USD cost to run AA Intelligence Index, shown on a log scale",
    scatterXAxis: "Cost to Run Intelligence Index (USD, Log Scale)",
    scatterYAxis: "Evidence-rank percentile",
    attractiveQuadrant: "High-score low-cost region",
    noCostData: "Not enough cost data to draw the scatter chart",
    scoreBandsTitle: "Evidence-rank percentile distribution",
    scoreBandsSubtitle: "Where deduplicated models cluster by mean evidence-rank percentile",
    providerChartTitle: "Provider coverage",
    providerChartSubtitle: "Scorable deduped model count and best score by lab",
    providerModelCount: "Model count",
    providerBestScore: "Best mean rank",
    providerPageTitle: "{provider} model overview",
    providerPageSubtitle: "{count} deduplicated ranking models · best mean rank {bestScore}",
    providerNotFound: "Provider not found",
    providerSummaryModels: "Scorable models",
    providerSummaryBest: "Best mean rank",
    providerSummaryAverage: "Average mean evidence rank",
    providerSummaryOpen: "Open models",
    providerModelsTitle: "Model list",
    providerModelsSubtitle: "Sorted by publication rank with mean evidence rank, release date, source type, and operating metrics",
    comparePageTitle: "Model comparison",
    comparePageSubtitle: "Choose models and compare scores, ranks, cost, speed, context, and benchmark data side by side",
    comparePickerTitle: "Choose models",
    compareModelSelectLabel: "Model",
    compareSearchPlaceholder: "Search model or provider",
    compareSearchEmpty: "No matching models available to add",
    compareAdd: "Add",
    compareClear: "Clear",
    compareEntry: "Compare",
    modelDetails: "Details",
    compareSelectedTitle: "Selected models",
    compareEmpty: "Choose at least one model",
    compareCoreTitle: "Core data",
    compareRadarTitle: "Capability radar",
    compareRadarSubtitle: "Five IRT capability boards plus evidence coverage; the evidence axis does not affect rank",
    compareBenchmarkTitle: "Benchmark data",
    compareMetricColumn: "Metric",
    compareRemove: "Remove",
    compareRows: {
      provider: "Provider",
      score: "Mean evidence rank",
      rank: "Rank",
      source: "Source",
      releaseDate: "Release date",
      speed: "Output speed",
      context: "Context",
      inputModality: "Input modality",
      outputModality: "Output modality",
      inputPrice: "Input price",
      outputPrice: "Output price",
      runCost: "AA run cost",
      coverage: "Coverage",
    },
    sourceExplorerTitle: "Benchmark source map",
    sourceExplorerSubtitle: "Public evaluation sources to cross-check model strengths beyond AA",
    detailRankTitle: "Rank snapshot",
    detailRadarSubtitle: "Five IRT capability boards plus evidence coverage; the outer ring is 100 and orange is the ranked-model average",
    detailBenchmarkTitle: "Benchmark Lab reference set",
    detailBenchmarkSubtitle: "Benchmarks in the balanced per-item experiment template; these are not fixed primary-ranking weights.",
    detailExternalTitle: "Non-reference benchmark scores",
    detailExternalSubtitle: "AA submetrics, official release scores, and public evals outside the Balanced Benchmark Lab reference set; they do not enter the default IRT ranking",
    detailCostTitle: "Detail",
    detailVariantsTitle: "Same-model tiers",
    detailSourcesTitle: "External evaluation references",
    radarAverage: "Ranked-model average",
    radarDataSource: "Sources",
    radarSourceText: "AInsights IRT ranking / observed benchmark results",
    radarBasisTitle: "Radar axis basis",
    radarBasisSubtitle: "The five capability axes read the ranking's IRT board scores directly. Evidence coverage only shows test breadth; it neither adjusts capability scores nor affects rank.",
    radarCoverage: "{available}/{total} tests",
    radarTestCount: "{available} tests",
    radarDualCoverage: "Core {coreAvailable}/{coreTotal} · Sparse {sparseAvailable}/{sparseTotal}",
    radarNoData: "No complete ranking capability profile is available for this configuration",
    radarAxes: {
      coding: "Coding",
      agenticToolWork: "Agentic/tool work",
      hardReasoning: "Hard reasoning",
      knowledgeScience: "Knowledge/science",
      instructionContext: "Instruction/context",
      evidenceCoverage: "Evidence coverage",
    },
    radarAxisNotes: {
      coding: "coding_score: software engineering, code generation, and execution.",
      agenticToolWork: "agentic-tool-work_score: tool, browser, terminal, and workflow execution.",
      hardReasoning: "hard-reasoning_score: difficult mathematical, scientific, and compound reasoning.",
      knowledgeScience: "knowledge-science_score: performance on knowledge and science tasks.",
      instructionContext: "instruction-context_score: instruction following and long-context stability.",
      evidenceCoverage: "evidenceCoverageScore: test breadth across the five boards, shown only as evidence sufficiency.",
    },
    detailRows: {
      provider: "Provider",
      inputTypes: "Input modality",
      outputTypes: "Output modality",
      parameters: "Parameters",
      activeParameters: "Active parameters",
      reasoningModes: "Reasoning modes",
      architecture: "Architecture",
      apiAccess: "Access",
      license: "License",
      contextNote: "Context note",
      scoreRank: "Current rank",
      speedRank: "Speed rank",
      contextRank: "Context rank",
      inputRank: "Input price rank",
      outputRank: "Output price rank",
      cacheRank: "Cache price rank",
      runCostRank: "Run-cost rank",
      lowerBetter: "lower is better",
      higherBetter: "higher is better",
      supported: "supported",
    },
    releaseDate: "Release date",
    currentPreset: "Current preset",
    noBenchmarks: "No component scores to display",
    benchmarkPageTitle: "Benchmark rankings",
    benchmarkPageSubtitle: "Inspect model rankings and source-backed scores for each benchmark",
    benchmarkPickerTitle: "Choose benchmark",
    benchmarkRankingTitle: "{label} ranking",
    benchmarkRankingSubtitle: "{count} scored models · {category}",
    benchmarkReference: "AInsights reference",
    benchmarkNonReference: "Non-reference",
    benchmarkSourcesOnly: "Sources",
    notAvailable: "N/A",
    homeStats: {
      leader: "Leader",
      topOpen: "Top open",
      bestValue: "High-score low-cost",
      modelCount: "Deduplicated models",
      byScore: "By mean evidence rank",
      perRun: "run cost",
      source: "Source",
    },
    headers: {
      model: "Model",
      score: "Score",
      rankMean: "Mean evidence rank",
      twoplRank: "2PL rank",
      denseRaschRank: "Dense Rasch rank",
      speed: "Speed",
      context: "Context",
      price: "Price",
      source: "Source",
      coverage: "Coverage",
    },
    table: {
      input: "In",
      output: "Out",
      cache: "Cache",
      perMillion: "/ 1M",
      tokensPerSecond: "tok/s",
      tokens: "tokens",
    },
    languages: {
      "zh-CN": "中",
      "en-US": "EN",
    },
    views: {
      histogram: "Histogram",
      table: "Table",
      text: "Text",
    },
    sourceFilters: {
      all: "All",
      open: "Open",
      closed: "Closed",
      unknown: "Unknown",
    },
    sourceTypes: {
      open: "Open weights",
      closed: "Proprietary",
      unknown: "Unknown",
    },
    presets: {
      "zhihu-adjusted": {
        label: "AInsights Index",
        calculation: "rank-mean",
        normalization: "none",
        description: "The primary ranking blends observed evidence ranks with 70% Equal-board 2PL and 30% Sparse-item Rasch, then breaks equal weighted ranks by 2PL rank, Sparse Rasch rank, and stable ID. Fable 5 #1 and GPT-5.6 Sol #2 are applied by a separate publication layer without changing observed scores.",
      },
      "aa-intelligence": {
        label: "AA Intelligence",
        description: "Artificial Analysis official Intelligence Index.",
      },
      "aa-coding": {
        label: "AA Coding",
        description: "Artificial Analysis official Coding Index.",
      },
      "aa-agentic": {
        label: "AA Agentic",
        description: "Artificial Analysis official Agentic Index.",
      },
      custom: {
        label: "Custom tools",
        calculation: "multi-tool",
        normalization: "mode-specific",
        description: "Separately combines four IRT method ranks, five IRT capability boards, or individual public benchmarks; unlike units are never mixed.",
      },
      "benchmark-lab": {
        label: "Balanced Benchmark Lab",
        description: "A balanced starting point for per-benchmark experiments; these are not fixed primary-ranking weights.",
      },
    },
  },
};

const initialRoute = getInitialRoute();

const state = {
  data: null,
  presetId: null,
  dedupe: true,
  query: "",
  customToolMode: "method-rank",
  customMethodWeights: {
    rasch: 0,
    sparseRasch: 30,
    twopl: 70,
    denseRasch: 0,
  },
  customMethodAggregator: "mean",
  customBoardWeights: {
    coding: 20,
    "agentic-tool-work": 20,
    "hard-reasoning": 20,
    "knowledge-science": 20,
    "instruction-context": 20,
  },
  customBoardAggregator: "arithmetic",
  customWeights: {},
  customWeightPresetId: "benchmark-lab",
  customCalculationMethod: "geometric",
  customNormalizationMethod: "relative-best",
  customMissingMode: "coverage025",
  customMissingBaseMode: "coverage025",
  customPenaltyMax: 0,
  customMinCoveragePct: 0,
  customCoverageDiscountExponent: 0.25,
  customWeakPriorRatio: 35,
  customMinMetricCoverage: 0,
  customMetricGroupsCache: null,
  customRawPriorBaselineCache: {},
  language: getInitialLanguage(),
  page: initialRoute.page,
  modelId: initialRoute.modelId,
  benchmarkId: initialRoute.benchmarkId,
  providerId: initialRoute.providerId,
  compareIds: initialRoute.compareIds || [],
  compareQuery: "",
  compareTouched: false,
  comparePickerOpen: false,
  contributionMode: "score",
  viewMode: "histogram",
  sourceFilter: "all",
  topChartLimit: 20,
};

const els = {
  updatedAt: document.querySelector("#updatedAt"),
  sourceLink: document.querySelector("#sourceLink"),
  sourcesLink: document.querySelector("#sourcesLink"),
  pageButtons: document.querySelector("#pageButtons"),
  homeView: document.querySelector("#homeView"),
  rankingView: document.querySelector("#rankingView"),
  sourcesView: document.querySelector("#sourcesView"),
  methodologyView: document.querySelector("#methodologyView"),
  methodologyDetail: document.querySelector("#methodologyDetail"),
  contributeView: document.querySelector("#contributeView"),
  contributionModeButtons: document.querySelector("#contributionModeButtons"),
  contributionModelName: document.querySelector("#contributionModelName"),
  contributionCreator: document.querySelector("#contributionCreator"),
  contributionReleaseDate: document.querySelector("#contributionReleaseDate"),
  contributionModelUrl: document.querySelector("#contributionModelUrl"),
  contributionOpenSource: document.querySelector("#contributionOpenSource"),
  contributionBenchmark: document.querySelector("#contributionBenchmark"),
  contributionBenchmarkId: document.querySelector("#contributionBenchmarkId"),
  contributionBenchmarkName: document.querySelector("#contributionBenchmarkName"),
  contributionBenchmarkCategory: document.querySelector("#contributionBenchmarkCategory"),
  contributionBenchmarkUnit: document.querySelector("#contributionBenchmarkUnit"),
  contributionBenchmarkIcon: document.querySelector("#contributionBenchmarkIcon"),
  contributionValue: document.querySelector("#contributionValue"),
  contributionSourceUrl: document.querySelector("#contributionSourceUrl"),
  contributionSourceLabel: document.querySelector("#contributionSourceLabel"),
  contributionNotes: document.querySelector("#contributionNotes"),
  contributionPreview: document.querySelector("#contributionPreview"),
  contributionCopyButton: document.querySelector("#contributionCopyButton"),
  contributionGithubButton: document.querySelector("#contributionGithubButton"),
  contributionGithubDevLink: document.querySelector("#contributionGithubDevLink"),
  contributionEditBenchmarksLink: document.querySelector("#contributionEditBenchmarksLink"),
  contributionEditCollectorLink: document.querySelector("#contributionEditCollectorLink"),
  contributionEditCsvLink: document.querySelector("#contributionEditCsvLink"),
  contributionModelList: document.querySelector("#contributionModelList"),
  providerView: document.querySelector("#providerView"),
  providerDetail: document.querySelector("#providerDetail"),
  compareView: document.querySelector("#compareView"),
  comparePageTitle: document.querySelector("#comparePageTitle"),
  comparePageSubtitle: document.querySelector("#comparePageSubtitle"),
  comparePickerTitle: document.querySelector("#comparePickerTitle"),
  compareModelSelectLabel: document.querySelector("#compareModelSelectLabel"),
  compareModelSelect: document.querySelector("#compareModelSelect"),
  compareModelOptions: document.querySelector("#compareModelOptions"),
  compareAddButton: document.querySelector("#compareAddButton"),
  compareClearButton: document.querySelector("#compareClearButton"),
  compareSelectedTitle: document.querySelector("#compareSelectedTitle"),
  compareSelectedModels: document.querySelector("#compareSelectedModels"),
  compareResults: document.querySelector("#compareResults"),
  modelView: document.querySelector("#modelView"),
  modelDetail: document.querySelector("#modelDetail"),
  benchmarkView: document.querySelector("#benchmarkView"),
  benchmarkDetail: document.querySelector("#benchmarkDetail"),
  languageButtons: document.querySelector("#languageButtons"),
  presetButtons: document.querySelector("#presetButtons"),
  viewButtons: document.querySelector("#viewButtons"),
  sourceFilterButtons: document.querySelector("#sourceFilterButtons"),
  searchLabel: document.querySelector("#searchLabel"),
  searchInput: document.querySelector("#searchInput"),
  dedupeToggle: document.querySelector("#dedupeToggle"),
  dedupeLabel: document.querySelector("#dedupeLabel"),
  summaryRow: document.querySelector("#summaryRow"),
  customPanel: document.querySelector("#customPanel"),
  customTitle: document.querySelector("#customTitle"),
  weightsGrid: document.querySelector("#weightsGrid"),
  homeMetrics: document.querySelector("#homeMetrics"),
  latestModelsTitle: document.querySelector("#latestModelsTitle"),
  latestModelsSubtitle: document.querySelector("#latestModelsSubtitle"),
  latestModels: document.querySelector("#latestModels"),
  top20Title: document.querySelector("#top20Title"),
  top20Subtitle: document.querySelector("#top20Subtitle"),
  viewFullRankingLink: document.querySelector("#viewFullRankingLink"),
  costScatterTitle: document.querySelector("#costScatterTitle"),
  costScatterSubtitle: document.querySelector("#costScatterSubtitle"),
  top20Chart: document.querySelector("#top20Chart"),
  costScatter: document.querySelector("#costScatter"),
  scoreBandsTitle: document.querySelector("#scoreBandsTitle"),
  scoreBandsSubtitle: document.querySelector("#scoreBandsSubtitle"),
  scoreBands: document.querySelector("#scoreBands"),
  providerChartTitle: document.querySelector("#providerChartTitle"),
  providerChartSubtitle: document.querySelector("#providerChartSubtitle"),
  providerChart: document.querySelector("#providerChart"),
  sourceExplorerTitle: document.querySelector("#sourceExplorerTitle"),
  sourceExplorerSubtitle: document.querySelector("#sourceExplorerSubtitle"),
  sourceExplorer: document.querySelector("#sourceExplorer"),
  sourcesPageTitle: document.querySelector("#sourcesPageTitle"),
  sourcesPageSubtitle: document.querySelector("#sourcesPageSubtitle"),
  sourceOverview: document.querySelector("#sourceOverview"),
  sourceMetricMapTitle: document.querySelector("#sourceMetricMapTitle"),
  sourceMetricMapSubtitle: document.querySelector("#sourceMetricMapSubtitle"),
  sourceMetricMap: document.querySelector("#sourceMetricMap"),
  histogramList: document.querySelector("#histogramList"),
  tableRanking: document.querySelector("#tableRanking"),
  rankingBody: document.querySelector("#rankingBody"),
  textRanking: document.querySelector("#textRanking"),
  resetWeightsButton: document.querySelector("#resetWeightsButton"),
  modelHeader: document.querySelector("#modelHeader"),
  scoreHeader: document.querySelector("#scoreHeader"),
  twoplRankHeader: document.querySelector("#twoplRankHeader"),
  denseRaschRankHeader: document.querySelector("#denseRaschRankHeader"),
  speedHeader: document.querySelector("#speedHeader"),
  contextHeader: document.querySelector("#contextHeader"),
  priceHeader: document.querySelector("#priceHeader"),
  sourceHeader: document.querySelector("#sourceHeader"),
  coverageHeader: document.querySelector("#coverageHeader"),
  siteFooter: document.querySelector("#siteFooter"),
  metricTemplate: document.querySelector("#metricTemplate"),
};

const presetOrder = ["zhihu-adjusted", "aa-intelligence", "aa-coding", "aa-agentic", "custom"];
const customToolModeOrder = ["method-rank", "board-score", "benchmark-lab"];
const customManualWeightPresetId = "manual";
const customMethodOrder = ["rasch", "sparseRasch", "twopl", "denseRasch"];
const customBoardOrder = ["coding", "agentic-tool-work", "hard-reasoning", "knowledge-science", "instruction-context"];
const customMethodAggregatorOrder = ["mean", "median", "worst"];
const customBoardAggregatorOrder = ["arithmetic", "geometric", "weakest"];
const customWeightPresetOrder = ["benchmark-lab", "aa-intelligence", "aa-coding", "aa-agentic"];
const customCalculationMethodOrder = ["geometric", "arithmetic"];
const customNormalizationMethodOrder = ["relative-best", "raw"];
const missingModePresetOrder = ["available", "coverage025", "coverageSqrt", "weakPrior", "penalty", "zero", "complete"];
const missingModePresets = {
  available: { penalty: 0, minCoverage: 0, coverageDiscountExponent: 0, weakPriorRatio: 35 },
  coverage025: { penalty: 0, minCoverage: 0, coverageDiscountExponent: 0.25, weakPriorRatio: 35 },
  coverageSqrt: { penalty: 0, minCoverage: 0, coverageDiscountExponent: 0.5, weakPriorRatio: 35 },
  weakPrior: { penalty: 0, minCoverage: 0, coverageDiscountExponent: 0, weakPriorRatio: 35 },
  penalty: { penalty: 10, minCoverage: 0, coverageDiscountExponent: 0, weakPriorRatio: 35 },
  zero: { penalty: 100, minCoverage: 0, coverageDiscountExponent: 0, weakPriorRatio: 35 },
  complete: { penalty: 0, minCoverage: 100, coverageDiscountExponent: 0, weakPriorRatio: 35 },
};
const metricCoverageFilterOptions = [0, 10, 25, 50, 100, 250];
const methodologyPageHref = "methodology.html";
const pageOrder = ["home", "ranking", "compare", "benchmarks", "sources", "contribute"];
const viewOrder = ["histogram", "table", "text"];
const sourceFilterOrder = ["all", "open", "closed", "unknown"];
const contributionModes = ["score", "model", "benchmark"];
const providerColors = {
  Alibaba: "#ff6d00",
  Amazon: "#ff9900",
  Anthropic: "#c87557",
  DeepSeek: "#2948d8",
  Google: "#34a853",
  Kimi: "#0b84f3",
  Meta: "#1683e5",
  MiniMax: "#e93569",
  Mistral: "#ff7900",
  NVIDIA: "#86b936",
  OpenAI: "#1e1e1e",
  xAI: "#7167d8",
  Xiaomi: "#ff6900",
  "Z AI": "#4b5563",
};
const fallbackColors = ["#0f766e", "#315c96", "#b45309", "#7c3aed", "#be123c", "#047857"];
const modalitySpecs = [
  { key: "text", label: "Text", icon: "text" },
  { key: "image", label: "Image", icon: "image" },
  { key: "speech", label: "Audio", icon: "audio" },
  { key: "video", label: "Video", icon: "video" },
];

init();

async function init() {
  try {
    state.data = window.AINSIGHTS_MODELS_DATA || (await fetchJsonData());
    state.presetId = state.data.defaultPreset;
    state.dedupe = Boolean(state.data.defaultDedupe);
    state.customWeights = customWeightsForPreset(state.customWeightPresetId);
    applyRankingStateFromUrl();
    els.dedupeToggle.checked = state.dedupe;
    bindControlEvents();
    renderStaticControls();
    setupTopChartResizeObserver();
    render();
  } catch (error) {
    renderLoadError(error);
  }
}

async function fetchJsonData() {
  const response = await fetch("./data/models.json", { cache: "no-store" });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

function applyRankingStateFromUrl(params = new URLSearchParams(location.search)) {
  const presetId = params.get("preset");
  if (presetId && state.data?.presets?.[presetId]) state.presetId = presetId;
  const viewMode = params.get("view");
  if (viewOrder.includes(viewMode)) state.viewMode = viewMode;
  const sourceFilter = params.get("source");
  if (sourceFilterOrder.includes(sourceFilter)) state.sourceFilter = sourceFilter;
  if (params.has("q")) state.query = String(params.get("q") || "").trim().toLowerCase();
  if (params.has("dedupe")) state.dedupe = parseDedupeParam(params.get("dedupe"), state.dedupe);
  if (els.searchInput) els.searchInput.value = state.query;
  if (els.dedupeToggle) els.dedupeToggle.checked = state.dedupe;
}

function parseDedupeParam(value, fallback = true) {
  const normalized = String(value ?? "").trim().toLowerCase();
  if (["0", "false", "no"].includes(normalized)) return false;
  if (["1", "true", "yes"].includes(normalized)) return true;
  return fallback;
}

function syncRankingUrl() {
  if (state.page !== "ranking" || !window.history?.replaceState) return;
  const nextHref = rankingHref(currentRankingContext());
  const currentHref = `${location.pathname.split("/").pop() || "full-rank.html"}${location.search}`;
  if (nextHref !== currentHref) history.replaceState(null, "", nextHref);
}

function bindControlEvents() {
  els.searchInput.addEventListener("input", (event) => {
    state.query = event.target.value.trim().toLowerCase();
    syncRankingUrl();
    render();
  });
  els.dedupeToggle.addEventListener("change", (event) => {
    state.dedupe = event.target.checked;
    syncRankingUrl();
    render();
  });
  els.resetWeightsButton.addEventListener("click", () => {
    resetCustomConfiguration();
    state.presetId = "custom";
    syncRankingUrl();
    render();
  });
  window.addEventListener("hashchange", () => {
    const previousPage = state.page;
    const route = getInitialRoute();
    state.page = route.page;
    state.modelId = route.modelId;
    state.benchmarkId = route.benchmarkId;
    state.providerId = route.providerId;
    state.compareIds = route.compareIds || [];
    state.compareTouched = false;
    renderStaticControls();
    render();
    if (previousPage !== state.page || state.page === "provider") {
      requestAnimationFrame(() => window.scrollTo({ top: 0, left: 0 }));
    }
  });
  document.addEventListener("click", (event) => {
    const backLink = event.target.closest("[data-history-back]");
    if (!backLink || !sameSiteReferrer()) return;
    event.preventDefault();
    history.back();
  });
  if (els.compareModelSelect) {
    els.compareModelSelect.addEventListener("input", (event) => {
      state.compareQuery = event.target.value.trim().toLowerCase();
      state.comparePickerOpen = true;
      render();
      requestAnimationFrame(() => els.compareModelSelect?.focus());
    });
    els.compareModelSelect.addEventListener("focus", () => {
      state.comparePickerOpen = true;
      render();
      requestAnimationFrame(() => els.compareModelSelect?.focus());
    });
    els.compareModelSelect.addEventListener("keydown", (event) => {
      if (event.key !== "Escape") return;
      state.comparePickerOpen = false;
      render();
      requestAnimationFrame(() => els.compareModelSelect?.focus());
    });
  }
  if (els.compareAddButton) {
    els.compareAddButton.addEventListener("click", (event) => {
      event.stopPropagation();
      addCompareModel(els.compareAddButton.dataset.compareAdd);
    });
  }
  if (els.compareClearButton) {
    els.compareClearButton.addEventListener("click", () => {
      updateCompareSelection([]);
    });
  }
  bindContributionEvents();
  document.addEventListener("click", (event) => {
    const addButton = event.target.closest("[data-compare-add]");
    if (!addButton) return;
    event.preventDefault();
    addCompareModel(addButton.dataset.compareAdd);
  });
  document.addEventListener("click", (event) => {
    const removeButton = event.target.closest("[data-compare-remove]");
    if (!removeButton) return;
    updateCompareSelection(state.compareIds.filter((id) => id !== removeButton.dataset.compareRemove));
  });
  document.addEventListener("click", (event) => {
    const card = event.target.closest("[data-card-href]");
    if (!card || event.target.closest("a, button, input, select, textarea, label")) return;
    window.location.href = card.dataset.cardHref;
  });
  document.addEventListener("keydown", (event) => {
    const card = event.target.closest("[data-card-href]");
    if (!card || !["Enter", " "].includes(event.key)) return;
    if (event.target.closest("a, button, input, select, textarea, label")) return;
    event.preventDefault();
    window.location.href = card.dataset.cardHref;
  });
  document.addEventListener("click", (event) => {
    if (!state.comparePickerOpen || event.target.closest(".compare-search-wrap")) return;
    state.comparePickerOpen = false;
    render();
  });
}

function setupTopChartResizeObserver() {
  const updateLimit = () => {
    const width = els.top20Chart.clientWidth || 0;
    const nextLimit = computeTopChartLimit(width);
    if (nextLimit !== state.topChartLimit) {
      state.topChartLimit = nextLimit;
      renderResults(state.data.presets[state.presetId]);
    }
  };
  if (window.ResizeObserver) {
    const observer = new ResizeObserver(updateLimit);
    observer.observe(els.top20Chart);
  }
  window.addEventListener("resize", updateLimit);
  requestAnimationFrame(updateLimit);
}

function renderStaticControls() {
  document.documentElement.lang = state.language;
  document.title = tr("pageTitle");
  els.updatedAt.textContent = tr("updatedAt", { date: formatDateTime(state.data.generatedAt) });
  els.sourceLink.textContent = tr("source");
  els.sourceLink.href = state.data.source.url;
  els.sourcesLink.textContent = tr("sourcesBadge", { count: catalogSources().length });
  els.sourcesLink.href = pageHref("sources");
  els.searchLabel.textContent = tr("search");
  els.searchInput.placeholder = tr("searchPlaceholder");
  els.dedupeLabel.textContent = tr("dedupe");
  els.customTitle.textContent = tr("customTitle");
  els.resetWeightsButton.textContent = tr("reset");
  if (els.latestModelsTitle) els.latestModelsTitle.textContent = tr("latestModelsTitle");
  if (els.latestModelsSubtitle) els.latestModelsSubtitle.textContent = tr("latestModelsSubtitle");
  if (els.comparePageTitle) els.comparePageTitle.textContent = tr("comparePageTitle");
  if (els.comparePageSubtitle) els.comparePageSubtitle.textContent = tr("comparePageSubtitle");
  if (els.comparePickerTitle) els.comparePickerTitle.textContent = tr("comparePickerTitle");
  if (els.compareModelSelectLabel) els.compareModelSelectLabel.textContent = tr("compareModelSelectLabel");
  if (els.compareModelSelect) {
    els.compareModelSelect.placeholder = tr("compareSearchPlaceholder");
    els.compareModelSelect.setAttribute("aria-label", tr("compareSearchPlaceholder"));
  }
  if (els.compareAddButton) els.compareAddButton.innerHTML = `${renderIcon("plus")}${escapeHtml(tr("compareAdd"))}`;
  if (els.compareClearButton) els.compareClearButton.innerHTML = `${renderIcon("x")}${escapeHtml(tr("compareClear"))}`;
  if (els.compareSelectedTitle) els.compareSelectedTitle.textContent = tr("compareSelectedTitle");
  els.top20Title.textContent = tr("top20Title", { count: state.topChartLimit });
  els.top20Subtitle.textContent = tr("top20Subtitle");
  els.viewFullRankingLink.textContent = tr("fullRanking");
  els.viewFullRankingLink.href = pageHref("ranking");
  els.costScatterTitle.textContent = tr("costScatterTitle");
  els.costScatterSubtitle.textContent = tr("costScatterSubtitle");
  els.scoreBandsTitle.textContent = tr("scoreBandsTitle");
  els.scoreBandsSubtitle.textContent = tr("scoreBandsSubtitle");
  els.providerChartTitle.textContent = tr("providerChartTitle");
  els.providerChartSubtitle.textContent = tr("providerChartSubtitle");
  els.sourceExplorerTitle.textContent = tr("sourceExplorerTitle");
  els.sourceExplorerSubtitle.textContent = tr("sourceExplorerSubtitle");
  els.sourcesPageTitle.textContent = tr("sourcesPageTitle");
  els.sourcesPageSubtitle.textContent = tr("sourcesPageSubtitle");
  els.sourceMetricMapTitle.textContent = tr("sourceMetricMapTitle");
  els.sourceMetricMapSubtitle.textContent = tr("sourceMetricMapSubtitle");
  if (els.contributionGithubDevLink) els.contributionGithubDevLink.textContent = tr("contributeGithubDev");
  if (els.contributionEditBenchmarksLink) els.contributionEditBenchmarksLink.textContent = tr("contributeEditBenchmarks");
  if (els.contributionEditCollectorLink) els.contributionEditCollectorLink.textContent = tr("contributeEditCollector");
  if (els.contributionEditCsvLink) els.contributionEditCsvLink.textContent = tr("contributeEditAaCsv");
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = tr(node.dataset.i18n);
  });
  els.modelHeader.textContent = tr("headers.model");
  els.scoreHeader.textContent = tr("headers.score");
  if (els.twoplRankHeader) {
    els.twoplRankHeader.textContent = tr("headers.twoplRank");
    els.twoplRankHeader.title = tr("customMethodWeightsSubtitle");
  }
  if (els.denseRaschRankHeader) {
    els.denseRaschRankHeader.textContent = tr("headers.denseRaschRank");
    els.denseRaschRankHeader.title = tr("customMethodWeightsSubtitle");
  }
  els.speedHeader.textContent = tr("headers.speed");
  els.contextHeader.textContent = tr("headers.context");
  els.priceHeader.textContent = tr("headers.price");
  els.sourceHeader.textContent = tr("headers.source");
  els.coverageHeader.textContent = tr("headers.coverage");
  els.languageButtons.setAttribute("aria-label", tr("languageLabel"));
  els.siteFooter.innerHTML = `${escapeHtml(tr("footerPrefix"))}<a href="${escapeHtml(state.data.source.url)}" target="_blank" rel="noreferrer">Artificial Analysis</a> · <a href="${escapeHtml(pageHref("sources"))}">${escapeHtml(tr("sourcesBadge", { count: catalogSources().length }))}</a>${escapeHtml(tr("footerSuffix"))} · <a href="https://github.com/TabNahida/AInsights" target="_blank" rel="noreferrer">${escapeHtml(tr("repository"))}: TabNahida/AInsights</a>`;

  renderPageButtons();
  renderLanguageButtons();
  renderPresetButtons();
  renderViewButtons();
  renderSourceFilterButtons();
}

function renderPageButtons() {
  els.pageButtons.innerHTML = "";
  for (const id of pageOrder) {
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.page = id;
    button.textContent = tr(`pages.${id}`);
    button.setAttribute("aria-pressed", String(id === state.page));
    button.addEventListener("click", () => {
      window.location.href = pageHref(id);
    });
    els.pageButtons.append(button);
  }
}

function renderLanguageButtons() {
  els.languageButtons.innerHTML = "";
  for (const language of Object.keys(copy)) {
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.language = language;
    button.textContent = tr(`languages.${language}`);
    button.setAttribute("aria-pressed", String(language === state.language));
    button.addEventListener("click", () => {
      state.language = language;
      saveLanguage(language);
      renderStaticControls();
      render();
    });
    els.languageButtons.append(button);
  }
}

function renderPresetButtons() {
  els.presetButtons.innerHTML = "";
  for (const id of presetOrder) {
    const button = document.createElement("button");
    button.type = "button";
    button.role = "tab";
    button.dataset.preset = id;
    button.textContent = presetLabel(id);
    button.addEventListener("click", () => {
      state.presetId = id;
      syncRankingUrl();
      render();
    });
    els.presetButtons.append(button);
  }
}

function renderViewButtons() {
  els.viewButtons.innerHTML = "";
  for (const id of viewOrder) {
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.view = id;
    button.textContent = tr(`views.${id}`);
    button.setAttribute("aria-pressed", String(id === state.viewMode));
    button.addEventListener("click", () => {
      state.viewMode = id;
      syncRankingUrl();
      render();
    });
    els.viewButtons.append(button);
  }
}

function renderSourceFilterButtons() {
  els.sourceFilterButtons.innerHTML = "";
  for (const id of sourceFilterOrder) {
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.sourceFilter = id;
    button.textContent = tr(`sourceFilters.${id}`);
    button.setAttribute("aria-pressed", String(id === state.sourceFilter));
    button.addEventListener("click", () => {
      state.sourceFilter = id;
      syncRankingUrl();
      render();
    });
    els.sourceFilterButtons.append(button);
  }
}

function bindContributionEvents() {
  if (!els.contributeView) return;
  els.contributeView.addEventListener("input", updateContributionPreview);
  els.contributeView.addEventListener("change", updateContributionPreview);
  els.contributeView.addEventListener("click", async (event) => {
    const modeButton = event.target.closest("[data-contribution-mode]");
    if (modeButton) {
      state.contributionMode = modeButton.dataset.contributionMode;
      renderContributionModeButtons();
      renderContributionFormMode();
      updateContributionPreview();
      return;
    }
    if (event.target.closest("#contributionCopyButton")) {
      event.preventDefault();
      await copyContributionPayload();
    }
  });
}

function renderContributePage() {
  document.title = `${tr("contributePageTitle")} · ${tr("pageTitle")}`;
  renderContributionModeButtons();
  renderContributionBenchmarkOptions();
  renderContributionModelList();
  renderContributionFormMode();
  updateContributionPreview();
}

function renderContributionModeButtons() {
  if (!els.contributionModeButtons) return;
  els.contributionModeButtons.innerHTML = "";
  for (const mode of contributionModes) {
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.contributionMode = mode;
    button.textContent = contributionModeLabel(mode);
    button.setAttribute("aria-pressed", String(state.contributionMode === mode));
    els.contributionModeButtons.append(button);
  }
}

function contributionModeLabel(mode) {
  if (mode === "model") return tr("contributeModeModel");
  if (mode === "benchmark") return tr("contributeModeBenchmark");
  return tr("contributeModeScore");
}

function renderContributionFormMode() {
  if (!els.contributeView) return;
  els.contributeView.querySelectorAll("[data-contribution-section]").forEach((element) => {
    const modes = String(element.dataset.contributionSection || "").split(/\s+/).filter(Boolean);
    element.hidden = !modes.includes(state.contributionMode);
  });
}

function renderContributionBenchmarkOptions() {
  if (!els.contributionBenchmark) return;
  const current = els.contributionBenchmark.value;
  const options = [`<option value="">${escapeHtml(tr("contributeSelectBenchmark"))}</option>`]
    .concat((state.data.metrics || []).map((metric) => (
      `<option value="${escapeHtml(metric.key)}">${escapeHtml(metric.label)}</option>`
    )));
  els.contributionBenchmark.innerHTML = options.join("");
  if (current) els.contributionBenchmark.value = current;
}

function renderContributionModelList() {
  if (!els.contributionModelList) return;
  els.contributionModelList.innerHTML = (state.data.models || [])
    .map((model) => `<option value="${escapeHtml(model.model)}"></option>`)
    .join("");
}

function contributionPayload() {
  const modelName = els.contributionModelName?.value.trim() || "";
  const creator = els.contributionCreator?.value.trim() || "";
  const sourceUrl = els.contributionSourceUrl?.value.trim() || "";
  const benchmarkKey = els.contributionBenchmark?.value || "";
  const metric = metricDefinition(benchmarkKey);
  const sourceLabel = els.contributionSourceLabel?.value.trim()
    || defaultContributionSourceLabel(modelName, creator);
  if (state.contributionMode === "benchmark") {
    const benchmarkName = els.contributionBenchmarkName?.value.trim() || "";
    const benchmarkId = els.contributionBenchmarkId?.value.trim() || slugPart(benchmarkName);
    return {
      version: 1,
      type: "benchmark",
      repository: "TabNahida/AInsights",
      benchmark: {
        id: benchmarkId,
        label: benchmarkName,
        category: els.contributionBenchmarkCategory?.value.trim() || "",
        unit: els.contributionBenchmarkUnit?.value.trim() || "%",
        icon: els.contributionBenchmarkIcon?.value.trim() || "",
      },
      source: {
        label: sourceLabel || [benchmarkName, "benchmark source"].filter(Boolean).join(" "),
        url: sourceUrl,
        category: "Benchmark methodology",
        note: els.contributionNotes?.value.trim() || "",
      },
      filesToReview: [
        "benchmarks/collect_benchmark_scores.py",
        "data/benchmarks/benchmark_scores.json",
        "scripts/build_docs_site.py",
      ],
    };
  }
  const payload = {
    version: 1,
    type: state.contributionMode === "model" ? "model" : "model-benchmark-data",
    repository: "TabNahida/AInsights",
    model: {
      name: modelName,
      creator,
      releaseDate: els.contributionReleaseDate?.value || "",
      modelUrl: els.contributionModelUrl?.value.trim() || "",
      openSourceCategorization: els.contributionOpenSource?.value || "",
    },
    source: {
      label: sourceLabel,
      url: sourceUrl,
      category: state.contributionMode === "model" ? "Official model card" : "Official release",
      note: els.contributionNotes?.value.trim() || "",
    },
    filesToReview: state.contributionMode === "model"
      ? ["ArtificialAnalysis/artificialanalysis_raw_scores_wide.csv", "benchmarks/collect_benchmark_scores.py"]
      : ["data/benchmarks/benchmark_scores.json", "benchmarks/collect_benchmark_scores.py"],
  };
  if (state.contributionMode === "score") {
    payload.benchmark = {
      metricKey: benchmarkKey,
      label: metric.label || "",
      value: numericContributionValue(),
      unit: metric.unit || "%",
    };
  }
  return payload;
}

function defaultContributionSourceLabel(modelName, creator) {
  return [creator, modelName, "official source"].filter(Boolean).join(" ");
}

function updateContributionPreview() {
  if (!els.contributionPreview) return;
  const payload = contributionPayload();
  const hasRequiredFields = contributionHasRequiredFields(payload);
  els.contributionPreview.textContent = hasRequiredFields
    ? JSON.stringify(payload, null, 2)
    : tr("contributeRequired");
  if (els.contributionGithubButton) {
    els.contributionGithubButton.textContent = tr("contributeGithubPr");
    els.contributionGithubButton.href = hasRequiredFields ? contributionGithubNewFileHref(payload) : "#";
    els.contributionGithubButton.setAttribute("aria-disabled", String(!hasRequiredFields));
  }
  if (els.contributionCopyButton) {
    els.contributionCopyButton.textContent = tr("contributeCopy");
    els.contributionCopyButton.disabled = !hasRequiredFields;
  }
}

async function copyContributionPayload() {
  const payload = contributionPayload();
  if (!contributionHasRequiredFields(payload)) return;
  const text = JSON.stringify(payload, null, 2);
  try {
    await navigator.clipboard.writeText(text);
    els.contributionCopyButton.textContent = tr("contributeCopied");
  } catch {
    els.contributionPreview.focus();
  }
}

function contributionGithubNewFileHref(payload) {
  const subject = contributionSubjectName(payload);
  const owner = payload.model?.creator || payload.benchmark?.category || payload.type || "contribution";
  const filename = `contributions/${slugPart(owner)}-${slugPart(subject || "update")}.json`;
  const params = new URLSearchParams({
    filename,
    value: `${JSON.stringify(payload, null, 2)}\n`,
    message: `Add ${subject} contribution payload`,
  });
  return `https://github.com/TabNahida/AInsights/new/main?${params.toString()}`;
}

function contributionHasRequiredFields(payload) {
  return Boolean(contributionSubjectName(payload) && payload.source?.url);
}

function contributionSubjectName(payload) {
  return payload.benchmark?.label || payload.model?.name || "";
}

function numericContributionValue() {
  const raw = Number(els.contributionValue?.value);
  return Number.isFinite(raw) ? raw : null;
}

function slugPart(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 60) || "update";
}

function render() {
  const preset = state.data.presets[state.presetId];
  els.homeView.hidden = state.page !== "home";
  els.rankingView.hidden = state.page !== "ranking";
  els.sourcesView.hidden = state.page !== "sources";
  if (els.methodologyView) els.methodologyView.hidden = state.page !== "methodology";
  if (els.contributeView) els.contributeView.hidden = state.page !== "contribute";
  els.modelView.hidden = state.page !== "model";
  els.benchmarkView.hidden = state.page !== "benchmarks";
  if (els.providerView) els.providerView.hidden = state.page !== "provider";
  if (els.compareView) els.compareView.hidden = state.page !== "compare";
  document.querySelectorAll("#pageButtons button").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.page === state.page));
  });
  document.querySelectorAll("#presetButtons button").forEach((button) => {
    button.setAttribute("aria-selected", String(button.dataset.preset === state.presetId));
  });
  document.querySelectorAll("#viewButtons button").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.view === state.viewMode));
  });
  document.querySelectorAll("#sourceFilterButtons button").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.sourceFilter === state.sourceFilter));
  });
  els.customPanel.hidden = state.presetId !== "custom";
  if (!els.customPanel.hidden) renderWeights();

  if (!els.sourcesView.hidden) {
    renderSourcesPage();
    return;
  }
  if (els.methodologyView && !els.methodologyView.hidden) {
    renderMethodologyPage();
    return;
  }
  if (els.contributeView && !els.contributeView.hidden) {
    renderContributePage();
    return;
  }

  renderResults(preset);
}

function renderResults(preset) {
  const scored = scoreModels(preset);
  const homePreset = state.data.presets["zhihu-adjusted"];
  const homeScored = scoreModels(homePreset, "zhihu-adjusted");
  const homeRanked = rankRows(dedupeByBestVariant(homeScored));
  const compareRanked = rankRows(homeScored);
  const filtered = scored.filter(matchesQuery).filter(matchesSourceFilter);
  const rankingUniverse = state.dedupe ? dedupeByBestVariant(scored) : scored;
  const ranked = rankRows(rankingUniverse).filter(matchesQuery).filter(matchesSourceFilter);
  const allRanked = rankRows(scored);
  const homeDisplayModels = mergeRankedWithUnscored(homeRanked, homeScored);
  const compareDisplayModels = mergeRankedWithUnscored(compareRanked, homeScored);
  const allDisplayModels = mergeRankedWithUnscored(allRanked, scored);

  if (!els.homeView.hidden) renderHome(homeRanked, homeDisplayModels);
  if (!els.rankingView.hidden) {
    els.scoreHeader.textContent = tr(scoreHeaderKeyForPreset(preset));
    renderSummary(filtered.length, ranked.length, scored.length, preset);
    renderRankings(ranked);
  }
  if (!els.modelView.hidden) renderModelDetail(allDisplayModels, preset);
  if (!els.benchmarkView.hidden) renderBenchmarkPage();
  if (els.providerView && !els.providerView.hidden) renderProviderPage(homeRanked);
  if (els.compareView && !els.compareView.hidden) renderComparePage(compareDisplayModels);
}

function mergeRankedWithUnscored(ranked, scoredUniverse = ranked) {
  const scoredIds = new Set(scoredUniverse.map(modelRouteId));
  const unscored = state.data.models
    .filter((model) => !scoredIds.has(modelRouteId(model)))
    .map((model) => ({
      ...model,
      score: null,
      rank: null,
      coverage: 0,
      coverageLabel: tr("notAvailable"),
      availableWeight: 0,
      scoreMeta: tr("notAvailable"),
    }));
  return [...ranked, ...unscored];
}

function scoreModels(preset, presetId = state.presetId) {
  return state.data.models
    .map((model) => {
      const result = scoreModel(model, preset, presetId);
      return {
        ...model,
        ...result,
      };
    })
    .filter((model) => Number.isFinite(model.score));
}

function scoreModel(model, preset, presetId = state.presetId) {
  if (preset.kind === "precomputed-ranking") {
    return scoreModelForPrecomputedRanking(model);
  }

  if (preset.kind === "aa-column") {
    const score = model.aa[preset.column];
    return {
      score,
      coverage: Number.isFinite(score) ? 1 : 0,
      coverageLabel: Number.isFinite(score) ? "AA" : "—",
      availableWeight: Number.isFinite(score) ? 1 : 0,
      scoreMeta: "AA",
    };
  }

  if (preset.kind === "frontier-groups") {
    return scoreModelForFrontierGroups(model, preset);
  }

  if (preset.kind === "regular-plus-bonus") {
    return scoreModelForRegularPlusBonus(model, preset);
  }

  if (presetId === "custom") {
    return scoreModelForCustomWeights(model);
  }

  const weights = presetId === "custom" ? state.customWeights : preset.weights;
  const entries = [];
  let denominator = 0;
  let availableWeight = 0;
  let coverage = 0;
  const ignoreMissing = Boolean(preset.ignoreMissing);
  const minCoverage = Number(preset.minCoverage || 0);
  const method = preset.calculation || "arithmetic";
  const normalization = preset.normalization || "raw";
  for (const metric of state.data.metrics) {
    const weight = Number(weights[metric.key] || 0);
    const rawValue = model.scores[metric.key];
    if (weight <= 0) continue;
    if (Number.isFinite(rawValue)) {
      const value = scoreValueForMetric(metric.key, rawValue, normalization);
      entries.push({ value, weight });
      denominator += weight;
      availableWeight += weight;
      coverage += 1;
    } else if (!ignoreMissing) {
      entries.push({ value: 0, weight });
      denominator += weight;
    }
  }
  const score = denominator > 0 && coverage >= minCoverage ? customAggregateScore(entries, denominator, method, normalization) : null;
  return {
    score,
    coverage,
    availableWeight,
    scoreMeta: `${formatNumber(availableWeight)}w`,
  };
}

function scoreModelForPrecomputedRanking(model) {
  const profile = model?.rankingProfile;
  const rankMean = Number(profile?.evidenceMeanRank);
  const rankPercentile = Number(profile?.rankPercentile);
  const publicationRank = Number(profile?.publicationRank);
  if (!Number.isFinite(rankMean) || !Number.isFinite(rankPercentile) || !Number.isFinite(publicationRank)) {
    return {
      score: null,
      displayScore: null,
      coverage: 0,
      coverageLabel: tr("notAvailable"),
      availableWeight: 0,
      scoreMeta: tr("notAvailable"),
    };
  }
  const twoplRank = rankingMethodEvidenceRank(model, "twopl");
  const sparseRank = rankingMethodEvidenceRank(model, "sparseRasch");
  const familyCount = Number(profile.uniqueBenchmarkFamilies || 0);
  const evidenceTier = String(profile.evidenceTier || "").trim();
  return {
    score: rankPercentile,
    displayScore: rankMean,
    scoreBarValue: rankPercentile,
    precomputedRanking: true,
    publicationRank,
    evidenceRank: Number(profile.evidenceRank),
    rankMean,
    rankMin: Number(profile.rankMin),
    rankMax: Number(profile.rankMax),
    coverage: familyCount,
    coverageLabel: [evidenceTier, familyCount ? `${familyCount} families` : ""].filter(Boolean).join(" · ") || tr("notAvailable"),
    availableWeight: 100,
    scoreMeta: [
      Number.isFinite(twoplRank) ? `2PL #${twoplRank}` : "",
      Number.isFinite(sparseRank) ? `Sparse #${sparseRank}` : "",
    ].filter(Boolean).join(" · "),
  };
}

function rankingMethodEvidenceRank(model, methodId) {
  const value = Number(model?.rankingProfile?.methods?.[methodId]?.evidenceRank);
  return Number.isFinite(value) ? value : null;
}

function rankingMethodPublicationRank(model, methodId) {
  const value = Number(model?.rankingProfile?.methods?.[methodId]?.publicationRank);
  return Number.isFinite(value) ? value : null;
}

function scoreModelForRegularPlusBonus(model, preset) {
  const method = preset.calculation || "geometric";
  const normalization = preset.normalization || "relative-best";
  const coverageDiscountExponent = Number(preset.coverageDiscountExponent ?? 0.25);
  const regularWeights = preset.regularWeights || preset.weights || {};
  const regular = scoreModelForWeightedMetrics(
    model,
    regularWeights,
    method,
    normalization,
    coverageDiscountExponent,
    preset.metricTransforms || [],
  );
  if (!Number.isFinite(regular.score)) return regular;

  const bonusWeights = preset.bonusWeights || {};
  const bonusCap = Number(preset.bonusCap || 0);
  const bonusTotalWeight = Object.values(bonusWeights).reduce((sum, value) => {
    const weight = Number(value || 0);
    return weight > 0 ? sum + weight : sum;
  }, 0);
  let bonus = 0;
  let bonusCoverage = 0;
  if (bonusCap > 0 && bonusTotalWeight > 0) {
    Object.entries(bonusWeights).forEach(([key, rawWeight]) => {
      const weight = Number(rawWeight || 0);
      const rawValue = model.scores?.[key];
      if (weight <= 0 || !Number.isFinite(rawValue)) return;
      bonus += bonusCap * weight * scoreValueForMetric(key, rawValue, normalization) / bonusTotalWeight;
      bonusCoverage += 1;
    });
  }

  return {
    score: regular.score + bonus,
    coverage: regular.coverage + bonusCoverage,
    coverageLabel: `${regular.coverageLabel} +${bonusCoverage}`,
    availableWeight: regular.availableWeight,
    scoreMeta: `${regular.scoreMeta} · +${formatTrimmed(bonus, 2)}`,
  };
}

function scoreModelForWeightedMetrics(
  model,
  weights,
  method,
  normalization,
  coverageDiscountExponent,
  metricTransforms = [],
) {
  const entries = [];
  let denominator = 0;
  let availableWeight = 0;
  let totalWeight = 0;
  let coverage = 0;
  Object.entries(weights || {}).forEach(([key, rawWeight]) => {
    const weight = Number(rawWeight || 0);
    if (weight <= 0) return;
    totalWeight += weight;
    const rawValue = model.scores?.[key];
    if (!Number.isFinite(rawValue)) return;
    entries.push({ value: transformedScoreValueForMetric(key, rawValue, normalization, metricTransforms), weight });
    denominator += weight;
    availableWeight += weight;
    coverage += 1;
  });
  let score = denominator > 0
    ? customAggregateScore(entries, denominator, method, normalization)
    : null;
  if (Number.isFinite(score) && totalWeight > 0) {
    score *= (availableWeight / totalWeight) ** coverageDiscountExponent;
  }
  return {
    score,
    coverage,
    coverageLabel: `${coverage}/${Object.values(weights || {}).filter((weight) => Number(weight || 0) > 0).length}`,
    availableWeight,
    scoreMeta: `${formatNumber(availableWeight)}w`,
  };
}

function transformedScoreValueForMetric(key, rawValue, normalization, metricTransforms = []) {
  let value = scoreValueForMetric(key, rawValue, normalization);
  for (const transform of metricTransforms || []) {
    if (!(transform.metrics || []).includes(key)) continue;
    if (transform.type === "log1p") {
      const factor = Number(transform.factor || 0);
      if (factor > 0) value = Math.log1p(factor * Math.max(value, 0)) / Math.log1p(factor);
    }
  }
  return value;
}

function scoreModelForFrontierGroups(model, preset) {
  const method = preset.calculation || "geometric";
  const normalization = preset.normalization || "relative-best";
  const missingPolicy = preset.missingPolicy || "coverage-discount";
  const groupMetricCoverageDiscountExponent = Number(preset.groupMetricCoverageDiscountExponent || 0);
  const singleMetricCoverageDiscountExponent = Number(
    preset.singleMetricCoverageDiscountExponent ?? groupMetricCoverageDiscountExponent,
  );
  const groups = Array.isArray(preset.groups) ? preset.groups : [];
  const entries = [];
  let denominator = 0;
  let availableWeight = 0;
  let totalWeight = 0;
  let coverage = 0;

  for (const group of groups) {
    const weight = Number(group.weight || preset.groupWeights?.[group.id] || 0);
    if (weight <= 0) continue;
    totalWeight += weight;
    const value = frontierGroupValue(
      model,
      group.metrics || [],
      method,
      normalization,
      groupMetricCoverageDiscountExponent,
      singleMetricCoverageDiscountExponent,
    );
    if (Number.isFinite(value)) {
      entries.push({ value, weight });
      denominator += weight;
      availableWeight += weight;
      coverage += 1;
    } else if (missingPolicy === "zero") {
      entries.push({ value: 0, weight });
      denominator += weight;
    } else if (missingPolicy === "weak-prior") {
      entries.push({ value: Number(preset.weakPriorRatio || 0.35), weight });
      denominator += weight;
    }
  }

  let score = denominator > 0 && coverage > 0
    ? customAggregateScore(entries, denominator, method, normalization)
    : null;
  if (Number.isFinite(score) && normalization === "relative-best" && Number.isFinite(Number(preset.displayScale))) {
    const defaultScale = aaIntelligenceScoreBaseline();
    if (defaultScale > 0) score *= Number(preset.displayScale) / defaultScale;
  }
  if (Number.isFinite(score) && missingPolicy === "coverage-discount") {
    const coverageRatio = totalWeight > 0 ? availableWeight / totalWeight : 0;
    score *= coverageRatio ** Number(preset.coverageDiscountExponent ?? 0.25);
  }
  return {
    score,
    coverage,
    coverageLabel: `${coverage}/${groups.length}`,
    availableWeight,
    scoreMeta: `${formatNumber(availableWeight)}w`,
  };
}

function frontierGroupValue(
  model,
  metricKeys,
  method = "geometric",
  normalization = "relative-best",
  coverageDiscountExponent = 0,
  singleMetricCoverageDiscountExponent = coverageDiscountExponent,
) {
  const metricItems = frontierGroupMetricItems(metricKeys);
  const totalMetricWeight = metricItems.reduce((sum, metric) => sum + metric.weight, 0);
  let availableMetricWeight = 0;
  const entries = [];
  for (const metric of metricItems) {
    const value = scoreValueForMetric(metric.key, model.scores?.[metric.key], normalization);
    if (!Number.isFinite(value)) continue;
    entries.push({ value, weight: metric.weight });
    availableMetricWeight += metric.weight;
  }
  if (!entries.length) return null;
  let score = aggregateScoreEntries(entries, availableMetricWeight, method);
  const discountExponent = entries.length === 1
    ? singleMetricCoverageDiscountExponent
    : coverageDiscountExponent;
  if (Number.isFinite(score) && discountExponent > 0 && totalMetricWeight > 0) {
    score *= (availableMetricWeight / totalMetricWeight) ** discountExponent;
  }
  return score;
}

function frontierGroupMetricItems(metricKeys) {
  return (metricKeys || [])
    .map((item) => {
      if (item && typeof item === "object") {
        return { key: String(item.key || ""), weight: Number(item.weight || 0) };
      }
      return { key: String(item || ""), weight: 1 };
    })
    .filter((item) => item.key && item.weight > 0);
}

function scoreModelForCustomWeights(model) {
  if (state.customToolMode === "method-rank") return scoreModelForCustomMethodRanks(model);
  if (state.customToolMode === "board-score") return scoreModelForCustomBoards(model);
  return scoreModelForBenchmarkWeights(model);
}

function scoreModelForCustomMethodRanks(model) {
  const entries = customMethodOrder
    .map((methodId) => ({
      value: rankingMethodEvidenceRank(model, methodId),
      weight: Math.max(Number(state.customMethodWeights[methodId] || 0), 0),
    }))
    .filter((entry) => Number.isFinite(entry.value) && entry.weight > 0);
  const denominator = entries.reduce((sum, entry) => sum + entry.weight, 0);
  let rankMean = null;
  if (entries.length && denominator > 0) {
    if (state.customMethodAggregator === "median") {
      rankMean = weightedMedianValue(entries);
    } else if (state.customMethodAggregator === "worst") {
      rankMean = Math.max(...entries.map((entry) => entry.value));
    } else {
      rankMean = entries.reduce((sum, entry) => sum + entry.value * entry.weight, 0) / denominator;
    }
  }
  const populationSize = rankingPopulationSize();
  const rankPercentile = Number.isFinite(rankMean)
    ? 100 * (populationSize - rankMean) / Math.max(populationSize - 1, 1)
    : null;
  return {
    score: Number.isFinite(rankPercentile) ? clamp(rankPercentile, 0, 100) : null,
    displayScore: rankMean,
    scoreBarValue: rankPercentile,
    customPublicationRanking: true,
    customMethodRanking: true,
    customRankMax: entries.length ? Math.max(...entries.map((entry) => entry.value)) : null,
    customRankMin: entries.length ? Math.min(...entries.map((entry) => entry.value)) : null,
    coverage: entries.length,
    coverageLabel: `${entries.length}/${customMethodOrder.length}`,
    availableWeight: denominator,
    scoreMeta: tr(`customMethodAggregators.${state.customMethodAggregator}`),
  };
}

function scoreModelForCustomBoards(model) {
  const entries = customBoardOrder
    .map((boardId) => ({
      value: Number(model?.rankingProfile?.boards?.[boardId]?.score),
      weight: Math.max(Number(state.customBoardWeights[boardId] || 0), 0),
    }))
    .filter((entry) => Number.isFinite(entry.value) && entry.weight > 0);
  const denominator = entries.reduce((sum, entry) => sum + entry.weight, 0);
  let score = null;
  if (entries.length && denominator > 0) {
    if (state.customBoardAggregator === "geometric") {
      score = Math.exp(entries.reduce((sum, entry) => (
        sum + Math.log(Math.max(entry.value, 0) + 1) * entry.weight
      ), 0) / denominator) - 1;
    } else if (state.customBoardAggregator === "weakest") {
      score = Math.min(...entries.map((entry) => entry.value));
    } else {
      score = entries.reduce((sum, entry) => sum + entry.value * entry.weight, 0) / denominator;
    }
  }
  return {
    score,
    displayScore: score,
    scoreBarValue: score,
    customPublicationRanking: true,
    coverage: entries.length,
    coverageLabel: `${entries.length}/${customBoardOrder.length}`,
    availableWeight: denominator,
    scoreMeta: tr(`customBoardAggregators.${state.customBoardAggregator}`),
  };
}

function weightedMedianValue(entries) {
  const sorted = [...entries].sort((a, b) => a.value - b.value);
  const total = sorted.reduce((sum, entry) => sum + entry.weight, 0);
  let cumulative = 0;
  for (let index = 0; index < sorted.length; index += 1) {
    const entry = sorted[index];
    cumulative += entry.weight;
    if (cumulative === total / 2 && sorted[index + 1]) {
      return (entry.value + sorted[index + 1].value) / 2;
    }
    if (cumulative >= total / 2) return entry.value;
  }
  return sorted.at(-1)?.value ?? null;
}

function rankingPopulationSize() {
  const configured = Number(state.data?.leaderboard?.populationSize);
  if (Number.isFinite(configured) && configured > 1) return configured;
  const count = (state.data?.models || []).filter((model) => model.rankingProfile).length;
  return Math.max(count, 2);
}

function scoreModelForBenchmarkWeights(model) {
  const availableEntries = [];
  const entries = [];
  let denominator = 0;
  let availableWeight = 0;
  let missingWeight = 0;
  let coverage = 0;
  let selected = 0;
  let selectedWeight = 0;

  for (const group of customMetricGroups()) {
    const weight = Number(state.customWeights[group.id] || 0);
    if (weight <= 0) continue;
    selected += 1;
    selectedWeight += weight;
    const value = customMetricGroupValue(model, group, state.customNormalizationMethod);
    if (Number.isFinite(value)) {
      availableEntries.push({ value, weight });
      entries.push({ value, weight });
      denominator += weight;
      availableWeight += weight;
      coverage += 1;
    } else {
      entries.push({ value: 0, weight });
      missingWeight += weight;
    }
  }

  const coverageRatio = selected > 0 ? (coverage / selected) * 100 : 0;
  const minCoverage = clamp(Number(state.customMinCoveragePct || 0), 0, 100);
  const availableScore = denominator > 0 && selected > 0 && coverageRatio >= minCoverage
    ? customAggregateScore(availableEntries, denominator, state.customCalculationMethod, state.customNormalizationMethod)
    : null;
  let score = availableScore;
  const penaltyRatio = clamp(Number(state.customPenaltyMax || 0), 0, 100) / 100;
  const zeroScore = customAggregateScore(entries, selectedWeight, state.customCalculationMethod, state.customNormalizationMethod);
  const weightCoverageRatio = selectedWeight > 0 ? availableWeight / selectedWeight : 0;
  const coverageExponent = Math.max(Number(state.customCoverageDiscountExponent || 0), 0);
  if (state.customMissingBaseMode === "weakPrior" && selectedWeight > 0 && coverageRatio >= minCoverage) {
    const priorRatio = clamp(Number(state.customWeakPriorRatio || 35), 0, 100) / 100;
    const priorEntries = [];
    for (const group of customMetricGroups()) {
      const weight = Number(state.customWeights[group.id] || 0);
      if (weight <= 0) continue;
      const value = customMetricGroupValue(model, group, state.customNormalizationMethod);
      const priorValue = customMetricGroupPriorValue(group, state.customNormalizationMethod, priorRatio);
      priorEntries.push({ value: Number.isFinite(value) ? value : priorValue, weight });
    }
    score = customAggregateScore(priorEntries, selectedWeight, state.customCalculationMethod, state.customNormalizationMethod);
  }
  if (Number.isFinite(score) && coverageExponent > 0) {
    score *= weightCoverageRatio ** coverageExponent;
  }
  if (Number.isFinite(score) && penaltyRatio > 0 && selectedWeight > 0) {
    score += (zeroScore - score) * penaltyRatio;
  }
  if (!Number.isFinite(score) && penaltyRatio >= 1 && coverageRatio >= minCoverage && Number.isFinite(zeroScore)) score = zeroScore;
  return {
    score,
    customPublicationRanking: true,
    coverage,
    coverageLabel: `${coverage}/${selected} · ${formatTrimmed(coverageRatio, 0)}%`,
    availableWeight,
    scoreMeta: `${formatNumber(availableWeight)}w · ${formatTrimmed(coverageRatio, 0)}%`,
  };
}

function customAggregateScore(entries, denominator, method = "arithmetic", normalization = "raw") {
  if (!Number.isFinite(denominator) || denominator <= 0 || !entries.length) return null;
  const score = aggregateScoreEntries(entries, denominator, method);
  return scaleAggregateScore(score, normalization);
}

function aggregateScoreEntries(entries, denominator, method = "arithmetic") {
  if (!Number.isFinite(denominator) || denominator <= 0 || !entries.length) return null;
  let score;
  if (method === "geometric") {
    const weightedLogScore = entries.reduce((sum, entry) => {
      const value = Math.max(Number(entry.value) || 0, 0);
      return sum + Math.log(value + 1) * Number(entry.weight || 0);
    }, 0);
    score = Math.exp(weightedLogScore / denominator) - 1;
  } else {
    const weightedScore = entries.reduce((sum, entry) => (
      sum + (Number(entry.value) || 0) * Number(entry.weight || 0)
    ), 0);
    score = weightedScore / denominator;
  }
  return score;
}

function scoreValueForMetric(metricKey, rawValue, normalization = "raw") {
  if (!Number.isFinite(rawValue)) return null;
  if (normalization !== "relative-best") return rawValue;
  const baseline = metricBaseline(metricKey);
  if (!Number.isFinite(baseline) || baseline <= 0) return 0;
  return Math.max(rawValue, 0) / baseline;
}

function metricBaseline(metricKey) {
  const payloadBaseline = Number(state.data.metricBaselines?.[metricKey]);
  if (Number.isFinite(payloadBaseline)) return payloadBaseline;
  const values = (state.data.models || [])
    .map((model) => Number(model.scores?.[metricKey]))
    .filter(Number.isFinite);
  return values.length ? Math.max(...values) : null;
}

function scaleAggregateScore(score, normalization = "raw") {
  if (!Number.isFinite(score)) return null;
  if (normalization !== "relative-best") return score;
  return score * aaIntelligenceScoreBaseline();
}

function aaIntelligenceScoreBaseline() {
  const payloadBaseline = Number(state.data.scoreBaselines?.aaIntelligenceMax);
  if (Number.isFinite(payloadBaseline)) return payloadBaseline;
  const values = (state.data.models || [])
    .map((model) => Number(model.aa?.["aa-intelligence"]))
    .filter(Number.isFinite);
  return values.length ? Math.max(...values) : 100;
}

function matchesQuery(model) {
  if (!state.query) return true;
  const haystack = `${model.model} ${model.creator} ${model.slug}`.toLowerCase();
  return haystack.includes(state.query);
}

function matchesSourceFilter(model) {
  if (state.sourceFilter === "all") return true;
  return sourceType(model) === state.sourceFilter;
}

function dedupeByBestVariant(models) {
  const best = new Map();
  for (const model of models) {
    const current = best.get(model.variantGroup);
    if (!current || isPreferredVariant(model, current)) {
      best.set(model.variantGroup, model);
    }
  }
  return [...best.values()];
}

function isPreferredVariant(candidate, current) {
  const candidatePriority = Number(candidate.variantPriority || 0);
  const currentPriority = Number(current.variantPriority || 0);
  if (candidatePriority !== currentPriority) {
    return candidatePriority > currentPriority;
  }
  return candidate.score > current.score;
}

function modelDisplayScore(model) {
  return Number.isFinite(model?.displayScore) ? model.displayScore : model?.score;
}

function modelScoreBarValue(model) {
  const value = Number.isFinite(model?.scoreBarValue) ? model.scoreBarValue : model?.score;
  return clamp(Number(value) || 0, 0, 100);
}

function rankRows(models) {
  if (models.length && models.every((model) => model.precomputedRanking)) {
    return [...models]
      .sort((a, b) => a.publicationRank - b.publicationRank || a.model.localeCompare(b.model))
      .map((model) => ({ ...model, rank: model.publicationRank }));
  }
  const sorted = [...models].sort(compareRankingRows);
  let previousScore = null;
  let currentRank = 0;
  const evidenceRows = sorted.map((model, index) => {
    if (model.customPublicationRanking || previousScore === null || model.score !== previousScore) {
      currentRank = index + 1;
      previousScore = model.score;
    }
    return {
      ...model,
      rank: currentRank,
      ...(model.customPublicationRanking ? { evidenceRank: currentRank } : {}),
    };
  });
  return evidenceRows.some((model) => model.customPublicationRanking)
    ? applyCustomPublicationLayer(evidenceRows)
    : evidenceRows;
}

function compareRankingRows(a, b) {
  const scoreDifference = b.score - a.score;
  if (scoreDifference) return scoreDifference;
  if (a.customMethodRanking && b.customMethodRanking) {
    const worstDifference = Number(a.customRankMax) - Number(b.customRankMax);
    if (worstDifference) return worstDifference;
    const bestDifference = Number(a.customRankMin) - Number(b.customRankMin);
    if (bestDifference) return bestDifference;
  }
  return String(a.modelKey || a.slug || a.model).localeCompare(String(b.modelKey || b.slug || b.model));
}

function applyCustomPublicationLayer(evidenceRows) {
  const fable = evidenceRows.find((model) => model.slug === "claude-fable-5")
    || evidenceRows.find((model) => /\bfable[ -]?5\b/i.test(`${model.model} ${model.variantGroup}`));
  const sol = evidenceRows.find((model) => model.variantGroup === "gpt 5 6 sol")
    || evidenceRows.find((model) => model.slug === "gpt-5-6-sol")
    || evidenceRows.find((model) => /\bgpt[ -]?5[.-]?6[ -]?sol\b/i.test(`${model.model} ${model.variantGroup}`));
  if (!fable || !sol) return evidenceRows;
  const anchors = [fable, sol];
  const anchorIds = new Set(anchors.map(modelRouteId));
  return [...anchors, ...evidenceRows.filter((model) => !anchorIds.has(modelRouteId(model)))]
    .map((model, index) => ({
      ...model,
      publicationRank: index + 1,
      rank: index + 1,
    }));
}

function scoreHeaderKeyForPreset(preset) {
  if (preset?.kind === "precomputed-ranking") return "headers.rankMean";
  if (state.presetId === "custom" && state.customToolMode === "method-rank") return "headers.rankMean";
  return "headers.score";
}

function methodRankTitle(evidenceRank) {
  return Number.isFinite(evidenceRank) ? `${tr("evidenceRankLabel")} #${evidenceRank}` : tr("notAvailable");
}

function renderSummary(filteredCount, visibleCount, scoredCount, preset) {
  const removed = filteredCount - visibleCount;
  const dedupeLabel = state.dedupe
    ? `${escapeHtml(tr("removedPrefix"))} <strong>${removed}</strong> ${escapeHtml(tr("removedSuffix"))}`
    : escapeHtml(tr("allTiers"));
  els.summaryRow.innerHTML = `
    <span><strong>${visibleCount}</strong> ${escapeHtml(tr("rankingItems"))}</span>
    <span><strong>${scoredCount}</strong> ${escapeHtml(tr("scorableModels"))}</span>
    <span>${dedupeLabel}</span>
    <span>${escapeHtml(tr("sourceFilter"))}: <strong>${escapeHtml(tr(`sourceFilters.${state.sourceFilter}`))}</strong></span>
    <a href="${escapeHtml(methodologyPageHref)}">${escapeHtml(tr("methodologyLink"))}</a>
  `;
}

function resetCustomConfiguration() {
  state.customToolMode = "method-rank";
  state.customMethodWeights = { rasch: 0, sparseRasch: 30, twopl: 70, denseRasch: 0 };
  state.customMethodAggregator = "mean";
  state.customBoardWeights = Object.fromEntries(customBoardOrder.map((boardId) => [boardId, 20]));
  state.customBoardAggregator = "arithmetic";
  state.customWeightPresetId = "benchmark-lab";
  state.customCalculationMethod = "geometric";
  state.customNormalizationMethod = "relative-best";
  state.customWeights = customWeightsForPreset(state.customWeightPresetId);
  applyMissingModePreset("coverage025");
}

function applyMissingModePreset(mode) {
  const preset = missingModePresets[mode] || missingModePresets.coverage025;
  state.customMissingMode = mode;
  state.customMissingBaseMode = mode;
  state.customPenaltyMax = preset.penalty;
  state.customMinCoveragePct = preset.minCoverage;
  state.customCoverageDiscountExponent = preset.coverageDiscountExponent;
  state.customWeakPriorRatio = preset.weakPriorRatio;
}

function syncMissingModePreset() {
  state.customMissingMode = matchingMissingModePreset() || "manual";
}

function matchingMissingModePreset() {
  return missingModePresetOrder.find((mode) => {
    const preset = missingModePresets[mode];
    return mode === state.customMissingBaseMode
      && Number(preset.penalty) === Number(state.customPenaltyMax)
      && Number(preset.minCoverage) === Number(state.customMinCoveragePct)
      && Number(preset.coverageDiscountExponent || 0) === Number(state.customCoverageDiscountExponent || 0)
      && Number(preset.weakPriorRatio || 0) === Number(state.customWeakPriorRatio || 0);
  });
}

function customWeightsForPreset(presetId) {
  const weights = Object.fromEntries(customMetricGroups().map((group) => [group.id, 0]));
  const preset = customWeightPresetDefinition(presetId);
  if (preset?.weights) {
    for (const group of customMetricGroups()) {
      weights[group.id] = Math.max(...group.metrics.map((metric) => Number(preset.weights[metric.key] || 0)), 0);
    }
    return weights;
  }

  const groups = customMetricGroups().filter((group) => customWeightPresetMatchesGroup(presetId, group));
  const weight = groups.length > 0 ? 100 / groups.length : 0;
  for (const group of groups) weights[group.id] = weight;
  return weights;
}

function customWeightPresetMetricCount(presetId) {
  return Object.values(customWeightsForPreset(presetId)).filter((weight) => weight > 0).length;
}

function customWeightPresetMatchesGroup(presetId, group) {
  const haystack = group.metrics
    .map((metric) => `${metric.key} ${metric.label} ${metric.category || ""}`)
    .join(" ")
    .toLowerCase();
  if (presetId === "aa-intelligence") {
    return group.metrics.some((metric) => !String(metric.key).startsWith("benchmark:"));
  }
  if (presetId === "aa-coding") {
    return /\b(coding|code|swe|scicode|livecodebench|terminal|repository|software)\b/.test(haystack);
  }
  if (presetId === "aa-agentic") {
    return /\b(agent|agentic|tool|computer|workflow|browse|search|gdpval|terminal|tau|apex|itbench|mcp|osworld|bfcl|finance)\b/.test(haystack);
  }
  return false;
}

function sourceMetricKeys(source) {
  const knownMetrics = new Set(state.data.metrics.map((metric) => metric.key));
  return (source.relatedMetrics || []).filter((key) => knownMetrics.has(key));
}

function renderWeights() {
  els.weightsGrid.innerHTML = `
    <section class="weight-group custom-tool-selector">
      <div class="weight-group-head custom-tool-head">
        <div>
          <h3>${escapeHtml(tr("customToolTitle"))}</h3>
          <p>${escapeHtml(tr("customToolSubtitle"))}</p>
        </div>
        <div class="custom-action-toolbar" role="group" aria-label="${escapeHtml(tr("customToolTitle"))}">
          ${["equalize", "normalize", "clear", "restore", "export"].map((action) => `
            <button type="button" data-custom-action="${action}">${escapeHtml(tr(`customActions.${action}`))}</button>
          `).join("")}
          <span class="custom-export-status" data-custom-export-status aria-live="polite"></span>
        </div>
      </div>
      <div class="custom-tool-tabs" role="tablist">
        ${customToolModeOrder.map((mode) => `
          <button type="button" role="tab" data-custom-tool-mode="${mode}" aria-selected="${mode === state.customToolMode}">
            <strong>${escapeHtml(tr(`customToolModes.${customToolTranslationId(mode)}`))}</strong>
            <span>${escapeHtml(tr(`customToolDescriptions.${customToolTranslationId(mode)}`))}</span>
          </button>
        `).join("")}
      </div>
    </section>
    <div class="custom-mode-body" data-custom-mode-body></div>
  `;
  bindCustomToolChrome();
  const body = els.weightsGrid.querySelector("[data-custom-mode-body]");
  if (state.customToolMode === "method-rank") {
    renderSimpleCustomWeights(body, {
      ids: customMethodOrder,
      weights: state.customMethodWeights,
      weightKind: "method",
      title: tr("customMethodWeightsTitle"),
      subtitle: tr("customMethodWeightsSubtitle"),
      aggregators: customMethodAggregatorOrder,
      selectedAggregator: state.customMethodAggregator,
    });
    return;
  }
  if (state.customToolMode === "board-score") {
    renderSimpleCustomWeights(body, {
      ids: customBoardOrder,
      weights: state.customBoardWeights,
      weightKind: "board",
      title: tr("customBoardWeightsTitle"),
      subtitle: tr("customBoardWeightsSubtitle"),
      aggregators: customBoardAggregatorOrder,
      selectedAggregator: state.customBoardAggregator,
    });
    return;
  }
  renderBenchmarkWeightLab(body);
}

function customWeightPresetDefinition(presetId) {
  if (presetId === "benchmark-lab") return state.data.presets.custom;
  if (presetId === customManualWeightPresetId) return null;
  return state.data.presets[presetId];
}

function customToolTranslationId(mode) {
  return {
    "method-rank": "methodRank",
    "board-score": "boardScore",
    "benchmark-lab": "benchmarkLab",
  }[mode] || "methodRank";
}

function bindCustomToolChrome() {
  els.weightsGrid.querySelectorAll("[data-custom-tool-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      state.customToolMode = button.dataset.customToolMode;
      renderWeights();
      renderResults(state.data.presets.custom);
    });
  });
  els.weightsGrid.querySelectorAll("[data-custom-action]").forEach((button) => {
    button.addEventListener("click", () => handleCustomAction(button.dataset.customAction));
  });
}

function renderSimpleCustomWeights(target, options) {
  const total = Object.values(options.weights).reduce((sum, value) => sum + Math.max(Number(value || 0), 0), 0);
  const isMethod = options.weightKind === "method";
  target.innerHTML = `
    <section class="weight-group simple-custom-weight-group">
      <div class="weight-group-head">
        <div>
          <h3>${escapeHtml(options.title)}</h3>
          <p>${escapeHtml(options.subtitle)}</p>
        </div>
        <p class="custom-weight-total" data-custom-weight-total>${escapeHtml(tr("customWeightSum", { total: formatWeight(total) }))}</p>
      </div>
      <div class="custom-aggregator-row">
        <span class="control-label">${escapeHtml(tr("customAggregatorTitle"))}</span>
        <div class="segmented-control custom-aggregator-controls" style="--option-count: ${options.aggregators.length}">
          ${options.aggregators.map((aggregator) => `
            <button type="button" data-custom-aggregator="${aggregator}" aria-pressed="${aggregator === options.selectedAggregator}">
              ${escapeHtml(tr(`${isMethod ? "customMethodAggregators" : "customBoardAggregators"}.${aggregator}`))}
            </button>
          `).join("")}
        </div>
      </div>
      <div class="custom-simple-weight-grid">
        ${options.ids.map((id) => `
          <label class="custom-simple-weight">
            <span>
              <strong>${escapeHtml(customWeightItemLabel(id, options.weightKind))}</strong>
              <em>${escapeHtml(isMethod ? tr("evidenceRankLabel") : customBoardEvidenceMeta(id))}</em>
            </span>
            <input type="range" min="0" max="100" step="0.1" value="${escapeHtml(options.weights[id] || 0)}" data-simple-weight="${escapeHtml(id)}" />
            <output>${escapeHtml(formatWeight(options.weights[id] || 0))}</output>
          </label>
        `).join("")}
      </div>
      <p class="publication-layer-note">${escapeHtml(tr("publicationLayerNote"))}</p>
    </section>
  `;
  target.querySelectorAll("[data-custom-aggregator]").forEach((button) => {
    button.addEventListener("click", () => {
      if (isMethod) state.customMethodAggregator = button.dataset.customAggregator;
      else state.customBoardAggregator = button.dataset.customAggregator;
      renderWeights();
      renderResults(state.data.presets.custom);
    });
  });
  target.querySelectorAll("[data-simple-weight]").forEach((input) => {
    input.addEventListener("input", (event) => {
      const weights = isMethod ? state.customMethodWeights : state.customBoardWeights;
      weights[event.target.dataset.simpleWeight] = Number(event.target.value);
      event.target.closest(".custom-simple-weight").querySelector("output").value = formatWeight(event.target.value);
      updateSimpleCustomWeightTotal(target, weights);
    });
    input.addEventListener("change", () => renderResults(state.data.presets.custom));
  });
}

function customWeightItemLabel(id, kind) {
  if (kind === "method") return tr(`customMethodNames.${id}`);
  const key = {
    coding: "coding",
    "agentic-tool-work": "agenticToolWork",
    "hard-reasoning": "hardReasoning",
    "knowledge-science": "knowledgeScience",
    "instruction-context": "instructionContext",
  }[id];
  return tr(`customBoardNames.${key}`);
}

function customBoardEvidenceMeta(boardId) {
  const size = Number(state.data?.leaderboard?.boardItemPoolSizes?.[boardId]);
  return Number.isFinite(size) ? `${size} items` : "IRT";
}

function updateSimpleCustomWeightTotal(target, weights) {
  const total = Object.values(weights).reduce((sum, value) => sum + Math.max(Number(value || 0), 0), 0);
  const output = target.querySelector("[data-custom-weight-total]");
  if (output) output.textContent = tr("customWeightSum", { total: formatWeight(total) });
}

function renderBenchmarkWeightLab(target) {
  target.innerHTML = `
    <section class="weight-group custom-weight-preset-group">
      <div class="weight-group-head">
        <h3>${escapeHtml(tr("customWeightPresetTitle"))}</h3>
        <p>${escapeHtml(tr("customWeightPresetSubtitle"))}</p>
      </div>
      <div class="custom-weight-preset-controls" data-custom-weight-presets></div>
    </section>
    <section class="weight-group missing-mode-group">
      <div class="weight-group-head">
        <h3>${escapeHtml(tr("missingModeTitle"))}</h3>
        <p>${escapeHtml(tr("missingModeSubtitle"))}</p>
      </div>
      <div class="missing-mode-controls" data-missing-mode-controls></div>
    </section>
    <section class="weight-group">
      <div class="weight-group-head metric-weight-head">
        <div>
          <h3>${escapeHtml(tr("metricWeightsTitle"))}</h3>
          <p>${escapeHtml(tr("metricWeightsSubtitle"))}</p>
        </div>
        <label class="metric-coverage-filter">
          <span>${escapeHtml(tr("metricCoverageFilterLabel"))}</span>
          <select data-coverage-filter>
            ${metricCoverageFilterOptions.map((count) => `
              <option value="${count}" ${count === state.customMinMetricCoverage ? "selected" : ""}>
                ${escapeHtml(count === 0 ? tr("metricCoverageFilterAll") : tr("metricCoverageFilterOption", { count }))}
              </option>
            `).join("")}
          </select>
        </label>
      </div>
      <div class="metric-filter-summary" data-coverage-filter-summary></div>
      <div class="metric-weight-controls" data-weight-controls="metrics"></div>
    </section>
    <p class="publication-layer-note">${escapeHtml(tr("publicationLayerNote"))}</p>
  `;
  renderCustomWeightPresetControls(target.querySelector("[data-custom-weight-presets]"));
  renderMissingModeControls(target.querySelector("[data-missing-mode-controls]"));
  const metricTarget = target.querySelector('[data-weight-controls="metrics"]');
  const coverageSelect = target.querySelector("[data-coverage-filter]");
  const groups = customMetricGroups()
    .sort((a, b) => (
      b.coverage - a.coverage
      || Number(b.defaultWeight || 0) - Number(a.defaultWeight || 0)
      || a.label.localeCompare(b.label)
    ));
  const visibleGroups = groups.filter((group) => group.coverage >= state.customMinMetricCoverage);
  const hiddenCount = groups.length - visibleGroups.length;
  const summary = target.querySelector("[data-coverage-filter-summary]");
  if (summary) {
    summary.textContent = tr("metricCoverageFilterSummary", {
      hidden: hiddenCount,
      visible: visibleGroups.length,
      total: groups.length,
    });
  }
  if (coverageSelect) {
    coverageSelect.addEventListener("change", (event) => {
      state.customMinMetricCoverage = Number(event.target.value);
      renderWeights();
    });
  }
  if (visibleGroups.length === 0) {
    metricTarget.innerHTML = `<div class="empty metric-filter-empty">${escapeHtml(tr("metricCoverageFilterEmpty"))}</div>`;
    return;
  }
  for (const group of visibleGroups) {
    const fragment = els.metricTemplate.content.cloneNode(true);
    const labelText = fragment.querySelector("span");
    const input = fragment.querySelector("input");
    const output = fragment.querySelector("output");
    labelText.className = "metric-weight-label";
    labelText.innerHTML = `
      <a class="metric-weight-link" href="${escapeHtml(benchmarkHref(group.metrics[0].key))}">
        <strong>${escapeHtml(group.label)}</strong>
      </a>
      <em>${escapeHtml(tr("metricGroupMeta", { count: group.coverage, metrics: group.metrics.length }))}</em>
    `;
    input.dataset.metricGroup = group.id;
    input.value = state.customWeights[group.id] ?? group.defaultWeight;
    output.value = formatWeight(input.value);
    input.addEventListener("input", (event) => {
      state.customWeights[event.target.dataset.metricGroup] = Number(event.target.value);
      state.customWeightPresetId = customManualWeightPresetId;
      updateCustomWeightPresetSelection();
      output.value = formatWeight(event.target.value);
    });
    input.addEventListener("change", () => {
      renderResults(state.data.presets.custom);
    });
    metricTarget.append(fragment);
  }
}

function handleCustomAction(action) {
  if (action === "export") {
    exportCustomConfiguration();
    return;
  }
  const weights = activeCustomWeights();
  if (action === "equalize") {
    const keys = Object.keys(weights);
    const value = keys.length ? 100 / keys.length : 0;
    keys.forEach((key) => { weights[key] = value; });
  } else if (action === "normalize") {
    const total = Object.values(weights).reduce((sum, value) => sum + Math.max(Number(value || 0), 0), 0);
    if (total > 0) Object.keys(weights).forEach((key) => { weights[key] = Math.max(Number(weights[key] || 0), 0) * 100 / total; });
  } else if (action === "clear") {
    Object.keys(weights).forEach((key) => { weights[key] = 0; });
  } else if (action === "restore") {
    restoreActiveCustomDefaults();
  }
  if (state.customToolMode === "benchmark-lab") state.customWeightPresetId = customManualWeightPresetId;
  renderWeights();
  renderResults(state.data.presets.custom);
}

function activeCustomWeights() {
  if (state.customToolMode === "method-rank") return state.customMethodWeights;
  if (state.customToolMode === "board-score") return state.customBoardWeights;
  return state.customWeights;
}

function restoreActiveCustomDefaults() {
  if (state.customToolMode === "method-rank") {
    state.customMethodWeights = { rasch: 0, sparseRasch: 30, twopl: 70, denseRasch: 0 };
    state.customMethodAggregator = "mean";
  } else if (state.customToolMode === "board-score") {
    state.customBoardWeights = Object.fromEntries(customBoardOrder.map((boardId) => [boardId, 20]));
    state.customBoardAggregator = "arithmetic";
  } else {
    state.customWeightPresetId = "benchmark-lab";
    state.customWeights = customWeightsForPreset(state.customWeightPresetId);
    state.customCalculationMethod = "geometric";
    state.customNormalizationMethod = "relative-best";
    applyMissingModePreset("coverage025");
  }
}

function exportCustomConfiguration() {
  const payload = {
    version: 1,
    toolMode: state.customToolMode,
    methodRank: { aggregator: state.customMethodAggregator, weights: state.customMethodWeights },
    boardScore: { aggregator: state.customBoardAggregator, weights: state.customBoardWeights },
    benchmarkLab: {
      weightPreset: state.customWeightPresetId,
      calculation: state.customCalculationMethod,
      normalization: state.customNormalizationMethod,
      missingMode: state.customMissingMode,
      missingBaseMode: state.customMissingBaseMode,
      penaltyMax: state.customPenaltyMax,
      coverageDiscountExponent: state.customCoverageDiscountExponent,
      weakPriorRatio: state.customWeakPriorRatio,
      minCoveragePct: state.customMinCoveragePct,
      weights: state.customWeights,
    },
    publicationLayer: ["Claude Fable 5", "GPT-5.6 Sol"],
  };
  const json = `${JSON.stringify(payload, null, 2)}\n`;
  if (navigator.clipboard?.writeText) navigator.clipboard.writeText(json).catch(() => {});
  const blob = new Blob([json], { type: "application/json" });
  const href = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = href;
  link.download = `ainsights-custom-${state.customToolMode}.json`;
  link.click();
  URL.revokeObjectURL(href);
  const status = els.weightsGrid.querySelector("[data-custom-export-status]");
  if (status) status.textContent = tr("customActions.exported");
}

function renderCustomWeightPresetControls(target) {
  target.innerHTML = customWeightPresetOrder.map((id) => `
    <button class="weight-preset-button" type="button" data-custom-weight-preset="${escapeHtml(id)}" aria-pressed="${id === state.customWeightPresetId}">
      <strong>${escapeHtml(presetLabel(id))}</strong>
      <em>${escapeHtml(tr("customWeightPresetMeta", { count: customWeightPresetMetricCount(id) }))}</em>
    </button>
  `).join("");
  target.querySelectorAll("[data-custom-weight-preset]").forEach((button) => {
    button.addEventListener("click", () => {
      state.customWeightPresetId = button.dataset.customWeightPreset;
      state.customWeights = customWeightsForPreset(state.customWeightPresetId);
      renderWeights();
      renderResults(state.data.presets.custom);
    });
  });
}

function updateCustomWeightPresetSelection() {
  document.querySelectorAll("[data-custom-weight-preset]").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.customWeightPreset === state.customWeightPresetId));
  });
}

function renderMissingModeControls(target) {
  target.innerHTML = `
    <div class="custom-config-grid">
      <div class="custom-setting-block">
        <span class="control-label">${escapeHtml(tr("normalizationMethodTitle"))}</span>
        <div class="segmented-control normalization-method-controls" data-normalization-method-controls style="--option-count: ${customNormalizationMethodOrder.length}">
          ${customNormalizationMethodOrder.map((method) => `
            <button type="button" data-normalization-method="${escapeHtml(method)}" aria-pressed="${method === state.customNormalizationMethod}">
              ${escapeHtml(tr(`normalizationMethods.${method}`))}
            </button>
          `).join("")}
        </div>
        <p>${escapeHtml(tr("normalizationMethodHint"))}</p>
      </div>
      <div class="custom-setting-block">
        <span class="control-label">${escapeHtml(tr("calculationMethodTitle"))}</span>
        <div class="segmented-control calculation-method-controls" data-calculation-method-controls style="--option-count: ${customCalculationMethodOrder.length}">
          ${customCalculationMethodOrder.map((method) => `
            <button type="button" data-calculation-method="${escapeHtml(method)}" aria-pressed="${method === state.customCalculationMethod}">
              ${escapeHtml(tr(`meanMethods.${method}`))}
            </button>
          `).join("")}
        </div>
        <p>${escapeHtml(tr("calculationMethodHint"))}</p>
      </div>
      <div class="custom-setting-block">
        <span class="control-label">${escapeHtml(tr("missingPresetTitle"))}</span>
        <div class="segmented-control" data-missing-preset style="--option-count: ${missingModePresetOrder.length}">
          ${missingModePresetOrder.map((mode) => `
            <button type="button" data-missing-mode="${escapeHtml(mode)}" aria-pressed="${mode === state.customMissingMode}">
              ${escapeHtml(tr(`missingModes.${mode}`))}
            </button>
          `).join("")}
        </div>
        <p class="custom-strategy-status">
          ${escapeHtml(tr("currentCustomStrategy"))}: <strong data-custom-strategy-label>${escapeHtml(customMissingModeLabel())}</strong>
        </p>
      </div>
      <label class="range-setting">
        <span class="range-setting-head">
          <span>${escapeHtml(tr("penaltyLabel"))}</span>
          <output>${escapeHtml(formatWeight(state.customPenaltyMax))}</output>
        </span>
        <input type="range" min="0" max="100" step="0.5" value="${escapeHtml(state.customPenaltyMax)}" data-custom-penalty />
        <em>${escapeHtml(tr("penaltyHint"))}</em>
      </label>
      <label class="range-setting">
        <span class="range-setting-head">
          <span>${escapeHtml(tr("minCoverageLabel"))}</span>
          <output>${escapeHtml(formatTrimmed(state.customMinCoveragePct, 0))}%</output>
        </span>
        <input type="range" min="0" max="100" step="5" value="${escapeHtml(state.customMinCoveragePct)}" data-custom-min-coverage />
        <em>${escapeHtml(tr("minCoverageHint"))}</em>
      </label>
    </div>
  `;
  target.querySelectorAll("[data-normalization-method]").forEach((button) => {
    button.addEventListener("click", () => {
      state.customNormalizationMethod = button.dataset.normalizationMethod;
      updateNormalizationMethodSelection(target);
      renderResults(state.data.presets.custom);
    });
  });
  target.querySelectorAll("[data-calculation-method]").forEach((button) => {
    button.addEventListener("click", () => {
      state.customCalculationMethod = button.dataset.calculationMethod;
      updateCalculationMethodSelection(target);
      renderResults(state.data.presets.custom);
    });
  });
  target.querySelectorAll("[data-missing-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      applyMissingModePreset(button.dataset.missingMode);
      renderWeights();
      renderResults(state.data.presets.custom);
    });
  });
  const penaltyInput = target.querySelector("[data-custom-penalty]");
  penaltyInput.addEventListener("input", (event) => {
    state.customPenaltyMax = Number(event.target.value);
    syncMissingModePreset();
    event.target.closest(".range-setting").querySelector("output").textContent = formatWeight(state.customPenaltyMax);
    updateMissingModeSelection(target);
  });
  penaltyInput.addEventListener("change", () => {
    renderResults(state.data.presets.custom);
  });
  const coverageInput = target.querySelector("[data-custom-min-coverage]");
  coverageInput.addEventListener("input", (event) => {
    state.customMinCoveragePct = Number(event.target.value);
    syncMissingModePreset();
    event.target.closest(".range-setting").querySelector("output").textContent = `${formatTrimmed(state.customMinCoveragePct, 0)}%`;
    updateMissingModeSelection(target);
  });
  coverageInput.addEventListener("change", () => {
    renderResults(state.data.presets.custom);
  });
}

function updateNormalizationMethodSelection(target) {
  target.querySelectorAll("[data-normalization-method]").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.normalizationMethod === state.customNormalizationMethod));
  });
}

function updateCalculationMethodSelection(target) {
  target.querySelectorAll("[data-calculation-method]").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.calculationMethod === state.customCalculationMethod));
  });
}

function customMissingModeLabel() {
  if (state.customMissingMode === "manual") {
    return `${tr("manualCustomStrategy")} · ${tr(`missingModes.${state.customMissingBaseMode}`)}`;
  }
  return tr(`missingModes.${state.customMissingMode}`);
}

function updateMissingModeSelection(target) {
  target.querySelectorAll("[data-missing-mode]").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.missingMode === state.customMissingMode));
  });
  const label = target.querySelector("[data-custom-strategy-label]");
  if (label) label.textContent = customMissingModeLabel();
}

function customMetricGroups() {
  if (state.customMetricGroupsCache) return state.customMetricGroupsCache;
  const groups = new Map();
  for (const metric of state.data.metrics || []) {
    const id = metricGroupId(metric);
    if (!groups.has(id)) {
      groups.set(id, {
        id,
        label: metric.label,
        metrics: [],
        defaultWeight: 0,
      });
    }
    const group = groups.get(id);
    group.metrics.push(metric);
    group.defaultWeight = Math.max(group.defaultWeight, Number(metric.defaultWeight || 0));
  }
  state.customMetricGroupsCache = [...groups.values()].map((group) => ({
    ...group,
    coverage: metricGroupCoverageCount(group.metrics),
  }));
  return state.customMetricGroupsCache;
}

function metricGroupId(metric) {
  return String(metric.label || metric.key || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function metricGroupCoverageCount(metrics) {
  return (state.data.models || []).filter((model) => (
    metrics.some((metric) => Number.isFinite(model.scores?.[metric.key]))
  )).length;
}

function customMetricGroupValue(model, group, normalization = "raw") {
  const canonicalWeights = state.data.presets.custom?.weights || {};
  const canonicalMetrics = group.metrics.filter((metric) => Number(canonicalWeights[metric.key] || 0) > 0);
  const metrics = canonicalMetrics.length ? canonicalMetrics : group.metrics;
  const values = metrics
    .map((metric) => scoreValueForMetric(metric.key, model.scores?.[metric.key], normalization))
    .filter(Number.isFinite);
  if (values.length === 0) return null;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function customMetricGroupPriorValue(group, normalization, priorRatio) {
  if (normalization === "relative-best") return priorRatio;
  const cacheKey = group.id;
  let baseline = Number(state.customRawPriorBaselineCache[cacheKey]);
  if (!Number.isFinite(baseline)) {
    const values = (state.data.models || [])
      .map((model) => customMetricGroupValue(model, group, "raw"))
      .filter(Number.isFinite);
    baseline = values.length ? Math.max(...values, 0) : 0;
    state.customRawPriorBaselineCache[cacheKey] = baseline;
  }
  return baseline * priorRatio;
}

function renderHome(models, displayModels = models) {
  renderHomeMetrics(models);
  renderLatestModels(displayModels);
  renderTop20Chart(models.slice(0, state.topChartLimit));
  renderCostScatter(models.filter((model) => Number.isFinite(modelCost(model)) && modelCost(model) > 0).slice(0, 28));
  renderScoreBands(models);
  renderProviderChart(models);
  renderSourceExplorer(els.sourceExplorer);
}

function renderProviderTextLink(provider, source = state.page, context = {}) {
  const providerName = provider || tr("unknownCreator");
  return `<a class="provider-text-link" href="${escapeHtml(providerHref(providerName, source, context))}">${escapeHtml(providerName)}</a>`;
}

function renderLatestModels(models) {
  if (!els.latestModels) return;
  const latest = models
    .filter((model) => parsedReleaseTime(model.releaseDate) !== null)
    .sort((a, b) => parsedReleaseTime(b.releaseDate) - parsedReleaseTime(a.releaseDate) || safeScore(b) - safeScore(a))
    .slice(0, 6);
  if (latest.length === 0) {
    els.latestModels.innerHTML = `<div class="empty">${escapeHtml(tr("notAvailable"))}</div>`;
    return;
  }
  els.latestModels.innerHTML = latest.map((model) => `
    <article class="latest-model-card" style="--bar-color: ${providerColor(model)}" data-card-href="${escapeHtml(modelHref(model, "home"))}" role="link" tabindex="0" aria-label="${escapeHtml(`${tr("modelDetails")} ${model.model}`)}">
      <span class="latest-model-top">
        <span class="latest-model-date">${escapeHtml(formatDate(model.releaseDate))}</span>
        <span class="latest-model-compare">${renderCompareEntry(model, "home")}</span>
      </span>
      <span class="latest-model-main">
        ${renderModelIcon(model)}
        <span>
          <strong>${escapeHtml(model.model)}</strong>
          <em>${renderProviderTextLink(model.creator, "home")}</em>
        </span>
      </span>
      <span class="latest-model-meta">
        <span class="latest-model-score">${renderIcon("trophy")}<b>${escapeHtml(formatNumber(modelDisplayScore(model)))}</b></span>
        <span>${escapeHtml(sourceTypeLabel(sourceType(model)))}</span>
      </span>
    </article>
  `).join("");
}

function renderHomeMetrics(models) {
  if (!els.homeMetrics || models.length === 0) return;
  const leader = models[0];
  const topOpen = models.find((model) => sourceType(model) === "open");
  const bestValue = bestValueModel(models);
  const stats = [
    {
      label: tr("homeStats.leader"),
      model: leader,
      meta: `${formatNumber(modelDisplayScore(leader))} · ${leader.creator || tr("unknownCreator")}`,
    },
    {
      label: tr("homeStats.topOpen"),
      model: topOpen,
      meta: topOpen ? `${formatNumber(modelDisplayScore(topOpen))} · ${topOpen.creator || tr("unknownCreator")}` : "—",
    },
    {
      label: tr("homeStats.bestValue"),
      model: bestValue,
      meta: bestValue ? `${formatNumber(modelDisplayScore(bestValue))} · ${formatMoney(modelCost(bestValue))} ${tr("homeStats.perRun")}` : "—",
    },
    {
      label: tr("homeStats.modelCount"),
      value: compactNumber(models.length),
      meta: tr("homeStats.byScore"),
    },
  ];
  els.homeMetrics.innerHTML = stats.map(renderHomeMetric).join("");
}

function renderHomeMetric(stat) {
  if (stat.model) {
    return `
      <article class="home-metric">
        <span class="home-metric-label">${escapeHtml(stat.label)}</span>
        <a class="home-metric-model" href="${escapeHtml(modelHref(stat.model))}">
          ${renderModelIcon(stat.model)}
          <strong>${escapeHtml(stat.model.model)}</strong>
        </a>
        <span class="home-metric-meta">${escapeHtml(stat.meta)}</span>
      </article>
    `;
  }
  return `
    <article class="home-metric">
      <span class="home-metric-label">${escapeHtml(stat.label)}</span>
      <strong class="home-metric-number">${escapeHtml(stat.value)}</strong>
      <span class="home-metric-meta">${escapeHtml(stat.meta)}</span>
    </article>
  `;
}

function renderTop20Chart(models) {
  els.top20Title.textContent = tr("top20Title", { count: models.length });
  els.top20Subtitle.textContent = tr("top20Subtitle");
  if (models.length === 0) {
    els.top20Chart.innerHTML = `<div class="empty">${escapeHtml(tr("empty"))}</div>`;
    return;
  }

  const maxScore = Math.max(...models.map((model) => model.score), 1);
  els.top20Chart.innerHTML = `
    <div class="top-bars" style="--bar-count: ${models.length}">
      ${models.map((model, index) => {
        const width = clamp((model.score / maxScore) * 100, 8, 100);
        const color = providerColor(model, index);
        return `
          <article class="top-bar-item" data-card-href="${escapeHtml(modelHref(model, "home"))}" role="link" tabindex="0" title="${escapeHtml(model.model)}" style="--bar-width: ${width}%; --bar-color: ${color}">
            <span class="top-bar-rank">#${model.rank || index + 1}</span>
            <span class="top-bar-model">
              ${renderModelIcon(model)}
              <span>
                <strong>${escapeHtml(model.model)}</strong>
                <em>${renderProviderTextLink(model.creator, "home")} · ${escapeHtml(sourceTypeLabel(sourceType(model)))}</em>
              </span>
            </span>
            <span class="top-bar-track"><span></span></span>
            <span class="top-bar-value">${formatNumber(modelDisplayScore(model))}</span>
          </article>
        `;
      }).join("")}
    </div>
  `;
}

function renderCostScatter(models) {
  if (models.length < 3) {
    els.costScatter.innerHTML = `<div class="empty">${escapeHtml(tr("noCostData"))}</div>`;
    return;
  }

  const width = 1180;
  const height = 560;
  const margin = { top: 42, right: 220, bottom: 76, left: 210 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const costs = models.map(modelCost);
  const scores = models.map((model) => model.score);
  const minCost = Math.min(...costs);
  const maxCost = Math.max(...costs);
  const xMin = minCost === maxCost ? minCost * 0.8 : minCost * 0.8;
  const xMax = minCost === maxCost ? maxCost * 1.2 + 1 : maxCost * 1.2;
  const logMin = Math.log10(Math.max(xMin, 0.01));
  const logMax = Math.log10(Math.max(xMax, 0.02));
  const yMin = Math.max(0, Math.floor((Math.min(...scores) - 5) / 5) * 5);
  const yMax = Math.min(100, Math.ceil((Math.max(...scores) + 5) / 5) * 5);
  const ySpan = Math.max(yMax - yMin, 1);
  const costThreshold = median(costs);
  const scoreThreshold = median(scores);
  const xFor = (cost) => margin.left + ((Math.log10(Math.max(cost, 0.01)) - logMin) / (logMax - logMin || 1)) * plotWidth;
  const yFor = (score) => margin.top + (1 - ((score - yMin) / ySpan)) * plotHeight;
  const xTicks = logTicks(xMin, xMax);
  const yTicks = linearTicks(yMin, yMax, 5);
  const quadrantX = xFor(costThreshold);
  const quadrantY = yFor(scoreThreshold);
  const points = models.map((model, index) => ({
    model,
    index,
    x: xFor(modelCost(model)),
    y: yFor(model.score),
  }));
  const labelPlacements = scatterLabelPlacements(points, margin, plotWidth, plotHeight, width);
  const providers = [...new Set(models.map((model) => model.creator || tr("unknownCreator")))].slice(0, 10);

  els.costScatter.innerHTML = `
    <div class="scatter-legend">
      <span class="quadrant-key"></span><span>${escapeHtml(tr("attractiveQuadrant"))}</span>
      ${providers.map((provider, index) => `
        <span class="legend-dot" style="--dot-color: ${providerColor({ creator: provider }, index)}"></span><span>${escapeHtml(provider)}</span>
      `).join("")}
    </div>
    <div class="scatter-scroll">
      <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHtml(tr("costScatterTitle"))}">
        <rect class="scatter-plot-bg" x="${margin.left}" y="${margin.top}" width="${plotWidth}" height="${plotHeight}"></rect>
        <rect class="scatter-quadrant" x="${margin.left}" y="${margin.top}" width="${Math.max(0, quadrantX - margin.left)}" height="${Math.max(0, quadrantY - margin.top)}"></rect>
        ${yTicks.map((tick) => {
          const y = yFor(tick);
          return `<line class="scatter-grid" x1="${margin.left}" x2="${width - margin.right}" y1="${y}" y2="${y}"></line><text class="scatter-tick" x="${margin.left - 12}" y="${y + 4}" text-anchor="end">${formatNumber(tick)}</text>`;
        }).join("")}
        ${xTicks.map((tick) => {
          const x = xFor(tick);
          return `<line class="scatter-grid" x1="${x}" x2="${x}" y1="${margin.top}" y2="${height - margin.bottom}"></line><text class="scatter-tick" x="${x}" y="${height - margin.bottom + 24}" text-anchor="middle">${escapeHtml(formatAxisCost(tick))}</text>`;
        }).join("")}
        <line class="scatter-axis" x1="${margin.left}" x2="${width - margin.right}" y1="${height - margin.bottom}" y2="${height - margin.bottom}"></line>
        <line class="scatter-axis" x1="${margin.left}" x2="${margin.left}" y1="${margin.top}" y2="${height - margin.bottom}"></line>
        <text class="scatter-axis-label" x="${margin.left + plotWidth / 2}" y="${height - 18}" text-anchor="middle">${escapeHtml(tr("scatterXAxis"))}</text>
        <text class="scatter-axis-label" transform="translate(22 ${margin.top + plotHeight / 2}) rotate(-90)" text-anchor="middle">${escapeHtml(tr("scatterYAxis"))}</text>
        ${points.map(({ model, index, x, y }) => {
          const placement = labelPlacements.get(model.modelKey);
          return `
            <g class="scatter-point is-labeled">
              ${placement ? `<path class="scatter-leader" d="${placement.path}"></path>` : ""}
              <circle cx="${x}" cy="${y}" r="5.6" fill="${providerColor(model, index)}"></circle>
              <title>${escapeHtml(`${model.model} · ${formatNumber(modelDisplayScore(model))} · ${formatMoney(modelCost(model))}`)}</title>
              ${placement ? `<text class="scatter-label" x="${placement.x}" y="${placement.y}" text-anchor="${placement.anchor}">${escapeHtml(scatterLabelText(model.model))}</text>` : ""}
            </g>
          `;
        }).join("")}
      </svg>
    </div>
  `;
}

function renderScoreBands(models) {
  if (!els.scoreBands) return;
  const bands = [
    { label: "60+", min: 60, max: Infinity },
    { label: "50-60", min: 50, max: 60 },
    { label: "40-50", min: 40, max: 50 },
    { label: "30-40", min: 30, max: 40 },
    { label: "<30", min: -Infinity, max: 30 },
  ].map((band) => ({
    ...band,
    count: models.filter((model) => model.score >= band.min && model.score < band.max).length,
  }));
  const maxCount = Math.max(...bands.map((band) => band.count), 1);
  els.scoreBands.innerHTML = bands.map((band) => `
    <div class="band-row">
      <span>${escapeHtml(band.label)}</span>
      <div class="band-track"><span style="--value: ${(band.count / maxCount) * 100}%"></span></div>
      <strong>${band.count}</strong>
    </div>
  `).join("");
}

function renderProviderChart(models) {
  if (!els.providerChart) return;
  const grouped = new Map();
  for (const model of models) {
    const provider = model.creator || tr("unknownCreator");
    const item = grouped.get(provider) || { provider, count: 0, bestScore: 0, bestModel: null };
    item.count += 1;
    if (!item.bestModel || model.score > item.bestScore) {
      item.bestScore = model.score;
      item.bestModel = model;
    }
    grouped.set(provider, item);
  }
  const rows = [...grouped.values()]
    .sort((a, b) => b.count - a.count || b.bestScore - a.bestScore)
    .slice(0, 10);
  const maxCount = Math.max(...rows.map((row) => row.count), 1);
  els.providerChart.innerHTML = rows.map((row, index) => `
    <a class="provider-row" href="${escapeHtml(providerHref(row.provider))}" style="--bar-color: ${providerColor({ creator: row.provider }, index)}; --value: ${(row.count / maxCount) * 100}%">
      <span class="provider-row-name">
        ${renderProviderCoverageIcon(row)}
        <span>${escapeHtml(row.provider)}</span>
      </span>
      <span class="provider-row-track"><span></span></span>
      <span class="provider-row-metric" title="${escapeHtml(tr("providerModelCount"))}" aria-label="${escapeHtml(tr("providerModelCount"))}">
        ${renderIcon("database")}
        <strong>${row.count}</strong>
      </span>
      <span class="provider-row-metric" title="${escapeHtml(tr("providerBestScore"))}" aria-label="${escapeHtml(tr("providerBestScore"))}">
        ${renderIcon("trophy")}
        <em>${escapeHtml(formatNumber(modelDisplayScore(row.bestModel)))}</em>
      </span>
    </a>
  `).join("");
}

function renderProviderCoverageIcon(row) {
  if (row.bestModel) return renderModelIcon(row.bestModel);
  return renderModelIcon({ creator: row.provider, model: row.provider, modelIcon: { title: row.provider } });
}

function renderSourceExplorer(target, compact = false) {
  if (!target) return;
  target.innerHTML = sourceCardsHtml(compact);
}

function sourceCardsHtml(compact = false, model = null, sources = catalogSources()) {
  return sources.map((source) => {
    const relatedMetrics = sourceMetricKeys(source);
    const coverage = currentSourceCoverage(source, model);
    const status = tr(`sourceWeightStatuses.${source.scoreStatus || (relatedMetrics.length ? "mapped" : "reference")}`);
    return `
    <a class="source-card${compact ? " compact" : ""}" href="${escapeHtml(source.url)}" target="_blank" rel="noreferrer">
      <span class="source-card-icon">${escapeHtml(source.icon || initials(source.label))}</span>
      <span class="source-card-kicker">${escapeHtml(source.category || tr("source"))}</span>
      <strong>${escapeHtml(source.label)}</strong>
      <p>${escapeHtml(compact ? source.focus : `${source.focus} ${source.note || ""}`)}</p>
      <em>${escapeHtml(coverage || `${status} · ${source.coverage || ""}`)}</em>
    </a>
  `;
  }).join("");
}

function currentSourceCoverage(source, model) {
  if (!model) return "";
  const relatedMetrics = sourceMetricKeys(source);
  if (relatedMetrics.length === 0) return source.coverage || "";
  const available = relatedMetrics.filter((key) => Number.isFinite(model.scores?.[key])).length;
  return tr("detailSourceCoverage", { available, total: relatedMetrics.length });
}

function renderSourcesPage() {
  const sources = catalogSources();
  els.sourceOverview.innerHTML = sources.map(renderSourceOverviewCard).join("");
  els.sourceMetricMap.innerHTML = sources.map(renderSourceMetricMapRow).join("");
}

function renderMethodologyPage() {
  if (!els.methodologyDetail) return;
  const zh = state.language === "zh-CN";
  document.title = `${zh ? "AInsights Index 计算方式" : "AInsights Index Methodology"} · ${tr("pageTitle")}`;
  els.methodologyDetail.innerHTML = `
    <section class="methodology-hero">
      <p class="eyebrow">Methodology</p>
      <h2>${escapeHtml(zh ? "AInsights Index 计算方式" : "AInsights Index Methodology")}</h2>
      <p>${escapeHtml(zh
        ? "主榜以等板块 2PL 真实证据名次的 70% 与稀疏 Rasch 证据名次的 30% 加权；覆盖度只决定入榜资格与证据标签，不修改合格模型的真实 IRT 成绩。"
        : "The primary ranking blends observed evidence ranks with 70% Equal-board 2PL and 30% Sparse Rasch. Coverage controls eligibility and evidence labels; it does not modify an eligible model's observed IRT score.")}</p>
    </section>
    <section class="methodology-grid">
      <article class="methodology-card methodology-card-wide">
        <h3>${escapeHtml(zh ? "默认名次" : "Default rank")}</h3>
        <p><code>rank_mean = 0.70 × twopl_evidence_rank + 0.30 × sparse_evidence_rank</code></p>
        <p>${escapeHtml(zh
          ? "先按 rank_mean，再按 2PL 名次、稀疏 Rasch 名次和稳定 ID 排序；所有输入都来自真实 benchmark 成绩。"
          : "Rows sort by rank_mean, then 2PL rank, Sparse Rasch rank, and stable ID; every input comes from observed benchmark results.")}</p>
      </article>
      <article class="methodology-card">
        <h3>Equal-board 2PL / Sparse Rasch</h3>
        <p>${escapeHtml(zh
          ? "等板块 2PL 在成熟 item pool 上匿名学习测试区分度，占默认名次 70%；Sparse Rasch 接纳覆盖较少但更前沿的早期信号，占 30%。"
          : "Equal-board 2PL anonymously learns item discrimination on the mature pool and contributes 70% of the default rank. Sparse Rasch admits earlier frontier signals with thinner coverage and contributes 30%.")}</p>
      </article>
      <article class="methodology-card">
        <h3>Core Rasch / Dense Rasch</h3>
        <p>${escapeHtml(zh
          ? "Core Rasch 与 Dense Rasch 作为敏感性对照；完整排名仍展示 2PL 的独立名次与 Dense Rasch 名次。"
          : "Core Rasch and Dense Rasch are sensitivity comparisons; Full Ranking still shows the standalone 2PL and Dense Rasch ranks.")}</p>
      </article>
      <article class="methodology-card methodology-card-wide">
        <h3>${escapeHtml(zh ? "Item Pool 与敏感性方法" : "Item Pools and Sensitivity Methods")}</h3>
        <div class="methodology-table-wrap">
          <table class="methodology-weight-table methodology-matrix-table">
            <thead><tr><th>${escapeHtml(zh ? "方法" : "Method")}</th><th>${escapeHtml(zh ? "测试准入" : "Item admission")}</th><th>${escapeHtml(zh ? "用途" : "Role")}</th></tr></thead>
            <tbody>
              <tr><td>Core Rasch</td><td>${escapeHtml(zh ? "至少 8 个独立模型 family、3 个 creator" : "At least 8 independent model families and 3 creators")}</td><td>${escapeHtml(zh ? "敏感性对照" : "Sensitivity comparison")}</td></tr>
              <tr><td>Sparse Rasch</td><td>${escapeHtml(zh ? "至少 3 个独立模型 family；1 个 creator 即可" : "At least 3 independent model families; one creator is sufficient")}</td><td>${escapeHtml(zh ? "默认名次 30%" : "30% of the default rank")}</td></tr>
              <tr><td>Equal-board 2PL</td><td>${escapeHtml(zh ? "与 Core Rasch 使用相同 item pool" : "Same pool as Core Rasch")}</td><td>${escapeHtml(zh ? "默认名次 70%；item discrimination 共同向 1 做 ridge，并限制在 0.35–2.5" : "70% of the default rank; item-discrimination ridge toward 1 with bounds of 0.35–2.5")}</td></tr>
              <tr><td>Dense Rasch</td><td>${escapeHtml(zh ? "至少 20 个独立模型 family、3 个 creator" : "At least 20 independent model families and 3 creators")}</td><td>${escapeHtml(zh ? "保守敏感性对照" : "Conservative sensitivity comparison")}</td></tr>
            </tbody>
          </table>
        </div>
      </article>
      <article class="methodology-card methodology-card-wide">
        <h3>${escapeHtml(zh ? "五个等权能力板块" : "Capability Boards")}</h3>
        <p>${escapeHtml(zh
          ? "每种 IRT 方法先在五个板块内独立拟合，再对五个板块做等权算术平均；默认榜没有 40 / 24 / 20 / 8 / 8 权重。"
          : "Each IRT method is fitted independently inside five boards, then the five board scores receive an equal arithmetic mean; the default ranking has no 40 / 24 / 20 / 8 / 8 weighting.")}</p>
        <div class="methodology-table-wrap">
          <table class="methodology-weight-table">
            <thead><tr><th>${escapeHtml(zh ? "板块" : "Board")}</th><th>${escapeHtml(zh ? "方法内占比" : "Share within method")}</th></tr></thead>
            <tbody>
              ${customBoardOrder.map((boardId) => `<tr><td>${escapeHtml(customWeightItemLabel(boardId, "board"))}</td><td>20%</td></tr>`).join("")}
            </tbody>
          </table>
        </div>
      </article>
      <article class="methodology-card methodology-card-wide">
        <h3>${escapeHtml(zh ? "计算公式" : "Calculation Formula")}</h3>
        <p><code>z_ij = theta_i - difficulty_j + error_ij</code></p>
        <p><code>board_score = 100 × Phi(theta_z)</code></p>
        <p>${escapeHtml(zh
          ? "Core、Sparse 与 Dense Rasch 都在各板块拟合连续 Rasch；2PL 在相同成熟 item pool 上匿名学习区分度。每种方法先将五板等权平均得到 evidence rank，再按 2PL 70% / Sparse Rasch 30% 计算 rank_mean；不含命名模型系数或事后模型修正。"
          : "Core, Sparse, and Dense Rasch fit a continuous Rasch model in each board; 2PL anonymously learns discrimination on the same mature item pool. Each method first averages the five boards equally, then rank_mean blends 70% 2PL and 30% Sparse Rasch evidence ranks, without any named-model coefficient or post-hoc model correction.")}</p>
      </article>
      <article class="methodology-card methodology-card-wide">
        <h3>${escapeHtml(zh ? "证据资格与覆盖" : "Evidence Eligibility and Coverage")}</h3>
        <p>${escapeHtml(zh
          ? "每个板块至少需要两个规范化 benchmark family 才能进入某一方法榜；每板至少三个标为 Main，否则合格配置标为 Provisional。证据不足表示不排名，不是按 0 分计算。"
          : "A configuration needs at least two canonical benchmark families in every board to enter a method ranking. At least three in every board earns Main status; another eligible row is Provisional. Insufficient evidence means not ranked, not a score of zero.")}</p>
        <p>${escapeHtml(zh
          ? "覆盖只控制资格和标签，不修改合格模型的真实 IRT 分数；不扣固定缺失分、不插入弱先验，也不从较低同系列模型复制成绩。"
          : "Coverage controls eligibility and labels; it does not modify a qualified model's observed IRT score. There is no fixed missing-score penalty, weak-prior insertion, or score copying from a lower sibling model.")}</p>
      </article>
      <article class="methodology-card">
        <h3>${escapeHtml(zh ? "六轴雷达" : "Radar Profile")}</h3>
        <p>${escapeHtml(zh
          ? "前五轴是等板块 2PL 与 Sparse Rasch 对应板块分的 70/30 加权；第六轴 evidence_coverage_score 按相同 70/30 审计证据广度，永不改变分数或名次。"
          : "The first five axes blend matching Equal-board 2PL and Sparse Rasch board scores at 70/30. The sixth, evidence_coverage_score, audits evidence breadth with the same 70/30 split and never changes a score or rank.")}</p>
      </article>
      <article class="methodology-card">
        <h3>${escapeHtml(zh ? "逐项权重与 Custom 工具" : "Metric Weights and Custom Tools")}</h3>
        <p>${escapeHtml(zh
          ? "默认榜不分配逐项自定义权重。Custom 分别提供四法 evidence rank 混合、五板真实分混合和逐项 Benchmark Lab，并支持等权、归一到 100、清零、恢复与 JSON 导出。"
          : "The default ranking assigns no custom per-benchmark weights. Custom separately offers a four-method evidence-rank mixer, a five-board score mixer, and a per-benchmark lab, with equalize, normalize-to-100, clear, restore, and JSON export actions.")}</p>
      </article>
      <article class="methodology-card methodology-card-wide">
        <h3>${escapeHtml(zh ? "透明发布顺序" : "Transparent publication order")}</h3>
        <p>${escapeHtml(zh
          ? "证据层完成后才发布 Claude Fable 5 #1 与 GPT-5.6 Sol #2。独立保存 evidence_rank、四法证据名次与真实分数，因此发布层不伪装成测量结果；Custom 当前配置只有在两者均有真实可计算结果时才应用该顺序，否则保持证据排序。"
          : "Only after the evidence layer is complete does publication place Claude Fable 5 #1 and GPT-5.6 Sol #2. evidence_rank, all four method evidence ranks, and observed scores remain separately available; a Custom configuration applies this order only when both models have observed, calculable results, otherwise it keeps the evidence order.")}</p>
      </article>
    </section>
  `;
}

function catalogSources() {
  return (state.data.externalSources || []).filter((source) => !isOfficialModelSource(source));
}

function isOfficialModelSource(source) {
  return /^official\b/i.test(String(source.category || ""))
    || /\bofficial\b/i.test(String(source.label || ""));
}

function modelSourceCardsHtml(model) {
  const sources = uniqueSources([
    ...modelOfficialSources(model),
    ...catalogSources().filter((source) => sourceCoversModel(source, model)),
  ]);
  if (sources.length === 0) return `<div class="empty">${escapeHtml(tr("notAvailable"))}</div>`;
  return sourceCardsHtml(true, model, sources);
}

function modelOfficialSources(model) {
  return (state.data.externalSources || [])
    .filter(isOfficialModelSource)
    .filter((source) => sourceCoversModel(source, model));
}

function sourceCoversModel(source, model) {
  if (!source || !model) return false;
  if ((model.externalBenchmarks || []).some((row) => row.sourceId === source.id)) return true;
  const relatedMetrics = sourceMetricKeys(source);
  if (relatedMetrics.some((key) => Number.isFinite(model.scores?.[key]))) return true;
  const modelKeys = [
    model.modelKey,
    model.model,
    model.slug,
    `${model.model} [R]`,
  ].map(sourceMatchKey).filter(Boolean);
  const aliases = [...(source.modelAliases || []), ...(source.modelKeys || [])].map(sourceMatchKey).filter(Boolean);
  return aliases.some((alias) => modelKeys.includes(alias));
}

function uniqueSources(sources) {
  const seen = new Set();
  return sources.filter((source) => {
    const id = source.id || source.url || source.label;
    if (!id || seen.has(id)) return false;
    seen.add(id);
    return true;
  });
}

function sourceMatchKey(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/\[r\]/g, "")
    .replace(/with fallback/g, "")
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function renderSourceOverviewCard(source) {
  const relatedMetrics = sourceMetricKeys(source);
  const modelCoverage = sourceModelCoverageCount(source);
  const resultCount = sourceResultCount(source);
  const status = tr(`sourceWeightStatuses.${source.scoreStatus || (relatedMetrics.length ? "mapped" : "reference")}`);
  return `
    <a class="source-list-card" href="${escapeHtml(source.url)}" target="_blank" rel="noreferrer">
      <span class="source-card-icon">${escapeHtml(source.icon || initials(source.label))}</span>
      <span class="source-card-kicker">${escapeHtml(source.category || tr("source"))}</span>
      <strong>${escapeHtml(source.label)}</strong>
      <p>${escapeHtml(`${source.focus || ""} ${source.note || ""}`.trim())}</p>
      <div class="source-stat-row">
        <span><b>${escapeHtml(String(relatedMetrics.length))}</b>${escapeHtml(tr("sourceStats.metrics"))}</span>
        <span><b>${escapeHtml(String(modelCoverage))}</b>${escapeHtml(tr("sourceStats.models"))}</span>
        <span><b>${escapeHtml(String(resultCount))}</b>${escapeHtml(tr("sourceStats.results"))}</span>
      </div>
      <em>${escapeHtml(status)}</em>
    </a>
  `;
}

function renderSourceMetricMapRow(source) {
  const relatedMetrics = sourceMetricKeys(source).map((key) => metricDefinition(key)).filter((metric) => metric.key);
  const metricChips = relatedMetrics.length
    ? relatedMetrics.map((metric) => `
        <span class="source-metric-chip">
          ${escapeHtml(metric.label)}
          <b>${escapeHtml(tr("metricCoverage", { count: metricGroupCoverageCount([metric]) }))}</b>
        </span>
      `).join("")
    : `<span class="source-metric-chip is-empty">${escapeHtml(source.coverage || tr("notAvailable"))}</span>`;
  return `
    <article class="source-map-row">
      <div>
        <span class="source-card-icon">${escapeHtml(source.icon || initials(source.label))}</span>
        <strong>${escapeHtml(source.label)}</strong>
        <em>${escapeHtml(source.category || tr("source"))}</em>
      </div>
      <div class="source-metric-chip-list">${metricChips}</div>
    </article>
  `;
}

function sourceModelCoverageCount(source) {
  const relatedMetrics = sourceMetricKeys(source);
  return (state.data.models || []).filter((model) => (
    relatedMetrics.some((key) => Number.isFinite(model.scores?.[key]))
    || (model.externalBenchmarks || []).some((row) => row.sourceId === source.id)
  )).length;
}

function sourceResultCount(source) {
  const relatedMetrics = sourceMetricKeys(source);
  const externalRows = (state.data.models || []).reduce((total, model) => (
    total + (model.externalBenchmarks || []).filter((row) => row.sourceId === source.id).length
  ), 0);
  if (externalRows > 0) return externalRows;
  return (state.data.models || []).reduce((total, model) => (
    total + relatedMetrics.filter((key) => Number.isFinite(model.scores?.[key])).length
  ), 0);
}

function renderRankings(models) {
  const viewMode = state.viewMode;
  els.histogramList.hidden = viewMode !== "histogram";
  els.tableRanking.hidden = viewMode !== "table";
  els.textRanking.hidden = viewMode !== "text";

  if (viewMode === "histogram") renderHistogram(models);
  if (viewMode === "table") renderTable(models);
  if (viewMode === "text") renderTextRanking(models);
}

function renderHistogram(models) {
  if (models.length === 0) {
    els.histogramList.innerHTML = `<div class="empty">${escapeHtml(tr("empty"))}</div>`;
    return;
  }
  els.histogramList.innerHTML = models.map(renderHistogramRow).join("");
}

function renderHistogramRow(model) {
  const scoreWidth = modelScoreBarValue(model);
  const displayScore = modelDisplayScore(model);
  return `
    <div class="histogram-row" data-card-href="${escapeHtml(modelHref(model, "ranking"))}" role="link" tabindex="0" aria-label="${escapeHtml(`${tr("modelDetails")} ${model.model}`)}">
      <div class="histogram-rank">#${model.rank}</div>
      <div class="histogram-model">
        ${renderModelIcon(model)}
        <div class="histogram-label">
          <a href="${escapeHtml(modelHref(model))}">${escapeHtml(model.model)}</a>
          <span>${renderProviderTextLink(model.creator, "ranking")} · ${escapeHtml(sourceTypeLabel(sourceType(model)))}</span>
        </div>
      </div>
      <div class="histogram-track" aria-label="${escapeHtml(tr(scoreHeaderKeyForPreset(state.data.presets[state.presetId])))} ${formatNumber(displayScore)}">
        <span class="histogram-fill" style="--value: ${scoreWidth}%"></span>
      </div>
      <div class="histogram-score">${formatNumber(displayScore)}</div>
      ${renderCompareEntry(model, "ranking")}
    </div>
  `;
}

function renderTable(models) {
  if (models.length === 0) {
    els.rankingBody.innerHTML = `<tr><td class="empty" colspan="10">${escapeHtml(tr("empty"))}</td></tr>`;
    return;
  }
  els.rankingBody.innerHTML = models.map(renderRow).join("");
}

function renderRow(model) {
  const scoreWidth = modelScoreBarValue(model);
  const displayScore = modelDisplayScore(model);
  const reason = model.isReasoning ? `<span class="pill">${escapeHtml(tr("reasoning"))}</span>` : "";
  return `
    <tr data-card-href="${escapeHtml(modelHref(model, "ranking"))}" tabindex="0" aria-label="${escapeHtml(`${tr("modelDetails")} ${model.model}`)}">
      <td class="rank-col">${model.rank}</td>
      <td>
        <div class="model-main">
          <div class="model-heading">
            ${renderModelIcon(model)}
            <a class="model-name" href="${escapeHtml(modelHref(model))}">${escapeHtml(model.model)}</a>
          </div>
          <div class="model-meta">
            ${renderProviderTextLink(model.creator, "ranking")}
            ${reason}
            ${renderCompareEntry(model, "ranking")}
          </div>
        </div>
      </td>
      <td class="score-cell">
        <div class="score-value"><span>${formatNumber(displayScore)}</span><span class="muted">${escapeHtml(model.scoreMeta || "")}</span></div>
        <div class="score-bar" style="--value: ${scoreWidth}%"><span></span></div>
      </td>
      ${renderMethodRankCell(model, "twopl")}
      ${renderMethodRankCell(model, "denseRasch")}
      <td>${escapeHtml(formatSpeed(model.medianOutputSpeed))}</td>
      <td>${escapeHtml(formatTokens(model.contextWindowTokens))}</td>
      <td>${renderPriceCell(model.pricing)}</td>
      <td>${renderSourcePill(model)}</td>
      <td>${escapeHtml(model.coverageLabel || model.coverage)}</td>
    </tr>
  `;
}

function renderMethodRankCell(model, methodId) {
  const publicationRank = rankingMethodPublicationRank(model, methodId);
  const evidenceRank = rankingMethodEvidenceRank(model, methodId);
  if (!Number.isFinite(publicationRank)) return `<td class="method-rank-col">—</td>`;
  return `
    <td class="method-rank-col" title="${escapeHtml(methodRankTitle(evidenceRank))}">
      #${publicationRank}
      ${Number.isFinite(evidenceRank) ? `<span class="method-rank-evidence">${escapeHtml(tr("evidenceRankLabel"))} #${evidenceRank}</span>` : ""}
    </td>
  `;
}

function renderPriceCell(pricing = {}) {
  const parts = [
    [tr("table.input"), pricing.inputPerMillionTokensUsd],
    [tr("table.output"), pricing.outputPerMillionTokensUsd],
    [tr("table.cache"), pricing.cacheHitPerMillionTokensUsd],
  ];
  return `
    <div class="price-stack">
      ${parts.map(([label, value]) => `
        <span><strong>${escapeHtml(label)}</strong><b>${escapeHtml(formatMoney(value))}</b><em>${escapeHtml(tr("table.perMillion"))}</em></span>
      `).join("")}
    </div>
  `;
}

function renderTextRanking(models) {
  if (models.length === 0) {
    els.textRanking.innerHTML = `<div class="empty">${escapeHtml(tr("empty"))}</div>`;
    return;
  }
  els.textRanking.innerHTML = models.map((model) => {
    const source = sourceTypeLabel(sourceType(model));
    const creator = model.creator || tr("unknownCreator");
    return `
      <div class="text-ranking-row" data-card-href="${escapeHtml(modelHref(model, "ranking"))}" role="link" tabindex="0" aria-label="${escapeHtml(`${tr("modelDetails")} ${model.model}`)}">
        <span>#${model.rank}</span>
        <a class="text-model" href="${escapeHtml(modelHref(model))}">${escapeHtml(model.model)}</a>
        ${renderProviderTextLink(creator, "ranking")}
        <strong>${formatNumber(modelDisplayScore(model))}</strong>
        <span class="text-source">${escapeHtml(source)}</span>
        ${renderCompareEntry(model, "ranking")}
      </div>
    `;
  }).join("");
}

function renderModelDetail(ranked, preset) {
  const model = findModelByRoute(ranked);
  if (!model) {
    document.title = `${tr("modelNotFound")} · ${tr("pageTitle")}`;
    els.modelDetail.innerHTML = `
      <div class="detail-nav">
        <a class="back-link" href="${escapeHtml(modelBackHref())}" data-history-back>${renderIcon("arrowLeft")}${escapeHtml(tr("back"))}</a>
      </div>
      <section class="detail-empty">${escapeHtml(tr("modelNotFound"))}</section>
    `;
    return;
  }

  document.title = `${model.model} · ${tr("pageTitle")}`;
  const color = providerColor(model);
  const siblingRows = ranked.filter((row) => row.variantGroup === model.variantGroup);
  const referenceRows = benchmarkProfileRows(model, { reference: true });
  const nonReferenceRows = benchmarkProfileRows(model, { reference: false });
  const providerName = model.creator || tr("unknownCreator");

  els.modelDetail.innerHTML = `
    <div class="detail-nav">
      <a class="back-link" href="${escapeHtml(modelBackHref())}" data-history-back>${renderIcon("arrowLeft")}${escapeHtml(tr("back"))}</a>
      <a class="back-link detail-compare-link" href="${escapeHtml(modelCompareHref(model))}" aria-label="${escapeHtml(`${tr("compareEntry")} ${model.model}`)}">
        <span>${escapeHtml(tr("compareEntry"))}</span>
        ${renderIcon("arrowRight")}
      </a>
    </div>
    <section class="detail-hero" style="--detail-color: ${color}">
      <div class="detail-hero-main">
        ${renderModelIcon(model)}
        <div>
          <p><a class="detail-provider-link" href="${escapeHtml(providerHref(providerName, currentModelBackSource()))}">${renderIcon("network")}${escapeHtml(providerName)}</a></p>
          <h2>${escapeHtml(model.model)}</h2>
          <div class="model-meta detail-meta">
            ${model.isReasoning ? `<span class="pill">${escapeHtml(tr("reasoning"))}</span>` : ""}
            ${renderSourcePill(model)}
            <span>${escapeHtml(tr("releaseDate"))}: ${escapeHtml(formatDate(model.releaseDate))}</span>
          </div>
        </div>
      </div>
      <div class="detail-hero-facts">${renderDetailHeroFacts(model)}</div>
    </section>

    <section class="detail-section">
      <div class="detail-section-head">
        <h2>${escapeHtml(tr("detailRankTitle"))}</h2>
        <p>${escapeHtml(tr("detailRadarSubtitle"))}</p>
      </div>
      ${renderRadarChart([model], { average: true, mode: "detail" })}
    </section>

    <section class="detail-grid">
      <section class="detail-section">
        <div class="detail-section-head">
          <h2>${escapeHtml(tr("detailCostTitle"))}</h2>
          <p>${escapeHtml(tr("currentPreset"))}: ${escapeHtml(presetLabel(state.presetId))}</p>
        </div>
        ${renderDetailPanel(model)}
      </section>

      <section class="detail-section">
        <div class="detail-section-head">
          <h2>${escapeHtml(tr("detailVariantsTitle"))}</h2>
        </div>
        <div class="variant-list">${renderSiblingVariants(siblingRows, model)}</div>
      </section>
    </section>

    <section class="detail-section">
      <div class="detail-section-head">
        <h2>${escapeHtml(tr("detailBenchmarkTitle"))}</h2>
        <p>${escapeHtml(tr("detailBenchmarkSubtitle"))}</p>
      </div>
      <div class="benchmark-profile">
        ${referenceRows.length ? referenceRows.map(renderBenchmarkRow).join("") : `<div class="empty">${escapeHtml(tr("noBenchmarks"))}</div>`}
      </div>
    </section>

    <section class="detail-section">
      <div class="detail-section-head">
        <h2>${escapeHtml(tr("detailExternalTitle"))}</h2>
        <p>${escapeHtml(tr("detailExternalSubtitle"))}</p>
      </div>
      <div class="benchmark-profile non-reference-profile">
        ${nonReferenceRows.length ? nonReferenceRows.map(renderBenchmarkRow).join("") : `<div class="empty">${escapeHtml(tr("notAvailable"))}</div>`}
      </div>
    </section>

    <section class="detail-section">
      <div class="detail-section-head">
        <h2>${escapeHtml(tr("detailSourcesTitle"))}</h2>
      </div>
      <div class="source-grid compact">${modelSourceCardsHtml(model)}</div>
      ${renderRadarBasisNotes()}
    </section>
  `;
}

function renderRankCards(model) {
  const ids = ["zhihu-adjusted", "aa-intelligence", "aa-coding", "aa-agentic"];
  const iconByPreset = {
    "zhihu-adjusted": "trophy",
    "aa-intelligence": "brain",
    "aa-coding": "code",
    "aa-agentic": "network",
    custom: "sliders",
  };
  if (state.presetId === "custom") ids.push("custom");
  return ids.map((id) => {
    const ranked = rankForPreset(model, id);
    const score = ranked ? formatNumber(modelDisplayScore(ranked)) : tr("notAvailable");
    const rank = ranked ? `#${ranked.rank}` : tr("notAvailable");
    return `
      <article class="rank-card">
        ${renderIcon(iconByPreset[id] || "trophy")}
        <span>${escapeHtml(presetLabel(id))}</span>
        <strong>${escapeHtml(score)}</strong>
        <em>${escapeHtml(rank)}</em>
      </article>
    `;
  }).join("");
}

function renderRadarChart(models, options = {}) {
  const axes = radarAxes();
  const visibleModels = models
    .filter(Boolean)
    .filter((model) => radarHasCompleteProfile(model, axes));
  if (visibleModels.length === 0) return `<div class="empty">${escapeHtml(tr("radarNoData"))}</div>`;

  const detailModel = options.mode === "detail" ? visibleModels[0] : null;
  const layout = radarChartLayout(options.mode, visibleModels.length);
  const { center, radius, labelRadius } = layout;
  const rings = [20, 40, 60, 80, 100];
  const averageValues = axes.map((axis) => radarAxisAverage(axis));
  const showAverage = Boolean(options.average && options.mode !== "compare")
    && averageValues.every(Number.isFinite);
  const averagePoints = showAverage ? radarPolygonPoints(averageValues, center, radius) : "";
  const series = visibleModels.slice(0, 8).map((model, index) => ({
    model,
    color: providerColor(model, index),
    values: axes.map((axis) => radarAxisValue(model, axis)),
  }));

  return `
    <div class="radar-card ${options.mode === "compare" ? "compare-radar-card" : ""}">
      <div class="radar-legend">
        ${series.map((item) => `
          <span><i style="--legend-color: ${escapeHtml(item.color)}"></i>${escapeHtml(item.model.model)}</span>
        `).join("")}
        ${showAverage ? `<span><i class="average-key"></i>${escapeHtml(tr("radarAverage"))}</span>` : ""}
      </div>
      <div class="radar-plot-wrap">
        <svg class="radar-plot" viewBox="0 0 ${layout.width} ${layout.height}" role="img" aria-label="${escapeHtml(tr("compareRadarTitle"))}">
          <g class="radar-grid">
            ${rings.map((ring) => `<polygon points="${escapeHtml(radarPolygonPoints(axes.map(() => ring), center, radius))}"></polygon>`).join("")}
            ${axes.map((axis, index) => {
              const end = radarPoint(index, 100, axes.length, center, radius);
              return `<line x1="${center.x}" y1="${center.y}" x2="${formatSvgNumber(end.x)}" y2="${formatSvgNumber(end.y)}"></line>`;
            }).join("")}
          </g>
          ${showAverage ? `<polygon class="radar-area radar-average-area" points="${escapeHtml(averagePoints)}"></polygon>` : ""}
          ${series.map((item, index) => `
            <polygon class="radar-area radar-series-area" style="--series-color: ${escapeHtml(item.color)}; --series-index: ${index}" points="${escapeHtml(radarPolygonPoints(item.values, center, radius))}"></polygon>
            <polyline class="radar-series-line" style="--series-color: ${escapeHtml(item.color)}" points="${escapeHtml(radarPolygonPoints(item.values, center, radius))}"></polyline>
            ${item.values.map((value, axisIndex) => {
              if (!Number.isFinite(value)) return "";
              const point = radarPoint(axisIndex, value, axes.length, center, radius);
              return `<circle class="radar-point" style="--series-color: ${escapeHtml(item.color)}" cx="${formatSvgNumber(point.x)}" cy="${formatSvgNumber(point.y)}" r="3.8"></circle>`;
            }).join("")}
          `).join("")}
          ${showAverage ? `<polyline class="radar-average-line" points="${escapeHtml(averagePoints)}"></polyline>` : ""}
          <g class="radar-labels">
            ${axes.map((axis, index) => renderRadarAxisLabel(axis, index, axes.length, layout, detailModel, series, options.mode)).join("")}
          </g>
        </svg>
      </div>
      <div class="radar-foot">
        <span>${escapeHtml(tr("radarDataSource"))}</span>
        <b>${escapeHtml(tr("radarSourceText"))}</b>
      </div>
    </div>
  `;
}

function radarChartLayout(mode, seriesCount = 1) {
  const isCompare = mode === "compare";
  const scoreRows = Math.min(Math.max(seriesCount, 1), 8);
  const width = isCompare ? 980 : 920;
  const height = isCompare ? Math.max(720, 600 + scoreRows * 22) : 690;
  return {
    width,
    height,
    center: { x: width / 2, y: isCompare ? Math.round(height * 0.46) : 322 },
    radius: isCompare ? 158 : 162,
    labelRadius: isCompare ? 286 : 278,
  };
}

function renderRadarAxisLabel(axis, index, count, layout, detailModel, series, mode) {
  const { center, labelRadius } = layout;
  const point = radarPoint(index, 100, count, center, labelRadius);
  const box = radarAxisLabelBox(point, layout, mode, series.length);
  const value = detailModel ? radarAxisValue(detailModel, axis) : null;
  const coverage = detailModel ? radarAxisCoverage(detailModel, axis) : null;
  const rank = detailModel ? radarAxisRank(axis, detailModel) : null;
  const average = radarAxisAverage(axis);
  const rankLabel = rank ? `#${rank.rank}` : "";
  const content = mode === "compare"
    ? renderRadarCompareAxisLabel(axis, series)
    : renderRadarDetailAxisLabel(axis, value, average, rankLabel, coverage);
  return `
    <foreignObject x="${formatSvgNumber(box.x)}" y="${formatSvgNumber(box.y)}" width="${formatSvgNumber(box.width)}" height="${formatSvgNumber(box.height)}">
      <div xmlns="http://www.w3.org/1999/xhtml" class="radar-axis-label ${box.anchorClass}">
        ${content}
      </div>
    </foreignObject>
  `;
}

function radarAxisLabelBox(point, layout, mode, seriesCount) {
  const isCompare = mode === "compare";
  const width = isCompare ? 244 : 236;
  const height = isCompare ? Math.min(196, 50 + Math.min(Math.max(seriesCount, 1), 8) * 20) : 82;
  const side = point.x < layout.center.x - 32 ? "left" : point.x > layout.center.x + 32 ? "right" : "center";
  let x = point.x - width / 2;
  let y = point.y - height / 2;
  if (side === "left") x = point.x - width - 10;
  if (side === "right") x = point.x + 10;
  if (point.y < layout.center.y - layout.labelRadius * 0.62) y = point.y - height - 4;
  if (point.y > layout.center.y + layout.labelRadius * 0.62) y = point.y + 4;
  return {
    x: clamp(x, 8, layout.width - width - 8),
    y: clamp(y, 8, layout.height - height - 8),
    width,
    height,
    anchorClass: side === "left" ? "is-left" : side === "right" ? "is-right" : "is-center",
  };
}

function renderRadarDetailAxisLabel(axis, value, average, rankLabel, coverage) {
  const coverageLabel = radarCoverageLabel(coverage);
  return `
    <strong><b>${escapeHtml(formatNumber(value))}</b> ${escapeHtml(axis.label)}</strong>
    <em>${escapeHtml(formatNumber(average))}${rankLabel ? ` · ${escapeHtml(rankLabel)}` : ""}${coverageLabel ? ` · ${escapeHtml(coverageLabel)}` : ""}</em>
  `;
}

function renderRadarCompareAxisLabel(axis, series) {
  const rows = series
    .map((item) => ({
      model: item.model,
      color: item.color,
      value: radarAxisValue(item.model, axis),
      coverage: radarAxisCoverage(item.model, axis),
    }))
    .sort((a, b) => {
      const aFinite = Number.isFinite(a.value);
      const bFinite = Number.isFinite(b.value);
      if (aFinite !== bFinite) return bFinite - aFinite;
      return (b.value - a.value) || a.model.model.localeCompare(b.model.model);
    });
  return `
    <strong>${escapeHtml(axis.label)}</strong>
    <span class="radar-axis-score-list">
      ${rows.map((row) => `
        <span class="radar-axis-score" style="--score-color: ${escapeHtml(row.color)}">
          <i></i>
          <b>${escapeHtml(formatNumber(row.value))}</b>
          <span>${escapeHtml(scatterLabelText(row.model.model))}${radarCoverageLabel(row.coverage) ? ` · ${escapeHtml(radarCoverageLabel(row.coverage))}` : ""}</span>
        </span>
      `).join("")}
    </span>
  `;
}

function radarAxes() {
  return [
    {
      id: "coding",
      boardId: "coding",
      label: tr("radarAxes.coding"),
      note: tr("radarAxisNotes.coding"),
    },
    {
      id: "agentic-tool-work",
      boardId: "agentic-tool-work",
      label: tr("radarAxes.agenticToolWork"),
      note: tr("radarAxisNotes.agenticToolWork"),
    },
    {
      id: "hard-reasoning",
      boardId: "hard-reasoning",
      label: tr("radarAxes.hardReasoning"),
      note: tr("radarAxisNotes.hardReasoning"),
    },
    {
      id: "knowledge-science",
      boardId: "knowledge-science",
      label: tr("radarAxes.knowledgeScience"),
      note: tr("radarAxisNotes.knowledgeScience"),
    },
    {
      id: "instruction-context",
      boardId: "instruction-context",
      label: tr("radarAxes.instructionContext"),
      note: tr("radarAxisNotes.instructionContext"),
    },
    {
      id: "evidence-coverage",
      profileKey: "evidenceCoverageScore",
      label: tr("radarAxes.evidenceCoverage"),
      note: tr("radarAxisNotes.evidenceCoverage"),
    },
  ];
}

function renderRadarBasisNotes() {
  const axes = radarAxes();
  return `
    <div class="radar-basis">
      <div class="radar-basis-head">
        <strong>${escapeHtml(tr("radarBasisTitle"))}</strong>
        <span>${escapeHtml(tr("radarBasisSubtitle"))}</span>
      </div>
      <div class="radar-basis-grid">
        ${axes.map((axis) => `
          <article>
            <strong>${escapeHtml(axis.label)}</strong>
            <span>${escapeHtml(axis.note)}</span>
          </article>
        `).join("")}
      </div>
    </div>
  `;
}

function radarBoardProfile(model, boardId) {
  const board = model?.rankingProfile?.boards?.[boardId];
  return board && typeof board === "object" ? board : null;
}

function radarAxisValue(model, axis) {
  const rawValue = axis.profileKey
    ? model?.rankingProfile?.[axis.profileKey]
    : radarBoardProfile(model, axis.boardId)?.score;
  if (rawValue === null || rawValue === undefined || rawValue === "") return null;
  const value = Number(rawValue);
  return Number.isFinite(value) ? clamp(value, 0, 100) : null;
}

function radarAxisCoverage(model, axis) {
  if (!axis.boardId) return null;
  const profile = model?.rankingProfile;
  const board = radarBoardProfile(model, axis.boardId);
  const available = Number(board?.tests);
  if (!Number.isFinite(available)) return null;
  const itemPoolSize = Number(
    board?.itemPoolSize
      ?? profile?.boardItemPoolSizesByMethod?.rasch?.[axis.boardId]
      ?? profile?.boardItemPoolSizes?.[axis.boardId],
  );
  const sparseAvailable = Number(board?.sparseTests);
  const sparseItemPoolSize = Number(
    board?.sparseItemPoolSize
      ?? profile?.boardItemPoolSizesByMethod?.sparseRasch?.[axis.boardId],
  );
  return {
    available,
    total: Number.isFinite(itemPoolSize) && itemPoolSize > 0 ? itemPoolSize : null,
    coreAvailable: available,
    coreTotal: Number.isFinite(itemPoolSize) && itemPoolSize > 0 ? itemPoolSize : null,
    sparseAvailable: Number.isFinite(sparseAvailable) ? sparseAvailable : null,
    sparseTotal: Number.isFinite(sparseItemPoolSize) && sparseItemPoolSize > 0 ? sparseItemPoolSize : null,
  };
}

function radarCoverageLabel(coverage) {
  if (!coverage || !Number.isFinite(coverage.available)) return "";
  if (
    Number.isFinite(coverage.coreTotal)
    && Number.isFinite(coverage.sparseAvailable)
    && Number.isFinite(coverage.sparseTotal)
  ) return tr("radarDualCoverage", coverage);
  if (!Number.isFinite(coverage.total)) return tr("radarTestCount", coverage);
  return tr("radarCoverage", coverage);
}

function radarHasCompleteProfile(model, axes = radarAxes()) {
  return Boolean(model?.rankingProfile)
    && axes.every((axis) => Number.isFinite(radarAxisValue(model, axis)));
}

function radarProfilePopulation(axes = radarAxes()) {
  return (state.data?.models || [])
    .filter((model) => radarHasCompleteProfile(model, axes));
}

function radarAxisAverage(axis) {
  const axes = radarAxes();
  const values = radarProfilePopulation(axes)
    .map((model) => radarAxisValue(model, axis))
    .filter(Number.isFinite);
  if (values.length === 0) return null;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function radarAxisRank(axis, model) {
  const target = radarAxisValue(model, axis);
  if (!Number.isFinite(target)) return null;
  const rows = radarProfilePopulation(radarAxes())
    .map((candidate) => ({ candidate, value: radarAxisValue(candidate, axis) }))
    .filter((row) => Number.isFinite(row.value))
    .sort((a, b) => b.value - a.value || a.candidate.model.localeCompare(b.candidate.model));
  return rankFromRows(rows, model);
}

function radarPolygonPoints(values, center, radius) {
  if (!Array.isArray(values) || values.length === 0 || values.some((value) => !Number.isFinite(value))) return "";
  return values.map((value, index) => {
    const point = radarPoint(index, value, values.length, center, radius);
    return `${formatSvgNumber(point.x)},${formatSvgNumber(point.y)}`;
  }).join(" ");
}

function radarPoint(index, value, count, center, radius) {
  const normalized = clamp(Number(value) || 0, 0, 100) / 100;
  const angle = -Math.PI / 2 + (index * Math.PI * 2) / count;
  return {
    x: center.x + Math.cos(angle) * radius * normalized,
    y: center.y + Math.sin(angle) * radius * normalized,
  };
}

function renderDetailPanel(model) {
  return `
    <div class="detail-panel">
      <div class="stat-grid detail-stat-grid">
        ${renderDetailStat(tr(scoreHeaderKeyForPreset(state.data.presets[state.presetId])), formatNumber(modelDisplayScore(model)), scoreRankMeta(model), "trophy")}
        ${renderDetailStat(tr("headers.speed"), formatSpeed(model.medianOutputSpeed), valueRankMeta(model, (row) => row.medianOutputSpeed, true, "higherBetter"), "gauge")}
        ${renderDetailStat("AA run", formatMoney(modelCost(model)), valueRankMeta(model, modelCost, false, "lowerBetter"), "dollar")}
        ${renderDetailStat(tr("headers.context"), formatTokens(model.contextWindowTokens), valueRankMeta(model, (row) => row.contextWindowTokens, true, "higherBetter"), "database")}
        ${renderDetailModalityStat(tr("detailRows.inputTypes"), model, "input", "arrowDown")}
        ${renderDetailModalityStat(tr("detailRows.outputTypes"), model, "output", "arrowUp")}
        ${renderDetailStat(tr("table.input"), formatMoney(model.pricing?.inputPerMillionTokensUsd), valueRankMeta(model, (row) => row.pricing?.inputPerMillionTokensUsd, false, "lowerBetter"), "arrowDown")}
        ${renderDetailStat(tr("table.output"), formatMoney(model.pricing?.outputPerMillionTokensUsd), valueRankMeta(model, (row) => row.pricing?.outputPerMillionTokensUsd, false, "lowerBetter"), "arrowUp")}
        ${renderDetailStat(tr("table.cache"), formatMoney(model.pricing?.cacheHitPerMillionTokensUsd), valueRankMeta(model, (row) => row.pricing?.cacheHitPerMillionTokensUsd, false, "lowerBetter"), "database")}
      </div>
    </div>
  `;
}

function normalizeList(values) {
  const list = Array.isArray(values) ? values : [values];
  return list.map((value) => String(value || "").trim()).filter(Boolean);
}

function renderDetailModalityStat(label, model, kind, icon = "database") {
  const state = modalitySupportState(model, kind);
  const meta = `${state.supportedCount}/${modalitySpecs.length} ${tr("detailRows.supported")}`;
  return `
    <article class="detail-stat detail-modality-card">
      ${renderIcon(icon)}
      <span>${escapeHtml(label)}</span>
      ${renderModalitySupportGrid(model, kind)}
      <em>${escapeHtml(meta)}</em>
    </article>
  `;
}

function renderModalitySupportGrid(model, kind) {
  const state = modalitySupportState(model, kind);
  return `
    <div class="modality-support-grid" role="list" aria-label="${escapeHtml(kind === "input" ? tr("detailRows.inputTypes") : tr("detailRows.outputTypes"))}">
      ${modalitySpecs.map((spec) => {
        const supported = Boolean(state.flags[spec.key]);
        return `
          <span class="modality-support-icon${supported ? " is-supported" : ""}" role="listitem" title="${escapeHtml(spec.label)}" aria-label="${escapeHtml(`${spec.label}: ${supported ? tr("detailRows.supported") : tr("notAvailable")}`)}">
            ${renderIcon(spec.icon)}
          </span>
        `;
      }).join("")}
    </div>
  `;
}

function modalitySupportState(model, kind) {
  const details = model.modelDetails || {};
  const rawFlags = details.modalities?.[kind] || {};
  const source = kind === "output"
    ? (model.outputModalities || details.outputModalities)
    : (model.inputModalities || details.inputModalities);
  const list = normalizeList(source || ["Text"]);
  const listFlags = modalityFlagsFromList(list);
  const flags = {};
  for (const spec of modalitySpecs) {
    const raw = rawFlags[spec.key];
    flags[spec.key] = typeof raw === "boolean" ? raw : Boolean(listFlags[spec.key]);
  }
  return {
    flags,
    supportedCount: modalitySpecs.filter((spec) => flags[spec.key]).length,
  };
}

function modalityFlagsFromList(values) {
  const flags = {};
  for (const value of normalizeList(values)) {
    const key = modalityKeyFromLabel(value);
    if (key) flags[key] = true;
  }
  return flags;
}

function modalityKeyFromLabel(value) {
  const text = String(value || "").toLowerCase();
  if (text.includes("image") || text.includes("vision") || text.includes("图片") || text.includes("图像")) return "image";
  if (text.includes("video") || text.includes("视频")) return "video";
  if (text.includes("audio") || text.includes("speech") || text.includes("sound") || text.includes("voice") || text.includes("语音") || text.includes("音频")) return "speech";
  if (text.includes("text") || text.includes("文本") || text.includes("文字")) return "text";
  return "";
}

function scoreRankMeta(model) {
  if (!model.rank) return tr("notAvailable");
  const preset = state.data.presets[state.presetId];
  const total = preset ? scoreModels(preset).length : 0;
  return total ? `#${model.rank}/${total}` : `#${model.rank}`;
}

function valueRankMeta(model, accessor, descending, directionKey) {
  const rank = valueRank(model, accessor, { descending });
  if (!rank) return tr("notAvailable");
  return `#${rank.rank}/${rank.total} · ${tr(`detailRows.${directionKey}`)}`;
}

function valueRank(model, accessor, options = {}) {
  const target = accessor(model);
  if (!Number.isFinite(target)) return null;
  const descending = options.descending !== false;
  const rows = state.data.models
    .map((candidate) => ({ candidate, value: accessor(candidate) }))
    .filter((row) => Number.isFinite(row.value))
    .sort((a, b) => (descending ? b.value - a.value : a.value - b.value) || a.candidate.model.localeCompare(b.candidate.model));
  return rankFromRows(rows, model);
}

function rankFromRows(rows, model) {
  let previousValue = null;
  let currentRank = 0;
  for (let index = 0; index < rows.length; index += 1) {
    const row = rows[index];
    if (previousValue === null || row.value !== previousValue) {
      currentRank = index + 1;
      previousValue = row.value;
    }
    if (sameModelIdentity(row.candidate, model)) {
      return { rank: currentRank, total: rows.length };
    }
  }
  return null;
}

function listLabel(values) {
  const list = Array.isArray(values) ? values : [values];
  const cleaned = list.map((value) => String(value || "").trim()).filter(Boolean);
  return cleaned.length ? cleaned.join(" / ") : tr("notAvailable");
}

function formatSvgNumber(value) {
  return Number(value).toFixed(2).replace(/\.?0+$/, "");
}

function renderDetailHeroFacts(model) {
  const facts = [
    ["calendar", `${tr("releaseDate")}: ${formatDate(model.releaseDate)}`],
    ["database", sourceTypeLabel(sourceType(model))],
    ["gauge", `${formatNumber(modelDisplayScore(model))} ${tr(scoreHeaderKeyForPreset(state.data.presets[state.presetId]))}`],
  ];
  return facts.map(([icon, label]) => `<span>${renderIcon(icon)}${escapeHtml(label)}</span>`).join("");
}

function renderDetailStat(label, value, meta, icon = "trophy") {
  return `
    <article class="detail-stat">
      ${renderIcon(icon)}
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value || tr("notAvailable"))}</strong>
      <em>${escapeHtml(meta || "")}</em>
    </article>
  `;
}

function renderSiblingVariants(rows, currentModel) {
  if (rows.length <= 1) return `<div class="empty">${escapeHtml(tr("notAvailable"))}</div>`;
  return rows.map((row) => `
    <a class="variant-row${sameModelIdentity(row, currentModel) ? " is-current" : ""}" href="${escapeHtml(modelHref(row, currentModelBackSource()))}">
      <span>${Number.isFinite(row.rank) ? `#${row.rank}` : escapeHtml(tr("notAvailable"))}</span>
      <strong>${escapeHtml(row.model)}</strong>
      <em>${escapeHtml(formatNumber(modelDisplayScore(row)))}</em>
    </a>
  `).join("");
}

function benchmarkProfileRows(model, { reference = true } = {}) {
  const defaultWeights = state.data.presets.custom?.weights || {};
  return state.data.metrics
    .map((metric) => {
      const value = model.scores?.[metric.key];
      const externalRow = (model.externalBenchmarks || []).find((row) => row.metricKey === metric.key);
      return {
        key: metric.key,
        label: metric.label,
        value,
        weight: Number(defaultWeights[metric.key] || 0),
        rank: metricRank(metric.key, model),
        metric,
        sourceLabel: externalRow?.sourceLabel || (metric.source === "benchmark" ? tr("source") : "Artificial Analysis"),
        sourceUrl: externalRow?.sourceUrl || "",
        unit: externalRow?.unit || metric.unit || "%",
      };
    })
    .filter((row) => (reference ? row.weight > 0 : row.weight <= 0))
    .filter((row) => Number.isFinite(row.value))
    .sort((a, b) => b.weight - a.weight || String(a.metric.category || "").localeCompare(String(b.metric.category || "")) || b.value - a.value || a.label.localeCompare(b.label));
}

function renderBenchmarkRow(row) {
  const valueWidth = clamp(row.value, 0, 100);
  const value = `${formatNumber(row.value)}${row.unit === "%" ? "%" : ` ${row.unit || ""}`}`.trim();
  const meta = row.weight > 0
    ? `#${row.rank || tr("notAvailable")} · w ${formatWeight(row.weight)}`
    : `#${row.rank || tr("notAvailable")} · ${row.sourceLabel || tr("benchmarkNonReference")}`;
  const label = `<strong>${escapeHtml(row.label)}</strong>`;
  const labelHtml = row.key
    ? `<a href="${escapeHtml(benchmarkHref(row.key))}">${label}</a>`
    : label;
  return `
    <div class="benchmark-row">
      <div>
        ${labelHtml}
        <span>${escapeHtml(meta)}</span>
      </div>
      <div class="benchmark-track"><span style="--value: ${valueWidth}%"></span></div>
      <em>${escapeHtml(value)}</em>
    </div>
  `;
}

function benchmarkEvidenceRows(model) {
  return [...(model.externalBenchmarks || [])].sort((a, b) => {
    const metricA = metricDefinition(a.metricKey);
    const metricB = metricDefinition(b.metricKey);
    return String(metricA.category || "").localeCompare(String(metricB.category || ""))
      || String(a.label || "").localeCompare(String(b.label || ""));
  });
}

function renderBenchmarkEvidenceRow(row) {
  const metric = metricDefinition(row.metricKey);
  const icon = metric.icon || initials(row.label);
  const valueWidth = clamp(row.value, 0, 100);
  const value = `${formatNumber(row.value)}${row.unit === "%" ? "%" : ` ${row.unit || ""}`}`.trim();
  const source = row.sourceLabel || tr("source");
  const href = row.sourceUrl || "#";
  return `
    <a class="benchmark-evidence-row" href="${escapeHtml(href)}" target="_blank" rel="noreferrer">
      <span class="benchmark-evidence-icon">${escapeHtml(icon)}</span>
      <span class="benchmark-evidence-copy">
        <strong>${escapeHtml(row.label)}</strong>
        <em>${escapeHtml(metric.category || source)} · ${escapeHtml(source)}</em>
      </span>
      <span class="benchmark-evidence-track"><span style="--value: ${valueWidth}%"></span></span>
      <b>${escapeHtml(value)}</b>
    </a>
  `;
}

function renderBenchmarkPage() {
  const metrics = rankedBenchmarkMetrics();
  const selected = findBenchmarkMetric(metrics);
  if (!selected) {
    els.benchmarkDetail.innerHTML = `<section class="detail-empty">${escapeHtml(tr("notAvailable"))}</section>`;
    return;
  }
  state.benchmarkId = selected.key;
  const rows = benchmarkRankingRows(selected);
  document.title = `${selected.label} · ${tr("benchmarkPageTitle")} · ${tr("pageTitle")}`;
  els.benchmarkDetail.innerHTML = `
    <section class="detail-section benchmark-page-hero">
      <div class="detail-section-head">
        <h2>${escapeHtml(tr("benchmarkPageTitle"))}</h2>
        <p>${escapeHtml(tr("benchmarkPageSubtitle"))}</p>
      </div>
      <div class="benchmark-page-grid">
        <section class="benchmark-picker" aria-labelledby="benchmarkPickerTitle">
          <h3 id="benchmarkPickerTitle">${escapeHtml(tr("benchmarkPickerTitle"))}</h3>
          <div class="benchmark-picker-list">
            ${metrics.map((metric) => renderBenchmarkPickerItem(metric, selected)).join("")}
          </div>
        </section>
        <section class="benchmark-ranking-panel">
          <div class="detail-section-head">
            <h2>${escapeHtml(tr("benchmarkRankingTitle", { label: selected.label }))}</h2>
            <p>${escapeHtml(tr("benchmarkRankingSubtitle", { count: rows.length, category: selected.category || tr("benchmarkNonReference") }))}</p>
          </div>
          <div class="benchmark-ranking-list">
            ${rows.length ? rows.map((row) => renderBenchmarkRankingRow(row, selected)).join("") : `<div class="empty">${escapeHtml(tr("notAvailable"))}</div>`}
          </div>
        </section>
      </div>
    </section>
  `;
}

function rankedBenchmarkMetrics() {
  const defaultWeights = state.data.presets.custom?.weights || {};
  return (state.data.metrics || []).map((metric) => ({
    ...metric,
    coverage: metricGroupCoverageCount([metric]),
    referenceWeight: Number(defaultWeights[metric.key] || 0),
  })).filter((metric) => metric.coverage > 0)
    .sort((a, b) => (
      (b.referenceWeight > 0) - (a.referenceWeight > 0)
      || b.coverage - a.coverage
      || a.label.localeCompare(b.label)
    ));
}

function findBenchmarkMetric(metrics) {
  const routeId = state.benchmarkId || new URLSearchParams(location.search).get("id") || "";
  return metrics.find((metric) => metric.key === routeId)
    || metrics.find((metric) => metricGroupId(metric) === routeId)
    || metrics[0]
    || null;
}

function renderBenchmarkPickerItem(metric, selected) {
  const active = metric.key === selected.key;
  const kind = metric.referenceWeight > 0 ? tr("benchmarkReference") : tr("benchmarkNonReference");
  return `
    <a class="benchmark-picker-item${active ? " is-active" : ""}" href="${escapeHtml(benchmarkHref(metric.key))}">
      <span>${escapeHtml(metric.icon || initials(metric.label))}</span>
      <strong>${escapeHtml(metric.label)}</strong>
      <em>${escapeHtml(tr("metricCoverage", { count: metric.coverage }))} · ${escapeHtml(kind)}</em>
    </a>
  `;
}

function benchmarkRankingRows(metric) {
  const rows = (state.data.models || [])
    .map((model) => {
      const value = model.scores?.[metric.key];
      if (!Number.isFinite(value)) return null;
      const sourceRow = (model.externalBenchmarks || []).find((row) => row.metricKey === metric.key);
      return {
        model,
        value,
        sourceLabel: sourceRow?.sourceLabel || (metric.source === "benchmark" ? tr("source") : "Artificial Analysis"),
        sourceUrl: sourceRow?.sourceUrl || "",
      };
    })
    .filter(Boolean)
    .sort((a, b) => b.value - a.value || a.model.model.localeCompare(b.model.model));
  let previousValue = null;
  let currentRank = 0;
  return rows.map((row, index) => {
    if (previousValue === null || row.value !== previousValue) {
      currentRank = index + 1;
      previousValue = row.value;
    }
    return { ...row, rank: currentRank };
  });
}

function renderBenchmarkRankingRow(row, metric) {
  const maxValue = metric.unit === "%"
    ? 100
    : Math.max(...benchmarkRankingRows(metric).map((item) => item.value), 1);
  const valueWidth = clamp((row.value / maxValue) * 100, 0, 100);
  const value = `${formatNumber(row.value)}${metric.unit === "%" ? "%" : ` ${metric.unit || ""}`}`.trim();
  const source = row.sourceUrl
    ? `<a href="${escapeHtml(row.sourceUrl)}" target="_blank" rel="noreferrer">${escapeHtml(row.sourceLabel)}</a>`
    : escapeHtml(row.sourceLabel);
  return `
    <article class="benchmark-ranking-row" data-card-href="${escapeHtml(modelHref(row.model, "benchmarks", { benchmarkId: metric.key }))}" role="link" tabindex="0" aria-label="${escapeHtml(`${tr("modelDetails")} ${row.model.model}`)}" style="--value: ${valueWidth}%">
      <span class="rank-number">#${escapeHtml(row.rank)}</span>
      ${renderModelIcon(row.model)}
      <span class="benchmark-ranking-model">
        <a href="${escapeHtml(modelHref(row.model, "benchmarks", { benchmarkId: metric.key }))}">
          <strong>${escapeHtml(row.model.model)}</strong>
        </a>
        <em>${renderProviderTextLink(row.model.creator, "benchmarks", { benchmarkId: metric.key })} · ${source}</em>
      </span>
      <span class="benchmark-ranking-track"><span></span></span>
      <b>${escapeHtml(value)}</b>
      ${renderCompareEntry(row.model, "benchmarks")}
    </article>
  `;
}

function renderComparePage(ranked) {
  if (!els.compareResults) return;
  document.title = `${tr("comparePageTitle")} · ${tr("pageTitle")}`;
  ensureDefaultCompareSelection(ranked);
  const selected = selectedCompareModels(ranked);
  state.compareIds = selected.map(modelRouteId);
  renderComparePicker(ranked);
  renderCompareSelectedModels(selected);

  if (selected.length === 0) {
    els.compareResults.innerHTML = `<section class="detail-empty">${escapeHtml(tr("compareEmpty"))}</section>`;
    return;
  }

  const coreRows = compareCoreRows(selected);
  const benchmarkRows = compareBenchmarkRows(selected);
  els.compareResults.innerHTML = `
    <section class="compare-model-grid" aria-label="${escapeHtml(tr("compareSelectedTitle"))}">
      ${selected.map(renderCompareModelCard).join("")}
    </section>

    <section class="detail-section compare-section compare-radar-section">
      <div class="detail-section-head">
        <h2>${escapeHtml(tr("compareRadarTitle"))}</h2>
        <p>${escapeHtml(tr("compareRadarSubtitle"))}</p>
      </div>
      ${renderRadarChart(selected, { average: false, mode: "compare" })}
    </section>

    <section class="detail-section compare-section">
      <div class="detail-section-head">
        <h2>${escapeHtml(tr("compareCoreTitle"))}</h2>
        <p>${escapeHtml(tr("currentPreset"))}: ${escapeHtml(presetLabel("zhihu-adjusted"))}</p>
      </div>
      ${renderCompareTable(coreRows, selected)}
    </section>

    <section class="detail-section compare-section">
      <div class="detail-section-head">
        <h2>${escapeHtml(tr("compareBenchmarkTitle"))}</h2>
        <p>${escapeHtml(tr("benchmarkPageSubtitle"))}</p>
      </div>
      ${renderCompareTable(benchmarkRows, selected)}
    </section>
  `;
}

function ensureDefaultCompareSelection(models) {
  const hasModelsParam = new URLSearchParams(location.search).has("models");
  if (state.compareIds.length === 0 && !hasModelsParam && !state.compareTouched) {
    state.compareIds = defaultCompareModels(models).map(modelRouteId);
  }
}

function defaultCompareModels(models) {
  return rankRows(dedupeByBestVariant(models.filter((model) => Number.isFinite(model.score)))).slice(0, 3);
}

function selectedCompareModels(models) {
  return normalizeCompareIds(state.compareIds)
    .map((id) => findCompareModel(models, id))
    .filter(Boolean);
}

function renderComparePicker(models) {
  if (!els.compareModelSelect || !els.compareModelOptions) return;
  const selected = new Set(state.compareIds);
  const query = state.compareQuery || "";
  const isOpen = Boolean(state.comparePickerOpen);
  const available = models.filter((model) => !selected.has(modelRouteId(model)));
  const matches = available
    .filter((model) => compareModelMatches(model, query))
    .slice(0, 9);
  const firstAvailable = matches[0] || null;
  els.compareModelSelect.value = state.compareQuery;
  els.compareModelSelect.setAttribute("aria-expanded", String(isOpen));
  els.compareModelOptions.hidden = !isOpen;
  els.compareModelOptions.innerHTML = matches.length
    ? matches.map(renderCompareOption).join("")
    : `<div class="empty compare-option-empty">${escapeHtml(tr("compareSearchEmpty"))}</div>`;
  if (els.compareAddButton) {
    els.compareAddButton.disabled = !firstAvailable;
    els.compareAddButton.dataset.compareAdd = firstAvailable ? modelRouteId(firstAvailable) : "";
  }
}

function compareModelMatches(model, query) {
  if (!query) return true;
  return compareOptionLabel(model).toLowerCase().includes(query);
}

function renderCompareOption(model) {
  const id = modelRouteId(model);
  return `
    <button class="compare-option-card" type="button" data-compare-add="${escapeHtml(id)}" role="option" aria-label="${escapeHtml(`${tr("compareAdd")} ${model.model}`)}">
      ${renderModelIcon(model)}
      <span>
        <strong>${escapeHtml(model.model)}</strong>
        <em>${escapeHtml(model.creator || tr("unknownCreator"))} · ${escapeHtml(rankLabel(model))} · ${escapeHtml(formatNumber(modelDisplayScore(model)))}</em>
      </span>
      ${renderIcon("plus")}
    </button>
  `;
}

function renderCompareSelectedModels(models) {
  if (!els.compareSelectedModels) return;
  if (models.length === 0) {
    els.compareSelectedModels.innerHTML = `<div class="empty">${escapeHtml(tr("compareEmpty"))}</div>`;
    return;
  }
  els.compareSelectedModels.innerHTML = models.map((model) => `
    <span class="compare-chip" style="--chip-color: ${providerColor(model)}">
      ${renderModelIcon(model)}
      <span>${escapeHtml(model.model)}</span>
      <button type="button" data-compare-remove="${escapeHtml(modelRouteId(model))}" aria-label="${escapeHtml(`${tr("compareRemove")} ${model.model}`)}">${renderIcon("x")}</button>
    </span>
  `).join("");
}

function renderCompareModelCard(model) {
  return `
    <article class="compare-model-card" style="--card-color: ${providerColor(model)}">
      <div class="compare-model-head">
        ${renderModelIcon(model)}
        <div>
          <a href="${escapeHtml(modelHref(model, "compare", { compareIds: state.compareIds }))}">${escapeHtml(model.model)}</a>
          <span>${renderProviderTextLink(model.creator, "compare", { compareIds: state.compareIds })}</span>
        </div>
        <button type="button" data-compare-remove="${escapeHtml(modelRouteId(model))}" aria-label="${escapeHtml(`${tr("compareRemove")} ${model.model}`)}">${renderIcon("x")}</button>
      </div>
      <div class="compare-model-facts">
        <span>${renderIcon("trophy")}<b>${escapeHtml(formatNumber(modelDisplayScore(model)))}</b><em>${escapeHtml(rankLabel(model))}</em></span>
        <span>${renderIcon("gauge")}<b>${escapeHtml(formatSpeed(model.medianOutputSpeed))}</b><em>${escapeHtml(tr("compareRows.speed"))}</em></span>
        <span>${renderIcon("database")}<b>${escapeHtml(formatTokens(model.contextWindowTokens))}</b><em>${escapeHtml(tr("compareRows.context"))}</em></span>
      </div>
    </article>
  `;
}

function renderCompareTable(rows, models) {
  if (rows.length === 0) return `<div class="empty">${escapeHtml(tr("notAvailable"))}</div>`;
  return `
    <div class="table-wrap compare-table-wrap">
      <table class="compare-table">
        <thead>
          <tr>
            <th>${escapeHtml(tr("compareMetricColumn"))}</th>
            ${models.map((model) => `
              <th>
                <a class="compare-table-model" href="${escapeHtml(modelHref(model, "compare", { compareIds: state.compareIds }))}">
                  ${renderModelIcon(model)}
                  <span>${escapeHtml(model.model)}</span>
                </a>
              </th>
            `).join("")}
          </tr>
        </thead>
        <tbody>
          ${rows.map((row) => `
            <tr>
              <th scope="row">${renderCompareRowLabel(row)}</th>
              ${row.values.map((value) => `<td>${value}</td>`).join("")}
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;
}

function renderCompareRowLabel(row) {
  const icon = row.iconName
    ? renderIcon(row.iconName)
    : `<span class="compare-metric-icon">${escapeHtml(row.iconText || initials(row.label))}</span>`;
  const label = `<span>${icon}${escapeHtml(row.label)}</span>`;
  return row.href ? `<a href="${escapeHtml(row.href)}">${label}</a>` : label;
}

function compareCoreRows(models) {
  const presetRows = ["aa-intelligence", "aa-coding", "aa-agentic"].map((presetId) => ({
    label: presetLabel(presetId),
    iconName: presetId === "aa-coding" ? "code" : presetId === "aa-agentic" ? "network" : "brain",
    values: models.map((model) => {
      const ranked = rankForPreset(model, presetId);
      return compareValue(ranked ? formatNumber(ranked.score) : tr("notAvailable"), ranked ? `#${ranked.rank}` : "");
    }),
  }));
  return [
    {
      label: tr("compareRows.provider"),
      iconName: "network",
      values: models.map((model) => compareProviderCell(model)),
    },
    {
      label: tr("compareRows.score"),
      iconName: "trophy",
      values: models.map((model) => compareValue(formatNumber(modelDisplayScore(model)), model.rank ? `#${model.rank}` : "")),
    },
    {
      label: tr("compareRows.source"),
      iconName: "code",
      values: models.map((model) => renderSourcePill(model)),
    },
    {
      label: tr("compareRows.releaseDate"),
      iconName: "calendar",
      values: models.map((model) => compareValue(formatDate(model.releaseDate))),
    },
    {
      label: tr("compareRows.speed"),
      iconName: "gauge",
      values: models.map((model) => compareValue(formatSpeed(model.medianOutputSpeed), compactValueRank(model, (row) => row.medianOutputSpeed, true))),
    },
    {
      label: tr("compareRows.context"),
      iconName: "database",
      values: models.map((model) => compareValue(formatTokens(model.contextWindowTokens), compactValueRank(model, (row) => row.contextWindowTokens, true))),
    },
    {
      label: tr("compareRows.inputModality"),
      iconName: "arrowDown",
      values: models.map((model) => compareModalityValue(model, "input")),
    },
    {
      label: tr("compareRows.outputModality"),
      iconName: "arrowUp",
      values: models.map((model) => compareModalityValue(model, "output")),
    },
    {
      label: tr("compareRows.inputPrice"),
      iconName: "arrowDown",
      values: models.map((model) => compareValue(formatMoney(model.pricing?.inputPerMillionTokensUsd), joinMeta(tr("table.perMillion"), compactValueRank(model, (row) => row.pricing?.inputPerMillionTokensUsd, false)))),
    },
    {
      label: tr("compareRows.outputPrice"),
      iconName: "arrowUp",
      values: models.map((model) => compareValue(formatMoney(model.pricing?.outputPerMillionTokensUsd), joinMeta(tr("table.perMillion"), compactValueRank(model, (row) => row.pricing?.outputPerMillionTokensUsd, false)))),
    },
    {
      label: tr("table.cache"),
      iconName: "database",
      values: models.map((model) => compareValue(formatMoney(model.pricing?.cacheHitPerMillionTokensUsd), joinMeta(tr("table.perMillion"), compactValueRank(model, (row) => row.pricing?.cacheHitPerMillionTokensUsd, false)))),
    },
    {
      label: tr("compareRows.runCost"),
      iconName: "dollar",
      values: models.map((model) => compareValue(formatMoney(modelCost(model)), compactValueRank(model, modelCost, false))),
    },
    {
      label: tr("compareRows.coverage"),
      iconName: "database",
      values: models.map((model) => compareValue(model.coverageLabel || model.coverage || tr("notAvailable"))),
    },
    ...presetRows,
  ];
}

function compareBenchmarkRows(models) {
  return state.data.metrics
    .filter((metric) => models.some((model) => Number.isFinite(model.scores?.[metric.key])))
    .sort((a, b) => Number(b.defaultWeight || 0) - Number(a.defaultWeight || 0)
      || String(a.category || "").localeCompare(String(b.category || ""))
      || String(a.label || "").localeCompare(String(b.label || "")))
    .map((metric) => ({
      label: metric.label,
      href: benchmarkHref(metric.key),
      iconText: metric.icon || initials(metric.label),
      values: models.map((model) => {
        const value = model.scores?.[metric.key];
        const rank = metricRank(metric.key, model);
        return compareValue(formatMetricValue(value, metric.unit), rank ? `#${rank}` : "");
      }),
    }));
}

function compareValue(value, meta = "") {
  return `
    <span class="compare-value">
      <strong>${escapeHtml(value || tr("notAvailable"))}</strong>
      ${meta ? `<em>${escapeHtml(meta)}</em>` : ""}
    </span>
  `;
}

function compareModalityValue(model, kind) {
  const state = modalitySupportState(model, kind);
  return `
    <span class="compare-value compare-modality-value">
      ${renderModalitySupportGrid(model, kind)}
      <em>${escapeHtml(`${state.supportedCount}/${modalitySpecs.length} ${tr("detailRows.supported")}`)}</em>
    </span>
  `;
}

function compactValueRank(model, accessor, descending) {
  const rank = valueRank(model, accessor, { descending });
  return rank ? `#${rank.rank}/${rank.total}` : "";
}

function joinMeta(...parts) {
  return parts.filter(Boolean).join(" · ");
}

function compareProviderCell(model) {
  const provider = model.creator || tr("unknownCreator");
  return `
    <a class="compare-provider-link" href="${escapeHtml(providerHref(provider, { page: "compare", compareIds: state.compareIds }))}">
      ${renderModelIcon(model)}
      <span>${escapeHtml(provider)}</span>
    </a>
  `;
}

function formatMetricValue(value, unit = "%") {
  if (!Number.isFinite(value)) return tr("notAvailable");
  const suffix = unit === "%" ? "%" : unit ? ` ${unit}` : "";
  return `${formatNumber(value)}${suffix}`;
}

function compareOptionLabel(model) {
  return `${model.model} · ${model.creator || tr("unknownCreator")} · ${formatNumber(modelDisplayScore(model))}`;
}

function rankLabel(model) {
  return model?.rank ? `#${model.rank}` : tr("notAvailable");
}

function renderCompareEntry(model) {
  const href = compareHref([modelRouteId(model)]);
  return `
    <a class="compare-entry-link" href="${escapeHtml(href)}" aria-label="${escapeHtml(`${tr("compareEntry")} ${model.model}`)}">
      ${renderIcon("sliders")}
      <span>${escapeHtml(tr("compareEntry"))}</span>
    </a>
  `;
}

function renderProviderPage(ranked) {
  if (!els.providerDetail) return;
  const providerRows = providerRowsForRoute(ranked);
  if (providerRows.length === 0) {
    document.title = `${tr("providerNotFound")} · ${tr("pageTitle")}`;
    els.providerDetail.innerHTML = `
      <a class="back-link" href="${escapeHtml(providerBackHref())}" data-provider-return>${renderIcon("arrowLeft")}${escapeHtml(tr("back"))}</a>
      <section class="detail-empty">${escapeHtml(tr("providerNotFound"))}</section>
    `;
    return;
  }

  const provider = providerRows[0].creator || tr("unknownCreator");
  const color = providerColor({ creator: provider });
  const best = providerRows[0];
  const averageScore = providerRows.reduce((sum, model) => sum + modelDisplayScore(model), 0) / providerRows.length;
  const openCount = providerRows.filter((model) => sourceType(model) === "open").length;
  document.title = `${provider} · ${tr("pageTitle")}`;
  els.providerDetail.innerHTML = `
    <a class="back-link" href="${escapeHtml(providerBackHref())}" data-provider-return>${renderIcon("arrowLeft")}${escapeHtml(tr("back"))}</a>
    <section class="detail-hero provider-hero" style="--detail-color: ${color}">
      <div class="detail-hero-main">
        ${renderModelIcon(best)}
        <div>
          <p>${escapeHtml(tr("providerPageTitle", { provider }))}</p>
          <h2>${escapeHtml(provider)}</h2>
          <div class="model-meta detail-meta">
            <span>${escapeHtml(tr("providerPageSubtitle", { count: providerRows.length, bestScore: formatNumber(modelDisplayScore(best)) }))}</span>
          </div>
        </div>
      </div>
      <div class="detail-hero-facts">
        <span>${renderIcon("database")}${escapeHtml(tr("providerSummaryModels"))}: ${providerRows.length}</span>
        <span>${renderIcon("trophy")}${escapeHtml(tr("providerSummaryBest"))}: ${escapeHtml(formatNumber(modelDisplayScore(best)))}</span>
        <span>${renderIcon("gauge")}${escapeHtml(tr("providerSummaryAverage"))}: ${escapeHtml(formatNumber(averageScore))}</span>
        <span>${renderIcon("code")}${escapeHtml(tr("providerSummaryOpen"))}: ${openCount}</span>
      </div>
    </section>

    <section class="detail-section">
      <div class="detail-section-head">
        <h2>${escapeHtml(tr("providerModelsTitle"))}</h2>
        <p>${escapeHtml(tr("providerModelsSubtitle"))}</p>
      </div>
      <div class="provider-model-list">
        ${providerRows.map(renderProviderModelRow).join("")}
      </div>
    </section>
  `;
}

function renderProviderModelRow(model) {
  return `
    <a class="provider-model-row" href="${escapeHtml(modelHref(model, "provider", { providerId: providerRouteId(model.creator || tr("unknownCreator")), providerSource: currentProviderBackSource() }))}">
      <span class="rank-number">#${escapeHtml(model.rank)}</span>
      ${renderModelIcon(model)}
      <span class="provider-model-copy">
        <strong>${escapeHtml(model.model)}</strong>
        <em>${escapeHtml(formatDate(model.releaseDate))} · ${escapeHtml(sourceTypeLabel(sourceType(model)))}</em>
      </span>
      <span class="provider-model-stat">
        ${renderIcon("trophy")}
        <b>${escapeHtml(formatNumber(modelDisplayScore(model)))}</b>
      </span>
      <span class="provider-model-stat">
        ${renderIcon("gauge")}
        <b>${escapeHtml(formatSpeed(model.medianOutputSpeed))}</b>
      </span>
      <span class="provider-model-stat">
        ${renderIcon("database")}
        <b>${escapeHtml(formatTokens(model.contextWindowTokens))}</b>
      </span>
      <span class="provider-model-price">${escapeHtml(formatMoney(modelCost(model)))}</span>
    </a>
  `;
}

function providerRowsForRoute(ranked) {
  const routeId = state.providerId || new URLSearchParams(location.search).get("id") || "";
  return ranked
    .filter((model) => providerRouteId(model.creator || tr("unknownCreator")) === routeId)
    .sort((a, b) => (a.rank || Infinity) - (b.rank || Infinity)
      || (parsedReleaseTime(b.releaseDate) || 0) - (parsedReleaseTime(a.releaseDate) || 0)
      || a.model.localeCompare(b.model));
}

function metricDefinition(metricKey) {
  return state.data.metrics.find((metric) => metric.key === metricKey) || {};
}

function renderIcon(name) {
  const paths = {
    arrowLeft: '<path d="M19 12H5"></path><path d="m12 19-7-7 7-7"></path>',
    arrowRight: '<path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path>',
    arrowDown: '<path d="M12 5v14"></path><path d="m19 12-7 7-7-7"></path>',
    arrowUp: '<path d="M12 19V5"></path><path d="m5 12 7-7 7 7"></path>',
    audio: '<path d="M9 18V5l12-2v13"></path><circle cx="6" cy="18" r="3"></circle><circle cx="18" cy="16" r="3"></circle>',
    brain: '<path d="M8 13a4 4 0 0 1-2-7.5A4 4 0 0 1 13 4a4 4 0 0 1 7 2.5A4 4 0 0 1 18 14"></path><path d="M8 13v3a4 4 0 0 0 4 4h1"></path><path d="M16 13v7"></path>',
    calendar: '<path d="M8 2v4"></path><path d="M16 2v4"></path><rect x="3" y="4" width="18" height="18" rx="2"></rect><path d="M3 10h18"></path>',
    code: '<path d="m16 18 6-6-6-6"></path><path d="m8 6-6 6 6 6"></path>',
    database: '<ellipse cx="12" cy="5" rx="8" ry="3"></ellipse><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5"></path><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"></path>',
    dollar: '<path d="M12 2v20"></path><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7H14a3.5 3.5 0 0 1 0 7H6"></path>',
    gauge: '<path d="M12 14l4-4"></path><path d="M3.3 18a10 10 0 1 1 17.4 0"></path>',
    image: '<rect x="3" y="5" width="18" height="14" rx="2"></rect><circle cx="8.5" cy="10.5" r="1.5"></circle><path d="m21 15-5-5L5 19"></path>',
    network: '<rect x="16" y="16" width="6" height="6" rx="1"></rect><rect x="2" y="16" width="6" height="6" rx="1"></rect><rect x="9" y="2" width="6" height="6" rx="1"></rect><path d="M12 8v4"></path><path d="M6 16l6-4 6 4"></path>',
    plus: '<path d="M5 12h14"></path><path d="M12 5v14"></path>',
    sliders: '<path d="M4 21v-7"></path><path d="M4 10V3"></path><path d="M12 21v-9"></path><path d="M12 8V3"></path><path d="M20 21v-5"></path><path d="M20 12V3"></path><path d="M2 14h4"></path><path d="M10 8h4"></path><path d="M18 16h4"></path>',
    text: '<path d="M4 7h16"></path><path d="M4 12h10"></path><path d="M4 17h14"></path>',
    trophy: '<path d="M8 21h8"></path><path d="M12 17v4"></path><path d="M7 4h10v5a5 5 0 0 1-10 0V4Z"></path><path d="M5 6H3a3 3 0 0 0 3 3h1"></path><path d="M19 6h2a3 3 0 0 1-3 3h-1"></path>',
    video: '<rect x="3" y="6" width="13" height="12" rx="2"></rect><path d="m16 10 5-3v10l-5-3"></path>',
    x: '<path d="M18 6 6 18"></path><path d="m6 6 12 12"></path>',
  };
  return `<span class="ui-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${paths[name] || paths.trophy}</svg></span>`;
}

function renderModelIcon(model) {
  const icon = model.modelIcon || {};
  const label = icon.fallbackLabel || icon.label || initials(model.creator || model.model);
  const title = icon.title || model.creator || model.model;
  const src = typeof icon.src === "string" && !/^https?:\/\//i.test(icon.src)
    ? icon.src
    : "";
  const colorStyle = icon.color ? ` style="--provider-color: ${escapeHtml(icon.color)}"` : "";
  const image = src
    ? `<img src="${escapeHtml(src)}" alt="" loading="lazy" referrerpolicy="no-referrer" style="opacity:0" onload="this.style.opacity=1;this.nextElementSibling.hidden=true" onerror="this.hidden=true;this.nextElementSibling.hidden=false" />`
    : "";
  return `<span class="provider-icon" role="img" aria-label="${escapeHtml(title)}"${colorStyle}>${image}<span class="icon-fallback">${escapeHtml(label)}</span></span>`;
}

function renderSourcePill(model) {
  const type = sourceType(model);
  const detail = model.openSourceCategorization || sourceTypeLabel(type);
  return `<span class="pill source-pill" data-source-type="${escapeHtml(type)}" title="${escapeHtml(detail)}">${escapeHtml(sourceTypeLabel(type))}</span>`;
}

function renderLoadError(error) {
  const message = tr("loadFailed", { message: error.message });
  els.rankingBody.innerHTML = `<tr><td class="empty" colspan="10">${escapeHtml(message)}</td></tr>`;
  els.histogramList.innerHTML = `<div class="empty">${escapeHtml(message)}</div>`;
  els.textRanking.innerHTML = `<div class="empty">${escapeHtml(message)}</div>`;
  els.top20Chart.innerHTML = `<div class="empty">${escapeHtml(message)}</div>`;
  if (els.latestModels) els.latestModels.innerHTML = `<div class="empty">${escapeHtml(message)}</div>`;
  els.costScatter.innerHTML = `<div class="empty">${escapeHtml(message)}</div>`;
  els.scoreBands.innerHTML = `<div class="empty">${escapeHtml(message)}</div>`;
  els.providerChart.innerHTML = `<div class="empty">${escapeHtml(message)}</div>`;
  els.sourceExplorer.innerHTML = `<div class="empty">${escapeHtml(message)}</div>`;
  els.modelDetail.innerHTML = `<div class="empty">${escapeHtml(message)}</div>`;
  if (els.providerDetail) els.providerDetail.innerHTML = `<div class="empty">${escapeHtml(message)}</div>`;
  if (els.compareResults) els.compareResults.innerHTML = `<div class="empty">${escapeHtml(message)}</div>`;
}

function presetLabel(id) {
  return tr(`presets.${id}.label`) || state.data.presets[id]?.label || id;
}

function presetDescription(id, preset) {
  return tr(`presets.${id}.description`) || preset.description || "";
}

function sourceType(model) {
  const type = model.openSourceType || "unknown";
  return ["open", "closed", "unknown"].includes(type) ? type : "unknown";
}

function sourceTypeLabel(type) {
  return tr(`sourceTypes.${type}`);
}

function rankForPreset(model, presetId) {
  const preset = state.data.presets[presetId];
  if (!preset) return null;
  const ranked = rankRows(scoreModels(preset, presetId));
  return ranked.find((row) => sameModelIdentity(row, model)) || null;
}

function metricRank(metricKey, model) {
  const rows = state.data.models
    .map((candidate) => ({ candidate, value: candidate.scores?.[metricKey] }))
    .filter((row) => Number.isFinite(row.value))
    .sort((a, b) => b.value - a.value || a.candidate.model.localeCompare(b.candidate.model));
  let previousValue = null;
  let currentRank = 0;
  for (let index = 0; index < rows.length; index += 1) {
    const row = rows[index];
    if (previousValue === null || row.value !== previousValue) {
      currentRank = index + 1;
      previousValue = row.value;
    }
    if (sameModelIdentity(row.candidate, model)) return currentRank;
  }
  return null;
}

function findModelByRoute(models) {
  const routeId = state.modelId || "";
  return models.find((model) => modelRouteId(model) === routeId || model.slug === routeId || model.modelKey === routeId) || null;
}

function sameModelIdentity(a, b) {
  return modelRouteId(a) === modelRouteId(b) || (a.modelKey && a.modelKey === b.modelKey);
}

function modelHref(model, source = state.page, context = {}) {
  const params = new URLSearchParams({ id: modelRouteId(model) });
  const sourceObject = typeof source === "object" ? source : { page: source };
  const sourcePage = context.page || sourceObject.page || "";
  const providerId = context.providerId || sourceObject.providerId || (sourcePage === "provider" ? state.providerId : "");
  const benchmarkId = context.benchmarkId || sourceObject.benchmarkId || (sourcePage === "benchmarks" ? state.benchmarkId : "");
  const compareIds = normalizeCompareIds(context.compareIds || sourceObject.compareIds || (sourcePage === "compare" ? state.compareIds : []));
  const providerSource = context.providerSource || sourceObject.providerSource || null;
  if (sourcePage && sourcePage !== "model") params.set("from", sourcePage);
  if (providerId) params.set("provider", providerId);
  if (benchmarkId) params.set("benchmark", benchmarkId);
  if (compareIds.length) params.set("models", compareIds.join(","));
  if (sourcePage === "ranking") appendRankingParams(params, rankingContextForSource(sourceObject, context));
  if (providerSource?.page) {
    params.set("providerFrom", providerSource.page);
    if (providerSource.benchmarkId) params.set("providerBenchmark", providerSource.benchmarkId);
    if (providerSource.compareIds?.length) params.set("providerModels", normalizeCompareIds(providerSource.compareIds).join(","));
  }
  return `model.html?${params.toString()}`;
}

function modelCompareHref(model) {
  const modelId = modelRouteId(model);
  const source = currentModelBackSource();
  const ids = source.page === "compare"
    ? normalizeCompareIds([...source.compareIds, modelId])
    : [modelId];
  return compareHref(ids, { forceModels: true });
}

function benchmarkHref(metricKey) {
  return `benchmark.html?id=${encodeURIComponent(metricKey)}`;
}

function providerHref(provider, source = state.page, context = {}) {
  const params = new URLSearchParams({ id: providerRouteId(provider) });
  const sourceObject = typeof source === "object" ? source : { page: source };
  const inheritedSource = sourceObject.page === "provider" && sourceObject.providerSource?.page
    ? sourceObject.providerSource
    : sourceObject;
  const sourcePage = context.page || inheritedSource.page || "";
  const benchmarkId = context.benchmarkId || inheritedSource.benchmarkId || (sourcePage === "benchmarks" ? state.benchmarkId : "");
  const compareIds = normalizeCompareIds(context.compareIds || inheritedSource.compareIds || (sourcePage === "compare" ? state.compareIds : []));
  if (sourcePage && sourcePage !== "provider" && sourcePage !== "model") params.set("from", sourcePage);
  if (benchmarkId) params.set("benchmark", benchmarkId);
  if (compareIds.length) params.set("models", compareIds.join(","));
  if (sourcePage === "ranking") appendRankingParams(params, rankingContextForSource(inheritedSource, context));
  return `provider.html?${params.toString()}`;
}

function modelRouteId(model) {
  return String(model.slug || model.modelKey || model.model || "").trim();
}

function providerRouteId(provider) {
  return String(provider || tr("unknownCreator"))
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "") || "unknown";
}

function currentModelBackSource() {
  const params = new URLSearchParams(location.search);
  return {
    page: params.get("from") || "",
    providerId: params.get("provider") || "",
    benchmarkId: params.get("benchmark") || "",
    compareIds: compareIdsFromParams(params),
    ...rankingContextFromParams(params),
    providerSource: {
      page: params.get("providerFrom") || "",
      benchmarkId: params.get("providerBenchmark") || "",
      compareIds: normalizeCompareIds(String(params.get("providerModels") || "").split(",")),
    },
  };
}

function modelBackHref() {
  const source = currentModelBackSource();
  if (source.page === "home") return pageHref("home");
  if (source.page === "ranking") return rankingHref(source);
  if (source.page === "sources") return pageHref("sources");
  if (source.page === "compare") return compareHref(source.compareIds);
  if (source.page === "provider") return source.providerId ? providerHref(source.providerId, source.providerSource) : pageHref("home");
  if (source.page === "benchmarks") return source.benchmarkId ? benchmarkHref(source.benchmarkId) : pageHref("benchmarks");
  return previousSameSiteHref() || pageHref("ranking");
}

function compareHref(compareIds = state.compareIds, { forceModels = false } = {}) {
  const ids = normalizeCompareIds(compareIds);
  const params = new URLSearchParams();
  if (ids.length || forceModels) params.set("models", ids.join(","));
  const query = params.toString();
  return query ? `compare.html?${query}` : pageHref("compare");
}

function currentRankingContext() {
  return {
    presetId: state.presetId,
    viewMode: state.viewMode,
    query: state.query,
    sourceFilter: state.sourceFilter,
    dedupe: state.dedupe,
  };
}

function rankingContextFromParams(params) {
  return {
    presetId: params.get("preset") || "",
    viewMode: params.get("view") || "",
    query: params.get("q") || "",
    sourceFilter: params.get("source") || "",
    dedupe: params.get("dedupe") ?? "",
  };
}

function rankingContextForSource(source = {}, context = {}) {
  return {
    presetId: context.presetId || source.presetId || state.presetId,
    viewMode: context.viewMode || source.viewMode || state.viewMode,
    query: context.query ?? source.query ?? state.query,
    sourceFilter: context.sourceFilter || source.sourceFilter || state.sourceFilter,
    dedupe: context.dedupe ?? source.dedupe ?? state.dedupe,
  };
}

function appendRankingParams(params, context = {}) {
  const presetId = state.data?.presets?.[context.presetId] ? context.presetId : state.presetId;
  const viewMode = viewOrder.includes(context.viewMode) ? context.viewMode : state.viewMode;
  const query = String(context.query || "").trim().toLowerCase();
  const sourceFilter = sourceFilterOrder.includes(context.sourceFilter) ? context.sourceFilter : state.sourceFilter;
  const dedupe = parseDedupeParam(context.dedupe, state.dedupe);
  params.set("preset", presetId);
  params.set("view", viewMode);
  if (query) params.set("q", query);
  params.set("source", sourceFilter);
  params.set("dedupe", dedupe ? "1" : "0");
}

function rankingHref(context = {}) {
  const params = new URLSearchParams();
  appendRankingParams(params, context);
  return `full-rank.html?${params.toString()}`;
}

function currentProviderBackSource() {
  const params = new URLSearchParams(location.search);
  return {
    page: params.get("from") || "home",
    benchmarkId: params.get("benchmark") || "",
    compareIds: compareIdsFromParams(params),
    ...rankingContextFromParams(params),
  };
}

function providerBackHref() {
  const source = currentProviderBackSource();
  if (source.page === "ranking") return rankingHref(source);
  if (source.page === "sources") return pageHref("sources");
  if (source.page === "benchmarks") return source.benchmarkId ? benchmarkHref(source.benchmarkId) : pageHref("benchmarks");
  if (source.page === "compare") return compareHref(source.compareIds);
  return pageHref("home");
}

function addCompareModel(modelId) {
  const id = String(modelId || "").trim();
  if (!id || state.compareIds.includes(id)) return;
  state.compareQuery = "";
  state.comparePickerOpen = false;
  updateCompareSelection([...state.compareIds, id]);
}

function updateCompareSelection(compareIds) {
  state.compareIds = normalizeCompareIds(compareIds);
  state.compareTouched = true;
  if (state.page === "compare") {
    history.replaceState(null, "", compareHref(state.compareIds, { forceModels: true }));
  }
  render();
}

function normalizeCompareIds(compareIds) {
  const seen = new Set();
  return (compareIds || []).map((id) => String(id || "").trim()).filter((id) => {
    if (!id || seen.has(id)) return false;
    seen.add(id);
    return true;
  });
}

function findCompareModel(models, id) {
  return models.find((model) => modelRouteId(model) === id || model.slug === id || model.modelKey === id) || null;
}

function previousSameSiteHref() {
  if (!sameSiteReferrer()) return "";
  const referrer = new URL(document.referrer);
  return `${referrer.pathname.split("/").pop() || "index.html"}${referrer.search}${referrer.hash}`;
}

function sameSiteReferrer() {
  if (!document.referrer) return false;
  try {
    const referrer = new URL(document.referrer);
    const current = new URL(location.href);
    return referrer.origin === current.origin && referrer.href !== current.href;
  } catch {
    return false;
  }
}

function parsedReleaseTime(value) {
  if (!value) return null;
  const time = new Date(value).getTime();
  return Number.isFinite(time) ? time : null;
}
