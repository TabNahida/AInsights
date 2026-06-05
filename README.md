# AInsights

Compare AI models across intelligence, coding, agentic behavior, speed, cost, and raw benchmark quality.

## Update data

```powershell
python ArtificialAnalysis\scrape_artificial_analysis.py --output-dir ArtificialAnalysis
python ArtificialAnalysis\build_docs_site.py
```

The static ranking site lives in `docs/` and reads `docs/data/models.json`.
