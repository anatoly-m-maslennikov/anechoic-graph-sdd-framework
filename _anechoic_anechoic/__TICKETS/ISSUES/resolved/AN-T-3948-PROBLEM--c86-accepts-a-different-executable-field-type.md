---
atom_family: TKT
atom_id: AN-T-3948
concern:
- subject: C86
  path: Project Structure.components
  relation: affects
container:
  component: C86
priority: 2
context:
  template: problem
state:
  status: resolved
  version: 1
  updated_at: '2026-11-25T22:51:21+00:00'
---
## Summary

C86 accepts a different executable field type

## Claim

### Prose Claim

The projection test allows an implicit Lean coercion. A field of an empty subtype still validated as matched. Independent Lean proofs established that the original record had a value and the changed record had none.

Review surface: LAYER_4_ENGINE_STUDIO_C14/SPEC_ENGINE_C75/LAYER_4_TRANSLATION_VALIDATOR_C86/shape_validation.py:37.

## Resolution criteria

Check the exact Lean projection type and reject a coercible but different field.

## Resolution

Lean compared exact projected types. A coercible empty subtype now conflicts.
