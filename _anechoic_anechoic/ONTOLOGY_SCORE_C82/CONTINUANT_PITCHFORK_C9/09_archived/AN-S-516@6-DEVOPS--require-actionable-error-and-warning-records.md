---
atom_family: SPEC
atom_id: AN-S-516
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 6
  updated_at: 2026-10-24 09:42:52 +0400
---
## Summary

Require actionable ERROR and WARNING records

# Summary

Require actionable ERROR and WARNING records

## Scope

ERROR **and** WARNING production log records.

## Claim

an `ERROR` **or** `WARNING` record **must** be actionable: it identifies the failed **or** degraded condition, affected scope, expected operator **or** automated response, **and** whether retry is safe.

## Details

the required context makes the response **and** retry disposition explicit for the failed **or** degraded condition.
