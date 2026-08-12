#!/usr/bin/env python3
"""Replace provider slices in the main pricing catalogue with researched fragments."""

from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOGUE = PROJECT_ROOT / "data" / "pricing" / "provider_pricing.json"
DEFAULT_MODELS = PROJECT_ROOT / "docs" / "data" / "models.json"


def safe_id(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-")


def referenced_source_ids(rows: Iterable[dict[str, Any]]) -> set[str]:
    return {
        str(source_id)
        for row in rows
        for source_id in row.get("sourceIds", [])
    }


def split_offer_by_model(offer: dict[str, Any]) -> list[dict[str, Any]]:
    slugs = list(dict.fromkeys(offer.get("modelSlugs", [])))
    if len(slugs) <= 1:
        return [copy.deepcopy(offer)]
    rows: list[dict[str, Any]] = []
    for index, slug in enumerate(slugs):
        row = copy.deepcopy(offer)
        row["modelSlugs"] = [slug]
        if index:
            row["id"] = f"{offer['id']}-{safe_id(slug)}"
        rows.append(row)
    return rows


def merge_fragment(
    catalogue: dict[str, Any],
    fragment: dict[str, Any],
    fragment_name: str,
) -> dict[str, int]:
    provider_ids = {row["id"] for row in fragment.get("providers", [])}
    if not provider_ids:
        raise ValueError(f"{fragment_name}: fragment contains no providers")

    removed_rows = [
        row
        for section in ("providers", "plans", "offers")
        for row in catalogue.get(section, [])
        if row.get("id") in provider_ids or row.get("providerId") in provider_ids
    ]
    removable_source_ids = referenced_source_ids(removed_rows)

    catalogue["providers"] = [
        row for row in catalogue.get("providers", []) if row.get("id") not in provider_ids
    ]
    catalogue["plans"] = [
        row for row in catalogue.get("plans", []) if row.get("providerId") not in provider_ids
    ]
    catalogue["offers"] = [
        row for row in catalogue.get("offers", []) if row.get("providerId") not in provider_ids
    ]

    catalogue["providers"].extend(copy.deepcopy(fragment.get("providers", [])))
    catalogue["plans"].extend(copy.deepcopy(fragment.get("plans", [])))
    split_offers = [
        split
        for offer in fragment.get("offers", [])
        for split in split_offer_by_model(offer)
    ]
    catalogue["offers"].extend(split_offers)

    fragment_source_ids = {row["id"] for row in fragment.get("sources", [])}
    catalogue["sources"] = [
        row
        for row in catalogue.get("sources", [])
        if row.get("id") not in fragment_source_ids
    ]
    catalogue["sources"].extend(copy.deepcopy(fragment.get("sources", [])))

    fragment_exchange_rates = fragment.get("exchangeRates") or {}
    if fragment_exchange_rates:
        catalogue["exchangeRates"] = {
            **(catalogue.get("exchangeRates") or {}),
            **copy.deepcopy(fragment_exchange_rates),
        }

    still_referenced = referenced_source_ids(
        row
        for section in ("providers", "plans", "offers")
        for row in catalogue.get(section, [])
    )
    for exchange_rate in (catalogue.get("exchangeRates") or {}).values():
        source_id = exchange_rate.get("sourceId") if isinstance(exchange_rate, dict) else None
        if source_id:
            still_referenced.add(str(source_id))
    catalogue["sources"] = [
        row
        for row in catalogue["sources"]
        if row.get("id") not in removable_source_ids or row.get("id") in still_referenced
    ]
    removed_metadata = list(fragment.get("removeMetadata", []))
    for key in removed_metadata:
        catalogue.pop(key, None)
    for key, value in fragment.get("metadata", {}).items():
        catalogue[key] = copy.deepcopy(value)
    catalogue["asOf"] = max(
        str(catalogue.get("asOf") or ""),
        str(fragment.get("checkedAt") or ""),
    )
    return {
        "providersReplaced": len(provider_ids),
        "plansAdded": len(fragment.get("plans", [])),
        "fragmentOffers": len(fragment.get("offers", [])),
        "singleModelOffersAdded": len(split_offers),
        "sourcesAdded": len(fragment.get("sources", [])),
        "exchangeRatesUpdated": len(fragment_exchange_rates),
        "metadataRemoved": len(removed_metadata),
        "metadataUpdated": len(fragment.get("metadata", {})),
    }


def validate(catalogue: dict[str, Any], valid_model_slugs: set[str]) -> None:
    provider_ids = [row["id"] for row in catalogue.get("providers", [])]
    plan_ids = [row["id"] for row in catalogue.get("plans", [])]
    offer_ids = [row["id"] for row in catalogue.get("offers", [])]
    source_ids = [row["id"] for row in catalogue.get("sources", [])]
    for label, values in (
        ("provider", provider_ids),
        ("plan", plan_ids),
        ("offer", offer_ids),
        ("source", source_ids),
    ):
        duplicates = sorted({value for value in values if values.count(value) > 1})
        if duplicates:
            raise ValueError(f"duplicate {label} ids: {duplicates[:10]}")
    provider_set = set(provider_ids)
    source_set = set(source_ids)
    for currency, exchange_rate in (catalogue.get("exchangeRates") or {}).items():
        if currency == "USD" or not isinstance(exchange_rate, dict):
            raise ValueError(f"invalid exchange-rate entry: {currency}")
        for field in ("usdPerUnit", "unitsPerUsd"):
            value = exchange_rate.get(field)
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or value <= 0
            ):
                raise ValueError(f"invalid {field} for exchange rate {currency}")
        if exchange_rate.get("sourceId") not in source_set:
            raise ValueError(f"unknown source on exchange rate {currency}")
    plans = {row["id"]: row for row in catalogue.get("plans", [])}
    for provider in catalogue.get("providers", []):
        unknown_sources = set(provider.get("sourceIds", [])) - source_set
        if unknown_sources:
            raise ValueError(
                f"unknown source on provider {provider['id']}: {sorted(unknown_sources)}"
            )
    for plan in plans.values():
        if plan["providerId"] not in provider_set:
            raise ValueError(f"orphan plan: {plan['id']}")
        unknown_sources = set(plan.get("sourceIds", [])) - source_set
        if unknown_sources:
            raise ValueError(
                f"unknown source on plan {plan['id']}: {sorted(unknown_sources)}"
            )
    for offer in catalogue.get("offers", []):
        plan = plans.get(offer.get("planId"))
        if offer.get("providerId") not in provider_set or plan is None:
            raise ValueError(f"orphan offer: {offer['id']}")
        if plan["providerId"] != offer["providerId"]:
            raise ValueError(f"offer/plan provider mismatch: {offer['id']}")
        if not offer.get("modelSlugs"):
            raise ValueError(f"offer contains no model slugs: {offer['id']}")
        unknown = set(offer.get("modelSlugs", [])) - valid_model_slugs
        if unknown:
            raise ValueError(f"unknown model slugs on {offer['id']}: {sorted(unknown)}")
        if not set(offer.get("sourceIds", [])) <= source_set:
            raise ValueError(f"unknown source on offer: {offer['id']}")
        if offer.get("bestCaseOnly") and offer.get("comparable"):
            raise ValueError(
                f"best-case-only offer cannot be comparable: {offer['id']}"
            )
        if offer.get("pricingKind") == "estimated-effective-subscription":
            if not offer.get("estimated") or offer.get("comparable"):
                raise ValueError(
                    "estimated subscription must be marked estimated and "
                    f"non-comparable: {offer['id']}"
                )
            if not isinstance(offer.get("effectiveUsdPerMillionTokens"), (int, float)):
                raise ValueError(
                    f"estimated subscription requires a finite effective price: {offer['id']}"
                )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fragments", nargs="+", type=Path)
    parser.add_argument("--catalogue", type=Path, default=DEFAULT_CATALOGUE)
    parser.add_argument("--models", type=Path, default=DEFAULT_MODELS)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    catalogue = json.loads(args.catalogue.read_text(encoding="utf-8"))
    model_payload = json.loads(args.models.read_text(encoding="utf-8"))
    valid_model_slugs = {
        row["slug"] for row in model_payload.get("models", []) if row.get("slug")
    }
    summaries: dict[str, Any] = {}
    for fragment_path in args.fragments:
        fragment = json.loads(fragment_path.read_text(encoding="utf-8"))
        summaries[str(fragment_path)] = merge_fragment(
            catalogue,
            fragment,
            fragment_path.name,
        )
    validate(catalogue, valid_model_slugs)
    summaries["catalogue"] = {
        "providers": len(catalogue["providers"]),
        "plans": len(catalogue["plans"]),
        "offers": len(catalogue["offers"]),
        "sources": len(catalogue["sources"]),
    }
    print(json.dumps(summaries, ensure_ascii=False, indent=2))
    if not args.dry_run:
        output = args.output or args.catalogue
        output.write_text(
            json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
