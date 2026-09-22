# AInsights

Compare AI models across intelligence, coding, agentic behavior, speed, cost, and raw benchmark quality.

The default leaderboard uses **AIndex Mixed Core 07**. Coding, agentic/tool work, hard reasoning, knowledge/science, and instruction/context use weights **12%, 9%, 22%, 37%, 20%** respectively.

| Board | Core | Weight |
| --- | --- | ---: |
| Coding | Terminal-Bench v4.0 + SciCode | 12% |
| Agentic/tool work | AutomationBench-AA + τ³-Banking | 9% |
| Hard reasoning | CritPt | 22% |
| Knowledge/science | AA-Omniscience Accuracy + GDP.pdf | 37% |
| Instruction/context | AA-LCR v1.1 | 20% |

A single Core item supplies its board's whole base; two items each supply half. Missing Core observations keep their fixed share with zero contribution; observed zero is valid. A configuration is excluded if any board has no observed Core or at least four configured Core items are missing. Representatives are chosen by descending inference priority and then slug **before** eligibility; evidence is never borrowed across configurations. Terminal v4 is the only scoring version. AIME, LiveCodeBench, GPQA and old short-math tests are excluded from Core.

The existing extension calculation remains: globally remove Core families and legacy Terminal, fit nonnegative-slope OLS only on complete-Core boards in the eligible representative cohort, retain positive residuals, aggregate `log(1 + sum(expm1(residual)))`, and cap with pooled positive-residual `mean + sqrt(2) * population_SD`. Incomplete-Core boards earn no extension bonus. Each board is `min(100, core + capped_bonus)`; AIndex is the sum of board score times its fixed weight. Exact configurations reuse the representative cohort's calibration.

The displayed 0–100 points are direct scores. Named-model ordering preferences were used only to choose a historical experimental scheme; they never gate daily publication or retune weights. Legacy Scheme 18, equal-board 2PL and Rasch outputs remain historical/sensitivity audits.

## Update data

For an agent-led research pass, use the English
[model data research playbook](docs/guides/model-data-research.md) and
[TokenPlan pricing research playbook](docs/guides/token-plan-pricing-research.md).
The [September 22 worked audit](analysis/model-and-token-plan-audit-2026-09-22.md)
checks MiMo V2.6 / Grok 4.7 coverage and calculates Xiaomi, Baidu, and Alibaba
plan examples from current official terms. Its reviewed inputs and offline
calculator distinguish full-quota normalization from actual workload cost.

```powershell
python -m pip install -r requirements.txt
python ArtificialAnalysis\scrape_artificial_analysis.py --output-dir ArtificialAnalysis
python benchmarks\discover_official_model_cards.py --output-json data\benchmarks\official_model_cards.json
python benchmarks\discover_official_vendor_pages.py --output-json data\benchmarks\official_vendor_pages.json
python benchmarks\collect_benchmark_scores.py --output-json data\benchmarks\benchmark_scores.json
python benchmarks\validate_official_sources.py
python scripts\build_docs_site.py
python -B analysis\irt_leaderboard_exploration\validate_mixed_core_production.py --input docs\data\models.json
```

The daily workflow refreshes Artificial Analysis and rebuilds the site; a separate
Monday workflow discovers and refreshes external benchmark sources. Discovery watches the verified
`Qwen`, `zai-org`, `moonshotai`, `deepseek-ai`, and `XiaomiMiMo` Hugging Face organizations as
well as pinned Qwen, Z.ai, Kimi, and DeepSeek first-party release indexes. It
preserves previously discovered cards and pages during transient outages and
feeds new candidates into the benchmark collector. Curated source specifications
remain authoritative for versioned or multi-value benchmark semantics.

The AA import covers the [Intelligence Index v4.3 suite](https://artificialanalysis.ai/methodology/intelligence-benchmarking),
including AA-Briefcase, AutomationBench-AA, Terminal-Bench v4.0, GDP.pdf, and an
explicit AA-LCR v1.1 column. AA-Briefcase and GDPval-AA v2 use the bounded
`100 * clamp((Elo - 500) / 2000, 0, 1)` scale; these are Elo-derived points,
not task pass percentages. The import uses the published current Elo/normalized
fields, not the frozen-at-entry Elo values used internally by AA's composite.
AutomationBench-AA uses objective completion with guardrail failures, GDP.pdf
uses all-pass (not mean criterion pass rate), and the other new task scores are
converted from fractions to percentages. Current unversioned `gdpval` manifest
fields update **GDPval-AA v2**; the legacy GDPval-AA column is retained only as
historical data. AA-LCR remains a compatibility alias for the current `lcr`
field (v1.1), while Terminal-Bench v2.1 and v4.0 remain separate observations.
SciCode's upstream v1.0.1 regrading continues through the existing `scicode` field.
The exact pre-v4.3 CSV schema is accepted for migration without disabling row
or score coverage validation. Adding these data columns makes them available
to the site. The production Core registry is the fixed Mixed Core 07 table above.

The AA scraper validates row and score coverage before atomically replacing the
snapshot. A large SciCode withdrawal is accepted only when the models page and
the dedicated SciCode evaluation page agree on the complete model catalogue and
every score/null. Confirmed withdrawn scores and ranks stay blank. Models missing
enough Core observations to fail the above eligibility rules remain in the
catalogue but are excluded from scoring, with missing items recorded in the validation summary. Other unexpected coverage losses still fail validation. The daily workflow's
`--allow-stale` option can retain a validated snapshot during upstream outages;
check its warning annotations before treating a green run as a fresh import.

September 2026 sources include GPT-6 Astra, Claude Fable 5.1, Gemini 3.8 Flash,
Qwen3.8-Flash-Next, GLM-5.3-Flash, and DeepSeek V4 Flash Vision. Official results
reported as best across unspecified effort settings remain reference evidence;
they are not assigned to a particular reasoning configuration. Versioned
Terminal-Bench, OSWorld, HLE-Verified, and CursorBench results remain distinct.

The September 18 refresh adds official cards for K2 Horizon 0.9B, 3.7B, 7B,
MoVA 36B A4B, and Ling-3.0-flash-Fin, including 42 reference results and
official license/context metadata. K2 tables are refreshed automatically;
Ling's image-only chart is manually transcribed with its URL and evaluation
protocols recorded in the source note. Unspecified effort settings remain
reference-only, and versioned LiveCodeBench and SpreadsheetBench rows stay
separate. Qwen3.8-Max's August release scores bind to the dated `0803` identity;
AA's rolling `qwen3-8-max` slug now identifies the September `0902` checkpoint.
Daily regression checks validate observed coverage and evidence tiers rather
than requiring named models to retain historical benchmark counts.

The September 22 refresh adds 17 official MiMo V2.6 Pro observations, a Flash
catalogue entry with 16 observations, and eight Grok 4.7 observations (seven
xhigh and the explicitly footnoted high-effort DeepSWE result). Final MiMo
report tables take precedence over intermediate training curves. Corrected
CyberGym, internal tasks, benchmark versions and Elo units remain distinct.
An initial import missed renamed AA fields. The corrected scraper supports
`terminalBench40`, `terminalBench21`, and flat Omniscience accuracy/hallucination
fields as well as the previous schemas. Live catalogue/evaluation manifests
agree on the recovered observations. Pro and both Grok configurations now lack
only τ³-Banking; AIndex is recalculated from AA's own scores. Model detail groups
use the production scoring role, so GDP.pdf and AA Terminal-Bench are correctly
shown as Core regardless of Custom template weights.

The static ranking site lives in `docs/` and reads `docs/data/models.json`. The detailed calculation is documented in `docs/methodology.html`; reproducible analysis outputs live in `analysis/irt_leaderboard_exploration/outputs/`.
