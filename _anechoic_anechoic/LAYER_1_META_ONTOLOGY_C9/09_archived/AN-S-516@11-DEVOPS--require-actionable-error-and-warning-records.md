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
  version: 11
  updated_at: 2026-10-29 07:45:31 +0400
---
## Summary

Require actionable ERROR and WARNING records

## Claim scope

ERROR **and** WARNING production log records.

## Claim

an `ERROR` **or** `WARNING` record **must** be actionable: it identifies the failed **or** degraded condition, affected scope, expected operator **or** automated response, **and** whether retry is safe.

## Details

the required context makes the response **and** retry disposition explicit for the failed **or** degraded condition.
