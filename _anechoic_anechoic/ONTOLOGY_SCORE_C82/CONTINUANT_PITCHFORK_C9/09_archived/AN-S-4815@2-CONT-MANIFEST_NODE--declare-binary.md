---
atom_family: SPEC
atom_id: AN-S-4815
concern:
  subject: Binary
  path: Model/Carrier/File//Executable File
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-26T17:13:49.147332+00:00"
---

## Summary

Declare Binary

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ExecutableFile

class Binary(ExecutableFile):
    pass
```
