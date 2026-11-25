---
atom_family: SPEC
atom_id: AN-S-3354
container:
  component: C61
tier: 1
context:
  template: DECISION
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-22T23:52:17.262612+00:00'
---

## Summary

Detect leaked Python context bindings

## Claim

### Prose Claim

For a recognized temporary ContextVar binding, follow its token across normal
and exceptional exits. Report a missing reset on a witnessed exit and keep
unknown token or context flows unresolved.
