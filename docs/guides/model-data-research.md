# Model data: refresh first, then investigate gaps

Work on `main`; read `AGENTS.md` and preserve local changes. Run commands from the repository root. Install dependencies once with `python -m pip install -r requirements.txt`.

## 1. Use the existing tools

Refresh AA's model catalogue, benchmark scores, speed and base API prices:

```powershell
python ArtificialAnalysis/scrape_artificial_analysis.py --output-dir ArtificialAnalysis
```

Discover official cards/releases and collect their benchmark tables:

```powershell
python benchmarks/discover_official_model_cards.py --output-json data/benchmarks/official_model_cards.json
python benchmarks/discover_official_vendor_pages.py --output-json data/benchmarks/official_vendor_pages.json
python benchmarks/collect_benchmark_scores.py --output-json data/benchmarks/benchmark_scores.json
```

Discovery watches selected vendors; it is not a complete search of new releases. The daily job refreshes AA; the Monday job refreshes external sources. Neither refreshes every TokenPlan tariff. `--allow-stale` may retain old data; `--seed-only` is for fixtures, not production refreshes.

After changing data or parsers, validate and publish generated files:

```powershell
python benchmarks/validate_official_sources.py
python scripts/build_docs_site.py
python -B analysis/irt_leaderboard_exploration/validate_mixed_core_production.py --input docs/data/models.json
python -B -m unittest discover -s tests
```

The site reads `docs/data/models.json` / `models.js`. Fix maintained inputs and parsers, not generated files alone. Check affected model pages before committing and pushing when authorized.

## 2. Find what automation missed

1. **Identify the exact model:** vendor, API ID, checkpoint, effort, modalities and release date. Pro/Flash and high/xhigh are separate configurations.
2. **Check AA directly:** compare the live models manifest with the named evaluation page before calling a blank CSV cell unpublished. Inspect renamed fields, explicit nulls and zero. September's `terminalBench40` / `terminalBench21` and flat Omniscience fields were missed by the old parser. Update both normalization and explicit-column merge handling; test that old values cannot overwrite new observations.
3. **Search official sources:** release article → API docs → model card → full technical report and evaluation appendix. Check benchmark-owner leaderboards next; use aggregators to locate originals. For MiMo, follow `mimo.mi.com` and `XiaomiMiMo`; for Grok, use `x.ai/news` and `docs.x.ai`.
4. **Read table footnotes:** retain version, unit, tools/harness and effort. MiMo's final report Table 3 differs from intermediate training curves. Grok's 71% DeepSWE result is explicitly **high**, not xhigh. Never choose the larger value or copy a competitor column without checking provenance.
5. **Implement verified observations:** add precise source specs, aliases and benchmark definitions in `benchmarks/collect_benchmark_scores.py`; extend discovery when useful. Preserve unrelated source rows/statuses. Record URL, table/page, access date, value and configuration decision; hash or pin the source where practical.

## 3. Explain coverage and score separately

AA Core and vendor runs retain separate provenance. Do not substitute one for the other. Keep versions, raw Elo and percentages distinct; ambiguous configurations remain reference-only. Use production `aindexRole`, not Custom preset weights, to label scoring roles.

[Methodology](../methodology.html#extension-registry) lists the actual extension pool. A published test outside that pool adds no AIndex points. Even an allowed extension needs exact evidence, complete board Core and a positive residual. Missing data is not an observed zero; do not change weights to raise a named model.

Report before/after coverage and scores, remaining gaps and their evidence, and checks run. A source list alone does not complete a request to add data. See the [AA field correction](../../analysis/aa-field-recheck-2026-09-22.json) for a reproducible example.
