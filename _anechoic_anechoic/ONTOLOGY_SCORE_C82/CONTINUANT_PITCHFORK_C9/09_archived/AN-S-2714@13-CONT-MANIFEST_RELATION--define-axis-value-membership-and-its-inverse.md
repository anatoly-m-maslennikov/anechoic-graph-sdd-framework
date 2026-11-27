---
atom_family: SPEC
atom_id: AN-S-2714
concern:
  subject: HAS_AXIS_VALUE
  path: Model/Graph/Relation
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_relation
  lens: DOM/CONT
state:
  status: "archived"
  version: 13
  updated_at: "2026-11-26T19:10:43.249903+00:00"
---

## Summary

Define axis value membership and its inverse

## Axes

| Relation | Transitive | Functional |
| --- | --- | --- |
| `HAS_AXIS_VALUE` | no | no |
| `IS_AXIS_VALUE_FOR` | no | no |

An entity can have values on distinct Axes. Entities can share an Axis value.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Continuant, EventRecord, Occurrent, ProjectConfigAtom, Relation, SSOT, SpecAtom, TicketAtom

class Relation2714(Relation):
    name = 'HAS_AXIS_VALUE'
    relation.endpoint_pairs = ({'source_endpoint': {'level': 'model_entities', 'entity_paths': (SpecAtom, ProjectConfigAtom, EventRecord)}, 'target_endpoint': {'level': 'model_entities', 'entity_paths': (Continuant,)}}, {'source_endpoint': {'level': 'model_entities', 'entity_paths': (TicketAtom,)}, 'target_endpoint': {'level': 'model_entities', 'entity_paths': (Occurrent,)}}, {'source_endpoint': {'level': 'model_entities', 'entity_paths': (SpecAtom, EventRecord)}, 'target_endpoint': {'level': 'model_entities', 'entity_paths': (SSOT,)}})
    relation.inverse_alias = 'IS_AXIS_VALUE_FOR'
```
