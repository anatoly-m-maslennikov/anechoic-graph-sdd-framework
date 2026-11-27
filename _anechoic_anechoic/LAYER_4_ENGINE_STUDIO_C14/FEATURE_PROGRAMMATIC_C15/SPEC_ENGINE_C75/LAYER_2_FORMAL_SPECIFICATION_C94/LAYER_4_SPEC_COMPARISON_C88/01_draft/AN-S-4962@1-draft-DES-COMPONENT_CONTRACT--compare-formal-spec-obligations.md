---
atom_family: SPEC
atom_id: AN-S-4962
container:
  component: C88
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-4935
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T21:35:58.956802+00:00'
---

## Summary

Compare formal Spec obligations.

## Guarantee

Compare Manifest to Contract, Manifest to Solution, and Contract to Solution through the formal model. Report each role comparison, including conflicting and unresolved obligations. A comparison result does not mean that all obligations match.

## Claim

### Formal Claim

```python trace
declare_trace_contract(
    action='compare_obligations',
    output='compared',
    must_effect=(('C88.manifest_contract', 'compared'),
                 ('C88.manifest_solution', 'compared'),
                 ('C88.contract_solution', 'compared')),
)
```
