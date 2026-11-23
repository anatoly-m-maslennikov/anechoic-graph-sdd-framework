---
atom_family: TKT
atom_id: AN-T-155
container:
  component: C00
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 2
  updated_at: 2026-10-24 06:04:08 +0400
---
## Summary

Prepare the validator golden corpus

# Summary

Prepare the validator golden corpus

## Claim

the assigned AI Agent **must** prepare source-bound mocked end-to-end cases for the public VALIDATE_ATOMS interface before implementation.

## Definition of Done

the Plan is **not** Done **if** the public-command suite is absent, skipped, derives expected results from implementation output, lacks positive/negative/boundary/mixed cases, or lacks a failing missing-executable baseline.

## Details

- tests/ only; expected reports and case manifest are independently authored from RED.
- use the source-bound input packet **in** `.anechoic_tmp/implementation/validate-atoms-20260924`; current source Atoms remain authority. record evidence **without** editing unrelated work, weakening expected results, **or** promoting learned Methods inside this implementation Run.
