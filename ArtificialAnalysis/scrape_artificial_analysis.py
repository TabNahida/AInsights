"""Scrape Artificial Analysis language-model benchmark data.

The Artificial Analysis pages are rendered by Next.js. The benchmark rows used by
the page are embedded in the initial React flight payload, so this scraper reads
that payload directly instead of driving a browser.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Callable, Iterable
from urllib.request import Request, urlopen


SOURCE_URL = "https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent
RAW_SCORES_FILENAME = "artificialanalysis_raw_scores_wide.csv"

NEXT_FLIGHT_CHUNK_RE = re.compile(
    r"self\.__next_f\.push\(\[1,\"((?:\\.|[^\"\\])*)\"\]\)</script>",
    re.DOTALL,
)


def fetch_html(url: str = SOURCE_URL, timeout: float = 30) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def decode_next_flight(html: str) -> str:
    chunks: list[str] = []
    for match in NEXT_FLIGHT_CHUNK_RE.finditer(html):
        chunks.append(json.loads(f'"{match.group(1)}"'))
    if not chunks:
        raise ValueError("No Next.js flight chunks found in the HTML.")
    return "".join(chunks)


def extract_default_data(html: str) -> list[dict[str, Any]]:
    flight = decode_next_flight(html)
    candidates: list[list[dict[str, Any]]] = []

    for match in re.finditer(r'"defaultData":(\[)', flight):
        array_text = _read_balanced_json_value(flight, match.start(1))
        try:
            value = json.loads(array_text)
        except json.JSONDecodeError:
            continue
        if _looks_like_model_rows(value):
            candidates.append(value)

    if not candidates:
        raise ValueError("Could not find Artificial Analysis model rows in the page payload.")
    return max(candidates, key=len)


def _read_balanced_json_value(text: str, start: int) -> str:
    if start >= len(text) or text[start] not in "[{":
        raise ValueError("Balanced JSON scan must start at an object or array.")

    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char in "[{":
            depth += 1
        elif char in "]}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]

    raise ValueError("Could not find the end of a balanced JSON value.")


def _looks_like_model_rows(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    first = value[0]
    return (
        isinstance(first, dict)
        and ("short_name" in first or "name" in first)
        and ("slug" in first or "model_url" in first)
    )


@dataclass(frozen=True)
class ScoreSpec:
    column: str
    extractor: Callable[[dict[str, Any]], float | None]


def build_raw_scores_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    source_rows = list(rows)
    output_rows: list[dict[str, Any]] = []

    score_values_by_column: dict[str, list[float | None]] = {
        spec.column: [spec.extractor(row) for row in source_rows] for spec in SCORE_SPECS
    }
    ranks_by_column = {
        column: _rank_descending(values) for column, values in score_values_by_column.items()
    }

    for index, row in enumerate(source_rows):
        model = _model_name(row)
        is_reasoning = bool(row.get("reasoning_model"))
        output: dict[str, Any] = {
            "model_key": f"{model} [R]" if is_reasoning else model,
            "model": model,
            "is_reasoning": "true" if is_reasoning else "false",
        }

        for spec in SCORE_SPECS:
            output[spec.column] = _format_number(score_values_by_column[spec.column][index])

        for spec in SCORE_SPECS:
            output[f"{spec.column}_rank"] = ranks_by_column[spec.column][index]

        output_rows.append(output)

    return output_rows


def build_models_metadata_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in rows:
        creator = _dict_or_empty(row.get("model_creators"))
        cost = _dict_or_empty(row.get("intelligence_index_cost"))
        output.append(
            {
                "Model Name": _model_name(row),
                "Model Slug": row.get("slug") or "",
                "Release Date": row.get("release_date") or "",
                "Model Creator Name": creator.get("name") or "",
                "Artificial Analysis Intelligence Index": _format_number(row.get("intelligence_index")),
                "Artificial Analysis Coding Index": _format_number(row.get("coding_index")),
                "Artificial Analysis Agentic Index": _format_number(row.get("agentic_index")),
                "Intelligence Index Cost (USD)": _format_number(cost.get("total_cost")),
            }
        )
    return output


def write_raw_scores_csv(rows: list[dict[str, Any]], path: Path) -> None:
    fieldnames = (
        ["model_key", "model", "is_reasoning"]
        + [spec.column for spec in SCORE_SPECS]
        + [f"{spec.column}_rank" for spec in SCORE_SPECS]
    )
    _write_dict_rows(path, fieldnames, rows)


def write_models_metadata_csv(rows: list[dict[str, Any]], path: Path) -> None:
    fieldnames = [
        "Model Name",
        "Model Slug",
        "Release Date",
        "Model Creator Name",
        "Artificial Analysis Intelligence Index",
        "Artificial Analysis Coding Index",
        "Artificial Analysis Agentic Index",
        "Intelligence Index Cost (USD)",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Artificial Analysis Model Benchmarks Data", *[""] * (len(fieldnames) - 1)])
        writer.writerow([""] * len(fieldnames))
        writer.writerow(fieldnames)
        for row in rows:
            writer.writerow([row.get(field, "") for field in fieldnames])


def _write_dict_rows(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _rank_descending(values: list[float | None]) -> list[int | str]:
    indexed_values = [(index, value) for index, value in enumerate(values) if value is not None]
    indexed_values.sort(key=lambda item: item[1], reverse=True)

    ranks: list[int | str] = [""] * len(values)
    previous_value: float | None = None
    current_rank = 0
    for position, (index, value) in enumerate(indexed_values, start=1):
        if previous_value is None or value != previous_value:
            current_rank = position
            previous_value = value
        ranks[index] = current_rank
    return ranks


def _model_name(row: dict[str, Any]) -> str:
    return str(row.get("short_name") or row.get("name") or row.get("slug") or "")


def _as_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _format_number(value: Any) -> float | str:
    number = _as_float(value)
    if number is None:
        return ""
    rounded = round(number, 4)
    return 0.0 if rounded == -0.0 else rounded


def _percent(row: dict[str, Any], key: str) -> float | None:
    value = _as_float(row.get(key))
    return None if value is None else value * 100


def _gdpval_score(row: dict[str, Any]) -> float | None:
    value = _as_float(row.get("gdpval"))
    return None if value is None else (value - 500) / 2000 * 100


def _omniscience_total_percent(row: dict[str, Any], key: str) -> float | None:
    breakdown = _dict_or_empty(row.get("omniscience_breakdown"))
    total = _dict_or_empty(breakdown.get("total"))
    value = _as_float(total.get(key))
    return None if value is None else value * 100


def _dict_or_empty(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


SCORE_SPECS = [
    ScoreSpec("GDPval-AA", _gdpval_score),
    ScoreSpec("Terminal-Bench Hard", lambda row: _percent(row, "terminalbench_hard")),
    ScoreSpec("τ²-Bench Telecom", lambda row: _percent(row, "tau2")),
    ScoreSpec("AA-LCR", lambda row: _percent(row, "lcr")),
    ScoreSpec("AA-Omniscience Accuracy", lambda row: _omniscience_total_percent(row, "accuracy")),
    ScoreSpec(
        "AA-Omniscience Non-Hallucination Rate",
        lambda row: _omniscience_total_percent(row, "non_hallucination_rate"),
    ),
    ScoreSpec("Humanity's Last Exam", lambda row: _percent(row, "hle")),
    ScoreSpec("GPQA Diamond", lambda row: _percent(row, "gpqa")),
    ScoreSpec("SciCode", lambda row: _percent(row, "scicode")),
    ScoreSpec("IFBench", lambda row: _percent(row, "ifbench")),
    ScoreSpec("CritPt", lambda row: _percent(row, "critpt")),
    ScoreSpec("APEX-Agents-AA", lambda row: _percent(row, "apex_agents")),
    ScoreSpec("ITBench-AA", lambda row: _percent(row, "it_bench_sre")),
    ScoreSpec("MMMU-Pro", lambda row: _percent(row, "mmmu_pro")),
    ScoreSpec("LiveCodeBench", lambda row: _percent(row, "livecodebench")),
    ScoreSpec("AIME 2025", lambda row: _percent(row, "aime25")),
]


def run(args: argparse.Namespace) -> tuple[Path, Path, int]:
    html = fetch_html(args.url, timeout=args.timeout)
    model_rows = extract_default_data(html)

    output_dir = Path(args.output_dir)
    metadata_path = output_dir / f"models-data_{args.date}.csv"
    raw_scores_path = output_dir / RAW_SCORES_FILENAME

    write_models_metadata_csv(build_models_metadata_rows(model_rows), metadata_path)
    write_raw_scores_csv(build_raw_scores_rows(model_rows), raw_scores_path)

    if args.raw_json:
        raw_path = Path(args.raw_json)
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_text(json.dumps(model_rows, ensure_ascii=False, indent=2), encoding="utf-8")

    return metadata_path, raw_scores_path, len(model_rows)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch the latest Artificial Analysis language-model benchmark data.",
    )
    parser.add_argument("--url", default=SOURCE_URL, help="Artificial Analysis page to scrape.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for CSV outputs.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Date suffix for models-data CSV.")
    parser.add_argument("--timeout", type=float, default=30, help="HTTP timeout in seconds.")
    parser.add_argument("--raw-json", help="Optional path to write the extracted model payload as JSON.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        metadata_path, raw_scores_path, row_count = run(args)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Fetched {row_count} model rows from Artificial Analysis.")
    print(f"Wrote {metadata_path}")
    print(f"Wrote {raw_scores_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
