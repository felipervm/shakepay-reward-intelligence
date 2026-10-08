import unittest, json, random, subprocess, sqlite3, csv
from pathlib import Path
from datetime import date, timedelta
from model import expected_tier, reconcile, cents
ROOT=Path(__file__).resolve().parent.parent

def event(kind="payroll",amount="2000",when="2026-10-01",**extra):
    return dict(date=when,kind=kind,amount_cad=amount,settled=True,**extra)

class AuditEdges(unittest.TestCase):
    def test_missing_effectiveness_is_uncertain(self):
        e=event();e.pop("settled")
        self.assertEqual(reconcile([e],"Base","2026-10-08")["assessment"],"INCOMPLETE_DATA")
    def test_tiny_unknown_cannot_raise_tier(self):
        result=reconcile([event("unknown","1")],"Base","2026-10-08")
        self.assertFalse(result["potential_higher_tier"])
    def test_known_floor_difference_survives_unknown(self):
        result=reconcile([event(),event("unknown","1")],"Base","2026-10-08")
        self.assertTrue(result["mismatch"])
        self.assertEqual(result["assessment"],"STATUS_REVIEW")
    def test_unknown_can_complete_direct_path(self):
        result=reconcile([event(amount="1999"),event("unknown","1")],"Bright","2026-10-08")
        self.assertEqual(result["possible_ceiling"],"Blue")
    def test_invalid_future_event_rejected(self):
        with self.assertRaises(ValueError): expected_tier([event(amount="-1",when="2026-10-28")],"2026-10-08")
    def test_input_contract(self):
        for amount in ["2e3","1000000.01",True,None,"0.001","Infinity"]:
            with self.subTest(amount=amount),self.assertRaises(ValueError): cents(amount)
        for flag in [1,"true","false",0]:
            e=event();e["settled"]=flag
            with self.subTest(flag=flag),self.assertRaises(ValueError): reconcile([e],"Base","2026-10-08")
        for when in ["20261008","2026-02-30","0000-01-01"]:
            with self.subTest(date=when),self.assertRaises(ValueError): expected_tier([],when)
    def test_scenario_answers(self):
        for c in json.loads((ROOT/'data/cases.json').read_text()):
            result=reconcile(c['events'],c['observed'],c['as_of'])
            self.assertEqual((result['expected_tier'],result['assessment']),(c['expected'],c['assessment']))
    def test_data_integrity(self):
        events=list(csv.DictReader((ROOT/'data/synthetic_events.csv').read_text(encoding='utf8').splitlines()))
        accounts=list(csv.DictReader((ROOT/'data/synthetic_reconciliation.csv').read_text(encoding='utf8').splitlines()))
        self.assertEqual(len(events),1774);self.assertEqual(len(accounts),300)
        self.assertEqual(len({e['event_id'] for e in events}),1774)
        self.assertEqual(len({a['account_id'] for a in accounts}),300)
        self.assertTrue({e['account_id'] for e in events}<={a['account_id'] for a in accounts})
        self.assertTrue(all(e['date']<='2026-10-08' and cents(e['amount_cad'])==int(e['amount_cents']) for e in events))
        self.assertEqual(sum(int(a['mismatch']) for a in accounts),45)

class CrossImplementation(unittest.TestCase):
    def test_1500_seeded_cases(self):
        rng=random.Random(260108)
        cases=[]
        amounts=['0','0.01','99.99','100','199.99','200','999.99','1000','1999.99','2000']
        kinds=['payroll','pension','government_benefit','exchange','etransfer','internal_transfer','crypto_deposit']
        for i in range(1500):
            cutoff=date.fromisoformat(rng.choice(['2026-01-01','2024-02-29','2026-10-08','2026-12-31']))
            events=[]
            for j in range(rng.randrange(0,9)):
                e=event(rng.choice(kinds),rng.choice(amounts),(cutoff+timedelta(days=rng.randrange(-70,30))).isoformat())
                e['settled']=rng.choice([True,True,False])
                if i>=1200:
                    if rng.random()<.3:e['kind']='unrecognized'
                    if rng.random()<.2:e['classification_confirmed']=None
                    if rng.random()<.2:e['settled']=None
                events.append(e)
            cases.append(dict(events=events,observed=rng.choice(['Base','Bright','Blue']),as_of=cutoff.isoformat()))
        javascript=json.loads(subprocess.run(['node',str(ROOT/'scripts/evaluate-json.mjs')],input=json.dumps(cases),text=True,capture_output=True,check=True).stdout)
        fields=['expected_tier','assessment','mismatch','confirmed_floor','possible_ceiling','potential_higher_tier']
        sql=(ROOT/'sql/eligibility_audit.sql').read_text()
        conn=sqlite3.connect(':memory:')
        conn.execute('CREATE TABLE events(account_id TEXT,event_id TEXT,event_date TEXT,kind TEXT,amount_cents INTEGER,settled INTEGER)')
        conn.execute('CREATE TABLE observed(account_id TEXT,status TEXT)')
        for i,(c,js) in enumerate(zip(cases,javascript)):
            py=reconcile(c['events'],c['observed'],c['as_of'])
            self.assertEqual({k:py[k] for k in fields},{k:js[k] for k in fields},f'Python/JS case {i}')
            self.assertEqual(expected_tier(list(reversed(c['events'])),c['as_of']),py['expected_tier'])
            if i<1200:
                conn.execute('DELETE FROM events');conn.execute('DELETE FROM observed')
                conn.execute('INSERT INTO observed VALUES (?,?)',('test',c['observed']))
                conn.executemany('INSERT INTO events VALUES (?,?,?,?,?,?)',[('test',str(j),e['date'],e['kind'],cents(e['amount_cad']),int(e['settled'])) for j,e in enumerate(c['events'])])
                row=conn.execute(sql,{'as_of':c['as_of']}).fetchone()
                self.assertEqual(row[1],py['expected_tier'],f'SQL case {i}')
                self.assertEqual(bool(row[3]),py['mismatch'])
        conn.close()
