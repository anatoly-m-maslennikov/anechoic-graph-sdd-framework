---
atom_family: SPEC
atom_id: AN-S-3354
container:
  component: C61
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_REFERENCE:
  - AN-S-3187@1-draft
  - AN-S-3188@1-draft
state:
  status: archived
  version: 1
  updated_at: '2026-11-22T18:38:16.549289+00:00'
---

## Summary

Detect leaked Python context bindings

## Claim

### Prose Claim

For a recognized temporary ContextVar binding, follow its token across normal
and exceptional exits. Report a missing reset on a witnessed exit and keep
unknown token or context flows unresolved.
