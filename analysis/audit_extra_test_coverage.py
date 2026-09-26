"""Report exact-config and fitting coverage for the current Extra Tests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics

from analysis.irt_leaderboard_exploration import aindex_mixed_core as scoring
from analysis.irt_leaderboard_exploration.mixed_core_extension_policy import CURRENT_EXTENSION_POLICIES


ROOT = Path(__file__).resolve().parents[1]


def audit(payload: dict) -> list[dict]:
    exact_models = scoring.source_models(payload)
    eligible, _ = scoring.prepare(scoring.representatives(exact_models))
    calibration = scoring.fit_calibration(eligible)
    current_policies = {policy.score_key: policy for policy in CURRENT_EXTENSION_POLICIES}
    rows = []
    for board, keys in scoring.EXTENSION_ITEMS.items():
        trends = {item["score_key"]: item for item in calibration["boards"][board]["extension_items"]}
        complete = [model for model in eligible
                    if all(scoring.score_value(model, core) is not None
                           for core in scoring.CORE_ITEMS[board])]
        for key in keys:
            scored = [(model, scoring.score_value(model, key)) for model in complete]
            scored = [(model, value) for model, value in scored if value is not None]
            exact_count = sum(scoring.score_value(model, key) is not None for model in exact_models)
            fit_count = len(scored)
            if fit_count != trends[key]["observed_count"] or not trends[key]["enabled"]:
                raise AssertionError(f"Extra fit mismatch or disabled metric: {key}")
            policy = current_policies.get(key)
            creators = len({str(model.get("creator") or "") for model, _ in scored})
            if policy and (policy.observed_groups != fit_count or policy.observed_creators != creators):
                raise AssertionError(f"Stale Extra policy coverage: {key}")
            rows.append({
                "board": board,
                "score_key": key,
                "exact_configs": exact_count,
                "fit_representatives": fit_count,
                "fit_creators": creators,
                "fit_median": statistics.median(value for _, value in scored),
            })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "docs/data/models.json")
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    rows = audit(payload)
    print("| Board | Extra Test key | Exact configs | Fit representatives / creators | Fit median |")
    print("| --- | --- | ---: | ---: | ---: |")
    for row in rows:
        print(f"| {row['board']} | `{row['score_key']}` | {row['exact_configs']} | "
              f"{row['fit_representatives']} / {row['fit_creators']} | {row['fit_median']:.2f}% |")


if __name__ == "__main__":
    main()
