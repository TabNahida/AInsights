"""Build the static ranking data used by the docs site."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ArtificialAnalysis.scrape_artificial_analysis import RAW_SCORES_FILENAME, SCORE_SPECS


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_CSV = PROJECT_ROOT / "ArtificialAnalysis" / RAW_SCORES_FILENAME
DEFAULT_OUTPUT_JSON = PROJECT_ROOT / "docs" / "data" / "models.json"

ARTICLE_URL = "https://zhuanlan.zhihu.com/p/2032797597627311070?share_code=YgrFlZy1McBQ&utm_psn=2043622787617641823"
SOURCE_URL = "https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index"

AA_PRESET_COLUMNS = {
    "aa-intelligence": "AA Intelligence Index",
    "aa-coding": "AA Coding Index",
    "aa-agentic": "AA Agentic Index",
}

DEFAULT_CORRECTED_METRICS = [
    "GDPval-AA",
    "Terminal-Bench Hard",
    "τ²-Bench Telecom",
    "AA-LCR",
    "AA-Omniscience Accuracy",
    "AA-Omniscience Non-Hallucination Rate",
    "Humanity's Last Exam",
    "GPQA Diamond",
    "SciCode",
    "IFBench",
    "CritPt",
    "APEX-Agents-AA",
    "ITBench-AA",
    "MMMU-Pro",
]

STRENGTH_SUFFIX_RE = re.compile(
    r"\s*\((?:x?high|medium|low|max|min|default|fast|thinking|non[- ]reasoning|reasoning)\)\s*$",
    re.IGNORECASE,
)
SLUG_SUFFIX_RE = re.compile(
    r"-(?:x?high|medium|low|max|min|default|fast|thinking|non-reasoning|reasoning)$",
    re.IGNORECASE,
)
NON_WORD_RE = re.compile(r"[^a-z0-9]+")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def build_site_payload(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    source_rows = list(rows)
    metric_keys = [spec.column for spec in SCORE_SPECS]
    models = [_model_payload(row, metric_keys) for row in source_rows]

    return {
        "version": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": {
            "label": "Artificial Analysis Intelligence Evaluations",
            "url": SOURCE_URL,
            "defaultCorrectionReference": ARTICLE_URL,
            "defaultCorrectionNote": (
                "The default corrected preset uses the 14 quality evaluations visible in the "
                "referenced discussion context, with equal weights and missing metrics ignored."
            ),
        },
        "defaultPreset": "zhihu-adjusted",
        "defaultDedupe": True,
        "metrics": [
            {
                "key": key,
                "label": key,
                "defaultWeight": 1 if key in DEFAULT_CORRECTED_METRICS else 0,
            }
            for key in metric_keys
        ],
        "presets": _presets(),
        "models": models,
        "summary": {
            "modelRows": len(models),
            "variantGroups": len({model["variantGroup"] for model in models}),
        },
    }


def variant_group(model: str, slug: str = "") -> str:
    base = STRENGTH_SUFFIX_RE.sub("", model or "").strip()
    if not base and slug:
        base = SLUG_SUFFIX_RE.sub("", slug).replace("-", " ")
    normalized = NON_WORD_RE.sub(" ", base.lower()).strip()
    return normalized or (slug or model or "").lower()


def write_site_payload(input_csv: Path, output_json: Path) -> dict[str, Any]:
    payload = build_site_payload(read_csv_rows(input_csv))
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build docs/data/models.json for the static ranking site.")
    parser.add_argument("--input-csv", default=str(DEFAULT_INPUT_CSV), help="Raw scores CSV to read.")
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON), help="JSON payload to write.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = write_site_payload(Path(args.input_csv), Path(args.output_json))
    print(
        f"Wrote {args.output_json} with {payload['summary']['modelRows']} rows "
        f"across {payload['summary']['variantGroups']} dedupe groups."
    )
    return 0


def _model_payload(row: dict[str, Any], metric_keys: list[str]) -> dict[str, Any]:
    model = str(row.get("model") or "")
    slug = str(row.get("slug") or "")
    scores = {key: _number_or_none(row.get(key)) for key in metric_keys}
    aa_scores = {key: _number_or_none(row.get(column)) for key, column in AA_PRESET_COLUMNS.items()}

    return {
        "modelKey": row.get("model_key") or model,
        "model": model,
        "variantGroup": variant_group(model, slug),
        "isReasoning": str(row.get("is_reasoning") or "").lower() == "true",
        "slug": slug,
        "creator": row.get("creator") or "",
        "releaseDate": row.get("release_date") or "",
        "modelUrl": row.get("model_url") or "",
        "contextWindowTokens": _number_or_none(row.get("context_window_tokens")),
        "openSourceCategorization": row.get("open_source_categorization") or "",
        "medianOutputSpeed": _number_or_none(row.get("median_output_speed")),
        "aa": aa_scores,
        "aaCostUsd": _number_or_none(row.get("AA Intelligence Index Cost (USD)")),
        "scores": scores,
    }


def _presets() -> dict[str, dict[str, Any]]:
    return {
        "zhihu-adjusted": {
            "label": "文章修正版",
            "kind": "weighted-metrics",
            "description": "14 项质量评测等权综合，缺失项不计入分母，默认去重。",
            "weights": {key: 1 for key in DEFAULT_CORRECTED_METRICS},
        },
        "aa-intelligence": {
            "label": "AA Intelligence",
            "kind": "aa-column",
            "column": "aa-intelligence",
            "description": "Artificial Analysis 官方 Intelligence Index。",
        },
        "aa-coding": {
            "label": "AA Coding",
            "kind": "aa-column",
            "column": "aa-coding",
            "description": "Artificial Analysis 官方 Coding Index。",
        },
        "aa-agentic": {
            "label": "AA Agentic",
            "kind": "aa-column",
            "column": "aa-agentic",
            "description": "Artificial Analysis 官方 Agentic Index。",
        },
        "custom": {
            "label": "自定义占比",
            "kind": "weighted-metrics",
            "description": "按用户设置的评测权重实时计算。",
            "weights": {key: 1 if key in DEFAULT_CORRECTED_METRICS else 0 for key in [spec.column for spec in SCORE_SPECS]},
        },
    }


def _number_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


if __name__ == "__main__":
    raise SystemExit(main())
