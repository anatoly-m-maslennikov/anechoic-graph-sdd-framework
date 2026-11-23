---
atom_family: SPEC
atom_id: AN-S-3667
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 13
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Define Plan completion

# Summary

Define Plan completion

## Scope

Plan completion.

## Claim

Plan Status Done **means** that **all** applicable completion conditions hold:

- the Plan satisfies CA-R-1575; absence of work **and** decomposition **must not** count as completion.
- its own work, **if** present, is complete.
- **every** directly decomposed Plan is Done.
- its Definition of Done falsifying Condition Expression evaluates **to** false.

a Hub requires its own Definition of Done **and** completion of its decomposed Plans; Canceled **or** Archived work does **not** satisfy Done.

## Details
