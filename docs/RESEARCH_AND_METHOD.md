# Reward Eligibility Intelligence — Research and methodology

**Author:** Felipe Mattos · October 2026 · Independent portfolio study, not affiliated with Shakepay.

## Business question
How could a product team distinguish an eligible deposit, an excluded or misclassified activity, and a true discrepancy between expected reward status and the status shown to a customer?

## Documented public rule
[Shakepay reward statuses](https://help.shakepay.com/en/articles/13067281-what-are-the-shakepay-reward-statuses) describes Base, Bright and Blue. Qualifying activity may include deposits or exchange activity. This simplified research model uses CAD 200/2,000 for Bright/Blue direct deposit qualification and CAD 100/1,000 for exchange activity. A tier is held through the following month. Consult current documentation for up-to-date, complete eligibility terms.

## Important distinctions
Direct-deposit reward eligibility is not identical to the *payroll*-classification condition used by certain Bitcoin auto-buy products. Do not collapse product-specific policies into a universal rule.

## Qualitative signals — leads, not verification
Public customer discussions have raised concerns about deposit categorization and cutoff dates. They are selected accounts, not a systematic sample, and cannot establish defect rates or actual processing behavior.

## Data and scope
The accompanying `model.py` calculates expected status from qualifying synthetic event types using a deliberately simplified monthly aggregation and one-month carryover. The `analysis.py` script generates 300 fictitious accounts, 1,774 fictitious events, and injects 45 observed-status mismatches by construction. This is **not** a measurement of Shakepay performance.

Simplifications: settlement is represented as a boolean; no refunds, reversals, provisional entries, chargebacks, timezone changes, classification ambiguity, employer encoding behavior, individual account restrictions or undocumented rules. A 'mismatch' may reflect an incomplete simulation rather than a true system fault.

## Proposed operational validation
1. With Product/Operations, agree on versioned effective rules and included payment types.
2. Obtain approved de-identified event/status history; reconcile processing and eligibility effective timestamps.
3. Distinguish expected exclusions, ambiguous classifications, and genuine inconsistencies. Review exceptions with a human before any account change.
4. If a meaningful issue exists, test an approved explanation or internal case prioritization.
5. Primary metric: avoidable support contacts per 1,000 eligible reward events; secondary: comprehension, time to resolution, review precision.
6. Guardrails: financial loss, unfair eligibility denial, unnecessary spending, confusion, complaints and compliance.

## Business relevance
The proof-of-work demonstrates data modeling, Python, SQL, versioned rules and an operational experiment proposal, not consulting services or real production access. I am interested in working at Shakepay.
