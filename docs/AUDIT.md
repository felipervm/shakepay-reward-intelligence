# Final audit — October 8, 2026

## Result
31 Python tests and 15 JavaScript tests pass. A deterministic suite compares 1,500 generated scenarios across Python and JavaScript; 1,200 fully classified scenarios also agree with SQL. The original 300-account, 1,774-event fixture reproduces its 45 deliberately injected status differences. These are synthetic checks, not company defect or impact measurements.

## Corrections
- Missing effectiveness now triggers information review instead of an assumed exclusion.
- Python and JavaScript share monetary, calendar-date and boolean input validation, including invalid future events.
- Unresolved information has a confirmed floor and possible ceiling. A demonstrated status difference is no longer hidden by another uncertain input.
- Small uncertain amounts no longer imply they could raise a tier when thresholds are unreachable.
- Removed a customer anecdote whose full text could not be checked. Retained the verified discussion with both negative and positive experiences.
- Rebuilt method and analysis pages from source and executed notebook output; added deterministic artifact and local-link validation.

## Browser checks
Chrome at 1440, 390 and 320 pixels: all six scenarios, invalid amounts, adding/removing events, both reports, no page-level horizontal overflow and no JavaScript exceptions. Desktop screenshot inspected.

## Evidence and limits
Three official sources and one customer discussion are indexed in [sources.json](sources.json), with the claim each supports and what it cannot establish. Official policy supports the simplified rule model. Customer feedback motivates a hypothesis; it does not establish a technical cause, prevalence or commercial impact. No internal data, confirmed product defect, validated customer demand or measured improvement is claimed. Raw timestamp mapping, reversals, policy exceptions and production entitlement need internal validation.

## Reproduce
Run the commands in the repository README. GitHub Actions runs the model, test suites, document build and artifact consistency checks on pushes and pull requests.
