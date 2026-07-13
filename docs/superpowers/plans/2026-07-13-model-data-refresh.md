# Model Data Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refresh static model data, add official GPT-5.6 benchmark coverage, and make GitHub Actions update the complete dataset daily.

**Architecture:** Extend the existing declarative benchmark/source registries rather than adding a second collector. Keep official seed values deterministic, let the generic HTML-table parser refresh them when OpenAI is reachable, and rebuild the existing data-driven static site payload.

**Tech Stack:** Python 3.13+, `unittest`, GitHub Actions YAML, static JSON/JavaScript artifacts.

## Global Constraints

- Only official vendor pages may seed vendor benchmark scores.
- Do not invent scores for Grok 4.5, Muse Spark 1.1, or JT-4.1 Flash.
- Keep generated site data in sync with the source CSV and benchmark JSON.
- Work in the current checkout because the user explicitly requested an in-place update and commit.

---

### Task 1: Add the GPT-5.6 official benchmark source

**Files:**
- Modify: `tests/test_collect_external_benchmarks.py`
- Modify: `benchmarks/collect_benchmark_scores.py`

**Interfaces:**
- Consumes: existing `BENCHMARKS`, `MODEL_ALIASES`, `OFFICIAL_SOURCE_SPECS`, and `build_payload()`.
- Produces: source ID `openai-gpt-5-6-release`, GPT-5.6 aliases, 28 new benchmark definitions, and official result rows for Sol/Terra/Luna.

- [ ] **Step 1: Write failing tests**

Add assertions that `build_payload({}, "seeded")` contains the official URL, representative existing scores (`swe-bench-pro`, `terminal-bench-2-1`, `gpqa-diamond`), representative new scores (`agents-last-exam`, `osworld-2`, `arc-agi-3`), and aliases matching the AA slugs.

- [ ] **Step 2: Verify the tests fail**

Run: `python -m unittest tests.test_collect_external_benchmarks.ExternalBenchmarkCollectorTests.test_build_payload_includes_gpt56_official_scores -v`

Expected: failure because `openai-gpt-5-6-release` and GPT-5.6 results do not exist.

- [ ] **Step 3: Add minimal collector data**

Add `OPENAI_GPT56_URL`, aliases for `GPT-5.6 Sol`, `GPT-5.6 Terra`, `GPT-5.6 Luna`, and `glm-5-2-non-reasoning`. Add the 28 distinct benchmark definitions. Add an official source spec whose `columns`, `rowLabels`, and `scores` map the three GPT-5.6 family members to the official table values.

- [ ] **Step 4: Verify focused tests pass**

Run: `python -m unittest tests.test_collect_external_benchmarks -v`

Expected: all external benchmark collector tests pass.

### Task 2: Update and test the scheduled refresh workflow

**Files:**
- Create: `tests/test_update_workflow.py`
- Modify: `.github/workflows/update-artificial-analysis.yml`

**Interfaces:**
- Consumes: the three README refresh commands.
- Produces: a daily complete model/benchmark/site refresh with official-source validation and a general commit message.

- [ ] **Step 1: Write a failing workflow contract test**

Assert that the workflow has `cron: "0 1 * * *"`, contains `openai-gpt-5-6-release`, runs the scraper, collector, builder, and tests, stages both benchmark/site data files, and uses `Update model and benchmark data` as its commit message.

- [ ] **Step 2: Verify the workflow test fails**

Run: `python -m unittest tests.test_update_workflow -v`

Expected: failure on the weekly cron and missing GPT-5.6 source ID.

- [ ] **Step 3: Update the workflow**

Change the display name and concurrency group to the complete refresh, change the schedule to daily, add the GPT-5.6 source ID to the official policy set, generalize no-change/commit messages, and retain pre/post tests plus rebase-before-push behavior.

- [ ] **Step 4: Verify the workflow test passes**

Run: `python -m unittest tests.test_update_workflow -v`

Expected: all workflow contract tests pass.

### Task 3: Refresh source and generated site data

**Files:**
- Modify: `ArtificialAnalysis/artificialanalysis_raw_scores_wide.csv`
- Modify: `data/benchmarks/benchmark_scores.json`
- Modify: `docs/data/models.json`
- Modify: `docs/data/models.js`
- Modify/Create: `docs/assets/logos/*` only when referenced by the refreshed AA payload.

**Interfaces:**
- Consumes: the updated collector and the live Artificial Analysis payload.
- Produces: a self-consistent static-site dataset with 559 model rows and GPT-5.6 official benchmark evidence.

- [ ] **Step 1: Run the production refresh commands**

Run:

```powershell
python ArtificialAnalysis\scrape_artificial_analysis.py --output-dir ArtificialAnalysis
python benchmarks\collect_benchmark_scores.py --output-json data\benchmarks\benchmark_scores.json
python scripts\build_docs_site.py
```

Expected: each command exits 0 and writes its target artifacts.

- [ ] **Step 2: Validate generated content**

Run a Python assertion script that checks model-row count, GPT-5.6 slugs, the official source URL, representative official scores, and attached external benchmarks in `docs/data/models.json`.

Expected: all assertions pass.

### Task 4: Verify and commit

**Files:**
- All files changed by Tasks 1-3.

**Interfaces:**
- Consumes: the completed source and generated changes.
- Produces: one reviewed repository commit containing the implementation and refreshed artifacts.

- [ ] **Step 1: Run the complete test suite**

Run: `python -m unittest discover -s tests -v`

Expected: all tests pass with no errors.

- [ ] **Step 2: Review scope**

Run: `git status --short` and `git diff --check`, then inspect the diff summary and confirm no temporary files are staged.

- [ ] **Step 3: Commit**

Stage the intended source, workflow, tests, design/plan, and generated artifacts. Commit with message `Update model and benchmark data`.

