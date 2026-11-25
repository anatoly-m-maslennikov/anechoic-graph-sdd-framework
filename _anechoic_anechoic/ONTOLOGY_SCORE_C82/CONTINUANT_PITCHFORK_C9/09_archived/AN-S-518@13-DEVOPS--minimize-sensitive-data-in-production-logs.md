---
atom_family: SPEC
atom_id: AN-S-518
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: "archived"
  version: 13
  updated_at: "2026-11-25T22:04:02.690277+00:00"
---
## Summary

Minimize sensitive data in production logs

## Claim

### Prose Claim


production logs that can contain personal, customer, **or** commercially sensitive data.


personal, customer, **and** commercially sensitive data in production logs **must** be omitted, masked, hashed, tokenized, **or** **otherwise** minimized according to the applicable boundary.

## Details

the applicable boundary selects the permitted minimization treatment for sensitive log data.
