# AInsights

Compare AI models across intelligence, coding, agentic behavior, speed, cost, and raw benchmark quality.

The default leaderboard uses AIndex Scheme 18. Each of five equally weighted capability boards starts from the geometric mean of a small, complete mandatory Core. Independently controlled extension benchmarks may then add only evidence above an anonymous cohort-wide OLS expectation. Positive residuals are accumulated with a zero-neutral monotone log-sum-exp bonus and capped by the current cohort's pooled positive-residual `mean + sqrt(2) * SD`. A board is `min(100, core + capped_bonus)`, and AIndex is the arithmetic mean of the five board scores.

Missing extension results stay absent: they are never filled with 0 or a neutral value and never reduce the Core score. Benchmarks controlled by a ranked model vendor are excluded from the extension pool. The displayed 0–100 points are direct calculated scores, not a percentile, canonical T score, mean rank, or model-specific correction. Equal-board 2PL and Dense Rasch remain available only as sensitivity comparisons.

## Update data

```powershell
python -m pip install -r requirements.txt
python ArtificialAnalysis\scrape_artificial_analysis.py --output-dir ArtificialAnalysis
python benchmarks\collect_benchmark_scores.py --output-json data\benchmarks\benchmark_scores.json
python scripts\build_docs_site.py
python -B analysis\irt_leaderboard_exploration\validate_scheme18_production.py --input docs\data\models.json
```

The static ranking site lives in `docs/` and reads `docs/data/models.json`. The detailed calculation is documented in `docs/methodology.html`; reproducible analysis outputs live in `analysis/irt_leaderboard_exploration/outputs/`.
