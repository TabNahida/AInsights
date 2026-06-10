function getInitialLanguage() {
  try {
    const stored = localStorage.getItem(LANGUAGE_STORAGE_KEY);
    if (copy[stored]) return stored;
  } catch {
    // Ignore storage errors in privacy-restricted contexts.
  }
  return navigator.language && navigator.language.toLowerCase().startsWith("zh") ? "zh-CN" : DEFAULT_LANGUAGE;
}

function getInitialRoute() {
  const pageHint = document.body?.dataset.page || "";
  const params = new URLSearchParams(location.search);
  const filename = location.pathname.split("/").pop() || "index.html";
  const hash = location.hash.replace(/^#/, "");
  if (hash.startsWith("model/")) {
    return { page: "model", modelId: decodeRoutePart(hash.slice("model/".length)), benchmarkId: null, providerId: null };
  }
  if (hash.startsWith("provider/")) {
    return { page: "provider", modelId: null, benchmarkId: null, providerId: decodeRoutePart(hash.slice("provider/".length)) };
  }
  if (pageHint === "model" || filename === "model.html") {
    return { page: "model", modelId: params.get("id") || null, benchmarkId: null, providerId: null };
  }
  if (pageHint === "ranking" || filename === "full-rank.html") {
    return { page: "ranking", modelId: null, benchmarkId: null, providerId: null };
  }
  if (pageHint === "benchmark" || filename === "benchmark.html") {
    return { page: "benchmarks", modelId: null, benchmarkId: params.get("id") || null, providerId: null };
  }
  if (pageHint === "sources" || filename === "sources.html") {
    return { page: "sources", modelId: null, benchmarkId: null, providerId: null };
  }
  if (pageHint === "contribute" || filename === "contribute.html") {
    return { page: "contribute", modelId: null, benchmarkId: null, providerId: null };
  }
  if (pageHint === "provider" || filename === "provider.html") {
    return { page: "provider", modelId: null, benchmarkId: null, providerId: params.get("id") || null };
  }
  if (pageHint === "compare" || filename === "compare.html") {
    return { page: "compare", modelId: null, benchmarkId: null, providerId: null, compareIds: compareIdsFromParams(params) };
  }
  return { page: hash === "ranking" ? "ranking" : "home", modelId: null, benchmarkId: null, providerId: null };
}

function pageHref(page) {
  if (page === "ranking") return "full-rank.html";
  if (page === "benchmarks") return "benchmark.html";
  if (page === "sources") return "sources.html";
  if (page === "contribute") return "contribute.html";
  if (page === "model") return "model.html";
  if (page === "provider") return "provider.html";
  if (page === "compare") return "compare.html";
  return "index.html";
}

function compareIdsFromParams(params) {
  return String(params.get("models") || "")
    .split(",")
    .map((value) => decodeRoutePart(value).trim())
    .filter(Boolean);
}

function decodeRoutePart(value) {
  try {
    return decodeURIComponent(value);
  } catch {
    return value;
  }
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
  const text = Number(value).toFixed(digits);
  return text.includes(".") ? text.replace(/\.?0+$/, "") : text;
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

function formatDate(value) {
  if (!value) return tr("notAvailable");
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return new Intl.DateTimeFormat(state.language, {
    dateStyle: "medium",
  }).format(date);
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

function scatterLabelText(label) {
  const value = String(label || "");
  return value.length > 34 ? `${value.slice(0, 31)}...` : value;
}

function scatterLabelPlacements(points, margin, plotWidth, plotHeight, width) {
  const splitX = margin.left + plotWidth * 0.52;
  const sides = {
    left: [],
    right: [],
  };
  for (const point of points) {
    sides[point.x >= splitX ? "right" : "left"].push(point);
  }

  const placements = new Map();
  layoutScatterLabelSide(sides.left, "left", placements, margin, plotWidth, plotHeight, width);
  layoutScatterLabelSide(sides.right, "right", placements, margin, plotWidth, plotHeight, width);
  return placements;
}

function layoutScatterLabelSide(points, side, placements, margin, plotWidth, plotHeight, width) {
  if (points.length === 0) return;
  const minY = margin.top + 14;
  const maxY = margin.top + plotHeight - 10;
  const gap = 17;
  const sorted = [...points].sort((a, b) => a.y - b.y || b.model.score - a.model.score);
  const labelYs = sorted.map((point) => clamp(point.y, minY, maxY));

  for (let index = 1; index < labelYs.length; index += 1) {
    labelYs[index] = Math.max(labelYs[index], labelYs[index - 1] + gap);
  }
  const overflow = labelYs[labelYs.length - 1] - maxY;
  if (overflow > 0) {
    for (let index = 0; index < labelYs.length; index += 1) labelYs[index] -= overflow;
  }
  for (let index = labelYs.length - 2; index >= 0; index -= 1) {
    labelYs[index] = Math.min(labelYs[index], labelYs[index + 1] - gap);
  }

  const plotRight = margin.left + plotWidth;
  for (let index = 0; index < sorted.length; index += 1) {
    const point = sorted[index];
    const labelY = clamp(labelYs[index], minY, maxY);
    const labelX = side === "right" ? plotRight + 34 : margin.left - 34;
    const anchor = side === "right" ? "start" : "end";
    const elbowX = side === "right" ? plotRight + 12 : margin.left - 12;
    const endX = side === "right" ? labelX - 8 : labelX + 8;
    placements.set(point.model.modelKey, {
      anchor,
      x: clamp(labelX, 18, width - 18),
      y: labelY + 4,
      path: `M${point.x.toFixed(1)},${point.y.toFixed(1)} L${elbowX.toFixed(1)},${labelY.toFixed(1)} L${endX.toFixed(1)},${labelY.toFixed(1)}`,
    });
  }
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
