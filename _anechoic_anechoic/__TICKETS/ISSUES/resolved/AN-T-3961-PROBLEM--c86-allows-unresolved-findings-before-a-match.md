---
atom_family: TKT
atom_id: AN-T-3961
concern:
- subject: C86
  path: Project Structure.components
  relation: affects
container:
  component: C86
priority: 2
context:
  template: problem
state:
  status: resolved
  version: 1
  updated_at: '2026-11-25T22:51:21+00:00'
---
## Summary

C86 allows unresolved findings before a match

## Claim

### Prose Claim

The current Spec passes a trace that reports unresolved evidence and immediately returns matched.

Review surface: Spec Engine Manifest, Contract, and Solution review.

## Resolution criteria

Declare a clean match condition that rejects the unresolved path.

## Resolution

The matched case forbids an open translation finding. Lean rejects the prior unresolved-then-matched control.
