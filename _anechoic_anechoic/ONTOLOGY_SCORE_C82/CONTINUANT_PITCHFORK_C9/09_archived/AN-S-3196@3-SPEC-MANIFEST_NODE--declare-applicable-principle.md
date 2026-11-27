---
atom_family: SPEC
atom_id: AN-S-3196
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
relations:
  IS_REPLACEMENT_FOR:
  - AN-S-3302
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T15:54:02.590667+00:00"
---

## Summary

Declare Applicable Principle

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Applicable Principle

## Claim

### Prose Claim

The Applicable Principle Template guides Project decisions when its
applicability conditions hold.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import SpecAtom

class ApplicablePrinciple(SpecAtom):
    pass
```
