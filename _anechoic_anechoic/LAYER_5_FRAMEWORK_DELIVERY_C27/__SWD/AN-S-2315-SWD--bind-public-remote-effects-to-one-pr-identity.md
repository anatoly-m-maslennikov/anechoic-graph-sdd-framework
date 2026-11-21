---
atom_family: SPEC
atom_id: AN-S-2315
structure:
  container:
    component: C27
  tier: 4
context:
  lens: SWD
state:
  status: active
  version: 14
  updated_at: 2026-11-09 15:54:30 +0400
---

## Summary

Bind public remote effects to one PR identity

## Scope

the selected `amm/dev` push and `main` PR maintenance sequence.

## Claim

### Prose Claim

**the Operator** **must** use admitted native bindings to prove the immutable pushed commit and retain exactly one matching open PR identity through its create/update and any final refresh.

## Details

The bindings may use local subprocess facilities after their own admission; this Method adds no MCP prerequisite. It excludes merge and makes an identity change a stop condition.
