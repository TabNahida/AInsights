# TokenPlan pricing research and calculation playbook

Use this guide to turn subscription marketing into a reproducible cost explanation. Deliver the price paid, what it buys, the conditions for consuming it, and the cost of the same workload on a comparable PAYG service. “Effective price per million tokens” requires both a defensible denominator and explicit utilization assumptions.

The [September 22 audit](../../analysis/model-and-token-plan-audit-2026-09-22.md) contains live-source examples for Xiaomi, Baidu and Alibaba. Reviewed inputs are in [the example ledger](../../analysis/token-plan-examples-2026-09-22.json); reproduce the arithmetic with:

```powershell
python scripts/calculate_token_plan_examples.py --output analysis/token-plan-calculations-2026-09-22.json
```

This command is offline and does not refresh tariffs, spend API credits or change the site's pricing catalogue.

## Define the comparison unit

Use one record per **provider + product + region + billing mode + tier + term + model/API ID + pricing regime + effective period**. Do not merge:

- Token Plan, Coding Plan, consumer chat subscriptions, and ordinary API balances.
- Personal and team seats; domestic CNY and global USD tariffs.
- Monthly and annually prepaid plans; introductory, renewal, regular and time-of-day prices.
- Raw-token quotas, weighted token credits, monetary credits, points, requests and rolling-window allowances.
- Model variants, context brackets, real-time and batch inference, or priority/fast service tiers.

Ask for customer logs only if the task requires their actual bill. Public documentation is sufficient for labelled scenarios. Do not claim measured savings without measured workload and payment records.

## Research the governing terms

Read the official product/pricing page, billing rules, model support list, usage-limit documentation, promotion terms and API usage-field documentation. Follow links to resolve material ambiguity. Preserve:

| Field group | Required observations |
| --- | --- |
| Price | Native currency, tax treatment if published, upfront payment, term, list/renewal price, promotion eligibility and expiry |
| Quota | Amount, unit, reset/issuance schedule, rollover/expiry, shared pool, seat allocation |
| Debit | Per-model input/cache-read/cache-write/output/reasoning coefficients, tool/media charges, rounding and minimum debit |
| Constraints | Five-hour/seven-day/monthly caps, concurrency, allowed clients/use cases, throttling, rate tiers and endpoint |
| Exhaustion | Service stop, optional pack/upgrade, automatic overage, or manual PAYG switch; prerequisite subscription fee |
| Identity | Model/API ID, reasoning mode, region, long-context threshold, effective date and announced retirement |
| Provenance | URL, table/footnote locator, published/effective/accessed dates, exact observed values and unresolved conflicts |

A marketing example such as “200 tasks” is not a guaranteed token allowance. An illustrative “about 3 points” is not an exact tariff. A page's successful HTTP response does not prove the selected region or billing tab was read. Inspect the relevant table and its units.

## Decide whether a token conversion is supported

| Mechanism | What may be calculated | Comparison status |
| --- | --- | --- |
| Fixed raw-token quota, confirmed uniform debit | Full-use blended rate and utilization scenarios | Conditional effective token comparison |
| Public per-model credit coefficients | Separate input/cache/output rates and explicit workload cost | Conditional effective token comparison |
| Monetary credits with published API tariffs | Same-workload purchasing power, expiry and actual spend | Conditional; preserve model tariffs and credit restrictions |
| Dynamic credits without an exact published formula | Fee, observed/conditional credits consumed, cost per credit | No universal token rate |
| Prompts/requests, “up to” tasks or fair use | Price and constraints; empirical workload results if logs exist | No fixed token conversion |

Unsupported rates are `null`, not zero. “Not token-comparable” does not mean worthless; show the useful native-unit calculation. Unknown coefficients must not be reverse-engineered from a previous model or a competitor.

## Keep three prices distinct

1. **Cash paid:** subscription fee plus actual packs, overages, tools, taxes and other applicable charges for the stated period.
2. **Full-utilization allocated rate:** the fee distributed across all usable quota. This is a conditional accounting rate; it is not the incremental debit shown on an API invoice.
3. **Realized effective rate:** actual cash divided by actual delivered billable workload. Unused expired quota raises this rate. At zero usage, it is undefined; report the cash paid and no unit rate.

Buying a package does not make unused capacity a saving. Do not allocate the full fee independently to every model sharing the same quota. Allocate the common fee consistently or compare the whole workload basket.

## Formula sheet

Let `P` be the fee and `Q` the quota for the **same period**, `T_i` mutually exclusive billed token counts, and `a_i` credits per token for input, cache-read, cache-write and output categories as applicable. Include billed reasoning in output if the provider does so; do not count it twice. `M = 1,000,000`.

### Raw-token quota

For a genuinely uniform token pool:

```text
full-use currency/M tokens = P × M / Q_tokens
utilization u             = actual eligible tokens / Q_tokens
realized currency/M       = full-use rate / u        (0 < u ≤ 1)
```

First check whether cached tokens and output consume the same quota and whether all models share the same rule. Do not apply Baidu Token-mode arithmetic to Baidu point mode.

### Weighted credit quota

```text
credit debit C            = Σ(T_i × a_i) + applicable non-token credit charges
full-use component rate   = P / Q_credits × a_i × M
```

For a fixed token mix `w_i` summing to 1, with no additional charges:

```text
average credits/token     = Σ(w_i × a_i)
full capacity in M tokens = Q_credits / average credits/token / M
full-use mixed rate       = Σ(w_i × component rate_i)
credit utilization u      = C / Q_credits
realized mixed rate       = full-use mixed rate / u
```

The last identity assumes the same mix and debit regime. If tools/media also consume the pool, simulate their debits and retain those dimensions; a token-only rate may no longer describe the product adequately.

### PAYG and break-even

```text
PAYG cost = Σ(T_i / M × PAYG_rate_i) + tools + media + other applicable charges
plan cost = P + packs/overages + separate charges
```

For a fixed mix without extras, let `b` be the PAYG mixed currency/M and `r` the plan's full-use mixed rate:

```text
break-even M tokens = P / b
break-even utilization = r / b
```

Above that utilization the plan is cheaper; below it PAYG is cheaper. If `r/b > 1`, no utilization up to the included quota breaks even under those assumptions. A zero-cost PAYG baseline has no ordinary positive-fee break-even. Do not compare different model outputs as if equal token counts establish equal task quality.

### Promotions, time and term

- A price discount `d` changes `P` to `dP`. Use the exact displayed price when the rounded marketing discount disagrees: CNY 19.9 is not exactly half of CNY 40.
- A debit discount `k` changes eligible coefficients to `ka_i`. It increases capacity; it does not refund part of the subscription fee.
- For a mixed day/night workload, sum actual eligible category debits. A single average discount is valid only when the model/token mix and eligibility justify it.
- A quoted annual fee may already include its discount. Divide by annual quota once; do not apply the advertised multiplier again. Report upfront cash and amortized monthly cost separately.
- Annual total quota does not prove it is available on day one. Verify issuance and expiry before simulating bursts or rollover. Team annual terms may differ from personal annual terms.
- Stop before extrapolating past exhaustion. If switching manually to PAYG is allowed, model that explicitly; do not assume automatic overage or charge both services for the same tokens.

### Rolling windows and marginal packs

`weekly quota × 52/12` is only an annualized convention. It does not prove a monthly allowance. Record how windows start and reset, whether unused credits expire, and whether subscription expiry cuts a window short. Model demand by timestamp and reject a workload that breaches a short-window cap even if its monthly total looks feasible.

A CNY 100 pack containing 20,000 Credits costs CNY 0.005 per **additional credit**. If an active CNY 39 subscription is required, purchasing both costs CNY 139. Do not put the marginal pack rate into a cheapest-plan ranking as if the prerequisite fee did not exist.

## Minimum worked scenarios

For a convertible plan, provide full utilization, 50% and 25%; a concrete token volume; the same-model PAYG bill; and break-even where defined. Show first-purchase and off-peak cases separately from the regular base case. Include annual prepayment if it materially changes the decision.

AInsights currently uses `20% new input + 70% cached input + 10% output`. These are shares of **all tokens**, not a 70% hit rate applied to input after the fact. At that mix, cache hits are 70/90 of input. Preserve native currencies and apply long-context rules per request, not to the aggregate monthly token count.

If exact conversion is unavailable, give one native-unit calculation and state the missing evidence. If logs are available, preserve model/effort, token categories, timestamps, tool calls, credit deltas, retries and invoice periods. Describe resulting rates as empirical for that workload. A single request or rounded balance change cannot establish a universal coefficient.

## Repository integration and validation

1. Inspect `data/pricing/provider_pricing.json`, its supplement ordering, `scripts/build_docs_site.py`'s merge behavior, and `docs/app.js`'s `catalogOfferRates`, `pricingScenarioWeights` and `pricingBlendFromRates`.
2. Retain native price and fee/quota metadata. Use stable provider, plan, offer and source IDs. Each offer must reference an existing plan/provider/source and the intended model slug.
3. Keep `comparable=false` and component rates null for dynamic/unknown conversions. Label full-use assumptions for `effective-subscription` offers. Keep promotions, regular renewal prices, context thresholds and regional differences visible.
4. A scoped supplement may override stable IDs. `replaceProviders` removes that provider's existing plan/offer slice, so use it only with a complete intended replacement. The standalone `merge_provider_pricing_fragment.py` also replaces provider slices; do not feed it a few new offers and accidentally delete the rest.
5. Recompute important numbers independently from fee/quota/coefficients, not from already-rounded effective rates. Reconcile full capacity × rate back to the fee. Check units (`B=10^9`, `M=10^6`), period alignment, zero usage, promotions, duplicate fee allocation and quota limits.
6. Rebuild and validate only when production inputs change; inspect the resulting offer and frontend labels. A documentation-only example must not silently overwrite current prices.

The catalogue's top-level `asOf` can be the newest supplement date. Inspect each underlying source and FX observation. CNY converted using an August exchange rate is not a September USD quote. Prefer within-currency comparisons; if FX is required, preserve its dated source and distinguish conversion from the provider's native USD tariff.

## Required handoff

Deliver an input ledger with citations and effective/access dates, formulas, reproducible calculations, a small result table, and the conditions beside each conclusion. Identify unavailable evidence, stale production fields, and supported next updates. State whether results are published terms, conditional scenarios or observed bills. Do not call a full-utilization best case the user's “actual price.”

### Reusable agent task

> Read `docs/guides/token-plan-pricing-research.md`. Investigate [providers/plans] as of [date]. Read current official prices, quota/debit rules, model support, resets, promotions and exhaustion behavior. Preserve native currencies. Classify which plans support a token conversion. Calculate full-use and 50%/25% utilization, a concrete workload, matched PAYG cost and break-even; separate first-purchase, renewal, annual and off-peak cases. For dynamic credits, keep token rates null and provide a native-unit example. Save cited inputs and an offline reproducible calculation, report uncertainty and stale repository fields, and update production offers only where the evidence supports the exact mapping.
