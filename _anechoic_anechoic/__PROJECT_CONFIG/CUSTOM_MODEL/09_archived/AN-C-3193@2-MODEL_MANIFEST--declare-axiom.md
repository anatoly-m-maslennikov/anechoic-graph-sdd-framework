---
atom_family: PROJECT_CONFIG
atom_id: AN-C-3193
structure:
  container:
    component: C00
context:
  template: model_manifest
relations:
  IS_REPLACEMENT_FOR:
  - AN-S-3193
  - AN-S-3194
  - AN-S-3195
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-21T21:19:38+00:00'
---

## Summary

Declare Axiom

## Semantics

An Axiom states an accepted premise for the Project within the context of
the Project Goal. It uses the SPEC Lens and Tier 0. The level 0 Project is its only Container. An Active
Axiom lives at the Project root. Its other revisions use the Project's
lifecycle status directories.

## Formal Manifest

### Type

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Axiom

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import SpecAtom

class Axiom(SpecAtom):
    pass

declare_entity(
    entity_name='Axiom',
    entity_class=Axiom,
    entity_kind='Primary',
)
```

### Tier

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Axiom.Header.Tier

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Tier',
    entity_kind='Property',
    relation_name='IS_PROPERTY_OF',
    base_path='Node//Artifact//Atom//Spec Atom.Header',
    value_format=int,
    field_options={'kw_only': True},
    allowed_values=(0,),
    value_cardinality=1,
    property_occurrence_cardinality=1,
    applies_to_entity_classes=('Node//Artifact//Atom//Spec Atom//Axiom',),
)
```

### Containment

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Axiom.Constraints

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Axiom

declare_entity(
    entity_name='Axiom Constraints',
    constraints_for='Node//Artifact//Atom//Spec Atom//Axiom',
    instance_relation_constraints={'CONTAINED_BY': {'target_entity_paths': ('Node//Artifact//Component//Project',), 'targets_per_source': 1}},
)
```
