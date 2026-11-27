---
atom_family: SPEC
atom_id: AN-S-3114
container:
  component: C9
tier: 2
context:
  lens: SPEC
relations:
  IS_REPLACEMENT_FOR:
  - AN-S-3129
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T15:54:03.583211+00:00"
---

## Summary

Declare Component Contract Spec Template

## Semantics

A Component Contract describes a Component’s externally observable behavior.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import declare_template
from anechoic.model import Contract

@declare_template()
class ComponentContract(Contract):
    pass
```
