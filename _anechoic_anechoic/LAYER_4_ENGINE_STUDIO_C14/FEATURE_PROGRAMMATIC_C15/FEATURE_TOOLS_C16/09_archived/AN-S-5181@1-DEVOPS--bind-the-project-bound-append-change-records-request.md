---
atom_family: SPEC
atom_id: AN-S-5181
container:
  component: C16
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 1
  updated_at: "2026-11-27T18:09:40.995150+00:00"
---

## Summary

Bind the Project-bound APPEND_CHANGE_RECORDS request

## Claim

For the Project-bound `append_change_records` interface, the closed transport request remains `{context, apply}` with strict boolean `apply`, default false; `context` supplies the existing Journal location inputs and `predictions.journal_records`. This transport shape is not a Journal-row validation or sealed-context requirement. Dry run changes nothing. Apply appends the supplied observations independently of real-change commits. Read returns existing stored data as recorded; it does **not** replay source effects.
