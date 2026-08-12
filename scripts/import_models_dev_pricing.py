#!/usr/bin/env python3
"""Expand the provider-pricing catalogue from a pinned Models.dev snapshot.

The importer intentionally treats Models.dev as a community catalogue, not as
an official price oracle.  It imports only provider rows that publish positive
input and output token rates.  Subscription/credit/call-plan providers are
excluded here because their zero-valued TOML costs are quota sentinels rather
than free-token prices; those plans are maintained as explicit, non-comparable
offers in ``provider_pricing.json``.

Every generated offer contains exactly one AInsights model slug.  Matching is
limited to exact normalized identifiers/names or the same exact token multiset
(needed for names such as ``Claude Sonnet 4.6`` vs ``Claude 4.6 Sonnet``).
No substring or fuzzy matching is used.
"""

from __future__ import annotations

import argparse
import json
import math
import posixpath
import re
import tarfile
import tomllib
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOGUE = PROJECT_ROOT / "data" / "pricing" / "provider_pricing.json"
DEFAULT_MODELS = PROJECT_ROOT / "docs" / "data" / "models.json"

SNAPSHOT_COMMIT = "95aaaeb"
SNAPSHOT_DATE = "2026-08-11"
SNAPSHOT_ROOT = f"anomalyco-models.dev-{SNAPSHOT_COMMIT[:7]}"
SNAPSHOT_SOURCE_ID = f"modelsdev-snapshot-{SNAPSHOT_COMMIT[:7]}"
IMPORTED_FROM = "models.dev"

MODELS_DEV_REPOSITORY = "https://github.com/anomalyco/models.dev"
MODELS_DEV_COMMIT_URL = f"{MODELS_DEV_REPOSITORY}/tree/{SNAPSHOT_COMMIT}"

# These directories describe subscriptions, credits, calls, or relative usage
# pools.  Their model TOMLs commonly use zero cost as a quota sentinel and must
# never enter the $/MTok leaderboard through this importer.
NON_PAYG_PROVIDER_IDS = {
    "alibaba-coding-plan",
    "alibaba-coding-plan-cn",
    "alibaba-token-plan",
    "alibaba-token-plan-cn",
    # Anthropic is imported from a same-day official pricing fragment instead
    # of the community snapshot so Fable 5, Batch, Fast, and US-only semantics
    # remain exact.
    "anthropic",
    "cline-pass",
    "github-copilot",
    "gitlab",
    "iflowcn",
    "kimi-for-coding",
    "kuae-cloud-coding-plan",
    "minimax-coding-plan",
    "minimax-cn-coding-plan",
    "opencode-go",
    "stepfun-ai-step-plan",
    "stepfun-step-plan",
    "tencent-coding-plan",
    "tencent-token-plan",
    "tencent-tokenhub",
    "umans-ai-coding-plan",
    "xiaomi-token-plan-ams",
    "xiaomi-token-plan-cn",
    "xiaomi-token-plan-sgp",
    "zai-coding-plan",
    "zhipuai-coding-plan",
}

# Keep first-party APIs separate from same-brand coding subscriptions already
# present in the hand-maintained catalogue.
PROVIDER_ID_ALIASES = {
    "alibaba": "alibaba-api",
    "alibaba-cn": "alibaba-api-cn",
    "anthropic": "anthropic-api",
    "google": "google-ai-api",
    "minimax": "minimax-api",
    "minimax-cn": "minimax-api-cn",
    "moonshotai": "moonshot-api",
    "moonshotai-cn": "moonshot-api-cn",
    "openai": "openai-api",
    "openrouter": "openrouter",
    "opencode": "opencode",
    "zai": "zai-api",
}

REUSED_PLAN_IDS = {
    "openai-api": "openai-api-standard",
    "openrouter": "openrouter-payg",
    "opencode": "opencode-zen",
}

FIRST_PARTY_PROVIDER_IDS = {
    "alibaba",
    "alibaba-cn",
    "anthropic",
    "cohere",
    "deepseek",
    "google",
    "meta",
    "minimax",
    "minimax-cn",
    "mistral",
    "moonshotai",
    "moonshotai-cn",
    "nvidia",
    "openai",
    "perplexity",
    "poolside",
    "sarvam",
    "stepfun",
    "stepfun-ai",
    "xai",
    "xiaomi",
    "zai",
    "zhipuai",
}

UNAVAILABLE_MODEL_STATUSES = {
    "deprecated",
    "disabled",
    "expired",
    "inactive",
    "retired",
}


@dataclass(frozen=True)
class SiteModel:
    slug: str
    names: tuple[str, ...]


@dataclass
class ProviderModelCandidate:
    provider_id: str
    provider_model_id: str
    source_model_name: str
    base_model: str | None
    match_quality: int
    site_slug: str
    input_rate: float
    output_rate: float
    cache_read_rate: float | None
    cache_write_rate: float | None
    context_length: int | None
    pricing_overrides: list[dict[str, Any]]
    status: str | None

    @property
    def coding_mix(self) -> float:
        cache = self.cache_read_rate if self.cache_read_rate is not None else self.input_rate
        return 0.2 * self.input_rate + 0.7 * cache + 0.1 * self.output_rate


def normalize_identity(value: Any) -> str:
    """Normalize punctuation/case while preserving every alphanumeric token."""

    text = str(value or "").lower().replace("&", " and ")
    return " ".join(re.findall(r"[a-z0-9]+", text))


def token_bag(value: Any) -> tuple[str, ...]:
    tokens = normalize_identity(value).split()
    # Provider catalogues reorder descriptors (for example
    # "Claude Sonnet 4.6" vs "Claude 4.6 Sonnet"), but version components
    # are semantic and must retain their order.  Without the numeric suffix,
    # GPT-5.4 and GPT-4.5 collapse to the same unordered token multiset.
    numeric_sequence = [token for token in tokens if token.isdigit()]
    return (*sorted(tokens), "__numeric_sequence__", *numeric_sequence)


def safe_id(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-")


def finite_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    return numeric if math.isfinite(numeric) else None


def positive_number(value: Any) -> float | None:
    numeric = finite_number(value)
    return numeric if numeric is not None and numeric > 0 else None


def nonnegative_number(value: Any) -> float | None:
    numeric = finite_number(value)
    return numeric if numeric is not None and numeric >= 0 else None


def strip_display_qualifier(value: str) -> str:
    return re.sub(r"\s*\([^)]*\)\s*$", "", value or "").strip()


def load_site_models(path: Path) -> list[SiteModel]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("models", payload if isinstance(payload, list) else [])
    models: list[SiteModel] = []
    for row in rows:
        slug = str(row.get("slug") or "").strip()
        if not slug:
            continue
        # The slug is the only unambiguous external identifier.  Display names
        # and variant groups are deliberately excluded: generic labels such as
        # "Gemini 2.5 Flash" and "GPT-4o" are shared by dated, preview,
        # reasoning, and ChatGPT-only rows that a provider may not expose.
        models.append(SiteModel(slug=slug, names=(slug,)))
    return models


def build_site_indexes(
    models: Iterable[SiteModel],
) -> tuple[dict[str, set[str]], dict[tuple[str, ...], set[str]], dict[str, set[str]]]:
    normalized: dict[str, set[str]] = defaultdict(set)
    bags: dict[tuple[str, ...], set[str]] = defaultdict(set)
    slug_names: dict[str, set[str]] = defaultdict(set)
    for model in models:
        for name in model.names:
            identity = normalize_identity(name)
            if not identity:
                continue
            normalized[identity].add(model.slug)
            bags[token_bag(name)].add(model.slug)
            slug_names[model.slug].add(identity)
    return normalized, bags, slug_names


def resolve_tar_member_bytes(archive: tarfile.TarFile, member: tarfile.TarInfo) -> bytes:
    """Read files and resolve both relative symlinks and archive hard links."""

    visited: set[str] = set()
    current = member
    while current.issym() or current.islnk():
        if current.name in visited:
            raise ValueError(f"cyclic archive link: {current.name}")
        visited.add(current.name)
        target = (
            posixpath.normpath(posixpath.join(posixpath.dirname(current.name), current.linkname))
            if current.issym()
            else current.linkname
        )
        current = archive.getmember(target)
    stream = archive.extractfile(current)
    if stream is None:
        raise ValueError(f"cannot read archive member: {current.name}")
    return stream.read()


def load_models_dev_snapshot(
    path: Path,
) -> tuple[dict[str, dict[str, Any]], list[tuple[str, str, dict[str, Any]]]]:
    providers: dict[str, dict[str, Any]] = {}
    models: list[tuple[str, str, dict[str, Any]]] = []
    provider_pattern = re.compile(
        rf"^{re.escape(SNAPSHOT_ROOT)}/providers/([^/]+)/provider\.toml$"
    )
    model_pattern = re.compile(
        rf"^{re.escape(SNAPSHOT_ROOT)}/providers/([^/]+)/models/(.+)\.toml$"
    )
    with tarfile.open(path, "r:gz") as archive:
        for member in archive.getmembers():
            provider_match = provider_pattern.fullmatch(member.name)
            model_match = model_pattern.fullmatch(member.name)
            if not provider_match and not model_match:
                continue
            try:
                parsed = tomllib.loads(resolve_tar_member_bytes(archive, member).decode("utf-8"))
            except KeyError:
                # A small number of upstream provider aliases are broken
                # symlinks in the pinned archive.  They carry no inspectable
                # model record, so omitting them is safer than guessing from
                # the alias filename alone.
                if model_match:
                    continue
                raise
            except (UnicodeDecodeError, ValueError, tomllib.TOMLDecodeError) as exc:
                raise ValueError(f"failed to parse {member.name}: {exc}") from exc
            if provider_match:
                providers[provider_match.group(1)] = parsed
            else:
                models.append((model_match.group(1), model_match.group(2), parsed))
    return providers, models


def candidate_identities(provider_model_id: str, row: dict[str, Any]) -> list[tuple[str, int]]:
    """Return identifiers with lower match-quality values preferred."""

    base_model = str(row.get("base_model") or "").strip()
    source_name = str(row.get("name") or "").strip()
    values: list[tuple[str, int]] = [(provider_model_id, 0)]
    if base_model:
        values.append((base_model.split("/", 1)[-1], 0))
        values.append((base_model, 1))
    if source_name:
        # Some generated names contain a lab prefix (for example
        # "Anthropic: Claude ..."); both forms remain exact comparisons.
        values.append((source_name, 1))
        if ":" in source_name:
            values.append((source_name.split(":", 1)[1], 1))
    deduped: dict[str, int] = {}
    for value, quality in values:
        identity = normalize_identity(value)
        if identity:
            deduped[identity] = min(quality, deduped.get(identity, quality))
    return sorted(deduped.items(), key=lambda item: (item[1], item[0]))


def matched_site_slugs(
    provider_model_id: str,
    row: dict[str, Any],
    normalized_index: dict[str, set[str]],
    bag_index: dict[tuple[str, ...], set[str]],
) -> dict[str, int]:
    matches: dict[str, int] = {}
    for identity, quality in candidate_identities(provider_model_id, row):
        for slug in normalized_index.get(identity, ()):
            matches[slug] = min(quality, matches.get(slug, quality))
        # Exact token-multiset equality handles only reordered names.  It does
        # not drop tokens or allow partial/fuzzy matching.
        for slug in bag_index.get(token_bag(identity), ()):
            bag_quality = quality + 2
            matches[slug] = min(bag_quality, matches.get(slug, bag_quality))
    return matches


def pricing_overrides(cost: dict[str, Any]) -> list[dict[str, Any]]:
    overrides: list[dict[str, Any]] = []
    tiers = cost.get("tiers") if isinstance(cost.get("tiers"), list) else []
    for tier in tiers:
        if not isinstance(tier, dict):
            continue
        threshold = finite_number((tier.get("tier") or {}).get("size"))
        input_rate = positive_number(tier.get("input"))
        output_rate = positive_number(tier.get("output"))
        if threshold is None or input_rate is None or output_rate is None:
            continue
        overrides.append(
            {
                "minPromptTokens": int(threshold),
                "inputPerMillionTokensUsd": input_rate,
                # Upstream zeroes are frequently inherited placeholders for an
                # unpublished cache rate, not evidence that cache reads are
                # free.  Preserve only a strictly positive published value.
                "cacheReadPerMillionTokensUsd": positive_number(tier.get("cache_read")),
                "outputPerMillionTokensUsd": output_rate,
                "notes": "Models.dev provider tier for prompts at or above this size.",
            }
        )
    return overrides


def collect_candidates(
    provider_models: Iterable[tuple[str, str, dict[str, Any]]],
    normalized_index: dict[str, set[str]],
    bag_index: dict[tuple[str, ...], set[str]],
) -> dict[tuple[str, str], ProviderModelCandidate]:
    selected: dict[tuple[str, str], ProviderModelCandidate] = {}
    for provider_id, provider_model_id, row in provider_models:
        if provider_id in NON_PAYG_PROVIDER_IDS:
            continue
        status = str(row.get("status") or "").strip().lower() or None
        if status in UNAVAILABLE_MODEL_STATUSES:
            continue
        cost = row.get("cost") if isinstance(row.get("cost"), dict) else {}
        input_rate = positive_number(cost.get("input"))
        output_rate = positive_number(cost.get("output"))
        # Both rates are required for the site's published Coding Mix.  Missing,
        # zero, or negative token rates are not silently imputed.
        if input_rate is None or output_rate is None:
            continue
        # Models.dev uses zero in a number of inherited/community rows where a
        # cache price is absent.  Treat only positive cache prices as published
        # rates so the comparison mix falls back to the new-input rate instead
        # of manufacturing free cached input.
        cache_read_rate = positive_number(cost.get("cache_read"))
        cache_write_rate = positive_number(cost.get("cache_write"))
        limit = row.get("limit") if isinstance(row.get("limit"), dict) else {}
        context = finite_number(limit.get("context"))
        matches = matched_site_slugs(
            provider_model_id,
            row,
            normalized_index,
            bag_index,
        )
        for site_slug, quality in matches.items():
            candidate = ProviderModelCandidate(
                provider_id=provider_id,
                provider_model_id=provider_model_id,
                source_model_name=str(row.get("name") or provider_model_id),
                base_model=str(row.get("base_model") or "") or None,
                match_quality=quality,
                site_slug=site_slug,
                input_rate=input_rate,
                output_rate=output_rate,
                cache_read_rate=cache_read_rate,
                cache_write_rate=cache_write_rate,
                context_length=int(context) if context is not None else None,
                pricing_overrides=pricing_overrides(cost),
                status=status,
            )
            key = (provider_id, site_slug)
            incumbent = selected.get(key)
            ordering = (
                candidate.match_quality,
                candidate.coding_mix,
                candidate.provider_model_id,
            )
            incumbent_ordering = (
                incumbent.match_quality,
                incumbent.coding_mix,
                incumbent.provider_model_id,
            ) if incumbent else None
            if incumbent_ordering is None or ordering < incumbent_ordering:
                selected[key] = candidate
    return selected


def source_id_for(provider_id: str) -> str:
    return f"modelsdev-{safe_id(provider_id)}-{SNAPSHOT_COMMIT[:7]}"


def target_provider_id(models_dev_provider_id: str) -> str:
    return PROVIDER_ID_ALIASES.get(models_dev_provider_id, models_dev_provider_id)


def target_plan_id(catalogue_provider_id: str) -> str:
    return REUSED_PLAN_IDS.get(catalogue_provider_id, f"{catalogue_provider_id}-payg")


def display_provider_name(provider_id: str, metadata: dict[str, Any]) -> str:
    name = str(metadata.get("name") or provider_id)
    if provider_id in {"anthropic", "minimax", "minimax-cn", "moonshotai", "moonshotai-cn", "zai"}:
        return f"{name} API"
    return name


def clean_previous_import(catalogue: dict[str, Any]) -> None:
    imported_prefix = "modelsdev-"
    for section in ("providers", "plans", "offers", "sources"):
        catalogue[section] = [
            row for row in catalogue.get(section, []) if row.get("importedFrom") != IMPORTED_FROM
        ]
    for section in ("providers", "plans", "offers"):
        for row in catalogue.get(section, []):
            if isinstance(row.get("sourceIds"), list):
                row["sourceIds"] = [
                    source_id
                    for source_id in row["sourceIds"]
                    if not str(source_id).startswith(imported_prefix)
                ]


def append_source_id(row: dict[str, Any], source_id: str) -> None:
    source_ids = row.setdefault("sourceIds", [])
    if source_id not in source_ids:
        source_ids.append(source_id)


def add_snapshot_source(catalogue: dict[str, Any]) -> None:
    catalogue["sources"].append(
        {
            "id": SNAPSHOT_SOURCE_ID,
            "title": f"Models.dev provider catalogue snapshot {SNAPSHOT_COMMIT[:7]}",
            "publisher": "Models.dev contributors",
            "url": MODELS_DEV_COMMIT_URL,
            "kind": "community-catalog",
            "asOf": SNAPSHOT_DATE,
            "accessedAt": SNAPSHOT_DATE,
            "notes": (
                "Community-maintained provider/model support and pricing metadata. "
                "Positive token rates are normalized as USD per million tokens; official "
                "provider pages remain authoritative and should be checked before purchase."
            ),
            "importedFrom": IMPORTED_FROM,
        }
    )


def augment_catalogue(
    catalogue: dict[str, Any],
    provider_metadata: dict[str, dict[str, Any]],
    candidates: dict[tuple[str, str], ProviderModelCandidate],
    valid_site_slugs: set[str],
) -> dict[str, int]:
    clean_previous_import(catalogue)
    add_snapshot_source(catalogue)
    provider_by_id = {row["id"]: row for row in catalogue["providers"]}
    plan_by_id = {row["id"]: row for row in catalogue["plans"]}

    existing_model_keys: set[tuple[str, str, str]] = set()
    for offer in catalogue["offers"]:
        for slug in offer.get("modelSlugs", []):
            existing_model_keys.add((offer["providerId"], offer["planId"], slug))

    candidates_by_provider: dict[str, list[ProviderModelCandidate]] = defaultdict(list)
    for candidate in candidates.values():
        candidates_by_provider[candidate.provider_id].append(candidate)

    imported_provider_count = 0
    imported_plan_count = 0
    imported_offer_count = 0
    reused_provider_count = 0
    reused_plan_count = 0

    for models_dev_provider_id in sorted(candidates_by_provider):
        rows = sorted(
            candidates_by_provider[models_dev_provider_id],
            key=lambda item: (item.site_slug, item.provider_model_id),
        )
        metadata = provider_metadata.get(models_dev_provider_id, {})
        provider_id = target_provider_id(models_dev_provider_id)
        plan_id = target_plan_id(provider_id)
        provider_source_id = source_id_for(models_dev_provider_id)
        provider_doc = str(metadata.get("doc") or "").strip()
        provider_catalogue_url = (
            f"{MODELS_DEV_COMMIT_URL}/providers/{models_dev_provider_id}"
        )
        catalogue["sources"].append(
            {
                "id": provider_source_id,
                "title": f"{display_provider_name(models_dev_provider_id, metadata)} model and pricing metadata",
                "publisher": str(metadata.get("name") or models_dev_provider_id),
                "url": provider_doc or provider_catalogue_url,
                "kind": "community-catalog-linked-provider-doc",
                "asOf": SNAPSHOT_DATE,
                "accessedAt": SNAPSHOT_DATE,
                "notes": (
                    f"Provider support and positive USD/MTok rates transcribed from Models.dev "
                    f"commit {SNAPSHOT_COMMIT[:7]}. The linked provider documentation is included "
                    "when the catalogue publishes one; live provider pricing remains authoritative."
                ),
                "catalogueUrl": provider_catalogue_url,
                "importedFrom": IMPORTED_FROM,
            }
        )

        provider = provider_by_id.get(provider_id)
        if provider is None:
            provider = {
                "id": provider_id,
                "name": display_provider_name(models_dev_provider_id, metadata),
                "category": (
                    "first-party-api"
                    if models_dev_provider_id in FIRST_PARTY_PROVIDER_IDS
                    else "aggregator"
                ),
                "url": provider_doc or provider_catalogue_url,
                "pricingUrl": provider_doc or provider_catalogue_url,
                "modelsDevProviderId": models_dev_provider_id,
                "sourceIds": [provider_source_id, SNAPSHOT_SOURCE_ID],
                "importedFrom": IMPORTED_FROM,
            }
            catalogue["providers"].append(provider)
            provider_by_id[provider_id] = provider
            imported_provider_count += 1
        else:
            append_source_id(provider, provider_source_id)
            append_source_id(provider, SNAPSHOT_SOURCE_ID)
            reused_provider_count += 1

        plan = plan_by_id.get(plan_id)
        if plan is None:
            plan = {
                "id": plan_id,
                "providerId": provider_id,
                "name": "Pay as you go",
                "billingType": "payg",
                "displayType": "token",
                "currency": "USD",
                "monthlyPriceUsd": None,
                "comparisonClass": "token-comparable",
                "sourceIds": [provider_source_id, SNAPSHOT_SOURCE_ID],
                "importedFrom": IMPORTED_FROM,
            }
            catalogue["plans"].append(plan)
            plan_by_id[plan_id] = plan
            imported_plan_count += 1
        else:
            append_source_id(plan, provider_source_id)
            append_source_id(plan, SNAPSHOT_SOURCE_ID)
            reused_plan_count += 1

        for candidate in rows:
            if candidate.site_slug not in valid_site_slugs:
                raise ValueError(f"unknown mapped site slug: {candidate.site_slug}")
            key = (provider_id, plan_id, candidate.site_slug)
            if key in existing_model_keys:
                continue
            offer: dict[str, Any] = {
                "id": f"md-{safe_id(models_dev_provider_id)}-{safe_id(candidate.site_slug)}",
                "providerId": provider_id,
                "planId": plan_id,
                "modelSlugs": [candidate.site_slug],
                "providerModelId": candidate.provider_model_id,
                "modelsDevBaseModel": candidate.base_model,
                "modelsDevModelName": candidate.source_model_name,
                "mappingMethod": (
                    "exact-normalized-identifier"
                    if candidate.match_quality <= 1
                    else "exact-token-multiset"
                ),
                "pricingKind": "per-token",
                "comparable": True,
                "inputPerMillionTokensUsd": candidate.input_rate,
                "cacheReadPerMillionTokensUsd": candidate.cache_read_rate,
                "cacheWritePerMillionTokensUsd": candidate.cache_write_rate,
                "outputPerMillionTokensUsd": candidate.output_rate,
                "contextLength": candidate.context_length,
                "sourceIds": [provider_source_id, SNAPSHOT_SOURCE_ID],
                "observedAt": SNAPSHOT_DATE,
                "evidenceKind": "community-catalog",
                "estimated": True,
                "importedFrom": IMPORTED_FROM,
            }
            if candidate.status:
                offer["status"] = candidate.status
            if candidate.pricing_overrides:
                offer["pricingOverrides"] = candidate.pricing_overrides
            if provider_id == "openrouter":
                # Existing OpenRouter cards expose route metadata.  Imported
                # catalogue rows are explicitly labelled rather than pretending
                # to be a live endpoint route observation.
                offer.update(
                    {
                        "routeProvider": "OpenRouter catalogue",
                        "routeTag": "models.dev",
                        "routeLabel": "Models.dev snapshot",
                    }
                )
            catalogue["offers"].append(offer)
            existing_model_keys.add(key)
            imported_offer_count += 1

    catalogue["asOf"] = max(str(catalogue.get("asOf") or ""), SNAPSHOT_DATE)
    return {
        "providersAdded": imported_provider_count,
        "providersReused": reused_provider_count,
        "plansAdded": imported_plan_count,
        "plansReused": reused_plan_count,
        "offersAdded": imported_offer_count,
        "totalProviders": len(catalogue["providers"]),
        "totalPlans": len(catalogue["plans"]),
        "totalOffers": len(catalogue["offers"]),
        "totalSources": len(catalogue["sources"]),
    }


def validate_catalogue(catalogue: dict[str, Any], valid_site_slugs: set[str]) -> None:
    provider_ids = [row["id"] for row in catalogue["providers"]]
    plan_ids = [row["id"] for row in catalogue["plans"]]
    offer_ids = [row["id"] for row in catalogue["offers"]]
    source_ids = [row["id"] for row in catalogue["sources"]]
    for label, values in (
        ("provider", provider_ids),
        ("plan", plan_ids),
        ("offer", offer_ids),
        ("source", source_ids),
    ):
        if len(values) != len(set(values)):
            duplicates = sorted(value for value in set(values) if values.count(value) > 1)
            raise ValueError(f"duplicate {label} ids: {duplicates[:10]}")
    provider_id_set = set(provider_ids)
    source_id_set = set(source_ids)
    plan_by_id = {row["id"]: row for row in catalogue["plans"]}
    for plan in catalogue["plans"]:
        if plan["providerId"] not in provider_id_set:
            raise ValueError(f"orphan plan provider: {plan['id']}")
    for offer in catalogue["offers"]:
        if offer["providerId"] not in provider_id_set:
            raise ValueError(f"orphan offer provider: {offer['id']}")
        if offer["planId"] not in plan_by_id:
            raise ValueError(f"orphan offer plan: {offer['id']}")
        if plan_by_id[offer["planId"]]["providerId"] != offer["providerId"]:
            raise ValueError(f"offer/plan provider mismatch: {offer['id']}")
        unknown_slugs = set(offer.get("modelSlugs", [])) - valid_site_slugs
        if unknown_slugs:
            raise ValueError(f"unknown offer slugs on {offer['id']}: {sorted(unknown_slugs)}")
        if offer.get("importedFrom") == IMPORTED_FROM and len(offer.get("modelSlugs", [])) != 1:
            raise ValueError(f"imported offer must map one model: {offer['id']}")
        if not set(offer.get("sourceIds", [])) <= source_id_set:
            raise ValueError(f"unknown offer source on {offer['id']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path, help="Pinned Models.dev .tar.gz snapshot")
    parser.add_argument("--catalogue", type=Path, default=DEFAULT_CATALOGUE)
    parser.add_argument("--models", type=Path, default=DEFAULT_MODELS)
    parser.add_argument(
        "--output",
        type=Path,
        help="Output JSON path (defaults to updating --catalogue in place)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate and print counts without writing")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    catalogue = json.loads(args.catalogue.read_text(encoding="utf-8"))
    site_models = load_site_models(args.models)
    valid_site_slugs = {model.slug for model in site_models}
    normalized_index, bag_index, _ = build_site_indexes(site_models)
    provider_metadata, provider_models = load_models_dev_snapshot(args.snapshot)
    candidates = collect_candidates(provider_models, normalized_index, bag_index)
    summary = augment_catalogue(
        catalogue,
        provider_metadata,
        candidates,
        valid_site_slugs,
    )
    validate_catalogue(catalogue, valid_site_slugs)
    summary.update(
        {
            "snapshotProviders": len(provider_metadata),
            "snapshotProviderModels": len(provider_models),
            "matchedPaygProviderModels": len(candidates),
            "mappedSiteModels": len(
                {
                    candidate.site_slug
                    for candidate in candidates.values()
                }
            ),
        }
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not args.dry_run:
        output = args.output or args.catalogue
        output.write_text(
            json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
