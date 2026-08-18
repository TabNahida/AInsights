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
      providers: "服务商",
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
      methodRank: "组合四种旧 IRT 审计方法的真实证据名次；默认等权，仅用于敏感性探索。",
      boardScore: "组合方案 18 的五个真实能力板块分；默认五板等权，也可切换几何或最弱板块聚合。",
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
    customMethodWeightsSubtitle: "使用各 IRT 方法的真实 evidence rank；权重为 0 即不纳入。",
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
    metricWeightsTitle: "测试项数据权重",
    metricWeightsSubtitle: "直接参与当前自定义排名的逐项权重，按已有模型数据量排序",
    metricCoverage: "{count} 个模型",
    extensionTestCount: "{count} 个扩展观测",
    scheme18Cap: "动态 cap {cap}",
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
    footerSuffix: "。AIndex 方案 18 使用 AA Core 与已链接的独立 benchmark 扩展来源计算。",
    repository: "仓库",
    rankingItems: "个排名项",
    scorableModels: "个可评分模型",
    unrankedSearchResults: "个未排名目录匹配",
    removedPrefix: "已去除",
    removedSuffix: "个重复档位",
    allTiers: "显示全部档位",
    sourceFilter: "来源",
    top20Title: "AInsights Index Top {count}",
    top20Subtitle: "按预计算的方案 18 AIndex score 降序生成名次；数值和柱宽均表示同一个 AIndex 分数（points）",
    latestModelsTitle: "最新模型",
    latestModelsSubtitle: "按发布日期展示最近进入数据集的去重模型",
    fullRanking: "查看完整排名",
    costScatterTitle: "排名模型最低可用价",
    costScatterSubtitle: "先固定 AInsights Top 10 / Top 50，再从有明确来源的可比报价中选择每个模型的最低价",
    priceTop10Title: "Top 10 · 最低价",
    priceTop10Subtitle: "前十名中有来源报价的模型里，价格最低的 {count} 个",
    priceTop50Title: "Top 50 · 最低价",
    priceTop50Subtitle: "前五十名中有来源报价的模型里，价格最低的 {count} 个",
    priceComparableShort: "可比 $/M",
    priceMixShort: "Coding Mix",
    priceIncludedShort: "额度内 $/M",
    pricingPerMonth: "每月",
    pricingPerYear: "每年",
    pricingMonthlyEquivalent: "月均",
    pricingUsageCreditsOnly: "仅可使用额外 Usage Credits",
    pricingWeeklyLimitShare: "最多占订阅周额度 {percent}%",
    pricingWeeklyCredits: "{credits} Credits / 周",
    pricingPerIncludedCredit: "{price} / 额度 Credit",
    pricingCallsPerFiveHours: "{calls} 次 / 5 小时",
    pricingCallsPerWeek: "{calls} 次 / 周",
    pricingCallsPerMonth: "{calls} 次 / 月",
    pricingOffPeakCredits: "低峰 {time}：积分消耗 ×{multiplier}",
    priceListEmpty: "固定排名范围内暂无可比较价格",
    pricingAsOf: "价格核验于 {date}",
    pricingViewProviders: "比较全部服务商",
    pricingMethodNote: "可比 $/M：API 按 Coding Mix（20% 新输入 + 70% 缓存输入 + 10% 输出；无缓存价时按新输入价）；长上下文阈值前展示基础费率，阈值价逐报价列出。Token/Coding Plan 仅在公开逐模型积分公式或固定 Token 额度时按满额使用折算。依据请求范围估算的订阅、标有“最高可得”的权益，以及未折入订阅门槛费的边际/超额费率只在模型详情展示，不进入最低价排名。人民币报价按核验日 ECB 参考汇率换算并保留本币价。",
    pricingSectionTitle: "实际可用 Token 价格",
    pricingSectionSubtitle: "仅展示明确支持当前模型且能计算出价格的官方 API、聚合中转、Token Plan 与 Coding Plan；N/A 报价自动隐藏。",
    pricingNoOffers: "这个模型暂无已收录、明确支持且能计算价格的服务商报价",
    pricingObserved: "模型 API 参考价",
    pricingSource: "价格来源",
    pricingPlanTypes: {
      all: "全部方案",
      token: "API / Token",
      subscription: "Token Plan",
      coding: "Coding Plan",
    },
    pricingLabels: {
      input: "输入",
      cache: "缓存",
      output: "输出",
      effective: "混合价",
      included: "包含 Token",
      monthly: "月费",
      quota: "额度",
      unavailable: "不可直接换算",
      estimate: "估算",
      displayOnly: "仅展示",
      official: "官方",
      aggregator: "聚合",
      source: "来源",
      models: "覆盖模型",
      offers: "报价",
      regions: "可用区域",
      billing: "计费",
      context: "上下文",
      activeEndpoint: "活跃端点",
      endpointStatus: "端点状态",
      dynamicEndpoint: "动态路由",
      quantization: "量化",
      observed: "观测于",
      pricingOverride: "价格覆盖",
      promptThreshold: "提示词 ≥ {tokens}",
    },
    pricingProvidersTitle: "Token 与 Coding 服务商",
    pricingProvidersSubtitle: "比较官方 API、聚合中转、Token Plan 与 Coding Plan；最低价仅使用有证据、标为可比并明确注明 Coding Mix 或额度内口径的报价。",
    pricingProvidersStats: {
      providers: "服务商",
      plans: "套餐",
      comparable: "可比报价",
      models: "已映射模型",
    },
    pricingProviderSearchLabel: "搜索 Provider",
    pricingProviderSearchPlaceholder: "按服务商名称查找",
    pricingModelSearchLabel: "搜索模型",
    pricingModelSearchPlaceholder: "按模型名称或 slug 查找",
    pricingProviderSearchEmpty: "没有符合当前方案类型与搜索条件的服务商",
    pricingProviderOffers: "模型与报价明细",
    pricingProviderNoOffers: "当前方案类型暂无已映射的模型报价",
    pricingFooter: "定价来源：公开官方定价页、聚合服务目录与列明的估算来源。",
    pricingProviderTypes: {
      "first-party": "官方服务",
      "first-party-api": "官方 API",
      aggregator: "聚合中转",
      "token-plan": "Token Plan",
      "coding-subscription": "Coding 订阅",
      "coding-platform": "Coding 平台",
    },
    scatterXAxis: "运行 Intelligence Index 的成本（USD，对数）",
    scatterYAxis: "AInsights 能力分",
    attractiveQuadrant: "高分低成本区域",
    noCostData: "没有足够的成本数据可绘制散点图",
    scoreBandsTitle: "AInsights 能力分分布",
    scoreBandsSubtitle: "去重模型在方案 18 AIndex 各分数区间的分布",
    providerChartTitle: "机构覆盖",
    providerChartSubtitle: "按可评分去重模型数量和最高分展示",
    providerModelCount: "模型数量",
    providerBestScore: "最高分",
    providerPageTitle: "{provider} 模型概览",
    providerPageSubtitle: "{count} 个去重目录模型 · 已排名最高分 {bestScore} points",
    providerNotFound: "没有找到这个机构",
    providerSummaryModels: "目录模型",
    providerSummaryBest: "最高分",
    providerSummaryAverage: "平均分",
    providerSummaryOpen: "开源模型",
    providerModelsTitle: "模型列表",
    providerModelsSubtitle: "已排名模型按方案 18 AIndex 名次优先，未排名模型明确标为暂无分数",
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
      score: "AInsights 分数",
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
    sourceExplorerSubtitle: "AA Core 与已链接的独立 benchmark 扩展来源，并列展示计分角色与协议",
    detailRankTitle: "排名快照",
    detailRadarSubtitle: "五个 IRT 能力板块加证据覆盖度；外圈为 100 分，橙色为入榜模型平均值",
    detailBenchmarkTitle: "Benchmark Lab 参考项目",
    detailBenchmarkSubtitle: "均衡逐项实验模板中的测试项；它们不作为主榜固定权重。",
    detailExternalTitle: "非参考项目分数",
    detailExternalSubtitle: "AA 子项、官方发布页及其他公开测评：其中一部分作为方案 18 的只增益扩展项参与计分，其余为排除项或仅用于 Custom Weight",
    detailCostTitle: "Detail",
    detailVariantsTitle: "同模型档位",
    detailSourcesTitle: "外部测评参考",
    radarAverage: "入榜模型平均值",
    radarDataSource: "数据来源",
    radarSourceText: "AIndex 方案 18 / 真实 Core 与列明的扩展 benchmark 成绩",
    radarBasisTitle: "雷达维度口径",
    radarBasisSubtitle: "五个能力轴直接读取方案 18 板块分；扩展覆盖轴只反映稀疏证据广度，不修正能力分，也不参与排名。",
    radarCoverage: "{available}/{total} 项测试",
    radarTestCount: "{available} 项测试",
    radarDualCoverage: "Core {coreAvailable}/{coreTotal} · 扩展 {extensionAvailable}/{extensionTotal}",
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
      evidenceCoverage: "extensionCoverageScore：五板块扩展测试覆盖广度，仅作证据充分度参考。",
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
    benchmarkReference: "AIndex 计分项",
    benchmarkNonReference: "不进入 AIndex",
    benchmarkCore: "Core 必做项",
    benchmarkExtension: "扩展加分项",
    benchmarkExcluded: "明确排除",
    benchmarkCustomOnly: "仅 Custom 工具",
    benchmarkSourcesOnly: "来源",
    notAvailable: "暂无",
    unranked: "未排名",
    homeStats: {
      leader: "领先模型",
      topOpen: "开源领先",
      bestValue: "高分低成本",
      modelCount: "去重模型",
      byScore: "按 AInsights 分数",
      perRun: "运行成本",
      source: "来源",
    },
    headers: {
      model: "模型",
      score: "分数",
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
        calculation: "scheme-18",
        normalization: "none",
        description: "方案 18：各板 Core 真实百分成绩取不加权几何均值，独立控制的扩展测试只以匿名趋势之上的正残差加分，并受动态统一 cap 限制；五板等分相加。",
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
      providers: "Providers",
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
      methodRank: "Combine observed ranks from four legacy IRT audit methods; the default is equal weights and remains sensitivity-only.",
      boardScore: "Combine the five observed Scheme 18 board scores; the default is equal boards, with geometric and weakest-board alternatives.",
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
    customMethodWeightsSubtitle: "Uses the observed evidence rank from each IRT method; a zero weight excludes the method.",
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
    metricWeightsTitle: "Evaluation data weights",
    metricWeightsSubtitle: "Fine-grained weights used directly by the custom ranking, sorted by model coverage",
    metricCoverage: "{count} models",
    extensionTestCount: "{count} extension observations",
    scheme18Cap: "dynamic cap {cap}",
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
    footerSuffix: ". Scheme 18 AIndex uses AA Core and linked, independently controlled benchmark extensions.",
    repository: "Repository",
    rankingItems: "ranked items",
    scorableModels: "scorable models",
    unrankedSearchResults: "unranked catalog matches",
    removedPrefix: "Removed",
    removedSuffix: "duplicate tiers",
    allTiers: "Showing every tier",
    sourceFilter: "Source",
    top20Title: "AInsights Index Top {count}",
    top20Subtitle: "Ranked directly by the precomputed Scheme 18 AIndex score; the value and bar encode the same AIndex points",
    latestModelsTitle: "Latest models",
    latestModelsSubtitle: "Recently released deduplicated models in the dataset",
    fullRanking: "View full ranking",
    costScatterTitle: "Cheapest usable prices for ranked models",
    costScatterSubtitle: "Freeze the AInsights Top 10 / Top 50 first, then select each model's lowest sourced comparable offer",
    priceTop10Title: "Top 10 · lowest price",
    priceTop10Subtitle: "The {count} least expensive models with sourced offers inside the Top 10",
    priceTop50Title: "Top 50 · lowest price",
    priceTop50Subtitle: "The {count} least expensive models with sourced offers inside the Top 50",
    priceComparableShort: "Comparable $/M",
    priceMixShort: "Coding Mix",
    priceIncludedShort: "Included $/M",
    pricingPerMonth: "per month",
    pricingPerYear: "per year",
    pricingMonthlyEquivalent: "monthly equivalent",
    pricingUsageCreditsOnly: "Requires separate Usage Credits",
    pricingWeeklyLimitShare: "Up to {percent}% of the weekly subscription limit",
    pricingWeeklyCredits: "{credits} Credits / week",
    pricingPerIncludedCredit: "{price} / included Credit",
    pricingCallsPerFiveHours: "{calls} calls / 5 hours",
    pricingCallsPerWeek: "{calls} calls / week",
    pricingCallsPerMonth: "{calls} calls / month",
    pricingOffPeakCredits: "Off-peak {time}: credit usage ×{multiplier}",
    priceListEmpty: "No comparable prices in this fixed ranking cohort",
    pricingAsOf: "Prices checked {date}",
    pricingViewProviders: "Compare all providers",
    pricingMethodNote: "Comparable $/M: APIs use a Coding Mix of 20% new input + 70% cached input + 10% output (new-input price substitutes for missing cache rates). Listed API prices are base rates before long-context thresholds; threshold rows are shown per offer. Token/Coding Plans are normalized at full utilization only when a per-model credit formula or fixed token quota is public. Request-range subscription estimates, ‘up to’ benefits, and marginal/overage rates that exclude a prerequisite subscription fee are display-only and never enter cheapest-price lists. CNY prices use the checked-date ECB reference cross-rate and retain the local amount.",
    pricingSectionTitle: "Usable token prices",
    pricingSectionSubtitle: "Only first-party APIs, aggregators, Token Plans, and Coding Plans that explicitly support this model and have a calculable price are shown. N/A offers are hidden.",
    pricingNoOffers: "No catalogued provider explicitly supports this model with a calculable price",
    pricingObserved: "Model API reference",
    pricingSource: "Pricing source",
    pricingPlanTypes: {
      all: "All plans",
      token: "API / Token",
      subscription: "Token Plan",
      coding: "Coding Plan",
    },
    pricingLabels: {
      input: "Input",
      cache: "Cache",
      output: "Output",
      effective: "Blended",
      included: "Included tokens",
      monthly: "Monthly",
      quota: "Quota",
      unavailable: "Not directly convertible",
      estimate: "Estimate",
      displayOnly: "Display only",
      official: "First-party",
      aggregator: "Aggregator",
      source: "Source",
      models: "Models",
      offers: "Offers",
      regions: "Regions",
      billing: "Billing",
      context: "Context",
      activeEndpoint: "Active endpoint",
      endpointStatus: "Endpoint status",
      dynamicEndpoint: "Dynamic route",
      quantization: "Quantization",
      observed: "Observed",
      pricingOverride: "Pricing override",
      promptThreshold: "Prompt ≥ {tokens}",
    },
    pricingProvidersTitle: "Token and coding providers",
    pricingProvidersSubtitle: "Compare first-party APIs, aggregators, Token Plans, and Coding Plans. Cheapest-price lists use only evidenced offers marked comparable and label each as Coding Mix or included-quota pricing.",
    pricingProvidersStats: {
      providers: "Providers",
      plans: "Plans",
      comparable: "Comparable offers",
      models: "Mapped models",
    },
    pricingProviderSearchLabel: "Search providers",
    pricingProviderSearchPlaceholder: "Find a provider by name",
    pricingModelSearchLabel: "Search models",
    pricingModelSearchPlaceholder: "Find a model by name or slug",
    pricingProviderSearchEmpty: "No providers match the current plan type and searches",
    pricingProviderOffers: "Model offer details",
    pricingProviderNoOffers: "No mapped model offers are available for this plan type",
    pricingFooter: "Pricing sources: public official pricing pages, aggregator catalogs, and explicitly identified estimate sources.",
    pricingProviderTypes: {
      "first-party": "First-party",
      "first-party-api": "First-party API",
      aggregator: "Aggregator",
      "token-plan": "Token plan",
      "coding-subscription": "Coding subscription",
      "coding-platform": "Coding platform",
    },
    scatterXAxis: "Cost to Run Intelligence Index (USD, Log Scale)",
    scatterYAxis: "AInsights points",
    attractiveQuadrant: "High-score low-cost region",
    noCostData: "Not enough cost data to draw the scatter chart",
    scoreBandsTitle: "AInsights point distribution",
    scoreBandsSubtitle: "Where deduplicated models fall across Scheme 18 AIndex score bands",
    providerChartTitle: "Provider coverage",
    providerChartSubtitle: "Scorable deduped model count and best score by lab",
    providerModelCount: "Model count",
    providerBestScore: "Highest points",
    providerPageTitle: "{provider} model overview",
    providerPageSubtitle: "{count} deduplicated catalog models · highest ranked score {bestScore} points",
    providerNotFound: "Provider not found",
    providerSummaryModels: "Catalog models",
    providerSummaryBest: "Highest points",
    providerSummaryAverage: "Average points",
    providerSummaryOpen: "Open models",
    providerModelsTitle: "Model list",
    providerModelsSubtitle: "Ranked models come first by Scheme 18 AIndex; unranked catalog models are clearly marked N/A",
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
      score: "AInsights points",
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
    sourceExplorerSubtitle: "AA Core and linked, independently controlled benchmark extensions, with scoring roles and protocols shown side by side",
    detailRankTitle: "Rank snapshot",
    detailRadarSubtitle: "Five IRT capability boards plus evidence coverage; the outer ring is 100 and orange is the ranked-model average",
    detailBenchmarkTitle: "Benchmark Lab reference set",
    detailBenchmarkSubtitle: "Benchmarks in the balanced per-item experiment template; these are not fixed primary-ranking weights.",
    detailExternalTitle: "Non-reference benchmark scores",
    detailExternalSubtitle: "AA submetrics, official release scores, and other public evaluations: some are only-add Scheme 18 extensions; others are excluded or Custom-only",
    detailCostTitle: "Detail",
    detailVariantsTitle: "Same-model tiers",
    detailSourcesTitle: "External evaluation references",
    radarAverage: "Ranked-model average",
    radarDataSource: "Sources",
    radarSourceText: "AIndex Scheme 18 / observed Core and listed extension benchmarks",
    radarBasisTitle: "Radar axis basis",
    radarBasisSubtitle: "The five capability axes read Scheme 18 board scores directly. Extension coverage only shows sparse-evidence breadth; it neither adjusts capability scores nor affects rank.",
    radarCoverage: "{available}/{total} tests",
    radarTestCount: "{available} tests",
    radarDualCoverage: "Core {coreAvailable}/{coreTotal} · Extension {extensionAvailable}/{extensionTotal}",
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
      evidenceCoverage: "extensionCoverageScore: extension-test breadth across the five boards, shown only as evidence sufficiency.",
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
    benchmarkReference: "AIndex scoring item",
    benchmarkNonReference: "Not used by AIndex",
    benchmarkCore: "Required Core",
    benchmarkExtension: "Only-add extension",
    benchmarkExcluded: "Explicitly excluded",
    benchmarkCustomOnly: "Custom tools only",
    benchmarkSourcesOnly: "Sources",
    notAvailable: "N/A",
    unranked: "Unranked",
    homeStats: {
      leader: "Leader",
      topOpen: "Top open",
      bestValue: "High-score low-cost",
      modelCount: "Deduplicated models",
      byScore: "By AInsights points",
      perRun: "run cost",
      source: "Source",
    },
    headers: {
      model: "Model",
      score: "Points",
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
        calculation: "scheme-18",
        normalization: "none",
        description: "Scheme 18 takes an unweighted geometric mean of each board's real Core percentages, adds only positive residual evidence from independent-controller extensions under one dynamic cap, and sums five equal board contributions.",
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
    rasch: 25,
    sparseRasch: 25,
    twopl: 25,
    denseRasch: 25,
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
  pricingProviderFilter: "all",
  pricingProviderQuery: "",
  pricingModelQuery: "",
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
  pricingProviderView: document.querySelector("#pricingProviderView"),
  pricingProviderDetail: document.querySelector("#pricingProviderDetail"),
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
const pageOrder = ["home", "ranking", "compare", "providers", "benchmarks", "sources", "contribute"];
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
  els.siteFooter.innerHTML = state.page === "providers"
    ? `${escapeHtml(tr("pricingFooter"))} · <a href="https://github.com/TabNahida/AInsights" target="_blank" rel="noreferrer">${escapeHtml(tr("repository"))}: TabNahida/AInsights</a>`
    : `${escapeHtml(tr("footerPrefix"))}<a href="${escapeHtml(state.data.source.url)}" target="_blank" rel="noreferrer">${escapeHtml(state.data.source.label || "AA Core + benchmark extensions")}</a> · <a href="${escapeHtml(pageHref("sources"))}">${escapeHtml(tr("sourcesBadge", { count: catalogSources().length }))}</a>${escapeHtml(tr("footerSuffix"))} · <a href="https://github.com/TabNahida/AInsights" target="_blank" rel="noreferrer">${escapeHtml(tr("repository"))}: TabNahida/AInsights</a>`;

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
  if (els.pricingProviderView) els.pricingProviderView.hidden = state.page !== "providers";
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
  const homeScored = scoreModels(homePreset, "zhihu-adjusted", "variant-group");
  const homeRanked = rankRows(dedupeByBestVariant(homeScored));
  const compareRanked = rankRows(homeScored);
  const filtered = scored.filter(matchesQuery).filter(matchesSourceFilter);
  const rankingUniverse = state.dedupe ? dedupeByBestVariant(scored) : scored;
  const ranked = rankRows(rankingUniverse).filter(matchesQuery).filter(matchesSourceFilter);
  const unrankedMatches = state.query
    ? unrankedCatalogModels(scored, {
      dedupe: state.dedupe,
      representedModels: rankingUniverse,
    }).filter(matchesQuery).filter(matchesSourceFilter)
    : [];
  const allRanked = rankRows(scored);
  const homeDisplayModels = mergeRankedWithUnscored(homeRanked, homeScored, { dedupe: true });
  const compareDisplayModels = mergeRankedWithUnscored(compareRanked, homeScored);
  const allDisplayModels = mergeRankedWithUnscored(allRanked, scored);

  if (!els.homeView.hidden) renderHome(homeRanked, homeDisplayModels);
  if (!els.rankingView.hidden) {
    els.scoreHeader.textContent = tr(scoreHeaderKeyForPreset(preset));
    renderSummary(filtered.length, ranked.length, scored.length, preset, unrankedMatches.length);
    renderRankings([...ranked, ...unrankedMatches]);
  }
  if (!els.modelView.hidden) renderModelDetail(allDisplayModels, preset);
  if (!els.benchmarkView.hidden) renderBenchmarkPage();
  if (els.providerView && !els.providerView.hidden) renderProviderPage(homeDisplayModels);
  if (els.pricingProviderView && !els.pricingProviderView.hidden) renderPricingProvidersPage(homeRanked);
  if (els.compareView && !els.compareView.hidden) renderComparePage(compareDisplayModels);
}

function mergeRankedWithUnscored(ranked, scoredUniverse = ranked, options = {}) {
  return [
    ...ranked,
    ...unrankedCatalogModels(scoredUniverse, {
      ...options,
      representedModels: ranked,
    }),
  ];
}

function unrankedCatalogModels(scoredUniverse, options = {}) {
  const scoredIds = new Set(scoredUniverse.map(modelRouteId));
  let unranked = state.data.models.filter((model) => !scoredIds.has(modelRouteId(model)));
  if (options.dedupe) {
    const representedGroups = new Set(
      (options.representedModels || []).map((model) => model.variantGroup).filter(Boolean),
    );
    const bestByGroup = new Map();
    for (const model of unranked) {
      if (representedGroups.has(model.variantGroup)) continue;
      const group = model.variantGroup || modelRouteId(model);
      const current = bestByGroup.get(group);
      if (!current || Number(model.variantPriority || 0) > Number(current.variantPriority || 0)) {
        bestByGroup.set(group, model);
      }
    }
    unranked = [...bestByGroup.values()];
  }
  return unranked.map((model) => ({
    ...model,
    score: null,
    displayScore: null,
    rank: null,
    coverage: 0,
    coverageLabel: tr("notAvailable"),
    availableWeight: 0,
    scoreMeta: tr("notAvailable"),
  }));
}

function scoreModels(
  preset,
  presetId = state.presetId,
  rankingGrain = state.dedupe ? "variant-group" : "exact-config",
) {
  return state.data.models
    .map((sourceModel) => {
      const model = modelForRankingGrain(sourceModel, rankingGrain);
      const result = scoreModel(model, preset, presetId);
      return {
        ...model,
        ...result,
      };
    })
    .filter((model) => Number.isFinite(model.score));
}

function modelForRankingGrain(model, rankingGrain) {
  if (rankingGrain !== "exact-config") return model;
  return {
    ...model,
    rankingProfile: model?.exactRankingProfile || null,
  };
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
  const finalScore = Number(profile?.displayScore);
  const generatedScoreRank = Number(profile?.publicationRank);
  if (
    profile?.displayScore === null
    || profile?.displayScore === undefined
    || profile?.displayScore === ""
    || !Number.isFinite(finalScore)
  ) {
    return {
      score: null,
      displayScore: null,
      coverage: 0,
      coverageLabel: tr("notAvailable"),
      availableWeight: 0,
      scoreMeta: tr("notAvailable"),
    };
  }
  const extensionTests = Number(profile.extensionTestsTotal || 0);
  const bonusCap = Number(profile.bonusCap);
  const evidenceTier = String(profile.evidenceTier || "").trim();
  return {
    score: finalScore,
    displayScore: finalScore,
    scoreBarValue: finalScore,
    scoreRank: Number.isInteger(generatedScoreRank) && generatedScoreRank > 0 ? generatedScoreRank : null,
    isPrecomputedScoreRanking: true,
    coverage: extensionTests,
    coverageLabel: [
      evidenceTier,
      tr("extensionTestCount", { count: extensionTests }),
    ].filter(Boolean).join(" · "),
    availableWeight: 100,
    scoreMeta: Number.isFinite(bonusCap)
      ? tr("scheme18Cap", { cap: formatNumber(bonusCap) })
      : "Scheme 18",
  };
}

function rankingMethodEvidenceRank(model, methodId) {
  const value = Number(model?.rankingProfile?.methods?.[methodId]?.evidenceRank);
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
  const configured = Number(
    state.dedupe
      ? state.data?.leaderboard?.populationSize
      : state.data?.leaderboard?.exactPopulationSize,
  );
  if (Number.isFinite(configured) && configured > 1) return configured;
  const profileKey = state.dedupe ? "rankingProfile" : "exactRankingProfile";
  const count = (state.data?.models || []).filter((model) => model[profileKey]).length;
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
  const aliases = Array.isArray(model.externalModelAliases)
    ? model.externalModelAliases.join(" ")
    : "";
  const haystack = `${model.model} ${model.modelKey || ""} ${model.creator} ${model.slug} ${aliases}`.toLowerCase();
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

function formatModelDisplayScore(model) {
  const value = modelDisplayScore(model);
  if (!Number.isFinite(value)) return tr("notAvailable");
  return model?.isPrecomputedScoreRanking && Number.isFinite(value)
    ? value.toFixed(3)
    : formatNumber(value);
}

function modelScoreBarValue(model) {
  const value = Number.isFinite(model?.scoreBarValue) ? model.scoreBarValue : model?.score;
  return clamp(Number(value) || 0, 0, 100);
}

function rankRows(models) {
  const sorted = [...models].sort(compareRankingRows);
  if (
    sorted.length
    && sorted.every((model) => (
      model.isPrecomputedScoreRanking
      && Number.isInteger(model.scoreRank)
      && model.scoreRank > 0
    ))
  ) {
    return sorted.map((model) => ({
      ...model,
      rank: model.scoreRank,
    }));
  }
  let previousScore = null;
  let currentRank = 0;
  return sorted.map((model, index) => {
    if (previousScore === null || model.score !== previousScore) {
      currentRank = index + 1;
      previousScore = model.score;
    }
    return {
      ...model,
      rank: currentRank,
    };
  });
}

function compareRankingRows(a, b) {
  const scoreDifference = b.score - a.score;
  if (scoreDifference) return scoreDifference;
  if (
    a.isPrecomputedScoreRanking
    && b.isPrecomputedScoreRanking
    && Number.isInteger(a.scoreRank)
    && Number.isInteger(b.scoreRank)
  ) {
    const generatedRankDifference = a.scoreRank - b.scoreRank;
    if (generatedRankDifference) return generatedRankDifference;
  }
  if (a.customMethodRanking && b.customMethodRanking) {
    const worstDifference = Number(a.customRankMax) - Number(b.customRankMax);
    if (worstDifference) return worstDifference;
    const bestDifference = Number(a.customRankMin) - Number(b.customRankMin);
    if (bestDifference) return bestDifference;
  }
  return String(a.modelKey || a.slug || a.model).localeCompare(String(b.modelKey || b.slug || b.model));
}

function scoreHeaderKeyForPreset(preset) {
  if (state.presetId === "custom" && state.customToolMode === "method-rank") return "headers.rankMean";
  return "headers.score";
}

function methodRankTitle(evidenceRank) {
  return Number.isFinite(evidenceRank) ? `${tr("evidenceRankLabel")} #${evidenceRank}` : tr("notAvailable");
}

function renderSummary(filteredCount, visibleCount, scoredCount, preset, unrankedCount = 0) {
  const removed = filteredCount - visibleCount;
  const dedupeLabel = state.dedupe
    ? `${escapeHtml(tr("removedPrefix"))} <strong>${removed}</strong> ${escapeHtml(tr("removedSuffix"))}`
    : escapeHtml(tr("allTiers"));
  els.summaryRow.innerHTML = `
    <span><strong>${visibleCount}</strong> ${escapeHtml(tr("rankingItems"))}</span>
    <span><strong>${scoredCount}</strong> ${escapeHtml(tr("scorableModels"))}</span>
    ${unrankedCount > 0 ? `<span><strong>${unrankedCount}</strong> ${escapeHtml(tr("unrankedSearchResults"))}</span>` : ""}
    <span>${dedupeLabel}</span>
    <span>${escapeHtml(tr("sourceFilter"))}: <strong>${escapeHtml(tr(`sourceFilters.${state.sourceFilter}`))}</strong></span>
    <a href="${escapeHtml(methodologyPageHref)}">${escapeHtml(tr("methodologyLink"))}</a>
  `;
}

function resetCustomConfiguration() {
  state.customToolMode = "method-rank";
  state.customMethodWeights = { rasch: 25, sparseRasch: 25, twopl: 25, denseRasch: 25 };
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
    state.customMethodWeights = { rasch: 25, sparseRasch: 25, twopl: 25, denseRasch: 25 };
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
  renderPriceLeaderboards(models);
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
        <span class="latest-model-score">${renderIcon("trophy")}<b>${escapeHtml(formatModelDisplayScore(model))}</b></span>
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
      meta: `${formatModelDisplayScore(leader)} · ${leader.creator || tr("unknownCreator")}`,
    },
    {
      label: tr("homeStats.topOpen"),
      model: topOpen,
      meta: topOpen ? `${formatModelDisplayScore(topOpen)} · ${topOpen.creator || tr("unknownCreator")}` : "—",
    },
    {
      label: tr("homeStats.bestValue"),
      model: bestValue,
      meta: bestValue ? `${formatModelDisplayScore(bestValue)} · ${formatMoney(modelCost(bestValue))} ${tr("homeStats.perRun")}` : "—",
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
            <span class="top-bar-value">${formatModelDisplayScore(model)}</span>
          </article>
        `;
      }).join("")}
    </div>
  `;
}

const HOME_PRICE_LIST_LIMIT = 6;
// `init()` runs before this source location when models.js is already warm in
// the browser. `var` is intentionally hoisted so the cache is available in
// that synchronous startup path as well as the async JSON fallback path.
var pricingCatalogRuntimeCache = null;

function providerPricingCatalog() {
  return state.data?.providerPricing || {};
}

function pricingProviders() {
  return Array.isArray(providerPricingCatalog().providers) ? providerPricingCatalog().providers : [];
}

function pricingPlans() {
  return Array.isArray(providerPricingCatalog().plans) ? providerPricingCatalog().plans : [];
}

function pricingSources() {
  return Array.isArray(providerPricingCatalog().sources) ? providerPricingCatalog().sources : [];
}

function pricingCatalogIndexes() {
  const catalog = providerPricingCatalog();
  if (!pricingCatalogRuntimeCache || pricingCatalogRuntimeCache.catalog !== catalog) {
    pricingCatalogRuntimeCache = {
      catalog,
      providersById: new Map(pricingProviders().map((provider) => [provider.id, provider])),
      plansById: new Map(pricingPlans().map((plan) => [plan.id, plan])),
      sourcesById: new Map(pricingSources().map((source) => [source.id, source])),
      expandedOffers: null,
      normalizedLanguage: "",
      normalizedOffers: null,
      offersByModelSlug: null,
    };
  }
  return pricingCatalogRuntimeCache;
}

function expandedPricingCatalogOffers() {
  const cache = pricingCatalogIndexes();
  if (cache.expandedOffers) return cache.expandedOffers;
  const offers = Array.isArray(providerPricingCatalog().offers) ? providerPricingCatalog().offers : [];
  cache.expandedOffers = offers.flatMap((offer) => {
    const variants = Array.isArray(offer.planVariants) ? offer.planVariants : [];
    const expanded = variants.map((variant) => {
      const multiplier = firstFinite(variant.rateMultiplier, 1);
      const scaled = (field) => {
        const explicit = firstFinite(variant[field]);
        const base = firstFinite(offer[field]);
        return Number.isFinite(explicit) ? explicit : (Number.isFinite(base) ? base * multiplier : null);
      };
      return {
        ...offer,
        ...variant,
        id: `${offer.id}:${variant.idSuffix || variant.planId}`,
        inputPerMillionTokensUsd: scaled("inputPerMillionTokensUsd"),
        cacheReadPerMillionTokensUsd: scaled("cacheReadPerMillionTokensUsd"),
        outputPerMillionTokensUsd: scaled("outputPerMillionTokensUsd"),
        effectiveUsdPerMillionTokens: scaled("effectiveUsdPerMillionTokens"),
        planVariants: undefined,
      };
    });
    return [{ ...offer, planVariants: undefined }, ...expanded];
  });
  return cache.expandedOffers;
}

function pricingProviderById(providerId) {
  return pricingCatalogIndexes().providersById.get(providerId) || null;
}

function pricingPlanById(planId) {
  return pricingCatalogIndexes().plansById.get(planId) || null;
}

function pricingSourceById(sourceId) {
  return pricingCatalogIndexes().sourcesById.get(sourceId) || null;
}

function catalogOfferModelSlugs(offer) {
  const direct = offer.modelSlugs || offer.appliesTo?.slugs || [];
  return [...new Set(direct)];
}

function firstFinite(...values) {
  for (const value of values) {
    const numeric = Number(value);
    if (value !== null && value !== "" && Number.isFinite(numeric)) return numeric;
  }
  return null;
}

function pricingCurrencyFor(offer = {}, fallback = {}) {
  const plan = pricingPlanById(offer.planId || fallback.planId) || {};
  return String(
    offer.currency
      || fallback.currency
      || plan.currency
      || providerPricingCatalog().currency
      || "USD",
  ).toUpperCase();
}

function pricingExchangeRate(currency) {
  const normalized = String(currency || "USD").toUpperCase();
  if (normalized === "USD") return { currency: normalized, usdPerUnit: 1 };
  const entry = providerPricingCatalog().exchangeRates?.[normalized] || {};
  return {
    currency: normalized,
    usdPerUnit: firstFinite(entry.usdPerUnit),
    unitsPerUsd: firstFinite(entry.unitsPerUsd),
    asOf: entry.asOf || "",
    sourceId: entry.sourceId || "",
  };
}

function pricingUsdFromLocal(value, currency) {
  const local = firstFinite(value);
  const rate = pricingExchangeRate(currency).usdPerUnit;
  return Number.isFinite(local) && Number.isFinite(rate) ? local * rate : null;
}

function catalogOfferLocalRates(offer, fallback = {}) {
  const currency = pricingCurrencyFor(offer, fallback);
  if (currency === "USD") return { input: null, cache: null, output: null };
  const rates = offer.localRates || offer.rates || offer.rate || {};
  return {
    input: firstFinite(offer.inputPerMillionTokensLocal, rates.input),
    cache: firstFinite(
      offer.cacheReadPerMillionTokensLocal,
      offer.cacheHitPerMillionTokensLocal,
      rates.cache,
      rates.cachedInput,
    ),
    output: firstFinite(offer.outputPerMillionTokensLocal, rates.output),
  };
}

function catalogOfferRates(offer, fallback = {}) {
  const rates = offer.rates || offer.rate || {};
  const currency = pricingCurrencyFor(offer, fallback);
  const genericRatesAreUsd = currency === "USD" || String(rates.currency || "").toUpperCase() === "USD";
  const localRates = catalogOfferLocalRates(offer, fallback);
  const resolved = (usdValue, localValue) => (
    Number.isFinite(usdValue) ? usdValue : pricingUsdFromLocal(localValue, currency)
  );
  const inputUsd = firstFinite(
    offer.inputPerMillionTokensUsd,
    rates.inputPerMillionTokensUsd,
    genericRatesAreUsd ? rates.input : null,
  );
  const cacheUsd = firstFinite(
    offer.cacheReadPerMillionTokensUsd,
    offer.cacheHitPerMillionTokensUsd,
    offer.cachedInputPerMillionTokensUsd,
    rates.cacheHitPerMillionTokensUsd,
    rates.cachedInputPerMillionTokensUsd,
    genericRatesAreUsd ? rates.cachedInput : null,
    genericRatesAreUsd ? rates.cache : null,
  );
  const outputUsd = firstFinite(
    offer.outputPerMillionTokensUsd,
    rates.outputPerMillionTokensUsd,
    genericRatesAreUsd ? rates.output : null,
  );
  return {
    input: resolved(inputUsd, localRates.input),
    cache: resolved(cacheUsd, localRates.cache),
    output: resolved(outputUsd, localRates.output),
  };
}

function pricingScenarioWeights() {
  const scenario = providerPricingCatalog().workloadScenario || {};
  const weights = scenario.weights || scenario.tokenWeights || {};
  const input = firstFinite(weights.input, weights.newInput, scenario.inputWeight, 0.2);
  const cache = firstFinite(weights.cache, weights.cacheRead, weights.cachedInput, scenario.cacheWeight, 0.7);
  const output = firstFinite(weights.output, scenario.outputWeight, 0.1);
  const total = Math.max((input || 0) + (cache || 0) + (output || 0), 1e-9);
  return { input: input / total, cache: cache / total, output: output / total };
}

function pricingBlendFromRates(rates) {
  if (!Number.isFinite(rates.input) || !Number.isFinite(rates.output)) return null;
  const weights = pricingScenarioWeights();
  const cache = Number.isFinite(rates.cache) ? rates.cache : rates.input;
  return rates.input * weights.input + cache * weights.cache + rates.output * weights.output;
}

function catalogPlanType(provider, plan, offer) {
  const raw = plan.type || plan.displayType || plan.billingType || offer.planType || offer.pricingKind || "token";
  const providerType = String(provider.category || provider.type || "").toLowerCase();
  if (String(raw).toLowerCase() === "subscription" && providerType.includes("coding")) return "coding";
  return raw;
}

function humanizePricingMetadataKey(key) {
  return String(key || "")
    .replace(/([a-z0-9])([A-Z])/g, "$1 $2")
    .replace(/[_-]+/g, " ")
    .trim()
    .replace(/^./, (character) => character.toUpperCase());
}

function pricingMetadataLines(value, prefix = "") {
  if (value === null || value === undefined || value === "") return [];
  if (Array.isArray(value)) {
    return value.flatMap((item) => pricingMetadataLines(item, prefix));
  }
  if (typeof value === "object") {
    return Object.entries(value).flatMap(([key, item]) => {
      const label = prefix
        ? `${prefix} · ${humanizePricingMetadataKey(key)}`
        : humanizePricingMetadataKey(key);
      return pricingMetadataLines(item, label);
    });
  }
  const text = typeof value === "boolean" ? (value ? "true" : "false") : String(value);
  return [prefix ? `${prefix}: ${text}` : text];
}

function pricingQuotaLabel(subject = {}, fallback = {}) {
  const subjectExplicit = subject.quotaLabel
    || subject.quota?.label
    || subject.billing?.quotaLabel;
  if (subjectExplicit) return subjectExplicit;

  const coverageMode = String(subject.coverageMode || fallback.coverageMode || "").toLowerCase();
  if (coverageMode.includes("usage-credits")) return tr("pricingUsageCreditsOnly");
  const weeklyShare = firstFinite(
    subject.includedWeeklyLimitPercent,
    fallback.includedWeeklyLimitPercent,
    Number.isFinite(firstFinite(subject.includedWeeklyLimitShare))
      ? firstFinite(subject.includedWeeklyLimitShare) * 100
      : null,
    Number.isFinite(firstFinite(fallback.includedWeeklyLimitShare))
      ? firstFinite(fallback.includedWeeklyLimitShare) * 100
      : null,
  );
  if (Number.isFinite(weeklyShare) && weeklyShare > 0) {
    return tr("pricingWeeklyLimitShare", { percent: compactNumber(weeklyShare) });
  }

  const fallbackExplicit = fallback.quotaLabel
    || fallback.quota?.label
    || fallback.billing?.quotaLabel;
  if (fallbackExplicit) return fallbackExplicit;

  const parts = [];
  const weeklyCredits = firstFinite(subject.weeklyCredits, fallback.weeklyCredits);
  if (Number.isFinite(weeklyCredits)) {
    parts.push(tr("pricingWeeklyCredits", { credits: compactNumber(weeklyCredits) }));
  }
  const creditCurrency = pricingCurrencyFor(subject, fallback);
  const localCreditCost = firstFinite(
    subject.costPerIncludedCreditLocal,
    fallback.costPerIncludedCreditLocal,
  );
  const usdCreditCost = firstFinite(
    subject.costPerIncludedCreditUsd,
    fallback.costPerIncludedCreditUsd,
  );
  const creditCost = Number.isFinite(localCreditCost) && creditCurrency !== "USD"
    ? formatLocalPrice(localCreditCost, creditCurrency)
    : (Number.isFinite(usdCreditCost) ? formatUnitPrice(usdCreditCost) : "");
  if (creditCost) parts.push(tr("pricingPerIncludedCredit", { price: creditCost }));

  const callsPerFiveHours = firstFinite(
    subject.callsPerFiveHours,
    fallback.callsPerFiveHours,
  );
  const callsPerWeek = firstFinite(subject.callsPerWeek, fallback.callsPerWeek);
  const callsPerMonth = firstFinite(subject.callsPerMonth, fallback.callsPerMonth);
  if (Number.isFinite(callsPerFiveHours)) {
    parts.push(tr("pricingCallsPerFiveHours", { calls: compactNumber(callsPerFiveHours) }));
  }
  if (Number.isFinite(callsPerWeek)) {
    parts.push(tr("pricingCallsPerWeek", { calls: compactNumber(callsPerWeek) }));
  }
  if (Number.isFinite(callsPerMonth)) {
    parts.push(tr("pricingCallsPerMonth", { calls: compactNumber(callsPerMonth) }));
  }

  const offPeakCreditMultiplier = firstFinite(
    subject.offPeakCreditMultiplier,
    fallback.offPeakCreditMultiplier,
  );
  const offPeakLocalTime = subject.offPeakLocalTime || fallback.offPeakLocalTime || "";
  if (Number.isFinite(offPeakCreditMultiplier) && offPeakLocalTime) {
    parts.push(tr("pricingOffPeakCredits", {
      time: offPeakLocalTime,
      multiplier: compactNumber(offPeakCreditMultiplier),
    }));
  }

  return parts.join(" · ")
    || pricingIncludedTokenLabel(
      subject.includedTokensPerMonth || fallback.includedTokensPerMonth,
    );
}

function catalogOfferPricingOverrideRows(offer) {
  const overrides = offer.pricingOverrides ?? offer.endpoint?.pricingOverrides;
  const rows = Array.isArray(overrides)
    ? overrides
    : (Array.isArray(overrides?.rows) ? overrides.rows : []);
  return rows.flatMap((row) => {
    if (!row || typeof row !== "object") return [];
    const minPromptTokens = firstFinite(
      row.minPromptTokens,
      row.thresholdTokens,
      row.minInputTokens,
      row.condition?.minPromptTokens,
    );
    const fallback = { planId: offer.planId, currency: pricingCurrencyFor(offer) };
    const rates = catalogOfferRates(row, fallback);
    const localRates = catalogOfferLocalRates(row, fallback);
    if (!Number.isFinite(minPromptTokens) || !Number.isFinite(rates.input) || !Number.isFinite(rates.output)) return [];
    return [{
      minPromptTokens,
      rates,
      localRates,
      currency: fallback.currency,
      effectivePrice: pricingBlendFromRates(rates),
      localEffectivePrice: pricingBlendFromRates(localRates),
      note: row.note || row.notes || row.thresholdNote || "",
    }];
  });
}

function catalogOfferOverrideNotes(offer) {
  const explicitNotes = [
    ...pricingMetadataLines(offer.thresholdNotes || offer.endpoint?.thresholdNotes),
    ...pricingMetadataLines(offer.pricingOverrideNotes || offer.endpoint?.pricingOverrideNotes),
  ];
  const overrides = catalogOfferPricingOverrideRows(offer).length
    ? []
    : pricingMetadataLines(offer.pricingOverrides ?? offer.endpoint?.pricingOverrides);
  return [...new Set([...explicitNotes, ...overrides])];
}

function normalizedCatalogOffer(offer) {
  const provider = pricingProviderById(offer.providerId) || {};
  const plan = pricingPlanById(offer.planId) || {};
  const rates = catalogOfferRates(offer);
  const currency = pricingCurrencyFor(offer);
  const localRates = catalogOfferLocalRates(offer);
  const sourceIds = [
    ...(Array.isArray(offer.sourceIds) ? offer.sourceIds : []),
    ...(Array.isArray(plan.sourceIds) ? plan.sourceIds : []),
  ];
  const source = pricingSourceById(sourceIds[0]) || {};
  const basePlanName = offer.planName || plan.name || tr("pricingObserved");
  const planName = offer.routeLabel ? `${basePlanName} · ${offer.routeLabel}` : basePlanName;
  const endpointSourceUrl = provider.id === "openrouter" && offer.providerModelId
    ? `https://openrouter.ai/api/v1/models/${offer.providerModelId}/endpoints`
    : "";
  const explicitEffectiveUsd = firstFinite(
    offer.effectiveUsdPerMillionTokens,
    offer.effectiveUsdPerMillionIncludedTokens,
    offer.normalizedUsdPerMillionTokens,
    offer.effectivePriceUsdPerMillionTokens,
    offer.effectivePrice?.usdPerMillionTokens,
    (offer.effectivePrices || []).find((row) => row.scenarioId === providerPricingCatalog().displayScenarioId)?.usdPerMillionTokens,
  );
  const explicitEffectiveLocal = firstFinite(
    offer.effectiveLocalPerMillionTokens,
    offer.effectiveLocalPerMillionIncludedTokens,
  );
  const explicitEffective = Number.isFinite(explicitEffectiveUsd)
    ? explicitEffectiveUsd
    : pricingUsdFromLocal(explicitEffectiveLocal, currency);
  const monthlyLocal = currency === "USD" ? null : firstFinite(
    offer.monthlyPriceLocal,
    plan.monthlyPriceLocal,
    plan.billing?.monthlyLocal,
  );
  const annualLocal = currency === "USD" ? null : firstFinite(
    offer.annualPriceLocal,
    offer.annualTotalLocal,
    plan.annualPriceLocal,
    plan.annualTotalLocal,
    plan.billing?.annualLocal,
  );
  const monthlyEquivalentLocal = currency === "USD" ? null : firstFinite(
    offer.annualEquivalentMonthlyLocal,
    offer.quarterlyEquivalentMonthlyLocal,
    plan.annualEquivalentMonthlyLocal,
    plan.quarterlyEquivalentMonthlyLocal,
  );
  const monthlyUsdPublished = firstFinite(
    offer.monthlyUsd,
    plan.monthlyUsd,
    plan.monthlyPriceUsd,
    plan.billing?.monthlyUsd,
    plan.billing?.amount,
  );
  const annualUsdPublished = firstFinite(
    offer.annualUsd,
    offer.annualPriceUsd,
    plan.annualUsd,
    plan.annualPriceUsd,
    plan.billing?.annualUsd,
  );
  const monthlyEquivalentUsdPublished = firstFinite(
    offer.annualEquivalentMonthlyUsd,
    plan.annualEquivalentMonthlyUsd,
  );
  const calculatedEffective = Number.isFinite(explicitEffective)
    ? explicitEffective
    : pricingBlendFromRates(rates);
  const hasCalculatedPrice = Number.isFinite(calculatedEffective);
  const note = [...new Set([
    ...pricingMetadataLines(offer.note || offer.notes),
    ...pricingMetadataLines(offer.calculation),
    ...pricingMetadataLines(plan.note || plan.notes),
  ])].join(" · ");
  const comparable = offer.comparable !== false
    && offer.availability?.status !== "expired"
    && hasCalculatedPrice;
  return {
    id: offer.id,
    providerId: offer.providerId || provider.id || "unknown",
    providerName: provider.name || offer.providerName || tr("unknownCreator"),
    providerType: provider.type || provider.category || "aggregator",
    planId: offer.planId || plan.id || "unknown-plan",
    planName,
    planType: catalogPlanType(provider, plan, offer),
    currency,
    rates,
    localRates,
    effectivePrice: hasCalculatedPrice ? calculatedEffective : null,
    localEffectivePrice: Number.isFinite(explicitEffectiveLocal)
      ? explicitEffectiveLocal
      : pricingBlendFromRates(localRates),
    effectiveUnit: Number.isFinite(firstFinite(
      offer.effectiveUsdPerMillionIncludedTokens,
      offer.effectiveLocalPerMillionIncludedTokens,
    )) ? "included" : "mix",
    comparable,
    estimated: Boolean(
      offer.estimated
      || offer.confidence === "estimated"
      || offer.pricingKind === "estimated"
      || source.kind === "third-party-analysis"
      || offer.evidenceKind === "community-catalog"
      || String(source.kind || "").startsWith("community-catalog")
    ),
    monthlyLocal,
    annualLocal,
    monthlyEquivalentLocal,
    monthlyUsd: Number.isFinite(monthlyUsdPublished)
      ? monthlyUsdPublished
      : pricingUsdFromLocal(monthlyLocal, currency),
    annualUsd: Number.isFinite(annualUsdPublished)
      ? annualUsdPublished
      : pricingUsdFromLocal(annualLocal, currency),
    monthlyEquivalentUsd: Number.isFinite(monthlyEquivalentUsdPublished)
      ? monthlyEquivalentUsdPublished
      : pricingUsdFromLocal(monthlyEquivalentLocal, currency),
    quotaLabel: pricingQuotaLabel(offer, plan),
    status: offer.status ?? offer.endpoint?.status ?? offer.availability?.status ?? null,
    quantization: offer.quantization || offer.endpoint?.quantization || "",
    contextLength: firstFinite(
      offer.contextLength,
      offer.contextWindow,
      offer.endpoint?.contextLength,
      offer.endpoint?.contextWindow,
    ),
    observedAt: offer.observedAt || offer.endpoint?.observedAt || "",
    dynamic: offer.dynamic ?? offer.endpoint?.dynamic ?? false,
    pricingOverrides: offer.pricingOverrides ?? offer.endpoint?.pricingOverrides ?? null,
    thresholdNotes: offer.thresholdNotes ?? offer.endpoint?.thresholdNotes ?? null,
    pricingOverrideNotes: offer.pricingOverrideNotes ?? offer.endpoint?.pricingOverrideNotes ?? null,
    pricingOverrideRows: catalogOfferPricingOverrideRows(offer),
    overrideNotes: catalogOfferOverrideNotes(offer),
    note,
    sourceUrl: offer.sourceUrl || endpointSourceUrl || source.url || plan.sourceUrl || provider.pricingUrl || provider.url || "",
    sourceLabel: source.label || source.title || source.name || offer.sourceLabel || provider.name || tr("pricingSource"),
    modelSlugs: catalogOfferModelSlugs(offer),
  };
}

function pricingOffersForModel(model) {
  return verifiedPricingOffersForModel(model).filter((offer) => (
    Number.isFinite(offer.effectivePrice)
  ));
}

function normalizedPricingCatalogOffers() {
  const cache = pricingCatalogIndexes();
  if (cache.normalizedOffers && cache.normalizedLanguage === state.language) {
    return cache.normalizedOffers;
  }
  const normalizedOffers = expandedPricingCatalogOffers().map(normalizedCatalogOffer);
  const offersByModelSlug = new Map();
  normalizedOffers.forEach((offer) => {
    offer.modelSlugs.forEach((modelSlug) => {
      if (!offersByModelSlug.has(modelSlug)) offersByModelSlug.set(modelSlug, []);
      offersByModelSlug.get(modelSlug).push(offer);
    });
  });
  offersByModelSlug.forEach((offers) => offers.sort((a, b) => (
    (Number.isFinite(a.effectivePrice) ? a.effectivePrice : Infinity)
      - (Number.isFinite(b.effectivePrice) ? b.effectivePrice : Infinity)
    || a.providerName.localeCompare(b.providerName)
    || a.planName.localeCompare(b.planName)
  )));
  cache.normalizedLanguage = state.language;
  cache.normalizedOffers = normalizedOffers;
  cache.offersByModelSlug = offersByModelSlug;
  return normalizedOffers;
}

function verifiedPricingOffersForModel(model) {
  normalizedPricingCatalogOffers();
  if (!model?.slug) return [];
  return pricingCatalogIndexes().offersByModelSlug.get(model.slug) || [];
}

function catalogOfferSupportsModel(offer, model) {
  if (!model?.slug) return false;
  return catalogOfferModelSlugs(offer).includes(model.slug);
}

function cheapestPricingOffer(model) {
  return verifiedPricingOffersForModel(model).find((offer) => (
    offer.comparable && Number.isFinite(offer.effectivePrice)
  )) || null;
}

function pricingOfferUnitLabel(offer) {
  return tr(offer?.effectiveUnit === "included" ? "priceIncludedShort" : "priceMixShort");
}

function priceLeaderboardRows(models, cohortSize) {
  return models.slice(0, cohortSize)
    .map((model) => ({ model, offer: cheapestPricingOffer(model) }))
    .filter((row) => row.offer)
    .sort((a, b) => a.offer.effectivePrice - b.offer.effectivePrice
      || (a.model.rank || Infinity) - (b.model.rank || Infinity)
      || a.model.slug.localeCompare(b.model.slug))
    .slice(0, HOME_PRICE_LIST_LIMIT);
}

function renderPriceLeaderboards(models) {
  if (!els.costScatter) return;
  const top10 = priceLeaderboardRows(models, 10);
  const top50 = priceLeaderboardRows(models, 50);
  const asOf = providerPricingCatalog().asOf || providerPricingCatalog().updatedAt || state.data.generatedAt;
  els.costScatter.innerHTML = `
    <div class="price-board-grid">
      ${renderPriceLeaderboardColumn("priceTop10Title", "priceTop10Subtitle", top10)}
      ${renderPriceLeaderboardColumn("priceTop50Title", "priceTop50Subtitle", top50)}
    </div>
    <div class="price-board-foot">
      <span>${renderIcon("sliders")}${escapeHtml(tr("pricingMethodNote"))}</span>
      <span>${escapeHtml(tr("pricingAsOf", { date: formatDate(asOf) }))}</span>
      <a href="${escapeHtml(pageHref("providers"))}">${escapeHtml(tr("pricingViewProviders"))}${renderIcon("arrowRight")}</a>
    </div>
  `;
}

function renderPriceLeaderboardColumn(titleKey, subtitleKey, rows) {
  return `
    <section class="price-board-column">
      <div class="price-board-heading">
        <div>
          <h3>${escapeHtml(tr(titleKey))}</h3>
          <p>${escapeHtml(tr(subtitleKey, { count: HOME_PRICE_LIST_LIMIT }))}</p>
        </div>
        <span>${escapeHtml(tr("priceComparableShort"))}</span>
      </div>
      <div class="price-board-list">
        ${rows.length ? rows.map(renderPriceLeaderboardRow).join("") : `<div class="empty">${escapeHtml(tr("priceListEmpty"))}</div>`}
      </div>
    </section>
  `;
}

function renderPriceLeaderboardRow({ model, offer }) {
  const estimateLabel = offer.estimated ? ` · ${tr("pricingLabels.estimate")}` : "";
  return `
    <article class="price-board-row">
      <span class="price-board-rank">#${escapeHtml(model.rank)}</span>
      ${renderModelIcon(model)}
      <span class="price-board-model">
        <a href="${escapeHtml(modelHref(model, "home"))}">${escapeHtml(model.model)}</a>
        <em>${escapeHtml(offer.providerName)} · ${escapeHtml(offer.planName)}${escapeHtml(estimateLabel)}</em>
      </span>
      <strong>${escapeHtml(formatUnitPrice(offer.effectivePrice))}<small>${escapeHtml(pricingOfferUnitLabel(offer))}</small></strong>
    </article>
  `;
}

function formatUnitPrice(value) {
  if (!Number.isFinite(value)) return tr("notAvailable");
  const absolute = Math.abs(value);
  const digits = absolute < 0.01 ? 6 : absolute < 1 ? 4 : 2;
  return `$${value.toLocaleString("en-US", { maximumFractionDigits: digits, minimumFractionDigits: 0 })}`;
}

function formatLocalPrice(value, currency) {
  if (!Number.isFinite(value)) return tr("notAvailable");
  const normalized = String(currency || "").toUpperCase();
  const symbol = { CNY: "¥", EUR: "€", GBP: "£", INR: "₹", JPY: "¥", KRW: "₩" }[normalized]
    || `${normalized} `;
  const absolute = Math.abs(value);
  const digits = absolute < 0.01 ? 6 : absolute < 1 ? 4 : absolute < 100 ? 2 : 0;
  return `${symbol}${value.toLocaleString("en-US", {
    maximumFractionDigits: digits,
    minimumFractionDigits: 0,
  })}`;
}

function formatBillingPrice(usdValue, localValue, currency) {
  const normalized = String(currency || "USD").toUpperCase();
  if (normalized !== "USD" && Number.isFinite(localValue)) {
    const local = formatLocalPrice(localValue, normalized);
    return Number.isFinite(usdValue) ? `${local} (~${formatUnitPrice(usdValue)})` : local;
  }
  return formatUnitPrice(usdValue);
}

function pricingLocalUnitLabel(value, currency) {
  const normalized = String(currency || "USD").toUpperCase();
  return normalized !== "USD" && Number.isFinite(value)
    ? `${formatLocalPrice(value, normalized)} / 1M`
    : "";
}

function formatRateWithLocal(usdValue, localValue, currency) {
  const local = pricingLocalUnitLabel(localValue, currency);
  return `${formatUnitPrice(usdValue)}${local ? ` (${local})` : ""}`;
}

function pricingIncludedTokenLabel(value) {
  const tokens = Number(value);
  return Number.isFinite(tokens) && tokens > 0
    ? `${compactNumber(tokens)} ${tr("table.tokens")} · ${tr("pricingPerMonth")}`
    : "";
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
              <title>${escapeHtml(`${model.model} · ${formatModelDisplayScore(model)} · ${formatMoney(modelCost(model))}`)}</title>
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
        <em>${escapeHtml(formatModelDisplayScore(row.bestModel))}</em>
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
  const cap = Number(state.data?.leaderboard?.bonusCap);
  const capText = Number.isFinite(cap) ? formatNumber(cap) : tr("notAvailable");
  document.title = `${zh ? "AInsights Index 计算方式" : "AInsights Index Methodology"} · ${tr("pageTitle")}`;
  els.methodologyDetail.innerHTML = `
    <section class="methodology-hero">
      <p class="eyebrow">Methodology</p>
      <h2>${escapeHtml(zh ? "AInsights Index 计算方式" : "AInsights Index Methodology")}</h2>
      <p>${escapeHtml(zh
        ? "AIndex 采用方案 18：每板由完整 Core 真实成绩给出基础分，列明的独立控制扩展测试只提供非负前沿加分；五板等权，最终只按未经舍入的 final_score 排序。"
        : "AIndex uses Scheme 18: complete real Core results establish each board's base, listed independent-controller extensions provide non-negative frontier bonuses, five boards are equal, and only the unrounded final_score determines order.")}</p>
    </section>
    <section class="methodology-grid">
      <article class="methodology-card methodology-card-wide">
        <h3>${escapeHtml(zh ? "Core 基础分" : "Core base score")}</h3>
        <p><code>core = 100 × exp(mean(log(score / 100)))</code></p>
        <p>${escapeHtml(zh
          ? "每板 Core 项必须全部完成，并在真实百分尺度上取不加权几何均值；不填 0、不填 50，也没有测试项特定权重。"
          : "Every Core item on a board must be complete and enters an unweighted geometric mean on the real percentage scale; there is no 0/50 fill and no item-specific weight.")}</p>
      </article>
      <article class="methodology-card">
        <h3>${escapeHtml(zh ? "匿名趋势" : "Anonymous trend")}</h3>
        <p>${escapeHtml(zh
          ? "每个扩展测试对同板 Core 分拟合 cohort-wide OLS，斜率限制为非负；只保留真实观测高于预测趋势的 r=max(y−ŷ,0)。"
          : "Each extension fits a cohort-wide OLS trend against the same board's Core score with a non-negative slope; only r=max(y−ŷ,0) above the predicted trend is retained.")}</p>
      </article>
      <article class="methodology-card">
        <h3>${escapeHtml(zh ? "动态统一 cap" : "One dynamic cap")}</h3>
        <p>${escapeHtml(zh
          ? `五板全部正残差共同计算 mean + √2 × population SD，Action 每次随数据重算；当前 cap 为 ${capText}。`
          : `All positive residuals across five boards determine mean + √2 × population SD and are recomputed on every data refresh; the current cap is ${capText}.`)}</p>
      </article>
      <article class="methodology-card methodology-card-wide">
        <h3>${escapeHtml(zh ? "扩展聚合与总分" : "Extension aggregation and total")}</h3>
        <p><code>bonus = min(cap, log(1 + Σ expm1(r)))</code></p>
        <p><code>board_score = min(100, core + bonus)</code></p>
        <p><code>final_score = Σ(board_score / 5) = mean(five board_scores)</code></p>
        <p>${escapeHtml(zh
          ? "log-sum-exp 对零残差中性，新增任意正证据都不会降分。五板完全等权；榜面 0–100 points 是直接计算分，不是 percentile、mean rank 或 T 分。"
          : "The log-sum-exp is neutral to zero residuals and any new positive evidence cannot lower a score. Five boards are exactly equal; displayed 0–100 points are direct calculated scores, not a percentile, mean rank, or T score.")}</p>
      </article>
      <article class="methodology-card methodology-card-wide">
        <h3>${escapeHtml(zh ? "缺失、去重与协议" : "Missingness, dedupe, and protocols")}</h3>
        <p>${escapeHtml(zh
          ? "扩展缺失保持 absent，bonus 为 0，绝不扣 Core。去重榜可使用系列级外部证据；关闭去重只使用 AA 精确行和 variantScoped 外部结果，并复用去重 cohort 的同一 OLS 参数与 cap。"
          : "Missing extensions remain absent with zero bonus and never reduce Core. The deduplicated view may use family-level evidence; dedupe-off accepts only AA exact rows and variantScoped external results while reusing the identical OLS parameters and cap from the deduplicated cohort.")}</p>
        <p>${escapeHtml(zh
          ? "扩展 benchmark 的 controller 均不属于被排名模型厂商，但部分 result operator、agent scaffold、prompt 或版本仍是混合/敏感协议；这些限制在 Benchmark 页面逐项披露。"
          : "Extension benchmark controllers are independent of ranked model vendors, but some result operators, agent scaffolds, prompts, or versions remain mixed or sensitive; the Benchmark page discloses these limits item by item.")}</p>
      </article>
      <article class="methodology-card">
        <h3>${escapeHtml(zh ? "六轴雷达" : "Radar Profile")}</h3>
        <p>${escapeHtml(zh
          ? "前五轴直接读取方案 18 的五个板块分；第六轴是扩展覆盖度，只反映证据广度，永不参与计分。"
          : "The first five axes directly read Scheme 18 board scores; the sixth is extension coverage, reflecting evidence breadth only and never entering the score.")}</p>
      </article>
      <article class="methodology-card">
        <h3>${escapeHtml(zh ? "敏感性与 Custom 工具" : "Sensitivity and Custom Tools")}</h3>
        <p>${escapeHtml(zh
          ? "等板块 2PL、Sparse Rasch、Core Rasch 与 Dense Rasch 只作审计/敏感性。Custom 可独立组合这些方法名次、方案 18 五板分或逐项 benchmark，不会改写主榜。"
          : "Equal-board 2PL, Sparse Rasch, Core Rasch, and Dense Rasch are audit/sensitivity only. Custom tools can independently combine those ranks, Scheme 18 board scores, or individual benchmarks without rewriting the primary ranking.")}</p>
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
  return `
    <div class="histogram-row" data-card-href="${escapeHtml(modelHref(model, "ranking"))}" role="link" tabindex="0" aria-label="${escapeHtml(`${tr("modelDetails")} ${model.model}`)}">
      <div class="histogram-rank">${escapeHtml(rankLabel(model))}</div>
      <div class="histogram-model">
        ${renderModelIcon(model)}
        <div class="histogram-label">
          <a href="${escapeHtml(modelHref(model))}">${escapeHtml(model.model)}</a>
          <span>${renderProviderTextLink(model.creator, "ranking")} · ${escapeHtml(sourceTypeLabel(sourceType(model)))}</span>
        </div>
      </div>
      <div class="histogram-track" aria-label="${escapeHtml(tr(scoreHeaderKeyForPreset(state.data.presets[state.presetId])))} ${escapeHtml(formatModelDisplayScore(model))}">
        <span class="histogram-fill" style="--value: ${scoreWidth}%"></span>
      </div>
      <div class="histogram-score">${escapeHtml(formatModelDisplayScore(model))}</div>
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
  const reason = model.isReasoning ? `<span class="pill">${escapeHtml(tr("reasoning"))}</span>` : "";
  return `
    <tr data-card-href="${escapeHtml(modelHref(model, "ranking"))}" tabindex="0" aria-label="${escapeHtml(`${tr("modelDetails")} ${model.model}`)}">
      <td class="rank-col">${escapeHtml(rankLabel(model))}</td>
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
        <div class="score-value"><span>${escapeHtml(formatModelDisplayScore(model))}</span><span class="muted">${escapeHtml(model.scoreMeta || "")}</span></div>
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
  const evidenceRank = rankingMethodEvidenceRank(model, methodId);
  if (!Number.isFinite(evidenceRank)) return `<td class="method-rank-col">—</td>`;
  return `
    <td class="method-rank-col" title="${escapeHtml(methodRankTitle(evidenceRank))}">
      #${evidenceRank}
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
        <span>${escapeHtml(rankLabel(model))}</span>
        <a class="text-model" href="${escapeHtml(modelHref(model))}">${escapeHtml(model.model)}</a>
        ${renderProviderTextLink(creator, "ranking")}
        <strong>${escapeHtml(formatModelDisplayScore(model))}</strong>
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

    ${renderModelPricingSection(model)}

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

function renderModelPricingSection(model) {
  const offers = pricingOffersForModel(model);
  const asOf = providerPricingCatalog().asOf || providerPricingCatalog().updatedAt || state.data.generatedAt;
  return `
    <section class="detail-section model-pricing-section">
      <div class="detail-section-head pricing-section-head">
        <div>
          <h2>${escapeHtml(tr("pricingSectionTitle"))}</h2>
          <p>${escapeHtml(tr("pricingSectionSubtitle"))}</p>
        </div>
        <span class="pricing-as-of">${escapeHtml(tr("pricingAsOf", { date: formatDate(asOf) }))}</span>
      </div>
      <div class="pricing-offer-scroll" tabindex="0" aria-label="${escapeHtml(tr("pricingSectionTitle"))}">
        ${offers.length ? offers.map(renderModelPricingOffer).join("") : `<div class="empty">${escapeHtml(tr("pricingNoOffers"))}</div>`}
      </div>
      <div class="pricing-method-strip">
        ${renderIcon("sliders")}
        <span>${escapeHtml(tr("pricingMethodNote"))}</span>
        <a href="${escapeHtml(pageHref("providers"))}">${escapeHtml(tr("pricingViewProviders"))}${renderIcon("arrowRight")}</a>
      </div>
    </section>
  `;
}

function renderModelPricingOffer(offer) {
  const type = pricingPlanTypeGroup(offer.planType);
  const planLabel = tr(`pricingPlanTypes.${type}`);
  const meta = [];
  if (Number.isFinite(offer.monthlyUsd) || Number.isFinite(offer.monthlyLocal)) {
    meta.push(`${tr("pricingLabels.monthly")} ${formatBillingPrice(offer.monthlyUsd, offer.monthlyLocal, offer.currency)}`);
  }
  if (Number.isFinite(offer.annualUsd) || Number.isFinite(offer.annualLocal)) {
    meta.push(`${formatBillingPrice(offer.annualUsd, offer.annualLocal, offer.currency)} ${tr("pricingPerYear")}`);
  }
  if (Number.isFinite(offer.monthlyEquivalentUsd) || Number.isFinite(offer.monthlyEquivalentLocal)) {
    meta.push(`${tr("pricingMonthlyEquivalent")} ${formatBillingPrice(offer.monthlyEquivalentUsd, offer.monthlyEquivalentLocal, offer.currency)}`);
  }
  if (offer.quotaLabel) meta.push(offer.quotaLabel);
  if (offer.estimated) meta.push(tr("pricingLabels.estimate"));
  if (!offer.comparable && Number.isFinite(offer.effectivePrice)) {
    meta.push(tr("pricingLabels.displayOnly"));
  }
  if (Number.isFinite(offer.contextLength)) {
    meta.push(`${tr("pricingLabels.context")} ${compactNumber(offer.contextLength)} ${tr("table.tokens")}`);
  }
  if (offer.status === 0 || String(offer.status).toLowerCase() === "active") {
    meta.push(tr("pricingLabels.activeEndpoint"));
  } else if (offer.status !== null && offer.status !== undefined && offer.status !== "") {
    meta.push(`${tr("pricingLabels.endpointStatus")} ${offer.status}`);
  }
  if (offer.dynamic) meta.push(tr("pricingLabels.dynamicEndpoint"));
  if (offer.quantization) meta.push(`${tr("pricingLabels.quantization")} ${String(offer.quantization).toUpperCase()}`);
  if (offer.observedAt) meta.push(`${tr("pricingLabels.observed")} ${formatDate(offer.observedAt)}`);
  const source = offer.sourceUrl
    ? `<a href="${escapeHtml(offer.sourceUrl)}" target="_blank" rel="noreferrer">${escapeHtml(offer.sourceLabel)}${renderIcon("arrowUpRight")}</a>`
    : `<span>${escapeHtml(offer.sourceLabel || tr("pricingSource"))}</span>`;
  return `
    <article class="pricing-offer-card${offer.comparable ? "" : " is-unpriced"}">
      <div class="pricing-offer-main">
        <span class="pricing-provider-mark">${escapeHtml(initials(offer.providerName))}</span>
        <span>
          <strong>${escapeHtml(offer.providerName)}</strong>
          <em>${escapeHtml(offer.planName)}</em>
        </span>
        <span class="pricing-plan-pill is-${escapeHtml(type)}">${escapeHtml(planLabel)}</span>
      </div>
      <div class="pricing-rate-grid">
        ${renderAvailablePricingRate(tr("pricingLabels.input"), offer.rates.input, false, offer.localRates.input, offer.currency)}
        ${renderAvailablePricingRate(tr("pricingLabels.cache"), offer.rates.cache, false, offer.localRates.cache, offer.currency)}
        ${renderAvailablePricingRate(tr("pricingLabels.output"), offer.rates.output, false, offer.localRates.output, offer.currency)}
        ${renderAvailablePricingRate(pricingOfferUnitLabel(offer), offer.effectivePrice, true, offer.localEffectivePrice, offer.currency)}
      </div>
      <div class="pricing-offer-meta">
        <span>${escapeHtml(meta.join(" · ") || pricingOfferUnitLabel(offer))}</span>
        ${source}
      </div>
      ${offer.note ? `<p class="pricing-offer-note">${escapeHtml(offer.note)}</p>` : ""}
      ${(offer.pricingOverrideRows || []).map(renderPricingOverrideRow).join("")}
      ${offer.overrideNotes?.length ? `<p class="pricing-offer-note is-override"><strong>${escapeHtml(tr("pricingLabels.pricingOverride"))}:</strong> ${escapeHtml(offer.overrideNotes.join(" · "))}</p>` : ""}
    </article>
  `;
}

function renderPricingOverrideRow(override) {
  const threshold = tr("pricingLabels.promptThreshold", {
    tokens: `${compactNumber(override.minPromptTokens)} ${tr("table.tokens")}`,
  });
  const rates = [
    [tr("pricingLabels.input"), override.rates.input, override.localRates?.input],
    [tr("pricingLabels.cache"), override.rates.cache, override.localRates?.cache],
    [tr("pricingLabels.output"), override.rates.output, override.localRates?.output],
    [tr("pricingLabels.effective"), override.effectivePrice, override.localEffectivePrice],
  ].filter(([, value, localValue]) => Number.isFinite(value) || Number.isFinite(localValue))
    .map(([label, value, localValue]) => `${label} ${formatRateWithLocal(value, localValue, override.currency)}`);
  return `<p class="pricing-offer-note is-override"><strong>${escapeHtml(threshold)}:</strong> ${escapeHtml(rates.join(" · "))}${override.note ? ` · ${escapeHtml(override.note)}` : ""}</p>`;
}

function renderAvailablePricingRate(label, value, effective = false, localValue = null, currency = "USD") {
  if (!Number.isFinite(value) && !Number.isFinite(localValue)) return "";
  return renderPricingRate(label, value, effective, localValue, currency);
}

function renderPricingRate(label, value, effective = false, localValue = null, currency = "USD") {
  const local = pricingLocalUnitLabel(localValue, currency);
  return `
    <span class="pricing-rate${effective ? " is-effective" : ""}">
      <em>${escapeHtml(label)}</em>
      <strong>${escapeHtml(formatUnitPrice(value))}</strong>
      <small>${escapeHtml(`${tr("table.perMillion")}${local ? ` · ${local}` : ""}`)}</small>
    </span>
  `;
}

function pricingPlanTypeGroup(value) {
  const type = String(value || "").toLowerCase();
  if (type.includes("coding")) return "coding";
  if (type.includes("subscription") || type.includes("plan") || type.includes("quota")) return "subscription";
  return "token";
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
    const score = ranked ? formatModelDisplayScore(ranked) : tr("notAvailable");
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
      profileKey: "extensionCoverageScore",
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
  const board = radarBoardProfile(model, axis.boardId);
  const coreAvailable = Number(board?.coreTests);
  const coreTotal = Number(board?.coreItemPoolSize);
  const extensionAvailable = Number(board?.extensionTests);
  const extensionTotal = Number(board?.extensionItemPoolSize);
  if (!Number.isFinite(coreAvailable) || !Number.isFinite(extensionAvailable)) return null;
  const available = coreAvailable + extensionAvailable;
  const total = Number.isFinite(coreTotal) && Number.isFinite(extensionTotal)
    ? coreTotal + extensionTotal
    : null;
  return {
    available,
    total,
    coreAvailable,
    coreTotal: Number.isFinite(coreTotal) ? coreTotal : null,
    extensionAvailable,
    extensionTotal: Number.isFinite(extensionTotal) ? extensionTotal : null,
  };
}

function radarCoverageLabel(coverage) {
  if (!coverage || !Number.isFinite(coverage.available)) return "";
  if (
    Number.isFinite(coverage.coreTotal)
    && Number.isFinite(coverage.extensionAvailable)
    && Number.isFinite(coverage.extensionTotal)
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
    .map((model) => modelForRankingGrain(
      model,
      state.dedupe ? "variant-group" : "exact-config",
    ))
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
        ${renderDetailStat(tr(scoreHeaderKeyForPreset(state.data.presets[state.presetId])), formatModelDisplayScore(model), scoreRankMeta(model), "trophy")}
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
    ["gauge", `${formatModelDisplayScore(model)} ${tr(scoreHeaderKeyForPreset(state.data.presets[state.presetId]))}`],
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
      <em>${escapeHtml(formatModelDisplayScore(row))}</em>
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
            <p>${escapeHtml(tr("benchmarkRankingSubtitle", { count: rows.length, category: benchmarkRoleLabel(selected) }))}</p>
          </div>
          ${benchmarkPolicySummary(selected)}
          <div class="benchmark-ranking-list">
            ${rows.length ? rows.map((row) => renderBenchmarkRankingRow(row, selected)).join("") : `<div class="empty">${escapeHtml(tr("notAvailable"))}</div>`}
          </div>
        </section>
      </div>
    </section>
  `;
}

function benchmarkRoleLabel(metric) {
  const key = {
    core: "benchmarkCore",
    extension: "benchmarkExtension",
    excluded: "benchmarkExcluded",
    "custom-only": "benchmarkCustomOnly",
  }[metric?.aindexRole] || "benchmarkCustomOnly";
  return tr(key);
}

function benchmarkPolicySummary(metric) {
  const zh = state.language === "zh-CN";
  const boards = (metric.aindexBoards || [])
    .map((boardId) => customWeightItemLabel(boardId, "board"))
    .join(" · ");
  const controller = metric.benchmarkController || tr("notAvailable");
  const operator = metric.resultOperator || tr("notAvailable");
  const protocol = metric.resultProtocol || tr("notAvailable");
  const version = metric.versionPin || tr("notAvailable");
  const reason = metric.scoringReason || "";
  return `
    <div class="source-note benchmark-policy-note">
      <strong>${escapeHtml(benchmarkRoleLabel(metric))}</strong>
      <p>${escapeHtml(zh ? `板块：${boards || "—"}` : `Boards: ${boards || "—"}`)}</p>
      <p>${escapeHtml(zh ? `Benchmark controller：${controller}` : `Benchmark controller: ${controller}`)}</p>
      <p>${escapeHtml(zh ? `结果执行方 / 协议：${operator} / ${protocol}` : `Result operator / protocol: ${operator} / ${protocol}`)}</p>
      <p>${escapeHtml(zh ? `版本约束：${version}` : `Version pin: ${version}`)}</p>
      ${reason ? `<p>${escapeHtml(reason)}</p>` : ""}
    </div>
  `;
}

function rankedBenchmarkMetrics() {
  return (state.data.metrics || []).map((metric) => ({
    ...metric,
    coverage: metricGroupCoverageCount([metric]),
  })).filter((metric) => metric.coverage > 0)
    .sort((a, b) => (
      ({ core: 0, extension: 1, excluded: 2, "custom-only": 3 }[a.aindexRole] ?? 4)
      - ({ core: 0, extension: 1, excluded: 2, "custom-only": 3 }[b.aindexRole] ?? 4)
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
  const kind = benchmarkRoleLabel(metric);
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
        <em>${escapeHtml(model.creator || tr("unknownCreator"))} · ${escapeHtml(rankLabel(model))} · ${escapeHtml(formatModelDisplayScore(model))}</em>
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
        <span>${renderIcon("trophy")}<b>${escapeHtml(formatModelDisplayScore(model))}</b><em>${escapeHtml(rankLabel(model))}</em></span>
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
      values: models.map((model) => compareValue(formatModelDisplayScore(model), model.rank ? `#${model.rank}` : "")),
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
  return `${model.model} · ${model.creator || tr("unknownCreator")} · ${formatModelDisplayScore(model)}`;
}

function rankLabel(model) {
  return Number.isFinite(model?.rank) ? `#${model.rank}` : tr("unranked");
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

function renderPricingProvidersPage(ranked) {
  if (!els.pricingProviderDetail) return;
  document.title = `${tr("pricingProvidersTitle")} · ${tr("pageTitle")}`;
  const catalog = providerPricingCatalog();
  const offers = normalizedPricingCatalogOffers();
  const filter = state.pricingProviderFilter;
  const providerQuery = state.pricingProviderQuery || "";
  const modelQuery = state.pricingModelQuery || "";
  const visibleProviders = pricingProviderComparisonRows(offers, filter, {
    providerQuery,
    modelQuery,
  });
  const visibleModelOffers = visibleProviders.flatMap((row) => row.modelOffers);
  const mappedModels = new Set(visibleModelOffers.map((row) => row.modelSlug));
  const comparableCount = visibleModelOffers.filter(({ offer }) => (
    offer.comparable && Number.isFinite(offer.effectivePrice)
  )).length;
  const planCount = new Set(visibleProviders.flatMap((row) => [
    ...row.plans.map((plan) => plan.id),
    ...row.offers.map((offer) => offer.planId),
  ])).size;
  const asOf = catalog.asOf || catalog.updatedAt || state.data.generatedAt;

  els.pricingProviderDetail.innerHTML = `
    <section class="pricing-provider-hero">
      <div>
        <p class="eyebrow">AInsights Providers</p>
        <h2>${escapeHtml(tr("pricingProvidersTitle"))}</h2>
        <p>${escapeHtml(tr("pricingProvidersSubtitle"))}</p>
      </div>
      <span>${escapeHtml(tr("pricingAsOf", { date: formatDate(asOf) }))}</span>
    </section>

    <section class="pricing-provider-stats" aria-label="${escapeHtml(tr("pricingProvidersTitle"))}">
      ${renderPricingProviderStat("network", tr("pricingProvidersStats.providers"), visibleProviders.length)}
      ${renderPricingProviderStat("database", tr("pricingProvidersStats.plans"), planCount)}
      ${renderPricingProviderStat("dollar", tr("pricingProvidersStats.comparable"), comparableCount)}
      ${renderPricingProviderStat("code", tr("pricingProvidersStats.models"), mappedModels.size)}
    </section>

    <section class="pricing-provider-controls">
      <div class="pricing-provider-control-row">
        <div class="segmented-control" role="group" aria-label="${escapeHtml(tr("pricingProvidersTitle"))}">
          ${["all", "token", "subscription", "coding"].map((type) => `
            <button type="button" data-pricing-provider-filter="${escapeHtml(type)}" aria-pressed="${type === filter}">${escapeHtml(tr(`pricingPlanTypes.${type}`))}</button>
          `).join("")}
        </div>
        <div class="pricing-provider-searches">
          ${renderPricingProviderSearch(
            "provider",
            tr("pricingProviderSearchLabel"),
            tr("pricingProviderSearchPlaceholder"),
            providerQuery,
          )}
          ${renderPricingProviderSearch(
            "model",
            tr("pricingModelSearchLabel"),
            tr("pricingModelSearchPlaceholder"),
            modelQuery,
          )}
        </div>
      </div>
      <p>${escapeHtml(tr("pricingMethodNote"))}</p>
    </section>

    <section class="pricing-provider-grid">
      ${visibleProviders.length
        ? visibleProviders.map(renderPricingProviderCard).join("")
        : `<p class="pricing-provider-search-empty">${escapeHtml(tr("pricingProviderSearchEmpty"))}</p>`}
    </section>
  `;

  els.pricingProviderDetail.querySelectorAll("[data-pricing-provider-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      state.pricingProviderFilter = button.dataset.pricingProviderFilter || "all";
      renderPricingProvidersPage(ranked);
    });
  });
  els.pricingProviderDetail.querySelectorAll("[data-pricing-provider-search]").forEach((input) => {
    input.addEventListener("input", () => {
      const kind = input.dataset.pricingProviderSearch;
      const key = kind === "model" ? "pricingModelQuery" : "pricingProviderQuery";
      const selectionStart = input.selectionStart;
      const selectionEnd = input.selectionEnd;
      state[key] = input.value;
      renderPricingProvidersPage(ranked);
      const nextInput = els.pricingProviderDetail.querySelector(`[data-pricing-provider-search="${kind}"]`);
      nextInput?.focus({ preventScroll: true });
      if (nextInput && Number.isInteger(selectionStart) && Number.isInteger(selectionEnd)) {
        nextInput.setSelectionRange(selectionStart, selectionEnd);
      }
    });
  });
}

function renderPricingProviderSearch(kind, label, placeholder, value) {
  return `
    <label class="pricing-provider-search">
      <span>${escapeHtml(label)}</span>
      <input
        type="search"
        value="${escapeHtml(value)}"
        placeholder="${escapeHtml(placeholder)}"
        data-pricing-provider-search="${escapeHtml(kind)}"
        autocomplete="off"
      />
    </label>
  `;
}

function pricingSearchText(value) {
  return String(value || "").trim().toLocaleLowerCase();
}

function pricingProviderComparisonRows(offers, filter = "all", searches = {}) {
  const providerQuery = pricingSearchText(searches.providerQuery);
  const modelQuery = pricingSearchText(searches.modelQuery);
  const rows = new Map();
  const matchesFilter = (planType) => (
    filter === "all" || pricingPlanTypeGroup(planType) === filter
  );
  const ensure = (providerId, fallback = {}) => {
    if (!rows.has(providerId)) {
      const provider = pricingProviderById(providerId) || fallback;
      rows.set(providerId, {
        provider: {
          id: providerId,
          name: provider.name || fallback.name || tr("unknownCreator"),
          type: provider.type || provider.category || fallback.type || "aggregator",
          regions: provider.regions || [],
          pricingUrl: provider.pricingUrl || provider.url || "",
          note: provider.note || provider.notes || "",
        },
        plans: pricingPlans().filter((plan) => (
          plan.providerId === providerId
          && matchesFilter(catalogPlanType(provider, plan, {}))
        )),
        offers: [],
      });
    }
    return rows.get(providerId);
  };
  pricingProviders().forEach((provider) => ensure(provider.id, provider));
  offers
    .filter((offer) => matchesFilter(offer.planType))
    .forEach((offer) => ensure(offer.providerId, {
      name: offer.providerName,
      type: offer.providerType,
    }).offers.push(offer));

  return [...rows.values()]
    .filter((row) => row.plans.length || row.offers.length)
    .filter((row) => {
      if (!providerQuery) return true;
      return pricingSearchText([
        row.provider.name,
        row.provider.id,
        row.provider.type,
      ].join(" ")).includes(providerQuery);
    })
    .map((row) => {
      const allModelOffers = pricingProviderModelOfferRows(row.offers);
      const modelOffers = modelQuery
        ? allModelOffers.filter((modelOffer) => pricingModelOfferMatchesSearch(modelOffer, modelQuery))
        : allModelOffers;
      const visiblePlanIds = new Set(modelOffers.map(({ offer }) => offer.planId));
      const visibleOffers = modelQuery
        ? row.offers.filter((offer) => visiblePlanIds.has(offer.planId))
        : row.offers;
      const visiblePlans = modelQuery
        ? row.plans.filter((plan) => visiblePlanIds.has(plan.id))
        : row.plans;
      const cheapestModelOffer = modelOffers
        .filter(({ offer }) => (
          offer.comparable
          && Number.isFinite(offer.effectivePrice)
        ))
        .sort((a, b) => (
          a.offer.effectivePrice - b.offer.effectivePrice
          || a.offer.id.localeCompare(b.offer.id)
          || a.modelSlug.localeCompare(b.modelSlug)
        ))[0] || null;
      return {
        ...row,
        plans: visiblePlans,
        offers: visibleOffers,
        modelOffers,
        cheapest: cheapestModelOffer?.offer || null,
        mappedModels: new Set(modelOffers.map((modelOffer) => modelOffer.modelSlug)).size,
      };
    })
    .filter((row) => !modelQuery || row.modelOffers.length)
    .sort((a, b) => (
      (a.cheapest ? 0 : 1) - (b.cheapest ? 0 : 1)
      || (a.cheapest?.effectivePrice ?? Infinity) - (b.cheapest?.effectivePrice ?? Infinity)
      || a.provider.name.localeCompare(b.provider.name)
    ));
}

function pricingModelOfferMatchesSearch(modelOffer, query) {
  const { model, modelSlug } = modelOffer;
  return pricingSearchText([
    model?.model,
    model?.creator,
    model?.variantGroup,
    modelSlug,
  ].join(" ")).includes(query);
}

function renderPricingProviderStat(icon, label, value) {
  return `
    <article>
      ${renderIcon(icon)}
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(compactNumber(value))}</strong>
    </article>
  `;
}

function renderPricingProviderCard(row) {
  const { provider, plans, offers, modelOffers, cheapest, mappedModels } = row;
  const typeLabel = lookup(copy[state.language]?.pricingProviderTypes || {}, provider.type)
    || lookup(copy[DEFAULT_LANGUAGE]?.pricingProviderTypes || {}, provider.type)
    || provider.type;
  const planRows = plans.length ? plans : uniquePlansFromOffers(offers);
  const sourceUrl = provider.pricingUrl || offers.find((offer) => offer.sourceUrl)?.sourceUrl || "";
  const cheapestMeta = cheapest
    ? `${pricingOfferUnitLabel(cheapest)}${cheapest.estimated ? ` · ${tr("pricingLabels.estimate")}` : ""}`
    : "";
  return `
    <article class="pricing-provider-card">
      <header>
        <span class="pricing-provider-mark">${escapeHtml(initials(provider.name))}</span>
        <span>
          <h3>${escapeHtml(provider.name)}</h3>
          <em>${escapeHtml(typeLabel)}</em>
        </span>
        ${sourceUrl ? `<a href="${escapeHtml(sourceUrl)}" target="_blank" rel="noreferrer" aria-label="${escapeHtml(`${provider.name} ${tr("pricingSource")}`)}">${renderIcon("arrowUpRight")}</a>` : ""}
      </header>
      <div class="pricing-provider-summary">
        <span><em>${escapeHtml(tr("pricingLabels.models"))}</em><strong>${escapeHtml(compactNumber(mappedModels))}</strong></span>
        <span><em>${escapeHtml(tr("priceComparableShort"))}</em><strong>${escapeHtml(cheapest ? formatUnitPrice(cheapest.effectivePrice) : "—")}</strong>${cheapestMeta ? `<small>${escapeHtml(cheapestMeta)}</small>` : ""}</span>
        <span><em>${escapeHtml(tr("pricingLabels.offers"))}</em><strong>${escapeHtml(compactNumber(modelOffers.length))}</strong></span>
      </div>
      <div class="pricing-provider-plans">
        ${planRows.map(renderPricingPlanChip).join("")}
      </div>
      <div class="pricing-provider-offers">
        <h4>${escapeHtml(tr("pricingProviderOffers"))}</h4>
        <div class="pricing-provider-offer-list" tabindex="0" aria-label="${escapeHtml(`${provider.name} ${tr("pricingProviderOffers")}`)}">
          ${modelOffers.length ? modelOffers.map(renderPricingProviderOfferRow).join("") : `<p>${escapeHtml(tr("pricingProviderNoOffers"))}</p>`}
        </div>
      </div>
      ${provider.note ? `<p class="pricing-provider-note">${escapeHtml(provider.note)}</p>` : ""}
    </article>
  `;
}

function uniquePlansFromOffers(offers) {
  const seen = new Set();
  return offers.map((offer) => ({
    id: offer.planId,
    name: offer.planName,
    type: offer.planType,
    currency: offer.currency,
    monthlyUsd: offer.monthlyUsd,
    monthlyPriceLocal: offer.monthlyLocal,
    annualPriceUsd: offer.annualUsd,
    annualPriceLocal: offer.annualLocal,
    annualEquivalentMonthlyUsd: offer.monthlyEquivalentUsd,
    annualEquivalentMonthlyLocal: offer.monthlyEquivalentLocal,
    quotaLabel: offer.quotaLabel,
  })).filter((plan) => {
    if (seen.has(plan.id)) return false;
    seen.add(plan.id);
    return true;
  });
}

function pricingProviderModelOfferRows(offers) {
  const modelBySlug = new Map((state.data?.models || []).map((model) => [model.slug, model]));
  return offers
    .flatMap((offer) => [...new Set(offer.modelSlugs || [])].map((modelSlug) => ({
      offer,
      modelSlug,
      model: modelBySlug.get(modelSlug) || null,
    })))
    .filter(({ offer }) => Number.isFinite(offer.effectivePrice))
    .sort((a, b) => (
      (a.model?.rank ?? Infinity) - (b.model?.rank ?? Infinity)
      || (a.model?.model || a.modelSlug).localeCompare(b.model?.model || b.modelSlug)
      || (Number.isFinite(a.offer.effectivePrice) ? a.offer.effectivePrice : Infinity)
        - (Number.isFinite(b.offer.effectivePrice) ? b.offer.effectivePrice : Infinity)
      || a.offer.planName.localeCompare(b.offer.planName)
      || a.offer.id.localeCompare(b.offer.id)
    ));
}

function renderPricingPlanChip(plan) {
  const currency = pricingCurrencyFor({}, { currency: plan.currency });
  const monthlyLocal = currency === "USD" ? null : firstFinite(plan.monthlyPriceLocal, plan.billing?.monthlyLocal);
  const annualLocal = currency === "USD" ? null : firstFinite(plan.annualPriceLocal, plan.annualTotalLocal, plan.billing?.annualLocal);
  const monthlyEquivalentLocal = currency === "USD" ? null : firstFinite(
    plan.annualEquivalentMonthlyLocal,
    plan.quarterlyEquivalentMonthlyLocal,
  );
  const monthlyPublished = firstFinite(plan.monthlyUsd, plan.monthlyPriceUsd, plan.billing?.monthlyUsd, plan.billing?.amount);
  const annualPublished = firstFinite(plan.annualUsd, plan.annualPriceUsd, plan.billing?.annualUsd);
  const monthlyEquivalentPublished = firstFinite(plan.annualEquivalentMonthlyUsd);
  const monthly = Number.isFinite(monthlyPublished) ? monthlyPublished : pricingUsdFromLocal(monthlyLocal, currency);
  const annual = Number.isFinite(annualPublished) ? annualPublished : pricingUsdFromLocal(annualLocal, currency);
  const monthlyEquivalent = Number.isFinite(monthlyEquivalentPublished)
    ? monthlyEquivalentPublished
    : pricingUsdFromLocal(monthlyEquivalentLocal, currency);
  const meta = [
    Number.isFinite(monthly) || Number.isFinite(monthlyLocal)
      ? `${formatBillingPrice(monthly, monthlyLocal, currency)} ${tr("pricingPerMonth")}` : "",
    Number.isFinite(annual) || Number.isFinite(annualLocal)
      ? `${formatBillingPrice(annual, annualLocal, currency)} ${tr("pricingPerYear")}` : "",
    Number.isFinite(monthlyEquivalent) || Number.isFinite(monthlyEquivalentLocal)
      ? `${tr("pricingMonthlyEquivalent")} ${formatBillingPrice(monthlyEquivalent, monthlyEquivalentLocal, currency)}` : "",
    pricingQuotaLabel(plan),
  ].filter(Boolean).join(" · ");
  return `
    <span class="pricing-plan-chip">
      <strong>${escapeHtml(plan.name || plan.id)}</strong>
      <em>${escapeHtml(meta || tr(`pricingPlanTypes.${pricingPlanTypeGroup(plan.type || plan.billingType)}`))}</em>
    </span>
  `;
}

function renderPricingProviderOfferRow(modelOffer) {
  const { offer, modelSlug, model } = modelOffer;
  const modelLabel = model?.model || modelSlug || tr("notAvailable");
  const priceUnit = pricingOfferUnitLabel(offer);
  const localUnit = pricingLocalUnitLabel(offer.localEffectivePrice, offer.currency);
  const estimate = offer.estimated ? ` · ${tr("pricingLabels.estimate")}` : "";
  const displayOnly = !offer.comparable && Number.isFinite(offer.effectivePrice)
    ? ` · ${tr("pricingLabels.displayOnly")}`
    : "";
  const entitlement = offer.quotaLabel ? ` · ${offer.quotaLabel}` : "";
  const offerMeta = `${offer.planName}${estimate}${displayOnly}${entitlement}`;
  return `
    <span class="pricing-provider-offer-row">
      <span><strong>${escapeHtml(modelLabel)}</strong><em title="${escapeHtml(offerMeta)}">${escapeHtml(offerMeta)}</em></span>
      <b>${escapeHtml(formatUnitPrice(offer.effectivePrice))}<small>${escapeHtml(`${priceUnit}${localUnit ? ` · ${localUnit}` : ""}`)}</small></b>
    </span>
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
  const rankedProviderRows = providerRows.filter((model) => (
    Number.isFinite(model.rank) && Number.isFinite(modelDisplayScore(model))
  ));
  const best = rankedProviderRows[0] || providerRows[0];
  const averageScore = rankedProviderRows.length
    ? rankedProviderRows.reduce((sum, model) => sum + modelDisplayScore(model), 0) / rankedProviderRows.length
    : null;
  const averageScoreLabel = Number.isFinite(averageScore) ? formatNumber(averageScore) : tr("notAvailable");
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
            <span>${escapeHtml(tr("providerPageSubtitle", { count: providerRows.length, bestScore: formatModelDisplayScore(best) }))}</span>
          </div>
        </div>
      </div>
      <div class="detail-hero-facts">
        <span>${renderIcon("database")}${escapeHtml(tr("providerSummaryModels"))}: ${providerRows.length}</span>
        <span>${renderIcon("trophy")}${escapeHtml(tr("providerSummaryBest"))}: ${escapeHtml(formatModelDisplayScore(best))}</span>
        <span>${renderIcon("gauge")}${escapeHtml(tr("providerSummaryAverage"))}: ${escapeHtml(averageScoreLabel)}</span>
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
      <span class="rank-number">${escapeHtml(rankLabel(model))}</span>
      ${renderModelIcon(model)}
      <span class="provider-model-copy">
        <strong>${escapeHtml(model.model)}</strong>
        <em>${escapeHtml(formatDate(model.releaseDate))} · ${escapeHtml(sourceTypeLabel(sourceType(model)))}</em>
      </span>
      <span class="provider-model-stat">
        ${renderIcon("trophy")}
        <b>${escapeHtml(formatModelDisplayScore(model))}</b>
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
    .sort((a, b) => (Number.isFinite(a.rank) ? a.rank : Infinity) - (Number.isFinite(b.rank) ? b.rank : Infinity)
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
    arrowUpRight: '<path d="M7 17 17 7"></path><path d="M7 7h10v10"></path>',
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
