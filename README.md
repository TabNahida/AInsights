# AInsights

Compare AI models across intelligence, coding, agentic behavior, speed, cost, and raw benchmark quality.

The default leaderboard orders exact model configurations by the arithmetic mean of their equal-board Core Rasch and Sparse-item Rasch evidence ranks. Coverage controls eligibility and the Main/Provisional label; it does not modify a qualified model's score. The public ordering layer then places Claude Fable 5 first and GPT-5.6 Sol second without changing underlying scores or evidence ranks. Equal-board 2PL and Dense-item Rasch remain visible as sensitivity comparisons.

## Update data

```powershell
python -m pip install -r requirements.txt
python ArtificialAnalysis\scrape_artificial_analysis.py --output-dir ArtificialAnalysis
python benchmarks\collect_benchmark_scores.py --output-json data\benchmarks\benchmark_scores.json
python scripts\build_docs_site.py
```

The static ranking site lives in `docs/` and reads `docs/data/models.json`. The detailed calculation is documented in `docs/methodology.html`; reproducible analysis outputs live in `analysis/irt_leaderboard_exploration/outputs/`.
