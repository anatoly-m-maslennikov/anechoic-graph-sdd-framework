---
identity:
  atom_id: AN-T-155
context:
  container:
    atom: AN-T-160
  tier: 3
  template: task
state:
  status: active
  version: 7
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Prepare the validator golden corpus

## Claim

the assigned AI Agent **must** prepare source-bound mocked end-to-end cases for the public VALIDATE_ATOMS interface before implementation.

## Definition of Done

the Plan is **not** Done **if** the public-command suite is absent, skipped, derives expected results from implementation output, lacks positive/negative/boundary/mixed cases, or lacks a failing missing-executable baseline.

## Details

- tests/ only; expected reports and case manifest are independently authored from RED.
- use the source-bound input packet **in** `.anechoic_tmp/implementation/validate-atoms-20260924`; current source Atoms remain authority. record evidence **without** editing unrelated work, weakening expected results, **or** promoting learned Methods inside this implementation Run.
