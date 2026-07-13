# Open-source Category Mapping Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore the `open` source type for every model whose Artificial Analysis category is `permissive` or `commercial-license`.

**Architecture:** Preserve the upstream CSV values and extend the shared `open_source_type(category: str) -> str` normalization boundary in the static-site builder. Rebuild the generated JSON and JavaScript payloads so every data-driven page and filter receives the corrected type.

**Tech Stack:** Python 3 standard library, `unittest`, generated JSON/JavaScript static-site data.

## Global Constraints

- Keep `ArtificialAnalysis/artificialanalysis_raw_scores_wide.csv` unchanged.
- Treat `permissive` and `commercial-license` as open weights.
- Preserve compatibility with descriptive `Open Weights (...)` values.
- Preserve `proprietary` and `closed` as closed, and missing or unrecognized values as unknown.
- Do not change scraper behavior, UI markup, benchmark data, or source data.

---

### Task 1: Normalize current Artificial Analysis category identifiers

**Files:**
- Modify: `tests/test_build_docs_site.py:7-20`
- Modify: `tests/test_build_docs_site.py:203-244`
- Modify: `scripts/build_docs_site.py:1323-1331`

**Interfaces:**
- Consumes: Artificial Analysis `open_source_categorization` strings.
- Produces: `open_source_type(category: str) -> str`, returning exactly `open`, `closed`, or `unknown`.

- [ ] **Step 1: Write the failing regression test**

Add `open_source_type` to the existing import list from `scripts.build_docs_site`, then add this focused test to `BuildDocsSiteTests` near the existing source-type payload test:

```python
    def test_open_source_type_supports_current_and_legacy_categories(self):
        expectations = {
            "permissive": "open",
            "commercial-license": "open",
            "Open Weights (Permissive License)": "open",
            "Proprietary": "closed",
            "closed": "closed",
            "": "unknown",
            "future-category": "unknown",
        }

        for category, expected in expectations.items():
            with self.subTest(category=category):
                self.assertEqual(open_source_type(category), expected)
```

- [ ] **Step 2: Run the focused test and verify the regression is reproduced**

Run:

```powershell
python -m unittest tests.test_build_docs_site.BuildDocsSiteTests.test_open_source_type_supports_current_and_legacy_categories -v
```

Expected: FAIL for `permissive` and `commercial-license`, each returning `unknown` instead of `open`.

- [ ] **Step 3: Implement the minimal compatibility mapping**

Update `open_source_type` without changing its interface:

```python
def open_source_type(category: str) -> str:
    normalized = category.strip().lower()
    if not normalized:
        return "unknown"
    if normalized in {"permissive", "commercial-license"} or "open" in normalized:
        return "open"
    if "proprietary" in normalized or "closed" in normalized:
        return "closed"
    return "unknown"
```

- [ ] **Step 4: Run the focused test and the builder test module**

Run:

```powershell
python -m unittest tests.test_build_docs_site.BuildDocsSiteTests.test_open_source_type_supports_current_and_legacy_categories -v
python -m unittest discover -s tests -p test_build_docs_site.py -v
```

Expected: the focused test passes, then every test in `test_build_docs_site.py` passes with zero failures.

- [ ] **Step 5: Commit the tested mapping fix**

```powershell
git add tests/test_build_docs_site.py scripts/build_docs_site.py
git commit -m "Fix open-source category mapping"
```

### Task 2: Rebuild and validate static-site data

**Files:**
- Modify: `docs/data/models.json`
- Modify: `docs/data/models.js`

**Interfaces:**
- Consumes: corrected `open_source_type(category: str) -> str` and `ArtificialAnalysis/artificialanalysis_raw_scores_wide.csv`.
- Produces: generated `docs/data/models.json` and `docs/data/models.js` with corrected `openSourceType` fields.

- [ ] **Step 1: Rebuild both generated payloads**

Run:

```powershell
python scripts/build_docs_site.py
```

Expected: `Wrote 559 model rows to docs\data\models.json` and the command exits with status 0.

- [ ] **Step 2: Assert category coverage and the reported Kimi example**

Run:

```powershell
@'
import json
from collections import Counter

payload = json.load(open("docs/data/models.json", encoding="utf-8"))
source_types = Counter(model["openSourceType"] for model in payload["models"])
categories = Counter(model["openSourceCategorization"] for model in payload["models"])
kimi = next(model for model in payload["models"] if model["slug"] == "kimi-k2-6")

assert len(payload["models"]) == 559, len(payload["models"])
assert categories == {"permissive": 310, "proprietary": 232, "commercial-license": 17}, categories
assert source_types == {"open": 327, "closed": 232}, source_types
assert kimi["openSourceCategorization"] == "permissive", kimi
assert kimi["openSourceType"] == "open", kimi
print(source_types)
'@ | python -
```

Expected: prints `Counter({'open': 327, 'closed': 232})` and exits with status 0.

- [ ] **Step 3: Run complete verification**

Run:

```powershell
python -m unittest discover -s tests -v
git diff --check
```

Expected: all tests pass with zero failures; `git diff --check` prints no errors.

- [ ] **Step 4: Review the generated diff scope**

Run:

```powershell
git status --short
git diff --stat
git diff -- scripts/build_docs_site.py tests/test_build_docs_site.py
```

Expected: only the mapping code, regression test, and generated `docs/data/models.json` / `docs/data/models.js` are implementation changes; the already committed spec and plan are not mixed into this commit.

- [ ] **Step 5: Commit the rebuilt site data**

```powershell
git add docs/data/models.json docs/data/models.js
git commit -m "Rebuild site data with source types"
```
