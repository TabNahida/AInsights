"""Recompute the dated research examples; never change production pricing.

Run from any directory. Inputs are reviewed observations, not a live tariff feed.
Only Python's standard library is required.
"""

from __future__ import annotations

import argparse
import json
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 36
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "analysis" / "token-plan-examples-2026-09-22.json"
D = Decimal
MILLION = D(1_000_000)
TYPES = ("input", "cache", "output")


def positive(value):
    result = D(value)
    if not result.is_finite() or result <= 0:
        raise ValueError("Expected a finite positive amount")
    return result


def blend(values, weights):
    return sum(D(values[k]) * weights[k] for k in TYPES)


def credit_case(case, weights, credit_multiplier=D(1), price_multiplier=D(1)):
    price = positive(case["price"]) * positive(price_multiplier)
    quota = positive(case["includedCredits"])
    multiplier = positive(credit_multiplier)
    coefficients = {k: positive(case["creditsPerToken"][k]) * multiplier for k in TYPES}
    weighted_credits = blend(coefficients, weights)
    capacity_m = quota / weighted_credits / MILLION
    rates = {k: price / quota * coefficients[k] * MILLION for k in TYPES}
    full_rate = blend(rates, weights)
    payg_rate = blend(case["paygPerMillion"], weights)
    # Independent capacity reconciliation: a full package costs exactly its fee.
    if abs(capacity_m * full_rate - price) > D("1e-25"):
        raise ValueError("Quota/fee reconciliation failed")
    return {
        "id": case["id"], "currency": case["currency"], "period": case["period"],
        "fee": price, "fullUtilizationRatesPerMillion": rates,
        "weightedCreditsPerToken": weighted_credits,
        "capacityMillionMixedTokens": capacity_m,
        "fullUtilizationMixedRatePerMillion": full_rate,
        "paygMixedRatePerMillion": payg_rate,
        "breakEvenUtilization": full_rate / positive(payg_rate),
        "realizedRateByCreditUtilization": {
            str(u): full_rate / u for u in (D(1), D("0.5"), D("0.25"))
        },
    }


def calculate(data):
    weights = {k: positive(data["workload"]["weights"][k]) for k in TYPES}
    if sum(weights.values()) != 1:
        raise ValueError("Workload weights must sum to one")
    cases = [credit_case(c, weights) for c in data["creditCases"]]
    cn = next(c for c in data["creditCases"] if c["id"] == "mimo-pro-cn-monthly")
    promo = data["mimoPromotions"]
    night = credit_case(cn, weights, D(promo["offPeakCreditMultiplier"]))
    first = credit_case(cn, weights, price_multiplier=D(promo["firstPurchasePriceMultiplier"]))
    # All token amounts below are billable, mutually exclusive categories.
    volume = D(10_000_000)
    debit = volume * blend(cn["creditsPerToken"], weights)
    fixed_volume = {
        "totalTokens": volume, "creditsUsed": debit,
        "creditUtilization": debit / D(cn["includedCredits"]),
        "subscriptionCashPaid": D(cn["price"]),
        "realizedCostPerMillion": D(cn["price"]) / (volume / MILLION),
        "paygCashForSameWorkload": volume / MILLION * blend(cn["paygPerMillion"], weights),
    }
    t = data["tokenCase"]
    token_quota_m = positive(t["includedTokens"]) / MILLION
    token_rates = {
        "list": positive(t["price"]) / token_quota_m,
        "conditionalFirstPurchase": positive(t["conditionalFirstPurchasePrice"]) / token_quota_m,
        "conditionalFirstRenewal": positive(t["price"]) * D(t["conditionalFirstRenewalMultiplier"]) / token_quota_m,
    }
    p = data["approximatePointCase"]
    point_capacity_m = positive(p["includedPoints"]) / positive(p["approximateExamplePoints"]) * sum(D(x) for x in p["exampleTokens"].values()) / MILLION
    a = data["dynamicCreditCase"]
    windows = [{
        "fullyConsumedWindows": n,
        "consumedCredits": D(n) * D(a["creditsPerSevenDays"]),
        "currentCostPerConsumedCredit": D(a["currentPrice"]) / (D(n) * D(a["creditsPerSevenDays"])),
        "listCostPerConsumedCredit": D(a["listPrice"]) / (D(n) * D(a["creditsPerSevenDays"])),
    } for n in a["illustrativeFullyConsumedWindows"]]
    return {
        "asOf": data["asOf"], "scope": data["purpose"],
        "creditCases": cases,
        "mimoCnMonthlyAllOffPeak": night,
        "mimoCnMonthlyFirstPurchaseDaytime": first,
        "mimoCnMonthlyTenMillionTokenExample": fixed_volume,
        "baiduLiteTokenMode": {
            "fullUtilizationRatesPerMillion": token_rates,
            "listRateAt50PercentUtilization": token_rates["list"] / D("0.5"),
            "listRateAt25PercentUtilization": token_rates["list"] / D("0.25"),
            "promotionNote": t["promotionNote"],
        },
        "baiduPointModeConditionalIllustration": {
            "capacityMillionTokensIfEveryCallRepeatsExample": point_capacity_m,
            "approximateRatePerMillion": D(p["price"]) / point_capacity_m,
            "comparisonEligible": False, "note": p["note"],
        },
        "alibabaLite": {
            "conditionalWindowSchedules": windows,
            "legacy52WeekMonthlyEquivalentCredits": D(a["creditsPerSevenDays"]) * D(52) / D(12),
            "legacyAverageCurrentCostPerCredit": D(a["currentPrice"]) / (D(a["creditsPerSevenDays"]) * D(52) / D(12)),
            "additionalPackMarginalCostPerCredit": D(a["packPrice"]) / D(a["packCredits"]),
            "currentCashForLitePlusOnePack": D(a["currentPrice"]) + D(a["packPrice"]),
            "tokenRatePerMillion": None, "comparisonEligible": False,
        },
    }


def serialize(value):
    if isinstance(value, Decimal):
        return str(value.quantize(D("0.000000001")))
    raise TypeError(type(value).__name__)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, help="Optional JSON file; otherwise prints to stdout")
    args = parser.parse_args()
    result = calculate(json.loads(args.input.read_text(encoding="utf-8")))
    rendered = json.dumps(result, ensure_ascii=False, indent=2, default=serialize) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
