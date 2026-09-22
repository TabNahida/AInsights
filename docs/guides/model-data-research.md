# Model data research playbook for AI agents

Use this playbook to investigate new releases, repair coverage gaps, and ship verified AInsights data updates. A successful scraper run is evidence of execution, not evidence that the model catalogue is complete. When the user asks to fill missing model data, finding sources or writing a gap report is an intermediate step: implement the supported observations, rebuild the site, and verify the affected model pages before reporting completion.

## Start from the current repository

1. Read repository instructions and inspect `git status --short --branch`, the current branch, and its upstream.
2. Work directly on `main`, as required by this repository. Fetch remote changes and inspect the difference from `origin/main`; preserve local work and fast-forward where possible. Do not create branches/worktrees or reset changes. If the task starts on a legacy branch, preserve its work and follow the user's instructions for merging and retiring it.
3. Record the inspected commit, `docs/data/models.json.generatedAt`, AA snapshot state, benchmark source dates, and pricing source dates separately. A site rebuild does not refresh its inputs.
4. Define the investigation: named releases, related variants, regions, evidence categories, and cutoff date. Start useful research immediately; do not turn ordinary public-source reads into an approval sequence.

The [September 22 worked audit](../../analysis/model-and-token-plan-audit-2026-09-22.md) shows why this matters: pulling `main` changed the finding from “missing releases” to “present releases with incomplete evidence.”

## Map the data paths before editing

| Evidence | Maintained input / transformation | Published output |
| --- | --- | --- |
| AA catalogue, scores, speed, API price snapshot | `ArtificialAnalysis/scrape_artificial_analysis.py` → `ArtificialAnalysis/artificialanalysis_raw_scores_wide.csv` | Model metadata, AA observations and base prices |
| Official model-card discovery | `benchmarks/discover_official_model_cards.py` → `data/benchmarks/official_model_cards.json` | Candidates consumed by the benchmark collector |
| Official release-page discovery | `benchmarks/discover_official_vendor_pages.py` → `data/benchmarks/official_vendor_pages.json` | Candidates consumed by the benchmark collector |
| Curated benchmark semantics, aliases and source parsers | `benchmarks/collect_benchmark_scores.py` → `data/benchmarks/benchmark_scores.json` | External evidence and eligible score fields |
| Reviewed visual evidence | `data/benchmarks/vision_evidence.json`, `benchmarks/vision_evidence.py` | Exact-configuration or reference visual results |
| Provider plans and offers | `data/pricing/provider_pricing.json` and its ordered `supplements` | `providerPricing` in the site payload |
| Site assembly | `scripts/build_docs_site.py` | `docs/data/models.json`, `models.js`, generated HTML and ranking audits |

Do not fix a generated JSON/JS file alone. Find the maintained input and ensure the next refresh preserves the correction. Read current schemas and tests rather than assuming this table is a complete schema specification.

## Build a release and coverage ledger

Use one row per exact model/checkpoint/configuration. Capture:

- Official product name, vendor, API model ID, dated checkpoint or revision, repository ID, AA slug, release date and retirement date.
- Reasoning mode/effort, deployment variant, region and modalities. Pro, Flash, UltraSpeed, base, RL, distilled and quantized releases are separate identities until a source proves otherwise.
- Catalogue presence, official metadata, AA observations, official benchmark observations, visual evidence, provider offers, and Core eligibility as independent columns.
- Status for each gap: `not researched`, `source unavailable`, `not published in reviewed sources`, `published but not ingested`, `ambiguous configuration`, `withdrawn`, or `not applicable`.

Count observations, not every non-null alias. For example, `AA-LCR` and `AA-LCR v1.1` can represent the same imported observation. Missing data is `null`, not an observed score of zero.

## Find sources actively

For each named release, inspect all relevant evidence classes:

1. **Official release article and changelog:** establish identity, date, variant family and links to the report or model card.
2. **Official model card and technical report:** inspect benchmark tables, footnotes, evaluation appendices, inference configuration, licence and architecture. Follow official links to Hugging Face, ModelScope, GitHub or a paper; verify organization ownership.
3. **Official API catalogue and model-specific docs:** verify API IDs, supported effort settings, context, maximum output, modalities, availability and deprecations. A product announcement alone does not establish API access.
4. **Official pricing, plan support and billing docs:** verify which model is actually included. Hand off the detailed calculation to the [TokenPlan playbook](token-plan-pricing-research.md).
5. **Independent benchmark owner:** inspect AA and relevant benchmark leaderboards for the exact configuration. Separate the evaluator's own run from a vendor's reproduction or quotation.
6. **Secondary discovery:** search release name + `model card`, `technical report`, `benchmark`, `pricing`, and local-language equivalents. Use aggregators/social posts to find originals; do not promote their uncited numbers to official evidence.

For Xiaomi, start with `mimo.mi.com`, its linked `XiaomiMiMo` organization, and the release's linked reports. For Grok, start with `x.ai/news`, `docs.x.ai/developers/models`, and the model-specific page. Extend the vendor watchlist when a confirmed release falls outside it. Xiaomi is now included in model-card discovery; Grok 4.7 has a curated release parser. The release-index discovery still covers Qwen, GLM, Kimi and DeepSeek; none of these lists is a complete vendor universe.

Search the full technical report, not only the README. Read final evaluation tables, methodology footnotes and linked images; independently verify important transcriptions against the rendered page. In the MiMo V2.6 report, Table 3 on page 26 establishes final product results, whereas earlier plots describe intermediate RL checkpoints. Section 5.2 also discloses corrected CyberGym environments, requiring a separate benchmark identity. Record these findings in the production source notes, not just the research memo.

Batch independent reads, then follow only leads that resolve material gaps. Read the actual table and footnotes, not just search snippets. HTTP 200 can contain a login page, empty application shell, or old content. For an image-only table, inspect the image/PDF visually and record a transcription locator; never guess a score from chart height. Record failed access without erasing last-known data or claiming a fresh check.

## Record an evidence unit

Every extracted number needs enough context to reproduce the decision:

```json
{
  "modelIdentity": "vendor / checkpoint / effort / harness",
  "benchmarkLabelAsPublished": "Terminal-Bench 4.0",
  "benchmarkVersion": "4.0",
  "value": 38.0,
  "unit": "percent",
  "evaluationConfiguration": "xhigh; preserve the source protocol",
  "publisher": "SpaceXAI",
  "sourceUrl": "https://x.ai/news/grok-4-7",
  "sourceLocator": "Model Improvements table, Terminal-Bench row",
  "publishedAt": "2026-09-21",
  "accessedAt": "2026-09-22",
  "bindingDecision": "exact configuration; scoring eligibility reviewed separately"
}
```

This is a research record, not a drop-in production schema. Retain a short source excerpt, table locator, archived response/hash or pinned repository revision where practical. Distinguish publication time, effective time, access time and pipeline generation time. Do not update every source's date merely because a job ran.

## Resolve semantics before matching

- Preserve benchmark versions, splits, units, pass@k, tool availability, scaffolding, token budgets, retries and grading protocols. Terminal-Bench 2.1 and 4.0, CursorBench 3.2 and 4.0, and Toolathlon versus Toolathlon-Verified are not interchangeable.
- Read exceptions at row level. Grok 4.7's release table labels the column xhigh, but the DeepSWE v1.1 result has a `high effort` footnote. Do not broadcast that score to xhigh.
- Do not merge an Elo score with a percentage. Preserve raw Elo and identify any display transformation explicitly.
- Do not infer effort from the best result, or infer that an arbitrary open RL checkpoint is identical to a hosted API configuration. Follow the report through to its final product table and the release/API identity. An explicitly identified final release can be attached as its published model-card configuration without inventing a named effort. Preserve `configurationConfidence="model-card-default"` and scope it to that release; a missing effort parameter alone is not a reason to discard the entire final product table. When the identity truly remains ambiguous, retain reference-only evidence and state what would establish a binding.
- Do not import competitors' scores from a vendor comparison table as that competitor's primary evidence without reviewing their provenance.
- When two official pages disagree, investigate checkpoint, harness, timing and metric differences. Do not choose the larger number. Xiaomi's September release narrative and final model-card table contain different DeepSWE values; report section 5.4 and Table 3 resolve which values describe the final product. Use that table for release observations and document why the training-stage values were not selected.
- Broad aliases can attach yesterday's results to today's rolling endpoint. Prefer exact dated identities and include negative matching checks for adjacent releases.

## Keep coverage separate from ranking policy

The production ranking uses the fixed Mixed Core 07 registry documented in the README and analysis code. Researching a missing model does not authorize retuning weights or changing eligibility to improve its position.

A vendor-published Terminal-Bench result can be useful external evidence while AA's `Terminal-Bench v4.0` Core observation remains null. Do not fill the AA column with a different evaluator's run just because the benchmark name matches. Official-source ownership, exact configuration matching and ranking eligibility are three separate decisions.

Read `modelScoreEligible`, `evidenceEligible`, configuration metadata and the relevant parser tests before adding curated sources. For visual evidence, distinguish `modelSlugs` from `referenceSlugs`; reference results must not enter exact-configuration radar calculations. Unpublished evidence remains missing, with its reason documented.

## Prepare and validate the update

1. Add precise aliases, benchmark definitions, source specifications and observations to maintained inputs. If adding discovery coverage, also enforce ownership, derivative-model exclusions and preservation during outages.
2. For pricing, prefer a scoped supplement with source IDs and one offer per model. Confirm merge ordering: later supplements may override earlier rows.
3. Add regression coverage where semantics or parsing changed. Include a positive match and a nearby model/effort/version that must not match. A new reference-only result must not unexpectedly change Core scores.
4. Run relevant commands, selecting the scope actually changed:

```powershell
python ArtificialAnalysis/scrape_artificial_analysis.py --output-dir ArtificialAnalysis
python benchmarks/discover_official_model_cards.py --output-json data/benchmarks/official_model_cards.json
python benchmarks/discover_official_vendor_pages.py --output-json data/benchmarks/official_vendor_pages.json
python benchmarks/collect_benchmark_scores.py --output-json data/benchmarks/benchmark_scores.json
python benchmarks/validate_official_sources.py
python scripts/build_docs_site.py
python -B analysis/irt_leaderboard_exploration/validate_mixed_core_production.py --input docs/data/models.json
python -B -m unittest discover -s tests
```

`--seed-only` is a fixture/debug mode; do not use it to replace a richer production snapshot. `--allow-stale` can preserve availability during outages; a successful run using old data is not a fresh import.

5. Inspect the generated target models: source links, exact/reference binding, null handling, pricing offers and eligibility. If a displayed surface changed, inspect it in the browser. Review `git diff --check` and the generated diff for unexpected removals, duplicates or unrelated changes.

Refresh a bounded set of source slices when investigating a few releases; preserve unrelated source rows and their dates/statuses. Compare the parser's live rows with reviewed source values before writing. Do not replace the entire benchmark catalogue with a seed-only payload. Ensure later scheduled runs know the same source specifications and preserve the corrections.

For documentation-only research, recompute the audit and examples without rebuilding the entire site. State that production data was not changed.

## Definition of done and handoff

Report the inspected commit and dates; actual before/after observation counts per configuration; what was added; which scores/ranks changed; what remains unverifiable; and which checks ran. Link maintained inputs and sources. Do not claim success merely because the models already existed or a document lists their missing values. Do not stop with known, well-supported observations still unimplemented. A missing value may remain missing if its source is unavailable or its semantics cannot be established; explain the specific reason. If more external observations leave AIndex unchanged because AA Core remains incomplete or the new tests are outside the fixed scoring registry, report that explicitly rather than promising a score increase.

For future refreshes, combine automation with a research pass triggered by a new release, a user report, unknown aliases, new benchmark labels, material price changes, or stale source dates. Track a queue of unresolved evidence with the next useful source to inspect. Do not claim “all models updated” based on a green daily workflow or a fixed list of vendors.

### Reusable agent task

> Read `docs/guides/model-data-research.md`. Synchronize and record the repository baseline. Investigate [release names] as of [date] using official releases, API docs, model cards, technical reports and independent evaluators. Build a per-configuration coverage ledger. Preserve benchmark versions, footnotes and source dates; retain ambiguous results as references. Update maintained inputs only for supported claims, rebuild affected outputs, run relevant checks, and report remaining gaps with sources. Do not infer completeness from successful automation or replace missing AA Core observations with vendor measurements.
