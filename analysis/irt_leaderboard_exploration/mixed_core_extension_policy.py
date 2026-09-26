"""Current Mixed Core extension additions, separate from frozen v5 research policy.

Each entry represents one benchmark version and result protocol.  A distinct
score key is required when the same benchmark has incompatible operators or
harnesses in the source library.
"""

from __future__ import annotations

try:
    from .v5_benchmark_policy import BenchmarkPolicy
except ImportError:  # Direct script imports.
    from v5_benchmark_policy import BenchmarkPolicy


CURRENT_EXTENSION_POLICIES = (
    BenchmarkPolicy(
        item_id="apex-agents-aa-current",
        label="APEX-Agents-AA",
        score_key="APEX-Agents-AA",
        canonical_family="apex-agents",
        boards=("agentic-tool-work",),
        scale="percent",
        observed_groups=23,
        observed_creators=13,
        benchmark_creator_controller="Mercor",
        controller_is_ranked_model_vendor=False,
        result_operator="Artificial Analysis",
        result_protocol="AA Stirrup common agent protocol over the Archipelago MCP environment; strict pass@1",
        score_provenance="direct_observation",
        tier="conditional_extension",
        exploration_eligible=True,
        publication_eligible=True,
        only_add=True,
        version_pin="AA APEX-Agents-AA public 452-task subset, excluding IB Worlds 244/246; three repeats, Stirrup 200 turns, 2026-09-25 snapshot",
        source_url="https://artificialanalysis.ai/evaluations/apex-agents-aa",
        rationale=(
            "AA runs one disclosed Stirrup agent and Archipelago MCP setting on "
            "452 public APEX tasks. Each of three repeats must pass every rubric "
            "item; the local grader uses Gemini 3 Flash low as judge. The public "
            "methodology specifies the protocol but does not pin immutable "
            "dataset, agent, grader, or environment commits; new revisions "
            "require another comparability review."
        ),
    ),
    BenchmarkPolicy(
        item_id="aa-analyst-agent-pass5",
        label="AA-AnalystAgent pass^5",
        score_key="benchmark:aa-analyst-agent-pass5",
        canonical_family="aa-analyst-agent",
        boards=("agentic-tool-work",),
        scale="percent",
        observed_groups=14,
        observed_creators=8,
        benchmark_creator_controller="Artificial Analysis",
        controller_is_ranked_model_vendor=False,
        result_operator="Artificial Analysis",
        result_protocol="AA common private-task protocol; 80 tasks, five runs, pass^5",
        score_provenance="direct_observation",
        tier="conditional_extension",
        exploration_eligible=True,
        publication_eligible=True,
        only_add=True,
        version_pin="AA-AnalystAgent September 25, 2026 public chart; pass^5, not pass@1",
        source_url="https://artificialanalysis.ai/evaluations/aa-analyst-agent",
        rationale=(
            "AA independently runs five attempts on each private analyst task. "
            "Only the all-five-correct fraction is scored; pass@1 and pass@k "
            "remain separate metrics. Publicly embedded selected-model rows "
            "are pinned with exact AA model slugs."
        ),
    ),
    BenchmarkPolicy(
        item_id="mlcr-aa-overall",
        label="MLCR-AA Overall",
        score_key="benchmark:mlcr-aa-overall",
        canonical_family="mlcr-aa",
        boards=("knowledge-science",),
        scale="percent",
        observed_groups=27,
        observed_creators=15,
        benchmark_creator_controller="Wisedocs",
        controller_is_ranked_model_vendor=False,
        result_operator="Artificial Analysis",
        result_protocol="AA private medical long-context tasks; Overall majority-judge score",
        score_provenance="direct_observation",
        tier="conditional_extension",
        exploration_eligible=True,
        publication_eligible=True,
        only_add=True,
        version_pin="MLCR-AA September 25, 2026 public chart; Overall, not component scores",
        source_url="https://artificialanalysis.ai/evaluations/mlcr-aa",
        rationale=(
            "The private expert and compound clinical tasks jointly require "
            "accuracy, completeness, and conciseness. The headline Overall "
            "score is distinct from its component scores and from broad AA-LCR."
        ),
    ),
    BenchmarkPolicy(
        item_id="terminal-bench-science-aa",
        label="Terminal-Bench-Science v0.1.0 (AA)",
        score_key="benchmark:terminal-bench-science-aa",
        canonical_family="terminal-bench-science",
        boards=("agentic-tool-work",),
        scale="percent",
        observed_groups=14,
        observed_creators=8,
        benchmark_creator_controller="Terminal-Bench-Science research team",
        controller_is_ranked_model_vendor=False,
        result_operator="Artificial Analysis",
        result_protocol="AA mini-swe-agent on 70 science terminal tasks; three-run mean pass@1",
        score_provenance="direct_observation",
        tier="conditional_extension",
        exploration_eligible=True,
        publication_eligible=True,
        only_add=True,
        version_pin="Terminal-Bench-Science v0.1.0; September 25, 2026 AA public chart",
        source_url="https://artificialanalysis.ai/evaluations/terminal-bench-science",
        rationale=(
            "This 70-task scientific-research set is separate from the software "
            "terminal tasks in Terminal-Bench v4.0 Core. Version 0.1.0, the AA "
            "mini-swe-agent, and three-run mean pass@1 are pinned together."
        ),
    ),
    BenchmarkPolicy(
        item_id="aa-briefcase-rubric-pass-rate",
        label="AA-Briefcase v1.1 Rubric Pass Rate",
        score_key="benchmark:aa-briefcase-rubric-pass-rate",
        canonical_family="aa-briefcase",
        boards=("agentic-tool-work",),
        scale="percent",
        observed_groups=19,
        observed_creators=12,
        benchmark_creator_controller="Artificial Analysis",
        controller_is_ranked_model_vendor=False,
        result_operator="Artificial Analysis",
        result_protocol="AA private artifact tasks; native rubric pass rate",
        score_provenance="direct_observation",
        tier="conditional_extension",
        exploration_eligible=True,
        publication_eligible=True,
        only_add=True,
        version_pin="AA-Briefcase v1.1 September 25, 2026 public chart; rubricPassRate",
        source_url="https://artificialanalysis.ai/evaluations/aa-briefcase?results=rubric-score",
        rationale=(
            "The native rubric pass fraction on 91 private artifact tasks is "
            "used. Briefcase Elo and its linear 0-100 transform are excluded "
            "from this family to prevent scale mixing and double counting."
        ),
    ),
    BenchmarkPolicy(
        item_id="harvey-lab-aa-all-pass-rate",
        label="Harvey LAB-AA All-pass Rate",
        score_key="benchmark:harvey-lab-aa-all-pass-rate",
        canonical_family="harvey-lab",
        boards=("agentic-tool-work",),
        scale="percent",
        observed_groups=9,
        observed_creators=6,
        benchmark_creator_controller="Harvey",
        controller_is_ranked_model_vendor=False,
        result_operator="Artificial Analysis",
        result_protocol="AA Stirrup private legal tasks; all rubric criteria pass",
        score_provenance="direct_observation",
        tier="conditional_extension",
        exploration_eligible=True,
        publication_eligible=True,
        only_add=True,
        version_pin="Harvey LAB-AA September 25, 2026 public chart; ungatedAverageAllPass",
        source_url="https://artificialanalysis.ai/evaluations/harvey-lab-aa?eval-score=all-pass-rate",
        rationale=(
            "The strict all-pass score on 120 private legal tasks is far from "
            "the criterion-level score ceiling. A single LLM judge grades "
            "the rubric; the protocol and limitation are disclosed."
        ),
    ),
    BenchmarkPolicy(
        item_id="toolathlon-verified-owner",
        label="Toolathlon-Verified official Pass@1",
        score_key="benchmark:toolathlon-verified-owner",
        canonical_family="toolathlon-verified",
        boards=("agentic-tool-work",),
        scale="percent",
        observed_groups=17,
        observed_creators=10,
        benchmark_creator_controller="HKUST NLP",
        controller_is_ranked_model_vendor=False,
        result_operator="HKUST NLP",
        result_protocol="Toolathlon-Verified owner leaderboard; Default agent; Pass@1",
        score_provenance="benchmark_operator_observation",
        tier="conditional_extension",
        exploration_eligible=True,
        publication_eligible=True,
        only_add=True,
        version_pin="Toolathlon-Verified 2026-06-30; September 25, 2026 owner snapshot",
        source_url="https://hkust.mintlify.app/docs/leaderboard",
        rationale=(
            "The maintained Verified benchmark is separate from older Toolathlon "
            "and from vendor-reported runs. Only checked independent evaluations "
            "with the Default agent and the Pass@1 point estimate enter this score."
        ),
    ),
    BenchmarkPolicy(
        item_id="osworld-v2-v2026-06-24-standard-500",
        label="OSWorld 2.0 (v2026.06.24, Standard, 500 steps)",
        score_key="benchmark:osworld-v2-v2026-06-24-standard-500",
        canonical_family="osworld-v2",
        boards=("agentic-tool-work",),
        scale="percent",
        observed_groups=5,
        observed_creators=4,
        benchmark_creator_controller="OSWorld research team",
        controller_is_ranked_model_vendor=False,
        result_operator="OSWorld research team",
        result_protocol="v2026.06.24 full 108-task release; Standard tools; 500 steps; binary accuracy",
        score_provenance="benchmark_operator_observation",
        tier="conditional_extension",
        exploration_eligible=True,
        publication_eligible=True,
        only_add=True,
        version_pin="OSWorld 2.0 v2026.06.24; September 25, 2026 owner snapshot",
        source_url="https://osworld-v2.xlang.ai/",
        rationale=(
            "Only full-release, 500-step Standard-tool runs with binary task "
            "completion enter this result. Newer task releases, offline subsets, "
            "batch-tool runs, and partial reward are separate protocols."
        ),
    ),
    BenchmarkPolicy(
        item_id="ifbench-aa",
        label="IFBench (AA)",
        score_key="IFBench",
        canonical_family="ifbench",
        boards=("instruction-context",),
        scale="percent",
        observed_groups=72,
        observed_creators=20,
        benchmark_creator_controller="Ai2 (Allen Institute for AI)",
        controller_is_ranked_model_vendor=False,
        result_operator="Artificial Analysis",
        result_protocol="AA common protocol",
        score_provenance="direct_observation",
        tier="conditional_extension",
        exploration_eligible=True,
        publication_eligible=True,
        only_add=True,
        version_pin="Ai2 allenai/IFBench 58 instruction constraints; AA 294 questions, five repeats, official loose evaluation, prompt-level accuracy",
        source_url="https://artificialanalysis.ai/evaluations/ifbench",
        rationale=(
            "Ai2 develops the 58-constraint IFBench benchmark and Artificial "
            "Analysis evaluates 294 questions over five repeats using the "
            "official loose mode. The AA IFBench Score is prompt-level "
            "accuracy, separate from vendor reports and multi-turn IFBench."
        ),
    ),
    BenchmarkPolicy(
        item_id="frontiercode-v1-1-main-cognition",
        label="FrontierCode v1.1 Main (Cognition)",
        score_key="benchmark:frontiercode-v1-1-main-cognition",
        canonical_family="frontiercode-v1-1-main",
        boards=("coding",),
        scale="percent",
        observed_groups=17,
        observed_creators=5,
        benchmark_creator_controller="Cognition",
        controller_is_ranked_model_vendor=False,
        result_operator="Cognition",
        result_protocol="FrontierCode v1.1 Main official Score; exact effort and model-specific agent harness",
        score_provenance="benchmark_operator_observation",
        tier="conditional_extension",
        exploration_eligible=True,
        publication_eligible=True,
        only_add=True,
        version_pin="FrontierCode v1.1 Main; official leaderboard snapshot",
        source_url="https://cognition.com/frontiercode",
        rationale=(
            "Main is the current version; Diamond is deprecated. The official "
            "leaderboard uses different agent harnesses across models, so this "
            "is a model-plus-agent result rather than a uniform model-only run. "
            "Cognition also develops coding agents, an owner interest disclosed here."
        ),
    ),
    BenchmarkPolicy(
        item_id="deepswe-v1-1-owner-mini-swe-agent",
        label="DeepSWE v1.1 (DataCurve mini-swe-agent)",
        score_key="benchmark:deepswe-v1-1-owner-mini-swe-agent",
        canonical_family="deepswe-v1-1",
        boards=("coding",),
        scale="percent",
        observed_groups=17,
        observed_creators=7,
        benchmark_creator_controller="DataCurve",
        controller_is_ranked_model_vendor=False,
        result_operator="DataCurve / Pier",
        result_protocol="DeepSWE v1.1 owner run; 113 tasks, mini-swe-agent, four repeats, scored-attempt pass@1",
        score_provenance="benchmark_operator_observation",
        tier="conditional_extension",
        exploration_eligible=True,
        publication_eligible=True,
        only_add=True,
        version_pin="DeepSWE v1.1 DataCurve owner JSON; September 25, 2026 snapshot",
        source_url="https://deepswe.datacurve.ai/",
        rationale=(
            "The owner runs all mapped models on the 113-task v1.1 set under "
            "mini-swe-agent with four repeats. Scores are the pass fraction "
            "among scored attempts; infrastructure errors leave the denominator. "
            "Vendor-reported DeepSWE values and other agent systems are separate."
        ),
    ),
    BenchmarkPolicy(
        item_id="swe-marathon-v1-1-owner",
        label="SWE-Marathon v1.1 (official 20-task run)",
        score_key="benchmark:swe-marathon-v1-1-owner",
        canonical_family="swe-marathon-v1-1",
        boards=("coding",),
        scale="percent",
        observed_groups=7,
        observed_creators=4,
        benchmark_creator_controller="SWE-Marathon research team / Abundant AI",
        controller_is_ranked_model_vendor=False,
        result_operator="SWE-Marathon research team",
        result_protocol="v1.1, 20 long software tasks, eight binary trials each; model-specific agents",
        score_provenance="benchmark_operator_observation",
        tier="conditional_extension",
        exploration_eligible=True,
        publication_eligible=True,
        only_add=True,
        version_pin="SWE-Marathon v1.1 current public page bundle; September 25, 2026",
        source_url="https://www.swe-marathon.org/",
        rationale=(
            "Complete 20-task v1.1 owner results with explicit max effort are "
            "summed over 160 trials. Agents differ across models. The bundle's "
            "GLM trial status labels disagree with three positive binary rewards; "
            "the published binary reward, not status, determines the score."
        ),
    ),
    BenchmarkPolicy(
        item_id="frontiermath-tier-4-v2-epoch",
        label="FrontierMath Tier 4 v2 (Epoch run)",
        score_key="benchmark:frontiermath-tier-4-v2-epoch",
        canonical_family="frontiermath-tier-4-v2",
        boards=("hard-reasoning",),
        scale="percent",
        observed_groups=25,
        observed_creators=9,
        benchmark_creator_controller="Epoch AI",
        controller_is_ranked_model_vendor=False,
        result_operator="Epoch AI",
        result_protocol="Epoch-administered FrontierMath Tier 4 v2 Best score across scorers",
        score_provenance="benchmark_operator_observation",
        tier="conditional_extension",
        exploration_eligible=True,
        publication_eligible=True,
        only_add=True,
        version_pin="FrontierMath Tier 4 v2; Epoch run IDs, 64-run September 23, 2026 export, 40 exact configurations",
        source_url="https://epoch.ai/benchmarks/frontiermath-tier-4-v2",
        rationale=(
            "The v2 correction is kept separate from earlier FrontierMath and "
            "from vendor-reported Tier 4 v2 results. OpenAI commissioned the "
            "benchmark and received substantial problem and answer access."
        ),
    ),
    BenchmarkPolicy(
        item_id="epoch-chess-puzzles-v1-1-6",
        label="Chess Puzzles v1.1.6 (Epoch run)",
        score_key="benchmark:epoch-chess-puzzles-v1-1-6",
        canonical_family="chess-puzzles",
        boards=("hard-reasoning",),
        scale="percent",
        observed_groups=38,
        observed_creators=12,
        benchmark_creator_controller="Epoch AI",
        controller_is_ranked_model_vendor=False,
        result_operator="Epoch AI",
        result_protocol="Epoch v1.1.6, 100 unpublished generated FEN positions, unique best next move; mean_score",
        score_provenance="benchmark_operator_observation",
        tier="conditional_extension",
        exploration_eligible=True,
        publication_eligible=True,
        only_add=True,
        version_pin="Chess Puzzles v1.1.6; Epoch September 25, 2026 export, 186 runs, 120 exact configurations",
        source_url="https://epoch.ai/benchmarks/chess-puzzles",
        rationale=(
            "Epoch's Success runs on one fixed generated chess puzzle version "
            "are matched by exact model version and effort. The related Mystery "
            "Game test can correlate with this one-step game-reasoning signal."
        ),
    ),
    BenchmarkPolicy(
        item_id="epoch-mystery-game-puzzles-v1-0-4",
        label="Mystery Game Puzzles v1.0.4 (Epoch run)",
        score_key="benchmark:epoch-mystery-game-puzzles-v1-0-4",
        canonical_family="mystery-game-puzzles",
        boards=("hard-reasoning",),
        scale="percent",
        observed_groups=24,
        observed_creators=10,
        benchmark_creator_controller="Epoch AI",
        controller_is_ranked_model_vendor=False,
        result_operator="Epoch AI",
        result_protocol="Epoch v1.0.4, 100 hidden-identity game positions, text state and minimal agent; mean_score",
        score_provenance="benchmark_operator_observation",
        tier="conditional_extension",
        exploration_eligible=True,
        publication_eligible=True,
        only_add=True,
        version_pin="Mystery Game Puzzles v1.0.4; Epoch September 25, 2026 export, 129 runs, 68 exact configurations",
        source_url="https://epoch.ai/benchmarks/mystery-game-puzzles",
        rationale=(
            "Epoch's Success runs on one fixed puzzle version are matched by "
            "exact model version and effort. The text-state minimal agent and "
            "unknown games differ from Chess, though both test one-step play."
        ),
    ),
    BenchmarkPolicy(
        item_id="epoch-ebr-bench-card-ban-v4",
        label="EBR-bench v4 Card-ban (Epoch single-agent)",
        score_key="benchmark:epoch-ebr-bench-card-ban-v4",
        canonical_family="ebr-bench",
        boards=("hard-reasoning",),
        scale="percent",
        observed_groups=4,
        observed_creators=2,
        benchmark_creator_controller="Epoch AI",
        controller_is_ranked_model_vendor=False,
        result_operator="Epoch AI",
        result_protocol="v4 Card-ban default single-agent; topline objective fraction from 10-game runs",
        score_provenance="benchmark_operator_observation",
        tier="conditional_extension",
        exploration_eligible=True,
        publication_eligible=True,
        only_add=True,
        version_pin="EBR-bench v4 Card-ban; Epoch September 25, 2026 export and page-verified run IDs",
        source_url="https://epoch.ai/benchmarks/ebr-bench",
        rationale=(
            "Only four exact-model runs confirmed under the Card-ban rule enter "
            "this score. The CSV has blank task-version cells, so run IDs are "
            "pinned against Epoch's v4 methodology note. Older unbanned runs, "
            "multi-agent settings, and fallback-ambiguous models are excluded. "
            "The four-model, two-creator fit is especially sensitive to updates."
        ),
    ),
    BenchmarkPolicy(
        item_id="arc-agi-3-standard",
        label="ARC-AGI-3 Standard harness",
        score_key="benchmark:arc-agi-3-standard",
        canonical_family="arc-agi-3",
        boards=("agentic-tool-work",),
        scale="percent",
        observed_groups=7,
        observed_creators=3,
        benchmark_creator_controller="ARC Prize Foundation",
        controller_is_ranked_model_vendor=False,
        result_operator="ARC Prize Foundation",
        result_protocol="ARC-AGI-3 official Standard harness leaderboard",
        score_provenance="benchmark_operator_observation",
        tier="conditional_extension",
        exploration_eligible=True,
        publication_eligible=True,
        only_add=True,
        version_pin="ARC-AGI-3 Standard harness; official leaderboard snapshot",
        source_url="https://arcprize.org/leaderboard",
        rationale=(
            "Interactive reasoning under the Standard harness. Provider Adapter "
            "and vendor-reported scores remain separate because their scores "
            "are not protocol-equivalent."
        ),
    ),
    BenchmarkPolicy(
        item_id="agents-last-exam-v1-overall-pass-rate",
        label="Agents' Last Exam V1 Overall pass rate",
        score_key="benchmark:agents-last-exam-v1-overall-pass-rate",
        canonical_family="agents-last-exam-v1",
        boards=("agentic-tool-work",),
        scale="percent",
        observed_groups=11,
        observed_creators=6,
        benchmark_creator_controller="UC Berkeley RDI",
        controller_is_ranked_model_vendor=False,
        result_operator="UC Berkeley RDI",
        result_protocol="ALE-V1 official Overall pass rate; disclosed model-specific agent harness",
        score_provenance="benchmark_operator_observation",
        tier="conditional_extension",
        exploration_eligible=True,
        publication_eligible=True,
        only_add=True,
        version_pin="Agents' Last Exam ALE-V1; Overall pass rate",
        source_url="https://agents-last-exam.org/leaderboard",
        rationale=(
            "The owner-run Overall pass rate is distinct from partial-credit "
            "Score and from vendor-reported ALE rows. Harnesses differ by model "
            "and are disclosed on the official leaderboard."
        ),
    ),
)
