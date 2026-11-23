---
atom_family: SPEC
atom_id: AN-S-3468
container:
  component: C19
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 1
  updated_at: 2026-10-10 19:05:35 +0400
---
## Summary

Recover public release by discovering uncertain effects

# Summary

Recover public release by discovering uncertain effects

## Scope

recovery after one interrupted public remote effect.

## Claim

**the Operator** **must** restore only existing schema-v5 Run evidence, discover an unknown push or PR from the remote, and require a fresh explicitly authorized continuation instead of replaying uncertainty.

## Details

Tool-call references remain parented evidence. Recording-only recovery cannot turn an unknown remote result into completed execution.
