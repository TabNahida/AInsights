#!/usr/bin/env python3
"""Generate researched China subscription-plan pricing as single-model offers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT_ROOT / "data" / "pricing" / "research_china_subscription_plans.json"
CHECKED_AT = "2026-08-11"


def source(source_id: str, title: str, publisher: str, url: str, notes: str) -> dict[str, Any]:
    return {
        "id": source_id,
        "title": title,
        "publisher": publisher,
        "url": url,
        "kind": "official-pricing",
        "asOf": CHECKED_AT,
        "accessedAt": CHECKED_AT,
        "notes": notes,
    }


def build_fragment() -> dict[str, Any]:
    providers: list[dict[str, Any]] = []
    plans: list[dict[str, Any]] = []
    offers: list[dict[str, Any]] = []
    sources = [
        source(
            "stepfun-step-plan-official-2026-08-11",
            "Step Plan pricing and Credit rules",
            "StepFun",
            "https://platform.stepfun.com/docs/zh/step-plan/overview.md",
            "Official monthly, quarterly, and annual prices, included Credits, and the rule that 1M Credits equals CNY 1 of PAYG value.",
        ),
        source(
            "stepfun-payg-official-2026-08-11",
            "StepFun model PAYG pricing",
            "StepFun",
            "https://platform.stepfun.com/docs/zh/guides/pricing/details.md",
            "Official CNY rates per million tokens used with the Step Plan discount factor.",
        ),
        source(
            "bigmodel-coding-plan-v3-official-2026-08-11",
            "BigModel Coding Plan V3 pricing, limits, and point coefficients",
            "Zhipu AI BigModel",
            "https://docs.bigmodel.cn/cn/coding-plan/overview.md",
            "Official plan prices, rolling point limits, and per-model input/cache/output point coefficients.",
        ),
        source(
            "volcengine-agent-plan-official-2026-08-11",
            "Volcengine Ark Agent Plan",
            "Volcengine",
            "https://www.volcengine.com/docs/82379/2366394",
            "Official AFP package prices. The full per-model AFP coefficient table was not sufficiently verified, so these plans have no token-price offers.",
        ),
    ]

    # Step Plan: the plan discount is the monthly-equivalent payment divided
    # by the monthly Credit face value.  The resulting multiplier applies to
    # each supported model's official PAYG token rates.
    providers.append({
        "id": "stepfun-step-plan",
        "name": "StepFun Step Plan",
        "category": "token-plan",
        "url": "https://platform.stepfun.com/docs/zh/step-plan/overview.md",
        "pricingUrl": "https://platform.stepfun.com/docs/zh/step-plan/overview.md",
        "region": "China",
        "sourceIds": [
            "stepfun-step-plan-official-2026-08-11",
            "stepfun-payg-official-2026-08-11",
        ],
    })
    step_models = {
        "step-3-7-flash": {"input": 1.35, "cache": 0.27, "output": 8.1},
        "step-3-5-flash": {"input": 0.7, "cache": 0.14, "output": 2.1},
    }
    step_tiers = {
        "mini": {"name": "Mini", "credits": 400, "month": 49, "quarter": 129, "year": 456},
        "plus": {"name": "Plus", "credits": 1_600, "month": 99, "quarter": 269, "year": 936},
        "pro": {"name": "Pro", "credits": 8_000, "month": 199, "quarter": 539, "year": 1_860},
        "max": {"name": "Max", "credits": 40_000, "month": 699, "quarter": 1_889, "year": 6_666},
    }
    cycles = {
        "monthly": ("Monthly", lambda tier: tier["month"], "monthlyPriceLocal", lambda tier: tier["month"]),
        "quarterly": ("Quarterly", lambda tier: tier["quarter"] / 3, "quarterlyPriceLocal", lambda tier: tier["quarter"]),
        "annual": ("Annual", lambda tier: tier["year"] / 12, "annualPriceLocal", lambda tier: tier["year"]),
    }
    for tier_id, tier in step_tiers.items():
        for cycle_id, (cycle_name, monthly_equivalent, total_field, total_value) in cycles.items():
            plan_id = f"stepfun-step-plan-{tier_id}-{cycle_id}"
            monthly_cost = monthly_equivalent(tier)
            discount_factor = monthly_cost / tier["credits"]
            plan: dict[str, Any] = {
                "id": plan_id,
                "providerId": "stepfun-step-plan",
                "name": f"{tier['name']} {cycle_name}",
                "billingType": "token-plan",
                "displayType": "token-plan",
                "currency": "CNY",
                total_field: total_value(tier),
                "includedMillionCreditsPerMonth": tier["credits"],
                "creditFaceValueLocalPerMillion": 1,
                "comparisonClass": "effective-token-comparable",
                "quotaLabel": f"{tier['credits']:,}M Credits / month · 1M Credits = CNY 1",
                "sourceIds": [
                    "stepfun-step-plan-official-2026-08-11",
                    "stepfun-payg-official-2026-08-11",
                ],
            }
            if cycle_id == "quarterly":
                plan["quarterlyEquivalentMonthlyLocal"] = round(monthly_cost, 6)
            elif cycle_id == "annual":
                plan["annualEquivalentMonthlyLocal"] = round(monthly_cost, 6)
            plans.append(plan)
            for model_slug, payg in step_models.items():
                offers.append({
                    "id": f"{plan_id}-{model_slug}",
                    "providerId": "stepfun-step-plan",
                    "planId": plan_id,
                    "modelSlugs": [model_slug],
                    "pricingKind": "effective-subscription",
                    "comparable": True,
                    "inputPerMillionTokensUsd": None,
                    "cacheReadPerMillionTokensUsd": None,
                    "outputPerMillionTokensUsd": None,
                    "inputPerMillionTokensLocal": round(payg["input"] * discount_factor, 9),
                    "cacheReadPerMillionTokensLocal": round(payg["cache"] * discount_factor, 9),
                    "outputPerMillionTokensLocal": round(payg["output"] * discount_factor, 9),
                    "calculation": "PAYG rate × (monthly-equivalent plan price ÷ monthly Credit face value)",
                    "sourceIds": [
                        "stepfun-step-plan-official-2026-08-11",
                        "stepfun-payg-official-2026-08-11",
                    ],
                    "notes": "Normalized at full monthly Credit utilization; unused Credits and rolling-window constraints can raise the realized price.",
                })

    # BigModel V3: points = tokens × coefficient / 10,000.  Weekly
    # points are normalized to 52/12 weeks per month at full utilization.
    providers.append({
        "id": "bigmodel-coding-plan",
        "name": "BigModel Coding Plan V3",
        "category": "coding-subscription",
        "url": "https://docs.bigmodel.cn/cn/coding-plan/overview.md",
        "pricingUrl": "https://docs.bigmodel.cn/cn/coding-plan/overview.md",
        "region": "China",
        "sourceIds": ["bigmodel-coding-plan-v3-official-2026-08-11"],
    })
    bigmodel_tiers = {
        "lite": {"name": "Lite", "monthly": 118, "quarterlyMonthly": 94.4, "annualMonthly": 82.6, "fiveHour": 2_000, "weekly": 10_000},
        "pro": {"name": "Pro", "monthly": 538, "quarterlyMonthly": 430.4, "annualMonthly": 376.6, "fiveHour": 12_000, "weekly": 60_000},
        "max": {"name": "Max", "monthly": 1_078, "quarterlyMonthly": 862.4, "annualMonthly": 754.6, "fiveHour": 28_000, "weekly": 140_000},
    }
    bigmodel_models = {
        "glm-5-2": {"input": 6.9, "cache": 1.7, "output": 24},
        "glm-4-7": {"input": 4.6, "cache": 1.2, "output": 16},
    }
    bigmodel_cycles = {
        "monthly": ("Monthly", "monthly"),
        "quarterly": ("Quarterly", "quarterlyMonthly"),
        "annual": ("Annual", "annualMonthly"),
    }
    for tier_id, tier in bigmodel_tiers.items():
        monthly_points = tier["weekly"] * 52 / 12
        for cycle_id, (cycle_name, price_key) in bigmodel_cycles.items():
            plan_id = f"bigmodel-coding-{tier_id}-{cycle_id}"
            monthly_cost = tier[price_key]
            plan: dict[str, Any] = {
                "id": plan_id,
                "providerId": "bigmodel-coding-plan",
                "name": f"{tier['name']} {cycle_name}",
                "billingType": "subscription",
                "displayType": "coding",
                "currency": "CNY",
                "includedPointsPerFiveHours": tier["fiveHour"],
                "weeklyPoints": tier["weekly"],
                "monthlyPointsEquivalent": round(monthly_points, 6),
                "comparisonClass": "effective-token-comparable",
                "quotaLabel": f"{tier['fiveHour']:,} points / 5h · {tier['weekly']:,} / week",
                "sourceIds": ["bigmodel-coding-plan-v3-official-2026-08-11"],
            }
            if cycle_id == "monthly":
                plan["monthlyPriceLocal"] = monthly_cost
            elif cycle_id == "quarterly":
                plan["quarterlyEquivalentMonthlyLocal"] = monthly_cost
                plan["quarterlyPriceLocal"] = round(monthly_cost * 3, 6)
            else:
                plan["annualEquivalentMonthlyLocal"] = monthly_cost
                plan["annualPriceLocal"] = round(monthly_cost * 12, 6)
            plans.append(plan)
            local_per_point = monthly_cost / monthly_points
            for model_slug, coefficients in bigmodel_models.items():
                # One million tokens consume 100 × coefficient points.
                offers.append({
                    "id": f"{plan_id}-{model_slug}",
                    "providerId": "bigmodel-coding-plan",
                    "planId": plan_id,
                    "modelSlugs": [model_slug],
                    "pricingKind": "effective-subscription",
                    "comparable": True,
                    "inputPerMillionTokensUsd": None,
                    "cacheReadPerMillionTokensUsd": None,
                    "outputPerMillionTokensUsd": None,
                    "inputPerMillionTokensLocal": round(local_per_point * 100 * coefficients["input"], 9),
                    "cacheReadPerMillionTokensLocal": round(local_per_point * 100 * coefficients["cache"], 9),
                    "outputPerMillionTokensLocal": round(local_per_point * 100 * coefficients["output"], 9),
                    "offPeakCreditMultiplier": 0.5,
                    "calculation": "monthly plan price ÷ (weekly points × 52/12) × 100 × model coefficient",
                    "sourceIds": ["bigmodel-coding-plan-v3-official-2026-08-11"],
                    "notes": "Normalized at full weekly-point utilization. Published off-peak point consumption is 50%; the base comparison does not assume off-peak-only use.",
                })

    # Volcengine Agent packages are useful Provider-page context, but no model
    # offer is emitted until the complete AFP coefficient table is verified.
    providers.append({
        "id": "volcengine-agent-plan",
        "name": "Volcengine Ark Agent Plan",
        "category": "coding-subscription",
        "url": "https://www.volcengine.com/docs/82379/2366394",
        "pricingUrl": "https://www.volcengine.com/docs/82379/2366394",
        "region": "China",
        "sourceIds": ["volcengine-agent-plan-official-2026-08-11"],
        "notes": "Packages are shown without model token prices until the full AFP coefficient table is verified.",
    })
    for tier_id, name, price, afp in (
        ("small", "Small", 40, 20_000),
        ("medium", "Medium", 200, 100_000),
        ("large", "Large", 500, 250_000),
        ("max", "Max", 1_000, 500_000),
    ):
        plans.append({
            "id": f"volcengine-agent-{tier_id}",
            "providerId": "volcengine-agent-plan",
            "name": name,
            "billingType": "subscription",
            "displayType": "coding",
            "currency": "CNY",
            "monthlyPriceLocal": price,
            "includedAfp": afp,
            "comparisonClass": "non-comparable",
            "quotaLabel": f"{afp:,} AFP",
            "sourceIds": ["volcengine-agent-plan-official-2026-08-11"],
        })

    return {
        "checkedAt": CHECKED_AT,
        "providers": providers,
        "plans": plans,
        "offers": offers,
        "sources": sources,
    }


def main() -> int:
    payload = build_fragment()
    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "output": str(OUTPUT),
        "providers": len(payload["providers"]),
        "plans": len(payload["plans"]),
        "offers": len(payload["offers"]),
        "sources": len(payload["sources"]),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
