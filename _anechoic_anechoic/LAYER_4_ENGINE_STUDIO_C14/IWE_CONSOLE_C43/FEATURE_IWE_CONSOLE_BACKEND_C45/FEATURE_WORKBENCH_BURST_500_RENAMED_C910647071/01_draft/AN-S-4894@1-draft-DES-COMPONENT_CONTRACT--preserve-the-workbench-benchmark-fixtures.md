---
atom_family: SPEC
atom_id: AN-S-4894
container:
  component: C910647071
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3073
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T11:41:14.183021+00:00'
---

## Summary

Preserve the Workbench benchmark fixtures

## Guarantee

Preserve the 500 Current Workbench benchmark fixture Atoms in their
declared group under C45. Retain the existing sources until their
deferred migration is authorized.

## Claim

### Formal Claim

```python group
declare_group_contract(
    roles={},
    current_record_count=500,
)
```
