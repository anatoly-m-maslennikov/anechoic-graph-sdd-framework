---
atom_family: SPEC
atom_id: AN-S-2734
concern:
  subject: IS_WORK_REPORT_FOR
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
  version: 4
  updated_at: "2026-11-26T16:34:52.381133+00:00"
---
## Summary

Declare IS_WORK_REPORT_FOR

## Semantics

A Work Report identifies the Task whose execution it records. Use the Task’s stable ID.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Relation, Task, WorkReport

class IsWorkReportFor(Relation):
    name = 'IS_WORK_REPORT_FOR'
    relation.source_endpoint = {'level': 'instances', 'entity_paths': (WorkReport,)}
    relation.target_endpoint = {
        'level': 'instances',
        'entity_paths': (Task,),
        'reference_form': 'base_atom_id',
    }
    relation.targets_per_source = 1
```
