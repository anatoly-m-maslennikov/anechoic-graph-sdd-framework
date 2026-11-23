---
atom_family: SPEC
atom_id: AN-S-3358
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
  updated_at: '2026-11-22T18:38:16.563185+00:00'
---

## Summary

Check JavaScript environment access and mutable exports

## Claim

### Prose Claim

Check supported process.env effects against ENV grants. Follow known aliases
of exported mutable objects to the owner and retain unresolved findings when
the alias cannot be resolved.
