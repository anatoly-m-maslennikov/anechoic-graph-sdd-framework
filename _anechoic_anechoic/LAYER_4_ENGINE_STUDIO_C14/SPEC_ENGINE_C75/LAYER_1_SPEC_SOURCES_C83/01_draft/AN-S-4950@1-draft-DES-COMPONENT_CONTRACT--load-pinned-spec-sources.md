---
atom_family: SPEC
atom_id: AN-S-4950
container:
  component: C83
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-4930
state:
  status: draft
  version: 1
  updated_at: '2026-11-26T00:00:00Z'
---

## Summary

Load pinned Spec sources.

## Guarantee

Load the exact pinned Manifest, Contract, and Solution. Check their Component, declared roles, and required links. Preserve claim sources and report unsupported claims.

## Claim

### Formal Claim

```python trace
declare_trace_contract(
    action='load_boundary_model',
    output='loaded',
    must_effect=(('C83.pinned_sources', 'loaded'),),
)
```
