---
atom_family: SPEC
atom_id: AN-S-4819
concern:
  subject: YAML
  path: Model/Carrier/File//Non-executable File
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
  updated_at: "2026-11-26T17:13:49.166356+00:00"
---

## Summary

Declare YAML

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import NonExecutableFile

class YAML(NonExecutableFile):
    pass
```
