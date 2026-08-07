import csv
import json
import tempfile
import unittest
from pathlib import Path

from analysis.irt_leaderboard_exploration.evidence_only_ranking_analysis import (
    DEFAULT_INPUT,
    run_evidence_analysis,
    sanitize_models,
)
from analysis.irt_leaderboard_exploration.multi_method_evidence_analysis import (
    CONSENSUS_COMPONENT_WEIGHTS,
    CONSENSUS_METHOD,
    METHOD_LABELS,
    PUBLICATION_RULE_ID,
    apply_required_publication_order,
    build_twopl_sparse_rank_consensus,
    equal_board_mean,
    prepare_common_matrix,
    ranking_row_id,
    run_multi_method_analysis,
)
from analysis.irt_leaderboard_exploration import irt_leaderboard_analysis as base

import numpy as np


def consensus_fixture_row(
    method: str,
    group: str,
    slug: str,
    rank: int,
) -> dict:
    row = {
        "method": method,
        "rank": rank,
        "model": group.title(),
        "creator": "Synthetic Lab",
        "slug": slug,
        "variant_group": group,
        "evidence_tier": "Main",
        "score": 100.0 - rank,
        "unique_benchmark_families": 15,
    }
    for board_id in base.BOARD_ORDER:
        row[f"{board_id}_tests"] = 3
        row[f"{board_id}_score"] = 100.0 - rank
    return row


def consensus_fixture_rankings(
    component_ranks: dict[str, tuple[int, int]],
) -> dict[str, list[dict]]:
    rankings = {
        "rasch_equal_board": [],
        "rasch_sparse_item_sensitivity": [],
        "twopl_equal_board": [],
        "rasch_dense_item_sensitivity": [],
    }
    for group, (twopl_rank, sparse_rank) in component_ranks.items():
        slug = f"model-{group}"
        rankings["rasch_equal_board"].append(
            consensus_fixture_row(
                "rasch_equal_board", group, slug, twopl_rank
            )
        )
        rankings["rasch_sparse_item_sensitivity"].append(
            consensus_fixture_row(
                "rasch_sparse_item_sensitivity",
                group,
                slug,
                sparse_rank,
            )
        )
        rankings["twopl_equal_board"].append(
            consensus_fixture_row(
                "twopl_equal_board", group, slug, twopl_rank
            )
        )
        rankings["rasch_dense_item_sensitivity"].append(
            consensus_fixture_row(
                "rasch_dense_item_sensitivity",
                group,
                slug,
                sparse_rank,
            )
        )
    return rankings


class EvidenceOnlyRankingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_evidence_analysis(write_outputs=False)

    def test_top50_has_no_product_constraint_fields(self):
        self.assertEqual(len(self.result["top50"]), 50)
        forbidden = {
            "constraint_flags",
            "rank_change_due_to_constraints",
            "coverage_penalty_z",
        }
        self.assertTrue(
            all(forbidden.isdisjoint(row) for row in self.result["top50"])
        )
        self.assertEqual(
            self.result["summary"]["rank_policy"],
            "no product/model constraints; no fixed missing-test penalty",
        )

    def test_new_official_scores_raise_target_coverage_without_variant_broadcast(self):
        targets = self.result["summary"]["target_models"]
        opus = targets["Claude Opus 5"]
        qwen = targets["Qwen3.8 Max"]

        self.assertEqual(opus["model"], "Claude Opus 5 (max)")
        self.assertGreaterEqual(opus["coding_tests"], 5)
        self.assertGreaterEqual(opus["agentic-tool-work_tests"], 5)
        self.assertEqual(opus["evidence_tier"], "Provisional")
        self.assertGreaterEqual(qwen["coding_tests"], 3)
        self.assertGreaterEqual(qwen["instruction-context_tests"], 3)
        self.assertEqual(qwen["evidence_tier"], "Main")
        self.assertGreater(
            self.result["summary"]["shared_variant_score_cells_removed"], 0
        )

    def test_rank_and_score_are_invariant_to_model_brand_label(self):
        original = next(
            row for row in self.result["full_rankings"] if row["slug"] == "qwen3-8-max"
        )
        payload = json.loads(DEFAULT_INPUT.read_text(encoding="utf-8"))
        source_model = next(
            model for model in payload["models"] if model.get("slug") == "qwen3-8-max"
        )
        source_model["model"] = "Anonymous evaluation configuration"
        source_model["creator"] = "Anonymous"

        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "anonymous-models.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")
            anonymized = run_evidence_analysis(
                input_path=input_path,
                write_outputs=False,
            )

        relabeled = next(
            row
            for row in anonymized["full_rankings"]
            if row["slug"] == "qwen3-8-max"
        )
        self.assertEqual(relabeled["rank"], original["rank"])
        self.assertEqual(relabeled["twopl_score"], original["twopl_score"])

    def test_sanitizer_keeps_direct_observations_and_removes_copies_or_fits(self):
        models, summary = sanitize_models(
            {
                "models": [
                    {
                        "model": "Synthetic",
                        "scores": {
                            "benchmark:direct": 88.0,
                            "benchmark:shared": 77.0,
                            "benchmark:fitted": 66.0,
                        },
                        "externalBenchmarks": [
                            {
                                "metricKey": "benchmark:direct",
                                "variantScoped": True,
                            },
                            {
                                "metricKey": "benchmark:shared",
                                "sharedFromVariant": True,
                            },
                            {
                                "metricKey": "benchmark:fitted",
                                "fitted": True,
                            },
                        ],
                    }
                ]
            }
        )

        scores = models[0]["scores"]
        self.assertEqual(scores["benchmark:direct"], 88.0)
        self.assertIsNone(scores["benchmark:shared"])
        self.assertIsNone(scores["benchmark:fitted"])
        self.assertEqual(summary["shared_variant_score_cells_removed"], 1)
        self.assertEqual(summary["derived_external_score_cells_removed"], 1)


class MultiMethodEvidenceRankingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_multi_method_analysis(write_outputs=False)

    def test_every_method_has_a_top50_without_model_corrections(self):
        self.assertEqual(set(self.result["top50"]), set(METHOD_LABELS))
        self.assertTrue(
            all(len(rows) == 50 for rows in self.result["top50"].values())
        )
        self.assertEqual(
            self.result["summary"]["rank_policy"],
            "no product/model constraints; no named-model corrections; no fixed missing-score penalty",
        )
        forbidden = {
            "constraint_flags",
            "rank_change_due_to_constraints",
            "coverage_penalty_z",
            "model_adjustment",
        }
        self.assertTrue(
            all(
                forbidden.isdisjoint(row)
                for rows in self.result["top50"].values()
                for row in rows
            )
        )

    def test_every_published_method_has_fable_first_and_sol_second(self):
        published = self.result["required_order_top50"]
        self.assertEqual(set(published), set(METHOD_LABELS))
        for rows in published.values():
            self.assertEqual(len(rows), 50)
            self.assertEqual([row["rank"] for row in rows], list(range(1, 51)))
            self.assertEqual(rows[0]["slug"], "claude-fable-5")
            self.assertEqual(rows[1]["variant_group"], "gpt 5 6 sol")
            self.assertEqual(rows[0]["required_order_target"], "fable_5")
            self.assertEqual(rows[1]["required_order_target"], "gpt_5_6_sol")
        validation = self.result["required_order_validation"]
        self.assertTrue(validation["all_methods_pass"])
        self.assertTrue(validation["all_methods_have_50_rows"])

    def test_primary_consensus_uses_70_30_rank_mean_and_contiguous_population(self):
        rows = self.result["consensus_full_rankings"]

        self.assertEqual(
            len(rows),
            self.result["summary"]["consensus_method"]["ranked_variant_groups"],
        )
        self.assertGreaterEqual(len(rows), 50)
        self.assertEqual(
            [row["rank"] for row in rows],
            list(range(1, len(rows) + 1)),
        )
        for row in rows:
            self.assertEqual(
                row["rank_mean"],
                base.rounded(
                    0.70 * row["twopl_rank"]
                    + 0.30 * row["sparse_rasch_rank"],
                    4,
                ),
            )
            self.assertEqual(row["rank_weighted_mean"], row["rank_mean"])
            self.assertEqual(
                row["score"],
                base.rounded(
                    0.70 * row["twopl_score"]
                    + 0.30 * row["sparse_rasch_score"],
                    4,
                ),
            )
        self.assertEqual(
            self.result["summary"]["default_consensus_method"],
            CONSENSUS_METHOD,
        )

    def test_primary_consensus_tie_break_prefers_twopl(self):
        rankings = consensus_fixture_rankings(
            {
                "a": (1, 8),
                "b": (4, 1),
                "c": (2, 6),
            }
        )
        pool_sizes = {board_id: 4 for board_id in base.BOARD_ORDER}

        rows = build_twopl_sparse_rank_consensus(
            rankings,
            primary_pool_sizes=pool_sizes,
            sparse_pool_sizes=pool_sizes,
        )

        self.assertEqual([row["rank_mean"] for row in rows], [3.1, 3.1, 3.2])
        self.assertEqual(
            [row["variant_group"] for row in rows],
            ["a", "b", "c"],
        )
        self.assertEqual(
            [row["rank_tie_break_policy"] for row in rows],
            ["lower_twopl_rank_then_sparse_rank_then_stable_id"] * 3,
        )

    def test_primary_consensus_rejects_exact_configuration_mismatch(self):
        rankings = consensus_fixture_rankings({"a": (1, 1)})
        rankings["rasch_sparse_item_sensitivity"][0]["slug"] = (
            "model-a-other-config"
        )
        pool_sizes = {board_id: 4 for board_id in base.BOARD_ORDER}

        with self.assertRaisesRegex(ValueError, "cannot mix exact configurations"):
            build_twopl_sparse_rank_consensus(
                rankings,
                primary_pool_sizes=pool_sizes,
                sparse_pool_sizes=pool_sizes,
            )

    def test_primary_consensus_publication_has_required_order_only(self):
        evidence_rows = self.result["consensus_full_rankings"]
        published_rows = self.result["publication_consensus_full_rankings"]
        evidence_by_id = {
            ranking_row_id(row): row for row in evidence_rows
        }

        self.assertEqual(published_rows[0]["slug"], "claude-fable-5")
        self.assertEqual(published_rows[0]["rank"], 1)
        self.assertEqual(published_rows[1]["variant_group"], "gpt 5 6 sol")
        self.assertEqual(published_rows[1]["rank"], 2)
        for published in published_rows:
            evidence = evidence_by_id[ranking_row_id(published)]
            self.assertEqual(published["score"], evidence["score"])
            self.assertEqual(published["evidence_rank"], evidence["rank"])

        def non_anchor_ids(rows):
            return [
                ranking_row_id(row)
                for row in rows
                if row["slug"] != "claude-fable-5"
                and row["variant_group"] != "gpt 5 6 sol"
            ]

        self.assertEqual(
            non_anchor_ids(published_rows),
            non_anchor_ids(evidence_rows),
        )
        self.assertTrue(
            self.result["consensus_publication_validation"][
                "all_methods_pass"
            ]
        )

    def test_primary_consensus_exposes_shadow_methods_and_board_scores(self):
        for row in self.result["consensus_full_rankings"]:
            for prefix in ("rasch", "twopl", "dense_rasch"):
                self.assertIsInstance(row[f"{prefix}_rank"], int)
                self.assertIsInstance(row[f"{prefix}_score"], float)
            self.assertEqual(
                set(row["component_methods"]),
                {
                    "rasch_equal_board",
                    "rasch_sparse_item_sensitivity",
                    "twopl_equal_board",
                    "rasch_dense_item_sensitivity",
                },
            )
            for board_id in base.BOARD_ORDER:
                self.assertEqual(
                    row[f"{board_id}_score"],
                    base.rounded(
                        0.70 * row[f"{board_id}_twopl_score"]
                        + 0.30 * row[f"{board_id}_sparse_rasch_score"],
                        3,
                    ),
                )
                self.assertIn(f"{board_id}_rasch_score", row)
                self.assertIn(f"{board_id}_twopl_score", row)
                self.assertIn(f"{board_id}_dense_rasch_score", row)

    def test_primary_consensus_evidence_coverage_formula_and_range(self):
        primary_method = "twopl_equal_board"
        sparse_method = "rasch_sparse_item_sensitivity"
        pools = self.result["summary"]["board_item_pool_sizes"]

        for row in self.result["consensus_full_rankings"]:
            board_coverages = []
            for board_id in base.BOARD_ORDER:
                primary_share = (
                    row[f"{board_id}_twopl_tests"]
                    / pools[primary_method][board_id]
                )
                sparse_share = (
                    row[f"{board_id}_sparse_rasch_tests"]
                    / pools[sparse_method][board_id]
                )
                expected_board = 100.0 * (
                    0.70 * primary_share + 0.30 * sparse_share
                )
                board_coverages.append(expected_board)
                self.assertEqual(
                    row[f"{board_id}_evidence_coverage_score"],
                    base.rounded(expected_board, 3),
                )
            self.assertEqual(
                row["evidence_coverage_score"],
                base.rounded(float(np.mean(board_coverages)), 3),
            )
            self.assertGreaterEqual(row["evidence_coverage_score"], 0)
            self.assertLessEqual(row["evidence_coverage_score"], 100)

        self.assertEqual(
            self.result["summary"]["consensus_method"]["component_weights"],
            dict(CONSENSUS_COMPONENT_WEIGHTS),
        )

    def test_publication_layer_preserves_scores_and_evidence_ranks(self):
        for method in METHOD_LABELS:
            evidence_rows = self.result["full_rankings"][method]
            published_rows = self.result["required_order_full_rankings"][method]
            evidence_by_id = {
                ranking_row_id(row): row for row in evidence_rows
            }
            published_by_id = {
                ranking_row_id(row): row for row in published_rows
            }
            self.assertEqual(set(published_by_id), set(evidence_by_id))
            for row_id, published in published_by_id.items():
                evidence_row = evidence_by_id[row_id]
                self.assertEqual(published["score"], evidence_row["score"])
                self.assertEqual(
                    published["evidence_rank"], evidence_row["rank"]
                )
                self.assertEqual(
                    published["rank_change_due_to_required_order"],
                    published["evidence_rank"] - published["rank"],
                )
                self.assertEqual(
                    published["publication_order_rule"], PUBLICATION_RULE_ID
                )

    def test_publication_layer_preserves_every_other_relative_order(self):
        for method in METHOD_LABELS:
            evidence_rows = self.result["full_rankings"][method]
            published_rows = self.result["required_order_full_rankings"][method]

            def non_anchor_ids(rows):
                return [
                    ranking_row_id(row)
                    for row in rows
                    if row["slug"] != "claude-fable-5"
                    and row["variant_group"] != "gpt 5 6 sol"
                ]

            self.assertEqual(
                non_anchor_ids(published_rows), non_anchor_ids(evidence_rows)
            )

    def test_publication_targets_use_stable_ids_not_display_names(self):
        evidence_rows = [
            {
                "rank": 1,
                "model": "Claude Fable 5 impostor",
                "slug": "unrelated-first",
                "variant_group": "unrelated first",
                "score": 100.0,
            },
            {
                "rank": 2,
                "model": "GPT-5.6 Sol impostor",
                "slug": "unrelated-second",
                "variant_group": "unrelated second",
                "score": 99.0,
            },
            {
                "rank": 3,
                "model": "Renamed Sol display label",
                "slug": "gpt-5-6-sol-xhigh",
                "variant_group": "gpt 5 6 sol",
                "score": 98.0,
            },
            {
                "rank": 4,
                "model": "Renamed Fable display label",
                "slug": "claude-fable-5",
                "variant_group": "renamed fable display label",
                "score": 97.0,
            },
        ]
        original = [dict(row) for row in evidence_rows]
        published = apply_required_publication_order(evidence_rows)

        self.assertEqual(published[0]["slug"], "claude-fable-5")
        self.assertEqual(published[1]["variant_group"], "gpt 5 6 sol")
        self.assertEqual(
            [row["slug"] for row in published[2:]],
            ["unrelated-first", "unrelated-second"],
        )
        self.assertEqual(evidence_rows, original)

    def test_required_order_files_are_the_validated_publication_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)
            result = run_multi_method_analysis(output_dir=output_dir)

            with (output_dir / "required_order_multi_method_top50.csv").open(
                encoding="utf-8-sig", newline=""
            ) as handle:
                combined = list(csv.DictReader(handle))
            self.assertEqual(len(combined), 50 * len(METHOD_LABELS))
            for method in METHOD_LABELS:
                rows = [row for row in combined if row["method"] == method]
                self.assertEqual(len(rows), 50)
                self.assertEqual(rows[0]["slug"], "claude-fable-5")
                self.assertEqual(rows[0]["rank"], "1")
                self.assertEqual(rows[1]["variant_group"], "gpt 5 6 sol")
                self.assertEqual(rows[1]["rank"], "2")
                with (
                    output_dir / f"top50_required_{method}.csv"
                ).open(encoding="utf-8-sig", newline="") as handle:
                    per_method_rows = list(csv.DictReader(handle))
                self.assertEqual(rows, per_method_rows)

            validation = json.loads(
                (output_dir / "required_order_validation_summary.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertTrue(validation["all_methods_pass"])
            self.assertEqual(validation, result["required_order_validation"])

            consensus_paths = {
                "full": output_dir
                / f"full_rankings_{CONSENSUS_METHOD}.csv",
                "top50": output_dir / f"top50_{CONSENSUS_METHOD}.csv",
                "published_full": output_dir
                / f"full_rankings_required_{CONSENSUS_METHOD}.csv",
                "published_top50": output_dir
                / f"top50_required_{CONSENSUS_METHOD}.csv",
            }
            consensus_rows = {}
            for key, path in consensus_paths.items():
                with path.open(encoding="utf-8-sig", newline="") as handle:
                    consensus_rows[key] = list(csv.DictReader(handle))
            expected_population = len(result["consensus_full_rankings"])
            self.assertEqual(len(consensus_rows["full"]), expected_population)
            self.assertEqual(len(consensus_rows["top50"]), 50)
            self.assertEqual(
                len(consensus_rows["published_full"]),
                expected_population,
            )
            self.assertEqual(len(consensus_rows["published_top50"]), 50)
            self.assertEqual(
                consensus_rows["published_top50"][0]["slug"],
                "claude-fable-5",
            )
            self.assertEqual(
                consensus_rows["published_top50"][1]["variant_group"],
                "gpt 5 6 sol",
            )

            consensus_validation = json.loads(
                (
                    output_dir
                    / "consensus_publication_validation_summary.json"
                ).read_text(encoding="utf-8")
            )
            self.assertTrue(consensus_validation["all_methods_pass"])
            self.assertEqual(
                consensus_validation,
                result["consensus_publication_validation"],
            )

    def test_equal_board_aggregation_is_exact_arithmetic_mean(self):
        board_scores = {
            board_id: np.asarray([float(position), float(position + 10)])
            for position, board_id in enumerate(base.BOARD_ORDER, start=1)
        }
        actual = equal_board_mean(board_scores)
        expected = np.mean(
            np.column_stack(
                [board_scores[board_id] for board_id in base.BOARD_ORDER]
            ),
            axis=1,
        )
        np.testing.assert_allclose(actual, expected, rtol=0.0, atol=0.0)

    def test_core_item_gate_uses_independent_groups_and_creators(self):
        payload = json.loads(DEFAULT_INPUT.read_text(encoding="utf-8"))
        models, _ = sanitize_models(payload)
        board_data = prepare_common_matrix(models)
        for board in board_data.values():
            self.assertTrue(np.all(board["n_variant_groups"] >= 8))
            self.assertTrue(np.all(board["n_creators"] >= 3))

    def test_fixed_exact_config_comparison_does_not_switch_effort(self):
        sol_rows = [
            row
            for row in self.result["target_exact_configs"]
            if row["target"] == "gpt_5_6_sol"
        ]
        self.assertEqual(len(sol_rows), len(METHOD_LABELS))
        self.assertTrue(all(row["model"] == "GPT-5.6 Sol (max)" for row in sol_rows))
        self.assertTrue(all(row["slug"] == "gpt-5-6-sol" for row in sol_rows))

    def test_pairwise_overlap_audit_reproduces_luna_deepseek_closeness(self):
        rows = [
            row
            for row in self.result["pairwise_overlap"]
            if row["pair"] == "luna_vs_deepseek"
        ]
        self.assertEqual(len(rows), 9)
        self.assertEqual(sum(row["winner"] == "left" for row in rows), 7)
        self.assertEqual(sum(row["winner"] == "right" for row in rows), 2)

    def test_first_party_source_coverage_distinguishes_stored_from_used_rows(self):
        by_model = {
            row["model"]: row for row in self.result["source_coverage"]
        }
        expected = {
            "Claude Fable 5 (with fallback)": (14, 7),
            "Claude Opus 5 (max)": (7, 5),
            "DeepSeek V4 Flash 0731 (max)": (7, 2),
            "GPT-5.6 Sol (max)": (37, 5),
            "GPT-5.6 Terra (max)": (37, 5),
            "GPT-5.6 Luna (max)": (37, 5),
        }
        for model, (stored, used) in expected.items():
            self.assertEqual(by_model[model]["first_party_direct_rows"], stored)
            self.assertEqual(
                by_model[model]["first_party_rows_in_common_protocol"], used
            )

    def test_row_order_and_brand_label_do_not_change_scores_or_ranks(self):
        payload = json.loads(DEFAULT_INPUT.read_text(encoding="utf-8"))
        payload["models"].reverse()
        source_model = next(
            model
            for model in payload["models"]
            if model.get("slug") == "qwen3-8-max"
        )
        source_model["model"] = "Anonymous evaluation configuration"
        source_model["creator"] = "Anonymous"

        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "anonymous-reversed-models.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")
            rerun = run_multi_method_analysis(
                input_path=input_path,
                write_outputs=False,
            )

        for method in METHOD_LABELS:
            original = next(
                row
                for row in self.result["full_rankings"][method]
                if row["slug"] == "qwen3-8-max"
            )
            anonymized = next(
                row
                for row in rerun["full_rankings"][method]
                if row["slug"] == "qwen3-8-max"
            )
            self.assertEqual(anonymized["rank"], original["rank"])
            self.assertEqual(anonymized["score"], original["score"])


if __name__ == "__main__":
    unittest.main()
