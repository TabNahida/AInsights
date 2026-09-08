# AInsights

Compare AI models across intelligence, coding, agentic behavior, speed, cost, and raw benchmark quality.

The default leaderboard uses AIndex Scheme 18. Each of five equally weighted capability boards starts from the geometric mean of a small, complete mandatory Core. Independently controlled extension benchmarks may then add only evidence above an anonymous cohort-wide OLS expectation. Positive residuals are accumulated with a zero-neutral monotone log-sum-exp bonus and capped by the current cohort's pooled positive-residual `mean + sqrt(2) * SD`. A board is `min(100, core + capped_bonus)`, and AIndex is the arithmetic mean of the five board scores.

Missing extension results stay absent: they are never filled with 0 or a neutral value and never reduce the Core score. Benchmarks controlled by a ranked model vendor are excluded from the extension pool. The displayed 0–100 points are direct calculated scores, not a percentile, canonical T score, mean rank, or model-specific correction. Equal-board 2PL and Dense Rasch remain available only as sensitivity comparisons.

## Update data

```powershell
python -m pip install -r requirements.txt
python ArtificialAnalysis\scrape_artificial_analysis.py --output-dir ArtificialAnalysis
python benchmarks\discover_official_model_cards.py --output-json data\benchmarks\official_model_cards.json
python benchmarks\discover_official_vendor_pages.py --output-json data\benchmarks\official_vendor_pages.json
python benchmarks\collect_benchmark_scores.py --output-json data\benchmarks\benchmark_scores.json
python benchmarks\validate_official_sources.py
python scripts\build_docs_site.py
python -B analysis\irt_leaderboard_exploration\validate_scheme18_production.py --input docs\data\models.json
```

The daily workflow refreshes Artificial Analysis and rebuilds the site; a separate
Monday workflow discovers and refreshes external benchmark sources. Discovery watches the verified
`Qwen`, `zai-org`, `moonshotai`, and `deepseek-ai` Hugging Face organizations as
well as pinned Qwen, Z.ai, Kimi, and DeepSeek first-party release indexes. It
preserves previously discovered cards and pages during transient outages and
feeds new candidates into the benchmark collector. Curated source specifications
remain authoritative for versioned or multi-value benchmark semantics.

The AA scraper validates row and score coverage before atomically replacing the
snapshot. A large SciCode withdrawal is accepted only when the models page and
the dedicated SciCode evaluation page agree on the complete model catalogue and
every score/null. Confirmed withdrawn scores and ranks stay blank. Models missing
a required Core observation remain in the catalogue but are excluded from
Scheme 18 calibration and ranking, with missing items recorded in its validation
summary. Other unexpected coverage losses still fail validation. The daily workflow's
`--allow-stale` option can retain a validated snapshot during upstream outages;
check its warning annotations before treating a green run as a fresh import.

September 2026 sources include GPT-6 Astra, Claude Fable 5.1, Gemini 3.8 Flash,
Qwen3.8-Flash-Next, GLM-5.3-Flash, and DeepSeek V4 Flash Vision. Official results
reported as best across unspecified effort settings remain reference evidence;
they are not assigned to a particular reasoning configuration. Versioned
Terminal-Bench, OSWorld, HLE-Verified, and CursorBench results remain distinct.

The static ranking site lives in `docs/` and reads `docs/data/models.json`. The detailed calculation is documented in `docs/methodology.html`; reproducible analysis outputs live in `analysis/irt_leaderboard_exploration/outputs/`.
