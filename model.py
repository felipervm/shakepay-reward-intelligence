"""Independent, simplified personal-account model of published Shakepay rules.
Dates are supplied eligibility-effective calendar dates, not raw bank timestamps.
Unknown classifications and unsupported reversals require review; this model
cannot establish production entitlement or why an employer coded a payment.
"""
from collections import defaultdict
from datetime import date, datetime
import re
import json
from pathlib import Path

RULES = json.loads((Path(__file__).parent / "rules/reward_status_v1.json").read_text())
TIERS = ["Base", "Bright", "Blue"]
DIRECT = set(RULES["eligible_direct_deposit_kinds"])
EXCLUDED = set(RULES["excluded_kinds"])
KNOWN = DIRECT | EXCLUDED | {"exchange"}

def calendar_date(value):
    if isinstance(value, datetime):
        raise ValueError("Supply an agreed eligibility-effective calendar date, not a timestamp")
    if isinstance(value, date):
        return value
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("Supply a YYYY-MM-DD calendar date")
    return date.fromisoformat(value)

def month_of(value):
    d = calendar_date(value)
    return d.year, d.month

def preceding_month(year, month):
    return (year - 1, 12) if month == 1 else (year, month - 1)

def cents(value):
    text = str(value).strip()
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]{1,2})?", text):
        raise ValueError("Enter a nonnegative CAD amount with at most two decimal places")
    whole, _, fraction = text.partition(".")
    if len(whole.lstrip("0")) > 7:
        raise ValueError("Use an amount from CAD 0 to 1,000,000 for this demo")
    amount = int(whole) * 100 + int(fraction.ljust(2, "0"))
    if amount > 100000000:
        raise ValueError("Use an amount from CAD 0 to 1,000,000 for this demo")
    return amount

def validate_event(event):
    if not isinstance(event, dict) or not all(k in event for k in ("date", "kind", "amount_cad")):
        raise ValueError("Every event requires date, kind and amount_cad")
    calendar_date(event["date"])
    cents(event["amount_cad"])
    if not isinstance(event["kind"], str):
        raise ValueError("Activity must be a string")
    for field in ("settled", "classification_confirmed"):
        if event.get(field) is not None and type(event[field]) is not bool:
            raise ValueError(f"{field} must be boolean or null; normalize CSV values before analysis")


def classify_event(event):
    amount = cents(event["amount_cad"])
    if event.get("settled") is not True or event.get("classification_confirmed", True) is not True:
        return None, 0
    kind = event["kind"]
    if kind not in KNOWN:
        return None, 0
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
    events = list(events)
    for event in events:
        validate_event(event)
    cutoff = calendar_date(as_of)
    year, month = cutoff.year, cutoff.month
    previous = preceding_month(year, month)
    return max((earned_tier(events, year, month, cutoff),
                earned_tier(events, *previous, as_of=cutoff)), key=TIERS.index)

def reconcile(events, observed_tier, as_of):
    if observed_tier not in TIERS:
        raise ValueError("Unsupported observed tier")
    events = list(events)
    for event in events:
        validate_event(event)
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
        elif event.get("settled") is None:
            reason = "EFFECTIVENESS_REVIEW"
            uncertain = True
        elif event.get("settled") is not True:
            reason = "NOT_EFFECTIVE_IN_FIXTURE"
        elif event.get("classification_confirmed", True) is not True or event["kind"] not in KNOWN:
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
    # Bound the tier by treating unresolved inputs as eligible, separately for
    # each qualification path. This is an upper bound, not a policy decision.
    upper = expected
    if uncertain:
        for possible_kind in ("payroll", "exchange"):
            optimistic = []
            for event in events:
                candidate = dict(event)
                if candidate.get("settled") is None:
                    candidate["settled"] = True
                if candidate.get("classification_confirmed", True) is not True or candidate["kind"] not in KNOWN:
                    candidate.update(kind=possible_kind, classification_confirmed=True)
                optimistic.append(candidate)
            upper = max(upper, expected_tier(optimistic, cutoff), key=TIERS.index)
    definite_difference = not TIERS.index(expected) <= TIERS.index(observed_tier) <= TIERS.index(upper)
    mismatch = True if definite_difference else None if uncertain and upper != expected else False
    assessment = "STATUS_REVIEW" if definite_difference else "INCOMPLETE_DATA" if uncertain else "MATCH"
    action = ("Review observed status against the confirmed tier bounds" if definite_difference else
              "Confirm missing effectiveness or classification before closing review" if uncertain else
              "Explain eligible contributions and carryover; no difference in this fixture")
    return {"as_of": cutoff.isoformat(), "rule_version": RULES["version"],
            "expected_tier": expected, "observed_tier": observed_tier,
            "assessment": assessment,
            "mismatch": mismatch, "confirmed_floor": expected, "possible_ceiling": upper,
            "has_unresolved_events": uncertain, "potential_higher_tier": TIERS.index(upper) > TIERS.index(expected), "action": action, "events": details}

if __name__ == "__main__":
    demo = [{"date": "2026-10-01", "kind": "payroll", "amount_cad": "2000.00", "settled": True}]
    print(json.dumps(reconcile(demo, "Bright", "2026-10-08"), indent=2))
