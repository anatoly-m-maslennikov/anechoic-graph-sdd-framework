---
atom_family: SPEC
atom_id: AN-S-1908
container:
  component: C15
tier: 4
context:
  lens: SWD
state:
  status: draft
  version: 17
  updated_at: '2026-11-14T08:28:49.256806+00:00'
---
## Summary
Select software Evaluation techniques by failure mode

## Claim
### Prose Claim
Use the applicable Spec, declared failure predicates, and active Evaluation authority to select one admitted behavioral Evaluation portfolio for a PROGRAMMATIC component.
Use CA-E-637 for the observable evidence rule and CA-E-389 for portfolio acceptance.

## Details
### Candidates
Before coding or choosing checks, bind each predicate to observable behavior, including transitions, side effects, and failure boundaries.
Identify applicable Evaluation Atoms across scope, purpose, boundary realism, environment, and release stage without a universal ranking.
Build candidate portfolios covering every predicate. Include a specialized technique only when its applicability and evidence preconditions hold.
### Admission
Apply both policies and each selected Evaluation Atom's acceptance and disposition rules to every candidate. Apply CA-E-536 when using canary evidence.
Repeat until one traceable portfolio is admitted with every predicate covered or no candidate remains. Return selected Evaluation identities and selection rationale.
If none passes, return uncovered predicates, failed conditions, and missing evidence for authority or design clarification.
### Observable results
Assert user-visible results for public behavior. Use observable domain state and effects for internal behavior.
Remove unit tests that mirror implementation or add no distinct evidence. Keep focused checks for gaps in end-to-end coverage.
Prefer real browser, MCP, or HTTP end-to-end checks for critical journeys or integration and emergent failures that narrower checks miss.
