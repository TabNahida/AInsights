# Mixed Core order sensitivity — 2026-09-25

This is a read-only scenario study. Production remains at Coding 24%, Agentic
24%, Hard Reasoning 27%, Knowledge 16%, Instruction 9%, with 19 Extra Tests.
Run `python -B -m analysis.irt_leaderboard_exploration.verify_mixed_core_scenarios`
from the repository root to reproduce the cases below. The script uses the
current `docs/data/models.json`, refits each Extra Test subset's anonymous OLS
trends and pooled cap, and applies the production score function to 200 eligible
exact configurations. It then compares the highest scoring eligible
configuration within each named model family; the winning configuration can
change when weights change.
The input `models.json` SHA-256 is
`1A7BF3F9916C1381F9E4F804930272B52614B64EA7502E70CA58B92D46C7EBB5`.

## Six comparisons with ranked evidence

The weight order is Coding / Agentic / Hard Reasoning / Knowledge / Instruction.
All entries are percentages summing to 100. A positive gap means the requested
order holds. For DeepSeek V4.1 Flash, the comparator is the highest score among
*all* eligible DeepSeek V4 Flash versions and tiers, including Flash Vision.

| Extra Tests | Weights | Grok 4.7−4.6 | 4.6−4.5 | V4.1 Flash−MiMo Pro | V4.1 Flash−best V4 Flash | Opus 5.5−5 | Fable 5.1−5 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| All 19 | 14/5/5/66/10 | +0.069 | +0.104 | +0.070 | +3.477 | +5.079 | +3.623 |
| All 19 | 16/5/5/69/5 | +0.334 | +0.139 | +0.093 | +3.539 | +5.285 | +3.651 |
| 17, without FrontierCode and EBR-bench | 15/5/5/69/6 | +0.212 | +0.121 | +0.155 | +3.501 | +5.207 | +3.635 |
| 14 with at least 10 fitting representatives | 15/5/5/68/7 | +0.232 | +0.103 | +0.106 | +3.506 | +5.190 | +3.689 |

The 17-test case excludes FrontierCode's model-specific agent evidence and
the four-representative EBR-bench fit.
The 14-test rule removes SWE-Marathon, Harvey LAB-AA, OSWorld 2.0,
ARC-AGI-3 Standard, and EBR-bench Card-ban based on a coverage threshold
specified independently of the named comparisons. The first two cases retain
all current Extra Tests. The cap is 16.9666123987326 with all 19 tests,
17.20686664 with the 17-test subset, and 16.49378194877355 with the 14-test
subset.

These are feasible arithmetic cases, not recommended default weights.
Knowledge rises from 16% to 66–69%, while Agentic and Hard Reasoning each fall
to 5%. The tightest relevant gap is only 0.069–0.103 points in the first case
and about 0.093–0.139 points in the second. A source refresh could reverse those
orders. Grok 4.7's highest scoring tier is high, Grok 4.6's is high, and Opus
5's is xhigh in these cases. Fable 5.1 becomes the overall rank 1 model, so the
change substantially alters the rest of the leaderboard.

Using the current 19-test board scores, allowing any nonnegative weights gives
a positive solution only when Knowledge is about 72% and some boards are zero.
With each board constrained to 5–45%, the best common margin is negative
(-1.131 points). A search over quality-motivated subsets and thousands of
additional subsets found no case with every board at least 5% and Knowledge at
most 60%; that search is exploratory, not a proof over all 19-test subsets.

## GPT-5.4 xhigh is not yet comparable

GPT-5.4 xhigh is excluded before scoring because both Coding Core results,
Terminal-Bench v4.0 and SciCode, are absent; AutomationBench-AA and GDP.pdf are
also absent, reaching four missing Core items. The [current AA model page](https://artificialanalysis.ai/models/gpt-5-4) and current AA evaluation
manifests return explicit nulls for these exact fields. Board weights and Extra
Test selection cannot repair an empty Core board.

[AA's March 2026 post](https://x.com/ArtificialAnlys/status/2029950497516573183)
has a historical SciCode chart labelling GPT-5.4 xhigh 57% after rounding;
[an Epoch data mirror](https://github.com/tobiasosborne/ai-agents-seminar/blob/dcfb8066af6de561705723477a459be1ebd8ee80/Wuerzburg-talk-2026/model-progress/data/epoch/scicode_external.csv)
records 56.5972%. The current AA manifest has that result as null. The
[OpenAI release page](https://openai.com/index/introducing-gpt-5-4/) reports
Terminal-Bench 2.0, which does not match the v4.0 Core protocol. None of those
values has been copied into current Core.

As a sensitivity check only, adding the historical 56.5972% SciCode value to
GPT-5.4 xhigh in memory would make it eligible, but it would still trail
GPT-5.6 Luna's highest tier by about 9.3–9.8 points in the four cases above.
This hypothetical value is not a published current AIndex result.

**Conclusion:** the four cases satisfy the six comparisons for which both
models have current AIndex scores. No verified case satisfies all seven requested
comparisons, because GPT-5.4 xhigh has no current AIndex score. No production
weights, Extra Test registry, scores, or generated rankings were changed.
