---
atom_family: SPEC
atom_id: AN-S-4954
container:
  component: C85
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-4932
state:
  status: draft
  version: 1
  updated_at: '2026-11-26T00:00:00Z'
---

## Summary

Normalize formal declarations.

## Guarantee

Validate the Manifest and lower supported Contract and Solution claims to a normalized model. Preserve source references and report gaps.

## Claim

### Formal Claim

```python trace
declare_trace_contract(
    action='normalize_spec',
    output='normalized',
    must_effect=(('C85.formal_declarations', 'normalized'),),
)
```
