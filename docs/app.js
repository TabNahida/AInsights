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
    },
    back: "返回",
    backToRanking: "返回完整排名",
    modelNotFound: "没有找到这个模型",
    search: "搜索",
    searchPlaceholder: "模型或机构",
    dedupe: "去除重复档位",
    customTitle: "自定义占比",
    metricWeightsTitle: "AA 子项权重",
    metricWeightsSubtitle: "直接参与当前自定义排名的逐项权重，按已有模型数据量排序",
    metricCoverage: "{count} 个模型",
    metricGroupMeta: "{count} 个模型 · {metrics} 个数据项",
    customWeightPresetTitle: "权重预设",
    customWeightPresetSubtitle: "一键套用 AInsights Index 或 AA 三个方向，再继续微调下方测试项权重",
    customWeightPresetMeta: "{count} 项",
    missingModeTitle: "缺失值处理",
    missingModeSubtitle: "四个按钮是预设；下方滑块决定缺失项扣分强度和最低覆盖率",
    missingPresetTitle: "处理预设",
    penaltyLabel: "缺失扣分强度",
    penaltyHint: "0 表示只按可用项求均分；100 表示缺失项按 0 计入总权重，与普通 AInsights Index 排名口径一致。",
    minCoverageLabel: "最低覆盖率",
    minCoverageHint: "低于该覆盖率的模型不进入排名；100% 等同全覆盖",
    currentCustomStrategy: "当前策略",
    manualCustomStrategy: "手动配置",
    missingModes: {
      available: "只按可用项",
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
    reset: "重置",
    empty: "没有符合条件的模型",
    loadFailed: "数据加载失败：{message}",
    unknownCreator: "Unknown",
    reasoning: "Reasoning",
    defaultCorrection: "默认修正参考",
    footerPrefix: "数据来源：",
    footerSuffix: "。AInsights Index 基于其公开评测数据重新计算。",
    rankingItems: "个排名项",
    scorableModels: "个可评分模型",
    removedPrefix: "已去除",
    removedSuffix: "个重复档位",
    allTiers: "显示全部档位",
    sourceFilter: "来源",
    top20Title: "AInsights Index Top {count}",
    top20Subtitle: "固定使用 AInsights Index，按屏幕宽度展示 12-30 个去重模型",
    latestModelsTitle: "最新模型",
    latestModelsSubtitle: "按发布日期展示最近进入数据集的去重模型",
    fullRanking: "查看完整排名",
    costScatterTitle: "智能 vs 运行成本",
    costScatterSubtitle: "横轴为运行 AA Intelligence Index 的美元成本，使用对数刻度",
    scatterXAxis: "运行 Intelligence Index 的成本（USD，对数）",
    scatterYAxis: "AInsights Index",
    attractiveQuadrant: "高分低成本区域",
    noCostData: "没有足够的成本数据可绘制散点图",
    scoreBandsTitle: "分数带分布",
    scoreBandsSubtitle: "去重模型在 AInsights Index 上的集中区间",
    providerChartTitle: "机构覆盖",
    providerChartSubtitle: "按可评分去重模型数量和最高分展示",
    providerModelCount: "模型数量",
    providerBestScore: "最高分",
    providerPageTitle: "{provider} 模型概览",
    providerPageSubtitle: "{count} 个可评分去重模型 · 最高分 {bestScore}",
    providerNotFound: "没有找到这个机构",
    providerSummaryModels: "可评分模型",
    providerSummaryBest: "最高分",
    providerSummaryAverage: "平均分",
    providerSummaryOpen: "开源模型",
    providerModelsTitle: "模型列表",
    providerModelsSubtitle: "按 AInsights Index 分数排序，展示发布日期、来源类型和运行指标",
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
    compareBenchmarkTitle: "测试项数据",
    compareMetricColumn: "指标",
    compareRemove: "移除",
    compareRows: {
      provider: "供应商",
      score: "AInsights Index",
      rank: "排名",
      source: "来源",
      releaseDate: "发布日期",
      speed: "输出速度",
      context: "上下文",
      inputPrice: "输入价格",
      outputPrice: "输出价格",
      runCost: "AA 运行成本",
      coverage: "覆盖率",
    },
    sourceExplorerTitle: "测评源地图",
    sourceExplorerSubtitle: "AA 主数据之外的常用公开测评，用来交叉理解模型强弱项",
    detailRankTitle: "排名快照",
    detailBenchmarkTitle: "AInsights Index 参考项目",
    detailBenchmarkSubtitle: "参与 AInsights Index 默认权重的测试项",
    detailExternalTitle: "非参考项目分数",
    detailExternalSubtitle: "未参与 AInsights Index 默认权重的 AA 子项、官方发布页或其他公开测评",
    detailCostTitle: "成本与吞吐",
    detailVariantsTitle: "同模型档位",
    detailSourcesTitle: "外部测评参考",
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
      byScore: "AInsights Index",
      perRun: "运行成本",
      source: "来源",
    },
    headers: {
      model: "模型",
      score: "综合分",
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
        description: "按 AA Intelligence Index evaluation suite 原始占比计算；AA-Omniscience 修正为 12.5% 全部计入 Accuracy，非幻觉率权重为 0。",
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
        label: "自定义占比",
        description: "默认使用 AInsights Index 配置；先按可用项求均分，再按用户设置的缺失扣分和覆盖率门槛实时计算。",
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
    },
    back: "Back",
    backToRanking: "Back to full ranking",
    modelNotFound: "Model not found",
    search: "Search",
    searchPlaceholder: "Model or lab",
    dedupe: "Remove duplicate tiers",
    customTitle: "Custom weights",
    metricWeightsTitle: "AA benchmark weights",
    metricWeightsSubtitle: "Fine-grained weights used directly by the custom ranking, sorted by model coverage",
    metricCoverage: "{count} models",
    metricGroupMeta: "{count} models · {metrics} data fields",
    customWeightPresetTitle: "Weight presets",
    customWeightPresetSubtitle: "Start from AInsights Index or the three AA directions, then tune individual benchmark weights below",
    customWeightPresetMeta: "{count} fields",
    missingModeTitle: "Missing values",
    missingModeSubtitle: "The buttons are presets; use the sliders below to tune missing-value penalty strength and coverage",
    missingPresetTitle: "Treatment presets",
    penaltyLabel: "Missing penalty strength",
    penaltyHint: "0 averages available scores only; 100 counts missing fields as 0 in the total weight, matching the regular AInsights Index ranking.",
    minCoverageLabel: "Minimum coverage",
    minCoverageHint: "Models below this coverage are excluded; 100% equals full coverage",
    currentCustomStrategy: "Current strategy",
    manualCustomStrategy: "Manual",
    missingModes: {
      available: "Available only",
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
    reset: "Reset",
    empty: "No models match the current filters",
    loadFailed: "Failed to load data: {message}",
    unknownCreator: "Unknown",
    reasoning: "Reasoning",
    defaultCorrection: "Default correction reference",
    footerPrefix: "Source: ",
    footerSuffix: ". AInsights Index recalculates the public benchmark data.",
    rankingItems: "ranked items",
    scorableModels: "scorable models",
    removedPrefix: "Removed",
    removedSuffix: "duplicate tiers",
    allTiers: "Showing every tier",
    sourceFilter: "Source",
    top20Title: "AInsights Index Top {count}",
    top20Subtitle: "Fixed to AInsights Index, showing 12-30 deduplicated models by screen width",
    latestModelsTitle: "Latest models",
    latestModelsSubtitle: "Recently released deduplicated models in the dataset",
    fullRanking: "View full ranking",
    costScatterTitle: "Intelligence vs. Cost to Run",
    costScatterSubtitle: "X-axis is the USD cost to run AA Intelligence Index, shown on a log scale",
    scatterXAxis: "Cost to Run Intelligence Index (USD, Log Scale)",
    scatterYAxis: "AInsights Index",
    attractiveQuadrant: "High-score low-cost region",
    noCostData: "Not enough cost data to draw the scatter chart",
    scoreBandsTitle: "Score band distribution",
    scoreBandsSubtitle: "Where deduplicated models cluster on AInsights Index",
    providerChartTitle: "Provider coverage",
    providerChartSubtitle: "Scorable deduped model count and best score by lab",
    providerModelCount: "Model count",
    providerBestScore: "Best score",
    providerPageTitle: "{provider} model overview",
    providerPageSubtitle: "{count} scorable deduped models · best score {bestScore}",
    providerNotFound: "Provider not found",
    providerSummaryModels: "Scorable models",
    providerSummaryBest: "Best score",
    providerSummaryAverage: "Average score",
    providerSummaryOpen: "Open models",
    providerModelsTitle: "Model list",
    providerModelsSubtitle: "Sorted by AInsights Index score with release date, source type, and operating metrics",
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
    compareBenchmarkTitle: "Benchmark data",
    compareMetricColumn: "Metric",
    compareRemove: "Remove",
    compareRows: {
      provider: "Provider",
      score: "AInsights Index",
      rank: "Rank",
      source: "Source",
      releaseDate: "Release date",
      speed: "Output speed",
      context: "Context",
      inputPrice: "Input price",
      outputPrice: "Output price",
      runCost: "AA run cost",
      coverage: "Coverage",
    },
    sourceExplorerTitle: "Benchmark source map",
    sourceExplorerSubtitle: "Public evaluation sources to cross-check model strengths beyond AA",
    detailRankTitle: "Rank snapshot",
    detailBenchmarkTitle: "AInsights Index reference benchmarks",
    detailBenchmarkSubtitle: "Benchmarks used by the default AInsights Index weighting",
    detailExternalTitle: "Non-reference benchmark scores",
    detailExternalSubtitle: "AA submetrics, official release scores, and public evals outside the default AInsights Index weighting",
    detailCostTitle: "Cost and throughput",
    detailVariantsTitle: "Same-model tiers",
    detailSourcesTitle: "External evaluation references",
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
      byScore: "AInsights Index",
      perRun: "run cost",
      source: "Source",
    },
    headers: {
      model: "Model",
      score: "Score",
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
        description: "Uses the AA Intelligence Index evaluation suite weights; AA-Omniscience is corrected by assigning its full 12.5% weight to Accuracy and zero to non-hallucination rate.",
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
        label: "Custom weights",
        description: "Defaults to the AInsights Index configuration and recalculates live from user-selected benchmark weights, missing penalties, and coverage gates.",
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
  customWeights: {},
  customWeightPresetId: "zhihu-adjusted",
  customMissingMode: "zero",
  customPenaltyMax: 100,
  customMinCoveragePct: 0,
  customMetricGroupsCache: null,
  language: getInitialLanguage(),
  page: initialRoute.page,
  modelId: initialRoute.modelId,
  benchmarkId: initialRoute.benchmarkId,
  providerId: initialRoute.providerId,
  compareIds: initialRoute.compareIds || [],
  compareQuery: "",
  compareTouched: false,
  comparePickerOpen: false,
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
  speedHeader: document.querySelector("#speedHeader"),
  contextHeader: document.querySelector("#contextHeader"),
  priceHeader: document.querySelector("#priceHeader"),
  sourceHeader: document.querySelector("#sourceHeader"),
  coverageHeader: document.querySelector("#coverageHeader"),
  siteFooter: document.querySelector("#siteFooter"),
  metricTemplate: document.querySelector("#metricTemplate"),
};

const presetOrder = ["zhihu-adjusted", "aa-intelligence", "aa-coding", "aa-agentic", "custom"];
const customWeightPresetOrder = ["zhihu-adjusted", "aa-intelligence", "aa-coding", "aa-agentic"];
const missingModePresetOrder = ["available", "penalty", "zero", "complete"];
const missingModePresets = {
  available: { penalty: 0, minCoverage: 0 },
  penalty: { penalty: 10, minCoverage: 0 },
  zero: { penalty: 100, minCoverage: 0 },
  complete: { penalty: 0, minCoverage: 100 },
};
const pageOrder = ["home", "ranking", "compare", "benchmarks", "sources"];
const viewOrder = ["histogram", "table", "text"];
const sourceFilterOrder = ["all", "open", "closed", "unknown"];
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

init();

async function init() {
  try {
    state.data = window.AINSIGHTS_MODELS_DATA || (await fetchJsonData());
    state.presetId = state.data.defaultPreset;
    state.dedupe = Boolean(state.data.defaultDedupe);
    state.customWeights = customWeightsForPreset(state.customWeightPresetId);
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

function bindControlEvents() {
  els.searchInput.addEventListener("input", (event) => {
    state.query = event.target.value.trim().toLowerCase();
    render();
  });
  els.dedupeToggle.addEventListener("change", (event) => {
    state.dedupe = event.target.checked;
    render();
  });
  els.resetWeightsButton.addEventListener("click", () => {
    resetCustomConfiguration();
    state.presetId = "custom";
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
  els.modelHeader.textContent = tr("headers.model");
  els.scoreHeader.textContent = tr("headers.score");
  els.speedHeader.textContent = tr("headers.speed");
  els.contextHeader.textContent = tr("headers.context");
  els.priceHeader.textContent = tr("headers.price");
  els.sourceHeader.textContent = tr("headers.source");
  els.coverageHeader.textContent = tr("headers.coverage");
  els.languageButtons.setAttribute("aria-label", tr("languageLabel"));
  els.siteFooter.innerHTML = `${escapeHtml(tr("footerPrefix"))}<a href="${escapeHtml(state.data.source.url)}" target="_blank" rel="noreferrer">Artificial Analysis</a> · <a href="${escapeHtml(pageHref("sources"))}">${escapeHtml(tr("sourcesBadge", { count: catalogSources().length }))}</a>${escapeHtml(tr("footerSuffix"))}`;

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
      render();
    });
    els.sourceFilterButtons.append(button);
  }
}

function render() {
  const preset = state.data.presets[state.presetId];
  els.homeView.hidden = state.page !== "home";
  els.rankingView.hidden = state.page !== "ranking";
  els.sourcesView.hidden = state.page !== "sources";
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

  renderResults(preset);
}

function renderResults(preset) {
  const scored = scoreModels(preset);
  const homePreset = state.data.presets["zhihu-adjusted"];
  const homeRanked = rankRows(dedupeByBestVariant(scoreModels(homePreset, "zhihu-adjusted")));
  const filtered = scored.filter(matchesQuery).filter(matchesSourceFilter);
  const visible = state.dedupe ? dedupeByBestVariant(filtered) : filtered;
  const ranked = rankRows(visible);
  const allRanked = rankRows(scored);

  if (!els.homeView.hidden) renderHome(homeRanked);
  if (!els.rankingView.hidden) {
    renderSummary(filtered.length, visible.length, scored.length, preset);
    renderRankings(ranked);
  }
  if (!els.modelView.hidden) renderModelDetail(allRanked, preset);
  if (!els.benchmarkView.hidden) renderBenchmarkPage();
  if (els.providerView && !els.providerView.hidden) renderProviderPage(homeRanked);
  if (els.compareView && !els.compareView.hidden) renderComparePage(homeRanked);
}

function scoreModels(preset, presetId = state.presetId) {
  return state.data.models
    .map((model) => {
      const result = scoreModel(model, preset, presetId);
      return {
        ...model,
        score: result.score,
        coverage: result.coverage,
        coverageLabel: result.coverageLabel,
        availableWeight: result.availableWeight,
        scoreMeta: result.scoreMeta,
      };
    })
    .filter((model) => Number.isFinite(model.score));
}

function scoreModel(model, preset, presetId = state.presetId) {
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

  if (presetId === "custom") {
    return scoreModelForCustomWeights(model);
  }

  const weights = presetId === "custom" ? state.customWeights : preset.weights;
  let weightedScore = 0;
  let denominator = 0;
  let availableWeight = 0;
  let coverage = 0;
  const ignoreMissing = Boolean(preset.ignoreMissing);
  const minCoverage = Number(preset.minCoverage || 0);
  for (const metric of state.data.metrics) {
    const weight = Number(weights[metric.key] || 0);
    const value = model.scores[metric.key];
    if (weight <= 0) continue;
    if (Number.isFinite(value)) {
      weightedScore += value * weight;
      denominator += weight;
      availableWeight += weight;
      coverage += 1;
    } else if (!ignoreMissing) {
      denominator += weight;
    }
  }
  const score = denominator > 0 && coverage >= minCoverage ? weightedScore / denominator : null;
  return {
    score,
    coverage,
    availableWeight,
    scoreMeta: `${formatNumber(availableWeight)}w`,
  };
}

function scoreModelForCustomWeights(model) {
  let weightedScore = 0;
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
    const value = customMetricGroupValue(model, group);
    if (Number.isFinite(value)) {
      weightedScore += value * weight;
      denominator += weight;
      availableWeight += weight;
      coverage += 1;
    } else {
      missingWeight += weight;
    }
  }

  const coverageRatio = selected > 0 ? (coverage / selected) * 100 : 0;
  const minCoverage = clamp(Number(state.customMinCoveragePct || 0), 0, 100);
  const availableScore = denominator > 0 && selected > 0 && coverageRatio >= minCoverage ? weightedScore / denominator : null;
  let score = availableScore;
  const penaltyRatio = clamp(Number(state.customPenaltyMax || 0), 0, 100) / 100;
  const zeroScore = selectedWeight > 0 && selected > 0 && coverageRatio >= minCoverage ? weightedScore / selectedWeight : null;
  if (Number.isFinite(availableScore) && penaltyRatio > 0 && selectedWeight > 0) {
    score = availableScore + (zeroScore - availableScore) * penaltyRatio;
  }
  if (!Number.isFinite(score) && penaltyRatio >= 1 && Number.isFinite(zeroScore)) score = zeroScore;
  return {
    score,
    coverage,
    coverageLabel: `${coverage}/${selected} · ${formatTrimmed(coverageRatio, 0)}%`,
    availableWeight,
    scoreMeta: `${formatNumber(availableWeight)}w · ${formatTrimmed(coverageRatio, 0)}%`,
  };
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

function rankRows(models) {
  const sorted = [...models].sort((a, b) => b.score - a.score || a.model.localeCompare(b.model));
  let previousScore = null;
  let currentRank = 0;
  return sorted.map((model, index) => {
    if (previousScore === null || model.score !== previousScore) {
      currentRank = index + 1;
      previousScore = model.score;
    }
    return { ...model, rank: currentRank };
  });
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
    <span>${escapeHtml(presetDescription(state.presetId, preset))}</span>
    <a href="${escapeHtml(state.data.source.defaultCorrectionReference)}" target="_blank" rel="noreferrer">${escapeHtml(tr("defaultCorrection"))}</a>
  `;
}

function resetCustomConfiguration() {
  state.customWeightPresetId = "zhihu-adjusted";
  state.customWeights = customWeightsForPreset(state.customWeightPresetId);
  applyMissingModePreset("zero");
}

function applyMissingModePreset(mode) {
  const preset = missingModePresets[mode] || missingModePresets.zero;
  state.customMissingMode = mode;
  state.customPenaltyMax = preset.penalty;
  state.customMinCoveragePct = preset.minCoverage;
}

function syncMissingModePreset() {
  state.customMissingMode = matchingMissingModePreset() || "manual";
}

function matchingMissingModePreset() {
  return missingModePresetOrder.find((mode) => {
    const preset = missingModePresets[mode];
    return Number(preset.penalty) === Number(state.customPenaltyMax)
      && Number(preset.minCoverage) === Number(state.customMinCoveragePct);
  });
}

function customWeightsForPreset(presetId) {
  const weights = Object.fromEntries(customMetricGroups().map((group) => [group.id, 0]));
  const preset = state.data.presets[presetId];
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
      <div class="weight-group-head">
        <h3>${escapeHtml(tr("metricWeightsTitle"))}</h3>
        <p>${escapeHtml(tr("metricWeightsSubtitle"))}</p>
      </div>
      <div class="metric-weight-controls" data-weight-controls="metrics"></div>
    </section>
  `;
  renderCustomWeightPresetControls(els.weightsGrid.querySelector("[data-custom-weight-presets]"));
  renderMissingModeControls(els.weightsGrid.querySelector("[data-missing-mode-controls]"));
  const metricTarget = els.weightsGrid.querySelector('[data-weight-controls="metrics"]');
  const groups = customMetricGroups()
    .sort((a, b) => (
      b.coverage - a.coverage
      || Number(b.defaultWeight || 0) - Number(a.defaultWeight || 0)
      || a.label.localeCompare(b.label)
    ));
  for (const group of groups) {
    const fragment = els.metricTemplate.content.cloneNode(true);
    const labelText = fragment.querySelector("span");
    const input = fragment.querySelector("input");
    const output = fragment.querySelector("output");
    labelText.className = "metric-weight-label";
    labelText.innerHTML = `
      <strong>${escapeHtml(group.label)}</strong>
      <em>${escapeHtml(tr("metricGroupMeta", { count: group.coverage, metrics: group.metrics.length }))}</em>
    `;
    input.dataset.metricGroup = group.id;
    input.value = state.customWeights[group.id] ?? group.defaultWeight;
    output.value = formatWeight(input.value);
    input.addEventListener("input", (event) => {
      state.customWeights[event.target.dataset.metricGroup] = Number(event.target.value);
      state.customWeightPresetId = "custom";
      updateCustomWeightPresetSelection();
      output.value = formatWeight(event.target.value);
    });
    input.addEventListener("change", () => {
      renderResults(state.data.presets.custom);
    });
    metricTarget.append(fragment);
  }
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
        <span class="control-label">${escapeHtml(tr("missingPresetTitle"))}</span>
        <div class="segmented-control" data-missing-preset>
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

function customMissingModeLabel() {
  if (state.customMissingMode === "manual") return tr("manualCustomStrategy");
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

function customMetricGroupValue(model, group) {
  const presetWeightedMetrics = group.metrics.filter((metric) => Number(state.data.presets[state.customWeightPresetId]?.weights?.[metric.key] || 0) > 0);
  const metrics = presetWeightedMetrics.length ? presetWeightedMetrics : group.metrics;
  const values = metrics
    .map((metric) => model.scores?.[metric.key])
    .filter(Number.isFinite);
  if (values.length === 0) return null;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function renderHome(models) {
  renderHomeMetrics(models);
  renderLatestModels(models);
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
    .sort((a, b) => parsedReleaseTime(b.releaseDate) - parsedReleaseTime(a.releaseDate) || b.score - a.score)
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
        <span class="latest-model-score">${renderIcon("trophy")}<b>${escapeHtml(formatNumber(model.score))}</b></span>
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
      meta: `${formatNumber(leader.score)} · ${leader.creator || tr("unknownCreator")}`,
    },
    {
      label: tr("homeStats.topOpen"),
      model: topOpen,
      meta: topOpen ? `${formatNumber(topOpen.score)} · ${topOpen.creator || tr("unknownCreator")}` : "—",
    },
    {
      label: tr("homeStats.bestValue"),
      model: bestValue,
      meta: bestValue ? `${formatNumber(bestValue.score)} · ${formatMoney(modelCost(bestValue))} ${tr("homeStats.perRun")}` : "—",
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
            <span class="top-bar-value">${formatNumber(model.score)}</span>
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
              <title>${escapeHtml(`${model.model} · ${formatNumber(model.score)} · ${formatMoney(modelCost(model))}`)}</title>
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
        <em>${escapeHtml(formatNumber(row.bestScore))}</em>
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

function sourceCardsHtml(compact = false, model = null) {
  const sources = catalogSources();
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

function catalogSources() {
  return (state.data.externalSources || []).filter((source) => !isOfficialModelSource(source));
}

function isOfficialModelSource(source) {
  return /^official\b/i.test(String(source.category || ""))
    || /\bofficial\b/i.test(String(source.label || ""));
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
  const scoreWidth = clamp(model.score, 0, 100);
  return `
    <div class="histogram-row">
      <div class="histogram-rank">#${model.rank}</div>
      <div class="histogram-model">
        ${renderModelIcon(model)}
        <div class="histogram-label">
          <a href="${escapeHtml(modelHref(model))}">${escapeHtml(model.model)}</a>
          <span>${renderProviderTextLink(model.creator, "ranking")} · ${escapeHtml(sourceTypeLabel(sourceType(model)))}</span>
        </div>
      </div>
      <div class="histogram-track" aria-label="${escapeHtml(tr("headers.score"))} ${formatNumber(model.score)}">
        <span class="histogram-fill" style="--value: ${scoreWidth}%"></span>
      </div>
      <div class="histogram-score">${formatNumber(model.score)}</div>
      ${renderCompareEntry(model, "ranking")}
    </div>
  `;
}

function renderTable(models) {
  if (models.length === 0) {
    els.rankingBody.innerHTML = `<tr><td class="empty" colspan="8">${escapeHtml(tr("empty"))}</td></tr>`;
    return;
  }
  els.rankingBody.innerHTML = models.map(renderRow).join("");
}

function renderRow(model) {
  const scoreWidth = clamp(model.score, 0, 100);
  const reason = model.isReasoning ? `<span class="pill">${escapeHtml(tr("reasoning"))}</span>` : "";
  return `
    <tr>
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
        <div class="score-value"><span>${formatNumber(model.score)}</span><span class="muted">${escapeHtml(model.scoreMeta || "")}</span></div>
        <div class="score-bar" style="--value: ${scoreWidth}%"><span></span></div>
      </td>
      <td>${escapeHtml(formatSpeed(model.medianOutputSpeed))}</td>
      <td>${escapeHtml(formatTokens(model.contextWindowTokens))}</td>
      <td>${renderPriceCell(model.pricing)}</td>
      <td>${renderSourcePill(model)}</td>
      <td>${escapeHtml(model.coverageLabel || model.coverage)}</td>
    </tr>
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
      <div class="text-ranking-row">
        <span>#${model.rank}</span>
        <a class="text-model" href="${escapeHtml(modelHref(model))}">${escapeHtml(model.model)}</a>
        ${renderProviderTextLink(creator, "ranking")}
        <strong>${formatNumber(model.score)}</strong>
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
      <a class="back-link" href="${escapeHtml(modelBackHref())}" data-history-back>${renderIcon("arrowLeft")}${escapeHtml(tr("back"))}</a>
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
    <a class="back-link" href="${escapeHtml(modelBackHref())}" data-history-back>${renderIcon("arrowLeft")}${escapeHtml(tr("back"))}</a>
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
        <p>${escapeHtml(tr("currentPreset"))}: ${escapeHtml(presetLabel(state.presetId))}</p>
      </div>
      <div class="rank-card-grid">${renderRankCards(model)}</div>
    </section>

    <section class="detail-grid">
      <section class="detail-section">
        <div class="detail-section-head">
          <h2>${escapeHtml(tr("detailCostTitle"))}</h2>
        </div>
        <div class="stat-grid">
          ${renderDetailStat(tr("headers.score"), formatNumber(model.score), `#${model.rank}`, "trophy")}
          ${renderDetailStat(tr("headers.speed"), formatSpeed(model.medianOutputSpeed), tr("table.tokensPerSecond"), "gauge")}
          ${renderDetailStat(tr("headers.context"), formatTokens(model.contextWindowTokens), "", "database")}
          ${renderDetailStat(tr("table.input"), formatMoney(model.pricing?.inputPerMillionTokensUsd), tr("table.perMillion"), "arrowDown")}
          ${renderDetailStat(tr("table.output"), formatMoney(model.pricing?.outputPerMillionTokensUsd), tr("table.perMillion"), "arrowUp")}
          ${renderDetailStat("AA run", formatMoney(modelCost(model)), "cost", "dollar")}
        </div>
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
      <div class="source-grid compact">${sourceCardsHtml(true, model)}</div>
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
    const score = ranked ? formatNumber(ranked.score) : tr("notAvailable");
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

function renderDetailHeroFacts(model) {
  const facts = [
    ["calendar", `${tr("releaseDate")}: ${formatDate(model.releaseDate)}`],
    ["database", sourceTypeLabel(sourceType(model))],
    ["gauge", `${formatNumber(model.score)} ${tr("headers.score")}`],
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
      <span>#${row.rank}</span>
      <strong>${escapeHtml(row.model)}</strong>
      <em>${escapeHtml(formatNumber(row.score))}</em>
    </a>
  `).join("");
}

function benchmarkProfileRows(model, { reference = true } = {}) {
  const defaultWeights = state.data.presets["zhihu-adjusted"].weights || {};
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
  const defaultWeights = state.data.presets["zhihu-adjusted"].weights || {};
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
    <article class="benchmark-ranking-row" style="--value: ${valueWidth}%">
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
    state.compareIds = models.slice(0, 3).map(modelRouteId);
  }
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
        <em>${escapeHtml(model.creator || tr("unknownCreator"))} · #${escapeHtml(model.rank)} · ${escapeHtml(formatNumber(model.score))}</em>
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
        <span>${renderIcon("trophy")}<b>${escapeHtml(formatNumber(model.score))}</b><em>#${escapeHtml(model.rank)}</em></span>
        <span>${renderIcon("gauge")}<b>${escapeHtml(formatSpeed(model.medianOutputSpeed))}</b><em>${escapeHtml(tr("compareRows.speed"))}</em></span>
        <span>${renderIcon("database")}<b>${escapeHtml(compactNumber(model.contextWindowTokens))}</b><em>${escapeHtml(tr("compareRows.context"))}</em></span>
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
      values: models.map((model) => compareValue(formatNumber(model.score), `#${model.rank}`)),
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
      values: models.map((model) => compareValue(formatSpeed(model.medianOutputSpeed))),
    },
    {
      label: tr("compareRows.context"),
      iconName: "database",
      values: models.map((model) => compareValue(formatTokens(model.contextWindowTokens))),
    },
    {
      label: tr("compareRows.inputPrice"),
      iconName: "arrowDown",
      values: models.map((model) => compareValue(formatMoney(model.pricing?.inputPerMillionTokensUsd), tr("table.perMillion"))),
    },
    {
      label: tr("compareRows.outputPrice"),
      iconName: "arrowUp",
      values: models.map((model) => compareValue(formatMoney(model.pricing?.outputPerMillionTokensUsd), tr("table.perMillion"))),
    },
    {
      label: tr("compareRows.runCost"),
      iconName: "dollar",
      values: models.map((model) => compareValue(formatMoney(modelCost(model)))),
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
  return `${model.model} · ${model.creator || tr("unknownCreator")} · ${formatNumber(model.score)}`;
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
  const averageScore = providerRows.reduce((sum, model) => sum + model.score, 0) / providerRows.length;
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
            <span>${escapeHtml(tr("providerPageSubtitle", { count: providerRows.length, bestScore: formatNumber(best.score) }))}</span>
          </div>
        </div>
      </div>
      <div class="detail-hero-facts">
        <span>${renderIcon("database")}${escapeHtml(tr("providerSummaryModels"))}: ${providerRows.length}</span>
        <span>${renderIcon("trophy")}${escapeHtml(tr("providerSummaryBest"))}: ${escapeHtml(formatNumber(best.score))}</span>
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
        <b>${escapeHtml(formatNumber(model.score))}</b>
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
    .sort((a, b) => b.score - a.score || (parsedReleaseTime(b.releaseDate) || 0) - (parsedReleaseTime(a.releaseDate) || 0) || a.model.localeCompare(b.model));
}

function metricDefinition(metricKey) {
  return state.data.metrics.find((metric) => metric.key === metricKey) || {};
}

function renderIcon(name) {
  const paths = {
    arrowLeft: '<path d="M19 12H5"></path><path d="m12 19-7-7 7-7"></path>',
    arrowDown: '<path d="M12 5v14"></path><path d="m19 12-7 7-7-7"></path>',
    arrowUp: '<path d="M12 19V5"></path><path d="m5 12 7-7 7 7"></path>',
    brain: '<path d="M8 13a4 4 0 0 1-2-7.5A4 4 0 0 1 13 4a4 4 0 0 1 7 2.5A4 4 0 0 1 18 14"></path><path d="M8 13v3a4 4 0 0 0 4 4h1"></path><path d="M16 13v7"></path>',
    calendar: '<path d="M8 2v4"></path><path d="M16 2v4"></path><rect x="3" y="4" width="18" height="18" rx="2"></rect><path d="M3 10h18"></path>',
    code: '<path d="m16 18 6-6-6-6"></path><path d="m8 6-6 6 6 6"></path>',
    database: '<ellipse cx="12" cy="5" rx="8" ry="3"></ellipse><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5"></path><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"></path>',
    dollar: '<path d="M12 2v20"></path><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7H14a3.5 3.5 0 0 1 0 7H6"></path>',
    gauge: '<path d="M12 14l4-4"></path><path d="M3.3 18a10 10 0 1 1 17.4 0"></path>',
    network: '<rect x="16" y="16" width="6" height="6" rx="1"></rect><rect x="2" y="16" width="6" height="6" rx="1"></rect><rect x="9" y="2" width="6" height="6" rx="1"></rect><path d="M12 8v4"></path><path d="M6 16l6-4 6 4"></path>',
    plus: '<path d="M5 12h14"></path><path d="M12 5v14"></path>',
    sliders: '<path d="M4 21v-7"></path><path d="M4 10V3"></path><path d="M12 21v-9"></path><path d="M12 8V3"></path><path d="M20 21v-5"></path><path d="M20 12V3"></path><path d="M2 14h4"></path><path d="M10 8h4"></path><path d="M18 16h4"></path>',
    trophy: '<path d="M8 21h8"></path><path d="M12 17v4"></path><path d="M7 4h10v5a5 5 0 0 1-10 0V4Z"></path><path d="M5 6H3a3 3 0 0 0 3 3h1"></path><path d="M19 6h2a3 3 0 0 1-3 3h-1"></path>',
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
  els.rankingBody.innerHTML = `<tr><td class="empty" colspan="8">${escapeHtml(message)}</td></tr>`;
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
  const sourcePage = typeof source === "object" ? source.page : source;
  const providerId = context.providerId || (typeof source === "object" ? source.providerId : "") || (sourcePage === "provider" ? state.providerId : "");
  const benchmarkId = context.benchmarkId || (typeof source === "object" ? source.benchmarkId : "") || (sourcePage === "benchmarks" ? state.benchmarkId : "");
  const compareIds = normalizeCompareIds(context.compareIds || (typeof source === "object" ? source.compareIds : []) || (sourcePage === "compare" ? state.compareIds : []));
  const providerSource = context.providerSource || (typeof source === "object" ? source.providerSource : null) || null;
  if (sourcePage && sourcePage !== "model") params.set("from", sourcePage);
  if (providerId) params.set("provider", providerId);
  if (benchmarkId) params.set("benchmark", benchmarkId);
  if (compareIds.length) params.set("models", compareIds.join(","));
  if (providerSource?.page) {
    params.set("providerFrom", providerSource.page);
    if (providerSource.benchmarkId) params.set("providerBenchmark", providerSource.benchmarkId);
    if (providerSource.compareIds?.length) params.set("providerModels", normalizeCompareIds(providerSource.compareIds).join(","));
  }
  return `model.html?${params.toString()}`;
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
  if (source.page === "ranking") return pageHref("ranking");
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

function currentProviderBackSource() {
  const params = new URLSearchParams(location.search);
  return {
    page: params.get("from") || "home",
    benchmarkId: params.get("benchmark") || "",
    compareIds: compareIdsFromParams(params),
  };
}

function providerBackHref() {
  const source = currentProviderBackSource();
  if (source.page === "ranking") return pageHref("ranking");
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
