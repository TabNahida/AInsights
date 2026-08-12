#!/usr/bin/env python3
"""Generate researched global coding-plan and at-cost inference pricing rows."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOGUE_PATH = ROOT / "data" / "pricing" / "provider_pricing.json"
MODELS_PATH = ROOT / "docs" / "data" / "models.json"
OUTPUT_PATH = ROOT / "data" / "pricing" / "research_global_coding_plans.json"
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


def non_comparable_offer(
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
        "outputPerMillionTokensUsd": None,
        "sourceIds": source_ids,
        **extra,
    }


def scaled(value: Any, factor: float) -> float | None:
    if not isinstance(value, (int, float)):
        return None
    return round(float(value) * factor, 9)


def build_fragment() -> dict[str, Any]:
    catalogue = json.loads(CATALOGUE_PATH.read_text(encoding="utf-8"))
    model_payload = json.loads(MODELS_PATH.read_text(encoding="utf-8"))
    valid_slugs = {row["slug"] for row in model_payload["models"]}

    providers: list[dict[str, Any]] = []
    plans: list[dict[str, Any]] = []
    offers: list[dict[str, Any]] = []

    # Zed publishes an authoritative hosted-model price table.  Keep raw hosted
    # usage separate from subscription-derived rates so a seat fee is never
    # mistaken for a cheaper PAYG endpoint.
    providers.append(
        {
            "id": "zed",
            "name": "Zed",
            "category": "coding-platform",
            "url": "https://zed.dev/",
            "pricingUrl": "https://zed.dev/pricing",
            "sourceIds": ["zed-pricing-2026-08-12", "zed-model-rates-2026-08-12"],
            "notes": "Zed's official table publishes a provider-reference column and a Zed-hosted column 10% above it. Those reference values are not asserted to equal current first-party API pricing.",
        }
    )
    plans.extend(
        [
            plan(
                "zed-personal",
                "zed",
                "Personal",
                0,
                ["zed-pricing-2026-08-12"],
                quotaLabel="No Zed-hosted model credits; BYOK/external agents",
            ),
            plan(
                "zed-pro-trial",
                "zed",
                "Pro Trial",
                0,
                ["zed-pricing-2026-08-12"],
                billingType="trial",
                includedApiSpendUsd=20,
                trialDurationDays=14,
                quotaLabel="$20 token credits or 14 days; Fable, Opus, and GPT Pro excluded",
            ),
            plan(
                "zed-pro",
                "zed",
                "Pro",
                10,
                ["zed-pricing-2026-08-12", "zed-model-rates-2026-08-12"],
                includedApiSpendUsd=5,
                quotaLabel="$5 token credits; overage at the published Zed per-token rate",
                comparisonClass="effective-token-comparable",
            ),
            plan(
                "zed-business",
                "zed",
                "Business",
                30,
                ["zed-pricing-2026-08-12", "zed-model-rates-2026-08-12"],
                quotaLabel="No fixed token credits; hosted usage at the published Zed rate",
            ),
            plan(
                "zed-hosted-overage",
                "zed",
                "Hosted model usage / overage",
                None,
                ["zed-pricing-2026-08-12", "zed-model-rates-2026-08-12"],
                billingType="payg",
                displayType="token",
                quotaLabel="Published marginal Zed-hosted rate; requires Pro or Business access",
                comparisonClass="non-comparable",
                requiresSubscription=True,
                eligibleSubscriptionPlanIds=["zed-pro", "zed-business"],
            ),
        ]
    )
    zed_models = [
        ("claude-fable-5", "claude-fable-5", 11, 1.1, 13.75, 55),
        ("claude-opus-5", "claude-opus-5", 5.5, 0.55, 6.875, 27.5),
        ("claude-opus-4-5", "claude-opus-4.5", 5.5, 0.55, 6.875, 27.5),
        ("claude-opus-4-6", "claude-opus-4.6", 5.5, 0.55, 6.875, 27.5),
        ("claude-opus-4-7", "claude-opus-4.7", 5.5, 0.55, 6.875, 27.5),
        ("claude-opus-4-8", "claude-opus-4.8", 5.5, 0.55, 6.875, 27.5),
        ("claude-sonnet-5", "claude-sonnet-5", 2.2, 0.22, 2.75, 11),
        ("claude-4-5-sonnet", "claude-sonnet-4.5", 3.3, 0.33, 4.125, 16.5),
        ("claude-sonnet-4-6", "claude-sonnet-4.6", 3.3, 0.33, 4.125, 16.5),
        ("claude-4-5-haiku", "claude-haiku-4.5", 1.1, 0.11, 1.375, 5.5),
        ("gpt-5-6-sol", "gpt-5.6-sol", 5.5, 0.55, 6.875, 33),
        ("gpt-5-6-terra", "gpt-5.6-terra", 2.75, 0.275, 3.4375, 16.5),
        ("gpt-5-6-luna", "gpt-5.6-luna", 1.1, 0.11, 1.375, 6.6),
        ("gpt-5-5", "gpt-5.5", 5.5, 0.55, None, 33),
        # Zed's current official table explicitly publishes $0.0275 cached input.
        ("gpt-5-4", "gpt-5.4", 2.75, 0.0275, None, 16.5),
        ("gpt-5-3-codex", "gpt-5.3-codex", 1.925, 0.1925, None, 15.4),
        ("gpt-5-2", "gpt-5.2", 1.925, 0.1925, None, 15.4),
        ("gpt-5-2-codex", "gpt-5.2-codex", 1.925, 0.1925, None, 15.4),
        ("gpt-5-mini", "gpt-5-mini", 0.275, 0.0275, None, 2.2),
        ("gpt-5-nano", "gpt-5-nano", 0.055, 0.0055, None, 0.44),
        # Zed names Gemini 3.1 Pro but does not publish an exact preview model ID;
        # omit it rather than guessing an AInsights preview slug.
        ("gemini-3-5-flash", "gemini-3.5-flash", 1.65, None, None, 9.9),
        ("gemini-3-flash", "gemini-3-flash", 0.55, None, None, 3.3),
    ]
    for slug, model_id, input_rate, cache_read, cache_write, output_rate in zed_models:
        # The official trial excludes Fable, every Opus model, and GPT Pro.
        # GPT Pro rows are not mapped today, but keep that rule explicit so a
        # future addition cannot silently become trial-eligible.
        trial_blocked = (
            slug == "claude-fable-5"
            or slug.startswith("claude-opus-")
            or (model_id.lower().startswith("gpt-") and model_id.lower().endswith(" pro"))
        )
        trial_variants: list[dict[str, Any]] = []
        if not trial_blocked:
            trial_variants.append(
                {
                    "planId": "zed-pro-trial",
                    "idSuffix": "trial",
                    "comparable": False,
                    "supportStatus": "trial",
                }
            )
        rate_note = (
            "Published Zed-hosted marginal rate copied from the official model table, "
            "where it is shown as 10% above Zed's provider-reference column. The "
            "reference value is not asserted to equal the current first-party API rate."
        )
        if slug == "claude-sonnet-5":
            rate_note += " Introductory Sonnet 5 rate is published through 2026-08-31."
        hosted_row = {
            "id": f"zed-hosted-{slug}",
            "providerId": "zed",
            "planId": "zed-hosted-overage",
            "modelSlugs": [slug],
            "providerModelId": model_id,
            "pricingKind": "per-token",
            "comparable": False,
            "inputPerMillionTokensUsd": input_rate,
            "cacheReadPerMillionTokensUsd": cache_read,
            "outputPerMillionTokensUsd": output_rate,
            "sourceIds": ["zed-model-rates-2026-08-12", "zed-pricing-2026-08-12"],
            "planVariants": trial_variants,
            "notes": rate_note,
        }
        if cache_write is not None:
            hosted_row["cacheWritePerMillionTokensUsd"] = cache_write
        offers.append(hosted_row)

        pro_row = {
            "id": f"zed-pro-effective-{slug}",
            "providerId": "zed",
            "planId": "zed-pro",
            "modelSlugs": [slug],
            "providerModelId": model_id,
            "pricingKind": "effective-subscription",
            "comparable": True,
            "subscriptionMultiplier": 2,
            "inputPerMillionTokensUsd": scaled(input_rate, 2),
            "cacheReadPerMillionTokensUsd": scaled(cache_read, 2),
            "outputPerMillionTokensUsd": scaled(output_rate, 2),
            "sourceIds": ["zed-model-rates-2026-08-12", "zed-pricing-2026-08-12"],
            "calculation": "$10 monthly fee / $5 included token credits = 2x the published hosted rate.",
            "notes": "Exact full-credit effective rate from the public $10 fee and $5 included credits; unused credits and overage are outside this full-utilization comparison.",
        }
        if cache_write is not None:
            pro_row["cacheWritePerMillionTokensUsd"] = scaled(cache_write, 2)
        offers.append(pro_row)

        offers.append(
            non_comparable_offer(
                f"zed-business-{slug}",
                "zed",
                "zed-business",
                slug,
                model_id,
                ["zed-model-rates-2026-08-12", "zed-pricing-2026-08-12"],
                quotaScope="seat-plus-separate-hosted-usage",
                notes="The $30 Business seat fee contains no fixed token credits. Raw hosted usage is represented by the separate Hosted model usage / overage plan.",
            )
        )

    # Cline charges its provider inference at cost and publishes five exact frontier model IDs.
    providers.append(
        {
            "id": "cline",
            "name": "Cline",
            "category": "coding-platform",
            "url": "https://cline.bot/",
            "pricingUrl": "https://cline.bot/pricing",
            "sourceIds": ["cline-pricing-2026-08-12", "cline-models-2026-08-12"],
            "notes": "The individual client is free; Cline provider inference is billed at cost, or users may BYOK.",
        }
    )
    plans.append(
        plan(
            "cline-at-cost",
            "cline",
            "At-cost model inference",
            0,
            ["cline-pricing-2026-08-12", "cline-models-2026-08-12"],
            billingType="payg",
            displayType="token",
            quotaLabel="No subscription or seat fee; model inference at provider cost",
            comparisonClass="token-comparable",
        )
    )
    cline_models = [
        ("claude-fable-5", "claude-fable-5", 10, 1, 12.5, 50, "anthropic-api-pricing-2026-08-11"),
        ("claude-opus-4-8", "claude-opus-4-8", 5, 0.5, 6.25, 25, "anthropic-api-pricing-2026-08-11"),
        ("claude-sonnet-5", "claude-sonnet-5", 2, 0.2, 2.5, 10, "anthropic-api-pricing-2026-08-11"),
        ("gpt-5-6-sol", "gpt-5-6-sol", 5, 0.5, 6.25, 30, "openai-api-official-pricing"),
        ("gpt-5-5", "gpt-5-5", 5, 0.5, None, 30, "openai-api-official-pricing"),
    ]
    for slug, model_id, input_rate, cache_read, cache_write, output_rate, rate_source in cline_models:
        row = {
            "id": f"cline-{slug}",
            "providerId": "cline",
            "planId": "cline-at-cost",
            "modelSlugs": [slug],
            "providerModelId": model_id,
            "pricingKind": "per-token",
            "comparable": True,
            "inputPerMillionTokensUsd": input_rate,
            "cacheReadPerMillionTokensUsd": cache_read,
            "outputPerMillionTokensUsd": output_rate,
            "derivedFromAtCostRule": True,
            "sourceIds": ["cline-pricing-2026-08-12", "cline-models-2026-08-12", rate_source],
            "notes": "Cline publishes inference at cost; the numeric fields apply the corresponding first-party standard API rate.",
        }
        if cache_write is not None:
            row["cacheWritePerMillionTokensUsd"] = cache_write
        offers.append(row)

    # Kilo Pass is kept separate from the existing Kilo Gateway provider slice so a
    # normal fragment merge cannot erase the 162 current Gateway offers.
    providers.append(
        {
            "id": "kilo-pass",
            "name": "Kilo Pass",
            "category": "token-plan",
            "url": "https://kilo.ai/",
            "pricingUrl": "https://kilo.ai/pricing",
            "sourceIds": ["kilo-pass-pricing-2026-08-12"],
            "notes": "Kilo Pass credits are spent against Kilo Gateway's exact provider rates. Effective rates below are explicitly best-case estimates using the displayed 'up to' credit values.",
        }
    )
    kilo_pass_plans = [
        ("kilo-pass-starter", "Starter", 19, 26.6),
        ("kilo-pass-pro", "Pro", 49, 68.6),
        ("kilo-pass-expert", "Expert", 199, 278.6),
    ]
    for plan_id, name, price, max_value in kilo_pass_plans:
        plans.append(
            plan(
                plan_id,
                "kilo-pass",
                name,
                price,
                ["kilo-pass-pricing-2026-08-12"],
                includedApiSpendUsd=price,
                maxAdvertisedCreditValueUsd=max_value,
                bestCaseCreditMultiplier=1.4,
                quotaLabel=f"${price} paid credits; up to ${max_value:.2f} displayed credit value",
                comparisonClass="non-comparable",
                estimated=True,
                notes="Bonus depends on billing cycle/subscription streak; the maximum displayed value is not guaranteed every month.",
            )
        )
    kilo_gateway_offers = [row for row in catalogue["offers"] if row.get("providerId") == "kilo"]
    best_case_factor = 5 / 7
    for gateway_offer in kilo_gateway_offers:
        row = copy.deepcopy(gateway_offer)
        original_id = row.pop("id")
        row["id"] = f"kilo-pass-{original_id.removeprefix('md-kilo-')}"
        row["providerId"] = "kilo-pass"
        row["planId"] = "kilo-pass-starter"
        row["pricingKind"] = "effective-subscription"
        row["comparable"] = False
        row["estimated"] = True
        row["bestCaseOnly"] = True
        row["subscriptionMultiplier"] = 1.4
        row["effectiveApiValueUsdPerMonth"] = 26.6
        for field in (
            "inputPerMillionTokensUsd",
            "cacheReadPerMillionTokensUsd",
            "cacheWritePerMillionTokensUsd",
            "outputPerMillionTokensUsd",
            "effectiveUsdPerMillionTokens",
        ):
            if field in row:
                row[field] = scaled(row[field], best_case_factor)
        row["sourceIds"] = list(dict.fromkeys([*row.get("sourceIds", []), "kilo-pass-pricing-2026-08-12"]))
        prior_notes = row.get("notes")
        row["notes"] = (
            (f"{prior_notes} " if prior_notes else "")
            + "Estimate: underlying Kilo Gateway exact-provider rate multiplied by 5/7, corresponding to the currently displayed maximum $1.40 credit value per $1 subscription. Actual bonus can be lower."
        )
        row["planVariants"] = [
            {
                "planId": "kilo-pass-pro",
                "idSuffix": "pro",
                "effectiveApiValueUsdPerMonth": 68.6,
                "subscriptionMultiplier": 1.4,
            },
            {
                "planId": "kilo-pass-expert",
                "idSuffix": "expert",
                "effectiveApiValueUsdPerMonth": 278.6,
                "subscriptionMultiplier": 1.4,
            },
        ]
        offers.append(row)

    # Kiro credits measure work rather than model tokens. Prices and exact model
    # choices are useful, but deliberately remain non-comparable per token.
    providers.append(
        {
            "id": "kiro",
            "name": "Kiro",
            "category": "coding-subscription",
            "url": "https://kiro.dev/",
            "pricingUrl": "https://kiro.dev/pricing/",
            "sourceIds": ["kiro-pricing-models-2026-08-12"],
        }
    )
    kiro_plans = [
        ("kiro-free", "Free", 0, 50),
        ("kiro-pro", "Pro", 20, 1000),
        ("kiro-pro-plus", "Pro+", 40, 2000),
        ("kiro-pro-max", "Pro Max", 100, 5000),
        ("kiro-power", "Power", 200, 10000),
    ]
    for plan_id, name, price, credits in kiro_plans:
        plans.append(
            plan(
                plan_id,
                "kiro",
                name,
                price,
                ["kiro-pricing-models-2026-08-12"],
                includedWorkCredits=credits,
                effectiveCostPerWorkCreditUsd=(round(price / credits, 6) if price else 0),
                addOnCostPerWorkCreditUsd=(0.04 if price else None),
                quotaLabel=f"{credits:,} work credits / month" + ("; add-ons $0.04/credit" if price else ""),
            )
        )
    kiro_free_slugs = {
        "claude-4-5-sonnet",
        "claude-sonnet-4-6",
        "qwen3-coder-next",
        "deepseek-v3-2",
        "minimax-m2-1",
    }
    kiro_paid_slugs = kiro_free_slugs | {
        "claude-4-5-haiku",
        "claude-opus-4-5",
        "claude-opus-4-6",
        "claude-opus-4-7",
    }
    for slug in sorted(kiro_paid_slugs):
        if slug in kiro_free_slugs:
            base_plan = "kiro-free"
            variant_ids = ["kiro-pro", "kiro-pro-plus", "kiro-pro-max", "kiro-power"]
        else:
            base_plan = "kiro-pro"
            variant_ids = ["kiro-pro-plus", "kiro-pro-max", "kiro-power"]
        offers.append(
            non_comparable_offer(
                f"kiro-{slug}",
                "kiro",
                base_plan,
                slug,
                slug,
                ["kiro-pricing-models-2026-08-12"],
                quotaScope="plan-work-credits",
                supportStatus=("conditional" if base_plan == "kiro-free" else "active"),
                planVariants=[
                    {"planId": variant_id, "idSuffix": variant_id.removeprefix("kiro-")}
                    for variant_id in variant_ids
                ],
                notes="Credits are metered by task complexity and model-specific work rates, not by a fixed token allowance.",
            )
        )

    # JetBrains AI Credits are dollar-denominated but model consumption is dynamic.
    providers.append(
        {
            "id": "jetbrains-ai",
            "name": "JetBrains AI",
            "category": "coding-subscription",
            "url": "https://www.jetbrains.com/ai-ides/",
            "pricingUrl": "https://www.jetbrains.com/ai-ides/buy/",
            "sourceIds": ["jetbrains-ai-licenses-2026-08-12", "jetbrains-ai-models-2026-07-21"],
        }
    )
    jetbrains_plans = [
        ("jetbrains-ai-free-personal", "AI Free — Personal", 0, 3),
        ("jetbrains-ai-pro-personal", "AI Pro — Personal", 10, 10),
        ("jetbrains-ai-ultimate-personal", "AI Ultimate — Personal", 30, 35),
        ("jetbrains-ai-free-org", "AI Free — Organization", 0, 3),
        ("jetbrains-ai-pro-org", "AI Pro — Organization", 20, 20),
        ("jetbrains-ai-ultimate-org", "AI Ultimate — Organization", 60, 70),
    ]
    for plan_id, name, price, credits in jetbrains_plans:
        plans.append(
            plan(
                plan_id,
                "jetbrains-ai",
                name,
                price,
                ["jetbrains-ai-licenses-2026-08-12"],
                includedAiCredits=credits,
                aiCreditNominalValueUsd=1,
                quotaLabel=f"{credits} AI Credits / 30 days; 1 AI Credit corresponds to $1 of model usage",
            )
        )
    jetbrains_models = {
        "claude-fable-5": "Claude Fable 5",
        "claude-opus-5": "Claude Opus 5",
        "claude-sonnet-5": "Claude Sonnet 5",
        "claude-opus-4-8": "Claude 4.8 Opus",
        "claude-opus-4-7": "Claude 4.7 Opus",
        "claude-opus-4-6": "Claude 4.6 Opus",
        "claude-sonnet-4-6": "Claude 4.6 Sonnet",
        "claude-opus-4-5": "Claude 4.5 Opus",
        "claude-4-5-sonnet": "Claude 4.5 Sonnet",
        "claude-4-5-haiku": "Claude 4.5 Haiku",
        "gemini-3-6-flash": "Gemini 3.6 Flash",
        "gemini-3-5-flash": "Gemini 3.5 Flash",
        "gemini-3-5-flash-lite": "Gemini 3.5 Flash Lite",
        "gemini-3-flash": "Gemini 3 Flash",
        "gemini-2-5-pro": "Gemini 2.5 Pro",
        "gemini-2-5-flash": "Gemini 2.5 Flash",
        "gemini-2-5-flash-lite": "Gemini 2.5 Flash-Lite",
        "gpt-5-6-luna": "GPT 5.6 Luna",
        "gpt-5-6-sol": "GPT 5.6 Sol",
        "gpt-5-6-terra": "GPT 5.6 Terra",
        "gpt-5-5": "GPT-5.5",
        "gpt-5-4-mini": "GPT-5.4 mini",
        "gpt-5-4-nano": "GPT-5.4 nano",
        "gpt-5-4": "GPT-5.4",
        "gpt-5-3-codex": "GPT-5.3 Codex",
        "gpt-5-2": "GPT-5.2",
        "gpt-5-1": "GPT-5.1",
        "gpt-5": "GPT-5",
        "gpt-5-mini": "GPT-5 mini",
        "gpt-5-nano": "GPT-5 nano",
        "gpt-4-1": "GPT-4.1",
        "gpt-4-1-mini": "GPT-4.1 mini",
        "gpt-4-1-nano": "GPT-4.1 nano",
        "gpt-4o": "GPT-4o",
        "o1": "o1",
        "o3": "o3",
        "o3-mini": "o3-mini",
        "o4-mini": "o4-mini",
        "grok-4-3": "Grok-4.3",
    }
    jb_variant_ids = [row[0] for row in jetbrains_plans[1:]]
    for slug, model_id in jetbrains_models.items():
        offers.append(
            non_comparable_offer(
                f"jetbrains-ai-{slug}",
                "jetbrains-ai",
                "jetbrains-ai-free-personal",
                slug,
                model_id,
                ["jetbrains-ai-models-2026-07-21", "jetbrains-ai-licenses-2026-08-12"],
                quotaScope="shared-ai-credit-balance",
                planVariants=[
                    {"planId": variant_id, "idSuffix": variant_id.removeprefix("jetbrains-ai-")}
                    for variant_id in jb_variant_ids
                ],
                notes="All listed models are Active in the official 2026.2 table. AI Credit consumption varies with model price and tokens; no fixed per-model token allowance is published.",
            )
        )

    # Warp publishes both plan cost and the API-rate dollar value of its credits.
    # Dividing plan cost by API value gives an exact plan multiplier that can be
    # applied to models with one unambiguous upstream standard rate.
    providers.append(
        {
            "id": "warp",
            "name": "Warp",
            "category": "coding-subscription",
            "url": "https://www.warp.dev/",
            "pricingUrl": "https://www.warp.dev/pricing",
            "sourceIds": ["warp-pricing-models-2026-08-12"],
        }
    )
    warp_plans = [
        ("warp-free", "Free", 0, None, None, None, None),
        ("warp-build-monthly", "Build Monthly", 20, None, 1500, 20, 1.0),
        ("warp-build-annual", "Build Annual", 18, 216, 1500, 20, 0.9),
        ("warp-max-monthly", "Max Monthly", 200, None, 18000, 240, 5 / 6),
        ("warp-max-annual", "Max Annual", 180, 2160, 18000, 240, 0.75),
        ("warp-business-monthly", "Business Monthly", 50, None, 1500, 20, 2.5),
        ("warp-business-annual", "Business Annual", 45, 540, 1500, 20, 2.25),
    ]
    warp_plan_factors: dict[str, float] = {}
    for plan_id, name, price, annual_price, credits, value, rate_factor in warp_plans:
        extra: dict[str, Any] = {
            "quotaLabel": "BYOK or Reload credits" if credits is None else f"{credits:,} credits = ${value} agent usage at API rates / month"
        }
        if annual_price is not None:
            extra["annualPriceUsd"] = annual_price
        if credits is not None:
            extra["includedWorkCredits"] = credits
            extra["includedApiSpendUsd"] = value
        if rate_factor is not None:
            extra["effectiveRateMultiplier"] = rate_factor
            extra["comparisonClass"] = "effective-token-comparable"
            warp_plan_factors[plan_id] = rate_factor
        plans.append(plan(plan_id, "warp", name, price, ["warp-pricing-models-2026-08-12"], **extra))
    warp_upstream_rates = {
        "claude-fable-5": ("Fable 5", 10, 1, 12.5, 50),
        "claude-opus-5": ("Claude Opus 5", 5, 0.5, 6.25, 25),
    }
    warp_paid_ids = [row[0] for row in warp_plans[1:]]
    for slug, (model_id, input_rate, cache_read, cache_write, output_rate) in warp_upstream_rates.items():
        variants: list[dict[str, Any]] = []
        for variant_id in warp_paid_ids[1:]:
            factor = warp_plan_factors[variant_id]
            variant: dict[str, Any] = {
                "planId": variant_id,
                "idSuffix": variant_id.removeprefix("warp-"),
                "rateMultiplier": factor,
                "calculation": f"Plan monthly cost / included API-rate value = {factor:.9g}x the upstream standard rate.",
            }
            # Front-end variant expansion scales input/cache-read/output.  Cache
            # write is explicit because it is not automatically scaled there.
            variant["cacheWritePerMillionTokensUsd"] = scaled(cache_write, factor)
            variants.append(variant)
        offers.append(
            {
                "id": f"warp-effective-{slug}",
                "providerId": "warp",
                "planId": "warp-build-monthly",
                "modelSlugs": [slug],
                "providerModelId": model_id,
                "pricingKind": "effective-subscription",
                "comparable": True,
                "inputPerMillionTokensUsd": input_rate,
                "cacheReadPerMillionTokensUsd": cache_read,
                "cacheWritePerMillionTokensUsd": cache_write,
                "outputPerMillionTokensUsd": output_rate,
                "sourceIds": ["warp-pricing-models-2026-08-12", "anthropic-api-pricing-2026-08-11"],
                "calculation": "Build Monthly $20 / $20 included API-rate value = 1x the upstream standard rate.",
                "planVariants": variants,
                "notes": "Finite effective rate derived from Warp's published plan price and API-rate usage value.",
            }
        )
    warp_unpriced_models = {
        "glm-5-2": "GLM 5.2",
        "kimi-k3": "Kimi K3",
    }
    for slug, model_id in warp_unpriced_models.items():
        offers.append(
            non_comparable_offer(
                f"warp-{slug}",
                "warp",
                warp_paid_ids[0],
                slug,
                model_id,
                ["warp-pricing-models-2026-08-12"],
                quotaScope="shared-agent-credits",
                planVariants=[
                    {"planId": variant_id, "idSuffix": variant_id.removeprefix("warp-")}
                    for variant_id in warp_paid_ids[1:]
                ],
                notes="Warp publishes the plan's API-rate USD value, but this model has no single upstream standard token rate that can be applied safely.",
            )
        )

    # Amp Unconstrained bills model tokens at upstream API pricing. Subscription
    # inclusions are stated as "at least", so their finite derivations are
    # useful upper-bound estimates but are deliberately excluded from ranking.
    providers.append(
        {
            "id": "amp",
            "name": "Amp",
            "category": "coding-subscription",
            "url": "https://ampcode.com/",
            "pricingUrl": "https://ampcode.com/pricing",
            "sourceIds": ["amp-pricing-2026-08-12", "amp-models-2026-08-12"],
        }
    )
    plans.extend(
        [
            plan(
                "amp-megawatt",
                "amp",
                "Megawatt",
                20,
                ["amp-pricing-2026-08-12"],
                minimumIncludedApiSpendUsd=20,
                quotaLabel="At least $20 included agent usage; low and medium modes",
                estimated=True,
            ),
            plan(
                "amp-gigawatt",
                "amp",
                "Gigawatt",
                200,
                ["amp-pricing-2026-08-12"],
                minimumIncludedApiSpendUsd=200,
                quotaLabel="At least $200 included agent usage; all modes including high and ultra",
                estimated=True,
            ),
            plan(
                "amp-unconstrained",
                "amp",
                "Unconstrained",
                None,
                ["amp-pricing-2026-08-12"],
                billingType="payg",
                displayType="token",
                quotaLabel="Model tokens and orbs billed at API pricing",
                comparisonClass="token-comparable",
            ),
        ]
    )
    amp_upstream_rates = {
        "claude-fable-5": ("Fable 5", 10, 1, 12.5, 50, "anthropic-api-pricing-2026-08-11"),
        "gpt-5-6-sol": ("GPT-5.6 Sol", 5, 0.5, 6.25, 30, "openai-api-official-pricing"),
        "gpt-5-6-terra": ("GPT-5.6 Terra", 2, 0.2, 2.5, 12, "openai-api-official-pricing"),
        "gpt-5-6-luna": ("GPT-5.6 Luna", 0.2, 0.02, 0.25, 1.2, "openai-api-official-pricing"),
        "gpt-5-5": ("GPT-5.5", 5, 0.5, None, 30, "modelsdev-openai-95aaaeb"),
        "gemini-3-flash": ("Gemini 3 Flash", 0.5, 0.05, None, 3, "modelsdev-google-95aaaeb"),
        "grok-4-5": ("Grok 4.5", 2, 0.3, None, 6, "modelsdev-xai-95aaaeb"),
    }
    for slug, (
        model_id,
        input_rate,
        cache_read,
        cache_write,
        output_rate,
        rate_source,
    ) in amp_upstream_rates.items():
        subscription_variants: list[dict[str, Any]] = [
            {
                "planId": "amp-gigawatt",
                "idSuffix": "gigawatt",
                "pricingKind": "effective-subscription",
                "comparable": False,
                "estimated": True,
                "conservativeUpperBoundOnly": True,
                "minimumIncludedApiSpendUsd": 200,
                "calculation": "$200 fee / at least $200 agent usage; effective rate is at most 1x upstream.",
            }
        ]
        if slug != "claude-fable-5":
            subscription_variants.insert(
                0,
                {
                    "planId": "amp-megawatt",
                    "idSuffix": "megawatt",
                    "pricingKind": "effective-subscription",
                    "comparable": False,
                    "estimated": True,
                    "conservativeUpperBoundOnly": True,
                    "minimumIncludedApiSpendUsd": 20,
                    "supportStatus": "mode-dependent",
                    "calculation": "$20 fee / at least $20 agent usage; effective rate is at most 1x upstream.",
                },
            )
        row = {
            "id": f"amp-unconstrained-{slug}",
            "providerId": "amp",
            "planId": "amp-unconstrained",
            "modelSlugs": [slug],
            "providerModelId": model_id,
            "pricingKind": "per-token",
            "comparable": True,
            "derivedFromAtCostRule": True,
            "inputPerMillionTokensUsd": input_rate,
            "cacheReadPerMillionTokensUsd": cache_read,
            "outputPerMillionTokensUsd": output_rate,
            "sourceIds": ["amp-pricing-2026-08-12", "amp-models-2026-08-12", rate_source],
            "planVariants": subscription_variants,
            "notes": "Amp Unconstrained bills model tokens at API pricing; numeric fields apply this model's unique upstream standard rate.",
        }
        if cache_write is not None:
            row["cacheWritePerMillionTokensUsd"] = cache_write
        offers.append(row)

    amp_unpriced_models = {
        "glm-5-2": "GLM-5.2",
        "inkling": "Inkling",
        "kimi-k3": "Kimi K3",
    }
    for slug, model_id in amp_unpriced_models.items():
        variants = [{"planId": "amp-unconstrained", "idSuffix": "unconstrained"}]
        variants.insert(0, {"planId": "amp-megawatt", "idSuffix": "megawatt", "supportStatus": "mode-dependent"})
        offers.append(
            non_comparable_offer(
                f"amp-{slug}",
                "amp",
                "amp-gigawatt",
                slug,
                model_id,
                ["amp-pricing-2026-08-12", "amp-models-2026-08-12"],
                quotaScope="shared-agent-usage",
                planVariants=variants,
                notes="Amp supports this routed model, but no single upstream standard token rate is available for a defensible conversion.",
            )
        )

    # Factory publishes exact model IDs and usage multipliers but only relative plan limits.
    providers.append(
        {
            "id": "factory",
            "name": "Factory",
            "category": "coding-subscription",
            "url": "https://www.factory.ai/",
            "pricingUrl": "https://www.factory.ai/pricing",
            "sourceIds": ["factory-pricing-2026-08-12", "factory-models-2026-08-12"],
        }
    )
    factory_plans = [
        ("factory-pro", "Pro", 20, 1),
        ("factory-plus", "Plus", 100, 5),
        ("factory-max", "Max", 200, 10),
    ]
    for plan_id, name, price, relative_usage in factory_plans:
        plans.append(
            plan(
                plan_id,
                "factory",
                name,
                price,
                ["factory-pricing-2026-08-12"],
                relativeUsageVsPro=relative_usage,
                quotaLabel=("Rolling rate limits" if relative_usage == 1 else f"Approximately {relative_usage}× Pro usage"),
            )
        )
    factory_models = {
        "claude-fable-5": ("claude-fable-5", 4),
        "claude-opus-5": ("claude-opus-5", 2),
        "claude-opus-4-8": ("claude-opus-4-8", 2),
        "claude-opus-4-7": ("claude-opus-4-7", 2),
        "claude-opus-4-6": ("claude-opus-4-6", 2),
        "claude-opus-4-5": ("claude-opus-4-5-20251101", 2),
        "claude-sonnet-5": ("claude-sonnet-5", 0.8),
        "claude-sonnet-4-6": ("claude-sonnet-4-6", 1.2),
        "claude-4-5-sonnet": ("claude-sonnet-4-5-20250929", 1.2),
        "claude-4-5-haiku": ("claude-haiku-4-5-20251001", 0.4),
        "gpt-5-6-sol": ("gpt-5.6-sol", 2),
        "gpt-5-6-terra": ("gpt-5.6-terra", 0.8),
        "gpt-5-6-luna": ("gpt-5.6-luna", 0.08),
        "gpt-5-5": ("gpt-5.5", 2),
        "gpt-5-4": ("gpt-5.4", 1),
        "gpt-5-4-mini": ("gpt-5.4-mini", 0.3),
        "gpt-5-3-codex": ("gpt-5.3-codex", 0.7),
        "gpt-5-2": ("gpt-5.2", 0.7),
        "gemini-3-1-pro-preview": ("gemini-3.1-pro-preview", 0.8),
        "gemini-3-6-flash": ("gemini-3.6-flash", 0.6),
        "gemini-3-5-flash": ("gemini-3.5-flash", 0.6),
        "gemini-3-flash": ("gemini-3-flash-preview", 0.2),
        "grok-4-5": ("grok-4.5", 0.8),
        "glm-5-2": ("glm-5.2", 0.55),
        "kimi-k3": ("kimi-k3", 1.2),
        "kimi-k2-7-code": ("kimi-k2.7-code", 0.38),
        "kimi-k2-6": ("kimi-k2.6", 0.4),
        "nvidia-nemotron-3-ultra-550b-a55b": ("nemotron-3-ultra", 0.24),
        "deepseek-v4-pro": ("deepseek-v4-pro", 0.7),
        "minimax-m3": ("minimax-m3", 0.12),
        "minimax-m2-7": ("minimax-m2.7", 0.12),
        "minimax-m2-5": ("minimax-m2.5", 0.12),
        "kimi-k2-5": ("kimi-k2.5", 0.25),
        "glm-5-1": ("glm-5.1", 0.55),
    }
    for slug, (model_id, usage_multiplier) in factory_models.items():
        deprecated = slug in {"kimi-k2-5", "glm-5-1"}
        offers.append(
            non_comparable_offer(
                f"factory-{slug}",
                "factory",
                "factory-pro",
                slug,
                model_id,
                ["factory-pricing-2026-08-12", "factory-models-2026-08-12"],
                usageMultiplier=usage_multiplier,
                supportStatus=("deprecated" if deprecated else "active"),
                planVariants=[
                    {"planId": "factory-plus", "idSuffix": "plus"},
                    {"planId": "factory-max", "idSuffix": "max"},
                ],
                notes="The multiplier is official model credit consumption. Factory publishes only relative rolling plan limits, so a token price cannot be derived.",
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

    provider_ids = [row["id"] for row in providers]
    plan_ids = [row["id"] for row in plans]
    offer_ids = [row["id"] for row in offers]
    for label, values in (("provider", provider_ids), ("plan", plan_ids), ("offer", offer_ids)):
        duplicates = sorted({value for value in values if values.count(value) > 1})
        if duplicates:
            raise ValueError(f"duplicate {label} ids: {duplicates}")

    sources = [
        {
            "id": "zed-pricing-2026-08-12",
            "title": "Zed plans and pricing",
            "publisher": "Zed Industries",
            "url": "https://zed.dev/pricing",
            "kind": "official-pricing",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Publishes Personal $0, Pro $10 with $5 token credits, Business $30, a $20/14-day Pro trial, and hosted usage that requires Pro or Business access.",
        },
        {
            "id": "zed-model-rates-2026-08-12",
            "title": "Zed hosted models and per-token prices",
            "publisher": "Zed Industries",
            "url": "https://zed.dev/docs/ai/models",
            "kind": "official-pricing",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Exact input/output/cache prices copied from the official table, which shows provider-reference values and Zed rates 10% above them. The reference column is not claimed to match current first-party pricing. Sonnet 5 launch pricing is valid through 2026-08-31.",
        },
        {
            "id": "cline-pricing-2026-08-12",
            "title": "Cline pricing",
            "publisher": "Cline Bot Inc.",
            "url": "https://cline.bot/pricing",
            "kind": "official-pricing",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Individual client is free and model inference is billed at cost or BYOK, with no subscription or seat fee.",
        },
        {
            "id": "cline-models-2026-08-12",
            "title": "Cline model directory",
            "publisher": "Cline Bot Inc.",
            "url": "https://cline.bot/models",
            "kind": "official-model-list",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Exact current model IDs; the at-cost numeric offers are limited to models whose first-party standard API rate is also documented.",
        },
        {
            "id": "kilo-pass-pricing-2026-08-12",
            "title": "Kilo pricing and Kilo Pass calculator",
            "publisher": "Kilo Code",
            "url": "https://kilo.ai/pricing",
            "kind": "official-pricing",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Publishes exact-provider-rate Gateway billing and Starter $19→up to $26.60, Pro $49→up to $68.60, Expert $199→up to $278.60 displayed credit values. Bonus values are maxima, not guaranteed monthly allowances.",
        },
        {
            "id": "kiro-pricing-models-2026-08-12",
            "title": "Kiro plans, credits, and models",
            "publisher": "Amazon Web Services",
            "url": "https://kiro.dev/pricing/",
            "kind": "official-pricing",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Publishes five tiers, monthly work credits, $0.04 paid-plan add-ons, exact selectable Claude models, and named open-weight models. Credits are task work units rather than tokens.",
        },
        {
            "id": "jetbrains-ai-licenses-2026-08-12",
            "title": "JetBrains AI licensing, subscriptions, and AI Credits",
            "publisher": "JetBrains",
            "url": "https://www.jetbrains.com/help/ai-assistant/licensing-and-subscriptions.html",
            "kind": "official-documentation",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Publishes personal and organization prices, credits per 30 days, the $1 nominal AI Credit value, and explains token/model-dependent consumption.",
        },
        {
            "id": "jetbrains-ai-models-2026-07-21",
            "title": "JetBrains AI Assistant supported models",
            "publisher": "JetBrains",
            "url": "https://www.jetbrains.com/help/ai-assistant/supported-llms.html",
            "kind": "official-model-list",
            "asOf": "2026-07-21",
            "accessedAt": CHECKED_AT,
            "notes": "Only models marked Active in the official 2026.2 table are included.",
        },
        {
            "id": "warp-pricing-models-2026-08-12",
            "title": "Warp plans, credits, and model examples",
            "publisher": "Warp",
            "url": "https://www.warp.dev/pricing",
            "kind": "official-pricing",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Publishes monthly/annual prices, included credits and their API-rate dollar value. Effective multipliers are Build monthly 1x, Build annual 0.9x, Max monthly 5/6x, Max annual 0.75x, Business monthly 2.5x, and Business annual 2.25x.",
        },
        {
            "id": "amp-pricing-2026-08-12",
            "title": "Amp pricing",
            "publisher": "Sourcegraph",
            "url": "https://ampcode.com/pricing",
            "kind": "official-pricing",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Megawatt $20 includes at least $20 agent usage; Gigawatt $200 includes at least $200; Unconstrained bills model tokens and orbs at API pricing.",
        },
        {
            "id": "amp-models-2026-08-12",
            "title": "Amp modes and models",
            "publisher": "Sourcegraph",
            "url": "https://ampcode.com/models",
            "kind": "official-model-list",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Exact current routed, subagent, system, and plugin model names.",
        },
        {
            "id": "factory-pricing-2026-08-12",
            "title": "Factory pricing",
            "publisher": "Factory",
            "url": "https://www.factory.ai/pricing",
            "kind": "official-pricing",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Pro $20, Plus $100 with approximately 5× Pro usage, and Max $200 with approximately 10× Pro usage; no numeric base token quota is published.",
        },
        {
            "id": "factory-models-2026-08-12",
            "title": "Factory supported models and usage multipliers",
            "publisher": "Factory",
            "url": "https://docs.factory.ai/models",
            "kind": "official-model-list",
            "asOf": CHECKED_AT,
            "accessedAt": CHECKED_AT,
            "notes": "Exact model IDs and official credit-consumption multipliers. Deprecated rows remain explicitly marked deprecated.",
        },
    ]
    existing_source_ids = {
        "modelsdev-kilo-95aaaeb",
        "modelsdev-snapshot-95aaaeb",
        "anthropic-api-pricing-2026-08-11",
        "openai-api-official-pricing",
    }
    sources.extend(
        copy.deepcopy(row)
        for row in catalogue["sources"]
        if row.get("id") in existing_source_ids
    )

    return {
        "schemaVersion": 1,
        "mergeTarget": "data/pricing/provider_pricing.json",
        "checkedAt": CHECKED_AT,
        "researchScope": "Global coding subscriptions, at-cost coding gateways, and token-credit plans omitted from the base catalogue",
        "comparisonPolicy": {
            "publishedPerTokenRate": "comparable",
            "atCostPlusOfficialApiRate": "comparable",
            "bestCaseAdvertisedCreditBonus": "comparable-estimate-with-bestCaseOnly-flag",
            "workCreditsOrRelativeLimitsWithoutTokenFormula": "non-comparable",
            "notes": "No work-credit, request, relative-limit, or model-multiplier plan is converted to USD per million tokens without a published conversion formula.",
        },
        "providers": providers,
        "plans": plans,
        "offers": offers,
        "sources": sources,
        "mergeNotes": [
            "Kilo Pass uses a separate provider id so merging this fragment cannot replace the existing 162-offer Kilo Gateway slice.",
            "Every offer contains exactly one AInsights model slug; planVariants expand the same explicit model into additional supported plans.",
            "Zed Pro full-credit effective rates and Cline at-cost rates are directly comparable; gated Zed hosted overage and Kilo Pass best-case estimates are explicitly non-comparable.",
            "Warp has finite six-plan rates only where a unique upstream rate exists; Amp Unconstrained does likewise, while its at-least subscription estimates are non-comparable.",
            "Kiro, JetBrains, and Factory retain null token rates because their published quota unit cannot be converted per model.",
        ],
    }


def main() -> int:
    fragment = build_fragment()
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
                "offerTemplates": len(fragment["offers"]),
                "expandedPlanModelRows": sum(1 + len(row.get("planVariants", [])) for row in fragment["offers"]),
                "sources": len(fragment["sources"]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
