---
atom_family: SPEC
atom_id: AN-S-4817
concern:
  subject: Non-executable File
  path: Model/Carrier/File
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
  updated_at: "2026-11-26T17:13:49.156636+00:00"
---

## Summary

Declare Non-executable File

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import File

class NonExecutableFile(File):
    pass
```
