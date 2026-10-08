"""Independent Shakepay reward eligibility model; synthetic data only.

Version 1 models positive settled events, monthly thresholds, and one-month
carryover. It does not implement reversals, fraud rules, regulatory exceptions,
payment-rail finality, or any Shakepay private business logic.
"""
from collections import defaultdict
from datetime import date
import json
from pathlib import Path

RULES = json.loads((Path(__file__).parent/"rules"/"reward_status_v1.json").read_text())
TIERS = ["Base","Bright","Blue"]
DIRECT = set(RULES["eligible_direct_deposit_kinds"])
EXCHANGE = "exchange"

def month_of(value):
    if isinstance(value,date): return (value.year,value.month)
    return tuple(map(int,str(value)[:7].split("-")))

def preceding_month(year,month):
    return (year-1,12) if month==1 else (year,month-1)

def classify_event(event):
    """Only positive, settled events. Excluded transactions contribute zero."""
    kind=event["kind"]
    amount=float(event["amount_cad"])
    if amount<=0 or not event.get("settled",True): return None,0.
    if kind in DIRECT: return "eligible_direct_deposit", amount
    if kind==EXCHANGE: return "eligible_exchange", amount
    return None,0.

def earned_tier(events,year,month):
    totals=defaultdict(float)
    for event in events:
        if month_of(event["date"])!=(year,month): continue
        category,amount=classify_event(event)
        if category: totals[category]+=amount
    level=0
    for category,amount in totals.items():
        thresholds=RULES["thresholds_cad"][category]
        if amount>=thresholds["Blue"]: level=max(level,2)
        elif amount>=thresholds["Bright"]: level=max(level,1)
    return TIERS[level]

def expected_tier(events,as_of):
    year,month=month_of(as_of)
    prev=preceding_month(year,month)
    return max((earned_tier(events,year,month),earned_tier(events,*prev)),key=TIERS.index)

def reconcile(events,observed_tier,as_of):
    expected=expected_tier(events,as_of)
    if observed_tier not in TIERS: raise ValueError("Unsupported observed tier")
    return {"expected_tier":expected,"observed_tier":observed_tier,
            "mismatch":expected!=observed_tier,
            "action":"Investigate classification, settlement and effective rule version" if expected!=observed_tier else "No discrepancy in simplified model"}

if __name__=="__main__":
    demo=[{"date":"2026-10-01","kind":"payroll","amount_cad":2000,"settled":True}]
    print(json.dumps(reconcile(demo,"Bright","2026-10-08"),indent=2))
