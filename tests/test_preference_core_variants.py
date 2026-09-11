import copy
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from analysis.irt_leaderboard_exploration import preference_core_variants as p


def score_row(slug, values):
    row = {"slug": slug, "model": slug, "score": sum(values) / 5}
    for board, value in zip(p.BOARDS, values):
        row[board + "_score"] = value
        row[board + "_core"] = value
    return row


class PreferenceCoreVariantsTests(unittest.TestCase):
    def test_weights_apply_to_scores_and_core_identically(self):
        rows = [score_row("a", [10, 20, 30, 40, 50]), score_row("b", [20]*5)]
        original = copy.deepcopy(rows)
        result = p.weighted_rows(rows, [10, 15, 30, 25, 20])
        self.assertEqual(result[0]["score"], 33)
        self.assertEqual(result[0]["core_only_score"], 33)
        self.assertEqual(result[0]["rank"], 1)
        self.assertEqual(rows, original)

    def test_renaming_models_or_providers_does_not_change_score(self):
        rows = [score_row("a", [25, 60, 40, 30, 80]), score_row("b", [65, 50, 30, 20, 90])]
        first = p.weighted_rows(rows, p.VARIANTS["e_small_change"]["weights"])
        for i, row in enumerate(rows):
            row["model"] = p.TARGETS[i]
            row["creator"] = "Arbitrary renamed provider"
        second = p.weighted_rows(rows, p.VARIANTS["e_small_change"]["weights"])
        self.assertEqual([(r["slug"], r["score"]) for r in first], [(r["slug"], r["score"]) for r in second])

    def test_invalid_weights_are_rejected(self):
        for weights in ([20]*4, [20]*4+[21], [-10, 20, 30, 30, 30], [float("nan"), 25, 25, 25, 25]):
            with self.subTest(weights=weights), self.assertRaises(ValueError):
                p.weighted_rows([], weights)

    def test_audit_requires_all_targets_and_actual_first_two_positions(self):
        # Synthetic scores verify the audit; current real-world rankings are
        # NOT assertions in CI, so future AA refreshes cannot enforce preferences.
        values = [99, 98, 95, 94, 97, 96, 93, 92, 91]
        rows = p.weighted_rows([score_row(t, [v]*5) for t, v in zip(p.TARGETS, values)], [20]*5)
        self.assertTrue(p.constraint_audit(rows)["passed"])
        snapshot = copy.deepcopy(rows)
        audit = p.constraint_audit(rows[:-1])
        self.assertFalse(audit["passed"])
        self.assertIn(p.TARGETS[-1], audit["missing_targets"])
        self.assertEqual(rows, snapshot)
        competitor = p.weighted_rows(rows + [score_row("competitor", [98.5]*5)], [20]*5)
        self.assertFalse(p.constraint_audit(competitor)["passed"])

    def test_margin_cannot_be_satisfied_by_rounding_or_id_ties(self):
        values = [99, 98, 95, 94.99, 97, 96, 93, 92, 91]
        rows = p.weighted_rows([score_row(t, [v]*5) for t, v in zip(p.TARGETS, values)], [20]*5)
        self.assertFalse(p.constraint_audit(rows)["passed"])

    def test_exports_keep_inputs_immutable_and_scores_consistent(self):
        inputs = [p.base.ROOT / "docs/data/models.json", p.base.ROOT / "ArtificialAnalysis/artificialanalysis_raw_scores_wide.csv"]
        hashes = [hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs]
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            p.run(*inputs, output)
            metadata = json.loads((output / "run.json").read_text(encoding="utf-8"))
            common = []
            for key, variant in p.VARIANTS.items():
                with (output / f"rankings_{key}.csv").open(encoding="utf-8") as handle:
                    rows = list(csv.DictReader(handle))
                self.assertEqual([float(r["score"]) for r in rows], sorted((float(r["score"]) for r in rows), reverse=True))
                for row in rows:
                    expected = sum(float(row[b+"_score"]) * w / 100 for b, w in zip(p.BOARDS, variant["weights"]))
                    self.assertAlmostEqual(float(row["score"]), expected)
                with (output / f"common_{key}.csv").open(encoding="utf-8") as handle:
                    common.append({r["slug"] for r in csv.DictReader(handle)})
                self.assertEqual(metadata["results"][key]["sensitivity"]["total"], 20)
            self.assertTrue(all(s == common[0] for s in common))
            self.assertEqual(len(common[0]), metadata["common_population"])
        self.assertEqual(hashes, [hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs])


if __name__ == "__main__":
    unittest.main()
