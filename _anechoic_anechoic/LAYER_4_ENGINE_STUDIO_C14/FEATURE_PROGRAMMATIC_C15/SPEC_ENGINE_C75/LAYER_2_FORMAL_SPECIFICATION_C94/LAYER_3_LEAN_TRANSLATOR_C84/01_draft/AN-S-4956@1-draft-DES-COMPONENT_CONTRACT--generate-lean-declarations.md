---
atom_family: SPEC
atom_id: AN-S-4956
container:
  component: C84
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-4931
state:
  status: draft
  version: 1
  updated_at: '2026-11-26T00:00:00Z'
---

## Summary

Generate Lean declarations.

## Guarantee

Obtain normalized claims and source-linked gaps from C85. Encode the
claims with their source references and return the Lean source and those
normalized results.

## Claim

### Formal Claim

```python trace
declare_trace_contract(
    action='compile_lean',
    output='compiled',
    must_effect=(('C84.lean_source', 'generated', {'model': 'request_normalized_model'}),),
)
```
