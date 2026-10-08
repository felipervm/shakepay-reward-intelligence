"""Independent, simplified personal-account model of published Shakepay rules.
Dates are supplied eligibility-effective calendar dates, not raw bank timestamps.
Unknown classifications and unsupported reversals require review; this model
cannot establish production entitlement or why an employer coded a payment.
"""
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path

RULES = json.loads((Path(__file__).parent / "rules/reward_status_v1.json").read_text())
TIERS = ["Base", "Bright", "Blue"]
DIRECT = set(RULES["eligible_direct_deposit_kinds"])

def calendar_date(value):
    if isinstance(value, datetime):
        raise ValueError("Supply an agreed eligibility-effective calendar date, not a timestamp")
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))

def month_of(value):
    d = calendar_date(value)
    return d.year, d.month

def preceding_month(year, month):
    return (year - 1, 12) if month == 1 else (year, month - 1)

def cents(value):
    try:
        amount = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("Amount must be a finite CAD number") from exc
    if not amount.is_finite() or amount < 0 or amount != amount.quantize(Decimal("0.01")):
        raise ValueError("Amount must be nonnegative CAD with at most two decimal places")
    return int(amount * 100)

def classify_event(event):
    amount = cents(event["amount_cad"])
    if event.get("settled") is not True or not event.get("classification_confirmed", True):
        return None, 0
    kind = event["kind"]
    if kind in DIRECT:
        return "eligible_direct_deposit", amount
    if kind == "exchange":
        return "eligible_exchange", amount
    return None, 0

def earned_tier(events, year, month, as_of=None):
    cutoff = calendar_date(as_of) if as_of is not None else None
    totals = defaultdict(int)
    for event in events:
        event_date = calendar_date(event["date"])
        if (event_date.year, event_date.month) != (year, month) or (cutoff and event_date > cutoff):
            continue
        category, amount = classify_event(event)
        if category:
            totals[category] += amount
    level = 0
    for category, amount in totals.items():
        thresholds = RULES["thresholds_cad"][category]
        if amount >= cents(thresholds["Blue"]):
            level = max(level, 2)
        elif amount >= cents(thresholds["Bright"]):
            level = max(level, 1)
    return TIERS[level]

def expected_tier(events, as_of):
    cutoff = calendar_date(as_of)
    year, month = cutoff.year, cutoff.month
    previous = preceding_month(year, month)
    return max((earned_tier(events, year, month, cutoff),
                earned_tier(events, *previous, as_of=cutoff)), key=TIERS.index)

def reconcile(events, observed_tier, as_of):
    if observed_tier not in TIERS:
        raise ValueError("Unsupported observed tier")
    cutoff = calendar_date(as_of)
    window = {month_of(cutoff), preceding_month(cutoff.year, cutoff.month)}
    details = []
    uncertain = False
    for event in events:
        d = calendar_date(event["date"])
        amount = cents(event["amount_cad"])
        reason = "ELIGIBLE"
        category = None
        contribution = 0
        if d > cutoff:
            reason = "AFTER_CUTOFF"
        elif month_of(d) not in window:
            reason = "OUTSIDE_CARRYOVER"
        elif event.get("settled") is not True:
            reason = "NOT_EFFECTIVE_IN_FIXTURE"
        elif not event.get("classification_confirmed", True) or event["kind"] == "unknown":
            reason = "CLASSIFICATION_REVIEW"
            uncertain = True
        else:
            category, contribution = classify_event(event)
            if not category:
                reason = "EXCLUDED_ACTIVITY"
        details.append({"date": d.isoformat(), "kind": event["kind"],
                        "amount_cents": amount, "contribution_cents": contribution,
                        "category": category, "reason": reason})
    expected = expected_tier(events, cutoff)
    mismatch = None if uncertain else expected != observed_tier
    action = ("Confirm classification before comparing status" if uncertain else
              "Review effective dates, rule version and observed status" if mismatch else
              "Explain eligible contributions and carryover; no difference in this fixture")
    return {"as_of": cutoff.isoformat(), "rule_version": RULES["version"],
            "expected_tier": expected, "observed_tier": observed_tier,
            "assessment": "INCOMPLETE_DATA" if uncertain else "STATUS_REVIEW" if mismatch else "MATCH",
            "mismatch": mismatch, "action": action, "events": details}

if __name__ == "__main__":
    demo = [{"date": "2026-10-01", "kind": "payroll", "amount_cad": "2000.00", "settled": True}]
    print(json.dumps(reconcile(demo, "Bright", "2026-10-08"), indent=2))
