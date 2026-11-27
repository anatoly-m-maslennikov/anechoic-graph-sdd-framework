---
atom_family: SPEC
atom_id: AN-S-3196
concern:
  subject: Applicable Principle
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
relations:
  IS_REPLACEMENT_FOR:
  - AN-S-3302
state:
  status: active
  version: 5
  updated_at: '2026-11-26T17:13:26.105922+00:00'
---

## Summary

Declare Applicable Principle

## Claim

### Prose Claim

The Applicable Principle Template guides Project decisions when its
applicability conditions hold.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

node(ApplicablePrinciple, SpecAtom)
```
