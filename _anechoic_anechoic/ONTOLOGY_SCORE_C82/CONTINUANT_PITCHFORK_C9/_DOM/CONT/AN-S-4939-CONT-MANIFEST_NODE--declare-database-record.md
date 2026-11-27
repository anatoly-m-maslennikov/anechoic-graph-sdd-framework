---
atom_family: SPEC
atom_id: AN-S-4939
concern:
  subject: Database Record
  path: Model/Carrier
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 2
  updated_at: '2026-11-26T17:13:38.390434+00:00'
---
## Summary

Declare Database Record

## Semantics

A Database Record identifies a stored entry by its database, table, and stable record ID.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

node(DatabaseRecord, Carrier)
```
