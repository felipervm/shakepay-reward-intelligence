# What counts toward Blue?

An independent Shakepay product and data study by Felipe Mattos.

**Question:** How can a team explain a transaction's contribution to reward status and separate expected exclusions, incomplete information and a status difference to review?

[Read the study](https://felipervm.github.io/shakepay-reward-intelligence/) · [Sources and method](https://felipervm.github.io/shakepay-reward-intelligence/docs/method.html) · [Executed analysis](https://felipervm.github.io/shakepay-reward-intelligence/docs/analysis.html)

The study uses public guidance and clearly labeled synthetic scenarios. It does not diagnose Shakepay production systems or estimate business impact. I made it because I am interested in working at Shakepay.

## What's included

- Six authored scenarios with independently specified answers and per-event review reasons.
- Python model with exact cents, audit-date filtering, monthly qualification and carryover.
- SQLite computation from events, independent of Python's calculated tiers.
- Executed notebook and HTML report, deterministic fixture, Python and JavaScript tests.
- Responsive static site with an editable multi-event demo and linked public sources.

## Reproduce

Python 3.10+ and Node.js 18+ are sufficient. No installed packages are needed for the scripts or tests.

```bash
python analysis.py
python -m unittest discover -s tests -v
npm test
python scripts/build_docs.py
python scripts/verify_artifacts.py
```

Open the published study: https://felipervm.github.io/shakepay-reward-intelligence/

Jupyter is optional; see requirements.txt. The notebook assumes its working directory is notebooks/.

## Scope

A single public-rule snapshot checked October 8, 2026, for personal accounts. Dates are agreed eligibility-effective calendar dates, not raw processing timestamps. Classification truth, reversals, settlement history, account restrictions and automatic historical policy selection are outside scope. Unknown or unrecognized classification gets an incomplete-data assessment. The model reports a confirmed minimum tier and whether unresolved classification might raise that tier. A known status difference requests review, not an automatic account correction.

The larger fixture has 300 accounts and 1,774 events. Its 45 deliberately altered statuses are design inputs, not detected issues. Python and SQL recompute the same expected tiers independently. These artifacts demonstrate the proposed reasoning and implementation, not access to Shakepay data.


## Validation boundaries

The SQL reference is an independent fixture check, not a general-purpose input validator. It assumes confirmed classifications and a synchronized policy snapshot. Python and browser models share regression examples, but thresholds are repeated in SQL and JavaScript; changes to rules must update all three and be checked by tests. The website requires browser testing for layout, accessibility and interactions.

The final audit adds 1,500 Python/JavaScript comparison cases; 1,200 confirmed-input cases also run through SQL. The bounded demo uses CAD 0–1,000,000 per event and explicit boolean/null flags. Missing effectiveness is unknown, not automatically an exclusion. See the method report for tier bounds and source limitations.
