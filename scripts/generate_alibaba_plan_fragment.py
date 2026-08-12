#!/usr/bin/env python3
"""Generate explicit Alibaba Token Plan and Coding Plan model offers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from import_models_dev_pricing import (
    SNAPSHOT_COMMIT,
    SNAPSHOT_DATE,
    build_site_indexes,
    load_models_dev_snapshot,
    load_site_models,
    matched_site_slugs,
    safe_id,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODELS = PROJECT_ROOT / "docs" / "data" / "models.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "pricing" / "research_alibaba_plans.json"

TOKEN_PLAN_GLOBAL_SOURCE = "alibaba-token-plan-global-official-2026-08-11"
TOKEN_PLAN_CN_SOURCE = "alibaba-token-plan-cn-official-2026-08-11"
CODING_PLAN_GLOBAL_SOURCE = "alibaba-coding-plan-global-official-2026-08-11"
CODING_PLAN_CN_SOURCE = "alibaba-coding-plan-cn-official-2026-08-11"


PROVIDER_DEFINITIONS = {
    "alibaba-token-plan": {
        "name": "Alibaba Token Plan",
        "category": "token-plan",
        "url": "https://www.alibabacloud.com/help/en/model-studio/token-plan-personal-overview",
        "sourceId": TOKEN_PLAN_GLOBAL_SOURCE,
        "region": "Global",
    },
    "alibaba-token-plan-cn": {
        "name": "百炼 Token Plan（中国）",
        "category": "token-plan",
        "url": "https://help.aliyun.com/zh/model-studio/token-plan-personal-overview",
        "sourceId": TOKEN_PLAN_CN_SOURCE,
        "region": "CN",
    },
    "alibaba-coding-plan": {
        "name": "Alibaba Coding Plan",
        "category": "coding-subscription",
        "url": "https://www.alibabacloud.com/help/en/model-studio/coding-plan",
        "sourceId": CODING_PLAN_GLOBAL_SOURCE,
        "region": "Global",
    },
    "alibaba-coding-plan-cn": {
        "name": "百炼 Coding Plan（中国）",
        "category": "coding-subscription",
        "url": "https://help.aliyun.com/zh/model-studio/coding-plan",
        "sourceId": CODING_PLAN_CN_SOURCE,
        "region": "CN",
    },
}


TOKEN_TIERS = {
    "alibaba-token-plan": [
        ("lite", "Lite", 6, 2_500),
        ("standard", "Standard", 20, 10_000),
        ("pro", "Pro", 70, 40_000),
    ],
    "alibaba-token-plan-cn": [
        ("lite", "Lite", 39, 2_500),
        ("standard", "Standard", 139, 10_000),
        ("pro", "Pro", 499, 40_000),
    ],
}

CODING_PLANS = {
    "alibaba-coding-plan": {
        "name": "Coding Plan",
        "currency": "USD",
        "monthlyPriceUsd": 50,
    },
    "alibaba-coding-plan-cn": {
        "name": "Coding Plan",
        "currency": "CNY",
        "monthlyPriceLocal": 200,
        "monthlyPriceUsd": None,
        "firstMonthPriceLocal": 39.9,
        "promotionalFirstMonth": True,
    },
}


def collect_plan_support(
    provider_models: list[tuple[str, str, dict[str, Any]]],
    normalized_index: dict[str, set[str]],
    bag_index: dict[tuple[str, ...], set[str]],
) -> dict[str, dict[str, str]]:
    selected: dict[str, dict[str, tuple[int, str]]] = {
        provider_id: {} for provider_id in PROVIDER_DEFINITIONS
    }
    for provider_id, provider_model_id, row in provider_models:
        if provider_id not in selected:
            continue
        matches = matched_site_slugs(
            provider_model_id,
            row,
            normalized_index,
            bag_index,
        )
        # A provider row can expose a generic/base identity in addition to its
        # concrete model ID.  Never fan that row out to benchmark variants such
        # as dated, preview, high-effort, or non-reasoning slugs.  Prefer the
        # provider ID, then the official display name, when either is itself an
        # exact AInsights slug.
        exact_candidates = [
            safe_id(provider_model_id),
            safe_id(row.get("name")),
            safe_id(str(row.get("base_model") or "").split("/", 1)[-1]),
        ]
        for exact_slug in exact_candidates:
            if exact_slug in matches:
                matches = {exact_slug: matches[exact_slug]}
                break
        for slug, quality in matches.items():
            candidate = (quality, provider_model_id)
            incumbent = selected[provider_id].get(slug)
            if incumbent is None or candidate < incumbent:
                selected[provider_id][slug] = candidate
    return {
        provider_id: {
            slug: value[1]
            for slug, value in sorted(slug_rows.items())
        }
        for provider_id, slug_rows in selected.items()
    }


def token_plan_rows(provider_id: str) -> list[dict[str, Any]]:
    is_cn = provider_id.endswith("-cn")
    currency = "CNY" if is_cn else "USD"
    rows: list[dict[str, Any]] = []
    for tier_id, name, monthly_price, weekly_credits in TOKEN_TIERS[provider_id]:
        monthly_credit_equivalent = weekly_credits * 52 / 12
        row: dict[str, Any] = {
            "id": f"{provider_id}-{tier_id}",
            "providerId": provider_id,
            "name": name,
            "billingType": "subscription",
            "displayType": "token-plan",
            "currency": currency,
            "monthlyPriceUsd": None if is_cn else monthly_price,
            "weeklyCredits": weekly_credits,
            "monthlyCreditsEquivalent": round(monthly_credit_equivalent, 6),
            "comparisonClass": "non-comparable",
            "region": PROVIDER_DEFINITIONS[provider_id]["region"],
            "sourceIds": [PROVIDER_DEFINITIONS[provider_id]["sourceId"]],
            "creditFormulaPublished": False,
            "notes": (
                "Credits per request vary by model, input/output tokens, reasoning, and tools; "
                "the plan cannot be converted to a fixed USD per million tokens."
            ),
        }
        if is_cn:
            row.update(
                {
                    "monthlyPriceLocal": monthly_price,
                    "costPerIncludedCreditLocal": round(
                        monthly_price / monthly_credit_equivalent,
                        9,
                    ),
                    "currentPriceIsLimitedTime": True,
                }
            )
        else:
            row["costPerIncludedCreditUsd"] = round(
                monthly_price / monthly_credit_equivalent,
                9,
            )
        rows.append(row)
    return rows


def coding_plan_row(provider_id: str) -> dict[str, Any]:
    row = {
        "id": f"{provider_id}-monthly",
        "providerId": provider_id,
        "billingType": "subscription",
        "displayType": "coding",
        "comparisonClass": "non-comparable",
        "region": PROVIDER_DEFINITIONS[provider_id]["region"],
        "callsPerFiveHours": 6_000,
        "callsPerWeek": 45_000,
        "callsPerMonth": 90_000,
        "sourceIds": [PROVIDER_DEFINITIONS[provider_id]["sourceId"]],
        "notes": (
            "Published usage is measured in model requests rather than a fixed token quota, "
            "so no USD per million tokens value is calculated."
        ),
        **CODING_PLANS[provider_id],
    }
    return row


def non_comparable_offer(
    offer_id: str,
    provider_id: str,
    plan_id: str,
    slug: str,
    provider_model_id: str,
    pricing_kind: str,
) -> dict[str, Any]:
    offer: dict[str, Any] = {
        "id": offer_id,
        "providerId": provider_id,
        "planId": plan_id,
        "modelSlugs": [slug],
        "providerModelId": provider_model_id,
        "pricingKind": pricing_kind,
        "comparable": False,
        "inputPerMillionTokensUsd": None,
        "cacheReadPerMillionTokensUsd": None,
        "outputPerMillionTokensUsd": None,
        "sourceIds": [PROVIDER_DEFINITIONS[provider_id]["sourceId"]],
    }
    if provider_id.startswith("alibaba-token-plan"):
        offer["notes"] = (
            "This model is listed for the plan, but Alibaba does not publish a stable "
            "model/token-to-Credit conversion formula."
        )
        if slug == "qwen3-8-max":
            offer.update(
                {
                    "offPeakCreditMultiplier": 0.5,
                    "offPeakLocalTime": "22:00-08:00",
                    "offPeakTimeZone": "Asia/Shanghai",
                    "offPeakNotes": "Qwen3.8 Max consumes 50% Credits during the published night window.",
                }
            )
    else:
        offer["notes"] = (
            "This model is listed for the Coding Plan. Published limits are calls, "
            "not tokens, so the effective token price is unavailable."
        )
    return offer


def build_fragment(snapshot: Path, models_path: Path) -> dict[str, Any]:
    site_models = load_site_models(models_path)
    normalized_index, bag_index, _ = build_site_indexes(site_models)
    _, provider_models = load_models_dev_snapshot(snapshot)
    support = collect_plan_support(provider_models, normalized_index, bag_index)

    providers = [
        {
            "id": provider_id,
            "name": definition["name"],
            "category": definition["category"],
            "url": definition["url"],
            "pricingUrl": definition["url"],
            "region": definition["region"],
            "sourceIds": [definition["sourceId"]],
        }
        for provider_id, definition in PROVIDER_DEFINITIONS.items()
    ]
    plans = [
        row
        for provider_id in TOKEN_TIERS
        for row in token_plan_rows(provider_id)
    ] + [coding_plan_row(provider_id) for provider_id in CODING_PLANS]
    offers: list[dict[str, Any]] = []
    for provider_id, model_rows in support.items():
        plan_ids = (
            [row["id"] for row in plans if row["providerId"] == provider_id]
        )
        pricing_kind = (
            "non-comparable-credit-plan"
            if provider_id.startswith("alibaba-token-plan")
            else "non-comparable-call-plan"
        )
        for plan_id in plan_ids:
            for slug, provider_model_id in model_rows.items():
                offers.append(
                    non_comparable_offer(
                        f"{safe_id(plan_id)}-{safe_id(slug)}",
                        provider_id,
                        plan_id,
                        slug,
                        provider_model_id,
                        pricing_kind,
                    )
                )

    sources = [
        {
            "id": TOKEN_PLAN_GLOBAL_SOURCE,
            "title": "Alibaba Cloud Model Studio Token Plan — Personal overview",
            "publisher": "Alibaba Cloud",
            "url": PROVIDER_DEFINITIONS["alibaba-token-plan"]["url"],
            "kind": "official-pricing",
            "asOf": SNAPSHOT_DATE,
            "accessedAt": SNAPSHOT_DATE,
            "notes": (
                "Lite $6/month with 2,500 Credits/week; Standard $20 with 10,000; "
                "Pro $70 with 40,000. Credits vary dynamically by model and request."
            ),
        },
        {
            "id": TOKEN_PLAN_CN_SOURCE,
            "title": "百炼 Token Plan 个人版套餐说明",
            "publisher": "阿里云",
            "url": PROVIDER_DEFINITIONS["alibaba-token-plan-cn"]["url"],
            "kind": "official-pricing",
            "asOf": SNAPSHOT_DATE,
            "accessedAt": SNAPSHOT_DATE,
            "notes": (
                "当前限时价：Lite ¥39/月、2,500 Credits/周；Standard ¥139、10,000；"
                "Pro ¥499、40,000。Qwen3.8 Max 公布夜间 Credits 五折。"
            ),
        },
        {
            "id": CODING_PLAN_GLOBAL_SOURCE,
            "title": "Alibaba Cloud Model Studio Coding Plan",
            "publisher": "Alibaba Cloud",
            "url": PROVIDER_DEFINITIONS["alibaba-coding-plan"]["url"],
            "kind": "official-pricing",
            "asOf": SNAPSHOT_DATE,
            "accessedAt": SNAPSHOT_DATE,
            "notes": "$50/month; 6,000 calls/5 hours, 45,000/week, and 90,000/month.",
        },
        {
            "id": CODING_PLAN_CN_SOURCE,
            "title": "百炼 Coding Plan 套餐说明",
            "publisher": "阿里云",
            "url": PROVIDER_DEFINITIONS["alibaba-coding-plan-cn"]["url"],
            "kind": "official-pricing",
            "asOf": SNAPSHOT_DATE,
            "accessedAt": SNAPSHOT_DATE,
            "notes": "¥200/month (published first-month promotion ¥39.90); 6,000 calls/5 hours, 45,000/week, and 90,000/month.",
        },
    ]
    return {
        "schemaVersion": 1,
        "mergeTarget": "data/pricing/provider_pricing.json",
        "checkedAt": SNAPSHOT_DATE,
        "researchScope": "Alibaba Token Plan and Coding Plan, Global and China",
        "comparisonPolicy": {
            "creditsWithoutPerModelFormula": "non-comparable",
            "callsWithoutTokenQuota": "non-comparable",
        },
        "modelsDevSupportSnapshot": SNAPSHOT_COMMIT,
        "providers": providers,
        "plans": plans,
        "offers": offers,
        "sources": sources,
        "supportCounts": {
            provider_id: len(model_rows)
            for provider_id, model_rows in support.items()
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--models", type=Path, default=DEFAULT_MODELS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    fragment = build_fragment(args.snapshot, args.models)
    args.output.write_text(
        json.dumps(fragment, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "providers": len(fragment["providers"]),
                "plans": len(fragment["plans"]),
                "offers": len(fragment["offers"]),
                "sources": len(fragment["sources"]),
                "supportCounts": fragment["supportCounts"],
                "output": str(args.output),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
