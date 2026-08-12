import unittest
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

from scripts.build_docs_site import (
    AINDEX_GROUPS,
    DEFAULT_AINDEX_WEIGHTS,
    DEFAULT_EXTERNAL_BENCHMARKS_JSON,
    DEFAULT_INPUT_CSV,
    DEFAULT_OUTPUT_JSON,
    DEFAULT_PROVIDER_PRICING_JSON,
    PRIMARY_RANKING_METHOD,
    _rank_consensus_rows_by_composite_score,
    build_site_payload,
    load_external_benchmarks,
    load_provider_pricing,
    merge_provider_pricing_catalogue,
    open_source_type,
    read_csv_rows,
    score_model_for_preset,
    variant_group,
    variant_priority,
    weighted_metric_score,
    write_site_payload,
)


class BuildDocsSiteTests(unittest.TestCase):
    def test_provider_pricing_supplements_replace_append_and_remove_by_id(self):
        base = {
            "asOf": "2026-08-10",
            "providers": [{"id": "keep"}, {"id": "replace", "value": 1}],
            "plans": [{"id": "remove"}],
            "offers": [],
            "sources": [],
            "exchangeRates": {"EUR": {"usdPerUnit": 1.1}},
            "stalePricingMethod": {"id": "obsolete-v1"},
        }
        supplement = {
            "checkedAt": "2026-08-11",
            "providers": [
                {"id": "replace", "value": 2},
                {"id": "append", "value": 3},
            ],
            "plans": [],
            "offers": [],
            "sources": [],
            "remove": {"plans": ["remove"]},
            "removeMetadata": ["stalePricingMethod"],
            "exchangeRates": {"CNY": {"usdPerUnit": 0.14}},
            "metadata": {"pricingMethodFixture": {"id": "fixture-v1"}},
        }

        merged = merge_provider_pricing_catalogue(base, supplement)

        self.assertEqual(merged["asOf"], "2026-08-11")
        self.assertEqual(
            merged["providers"],
            [{"id": "keep"}, {"id": "replace", "value": 2}, {"id": "append", "value": 3}],
        )
        self.assertEqual(merged["plans"], [])
        self.assertEqual(set(merged["exchangeRates"]), {"EUR", "CNY"})
        self.assertNotIn("stalePricingMethod", merged)
        self.assertEqual(merged["pricingMethodFixture"], {"id": "fixture-v1"})

    def test_provider_pricing_catalogue_references_are_integral_and_unique(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        provider_ids = [provider["id"] for provider in catalogue["providers"]]
        plan_ids = [plan["id"] for plan in catalogue["plans"]]
        offer_ids = [offer["id"] for offer in catalogue["offers"]]
        source_ids = [source["id"] for source in catalogue["sources"]]

        for ids in (provider_ids, plan_ids, offer_ids, source_ids):
            self.assertEqual(len(ids), len(set(ids)))

        provider_id_set = set(provider_ids)
        plan_by_id = {plan["id"]: plan for plan in catalogue["plans"]}
        source_id_set = set(source_ids)
        exchange_rates = catalogue.get("exchangeRates", {})
        model_slugs = {
            model["slug"]
            for model in json.loads(DEFAULT_OUTPUT_JSON.read_text(encoding="utf-8"))["models"]
        }

        for provider in catalogue["providers"]:
            self.assertTrue(set(provider["sourceIds"]) <= source_id_set)
        for currency, rate in exchange_rates.items():
            self.assertNotEqual(currency, "USD")
            self.assertGreater(rate["usdPerUnit"], 0)
            self.assertGreater(rate["unitsPerUsd"], 0)
            self.assertIn(rate["sourceId"], source_id_set)
        for plan in catalogue["plans"]:
            self.assertIn(plan["providerId"], provider_id_set)
            self.assertTrue(set(plan["sourceIds"]) <= source_id_set)
        for offer in catalogue["offers"]:
            self.assertIn(offer["providerId"], provider_id_set)
            self.assertIn(offer["planId"], plan_by_id)
            self.assertEqual(plan_by_id[offer["planId"]]["providerId"], offer["providerId"])
            self.assertEqual(len(offer["modelSlugs"]), 1)
            self.assertTrue(set(offer["modelSlugs"]) <= model_slugs)
            self.assertTrue(set(offer["sourceIds"]) <= source_id_set)
            token_rate_fields = (
                "inputPerMillionTokensUsd",
                "cacheReadPerMillionTokensUsd",
                "outputPerMillionTokensUsd",
                "inputPerMillionTokensLocal",
                "cacheReadPerMillionTokensLocal",
                "outputPerMillionTokensLocal",
            )
            if any(offer.get(field) == 0 for field in token_rate_fields):
                self.assertTrue(
                    offer.get("publishedZeroRate"),
                    f"zero token rate must be explicitly sourced: {offer['id']}",
                )
            offer_currency = offer.get("currency") or plan_by_id[offer["planId"]].get(
                "currency",
                catalogue["currency"],
            )
            local_rate_fields = (
                "inputPerMillionTokensLocal",
                "cacheReadPerMillionTokensLocal",
                "outputPerMillionTokensLocal",
                "effectiveLocalPerMillionTokens",
                "effectiveLocalPerMillionIncludedTokens",
            )
            has_local_rate = any(offer.get(field) is not None for field in local_rate_fields)
            if offer.get("comparable") and offer_currency != "USD" and has_local_rate:
                self.assertIn(offer_currency, exchange_rates)
            for variant in offer.get("planVariants", []):
                self.assertIn(variant["planId"], plan_by_id)
                self.assertEqual(
                    plan_by_id[variant["planId"]]["providerId"],
                    offer["providerId"],
                )

        expanded_offer_ids = offer_ids + [
            f"{offer['id']}:{variant.get('idSuffix') or variant['planId']}"
            for offer in catalogue["offers"]
            for variant in offer.get("planVariants", [])
        ]
        self.assertEqual(len(expanded_offer_ids), len(set(expanded_offer_ids)))

    def test_provider_pricing_sources_are_dated_and_linked(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)

        self.assertEqual(catalogue["asOf"], "2026-08-12")
        self.assertEqual(catalogue["currency"], "USD")
        weights = catalogue["workloadScenario"]["weights"]
        self.assertAlmostEqual(sum(weights.values()), 1)
        self.assertGreater(weights["input"], 0)
        self.assertGreater(weights["cacheRead"], 0)
        self.assertGreater(weights["output"], 0)
        for source in catalogue["sources"]:
            self.assertTrue(source["url"].startswith("https://"))
            self.assertLessEqual(source["asOf"], source["accessedAt"])
            self.assertLessEqual(source["accessedAt"], catalogue["asOf"])
            self.assertTrue(source["publisher"])
            self.assertTrue(source["kind"])

    def test_non_rankable_pricing_classes_are_explicitly_non_comparable(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)

        for offer in catalogue["offers"]:
            coverage_mode = str(offer.get("coverageMode", "")).lower()
            is_unrankable = (
                offer.get("bestCaseOnly") is True
                or offer.get("pricingKind") == "estimated-effective-subscription"
                or any(
                    marker in coverage_mode
                    for marker in ("usage-credit", "marginal", "overage")
                )
            )
            if is_unrankable:
                self.assertFalse(
                    offer.get("comparable", True),
                    f"display-only offer must not enter cheapest ranking: {offer['id']}",
                )

    def test_provider_pricing_requires_explicit_model_slugs_without_family_inheritance(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)

        for section in ("providers", "plans", "offers"):
            for row in catalogue[section]:
                self.assertNotIn("inheritVariantGroupPricing", row)

    def test_models_dev_expansion_is_broad_single_model_and_positive_rate_only(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        imported_providers = [
            provider
            for provider in catalogue["providers"]
            if provider.get("importedFrom") == "models.dev"
        ]
        imported_offers = [
            offer
            for offer in catalogue["offers"]
            if offer.get("importedFrom") == "models.dev"
        ]

        self.assertGreaterEqual(len(catalogue["providers"]), 140)
        # Official-provider supplements replace a handful of community rows,
        # while the remaining snapshot still supplies broad aggregator coverage.
        self.assertGreaterEqual(len(imported_providers), 115)
        # Exact slug matching intentionally drops ambiguous display-name and
        # variant-group expansions while preserving broad provider coverage.
        self.assertGreaterEqual(len(imported_offers), 2_700)
        self.assertGreaterEqual(
            len({offer["modelSlugs"][0] for offer in imported_offers}),
            240,
        )
        for offer in imported_offers:
            self.assertEqual(len(offer["modelSlugs"]), 1)
            if offer.get("bestCaseOnly"):
                self.assertFalse(offer["comparable"])
            else:
                self.assertTrue(offer["comparable"])
            self.assertTrue(offer["estimated"])
            self.assertGreater(offer["inputPerMillionTokensUsd"], 0)
            self.assertGreater(offer["outputPerMillionTokensUsd"], 0)
            self.assertNotEqual(offer.get("cacheReadPerMillionTokensUsd"), 0)
            self.assertIn(
                offer["mappingMethod"],
                {"exact-normalized-identifier", "exact-token-multiset"},
            )
            self.assertEqual(offer["evidenceKind"], "community-catalog")

        imported_provider_ids = {provider["id"] for provider in imported_providers}
        self.assertFalse(
            {
                "alibaba-token-plan",
                "alibaba-token-plan-cn",
                "alibaba-coding-plan",
                "alibaba-coding-plan-cn",
                "anthropic-api",
            }
            & imported_provider_ids
        )

    def test_alibaba_token_and_coding_plans_keep_native_units_per_model(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        plans = {plan["id"]: plan for plan in catalogue["plans"]}
        offers = [
            offer
            for offer in catalogue["offers"]
            if offer["providerId"].startswith("alibaba-token-plan")
            or offer["providerId"].startswith("alibaba-coding-plan")
        ]

        expected_token_plans = {
            "alibaba-token-plan-lite": ("USD", 6, 2_500),
            "alibaba-token-plan-standard": ("USD", 20, 10_000),
            "alibaba-token-plan-pro": ("USD", 70, 40_000),
            "alibaba-token-plan-cn-lite": ("CNY", 39, 2_500),
            "alibaba-token-plan-cn-standard": ("CNY", 139, 10_000),
            "alibaba-token-plan-cn-pro": ("CNY", 499, 40_000),
        }
        for plan_id, (currency, price, weekly_credits) in expected_token_plans.items():
            plan = plans[plan_id]
            self.assertEqual(plan["currency"], currency)
            self.assertEqual(plan["weeklyCredits"], weekly_credits)
            monthly_credits = weekly_credits * 52 / 12
            self.assertAlmostEqual(plan["monthlyCreditsEquivalent"], monthly_credits, places=5)
            if currency == "USD":
                self.assertEqual(plan["monthlyPriceUsd"], price)
                self.assertAlmostEqual(
                    plan["costPerIncludedCreditUsd"],
                    price / monthly_credits,
                    places=8,
                )
            else:
                self.assertEqual(plan["monthlyPriceLocal"], price)
                self.assertIsNone(plan["monthlyPriceUsd"])
                self.assertAlmostEqual(
                    plan["costPerIncludedCreditLocal"],
                    price / monthly_credits,
                    places=8,
                )

        for plan_id in (
            "alibaba-coding-plan-monthly",
            "alibaba-coding-plan-cn-monthly",
        ):
            plan = plans[plan_id]
            self.assertEqual(plan["callsPerFiveHours"], 6_000)
            self.assertEqual(plan["callsPerWeek"], 45_000)
            self.assertEqual(plan["callsPerMonth"], 90_000)

        self.assertEqual(len(offers), 102)
        for offer in offers:
            self.assertEqual(len(offer["modelSlugs"]), 1)
            self.assertFalse(offer["comparable"])
            self.assertIsNone(offer["inputPerMillionTokensUsd"])
            self.assertIsNone(offer["cacheReadPerMillionTokensUsd"])
            self.assertIsNone(offer["outputPerMillionTokensUsd"])
            self.assertNotIn("preview", offer["modelSlugs"][0])
            self.assertNotIn("0420", offer["modelSlugs"][0])

        night_offers = [
            offer
            for offer in offers
            if offer["modelSlugs"] == ["qwen3-8-max"]
            and offer["providerId"].startswith("alibaba-token-plan")
        ]
        self.assertEqual(len(night_offers), 6)
        for offer in night_offers:
            self.assertEqual(offer["offPeakCreditMultiplier"], 0.5)
            self.assertEqual(offer["offPeakLocalTime"], "22:00-08:00")

    def test_zai_v3_offers_use_supported_slugs_and_peak_credit_formula(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        zai_plans = {
            plan["id"]: plan
            for plan in catalogue["plans"]
            if plan["providerId"] == "z-ai"
        }
        zai_offers = [
            offer
            for offer in catalogue["offers"]
            if offer["providerId"] == "z-ai"
        ]

        self.assertNotIn(
            "glm-5-1",
            {slug for offer in zai_offers for slug in offer["modelSlugs"]},
        )
        comparable = [offer for offer in zai_offers if offer["comparable"]]
        self.assertEqual(
            {offer["id"] for offer in comparable},
            {
                "zai-lite-glm-5-2-peak",
                "zai-pro-glm-5-2-peak",
                "zai-max-glm-5-2-peak",
            },
        )
        for offer in comparable:
            plan = zai_plans[offer["planId"]]
            monthly_credits = offer["weeklyCredits"] * 52 / 12
            usd_per_credit = plan["monthlyPriceUsd"] / monthly_credits
            self.assertAlmostEqual(
                offer["inputPerMillionTokensUsd"],
                usd_per_credit * 690,
                places=6,
            )
            self.assertAlmostEqual(
                offer["cacheReadPerMillionTokensUsd"],
                usd_per_credit * 170,
                places=6,
            )
            self.assertAlmostEqual(
                offer["outputPerMillionTokensUsd"],
                usd_per_credit * 2400,
                places=6,
            )
            self.assertEqual(offer["offPeakRateMultiplier"], 0.5)

    def test_kimi_cn_plans_use_live_goods_and_verified_model_access(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        expected_prices = {
            "kimi-code-andante": (49, 468, 39),
            "kimi-code-moderato": (99, 948, 79),
            "kimi-code-allegretto": (199, 1908, 159),
            "kimi-code-allegro": (699, 6708, 559),
        }
        kimi_plans = {
            plan["id"]: plan
            for plan in catalogue["plans"]
            if plan["providerId"] == "kimi"
        }

        self.assertEqual(set(kimi_plans), set(expected_prices))
        for plan_id, prices in expected_prices.items():
            plan = kimi_plans[plan_id]
            self.assertEqual(plan["region"], "CN")
            self.assertEqual(plan["currency"], "CNY")
            self.assertIsNone(plan["monthlyPriceUsd"])
            self.assertEqual(
                (
                    plan["monthlyPriceLocal"],
                    plan["annualTotalLocal"],
                    plan["annualEquivalentMonthlyLocal"],
                ),
                prices,
            )
            self.assertEqual(plan["comparisonClass"], "non-comparable")

        kimi_offers = [
            offer
            for offer in catalogue["offers"]
            if offer["providerId"] == "kimi"
        ]
        kimi_model_slugs_by_plan = {}
        for offer in kimi_offers:
            kimi_model_slugs_by_plan.setdefault(offer["planId"], set()).update(
                offer["modelSlugs"]
            )
        self.assertEqual(
            kimi_model_slugs_by_plan["kimi-code-andante"],
            {"kimi-k2-7-code"},
        )
        for plan_id in (
            "kimi-code-moderato",
            "kimi-code-allegretto",
            "kimi-code-allegro",
        ):
            self.assertEqual(
                kimi_model_slugs_by_plan[plan_id],
                {"kimi-k2-7-code", "kimi-k3"},
            )
        self.assertFalse(
            {"kimi-k2-6", "kimi-k2-5"}
            & {slug for offer in kimi_offers for slug in offer["modelSlugs"]}
        )
        self.assertTrue(all(not offer["comparable"] for offer in kimi_offers))

        source = next(
            source
            for source in catalogue["sources"]
            if source["id"] == "kimi-code-pricing"
        )
        self.assertEqual(source["httpMethod"], "POST")
        self.assertEqual(source["kind"], "official-live-api")
        self.assertTrue(source["url"].endswith("GoodsService/ListGoods"))

    def test_alibaba_token_and_coding_plans_keep_native_credit_and_call_limits(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        plans = {plan["id"]: plan for plan in catalogue["plans"]}

        expected_credits = {
            "alibaba-token-plan-lite": (6, 2_500),
            "alibaba-token-plan-standard": (20, 10_000),
            "alibaba-token-plan-pro": (70, 40_000),
        }
        for plan_id, (monthly_price, weekly_credits) in expected_credits.items():
            plan = plans[plan_id]
            self.assertEqual(plan["monthlyPriceUsd"], monthly_price)
            self.assertEqual(plan["weeklyCredits"], weekly_credits)
            self.assertFalse(plan["creditFormulaPublished"])
            self.assertEqual(plan["comparisonClass"], "non-comparable")

        expected_cn = {
            "alibaba-token-plan-cn-lite": (39, 2_500),
            "alibaba-token-plan-cn-standard": (139, 10_000),
            "alibaba-token-plan-cn-pro": (499, 40_000),
        }
        for plan_id, (monthly_price, weekly_credits) in expected_cn.items():
            plan = plans[plan_id]
            self.assertEqual(plan["currency"], "CNY")
            self.assertEqual(plan["monthlyPriceLocal"], monthly_price)
            self.assertEqual(plan["weeklyCredits"], weekly_credits)

        for plan_id in (
            "alibaba-coding-plan-monthly",
            "alibaba-coding-plan-cn-monthly",
        ):
            plan = plans[plan_id]
            self.assertEqual(plan["callsPerFiveHours"], 6_000)
            self.assertEqual(plan["callsPerWeek"], 45_000)
            self.assertEqual(plan["callsPerMonth"], 90_000)
            self.assertEqual(plan["comparisonClass"], "non-comparable")

        alibaba_plan_offers = [
            offer
            for offer in catalogue["offers"]
            if offer["providerId"].startswith("alibaba-token-plan")
            or offer["providerId"].startswith("alibaba-coding-plan")
        ]
        self.assertEqual(len(alibaba_plan_offers), 102)
        self.assertTrue(all(len(offer["modelSlugs"]) == 1 for offer in alibaba_plan_offers))
        self.assertTrue(all(not offer["comparable"] for offer in alibaba_plan_offers))

    def test_openrouter_offers_use_endpoint_routes_and_nullable_cache(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        offers = [
            offer
            for offer in catalogue["offers"]
            if offer["providerId"] == "openrouter"
        ]

        self.assertGreaterEqual(len(offers), 40)
        for offer in offers:
            self.assertTrue(offer["routeProvider"])
            self.assertTrue(offer["routeTag"])
            self.assertTrue(offer["routeLabel"])
            self.assertTrue(offer["providerModelId"])
        by_id = {offer["id"]: offer for offer in offers}
        self.assertEqual(by_id["or-gpt-5-6-terra"]["routeTag"], "openai/flex")
        self.assertEqual(by_id["or-gpt-5-6-terra"]["inputPerMillionTokensUsd"], 0.5)
        self.assertIsNone(by_id["or-qwen3-6-plus"]["cacheReadPerMillionTokensUsd"])

    def test_openrouter_long_context_overrides_keep_thresholds_and_recomputed_mix(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        offers = {offer["id"]: offer for offer in catalogue["offers"]}
        expected = {
            "or-gemini-3-1-pro-preview": (1_048_576, 200_000, 2, 0.2, 9, 1.44),
            "or-gpt-5-4": (1_050_000, 272_000, 2.5, 0.25, 11.25, 1.8),
            "or-gpt-5-5": (1_050_000, 272_000, 5, 0.5, 22.5, 3.6),
            "or-gpt-5-6-luna": (1_050_000, 272_000, 0.1, 0.01, 0.45, 0.072),
            "or-gpt-5-6-sol": (1_050_000, 272_000, 10, 1, 45, 7.2),
            "or-gpt-5-6-terra": (1_050_000, 272_000, 1, 0.1, 4.5, 0.72),
            "or-grok-4-3": (1_000_000, 200_000, 2.5, 0.4, 5, 1.28),
            "or-grok-4-5": (500_000, 200_000, 4, 0.6, 12, 2.42),
            "or-grok-build-0-1": (256_000, 200_000, 2, 0.4, 4, 1.08),
            "or-qwen3-6-plus": (1_000_000, 256_000, 1.3, None, 3.9, 1.56),
            "or-qwen3-7-plus": (1_000_000, 256_000, 0.96, 0.192, 3.84, 0.7104),
        }

        for offer_id, values in expected.items():
            context, threshold, input_rate, cache_rate, output_rate, expected_mix = values
            offer = offers[offer_id]
            override = offer["pricingOverrides"][0]
            self.assertEqual(offer["status"], 0)
            self.assertTrue(offer["dynamic"])
            self.assertEqual(offer["contextLength"], context)
            self.assertEqual(offer["observedAt"], "2026-08-10T10:56:40Z")
            self.assertEqual(override["minPromptTokens"], threshold)
            self.assertEqual(override["inputPerMillionTokensUsd"], input_rate)
            self.assertEqual(override["cacheReadPerMillionTokensUsd"], cache_rate)
            self.assertEqual(override["outputPerMillionTokensUsd"], output_rate)
            effective_cache = input_rate if cache_rate is None else cache_rate
            calculated_mix = 0.2 * input_rate + 0.7 * effective_cache + 0.1 * output_rate
            self.assertAlmostEqual(calculated_mix, expected_mix)

        self.assertEqual(offers["or-gpt-5-6-sol"]["routeProvider"], "Azure")
        self.assertEqual(offers["or-gpt-5-6-sol"]["routeTag"], "azure")
        self.assertEqual(
            offers["or-gpt-5-6-sol"]["endpointModelId"],
            "openai/gpt-5.6-sol-20260709",
        )
        self.assertEqual(offers["or-qwen3-6-plus"]["quantization"], "fp8")
        self.assertIsNone(
            offers["or-qwen3-6-plus"]["pricingOverrides"][0]["cacheReadPerMillionTokensUsd"]
        )

    def test_official_agnes_and_verified_openrouter_rows_cover_top50_gaps(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        offers = {offer["id"]: offer for offer in catalogue["offers"]}
        agnes = offers["sapiens-agnes-2-5-pro-alpha"]

        self.assertEqual(agnes["providerId"], "sapiens-ai")
        self.assertEqual(agnes["planId"], "sapiens-payg")
        self.assertEqual(agnes["modelSlugs"], ["agnes-2-5-pro-alpha"])
        self.assertEqual(agnes["contextLength"], 1000000)
        self.assertEqual(
            (
                agnes["inputPerMillionTokensUsd"],
                agnes["cacheReadPerMillionTokensUsd"],
                agnes["outputPerMillionTokensUsd"],
            ),
            (0.45, 0.0038, 0.9),
        )
        self.assertEqual(agnes["effectiveUsdPerMillionTokens"], 0.18266)
        self.assertTrue(agnes["comparable"])

        expected_openrouter = {
            "or-nex-n2-pro": ("nex-n2-pro", 0.25, 0.025, 1, 262144),
            "or-hy3": ("hy3", 0.1288, 0.0322, 0.5336, 262144),
            "or-inkling-small": ("inkling-small", 0.5, 0.1, 1.2, 524288),
            "or-inkling": ("inkling", 0.95, 0.16, 4.05, 524288),
            "or-mimo-v2-5": ("mimo-v2-5-0424", 0.14, 0.0028, 0.28, 1048576),
        }
        for offer_id, expected in expected_openrouter.items():
            offer = offers[offer_id]
            slug, input_rate, cache_rate, output_rate, context_length = expected
            self.assertEqual(offer["modelSlugs"], [slug])
            self.assertEqual(offer["status"], 0)
            self.assertEqual(offer["observedAt"], "2026-08-10")
            self.assertTrue(offer["dynamic"])
            self.assertEqual(offer["contextLength"], context_length)
            self.assertEqual(
                (
                    offer["inputPerMillionTokensUsd"],
                    offer["cacheReadPerMillionTokensUsd"],
                    offer["outputPerMillionTokensUsd"],
                ),
                (input_rate, cache_rate, output_rate),
            )

        generated = json.loads(DEFAULT_OUTPUT_JSON.read_text(encoding="utf-8"))
        top50_slugs = {
            model["slug"]
            for model in generated["models"]
            if 1 <= int(model.get("rankingProfile", {}).get("publicationRank", 0)) <= 50
        }
        expected_slugs = {"agnes-2-5-pro-alpha"} | {
            expected[0] for expected in expected_openrouter.values()
        }
        self.assertTrue(expected_slugs <= top50_slugs)

    def test_codex_empirical_multiplier_is_only_rankable_for_measured_model(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        offers = [
            offer
            for offer in catalogue["offers"]
            if offer["providerId"] == "openai-codex"
        ]

        comparable = [offer for offer in offers if offer["comparable"]]
        self.assertEqual([offer["modelSlugs"] for offer in comparable], [["gpt-5-6-sol"]])
        self.assertEqual(comparable[0]["subscriptionMultiplier"], 34.6667)
        self.assertEqual(comparable[0]["planId"], "codex-pro-20x")

    def test_codex_official_plans_remain_non_comparable_without_token_quotas(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        plans = {
            plan["id"]: plan
            for plan in catalogue["plans"]
            if plan["providerId"] == "openai-codex"
        }
        expected_monthly = {
            "codex-free": 0,
            "codex-go": 8,
            "codex-plus": 20,
            "codex-pro-5x": 100,
            "codex-pro-20x": 200,
            "codex-business-annual": 20,
            "codex-business-monthly": 25,
            "codex-enterprise": None,
            "codex-edu": None,
        }
        self.assertEqual(
            {plan_id: plans[plan_id]["monthlyPriceUsd"] for plan_id in expected_monthly},
            expected_monthly,
        )
        self.assertTrue(plans["codex-business-annual"]["annualCommitment"])
        self.assertTrue(
            all(
                plan["comparisonClass"] == "non-comparable"
                for plan_id, plan in plans.items()
                if plan_id != "codex-pro-20x"
            )
        )
        plus_offers = [
            offer
            for offer in catalogue["offers"]
            if offer["planId"] == "codex-plus"
        ]
        self.assertEqual(
            {offer["modelSlugs"][0] for offer in plus_offers},
            {"gpt-5-6-sol", "gpt-5-6-terra", "gpt-5-6-luna"},
        )
        self.assertTrue(all(not offer["comparable"] for offer in plus_offers))
        source = next(
            source
            for source in catalogue["sources"]
            if source["id"] == "openai-codex-official-pricing"
        )
        self.assertEqual(source["url"], "https://developers.openai.com/codex/pricing.md")

    def test_openai_api_service_tiers_and_long_context_prices_are_official(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        offers = {
            offer["id"]: offer
            for offer in catalogue["offers"]
            if offer["providerId"] == "openai-api"
        }
        official_offer_ids = {
            f"openai-api-{tier}-{model}"
            for tier in ("standard", "flex", "batch", "fast")
            for model in ("sol", "terra", "luna")
        }
        self.assertTrue(official_offer_ids <= set(offers))
        base_standard = {
            "sol": (5, 0.5, 30),
            "terra": (2, 0.2, 12),
            "luna": (0.2, 0.02, 1.2),
        }
        base_cache_writes = {"sol": 6.25, "terra": 2.5, "luna": 0.25}
        for model, standard in base_standard.items():
            standard_offer = offers[f"openai-api-standard-{model}"]
            standard_rates = (
                standard_offer["inputPerMillionTokensUsd"],
                standard_offer["cacheReadPerMillionTokensUsd"],
                standard_offer["outputPerMillionTokensUsd"],
            )
            self.assertEqual(standard_rates, standard)
            self.assertEqual(
                standard_offer["cacheWritePerMillionTokensUsd"],
                base_cache_writes[model],
            )
            for tier in ("flex", "batch"):
                offer = offers[f"openai-api-{tier}-{model}"]
                self.assertEqual(
                    (
                        offer["inputPerMillionTokensUsd"],
                        offer["cacheReadPerMillionTokensUsd"],
                        offer["outputPerMillionTokensUsd"],
                    ),
                    tuple(rate / 2 for rate in standard),
                )
                self.assertEqual(
                    offer["cacheWritePerMillionTokensUsd"],
                    base_cache_writes[model] / 2,
                )
            fast = offers[f"openai-api-fast-{model}"]
            self.assertEqual(
                (
                    fast["inputPerMillionTokensUsd"],
                    fast["cacheReadPerMillionTokensUsd"],
                    fast["outputPerMillionTokensUsd"],
                ),
                tuple(rate * 2 for rate in standard),
            )
            self.assertEqual(
                fast["cacheWritePerMillionTokensUsd"],
                base_cache_writes[model] * 2,
            )
            for tier in ("standard", "flex", "batch", "fast"):
                override = offers[f"openai-api-{tier}-{model}"]["pricingOverrides"][0]
                self.assertEqual(override["minPromptTokens"], 272_000)
                self.assertEqual(
                    override["cacheWritePerMillionTokensUsd"],
                    offers[f"openai-api-{tier}-{model}"]["cacheWritePerMillionTokensUsd"] * 2,
                )
        source = next(
            source
            for source in catalogue["sources"]
            if source["id"] == "openai-api-official-pricing"
        )
        self.assertEqual(
            source["url"],
            "https://developers.openai.com/api/docs/pricing.md",
        )

    def test_anthropic_fable_entitlements_are_not_misread_as_token_discounts(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        offers = {offer["id"]: offer for offer in catalogue["offers"]}

        for offer_id in (
            "anthropic-pro-fable-5-usage-credits",
            "anthropic-pro-annual-fable-5-usage-credits",
        ):
            offer = offers[offer_id]
            self.assertEqual(offer["coverageMode"], "usage-credits-only")
            self.assertEqual(offer["includedWeeklyLimitShare"], 0)
            self.assertEqual(
                (
                    offer["inputPerMillionTokensUsd"],
                    offer["cacheReadPerMillionTokensUsd"],
                    offer["outputPerMillionTokensUsd"],
                ),
                (10, 1, 50),
            )
            self.assertEqual(offer["effectiveUsdPerMillionTokens"], 7.7)
            self.assertFalse(offer["comparable"])

        for offer_id in (
            "anthropic-max-5x-fable-5",
            "anthropic-max-20x-fable-5",
        ):
            self.assertNotIn(offer_id, offers)

    def test_anthropic_subscription_calculations_are_removed(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        subscription_calculations = [
            offer
            for offer in catalogue["offers"]
            if offer.get("providerId") == "anthropic"
            and (
                offer.get("estimateMethodId")
                or offer.get("pricingKind") == "estimated-effective-subscription"
            )
        ]

        self.assertEqual(subscription_calculations, [])
        self.assertNotIn("anthropicSubscriptionEstimateMethodology", catalogue)
        self.assertNotIn(
            "claude-code-token-quota-estimate-2026-03-27",
            {source["id"] for source in catalogue["sources"]},
        )

    def test_anthropic_fragment_contains_no_subscription_estimates(self):
        fragment = json.loads(
            DEFAULT_PROVIDER_PRICING_JSON.with_name(
                "research_anthropic_offers.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(len(fragment["offers"]), 79)
        self.assertEqual(
            len({offer["id"] for offer in fragment["offers"]}),
            len(fragment["offers"]),
        )
        self.assertTrue(
            all(len(offer["modelSlugs"]) == 1 for offer in fragment["offers"])
        )
        self.assertNotIn("subscriptionEstimateMethodology", fragment)
        self.assertNotIn("metadata", fragment)
        self.assertEqual(
            fragment["removeMetadata"],
            ["anthropicSubscriptionEstimateMethodology"],
        )
        self.assertFalse(
            any(
                offer.get("estimateMethodId")
                or offer.get("pricingKind") == "estimated-effective-subscription"
                for offer in fragment["offers"]
            )
        )
        self.assertNotIn(
            "claude-code-token-quota-estimate-2026-03-27",
            {source["id"] for source in fragment["sources"]},
        )

    def test_first_party_fragment_marks_free_rates_and_supplies_inr_fx(self):
        fragment = json.loads(
            DEFAULT_PROVIDER_PRICING_JSON.with_name(
                "research_first_party_model_apis.json"
            ).read_text(encoding="utf-8")
        )
        source_ids = {source["id"] for source in fragment["sources"]}
        inr = fragment["exchangeRates"]["INR"]
        self.assertGreater(inr["unitsPerUsd"], 0)
        self.assertGreater(inr["usdPerUnit"], 0)
        self.assertAlmostEqual(
            inr["unitsPerUsd"] * inr["usdPerUnit"],
            1,
            places=7,
        )
        self.assertIn(inr["sourceId"], source_ids)

        sarvam = [
            offer
            for offer in fragment["offers"]
            if offer["providerId"] == "sarvam-api"
        ]
        self.assertEqual(len(sarvam), 2)
        for offer in sarvam:
            self.assertTrue(offer["publishedZeroRate"])
            self.assertEqual(offer["inputPerMillionTokensUsd"], 0)
            self.assertEqual(offer["outputPerMillionTokensUsd"], 0)

    def test_anthropic_paid_plan_usage_credits_use_standard_api_rates(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        offers = {offer["id"]: offer for offer in catalogue["offers"]}
        expected = {
            "anthropic-usage-credits-fable-5": (10, 1, 50, 7.7),
            "anthropic-usage-credits-opus-5": (5, 0.5, 25, 3.85),
            "anthropic-usage-credits-sonnet-5": (2, 0.2, 10, 1.54),
            "anthropic-usage-credits-haiku-4-5": (1, 0.1, 5, 0.77),
        }

        for offer_id, rates in expected.items():
            offer = offers[offer_id]
            self.assertEqual(
                (
                    offer["inputPerMillionTokensUsd"],
                    offer["cacheReadPerMillionTokensUsd"],
                    offer["outputPerMillionTokensUsd"],
                    offer["effectiveUsdPerMillionTokens"],
                ),
                rates,
            )
            self.assertFalse(offer["comparable"])
            self.assertEqual(offer["coverageMode"], "paid-plan-usage-credits")

    def test_anthropic_first_party_api_tiers_keep_published_fable_rates(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        offers = {offer["id"]: offer for offer in catalogue["offers"]}

        expected = {
            "anthropic-api-standard-fable-5": (10, 1, 50),
            "anthropic-api-batch-fable-5": (5, 0.5, 25),
            "anthropic-api-us-only-fable-5": (11, 1, 55),
        }
        for offer_id, rates in expected.items():
            offer = offers[offer_id]
            self.assertEqual(
                (
                    offer["inputPerMillionTokensUsd"],
                    offer["cacheReadPerMillionTokensUsd"],
                    offer["outputPerMillionTokensUsd"],
                ),
                rates,
            )
            self.assertTrue(offer["comparable"])
            self.assertEqual(offer["modelSlugs"], ["claude-fable-5"])

        api_provider = next(
            provider
            for provider in catalogue["providers"]
            if provider["id"] == "anthropic-api"
        )
        self.assertNotEqual(api_provider.get("importedFrom"), "models.dev")

    def test_cursor_plan_variants_encode_full_pool_rate_multipliers(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        cursor_templates = [
            offer
            for offer in catalogue["offers"]
            if offer["providerId"] == "cursor" and offer.get("planVariants")
        ]

        self.assertGreaterEqual(len(cursor_templates), 10)
        for offer in cursor_templates:
            variants = {variant["planId"]: variant for variant in offer["planVariants"]}
            self.assertAlmostEqual(variants["cursor-pro-plus"]["rateMultiplier"], 60 / 70)
            self.assertEqual(variants["cursor-ultra"]["rateMultiplier"], 0.5)

    def test_provider_pricing_zero_rates_are_published_not_missing_sentinels(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        plan_by_id = {plan["id"]: plan for plan in catalogue["plans"]}
        token_rate_offers = [
            offer
            for offer in catalogue["offers"]
            if offer["pricingKind"] in {"per-token", "effective-subscription"}
        ]

        for offer in token_rate_offers:
            plan = plan_by_id[offer["planId"]]
            currency = offer.get("currency") or plan.get("currency") or catalogue["currency"]
            input_rate = offer.get("inputPerMillionTokensUsd")
            output_rate = offer.get("outputPerMillionTokensUsd")
            cache_rate = offer.get("cacheReadPerMillionTokensUsd")
            if currency != "USD" and input_rate is None:
                input_rate = offer.get("inputPerMillionTokensLocal")
            if currency != "USD" and output_rate is None:
                output_rate = offer.get("outputPerMillionTokensLocal")
            if currency != "USD" and cache_rate is None:
                cache_rate = offer.get("cacheReadPerMillionTokensLocal")

            self.assertIsNotNone(input_rate)
            self.assertIsNotNone(output_rate)
            for rate in (input_rate, output_rate, cache_rate):
                if rate is None:
                    continue
                self.assertGreaterEqual(rate, 0)
                if rate == 0:
                    self.assertTrue(offer.get("publishedZeroRate"))
                    self.assertTrue(offer.get("sourceIds"))

        zero_cache_offer_ids = {
            offer["id"]
            for offer in token_rate_offers
            if offer.get("cacheReadPerMillionTokensUsd") == 0
            or offer.get("cacheReadPerMillionTokensLocal") == 0
        }
        # A numeric zero is retained only when the source catalogue publishes
        # a zero rate.  Unknown cache prices stay null and therefore cannot be
        # confused with a free cache read.
        for offer in token_rate_offers:
            if offer["id"] not in zero_cache_offer_ids:
                continue
            self.assertTrue(offer.get("sourceIds"))
            self.assertTrue(offer["comparable"])
            self.assertNotEqual(offer.get("importedFrom"), "models.dev")
        self.assertIsNone(
            next(
                offer
                for offer in token_rate_offers
                if offer["id"] == "or-qwen3-6-plus"
            )["cacheReadPerMillionTokensUsd"]
        )
        # A finite rate may intentionally be display-only (for example, a
        # paid-plan overage rate whose prerequisite subscription fee is not
        # folded into the token price). Non-comparable must therefore remain
        # independent from whether a rate is present.
        display_only = next(
            offer
            for offer in catalogue["offers"]
            if offer["id"] == "anthropic-pro-fable-5-usage-credits"
        )
        self.assertFalse(display_only["comparable"])
        self.assertGreater(display_only["inputPerMillionTokensUsd"], 0)
        self.assertGreater(display_only["outputPerMillionTokensUsd"], 0)

    def test_site_payload_exposes_provider_pricing_at_the_root(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        payload = build_site_payload(
            [{"model": "Pricing Fixture", "slug": "pricing-fixture"}],
            provider_pricing_data=catalogue,
        )

        self.assertIs(payload["providerPricing"], catalogue)
        self.assertEqual(payload["providerPricing"]["version"], 1)

    def test_generated_site_provider_pricing_matches_source_catalogue(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        generated = json.loads(DEFAULT_OUTPUT_JSON.read_text(encoding="utf-8"))

        self.assertEqual(generated["providerPricing"], catalogue)

    def test_coding_plan_prices_and_usage_fields_keep_their_native_terms(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        plans = {plan["id"]: plan for plan in catalogue["plans"]}

        self.assertEqual(plans["opencode-go"]["firstMonthPriceUsd"], 5)
        self.assertEqual(plans["cursor-pro-plus"]["includedApiSpendUsd"], 70)
        self.assertEqual(plans["github-copilot-pro-plus"]["includedAiCredits"], 7000)
        self.assertEqual(plans["kimi-code-moderato"]["currency"], "CNY")
        self.assertEqual(plans["kimi-code-moderato"]["monthlyPriceLocal"], 99)
        self.assertEqual(plans["minimax-ultra"]["currency"], "CNY")
        self.assertEqual(plans["minimax-ultra"]["monthlyPriceLocal"], 469)
        self.assertNotIn("includedTokensPerMonth", plans["minimax-ultra"])

    def test_minimax_current_plans_do_not_reuse_retired_fixed_token_quotas(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        plans = {
            plan["id"]: plan
            for plan in catalogue["plans"]
            if plan["providerId"] == "minimax"
        }
        expected = {
            "minimax-plus": 49,
            "minimax-max": 119,
            "minimax-ultra": 469,
        }
        self.assertEqual(set(plans), set(expected))
        for plan_id, monthly_price in expected.items():
            plan = plans[plan_id]
            self.assertEqual(plan["currency"], "CNY")
            self.assertEqual(plan["monthlyPriceLocal"], monthly_price)
            self.assertEqual(plan["comparisonClass"], "non-comparable")
            self.assertNotIn("includedTokensPerMonth", plan)

        offers = [
            offer
            for offer in catalogue["offers"]
            if offer["providerId"] == "minimax"
        ]
        self.assertEqual(len(offers), 9)
        self.assertEqual(
            {offer["modelSlugs"][0] for offer in offers},
            {"minimax-m3", "minimax-m2-7", "minimax-m2-5"},
        )
        for offer in offers:
            self.assertFalse(offer["comparable"])
            self.assertIsNone(offer["inputPerMillionTokensUsd"])
            self.assertIsNone(offer["cacheReadPerMillionTokensUsd"])
            self.assertIsNone(offer["outputPerMillionTokensUsd"])

    def test_google_cli_plans_keep_shared_request_quotas_non_comparable(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        plans = {plan["id"]: plan for plan in catalogue["plans"]}
        offers = [
            offer
            for offer in catalogue["offers"]
            if offer["providerId"] == "google-gemini-cli"
        ]

        self.assertEqual(plans["gemini-cli-free"]["maxRequestsPerUserPerDay"], 1_000)
        self.assertEqual(plans["gemini-cli-google-ai-pro"]["maxRequestsPerUserPerDay"], 1_500)
        self.assertEqual(plans["gemini-cli-google-ai-ultra"]["maxRequestsPerUserPerDay"], 2_000)
        self.assertIsNone(plans["gemini-cli-google-ai-pro"]["monthlyPriceUsd"])
        self.assertIsNone(plans["gemini-cli-google-ai-ultra"]["monthlyPriceUsd"])
        self.assertEqual(len(offers), 15)
        self.assertEqual(
            {offer["planId"] for offer in offers},
            {
                "gemini-cli-free",
                "gemini-cli-google-ai-pro",
                "gemini-cli-google-ai-ultra",
            },
        )
        for offer in offers:
            self.assertFalse(offer["comparable"])
            self.assertEqual(len(offer["modelSlugs"]), 1)
            self.assertNotIn("planVariants", offer)

    def test_baidu_token_plan_uses_exact_model_support_and_one_to_one_credits(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        plans = {
            plan["id"]: plan
            for plan in catalogue["plans"]
            if plan["providerId"] == "baidu-qianfan-token-plan"
        }
        expected = {
            "baidu-qianfan-token-plan-mini": (4.9, 10, 0.49),
            "baidu-qianfan-token-plan-lite": (19.9, 42, 19.9 / 42),
            "baidu-qianfan-token-plan-pro": (99.9, 230, 99.9 / 230),
            "baidu-qianfan-token-plan-max": (299.9, 700, 299.9 / 700),
        }
        self.assertEqual(set(plans), set(expected))
        for plan_id, (price, included_millions, effective) in expected.items():
            plan = plans[plan_id]
            self.assertEqual(plan["monthlyPriceLocal"], price)
            self.assertEqual(
                plan["includedMillionTokensPerSubscriptionMonth"],
                included_millions,
            )
            self.assertAlmostEqual(plan["effectiveUniformPerMillionTokensLocal"], effective)

        offers = [
            offer
            for offer in catalogue["offers"]
            if offer["providerId"] == "baidu-qianfan-token-plan"
        ]
        self.assertEqual(len(offers), 32)
        self.assertEqual(
            {offer["modelSlugs"][0] for offer in offers},
            {
                "deepseek-v4-pro",
                "deepseek-v4-pro-non-reasoning",
                "deepseek-v4-flash",
                "deepseek-v4-flash-non-reasoning",
                "glm-5-2",
                "glm-5-1",
                "kimi-k2-6",
                "kimi-k2-6-non-reasoning",
            },
        )
        for offer in offers:
            self.assertEqual(len(offer["modelSlugs"]), 1)
            self.assertTrue(offer["comparable"])
            plan_rate = plans[offer["planId"]]["effectiveUniformPerMillionTokensLocal"]
            self.assertAlmostEqual(offer["inputPerMillionTokensLocal"], plan_rate)
            self.assertAlmostEqual(offer["cacheReadPerMillionTokensLocal"], plan_rate)
            self.assertAlmostEqual(offer["outputPerMillionTokensLocal"], plan_rate)

    def test_baidu_qianfan_api_keeps_context_tiers_and_exact_batch_rows(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        offers = [
            offer
            for offer in catalogue["offers"]
            if offer["providerId"] == "baidu-qianfan-api"
        ]
        self.assertEqual(len(offers), 17)
        self.assertTrue(all(len(offer["modelSlugs"]) == 1 for offer in offers))
        self.assertTrue(all(offer["inputPerMillionTokensLocal"] > 0 for offer in offers))
        self.assertTrue(all(offer["outputPerMillionTokensLocal"] > 0 for offer in offers))

        batch = [offer for offer in offers if offer["planId"].endswith("batch-payg")]
        self.assertEqual(
            {offer["modelSlugs"][0] for offer in batch},
            {"deepseek-v3-2", "deepseek-v3-2-reasoning"},
        )
        glm = next(offer for offer in offers if offer["id"].endswith("payg-glm-5-1"))
        self.assertEqual(glm["pricingOverrides"][0]["minPromptTokens"], 32_000)
        qwen = next(offer for offer in offers if offer["id"].endswith("qwen3-5-397b-a17b"))
        self.assertEqual(qwen["pricingOverrides"][0]["minPromptTokens"], 128_000)

    def test_step_and_bigmodel_plans_apply_published_credit_formulas_per_model(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        plans = {plan["id"]: plan for plan in catalogue["plans"]}
        offers = {offer["id"]: offer for offer in catalogue["offers"]}

        step = offers["stepfun-step-plan-mini-monthly-step-3-7-flash"]
        self.assertEqual(step["modelSlugs"], ["step-3-7-flash"])
        self.assertAlmostEqual(step["inputPerMillionTokensLocal"], 1.35 * 49 / 400)
        self.assertAlmostEqual(step["cacheReadPerMillionTokensLocal"], 0.27 * 49 / 400)
        self.assertAlmostEqual(step["outputPerMillionTokensLocal"], 8.1 * 49 / 400)
        self.assertTrue(step["comparable"])
        self.assertEqual(
            plans["stepfun-step-plan-max-annual"]["annualEquivalentMonthlyLocal"],
            555.5,
        )

        bigmodel = offers["bigmodel-coding-lite-monthly-glm-5-2"]
        monthly_points = 10_000 * 52 / 12
        self.assertAlmostEqual(bigmodel["inputPerMillionTokensLocal"], 118 / monthly_points * 690)
        self.assertAlmostEqual(bigmodel["cacheReadPerMillionTokensLocal"], 118 / monthly_points * 170)
        self.assertAlmostEqual(bigmodel["outputPerMillionTokensLocal"], 118 / monthly_points * 2_400)
        self.assertEqual(bigmodel["offPeakCreditMultiplier"], 0.5)
        self.assertTrue(bigmodel["comparable"])

    def test_china_official_api_rates_preserve_local_currency_and_thresholds(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        plans = {plan["id"]: plan for plan in catalogue["plans"]}
        offers = {offer["id"]: offer for offer in catalogue["offers"]}

        bailian = offers["bailian-cn-qwen3-8-max"]
        self.assertEqual(plans[bailian["planId"]]["currency"], "CNY")
        self.assertEqual(bailian["modelSlugs"], ["qwen3-8-max"])
        self.assertEqual(bailian["inputPerMillionTokensLocal"], 12)
        self.assertEqual(bailian["outputPerMillionTokensLocal"], 36)

        deepseek = offers["deepseek-api-v4-flash"]
        self.assertEqual(
            (
                deepseek["inputPerMillionTokensUsd"],
                deepseek["cacheReadPerMillionTokensUsd"],
                deepseek["outputPerMillionTokensUsd"],
            ),
            (0.14, 0.0028, 0.28),
        )

        kimi_batch = offers["kimi-cn-batch-k2-7-code"]
        self.assertEqual(kimi_batch["modelSlugs"], ["kimi-k2-7-code"])
        self.assertEqual(kimi_batch["inputPerMillionTokensLocal"], 3.9)
        self.assertEqual(kimi_batch["cacheReadPerMillionTokensLocal"], 0.78)
        self.assertEqual(kimi_batch["outputPerMillionTokensLocal"], 16.2)

        minimax = offers["minimax-cn-m3"]
        override = minimax["pricingOverrides"][0]
        self.assertEqual(override["minPromptTokens"], 512_001)
        self.assertEqual(override["inputPerMillionTokensLocal"], 4.2)
        self.assertEqual(override["cacheReadPerMillionTokensLocal"], 0.84)
        self.assertEqual(override["outputPerMillionTokensLocal"], 16.8)

        self.assertEqual(
            offers["minimax-cn-m2-7"]["cacheWritePerMillionTokensLocal"],
            2.625,
        )
        self.assertEqual(
            offers["volcengine-ark-cn-deepseek-v4-pro"]["modelSlugs"],
            ["deepseek-v4-pro"],
        )

    @staticmethod
    def benchmark_lab_frontier_preset():
        """Legacy board calculator retained only inside the Custom benchmark lab."""

        return {
            "kind": "frontier-groups",
            "calculation": "geometric",
            "normalization": "relative-best",
            "missingPolicy": "weak-prior",
            "weakPriorRatio": 0.34,
            "groupMetricCoverageDiscountExponent": 0.10,
            "singleMetricCoverageDiscountExponent": 0.10,
            "groups": AINDEX_GROUPS,
        }

    def test_generated_site_attaches_consensus_only_to_selected_exact_configs(self):
        payload = json.loads(DEFAULT_OUTPUT_JSON.read_text(encoding="utf-8"))
        ranked = [model for model in payload["models"] if model.get("rankingProfile")]
        ranked.sort(key=lambda model: model["rankingProfile"]["publicationRank"])

        self.assertEqual(len(ranked), payload["leaderboard"]["populationSize"])
        self.assertGreaterEqual(len(ranked), 50)
        self.assertEqual(ranked[0]["slug"], "claude-fable-5")
        self.assertEqual(ranked[1]["slug"], "gpt-5-6-sol")
        self.assertEqual(
            [model["rankingProfile"]["publicationRank"] for model in ranked],
            list(range(1, len(ranked) + 1)),
        )
        self.assertEqual(
            [model["rankingProfile"]["displayScore"] for model in ranked],
            sorted(
                (model["rankingProfile"]["displayScore"] for model in ranked),
                reverse=True,
            ),
        )
        self.assertNotIn("publicationOrderRule", payload["leaderboard"])

        for model in ranked:
            profile = model["rankingProfile"]
            methods = profile["methods"]
            self.assertEqual(profile["publicationRank"], profile["evidenceRank"])
            self.assertNotIn("publicationOrderRule", profile)
            self.assertNotIn("requiredOrderTarget", profile)
            self.assertNotIn("rankChangeDueToRequiredOrder", profile)
            self.assertGreaterEqual(profile["displayScore"], 0)
            self.assertLessEqual(profile["displayScore"], 100)
            self.assertAlmostEqual(
                profile["displayScore"],
                profile["finalScore"],
                delta=0.00006,
            )
            self.assertTrue(profile["coreComplete"])
            self.assertEqual(profile["candidateId"], payload["leaderboard"]["candidateId"])
            self.assertEqual(
                float(profile["scoreFullPrecision"]),
                profile["finalScore"],
            )
            self.assertGreaterEqual(profile["bonusCap"], 0)
            self.assertAlmostEqual(
                profile["finalScore"],
                sum(board["points"] for board in profile["boards"].values()),
                delta=1e-10,
            )
            self.assertIn("twopl", methods)
            self.assertIn("denseRasch", methods)
            self.assertEqual(methods["twopl"]["role"], "audit-and-sensitivity-only")
            self.assertEqual(methods["denseRasch"]["role"], "audit-and-sensitivity-only")
            extension_coverages = []
            for board_id, board in profile["boards"].items():
                self.assertAlmostEqual(
                    board["score"],
                    min(100, board["coreScore"] + board["extensionBonus"]),
                    delta=2e-6,
                )
                self.assertGreaterEqual(board["extensionBonus"], 0)
                self.assertLessEqual(
                    board["extensionBonus"],
                    profile["bonusCap"] + 1e-6,
                )
                self.assertEqual(board["coreTests"], board["coreItemPoolSize"])
                extension_coverages.append(board["extensionCoverageScore"])
            self.assertAlmostEqual(
                profile["extensionCoverageScore"],
                sum(extension_coverages) / len(extension_coverages),
                delta=0.0006,
            )
            self.assertEqual(
                profile["evidenceCoverageScore"],
                profile["extensionCoverageScore"],
            )

        selected_slugs = {model["slug"] for model in ranked}
        by_slug = {model["slug"]: model for model in payload["models"]}
        self.assertIn("rankingProfile", by_slug["gpt-5-5"])
        self.assertNotIn("rankingProfile", by_slug["gpt-5-5-high"])
        for model in payload["models"]:
            if model["slug"] not in selected_slugs:
                self.assertNotIn("rankingProfile", model)

    def test_generated_site_exposes_independent_exact_config_profiles(self):
        payload = json.loads(DEFAULT_OUTPUT_JSON.read_text(encoding="utf-8"))
        exact_ranked = [
            model
            for model in payload["models"]
            if model.get("exactRankingProfile")
        ]
        exact_ranked.sort(
            key=lambda model: model["exactRankingProfile"]["publicationRank"]
        )

        self.assertEqual(
            len(exact_ranked),
            payload["leaderboard"]["exactPopulationSize"],
        )
        self.assertGreater(
            len(exact_ranked),
            payload["leaderboard"]["populationSize"],
        )
        self.assertEqual(
            [
                model["exactRankingProfile"]["publicationRank"]
                for model in exact_ranked
            ],
            list(range(1, len(exact_ranked) + 1)),
        )
        self.assertEqual(
            [model["exactRankingProfile"]["displayScore"] for model in exact_ranked],
            sorted(
                (
                    model["exactRankingProfile"]["displayScore"]
                    for model in exact_ranked
                ),
                reverse=True,
            ),
        )
        self.assertTrue(
            all(
                model["exactRankingProfile"]["rankingGrain"] == "exact_config"
                for model in exact_ranked
            )
        )

        by_slug = {model["slug"]: model for model in payload["models"]}
        expected_gpt55 = {
            "gpt-5-5",
            "gpt-5-5-high",
            "gpt-5-5-medium",
            "gpt-5-5-low",
            "gpt-5-5-non-reasoning",
        }

        self.assertTrue(
            all(by_slug[slug].get("exactRankingProfile") for slug in expected_gpt55)
        )
        self.assertNotIn(
            "exactRankingProfile",
            by_slug["gpt-5-5-instant-05-26"],
        )
        self.assertLess(
            by_slug["gpt-5-5"]["exactRankingProfile"]["publicationRank"],
            by_slug["gpt-5-5-high"]["exactRankingProfile"]["publicationRank"],
        )
        self.assertGreater(
            by_slug["gpt-5-5"]["exactRankingProfile"]["displayScore"],
            by_slug["gpt-5-5-high"]["exactRankingProfile"]["displayScore"],
        )
        self.assertNotEqual(
            payload["leaderboard"]["boardItemPoolSizesByMethod"],
            payload["leaderboard"]["exactBoardItemPoolSizesByMethod"],
        )
        self.assertEqual(
            {row["slug"] for row in payload["leaderboard"]["exactRows"]},
            {model["slug"] for model in exact_ranked},
        )

    def test_primary_contract_is_score_ordered_without_named_rank_override(self):
        root = Path(__file__).resolve().parents[1]
        readme = (root / "README.md").read_text(encoding="utf-8")
        methodology = (root / "docs" / "methodology.html").read_text(
            encoding="utf-8"
        )
        full_rank = (root / "docs" / "full-rank.html").read_text(
            encoding="utf-8"
        )
        analysis_readme = (
            root / "analysis" / "irt_leaderboard_exploration" / "README.md"
        ).read_text(encoding="utf-8")
        current_analysis = analysis_readme.split("## 历史五套实验", 1)[0]

        self.assertEqual(PRIMARY_RANKING_METHOD, "aindex_scheme18")
        for text in (readme, methodology, current_analysis):
            self.assertNotIn("发布层", text)
            self.assertNotIn("reserves rank 1", text)
        self.assertIn("Scheme 18", methodology)
        self.assertIn("positive residual", methodology)
        self.assertIn("dynamic cap", methodology.lower())
        self.assertIn("0–100", methodology)
        self.assertIn("sensitivity", methodology.lower())
        self.assertNotIn("Claude Fable 5", methodology)
        self.assertNotIn("GPT-5.6 Sol", methodology)

    def test_composite_score_sort_ignores_legacy_named_publication_order(self):
        consensus_rows = [
            {
                "slug": "claude-fable-5",
                "variant_group": "fable",
                "rank": 1,
                "score": 100,
                "publication_order_rule": "legacy-anchor",
                "required_order_target": "fable",
                "rank_change_due_to_required_order": 8,
            },
            {
                "slug": "gpt-5-6-sol",
                "variant_group": "sol",
                "rank": 2,
                "score": 99,
            },
            {
                "slug": "claude-opus-5",
                "variant_group": "opus",
                "rank": 3,
                "score": 98,
            },
        ]
        components = {
            "twopl": {
                "fable": {"score": 90.0},
                "sol": {"score": 92.5},
                "opus": {"score": 96.0},
            },
            "sparseRasch": {
                "fable": {"score": 100.0},
                "sol": {"score": 90.0},
                "opus": {"score": 95.0},
            },
        }

        ranked = _rank_consensus_rows_by_composite_score(
            consensus_rows,
            components,
            identity_field="variant_group",
        )

        self.assertEqual(
            [row["slug"] for row in ranked],
            ["claude-opus-5", "claude-fable-5", "gpt-5-6-sol"],
        )
        self.assertEqual([row["rank"] for row in ranked], [1, 2, 3])
        self.assertEqual([row["score"] for row in ranked], [95.8, 92.0, 92.0])
        self.assertTrue(
            all(
                row["rank_tie_break_policy"]
                == "higher_unrounded_score_then_stable_id"
                for row in ranked
            )
        )
        for row in ranked:
            self.assertNotIn("publication_order_rule", row)
            self.assertNotIn("required_order_target", row)
            self.assertNotIn("rank_change_due_to_required_order", row)

    def test_grok45_official_scores_attach_to_high_variant(self):
        payload = build_site_payload(
            read_csv_rows(DEFAULT_INPUT_CSV),
            load_external_benchmarks(DEFAULT_EXTERNAL_BENCHMARKS_JSON),
        )
        grok = next(model for model in payload["models"] if model["model"] == "Grok 4.5 (high)")

        self.assertEqual(grok["scores"]["benchmark:deepswe"], 62.0)
        self.assertEqual(grok["scores"]["benchmark:deepswe-v1-1"], 53.0)
        self.assertEqual(grok["scores"]["benchmark:swe-marathon"], 29.0)
        self.assertEqual(grok["scores"]["benchmark:terminal-bench-2-1"], 83.3)
        self.assertEqual(grok["scores"]["benchmark:swe-bench-pro"], 64.7)
        self.assertEqual(len(grok["externalBenchmarks"]), 5)
        self.assertEqual(
            {row["sourceId"] for row in grok["externalBenchmarks"]},
            {"spacexai-grok-4-5-release"},
        )

    def test_opus5_max_effort_scores_do_not_broadcast_to_lower_effort_variants(self):
        payload = build_site_payload(
            read_csv_rows(DEFAULT_INPUT_CSV),
            load_external_benchmarks(DEFAULT_EXTERNAL_BENCHMARKS_JSON),
        )
        opus_max = next(
            model for model in payload["models"] if model["model"] == "Claude Opus 5 (max)"
        )
        opus_low = next(
            model for model in payload["models"] if model["model"] == "Claude Opus 5 (low)"
        )

        self.assertEqual(opus_max["scores"]["benchmark:swe-bench-pro"], 79.2)
        self.assertIsNone(opus_low["scores"]["benchmark:swe-bench-pro"])
        self.assertTrue(
            next(
                row
                for row in opus_max["externalBenchmarks"]
                if row["metricKey"] == "benchmark:swe-bench-pro"
            )["variantScoped"]
        )

    def test_gpt56_release_scores_attach_only_to_max_variants(self):
        payload = build_site_payload(
            read_csv_rows(DEFAULT_INPUT_CSV),
            load_external_benchmarks(DEFAULT_EXTERNAL_BENCHMARKS_JSON),
        )
        sol_max = next(
            model for model in payload["models"] if model["model"] == "GPT-5.6 Sol (max)"
        )
        sol_xhigh = next(
            model
            for model in payload["models"]
            if model["model"] == "GPT-5.6 Sol (xhigh)"
        )

        self.assertEqual(sol_max["scores"]["benchmark:swe-bench-pro"], 64.6)
        self.assertIsNone(sol_xhigh["scores"]["benchmark:swe-bench-pro"])
        swe_row = next(
            row
            for row in sol_max["externalBenchmarks"]
            if row["metricKey"] == "benchmark:swe-bench-pro"
        )
        self.assertTrue(swe_row["variantScoped"])
        self.assertEqual(swe_row["effort"], "max")
        self.assertEqual(swe_row["configurationConfidence"], "inferred")

    def test_fable_system_card_replaces_unattributed_higher_of_two_rows(self):
        payload = build_site_payload(
            read_csv_rows(DEFAULT_INPUT_CSV),
            load_external_benchmarks(DEFAULT_EXTERNAL_BENCHMARKS_JSON),
        )
        fable = next(
            model
            for model in payload["models"]
            if model["model"] == "Claude Fable 5 (with fallback)"
        )

        self.assertEqual(fable["scores"]["benchmark:swe-bench-pro"], 80.0)
        self.assertEqual(fable["scores"]["benchmark:terminal-bench-2-1"], 84.3)
        self.assertNotIn(
            "anthropic-claude-fable-5-docs",
            {row["sourceId"] for row in fable["externalBenchmarks"]},
        )
        terminal_row = next(
            row
            for row in fable["externalBenchmarks"]
            if row["metricKey"] == "benchmark:terminal-bench-2-1"
        )
        self.assertEqual(terminal_row["sourceId"], "anthropic-claude-fable-5-system-card")
        self.assertTrue(terminal_row["variantScoped"])
        self.assertTrue(terminal_row["composite"])
        self.assertTrue(terminal_row["fallbackObserved"])
        self.assertEqual(terminal_row["fallbackRate"], 0.209)
        self.assertTrue(terminal_row["productEvidenceEligible"])
        self.assertFalse(terminal_row["pureModelEligible"])

    def test_opus5_release_effort_and_fallback_scores_are_isolated(self):
        payload = build_site_payload(
            read_csv_rows(DEFAULT_INPUT_CSV),
            load_external_benchmarks(DEFAULT_EXTERNAL_BENCHMARKS_JSON),
        )
        opus_high = next(
            model for model in payload["models"] if model["model"] == "Claude Opus 5 (high)"
        )
        opus_max = next(
            model for model in payload["models"] if model["model"] == "Claude Opus 5 (max)"
        )

        high_release_rows = [
            row
            for row in opus_high["externalBenchmarks"]
            if row["sourceId"] == "anthropic-claude-opus-5-release"
            and not row.get("sharedFromVariant")
        ]
        max_release_rows = [
            row
            for row in opus_max["externalBenchmarks"]
            if row["sourceId"] == "anthropic-claude-opus-5-release"
        ]
        self.assertEqual(
            [(row["benchmarkId"], row["effort"]) for row in high_release_rows],
            [("arc-agi-3", "high")],
        )
        self.assertEqual(max_release_rows, [])

    def test_default_ainsights_terminal_bench_uses_aa_column_not_duplicate_external_versions(self):
        group_metrics = {
            group["id"]: [metric["key"] for metric in group["metrics"]]
            for group in AINDEX_GROUPS
        }

        self.assertIn("Terminal-Bench v2.1", group_metrics["coding"])
        self.assertIn("Terminal-Bench v2.1", group_metrics["agentic-tool-work"])
        self.assertNotIn("benchmark:terminal-bench-2", group_metrics["coding"])
        self.assertNotIn("benchmark:terminal-bench-2-1", group_metrics["coding"])
        self.assertNotIn("benchmark:terminal-bench-2", group_metrics["agentic-tool-work"])
        self.assertNotIn("benchmark:terminal-bench-2-1", group_metrics["agentic-tool-work"])
        self.assertEqual(DEFAULT_AINDEX_WEIGHTS.get("benchmark:terminal-bench-2", 0), 0)
        self.assertEqual(DEFAULT_AINDEX_WEIGHTS.get("benchmark:terminal-bench-2-1", 0), 0)

    def test_default_ainsights_uses_external_livecodebench_only_as_fallback_source(self):
        group_metrics = {
            group["id"]: [metric["key"] for metric in group["metrics"]]
            for group in AINDEX_GROUPS
        }

        self.assertIn("LiveCodeBench", group_metrics["coding"])
        self.assertNotIn("benchmark:livecodebench", group_metrics["coding"])
        self.assertEqual(DEFAULT_AINDEX_WEIGHTS.get("benchmark:livecodebench", 0), 0)

    def test_advanced_benchmark_profile_excludes_metrics_with_fewer_than_four_models(self):
        payload = build_site_payload(
            read_csv_rows(DEFAULT_INPUT_CSV),
            load_external_benchmarks(DEFAULT_EXTERNAL_BENCHMARKS_JSON),
        )
        selected_keys = {
            metric["key"]
            for group in AINDEX_GROUPS
            for metric in group["metrics"]
        }

        sparse_metrics = []
        for key in sorted(selected_keys):
            coverage = sum(
                1
                for model in payload["models"]
                if model.get("scores", {}).get(key) is not None
            )
            if coverage < 4:
                sparse_metrics.append((key, coverage))

        self.assertEqual([], sparse_metrics)
        self.assertNotIn("benchmark:frontiercode-diamond", selected_keys)
        self.assertNotIn("benchmark:kimi-code-bench-v2", selected_keys)
        self.assertNotIn("benchmark:programbench", selected_keys)
        self.assertNotIn("benchmark:livecodebench-pro-elo", selected_keys)
        self.assertNotIn("benchmark:arc-agi-2", selected_keys)

    def test_default_ainsights_uses_aa_ifbench_not_duplicate_external_version(self):
        group_metrics = {
            group["id"]: [metric["key"] for metric in group["metrics"]]
            for group in AINDEX_GROUPS
        }

        self.assertIn("IFBench", group_metrics["instruction-context"])
        self.assertNotIn("benchmark:ifbench", group_metrics["instruction-context"])
        self.assertEqual(DEFAULT_AINDEX_WEIGHTS.get("benchmark:ifbench", 0), 0)

    def test_default_ainsights_group_metrics_are_ordered_by_internal_weight(self):
        for group in AINDEX_GROUPS:
            weights = [metric["weight"] for metric in group["metrics"]]
            self.assertEqual(
                weights,
                sorted(weights, reverse=True),
                f"{group['id']} metrics should be listed from highest to lowest weight",
            )

    def test_variant_group_removes_common_strength_suffixes(self):
        self.assertEqual(variant_group("GPT-5.5 (xhigh)", "gpt-5-5"), "gpt 5 5")
        self.assertEqual(variant_group("Claude Opus 4.8 (max)", "claude-opus-4-8"), "claude opus 4 8")
        self.assertEqual(variant_group("GPT-5.5 (Non-reasoning)", "gpt-5-5-non-reasoning"), "gpt 5 5")
        self.assertEqual(variant_group("Claude Opus 4.7 (Non-reasoning, high)", "claude-opus-4-7-non-reasoning"), "claude opus 4 7")
        self.assertEqual(variant_group("Gemini 3.5 Flash (minimal)", "gemini-3-5-flash-minimal"), "gemini 3 5 flash")

    def test_variant_priority_prefers_stronger_inference_presets(self):
        self.assertGreater(variant_priority("GPT-5.5 (xhigh)", "gpt-5-5-xhigh"), variant_priority("GPT-5.5 (high)", "gpt-5-5-high"))
        self.assertGreater(variant_priority("GPT-5.5 (high)", "gpt-5-5-high"), variant_priority("GPT-5.5", "gpt-5-5"))
        self.assertGreater(variant_priority("Claude Opus 4.8 (max)", "claude-opus-4-8-max"), variant_priority("Claude Opus 4.8 (xhigh)", "claude-opus-4-8-xhigh"))
        self.assertLess(variant_priority("Claude Opus 4.7 (Non-reasoning, high)", "claude-opus-4-7-non-reasoning"), variant_priority("Claude Opus 4.7", "claude-opus-4-7"))

    def test_opus_non_reasoning_tier_dedupes_with_reasoning_tier(self):
        payload = build_site_payload(read_csv_rows(DEFAULT_INPUT_CSV))
        opus_max = next(model for model in payload["models"] if model["modelKey"] == "Claude Opus 4.7 (max) [R]")
        opus_non_reasoning = next(model for model in payload["models"] if model["modelKey"] == "Claude Opus 4.7 (Non-reasoning, high)")

        self.assertEqual(opus_max["variantGroup"], "claude opus 4 7")
        self.assertEqual(opus_non_reasoning["variantGroup"], opus_max["variantGroup"])
        self.assertLess(opus_non_reasoning["variantPriority"], opus_max["variantPriority"])

    def test_build_site_payload_includes_presets_metrics_and_model_groups(self):
        rows = [
            {
                "model_key": "Model A (high) [R]",
                "model": "Model A (high)",
                "is_reasoning": "true",
                "slug": "model-a-high",
                "creator": "Lab A",
                "input_modality_text": "true",
                "input_modality_image": "true",
                "input_modality_speech": "false",
                "input_modality_video": "",
                "output_modality_text": "true",
                "output_modality_image": "false",
                "output_modality_speech": "false",
                "output_modality_video": "false",
                "context_window_tokens": "128000",
                "median_output_speed": "123.4",
                "Input Price Per 1M Tokens (USD)": "1.25",
                "Output Price Per 1M Tokens (USD)": "5",
                "Cache Hit Price Per 1M Tokens (USD)": "0.5",
                "AA Intelligence Index Cost (USD)": "42.25",
                "AA Intelligence Index Input Cost (USD)": "12.25",
                "AA Intelligence Index Output Cost (USD)": "30",
                "AA Intelligence Index": "50",
                "AA Coding Index": "60",
                "AA Agentic Index": "70",
                "GDPval-AA v2": "80",
                "Terminal-Bench v2.1": "40",
            },
            {
                "model_key": "Model A (low) [R]",
                "model": "Model A (low)",
                "is_reasoning": "true",
                "slug": "model-a-low",
                "creator": "Lab A",
                "AA Intelligence Index": "45",
                "AA Coding Index": "55",
                "AA Agentic Index": "65",
                "GDPval-AA v2": "60",
                "Terminal-Bench v2.1": "20",
            },
        ]

        payload = build_site_payload(rows)

        self.assertEqual(payload["models"][0]["variantGroup"], "model a")
        self.assertEqual(payload["models"][1]["variantGroup"], "model a")
        self.assertIn("zhihu-adjusted", payload["presets"])
        self.assertIn("aa-intelligence", payload["presets"])
        self.assertIn("aa-coding", payload["presets"])
        self.assertIn("aa-agentic", payload["presets"])
        self.assertGreaterEqual(len(payload["externalSources"]), 5)
        self.assertEqual(payload["externalSources"][0]["id"], "artificial-analysis")
        self.assertIn("url", payload["externalSources"][0])
        self.assertEqual(payload["externalSources"][0]["defaultWeight"], 100)
        self.assertEqual(payload["externalSources"][0]["scoreStatus"], "active")
        self.assertIn("GDPval-AA v2", payload["externalSources"][0]["relatedMetrics"])
        self.assertIn("relatedMetrics", payload["externalSources"][1])
        self.assertEqual(payload["defaultPreset"], "zhihu-adjusted")
        self.assertIn("GDPval-AA v2", [metric["key"] for metric in payload["metrics"]])
        self.assertEqual(payload["presets"]["zhihu-adjusted"]["kind"], "precomputed-ranking")
        self.assertEqual(payload["presets"]["zhihu-adjusted"]["label"], "AInsights Index")
        self.assertEqual(
            payload["presets"]["zhihu-adjusted"]["calculation"],
            "geometric-core-positive-residual-logsumexp",
        )
        self.assertEqual(payload["presets"]["zhihu-adjusted"]["normalization"], "none")
        self.assertEqual(
            payload["presets"]["zhihu-adjusted"]["missingPolicy"],
            "core-required-extension-absent",
        )
        self.assertEqual(
            payload["presets"]["zhihu-adjusted"]["candidateId"],
            "v5_partial_credit_geometric_logsumexp_residual_t1_independent_audit_mean_plus_sqrt2_sd",
        )
        self.assertNotIn("componentMethods", payload["presets"]["zhihu-adjusted"])
        self.assertNotIn("componentWeights", payload["presets"]["zhihu-adjusted"])
        metrics_by_key = {metric["key"]: metric for metric in payload["metrics"]}
        self.assertEqual(metrics_by_key["SciCode"]["aindexRole"], "core")
        self.assertEqual(
            metrics_by_key["Terminal-Bench v2.1"]["aindexRole"],
            "extension",
        )
        self.assertEqual(metrics_by_key["GDPval-AA v2"]["aindexRole"], "excluded")
        for field in (
            "aindexBoards",
            "benchmarkController",
            "resultOperator",
            "resultProtocol",
            "scoreProvenance",
            "versionPin",
            "onlyAdd",
            "scoringReason",
            "protocolStatus",
        ):
            self.assertIn(field, metrics_by_key["Terminal-Bench v2.1"])
        self.assertNotIn("groups", payload["presets"]["zhihu-adjusted"])
        self.assertNotIn("weights", payload["presets"]["zhihu-adjusted"])
        self.assertNotIn("displayScale", payload["presets"]["zhihu-adjusted"])
        self.assertEqual(payload["presets"]["custom"]["normalization"], "relative-best")
        self.assertEqual(payload["metricBaselines"]["GDPval-AA v2"], 80)
        self.assertEqual(payload["scoreBaselines"]["aaIntelligenceMax"], 50)
        self.assertGreater(payload["models"][0]["variantPriority"], payload["models"][1]["variantPriority"])
        self.assertEqual(payload["models"][0]["contextWindowTokens"], 128000)
        self.assertEqual(payload["models"][0]["inputModalities"], ["Text", "Image"])
        self.assertEqual(payload["models"][0]["outputModalities"], ["Text"])
        self.assertEqual(payload["models"][0]["modelDetails"]["modalities"]["input"]["image"], True)
        self.assertEqual(payload["models"][0]["modelDetails"]["modalities"]["output"]["video"], False)
        self.assertEqual(payload["models"][0]["medianOutputSpeed"], 123.4)
        self.assertEqual(payload["models"][0]["pricing"]["inputPerMillionTokensUsd"], 1.25)
        self.assertEqual(payload["models"][0]["pricing"]["outputPerMillionTokensUsd"], 5)
        self.assertEqual(payload["models"][0]["pricing"]["cacheHitPerMillionTokensUsd"], 0.5)
        self.assertEqual(payload["models"][0]["pricing"]["aaIndexCostUsd"], 42.25)
        self.assertEqual(payload["models"][0]["pricing"]["aaIndexInputCostUsd"], 12.25)
        self.assertEqual(payload["models"][0]["pricing"]["aaIndexOutputCostUsd"], 30)

    def test_build_site_payload_adds_aa_logo_icons_and_source_types(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "Open Model",
                    "model": "Open Model",
                    "is_reasoning": "false",
                    "slug": "open-model",
                    "creator": "OpenAI",
                    "open_source_categorization": "Open Weights (Permissive License)",
                    "AA Intelligence Index": "50",
                },
                {
                    "model_key": "Closed Model",
                    "model": "Closed Model",
                    "is_reasoning": "false",
                    "slug": "closed-model",
                    "creator": "Lab B",
                    "open_source_categorization": "Proprietary",
                    "AA Intelligence Index": "40",
                },
                {
                    "model_key": "Unknown Model",
                    "model": "Unknown Model",
                    "is_reasoning": "false",
                    "slug": "unknown-model",
                    "creator": "",
                    "AA Intelligence Index": "30",
                },
            ]
        )

        self.assertEqual(payload["models"][0]["openSourceType"], "open")
        self.assertEqual(payload["models"][1]["openSourceType"], "closed")
        self.assertEqual(payload["models"][2]["openSourceType"], "unknown")
        self.assertEqual(payload["models"][0]["modelIcon"]["src"], "assets/logos/openai_small.svg")
        self.assertEqual(payload["models"][0]["modelIcon"]["title"], "OpenAI")
        self.assertEqual(payload["models"][0]["modelIcon"]["fallbackLabel"], "OAI")
        self.assertEqual(payload["models"][1]["modelIcon"]["src"], "assets/logos/lab-b_small.svg")
        self.assertNotIn("sourceSrc", payload["models"][0]["modelIcon"])
        self.assertEqual(payload["models"][1]["modelIcon"]["label"], "LB")
        self.assertEqual(payload["models"][1]["modelIcon"]["fallbackLabel"], "LB")

    def test_open_source_type_supports_current_and_legacy_categories(self):
        expectations = {
            "permissive": "open",
            "commercial-license": "open",
            "Open Weights (Permissive License)": "open",
            "Proprietary": "closed",
            "closed": "closed",
            "": "unknown",
            "future-category": "unknown",
        }

        for category, expected in expectations.items():
            with self.subTest(category=category):
                self.assertEqual(open_source_type(category), expected)

    def test_build_site_payload_merges_external_benchmark_scores(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "GPT-5.5 (xhigh) [R]",
                    "model": "GPT-5.5 (xhigh)",
                    "is_reasoning": "true",
                    "slug": "gpt-5-5",
                    "creator": "OpenAI",
                    "creator_logo_small_url": "https://artificialanalysis.ai/img/logos/openai_small.svg",
                    "creator_color": "#1f1f1f",
                    "AA Intelligence Index": "60",
                }
            ],
            {
                "version": 1,
                "sources": [
                    {
                        "id": "official-release",
                        "label": "Official release evals",
                        "url": "https://example.com/evals",
                        "category": "Official",
                    }
                ],
                "benchmarks": [
                    {
                        "id": "terminal-bench-2",
                        "label": "Terminal-Bench 2.0",
                        "category": "Agentic coding",
                        "unit": "%",
                        "icon": "TERM",
                    }
                ],
                "results": [
                    {
                        "benchmarkId": "terminal-bench-2",
                        "benchmarkLabel": "Terminal-Bench 2.0",
                        "model": "GPT-5.5",
                        "modelAliases": ["GPT-5.5 (xhigh)", "gpt-5-5"],
                        "value": 82.7,
                        "unit": "%",
                        "sourceId": "official-release",
                        "sourceUrl": "https://example.com/evals",
                        "sourceLabel": "Official release evals",
                    }
                ],
            },
        )

        model = payload["models"][0]
        self.assertIn("benchmark:terminal-bench-2", [metric["key"] for metric in payload["metrics"]])
        self.assertEqual(model["scores"]["benchmark:terminal-bench-2"], 82.7)
        self.assertEqual(model["externalBenchmarks"][0]["label"], "Terminal-Bench 2.0")
        self.assertEqual(model["modelIcon"]["src"], "assets/logos/openai_small.svg")
        self.assertEqual(model["modelIcon"]["color"], "#1f1f1f")
        self.assertEqual(payload["externalSources"][-1]["scoreStatus"], "benchmark")
        self.assertIn("benchmark:terminal-bench-2", payload["externalSources"][-1]["relatedMetrics"])

    def test_first_party_score_beats_later_vendor_comparator(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "Claude Fable 5",
                    "model": "Claude Fable 5 (with fallback)",
                    "slug": "claude-fable-5",
                    "creator": "Anthropic",
                    "AA Intelligence Index": "60",
                }
            ],
            {
                "version": 1,
                "sources": [
                    {
                        "id": "anthropic-fable",
                        "category": "Official release",
                        "modelAliases": ["Claude Fable 5", "claude-fable-5"],
                    },
                    {
                        "id": "competitor-release",
                        "category": "Official release",
                        "modelAliases": ["Competitor Model"],
                    },
                ],
                "benchmarks": [{"id": "hle", "label": "HLE"}],
                "results": [
                    {
                        "benchmarkId": "hle",
                        "model": "Claude Fable 5",
                        "modelAliases": ["Claude Fable 5", "claude-fable-5"],
                        "value": 59.0,
                        "sourceId": "anthropic-fable",
                    },
                    {
                        "benchmarkId": "hle",
                        "model": "Claude Fable 5",
                        "modelAliases": ["Claude Fable 5", "claude-fable-5"],
                        "value": 53.3,
                        "sourceId": "competitor-release",
                    },
                ],
            },
        )

        model = payload["models"][0]
        self.assertEqual(model["scores"]["benchmark:hle"], 59.0)
        self.assertEqual(len(model["externalBenchmarks"]), 1)
        self.assertEqual(model["externalBenchmarks"][0]["sourceId"], "anthropic-fable")

    def test_external_benchmark_matching_keeps_deepseek_0731_separate_from_0424(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "DeepSeek V4 Flash 0731 (max) [R]",
                    "model": "DeepSeek V4 Flash 0731 (max)",
                    "is_reasoning": "true",
                    "slug": "deepseek-v4-flash",
                    "creator": "DeepSeek",
                    "AA Intelligence Index": "60",
                },
                {
                    "model_key": "DeepSeek V4 Flash",
                    "model": "DeepSeek V4 Flash",
                    "is_reasoning": "false",
                    "slug": "deepseek-v4-flash-non-reasoning",
                    "creator": "DeepSeek",
                    "AA Intelligence Index": "50",
                },
            ],
            {
                "version": 1,
                "sources": [],
                "benchmarks": [
                    {"id": "old-0424", "label": "Old 0424", "category": "General"},
                    {"id": "new-0731", "label": "New 0731", "category": "Agentic"},
                ],
                "results": [
                    {
                        "benchmarkId": "old-0424",
                        "model": "DeepSeek V4 Flash",
                        "modelAliases": ["DeepSeek V4 Flash", "deepseek-v4-flash-non-reasoning"],
                        "value": 83.0,
                        "sourceId": "deepseek-v4-preview-0424",
                    },
                    {
                        "benchmarkId": "new-0731",
                        "model": "DeepSeek V4 Flash 0731 (max)",
                        "modelAliases": ["DeepSeek V4 Flash 0731 (max)", "DeepSeek-V4-Flash-0731"],
                        "value": 82.7,
                        "sourceId": "deepseek-v4-flash-0731-update",
                    },
                ],
            },
        )

        flash_0731 = next(model for model in payload["models"] if model["slug"] == "deepseek-v4-flash")
        flash_0424 = next(
            model for model in payload["models"] if model["slug"] == "deepseek-v4-flash-non-reasoning"
        )

        self.assertEqual(flash_0424["scores"]["benchmark:old-0424"], 83.0)
        self.assertIsNone(flash_0731["scores"]["benchmark:old-0424"])
        self.assertEqual(flash_0731["scores"]["benchmark:new-0731"], 82.7)
        self.assertIsNone(flash_0424["scores"]["benchmark:new-0731"])
        self.assertEqual(
            {row["sourceId"] for row in flash_0731["externalBenchmarks"]},
            {"deepseek-v4-flash-0731-update"},
        )

    def test_build_docs_site_runs_when_invoked_by_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            input_csv = tmp / "raw.csv"
            output_json = tmp / "models.json"
            input_csv.write_text(
                "model_key,model,is_reasoning,slug,creator,AA Intelligence Index,GDPval-AA v2\n"
                "Model A,Model A,false,model-a,Lab A,50,80\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/build_docs_site.py",
                    "--input-csv",
                    str(input_csv),
                    "--output-json",
                    str(output_json),
                    "--skip-irt-ranking",
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output_json.exists())
            self.assertTrue((tmp / "models.js").exists())

    def test_write_site_payload_also_writes_file_loadable_js(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            input_csv = tmp / "raw.csv"
            output_json = tmp / "models.json"
            output_js = tmp / "models.js"
            input_csv.write_text(
                "model_key,model,is_reasoning,slug,creator,AA Intelligence Index,GDPval-AA v2\n"
                "Model A,Model A,false,model-a,Lab A,50,80\n",
                encoding="utf-8",
            )

            write_site_payload(input_csv, output_json, output_js)

            content = output_js.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("window.AINSIGHTS_MODELS_DATA = "))
            self.assertIn('"modelRows": 1', content)

    def test_custom_benchmark_lab_can_use_frontier_capability_boards(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "Coding Only Model",
                    "model": "Coding Only Model",
                    "is_reasoning": "true",
                    "slug": "coding-only-model",
                    "Terminal-Bench v2.1": "100",
                },
                {
                    "model_key": "Balanced Model",
                    "model": "Balanced Model",
                    "is_reasoning": "true",
                    "slug": "balanced-model",
                    "Terminal-Bench v2.1": "100",
                    "Humanity's Last Exam": "100",
                    "AA-Omniscience Accuracy": "100",
                    "IFBench": "100",
                },
            ],
            {
                "version": 1,
                "sources": [],
                "benchmarks": [
                    {"id": "swe-bench-pro", "label": "SWE-Bench Pro", "category": "Agentic coding"},
                ],
                "results": [
                    {
                        "benchmarkId": "swe-bench-pro",
                        "model": "Balanced Model",
                        "modelAliases": ["Balanced Model", "balanced-model"],
                        "value": 100,
                    },
                ],
            },
        )
        coding_model = next(model for model in payload["models"] if model["slug"] == "coding-only-model")
        balanced_model = next(model for model in payload["models"] if model["slug"] == "balanced-model")
        preset = self.benchmark_lab_frontier_preset()

        coding_score = score_model_for_preset(
            coding_model,
            preset,
            payload["metrics"],
            payload["metricBaselines"],
            payload["scoreBaselines"]["aaIntelligenceMax"],
        )
        balanced_score = score_model_for_preset(
            balanced_model,
            preset,
            payload["metrics"],
            payload["metricBaselines"],
            payload["scoreBaselines"]["aaIntelligenceMax"],
        )

        self.assertEqual(preset["kind"], "frontier-groups")
        self.assertEqual(preset["missingPolicy"], "weak-prior")
        self.assertEqual(preset["weakPriorRatio"], 0.34)
        self.assertEqual(preset["groupMetricCoverageDiscountExponent"], 0.10)
        self.assertEqual(preset["singleMetricCoverageDiscountExponent"], 0.10)
        self.assertEqual([group["id"] for group in preset["groups"]], [
            "coding",
            "agentic-tool-work",
            "hard-reasoning",
            "knowledge-science",
            "instruction-context",
        ])
        self.assertEqual([group["weight"] for group in preset["groups"]], [40, 24, 20, 8, 8])
        hard_metrics = {
            metric["key"]: metric["weight"]
            for metric in next(group for group in preset["groups"] if group["id"] == "hard-reasoning")["metrics"]
        }
        knowledge_metrics = {
            metric["key"]: metric["weight"]
            for metric in next(group for group in preset["groups"] if group["id"] == "knowledge-science")["metrics"]
        }
        self.assertEqual(hard_metrics["benchmark:aime-2026"], 0.3)
        self.assertEqual(hard_metrics["benchmark:hmmt-2026-feb"], 0.3)
        self.assertEqual(knowledge_metrics["benchmark:mmlu-pro"], 0.2)
        self.assertNotIn("bonusWeights", preset)
        self.assertGreater(balanced_score["score"], coding_score["score"])
        self.assertEqual(coding_score["coverage"], 2)
        self.assertEqual(balanced_score["coverage"], 5)

    def test_precomputed_ranking_score_uses_real_profile_value(self):
        payload = build_site_payload(
            read_csv_rows(DEFAULT_INPUT_CSV),
            load_external_benchmarks(DEFAULT_EXTERNAL_BENCHMARKS_JSON),
        )
        fable = next(model for model in payload["models"] if model["slug"] == "claude-fable-5")
        fable["rankingProfile"] = {
            "displayScore": 97.25,
            "publicationRank": 1,
            "boardTestSlotsTotal": 25,
        }
        preset = payload["presets"]["zhihu-adjusted"]

        score = score_model_for_preset(
            fable,
            preset,
            payload["metrics"],
            payload["metricBaselines"],
            payload["scoreBaselines"]["aaIntelligenceMax"],
        )

        self.assertEqual(score["score"], 97.25)
        self.assertEqual(score["rank"], 1)
        self.assertEqual(score["coverage"], 25)

    def test_custom_benchmark_lab_weights_metrics_inside_frontier_boards(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "Leader Model",
                    "model": "Leader Model",
                    "is_reasoning": "true",
                    "slug": "leader-model",
                    "SciCode": "100",
                },
                {
                    "model_key": "Half SciCode Model",
                    "model": "Half SciCode Model",
                    "is_reasoning": "true",
                    "slug": "half-scicode-model",
                    "SciCode": "50",
                },
            ]
        )
        model = next(model for model in payload["models"] if model["slug"] == "half-scicode-model")
        preset = self.benchmark_lab_frontier_preset()

        score = score_model_for_preset(
            model,
            preset,
            payload["metrics"],
            payload["metricBaselines"],
            payload["scoreBaselines"]["aaIntelligenceMax"],
        )

        self.assertIsNotNone(score["score"])
        self.assertGreater(score["score"], 0)
        self.assertEqual(score["coverage"], 2)
        self.assertAlmostEqual(score["availableWeight"], 48)

    def test_custom_benchmark_lab_uses_livecodebench_external_fit(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "Paired Low Model",
                    "model": "Paired Low Model",
                    "is_reasoning": "true",
                    "slug": "paired-low-model",
                    "LiveCodeBench": "25",
                },
                {
                    "model_key": "Paired High Model",
                    "model": "Paired High Model",
                    "is_reasoning": "true",
                    "slug": "paired-high-model",
                    "LiveCodeBench": "75",
                },
                {
                    "model_key": "Fallback Model",
                    "model": "Fallback Model",
                    "is_reasoning": "true",
                    "slug": "fallback-model",
                },
            ],
            {
                "version": 1,
                "sources": [],
                "benchmarks": [
                    {"id": "livecodebench", "label": "LiveCodeBench", "category": "Coding"},
                ],
                "results": [
                    {
                        "benchmarkId": "livecodebench",
                        "model": "Paired Low Model",
                        "modelAliases": ["Paired Low Model"],
                        "value": 50,
                    },
                    {
                        "benchmarkId": "livecodebench",
                        "model": "Paired High Model",
                        "modelAliases": ["Paired High Model"],
                        "value": 100,
                    },
                    {
                        "benchmarkId": "livecodebench",
                        "model": "Fallback Model",
                        "modelAliases": ["Fallback Model"],
                        "value": 80,
                    },
                ],
            },
        )
        paired = next(model for model in payload["models"] if model["slug"] == "paired-low-model")
        fallback = next(model for model in payload["models"] if model["slug"] == "fallback-model")
        preset = self.benchmark_lab_frontier_preset()

        score = score_model_for_preset(
            fallback,
            preset,
            payload["metrics"],
            payload["metricBaselines"],
            payload["scoreBaselines"]["aaIntelligenceMax"],
        )

        self.assertEqual(paired["scores"]["LiveCodeBench"], 25)
        self.assertEqual(fallback["scores"]["LiveCodeBench"], 55)
        self.assertAlmostEqual(payload["metricBaselines"]["LiveCodeBench"], 75)
        self.assertIsNotNone(score["score"])
        self.assertEqual(score["coverage"], 1)
        self.assertAlmostEqual(score["availableWeight"], 40)

    def test_external_benchmarks_are_shared_across_model_variants(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "Variant Model",
                    "model": "Variant Model",
                    "is_reasoning": "false",
                    "slug": "variant-model",
                    "creator": "Lab",
                    "AA Intelligence Index": "50",
                },
                {
                    "model_key": "Variant Model [R]",
                    "model": "Variant Model",
                    "is_reasoning": "true",
                    "slug": "variant-model-reasoning",
                    "creator": "Lab",
                    "AA Intelligence Index": "60",
                },
            ],
            {
                "version": 1,
                "sources": [],
                "benchmarks": [{"id": "bench", "label": "Bench", "category": "Reasoning"}],
                "results": [
                    {
                        "benchmarkId": "bench",
                        "benchmarkLabel": "Bench",
                        "model": "Variant Model",
                        "modelAliases": ["Variant Model"],
                        "value": 88,
                        "sourceId": "official",
                        "sourceLabel": "Official",
                        "sourceUrl": "https://example.com",
                    }
                ],
            },
        )

        non_reasoning = next(model for model in payload["models"] if model["slug"] == "variant-model")
        reasoning = next(model for model in payload["models"] if model["slug"] == "variant-model-reasoning")

        self.assertEqual(non_reasoning["scores"]["benchmark:bench"], 88)
        self.assertEqual(reasoning["scores"]["benchmark:bench"], 88)
        self.assertEqual(reasoning["externalBenchmarks"][0]["sourceLabel"], "Official")
        self.assertTrue(reasoning["externalBenchmarks"][0]["sharedFromVariant"])

    def test_precomputed_ranking_profile_is_model_name_agnostic(self):
        payload = build_site_payload(
            read_csv_rows(DEFAULT_INPUT_CSV),
            load_external_benchmarks(DEFAULT_EXTERNAL_BENCHMARKS_JSON),
        )
        preset = payload["presets"]["zhihu-adjusted"]
        model = next(model for model in payload["models"] if model["slug"] == "qwen3-8-max")
        model["rankingProfile"] = {
            "displayScore": 95.5,
            "publicationRank": 7,
            "boardTestSlotsTotal": 21,
        }
        relabeled = dict(model)
        relabeled.update(
            {
                "model": "Anonymous evaluation configuration",
                "slug": "anonymous-evaluation-configuration",
                "creator": "Anonymous",
                "variantGroup": "anonymous-evaluation-configuration",
            }
        )

        def score(candidate):
            return score_model_for_preset(
                candidate,
                preset,
                payload["metrics"],
                payload["metricBaselines"],
                payload["scoreBaselines"]["aaIntelligenceMax"],
            )["score"]

        self.assertIsNotNone(score(model))
        self.assertEqual(score(model), score(relabeled))
        self.assertEqual(score(model), 95.5)

    def test_qwen36_benchmark_lab_scores_are_independently_data_driven(self):
        payload = build_site_payload(
            read_csv_rows(DEFAULT_INPUT_CSV),
            load_external_benchmarks(DEFAULT_EXTERNAL_BENCHMARKS_JSON),
        )
        preset = self.benchmark_lab_frontier_preset()
        scores = {}
        for model in payload["models"]:
            if model["slug"] not in {"qwen3-6-27b", "qwen3-6-plus", "qwen3-6-max"}:
                continue
            score = score_model_for_preset(
                model,
                preset,
                payload["metrics"],
                payload["metricBaselines"],
                payload["scoreBaselines"]["aaIntelligenceMax"],
            )
            scores[model["slug"]] = score["score"]
            self.assertNotIn("presetMetricFallbacks", model)

        self.assertEqual(set(scores), {"qwen3-6-27b", "qwen3-6-plus", "qwen3-6-max"})
        self.assertTrue(all(score is not None for score in scores.values()))
        self.assertGreater(scores["qwen3-6-plus"], scores["qwen3-6-27b"])
        self.assertNotEqual(scores["qwen3-6-max"], scores["qwen3-6-plus"])

    def test_custom_benchmark_lab_discounts_sparse_regular_coverage(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "Sparse GPQA Model",
                    "model": "Sparse GPQA Model",
                    "is_reasoning": "true",
                    "slug": "sparse-gpqa-model",
                    "SciCode": "100",
                },
                {
                    "model_key": "Broad Suite Model",
                    "model": "Broad Suite Model",
                    "is_reasoning": "true",
                    "slug": "broad-suite-model",
                    "SciCode": "70",
                    "Terminal-Bench Hard": "70",
                    "LiveCodeBench": "70",
                    "Humanity's Last Exam": "70",
                    "GPQA Diamond": "70",
                    "AIME 2025": "70",
                },
            ]
        )
        preset = self.benchmark_lab_frontier_preset()
        sparse = next(model for model in payload["models"] if model["slug"] == "sparse-gpqa-model")
        broad = next(model for model in payload["models"] if model["slug"] == "broad-suite-model")

        sparse_score = score_model_for_preset(
            sparse,
            preset,
            payload["metrics"],
            payload["metricBaselines"],
            payload["scoreBaselines"]["aaIntelligenceMax"],
        )
        broad_score = score_model_for_preset(
            broad,
            preset,
            payload["metrics"],
            payload["metricBaselines"],
            payload["scoreBaselines"]["aaIntelligenceMax"],
        )

        self.assertGreater(broad_score["score"], sparse_score["score"])
        self.assertLess(sparse_score["score"], 70)
        self.assertEqual(sparse_score["coverage"], 2)

    def test_weighted_metric_score_supports_geometric_mean(self):
        model = {"scores": {"A": 100, "B": 25}}

        score = weighted_metric_score(
            model,
            {"A": 1, "B": 1},
            False,
            method="geometric",
        )

        self.assertAlmostEqual(score["score"], math.sqrt(101 * 26) - 1)
        self.assertEqual(score["coverage"], 2)

    def test_weighted_metric_score_supports_relative_best_normalization(self):
        model = {"scores": {"A": 50, "B": 25}}

        score = weighted_metric_score(
            model,
            {"A": 1, "B": 1},
            False,
            method="arithmetic",
            normalization="relative-best",
            metric_baselines={"A": 100, "B": 50},
            display_scale=90,
        )

        self.assertAlmostEqual(score["score"], 45)
        self.assertEqual(score["coverage"], 2)

    def test_weighted_metric_score_supports_custom_missing_policies(self):
        model = {"scores": {"A": 100}}

        coverage_discount = weighted_metric_score(
            model,
            {"A": 1, "B": 1},
            True,
            method="geometric",
            normalization="relative-best",
            metric_baselines={"A": 100, "B": 100},
            display_scale=100,
            missing_policy="coverage-discount",
            coverage_discount_exponent=0.5,
        )
        weak_prior = weighted_metric_score(
            model,
            {"A": 1, "B": 1},
            True,
            method="geometric",
            normalization="relative-best",
            metric_baselines={"A": 100, "B": 100},
            display_scale=100,
            missing_policy="weak-prior",
            weak_prior_ratio=0.35,
        )

        self.assertAlmostEqual(coverage_discount["score"], 100 * (1 / 2) ** 0.5)
        self.assertEqual(coverage_discount["coverage"], 1)
        self.assertAlmostEqual(weak_prior["score"], (math.sqrt(2 * 1.35) - 1) * 100)
        self.assertEqual(weak_prior["coverage"], 1)

    def test_default_score_uses_relative_best_then_aa_intelligence_scale(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "Leader Model",
                    "model": "Leader Model",
                    "is_reasoning": "true",
                    "slug": "leader-model",
                    "AA Intelligence Index": "90",
                    "GDPval-AA v2": "100",
                },
                {
                    "model_key": "Ratio Model",
                    "model": "Ratio Model",
                    "is_reasoning": "true",
                    "slug": "ratio-model",
                    "AA Intelligence Index": "60",
                    "GDPval-AA v2": "50",
                },
            ]
        )
        model = next(model for model in payload["models"] if model["slug"] == "ratio-model")
        preset = payload["presets"]["zhihu-adjusted"]

        score = score_model_for_preset(
            model,
            preset,
            payload["metrics"],
            payload["metricBaselines"],
            payload["scoreBaselines"]["aaIntelligenceMax"],
        )

        self.assertIsNone(score["score"])
        self.assertEqual(score["coverage"], 0)

    def test_geometric_weighted_score_penalizes_missing_without_collapsing_to_zero(self):
        model = {"scores": {"A": 100}}

        score = weighted_metric_score(
            model,
            {"A": 1, "B": 1},
            False,
            method="geometric",
        )

        self.assertAlmostEqual(score["score"], math.sqrt(101) - 1)
        self.assertEqual(score["coverage"], 1)

    def test_aa_presets_include_official_component_weights(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "AA Preset Model",
                    "model": "AA Preset Model",
                    "is_reasoning": "false",
                    "slug": "aa-preset-model",
                    "AA Intelligence Index": "50",
                }
            ]
        )

        intelligence = payload["presets"]["aa-intelligence"]["weights"]
        coding = payload["presets"]["aa-coding"]["weights"]
        agentic = payload["presets"]["aa-agentic"]["weights"]

        self.assertAlmostEqual(intelligence["GDPval-AA v2"], 20)
        self.assertAlmostEqual(intelligence["τ³-Banking"], 14)
        self.assertAlmostEqual(intelligence["Terminal-Bench v2.1"], 16)
        self.assertAlmostEqual(intelligence["SciCode"], 8)
        self.assertAlmostEqual(intelligence["AA-LCR"], 6)
        self.assertAlmostEqual(intelligence["AA-Omniscience Accuracy"], 8)
        self.assertAlmostEqual(intelligence["AA-Omniscience Non-Hallucination Rate"], 4)
        self.assertAlmostEqual(intelligence["Humanity's Last Exam"], 12)
        self.assertAlmostEqual(intelligence["GPQA Diamond"], 6)
        self.assertAlmostEqual(intelligence["CritPt"], 6)
        self.assertEqual(coding, {"Terminal-Bench v2.1": 200 / 3, "SciCode": 100 / 3})
        self.assertEqual(agentic, {"GDPval-AA v2": 1000 / 17, "τ³-Banking": 700 / 17})

    def test_custom_benchmark_lab_uses_frontier_board_coverage(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "Sparse Default Model",
                    "model": "Sparse Default Model",
                    "is_reasoning": "false",
                    "slug": "sparse-default-model",
                    "SciCode": "84",
                }
            ]
        )
        model = payload["models"][0]
        preset = self.benchmark_lab_frontier_preset()

        score = score_model_for_preset(
            model,
            preset,
            payload["metrics"],
            payload["metricBaselines"],
            payload["scoreBaselines"]["aaIntelligenceMax"],
        )

        self.assertIsNotNone(score["score"])
        self.assertEqual(score["coverage"], 2)
        self.assertAlmostEqual(score["availableWeight"], 48)

    def test_custom_score_uses_geometric_coverage_discount_by_default(self):
        payload = build_site_payload(
            [
                {
                    "model_key": "Sparse Model",
                    "model": "Sparse Model",
                    "is_reasoning": "true",
                    "slug": "sparse-model",
                    "GPQA Diamond": "84",
                }
            ]
        )
        model = payload["models"][0]
        preset = payload["presets"]["custom"]

        score = score_model_for_preset(
            model,
            preset,
            payload["metrics"],
            payload["metricBaselines"],
            payload["scoreBaselines"]["aaIntelligenceMax"],
        )

        self.assertEqual(preset["calculation"], "geometric")
        self.assertEqual(preset["missingPolicy"], "coverage-discount")
        available_weight = preset["weights"]["GPQA Diamond"]
        total_weight = sum(weight for weight in preset["weights"].values() if weight > 0)
        expected = 100 * (available_weight / total_weight) ** 0.25
        self.assertAlmostEqual(score["score"], expected)
        self.assertEqual(score["coverage"], 1)

    def test_additional_china_official_apis_are_exact_and_model_specific(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        offers = {offer["id"]: offer for offer in catalogue["offers"]}

        self.assertNotIn("md-longcat-longcat-2-0", offers)
        zhipu = [
            offer
            for offer in catalogue["offers"]
            if offer["providerId"] == "zhipu-bigmodel-api-cn"
        ]
        self.assertEqual(
            {offer["modelSlugs"][0] for offer in zhipu},
            {"glm-5-2", "glm-5-1", "glm-5-turbo", "glm-5", "glm-4-7", "glm-4-5-air"},
        )
        for offer in zhipu:
            self.assertEqual(len(offer["modelSlugs"]), 1)
            self.assertTrue(offer["comparable"])
            self.assertGreater(offer["inputPerMillionTokensLocal"], 0)
            self.assertGreater(offer["outputPerMillionTokensLocal"], 0)

        expected_pack_prices = {
            "zhipu-bigmodel-pack-glm-5-2-20m-offer": ("glm-5-2", 1.995),
            "zhipu-bigmodel-pack-glm-5-2-100m-offer": ("glm-5-2", 1.899),
            "zhipu-bigmodel-pack-glm-4-6v-10m-offer": ("glm-4-6v", 1.6),
            "zhipu-bigmodel-pack-glm-4-6v-500m-offer": ("glm-4-6v", 1.6),
        }
        for offer_id, (slug, price) in expected_pack_prices.items():
            offer = offers[offer_id]
            self.assertEqual(offer["modelSlugs"], [slug])
            self.assertAlmostEqual(offer["inputPerMillionTokensLocal"], price)
            self.assertAlmostEqual(offer["outputPerMillionTokensLocal"], price)

        longcat = [offer for offer in catalogue["offers"] if offer["providerId"] == "longcat"]
        self.assertEqual(
            {offer["id"] for offer in longcat},
            {
                "longcat-payg-discounted-longcat-2-0",
                "longcat-payg-list-longcat-2-0",
            },
        )
        self.assertTrue(all(offer["modelSlugs"] == ["longcat-2-0"] for offer in longcat))

        doubao = offers["volcengine-ark-cn-doubao-seed-code"]
        self.assertEqual(doubao["modelSlugs"], ["doubao-seed-code"])
        self.assertEqual(
            [row["minPromptTokens"] for row in doubao["pricingOverrides"]],
            [32001, 128001],
        )

    def test_additional_global_coding_plans_are_single_model_and_display_only(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        provider_ids = {
            "amazon-q-developer",
            "augment-code",
            "sourcegraph-cody",
            "replit",
            "devin",
            "tabnine",
        }
        providers = {
            provider["id"]
            for provider in catalogue["providers"]
            if provider["id"] in provider_ids
        }
        self.assertEqual(providers, provider_ids)

        offers = [
            offer
            for offer in catalogue["offers"]
            if offer["providerId"] in provider_ids
        ]
        self.assertEqual(len(offers), 349)
        self.assertTrue(all(len(offer["modelSlugs"]) == 1 for offer in offers))
        self.assertEqual(
            len({(offer["planId"], offer["modelSlugs"][0]) for offer in offers}),
            len(offers),
        )
        self.assertTrue(all(not offer["comparable"] for offer in offers))

        finite = [
            offer
            for offer in offers
            if any(
                offer.get(field) is not None
                for field in (
                    "inputPerMillionTokensUsd",
                    "effectiveUsdPerMillionTokens",
                    "effectiveUsdPerMillionIncludedTokens",
                )
            )
        ]
        self.assertEqual(len(finite), 261)
        self.assertTrue(
            all(
                offer.get("bestCaseOnly")
                or offer.get("requiresSubscription")
                or offer["pricingKind"] in {"per-token-overage", "per-token-plus-service-fee"}
                for offer in finite
            )
        )

    def test_qiniu_and_model_author_apis_keep_exact_published_rates(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        offers = {offer["id"]: offer for offer in catalogue["offers"]}

        qiniu = [offer for offer in catalogue["offers"] if offer["providerId"] == "qiniu-ai"]
        self.assertEqual(len(qiniu), 22)
        self.assertTrue(all(len(offer["modelSlugs"]) == 1 for offer in qiniu))
        self.assertEqual(
            {offer["planId"] for offer in qiniu},
            {"qiniu-ai-payg", "qiniu-ai-batch-payg"},
        )

        expected = {
            "ai21-api-jamba-1-7-large": ("jamba-1-7-large", 2, 8),
            "upstage-solar-pro-3": ("solar-pro-3", 0.15, 0.6),
            "upstage-solar-pro-2": ("solar-pro-2", 0.15, 0.6),
            "upstage-solar-mini": ("solar-mini", 0.15, 0.15),
            "reka-api-reka-flash": ("reka-flash", 0.8, 2),
            "inception-mercury-2": ("mercury-2", 0.25, 0.75),
        }
        for offer_id, (slug, input_rate, output_rate) in expected.items():
            offer = offers[offer_id]
            self.assertEqual(offer["modelSlugs"], [slug])
            self.assertAlmostEqual(offer["inputPerMillionTokensUsd"], input_rate)
            self.assertAlmostEqual(offer["outputPerMillionTokensUsd"], output_rate)
            self.assertTrue(offer["comparable"])

        sarvam = offers["sarvam-api-sarvam-105b"]
        self.assertEqual(sarvam["modelSlugs"], ["sarvam-105b"])
        self.assertEqual(sarvam["inputPerMillionTokensUsd"], 0)
        self.assertEqual(sarvam["outputPerMillionTokensUsd"], 0)
        self.assertTrue(sarvam["publishedZeroRate"])
        self.assertTrue(sarvam["comparable"])


if __name__ == "__main__":
    unittest.main()
