---
atom_family: SPEC
atom_id: AN-S-3358
container:
  component: C61
tier: 1
context:
  template: DECISION
  lens: QA
state:
  status: active
  version: 3
  updated_at: "2026-11-27T18:09:40.995150+00:00"
---

## Summary

Check JavaScript environment access and mutable exports

## Claim

### Prose Claim

Check supported process.env effects against ENV grants. Follow known aliases
of exported mutable objects to the owner and retain unresolved findings when
the alias cannot be resolved.
