---
name: AInsights IRT Leaderboard Exploration
description: Executive Chinese report for comparing coverage-aware, product-constrained ranking schemes.
colors:
  canvas: "#ffffff"
  surface: "#ffffff"
  ink: "#171411"
  muted: "#625f5a"
  accent: "#2563eb"
  positive: "#0f7b45"
  warning: "#b45309"
typography:
  family: "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
  title: "24px/30px semibold"
  section: "20px/26px medium"
  body: "14px/20px regular"
spacing:
  page: "32px"
  section: "24px"
  card: "16px"
rounded:
  card: "16px"
  badge: "999px"
surfaces:
  report: "single-column narrative with bounded evidence cards"
  table: "full-width, horizontally scrollable on narrow screens"
components:
  title: "visible H1 matching the manifest title"
  executive-summary: "first section immediately below title"
  summary: "answer-first executive summary before any evidence table or chart"
  charts: "native grouped or single-series bars with explicit axes"
  tables: "native tables with explicit default rank sort"
---

# Report design contract

The report is optimized for product stakeholders who need a decision, not a modeling tutorial. It follows an answer-first reading order: executive summary, source-conflict fix, measurement-versus-policy separation, constrained method comparison, product-anchor checks, coverage risk, Flash sensitivity, external-source decision, recommendation, caveats, then five complete Top 50 appendices.

Quantitative visuals use only native report charts and tables. Each chart is introduced by a narrative block that states the question and followed by a narrative block that explains the implication. All Top 50 tables use the same compact column set, preserve the original measurement rank and hard-constraint shift, and visibly label Main versus Provisional evidence.

The visual hierarchy is intentionally restrained: white canvas, neutral text, blue accent, no decorative graphics, and no interactive dashboard filters. The portable runtime owns responsive layout, dark mode, source affordances, and print behavior.
