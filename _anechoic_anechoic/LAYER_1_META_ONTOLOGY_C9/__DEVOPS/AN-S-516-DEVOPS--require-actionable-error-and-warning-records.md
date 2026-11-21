---
atom_family: SPEC
atom_id: AN-S-516
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DevOps
state:
  status: active
  version: 13
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Require actionable ERROR and WARNING records

## Claim

### Prose Claim


ERROR **and** WARNING production log records.


an `ERROR` **or** `WARNING` record **must** be actionable: it identifies the failed **or** degraded condition, affected scope, expected operator **or** automated response, **and** whether retry is safe.

## Details

the required context makes the response **and** retry disposition explicit for the failed **or** degraded condition.
