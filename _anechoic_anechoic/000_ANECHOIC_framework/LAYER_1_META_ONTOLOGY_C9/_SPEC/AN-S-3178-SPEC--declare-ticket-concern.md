---
atom_family: SPEC
atom_id: AN-S-3178
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-20T21:44:52.681755+00:00'
---

## Summary

Declare Ticket Concern

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Ticket Atom.Header.Concern

## Claim

### Prose Claim

A Ticket Concern is an optional list of locators. Each locator contains Subject, Path, and Relation, as defined in AN-S-3163. For an affected Component, use its ID as `subject`, `Project Structure.components` as `path`, and `affects` as `relation`.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
declare_entity(entity_name='Concern', entity_kind='Property', relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom//Ticket Atom.Header', value_format=list[dict[str, str]],
    value_cardinality=Cardinality(minimum=1, maximum=None),
    property_occurrence_cardinality=Cardinality(minimum=0, maximum=1),
    field_options={'default': None, 'kw_only': True})
```
