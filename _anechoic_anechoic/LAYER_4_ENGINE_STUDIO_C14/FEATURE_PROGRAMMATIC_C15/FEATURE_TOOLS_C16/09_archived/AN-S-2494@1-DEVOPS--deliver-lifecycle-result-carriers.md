---
atom_family: SPEC
atom_id: AN-S-2494
container:
  component: C16
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 1
  updated_at: 2026-10-04 19:29:30 +0000
---
## Summary

Deliver lifecycle result carriers

# Summary

Deliver lifecycle result carriers

## Scope

The returned lifecycle dispatch record and its handoff to native Tools and shared Run support.

## Claim

The result carrier preserves request, sealed/observed Carrier data, operation/model selection, authorization, diagnostics, exact native outcome, history/lineage, and known/unknown effects. It hands these facts to shared Run support without creating a second event schema or asserting persistence that did not occur.

## Details

Status-transition diagnostics distinguish observed broken references from an unperformed or failed transition, and identify the separate repair handoff where it is needed.
