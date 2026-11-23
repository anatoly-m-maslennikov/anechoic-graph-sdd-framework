---
atom_family: SPEC
atom_id: AN-S-80
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 17
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Commit one folder action atomically

# Commit one folder action atomically

## Test case

Given one sealed folder action with its complete ordered entry set, **when** `COMMIT_CHANGE_SET` applies it, **then** exactly one real-change commit **contains** **all** **and** **only** that folder action's entry changes with its Initiative-based message. Its Journal record is appended independently **and** a later Journal-only batch, **if** **any**, **contains** **only** Journal carrier changes.

## Sources

- [CA-R-805 — Serialize repository Git mutations through one logical gate](../04_requirement/CA-R-805-COMMIT_CHANGE_SET-RULE--serialize-admitted-local-commits-through-one-logical-gate.md)
- [CA-R-812 — Append governed action records independently of real-change commits](../../APPEND_CHANGE_RECORDS/04_requirement/CA-R-812-APPEND_CHANGE_RECORDS-RULE--append-governed-action-records-independently-of-real-change-commits.md)
