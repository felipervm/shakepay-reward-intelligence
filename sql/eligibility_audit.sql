-- SQLite reference implementation, independent of Python's calculated tiers.
-- Input dates are agreed eligibility-effective calendar dates, settled is 0/1.
-- This fixture assumes confirmed classification, no reversals and personal accounts.
-- Thresholds are explicit from the public rule snapshot; update both implementations
-- if the rule version changes. Bind :as_of as YYYY-MM-DD.
WITH qualifying AS (
 SELECT account_id, substr(event_date,1,7) AS month,
        SUM(CASE WHEN kind IN ('payroll','pension','government_benefit') THEN amount_cents ELSE 0 END) AS direct_cents,
        SUM(CASE WHEN kind='exchange' THEN amount_cents ELSE 0 END) AS exchange_cents
 FROM events
 WHERE settled=1 AND amount_cents>0 AND event_date<=:as_of
   AND event_date>=date(:as_of,'start of month','-1 month')
 GROUP BY account_id, substr(event_date,1,7)
), earned AS (
 SELECT account_id, month,
        CASE WHEN direct_cents>=200000 OR exchange_cents>=100000 THEN 2
             WHEN direct_cents>=20000 OR exchange_cents>=10000 THEN 1 ELSE 0 END AS level
 FROM qualifying
), active AS (
 SELECT o.account_id, o.status AS observed_tier, COALESCE(MAX(e.level),0) AS level
 FROM observed o LEFT JOIN earned e ON e.account_id=o.account_id
 GROUP BY o.account_id, o.status
), expected AS (
 SELECT account_id, CASE level WHEN 2 THEN 'Blue' WHEN 1 THEN 'Bright' ELSE 'Base' END AS expected_tier,
        observed_tier FROM active
)
SELECT account_id, expected_tier, observed_tier,
       CASE WHEN expected_tier<>observed_tier THEN 1 ELSE 0 END AS mismatch
FROM expected ORDER BY account_id;
