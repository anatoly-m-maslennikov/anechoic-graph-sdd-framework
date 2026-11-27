---
atom_family: SPEC
atom_id: AN-S-2726
concern:
  subject: IS_BLOCKED_BY
  path: Model/Graph/Relation
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_relation
  lens: DOM/CONT
state:
  status: "active"
  version: 4
  updated_at: "2026-11-26T14:46:18.880365+00:00"
---
## Summary

Declare IS_BLOCKED_BY

## Semantics

The source Task depends on the target Task. Use the stable ID of the blocking Task. The Tasks can belong to different Epics. An Epic uses the Task template and can be either endpoint.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Relation, Task

class IsBlockedBy(Relation):
    name = 'IS_BLOCKED_BY'
    relation.source_endpoint = {'level': 'instances', 'entity_paths': (Task,)}
    relation.target_endpoint = {
        'level': 'instances',
        'entity_paths': (Task,),
        'reference_form': 'base_atom_id',
    }
    relation.inverse_alias = 'BLOCKS'
    relation.acyclic = True
```
