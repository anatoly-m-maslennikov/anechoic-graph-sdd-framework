---
atom_family: SPEC
atom_id: AN-S-3917
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 13
  updated_at: 2026-10-15 12:21:24 +0000
---
## Summary

Limit Artifact Activity to explicit Status models

# Summary

Limit Artifact Activity to explicit Status models

## Scope

Artifacts to which explicitly defined Status models apply.

## Claim

an Artifact **must** have **`=1`** Activity **in** (Active, Inactive) **if** an explicitly defined Status model applies **to** it, **and** **`=0`** Activity **otherwise**.

## Details
