import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import numpy as np

from analysis.irt_leaderboard_exploration import aindex_mixed_core as primary
from analysis.irt_leaderboard_exploration import multi_method_evidence_analysis as analysis


def core_only_payload():
    """New benchmark coverage without the historical HLE/GPQA/LCR item pool."""
    return {"models": [
        {
            "slug": f"new-core-{index:02}",
            "model": f"New Core {index}",
            "creator": f"Fixture {index % 3}",
            "variantGroup": f"new-core-{index:02}",
            "variantPriority": 10,
            "scores": {
                key: float(35 + index + slot)
                for slot, key in enumerate(key for keys in primary.CORE_ITEMS.values() for key in keys)
            },
        }
        for index in range(12)
    ]}


class PrimaryAuditIndependenceTests(unittest.TestCase):
    def setUp(self):
        self.payload = core_only_payload()

    def assert_primary_matches(self, result, expected):
        self.assertEqual(result["aindex_mixed_core_full_rankings"], expected["full_rankings"])
        self.assertEqual(result["exact_config_aindex_mixed_core_full_rankings"], expected["exact_config_full_rankings"])
        self.assertEqual(result["aindex_mixed_core_calibration"], expected["calibration"])
        self.assertTrue(result["aindex_mixed_core_validation"]["passed"])
        self.assertEqual(result["summary"]["legacy_audits"]["status"], "unavailable")
        for key in ("full_rankings", "top50", "exact_config_full_rankings", "exact_config_top50"):
            self.assertEqual(result[key], {method: [] for method in analysis.METHOD_LABELS})

    def test_all_eight_core_items_publish_without_legacy_coverage(self):
        expected = primary.run_aindex_mixed_core_from_payload(self.payload)
        result = analysis.run_multi_method_analysis_from_payload(self.payload)
        self.assert_primary_matches(result, expected)
        self.assertEqual(len(result["aindex_mixed_core_full_rankings"]), 12)
        self.assertTrue(all(row["missing_core_count"] == 0 for row in result["aindex_mixed_core_full_rankings"]))
        self.assertIn("coverage requirements", result["summary"]["legacy_audits"]["reason"])

        # The site must also accept a valid production profile with no IRT rows.
        from scripts.build_docs_site import attach_irt_ranking_profiles
        site = attach_irt_ranking_profiles(copy.deepcopy(self.payload), result)
        self.assertEqual(site["leaderboard"]["populationSize"], 12)
        self.assertTrue(all(model["rankingProfile"]["method"] == primary.METHOD_ID for model in site["models"]))

    def test_explicit_audit_qualification_failure_occurs_after_primary_validation(self):
        expected = primary.run_aindex_mixed_core_from_payload(self.payload)

        def unavailable(payload, *, primary_result, **kwargs):
            self.assertTrue(primary_result["validation"]["passed"])
            self.assertEqual(primary_result, expected)
            raise analysis.LegacyAuditUnavailable("simulated insufficient legacy evidence")

        with mock.patch.object(analysis, "_run_legacy_audits_from_payload", side_effect=unavailable):
            result = analysis.run_multi_method_analysis_from_payload(self.payload)
        self.assert_primary_matches(result, expected)

    def test_numeric_legacy_fit_failure_is_explicitly_unavailable(self):
        expected = primary.run_aindex_mixed_core_from_payload(self.payload)
        for failure in (FloatingPointError("legacy numeric fit"), np.linalg.LinAlgError("singular legacy fit")):
            with self.subTest(type=type(failure).__name__):
                with mock.patch.object(analysis, "_run_legacy_audits_from_payload", side_effect=failure):
                    result = analysis.run_multi_method_analysis_from_payload(self.payload)
                self.assert_primary_matches(result, expected)
                self.assertEqual(result["summary"]["legacy_audits"]["reason_type"], type(failure).__name__)

    def test_legacy_io_and_programming_errors_still_fail_publication(self):
        for failure in (OSError("disk full"), KeyError("missing field"), ValueError("broken parser"),
                        AssertionError("bad score identity"), TypeError("bad interface")):
            with self.subTest(type=type(failure).__name__):
                with mock.patch.object(analysis, "_run_legacy_audits_from_payload", side_effect=failure):
                    with self.assertRaises(type(failure)):
                        analysis.run_multi_method_analysis_from_payload(self.payload)

    def test_primary_failures_never_enter_optional_audit_handling(self):
        with mock.patch.object(primary, "run_aindex_mixed_core_from_payload", side_effect=AssertionError("mixed Core production validation failed")):
            with mock.patch.object(analysis, "_run_legacy_audits_from_payload") as legacy:
                with self.assertRaisesRegex(AssertionError, "mixed Core production validation failed"):
                    analysis.run_multi_method_analysis_from_payload(self.payload)
                legacy.assert_not_called()

    def test_scheme18_classifies_only_known_data_qualification_assertions(self):
        for message in ("Scheme 18 calibration population is empty", "cannot derive Scheme 18 cap without positive evidence"):
            with self.subTest(message=message):
                with mock.patch.object(analysis.scheme18, "run_aindex_scheme18_from_payload", side_effect=AssertionError(message)):
                    with self.assertRaisesRegex(analysis.LegacyAuditUnavailable, message):
                        analysis._run_optional_scheme18(self.payload)
        with mock.patch.object(analysis.scheme18, "run_aindex_scheme18_from_payload", side_effect=AssertionError("Scheme 18 production validation failed")):
            with self.assertRaisesRegex(AssertionError, "Scheme 18 production validation failed"):
                analysis._run_optional_scheme18(self.payload)

    def test_unavailable_export_clears_stale_audits_and_preserves_primary_files(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            old_csv = output / "full_rankings_aindex_scheme18.csv"
            old_csv.write_text("stale audit data", encoding="utf-8")
            result = analysis.run_multi_method_analysis_from_payload(self.payload, output_dir=output, write_outputs=True)
            self.assertEqual(old_csv.read_text(encoding="utf-8"), "")
            self.assertTrue((output / primary.OUTPUT_FILENAMES["full_rankings"]).read_text(encoding="utf-8"))
            primary_validation = json.loads((output / primary.OUTPUT_FILENAMES["validation"]).read_text(encoding="utf-8"))
            self.assertTrue(primary_validation["passed"])
            summary = json.loads((output / "multi_method_validation_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary, json.loads(json.dumps(result["summary"])))
            old_validation = json.loads((output / "aindex_scheme18_validation_summary.json").read_text(encoding="utf-8"))
            self.assertIsNone(old_validation["passed"])
            self.assertEqual(old_validation["status"], "unavailable")
            for method in analysis.METHOD_LABELS:
                self.assertTrue((output / f"top50_{method}.csv").exists())


if __name__ == "__main__":
    unittest.main()
