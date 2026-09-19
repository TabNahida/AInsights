# Visual evidence audit — 2026-09-19

## Scope and outcome

The snapshot has 653 configurations; 261 have AA MMMU-Pro observations. Of the 392 without AA MMMU-Pro, 69 list Image input. Missing image metadata is not proof that a model cannot process images.

This update adds 54 manually reviewed official results. Within the 69 missing-AA image configurations, 20 now have an exact-configuration visual result, 18 have reference evidence only (including existing external evidence), and 31 remain unverified. These are configuration counts, not model-family counts.

## Interpretation rules

- Keep AA and official evaluations separate, including MMMU, MMMU-Pro variants, MathVista, CharXiv and Chartography.
- Select one visual test for the whole comparison; never fill a missing point using another test.
- Only explicitly matched configurations can be plotted. Other effort tiers remain reference evidence.
- Official results receive no cross-model mean or rank: protocols may differ even with the same test name.
- Visual evidence does not enter scores, AIndex, Custom calculations or ranking profiles.
- Exact means the reviewed source matches the named configuration; unspecified evaluation details remain documented as unspecified.

## Reviewed sources

- [OpenAI GPT-5.2 release](https://openai.com/index/introducing-gpt-5-2/): Appendix: Vision; benchmark methodology footnote
- [Anthropic Fable 5.1 system card](https://www.anthropic.com/claude-fable-5-1-mythos-5-1-system-card): Section 8.14.1, pages 184-186
- [Anthropic Sonnet 5 system card](https://www-cdn.anthropic.com/9e6a1044980d8c4ed85669faf9c2a8342e2e9f1e/Claude%20Sonnet%205%20System%20Card.pdf): Section 8.10.5, pages 128-129
- [Mistral Small 3.1 official model card](https://huggingface.co/mistralai/Mistral-Small-3.1-24B-Instruct-2503): Instruction Evals / Vision table (not the Base model table)
- [ServiceNow Apriel 1.6 official model card](https://huggingface.co/ServiceNow-AI/Apriel-1.6-15b-Thinker): Multimodal evaluation table, Apriel-1.6-15B-Thinker column
- [LG AI EXAONE 4.5 official model card](https://huggingface.co/LGAI-EXAONE/EXAONE-4.5-33B): Vision-language Tasks, EXAONE 4.5 33B (Reasoning) column
- [Anthropic June 2024 vision evaluations](https://www.anthropic.com/news/claude-3-5-sonnet): Claude 3.5 Sonnet vision evals image
- [Anthropic Claude 3.7 launch evaluations](https://www.anthropic.com/news/claude-3-7-sonnet): Visual reasoning MMMU validation row
- [Anthropic Claude 4 launch evaluations](https://www.anthropic.com/news/claude-4): Evaluation methodology: MMMU without extended thinking
- [OpenAI o1 developer release](https://openai.com/index/o1-and-new-tools-for-developers/): Evaluation table / Vision
- [Google Gemini 1.5 technical report](https://storage.googleapis.com/deepmind-media/gemini/gemini_v1_5_report.pdf): Table 18, page 39
- [Anthropic Claude 3 model card](https://www.anthropic.com/claude-3-model-card): Table 3, page 8; section 5.3
- [Google Gemini 2.0 February release](https://blog.google/technology/google-deepmind/gemini-model-updates-february-2025/): Benchmark table image: Image / MMMU row (gemini_benchmarks_cropped_light1x.gif)
- [Google Gemini 2.5 Pro March release](https://blog.google/technology/google-deepmind/gemini-model-thinking-updates-march-2025/): Benchmark image: visual reasoning MMMU row and methodology footer; Benchmark image: image understanding Vibe-Eval row and methodology footer
- [OpenAI GPT-4.5 release](https://openai.com/index/introducing-gpt-4-5/): Appendix: Model evaluation scores, MMMU (multimodal) row
- [OpenAI GPT-4o May release](https://openai.com/index/hello-gpt-4o/): Model evaluations > Vision understanding evals; gpt-40-01_dark.png; Model evaluations > Vision understanding evals; GPT-4T 2024-04-09 column

## Outstanding verification

Not verified does not mean no test exists. Do not copy regular-model scores into Pro or Instant releases. GPT-5.2/5.5 release tables leave relevant Pro vision entries empty. Fable/Sonnet system cards report max-effort results; lower-tier chart dots without numeric labels are insufficient.

GLM-5.3-Flash release text and all three evaluation/architecture images were checked: the displayed results cover coding, agentic work and intelligence, without a separate visual score. Agnes 2.5 Pro Alpha, Celeris-1, HyperCLOVA, Gemma 3n and Grok 4.6 pages checked in this pass did not yield a verified compatible numeric visual result. Some older release/PDF routes were unavailable. Other configurations below remain pending source/snapshot verification.

GPT-4o May results are references for later November/ChatGPT snapshots. GPT-4 Turbo results explicitly name 2024-04-09, while the local row is dated November 2023. Gemini 2.0 Flash-Lite results name the February 5 public preview, so the February 25 GA configuration remains reference only.

## Missing-AA image configuration inventory

| Configuration | Status |
| --- | --- |
| `agnes-2-5-pro-alpha` | Unverified in this pass |
| `agnes-3-0-flash` | Unverified in this pass |
| `apriel-v1-6-15b-thinker` | Exact result: MMMU, MMMU-Pro (10 choice), MMMU-Pro (vision only), MathVista, CharXiv Reasoning (published protocol) |
| `celeris-1` | Unverified in this pass |
| `claude-3-7-sonnet-thinking` | Reference only; no matching configuration score |
| `claude-3-opus` | Exact result: MMMU, MathVista |
| `claude-3-sonnet` | Exact result: MMMU, MathVista |
| `claude-35-sonnet` | Exact result: MMMU |
| `claude-35-sonnet-june-24` | Exact result: MMMU, MathVista |
| `claude-4-1-opus` | Unverified in this pass |
| `claude-4-opus` | Exact result: MMMU |
| `claude-4-opus-thinking` | Reference only; no matching configuration score |
| `claude-fable-5` | Reference only; no matching configuration score |
| `claude-fable-5-1` | Exact result: Chartography (no tools), Chartography (with tools) |
| `claude-fable-5-1-high` | Reference only; no matching configuration score |
| `claude-fable-5-1-low` | Reference only; no matching configuration score |
| `claude-fable-5-1-medium` | Reference only; no matching configuration score |
| `claude-fable-5-1-xhigh` | Reference only; no matching configuration score |
| `claude-opus-4-8` | Exact result: CharXiv Reasoning (no tools), CharXiv Reasoning (with tools) |
| `claude-sonnet-5-high` | Reference only; no matching configuration score |
| `claude-sonnet-5-low` | Reference only; no matching configuration score |
| `claude-sonnet-5-medium` | Reference only; no matching configuration score |
| `claude-sonnet-5-xhigh` | Reference only; no matching configuration score |
| `exaone-4-5-33b-non-reasoning` | Reference only; no matching configuration score |
| `gemini-1-0-pro` | Exact result: MMMU, MathVista |
| `gemini-1-5-flash-may-2024` | Exact result: MMMU, MathVista |
| `gemini-1-5-pro-may-2024` | Exact result: MMMU, MathVista |
| `gemini-2-0-flash` | Exact result: MMMU |
| `gemini-2-0-flash-experimental` | Unverified in this pass |
| `gemini-2-0-flash-lite-001` | Reference only; no matching configuration score |
| `gemini-2-0-flash-lite-preview` | Exact result: MMMU |
| `gemini-2-0-flash-thinking-exp-0121` | Unverified in this pass |
| `gemini-2-0-flash-thinking-exp-1219` | Unverified in this pass |
| `gemini-2-0-pro-experimental-02-05` | Exact result: MMMU |
| `gemini-2-5-flash-reasoning-04-2025` | Unverified in this pass |
| `gemini-2-5-pro-03-25` | Exact result: MMMU, Vibe-Eval (Reka) |
| `gemini-3-pro-low` | Unverified in this pass |
| `gemma-3n-e2b` | Unverified in this pass |
| `glm-5-3-flash` | Unverified in this pass |
| `gpt-4-5` | Exact result: MMMU |
| `gpt-4-turbo` | Reference only; no matching configuration score |
| `gpt-4o` | Reference only; no matching configuration score |
| `gpt-4o-2024-05-13` | Exact result: MMMU, MathVista |
| `gpt-4o-chatgpt` | Reference only; no matching configuration score |
| `gpt-4o-chatgpt-03-25` | Reference only; no matching configuration score |
| `gpt-5-2` | Exact result: MMMU-Pro (no tools), MMMU-Pro (with tools), CharXiv Reasoning (no tools), CharXiv Reasoning (with tools) |
| `gpt-5-4-pro` | Unverified in this pass |
| `gpt-5-5-instant-05-26` | Unverified in this pass |
| `gpt-5-5-instant-06-26` | Unverified in this pass |
| `gpt-5-5-pro` | Unverified in this pass |
| `gpt-5-chatgpt` | Unverified in this pass |
| `grok-4-6` | Unverified in this pass |
| `grok-4-6-low` | Unverified in this pass |
| `grok-4-6-medium` | Unverified in this pass |
| `grok-4-6-xhigh` | Unverified in this pass |
| `hyperclova-x-seed-think-32b` | Unverified in this pass |
| `kimi-k2-6-non-reasoning` | Reference only; no matching configuration score |
| `kimi-k2-7-code` | Unverified in this pass |
| `lfm-40b` | Unverified in this pass |
| `mistral-small-3-1` | Exact result: MMMU-Pro, MMMU, MathVista |
| `muse-spark-1-1` | Unverified in this pass |
| `muse-spark-1-2` | Unverified in this pass |
| `muse-spark-1-3` | Unverified in this pass |
| `nex-n2-pro` | Unverified in this pass |
| `nova-2-0-pro` | Unverified in this pass |
| `o1` | Exact result: MMMU, MathVista |
| `o1-pro` | Unverified in this pass |
| `o3-pro` | Unverified in this pass |
| `reka-flash` | Unverified in this pass |

## Validation

- Generated model payload differs only by the new visionBenchmarks field and generation timestamp. Existing scores, profiles and other model fields are identical to the previous commit.
- 358 Python tests and 11 frontend behavior tests pass; the independent production ranking validator passes.
- Browser checks cover desktop/mobile lab layout, numeric input and slider synchronization, input clamping, normalization, mode keyboard navigation and official visual benchmark selection.

## Remote data reconciliation

Merged the September 19 automatic update at `670023b` and regenerated both static payloads from its latest inputs. The 653 model records retain all remote non-vision data; rebuilt ranking profiles differ only in 12 floating-point values at machine precision. The independent production validator passes. A static-payload regression verifies models.js equals models.json and every generated visionBenchmarks field matches the registry attachment.

When a comparison selects AA MMMU-Pro, a Claude configuration measured on another test can still have a missing radar point. The page now displays its available tested scores and switch buttons above the radar. Reference-only configurations receive an explicit explanation instead of an unexplained dash.
