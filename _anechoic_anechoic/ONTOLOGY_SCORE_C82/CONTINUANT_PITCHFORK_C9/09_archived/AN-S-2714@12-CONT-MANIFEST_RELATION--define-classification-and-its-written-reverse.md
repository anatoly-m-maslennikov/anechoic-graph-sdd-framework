---
atom_family: SPEC
atom_id: AN-S-2714
concern:
  subject: IS_CLASSIFIED_BY
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
  version: 12
  updated_at: "2026-11-26T18:34:34.741624+00:00"
---

## Summary

Define classification and its written reverse

## Classifications

| Relation | Transitive | Functional |
| --- | --- | --- |
| `IS_CLASSIFIED_BY` | no | no |
| `CLASSIFIES` | no | no |

A Spec Atom can be classified through both the Continuant and SSOT endpoint pairs. A classifier can have multiple members.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Continuant, EventRecord, Occurrent, ProjectConfigAtom, Relation, SSOT, SpecAtom, TicketAtom

class Relation2714(Relation):
    name = 'IS_CLASSIFIED_BY'
    relation.endpoint_pairs = ({'source_endpoint': {'level': 'model_entities', 'entity_paths': (SpecAtom, ProjectConfigAtom, EventRecord)}, 'target_endpoint': {'level': 'model_entities', 'entity_paths': (Continuant,)}}, {'source_endpoint': {'level': 'model_entities', 'entity_paths': (TicketAtom,)}, 'target_endpoint': {'level': 'model_entities', 'entity_paths': (Occurrent,)}}, {'source_endpoint': {'level': 'model_entities', 'entity_paths': (SpecAtom, EventRecord)}, 'target_endpoint': {'level': 'model_entities', 'entity_paths': (SSOT,)}})
    relation.inverse_alias = 'CLASSIFIES'
```
