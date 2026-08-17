"""Discover benchmark-bearing model cards published by official Hugging Face orgs.

The benchmark collector has curated source specifications for models that need
special score semantics. This manifest complements those specifications: it
lets the daily update notice a newly published Qwen, GLM, Kimi, or DeepSeek
generation before somebody adds a hand-written source entry for it.

Only first-party repositories are considered. Quantized, distilled, and base
weight variants are excluded because their cards commonly repeat a parent
model's table and would otherwise duplicate evidence.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from http.client import IncompleteRead
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_JSON = PROJECT_ROOT / "data" / "benchmarks" / "official_model_cards.json"
HF_MODELS_API_URL = "https://huggingface.co/api/models"


@dataclass(frozen=True)
class VendorConfig:
    id: str
    organization: str
    include_pattern: str
    max_models: int = 12


OFFICIAL_VENDORS = (
    VendorConfig("qwen", "Qwen", r"^Qwen\d"),
    VendorConfig("glm", "zai-org", r"^GLM[-_.]?\d"),
    VendorConfig("kimi", "moonshotai", r"^Kimi[-_.]?K\d"),
    VendorConfig("deepseek", "deepseek-ai", r"^DeepSeek[-_.]?(?:V|R)\d"),
)

DERIVATIVE_MODEL_RE = re.compile(
    r"(?:^|[-_.])(?:"
    r"awq|bnb|compressed|distill|dspark|fp\d+|gguf|gptq|int\d+|mlx|quant(?:ized)?|base"
    r")(?:$|[-_.])",
    re.IGNORECASE,
)


def fetch_json(url: str, timeout: float = 30) -> Any:
    request = Request(
        url,
        headers={
            "User-Agent": "AInsights official-model-card discovery/1.0",
            "Accept": "application/json",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def vendor_api_url(vendor: VendorConfig, limit: int = 100) -> str:
    query = urlencode(
        {
            "author": vendor.organization,
            "sort": "createdAt",
            "direction": "-1",
            "limit": limit,
            "full": "true",
        }
    )
    return f"{HF_MODELS_API_URL}?{query}"


def discover_vendor_models(
    vendor: VendorConfig,
    *,
    timeout: float = 30,
    fetcher: Callable[[str, float], Any] = fetch_json,
) -> list[dict[str, Any]]:
    payload = fetcher(vendor_api_url(vendor), timeout)
    if not isinstance(payload, list):
        raise ValueError(f"Hugging Face returned a non-list payload for {vendor.organization}")

    models: list[dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict) or item.get("private") is True:
            continue
        model_id = str(item.get("id") or item.get("modelId") or "").strip()
        expected_prefix = f"{vendor.organization}/"
        if not model_id.startswith(expected_prefix):
            continue
        name = model_id[len(expected_prefix) :]
        pipeline_tag = str(item.get("pipeline_tag") or "")
        if not _is_eligible_model(vendor, name, pipeline_tag):
            continue
        siblings = item.get("siblings") or []
        filenames = {
            str(sibling.get("rfilename") or "")
            for sibling in siblings
            if isinstance(sibling, dict)
        }
        if "README.md" not in filenames:
            continue
        entry = _manifest_entry(vendor, item, model_id, name)
        if not _is_valid_manifest_entry(vendor, entry):
            raise ValueError(
                f"Hugging Face returned an invalid manifest entry for {model_id}"
            )
        models.append(entry)

    models.sort(
        key=lambda model: (str(model.get("createdAt") or ""), str(model["modelId"])),
        reverse=True,
    )
    return models[: vendor.max_models]


def _is_eligible_model(vendor: VendorConfig, name: str, pipeline_tag: str) -> bool:
    if not re.search(vendor.include_pattern, name, re.IGNORECASE):
        return False
    if DERIVATIVE_MODEL_RE.search(name):
        return False
    if pipeline_tag and pipeline_tag not in {"text-generation", "image-text-to-text"}:
        return False
    if vendor.id == "deepseek" and re.search(r"(?:qwen|llama)", name, re.IGNORECASE):
        return False
    return True


def _manifest_entry(
    vendor: VendorConfig,
    item: dict[str, Any],
    model_id: str,
    name: str,
) -> dict[str, Any]:
    revision = str(item.get("sha") or "").strip()
    revision_path = revision or "main"
    aliases = _model_aliases(model_id, name)
    tags = sorted(
        {
            str(tag)
            for tag in item.get("tags") or []
            if isinstance(tag, str)
            and (
                tag == "eval-results"
                or tag.startswith("license:")
                or tag.startswith("base_model:")
            )
        }
    )
    return {
        "vendor": vendor.id,
        "organization": vendor.organization,
        "modelId": model_id,
        "name": name,
        "displayName": aliases[0],
        "url": f"https://huggingface.co/{model_id}",
        "rawUrl": f"https://huggingface.co/{model_id}/raw/{revision_path}/README.md",
        "createdAt": str(item.get("createdAt") or ""),
        "lastModified": str(item.get("lastModified") or ""),
        "revision": revision,
        "pipelineTag": str(item.get("pipeline_tag") or ""),
        "tags": tags,
        "aliases": aliases,
    }


def _model_aliases(model_id: str, name: str) -> list[str]:
    display_name = name
    if name.startswith("Qwen"):
        display_name = re.sub(r"^(Qwen\d+(?:\.\d+)*?)-(.+)$", r"\1 \2", name)
    elif name.startswith("Kimi-") or name.startswith("DeepSeek-"):
        display_name = name.replace("-", " ")

    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    spaced = re.sub(r"[-_.]+", " ", name).strip()
    aliases: list[str] = []
    for alias in (display_name, name, model_id, spaced, slug):
        if alias and alias not in aliases:
            aliases.append(alias)
    return aliases


def _is_valid_manifest_entry(vendor: VendorConfig, model: dict[str, Any]) -> bool:
    """Return whether a persisted card is still scoped to its declared HF org.

    The manifest is repository input on later runs, so failed refreshes must not
    blindly preserve URLs or organization fields that were edited or corrupted
    after discovery.
    """

    if model.get("vendor") != vendor.id:
        return False
    if model.get("organization") != vendor.organization:
        return False

    name = str(model.get("name") or "")
    model_id = str(model.get("modelId") or "")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name):
        return False
    if model_id != f"{vendor.organization}/{name}":
        return False
    if not _is_eligible_model(
        vendor,
        name,
        str(model.get("pipelineTag") or ""),
    ):
        return False

    revision = str(model.get("revision") or "")
    if revision and not re.fullmatch(r"[A-Za-z0-9._-]+", revision):
        return False
    revision_path = revision or "main"
    return (
        model.get("url") == f"https://huggingface.co/{model_id}"
        and model.get("rawUrl")
        == f"https://huggingface.co/{model_id}/raw/{revision_path}/README.md"
    )


def discover_manifest(
    previous: dict[str, Any] | None = None,
    *,
    timeout: float = 30,
    fetcher: Callable[[str, float], Any] = fetch_json,
) -> tuple[dict[str, Any], dict[str, str]]:
    previous = previous or {}
    vendors_by_id = {vendor.id: vendor for vendor in OFFICIAL_VENDORS}
    previous_models = []
    for model in previous.get("models", []):
        if not isinstance(model, dict):
            continue
        vendor = vendors_by_id.get(str(model.get("vendor") or ""))
        if vendor is None:
            continue
        if _is_valid_manifest_entry(vendor, model):
            previous_models.append(model)
    previous_by_vendor: dict[str, list[dict[str, Any]]] = {}
    for model in previous_models:
        previous_by_vendor.setdefault(str(model.get("vendor") or ""), []).append(model)

    merged_by_id: dict[str, dict[str, Any]] = {}
    statuses: dict[str, str] = {}
    for vendor in OFFICIAL_VENDORS:
        try:
            discovered = discover_vendor_models(
                vendor,
                timeout=timeout,
                fetcher=fetcher,
            )
        except (
            HTTPError,
            URLError,
            TimeoutError,
            OSError,
            IncompleteRead,
            json.JSONDecodeError,
            ValueError,
        ) as exc:
            preserved = len(previous_by_vendor.get(vendor.id, []))
            statuses[vendor.id] = (
                f"preserved {preserved}; refresh blocked: {exc.__class__.__name__}"
            )
            selected = previous_by_vendor.get(vendor.id, [])
        else:
            # A successful scan is authoritative for this vendor. Keeping older
            # entries here would make deleted, renamed, or aged-out cards grow
            # without bound across daily refreshes.
            selected = discovered
            statuses[vendor.id] = f"refreshed; discovered {len(discovered)}"

        for model in selected:
            merged_by_id[str(model["modelId"])] = model

    models = sorted(
        merged_by_id.values(),
        key=lambda model: (
            str(model.get("vendor") or ""),
            str(model.get("createdAt") or ""),
            str(model.get("modelId") or ""),
        ),
        reverse=True,
    )
    if not models:
        raise RuntimeError("No official model cards were discovered and no prior manifest exists")

    manifest = {
        "version": 1,
        "vendors": [
            {
                "id": vendor.id,
                "organization": vendor.organization,
                "includePattern": vendor.include_pattern,
                "maxModelsPerScan": vendor.max_models,
            }
            for vendor in OFFICIAL_VENDORS
        ],
        "models": models,
    }
    return manifest, statuses


def load_previous_manifest(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def write_manifest(path: Path, timeout: float = 30) -> tuple[dict[str, Any], dict[str, str]]:
    manifest, statuses = discover_manifest(
        load_previous_manifest(path),
        timeout=timeout,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest, statuses


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Discover official Qwen, GLM, Kimi, and DeepSeek model cards."
    )
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--timeout", type=float, default=30)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        manifest, statuses = write_manifest(Path(args.output_json), timeout=args.timeout)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    details = "; ".join(f"{vendor}: {status}" for vendor, status in statuses.items())
    print(f"Wrote {args.output_json} with {len(manifest['models'])} official cards ({details}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
