---
atom_family: TKT
atom_id: AN-T-3952
concern:
- subject: C75
  path: Project Structure.components
  relation: affects
container:
  component: C75
priority: 2
context:
  template: problem
state:
  status: resolved
  version: 1
  updated_at: '2026-11-25T22:51:21+00:00'
---
## Summary

C75 renders Mermaid after the comparisons

## Claim

### Prose Claim

The pinned Solution requires rendering before comparison. Lean checked the opposite order in a trace captured from the production entry point.

Review surface: LAYER_4_ENGINE_STUDIO_C14/SPEC_ENGINE_C75/LAYER_4_SPEC_COMPARISON_C88/trace_spec__pub.py:250.

## Resolution criteria

Render Mermaid before comparisons through the parent chain, after translation validation.

## Resolution

The observed parent call order and Lean agree that validation precedes rendering and rendering precedes comparison.
