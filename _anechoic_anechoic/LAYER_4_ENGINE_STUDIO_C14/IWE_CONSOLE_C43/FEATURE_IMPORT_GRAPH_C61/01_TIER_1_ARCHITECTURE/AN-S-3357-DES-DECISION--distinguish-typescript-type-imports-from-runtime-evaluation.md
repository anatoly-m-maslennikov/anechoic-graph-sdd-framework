---
atom_family: SPEC
atom_id: AN-S-3357
container:
  component: C61
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_REFERENCE:
  - AN-S-3083@6
state:
  status: active
  version: 1
  updated_at: "2026-11-22T18:38:16.560096+00:00"
---

## Summary

Distinguish TypeScript type imports from runtime evaluation

## Claim

### Prose Claim

Record type-only bindings and runtime Module evaluation separately. Account
for the effective compiler options and emitted empty imports when reporting
runtime cycles.
