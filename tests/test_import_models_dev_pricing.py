import unittest

from scripts.build_docs_site import DEFAULT_PROVIDER_PRICING_JSON, load_provider_pricing
from scripts.import_models_dev_pricing import (
    DEFAULT_MODELS,
    NON_PAYG_PROVIDER_IDS,
    UNAVAILABLE_MODEL_STATUSES,
    SiteModel,
    build_site_indexes,
    load_site_models,
    matched_site_slugs,
)


class ModelsDevPricingImportTests(unittest.TestCase):
    def test_imported_catalogue_rows_are_exact_single_model_positive_payg_rates(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        imported_offers = [
            offer
            for offer in catalogue["offers"]
            if offer.get("importedFrom") == "models.dev"
        ]

        # Conservative slug-only matching intentionally rejects thousands of
        # ambiguous display-name/variant-group expansions while preserving
        # broad provider and model coverage.
        self.assertGreaterEqual(len(imported_offers), 2_500)
        self.assertGreaterEqual(
            len({offer["providerId"] for offer in imported_offers}),
            120,
        )
        self.assertGreaterEqual(
            len({offer["modelSlugs"][0] for offer in imported_offers}),
            200,
        )
        for offer in imported_offers:
            self.assertEqual(len(offer["modelSlugs"]), 1)
            self.assertGreater(offer["inputPerMillionTokensUsd"], 0)
            self.assertGreater(offer["outputPerMillionTokensUsd"], 0)
            self.assertIn(
                offer["mappingMethod"],
                {"exact-normalized-identifier", "exact-token-multiset"},
            )
            if offer.get("bestCaseOnly"):
                self.assertFalse(offer["comparable"])
            else:
                self.assertTrue(offer["comparable"])
            self.assertTrue(offer["estimated"])
            self.assertEqual(offer["evidenceKind"], "community-catalog")
            self.assertNotIn(offer.get("status"), UNAVAILABLE_MODEL_STATUSES)
            self.assertNotEqual(offer.get("cacheReadPerMillionTokensUsd"), 0)

    def test_subscription_and_credit_catalogues_are_not_imported_as_free_token_rates(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        imported_provider_origins = {
            provider.get("modelsDevProviderId")
            for provider in catalogue["providers"]
            if provider.get("importedFrom") == "models.dev"
        }

        self.assertFalse(imported_provider_origins & NON_PAYG_PROVIDER_IDS)

    def test_generic_provider_ids_do_not_expand_to_dated_or_private_variants(self):
        catalogue = load_provider_pricing(DEFAULT_PROVIDER_PRICING_JSON)
        imported_offers = [
            offer
            for offer in catalogue["offers"]
            if offer.get("importedFrom") == "models.dev"
        ]

        generic_gemini = [
            offer
            for offer in imported_offers
            if offer.get("providerModelId", "").split("/")[-1] == "gemini-2.5-flash"
        ]
        generic_gpt4o = [
            offer
            for offer in imported_offers
            if offer.get("providerModelId", "").split("/")[-1] == "gpt-4o"
        ]

        self.assertTrue(generic_gemini)
        self.assertTrue(generic_gpt4o)
        self.assertEqual(
            {offer["modelSlugs"][0] for offer in generic_gemini},
            {"gemini-2-5-flash"},
        )
        self.assertEqual(
            {offer["modelSlugs"][0] for offer in generic_gpt4o},
            {"gpt-4o"},
        )

    def test_model_matching_never_accepts_partial_names(self):
        models = [
            SiteModel(
                slug="claude-sonnet-5",
                names=("Claude Sonnet 5", "claude-sonnet-5"),
            )
        ]
        normalized, bags, _ = build_site_indexes(models)

        exact = matched_site_slugs(
            "claude-sonnet-5",
            {"name": "Claude Sonnet 5"},
            normalized,
            bags,
        )
        reordered = matched_site_slugs(
            "claude-5-sonnet",
            {"name": "Claude 5 Sonnet"},
            normalized,
            bags,
        )
        partial = matched_site_slugs(
            "sonnet-5",
            {"name": "Sonnet 5"},
            normalized,
            bags,
        )

        self.assertEqual(set(exact), {"claude-sonnet-5"})
        self.assertEqual(set(reordered), {"claude-sonnet-5"})
        self.assertEqual(partial, {})

    def test_reordered_descriptors_keep_version_number_order_semantic(self):
        models = [
            SiteModel(slug="gpt-5-4", names=("GPT-5.4", "gpt-5-4")),
            SiteModel(slug="gpt-4-5", names=("GPT-4.5", "gpt-4-5")),
            SiteModel(
                slug="claude-sonnet-4-6",
                names=("Claude Sonnet 4.6", "claude-sonnet-4-6"),
            ),
        ]
        normalized, bags, _ = build_site_indexes(models)

        gpt = matched_site_slugs(
            "gpt-5-4",
            {"name": "GPT 5.4"},
            normalized,
            bags,
        )
        claude = matched_site_slugs(
            "claude-4-6-sonnet",
            {"name": "Claude 4.6 Sonnet"},
            normalized,
            bags,
        )

        self.assertEqual(set(gpt), {"gpt-5-4"})
        self.assertNotIn("gpt-4-5", gpt)
        self.assertEqual(set(claude), {"claude-sonnet-4-6"})

    def test_production_matching_indexes_only_unambiguous_model_slugs(self):
        models = load_site_models(DEFAULT_MODELS)

        self.assertTrue(models)
        self.assertTrue(all(model.names == (model.slug,) for model in models))

        selected = [
            SiteModel(slug="gemini-2-5-flash", names=("gemini-2-5-flash",)),
            SiteModel(
                slug="gemini-2-5-flash-preview-09-2025",
                names=("gemini-2-5-flash-preview-09-2025",),
            ),
        ]
        normalized, bags, _ = build_site_indexes(selected)
        matches = matched_site_slugs(
            "gemini-2.5-flash",
            {"name": "Gemini 2.5 Flash"},
            normalized,
            bags,
        )

        self.assertEqual(set(matches), {"gemini-2-5-flash"})


if __name__ == "__main__":
    unittest.main()
