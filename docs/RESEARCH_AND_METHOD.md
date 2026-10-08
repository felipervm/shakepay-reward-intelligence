# What counts toward Blue? — Research and method

Felipe Mattos · October 8, 2026 · Independent study of personal-account reward status.

## Question and working hypothesis

How can a team explain whether a received transaction contributes to reward status, and distinguish an expected exclusion from incomplete information or a status difference worth reviewing?

The hypothesis is that a transaction-level explanation might reduce some eligibility-related confusion. Shakepay already offers status and progress in Shaker Profile. This project does not establish a gap in that feature or a defect in Shakepay's systems.

## Public evidence

The reward-status guide and Benefits and Rewards Terms describe two independent monthly qualification paths. Direct deposits reach Bright at CAD 200 and Blue at CAD 2,000; exchange activity reaches Bright at CAD 100 and Blue at CAD 1,000. Qualification activates immediately and carries through the next calendar month.

Payroll, pensions and supported government benefits can qualify for status. The auto-buy guidance separately requires payroll-coded deposits. A classification can therefore matter differently across products; this does not mean every received bank payment qualifies.

A May 12 customer discussion reports a paycheque received without Blue, attributed by its author to employer coding. A later thread asks about a deposit delayed across the September/October boundary. Both motivate investigation; neither verifies cause, resolution, prevalence or entitlement. The latter was located through search indexing; its full thread was not independently verified in this research.

## Model scope

A single public-rule snapshot, research-demo-v2, checked October 8, 2026. The JSON labels the snapshot; it does not select historical policy versions automatically.

Inputs use agreed eligibility-effective calendar dates. Conversion from raw processing timestamps, timezone determination, reversals, provisional entries, linked accounts, business accounts, special restrictions and private policy are outside scope. An event's settled flag represents effectiveness for this fixture, not a reconstruction of settlement history. Amounts use integer cents; negative amounts and fractions beyond a cent are rejected.

Python excludes events after the audit date. It sums confirmed eligible deposit and exchange categories separately, then takes the higher tier earned in the current and prior calendar months. Unconfirmed or unrecognized classification receives an incomplete-data assessment rather than an asserted mismatch. A confirmed minimum tier is retained; an unresolved category may increase that tier unless Blue is already confirmed. A known difference requests review; it does not identify its cause.

SQLite independently derives status from the event table at the same cutoff. Its fixture assumes confirmed classifications and no reversals. It applies separate sums, threshold comparisons and prior-month carryover, then joins simulated observed status. It does not import Python's computed tier. Agreement checks shared rule interpretation and implementation; it cannot validate private Shakepay policy.

## Authored scenario results

Six examples have expected answers specified in the scenario file before comparison with the implementations. They demonstrate aggregation, exclusion, carryover, future-event filtering, unresolved classification and a known-input status difference. These are test scenarios, not observed customer cases.

**Two deposits, one monthly total** — Both effective deposits count in October. Together they reach CAD 2,000. Expected: Blue; assessment: MATCH. Next step: Explain the two contributions; no status difference in this scenario.

**Money arrived, but by e-Transfer** — The transfer is excluded from this status rule, regardless of amount. Expected: Base; assessment: MATCH. Next step: Explain the excluded payment type, without suggesting extra trading.

**September qualification carries into October** — A qualifying September deposit carries Blue through October. Expected: Blue; assessment: MATCH. Next step: Show the qualification month and carryover end date.

**A deposit after the cutoff does not count yet** — The October 28 event is after this October 8 snapshot. Its contribution is zero here. Expected: Base; assessment: MATCH. Next step: Compare status at the right effective date, not the full month.

**Classification is unresolved** — The payment type is unconfirmed. A status difference cannot be established from this input. Expected: Base; assessment: INCOMPLETE_DATA. Next step: Confirm the payment classification before deciding whether status needs review.

**Confirmed inputs, different observed status** — Known eligible inputs indicate Blue, while the simulated observed status is Bright. Expected: Blue; assessment: STATUS_REVIEW. Next step: Review effective timestamps, current policy and status history. This is not a confirmed bug.

## Larger fixture and reproducibility

The deterministic generator creates 300 fictitious accounts and 1,774 events through October 8. It deliberately changes 45 observed statuses to exercise review comparison. These counts are design choices, not detected problems or prevalence estimates. All 300 expected tiers agree between Python and SQL. The generated fixture contains no events after its cutoff.

Python tests cover thresholds, aggregation, separate qualification paths, invalid money, missing effectiveness, future events, before/on qualification, year rollover, expiry and uncertain classifications. Browser model tests compare all six authored examples and additional edge cases. The fixture and executed notebook are available in the repository.

Run `python analysis.py`, `python -m unittest discover -s tests -v` and `npm test`. The analytical scripts use Python's standard library. Jupyter is optional for opening the notebook; an HTML analysis is provided for reading without installation.

## A narrow operational test

First agree on classifications, effective timestamps, approved policy versions and permitted de-identified event/status history. Compare eligible contributions with observed status and categorize exclusions, insufficient data and review cases. Check whether a meaningful explanatory gap remains in the current experience.

If supported, test one transaction explanation against the existing experience. Before starting, define which support contacts are eligibility-related, the observation window, the assignment unit and repeat-contact handling. Measure those contacts per 1,000 relevant events, comprehension and resolution time. Review incorrect benefit denial, complaint levels, fairness and incentives to spend or trade. Do not call a fall in contacts a success if customers simply stop seeking help.

No revenue uplift, error rate or support reduction is estimated. A test might find improvement, no effect, or that the existing workflow is sufficient.

## Sources

[Reward-status guide](https://help.shakepay.com/en/articles/13067281-what-are-the-shakepay-reward-statuses) — updated August 31, 2026; reviewed October 8.

[Benefits and Rewards Terms](https://legal.shakepay.com/master/rewards) — updated September 10, 2026; reviewed October 8.

[Payroll auto-buy and spread guidance](https://help.shakepay.com/en/articles/14040432-0-spread-on-bitcoin-recurring-buys-and-payroll-auto-buys) — March 11, 2026; reviewed October 8.

[Customer classification discussion](https://www.reddit.com/r/shakepay/comments/1tbcd2k/considering_using_direct_deposit_anyone_have/) — May 12, 2026; anecdotal signal.

[Customer month-boundary discussion](https://www.reddit.com/r/shakepay/comments/1wv4gwx/bank_holiday_on_sept_30_delayed_dd_was_short_8_to/) — indexed anecdotal signal; cause and resolution unverified.


## Implementation guardrails

The Python source uses the JSON rule snapshot. The SQL and browser versions deliberately encode the same research snapshot separately, so every policy update requires synchronized changes and cross-implementation regression checks. This project does not claim full browser accessibility validation or production equivalence.
