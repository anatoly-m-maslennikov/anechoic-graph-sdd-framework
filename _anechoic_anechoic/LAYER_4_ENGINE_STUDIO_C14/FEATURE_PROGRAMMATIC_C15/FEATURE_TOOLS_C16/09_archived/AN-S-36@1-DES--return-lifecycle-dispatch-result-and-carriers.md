---
atom_family: SPEC
atom_id: AN-S-36
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-04 19:29:30 +0000
---
## Summary

Return lifecycle dispatch result and carriers

# Summary

Return lifecycle dispatch result and carriers

## Scope

The request/result and carrier handoff at the lifecycle dispatcher boundary.

## Claim

The dispatcher **must** return a typed result containing request identity, target/predecessor identity where applicable, sealed expected and observed Carrier metadata, selected operation, model/currentness resolution, preview-or-mutation disposition, authorization disposition, exact native result, diagnostics, changed/unchanged/unknown effects, and history/lineage references. A successful Replace result names both predecessor and successor Carriers. A Change Status result names the prior and admitted resulting status. A preview names no observed mutation.

If carrier persistence, verification, or result recording is incomplete, the result marks the affected carrier/effect `unknown` or `unverified`, retains recoverable evidence, and never claims recovery or success without observed restoration.

## Details

The shared Run receipt consumes this result; this carrier contract does not duplicate its event schema.
