"""Run from repository root: python -m unittest discover -s tests -v"""
import unittest
from model import expected_tier,earned_tier,reconcile,RULES
def e(kind,amt,when="2026-10-04",settled=True):
    return {"kind":kind,"amount_cad":amt,"date":when,"settled":settled}
class Rewards(unittest.TestCase):
    def test_policy_thresholds_match_sql(self):
        from pathlib import Path
        sql=(Path(__file__).resolve().parent.parent/"sql/eligibility_audit.sql").read_text()
        for kind, column in [("eligible_direct_deposit","direct_cents"),("eligible_exchange","exchange_cents")]:
            for tier in ["Bright","Blue"]:
                value=RULES["thresholds_cad"][kind][tier]*100
                self.assertIn(f"{column}>={value}",sql)
    def test_direct_bright(self): self.assertEqual(expected_tier([e("payroll",200)],"2026-10-10"),"Bright")
    def test_direct_blue(self): self.assertEqual(expected_tier([e("payroll",2000)],"2026-10-10"),"Blue")
    def test_exchange_bright(self): self.assertEqual(expected_tier([e("exchange",100)],"2026-10-10"),"Bright")
    def test_exchange_blue(self): self.assertEqual(expected_tier([e("exchange",1000)],"2026-10-10"),"Blue")
    def test_under_threshold(self): self.assertEqual(expected_tier([e("exchange",99)],"2026-10-10"),"Base")
    def test_excluded(self): self.assertEqual(expected_tier([e("etransfer",3000)],"2026-10-10"),"Base")
    def test_previous_month(self): self.assertEqual(expected_tier([e("payroll",2000,"2026-09-27")],"2026-10-02"),"Blue")
    def test_expiry(self): self.assertEqual(expected_tier([e("payroll",2000,"2026-08-27")],"2026-10-02"),"Base")
    def test_not_settled(self): self.assertEqual(expected_tier([e("payroll",2000,settled=False)],"2026-10-10"),"Base")
    def test_reconcile(self): self.assertTrue(reconcile([e("payroll",2000)],"Bright","2026-10-10")["mismatch"])
    def test_aggregation(self): self.assertEqual(earned_tier([e("payroll",100),e("pension",100)],2026,10),"Bright")
    def test_future_event(self): self.assertEqual(expected_tier([e("payroll",2000,"2026-10-28")],"2026-10-08"),"Base")
    def test_before_and_on_qualification(self):
        events=[e("payroll",2000,"2026-10-08")]
        self.assertEqual(expected_tier(events,"2026-10-07"),"Base")
        self.assertEqual(expected_tier(events,"2026-10-08"),"Blue")
    def test_year_rollover(self): self.assertEqual(expected_tier([e("payroll",2000,"2025-12-31")],"2026-01-01"),"Blue")
    def test_categories_not_combined(self): self.assertEqual(expected_tier([e("payroll",150),e("exchange",50)],"2026-10-08"),"Base")
    def test_exact_cents(self): self.assertEqual(expected_tier([e("payroll","199.90"),e("pension","0.10")],"2026-10-08"),"Bright")
    def test_unknown_not_called_bug(self):
        result=reconcile([e("unknown",2000)],"Base","2026-10-08")
        self.assertEqual(result["assessment"],"INCOMPLETE_DATA")
        self.assertIsNone(result["mismatch"])
    def test_unrecognized_kind_requires_review(self):
        result=reconcile([e("new_payment_channel",2000)],"Base","2026-10-08")
        self.assertEqual(result["assessment"],"INCOMPLETE_DATA")
        self.assertIsNone(result["mismatch"])
    def test_confirmed_blue_floor_with_unknown(self):
        result=reconcile([e("payroll",2000),e("new_payment_channel",500)],"Blue","2026-10-08")
        self.assertEqual(result["confirmed_floor"],"Blue")
        self.assertFalse(result["potential_higher_tier"])
    def test_missing_settlement_not_assumed(self):
        event=e("payroll",2000);event.pop("settled")
        self.assertEqual(expected_tier([event],"2026-10-08"),"Base")
    def test_invalid_money(self):
        for amount in ["NaN","Infinity","-1","1.001"]:
            with self.assertRaises(ValueError): expected_tier([e("payroll",amount)],"2026-10-08")
if __name__=="__main__":unittest.main()
