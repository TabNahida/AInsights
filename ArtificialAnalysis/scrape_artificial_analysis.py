"""Scrape Artificial Analysis language-model benchmark data.

Artificial Analysis is rendered by Next.js. Older pages embed rows directly in
the React flight payload; current pages reference an authenticated, encrypted
model manifest from that payload. This scraper supports both forms without
driving a browser.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import math
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


SOURCE_URL = "https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index"
MODELS_URL = "https://artificialanalysis.ai/models"
AA_BASE_URL = "https://artificialanalysis.ai"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent
DEFAULT_LOGO_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "docs" / "assets" / "logos"
RAW_SCORES_FILENAME = "artificialanalysis_raw_scores_wide.csv"
MAX_MANIFEST_CIPHERTEXT_BYTES = 8 * 1024 * 1024
MAX_MANIFEST_JSON_BYTES = 32 * 1024 * 1024

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


@dataclass(frozen=True)
class DataManifest:
    path: str
    key: str


class RefreshUnavailableError(RuntimeError):
    """The remote snapshot was unavailable or failed content validation."""


def extract_data_manifests(html: str) -> list[DataManifest]:
    """Extract encrypted data-manifest references from a Next.js flight payload."""

    flight = decode_next_flight(html)
    manifests: list[DataManifest] = []
    for match in re.finditer(r'"manifest"\s*:\s*(\{)', flight):
        object_text = _read_balanced_json_value(flight, match.start(1))
        try:
            value = json.loads(object_text)
        except json.JSONDecodeError:
            continue
        if not isinstance(value, dict):
            continue
        path = value.get("path")
        key = value.get("key")
        if isinstance(path, str) and isinstance(key, str):
            manifests.append(DataManifest(path=path, key=key))
    if not manifests:
        raise ValueError("Could not find an Artificial Analysis data manifest in the page payload.")
    return manifests


def _validated_manifest_location(
    manifest: DataManifest,
    page_url: str,
) -> tuple[str, bytes]:
    if re.fullmatch(r"[0-9a-fA-F]{64}", manifest.key) is None:
        raise ValueError("Artificial Analysis manifest key must be exactly 64 hexadecimal characters.")

    page = urlparse(page_url)
    manifest_url = urljoin(page_url, manifest.path)
    target = urlparse(manifest_url)
    page_origin = (page.scheme.lower(), (page.hostname or "").lower(), page.port or 443)
    target_origin = (
        target.scheme.lower(),
        (target.hostname or "").lower(),
        target.port or 443,
    )
    expected_origin = ("https", "artificialanalysis.ai", 443)
    if page_origin != expected_origin or target_origin != page_origin:
        raise ValueError(
            "Artificial Analysis manifest URL must use HTTPS on the same "
            "artificialanalysis.ai origin."
        )
    if target.username or target.password or target.fragment:
        raise ValueError("Artificial Analysis manifest URL contains forbidden URL components.")

    return manifest_url, bytes.fromhex(manifest.key)


def fetch_manifest_payload(
    manifest: DataManifest,
    page_url: str,
    timeout: float = 30,
) -> dict[str, Any]:
    """Fetch, authenticate, decrypt, and decode one encrypted AA manifest."""

    manifest_url, key = _validated_manifest_location(manifest, page_url)
    request = Request(manifest_url, headers=_http_headers())
    with urlopen(request, timeout=timeout) as response:
        headers = getattr(response, "headers", None)
        content_length = headers.get("Content-Length") if headers is not None else None
        if content_length:
            try:
                declared_length = int(content_length)
            except (TypeError, ValueError):
                declared_length = 0
            if declared_length > MAX_MANIFEST_CIPHERTEXT_BYTES:
                raise ValueError(
                    "Artificial Analysis manifest ciphertext exceeds the allowed size limit."
                )
        ciphertext = response.read(MAX_MANIFEST_CIPHERTEXT_BYTES + 1)

    if len(ciphertext) > MAX_MANIFEST_CIPHERTEXT_BYTES:
        raise ValueError("Artificial Analysis manifest ciphertext exceeds the allowed size limit.")

    iv = hashlib.sha256(key).digest()[:12]
    try:
        compressed = AESGCM(key).decrypt(iv, ciphertext, None)
    except InvalidTag as exc:
        raise ValueError("Artificial Analysis manifest failed AES-GCM authentication.") from exc

    try:
        with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as archive:
            payload_bytes = archive.read(MAX_MANIFEST_JSON_BYTES + 1)
    except (OSError, EOFError) as exc:
        raise ValueError("Artificial Analysis manifest is not valid gzip data.") from exc
    if len(payload_bytes) > MAX_MANIFEST_JSON_BYTES:
        raise ValueError("Artificial Analysis manifest JSON exceeds the allowed size limit.")

    try:
        payload = json.loads(payload_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Artificial Analysis manifest does not contain valid JSON.") from exc
    if not isinstance(payload, dict):
        raise ValueError("Artificial Analysis manifest JSON must be an object.")
    return payload


def fetch_rich_manifest_model_rows(
    html: str,
    page_url: str,
    timeout: float = 30,
) -> list[dict[str, Any]]:
    """Decrypt every page manifest and select the largest rich model payload."""

    candidates: list[list[dict[str, Any]]] = []
    errors: list[str] = []
    for manifest in extract_data_manifests(html):
        try:
            payload = fetch_manifest_payload(manifest, page_url, timeout=timeout)
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
            continue
        rows = payload.get("models")
        if _looks_like_rich_model_rows(rows):
            candidates.append(rows)

    if not candidates:
        detail = f" Manifest errors: {'; '.join(errors)}" if errors else ""
        raise ValueError(
            "Could not find rich Artificial Analysis model rows in the encrypted manifests."
            + detail
        )
    return max(candidates, key=len)


def _looks_like_rich_model_rows(value: Any) -> bool:
    if not isinstance(value, list) or len(value) < MINIMUM_MODEL_ROWS:
        return False
    required = {"slug", "shortName", "creator", "contextWindowTokens"}
    return all(isinstance(row, dict) and required <= row.keys() for row in value)


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
        creator = _dict_or_empty(row.get("model_creators"))
        cost = _dict_or_empty(row.get("intelligence_index_cost"))
        timescale = _dict_or_empty(row.get("timescaleData"))
        creator_logo_url = _absolute_aa_url(creator.get("logo_url"))
        creator_logo_small_url = _absolute_aa_url(creator.get("logo_small_url"))
        output: dict[str, Any] = {
            "model_key": f"{model} [R]" if is_reasoning else model,
            "model": model,
            "is_reasoning": "true" if is_reasoning else "false",
            "slug": row.get("slug") or "",
            "creator": creator.get("name") or "",
            "creator_slug": creator.get("slug") or "",
            "creator_color": creator.get("color") or "",
            "creator_logo_url": creator_logo_url,
            "creator_logo_small_url": creator_logo_small_url or creator_logo_url,
            "release_date": row.get("release_date") or "",
            "model_url": row.get("model_url") or "",
            **{
                column: _format_bool(row.get(column))
                for column in MODALITY_COLUMNS
            },
            "context_window_tokens": _format_number(row.get("context_window_tokens")),
            "open_source_categorization": row.get("open_source_categorization") or "",
            "median_output_speed": _format_number(timescale.get("median_output_speed")),
            "Cache Hit Price Per 1M Tokens (USD)": _format_number(row.get("cache_hit_price")),
            "Input Price Per 1M Tokens (USD)": _format_number(row.get("price_1m_input_tokens")),
            "Output Price Per 1M Tokens (USD)": _format_number(row.get("price_1m_output_tokens")),
            "AA Intelligence Index": _format_number(row.get("intelligence_index")),
            "AA Coding Index": _format_number(row.get("coding_index")),
            "AA Agentic Index": _format_number(row.get("agentic_index")),
            "AA Intelligence Index Cost (USD)": _format_number(cost.get("total_cost")),
            "AA Intelligence Index Input Cost (USD)": _format_number(cost.get("input_cost")),
            "AA Intelligence Index Output Cost (USD)": _format_number(cost.get("output_cost")),
            "AA Intelligence Index Reasoning Cost (USD)": _format_number(cost.get("reasoning_cost")),
            "AA Intelligence Index Answer Cost (USD)": _format_number(cost.get("answer_cost")),
        }

        for spec in SCORE_SPECS:
            output[spec.column] = _format_number(score_values_by_column[spec.column][index])

        for spec in SCORE_SPECS:
            output[f"{spec.column}_rank"] = ranks_by_column[spec.column][index]

        output_rows.append(output)

    return output_rows


def write_raw_scores_csv(rows: list[dict[str, Any]], path: Path) -> None:
    _write_dict_rows(path, raw_scores_fieldnames(), rows)


def download_creator_logos(
    rows: Iterable[dict[str, Any]],
    output_dir: Path,
    timeout: float = 30,
    overwrite: bool = False,
) -> int:
    """Download provider logos referenced by the AA payload into docs assets."""

    logo_urls: dict[str, str] = {}
    for row in rows:
        creator = _dict_or_empty(row.get("model_creators"))
        for key in ("logo_small_url", "logo_url"):
            url = _absolute_aa_url(creator.get(key))
            if not url:
                continue
            filename = _logo_filename(url)
            if filename:
                logo_urls[filename] = url
                break

    output_dir.mkdir(parents=True, exist_ok=True)
    downloaded = 0
    for filename, url in sorted(logo_urls.items()):
        path = output_dir / filename
        if path.exists() and not overwrite:
            continue
        request = Request(url, headers=_http_headers())
        with urlopen(request, timeout=timeout) as response:
            path.write_bytes(response.read())
        downloaded += 1
    return downloaded


def _write_dict_rows(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _write_text_atomically(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    os.close(descriptor)
    temporary_path = Path(temporary_name)
    try:
        temporary_path.write_text(text, encoding="utf-8")
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


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


def _format_bool(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return ""


def _percent(row: dict[str, Any], key: str) -> float | None:
    value = _as_float(row.get(key))
    return None if value is None else value * 100


def _gdpval_score(row: dict[str, Any], key: str = "gdpval") -> float | None:
    value = _as_float(row.get(key))
    return None if value is None else (value - 500) / 2000 * 100


def _omniscience_total_percent(row: dict[str, Any], key: str) -> float | None:
    breakdown = _dict_or_empty(row.get("omniscience_breakdown"))
    total = _dict_or_empty(breakdown.get("total"))
    value = _as_float(total.get(key))
    return None if value is None else value * 100


def _dict_or_empty(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _absolute_aa_url(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""
    return urljoin(AA_BASE_URL, value.strip())


def _logo_filename(url: str) -> str:
    parsed = urlparse(url)
    filename = Path(parsed.path).name
    if not filename or "." not in filename:
        return ""
    return filename


def _http_headers() -> dict[str, str]:
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }


SCORE_SPECS = [
    ScoreSpec("GDPval-AA v2", lambda row: _gdpval_score(row, "gdpval_v2")),
    ScoreSpec("τ³-Banking", lambda row: _percent(row, "tau_banking")),
    ScoreSpec("Terminal-Bench v2.1", lambda row: _percent(row, "terminalbench_v2_1")),
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


RAW_METADATA_COLUMNS = [
    "model_key",
    "model",
    "is_reasoning",
    "slug",
    "creator",
    "creator_slug",
    "creator_color",
    "creator_logo_url",
    "creator_logo_small_url",
    "release_date",
    "model_url",
    "input_modality_text",
    "input_modality_image",
    "input_modality_speech",
    "input_modality_video",
    "output_modality_text",
    "output_modality_image",
    "output_modality_speech",
    "output_modality_video",
    "context_window_tokens",
    "open_source_categorization",
    "median_output_speed",
    "Cache Hit Price Per 1M Tokens (USD)",
    "Input Price Per 1M Tokens (USD)",
    "Output Price Per 1M Tokens (USD)",
]

MODALITY_COLUMNS = [
    "input_modality_text",
    "input_modality_image",
    "input_modality_speech",
    "input_modality_video",
    "output_modality_text",
    "output_modality_image",
    "output_modality_speech",
    "output_modality_video",
]

AA_PRESET_COLUMNS = [
    "AA Intelligence Index",
    "AA Coding Index",
    "AA Agentic Index",
    "AA Intelligence Index Cost (USD)",
    "AA Intelligence Index Input Cost (USD)",
    "AA Intelligence Index Output Cost (USD)",
    "AA Intelligence Index Reasoning Cost (USD)",
    "AA Intelligence Index Answer Cost (USD)",
]


MINIMUM_MODEL_ROWS = 50
MINIMUM_INTELLIGENCE_INDEX_COVERAGE = 0.5
MINIMUM_CANDIDATE_ROW_RATIO = 0.8
MINIMUM_PRIOR_SLUG_OVERLAP = 0.7
MINIMUM_GUARDED_COLUMN_COVERAGE_RATIO = 0.8

# A disappearing benchmark score must be corroborated by its dedicated AA
# evaluation page before it can reduce the coverage baseline. Keep this list
# explicit: unknown schema changes still fail the ordinary coverage guard.
SCORE_WITHDRAWAL_SOURCES = {
    "scicode": ("SciCode", f"{AA_BASE_URL}/evaluations/scicode"),
}


MANIFEST_SCORE_KEYS = {
    "gdpval": "GDPval-AA",
    "gdpvalNormalized": "GDPval-AA",
    "tauBanking": "τ³-Banking",
    "terminalbenchV21": "Terminal-Bench v2.1",
    "terminalbenchHard": "Terminal-Bench Hard",
    "tau2": "τ²-Bench Telecom",
    "lcr": "AA-LCR",
    "hle": "Humanity's Last Exam",
    "gpqa": "GPQA Diamond",
    "scicode": "SciCode",
    "ifbench": "IFBench",
    "critpt": "CritPt",
    "apexAgents": "APEX-Agents-AA",
    "itBenchSre": "ITBench-AA",
    "itbenchSre": "ITBench-AA",
    "mmmuPro": "MMMU-Pro",
    "livecodebench": "LiveCodeBench",
    "aime25": "AIME 2025",
}

PRESERVE_EXPLICIT_NULL_COLUMNS = {
    "model_key",
    "model",
    "is_reasoning",
    "creator",
    "creator_slug",
    "creator_color",
    "creator_logo_url",
    "creator_logo_small_url",
    "release_date",
    *MODALITY_COLUMNS,
    "context_window_tokens",
    "open_source_categorization",
    "median_output_speed",
    "Cache Hit Price Per 1M Tokens (USD)",
    "Input Price Per 1M Tokens (USD)",
    "Output Price Per 1M Tokens (USD)",
}


def normalize_manifest_model_row(row: dict[str, Any]) -> dict[str, Any]:
    """Translate one rich camelCase manifest row to the legacy scraper schema."""

    normalized: dict[str, Any] = {}

    direct_keys = {
        "slug": "slug",
        "name": "name",
        "releaseDate": "release_date",
        "modelWeightsSourceUrl": "model_url",
        "isReasoning": "reasoning_model",
        "contextWindowTokens": "context_window_tokens",
        "cacheHitPrice": "cache_hit_price",
        "price1mInputTokens": "price_1m_input_tokens",
        "price1mOutputTokens": "price_1m_output_tokens",
        "intelligenceIndex": "intelligence_index",
        "agenticIndex": "agentic_index",
        "tauBanking": "tau_banking",
        "terminalbenchV21": "terminalbench_v2_1",
        "terminalbenchHard": "terminalbench_hard",
        "tau2": "tau2",
        "lcr": "lcr",
        "hle": "hle",
        "gpqa": "gpqa",
        "scicode": "scicode",
        "ifbench": "ifbench",
        "critpt": "critpt",
        "apexAgents": "apex_agents",
        "mmmuPro": "mmmu_pro",
        "livecodebench": "livecodebench",
        "aime25": "aime25",
        "inputModalityText": "input_modality_text",
        "inputModalityImage": "input_modality_image",
        "inputModalitySpeech": "input_modality_speech",
        "inputModalityVideo": "input_modality_video",
        "outputModalityText": "output_modality_text",
        "outputModalityImage": "output_modality_image",
        "outputModalitySpeech": "output_modality_speech",
        "outputModalityVideo": "output_modality_video",
    }
    for source_key, target_key in direct_keys.items():
        if source_key in row:
            normalized[target_key] = row[source_key]

    if "shortName" in row:
        normalized["short_name"] = row["shortName"]
    elif "name" in row:
        normalized["short_name"] = row["name"]

    creator = row.get("creator")
    if isinstance(creator, dict):
        logo = creator.get("logo")
        normalized["model_creators"] = {
            "name": creator.get("name"),
            "slug": creator.get("slug"),
            "color": creator.get("color"),
            "logo_url": logo,
            "logo_small_url": logo,
        }

    if "openSourceCategorization" in row:
        normalized["open_source_categorization"] = row["openSourceCategorization"]
    elif "isOpenWeights" in row:
        normalized["open_source_categorization"] = (
            "open-weights" if row["isOpenWeights"] is True else "proprietary"
        )

    timescale = row.get("timescaleData")
    if isinstance(timescale, dict) and "medianOutputSpeed" in timescale:
        normalized["timescaleData"] = {
            "median_output_speed": timescale["medianOutputSpeed"]
        }
    elif "medianCanonicalAnswerOutputSpeed" in row:
        normalized["timescaleData"] = {
            "median_output_speed": row["medianCanonicalAnswerOutputSpeed"]
        }

    if "gdpvalNormalized" in row:
        value = _as_float(row["gdpvalNormalized"])
        normalized["gdpval"] = None if value is None else value * 2000 + 500
    elif "gdpval" in row:
        normalized["gdpval"] = row["gdpval"]

    for source_key in ("itBenchSre", "itbenchSre"):
        if source_key in row:
            normalized["it_bench_sre"] = row[source_key]
            break

    omniscience = row.get("omniscienceBreakdown")
    if isinstance(omniscience, dict):
        total: dict[str, Any] = {}
        if "accuracy" in omniscience:
            total["accuracy"] = omniscience["accuracy"]
        if "hallucinationRate" in omniscience:
            rate = _as_float(omniscience["hallucinationRate"])
            total["non_hallucination_rate"] = None if rate is None else 1 - rate
        if total:
            normalized["omniscience_breakdown"] = {"total": total}

    cost = row.get("intelligenceIndexCost")
    if isinstance(cost, dict):
        normalized["intelligence_index_cost"] = {
            "total_cost": cost.get("total", cost.get("totalCost")),
            "input_cost": cost.get("input", cost.get("inputCost")),
            "output_cost": cost.get("output", cost.get("outputCost")),
            "reasoning_cost": cost.get("reasoning", cost.get("reasoningCost")),
            "answer_cost": cost.get("answer", cost.get("answerCost")),
        }

    return normalized


def _manifest_explicit_raw_columns(row: dict[str, Any]) -> set[str]:
    columns: set[str] = {"slug"}
    mapping = {
        "shortName": {"model", "model_key"},
        "name": {"model", "model_key"},
        "isReasoning": {"is_reasoning", "model_key"},
        "creator": {
            "creator",
            "creator_slug",
            "creator_color",
            "creator_logo_url",
            "creator_logo_small_url",
        },
        "releaseDate": {"release_date"},
        "modelWeightsSourceUrl": {"model_url"},
        "contextWindowTokens": {"context_window_tokens"},
        "openSourceCategorization": {"open_source_categorization"},
        "isOpenWeights": {"open_source_categorization"},
        "timescaleData": {"median_output_speed"},
        "medianCanonicalAnswerOutputSpeed": {"median_output_speed"},
        "cacheHitPrice": {"Cache Hit Price Per 1M Tokens (USD)"},
        "price1mInputTokens": {"Input Price Per 1M Tokens (USD)"},
        "price1mOutputTokens": {"Output Price Per 1M Tokens (USD)"},
        "intelligenceIndex": {"AA Intelligence Index"},
        "agenticIndex": {"AA Agentic Index"},
        "inputModalityText": {"input_modality_text"},
        "inputModalityImage": {"input_modality_image"},
        "inputModalitySpeech": {"input_modality_speech"},
        "inputModalityVideo": {"input_modality_video"},
        "outputModalityText": {"output_modality_text"},
        "outputModalityImage": {"output_modality_image"},
        "outputModalitySpeech": {"output_modality_speech"},
        "outputModalityVideo": {"output_modality_video"},
    }
    for source_key, raw_columns in mapping.items():
        if source_key in row:
            columns.update(raw_columns)

    if "intelligenceIndexCost" in row:
        columns.update(
            {
                "AA Intelligence Index Cost (USD)",
                "AA Intelligence Index Input Cost (USD)",
                "AA Intelligence Index Output Cost (USD)",
                "AA Intelligence Index Reasoning Cost (USD)",
                "AA Intelligence Index Answer Cost (USD)",
            }
        )

    for source_key, score_column in MANIFEST_SCORE_KEYS.items():
        if source_key in row:
            columns.add(score_column)
            columns.add(f"{score_column}_rank")

    breakdown = row.get("omniscienceBreakdown")
    if isinstance(breakdown, dict):
        if "accuracy" in breakdown:
            columns.update(
                {"AA-Omniscience Accuracy", "AA-Omniscience Accuracy_rank"}
            )
        if "hallucinationRate" in breakdown:
            columns.update(
                {
                    "AA-Omniscience Non-Hallucination Rate",
                    "AA-Omniscience Non-Hallucination Rate_rank",
                }
            )
    return columns


def merge_manifest_rows_with_prior(
    candidate_rows: list[dict[str, Any]],
    manifest_rows: list[dict[str, Any]],
    prior_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """Retain prior fields unavailable from the manifest without reviving old scores."""

    manifest_by_slug = {str(row.get("slug") or ""): row for row in manifest_rows}
    prior_by_slug = {row["slug"]: row for row in prior_rows}
    fieldnames = raw_scores_fieldnames()
    for candidate in candidate_rows:
        slug = str(candidate.get("slug") or "")
        prior = prior_by_slug.get(slug)
        manifest = manifest_by_slug.get(slug)
        if prior is None or manifest is None:
            continue
        explicit_columns = _manifest_explicit_raw_columns(manifest)
        for column in fieldnames:
            candidate_value = candidate.get(column)
            prior_value = prior.get(column)
            candidate_is_blank = (
                candidate_value is None or str(candidate_value).strip() == ""
            )
            prior_is_present = prior_value is not None and str(prior_value).strip() != ""
            preserve_explicit_null = column in PRESERVE_EXPLICIT_NULL_COLUMNS
            if column not in explicit_columns or (
                preserve_explicit_null and candidate_is_blank and prior_is_present
            ):
                candidate[column] = prior.get(column, "")
    return candidate_rows


def raw_scores_fieldnames() -> list[str]:
    return (
        RAW_METADATA_COLUMNS
        + AA_PRESET_COLUMNS
        + [spec.column for spec in SCORE_SPECS]
        + [f"{spec.column}_rank" for spec in SCORE_SPECS]
    )


def validate_raw_scores_csv(path: Path) -> list[dict[str, str]]:
    """Read and validate a complete Artificial Analysis CSV snapshot."""

    if not path.is_file():
        raise ValueError(f"Artificial Analysis snapshot does not exist: {path}")

    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        expected = raw_scores_fieldnames()
        if reader.fieldnames != expected:
            raise ValueError(
                "Artificial Analysis snapshot has an unexpected CSV schema "
                f"({len(reader.fieldnames or [])} columns; expected {len(expected)})."
            )
        rows = list(reader)

    if len(rows) < MINIMUM_MODEL_ROWS:
        raise ValueError(
            "Artificial Analysis snapshot is suspiciously small "
            f"({len(rows)} rows; expected at least {MINIMUM_MODEL_ROWS})."
        )

    numeric_columns = {
        "context_window_tokens",
        "median_output_speed",
        "Cache Hit Price Per 1M Tokens (USD)",
        "Input Price Per 1M Tokens (USD)",
        "Output Price Per 1M Tokens (USD)",
        *AA_PRESET_COLUMNS,
        *(spec.column for spec in SCORE_SPECS),
        *(f"{spec.column}_rank" for spec in SCORE_SPECS),
    }
    seen_slugs: set[str] = set()
    intelligence_index_count = 0
    for row_number, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(f"Artificial Analysis row {row_number} has extra CSV fields.")
        for column in ("model_key", "model", "slug"):
            if not str(row.get(column) or "").strip():
                raise ValueError(
                    f"Artificial Analysis row {row_number} has no {column!r} value."
                )

        slug = row["slug"].strip()
        if slug in seen_slugs:
            raise ValueError(f"Artificial Analysis snapshot has duplicate slug {slug!r}.")
        seen_slugs.add(slug)

        for column in MODALITY_COLUMNS + ["is_reasoning"]:
            value = str(row.get(column) or "").strip().lower()
            if value not in {"", "true", "false"}:
                raise ValueError(
                    f"Artificial Analysis row {row_number} has invalid {column!r} value {value!r}."
                )

        for column in numeric_columns:
            value = str(row.get(column) or "").strip()
            if value and _as_float(value) is None:
                raise ValueError(
                    f"Artificial Analysis row {row_number} has invalid numeric "
                    f"{column!r} value {value!r}."
                )

        if str(row.get("AA Intelligence Index") or "").strip():
            intelligence_index_count += 1

    minimum_index_rows = math.ceil(len(rows) * MINIMUM_INTELLIGENCE_INDEX_COVERAGE)
    if intelligence_index_count < minimum_index_rows:
        raise ValueError(
            "Artificial Analysis snapshot has insufficient Intelligence Index coverage "
            f"({intelligence_index_count}/{len(rows)} rows; expected at least "
            f"{minimum_index_rows})."
        )

    return rows


def _validate_candidate_against_prior(
    candidate_rows: list[dict[str, str]],
    prior_rows: list[dict[str, str]],
    *,
    confirmed_score_removals: dict[str, set[str]] | None = None,
) -> None:
    minimum_rows = math.ceil(len(prior_rows) * MINIMUM_CANDIDATE_ROW_RATIO)
    if len(candidate_rows) < minimum_rows:
        raise ValueError(
            "Artificial Analysis candidate lost too many rows "
            f"({len(candidate_rows)} versus {len(prior_rows)} previously; expected at least "
            f"{minimum_rows})."
        )

    prior_slugs = {row["slug"] for row in prior_rows}
    candidate_slugs = {row["slug"] for row in candidate_rows}
    overlap = len(prior_slugs & candidate_slugs)
    minimum_overlap = math.ceil(len(prior_slugs) * MINIMUM_PRIOR_SLUG_OVERLAP)
    if overlap < minimum_overlap:
        raise ValueError(
            "Artificial Analysis candidate retained too few prior model slugs "
            f"({overlap}/{len(prior_slugs)}; expected at least {minimum_overlap})."
        )

    guarded_columns = [
        "creator",
        "release_date",
        "Cache Hit Price Per 1M Tokens (USD)",
        "Input Price Per 1M Tokens (USD)",
        "Output Price Per 1M Tokens (USD)",
        "AA Intelligence Index",
        *[spec.column for spec in SCORE_SPECS],
    ]
    for column in guarded_columns:
        prior_scored_slugs = {
            row["slug"] for row in prior_rows if _has_value(row.get(column))
        }
        candidate_scored_slugs = {
            row["slug"] for row in candidate_rows if _has_value(row.get(column))
        }
        # Only previously scored rows still present with a blank score can be
        # withdrawn. Row loss and unrelated column loss retain their guards.
        confirmed = (confirmed_score_removals or {}).get(column, set())
        removed = confirmed & prior_scored_slugs & (candidate_slugs - candidate_scored_slugs)
        prior_count = len(prior_scored_slugs) - len(removed)
        if prior_count == 0:
            continue
        candidate_count = len(candidate_scored_slugs)
        minimum_count = math.ceil(
            prior_count * MINIMUM_GUARDED_COLUMN_COVERAGE_RATIO
        )
        if candidate_count < minimum_count:
            raise ValueError(
                f"Artificial Analysis candidate lost too much {column!r} coverage "
                f"({candidate_count} versus {prior_count} previously; expected at least "
                f"{minimum_count})."
            )


def _has_value(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def confirm_manifest_score_removals(
    candidate_rows: list[dict[str, Any]],
    manifest_rows: list[dict[str, Any]],
    prior_rows: list[dict[str, str]],
    *,
    timeout: float = 30,
) -> dict[str, set[str]]:
    """Corroborate large explicit-null score withdrawals against evaluation pages.

    A missing key, missing model, malformed value, or conflicting live score is
    not evidence of withdrawal. The complete model catalogue and every value of
    this metric must agree across both authenticated public manifests.
    """

    manifest_by_slug = {row["slug"]: row for row in manifest_rows}
    candidate_by_slug = {row["slug"]: row for row in candidate_rows}
    confirmed: dict[str, set[str]] = {}
    for source_key, (column, url) in SCORE_WITHDRAWAL_SOURCES.items():
        prior_scored = {row["slug"] for row in prior_rows if _has_value(row.get(column))}
        candidate_count = sum(_has_value(row.get(column)) for row in candidate_rows)
        if candidate_count >= math.ceil(
            len(prior_scored) * MINIMUM_GUARDED_COLUMN_COVERAGE_RATIO
        ):
            continue
        withdrawals = {
            slug
            for slug in prior_scored & candidate_by_slug.keys() & manifest_by_slug.keys()
            if not _has_value(candidate_by_slug[slug].get(column))
            and source_key in manifest_by_slug[slug]
            and manifest_by_slug[slug][source_key] is None
        }
        if not withdrawals:
            continue

        html = fetch_html(url, timeout=timeout)
        errors: list[str] = []
        for manifest in extract_data_manifests(html):
            try:
                payload = fetch_manifest_payload(manifest, url, timeout=timeout)
                rows = payload.get("models")
                if not isinstance(rows, list) or not all(
                    isinstance(row, dict)
                    and isinstance(row.get("slug"), str)
                    and source_key in row
                    for row in rows
                ):
                    raise ValueError("evaluation manifest has no complete score rows")
                by_slug = {row["slug"]: row for row in rows}
                if (
                    len(by_slug) != len(rows)
                    or len(manifest_by_slug) != len(manifest_rows)
                    or by_slug.keys() != manifest_by_slug.keys()
                ):
                    raise ValueError("evaluation model catalogue differs from the models page")
                for slug, source in manifest_by_slug.items():
                    if source_key not in source:
                        raise ValueError(f"models page omits {source_key!r} for {slug!r}")
                    primary, secondary = source[source_key], by_slug[slug][source_key]
                    if primary is None and secondary is None:
                        continue
                    primary_number, secondary_number = _as_float(primary), _as_float(secondary)
                    if (
                        primary_number is None
                        or secondary_number is None
                        or not math.isclose(primary_number, secondary_number, rel_tol=1e-12)
                    ):
                        raise ValueError(f"evaluation score disagrees for {slug!r}")
                confirmed[column] = withdrawals
                break
            except (OSError, ValueError) as exc:
                errors.append(str(exc))
        else:
            raise ValueError(
                f"Could not corroborate {column!r} score withdrawals at {url}: "
                + "; ".join(errors)
            )
    return confirmed


def write_raw_scores_csv_atomically(
    rows: list[dict[str, Any]],
    path: Path,
    *,
    confirmed_score_removals: dict[str, set[str]] | None = None,
) -> None:
    """Validate a candidate snapshot before atomically replacing the current CSV."""

    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    os.close(descriptor)
    temporary_path = Path(temporary_name)
    try:
        write_raw_scores_csv(rows, temporary_path)
        candidate_rows = validate_raw_scores_csv(temporary_path)

        if path.exists():
            try:
                prior_rows = validate_raw_scores_csv(path)
            except (OSError, ValueError, csv.Error):
                prior_rows = []
            if prior_rows:
                _validate_candidate_against_prior(
                    candidate_rows,
                    prior_rows,
                    confirmed_score_removals=confirmed_score_removals,
                )

        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def _emit_warning(message: str) -> None:
    print(f"warning: {message}", file=sys.stderr)
    if os.environ.get("GITHUB_ACTIONS") == "true":
        escaped = message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        print(f"::warning title=Artificial Analysis refresh::{escaped}", file=sys.stderr)


def run(args: argparse.Namespace) -> tuple[Path, int, int]:
    output_dir = Path(args.output_dir)
    raw_scores_path = output_dir / RAW_SCORES_FILENAME

    manifest_rows: list[dict[str, Any]] | None = None
    model_rows: list[dict[str, Any]] | None = None
    manifest_error: Exception | None = None
    models_html: str | None = None
    models_url = getattr(args, "models_url", MODELS_URL)
    try:
        models_html = fetch_html(models_url, timeout=args.timeout)
        manifest_rows = fetch_rich_manifest_model_rows(
            models_html,
            models_url,
            timeout=args.timeout,
        )
        model_rows = [normalize_manifest_model_row(row) for row in manifest_rows]
    except (OSError, ValueError) as exc:
        manifest_error = exc

    if model_rows is not None and manifest_rows is not None:
        raw_score_rows = build_raw_scores_rows(model_rows)
        prior_rows = []
        if raw_scores_path.exists():
            try:
                prior_rows = validate_raw_scores_csv(raw_scores_path)
            except (OSError, ValueError, csv.Error):
                prior_rows = []
            if prior_rows:
                raw_score_rows = merge_manifest_rows_with_prior(
                    raw_score_rows,
                    manifest_rows,
                    prior_rows,
                )
        try:
            confirmed_removals = confirm_manifest_score_removals(
                raw_score_rows, manifest_rows, prior_rows, timeout=args.timeout
            )
        except (OSError, ValueError) as exc:
            manifest_error = exc
            manifest_rows = None
            model_rows = None
        else:
            try:
                write_raw_scores_csv_atomically(
                    raw_score_rows,
                    raw_scores_path,
                    confirmed_score_removals=confirmed_removals,
                )
            except ValueError as exc:
                manifest_error = exc
                manifest_rows = None
                model_rows = None
            else:
                for column, slugs in confirmed_removals.items():
                    _emit_warning(
                        f"{column}: {len(slugs)} previously published scores are now null "
                        "on both the models and dedicated evaluation pages; cleared those "
                        "scores and ranks after corroborating the complete live catalogue."
                    )

    if model_rows is None:
        try:
            legacy_html = (
                models_html
                if models_html is not None and models_url == args.url
                else fetch_html(args.url, timeout=args.timeout)
            )
            model_rows = extract_default_data(legacy_html)
            if len(model_rows) < MINIMUM_MODEL_ROWS:
                raise ValueError(
                    "Legacy Artificial Analysis payload contains too few model rows "
                    f"({len(model_rows)}; expected at least {MINIMUM_MODEL_ROWS})."
                )
        except (OSError, ValueError) as exc:
            raise RefreshUnavailableError(
                "Could not load Artificial Analysis model rows from either encrypted "
                f"model manifests ({manifest_error}) or the legacy payload ({exc})."
            ) from exc

        try:
            write_raw_scores_csv_atomically(
                build_raw_scores_rows(model_rows),
                raw_scores_path,
            )
        except ValueError as exc:
            raise RefreshUnavailableError(
                f"Legacy Artificial Analysis candidate failed validation: {exc}"
            ) from exc

    if args.raw_json:
        _write_text_atomically(
            Path(args.raw_json),
            json.dumps(model_rows, ensure_ascii=False, indent=2),
        )

    logo_count = 0
    if not args.skip_logos:
        try:
            logo_count = download_creator_logos(
                model_rows,
                Path(args.logo_output_dir),
                timeout=args.timeout,
                overwrite=args.refresh_logos,
            )
        except Exception as exc:
            _emit_warning(f"Could not refresh provider logos: {exc}")

    return raw_scores_path, len(model_rows), logo_count


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch the latest Artificial Analysis language-model benchmark data.",
    )
    parser.add_argument("--url", default=SOURCE_URL, help="Artificial Analysis page to scrape.")
    parser.add_argument(
        "--models-url",
        default=MODELS_URL,
        help="Artificial Analysis models page containing the encrypted rich-data manifest.",
    )
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for CSV outputs.")
    parser.add_argument("--timeout", type=float, default=30, help="HTTP timeout in seconds.")
    parser.add_argument("--raw-json", help="Optional path to write the extracted model payload as JSON.")
    parser.add_argument(
        "--logo-output-dir",
        default=str(DEFAULT_LOGO_OUTPUT_DIR),
        help="Directory where AA provider logo assets should be downloaded.",
    )
    parser.add_argument("--skip-logos", action="store_true", help="Do not download provider logo assets.")
    parser.add_argument("--refresh-logos", action="store_true", help="Overwrite existing provider logo assets.")
    parser.add_argument(
        "--allow-stale",
        action="store_true",
        help=(
            "Keep a validated existing CSV and return success if the live Artificial Analysis "
            "refresh fails. By default refresh failures are fatal."
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        raw_scores_path, row_count, logo_count = run(args)
    except RefreshUnavailableError as exc:
        raw_scores_path = Path(args.output_dir) / RAW_SCORES_FILENAME
        if args.allow_stale:
            try:
                stale_rows = validate_raw_scores_csv(raw_scores_path)
            except Exception as stale_exc:
                print(
                    f"error: Artificial Analysis refresh failed ({exc}); the existing snapshot "
                    f"is not a valid fallback ({stale_exc}).",
                    file=sys.stderr,
                )
                return 1
            _emit_warning(
                f"Artificial Analysis refresh failed ({exc}); keeping the validated prior "
                f"snapshot at {raw_scores_path} ({len(stale_rows)} rows)."
            )
            return 0
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Fetched {row_count} model rows from Artificial Analysis.")
    print(f"Wrote {raw_scores_path}")
    if not args.skip_logos:
        print(f"Downloaded {logo_count} provider logo assets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
