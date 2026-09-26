# Priority order scenarios — 2026-09-26

This is a **read-only scenario study** of the current Mixed Core formula after
the September 26 source refresh. The study itself changes no default weights,
Extra Test registry, source scores, or generated rankings. Its input is
`docs/data/models.json`, SHA-256
`614f37c1c9c27e51551d0f233fc63e9a60af901876e3b4683287011262df395f`.
Run `python -B -m analysis.irt_leaderboard_exploration.verify_mixed_core_priority_scenarios`
from the repository root to refit every listed Extra Test subset and reproduce
the exact-configuration comparisons. Each named family uses its highest scoring
eligible tier under that scenario.

## The three hard requirements with current data

**No current-data combination can satisfy all three.** GPT-5.4 xhigh has no
AIndex score: Terminal-Bench v4.0, SciCode, AutomationBench-AA, and GDP.pdf are
all missing. Both configured Coding Core tests are missing, so the eligibility
rule excludes this exact configuration before weights and Extra Tests are
applied. Changing either cannot create a score for comparison with the highest
eligible GPT-5.6 Luna tier.

The [current AA SciCode evaluation](https://artificialanalysis.ai/evaluations/scicode)
does not list the main GPT-5.4 xhigh configuration, and the
[Terminal-Bench v4.0 owner leaderboard](https://www.tbench.ai/) has no matching
run. [OpenAI's GPT-5.4 release](https://openai.com/index/introducing-gpt-5-4/)
reports Terminal-Bench 2.0, which is a different Core release.

The other two model orders and the requirement that Coding + Agentic + Hard
Reasoning exceed 60% have several arithmetic candidates. The weights below are
in the order Coding / Agentic / Hard Reasoning / Knowledge / Instruction;
positive gaps mean the requested order holds.

| Extra Tests | Weights | First three weights | Opus 5.5 − Opus 5 | Fable 5.1 − Fable 5 |
| --- | --- | ---: | ---: | ---: |
| All current 19 | 35 / 15 / 20 / 20 / 10 | 70% | +0.988448 | +6.309094 |
| 17, excluding FrontierCode and EBR-bench | 35 / 15 / 20 / 20 / 10 | 70% | +1.036260 | +6.344953 |
| 14, retaining items with at least 10 fitting representatives | 35 / 15 / 20 / 20 / 10 | 70% | +0.894191 | +6.479548 |
| All current 19, alternative | 30 / 15 / 20 / 25 / 10 | 65% | +0.838917 | +6.119194 |

The 17-item case removes FrontierCode because its official results combine
models with different agents, and EBR-bench because only four representatives
fit its trend. The 14-item case applies a coverage rule independently of the
named model orders: it removes SWE-Marathon, OSWorld 2.0, ARC-AGI-3 Standard,
EBR-bench Card-ban, and Harvey LAB-AA. Repeating the same weights across these
subsets isolates the effect of changing Extra Tests. The script also searches a five-point
weight grid, with every board between 10% and 35% and the first three over
60%; respectively 49, 53, and 48 grid combinations satisfy the two currently
comparable Claude orders. This grid is a search domain, not a global proof.

At the **current production weights** of 24 / 24 / 27 / 16 / 9, all 19 tests
give Opus 5.5 − Opus 5 **−3.143799** and Fable 5.1 − Fable 5 **+7.604158**.
The first three boards already sum to 75%. The script applies these same
production weights to each smaller Extra Test subset as a baseline.

At the current 19-item weights, Opus 5.5 has an Agentic board score of
**34.769350** against Opus 5's **60.028052**. Opus 5.5's τ³-Banking Core cell is empty, so
its Agentic Core base is half of its 69.5387 AutomationBench-AA result and it
receives no Agentic Extra bonus. Opus 5 has both Core cells and a 10.710302
Extra bonus. A live check of [AA's τ³-Banking evaluation](https://artificialanalysis.ai/evaluations/tau3-banking)
and [Opus 5.5 model page](https://artificialanalysis.ai/models/claude-opus-5-5)
found explicit nulls for all five Opus 5.5 tiers; the
[official release](https://www.anthropic.com/claude-opus-5-5) and its system card
do not provide a matching score. A weight-only reversal does not establish
that the newer model is stronger on this board.

## Historical SciCode sensitivity, not a current result

A historical [Epoch data mirror](https://github.com/tobiasosborne/ai-agents-seminar/blob/dcfb8066af6de561705723477a459be1ebd8ee80/Wuerzburg-talk-2026/model-progress/data/epoch/scicode_external.csv)
records 56.5972% SciCode for GPT-5.4 xhigh, consistent with [AA's rounded
March chart](https://x.com/ArtificialAnlys/status/2029950497516573183).
The [current AA model page](https://artificialanalysis.ai/models/gpt-5-4)
does not expose a current result for that exact Core field. The script inserts
56.5972 only into an in-memory copy, leaving Terminal-Bench v4.0 and the other
Core gaps empty. That makes GPT-5.4 xhigh eligible with three missing Core
items, but cannot be represented as a published AIndex result.

With **all 19 Extra Tests**, a linear program over *all nonnegative board
weights* summing to 100 and Coding + Agentic + Hard Reasoning at least 60.0001% finds
the best common gap across all three required comparisons is **−8.644276**
points. Requiring each board to retain at least 5% gives **−9.551990** points.
Thus the historical SciCode value alone does not make the current 19-item
configuration feasible, even with extreme weights.

The current source gaps, especially GPT-5.4's empty Coding board, are the
binding issue. Filling them requires exact-version, exact-protocol public
evidence rather than weight or Extra Test selection.
