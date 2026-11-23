---
atom_family: SPEC
atom_id: AN-S-1496
container:
  component: C00
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 18
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Provide capabilities **without** forcing their execution

## Claim scope

capabilities provided by the ANECHOIC Framework Instance.

## Claim

the ANECHOIC Framework Instance **must** provide capabilities for the Operator **without** initiating **or** forcing their execution independently of Operator authorization.

## Details

- a Requirement **to** provide a capability specifies what is available **to** the Operator; it does **not** itself authorize **or** trigger execution.
- execution follows direct Operator instruction **or** explicit prior authorization. prior authorization **may** cover a Workflow **or** automation **and** its Actions within the authorized targets **and** constraints; separate approval for **every** covered Action is **not** required.
- required outcomes, validation gates, **and** safeguards remain binding **when** an authorized capability executes. capability wording does **not** make those conditions optional.
