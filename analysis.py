"""Generate fully synthetic accounts and reconcile expected/observed tiers.
Run: python analysis.py
"""
import csv,random,json
from pathlib import Path
from model import expected_tier,TIERS
rng=random.Random(42)
ROOT=Path(__file__).parent
DATA=ROOT/"data"
DATA.mkdir(exist_ok=True)
events=[]
results=[]
types=["payroll","pension","government_benefit","exchange","etransfer","internal_transfer"]
for n in range(1,301):
    case=f"S-{n:04d}"
    user_events=[]
    count=6 if n<=274 else 5 # 274*6+26*5 = 1774
    for j in range(count):
        item={"account_id":case,"event_id":f"E-{n:04d}-{j+1}","date":f"2026-{rng.choice([8,9,10]):02d}-{rng.randrange(1,29):02d}",
            "kind":rng.choice(types),"amount_cad":rng.choice([25,50,100,150,200,450,800,1000,1500,2000]),"settled":True}
        events.append(item);user_events.append(item)
    tier=expected_tier(user_events,"2026-10-08")
    changed=n<=45
    observed=TIERS[(TIERS.index(tier)+1)%3] if changed else tier
    results.append({"account_id":case,"expected_tier":tier,"observed_tier":observed,"mismatch":int(changed)})
for path,rows in [(DATA/"synthetic_events.csv",events),(DATA/"synthetic_reconciliation.csv",results)]:
    with path.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
summary={"accounts":len(results),"events":len(events),"injected_mismatches":sum(r["mismatch"] for r in results),"expected_tier_counts":{t:sum(r["expected_tier"]==t for r in results) for t in TIERS},"synthetic":True}
(DATA/"demo_summary.json").write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
