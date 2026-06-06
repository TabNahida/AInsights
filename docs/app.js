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
    headers: {
      model: "模型",
      score: "综合分",
      source: "来源",
      coverage: "覆盖",
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
    headers: {
      model: "Model",
      score: "Score",
      source: "Source",
      coverage: "Coverage",
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
  viewMode: "histogram",
  sourceFilter: "all",
};

const els = {
  updatedAt: document.querySelector("#updatedAt"),
  sourceLink: document.querySelector("#sourceLink"),
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
  histogramList: document.querySelector("#histogramList"),
  tableRanking: document.querySelector("#tableRanking"),
  rankingBody: document.querySelector("#rankingBody"),
  textRanking: document.querySelector("#textRanking"),
  resetWeightsButton: document.querySelector("#resetWeightsButton"),
  modelHeader: document.querySelector("#modelHeader"),
  scoreHeader: document.querySelector("#scoreHeader"),
  sourceHeader: document.querySelector("#sourceHeader"),
  coverageHeader: document.querySelector("#coverageHeader"),
  siteFooter: document.querySelector("#siteFooter"),
  metricTemplate: document.querySelector("#metricTemplate"),
};

const presetOrder = ["zhihu-adjusted", "aa-intelligence", "aa-coding", "aa-agentic", "custom"];
const viewOrder = ["histogram", "table", "text"];
const sourceFilterOrder = ["all", "open", "closed", "unknown"];

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
  els.modelHeader.textContent = tr("headers.model");
  els.scoreHeader.textContent = tr("headers.score");
  els.sourceHeader.textContent = tr("headers.source");
  els.coverageHeader.textContent = tr("headers.coverage");
  els.languageButtons.setAttribute("aria-label", tr("languageLabel"));
  els.siteFooter.innerHTML = `${escapeHtml(tr("footerPrefix"))}<a href="${escapeHtml(state.data.source.url)}" target="_blank" rel="noreferrer">Artificial Analysis</a>${escapeHtml(tr("footerSuffix"))}`;

  renderLanguageButtons();
  renderPresetButtons();
  renderViewButtons();
  renderSourceFilterButtons();
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
  const filtered = scored.filter(matchesQuery).filter(matchesSourceFilter);
  const visible = state.dedupe ? dedupeByBestVariant(filtered) : filtered;
  const ranked = rankRows(visible);
  const capped = ranked.slice(0, 250);

  renderSummary(filtered.length, visible.length, scored.length, preset);
  renderRankings(capped);
}

function scoreModels(preset) {
  return state.data.models
    .map((model) => {
      const result = scoreModel(model, preset);
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

function scoreModel(model, preset) {
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

  const weights = state.presetId === "custom" ? state.customWeights : preset.weights;
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
    els.rankingBody.innerHTML = `<tr><td class="empty" colspan="5">${escapeHtml(tr("empty"))}</td></tr>`;
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
      <td>${renderSourcePill(model)}</td>
      <td>${escapeHtml(model.coverageLabel || model.coverage)}</td>
    </tr>
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
    ? `<img src="${escapeHtml(src)}" alt="" loading="lazy" referrerpolicy="no-referrer" onerror="this.hidden=true;this.nextElementSibling.hidden=false" />`
    : "";
  return `<span class="provider-icon" role="img" aria-label="${escapeHtml(title)}">${image}<span class="icon-fallback" ${src ? "hidden" : ""}>${escapeHtml(label)}</span></span>`;
}

function renderSourcePill(model) {
  const type = sourceType(model);
  const detail = model.openSourceCategorization || sourceTypeLabel(type);
  return `<span class="pill source-pill" data-source-type="${escapeHtml(type)}" title="${escapeHtml(detail)}">${escapeHtml(sourceTypeLabel(type))}</span>`;
}

function renderLoadError(error) {
  const message = tr("loadFailed", { message: error.message });
  els.rankingBody.innerHTML = `<tr><td class="empty" colspan="5">${escapeHtml(message)}</td></tr>`;
  els.histogramList.innerHTML = `<div class="empty">${escapeHtml(message)}</div>`;
  els.textRanking.innerHTML = `<div class="empty">${escapeHtml(message)}</div>`;
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

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
