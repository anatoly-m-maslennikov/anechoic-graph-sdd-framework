---
atom_family: SPEC
atom_id: AN-S-4939
concern:
  subject: Database Record
  path: Model/Carrier/Database
  relation: is_contained_by
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 3
  updated_at: "2026-11-28T11:52:02.110048+00:00"
---
## Summary

Declare Database Record

## Semantics

A Database Record identifies a stored entry by its database, table, and stable record ID.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

node(DatabaseRecord, Database)
```
