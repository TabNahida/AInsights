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
    },
    search: "搜索",
    searchPlaceholder: "模型或机构",
    dedupe: "去除重复档位",
    customTitle: "自定义占比",
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
    fullRanking: "查看完整排名",
    costScatterTitle: "智能 vs 运行成本",
    costScatterSubtitle: "横轴为运行 AA Intelligence Index 的美元成本，使用对数刻度",
    scatterXAxis: "运行 Intelligence Index 的成本（USD，对数）",
    scatterYAxis: "AInsights Index",
    attractiveQuadrant: "高分低成本区域",
    noCostData: "没有足够的成本数据可绘制散点图",
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
        description: "默认使用 AInsights Index 配置；可按用户设置的评测权重实时计算，缺失项按 0 计入分母。",
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
    },
    search: "Search",
    searchPlaceholder: "Model or lab",
    dedupe: "Remove duplicate tiers",
    customTitle: "Custom weights",
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
    fullRanking: "View full ranking",
    costScatterTitle: "Intelligence vs. Cost to Run",
    costScatterSubtitle: "X-axis is the USD cost to run AA Intelligence Index, shown on a log scale",
    scatterXAxis: "Cost to Run Intelligence Index (USD, Log Scale)",
    scatterYAxis: "AInsights Index",
    attractiveQuadrant: "High-score low-cost region",
    noCostData: "Not enough cost data to draw the scatter chart",
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
        description: "Defaults to the AInsights Index configuration and recalculates live from user-selected benchmark weights, with missing values counted as zero in the denominator.",
      },
    },
  },
};

const state = {
  data: null,
  presetId: null,
  dedupe: true,
  query: "",
  customWeights: {},
  language: getInitialLanguage(),
  page: getInitialPage(),
  viewMode: "histogram",
  sourceFilter: "all",
  topChartLimit: 20,
};

const els = {
  updatedAt: document.querySelector("#updatedAt"),
  sourceLink: document.querySelector("#sourceLink"),
  pageButtons: document.querySelector("#pageButtons"),
  homeView: document.querySelector("#homeView"),
  rankingView: document.querySelector("#rankingView"),
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
  top20Title: document.querySelector("#top20Title"),
  top20Subtitle: document.querySelector("#top20Subtitle"),
  viewFullRankingLink: document.querySelector("#viewFullRankingLink"),
  costScatterTitle: document.querySelector("#costScatterTitle"),
  costScatterSubtitle: document.querySelector("#costScatterSubtitle"),
  top20Chart: document.querySelector("#top20Chart"),
  costScatter: document.querySelector("#costScatter"),
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
const pageOrder = ["home", "ranking"];
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
    state.customWeights = Object.fromEntries(state.data.metrics.map((metric) => [metric.key, metric.defaultWeight]));
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
    state.customWeights = Object.fromEntries(state.data.metrics.map((metric) => [metric.key, metric.defaultWeight]));
    state.presetId = "custom";
    render();
  });
  window.addEventListener("hashchange", () => {
    state.page = getInitialPage();
    renderStaticControls();
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
  els.searchLabel.textContent = tr("search");
  els.searchInput.placeholder = tr("searchPlaceholder");
  els.dedupeLabel.textContent = tr("dedupe");
  els.customTitle.textContent = tr("customTitle");
  els.resetWeightsButton.textContent = tr("reset");
  els.top20Title.textContent = tr("top20Title", { count: state.topChartLimit });
  els.top20Subtitle.textContent = tr("top20Subtitle");
  els.viewFullRankingLink.textContent = tr("fullRanking");
  els.costScatterTitle.textContent = tr("costScatterTitle");
  els.costScatterSubtitle.textContent = tr("costScatterSubtitle");
  els.modelHeader.textContent = tr("headers.model");
  els.scoreHeader.textContent = tr("headers.score");
  els.speedHeader.textContent = tr("headers.speed");
  els.contextHeader.textContent = tr("headers.context");
  els.priceHeader.textContent = tr("headers.price");
  els.sourceHeader.textContent = tr("headers.source");
  els.coverageHeader.textContent = tr("headers.coverage");
  els.languageButtons.setAttribute("aria-label", tr("languageLabel"));
  els.siteFooter.innerHTML = `${escapeHtml(tr("footerPrefix"))}<a href="${escapeHtml(state.data.source.url)}" target="_blank" rel="noreferrer">Artificial Analysis</a>${escapeHtml(tr("footerSuffix"))}`;

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
      state.page = id;
      history.replaceState(null, "", id === "home" ? "#" : "#ranking");
      render();
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

  renderResults(preset);
}

function renderResults(preset) {
  const scored = scoreModels(preset);
  const homePreset = state.data.presets["zhihu-adjusted"];
  const homeRanked = rankRows(dedupeByBestVariant(scoreModels(homePreset, "zhihu-adjusted")));
  const filtered = scored.filter(matchesQuery).filter(matchesSourceFilter);
  const visible = state.dedupe ? dedupeByBestVariant(filtered) : filtered;
  const ranked = rankRows(visible);
  const capped = ranked.slice(0, 250);

  renderHome(homeRanked);
  renderSummary(filtered.length, visible.length, scored.length, preset);
  renderRankings(capped);
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

function renderWeights() {
  els.weightsGrid.innerHTML = "";
  for (const metric of state.data.metrics) {
    const fragment = els.metricTemplate.content.cloneNode(true);
    const labelText = fragment.querySelector("span");
    const input = fragment.querySelector("input");
    const output = fragment.querySelector("output");
    labelText.textContent = metric.label;
    input.value = state.customWeights[metric.key] ?? metric.defaultWeight;
    output.value = formatWeight(input.value);
    input.addEventListener("input", (event) => {
      state.customWeights[metric.key] = Number(event.target.value);
      output.value = formatWeight(event.target.value);
      renderResults(state.data.presets.custom);
    });
    els.weightsGrid.append(fragment);
  }
}

function renderHome(models) {
  renderHomeMetrics(models);
  renderTop20Chart(models.slice(0, state.topChartLimit));
  renderCostScatter(models.filter((model) => Number.isFinite(modelCost(model)) && modelCost(model) > 0).slice(0, 28));
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
        <a class="home-metric-model" href="https://artificialanalysis.ai${escapeHtml(stat.model.modelUrl)}" target="_blank" rel="noreferrer">
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
          <a class="top-bar-item" href="https://artificialanalysis.ai${escapeHtml(model.modelUrl)}" title="${escapeHtml(model.model)}" target="_blank" rel="noreferrer" style="--bar-width: ${width}%; --bar-color: ${color}">
            <span class="top-bar-rank">#${model.rank || index + 1}</span>
            <span class="top-bar-model">
              ${renderModelIcon(model)}
              <span>
                <strong>${escapeHtml(model.model)}</strong>
                <em>${escapeHtml(model.creator || tr("unknownCreator"))} · ${escapeHtml(sourceTypeLabel(sourceType(model)))}</em>
              </span>
            </span>
            <span class="top-bar-track"><span></span></span>
            <span class="top-bar-value">${formatNumber(model.score)}</span>
          </a>
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

  const width = 980;
  const height = 500;
  const margin = { top: 42, right: 58, bottom: 76, left: 72 };
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
  const labelOrder = new Map(scatterLabelModels(models, costThreshold, scoreThreshold).map((model, index) => [model.modelKey, index]));
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
        ${models.map((model, index) => {
          const x = xFor(modelCost(model));
          const y = yFor(model.score);
          const labelIndex = labelOrder.get(model.modelKey);
          const placement = scatterLabelPlacement(x, y, labelIndex ?? index, margin, plotWidth, plotHeight);
          const labeled = labelOrder.has(model.modelKey);
          return `
            <g class="scatter-point${labeled ? " is-labeled" : ""}">
              <circle cx="${x}" cy="${y}" r="${labeled ? 6.4 : 4.8}" fill="${providerColor(model, index)}"></circle>
              <title>${escapeHtml(`${model.model} · ${formatNumber(model.score)} · ${formatMoney(modelCost(model))}`)}</title>
              ${labeled ? `<text class="scatter-label" x="${placement.x}" y="${placement.y}" text-anchor="${placement.anchor}">${escapeHtml(model.model)}</text>` : ""}
            </g>
          `;
        }).join("")}
      </svg>
    </div>
  `;
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
  els.histogramList.innerHTML = models.slice(0, 120).map(renderHistogramRow).join("");
}

function renderHistogramRow(model) {
  const scoreWidth = clamp(model.score, 0, 100);
  return `
    <div class="histogram-row">
      <div class="histogram-rank">#${model.rank}</div>
      <div class="histogram-model">
        ${renderModelIcon(model)}
        <div class="histogram-label">
          <a href="https://artificialanalysis.ai${escapeHtml(model.modelUrl)}" target="_blank" rel="noreferrer">${escapeHtml(model.model)}</a>
          <span>${escapeHtml(model.creator || tr("unknownCreator"))} · ${escapeHtml(sourceTypeLabel(sourceType(model)))}</span>
        </div>
      </div>
      <div class="histogram-track" aria-label="${escapeHtml(tr("headers.score"))} ${formatNumber(model.score)}">
        <span class="histogram-fill" style="--value: ${scoreWidth}%"></span>
      </div>
      <div class="histogram-score">${formatNumber(model.score)}</div>
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
            <a class="model-name" href="https://artificialanalysis.ai${escapeHtml(model.modelUrl)}" target="_blank" rel="noreferrer">${escapeHtml(model.model)}</a>
          </div>
          <div class="model-meta">
            <span>${escapeHtml(model.creator || tr("unknownCreator"))}</span>
            ${reason}
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
        <span class="text-model">${escapeHtml(model.model)} — ${escapeHtml(creator)}</span>
        <strong>${formatNumber(model.score)}</strong>
        <span>${escapeHtml(source)}</span>
      </div>
    `;
  }).join("");
}

function renderModelIcon(model) {
  const icon = model.modelIcon || {};
  const label = icon.fallbackLabel || icon.label || initials(model.creator || model.model);
  const title = icon.title || model.creator || model.model;
  const src = typeof icon.src === "string" && icon.src.startsWith("https://artificialanalysis.ai/")
    ? icon.src
    : "";
  const image = src
    ? `<img src="${escapeHtml(src)}" alt="" loading="lazy" referrerpolicy="no-referrer" style="opacity:0" onload="this.style.opacity=1;this.nextElementSibling.hidden=true" onerror="this.hidden=true;this.nextElementSibling.hidden=false" />`
    : "";
  return `<span class="provider-icon" role="img" aria-label="${escapeHtml(title)}">${image}<span class="icon-fallback">${escapeHtml(label)}</span></span>`;
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
  els.costScatter.innerHTML = `<div class="empty">${escapeHtml(message)}</div>`;
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

function getInitialLanguage() {
  try {
    const stored = localStorage.getItem(LANGUAGE_STORAGE_KEY);
    if (copy[stored]) return stored;
  } catch {
    // Ignore storage errors in privacy-restricted contexts.
  }
  return navigator.language && navigator.language.toLowerCase().startsWith("zh") ? "zh-CN" : DEFAULT_LANGUAGE;
}

function getInitialPage() {
  return location.hash.replace("#", "") === "ranking" ? "ranking" : "home";
}

function saveLanguage(language) {
  try {
    localStorage.setItem(LANGUAGE_STORAGE_KEY, language);
  } catch {
    // Language selection still works for the current session.
  }
}

function tr(path, variables = {}) {
  const primary = lookup(copy[state.language], path);
  const fallback = lookup(copy[DEFAULT_LANGUAGE], path);
  const value = primary ?? fallback ?? path;
  if (typeof value !== "string") return String(value);
  return value.replace(/\{([a-zA-Z0-9_]+)\}/g, (_, key) => variables[key] ?? "");
}

function lookup(source, path) {
  return path.split(".").reduce((current, part) => {
    if (current && Object.prototype.hasOwnProperty.call(current, part)) return current[part];
    return undefined;
  }, source);
}

function initials(value) {
  const tokens = String(value || "").match(/[a-z0-9]+/gi) || [];
  if (tokens.length === 0) return "AI";
  if (tokens.length === 1) return tokens[0].slice(0, 3).toUpperCase();
  return tokens.slice(0, 3).map((token) => token[0].toUpperCase()).join("");
}

function formatNumber(value) {
  return Number.isFinite(value) ? value.toFixed(1) : "—";
}

function formatSpeed(value) {
  if (!Number.isFinite(value) || value <= 0) return "—";
  return `${compactNumber(value)} ${tr("table.tokensPerSecond")}`;
}

function formatTokens(value) {
  if (!Number.isFinite(value) || value <= 0) return "—";
  return `${compactNumber(value)} ${tr("table.tokens")}`;
}

function formatMoney(value) {
  if (!Number.isFinite(value)) return "—";
  const digits = Math.abs(value) < 1 ? 4 : 2;
  return `$${value.toLocaleString("en-US", {
    maximumFractionDigits: digits,
    minimumFractionDigits: 0,
  })}`;
}

function compactNumber(value) {
  return new Intl.NumberFormat(state.language, {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
}

function formatAxisCost(value) {
  if (value >= 1000) return `${formatTrimmed(value / 1000)}k`;
  if (value >= 1) return formatTrimmed(value);
  return formatTrimmed(value, 2);
}

function formatTrimmed(value, digits = 1) {
  return Number(value).toFixed(digits).replace(/\.?0+$/, "");
}

function formatWeight(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "0";
  return number.toFixed(2).replace(/\.?0+$/, "");
}

function formatDateTime(value) {
  if (!value) return tr("unknownTime");
  return new Intl.DateTimeFormat(state.language, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function computeTopChartLimit(width) {
  if (!Number.isFinite(width) || width <= 0) return 20;
  if (width >= 1180) return 30;
  if (width >= 980) return 24;
  if (width >= 720) return 20;
  if (width >= 520) return 16;
  return 12;
}

function modelCost(model) {
  const pricingCost = model.pricing?.aaIndexCostUsd;
  return Number.isFinite(pricingCost) ? pricingCost : model.aaCostUsd;
}

function bestValueModel(models) {
  const costModels = models.filter((model) => Number.isFinite(modelCost(model)) && modelCost(model) > 0);
  if (costModels.length === 0) return null;
  const scoreThreshold = median(costModels.map((model) => model.score));
  const costThreshold = median(costModels.map(modelCost));
  const candidates = costModels.filter((model) => model.score >= scoreThreshold && modelCost(model) <= costThreshold);
  return (candidates.length ? candidates : costModels)
    .sort((a, b) => b.score - a.score || modelCost(a) - modelCost(b))[0];
}

function median(values) {
  const sorted = values.filter(Number.isFinite).sort((a, b) => a - b);
  if (sorted.length === 0) return 0;
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
}

function linearTicks(min, max, count) {
  if (max <= min) return [min];
  const step = (max - min) / Math.max(count - 1, 1);
  return Array.from({ length: count }, (_, index) => min + step * index);
}

function logTicks(min, max) {
  const bases = [1, 2, 3, 5, 7];
  const ticks = [];
  const minPower = Math.floor(Math.log10(Math.max(min, 0.01)));
  const maxPower = Math.ceil(Math.log10(Math.max(max, 0.02)));
  for (let power = minPower; power <= maxPower; power += 1) {
    for (const base of bases) {
      const value = base * 10 ** power;
      if (value >= min && value <= max) ticks.push(value);
    }
  }
  return ticks.slice(0, 12);
}

function providerColor(model, index = 0) {
  return providerColors[model.creator] || fallbackColors[index % fallbackColors.length];
}

function scatterLabelModels(models, costThreshold, scoreThreshold) {
  const byScore = models.slice(0, 5);
  const attractive = models
    .filter((model) => model.score >= scoreThreshold && modelCost(model) <= costThreshold)
    .sort((a, b) => b.score - a.score || modelCost(a) - modelCost(b))
    .slice(0, 2);
  return [...new Map([...byScore, ...attractive].map((model) => [model.modelKey, model])).values()].slice(0, 7);
}

function scatterLabelPlacement(x, y, index, margin, plotWidth, plotHeight) {
  const anchor = x > margin.left + plotWidth * 0.58 ? "end" : "start";
  const labelX = anchor === "end" ? x - 12 : x + 12;
  const offset = [-10, 8, 24, -28, 38, -38, -16, 46][index % 8];
  return {
    anchor,
    x: labelX,
    y: clamp(y + 4 + offset, margin.top + 14, margin.top + plotHeight - 8),
  };
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
