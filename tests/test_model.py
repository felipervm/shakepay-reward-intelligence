"""Run from repository root: python -m unittest discover -s tests -v"""
import unittest
from model import expected_tier,earned_tier,reconcile
def e(kind,amt,when="2026-10-04",settled=True):
    return {"kind":kind,"amount_cad":amt,"date":when,"settled":settled}
class Rewards(unittest.TestCase):
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
if __name__=="__main__":unittest.main()
