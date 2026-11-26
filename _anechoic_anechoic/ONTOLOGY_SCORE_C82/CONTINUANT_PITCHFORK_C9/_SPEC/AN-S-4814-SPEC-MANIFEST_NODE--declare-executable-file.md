---
atom_family: SPEC
atom_id: AN-S-4814
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "active"
  version: 1
  updated_at: '2026-11-24T00:00:00+00:00'
---

## Summary

Declare Executable File

## Claim scope

MODEL//ANECHOIC <+ Carrier/File//Executable File

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import File

class ExecutableFile(File):
    pass
```
