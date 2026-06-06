"""Collect source-backed external benchmark scores for the docs site.

Some model launch pages expose benchmark tables as stable HTML text; others use
images or heavily protected pages. This script keeps the output deterministic by
falling back to curated seed rows with explicit source URLs when direct refresh
is blocked.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_JSON = PROJECT_ROOT / "ArtificialAnalysis" / "external_benchmark_scores.json"
OPENAI_GPT55_URL = "https://openai.com/index/introducing-gpt-5-5/"
GOOGLE_GEMINI31_URL = "https://deepmind.google/models/model-cards/gemini-3-1-pro/"

MODEL_ALIASES = {
    "GPT-5.5": ["GPT-5.5", "GPT-5.5 (xhigh)", "gpt-5-5", "gpt-5-5-xhigh"],
    "GPT-5.4": ["GPT-5.4", "GPT-5.4 (xhigh)", "gpt-5-4", "gpt-5-4-xhigh"],
    "GPT-5.5 Pro": ["GPT-5.5 Pro", "GPT-5.5 Pro (xhigh)", "gpt-5-5-pro"],
    "GPT-5.4 Pro": ["GPT-5.4 Pro", "GPT-5.4 Pro (xhigh)", "gpt-5-4-pro"],
    "Claude Opus 4.7": ["Claude Opus 4.7", "Claude Opus 4.7 (Adaptive Reasoning)", "claude-opus-4-7"],
    "Gemini 3.1 Pro": ["Gemini 3.1 Pro", "Gemini 3.1 Pro Preview", "Gemini 3.1 Pro (high)", "gemini-3-1-pro-preview", "gemini-3-1-pro-high"],
}

OPENAI_MODEL_COLUMNS = [
    "GPT-5.5",
    "GPT-5.4",
    "GPT-5.5 Pro",
    "GPT-5.4 Pro",
    "Claude Opus 4.7",
    "Gemini 3.1 Pro",
]

BENCHMARKS = [
    {
        "id": "swe-bench-pro",
        "label": "SWE-Bench Pro",
        "category": "Agentic coding",
        "unit": "%",
        "icon": "SWE",
        "openaiLabel": "SWE-Bench Pro (Public)",
    },
    {
        "id": "terminal-bench-2",
        "label": "Terminal-Bench 2.0",
        "category": "Agentic coding",
        "unit": "%",
        "icon": "TERM",
        "openaiLabel": "Terminal-Bench 2.0",
    },
    {
        "id": "expert-swe-internal",
        "label": "Expert-SWE (Internal)",
        "category": "Agentic coding",
        "unit": "%",
        "icon": "EXP",
        "openaiLabel": "Expert-SWE (Internal)",
    },
    {
        "id": "gdpval-wins-ties",
        "label": "GDPval (wins or ties)",
        "category": "Professional work",
        "unit": "%",
        "icon": "GDP",
        "openaiLabel": "GDPval (wins or ties)",
    },
    {
        "id": "osworld-verified",
        "label": "OSWorld-Verified",
        "category": "Computer use",
        "unit": "%",
        "icon": "OS",
        "openaiLabel": "OSWorld-Verified",
    },
    {
        "id": "toolathlon",
        "label": "Toolathlon",
        "category": "Tool use",
        "unit": "%",
        "icon": "TOOL",
        "openaiLabel": "Toolathlon",
    },
    {
        "id": "browsecomp",
        "label": "BrowseComp",
        "category": "Tool use",
        "unit": "%",
        "icon": "WEB",
        "openaiLabel": "BrowseComp",
    },
    {
        "id": "frontiermath-tier-1-3",
        "label": "FrontierMath Tier 1-3",
        "category": "Academic reasoning",
        "unit": "%",
        "icon": "FM",
        "openaiLabel": "FrontierMath Tier 1–3",
    },
    {
        "id": "frontiermath-tier-4",
        "label": "FrontierMath Tier 4",
        "category": "Academic reasoning",
        "unit": "%",
        "icon": "FM4",
        "openaiLabel": "FrontierMath Tier 4",
    },
    {
        "id": "cybergym",
        "label": "CyberGym",
        "category": "Cybersecurity",
        "unit": "%",
        "icon": "CY",
        "openaiLabel": "CyberGym",
    },
]

SEED_OPENAI_VALUES = {
    "swe-bench-pro": [58.6, 57.7, None, None, 64.3, 54.2],
    "terminal-bench-2": [82.7, 75.1, None, None, 69.4, 68.5],
    "expert-swe-internal": [73.1, 68.5, None, None, None, None],
    "gdpval-wins-ties": [84.9, 83.0, 82.3, 82.0, 80.3, 67.3],
    "osworld-verified": [78.7, 75.0, None, None, 78.0, None],
    "toolathlon": [55.6, 54.6, None, None, None, 48.8],
    "browsecomp": [84.4, 82.7, 90.1, 89.3, 79.3, 85.9],
    "frontiermath-tier-1-3": [51.7, 47.6, 52.4, 50.0, 43.8, 36.9],
    "frontiermath-tier-4": [35.4, 27.1, 39.6, 38.0, 22.9, 16.7],
    "cybergym": [81.8, 79.0, None, None, 73.1, None],
}


class _VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tokens: list[str] = []

    def handle_data(self, data: str) -> None:
        text = re.sub(r"\s+", " ", data).strip()
        if text:
            self.tokens.append(text)


def fetch_html(url: str, timeout: float = 30) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def parse_openai_scores(html: str) -> dict[str, list[float | None]]:
    tokens = visible_text_tokens(html)
    try:
        start = tokens.index("Evaluations")
        tokens = tokens[start:]
    except ValueError:
        pass

    scores: dict[str, list[float | None]] = {}
    for benchmark in BENCHMARKS:
        label = benchmark["openaiLabel"]
        index = _find_label_index(tokens, label)
        if index is None:
            continue
        values = _next_percent_values(tokens[index + 1 :], len(OPENAI_MODEL_COLUMNS))
        if len(values) == len(OPENAI_MODEL_COLUMNS):
            scores[benchmark["id"]] = values
    return scores


def visible_text_tokens(html: str) -> list[str]:
    parser = _VisibleTextParser()
    parser.feed(html)
    return parser.tokens


def build_payload(openai_scores: dict[str, list[float | None]], collection_status: str) -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    benchmarks = [
        {key: value for key, value in benchmark.items() if key != "openaiLabel"}
        for benchmark in BENCHMARKS
    ]
    source = {
        "id": "openai-gpt-5-5",
        "label": "OpenAI GPT-5.5 launch evaluations",
        "url": OPENAI_GPT55_URL,
        "category": "Official model release",
        "collectionStatus": collection_status,
        "note": "Official OpenAI table covering GPT-5.5, GPT-5.4, GPT-5.5 Pro, GPT-5.4 Pro, Claude Opus 4.7, and Gemini 3.1 Pro.",
    }
    google_source = {
        "id": "google-gemini-3-1-pro-card",
        "label": "Google DeepMind Gemini 3.1 Pro model card",
        "url": GOOGLE_GEMINI31_URL,
        "category": "Official model card",
        "collectionStatus": "reference",
        "note": "Official Google DeepMind model card with Gemini 3.1 Pro cross-model benchmark context.",
    }
    results = []
    for benchmark in BENCHMARKS:
        values = openai_scores.get(benchmark["id"], SEED_OPENAI_VALUES.get(benchmark["id"], []))
        for model_name, value in zip(OPENAI_MODEL_COLUMNS, values):
            if value is None:
                continue
            results.append(
                {
                    "benchmarkId": benchmark["id"],
                    "benchmarkLabel": benchmark["label"],
                    "model": model_name,
                    "modelAliases": MODEL_ALIASES.get(model_name, [model_name]),
                    "value": value,
                    "unit": benchmark["unit"],
                    "sourceId": source["id"],
                    "sourceUrl": source["url"],
                    "sourceLabel": source["label"],
                }
            )

    return {
        "version": 1,
        "generatedAt": generated_at,
        "sources": [source, google_source],
        "benchmarks": benchmarks,
        "results": results,
    }


def collect(timeout: float = 30) -> dict[str, Any]:
    try:
        html = fetch_html(OPENAI_GPT55_URL, timeout=timeout)
        parsed = parse_openai_scores(html)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        return build_payload(SEED_OPENAI_VALUES, f"seeded-official-values; refresh blocked: {exc.__class__.__name__}")

    missing = {benchmark["id"] for benchmark in BENCHMARKS} - set(parsed)
    if missing:
        merged = {**SEED_OPENAI_VALUES, **parsed}
        return build_payload(merged, f"partial-refresh; seeded {len(missing)} benchmark rows")
    return build_payload(parsed, "refreshed")


def write_payload(output_json: Path, timeout: float = 30) -> dict[str, Any]:
    payload = collect(timeout=timeout)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def _find_label_index(tokens: list[str], label: str) -> int | None:
    normalized_label = _normalize_label(label)
    for index, token in enumerate(tokens):
        if _normalize_label(token).startswith(normalized_label):
            return index
    return None


def _next_percent_values(tokens: list[str], count: int) -> list[float | None]:
    values: list[float | None] = []
    for token in tokens:
        if token == "-":
            values.append(None)
        else:
            match = re.search(r"(-?\d+(?:\.\d+)?)\s*%", token)
            if not match:
                continue
            values.append(float(match.group(1)))
        if len(values) == count:
            return values
    return values


def _normalize_label(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect external benchmark scores for the static site.")
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON), help="JSON payload to write.")
    parser.add_argument("--timeout", type=float, default=30, help="HTTP timeout in seconds.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        payload = write_payload(Path(args.output_json), timeout=args.timeout)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(
        f"Wrote {args.output_json} with {len(payload['results'])} benchmark scores "
        f"({payload['sources'][0]['collectionStatus']})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
