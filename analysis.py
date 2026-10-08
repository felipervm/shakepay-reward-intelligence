"""Deterministic synthetic fixture; no measured Shakepay outcomes.
Python computes expected status; SQLite independently recomputes it from events.
Observed statuses are deliberately perturbed to exercise a review workflow.
"""
import csv, json, random, sqlite3
from pathlib import Path
from model import expected_tier, TIERS, cents
rng = random.Random(42)
ROOT = Path(__file__).parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
AS_OF = "2026-10-08"
events, results = [], []
types = ["payroll", "pension", "government_benefit", "exchange", "etransfer", "internal_transfer"]
changed_ids = set(rng.sample(range(1, 301), 45))
for n in range(1, 301):
    account = f"S-{n:04d}"
    account_events = []
    for j in range(6 if n <= 274 else 5):
        month = rng.choice([8, 9, 10])
        day = rng.randrange(1, 9 if month == 10 else 29)
        amount = rng.choice([25, 50, 100, 150, 200, 450, 800, 1000, 1500, 2000])
        event = {"account_id": account, "event_id": f"E-{n:04d}-{j+1}",
                 "date": f"2026-{month:02d}-{day:02d}", "kind": rng.choice(types),
                 "amount_cad": amount, "amount_cents": cents(amount), "settled": 1}
        events.append(event)
        account_events.append(dict(event, settled=True))
    tier = expected_tier(account_events, AS_OF)
    observed = TIERS[(TIERS.index(tier) + 1) % 3] if n in changed_ids else tier
    results.append({"account_id": account, "as_of": AS_OF, "expected_tier": tier,
                    "observed_tier": observed, "mismatch": int(tier != observed)})
for name, rows in [("synthetic_events.csv", events), ("synthetic_reconciliation.csv", results)]:
    with (DATA/name).open("w", newline="", encoding="utf8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE events(account_id TEXT, event_id TEXT, event_date TEXT, kind TEXT, amount_cents INTEGER, settled INTEGER)")
conn.execute("CREATE TABLE observed(account_id TEXT PRIMARY KEY, status TEXT)")
conn.executemany("INSERT INTO events VALUES (?,?,?,?,?,?)", [(e['account_id'],e['event_id'],e['date'],e['kind'],e['amount_cents'],e['settled']) for e in events])
conn.executemany("INSERT INTO observed VALUES (?,?)", [(r['account_id'],r['observed_tier']) for r in results])
sql_results = conn.execute((ROOT/'sql/eligibility_audit.sql').read_text(), {"as_of": AS_OF}).fetchall()
python_status = {r['account_id']:r['expected_tier'] for r in results}
assert len(sql_results) == len(results)
assert all(python_status[account] == tier for account,tier,observed,mismatch in sql_results)
assert all(e['date'] <= AS_OF for e in events)
summary = {"synthetic": True, "as_of": AS_OF, "accounts": len(results), "events": len(events),
           "injected_status_differences": sum(r['mismatch'] for r in results),
           "python_sql_agreement": len(sql_results), "future_events": 0,
           "interpretation": "Fixture validation, not error rate or business impact"}
(DATA/'demo_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
print(json.dumps(summary,indent=2))
