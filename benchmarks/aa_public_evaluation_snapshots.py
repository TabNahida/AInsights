"""Pinned public Artificial Analysis evaluation-page scores for hard tests.

The public pages embed the selected chart's exact model/configuration rows in
Next.js flight data. Each score below comes from that page's named metric,
never from the similarly named vendor-reported or Elo result. The checked
snapshot retains the AA slug and name, the site's exact slug match at capture
time, and a SHA-256 of each downloaded page.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = ROOT / "data/benchmarks/aa_difficult_public_pages_2026-09-25.json"
AA_RAW_SCORES_PATH = ROOT / "ArtificialAnalysis/artificialanalysis_raw_scores_wide.csv"
SNAPSHOT_SHA256 = "cc769b605412ad11802a684af5292957d40a3d3e42b32e7cb1b00acd96a06789"

METRICS = (
    {
        "id": "aa-analyst-agent-pass5",
        "label": "AA-AnalystAgent (pass^5)",
        "category": "Agentic analysis",
        "url": "https://artificialanalysis.ai/evaluations/aa-analyst-agent",
        "field": ("analystAgent",),
        "selectedChartRows": 15,
        "protocol": "80 private analysis tasks, five independent runs; pass^5",
    },
    {
        "id": "mlcr-aa-overall",
        "label": "MLCR-AA (Overall)",
        "category": "Medical long-context reasoning",
        "url": "https://artificialanalysis.ai/evaluations/mlcr-aa",
        "field": ("mlcrOverall",),
        "selectedChartRows": 31,
        "protocol": "Private expert and compound clinical tasks; Overall score",
    },
    {
        "id": "terminal-bench-science-aa",
        "label": "Terminal-Bench-Science v0.1.0 (AA)",
        "category": "Agentic scientific work",
        "url": "https://artificialanalysis.ai/evaluations/terminal-bench-science",
        "field": ("terminalBenchScience",),
        "selectedChartRows": 26,
        "protocol": "v0.1.0; 70 science terminal tasks, common AA mini-swe-agent, mean pass@1 across three runs",
    },
    {
        "id": "aa-briefcase-rubric-pass-rate",
        "label": "AA-Briefcase v1.1 (Rubric Pass Rate)",
        "category": "Agentic document work",
        "url": "https://artificialanalysis.ai/evaluations/aa-briefcase?results=rubric-score",
        "field": ("briefcaseBreakdown", "rubricPassRate"),
        "selectedChartRows": 32,
        "protocol": "91 private document/artifact tasks; rubric pass rate, distinct from Briefcase Elo",
    },
    {
        "id": "harvey-lab-aa-all-pass-rate",
        "label": "Harvey LAB-AA (All-pass Rate)",
        "category": "Legal agentic work",
        "url": "https://artificialanalysis.ai/evaluations/harvey-lab-aa?eval-score=all-pass-rate",
        "field": ("harveyLabBreakdown", "ungatedAverageAllPass"),
        "selectedChartRows": 14,
        "protocol": "120 private legal tasks; all rubric criteria must pass",
    },
)


class _ScriptParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.active = False
        self.parts: list[str] = []
        self.scripts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "script":
            self.active = True
            self.parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self.active:
            self.scripts.append("".join(self.parts))
            self.active = False

    def handle_data(self, data: str) -> None:
        if self.active:
            self.parts.append(data)


def _find_initial_models(value: Any):
    if isinstance(value, dict):
        rows = value.get("initialModels")
        if isinstance(rows, list) and rows and all(isinstance(row, dict) for row in rows):
            yield rows
        for child in value.values():
            yield from _find_initial_models(child)
    elif isinstance(value, list):
        for child in value:
            yield from _find_initial_models(child)


def _score(model: dict[str, Any], field: tuple[str, ...]) -> float | None:
    value: Any = model
    for key in field:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"AA score has unexpected type: {field}")
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"AA score outside [0,1]: {field}: {value}")
    return float(value)


def extract_page_rows(html: str, field: tuple[str, ...], selected_chart_rows: int) -> list[dict[str, Any]]:
    """Require the reviewed selected-chart size and an unambiguous SSR row set.

    AA pages embed several charts in flight data. An unrelated chart may have
    more rows than the selected score chart, so the largest array is unsafe.
    The selected-model count is pinned from the visible chart and must be
    reviewed again before capturing an expanded set.
    """

    if selected_chart_rows < 1:
        raise ValueError("AA selected-chart row count must be positive")

    parser = _ScriptParser()
    parser.feed(html)
    candidates = []
    for script in parser.scripts:
        prefix = "self.__next_f.push("
        if not script.startswith(prefix) or not script.endswith(")"):
            continue
        try:
            outer = json.loads(script[len(prefix):-1])
        except json.JSONDecodeError:
            continue
        if not isinstance(outer, list) or len(outer) != 2 or not isinstance(outer[1], str):
            continue
        _, colon, data = outer[1].partition(":")
        if not colon or field[0] not in data:
            continue
        try:
            value = json.loads(data)
        except json.JSONDecodeError:
            continue
        for models in _find_initial_models(value):
            rows = []
            for model in models:
                score = _score(model, field)
                if score is None:
                    continue
                slug, name = model.get("slug"), model.get("name")
                if not isinstance(slug, str) or not isinstance(name, str):
                    raise ValueError("AA public chart row lacks model identity")
                rows.append({"aaSlug": slug, "aaName": name, "scoreFraction": score})
            if rows:
                candidates.append(rows)
    if not candidates:
        raise ValueError(f"AA page has no selected-model chart for {field}")
    matches = [rows for rows in candidates if len(rows) == selected_chart_rows]
    if not matches:
        counts = sorted({len(rows) for rows in candidates})
        raise ValueError(
            f"AA selected-model chart for {field} changed from {selected_chart_rows} rows; "
            f"SSR candidate counts: {counts}"
        )
    signatures = {
        tuple(sorted((row["aaSlug"], row["aaName"], row["scoreFraction"]) for row in rows))
        for rows in matches
    }
    if len(signatures) != 1:
        raise ValueError(f"AA selected-model chart for {field} is ambiguous")
    rows = matches[0]
    slugs = [row["aaSlug"] for row in rows]
    if len(slugs) != len(set(slugs)):
        raise ValueError(f"AA selected-model chart has duplicate slugs for {field}")
    return rows


def _current_aa_model_keys() -> dict[str, str]:
    """Read the maintained AA model/configuration identity table."""

    with AA_RAW_SCORES_PATH.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not {"slug", "model_key"}.issubset(reader.fieldnames):
            raise ValueError("AA raw score CSV lacks slug/model_key columns")
        by_slug = {}
        for row in reader:
            slug, model_key = row["slug"], row["model_key"]
            if not slug or not model_key or slug in by_slug:
                raise ValueError(f"AA raw score CSV has missing/duplicate model identity: {slug!r}")
            by_slug[slug] = model_key
    return by_slug


def _check_aa_config(row: dict[str, Any], raw_keys: dict[str, str]) -> None:
    model_key = row["siteModelKey"]
    if model_key is not None and _matching_aa_config(row, raw_keys) is None:
        raise ValueError(
            f"AA model configuration drift for {row['aaSlug']}: "
            f"snapshot {model_key!r}, current AA {raw_keys.get(row['aaSlug'])!r}"
        )


def _matching_aa_config(row: dict[str, Any], raw_keys: dict[str, str]) -> str | None:
    """Allow display-name casing changes, but never infer a different tier.

    A pinned slug can later be removed or reassigned. Historical evidence is
    usable only when its complete configuration name still matches the live
    catalogue; an added effort label requires a new reviewed observation.
    """

    captured_key = row["siteModelKey"]
    current_key = raw_keys.get(row["aaSlug"])
    if captured_key is None or current_key is None:
        return None
    return current_key if current_key.casefold() == captured_key.casefold() else None


def capture_snapshot() -> dict[str, Any]:
    """Download only public benchmark pages and pin their visible chart rows."""

    site = json.loads((ROOT / "docs/data/models.json").read_text(encoding="utf-8"))
    site_by_slug = {model["slug"]: model for model in site["models"]}
    if len(site_by_slug) != len(site["models"]):
        raise ValueError("site model slugs are not unique")
    raw_keys = _current_aa_model_keys()
    snapshot = {
        "schemaVersion": 1,
        "capturedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "metrics": [],
    }
    for spec in METRICS:
        request = Request(spec["url"], headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request, timeout=30) as response:
            if response.status != 200:
                raise ValueError(f"AA page returned {response.status}: {spec['url']}")
            body = response.read()
        rows = extract_page_rows(body.decode("utf-8", "replace"), spec["field"], spec["selectedChartRows"])
        for row in rows:
            site_model = site_by_slug.get(row["aaSlug"])
            row["siteModelKey"] = site_model["modelKey"] if site_model else None
            _check_aa_config(row, raw_keys)
        snapshot["metrics"].append({
            "benchmarkId": spec["id"],
            "sourceUrl": spec["url"],
            "field": list(spec["field"]),
            "pageSha256": hashlib.sha256(body).hexdigest(),
            "publicChartRows": len(rows),
            "rows": rows,
        })
    SNAPSHOT_PATH.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return snapshot


def load_aa_difficult_snapshots() -> tuple[tuple[dict[str, Any], list[dict[str, Any]]], ...]:
    """Load checked AA rows with only exact, existing site configurations."""

    raw = SNAPSHOT_PATH.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != SNAPSHOT_SHA256:
        raise ValueError(f"AA difficult-evaluation snapshot hash changed: {digest}")
    snapshot = json.loads(raw)
    if snapshot.get("schemaVersion") != 1:
        raise ValueError("AA difficult-evaluation snapshot schema changed")
    by_id = {item["benchmarkId"]: item for item in snapshot["metrics"]}
    if set(by_id) != {spec["id"] for spec in METRICS}:
        raise ValueError("AA difficult-evaluation snapshot metric set changed")
    raw_keys = _current_aa_model_keys()
    pairs = []
    for spec in METRICS:
        item = by_id[spec["id"]]
        if item["field"] != list(spec["field"]) or item["sourceUrl"] != spec["url"]:
            raise ValueError(f"AA metric protocol selector changed: {spec['id']}")
        rows = item["rows"]
        slugs = [row["aaSlug"] for row in rows]
        if len(slugs) != len(set(slugs)) or len(rows) != item["publicChartRows"]:
            raise ValueError(f"AA snapshot row count/identity changed: {spec['id']}")
        if len(rows) != spec["selectedChartRows"]:
            raise ValueError(f"AA selected-model chart size changed: {spec['id']}")
        model_keys = [_matching_aa_config(row, raw_keys) for row in rows]
        drift_rows = [
            {
                "aaSlug": row["aaSlug"],
                "snapshotModelKey": row["siteModelKey"],
                "currentModelKey": raw_keys.get(row["aaSlug"]),
            }
            for row, model_key in zip(rows, model_keys, strict=True)
            if row["siteModelKey"] is not None and model_key is None
        ]
        source_id = f"aa-public-{spec['id']}-2026-09-25"
        source = {
            "id": source_id,
            "label": f"Artificial Analysis public {spec['label']} chart",
            "url": spec["url"],
            "category": "Independent benchmark evaluation",
            "collectionStatus": f"pinned-public-chart; checked {snapshot['capturedAt']}",
            "note": (
                f"{spec['protocol']}. Only the page's selected, publicly embedded "
                "chart rows are included; no paid download is implied. AA's exact "
                "model slug and display name are retained, and only slugs matching "
                "an existing site configuration contribute a score. Removed or "
                "changed configurations remain in the pinned snapshot and are "
                "excluded from scoring until their identity is reviewed again."
            ),
            "snapshotFile": str(SNAPSHOT_PATH.relative_to(ROOT)).replace("\\", "/"),
            "snapshotSha256": SNAPSHOT_SHA256,
            "pageSha256": item["pageSha256"],
            "snapshotRows": len(rows),
            "mappedRows": sum(model_key is not None for model_key in model_keys),
            "configurationDriftRows": drift_rows,
            "scoreSelection": ".".join(spec["field"]),
            "resultProtocol": spec["protocol"],
        }
        results = []
        for row, model_key in zip(rows, model_keys, strict=True):
            score = row["scoreFraction"]
            if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score) or not 0 <= score <= 1:
                raise ValueError(f"AA snapshot score invalid: {spec['id']}: {row['aaSlug']}")
            if model_key is None:
                continue
            results.append({
                "benchmarkId": spec["id"],
                "benchmarkLabel": spec["label"],
                "model": model_key,
                "modelAliases": [model_key],
                "value": score * 100,
                "unit": "%",
                "sourceId": source_id,
                "sourceUrl": spec["url"],
                "sourceLabel": source["label"],
                "variantScoped": True,
                "modelScoreEligible": True,
                "evidenceEligible": True,
                "configurationConfidence": "explicit",
                "scoreOrigin": "aa-public-evaluation-page",
                "scoreSelection": ".".join(spec["field"]),
                "configurationNote": f"AA slug {row['aaSlug']}; AA name {row['aaName']}; {spec['protocol']}.",
            })
        if len({row["model"] for row in results}) != len(results):
            raise ValueError(f"AA snapshot maps duplicate site configurations: {spec['id']}")
        pairs.append((source, results))
    return tuple(pairs)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--capture", action="store_true")
    args = parser.parse_args()
    if not args.capture:
        parser.error("use --capture to update the pinned public AA chart snapshot")
    result = capture_snapshot()
    print(f"Wrote {SNAPSHOT_PATH} with {len(result['metrics'])} public metrics")
