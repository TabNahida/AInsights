const state = {
  data: null,
  presetId: null,
  dedupe: true,
  query: "",
  customWeights: {},
};

const els = {
  updatedAt: document.querySelector("#updatedAt"),
  presetButtons: document.querySelector("#presetButtons"),
  searchInput: document.querySelector("#searchInput"),
  dedupeToggle: document.querySelector("#dedupeToggle"),
  summaryRow: document.querySelector("#summaryRow"),
  customPanel: document.querySelector("#customPanel"),
  weightsGrid: document.querySelector("#weightsGrid"),
  rankingBody: document.querySelector("#rankingBody"),
  resetWeightsButton: document.querySelector("#resetWeightsButton"),
  metricTemplate: document.querySelector("#metricTemplate"),
};

const presetOrder = ["zhihu-adjusted", "aa-intelligence", "aa-coding", "aa-agentic", "custom"];

init();

async function init() {
  try {
    state.data = window.AINSIGHTS_MODELS_DATA || (await fetchJsonData());
    state.presetId = state.data.defaultPreset;
    state.dedupe = Boolean(state.data.defaultDedupe);
    state.customWeights = Object.fromEntries(state.data.metrics.map((metric) => [metric.key, metric.defaultWeight]));
    els.dedupeToggle.checked = state.dedupe;
    renderStaticControls();
    render();
  } catch (error) {
    els.rankingBody.innerHTML = `<tr><td class="empty" colspan="7">数据加载失败：${escapeHtml(error.message)}</td></tr>`;
  }
}

async function fetchJsonData() {
  const response = await fetch("./data/models.json", { cache: "no-store" });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

function renderStaticControls() {
  els.updatedAt.textContent = `更新于 ${formatDateTime(state.data.generatedAt)}`;
  els.presetButtons.innerHTML = "";
  for (const id of presetOrder) {
    const preset = state.data.presets[id];
    const button = document.createElement("button");
    button.type = "button";
    button.role = "tab";
    button.dataset.preset = id;
    button.textContent = preset.label;
    button.addEventListener("click", () => {
      state.presetId = id;
      render();
    });
    els.presetButtons.append(button);
  }

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

function render() {
  const preset = state.data.presets[state.presetId];
  document.querySelectorAll("#presetButtons button").forEach((button) => {
    button.setAttribute("aria-selected", String(button.dataset.preset === state.presetId));
  });
  els.customPanel.hidden = state.presetId !== "custom";
  if (!els.customPanel.hidden) renderWeights();

  renderResults(preset);
}

function renderResults(preset) {
  const scored = scoreModels(preset);
  const searched = scored.filter(matchesQuery);
  const visible = state.dedupe ? dedupeByBestVariant(searched) : searched;
  const ranked = rankRows(visible);

  renderSummary(searched.length, visible.length, scored.length, preset);
  renderTable(ranked.slice(0, 250));
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

function renderSummary(searchedCount, visibleCount, scoredCount, preset) {
  const removed = searchedCount - visibleCount;
  els.summaryRow.innerHTML = `
    <span><strong>${visibleCount}</strong> 个排名项</span>
    <span><strong>${scoredCount}</strong> 个可评分模型</span>
    <span>${state.dedupe ? `已去除 <strong>${removed}</strong> 个重复档位` : "显示全部档位"}</span>
    <span>${escapeHtml(preset.description)}</span>
    <a href="${state.data.source.defaultCorrectionReference}" target="_blank" rel="noreferrer">默认修正参考</a>
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
    output.value = input.value;
    input.addEventListener("input", (event) => {
      state.customWeights[metric.key] = Number(event.target.value);
      output.value = event.target.value;
      renderResults(state.data.presets.custom);
    });
    els.weightsGrid.append(fragment);
  }
}

function renderTable(models) {
  if (models.length === 0) {
    els.rankingBody.innerHTML = '<tr><td class="empty" colspan="7">没有符合条件的模型</td></tr>';
    return;
  }
  els.rankingBody.innerHTML = models.map(renderRow).join("");
}

function renderRow(model) {
  const scoreWidth = clamp(model.score, 0, 100);
  const reason = model.isReasoning ? '<span class="pill">Reasoning</span>' : "";
  const source = model.openSourceCategorization ? `<span class="pill">${escapeHtml(model.openSourceCategorization)}</span>` : "";
  return `
    <tr>
      <td class="rank-col">${model.rank}</td>
      <td>
        <div class="model-main">
          <a class="model-name" href="https://artificialanalysis.ai${escapeHtml(model.modelUrl)}" target="_blank" rel="noreferrer">${escapeHtml(model.model)}</a>
          <div class="model-meta">
            <span>${escapeHtml(model.creator || "Unknown")}</span>
            ${reason}
            ${source}
          </div>
        </div>
      </td>
      <td class="score-cell">
        <div class="score-value"><span>${formatNumber(model.score)}</span><span class="muted">${escapeHtml(model.scoreMeta || "")}</span></div>
        <div class="score-bar" style="--value: ${scoreWidth}%"><span></span></div>
      </td>
      <td>${formatNumber(model.aa["aa-intelligence"])}</td>
      <td>${formatNumber(model.aa["aa-coding"])}</td>
      <td>${formatNumber(model.aa["aa-agentic"])}</td>
      <td>${escapeHtml(model.coverageLabel || model.coverage)}</td>
    </tr>
  `;
}

function formatNumber(value) {
  return Number.isFinite(value) ? value.toFixed(1) : "—";
}

function formatDateTime(value) {
  if (!value) return "未知时间";
  return new Intl.DateTimeFormat("zh-CN", {
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
