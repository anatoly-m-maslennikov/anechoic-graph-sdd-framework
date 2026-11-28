---
atom_family: SPEC
atom_id: AN-S-4813
concern:
  subject: File
  path: Model/Carrier/Filesystem
  relation: is_contained_by
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: active
  version: 5
  updated_at: "2026-11-28T11:52:02.110048+00:00"
---

## Summary

Declare File

## Semantics

A File represents content carried as bytes at a filesystem path.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

node(File, Filesystem)
```
