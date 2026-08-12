#!/usr/bin/env python3
"""Generate verified model-author first-party API pricing rows.

Only prices confirmed on the model author's official public pages are emitted.
The audit exclusions intentionally preserve researched gaps without turning
community aggregator prices into first-party API claims.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MODELS_PATH = ROOT / "docs" / "data" / "models.json"
OUTPUT_PATH = ROOT / "data" / "pricing" / "research_first_party_model_apis.json"
CHECKED_AT = "2026-08-12"
FX_AS_OF = "2026-08-10"
INR_PER_EUR = 110.1228
USD_PER_EUR = 1.1555
INR_PER_USD = INR_PER_EUR / USD_PER_EUR
USD_PER_INR = 1 / INR_PER_USD
INR_FX_SOURCE_ID = "ecb-reference-fx-inr-2026-08-10"


def provider(
    provider_id: str,
    name: str,
    url: str,
    pricing_url: str,
    source_ids: list[str],
    **extra: Any,
) -> dict[str, Any]:
    return {
        "id": provider_id,
        "name": name,
        "category": "first-party-api",
        "url": url,
        "pricingUrl": pricing_url,
        "sourceIds": source_ids,
        **extra,
    }


def payg_plan(
    plan_id: str,
    provider_id: str,
    name: str,
    source_ids: list[str],
    currency: str = "USD",
    **extra: Any,
) -> dict[str, Any]:
    row = {
        "id": plan_id,
        "providerId": provider_id,
        "name": name,
        "billingType": "payg",
        "displayType": "token",
        "currency": currency,
        "monthlyPriceUsd": None,
        "comparisonClass": "token-comparable",
        "quotaLabel": "Pay as you go",
        "sourceIds": source_ids,
    }
    row.update(extra)
    return row


def token_offer(
    offer_id: str,
    provider_id: str,
    plan_id: str,
    slug: str,
    provider_model_id: str,
    input_rate: float,
    output_rate: float,
    source_ids: list[str],
    cache_read_rate: float | None = None,
    **extra: Any,
) -> dict[str, Any]:
    row = {
        "id": offer_id,
        "providerId": provider_id,
        "planId": plan_id,
        "modelSlugs": [slug],
        "providerModelId": provider_model_id,
        "pricingKind": "per-token",
        "comparable": extra.pop("comparable", True),
        "checkedAt": CHECKED_AT,
        "inputPerMillionTokensUsd": input_rate,
        "cacheReadPerMillionTokensUsd": cache_read_rate,
        "cacheWritePerMillionTokensUsd": None,
        "outputPerMillionTokensUsd": output_rate,
        "sourceIds": source_ids,
        **extra,
    }
    return row


def build_fragment() -> dict[str, Any]:
    providers = [
        provider(
            "ai21-api",
            "AI21 Labs API",
            "https://www.ai21.com/",
            "https://www.ai21.com/pricing/",
            ["ai21-api-pricing-2026-08-12", "ai21-jamba-models-2026-08-12"],
            notes="Model-author API. Jamba Large pricing is linked to the official current 1.7 API version documented by AI21.",
        ),
        provider(
            "upstage",
            "Upstage API",
            "https://console.upstage.ai/",
            "https://www.upstage.ai/pricing/api",
            ["upstage-api-pricing-2026-08-12", "upstage-api-models-2026-08-12"],
            notes="Model-author API; replaces the community-imported Upstage provider classification when merged.",
        ),
        provider(
            "reka-api",
            "Reka API",
            "https://reka.ai/",
            "https://docs.reka.ai/pricing",
            ["reka-api-pricing-2026-08-12", "reka-api-models-2026-08-12"],
        ),
        provider(
            "inception",
            "Inception API",
            "https://www.inceptionlabs.ai/",
            "https://www.inceptionlabs.ai/models",
            ["inception-api-models-pricing-2026-08-12"],
            notes="Model-author API; replaces the community-imported Inception provider classification when merged.",
        ),
        provider(
            "sarvam-api",
            "Sarvam AI API",
            "https://www.sarvam.ai/",
            "https://www.sarvam.ai/api-pricing",
            ["sarvam-api-pricing-2026-08-12", "sarvam-api-models-2026-08-12"],
            notes="Official pricing currently marks the listed chat LLMs free per token.",
        ),
    ]

    plans = [
        payg_plan(
            "ai21-api-payg",
            "ai21-api",
            "AI21 Platform PAYG",
            ["ai21-api-pricing-2026-08-12", "ai21-jamba-models-2026-08-12"],
            quotaLabel="$10 seven-day trial credit, then usage-based billing",
        ),
        payg_plan(
            "upstage-payg",
            "upstage",
            "Upstage Console PAYG",
            ["upstage-api-pricing-2026-08-12", "upstage-api-models-2026-08-12"],
            quotaLabel="Usage-based API pricing; published prices exclude 10% VAT",
        ),
        payg_plan(
            "reka-api-payg",
            "reka-api",
            "Reka Chat PAYG",
            ["reka-api-pricing-2026-08-12", "reka-api-models-2026-08-12"],
        ),
        payg_plan(
            "inception-payg",
            "inception",
            "Inception Developer PAYG",
            ["inception-api-models-pricing-2026-08-12"],
            quotaLabel="Usage-based developer API; official page also advertises a free-token allowance",
        ),
        payg_plan(
            "sarvam-api-payg",
            "sarvam-api",
            "Sarvam Starter PAYG",
            ["sarvam-api-pricing-2026-08-12", "sarvam-api-models-2026-08-12"],
            currency="INR",
            quotaLabel="Pay as you go; Sarvam 105B and 30B are currently free per token",
        ),
    ]

    offers = [
        token_offer(
            "ai21-api-jamba-1-7-large",
            "ai21-api",
            "ai21-api-payg",
            "jamba-1-7-large",
            "jamba-large-1.7",
            2,
            8,
            ["ai21-api-pricing-2026-08-12", "ai21-jamba-models-2026-08-12"],
            contextLength=256000,
            notes="Official pricing lists Jamba Large at $2 input / $8 output per million tokens; official model docs map jamba-large-1.7 to the current 1.7 snapshot.",
        ),
        token_offer(
            "upstage-solar-pro-3",
            "upstage",
            "upstage-payg",
            "solar-pro-3",
            "solar-pro-3",
            0.15,
            0.6,
            ["upstage-api-pricing-2026-08-12", "upstage-api-models-2026-08-12"],
            cache_read_rate=0.015,
            notes="Official list price excluding 10% VAT.",
        ),
        token_offer(
            "upstage-solar-pro-2",
            "upstage",
            "upstage-payg",
            "solar-pro-2",
            "solar-pro-2",
            0.15,
            0.6,
            ["upstage-api-pricing-2026-08-12", "upstage-api-models-2026-08-12"],
            cache_read_rate=0.015,
            notes="Official list price excluding 10% VAT. The consolidated Solar Pro 2 API model supports chat and reasoning modes; preview/reasoning-only AInsights aliases are not inferred.",
        ),
        token_offer(
            "upstage-solar-mini",
            "upstage",
            "upstage-payg",
            "solar-mini",
            "solar-mini",
            0.15,
            0.15,
            ["upstage-api-pricing-2026-08-12", "upstage-api-models-2026-08-12"],
            notes="The official card publishes one $0.15 per-million-token rate without input/output differentiation; the same rate is recorded for both categories. Price excludes 10% VAT.",
        ),
        token_offer(
            "reka-api-reka-flash",
            "reka-api",
            "reka-api-payg",
            "reka-flash",
            "reka-flash",
            0.8,
            2,
            ["reka-api-pricing-2026-08-12", "reka-api-models-2026-08-12"],
            notes="Reka's public baseline-model documentation names reka-flash and the pricing page publishes $0.80 input / $2 output per million tokens.",
        ),
        token_offer(
            "inception-mercury-2",
            "inception",
            "inception-payg",
            "mercury-2",
            "mercury-2",
            0.25,
            0.75,
            ["inception-api-models-pricing-2026-08-12"],
            cache_read_rate=0.025,
            contextLength=128000,
            notes="Official Inception models page publishes input, cached-input, and output rates and shows the mercury-2 API request ID.",
        ),
        token_offer(
            "sarvam-api-sarvam-105b",
            "sarvam-api",
            "sarvam-api-payg",
            "sarvam-105b",
            "sarvam-105b",
            0,
            0,
            ["sarvam-api-pricing-2026-08-12", "sarvam-api-models-2026-08-12"],
            inputPerMillionTokensLocal=0,
            cacheReadPerMillionTokensLocal=None,
            outputPerMillionTokensLocal=0,
            currency="INR",
            publishedZeroRate=True,
            supportStatus="active",
            notes="Official pricing says 'Free per token'; the official model page lists sarvam-105b as an active API model.",
        ),
        token_offer(
            "sarvam-api-sarvam-30b",
            "sarvam-api",
            "sarvam-api-payg",
            "sarvam-30b",
            "sarvam-30b",
            0,
            0,
            ["sarvam-api-pricing-2026-08-12", "sarvam-api-models-2026-08-12"],
            comparable=False,
            inputPerMillionTokensLocal=0,
            cacheReadPerMillionTokensLocal=None,
            outputPerMillionTokensLocal=0,
            currency="INR",
            publishedZeroRate=True,
            supportStatus="deprecated",
            availability={
                "status": "deprecated",
                "note": "Official model docs recommend migration to Sarvam 105B.",
            },
            notes="Official pricing still says 'Free per token', but official model docs mark Sarvam 30B deprecated and being phased out; it is excluded from cheapest-price ranking.",
        ),
    ]

    sources = [
        {
            "id": "ai21-api-pricing-2026-08-12",
            "title": "AI21 pricing — Foundation Models",
            "publisher": "AI21 Labs",
            "url": "https://www.ai21.com/pricing/",
            "kind": "official-pricing",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Publishes Jamba Mini at $0.20/$0.40 and Jamba Large at $2/$8 per million input/output tokens. Only Large maps to an exact current AInsights version slug.",
        },
        {
            "id": "ai21-jamba-models-2026-08-12",
            "title": "AI21 Jamba foundation models",
            "publisher": "AI21 Labs",
            "url": "https://docs.ai21.com/docs/jamba-foundation-models",
            "kind": "official-model-list",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Identifies Jamba Large 1.7 as the current Large API version, Jamba Mini 2 as the current Mini version, and older Mini/Large versions as deprecated.",
        },
        {
            "id": "upstage-api-pricing-2026-08-12",
            "title": "Upstage API pricing",
            "publisher": "Upstage",
            "url": "https://www.upstage.ai/pricing/api",
            "kind": "official-pricing",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Publishes Solar Pro 3 and Solar Pro 2 input/cached-input/output rates, a single Solar Mini token rate, and states prices exclude 10% VAT.",
        },
        {
            "id": "upstage-api-models-2026-08-12",
            "title": "Upstage Console model documentation",
            "publisher": "Upstage",
            "url": "https://console.upstage.ai/docs/models",
            "kind": "official-model-list",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Official model pages confirm Solar Pro 3, Solar Pro 2, and Solar Mini as Console API models.",
        },
        {
            "id": "reka-api-pricing-2026-08-12",
            "title": "Reka API pricing",
            "publisher": "Reka AI",
            "url": "https://docs.reka.ai/pricing",
            "kind": "official-pricing",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Publishes Reka Flash at $0.80 input and $2 output per million tokens.",
        },
        {
            "id": "reka-api-models-2026-08-12",
            "title": "Reka Chat models",
            "publisher": "Reka AI",
            "url": "https://docs.reka.ai/chat/models",
            "kind": "official-model-list",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Names reka-flash as an always-available public baseline API model and shows the exact ID.",
        },
        {
            "id": "inception-api-models-pricing-2026-08-12",
            "title": "Inception models and API pricing",
            "publisher": "Inception",
            "url": "https://www.inceptionlabs.ai/models",
            "kind": "official-pricing",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Publishes Mercury 2 at $0.25 input, $0.025 cached input, and $0.75 output per million tokens and shows model='mercury-2'.",
        },
        {
            "id": "sarvam-api-pricing-2026-08-12",
            "title": "Sarvam AI API pricing",
            "publisher": "Sarvam AI",
            "url": "https://www.sarvam.ai/api-pricing",
            "kind": "official-pricing",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Lists Sarvam 105B and Sarvam 30B chat LLM usage as free per token.",
        },
        {
            "id": "sarvam-api-models-2026-08-12",
            "title": "Sarvam AI model selection guide",
            "publisher": "Sarvam AI",
            "url": "https://docs.sarvam.ai/api/getting-started/models",
            "kind": "official-model-list",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Confirms sarvam-105b as active, Sarvam 30B as deprecated/being phased out, and Sarvam-M as no longer available through the API.",
        },
        {
            "id": INR_FX_SOURCE_ID,
            "title": "ECB reference exchange rates — INR and USD against EUR",
            "publisher": "European Central Bank",
            "url": "https://data-api.ecb.europa.eu/service/data/EXR/D.INR+USD.EUR.SP00.A?startPeriod=2026-08-10&endPeriod=2026-08-10&format=csvdata",
            "kind": "official-reference-data",
            "asOf": FX_AS_OF,
            "accessedAt": CHECKED_AT,
            "notes": "INR/EUR 110.1228 and USD/EUR 1.1555 on 2026-08-10 imply 95.303158806 INR per USD; used only to normalize local-currency prices for cross-provider comparison.",
        },
    ]

    exclusions = [
        {
            "creator": "Cohere",
            "modelSlugs": [
                "north-mini-code",
                "command-a",
                "tiny-aya-global",
                "command-a-plus",
                "command-r-plus-04-2024",
                "command-r-03-2024",
            ],
            "reason": "The official pricing page does not publish per-token rates for the live A/A+/North/Tiny Aya slugs. The two exact Command R slugs with public legacy rates were deprecated on 2025-09-15, so they are not emitted as usable current API offers.",
            "sourceUrls": [
                "https://cohere.com/pricing",
                "https://docs.cohere.com/docs/models",
            ],
        },
        {
            "creator": "AI21 Labs",
            "modelSlugs": [
                "jamba-1-7-mini",
                "jamba-reasoning-3b",
                "jamba-1-5-mini",
                "jamba-1-5-large",
                "jamba-1-6-large",
                "jamba-1-6-mini",
            ],
            "reason": "Current Jamba Mini pricing applies to Mini 2, for which AInsights has no exact slug; Mini 1.7 and all 1.5/1.6 rows are deprecated. Jamba 3B has no hosted API endpoint in the official model table.",
            "sourceUrls": [
                "https://www.ai21.com/pricing/",
                "https://docs.ai21.com/docs/jamba-foundation-models",
            ],
        },
        {
            "creator": "Upstage",
            "modelSlugs": [
                "solar-open-100b-reasoning",
                "solar-pro-2-preview-reasoning",
                "solar-pro-2-reasoning",
                "solar-pro-2-preview",
            ],
            "reason": "Official API pricing identifies the consolidated Solar Pro 2 model but not separate preview/reasoning API IDs or prices. Solar Open is not given a public hosted token price.",
            "sourceUrls": [
                "https://www.upstage.ai/pricing/api",
                "https://console.upstage.ai/docs/models",
            ],
        },
        {
            "creator": "Liquid AI",
            "modelSlugs": [
                "lfm2-24b-a2b",
                "lfm2-8b-a1b",
                "lfm2-2-6b",
                "lfm2-5-1-2b-thinking",
                "lfm2-5-vl-1-6b",
                "lfm2-5-1-2b-instruct",
                "lfm2-5-8b-a1b",
                "lfm-40b",
                "lfm2-1-2b",
            ],
            "reason": "Liquid's official pricing page covers the LFM Open License and self-hosted commercial licensing, not a public Liquid-hosted per-token API.",
            "sourceUrls": ["https://www.liquid.ai/pricing"],
        },
        {
            "creator": "Reka AI",
            "modelSlugs": ["reka-flash-3"],
            "reason": "Official public API docs price and identify reka-flash, not the separate Reka Flash 3 slug; no alias is inferred.",
            "sourceUrls": [
                "https://docs.reka.ai/pricing",
                "https://docs.reka.ai/chat/models",
            ],
        },
        {
            "creator": "Sarvam",
            "modelSlugs": ["sarvam-m-reasoning"],
            "reason": "Official model docs say Sarvam-M is deprecated and no longer available through the API.",
            "sourceUrls": ["https://docs.sarvam.ai/api/getting-started/models"],
        },
        {
            "creator": "Additional audited gaps",
            "modelSlugs": [
                "hermes-4-llama-3-1-405b",
                "hermes-4-llama-3-1-70b",
                "trinity-large-thinking",
                "intellect-3",
            ],
            "reason": "Nous Research, Arcee AI, and Prime Intellect expose products or inference surfaces, but no directly verifiable official public per-model token price was found for these exact author-model slugs. Aggregator prices are intentionally not substituted.",
            "sourceUrls": [
                "https://portal.nousresearch.com/",
                "https://docs.arcee.ai/",
                "https://docs.primeintellect.ai/api-reference/inference-models",
            ],
        },
    ]

    return {
        "schemaVersion": 1,
        "checkedAt": CHECKED_AT,
        "scope": "Verified model-author first-party public APIs; one offer per exact AInsights model slug.",
        "providers": providers,
        "plans": plans,
        "offers": offers,
        "sources": sources,
        "exchangeRates": {
            "INR": {
                "unitsPerUsd": round(INR_PER_USD, 9),
                "usdPerUnit": round(USD_PER_INR, 9),
                "asOf": FX_AS_OF,
                "sourceId": INR_FX_SOURCE_ID,
                "notes": "Cross rate from ECB INR/EUR 110.1228 and USD/EUR 1.1555 reference rates.",
            }
        },
        "exclusions": exclusions,
        "mergeNotes": [
            "Upstage and Inception reuse their existing provider ids so an official fragment merge replaces, rather than duplicates, their community-imported aggregator slices.",
            "Zero-dollar Sarvam rates are literal official 'Free per token' prices. Sarvam 30B remains finite but non-comparable because it is deprecated.",
            "No offer is inferred from an aggregator, an open-weight license, an alias without official evidence, or a generic model-family price that cannot be tied to an exact current slug.",
        ],
    }


def validate(fragment: dict[str, Any]) -> None:
    model_payload = json.loads(MODELS_PATH.read_text(encoding="utf-8"))
    valid_slugs = {row["slug"] for row in model_payload["models"]}
    provider_ids = [row["id"] for row in fragment["providers"]]
    plan_ids = [row["id"] for row in fragment["plans"]]
    offer_ids = [row["id"] for row in fragment["offers"]]
    source_ids = [row["id"] for row in fragment["sources"]]
    for label, values in (
        ("provider", provider_ids),
        ("plan", plan_ids),
        ("offer", offer_ids),
        ("source", source_ids),
    ):
        duplicates = sorted({value for value in values if values.count(value) > 1})
        if duplicates:
            raise ValueError(f"duplicate {label} ids: {duplicates}")
    provider_set = set(provider_ids)
    plan_map = {row["id"]: row for row in fragment["plans"]}
    source_set = set(source_ids)
    for currency, rate in fragment.get("exchangeRates", {}).items():
        if currency == "USD":
            raise ValueError("USD must not be stored as an exchange-rate override")
        if not isinstance(rate.get("usdPerUnit"), (int, float)) or rate["usdPerUnit"] <= 0:
            raise ValueError(f"invalid usdPerUnit for {currency}")
        if not isinstance(rate.get("unitsPerUsd"), (int, float)) or rate["unitsPerUsd"] <= 0:
            raise ValueError(f"invalid unitsPerUsd for {currency}")
        if rate.get("sourceId") not in source_set:
            raise ValueError(f"unknown exchange-rate source for {currency}")
    for row in fragment["providers"] + fragment["plans"] + fragment["offers"]:
        unknown_sources = set(row.get("sourceIds", [])) - source_set
        if unknown_sources:
            raise ValueError(f"unknown source ids on {row['id']}: {sorted(unknown_sources)}")
    for row in fragment["plans"]:
        if row["providerId"] not in provider_set:
            raise ValueError(f"orphan plan: {row['id']}")
    for row in fragment["offers"]:
        if len(row.get("modelSlugs", [])) != 1:
            raise ValueError(f"offer must contain exactly one model slug: {row['id']}")
        if row["modelSlugs"][0] not in valid_slugs:
            raise ValueError(f"unknown model slug on {row['id']}: {row['modelSlugs'][0]}")
        plan = plan_map.get(row["planId"])
        if not plan or plan["providerId"] != row["providerId"]:
            raise ValueError(f"offer/plan provider mismatch: {row['id']}")
        for field in ("inputPerMillionTokensUsd", "outputPerMillionTokensUsd"):
            if not isinstance(row.get(field), (int, float)):
                raise ValueError(f"non-finite {field} on {row['id']}")
            if row[field] == 0 and not row.get("publishedZeroRate"):
                raise ValueError(f"unmarked published zero rate on {row['id']}")
        if row.get("publishedZeroRate") and not (
            row["inputPerMillionTokensUsd"] == 0
            and row["outputPerMillionTokensUsd"] == 0
        ):
            raise ValueError(f"publishedZeroRate requires zero input/output: {row['id']}")


def main() -> int:
    fragment = build_fragment()
    validate(fragment)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(fragment, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "output": str(OUTPUT_PATH),
                "providers": len(fragment["providers"]),
                "plans": len(fragment["plans"]),
                "offers": len(fragment["offers"]),
                "sources": len(fragment["sources"]),
                "excludedGroups": len(fragment["exclusions"]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
