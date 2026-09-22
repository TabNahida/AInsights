# Model coverage and TokenPlan research examples — September 22, 2026

## Scope and baseline

This records a completed production benchmark refresh and a TokenPlan worked-example handoff. Public source pages were read on September 22, 2026. The pricing examples are not measurements of a customer's bill. Calculations assume text-token workloads without taxes, paid tools, media or other extras; source-specific restrictions still apply.

The working branch was fast-forwarded to remote `main` commit `d8849e0` before the final audit. The inspected site payload was generated at `2026-09-22T03:11:21+00:00`. The earlier local September 19 snapshot did not contain these releases; conclusions based on that snapshot were superseded after synchronization.

## Before the refresh: models present, external evidence missing

| Exact site configuration | Catalogue | Missing AA Core observations | External benchmark rows | Reviewed visual rows | Provider offer rows |
| --- | --- | --- | ---: | ---: | ---: |
| MiMo-V2.6-Pro (`mimo-v2-6-pro`) | Present | Terminal-Bench v4.0; τ³-Banking; AA-Omniscience Accuracy | 0 | 0 | 0 |
| Grok 4.7 high (`grok-4-7-high`) | Present | Same three | 0 | 0 | 0 |
| Grok 4.7 xhigh (`grok-4-7`) | Present | Same three | 0 | 0 | 0 |

Counts refer to the generated model's `externalBenchmarks` and `visionBenchmarks`, and exact slug references in `providerPricing.offers`. Missing items are taken from `exactRankingProfile`; high and xhigh must be audited separately. Each configuration has eight distinct populated AA benchmark observations, plus the duplicate AA-LCR compatibility alias.

Zero provider offers does **not** mean zero price information: AA's base `pricing` fields already contain MiMo Pro USD 0.435 input / 0.0036 cached / 0.87 output and Grok USD 2 / 0.5 / 6 per million tokens. These agree with the reviewed base API pages. Provider-specific offers, plan inclusion and pricing conditions have not been attached to these new slugs.

The [Xiaomi API model list](https://mimo.mi.com/docs/zh-CN/quick-start/summary/model) also lists `mimo-v2.6-flash` and `mimo-v2.6-pro-ultraspeed`, neither present in the baseline snapshot. It lists 1M context and 128K maximum output for the new models; UltraSpeed requires a custom service arrangement. The refresh adds Flash from the final release table and official product identity; it does not equate arbitrary weight checkpoints or service variants.

### Published evidence found and ingested

| Source and locator | Observed result | Binding constraint |
| --- | --- | --- |
| [MiMo-V2.6-Pro-RL official card](https://huggingface.co/XiaomiMiMo/MiMo-V2.6-Pro-RL), Evaluation Results | Pro / Flash: DeepSWE v1.1 71.9 / 67.9; Terminal Bench 4.0 34.9 / 28.8; Terminal Bench 2.1 89.9 / 87.6 | Final product table independently confirmed in report Table 3, page 26; bind to the released model with model-card-default configuration confidence, without inventing an API effort |
| Same card, General Agent and Visual Agent sections | Pro / Flash: OSWorld-Verified 82.0 / 80.8; MiMo VisualCoding 72.3 / 71.5 | Agent/visual-coding results are not generic vision accuracy; preserve protocol and benchmark identity |
| [Grok 4.7 release](https://x.ai/news/grok-4-7), Model Improvements table | CursorBench 4.0 46.3%; Terminal-Bench 4.0 38.0%; EEBench 64.0% | Column is xhigh; new benchmark versions need explicit definitions |
| Same Grok table, starred DeepSWE v1.1 row | 71.0% | Footnote explicitly says **high effort**, despite the xhigh column heading |

These observations close the external ingestion gap; they do not replace missing AA Core values with vendor runs. The [MiMo release narrative](https://mimo.mi.com/docs/zh-CN/news/latest/v2-6) separately reports training-stage DeepSWE improvements ending at Pro 72.6 and Flash 65.7. The [technical report](https://huggingface.co/XiaomiMiMo/MiMo-V2.6-Pro-RL/blob/main/MiMo_V2_6_technical_report.pdf), section 5.4 and final Table 3, resolves this as different training-stage versus final-product evidence. The final table supplies the ingested values. Section 5.2 discloses corrected CyberGym environments, now recorded under a distinct benchmark ID. Internal tests and raw Elo observations retain their own labels and are excluded from ranking evidence.

### After the refresh: 41 official observations added

The rebuilt payload at `2026-09-22T04:10:41+00:00` contains 657 model rows. Live parsed values matched all 41 reviewed source observations. The [source verification ledger](model-release-source-checks-2026-09-22.json) records URLs, access times, hashes and report locators.

| Configuration | External rows before → after | AIndex before → after | Exact-configuration rank before → after |
| --- | ---: | ---: | ---: |
| MiMo-V2.6-Pro | 0 → 17 | 32.955197 → 32.955197 | 75 → 75 |
| MiMo-V2.6-Flash | Absent → 16 | Unranked | Unranked |
| Grok 4.7 xhigh | 0 → 7 | 29.325058 → 29.325058 | 104 → 104 |
| Grok 4.7 high | 0 → 1 | 29.975649 → 29.975649 | 99 → 99 |

Ranks above are the generated `exactRankingProfile.publicationRank`, not the UI's deduplicated representative rank. Grok's starred 71.0% DeepSWE result belongs only to high; the other seven results belong to xhigh. Flash is now a browsable external-only catalogue entry without sufficient AA Core for ranking. No general vision-accuracy results were established for these configurations; MiMo Visual Coding is an internal agent task and does not fill MMMU-Pro.

The refreshed live AA import still leaves Terminal-Bench v4.0, τ³-Banking and AA-Omniscience Accuracy missing for Pro and both Grok configurations. Their fixed Core shares contribute no points, and incomplete-Core boards receive no extension bonus. Richer official coverage therefore leaves these AIndex values unchanged. No weights or missing-data rules were changed to raise named models' scores.

The [Grok model page](https://docs.x.ai/developers/models/grok-4.7) confirms 500K context, text/image input, text output, low/medium/high/xhigh reasoning with high as default, and a higher-price condition above 200K context. A USD 2/6 headline alone is not a complete tariff. The [release](https://x.ai/news/grok-4-7) also advertises a fast variant at twice the price. This audit has not reconstructed its complete regional/long-context price matrix.

### Why the automation did not complete the job

The daily job imports AA and rebuilds the site. Before this update, the Monday external-source discovery lists covered Qwen, GLM, Kimi and DeepSeek, excluding Xiaomi and xAI; curated Xiaomi coverage stopped at V2.5. This update adds Xiaomi organization discovery and three maintained source specifications, including a Grok parser that checks column order and the high-effort footnote. Future collectors can refresh these observations. Neither workflow refreshes the researched provider-pricing fragments. A recent AA snapshot can still coexist with older provider-plan data.

The current pricing catalogue's FX observations are dated August 10. The Xiaomi, Baidu and Alibaba research fragments inspected here were checked August 11–12. A new `generatedAt` date must not be presented as fresh verification of those prices.

## Worked prices from current official rules

All token-mix calculations below use the site's scenario: **20% uncached input + 70% cached input + 10% output**, measured as shares of total billable tokens. This is a hypothetical workload. All prices below are in the stated native currency; there is no FX conversion.

### 1. Xiaomi Lite: published credit formula, narrow daytime savings

Sources: [Token Plan](https://mimo.mi.com/docs/zh-CN/price/token-plan), [PAYG](https://mimo.mi.com/docs/zh-CN/price/pay-as-you-go), both showing September 21 updates when read.

Personal Lite costs CNY 39/month for 4.1B Credits. MiMo-V2.6-Pro consumes 300 Credits per uncached input token, 2.5 per cache-hit token, and 600 per output token:

```text
input rate  = 39 / 4,100,000,000 × 300 × 1,000,000 = CNY 2.853659/M
cache rate  = 39 / 4,100,000,000 × 2.5 × 1,000,000 = CNY 0.023780/M
output rate = 39 / 4,100,000,000 × 600 × 1,000,000 = CNY 5.707317/M
mix debit   = 0.2×300 + 0.7×2.5 + 0.1×600 = 121.75 Credits/token
capacity    = 4.1B / 121.75 = 33.675565M mixed tokens
```

| Plan / model / regime | Full-use mixed cost/M | At 50% credit use | At 25% credit use | Matched PAYG/M | Break-even credit use |
| --- | ---: | ---: | ---: | ---: | ---: |
| CN Lite monthly, V2.6 Pro, daytime | CNY 1.158110 | CNY 2.316220 | CNY 4.632439 | CNY 1.217500 | 95.12% |
| CN Lite monthly, V2.6 Flash, daytime | CNY 0.393805 | CNY 0.787610 | CNY 1.575220 | CNY 0.414000 | 95.12% |
| Global Lite monthly, V2.6 Pro, daytime | USD 0.178171 | USD 0.356341 | USD 0.712683 | USD 0.176520 | 100.94% — beyond included quota |
| CN Lite annual, V2.6 Pro, daytime | CNY 1.019137 | CNY 2.038273 | CNY 4.076546 | CNY 1.217500 | 83.71% of annual quota |

The CN monthly plan is only about 4.88% cheaper than regular PAYG when fully consumed. At the published global USD tariff, the ordinary daytime Lite plan is about 0.94% **more expensive even at full use** for this mix. Do not carry a CN savings conclusion into the global tariff.

For a concrete month of **10M tokens** (2M uncached + 7M cached + 1M output), Pro consumes 1.2175B Credits, or 29.70% of Lite. The customer pays CNY 39; the realized rate is **CNY 3.90/M**, while the same PAYG workload costs **CNY 12.175 total**. The full-use CNY 1.158110/M figure does not describe that customer's realized cost.

The annual case pays **CNY 411.84 upfront**, equivalent to CNY 34.32/month, for the published 49.2B annual Credits. Its 0.88 discount is already included. Annual allocation timing and rollover must be verified before treating that capacity as available for a one-month burst.

### 2. Xiaomi discounts change capacity or fee, not both by default

Eligible off-peak calls between 00:00 and 08:00 China Standard Time consume 0.8× Credits. With the same CNY 39 fee, an entirely off-peak Pro workload has 42.094456M-token full capacity, a **CNY 0.926488/M** full-use rate and a **76.10%** break-even credit utilization. At the same fixed 10M-token volume, the cash paid remains CNY 39.

An eligible first personal monthly purchase costs 39×0.88 = **CNY 34.32**. Its daytime full-use Pro rate is **CNY 1.019137/M**. This first-purchase benefit is separate from normal renewal and is not applied on top of the already-discounted annual fee. These cases are shown separately, without assuming every customer or request qualifies.

Exhaustion stops Token Plan service. The docs offer upgrades or a switch to ordinary API; they do not describe automatic PAYG overflow. The PAYG page also charges search separately. These token-only examples exclude search.

### 3. Baidu Lite: Token mode and point mode must remain separate

Sources: [Token Plan documentation](https://cloud.baidu.com/doc/qianfan/s/Dmrabu8b6), updated September 18; [product/promotions](https://cloud.baidu.com/product/codingplan.html), accessed September 22.

The documentation confirms two distinct Lite modes at CNY 40/month: **42M raw tokens** or **6,600 points**. Token mode counts input, output and cache hits uniformly:

| Token-mode case | Effective CNY/M tokens |
| --- | ---: |
| Regular CNY 40, all 42M used | 0.952381 |
| Regular CNY 40, 21M used | 1.904762 |
| Regular CNY 40, 10.5M used | 3.809524 |
| Conditional CNY 19.9 first purchase, all 42M used | 0.473810 |
| Conditional first-renewal 60% price, CNY 24, all 42M used | 0.571429 |

The promotional examples require eligibility and confirmation of the selected Token-mode price at checkout: the fetched product page defaults to **point mode**. Its first-renewal discount is an activity benefit, not a permanent renewal promise. The exact CNY 19.9 displayed amount takes precedence over a rounded “half price” label.

Point mode is different. The official example says approximately 853 input + 10,240 cache-hit + 427 output tokens consume approximately 3 points for DeepSeek V4 Pro. Repeating exactly that illustrative request would yield `6600 / 3 × 11520 = 25.344M` tokens and about `40 / 25.344 = CNY 1.578283/M`. This is **illustrative extrapolation, not a published exact rate**, because debit is dynamic and the example is approximate. It must remain ineligible for universal token-price rankings.

The repository's old uniform-token offer is therefore not inherently arithmetically wrong; it is incomplete unless labelled Token mode and separated from current point-mode products and promotions. We did not estimate a Baidu-versus-PAYG break-even without an independently verified matching model tariff.

### 4. Alibaba Lite: calculate Credits honestly, leave token price unknown

Source: [official Personal Token Plan overview](https://help.aliyun.com/zh/model-studio/token-plan-personal-overview), accessed September 22.

Lite currently advertises CNY 39/month (list CNY 60), with 2,500 Credits per seven-day window. Each window starts at its first call; unused credits do not carry over. The page says request debit depends on model, tokens, reasoning and tools, with actual usage recorded in the console. It does not establish a stable universal token formula.

| Conditional use within an active subscription | Credits consumed | CNY 39 / consumed Credits |
| --- | ---: | ---: |
| Four fully consumed windows | 10,000 | 0.003900/Credit |
| Five windows fully consumed before subscription expiry, if timing permits | 12,500 | 0.003120/Credit |

The existing `2500 × 52/12 = 10,833.333333` monthly equivalent yields CNY 0.003600/Credit. That is an annualized convention, **not a guaranteed monthly quota**. Window timing, demand and expiry decide actual consumption. None of these figures can be labelled currency per token.

An extra pack costs CNY 100 for 20,000 Credits: **CNY 0.005 per marginal credit**. It requires an active subscription, so buying Lite plus one pack costs **CNY 139**, not CNY 100. The new Essential tier and usage-pack rules also show why August data needs a fresh research pass.

## Deliverables, validation and remaining work

- [Model research guide](../docs/guides/model-data-research.md): source discovery, exact identities, missing-data states, benchmark semantics, repository integration and validation.
- [TokenPlan pricing guide](../docs/guides/token-plan-pricing-research.md): comparability, formulas, cash versus allocated cost, utilization, promotions, resets, packs and reporting.
- [Reviewed input ledger](token-plan-examples-2026-09-22.json), [calculator](../scripts/calculate_token_plan_examples.py), and [recomputed results](token-plan-calculations-2026-09-22.json).

The calculator uses decimal arithmetic and reconciles capacity × full-use rate with the fee. Important results were independently checked with rational arithmetic. Production benchmark data and generated pages were refreshed; production provider offers and ranking policy were not changed. No customer usage or checkout was accessed.

Validation passed: all 365 Python tests (including parser/configuration regressions), 13 frontend tests, official-source ownership validation, and an independent Mixed Core production recomputation. The affected model pages were inspected in the browser, and the TokenPlan calculation artifact exactly matches recomputation from its reviewed inputs. Repository instructions and the English playbook now require supported observations to reach maintained data and generated pages rather than ending at an audit.

Remaining evidence work: attach current provider offers; research UltraSpeed's custom-service identity and conditions; distinguish Baidu billing modes and promotional terms in production offers; and refresh Alibaba's supported models, tiers and window metadata. The three absent AA Core observations remain missing until matching evaluator evidence becomes available. Those gaps are separate from the 41 official release observations now ingested.
