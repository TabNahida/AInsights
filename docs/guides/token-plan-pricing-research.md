# TokenPlan prices: tools and a MiMo example

Run commands from the repository root. Full-quota cost is not a customer's actual bill.

## 1. Use the existing tools

Recompute the reviewed examples offline with Python's standard library:

```powershell
python scripts/calculate_token_plan_examples.py --output analysis/token-plan-calculations-2026-09-22.json
```

Inputs: [dated price ledger](../../analysis/token-plan-examples-2026-09-22.json). Outputs: fees, credit capacity, component rates, utilization scenarios and PAYG break-even. This command does **not** fetch current tariffs, call a paid API or update production offers. `--input path.json` accepts another ledger with the same schema; `credit_case(case, weights)` in the script calculates a single weighted-credit plan.

For production updates, inspect `data/pricing/provider_pricing.json` and its ordered supplements, then edit the appropriate fragment. Later supplements can override earlier IDs. Validate a prepared fragment with:

```powershell
python scripts/merge_provider_pricing_fragment.py path/to/fragment.json --dry-run
```

Replace the path with your file. This tool replaces affected providers' plan/offer slices: supply a complete replacement, not a partial list. After changing production inputs, run `python scripts/build_docs_site.py` and inspect the model's offers. Research-only examples need no site rebuild.

## 2. Find the governing rules

Read official pricing, supported models and billing/limit pages. Record URLs and effective/access dates alongside: region/currency, model ID, fee/term, quota unit, reset/expiry, token debit, tools, promotions and exhaustion behavior. A fresh build does not refresh tariffs.

Convert to tokens only for a fixed raw-token quota or published model-specific credit formula. Dynamic points, requests and “up to” tasks do not establish a universal token rate; leave it null. Keep input/cache categories disjoint, count billed reasoning once, and compare the same model/region with PAYG. Never borrow another model's coefficients.

## 3. Worked example: official MiMo Personal Lite

Sources checked September 22, 2026: [Token Plan](https://mimo.mi.com/docs/zh-CN/price/token-plan) and [PAYG](https://mimo.mi.com/docs/zh-CN/price/pay-as-you-go). Recheck before quoting a later price.

Regular China monthly plan, **MiMo-V2.6-Pro**, daytime, without tools or promotions:

| Input | Value |
| --- | --- |
| Fee / monthly quota | CNY 39 / 4.1 billion Credits |
| Credits/token: new input / cache hit / output | 300 / 2.5 / 600 |
| PAYG CNY/million: same categories | 3 / 0.025 / 6 |
| Workload shares of all tokens | 20% / 70% / 10% |

```text
average debit = 0.2×300 + 0.7×2.5 + 0.1×600 = 121.75 Credits/token
capacity      = 4.1 billion / 121.75 = 33.675565 million tokens
full-use rate = 39 / 33.675565 = CNY 1.158110 per million
PAYG mix rate = 0.2×3 + 0.7×0.025 + 0.1×6 = CNY 1.217500 per million
break-even    = 1.158110 / 1.217500 = 95.12% of credits consumed
```

| Credit utilization, same mix | Realized CNY/million |
| --- | ---: |
| 100% | 1.158110 |
| 50% | 2.316220 |
| 25% | 4.632439 |

At **10 million tokens**, debit is 1.2175 billion Credits. Cash paid remains **CNY 39**, or **CNY 3.90/million**; PAYG costs **CNY 12.175 total**. The plan saves about 4.88% at full use but costs more at this volume.

For another credit plan:

```text
debit = Σ(tokens × coefficient)
full-use component rate/M = fee ÷ quota × coefficient × 1,000,000
realized rate/M = actual cash ÷ actual million tokens
```

Align fee and quota periods; reconcile capacity × full-use rate back to the fee.

MiMo off-peak calls (00:00–08:00 China time) use 0.8× Credits, increasing capacity without reducing the fee. First-purchase and annual discounts change the fee; calculate separately without double-discounting. Exhaustion stops service rather than automatically overflowing to PAYG. Keep USD and CNY tariffs separate.

Deliver cited inputs, reproducible arithmetic, actual-volume/PAYG comparisons and conditions. Further regional, annual and provider examples remain in the [worked audit](../../analysis/model-and-token-plan-audit-2026-09-22.md).
