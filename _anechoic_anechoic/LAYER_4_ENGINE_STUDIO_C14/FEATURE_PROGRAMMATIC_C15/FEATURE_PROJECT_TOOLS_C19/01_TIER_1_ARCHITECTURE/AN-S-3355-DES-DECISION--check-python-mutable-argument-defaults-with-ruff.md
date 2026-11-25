---
atom_family: SPEC
atom_id: AN-S-3355
container:
  component: C19
tier: 1
context:
  template: DECISION
  lens: DES
state:
  status: active
  version: 1
  updated_at: "2026-11-22T18:38:16.552745+00:00"
---

## Summary

Check Python mutable argument defaults with Ruff

## Claim

### Prose Claim

Use Ruff B006 in the Engine static phase to flag mutable defaults. Retain
explicit exceptions for intentional shared state.
