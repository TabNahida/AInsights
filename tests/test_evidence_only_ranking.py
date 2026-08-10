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
    build_twopl_sparse_score_consensus,
    equal_board_mean,
    prepare_common_matrix,
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
    component_scores: dict[str, tuple[float, float]] | None = None,
) -> dict[str, list[dict]]:
    rankings = {
        "rasch_equal_board": [],
        "rasch_sparse_item_sensitivity": [],
        "twopl_equal_board": [],
        "rasch_dense_item_sensitivity": [],
    }
    for group, (twopl_rank, sparse_rank) in component_ranks.items():
        slug = f"model-{group}"
        twopl_score, sparse_score = (
            component_scores[group]
            if component_scores is not None
            else (100.0 - twopl_rank, 100.0 - sparse_rank)
        )
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
        for method in ("rasch_equal_board", "twopl_equal_board"):
            rankings[method][-1]["score"] = twopl_score
            for board_id in base.BOARD_ORDER:
                rankings[method][-1][f"{board_id}_score"] = twopl_score
        for method in (
            "rasch_sparse_item_sensitivity",
            "rasch_dense_item_sensitivity",
        ):
            rankings[method][-1]["score"] = sparse_score
            for board_id in base.BOARD_ORDER:
                rankings[method][-1][f"{board_id}_score"] = sparse_score
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

    def test_exact_config_sanitizer_removes_unscoped_family_results(self):
        payload = {
            "models": [
                {
                    "model": "Synthetic",
                    "scores": {
                        "benchmark:family": 88.0,
                        "benchmark:exact": 91.0,
                    },
                    "externalBenchmarks": [
                        {
                            "metricKey": "benchmark:family",
                            "variantScoped": False,
                        },
                        {
                            "metricKey": "benchmark:exact",
                            "variantScoped": True,
                        },
                    ],
                }
            ]
        }

        family_models, _ = sanitize_models(payload)
        exact_models, exact_summary = sanitize_models(
            payload,
            exact_config_only=True,
        )

        self.assertEqual(
            family_models[0]["scores"]["benchmark:family"],
            88.0,
        )
        self.assertIsNone(
            exact_models[0]["scores"]["benchmark:family"]
        )
        self.assertEqual(
            exact_models[0]["scores"]["benchmark:exact"],
            91.0,
        )
        self.assertEqual(
            exact_summary["unscoped_external_score_cells_removed"],
            1,
        )


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
            "no product/model constraints; no named-model corrections; no fixed "
            "missing-score penalty; score descending is the only ranking rule",
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

    def test_primary_consensus_uses_80_20_score_and_contiguous_population(self):
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
        recomputed_scores = []
        for row in rows:
            self.assertEqual(
                row["rank_mean"],
                base.rounded(
                    0.80 * row["twopl_rank"]
                    + 0.20 * row["sparse_rasch_rank"],
                    4,
                ),
            )
            self.assertEqual(row["rank_weighted_mean"], row["rank_mean"])
            self.assertEqual(
                row["score"],
                base.rounded(
                    0.80 * row["twopl_score"]
                    + 0.20 * row["sparse_rasch_score"],
                    4,
                ),
            )
            recomputed_scores.append(
                0.80 * row["twopl_score"]
                + 0.20 * row["sparse_rasch_score"]
            )
            self.assertEqual(
                row["rank_mean_role"],
                "audit_only_not_ranking_key",
            )
        self.assertTrue(
            all(
                left >= right
                for left, right in zip(
                    recomputed_scores,
                    recomputed_scores[1:],
                )
            )
        )
        self.assertEqual(
            self.result["summary"]["default_consensus_method"],
            "aindex_scheme18",
        )
        self.assertEqual(
            self.result["summary"]["default_ranking_method"],
            "aindex_scheme18",
        )
        self.assertEqual(
            CONSENSUS_METHOD,
            "twopl_sparse_80_20_score",
        )

    def test_primary_consensus_ranks_by_score_not_component_rank_mean(self):
        rankings = consensus_fixture_rankings(
            {
                "a": (1, 5),
                "b": (2, 1),
                "c": (1, 6),
            },
            {
                "a": (91.0, 91.0),
                "b": (95.0, 95.0),
                "c": (91.0, 91.0),
            },
        )
        pool_sizes = {board_id: 4 for board_id in base.BOARD_ORDER}

        rows = build_twopl_sparse_score_consensus(
            rankings,
            primary_pool_sizes=pool_sizes,
            sparse_pool_sizes=pool_sizes,
        )

        self.assertEqual(
            [row["variant_group"] for row in rows],
            ["b", "a", "c"],
        )
        self.assertEqual([row["score"] for row in rows], [95.0, 91.0, 91.0])
        self.assertEqual([row["rank_mean"] for row in rows], [1.8, 1.8, 2.0])
        self.assertEqual(
            [row["rank_tie_break_policy"] for row in rows],
            ["higher_score_then_stable_id"] * 3,
        )

    def test_primary_consensus_rejects_exact_configuration_mismatch(self):
        rankings = consensus_fixture_rankings({"a": (1, 1)})
        rankings["rasch_sparse_item_sensitivity"][0]["slug"] = (
            "model-a-other-config"
        )
        pool_sizes = {board_id: 4 for board_id in base.BOARD_ORDER}

        with self.assertRaisesRegex(ValueError, "cannot mix exact configurations"):
            build_twopl_sparse_score_consensus(
                rankings,
                primary_pool_sizes=pool_sizes,
                sparse_pool_sizes=pool_sizes,
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
                        0.80 * row[f"{board_id}_twopl_score"]
                        + 0.20 * row[f"{board_id}_sparse_rasch_score"],
                        3,
                    ),
                )
                self.assertIn(f"{board_id}_rasch_score", row)
                self.assertIn(f"{board_id}_twopl_score", row)
                self.assertIn(f"{board_id}_dense_rasch_score", row)

    def test_exact_config_population_exposes_every_eligible_tier(self):
        rows = self.result["exact_config_consensus_full_rankings"]
        summary = self.result["summary"]
        deduped_gpt55 = next(
            row
            for row in self.result["consensus_full_rankings"]
            if row["variant_group"] == "gpt 5 5"
        )

        self.assertEqual(deduped_gpt55["slug"], "gpt-5-5")
        self.assertEqual(deduped_gpt55["evidence_tier"], "Main")

        self.assertEqual(len(rows), summary["ranked_exact_config_rows"])
        self.assertEqual(
            len(rows) - len(self.result["consensus_full_rankings"]),
            summary["exact_config_population_net_change"],
        )
        self.assertGreater(
            summary["exact_config_sanitation"][
                "unscoped_external_score_cells_removed"
            ],
            0,
        )
        self.assertEqual(len({row["slug"] for row in rows}), len(rows))
        self.assertTrue(all(row["ranking_grain"] == "exact_config" for row in rows))
        for method_rows in self.result["exact_config_full_rankings"].values():
            self.assertEqual(
                {row["slug"] for row in method_rows},
                {row["slug"] for row in rows},
            )

        gpt55 = {
            row["slug"]: row
            for row in rows
            if row["variant_group"] == "gpt 5 5"
        }
        self.assertEqual(
            set(gpt55),
            {
                "gpt-5-5",
                "gpt-5-5-high",
                "gpt-5-5-medium",
                "gpt-5-5-low",
                "gpt-5-5-non-reasoning",
            },
        )
        self.assertLess(
            gpt55["gpt-5-5"]["rank"],
            gpt55["gpt-5-5-high"]["rank"],
        )
        self.assertGreater(
            gpt55["gpt-5-5"]["score"],
            gpt55["gpt-5-5-high"]["score"],
        )
        self.assertEqual(
            [row["rank"] for row in rows],
            list(range(1, len(rows) + 1)),
        )
        self.assertTrue(
            self.result["exact_config_score_order_validation"][
                "all_methods_pass"
            ]
        )
        visibility = self.result["exact_config_visibility"]
        self.assertEqual(len(visibility), len(rows))
        self.assertEqual(
            sum(row["recovered_when_dedupe_disabled"] for row in visibility),
            summary["eligible_exact_configs_hidden_by_group_collapse"],
        )
        recovered_gpt55 = {
            row["slug"]
            for row in visibility
            if row["variant_group"] == "gpt 5 5"
            and row["recovered_when_dedupe_disabled"]
        }
        self.assertEqual(
            recovered_gpt55,
            {
                "gpt-5-5-high",
                "gpt-5-5-medium",
                "gpt-5-5-low",
                "gpt-5-5-non-reasoning",
            },
        )

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
                    0.80 * primary_share + 0.20 * sparse_share
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

    def test_score_order_files_are_the_validated_primary_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)
            result = run_multi_method_analysis(output_dir=output_dir)

            consensus_paths = {
                "full": output_dir
                / f"full_rankings_{CONSENSUS_METHOD}.csv",
                "top50": output_dir / f"top50_{CONSENSUS_METHOD}.csv",
                "exact_full": output_dir
                / f"full_rankings_exact_config_{CONSENSUS_METHOD}.csv",
                "exact_top50": output_dir
                / f"top50_exact_config_{CONSENSUS_METHOD}.csv",
            }
            consensus_rows = {}
            for key, path in consensus_paths.items():
                with path.open(encoding="utf-8-sig", newline="") as handle:
                    consensus_rows[key] = list(csv.DictReader(handle))
            expected_population = len(result["consensus_full_rankings"])
            self.assertEqual(len(consensus_rows["full"]), expected_population)
            self.assertEqual(len(consensus_rows["top50"]), 50)
            self.assertEqual(
                len(consensus_rows["exact_full"]),
                len(result["exact_config_consensus_full_rankings"]),
            )
            self.assertEqual(len(consensus_rows["exact_top50"]), 50)
            for key in ("full", "exact_full"):
                rows = consensus_rows[key]
                self.assertEqual(
                    [int(row["rank"]) for row in rows],
                    list(range(1, len(rows) + 1)),
                )
                scores = [float(row["score"]) for row in rows]
                self.assertTrue(
                    all(left >= right for left, right in zip(scores, scores[1:]))
                )
                for row in rows:
                    self.assertNotIn("publication_order_rule", row)
                    self.assertNotIn("required_order_target", row)

            validation = json.loads(
                (output_dir / "score_order_validation_summary.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(
                validation["variant_group_consensus"],
                result["consensus_score_order_validation"],
            )
            self.assertEqual(
                validation["exact_config_consensus"],
                result["exact_config_score_order_validation"],
            )
            self.assertTrue(validation["variant_group_consensus"]["all_methods_pass"])
            self.assertTrue(validation["exact_config_consensus"]["all_methods_pass"])
            self.assertFalse(
                (output_dir / "required_order_multi_method_top50.csv").exists()
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
