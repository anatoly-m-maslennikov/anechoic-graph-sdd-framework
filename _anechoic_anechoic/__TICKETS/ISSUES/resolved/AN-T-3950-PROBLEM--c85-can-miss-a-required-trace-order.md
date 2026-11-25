---
atom_family: TKT
atom_id: AN-T-3950
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

C85 can miss a required trace order

## Claim

### Prose Claim

Python equality admits count: true as the endpoint of a requirement for count: 1. Lean keeps the types distinct so the earlier approval can go unchecked. The full chain returned matched although the workflow omitted approval.

Review surface: LAYER_4_ENGINE_STUDIO_C14/SPEC_ENGINE_C75/LAYER_2_FORMAL_MODEL_C85/contract_model__pub.py:243.

## Resolution criteria

Validate trace-order endpoints with typed equality. Report an invalid endpoint.

## Resolution

A Boolean in a numeric order endpoint now fails validation. Valid typed ordering still reaches Lean.
