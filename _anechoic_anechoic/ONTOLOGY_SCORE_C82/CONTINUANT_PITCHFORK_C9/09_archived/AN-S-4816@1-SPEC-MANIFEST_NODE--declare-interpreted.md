---
atom_family: SPEC
atom_id: AN-S-4816
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-26T15:54:02.755571+00:00"
---

## Summary

Declare Interpreted

## Claim scope

MODEL//ANECHOIC <+ Carrier/File//Executable File//Interpreted

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ExecutableFile

class Interpreted(ExecutableFile):
    pass
```
