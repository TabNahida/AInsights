# Model Data Refresh Design

## Goal

Refresh the static site with the latest Artificial Analysis model rows, add source-backed GPT-5.6 evaluations from OpenAI's official release page, make the scheduled GitHub Action refresh the complete model and benchmark dataset, and commit the resulting source and generated files.

## Source Policy

- Artificial Analysis remains the source for model metadata, pricing, speed, and AA benchmark columns.
- OpenAI's official `https://openai.com/index/gpt-5-6/` release page is the only new source of GPT-5.6 external benchmark scores.
- The OpenAI page's two composite Artificial Analysis indices are not duplicated as external benchmarks.
- Existing benchmark IDs are reused only when the official row is the same named/versioned evaluation. Versioned or materially different rows receive new IDs.
- Grok 4.5, Muse Spark 1.1, and JT-4.1 Flash receive refreshed Artificial Analysis data but no seeded external scores until an official, machine-verifiable evaluation table is available.
- GLM-5.2's non-reasoning slug is added to the existing official model alias set; it does not create a duplicate source.

## Data Model

`benchmarks/collect_benchmark_scores.py` will add aliases for GPT-5.6 Sol, Terra, and Luna and an `openai-gpt-5-6-release` official-source specification. The source will contain deterministic seed values for the three GPT-5.6 family members and parsing metadata for the official HTML tables. Nine already-defined benchmark IDs will be reused and 28 distinct official evaluation rows will be added to `BENCHMARKS`.

The static site remains data-driven. Running `scripts/build_docs_site.py` will propagate the refreshed CSV and benchmark payload into `docs/data/models.json` and `docs/data/models.js`. Existing model, benchmark, and source pages will display the new rows without duplicating HTML templates.

## Automation

`.github/workflows/update-artificial-analysis.yml` will be renamed at the workflow-display level to describe the complete model and benchmark refresh, run daily instead of weekly, validate the GPT-5.6 official source URL policy, rebuild the static site, run tests before and after the refresh, and commit all refreshed data/site assets with a general model-data commit message.

## Failure Handling

Official-page refreshes may be blocked by Cloudflare or time out. The collector will retain the existing deterministic fallback behavior: it emits curated official seed values and records the blocked/partial status in the source metadata. The workflow fails on scraper, build, policy, or test errors and does not push a partial commit.

## Verification

- Unit tests prove that the GPT-5.6 source, aliases, benchmark definitions, and representative Sol/Terra/Luna scores exist.
- A workflow test proves the daily schedule, official-source policy entry, complete refresh commands, and staged generated files.
- The full test suite runs before and after data generation.
- Generated payload checks confirm 559 model rows, GPT-5.6 visibility, the official source URL, and external benchmark attachment across GPT-5.6 variants.

