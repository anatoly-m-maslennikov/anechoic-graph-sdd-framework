---
atom_family: SPEC
atom_id: AN-S-2598
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-25T20:32:20.838193+00:00"
---

## Summary

Declare Work Report Form

## Claim

### Prose Claim

A Work Report records the execution of one Plan with Form Plan in a separate Atom. This is the reported Task. It has its own ID and the same Summary and Container as that Task. IS_WORK_REPORT_FOR identifies the Task by its base Atom ID.

Details records:

- actual changes;
- checks performed;
- results;
- remaining gaps.

The report is updated throughout execution. Its Status describes the reporting work: Active while maintained, Done when the final known changes, checks, results and remaining gaps are recorded, or Canceled when reporting is abandoned. Completed reporting includes explicit remaining gaps. The Task retains its own Status.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Plan

class WorkReport(Plan):
    pass

declare_entity(
    entity_name='Work Report', entity_class=WorkReport,
    qualification_property_path='Atom.Header.Context.Form',
    form_roles=('Plan',),
    instance_relation_constraints={
        'IS_WORK_REPORT_FOR': {
            'target_entity_paths': ('Atom/(.Header.Context.Role:=Plan)/(.Header.Context.Form:=Plan)',),
            'targets_per_source': 1,
        },
    },
    form_content={'required_value': 'Details', 'no_children': 'Details', 'after': 'Summary'},
)
```

## Semantics

A Work Report is the evolving record of a Task’s execution.
