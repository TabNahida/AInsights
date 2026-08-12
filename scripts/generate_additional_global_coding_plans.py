#!/usr/bin/env python3
"""Generate a researched fragment for additional global coding plans.

The fragment deliberately separates plan/model rows and never expands offers
through ``planVariants``.  A finite token price is emitted only where the
platform publishes either the rate itself or an exact public-price formula.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MODELS_PATH = ROOT / "docs" / "data" / "models.json"
OUTPUT_PATH = ROOT / "data" / "pricing" / "research_additional_global_coding_plans.json"
CHECKED_AT = "2026-08-12"


def plan(
    plan_id: str,
    provider_id: str,
    name: str,
    monthly_price_usd: float | None,
    source_ids: list[str],
    **extra: Any,
) -> dict[str, Any]:
    return {
        "id": plan_id,
        "providerId": provider_id,
        "name": name,
        "billingType": extra.pop("billingType", "subscription"),
        "displayType": extra.pop("displayType", "coding"),
        "currency": "USD",
        "monthlyPriceUsd": monthly_price_usd,
        "comparisonClass": extra.pop("comparisonClass", "non-comparable"),
        "sourceIds": source_ids,
        **extra,
    }


def support_offer(
    offer_id: str,
    provider_id: str,
    plan_id: str,
    slug: str,
    provider_model_id: str,
    source_ids: list[str],
    **extra: Any,
) -> dict[str, Any]:
    return {
        "id": offer_id,
        "providerId": provider_id,
        "planId": plan_id,
        "modelSlugs": [slug],
        "providerModelId": provider_model_id,
        "pricingKind": extra.pop("pricingKind", "non-comparable-subscription"),
        "comparable": False,
        "inputPerMillionTokensUsd": None,
        "cacheReadPerMillionTokensUsd": None,
        "cacheWritePerMillionTokensUsd": None,
        "outputPerMillionTokensUsd": None,
        "sourceIds": source_ids,
        **extra,
    }


def token_offer(
    offer_id: str,
    provider_id: str,
    plan_id: str,
    slug: str,
    provider_model_id: str,
    rates: tuple[float, float | None, float | None, float],
    source_ids: list[str],
    factor: float = 1.0,
    **extra: Any,
) -> dict[str, Any]:
    input_rate, cache_read, cache_write, output_rate = rates

    def scaled(value: float | None) -> float | None:
        return None if value is None else round(value * factor, 9)

    return {
        "id": offer_id,
        "providerId": provider_id,
        "planId": plan_id,
        "modelSlugs": [slug],
        "providerModelId": provider_model_id,
        "pricingKind": extra.pop("pricingKind", "per-token-overage"),
        "comparable": extra.pop("comparable", False),
        "inputPerMillionTokensUsd": scaled(input_rate),
        "cacheReadPerMillionTokensUsd": scaled(cache_read),
        "cacheWritePerMillionTokensUsd": scaled(cache_write),
        "outputPerMillionTokensUsd": scaled(output_rate),
        "sourceIds": source_ids,
        **extra,
    }


# Exact public per-token rows that are independently visible in Cognition's
# official model table.  Replit and Tabnine publish formulas tied to public API
# list price; their derived rows cite both the platform rule and this table.
PUBLIC_RATE_MODELS: dict[str, tuple[str, tuple[float, float | None, float | None, float]]] = {
    "claude-opus-5": ("claude-opus-5", (5, 0.5, 6.25, 25)),
    "claude-opus-4-8": ("claude-opus-4-8", (5, 0.5, 6.25, 25)),
    "claude-opus-4-7": ("claude-opus-4-7", (5, 0.5, 6.25, 25)),
    "claude-opus-4-6": ("claude-opus-4-6", (5, 0.5, 6.25, 25)),
    "claude-opus-4-5": ("claude-opus-4-5", (5, 0.5, 6.25, 25)),
    "claude-4-1-opus": ("claude-opus-4.1", (15, 1.5, 18.75, 75)),
    "claude-sonnet-4-6": ("claude-sonnet-4-6", (3, 0.3, 3.75, 15)),
    "claude-4-5-sonnet": ("claude-sonnet-4.5", (3, 0.3, 3.75, 15)),
    "claude-4-sonnet": ("claude-sonnet-4", (3, 0.3, 3.75, 15)),
    "claude-4-5-haiku": ("claude-haiku-4.5", (1, 0.1, 1.25, 5)),
    "gpt-5-6-sol": ("gpt-5.6-sol", (5, 0.5, 6.25, 30)),
    "gpt-5-6-terra": ("gpt-5.6-terra", (2, 0.2, 2.5, 12)),
    "gpt-5-6-luna": ("gpt-5.6-luna", (0.2, 0.02, 0.25, 1.2)),
    "gpt-5-5": ("gpt-5.5", (5, 0.5, None, 30)),
    "gpt-5-4": ("gpt-5.4", (2.5, 0.25, None, 15)),
    "gpt-5-3-codex": ("gpt-5.3-codex", (1.75, 0.175, None, 14)),
    "gpt-5-2-codex": ("gpt-5.2-codex", (1.75, 0.175, None, 14)),
    "gpt-5-2": ("gpt-5.2", (1.75, 0.175, None, 14)),
    "gpt-5": ("gpt-5", (1.25, 0.125, None, 10)),
    "gpt-4o": ("gpt-4o", (2.5, 1.25, None, 10)),
    "gpt-4-1": ("gpt-4.1", (2, 0.5, None, 8)),
    "o3": ("o3", (2, 0.5, None, 8)),
    "gemini-2-5-pro": ("gemini-2.5-pro", (1.25, 0.125, 4.5, 10)),
    "deepseek-v4-pro": ("deepseek-v4", (1.74, 0.15, 0, 3.48)),
    "glm-5-1": ("glm-5-1", (1.4, 0.26, 0, 4.4)),
    "glm-5-2": ("glm-5-2", (1.4, 0.26, 0, 4.4)),
    "kimi-k2-5": ("kimi-k2-5", (0.6, 0.1, 0, 3)),
    "kimi-k2-6": ("kimi-k2-6", (0.95, 0.16, 0, 4)),
    "minimax-m2-5": ("minimax-m2-5", (0.3, 0.03, 0.375, 1.2)),
}


# Rows whose official Devin model label or ID maps exactly to a current
# AInsights slug.  Rates are copied from the TEAMS_TIER_PRO table; duplicate
# aliases with the same label/rate are intentionally collapsed.
DEVIN_MODELS: list[tuple[str, str, tuple[float, float | None, float | None, float]]] = [
    ("gpt-4o", "MODEL_CHAT_GPT_4O_2024_08_06", (2.5, 1.25, 0, 10)),
    ("gpt-4-1", "MODEL_CHAT_GPT_4_1_2025_04_14", (2, 0.5, 0, 8)),
    ("gpt-5-codex", "MODEL_CHAT_GPT_5_CODEX", (1.25, 0.125, 0, 10)),
    ("o3", "MODEL_CHAT_O3", (2, 0.5, 0, 8)),
    ("claude-opus-4-5", "MODEL_CLAUDE_4_5_OPUS", (5, 0.5, 6.25, 25)),
    ("claude-opus-4-5-thinking", "MODEL_CLAUDE_4_5_OPUS_THINKING", (5, 0.5, 6.25, 25)),
    ("gemini-2-5-pro", "MODEL_GOOGLE_GEMINI_2_5_PRO", (1.25, 0.125, 4.5, 10)),
    ("gpt-5-1-codex-mini", "MODEL_PRIVATE_19", (1.25, 0.125, 0, 10)),
    ("grok-code-fast-1", "MODEL_PRIVATE_4", (0.2, 0.02, 0, 1.5)),
    ("claude-opus-4-6", "claude-opus-4-6", (5, 0.5, 6.25, 25)),
    ("claude-opus-5-high", "claude-opus-5-high", (5, 0.5, 6.25, 25)),
    ("claude-opus-5-low", "claude-opus-5-low", (5, 0.5, 6.25, 25)),
    ("claude-opus-5-medium", "claude-opus-5-medium", (5, 0.5, 6.25, 25)),
    ("claude-opus-5-xhigh", "claude-opus-5-xhigh", (5, 0.5, 6.25, 25)),
    ("claude-sonnet-4-6", "claude-sonnet-4-6", (3, 0.3, 3.75, 15)),
    ("deepseek-v4-pro", "deepseek-v4", (1.74, 0.15, 0, 3.48)),
    ("gemini-3-5-flash-medium", "gemini-3-5-flash-medium", (1.5, 0.15, 1, 9)),
    ("gemini-3-5-flash-minimal", "gemini-3-5-flash-minimal", (1.5, 0.15, 1, 9)),
    ("glm-5-1", "glm-5-1", (1.4, 0.26, 0, 4.4)),
    ("glm-5-2", "glm-5-2", (1.4, 0.26, 0, 4.4)),
    ("gpt-5-4-low", "gpt-5-4-low", (2.5, 0.25, 0, 15)),
    ("gpt-5-4-mini-medium", "gpt-5-4-mini-medium", (0.75, 0.075, 0, 4.5)),
    ("gpt-5-5-high", "gpt-5-5-high", (5, 0.5, 0, 30)),
    ("gpt-5-5-low", "gpt-5-5-low", (5, 0.5, 0, 30)),
    ("gpt-5-5-medium", "gpt-5-5-medium", (5, 0.5, 0, 30)),
    ("gpt-5-6-luna-high", "gpt-5-6-luna-high", (0.2, 0.02, 0.25, 1.2)),
    ("gpt-5-6-luna-low", "gpt-5-6-luna-low", (0.2, 0.02, 0.25, 1.2)),
    ("gpt-5-6-luna-medium", "gpt-5-6-luna-medium", (0.2, 0.02, 0.25, 1.2)),
    ("gpt-5-6-luna-xhigh", "gpt-5-6-luna-xhigh", (0.2, 0.02, 0.25, 1.2)),
    ("gpt-5-6-sol-high", "gpt-5-6-sol-high", (5, 0.5, 6.25, 30)),
    ("gpt-5-6-sol-low", "gpt-5-6-sol-low", (5, 0.5, 6.25, 30)),
    ("gpt-5-6-sol-medium", "gpt-5-6-sol-medium", (5, 0.5, 6.25, 30)),
    ("gpt-5-6-sol-xhigh", "gpt-5-6-sol-xhigh", (5, 0.5, 6.25, 30)),
    ("gpt-5-6-terra-high", "gpt-5-6-terra-high", (2, 0.2, 2.5, 12)),
    ("gpt-5-6-terra-low", "gpt-5-6-terra-low", (2, 0.2, 2.5, 12)),
    ("gpt-5-6-terra-medium", "gpt-5-6-terra-medium", (2, 0.2, 2.5, 12)),
    ("gpt-5-6-terra-xhigh", "gpt-5-6-terra-xhigh", (2, 0.2, 2.5, 12)),
    ("kimi-k2-5", "kimi-k2-5", (0.6, 0.1, 0, 3)),
    ("kimi-k2-6", "kimi-k2-6", (0.95, 0.16, 0, 4)),
    ("kimi-k3-low", "kimi-k3-low", (3, 0.3, 0, 15)),
    ("minimax-m2-5", "minimax-m2-5", (0.3, 0.03, 0.375, 1.2)),
]


def build_fragment() -> dict[str, Any]:
    valid_slugs = {
        row["slug"]
        for row in json.loads(MODELS_PATH.read_text(encoding="utf-8"))["models"]
    }
    providers: list[dict[str, Any]] = []
    plans: list[dict[str, Any]] = []
    offers: list[dict[str, Any]] = []

    providers.extend(
        [
            {
                "id": "amazon-q-developer",
                "name": "Amazon Q Developer",
                "category": "coding-subscription",
                "url": "https://aws.amazon.com/q/developer/",
                "pricingUrl": "https://aws.amazon.com/q/developer/pricing/",
                "sourceIds": ["amazon-q-pricing-2026-08-12"],
            },
            {
                "id": "augment-code",
                "name": "Augment Code",
                "category": "coding-subscription",
                "url": "https://www.augmentcode.com/",
                "pricingUrl": "https://www.augmentcode.com/pricing",
                "sourceIds": ["augment-pricing-2026-08-12"],
            },
            {
                "id": "sourcegraph-cody",
                "name": "Sourcegraph Cody",
                "category": "coding-subscription",
                "url": "https://sourcegraph.com/docs/cody",
                "pricingUrl": "https://sourcegraph.com/pricing",
                "sourceIds": [
                    "sourcegraph-pricing-2026-08-12",
                    "sourcegraph-cody-models-2026-08-12",
                ],
            },
            {
                "id": "replit",
                "name": "Replit",
                "category": "coding-platform",
                "url": "https://replit.com/",
                "pricingUrl": "https://replit.com/pricing",
                "sourceIds": [
                    "replit-pricing-2026-08-12",
                    "replit-ai-billing-2026-08-12",
                    "replit-ai-integrations-2026-08-12",
                ],
            },
            {
                "id": "devin",
                "name": "Devin",
                "category": "coding-subscription",
                "url": "https://devin.ai/",
                "pricingUrl": "https://devin.ai/pricing",
                "sourceIds": [
                    "devin-pricing-2026-08-12",
                    "devin-self-serve-2026-08-12",
                    "devin-model-rates-2026-08-12",
                    "devin-quota-2026-08-12",
                ],
                "notes": "Kept separate from the legacy Windsurf / Devin catalogue slice; this provider represents current Devin-wide self-serve plans and Devin Desktop extra usage.",
            },
            {
                "id": "tabnine",
                "name": "Tabnine",
                "category": "coding-subscription",
                "url": "https://www.tabnine.com/",
                "pricingUrl": "https://www.tabnine.com/pricing/",
                "sourceIds": [
                    "tabnine-pricing-2026-08-12",
                    "tabnine-models-2026-08-12",
                    "tabnine-headless-pricing-2026-08-12",
                ],
            },
        ]
    )

    # Amazon Q and Augment publish useful plan economics but not an exact model
    # catalogue that can be joined to AInsights without guessing.
    plans.extend(
        [
            plan(
                "amazon-q-free",
                "amazon-q-developer",
                "Free",
                0,
                ["amazon-q-pricing-2026-08-12"],
                includedAgenticRequestsPerMonth=50,
                includedTransformationLocPerMonth=1000,
                quotaLabel="50 agentic requests and 1,000 Java transformation LOC / month",
            ),
            plan(
                "amazon-q-pro",
                "amazon-q-developer",
                "Pro",
                19,
                ["amazon-q-pricing-2026-08-12"],
                priceUnit="user-month",
                includedTransformationLocPerUserMonth=4000,
                transformationOverageUsdPerLoc=0.003,
                quotaLabel="Agentic requests included with unpublished limits; 4,000 pooled transformation LOC per user-month",
            ),
            plan(
                "augment-business",
                "augment-code",
                "Business",
                100,
                ["augment-pricing-2026-08-12"],
                includedApiSpendUsd=100,
                includedSeats=50,
                llmServiceFeeRate=0.40,
                quotaLabel="$100 pooled usage across LLM, Context Engine, and compute; up to 50 seats",
            ),
            plan(
                "augment-enterprise",
                "augment-code",
                "Enterprise",
                None,
                ["augment-pricing-2026-08-12"],
                billingType="contract",
                quotaLabel="Custom user pricing, usage limits, and volume discounts",
            ),
            plan(
                "sourcegraph-cody-enterprise",
                "sourcegraph-cody",
                "Enterprise",
                None,
                ["sourcegraph-pricing-2026-08-12", "sourcegraph-cody-models-2026-08-12"],
                billingType="contract",
                startingContractPriceUsd=16000,
                quotaLabel="Starting at $16K; AI credits scale with team size",
            ),
        ]
    )

    cody_models = [
        ("claude-opus-5", "Claude Opus 5"),
        ("claude-opus-4-8", "Claude Opus 4.8"),
        ("claude-opus-4-7", "Claude Opus 4.7"),
        ("claude-opus-4-6", "Claude Opus 4.6"),
        ("claude-sonnet-5", "Claude Sonnet 5"),
        ("claude-sonnet-4-6", "Claude Sonnet 4.6"),
        ("claude-4-5-sonnet", "Claude Sonnet 4.5"),
        ("claude-4-5-sonnet-thinking", "Claude Sonnet 4.5 with Thinking"),
        ("claude-opus-4-5", "Claude Opus 4.5"),
        ("claude-opus-4-5-thinking", "Claude Opus 4.5 with Thinking"),
        ("claude-4-5-haiku", "Claude Haiku 4.5"),
        ("claude-4-5-haiku-reasoning", "Claude Haiku 4.5 with Thinking"),
        ("gemini-2-5-flash", "Gemini 2.5 Flash"),
        ("gemini-2-5-pro", "Gemini 2.5 Pro"),
        ("gemini-3-1-flash-lite-preview", "Gemini 3.1 Flash Lite"),
        ("gemini-3-1-pro-preview", "Gemini 3.1 Pro"),
        ("gemini-3-5-flash", "Gemini 3.5 Flash"),
        ("gpt-5-6-sol", "GPT-5.6 Sol"),
        ("gpt-5-6-terra", "GPT-5.6 Terra"),
        ("gpt-5-6-luna", "GPT-5.6 Luna"),
        ("gpt-5-4", "GPT-5.4"),
        ("gpt-5-4-mini", "GPT-5.4 mini"),
        ("gpt-5-4-nano", "GPT-5.4 nano"),
        ("gpt-5-2", "GPT-5.2"),
        ("gpt-5-1", "GPT-5.1"),
        ("gpt-5", "GPT-5"),
        ("gpt-5-mini", "GPT-5 mini"),
        ("gpt-5-nano", "GPT-5 nano"),
        ("gpt-4o", "GPT-4o"),
        ("gpt-4-1", "GPT-4.1"),
        ("gpt-4o-mini", "GPT-4o-mini"),
        ("gpt-4-1-mini", "GPT-4.1-mini"),
        ("o3", "o3"),
    ]
    for slug, model_id in cody_models:
        offers.append(
            support_offer(
                f"sourcegraph-cody-enterprise-{slug}",
                "sourcegraph-cody",
                "sourcegraph-cody-enterprise",
                slug,
                model_id,
                ["sourcegraph-cody-models-2026-08-12", "sourcegraph-pricing-2026-08-12"],
                quotaScope="contract-ai-credits",
                notes="Cody publishes exact support but not the contract credit quantity or a per-model credit-to-token conversion.",
            )
        )

    # Replit subscription credits and discounted credit packs can fund managed
    # model calls at public API price.  Effective rates assume the entire credit
    # value is consumed by one model and are therefore display-only.
    replit_subscription_plans = [
        ("replit-starter", "Starter", 0, None, None),
        ("replit-core-monthly", "Core Monthly", 25, 25, 1.0),
        ("replit-core-annual", "Core Annual", 20, 25, 0.8),
        ("replit-pro-monthly", "Pro Monthly", 100, 100, 1.0),
        ("replit-pro-annual", "Pro Annual", 95, 100, 0.95),
        ("replit-enterprise", "Enterprise", None, None, None),
    ]
    for plan_id, name, price, credits, multiplier in replit_subscription_plans:
        plans.append(
            plan(
                plan_id,
                "replit",
                name,
                price,
                ["replit-pricing-2026-08-12", "replit-ai-billing-2026-08-12"],
                billingType=("contract" if plan_id == "replit-enterprise" else "subscription"),
                includedCreditsUsd=credits,
                fullCreditEffectiveMultiplier=multiplier,
                quotaLabel=(
                    "Free daily Agent credits; Replit AI Integrations disabled"
                    if plan_id == "replit-starter"
                    else (f"${credits:g} monthly credits" if credits is not None else "Custom")
                ),
            )
        )
    plans.append(
        plan(
            "replit-ai-integrations-at-cost",
            "replit",
            "AI Integrations at public API price",
            None,
            ["replit-ai-integrations-2026-08-12", "devin-model-rates-2026-08-12"],
            billingType="payg",
            displayType="token",
            requiresSubscription=True,
            eligibleSubscriptionPlanIds=[
                "replit-core-monthly",
                "replit-core-annual",
                "replit-pro-monthly",
                "replit-pro-annual",
                "replit-enterprise",
            ],
            quotaLabel="Public API list price; billed to Replit credits",
        )
    )
    replit_credit_packs = [
        ("replit-credit-pack-100", "$100 credit pack", 100, 100),
        ("replit-credit-pack-300", "$300 credit pack", 290, 300),
        ("replit-credit-pack-500", "$500 credit pack", 480, 500),
        ("replit-credit-pack-1000", "$1,000 credit pack", 950, 1000),
    ]
    for plan_id, name, purchase_price, credit_value in replit_credit_packs:
        plans.append(
            plan(
                plan_id,
                "replit",
                name,
                None,
                ["replit-credit-packs-2026-08-12", "replit-ai-integrations-2026-08-12"],
                billingType="prepaid",
                displayType="token",
                purchasePriceUsd=purchase_price,
                includedCreditsUsd=credit_value,
                fullCreditEffectiveMultiplier=purchase_price / credit_value,
                creditExpirationMonths=6,
                requiresSubscription=True,
                eligibleSubscriptionPlanIds=[
                    "replit-core-monthly",
                    "replit-core-annual",
                    "replit-pro-monthly",
                    "replit-pro-annual",
                ],
                quotaLabel=f"Pay ${purchase_price:g} for ${credit_value:g} credits; expires after 6 months",
            )
        )

    replit_integration_slugs = [
        "gpt-5-6-sol",
        "gpt-5-6-terra",
        "gpt-5-6-luna",
        "claude-opus-5",
        "claude-opus-4-8",
        "claude-opus-4-7",
        "claude-opus-4-6",
        "claude-opus-4-5",
        "claude-4-1-opus",
        "claude-sonnet-4-6",
        "claude-4-5-sonnet",
        "claude-4-5-haiku",
    ]
    for slug in replit_integration_slugs:
        model_id, rates = PUBLIC_RATE_MODELS[slug]
        offers.append(
            token_offer(
                f"replit-at-cost-{slug}",
                "replit",
                "replit-ai-integrations-at-cost",
                slug,
                model_id,
                rates,
                ["replit-ai-integrations-2026-08-12", "devin-model-rates-2026-08-12"],
                requiresSubscription=True,
                notes="Replit publishes managed calls at public API price; the numeric public-list row is independently visible in Cognition's official model table.",
            )
        )
        for plan_id, _name, _price, _credits, multiplier in replit_subscription_plans:
            if multiplier is None:
                continue
            offers.append(
                token_offer(
                    f"{plan_id}-{slug}",
                    "replit",
                    plan_id,
                    slug,
                    model_id,
                    rates,
                    [
                        "replit-pricing-2026-08-12",
                        "replit-ai-integrations-2026-08-12",
                        "devin-model-rates-2026-08-12",
                    ],
                    factor=multiplier,
                    pricingKind="effective-subscription",
                    bestCaseOnly=True,
                    fullCreditUtilizationAssumed=True,
                    calculation=f"Public API rate × {multiplier:g}, from monthly-equivalent plan cost divided by included credit value.",
                    notes="Display-only full-credit effective rate; Replit credits can also be spent on Agent, publishing, databases, storage, and compute.",
                )
            )
        for pack_id, _name, purchase_price, credit_value in replit_credit_packs:
            multiplier = purchase_price / credit_value
            offers.append(
                token_offer(
                    f"{pack_id}-{slug}",
                    "replit",
                    pack_id,
                    slug,
                    model_id,
                    rates,
                    [
                        "replit-credit-packs-2026-08-12",
                        "replit-ai-integrations-2026-08-12",
                        "devin-model-rates-2026-08-12",
                    ],
                    factor=multiplier,
                    pricingKind="effective-prepaid-credit",
                    bestCaseOnly=True,
                    fullCreditUtilizationAssumed=True,
                    requiresSubscription=True,
                    calculation=f"Public API rate × ${purchase_price:g}/${credit_value:g} credit value.",
                    notes="Display-only full-credit effective rate; packs expire after six months and can fund non-model Replit services.",
                )
            )

    replit_agent_models = {
        "lite": [
            ("gpt-5-6-luna", "GPT-5.6 Luna"),
            ("gemini-3-5-flash", "Gemini 3.5 Flash"),
            ("deepseek-v4-flash", "DeepSeek V4 Flash"),
        ],
        "paid": [
            ("claude-sonnet-4-6", "Claude Sonnet 4.6"),
            ("claude-sonnet-5", "Claude Sonnet 5"),
            ("gpt-5-6-terra", "GPT-5.6 Terra"),
            ("glm-5-2", "GLM 5.2"),
            ("claude-fable-5", "Claude Fable 5"),
            ("claude-opus-4-8", "Claude Opus 4.8"),
            ("claude-opus-5", "Claude Opus 5"),
            ("kimi-k3", "Kimi K3"),
            ("gpt-5-6-sol", "GPT-5.6 Sol"),
        ],
    }
    for slug, model_id in replit_agent_models["lite"]:
        offers.append(
            support_offer(
                f"replit-starter-agent-{slug}",
                "replit",
                "replit-starter",
                slug,
                model_id,
                ["replit-model-selector-2026-08-12", "replit-ai-billing-2026-08-12"],
                usageMode="Lite",
                quotaScope="daily-agent-credits-with-monthly-cap",
                notes="Effort-based task pricing has no published fixed token conversion.",
            )
        )
    for plan_id in [
        "replit-core-monthly",
        "replit-core-annual",
        "replit-pro-monthly",
        "replit-pro-annual",
        "replit-enterprise",
    ]:
        for usage_mode, model_rows in replit_agent_models.items():
            for slug, model_id in model_rows:
                # The paid self-serve plan already has one finite plan/model
                # row when the same model is also exposed by AI Integrations.
                # Keep the fragment strictly one row per plan/model pair.
                if plan_id != "replit-enterprise" and slug in replit_integration_slugs:
                    continue
                offers.append(
                    support_offer(
                        f"{plan_id}-agent-{slug}",
                        "replit",
                        plan_id,
                        slug,
                        model_id,
                        ["replit-model-selector-2026-08-12", "replit-ai-billing-2026-08-12"],
                        usageMode=("Lite" if usage_mode == "lite" else "Economy/Power"),
                        quotaScope="effort-based-agent-credits",
                        supportStatus=("conditional" if plan_id == "replit-enterprise" else "active"),
                        notes="Agent task cost varies with effort, context, and routing; it is not a fixed per-token price.",
                    )
                )

    # Devin publishes current plan prices and an exact Desktop token table.
    devin_plan_rows = [
        ("devin-free", "Free", 0, "Limited quota; no paid extra usage"),
        ("devin-pro", "Pro", 20, "Daily and weekly quota; extra usage at API list price"),
        ("devin-max", "Max", 200, "Larger weekly quota with no daily cap; extra usage at API list price"),
        ("devin-teams", "Teams", 80, "$80/month minimum; $40/full seat; shared on-demand credits"),
        ("devin-enterprise", "Enterprise", None, "Custom contract and ACU allocation"),
    ]
    for plan_id, name, price, quota in devin_plan_rows:
        plans.append(
            plan(
                plan_id,
                "devin",
                name,
                price,
                ["devin-pricing-2026-08-12", "devin-self-serve-2026-08-12"],
                billingType=("contract" if plan_id == "devin-enterprise" else "subscription"),
                priceUnit=("team-month-minimum" if plan_id == "devin-teams" else "month"),
                fullSeatMonthlyPriceUsd=(40 if plan_id == "devin-teams" else None),
                quotaLabel=quota,
            )
        )
    for plan_id in ("devin-pro", "devin-max", "devin-teams"):
        for slug, model_id, rates in DEVIN_MODELS:
            offers.append(
                token_offer(
                    f"{plan_id}-extra-{slug}",
                    "devin",
                    plan_id,
                    slug,
                    model_id,
                    rates,
                    [
                        "devin-pricing-2026-08-12",
                        "devin-model-rates-2026-08-12",
                        "devin-quota-2026-08-12",
                    ],
                    pricingKind="per-token-overage",
                    requiresIncludedQuotaExhaustion=True,
                    notes="Exact published Devin Desktop extra-usage rate. Included daily/weekly quota is not converted because its quantity is unpublished.",
                )
            )

    # Tabnine annual seat plans add 5% to the selected provider's public price.
    # Exact supported models without a cross-checked numeric base remain
    # support-only rows and will be hidden from finite-price model views.
    tabnine_plan_rows = [
        ("tabnine-code-assistant", "Code Assistant", 39),
        ("tabnine-agentic", "Agentic Platform", 59),
    ]
    for plan_id, name, price in tabnine_plan_rows:
        plans.append(
            plan(
                plan_id,
                "tabnine",
                name,
                price,
                ["tabnine-pricing-2026-08-12", "tabnine-models-2026-08-12"],
                billingCycle="annual",
                priceUnit="user-month-billed-annually",
                llmHandlingFeeRate=0.05,
                quotaLabel="BYO LLM unlimited; Tabnine-hosted reserved token quota at provider price + 5%",
            )
        )
    plans.extend(
        [
            plan(
                "tabnine-headless-business",
                "tabnine",
                "Headless Agents Business",
                1200,
                ["tabnine-headless-pricing-2026-08-12"],
                billingCycle="annual",
                includedProcessedTokensPerMonth=5_000_000_000,
                effectivePlatformUsdPerMillionProcessedTokens=0.24,
                excludesModelProviderTokenCost=True,
                quotaLabel="Up to 5B processed tokens/month; selected LLM provider cost is separate",
            ),
            plan(
                "tabnine-headless-enterprise",
                "tabnine",
                "Headless Agents Enterprise",
                5000,
                ["tabnine-headless-pricing-2026-08-12"],
                billingCycle="annual",
                includedProcessedTokensPerMonth=50_000_000_000,
                effectivePlatformUsdPerMillionProcessedTokens=0.10,
                excludesModelProviderTokenCost=True,
                quotaLabel="Up to 50B processed tokens/month; selected LLM provider cost is separate",
            ),
        ]
    )
    tabnine_models = [
        ("claude-opus-4-8", "Claude 4.8 Opus"),
        ("claude-opus-4-7", "Claude 4.7 Opus"),
        ("claude-sonnet-4-6", "Claude 4.6 Sonnet"),
        ("claude-opus-4-6", "Claude 4.6 Opus"),
        ("claude-4-5-sonnet", "Claude 4.5 Sonnet"),
        ("claude-opus-4-5", "Claude 4.5 Opus"),
        ("claude-4-5-haiku", "Claude 4.5 Haiku"),
        ("claude-4-sonnet", "Claude 4 Sonnet"),
        ("gpt-5-5", "GPT-5.5"),
        ("gpt-5-4", "GPT-5.4"),
        ("gpt-5-3-codex", "GPT-5.3 Codex"),
        ("gpt-5-2-codex", "GPT-5.2 Codex"),
        ("gpt-5-2", "GPT-5.2"),
        ("gpt-5", "GPT-5"),
        ("gpt-4o", "GPT-4o"),
        ("gemini-3-1-pro-preview", "Gemini 3.1 Pro"),
        ("gemini-3-pro", "Gemini 3.0 Pro"),
        ("devstral-small-2", "Devstral-Small-2-24B-Instruct-2512"),
        ("devstral-2", "Devstral-2-123B-Instruct-2512"),
        ("minimax-m2-7", "MiniMax-M2.7"),
        ("glm-4-7", "GLM-4.7"),
        ("qwen3-coder-480b-a35b-instruct", "Qwen-3-Coder-480B-A35B-Instruct"),
        ("qwen3-30b-a3b-instruct", "Qwen-3-30B"),
    ]
    for plan_id, _name, _price in tabnine_plan_rows:
        for slug, model_id in tabnine_models:
            if slug in PUBLIC_RATE_MODELS:
                _public_id, rates = PUBLIC_RATE_MODELS[slug]
                offers.append(
                    token_offer(
                        f"{plan_id}-{slug}",
                        "tabnine",
                        plan_id,
                        slug,
                        model_id,
                        rates,
                        [
                            "tabnine-pricing-2026-08-12",
                            "tabnine-models-2026-08-12",
                            "devin-model-rates-2026-08-12",
                        ],
                        factor=1.05,
                        pricingKind="per-token-plus-service-fee",
                        requiresSubscription=True,
                        calculation="Public API list rate × 1.05 (Tabnine's published 5% handling fee).",
                        notes="Marginal hosted-token rate; the annual Tabnine seat fee is separate.",
                    )
                )
            else:
                offers.append(
                    support_offer(
                        f"{plan_id}-{slug}",
                        "tabnine",
                        plan_id,
                        slug,
                        model_id,
                        ["tabnine-pricing-2026-08-12", "tabnine-models-2026-08-12"],
                        quotaScope="provider-price-plus-five-percent",
                        notes="Exact model support is official, but this research batch did not obtain a sufficiently direct numeric public-list row for the +5% calculation.",
                    )
                )

    unknown_slugs = sorted(
        {
            slug
            for row in offers
            for slug in row.get("modelSlugs", [])
            if slug not in valid_slugs
        }
    )
    if unknown_slugs:
        raise ValueError(f"unknown AInsights model slugs: {unknown_slugs}")
    if any("planVariants" in row for row in offers):
        raise ValueError("additional global fragment must not use planVariants")
    if any(len(row.get("modelSlugs", [])) != 1 for row in offers):
        raise ValueError("every offer must contain exactly one model slug")
    plan_model_keys = [
        (row["providerId"], row["planId"], row["modelSlugs"][0]) for row in offers
    ]
    duplicate_plan_models = sorted(
        {key for key in plan_model_keys if plan_model_keys.count(key) > 1}
    )
    if duplicate_plan_models:
        raise ValueError(f"duplicate provider/plan/model rows: {duplicate_plan_models}")

    for label, rows in (("provider", providers), ("plan", plans), ("offer", offers)):
        ids = [row["id"] for row in rows]
        duplicates = sorted({value for value in ids if ids.count(value) > 1})
        if duplicates:
            raise ValueError(f"duplicate {label} ids: {duplicates}")

    sources = [
        {
            "id": "amazon-q-pricing-2026-08-12",
            "title": "Amazon Q Developer pricing",
            "publisher": "Amazon Web Services",
            "url": "https://aws.amazon.com/q/developer/pricing/",
            "kind": "official-pricing",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Free has 50 agentic requests and 1,000 transformation LOC/month; Pro is $19/user/month with 4,000 pooled LOC and $0.003/LOC overage. Pro's agentic-request quantity is unpublished.",
        },
        {
            "id": "augment-pricing-2026-08-12",
            "title": "Augment Code pricing",
            "publisher": "Augment Code",
            "url": "https://www.augmentcode.com/pricing",
            "kind": "official-pricing",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Business is $100/month for up to 50 seats with $100 pooled usage; LLM inference is provider public API list price plus a 40% service fee. The page does not list exact models.",
        },
        {
            "id": "sourcegraph-pricing-2026-08-12",
            "title": "Sourcegraph pricing",
            "publisher": "Sourcegraph",
            "url": "https://sourcegraph.com/pricing",
            "kind": "official-pricing",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Current public offer is Enterprise starting at $16K with AI credits that scale with team size; the page does not publish a billing period or finite credit quantity.",
        },
        {
            "id": "sourcegraph-cody-models-2026-08-12",
            "title": "Cody supported LLMs",
            "publisher": "Sourcegraph",
            "url": "https://sourcegraph.com/docs/cody/capabilities/supported-models",
            "kind": "official-model-list",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
        },
        {
            "id": "replit-pricing-2026-08-12",
            "title": "Replit pricing",
            "publisher": "Replit",
            "url": "https://replit.com/pricing",
            "kind": "official-pricing",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Core is $25 monthly or $20/month annual with $25 credits; Pro is $100 monthly or $95/month annual with $100 credits.",
        },
        {
            "id": "replit-ai-billing-2026-08-12",
            "title": "Replit AI billing",
            "publisher": "Replit",
            "url": "https://docs.replit.com/billing/ai-billing",
            "kind": "official-documentation",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Agent uses effort-based task/checkpoint pricing; third-party Agent services are billed at provider public API rates.",
        },
        {
            "id": "replit-ai-integrations-2026-08-12",
            "title": "Replit AI Integrations",
            "publisher": "Replit",
            "url": "https://docs.replit.com/features/integrations/replit-ai-integrations",
            "kind": "official-pricing-and-model-list",
            "asOf": "2026-08-01",
            "accessedAt": CHECKED_AT,
            "notes": "Publishes exact managed model IDs and states usage is billed to Replit credits at public API price. Requires Core; Pro/Enterprise admins must enable access.",
        },
        {
            "id": "replit-model-selector-2026-08-12",
            "title": "Replit Agent model selector",
            "publisher": "Replit",
            "url": "https://docs.replit.com/features/agent/model-selector",
            "kind": "official-model-list",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
        },
        {
            "id": "replit-credit-packs-2026-08-12",
            "title": "Replit credit packs and spend controls",
            "publisher": "Replit",
            "url": "https://docs.replit.com/billing/managing-spend",
            "kind": "official-pricing",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "$100/$100, $290/$300, $480/$500, and $950/$1,000 packs; packs expire after six months and require Core or Pro.",
        },
        {
            "id": "devin-pricing-2026-08-12",
            "title": "Devin plans and pricing",
            "publisher": "Cognition",
            "url": "https://devin.ai/pricing",
            "kind": "official-pricing",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
        },
        {
            "id": "devin-self-serve-2026-08-12",
            "title": "Devin self-serve plans",
            "publisher": "Cognition",
            "url": "https://docs.devin.ai/admin/billing/self-serve",
            "kind": "official-documentation",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Documents $20 Pro, $200 Max, the $80 Teams minimum, $40 full seats, and non-expiring on-demand credits.",
        },
        {
            "id": "devin-model-rates-2026-08-12",
            "title": "Devin Desktop AI models and token prices",
            "publisher": "Cognition",
            "url": "https://docs.devin.ai/desktop/models",
            "kind": "official-pricing-and-model-list",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Official user-facing tables publish exact model IDs and input, cache-input, and output USD per million token rates for Pro and Enterprise tiers.",
        },
        {
            "id": "devin-quota-2026-08-12",
            "title": "Devin Desktop quota-based usage",
            "publisher": "Cognition",
            "url": "https://docs.devin.ai/desktop/accounts/quota",
            "kind": "official-documentation",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Included daily/weekly allowances are unpublished; paid extra usage is billed at the model's API list price based on tokens used.",
        },
        {
            "id": "tabnine-pricing-2026-08-12",
            "title": "Tabnine plans and pricing",
            "publisher": "Tabnine",
            "url": "https://www.tabnine.com/pricing/",
            "kind": "official-pricing",
            "asOf": "2026-05-07",
            "accessedAt": CHECKED_AT,
            "notes": "Code Assistant is $39/user/month annual and Agentic Platform $59/user/month annual. BYO endpoints are unlimited; Tabnine-provided LLM quota is actual provider price plus 5%.",
        },
        {
            "id": "tabnine-models-2026-08-12",
            "title": "Tabnine AI models",
            "publisher": "Tabnine",
            "url": "https://docs.tabnine.com/main/welcome/readme/ai-models",
            "kind": "official-model-list",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
        },
        {
            "id": "tabnine-headless-pricing-2026-08-12",
            "title": "Tabnine Headless Agent pricing",
            "publisher": "Tabnine",
            "url": "https://www.tabnine.com/headless-agent-pricing/",
            "kind": "official-pricing",
            "asOf": "2026-03-24",
            "accessedAt": CHECKED_AT,
            "notes": "Business is $1,200/month annual for up to 5B processed tokens; Enterprise is $5,000/month annual for up to 50B. Selected LLM provider charges are separate.",
        },
    ]

    return {
        "schemaVersion": 1,
        "mergeTarget": "data/pricing/provider_pricing.json",
        "checkedAt": CHECKED_AT,
        "researchScope": "Additional global coding subscriptions, hosted-model overage, prepaid credit packs, and token-capacity plans",
        "comparisonPolicy": {
            "finiteMarginalRatesBehindSubscription": "display-only-non-comparable",
            "fullCreditEffectiveRates": "display-only-best-case",
            "unpublishedQuotaOrConversion": "support-only-null-rate",
            "notes": "No request, task, work-credit, ACU, or unspecified contract allowance is converted to tokens without a published formula.",
        },
        "providers": providers,
        "plans": plans,
        "offers": offers,
        "sources": sources,
        "exclusions": [
            {
                "provider": "Amazon Q Developer",
                "reason": "The pricing page says latest Claude models but publishes no exact model names and no finite Pro agentic-request quantity; no model offers were guessed.",
            },
            {
                "provider": "Augment Code",
                "reason": "The +40% LLM formula is exact, but the public pricing page does not identify the selectable model catalogue; plans are retained without model offers.",
            },
            {
                "provider": "Sourcegraph Cody",
                "reason": "Exact supported models are retained as support-only because current Enterprise AI-credit quantities and a credit-to-token formula are not public.",
            },
            {
                "provider": "Replit Agent",
                "reason": "Agent uses effort/checkpoint pricing. Exact models are retained as support-only; only separate Replit AI Integrations and credit-pack derivations have finite token rows.",
            },
            {
                "provider": "Devin",
                "reason": "Included daily/weekly quotas are unpublished, so only exact paid extra-usage token rates are finite. Enterprise ACU contract economics are not converted.",
            },
            {
                "provider": "Tabnine Headless Agents",
                "reason": "The derived $0.24/$0.10 per million processed-token platform capacity excludes the separately paid LLM and is stored on the plan, not misrepresented as a model price.",
            },
            {
                "provider": "Continue",
                "reason": "The official continue.dev pricing route returned 404 in this research batch; no current paid plan was inferred from historical third-party pages.",
            },
            {
                "provider": "Roo Code",
                "reason": "The official pricing route redirected to roomote.dev and this batch did not establish an authoritative product/plan identity; no cross-brand mapping was guessed.",
            },
        ],
        "mergeNotes": [
            "All offers contain one exact AInsights slug and no planVariants.",
            "Replit credit-pack and annual-plan rates assume full use of credits on one model and remain non-comparable best-case displays.",
            "Devin numeric rows are paid extra-usage rates, not a conversion of the unpublished included quota.",
            "Tabnine finite rows apply the official 5% handling fee; the annual seat fee remains separate.",
            "Amazon Q, Augment, Sourcegraph Cody, Replit Agent, and unresolved Tabnine rows remain plan/support data rather than invented token prices.",
        ],
    }


def main() -> int:
    fragment = build_fragment()
    OUTPUT_PATH.write_text(
        json.dumps(fragment, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    finite_offers = sum(
        1
        for row in fragment["offers"]
        if isinstance(row.get("inputPerMillionTokensUsd"), (int, float))
        or isinstance(row.get("outputPerMillionTokensUsd"), (int, float))
    )
    print(
        json.dumps(
            {
                "output": str(OUTPUT_PATH),
                "providers": len(fragment["providers"]),
                "plans": len(fragment["plans"]),
                "offers": len(fragment["offers"]),
                "finiteOffers": finite_offers,
                "supportOnlyOffers": len(fragment["offers"]) - finite_offers,
                "sources": len(fragment["sources"]),
                "exclusions": len(fragment["exclusions"]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
