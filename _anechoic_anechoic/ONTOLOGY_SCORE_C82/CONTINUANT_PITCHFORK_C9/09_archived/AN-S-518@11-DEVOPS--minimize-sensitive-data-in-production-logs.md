---
atom_family: SPEC
atom_id: AN-S-518
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 11
  updated_at: 2026-10-29 07:45:31 +0400
---
## Summary

Minimize sensitive data in production logs

## Claim scope

production logs that can contain personal, customer, **or** commercially sensitive data.

## Claim

personal, customer, **and** commercially sensitive data in production logs **must** be omitted, masked, hashed, tokenized, **or** **otherwise** minimized according to the applicable boundary.

## Details

the applicable boundary selects the permitted minimization treatment for sensitive log data.
