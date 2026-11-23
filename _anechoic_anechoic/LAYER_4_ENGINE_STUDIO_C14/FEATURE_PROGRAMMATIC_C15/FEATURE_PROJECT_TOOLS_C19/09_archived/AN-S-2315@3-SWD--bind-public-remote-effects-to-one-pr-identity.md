---
atom_family: SPEC
atom_id: AN-S-2315
container:
  component: C19
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 3
  updated_at: 2026-10-23 23:34:06 +0400
---
## Summary

Bind public remote effects to one PR identity

# Summary

Bind public remote effects to one PR identity

## Scope

the selected `amm/dev` push and `main` PR maintenance sequence.

## Claim

**the Operator** **must** use admitted native bindings to prove the immutable pushed commit and retain exactly one matching open PR identity through its create/update and any final refresh.

## Details

The bindings may use local subprocess facilities after their own admission; this Method adds no MCP prerequisite. It excludes merge and makes an identity change a stop condition.
