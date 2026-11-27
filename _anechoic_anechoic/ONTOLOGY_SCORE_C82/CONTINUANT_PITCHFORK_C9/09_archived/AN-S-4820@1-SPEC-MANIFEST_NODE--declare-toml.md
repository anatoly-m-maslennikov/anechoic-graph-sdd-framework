---
atom_family: SPEC
atom_id: AN-S-4820
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-26T15:54:02.788643+00:00"
---

## Summary

Declare TOML

## Claim scope

MODEL//ANECHOIC <+ Carrier/File//Non-executable File//TOML

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import NonExecutableFile

class TOML(NonExecutableFile):
    pass
```
