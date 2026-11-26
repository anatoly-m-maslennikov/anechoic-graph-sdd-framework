---
atom_family: TKT
atom_id: AN-T-3953
concern:
- subject: C88
  path: Project Structure.components
  relation: affects
container:
  component: C88
priority: 2
context:
  template: problem
state:
  status: resolved
  version: 1
  updated_at: '2026-11-25T22:51:21+00:00'
---
## Summary

C88 reports a false conflict for a null target

## Claim

### Prose Claim

The comparison lowers an explicit null target as a wildcard. Independent Lean replay accepts only null in this case. Omitting the field does allow the disputed target.

Review surface: LAYER_4_ENGINE_STUDIO_C14/SPEC_ENGINE_C75/LAYER_3_LEAN_TRANSLATOR_C84/trace_lean__pub.py:48.

## Resolution criteria

Distinguish explicit null from an omitted target in the Lean comparison.

## Resolution

The Lean guard tests distinguish explicit null from a missing target or outcome.
