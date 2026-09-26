# Extra Tests review — updated 2026-09-25

Mixed Core 07 now permits **19** difficult, source-backed Extra Tests, up from
eight in the September 23 review. The eight Core items, only-add
positive-residual formula, and eligibility rules are unchanged. The five board
weights are now Coding 24%, Agentic 24%, Hard Reasoning 27%, Knowledge 16%,
and Instruction 9%. A test
needs at least three exact-configuration default representatives with complete
Core on its board. The item must have a reviewed source, task version, score
definition, and operator. Sparse fits are sensitive to new observations; fitted
counts and trend parameters are published in `docs/data/models.json`.

## Current registry

`Exact configs` counts all exactly matched site configurations; `Fit n` counts
eligible default representatives with exact score and complete board Core.
Creators and medians use that fitting population. Reference-only or unmatched
vendor rows are excluded. Recompute the table with
`python -B -m analysis.audit_extra_test_coverage` after a site build.

| Board | Test | Exact configs | Fit n / creators | Median | Source and pinned protocol |
| --- | --- | ---: | ---: | ---: | --- |
| Coding | [FrontierCode v1.1 Main](https://cognition.com/frontiercode) | 61 | 17 / 5 | 42.40% | Cognition owner-run Score; model-specific agent harness and explicit effort. Diamond is deprecated; Cognition's agent business is disclosed. |
| Coding | [DeepSWE v1.1](https://deepswe.datacurve.ai/) | 51 | 17 / 7 | 67.04% | DataCurve/Pier owner run; 113 tasks, mini-swe-agent, four repeats, pass fraction over scored attempts. No vendor-reported value is merged. |
| Coding | [SWE-Marathon v1.1](https://www.swe-marathon.org/) | 7 | 7 / 4 | 32.50% | Owner page bundle; 20 long software tasks, eight binary trials each. Agents vary by model. GLM has 50 trial error status labels, three alongside positive binary rewards; published binary rewards are used. |
| Agentic/tool work | [APEX-Agents-AA](https://artificialanalysis.ai/evaluations/apex-agents-aa) | 31 | 23 / 13 | 27.43% | AA runs a common Stirrup agent on 452 public Mercor tasks, with Archipelago MCP tools, three repeats, strict pass@1, and Gemini 3 Flash low as judge. Immutable task and agent revisions are not published. |
| Agentic/tool work | [AA-AnalystAgent pass^5](https://artificialanalysis.ai/evaluations/aa-analyst-agent) | 15 | 14 / 8 | 46.88% | AA private 80-task analyst set; all five independent attempts must pass. |
| Agentic/tool work | [Terminal-Bench-Science v0.1.0](https://artificialanalysis.ai/evaluations/terminal-bench-science) | 26 | 14 / 8 | 9.76% | AA mini-swe-agent; 70 science tasks, mean pass@1 over three runs. Its task set has no same-name overlap with Terminal-Bench v4's 66 Core tasks, but the ecosystem and agent are related. |
| Agentic/tool work | [AA-Briefcase v1.1 Rubric Pass Rate](https://artificialanalysis.ai/evaluations/aa-briefcase?results=rubric-score) | 32 | 19 / 12 | 42.12% | AA private 91-task artifact set; native rubric pass fraction, separate from Elo. |
| Agentic/tool work | [Harvey LAB-AA All-pass Rate](https://artificialanalysis.ai/evaluations/harvey-lab-aa?eval-score=all-pass-rate) | 14 | 9 / 6 | 6.67% | AA private 120-task legal set; every rubric criterion must pass, with a single LLM judge. |
| Agentic/tool work | [Toolathlon-Verified](https://hkust.mintlify.app/docs/leaderboard) | 17 | 17 / 10 | 59.90% | HKUST owner-run Pass@1, Default agent; older Toolathlon and vendor submissions stay separate. |
| Agentic/tool work | [OSWorld 2.0](https://osworld-v2.xlang.ai/) | 6 | 5 / 4 | 4.60% | Official v2026.06.24 full 108-task set, standard tools, 500 steps, binary completion; excludes batch tools, other releases, offline subsets, and partial reward. |
| Agentic/tool work | [ARC-AGI-3 Standard](https://arcprize.org/leaderboard) | 34 | 7 / 3 | 2.11% | ARC Prize Standard harness; Provider Adapter and vendor results remain separate. |
| Agentic/tool work | [Agents' Last Exam ALE-V1 Overall pass rate](https://agents-last-exam.org/leaderboard) | 46 | 11 / 6 | 28.29% | Berkeley RDI owner leaderboard; exact effort and disclosed per-model agent harness, separate from partial-credit Score. |
| Hard reasoning | [FrontierMath Tier 4 v2](https://epoch.ai/benchmarks/frontiermath-tier-4-v2) | 40 | 25 / 9 | 29.27% | Epoch-run export; distinct from older problem sets and vendor-reported v2. OpenAI commissioned the benchmark and received substantial problem/answer access. |
| Hard reasoning | [Chess Puzzles v1.1.6](https://epoch.ai/benchmarks/chess-puzzles) | 120 | 38 / 12 | 21.00% | Epoch run-level scores on 100 unpublished generated FEN positions, with a unique best move. Related to Mystery's one-step game skill. |
| Hard reasoning | [Mystery Game Puzzles v1.0.4](https://epoch.ai/benchmarks/mystery-game-puzzles) | 68 | 24 / 10 | 33.00% | Epoch run-level scores on 100 hidden-identity games with text state and minimal agent. Separate tasks but a related one-step reasoning signal. |
| Hard reasoning | [EBR-bench v4 Card-ban](https://epoch.ai/benchmarks/ebr-bench) | 4 | 4 / 2 | 49.52% | Four page-confirmed Card-ban single-agent runs only. The CSV lacks per-row v4 labels, so exact run IDs and the hashed methodology page pin the selection; small fit is fragile. |
| Hard reasoning | [Humanity's Last Exam (AA, no tools)](https://artificialanalysis.ai/evaluations/humanitys-last-exam) | 636 | 135 / 34 | 25.21% | AA common protocol on the CAIS/Scale AI benchmark. |
| Knowledge/science | [MLCR-AA Overall](https://artificialanalysis.ai/evaluations/mlcr-aa) | 31 | 27 / 15 | 21.67% | AA private medical long-context tasks; Overall combines accuracy, completeness, and conciseness. |
| Instruction/context | [IFBench (AA)](https://artificialanalysis.ai/evaluations/ifbench) | 450 | 72 / 20 | 65.65% | AA runs 294 questions over five repeats using the official loose mode; Score is prompt-level accuracy, separate from vendor reports and multi-turn IFBench. |

The five new AA page metrics have a checked public SSR snapshot with page
hashes, exact AA slugs, metric selectors, selected-chart row counts, and
matching site model keys. Owner leaderboards for FrontierCode, FrontierMath,
ARC-AGI-3, ALE-V1, Toolathlon, OSWorld, DeepSWE, SWE-Marathon, Epoch Chess,
Mystery, and EBR have distinct benchmark IDs
and pinned snapshots under `data/benchmarks/`. Parsers under `benchmarks/` check
the content hashes and protocol fields. The official OSWorld snapshot has 50
rows, seven under the selected protocol, six exact site configurations and five
fitting representatives; the DeepSWE snapshot has 70 rows, 69 common-harness
full-task rows, 51 exact site configurations and 17 fitting representatives.
Epoch Chess and Mystery use a filtered copy of the
public run-level export, and EBR uses only four current-rule run IDs confirmed
by Epoch's v4 methodology note. SWE-Marathon's pinned page bundle retains all
20 tasks and the eight binary trial rewards for each of seven mapped models.
The source URL, exact configuration, structured agent/harness fields where
provided, and score provenance remain visible on each benchmark page.

This refresh added 54 exact configurations across DeepSWE, OSWorld,
Toolathlon, ARC-AGI-3 and ALE-V1, plus 142 from already pinned Epoch
FrontierMath, Chess and Mystery run exports. The FrontierCode official JSON's
61 mappable Main rows matched the prior CSV; SWE-Marathon's public bundle was
unchanged. AA's five new evaluation pages, APEX and IFBench had no score
changes. A live AA catalogue refresh added three HLE no-tools configurations
and removed three delisted Agnes configurations. Remaining owner rows are
unmatched chiefly because of absent effort or checkpoint, fallback ambiguity,
another harness (including ARC Provider Adapter), or no exact site model. They
remain outside the scoring input.

## Exclusions and limits

- AIME, LiveCodeBench, τ² Telecom, MMMU-Pro, MMLU-Pro, and several short tests
  have current frontier scores near their ceilings. A high score does not prove
  contamination or intentional gaming.
- [Epoch AI's SWE-Bench Pro review](https://epoch.ai/benchmarks/swe-bench-pro/review)
  found substantial task and scoring defects. It is removed from current Extra
  slots while collected scores stay visible.
- HLE with tools remains viewable but is not an Extra Test. Published rows mix
  vendor-specific tools, search, judging and sampling; they cannot define one
  comparable result protocol and reuse the no-tools HLE question family.
- IBM's ITBench-AA and ServiceNow's EnterpriseOps-Gym-AA are controlled by
  ranked model vendors, even though AA runs their evaluations independently.
- Terminal-Bench Hard shares the Core family. FrontierCode Diamond is
  deprecated. FrontierMath v2 corrected a large share of the earlier set, so
  earlier FrontierMath versions cannot make another family bonus.
- NL2Repo has no current uniform owner-run table. SEC-Bench Pro, Gaia2-CLI, ExploitGym, and
  MirrorCode lack three exact-config, Core-complete representatives under one
  pinned current protocol. MathArena Apex is deprecated.
- Results based on a model-specific agent or a single LLM judge may differ in
  ways beyond bare-model ability. APEX's common AA protocol is unusually well
  disclosed, but its dataset, agent, grader and environment commits are not
  immutable public pins. These limitations are disclosed in the registry.

## Rebuild and validation

After the 19-test registry was rebuilt on the September 25 source snapshot,
**135** default representatives and **200** exact configurations passed the
Core eligibility rules. The independently reproduced pooled board cap is
**16.9666123987326** (the previous 20-test snapshot cap was
**16.874763378317844**). Every
extension metric is enabled with at least three fitting representatives.
New source rows, the HLE-with-tools exclusion, and population changes alter the
anonymous fitted trends and pooled cap; the new board weights also change final
scores. No named-model weight or score correction was used.

On the same source snapshot, the preceding 20/20/30/15/15 weights place
GPT-6 Astra (max), Claude Fable 5.1 (max with fallback), and Claude Opus 5
(max) first through third at 59.841045, 56.997962, and 53.749230. The
requested 24/24/27/16/9 weights keep that order at 59.231968, 56.718985,
and 52.956193. The pooled residual cap is unchanged by board weights.

Reproduce the pinned source refresh, site build, and independent validation:

```text
python benchmarks/collect_benchmark_scores.py --pinned-only --output-json data/benchmarks/benchmark_scores.json
python scripts/build_docs_site.py
python -B analysis/irt_leaderboard_exploration/validate_mixed_core_production.py --input docs/data/models.json
python -B -m analysis.audit_extra_test_coverage
```
