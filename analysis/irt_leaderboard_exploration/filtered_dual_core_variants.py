"""Publish only two-Core proposals passing every user ranking preference.

Search first checks the original 10--40% board bounds, then 9--40% if needed,
with 1pp resolution. Terminal uses v4 observations only. Desired model order is
a proposal filter, not a score term. Never use this as a daily named-rank gate.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
import sys

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from analysis.irt_leaderboard_exploration import dual_core_variants as dual

base, preferences, BOARDS = dual.base, dual.preferences, dual.BOARDS
OUTPUT = Path(__file__).resolve().parent / "outputs" / "filtered_dual_core_v4"
CURRENT_TARGETS = preferences.TARGETS + (
    "gpt-5-6-sol", "claude-opus-5", "gpt-5-6-terra", "grok-4-6-xhigh", "grok-4-5",
)
CURRENT_PAIRS = preferences.PAIRS + ((9, 10), (11, 5), (12, 13))
CURRENT_LABELS = (
    "Fable 5.1 第一", "GPT-6 Astra 第二", "Kimi K3 高于 Gemini 3.8 Flash",
    "GPT-5.5 高于 Muse Spark 1.3", "Qwen3.8 Max 高于 Qwen3.8 Flash-Next",
    "Qwen3.8 2.4T A95B 高于 Qwen3.8 Flash-Next", "GPT-5.6 Sol 高于 Claude Opus 5",
    "GPT-5.6 Terra 高于 Muse Spark 1.3", "Grok 4.6 高于 Grok 4.5",
)
AUDIT_KWARGS = {"targets": CURRENT_TARGETS, "pairs": CURRENT_PAIRS, "labels": CURRENT_LABELS}
EXCLUDED_VARIANT_GROUPS = ()
CORE_OPTIONS = (
    ((base.LATEST_TB, "SciCode"), (base.LATEST_TB, "LiveCodeBench")),
    (("AutomationBench-AA", "τ³-Banking"), ("AutomationBench-AA", "AA-Briefcase"),
     ("τ³-Banking", "AA-Briefcase"), ("AutomationBench-AA", "GDPval-AA v2"),
     ("τ²-Bench Telecom", "τ³-Banking")),
    (("CritPt", "Humanity's Last Exam"), ("CritPt", "GPQA Diamond"),
     ("Humanity's Last Exam", "GPQA Diamond"), ("CritPt", "AIME 2025")),
    (("AA-Omniscience Accuracy", "GPQA Diamond"), ("AA-Omniscience Accuracy", "MMMU-Pro"),
     ("AA-Omniscience Accuracy", "Humanity's Last Exam")),
    (("AA-LCR v1.1", "GDP.pdf"), ("AA-LCR v1.1", "IFBench")),
)


def weight_grid(values=range(10, 41)):
    values = tuple(values)
    allowed = set(values)
    return np.asarray([(*head, 100 - sum(head))
                       for head in itertools.product(values, repeat=4)
                       if 100 - sum(head) in allowed], dtype=float).reshape(-1, 5)


def passing_weight_indices(rows, weights, margin=preferences.MIN_MARGIN, *,
                           targets=preferences.TARGETS, pairs=preferences.PAIRS):
    """Screen linear score differences, including Astra against the whole field."""
    index = {row["slug"]: i for i, row in enumerate(rows)}
    if not set(targets) <= set(index):
        return np.array([], dtype=int)
    values = np.asarray([[row[b + "_score"] for b in BOARDS] for row in rows])
    target = [index[slug] for slug in targets]
    remaining = np.arange(len(weights))
    # The most selective pair goes first solely to reduce matrix work.
    for a, b in (*pairs, (0, 1)):
        gap = weights[remaining] @ (values[target[a]] - values[target[b]]) / 100
        remaining = remaining[gap > margin]
        if not len(remaining):
            return remaining
    for i in range(len(rows)):
        if i in target[:2]:
            continue
        gap = weights[remaining] @ (values[target[1]] - values[i]) / 100
        remaining = remaining[gap > margin]
        if not len(remaining):
            break
    return remaining


def core_signature(core):
    return tuple(tuple(core[board]) for board in BOARDS)


def search_candidates(models, maps, *, values=range(10, 41), options=CORE_OPTIONS,
                      minimum_population=100):
    models = [m for m in models if m["variantGroup"] not in EXCLUDED_VARIANT_GROUPS]
    grid = weight_grid(values)
    candidates, valid, skipped, evaluated = [], 0, 0, 0
    coarse_count = 0
    for pairs in itertools.product(*options):
        core = dict(zip(BOARDS, pairs))
        try:
            dual.validate_core(core)
        except ValueError:
            continue
        valid += 1
        rows, _, calibration, eligible = dual.score_variant(models, core, [20]*5, maps, "v4_only")
        if len(rows) < minimum_population or not set(CURRENT_TARGETS) <= {r["slug"] for r in rows}:
            skipped += 1
            continue
        evaluated += len(grid)
        for j in passing_weight_indices(rows, grid, targets=CURRENT_TARGETS, pairs=CURRENT_PAIRS):
            weights = grid[j].astype(int).tolist()
            ranked = dual.score_models(eligible, core, weights, calibration)
            audit = preferences.constraint_audit(ranked, **AUDIT_KWARGS)
            if not audit["passed"]:
                # Reject floating-point boundary disagreements as well.
                continue
            sensitivity = preferences.weight_sensitivity(ranked, weights, **AUDIT_KWARGS)
            candidate = {"core": core, "weights": weights, "population": len(rows),
                         "minimum_margin": audit["minimum_margin"],
                         "distance_from_equal": sum(abs(w - 20) for w in weights),
                         "sensitivity_passing": sensitivity["passing"],
                         "sensitivity_total": sensitivity["total"],
                         "missing_core_total": sum(r["missing_core_count"] for r in rows)}
            candidates.append(candidate)
            coarse_count += all(w % 5 == 0 for w in weights)
    candidates.sort(key=lambda c: (core_signature(c["core"]), tuple(c["weights"])))
    return {
        "core_combinations": int(np.prod([len(group) for group in options])),
        "valid_core_combinations": valid, "skipped_core_combinations": skipped,
        "weight_vectors": len(grid), "weight_range": [min(values), max(values)],
        "weight_step": int(min(np.diff(sorted(values)))) if len(values) > 1 else None,
        "weight_grid_percent": f"{min(values)}%–{max(values)}%，{int(min(np.diff(sorted(values)))) if len(values) > 1 else 0} 个百分点步长，五领域合计 100%",
        "evaluated_core_weight_combinations": evaluated,
        "passing_combinations": len(candidates),
        "distinct_core_combinations": len({core_signature(c["core"]) for c in candidates}),
        "coarse_5pp_passing_combinations": coarse_count,
        "minimum_population": minimum_population, "minimum_margin": preferences.MIN_MARGIN,
        "core_options": dict(zip(BOARDS, options)), "candidates": candidates,
    }


SELECTION_ROLES = (
    ("接近等权", "在尚未入选的合格候选中，优先选择与五领域等权偏离最小的权重。"),
    ("分差优先", "在尚未入选的合格候选中，优先选择九项筛选的最小分差较大的权重。"),
    ("扰动对照", "在尚未入选的合格候选中，优先选择 1 个百分点权重转移后仍通过次数最多的权重。"),
    ("Agent 保留", "在尚未入选的合格候选中，优先保留较高的 Agent 领域权重。"),
    ("权重差异对照", "在尚未入选的合格候选中，选择与本组已入选方案最小权重距离最大的方案，增加比较差异。"),
)


def select_candidates(search, count=10):
    """Keep distinct structures represented, then select distinct weight variants."""
    grouped = {}
    for candidate in search["candidates"]:
        grouped.setdefault(core_signature(candidate["core"]), []).append(candidate)
    groups = sorted(grouped.values(), key=lambda g: (g[0]["core"]["coding"][1] != "SciCode",
                                                    core_signature(g[0]["core"])))
    chosen_by_group = [[] for _ in groups]
    for slot in range(count):
        before = sum(map(len, chosen_by_group))
        for group, chosen in zip(groups, chosen_by_group):
            if sum(map(len, chosen_by_group)) >= count:
                break
            available = [c for c in group if c not in chosen]
            if not available:
                continue
            tie = lambda c: (-c["minimum_margin"], tuple(c["weights"]))
            if slot == 0:
                key = lambda c: (c["distance_from_equal"], *tie(c))
            elif slot == 1:
                key = tie
            elif slot == 2:
                key = lambda c: (-c["sensitivity_passing"], *tie(c))
            elif slot == 3:
                key = lambda c: (-c["weights"][1], *tie(c))
            else:
                key = lambda c: (-min(sum(abs(a-b) for a, b in zip(c["weights"], old["weights"]))
                                     for old in chosen), *tie(c))
            pick = min(available, key=key)
            chosen.append(pick)
        if sum(map(len, chosen_by_group)) == before:
            break
    return [(candidate, SELECTION_ROLES[min(i, len(SELECTION_ROLES)-1)]) for group in chosen_by_group
            for i, candidate in enumerate(group)]


def make_variants(selected):
    variants = {}
    for i, (candidate, (role, reason)) in enumerate(selected, 1):
        coding = candidate["core"]["coding"][1]
        coding_label = "科学编程" if coding == "SciCode" else "算法编程"
        agent_pair = "＋".join(candidate["core"]["agentic-tool-work"])
        elo_note = ("其中含 Elo 换算分。" if any(k in {"AA-Briefcase", "GDPval-AA v2"}
                    for k in candidate["core"]["agentic-tool-work"]) else "")
        variants[f"fc{i:02d}"] = {
            "label": f"{i:02d} {coding_label}·{role}",
            "purpose": reason + "全部模型使用相同权重，九项排序标准只在计分后筛选方案。",
            "tradeoff": ("该结构的 AIME 2025 在多数关注的新模型上缺测，推理仅保留 CritPt 的半份贡献。"
                         + ("LiveCodeBench 也普遍缺测，部分模型因此同时损失两个领域的半份。" if coding == "LiveCodeBench" else "SciCode 增加科学编程实测证据。")
                         + f"Agent 使用 {agent_pair}。{elo_note}Terminal 只用 v4，旧成绩不补位；所选权重更偏推理与知识，五领域不等权。"),
            "core": candidate["core"], "weights": candidate["weights"], "fallback": "v4_only",
        }
    return variants


def run(input_json, raw_csv, output, *, write_markdown=True):
    _, _, models, maps = dual.load_inputs(input_json, raw_csv, terminal_mode="v4_only")
    search = search_candidates(models, maps)
    original_search = {k: v for k, v in search.items() if k not in ("candidates", "core_options")}
    if search["passing_combinations"] < 10:
        search = search_candidates(models, maps, values=range(9, 41))
        search["previous_range_search"] = original_search
        search["range_change_reason"] = "原 10%–40% 范围未能给出十套九条全过的方案；只将下限细化到 9%，上限 40%、九条偏好、0.05 分差和全部计分规则保持不变"
    selected = select_candidates(search)
    if not selected:
        raise ValueError("No proposal passed every criterion; no ranking was published")
    variants = make_variants(selected)
    summary = {k: v for k, v in search.items() if k != "candidates"}
    summary.update(selected_count=len(variants),
                   selected_core_groups=len({core_signature(c["core"]) for c, _ in selected}),
                   selection_method="按不同 Core 分组，每组依次选择接近等权、分差、扰动、Agent 权重和权重差异；每次排除已选候选，分差优先破同值")
    result = dual.run(input_json, raw_csv, output, write_markdown=write_markdown,
                      variants=variants, selection_mode="preference_filtered", search_metadata=summary,
                      preference_targets=CURRENT_TARGETS, preference_pairs=CURRENT_PAIRS,
                      preference_labels=CURRENT_LABELS, excluded_variant_groups=EXCLUDED_VARIANT_GROUPS)
    (output / "search.json").write_text(json.dumps(search, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"search": summary, "selected": result}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=base.ROOT / "docs/data/models.json")
    parser.add_argument("--raw-csv", type=Path, default=base.ROOT / "ArtificialAnalysis/artificialanalysis_raw_scores_wide.csv")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.raw_csv, args.output_dir), ensure_ascii=False, indent=2))
