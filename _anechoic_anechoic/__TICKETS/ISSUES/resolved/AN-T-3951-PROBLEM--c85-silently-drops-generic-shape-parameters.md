---
atom_family: TKT
atom_id: AN-T-3951
concern:
- subject: C85
  path: Project Structure.components
  relation: affects
container:
  component: C85
priority: 2
context:
  template: problem
state:
  status: resolved
  version: 1
  updated_at: '2026-11-25T22:51:21+00:00'
---
## Summary

C85 silently drops generic shape parameters

## Claim

### Prose Claim

Plain Atom and Atom[T] emitted identical Lean and both passed C86. The shape parser reads class fields and bases but ignores type parameters.

Review surface: LAYER_4_ENGINE_STUDIO_C14/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C85/shape_model__pub.py:40.

## Resolution criteria

Report generic classes as unsupported until lowering preserves the type parameters.

## Resolution

Generic record and subtype classes now report unsupported shape syntax before translation.
