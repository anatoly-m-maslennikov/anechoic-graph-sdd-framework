---
atom_family: TKT
atom_id: AN-T-3955
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

C86 throws instead of returning a shape conflict

## Claim

### Prose Claim

A field with the wrong type that Lean cannot coerce raises ValueError in the public validator. Callers receive no conflicting receipt or source-linked field finding.

Review surface: LAYER_4_ENGINE_STUDIO_C14/SPEC_ENGINE_C75/LAYER_4_TRANSLATION_VALIDATOR_C86/translation_validation__pub.py:69.

## Resolution criteria

Return a source-linked conflicting receipt for a well-typed incompatible projection.

## Resolution

A compiling shape with an incompatible projection returns a source-linked conflicting receipt.
