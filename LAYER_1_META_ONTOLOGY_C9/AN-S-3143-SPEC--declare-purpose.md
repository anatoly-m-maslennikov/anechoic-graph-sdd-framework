---
atom_family: SPEC
atom_id: AN-S-3143
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: active
  version: 2
  updated_at: '2026-11-22T08:56:40.513203+00:00'
---

## Summary

Declare Purpose

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Component Seed Manifest.Purpose

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Purpose',
    entity_kind='Property',
    relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom//Spec Atom//Component Seed Manifest',
    value_format=str,
    value_cardinality=1,
    property_occurrence_cardinality=1,
)
```
