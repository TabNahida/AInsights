"""Frozen benchmark eligibility policy for the v5 ranking search.

This module deliberately contains no scoring or ranking implementation.  It
separates who creates/controls a benchmark from who runs/reports a result, and
exposes immutable data plus small selection/validation helpers for search and
publication QA.

The policy is intentionally conservative:

* ``core`` contains only direct 0--100 observations available for every model
  in the frozen 154-``variantGroup`` population under one Artificial Analysis
  protocol.
* ``extension`` and ``conditional_extension`` are only-add evidence.  They may
  never replace a missing core value, inject a neutral value, or alter the
  frozen population.
* every GDPval/GDPval-AA representation is excluded.  GDPval is controlled by
  OpenAI, while the AA fields are Elo-derived transforms rather than native
  task percentages.
* named-model acceptance rules are publication gates applied after an
  anonymous score sort; they do not appear here as benchmark or model weights.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal


BoardId = Literal[
    "coding",
    "agentic-tool-work",
    "hard-reasoning",
    "knowledge-science",
    "instruction-context",
]
EligibilityTier = Literal[
    "core",
    "extension",
    "conditional_extension",
    "quarantine",
    "excluded",
    "auxiliary",
]


POLICY_VERSION: Final = "v5-2026-08-10-draft2"
FROZEN_POPULATION_SIZE: Final = 154
CORE_REQUIRED_GROUPS: Final = FROZEN_POPULATION_SIZE
CORE_MIN_CREATORS: Final = 5
EXTENSION_MIN_GROUPS: Final = 5
EXTENSION_MIN_CREATORS: Final = 3
MAX_SINGLE_RESULT_SOURCE_SHARE: Final = 0.50
NUMERIC_SCALES_ALLOWED_FOR_DIRECT_SCORE: Final = frozenset({"percent"})
EXCLUDED_CANONICAL_FAMILIES: Final = frozenset({"gdpval"})


@dataclass(frozen=True, slots=True)
class BenchmarkPolicy:
    """One canonical benchmark family under one frozen result protocol."""

    item_id: str
    label: str
    score_key: str
    canonical_family: str
    boards: tuple[BoardId, ...]
    scale: str
    observed_groups: int
    observed_creators: int
    benchmark_creator_controller: str
    controller_is_ranked_model_vendor: bool | None
    result_operator: str
    result_protocol: str
    score_provenance: str
    tier: EligibilityTier
    exploration_eligible: bool
    publication_eligible: bool
    only_add: bool
    version_pin: str
    source_url: str
    rationale: str


def _policy(
    item_id: str,
    label: str,
    score_key: str,
    canonical_family: str,
    boards: tuple[BoardId, ...],
    scale: str,
    observed_groups: int,
    observed_creators: int,
    benchmark_creator_controller: str,
    controller_is_ranked_model_vendor: bool | None,
    result_operator: str,
    result_protocol: str,
    score_provenance: str,
    tier: EligibilityTier,
    exploration_eligible: bool,
    publication_eligible: bool,
    only_add: bool,
    version_pin: str,
    source_url: str,
    rationale: str,
) -> BenchmarkPolicy:
    return BenchmarkPolicy(
        item_id=item_id,
        label=label,
        score_key=score_key,
        canonical_family=canonical_family,
        boards=boards,
        scale=scale,
        observed_groups=observed_groups,
        observed_creators=observed_creators,
        benchmark_creator_controller=benchmark_creator_controller,
        controller_is_ranked_model_vendor=controller_is_ranked_model_vendor,
        result_operator=result_operator,
        result_protocol=result_protocol,
        score_provenance=score_provenance,
        tier=tier,
        exploration_eligible=exploration_eligible,
        publication_eligible=publication_eligible,
        only_add=only_add,
        version_pin=version_pin,
        source_url=source_url,
        rationale=rationale,
    )


BENCHMARK_POLICIES: Final[tuple[BenchmarkPolicy, ...]] = (
    # Core: complete, direct, common-protocol observations on all 154 groups.
    _policy(
        "scicode-aa", "SciCode (AA)", "SciCode", "scicode",
        ("coding", "knowledge-science"), "percent", 154, 37,
        "SciCode academic consortium (UIUC, Argonne, CMU, and collaborators)",
        False, "Artificial Analysis", "AA common protocol", "direct_observation",
        "core", True, True, False, "AA snapshot + SciCode dataset revision",
        "https://github.com/scicode-bench/SciCode",
        "Complete common-protocol direct percentage; one canonical family even when reused across boards.",
    ),
    _policy(
        "hle-aa", "Humanity's Last Exam (AA)", "Humanity's Last Exam", "hle",
        ("hard-reasoning", "knowledge-science"), "percent", 154, 37,
        "Center for AI Safety and Scale AI", False, "Artificial Analysis",
        "AA common protocol", "direct_observation", "core", True, True, False,
        "AA snapshot + CAIS HLE dataset revision",
        "https://github.com/centerforaisafety/hle",
        "Complete common-protocol direct percentage; benchmark controller is independent of ranked model vendors.",
    ),
    _policy(
        "critpt-aa", "CritPt (AA)", "CritPt", "critpt",
        ("hard-reasoning", "instruction-context"), "percent", 154, 37,
        "CritPt consortium (50+ physics researchers)", False, "Artificial Analysis",
        "AA continuously monitored protocol", "direct_observation", "core", True, True, False,
        "AA snapshot + CritPt dataset revision",
        "https://github.com/CritPt-Benchmark/CritPt-Benchmark.github.io",
        "Complete common-protocol direct percentage with an independently controlled research benchmark.",
    ),
    _policy(
        "gpqa-diamond-aa", "GPQA Diamond (AA)", "GPQA Diamond", "gpqa-diamond",
        ("hard-reasoning", "knowledge-science"), "percent", 154, 37,
        "GPQA academic authors", False, "Artificial Analysis", "AA common protocol",
        "direct_observation", "core", True, True, False,
        "AA snapshot + GPQA dataset revision", "https://github.com/idavidrein/gpqa",
        "Complete common-protocol direct percentage; Diamond is frozen as the canonical subset.",
    ),
    _policy(
        "omniscience-aa", "AA-Omniscience Accuracy", "AA-Omniscience Accuracy",
        "aa-omniscience", ("knowledge-science",), "percent", 154, 37,
        "Artificial Analysis", False, "Artificial Analysis", "AA common protocol",
        "direct_observation", "core", True, True, False,
        "AA snapshot + Omniscience benchmark revision",
        "https://artificialanalysis.ai/evaluations/omniscience",
        "Complete direct accuracy. Accuracy is the sole scoring representative of the Omniscience family.",
    ),
    _policy(
        "aa-lcr", "AA-LCR", "AA-LCR", "aa-lcr",
        ("agentic-tool-work", "instruction-context"), "percent", 154, 37,
        "Artificial Analysis", False, "Artificial Analysis", "AA common protocol",
        "direct_observation", "core", True, True, False,
        "AA snapshot + AA-LCR benchmark revision",
        "https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index",
        "Complete direct percentage; one family may support two boards but is counted once within either board.",
    ),

    # Extension: direct real observations that are sparse on the frozen population.
    _policy(
        "terminal-bench-v2-1-aa", "Terminal-Bench v2.1 (AA)", "Terminal-Bench v2.1",
        "terminal-bench-v2-1", ("coding", "agentic-tool-work"), "percent", 143, 37,
        "Harbor / Terminal-Bench maintainers", False, "Artificial Analysis",
        "AA common protocol", "direct_observation", "extension", True, True, True,
        "Terminal-Bench v2.1 + AA snapshot",
        "https://github.com/harbor-framework/terminal-bench",
        "High-coverage direct AA run, but not complete; extension may only add shared observed evidence.",
    ),
    _policy(
        "mmmu-pro-aa", "MMMU-Pro (AA)", "MMMU-Pro", "mmmu-pro",
        ("knowledge-science",), "percent", 81, 18, "MMMU academic team", False,
        "Artificial Analysis", "AA common protocol", "direct_observation",
        "extension", True, True, True, "AA snapshot + MMMU-Pro dataset revision",
        "https://github.com/Zheng0428/MMMU-Pro",
        "Independent benchmark and common operator, with partial population coverage.",
    ),
    _policy(
        "aime-2025-aa", "AIME 2025 (AA)", "AIME 2025", "aime-2025",
        ("hard-reasoning",), "percent", 53, 15,
        "Mathematical Association of America", False, "Artificial Analysis",
        "AA common protocol", "direct_observation", "extension", True, True, True,
        "AIME 2025 question set + AA snapshot", "https://maa.org/math-competitions/aime",
        "Direct common-protocol contest score with sufficient but partial coverage.",
    ),
    _policy(
        "ifbench-aa", "IFBench (AA)", "IFBench", "ifbench",
        ("instruction-context",), "percent", 129, 29,
        "Unknown in current local benchmark registry", None, "Artificial Analysis",
        "AA common protocol", "direct_observation", "conditional_extension", True, False, True,
        "BLOCKED: record owner, dataset revision, and evaluator protocol",
        "https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index",
        "Coverage is strong, but creator/controller metadata is absent; exploration only until registered.",
    ),
    _policy(
        "tau2-bench-telecom-aa", "tau2-Bench Telecom (AA)", "τ²-Bench Telecom",
        "tau2-bench", ("agentic-tool-work",), "percent", 128, 29,
        "Sierra Research", False, "Artificial Analysis", "AA common protocol",
        "direct_observation", "conditional_extension", True, False, True,
        "Pin tau2/tau3 package tag and AA harness before publication",
        "https://github.com/sierra-research/tau2-bench",
        "Independent operator and high coverage, but the source snapshot does not record the benchmark package revision.",
    ),
    _policy(
        "tau3-banking-aa", "tau3-Banking (AA)", "τ³-Banking", "tau3-banking",
        ("agentic-tool-work",), "percent", 104, 23, "Sierra Research", False,
        "Artificial Analysis", "AA common protocol", "direct_observation",
        "conditional_extension", True, False, True,
        "Require tau2-bench >= v1.0.1 and exact commit; pre-v1.0.1 is incomparable",
        "https://github.com/sierra-research/tau2-bench",
        "July 2026 banking grading changes make an unversioned score unsafe for publication.",
    ),
    _policy(
        "apex-agents-aa", "APEX-Agents-AA", "APEX-Agents-AA", "apex-agents",
        ("agentic-tool-work",), "percent", 24, 12, "Mercor", False,
        "Artificial Analysis", "AA common protocol over the Mercor environment",
        "direct_observation", "conditional_extension", True, False, True,
        "Pin APEX dataset, Archipelago agent wrapper, judge, and tool environment",
        "https://github.com/Mercor-Intelligence/archipelago",
        "Real observations, but agent wrapper and judge choices can dominate a model-only ranking.",
    ),
    _policy(
        "itbench-aa", "ITBench-AA", "ITBench-AA", "itbench",
        ("agentic-tool-work",), "percent", 27, 13, "IBM Research", True,
        "Artificial Analysis with IBM Research", "joint ITBench-AA protocol",
        "direct_observation", "quarantine", True, False, True,
        "Require independent governance and frozen SRE task/environment revision",
        "https://github.com/itbench-hub/ITBench",
        "IBM controls the benchmark and is also a ranked model vendor; keep as a sensitivity only.",
    ),

    # Sparse first-party / mixed-protocol families used only for exploration.
    _policy(
        "swe-bench-pro", "SWE-Bench Pro", "benchmark:swe-bench-pro", "swe-bench-pro",
        ("coding", "agentic-tool-work"), "percent", 37, 11, "Scale AI", False,
        "Mixed model-vendor release/system-card operators", "non-uniform reported protocols",
        "first_party_reported", "conditional_extension", True, False, True,
        "Freeze one comparable harness/configuration per row",
        "https://scale.com/leaderboard/swe_bench_pro_public",
        "Useful frontier signal, but result operators and agent stacks are not uniform.",
    ),
    _policy(
        "livecodebench", "LiveCodeBench (reported)", "benchmark:livecodebench", "livecodebench",
        ("coding",), "percent", 19, 5, "LiveCodeBench academic/community maintainers", False,
        "Mixed model-vendor release/system-card operators", "non-uniform reported protocols",
        "first_party_reported", "conditional_extension", True, False, True,
        "Freeze release window, pass@k, sampling, and execution harness",
        "https://github.com/LiveCodeBench/LiveCodeBench",
        "Raw reported rows avoid the fitted site fallback but remain cross-protocol.",
    ),
    _policy(
        "swe-bench-verified", "SWE-bench Verified", "benchmark:swe-bench-verified",
        "swe-bench-verified", ("coding",), "percent", 23, 10,
        "SWE-bench team; Verified subset produced with OpenAI involvement", True,
        "Mixed model-vendor release/system-card operators", "non-uniform agent protocols",
        "first_party_reported", "conditional_extension", True, False, True,
        "Require benchmark-owner conflict review and one frozen agent harness",
        "https://www.swebench.com/SWE-bench/",
        "Observed results are real, but benchmark-subset governance and agent stacks are not independent/uniform.",
    ),
    _policy(
        "swe-bench-multilingual", "SWE-bench Multilingual", "benchmark:swe-bench-multilingual",
        "swe-bench-multilingual", ("coding",), "percent", 14, 7,
        "SWE-bench Multilingual maintainers", None,
        "Mixed model-vendor release/system-card operators", "non-uniform agent protocols",
        "first_party_reported", "conditional_extension", True, False, True,
        "Record owner, task revision, and one frozen agent harness",
        "https://www.swebench.com/multilingual.html",
        "Sufficient sparse coverage for exploration, not yet a comparable publication input.",
    ),
    _policy(
        "hle-tools", "HLE with tools", "benchmark:hle-tools", "hle-tools",
        ("agentic-tool-work",), "percent", 26, 10, "Center for AI Safety and Scale AI", False,
        "Mixed model-vendor release/system-card operators", "non-uniform tool protocols",
        "first_party_reported", "conditional_extension", True, False, True,
        "Freeze tools, search access, judge, and sampling",
        "https://github.com/centerforaisafety/hle",
        "Independent benchmark, but tool-enabled result protocols differ by reporting vendor.",
    ),
    _policy(
        "mcp-atlas", "MCP-Atlas Public", "benchmark:mcp-atlas", "mcp-atlas",
        ("agentic-tool-work",), "percent", 22, 10, "Scale AI", False,
        "Mixed model-vendor release/system-card operators", "non-uniform agent protocols",
        "first_party_reported", "conditional_extension", True, False, True,
        "Freeze public split, tools, wrapper, judge, and sampling", "",
        "Direct reported values, but agent execution stacks are not comparable enough for publication.",
    ),
    _policy(
        "osworld-verified", "OSWorld-Verified", "benchmark:osworld-verified", "osworld-verified",
        ("agentic-tool-work",), "percent", 10, 5, "OSWorld academic maintainers", False,
        "Mixed model-vendor release/system-card operators", "non-uniform computer-use protocols",
        "first_party_reported", "conditional_extension", True, False, True,
        "Freeze OS image, task revision, wrapper, and sampling", "https://os-world.github.io/",
        "Meets sparse coverage but remains system/harness-sensitive.",
    ),
    _policy(
        "toolathlon", "Toolathlon", "benchmark:toolathlon", "toolathlon",
        ("agentic-tool-work",), "percent", 21, 10, "Toolathlon maintainers", None,
        "Mixed model-vendor release/system-card operators", "non-uniform tool protocols",
        "first_party_reported", "conditional_extension", True, False, True,
        "Record owner and freeze tool environment, wrapper, judge, and sampling", "",
        "Adequate coverage for exploration; current source registry cannot prove protocol comparability.",
    ),
    _policy(
        "automationbench", "AutomationBench", "benchmark:automationbench", "automationbench",
        ("agentic-tool-work",), "percent", 10, 6, "Unknown in current local benchmark registry", None,
        "Mixed model-vendor release/system-card operators", "non-uniform agent protocols",
        "first_party_reported", "conditional_extension", True, False, True,
        "Record owner and freeze environment, wrapper, judge, and sampling", "",
        "Meets sparse coverage but creator/controller metadata is missing.",
    ),
    _policy(
        "mmlu-pro", "MMLU-Pro", "benchmark:mmlu-pro", "mmlu-pro",
        ("knowledge-science",), "percent", 17, 6, "MMLU-Pro academic maintainers", False,
        "Mixed model-vendor release/system-card operators", "non-uniform reported protocols",
        "first_party_reported", "conditional_extension", True, False, True,
        "Freeze dataset revision, prompt, sampling, and grading", "https://github.com/TIGER-AI-Lab/MMLU-Pro",
        "Direct sparse results, but reporting protocols differ.",
    ),
    _policy(
        "charxiv-no-tools", "CharXiv Reasoning", "benchmark:charxiv-no-tools", "charxiv-no-tools",
        ("instruction-context",), "percent", 12, 6, "CharXiv academic maintainers", False,
        "Mixed model-vendor release/system-card operators", "non-uniform reported protocols",
        "first_party_reported", "conditional_extension", True, False, True,
        "Freeze split, no-tools protocol, judge, and sampling", "https://charxiv.github.io/",
        "Useful context signal, but only under a fixed no-tools protocol.",
    ),

    # Quarantine: below the reproducible extension floor or source-concentrated.
    _policy(
        "deepswe-v1-1", "DeepSWE v1.1", "benchmark:deepswe-v1-1", "deepswe-v1-1",
        ("coding",), "percent", 6, 4, "Unknown in current local benchmark registry", None,
        "Primarily OpenAI release rows", "source-concentrated reported protocol",
        "first_party_reported", "quarantine", True, False, True,
        "Require independent rows and owner/protocol registry", "",
        "Barely clears the count floor and is dominated by one reporting source.",
    ),
    _policy(
        "frontiermath-tier-4", "FrontierMath Tier 4", "benchmark:frontiermath-tier-4",
        "frontiermath-tier-4", ("hard-reasoning",), "percent", 4, 3, "Epoch AI", False,
        "OpenAI GPT-5.5 release", "single-release reported protocol", "first_party_reported",
        "quarantine", True, False, True, "Need >=5 groups and independent operators",
        "https://epoch.ai/frontiermath", "Below the extension group floor and source-concentrated.",
    ),
    _policy(
        "frontiermath-tier-1-3", "FrontierMath Tier 1-3", "benchmark:frontiermath-tier-1-3",
        "frontiermath-tier-1-3", ("hard-reasoning",), "percent", 4, 3, "Epoch AI", False,
        "OpenAI GPT-5.5 release", "single-release reported protocol", "first_party_reported",
        "quarantine", True, False, True, "Need >=5 groups and independent operators",
        "https://epoch.ai/frontiermath", "Below the extension group floor and source-concentrated.",
    ),
    _policy(
        "mmmlu", "MMMLU", "benchmark:mmmlu", "mmmlu", ("knowledge-science",),
        "percent", 3, 2, "Unknown in current local benchmark registry", None,
        "Mixed model-vendor releases", "reported protocol", "first_party_reported",
        "quarantine", True, False, True, "Need >=5 groups, >=3 creators, owner metadata",
        "", "Below both extension coverage floors.",
    ),

    # Explicitly excluded vendor-controlled or non-comparable families.
    _policy(
        "browsecomp", "BrowseComp", "benchmark:browsecomp", "browsecomp",
        ("agentic-tool-work",), "percent", 24, 9, "OpenAI", True,
        "Mixed model-vendor releases", "reported protocols", "first_party_reported",
        "excluded", False, False, True, "Excluded by creator-conflict rule",
        "https://openai.com/index/browsecomp/",
        "Benchmark controller is a ranked model vendor; operator diversity does not remove that conflict.",
    ),
    _policy(
        "gdpval-wins-ties", "GDPval wins/ties", "benchmark:gdpval-wins-ties", "gdpval",
        ("agentic-tool-work",), "percent", 4, 3, "OpenAI", True, "OpenAI release",
        "single-release protocol", "first_party_reported", "excluded", False, False, True,
        "Excluded by creator-conflict rule", "https://openai.com/index/gdpval/",
        "OpenAI controls the benchmark and the available rows are source-concentrated.",
    ),
    _policy(
        "gdpval-aa-elo", "GDPval-AA Elo", "benchmark:gdpval-aa-elo", "gdpval",
        ("agentic-tool-work",), "rank", 17, 8, "OpenAI", True,
        "Mixed model-vendor releases", "non-uniform reported protocols", "ordinal_or_elo",
        "excluded", False, False, True, "Excluded by creator-conflict and scale rules", "",
        "Rank/Elo scale is not a direct percentage and GDPval is vendor controlled.",
    ),
    _policy(
        "gdpval-aa-v2-aa", "GDPval-AA v2", "GDPval-AA v2", "gdpval",
        ("agentic-tool-work",), "derived", 139, 37, "OpenAI", True,
        "Artificial Analysis", "AA common protocol", "elo_linear_transform",
        "excluded", False, False, True, "Excluded by creator-conflict and transform rules",
        "https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index",
        "The stored value is (Elo-500)/2000*100, not a native task percentage.",
    ),
    _policy(
        "gdpval-aa-v1-aa", "GDPval-AA", "GDPval-AA", "gdpval",
        ("agentic-tool-work",), "derived", 139, 37, "OpenAI", True,
        "Artificial Analysis", "AA common protocol", "elo_linear_transform",
        "excluded", False, False, True, "Excluded by creator-conflict and transform rules",
        "https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index",
        "The stored value is (Elo-500)/2000*100, not a native task percentage.",
    ),
    _policy(
        "omniscience-non-hallucination-aa", "AA-Omniscience Non-Hallucination Rate",
        "AA-Omniscience Non-Hallucination Rate", "aa-omniscience",
        ("knowledge-science",), "percent", 154, 37, "Artificial Analysis", False,
        "Artificial Analysis", "AA common protocol", "direct_observation", "auxiliary",
        False, False, False, "Same revision as Omniscience Accuracy",
        "https://artificialanalysis.ai/evaluations/omniscience",
        "Audit/display only; scoring it separately would double-count the Omniscience family.",
    ),
)


BENCHMARK_POLICY_BY_ID: Final = {policy.item_id: policy for policy in BENCHMARK_POLICIES}
CORE_ITEM_IDS: Final = tuple(
    policy.item_id for policy in BENCHMARK_POLICIES if policy.tier == "core"
)
EXTENSION_ITEM_IDS: Final = tuple(
    policy.item_id for policy in BENCHMARK_POLICIES if policy.tier == "extension"
)
CONDITIONAL_EXTENSION_ITEM_IDS: Final = tuple(
    policy.item_id
    for policy in BENCHMARK_POLICIES
    if policy.tier == "conditional_extension"
)
QUARANTINED_ITEM_IDS: Final = tuple(
    policy.item_id for policy in BENCHMARK_POLICIES if policy.tier == "quarantine"
)
EXCLUDED_ITEM_IDS: Final = tuple(
    policy.item_id for policy in BENCHMARK_POLICIES if policy.tier == "excluded"
)


def item_ids_for_pool(
    pool: Literal["core", "publication_extension", "exploration_extension"],
) -> tuple[str, ...]:
    """Return a deterministic only-add pool for v5 search or publication QA."""

    if pool == "core":
        return CORE_ITEM_IDS
    if pool == "publication_extension":
        return CORE_ITEM_IDS + EXTENSION_ITEM_IDS
    if pool == "exploration_extension":
        return CORE_ITEM_IDS + EXTENSION_ITEM_IDS + CONDITIONAL_EXTENSION_ITEM_IDS
    raise ValueError(f"unknown v5 benchmark pool: {pool}")


def is_forbidden_identifier(identifier: str) -> bool:
    """Fail closed for GDPval aliases that are not yet present in the registry."""

    normalized = "".join(character.lower() for character in identifier if character.isalnum())
    return "gdpval" in normalized


def validate_policy() -> None:
    """Raise if policy edits violate the frozen v5 publication invariants."""

    if len(BENCHMARK_POLICY_BY_ID) != len(BENCHMARK_POLICIES):
        raise ValueError("duplicate benchmark item_id in v5 policy")
    for policy in BENCHMARK_POLICIES:
        if is_forbidden_identifier(policy.item_id) or is_forbidden_identifier(policy.score_key):
            if policy.tier != "excluded" or policy.exploration_eligible or policy.publication_eligible:
                raise ValueError(f"GDPval alias is not fully excluded: {policy.item_id}")
        if policy.tier == "core":
            if policy.observed_groups != CORE_REQUIRED_GROUPS:
                raise ValueError(f"core item is not complete: {policy.item_id}")
            if policy.observed_creators < CORE_MIN_CREATORS:
                raise ValueError(f"core creator coverage is too low: {policy.item_id}")
            if policy.scale not in NUMERIC_SCALES_ALLOWED_FOR_DIRECT_SCORE:
                raise ValueError(f"core scale is not direct percent: {policy.item_id}")
            if policy.score_provenance != "direct_observation":
                raise ValueError(f"core item is not a direct observation: {policy.item_id}")
            if policy.controller_is_ranked_model_vendor is not False:
                raise ValueError(f"core controller conflict unresolved: {policy.item_id}")
            if policy.result_operator != "Artificial Analysis":
                raise ValueError(f"core operator is not common-protocol AA: {policy.item_id}")
            if policy.only_add:
                raise ValueError(f"core item incorrectly marked only-add: {policy.item_id}")
        elif policy.exploration_eligible and not policy.only_add and policy.tier != "auxiliary":
            raise ValueError(f"non-core evidence must be only-add: {policy.item_id}")


validate_policy()
