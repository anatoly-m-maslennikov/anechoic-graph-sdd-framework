---
atom_family: SPEC
atom_id: AN-S-3163
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: active
  version: 3
  updated_at: '2026-11-21T19:14:35.061068+00:00'
---

## Summary

Declare Concern

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom.Header.Concern

## Claim

### Prose Claim

A SPEC Concern records affected Component IDs, a Subject with its Path and Relation, or both. Supply Subject, Path, and Relation together when you use any of them. A TKT Concern is an optional single list of typed references. Reference kinds share that list; reserve `@` for eDSL function calls. The generated Model fields do not prescribe the Carrier representation.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
declare_entity(entity_name='Concern', entity_kind='Property', relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom.Header', value_format=object, value_cardinality=0, property_occurrence_cardinality=Cardinality(minimum=0, maximum=1), allowed_dependent_property_names=('Subject', 'Path', 'Relation', 'Components'), ordered_dependent_property_pairs=(('Subject', 'Path'), ('Path', 'Relation'), ('Relation', 'Components')))
```
