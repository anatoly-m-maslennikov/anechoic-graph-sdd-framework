---
atom_family: SPEC
atom_id: AN-S-2697
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 20
  updated_at: "2026-11-25T20:41:49.259175+00:00"
---

## Summary

Define Relation

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation

## Semantics

An authored Relation fact has one authoritative declaration. Derived Relations identify their derivation and authoritative input facts, including through an upstream Projection. A derived inverse exposes the same fact with the endpoints reversed.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

class Relation:
    pass
```
