---
identity:
  atom_id: CA-M-424
  ref_id: CA-M-424@17-draft
context:
  container:
    scope_unit: CA-SU-15
  role: Method
  form: Direct Policy
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality
      <+ Verification <+ Test Design
    dependencies:
    - MODEL//ANECHOIC <+ Actor
  tier: 4
relations:
  IS_REPLACEMENT_FOR:
  - CA-M-424
  DERIVED_FROM:
  - CA-A-053
  child_of:
  - CA-M-415
state:
  status: draft
  version: 17
  updated_at: '2026-11-14T08:28:49.256806+00:00'
destination:
  file:
    name: CA-M-424@17-draft-PROGRAMMATIC-DIRECT_POLICY--select-software-evaluation-techniques-by-failure-mode.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/05_method/000_draft
current_scope_unit: PROGRAMMATIC
claim_target_scope_unit: PROGRAMMATIC
author: Anatoly Maslennikov
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
